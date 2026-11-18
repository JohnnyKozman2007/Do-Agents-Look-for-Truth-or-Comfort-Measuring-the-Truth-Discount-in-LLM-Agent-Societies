"""Metric 12 - the ten planned contrasts on the pair-level truth discount, with Holm correction.

Model: pair TD ~ 6 effect-coded knobs (+/-0.5, so a coefficient is the difference between levels) + the four planned
interactions (coefficient = difference-in-differences), HC1-robust SEs. The Holm family is the ten contrasts of
docs/01_experimental_spec.md section 9. Sensitivity: NOT_MENTIONED = 0 / 0.5, and adjusting for layout and repetition.
"""
import numpy as np
import pandas as pd

from m10_primary_td import groups
from t3lib import CONTRASTS, SCORES, fit_contrasts, pair_table, usable
import charts


def run(d, B=2000):
    blocks, tables, summary = [], {}, []
    all_rows = []
    for name, s in groups(d):
        adj = ("model", "layout_id", "rep_id") if name == "Pooled" else ("layout_id", "rep_id")
        base = {}
        for variant, col in SCORES.items():
            pt = usable(pair_table(s, col, "first_hand"))
            if len(pt) < 40:
                continue
            base[variant], _ = fit_contrasts(pt)
        if "primary" not in base:
            continue
        t = base["primary"].copy()
        for variant in ("NOT_MENTIONED=0", "NOT_MENTIONED=0.5"):
            if variant in base:
                t["est_" + variant.replace("NOT_MENTIONED=", "nm")] = base[variant].estimate.values
                t["p_holm_" + variant.replace("NOT_MENTIONED=", "nm")] = base[variant].p_holm.values
        ta, _ = fit_contrasts(usable(pair_table(s, "score", "first_hand")), adjust=adj)
        t["est_adj_layout_rep"] = ta.estimate.values
        t["p_holm_adj_layout_rep"] = ta.p_holm.values
        t.insert(0, "model", name)
        all_rows.append(t)
    T = pd.concat(all_rows, ignore_index=True)
    tables["m12_planned_contrasts"] = T

    blocks += [("h3", "The ten planned contrasts"),
               ("p", "Each estimate is a difference in truth discount (belief points, 0-1 scale). A main-effect contrast compares the first-named level with the second, "
                     "averaged over the other factors; an interaction contrast is a difference-in-differences. Sign matters: TD is truth minus rumor belief, "
                     "so a smaller TD means the rumor is believed relatively more. p_holm is the Holm-adjusted p-value across the ten contrasts.")]
    for name in T.model.unique():
        s = T[T.model == name]
        f = [dict(label=f"{r.id}. {r.contrast.replace(' x truth discount', '')}", est=r.estimate, lo=r.ci_low, hi=r.ci_high,
                  group=0 if r.significant_holm_05 else 1) for r in s.itertuples()]
        blocks += [("svg", charts.forest(f, "difference in truth discount", kind="signed", row_h=21,
                                          title=f"Planned contrasts - {name} (green = significant after Holm, orange = not)")),
                   ("table", s.drop(columns=["model", "hypothesis"]), f"{name}: estimates with 95% CI (HC1 robust), raw and Holm-adjusted p, and sensitivity estimates.")]
        sig = [f"{r.id}" for r in s.itertuples() if r.significant_holm_05]
        summary.append(f"{name}: {len(sig)} of 10 planned contrasts survive Holm at 0.05" + (f" (contrast {', '.join(sig)})." if sig else "."))
    hyp = pd.DataFrame([dict(id=c[0], contrast=c[1], hypothesis=c[4]) for c in CONTRASTS])
    blocks.append(("table", hyp, "What each contrast tests (from the experimental spec)."))
    return dict(id="m12", title="Metric 12 - Ten planned contrasts", summary=summary, blocks=blocks, tables=tables)
