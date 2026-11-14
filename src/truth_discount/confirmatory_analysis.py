"""Policy-gated planned LMM contrasts; this engine does not preregister a study.

The source-bound adapter must validate actual source/profile/attempt bindings.
Available valid mentioning listeners define this conditional model estimand; it
is different from averaging matched-town truth discounts. No source is edited.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from importlib import metadata
import itertools
import math
import re
import warnings

from .contracts import clone, digest


VERSION = "truth-discount-planned-contrasts-0.1"
FACTORS = ("closeness", "authority", "reliability", "wealth", "gender", "age")
INTERACTIONS = (("closeness", "reliability"), ("authority", "reliability"),
                ("wealth", "reliability"), ("closeness", "authority"))
ATTEMPT_POLICIES = {"first_only", "latest_sensitivity"}
FAMILY_SCOPES = {"ten_per_model", "twenty_global"}
FORMULA = ("belief ~ truth * (" + " + ".join(f"C({name})" for name in FACTORS)
           + " + " + " + ".join(f"C({a}):C({b})" for a, b in INTERACTIONS)
           + ") + C(real_artist)")
CONTRASTS = (
    ("closeness", ("closeness",)), ("authority", ("authority",)),
    ("wealth", ("wealth",)), ("reliability", ("reliability",)),
    ("closeness_by_reliability", INTERACTIONS[0]),
    ("authority_by_reliability", INTERACTIONS[1]),
    ("wealth_by_reliability", INTERACTIONS[2]),
    ("closeness_by_authority", INTERACTIONS[3]),
    ("gender", ("gender",)), ("age", ("age",)),
)
_HASH = re.compile(r"[0-9a-f]{64}\Z")


def _binding(value, name):
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise ValueError(name + " must be a nonempty SHA-256 binding")
    return value


def _design(config):
    if config.get("meta", {}).get("module") != "main":
        raise ValueError("planned confirmatory contrasts require the main factorial configuration")
    configured = config.get("factorial_levels", {})
    levels = {name: list(configured.get(name, [])) for name in FACTORS[:4]}
    identities = configured.get("identity", [])
    if not identities or any(not isinstance(value, str) or "_" not in value for value in identities):
        raise ValueError("main configuration needs explicit identity levels")
    levels["gender"] = list(dict.fromkeys(value.partition("_")[0] for value in identities))
    levels["age"] = list(dict.fromkeys(value.partition("_")[2] for value in identities))
    if (any(len(values) != 2 or len(set(values)) != 2
            or any(not isinstance(value, str) or not value for value in values)
            for values in levels.values())
            or set(identities) != {f"{gender}_{age}" for gender in levels["gender"] for age in levels["age"]}):
        raise ValueError("planned contrasts require six binary factors with a complete identity crossing")
    models = [model["key"] for model in config["models"]["agent_models"]]
    artists = list(config["artists"]["artist_pool"])
    if len(models) != 2 or len(set(models)) != 2 or len(artists) != 2 or len(set(artists)) != 2:
        raise ValueError("the planned ten/twenty-test families require two actors and two artists")
    return levels, models, artists


def analysis_policy_template(config, judge_profile_sha256: str, source_sha256: str,
                             attempt_policy="first_only") -> dict:
    """Return a concrete proposal with unresolved choices and no approval."""
    _binding(judge_profile_sha256, "judge_profile_sha256")
    _binding(source_sha256, "source_sha256")
    if attempt_policy not in ATTEMPT_POLICIES:
        raise ValueError("unknown analysis attempt policy")
    levels, models, artists = _design(config)
    return {"version": VERSION, "approved": False,
        "unresolved_policy": ["approve conditional listener estimand and town-only dependence model",
                              "choose ten_per_model or twenty_global multiplicity family",
                              "approve two-sided contrasts, directions and uniform marginal grid",
                              "approve first-only versus separately reported repaired sensitivity",
                              "approve exclusions and retained generation-failure reporting",
                              "record analysis freeze before access to main outcomes"],
        "config_sha256": digest(config), "judge_profile_sha256": judge_profile_sha256,
        "source_sha256": source_sha256, "attempt_policy": attempt_policy,
        "factor_levels": levels, "actor_model_keys": models, "real_artist_levels": artists,
        "formula": FORMULA, "random_intercept_group": "run_id",
        "estimand": "available_valid_mentioning_listener_conditional_model",
        "marginal_grid": "uniform_64_factor_cells_and_two_configured_artists_fixed_effects_only",
        "contrast_direction": "config_level_0_minus_level_1; interactions_difference_of_these_differences",
        "contrasts": [{"id": name, "factors": list(factors)} for name, factors in CONTRASTS],
        "fit": {"method": "reml", "optimizer": "lbfgs", "covariance": "model_based_fixed_effects",
                "test": "two_sided_wald_normal", "singular_variance_threshold": 1e-10},
        "confidence_level": 0.95,
        "multiplicity": {"method": "holm", "family_scope": "ten_per_model", "alpha": 0.05,
                         "planned_per_model": 10, "planned_total": 20,
                         "unavailable_tests": "retain_planned_family_size_keep_p_null"},
        "missing_policy": {"invalid_or_missing": "exclude_remain_missing",
                           "valid_not_mentioned": "exclude_from_conditional_model",
                           "generation_failures": "retain_report_no_automatic_regeneration",
                           "paired_town_td": "separate_matched_truth_rumor_town_estimator"},
        "dependence_limitation": "Town intercepts do not model dependence between matched twins.",
        "approval_is_not_preregistration_or_outcome_access_authority": True}


def validate_policy(policy, config, profile_sha256, source_sha256, attempt_policy):
    """Block inference until a complete explicit policy matches actual bindings."""
    expected = analysis_policy_template(config, profile_sha256, source_sha256, attempt_policy)
    if not isinstance(policy, dict) or set(policy) != set(expected):
        raise ValueError("analysis policy has missing or unsupported fields")
    if policy["approved"] is not True or policy["unresolved_policy"] != []:
        raise ValueError("analysis policy is unapproved or has unresolved choices")
    family = policy.get("multiplicity", {}).get("family_scope")
    if family not in FAMILY_SCOPES:
        raise ValueError("choose an explicit ten_per_model or twenty_global family")
    expected["approved"], expected["unresolved_policy"] = True, []
    expected["multiplicity"]["family_scope"] = family
    for key, value in expected.items():
        if policy[key] != value:
            raise ValueError("analysis policy differs from the supported configuration/binding: " + key)
    return clone(policy)


def _validated_rows(listeners, config, policy):
    levels, models, artists = _design(config)
    if not isinstance(listeners, list):
        raise ValueError("listeners must be an explicit list of source-bound rows")
    bindings = {"judge_profile_sha256": policy["judge_profile_sha256"],
                "judging_source_sha256": policy["source_sha256"],
                "analysis_attempt_policy": policy["attempt_policy"]}
    use_provenance = any(any(key in row for key in bindings) for row in listeners if isinstance(row, dict))
    by_model = {model: [] for model in models}
    seen, towns, pair_towns, pair_values = set(), {}, {}, {}
    required = {"model_key", "run_id", "pair_id", "seat_id", "truth", "real_artist",
                "judgment_status", "mentioned", "belief", *FACTORS}
    for row in listeners:
        if not isinstance(row, dict) or not required <= set(row):
            raise ValueError("listener row lacks required analysis fields")
        if row["model_key"] not in by_model or any(row[name] not in levels[name] for name in FACTORS):
            raise ValueError("listener actor or factor level differs from the policy")
        if row["real_artist"] not in artists or type(row["truth"]) is not int or row["truth"] not in (0, 1):
            raise ValueError("listener truth/artist differs from the policy")
        if (any(not isinstance(row[key], str) or not row[key] for key in ("run_id", "pair_id"))
                or type(row["seat_id"]) is not int or not 1 <= row["seat_id"] <= 12):
            raise ValueError("listener town, pair or seat identity is invalid")
        identity = row["run_id"], row["seat_id"]
        if identity in seen:
            raise ValueError("duplicate source listener identity")
        seen.add(identity)
        if use_provenance and any(row.get(key) != value for key, value in bindings.items()):
            raise ValueError("listener provenance differs from the approved analysis policy")
        town_values = tuple(row[key] for key in ("model_key", "pair_id", "truth", "real_artist", *FACTORS))
        if row["run_id"] in towns and towns[row["run_id"]] != town_values:
            raise ValueError("listener rows disagree on their town metadata")
        towns[row["run_id"]] = town_values
        pair_key = row["model_key"], row["pair_id"]
        pair_condition = (*pair_key, row["truth"])
        if pair_condition in pair_towns and pair_towns[pair_condition] != row["run_id"]:
            raise ValueError("duplicate truth condition in a matched pair")
        pair_towns[pair_condition] = row["run_id"]
        match_values = tuple(row[key] for key in ("real_artist", *FACTORS))
        if pair_key in pair_values and pair_values[pair_key] != match_values:
            raise ValueError("matched twins have inconsistent factor/artist metadata")
        pair_values[pair_key] = match_values
        status, mentioned, belief = row["judgment_status"], row["mentioned"], row["belief"]
        if not isinstance(status, str) or not status:
            raise ValueError("listener judgment status must be explicit")
        if status == "valid":
            if type(mentioned) is not int or mentioned not in (0, 1):
                raise ValueError("valid listener needs explicit mention status")
            if mentioned == 0 and belief is not None:
                raise ValueError("valid omission cannot be given a conditional belief score")
            if mentioned == 1 and (isinstance(belief, bool) or not isinstance(belief, (int, float))
                                   or not math.isfinite(belief) or belief not in (0, 0.5, 1)):
                raise ValueError("valid mentioning listener needs the declared numerical belief score")
        elif belief is not None or mentioned is not None:
            raise ValueError("invalid/missing judgments must remain missing")
        by_model[row["model_key"]].append(clone(row))
    return by_model, use_provenance


def _dependencies():
    import numpy as np
    import pandas as pd
    import patsy
    from scipy.stats import norm
    import statsmodels.formula.api as smf
    return np, pd, patsy, norm, smf


def _categorical(frame, levels, artists, pd):
    frame = frame.copy()
    for name, values in {**levels, "real_artist": artists}.items():
        frame[name] = pd.Categorical(frame[name], categories=values, ordered=True)
    return frame


def _grid(levels, artists, pd):
    rows = [{**dict(zip(FACTORS, values)), "real_artist": artist, "truth": truth}
            for values in itertools.product(*(levels[name] for name in FACTORS))
            for artist in artists for truth in (0, 1)]
    return _categorical(pd.DataFrame(rows), levels, artists, pd)


def _contrast_vectors(design_info, levels, artists, deps):
    np, pd, patsy, _, _ = deps
    grid = _grid(levels, artists, pd)
    matrix = np.asarray(patsy.build_design_matrices([design_info], grid)[0], dtype=float)
    vectors = {}
    for name, factors in CONTRASTS:
        sign = np.where(grid["truth"].to_numpy() == 1, 1.0, -1.0)
        for factor in factors:
            sign *= np.where(grid[factor].to_numpy() == levels[factor][0], 1.0, -1.0)
        # Average over only the remaining factor/artist grid; differencing
        # dimensions (truth and the selected one/two factors) are summed.
        denominator = len(grid) / (2 ** (len(factors) + 1))
        vectors[name] = sign @ matrix / denominator
    return vectors


def _unavailable_contrasts(reason):
    return [{"id": name, "factors": list(factors), "status": "unavailable",
             "reason": reason, "estimate": None, "se": None, "z": None,
             "p_value": None, "ci_low": None, "ci_high": None}
            for name, factors in CONTRASTS]


def _linear_contrasts(beta, covariance, design_info, levels, artists, policy, deps):
    np, _, _, norm, _ = deps
    vectors = _contrast_vectors(design_info, levels, artists, deps)
    rows = _unavailable_contrasts("not_computed")
    for row in rows:
        vector = vectors[row["id"]]
        estimate = float(vector @ beta)
        variance = float(vector @ covariance @ vector)
        if not math.isfinite(estimate) or not math.isfinite(variance):
            row["reason"] = "nonfinite_contrast"
        elif variance <= 0:
            row["reason"] = "zero_or_negative_contrast_variance"
        else:
            se = math.sqrt(variance)
            z = estimate / se
            critical = float(norm.ppf((1 + policy["confidence_level"]) / 2))
            p_value = float(2 * norm.sf(abs(z)))
            ci_low, ci_high = estimate - critical * se, estimate + critical * se
            if not all(math.isfinite(value) for value in (se, z, p_value, ci_low, ci_high)):
                row["reason"] = "nonfinite_contrast"
                continue
            row.update(status="available", reason=None, estimate=estimate, se=se, z=z,
                       p_value=p_value, ci_low=ci_low, ci_high=ci_high)
    return rows


def _fit_actor(rows, levels, artists, policy, deps):
    np, pd, patsy, _, smf = deps
    entry = {"status": "unavailable", "reason": None,
             "contrasts": _unavailable_contrasts("no_valid_mentioning_listeners"), "warnings": []}
    if not rows:
        entry["reason"] = "no_valid_mentioning_listeners"
        return entry
    data = _categorical(pd.DataFrame(rows), levels, artists, pd)
    if data["run_id"].nunique() < 2:
        entry["reason"] = "insufficient_towns"
        entry["contrasts"] = _unavailable_contrasts(entry["reason"])
        return entry
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            # Keep a version-independent Patsy design for marginal predictions.
            # statsmodels 0.15 stores model_spec instead of data.design_info.
            _, fixed_design = patsy.dmatrices(FORMULA, data, return_type="dataframe")
            model = smf.mixedlm(FORMULA, data, groups=data["run_id"])
            rank = int(np.linalg.matrix_rank(model.exog))
            entry.update(design_rank=rank, design_columns=int(model.exog.shape[1]))
            if rank != model.exog.shape[1]:
                entry["reason"] = "rank_deficient_design"
            elif (model.exog_names != list(fixed_design.columns)
                  or model.exog.shape != fixed_design.shape
                  or not np.allclose(model.exog, fixed_design.to_numpy())):
                entry["reason"] = "fitted_and_marginal_design_mismatch"
            else:
                fit = model.fit(reml=True, method=policy["fit"]["optimizer"])
                entry["converged"] = bool(fit.converged)
                if not fit.converged:
                    entry["reason"] = "nonconverged"
                else:
                    random_variance = np.asarray(fit.cov_re, dtype=float)
                    beta = np.asarray(fit.fe_params, dtype=float)
                    covariance = np.asarray(fit.cov_params().loc[fit.fe_params.index, fit.fe_params.index], dtype=float)
                    observed_variance, residual_variance = float(random_variance[0, 0]), float(fit.scale)
                    entry["random_intercept_variance"] = observed_variance if math.isfinite(observed_variance) else None
                    entry["residual_variance"] = residual_variance if math.isfinite(residual_variance) else None
                    if (not np.isfinite(beta).all() or not np.isfinite(covariance).all()
                            or not np.isfinite(random_variance).all() or not math.isfinite(float(fit.scale))):
                        entry["reason"] = "nonfinite_fit"
                    elif (float(np.linalg.eigvalsh(random_variance).min()) <= policy["fit"]["singular_variance_threshold"]
                          or float(fit.scale) <= 0):
                        entry["reason"] = "singular_random_or_residual_covariance"
                    elif (not np.allclose(covariance, covariance.T)
                          or float(np.linalg.eigvalsh(covariance).min()) <= 0):
                        entry["reason"] = "singular_or_indefinite_fixed_effect_covariance"
                    else:
                        entry["contrasts"] = _linear_contrasts(beta, covariance,
                            fixed_design.design_info, levels, artists, policy, deps)
                        entry["status"] = "available" if all(r["status"] == "available" for r in entry["contrasts"]) else "partly_unavailable"
        except Exception as error:
            entry["reason"] = "fit_failure"
            entry["error"] = type(error).__name__ + ": " + str(error)[:300]
        entry["warnings"] = sorted({str(warning.message)[:300] for warning in caught})
    if entry["status"] == "unavailable":
        entry["contrasts"] = _unavailable_contrasts(entry["reason"] or "fit_unavailable")
    return entry


def _holm(rows, planned_size, alpha):
    """Keep the full planned family even when some tests are unavailable."""
    if len(rows) != planned_size:
        raise ValueError("Holm family must retain every planned hypothesis")
    observed = [(index, row["p_value"]) for index, row in enumerate(rows) if row["p_value"] is not None]
    if any(not math.isfinite(p) or not 0 <= p <= 1 for _, p in observed):
        raise ValueError("invalid raw p value")
    for row in rows:
        row.update(holm_adjusted_p=None, reject_null=None, holm_planned_family_size=planned_size)
    previous = 0.0
    for rank, (index, p_value) in enumerate(sorted(observed, key=lambda item: (item[1], item[0]))):
        previous = min(1.0, max(previous, (planned_size - rank) * p_value))
        rows[index].update(holm_adjusted_p=previous, reject_null=previous <= alpha)
    return {"planned_hypotheses": planned_size, "available_hypotheses": len(observed),
            "complete_family": len(observed) == planned_size, "method": "holm", "alpha": alpha}


def planned_contrasts(listeners, config, policy) -> dict:
    """Fit only an explicitly approved policy, retaining all ten tests per actor."""
    if not isinstance(policy, dict):
        raise ValueError("explicit analysis policy is required")
    policy = validate_policy(policy, config, policy.get("judge_profile_sha256"),
                             policy.get("source_sha256"), policy.get("attempt_policy"))
    by_model, provenance = _validated_rows(listeners, config, policy)
    levels, models, artists = _design(config)
    try:
        deps = _dependencies()
        missing_dependency = None
    except ImportError as error:
        deps, missing_dependency = None, str(error)
    result = {"version": VERSION, "policy_sha256": digest(policy), "policy": policy,
              "analysis_status": "approved_policy_offline_engine_not_proof_of_preregistration",
              "attempt_policy": policy["attempt_policy"], "formula": FORMULA,
              "estimand": policy["estimand"], "dependence_limitation": policy["dependence_limitation"],
              "paired_town_truth_discount_is_separate": True,
              "source_binding_validated_by_adapter_required": True,
              "per_row_provenance_checked": provenance,
              "confidence_intervals_multiplicity_adjusted": False,
              "models": {}, "multiplicity": {"family_scope": policy["multiplicity"]["family_scope"], "families": {}}}
    for model in models:
        all_rows = by_model[model]
        rows = [row for row in all_rows if row["judgment_status"] == "valid" and row["mentioned"] == 1]
        entry = (_fit_actor(rows, levels, artists, policy, deps) if deps is not None else
                 {"status": "unavailable", "reason": "dependencies_missing", "error": missing_dependency,
                  "contrasts": _unavailable_contrasts("dependencies_missing"), "warnings": []})
        pair_truths = defaultdict(set)
        for row in all_rows:
            pair_truths[row["pair_id"]].add(row["truth"])
        fit_pair_truths = defaultdict(set)
        for row in rows:
            fit_pair_truths[row["pair_id"]].add(row["truth"])
        entry.update(input_listeners=len(all_rows), fitted_listeners=len(rows),
                     valid_omissions=sum(row["judgment_status"] == "valid" and row["mentioned"] == 0 for row in all_rows),
                     excluded_invalid_or_missing=dict(Counter(row["judgment_status"] for row in all_rows if row["judgment_status"] != "valid")),
                     input_towns=len({row["run_id"] for row in all_rows}),
                     fitted_towns=len({row["run_id"] for row in rows}),
                     input_complete_twin_pairs=sum(values == {0, 1} for values in pair_truths.values()),
                     fitted_pairs_with_both_conditions=sum(values == {0, 1} for values in fit_pair_truths.values()),
                     fitted_pairs_with_one_condition=sum(len(values) == 1 for values in fit_pair_truths.values()))
        result["models"][model] = entry
    alpha = policy["multiplicity"]["alpha"]
    if policy["multiplicity"]["family_scope"] == "ten_per_model":
        for model in models:
            result["multiplicity"]["families"][model] = _holm(result["models"][model]["contrasts"], 10, alpha)
    else:
        rows = [row for model in models for row in result["models"][model]["contrasts"]]
        result["multiplicity"]["families"]["all_actors"] = _holm(rows, 20, alpha)
    result["status"] = "available" if all(entry["status"] == "available" for entry in result["models"].values()) else "partly_or_wholly_unavailable"
    result["dependency_versions"] = {}
    for name in ("numpy", "pandas", "patsy", "scipy", "statsmodels"):
        try:
            result["dependency_versions"][name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            result["dependency_versions"][name] = None
    return result
