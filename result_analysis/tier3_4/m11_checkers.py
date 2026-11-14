"""Metric 11 - truth discount among checkers vs non-checkers (first-hand).

First-hand listeners decide GO/SKIP before seeing any poster. A SKIP listener in either twin has seen no evidence,
so the truth discount among non-checkers is a built-in noise floor; the discount among checkers is what the poster adds.
"""
import numpy as np
import pandas as pd

from m10_primary_td import groups
from t3lib import boot_mean, pair_table, usable
import charts


def run(d, B=2000):
    blocks, tables, summary = [], {}, []
    fh = d[d.layer == "first_hand"]
    rows = []
    for name, s in groups(d):
        p_go = s[s.layer == "first_hand"].go.mean()
        for stratum, mask in (("all first-hand", None), ("checkers (GO)", s.go == 1), ("non-checkers (SKIP)", s.go == 0)):
            pt = pair_table(s, "score", "first_hand", mask)
            u = usable(pt)
            td = boot_mean(u.td, B=B)
            rows.append(dict(model=name, stratum=stratum, pairs_usable=td[3], truth_mean=u.truth_mean.mean(), rumor_mean=u.rumor_mean.mean(),
                             td=td[0], td_lo=td[1], td_hi=td[2], share_checkers=p_go))
    t = pd.DataFrame(rows)
    tables["m11_strata_td"] = t
    f_rows = []
    for gi, stratum in enumerate(("all first-hand", "checkers (GO)", "non-checkers (SKIP)")):
        for r in t[t.stratum == stratum].itertuples():
            f_rows.append(dict(label=f"{r.model} | {stratum}", est=r.td, lo=r.td_lo, hi=r.td_hi, group=gi))
    f_rows.sort(key=lambda r: (r["label"].split(" | ")[0] != "Pooled", r["label"]))
    blocks += [("h3", "Truth discount by whether the listener checked"),
               ("p", "Non-checkers never saw a poster, so their twin-to-twin difference should be near zero (sampling noise only). "
                     "Checkers in the truth twin read the true poster and checkers in the rumor twin read a different artist, so their difference is the checking effect."),
               ("svg", charts.forest(f_rows, "truth discount (belief score points)", kind="signed", row_h=19, title="Truth discount by GO / SKIP stratum")),
               ("table", t, "Pair-level, bootstrap CIs over pairs. Stratum membership is a post-treatment choice, so use the strata descriptively.", ("share_checkers",))]
    for r in t[t.stratum == "non-checkers (SKIP)"].itertuples():
        ok = np.isfinite(r.td_lo) and r.td_lo <= 0 <= r.td_hi
        summary.append(f"{r.model}: non-checker TD (noise floor) = {r.td:+.3f} ({r.td_lo:+.3f} to {r.td_hi:+.3f}); "
                       + ("the interval includes 0 as designed." if ok else "the interval excludes 0, so something other than a poster separates the twins (check this)."))
    for r in t[t.stratum == "checkers (GO)"].itertuples():
        summary.append(f"{r.model}: checker TD = {r.td:+.3f}; checkers are {100 * r.share_checkers:.0f}% of first-hand listeners.")

    # ---- do the labels agree with the GO log? -------------------------------------------------
    rows = []
    for name, s in groups(fh):
        x = s[s.labeled == 1]
        chk = x.label.isin(["CHECKED_TRUE", "CHECKED_FALSE"])
        rows.append(dict(model=name, labeled=len(x),
                         go_labeled_checked=float(chk[x.go == 1].mean()) if (x.go == 1).any() else np.nan,
                         skip_labeled_checked=float(chk[x.go == 0].mean()) if (x.go == 0).any() else np.nan,
                         go_truth_labeled_CHECKED_TRUE=float((x.label[(x.go == 1) & (x.condition == "truth_twin")] == "CHECKED_TRUE").mean()),
                         go_rumor_labeled_CHECKED_FALSE=float((x.label[(x.go == 1) & (x.condition == "rumor")] == "CHECKED_FALSE").mean()),
                         go_but_not_checked_n=int(((x.go == 1) & ~chk).sum()), skip_but_checked_n=int(((x.go == 0) & chk).sum())))
    t2 = pd.DataFrame(rows)
    tables["m11_label_vs_go_log"] = t2
    blocks += [("h4", "Do the belief labels agree with the GO/SKIP log?"),
               ("p", "GO means the listener took the bus and read the board, so their label should be CHECKED_TRUE (truth twin) or CHECKED_FALSE (rumor twin); "
                     "SKIP listeners should not carry a CHECKED label. This is the only ground truth available for the judge at scale."),
               ("table", t2, "First-hand, labeled listeners. skip_labeled_checked and the *_n columns count disagreements.",
                ("go_labeled_checked", "skip_labeled_checked", "go_truth_labeled_CHECKED_TRUE", "go_rumor_labeled_CHECKED_FALSE"))]
    return dict(id="m11", title="Metric 11 - Checkers vs non-checkers", summary=summary, blocks=blocks, tables=tables)
