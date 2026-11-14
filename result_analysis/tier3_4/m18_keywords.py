"""Metric 18 - keyword-only transcript analysis (no LLM).

The saved runs hold no hidden reasoning: agent histories contain only what each agent said. So this pass flags cue language in
each listener's own spoken lines (afternoon catch-up and evening phone call) with regular expressions. It is a crude lexical proxy,
not semantic coding: a keyword hit does not prove the motive. Three views:
  1. how common each kind of language is;
  2. whether it differs between listeners who checked (GO) and those who did not;
  3. whether cue language tracks the manipulated source knobs (and, when labels exist, the belief label).
"""
import json
import os
import re

import numpy as np
import pandas as pd

from t3lib import MODEL_NAMES, MODELS, rate_diff_ci
import charts
from t2lib import RUN_RE

FAMILIES = {  # key -> (label, regex)
    "check": ("checking / noticeboard", r"\b(check(ed|ing)?|verif(y|ied|ying)|see for myself|noticeboard|notice board|community hall|poster|bus)\b"),
    "cost": ("cost of checking", r"(\$ ?5\b|five (bucks|dollars)|\bfare\b|worth (it|the|my)|\bwaste\b|\bmoney\b|\bafford|\bcash\b|\bpay(ing)?\b)"),
    "hedge": ("hedging / rumor", r"(rumou?r|gossip|grain of salt|supposedly|apparently|not sure|who knows|could be (something|nothing)|believe it when|unverified|hearsay|take it with)"),
    "trust": ("trust in source", r"(usually (right|spot|reliable)|never (wrong|steered)|\breliable\b|trust(worthy)?|spot[- ]on|count on|good (word|track))"),
    "distrust": ("distrust of source", r"(unreliable|exaggerat|tall tale|wrong before|not (the most )?reliable|you know how \w+ (gets|is)|\bswore\b|cried wolf|track record|shaky)"),
    "authority": ("authority cue", r"\b(mayor|town council|council)\b"),
    "closeness": ("closeness cue", r"\b(friend|buddy|pal)\b"),
    "confirm": ("confirmation", r"(confirm(ed|s)?|it'?s real|\blegit\b|official(ly)?)"),
}
KNOB_LINKS = [  # (family key, knob column, level that should raise the cue)
    ("authority", "authority", "mayor"), ("closeness", "closeness", "close_friend"),
    ("trust", "reliability", "good_record"), ("distrust", "reliability", "poor_record"),
]
SOURCES = {"cu": "catch-up conversation", "ph": "evening phone call"}


def load_text_flags(data_dir, progress=True):
    """One row per listener: keyword hit counts in their own catch-up lines and phone lines. Text itself is not stored."""
    runs = sorted(d for d in os.listdir(data_dir) if RUN_RE.match(d))
    rx = {k: re.compile(v[1], re.I) for k, v in FAMILIES.items()}
    rows = []
    for i, run in enumerate(runs):
        t = json.load(open(os.path.join(data_dir, run, "town.json")))
        own = {}
        for ct in t.get("scene_3_catch_up_transcripts", []):
            for ln in ct.get("lines", []):
                if not ln.get("scripted", False):
                    own.setdefault(("cu", int(ln["seat_id"])), []).append(ln["text"])
        for pt in t.get("scene_5_phone_transcripts", []):
            seat = pt.get("seat_id")
            for ln in pt.get("lines", []):
                if ln.get("speaker") == "listener":
                    own.setdefault(("ph", int(seat)), []).append(ln["text"])
        for seat in range(1, 13):
            r = dict(run_id=t["run_id"], seat=seat)
            for src in SOURCES:
                txt = " ".join(own.get((src, seat), []))
                r[f"{src}_words"] = len(txt.split())
                for k, p in rx.items():
                    r[f"{src}__{k}"] = int(bool(p.search(txt)))
            rows.append(r)
        if progress and (i + 1) % 400 == 0:
            print(f"  scanned text for {i + 1}/{len(runs)} towns", flush=True)
    return pd.DataFrame(rows)


def read_text_flags(data_dirs, out_dir, refresh=False):
    import hashlib
    dirs = [os.path.abspath(x) for x in data_dirs]
    key = hashlib.md5("|".join(sorted(dirs)).encode()).hexdigest()[:8]
    cache = os.path.join(out_dir, f"text_flags_{key}.csv")
    if os.path.exists(cache) and not refresh:
        return pd.read_csv(cache)
    f = pd.concat([load_text_flags(x) for x in dirs], ignore_index=True)
    f.to_csv(cache, index=False)
    return f


def run(d, flags, B=500):
    """d: listener rows with labels; flags: output of read_text_flags."""
    blocks, tables, summary = [], {}, []
    x = d.merge(flags, on=["run_id", "seat"], how="left")
    for c in [c for c in flags.columns if "__" in c]:
        x[c] = x[c].fillna(0)
    blocks += [("h3", "What the keyword pass can and cannot say"),
               ("p", "Only listeners' own spoken lines are scanned. Hits are presence flags per listener (any match in that conversation). "
                     "Treat differences as hints about what language accompanies a decision, not as reasons.")]

    # ---- 1. how common ---------------------------------------------------------------------------------
    rows = []
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            s = x[(x.model == m) & (x.layer == layer)]
            for src, srcname in SOURCES.items():
                for k, (lab, _) in FAMILIES.items():
                    col = f"{src}__{k}"
                    if col in s and len(s):
                        rows.append(dict(model=MODEL_NAMES[m], layer=layer, text=srcname, family=lab, share_with_hit=float(s[col].mean()), listeners=len(s)))
    C = pd.DataFrame(rows)
    tables["m18_family_rates"] = C
    blocks += [("h3", "How common is each kind of language?"),
               ("table", C.pivot_table(index=["model", "layer", "text"], columns="family", values="share_with_hit").reset_index(), "Share of listeners with at least one keyword hit.",
                tuple(l for l, _ in FAMILIES.values()))]

    # ---- 2. language by the listener's own GO/SKIP -------------------------------------------------------
    rows = []
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            s = x[(x.model == m) & (x.layer == layer)].reset_index(drop=True)
            for src, srcname in SOURCES.items():
                for k, (lab, _) in FAMILIES.items():
                    col = f"{src}__{k}"
                    if len(s) == 0 or s[col].sum() < 10:
                        continue
                    dif, lo, hi = rate_diff_ci(s, col, s.go == 1, s.go == 0, B=B)
                    rows.append(dict(model=MODEL_NAMES[m], layer=layer, text=srcname, family=lab, hit_if_GO=float(s[col][s.go == 1].mean()),
                                     hit_if_SKIP=float(s[col][s.go == 0].mean()), diff=dif, lo=lo, hi=hi))
    G = pd.DataFrame(rows)
    tables["m18_language_by_decision"] = G
    blocks += [("h3", "Does the language differ between checkers and non-checkers?"),
               ("p", "Difference in hit rate (GO minus SKIP). The first-hand catch-up comes after the first-hand listener's own GO/SKIP decision, so it can reflect that decision (for example, mentioning the bus or poster). "
                     "For second-hand listeners the catch-up comes before their own decision.")]
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            g = G[(G.model == MODEL_NAMES[m]) & (G.layer == layer)]
            if g.empty:
                continue
            f = [dict(label=f"{r.text.split(' ')[0]} | {r.family}", est=r.diff, lo=r.lo, hi=r.hi, group=0 if r.text.startswith("catch") else 1) for r in g.itertuples()]
            blocks.append(("svg", charts.forest(f, "hit rate: GO minus SKIP", kind="signed", row_h=16, title=f"{MODEL_NAMES[m]} - {layer.replace('_', '-')} listeners")))
    blocks.append(("table", G, "Cluster bootstrap over twin pairs."))
    top = G[G.layer == "first_hand"].sort_values("diff", key=lambda s: s.abs(), ascending=False).head(3)
    for r in top.itertuples():
        summary.append(f"{r.model} first-hand {r.text}: '{r.family}' language is {r.diff * 100:+.0f} points more common among checkers (CI {r.lo * 100:+.0f} to {r.hi * 100:+.0f}).")

    # ---- 3. cue language vs manipulated knobs -----------------------------------------------------------------
    rows = []
    for m in MODELS:
        for layer in ("first_hand", "second_hand"):
            s = x[(x.model == m) & (x.layer == layer)].reset_index(drop=True)
            for fam, col_knob, level in KNOB_LINKS:
                for src, srcname in SOURCES.items():
                    col = f"{src}__{fam}"
                    if len(s) == 0 or s[col].sum() < 10:
                        continue
                    dif, lo, hi = rate_diff_ci(s, col, s[col_knob] == level, s[col_knob] != level, B=B)
                    rows.append(dict(model=MODEL_NAMES[m], layer=layer, text=srcname, cue=FAMILIES[fam][0], knob=f"{col_knob} = {level.replace('_', ' ')}", diff=dif, lo=lo, hi=hi))
    K = pd.DataFrame(rows)
    tables["m18_language_by_knob"] = K
    blocks += [("h3", "Does cue language follow the manipulation?"),
               ("p", "Hit-rate difference when the source has the named knob level versus the other level. Language that does not move with its own knob suggests the listener is not repeating the cue."),
               ("table", K, "Cluster bootstrap over twin pairs.")]
    if len(K):
        for r in K[K.layer == "first_hand"].sort_values("diff", key=lambda s: s.abs(), ascending=False).head(2).itertuples():
            summary.append(f"{r.model} first-hand {r.text}: '{r.cue}' language moves {r.diff * 100:+.0f} points with {r.knob}.")

    # ---- 4. language vs belief label (validity of both) -----------------------------------------------------
    if x.label.notna().any():
        rows = []
        for lab, g in x[x.label.notna()].groupby("label"):
            r = dict(label=lab, listeners=len(g))
            for k in ("hedge", "check", "confirm", "distrust"):
                r[FAMILIES[k][0] + " (phone)"] = float(g[f"ph__{k}"].mean())
            rows.append(r)
        L = pd.DataFrame(rows)
        tables["m18_language_by_label"] = L
        blocks += [("h3", "Does phone-call language line up with the belief label?"),
                   ("p", "A rough validity check on the labels: hedging words should be commonest under UNCERTAIN and SKEPTICAL; checking words under CHECKED_*; confirmation words under FACT and CHECKED_TRUE."),
                   ("table", L, "Share of phone calls with a keyword hit, by label.", tuple(c for c in L.columns if c.endswith("(phone)")))]
    if not summary:
        summary.append("No keyword family had enough hits for a stable comparison.")
    return dict(id="m18", title="Metric 18 - Keyword transcript pass", summary=summary, blocks=blocks, tables=tables)
