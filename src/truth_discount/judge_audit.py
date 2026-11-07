"""Human audit of the blind judge: a stratified sample, blind sheets and Cohen's kappa.

The labeling sheet shows raters only what the judge saw: the announced artist and
the phone-call lines. Model, cell, twin condition, seat and the judge's own
label stay in a private key. Strata are twin condition x listener layer.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
import io
import json
from pathlib import Path
import random

from .analysis import load_towns
from .scoring import LABELS

STRATA = [(condition, layer) for condition in ("rumor", "truth_twin") for layer in ("first_hand", "second_hand")]
_MARKER = "\nPHONE CALL TRANSCRIPT:\n"
_SHEET_FIELDS = ["audit_id", "announced_artist", "transcript", "human_label", "notes"]
_KEY_FIELDS = ["audit_id", "run_id", "seat_id", "model_key", "cell_id", "condition_type", "layer", "judge_label"]


def judged_calls(towns: list[dict], config: dict) -> list[dict]:
    """Every phone call the judge labeled validly, with the exact lines it was shown."""
    first = set(config["seating_and_pairing"]["first_hand_seats"])
    items = []
    for town in towns:
        evaluations = {e["seat_id"]: e for e in town["judge_evaluations"]}
        for judged in town["judge_inputs"]:
            seat = judged["seat_id_private"]
            evaluation = evaluations.get(seat, {})
            if evaluation.get("status") != "valid":
                continue
            content = judged["input"]["messages"][0]["content"]
            lines = json.loads(content.split(_MARKER, 1)[1])
            items.append({"run_id": town["run_id"], "seat_id": seat, "model_key": town["model_key"],
                          "cell_id": town["cell_id"], "condition_type": town["condition_type"],
                          "layer": "first_hand" if seat in first else "second_hand",
                          "judge_label": evaluation["label"], "announced_artist": town["announced_artist"],
                          "transcript": "\n".join(f"{line['speaker']}: {line['text']}" for line in lines)})
    return sorted(items, key=lambda item: (item["run_id"], item["seat_id"]))


def stratified_sample(items: list[dict], size: int, seed: int) -> tuple[list[dict], dict]:
    rng = random.Random(seed)
    pools = {stratum: [i for i in items if (i["condition_type"], i["layer"]) == stratum] for stratum in STRATA}
    quota = {stratum: size // len(STRATA) + (index < size % len(STRATA)) for index, stratum in enumerate(STRATA)}
    picked = {s: rng.sample(pools[s], min(quota[s], len(pools[s]))) for s in STRATA}
    # A short stratum is filled from the others, largest leftover pool first.
    short = size - sum(len(v) for v in picked.values())
    while short > 0:
        leftovers = {s: [i for i in pools[s] if i not in picked[s]] for s in STRATA}
        stratum = max(STRATA, key=lambda s: len(leftovers[s]))
        if not leftovers[stratum]:
            break
        picked[stratum].append(rng.choice(leftovers[stratum]))
        short -= 1
    sample = [item for s in STRATA for item in picked[s]]
    rng.shuffle(sample)   # sheet order must not reveal the strata
    counts = {f"{c}/{l}": len(picked[(c, l)]) for c, l in STRATA}
    return sample, counts


def _csv(rows: list[dict], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows({k: row[k] for k in fields} for row in rows)
    return stream.getvalue()


def make_audit(output_root: Path, destination: Path, *, size: int = 100, seed: int = 2027) -> dict:
    towns, config, _ = load_towns(output_root)
    items = judged_calls(towns, config)
    if len(items) < size:
        raise ValueError(f"only {len(items)} judged phone calls are available for a sample of {size}")
    sample, counts = stratified_sample(items, size, seed)
    for number, item in enumerate(sample, start=1):
        item.update(audit_id=f"A{number:03d}", human_label="", notes="")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    protocol = config["judging_and_scoring"]["human_audit_protocol"]
    meta = {"size": size, "seed": seed, "strata": counts, "threshold": protocol["target_threshold"],
            "config_sha256": towns[0]["config_sha256"], "evidence_kind": towns[0]["evidence_kind"],
            "judged_calls_available": len(items)}
    rubric = config["judging_and_scoring"]["canonical_judge_prompt"].replace(
        "{announced_artist}", "the sheet's announced artist")
    rubric = rubric.split("REPLY STRICTLY AS JSON:")[0].rstrip()
    (destination / "labeling_sheet.csv").write_text(_csv(sample, _SHEET_FIELDS), encoding="utf-8", newline="")
    (destination / "audit_key_PRIVATE.csv").write_text(_csv(sample, _KEY_FIELDS), encoding="utf-8", newline="")
    (destination / "audit_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (destination / "labeling_instructions.md").write_text(
        "# Labeling instructions\n\nWork alone and do not look at the private key or the run outputs. "
        "For each row, read the transcript and write exactly one label in `human_label`. "
        "Each rater fills a separate copy of `labeling_sheet.csv`, named after the rater.\n\n"
        + rubric + "\n", encoding="utf-8")
    return meta


def cohen_kappa(first: list[str], second: list[str]) -> float | None:
    """Unweighted kappa; None when chance agreement is 1 (a single shared label)."""
    n = len(first)
    if n == 0 or n != len(second):
        raise ValueError("kappa needs two equal, nonempty label lists")
    observed = sum(a == b for a, b in zip(first, second)) / n
    a, b = Counter(first), Counter(second)
    expected = sum(a[label] * b[label] for label in set(a) | set(b)) / (n * n)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def _read(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def read_sheet(path: Path, audit_ids: list[str]) -> dict[str, str]:
    rows = _read(path)
    labels, problems = {}, []
    for row in rows:
        identifier = (row.get("audit_id") or "").strip()
        label = (row.get("human_label") or "").strip().upper()
        if identifier in labels:
            problems.append(f"duplicate {identifier}")
        elif label not in LABELS:
            problems.append(f"{identifier or '?'}: {'blank' if not label else 'unknown label ' + label}")
        labels[identifier] = label
    missing, extra = sorted(set(audit_ids) - set(labels)), sorted(set(labels) - set(audit_ids))
    problems += [f"missing {i}" for i in missing] + [f"not in the key {i}" for i in extra]
    if problems:
        raise ValueError(f"{Path(path).name}: " + "; ".join(problems[:10])
                         + (f" (+{len(problems) - 10} more)" if len(problems) > 10 else ""))
    return labels


def score_audit(audit_dir: Path, sheets: list[Path]) -> dict:
    audit_dir = Path(audit_dir)
    key = _read(audit_dir / "audit_key_PRIVATE.csv")
    meta = json.loads((audit_dir / "audit_meta.json").read_text(encoding="utf-8"))
    ids = [row["audit_id"] for row in key]
    judge = [row["judge_label"] for row in key]
    raters = {Path(p).stem: read_sheet(p, ids) for p in sheets}
    if len(raters) != len(sheets):
        raise ValueError("each rater's sheet needs a distinct file name")
    result = {"n_items": len(ids), "threshold": meta["threshold"], "raters": {}, "between_raters": {}}
    for name, labels in raters.items():
        human = [labels[i] for i in ids]
        by_stratum = defaultdict(list)
        for row, h in zip(key, human):
            by_stratum[f"{row['condition_type']}/{row['layer']}"].append(h == row["judge_label"])
        confusion = Counter(f"{j} -> {h}" for j, h in zip(judge, human) if j != h)
        kappa = cohen_kappa(judge, human)
        result["raters"][name] = {
            "kappa_vs_judge": kappa, "agreement": sum(j == h for j, h in zip(judge, human)) / len(ids),
            "agreement_by_stratum": {s: sum(v) / len(v) for s, v in sorted(by_stratum.items())},
            "disagreements": dict(confusion.most_common()),
            "meets_threshold": kappa is not None and kappa >= meta["threshold"]}
    names = sorted(raters)
    for index, a in enumerate(names):
        for b in names[index + 1:]:
            result["between_raters"][f"{a} vs {b}"] = cohen_kappa([raters[a][i] for i in ids],
                                                                  [raters[b][i] for i in ids])
    result["judge_meets_threshold"] = bool(raters) and all(r["meets_threshold"] for r in result["raters"].values())
    return result
