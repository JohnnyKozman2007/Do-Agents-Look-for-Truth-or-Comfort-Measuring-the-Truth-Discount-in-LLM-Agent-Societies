"""Provider protocol integration uses fake credentials and injected HTTP only."""
from __future__ import annotations

import asyncio
from contextlib import redirect_stderr, redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
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
