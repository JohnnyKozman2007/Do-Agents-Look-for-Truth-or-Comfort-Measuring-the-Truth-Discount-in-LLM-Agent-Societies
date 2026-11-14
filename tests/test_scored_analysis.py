"""Synthetic actor collections and mock-only separate judging, never live calls."""
import asyncio
from contextlib import redirect_stdout, redirect_stderr
import copy
import csv
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
from test_deferred_judging import profile, HTTP, inventory
from truth_discount.budget import BudgetLedger
from truth_discount.cli import main
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import digest
from truth_discount.deferred_judging import judge_collection, make_judge_selection
from truth_discount.fixtures import FixtureBackend
from truth_discount.providers import ProviderBackend
from truth_discount.runner import run_town
from truth_discount.scored_analysis import analyze_scored, load_scored_collection


class ScoredAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.scores = self.root / "source", self.root / "scores"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.runs = build_manifest(self.config)[:2]
        async def create():
            for run in self.runs:
                await run_town(self.config, run, FixtureBackend(), self.source, defer_judging=True)
        asyncio.run(create())
        self.profile = profile(self.config, population="all_phones")
        self.before = inventory(self.source)

    def judge(self, http=None, **flags):
        with patch.dict(os.environ, {"DEFERRED_TEST_KEY": "FAKE_ONLY"}), \
             BudgetLedger(self.root / "ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(self.profile["provider_manifest"], ledger,
                                      transport=http or HTTP(), evidence_kind="mocked_provider")
            return asyncio.run(judge_collection(self.source, self.scores, self.profile, backend,
                execution_authorized=True, spending_authorized=True, **flags))

    def test_analysis_joins_sealed_attempts_without_retaining_histories_or_mutating_originals(self):
        self.judge()
        towns, config, provenance = load_scored_collection(self.source, self.scores, self.profile)
        self.assertEqual((len(towns), provenance["source_phone_outcomes"], provenance["judgment_status_counts"]),
                         (2, 24, {"valid": 24}))
        self.assertEqual(config, self.config)
        self.assertTrue(all(t["metrics"]["status"] == "complete" for t in towns))
        for town in towns:
            for forbidden in ("calls", "agent_histories", "native_response", "scene_5_phone_transcripts"):
                self.assertNotIn(forbidden, town)
        out = self.root / "analysis"
        report = analyze_scored(self.source, self.scores, self.profile, out)
        self.assertEqual((report["pairs"], report["missing_judgments"], report["invalid_judgments"]), (1, 0, 0))
        self.assertFalse(report["full_config_coverage"])
        with (out / "listeners.csv").open(newline="") as stream:
            listener = next(csv.DictReader(stream))
        with (out / "pairs.csv").open(newline="") as stream:
            pair = next(csv.DictReader(stream))
        self.assertTrue(listener["generation_attempt_id"])
        self.assertEqual(listener["saved_evaluation_status"], "valid")
        self.assertTrue(pair["truth_generation_attempt_id"])
        self.assertTrue(pair["rumor_generation_attempt_id"])
        self.assertEqual(report["models"]["status"], "blocked")
        self.assertEqual(json.loads((out / "summary.json").read_bytes())["source_sha256"], provenance["source_sha256"])
        self.assertEqual(self.before, inventory(self.source))

    def test_invalid_first_attempt_is_never_silently_replaced_with_a_good_repair(self):
        self.judge(HTTP(malformed=True))
        self.judge(HTTP(), resume=True, retry_invalid=True)
        first, _, provenance = load_scored_collection(self.source, self.scores, self.profile)
        latest, _, sensitivity = load_scored_collection(self.source, self.scores, self.profile,
                                                        attempt_policy="latest_sensitivity")
        self.assertEqual(provenance["judgment_status_counts"], {"malformed": 24})
        self.assertTrue(all(t["metrics"]["belief_mean"] is None for t in first))
        self.assertTrue(all(t["metrics"]["status"] == "complete" for t in latest))
        self.assertEqual(sensitivity["judgment_status_counts"], {"valid": 24})
        self.assertEqual(sensitivity["repaired_items"], 24)
        self.assertEqual(self.before, inventory(self.source))

    def test_small_calibration_selection_preserves_all_generated_listener_denominators(self):
        from truth_discount.deferred_judging import plan_judging
        original = plan_judging(self.source, self.profile)
        self.profile["selection"] = make_judge_selection(self.source, self.profile,
            [original["items"][0]["item_id"]], approved=True)
        self.judge()
        towns, _, provenance = load_scored_collection(self.source, self.scores, self.profile)
        self.assertEqual(len(towns), 2)
        self.assertEqual(provenance["judgment_status_counts"], {"unselected": 23, "valid": 1})
        self.assertTrue(provenance["explicit_phone_selection"])
        self.assertTrue(all(t["metrics"]["belief_mean"] is None for t in towns))

    def test_forged_or_changed_generation_is_rejected_even_with_good_scores(self):
        self.judge()
        path = self.source / self.runs[0]["run_id"] / "town.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "hash|checksum|integrity"):
            load_scored_collection(self.source, self.scores, self.profile)

    def test_destination_and_concurrent_sidecar_changes_fail_without_creating_results(self):
        self.judge()
        for destination in (self.source / "analysis", self.scores / "analysis", self.root):
            with self.assertRaises((ValueError, FileExistsError)):
                analyze_scored(self.source, self.scores, self.profile, destination)
        from truth_discount import scored_analysis
        original = scored_analysis._verify_source_files
        def change_sidecar(*args):
            original(*args)
            journal = self.scores / self.profile["profile_id"] / "attempts.jsonl"
            journal.write_bytes(journal.read_bytes() + b" ")
        with patch.object(scored_analysis, "_verify_source_files", side_effect=change_sidecar):
            with self.assertRaisesRegex(ValueError, "sidecar changed"):
                analyze_scored(self.source, self.scores, self.profile, self.root / "rejected")
        self.assertFalse((self.root / "rejected").exists())

    def test_cli_reads_saved_labels_without_credentials_ledger_or_network(self):
        self.judge()
        file = self.root / "profile.json"
        file.write_text(json.dumps(self.profile))
        out, error = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {}, clear=True), \
             patch("truth_discount.budget.BudgetLedger", side_effect=AssertionError("opened ledger")), \
             redirect_stdout(out), redirect_stderr(error):
            code = main(["analyze-scored", str(self.source), "--profile", str(file),
                         "--judge-output", str(self.scores), "--out", str(self.root / "cli-analysis")])
        self.assertEqual(code, 0, error.getvalue())
        self.assertEqual(json.loads(out.getvalue())["pairs"], 1)
        self.assertEqual(self.before, inventory(self.source))

    def test_main_access_requires_policy_before_any_actor_or_label_replay(self):
        # Metadata-only synthetic fixture. It deliberately has no replayable
        # actor payload, so this proves the access gate runs before _source.
        main = load_config(ROOT / "configs/main_config.json")
        gate_source = self.root / "quarantine-metadata"
        gate_source.mkdir()
        (gate_source / "town.json").write_text("{}")
        (gate_source / "config.json").write_text(json.dumps(main))
        (gate_source / "manifest.json").write_text(json.dumps({"evidence_kind": "development_pilot"}))
        from truth_discount import scored_analysis
        with patch.object(scored_analysis, "_source", side_effect=AssertionError("read outcomes")) as audit:
            for authorize in (False, True):
                with self.assertRaisesRegex(ValueError, "quarantined|analysis policy"):
                    load_scored_collection(gate_source, self.scores, self.profile,
                                           outcomes_authorized=authorize)
            self.assertEqual(audit.call_count, 0)
        from truth_discount.confirmatory_analysis import analysis_policy_template
        from truth_discount.deferred_judging import _profile
        profile_hash = digest(_profile(self.profile))
        candidate = analysis_policy_template(main, profile_hash, "1" * 64)
        sidecar = self.scores / self.profile["profile_id"]
        sidecar.mkdir(parents=True)
        (sidecar / "judging_plan.json").write_text(json.dumps({
            "profile_sha256": profile_hash, "source_sha256": "1" * 64}))
        mismatch = copy.deepcopy(candidate)
        mismatch.update(approved=True, unresolved_policy=[])
        mismatch["source_sha256"] = "2" * 64
        with patch.object(scored_analysis, "_source", side_effect=AssertionError("read outcomes")) as audit:
            for policy in (candidate, mismatch):
                with self.assertRaisesRegex(ValueError, "unapproved|binding"):
                    load_scored_collection(gate_source, self.scores, self.profile,
                                           outcomes_authorized=True, analysis_policy=policy)
            self.assertEqual(audit.call_count, 0)

    def test_mutation_during_table_or_model_computation_cannot_publish_a_snapshot(self):
        self.judge()
        from truth_discount import scored_analysis
        original = scored_analysis.analysis.listener_rows
        def change_journal(*args):
            rows = original(*args)
            journal = self.scores / self.profile["profile_id"] / "attempts.jsonl"
            journal.write_bytes(journal.read_bytes() + b" ")
            return rows
        with patch.object(scored_analysis.analysis, "listener_rows", side_effect=change_journal):
            with self.assertRaisesRegex(ValueError, "sidecar changed"):
                analyze_scored(self.source, self.scores, self.profile, self.root / "late-change")
        self.assertFalse((self.root / "late-change").exists())


if __name__ == "__main__":
    unittest.main()
