"""Metric 17 - variance decomposition (belief side) and seed-count planning.

  (a) ICCs of listener-level belief within towns / pairs / layouts / cells / personas / seats / source personas.
  (b) How much of the pair-level truth discount is explained by the knobs vs layout, repetition and source persona.
  (c) Minimum detectable effects for the ten planned contrasts at today's n and at the planned 39 pairs per cell,
      and the pairs per cell needed to detect a target effect. These use the observed pair-level variance, so they are
      only as good as the pilot's variance estimate.
"""
import numpy as np
import pandas as pd

from m10_primary_td import groups
from t3lib import KNOBS, LAYER_NAMES, MODEL_NAMES, MODELS, code_pm, design, dummies, fit_contrasts, icc_anova, norm_isf, ols, pair_table, usable
import charts

PLANNED_PAIRS_PER_CELL = 39
TARGETS = (0.05, 0.10)


def _r2(pt, blocks):
    spec = []
    for kind, cols in blocks:
        if kind == "knobs":
            x = {k: code_pm(pt[k], a) for k, a, _, _ in KNOBS}
            spec += [(k, x[k]) for k in x]
            for a, b in (("closeness", "reliability"), ("authority", "reliability"), ("wealth", "reliability"), ("closeness", "authority")):
                spec.append((f"{a}:{b}", x[a] * x[b]))
        else:
            for c in cols:
                if pt[c].nunique() > 1:
                    spec += dummies(pt[c], c)
    if not spec:
        return np.nan, np.nan, 0
    X, _ = design(pt, spec)
    f = ols(X, pt.td.values)
    n, k = len(pt), f["rank"]
    return f["r2"], (1 - (1 - f["r2"]) * (n - 1) / max(n - k, 1)), k


def run(d, B=300):
    blocks, tables, summary = [], {}, []
    # ---- (a) ICC of listener belief ---------------------------------------------------------------------
    rows = []
    for layer in ("first_hand", "second_hand"):
        for name, s in groups(d):
            x = s[(s.layer == layer) & s.score.notna()]
            for grp, col in (("town", "run_id"), ("twin pair", "pair_id"), ("cell (knob profile)", "cell_id"), ("layout", "layout_id"),
                             ("listener persona", "persona_id"), ("seat", "seat"), ("source persona", "source_persona_id")):
                icc, lo, hi, G, nbar, deff = icc_anova(x.score.values, x[col].values, B=B)
                rows.append(dict(layer=LAYER_NAMES[layer], model=name, grouping=grp, icc=icc, lo=lo, hi=hi, groups=G, mean_group_size=nbar, design_effect=deff))
    I = pd.DataFrame(rows)
    tables["m17_icc"] = I
    f = [dict(label=f"{r.layer} | {r.model} | {r.grouping}", est=r.icc, lo=r.lo, hi=r.hi, group=0 if r.layer == "First-hand" else 1) for r in I[I.model != "Pooled"].itertuples()]
    blocks += [("h3", "How clustered is belief?"),
               ("p", "ICC = the share of listener-level belief variance that sits between groups (ANOVA estimator, unbalanced). "
                     "The town ICC is the non-independence the spec warns about; the design effect is how much it inflates variances if listeners were treated as independent."),
               ("svg", charts.forest(f, "intraclass correlation", kind="num", row_h=14, title="ICC of listener belief by grouping (per model)")),
               ("table", I, "Bootstrap CIs resample groups.")]
    t_town = I[(I.grouping == "town") & (I.layer == "First-hand") & (I.model != "Pooled")]
    for r in t_town.itertuples():
        summary.append(f"{r.model}: first-hand belief ICC within towns = {r.icc:.2f}; treating the {r.mean_group_size:.0f} listeners per town as independent would understate variances by about x{r.design_effect:.1f}.")

    # ---- (b) pair-level TD variance explained -------------------------------------------------------------
    rows = []
    for name, s in groups(d):
        pt = usable(pair_table(s, "score", "first_hand")).reset_index(drop=True)
        if len(pt) < 40:
            continue
        sets = [("knobs", None), ("layout", ["layout_id"]), ("repetition", ["rep_id"]), ("source persona", ["source_persona_id"])]
        if name == "Pooled":
            sets.insert(0, ("model", ["model"]))
        full_blocks = [("knobs" if k == "knobs" else "dummy", c) for k, c in sets]
        full = _r2(pt, full_blocks)
        row = dict(model=name, pairs=len(pt), r2_all=full[0], r2_adjusted=full[1], rank=full[2])
        for i, (k, c) in enumerate(sets):
            rest = full_blocks[:i] + full_blocks[i + 1:]
            only = _r2(pt, [full_blocks[i]])
            row[f"only_{k}"] = only[0]
            row[f"added_last_{k}"] = full[0] - (_r2(pt, rest)[0] if rest else 0.0)
        rows.append(row)
    V = pd.DataFrame(rows)
    tables["m17_td_variance_explained"] = V
    blocks += [("h3", "What explains the pair-level truth discount?"),
               ("p", "R-squared of an OLS model of pair TD. 'only_X' is the R-squared of block X alone; 'added_last_X' is what X adds on top of the other blocks. "
                     "Layout and source persona are partly collinear (the layout fixes the source persona), so read their numbers together. Large unexplained variance means pair-to-pair noise dominates."),
               ("table", V, "Descriptive; ignores model uncertainty.")]
    for r in V.itertuples():
        summary.append(f"{r.model}: knobs and interactions alone explain {100 * r.only_knobs:.1f}% of pair-level TD variance; all factors {100 * r.r2_all:.1f}% (adjusted {100 * r.r2_adjusted:.1f}%).")

    # ---- (c) power and seed planning ----------------------------------------------------------------------
    rows = []
    z_raw = norm_isf(0.025) + norm_isf(0.2)       # alpha 0.05 two-sided, power 80%
    z_holm = norm_isf(0.005 / 2) + norm_isf(0.2)  # alpha 0.05/10 per contrast (conservative Holm bound)
    for name, s in groups(d):
        pt = usable(pair_table(s, "score", "first_hand"))
        if len(pt) < 40:
            continue
        t, fit = fit_contrasts(pt)
        per_cell = len(pt) / max(pt.cell_id.nunique(), 1) / (1 if name != "Pooled" else 2)  # pairs per cell per model
        for r in t.itertuples():
            row = dict(model=name, id=r.id, contrast=r.contrast, se_now=r.se, pairs_per_cell_now=per_cell,
                       mde_80_raw=z_raw * r.se, mde_80_holm_bound=z_holm * r.se,
                       mde_at_planned_39=z_holm * r.se * np.sqrt(per_cell / PLANNED_PAIRS_PER_CELL))
            for tg in TARGETS:
                row[f"pairs_per_cell_for_{tg:.2f}"] = per_cell * (z_holm * r.se / tg) ** 2
            rows.append(row)
    P = pd.DataFrame(rows)
    tables["m17_power_planning"] = P
    blocks += [("h3", "Seed count needed to scale up"),
               ("p", f"Minimum detectable effect (MDE) at 80% power: 'raw' uses alpha 0.05 per test, 'holm_bound' uses alpha 0.005 (0.05 / 10, a conservative stand-in for the Holm family). "
                     f"mde_at_planned_39 projects the holm-bound MDE to {PLANNED_PAIRS_PER_CELL} pairs per cell, assuming the same pair-level variance. "
                     "pairs_per_cell_for_X is the pairs per cell needed to detect an effect of X belief points. Interactions usually have larger standard errors than main effects, so compare the rows."),
               ("table", P, "Per model, first-hand TD. Based on this run's pair-level variance (including any judge noise).")]
    for name in P.model.unique():
        x = P[P.model == name]
        mains = x[x.id.isin([1, 2, 3, 4, 9, 10])]
        summary.append(f"{name}: at {PLANNED_PAIRS_PER_CELL} pairs/cell the Holm-bound MDE is about {mains.mde_at_planned_39.mean():.3f} belief points for main effects and "
                       f"{x[x.id.isin([5, 6, 7, 8])].mde_at_planned_39.mean():.3f} for interactions.")
    return dict(id="m17", title="Metric 17 - Variance decomposition and seed planning", summary=summary, blocks=blocks, tables=tables)
