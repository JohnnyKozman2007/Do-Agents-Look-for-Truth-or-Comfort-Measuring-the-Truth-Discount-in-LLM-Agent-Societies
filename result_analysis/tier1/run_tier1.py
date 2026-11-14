#!/usr/bin/env python3
"""Run the Tier 1 judge and label-quality metrics (4, 5, 6) on labels produced by a separate judging workflow.

Usage:
    python3 run_tier1.py --data SHARD_DIR [SHARD_DIR ...] --labels LABELS_FILE [LABELS_FILE ...] --out OUT_DIR
                         [--reference-labels REF_FILE [REF_FILE ...]] [--judge-name "Gemini 3.7 Flash"] [--boot 1000] [--refresh]

--labels            the judge's belief labels (.csv or .jsonl with run_id, seat, label)
--reference-labels  optional second label set (human audit or another judge, same format) for agreement statistics in metric 4
Output: OUT_DIR/tier1_report.html and OUT_DIR/tables/*.csv. Requires only numpy and pandas; makes no model calls.
"""
import argparse
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import build_report1  # noqa: E402
import m4_judge_validation, m5_omissions, m6_scoring_sensitivity  # noqa: E401,E402
from t3lib import load_labeled, read_labels  # noqa: E402


def run_metrics(d, reference, boot, out_dir):
    """Run metrics 4-6 on a listener table with labels attached. Writes CSV tables to out_dir/tables; returns the result dicts."""
    os.makedirs(os.path.join(out_dir, "tables"), exist_ok=True)
    mods = {"m4": lambda: m4_judge_validation.run(d, reference=reference, B=min(500, boot)),
            "m5": lambda: m5_omissions.run(d, B=min(500, boot)),
            "m6": lambda: m6_scoring_sensitivity.run(d, B=boot)}
    results = []
    print(f"[3/4] Tier 1 metrics: {', '.join(mods)}")
    for m, fn in mods.items():
        t1 = time.time()
        try:
            r = fn()
        except Exception:
            traceback.print_exc()
            r = dict(id=m, title=f"{m} - FAILED", summary=["This metric raised an error; see the console output."], blocks=[], tables={})
        results.append(r)
        for name, tbl in r["tables"].items():
            tbl.to_csv(os.path.join(out_dir, "tables", f"{name}.csv"), index=False)
        print(f"      {m} done ({time.time() - t1:.0f}s)")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--reference-labels", nargs="+", help="optional reference label set for agreement statistics")
    ap.add_argument("--out", required=True)
    ap.add_argument("--judge-name", default="the LLM judge")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    d = load_labeled(a.data, a.labels, a.out, a.refresh)
    ref = read_labels(a.reference_labels) if a.reference_labels else None
    results = run_metrics(d, ref, a.boot, a.out)
    print("[4/4] report")
    out = os.path.join(a.out, "tier1_report.html")
    syn = any("SYNTHETIC" in os.path.basename(p).upper() for p in a.labels)
    build_report1.build(results, d, a.data, a.labels, a.reference_labels or [], a.judge_name, out, synthetic=syn)
    print(f"[done] {out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
