"""Shared helpers for the Tier-2 analyses: data loading, bootstrap CIs, logistic regression.

Only numpy + pandas are required (no scipy / statsmodels).
"""
import hashlib
import json
import math
import os
import re

import numpy as np
import pandas as pd

RUN_RE = re.compile(r"(.+)__cell-(\d+)__layout-(\d+)__rep-(\d+)__(.+)")


# --------------------------------------------------------------------------- loading
def _persona_table(config):
    return {p["id"]: p for p in config["personas"]}


def load_listeners(data_dir, progress=True):
    """One row per listener per town (12 per town) from every town.json under data_dir."""
    runs = sorted(d for d in os.listdir(data_dir) if RUN_RE.match(d))
    if not runs:
        raise SystemExit(f"no run folders found in {data_dir}")
    personas = _persona_table(json.load(open(os.path.join(data_dir, runs[0], "config.json"))))
    rows = []
    for i, d in enumerate(runs):
        t = json.load(open(os.path.join(data_dir, d, "town.json")))
        m = RUN_RE.match(d)
        knobs = t["knobs"]
        gender, age = knobs["identity"].split("_")
        seat_persona = {int(k): v for k, v in t["seating_assignment"].items()}
        base = dict(
            run_id=t["run_id"], pair_id=t["pair_id"], model=t["model_key"], condition=t["condition_type"],
            cell_id=t["cell_id"], layout_id=t["layout_id"], rep_id=t["repetition_id"],
            announced_artist=t["announced_artist"], real_artist=t["real_artist"],
            source_persona_id=t["source_persona_id"], source_persona=personas[t["source_persona_id"]]["name"],
            closeness=knobs["closeness"], authority=knobs["authority"], reliability=knobs["reliability"],
            wealth=knobs["wealth"], identity=knobs["identity"], gender=gender, age=age,
            run_status=t["run_status"],
        )
        # partner map: second-hand seat -> first-hand seat
        fh_of = {p["second_hand_seat"]: p["first_hand_seat"] for p in t["catch_up_pairs"]}
        ev = {e["second_hand_seat"]: e for e in t["scene_3_poster_evidence_passed"]}
        fh_dec = {x["seat_id"]: x for x in t["scene_2_first_hand_decisions"]}
        for layer, key in (("first_hand", "scene_2_first_hand_decisions"), ("second_hand", "scene_4_second_hand_decisions")):
            for x in t[key]:
                seat = x["seat_id"]
                pid = seat_persona[seat]
                r = dict(base, layer=layer, seat=seat, persona_id=pid, persona=personas[pid]["name"],
                         occupation=personas[pid]["occupation"], style=personas[pid]["conversational_style"],
                         decision=x["decision"], go=int(x["decision"] == "GO"), parse_status=x["parse_status"],
                         malformed=int(x["parse_status"] != "valid"))
                if layer == "second_hand":
                    ps = fh_of[seat]
                    r.update(partner_seat=ps, partner_persona=personas[seat_persona[ps]]["name"],
                             partner_go=int(fh_dec[ps]["decision"] == "GO"),
                             evidence_passed=int(bool(ev[seat]["evidence_passed"])))
                rows.append(r)
        if progress and (i + 1) % 200 == 0:
            print(f"  loaded {i + 1}/{len(runs)} towns", flush=True)
    return pd.DataFrame(rows)


def read_listeners(data_dirs, out_dir, refresh=False, progress=True):
    """Listener rows from one or more shard folders (cached per set of folders)."""
    dirs = [os.path.abspath(d) for d in data_dirs]
    key = hashlib.md5("|".join(sorted(dirs)).encode()).hexdigest()[:8]
    cache = os.path.join(out_dir, f"listeners_{key}.csv")
    if os.path.exists(cache) and not refresh:
        print(f"  using cached {cache}")
        df = pd.read_csv(cache)
    else:
        df = pd.concat([load_listeners(d, progress=progress) for d in dirs], ignore_index=True)
        df.to_csv(cache, index=False)
    dup = df.duplicated(["run_id", "seat"]).sum()
    if dup:
        raise SystemExit(f"{dup} duplicated (run_id, seat) rows across the data folders; the shards must not overlap")
    return df


# --------------------------------------------------------------------------- bootstrap
def boot_groups(df, masks, fn, B=2000, seed=0, cluster="pair_id"):
    """Cluster bootstrap of fn(rates) where rates[g] = mean(go) over rows with masks[g].

    masks: list of boolean arrays aligned with df. Returns (point, lo, hi).
    """
    cl_codes, cl_idx = np.unique(df[cluster].values, return_inverse=True)
    C = len(cl_codes)
    y = df["go"].values.astype(float)
    S = np.zeros((C, len(masks)))
    N = np.zeros((C, len(masks)))
    for g, m in enumerate(masks):
        m = np.asarray(m)
        np.add.at(S[:, g], cl_idx[m], y[m])
        np.add.at(N[:, g], cl_idx[m], 1.0)

    def stat(s, n):
        with np.errstate(invalid="ignore", divide="ignore"):
            return fn(s / n)

    point = stat(S.sum(0), N.sum(0))
    rng = np.random.default_rng(seed)
    W = rng.multinomial(C, np.full(C, 1.0 / C), size=B).astype(float)  # B x C
    bs = W @ S, W @ N
    with np.errstate(invalid="ignore", divide="ignore"):
        vals = np.array([fn(bs[0][b] / bs[1][b]) for b in range(B)])
    vals = vals[np.isfinite(vals)]
    if len(vals) < 20:
        return point, np.nan, np.nan
    return point, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def rate_ci(df, **kw):
    m = np.ones(len(df), bool)
    p, lo, hi = boot_groups(df, [m], lambda r: r[0], **kw)
    return p, lo, hi, len(df)


def diff_ci(df, mask_a, mask_b, **kw):
    """rate(a) - rate(b) with cluster-bootstrap CI."""
    p, lo, hi = boot_groups(df, [mask_a, mask_b], lambda r: r[0] - r[1], **kw)
    return p, lo, hi


def did_ci(df, a, b, **kw):
    """Difference-in-differences of binary a,b boolean arrays: [r(a1,b1)-r(a0,b1)] - [r(a1,b0)-r(a0,b0)]."""
    a = np.asarray(a); b = np.asarray(b)
    masks = [a & b, ~a & b, a & ~b, ~a & ~b]
    return boot_groups(df, masks, lambda r: (r[0] - r[1]) - (r[2] - r[3]), **kw)


# --------------------------------------------------------------------------- logistic regression
def chi2_sf(x, k):
    """Survival function of chi-square(k) (regularized upper incomplete gamma Q(k/2, x/2))."""
    if x <= 0:
        return 1.0
    a, x = k / 2.0, x / 2.0
    if x < a + 1:  # series for P
        term = s = 1.0 / a
        n = a
        for _ in range(500):
            n += 1
            term *= x / n
            s += term
            if abs(term) < abs(s) * 1e-12:
                break
        P = s * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return max(0.0, 1.0 - P)
    # continued fraction for Q
    tiny = 1e-300
    b = x + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-12:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def norm_sf2(z):
    """Two-sided normal p-value."""
    return math.erfc(abs(z) / math.sqrt(2))


def logit(X, y, cluster=None, ridge=1e-6, maxit=100):
    """Logistic regression via IRLS with cluster-robust (sandwich) covariance.

    Returns dict(beta, se, cov, loglik, n). X must include an intercept column.
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    k = X.shape[1]
    beta = np.zeros(k)
    for _ in range(maxit):
        eta = np.clip(X @ beta, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        W = p * (1 - p)
        H = X.T @ (X * W[:, None]) + ridge * np.eye(k)
        g = X.T @ (y - p) - ridge * beta
        step = np.linalg.solve(H, g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    eta = np.clip(X @ beta, -30, 30)
    p = 1 / (1 + np.exp(-eta))
    W = p * (1 - p)
    H = X.T @ (X * W[:, None]) + ridge * np.eye(k)
    bread = np.linalg.inv(H)
    if cluster is None:
        cov = bread
    else:
        _, idx = np.unique(cluster, return_inverse=True)
        G = idx.max() + 1
        scores = (X * (y - p)[:, None])
        sc = np.zeros((G, k))
        np.add.at(sc, idx, scores)
        meat = sc.T @ sc
        cov = bread @ meat @ bread * (G / max(G - 1, 1))
    ll = float(np.sum(y * np.log(np.clip(p, 1e-12, 1)) + (1 - y) * np.log(np.clip(1 - p, 1e-12, 1))))
    return dict(beta=beta, se=np.sqrt(np.diag(cov)), cov=cov, loglik=ll, n=len(y))


def design(df, spec):
    """Build (X, names). spec: list of (name, array_or_series)."""
    cols = [np.ones(len(df))]
    names = ["intercept"]
    for name, arr in spec:
        cols.append(np.asarray(arr, float))
        names.append(name)
    return np.column_stack(cols), names


def dummies(series, prefix, drop_first=True):
    cats = sorted(pd.unique(series))
    out = []
    for c in (cats[1:] if drop_first else cats):
        out.append((f"{prefix}={c}", (series == c).values.astype(float)))
    return out


def or_table(fit, names, skip=("intercept",)):
    rows = []
    for n, b, s in zip(names, fit["beta"], fit["se"]):
        if n in skip:
            continue
        z = b / s if s > 0 else np.nan
        rows.append(dict(term=n, odds_ratio=math.exp(b), lo=math.exp(b - 1.96 * s), hi=math.exp(b + 1.96 * s),
                         p=norm_sf2(z) if np.isfinite(z) else np.nan))
    return pd.DataFrame(rows)


def wald_joint(fit, idx):
    b = fit["beta"][idx]
    V = fit["cov"][np.ix_(idx, idx)]
    chi = float(b @ np.linalg.pinv(V) @ b)
    return chi, len(idx), chi2_sf(chi, len(idx))


def pct(x, d=0):
    return "n/a" if x is None or not np.isfinite(x) else f"{100 * x:.{d}f}%"


MODEL_NAMES = {"deepseek_v4_flash": "DeepSeek-V4-Flash", "qwen_3_8_flash": "Qwen3.8-Flash"}
