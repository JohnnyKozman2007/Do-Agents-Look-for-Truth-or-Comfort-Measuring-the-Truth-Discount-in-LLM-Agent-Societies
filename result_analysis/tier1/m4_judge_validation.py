"""Metric 4 - judge validation from the labeled data.

Three checks, none of which need another model call:
  1. Ground truth from the GO/SKIP log: a listener who paid to check read the board, so their call should be labeled CHECKED_*
     (truth twin -> CHECKED_TRUE, rumor twin -> CHECKED_FALSE). Recall, precision and direction accuracy of the CHECKED labels.
  2. Placebo (leakage) test: listeners who saw no poster cannot know whether the claim is true, so their label distribution must
     not differ between twins. A paired-twin permutation test checks that the judge is not reacting to anything but the dialogue.
  3. Optional agreement with a reference label set (a human audit or a second judge): Cohen's kappa and confusion matrix.
"""
import numpy as np
import pandas as pd

import charts
from t3lib import LABELS, LAYER_NAMES, MODEL_NAMES, MODELS, coverage_table, flag_rate_ci, kappa_stats, swap_test

CHECKED = ("CHECKED_TRUE", "CHECKED_FALSE")
KAPPA_TARGET = 0.85  # diagnostic benchmark from docs/08_analysis_and_audit.md
COLLAPSE = {"FACT": "believe", "CHECKED_TRUE": "believe", "UNCERTAIN": "uncertain", "SKEPTICAL": "disbelieve",
            "CHECKED_FALSE": "disbelieve", "NOT_MENTIONED": "not mentioned"}


def _mix_table(d):
    rows = []
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            for c in ("truth_twin", "rumor"):
                x = d[(d.model == m) & (d.layer == layer) & (d.condition == c) & (d.labeled == 1)]
                if len(x):
                    r = dict(model=MODEL_NAMES[m], layer=LAYER_NAMES[layer], twin=c, labeled=len(x))
                    r.update({k: float((x.label == k).mean()) for k in LABELS})
                    rows.append(r)
    return pd.DataFrame(rows)


def _ground_truth(d, B):
    rows = []
    for m in MODELS:
        for layer, defs in (("first_hand", [("own GO", lambda x: x.go == 1)]),
                            ("second_hand", [("own GO", lambda x: x.go == 1), ("own or partner GO", lambda x: (x.go == 1) | (x.partner_go == 1))])):
            x = d[(d.model == m) & (d.layer == layer) & (d.labeled == 1)].copy()
            if x.empty:
                continue
            x["chk"] = x.label.isin(CHECKED).astype(int)
            x["dir_ok"] = (((x.label == "CHECKED_TRUE") & (x.condition == "truth_twin")) | ((x.label == "CHECKED_FALSE") & (x.condition == "rumor"))).astype(int)
            for name, fn in defs:
                x["real"] = fn(x).astype(int)
                rec = flag_rate_ci(x, "chk", x.real == 1, B=B)
                pre = flag_rate_ci(x, "real", x.chk == 1, B=B)
                fa = flag_rate_ci(x, "chk", x.real == 0, B=B)
                both = x[(x.real == 1) & (x.chk == 1)]
                dr = flag_rate_ci(both, "dir_ok", None, B=B) if len(both) >= 5 else (np.nan, np.nan, np.nan, len(both))
                rows.append(dict(model=MODEL_NAMES[m], layer=LAYER_NAMES[layer], checked_means=name, listeners=len(x), truly_checked=int(x.real.sum()),
                                 recall=rec[0], recall_lo=rec[1], recall_hi=rec[2], precision=pre[0], precision_lo=pre[1], precision_hi=pre[2],
                                 false_alarm=fa[0], direction_accuracy=dr[0], direction_lo=dr[1], direction_hi=dr[2], direction_n=dr[3]))
    return pd.DataFrame(rows)


def _placebo(d, B=5000):
    rows, shares = [], []
    strata = [("first_hand", "first-hand listeners who skipped", lambda x: x.go == 0),
              ("second_hand", "second-hand listeners with no check by them or their partner", lambda x: (x.go == 0) & (x.partner_go == 0))]
    for m in MODELS:
        for layer, name, fn in strata:
            x = d[(d.model == m) & (d.layer == layer) & (d.labeled == 1)]
            x = x[fn(x)]
            if x.empty:
                continue
            g = x.groupby(["pair_id", "condition", "label"]).size().unstack(["condition", "label"], fill_value=0)
            if not {"truth_twin", "rumor"} <= set(g.columns.get_level_values(0)):
                continue
            pairs = g.index
            A = g["truth_twin"].reindex(columns=LABELS, fill_value=0).values
            R = g["rumor"].reindex(columns=LABELS, fill_value=0).values
            stat, p = swap_test(A, R, B=B)
            rows.append(dict(model=MODEL_NAMES[m], stratum=name, pairs=len(pairs), listeners_truth=int(A.sum()), listeners_rumor=int(R.sum()), statistic=stat, p_swap=p))
            for tw, arr in (("truth_twin", A), ("rumor", R)):
                s = dict(model=MODEL_NAMES[m], stratum=name, twin=tw)
                s.update({k: float(arr.sum(0)[i] / arr.sum()) for i, k in enumerate(LABELS)})
                shares.append(s)
    return pd.DataFrame(rows), pd.DataFrame(shares)


def _reference(d, ref, B):
    x = d[d.labeled == 1].merge(ref.rename(columns={"label": "ref_label"}), on=["run_id", "seat"], how="inner")
    rows = []
    strata = [("all", np.ones(len(x), bool))]
    for layer in ("first_hand", "second_hand"):
        strata.append((LAYER_NAMES[layer], (x.layer == layer).values))
    for c in ("truth_twin", "rumor"):
        strata.append((f"{c.replace('_twin', '')} twin", (x.condition == c).values))
    for m in MODELS:
        strata.append((MODEL_NAMES[m], (x.model == m).values))
    for name, mask in strata:
        s = x[mask]
        if len(s) < 10:
            continue
        for scheme, fa, fb in (("6 labels", s.label, s.ref_label), ("3 classes + not mentioned", s.label.map(COLLAPSE), s.ref_label.map(COLLAPSE)),
                               ("checked vs not", s.label.isin(CHECKED), s.ref_label.isin(CHECKED))):
            k, lo, hi, agree, n = kappa_stats(fa.values, fb.values, cluster=s.pair_id.values, B=B)
            rows.append(dict(stratum=name, scheme=scheme, n=n, agreement=agree, kappa=k, kappa_lo=lo, kappa_hi=hi, meets_target=bool(k >= KAPPA_TARGET)))
    return x, pd.DataFrame(rows)


def run(d, reference=None, B=500):
    blocks, tables, summary = [], {}, []
    cov = coverage_table(d)
    tables["m4_label_coverage"] = cov
    mix = _mix_table(d)
    tables["m4_label_mix"] = mix
    blocks += [("h3", "Label coverage and mix"),
               ("table", cov, "Listeners with a valid label, and omissions (NOT_MENTIONED) among them.", ("share_labeled", "omission_rate")),
               ("svg", charts.heatmap([f"{r.model.split('-')[0]} | {r.layer} | {r.twin}" for r in mix.itertuples()], list(LABELS),
                                      [[float(getattr(r, k)) for k in LABELS] for r in mix.itertuples()], kind="pct", cell=40,
                                      title="Label shares by model, layer and twin (x100)")),
               ("table", mix, "Share of each label among labeled listeners.", tuple(LABELS))]
    if d.labeled.mean() < 0.95:
        summary.append(f"Only {100 * d.labeled.mean():.0f}% of listeners have a valid label; every later estimate uses the labeled subset only.")

    # ---- 1. ground truth from the GO/SKIP log -------------------------------------------------------
    gt = _ground_truth(d, B)
    tables["m4_checked_vs_go_log"] = gt
    blocks += [("h3", "Do CHECKED labels match the GO/SKIP log?"),
               ("p", "Recall = share of listeners who really checked that the judge labeled CHECKED. Precision = share of CHECKED labels that were real checks. "
                     "Direction accuracy = among real checkers labeled CHECKED, truth-twin calls labeled CHECKED_TRUE and rumor-twin calls labeled CHECKED_FALSE. "
                     "Second-hand listeners may legitimately report that their partner checked, so they are scored two ways: only their own GO, or their own or their partner's GO."),
               ("table", gt, "Cluster bootstrap over twin pairs, 95% CIs.", ("recall", "recall_lo", "recall_hi", "precision", "precision_lo", "precision_hi", "false_alarm",
                                                                             "direction_accuracy", "direction_lo", "direction_hi"))]
    fr = [dict(label=f"{r.model.split('-')[0]} | {r.layer} | {r.checked_means}", est=r.recall, lo=r.recall_lo, hi=r.recall_hi, group=0) for r in gt.itertuples()]
    fr += [dict(label=f"{r.model.split('-')[0]} | {r.layer} | {r.checked_means}", est=r.precision, lo=r.precision_lo, hi=r.precision_hi, group=1) for r in gt.itertuples()]
    fr.sort(key=lambda r: r["label"])
    blocks.append(("svg", charts.forest(fr, "rate", xmin=0, xmax=1, zero=1.0, kind="pct", row_h=15, title="CHECKED-label recall (green) and precision (orange) against the GO log")))
    for r in gt[gt.layer == "First-hand"].itertuples():
        summary.append(f"{r.model}, first-hand: the judge labels {100 * r.recall:.0f}% of real checkers CHECKED (precision {100 * r.precision:.0f}%); "
                       f"direction is right on {100 * r.direction_accuracy:.0f}% of them.")

    # ---- 2. placebo ------------------------------------------------------------------------------------
    pl, pl_shares = _placebo(d)
    tables["m4_placebo_label_shares"] = pl_shares
    tables["m4_placebo_tests"] = pl
    blocks += [("h3", "Placebo: does the judge react to anything but the dialogue?"),
               ("p", "Listeners who saw no poster and heard of none cannot know whether the claim is true, so the twins' label distributions should match. "
                     "A paired-twin permutation test (twin identities swapped at random within each pair, 5,000 permutations) compares the distributions. "
                     "A small p-value means something other than what listeners said separates the twins (for example, judge context or a generation difference between twins)."),
               ("table", pl, "Statistic = squared distance between the two label-share vectors."),
               ("table", pl_shares, "Label shares by twin within each placebo stratum.", tuple(LABELS))]
    for r in pl.itertuples():
        summary.append(f"Placebo, {r.model}, {r.stratum}: permutation p = {r.p_swap:.3f}" + (" (twins differ more than chance; investigate)." if r.p_swap < 0.01 else " (no evidence of leakage)."))

    # ---- 3. reference agreement ----------------------------------------------------------------------------
    blocks.append(("h3", "Agreement with a reference label set"))
    if reference is None or len(reference) == 0:
        blocks.append(("p", "No reference labels were supplied. Pass a second label file (a human audit or another judge, same format) with --reference-labels to get Cohen's kappa, "
                            f"a confusion matrix and per-label precision and recall against it. The spec's diagnostic target is kappa {KAPPA_TARGET}."))
        summary.append("No reference labels supplied; judge agreement (kappa) was not computed.")
    else:
        x, K = _reference(d, reference, B)
        tables["m4_reference_agreement"] = K
        n = len(x)
        if n < 20:
            blocks.append(("p", f"Only {n} listeners overlap with the reference labels, too few for stable agreement estimates."))
        if len(K):
            blocks += [("p", f"{n:,} labeled listeners overlap with the reference. Kappa is Cohen's, with a cluster bootstrap over twin pairs. The target line is {KAPPA_TARGET} "
                             "(a diagnostic benchmark, not a pass/fail rule; the reference is not necessarily correct)."),
                       ("table", K, "Agreement by stratum and label granularity.", ("agreement",))]
            ks = K[K.scheme == "6 labels"]
            fr = [dict(label=r.stratum, est=r.kappa, lo=r.kappa_lo, hi=r.kappa_hi, group=0 if r.meets_target else 1) for r in ks.itertuples()]
            blocks.append(("svg", charts.forest(fr, "Cohen's kappa (6 labels)", xmin=0, xmax=1, zero=KAPPA_TARGET, kind="num", row_h=22, title="Judge vs reference: kappa by stratum (dashed = target)")))
            allk = ks[ks.stratum == "all"].iloc[0]
            summary.append(f"Kappa against the reference on {int(allk.n):,} listeners: {allk.kappa:.2f} (CI {allk.kappa_lo:.2f} to {allk.kappa_hi:.2f}) on 6 labels; "
                           f"{'meets' if allk.meets_target else 'is below'} the {KAPPA_TARGET} target.")
        cm = pd.crosstab(x.ref_label, x.label).reindex(index=LABELS, columns=LABELS, fill_value=0)
        cm.insert(0, "reference", cm.index)
        pr = pd.DataFrame({"label": LABELS, "judge_precision": [float((x.ref_label[x.label == k] == k).mean()) if (x.label == k).any() else np.nan for k in LABELS],
                           "judge_recall": [float((x.label[x.ref_label == k] == k).mean()) if (x.ref_label == k).any() else np.nan for k in LABELS],
                           "n_reference": [int((x.ref_label == k).sum()) for k in LABELS]})
        tables["m4_reference_confusion"] = cm.reset_index(drop=True)
        tables["m4_reference_per_label"] = pr
        blocks += [("table", cm.reset_index(drop=True), "Confusion counts: rows = reference label, columns = judge label."),
                   ("table", pr, "Judge precision and recall per label against the reference.", ("judge_precision", "judge_recall"))]
    return dict(id="m4", title="Metric 4 - Judge validation", summary=summary, blocks=blocks, tables=tables)
