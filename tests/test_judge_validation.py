"""Offline calibration preparation keeps all phone calls and hides private labels."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from truth_discount.artifacts import audit_town, save_town
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import GenerationResponse, clone, digest
from truth_discount.fixtures import FixtureBackend
from truth_discount.judge_validation import HUMAN_FIELDS, VERSION, prepare_validation
from truth_discount.runner import run_town


ROOT = Path(__file__).resolve().parents[1]


class ValidationFixture(FixtureBackend):
    async def generate(self, request):
        if request.kind == "chat" and request.scene == 5 and request.seat == 1:
            return GenerationResponse("I had a busy day at work.")
        if request.kind == "judge" and request.seat == 2:
            return GenerationResponse("not a JSON judge response")
        return await super().generate(request)


class JudgeValidationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.out = Path(self.temp.name) / "calibration"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.towns = [await run_town(self.config, run, ValidationFixture("mixed"), self.root)
                      for run in build_manifest(self.config)[:2]]

    def hashes(self):
        return {path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()}

    def read_inventory(self):
        return [json.loads(line) for line in (self.out / "inventory_PRIVATE.jsonl").read_text().splitlines()]

    def test_all_phones_include_rule_coded_and_invalid_labels_without_model_execution(self):
        before = self.hashes()
        report = prepare_validation(self.root, self.out, size=4)
        self.assertEqual(report["status"], "prepared")
        self.assertEqual((report["inventory_phone_calls"], report["sample_size"]), (24, 4))
        self.assertEqual(report["provider_api_calls"], 0)
        self.assertFalse(report["human_results_generated"])
        self.assertFalse(report["study_eligible"])
        inventory = self.read_inventory()
        self.assertEqual(len({row["validation_id"] for row in inventory}), 24)
        rule = [row for row in inventory if row["seat_id"] == 1]
        self.assertTrue(all(row["original_provenance_class"] == "rule" for row in rule))
        self.assertTrue(all(row["original_recorded_judge_input"] is None for row in rule))
        self.assertTrue(all(row["judge_input_origin"] == "reconstructed_not_executed" for row in rule))
        invalid = [row for row in inventory if row["seat_id"] == 2]
        self.assertTrue(all(row["original_evaluation"]["status"] == "malformed" for row in invalid))
        self.assertTrue(all(row["judge_input_origin"] == "recorded" for row in invalid))
        for row in inventory:
            self.assertEqual(row["judge_input_sha256"], digest(row["judge_input"]))
            self.assertEqual(row["phone_sha256"], digest(row["phone_lines"]))
            self.assertIn(row["verification_decision_PRIVATE"]["decision"], {"GO", "SKIP"})
        self.assertEqual(before, self.hashes())

    def test_rater_files_are_blank_blinded_and_retain_original_rubric(self):
        prepare_validation(self.root, self.out, size=4)
        rows = list(csv.DictReader(io.StringIO((self.out / "human_labeling.csv").read_text())))
        self.assertEqual(list(rows[0]), HUMAN_FIELDS)
        self.assertTrue(all(row["human_label"] == row["notes"] == "" for row in rows))
        self.assertTrue(all(len(row["validation_id"]) == 64 for row in rows))
        private = {row["validation_id"]: row for row in self.read_inventory()}
        for row in rows:
            self.assertEqual(row["transcript"], private[row["validation_id"]]["transcript"])
            self.assertEqual(row["target_artist"], private[row["validation_id"]]["target_artist"])
        instructions = (self.out / "labeling_instructions.md").read_text()
        self.assertIn(self.config["judging_and_scoring"]["canonical_judge_prompt"], instructions)
        for hidden in ("model_key", "cell_id", "condition_type", "original_evaluation",
                       "verification_decision_PRIVATE", "stratum_PRIVATE"):
            self.assertNotIn(hidden, instructions)
            self.assertNotIn(hidden, rows[0])

    def test_sampling_is_deterministic_with_explicit_population_and_inclusion_probabilities(self):
        prepare_validation(self.root, self.out, size=4, seed=23)
        another = self.out.parent / "same-sample"
        prepare_validation(self.root, another, size=4, seed=23)
        self.assertEqual((self.out / "human_labeling.csv").read_bytes(),
                         (another / "human_labeling.csv").read_bytes())
        meta = json.loads((self.out / "validation_meta_PRIVATE.json").read_text())
        self.assertEqual(len(meta["strata"]), 4)
        for group in meta["strata"].values():
            self.assertEqual((group["N_h"], group["n_h"]), (6, 1))
            self.assertEqual(group["inclusion_probability"], 1 / 6)
            self.assertEqual(group["inverse_probability_weight"], 6)
        key = list(csv.DictReader(io.StringIO((self.out / "sample_key_PRIVATE.csv").read_text())))
        self.assertEqual(len({row["stratum_PRIVATE"] for row in key}), 4)

    def test_source_manifest_binds_ignored_overlay_without_applying_it(self):
        overlay = self.root / "rejudged.jsonl"
        overlay.write_text("unparsed historical overlay, not a primary-label replacement\n")
        before = self.hashes()
        prepare_validation(self.root, self.out, size=4)
        meta = json.loads((self.out / "validation_meta_PRIVATE.json").read_text())
        manifest = json.loads((self.out / "validation_manifest_PRIVATE.json").read_text())
        self.assertEqual(manifest["version"], VERSION)
        self.assertTrue(manifest["source_before_after_equal"])
        self.assertEqual(meta["source_files_sha256"], before)
        self.assertEqual(meta["ignored_rejudged_overlay_sha256"], before["rejudged.jsonl"])
        self.assertFalse(meta["rejudged_overlays_used"])
        for name, value in manifest["files_sha256"].items():
            self.assertEqual(hashlib.sha256((self.out / name).read_bytes()).hexdigest(), value)
        self.assertEqual(before, self.hashes())

    def test_short_strata_and_invalid_sizes_do_not_silently_change_sample(self):
        with self.assertRaisesRegex(ValueError, "insufficient calibration stratum"):
            prepare_validation(self.root, self.out)
        self.assertFalse(self.out.exists())
        for size in (0, 3, 5, True):
            with self.subTest(size=size), self.assertRaises(ValueError):
                prepare_validation(self.root, self.out, size=size)

    async def test_default_hundred_samples_twenty_five_per_declared_stratum(self):
        for run in build_manifest(self.config)[2:10]:
            await run_town(self.config, run, ValidationFixture("mixed"), self.root)
        report = prepare_validation(self.root, self.out)
        self.assertEqual((report["inventory_phone_calls"], report["sample_size"]), (120, 100))
        meta = json.loads((self.out / "validation_meta_PRIVATE.json").read_text())
        self.assertTrue(all((group["N_h"], group["n_h"]) == (30, 25)
                            and group["inclusion_probability"] == 25 / 30
                            for group in meta["strata"].values()))

    def test_output_stays_outside_source_and_existing_packages_are_preserved(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            prepare_validation(self.root, self.root / "calibration", size=4)
        prepare_validation(self.root, self.out, size=4)
        before = (self.out / "human_labeling.csv").read_bytes()
        with self.assertRaises(FileExistsError):
            prepare_validation(self.root, self.out, size=4)
        self.assertEqual((self.out / "human_labeling.csv").read_bytes(), before)

    def test_missing_or_duplicate_phones_are_rejected(self):
        original = self.towns[0]
        directory = self.root / original["run_id"]
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate):
                town = clone(original)
                if duplicate:
                    town["scene_5_phone_transcripts"].append(clone(town["scene_5_phone_transcripts"][0]))
                else:
                    town["scene_5_phone_transcripts"].pop()
                save_town(directory, town, self.config)
                with self.assertRaises(ValueError):
                    prepare_validation(self.root, self.out, size=4)
                self.assertFalse(self.out.exists())
        save_town(directory, original, self.config)

    def test_source_changes_during_preparation_are_rejected(self):
        from truth_discount import judge_validation
        snapshot = judge_validation._source_hashes
        count = 0
        def changed(root):
            nonlocal count
            count += 1
            if count == 2:
                (root / "changed-during-preparation.txt").write_text("synthetic concurrent source change")
            return snapshot(root)
        with patch.object(judge_validation, "_source_hashes", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "source collection changed"):
                prepare_validation(self.root, self.out, size=4)
        self.assertFalse(self.out.exists())

    def test_legacy_fixture_bundles_remain_unchanged(self):
        for original in self.towns:
            legacy = clone(original)
            legacy["schema_version"] = "truth-discount-offline-0.1"
            legacy.pop("diagnostic_limits")
            legacy.pop("scene_5_mention_step_confirmed")
            save_town(self.root / legacy["run_id"], legacy, self.config)
            self.assertEqual(audit_town(self.root / legacy["run_id"])["schema_version"], legacy["schema_version"])
        before = self.hashes()
        prepare_validation(self.root, self.out, size=4)
        self.assertEqual(before, self.hashes())


if __name__ == "__main__":
    unittest.main()
