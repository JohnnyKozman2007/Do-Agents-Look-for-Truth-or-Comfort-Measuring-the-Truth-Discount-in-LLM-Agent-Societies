"""Reconciliation consumes only audited fake-transport evidence, never a live key."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from truth_discount.artifacts import audit_town, save_town
from truth_discount.budget import BudgetLedger
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import GenerationResponse, canonical_bytes, capture, digest, usage_totals
from truth_discount.execution import _atomic_json, plan
from truth_discount.providers import ProviderBackend, ProviderError
from truth_discount.runner import run_town

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reconcile_unknowns_under_test", ROOT / "scripts/reconcile_unknowns.py")
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


class ReconcileUnknownsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output, self.journal = self.root / "output", self.root / "ledger.jsonl"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.runs = build_manifest(self.config)[:2]
        self.providers = {"version": 1, "approved": True, "routes": {}}
        for model in self.config["models"]["agent_models"] + self.config["models"]["judge_models"][:1]:
            native = model["provider"] == "Anthropic"
            self.providers["routes"][model["key"]] = {
                "provider": model["provider"], "model_id": model["model_id"],
                "endpoint": "https://api.anthropic.com/v1/messages" if native else "https://api.deepinfra.com/v1/openai/chat/completions",
                "api_key_env": "FAKE_RECONCILIATION_TEST_KEY", "settings_verified": True,
                "pricing_verified": True, "input_usd_per_million": .1, "output_usd_per_million": .5,
                "cached_input_usd_per_million": .01, "max_input_tokens": 32768, "timeout_seconds": 1,
                "thinking_disabled_parameters": {"thinking": {"type": "disabled"}} if native else {"reasoning_effort": "none"},
                "allow_synchronous_judge": native}
        def transport(method, url, headers, body, timeout):
            return {"id": "fake-known-response", "model": body["model"],
                    "choices": [{"message": {"content": "SKIP"}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 1,
                              "prompt_tokens_details": {"cached_tokens": 0}}}
        with BudgetLedger(self.journal, "1") as ledger:
            settle = ledger.settle
            self.target = None
            def hold_first(identifier, amount, receipt=None):
                if self.target is None:
                    self.target, self.known_amount = identifier, amount
                    return settle(identifier, None, {"cost_status": "unknown"})
                return settle(identifier, amount, receipt)
            backend = ProviderBackend(self.providers, ledger, transport, evidence_kind="mocked_provider")
            with patch.dict(os.environ, {"FAKE_RECONCILIATION_TEST_KEY": "UNIT_TEST_NO_REAL_CREDENTIAL"}), \
                 patch.object(ledger, "settle", side_effect=hold_first):
                with self.assertRaises(ProviderError):
                    await run_town(self.config, self.runs[0], backend, self.output)
            saved = plan(self.config, self.providers, self.runs)
            saved.update(execution_plan_version=2, evidence_kind="mocked_provider",
                         ledger_binding={key: ledger.checkpoint()[key] for key in ("ledger_id", "limit_usd")})
            _atomic_json(self.output / "execution_plan.json", saved)
            _atomic_json(self.output / "budget_checkpoint.json", {
                "execution_plan_sha256": digest(saved), "ledger_checkpoint": ledger.checkpoint()})
        self.town_path = self.output / self.runs[0]["run_id"]
        self.assertEqual(audit_town(self.town_path)["evidence_kind"], "mocked_provider")
        Path(str(self.journal) + ".lock").unlink()

    def preview(self, *, apply=False):
        return recovery.reconcile_known(self.journal, "1", [self.output], apply=apply)

    def refresh_anchor(self):
        saved = json.loads((self.output / "execution_plan.json").read_text())
        with BudgetLedger(self.journal, "1") as ledger:
            _atomic_json(self.output / "budget_checkpoint.json", {
                "execution_plan_sha256": digest(saved), "ledger_checkpoint": ledger.checkpoint()})
        Path(str(self.journal) + ".lock").unlink()

    def test_preview_is_read_only_and_known_charge_is_not_invoice_proof(self):
        before = self.journal.read_bytes()
        source = recovery._snapshot(self.output)
        result = self.preview()
        self.assertEqual(result["status"], "ready_for_explicit_apply")
        self.assertEqual(result["applied_count"], 0)
        self.assertEqual(result["eligible"][0]["reservation_id"], self.target)
        self.assertFalse(result["billing_verified"])
        self.assertEqual(result["eligible"][0]["evidence_kind"], "mocked_provider")
        self.assertEqual(before, self.journal.read_bytes())
        self.assertEqual(source, recovery._snapshot(self.output))
        self.assertFalse(Path(str(self.journal) + ".lock").exists())

    def test_apply_resolves_only_unique_priced_reservation_and_preserves_history(self):
        before = self.journal.read_bytes()
        old_anchor = json.loads((self.output / "budget_checkpoint.json").read_text())
        result = self.preview(apply=True)
        self.assertEqual((result["status"], result["applied_count"]), ("applied", 1))
        self.assertEqual(result["budget"]["unknown_count"], 0)
        self.assertTrue(self.journal.read_bytes().startswith(before))
        appended = [json.loads(line) for line in self.journal.read_bytes()[len(before):].splitlines()]
        self.assertEqual(len(appended), 1)
        self.assertEqual((appended[0]["type"], appended[0]["id"]), ("reconcile", self.target))
        self.assertEqual(float(appended[0]["actual_usd"]), float(self.known_amount))
        self.assertIn("not invoice proof", appended[0]["note"])
        with BudgetLedger(self.journal, "1") as ledger:
            ledger.verify_checkpoint(old_anchor["ledger_checkpoint"])
            anchor = json.loads((self.output / "budget_checkpoint.json").read_text())
            ledger.verify_checkpoint(anchor["ledger_checkpoint"])
        self.assertEqual(self.preview()["status"], "no_unknown_charges")

    def test_archived_attempt_is_audited_and_duplicate_matches_are_refused(self):
        archive = self.output / "_incomplete" / "attempt-1" / self.town_path.name
        archive.parent.mkdir(parents=True)
        shutil.copytree(self.town_path, archive)
        before = self.journal.read_bytes()
        self.assertEqual(self.preview()["status"], "unresolved")
        with self.assertRaisesRegex(ValueError, "remain held"):
            self.preview(apply=True)
        self.assertEqual(before, self.journal.read_bytes())
        shutil.rmtree(self.town_path)
        self.assertEqual(self.preview()["status"], "ready_for_explicit_apply")

    def test_tampered_unaudited_town_does_not_release_money(self):
        with (self.town_path / "town.json").open("a") as stream:
            stream.write(" ")
        before = self.journal.read_bytes()
        with self.assertRaises(ValueError):
            self.preview(apply=True)
        self.assertEqual(before, self.journal.read_bytes())
        self.assertFalse(Path(str(self.journal) + ".lock").exists())

    def test_request_pricing_and_evidence_metadata_must_match_native_request(self):
        original = self.journal.read_bytes()
        for field, value in (("request_sha256", "0" * 64), ("pricing_sha256", "0" * 64),
                             ("evidence_kind", "development_pilot")):
            with self.subTest(field=field):
                events = [json.loads(line) for line in original.splitlines()]
                event = next(row for row in events if row.get("type") == "reserve" and row["id"] == self.target)
                event["metadata"][field] = value
                self.journal.write_bytes(b"".join(canonical_bytes(row) + b"\n" for row in events))
                self.refresh_anchor()
                before = self.journal.read_bytes()
                self.assertEqual(self.preview()["status"], "unresolved")
                with self.assertRaises(ValueError):
                    self.preview(apply=True)
                self.assertEqual(before, self.journal.read_bytes())

    def test_unpriced_receipt_stays_held_without_reservation_fallback(self):
        town = audit_town(self.town_path)
        call = next(call for call in town["calls"] if any(a.get("reservation_id") == self.target
                    for a in (call.get("token_usage") or {}).get("attempts", [])))
        call["token_usage"].update(cost_usd=None, cost_status="unknown")
        call["cost_usd"] = None
        call["raw_response"] = capture(GenerationResponse(call["response"], call["token_usage"]))
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        save_town(self.town_path, town, self.config)
        before = self.journal.read_bytes()
        self.assertEqual(self.preview()["status"], "unresolved")
        with self.assertRaisesRegex(ValueError, "remain held"):
            self.preview(apply=True)
        self.assertEqual(before, self.journal.read_bytes())

    def test_wrong_ledger_or_checkpoint_and_torn_preview_are_rejected_without_writes(self):
        with BudgetLedger(self.root / "wrong-ledger.jsonl", "1"):
            pass
        before = self.journal.read_bytes()
        with self.assertRaises(ValueError):
            recovery.reconcile_known(self.root / "wrong-ledger.jsonl", "1", [self.output])
        anchor_path = self.output / "budget_checkpoint.json"
        anchor = json.loads(anchor_path.read_text())
        anchor["ledger_checkpoint"]["history_sha256"] = "0" * 64
        anchor_path.write_bytes(canonical_bytes(anchor))
        with self.assertRaises(ValueError):
            self.preview()
        self.assertEqual(before, self.journal.read_bytes())
        self.journal.write_bytes(before[:-1])
        with self.assertRaisesRegex(ValueError, "torn"):
            self.preview()
        self.assertEqual(self.journal.read_bytes(), before[:-1])
        self.assertFalse(Path(str(self.journal) + ".lock").exists())

    def test_missing_journal_is_not_created_and_main_is_import_safe(self):
        absent = self.root / "absent" / "journal.jsonl"
        with self.assertRaises(ValueError):
            recovery.reconcile_known(absent, "1", [self.output])
        self.assertFalse(absent.parent.exists())
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = recovery.main([str(self.journal), "1", str(self.output)])
        self.assertEqual(code, 0, err.getvalue())
        self.assertEqual(json.loads(out.getvalue())["provider_api_calls"], 0)

    def test_pending_crash_preview_recovers_only_temp_copy_then_explicit_apply_preserves_hold_history(self):
        events = [json.loads(line) for line in self.journal.read_bytes().splitlines()]
        events = [row for row in events if not (row.get("type") == "settle" and row["id"] == self.target)]
        raw = b"".join(canonical_bytes(row) + b"\n" for row in events)
        self.journal.write_bytes(raw)
        saved = json.loads((self.output / "execution_plan.json").read_text())
        _atomic_json(self.output / "budget_checkpoint.json", {
            "execution_plan_sha256": digest(saved),
            "ledger_checkpoint": {**saved["ledger_binding"], "event_count": len(events),
                                  "history_sha256": hashlib.sha256(raw).hexdigest()}})
        self.assertEqual(self.preview()["status"], "ready_for_explicit_apply")
        self.assertEqual(self.journal.read_bytes(), raw)
        self.assertFalse(Path(str(self.journal) + ".lock").exists())
        result = self.preview(apply=True)
        self.assertEqual(result["budget"]["unknown_count"], 0)
        added = [json.loads(line) for line in self.journal.read_bytes()[len(raw):].splitlines()]
        self.assertEqual([row["type"] for row in added], ["interrupt", "reconcile"])

    def test_aggregate_multiattempt_receipt_is_not_applied_to_a_single_reservation(self):
        town = audit_town(self.town_path)
        call = next(call for call in town["calls"] if any(a.get("reservation_id") == self.target
                    for a in (call.get("token_usage") or {}).get("attempts", [])))
        receipt = call["token_usage"]
        receipt["attempts"].insert(0, {"attempt_index": 1, "status": "failed", "reservation_id": "f" * 32})
        receipt["provider_api_calls"] = call["provider_api_calls"] = 2
        call["raw_response"] = capture(GenerationResponse(call["response"], receipt))
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        save_town(self.town_path, town, self.config)
        before = self.journal.read_bytes()
        result = self.preview()
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("one native attempt", result["unresolved"][0]["reason"])
        with self.assertRaises(ValueError):
            self.preview(apply=True)
        self.assertEqual(before, self.journal.read_bytes())

    def test_changed_source_is_rejected_before_original_journal_is_opened(self):
        original = recovery._bound_evidence
        def changed(*args):
            result = original(*args)
            (self.output / "concurrent-change.txt").write_text("synthetic concurrent source change")
            return result
        before = self.journal.read_bytes()
        with patch.object(recovery, "_bound_evidence", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "changed"):
                self.preview(apply=True)
        self.assertEqual(self.journal.read_bytes(), before)
        self.assertFalse(Path(str(self.journal) + ".lock").exists())

    def test_resealed_priced_receipt_above_native_token_bound_stays_held(self):
        original = audit_town(self.town_path)
        for field, value in (("input_tokens", 32769), ("output_tokens", 6)):
            with self.subTest(field=field):
                town = json.loads(json.dumps(original))
                call = next(call for call in town["calls"] if any(a.get("reservation_id") == self.target
                            for a in (call.get("token_usage") or {}).get("attempts", [])))
                receipt = call["token_usage"]
                receipt[field] = value
                receipt["cost_usd"] = call["cost_usd"] = (receipt["input_tokens"] * .1 + receipt["output_tokens"] * .5) / 1e6
                call["raw_response"] = capture(GenerationResponse(call["response"], receipt))
                town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
                save_town(self.town_path, town, self.config)
                before = self.journal.read_bytes()
                result = self.preview()
                self.assertEqual(result["status"], "unresolved")
                self.assertIn("token usage exceeds", result["unresolved"][0]["reason"])
                with self.assertRaises(ValueError):
                    self.preview(apply=True)
                self.assertEqual(self.journal.read_bytes(), before)

    def test_observed_response_fields_cannot_be_replaced_by_conflicting_candidate(self):
        raw = self.journal.read_bytes()
        for field, value in (("actual_provider", "OpenAI"), ("actual_model", "other-model"),
                             ("request_id", "different-request"), ("pricing_sha256", "0" * 64),
                             ("input_tokens", 999), ("output_tokens", 2), ("cached_input_tokens", 1),
                             ("reasoning_tokens", 1), ("cost_usd", .9)):
            with self.subTest(field=field):
                events = [json.loads(line) for line in raw.splitlines()]
                event = next(row for row in events if row.get("type") == "settle" and row["id"] == self.target)
                event["receipt"][field] = value
                self.journal.write_bytes(b"".join(canonical_bytes(row) + b"\n" for row in events))
                self.refresh_anchor()
                before = self.journal.read_bytes()
                result = self.preview()
                self.assertEqual(result["status"], "unresolved")
                self.assertIn("contradicts", result["unresolved"][0]["reason"])
                with self.assertRaises(ValueError):
                    self.preview(apply=True)
                self.assertEqual(self.journal.read_bytes(), before)

    def test_matching_observations_and_unknown_operational_status_do_not_prevent_known_recovery(self):
        town = audit_town(self.town_path)
        receipt = next(call["token_usage"] for call in town["calls"] if any(a.get("reservation_id") == self.target
                       for a in (call.get("token_usage") or {}).get("attempts", [])))
        events = [json.loads(line) for line in self.journal.read_bytes().splitlines()]
        event = next(row for row in events if row.get("type") == "settle" and row["id"] == self.target)
        event["receipt"].update({field: receipt[field] for field in
                                ("actual_provider", "actual_model", "request_id", "input_tokens", "output_tokens")})
        event["receipt"].update(cost_status="unknown", error_code="interrupted_request", cost_usd=None)
        self.journal.write_bytes(b"".join(canonical_bytes(row) + b"\n" for row in events))
        self.refresh_anchor()
        self.assertEqual(self.preview()["status"], "ready_for_explicit_apply")


class SimulationReconcileTests(unittest.TestCase):
    """A sealed simulation-only collection is audited against its own saved plan."""

    def setUp(self):
        import asyncio
        import sys
        sys.path.insert(0, str(ROOT / "tests"))
        from test_live_cli import MockHTTP, approved_test_manifest
        from truth_discount.execution import select_runs
        from truth_discount.simulation_execution import allocate_runs, collect_simulations
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.output, self.journal = root / "shard", root / "shard.jsonl"
        config = load_config(ROOT / "configs/pilot_config.json")
        providers = approved_test_manifest(config)
        agents = {model["key"] for model in config["models"]["agent_models"]}
        providers["routes"] = {k: v for k, v in providers["routes"].items() if k in agents}
        selection = select_runs(config, [config["models"]["agent_models"][0]["key"]])[:2]
        runs, allocation = allocate_runs(config, selection)
        with BudgetLedger(self.journal, "1") as ledger:
            settle = ledger.settle
            self.target = None
            def hold_first(identifier, amount, receipt=None):
                # The provider priced this call, but the ledger only learned "unknown".
                if self.target is None:
                    self.target, self.known_amount = identifier, amount
                    return settle(identifier, None, {"cost_status": "unknown"})
                return settle(identifier, amount, receipt)
            backend = ProviderBackend(providers, ledger, transport=MockHTTP(), evidence_kind="mocked_provider")
            with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "UNIT_TEST_NO_REAL_CREDENTIAL"}), \
                 patch("socket.create_connection", side_effect=AssertionError("network forbidden")), \
                 patch.object(ledger, "settle", side_effect=hold_first):
                with self.assertRaises(Exception):
                    asyncio.run(collect_simulations(config, providers, runs, self.output, backend,
                        allocation=allocation, execution_authorized=True, spending_authorized=True))
        lock = Path(str(self.journal) + ".lock")
        if lock.exists():
            lock.unlink()

    def test_priced_simulation_receipt_is_recovered_and_collection_stays_resumable(self):
        from truth_discount.simulation_execution import _read_plan
        source = recovery._snapshot(self.output)
        preview = recovery.reconcile_known(self.journal, "1", [self.output])
        self.assertEqual(preview["status"], "ready_for_explicit_apply")
        self.assertEqual(preview["eligible"][0]["reservation_id"], self.target)
        self.assertEqual(source, recovery._snapshot(self.output))
        applied = recovery.reconcile_known(self.journal, "1", [self.output], apply=True)
        self.assertEqual((applied["status"], applied["applied_count"]), ("applied", 1))
        self.assertEqual(applied["budget"]["unknown_count"], 0)
        self.assertEqual(recovery.reconcile_known(self.journal, "1", [self.output])["status"], "no_unknown_charges")
        # The rewritten anchor still binds the saved plan, so `simulate --resume` can continue.
        saved = _read_plan(self.output)
        with BudgetLedger(self.journal, "1") as ledger:
            ledger.verify_checkpoint(json.loads((self.output / "budget_checkpoint.json").read_text())["ledger_checkpoint"])
        self.assertEqual(saved["execution_mode"], "simulation_only")


if __name__ == "__main__":
    unittest.main()
