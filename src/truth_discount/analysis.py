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
import io
import json
from pathlib import Path
import random
import warnings
from typing import Any

from .artifacts import audit_town
from .config import load_config, study_cells
from .runner import concert_mentioned
from .scoring import paired_metrics

BOOTSTRAP_RESAMPLES = 5000
BOOTSTRAP_SEED = 20261120
_PAIR_OUTCOMES = ("truth_discount", "sensitivity_lower_difference", "sensitivity_neutral_difference",
                  "omission_rate_difference")
FACTORS = ("closeness", "authority", "reliability", "wealth", "gender", "age")
_TOWN_OUTCOMES = ("belief_mean", "sensitivity_lower", "sensitivity_neutral", "omission_rate",
                  "go_rate_first_hand", "go_rate_second_hand", "transmission_rate",
                  "evidence_transmission_rate")


def load_towns(output_root: Path) -> tuple[list[dict], dict, dict]:
    """Audit every saved town; return completed towns, their config and exclusions."""
    paths = sorted(p.parent for p in Path(output_root).glob("*/manifest.json"))
    if not paths:
        raise ValueError("no saved towns found")
    towns, excluded = [], defaultdict(int)
    for path in paths:
        town = audit_town(path)
        if town["run_status"] == "completed":
            towns.append(town)
        else:
            excluded[town["run_status"]] += 1
    if not towns:
        raise ValueError("no completed towns to analyze")
    if len({t["evidence_kind"] for t in towns}) != 1:
        raise ValueError("cannot pool fixture, mocked-provider and development-pilot evidence")
    if len({t["config_sha256"] for t in towns}) != 1:
        raise ValueError("towns were collected with different configurations")
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
            "evidence_transmission_rate": (sum(r["evidence_passed"] for r in checkers) / len(checkers)
                                           if checkers else None)}


def listener_rows(towns: list[dict], config: dict) -> list[dict]:
    """One row per scored listener, the long format for any statistics package."""
    mapping = config["judging_and_scoring"]["belief_numerical_mapping"]
    first = set(config["seating_and_pairing"]["first_hand_seats"])
    rows = []
    for town in towns:
        decisions = {d["seat_id"]: d["decision"] for d in
                     town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]}
        for evaluation in town["judge_evaluations"]:
            seat, label = evaluation["seat_id"], evaluation.get("label")
            valid = evaluation.get("status") == "valid"
            rows.append({"run_id": town["run_id"], "pair_id": town["pair_id"], "model_key": town["model_key"],
                         "cell_id": town["cell_id"], "condition_type": town["condition_type"],
                         "truth": int(town["condition_type"] == "truth_twin"),
                         "layout_id": town["layout_id"], "repetition_id": town["repetition_id"],
                         "real_artist": town["real_artist"], **factor_levels(town["knobs"]), "seat_id": seat,
                         "layer": "first_hand" if seat in first else "second_hand",
                         "label": label if valid else None,
                         "belief": mapping.get(label) if valid else None,
                         "mentioned": int(valid and label != "NOT_MENTIONED"),
                         "decision": decisions.get(seat)})
    return rows


def pair_rows(towns: list[dict], config: dict) -> list[dict]:
    by_run = {t["run_id"]: t for t in towns}
    rows = []
    for pair in paired_metrics(towns):
        if pair["status"] != "complete":
            continue
        truth, rumor = by_run[pair["truth_run_id"]], by_run[pair["rumor_run_id"]]
        tv, rv = _town_values(truth, config), _town_values(rumor, config)
        row = {"model_key": pair["model_key"], "pair_id": pair["pair_id"], "cell_id": truth["cell_id"],
               "real_artist": truth["real_artist"], **factor_levels(truth["knobs"]),
               **{k: pair[k] for k in _PAIR_OUTCOMES}}
        for key in _TOWN_OUTCOMES:
            row[key + "_truth"], row[key + "_rumor"] = tv[key], rv[key]
        rows.append(row)
    return rows


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bootstrap_ci(values: list[float], *, resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED,
                 level: float = 0.95) -> tuple[float, float] | tuple[None, None]:
    """Percentile interval for a mean, resampling independent pairs."""
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
                            key + "_n": len(values)})
        for key in _TOWN_OUTCOMES:
            for twin in ("truth", "rumor"):
                summary[f"{key}_{twin}"] = _mean(_present(rows, f"{key}_{twin}"))
        result.append(summary)
    return result


def contrasts(pairs: list[dict], reference: int = 2) -> list[dict]:
    """Each pilot cell's truth discount minus the Maximum Skepticism cell's."""
    grouped = defaultdict(list)
    for row in pairs:
        if row["truth_discount"] is not None:
            grouped[(row["model_key"], row["cell_id"])].append(row["truth_discount"])
    result = []
    for model in sorted({m for m, _ in grouped}):
        base = grouped.get((model, reference), [])
        for cell in sorted(c for m, c in grouped if m == model and c != reference):
            values = grouped[(model, cell)]
            low, high = _difference_ci(values, base, BOOTSTRAP_SEED + cell)
            result.append({"model_key": model, "cell_id": cell, "reference_cell_id": reference,
                           "difference": _mean(values) - _mean(base) if values and base else None,
                           "ci_low": low, "ci_high": high, "n_pairs": len(values), "n_reference_pairs": len(base)})
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
        rows = [row for row in pairs if row["model_key"] == model and row["truth_discount"] is not None]
        for index, factor in enumerate(FACTORS):
            present = {row[factor] for row in rows}
            levels = [level for level in order[factor] if level in present]
            if len(levels) != 2:
                continue
            a, b = ([row["truth_discount"] for row in rows if row[factor] == level] for level in levels)
            low, high = _difference_ci(a, b, BOOTSTRAP_SEED + 100 + index)
            result.append({"model_key": model, "factor": factor, "level_a": levels[0], "level_b": levels[1],
                           "truth_discount_a": _mean(a), "truth_discount_b": _mean(b),
                           "difference": _mean(a) - _mean(b) if a and b else None,
                           "ci_low": low, "ci_high": high, "n_pairs_a": len(a), "n_pairs_b": len(b)})
    return result


def mixed_models(listeners: list[dict], module: str = "pilot") -> dict:
    """Random intercept per town, fit separately for each agent model.

    Main study: belief ~ truth * (six factors) + real artist, as specified. The
    pilot's four cells fix the factors jointly, so cell indicators stand in for
    them. A town-clustered OLS fit is reported alongside.
    """
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
    except ImportError:
        return {"status": "not_run", "reason": "install the analysis extra (statsmodels, pandas)"}
    frame = pd.DataFrame([r for r in listeners if r["mentioned"]])
    formula = ("belief ~ truth * (" + " + ".join(f"C({f})" for f in FACTORS) + ") + C(real_artist)"
               if module == "main" else "belief ~ truth * C(cell_id) + C(real_artist)")
    result = {"status": "run", "formula": formula, "groups": "run_id (town)", "models": {}}
    for model, data in frame.groupby("model_key") if len(frame) else []:
        entry = {"n_listeners": int(len(data)), "n_towns": int(data["run_id"].nunique())}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                fit = smf.mixedlm(formula, data, groups=data["run_id"]).fit(reml=True)
                ci = fit.conf_int()
                entry["mixed"] = {name: {"estimate": float(fit.params[name]), "se": float(fit.bse[name]),
                                         "p": float(fit.pvalues[name]), "ci_low": float(ci.loc[name, 0]),
                                         "ci_high": float(ci.loc[name, 1])}
                                  for name in fit.params.index if name != "Group Var"}
                entry["converged"] = bool(fit.converged)
                ols = smf.ols(formula, data).fit(cov_type="cluster",
                                                 cov_kwds={"groups": pd.factorize(data["run_id"])[0]})
                entry["ols_town_clustered"] = {name: {"estimate": float(ols.params[name]),
                                                      "se": float(ols.bse[name]), "p": float(ols.pvalues[name])}
                                               for name in ols.params.index}
            except Exception as error:  # singular designs are reported, not hidden
                entry["error"] = f"{type(error).__name__}: {error}"
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
    if row[key] is None:
        return "—"
    if row[key + "_ci_low"] is None:
        return _fmt(row[key])
    return f"{_fmt(row[key])} [{_fmt(row[key + '_ci_low'])}, {_fmt(row[key + '_ci_high'])}]"


def _knob_lines(rows: list[dict]) -> list[str]:
    lines = ["| Factor | Levels (A / B) | Truth discount A / B | A − B [95% interval] | Pairs A / B |",
             "|---|---|---|---|---|"]
    for k in rows:
        interval = "" if k["ci_low"] is None else f" [{_fmt(k['ci_low'])}, {_fmt(k['ci_high'])}]"
        lines.append(f"| {k['factor']} | {k['level_a']} / {k['level_b']} | {_fmt(k['truth_discount_a'])} / "
                     f"{_fmt(k['truth_discount_b'])} | {_fmt(k['difference'])}{interval} | "
                     f"{k['n_pairs_a']} / {k['n_pairs_b']} |")
    return lines


def _report(meta: dict, cells: list[dict], diffs: list[dict], knobs: list[dict], models: dict) -> str:
    main = meta["module"] == "main"
    lines = ["# Main-study analysis" if main else "# Pilot analysis", "",
             f"Evidence: `{meta['evidence_kind']}` (not study-eligible). Towns analyzed: {meta['towns']}; "
             f"complete twin pairs: {meta['pairs']}; excluded towns: {meta['excluded_towns'] or 'none'}.",
             "Truth discount = truth-twin belief minus rumor belief, averaged over twin pairs. "
             "Brackets are 95% bootstrap intervals over pairs.", ""]
    for model in sorted({c["model_key"] for c in cells}):
        lines += [f"## {model}", ""]
        if main:
            lines += ["Truth discount at each level of each factor, averaged over the cells with that level. "
                      "Per-cell results for every cell are in `cells.csv`.", ""]
            lines += _knob_lines([k for k in knobs if k["model_key"] == model])
        else:
            lines += ["| Cell | Pairs | Truth discount | Silence = 0 | Silence = 0.5 | Belief truth / rumor | "
                      "Omission truth / rumor | GO first-hand truth / rumor | GO second-hand truth / rumor | "
                      "Passed on (rumor) | Evidence passed (rumor) |",
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
            lines += ["", "Truth discount compared with the Maximum Skepticism cell:", "",
                      "| Cell | Difference | 95% interval |", "|---|---|---|"]
            for d in rows:
                interval = "—" if d["ci_low"] is None else f"[{_fmt(d['ci_low'])}, {_fmt(d['ci_high'])}]"
                lines.append(f"| {d['cell_id']} | {_fmt(d['difference'])} | {interval} |")
        fit = models.get("models", {}).get(model, {}).get("mixed")
        if fit:
            lines += ["", f"Mixed model `{models['formula']}`, random intercept per town:", "",
                      "| Term | Estimate | SE | p |", "|---|---|---|---|"]
            lines += [f"| `{name}` | {_fmt(v['estimate'])} | {_fmt(v['se'])} | {_fmt(v['p'], 4)} |"
                      for name, v in fit.items() if name.startswith("truth") or name == "Intercept"]
        lines.append("")
    if models["status"] != "run":
        lines += [f"Mixed model not run: {models['reason']}.", ""]
    return "\n".join(lines)


def _plot(cells: list[dict], path: Path) -> bool:
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
        errors = [[h - (r["truth_discount_ci_low"] if r["truth_discount_ci_low"] is not None else h) for h, r in zip(heights, picked)],
                  [(r["truth_discount_ci_high"] if r["truth_discount_ci_high"] is not None else h) - h for h, r in zip(heights, picked)]]
        axis.bar(xs, heights, width, yerr=errors, capsize=3, label=model)
    axis.axhline(0, color="black", linewidth=0.8)
    axis.set_xticks([i + width * (len(models) - 1) / 2 for i in range(len(cell_ids))])
    axis.set_xticklabels([f"Cell {c}" for c in cell_ids])
    axis.set_ylabel("Truth discount (truth − rumor belief)")
    axis.legend(frameon=False, ncol=len(models), loc="lower center", bbox_to_anchor=(0.5, 1.0))
    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)
    return True


def _plot_knobs(knobs: list[dict], path: Path) -> bool:
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
        errors = [[v - (r["ci_low"] if r["ci_low"] is not None else v) for v, r in zip(values, picked)],
                  [(r["ci_high"] if r["ci_high"] is not None else v) - v for v, r in zip(values, picked)]]
        axis.barh(ys, values, height, xerr=errors, capsize=3, label=model)
    axis.axvline(0, color="black", linewidth=0.8)
    labels = {k["factor"]: f"{k['factor']}: {k['level_a']} − {k['level_b']}" for k in knobs}
    axis.set_yticks([i + height * (len(models) - 1) / 2 for i in range(len(FACTORS))])
    axis.set_yticklabels([labels.get(f, f) for f in FACTORS])
    axis.invert_yaxis()
    axis.set_xlabel("Difference in truth discount between levels")
    axis.legend(frameon=False, ncol=len(models), loc="lower center", bbox_to_anchor=(0.5, 1.0))
    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)
    return True


def analyze(output_root: Path, destination: Path) -> dict:
    towns, config, excluded = load_towns(output_root)
    module = config["meta"]["module"]
    listeners = listener_rows(towns, config)
    pairs = pair_rows(towns, config)
    cells = cell_summary(pairs, config)
    diffs = contrasts(pairs) if module == "pilot" else []
    knobs = knob_summary(pairs, config) if module == "main" else []
    models = mixed_models(listeners, module)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    meta = {"module": module, "evidence_kind": towns[0]["evidence_kind"], "study_eligible": False, "towns": len(towns),
            "pairs": len(pairs), "excluded_towns": excluded, "config_sha256": towns[0]["config_sha256"],
            "bootstrap": {"resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED, "unit": "twin pair"}}
    (destination / "listeners.csv").write_text(_csv(listeners), encoding="utf-8", newline="")
    (destination / "pairs.csv").write_text(_csv(pairs), encoding="utf-8", newline="")
    (destination / "cells.csv").write_text(_csv(cells), encoding="utf-8", newline="")
    if module == "main":
        (destination / "knobs.csv").write_text(_csv(knobs), encoding="utf-8", newline="")
        plotted = _plot_knobs(knobs, destination / "truth_discount_by_knob.png")
    else:
        plotted = _plot(cells, destination / "truth_discount_by_cell.png")
    summary = {**meta, "cells": cells, "contrasts": diffs, "knobs": knobs, "models": models,
               "plot_written": plotted}
    (destination / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    (destination / "report.md").write_text(_report(meta, cells, diffs, knobs, models), encoding="utf-8")
    return summary
