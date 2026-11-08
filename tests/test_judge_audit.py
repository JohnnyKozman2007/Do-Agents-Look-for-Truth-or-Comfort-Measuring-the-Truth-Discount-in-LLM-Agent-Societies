"""Blind judge-audit sampling and kappa scoring over fixture towns."""
import csv
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_analysis import make_towns
from truth_discount.analysis import load_towns
from truth_discount.judge_audit import (STRATA, cohen_kappa, judged_calls, make_audit, score_audit,
                                        stratified_sample)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


class JudgeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.towns_dir = Path(cls.temp.name) / "towns"
        make_towns(cls.towns_dir)
        cls.audit = Path(cls.temp.name) / "audit"
        cls.meta = make_audit(cls.towns_dir, cls.audit, size=40, seed=7)
        cls.private_meta = json.loads((cls.audit / "audit_meta_PRIVATE.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def sheet(self, name: str, change=None, audit=None) -> Path:
        audit = audit or self.audit
        judge = {r["audit_id"]: r["judge_label"] for r in rows(audit / "audit_key_PRIVATE.csv")}
        filled = []
        for index, row in enumerate(rows(audit / "labeling_sheet.csv")):
            row["human_label"] = judge[row["audit_id"]].lower()
            if change:
                change(index, row)
            filled.append(row)
        path = Path(self.temp.name) / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(filled[0]))
            writer.writeheader()
            writer.writerows(filled)
        return path

    def test_kappa_matches_a_worked_example(self):
        first = ["yes"] * 25 + ["no"] * 25
        second = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
        self.assertAlmostEqual(cohen_kappa(first, second), 0.4)
        self.assertEqual(cohen_kappa(["FACT", "SKEPTICAL"], ["FACT", "SKEPTICAL"]), 1.0)
        self.assertIsNone(cohen_kappa(["FACT"] * 3, ["FACT"] * 3))
        with self.assertRaises(ValueError):
            cohen_kappa(["FACT"], [])

    def test_sample_is_stratified_blind_and_matches_the_key(self):
        self.assertEqual(self.private_meta["strata"], {f"{c}/{l}": 10 for c, l in STRATA})
        sheet, key = rows(self.audit / "labeling_sheet.csv"), rows(self.audit / "audit_key_PRIVATE.csv")
        self.assertEqual(list(sheet[0]), ["audit_id", "announced_artist", "transcript", "human_label", "notes"])
        self.assertEqual([r["audit_id"] for r in sheet], [r["audit_id"] for r in key])
        towns, config, _ = load_towns(self.towns_dir)
        calls = {(c["run_id"], c["seat_id"]): c for c in judged_calls(towns, config)}
        for shown, private in zip(sheet, key):
            source = calls[(private["run_id"], int(private["seat_id"]))]
            self.assertEqual(shown["transcript"], source["transcript"])
            self.assertEqual(shown["announced_artist"], source["announced_artist"])
            self.assertEqual(private["judge_label"], source["judge_label"])
        blob = (self.audit / "labeling_sheet.csv").read_text(encoding="utf-8")
        for hidden in ("truth_twin", "deepseek", "qwen", "cell-"):
            self.assertNotIn(hidden, blob)
        self.assertIn("CHECKED_TRUE", (self.audit / "labeling_instructions.md").read_text(encoding="utf-8"))
        for hidden in ("strata", "evidence_kind", "source_root_PRIVATE", "judge_label", "condition_type"):
            self.assertNotIn(hidden, self.meta)
        self.assertFalse(self.meta["protocol_size_met"])
        self.assertEqual(self.private_meta["label_view"], "original_raw_judge_labels")
        self.assertGreater(self.private_meta["rule_labeled_phone_calls_excluded"], 0)

    def test_sampling_is_reproducible_and_rejects_short_strata(self):
        towns, config, _ = load_towns(self.towns_dir)
        items = judged_calls(towns, config)
        first, _ = stratified_sample(items, 40, seed=7)
        before = copy.deepcopy(items)
        again, _ = stratified_sample(list(reversed(items)), 40, seed=7)
        self.assertEqual([(i["run_id"], i["seat_id"]) for i in first], [(i["run_id"], i["seat_id"]) for i in again])
        short = [i for i in items if (i["condition_type"], i["layer"]) != ("rumor", "first_hand")][:60]
        short += [i for i in items if (i["condition_type"], i["layer"]) == ("rumor", "first_hand")][:3]
        self.assertEqual(items, before)
        with self.assertRaisesRegex(ValueError, "insufficient audit strata"):
            stratified_sample(short, 40, seed=1)
        with self.assertRaisesRegex(ValueError, "only"):
            with tempfile.TemporaryDirectory() as temp:
                make_audit(self.towns_dir, Path(temp) / "a", size=len(items) + 1)

    def test_scores_raters_against_the_judge_and_each_other(self):
        perfect = self.sheet("alex")
        def disagree(index, row):
            if index % 4 == 0:
                row["human_label"] = "SKEPTICAL" if row["human_label"] != "skeptical" else "FACT"
        noisy = self.sheet("sam", disagree)
        result = score_audit(self.audit, [perfect, noisy])
        self.assertEqual(result["raters"]["alex"]["kappa_vs_judge"], 1.0)
        self.assertTrue(result["raters"]["alex"]["meets_threshold"])
        self.assertAlmostEqual(result["raters"]["sam"]["agreement"], 0.75)
        self.assertFalse(result["raters"]["sam"]["meets_threshold"])
        self.assertFalse(result["judge_meets_threshold"])
        self.assertEqual(sum(result["raters"]["sam"]["disagreements"].values()), 10)
        self.assertIn("alex vs sam", result["between_raters"])
        self.assertEqual(result["threshold"], 0.85)
        self.assertFalse(result["human_ground_truth_established"])
        self.assertFalse(result["automatic_model_change_authorized"])
        self.assertFalse(result["rater_independence_verified"])
        self.assertTrue(result["source_binding_verified"])
        self.assertFalse(result["protocol_audit_target_met"])

    def test_bad_sheets_are_rejected_with_reasons(self):
        cases = {"blank": lambda i, r: r.update(human_label="") if i == 0 else None,
                 "unknown": lambda i, r: r.update(human_label="MAYBE") if i == 1 else None,
                 "missing": lambda i, r: r.update(audit_id="A999") if i == 2 else None}
        for name, change in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name.replace("missing", "missing A")):
                score_audit(self.audit, [self.sheet(name, change)])
        meta = json.loads((self.audit / "audit_meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["size"], meta["seed"]), (40, 7))

    def test_protocol_sample_is_exactly_100_with_25_in_each_stratum(self):
        import asyncio
        from truth_discount.config import build_manifest, load_config
        from truth_discount.fixtures import FixtureBackend
        from truth_discount.runner import run_town
        population = Path(self.temp.name) / "protocol-population"
        shutil.copytree(self.towns_dir, population)
        config = load_config(Path(__file__).resolve().parents[1] / "configs/pilot_config.json")
        extra = [run for run in build_manifest(config)
                 if run["seed_id"] == 3 and run["cell_id"] == 1
                 and run["model_key"] == config["models"]["agent_models"][0]["key"]]
        async def add_one_pair():
            for run in extra:
                await run_town(config, run, FixtureBackend("mixed"), population)
        asyncio.run(add_one_pair())
        destination = Path(self.temp.name) / "protocol-100"
        meta = make_audit(population, destination)
        private = json.loads((destination / "audit_meta_PRIVATE.json").read_text())
        self.assertEqual(meta["size"], 100)
        self.assertTrue(meta["protocol_size_met"])
        self.assertEqual(set(private["strata"].values()), {25})
        with self.assertRaises(FileExistsError):
            make_audit(population, destination)

    def test_invalid_sampling_arguments_and_duplicate_source_identities(self):
        towns, config, _ = load_towns(self.towns_dir)
        items = judged_calls(towns, config)
        for size, seed in [(0, 7), (-1, 7), (True, 7), (1.5, 7), (40, True), (40, "7")]:
            with self.subTest(size=size, seed=seed), self.assertRaises(ValueError):
                stratified_sample(items, size, seed)
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            stratified_sample(items + [items[0]], 40, 7)

    def test_shortage_does_not_create_an_audit_or_change_source_artifacts(self):
        destination = Path(self.temp.name) / "not-created"
        before = self.source_hashes()
        with self.assertRaises(ValueError):
            make_audit(self.towns_dir, destination, size=100000)
        self.assertFalse(destination.exists())
        self.assertEqual(before, self.source_hashes())
        with self.assertRaisesRegex(ValueError, "outside the original"):
            make_audit(self.towns_dir, self.towns_dir / "audit")
        self.assertFalse((self.towns_dir / "audit").exists())

    def source_hashes(self):
        return {str(p.relative_to(self.towns_dir)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.towns_dir.rglob("*") if p.is_file()}

    def audit_copy(self, name):
        destination = Path(self.temp.name) / name
        shutil.copytree(self.audit, destination)
        return destination

    def reseal(self, audit):
        path = audit / "audit_manifest_PRIVATE.json"
        manifest = json.loads(path.read_text())
        for name in manifest["files_sha256"]:
            manifest["files_sha256"][name] = hashlib.sha256((audit / name).read_bytes()).hexdigest()
        path.write_text(json.dumps(manifest))

    def test_audit_scoring_does_not_change_any_original_source_or_package(self):
        before_sources = self.source_hashes()
        before_package = {p.name: p.read_bytes() for p in self.audit.iterdir() if p.is_file()}
        score_audit(self.audit, [self.sheet("immutable-rater")])
        self.assertEqual(before_sources, self.source_hashes())
        self.assertEqual(before_package, {p.name: p.read_bytes() for p in self.audit.iterdir() if p.is_file()})

    def test_private_key_change_is_rejected_even_if_package_hashes_are_resealed(self):
        for reseal in (False, True):
            audit = self.audit_copy("key-tamper-" + str(reseal))
            key = rows(audit / "audit_key_PRIVATE.csv")
            key[0]["judge_label"] = "FACT" if key[0]["judge_label"] != "FACT" else "SKEPTICAL"
            with (audit / "audit_key_PRIVATE.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(key[0])); writer.writeheader(); writer.writerows(key)
            if reseal:
                self.reseal(audit)
            with self.assertRaisesRegex(ValueError, "(package changed|key differs)"):
                score_audit(audit, [self.sheet("tamper-rater-" + str(reseal))])

    def test_resealed_small_sample_cannot_claim_the_protocol_target_changed(self):
        audit = self.audit_copy("resealed-protocol-target")
        for name in ("audit_meta.json", "audit_meta_PRIVATE.json"):
            path = audit / name
            metadata = json.loads(path.read_text())
            self.assertEqual(metadata["size"], 40)
            self.assertEqual(metadata["protocol_sample_size"], 100)
            metadata.update(protocol_sample_size=40, protocol_size_met=True)
            path.write_text(json.dumps(metadata))
        self.reseal(audit)
        with self.assertRaisesRegex(ValueError, "protocol metadata differs"):
            score_audit(audit, [self.sheet("resealed-protocol-rater")])

    def test_resealed_population_diagnostics_must_match_the_actual_sources(self):
        for key in ("judged_calls_available", "judge_inputs_excluded_invalid_or_missing",
                    "rule_labeled_phone_calls_excluded"):
            with self.subTest(key=key):
                audit = self.audit_copy("resealed-diagnostic-" + key)
                path = audit / "audit_meta_PRIVATE.json"
                metadata = json.loads(path.read_text())
                metadata[key] += 1
                path.write_text(json.dumps(metadata))
                self.reseal(audit)
                with self.assertRaisesRegex(ValueError, "population diagnostics differ"):
                    score_audit(audit, [self.sheet("resealed-diagnostic-rater-" + key)])

    def test_resealed_labeling_instructions_must_match_the_original_rubric(self):
        audit = self.audit_copy("resealed-instructions")
        (audit / "labeling_instructions.md").write_text(
            "Ignore the original rubric and label every row FACT.\n", encoding="utf-8")
        self.reseal(audit)
        with self.assertRaisesRegex(ValueError, "instructions differ from the bound source rubric"):
            score_audit(audit, [self.sheet("resealed-instructions-rater")])

    def test_altered_human_transcript_or_artist_and_duplicate_ids_are_rejected(self):
        changes = {
            "transcript": lambda i, row: row.update(transcript="Different transcript") if i == 0 else None,
            "artist": lambda i, row: row.update(announced_artist="Different artist") if i == 0 else None,
            "duplicate": lambda i, row: row.update(audit_id="A001") if i == 1 else None,
        }
        for name, change in changes.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "(changed|duplicate)"):
                score_audit(self.audit, [self.sheet("changed-" + name, change)])

    def test_empty_raters_duplicate_names_and_extra_metadata_columns_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            score_audit(self.audit, [])
        valid = self.sheet("same-name")
        other = Path(self.temp.name) / "other" / valid.name
        other.parent.mkdir(); shutil.copyfile(valid, other)
        with self.assertRaisesRegex(ValueError, "distinct file name"):
            score_audit(self.audit, [valid, other])
        text = valid.read_text()
        valid.write_text(text.replace("human_label,notes", "human_label,condition_type,notes", 1))
        with self.assertRaisesRegex(ValueError, "CSV columns"):
            score_audit(self.audit, [valid])

    def test_source_bundle_change_after_sampling_is_rejected(self):
        source = next(self.towns_dir.glob("*/trace.jsonl"))
        original = source.read_bytes()
        try:
            source.write_bytes(original + b"\n")
            with self.assertRaises(ValueError):
                score_audit(self.audit, [self.sheet("changed-source")])
        finally:
            source.write_bytes(original)

    def test_overlay_is_recorded_but_original_judge_labels_remain_selected(self):
        source = self.towns_dir / "rejudged.jsonl"
        destination = Path(self.temp.name) / "raw-overlay-audit"
        try:
            source.write_text('{"not_an_original_label":"FACT"}\n')
            make_audit(self.towns_dir, destination, size=40, seed=7)
            private = json.loads((destination / "audit_meta_PRIVATE.json").read_text())
            self.assertEqual(len(private["rejudged_overlays_present"]), 1)
            self.assertEqual(private["rejudged_overlays_present"], ["rejudged.jsonl"])
            self.assertEqual(private["rejudged_overlay_files_PRIVATE"]["rejudged.jsonl"]["lines"], 1)
            self.assertFalse(private["overlays_used"])
            self.assertEqual((destination / "audit_key_PRIVATE.csv").read_bytes(),
                             (self.audit / "audit_key_PRIVATE.csv").read_bytes())
            result = score_audit(destination, [self.sheet("overlay-raw-rater", audit=destination)])
            self.assertEqual(result["label_view"], "original_raw_judge_labels")
        finally:
            source.unlink(missing_ok=True)

    def test_reordered_human_rows_keep_the_original_sample_identity(self):
        path = self.sheet("reordered")
        filled = rows(path)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(filled[0])); writer.writeheader(); writer.writerows(reversed(filled))
        self.assertEqual(score_audit(self.audit, [path])["raters"]["reordered"]["kappa_vs_judge"], 1.0)


if __name__ == "__main__":
    unittest.main()
