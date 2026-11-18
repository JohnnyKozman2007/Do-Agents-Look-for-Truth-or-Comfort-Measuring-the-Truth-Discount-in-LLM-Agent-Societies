"""Metric 10 - primary truth discount (first-hand listeners), with the denominators the spec asks to show alongside it."""
import numpy as np
import pandas as pd

from t3lib import LABELS, MODEL_NAMES, MODELS, SCORES, boot_mean, pair_table, usable
import charts


def groups(d):
    return [(MODEL_NAMES[m], d[d.model == m]) for m in MODELS if (d.model == m).any()] + [("Pooled", d)]


def run(d, B=2000):
    blocks, tables, summary = [], {}, []
    layer = "first_hand"
    rows = []
    for name, s in groups(d):
        for variant, col in SCORES.items():
            pt = pair_table(s, col, layer)
            u = usable(pt)
            td = boot_mean(u.td, B=B)
            tr = boot_mean(u.truth_mean, B=B)
            ru = boot_mean(u.rumor_mean, B=B)
            rows.append(dict(model=name, scoring=variant, pairs_total=len(pt), pairs_usable=td[3], truth_mean=tr[0], truth_lo=tr[1], truth_hi=tr[2],
                             rumor_mean=ru[0], rumor_lo=ru[1], rumor_hi=ru[2], td=td[0], td_lo=td[1], td_hi=td[2]))
    t = pd.DataFrame(rows)
    tables["m10_primary_td"] = t

    prim = t[t.scoring == "primary"]
    blocks += [("h3", "Primary truth discount"),
               ("p", "Belief score is 1 for FACT / CHECKED_TRUE, 0.5 for UNCERTAIN, 0 for SKEPTICAL / CHECKED_FALSE; NOT_MENTIONED is left out of the mean. "
                     "Each twin pair contributes the mean belief of its valid first-hand listeners in each twin. A pair is usable when both twins have at least one valid score."),
               ("svg", charts.grouped_bars(list(prim.model), [dict(name="Truth twin", vals=list(prim.truth_mean), lo=list(prim.truth_lo), hi=list(prim.truth_hi)),
                                                                dict(name="Rumor twin", vals=list(prim.rumor_mean), lo=list(prim.rumor_lo), hi=list(prim.rumor_hi))],
                                           kind="num", title="Mean belief score by twin (first-hand listeners)")),
               ("table", t, "Pair-level means; 95% bootstrap CIs over twin pairs. pairs_total = pairs in the data, pairs_usable = pairs with a defined TD.")]
    f_rows = []
    for gi, (variant, col) in enumerate(SCORES.items()):
        for r in t[t.scoring == variant].itertuples():
            f_rows.append(dict(label=f"{r.model} | {variant}", est=r.td, lo=r.td_lo, hi=r.td_hi, group=gi))
    f_rows.sort(key=lambda r: (r["label"].split(" | ")[0] != "Pooled", r["label"]))
    blocks.append(("svg", charts.forest(f_rows, "truth discount (belief score points, 0-1 scale)", kind="signed", row_h=20,
                                          title="Truth discount under the primary score and both omission bounds")))
    for r in prim.itertuples():
        summary.append(f"{r.model}: TD = {r.td:+.3f} (95% CI {r.td_lo:+.3f} to {r.td_hi:+.3f}) on {int(r.pairs_usable):,} usable pairs; "
                       f"truth-twin belief {r.truth_mean:.2f}, rumor-twin belief {r.rumor_mean:.2f}.")
    bounds = t[(t.scoring != "primary")]
    stable = all(np.isfinite(r.td_lo) and (r.td_lo > 0 or r.td_hi < 0) for r in bounds.itertuples())
    summary.append("The sign and interval exclusion of zero " + ("hold" if stable else "do NOT all hold") + " under both NOT_MENTIONED bounds (see the forest plot).")

    # ---- denominators next to the difference --------------------------------------------------
    fh = d[d.layer == layer]
    rows = []
    for name, s in groups(fh):
        for c in ("truth_twin", "rumor"):
            x = s[s.condition == c]
            lab = x.label.value_counts()
            r = dict(model=name, twin=c, listeners=len(x), labeled=int(x.labeled.sum()), omission_rate=x.omitted.sum() / max(x.labeled.sum(), 1),
                     go_rate=x.go.mean())
            r.update({f"n_{k}": int(lab.get(k, 0)) for k in LABELS})
            rows.append(r)
    t2 = pd.DataFrame(rows)
    tables["m10_denominators"] = t2
    blocks += [("h4", "Denominators: omissions, GO rates and label counts"),
               ("table", t2, "First-hand listeners. The belief mean excludes omissions; GO denominators are kept even when a belief label is missing.", ("omission_rate", "go_rate"))]
    return dict(id="m10", title="Metric 10 - Primary truth discount", summary=summary, blocks=blocks, tables=tables)
