"""Native adaptive judge payloads use injected transport only."""
import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_providers import manifest
from truth_discount.budget import BudgetLedger
from truth_discount.contracts import GenerationRequest
from truth_discount.providers import ProviderBackend, ProviderError


class AdaptiveJudgeProviderTests(unittest.TestCase):
    def test_effort_and_json_schema_are_siblings_and_thinking_usage_is_not_double_counted(self):
        with tempfile.TemporaryDirectory() as directory, \
             BudgetLedger(Path(directory) / "ledger.jsonl", "1") as ledger, \
             patch.dict(os.environ, {"TRUTH_DISCOUNT_UNIT_TEST_KEY": "FAKE_NOT_REAL"}):
            configuration = manifest("Anthropic")
            configuration["routes"]["agent"]["model_id"] = "claude-sonnet-5-5"
            calls = []
            def transport(method, url, headers, body, timeout_seconds):
                calls.append(deepcopy(body))
                return {"id": "mock_adaptive", "model": body["model"], "stop_reason": "end_turn",
                        "content": [{"type": "thinking", "thinking": "not a user-facing answer"},
                                    {"type": "text", "text": json.dumps({"label": "UNCERTAIN", "quote": "Maybe."})}],
                        "usage": {"input_tokens": 100, "output_tokens": 30, "cache_read_input_tokens": 0,
                                  "cache_creation_input_tokens": 0, "output_tokens_details": {"thinking_tokens": 10}}}
            backend = ProviderBackend(configuration, ledger, transport=transport, evidence_kind="mocked_provider")
            settings = {"max_tokens": 1024, "thinking": {"type": "adaptive"}, "effort": "low",
                        "structured_output": {"label_enum_from": "judging_and_scoring.categorical_labels",
                                              "required_fields": ["label", "quote"]}}
            request = GenerationRequest([{"role": "user", "content": "Classify this quote: Maybe."}],
                                         settings, "agent", "judge", 5, None, 0)
            response = asyncio.run(backend.generate(request))
            self.assertEqual(calls[0]["thinking"], {"type": "adaptive"})
            self.assertEqual(set(calls[0]["output_config"]), {"effort", "format"})
            self.assertEqual(calls[0]["output_config"]["effort"], "low")
            self.assertEqual(response.usage["output_tokens"], 30)
            self.assertEqual(response.usage["reasoning_tokens"], 10)
            self.assertAlmostEqual(response.usage["cost_usd"], (100 + 30*4)/1e6)
            self.assertEqual(response.native_response["content"][0]["type"], "thinking")
            self.assertEqual(response.native_response["stop_reason"], "end_turn")

    def test_adaptive_settings_never_change_actor_protocol_or_bypass_verification(self):
        with tempfile.TemporaryDirectory() as directory, BudgetLedger(Path(directory)/"ledger.jsonl", "1") as ledger:
            for provider in ("Anthropic", "DeepInfra", "OpenAI"):
                backend = ProviderBackend(manifest(provider), ledger, transport=lambda *a: self.fail("network"),
                                          evidence_kind="mocked_provider")
                settings = {"max_tokens": 1024, "thinking": {"type": "adaptive"}, "effort": "low"}
                for kind in (("chat", "decision") if provider == "Anthropic" else ("judge",)):
                    with self.assertRaises(ProviderError):
                        backend.validate_request(GenerationRequest([{"role": "user", "content": "x"}],
                                                 settings, "agent", kind, 5, 1, 0))
            backend = ProviderBackend(manifest("Anthropic"), ledger, transport=lambda *a: self.fail("network"),
                                      evidence_kind="mocked_provider")
            for effort in ({}, True, "unbounded"):
                with self.assertRaises(ProviderError):
                    backend.validate_request(GenerationRequest([{"role": "user", "content": "x"}],
                        {"max_tokens": 1024, "thinking": {"type": "adaptive"}, "effort": effort},
                        "agent", "judge", 5, 1, 0))

    def test_openai_judge_reasoning_is_profile_bound_without_changing_actors(self):
        with tempfile.TemporaryDirectory() as directory, BudgetLedger(Path(directory)/"ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(manifest("OpenAI"), ledger,
                transport=lambda *a: self.fail("network"), evidence_kind="mocked_provider")
            request = GenerationRequest([{"role": "user", "content": "x"}],
                {"max_tokens": 1024, "reasoning_effort": "low"}, "agent", "judge", 5, None, 0)
            _, body, _, _, _ = backend._prepare(request)
            self.assertEqual(body["reasoning_effort"], "low")
            self.assertEqual(body["max_completion_tokens"], 1024)
            for kind in ("chat", "decision"):
                with self.assertRaises(ProviderError):
                    backend.validate_request(GenerationRequest(request.messages, request.settings,
                                             "agent", kind, 5, 1, 0))
            for conflicting in ({"thinking": {"type": "disabled"}}, {"disable_thinking": True}):
                with self.assertRaises(ProviderError):
                    backend.validate_request(GenerationRequest(request.messages,
                        {**request.settings, **conflicting}, "agent", "judge", 5, None, 0))

    def test_echoed_fake_credentials_are_never_retained_in_native_judge_bodies(self):
        fake_key = 'FAKE-UNIT-KEY-"-ONLY'
        for in_text in (False, True):
            with self.subTest(in_text=in_text), tempfile.TemporaryDirectory() as directory, \
                 patch.dict(os.environ, {"TRUTH_DISCOUNT_UNIT_TEST_KEY": fake_key}), \
                 BudgetLedger(Path(directory)/"ledger.jsonl", "1") as ledger:
                def transport(method, url, headers, body, timeout_seconds):
                    return {"id": "mock", "model": "model-v1", "stop_reason": "end_turn",
                            "content": [{"type": "text", "text": fake_key if in_text else '{}'}],
                            "metadata": {fake_key: ["nested", fake_key]},
                            "usage": {"input_tokens": 10, "output_tokens": 5}}
                backend = ProviderBackend(manifest("Anthropic"), ledger, transport=transport,
                                          evidence_kind="mocked_provider")
                request = GenerationRequest([{"role": "user", "content": "classify"}],
                    {"max_tokens": 250, "thinking": {"type": "disabled"}}, "agent", "judge", 5, None, 0)
                if in_text:
                    with self.assertRaises(ProviderError) as caught:
                        asyncio.run(backend.generate(request))
                    self.assertIsNone(caught.exception.native_response)
                    self.assertNotIn(fake_key, json.dumps(caught.exception.receipt))
                else:
                    self.assertIsNone(asyncio.run(backend.generate(request)).native_response)
                self.assertNotIn(fake_key, ledger.path.read_text())


if __name__ == "__main__":
    unittest.main()
