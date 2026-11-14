"""Metric 14 - override and 64-cell map of the truth discount (exploratory: each cell has only a handful of twin pairs)."""
import numpy as np
import pandas as pd

from t3lib import MODEL_NAMES, MODELS, boot_diff, boot_mean, dna_name, pair_table, usable
import charts

ROWS = [(r, c) for r in ("good_record", "poor_record") for c in ("close_friend", "stranger")]
COLS = [(a, w, i) for a in ("mayor", "citizen") for w in ("rich", "poor") for i in ("woman_old", "woman_young", "man_old", "man_young")]


def _heat(c, value, title, vmin, vmax):
    vals, ann = [], []
    for r, cl in ROWS:
        rv, ra = [], []
        for a, w, i in COLS:
            x = c[(c.reliability == r) & (c.closeness == cl) & (c.authority == a) & (c.wealth == w) & (c.identity == i)]
            if len(x) and np.isfinite(x[value].iloc[0]):
                rv.append(float(x[value].iloc[0]))
                ra.append(f"cell {int(x.cell_id.iloc[0])}: {x[value].iloc[0]:+.2f} (pairs={int(x.pairs.iloc[0])})")
            else:
                rv.append(None)
                ra.append("")
        vals.append(rv)
        ann.append(ra)
    return charts.heatmap([f"{r.split('_')[0]} / {cl.split('_')[0]}" for r, cl in ROWS], [f"{a} | {w} | {i.replace('_', ' ')}" for a, w, i in COLS], vals,
                          vmin=vmin, vmax=vmax, kind="pct", ann=ann, cell=30, title=title)


def run(d, B=500):
    blocks, tables, summary = [], {}, []
    cells = []
    for m in MODELS:
        s = d[d.model == m]
        if s.empty:
            continue
        u = usable(pair_table(s, "score", "first_hand"))
        for cid, g in u.groupby("cell_id"):
            td = boot_mean(g.td, B=B, seed=cid)
            cells.append(dict(model=MODEL_NAMES[m], cell_id=int(cid), dna=dna_name(g.iloc[0]), closeness=g.closeness.iloc[0], authority=g.authority.iloc[0],
                              reliability=g.reliability.iloc[0], wealth=g.wealth.iloc[0], identity=g.identity.iloc[0], pairs=len(g),
                              truth_mean=g.truth_mean.mean(), rumor_mean=g.rumor_mean.mean(), td=td[0], td_lo=td[1], td_hi=td[2],
                              comfort_wins=bool(g.rumor_mean.mean() >= g.truth_mean.mean()), rumor_believed=bool(g.rumor_mean.mean() >= 0.5)))
    C = pd.DataFrame(cells)
    tables["m14_cell_td"] = C
    blocks += [("h3", "Where does comfort beat truth? (exploratory)"),
               ("p", "Each cell is one source profile (closeness, authority, record, wealth, gender and age). Numbers in the heatmap are TD x 100 (belief points). "
                     "Cells hold few twin pairs, so use the map to spot patterns, not to test individual cells."),
               ("p", "comfort_wins = the rumor twin believes at least as much as the truth twin (TD <= 0). rumor_believed = the rumor twin's mean belief is at least 0.5.")]
    for m in MODELS:
        c = C[C.model == MODEL_NAMES[m]] if len(C) else C
        if c.empty:
            continue
        blocks.append(("svg", _heat(c, "td", f"Truth discount by cell (x100) - {MODEL_NAMES[m]}", min(0.0, c.td.min()), max(0.01, c.td.max()))))
        blocks.append(("svg", _heat(c, "rumor_mean", f"Belief in the rumor by cell (x100) - {MODEL_NAMES[m]}", 0.0, 1.0)))
        k = int(c.comfort_wins.sum())
        summary.append(f"{MODEL_NAMES[m]}: {k} of {len(c)} cells have TD <= 0 (rumor believed at least as much as truth); {int(c.rumor_believed.sum())} cells have mean rumor belief >= 0.5. Cells average {c.pairs.mean():.1f} pairs.")
    low = C.sort_values(["model", "td"]).groupby("model").head(8) if len(C) else C
    blocks.append(("table", low.drop(columns=["closeness", "authority", "reliability", "wealth", "identity"]), "The eight lowest-TD cells per model (noisy: small n per cell)."))

    # ---- the two planned override questions, restricted to poor-record sources ---------------
    rows = []
    for m in MODELS:
        s = d[d.model == m]
        if s.empty:
            continue
        u = usable(pair_table(s, "score", "first_hand"))
        for lab, col, a, b in (("Friendship override: close friend vs stranger", "closeness", "close_friend", "stranger"),
                               ("Authority override: mayor vs citizen", "authority", "mayor", "citizen")):
            for rel in ("poor_record", "good_record"):
                x = u[u.reliability == rel]
                dd = boot_diff(x[x[col] == a].td, x[x[col] == b].td, B=B)
                rows.append(dict(model=MODEL_NAMES[m], question=lab, source_record=rel.replace("_", " "), td_difference=dd[0], lo=dd[1], hi=dd[2], pairs_a=dd[3], pairs_b=dd[4]))
    O = pd.DataFrame(rows)
    tables["m14_override"] = O
    blocks += [("h3", "Do closeness or authority override a bad track record?"),
               ("p", "TD difference (first level minus second) separately for poor-record and good-record sources. A friendship or authority override shows up as a clearly negative difference for poor-record sources "
                     "(the rumor is believed relatively more) that is smaller or absent for good-record sources. The formal test is contrasts 5 and 6 in metric 12."),
               ("table", O, "Independent-group bootstrap over twin pairs.")]
    for r in O[(O.source_record == "poor record")].itertuples():
        summary.append(f"{r.model} | {r.question.split(':')[0]} (poor-record sources): TD difference {r.td_difference:+.3f} (CI {r.lo:+.3f} to {r.hi:+.3f}).")
    return dict(id="m14", title="Metric 14 - Override and cell map", summary=summary, blocks=blocks, tables=tables)
