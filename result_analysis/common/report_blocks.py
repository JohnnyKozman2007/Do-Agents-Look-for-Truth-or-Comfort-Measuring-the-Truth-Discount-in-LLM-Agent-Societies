"""Block and table rendering shared by the Tier 1 and Tier 3/4 report builders (inline SVG, no external assets)."""
from html import escape

import numpy as np


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
