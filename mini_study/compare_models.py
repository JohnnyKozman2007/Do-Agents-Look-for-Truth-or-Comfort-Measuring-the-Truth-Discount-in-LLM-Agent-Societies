#!/usr/bin/env python3
"""Side-by-side comparison of every model run in the mini study (reads each run's summary.csv + decisions.csv)."""
import csv, os, sys
import pandas as pd


def md(t):
    t = t.reset_index()
    cols = [str(c) for c in t.columns]
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(str(v) for v in r) + " |" for r in t.itertuples(index=False)]
    return "\n".join(rows)

RUNS = [("terra_full", "GPT-6.1 Terra"), ("sonnet_full", "Claude Sonnet 5.5"), ("sol_full", "GPT-6.1 Sol"),
        ("luna_full", "GPT-6 Luna"), ("opus_full", "Claude Opus 5.5")]
here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
frames = []
for d, name in RUNS:
    p = os.path.join(here, d, "summary.csv")
    if os.path.exists(p):
        s = pd.read_csv(p); frames.append(s)
S = pd.concat(frames).drop_duplicates(["table", "group", "model"])
order = [n for _, n in RUNS if n in set(S.model)] + ["deepseek_v4_flash", "qwen_3_8_flash"]
def piv(table, fmt):
    t = S[S.table == table].pivot_table(index="group", columns="model", values="go_rate", aggfunc="first")[order]
    return t.map(fmt)
pc = lambda v: f"{100*v:.0f}%"; pp = lambda v: f"{100*v:+.0f}"
out = ["# Mini study: all models on the same 576 prompts\n",
       "## Overall P(GO)\n", md(piv("Overall P(GO)", pc)),
       "\n## P(GO) by reliability x closeness\n", md(piv("P(GO) by reliability x closeness", pc)),
       "\n## Cue effects (percentage points, first level minus second)\n", md(piv("cue effects", pp))]
dec = None
for d, name in RUNS:
    p = os.path.join(here, d, "decisions.csv")
    if os.path.exists(p):
        x = pd.read_csv(p)[["item_id", "new"]].rename(columns={"new": name})
        dec = x if dec is None else dec.merge(x, on="item_id")
if dec is not None:
    names = [c for c in dec.columns if c != "item_id"]
    agree = pd.DataFrame({a: {b: f"{(dec[a] == dec[b]).mean():.0%}" for b in names} for a in names})
    out += ["\n## Share of identical decisions between models\n", md(agree)]
open(os.path.join(here, "comparison.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
