"""Synthetic policy/statistical checks only; no experimental outcomes or providers."""
import copy
import itertools
import json
import math
from pathlib import Path
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount import confirmatory_analysis as ca
from truth_discount.config import load_config

ROOT = Path(__file__).resolve().parents[1]
try:
    DEPS = ca._dependencies()
except ImportError:
    DEPS = None


def approved_policy(config, *, family="ten_per_model", attempt="first_only"):
    # Explicit synthetic test approval; no user/team policy is approved here.
    value = ca.analysis_policy_template(config, "a" * 64, "b" * 64, attempt)
    value["approved"], value["unresolved_policy"] = True, []
    value["multiplicity"]["family_scope"] = family
    return value


def synthetic_rows(config, *, seats=4):
    levels, models, artists = ca._design(config)
    rng, rows = random.Random(94017), []
    for cell, factors in enumerate(itertools.product(*(levels[name] for name in ca.FACTORS))):
        values = dict(zip(ca.FACTORS, factors))
        for artist_index, artist in enumerate(artists):
            pair = f"synthetic-pair-{cell}-{artist_index}"
            for truth in (0, 1):
                run = pair + f"-truth-{truth}"
                town_effect = rng.choice((-0.28, 0.28))
                for seat in range(1, seats + 1):
                    latent = 0.45 + 0.08 * truth + town_effect + rng.uniform(-0.24, 0.24)
                    belief = 0 if latent < 0.30 else 0.5 if latent < 0.70 else 1
                    rows.append({"model_key": models[0], "run_id": run, "pair_id": pair,
                        "seat_id": seat, "truth": truth, "real_artist": artist, **values,
                        "judgment_status": "valid", "mentioned": 1, "belief": belief,
                        "judge_profile_sha256": "a" * 64, "judging_source_sha256": "b" * 64,
                        "analysis_attempt_policy": "first_only"})
    return rows


class PolicyGuardTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "configs/main_config.json")

    def test_template_is_reviewable_but_cannot_produce_inference(self):
        policy = ca.analysis_policy_template(self.config, "a" * 64, "b" * 64)
        self.assertFalse(policy["approved"])
        self.assertTrue(policy["unresolved_policy"])
        self.assertEqual(policy["factor_levels"]["authority"], ["mayor", "citizen"])
        self.assertEqual(policy["factor_levels"]["gender"], ["woman", "man"])
        self.assertEqual(policy["factor_levels"]["age"], ["old", "young"])
        self.assertEqual(len(policy["contrasts"]), 10)
        with patch.object(ca, "_dependencies", side_effect=AssertionError("must not fit")):
            with self.assertRaisesRegex(ValueError, "unapproved"):
                ca.planned_contrasts([], self.config, policy)
            policy["approved"] = True
            with self.assertRaisesRegex(ValueError, "unresolved"):
                ca.planned_contrasts([], self.config, policy)

    def test_actual_bindings_attempt_and_supported_family_are_required(self):
        policy = approved_policy(self.config)
        self.assertEqual(ca.validate_policy(policy, self.config, "a" * 64, "b" * 64, "first_only"), policy)
        for name, value in (("judge_profile_sha256", "c" * 64), ("source_sha256", "c" * 64),
                            ("config_sha256", "c" * 64), ("attempt_policy", "latest_sensitivity")):
            changed = copy.deepcopy(policy)
            changed[name] = value
            with self.subTest(field=name), self.assertRaises(ValueError):
                ca.validate_policy(changed, self.config, "a" * 64, "b" * 64, "first_only")
        for profile_hash, source_hash in (("", "b" * 64), ("a" * 64, ""), (None, "b" * 64)):
            with self.assertRaisesRegex(ValueError, "binding"):
                ca.analysis_policy_template(self.config, profile_hash, source_hash)
        changed = copy.deepcopy(policy)
        changed["multiplicity"]["family_scope"] = "observed_tests_only"
        with self.assertRaisesRegex(ValueError, "explicit"):
            ca.validate_policy(changed, self.config, "a" * 64, "b" * 64, "first_only")
        latest = approved_policy(self.config, attempt="latest_sensitivity")
        ca.validate_policy(latest, self.config, "a" * 64, "b" * 64, "latest_sensitivity")

    def test_pilot_aliasing_is_not_rebranded_as_confirmatory_main(self):
        pilot = load_config(ROOT / "configs/pilot_config.json")
        with self.assertRaisesRegex(ValueError, "main factorial"):
            ca.analysis_policy_template(pilot, "a" * 64, "b" * 64)

    def test_row_provenance_invalid_scores_and_duplicate_pairs_fail_closed(self):
        policy = approved_policy(self.config)
        row = synthetic_rows(self.config)[0]
        for mutate in (lambda r: r.update(judge_profile_sha256="c" * 64),
                       lambda r: r.update(analysis_attempt_policy="latest_sensitivity"),
                       lambda r: r.update(judgment_status="invalid", belief=0, mentioned=None)):
            changed = copy.deepcopy(row)
            mutate(changed)
            with self.assertRaises(ValueError):
                ca._validated_rows([changed], self.config, policy)
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            ca._validated_rows([row, row], self.config, policy)
        other = copy.deepcopy(row)
        other["run_id"] += "-second-town"
        with self.assertRaisesRegex(ValueError, "duplicate truth condition"):
            ca._validated_rows([row, other], self.config, policy)

    def test_missing_dependencies_keep_twenty_planned_hypotheses(self):
        policy = approved_policy(self.config, family="twenty_global")
        with patch.object(ca, "_dependencies", side_effect=ImportError("optional test dependency")):
            result = ca.planned_contrasts([], self.config, policy)
        family = result["multiplicity"]["families"]["all_actors"]
        self.assertEqual((family["planned_hypotheses"], family["available_hypotheses"]), (20, 0))
        self.assertTrue(all(row["p_value"] is None and row["holm_adjusted_p"] is None
                            for model in result["models"].values() for row in model["contrasts"]))


@unittest.skipUnless(DEPS is not None, "optional numpy/pandas/patsy/scipy/statsmodels dependencies")
class StatisticalContrastTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "configs/main_config.json")
        self.policy = approved_policy(self.config)
        self.levels, self.models, self.artists = ca._design(self.config)
        self.np, self.pd, self.patsy, self.norm, self.smf = DEPS

    def known_model(self):
        grid = ca._grid(self.levels, self.artists, self.pd)
        x = self.patsy.dmatrix(ca.FORMULA.split("~", 1)[1], grid, return_type="dataframe")
        friend = (grid["closeness"] == "close_friend").to_numpy(dtype=float)
        mayor = (grid["authority"] == "mayor").to_numpy(dtype=float)
        good = (grid["reliability"] == "good_record").to_numpy(dtype=float)
        rich = (grid["wealth"] == "rich").to_numpy(dtype=float)
        # Independently specified polynomial: its grid-averaged contrasts have
        # closed-form values, including three-way truth interactions.
        truth_discount = (0.12 + 0.10 * friend + 0.08 * good + 0.06 * friend * good
                          + 0.04 * mayor * good + 0.02 * rich * good + 0.03 * friend * mayor)
        mean = 0.30 + grid["truth"].to_numpy() * truth_discount
        beta, _, _, _ = self.np.linalg.lstsq(x.to_numpy(), mean, rcond=None)
        self.assertLess(self.np.max(self.np.abs(x.to_numpy() @ beta - mean)), 1e-12)
        return x, beta

    def test_known_polynomial_and_covariance_give_all_ten_correct_contrasts(self):
        x, beta = self.known_model()
        self.assertEqual(x.shape[1], 23)  # Full hierarchy, not the old 15-column model.
        covariance = self.np.eye(len(beta)) * 0.0001
        rows = ca._linear_contrasts(beta, covariance, x.design_info,
                                   self.levels, self.artists, self.policy, DEPS)
        observed = {row["id"]: row for row in rows}
        expected = {"closeness": .145, "authority": .035, "wealth": .01, "reliability": .14,
                    "closeness_by_reliability": .06, "authority_by_reliability": .04,
                    "wealth_by_reliability": .02, "closeness_by_authority": .03,
                    "gender": 0, "age": 0}
        for name, value in expected.items():
            self.assertAlmostEqual(observed[name]["estimate"], value, places=11, msg=name)
            self.assertEqual(observed[name]["status"], "available")
        for name in ("closeness_by_reliability", "authority_by_reliability",
                     "wealth_by_reliability", "closeness_by_authority", "gender", "age"):
            self.assertAlmostEqual(observed[name]["se"], .01, places=11)
        self.assertAlmostEqual(observed["closeness"]["se"], math.sqrt(.00015), places=11)
        self.assertAlmostEqual(observed["reliability"]["se"], math.sqrt(.000175), places=11)
        self.assertAlmostEqual(observed["gender"]["p_value"], 1, places=10)

    def test_grid_margins_do_not_depend_on_observed_cell_prevalence(self):
        x, beta = self.known_model()
        vectors = ca._contrast_vectors(x.design_info, self.levels, self.artists, DEPS)
        # Reliability's .14 marginal differs from the poor-record conditional
        # coefficient (.08); all omitted dimensions receive uniform grid weight.
        self.assertAlmostEqual(float(vectors["reliability"] @ beta), .14, places=11)
        self.assertAlmostEqual(float(vectors["closeness_by_reliability"] @ beta), .06, places=11)

    def test_holm_matches_reference_and_missing_tests_do_not_shrink_family(self):
        from statsmodels.stats.multitest import multipletests
        p_values = [.001, .006, None, .03, .09, .2, .4, .8, None, 1.0]
        rows = [{"p_value": value} for value in p_values]
        family = ca._holm(rows, 10, .05)
        reference = multipletests([value if value is not None else 1 for value in p_values],
                                  alpha=.05, method="holm")[1]
        self.assertEqual((family["planned_hypotheses"], family["available_hypotheses"]), (10, 8))
        for index, value in enumerate(p_values):
            if value is None:
                self.assertIsNone(rows[index]["holm_adjusted_p"])
                self.assertIsNone(rows[index]["reject_null"])
            else:
                self.assertAlmostEqual(rows[index]["holm_adjusted_p"], reference[index], places=13)
        global_rows = [{"p_value": value} for value in p_values + [None] * 10]
        ca._holm(global_rows, 20, .05)
        self.assertAlmostEqual(global_rows[0]["holm_adjusted_p"], .02)
        self.assertGreater(global_rows[1]["holm_adjusted_p"], rows[1]["holm_adjusted_p"])

    def test_zero_and_nonfinite_contrast_uncertainty_never_become_significance(self):
        x, beta = self.known_model()
        for covariance in (self.np.zeros((len(beta), len(beta))),
                           self.np.full((len(beta), len(beta)), self.np.nan)):
            rows = ca._linear_contrasts(beta, covariance, x.design_info,
                                       self.levels, self.artists, self.policy, DEPS)
            self.assertTrue(all(row["p_value"] is None and row["status"] == "unavailable" for row in rows))

    def test_nonfinite_interval_is_unavailable_and_json_safe(self):
        x, beta = self.known_model()
        oversized_interval = SimpleNamespace(ppf=lambda _: 1e308, sf=self.norm.sf)
        deps = (*DEPS[:3], oversized_interval, DEPS[4])
        rows = ca._linear_contrasts(beta, self.np.eye(len(beta)) * 100,
                                   x.design_info, self.levels, self.artists, self.policy, deps)
        self.assertTrue(all(row["status"] == "unavailable" and row["p_value"] is None for row in rows))
        json.dumps(rows, allow_nan=False)

    def test_nonconvergence_singularity_nonfinite_and_rank_deficiency_are_unavailable(self):
        x, beta = self.known_model()
        rows = synthetic_rows(self.config)
        data = ca._categorical(self.pd.DataFrame(rows), self.levels, self.artists, self.pd)
        _, fitted_design = self.patsy.dmatrices(ca.FORMULA, data, return_type="dataframe")
        covariance = self.pd.DataFrame(self.np.eye(len(beta)) * .01, index=x.columns, columns=x.columns)
        normal = {"converged": True, "cov_re": self.np.array([[.1]]),
                  "fe_params": self.pd.Series(beta, index=x.columns), "scale": .1,
                  "cov_params": lambda: covariance}
        cases = [(dict(normal, converged=False), "nonconverged"),
                 (dict(normal, cov_re=self.np.zeros((1, 1))), "singular_random"),
                 (dict(normal, cov_re=self.np.array([[self.np.nan]])), "nonfinite_fit"),
                 (dict(normal, cov_re=self.np.array([[self.np.inf]])), "nonfinite_fit"),
                 (dict(normal, scale=self.np.nan), "nonfinite_fit"),
                 (dict(normal, scale=self.np.inf), "nonfinite_fit"),
                 (dict(normal, fe_params=self.pd.Series([self.np.nan] * len(beta), index=x.columns)), "nonfinite_fit"),
                 (dict(normal, cov_params=lambda: covariance * 0), "singular_or_indefinite_fixed")]
        for fit_values, expected in cases:
            model = SimpleNamespace(exog=fitted_design.to_numpy(), exog_names=list(fitted_design.columns),
                                    fit=lambda **kwargs: SimpleNamespace(**fit_values))
            with self.subTest(status=expected), patch.object(self.smf, "mixedlm", return_value=model):
                result = ca._fit_actor(rows, self.levels, self.artists, self.policy, DEPS)
                self.assertEqual(result["status"], "unavailable")
                self.assertIn(expected, result["reason"])
                self.assertTrue(all(row["p_value"] is None for row in result["contrasts"]))
                json.dumps(result, allow_nan=False)
        aliased = x.to_numpy().copy()
        aliased[:, -1] = aliased[:, 0]
        model = SimpleNamespace(exog=aliased, data=SimpleNamespace(design_info=x.design_info))
        with patch.object(self.smf, "mixedlm", return_value=model):
            result = ca._fit_actor(rows, self.levels, self.artists, self.policy, DEPS)
        self.assertEqual(result["reason"], "rank_deficient_design")

    def test_actual_mixed_fit_and_missing_actor_keep_the_declared_global_family(self):
        policy = approved_policy(self.config, family="twenty_global")
        result = ca.planned_contrasts(synthetic_rows(self.config), self.config, policy)
        observed, missing = [result["models"][model] for model in self.models]
        self.assertEqual(observed["status"], "available", observed)
        self.assertTrue(observed["converged"])
        self.assertEqual(observed["design_columns"], 23)
        self.assertGreater(observed["random_intercept_variance"], 0)
        self.assertEqual(missing["reason"], "no_valid_mentioning_listeners")
        self.assertTrue(all(row["p_value"] is None for row in missing["contrasts"]))
        family = result["multiplicity"]["families"]["all_actors"]
        self.assertEqual((family["planned_hypotheses"], family["available_hypotheses"]), (20, 10))
        self.assertTrue(result["per_row_provenance_checked"])
        self.assertEqual(observed["input_complete_twin_pairs"], 128)
        self.assertEqual(observed["fitted_pairs_with_both_conditions"], 128)


if __name__ == "__main__":
    unittest.main()
