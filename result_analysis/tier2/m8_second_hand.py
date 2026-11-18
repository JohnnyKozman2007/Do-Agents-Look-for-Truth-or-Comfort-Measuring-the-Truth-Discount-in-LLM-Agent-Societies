"""Metric 8 - second-hand behavior: how evidence spreads one hop and whether it changes checking."""
import numpy as np
import pandas as pd

import charts
from m7_check_rates import KNOBS, MODELS
from t2lib import MODEL_NAMES, design, diff_ci, logit, or_table, pct, rate_ci

STRATA = [("Partner skipped\n(no evidence)", lambda s: s.partner_go == 0),
          ("Partner checked,\nevidence not passed", lambda s: (s.partner_go == 1) & (s.evidence_passed == 0)),
          ("Partner checked,\nevidence passed", lambda s: (s.partner_go == 1) & (s.evidence_passed == 1))]


def run(df, B=2000):
    sh = df[df.layer == "second_hand"].reset_index(drop=True)
    blocks, tables, summary = [], {}, []

    # ---- 1. evidence funnel -------------------------------------------------------------------
    rows = []
    for m in MODELS:
        for c in ("rumor", "truth_twin"):
            s = sh[(sh.model == m) & (sh.condition == c)]
            pc = s[s.partner_go == 1]
            rows.append(dict(model=MODEL_NAMES[m], condition=c, n=len(s),
                             partner_checked=s.partner_go.mean(),
                             evidence_passed_given_checked=pc.evidence_passed.mean() if len(pc) else np.nan,
                             go_overall=s.go.mean()))
    t_funnel = pd.DataFrame(rows)
    tables["m8_funnel"] = t_funnel
    blocks += [("h3", "The evidence funnel: partner checks, passes it on, listener acts"),
               ("p", "A second-hand listener only hears about the concert from a first-hand partner. The partner may have skipped the check, "
                     "checked but not repeated what the poster said, or checked and passed the evidence on. "
                     "'Evidence passed' is a keyword rule in the runner (checked, then named the real artist and the board in one line), not a semantic judgment."),
               ("table", t_funnel, "Funnel by model and condition")]
    for m in MODELS:
        s = sh[sh.model == m]
        series, rows2 = [], []
        for c, lab in (("rumor", "Rumor twin"), ("truth_twin", "Truth twin")):
            vals, los, his = [], [], []
            for sl, f in STRATA:
                sub = s[(s.condition == c) & f(s)]
                if len(sub) >= 10:
                    p, lo, hi, n = rate_ci(sub, B=B)
                else:
                    p = lo = hi = np.nan
                vals.append(p); los.append(lo); his.append(hi)
                rows2.append(dict(model=MODEL_NAMES[m], condition=c, stratum=sl.replace("\n", " "), go_rate=p, lo=lo, hi=hi, n=len(sub)))
            series.append(dict(name=lab, vals=vals, lo=los, hi=his))
        tables[f"m8_go_by_partner_state_{m}"] = pd.DataFrame(rows2)
        blocks.append(("svg", charts.grouped_bars([x[0] for x in STRATA], series, title=f"Second-hand check rate by what the partner did - {MODEL_NAMES[m]}")))
    blocks.append(("p", "Strata with fewer than 10 listeners are left blank."))

    # ---- 2. truth vs rumor at second hand -----------------------------------------------------
    rows = []
    for m in MODELS + ["pooled"]:
        s = sh if m == "pooled" else sh[sh.model == m]
        d, lo, hi = diff_ci(s, (s.condition == "truth_twin").values, (s.condition == "rumor").values, B=B)
        rows.append(dict(model=MODEL_NAMES.get(m, "Pooled"), stratum="all second-hand listeners", truth_minus_rumor=d, lo=lo, hi=hi))
        for sl, f in STRATA:
            msk = f(s).values
            a = ((s.condition == "truth_twin").values & msk); b = ((s.condition == "rumor").values & msk)
            if a.sum() >= 10 and b.sum() >= 10:
                d, lo, hi = diff_ci(s, a, b, B=B)
            else:
                d = lo = hi = np.nan
            rows.append(dict(model=MODEL_NAMES.get(m, "Pooled"), stratum=sl.replace("\n", " "), truth_minus_rumor=d, lo=lo, hi=hi))
    t_diff = pd.DataFrame(rows)
    tables["m8_truth_minus_rumor"] = t_diff
    f_rows = [dict(label=f"{r.stratum} - {r.model.split('-')[0]}", est=r.truth_minus_rumor, lo=r.lo, hi=r.hi,
                   group={"Pooled": 0, "DeepSeek-V4-Flash": 1, "Qwen3.8-Flash": 2}[r.model]) for r in t_diff.itertuples()
              if r.model != "Pooled"]
    blocks += [("h3", "Does the truth of the claim change second-hand checking?"),
               ("p", "Truth-twin minus rumor-twin check rate. A negative value means truth makes listeners check less (they trust it); positive means more. "
                     "Within a stratum the partner's behavior is held roughly fixed, which separates 'what the partner said' from 'what the listener does with it'."),
               ("svg", charts.forest(f_rows, "truth minus rumor (check rate)", kind="signed", title="Second-hand: truth twin vs rumor twin", row_h=20)),
               ("table", t_diff, "Cluster-bootstrap 95% CIs (cluster = twin pair)")]
    ov = t_diff[(t_diff.stratum == "all second-hand listeners") & (t_diff.model != "Pooled")]
    for r in ov.itertuples():
        sig = "significant" if (r.lo > 0 or r.hi < 0) else "not clearly different from zero"
        summary.append(f"{r.model}: second-hand check rate is {r.truth_minus_rumor * 100:+.1f} pts in truth vs rumor twins ({sig}).")

    # ---- 3. how much do second-hand listeners follow the partner? -----------------------------
    rows = []
    for m in MODELS:
        s = sh[sh.model == m]
        a = s[s.partner_go == 1].go.mean(); b = s[s.partner_go == 0].go.mean()
        rows.append(dict(model=MODEL_NAMES[m], go_if_partner_checked=a, go_if_partner_skipped=b, gap=a - b))
    t_follow = pd.DataFrame(rows)
    tables["m8_partner_following"] = t_follow
    blocks += [("table", t_follow, "Second-hand check rate by partner's decision")]
    for r in t_follow.itertuples():
        summary.append(f"{r.model}: second-hand listeners check {pct(r.go_if_partner_checked)} of the time when their partner checked vs {pct(r.go_if_partner_skipped)} when the partner skipped.")

    # ---- 4. knob effects at second hand ---------------------------------------------------------
    rows = []
    for m in MODELS + ["pooled"]:
        s = sh if m == "pooled" else sh[sh.model == m]
        for lab, col, a, b in KNOBS:
            d, lo, hi = diff_ci(s, (s[col] == a).values, (s[col] == b).values, B=B)
            rows.append(dict(model=MODEL_NAMES.get(m, "Pooled"), knob=lab, diff=d, lo=lo, hi=hi))
    t_knob = pd.DataFrame(rows)
    tables["m8_knob_contrasts"] = t_knob
    f_rows = []
    for lab, *_ in KNOBS:
        for gi, m in enumerate(["Pooled", "DeepSeek-V4-Flash", "Qwen3.8-Flash"]):
            r = t_knob[(t_knob.knob == lab) & (t_knob.model == m)].iloc[0]
            f_rows.append(dict(label=f"{lab.split(':')[0]} - {m.split('-')[0]}", est=r["diff"], lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "Source cues at second hand"),
               ("p", "Second-hand listeners also see the 'About the source' block, but only hear the source's claim through a partner. Do the same cues still move their checking?"),
               ("svg", charts.forest(f_rows, "difference in check rate", kind="signed", title="Knob effects on second-hand checking", row_h=20)),
               ("table", t_knob, "Marginal contrasts")]
    pooled = t_knob[t_knob.model == "Pooled"].set_index("knob")
    sig = [(k, r) for k, r in pooled.iterrows() if r.lo > 0 or r.hi < 0]
    summary.append("Second-hand cues that significantly move checking (pooled): " +
                   ("; ".join(f"{k} ({r['diff'] * 100:+.0f} pts)" for k, r in sig) if sig else "none") + ".")

    # ---- 5. adjusted model ------------------------------------------------------------------
    reg = []
    for m in ["pooled"] + MODELS:
        s = sh if m == "pooled" else sh[sh.model == m]
        spec = [("closeness: friend", s.closeness == "close_friend"), ("authority: mayor", s.authority == "mayor"),
                ("reliability: good record", s.reliability == "good_record"), ("wealth: rich", s.wealth == "rich"),
                ("gender: woman", s.gender == "woman"), ("age: old", s.age == "old"),
                ("partner checked", s.partner_go == 1), ("evidence passed", s.evidence_passed == 1),
                ("truth twin", s.condition == "truth_twin")]
        if m == "pooled":
            spec.append(("model: Qwen", s.model == "qwen_3_8_flash"))
        X, names = design(s, spec)
        t = or_table(logit(X, s.go.values, cluster=s.pair_id.values), names)
        t.insert(0, "sample", MODEL_NAMES.get(m, "Pooled"))
        reg.append(t)
    t_reg = pd.concat(reg, ignore_index=True)
    tables["m8_logit"] = t_reg
    f_rows = []
    for gi, m in enumerate(["Pooled", "DeepSeek-V4-Flash", "Qwen3.8-Flash"]):
        for r in t_reg[(t_reg["sample"] == m) & (t_reg.term != "model: Qwen")].itertuples():
            f_rows.append(dict(label=f"{r.term} - {m.split('-')[0]}", est=r.odds_ratio, lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "Adjusted model (second-hand)"),
               ("p", "Odds ratios for the second-hand listener checking, controlling for the source knobs, whether the partner checked, whether evidence was passed on, and the twin condition."),
               ("svg", charts.forest(f_rows, "odds ratio (log scale)", xmin=0.05, xmax=20, zero=1.0, kind="or", log=True, title="Adjusted odds ratios, second-hand", row_h=18)),
               ("table", t_reg.round(3), "Additive logistic model, cluster-robust by twin pair")]
    return dict(id="m8", title="Metric 8 - Second-hand behavior", summary=summary, blocks=blocks, tables=tables)
