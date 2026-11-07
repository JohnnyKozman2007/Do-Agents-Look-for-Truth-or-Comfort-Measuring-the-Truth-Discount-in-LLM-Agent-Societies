"""Source-bound, blinded sampling and human/judge agreement diagnostics.

Give raters only the labeling sheet and instructions. The PRIVATE files bind
the sample to original raw-label bundles. Agreement is not human truth or
authorization to change the judge automatically.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import random

from .analysis import load_towns
from .contracts import digest
from .scoring import LABELS

STRATA = [(c, l) for c in ("rumor", "truth_twin") for l in ("first_hand", "second_hand")]
_MARKER = "\nPHONE CALL TRANSCRIPT:\n"
_SHEET_FIELDS = ["audit_id", "announced_artist", "transcript", "human_label", "notes"]
_KEY_FIELDS = ["audit_id", "source_id", "run_id", "seat_id", "model_key", "cell_id",
               "condition_type", "layer", "judge_label", "input_sha256",
               "judge_revision_sha256", "config_sha256", "provider_manifest_sha256",
               "trace_sha256", "shown_sha256"]
_IMMUTABLE_FILES = ("labeling_sheet.csv", "audit_key_PRIVATE.csv", "audit_meta.json",
                    "audit_meta_PRIVATE.json", "labeling_instructions.md")
_VERSION = "truth-discount-human-audit-1"


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def judged_calls(towns: list[dict], config: dict) -> list[dict]:
    """Valid original judge labels, exact shown lines and private provenance."""
    first = set(config["seating_and_pairing"]["first_hand_seats"])
    items = []
    for town in towns:
        evaluations = {e["seat_id"]: e for e in town["judge_evaluations"]}
        trace_sha256 = digest(town["calls"])
        for judged in town["judge_inputs"]:
            seat = judged["seat_id_private"]
            evaluation = evaluations.get(seat, {})
            if evaluation.get("status") != "valid":
                continue
            if evaluation.get("label") not in LABELS:
                raise ValueError("valid judgment has an unknown label")
            content = judged["input"]["messages"][0]["content"]
            if not isinstance(content, str) or _MARKER not in content:
                raise ValueError("judge input has no phone-call transcript")
            lines = json.loads(content.split(_MARKER, 1)[1])
            if (not isinstance(lines, list) or not lines
                    or any(not isinstance(line, dict) or line.get("speaker") not in {"caller", "listener"}
                           or not isinstance(line.get("text"), str) for line in lines)):
                raise ValueError("invalid phone-call transcript")
            calls = [call for call in town["calls"] if call["kind"] == "judge" and call["seat_id"] == seat]
            if len(calls) != 1:
                raise ValueError("audit needs one recorded judge callback per sampled listener")
            item = {"run_id": town["run_id"], "seat_id": seat, "model_key": town["model_key"],
                    "cell_id": town["cell_id"], "condition_type": town["condition_type"],
                    "layer": "first_hand" if seat in first else "second_hand",
                    "judge_label": evaluation["label"], "announced_artist": town["announced_artist"],
                    "transcript": "\n".join(f"{line['speaker']}: {line['text']}" for line in lines),
                    "input_sha256": digest(judged["input"]),
                    "judge_revision_sha256": digest({"call": calls[0], "evaluation": evaluation}),
                    "config_sha256": town["config_sha256"],
                    "provider_manifest_sha256": town.get("execution_manifest_sha256"),
                    "trace_sha256": trace_sha256}
            item["shown_sha256"] = digest({key: item[key] for key in ("announced_artist", "transcript")})
            item["source_id"] = digest({key: item[key] for key in
                                       ("run_id", "seat_id", "input_sha256", "judge_revision_sha256",
                                        "config_sha256", "provider_manifest_sha256", "trace_sha256")})
            items.append(item)
    return sorted(items, key=lambda item: (item["run_id"], item["seat_id"]))


def stratified_sample(items: list[dict], size: int, seed: int) -> tuple[list[dict], dict]:
    """Take declared quotas without silently redistributing short strata."""
    if type(size) is not int or size < 1 or type(seed) is not int:
        raise ValueError("sample size must be a positive integer and seed an integer")
    if len(items) < size:
        raise ValueError(f"only {len(items)} judged phone calls are available for a sample of {size}")
    identities = [(item["run_id"], item["seat_id"]) for item in items]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate source identity in audit pool")
    if any((item["condition_type"], item["layer"]) not in STRATA for item in items):
        raise ValueError("unknown audit stratum")
    rng = random.Random(seed)
    ordered = sorted(items, key=lambda item: (item["run_id"], item["seat_id"]))
    pools = {s: [item for item in ordered if (item["condition_type"], item["layer"]) == s] for s in STRATA}
    quota = {s: size // len(STRATA) + int(i < size % len(STRATA)) for i, s in enumerate(STRATA)}
    shortages = [f"{c}/{l}: need {quota[(c, l)]}, available {len(pools[(c, l)])}"
                 for c, l in STRATA if len(pools[(c, l)]) < quota[(c, l)]]
    if shortages:
        raise ValueError("insufficient audit strata; retain the declared quotas: " + "; ".join(shortages))
    picked = {s: rng.sample(pools[s], quota[s]) for s in STRATA}
    sample = [dict(item) for s in STRATA for item in picked[s]]
    rng.shuffle(sample)
    return sample, {f"{c}/{l}": len(picked[(c, l)]) for c, l in STRATA}


def _csv(rows: list[dict], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows({key: row[key] for key in fields} for row in rows)
    return stream.getvalue()


def _selected(items: list[dict], size: int, seed: int) -> tuple[list[dict], dict]:
    sample, counts = stratified_sample(items, size, seed)
    for number, item in enumerate(sample, start=1):
        item.update(audit_id=f"A{number:03d}", human_label="", notes="")
    return sample, counts


def _inventory(output_root: Path, towns: list[dict]) -> dict:
    return {town["run_id"]: {path.name: _file_hash(path)
                             for path in sorted((output_root / town["run_id"]).iterdir()) if path.is_file()}
            for town in towns}


def _overlay_metadata(output_root: Path) -> dict:
    candidates = [output_root / "rejudged.jsonl", *output_root.glob("*/rejudged.jsonl")]
    result = {}
    for path in sorted(candidates):
        if path.exists():
            if not path.is_file():
                raise ValueError("rejudge overlay path is not a file")
            result[path.relative_to(output_root).as_posix()] = {
                "sha256": _file_hash(path), "lines": len(path.read_bytes().splitlines()),
                "canonical_location": path.parent == output_root}
    return result


def _public_metadata(config: dict, size: int, seed: int) -> dict:
    protocol = config["judging_and_scoring"]["human_audit_protocol"]
    target = protocol["target_threshold"]
    if type(target) not in (int, float) or not math.isfinite(target) or not 0 <= target <= 1:
        raise ValueError("invalid kappa target")
    return {"audit_version": _VERSION, "size": size, "seed": seed, "threshold": target,
            "protocol_sample_size": protocol["sample_size"],
            "protocol_size_met": size == protocol["sample_size"],
            "purpose": "Human/judge label agreement, not a gold-truth or automatic model-selection result"}


def _pool_diagnostics(towns: list[dict], items: list[dict], excluded: dict) -> dict:
    return {"judged_calls_available": len(items),
            "judge_inputs_excluded_invalid_or_missing": sum(len(t["judge_inputs"]) for t in towns) - len(items),
            "rule_labeled_phone_calls_excluded": sum(len(t["scene_5_phone_transcripts"]) - len(t["judge_inputs"]) for t in towns),
            "excluded_towns": excluded, "label_view": "original_raw_judge_labels", "overlays_used": False}


def _instructions(config: dict) -> str:
    rubric = config["judging_and_scoring"]["canonical_judge_prompt"].replace(
        "{announced_artist}", "the sheet's announced artist").split("REPLY STRICTLY AS JSON:")[0].rstrip()
    return ("# Labeling instructions\n\nShare only this file and labeling_sheet.csv with raters. "
            "Keep every PRIVATE file, the source outputs and other raters' labels separate. "
            "Work independently. Read each transcript and write one label in human_label. "
            "Do not alter audit_id, announced_artist or transcript. Save a separate copy for each rater.\n\n"
            + rubric + "\n")


def make_audit(output_root: Path, destination: Path, *, size: int = 100, seed: int = 2027) -> dict:
    output_root, destination = Path(output_root).resolve(), Path(destination)
    if destination.exists():
        raise FileExistsError("refusing existing human-audit directory")
    if destination.resolve().is_relative_to(output_root):
        raise ValueError("audit destination must stay outside the original source collection")
    towns, config, excluded = load_towns(output_root)
    items = judged_calls(towns, config)
    sample, counts = _selected(items, size, seed)
    public = _public_metadata(config, size, seed)
    private = {**public, "source_root_PRIVATE": str(output_root), "strata": counts,
               "config_sha256": towns[0]["config_sha256"], "evidence_kind": towns[0]["evidence_kind"],
               "source_files_sha256": _inventory(output_root, towns),
               "pool_sha256": digest(items), "sample_source_ids": [item["source_id"] for item in sample],
               **_pool_diagnostics(towns, items, excluded),
               "rejudged_overlays_present": list(_overlay_metadata(output_root)),
               "rejudged_overlay_files_PRIVATE": _overlay_metadata(output_root),
               "sampling_limit": "Agreement is conditional on completed towns and valid original LLM judge labels. Invalid/missing judge labels and rule-coded omissions without an LLM judge call are excluded explicitly.",
               "blinding_limit": "The sheet removes experiment metadata and automated labels; dialogue content can still reveal contextual clues."}
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "labeling_sheet.csv").write_text(_csv(sample, _SHEET_FIELDS), encoding="utf-8", newline="")
    (destination / "audit_key_PRIVATE.csv").write_text(_csv(sample, _KEY_FIELDS), encoding="utf-8", newline="")
    for name, value in (("audit_meta.json", public), ("audit_meta_PRIVATE.json", private)):
        (destination / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    (destination / "labeling_instructions.md").write_text(_instructions(config), encoding="utf-8", newline="")
    manifest = {"audit_version": _VERSION,
                "files_sha256": {name: _file_hash(destination / name) for name in _IMMUTABLE_FILES}}
    (destination / "audit_manifest_PRIVATE.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return public


def cohen_kappa(first: list[str], second: list[str]) -> float | None:
    """Unweighted agreement; None when the two marginals imply chance agreement 1."""
    n = len(first)
    if n == 0 or n != len(second) or any(not isinstance(x, str) or not x for x in first + second):
        raise ValueError("kappa needs two equal, nonempty label lists")
    observed = sum(a == b for a, b in zip(first, second)) / n
    a, b = Counter(first), Counter(second)
    expected = sum(a[label] * b[label] for label in set(a) | set(b)) / (n * n)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def _read(path: Path, fields: list[str]) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != fields:
            raise ValueError(f"{Path(path).name}: CSV columns differ from the original sheet")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f"{Path(path).name}: malformed CSV row")
        return rows


def read_sheet(path: Path, audit_ids: list[str], originals: dict[str, dict] | None = None) -> dict[str, str]:
    rows = _read(path, _SHEET_FIELDS)
    labels, problems = {}, []
    for row in rows:
        identifier = row["audit_id"].strip()
        label = row["human_label"].strip().upper()
        if identifier in labels:
            problems.append(f"duplicate {identifier}")
        if label not in LABELS:
            problems.append(f"{identifier or '?'}: {'blank' if not label else 'unknown label ' + label}")
        if originals is not None and identifier in originals:
            if any(row[key] != originals[identifier][key] for key in ("announced_artist", "transcript")):
                problems.append(f"{identifier}: original artist/transcript changed")
        labels[identifier] = label
    problems += [f"missing {i}" for i in sorted(set(audit_ids) - set(labels))]
    problems += [f"not in the key {i}" for i in sorted(set(labels) - set(audit_ids))]
    if problems:
        raise ValueError(f"{Path(path).name}: " + "; ".join(problems[:10])
                         + (f" (+{len(problems) - 10} more)" if len(problems) > 10 else ""))
    return labels


def _verify_audit(audit_dir: Path) -> tuple[list[dict], dict, dict]:
    manifest = json.loads((audit_dir / "audit_manifest_PRIVATE.json").read_text(encoding="utf-8"))
    if manifest.get("audit_version") != _VERSION or set(manifest.get("files_sha256", {})) != set(_IMMUTABLE_FILES):
        raise ValueError("invalid immutable audit manifest")
    if any(_file_hash(audit_dir / name) != value for name, value in manifest["files_sha256"].items()):
        raise ValueError("original audit package changed")
    meta = json.loads((audit_dir / "audit_meta_PRIVATE.json").read_text(encoding="utf-8"))
    public = json.loads((audit_dir / "audit_meta.json").read_text(encoding="utf-8"))
    if any(meta.get(key) != value for key, value in public.items()):
        raise ValueError("audit public/private metadata differs")
    source = Path(meta["source_root_PRIVATE"])
    towns, config, excluded = load_towns(source)
    if _inventory(source, towns) != meta["source_files_sha256"]:
        raise ValueError("original source bundles changed since audit sampling")
    if _overlay_metadata(source) != meta["rejudged_overlay_files_PRIVATE"]:
        raise ValueError("rejudge overlay provenance changed since audit sampling")
    items = judged_calls(towns, config)
    if digest(items) != meta["pool_sha256"]:
        raise ValueError("original audit population changed")
    expected_public = _public_metadata(config, meta["size"], meta["seed"])
    if digest(public) != digest(expected_public) or any(digest(meta.get(key)) != digest(value)
                                                       for key, value in expected_public.items()):
        raise ValueError("audit protocol metadata differs from the bound source configuration")
    if any(digest(meta.get(key)) != digest(value)
           for key, value in _pool_diagnostics(towns, items, excluded).items()):
        raise ValueError("audit population diagnostics differ from the bound source selection")
    if (audit_dir / "labeling_instructions.md").read_bytes() != _instructions(config).encode("utf-8"):
        raise ValueError("labeling instructions differ from the bound source rubric")
    sample, counts = _selected(items, meta["size"], meta["seed"])
    if (counts != meta["strata"] or [item["source_id"] for item in sample] != meta["sample_source_ids"]
            or meta["config_sha256"] != towns[0]["config_sha256"]
            or meta["evidence_kind"] != towns[0]["evidence_kind"]
            or meta["threshold"] != config["judging_and_scoring"]["human_audit_protocol"]["target_threshold"]
            or meta["excluded_towns"] != excluded):
        raise ValueError("audit sample differs from its original source selection")
    if (audit_dir / "audit_key_PRIVATE.csv").read_bytes() != _csv(sample, _KEY_FIELDS).encode("utf-8"):
        raise ValueError("private audit key differs from the original source sample")
    original = _read(audit_dir / "labeling_sheet.csv", _SHEET_FIELDS)
    expected = list(csv.DictReader(io.StringIO(_csv(sample, _SHEET_FIELDS))))
    if original != expected:
        raise ValueError("original blind sheet differs from source sample")
    return _read(audit_dir / "audit_key_PRIVATE.csv", _KEY_FIELDS), meta, {row["audit_id"]: row for row in original}


def score_audit(audit_dir: Path, sheets: list[Path]) -> dict:
    if not sheets:
        raise ValueError("provide at least one completed rater sheet")
    names = [Path(path).stem for path in sheets]
    if len(set(names)) != len(names):
        raise ValueError("each rater's sheet needs a distinct file name")
    key, meta, originals = _verify_audit(Path(audit_dir))
    ids = [row["audit_id"] for row in key]
    if len(set(ids)) != len(ids) or len(ids) != meta["size"]:
        raise ValueError("invalid duplicate or missing audit identity")
    judge = [row["judge_label"] for row in key]
    if any(label not in LABELS for label in judge):
        raise ValueError("private key has an invalid judge label")
    raters = {name: read_sheet(path, ids, originals) for name, path in zip(names, sheets)}
    result = {"n_items": len(ids), "threshold": meta["threshold"], "raters": {}, "between_raters": {},
              "metric": "unweighted Cohen's kappa", "protocol_size_met": meta["protocol_size_met"],
              "evidence_kind": meta["evidence_kind"], "source_binding_verified": True,
              "strata": meta["strata"], "judge_inputs_excluded_invalid_or_missing": meta["judge_inputs_excluded_invalid_or_missing"],
              "rule_labeled_phone_calls_excluded": meta["rule_labeled_phone_calls_excluded"],
              "label_view": meta["label_view"], "overlays_used": False,
              "rater_independence_verified": False, "human_ground_truth_established": False,
              "automatic_model_change_authorized": False,
              "interpretation": "Agreement of each rater with the recorded automated judge, conditional on the fixed valid-label sample."}
    for name, labels in raters.items():
        human = [labels[identifier] for identifier in ids]
        by_stratum = defaultdict(list)
        for row, value in zip(key, human):
            by_stratum[f"{row['condition_type']}/{row['layer']}"].append(value == row["judge_label"])
        confusion = Counter(f"{j} -> {h}" for j, h in zip(judge, human) if j != h)
        kappa = cohen_kappa(judge, human)
        result["raters"][name] = {
            "kappa_vs_judge": kappa, "agreement": sum(j == h for j, h in zip(judge, human)) / len(ids),
            "kappa_status": "undefined_degenerate_marginals" if kappa is None else "defined",
            "agreement_by_stratum": {s: sum(v) / len(v) for s, v in sorted(by_stratum.items())},
            "n_by_stratum": {s: len(v) for s, v in sorted(by_stratum.items())},
            "disagreements": dict(confusion.most_common()),
            "meets_threshold": kappa is not None and kappa >= meta["threshold"]}
    for index, first in enumerate(names):
        for second in names[index + 1:]:
            result["between_raters"][f"{first} vs {second}"] = cohen_kappa(
                [raters[first][identifier] for identifier in ids], [raters[second][identifier] for identifier in ids])
    result["judge_meets_threshold"] = all(rater["meets_threshold"] for rater in result["raters"].values())
    result["protocol_audit_target_met"] = meta["protocol_size_met"] and result["judge_meets_threshold"]
    return result
