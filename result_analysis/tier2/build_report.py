"""Render the Tier-2 results into one self-contained HTML file (inline SVG, no external assets)."""
from datetime import datetime
from html import escape

import numpy as np
import pandas as pd

from styles import CSS  # noqa: E402


def _fmt_cell(col, v):
    if isinstance(v, (float, np.floating)):
        if not np.isfinite(v):
            return "-"
        c = col.lower()
        if c == "p" or c.endswith("_p"):
            return "<0.001" if v < 0.001 else f"{v:.3f}"
        if any(k in c for k in ("rate", "lo", "hi", "diff", "did", "minus", "agree", "share", "checked", "passed", "gap", "go_", "same", "expected",
                                 "knobs_only", "all_factors", "added", "rate_a", "rate_b", "overall", "if_")):
            return f"{100 * v:.1f}%" if abs(v) <= 1.0 and "odds" not in c else f"{v:.2f}"
        return f"{v:.3f}" if abs(v) < 100 else f"{v:.1f}"
    return escape(str(v))


def table_html(df, caption=None):
    df = df.copy()
    head = "".join(f'<th class="{"l" if df[c].dtype == object else ""}">{escape(str(c).replace("_", " "))}</th>' for c in df.columns)
    rows = []
    for r in df.itertuples(index=False):
        rows.append("<tr>" + "".join(f'<td class="{"l" if isinstance(v, str) else ""}">{_fmt_cell(c, v)}</td>' for c, v in zip(df.columns, r)) + "</tr>")
    cap = f"<caption>{escape(caption)}</caption>" if caption else ""
    return f'<div class="tbl"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def render_blocks(blocks):
    out = []
    for b in blocks:
        kind = b[0]
        if kind in ("h3", "h4"):
            out.append(f"<{kind}>{escape(b[1])}</{kind}>")
        elif kind == "p":
            out.append(f"<p>{escape(b[1])}</p>")
        elif kind == "svg":
            out.append(f'<div class="card">{b[1]}</div>')
        elif kind == "table":
            out.append(table_html(b[1], b[2] if len(b) > 2 else None))
        elif kind == "grid":
            out.append(f'<div class="card"><h4>{escape(b[2])}</h4><div class="grid2">{"".join(b[1])}</div></div>')
    return "\n".join(out)


def build(results, df, data_dir, out_path):
    towns = df.run_id.nunique()
    kpis = [("Towns", f"{towns:,}"), ("Twin pairs", f"{df.pair_id.nunique():,}"),
            ("Listener decisions", f"{len(df):,}"), ("Models", str(df.model.nunique())), ("Cells", str(df.cell_id.nunique())),
            ("Malformed decisions", str(int(df.malformed.sum())))]
    kpi_html = "".join(f'<div class="kpi"><b>{v}</b><span>{k}</span></div>' for k, v in kpis)
    nav = "".join(f'<a href="#{r["id"]}">{escape(r["title"].split(" - ")[0])}</a>' for r in results)
    sections = []
    for r in results:
        take = "".join(f"<li>{escape(s)}</li>" for s in r["summary"])
        sections.append(f'<h2 id="{r["id"]}">{escape(r["title"])}</h2><div class="card"><b>Key takeaways</b><ul class="take">{take}</ul></div>'
                        + render_blocks(r["blocks"]))
    caveats = [
        "Development pilot data: <code>evidence_kind = development_pilot</code>, <code>study_eligible = false</code>. Treat numbers as exploratory.",
        "Partial design: each model ran about 6-7 twin pairs per cell (the full plan is 39). The two models ran different layouts, so model, source persona and layout are partly confounded.",
        "First-hand listeners decide to check before seeing any poster, so truth cannot affect their check decision by design.",
        "Confidence intervals are cluster-bootstrap (cluster = twin pair, 2,000 resamples); regressions use cluster-robust standard errors. Listeners in one town share a source interaction and are not independent.",
        "These metrics are behavioral (GO/SKIP) and need no LLM judge. Belief-based metrics (truth discount) are a separate step.",
    ]
    cav = "".join(f"<li>{c}</li>" for c in caveats)
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tier 2 Check Behavior</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Tier 2: Who Checks the Noticeboard?</h1>
<p class="sub">Behavioral analysis of the AgentTruth main-study simulation (no LLM judge needed). Generated {datetime.now():%Y-%m-%d %H:%M} from <code>{escape(str(data_dir))}</code>.</p>
<nav>{nav}<a href="#method">Method</a></nav>
<div class="kpis">{kpi_html}</div>
<div class="card warn"><b>Read this first</b><ul class="take">{cav}</ul></div>
{"".join(sections)}
<h2 id="method">Method and files</h2>
<div class="card"><ul class="take">
<li><b>Extraction:</b> <code>t2lib.load_listeners</code> reads each <code>town.json</code> into one row per listener (decision, knobs, seat, persona, partner state).</li>
<li><b>Rates and differences:</b> cluster bootstrap over twin pairs (<code>t2lib.boot_groups</code>).</li>
<li><b>Regression:</b> logistic regression (IRLS) with cluster-robust sandwich SEs, implemented in numpy.</li>
<li><b>Outputs:</b> this report plus CSVs for every table and <code>listeners.csv</code> in the output folder.</li>
</ul></div>
<footer>Generated by result_analysis/tier2/run_tier2.py</footer></div></body></html>"""
    with open(out_path, "w") as f:
        f.write(html)
    return out_path
