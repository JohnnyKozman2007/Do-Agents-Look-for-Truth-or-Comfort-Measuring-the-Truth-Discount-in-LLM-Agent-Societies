"""Metric 16 - model comparison, belief side (the behavioral side is Tier 2 metrics 7-9; a compact recap is included)."""
import numpy as np
import pandas as pd

from t3lib import LAYER_NAMES, LABELS, MODEL_NAMES, MODELS, boot_diff, boot_mean, fit_contrasts, norm_sf2, pair_table, usable
import charts


def run(d, B=2000):
    blocks, tables, summary = [], {}, []
    if not all((d.model == m).any() for m in MODELS):
        return dict(id="m16", title="Metric 16 - Model comparison", summary=["Skipped: needs both models in the data."], blocks=[], tables={})
    a, b = MODELS
    # ---- TD by model and layer -----------------------------------------------------------------------
    rows = []
    for layer in ("first_hand", "second_hand"):
        ua = usable(pair_table(d[d.model == a], "score", layer))
        ub = usable(pair_table(d[d.model == b], "score", layer))
        for m, u in ((a, ua), (b, ub)):
            td = boot_mean(u.td, B=B)
            rows.append(dict(layer=LAYER_NAMES[layer], model=MODEL_NAMES[m], pairs_usable=td[3], td=td[0], lo=td[1], hi=td[2]))
        dd = boot_diff(ua.td, ub.td, B=B)
        rows.append(dict(layer=LAYER_NAMES[layer], model=f"{MODEL_NAMES[a]} minus {MODEL_NAMES[b]}", pairs_usable=dd[3] + dd[4], td=dd[0], lo=dd[1], hi=dd[2]))
    t = pd.DataFrame(rows)
    tables["m16_td_by_model"] = t
    f = [dict(label=f"{r.layer} | {r.model}", est=r.td, lo=r.lo, hi=r.hi, group=2 if "minus" in r.model else (0 if r.model == MODEL_NAMES[a] else 1)) for r in t.itertuples()]
    blocks += [("h3", "Truth discount by model"),
               ("svg", charts.forest(f, "truth discount (belief points)", kind="signed", row_h=21, title="Truth discount by model and layer")),
               ("table", t, "Bootstrap over twin pairs (models never share pairs, so differences use independent resampling).")]
    for r in t[t.model.str.contains("minus")].itertuples():
        summary.append(f"{r.layer} TD, {r.model}: {r.td:+.3f} (CI {r.lo:+.3f} to {r.hi:+.3f}).")

    # ---- belief label mix and omissions ---------------------------------------------------------------
    rows = []
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            for c in ("truth_twin", "rumor"):
                x = d[(d.model == m) & (d.layer == layer) & (d.condition == c) & (d.labeled == 1)]
                r = dict(model=MODEL_NAMES[m], layer=LAYER_NAMES[layer], twin=c, labeled=len(x))
                r.update({k: float((x.label == k).mean()) if len(x) else np.nan for k in LABELS})
                rows.append(r)
    t2 = pd.DataFrame(rows)
    tables["m16_label_mix"] = t2
    blocks += [("h4", "Label mix by model, layer and twin"), ("table", t2, "Share of labeled listeners.", tuple(LABELS))]

    # ---- do the planned contrasts replicate across models? ---------------------------------------------
    fa = fit_contrasts(usable(pair_table(d[d.model == a], "score", "first_hand")))[0]
    fb = fit_contrasts(usable(pair_table(d[d.model == b], "score", "first_hand")))[0]
    z = (fa.estimate - fb.estimate) / np.sqrt(fa.se ** 2 + fb.se ** 2)
    cmp_ = pd.DataFrame({"id": fa.id, "contrast": fa.contrast, f"est_{MODEL_NAMES[a]}": fa.estimate, f"est_{MODEL_NAMES[b]}": fb.estimate,
                         "difference": fa.estimate - fb.estimate, "p_difference": [norm_sf2(x) if np.isfinite(x) else np.nan for x in z],
                         f"holm_sig_{MODEL_NAMES[a].split('-')[0]}": fa.significant_holm_05, f"holm_sig_{MODEL_NAMES[b].split('-')[0]}": fb.significant_holm_05})
    tables["m16_contrast_replication"] = cmp_
    f = []
    for i, (name, tt) in enumerate(((MODEL_NAMES[a], fa), (MODEL_NAMES[b], fb))):
        for r in tt.itertuples():
            f.append(dict(label=f"{r.id}. {r.contrast.replace(' x truth discount', '')} | {name.split('-')[0]}", est=r.estimate, lo=r.ci_low, hi=r.ci_high, group=i))
    f.sort(key=lambda r: int(r["label"].split(".")[0]))
    blocks += [("h3", "Do the planned effects replicate across models?"),
               ("svg", charts.forest(f, "difference in truth discount", kind="signed", row_h=15, title="Planned contrasts by model (first-hand)")),
               ("table", cmp_, "p_difference tests whether the two models' estimates differ (independent samples, normal approximation).")]
    same = int(((fa.significant_holm_05 == fb.significant_holm_05)).sum())
    summary.append(f"The Holm significance verdict agrees across models for {same} of 10 planned contrasts.")

    # ---- behavior recap and design balance ----------------------------------------------------------------
    beh = d.groupby(["model", "layer"]).go.mean().reset_index()
    beh["model"] = beh.model.map(MODEL_NAMES)
    beh = beh.rename(columns={"go": "check_rate"})
    tables["m16_check_rate_recap"] = beh
    bal = d.drop_duplicates("pair_id").groupby(["model", "rep_id"]).size().unstack(fill_value=0).reset_index()
    bal["model"] = bal.model.map(MODEL_NAMES)
    lay = d.drop_duplicates("pair_id").groupby("model").layout_id.nunique().rename("layouts_covered").reset_index()
    lay["model"] = lay.model.map(MODEL_NAMES)
    tables["m16_design_balance"] = bal
    blocks += [("h4", "Behavioral recap (full analysis: Tier 2)"), ("table", beh, "GO rate by model and layer.", ("check_rate",)),
               ("h4", "Design balance"), ("p", "Twin pairs per model and repetition, and layouts covered per model. If a model covers only some layouts, model and source persona are confounded."),
               ("table", bal, "Twin pairs per model x repetition."), ("table", lay, "Distinct layouts covered per model.")]
    return dict(id="m16", title="Metric 16 - Model comparison", summary=summary, blocks=blocks, tables=tables)
