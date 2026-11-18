"""Build standalone Rumor Towns and Truth Towns reports (Gemini 3.7 Flash).

Implements the agreed specification in reports/SPEC_rumor_and_truth_reports.md:
  - Separate reports for condition_type='rumor' and condition_type='truth_twin'.
  - Excludes INVALID judgments completely (never imputes zeros).
  - Top summary tables per model/layer + experiment-wide combined average.
  - 3 POVs (Source/All-12, First-Hand Gatekeeper, Second-Hand Target) x 2 models.
  - Dyadic gatekeeper link (Seat i <-> Seat i+6) showing Second-Hand outcomes
    conditional on First-Hand GO vs SKIP.
  - Top 10 Strongest & Bottom 10 Weakest DNAs for Belief, SKIP %, and every
    individual categorical label, with deterministic tie-breaking.
  - Controlled main effects of all 6 knobs (controlling for each other +
    real_artist) using town-clustered (run_id) standard errors, Holm p-values,
    and companion Linear Mixed-Effects (LMM) check for Belief.

Outputs for each condition: report.html, report.md, and csv/*.csv.
"""
from __future__ import annotations

import argparse
import html
import itertools
import json
import math
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import patsy
from scipy.stats import norm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "results" / "main-gemini-3.7-flash"
DEFAULT_OUT = ROOT / "reports"

LABELS = ("FACT", "UNCERTAIN", "SKEPTICAL", "CHECKED_TRUE", "CHECKED_FALSE", "NOT_MENTIONED")
FACTORS = (
    ("closeness", "close_friend", "stranger"),
    ("authority", "mayor", "citizen"),
    ("reliability", "good_record", "poor_record"),
    ("wealth", "rich", "poor"),
    ("gender", "woman", "man"),
    ("age", "old", "young"),
)
FACTOR_LEVELS = {f: (a, b) for f, a, b in FACTORS}
INTERACTIONS = (
    ("closeness", "reliability"),
    ("authority", "reliability"),
    ("wealth", "reliability"),
    ("closeness", "authority"),
)
MODEL_NAMES = {
    "deepseek_v4_flash": "DeepSeek-V4-Flash",
    "qwen_3_8_flash": "Qwen3.8-Flash",
}
POV_DEFS = (
    ("source", "Source POV (All 12 Listeners)", None),
    ("first_hand", "First-Hand POV (Seats 1-6: Fooled & Gatekeeper)", "first_hand"),
    ("second_hand", "Second-Hand POV (Seats 7-12: Downstream Susceptibility)", "second_hand"),
)
RANK_METRICS = (
    ("belief", "Belief Score (0-1)", False),
    ("skip_pct", "SKIP Rate (%)", True),
    ("FACT", "FACT (%)", True),
    ("UNCERTAIN", "UNCERTAIN (%)", True),
    ("SKEPTICAL", "SKEPTICAL (%)", True),
    ("CHECKED_TRUE", "CHECKED_TRUE (%)", True),
    ("CHECKED_FALSE", "CHECKED_FALSE (%)", True),
    ("NOT_MENTIONED", "NOT_MENTIONED (%)", True),
)
OUTCOME_SPECS = (
    ("belief", "Belief Score (Valid Mentioning)", False),
    ("belief_sil0", "Belief (Silence=0.0 Sensitivity)", False),
    ("belief_sil05", "Belief (Silence=0.5 Sensitivity)", False),
    ("is_go", "GO Rate (Verification %)", True),
    ("label_NOT_MENTIONED", "NOT_MENTIONED (%)", True),
    ("label_FACT", "FACT (%)", True),
    ("label_UNCERTAIN", "UNCERTAIN (%)", True),
    ("label_SKEPTICAL", "SKEPTICAL (%)", True),
    ("label_CHECKED_TRUE", "CHECKED_TRUE (%)", True),
    ("label_CHECKED_FALSE", "CHECKED_FALSE (%)", True),
)
ARTISTS = ("Vesper Vance", "Kaelen Cross")
FORMULA = (
    "outcome ~ "
    + " + ".join(f"C({f})" for f, _, _ in FACTORS)
    + " + "
    + " + ".join(f"C({a}):C({b})" for a, b in INTERACTIONS)
    + " + C(real_artist)"
)


# --------------------------------------------------------------------------- data prep
def prepare_condition_frames(
    listeners: pd.DataFrame,
    cells: pd.DataFrame,
    conditions: pd.DataFrame,
    condition_type: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Filter to one condition_type, preserve NaN on INVALID rows, attach DNA & dyadic links."""
    df = listeners[listeners["condition_type"] == condition_type].copy()
    cond = conditions[conditions["condition_type"] == condition_type].copy()
    cell_names = cells[["cell_id", "cell_name"]].drop_duplicates()
    df = df.merge(cell_names, on="cell_id", how="left")
    if df["cell_name"].isna().any():
        missing_mask = df["cell_name"].isna()
        df.loc[missing_mask, "cell_name"] = (
            df.loc[missing_mask, "closeness"] + " / "
            + df.loc[missing_mask, "authority"] + " / "
            + df.loc[missing_mask, "reliability"] + " / "
            + df.loc[missing_mask, "wealth"] + " / "
            + df.loc[missing_mask, "gender"] + "_" + df.loc[missing_mask, "age"]
        )

    is_valid = df["judgment_status"] == "valid"
    is_not_mentioned = is_valid & (df["label"] == "NOT_MENTIONED")

    df["is_valid"] = is_valid
    df["is_invalid"] = ~is_valid
    df["is_go"] = np.where(df["decision"] == "GO", 1.0, np.where(df["decision"] == "SKIP", 0.0, np.nan))
    df["is_skip"] = 1.0 - df["is_go"]

    # Ensure INVALID rows remain NaN in belief & sensitivity scores (never imputed as 0).
    df["belief"] = np.where(is_valid & (df["mentioned"] == 1), df["belief"].astype(float), np.nan)
    df["belief_sil0"] = np.where(is_not_mentioned, 0.0, df["belief"])
    df["belief_sil05"] = np.where(is_not_mentioned, 0.5, df["belief"])

    for label in LABELS:
        df[f"label_{label}"] = np.where(is_valid, (df["label"] == label).astype(float), np.nan)

    # Dyadic pairing: Seat i (1..6) <-> Seat i+6 (7..12) within the same town run_id.
    fh = df[df["layer"] == "first_hand"][
        ["run_id", "model_key", "cell_id", "cell_name", "seat_id", "decision", "judgment_status", "label", "belief"]
    ].rename(columns={
        "seat_id": "fh_seat_id",
        "decision": "fh_decision",
        "judgment_status": "fh_judgment_status",
        "label": "fh_label",
        "belief": "fh_belief",
    })
    fh["sh_seat_id"] = fh["fh_seat_id"] + 6

    sh = df[df["layer"] == "second_hand"][
        ["run_id", "seat_id", "judgment_status", "label", "belief", "belief_sil0", "is_go",
         *[f"label_{lbl}" for lbl in LABELS]]
    ].rename(columns={
        "seat_id": "sh_seat_id",
        "judgment_status": "sh_judgment_status",
        "label": "sh_label",
        "belief": "sh_belief",
        "belief_sil0": "sh_belief_sil0",
        "is_go": "sh_is_go",
        **{f"label_{lbl}": f"sh_label_{lbl}" for lbl in LABELS},
    })
    dyadic = fh.merge(sh, on=["run_id", "sh_seat_id"], how="inner")
    return df, cond, dyadic


def _pct(series: pd.Series) -> float:
    valid = series.dropna()
    return float(valid.mean() * 100.0) if len(valid) else float("nan")


def _mean_or_nan(series: pd.Series) -> float:
    valid = series.dropna()
    return float(valid.mean()) if len(valid) else float("nan")


# --------------------------------------------------------------------------- top summary
def _aggregate_listener_slice(sub: pd.DataFrame, cond_slice: pd.DataFrame | None) -> dict:
    expected_n = int(len(sub))
    valid_n = int(sub["is_valid"].sum())
    invalid_n = int(sub["is_invalid"].sum())
    mentioned_n = int(sub["belief"].notna().sum())
    go_obs_n = int(sub["is_go"].notna().sum())
    go_n = int(sub["is_go"].sum())
    n_towns = int(sub["run_id"].nunique()) if "run_id" in sub.columns else 0

    trans_pct = float("nan")
    ev_pct = float("nan")
    fallback_fh = 0
    fallback_sh = 0
    if cond_slice is not None and len(cond_slice):
        t_den = float(cond_slice["transmission_observed_denominator"].sum())
        e_den = float(cond_slice["evidence_checker_denominator"].sum())
        if t_den > 0:
            trans_pct = float(cond_slice["transmission_keyword_count"].sum() / t_den * 100.0)
        if e_den > 0:
            ev_pct = float(cond_slice["evidence_keyword_count"].sum() / e_den * 100.0)
        fallback_fh = int(cond_slice["go_first_hand_fallback_skip_count"].sum())
        fallback_sh = int(cond_slice["go_second_hand_fallback_skip_count"].sum())

    row = {
        "n_towns": n_towns,
        "expected_n": expected_n,
        "valid_n": valid_n,
        "invalid_n": invalid_n,
        "invalid_pct": (invalid_n / expected_n * 100.0) if expected_n else float("nan"),
        "mentioned_n": mentioned_n,
        "go_obs_n": go_obs_n,
        "belief": _mean_or_nan(sub["belief"]),
        "belief_sil0": _mean_or_nan(sub["belief_sil0"]),
        "belief_sil05": _mean_or_nan(sub["belief_sil05"]),
        "go_n": go_n,
        "go_pct": _pct(sub["is_go"]),
        "skip_pct": _pct(sub["is_skip"]),
        "fallback_skip_fh": fallback_fh,
        "fallback_skip_sh": fallback_sh,
        "transmission_pct": trans_pct,
        "evidence_transmission_pct": ev_pct,
    }
    for label in LABELS:
        row[f"{label}_n"] = int(sub[f"label_{label}"].sum())
        row[f"{label}_pct"] = _pct(sub[f"label_{label}"])
    return row


def compute_summary_tables(df: pd.DataFrame, cond: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build Table A (per model x layer) and Table B (experiment total across both models)."""
    rows_a = []
    for model_key in MODEL_NAMES:
        mdf = df[df["model_key"] == model_key]
        mc = cond[cond["model_key"] == model_key]
        for layer_key, layer_label in (("first_hand", "First-Hand (Seats 1-6)"),
                                       ("second_hand", "Second-Hand (Seats 7-12)"),
                                       ("overall", "Overall (All 12 Listeners)")):
            sub = mdf if layer_key == "overall" else mdf[mdf["layer"] == layer_key]
            c_use = mc if layer_key in ("first_hand", "overall") else None
            stats = _aggregate_listener_slice(sub, c_use)
            rows_a.append({"model_key": model_key, "model_name": MODEL_NAMES[model_key],
                           "layer": layer_key, "layer_label": layer_label, **stats})

    rows_b = []
    for layer_key, layer_label in (("first_hand", "First-Hand (Seats 1-6)"),
                                   ("second_hand", "Second-Hand (Seats 7-12)"),
                                   ("overall", "Overall (All 12 Listeners)")):
        sub = df if layer_key == "overall" else df[df["layer"] == layer_key]
        c_use = cond if layer_key in ("first_hand", "overall") else None
        stats = _aggregate_listener_slice(sub, c_use)
        rows_b.append({"scope": "Both Models Combined", "layer": layer_key, "layer_label": layer_label, **stats})

    return pd.DataFrame(rows_a), pd.DataFrame(rows_b)


def compute_dyadic_gatekeeper(dyadic: pd.DataFrame, cond: pd.DataFrame) -> pd.DataFrame:
    """Second-hand listener outcomes conditional on paired First-Hand partner decision (GO vs SKIP)."""
    rows = []
    for model_key in list(MODEL_NAMES) + ["ALL_MODELS"]:
        sub_m = dyadic if model_key == "ALL_MODELS" else dyadic[dyadic["model_key"] == model_key]
        c_m = cond if model_key == "ALL_MODELS" else cond[cond["model_key"] == model_key]
        t_den = float(c_m["transmission_observed_denominator"].sum())
        e_den = float(c_m["evidence_checker_denominator"].sum())
        trans_pct = float(c_m["transmission_keyword_count"].sum() / t_den * 100.0) if t_den else float("nan")
        ev_pct = float(c_m["evidence_keyword_count"].sum() / e_den * 100.0) if e_den else float("nan")
        for fh_dec in ("ALL", "GO", "SKIP"):
            sub = sub_m if fh_dec == "ALL" else sub_m[sub_m["fh_decision"] == fh_dec]
            valid_sh = sub[sub["sh_judgment_status"] == "valid"]
            row = {
                "model_key": model_key,
                "model_name": "Both Models Combined" if model_key == "ALL_MODELS" else MODEL_NAMES[model_key],
                "fh_partner_decision": fh_dec,
                "n_pairs": int(len(sub)),
                "share_of_pairs_pct": float(len(sub) / len(sub_m) * 100.0) if len(sub_m) else float("nan"),
                "sh_valid_n": int(len(valid_sh)),
                "sh_mentioned_n": int(sub["sh_belief"].notna().sum()),
                "sh_go_pct": _pct(sub["sh_is_go"]),
                "sh_skip_pct": 100.0 - _pct(sub["sh_is_go"]),
                "sh_belief": _mean_or_nan(sub["sh_belief"]),
                "sh_belief_sil0": _mean_or_nan(sub["sh_belief_sil0"]),
                "fh_transmission_pct": trans_pct if fh_dec == "ALL" else float("nan"),
                "fh_evidence_transmission_pct": ev_pct if fh_dec in ("ALL", "GO") else float("nan"),
            }
            for lbl in LABELS:
                row[f"sh_{lbl}_pct"] = _pct(sub[f"sh_label_{lbl}"])
            rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- 64-DNA rankings
def compute_dna_metrics(df: pd.DataFrame, cond: pd.DataFrame, dyadic: pd.DataFrame) -> pd.DataFrame:
    """Compute metrics for all 64 Source DNAs across each Model x POV."""
    cond_cell = cond.groupby(["model_key", "cell_id"]).agg(
        trans_count=("transmission_keyword_count", "sum"),
        trans_den=("transmission_observed_denominator", "sum"),
        ev_count=("evidence_keyword_count", "sum"),
        ev_den=("evidence_checker_denominator", "sum"),
    ).reset_index()
    cond_cell["transmission_pct"] = cond_cell["trans_count"] / cond_cell["trans_den"] * 100.0
    cond_cell["evidence_transmission_pct"] = np.where(
        cond_cell["ev_den"] > 0, cond_cell["ev_count"] / cond_cell["ev_den"] * 100.0, np.nan
    )
    cond_lookup = cond_cell.set_index(["model_key", "cell_id"]).to_dict("index")

    dy_go = dyadic[dyadic["fh_decision"] == "GO"].groupby(["model_key", "cell_id"]).agg(
        sh_belief_when_fh_go=("sh_belief", "mean"),
        sh_go_when_fh_go=("sh_is_go", lambda s: s.mean() * 100.0),
        n_fh_go=("sh_is_go", "size"),
    ).to_dict("index")
    dy_skip = dyadic[dyadic["fh_decision"] == "SKIP"].groupby(["model_key", "cell_id"]).agg(
        sh_belief_when_fh_skip=("sh_belief", "mean"),
        sh_go_when_fh_skip=("sh_is_go", lambda s: s.mean() * 100.0),
        n_fh_skip=("sh_is_go", "size"),
    ).to_dict("index")

    rows = []
    for model_key in MODEL_NAMES:
        mdf = df[df["model_key"] == model_key]
        for pov_key, _, layer_filter in POV_DEFS:
            sub_pov = mdf if layer_filter is None else mdf[mdf["layer"] == layer_filter]
            for cell_id, csub in sub_pov.groupby("cell_id", sort=True):
                first_row = csub.iloc[0]
                stats = _aggregate_listener_slice(csub, None)
                cinfo = cond_lookup.get((model_key, int(cell_id)), {})
                ginfo = dy_go.get((model_key, int(cell_id)), {})
                sinfo = dy_skip.get((model_key, int(cell_id)), {})
                rows.append({
                    "model_key": model_key,
                    "model_name": MODEL_NAMES[model_key],
                    "pov": pov_key,
                    "cell_id": int(cell_id),
                    "cell_name": first_row["cell_name"],
                    "closeness": first_row["closeness"],
                    "authority": first_row["authority"],
                    "reliability": first_row["reliability"],
                    "wealth": first_row["wealth"],
                    "gender": first_row["gender"],
                    "age": first_row["age"],
                    **stats,
                    "transmission_pct": cinfo.get("transmission_pct", float("nan")),
                    "evidence_transmission_pct": cinfo.get("evidence_transmission_pct", float("nan")),
                    "sh_belief_when_fh_go": ginfo.get("sh_belief_when_fh_go", float("nan")),
                    "sh_go_when_fh_go": ginfo.get("sh_go_when_fh_go", float("nan")),
                    "sh_belief_when_fh_skip": sinfo.get("sh_belief_when_fh_skip", float("nan")),
                    "sh_go_when_fh_skip": sinfo.get("sh_go_when_fh_skip", float("nan")),
                })
    return pd.DataFrame(rows)


def rank_dna_table(slice_df: pd.DataFrame, metric_key: str, ascending: bool, limit: int = 10) -> tuple[pd.DataFrame, int]:
    """Return top/bottom `limit` DNAs with deterministic tie-breaking + zero-cell count."""
    col = metric_key if metric_key in ("belief", "skip_pct") else f"{metric_key}_pct"
    work = slice_df.copy()
    zero_count = int((work[col].fillna(0.0) == 0.0).sum())
    if metric_key == "belief":
        work = work.sort_values(
            by=[col, "skip_pct", "cell_id"],
            ascending=[ascending, False, True],
        )
    elif metric_key == "skip_pct":
        work = work.sort_values(
            by=[col, "belief", "cell_id"],
            ascending=[ascending, False, True],
        )
    else:
        work = work.sort_values(
            by=[col, "belief", "skip_pct", "cell_id"],
            ascending=[ascending, False, False, True],
        )
    return work.head(limit).reset_index(drop=True), zero_count


# --------------------------------------------------------------------------- controlled knob regressions
def _categorical_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for factor, lvl_a, lvl_b in FACTORS:
        out[factor] = pd.Categorical(out[factor], categories=[lvl_a, lvl_b], ordered=True)
    out["real_artist"] = pd.Categorical(out["real_artist"], categories=list(ARTISTS), ordered=True)
    return out


def _marginal_grid(design_info) -> tuple[pd.DataFrame, np.ndarray]:
    rows = [
        {**{f: vals[i] for i, (f, _, _) in enumerate(FACTORS)}, "real_artist": artist}
        for vals in itertools.product(*((a, b) for _, a, b in FACTORS))
        for artist in ARTISTS
    ]
    grid = _categorical_frame(pd.DataFrame(rows))
    matrix = np.asarray(patsy.build_design_matrices([design_info], grid)[0], dtype=float)
    return grid, matrix


def _holm_adjust(p_values: list[float]) -> list[float]:
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [1.0] * n
    prev = 0.0
    for rank, (idx, p) in enumerate(indexed):
        val = min(1.0, max(prev, (n - rank) * p))
        adjusted[idx] = val
        prev = val
    return adjusted


def _contrast_stats(vec: np.ndarray, beta: np.ndarray, cov: np.ndarray, crit: float) -> tuple[float, float, float, float, float]:
    """Compute linear contrast estimate, SE, 95% CI, and two-sided Wald p-value."""
    est = float(vec @ beta)
    var = float(vec @ cov @ vec)
    se = math.sqrt(var) if var > 0 else float("nan")
    z = est / se if se and math.isfinite(se) else float("nan")
    p_val = float(2.0 * norm.sf(abs(z))) if math.isfinite(z) else float("nan")
    ci_lo = est - crit * se if math.isfinite(se) else float("nan")
    ci_hi = est + crit * se if math.isfinite(se) else float("nan")
    return est, se, ci_lo, ci_hi, p_val


def compute_knob_effects(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fit the 10-term spec model (6 main knobs + 4 interactions, town-clustered SEs + Holm across 10 tests)
    plus controlled 4-combo means and simple comparisons for every interaction pair."""
    grid_matrix_cache: dict[str, tuple[pd.DataFrame, np.ndarray]] = {}
    knob_rows, combo_rows, simple_rows = [], [], []
    crit = float(norm.ppf(0.975))

    for model_key in MODEL_NAMES:
        mdf = df[df["model_key"] == model_key]
        for pov_key, _, layer_filter in POV_DEFS:
            sub_pov = mdf if layer_filter is None else mdf[mdf["layer"] == layer_filter]
            for outcome_col, outcome_label, is_pct in OUTCOME_SPECS:
                work = sub_pov[sub_pov[outcome_col].notna()].copy()
                work["outcome"] = work[outcome_col].astype(float) * (100.0 if is_pct else 1.0)
                work = _categorical_frame(work)
                n_obs = int(len(work))
                n_towns = int(work["run_id"].nunique())

                design = smf.ols(FORMULA, work)
                design_info = design.data.design_info
                if pov_key not in grid_matrix_cache:
                    grid_matrix_cache[pov_key] = _marginal_grid(design_info)
                grid_df, grid_mat = grid_matrix_cache[pov_key]

                fit = design.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(work["run_id"])[0]})
                beta = np.asarray(fit.params, dtype=float)
                cov = np.asarray(fit.cov_params(), dtype=float)

                # Companion Linear Mixed-Effects Model (run_id random intercept) on Belief outcomes.
                lmm_beta, lmm_cov, lmm_status = None, None, "not_run"
                if outcome_col in ("belief", "belief_sil0", "belief_sil05"):
                    with warnings.catch_warnings(record=True):
                        warnings.simplefilter("always")
                        lmm_fit = None
                        for method in ("lbfgs", "powell"):
                            try:
                                cand = smf.mixedlm(FORMULA, work, groups=work["run_id"]).fit(reml=True, method=method)
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
                base_meta = {
                    "model_key": model_key,
                    "model_name": MODEL_NAMES[model_key],
                    "pov": pov_key,
                    "outcome": outcome_col,
                    "outcome_label": outcome_label,
                    "unit": unit,
                    "n_obs": n_obs,
                    "n_towns": n_towns,
                }

                raw_p_list: list[float] = []
                batch: list[dict] = []

                def add_planned(test_type: str, factor_id: str, lvl_a: str, lvl_b: str,
                                contrast_lbl: str, vec_a: np.ndarray, vec_b: np.ndarray) -> None:
                    diff_vec = vec_a - vec_b
                    mean_a = float(vec_a @ beta)
                    mean_b = float(vec_b @ beta)
                    effect, se, ci_lo, ci_hi, p_val = _contrast_stats(diff_vec, beta, cov, crit)
                    lmm_eff, lmm_p = float("nan"), float("nan")
                    if lmm_beta is not None and lmm_cov is not None:
                        lmm_eff, _, _, _, lmm_p = _contrast_stats(diff_vec, lmm_beta, lmm_cov, crit)
                    raw_p_list.append(p_val if math.isfinite(p_val) else 1.0)
                    batch.append({
                        **base_meta,
                        "test_type": test_type,
                        "factor": factor_id,
                        "level_a": lvl_a,
                        "level_b": lvl_b,
                        "contrast": contrast_lbl,
                        "mean_a": mean_a,
                        "mean_b": mean_b,
                        "effect": effect,
                        "se_clustered": se,
                        "ci_low": ci_lo,
                        "ci_high": ci_hi,
                        "p_clustered": p_val,
                        "lmm_effect": lmm_eff,
                        "lmm_p": lmm_p,
                        "lmm_status": lmm_status,
                    })

                # 6 Main Knobs
                for factor, lvl_a, lvl_b in FACTORS:
                    vec_a = grid_mat[(grid_df[factor] == lvl_a).to_numpy()].mean(axis=0)
                    vec_b = grid_mat[(grid_df[factor] == lvl_b).to_numpy()].mean(axis=0)
                    add_planned("main", factor, lvl_a, lvl_b, f"{lvl_a} - {lvl_b}", vec_a, vec_b)

                # 4 Planned Interactions + 4-Combo Marginal Means + Simple Pairwise Comparisons
                for fa, fb in INTERACTIONS:
                    a1, a0 = FACTOR_LEVELS[fa]
                    b1, b0 = FACTOR_LEVELS[fb]
                    pair_id = f"{fa}_x_{fb}"
                    pair_label = f"{fa} x {fb}"
                    vecs = {}
                    combo_counts = {}
                    for va in (a1, a0):
                        for vb in (b1, b0):
                            mask = ((grid_df[fa] == va) & (grid_df[fb] == vb)).to_numpy()
                            v = grid_mat[mask].mean(axis=0)
                            vecs[(va, vb)] = v
                            w_mask = ((work[fa] == va) & (work[fb] == vb)).to_numpy()
                            c_n_obs = int(w_mask.sum())
                            c_n_towns = int(work.loc[w_mask, "run_id"].nunique())
                            combo_counts[(va, vb)] = (c_n_obs, c_n_towns)
                            est, se, ci_lo, ci_hi, _ = _contrast_stats(v, beta, cov, crit)
                            combo_rows.append({
                                **base_meta,
                                "pair_id": pair_id,
                                "pair_label": pair_label,
                                "factor_a": fa,
                                "factor_b": fb,
                                "level_a": va,
                                "level_b": vb,
                                "combo_label": f"{va} + {vb}",
                                "combo_n_obs": c_n_obs,
                                "combo_n_towns": c_n_towns,
                                "mean": est,
                                "se_clustered": se,
                                "ci_low": ci_lo,
                                "ci_high": ci_hi,
                            })

                    # DID interaction: (a1 vs a0 | b1) - (a1 vs a0 | b0)
                    diff_given_b1 = vecs[(a1, b1)] - vecs[(a0, b1)]
                    diff_given_b0 = vecs[(a1, b0)] - vecs[(a0, b0)]
                    add_planned(
                        "interaction",
                        f"{fa}_by_{fb}",
                        f"{a1}-{a0}|{b1}",
                        f"{a1}-{a0}|{b0}",
                        f"({a1}-{a0} | {b1}) - ({a1}-{a0} | {b0})",
                        diff_given_b1,
                        diff_given_b0,
                    )

                    # Conditional simple effects within the 2x2 (each uses town-clustered Wald z-test)
                    simple_specs = [
                        (f"{fa} effect | {fb}={b0}", (a1, b0), (a0, b0), f"{a1}+{b0} vs {a0}+{b0}"),
                        (f"{fa} effect | {fb}={b1}", (a1, b1), (a0, b1), f"{a1}+{b1} vs {a0}+{b1}"),
                        (f"{fb} effect | {fa}={a0}", (a0, b1), (a0, b0), f"{a0}+{b1} vs {a0}+{b0}"),
                        (f"{fb} effect | {fa}={a1}", (a1, b1), (a1, b0), f"{a1}+{b1} vs {a1}+{b0}"),
                    ]
                    for desc, k_hi, k_lo, cmp_lbl in simple_specs:
                        v_hi, v_lo = vecs[k_hi], vecs[k_lo]
                        n_obs_hi, n_towns_hi = combo_counts[k_hi]
                        n_obs_lo, n_towns_lo = combo_counts[k_lo]
                        eff, se, ci_lo, ci_hi, p_val = _contrast_stats(v_hi - v_lo, beta, cov, crit)
                        simple_rows.append({
                            **base_meta,
                            "pair_id": pair_id,
                            "pair_label": pair_label,
                            "comparison": desc,
                            "combo_contrast": cmp_lbl,
                            "n_obs_hi": n_obs_hi,
                            "n_towns_hi": n_towns_hi,
                            "n_obs_lo": n_obs_lo,
                            "n_towns_lo": n_towns_lo,
                            "mean_hi": float(v_hi @ beta),
                            "mean_lo": float(v_lo @ beta),
                            "effect": eff,
                            "se_clustered": se,
                            "ci_low": ci_lo,
                            "ci_high": ci_hi,
                            "p_clustered": p_val,
                        })

                holm_ps = _holm_adjust(raw_p_list)
                for row, hp in zip(batch, holm_ps):
                    row["p_holm"] = hp
                    knob_rows.append(row)

    return pd.DataFrame(knob_rows), pd.DataFrame(combo_rows), pd.DataFrame(simple_rows)


# --------------------------------------------------------------------------- formatting helpers
def _f3(v: float) -> str:
    return "—" if pd.isna(v) else f"{v:.3f}"


def _f1(v: float) -> str:
    return "—" if pd.isna(v) else f"{v:.1f}%"


def _fp(p: float) -> str:
    if pd.isna(p):
        return "—"
    if p < 1e-4:
        return "<0.0001"
    return f"{p:.4f}"


def _stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


# --------------------------------------------------------------------------- markdown rendering
def render_markdown(
    condition_type: str,
    table_a: pd.DataFrame,
    table_b: pd.DataFrame,
    dyadic_df: pd.DataFrame,
    dna_df: pd.DataFrame,
    knobs_df: pd.DataFrame,
    combos_df: pd.DataFrame,
    simple_df: pd.DataFrame,
) -> str:
    title = "Rumor Towns Report (False Claims)" if condition_type == "rumor" else "Truth Towns Report (True Claims)"
    total_towns = int(table_b.loc[table_b["layer"] == "overall", "n_towns"].iloc[0])
    per_model_towns = int(table_a.loc[table_a["layer"] == "overall", "n_towns"].iloc[0])
    total_fallback_fh = int(table_b.loc[table_b["layer"] == "overall", "fallback_skip_fh"].iloc[0])
    total_fallback_sh = int(table_b.loc[table_b["layer"] == "overall", "fallback_skip_sh"].iloc[0])
    total_invalid = int(table_b.loc[table_b["layer"] == "overall", "invalid_n"].iloc[0])
    total_expected = int(table_b.loc[table_b["layer"] == "overall", "expected_n"].iloc[0])

    total_towns = int(table_b.loc[table_b["layer"] == "overall", "n_towns"].iloc[0])
    per_model_towns = int(table_a.loc[table_a["layer"] == "overall", "n_towns"].iloc[0])

    lines = [
        f"# {title}",
        "",
        f"**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Condition:** `{condition_type}` | **Towns:** {total_towns:,} ({per_model_towns:,} per model) | **Expected Listeners:** {total_expected:,}",
        "",
        "### Methodological & Missingness Disclosure",
        f"- **Excluded Invalid Judgments:** {total_invalid:,} / {total_expected:,} ({total_invalid / total_expected * 100:.2f}%) had `judgment_status = invalid`. They are **completely excluded** (`NaN`), never turned into zeros.",
        "- **Three Dynamic Denominators (Never Hardcoded):** `Expected N` = all listeners in slice (used for `GO %`/`SKIP %`); `Valid N` = `Expected N - Invalid` (used for all 6 label `%` and `Silence=0.0/0.5`); `Mentioned N` = `Valid N - NOT_MENTIONED` (used for primary conditional `Belief`).",
        f"- **Verification (`GO`/`SKIP`):** 0 missing or invalid decisions. {total_fallback_fh + total_fallback_sh} simulation decisions ({total_fallback_fh} first-hand, {total_fallback_sh} second-hand; {(total_fallback_fh + total_fallback_sh) / total_expected * 100:.2f}%) were `malformed_fallback_skip` in the simulation runner and appear as `SKIP`.",
        "- **Statistical Model (Section 3):** 10-term OLS / Linear Probability Model (`6 main knobs + 4 interactions + real_artist`) with standard errors clustered by town (`run_id`), two-sided Wald z-tests, and Holm adjustment across all 10 planned contrasts per outcome. `Belief` also reports the spec's REML LMM (`1 | run_id`) companion check.",
        "",
        "---",
        "",
        "## 1. Overall Categorical & Behavioral Summary",
        "",
        "*Estimator: Descriptive Means (`Belief` over `Mentioned N`; `Silence=0.0/0.5` over `Valid N`) & Shares (`GO/SKIP` over `Expected N`; 6 Labels over `Valid N`).*",
        "",
        "### Table A: Per-Model Summary (First-Hand, Second-Hand, and Overall)",
        "",
        "| Model | Layer | Towns | Expected N | Valid N | Invalid (n / %) | Mentioned N | Belief (0-1 Mean) | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in table_a.iterrows():
        lines.append(
            f"| {r['model_name']} | {r['layer_label']} | {r['n_towns']:,} | {r['expected_n']:,} | {r['valid_n']:,} | {r['invalid_n']} ({_f1(r['invalid_pct'])}) | {r['mentioned_n']:,} | "
            f"{_f3(r['belief'])} | {_f3(r['belief_sil0'])} | {_f3(r['belief_sil05'])} | {_f1(r['go_pct'])} | {_f1(r['skip_pct'])} | "
            f"{_f1(r['FACT_pct'])} | {_f1(r['UNCERTAIN_pct'])} | {_f1(r['SKEPTICAL_pct'])} | "
            f"{_f1(r['CHECKED_TRUE_pct'])} | {_f1(r['CHECKED_FALSE_pct'])} | {_f1(r['NOT_MENTIONED_pct'])} | "
            f"{_f1(r['transmission_pct'])} | {_f1(r['evidence_transmission_pct'])} |"
        )

    lines += [
        "",
        "### Table B: Entire Experiment Average (Both Models Combined)",
        "",
        "| Scope | Layer | Towns | Expected N | Valid N | Invalid (n / %) | Mentioned N | Belief (0-1 Mean) | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in table_b.iterrows():
        lines.append(
            f"| {r['scope']} | {r['layer_label']} | {r['n_towns']:,} | {r['expected_n']:,} | {r['valid_n']:,} | {r['invalid_n']} ({_f1(r['invalid_pct'])}) | {r['mentioned_n']:,} | "
            f"{_f3(r['belief'])} | {_f3(r['belief_sil0'])} | {_f3(r['belief_sil05'])} | {_f1(r['go_pct'])} | {_f1(r['skip_pct'])} | "
            f"{_f1(r['FACT_pct'])} | {_f1(r['UNCERTAIN_pct'])} | {_f1(r['SKEPTICAL_pct'])} | "
            f"{_f1(r['CHECKED_TRUE_pct'])} | {_f1(r['CHECKED_FALSE_pct'])} | {_f1(r['NOT_MENTIONED_pct'])} | "
            f"{_f1(r['transmission_pct'])} | {_f1(r['evidence_transmission_pct'])} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 2. Gatekeeper & Downstream Susceptibility (`Seat i <-> Seat i+6`)",
        "",
        "*Estimator: Descriptive Means & Shares of Second-Hand Listeners (Seats 7-12) grouped by paired First-Hand Partner decision (`GO` vs `SKIP`). No hypothesis test.*",
        "",
        "| Model | First-Hand Partner | Pairs (n / share) | SH Valid N | SH Mentioned N | SH GO % | SH Belief | SH FACT % | SH UNCERTAIN % | SH SKEPTICAL % | SH CHECKED_TRUE % | SH CHECKED_FALSE % | SH NOT_MENTIONED % |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in dyadic_df.iterrows():
        lines.append(
            f"| {r['model_name']} | {r['fh_partner_decision']} | {r['n_pairs']:,} ({_f1(r['share_of_pairs_pct'])}) | {r['sh_valid_n']:,} | {r['sh_mentioned_n']:,} | "
            f"{_f1(r['sh_go_pct'])} | {_f3(r['sh_belief'])} | {_f1(r['sh_FACT_pct'])} | {_f1(r['sh_UNCERTAIN_pct'])} | "
            f"{_f1(r['sh_SKEPTICAL_pct'])} | {_f1(r['sh_CHECKED_TRUE_pct'])} | {_f1(r['sh_CHECKED_FALSE_pct'])} | "
            f"{_f1(r['sh_NOT_MENTIONED_pct'])} |"
        )

    lines += ["", "---", "", "## 3. Controlled Effects: 6 Main Knobs + 4 Planned Interactions (Town-Clustered)"]
    for model_key, model_name in MODEL_NAMES.items():
        lines += ["", f"### Model: {model_name}"]
        for pov_key, pov_title, _ in POV_DEFS:
            lines += ["", f"#### {pov_title}"]
            sub_k = knobs_df[(knobs_df["model_key"] == model_key) & (knobs_df["pov"] == pov_key)]
            sub_c = combos_df[(combos_df["model_key"] == model_key) & (combos_df["pov"] == pov_key)]
            sub_s = simple_df[(simple_df["model_key"] == model_key) & (simple_df["pov"] == pov_key)]
            for outcome_col, outcome_label, is_pct in OUTCOME_SPECS:
                ok = sub_k[sub_k["outcome"] == outcome_col]
                lines += [
                    "",
                    f"**Outcome: {outcome_label}** (n={ok['n_obs'].iloc[0]:,}, towns={ok['n_towns'].iloc[0]:,})",
                    "",
                    "| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |"
                    if outcome_col in ("belief", "belief_sil0", "belief_sil05")
                    else "| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |",
                    "|---|---|---|---:|---:|---:|---:|---:|---:|---:|"
                    if outcome_col in ("belief", "belief_sil0", "belief_sil05")
                    else "|---|---|---|---:|---:|---:|---:|---:|---:|",
                ]
                for _, kr in ok.iterrows():
                    fmt_val = (lambda x: f"{x:.2f}%") if is_pct else (lambda x: f"{x:.4f}")
                    fmt_eff = (lambda x: f"{x:+.2f} pp") if is_pct else (lambda x: f"{x:+.4f}")
                    ci_txt = f"[{fmt_eff(kr['ci_low']).replace(' pp','')}, {fmt_eff(kr['ci_high'])}]"
                    ma = fmt_eff(kr["mean_a"]) if kr["test_type"] == "interaction" else fmt_val(kr["mean_a"])
                    mb = fmt_eff(kr["mean_b"]) if kr["test_type"] == "interaction" else fmt_val(kr["mean_b"])
                    row_str = (
                        f"| {kr['test_type']} | {kr['factor']} | `{kr['contrast']}` | {ma} | {mb} | "
                        f"{fmt_eff(kr['effect'])}{_stars(kr['p_holm'])} | {ci_txt} | {_fp(kr['p_clustered'])} | {_fp(kr['p_holm'])} |"
                    )
                    if outcome_col in ("belief", "belief_sil0", "belief_sil05"):
                        lmm_txt = f"{kr['lmm_effect']:+.4f} (p={_fp(kr['lmm_p'])})" if pd.notna(kr['lmm_effect']) else kr['lmm_status']
                        row_str += f" {lmm_txt} |"
                    lines.append(row_str)

                if outcome_col not in ("belief_sil0", "belief_sil05"):
                    lines += ["", f"*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, {outcome_label}):*", ""]
                    for fa, fb in INTERACTIONS:
                        pair_id = f"{fa}_x_{fb}"
                        oc = sub_c[(sub_c["outcome"] == outcome_col) & (sub_c["pair_id"] == pair_id)]
                        os_df = sub_s[(sub_s["outcome"] == outcome_col) & (sub_s["pair_id"] == pair_id)]
                        fv = (lambda x: f"{x:.2f}%") if is_pct else (lambda x: f"{x:.4f}")
                        fe = (lambda x: f"{x:+.2f} pp") if is_pct else (lambda x: f"{x:+.4f}")
                        lines += [
                            f"- **`{fa} × {fb}` — Controlled Combos:** " + " | ".join(
                                f"`{cr['combo_label']}` (n={int(cr['combo_n_obs']):,}, {int(cr['combo_n_towns'])} towns) = **{fv(cr['mean'])}** [{fv(cr['ci_low']).replace('%','')}, {fv(cr['ci_high'])}]"
                                for _, cr in oc.iterrows()
                            ),
                            "",
                            "| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |",
                            "|---|---:|---:|---:|---:|",
                        ]
                        for _, sr in os_df.iterrows():
                            sci = f"[{fe(sr['ci_low']).replace(' pp','')}, {fe(sr['ci_high'])}]"
                            n_pair = f"{int(sr['n_obs_hi']):,} / {int(sr['n_obs_lo']):,}"
                            lines.append(
                                f"| `{sr['comparison']}` | {n_pair} | {fe(sr['effect'])}{_stars(sr['p_clustered'])} | {sci} | {_fp(sr['p_clustered'])} |"
                            )
                        lines.append("")

    lines += ["", "---", "", "## 4. Top 10 Strongest & Bottom 10 Weakest Source DNAs (Descriptive Per-Cell Means & Shares; No Hypothesis Test)"]
    for model_key, model_name in MODEL_NAMES.items():
        lines += ["", f"### Model: {model_name}"]
        for pov_key, pov_title, _ in POV_DEFS:
            lines += ["", f"#### {pov_title}"]
            slice_df = dna_df[(dna_df["model_key"] == model_key) & (dna_df["pov"] == pov_key)]
            for metric_key, metric_label, is_pct in RANK_METRICS:
                top10, zero_n = rank_dna_table(slice_df, metric_key, ascending=False, limit=10)
                bot10, _ = rank_dna_table(slice_df, metric_key, ascending=True, limit=10)
                col = metric_key if metric_key in ("belief", "skip_pct") else f"{metric_key}_pct"
                tie_note = f" *(Note: {zero_n} of 64 cells are 0.0%)*" if is_pct and zero_n > 10 else ""
                lines += ["", f"**{metric_label}**{tie_note}", ""]
                for heading, tbl in (("Top 10 Strongest (Highest)", top10), ("Bottom 10 Weakest (Lowest)", bot10)):
                    lines += [
                        f"*{heading}:*",
                        "",
                        "| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |",
                        "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
                    ]
                    for idx, dr in tbl.iterrows():
                        targ = f"{dr[col]:.1f}%" if is_pct else f"{dr[col]:.4f}"
                        lines.append(
                            f"| {idx + 1} | {dr['cell_id']} | {dr['cell_name']} | {int(dr['n_towns'])} | {int(dr['valid_n'])} | {int(dr['mentioned_n'])} | **{targ}** | {_f3(dr['belief'])} | "
                            f"{_f1(dr['go_pct'])} | {_f1(dr['skip_pct'])} | {_f1(dr['FACT_pct'])} | {_f1(dr['UNCERTAIN_pct'])} | "
                            f"{_f1(dr['SKEPTICAL_pct'])} | {_f1(dr['CHECKED_TRUE_pct'])} | {_f1(dr['CHECKED_FALSE_pct'])} | "
                            f"{_f1(dr['NOT_MENTIONED_pct'])} |"
                        )
                    lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------------- interactive html rendering
def render_html(
    condition_type: str,
    table_a: pd.DataFrame,
    table_b: pd.DataFrame,
    dyadic_df: pd.DataFrame,
    dna_df: pd.DataFrame,
    knobs_df: pd.DataFrame,
    combos_df: pd.DataFrame,
    simple_df: pd.DataFrame,
) -> str:
    is_rumor = condition_type == "rumor"
    title = "Rumor Towns Report — False Claims (Gemini 3.7 Flash)" if is_rumor else "Truth Towns Report — True Claims (Gemini 3.7 Flash)"
    badge = "FALSE CLAIMS (RUMOR)" if is_rumor else "TRUE CLAIMS (TRUTH TWIN)"
    accent = "#c0392b" if is_rumor else "#1e8449"

    total_towns = int(table_b.loc[table_b["layer"] == "overall", "n_towns"].iloc[0])
    per_model_towns = int(table_a.loc[table_a["layer"] == "overall", "n_towns"].iloc[0])
    total_fallback_fh = int(table_b.loc[table_b["layer"] == "overall", "fallback_skip_fh"].iloc[0])
    total_fallback_sh = int(table_b.loc[table_b["layer"] == "overall", "fallback_skip_sh"].iloc[0])
    total_invalid = int(table_b.loc[table_b["layer"] == "overall", "invalid_n"].iloc[0])
    total_expected = int(table_b.loc[table_b["layer"] == "overall", "expected_n"].iloc[0])

    # Pack pre-computed data into JSON for clean interactive client-side tabs (works completely offline).
    payload = {
        "knobs": knobs_df.replace({np.nan: None}).to_dict(orient="records"),
        "combos": combos_df.replace({np.nan: None}).to_dict(orient="records"),
        "simple": simple_df.replace({np.nan: None}).to_dict(orient="records"),
        "dna": dna_df.replace({np.nan: None}).to_dict(orient="records"),
        "interactions": [{"id": f"{a}_x_{b}", "label": f"{a} × {b}"} for a, b in INTERACTIONS],
        "rank_metrics": [{"key": k, "label": lbl, "is_pct": p} for k, lbl, p in RANK_METRICS],
        "outcomes": [{"key": k, "label": lbl, "is_pct": p} for k, lbl, p in OUTCOME_SPECS],
    }
    payload_json = json.dumps(payload).replace("</", "<\\/")

    def summary_rows_html(df_in: pd.DataFrame, first_col: str) -> str:
        out = []
        for _, r in df_in.iterrows():
            cls = "row-overall" if r["layer"] == "overall" else ""
            out.append(
                f"<tr class='{cls}'>"
                f"<td><b>{html.escape(str(r[first_col]))}</b></td>"
                f"<td>{html.escape(str(r['layer_label']))}</td>"
                f"<td class='num'>{r['n_towns']:,}</td>"
                f"<td class='num'>{r['expected_n']:,}</td>"
                f"<td class='num'>{r['valid_n']:,}</td>"
                f"<td class='num'>{r['invalid_n']} ({_f1(r['invalid_pct'])})</td>"
                f"<td class='num'>{r['mentioned_n']:,}</td>"
                f"<td class='num strong'>{_f3(r['belief'])}</td>"
                f"<td class='num'>{_f3(r['belief_sil0'])}</td>"
                f"<td class='num'>{_f3(r['belief_sil05'])}</td>"
                f"<td class='num'>{_f1(r['go_pct'])}</td>"
                f"<td class='num'>{_f1(r['skip_pct'])}</td>"
                f"<td class='num'>{_f1(r['FACT_pct'])}</td>"
                f"<td class='num'>{_f1(r['UNCERTAIN_pct'])}</td>"
                f"<td class='num'>{_f1(r['SKEPTICAL_pct'])}</td>"
                f"<td class='num'>{_f1(r['CHECKED_TRUE_pct'])}</td>"
                f"<td class='num'>{_f1(r['CHECKED_FALSE_pct'])}</td>"
                f"<td class='num'>{_f1(r['NOT_MENTIONED_pct'])}</td>"
                f"<td class='num'>{_f1(r['transmission_pct'])}</td>"
                f"<td class='num'>{_f1(r['evidence_transmission_pct'])}</td>"
                f"</tr>"
            )
        return "\n".join(out)

    dyadic_rows_html = []
    for _, r in dyadic_df.iterrows():
        cls = "row-overall" if r["fh_partner_decision"] == "ALL" else ""
        dyadic_rows_html.append(
            f"<tr class='{cls}'>"
            f"<td><b>{html.escape(str(r['model_name']))}</b></td>"
            f"<td><span class='pill'>{html.escape(str(r['fh_partner_decision']))}</span></td>"
            f"<td class='num'>{r['n_pairs']:,} ({_f1(r['share_of_pairs_pct'])})</td>"
            f"<td class='num'>{r['sh_valid_n']:,}</td>"
            f"<td class='num'>{r['sh_mentioned_n']:,}</td>"
            f"<td class='num'>{_f1(r['sh_go_pct'])}</td>"
            f"<td class='num strong'>{_f3(r['sh_belief'])}</td>"
            f"<td class='num'>{_f1(r['sh_FACT_pct'])}</td>"
            f"<td class='num'>{_f1(r['sh_UNCERTAIN_pct'])}</td>"
            f"<td class='num'>{_f1(r['sh_SKEPTICAL_pct'])}</td>"
            f"<td class='num'>{_f1(r['sh_CHECKED_TRUE_pct'])}</td>"
            f"<td class='num'>{_f1(r['sh_CHECKED_FALSE_pct'])}</td>"
            f"<td class='num'>{_f1(r['sh_NOT_MENTIONED_pct'])}</td>"
            f"</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ --accent: {accent}; --bg: #f7f8fa; --card: #ffffff; --border: #e1e5eb; --text: #1c2430; --muted: #5b6778; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: var(--bg); color: var(--text); line-height: 1.45; }}
  .wrap {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
  header {{ background: var(--card); border: 1px solid var(--border); border-left: 6px solid var(--accent); border-radius: 10px; padding: 20px 24px; margin-bottom: 20px; }}
  .badge {{ display: inline-block; background: var(--accent); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: .06em; padding: 3px 9px; border-radius: 999px; margin-bottom: 6px; }}
  h1 {{ margin: 4px 0 8px; font-size: 24px; }}
  h2 {{ margin: 24px 0 10px; font-size: 18px; border-bottom: 2px solid var(--border); padding-bottom: 6px; }}
  h3 {{ margin: 16px 0 8px; font-size: 15px; }}
  .meta {{ color: var(--muted); font-size: 13px; }}
  .note {{ background: #f1f4f9; border-left: 3px solid #6b7b8f; padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-top: 12px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; margin-bottom: 18px; }}
  .scroll {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  th, td {{ padding: 7px 9px; border-bottom: 1px solid var(--border); text-align: left; white-space: nowrap; }}
  th {{ background: #f4f6f9; font-weight: 600; color: #344054; position: sticky; top: 0; }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.strong {{ font-weight: 700; color: var(--accent); }}
  tr.row-overall {{ background: #f8fafc; font-weight: 600; }}
  tr:hover {{ background: #f4f8ff; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 14px; }}
  .btn-group {{ display: inline-flex; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: #fff; }}
  .btn {{ border: 0; background: transparent; padding: 8px 13px; font-size: 13px; font-weight: 600; cursor: pointer; color: var(--muted); }}
  .btn.active {{ background: var(--accent); color: #fff; }}
  select {{ padding: 7px 10px; border: 1px solid var(--border); border-radius: 7px; font-size: 13px; background: #fff; }}
  .sig-pos {{ color: #166534; font-weight: 700; }}
  .sig-neg {{ color: #991b1b; font-weight: 700; }}
  .ns {{ color: #64748b; }}
  .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #eef2f7; font-size: 11px; font-weight: 700; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr; gap: 16px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="badge">{badge}</div>
    <h1>{html.escape(title)}</h1>
    <div class="meta">{total_towns:,} towns ({per_model_towns:,} per agent model) &bull; {total_expected:,} expected listeners &bull; Single Judge: Gemini 3.7 Flash &bull; Clustering: town (<code>run_id</code>)</div>
    <div class="note">
      <b>Honest Missingness &amp; Three Dynamic Denominators (Never Hardcoded):</b>
      {total_invalid:,} / {total_expected:,} ({total_invalid / total_expected * 100:.2f}%) judge outputs were <code>invalid</code> and are <b>completely excluded</b> (never zero-imputed).
      <code>Expected N</code> = all listeners (used for <code>GO</code>/<code>SKIP</code>); <code>Valid N</code> = <code>Expected N &minus; Invalid</code> (used for all 6 label % and <code>Sil=0.0/0.5</code>); <code>Mentioned N</code> = <code>Valid N &minus; NOT_MENTIONED</code> (used for conditional <code>Belief</code>).
      Runner verification decisions (<code>GO</code>/<code>SKIP</code>) have 0 missing values ({total_fallback_fh + total_fallback_sh} simulation <code>malformed_fallback_skip</code> rows = {(total_fallback_fh + total_fallback_sh) / total_expected * 100:.2f}% appear as <code>SKIP</code>).
    </div>
  </header>

  <div class="card">
    <h2>1A. Overall Categorical &amp; Belief Summary — Per Model (First-Hand, Second-Hand, Overall)</h2>
    <div class="meta" style="margin-bottom:8px;"><b>Estimator:</b> Descriptive Means (<code>Belief</code> over <code>Mentioned N</code>; <code>Sil=0.0/0.5</code> over <code>Valid N</code>) &amp; Percentage Shares (<code>GO/SKIP</code> over <code>Expected N</code>; 6 Labels over <code>Valid N</code>).</div>
    <div class="scroll">
      <table>
        <thead>
          <tr><th>Model</th><th>Layer</th><th class="num">Towns</th><th class="num">Expected N</th><th class="num">Valid N</th><th class="num">Invalid</th><th class="num">Mentioned N</th><th class="num">Belief (Mean)</th><th class="num">Sil=0.0</th><th class="num">Sil=0.5</th><th class="num">GO %</th><th class="num">SKIP %</th><th class="num">FACT %</th><th class="num">UNCERTAIN %</th><th class="num">SKEPTICAL %</th><th class="num">CHECKED_TRUE %</th><th class="num">CHECKED_FALSE %</th><th class="num">NOT_MENTIONED %</th><th class="num">Trans %</th><th class="num">Evid Trans %</th></tr>
        </thead>
        <tbody>{summary_rows_html(table_a, "model_name")}</tbody>
      </table>
    </div>
    <h2>1B. Entire Experiment Average — Both Models Combined</h2>
    <div class="scroll">
      <table>
        <thead>
          <tr><th>Scope</th><th>Layer</th><th class="num">Towns</th><th class="num">Expected N</th><th class="num">Valid N</th><th class="num">Invalid</th><th class="num">Mentioned N</th><th class="num">Belief (Mean)</th><th class="num">Sil=0.0</th><th class="num">Sil=0.5</th><th class="num">GO %</th><th class="num">SKIP %</th><th class="num">FACT %</th><th class="num">UNCERTAIN %</th><th class="num">SKEPTICAL %</th><th class="num">CHECKED_TRUE %</th><th class="num">CHECKED_FALSE %</th><th class="num">NOT_MENTIONED %</th><th class="num">Trans %</th><th class="num">Evid Trans %</th></tr>
        </thead>
        <tbody>{summary_rows_html(table_b, "scope")}</tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>2. Gatekeeper &amp; Downstream Susceptibility (Seat i &harr; Seat i+6)</h2>
    <div class="meta" style="margin-bottom:8px;"><b>Estimator:</b> Descriptive Means &amp; Shares of Second-Hand Listeners (Seats 7&ndash;12) grouped by paired First-Hand decision (<code>GO</code> vs. <code>SKIP</code>). No hypothesis test.</div>
    <div class="scroll">
      <table>
        <thead>
          <tr><th>Model</th><th>First-Hand Decision</th><th class="num">Pairs (GO/SKIP N)</th><th class="num">SH Valid N</th><th class="num">SH Ment. N</th><th class="num">SH GO %</th><th class="num">SH Belief</th><th class="num">SH FACT %</th><th class="num">SH UNCERTAIN %</th><th class="num">SH SKEPTICAL %</th><th class="num">SH CHECKED_TRUE %</th><th class="num">SH CHECKED_FALSE %</th><th class="num">SH NOT_MENTIONED %</th></tr>
        </thead>
        <tbody>{"".join(dyadic_rows_html)}</tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>3. Interactive Explorer: Controlled Knob Effects &amp; Top/Bottom 10 DNAs</h2>
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
    </div>

    <h3>Part A: Controlled 10-Test Spec Model (6 Main Knobs + 4 Interactions, Town-Clustered SEs + Holm across 10)</h3>
    <div class="controls">
      <label>Outcome: <select id="outcome-select"></select></label>
      <span class="meta" id="knob-meta"></span>
    </div>
    <div class="scroll" id="knob-table"></div>

    <h3>Part B: 4 Planned Interaction Pairs — 16-DNA Controlled Combos &amp; Pairwise Comparisons</h3>
    <div class="controls">
      <div class="btn-group" id="pair-btns">
        <button class="btn active" data-val="closeness_x_reliability">closeness &times; reliability</button>
        <button class="btn" data-val="authority_x_reliability">authority &times; reliability</button>
        <button class="btn" data-val="wealth_x_reliability">wealth &times; reliability</button>
        <button class="btn" data-val="closeness_x_authority">closeness &times; authority</button>
      </div>
      <span class="meta"><b>Estimator:</b> Marginal Predictions &amp; Conditional Wald z-tests from Town-Clustered OLS (<code>groups=run_id</code>), controlling for the other 4 knobs + artist. Exact non-NaN <code>N</code> shown per combo.</span>
    </div>
    <div class="grid-2">
      <div><h4>4 Combo Controlled Means (95% CI)</h4><div class="scroll" id="combo-table"></div></div>
      <div><h4>Conditional Simple Comparisons Inside the 2&times;2</h4><div class="scroll" id="simple-table"></div></div>
    </div>

    <h3>Part C: Top 10 Strongest &amp; Bottom 10 Weakest Source DNAs (Descriptive Per-Cell Means &amp; Shares)</h3>
    <div class="controls">
      <label>Rank by Metric / Categorical Label: <select id="rank-select"></select></label>
      <span class="meta" id="dna-note"></span>
    </div>
    <div class="grid-2">
      <div><h4>Top 10 Strongest (Highest)</h4><div class="scroll" id="dna-top"></div></div>
      <div><h4>Bottom 10 Weakest (Lowest)</h4><div class="scroll" id="dna-bot"></div></div>
    </div>
  </div>
</div>

<script>
const DATA = {payload_json};
let state = {{ model: "deepseek_v4_flash", pov: "source", outcome: "belief", pair: "closeness_x_reliability", rankMetric: "belief" }};

const outSel = document.getElementById("outcome-select");
DATA.outcomes.forEach(o => {{
  const opt = document.createElement("option");
  opt.value = o.key; opt.textContent = o.label; outSel.appendChild(opt);
}});
const rankSel = document.getElementById("rank-select");
DATA.rank_metrics.forEach(m => {{
  const opt = document.createElement("option");
  opt.value = m.key; opt.textContent = m.label; rankSel.appendChild(opt);
}});

function wireButtons(id, key) {{
  document.querySelectorAll(`#${{id}} .btn`).forEach(btn => {{
    btn.onclick = () => {{
      document.querySelectorAll(`#${{id}} .btn`).forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state[key] = btn.dataset.val;
      renderAll();
    }};
  }});
}}
wireButtons("model-btns", "model");
wireButtons("pov-btns", "pov");
wireButtons("pair-btns", "pair");
outSel.onchange = e => {{ state.outcome = e.target.value; renderKnobs(); renderInteractions(); }};
rankSel.onchange = e => {{ state.rankMetric = e.target.value; renderDNA(); }};

function fmtP(p) {{ return p == null ? "—" : (p < 1e-4 ? "&lt;0.0001" : p.toFixed(4)); }}
function stars(p) {{ return p == null ? "" : (p < 0.001 ? "***" : (p < 0.01 ? "**" : (p < 0.05 ? "*" : ""))); }}
function f1(v) {{ return v == null ? "—" : v.toFixed(1) + "%"; }}
function f3(v) {{ return v == null ? "—" : v.toFixed(3); }}

function renderKnobs() {{
  const rows = DATA.knobs.filter(r => r.model_key === state.model && r.pov === state.pov && r.outcome === state.outcome);
  if (!rows.length) return;
  const isPct = rows[0].unit === "pp";
  const isBelief = rows[0].outcome.startsWith("belief");
  document.getElementById("knob-meta").textContent = `Estimator: Town-Clustered OLS / LPM (cov_type='cluster', groups=run_id) + Wald z-test + Holm (10 tests) | N = ${{rows[0].n_obs.toLocaleString()}} non-NaN obs across ${{rows[0].n_towns.toLocaleString()}} towns`;
  const fv = v => v == null ? "—" : (isPct ? v.toFixed(2) + "%" : v.toFixed(4));
  const fe = v => v == null ? "—" : (isPct ? (v >= 0 ? "+" : "") + v.toFixed(2) + " pp" : (v >= 0 ? "+" : "") + v.toFixed(4));
  let h = `<table><thead><tr><th>Type</th><th>Contrast</th><th>Detail (A &minus; B)</th><th class="num">A</th><th class="num">B</th><th class="num">Controlled Effect</th><th class="num">95% CI</th><th class="num">p (Clustered)</th><th class="num">p (Holm 10)</th>`;
  if (isBelief) h += `<th class="num">LMM Check (run_id RE)</th>`;
  h += `</tr></thead><tbody>`;
  rows.forEach(r => {{
    const sig = r.p_holm < 0.05;
    const cls = !sig ? "ns" : (r.effect >= 0 ? "sig-pos" : "sig-neg");
    const ci = `[${{fe(r.ci_low).replace(" pp","")}}, ${{fe(r.ci_high)}}]`;
    const ma = r.test_type === "interaction" ? fe(r.mean_a) : fv(r.mean_a);
    const mb = r.test_type === "interaction" ? fe(r.mean_b) : fv(r.mean_b);
    const badge = r.test_type === "interaction" ? "interaction" : "main";
    h += `<tr class="${{r.test_type === 'interaction' ? 'row-overall' : ''}}"><td><span class="pill">${{badge}}</span></td><td><b>${{r.factor}}</b></td><td><code>${{r.contrast}}</code></td><td class="num">${{ma}}</td><td class="num">${{mb}}</td><td class="num ${{cls}}">${{fe(r.effect)}}${{stars(r.p_holm)}}</td><td class="num">${{ci}}</td><td class="num">${{fmtP(r.p_clustered)}}</td><td class="num ${{cls}}">${{fmtP(r.p_holm)}}</td>`;
    if (isBelief) {{
      const lmm = r.lmm_effect != null ? `${{(r.lmm_effect>=0?"+":"")+r.lmm_effect.toFixed(4)}} (p=${{fmtP(r.lmm_p)}})` : r.lmm_status;
      h += `<td class="num">${{lmm}}</td>`;
    }}
    h += `</tr>`;
  }});
  h += `</tbody></table>`;
  document.getElementById("knob-table").innerHTML = h;
}}

function renderInteractions() {{
  const cRows = DATA.combos.filter(r => r.model_key === state.model && r.pov === state.pov && r.outcome === state.outcome && r.pair_id === state.pair);
  const sRows = DATA.simple.filter(r => r.model_key === state.model && r.pov === state.pov && r.outcome === state.outcome && r.pair_id === state.pair);
  if (!cRows.length) return;
  const isPct = cRows[0].unit === "pp";
  const fv = v => v == null ? "—" : (isPct ? v.toFixed(2) + "%" : v.toFixed(4));
  const fe = v => v == null ? "—" : (isPct ? (v >= 0 ? "+" : "") + v.toFixed(2) + " pp" : (v >= 0 ? "+" : "") + v.toFixed(4));

  let ch = `<table><thead><tr><th>16-DNA Combo</th><th class="num">Non-NaN N</th><th class="num">Towns</th><th class="num">Controlled Mean</th><th class="num">95% CI</th><th class="num">Clustered SE</th></tr></thead><tbody>`;
  cRows.forEach(r => {{
    const ci = `[${{fv(r.ci_low).replace("%","")}}, ${{fv(r.ci_high)}}]`;
    ch += `<tr><td><b><code>${{r.combo_label}}</code></b></td><td class="num">${{r.combo_n_obs.toLocaleString()}}</td><td class="num">${{r.combo_n_towns.toLocaleString()}}</td><td class="num strong">${{fv(r.mean)}}</td><td class="num">${{ci}}</td><td class="num">${{fv(r.se_clustered)}}</td></tr>`;
  }});
  ch += `</tbody></table>`;
  document.getElementById("combo-table").innerHTML = ch;

  let sh = `<table><thead><tr><th>Comparison</th><th>Combos Compared</th><th class="num">N (Hi / Lo)</th><th class="num">Hi Mean</th><th class="num">Lo Mean</th><th class="num">Diff</th><th class="num">95% CI</th><th class="num">p (Clustered)</th></tr></thead><tbody>`;
  sRows.forEach(r => {{
    const sig = r.p_clustered < 0.05;
    const cls = !sig ? "ns" : (r.effect >= 0 ? "sig-pos" : "sig-neg");
    const ci = `[${{fe(r.ci_low).replace(" pp","")}}, ${{fe(r.ci_high)}}]`;
    const np = `${{r.n_obs_hi.toLocaleString()}} / ${{r.n_obs_lo.toLocaleString()}}`;
    sh += `<tr><td><b>${{r.comparison}}</b></td><td><code>${{r.combo_contrast}}</code></td><td class="num">${{np}}</td><td class="num">${{fv(r.mean_hi)}}</td><td class="num">${{fv(r.mean_lo)}}</td><td class="num ${{cls}}">${{fe(r.effect)}}${{stars(r.p_clustered)}}</td><td class="num">${{ci}}</td><td class="num ${{cls}}">${{fmtP(r.p_clustered)}}</td></tr>`;
  }});
  sh += `</tbody></table>`;
  document.getElementById("simple-table").innerHTML = sh;
}}

function dnaTableHtml(list, col, isPct) {{
  let h = `<table><thead><tr><th>#</th><th>Cell</th><th>Source DNA</th><th class="num">Towns</th><th class="num">Valid N</th><th class="num">Ment. N</th><th class="num">Target</th><th class="num">Belief</th><th class="num">GO %</th><th class="num">SKIP %</th><th class="num">FACT %</th><th class="num">UNCERTAIN %</th><th class="num">SKEPTICAL %</th><th class="num">CHECKED_TRUE %</th><th class="num">CHECKED_FALSE %</th><th class="num">NOT_MENTIONED %</th></tr></thead><tbody>`;
  list.forEach((r, i) => {{
    const t = r[col] == null ? "—" : (isPct ? r[col].toFixed(1) + "%" : r[col].toFixed(4));
    h += `<tr><td>${{i+1}}</td><td>${{r.cell_id}}</td><td>${{r.cell_name}}</td><td class="num">${{r.n_towns}}</td><td class="num">${{r.valid_n}}</td><td class="num">${{r.mentioned_n}}</td><td class="num strong">${{t}}</td><td class="num">${{f3(r.belief)}}</td><td class="num">${{f1(r.go_pct)}}</td><td class="num">${{f1(r.skip_pct)}}</td><td class="num">${{f1(r.FACT_pct)}}</td><td class="num">${{f1(r.UNCERTAIN_pct)}}</td><td class="num">${{f1(r.SKEPTICAL_pct)}}</td><td class="num">${{f1(r.CHECKED_TRUE_pct)}}</td><td class="num">${{f1(r.CHECKED_FALSE_pct)}}</td><td class="num">${{f1(r.NOT_MENTIONED_pct)}}</td></tr>`;
  }});
  return h + `</tbody></table>`;
}}

function renderDNA() {{
  const rows = DATA.dna.filter(r => r.model_key === state.model && r.pov === state.pov);
  const meta = DATA.rank_metrics.find(m => m.key === state.rankMetric);
  const col = (state.rankMetric === "belief" || state.rankMetric === "skip_pct") ? state.rankMetric : `${{state.rankMetric}}_pct`;
  const zeroCount = rows.filter(r => (r[col] || 0) === 0).length;
  document.getElementById("dna-note").textContent = (meta.is_pct && zeroCount > 10)
    ? `Note: ${{zeroCount}} of 64 cells are 0.0% (ties broken by Belief, SKIP %, Cell ID).`
    : `Tie-breaker: Belief / SKIP % / Cell ID.`;

  const cmp = (asc) => (a, b) => {{
    const va = a[col] ?? -999, vb = b[col] ?? -999;
    if (va !== vb) return asc ? va - vb : vb - va;
    if (state.rankMetric === "belief") {{
      if (a.skip_pct !== b.skip_pct) return b.skip_pct - a.skip_pct;
    }} else if (state.rankMetric === "skip_pct") {{
      if (a.belief !== b.belief) return b.belief - a.belief;
    }} else {{
      if (a.belief !== b.belief) return b.belief - a.belief;
      if (a.skip_pct !== b.skip_pct) return b.skip_pct - a.skip_pct;
    }}
    return a.cell_id - b.cell_id;
  }};
  const top10 = [...rows].sort(cmp(false)).slice(0, 10);
  const bot10 = [...rows].sort(cmp(true)).slice(0, 10);
  document.getElementById("dna-top").innerHTML = dnaTableHtml(top10, col, meta.is_pct);
  document.getElementById("dna-bot").innerHTML = dnaTableHtml(bot10, col, meta.is_pct);
}}

function renderAll() {{ renderKnobs(); renderInteractions(); renderDNA(); }}
renderAll();
</script>
</body>
</html>"""


# --------------------------------------------------------------------------- build driver
def build_single_report(
    listeners: pd.DataFrame,
    cells: pd.DataFrame,
    conditions: pd.DataFrame,
    condition_type: str,
    out_dir: Path,
) -> dict:
    df, cond, dyadic = prepare_condition_frames(listeners, cells, conditions, condition_type)
    table_a, table_b = compute_summary_tables(df, cond)
    dyadic_df = compute_dyadic_gatekeeper(dyadic, cond)
    dna_df = compute_dna_metrics(df, cond, dyadic)
    knobs_df, combos_df, simple_df = compute_knob_effects(df)

    csv_dir = out_dir / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    table_a.to_csv(csv_dir / "summary_by_model_layer.csv", index=False)
    table_b.to_csv(csv_dir / "summary_experiment_overall.csv", index=False)
    dyadic_df.to_csv(csv_dir / "dyadic_gatekeeper.csv", index=False)
    dna_df.to_csv(csv_dir / "dna_rankings_all64.csv", index=False)
    knobs_df.to_csv(csv_dir / "knob_effects.csv", index=False)
    combos_df.to_csv(csv_dir / "interaction_combos.csv", index=False)
    simple_df.to_csv(csv_dir / "interaction_simple_effects.csv", index=False)

    (out_dir / "report.md").write_text(
        render_markdown(condition_type, table_a, table_b, dyadic_df, dna_df, knobs_df, combos_df, simple_df),
        encoding="utf-8",
    )
    (out_dir / "report.html").write_text(
        render_html(condition_type, table_a, table_b, dyadic_df, dna_df, knobs_df, combos_df, simple_df),
        encoding="utf-8",
    )
    return {
        "condition": condition_type,
        "out_dir": str(out_dir),
        "knobs_rows": len(knobs_df),
        "combos_rows": len(combos_df),
        "simple_rows": len(simple_df),
        "dna_rows": len(dna_df),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    res = Path(args.results)
    out = Path(args.out)
    listeners = pd.read_csv(res / "listeners.csv")
    cells = pd.read_csv(res / "cells.csv")
    conditions = pd.read_csv(res / "conditions.csv")

    summaries = [
        build_single_report(listeners, cells, conditions, "rumor", out / "rumor_towns"),
        build_single_report(listeners, cells, conditions, "truth_twin", out / "truth_towns"),
    ]
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
