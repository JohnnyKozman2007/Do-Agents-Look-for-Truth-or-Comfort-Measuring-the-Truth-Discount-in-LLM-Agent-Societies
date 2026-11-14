#!/usr/bin/env python3
"""Run the Tier 2 behavioral analyses (metrics 7, 8, 9) and write the HTML report. No labels or LLM calls needed.

Usage:
    python3 run_tier2.py --data SHARD_DIR [SHARD_DIR ...] --out OUT_DIR [--refresh] [--boot 2000]

--data   one or more folders that hold the run directories (e.g. .../outputs/main-owner-0); shards must not overlap
--out    output folder: listeners_<hash>.csv (cached), tables/*.csv, tier2_report.html
Requires only numpy and pandas.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import build_report  # noqa: E402
import m7_check_rates  # noqa: E402
import m8_second_hand  # noqa: E402
import m9_who_checks  # noqa: E402
from t2lib import read_listeners  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True, help="folder(s) of run directories")
    ap.add_argument("--out", required=True)
    ap.add_argument("--refresh", action="store_true", help="re-extract the listener table even if cached")
    ap.add_argument("--boot", type=int, default=2000, help="bootstrap resamples")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "tables"), exist_ok=True)
    t0 = time.time()

    print("[1/4] listeners")
    df = read_listeners(a.data, a.out, refresh=a.refresh)
    print(f"      {len(df):,} listener rows, {df.run_id.nunique():,} towns ({time.time() - t0:.0f}s)")

    results = []
    for n, mod in ((2, m7_check_rates), (3, m8_second_hand), (4, m9_who_checks)):
        print(f"[{n}/4] {mod.__name__}")
        r = mod.run(df, B=a.boot) if mod is not m9_who_checks else mod.run(df, B=max(500, a.boot // 2))
        results.append(r)
        for name, t in r["tables"].items():
            t.to_csv(os.path.join(a.out, "tables", f"{name}.csv"), index=False)

    out = os.path.join(a.out, "tier2_report.html")
    build_report.build(results, df, ", ".join(os.path.abspath(d) for d in a.data), out)
    print(f"[done] {out}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
