"""Unit tests for scripts/build_comparison_report.py."""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_condition_reports as bcr
import build_comparison_report as bcmp


def _synthetic_paired_dataset():
    """Minimal balanced 64-cell dataset with matched Truth and Rumor twins."""
    levels = [(a, b) for _, a, b in bcr.FACTORS]
    rows, cond_rows, cell_rows = [], [], []
    for cell_idx, vals in enumerate(itertools.product(*levels), start=1):
        closeness, authority, reliability, wealth, gender, age = vals
        cell_name = f"{closeness} / {authority} / {reliability} / {wealth} / {gender}_{age}"
        cell_rows.append({"cell_id": cell_idx, "cell_name": cell_name})
        for model_key in ("deepseek_v4_flash", "qwen_3_8_flash"):
            for ctype, truth in (("rumor", 0), ("truth_twin", 1)):
                cond_rows.append({
                    "model_key": model_key,
                    "cell_id": cell_idx,
                    "condition_type": ctype,
                    "transmission_keyword_count": 6,
                    "transmission_observed_denominator": 6,
                    "evidence_keyword_count": 3 if truth == 1 else 2,
                    "evidence_checker_denominator": 4,
                    "go_first_hand_fallback_skip_count": 0,
                    "go_second_hand_fallback_skip_count": 0,
                })
                for rep in range(2):
                    artist = bcr.ARTISTS[rep]
                    pair_id = f"pair-{cell_idx:02d}-{rep}"
                    run_id = f"{model_key}__{pair_id}__{ctype}"
                    for seat in range(1, 13):
                        layer = "first_hand" if seat <= 6 else "second_hand"
                        if cell_idx == 1 and rep == 0 and seat == 1 and truth == 0:
                            status, label, belief, mentioned, decision = "invalid", np.nan, np.nan, np.nan, "SKIP"
                        elif truth == 1 and closeness == "close_friend":
                            # Inject strong asymmetric closeness boost ONLY in Truth Twin (+1.0 on Truth, 0 on Rumor).
                            status, label, belief, mentioned, decision = "valid", "FACT", 1.0, 1, "SKIP"
                        elif truth == 1:
                            status, label, belief, mentioned, decision = "valid", "SKEPTICAL", 0.0, 1, "GO"
                        else:
                            status, label, belief, mentioned, decision = "valid", "SKEPTICAL", 0.0, 1, "GO"
                        rows.append({
                            "run_id": run_id,
                            "pair_id": pair_id,
                            "model_key": model_key,
                            "cell_id": cell_idx,
                            "condition_type": ctype,
                            "truth": truth,
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


def test_paired_truth_discount_and_symmetry_model():
    listeners, cells, conditions = _synthetic_paired_dataset()
    df = bcmp.prepare_all_listeners(listeners, cells)
    assert pd.isna(df[df["judgment_status"] == "invalid"].iloc[0]["belief"])

    ta, tb = bcmp.compute_comparison_summaries(df, conditions)
    ds_all = ta[(ta["model_key"] == "deepseek_v4_flash") & (ta["layer"] == "overall")].iloc[0]
    assert abs(ds_all["truth_discount"] - 0.5) < 0.02
    assert len(tb) == 3

    dna_df = bcmp.compute_paired_dna_truth_discount(df)
    assert len(dna_df) == 64 * 3 * 2

    td_knobs, combos, simple = bcmp.compute_symmetry_and_td_tests(df)
    sub = td_knobs[
        (td_knobs["model_key"] == "deepseek_v4_flash")
        & (td_knobs["pov"] == "source")
        & (td_knobs["outcome"] == "belief")
    ]
    assert len(sub) == 10
    closeness_row = sub[sub["factor"] == "closeness"].iloc[0]
    assert abs(closeness_row["effect_rumor"]) < 1e-6
    assert closeness_row["effect_truth"] > 0.99
    assert closeness_row["effect_td"] > 0.99
    assert closeness_row["p_td_holm"] < 0.001

    assert len(combos[combos["pair_id"] == "closeness_x_reliability"]) > 0
    assert len(simple[simple["pair_id"] == "closeness_x_reliability"]) > 0

    mcmp = bcmp.compute_model_comparison(df)
    assert len(mcmp) == 3 * 6
