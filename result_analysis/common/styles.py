"""Shared CSS for the self-contained HTML reports."""
CSS = """
:root{--bg:#fbfaf7;--card:#fff;--fg:#1f2328;--muted:#656d76;--line:#e4e1da;--grid:#ecebe6;--accent:#2f6f5e;
--c1:#2f6f5e;--c2:#c46a2d;--c3:#4a6fa5;--c4:#8a5a9c;--na:#ecebe6}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14171a;--card:#1c2024;--fg:#e6e8ea;--muted:#9aa3ab;--line:#2c3238;--grid:#2a3036;--accent:#58b79c;
--c1:#58b79c;--c2:#e39a62;--c3:#7fa3d6;--c4:#b98bcb;--na:#2a3036}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:26px;margin:8px 0 4px}h2{font-size:21px;margin:36px 0 8px;padding-top:12px;border-top:1px solid var(--line)}
h3{font-size:17px;margin:26px 0 6px}h4{font-size:15px;margin:18px 0 4px;color:var(--muted)}
.sub{color:var(--muted);margin:0 0 18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kpi b{display:block;font-size:22px}.kpi span{color:var(--muted);font-size:13px}
.take{margin:8px 0 0;padding-left:20px}.take li{margin:4px 0}
nav{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:5;font-size:14px}
nav a{margin-right:14px;color:var(--accent);text-decoration:none}
svg.chart{width:100%;height:auto;display:block;margin:8px 0}
.t-axis{font-size:11px;fill:var(--muted)}.t-title{font-size:13px;font-weight:600;fill:var(--fg)}.t-cell{font-size:9px;fill:var(--fg)}
.grid{stroke:var(--grid);stroke-width:1}.zero{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 3}.whisker{stroke:var(--fg);stroke-width:1.2;opacity:.65}
.na{fill:var(--na)}
.tbl{overflow-x:auto;margin:8px 0}table{border-collapse:collapse;font-size:13px;width:100%}
caption{caption-side:bottom;text-align:left;color:var(--muted);font-size:12px;padding-top:4px}
th,td{padding:4px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th{text-align:right;color:var(--muted);font-weight:600}th:first-child,td:first-child{text-align:left}
td.l,th.l{text-align:left}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px}
.warn{border-left:4px solid var(--c2)}
footer{color:var(--muted);font-size:12px;margin-top:40px}
p{margin:6px 0}code{background:var(--grid);padding:1px 5px;border-radius:4px;font-size:13px}
"""
