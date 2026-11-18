"""Metric 20 - top-10 DNA rule: rank the 64 source profiles ("DNAs") by how persuasive a LYING source is, per model.

Persuasiveness of a DNA = mean belief in the rumor twin (first-hand listeners, conditional on mentioning the claim), averaged over
that cell's twin pairs. The rule is checked with a split-sample test: rank on half the pairs of every cell, rank again on the other
half, and ask how much the two top-10 lists overlap. A bootstrap gives each cell's probability of making the top 10.
"""
import numpy as np
import pandas as pd

from t3lib import MODEL_NAMES, MODELS, dna_name, pair_table, spearman, usable

K = 10


def _top(means, k=K):
    return set(means.sort_values(ascending=False).index[:k])


def run(d, B=500, splits=500, seed=7):
    blocks, tables, summary = [], {}, []
    rng = np.random.default_rng(seed)
    tops, ranks = {}, {}
    for m in MODELS:
        s = d[d.model == m]
        if s.empty:
            continue
        u = usable(pair_table(s, "score", "first_hand"), "rumor_mean").reset_index(drop=True)
        cells = sorted(u.cell_id.unique())
        if len(cells) < K + 2:
            continue
        full = u.groupby("cell_id").rumor_mean.mean()
        by_cell = {c: u.index[u.cell_id == c].to_numpy() for c in cells}

        # split-sample stability
        overlaps, rhos, regret = [], [], []
        for _ in range(splits):
            a_idx, b_idx = [], []
            for c in cells:
                ix = rng.permutation(by_cell[c])
                h = len(ix) // 2
                a_idx += list(ix[:h])
                b_idx += list(ix[h:])
            ma = u.loc[a_idx].groupby("cell_id").rumor_mean.mean()
            mb = u.loc[b_idx].groupby("cell_id").rumor_mean.mean()
            common = ma.index.intersection(mb.index)
            ta, tb = _top(ma[common]), _top(mb[common])
            overlaps.append(len(ta & tb))
            rhos.append(spearman(ma[common], mb[common]))
            regret.append(float(mb[common].sort_values(ascending=False).iloc[:K].mean() - mb[list(ta)].mean()))
        # chance overlap for K of n cells
        chance = K * K / len(cells)

        # bootstrap probability of being in the top 10
        arr = {c: u.rumor_mean.values[by_cell[c]] for c in cells}
        inc = pd.Series(0.0, index=cells)
        for _ in range(B):
            bm = pd.Series({c: rng.choice(arr[c], len(arr[c])).mean() for c in cells})
            inc[list(_top(bm))] += 1
        inc /= B

        info = u.drop_duplicates("cell_id").set_index("cell_id")
        td = u.groupby("cell_id").td.mean()
        T = pd.DataFrame({"model": MODEL_NAMES[m], "rank": full.rank(ascending=False, method="first").astype(int), "cell_id": full.index,
                          "dna": [dna_name(info.loc[c]) for c in full.index], "pairs": [len(by_cell[c]) for c in full.index],
                          "rumor_belief": full.values, "td": td.reindex(full.index).values, "p_in_top10": inc.reindex(full.index).values}).sort_values("rank")
        tables[f"m20_ranking_{m}"] = T
        tops[m], ranks[m] = list(T.cell_id.iloc[:K]), full
        S = dict(model=MODEL_NAMES[m], cells=len(cells), pairs_per_cell=float(np.mean([len(v) for v in by_cell.values()])), top10_overlap_between_halves=float(np.mean(overlaps)),
                 overlap_expected_by_chance=chance, spearman_between_halves=float(np.nanmean(rhos)), rho_lo=float(np.nanpercentile(rhos, 2.5)), rho_hi=float(np.nanpercentile(rhos, 97.5)),
                 regret_rumor_belief=float(np.mean(regret)))
        tables.setdefault("m20_split_sample", []).append(S)
        blocks += [("h3", f"Top-{K} most persuasive liar DNAs - {MODEL_NAMES[m]}"),
                   ("table", T.head(K).drop(columns=["model"]), f"Top {K} of {len(cells)} cells by mean rumor-twin belief; p_in_top10 is the bootstrap selection frequency."),
                   ("table", T.tail(5).drop(columns=["model"]), "Five least persuasive cells, for contrast.")]
        summary.append(f"{MODEL_NAMES[m]}: half-vs-half top-10 lists share {np.mean(overlaps):.1f} cells on average (chance: {chance:.1f}); rank correlation {np.nanmean(rhos):.2f}. "
                       f"Selecting on half the data costs {np.mean(regret):.3f} belief points of rumor persuasiveness versus the best top-10 in the other half.")
    if "m20_split_sample" in tables:
        tables["m20_split_sample"] = pd.DataFrame(tables["m20_split_sample"])
        blocks.insert(0, ("table", tables["m20_split_sample"], "Split-sample check of the selection rule (500 random splits). Overlap far above chance and a high rank correlation mean the top-10 is a stable selection at this sample size."))
        blocks.insert(0, ("p", "Rule: rank the 64 DNAs by mean belief in the rumor (first-hand, rumor twin) and keep the top 10 per model. A DNA ranked on noise would not replicate in the other half of the pairs."))
        blocks.insert(0, ("h3", "Is the top-10 selection stable?"))
    if len(tops) == 2:
        a, b = MODELS
        ov = len(set(tops[a]) & set(tops[b]))
        rho = spearman(ranks[a].reindex(ranks[b].index), ranks[b])
        blocks.append(("p", f"Cross-model agreement: the two top-10 lists share {ov} cells; rank correlation of cell-level rumor persuasiveness between models is {rho:.2f}."))
        summary.append(f"The two models' top-10 lists share {ov} of {K} cells (cell-level rank correlation {rho:.2f}).")
    if not summary:
        summary.append("Not enough cells with usable rumor-twin beliefs.")
    return dict(id="m20", title="Metric 20 - Top-10 DNA rule", summary=summary, blocks=blocks, tables={k: v for k, v in tables.items() if hasattr(v, "to_csv")})
