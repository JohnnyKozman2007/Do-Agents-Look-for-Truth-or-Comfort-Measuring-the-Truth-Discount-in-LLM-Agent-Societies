"""Provider protocol integration uses fake credentials and injected HTTP only."""
from __future__ import annotations

import asyncio
from contextlib import redirect_stderr, redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from truth_discount.cli import main
from truth_discount.config import load_config
from truth_discount.contracts import clone
from truth_discount.execution import plan, select_runs, collect

ROOT = Path(__file__).resolve().parents[1]


def approved_test_manifest(config):
    routes = {}
    for model in config["models"]["agent_models"] + config["models"]["judge_models"][:1]:
        anth = model["provider"] == "Anthropic"
        routes[model["key"]] = {
            "provider": model["provider"], "model_id": model["model_id"],
            "endpoint": "https://api.anthropic.com/v1/messages" if anth else
                        "https://api.deepinfra.com/v1/openai/chat/completions",
            "api_key_env": "TEST_PROVIDER_KEY", "settings_verified": True,
            "pricing_verified": True, "input_usd_per_million": 0.1,
            "output_usd_per_million": 0.5, "cached_input_usd_per_million": 0.01,
            "max_input_tokens": 32768, "timeout_seconds": 30,
            "thinking_disabled_parameters": {"thinking": {"type": "disabled"}} if anth else {"reasoning_effort": "none"},
            "allow_synchronous_judge": anth,
        }
    return {"version": 1, "approved": True, "routes": routes}


class MockHTTP:
    def __init__(self):
        self.requests = []

    def __call__(self, method, url, headers, body, timeout_seconds):
        self.requests.append({"url": url, "body": clone(body)})
        is_judge = "anthropic.com" in url
        text = (json.dumps({"label": "UNCERTAIN", "quote": "I am unsure about the concert."})
                if is_judge else "SKIP" if body["max_tokens"] == 5 else
                "I am unsure about the concert.")
        if is_judge:
            return {"id": "mock-" + str(len(self.requests)), "model": body["model"],
                    "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                    "usage": {"input_tokens": 100, "output_tokens": 20, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}
        return {"id": "mock-" + str(len(self.requests)), "model": body["model"],
                "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": min(20, body["max_tokens"]), "total_tokens": 100 + min(20, body["max_tokens"]), "prompt_tokens_details": {"cached_tokens": 0}}}


class LiveCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.providers = approved_test_manifest(self.config)
        self.provider_file = self.root / "providers.json"
        self.provider_file.write_text(json.dumps(self.providers))

    def invoke(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(map(str, args)))
        return code, out.getvalue(), err.getvalue()

    def args(self):
        return ("live", "--providers", self.provider_file, "--output", self.root / "output")

    def test_pair_selection_preserves_twins_and_all_cells(self):
        runs = select_runs(self.config)
        self.assertEqual(len(runs), 16)
        self.assertEqual({r["cell_id"] for r in runs}, {1, 2, 3, 4})
        for pair in {r["pair_id"] for r in runs}:
            self.assertEqual({r["condition_type"] for r in runs if r["pair_id"] == pair},
                             {"rumor", "truth_twin"})
        self.assertEqual(len(select_runs(self.config, full_pilot=True)), 624)
        remainder = select_runs(self.config, full_pilot=True, start_pair=1)
        self.assertEqual(len(remainder), 608)
        self.assertFalse({r["run_id"] for r in runs} & {r["run_id"] for r in remainder})
        self.assertEqual(len(runs) + len(remainder), 624)
        with self.assertRaises(ValueError):
            select_runs(self.config, pairs_per_cell=0)

    def test_preview_does_not_read_keys_create_ledger_or_make_network_calls(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch("urllib.request.urlopen", side_effect=AssertionError("no network")):
            code, out, err = self.invoke(*self.args())
        self.assertEqual(code, 0, err)
        info = json.loads(out)
        self.assertEqual(info["planned_towns"], 16)
        self.assertEqual(info["provider_api_calls"], 0)
        self.assertFalse(info["spending_authorized_by_planning"])
        self.assertFalse((self.root / "output").exists())

    def test_preview_lists_unapproved_gates_without_claiming_access(self):
        self.providers["approved"] = False
        self.provider_file.write_text(json.dumps(self.providers))
        code, out, err = self.invoke(*self.args())
        self.assertEqual(code, 0, err)
        info = json.loads(out)
        self.assertEqual(info["status"], "blocked")
        self.assertFalse(info["api_access_validated"])

    def test_execute_requires_explicit_hold_release_and_budget(self):
        code, _, err = self.invoke(*self.args(), "--execute")
        self.assertEqual(code, 1)
        self.assertIn("spending hold", err)
        code, _, err = self.invoke(*self.args(), "--execute", "--spending-authorized")
        self.assertEqual(code, 1)
        self.assertIn("--ledger", err)
        self.assertFalse((self.root / "output").exists())

    def test_model_substitution_and_silent_batch_override_block_plan(self):
        runs = select_runs(self.config)
        key = runs[0]["model_key"]
        altered = copy.deepcopy(self.providers)
        altered["routes"][key]["model_id"] = "unagreed-model"
        self.assertTrue(any("changes configured model" in e for e in plan(self.config, altered, runs)["execution_gates"]))
        judge = self.config["models"]["judge_models"][0]["key"]
        altered = copy.deepcopy(self.providers)
        altered["routes"][judge]["allow_synchronous_judge"] = False
        self.assertTrue(any("batch" in e for e in plan(self.config, altered, runs)["execution_gates"]))

    def test_mocked_adapter_collection_replays_and_remains_nonempirical(self):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        from truth_discount.artifacts import audit_town, summarize
        runs = select_runs(self.config)[:2]
        http = MockHTTP()
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("no network")), \
             BudgetLedger(self.root / "ledger.json", "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http,
                                      evidence_kind="mocked_provider")
            result = asyncio.run(collect(self.config, self.providers, runs, self.root / "output", backend))
        self.assertEqual(result["evidence_kind"], "mocked_provider")
        self.assertEqual(result["provider_api_calls"], 0)
        self.assertGreater(result["simulated_provider_requests"], 0)
        self.assertEqual(result["towns"], 2)
        self.assertFalse(result["study_results_generated"])
        for run in runs:
            town = audit_town(self.root / "output" / run["run_id"])
            self.assertFalse(town["study_eligible"])
            self.assertEqual(town["token_usage"]["provider_api_calls"], 0)
            self.assertEqual(town["diagnostic_limits"]["scene_3_poster_evidence_passed"],
                             "Checked plus artist/board keywords, not semantic evidence-transfer adjudication")
        with self.assertRaises(FileExistsError):
            asyncio.run(collect(self.config, self.providers, runs, self.root / "output", backend))

    def test_cli_explicit_execution_uses_mock_transport_and_preserves_zero_actual_calls(self):
        from truth_discount.providers import ProviderBackend
        real_backend = ProviderBackend
        http = MockHTTP()
        def fake_backend(manifest, ledger):
            return real_backend(manifest, ledger, transport=http, evidence_kind="mocked_provider")
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("truth_discount.providers.ProviderBackend", side_effect=fake_backend), \
             patch("socket.create_connection", side_effect=AssertionError("no network")):
            code, out, err = self.invoke(*self.args(), "--execute", "--spending-authorized",
                                         "--ledger", self.root / "ledger.json", "--budget-usd", "1",
                                         "--model-key", self.config["models"]["agent_models"][0]["key"])
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["towns"], 8)
        self.assertEqual(result["provider_api_calls"], 0)
        self.assertGreater(result["simulated_provider_requests"], 0)
        self.assertFalse(result["budget"]["blocked"])

    def test_insufficient_budget_saves_failed_town_before_any_http_request(self):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend, ProviderError
        from truth_discount.artifacts import audit_town
        http = MockHTTP()
        runs = select_runs(self.config)[:2]
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             BudgetLedger(self.root / "ledger.json", "0.000001") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            with self.assertRaises(ProviderError):
                asyncio.run(collect(self.config, self.providers, runs, self.root / "output", backend))
        self.assertEqual(http.requests, [])
        town = audit_town(self.root / "output" / runs[0]["run_id"])
        self.assertNotEqual(town["run_status"], "completed")
        self.assertEqual(town["token_usage"]["simulated_provider_requests"], 0)

    def test_charged_empty_chat_preserves_usage_in_failed_bundle(self):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        from truth_discount.artifacts import audit_town
        class EmptyChatHTTP(MockHTTP):
            def __call__(self, method, url, headers, body, timeout_seconds):
                response = super().__call__(method, url, headers, body, timeout_seconds)
                if "choices" in response and body["max_tokens"] != 5:
                    response["choices"][0]["message"]["content"] = ""
                return response
        http = EmptyChatHTTP()
        runs = select_runs(self.config)[:2]
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             BudgetLedger(self.root / "ledger.json", "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            with self.assertRaises(ValueError):
                asyncio.run(collect(self.config, self.providers, runs, self.root / "output", backend))
        town = audit_town(self.root / "output" / runs[0]["run_id"])
        charged_failures = [c for c in town["calls"] if c["status"] == "malformed_response"]
        self.assertTrue(charged_failures)
        self.assertTrue(all(c["provider_api_calls"] == 1 and c["cost_usd"] > 0 for c in charged_failures))
        self.assertGreater(town["token_usage"]["cost_usd"], 0)

    def test_missing_judge_key_is_detected_before_agent_generation(self):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend, ProviderError
        providers = copy.deepcopy(self.providers)
        judge = self.config["models"]["judge_models"][0]["key"]
        providers["routes"][judge]["api_key_env"] = "MISSING_TEST_JUDGE_KEY"
        http = MockHTTP()
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}, clear=True), \
             BudgetLedger(self.root / "ledger.json", "1") as ledger:
            backend = ProviderBackend(providers, ledger, transport=http, evidence_kind="mocked_provider")
            with self.assertRaises(ProviderError):
                asyncio.run(collect(self.config, providers, select_runs(self.config)[:2],
                                    self.root / "output", backend))
        self.assertEqual(http.requests, [])
        self.assertFalse((self.root / "output").exists())

    def collect_with(self, http, runs, *, cap="1", resume=False, towns=1, providers=None,
                     ledger_path=None):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        providers = providers or self.providers
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             BudgetLedger(ledger_path or self.root / "ledger.jsonl", cap) as ledger:
            backend = ProviderBackend(providers, ledger, transport=http, evidence_kind="mocked_provider")
            try:
                return asyncio.run(collect(self.config, providers, runs, self.root / "output", backend,
                                           resume=resume, max_concurrent_towns=towns))
            finally:
                self.budget = ledger.summary()

    def test_crash_reconcile_and_resume_skip_verified_towns(self):
        from truth_discount.artifacts import audit_town
        from truth_discount.providers import ProviderError

        class DropsOneRequest(MockHTTP):
            def __call__(self, method, url, headers, body, timeout_seconds):
                if len(self.requests) == 69:   # inside the second town
                    self.requests.append({"url": url, "body": clone(body)})
                    raise ConnectionResetError("connection dropped after sending")
                return super().__call__(method, url, headers, body, timeout_seconds)

        runs = select_runs(self.config)[:4]
        with self.assertRaises(ProviderError):
            self.collect_with(DropsOneRequest(), runs)
        self.assertEqual(self.budget["block_reasons"], ["unknown_charge"])
        self.assertTrue(audit_town(self.root / "output" / runs[0]["run_id"])["run_status"] == "completed")
        self.assertFalse((self.root / "output" / runs[2]["run_id"]).exists())

        # The unclear charge holds the run until someone records what was billed.
        with self.assertRaisesRegex(ValueError, "blocked"):
            self.collect_with(MockHTTP(), runs, resume=True)
        code, out, err = self.invoke("ledger", "--ledger", self.root / "ledger.jsonl", "--budget-usd", "1")
        self.assertEqual(code, 0, err)
        unknown = json.loads(out)["unknown_reservations"]
        self.assertEqual(len(unknown), 1)
        code, out, err = self.invoke("ledger", "--ledger", self.root / "ledger.jsonl", "--budget-usd", "1",
                                     "--reconcile", unknown[0]["id"], "--actual-usd", "0.00002")
        self.assertEqual(code, 1)
        self.assertIn("--note", err)
        code, out, err = self.invoke("ledger", "--ledger", self.root / "ledger.jsonl", "--budget-usd", "1",
                                     "--reconcile", unknown[0]["id"], "--actual-usd", "0.00002",
                                     "--note", "DeepInfra usage page")
        self.assertEqual(code, 0, err)
        self.assertFalse(json.loads(out)["budget"]["blocked"])
        spent_before = json.loads(out)["budget"]["settled_usd"]

        http = MockHTTP()
        result = self.collect_with(http, runs, resume=True)
        self.assertEqual(result["skipped_verified_towns"], 1)
        self.assertEqual(result["set_aside_towns"], ["_incomplete/attempt-1/" + runs[1]["run_id"]])
        self.assertEqual(result["completed_towns"], 4)
        self.assertEqual(len(http.requests), 3 * 66)
        kept = audit_town(self.root / "output" / result["set_aside_towns"][0])
        self.assertNotEqual(kept["run_status"], "completed")
        skipped_cost = audit_town(self.root / "output" / runs[0]["run_id"])["token_usage"]["cost_usd"]
        self.assertAlmostEqual(self.budget["settled_usd"],
                               spent_before + result["simulated_cost_usd"] - skipped_cost, places=9)
        self.assertEqual(result["budget_accounting"]["budget"]["settled_usd"], self.budget["settled_usd"])
        accounting = result["receipt_accounting"]
        self.assertEqual(accounting["archived_attempts"]["town_count"], 1)
        self.assertEqual(accounting["completed_active_towns"]["town_count"], 4)
        self.assertIsNone(accounting["all_attempts"]["simulated_cost_usd"])
        self.assertTrue(accounting["all_attempts"]["reconciliation_required"])
        self.assertGreater(self.budget["settled_usd"], result["simulated_cost_usd"])
        log = (self.root / "output" / "resume_log.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(json.loads(log[-1])["skipped_verified_towns"], 1)

    def test_resume_needs_the_same_plan_and_existing_output(self):
        runs = select_runs(self.config)[:2]
        with self.assertRaisesRegex(ValueError, "nothing to resume"):
            self.collect_with(MockHTTP(), runs, resume=True)
        self.collect_with(MockHTTP(), runs)
        with self.assertRaisesRegex(ValueError, "run_manifest_sha256"):
            self.collect_with(MockHTTP(), select_runs(self.config)[2:4], resume=True)
        result = self.collect_with(MockHTTP(), runs, resume=True)
        self.assertEqual((result["skipped_verified_towns"], result["set_aside_towns"]), (2, []))

    def test_resume_rejects_fresh_ledger_before_keys_or_calls(self):
        from truth_discount.providers import ProviderBackend, ProviderError

        class DropsOneRequest(MockHTTP):
            def __call__(self, *args):
                if len(self.requests) == 69:
                    self.requests.append({"synthetic": "disconnect"})
                    raise ConnectionResetError("synthetic interrupted call")
                return super().__call__(*args)

        runs = select_runs(self.config)[:4]
        with self.assertRaises(ProviderError):
            self.collect_with(DropsOneRequest(), runs)
        self.assertTrue(self.budget["blocked"])
        original = (self.root / "ledger.jsonl").read_bytes()
        http = MockHTTP()
        with patch.object(ProviderBackend, "validate_credentials", side_effect=AssertionError("key read")):
            with self.assertRaisesRegex(ValueError, "original ledger identity"):
                self.collect_with(http, runs, resume=True, ledger_path=self.root / "replacement.jsonl")
        self.assertEqual(http.requests, [])
        self.assertEqual(original, (self.root / "ledger.jsonl").read_bytes())

    def test_resume_rejects_same_identity_with_rewound_spending_history(self):
        from truth_discount.providers import ProviderBackend
        runs = select_runs(self.config)[:2]
        self.collect_with(MockHTTP(), runs)
        path = self.root / "ledger.jsonl"
        path.write_bytes(path.read_bytes().splitlines(keepends=True)[0])
        http = MockHTTP()
        with patch.object(ProviderBackend, "validate_credentials", side_effect=AssertionError("key read")):
            with self.assertRaisesRegex(ValueError, "checkpoint|history|prefix"):
                self.collect_with(http, runs, resume=True)
        self.assertEqual(http.requests, [])

    def test_resume_rejects_valid_bundle_from_different_config_or_provider(self):
        from truth_discount.artifacts import audit_town
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        from truth_discount.runner import run_town
        for mismatch in ("config", "provider"):
            with self.subTest(mismatch=mismatch):
                self.root = Path(self.temp.name) / mismatch
                self.root.mkdir()
                runs = select_runs(self.config)[:2]
                self.collect_with(MockHTTP(), runs)
                other_config, other_providers = copy.deepcopy(self.config), copy.deepcopy(self.providers)
                if mismatch == "config":
                    other_config["meta"]["town_name"] = "Synthetic Alternative Town"
                else:
                    other_providers["routes"][runs[0]["model_key"]]["max_concurrent_requests"] = 2
                with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
                     BudgetLedger(self.root / "foreign.jsonl", "1") as ledger:
                    backend = ProviderBackend(other_providers, ledger, transport=MockHTTP(),
                                              evidence_kind="mocked_provider")
                    asyncio.run(run_town(other_config, runs[0], backend, self.root / "foreign"))
                foreign = self.root / "foreign" / runs[0]["run_id"]
                self.assertEqual(audit_town(foreign)["run_status"], "completed")
                victim = self.root / "output" / runs[0]["run_id"]
                victim.rename(self.root / "preserved-original")
                shutil.copytree(foreign, victim)
                http = MockHTTP()
                with patch.object(ProviderBackend, "validate_credentials", side_effect=AssertionError("key read")):
                    with self.assertRaisesRegex(ValueError, mismatch + ".*differs from execution plan"):
                        self.collect_with(http, runs, resume=True)
                self.assertEqual(http.requests, [])
                self.assertTrue(victim.exists())

    def test_resume_rejects_evidence_kind_change_before_keys(self):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        runs = select_runs(self.config)[:2]
        self.collect_with(MockHTTP(), runs)
        with BudgetLedger(self.root / "ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=MockHTTP(),
                                      evidence_kind="development_pilot")
            with patch.object(backend, "validate_credentials", side_effect=AssertionError("key read")):
                with self.assertRaisesRegex(ValueError, "evidence kind"):
                    asyncio.run(collect(self.config, self.providers, runs, self.root / "output", backend, resume=True))

    def test_resume_rejects_missing_anchor_unverifiable_town_and_bad_archives(self):
        from truth_discount.providers import ProviderBackend
        for issue in ("anchor", "town", "archive_file", "empty_archive"):
            with self.subTest(issue=issue):
                self.root = Path(self.temp.name) / issue
                self.root.mkdir()
                runs = select_runs(self.config)[:2]
                self.collect_with(MockHTTP(), runs)
                out = self.root / "output"
                if issue == "anchor":
                    (out / "budget_checkpoint.json").unlink()
                elif issue == "town":
                    (out / runs[0]["run_id"] / "manifest.json").unlink()
                elif issue == "archive_file":
                    (out / "_incomplete").mkdir()
                    (out / "_incomplete" / "unexpected").write_text("preserve")
                else:
                    (out / "_incomplete" / "attempt-1").mkdir(parents=True)
                http = MockHTTP()
                with patch.object(ProviderBackend, "validate_credentials", side_effect=AssertionError("key read")):
                    with self.assertRaises((ValueError, OSError)):
                        self.collect_with(http, runs, resume=True)
                self.assertEqual(http.requests, [])

    def test_anchor_write_failure_prevents_submission_and_holds_reservation(self):
        import truth_discount.execution as execution
        from truth_discount.providers import ProviderError
        original = execution._atomic_json
        anchor_writes = []
        def fails_after_initial_anchor(path, value):
            if path.name == "budget_checkpoint.json":
                anchor_writes.append(value)
                if len(anchor_writes) > 1:
                    raise OSError("synthetic anchor storage failure")
            return original(path, value)
        http = MockHTTP()
        with patch.object(execution, "_atomic_json", side_effect=fails_after_initial_anchor):
            with self.assertRaises(ProviderError):
                self.collect_with(http, select_runs(self.config)[:2])
        self.assertEqual(http.requests, [])
        self.assertTrue(self.budget["blocked"])
        self.assertGreater(self.budget["reserved_usd"], 0)

    def test_checkpoint_survives_brief_windows_file_locks(self):
        # The 7 Nov smoke test lost a town when Windows briefly refused to replace
        # budget_checkpoint.json; a collection now rides out such collisions.
        import truth_discount.execution as execution
        real_replace, state = os.replace, {"calls": 0}
        def sometimes_locked(source, target):
            state["calls"] += 1
            if Path(target).name == "budget_checkpoint.json" and state["calls"] % 7 == 0:
                raise PermissionError(5, "Access is denied")   # someone else has the file open
            return real_replace(source, target)
        http = MockHTTP()
        with patch.object(execution.os, "replace", side_effect=sometimes_locked), \
             patch.object(execution.time, "sleep"):
            result = self.collect_with(http, select_runs(self.config)[:2])
        self.assertEqual(result["completed_towns"], 2)
        self.assertFalse(self.budget["blocked"])
        self.assertEqual(self.budget["reserved_usd"], 0)
        self.assertEqual(list((self.root / "output").glob("budget_checkpoint.json.*")), [])

    def test_checkpoint_lock_that_never_clears_still_stops_safely(self):
        import truth_discount.execution as execution
        from truth_discount.providers import ProviderError
        real_replace, state = os.replace, {"anchors": 0}
        def locked_after_first(source, target):
            if Path(target).name == "budget_checkpoint.json":
                state["anchors"] += 1
                if state["anchors"] > 1:
                    raise PermissionError(5, "Access is denied")
            return real_replace(source, target)
        http = MockHTTP()
        with patch.object(execution.os, "replace", side_effect=locked_after_first), \
             patch.object(execution.time, "sleep") as sleep:
            with self.assertRaises(ProviderError):
                self.collect_with(http, select_runs(self.config)[:2])
        self.assertEqual(http.requests, [])
        self.assertTrue(self.budget["blocked"])
        self.assertEqual(sleep.call_count, execution.REPLACE_ATTEMPTS - 1)

    def test_concurrent_towns_share_one_request_limit_and_budget(self):
        providers = copy.deepcopy(self.providers)
        for route in providers["routes"].values():
            route["max_concurrent_requests"] = 3
        from truth_discount.artifacts import audit_town
        mock, now, peak = MockHTTP(), {}, {}

        async def http(method, url, headers, body, timeout_seconds):
            model = body["model"]
            now[model] = now.get(model, 0) + 1
            peak[model] = max(peak.get(model, 0), now[model])
            await asyncio.sleep(.001)
            now[model] -= 1
            return mock(method, url, headers, body, timeout_seconds)

        runs = select_runs(self.config)[:4]
        result = self.collect_with(http, runs, towns=4, providers=providers)
        self.assertEqual(result["completed_towns"], 4)
        self.assertEqual(max(peak.values()), 3)
        times = [audit_town(self.root / "output" / r["run_id"])["timestamps"] for r in runs]
        self.assertLess(max(t["started_utc"] for t in times), min(t["finished_utc"] for t in times))
        self.assertAlmostEqual(self.budget["settled_usd"], result["simulated_cost_usd"], places=9)
        self.assertEqual(self.budget["reserved_usd"], 0)

    def test_budget_limit_stops_new_towns_and_is_never_exceeded(self):
        from truth_discount.providers import ProviderError
        for towns in (1, 2):
            with self.subTest(concurrent_towns=towns):
                self.root = Path(self.temp.name) / f"limit-{towns}"
                self.root.mkdir()
                runs = select_runs(self.config)[:4]
                with self.assertRaises(ProviderError):
                    self.collect_with(MockHTTP(), runs, cap="0.043", towns=towns)
                saved = [r for r in runs if (self.root / "output" / r["run_id"]).exists()]
                self.assertLess(len(saved), 4)
                if towns == 1:   # the first town fits under the cap; the run stops at a later one
                    from truth_discount.artifacts import audit_town
                    first = audit_town(self.root / "output" / saved[0]["run_id"])
                    self.assertEqual(first["run_status"], "completed")
                else:            # both running towns drew on one cap; no third town started
                    self.assertEqual(len(saved), 2)
                self.assertLessEqual(self.budget["settled_usd"] + self.budget["reserved_usd"], 0.043)
                self.assertFalse(self.budget["blocked"])

    def test_ledger_command_refuses_missing_file_and_stray_flags(self):
        code, _, err = self.invoke("ledger", "--ledger", self.root / "none.jsonl", "--budget-usd", "1")
        self.assertEqual(code, 1)
        self.assertIn("does not exist", err)
        self.assertFalse((self.root / "none.jsonl").exists())
        from truth_discount.budget import BudgetLedger
        BudgetLedger(self.root / "ledger.jsonl", "1").close()
        code, _, err = self.invoke("ledger", "--ledger", self.root / "ledger.jsonl", "--budget-usd", "1",
                                   "--actual-usd", "0.1")
        self.assertEqual(code, 1)
        code, _, err = self.invoke("ledger", "--ledger", self.root / "ledger.jsonl", "--budget-usd", "2")
        self.assertEqual(code, 1)
        self.assertIn("cap cannot be changed", err)

    def test_backend_manifest_cannot_differ_from_preflight_plan(self):
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        altered = copy.deepcopy(self.providers)
        key = self.config["models"]["agent_models"][0]["key"]
        altered["routes"][key]["model_id"] = "unagreed-model"
        http = MockHTTP()
        with BudgetLedger(self.root / "ledger.json", "1") as ledger:
            backend = ProviderBackend(altered, ledger, transport=http, evidence_kind="mocked_provider")
            with self.assertRaisesRegex(ValueError, "differs"):
                asyncio.run(collect(self.config, self.providers, select_runs(self.config)[:2],
                                    self.root / "output", backend))
        self.assertEqual(http.requests, [])
        self.assertFalse((self.root / "output").exists())


if __name__ == "__main__":
    unittest.main()
