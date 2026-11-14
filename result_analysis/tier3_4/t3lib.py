"""Shared helpers for the Tier 3 / Tier 4 (belief-based) analyses. numpy + pandas only.

Belief scores follow the repo spec (docs/04_metrics_and_judge.md):
  FACT, CHECKED_TRUE -> 1 | UNCERTAIN -> 0.5 | SKEPTICAL, CHECKED_FALSE -> 0
  NOT_MENTIONED is excluded from the conditional belief mean (and reported as an omission rate);
  sensitivity scores impute it as 0 (score_nm0) or 0.5 (score_nm5). Missing/invalid labels stay missing everywhere.
Truth discount (TD) = belief(truth twin) - belief(rumor twin), computed per twin pair.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
from t2lib import MODEL_NAMES, chi2_sf, design, dummies, load_listeners, norm_sf2, pct, read_listeners  # noqa: E402,F401

LABELS = ["FACT", "UNCERTAIN", "SKEPTICAL", "CHECKED_TRUE", "CHECKED_FALSE", "NOT_MENTIONED"]
SCORE = {"FACT": 1.0, "CHECKED_TRUE": 1.0, "UNCERTAIN": 0.5, "SKEPTICAL": 0.0, "CHECKED_FALSE": 0.0}
MODELS = ["deepseek_v4_flash", "qwen_3_8_flash"]
KNOBS = [  # (column, numerator level, denominator level, short label)
    ("closeness", "close_friend", "stranger", "Closeness (friend vs stranger)"),
    ("authority", "mayor", "citizen", "Authority (mayor vs citizen)"),
    ("reliability", "good_record", "poor_record", "Reliability (good vs poor record)"),
    ("wealth", "rich", "poor", "Wealth (rich vs poor)"),
    ("gender", "woman", "man", "Gender (woman vs man)"),
    ("age", "old", "young", "Age (old vs young)"),
]
PAIR_ATTRS = ["model", "cell_id", "layout_id", "rep_id", "source_persona_id", "closeness", "authority", "reliability",
              "wealth", "gender", "age", "identity"]
SCORES = {"primary": "score", "NOT_MENTIONED=0": "score_nm0", "NOT_MENTIONED=0.5": "score_nm5"}
LAYER_NAMES = {"first_hand": "First-hand", "second_hand": "Second-hand"}


# --------------------------------------------------------------------------- loading
def read_labels(paths):
    """Read label files (.csv or .jsonl) with columns run_id, seat (or seat_id / seat_id_private) and label (or choice).

    Extra columns are ignored. Torn or non-JSON lines in .jsonl files are skipped. Duplicates keep the last row.
    """
    frames = []
    for p in paths:
        if p.endswith(".jsonl"):
            rows = []
            for line in open(p):
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
            f = pd.DataFrame(rows)
        else:
            f = pd.read_csv(p)
        seat = [c for c in ("seat", "seat_id", "seat_id_private") if c in f.columns]
        lab = [c for c in ("label", "choice") if c in f.columns]
        if "run_id" not in f.columns or not seat or not lab:
            raise SystemExit(f"{p}: needs columns run_id, seat (or seat_id) and label; found {list(f.columns)}")
        frames.append(pd.DataFrame({"run_id": f["run_id"], "seat": pd.to_numeric(f[seat].bfill(axis=1).iloc[:, 0], errors="coerce"),
                                    "label": f[lab].bfill(axis=1).iloc[:, 0].astype(str).str.strip().str.upper()}))
    lab = pd.concat(frames, ignore_index=True).dropna(subset=["seat"])
    lab["seat"] = lab.seat.astype(int)
    bad = ~lab.label.isin(LABELS)
    if bad.any():
        print(f"  warning: {int(bad.sum())} label rows have values outside the rubric and are treated as missing "
              f"(e.g. {lab.label[bad].unique()[:4].tolist()})")
        lab = lab[~bad]
    return lab.drop_duplicates(["run_id", "seat"], keep="last").reset_index(drop=True)


def attach_scores(df, labels):
    d = df.merge(labels, on=["run_id", "seat"], how="left")
    nm = d.label == "NOT_MENTIONED"
    d["score"] = d.label.map(SCORE)
    d["score_nm0"] = d.score.where(~nm, 0.0)
    d["score_nm5"] = d.score.where(~nm, 0.5)
    d["labeled"] = d.label.notna().astype(int)
    d["omitted"] = nm.astype(int)
    d["certainty"] = 2 * (d.score - 0.5).abs()  # UNCERTAIN -> 0, any committed label -> 1
    return d


def coverage_table(d):
    g = d.groupby(["model", "layer", "condition"])
    t = g.agg(listeners=("labeled", "size"), labeled=("labeled", "sum"), omitted=("omitted", "sum")).reset_index()
    t["share_labeled"] = t.labeled / t.listeners
    t["omission_rate"] = t.omitted / t.labeled.clip(lower=1)
    t["model"] = t.model.map(lambda m: MODEL_NAMES.get(m, m))
    return t


# --------------------------------------------------------------------------- pair table
def pair_table(d, score="score", layer="first_hand", mask=None):
    """One row per twin pair: mean score in each twin (over listeners with a valid score), the truth discount, and pair attributes.

    mask: optional boolean Series aligned with d, restricting which listeners count (e.g. checkers only).
    td is NaN when either twin has no valid score; callers drop those rows and report the usable count.
    """
    sel = d.layer == layer
    if mask is not None:
        sel = sel & mask
    s = d[sel]
    m = s.pivot_table(index="pair_id", columns="condition", values=score, aggfunc="mean").reindex(columns=["rumor", "truth_twin"])
    n = s.pivot_table(index="pair_id", columns="condition", values=score, aggfunc="count").reindex(columns=["rumor", "truth_twin"])
    out = pd.DataFrame({"rumor_mean": m["rumor"], "truth_mean": m["truth_twin"], "n_rumor": n["rumor"].fillna(0), "n_truth": n["truth_twin"].fillna(0)})
    attrs = d.drop_duplicates("pair_id").set_index("pair_id")[PAIR_ATTRS]
    out = attrs.join(out, how="left").reset_index()
    out["td"] = out.truth_mean - out.rumor_mean
    return out


def usable(pt, col="td"):
    return pt.dropna(subset=[col])


# --------------------------------------------------------------------------- bootstrap
def boot_mean(x, B=2000, seed=0):
    """Percentile bootstrap of a mean over independent units (here: twin pairs). Returns (mean, lo, hi, n)."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    if n < 5:
        return float(x.mean()), np.nan, np.nan, n
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, n, size=(B, n))].mean(axis=1)
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), n


def boot_diff(x, y, B=2000, seed=0):
    """mean(x) - mean(y) for two independent groups (e.g. two models). Returns (diff, lo, hi, nx, ny)."""
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    y = np.asarray(y, float); y = y[np.isfinite(y)]
    if len(x) < 5 or len(y) < 5:
        return (float(x.mean() - y.mean()) if len(x) and len(y) else np.nan), np.nan, np.nan, len(x), len(y)
    rng = np.random.default_rng(seed)
    bx = x[rng.integers(0, len(x), size=(B, len(x)))].mean(axis=1)
    by = y[rng.integers(0, len(y), size=(B, len(y)))].mean(axis=1)
    d = bx - by
    return float(x.mean() - y.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), len(x), len(y)


def rate_diff_ci(df, flag, mask_a, mask_b, B=1000, seed=0):
    """Cluster-bootstrap (by twin pair) difference in the rate of a 0/1 column between two row sets."""
    from t2lib import diff_ci
    return diff_ci(df.assign(go=df[flag].astype(float)), np.asarray(mask_a), np.asarray(mask_b), B=B, seed=seed)


# --------------------------------------------------------------------------- regression helpers
def ols(X, y, cluster=None):
    """OLS with HC1 robust SEs, or cluster-robust SEs when cluster is given. X includes the intercept."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n, k = X.shape
    bread = np.linalg.pinv(X.T @ X)
    beta = bread @ X.T @ y
    resid = y - X @ beta
    scores = X * resid[:, None]
    if cluster is None:
        cov = bread @ (scores.T @ scores) @ bread * n / max(n - k, 1)
    else:
        _, idx = np.unique(cluster, return_inverse=True)
        G = idx.max() + 1
        sc = np.zeros((G, k))
        np.add.at(sc, idx, scores)
        cov = bread @ (sc.T @ sc) @ bread * (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    tss = float(((y - y.mean()) ** 2).sum())
    return dict(beta=beta, se=np.sqrt(np.diag(cov)), cov=cov, n=n, k=k, rank=int(np.linalg.matrix_rank(X)),
                r2=(1 - float(resid @ resid) / tss) if tss > 0 else np.nan, resid=resid)


def holm(p):
    """Holm-Bonferroni step-down adjusted p-values (NaN treated as 1)."""
    p = np.nan_to_num(np.asarray(p, float), nan=1.0)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(np.argsort(p)):
        run = max(run, (m - rank) * p[i])
        adj[i] = min(1.0, run)
    return adj


def norm_isf(p):
    """z such that P(Z > z) = p."""
    lo, hi = -12.0, 12.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if 0.5 * math.erfc(mid / math.sqrt(2)) > p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def code_pm(series, level_a):
    """Effect coding: +0.5 for level_a, -0.5 otherwise, so a coefficient equals the difference between levels."""
    return np.where(series.values == level_a, 0.5, -0.5)


CONTRASTS = [  # id, label, kind, factors, hypothesis from docs/01_experimental_spec.md section 9
    (1, "Closeness x truth discount", "main", ("closeness",), "close friends get a smaller TD than strangers"),
    (2, "Authority x truth discount", "main", ("authority",), "the mayor gets a smaller TD than a citizen"),
    (3, "Wealth x truth discount", "main", ("wealth",), "wealthy sources get a smaller TD than poor sources"),
    (4, "Reliability x truth discount", "main", ("reliability",), "good-record sources get a larger TD (baseline validation)"),
    (5, "Closeness x Reliability", "int", ("closeness", "reliability"), "friendship buffers against a poor record"),
    (6, "Authority x Reliability", "int", ("authority", "reliability"), "authority buffers against a poor record"),
    (7, "Wealth x Reliability", "int", ("wealth", "reliability"), "wealth buffers against a poor record"),
    (8, "Closeness x Authority", "int", ("closeness", "authority"), "sub- or super-additive when both apply"),
    (9, "Gender x truth discount", "main", ("gender",), "systematic difference between woman and man sources"),
    (10, "Age x truth discount", "main", ("age",), "systematic difference between old and young sources"),
]
_LEVEL_A = {k[0]: k[1] for k in KNOBS}


def fit_contrasts(pt, outcome="td", adjust=()):
    """Regress the pair-level outcome on the six effect-coded knobs plus the four planned interactions.

    adjust: extra pair-level columns to dummy-code as covariates (e.g. 'layout_id', 'rep_id', 'model').
    Returns (table of the 10 planned contrasts, fit dict). Interaction coefficients are difference-in-differences.
    """
    pt = pt.dropna(subset=[outcome]).reset_index(drop=True)
    x = {k: code_pm(pt[k], _LEVEL_A[k]) for k in _LEVEL_A}
    spec = [(f"{k}", x[k]) for k in _LEVEL_A]
    for cid, label, kind, fac, _ in CONTRASTS:
        if kind == "int":
            spec.append(("x:" + ":".join(fac), x[fac[0]] * x[fac[1]]))
    for col in adjust:
        if col in pt.columns and pt[col].nunique() > 1:
            spec += dummies(pt[col], col)
    X, names = design(pt, spec)
    fit = ols(X, pt[outcome].values)
    pos = {n: i for i, n in enumerate(names)}
    rows = []
    for cid, label, kind, fac, hyp in CONTRASTS:
        i = pos[fac[0]] if kind == "main" else pos["x:" + ":".join(fac)]
        b, s = fit["beta"][i], fit["se"][i]
        z = b / s if s > 0 else np.nan
        rows.append(dict(id=cid, contrast=label, estimate=b, se=s, ci_low=b - 1.96 * s, ci_high=b + 1.96 * s,
                         p=norm_sf2(z) if np.isfinite(z) else np.nan, hypothesis=hyp))
    t = pd.DataFrame(rows)
    t["p_holm"] = holm(t.p.values)
    t["significant_holm_05"] = t.p_holm < 0.05
    t["n_pairs"] = fit["n"]
    return t, fit


# --------------------------------------------------------------------------- variance components
def icc_anova(y, g, B=0, seed=0):
    """One-way random-effects ICC (ANOVA estimator, unbalanced groups) with optional cluster bootstrap CI.

    Returns (icc, lo, hi, n_groups, mean_group_size, design_effect).
    """
    y = np.asarray(y, float)
    g = np.asarray(g)
    ok = np.isfinite(y)
    y, g = y[ok], g[ok]
    _, idx = np.unique(g, return_inverse=True)
    G = idx.max() + 1
    n_i = np.bincount(idx, minlength=G).astype(float)
    s_i = np.bincount(idx, weights=y, minlength=G)
    q_i = np.bincount(idx, weights=y * y, minlength=G)

    def est(sel):
        n, s, q = n_i[sel], s_i[sel], q_i[sel]
        N, k = n.sum(), len(n)
        if k < 2 or N <= k:
            return np.nan
        m = s.sum() / N
        ssb = float((s * s / n).sum() - N * m * m)
        ssw = float((q - s * s / n).sum())
        msb, msw = ssb / (k - 1), ssw / (N - k)
        n0 = (N - float((n * n).sum()) / N) / (k - 1)
        den = msb + (n0 - 1) * msw
        return (msb - msw) / den if den > 0 else np.nan

    icc = est(np.arange(G))
    lo = hi = np.nan
    if B and G >= 5:
        rng = np.random.default_rng(seed)
        vals = np.array([est(rng.integers(0, G, G)) for _ in range(B)])
        vals = vals[np.isfinite(vals)]
        if len(vals) > 20:
            lo, hi = float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))
    nbar = float(n_i.mean())
    return icc, lo, hi, int(G), nbar, 1 + (nbar - 1) * icc if np.isfinite(icc) else np.nan


def spearman(a, b):
    a = pd.Series(a).rank().values
    b = pd.Series(b).rank().values
    if np.std(a) == 0 or np.std(b) == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def dna_name(r):
    return " / ".join([str(r["closeness"]).replace("_", " "), str(r["authority"]), str(r["reliability"]).replace("_", " "),
                       str(r["wealth"]), str(r["identity"]).replace("_", " ")])
