"""Tiny dependency-free SVG chart helpers. Colors come from CSS variables defined in the report."""
from html import escape

import numpy as np

SERIES = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)"]


def _fmt(v, kind="pct"):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a"
    return f"{100 * v:.0f}%" if kind == "pct" else (f"{v:+.2f}" if kind == "signed" else f"{v:.2f}")


def tick_txt(t, kind):
    return "%.2f" % t if kind == "or" else _fmt(t, kind)


def grouped_bars(categories, series, ymax=1.0, height=260, kind="pct", title=None):
    """Vertical grouped bars with 95% CI whiskers.

    series: list of dict(name, vals, lo, hi)  (lists aligned with categories)
    """
    n_c, n_s = len(categories), len(series)
    W = max(520, 90 * n_c * max(1, n_s * 0.55) + 90)
    ml, mr, mt, mb = 44, 12, 28 if title else 12, 58
    H = height
    pw, ph = W - ml - mr, H - mt - mb
    out = [f'<svg viewBox="0 0 {W:.0f} {H + 28}" class="chart" role="img">']
    if title:
        out.append(f'<text x="{ml}" y="16" class="t-title">{escape(title)}</text>')
    for i in range(0, 5):
        v = ymax * i / 4
        y = mt + ph - ph * v / ymax
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{ml - 6}" y="{y + 4:.1f}" class="t-axis" text-anchor="end">{_fmt(v, kind)}</text>')
    gw = pw / n_c
    bw = min(34, gw * 0.8 / n_s)
    for ci, cat in enumerate(categories):
        gx = ml + gw * ci + gw / 2 - bw * n_s / 2
        for si, s in enumerate(series):
            v = s["vals"][ci]
            if v is None or not np.isfinite(v):
                continue
            x = gx + si * bw
            h = ph * max(v, 0) / ymax
            out.append(f'<rect x="{x:.1f}" y="{mt + ph - h:.1f}" width="{bw - 3:.1f}" height="{h:.1f}" '
                       f'fill="{SERIES[si % 4]}" rx="2"><title>{escape(s["name"])} / {escape(str(cat))}: {_fmt(v, kind)}</title></rect>')
            lo, hi = s.get("lo", [None] * n_c)[ci], s.get("hi", [None] * n_c)[ci]
            if lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi):
                xc = x + (bw - 3) / 2
                y1 = mt + ph - ph * min(max(hi, 0), ymax) / ymax
                y2 = mt + ph - ph * min(max(lo, 0), ymax) / ymax
                out.append(f'<line x1="{xc:.1f}" x2="{xc:.1f}" y1="{y1:.1f}" y2="{y2:.1f}" class="whisker"/>')
                out.append(f'<line x1="{xc - 3:.1f}" x2="{xc + 3:.1f}" y1="{y1:.1f}" y2="{y1:.1f}" class="whisker"/>')
                out.append(f'<line x1="{xc - 3:.1f}" x2="{xc + 3:.1f}" y1="{y2:.1f}" y2="{y2:.1f}" class="whisker"/>')
        lines = str(cat).split("\n")
        for li, ln in enumerate(lines):
            out.append(f'<text x="{ml + gw * ci + gw / 2:.1f}" y="{mt + ph + 16 + 12 * li}" class="t-axis" text-anchor="middle">{escape(ln)}</text>')
    # legend
    lx = ml
    for si, s in enumerate(series):
        out.append(f'<rect x="{lx}" y="{H + 10}" width="10" height="10" fill="{SERIES[si % 4]}" rx="2"/>')
        out.append(f'<text x="{lx + 14}" y="{H + 19}" class="t-axis">{escape(s["name"])}</text>')
        lx += 22 + 7 * len(s["name"])
    out.append("</svg>")
    return "".join(out)


def forest(rows, xlabel, xmin=None, xmax=None, zero=0.0, kind="signed", row_h=24, title=None, log=False):
    """Horizontal point + CI plot. rows: list of dict(label, est, lo, hi, group(optional, picks color index))."""
    ml, mr = 210, 70
    mt = 26 if title else 8
    H = mt + row_h * len(rows) + 40
    W = 620
    vals = [v for r in rows for v in (r["est"], r["lo"], r["hi"]) if v is not None and np.isfinite(v)]
    if log:
        pos = [v for v in vals + [zero] if v > 0]
        if xmin is None or xmin > min(pos) / 1.15:
            xmin = max(min(pos) / 1.15, 1e-3)
        if xmax is None or xmax < max(pos) * 1.15:
            xmax = min(max(pos) * 1.15, 300.0)
    else:
        if xmin is None:
            xmin = min(vals + [zero]) - 0.03
        if xmax is None:
            xmax = max(vals + [zero]) + 0.03
    pw = W - ml - mr

    def X(v):
        if log:
            v, a, b = np.log(v), np.log(xmin), np.log(xmax)
            return ml + pw * (v - a) / (b - a)
        return ml + pw * (v - xmin) / (xmax - xmin)

    out = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img">']
    if title:
        out.append(f'<text x="{ml}" y="14" class="t-title">{escape(title)}</text>')
    ticks = np.exp(np.linspace(np.log(xmin), np.log(xmax), 5)) if log else np.linspace(xmin, xmax, 5)
    for t in ticks:
        out.append(f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{mt}" y2="{H - 34}" class="grid"/>')
        out.append(f'<text x="{X(t):.1f}" y="{H - 20}" class="t-axis" text-anchor="middle">{tick_txt(t, kind)}</text>')
    out.append(f'<line x1="{X(zero):.1f}" x2="{X(zero):.1f}" y1="{mt}" y2="{H - 34}" class="zero"/>')
    out.append(f'<text x="{ml + pw / 2:.1f}" y="{H - 4}" class="t-axis" text-anchor="middle">{escape(xlabel)}</text>')
    for i, r in enumerate(rows):
        y = mt + row_h * i + row_h / 2
        col = SERIES[r.get("group", 0) % 4]
        out.append(f'<text x="{ml - 8}" y="{y + 4:.1f}" class="t-axis" text-anchor="end">{escape(r["label"])}</text>')
        if r["est"] is None or not np.isfinite(r["est"]):
            continue
        if r["lo"] is not None and np.isfinite(r["lo"]) and np.isfinite(r["hi"]):
            lo, hi = max(r["lo"], xmin), min(r["hi"], xmax)
            out.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2"/>')
        txt = _fmt(r["est"], kind) if kind != "or" else "%.2f" % r["est"]
        cx = X(min(max(r["est"], xmin), xmax))
        out.append(f'<circle cx="{cx:.1f}" cy="{y:.1f}" r="4.5" fill="{col}"><title>{escape(r["label"])}: {txt}</title></circle>')
        out.append(f'<text x="{W - mr + 8}" y="{y + 4:.1f}" class="t-axis">{txt}</text>')
    out.append("</svg>")
    return "".join(out)


def heatmap(row_labels, col_labels, values, vmin=0.0, vmax=1.0, kind="pct", cell=34, annotate=True, title=None, ann=None):
    """values: 2-D list; None = missing. ann: optional same-shape list of tooltip strings."""
    nr, nc = len(row_labels), len(col_labels)
    ml = max(130, 6 * max(len(r) for r in row_labels) + 12)
    longest = max(len(c) for c in col_labels)
    mt = 24 + int(longest * 4.4) + (16 if title else 0)
    W = max(ml + nc * cell + 10 + int(longest * 3.5), ml + (len(title) * 6.5 if title else 0) + 10)
    H = mt + nr * cell + 8
    out = [f'<svg viewBox="0 0 {W} {H}" class="chart heat" style="max-width:{W}px" role="img">']
    if title:
        out.append(f'<text x="{ml}" y="14" class="t-title">{escape(title)}</text>')
    for j, c in enumerate(col_labels):
        x = ml + cell * j + cell / 2
        out.append(f'<text transform="translate({x:.1f},{mt - 6}) rotate(-50)" class="t-axis">{escape(c)}</text>')
    for i, rl in enumerate(row_labels):
        out.append(f'<text x="{ml - 6}" y="{mt + cell * i + cell / 2 + 4:.1f}" class="t-axis" text-anchor="end">{escape(rl)}</text>')
        for j in range(nc):
            v = values[i][j]
            x, y = ml + cell * j, mt + cell * i
            if v is None or not np.isfinite(v):
                out.append(f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" class="na" rx="3"/>')
                continue
            a = 0.08 + 0.87 * min(max((v - vmin) / (vmax - vmin + 1e-12), 0), 1)
            tip = ann[i][j] if ann else f"{rl} / {col_labels[j]}: {_fmt(v, kind)}"
            out.append(f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" rx="3" fill="var(--c1)" fill-opacity="{a:.2f}"><title>{escape(tip)}</title></rect>')
            if annotate:
                txt = f"{100 * v:.0f}" if kind == "pct" else f"{v:.2f}"
                out.append(f'<text x="{x + (cell - 2) / 2}" y="{y + cell / 2 + 3}" class="t-cell" text-anchor="middle">{txt}</text>')
    out.append("</svg>")
    return "".join(out)
