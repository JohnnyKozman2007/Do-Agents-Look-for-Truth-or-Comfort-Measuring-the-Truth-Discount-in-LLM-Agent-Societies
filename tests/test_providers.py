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
from truth_discount.budget import BudgetLedger
from truth_discount.contracts import GenerationRequest, digest
from truth_discount.providers import ProviderBackend, ProviderError, HTTPResponse


KEY = "sk-TEST-ONLY-never-a-live-key"


def manifest(provider="DeepInfra"):
    endpoint = {"DeepInfra": "https://api.deepinfra.com/v1/openai/chat/completions",
                "OpenAI": "https://api.openai.com/v1/chat/completions",
                "Anthropic": "https://api.anthropic.com/v1/messages"}[provider]
    return {"version": 1, "approved": True, "routes": {"agent": {
        "provider": provider, "model_id": "model-v1", "endpoint": endpoint,
        "api_key_env": "TRUTH_DISCOUNT_UNIT_TEST_KEY", "input_usd_per_million": 1.0,
        "output_usd_per_million": 4.0, "cached_input_usd_per_million": .1,
        "max_input_tokens": 8192, "timeout_seconds": 1.0,
        "settings_verified": True, "pricing_verified": True,
        "thinking_disabled_parameters": {"thinking": {"type": "disabled"}} if provider == "Anthropic" else {"reasoning_effort": "none"}}}}


def request(**kwargs):
    values = {"messages": [{"role": "system", "content": "You are a town resident."},
                           {"role": "user", "content": "GO or SKIP?"}],
        "settings": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 5,
                     "disable_thinking": True, "presence_penalty": 0, "frequency_penalty": 0,
                     "scenes": [2, 4], "description": "decision"},
        "model_key": "agent", "kind": "decision", "scene": 2, "seat": 1, "turn": 1}
    values.update(kwargs)
    return GenerationRequest(**values)


def response(**kwargs):
    body = {"id": "request-123", "model": "model-v1", "choices": [{"message": {"content": "GO"}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 3,
                  "prompt_tokens_details": {"cached_tokens": 40},
                  "completion_tokens_details": {"reasoning_tokens": 1}}}
    body.update(kwargs)
    return body


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "budget.json"
        self.ledger = BudgetLedger(self.path, 1)
        self.addCleanup(self.ledger.close)
        self.env = patch.dict(os.environ, {"TRUTH_DISCOUNT_UNIT_TEST_KEY": KEY})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.calls = []

    def backend(self, configuration=None, body=None, transport=None):
        def fake(*args):
            self.calls.append(args)
            return deepcopy(response() if body is None else body)
        return ProviderBackend(configuration or manifest(), self.ledger, transport or fake,
                               evidence_kind="mocked_provider")

    async def test_deepinfra_exact_payload_usage_and_cache_accounting(self):
        backend = self.backend()
        result = await backend.generate(request())
        self.assertEqual(result.text, "GO")
        method, url, headers, payload, timeout = self.calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(url, manifest()["routes"]["agent"]["endpoint"])
        self.assertEqual(headers["Authorization"], "Bearer " + KEY)
        self.assertEqual(payload["reasoning_effort"], "none")
        self.assertEqual(payload["max_tokens"], 5)
        self.assertNotIn("disable_thinking", payload)
        self.assertNotIn("scenes", payload)
        self.assertNotIn("description", payload)
        self.assertEqual(result.usage["input_tokens"], 100)
        self.assertEqual(result.usage["reasoning_tokens"], 1)
        # Completion includes reasoning: do not bill that token twice.
        self.assertAlmostEqual(result.usage["cost_usd"], (60 + 4 + 12) / 1e6)
        self.assertEqual(result.usage["provider_api_calls"], 1)
        self.assertEqual(result.usage["cost_status"], "calculated_from_usage")
        self.assertEqual(result.usage["pricing_sha256"], digest({k: manifest()["routes"]["agent"][k]
            for k in ("input_usd_per_million", "output_usd_per_million", "cached_input_usd_per_million")}))
        self.assertEqual(self.ledger.summary()["reserved_usd"], 0)
        self.assertNotIn(KEY, self.path.read_text())
        self.assertEqual(backend.evidence_kind, "mocked_provider")

    async def test_openai_explicit_route_and_output_token_parameter(self):
        backend = self.backend(manifest("OpenAI"))
        await backend.generate(request())
        self.assertIn("max_completion_tokens", self.calls[0][3])
        self.assertNotIn("max_tokens", self.calls[0][3])

    async def test_native_anthropic_system_schema_and_standard_sync_override(self):
        config = manifest("Anthropic")
        config["routes"]["agent"]["allow_synchronous_judge"] = True
        native = {"id": "msg-123", "model": "model-v1", "content": [{"type": "text", "text": '{"label":"FACT","quote":"concert"}'}],
            "usage": {"input_tokens": 60, "cache_read_input_tokens": 40, "cache_creation_input_tokens": 0,
                      "output_tokens": 3, "output_tokens_details": {"thinking_tokens": 0}}}
        settings = {"max_tokens": 250, "thinking": {"type": "disabled"}, "use_batch_api": True,
            "structured_output": {"label_enum_from": "judging_and_scoring.categorical_labels", "required_fields": ["label", "quote"]}}
        result = await self.backend(config, native).generate(request(kind="judge", settings=settings))
        payload = self.calls[0][3]
        self.assertEqual(payload["system"], [{"type": "text", "text": "You are a town resident."}])
        self.assertEqual(payload["messages"], [{"role": "user", "content": "GO or SKIP?"}])
        self.assertEqual(payload["thinking"], {"type": "disabled"})
        self.assertIn("output_config", payload)
        self.assertNotIn("response_format", payload)
        self.assertNotIn("temperature", payload)
        self.assertNotIn("use_batch_api", payload)
        self.assertEqual(self.calls[0][2]["x-api-key"], KEY)
        self.assertEqual(result.usage["execution_mode"], "synchronous_override")
        self.assertEqual(result.usage["input_tokens"], 100)
        self.assertAlmostEqual(result.usage["cost_usd"], .000076)

    async def test_approval_pricing_settings_batch_and_thinking_gates_no_key_or_network(self):
        cases = []
        for mutate in (lambda c: c.update(approved=False),
                       lambda c: c["routes"]["agent"].update(settings_verified=False),
                       lambda c: c["routes"]["agent"].update(pricing_verified=False),
                       lambda c: c["routes"]["agent"].pop("thinking_disabled_parameters")):
            config = manifest()
            mutate(config)
            cases.append((config, request()))
        cases.append((manifest(), request(kind="judge", settings={"max_tokens": 250, "use_batch_api": True})))
        for config, req in cases:
            with self.subTest(config=config), patch("truth_discount.providers.os.environ.get", side_effect=AssertionError("key read")):
                backend = self.backend(config)
                with self.assertRaises(ProviderError):
                    backend.validate_request(req)
                with self.assertRaises(ProviderError) as error:
                    await backend.generate(req)
                self.assertEqual(error.exception.receipt["provider_api_calls"], 0)
                self.assertEqual(error.exception.receipt["cost_status"], "not_submitted")
        self.assertEqual(self.calls, [])
        self.assertEqual(self.ledger.summary()["reservation_count"], 0)

    async def test_preflight_is_pure_and_manifest_detached(self):
        config = manifest()
        backend = self.backend(config)
        config["approved"] = False
        exposed = backend.manifest
        exposed["routes"]["agent"]["model_id"] = "other"
        with patch("truth_discount.providers.os.environ.get", side_effect=AssertionError("key read")):
            backend.validate_request(request())
        self.assertEqual(backend.manifest["routes"]["agent"]["model_id"], "model-v1")
        self.assertEqual(self.ledger.summary()["reservation_count"], 0)

    async def test_optional_nonreasoning_route_does_not_emit_fake_setting(self):
        config = manifest()
        config["routes"]["agent"].update(thinking_disabled_parameters={}, verified_nonreasoning=True)
        await self.backend(config).generate(request())
        self.assertNotIn("reasoning_effort", self.calls[0][3])

    async def test_missing_key_and_insufficient_cap_do_not_submit(self):
        backend = self.backend()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderError) as error:
                await backend.generate(request())
        self.assertEqual(error.exception.receipt["provider_api_calls"], 0)
        self.ledger.reserve(1)
        with self.assertRaises(ProviderError) as error:
            await backend.generate(request())
        self.assertEqual(error.exception.receipt["provider_api_calls"], 0)
        self.assertEqual(self.calls, [])

    async def test_unknown_usage_is_not_zero_and_blocks_next_request(self):
        body = response(usage={"prompt_tokens": 100, "completion_tokens": 3})
        backend = self.backend(body=body)
        with self.assertRaises(ProviderError) as error:
            await backend.generate(request())
        receipt = error.exception.receipt
        self.assertIsNone(receipt["cached_input_tokens"])
        self.assertIsNone(receipt["cost_usd"])
        self.assertEqual(receipt["input_tokens"], 100)
        self.assertEqual(receipt["cost_status"], "unknown")
        self.assertTrue(self.ledger.summary()["blocked"])
        with self.assertRaises(ProviderError):
            await backend.generate(request())
        self.assertEqual(len(self.calls), 1)

    async def test_transport_error_never_records_secret_or_retries(self):
        async def bad(*args):
            self.calls.append(args)
            raise ProviderError("HTTP body and Authorization: " + KEY)
        with self.assertRaises(ProviderError) as error:
            await self.backend(transport=bad).generate(request())
        self.assertNotIn(KEY, str(error.exception))
        self.assertNotIn(KEY, json.dumps(error.exception.receipt))
        self.assertNotIn(KEY, self.path.read_text())
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(self.ledger.summary()["blocked"])

    async def test_successful_echoed_key_id_is_redacted_before_persistence(self):
        result = await self.backend(body=response(id=KEY)).generate(request())
        self.assertEqual(result.usage["request_id"], "[REDACTED]")
        self.assertNotIn(KEY, self.path.read_text())

    async def test_echoed_key_in_generated_text_cannot_escape_to_history(self):
        body = response(choices=[{"message": {"content": "The server echoed " + KEY}}])
        with self.assertRaises(ProviderError) as error:
            await self.backend(body=body).generate(request())
        self.assertNotIn(KEY, str(error.exception) + json.dumps(error.exception.receipt) + self.path.read_text())
        self.assertEqual(error.exception.receipt["cost_status"], "calculated_from_usage")
        self.assertAlmostEqual(self.ledger.summary()["settled_usd"], .000076)
        self.assertFalse(self.ledger.summary()["blocked"])

    def test_credential_presence_checks_only_selected_verified_routes(self):
        config = manifest()
        config["routes"]["unused_audit"] = deepcopy(config["routes"]["agent"])
        config["routes"]["unused_audit"]["api_key_env"] = "UNUSED_AUDIT_KEY"
        backend = self.backend(config)
        with patch("truth_discount.providers.os.environ.get", return_value=KEY) as lookup:
            backend.validate_credentials(["agent", "agent"])
        lookup.assert_called_once_with("TRUTH_DISCOUNT_UNIT_TEST_KEY")
        for value in (None, "", "secret\rvalue", "secret\nvalue"):
            with patch("truth_discount.providers.os.environ.get", return_value=value):
                with self.assertRaises(ProviderError) as error:
                    backend.validate_credentials(["agent"])
                self.assertNotIn("secret", str(error.exception))
        self.assertEqual(self.calls, [])
        self.assertEqual(self.ledger.summary()["reservation_count"], 0)
        config["approved"] = False
        with patch("truth_discount.providers.os.environ.get", side_effect=AssertionError("key read")):
            with self.assertRaises(ProviderError):
                self.backend(config).validate_credentials(["agent"])

    async def test_http_error_body_and_headers_not_persisted(self):
        def bad(*args):
            return HTTPResponse(429, {"error": KEY}, {"Authorization": KEY})
        with self.assertRaises(ProviderError) as error:
            await self.backend(transport=bad).generate(request())
        self.assertEqual(error.exception.receipt["attempts"][0]["http_status"], 429)
        self.assertNotIn(KEY, str(error.exception) + self.path.read_text())
        self.assertTrue(self.ledger.summary()["blocked"])

    async def test_timeout_and_cancellation_hold_reservation(self):
        async def slow(*args):
            await asyncio.sleep(10)
        config = manifest()
        config["routes"]["agent"]["timeout_seconds"] = .01
        with self.assertRaises(ProviderError) as error:
            await self.backend(config, transport=slow).generate(request())
        self.assertEqual(error.exception.receipt["provider_api_calls"], 1)
        self.assertTrue(self.ledger.summary()["blocked"])
        # Use a fresh ledger to test cancellation independently of timeout hold.
        self.ledger.close()
        self.path = Path(self.temp.name) / "cancel.json"
        self.ledger = BudgetLedger(self.path, 1)
        self.addCleanup(self.ledger.close)
        entered = asyncio.Event()
        async def waiting(*args):
            entered.set()
            await asyncio.sleep(10)
        task = asyncio.create_task(self.backend(transport=waiting).generate(request()))
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError) as cancellation:
            await task
        self.assertEqual(cancellation.exception.receipt["attempts"][0]["status"], "cancelled")
        self.assertTrue(self.ledger.summary()["blocked"])

    async def test_malformed_content_still_records_known_bill(self):
        body = response(choices=[])
        with self.assertRaises(ProviderError) as error:
            await self.backend(body=body).generate(request())
        self.assertEqual(error.exception.receipt["cost_status"], "calculated_from_usage")
        self.assertAlmostEqual(self.ledger.summary()["settled_usd"], .000076)
        self.assertFalse(self.ledger.summary()["blocked"])

    async def test_wrong_response_model_does_not_use_requested_model_price(self):
        with self.assertRaises(ProviderError) as error:
            await self.backend(body=response(model="different-model")).generate(request())
        self.assertEqual(error.exception.receipt["actual_model"], "different-model")
        self.assertIsNone(error.exception.receipt["cost_usd"])
        self.assertTrue(self.ledger.summary()["blocked"])

    async def test_explicit_snapshot_alias_is_required(self):
        config = manifest()
        config["routes"]["agent"]["accepted_model_ids"] = ["model-v1-20261106"]
        result = await self.backend(config, response(model="model-v1-20261106")).generate(request())
        self.assertEqual(result.usage["actual_model"], "model-v1-20261106")

    async def test_openai_judge_thinking_is_explicitly_mapped_not_silently_dropped(self):
        config = manifest("OpenAI")
        config["routes"]["agent"].update(thinking_disabled_parameters={}, verified_nonreasoning=True,
                                        allow_synchronous_judge=True)
        settings = {"max_tokens": 250, "thinking": {"type": "disabled"}, "use_batch_api": True}
        await self.backend(config).generate(request(kind="judge", settings=settings))
        self.assertNotIn("thinking", self.calls[0][3])
        self.assertNotIn("reasoning_effort", self.calls[0][3])

    async def test_invalid_counts_and_unpriced_cache_writes_stop(self):
        for mutation in (lambda u: u.update(prompt_tokens=True),
                         lambda u: u["prompt_tokens_details"].update(cached_tokens=101),
                         lambda u: u["prompt_tokens_details"].update(cache_write_tokens=1)):
            self.ledger.close()
            self.path = Path(self.temp.name) / (str(len(list(Path(self.temp.name).iterdir()))) + ".json")
            self.ledger = BudgetLedger(self.path, 1)
            self.addCleanup(self.ledger.close)
            body = response()
            mutation(body["usage"])
            with self.assertRaises(ProviderError):
                await self.backend(body=body).generate(request())
            self.assertTrue(self.ledger.summary()["blocked"])

    def test_secret_endpoint_and_invalid_numeric_manifest_rejected(self):
        changes = [{"endpoint": "https://evil.example/chat"}, {"api_key": KEY},
                   {"input_usd_per_million": True}, {"output_usd_per_million": float("nan")},
                   {"timeout_seconds": 0}, {"max_input_tokens": False}, {"max_retries": 1},
                   {"thinking_disabled_parameters": {"unsupported": False}},
                   {"thinking_disabled_parameters": {"reasoning": {"enabled": 0}}}]
        for change in changes:
            config = manifest()
            config["routes"]["agent"].update(change)
            with self.subTest(change=change), self.assertRaises(ProviderError):
                self.backend(config)
        self.assertEqual(self.calls, [])

    def test_oversized_utf8_input_and_unknown_settings_stop_preflight(self):
        backend = self.backend()
        for req in (request(messages=[{"role": "user", "content": "é" * 8192}]),
                    request(settings={"max_tokens": 5, "unsupported": True})):
            with self.assertRaises(ProviderError):
                backend.validate_request(req)
        self.assertEqual(self.ledger.summary()["reservation_count"], 0)

    def test_mocked_evidence_requires_injected_transport_without_real_http_fallback(self):
        with patch("truth_discount.providers._http_transport", side_effect=AssertionError("no network")):
            with self.assertRaisesRegex(ProviderError, "explicit injected transport"):
                ProviderBackend(manifest(), self.ledger, evidence_kind="mocked_provider")
            with self.assertRaisesRegex(ProviderError, "must be callable"):
                ProviderBackend(manifest(), self.ledger, transport=False, evidence_kind="mocked_provider")
            class FalsyTransport:
                def __bool__(self):
                    return False
                def __call__(self, *args):
                    return response()
            supplied = FalsyTransport()
            backend = ProviderBackend(manifest(), self.ledger, transport=supplied,
                                      evidence_kind="mocked_provider")
            self.assertIs(backend.transport, supplied)
        self.assertEqual(self.ledger.summary()["reservation_count"], 0)


if __name__ == "__main__":
    unittest.main()
