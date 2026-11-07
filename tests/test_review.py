"""Saved-collection handoff uses synthetic/injected responses, never a provider."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_live_cli import MockHTTP, approved_test_manifest
from truth_discount.budget import BudgetLedger
from truth_discount.cli import main
from truth_discount.config import build_manifest, load_config
from truth_discount.execution import collect, plan
from truth_discount.fixtures import FixtureBackend
from truth_discount.providers import ProviderBackend
from truth_discount.review import review_collection
from truth_discount.runner import run_town

ROOT = Path(__file__).resolve().parents[1]


def hashes(root):
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.config = load_config(ROOT / "configs/pilot_config.json")
        cls.providers = approved_test_manifest(cls.config)
        # Two pairs for one model/cell. This complete selection is not 624 towns.
        cls.runs = [r for r in build_manifest(cls.config)
                    if r["cell_id"] == 1 and r["seed_id"] < 2
                    and r["model_key"] == cls.config["models"]["agent_models"][0]["key"]]
        cls.source = cls.base / "source"
        cls.journal = cls.base / "journal.jsonl"
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("no network")), \
             BudgetLedger(cls.journal, "1") as ledger:
            backend = ProviderBackend(cls.providers, ledger, transport=MockHTTP(), evidence_kind="mocked_provider")
            asyncio.run(collect(cls.config, cls.providers, cls.runs, cls.source, backend))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.local = tempfile.TemporaryDirectory()
        self.addCleanup(self.local.cleanup)
        self.root = Path(self.local.name)
        self.source = self.root / "source"
        shutil.copytree(type(self).source, self.source)
        self.journal = self.root / "provided-copy.jsonl"
        shutil.copyfile(type(self).journal, self.journal)
        self.destination = self.root / "review"

    def test_complete_selection_does_not_claim_the_whole_matrix(self):
        before, journal = hashes(self.source), self.journal.read_bytes()
        with patch.dict(os.environ, {}, clear=True), \
             patch("socket.create_connection", side_effect=AssertionError("no network")):
            result = review_collection(self.source, self.destination, self.journal)
        coverage = result["coverage"]
        self.assertTrue(coverage["selected_complete"])
        self.assertEqual(coverage["selected_expected_towns"], 4)
        self.assertEqual(coverage["configured_run_count"], 624)
        self.assertFalse(coverage["full_matrix_coverage"]["complete"])
        self.assertEqual(len(coverage["full_matrix_coverage"]["missing_or_incomplete_run_ids"]), 620)
        self.assertTrue(result["ledger"]["checkpoint_verified"])
        self.assertFalse(result["ledger"]["billing_verified"])
        self.assertEqual(result["review_provider_api_calls"], 0)
        self.assertEqual(result["evidence_kind"], "mocked_provider")
        self.assertIsNone(result["receipt_accounting"]["all_attempts"]["cost_usd"])
        self.assertGreater(result["receipt_accounting"]["all_attempts"]["simulated_cost_usd"], 0)
        self.assertEqual(hashes(self.source), before)
        self.assertEqual(self.journal.read_bytes(), journal)
        self.assertFalse(Path(str(self.journal) + ".lock").exists())
        self.assertEqual(json.loads((self.destination / "review.json").read_text()), result)

    def test_cli_outputs_compact_saved_data_review_without_access_or_spending(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {}, clear=True), \
             patch("socket.create_connection", side_effect=AssertionError("no network")), \
             patch.object(ProviderBackend, "validate_credentials", side_effect=AssertionError("no credentials")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(["review-collection", str(self.source), "--out", str(self.destination),
                           "--ledger-copy", str(self.journal)])
        self.assertEqual(status, 0, stderr.getvalue())
        compact = json.loads(stdout.getvalue())
        self.assertTrue(compact["selected_complete"])
        self.assertFalse(compact["full_matrix_complete"])
        self.assertEqual(compact["missing_towns"], 0)
        self.assertEqual(compact["ledger_status"], "verified_local_journal")
        self.assertTrue(Path(compact["report"]).is_file())
        self.assertNotIn("source_files_sha256", compact)
        self.assertLess(len(stdout.getvalue()), 1000)

    def test_missing_both_twins_is_visible_without_inventing_an_outcome(self):
        absent = self.runs[:2]
        for run in absent:
            shutil.rmtree(self.source / run["run_id"])
        result = review_collection(self.source, self.destination)
        self.assertFalse(result["coverage"]["selected_complete"])
        self.assertEqual(result["coverage"]["missing_run_ids"], sorted(r["run_id"] for r in absent))
        self.assertEqual(result["coverage"]["missing_entire_pairs"],
                         [{"model_key": absent[0]["model_key"], "pair_id": absent[0]["pair_id"]}])
        self.assertEqual(result["ledger"]["status"], "not_provided")
        self.assertFalse(result["study_results_generated"])

    def test_tampered_plan_is_rejected_before_creating_output(self):
        path = self.source / "execution_plan.json"
        saved = json.loads(path.read_text())
        saved["runs"][0]["real_artist"] = "Unagreed artist"
        path.write_text(json.dumps(saved))
        with self.assertRaisesRegex(ValueError, "selection differs"):
            review_collection(self.source, self.destination)
        self.assertFalse(self.destination.exists())

    def test_plan_provenance_and_duplicate_ids_cannot_be_resealed(self):
        path = self.source / "execution_plan.json"
        original = path.read_bytes()
        for changed in ("provider_manifest_sha256", "planned_towns", "duplicate"):
            with self.subTest(changed=changed):
                saved = json.loads(original)
                if changed == "duplicate":
                    saved["runs"].append(saved["runs"][0])
                else:
                    saved[changed] = "not-the-original"
                path.write_text(json.dumps(saved))
                with self.assertRaisesRegex(ValueError, "(duplicate|differs)"):
                    review_collection(self.source, self.destination)
                self.assertFalse(self.destination.exists())
        path.write_bytes(original)

    def test_resealed_singleton_selection_and_nonpositive_caps_are_rejected(self):
        path = self.source / "execution_plan.json"
        original = json.loads(path.read_text())
        singleton = plan(self.config, self.providers, self.runs[:1])
        singleton.update(execution_plan_version=2, evidence_kind="mocked_provider",
                         ledger_binding=original["ledger_binding"])
        path.write_text(json.dumps(singleton))
        with self.assertRaisesRegex(ValueError, "preserve matched twins"):
            review_collection(self.source, self.destination)
        for cap in (0, -1, "NaN", True):
            with self.subTest(cap=cap):
                changed = json.loads(json.dumps(original))
                changed["ledger_binding"]["limit_usd"] = cap
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, "(positive|finite)"):
                    review_collection(self.source, self.destination)
        self.assertFalse(self.destination.exists())

    def test_budget_anchor_remains_bound_without_a_supplied_journal(self):
        path = self.source / "budget_checkpoint.json"
        anchor = json.loads(path.read_text())
        anchor["execution_plan_sha256"] = "0" * 64
        path.write_text(json.dumps(anchor))
        with self.assertRaisesRegex(ValueError, "checkpoint differs"):
            review_collection(self.source, self.destination)
        self.assertFalse(self.destination.exists())

    def test_legacy_fixture_without_plan_never_infers_collection_completeness(self):
        source = self.root / "legacy"
        asyncio.run(run_town(self.config, self.runs[0], FixtureBackend(), source))
        result = review_collection(source, self.destination)
        self.assertEqual(result["coverage"]["plan_status"], "unavailable")
        self.assertIsNone(result["coverage"]["selected_expected_towns"])
        self.assertIsNone(result["coverage"]["configured_run_count"])
        self.assertIsNone(result["coverage"]["full_matrix_coverage"]["complete"])
        self.assertIn("selected_plan_incomplete_or_unavailable", result["issues"])

    def test_no_overwrite_inside_input_and_source_instability(self):
        before = hashes(self.source)
        with self.assertRaisesRegex(ValueError, "outside"):
            review_collection(self.source, self.source / "report")
        self.destination.mkdir()
        with self.assertRaises(FileExistsError):
            review_collection(self.source, self.destination)
        self.destination.rmdir()
        from truth_discount.artifacts import summarize as real_summarize
        def changed(root):
            result = real_summarize(root)
            (root / "changed-during-review.txt").write_text("new data")
            return result
        with patch("truth_discount.review.summarize", side_effect=changed), \
             self.assertRaisesRegex(ValueError, "changed during review"):
            review_collection(self.source, self.destination)
        self.assertFalse(self.destination.exists())
        (self.source / "changed-during-review.txt").unlink()
        self.assertEqual(hashes(self.source), before)

    def test_ledger_missing_torn_pending_and_unstable_evidence_is_not_healed(self):
        # Pending reservations are converted to unknown only in the temporary copy.
        with BudgetLedger(self.journal, "1") as ledger:
            ledger.reserve("0.01", {"evidence_kind": "mocked_provider"})
        original = self.journal.read_bytes()
        result = review_collection(self.source, self.destination, self.journal)
        self.assertTrue(result["ledger"]["temporary_recovery_events_added"])
        self.assertTrue(result["ledger"]["budget"]["blocked"])
        self.assertEqual(result["ledger"]["budget"]["unknown_count"], 1)
        self.assertEqual(result["ledger"]["budget"]["reserved_usd"], 0.01)
        self.assertEqual(self.journal.read_bytes(), original)
        torn = self.root / "torn.jsonl"
        torn.write_bytes(original + b'{"type":"reserve"')
        torn_before = torn.read_bytes()
        result = review_collection(self.source, self.root / "torn-review", torn)
        self.assertEqual(result["ledger"]["status"], "incomplete_or_torn_journal")
        self.assertIsNone(result["ledger"]["budget"])
        self.assertFalse(result["ledger"]["checkpoint_verified"])
        self.assertEqual(torn.read_bytes(), torn_before)
        (self.source / "budget_checkpoint.json").unlink()
        result = review_collection(self.source, self.root / "missing-checkpoint", self.journal)
        self.assertEqual(result["ledger"]["status"], "missing_checkpoint")

    def test_wrong_ledger_identity_or_checkpoint_is_rejected(self):
        wrong = self.root / "wrong.jsonl"
        with BudgetLedger(wrong, "1"):
            pass
        with self.assertRaisesRegex(ValueError, "identity differs"):
            review_collection(self.source, self.destination, wrong)
        checkpoint = self.source / "budget_checkpoint.json"
        data = json.loads(checkpoint.read_text())
        data["ledger_checkpoint"]["history_sha256"] = "0" * 64
        checkpoint.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "history differs"):
            review_collection(self.source, self.destination, self.journal)
        self.assertFalse(self.destination.exists())

    def test_supplied_journal_instability_fails_before_output(self):
        from truth_discount.review import _ledger_review as real_review
        def changing(root, saved, raw):
            result = real_review(root, saved, raw)
            with self.journal.open("ab") as stream:
                stream.write(b'{"unacknowledged":')
            return result
        with patch("truth_discount.review._ledger_review", side_effect=changing), \
             self.assertRaisesRegex(ValueError, "journal changed"):
            review_collection(self.source, self.destination, self.journal)
        self.assertFalse(self.destination.exists())

    def test_unknown_archived_charge_and_raw_overlay_remain_separate(self):
        # Save one failed injected-provider attempt with unreported input usage.
        class MissingUsageHTTP(MockHTTP):
            def __call__(self, *args):
                response = super().__call__(*args)
                response["usage"].pop("prompt_tokens", None)
                return response
        scratch = self.root / "failed"
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             BudgetLedger(self.root / "failed-ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=MissingUsageHTTP(), evidence_kind="mocked_provider")
            with self.assertRaises(ValueError):
                asyncio.run(run_town(self.config, self.runs[0], backend, scratch))
        archived = self.source / "_incomplete" / "attempt-1"
        archived.mkdir(parents=True)
        shutil.copytree(scratch / self.runs[0]["run_id"], archived / self.runs[0]["run_id"])
        overlay = self.source / "rejudged.jsonl"
        overlay.write_text('{"unvalidated":"raw overlay"}\n')
        result = review_collection(self.source, self.destination)
        accounting = result["receipt_accounting"]
        self.assertEqual(accounting["archived_attempts"]["town_count"], 1)
        self.assertGreater(accounting["all_attempts"]["unknown_charge_calls"], 0)
        self.assertIsNone(accounting["all_attempts"]["simulated_cost_usd"])
        self.assertGreater(accounting["all_attempts"]["recorded_known_simulated_cost_subtotal_usd"], 0)
        self.assertEqual(result["labels"]["overlay_files"][0]["sha256"], hashlib.sha256(overlay.read_bytes()).hexdigest())
        self.assertFalse(result["labels"]["overlays_applied"])
        self.assertFalse(result["labels"]["overlay_provenance_validated"])


if __name__ == "__main__":
    unittest.main()
