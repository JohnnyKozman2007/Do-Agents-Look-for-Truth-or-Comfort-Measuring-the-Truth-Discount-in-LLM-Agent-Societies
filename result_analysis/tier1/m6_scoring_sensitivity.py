"""Metric 6 - scoring sensitivity: which conclusions depend on how labels are turned into a belief score?

The same labels are recoded under alternative scorings and the headline truth discount and the ten planned contrasts are recomputed.
No new labels are needed. Schemes:
  primary                      FACT, CHECKED_TRUE = 1 | UNCERTAIN = 0.5 | SKEPTICAL, CHECKED_FALSE = 0
  strict (UNCERTAIN = 0)       only confident acceptance counts as belief
  lenient (UNCERTAIN = 1)      anything but rejection counts as belief
  graded (5 levels)            CHECKED_TRUE 1, FACT 0.75, UNCERTAIN 0.5, SKEPTICAL 0.25, CHECKED_FALSE 0
  primary + NOT_MENTIONED = 0 or 0.5   the spec's silence bounds
Scales differ between schemes, so compare signs, significance and rankings rather than raw magnitudes.
"""
import numpy as np
import pandas as pd

import charts
from t3lib import CONTRASTS, LAYER_NAMES, MODEL_NAMES, MODELS, SCHEMES, boot_mean, fit_contrasts, pair_table, usable


def _groups(d):
    return [(MODEL_NAMES[m], d[d.model == m]) for m in MODELS if (d.model == m).any()] + [("Pooled", d)]


def run(d, B=1000):
    blocks, tables, summary = [], {}, []
    d2 = d.copy()
    cols = {}
    for i, (name, mapping) in enumerate(SCHEMES.items()):
        d2[f"_s{i}"] = d2.label.map(mapping)
        cols[name] = f"_s{i}"
    cols["primary, NOT_MENTIONED = 0"] = "score_nm0"
    cols["primary, NOT_MENTIONED = 0.5"] = "score_nm5"
    primary = next(iter(cols))

    # ---- A. headline truth discount under each scheme ---------------------------------------------------
    rows = []
    for name, s in _groups(d2):
        for layer in ("first_hand", "second_hand"):
            for scheme, col in cols.items():
                td = boot_mean(usable(pair_table(s, col, layer)).td, B=B)
                rows.append(dict(model=name, layer=LAYER_NAMES[layer], scheme=scheme, pairs=td[3], td=td[0], lo=td[1], hi=td[2]))
    A = pd.DataFrame(rows)
    tables["m6_td_by_scheme"] = A
    blocks += [("h3", "Headline truth discount under each scoring"),
               ("p", "Truth discount = truth-twin minus rumor-twin mean belief, per twin pair. Magnitudes shift with the scale (a strict scheme lowers every belief; a lenient one raises it), "
                     "so the question is whether the sign and the exclusion of zero survive.")]
    for layer in ("First-hand", "Second-hand"):
        z = A[A.layer == layer]
        fr = []
        for gi, name in enumerate(dict.fromkeys(z.model)):
            for r in z[z.model == name].itertuples():
                fr.append(dict(label=f"{name.split('-')[0]} | {r.scheme}", est=r.td, lo=r.lo, hi=r.hi, group=gi))
        blocks.append(("svg", charts.forest(fr, "truth discount (belief points)", kind="signed", row_h=14, title=f"{layer} truth discount by scoring scheme")))
    blocks.append(("table", A, "Pair-level, bootstrap CIs over twin pairs."))
    for layer in ("First-hand", "Second-hand"):
        for name in dict.fromkeys(A.model):
            z = A[(A.model == name) & (A.layer == layer)]
            ok = bool(((z.lo > 0) | (z.hi < 0)).all())
            same_sign = bool((np.sign(z.td) == np.sign(z.td.iloc[0])).all())
            summary.append(f"{layer} TD, {name}: " + ("sign and exclusion of zero hold under all schemes" if ok else
                                                      ("sign agrees under all schemes, but the interval includes zero under at least one" if same_sign else "the sign changes with the scoring scheme")) +
                           f" (range {z.td.min():+.3f} to {z.td.max():+.3f}).")

    # ---- B. planned contrasts under each scheme -----------------------------------------------------------
    rows = []
    for name, s in _groups(d2):
        for scheme, col in cols.items():
            pt = usable(pair_table(s, col, "first_hand"))
            if len(pt) < 40:
                continue
            t, _ = fit_contrasts(pt)
            for r in t.itertuples():
                rows.append(dict(model=name, scheme=scheme, id=r.id, contrast=r.contrast, estimate=r.estimate, p=r.p, p_holm=r.p_holm, significant_holm_05=bool(r.significant_holm_05)))
    C = pd.DataFrame(rows)
    tables["m6_contrasts_by_scheme"] = C
    blocks += [("h3", "Do the ten planned contrasts depend on the scoring?"),
               ("p", "Each cell shows the contrast estimate (difference in truth discount); * marks a contrast that survives Holm at 0.05 under that scheme. "
                     "A contrast is robust when its sign and its star agree across the columns.")]
    for name in dict.fromkeys(C.model):
        z = C[C.model == name]
        mat = []
        for cid, label, _, _, _ in CONTRASTS:
            row = {"contrast": f"{cid}. {label.replace(' x truth discount', '')}"}
            for scheme in cols:
                r = z[(z.scheme == scheme) & (z.id == cid)]
                row[scheme] = (f"{r.estimate.iloc[0]:+.3f}{'*' if bool(r.significant_holm_05.iloc[0]) else ''}" if len(r) else "-")
            mat.append(row)
        blocks.append(("table", pd.DataFrame(mat), f"{name}: estimate per scheme, * = significant after Holm (first-hand)."))
        sig = z.pivot(index="id", columns="scheme", values="significant_holm_05")
        est = z.pivot(index="id", columns="scheme", values="estimate")
        stable_verdict = int((sig.nunique(axis=1) == 1).sum())
        stable_sign = int(((np.sign(est).nunique(axis=1)) == 1).sum())
        summary.append(f"{name}: {stable_verdict} of 10 planned contrasts keep the same Holm verdict under all {len(cols)} scorings; {stable_sign} of 10 keep the same sign.")
        flips = [int(i) for i in sig.index[sig.nunique(axis=1) > 1]]
        if flips:
            summary.append(f"{name}: scoring-dependent contrasts (Holm verdict changes): {', '.join(map(str, flips))}.")
    return dict(id="m6", title="Metric 6 - Scoring sensitivity", summary=summary, blocks=blocks, tables=tables)
