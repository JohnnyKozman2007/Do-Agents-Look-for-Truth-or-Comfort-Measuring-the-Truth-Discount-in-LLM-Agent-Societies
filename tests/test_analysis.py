"""Pilot analysis over replay-audited fixture towns; no network or model calls."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.analysis import analyze, bootstrap_ci, contrasts, load_towns, pair_rows
from truth_discount.cli import main
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import GenerationResponse
from truth_discount.fixtures import FixtureBackend
from truth_discount.runner import run_town
from truth_discount.scoring import paired_metrics

ROOT = Path(__file__).resolve().parents[1]
MODES = ("mixed", "all_skip", "silent")


def make_towns(root: Path, seeds: int = 3) -> list[dict]:
    """Rumor towns vary by fixture mode so pairs differ; truth twins answer normally."""
    config = load_config(ROOT / "configs/pilot_config.json")
    runs = [r for r in build_manifest(config) if r["seed_id"] < seeds]

    async def collect():
        for index, run in enumerate(runs):
            mode = MODES[index % 3] if run["condition_type"] == "rumor" else "mixed"
            await run_town(config, run, FixtureBackend(mode), root)
    asyncio.run(collect())
    return runs


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.towns_dir = Path(cls.temp.name) / "towns"
        cls.runs = make_towns(cls.towns_dir)
        cls.summary = analyze(cls.towns_dir, Path(cls.temp.name) / "analysis")
        cls.out = Path(cls.temp.name) / "analysis"

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_cell_truth_discount_is_the_mean_of_pair_differences(self):
        towns, config, excluded = load_towns(self.towns_dir)
        self.assertEqual((len(towns), excluded), (48, {}))
        expected = {}
        for pair in paired_metrics(towns):
            cell = next(t["cell_id"] for t in towns if t["run_id"] == pair["truth_run_id"])
            expected.setdefault((pair["model_key"], cell), []).append(pair["truth_discount"])
        self.assertEqual(len(self.summary["cells"]), 8)
        for cell in self.summary["cells"]:
            values = [v for v in expected[(cell["model_key"], cell["cell_id"])] if v is not None]
            self.assertEqual(cell["n_pairs"], 3)
            self.assertAlmostEqual(cell["truth_discount"], sum(values) / len(values))
            self.assertLessEqual(cell["truth_discount_ci_low"], cell["truth_discount"])
            self.assertGreaterEqual(cell["truth_discount_ci_high"], cell["truth_discount"])
            self.assertEqual(cell["cell_name"], config["pilot_cells"][cell["cell_id"] - 1]["name"])

    def test_outputs_are_written_and_consistent(self):
        for name in ("listeners.csv", "pairs.csv", "cells.csv", "summary.json", "report.md"):
            self.assertTrue((self.out / name).is_file(), name)
        for name, count in (("listeners.csv", 48 * 12), ("pairs.csv", 24), ("cells.csv", 8)):
            with (self.out / name).open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), count)
        saved = json.loads((self.out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual((saved["towns"], saved["pairs"], saved["study_eligible"]), (48, 24, False))
        report = (self.out / "report.md").read_text(encoding="utf-8")
        self.assertIn("Cell 1: Maximum Trust", report)
        self.assertIn("not study-eligible", report)

    def test_rumor_values_come_from_the_saved_dialogue(self):
        towns, config, _ = load_towns(self.towns_dir)
        rows = pair_rows(towns, config)
        silent = [r for r in rows if r["omission_rate_rumor"] == max(x["omission_rate_rumor"] for x in rows)]
        self.assertTrue(silent)
        for row in rows:
            self.assertGreaterEqual(row["go_rate_first_hand_truth"], 0)
            self.assertTrue(row["transmission_rate_truth"] is None or 0 <= row["transmission_rate_truth"] <= 1)

    def test_bootstrap_is_deterministic_and_brackets_the_mean(self):
        values = [0.1, 0.4, 0.35, 0.8, 0.5, 0.2, 0.65]
        low, high = bootstrap_ci(values)
        self.assertEqual((low, high), bootstrap_ci(values))
        self.assertLess(low, sum(values) / len(values))
        self.assertGreater(high, sum(values) / len(values))
        self.assertEqual(bootstrap_ci([0.3]), (None, None))

    def test_contrasts_subtract_the_skepticism_cell(self):
        rows = [{"model_key": "m", "cell_id": cell, "truth_discount": value}
                for cell, values in ((2, [0.1, 0.2, 0.3]), (1, [0.5, 0.6, 0.7])) for value in values]
        (result,) = contrasts(rows)
        self.assertEqual((result["cell_id"], result["reference_cell_id"]), (1, 2))
        self.assertAlmostEqual(result["difference"], 0.4)
        self.assertLessEqual(result["ci_low"], 0.4)
        self.assertGreaterEqual(result["ci_high"], 0.4)

    def test_mixed_model_runs_or_is_marked_not_run(self):
        models = self.summary["models"]
        try:
            import statsmodels  # noqa: F401
        except ImportError:
            self.assertEqual(models["status"], "not_run")
            return
        self.assertEqual(models["status"], "run")
        for entry in models["models"].values():
            self.assertNotIn("error", entry)
            self.assertIn("truth", entry["mixed"])
            self.assertIn("truth", entry["ols_town_clustered"])

    def test_tables_are_still_written_without_statsmodels(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch.dict(sys.modules, {"statsmodels": None, "statsmodels.formula.api": None}):
            summary = analyze(self.towns_dir, Path(temp) / "out")
            self.assertEqual(summary["models"]["status"], "not_run")
            self.assertIn("Mixed model not run", (Path(temp) / "out/report.md").read_text(encoding="utf-8"))

    def test_incomplete_towns_are_excluded_and_counted(self):
        class EmptyChat(FixtureBackend):
            async def generate(self, request):
                if request.scene == 3:
                    return GenerationResponse("")
                return await super().generate(request)

        config = load_config(ROOT / "configs/pilot_config.json")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "towns"
            make_towns(root, seeds=1)
            extra = next(r for r in build_manifest(config) if r["seed_id"] == 1)
            asyncio.run(run_town(config, extra, EmptyChat(), root))
            towns, _, excluded = load_towns(root)
            self.assertEqual((len(towns), excluded), (16, {"malformed_response": 1}))
            self.assertEqual(analyze(root, Path(temp) / "out")["excluded_towns"], {"malformed_response": 1})

    def test_cli_refuses_existing_destination(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["analyze", str(self.towns_dir), "--out", str(self.out)])
        self.assertEqual(code, 1)
        self.assertIn("error:", err.getvalue())
        with tempfile.TemporaryDirectory() as temp, redirect_stdout(out):
            self.assertEqual(main(["analyze", str(self.towns_dir), "--out", str(Path(temp) / "new")]), 0)
        self.assertIn('"towns": 48', out.getvalue())


class MainStudyAnalysisTests(unittest.TestCase):
    """Eight of the 64 cells, chosen so every factor has both levels."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.config = load_config(ROOT / "configs/main_config.json")
        model = cls.config["models"]["agent_models"][0]["key"]
        runs = [r for r in build_manifest(cls.config, [model])
                if r["cell_id"] in {1, 2, 3, 5, 9, 17, 33, 64} and r["seed_id"] < 2]

        async def collect():
            for index, run in enumerate(runs):
                mode = MODES[(index + run["cell_id"]) % 3] if run["condition_type"] == "rumor" else "mixed"
                await run_town(cls.config, run, FixtureBackend(mode), root / "towns")
        asyncio.run(collect())
        cls.out = root / "analysis"
        cls.summary = analyze(root / "towns", cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_reports_each_factor_in_high_minus_low_order(self):
        self.assertEqual(self.summary["module"], "main")
        self.assertEqual(self.summary["contrasts"], [])
        knobs = {k["factor"]: k for k in self.summary["knobs"]}
        self.assertEqual(list(knobs), ["closeness", "authority", "reliability", "wealth", "gender", "age"])
        self.assertEqual([(k["level_a"], k["level_b"]) for k in knobs.values()],
                         [("close_friend", "stranger"), ("mayor", "citizen"), ("good_record", "poor_record"),
                          ("rich", "poor"), ("woman", "man"), ("old", "young")])
        pairs = list(csv.DictReader(io.StringIO((self.out / "pairs.csv").read_text(encoding="utf-8"))))
        for factor, row in knobs.items():
            a = [float(p["truth_discount"]) for p in pairs if p[factor] == row["level_a"] and p["truth_discount"]]
            self.assertAlmostEqual(row["truth_discount_a"], sum(a) / len(a))
            # A pair whose rumor town had no mentioning listener has no conditional truth discount.
            self.assertEqual(row["n_pairs_a"] + row["n_pairs_b"], sum(bool(p["truth_discount"]) for p in pairs))
        self.assertEqual(len(pairs), 16)

    def test_writes_the_knob_report_table_and_chart(self):
        report = (self.out / "report.md").read_text(encoding="utf-8")
        self.assertTrue(report.startswith("# Main-study analysis"))
        self.assertIn("| closeness | close_friend / stranger |", report)
        self.assertTrue((self.out / "knobs.csv").is_file())
        if self.summary["plot_written"]:
            self.assertTrue((self.out / "truth_discount_by_knob.png").is_file())
        self.assertEqual(len(self.summary["cells"]), 8)

    def test_model_uses_the_six_specified_factors(self):
        models = self.summary["models"]
        if models["status"] != "run":
            self.skipTest("statsmodels is not installed")
        self.assertIn("C(gender)", models["formula"])
        (entry,) = models["models"].values()
        self.assertNotIn("error", entry)
        self.assertIn("truth:C(closeness)[T.stranger]", entry["mixed"])


if __name__ == "__main__":
    unittest.main()
