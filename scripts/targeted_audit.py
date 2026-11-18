"""Targeted human audit of the Gemini judge labels, split into rater shards.

Subcommands (stdlib only, no model calls):

  build   Read the judging plan + Gemini attempts log, partition every phone call
          into audit strata (Roshan's targeted design), draw the sample, and write
          one blind sheet per rater into audit/targeted/ (committable).
  label   Interactive, resumable terminal labeler for one rater sheet.
  status  Completion count per rater sheet.
  score   Gemini-vs-human agreement: raw and population-weighted, per stratum /
          label / model / layer / condition, inter-rater kappa, coverage audit.

Typical flow:
  python scripts/targeted_audit.py build --raters 5
  python scripts/targeted_audit.py label audit/targeted/sheets/rater-1.csv
  python scripts/targeted_audit.py score
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JUDGED = ROOT / "outputs" / "judged-main" / "gemini-3.7-flash-v2"
DEFAULT_AUDIT = ROOT / "audit" / "targeted"
DEFAULT_EXCLUDE = ROOT / "audit" / "bakeoff_human_labels_100.csv"
LABELS = ["FACT", "UNCERTAIN", "SKEPTICAL", "CHECKED_TRUE", "CHECKED_FALSE", "NOT_MENTIONED"]
KEYS = {str(i + 1): label for i, label in enumerate(LABELS)}
ARTISTS = ("Vesper Vance", "Kaelen Cross")
FIRST_HAND_SEATS = {1, 2, 3, 4, 5, 6}
SHEET_FIELDS = ["audit_id", "announced_artist", "transcript", "human_label", "notes"]
KEY_FIELDS = ["audit_id", "item_id", "run_id", "seat_id", "model_key", "cell_id", "condition_type", "layer",
              "stratum", "flags", "stratum_population", "stratum_n", "gemini_label", "gemini_status",
              "gemini_quote", "gemini_source", "raters"]

# Assignment order matters: an item goes to the FIRST stratum it qualifies for.
# (name, default quota). Roshan's first draft; total 360.
STRATA = [
    ("UNPARSED_OR_RETRIED", 30),   # invalid (quote mismatch / bad JSON), length-truncated, retried
    ("NOT_MENTIONED_RULE", 20),    # keyword-rule omissions, never judged by the model
    ("NOT_MENTIONED_JUDGE", 60),
    ("FACT", 50),
    ("UNCERTAIN", 80),
    ("CHECKED_FALSE", 40),
    ("CHECKED_TRUE", 40),
    ("SKEPTICAL", 40),
]
POSTER = re.compile(r"poster|noticeboard|notice board|community hall|the board|bus\b|checked|went to see|saw it", re.I)

RUBRIC = """# Labeling instructions

Work independently. Read each transcript and write ONE label in `human_label`. Do not edit any other column.
Use the person's LAST statement about the possible concert by the announced artist.

- FACT: states the concert is happening, with no doubt or hesitation.
- UNCERTAIN: says it might be happening, is unsure, or expresses ambiguity.
- SKEPTICAL: says it probably is not happening, doubts the claim, or calls it an unverified rumor.
- CHECKED_TRUE: they, or someone they spoke with, physically went to the town noticeboard and read that the concert is confirmed.
- CHECKED_FALSE: they, or someone they spoke with, physically went to the noticeboard and read that the announced artist is NOT performing (e.g. the poster names a different artist).
- NOT_MENTIONED: never brings up the concert at all, or dodges the topic even when asked.

CRITICAL: saying only that someone claimed they saw a poster, without anyone actually going to the Community Hall
noticeboard, is FACT or UNCERTAIN, not CHECKED.

If a case is genuinely ambiguous, pick the closest label and explain in `notes` (e.g. "relay of other artist",
"false because of date/venue"). Those notes feed the codebook revision.
"""


# --------------------------------------------------------------------------- loading
def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    return {"model_key": parts[0], "cell_id": parts[1].split("-", 1)[1] if len(parts) > 1 else "",
            "condition_type": parts[-1]}


def listener_text(turns: list[dict]) -> str:
    return " ".join(t["text"] for t in turns if t.get("speaker") == "listener")


def names_in(text: str, artist: str) -> bool:
    low = text.lower()
    return artist.lower() in low or artist.split()[0].lower() in low


def load_plan(path: Path) -> dict[str, dict]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    items = {}
    for it in plan["items"]:
        turns = it["phone_transcript"]
        items[it["item_id"]] = {"item_id": it["item_id"], "run_id": it["run_id"], "seat_id": it["seat_id_private"],
                                "announced_artist": it["target_artist"], "turns": turns, **parse_run_id(it["run_id"])}
    return items


def load_attempts(path: Path) -> dict[str, dict]:
    """Final evaluation per item plus retry / truncation / parse diagnostics."""
    info: dict[str, dict] = defaultdict(lambda: {"attempts": 0, "length": False, "final": None, "rule": None, "raw_label": ""})
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)["event"]
            kind = event["type"]
            if kind == "rule":
                info[event["item_id"]]["rule"] = event["evaluation"]
            elif kind == "finish":
                rec = info[event["item_id"]]
                call = event.get("call") or {}
                rec["attempts"] = max(rec["attempts"], event["attempt"])
                rec["length"] |= call.get("native_stop_reason") == "length"
                rec["final"] = event.get("evaluation") or call.get("parser_evaluation") or {}
                if rec["final"].get("status") != "valid":
                    rec["raw_label"] = raw_label(call)
    return info


def raw_label(call: dict) -> str:
    try:
        content = call["native_response"]["choices"][0]["message"]["content"]
        label = str(json.loads(content).get("label", "")).upper()
        return label if label in LABELS else ""
    except Exception:
        match = re.search(r'"label"\s*:\s*"([A-Z_]+)"', json.dumps(call.get("native_response", "")))
        return match.group(1) if match and match.group(1) in LABELS else ""


def build_pool(plan: dict[str, dict], attempts: dict[str, dict]) -> list[dict]:
    pool = []
    for item_id, item in plan.items():
        rec = attempts.get(item_id)
        if rec is None:
            continue
        text = listener_text(item["turns"])
        target = item["announced_artist"]
        other = next(a for a in ARTISTS if a != target)
        rule, final = rec["rule"], rec["final"]
        if rule is not None:
            status, label, quote, source = rule.get("status", "valid"), rule["label"], "", "rule"
        else:
            final = final or {}
            status, label, quote, source = final.get("status", "missing"), final.get("label") or "", final.get("quote") or "", "judge"
        flags = []
        if status != "valid":
            flags.append("invalid_label")
        if rec["length"]:
            flags.append("length_truncated")
        if rec["attempts"] > 1:
            flags.append("retried")
        if names_in(text, other) and not names_in(text, target):
            flags.append("only_other_artist")
        if label == "FACT" and POSTER.search(text):
            flags.append("fact_mentions_poster")
        if label == "CHECKED_FALSE" and not names_in(text, other):
            flags.append("checked_false_no_other_artist")
        if status != "valid" or rec["length"] or rec["attempts"] > 1:
            stratum = "UNPARSED_OR_RETRIED"
            label = label or rec["raw_label"]
        elif source == "rule":
            stratum = "NOT_MENTIONED_RULE"
        elif label == "NOT_MENTIONED":
            stratum = "NOT_MENTIONED_JUDGE"
        else:
            stratum = label
        priority = (("only_other_artist" in flags and label == "NOT_MENTIONED") or "fact_mentions_poster" in flags
                    or "checked_false_no_other_artist" in flags or stratum == "UNPARSED_OR_RETRIED")
        pool.append({**item, "layer": "first_hand" if item["seat_id"] in FIRST_HAND_SEATS else "second_hand",
                     "gemini_label": label, "gemini_status": status, "gemini_quote": quote, "gemini_source": source,
                     "flags": flags, "stratum": stratum, "priority": priority})
    return pool


# --------------------------------------------------------------------------- sampling
def allocate(total: int, sizes: dict) -> dict:
    """Largest-remainder split of `total` over cells, capped at each cell's size."""
    cells = {k: v for k, v in sizes.items() if v > 0}
    out = {k: 0 for k in sizes}
    total = min(total, sum(cells.values()))
    while total > 0:
        open_cells = [k for k in cells if out[k] < cells[k]]
        share = max(1, total // len(open_cells))
        for k in open_cells:
            take = min(share, cells[k] - out[k], total)
            out[k] += take
            total -= take
            if total == 0:
                break
    return out


def load_excluded_keys(path: Path) -> set[tuple[str, int]]:
    if not path or not path.exists():
        return set()
    excluded: set[tuple[str, int]] = set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if "run_id" in row and "seat_id" in row and row["run_id"] and row["seat_id"]:
                excluded.add((row["run_id"], int(row["seat_id"])))
            elif "item_id" in row and "_seat_" in row["item_id"]:
                run_id, seat = row["item_id"].rsplit("_seat_", 1)
                excluded.add((run_id, int(seat)))
    return excluded


def draw(pool: list[dict], quotas: dict, seed: int, priority_share: float,
         excluded: set[tuple[str, int]] | None = None) -> list[dict]:
    excluded = excluded or set()
    rng = random.Random(seed)
    sample = []
    for name, _ in STRATA:
        members = sorted((p for p in pool if p["stratum"] == name and (p["run_id"], int(p["seat_id"])) not in excluded),
                         key=lambda p: p["item_id"])
        pop_count = sum(1 for p in pool if p["stratum"] == name)
        cells = defaultdict(list)
        for p in members:
            cells[(p["model_key"], p["layer"], p["condition_type"])].append(p)
        alloc = allocate(quotas[name], {c: len(v) for c, v in cells.items()})
        for cell, members_in_cell in cells.items():
            want = alloc[cell]
            first = [p for p in members_in_cell if p["priority"]]
            rest = [p for p in members_in_cell if not p["priority"]]
            rng.shuffle(first)
            rng.shuffle(rest)
            take_first = min(len(first), math.ceil(want * priority_share))
            chosen = first[:take_first] + rest[:want - take_first]
            if len(chosen) < want:
                chosen += first[take_first:take_first + want - len(chosen)]
            sample += [{**p, "stratum_population": pop_count, "stratum_n": 0} for p in chosen]
    counts = Counter(p["stratum"] for p in sample)
    for p in sample:
        p["stratum_n"] = counts[p["stratum"]]
    return sample


def assign_raters(sample: list[dict], raters: int, overlap: float, seed: int) -> None:
    rng = random.Random(seed + 1)
    ordered = sorted(sample, key=lambda p: (p["stratum"], p["model_key"], p["layer"], p["condition_type"], p["item_id"]))
    for i, p in enumerate(ordered):          # round-robin keeps every stratum balanced across raters
        p["raters"] = [i % raters]
    if raters > 1 and overlap > 0:
        double = rng.sample(ordered, round(len(ordered) * overlap))
        for p in double:
            p["raters"].append((p["raters"][0] + 1) % raters)
    rng.shuffle(sample)
    for n, p in enumerate(sample, start=1):
        p["audit_id"] = f"T{n:04d}"


def transcript_text(turns: list[dict]) -> str:
    return "\n".join(f"{t['speaker']}: {t['text']}" for t in turns)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def cmd_build(args) -> None:
    out = Path(args.out)
    if out.exists() and not args.force:
        sys.exit(f"{out} exists; pass --force to rebuild (this discards labels already written there).")
    quotas = {name: round(q * args.scale) for name, q in STRATA}
    if args.quotas:
        quotas.update(json.loads(args.quotas))
    plan = load_plan(Path(args.judged) / "judging_plan.json")
    attempts = load_attempts(Path(args.judged) / "attempts.jsonl")
    pool = build_pool(plan, attempts)
    excluded = load_excluded_keys(Path(args.exclude)) if args.exclude else set()
    sample = draw(pool, quotas, args.seed, args.priority_share, excluded)
    assign_raters(sample, args.raters, args.overlap, args.seed)
    pop = Counter(p["stratum"] for p in pool)
    for rater in range(args.raters):
        mine = [p for p in sample if rater in p["raters"]]
        mine = [{**p, "transcript": transcript_text(p["turns"]), "human_label": "", "notes": ""} for p in mine]
        write_csv(out / "sheets" / f"rater-{rater + 1}.csv", sorted(mine, key=lambda p: p["audit_id"]), SHEET_FIELDS)
    key = [{**p, "flags": "|".join(p["flags"]), "raters": "|".join(str(r + 1) for r in p["raters"])}
           for p in sorted(sample, key=lambda p: p["audit_id"])]
    write_csv(out / "PRIVATE" / "key.csv", key, KEY_FIELDS)
    (out / "labeling_instructions.md").write_text(RUBRIC, encoding="utf-8")
    manifest = {"seed": args.seed, "raters": args.raters, "overlap": args.overlap, "priority_share": args.priority_share,
                "excluded_bakeoff_calls": len(excluded),
                "quotas": quotas, "population_by_stratum": dict(pop), "pool_size": len(pool),
                "sample_size": len(sample), "sample_by_stratum": dict(Counter(p["stratum"] for p in sample)),
                "judged_dir": str(args.judged),
                "attempts_sha256_first_1mb": hashlib.sha256((Path(args.judged) / "attempts.jsonl").open("rb").read(1 << 20)).hexdigest(),
                "note": "Raters get only sheets/rater-N.csv and labeling_instructions.md. Do not open PRIVATE/."}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("pool_size", "sample_size", "population_by_stratum", "sample_by_stratum")}, indent=2))
    print(f"Wrote {args.raters} sheets to {out / 'sheets'}")


# --------------------------------------------------------------------------- labeling
def read_sheet(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def cmd_label(args) -> None:
    path = Path(args.sheet)
    rows = read_sheet(path)
    todo = [r for r in rows if not r["human_label"].strip()]
    print(f"{len(rows) - len(todo)}/{len(rows)} labeled. Keys: " + ", ".join(f"{k}={v}" for k, v in KEYS.items())
          + "; s=skip, q=save+quit. Add a note after the key, e.g. '5 relay of other artist'.")
    for row in todo:
        print("\n" + "=" * 78 + f"\n{row['audit_id']}   announced artist: {row['announced_artist']}\n" + "-" * 78)
        print(row["transcript"])
        while True:
            answer = input("label> ").strip()
            if answer.lower() == "q":
                save(path, rows)
                return
            if answer.lower() == "s":
                break
            key, _, note = answer.partition(" ")
            if key in KEYS:
                row["human_label"], row["notes"] = KEYS[key], note.strip()
                save(path, rows)
                break
            print("Use 1-6, s or q.")
    save(path, rows)
    print("Done.")


def save(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SHEET_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def cmd_status(args) -> None:
    for path in sorted(Path(args.audit).glob("sheets/*.csv")):
        rows = read_sheet(path)
        done = sum(bool(r["human_label"].strip()) for r in rows)
        print(f"{path.stem}: {done}/{len(rows)} labeled")


# --------------------------------------------------------------------------- scoring
def kappa_from_counts(counts: dict) -> float | None:
    total = sum(counts.values())
    if total == 0:
        return None
    rows, cols = Counter(), Counter()
    for (a, b), w in counts.items():
        rows[a] += w
        cols[b] += w
    observed = sum(w for (a, b), w in counts.items() if a == b) / total
    expected = sum(rows[l] * cols[l] for l in LABELS) / total ** 2
    return None if expected == 1 else (observed - expected) / (1 - expected)


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def weighted_counts(items: list[dict]) -> Counter:
    counts = Counter()
    for it in items:
        counts[(it["gemini_label"], it["human"])] += it["weight"]
    return counts


def agreement(items: list[dict]) -> dict:
    k = sum(i["gemini_label"] == i["human"] for i in items)
    lo, hi = wilson(k, len(items))
    w_total = sum(i["weight"] for i in items)
    w_agree = sum(i["weight"] for i in items if i["gemini_label"] == i["human"])
    return {"n": len(items), "agreement_raw": k / len(items) if items else None, "ci95": [lo, hi],
            "agreement_weighted": w_agree / w_total if w_total else None}


def cmd_score(args) -> None:
    audit = Path(args.audit)
    key = {r["audit_id"]: r for r in read_sheet(audit / "PRIVATE" / "key.csv")}
    labels: dict[str, dict[str, str]] = defaultdict(dict)     # audit_id -> rater -> label
    problems = []
    for path in sorted(audit.glob("sheets/*.csv")):
        for row in read_sheet(path):
            value = row["human_label"].strip().upper()
            if not value:
                continue
            if value not in LABELS or row["audit_id"] not in key:
                problems.append(f"{path.stem} {row['audit_id']}: bad label/id '{value}'")
                continue
            labels[row["audit_id"]][path.stem] = value
    if problems:
        sys.exit("Problems:\n" + "\n".join(problems[:20]))
    adjudicated = {}
    if args.adjudicated:
        adjudicated = {r["audit_id"]: r["label"].strip().upper() for r in read_sheet(Path(args.adjudicated))}
    disputes, items, dropped_rows = [], [], []
    for audit_id, by_rater in labels.items():
        row = key[audit_id]
        values = set(by_rater.values())
        if audit_id in adjudicated:
            human = adjudicated[audit_id]
        elif len(values) == 1:
            human = next(iter(values))
        else:
            disputes.append({"audit_id": audit_id, **by_rater, "gemini_label": row["gemini_label"]})
            continue
        item = {**row, "human": human, "weight": int(row["stratum_population"]) / int(row["stratum_n"])}
        (items if row["gemini_status"] == "valid" else dropped_rows).append(item)
    if not items:
        sys.exit("No labeled items with a valid Gemini label yet.")
    overlap_pairs = [(list(v.values())[0], list(v.values())[1]) for v in labels.values() if len(v) >= 2]
    result = {"labeled_items": len(labels), "scored_items": len(items), "disputed_items": len(disputes),
              "target_kappa": 0.85,
              "note": "Weighted figures use stratum population / stratum sample size, so they estimate the full 119,808-call "
                      "population. Raw figures over-represent rare strata and are NOT population estimates."}
    raw = Counter((i["gemini_label"], i["human"]) for i in items)
    result["overall"] = {**agreement(items), "kappa_raw": kappa_from_counts(raw),
                         "kappa_weighted": kappa_from_counts(weighted_counts(items))}
    rng = random.Random(7)
    by_stratum = defaultdict(list)
    for i in items:
        by_stratum[i["stratum"]].append(i)
    boots = []
    for _ in range(args.boot):
        resample = [rng.choice(v) for v in by_stratum.values() for _ in v]
        boots.append(kappa_from_counts(weighted_counts(resample)))
    boots = sorted(b for b in boots if b is not None)
    if boots:
        result["overall"]["kappa_weighted_ci95"] = [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]]
    for name, field in (("by_stratum", "stratum"), ("by_model", "model_key"), ("by_layer", "layer"),
                        ("by_condition", "condition_type"), ("by_gemini_label", "gemini_label")):
        groups = defaultdict(list)
        for i in items:
            groups[i[field]].append(i)
        result[name] = {g: agreement(v) for g, v in sorted(groups.items())}
    result["gemini_precision_by_label_weighted"] = {
        label: (sum(i["weight"] for i in items if i["gemini_label"] == label and i["human"] == label)
                / sum(i["weight"] for i in items if i["gemini_label"] == label))
        for label in LABELS if any(i["gemini_label"] == label for i in items)}
    result["gemini_recall_by_label_weighted"] = {
        label: (sum(i["weight"] for i in items if i["human"] == label and i["gemini_label"] == label)
                / sum(i["weight"] for i in items if i["human"] == label))
        for label in LABELS if any(i["human"] == label for i in items)}
    result["confusion_gemini_to_human_raw"] = {f"{g} -> {h}": n for (g, h), n in raw.most_common() if g != h}
    flagged = defaultdict(list)
    for i in items:
        for flag in filter(None, i["flags"].split("|")):
            flagged[flag].append(i)
    result["by_flag"] = {f: agreement(v) for f, v in sorted(flagged.items())}
    if overlap_pairs:
        result["inter_rater"] = {"pairs": len(overlap_pairs),
                                 "kappa": kappa_from_counts(Counter(overlap_pairs)),
                                 "agreement": sum(a == b for a, b in overlap_pairs) / len(overlap_pairs)}
    result["coverage_audit_unparsed_or_invalid"] = {
        "n": len(dropped_rows),
        "human_label_distribution": dict(Counter(i["human"] for i in dropped_rows)),
        "note": "These calls have no valid Gemini label (dropped from every analysis). Compare to the valid-label mix."}
    res_dir = audit / "results"
    res_dir.mkdir(exist_ok=True)
    (res_dir / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(res_dir / "disputes.csv", disputes, sorted({k for d in disputes for k in d}) or ["audit_id"])
    write_csv(res_dir / "scored_items.csv", [{**i, "weight": round(i["weight"], 4)} for i in items],
              ["audit_id", "stratum", "model_key", "layer", "condition_type", "flags", "gemini_label", "human", "weight"])
    (res_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    print((res_dir / "report.md").read_text(encoding="utf-8"))


def fmt(x) -> str:
    return "-" if x is None else f"{x:.3f}"


def render_report(r: dict) -> str:
    o = r["overall"]
    lines = ["# Targeted human audit of Gemini labels", "",
             f"Labeled items: {r['labeled_items']}; scored (valid Gemini label, no dispute): {r['scored_items']}; "
             f"disputed between raters: {r['disputed_items']}.", "", r["note"], "",
             "## Overall", "",
             f"- Raw agreement {fmt(o['agreement_raw'])}, raw kappa {fmt(o['kappa_raw'])}",
             f"- Population-weighted agreement {fmt(o['agreement_weighted'])}, weighted kappa {fmt(o['kappa_weighted'])} "
             f"(95% CI {', '.join(fmt(x) for x in o.get('kappa_weighted_ci95', []))}); target {r['target_kappa']}", ""]
    if "inter_rater" in r:
        lines += [f"- Inter-rater (double-labeled, {r['inter_rater']['pairs']} pairs): kappa {fmt(r['inter_rater']['kappa'])}, "
                  f"agreement {fmt(r['inter_rater']['agreement'])}", ""]
    for title, key in (("By stratum", "by_stratum"), ("By agent model", "by_model"), ("By layer", "by_layer"),
                       ("By condition", "by_condition"), ("By Gemini label", "by_gemini_label"), ("By flag", "by_flag")):
        lines += [f"## {title}", "", "| group | n | raw agreement | 95% CI | weighted agreement |", "|---|---|---|---|---|"]
        for g, v in r[key].items():
            lines.append(f"| {g} | {v['n']} | {fmt(v['agreement_raw'])} | {fmt(v['ci95'][0])}-{fmt(v['ci95'][1])} | {fmt(v['agreement_weighted'])} |")
        lines.append("")
    lines += ["## Gemini precision / recall per label (weighted, human as reference)", "", "| label | precision | recall |", "|---|---|---|"]
    for label in LABELS:
        lines.append(f"| {label} | {fmt(r['gemini_precision_by_label_weighted'].get(label))} | {fmt(r['gemini_recall_by_label_weighted'].get(label))} |")
    lines += ["", "## Disagreements (Gemini -> human, raw counts)", ""]
    lines += [f"- {k}: {v}" for k, v in r["confusion_gemini_to_human_raw"].items()] or ["- none"]
    c = r["coverage_audit_unparsed_or_invalid"]
    lines += ["", "## Coverage audit (calls with no valid Gemini label)", "", f"n = {c['n']}; human labels: {c['human_label_distribution']}", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="draw the targeted sample and write rater sheets")
    b.add_argument("--judged", default=str(DEFAULT_JUDGED), help="dir with judging_plan.json and attempts.jsonl")
    b.add_argument("--out", default=str(DEFAULT_AUDIT))
    b.add_argument("--exclude", default=str(DEFAULT_EXCLUDE), help="CSV of previously human-labeled calls to exclude")
    b.add_argument("--raters", type=int, default=5)
    b.add_argument("--overlap", type=float, default=0.2, help="share of items given to a second rater (inter-rater kappa)")
    b.add_argument("--scale", type=float, default=1.0, help="multiply every default quota (360 total at 1.0)")
    b.add_argument("--quotas", help='JSON override, e.g. \'{"UNCERTAIN": 120}\'')
    b.add_argument("--priority-share", type=float, default=0.5, help="share of each cell reserved for flagged high-risk calls")
    b.add_argument("--seed", type=int, default=2027)
    b.add_argument("--force", action="store_true")
    b.set_defaults(func=cmd_build)
    l = sub.add_parser("label", help="interactive labeling of one rater sheet")
    l.add_argument("sheet")
    l.set_defaults(func=cmd_label)
    s = sub.add_parser("status", help="completion per rater sheet")
    s.add_argument("--audit", default=str(DEFAULT_AUDIT))
    s.set_defaults(func=cmd_status)
    c = sub.add_parser("score", help="agreement of Gemini with the human labels")
    c.add_argument("--audit", default=str(DEFAULT_AUDIT))
    c.add_argument("--adjudicated", help="CSV audit_id,label resolving rater disputes")
    c.add_argument("--boot", type=int, default=1000)
    c.set_defaults(func=cmd_score)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
