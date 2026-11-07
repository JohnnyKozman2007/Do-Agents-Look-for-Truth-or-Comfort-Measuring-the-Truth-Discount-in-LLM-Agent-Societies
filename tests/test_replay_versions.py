"""Historical replay and truthful development receipts, without a network client."""

import copy
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from truth_discount.artifacts import (InvalidBundle, archived_attempt_paths, audit_town,
                                     save_town, summarize)
from truth_discount.config import build_manifest, load_config, render_contexts
from truth_discount.contracts import (GenerationRequest, GenerationResponse, capture,
                                     digest, usage_totals)
from truth_discount.fixtures import FixtureBackend
from truth_discount.runner import run_town


ROOT = Path(__file__).resolve().parents[1]
LEGACY = "truth-discount-offline-0.1"
CURRENT = "truth-discount-0.2"


class MockReceipts(FixtureBackend):
    """Manufactured receipt fixtures, explicitly marked as mocked evidence."""

    evidence_kind = "mocked_provider"

    def __init__(self, config, *, missing_usage=False):
        super().__init__("mixed")
        self.missing_usage = missing_usage
        models = config["models"]["agent_models"] + config["models"]["judge_models"]
        self.manifest = {"version": 1, "approved": True, "routes": {
            model["key"]: {"provider": "deepinfra", "model_id": model["model_id"],
                           "endpoint": "https://api.deepinfra.com/v1/openai/chat/completions",
                           "api_key_env": "UNUSED_TEST_KEY", "input_usd_per_million": 0.1,
                           "output_usd_per_million": 0.2, "cached_input_usd_per_million": 0.01,
                           "max_input_tokens": 10000, "timeout_seconds": 10,
                           "settings_verified": True, "pricing_verified": True,
                           "allow_synchronous_judge": True}
            for model in models}}

    def receipt(self, request):
        route = self.manifest["routes"][request.model_key]
        return {"actual_provider": route["provider"], "actual_model": route["model_id"],
                "request_id": f"mock-{request.scene}-{request.seat}-{request.kind}-{request.turn}",
                "provider_api_calls": 1, "input_tokens": None if self.missing_usage else 10,
                "output_tokens": None if self.missing_usage else 2,
                "cached_input_tokens": None if self.missing_usage else 0, "reasoning_tokens": None,
                "cost_usd": None if self.missing_usage else 0.0000014,
                "cost_status": "unknown" if self.missing_usage else "calculated_from_usage",
                "execution_mode": "synchronous_override" if request.settings.get("use_batch_api") else "synchronous",
                "attempts": [{"attempt_index": 1, "status": "completed"}],
                "pricing_sha256": digest({k: route[k] for k in
                                          ("input_usd_per_million", "output_usd_per_million",
                                           "cached_input_usd_per_million")})}

    async def generate(self, request):
        response = await super().generate(request)
        return GenerationResponse(response.text, self.receipt(request))


class FailFastReceipts(MockReceipts):
    """DeepInfra-style receipts: GO/SKIP checks were turned away once before being served."""

    def __init__(self, config, *, unreported_cache=False):
        super().__init__(config)
        self.unreported_cache = unreported_cache
        for route in self.manifest["routes"].values():
            route.update(provider="DeepInfra", fail_fast=True, max_retries=2)

    def receipt(self, request):
        receipt = super().receipt(request)
        receipt["cache_usage"] = "reported"
        if self.unreported_cache:
            receipt.update(cached_input_tokens=None, cache_usage="unreported")
        if request.scene == 2:
            receipt["provider_api_calls"] = 2
            receipt["attempts"] = [{"attempt_index": 0, "status": "rejected", "http_status": 429,
                                    "error_code": "engine_overloaded"},
                                   {"attempt_index": 1, "status": "completed"}]
        return receipt


class ReplayVersionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.runs = build_manifest(self.config)

    async def make(self, index=0, backend=None):
        town = await run_town(self.config, self.runs[index], backend or FixtureBackend(), self.root)
        return town, self.root / town["run_id"]

    def save(self, town, directory):
        save_town(directory, town, self.config)

    def legacy(self, town, *, generated=False):
        town = copy.deepcopy(town)
        town["schema_version"] = LEGACY
        town.pop("diagnostic_limits", None)
        town.pop("scene_5_mention_step_confirmed", None)
        if generated:
            town["source_mode"] = "offline_generated_exact_prompt"
            request = GenerationRequest(
                [{"role": "system", "content": render_contexts(self.config, town)[0]},
                 {"role": "user", "content": "Share your departure message now."}],
                self.config["hyperparameters"]["conversational_turns"], town["model_key"], "chat", 1, 0, 1)
            call = {"call_id": 1, "kind": "chat", "scene": 1, "seat_id": 0, "turn": 1,
                    "model_key": town["model_key"], "request": asdict(request),
                    "request_sha256": digest(asdict(request)), "status": "completed",
                    "response": town["scene_1_departure_broadcast_text"], "error": None,
                    "backend": "synthetic_fixture", "provider_api_calls": 0,
                    "actual_provider": None, "actual_model": None, "token_usage": None,
                    "cost_usd": None, "attempt_index": 1, "elapsed_seconds": 0,
                    "raw_response": capture(GenerationResponse(town["scene_1_departure_broadcast_text"]))}
            for old in town["calls"]:
                old["call_id"] += 1
            town["calls"].insert(0, call)
            town["token_usage"]["fixture_callback_invocations"] = len(town["calls"])
        return town

    async def test_legacy_generated_source_and_absent_new_field_replay(self):
        town, directory = await self.make()
        legacy = self.legacy(town, generated=True)
        self.save(legacy, directory)
        self.assertEqual(audit_town(directory), legacy)

    async def test_pr6_scripted_source_with_legacy_schema_replays(self):
        town, directory = await self.make()
        town["schema_version"] = LEGACY
        self.save(town, directory)
        self.assertEqual(audit_town(directory), town)

    async def test_legacy_generated_exact_match_is_recomputed_not_assumed(self):
        town, directory = await self.make()
        legacy = self.legacy(town, generated=True)
        legacy["source_exact_text_match"] = False
        self.save(legacy, directory)
        with self.assertRaisesRegex(InvalidBundle, "legacy broadcast"):
            audit_town(directory)

    def test_preserved_local_v01_bundles_replay_without_rewriting(self):
        paths = sorted((ROOT / "artifacts/implementation-review/mixed").glob("*/manifest.json"))
        if not paths:
            self.skipTest("optional original local fixture bundles are not committed")
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for m in paths
                  for p in m.parent.iterdir() if p.is_file()}
        for manifest in paths:
            self.assertEqual(audit_town(manifest.parent)["schema_version"], LEGACY)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    async def test_v02_requires_both_new_diagnostics(self):
        town, directory = await self.make()
        self.assertEqual(town["schema_version"], CURRENT)
        for field in ("scene_3_poster_evidence_passed", "scene_5_mention_step_confirmed", "diagnostic_limits"):
            with self.subTest(field=field):
                changed = copy.deepcopy(town)
                del changed[field]
                self.save(changed, directory)
                with self.assertRaises(InvalidBundle):
                    audit_town(directory)

    async def test_keyword_evidence_and_quotes_replay_from_dialogue(self):
        town, directory = await self.make()
        for field, value in (("evidence_passed", False), ("supporting_quotes", ["invented"]),
                             ("partner_checked", False)):
            with self.subTest(field=field):
                changed = copy.deepcopy(town)
                row = next(r for r in changed["scene_3_poster_evidence_passed"] if r["evidence_passed"])
                row[field] = value
                self.save(changed, directory)
                with self.assertRaisesRegex(InvalidBundle, "poster evidence diagnostic"):
                    audit_town(directory)

    async def test_confirmed_steps_reject_extra_seats_or_altered_trigger(self):
        town, directory = await self.make()
        for key, value in (("99", 1), ("1", 4)):
            with self.subTest(key=key):
                changed = copy.deepcopy(town)
                changed["scene_5_mention_step_confirmed"][key] = value
                self.save(changed, directory)
                with self.assertRaisesRegex(InvalidBundle, "confirmed mention step"):
                    audit_town(directory)

    async def test_funnel_trigger_rejects_unobserved_seats(self):
        town, directory = await self.make()
        town["scene_5_funnel_step_mentioned"]["99"] = 1
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "trigger coverage"):
            audit_town(directory)

    async def test_scripted_opener_cannot_be_rewritten_as_evidence(self):
        town, directory = await self.make()
        town["scene_3_catch_up_transcripts"][0]["lines"][0]["text"] = "The board names " + town["real_artist"]
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "scripted catch-up opener"):
            audit_town(directory)

    async def test_mocked_receipts_export_and_summarize_as_simulation(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        self.assertEqual(audit_town(directory), town)
        report = summarize(self.root)
        self.assertEqual(report["evidence_kind"], "mocked_provider")
        self.assertEqual(report["provider_api_calls"], 0)
        self.assertEqual(report["actual_provider_api_calls"], 0)
        self.assertEqual(report["simulated_provider_requests"], len(town["calls"]))
        self.assertEqual(report["fixture_callbacks"], 0)
        self.assertIsNone(report["cost_usd"])
        self.assertGreater(report["simulated_cost_usd"], 0)
        self.assertNotIn("paired_fixture_metrics", report)
        self.assertIn("mocked_provider", (directory / "listener_scores.csv").read_text())
        self.assertIn("Mocked provider", (directory / "transcript.md").read_text())
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertEqual((manifest["schema_version"], manifest["evidence_kind"]), (CURRENT, "mocked_provider"))

    async def test_missing_provider_usage_remains_unknown(self):
        town, directory = await self.make(backend=MockReceipts(self.config, missing_usage=True))
        self.assertEqual(audit_town(directory), town)
        self.assertIsNone(town["token_usage"]["input_tokens"])
        self.assertIsNone(summarize(self.root)["simulated_cost_usd"])
        town["token_usage"]["input_tokens"] = 0
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "aggregate mismatch"):
            audit_town(directory)

    async def archived_partial(self, *, unknown=False, fixture=False):
        class ReceiptFailure(ValueError):
            def __init__(self, receipt):
                super().__init__("synthetic uncertain charge")
                self.receipt = receipt

        class Partial(MockReceipts):
            async def generate(inner, request):
                response = await super().generate(request)
                if request.scene == 3 and request.seat == 1:
                    if unknown:
                        receipt = inner.receipt(request)
                        receipt.update(actual_model=None, request_id=None, input_tokens=None,
                                       output_tokens=None, cached_input_tokens=None, cost_usd=None,
                                       cost_status="unknown", attempts=[{"attempt_index": 0, "status": "failed"}])
                        raise ReceiptFailure(receipt)
                    return GenerationResponse("", response.usage)
                return response

        class PartialFixture(FixtureBackend):
            async def generate(inner, request):
                response = await super().generate(request)
                return GenerationResponse("") if request.scene == 3 and request.seat == 1 else response

        if unknown:
            with self.assertRaises(ReceiptFailure):
                await self.make(backend=Partial(self.config))
        else:
            await self.make(backend=PartialFixture() if fixture else Partial(self.config))
        directory = self.root / self.runs[0]["run_id"]
        town = audit_town(directory)
        self.assertNotEqual(town["run_status"], "completed")
        archived = self.root / "_incomplete" / "attempt-1" / directory.name
        archived.parent.mkdir(parents=True)
        directory.rename(archived)
        return town, archived

    async def test_archived_paid_partial_attempt_is_counted_without_reentering_pairs(self):
        partial, archived = await self.archived_partial()
        first, _ = await self.make(0, MockReceipts(self.config))
        second, _ = await self.make(1, MockReceipts(self.config))
        report = summarize(self.root)
        accounting = report["receipt_accounting"]
        active, archive, combined = (accounting[key] for key in
                                     ("active_towns", "archived_attempts", "all_attempts"))
        self.assertEqual((report["towns"], report["completed_towns"], report["pairs"]), (2, 2, 1))
        self.assertEqual(len(report["town_summaries"]), 2)
        self.assertFalse(accounting["archived_attempts_in_paired_metrics"])
        self.assertEqual(accounting["archived_attempt_paths"], [archived.relative_to(self.root).as_posix()])
        self.assertEqual((active["town_count"], archive["town_count"], combined["town_count"]), (2, 1, 3))
        active_cost = first["token_usage"]["cost_usd"] + second["token_usage"]["cost_usd"]
        self.assertAlmostEqual(report["simulated_cost_usd"], active_cost)
        self.assertAlmostEqual(archive["simulated_cost_usd"], partial["token_usage"]["cost_usd"])
        self.assertAlmostEqual(combined["simulated_cost_usd"], active_cost + partial["token_usage"]["cost_usd"])
        self.assertEqual(combined["input_tokens"], sum(t["token_usage"]["input_tokens"]
                                                     for t in (first, second, partial)))
        self.assertEqual(combined["simulated_provider_requests"], sum(len(t["calls"])
                                                                    for t in (first, second, partial)))
        self.assertEqual(combined["provider_api_calls"], 0)
        self.assertIsNone(combined["cost_usd"])
        self.assertFalse(combined["billing_verified"])

    async def test_archived_unknown_charge_keeps_all_attempt_cost_unknown(self):
        partial, _ = await self.archived_partial(unknown=True)
        active, _ = await self.make(0, MockReceipts(self.config))
        report = summarize(self.root)
        accounting = report["receipt_accounting"]
        self.assertAlmostEqual(report["simulated_cost_usd"], active["token_usage"]["cost_usd"])
        for key in ("archived_attempts", "all_attempts"):
            group = accounting[key]
            self.assertIsNone(group["simulated_cost_usd"])
            self.assertIsNone(group["input_tokens"])
            self.assertEqual(group["unknown_charge_calls"], 1)
            self.assertTrue(group["reconciliation_required"])
            self.assertFalse(group["ledger_reconciled"])
            self.assertGreater(group["recorded_known_simulated_cost_subtotal_usd"], 0)
        self.assertEqual(accounting["all_attempts"]["call_count"], len(partial["calls"]) + len(active["calls"]))
        self.assertEqual(accounting["active_towns"]["unknown_charge_calls"], 0)

    async def test_active_incomplete_receipts_are_separate_from_completed_active_towns(self):
        partial, archived = await self.archived_partial()
        archived.rename(self.root / archived.name)
        archived.parent.rmdir()
        archived.parent.parent.rmdir()
        completed, _ = await self.make(1, MockReceipts(self.config))
        report = summarize(self.root)
        accounting = report["receipt_accounting"]
        self.assertEqual(report["completed_towns"], 1)
        self.assertEqual(accounting["active_towns"]["town_count"], 2)
        self.assertEqual(accounting["completed_active_towns"]["town_count"], 1)
        self.assertAlmostEqual(accounting["completed_active_towns"]["simulated_cost_usd"],
                               completed["token_usage"]["cost_usd"])
        self.assertAlmostEqual(report["simulated_cost_usd"],
                               partial["token_usage"]["cost_usd"] + completed["token_usage"]["cost_usd"])

    async def test_broken_archived_attempt_cannot_disappear_from_cost_totals(self):
        for defect in ("missing_manifest", "tampered_receipt"):
            with self.subTest(defect=defect):
                self.root = Path(self.temp.name) / defect
                _, archived = await self.archived_partial()
                await self.make(0, MockReceipts(self.config))
                if defect == "missing_manifest":
                    (archived / "manifest.json").unlink()
                else:
                    with (archived / "trace.jsonl").open("a") as stream:
                        stream.write("{}\n")
                with self.assertRaisesRegex(InvalidBundle, "cannot account for archived attempt"):
                    summarize(self.root)

    async def test_archive_evidence_kind_cannot_be_hidden_by_active_mocked_towns(self):
        await self.archived_partial(fixture=True)
        await self.make(0, MockReceipts(self.config))
        with self.assertRaisesRegex(InvalidBundle, "cannot pool"):
            summarize(self.root)

    def test_archive_enumeration_rejects_shapes_that_could_hide_attempt_costs(self):
        for defect in ("root_file", "stray_file", "empty_attempt", "unknown_name", "zero_attempt",
                       "leading_zero_attempt", "town_file"):
            with self.subTest(defect=defect):
                root = Path(self.temp.name) / defect
                archive = root / "_incomplete"
                root.mkdir()
                if defect == "root_file":
                    archive.write_text("unaccounted receipts")
                else:
                    archive.mkdir()
                    if defect == "stray_file":
                        (archive / "trace.jsonl").write_text("{}\n")
                    elif defect == "empty_attempt":
                        (archive / "attempt-1").mkdir()
                    elif defect == "town_file":
                        (archive / "attempt-1").mkdir()
                        (archive / "attempt-1" / "town.json").write_text("{}")
                    else:
                        name = {"unknown_name": "old-attempt", "zero_attempt": "attempt-0",
                                "leading_zero_attempt": "attempt-01"}[defect]
                        (archive / name / "town-id").mkdir(parents=True)
                with self.assertRaises(InvalidBundle):
                    archived_attempt_paths(root)

    async def test_archived_fixture_attempts_claim_no_paid_or_simulated_requests(self):
        partial, _ = await self.archived_partial(fixture=True)
        completed, _ = await self.make(0)
        report = summarize(self.root)
        combined = report["receipt_accounting"]["all_attempts"]
        self.assertEqual((combined["provider_api_calls"], combined["simulated_provider_requests"]), (0, 0))
        self.assertIsNone(combined["cost_usd"])
        self.assertIsNone(combined["simulated_cost_usd"])
        self.assertEqual(combined["fixture_callback_invocations"], len(partial["calls"]) + len(completed["calls"]))

    async def test_unreported_cache_and_free_rejections_replay(self):
        town, directory = await self.make(backend=FailFastReceipts(self.config, unreported_cache=True))
        self.assertEqual(audit_town(directory), town)
        report = summarize(self.root)
        self.assertEqual(report["cache_usage_unreported_calls"], len(town["calls"]))
        self.assertEqual(report["simulated_provider_requests"], len(town["calls"]) + 6)
        self.assertAlmostEqual(report["simulated_cost_usd"], len(town["calls"]) * 0.0000014)

    async def test_cache_marker_must_match_the_priced_count(self):
        town, directory = await self.make(backend=FailFastReceipts(self.config, unreported_cache=True))
        call = town["calls"][0]
        call["token_usage"]["cache_usage"] = "reported"
        call["raw_response"] = capture(GenerationResponse(call["response"], call["token_usage"]))
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "cache usage marker"):
            audit_town(directory)

    async def test_free_attempt_needs_a_documented_fail_fast_rejection(self):
        for change in ("route", "code", "order"):
            with self.subTest(change=change):
                self.root = Path(self.temp.name) / change
                town, directory = await self.make(backend=FailFastReceipts(self.config))
                call = next(c for c in town["calls"] if c["scene"] == 2)
                if change == "route":
                    town["execution_manifest"]["routes"][call["model_key"]]["fail_fast"] = False
                    town["execution_manifest_sha256"] = digest(town["execution_manifest"])
                else:
                    attempts = call["token_usage"]["attempts"]
                    if change == "code":
                        attempts[0]["error_code"] = "rate_limited"
                    else:
                        attempts.reverse()
                    call["raw_response"] = capture(GenerationResponse(call["response"], call["token_usage"]))
                self.save(town, directory)
                with self.assertRaisesRegex(InvalidBundle, "pre-inference rejection"):
                    audit_town(directory)

    async def test_mixed_fixture_and_mocked_outputs_are_not_pooled(self):
        await self.make(0)
        await self.make(1, MockReceipts(self.config))
        with self.assertRaisesRegex(InvalidBundle, "cannot pool"):
            summarize(self.root)

    async def test_resealed_usage_cannot_disagree_with_raw_provider_response(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        town["calls"][0]["token_usage"]["input_tokens"] += 1
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "raw response usage"):
            audit_town(directory)

    async def test_charged_empty_response_usage_remains_bound_after_failure(self):
        class EmptyChat(MockReceipts):
            async def generate(self, request):
                response = await super().generate(request)
                if request.scene == 3 and request.kind == "chat":
                    return GenerationResponse("", response.usage)
                return response

        town, directory = await self.make(backend=EmptyChat(self.config))
        self.assertEqual(audit_town(directory)["run_status"], "malformed_response")
        failed = next(c for c in town["calls"] if c["status"] == "malformed_response")
        receipt = failed["token_usage"]
        self.assertEqual(receipt["provider_api_calls"], 1)
        receipt["input_tokens"] += 1
        route = town["execution_manifest"]["routes"][failed["model_key"]]
        cost = (Decimal(receipt["input_tokens"] - receipt["cached_input_tokens"])
                * Decimal(str(route["input_usd_per_million"]))
                + Decimal(receipt["cached_input_tokens"])
                * Decimal(str(route["cached_input_usd_per_million"]))
                + Decimal(receipt["output_tokens"])
                * Decimal(str(route["output_usd_per_million"]))) / Decimal(1_000_000)
        receipt["cost_usd"] = failed["cost_usd"] = float(cost)
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "raw response usage mismatch"):
            audit_town(directory)

    async def test_call_cost_projection_cannot_change_with_resealed_files(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        town["calls"][0]["cost_usd"] = 12
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "receipt projection"):
            audit_town(directory)

    async def test_pricing_hash_binds_the_saved_route_even_after_raw_resealing(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        call = town["calls"][0]
        call["token_usage"]["pricing_sha256"] = "0" * 64
        call["raw_response"] = capture(GenerationResponse(call["response"], call["token_usage"]))
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "pricing hash mismatch"):
            audit_town(directory)

    async def test_usage_derived_cost_cannot_be_invented_by_resealing(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        call = town["calls"][0]
        call["cost_usd"] = call["token_usage"]["cost_usd"] = 99
        call["raw_response"] = capture(GenerationResponse(call["response"], call["token_usage"]))
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "usage-derived cost"):
            audit_town(directory)

    async def test_submitted_provider_failure_preserves_unknowns_and_receipt(self):
        class ReceiptFailure(ValueError):
            def __init__(self, receipt):
                super().__init__("synthetic transport failure")
                self.receipt = receipt

        class Failing(MockReceipts):
            async def generate(self, request):
                if request.scene == 2 and request.seat == 1:
                    receipt = self.receipt(request)
                    receipt.update(actual_model=None, request_id=None, input_tokens=None,
                                   output_tokens=None, cached_input_tokens=None, cost_usd=None,
                                   cost_status="unknown", attempts=[{"attempt_index": 0, "status": "failed"}])
                    raise ReceiptFailure(receipt)
                return await super().generate(request)

        with self.assertRaises(ReceiptFailure):
            await self.make(backend=Failing(self.config))
        directory = self.root / self.runs[0]["run_id"]
        town = audit_town(directory)
        self.assertIsNone(town["token_usage"]["input_tokens"])
        self.assertIsNone(town["token_usage"]["cost_usd"])
        failed = next(c for c in town["calls"] if c["status"] != "completed")
        self.assertEqual(failed["provider_receipt"]["provider_api_calls"], 1)
        failed["provider_receipt"]["cost_usd"] = 0
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "failure receipt mismatch"):
            audit_town(directory)

    async def test_pre_submission_failure_does_not_invent_model_usage_or_price(self):
        class ReceiptFailure(ValueError):
            def __init__(self, receipt):
                super().__init__("synthetic preflight failure")
                self.receipt = receipt

        class Failing(MockReceipts):
            async def generate(self, request):
                if request.scene == 2 and request.seat == 1:
                    receipt = self.receipt(request)
                    receipt.update(actual_provider=None, actual_model=None, request_id=None,
                                   provider_api_calls=0, input_tokens=None, output_tokens=None,
                                   cached_input_tokens=None, cost_usd=None, cost_status="not_submitted",
                                   attempts=[], pricing_sha256=None)
                    raise ReceiptFailure(receipt)
                return await super().generate(request)

        with self.assertRaises(ReceiptFailure):
            await self.make(backend=Failing(self.config))
        town = audit_town(self.root / self.runs[0]["run_id"])
        self.assertEqual(town["token_usage"]["simulated_provider_requests"], 5)
        self.assertIsNone(town["token_usage"]["input_tokens"])

    async def test_execution_manifest_hash_and_secret_fields_are_checked(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        town["execution_manifest"]["approved"] = False
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "execution manifest hash"):
            audit_town(directory)
        town["execution_manifest"]["api_key"] = "test-secret-not-a-real-key"
        town["execution_manifest_sha256"] = digest(town["execution_manifest"])
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "secret field"):
            audit_town(directory)

    async def test_development_marker_cannot_bypass_approval(self):
        town, directory = await self.make(backend=MockReceipts(self.config))
        town["evidence_kind"] = "development_pilot"
        town["execution_manifest"]["approved"] = False
        town["execution_manifest_sha256"] = digest(town["execution_manifest"])
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "approved verified"):
            audit_town(directory)

    async def test_raw_response_hash_and_source_hash_shape_are_checked(self):
        town, directory = await self.make()
        town["calls"][0]["raw_response"]["sha256"] = "0" * 64
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "raw response hash"):
            audit_town(directory)
        manifest = json.loads((directory / "manifest.json").read_text())
        manifest["source_files_sha256"]["runner.py"] = "not-a-hash"
        (directory / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(InvalidBundle, "source hashes"):
            audit_town(directory)

    async def test_unknown_schema_is_not_treated_as_legacy(self):
        town, directory = await self.make()
        town["schema_version"] = "truth-discount-99"
        self.save(town, directory)
        with self.assertRaisesRegex(InvalidBundle, "unsupported schema"):
            audit_town(directory)


if __name__ == "__main__":
    unittest.main()
