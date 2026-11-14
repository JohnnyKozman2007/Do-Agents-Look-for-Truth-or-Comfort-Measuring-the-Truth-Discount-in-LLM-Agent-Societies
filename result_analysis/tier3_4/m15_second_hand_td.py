"""Metric 15 - second-hand truth discount and certainty decay across one hop."""
import numpy as np
import pandas as pd

from m10_primary_td import groups
from t3lib import LAYER_NAMES, MODEL_NAMES, MODELS, SCORES, boot_mean, pair_table, usable
import charts


def run(d, B=2000):
    blocks, tables, summary = [], {}, []
    # ---- second-hand TD and decay vs first-hand --------------------------------------------------
    rows = []
    for name, s in groups(d):
        p1 = pair_table(s, "score", "first_hand")[["pair_id", "td"]].rename(columns={"td": "td_first"})
        for variant, col in SCORES.items():
            p2 = pair_table(s, col, "second_hand")[["pair_id", "td", "truth_mean", "rumor_mean"]].rename(columns={"td": "td_second"})
            u2 = usable(p2, "td_second")
            td = boot_mean(u2.td_second, B=B)
            both = p1.merge(p2, on="pair_id").dropna(subset=["td_first", "td_second"])
            dec = boot_mean(both.td_first - both.td_second, B=B)
            rows.append(dict(model=name, scoring=variant, pairs_usable=td[3], td_second_hand=td[0], td_lo=td[1], td_hi=td[2],
                             decay_first_minus_second=dec[0], decay_lo=dec[1], decay_hi=dec[2], pairs_both_layers=dec[3]))
    t = pd.DataFrame(rows)
    tables["m15_second_hand_td"] = t
    prim = t[t.scoring == "primary"]
    f = []
    for gi, (variant, _) in enumerate(SCORES.items()):
        for r in t[t.scoring == variant].itertuples():
            f.append(dict(label=f"{r.model} | {variant}", est=r.td_second_hand, lo=r.td_lo, hi=r.td_hi, group=gi))
    f.sort(key=lambda r: (r["label"].split(" | ")[0] != "Pooled", r["label"]))
    blocks += [("h3", "Truth discount after one hop"),
               ("p", "Second-hand listeners hear the news from a first-hand partner at the afternoon catch-up, then choose GO/SKIP and later take the evening call. "
                     "Decay = first-hand TD minus second-hand TD on pairs where both are defined (positive = the truth signal weakens after one hop)."),
               ("svg", charts.forest(f, "second-hand truth discount (belief points)", kind="signed", row_h=20, title="Second-hand truth discount")),
               ("table", t, "Pair-level, bootstrap CIs over twin pairs.")]
    for r in prim.itertuples():
        summary.append(f"{r.model}: second-hand TD {r.td_second_hand:+.3f} (CI {r.td_lo:+.3f} to {r.td_hi:+.3f}); decay vs first-hand {r.decay_first_minus_second:+.3f} (CI {r.decay_lo:+.3f} to {r.decay_hi:+.3f}).")

    # ---- what the second-hand listener learned from the partner -----------------------------------
    rows = []
    for name, s in groups(d):
        sh = s[s.layer == "second_hand"]
        for stratum, mask in (("partner checked", sh.partner_go == 1), ("partner skipped", sh.partner_go == 0),
                              ("evidence passed (rule)", sh.evidence_passed == 1), ("no evidence passed", sh.evidence_passed == 0),
                              ("listener checked", sh.go == 1), ("listener skipped", sh.go == 0)):
            full = s.copy()
            m = pd.Series(False, index=full.index)
            m.loc[sh.index[mask.values]] = True
            u = usable(pair_table(full, "score", "second_hand", m))
            td = boot_mean(u.td, B=B)
            rows.append(dict(model=name, stratum=stratum, pairs_usable=td[3], truth_mean=u.truth_mean.mean(), rumor_mean=u.rumor_mean.mean(), td=td[0], td_lo=td[1], td_hi=td[2]))
    t2 = pd.DataFrame(rows)
    tables["m15_second_hand_strata"] = t2
    blocks += [("h4", "Second-hand TD by what the listener received or did"),
               ("p", "Strata are determined partly by the twin (a partner's check, evidence passed, or the listener's own check), so these are descriptive. "
                     "'Evidence passed' is the runner's keyword rule, not a semantic judgment."),
               ("table", t2, "Pair-level TD within each stratum; a pair is usable only if both twins have listeners in the stratum.")]

    # ---- certainty decay ----------------------------------------------------------------------------
    rows, pair_cert = [], {}
    for name, s in groups(d):
        for layer in ("first_hand", "second_hand"):
            x = s[(s.layer == layer) & s.certainty.notna()]
            c = x.groupby("pair_id").certainty.mean()
            pair_cert[(name, layer)] = c
            cm = boot_mean(c.values, B=B)
            rows.append(dict(model=name, layer=LAYER_NAMES[layer], pairs=cm[3], certainty=cm[0], lo=cm[1], hi=cm[2],
                             uncertain_share=float((x.label == "UNCERTAIN").mean()) if len(x) else np.nan))
        both = pd.concat([pair_cert[(name, "first_hand")], pair_cert[(name, "second_hand")]], axis=1, keys=["a", "b"]).dropna()
        dd = boot_mean(both.a - both.b, B=B)
        rows.append(dict(model=name, layer="decay (first - second)", pairs=dd[3], certainty=dd[0], lo=dd[1], hi=dd[2], uncertain_share=np.nan))
    t3 = pd.DataFrame(rows)
    tables["m15_certainty"] = t3
    show = t3[~t3.layer.str.startswith("decay")]
    cats = list(dict.fromkeys(show.model))
    series = [dict(name=ly, vals=list(show[show.layer == ly].certainty), lo=list(show[show.layer == ly].lo), hi=list(show[show.layer == ly].hi)) for ly in ("First-hand", "Second-hand")]
    blocks += [("h3", "Certainty decay"),
               ("p", "Certainty = 1 when the listener commits to a belief (any label but UNCERTAIN) and 0 when UNCERTAIN, averaged within each pair across both twins and omission-free listeners. "
                     "A lower second-hand value means more hedging after one hop."),
               ("svg", charts.grouped_bars(cats, series, kind="num", title="Mean certainty by layer")),
               ("table", t3, "Bootstrap over twin pairs; decay rows are paired differences.", ("uncertain_share",))]
    for r in t3[t3.layer.str.startswith("decay")].itertuples():
        summary.append(f"{r.model}: certainty falls by {r.certainty:+.3f} (CI {r.lo:+.3f} to {r.hi:+.3f}) from first-hand to second-hand listeners.")
    return dict(id="m15", title="Metric 15 - Second-hand truth discount", summary=summary, blocks=blocks, tables=tables)
