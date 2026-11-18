"""Metric 9 - who checks: persona, seat and source-persona effects vs the experimental knobs."""
import numpy as np
import pandas as pd

import charts
from m7_check_rates import MODELS
from t2lib import MODEL_NAMES, design, dummies, logit, pct, rate_ci, wald_joint, chi2_sf

KNOB_SPEC = lambda s: [("closeness", s.closeness == "close_friend"), ("authority", s.authority == "mayor"),
                       ("reliability", s.reliability == "good_record"), ("wealth", s.wealth == "rich"),
                       ("gender", s.gender == "woman"), ("age", s.age == "old")]


def _fit(s, groups):
    """Logistic fit with knob columns plus the requested dummy groups."""
    spec = KNOB_SPEC(s)
    idx = {}
    for g in groups:
        before = len(spec)
        spec = spec + dummies(s[g], g)
        idx[g] = list(range(before + 1, len(spec) + 1))  # +1 for the intercept column
    X, names = design(s, spec)
    return logit(X, s.go.values, cluster=s.pair_id.values), idx


def run(df, B=1000):
    blocks, tables, summary = [], {}, []
    persona_info = df[["persona_id", "persona", "occupation", "style"]].drop_duplicates().sort_values("persona_id")
    tables["m9_personas"] = persona_info

    # ---- 1. persona effects (per model, per layer) --------------------------------------------
    het_rows, rate_rows = [], []
    for layer in ("first_hand", "second_hand"):
        for m in MODELS:
            s = df[(df.layer == layer) & (df.model == m)].reset_index(drop=True)
            for pid, g in s.groupby("persona_id"):
                p, lo, hi, n = rate_ci(g, B=B)
                rate_rows.append(dict(layer=layer, model=MODEL_NAMES[m], persona_id=pid, persona=g.persona.iloc[0],
                                      occupation=g.occupation.iloc[0], go_rate=p, lo=lo, hi=hi, n=n))
            fit, idx = _fit(s, ["persona"])
            chi, k, p = wald_joint(fit, idx["persona"])
            het_rows.append(dict(layer=layer, model=MODEL_NAMES[m], factor="listener persona", wald_chi2=chi, df=k, p=p))
    t_pers = pd.DataFrame(rate_rows)
    tables["m9_persona_rates"] = t_pers
    for layer, lab in (("first_hand", "First-hand listeners"), ("second_hand", "Second-hand listeners")):
        f_rows = []
        for gi, m in enumerate(MODELS):
            sub = t_pers[(t_pers.layer == layer) & (t_pers.model == MODEL_NAMES[m])].sort_values("persona_id")
            for r in sub.itertuples():
                f_rows.append(dict(label=f"{r.persona} ({r.occupation}) - {MODEL_NAMES[m].split('-')[0]}", est=r.go_rate, lo=r.lo, hi=r.hi, group=gi))
        blocks += [("h3" if layer == "first_hand" else "h4", f"{lab}: check rate by persona"),
                   ("svg", charts.forest(f_rows, "check rate", xmin=0, xmax=1, zero=0.5, kind="pct", row_h=15, title=lab))]
    blocks.insert(0, ("h3", "Do some personas check more than others?"))
    blocks.insert(1, ("p", "Each persona sits in every seat across the Latin-square layouts, so persona and seat are balanced by design. "
                           "But each model only ran about half of the layouts, so the balance is partial; treat persona effects as exploratory."))

    # ---- 2. seat and source persona effects ---------------------------------------------------
    seat_rows = []
    for m in MODELS:
        for seat, g in df[df.model == m].groupby("seat"):
            if seat == 0:
                continue
            p, lo, hi, n = rate_ci(g, B=B)
            seat_rows.append(dict(model=MODEL_NAMES[m], seat=int(seat), layer=g.layer.iloc[0], go_rate=p, lo=lo, hi=hi, n=n))
    t_seat = pd.DataFrame(seat_rows)
    tables["m9_seat_rates"] = t_seat
    cats = [f"seat {int(s)}" + ("\n(1st hand)" if s <= 6 else "\n(2nd hand)") for s in sorted(t_seat.seat.unique())]
    series = []
    for m in MODELS:
        sub = t_seat[t_seat.model == MODEL_NAMES[m]].sort_values("seat")
        series.append(dict(name=MODEL_NAMES[m], vals=list(sub.go_rate), lo=list(sub.lo), hi=list(sub.hi)))
    blocks += [("h3", "Does seat position matter?"),
               ("svg", charts.grouped_bars(cats, series, title="Check rate by seat (seats 1-6 hear the source, seats 7-12 hear a partner)"))]

    src_rows = []
    for m in MODELS:
        s = df[(df.model == m) & (df.layer == "first_hand")]
        for pid, g in s.groupby("source_persona_id"):
            p, lo, hi, n = rate_ci(g, B=B)
            src_rows.append(dict(model=MODEL_NAMES[m], source_persona_id=int(pid), source_persona=g.source_persona.iloc[0],
                                 layouts=sorted(g.layout_id.unique().tolist()), go_rate=p, lo=lo, hi=hi, n=n))
    t_src = pd.DataFrame(src_rows)
    tables["m9_source_persona_rates"] = t_src.assign(layouts=t_src.layouts.astype(str))
    f_rows = []
    for gi, m in enumerate(MODELS):
        for r in t_src[t_src.model == MODEL_NAMES[m]].itertuples():
            f_rows.append(dict(label=f"source {r.source_persona} - {MODEL_NAMES[m].split('-')[0]}", est=r.go_rate, lo=r.lo, hi=r.hi, group=gi))
    blocks += [("h3", "Does the identity of the source persona matter?"),
               ("p", "The persona in the source seat is set by the layout, and the two models ran different layouts, so model and source persona are partly confounded."),
               ("svg", charts.forest(f_rows, "first-hand check rate", xmin=0, xmax=1, zero=0.5, kind="pct", row_h=15, title="Check rate by source persona"))]
    for layer in ("first_hand", "second_hand"):
        for m in MODELS:
            s = df[(df.layer == layer) & (df.model == m)].reset_index(drop=True)
            fit, idx = _fit(s, ["seat"])
            chi, k, p = wald_joint(fit, idx["seat"])
            het_rows.append(dict(layer=layer, model=MODEL_NAMES[m], factor="seat", wald_chi2=chi, df=k, p=p))
            fit, idx = _fit(s, ["source_persona_id"])
            chi, k, p = wald_joint(fit, idx["source_persona_id"])
            het_rows.append(dict(layer=layer, model=MODEL_NAMES[m], factor="source persona", wald_chi2=chi, df=k, p=p))
    t_het = pd.DataFrame(het_rows)
    tables["m9_heterogeneity_tests"] = t_het
    blocks += [("table", t_het, "Joint Wald tests (knobs adjusted, cluster-robust by twin pair). Small p = the factor shifts checking.")]

    # ---- 3. variance decomposition ----------------------------------------------------------
    rows = []
    for layer in ("first_hand", "second_hand"):
        for m in MODELS:
            s = df[(df.layer == layer) & (df.model == m)].reset_index(drop=True)
            y = s.go.values
            p0 = y.mean()
            ll0 = float(np.sum(y * np.log(p0) + (1 - y) * np.log(1 - p0)))
            X, _ = design(s, KNOB_SPEC(s))
            base = logit(X, y)
            full_groups = ["persona", "seat", "source_persona_id"]
            full = _fit_naive(s, full_groups)

            def r2(ll):
                return 1 - ll / ll0

            row = dict(layer=layer, model=MODEL_NAMES[m], knobs_only=r2(base["loglik"]), all_factors=r2(full["loglik"]))
            for g in full_groups:
                rest = [x for x in full_groups if x != g]
                ll_rest = _fit_naive(s, rest)["loglik"]
                row[f"+{g}"] = r2(full["loglik"]) - r2(ll_rest)
            rows.append(row)
    t_var = pd.DataFrame(rows).rename(columns={"+persona": "added by persona", "+seat": "added by seat", "+source_persona_id": "added by source persona"})
    tables["m9_variance_share"] = t_var
    blocks += [("h3", "How much of checking is knobs vs who the agents are?"),
               ("p", "McFadden pseudo-R-squared (share of deviance explained). 'Knobs only' is the six source cues. "
                     "The 'added by' columns show how much each setup factor adds on top of everything else. If persona/seat/source add more than the knobs, setup noise dominates."),
               ("table", t_var, "Explained deviance by factor group (ignores clustering; descriptive)")]
    for r in t_var[t_var.layer == "first_hand"].to_dict("records"):
        summary.append(f"{r['model']} (first-hand): the six knobs explain {pct(r['knobs_only'], 1)} of check-decision deviance; "
                       f"persona adds {pct(r['added by persona'], 1)}, seat {pct(r['added by seat'], 1)}, "
                       f"source persona {pct(r['added by source persona'], 1)}.")

    # ---- 4. budget note --------------------------------------------------------------------------
    blocks += [("h3", "Budget"),
               ("p", "Every listener starts with the same $40 and the check costs a flat $5, so budget does not vary before the decision and cannot predict checking. "
                     "It only records the outcome (a GO leaves $35).")]
    return dict(id="m9", title="Metric 9 - Who checks", summary=summary, blocks=blocks, tables=tables)


def _fit_naive(s, groups):
    """Same as _fit but returns only the fit (no clustering needed for log-likelihood)."""
    spec = KNOB_SPEC(s)
    for g in groups:
        spec = spec + dummies(s[g], g)
    X, _ = design(s, spec)
    return logit(X, s.go.values, ridge=1e-4)
