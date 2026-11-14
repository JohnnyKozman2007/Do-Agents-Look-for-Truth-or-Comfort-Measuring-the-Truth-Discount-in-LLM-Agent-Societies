"""Metric 13 - asymmetry: over-believing rumors vs under-believing truths.

Ideal listeners believe the truth (score 1) and reject the rumor (score 0). So:
  over-belief in rumors = mean belief in the rumor twin            (0 is ideal)
  under-belief in truths = 1 - mean belief in the truth twin       (0 is ideal)
  net credulity = rumor belief + truth belief - 1 = over-belief - under-belief
Positive net credulity means the listeners lean toward believing whatever they hear; negative means they lean skeptical.
"""
import numpy as np
import pandas as pd

from m10_primary_td import groups
from t3lib import KNOBS, LAYER_NAMES, boot_diff, boot_mean, pair_table, usable
import charts


def run(d, B=2000):
    blocks, tables, summary = [], {}, []
    rows = []
    for layer in ("first_hand", "second_hand"):
        for name, s in groups(d):
            u = usable(pair_table(s, "score", layer))
            if len(u) == 0:
                continue
            over = boot_mean(u.rumor_mean, B=B)
            under = boot_mean(1 - u.truth_mean, B=B)
            net = boot_mean(u.rumor_mean + u.truth_mean - 1, B=B)
            rows.append(dict(layer=LAYER_NAMES[layer], model=name, pairs_usable=over[3],
                             over_belief_rumor=over[0], over_lo=over[1], over_hi=over[2],
                             under_belief_truth=under[0], under_lo=under[1], under_hi=under[2],
                             net_credulity=net[0], net_lo=net[1], net_hi=net[2]))
    t = pd.DataFrame(rows)
    tables["m13_asymmetry"] = t
    f = []
    for gi, (lab, col) in enumerate((("over-belief in rumors", "over"), ("under-belief in truths", "under"), ("net credulity", "net"))):
        for r in t.itertuples():
            f.append(dict(label=f"{r.layer} | {r.model}", est=getattr(r, {"over": "over_belief_rumor", "under": "under_belief_truth", "net": "net_credulity"}[col]),
                          lo=getattr(r, col + "_lo"), hi=getattr(r, col + "_hi"), group=gi))
    f.sort(key=lambda r: r["label"])
    blocks += [("h3", "Do listeners err more toward credulity or toward skepticism?"),
               ("p", "Over-belief and under-belief are both 0 for a perfect listener. Net credulity is their difference: positive means more belief than the truth warrants overall."),
               ("svg", charts.forest(f, "belief score points", kind="signed", row_h=17, title="Over-belief in rumors / under-belief in truths / net credulity")),
               ("table", t, "Pair-level means with 95% bootstrap CIs over twin pairs (a series per colour: green over-belief, orange under-belief, blue net).")]
    for r in t[t.layer == "First-hand"].itertuples():
        lean = "credulous" if r.net_credulity > 0 else "skeptical"
        summary.append(f"{r.model} (first-hand): over-belief {r.over_belief_rumor:.2f}, under-belief {r.under_belief_truth:.2f}, net {r.net_credulity:+.2f} ({lean} on balance; CI {r.net_lo:+.2f} to {r.net_hi:+.2f}).")

    # ---- which source cues drive over-belief in rumors vs under-belief in truths? -------------
    rows = []
    for name, s in groups(d):
        u = usable(pair_table(s, "score", "first_hand"))
        for col, a, b, lab in KNOBS:
            ua, ub = u[u[col] == a], u[u[col] == b]
            r1 = boot_diff(ua.rumor_mean, ub.rumor_mean, B=B)
            r2 = boot_diff(1 - ua.truth_mean, 1 - ub.truth_mean, B=B)
            rows.append(dict(model=name, knob=lab, d_over_belief_rumor=r1[0], d_over_lo=r1[1], d_over_hi=r1[2],
                             d_under_belief_truth=r2[0], d_under_lo=r2[1], d_under_hi=r2[2], pairs_a=r1[3], pairs_b=r1[4]))
    t2 = pd.DataFrame(rows)
    tables["m13_asymmetry_by_knob"] = t2
    blocks += [("h3", "Which cues push listeners toward over- or under-belief?"),
               ("p", "Differences between knob levels (first level minus second) in rumor-twin belief and in 1 minus truth-twin belief. "
                     "A cue that raises over-belief in rumors without changing under-belief in truths is a pure credulity cue.")]
    for name in t2.model.unique():
        s = t2[t2.model == name]
        f = []
        for r in s.itertuples():
            f.append(dict(label=f"{r.knob} | rumor over-belief", est=r.d_over_belief_rumor, lo=r.d_over_lo, hi=r.d_over_hi, group=0))
            f.append(dict(label=f"{r.knob} | truth under-belief", est=r.d_under_belief_truth, lo=r.d_under_lo, hi=r.d_under_hi, group=1))
        blocks.append(("svg", charts.forest(f, "difference between levels (belief points)", kind="signed", row_h=17, title=f"Cue effects on over- and under-belief - {name}")))
    blocks.append(("table", t2, "Independent-group bootstrap over twin pairs; positive = the first-named level believes more."))
    return dict(id="m13", title="Metric 13 - Asymmetry", summary=summary, blocks=blocks, tables=tables)
