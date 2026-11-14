#!/usr/bin/env python3
"""Write RANDOM placeholder labels (labels_SYNTHETIC.csv) so the Tier 3/4 code can be tested before real labels exist.

The labels carry no information about the simulation except a crude GO -> CHECKED_* link. Never use them for results;
the report adds a banner when the labels file name contains SYNTHETIC.

Usage: python3 make_fixture.py --data SHARD_DIR [SHARD_DIR ...] --out FILE.csv [--seed 0] [--missing 0.02]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t3lib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--missing", type=float, default=0.02, help="share of listeners left unlabeled")
    ap.add_argument("--cache-dir", default=None, help="where to cache the listener table (default: next to --out)")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    cache = a.cache_dir or os.path.dirname(os.path.abspath(a.out))
    df = t3lib.read_listeners(a.data, cache)
    lab = []
    for r in df.itertuples():
        if r.layer == "first_hand" and r.go == 1:
            lab.append("CHECKED_TRUE" if r.condition == "truth_twin" else "CHECKED_FALSE")
        else:
            lab.append(rng.choice(["FACT", "UNCERTAIN", "SKEPTICAL", "NOT_MENTIONED"], p=[0.3, 0.3, 0.3, 0.1]))
    out = pd.DataFrame({"run_id": df.run_id, "seat": df.seat, "label": lab})
    out = out[rng.random(len(out)) > a.missing]
    out.to_csv(a.out, index=False)
    print(f"wrote {len(out):,} random placeholder labels to {a.out}")


if __name__ == "__main__":
    main()
