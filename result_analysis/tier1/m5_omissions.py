"""Metric 5 - label and omission analysis: is silence (NOT_MENTIONED) real behavior or a judge artifact?

The primary belief mean leaves NOT_MENTIONED out, so omissions matter in two ways: if they differ between twins the conditional
truth discount is selection-biased, and if the judge assigns them where the runner's keyword rule saw a mention they may be
judge artifacts. This module reports omission rates by group, the runner-rule vs judge comparison, and how far omissions can move
the truth discount (the spec's 0 / 0.5 imputations plus worst-case bounds).
"""
import numpy as np
import pandas as pd

import charts
from t2lib import design, dummies, logit, wald_joint
from t3lib import KNOBS, LAYER_NAMES, MODEL_NAMES, MODELS, boot_mean, flag_rate_ci, pair_table, rate_diff_ci, usable


def _groups(d):
    return [(MODEL_NAMES[m], d[d.model == m]) for m in MODELS if (d.model == m).any()] + [("Pooled", d)]


def run(d, B=500):
    blocks, tables, summary = [], {}, []
    lab = d[d.labeled == 1]

    # ---- 1. omission rate by model, layer and twin --------------------------------------------------
    rows = []
    for name, s in _groups(lab):
        for layer in ("first_hand", "second_hand"):
            for c in ("truth_twin", "rumor"):
                x = s[(s.layer == layer) & (s.condition == c)]
                if len(x):
                    r = flag_rate_ci(x, "omitted", None, B=B)
                    rows.append(dict(model=name, layer=LAYER_NAMES[layer], twin=c, labeled=len(x), omitted=int(x.omitted.sum()), omission_rate=r[0], lo=r[1], hi=r[2]))
    T1 = pd.DataFrame(rows)
    tables["m5_omission_rates"] = T1
    sub = T1[T1.model != "Pooled"]
    cats = [f"{m.split('-')[0]}\n{ly}" for m, ly in dict.fromkeys(zip(sub.model, sub.layer))]
    series = []
    for c, nm in (("truth_twin", "Truth twin"), ("rumor", "Rumor twin")):
        z = sub[sub.twin == c]
        series.append(dict(name=nm, vals=list(z.omission_rate), lo=list(z.lo), hi=list(z.hi)))
    his = [v for s_ in series for v in s_["hi"] if np.isfinite(v)]
    ymax = max(0.02, max(his) * 1.15) if his else 0.1
    blocks += [("h3", "How often are listeners silent about the concert?"),
               ("p", "Omission rate = NOT_MENTIONED labels among labeled listeners. Silence is a real choice by design (each persona has an ordinary daily event to talk about), "
                     "but it also depends on the judge. Rates are cluster-bootstrap over twin pairs."),
               ("svg", charts.grouped_bars(cats, series, ymax=ymax, kind="pct", title="Omission rate by model, layer and twin")),
               ("table", T1, "Share of labeled listeners labeled NOT_MENTIONED.", ("omission_rate", "lo", "hi"))]

    # ---- 2. do omissions differ between twins? --------------------------------------------------------
    rows = []
    for name, s in _groups(lab):
        for layer in ("first_hand", "second_hand"):
            x = s[s.layer == layer].reset_index(drop=True)
            if x.empty:
                continue
            dd, lo, hi = rate_diff_ci(x, "omitted", x.condition == "truth_twin", x.condition == "rumor", B=B)
            rows.append(dict(model=name, layer=LAYER_NAMES[layer], truth_minus_rumor_omission=dd, lo=lo, hi=hi, differs=bool(np.isfinite(lo) and (lo > 0 or hi < 0))))
    T2 = pd.DataFrame(rows)
    tables["m5_omission_twin_difference"] = T2
    blocks += [("h3", "Do omissions differ between twins?"),
               ("p", "If the rumor twin stays silent more (or less) often than the truth twin, the conditional truth discount compares different kinds of listeners in the two twins."),
               ("table", T2, "Truth-twin minus rumor-twin omission rate, cluster bootstrap over pairs.", ("truth_minus_rumor_omission", "lo", "hi"))]
    for r in T2[(T2.model == "Pooled")].itertuples():
        summary.append(f"{r.layer}: omission rate differs by {100 * r.truth_minus_rumor_omission:+.1f} points between truth and rumor twins "
                       f"(CI {100 * r.lo:+.1f} to {100 * r.hi:+.1f})" + ("; selection is possible." if r.differs else "; no clear selection."))

    # ---- 3. omissions by source cue --------------------------------------------------------------------
    rows = []
    for name, s in _groups(lab):
        for layer in ("first_hand", "second_hand"):
            x = s[s.layer == layer].reset_index(drop=True)
            if len(x) == 0:
                continue
            for col, a, b, label in KNOBS:
                dd, lo, hi = rate_diff_ci(x, "omitted", x[col] == a, x[col] == b, B=B)
                rows.append(dict(model=name, layer=LAYER_NAMES[layer], knob=label, omission_difference=dd, lo=lo, hi=hi))
    T3 = pd.DataFrame(rows)
    tables["m5_omission_by_knob"] = T3
    blocks += [("h3", "Does the source's profile change who stays silent?")]
    for layer in ("First-hand", "Second-hand"):
        z = T3[(T3.model == "Pooled") & (T3.layer == layer)]
        if len(z):
            blocks.append(("svg", charts.forest([dict(label=r.knob, est=r.omission_difference, lo=r.lo, hi=r.hi, group=0) for r in z.itertuples()],
                                                "omission rate difference (first level minus second)", kind="signed", row_h=20, title=f"{layer} listeners, pooled models")))
    blocks.append(("table", T3, "Cluster bootstrap over twin pairs."))

    # ---- 4. persona ---------------------------------------------------------------------------------------
    rows, tests = [], []
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            x = lab[(lab.model == m) & (lab.layer == layer)].reset_index(drop=True)
            if x.empty:
                continue
            for pid, g in x.groupby("persona_id"):
                r = flag_rate_ci(g, "omitted", None, B=min(B, 300))
                rows.append(dict(model=MODEL_NAMES[m], layer=LAYER_NAMES[layer], persona_id=pid, persona=g.persona.iloc[0], occupation=g.occupation.iloc[0],
                                 labeled=len(g), omission_rate=r[0], lo=r[1], hi=r[2]))
            if x.omitted.sum() >= 30:
                spec = [("closeness", (x.closeness == "close_friend")), ("authority", (x.authority == "mayor")), ("reliability", (x.reliability == "good_record")),
                        ("wealth", (x.wealth == "rich")), ("gender", (x.gender == "woman")), ("age", (x.age == "old"))]
                base = len(spec)
                spec = spec + dummies(x.persona_id, "persona")
                X, _ = design(x, spec)
                fit = logit(X, x.omitted.values, cluster=x.pair_id.values, ridge=1e-4)
                chi, k, p = wald_joint(fit, list(range(base + 1, len(spec) + 1)))
                tests.append(dict(model=MODEL_NAMES[m], layer=LAYER_NAMES[layer], omissions=int(x.omitted.sum()), factor="listener persona", wald_chi2=chi, df=k, p=p))
    T4 = pd.DataFrame(rows)
    T4t = pd.DataFrame(tests)
    tables["m5_omission_by_persona"] = T4
    if len(T4t):
        tables["m5_omission_persona_tests"] = T4t
    blocks += [("h3", "Is silence a persona trait?"),
               ("p", "Omission rate by listener persona, and a joint Wald test of persona effects with the six source knobs adjusted (cluster-robust by pair). "
                     "A strong persona effect suggests silence reflects the character's conversational style, not just the judge. Tests are skipped when a group has fewer than 30 omissions.")]
    if len(T4t):
        blocks.append(("table", T4t, "Joint Wald test of listener-persona effects on being labeled NOT_MENTIONED."))
    blocks.append(("table", T4, "Omission rate by listener persona.", ("omission_rate", "lo", "hi")))
    for r in T4t.itertuples():
        summary.append(f"{r.model}, {r.layer}: persona explains omissions " + ("clearly" if r.p < 0.01 else "weakly or not at all") + f" (Wald p = {r.p:.3g}, {r.omissions} omissions).")

    # ---- 5. runner keyword rule vs judge ------------------------------------------------------------------
    rows = []
    for layer in ("first_hand", "second_hand"):
        x = lab[lab.layer == layer]
        for step, g in x.assign(step=x.funnel_step.fillna(0).astype(int)).groupby("step"):
            rows.append(dict(layer=LAYER_NAMES[layer], runner_rule=("no mention found (rule-coded omission)" if step == 0 else f"mention found at funnel step {step}"),
                             labeled=len(g), judged_not_mentioned=int(g.omitted.sum()), share_judged_not_mentioned=float(g.omitted.mean())))
    T5 = pd.DataFrame(rows)
    tables["m5_runner_rule_vs_judge"] = T5
    rule_mention = lab[lab.funnel_step.notna()]
    rule_none = lab[lab.funnel_step.isna()]
    blocks += [("h3", "Runner keyword rule vs judge"),
               ("p", "The runner marks a listener as having mentioned the concert when a keyword rule fires at funnel steps 1-4, and rule-codes the rest as omissions without a judge call. "
                     "Judge NOT_MENTIONED on a call where the rule saw a mention is either a keyword false positive (for example, only the other artist was named) or a judge artifact; "
                     "a non-omission label on a rule-coded omission should not happen."),
               ("table", T5, "Judge omissions by what the runner rule found.", ("share_judged_not_mentioned",))]
    if len(rule_mention):
        summary.append(f"Judge says NOT_MENTIONED on {int(rule_mention.omitted.sum()):,} of {len(rule_mention):,} calls where the runner's rule saw a mention "
                       f"({100 * rule_mention.omitted.mean():.1f}%); {int((rule_none.omitted == 0).sum()):,} of {len(rule_none):,} rule-coded omissions got a mention label.")

    # ---- 6. how far can omissions move the truth discount ----------------------------------------------------
    dd_ = d.copy()
    nm = dd_.label == "NOT_MENTIONED"
    tw = dd_.condition == "truth_twin"
    dd_["_lo"] = dd_.score.where(~nm, np.where(tw, 0.0, 1.0))  # omissions most damaging to a positive TD
    dd_["_hi"] = dd_.score.where(~nm, np.where(tw, 1.0, 0.0))
    rows = []
    for name, s in _groups(dd_):
        for layer in ("first_hand", "second_hand"):
            for label, col in (("conditional (omissions excluded)", "score"), ("omissions = 0", "score_nm0"), ("omissions = 0.5", "score_nm5"),
                               ("worst case, lower bound", "_lo"), ("worst case, upper bound", "_hi")):
                u = usable(pair_table(s, col, layer))
                td = boot_mean(u.td, B=B)
                rows.append(dict(model=name, layer=LAYER_NAMES[layer], treatment_of_omissions=label, pairs=td[3], td=td[0], lo=td[1], hi=td[2]))
    T6 = pd.DataFrame(rows)
    tables["m5_td_under_omission_bounds"] = T6
    fr = []
    z = T6[T6.layer == "First-hand"]
    for gi, name in enumerate(dict.fromkeys(z.model)):
        for r in z[z.model == name].itertuples():
            fr.append(dict(label=f"{name.split('-')[0]} | {r.treatment_of_omissions}", est=r.td, lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "How far can omissions move the truth discount?"),
               ("p", "The spec's two bounds impute every omission as 0 or 0.5. The worst-case bounds are looser: omitted truth-twin listeners count as 0 and omitted rumor-twin listeners as 1 (lower), or the reverse (upper). "
                     "If even the lower bound stays above 0, the sign of the truth discount cannot be an artifact of silence."),
               ("svg", charts.forest(fr, "truth discount (belief points)", kind="signed", row_h=15, title="First-hand truth discount under each treatment of omissions")),
               ("table", T6, "Pair-level, bootstrap CIs over twin pairs.")]
    pooled = T6[(T6.model == "Pooled") & (T6.layer == "First-hand")].set_index("treatment_of_omissions")
    if len(pooled) == 5:
        summary.append(f"First-hand TD ranges from {pooled.loc['worst case, lower bound', 'td']:+.3f} (worst case) to {pooled.loc['worst case, upper bound', 'td']:+.3f} (best case) "
                       f"depending on how omissions are treated; the conditional estimate is {pooled.loc['conditional (omissions excluded)', 'td']:+.3f}.")
    return dict(id="m5", title="Metric 5 - Label and omission analysis", summary=summary, blocks=blocks, tables=tables)
