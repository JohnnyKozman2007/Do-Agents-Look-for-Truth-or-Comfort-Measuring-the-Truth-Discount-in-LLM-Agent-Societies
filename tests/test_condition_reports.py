"""Unit tests for scripts/build_condition_reports.py."""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_condition_reports as bcr


def _synthetic_dataset():
    """Minimal balanced 64-cell factorial toy dataset with 1 town per cell, plus INVALID and NOT_MENTIONED rows."""
    levels = [(a, b) for _, a, b in bcr.FACTORS]
    rows = []
    cond_rows = []
    cell_rows = []
    for cell_idx, vals in enumerate(itertools.product(*levels), start=1):
        closeness, authority, reliability, wealth, gender, age = vals
        cell_name = f"{closeness} / {authority} / {reliability} / {wealth} / {gender}_{age}"
        cell_rows.append({"cell_id": cell_idx, "cell_name": cell_name})
        for model_key in ("deepseek_v4_flash", "qwen_3_8_flash"):
            cond_rows.append({
                "model_key": model_key,
                "cell_id": cell_idx,
                "condition_type": "rumor",
                "transmission_keyword_count": 6,
                "transmission_observed_denominator": 6,
                "evidence_keyword_count": 2,
                "evidence_checker_denominator": 3,
                "go_first_hand_fallback_skip_count": 0,
                "go_second_hand_fallback_skip_count": 0,
            })
            for rep in range(2):
                artist = bcr.ARTISTS[rep]
                run_id = f"{model_key}__cell-{cell_idx:02d}__rep-{rep}__rumor"
                for seat in range(1, 13):
                    layer = "first_hand" if seat <= 6 else "second_hand"
                    # Inject known closeness effect on belief & FACT, plus 1 invalid and 1 not_mentioned row.
                    if cell_idx == 1 and rep == 0 and seat == 1:
                        status, label, belief, mentioned, decision = "invalid", np.nan, np.nan, np.nan, "SKIP"
                    elif cell_idx == 2 and rep == 0 and seat == 7:
                        status, label, belief, mentioned, decision = "valid", "NOT_MENTIONED", np.nan, 0, "SKIP"
                    elif closeness == "close_friend":
                        status, label, belief, mentioned, decision = "valid", "FACT", 1.0, 1, "SKIP"
                    else:
                        status, label, belief, mentioned, decision = "valid", "SKEPTICAL", 0.0, 1, "GO"
                    rows.append({
                        "run_id": run_id,
                        "pair_id": f"pair-{cell_idx}-{rep}",
                        "model_key": model_key,
                        "cell_id": cell_idx,
                        "condition_type": "rumor",
                        "truth": 0,
                        "layout_id": 0,
                        "repetition_id": rep,
                        "real_artist": artist,
                        "closeness": closeness,
                        "authority": authority,
                        "reliability": reliability,
                        "wealth": wealth,
                        "gender": gender,
                        "age": age,
                        "seat_id": seat,
                        "layer": layer,
                        "judgment_status": status,
                        "label": label,
                        "belief": belief,
                        "mentioned": mentioned,
                        "decision": decision,
                    })
    return pd.DataFrame(rows), pd.DataFrame(cell_rows), pd.DataFrame(cond_rows)


def test_invalid_not_zero_imputed_and_summary_tables():
    listeners, cells, conditions = _synthetic_dataset()
    df, cond, dyadic = bcr.prepare_condition_frames(listeners, cells, conditions, "rumor")

    inv = df[df["judgment_status"] == "invalid"].iloc[0]
    assert pd.isna(inv["belief"])
    assert pd.isna(inv["belief_sil0"])
    assert pd.isna(inv["belief_sil05"])
    for lbl in bcr.LABELS:
        assert pd.isna(inv[f"label_{lbl}"])

    nm = df[df["label"] == "NOT_MENTIONED"].iloc[0]
    assert pd.isna(nm["belief"])
    assert nm["belief_sil0"] == 0.0
    assert nm["belief_sil05"] == 0.5
    assert nm["label_NOT_MENTIONED"] == 1.0

    table_a, table_b = bcr.compute_summary_tables(df, cond)
    ds_overall = table_a[(table_a["model_key"] == "deepseek_v4_flash") & (table_a["layer"] == "overall")].iloc[0]
    assert ds_overall["invalid_n"] == 1
    assert abs(sum(ds_overall[f"{lbl}_pct"] for lbl in bcr.LABELS) - 100.0) < 1e-9
    assert len(table_b) == 3

    dy_tbl = bcr.compute_dyadic_gatekeeper(dyadic, cond)
    assert set(dy_tbl["fh_partner_decision"]) == {"ALL", "GO", "SKIP"}


def test_dna_tie_breaking_and_knob_effects():
    listeners, cells, conditions = _synthetic_dataset()
    df, cond, dyadic = bcr.prepare_condition_frames(listeners, cells, conditions, "rumor")
    dna_df = bcr.compute_dna_metrics(df, cond, dyadic)
    sub = dna_df[(dna_df["model_key"] == "deepseek_v4_flash") & (dna_df["pov"] == "source")]
    top, zeros = bcr.rank_dna_table(sub, "CHECKED_TRUE", ascending=False, limit=10)
    assert zeros == 64
    assert len(top) == 10
    # Tie-breaker picks closeness=close_friend (higher belief=1.0, skip_pct=100%) first.
    assert top.iloc[0]["belief"] == 1.0

    knobs, combos, simple = bcr.compute_knob_effects(df)
    sub_k = knobs[
        (knobs["model_key"] == "deepseek_v4_flash")
        & (knobs["pov"] == "source")
        & (knobs["outcome"] == "belief")
    ]
    assert len(sub_k) == 10
    assert set(sub_k["test_type"]) == {"main", "interaction"}
    closeness_row = sub_k[sub_k["factor"] == "closeness"].iloc[0]
    assert closeness_row["effect"] > 0.99
    assert closeness_row["p_holm"] < 0.001

    sub_c = combos[
        (combos["model_key"] == "deepseek_v4_flash")
        & (combos["pov"] == "source")
        & (combos["outcome"] == "belief")
        & (combos["pair_id"] == "closeness_x_reliability")
    ]
    assert len(sub_c) == 4
    sub_s = simple[
        (simple["model_key"] == "deepseek_v4_flash")
        & (simple["pov"] == "source")
        & (simple["outcome"] == "belief")
        & (simple["pair_id"] == "closeness_x_reliability")
    ]
    assert len(sub_s) == 4
