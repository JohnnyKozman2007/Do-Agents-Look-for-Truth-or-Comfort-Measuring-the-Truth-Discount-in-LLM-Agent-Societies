"""Pilot and main-study analysis: truth discount per cell and per knob, bounds and model fits.

Only towns that pass the full replay audit and completed are analyzed. The twin
pair (one truth twin and one rumor town on the same seed) is the unit for
confidence intervals; the mixed-effects model groups listeners by town as the
specification requires. statsmodels and matplotlib are optional: without them
the descriptive tables are still written and the model/plot are marked not run.
"""
from __future__ import annotations

import csv
from collections import defaultdict
import hashlib
from importlib import metadata as package_metadata
import io
import json
import math
from pathlib import Path
import random
import sys
import warnings
from typing import Any

from .artifacts import audit_town
from .config import load_config, study_cells
from .contracts import digest
from .runner import concert_mentioned

BOOTSTRAP_RESAMPLES = 5000
BOOTSTRAP_SEED = 20261120
_PAIR_OUTCOMES = ("truth_discount", "sensitivity_lower_difference", "sensitivity_neutral_difference",
                  "omission_rate_difference")
FACTORS = ("closeness", "authority", "reliability", "wealth", "gender", "age")
_TOWN_OUTCOMES = ("belief_mean", "sensitivity_lower", "sensitivity_neutral", "omission_rate",
                  "go_rate_first_hand", "go_rate_second_hand", "transmission_rate",
                  "evidence_transmission_rate")
_PAIR_TOWN_FIELDS = {"belief_mean": "truth_discount", "sensitivity_lower": "sensitivity_lower_difference",
                     "sensitivity_neutral": "sensitivity_neutral_difference",
                     "omission_rate": "omission_rate_difference"}
MEASUREMENT_LIMITS = {
    "transmission": "Concert/artist keyword diagnostic in first-hand dialogue, not human-adjudicated rumor transmission.",
    "evidence_transmission": "Checked-plus-keyword or legacy literal-text diagnostic, not semantic proof of evidence transfer.",
    "missingness": "Only valid NOT_MENTIONED labels receive the declared 0/0.5 sensitivity values; invalid and unobserved judgments remain missing.",
    "pilot_cells": "The four pilot cells bundle several factors and cannot identify six separate causal factor effects.",
    "intervals": "Descriptive percentile bootstrap over observed twin pairs, with no multiplicity adjustment or guaranteed small-sample coverage.",
    "models": "Town random intercepts do not model within-twin dependence. Models use available valid mentioning listeners, which can differ from the complete-pair population. Pair-clustered OLS is a sensitivity analysis, not an adopted final model.",
}


def load_towns(output_root: Path) -> tuple[list[dict], dict, dict]:
    """Audit every saved town; return completed towns, their config and exclusions."""
    root = Path(output_root)
    directories = sorted(p for p in root.iterdir() if p.is_dir() and p.name != "_incomplete")
    if any(not (directory / "manifest.json").is_file() for directory in directories):
        raise ValueError("saved town directory lacks a manifest; wait for collection or inspect the incomplete output")
    paths = directories
    if not paths:
        raise ValueError("no saved towns found")
    towns, all_towns, excluded = [], [], defaultdict(int)
    for path in paths:
        town = audit_town(path)
        all_towns.append(town)
        if town["run_status"] == "completed":
            towns.append(town)
        else:
            excluded[town["run_status"]] += 1
    if not towns:
        raise ValueError("no completed towns to analyze")
    if len({t["evidence_kind"] for t in all_towns}) != 1:
        raise ValueError("cannot pool fixture, mocked-provider and development-pilot evidence")
    if len({t["config_sha256"] for t in all_towns}) != 1:
        raise ValueError("towns were collected with different configurations")
    if len({t.get("execution_manifest_sha256") for t in all_towns}) != 1:
        raise ValueError("towns were collected with different provider manifests")
    if len({t["run_id"] for t in all_towns}) != len(all_towns):
        raise ValueError("duplicate town identity in analysis input")
    config = load_config(Path(output_root) / towns[0]["run_id"] / "config.json")
    return towns, config, dict(excluded)


def factor_levels(knobs: dict) -> dict:
    """The six specification factors; the config's identity knob holds gender and age."""
    gender, _, age = knobs["identity"].partition("_")
    return {"closeness": knobs["closeness"], "authority": knobs["authority"],
            "reliability": knobs["reliability"], "wealth": knobs["wealth"], "gender": gender, "age": age}


def _town_values(town: dict, config: dict) -> dict:
    artists = config["artists"]["artist_pool"]
    told = [any(line["seat_id"] == pair["first_hand_seat"] and not line.get("scripted")
                and concert_mentioned(line["text"], artists) for line in pair["lines"])
            for pair in town["scene_3_catch_up_transcripts"]]
    checkers = [row for row in town["scene_3_poster_evidence_passed"] if row["partner_checked"]]
    metrics = town["metrics"]
    return {**{k: metrics.get(k) for k in _TOWN_OUTCOMES[:6]},
            "transmission_rate": sum(told) / len(told) if told else None,
            "evidence_transmission_rate": (sum(r.get("evidence_passed", r.get("literal_poster_quote_found", False))
                                               for r in checkers) / len(checkers)
                                           if checkers else None)}


def listener_rows(towns: list[dict], config: dict) -> list[dict]:
    """One row per expected listener, preserving missing/invalid versus silence."""
    mapping = config["judging_and_scoring"]["belief_numerical_mapping"]
    first = set(config["seating_and_pairing"]["first_hand_seats"])
    rows = []
    for town in towns:
        decisions = {d["seat_id"]: d["decision"] for d in
                     town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]}
        evaluations = defaultdict(list)
        for evaluation in town["judge_evaluations"]:
            evaluations[evaluation["seat_id"]].append(evaluation)
        seats = sorted(first | set(config["seating_and_pairing"]["second_hand_seats"]))
        for seat in seats:
            entries = evaluations[seat]
            evaluation = entries[0] if len(entries) == 1 else {}
            label = evaluation.get("label")
            valid = evaluation.get("status") == "valid" and (label in mapping or label == "NOT_MENTIONED")
            status = ("valid" if valid else "missing" if not entries else
                      "duplicate" if len(entries) > 1 else "invalid")
            rows.append({"run_id": town["run_id"], "pair_id": town["pair_id"], "model_key": town["model_key"],
                         "cell_id": town["cell_id"], "condition_type": town["condition_type"],
                         "truth": int(town["condition_type"] == "truth_twin"),
                         "layout_id": town["layout_id"], "repetition_id": town["repetition_id"],
                         "real_artist": town["real_artist"], **factor_levels(town["knobs"]), "seat_id": seat,
                         "layer": "first_hand" if seat in first else "second_hand",
                         "judgment_status": status,
                         "label": label if valid else None,
                         "belief": mapping.get(label) if valid else None,
                         "mentioned": int(label != "NOT_MENTIONED") if valid else None,
                         "decision": decisions.get(seat)})
    return rows


def pair_rows(towns: list[dict], config: dict) -> list[dict]:
    """Match twins before differencing; invalid judgments never become silence."""
    if len({t["run_id"] for t in towns}) != len(towns):
        raise ValueError("duplicate town identity in pair input")
    grouped = defaultdict(list)
    for town in towns:
        grouped[(town["model_key"], town["pair_id"])].append(town)
    rows = []
    shared = ("cell_id", "seed_id", "layout_id", "repetition_id", "real_artist", "fake_artist",
              "source_persona_id", "seating_assignment", "knobs", "catch_up_pairs", "config_sha256",
              "evidence_kind", "execution_manifest_sha256")
    for (model, pair_id), members in sorted(grouped.items()):
        if len(members) > 2 or len({t["condition_type"] for t in members}) != len(members):
            raise ValueError("duplicate or invalid twin condition: " + pair_id)
        if len(members) != 2:
            continue
        by_condition = {town["condition_type"]: town for town in members}
        if set(by_condition) != {"truth_twin", "rumor"}:
            raise ValueError("pair requires rumor and truth_twin: " + pair_id)
        truth, rumor = by_condition["truth_twin"], by_condition["rumor"]
        if any(digest(truth.get(key)) != digest(rumor.get(key)) for key in shared):
            raise ValueError("twins have different matching metadata: " + pair_id)
        tv, rv = _town_values(truth, config), _town_values(rumor, config)
        row = {"model_key": model, "pair_id": pair_id, "cell_id": truth["cell_id"],
               "truth_run_id": truth["run_id"], "rumor_run_id": rumor["run_id"],
               "layout_id": truth["layout_id"], "repetition_id": truth["repetition_id"],
               "judgments_complete": all(t["metrics"]["status"] == "complete" for t in members),
               "real_artist": truth["real_artist"], **factor_levels(truth["knobs"]),
               **{output: tv[key] - rv[key] if tv[key] is not None and rv[key] is not None else None
                  for key, output in _PAIR_TOWN_FIELDS.items()}}
        for key in _TOWN_OUTCOMES:
            row[key + "_truth"], row[key + "_rumor"] = tv[key], rv[key]
        row["conditional_belief_status"] = ("available" if row["truth_discount"] is not None else
                                             "undefined_all_omitted" if row["judgments_complete"] else
                                             "invalid_or_missing_judgments")
        rows.append(row)
    return rows


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bootstrap_ci(values: list[float], *, resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED,
                 level: float = 0.95) -> tuple[float, float] | tuple[None, None]:
    """Percentile interval for a mean, resampling independent pairs."""
    if (type(resamples) is not int or resamples < 1 or type(level) not in (int, float)
            or not math.isfinite(level) or not 0 < level < 1
            or any(type(value) not in (int, float) or not math.isfinite(value) for value in values)):
        raise ValueError("bootstrap needs finite values, positive resamples and a level strictly between zero and one")
    if len(values) < 2:
        return None, None
    rng, n = random.Random(seed), len(values)
    means = sorted(sum(rng.choice(values) for _ in range(n)) / n for _ in range(resamples))
    tail = (1 - level) / 2
    return means[int(tail * resamples)], means[min(resamples - 1, int((1 - tail) * resamples))]


def _difference_ci(a: list[float], b: list[float], seed: int) -> tuple[float, float] | tuple[None, None]:
    if len(a) < 2 or len(b) < 2:
        return None, None
    rng = random.Random(seed)
    diffs = sorted(sum(rng.choice(a) for _ in a) / len(a) - sum(rng.choice(b) for _ in b) / len(b)
                   for _ in range(BOOTSTRAP_RESAMPLES))
    return diffs[int(.025 * BOOTSTRAP_RESAMPLES)], diffs[int(.975 * BOOTSTRAP_RESAMPLES)]


def _present(rows: list[dict], key: str) -> list[float]:
    return [r[key] for r in rows if r[key] is not None]


def _interval_status(values: list[float]) -> str:
    return ("insufficient_pairs" if len(values) < 2 else
            "degenerate_constant_pairs" if len(set(values)) == 1 else "descriptive_percentile")


def cell_summary(pairs: list[dict], config: dict) -> list[dict]:
    names = {c["cell_id"]: c["name"] for c in study_cells(config)}
    grouped = defaultdict(list)
    for row in pairs:
        grouped[(row["model_key"], row["cell_id"])].append(row)
    result = []
    for (model, cell), rows in sorted(grouped.items()):
        summary = {"model_key": model, "cell_id": cell, "cell_name": names.get(cell), "n_pairs": len(rows)}
        for index, key in enumerate(_PAIR_OUTCOMES):
            values = _present(rows, key)
            low, high = bootstrap_ci(values, seed=BOOTSTRAP_SEED + index)
            summary.update({key: _mean(values), key + "_ci_low": low, key + "_ci_high": high,
                            key + "_n": len(values), key + "_n_missing": len(rows) - len(values),
                            key + "_interval_status": _interval_status(values)})
        for key in _TOWN_OUTCOMES:
            for twin in ("truth", "rumor"):
                summary[f"{key}_{twin}"] = _mean(_present(rows, f"{key}_{twin}"))
                summary[f"{key}_{twin}_n"] = len(_present(rows, f"{key}_{twin}"))
        result.append(summary)
    return result


def condition_summary(towns: list[dict], config: dict) -> list[dict]:
    """Observed denominators for each condition, including unmatched complete towns."""
    grouped = defaultdict(list)
    for town in towns:
        grouped[(town["model_key"], town["cell_id"], town["condition_type"])].append(town)
    result = []
    for (model, cell, condition), members in sorted(grouped.items()):
        listeners = listener_rows(members, config)
        valid = [row for row in listeners if row["judgment_status"] == "valid"]
        omitted = sum(row["label"] == "NOT_MENTIONED" for row in valid)
        row = {"model_key": model, "cell_id": cell, "condition_type": condition,
               "n_towns": len(members), "expected_listener_count": len(listeners),
               "valid_judgment_count": len(valid),
               "missing_judgment_count": sum(item["judgment_status"] == "missing" for item in listeners),
               "invalid_judgment_count": sum(item["judgment_status"] in {"invalid", "duplicate"} for item in listeners),
               "not_mentioned_count": omitted, "mentioned_count": len(valid) - omitted,
               "omission_rate": omitted / len(listeners) if listeners and len(valid) == len(listeners) else None,
               "omission_rate_among_valid": omitted / len(valid) if valid else None,
               "n_towns_with_complete_judgments": sum(t["metrics"]["status"] == "complete" for t in members)}
        for key in ("belief_mean", "sensitivity_lower", "sensitivity_neutral"):
            values = [t["metrics"].get(key) for t in members if t["metrics"].get(key) is not None]
            row[key] = _mean(values)
            row[key + "_n_towns"] = len(values)
        for layer in ("first_hand", "second_hand"):
            seats = set(config["seating_and_pairing"][layer + "_seats"])
            expected = len(members) * len(seats)
            observed, missing, fallback, go = 0, 0, 0, 0
            for town in members:
                decisions = defaultdict(list)
                for decision in town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]:
                    if decision["seat_id"] in seats:
                        decisions[decision["seat_id"]].append(decision)
                for seat in seats:
                    items = decisions[seat]
                    if not items:
                        missing += 1
                    if len(items) != 1:
                        continue
                    item = items[0]
                    is_fallback = item.get("parse_status") == "malformed_fallback_skip" and item.get("decision") == "SKIP"
                    if item.get("layer") == layer and ((item.get("parse_status") == "valid"
                                                       and item.get("decision") in {"GO", "SKIP"}) or is_fallback):
                        observed += 1
                        fallback += int(is_fallback)
                        go += int(item["decision"] == "GO")
            prefix = "go_" + layer
            row.update({prefix + "_count": go, prefix + "_expected_denominator": expected,
                        prefix + "_observed_denominator": observed, prefix + "_missing_count": missing,
                        prefix + "_invalid_count": expected - observed - missing,
                        prefix + "_fallback_skip_count": fallback,
                        "go_rate_" + layer: go / expected if expected and observed == expected else None,
                        "go_rate_" + layer + "_among_observed": go / observed if observed else None})
        pairs = [pair for town in members for pair in town["scene_3_catch_up_transcripts"]]
        told = sum(any(line["seat_id"] == pair["first_hand_seat"] and not line.get("scripted")
                       and concert_mentioned(line["text"], config["artists"]["artist_pool"])
                       for line in pair["lines"]) for pair in pairs)
        checkers = [item for town in members for item in town["scene_3_poster_evidence_passed"]
                    if item["partner_checked"]]
        passed = sum(item.get("evidence_passed", item.get("literal_poster_quote_found", False)) for item in checkers)
        row.update(transmission_keyword_count=told, transmission_observed_denominator=len(pairs),
                   transmission_keyword_rate=told / len(pairs) if pairs else None,
                   evidence_keyword_count=passed, evidence_checker_denominator=len(checkers),
                   evidence_keyword_rate=passed / len(checkers) if checkers else None,
                   transmission_status="keyword_diagnostic_not_human_adjudicated")
        result.append(row)
    return result


def contrasts(pairs: list[dict], reference: int = 2) -> list[dict]:
    """Each pilot cell's truth discount minus the Maximum Skepticism cell's."""
    grouped = defaultdict(list)
    for row in pairs:
        grouped[(row["model_key"], row["cell_id"])].append(row)
    result = []
    for model in sorted({m for m, _ in grouped}):
        base_rows = grouped.get((model, reference), [])
        base = _present(base_rows, "truth_discount")
        for cell in sorted(c for m, c in grouped if m == model and c != reference):
            members = grouped[(model, cell)]
            values = _present(members, "truth_discount")
            low, high = _difference_ci(values, base, BOOTSTRAP_SEED + cell)
            result.append({"model_key": model, "cell_id": cell, "reference_cell_id": reference,
                           "difference": _mean(values) - _mean(base) if values and base else None,
                           "ci_low": low, "ci_high": high, "n_pairs": len(values), "n_reference_pairs": len(base),
                           "n_missing_pairs": len(members) - len(values),
                           "n_missing_reference_pairs": len(base_rows) - len(base),
                           "interval_status": ("insufficient_pairs" if len(values) < 2 or len(base) < 2 else
                                               "degenerate_constant_cells" if len(set(values)) == len(set(base)) == 1 else
                                               "descriptive_percentile"),
                           "comparison_scope": "bundled_pilot_cells", "confirmatory": False,
                           "bootstrap_unit": "independent_twin_pairs_within_each_cell",
                           "multiplicity_adjusted": False})
    return result


def factor_order(config: dict) -> dict[str, list[str]]:
    """Level order for each factor, from the main config's factorial_levels (A minus B)."""
    levels = config["factorial_levels"]
    split = [level.partition("_") for level in levels["identity"]]
    return {**{k: levels[k] for k in FACTORS[:4]},
            "gender": list(dict.fromkeys(g for g, _, _ in split)), "age": list(dict.fromkeys(a for _, _, a in split))}


def knob_summary(pairs: list[dict], config: dict) -> list[dict]:
    """Main study: truth discount at each level of each factor, and the level difference."""
    order = factor_order(config)
    result = []
    for model in sorted({row["model_key"] for row in pairs}):
        rows = [row for row in pairs if row["model_key"] == model]
        for index, factor in enumerate(FACTORS):
            present = {row[factor] for row in rows}
            levels = [level for level in order[factor] if level in present]
            if len(levels) != 2:
                continue
            all_a, all_b = ([row for row in rows if row[factor] == level] for level in levels)
            a, b = _present(all_a, "truth_discount"), _present(all_b, "truth_discount")
            low, high = _difference_ci(a, b, BOOTSTRAP_SEED + 100 + index)
            result.append({"model_key": model, "factor": factor, "level_a": levels[0], "level_b": levels[1],
                           "truth_discount_a": _mean(a), "truth_discount_b": _mean(b),
                           "difference": _mean(a) - _mean(b) if a and b else None,
                           "ci_low": low, "ci_high": high, "n_pairs_a": len(a), "n_pairs_b": len(b),
                           "n_missing_pairs_a": len(all_a) - len(a), "n_missing_pairs_b": len(all_b) - len(b),
                           "comparison_scope": "descriptive_marginal_observed_cells", "confirmatory": False})
    return result


def mixed_models(listeners: list[dict], module: str = "pilot") -> dict:
    """Random intercept per town, fit separately for each agent model.

    Main study: belief ~ truth * (six factors) + real artist, as specified. The
    pilot's four cells fix the factors jointly, so cell indicators stand in for
    them. Town- and twin-pair-clustered OLS fits are exploratory sensitivities.
    This preserves the declared model rather than silently adopting a new
    nested random-effects specification before the team agrees the analysis.
    """
    try:
        import pandas as pd
        import numpy as np
        import statsmodels.formula.api as smf
    except ImportError:
        return {"status": "not_run", "reason": "install the analysis extra (statsmodels, pandas)",
                "inference_status": "exploratory_not_confirmatory", "specification_finalized": False}
    frame = pd.DataFrame([r for r in listeners if r["mentioned"] == 1 and r["belief"] is not None])
    formula = ("belief ~ truth * (" + " + ".join(f"C({f})" for f in FACTORS) + ") + C(real_artist)"
               if module == "main" else "belief ~ truth * C(cell_id) + C(real_artist)")
    result = {"status": "run" if len(frame) else "not_run", "formula": formula,
              "groups": "run_id (town)", "models": {}, "specification_finalized": False,
              "inference_status": "exploratory_not_confirmatory",
              "dependence_limitation": MEASUREMENT_LIMITS["models"],
              "pair_sensitivity_groups": "pair_id (matched twin pair)"}
    if not len(frame):
        result["reason"] = "no observed valid conditional belief scores"
    def finite(value):
        value = float(value)
        return value if math.isfinite(value) else None
    for model, data in frame.groupby("model_key") if len(frame) else []:
        entry = {"n_listeners": int(len(data)), "n_towns": int(data["run_id"].nunique()),
                 "n_twin_pairs": int(data["pair_id"].nunique()), "fit_failures": {}}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                design = smf.ols(formula, data)
                entry.update(design_rank=int(np.linalg.matrix_rank(design.exog)),
                             design_columns=int(design.exog.shape[1]))
                if entry["design_rank"] < entry["design_columns"]:
                    entry["fit_failures"]["design"] = "rank-deficient observed design; coefficients are not separately identifiable"
                else:
                    try:
                        fit = smf.mixedlm(formula, data, groups=data["run_id"]).fit(reml=True)
                        ci = fit.conf_int()
                        entry["mixed"] = {name: {"estimate": finite(fit.params[name]), "se": finite(fit.bse[name]),
                                                 "p": finite(fit.pvalues[name]), "ci_low": finite(ci.loc[name, 0]),
                                                 "ci_high": finite(ci.loc[name, 1])}
                                          for name in fit.params.index if name != "Group Var"}
                        entry["converged"] = bool(fit.converged)
                        entry["mixed_status"] = "converged" if fit.converged else "nonconverged_do_not_interpret"
                    except Exception as error:
                        entry["fit_failures"]["mixed"] = f"{type(error).__name__}: {error}"
                    for key, group in (("ols_town_clustered", "run_id"), ("ols_twin_pair_clustered", "pair_id")):
                        if data[group].nunique() < 2:
                            entry["fit_failures"][key] = "at least two observed clusters are required"
                            continue
                        try:
                            ols = design.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(data[group])[0]})
                            entry[key] = {name: {"estimate": finite(ols.params[name]), "se": finite(ols.bse[name]),
                                                 "p": finite(ols.pvalues[name])} for name in ols.params.index}
                        except Exception as error:
                            entry["fit_failures"][key] = f"{type(error).__name__}: {error}"
            except Exception as error:
                entry["fit_failures"]["design"] = f"{type(error).__name__}: {error}"
        entry["warnings"] = sorted({str(w.message)[:200] for w in caught})
        result["models"][model] = entry
    return result


def _csv(rows: list[dict]) -> str:
    stream = io.StringIO(newline="")
    if rows:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return stream.getvalue()


def _fmt(value: Any, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def _interval(row: dict, key: str) -> str:
    count = f" (n={row[key + '_n']}, missing={row[key + '_n_missing']})"
    if row[key] is None:
        return "—" + count
    if row[key + "_ci_low"] is None:
        return _fmt(row[key]) + count
    return f"{_fmt(row[key])} [{_fmt(row[key + '_ci_low'])}, {_fmt(row[key + '_ci_high'])}]" + count


def _knob_lines(rows: list[dict]) -> list[str]:
    lines = ["| Factor | Levels (A / B) | Truth discount A / B | A − B [95% interval] | Pairs A / B |",
             "|---|---|---|---|---|"]
    for k in rows:
        interval = "" if k["ci_low"] is None else f" [{_fmt(k['ci_low'])}, {_fmt(k['ci_high'])}]"
        lines.append(f"| {k['factor']} | {k['level_a']} / {k['level_b']} | {_fmt(k['truth_discount_a'])} / "
                     f"{_fmt(k['truth_discount_b'])} | {_fmt(k['difference'])}{interval} | "
                     f"{k['n_pairs_a']} / {k['n_pairs_b']} |")
    return lines


def _report(meta: dict, cells: list[dict], diffs: list[dict], knobs: list[dict], models: dict,
            conditions: list[dict]) -> str:
    main = meta["module"] == "main"
    lines = ["# Main-study analysis" if main else "# Pilot analysis", "",
             f"Evidence: `{meta['evidence_kind']}` (not study-eligible). Towns analyzed: {meta['towns']}; "
             f"complete twin pairs: {meta['pairs']}; excluded towns: {meta['excluded_towns'] or 'none'}.",
             "Truth discount = truth-twin belief minus rumor belief, averaged over twin pairs. "
             "Brackets are descriptive 95% percentile bootstrap intervals over observed pairs. "
             "They do not establish confirmatory significance or calibrated small-sample coverage.",
             "Each outcome shows its available-pair count and missing count. A collapsed interval can reflect constant observed pairs.",
             "Invalid or unobserved judgments stay missing. Only valid NOT_MENTIONED labels receive the sensitivity values.",
             f"Completed towns without a completed twin: {meta['unmatched_completed_towns']}. "
             f"Matched pairs with incomplete judgment metrics: {meta['pairs_with_incomplete_judgments']}.",
             "Transmission columns are keyword diagnostics, not human-adjudicated transmission.",
             MEASUREMENT_LIMITS["models"],
             "The analysis uses original saved labels. Any rejudged.jsonl overlay remains unapplied.", ""]
    if not main:
        lines += [MEASUREMENT_LIMITS["pilot_cells"], ""]
    else:
        lines += ["Factor tables are descriptive marginal summaries of the observed cells. "
                  "An incomplete or unbalanced factorial does not identify isolated factor effects.", ""]
    for model in sorted({c["model_key"] for c in cells} | {c["model_key"] for c in conditions}):
        lines += [f"## {model}", ""]
        if main:
            lines += ["Truth discount at each level of each factor, averaged over the cells with that level. "
                      "Per-cell results for every cell are in `cells.csv`.", ""]
            lines += _knob_lines([k for k in knobs if k["model_key"] == model])
        else:
            lines += ["| Cell | Pairs | Truth discount | NOT_MENTIONED = 0 | NOT_MENTIONED = 0.5 | Belief truth / rumor | "
                      "Omission truth / rumor | GO first-hand truth / rumor | GO second-hand truth / rumor | "
                      "Mention keyword (rumor) | Evidence keyword (rumor) |",
                      "|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in (c for c in cells if c["model_key"] == model and not main):
            lines.append(
                f"| {c['cell_name'] or c['cell_id']} | {c['n_pairs']} | {_interval(c, 'truth_discount')} | "
                f"{_interval(c, 'sensitivity_lower_difference')} | {_interval(c, 'sensitivity_neutral_difference')} | "
                f"{_fmt(c['belief_mean_truth'])} / {_fmt(c['belief_mean_rumor'])} | "
                f"{_fmt(c['omission_rate_truth'])} / {_fmt(c['omission_rate_rumor'])} | "
                f"{_fmt(c['go_rate_first_hand_truth'])} / {_fmt(c['go_rate_first_hand_rumor'])} | "
                f"{_fmt(c['go_rate_second_hand_truth'])} / {_fmt(c['go_rate_second_hand_rumor'])} | "
                f"{_fmt(c['transmission_rate_rumor'])} | {_fmt(c['evidence_transmission_rate_rumor'])} |")
        rows = [d for d in diffs if d["model_key"] == model]
        if rows:
            lines += ["", "Descriptive bundled-cell contrasts against Maximum Skepticism, without multiplicity adjustment:", "",
                      "| Cell | Difference | 95% interval |", "|---|---|---|"]
            for d in rows:
                interval = "—" if d["ci_low"] is None else f"[{_fmt(d['ci_low'])}, {_fmt(d['ci_high'])}]"
                lines.append(f"| {d['cell_id']} | {_fmt(d['difference'])} | {interval} |")
        lines += ["", "Condition counts include all completed towns, including unmatched twins. "
                  "GO denominators count expected listener decisions, independently of judge validity.", "",
                  "| Cell | Condition | Towns | Valid / expected judgments | Invalid / missing | NOT_MENTIONED | "
                  "GO first hand / denominator | GO second hand / denominator |",
                  "|---|---|---|---|---|---|---|---|"]
        for condition in (row for row in conditions if row["model_key"] == model):
            lines.append(f"| {condition['cell_id']} | {condition['condition_type']} | {condition['n_towns']} | "
                         f"{condition['valid_judgment_count']} / {condition['expected_listener_count']} | "
                         f"{condition['invalid_judgment_count']} / {condition['missing_judgment_count']} | "
                         f"{condition['not_mentioned_count']} | "
                         f"{condition['go_first_hand_count']} / {condition['go_first_hand_expected_denominator']} | "
                         f"{condition['go_second_hand_count']} / {condition['go_second_hand_expected_denominator']} |")
        entry = models.get("models", {}).get(model, {})
        fit = entry.get("mixed")
        if fit:
            lines += ["", f"Exploratory declared mixed model `{models['formula']}`, random intercept per town. "
                      f"Fit status: {entry.get('mixed_status', 'unverified')}. No confirmatory interpretation.", "",
                      "| Term | Estimate | SE | Exploratory p |", "|---|---|---|---|"]
            lines += [f"| `{name}` | {_fmt(v['estimate'])} | {_fmt(v['se'])} | {_fmt(v['p'], 4)} |"
                      for name, v in fit.items() if name.startswith("truth") or name == "Intercept"]
        if entry.get("fit_failures"):
            lines += ["", "Model fits unavailable: " + json.dumps(entry["fit_failures"], sort_keys=True), ""]
        lines.append("")
    if models["status"] != "run":
        lines += [f"Mixed model not run: {models['reason']}.", ""]
    return "\n".join(lines)


def _figure_evidence_label(evidence_kind: str) -> str:
    return {"synthetic_fixture": "Synthetic fixture data. Software validation only.",
            "mocked_provider": "Mocked provider responses. Software validation only.",
            "development_pilot": "Development pilot data. Descriptive and exploratory."}[evidence_kind]


def _plot(cells: list[dict], path: Path, evidence_kind: str) -> bool:
    if not cells or all(row["truth_discount"] is None for row in cells):
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    models = sorted({c["model_key"] for c in cells})
    cell_ids = sorted({c["cell_id"] for c in cells})
    figure, axis = plt.subplots(figsize=(7, 3.5))
    width = 0.8 / max(1, len(models))
    for index, model in enumerate(models):
        rows = {c["cell_id"]: c for c in cells if c["model_key"] == model}
        xs = [i + index * width for i, cell in enumerate(cell_ids) if rows.get(cell, {}).get("truth_discount") is not None]
        picked = [rows[cell] for cell in cell_ids if rows.get(cell, {}).get("truth_discount") is not None]
        heights = [r["truth_discount"] for r in picked]
        axis.bar(xs, heights, width, label=model)
        for x, row in zip(xs, picked):
            low, high = row["truth_discount_ci_low"], row["truth_discount_ci_high"]
            if low is not None and high is not None:
                axis.errorbar(x, (low + high) / 2, yerr=(high - low) / 2, fmt="none", color="black", capsize=3)
    axis.axhline(0, color="black", linewidth=0.8)
    axis.set_xticks([i + width * (len(models) - 1) / 2 for i in range(len(cell_ids))])
    axis.set_xticklabels([f"Cell {c}" for c in cell_ids])
    axis.set_ylabel("Truth discount (truth − rumor belief)")
    axis.legend(frameon=False, ncol=len(models), loc="lower center", bbox_to_anchor=(0.5, 1.0))
    figure.text(.5, .012, _figure_evidence_label(evidence_kind), ha="center", va="bottom", fontsize=8, color="#444444")
    figure.tight_layout(rect=(0, .08, 1, 1))
    figure.savefig(path, dpi=200)
    plt.close(figure)
    return True


def _plot_knobs(knobs: list[dict], path: Path, evidence_kind: str) -> bool:
    if not knobs or all(row["difference"] is None for row in knobs):
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    models = sorted({k["model_key"] for k in knobs})
    figure, axis = plt.subplots(figsize=(7, 3.8))
    height = 0.8 / max(1, len(models))
    for index, model in enumerate(models):
        rows = {k["factor"]: k for k in knobs if k["model_key"] == model and k["difference"] is not None}
        ys = [i + index * height for i, factor in enumerate(FACTORS) if factor in rows]
        picked = [rows[f] for f in FACTORS if f in rows]
        values = [r["difference"] for r in picked]
        axis.barh(ys, values, height, label=model)
        for y, row in zip(ys, picked):
            low, high = row["ci_low"], row["ci_high"]
            if low is not None and high is not None:
                axis.errorbar((low + high) / 2, y, xerr=(high - low) / 2, fmt="none", color="black", capsize=3)
    axis.axvline(0, color="black", linewidth=0.8)
    labels = {k["factor"]: f"{k['factor']}: {k['level_a']} − {k['level_b']}" for k in knobs}
    axis.set_yticks([i + height * (len(models) - 1) / 2 for i in range(len(FACTORS))])
    axis.set_yticklabels([labels.get(f, f) for f in FACTORS])
    axis.invert_yaxis()
    axis.set_xlabel("Difference in truth discount between levels")
    axis.legend(frameon=False, ncol=len(models), loc="lower center", bbox_to_anchor=(0.5, 1.0))
    figure.text(.5, .012, _figure_evidence_label(evidence_kind), ha="center", va="bottom", fontsize=8, color="#444444")
    figure.tight_layout(rect=(0, .08, 1, 1))
    figure.savefig(path, dpi=200)
    plt.close(figure)
    return True


def _input_notes(output_root: Path, towns: list[dict]) -> dict:
    """Describe retained retries and overlays without selecting replacement labels."""
    overlay = output_root / "rejudged.jsonl"
    overlay_info = {"present": overlay.exists(), "applied": False,
                    "status": "original_saved_labels_only", "sha256": None,
                    "provenance_validated": False, "nonempty_line_count": 0}
    if overlay.exists():
        data = overlay.read_bytes()
        overlay_info.update(status="detected_not_applied", sha256=hashlib.sha256(data).hexdigest(),
                            nonempty_line_count=sum(bool(line.strip()) for line in data.splitlines()))
    archived = []
    archive_root = output_root / "_incomplete"
    if archive_root.exists():
        if not archive_root.is_dir():
            raise ValueError("archived attempt root must be a directory")
        for attempt in sorted(archive_root.iterdir()):
            if not attempt.is_dir():
                raise ValueError("unexpected archived attempt entry")
            paths = sorted(attempt.iterdir())
            if not paths or any(not path.is_dir() for path in paths):
                raise ValueError("archived attempt has missing or unexpected town entries")
            for path in paths:
                town = audit_town(path)
                if town["run_status"] == "completed":
                    raise ValueError("completed archived attempt requires an explicit attempt-selection policy")
                if any(town.get(key) != towns[0].get(key)
                       for key in ("config_sha256", "execution_manifest_sha256", "evidence_kind")):
                    raise ValueError("archived and active attempts have different collection provenance")
                archived.append({"path": path.relative_to(output_root).as_posix(),
                                 "run_id": town["run_id"], "run_status": town["run_status"],
                                 "manifest_sha256": hashlib.sha256((path / "manifest.json").read_bytes()).hexdigest()})
    return {"label_policy": "original_saved_evaluations_only_no_best_attempt_selection",
            "rejudge_overlay": overlay_info, "archived_attempts_excluded_from_outcomes": archived,
            "active_manifest_sha256": {path.relative_to(output_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                                       for path in sorted(output_root.glob("*/manifest.json"))},
            "archived_manifest_sha256": {item["path"] + "/manifest.json": item["manifest_sha256"] for item in archived}}


def analyze(output_root: Path, destination: Path) -> dict:
    output_root = Path(output_root)
    destination = Path(destination)
    source_path, destination_path = output_root.resolve(), destination.resolve()
    if destination_path == source_path or source_path in destination_path.parents:
        raise ValueError("analysis destination must be outside the saved collection")
    if destination.exists():
        raise FileExistsError("analysis destination already exists")
    towns, config, excluded = load_towns(output_root)
    input_notes = _input_notes(output_root, towns)
    module = config["meta"]["module"]
    listeners = listener_rows(towns, config)
    pairs = pair_rows(towns, config)
    conditions = condition_summary(towns, config)
    cells = cell_summary(pairs, config)
    diffs = contrasts(pairs) if module == "pilot" else []
    knobs = knob_summary(pairs, config) if module == "main" else []
    models = mixed_models(listeners, module)
    dependency_versions = {}
    for name in ("statsmodels", "pandas", "numpy", "scipy", "matplotlib"):
        try:
            dependency_versions[name] = package_metadata.version(name)
        except package_metadata.PackageNotFoundError:
            dependency_versions[name] = None
    destination.mkdir(parents=True, exist_ok=False)
    meta = {"module": module, "evidence_kind": towns[0]["evidence_kind"], "study_eligible": False, "towns": len(towns),
            "pairs": len(pairs), "excluded_towns": excluded, "config_sha256": towns[0]["config_sha256"],
            "provider_manifest_sha256": towns[0].get("execution_manifest_sha256"),
            "unmatched_completed_towns": len(towns) - 2 * len(pairs),
            "pairs_with_incomplete_judgments": sum(not row["judgments_complete"] for row in pairs),
            "pairs_with_undefined_conditional_belief": sum(row["truth_discount"] is None for row in pairs),
            "missing_judgments": sum(row["judgment_status"] == "missing" for row in listeners),
            "invalid_judgments": sum(row["judgment_status"] in {"invalid", "duplicate"} for row in listeners),
            "analysis_status": "descriptive_exploratory_not_final_specification",
            "analysis_bundle_version": "truth-discount-analysis-0.3", "python_version": sys.version.split()[0],
            "dependency_versions": dependency_versions,
            "analysis_source_sha256": {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                       for name in ("analysis.py", "artifacts.py", "scoring.py", "config.py", "runner.py", "contracts.py")},
            "measurement_limits": MEASUREMENT_LIMITS, "input_notes": input_notes,
            "bootstrap": {"resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED,
                          "unit": "twin pair", "method": "percentile", "multiplicity_adjusted": False,
                          "missing_policy": "available_matched_pairs_per_outcome_no_invalid_label_imputation"}}
    (destination / "listeners.csv").write_text(_csv(listeners), encoding="utf-8", newline="")
    (destination / "pairs.csv").write_text(_csv(pairs), encoding="utf-8", newline="")
    (destination / "cells.csv").write_text(_csv(cells), encoding="utf-8", newline="")
    (destination / "conditions.csv").write_text(_csv(conditions), encoding="utf-8", newline="")
    if module == "main":
        (destination / "knobs.csv").write_text(_csv(knobs), encoding="utf-8", newline="")
        plotted = _plot_knobs(knobs, destination / "truth_discount_by_knob.png", meta["evidence_kind"])
    else:
        plotted = _plot(cells, destination / "truth_discount_by_cell.png", meta["evidence_kind"])
    summary = {**meta, "cells": cells, "conditions": conditions, "contrasts": diffs, "knobs": knobs, "models": models,
               "plot_written": plotted}
    (destination / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    (destination / "report.md").write_text(_report(meta, cells, diffs, knobs, models, conditions), encoding="utf-8")
    return summary
