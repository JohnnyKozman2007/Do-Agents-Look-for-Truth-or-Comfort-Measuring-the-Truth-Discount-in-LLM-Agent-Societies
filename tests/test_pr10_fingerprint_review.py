"""Independent PR10 fingerprint and final source-integrity regressions, offline only."""
import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_deferred_judging import HTTP, KEY, profile
from test_live_cli import MockHTTP, approved_test_manifest
from truth_discount import deferred_judging
from truth_discount.budget import BudgetLedger
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import canonical_bytes, digest
from truth_discount.deferred_judging import judge_collection, plan_judging, replay_judging
from truth_discount.fixtures import FixtureBackend
from truth_discount.providers import ProviderBackend
from truth_discount.runner import run_town
from truth_discount.simulation_execution import allocate_runs, collect_simulations


ROOT = Path(__file__).resolve().parents[1]


class _MutatingHTTP(HTTP):
    def __init__(self, mutate):
        super().__init__()
        self.mutate = mutate
        self.urls = []

    def __call__(self, method, url, headers, body, timeout_seconds):
        self.urls.append(url)
        response = super().__call__(method, url, headers, body, timeout_seconds)
        if self.mutate is not None:
            mutate, self.mutate = self.mutate, None
            mutate()
        return response


class _FirstChatEmpty(MockHTTP):
    def __init__(self):
        super().__init__()
        self.failed = False

    def __call__(self, method, url, headers, body, timeout_seconds):
        response = super().__call__(method, url, headers, body, timeout_seconds)
        if not self.failed and body["max_tokens"] != 5:
            self.failed = True
            response["choices"][0]["message"]["content"] = "   "
        return response


def _hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class FingerprintAndSourceReviewTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.runs = build_manifest(self.config)[:2]
        for run in self.runs:
            await run_town(self.config, run, FixtureBackend(), self.source, defer_judging=True)
        self.profile = profile(self.config)
        env = patch.dict(os.environ, {"DEFERRED_TEST_KEY": KEY,
                                      "TEST_PROVIDER_KEY": "FAKE-ACTOR-KEY-NOT-REAL"})
        env.start()
        self.addCleanup(env.stop)
        network = patch("socket.create_connection", side_effect=AssertionError("network forbidden"))
        network.start()
        self.addCleanup(network.stop)

    async def judge(self, *, source=None, current=None, http=None, resume=False):
        current = current or self.profile
        with BudgetLedger(self.root / (current["profile_id"] + "-ledger.jsonl"), "1") as ledger:
            backend = ProviderBackend(current["provider_manifest"], ledger, transport=http or HTTP(),
                                      evidence_kind="mocked_provider")
            return await judge_collection(source or self.source, self.root / "judging", current,
                                          backend, resume=resume,
                                          execution_authorized=True, spending_authorized=True)

    async def test_all_generation_dependencies_must_match_across_source_shards(self):
        left, right = [self.source / run["run_id"] for run in self.runs]
        path = right / "manifest.json"
        original = path.read_bytes()
        for name in ("budget.py", "artifacts.py", "scoring.py"):
            with self.subTest(dependency=name):
                manifest = json.loads(original)
                manifest["source_files_sha256"][name] = "0" * 64
                manifest["source_runtime_sha256"] = digest({
                    "runtime": manifest["runtime"],
                    "source_files_sha256": manifest["source_files_sha256"]})
                path.write_bytes(canonical_bytes(manifest))
                with self.assertRaisesRegex(ValueError, "implementation differs"):
                    plan_judging([left, right], self.profile)
                path.write_bytes(original)

    async def test_missing_generation_dependency_is_not_an_older_compatible_profile(self):
        directory = self.source / self.runs[0]["run_id"]
        path = directory / "manifest.json"
        manifest = json.loads(path.read_bytes())
        manifest["source_files_sha256"].pop("budget.py")
        manifest["source_runtime_sha256"] = digest({
            "runtime": manifest["runtime"], "source_files_sha256": manifest["source_files_sha256"]})
        path.write_bytes(canonical_bytes(manifest))
        with self.assertRaisesRegex(ValueError, "fingerprints are missing"):
            plan_judging(directory, self.profile)

    async def test_shared_helper_change_blocks_both_replay_and_paid_resume(self):
        await self.judge()
        actual = deferred_judging.source_sha256
        for helper in ("artifacts.py", "budget.py", "simulation_artifacts.py",
                       "execution.py", "simulation_execution.py"):
            def changed(path, selected=helper):
                return "0" * 64 if Path(path).name == selected else actual(path)
            with self.subTest(helper=helper), patch.object(deferred_judging, "source_sha256", side_effect=changed):
                with self.assertRaisesRegex(ValueError, "judging_implementation"):
                    replay_judging(self.source, self.root / "judging", self.profile)
                http = HTTP()
                with self.assertRaisesRegex(ValueError, "judging_implementation"):
                    await self.judge(http=http, resume=True)
                self.assertEqual(http.requests, [])

    async def test_actor_payload_edits_after_audit_cannot_finish_judging(self):
        directory = self.source / self.runs[0]["run_id"]
        for filename in ("town.json", "trace.jsonl", "agent_histories.json"):
            with self.subTest(payload=filename):
                path = directory / filename
                original, before = path.read_bytes(), _hashes(self.source)
                current = copy.deepcopy(self.profile)
                current["profile_id"] = "mutated-" + filename.replace(".", "-")
                http = _MutatingHTTP(lambda p=path, data=original: p.write_bytes(data + b"\n"))
                with self.assertRaisesRegex(ValueError, "source.*changed"):
                    await self.judge(current=current, http=http)
                after = _hashes(self.source)
                self.assertEqual({name for name in before if before[name] != after[name]},
                                 {path.relative_to(self.source).as_posix()})
                self.assertTrue(http.urls)
                self.assertTrue(all("anthropic.com" in url for url in http.urls))
                path.write_bytes(original)

    async def make_collection(self, name, *, archived_failure=False):
        source = self.root / name
        providers = approved_test_manifest(self.config)
        providers["routes"] = {key: route for key, route in providers["routes"].items()
                               if key in {run["model_key"] for run in self.runs}}
        runs, allocation = allocate_runs(self.config, self.runs)
        ledger_path = self.root / (name + "-actor-ledger.jsonl")
        async def collect(http, **flags):
            with BudgetLedger(ledger_path, "1") as ledger:
                backend = ProviderBackend(providers, ledger, transport=http, evidence_kind="mocked_provider")
                return await collect_simulations(self.config, providers, runs, source, backend,
                    allocation=allocation, execution_authorized=True, spending_authorized=True, **flags)
        if archived_failure:
            with self.assertRaisesRegex(ValueError, "incomplete town"):
                await collect(_FirstChatEmpty())
            await collect(MockHTTP(), resume=True, regenerate_failed=True)
        else:
            await collect(MockHTTP())
        return source

    async def test_collection_control_edits_after_audit_cannot_finish_judging(self):
        source = await self.make_collection("controlled")
        for filename in ("execution_plan.json", "budget_checkpoint.json"):
            with self.subTest(control=filename):
                path = source / filename
                original, before = path.read_bytes(), _hashes(source)
                current = copy.deepcopy(self.profile)
                current["profile_id"] = "changed-" + filename.replace(".", "-")
                http = _MutatingHTTP(lambda p=path, data=original: p.write_bytes(data + b"\n"))
                with self.assertRaisesRegex(ValueError, "source.*changed"):
                    await self.judge(source=source, current=current, http=http)
                after = _hashes(source)
                self.assertEqual({name for name in before if before[name] != after[name]}, {filename})
                path.write_bytes(original)

    async def test_archived_payload_and_archive_inventory_remain_bound(self):
        source = await self.make_collection("archived", archived_failure=True)
        trace = next((source / "_incomplete").glob("attempt-*/*/trace.jsonl"))
        original, before = trace.read_bytes(), _hashes(source)
        http = _MutatingHTTP(lambda: trace.write_bytes(original + b"\n"))
        with self.assertRaisesRegex(ValueError, "source.*changed"):
            await self.judge(source=source, http=http)
        after = _hashes(source)
        self.assertEqual({name for name in before if before[name] != after[name]},
                         {trace.relative_to(source).as_posix()})
        trace.write_bytes(original)
        current = copy.deepcopy(self.profile)
        current["profile_id"] = "new-archive-entry"
        added = source / "_incomplete" / "attempt-999"
        http = _MutatingHTTP(lambda: added.mkdir())
        with self.assertRaisesRegex(ValueError, "inventory changed"):
            await self.judge(source=source, current=current, http=http)
        self.assertEqual(_hashes(source), before)


if __name__ == "__main__":
    unittest.main()
