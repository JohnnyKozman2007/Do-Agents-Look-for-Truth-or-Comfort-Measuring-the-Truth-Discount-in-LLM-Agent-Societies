"""Regression tests for the PR #10 review fixes. Mocked/fixture only; no network or real keys."""
import asyncio
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
from test_live_cli import approved_test_manifest, MockHTTP
from truth_discount import deferred_judging, scoring
from truth_discount.budget import BudgetLedger
from truth_discount.config import build_manifest, load_config
from truth_discount.deferred_judging import (_writer_lock, compare_judgments, judge_collection,
                                             load_judge_profile, parser_sha256, replay_judging)
from truth_discount.execution import select_runs
from truth_discount.providers import ProviderBackend
from truth_discount.runner import run_town
from truth_discount.simulation_artifacts import (GENERATION_SOURCE_FILES, generation_source_hashes,
                                                 source_sha256)
from truth_discount.simulation_execution import allocate_runs, collect_simulations, review_simulations
from truth_discount.fixtures import FixtureBackend

ROOT = Path(__file__).resolve().parents[1]


class LineEndingAndFingerprintTests(unittest.TestCase):
    def test_crlf_checkout_hashes_like_lf(self):
        lf = Path(scoring.__file__).read_bytes().replace(b"\r\n", b"\n")
        with tempfile.TemporaryDirectory() as temp:
            crlf = Path(temp) / "scoring.py"
            crlf.write_bytes(lf.replace(b"\n", b"\r\n"))
            self.assertEqual(source_sha256(crlf), parser_sha256())

    def test_every_judge_template_pins_the_current_parser_and_loads(self):
        templates = sorted((ROOT / "configs/judges").glob("*.example.json"))
        self.assertEqual(len(templates), 4)
        for path in templates:
            self.assertEqual(json.loads(path.read_text())["parser"]["sha256"], parser_sha256(), path.name)
            load_judge_profile(path)

    def test_repository_forces_lf_checkouts(self):
        self.assertIn("eol=lf", (ROOT / ".gitattributes").read_text())

    def test_fingerprint_covers_generation_modules_only(self):
        hashes = generation_source_hashes()
        self.assertEqual(tuple(sorted(hashes)), tuple(sorted(GENERATION_SOURCE_FILES)))
        for unrelated in ("cli.py", "deferred_judging.py", "judge_selection.py", "simulation_execution.py"):
            self.assertNotIn(unrelated, hashes)
        config = load_config(ROOT / "configs/pilot_config.json")
        with tempfile.TemporaryDirectory() as temp:
            run = build_manifest(config)[0]
            asyncio.run(run_town(config, run, FixtureBackend(), Path(temp), defer_judging=True))
            manifest = json.loads((Path(temp) / run["run_id"] / "manifest.json").read_text())
        self.assertEqual(manifest["source_files_sha256"], hashes)


class _FirstChatEmpty(MockHTTP):
    """Return one empty actor chat reply (a known-cost malformed generation)."""
    def __init__(self):
        super().__init__()
        self.failed = False

    def __call__(self, method, url, headers, body, timeout_seconds):
        response = super().__call__(method, url, headers, body, timeout_seconds)
        if not self.failed and body["max_tokens"] != 5:
            self.failed = True
            response["choices"][0]["message"]["content"] = "   "
        return response


class CollectionResumeAndStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.providers = approved_test_manifest(self.config)
        self.providers["routes"] = {k: v for k, v in self.providers["routes"].items()
                                    if k in {r["key"] for r in self.config["models"]["agent_models"]}}
        self.selection = select_runs(self.config, [self.config["models"]["agent_models"][0]["key"]])[:4]

    def collect(self, output, ledger_path, http, runs, allocation, **flags):
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("network forbidden")), \
             BudgetLedger(ledger_path, "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            return asyncio.run(collect_simulations(self.config, self.providers, runs, output, backend,
                allocation=allocation, max_concurrent_towns=1,
                execution_authorized=True, spending_authorized=True, **flags))

    def test_one_finished_shard_is_not_reported_as_the_whole_generation(self):
        for index in range(2):
            runs, allocation = allocate_runs(self.config, self.selection, shard_count=2, shard_index=index)
            self.collect(self.root / str(index), self.root / f"ledger-{index}.jsonl", MockHTTP(), runs, allocation)
        single = review_simulations(self.root / "0")
        self.assertEqual(single["status"], "shards_complete")
        self.assertFalse(single["full_allocation_present"])
        both = review_simulations([self.root / "0", self.root / "1"])
        self.assertEqual(both["status"], "generation_complete")

    def test_failed_town_needs_explicit_regeneration_and_is_counted_per_cell(self):
        runs, allocation = allocate_runs(self.config, self.selection)
        output, ledger_path = self.root / "output", self.root / "ledger.jsonl"
        with self.assertRaisesRegex(ValueError, "incomplete town"):
            self.collect(output, ledger_path, _FirstChatEmpty(), runs, allocation)
        status = review_simulations(output)
        self.assertEqual(status["failed_generation_attempts"], 1)
        http = MockHTTP()
        with self.assertRaisesRegex(ValueError, "regenerate"):
            self.collect(output, ledger_path, http, runs, allocation, resume=True)
        self.assertEqual(http.requests, [])
        result = self.collect(output, ledger_path, MockHTTP(), runs, allocation,
                              resume=True, regenerate_failed=True)
        self.assertEqual(result["status"], "generation_complete")
        self.assertEqual(result["failed_generation_attempts"], 1)
        self.assertEqual(sum(result["failed_generation_attempts_by_cell"].values()), 1)
        log = [json.loads(line) for line in (output / "resume_log.jsonl").read_text().splitlines()]
        self.assertTrue(log[-1]["regenerate_failed"])


class JudgingReplayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / "source", self.root / "grading"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        await run_town(self.config, build_manifest(self.config)[0], FixtureBackend(), self.source,
                       defer_judging=True)
        self.profile = profile(self.config)
        env = patch.dict(os.environ, {"DEFERRED_TEST_KEY": KEY})
        env.start()
        self.addCleanup(env.stop)

    async def judge(self, current=None, *, resume=False):
        current = current or self.profile
        with BudgetLedger(self.root / f"ledger-{current['profile_id']}.jsonl", "1") as ledger:
            backend = ProviderBackend(current["provider_manifest"], ledger, transport=HTTP(),
                                      evidence_kind="mocked_provider")
            return await judge_collection(self.source, self.output, current, backend, resume=resume,
                                          execution_authorized=True, spending_authorized=True)

    async def test_each_town_is_audited_once_per_judge_run(self):
        with patch.object(deferred_judging, "_source", wraps=deferred_judging._source) as audit:
            result = await self.judge()
        self.assertEqual(audit.call_count, 1)
        self.assertEqual(result["valid_first_attempt"], 12)

    async def test_comparison_audits_the_shared_source_once(self):
        other = profile(self.config, "OpenAI", name="judge-b")
        await self.judge()
        await self.judge(other)
        with patch.object(deferred_judging, "_source", wraps=deferred_judging._source) as audit:
            report = compare_judgments(self.source, [(self.output, self.profile), (self.output, other)])
        self.assertEqual(audit.call_count, 1)
        self.assertEqual(len(report["comparisons"]), 1)

    async def test_read_only_replay_reports_but_resume_refuses_a_different_python(self):
        await self.judge()
        other_build = sys.version.replace(sys.version.split()[0], "3.99.0", 1)
        with patch.object(deferred_judging.sys, "version", other_build):
            replay = replay_judging(self.source, self.output, self.profile)
            self.assertFalse(replay["replay_runtime"]["matches_plan"])
            self.assertEqual(replay["valid_first_attempt"], 12)
            with self.assertRaisesRegex(ValueError, "judging_implementation"):
                await self.judge(resume=True)
        self.assertTrue(replay_judging(self.source, self.output, self.profile)["replay_runtime"]["matches_plan"])

    def test_writer_lock_is_released_for_an_immediate_rerun(self):
        lock = self.root / ".judge.lock"
        with _writer_lock(lock):
            with self.assertRaisesRegex(ValueError, "another process"):
                with _writer_lock(lock):
                    pass
        with _writer_lock(lock):
            pass


if __name__ == "__main__":
    unittest.main()
