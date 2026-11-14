#!/usr/bin/env python3
"""Run the Tier 3 / Tier 4 belief-based analyses and write one HTML report plus a CSV per table.

Usage:
  python3 run_tier34.py --data SHARD_DIR [SHARD_DIR ...] --labels LABELS_FILE [LABELS_FILE ...] --out OUT_DIR
                        [--judge-name "Gemini 3.7 Flash"] [--boot 2000] [--refresh] [--only m10,m12] [--no-text]

  --data    folders that hold the run directories (e.g. .../outputs/main-owner-0); pass several to pool shards
  --labels  .csv or .jsonl files with columns run_id, seat (or seat_id) and label (FACT, UNCERTAIN, SKEPTICAL, CHECKED_TRUE,
            CHECKED_FALSE, NOT_MENTIONED); extra columns are ignored
Requires only numpy and pandas. Metrics: 10-17, 18 (keyword pass) and 20. Skipped: 19, 21, 22.
"""
import argparse
import os
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_report34  # noqa: E402
import m10_primary_td, m11_checkers, m12_contrasts, m13_asymmetry, m14_cell_map, m15_second_hand_td  # noqa: E401,E402
import m16_model_comparison, m17_variance, m18_keywords, m20_dna_ranking  # noqa: E401,E402
import t3lib  # noqa: E402

SKIPPED = [
    "metric 19 (judge sensitivity: needs labels from several judges on the full set)",
    "metrics 21 and 22 (excluded by request)",
    "margin- or probability-based analyses (the Gemini labels carry no probabilities)",
    "LLM coding of agent reasoning (metric 18 is a keyword-only pass)",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--judge-name", default="the LLM judge")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--refresh", action="store_true", help="rebuild cached listener and text tables")
    ap.add_argument("--only", help="comma-separated metric ids to run, e.g. m10,m12")
    ap.add_argument("--no-text", action="store_true", help="skip the keyword pass (metric 18)")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "tables"), exist_ok=True)
    t0 = time.time()

    print("[1/4] listeners")
    df = t3lib.read_listeners(a.data, a.out, refresh=a.refresh)
    print(f"      {len(df):,} listeners, {df.run_id.nunique():,} towns, {df.pair_id.nunique():,} pairs")

    print("[2/4] labels")
    labels = t3lib.read_labels(a.labels)
    d = t3lib.attach_scores(df, labels)
    cov = t3lib.coverage_table(d)
    cov.to_csv(os.path.join(a.out, "tables", "label_coverage.csv"), index=False)
    share = d.labeled.mean()
    print(f"      {int(d.labeled.sum()):,} of {len(d):,} listeners labeled ({100 * share:.1f}%); {int(d.omitted.sum()):,} NOT_MENTIONED")
    extra = len(labels) - int(d.labeled.sum())
    if extra:
        print(f"      note: {extra:,} label rows did not match any listener (wrong run_id/seat or a shard that was not passed to --data)")
    if share < 0.95:
        print("      WARNING: under 95% of listeners are labeled; estimates use only the labeled listeners and pairs missing a twin are dropped")

    mods = {"m10": lambda: m10_primary_td.run(d, B=a.boot), "m11": lambda: m11_checkers.run(d, B=a.boot),
            "m12": lambda: m12_contrasts.run(d, B=a.boot), "m13": lambda: m13_asymmetry.run(d, B=a.boot),
            "m14": lambda: m14_cell_map.run(d, B=min(500, a.boot)), "m15": lambda: m15_second_hand_td.run(d, B=a.boot),
            "m16": lambda: m16_model_comparison.run(d, B=a.boot), "m17": lambda: m17_variance.run(d, B=min(300, a.boot)),
            "m18": lambda: m18_keywords.run(d, m18_keywords.read_text_flags(a.data, a.out, refresh=a.refresh), B=min(500, a.boot)),
            "m20": lambda: m20_dna_ranking.run(d, B=500, splits=500)}
    wanted = [m.strip() for m in a.only.split(",")] if a.only else list(mods)
    if a.no_text and "m18" in wanted:
        wanted.remove("m18")
    results = []
    print(f"[3/4] metrics: {', '.join(wanted)}")
    for m in wanted:
        t1 = time.time()
        try:
            r = mods[m]()
        except Exception:
            traceback.print_exc()
            r = dict(id=m, title=f"{m} - FAILED", summary=["This metric raised an error; see the console output."], blocks=[], tables={})
        results.append(r)
        for name, t in r["tables"].items():
            t.to_csv(os.path.join(a.out, "tables", f"{name}.csv"), index=False)
        print(f"      {m} done ({time.time() - t1:.0f}s)")

    print("[4/4] report")
    out = os.path.join(a.out, "tier34_report.html")
    syn = any("SYNTHETIC" in os.path.basename(p).upper() for p in a.labels)
    build_report34.build(results, d, a.data, a.labels, a.judge_name, out, SKIPPED + ([] if not a.no_text else ["metric 18 (--no-text)"]), synthetic=syn)
    print(f"[done] {out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
