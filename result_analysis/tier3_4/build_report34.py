"""Render Tier 3/4 results into one self-contained HTML file (reuses the Tier 2 CSS and chart helpers)."""
from datetime import datetime
from html import escape

import numpy as np
import pandas as pd

import t3lib  # noqa: F401  (adds ../common to sys.path)
from styles import CSS


def _fmt(col, v, pct_cols):
    if isinstance(v, (float, np.floating)):
        if not np.isfinite(v):
            return "-"
        c = str(col)
        if c == "p" or c.startswith("p_") or c.endswith("_p"):
            return "<0.001" if v < 0.001 else f"{v:.3f}"
        if c in pct_cols:
            return f"{100 * v:.1f}%"
        return f"{v:.3f}" if abs(v) < 100 else f"{v:.1f}"
    if isinstance(v, (bool, np.bool_)):
        return "yes" if v else "no"
    if isinstance(v, (int, np.integer)):
        return f"{int(v):,}"
    return escape(str(v))


def table2(df, caption=None, pct_cols=()):
    df = df.copy()
    head = "".join(f'<th class="{"l" if df[c].dtype == object else ""}">{escape(str(c).replace("_", " "))}</th>' for c in df.columns)
    rows = []
    for r in df.itertuples(index=False):
        rows.append("<tr>" + "".join(f'<td class="{"l" if isinstance(v, str) else ""}">{_fmt(c, v, pct_cols)}</td>' for c, v in zip(df.columns, r)) + "</tr>")
    cap = f"<caption>{escape(caption)}</caption>" if caption else ""
    return f'<div class="tbl"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def render_blocks(blocks):
    out = []
    for b in blocks:
        k = b[0]
        if k in ("h3", "h4"):
            out.append(f"<{k}>{escape(b[1])}</{k}>")
        elif k == "p":
            out.append(f"<p>{escape(b[1])}</p>")
        elif k == "svg":
            out.append(f'<div class="card">{b[1]}</div>')
        elif k == "table":
            out.append(table2(b[1], b[2] if len(b) > 2 else None, b[3] if len(b) > 3 else ()))
        elif k == "grid":
            out.append(f'<div class="card"><h4>{escape(b[2])}</h4><div class="grid2">{"".join(b[1])}</div></div>')
    return "\n".join(out)


def caveats(judge_name, skipped, synthetic=False):
    """Reading guide for the belief-based (Tier 3/4) metrics."""
    cav = [
        f"Belief labels come from <b>{escape(judge_name)}</b>, a single LLM judge. Judge error is not propagated into the confidence intervals; the intervals reflect sampling variation over twin pairs only.",
        "Belief scores: FACT and CHECKED_TRUE = 1, UNCERTAIN = 0.5, SKEPTICAL and CHECKED_FALSE = 0. NOT_MENTIONED is excluded from the primary mean; NOT_MENTIONED = 0 and = 0.5 are reported as sensitivity bounds. Missing or invalid labels stay missing.",
        "Truth discount (TD) = mean belief in the truth twin minus mean belief in the rumor twin, computed per twin pair; the pair is the independent unit. Intervals are percentile bootstraps over pairs (2,000 resamples by default, set with --boot) unless stated.",
        "First-hand listeners choose GO/SKIP before seeing any poster, so TD among first-hand non-checkers is a built-in noise floor (expected near 0).",
        "Exploratory analysis until a dated analysis specification exists; the ten planned contrasts here use Holm correction, but this report is not the confirmatory test.",
        f"Not computed here (need LLM calls or probabilities): {escape('; '.join(skipped))}.",
    ]
    if synthetic:
        cav.insert(0, "<b>SYNTHETIC PLACEHOLDER LABELS.</b> These labels are random and exist only to test the code. Nothing below is a result.")
    return cav


def build(results, d, data_dirs, label_files, judge_name, out_path, skipped, synthetic=False):
    n_lab = int(d.labeled.sum())
    kpis = [("Towns", f"{d.run_id.nunique():,}"), ("Twin pairs", f"{d.pair_id.nunique():,}"), ("Listeners", f"{len(d):,}"),
            ("Labeled", f"{n_lab:,} ({100 * n_lab / len(d):.0f}%)"), ("Omitted (NOT_MENTIONED)", f"{int(d.omitted.sum()):,}"),
            ("Models", str(d.model.nunique()))]
    kpi_html = "".join(f'<div class="kpi"><b>{v}</b><span>{k}</span></div>' for k, v in kpis)
    nav = "".join(f'<a href="#{r["id"]}">{escape(r["title"].split(" - ")[0])}</a>' for r in results)
    secs = []
    for r in results:
        take = "".join(f"<li>{escape(s)}</li>" for s in r["summary"])
        secs.append(f'<h2 id="{r["id"]}">{escape(r["title"])}</h2><div class="card"><b>Key takeaways</b><ul class="take">{take}</ul></div>' + render_blocks(r["blocks"]))
    cav = caveats(judge_name, skipped, synthetic)
    cav_html = "".join(f"<li>{c}</li>" for c in cav)
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tier 3 and 4 Truth Discount</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Tiers 3 and 4: Truth Discount, Robustness and Mechanism</h1>
<p class="sub">Belief-based analysis of the AgentTruth main-study simulation. Generated {datetime.now():%Y-%m-%d %H:%M}. Data: <code>{escape(", ".join(str(x) for x in data_dirs))}</code>. Labels: <code>{escape(", ".join(str(x) for x in label_files))}</code>.</p>
<nav>{nav}</nav><div class="kpis">{kpi_html}</div>
<div class="card warn"><b>Read this first</b><ul class="take">{cav_html}</ul></div>
{"".join(secs)}
<footer>Generated by result_analysis/tier3_4/run_tier34.py</footer></div></body></html>"""
    with open(out_path, "w") as f:
        f.write(html)
    return out_path
