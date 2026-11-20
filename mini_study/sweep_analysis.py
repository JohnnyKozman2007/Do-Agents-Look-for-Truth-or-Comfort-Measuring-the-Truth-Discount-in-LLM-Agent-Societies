#!/usr/bin/env python3
"""Analyze the checking-price sweep: P(GO) by price for each model, how cue effects change with price, and the
"half price" (fare at which half of listeners still check). Writes runs/sweep/sweep_report.md, sweep_summary.csv and
sweep_report.html (inline SVG, no external assets).

Inputs: runs/sweep/<tag>_price<p>/results.jsonl for p in PRICES (and runs/<tag>_full for the $5 baseline),
plus the design files (for the cue levels of each prompt). Requires numpy and pandas.
"""
import json
import os
from html import escape

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
PRICES = [0, 1, 5, 15, 35]
MODELS = [("terra", "GPT-6.1 Terra"), ("sol", "GPT-6.1 Sol"), ("luna", "GPT-6 Luna"),
          ("sonnet", "Claude Sonnet 5.5"), ("opus", "Claude Opus 5.5"),
          ("deepseek", "DeepSeek-V4-Flash"), ("qwen", "Qwen3.8-Flash")]  # models with no results are skipped
COLORS = ["#2f6f5e", "#c46a2d", "#4a6fa5", "#8a5a9c", "#b0413e", "#5b7f2a", "#a07c1e"]
CUES = [("reliability", "good_record", "poor_record"), ("closeness", "close_friend", "stranger"),
        ("authority", "mayor", "citizen"), ("wealth", "rich", "poor"), ("gender", "woman", "man"), ("age", "old", "young")]
B = 1000


def results_dir(tag, p):
    return os.path.join(RUNS, f"{tag}_full") if p == 5 else os.path.join(RUNS, "sweep", f"{tag}_price{p}")


def load():
    design = {}
    for l in open(os.path.join(RUNS, "design_full", "design.jsonl")):
        it = json.loads(l)
        design[it["item_id"]] = {k: it[k] for k in ("persona_id", "cell_id", "layout_id") + tuple(c for c, _, _ in CUES)}
    rows = []
    for tag, name in MODELS:
        for p in PRICES:
            f = os.path.join(results_dir(tag, p), "results.jsonl")
            if not os.path.exists(f):
                continue
            for l in open(f):
                try:
                    r = json.loads(l)
                except Exception:
                    continue
                rows.append(dict(model=name, price=p, item_id=r["item_id"], go=int(r["decision"] == "GO"),
                                 malformed=int(r["parse_status"] != "valid"), **design[r["item_id"]]))
    return pd.DataFrame(rows).drop_duplicates(["model", "price", "item_id"], keep="last")


def boot_rate(df, seed=0):
    """P(GO) with a bootstrap over listener personas."""
    g = df.groupby("persona_id").go.agg(["sum", "count"]).values
    p = g[:, 0].sum() / g[:, 1].sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(g), size=(B, len(g)))
    sims = g[idx, 0].sum(1) / g[idx, 1].sum(1)
    return p, np.percentile(sims, 2.5), np.percentile(sims, 97.5)


def boot_diff(df, col, level, seed=0):
    """P(GO | col == level) - P(GO | otherwise), bootstrap over personas."""
    df = df.assign(a=(df[col] == level).astype(int))
    g = df.groupby("persona_id").apply(lambda x: pd.Series({"sa": x.go[x.a == 1].sum(), "na": (x.a == 1).sum(),
                                                             "sb": x.go[x.a == 0].sum(), "nb": (x.a == 0).sum()}),
                                       include_groups=False).values
    est = g[:, 0].sum() / g[:, 1].sum() - g[:, 2].sum() / g[:, 3].sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(g), size=(B, len(g)))
    s = g[idx].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        sims = s[:, 0] / s[:, 1] - s[:, 2] / s[:, 3]
    sims = sims[np.isfinite(sims)]
    return est, np.percentile(sims, 2.5), np.percentile(sims, 97.5)


def logit_fit(x, y, iters=50):
    X = np.column_stack([np.ones(len(x)), x])
    b = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
        W = p * (1 - p) + 1e-9
        b += np.linalg.solve(X.T @ (X * W[:, None]) + 1e-6 * np.eye(2), X.T @ (y - p))
    return b


def half_price(df):
    """Fare at which P(GO) = 50%, from a logistic fit of GO on log(1 + price). Bootstrap over personas."""
    x, y = np.log1p(df.price.values), df.go.values

    def est(xx, yy):
        if yy.min() == yy.max():
            return np.nan
        b0, b1 = logit_fit(xx, yy)
        if b1 >= 0:
            return np.nan  # checking does not fall with price
        return float(np.expm1(-b0 / b1))

    h = est(x, y)
    pers = df.persona_id.values
    ids = np.unique(pers)
    by = {i: np.where(pers == i)[0] for i in ids}
    rng = np.random.default_rng(1)
    sims = []
    for _ in range(300):
        take = np.concatenate([by[i] for i in rng.choice(ids, len(ids))])
        v = est(x[take], y[take])
        if np.isfinite(v):
            sims.append(v)
    lo, hi = (np.percentile(sims, 2.5), np.percentile(sims, 97.5)) if len(sims) > 50 else (np.nan, np.nan)
    return h, lo, hi


# ------------------------------------------------------------------------------------------------ svg
def line_chart(series, title, ylabel, ymin, ymax, pct=True, zero=None):
    W, H, ml, mr, mt, mb = 640, 330, 56, 150, 34, 46
    pw, ph = W - ml - mr, H - mt - mb
    xs = {p: ml + pw * i / (len(PRICES) - 1) for i, p in enumerate(PRICES)}  # evenly spaced price levels
    Y = lambda v: mt + ph - ph * (v - ymin) / (ymax - ymin)
    o = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{escape(title)}">',
         f'<text x="{ml}" y="18" class="t-title">{escape(title)}</text>']
    for i in range(5):
        v = ymin + (ymax - ymin) * i / 4
        o.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/>')
        o.append(f'<text x="{ml - 6}" y="{Y(v) + 4:.1f}" class="t-axis" text-anchor="end">{(f"{100 * v:.0f}%" if pct else f"{100 * v:+.0f}")}</text>')
    if zero is not None:
        o.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{Y(zero):.1f}" y2="{Y(zero):.1f}" class="zero"/>')
    for p, x in xs.items():
        o.append(f'<text x="{x:.1f}" y="{mt + ph + 18}" class="t-axis" text-anchor="middle">{"free" if p == 0 else f"${p}"}</text>')
    o.append(f'<text x="{ml + pw / 2:.1f}" y="{H - 6}" class="t-axis" text-anchor="middle">bus fare (of a $40 weekly budget)</text>')
    o.append(f'<text transform="translate(14,{mt + ph / 2:.1f}) rotate(-90)" class="t-axis" text-anchor="middle">{escape(ylabel)}</text>')
    labels = []
    for k, (name, pts) in enumerate(series):
        c = COLORS[k % len(COLORS)]
        pts = [(p, v, lo, hi) for p, v, lo, hi in pts if np.isfinite(v)]
        for p, v, lo, hi in pts:
            if np.isfinite(lo):
                o.append(f'<line x1="{xs[p]:.1f}" x2="{xs[p]:.1f}" y1="{Y(min(hi, ymax)):.1f}" y2="{Y(max(lo, ymin)):.1f}" stroke="{c}" stroke-opacity=".35" stroke-width="5" stroke-linecap="round"/>')
        o.append('<polyline fill="none" stroke="{}" stroke-width="2.2" points="{}"/>'.format(c, " ".join(f"{xs[p]:.1f},{Y(v):.1f}" for p, v, _, _ in pts)))
        for p, v, _, _ in pts:
            o.append(f'<circle cx="{xs[p]:.1f}" cy="{Y(v):.1f}" r="3.5" fill="{c}"><title>{escape(name)} at {"free" if p == 0 else f"${p}"}: {(f"{100 * v:.0f}%" if pct else f"{100 * v:+.0f} pp")}</title></circle>')
        if pts:
            labels.append([Y(pts[-1][1]) + 4, name, c])
    labels.sort()
    for i in range(1, len(labels)):  # push overlapping end labels apart
        labels[i][0] = max(labels[i][0], labels[i - 1][0] + 13)
    shift = max(0, labels[-1][0] - (H - 4)) if labels else 0
    for y, name, c in labels:
        o.append(f'<text x="{ml + pw + 10}" y="{y - shift:.1f}" class="t-label" fill="{c}">{escape(name)}</text>')
    o.append("</svg>")
    return "".join(o)


def main():
    d = load()
    if d.empty:
        raise SystemExit("no results found")
    have = d.groupby(["model", "price"]).size().unstack(fill_value=0)
    rows = []
    for name in [n for _, n in MODELS if n in set(d.model)]:
        for p in PRICES:
            s = d[(d.model == name) & (d.price == p)]
            if s.empty:
                continue
            r, lo, hi = boot_rate(s)
            row = dict(model=name, price=p, n=len(s), malformed=int(s.malformed.sum()), go_rate=r, go_lo=lo, go_hi=hi)
            for col, a, b in CUES[:2]:
                e, l, h = boot_diff(s, col, a)
                row.update({f"{col}_effect": e, f"{col}_lo": l, f"{col}_hi": h})
            for rel in ("good_record", "poor_record"):
                for clo in ("close_friend", "stranger"):
                    x = s[(s.reliability == rel) & (s.closeness == clo)]
                    row[f"go_{rel.split('_')[0]}_{clo.split('_')[0]}"] = x.go.mean() if len(x) else np.nan
            rows.append(row)
    T = pd.DataFrame(rows)
    os.makedirs(os.path.join(RUNS, "sweep"), exist_ok=True)
    T.to_csv(os.path.join(RUNS, "sweep", "sweep_summary.csv"), index=False)

    hp = []
    for name in T.model.unique():
        s = d[d.model == name]
        h, lo, hi = half_price(s) if s.price.nunique() >= 3 else (np.nan, np.nan, np.nan)
        hp.append(dict(model=name, half_price=h, lo=lo, hi=hi, free=T[(T.model == name) & (T.price == 0)].go_rate.max(),
                       at35=T[(T.model == name) & (T.price == 35)].go_rate.max()))
    H = pd.DataFrame(hp)
    H.to_csv(os.path.join(RUNS, "sweep", "sweep_half_price.csv"), index=False)

    # ---- markdown --------------------------------------------------------------------------------------
    def pc(v):
        return "n/a" if not np.isfinite(v) else f"{100 * v:.0f}%"

    def pp(v, lo, hi):
        return "n/a" if not np.isfinite(v) else f"{100 * v:+.0f} [{100 * lo:+.0f}, {100 * hi:+.0f}]"

    names = list(T.model.unique())
    L = ["# Checking-price sweep\n", "Same 576 first-hand prompts per model at each bus fare (budget stays $40). "
         "95% CIs bootstrap over the 13 listener personas.\n", "## P(GO) by fare\n",
         "| model | " + " | ".join("free" if p == 0 else f"${p}" for p in PRICES) + " |", "|---|" + "---|" * len(PRICES)]
    for n in names:
        L.append(f"| {n} | " + " | ".join(pc(T[(T.model == n) & (T.price == p)].go_rate.max()) if ((T.model == n) & (T.price == p)).any() else "-" for p in PRICES) + " |")
    for col, a, b in CUES[:2]:
        L += [f"\n## {col.capitalize()} effect by fare (P(GO) {a} minus {b}, percentage points)\n",
              "| model | " + " | ".join("free" if p == 0 else f"${p}" for p in PRICES) + " |", "|---|" + "---|" * len(PRICES)]
        for n in names:
            cells = []
            for p in PRICES:
                x = T[(T.model == n) & (T.price == p)]
                cells.append(pp(x[f"{col}_effect"].iloc[0], x[f"{col}_lo"].iloc[0], x[f"{col}_hi"].iloc[0]) if len(x) else "-")
            L.append(f"| {n} | " + " | ".join(cells) + " |")
    L += ["\n## Half price (fare at which half of listeners still check)\n",
          "From a logistic fit of GO on log(1 + fare); 'n/a' when checking never crosses 50% or does not fall with price.\n",
          "| model | half price | 95% CI | P(GO) free | P(GO) $35 |", "|---|---|---|---|---|"]
    for r in H.itertuples():
        hp_txt = "n/a" if not np.isfinite(r.half_price) else f"${r.half_price:.1f}"
        ci = "n/a" if not np.isfinite(r.lo) else f"${r.lo:.1f} to ${r.hi:.1f}"
        L.append(f"| {r.model} | {hp_txt} | {ci} | {pc(r.free)} | {pc(r.at35)} |")
    L += ["\n## Coverage\n", "Answers per model and fare (576 expected):\n", have.to_string(), "",
          f"Malformed answers (counted as SKIP): {int(T.malformed.sum())}."]
    open(os.path.join(RUNS, "sweep", "sweep_report.md"), "w").write("\n".join(L) + "\n")

    # ---- html --------------------------------------------------------------------------------------------
    s1 = [(n, [(p, *T[(T.model == n) & (T.price == p)][["go_rate", "go_lo", "go_hi"]].iloc[0]) for p in PRICES if ((T.model == n) & (T.price == p)).any()]) for n in names]
    charts = [line_chart(s1, "How often each model pays to check, by fare", "P(GO)", 0, 1)]
    for col, a, b in CUES[:2]:
        sr = [(n, [(p, *T[(T.model == n) & (T.price == p)][[f"{col}_effect", f"{col}_lo", f"{col}_hi"]].iloc[0]) for p in PRICES if ((T.model == n) & (T.price == p)).any()]) for n in names]
        vals = [v for _, pts in sr for _, v, lo, hi in pts for v in (lo, hi) if np.isfinite(v)]
        lim = max(0.1, np.ceil(max(abs(min(vals)), abs(max(vals))) * 10) / 10) if vals else 0.5
        lab = {"reliability": "good record minus poor record", "closeness": "close friend minus stranger"}[col]
        charts.append(line_chart(sr, f"{col.capitalize()} effect on checking, by fare ({lab})", "difference in P(GO), pp", -lim, lim, pct=False, zero=0))
    css = """:root{--bg:#fbfaf7;--card:#fff;--fg:#1f2328;--muted:#656d76;--line:#e4e1da;--grid:#ecebe6}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14171a;--card:#1c2024;--fg:#e6e8ea;--muted:#9aa3ab;--line:#2c3238;--grid:#2a3036}}
:root[data-theme=dark]{--bg:#14171a;--card:#1c2024;--fg:#e6e8ea;--muted:#9aa3ab;--line:#2c3238;--grid:#2a3036}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:20px 16px 60px}h1{font-size:24px}h2{font-size:18px;margin-top:28px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;margin:12px 0}
svg.chart{width:100%;height:auto}.t-axis{font-size:11px;fill:var(--muted)}.t-title{font-size:13px;font-weight:600;fill:var(--fg)}.t-label{font-size:11px;font-weight:600}
.grid{stroke:var(--grid)}.zero{stroke:var(--muted);stroke-dasharray:3 3}
table{border-collapse:collapse;width:100%;font-size:13px;background:var(--card)}th,td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:right}th:first-child,td:first-child{text-align:left}
.tbl{overflow-x:auto}.muted{color:var(--muted)}"""

    def html_table(header, body):
        return '<div class="tbl"><table><thead><tr>' + "".join(f"<th>{escape(h)}</th>" for h in header) + "</tr></thead><tbody>" + \
               "".join("<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>"

    go_tab = html_table(["model"] + ["free" if p == 0 else f"${p}" for p in PRICES],
                        [[n] + [pc(T[(T.model == n) & (T.price == p)].go_rate.max()) if ((T.model == n) & (T.price == p)).any() else "-" for p in PRICES] for n in names])
    hp_tab = html_table(["model", "half price", "95% CI", "P(GO) free", "P(GO) $35"],
                        [[r.model, "n/a" if not np.isfinite(r.half_price) else f"${r.half_price:.1f}",
                          "n/a" if not np.isfinite(r.lo) else f"${r.lo:.1f} to ${r.hi:.1f}", pc(r.free), pc(r.at35)] for r in H.itertuples()])
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Checking Price Sweep</title><style>{css}</style></head><body><div class="wrap">
<h1>What does it take to make an agent check?</h1>
<p class="muted">The same 576 first-hand prompts per model at five bus fares (free, $1, $5, $15, $35), with the weekly budget fixed at $40. Shaded bars are 95% CIs (bootstrap over the 13 listener personas).</p>
<div class="card">{charts[0]}</div>{go_tab}
<h2>Half price: the fare at which half of listeners still check</h2>
<p class="muted">From a logistic fit of GO on log(1 + fare). n/a = checking never crosses 50%, or does not fall as the fare rises.</p>{hp_tab}
<h2>Does the source's track record matter more when checking is costly?</h2><div class="card">{charts[1]}</div>
<h2>Does closeness matter more when checking is costly?</h2><div class="card">{charts[2]}</div>
<p class="muted">GPT and Claude models ran with their default settings (hidden reasoning, default temperature); DeepSeek and Qwen ran with thinking off (reasoning_effort none), as in the main study. One answer per prompt. Generated by mini_study/sweep_analysis.py.</p>
</div></body></html>"""
    open(os.path.join(RUNS, "sweep", "sweep_report.html"), "w").write(html)
    print("\n".join(L))


if __name__ == "__main__":
    main()
