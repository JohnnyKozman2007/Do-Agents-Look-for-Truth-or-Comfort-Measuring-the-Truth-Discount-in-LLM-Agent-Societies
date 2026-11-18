"""Build Report 3: Truth Discount & Comparisons (Gemini 3.7 Flash).

Implements reports/SPEC_truth_discount_comparison.md:
  - Matched-pair Truth Discount (Truth Twin - Rumor Twin) across models & layers.
  - Offline SVG Butterfly (Mirror Bar) charts for categorical labels & 64 DNAs.
  - Pooled symmetry & Truth Discount regression across all 10 planned contrasts
    (6 main knobs + 4 interactions), pair-clustered (pair_id) SEs, Holm across 10,
    plus companion spec LMM check on conditional Belief and Paired Forest SVG plot.
  - 4 Planned Interaction Pairs: 16-DNA combo Truth vs Rumor vs Truth Discount.
  - Top 10 Largest & Bottom 10 Smallest Truth Discount DNAs per Model x POV.
  - Model comparison: DeepSeek-V4-Flash vs Qwen3.8-Flash.

Outputs in reports/truth_discount_comparison/: report.html, report.md, csv/*.csv.
"""
from __future__ import annotations

import argparse
import html
import itertools
import json
import math
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
import patsy
from scipy.stats import norm
import statsmodels.formula.api as smf

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_condition_reports as bcr

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "results" / "main-gemini-3.7-flash"
DEFAULT_OUT = ROOT / "reports" / "truth_discount_comparison"

FORMULA_POOLED = (
    "outcome ~ truth * ("
    + " + ".join(f"C({f})" for f, _, _ in bcr.FACTORS)
    + " + "
    + " + ".join(f"C({a}):C({b})" for a, b in bcr.INTERACTIONS)
    + ") + C(real_artist)"
)

BUTTERFLY_METRICS = (
    ("belief", "Belief Score (0-1)", False),
    ("go_pct", "GO Rate (%)", True),
    ("FACT", "FACT (%)", True),
    ("UNCERTAIN", "UNCERTAIN (%)", True),
    ("SKEPTICAL", "SKEPTICAL (%)", True),
    ("CHECKED_TRUE", "CHECKED_TRUE (%)", True),
    ("CHECKED_FALSE", "CHECKED_FALSE (%)", True),
    ("NOT_MENTIONED", "NOT_MENTIONED (%)", True),
)


# --------------------------------------------------------------------------- data prep
def prepare_all_listeners(listeners: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    """Prepare full listener DataFrame (rumor + truth_twin), preserving NaN on INVALID rows."""
    df = listeners.copy()
    cell_names = cells[["cell_id", "cell_name"]].drop_duplicates()
    df = df.merge(cell_names, on="cell_id", how="left")
    is_valid = df["judgment_status"] == "valid"
    is_nm = is_valid & (df["label"] == "NOT_MENTIONED")

    df["is_valid"] = is_valid
    df["is_invalid"] = ~is_valid
    df["is_go"] = np.where(df["decision"] == "GO", 1.0, np.where(df["decision"] == "SKIP", 0.0, np.nan))
    df["is_skip"] = 1.0 - df["is_go"]
    df["belief"] = np.where(is_valid & (df["mentioned"] == 1), df["belief"].astype(float), np.nan)
    df["belief_sil0"] = np.where(is_nm, 0.0, df["belief"])
    df["belief_sil05"] = np.where(is_nm, 0.5, df["belief"])
    for lbl in bcr.LABELS:
        df[f"label_{lbl}"] = np.where(is_valid, (df["label"] == lbl).astype(float), np.nan)
    df["pair_cluster"] = df["model_key"].astype(str) + "__" + df["pair_id"].astype(str)
    return df


def _paired_diff_summary(sub: pd.DataFrame, col: str, scale: float = 1.0) -> tuple[float, float, float, float, int]:
    """Compute mean matched-pair difference (truth - rumor) and 95% normal CI across complete pairs."""
    paired = (
        sub.groupby(["pair_cluster", "truth"], observed=True)[col]
        .mean()
        .unstack("truth")
    )
    if 0 not in paired.columns or 1 not in paired.columns:
        return float("nan"), float("nan"), float("nan"), float("nan"), 0
    valid_pairs = paired[[0, 1]].dropna()
    n = int(len(valid_pairs))
    if n == 0:
        return float("nan"), float("nan"), float("nan"), float("nan"), 0
    diffs = (valid_pairs[1] - valid_pairs[0]) * scale
    mean_d = float(diffs.mean())
    se = float(diffs.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    crit = float(norm.ppf(0.975))
    lo = mean_d - crit * se if math.isfinite(se) else float("nan")
    hi = mean_d + crit * se if math.isfinite(se) else float("nan")
    p_val = float(2.0 * norm.sf(abs(mean_d / se))) if se and se > 0 else float("nan")
    return mean_d, lo, hi, p_val, n


# --------------------------------------------------------------------------- summary tables
def compute_comparison_summaries(df: pd.DataFrame, conditions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Table 1A (Per Model x Layer) and Table 1B (Both Models Combined) comparing Rumor vs Truth."""
    rows_a, rows_b = [], []

    def build_slice(sub: pd.DataFrame, cond_sub: pd.DataFrame | None, label_meta: dict) -> dict:
        r_sub = sub[sub["truth"] == 0]
        t_sub = sub[sub["truth"] == 1]
        td, td_lo, td_hi, td_p, td_n = _paired_diff_summary(sub, "belief", 1.0)
        td0, _, _, _, td0_n = _paired_diff_summary(sub, "belief_sil0", 1.0)
        td05, _, _, _, _ = _paired_diff_summary(sub, "belief_sil05", 1.0)
        d_go, _, _, _, d_go_n = _paired_diff_summary(sub, "is_go", 100.0)
        d_nm, _, _, _, d_nm_n = _paired_diff_summary(sub, "label_NOT_MENTIONED", 100.0)

        row = {
            **label_meta,
            "n_towns_rumor": int(r_sub["run_id"].nunique()),
            "n_towns_truth": int(t_sub["run_id"].nunique()),
            "rumor_expected_n": int(len(r_sub)),
            "truth_expected_n": int(len(t_sub)),
            "rumor_valid_n": int(r_sub["is_valid"].sum()),
            "truth_valid_n": int(t_sub["is_valid"].sum()),
            "rumor_mentioned_n": int(r_sub["belief"].notna().sum()),
            "truth_mentioned_n": int(t_sub["belief"].notna().sum()),
            "n_pairs_used_belief": td_n,
            "n_pairs_used_sil": td0_n,
            "n_pairs_used_go": d_go_n,
            "n_pairs_used_nm": d_nm_n,
            "rumor_belief": bcr._mean_or_nan(r_sub["belief"]),
            "truth_belief": bcr._mean_or_nan(t_sub["belief"]),
            "truth_discount": td,
            "td_ci_low": td_lo,
            "td_ci_high": td_hi,
            "td_p": td_p,
            "td_sil0": td0,
            "td_sil05": td05,
            "rumor_go_pct": bcr._pct(r_sub["is_go"]),
            "truth_go_pct": bcr._pct(t_sub["is_go"]),
            "diff_go_pp": d_go,
            "rumor_nm_pct": bcr._pct(r_sub["label_NOT_MENTIONED"]),
            "truth_nm_pct": bcr._pct(t_sub["label_NOT_MENTIONED"]),
            "diff_nm_pp": d_nm,
            "rumor_invalid_n": int(r_sub["is_invalid"].sum()),
            "truth_invalid_n": int(t_sub["is_invalid"].sum()),
        }
        for lbl in bcr.LABELS:
            row[f"rumor_{lbl}_pct"] = bcr._pct(r_sub[f"label_{lbl}"])
            row[f"truth_{lbl}_pct"] = bcr._pct(t_sub[f"label_{lbl}"])
            row[f"diff_{lbl}_pp"] = row[f"truth_{lbl}_pct"] - row[f"rumor_{lbl}_pct"]
        if cond_sub is not None and len(cond_sub):
            for cname, prefix in (("rumor", "rumor"), ("truth_twin", "truth")):
                cs = cond_sub[cond_sub["condition_type"] == cname]
                td_den = float(cs["transmission_observed_denominator"].sum())
                ev_den = float(cs["evidence_checker_denominator"].sum())
                row[f"{prefix}_trans_pct"] = float(cs["transmission_keyword_count"].sum() / td_den * 100.0) if td_den else float("nan")
                row[f"{prefix}_evid_pct"] = float(cs["evidence_keyword_count"].sum() / ev_den * 100.0) if ev_den else float("nan")
            row["diff_trans_pp"] = row["truth_trans_pct"] - row["rumor_trans_pct"]
            row["diff_evid_pp"] = row["truth_evid_pct"] - row["rumor_evid_pct"]
        else:
            for k in ("rumor_trans_pct", "truth_trans_pct", "diff_trans_pp", "rumor_evid_pct", "truth_evid_pct", "diff_evid_pp"):
                row[k] = float("nan")
        return row

    layer_defs = (("first_hand", "First-Hand (Seats 1-6)"), ("second_hand", "Second-Hand (Seats 7-12)"), ("overall", "Overall (All 12 Listeners)"))
    for model_key, model_name in bcr.MODEL_NAMES.items():
        mdf = df[df["model_key"] == model_key]
        mc = conditions[conditions["model_key"] == model_key]
        for lkey, llabel in layer_defs:
            sub = mdf if lkey == "overall" else mdf[mdf["layer"] == lkey]
            cuse = mc if lkey in ("first_hand", "overall") else None
            rows_a.append(build_slice(sub, cuse, {"model_key": model_key, "model_name": model_name, "layer": lkey, "layer_label": llabel}))

    for lkey, llabel in layer_defs:
        sub = df if lkey == "overall" else df[df["layer"] == lkey]
        cuse = conditions if lkey in ("first_hand", "overall") else None
        rows_b.append(build_slice(sub, cuse, {"scope": "Both Models Combined", "layer": lkey, "layer_label": llabel}))

    return pd.DataFrame(rows_a), pd.DataFrame(rows_b)


# --------------------------------------------------------------------------- 64-DNA paired Truth Discount
def compute_paired_dna_truth_discount(df: pd.DataFrame) -> pd.DataFrame:
    """For each Model x POV x 64 cells, compute Rumor, Truth, and matched-pair Truth Discount metrics."""
    rows = []
    for model_key, model_name in bcr.MODEL_NAMES.items():
        mdf = df[df["model_key"] == model_key]
        for pov_key, _, layer_filter in bcr.POV_DEFS:
            sub_pov = mdf if layer_filter is None else mdf[mdf["layer"] == layer_filter]
            for cell_id, csub in sub_pov.groupby("cell_id", sort=True):
                first = csub.iloc[0]
                r_sub = csub[csub["truth"] == 0]
                t_sub = csub[csub["truth"] == 1]
                td, td_lo, td_hi, td_p, n_pairs = _paired_diff_summary(csub, "belief", 1.0)
                td0, _, _, _, n_pairs_sil = _paired_diff_summary(csub, "belief_sil0", 1.0)
                td05, _, _, _, _ = _paired_diff_summary(csub, "belief_sil05", 1.0)
                d_go, _, _, _, n_pairs_go = _paired_diff_summary(csub, "is_go", 100.0)
                r_bel = bcr._mean_or_nan(r_sub["belief"])
                t_bel = bcr._mean_or_nan(t_sub["belief"])
                r_go = bcr._pct(r_sub["is_go"])
                t_go = bcr._pct(t_sub["is_go"])
                row = {
                    "model_key": model_key,
                    "model_name": model_name,
                    "pov": pov_key,
                    "cell_id": int(cell_id),
                    "cell_name": first["cell_name"],
                    "n_pairs_used": n_pairs,
                    "n_pairs_used_go": n_pairs_go,
                    "n_pairs_used_sil": n_pairs_sil,
                    "rumor_valid_n": int(r_sub["is_valid"].sum()),
                    "truth_valid_n": int(t_sub["is_valid"].sum()),
                    "rumor_mentioned_n": int(r_sub["belief"].notna().sum()),
                    "truth_mentioned_n": int(t_sub["belief"].notna().sum()),
                    "rumor_belief": r_bel,
                    "truth_belief": t_bel,
                    "truth_discount": td,
                    "td_ci_low": td_lo,
                    "td_ci_high": td_hi,
                    "td_p": td_p,
                    "td_sil0": td0,
                    "td_sil05": td05,
                    "rumor_go_pct": r_go,
                    "truth_go_pct": t_go,
                    "diff_go_pp": d_go,
                    "rumor_skip_pct": 100.0 - r_go,
                    "truth_skip_pct": 100.0 - t_go,
                }
                for lbl in bcr.LABELS:
                    rp = bcr._pct(r_sub[f"label_{lbl}"])
                    tp = bcr._pct(t_sub[f"label_{lbl}"])
                    row[f"rumor_{lbl}_pct"] = rp
                    row[f"truth_{lbl}_pct"] = tp
                    row[f"diff_{lbl}_pp"] = tp - rp
                rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- pooled Truth x Knob symmetry & TD model
def _pooled_grid(design_info) -> tuple[pd.DataFrame, np.ndarray]:
    rows = [
        {**{f: vals[i] for i, (f, _, _) in enumerate(bcr.FACTORS)}, "real_artist": artist, "truth": truth}
        for vals in itertools.product(*((a, b) for _, a, b in bcr.FACTORS))
        for artist in bcr.ARTISTS
        for truth in (0, 1)
    ]
    grid = bcr._categorical_frame(pd.DataFrame(rows))
    matrix = np.asarray(patsy.build_design_matrices([design_info], grid)[0], dtype=float)
    return grid, matrix


def compute_symmetry_and_td_tests(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Pooled Rumor vs Truth symmetry test across all 10 planned contrasts + 4-combo interaction TD comparisons."""
    grid_cache: dict[str, tuple[pd.DataFrame, np.ndarray]] = {}
    td_rows, combo_rows, simple_rows = [], [], []
    crit = float(norm.ppf(0.975))

    for model_key, model_name in bcr.MODEL_NAMES.items():
        mdf = df[df["model_key"] == model_key]
        for pov_key, _, layer_filter in bcr.POV_DEFS:
            sub_pov = mdf if layer_filter is None else mdf[mdf["layer"] == layer_filter]
            for outcome_col, outcome_label, is_pct in bcr.OUTCOME_SPECS:
                work = sub_pov[sub_pov[outcome_col].notna()].copy()
                work["outcome"] = work[outcome_col].astype(float) * (100.0 if is_pct else 1.0)
                work = bcr._categorical_frame(work)
                n_obs = int(len(work))
                n_pairs = int(work["pair_id"].nunique())

                design = smf.ols(FORMULA_POOLED, work)
                design_info = design.data.design_info
                if pov_key not in grid_cache:
                    grid_cache[pov_key] = _pooled_grid(design_info)
                grid_df, grid_mat = grid_cache[pov_key]

                fit = design.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(work["pair_id"])[0]})
                beta = np.asarray(fit.params, dtype=float)
                cov = np.asarray(fit.cov_params(), dtype=float)

                # Spec LMM companion check on conditional Belief (groups=run_id, matching confirmatory_analysis.py)
                lmm_beta, lmm_cov, lmm_status = None, None, "not_run"
                if outcome_col == "belief":
                    with warnings.catch_warnings(record=True):
                        warnings.simplefilter("always")
                        lmm_fit = None
                        for method in ("lbfgs", "powell"):
                            try:
                                cand = smf.mixedlm(FORMULA_POOLED, work, groups=work["run_id"]).fit(reml=True, method=method)
                                if cand.converged:
                                    lmm_fit = cand
                                    break
                            except Exception:
                                continue
                        if lmm_fit is not None:
                            try:
                                re_var = float(np.asarray(lmm_fit.cov_re, dtype=float)[0, 0])
                                lmm_beta = np.asarray(lmm_fit.fe_params, dtype=float)
                                lmm_cov = np.asarray(
                                    lmm_fit.cov_params().loc[lmm_fit.fe_params.index, lmm_fit.fe_params.index],
                                    dtype=float,
                                )
                                lmm_status = "boundary_re_var0" if re_var <= 1e-10 else "converged"
                            except Exception as exc:
                                lmm_status = f"error:{type(exc).__name__}"
                        else:
                            lmm_status = "nonconverged"

                unit = "pp" if is_pct else "belief"
                meta = {
                    "model_key": model_key,
                    "model_name": model_name,
                    "pov": pov_key,
                    "outcome": outcome_col,
                    "outcome_label": outcome_label,
                    "unit": unit,
                    "n_obs": n_obs,
                    "n_pairs": n_pairs,
                }
                raw_p_list: list[float] = []
                batch: list[dict] = []

                def add_contrast(test_type: str, factor_id: str, contrast_lbl: str,
                                 vec_rumor: np.ndarray, vec_truth: np.ndarray) -> None:
                    vec_td = vec_truth - vec_rumor
                    eff_r, se_r, r_lo, r_hi, p_r = bcr._contrast_stats(vec_rumor, beta, cov, crit)
                    eff_t, se_t, t_lo, t_hi, p_t = bcr._contrast_stats(vec_truth, beta, cov, crit)
                    eff_d, se_d, d_lo, d_hi, p_d = bcr._contrast_stats(vec_td, beta, cov, crit)
                    lmm_d, lmm_p = float("nan"), float("nan")
                    if lmm_beta is not None and lmm_cov is not None:
                        lmm_d, _, _, _, lmm_p = bcr._contrast_stats(vec_td, lmm_beta, lmm_cov, crit)
                    raw_p_list.append(p_d if math.isfinite(p_d) else 1.0)
                    batch.append({
                        **meta,
                        "test_type": test_type,
                        "factor": factor_id,
                        "contrast": contrast_lbl,
                        "effect_rumor": eff_r,
                        "rumor_ci_low": r_lo,
                        "rumor_ci_high": r_hi,
                        "p_rumor": p_r,
                        "effect_truth": eff_t,
                        "truth_ci_low": t_lo,
                        "truth_ci_high": t_hi,
                        "p_truth": p_t,
                        "effect_td": eff_d,
                        "se_td_pair_clustered": se_d,
                        "td_ci_low": d_lo,
                        "td_ci_high": d_hi,
                        "p_td_clustered": p_d,
                        "lmm_td_effect": lmm_d,
                        "lmm_td_p": lmm_p,
                        "lmm_status": lmm_status,
                    })

                # 6 Main Knobs
                for factor, lvl_a, lvl_b in bcr.FACTORS:
                    vr = grid_mat[((grid_df["truth"] == 0) & (grid_df[factor] == lvl_a)).to_numpy()].mean(axis=0) - \
                         grid_mat[((grid_df["truth"] == 0) & (grid_df[factor] == lvl_b)).to_numpy()].mean(axis=0)
                    vt = grid_mat[((grid_df["truth"] == 1) & (grid_df[factor] == lvl_a)).to_numpy()].mean(axis=0) - \
                         grid_mat[((grid_df["truth"] == 1) & (grid_df[factor] == lvl_b)).to_numpy()].mean(axis=0)
                    add_contrast("main", factor, f"{lvl_a} - {lvl_b}", vr, vt)

                # 4 Planned Interactions + 16-DNA Combo Rumor/Truth/TD + Simple Effects
                for fa, fb in bcr.INTERACTIONS:
                    a1, a0 = bcr.FACTOR_LEVELS[fa]
                    b1, b0 = bcr.FACTOR_LEVELS[fb]
                    pair_id = f"{fa}_x_{fb}"
                    pair_label = f"{fa} x {fb}"
                    vecs_r, vecs_t = {}, {}
                    combo_counts = {}
                    for va in (a1, a0):
                        for vb in (b1, b0):
                            vr_c = grid_mat[((grid_df["truth"] == 0) & (grid_df[fa] == va) & (grid_df[fb] == vb)).to_numpy()].mean(axis=0)
                            vt_c = grid_mat[((grid_df["truth"] == 1) & (grid_df[fa] == va) & (grid_df[fb] == vb)).to_numpy()].mean(axis=0)
                            vecs_r[(va, vb)], vecs_t[(va, vb)] = vr_c, vt_c
                            w_combo = work[(work[fa] == va) & (work[fb] == vb)]
                            r_n_c = int((w_combo["truth"] == 0).sum())
                            t_n_c = int((w_combo["truth"] == 1).sum())
                            p_n_c = int(w_combo["pair_id"].nunique())
                            combo_counts[(va, vb)] = (r_n_c + t_n_c, p_n_c)
                            mr, _, _, _, _ = bcr._contrast_stats(vr_c, beta, cov, crit)
                            mt, _, _, _, _ = bcr._contrast_stats(vt_c, beta, cov, crit)
                            mtd, _, td_lo, td_hi, p_td = bcr._contrast_stats(vt_c - vr_c, beta, cov, crit)
                            combo_rows.append({
                                **meta,
                                "pair_id": pair_id,
                                "pair_label": pair_label,
                                "combo_label": f"{va} + {vb}",
                                "rumor_n_obs": r_n_c,
                                "truth_n_obs": t_n_c,
                                "n_pairs_combo": p_n_c,
                                "rumor_mean": mr,
                                "truth_mean": mt,
                                "truth_discount": mtd,
                                "td_ci_low": td_lo,
                                "td_ci_high": td_hi,
                                "p_td_vs_zero": p_td,
                            })

                    vr_did = (vecs_r[(a1, b1)] - vecs_r[(a0, b1)]) - (vecs_r[(a1, b0)] - vecs_r[(a0, b0)])
                    vt_did = (vecs_t[(a1, b1)] - vecs_t[(a0, b1)]) - (vecs_t[(a1, b0)] - vecs_t[(a0, b0)])
                    add_contrast("interaction", f"{fa}_by_{fb}", f"({a1}-{a0} | {b1}) - ({a1}-{a0} | {b0})", vr_did, vt_did)

                    simple_specs = [
                        (f"{fa} effect | {fb}={b0}", (a1, b0), (a0, b0), f"{a1}+{b0} vs {a0}+{b0}"),
                        (f"{fa} effect | {fb}={b1}", (a1, b1), (a0, b1), f"{a1}+{b1} vs {a0}+{b1}"),
                        (f"{fb} effect | {fa}={a0}", (a0, b1), (a0, b0), f"{a0}+{b1} vs {a0}+{b0}"),
                        (f"{fb} effect | {fa}={a1}", (a1, b1), (a1, b0), f"{a1}+{b1} vs {a1}+{b0}"),
                    ]
                    for desc, k_hi, k_lo, clbl in simple_specs:
                        dr = vecs_r[k_hi] - vecs_r[k_lo]
                        dt = vecs_t[k_hi] - vecs_t[k_lo]
                        n_obs_hi, n_pairs_hi = combo_counts[k_hi]
                        n_obs_lo, n_pairs_lo = combo_counts[k_lo]
                        er, _, _, _, pr = bcr._contrast_stats(dr, beta, cov, crit)
                        et, _, _, _, pt = bcr._contrast_stats(dt, beta, cov, crit)
                        ed, _, dlo, dhi, pd_val = bcr._contrast_stats(dt - dr, beta, cov, crit)
                        simple_rows.append({
                            **meta,
                            "pair_id": pair_id,
                            "pair_label": pair_label,
                            "comparison": desc,
                            "combo_contrast": clbl,
                            "n_obs_hi": n_obs_hi,
                            "n_pairs_hi": n_pairs_hi,
                            "n_obs_lo": n_obs_lo,
                            "n_pairs_lo": n_pairs_lo,
                            "effect_rumor": er,
                            "p_rumor": pr,
                            "effect_truth": et,
                            "p_truth": pt,
                            "effect_td": ed,
                            "td_ci_low": dlo,
                            "td_ci_high": dhi,
                            "p_td_clustered": pd_val,
                        })

                holm_ps = bcr._holm_adjust(raw_p_list)
                for row, hp in zip(batch, holm_ps):
                    row["p_td_holm"] = hp
                    td_rows.append(row)

    return pd.DataFrame(td_rows), pd.DataFrame(combo_rows), pd.DataFrame(simple_rows)


# --------------------------------------------------------------------------- Model vs Model formal comparison
def compute_model_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Compare DeepSeek-V4-Flash minus Qwen3.8-Flash on Rumor, Truth, and Truth Discount."""
    rows = []
    crit = float(norm.ppf(0.975))
    outcomes = (
        ("belief", "Belief Score", False),
        ("is_go", "GO Rate (%)", True),
        ("label_NOT_MENTIONED", "NOT_MENTIONED (%)", True),
        ("label_FACT", "FACT (%)", True),
        ("label_UNCERTAIN", "UNCERTAIN (%)", True),
        ("label_SKEPTICAL", "SKEPTICAL (%)", True),
    )
    for pov_key, pov_title, layer_filter in bcr.POV_DEFS:
        sub_pov = df if layer_filter is None else df[df["layer"] == layer_filter]
        for ocol, olabel, is_pct in outcomes:
            work = sub_pov[sub_pov[ocol].notna()].copy()
            work["outcome"] = work[ocol].astype(float) * (100.0 if is_pct else 1.0)
            work["is_deepseek"] = (work["model_key"] == "deepseek_v4_flash").astype(float)
            fit = smf.ols("outcome ~ truth * is_deepseek", work).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(work["pair_cluster"])[0]}
            )
            beta = np.asarray(fit.params, dtype=float)
            cov = np.asarray(fit.cov_params(), dtype=float)
            # Design columns: [Intercept, truth, is_deepseek, truth:is_deepseek]
            ds_r, _, _, _, p_r = bcr._contrast_stats(np.array([0.0, 0.0, 1.0, 0.0]), beta, cov, crit)
            ds_t, _, _, _, p_t = bcr._contrast_stats(np.array([0.0, 0.0, 1.0, 1.0]), beta, cov, crit)
            ds_td, _, lo_td, hi_td, p_td = bcr._contrast_stats(np.array([0.0, 0.0, 0.0, 1.0]), beta, cov, crit)

            m_ds_r = float(np.array([1.0, 0.0, 1.0, 0.0]) @ beta)
            m_qw_r = float(np.array([1.0, 0.0, 0.0, 0.0]) @ beta)
            m_ds_t = float(np.array([1.0, 1.0, 1.0, 1.0]) @ beta)
            m_qw_t = float(np.array([1.0, 1.0, 0.0, 0.0]) @ beta)
            rows.append({
                "pov": pov_key,
                "pov_title": pov_title,
                "outcome": ocol,
                "outcome_label": olabel,
                "unit": "pp" if is_pct else "belief",
                "n_obs_rumor": int((work["truth"] == 0).sum()),
                "n_obs_truth": int((work["truth"] == 1).sum()),
                "n_pairs_total": int(work["pair_cluster"].nunique()),
                "deepseek_rumor": m_ds_r,
                "qwen_rumor": m_qw_r,
                "diff_rumor_ds_minus_qw": ds_r,
                "p_rumor": p_r,
                "deepseek_truth": m_ds_t,
                "qwen_truth": m_qw_t,
                "diff_truth_ds_minus_qw": ds_t,
                "p_truth": p_t,
                "deepseek_td": m_ds_t - m_ds_r,
                "qwen_td": m_qw_t - m_qw_r,
                "diff_td_ds_minus_qw": ds_td,
                "td_ci_low": lo_td,
                "td_ci_high": hi_td,
                "p_td": p_td,
            })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- markdown rendering
def render_markdown(
    table_a: pd.DataFrame,
    table_b: pd.DataFrame,
    dna_df: pd.DataFrame,
    td_knobs: pd.DataFrame,
    combos_df: pd.DataFrame,
    simple_df: pd.DataFrame,
    model_cmp: pd.DataFrame,
) -> str:
    ov_b = table_b.loc[table_b["layer"] == "overall"].iloc[0]
    total_towns = int(ov_b["n_towns_rumor"] + ov_b["n_towns_truth"])
    total_pairs_exp = int(ov_b["n_pairs_used_go"])

    lines = [
        "# Report 3: Truth Discount & Comparisons (Truth Twin − Rumor Twin)",
        "",
        f"**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Towns:** {total_towns:,} ({int(ov_b['n_towns_rumor']):,} Rumor + {int(ov_b['n_towns_truth']):,} Truth) | **Twin Pairs:** {total_pairs_exp:,} | **Clustering:** Twin Pair (`pair_id`)",
        "",
        "### Methodological Policy (Dynamic Denominators — Never Hardcoded)",
        "- **Core Estimand:** $\\text{Truth Discount} = \\text{Belief}_{\\text{Truth Twin}} - \\text{Belief}_{\\text{Rumor Twin}}$ (`Matched-Pair Mean ± 1.96·SE`), alongside $\\Delta\\text{GO}$, $\\Delta\\text{Omission}$, and categorical label shifts.",
        "- **Invalid Exclusion:** Individual `judgment_status = invalid` rows stay `NaN` (never zero-imputed, and without discarding valid listeners in the same town).",
        "- **Dynamic Denominators:** `R/T Ment. N` = non-NaN mentioning listeners used for Rumor/Truth conditional `Belief`; `Belief Pairs` = complete twin pairs having valid mentioning listeners in both twins; `GO Pairs` = complete twin pairs with verification decisions.",
        "- **Symmetry / Truth Discount Model:** Pooled `outcome ~ truth * (6 main knobs + 4 interactions) + C(real_artist)` OLS / LPM with Twin-Pair-Clustered SEs (`groups=pair_id`), two-sided Wald z-tests, and Holm adjustment across all 10 planned contrasts. `Belief` also reports the spec's REML LMM (`1 | run_id`).",
        "",
        "---",
        "",
        "## 1. Overall Truth vs. Rumor & Matched Truth Discount Summary",
        "",
        "*Estimator: Matched-Pair Mean (`Truth − Rumor`), Normal 95% CI (`Mean ± 1.96·SE`); `GO %` over Expected N, `NM %` over Valid N.*",
        "",
        "### Table 1A: Per Model × Layer",
        "",
        "| Model | Layer | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Sil=0.0 TD | Sil=0.5 TD | GO Pairs | Rumor GO % | Truth GO % | Δ GO | Rumor NM % | Truth NM % | Δ NM |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in table_a.iterrows():
        ci = f"[{bcr._f3(r['td_ci_low'])}, {bcr._f3(r['td_ci_high'])}]"
        n_rt = f"{int(r['rumor_mentioned_n']):,} / {int(r['truth_mentioned_n']):,}"
        lines.append(
            f"| {r['model_name']} | {r['layer_label']} | {n_rt} | {int(r['n_pairs_used_belief']):,} | "
            f"{bcr._f3(r['rumor_belief'])} | {bcr._f3(r['truth_belief'])} | **{bcr._f3(r['truth_discount'])}** {ci} | "
            f"{bcr._f3(r['td_sil0'])} | {bcr._f3(r['td_sil05'])} | {int(r['n_pairs_used_go']):,} | "
            f"{bcr._f1(r['rumor_go_pct'])} | {bcr._f1(r['truth_go_pct'])} | {r['diff_go_pp']:+.1f} pp | "
            f"{bcr._f1(r['rumor_nm_pct'])} | {bcr._f1(r['truth_nm_pct'])} | {r['diff_nm_pp']:+.1f} pp |"
        )

    lines += [
        "",
        "### Table 1B: Entire Experiment Average (Both Models Combined)",
        "",
        "| Scope | Layer | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Sil=0.0 TD | Sil=0.5 TD | GO Pairs | Rumor GO % | Truth GO % | Δ GO | Rumor NM % | Truth NM % | Δ NM |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in table_b.iterrows():
        ci = f"[{bcr._f3(r['td_ci_low'])}, {bcr._f3(r['td_ci_high'])}]"
        n_rt = f"{int(r['rumor_mentioned_n']):,} / {int(r['truth_mentioned_n']):,}"
        lines.append(
            f"| {r['scope']} | {r['layer_label']} | {n_rt} | {int(r['n_pairs_used_belief']):,} | "
            f"{bcr._f3(r['rumor_belief'])} | {bcr._f3(r['truth_belief'])} | **{bcr._f3(r['truth_discount'])}** {ci} | "
            f"{bcr._f3(r['td_sil0'])} | {bcr._f3(r['td_sil05'])} | {int(r['n_pairs_used_go']):,} | "
            f"{bcr._f1(r['rumor_go_pct'])} | {bcr._f1(r['truth_go_pct'])} | {r['diff_go_pp']:+.1f} pp | "
            f"{bcr._f1(r['rumor_nm_pct'])} | {bcr._f1(r['truth_nm_pct'])} | {r['diff_nm_pp']:+.1f} pp |"
        )

    lines += [
        "",
        "---",
        "",
        "## 2. Model Comparison (`DeepSeek-V4-Flash − Qwen3.8-Flash`)",
        "",
        "*Estimator: Pooled `outcome ~ truth * is_deepseek` OLS / LPM with Pair-Clustered SEs (`groups = model__pair_id`) & two-sided Wald z-test.*",
        "",
        "| POV | Outcome | Non-NaN N (R / T) | Pairs | DeepSeek Rumor | Qwen Rumor | Δ Rumor (p) | DeepSeek Truth | Qwen Truth | Δ Truth (p) | DeepSeek TD | Qwen TD | Δ TD (DS − Qwen) | 95% CI | p (clustered) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in model_cmp.iterrows():
        is_pct = r["unit"] == "pp"
        fv = (lambda x: f"{x:.1f}%") if is_pct else (lambda x: f"{x:.3f}")
        fe = (lambda x: f"{x:+.1f} pp") if is_pct else (lambda x: f"{x:+.3f}")
        ci = f"[{fe(r['td_ci_low']).replace(' pp','')}, {fe(r['td_ci_high'])}]"
        n_rt = f"{int(r['n_obs_rumor']):,} / {int(r['n_obs_truth']):,}"
        lines.append(
            f"| {r['pov']} | {r['outcome_label']} | {n_rt} | {int(r['n_pairs_total']):,} | {fv(r['deepseek_rumor'])} | {fv(r['qwen_rumor'])} | {fe(r['diff_rumor_ds_minus_qw'])} ({bcr._fp(r['p_rumor'])}) | "
            f"{fv(r['deepseek_truth'])} | {fv(r['qwen_truth'])} | {fe(r['diff_truth_ds_minus_qw'])} ({bcr._fp(r['p_truth'])}) | "
            f"{fv(r['deepseek_td'])} | {fv(r['qwen_td'])} | **{fe(r['diff_td_ds_minus_qw'])}{bcr._stars(r['p_td'])}** | {ci} | {bcr._fp(r['p_td'])} |"
        )

    lines += ["", "---", "", "## 3. Paired Symmetry & Truth Discount Tests (10 Planned Contrasts)"]
    for model_key, model_name in bcr.MODEL_NAMES.items():
        lines += ["", f"### Model: {model_name}"]
        for pov_key, pov_title, _ in bcr.POV_DEFS:
            lines += ["", f"#### {pov_title}"]
            sub_k = td_knobs[(td_knobs["model_key"] == model_key) & (td_knobs["pov"] == pov_key)]
            for ocol, olabel, is_pct in bcr.OUTCOME_SPECS:
                if ocol in ("belief_sil0", "belief_sil05"):
                    continue
                ok = sub_k[sub_k["outcome"] == ocol]
                fe = (lambda x: f"{x:+.2f} pp") if is_pct else (lambda x: f"{x:+.4f}")
                lines += [
                    "",
                    f"**Outcome: {olabel}** (n={ok['n_obs'].iloc[0]:,}, pairs={ok['n_pairs'].iloc[0]:,})",
                    "",
                    "| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |"
                    + (" LMM TD Check |" if ocol == "belief" else ""),
                    "|---|---|---:|---:|---:|---:|---:|---:|" + ("---:|" if ocol == "belief" else ""),
                ]
                for _, kr in ok.iterrows():
                    ci = f"[{fe(kr['td_ci_low']).replace(' pp','')}, {fe(kr['td_ci_high'])}]"
                    row_s = (
                        f"| {kr['test_type']} | {kr['factor']} (`{kr['contrast']}`) | {fe(kr['effect_rumor'])} ({bcr._fp(kr['p_rumor'])}) | "
                        f"{fe(kr['effect_truth'])} ({bcr._fp(kr['p_truth'])}) | **{fe(kr['effect_td'])}{bcr._stars(kr['p_td_holm'])}** | "
                        f"{ci} | {bcr._fp(kr['p_td_clustered'])} | {bcr._fp(kr['p_td_holm'])} |"
                    )
                    if ocol == "belief":
                        lmm_s = f"{kr['lmm_td_effect']:+.4f} (p={bcr._fp(kr['lmm_td_p'])})" if pd.notna(kr["lmm_td_effect"]) else kr["lmm_status"]
                        row_s += f" {lmm_s} |"
                    lines.append(row_s)

    lines += ["", "---", "", "## 4. Top 10 Largest & Bottom 10 Smallest Truth Discount DNAs (`Truth − Rumor` — Matched-Pair Mean ± 1.96·SE)"]
    for model_key, model_name in bcr.MODEL_NAMES.items():
        lines += ["", f"### Model: {model_name}"]
        for pov_key, pov_title, _ in bcr.POV_DEFS:
            lines += ["", f"#### {pov_title}"]
            sub_d = dna_df[(dna_df["model_key"] == model_key) & (dna_df["pov"] == pov_key)]
            top10 = sub_d.sort_values(by=["truth_discount", "truth_belief", "cell_id"], ascending=[False, False, True]).head(10)
            bot10 = sub_d.sort_values(by=["truth_discount", "truth_belief", "cell_id"], ascending=[True, True, True]).head(10)
            for heading, tbl in (("Top 10 Largest Truth Discount (Best Truth Discrimination)", top10),
                                 ("Bottom 10 Smallest Truth Discount (Most Discounted)", bot10)):
                lines += [
                    "",
                    f"*{heading}:*",
                    "",
                    "| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |",
                    "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
                ]
                for idx, (_, dr) in enumerate(tbl.iterrows(), start=1):
                    ci = f"[{bcr._f3(dr['td_ci_low'])}, {bcr._f3(dr['td_ci_high'])}]"
                    n_rt = f"{int(dr['rumor_mentioned_n'])} / {int(dr['truth_mentioned_n'])}"
                    lines.append(
                        f"| {idx} | {dr['cell_id']} | {dr['cell_name']} | {n_rt} | {int(dr['n_pairs_used'])} | {bcr._f3(dr['rumor_belief'])} | "
                        f"{bcr._f3(dr['truth_belief'])} | **{bcr._f3(dr['truth_discount'])}** {ci} | "
                        f"{bcr._f1(dr['rumor_go_pct'])} | {bcr._f1(dr['truth_go_pct'])} | {dr['diff_go_pp']:+.1f} pp |"
                    )
    return "\n".join(lines)


# --------------------------------------------------------------------------- interactive html rendering
def render_html(
    table_a: pd.DataFrame,
    table_b: pd.DataFrame,
    dna_df: pd.DataFrame,
    td_knobs: pd.DataFrame,
    combos_df: pd.DataFrame,
    simple_df: pd.DataFrame,
    model_cmp: pd.DataFrame,
) -> str:
    payload = {
        "summary_a": table_a.replace({np.nan: None}).to_dict(orient="records"),
        "summary_b": table_b.replace({np.nan: None}).to_dict(orient="records"),
        "dna": dna_df.replace({np.nan: None}).to_dict(orient="records"),
        "knobs": td_knobs.replace({np.nan: None}).to_dict(orient="records"),
        "combos": combos_df.replace({np.nan: None}).to_dict(orient="records"),
        "simple": simple_df.replace({np.nan: None}).to_dict(orient="records"),
        "model_cmp": model_cmp.replace({np.nan: None}).to_dict(orient="records"),
        "outcomes": [{"key": k, "label": lbl, "is_pct": p} for k, lbl, p in bcr.OUTCOME_SPECS],
        "butterfly_metrics": [{"key": k, "label": lbl, "is_pct": p} for k, lbl, p in BUTTERFLY_METRICS],
    }
    payload_json = json.dumps(payload).replace("</", "<\\/")

    ov_b = table_b.loc[table_b["layer"] == "overall"].iloc[0]
    total_towns = int(ov_b["n_towns_rumor"] + ov_b["n_towns_truth"])
    total_pairs_exp = int(ov_b["n_pairs_used_go"])

    def sum_rows(df_in: pd.DataFrame, first_col: str) -> str:
        out = []
        for _, r in df_in.iterrows():
            cls = "row-overall" if r["layer"] == "overall" else ""
            ci = f"[{bcr._f3(r['td_ci_low'])}, {bcr._f3(r['td_ci_high'])}]"
            n_rt = f"{int(r['rumor_mentioned_n']):,} / {int(r['truth_mentioned_n']):,}"
            out.append(
                f"<tr class='{cls}'>"
                f"<td><b>{html.escape(str(r[first_col]))}</b></td>"
                f"<td>{html.escape(str(r['layer_label']))}</td>"
                f"<td class='num'>{n_rt}</td>"
                f"<td class='num'>{int(r['n_pairs_used_belief']):,}</td>"
                f"<td class='num rumor-col'>{bcr._f3(r['rumor_belief'])}</td>"
                f"<td class='num truth-col'>{bcr._f3(r['truth_belief'])}</td>"
                f"<td class='num strong'>{bcr._f3(r['truth_discount'])} <span class='muted-sm'>{ci}</span></td>"
                f"<td class='num'>{bcr._f3(r['td_sil0'])}</td>"
                f"<td class='num'>{bcr._f3(r['td_sil05'])}</td>"
                f"<td class='num'>{int(r['n_pairs_used_go']):,}</td>"
                f"<td class='num'>{bcr._f1(r['rumor_go_pct'])}</td>"
                f"<td class='num'>{bcr._f1(r['truth_go_pct'])}</td>"
                f"<td class='num'>{r['diff_go_pp']:+.1f} pp</td>"
                f"<td class='num'>{bcr._f1(r['rumor_nm_pct'])}</td>"
                f"<td class='num'>{bcr._f1(r['truth_nm_pct'])}</td>"
                f"<td class='num'>{r['diff_nm_pp']:+.1f} pp</td>"
                f"</tr>"
            )
        return "\n".join(out)

    mcmp_rows = []
    for _, r in model_cmp.iterrows():
        is_pct = r["unit"] == "pp"
        fv = (lambda x: f"{x:.1f}%") if is_pct else (lambda x: f"{x:.3f}")
        fe = (lambda x: f"{x:+.1f} pp") if is_pct else (lambda x: f"{x:+.3f}")
        ci = f"[{fe(r['td_ci_low']).replace(' pp','')}, {fe(r['td_ci_high'])}]"
        cls = "ns" if r["p_td"] >= 0.05 else ("sig-pos" if r["diff_td_ds_minus_qw"] >= 0 else "sig-neg")
        n_rt = f"{int(r['n_obs_rumor']):,} / {int(r['n_obs_truth']):,}"
        mcmp_rows.append(
            f"<tr><td>{html.escape(r['pov'])}</td><td><b>{html.escape(r['outcome_label'])}</b></td>"
            f"<td class='num'>{n_rt}</td><td class='num'>{int(r['n_pairs_total']):,}</td>"
            f"<td class='num'>{fv(r['deepseek_rumor'])}</td><td class='num'>{fv(r['qwen_rumor'])}</td>"
            f"<td class='num'>{fe(r['diff_rumor_ds_minus_qw'])} <span class='muted-sm'>({bcr._fp(r['p_rumor'])})</span></td>"
            f"<td class='num'>{fv(r['deepseek_truth'])}</td><td class='num'>{fv(r['qwen_truth'])}</td>"
            f"<td class='num'>{fe(r['diff_truth_ds_minus_qw'])} <span class='muted-sm'>({bcr._fp(r['p_truth'])})</span></td>"
            f"<td class='num'>{fv(r['deepseek_td'])}</td><td class='num'>{fv(r['qwen_td'])}</td>"
            f"<td class='num {cls}'>{fe(r['diff_td_ds_minus_qw'])}{bcr._stars(r['p_td'])}</td>"
            f"<td class='num'>{ci}</td><td class='num {cls}'>{bcr._fp(r['p_td'])}</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Report 3: Truth Discount &amp; Comparisons (Gemini 3.7 Flash)</title>
<style>
  :root {{ --accent: #2c3e50; --rumor: #c0392b; --truth: #1e8449; --bg: #f6f7fb; --card: #ffffff; --border: #dfe4ec; --text: #1c2430; --muted: #5b6778; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: var(--bg); color: var(--text); line-height: 1.45; }}
  .wrap {{ max-width: 1460px; margin: 0 auto; padding: 24px; }}
  header {{ background: var(--card); border: 1px solid var(--border); border-left: 6px solid var(--accent); border-radius: 10px; padding: 20px 24px; margin-bottom: 20px; }}
  .badge {{ display: inline-block; background: var(--accent); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: .06em; padding: 3px 9px; border-radius: 999px; margin-bottom: 6px; }}
  h1 {{ margin: 4px 0 8px; font-size: 24px; }}
  h2 {{ margin: 22px 0 10px; font-size: 18px; border-bottom: 2px solid var(--border); padding-bottom: 6px; }}
  h3 {{ margin: 16px 0 8px; font-size: 15px; }}
  .meta, .muted-sm {{ color: var(--muted); font-size: 12px; }}
  .note {{ background: #f1f4f9; border-left: 3px solid #6b7b8f; padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-top: 10px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; margin-bottom: 18px; }}
  .scroll {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  th, td {{ padding: 7px 9px; border-bottom: 1px solid var(--border); text-align: left; white-space: nowrap; }}
  th {{ background: #f4f6f9; font-weight: 600; color: #344054; }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.strong {{ font-weight: 700; color: var(--accent); }}
  td.rumor-col {{ color: var(--rumor); font-weight: 600; }}
  td.truth-col {{ color: var(--truth); font-weight: 600; }}
  tr.row-overall {{ background: #f8fafc; font-weight: 600; }}
  tr:hover {{ background: #f4f8ff; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 14px; }}
  .btn-group {{ display: inline-flex; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: #fff; }}
  .btn {{ border: 0; background: transparent; padding: 7px 12px; font-size: 12.5px; font-weight: 600; cursor: pointer; color: var(--muted); }}
  .btn.active {{ background: var(--accent); color: #fff; }}
  select {{ padding: 7px 10px; border: 1px solid var(--border); border-radius: 7px; font-size: 13px; background: #fff; }}
  .sig-pos {{ color: #166534; font-weight: 700; }}
  .sig-neg {{ color: #991b1b; font-weight: 700; }}
  .ns {{ color: #64748b; }}
  .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #eef2f7; font-size: 11px; font-weight: 700; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr; gap: 16px; }}
  .svg-box {{ width: 100%; overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; padding: 10px; background: #fcfdff; }}
  .legend {{ display: flex; gap: 18px; font-size: 12.5px; margin-bottom: 8px; align-items: center; }}
  .dot {{ width: 11px; height: 11px; border-radius: 50%; display: inline-block; margin-right: 5px; }}
  .sq {{ width: 12px; height: 12px; border-radius: 2px; display: inline-block; margin-right: 5px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="badge">TRUTH DISCOUNT &amp; SYMMETRY COMPARISONS</div>
    <h1>Report 3: Truth Discount &amp; Comparisons (Truth Twin &minus; Rumor Twin)</h1>
    <div class="meta">{total_towns:,} towns ({int(ov_b['n_towns_rumor']):,} Rumor + {int(ov_b['n_towns_truth']):,} Truth) &bull; {total_pairs_exp:,} matched twin pairs &bull; Single Judge: Gemini 3.7 Flash &bull; Clustering: Twin Pair (<code>pair_id</code>)</div>
    <div class="note">
      <b>Dynamic Denominators (Never Hardcoded):</b> <b>Truth Discount</b> = <code>Truth Belief &minus; Rumor Belief</code>.
      Individual <code>invalid</code> judge rows stay <code>NaN</code> (never zero-imputed, and without dropping valid listeners in the same town).
      Every table reports the exact non-NaN count (<code>Ment. N</code> for conditional <code>Belief</code>, <code>Valid N</code> for labels/silence, <code>Pairs</code> for matched-pair comparisons) and exact estimator.
    </div>
  </header>

  <div class="card">
    <h2>1. Overall Rumor vs. Truth &amp; Matched Truth Discount Summary</h2>
    <div class="meta" style="margin-bottom:8px;"><b>Estimator:</b> Matched-Pair Mean (<code>Truth &minus; Rumor</code>), Normal 95% CI (<code>Mean &plusmn; 1.96&middot;SE</code>); <code>GO %</code> over Expected N, <code>NM %</code> over Valid N.</div>
    <h3>Table 1A: Per Model &times; Layer</h3>
    <div class="scroll">
      <table>
        <thead><tr><th>Model</th><th>Layer</th><th class="num">Ment. N (R / T)</th><th class="num">Belief Pairs</th><th class="num">Rumor Belief</th><th class="num">Truth Belief</th><th class="num">Truth Discount [95% CI]</th><th class="num">Sil=0.0 TD</th><th class="num">Sil=0.5 TD</th><th class="num">GO Pairs</th><th class="num">Rumor GO %</th><th class="num">Truth GO %</th><th class="num">&Delta; GO</th><th class="num">Rumor NM %</th><th class="num">Truth NM %</th><th class="num">&Delta; NM</th></tr></thead>
        <tbody>{sum_rows(table_a, "model_name")}</tbody>
      </table>
    </div>
    <h3>Table 1B: Entire Experiment Average (Both Models Combined)</h3>
    <div class="scroll">
      <table>
        <thead><tr><th>Scope</th><th>Layer</th><th class="num">Ment. N (R / T)</th><th class="num">Belief Pairs</th><th class="num">Rumor Belief</th><th class="num">Truth Belief</th><th class="num">Truth Discount [95% CI]</th><th class="num">Sil=0.0 TD</th><th class="num">Sil=0.5 TD</th><th class="num">GO Pairs</th><th class="num">Rumor GO %</th><th class="num">Truth GO %</th><th class="num">&Delta; GO</th><th class="num">Rumor NM %</th><th class="num">Truth NM %</th><th class="num">&Delta; NM</th></tr></thead>
        <tbody>{sum_rows(table_b, "scope")}</tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>2. Butterfly (Mirror Bar) Comparison Charts: Rumor (Left) vs. Truth (Right)</h2>
    <div class="controls">
      <div class="btn-group" id="bf-model">
        <button class="btn active" data-val="deepseek_v4_flash">DeepSeek-V4-Flash</button>
        <button class="btn" data-val="qwen_3_8_flash">Qwen3.8-Flash</button>
        <button class="btn" data-val="combined">Combined</button>
      </div>
      <div class="btn-group" id="bf-layer">
        <button class="btn active" data-val="overall">Overall (All 12)</button>
        <button class="btn" data-val="first_hand">First-Hand (1-6)</button>
        <button class="btn" data-val="second_hand">Second-Hand (7-12)</button>
      </div>
    </div>
    <div class="legend">
      <span><span class="sq" style="background:var(--rumor)"></span><b>Left: Rumor Towns (False)</b></span>
      <span><span class="sq" style="background:var(--truth)"></span><b>Right: Truth Towns (True)</b></span>
    </div>
    <h3>2A. Categorical Label &amp; Verification Butterfly</h3>
    <div class="svg-box" id="bf-labels-svg"></div>

    <h3>2B. Source DNA Butterfly (Sorted by Gap: Truth &minus; Rumor)</h3>
    <div class="controls">
      <label>Metric: <select id="bf-dna-metric"></select></label>
      <div class="btn-group" id="bf-dna-scope">
        <button class="btn active" data-val="top_bot">Top 12 Largest &amp; Bottom 12 Smallest Gap</button>
        <button class="btn" data-val="all64">All 64 DNAs</button>
      </div>
    </div>
    <div class="svg-box" id="bf-dna-svg"></div>
  </div>

  <div class="card">
    <h2>3. Interactive Explorer: Symmetry Tests (10 Contrasts), 4 Interaction Combos &amp; Top/Bottom DNAs</h2>
    <div class="controls">
      <div class="btn-group" id="model-btns">
        <button class="btn active" data-val="deepseek_v4_flash">DeepSeek-V4-Flash</button>
        <button class="btn" data-val="qwen_3_8_flash">Qwen3.8-Flash</button>
      </div>
      <div class="btn-group" id="pov-btns">
        <button class="btn active" data-val="source">Source POV (All 12)</button>
        <button class="btn" data-val="first_hand">First-Hand (Gatekeeper)</button>
        <button class="btn" data-val="second_hand">Second-Hand (Target)</button>
      </div>
      <label>Outcome: <select id="outcome-select"></select></label>
    </div>

    <h3>3A. Paired Forest Plot: Effect in Rumor vs. Effect in Truth</h3>
    <div class="legend">
      <span><span class="dot" style="background:var(--rumor)"></span>Effect in Rumor Towns</span>
      <span><span class="dot" style="background:var(--truth)"></span>Effect in Truth Towns</span>
      <span class="meta">Line connects Rumor &rarr; Truth (= &Delta; Truth Discount)</span>
    </div>
    <div class="svg-box" id="forest-svg"></div>

    <h3>3B. Full 10-Test Symmetry &amp; Truth Discount Table (Pair-Clustered SEs + Holm across 10)</h3>
    <div class="meta" id="td-meta" style="margin-bottom:8px;"></div>
    <div class="scroll" id="td-table"></div>

    <h3>3C. 4 Planned Interaction Pairs — 16-DNA Combos (Rumor vs. Truth vs. Truth Discount)</h3>
    <div class="controls">
      <div class="btn-group" id="pair-btns">
        <button class="btn active" data-val="closeness_x_reliability">closeness &times; reliability</button>
        <button class="btn" data-val="authority_x_reliability">authority &times; reliability</button>
        <button class="btn" data-val="wealth_x_reliability">wealth &times; reliability</button>
        <button class="btn" data-val="closeness_x_authority">closeness &times; authority</button>
      </div>
    </div>
    <div class="grid-2">
      <div class="scroll" id="combo-table"></div>
      <div class="scroll" id="simple-table"></div>
    </div>

    <h3>3D. Top 10 Largest &amp; Bottom 10 Smallest Truth Discount DNAs</h3>
    <div class="grid-2">
      <div><h4>Top 10 Largest Truth Discount</h4><div class="scroll" id="dna-top"></div></div>
      <div><h4>Bottom 10 Smallest Truth Discount</h4><div class="scroll" id="dna-bot"></div></div>
    </div>
  </div>

  <div class="card">
    <h2>4. Model Comparison: DeepSeek-V4-Flash &minus; Qwen3.8-Flash</h2>
    <div class="meta" style="margin-bottom:8px;"><b>Estimator:</b> Pooled <code>outcome ~ truth * is_deepseek</code> OLS / LPM with Pair-Clustered SEs (<code>groups = model__pair_id</code>) &amp; two-sided Wald z-test.</div>
    <div class="scroll">
      <table>
        <thead><tr><th>POV</th><th>Outcome</th><th class="num">Non-NaN N (R / T)</th><th class="num">Pairs</th><th class="num">DeepSeek Rumor</th><th class="num">Qwen Rumor</th><th class="num">&Delta; Rumor (p)</th><th class="num">DeepSeek Truth</th><th class="num">Qwen Truth</th><th class="num">&Delta; Truth (p)</th><th class="num">DeepSeek TD</th><th class="num">Qwen TD</th><th class="num">&Delta; TD (DS &minus; Qwen)</th><th class="num">95% CI</th><th class="num">p</th></tr></thead>
        <tbody>{"".join(mcmp_rows)}</tbody>
      </table>
    </div>
  </div>
</div>

<script>
const DATA = {payload_json};
let st = {{ bfModel: "deepseek_v4_flash", bfLayer: "overall", bfMetric: "belief", bfScope: "top_bot", model: "deepseek_v4_flash", pov: "source", outcome: "belief", pair: "closeness_x_reliability" }};

const bfSel = document.getElementById("bf-dna-metric");
DATA.butterfly_metrics.forEach(m => {{
  const opt = document.createElement("option");
  opt.value = m.key; opt.textContent = m.label; bfSel.appendChild(opt);
}});
const outSel = document.getElementById("outcome-select");
DATA.outcomes.forEach(o => {{
  const opt = document.createElement("option");
  opt.value = o.key; opt.textContent = o.label; outSel.appendChild(opt);
}});

function wire(id, key, fn) {{
  document.querySelectorAll(`#${{id}} .btn`).forEach(b => {{
    b.onclick = () => {{
      document.querySelectorAll(`#${{id}} .btn`).forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      st[key] = b.dataset.val;
      fn();
    }};
  }});
}}
wire("bf-model", "bfModel", renderButterflies);
wire("bf-layer", "bfLayer", renderButterflies);
wire("bf-dna-scope", "bfScope", renderDnaButterfly);
wire("model-btns", "model", renderExplorer);
wire("pov-btns", "pov", renderExplorer);
wire("pair-btns", "pair", renderCombos);
bfSel.onchange = e => {{ st.bfMetric = e.target.value; renderDnaButterfly(); }};
outSel.onchange = e => {{ st.outcome = e.target.value; renderExplorer(); }};

const fmtP = p => p == null ? "—" : (p < 1e-4 ? "&lt;0.0001" : p.toFixed(4));
const stars = p => p == null ? "" : (p < 0.001 ? "***" : (p < 0.01 ? "**" : (p < 0.05 ? "*" : "")));
const f1 = v => v == null ? "—" : v.toFixed(1) + "%";
const f3 = v => v == null ? "—" : v.toFixed(3);

function renderButterflies() {{
  renderLabelsButterfly();
  renderDnaButterfly();
}}

function renderLabelsButterfly() {{
  const row = st.bfModel === "combined"
    ? DATA.summary_b.find(r => r.layer === st.bfLayer)
    : DATA.summary_a.find(r => r.model_key === st.bfModel && r.layer === st.bfLayer);
  if (!row) return;
  const items = [
    ["Belief (×100)", row.rumor_belief * 100, row.truth_belief * 100],
    ["GO % (Checked)", row.rumor_go_pct, row.truth_go_pct],
    ["FACT %", row.rumor_FACT_pct, row.truth_FACT_pct],
    ["CHECKED_TRUE %", row.rumor_CHECKED_TRUE_pct, row.truth_CHECKED_TRUE_pct],
    ["UNCERTAIN %", row.rumor_UNCERTAIN_pct, row.truth_UNCERTAIN_pct],
    ["SKEPTICAL %", row.rumor_SKEPTICAL_pct, row.truth_SKEPTICAL_pct],
    ["CHECKED_FALSE %", row.rumor_CHECKED_FALSE_pct, row.truth_CHECKED_FALSE_pct],
    ["NOT_MENTIONED %", row.rumor_nm_pct, row.truth_nm_pct],
  ];
  const W = 860, cx = 430, maxW = 280, rh = 30, topPad = 14;
  const H = topPad + items.length * rh + 24;
  let s = `<svg width="${{W}}" height="${{H}}" viewBox="0 0 ${{W}} ${{H}}" style="font-family:inherit;font-size:12px;">`;
  s += `<line x1="${{cx}}" y1="8" x2="${{cx}}" y2="${{H-20}}" stroke="#94a3b8" stroke-dasharray="3,3"/>`;
  items.forEach(([lbl, rv, tv], i) => {{
    const y = topPad + i * rh;
    const rw = Math.max(0, (rv || 0) / 100 * maxW);
    const tw = Math.max(0, (tv || 0) / 100 * maxW);
    s += `<rect x="${{cx - 75 - rw}}" y="${{y+5}}" width="${{rw}}" height="18" rx="3" fill="#c0392b" opacity="0.88"/>`;
    s += `<rect x="${{cx + 75}}" y="${{y+5}}" width="${{tw}}" height="18" rx="3" fill="#1e8449" opacity="0.88"/>`;
    s += `<text x="${{cx}}" y="${{y+18}}" text-anchor="middle" font-weight="600" fill="#1e293b">${{lbl}}</text>`;
    s += `<text x="${{cx - 81 - rw}}" y="${{y+18}}" text-anchor="end" fill="#7f1d1d">${{(rv||0).toFixed(1)}}%</text>`;
    s += `<text x="${{cx + 81 + tw}}" y="${{y+18}}" text-anchor="start" fill="#14532d">${{(tv||0).toFixed(1)}}%</text>`;
  }});
  s += `</svg>`;
  document.getElementById("bf-labels-svg").innerHTML = s;
}}

function renderDnaButterfly() {{
  const pov = st.bfLayer === "overall" ? "source" : st.bfLayer;
  const meta = DATA.butterfly_metrics.find(m => m.key === st.bfMetric);
  const isPct = meta.is_pct;
  const rCol = st.bfMetric === "belief" ? "rumor_belief" : (st.bfMetric === "go_pct" ? "rumor_go_pct" : `rumor_${{st.bfMetric}}_pct`);
  const tCol = st.bfMetric === "belief" ? "truth_belief" : (st.bfMetric === "go_pct" ? "truth_go_pct" : `truth_${{st.bfMetric}}_pct`);
  const scaleMax = isPct ? 100 : 1;

  let rows;
  if (st.bfModel === "combined") {{
    const ds = DATA.dna.filter(r => r.model_key === "deepseek_v4_flash" && r.pov === pov);
    const qwMap = new Map(DATA.dna.filter(r => r.model_key === "qwen_3_8_flash" && r.pov === pov).map(r => [r.cell_id, r]));
    rows = ds.map(r => {{
      const q = qwMap.get(r.cell_id) || r;
      const rv = ((r[rCol] ?? 0) + (q[rCol] ?? 0)) / 2;
      const tv = ((r[tCol] ?? 0) + (q[tCol] ?? 0)) / 2;
      return {{ cell_id: r.cell_id, cell_name: r.cell_name, [rCol]: rv, [tCol]: tv, gap: tv - rv }};
    }});
  }} else {{
    rows = DATA.dna.filter(r => r.model_key === st.bfModel && r.pov === pov)
      .map(r => ({{ ...r, gap: (r[tCol] ?? 0) - (r[rCol] ?? 0) }}));
  }}
  rows.sort((a, b) => b.gap - a.gap || a.cell_id - b.cell_id);
  if (st.bfScope === "top_bot" && rows.length > 24) {{
    rows = [...rows.slice(0, 12), ...rows.slice(-12)];
  }}
  const W = 980, cx = 490, labelHalf = 145, maxW = 240, rh = 24, topPad = 24;
  const H = topPad + rows.length * rh + 16;
  let s = `<svg width="${{W}}" height="${{H}}" viewBox="0 0 ${{W}} ${{H}}" style="font-family:inherit;font-size:11px;">`;
  s += `<text x="${{cx}}" y="14" text-anchor="middle" fill="#475569" font-weight="700">Showing ${{st.bfModel}} / ${{pov}} &mdash; Rumor (Left) vs. Truth (Right) | Center = Cell ID &amp; Gap</text>`;
  rows.forEach((r, i) => {{
    const y = topPad + i * rh;
    const rv = r[rCol] || 0, tv = r[tCol] || 0;
    const rw = Math.max(0, rv / scaleMax * maxW);
    const tw = Math.max(0, tv / scaleMax * maxW);
    const fmt = v => isPct ? v.toFixed(1) + "%" : v.toFixed(3);
    const gapTxt = isPct ? (r.gap >= 0 ? "+" : "") + r.gap.toFixed(1) : (r.gap >= 0 ? "+" : "") + r.gap.toFixed(3);
    s += `<rect x="${{cx - labelHalf - rw}}" y="${{y+4}}" width="${{rw}}" height="15" rx="2" fill="#c0392b" opacity="0.85"/>`;
    s += `<rect x="${{cx + labelHalf}}" y="${{y+4}}" width="${{tw}}" height="15" rx="2" fill="#1e8449" opacity="0.85"/>`;
    s += `<text x="${{cx}}" y="${{y+15}}" text-anchor="middle" fill="#1e293b"><b>C${{String(r.cell_id).padStart(2,'0')}}</b> (${{gapTxt}}) <title>${{r.cell_name}}</title></text>`;
    s += `<text x="${{cx - labelHalf - rw - 4}}" y="${{y+15}}" text-anchor="end" fill="#7f1d1d">${{fmt(rv)}}</text>`;
    s += `<text x="${{cx + labelHalf + tw + 4}}" y="${{y+15}}" text-anchor="start" fill="#14532d">${{fmt(tv)}}</text>`;
  }});
  s += `</svg>`;
  document.getElementById("bf-dna-svg").innerHTML = s;
}}

function renderForest(rows) {{
  if (!rows.length) return;
  const isPct = rows[0].unit === "pp";
  const vals = rows.flatMap(r => [r.effect_rumor, r.effect_truth, r.effect_td, 0]).filter(x => x != null);
  const lo = Math.min(...vals, -0.05), hi = Math.max(...vals, 0.05);
  const pad = (hi - lo) * 0.15 || 1;
  const minX = lo - pad, maxX = hi + pad;
  const W = 940, leftLbl = 230, plotW = 540, rh = 32, topPad = 24;
  const H = topPad + rows.length * rh + 24;
  const sx = v => leftLbl + ((v - minX) / (maxX - minX)) * plotW;
  const x0 = sx(0);
  let s = `<svg width="${{W}}" height="${{H}}" viewBox="0 0 ${{W}} ${{H}}" style="font-family:inherit;font-size:12px;">`;
  s += `<line x1="${{x0}}" y1="12" x2="${{x0}}" y2="${{H-16}}" stroke="#94a3b8" stroke-dasharray="4,3"/>`;
  rows.forEach((r, i) => {{
    const y = topPad + i * rh;
    const xr = sx(r.effect_rumor), xt = sx(r.effect_truth);
    const fmt = v => isPct ? (v>=0?"+":"") + v.toFixed(1) + " pp" : (v>=0?"+":"") + v.toFixed(3);
    s += `<text x="${{leftLbl - 10}}" y="${{y+14}}" text-anchor="end" font-weight="${{r.test_type==='interaction'?'700':'600'}}" fill="#1e293b">${{r.factor}}</text>`;
    s += `<line x1="${{xr}}" y1="${{y+10}}" x2="${{xt}}" y2="${{y+10}}" stroke="#64748b" stroke-width="2"/>`;
    s += `<circle cx="${{xr}}" cy="${{y+10}}" r="5" fill="#c0392b"/>`;
    s += `<circle cx="${{xt}}" cy="${{y+10}}" r="5" fill="#1e8449"/>`;
    s += `<text x="${{leftLbl + plotW + 14}}" y="${{y+14}}" fill="#1e293b">&Delta;TD: <b>${{fmt(r.effect_td)}}</b>${{stars(r.p_td_holm)}}</text>`;
  }});
  s += `</svg>`;
  document.getElementById("forest-svg").innerHTML = s;
}}

function renderExplorer() {{
  const rows = DATA.knobs.filter(r => r.model_key === st.model && r.pov === st.pov && r.outcome === st.outcome);
  renderForest(rows);
  if (rows.length) {{
    const isPct = rows[0].unit === "pp";
    const isBel = rows[0].outcome === "belief";
    const fe = v => v == null ? "—" : (isPct ? (v>=0?"+":"") + v.toFixed(2) + " pp" : (v>=0?"+":"") + v.toFixed(4));
    document.getElementById("td-meta").textContent = `Estimator: Pooled Truth × Contrast OLS / LPM (cov_type='cluster', groups=pair_id) + Wald z-test + Holm (10 tests) | N = ${{rows[0].n_obs.toLocaleString()}} non-NaN obs across ${{rows[0].n_pairs.toLocaleString()}} twin pairs`;
    let h = `<table><thead><tr><th>Type</th><th>Contrast</th><th>Detail</th><th class="num">Effect in Rumor</th><th class="num">Effect in Truth</th><th class="num">&Delta; Truth Discount</th><th class="num">95% CI (&Delta;TD)</th><th class="num">p (Clustered)</th><th class="num">p (Holm 10)</th>`;
    if (isBel) h += `<th class="num">Spec LMM Check</th>`;
    h += `</tr></thead><tbody>`;
    rows.forEach(r => {{
      const sig = r.p_td_holm < 0.05;
      const cls = !sig ? "ns" : (r.effect_td >= 0 ? "sig-pos" : "sig-neg");
      const ci = `[${{fe(r.td_ci_low).replace(" pp","")}}, ${{fe(r.td_ci_high)}}]`;
      h += `<tr class="${{r.test_type==='interaction'?'row-overall':''}}"><td><span class="pill">${{r.test_type}}</span></td><td><b>${{r.factor}}</b></td><td><code>${{r.contrast}}</code></td><td class="num rumor-col">${{fe(r.effect_rumor)}}</td><td class="num truth-col">${{fe(r.effect_truth)}}</td><td class="num ${{cls}}">${{fe(r.effect_td)}}${{stars(r.p_td_holm)}}</td><td class="num">${{ci}}</td><td class="num">${{fmtP(r.p_td_clustered)}}</td><td class="num ${{cls}}">${{fmtP(r.p_td_holm)}}</td>`;
      if (isBel) {{
        const lmm = r.lmm_td_effect != null ? `${{(r.lmm_td_effect>=0?"+":"")+r.lmm_td_effect.toFixed(4)}} (p=${{fmtP(r.lmm_td_p)}})` : r.lmm_status;
        h += `<td class="num">${{lmm}}</td>`;
      }}
      h += `</tr>`;
    }});
    document.getElementById("td-table").innerHTML = h + `</tbody></table>`;
  }}
  renderCombos();
  renderTopBotDna();
}}

function renderCombos() {{
  const cRows = DATA.combos.filter(r => r.model_key === st.model && r.pov === st.pov && r.outcome === st.outcome && r.pair_id === st.pair);
  const sRows = DATA.simple.filter(r => r.model_key === st.model && r.pov === st.pov && r.outcome === st.outcome && r.pair_id === st.pair);
  if (!cRows.length) return;
  const isPct = cRows[0].unit === "pp";
  const fv = v => v == null ? "—" : (isPct ? v.toFixed(2) + "%" : v.toFixed(4));
  const fe = v => v == null ? "—" : (isPct ? (v>=0?"+":"") + v.toFixed(2) + " pp" : (v>=0?"+":"") + v.toFixed(4));
  let ch = `<table><thead><tr><th>16-DNA Combo (Marginal Adj. Mean &amp; Pair-Clustered Wald CI)</th><th class="num">Obs (R / T)</th><th class="num">Pairs</th><th class="num">Rumor Mean</th><th class="num">Truth Mean</th><th class="num">Truth Discount (Truth &minus; Rumor)</th><th class="num">95% CI</th></tr></thead><tbody>`;
  cRows.forEach(r => {{
    const ci = `[${{fe(r.td_ci_low).replace(" pp","")}}, ${{fe(r.td_ci_high)}}]`;
    const nrt = `${{r.rumor_n_obs.toLocaleString()}} / ${{r.truth_n_obs.toLocaleString()}}`;
    ch += `<tr><td><b><code>${{r.combo_label}}</code></b></td><td class="num">${{nrt}}</td><td class="num">${{r.n_pairs_combo.toLocaleString()}}</td><td class="num rumor-col">${{fv(r.rumor_mean)}}</td><td class="num truth-col">${{fv(r.truth_mean)}}</td><td class="num strong">${{fe(r.truth_discount)}}</td><td class="num">${{ci}}</td></tr>`;
  }});
  document.getElementById("combo-table").innerHTML = ch + `</tbody></table>`;

  let sh = `<table><thead><tr><th>Comparison (Pair-Clustered Wald z-test)</th><th class="num">Pairs (Hi / Lo)</th><th class="num">Rumor Diff</th><th class="num">Truth Diff</th><th class="num">&Delta;TD (Truth &minus; Rumor)</th><th class="num">95% CI</th><th class="num">p (&Delta;TD)</th></tr></thead><tbody>`;
  sRows.forEach(r => {{
    const cls = r.p_td_clustered >= 0.05 ? "ns" : (r.effect_td >= 0 ? "sig-pos" : "sig-neg");
    const ci = `[${{fe(r.td_ci_low).replace(" pp","")}}, ${{fe(r.td_ci_high)}}]`;
    const np = `${{r.n_pairs_hi.toLocaleString()}} / ${{r.n_pairs_lo.toLocaleString()}}`;
    sh += `<tr><td><b>${{r.comparison}}</b></td><td class="num">${{np}}</td><td class="num rumor-col">${{fe(r.effect_rumor)}}</td><td class="num truth-col">${{fe(r.effect_truth)}}</td><td class="num ${{cls}}">${{fe(r.effect_td)}}${{stars(r.p_td_clustered)}}</td><td class="num">${{ci}}</td><td class="num ${{cls}}">${{fmtP(r.p_td_clustered)}}</td></tr>`;
  }});
  document.getElementById("simple-table").innerHTML = sh + `</tbody></table>`;
}}

function renderTopBotDna() {{
  const rows = DATA.dna.filter(r => r.model_key === st.model && r.pov === st.pov);
  const top10 = [...rows].sort((a,b) => (b.truth_discount - a.truth_discount) || (b.truth_belief - a.truth_belief) || (a.cell_id - b.cell_id)).slice(0, 10);
  const bot10 = [...rows].sort((a,b) => (a.truth_discount - b.truth_discount) || (a.truth_belief - b.truth_belief) || (a.cell_id - b.cell_id)).slice(0, 10);
  const mk = list => {{
    let h = `<table><thead><tr><th>#</th><th>Cell</th><th>Source DNA</th><th class="num">Ment. N (R / T)</th><th class="num">Pairs</th><th class="num">Rumor Belief</th><th class="num">Truth Belief</th><th class="num">Truth Discount (Paired Mean)</th><th class="num">95% CI</th><th class="num">Rumor GO %</th><th class="num">Truth GO %</th><th class="num">&Delta; GO</th></tr></thead><tbody>`;
    list.forEach((r, i) => {{
      const ci = `[${{f3(r.td_ci_low)}}, ${{f3(r.td_ci_high)}}]`;
      const nrt = `${{r.rumor_mentioned_n}} / ${{r.truth_mentioned_n}}`;
      h += `<tr><td>${{i+1}}</td><td>${{r.cell_id}}</td><td>${{r.cell_name}}</td><td class="num">${{nrt}}</td><td class="num">${{r.n_pairs_used}}</td><td class="num rumor-col">${{f3(r.rumor_belief)}}</td><td class="num truth-col">${{f3(r.truth_belief)}}</td><td class="num strong">${{f3(r.truth_discount)}}</td><td class="num">${{ci}}</td><td class="num">${{f1(r.rumor_go_pct)}}</td><td class="num">${{f1(r.truth_go_pct)}}</td><td class="num">${{(r.diff_go_pp>=0?"+":"")+r.diff_go_pp.toFixed(1)}} pp</td></tr>`;
    }});
    return h + `</tbody></table>`;
  }};
  document.getElementById("dna-top").innerHTML = mk(top10);
  document.getElementById("dna-bot").innerHTML = mk(bot10);
}}

renderButterflies();
renderExplorer();
</script>
</body>
</html>"""


def build_comparison_report(results_dir: Path, out_dir: Path) -> dict:
    listeners = pd.read_csv(results_dir / "listeners.csv")
    cells = pd.read_csv(results_dir / "cells.csv")
    conditions = pd.read_csv(results_dir / "conditions.csv")

    df = prepare_all_listeners(listeners, cells)
    table_a, table_b = compute_comparison_summaries(df, conditions)
    dna_df = compute_paired_dna_truth_discount(df)
    td_knobs, combos_df, simple_df = compute_symmetry_and_td_tests(df)
    model_cmp = compute_model_comparison(df)

    csv_dir = out_dir / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    table_a.to_csv(csv_dir / "summary_by_model_layer.csv", index=False)
    table_b.to_csv(csv_dir / "summary_experiment_overall.csv", index=False)
    dna_df.to_csv(csv_dir / "dna_truth_discount_all64.csv", index=False)
    td_knobs.to_csv(csv_dir / "truth_discount_knob_tests.csv", index=False)
    combos_df.to_csv(csv_dir / "interaction_combos_comparison.csv", index=False)
    simple_df.to_csv(csv_dir / "interaction_simple_comparison.csv", index=False)
    model_cmp.to_csv(csv_dir / "model_comparison.csv", index=False)

    (out_dir / "report.md").write_text(
        render_markdown(table_a, table_b, dna_df, td_knobs, combos_df, simple_df, model_cmp),
        encoding="utf-8",
    )
    (out_dir / "report.html").write_text(
        render_html(table_a, table_b, dna_df, td_knobs, combos_df, simple_df, model_cmp),
        encoding="utf-8",
    )
    return {
        "out_dir": str(out_dir),
        "td_knobs_rows": len(td_knobs),
        "combos_rows": len(combos_df),
        "dna_rows": len(dna_df),
        "model_cmp_rows": len(model_cmp),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    print(json.dumps(build_comparison_report(Path(args.results), Path(args.out)), indent=2))


if __name__ == "__main__":
    main()
