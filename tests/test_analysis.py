"""Pilot analysis over replay-audited fixture towns; no network or model calls."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
import csv
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.analysis import (analyze, bootstrap_ci, cell_summary, condition_summary, contrasts,
                                     listener_rows, load_towns, mixed_models, pair_rows)
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
        self.assertEqual(models["inference_status"], "exploratory_not_confirmatory")
        self.assertFalse(models["specification_finalized"])
        for entry in models["models"].values():
            self.assertTrue("mixed" in entry or entry["fit_failures"])
            self.assertIn("truth", entry["ols_town_clustered"])
            self.assertIn("truth", entry["ols_twin_pair_clustered"])

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
        self.assertTrue("mixed" in entry or entry["fit_failures"])
        self.assertIn("truth:C(closeness)[T.stranger]", entry["ols_twin_pair_clustered"])


class AnalysisBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.towns = self.root / "towns"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.runs = build_manifest(self.config)[:2]

    def collect_fixtures(self, backends=None, configs=None):
        backends = backends or [FixtureBackend(), FixtureBackend()]
        configs = configs or [self.config, self.config]
        async def collect():
            for run, backend, config in zip(self.runs, backends, configs):
                await run_town(config, run, backend, self.towns)
        asyncio.run(collect())

    def analyze_descriptive(self):
        with patch("truth_discount.analysis.mixed_models", return_value={"status": "not_run", "reason": "synthetic boundary test"}):
            return analyze(self.towns, self.root / "analysis")

    def test_missing_and_invalid_judgments_are_not_nonmention(self):
        self.collect_fixtures()
        towns, _, _ = load_towns(self.towns)
        town = copy.deepcopy(towns[0])
        town["judge_evaluations"] = [row for row in town["judge_evaluations"] if row["seat_id"] != 1]
        town["judge_evaluations"][0].update(status="malformed", label=None)
        rows = listener_rows([town], self.config)
        self.assertEqual(len(rows), 12)
        missing = next(row for row in rows if row["seat_id"] == 1)
        self.assertEqual(missing["judgment_status"], "missing")
        self.assertIsNone(missing["mentioned"])
        self.assertIsNone(missing["belief"])
        invalid = next(row for row in rows if row["judgment_status"] == "invalid")
        self.assertIsNone(invalid["mentioned"])
        self.assertIsNone(invalid["belief"])
        (condition,) = condition_summary([town], self.config)
        self.assertEqual(condition["missing_judgment_count"], 1)
        self.assertEqual(condition["invalid_judgment_count"], 1)
        self.assertIsNone(condition["omission_rate"])

    def test_invalid_judge_preserves_pair_and_observed_go_denominators(self):
        class BadJudge(FixtureBackend):
            async def generate(self, request):
                if request.kind == "judge" and request.seat == 1:
                    return GenerationResponse("not valid judge JSON")
                return await super().generate(request)
        self.collect_fixtures(backends=[BadJudge(), FixtureBackend()])
        summary = self.analyze_descriptive()
        self.assertEqual(summary["pairs"], 1)
        self.assertEqual(summary["pairs_with_incomplete_judgments"], 1)
        self.assertEqual(summary["invalid_judgments"], 1)
        cell = summary["cells"][0]
        self.assertIsNone(cell["truth_discount"])
        self.assertEqual((cell["truth_discount_n"], cell["truth_discount_n_missing"]), (0, 1))
        self.assertIsNone(cell["sensitivity_lower_difference"])
        rumor = next(row for row in summary["conditions"] if row["condition_type"] == "rumor")
        self.assertEqual((rumor["go_first_hand_count"], rumor["go_first_hand_expected_denominator"]), (3, 6))
        self.assertEqual(rumor["go_first_hand_observed_denominator"], 6)
        self.assertEqual(rumor["go_rate_first_hand"], .5)
        self.assertIn("not human-adjudicated", summary["measurement_limits"]["transmission"])
        self.assertIn("n=0, missing=1", (self.root / "analysis/report.md").read_text(encoding="utf-8"))

    def test_unmatched_town_keeps_condition_counts_without_inventing_pair(self):
        self.collect_fixtures(backends=[FixtureBackend()])
        summary = self.analyze_descriptive()
        self.assertEqual((summary["towns"], summary["pairs"], summary["unmatched_completed_towns"]), (1, 0, 1))
        self.assertEqual(summary["cells"], [])
        self.assertFalse(summary["plot_written"])
        self.assertEqual(summary["conditions"][0]["go_first_hand_expected_denominator"], 6)
        self.assertTrue((self.root / "analysis/conditions.csv").is_file())

    def test_twin_matching_rejects_duplicates_and_changed_layout(self):
        self.collect_fixtures()
        towns, _, _ = load_towns(self.towns)
        with self.assertRaisesRegex(ValueError, "duplicate town"):
            pair_rows([towns[0], towns[0]], self.config)
        altered = copy.deepcopy(towns)
        altered[0]["layout_id"] += 1
        with self.assertRaisesRegex(ValueError, "different matching metadata"):
            pair_rows(altered, self.config)

    def test_bootstrap_uses_pair_differences_and_counts_undefined_outcomes(self):
        self.collect_fixtures()
        towns, _, _ = load_towns(self.towns)
        pair = pair_rows(towns, self.config)[0]
        first, second, missing = copy.deepcopy(pair), copy.deepcopy(pair), copy.deepcopy(pair)
        first["truth_discount"], second["truth_discount"], missing["truth_discount"] = -.4, .8, None
        (summary,) = cell_summary([first, second, missing], self.config)
        self.assertAlmostEqual(summary["truth_discount"], .2)
        self.assertEqual((summary["truth_discount_n"], summary["truth_discount_n_missing"]), (2, 1))
        self.assertEqual((summary["truth_discount_ci_low"], summary["truth_discount_ci_high"]), bootstrap_ci([-.4, .8]))
        self.assertEqual(summary["truth_discount_interval_status"], "descriptive_percentile")
        (constant,) = cell_summary([first, copy.deepcopy(first)], self.config)
        self.assertEqual(constant["truth_discount_interval_status"], "degenerate_constant_pairs")

    def test_bootstrap_rejects_nonfinite_values_and_invalid_settings(self):
        for values, kwargs in (([float("nan"), 0], {}), ([float("inf"), 0], {}), ([True, .2], {}),
                               ([0, 1], {"resamples": 0}), ([0, 1], {"level": 1}),
                               ([0, 1], {"level": float("nan")})):
            with self.subTest(values=values, kwargs=kwargs), self.assertRaises(ValueError):
                bootstrap_ci(values, **kwargs)

    def test_mixed_config_is_rejected_even_when_wrong_config_town_is_excluded(self):
        class EmptyChat(FixtureBackend):
            async def generate(self, request):
                return GenerationResponse("") if request.scene == 3 else await super().generate(request)
        other = copy.deepcopy(self.config)
        other["meta"]["town_name"] = "Synthetic other town"
        self.collect_fixtures(backends=[FixtureBackend(), EmptyChat()], configs=[self.config, other])
        with self.assertRaisesRegex(ValueError, "different configurations"):
            load_towns(self.towns)

    def test_provider_manifest_mismatch_is_rejected(self):
        from test_live_cli import approved_test_manifest, MockHTTP
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        first = approved_test_manifest(self.config)
        second = copy.deepcopy(first)
        second["routes"][self.runs[0]["model_key"]]["input_usd_per_million"] = .2
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("no network")), \
             BudgetLedger(self.root / "ledger.jsonl", "1") as ledger:
            for run, manifest in zip(self.runs, (first, second)):
                backend = ProviderBackend(manifest, ledger, transport=MockHTTP(), evidence_kind="mocked_provider")
                asyncio.run(run_town(self.config, run, backend, self.towns))
        with self.assertRaisesRegex(ValueError, "different provider manifests"):
            load_towns(self.towns)

    def test_rejudge_overlay_is_hashed_unapplied_and_input_files_stay_unchanged(self):
        self.collect_fixtures()
        overlay = self.towns / "rejudged.jsonl"
        overlay.write_text('{"final":{"status":"valid","label":"FACT"}}\n', encoding="utf-8")
        before = {p.relative_to(self.towns).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.towns.rglob("*") if p.is_file()}
        summary = self.analyze_descriptive()
        notes = summary["input_notes"]
        self.assertEqual(notes["rejudge_overlay"]["status"], "detected_not_applied")
        self.assertFalse(notes["rejudge_overlay"]["applied"])
        self.assertEqual(notes["rejudge_overlay"]["sha256"], before["rejudged.jsonl"])
        self.assertEqual(len(notes["active_manifest_sha256"]), 2)
        for path, value in notes["active_manifest_sha256"].items():
            self.assertEqual(value, before[path])
        after = {p.relative_to(self.towns).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.towns.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(summary["analysis_source_sha256"]["analysis.py"], hashlib.sha256(
            (ROOT / "src/truth_discount/analysis.py").read_bytes()).hexdigest())

    def test_missing_town_manifest_is_not_silently_ignored(self):
        self.collect_fixtures(backends=[FixtureBackend()])
        (self.towns / "another_unfinished_town").mkdir()
        with self.assertRaisesRegex(ValueError, "lacks a manifest"):
            load_towns(self.towns)

    def test_no_valid_conditional_beliefs_has_explicit_model_status(self):
        rows = [{"mentioned": None, "belief": None}, {"mentioned": 0, "belief": None}]
        result = mixed_models(rows)
        self.assertEqual(result["status"], "not_run")
        self.assertEqual(result["inference_status"], "exploratory_not_confirmatory")

    def test_missing_go_decision_is_not_a_skip_and_fallback_is_counted(self):
        self.collect_fixtures(backends=[FixtureBackend()])
        (town,), _, _ = load_towns(self.towns)
        partial = copy.deepcopy(town)
        partial["scene_2_first_hand_decisions"] = [row for row in partial["scene_2_first_hand_decisions"]
                                                 if row["seat_id"] != 1]
        (condition,) = condition_summary([partial], self.config)
        self.assertEqual(condition["go_first_hand_expected_denominator"], 6)
        self.assertEqual(condition["go_first_hand_observed_denominator"], 5)
        self.assertEqual(condition["go_first_hand_missing_count"], 1)
        self.assertIsNone(condition["go_rate_first_hand"])
        self.assertAlmostEqual(condition["go_rate_first_hand_among_observed"], 2 / 5)
        fallback = copy.deepcopy(town)
        row = next(row for row in fallback["scene_2_first_hand_decisions"] if row["seat_id"] == 1)
        row.update(decision="SKIP", parse_status="malformed_fallback_skip")
        (condition,) = condition_summary([fallback], self.config)
        self.assertEqual(condition["go_first_hand_fallback_skip_count"], 1)
        self.assertEqual(condition["go_first_hand_observed_denominator"], 6)

    def test_all_valid_nonmention_stays_distinct_from_invalid_judgments(self):
        self.collect_fixtures(backends=[FixtureBackend("silent"), FixtureBackend("silent")])
        summary = self.analyze_descriptive()
        self.assertEqual((summary["invalid_judgments"], summary["missing_judgments"]), (0, 0))
        self.assertEqual(summary["pairs_with_incomplete_judgments"], 0)
        self.assertEqual(summary["pairs_with_undefined_conditional_belief"], 1)
        self.assertEqual(summary["cells"][0]["sensitivity_lower_difference"], 0)
        self.assertEqual(summary["cells"][0]["sensitivity_neutral_difference"], 0)
        self.assertIsNone(summary["cells"][0]["truth_discount"])
        self.assertFalse(summary["plot_written"])

    def test_completed_town_and_excluded_town_cannot_mix_evidence(self):
        from test_live_cli import approved_test_manifest, MockHTTP
        from truth_discount.budget import BudgetLedger
        from truth_discount.providers import ProviderBackend
        class EmptyChat(MockHTTP):
            def __call__(self, method, url, headers, body, timeout_seconds):
                result = super().__call__(method, url, headers, body, timeout_seconds)
                if "choices" in result and body["max_tokens"] != 5:
                    result["choices"][0]["message"]["content"] = ""
                return result
        asyncio.run(run_town(self.config, self.runs[0], FixtureBackend(), self.towns))
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("no network")), \
             BudgetLedger(self.root / "ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(approved_test_manifest(self.config), ledger, transport=EmptyChat(),
                                      evidence_kind="mocked_provider")
            asyncio.run(run_town(self.config, self.runs[1], backend, self.towns))
        with self.assertRaisesRegex(ValueError, "cannot pool"):
            load_towns(self.towns)

    def test_archived_partial_is_pinned_and_excluded_from_outcome_metrics(self):
        class EmptyChat(FixtureBackend):
            async def generate(self, request):
                return GenerationResponse("") if request.scene == 3 else await super().generate(request)
        self.collect_fixtures()
        archive = self.towns / "_incomplete/attempt-1"
        asyncio.run(run_town(self.config, self.runs[0], EmptyChat(), archive))
        summary = self.analyze_descriptive()
        self.assertEqual((summary["towns"], summary["pairs"]), (2, 1))
        archived = summary["input_notes"]["archived_attempts_excluded_from_outcomes"]
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["run_status"], "malformed_response")
        self.assertEqual(len(summary["input_notes"]["archived_manifest_sha256"]), 1)

    def test_archived_completed_attempt_requires_explicit_selection_policy(self):
        self.collect_fixtures()
        asyncio.run(run_town(self.config, self.runs[0], FixtureBackend(), self.towns / "_incomplete/attempt-1"))
        with self.assertRaisesRegex(ValueError, "explicit attempt-selection policy"):
            self.analyze_descriptive()

    def test_analysis_destination_cannot_mutate_the_input_collection(self):
        self.collect_fixtures()
        with self.assertRaisesRegex(ValueError, "outside the saved collection"):
            analyze(self.towns, self.towns / "analysis")
        self.assertFalse((self.towns / "analysis").exists())

    def test_contrast_with_undefined_cell_is_reported_as_missing(self):
        rows = [{"model_key": "model", "cell_id": 1, "truth_discount": None},
                {"model_key": "model", "cell_id": 2, "truth_discount": .2}]
        (result,) = contrasts(rows)
        self.assertIsNone(result["difference"])
        self.assertIsNone(result["ci_low"])
        self.assertEqual((result["n_pairs"], result["n_missing_pairs"]), (0, 1))
        self.assertEqual(result["interval_status"], "insufficient_pairs")
        self.assertFalse(result["confirmatory"])


class OptionalModelBoundaryTests(unittest.TestCase):
    def setUp(self):
        try:
            import statsmodels  # noqa: F401
        except ImportError:
            self.skipTest("statsmodels is not installed")
        self.rows = [{"mentioned": 1, "belief": .1 + .3 * truth + .02 * pair + .01 * seat,
                      "model_key": "synthetic", "pair_id": f"pair-{pair}",
                      "run_id": f"pair-{pair}-truth-{truth}", "truth": truth,
                      "cell_id": pair % 2 + 1, "real_artist": (pair // 2) % 2}
                     for pair in range(8) for truth in (0, 1) for seat in range(5)]

    def test_nonfinite_fit_values_are_missing_and_nonconvergence_is_explicit(self):
        import pandas as pd
        params = pd.Series({"Intercept": float("nan"), "truth": float("nan")})
        fit = SimpleNamespace(params=params, bse=params, pvalues=params, converged=False,
                              conf_int=lambda: pd.DataFrame([[float("nan")] * 2] * 2, index=params.index))
        with patch("statsmodels.formula.api.mixedlm", return_value=Mock(fit=Mock(return_value=fit))):
            result = mixed_models(self.rows)
        entry = result["models"]["synthetic"]
        self.assertIsNone(entry["mixed"]["truth"]["estimate"])
        self.assertEqual(entry["mixed_status"], "nonconverged_do_not_interpret")
        self.assertIn("ols_twin_pair_clustered", entry)
        self.assertEqual((entry["n_towns"], entry["n_twin_pairs"]), (16, 8))
        json.dumps(result, allow_nan=False)

    def test_rank_deficient_design_is_reported_without_pseudoinverse_effect_claim(self):
        rows = copy.deepcopy(self.rows)
        for row in rows:
            row["truth"] = 1
        result = mixed_models(rows)
        entry = result["models"]["synthetic"]
        self.assertLess(entry["design_rank"], entry["design_columns"])
        self.assertIn("rank-deficient", entry["fit_failures"]["design"])
        self.assertNotIn("mixed", entry)
        self.assertNotIn("ols_twin_pair_clustered", entry)
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
