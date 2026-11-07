"""Blind judge-audit sampling and kappa scoring over fixture towns."""
import csv
import json
from pathlib import Path
import sys
import tempfile
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

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def sheet(self, name: str, change=None) -> Path:
        judge = {r["audit_id"]: r["judge_label"] for r in rows(self.audit / "audit_key_PRIVATE.csv")}
        filled = []
        for index, row in enumerate(rows(self.audit / "labeling_sheet.csv")):
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
        self.assertEqual(self.meta["strata"], {f"{c}/{l}": 10 for c, l in STRATA})
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

    def test_sampling_is_reproducible_and_fills_a_short_stratum(self):
        towns, config, _ = load_towns(self.towns_dir)
        items = judged_calls(towns, config)
        first, _ = stratified_sample(items, 40, seed=7)
        again, _ = stratified_sample(items, 40, seed=7)
        self.assertEqual([(i["run_id"], i["seat_id"]) for i in first], [(i["run_id"], i["seat_id"]) for i in again])
        short = [i for i in items if (i["condition_type"], i["layer"]) != ("rumor", "first_hand")][:60]
        short += [i for i in items if (i["condition_type"], i["layer"]) == ("rumor", "first_hand")][:3]
        sample, counts = stratified_sample(short, 40, seed=1)
        self.assertEqual((len(sample), counts["rumor/first_hand"]), (40, 3))
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

    def test_bad_sheets_are_rejected_with_reasons(self):
        cases = {"blank": lambda i, r: r.update(human_label="") if i == 0 else None,
                 "unknown": lambda i, r: r.update(human_label="MAYBE") if i == 1 else None,
                 "missing": lambda i, r: r.update(audit_id="A999") if i == 2 else None}
        for name, change in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name.replace("missing", "missing A")):
                score_audit(self.audit, [self.sheet(name, change)])
        meta = json.loads((self.audit / "audit_meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["size"], meta["seed"]), (40, 7))


if __name__ == "__main__":
    unittest.main()
