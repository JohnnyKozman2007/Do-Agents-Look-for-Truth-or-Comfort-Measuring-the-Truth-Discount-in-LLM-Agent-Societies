"""Unit tests for result_analysis/pov_and_comparison/build_second_hand_2x2_report.py."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "result_analysis" / "pov_and_comparison"))
sys.path.insert(0, str(ROOT / "tests"))

import build_second_hand_2x2_report as sh2x2
from test_comparison_report import _synthetic_paired_dataset


def test_build_second_hand_2x2_report_outputs(tmp_path: Path):
    listeners, _, _ = _synthetic_paired_dataset()
    # Vary first-hand and second-hand decisions so all 4 cells of the 2x2 are populated.
    fh_mask = listeners["layer"] == "first_hand"
    sh_mask = listeners["layer"] == "second_hand"
    listeners.loc[fh_mask & (listeners["seat_id"].isin([1, 2, 3])), "decision"] = "GO"
    listeners.loc[fh_mask & (listeners["seat_id"].isin([4, 5, 6])), "decision"] = "SKIP"
    listeners.loc[sh_mask & (listeners["seat_id"].isin([7, 8, 10])), "decision"] = "GO"
    listeners.loc[sh_mask & (listeners["seat_id"].isin([9, 11, 12])), "decision"] = "SKIP"

    results_dir = tmp_path / "results"
    results_dir.mkdir()
    listeners.to_csv(results_dir / "listeners.csv", index=False)

    out_dir = tmp_path / "reports" / "second_hand_2x2"
    cells_df, tests_df = sh2x2.build_report(results_dir, out_dir)

    assert (out_dir / "report.md").exists()
    assert (out_dir / "report.html").exists()
    assert (out_dir / "csv" / "second_hand_2x2_cells.csv").exists()
    assert (out_dir / "csv" / "second_hand_2x2_factorial_tests.csv").exists()
    # 3 scopes x 4 cells = 12 rows
    assert len(cells_df) == 12
    assert set(cells_df["cell_key"]) == {"both_checked", "sh_only", "partner_only", "neither_checked"}
    assert len(tests_df) > 0
