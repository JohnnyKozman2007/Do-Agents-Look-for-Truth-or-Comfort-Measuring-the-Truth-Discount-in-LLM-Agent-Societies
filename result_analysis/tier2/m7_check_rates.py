"""Metric 7 - first-hand check (GO) rates: which source cues drive verification.

First-hand listeners decide GO/SKIP *before* they see any poster, so rumor and truth twins get the same
information. Differences between twins at this stage are pure sampling noise, which makes that a built-in
placebo check.
"""
import numpy as np
import pandas as pd

import charts
from t2lib import (MODEL_NAMES, boot_groups, design, diff_ci, did_ci, logit, norm_sf2, or_table, pct, rate_ci)

KNOBS = [  # (label, column, level_a (numerator), level_b)
    ("Closeness: friend vs stranger", "closeness", "close_friend", "stranger"),
    ("Authority: mayor vs citizen", "authority", "mayor", "citizen"),
    ("Reliability: good vs poor record", "reliability", "good_record", "poor_record"),
    ("Wealth: rich vs poor", "wealth", "rich", "poor"),
    ("Gender: woman vs man", "gender", "woman", "man"),
    ("Age: old vs young", "age", "old", "young"),
]
INTERACTIONS = [
    ("Closeness x Reliability", "closeness", "close_friend", "reliability", "good_record"),
    ("Authority x Reliability", "authority", "mayor", "reliability", "good_record"),
    ("Wealth x Reliability", "wealth", "rich", "reliability", "good_record"),
    ("Closeness x Authority", "closeness", "close_friend", "authority", "mayor"),
]
MODELS = ["deepseek_v4_flash", "qwen_3_8_flash"]


def run(df, B=2000):
    fh = df[df.layer == "first_hand"].reset_index(drop=True)
    blocks, tables, summary = [], {}, []

    # ---- 1. overall rates by model x condition -------------------------------------------------
    rows = []
    for m in MODELS:
        for c in ("rumor", "truth_twin"):
            s = fh[(fh.model == m) & (fh.condition == c)]
            p, lo, hi, n = rate_ci(s, B=B)
            rows.append(dict(model=MODEL_NAMES[m], condition=c, go_rate=p, lo=lo, hi=hi, n=n))
    t_overall = pd.DataFrame(rows)
    tables["m7_overall_rates"] = t_overall
    series = []
    for c, label in (("rumor", "Rumor twin"), ("truth_twin", "Truth twin")):
        sub = t_overall[t_overall.condition == c]
        series.append(dict(name=label, vals=list(sub.go_rate), lo=list(sub.lo), hi=list(sub.hi)))
    blocks += [("h3", "How often do first-hand listeners pay $5 to check?"),
               ("svg", charts.grouped_bars(list(t_overall.model.unique()), series, title="Check (GO) rate, first-hand listeners"))]
    ds, qw = t_overall[t_overall.model == "DeepSeek-V4-Flash"].go_rate.mean(), t_overall[t_overall.model == "Qwen3.8-Flash"].go_rate.mean()
    summary.append(f"Models differ sharply in baseline checking: DeepSeek {pct(ds)} vs Qwen {pct(qw)} of first-hand listeners take the bus. "
                   "Qwen's near-ceiling rate leaves little room for any knob to matter.")

    # ---- 2. placebo: rumor vs truth at first-hand (should be ~0) ------------------------------
    rows = []
    for m in MODELS + ["pooled"]:
        s = fh if m == "pooled" else fh[fh.model == m]
        d, lo, hi = diff_ci(s, (s.condition == "truth_twin").values, (s.condition == "rumor").values, B=B)
        rows.append(dict(model=MODEL_NAMES.get(m, "Pooled"), truth_minus_rumor=d, lo=lo, hi=hi))
    t_placebo = pd.DataFrame(rows)
    tables["m7_placebo_truth_vs_rumor"] = t_placebo
    # twin agreement on the same seat
    w = fh.pivot_table(index=["pair_id", "seat", "model"], columns="condition", values="go").dropna().reset_index()
    ag = []
    for m in MODELS:
        s = w[w.model == m]
        obs = float((s.rumor == s.truth_twin).mean())
        p = (s.rumor.mean() + s.truth_twin.mean()) / 2
        exp = p ** 2 + (1 - p) ** 2
        ag.append(dict(model=MODEL_NAMES[m], same_decision_in_both_twins=obs, expected_if_independent=exp, n_seats=len(s)))
    t_agree = pd.DataFrame(ag)
    tables["m7_twin_agreement"] = t_agree
    blocks += [("h3", "Placebo check: rumor vs truth twin at the check decision"),
               ("p", "Listeners decide before they see the poster, so truth should not change who checks. "
                     "A difference near zero (CI spanning 0) confirms the check decision carries no hidden twin signal."),
               ("table", t_placebo, "Truth-twin minus rumor-twin check rate (cluster-bootstrap 95% CI)"),
               ("p", "Same seat, same layout, both twins: how often did the agent make the same GO/SKIP choice? "
                     "Agreement above the independence baseline means the choice is driven by the seat/persona/cues, the remainder is sampling noise."),
               ("table", t_agree, "Twin agreement at identical seats")]
    pd_pooled = t_placebo.iloc[-1]
    summary.append(f"Placebo holds: truth minus rumor check rate is {pd_pooled.truth_minus_rumor * 100:+.1f} pts "
                   f"(95% CI {pd_pooled.lo * 100:+.1f} to {pd_pooled.hi * 100:+.1f}).")

    # ---- 3. knob contrasts ------------------------------------------------------------------
    rows = []
    for m in MODELS + ["pooled"]:
        s = fh if m == "pooled" else fh[fh.model == m]
        for lab, col, a, b in KNOBS:
            d, lo, hi = diff_ci(s, (s[col] == a).values, (s[col] == b).values, B=B)
            ra = s[s[col] == a].go.mean(); rb = s[s[col] == b].go.mean()
            rows.append(dict(model=MODEL_NAMES.get(m, "Pooled"), knob=lab, rate_a=ra, rate_b=rb, diff=d, lo=lo, hi=hi))
    t_knob = pd.DataFrame(rows)
    tables["m7_knob_contrasts"] = t_knob
    f_rows = []
    for lab, *_ in KNOBS:
        for gi, m in enumerate(["Pooled", "DeepSeek-V4-Flash", "Qwen3.8-Flash"]):
            r = t_knob[(t_knob.knob == lab) & (t_knob.model == m)].iloc[0]
            f_rows.append(dict(label=f"{lab.split(':')[0]} - {m.split('-')[0]}", est=r["diff"], lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "Which source cues change checking?"),
               ("p", "Each dot is the difference in check rate between the two levels of a knob (first level minus second), pooled over rumor and truth twins. "
                     "Right of zero means the first level triggers more checking."),
               ("svg", charts.forest(f_rows, "difference in check rate", kind="signed", title="Knob effects on first-hand checking")),
               ("table", t_knob, "Marginal contrasts with cluster-bootstrap 95% CIs (cluster = twin pair)")]
    pooled = t_knob[t_knob.model == "Pooled"].set_index("knob")
    sig = [(k, r) for k, r in pooled.iterrows() if r.lo > 0 or r.hi < 0]
    summary.append("Cues that significantly move checking (pooled): " +
                   ("; ".join(f"{k} ({r['diff'] * 100:+.0f} pts)" for k, r in sig) if sig else "none") + ".")
    cl = pooled.loc["Closeness: friend vs stranger"]
    if cl["diff"] > 0 and cl.lo > 0:
        summary.append("Closeness runs opposite to the 'trust a friend' hypothesis: listeners check MORE when the source is a close friend, not less.")

    # ---- 4. logistic regression --------------------------------------------------------------
    reg_rows = []
    for m in ["pooled"] + MODELS:
        s = fh if m == "pooled" else fh[fh.model == m]
        spec = [("closeness: friend", (s.closeness == "close_friend")), ("authority: mayor", (s.authority == "mayor")),
                ("reliability: good record", (s.reliability == "good_record")), ("wealth: rich", (s.wealth == "rich")),
                ("gender: woman", (s.gender == "woman")), ("age: old", (s.age == "old"))]
        if m == "pooled":
            spec.append(("model: Qwen", (s.model == "qwen_3_8_flash")))
        X, names = design(s, spec)
        fit = logit(X, s.go.values, cluster=s.pair_id.values)
        t = or_table(fit, names)
        t.insert(0, "sample", MODEL_NAMES.get(m, "Pooled"))
        reg_rows.append(t)
    t_reg = pd.concat(reg_rows, ignore_index=True)
    tables["m7_logit_additive"] = t_reg
    f_rows = []
    for gi, m in enumerate(["Pooled", "DeepSeek-V4-Flash", "Qwen3.8-Flash"]):
        for _, r in t_reg[(t_reg["sample"] == m) & (t_reg.term != "model: Qwen")].iterrows():
            f_rows.append(dict(label=f"{r.term} - {m.split('-')[0]}", est=r.odds_ratio, lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "Adjusted effects (logistic regression)"),
               ("p", "Odds ratios for checking, all knobs in one model, cluster-robust SEs by twin pair. OR above 1 means more checking."),
               ("svg", charts.forest(f_rows, "odds ratio (log scale)", xmin=0.15, xmax=8, zero=1.0, kind="or", log=True,
                                     title="Adjusted odds ratios", row_h=20)),
               ("table", t_reg.round(3), "Additive logistic model")]

    # ---- 5. planned interactions -------------------------------------------------------------
    rows, heat_blocks = [], []
    for m in MODELS + ["pooled"]:
        s = fh if m == "pooled" else fh[fh.model == m]
        for lab, ca, la, cb, lb in INTERACTIONS:
            p, lo, hi = did_ci(s, (s[ca] == la).values, (s[cb] == lb).values, B=B)
            rows.append(dict(model=MODEL_NAMES.get(m, "Pooled"), interaction=lab, did=p, lo=lo, hi=hi))
    t_int = pd.DataFrame(rows)
    tables["m7_interactions"] = t_int
    f_rows = []
    for lab, *_ in INTERACTIONS:
        for gi, m in enumerate(["Pooled", "DeepSeek-V4-Flash", "Qwen3.8-Flash"]):
            r = t_int[(t_int.interaction == lab) & (t_int.model == m)].iloc[0]
            f_rows.append(dict(label=f"{lab} - {m.split('-')[0]}", est=r.did, lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "Do cues combine? (planned 2x2 interactions)"),
               ("p", "Difference-in-differences of check rates: how much the effect of the first factor changes when the second factor flips. Zero means the effects simply add."),
               ("svg", charts.forest(f_rows, "difference-in-differences (check rate)", kind="signed", title="Interaction contrasts", row_h=20)),
               ("table", t_int, "Interaction contrasts, cluster-bootstrap 95% CI")]
    # 2x2 heatmaps for the reliability pairs, per model
    for m in MODELS:
        s = fh[fh.model == m]
        panels = []
        for lab, ca, la, cb, lb in INTERACTIONS:
            rl = [f"{ca}: " + x.replace("_", " ") for x in (la, [v for v in s[ca].unique() if v != la][0])]
            cl_ = [x.replace("_", " ") for x in (lb, [v for v in s[cb].unique() if v != lb][0])]
            vals = [[s[(s[ca] == a) & (s[cb] == b)].go.mean() for b in (lb, [v for v in s[cb].unique() if v != lb][0])]
                    for a in (la, [v for v in s[ca].unique() if v != la][0])]
            panels.append(charts.heatmap(rl, cl_, vals, cell=52, title=lab))
        blocks.append(("grid", panels, f"Check rates for each 2x2 combination - {MODEL_NAMES[m]}"))

    # ---- 6. 64-cell map ----------------------------------------------------------------------
    cell_rows = fh.groupby(["model", "cell_id", "closeness", "authority", "reliability", "wealth", "identity"]).go.agg(["mean", "count"]).reset_index()
    cell_rows = cell_rows.rename(columns={"mean": "go_rate", "count": "n_listeners"})
    tables["m7_cell_rates"] = cell_rows
    for m in MODELS:
        c = cell_rows[cell_rows.model == m]
        row_keys = [(r, cl_) for r in ("good_record", "poor_record") for cl_ in ("close_friend", "stranger")]
        col_keys = [(a, w, i) for a in ("mayor", "citizen") for w in ("rich", "poor") for i in ("woman_old", "woman_young", "man_old", "man_young")]
        vals, ann = [], []
        for r, cl_ in row_keys:
            rv, ra = [], []
            for a, w, i in col_keys:
                x = c[(c.reliability == r) & (c.closeness == cl_) & (c.authority == a) & (c.wealth == w) & (c.identity == i)]
                if len(x):
                    rv.append(float(x.go_rate.iloc[0]))
                    ra.append(f"cell {int(x.cell_id.iloc[0])}: {x.go_rate.iloc[0]:.0%} (n={int(x.n_listeners.iloc[0])})")
                else:
                    rv.append(None); ra.append("")
            vals.append(rv); ann.append(ra)
        blocks.append(("svg", charts.heatmap([f"{r.split('_')[0]} / {cl_.split('_')[0]}" for r, cl_ in row_keys],
                                              [f"{a} | {w} | {i.replace('_', ' ')}" for a, w, i in col_keys], vals, ann=ann, cell=30,
                                              title=f"All 64 cells, check rate (%) - {MODEL_NAMES[m]}")))
    blocks.append(("p", "Each cell holds only about 6-7 twin pairs x 12 listeners per model, so single cells are noisy; use them for pattern-spotting, not inference."))

    # ---- 7. data quality ---------------------------------------------------------------------
    mal = fh.groupby(["model", "condition"]).malformed.sum().reset_index()
    tables["m7_malformed_decisions"] = mal
    blocks += [("h3", "Data quality"),
               ("p", f"{int(fh.malformed.sum())} first-hand decisions were malformed and defaulted to SKIP "
                     f"({int(df.malformed.sum())} across all listeners). They are kept as SKIP, as the runner defined; the table shows where they fall."),
               ("table", mal, "Malformed decisions by model and condition")]
    return dict(id="m7", title="Metric 7 - First-hand check rates", summary=summary, blocks=blocks, tables=tables)
