"""Offline, source-bound calibration inventory covering every saved phone call.

This package is separate from audit-v1. It neither selects a replacement judge
nor changes saved labels, the primary analysis, collection prompts or spending.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import io
from pathlib import Path
import random

from .analysis import load_towns
from .contracts import canonical_bytes, clone, digest
from .scoring import make_judge_input

VERSION = "truth-discount-judge-calibration-1"
STRATA = [(condition, layer) for condition in ("rumor", "truth_twin")
          for layer in ("first_hand", "second_hand")]
HUMAN_FIELDS = ["validation_id", "target_artist", "transcript", "human_label", "notes"]


def _source_hashes(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("source collection must not contain symlinks")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _csv(rows: list[dict], fields: list[str]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows({field: row[field] for field in fields} for row in rows)
    return output.getvalue()


def _inventory(towns: list[dict], config: dict) -> list[dict]:
    first = set(config["seating_and_pairing"]["first_hand_seats"])
    expected = first | set(config["seating_and_pairing"]["second_hand_seats"])
    items = []
    for town in towns:
        phones = town["scene_5_phone_transcripts"]
        if len(phones) != 12 or {phone["seat_id"] for phone in phones} != expected:
            raise ValueError("completed town needs exactly 12 unique phone transcripts")
        evaluations = {row["seat_id"]: row for row in town["judge_evaluations"]}
        judged = {row["seat_id_private"]: row for row in town["judge_inputs"]}
        decisions = {row["seat_id"]: row for row in
                     town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]}
        for phone in sorted(phones, key=lambda row: row["seat_id"]):
            seat, lines = phone["seat_id"], phone["lines"]
            projected = [{"speaker": line["speaker"], "text": line["text"]} for line in lines]
            original = judged.get(seat)
            original_input = clone(original["input"]) if original else None
            if original and digest(original_input) != original["input_sha256"]:
                raise ValueError("recorded judge input hash differs from its content")
            request = original_input or make_judge_input(config, town["announced_artist"], lines)
            evaluation = clone(evaluations.get(seat, {}))
            provenance = evaluation.get("provenance")
            origin = ("rule" if provenance == "runner_phone_funnel_rule" else
                      "provider" if provenance == "provider_judge_callback" else
                      "fixture" if provenance in {"synthetic_judge_callback", "mocked_provider_judge_callback"}
                      else "missing")
            source_identity = {"run_id": town["run_id"], "seat_id": seat,
                               "target_artist": town["announced_artist"], "phone": lines}
            items.append({"validation_id": digest(source_identity),
                          "run_id": town["run_id"], "pair_id": town["pair_id"], "seat_id": seat,
                          "model_key": town["model_key"], "cell_id": town["cell_id"],
                          "condition_type": town["condition_type"],
                          "layer": "first_hand" if seat in first else "second_hand",
                          "target_artist": town["announced_artist"],
                          "transcript": "\n".join(f"{line['speaker']}: {line['text']}" for line in projected),
                          "phone_lines": clone(lines), "phone_sha256": digest(lines),
                          "shown_text_sha256": digest({"target_artist": town["announced_artist"],
                                                       "phone": projected}),
                          "original_evaluation": evaluation, "original_provenance_class": origin,
                          "original_recorded_judge_input": original_input,
                          "original_recorded_judge_input_sha256": digest(original_input) if original else None,
                          "judge_input": request, "judge_input_sha256": digest(request),
                          "judge_input_origin": "recorded" if original else "reconstructed_not_executed",
                          "verification_decision_PRIVATE": clone(decisions.get(seat)),
                          "config_sha256": town["config_sha256"],
                          "source_schema_version": town["schema_version"],
                          "trace_sha256": digest(town["calls"]),
                          "provider_manifest_sha256": town.get("execution_manifest_sha256")})
    if len({item["validation_id"] for item in items}) != len(items):
        raise ValueError("duplicate validation identity")
    return items


def prepare_validation(output_root: Path, destination: Path, size: int = 100,
                       seed: int = 20261108) -> dict:
    """Prepare blinded independent labels and private probability-sample metadata."""
    root, destination = Path(output_root).resolve(), Path(destination).resolve()
    if destination.exists():
        raise FileExistsError("refusing existing calibration directory")
    if destination.is_relative_to(root):
        raise ValueError("calibration destination must stay outside the source collection")
    if type(size) is not int or size < 4 or size % 4 or type(seed) is not int:
        raise ValueError("size must be a positive multiple of 4 and seed an integer")
    before = _source_hashes(root)
    towns, config, excluded = load_towns(root)
    inventory = _inventory(towns, config)
    pools = defaultdict(list)
    for item in inventory:
        pools[(item["condition_type"], item["layer"])].append(item)
    quota, rng, sample, strata = size // 4, random.Random(seed), [], {}
    for stratum in STRATA:
        population = sorted(pools[stratum], key=lambda item: item["validation_id"])
        if len(population) < quota:
            raise ValueError("insufficient calibration stratum " + "/".join(stratum))
        sample.extend(rng.sample(population, quota))
        strata["/".join(stratum)] = {"N_h": len(population), "n_h": quota,
                                    "inclusion_probability": quota / len(population),
                                    "inverse_probability_weight": len(population) / quota}
    rng.shuffle(sample)
    if _source_hashes(root) != before:
        raise ValueError("source collection changed during calibration preparation")
    public = {"version": VERSION, "status": "prepared", "evidence_kind": towns[0]["evidence_kind"],
              "study_eligible": False, "completed_towns": len(towns), "inventory_phone_calls": len(inventory),
              "sample_size": size, "seed": seed, "provider_api_calls": 0,
              "human_results_generated": False, "original_labels_changed": False,
              "primary_analysis_changed": False}
    private = {**public, "source_root_PRIVATE": str(root), "source_files_sha256": before,
               "source_inventory_sha256": digest(inventory), "strata": strata,
               "sampling": "fixed-seed simple random sampling without replacement within four declared strata",
               "excluded_towns": excluded, "original_rubric_sha256": digest(config["judging_and_scoring"]["canonical_judge_prompt"]),
               "ignored_rejudged_overlay_sha256": before.get("rejudged.jsonl"),
               "rejudged_overlays_used": False,
               "limitations": ["Calibration sample, not an automatic primary-judge replacement.",
                               "Reported checking in dialogue is separate from private GO/SKIP actions.",
                               "Dialogue content can reveal contextual clues despite removed experiment metadata.",
                               "Source equality is checked before and after package preparation."]}
    rubric = config["judging_and_scoring"]["canonical_judge_prompt"]
    instructions = ("# Independent labeling instructions\n\n"
                    "Use human_labeling.csv. Work independently and leave human_label blank until you label each row. "
                    "Read the full dialogue and use target_artist for {announced_artist} in the original rubric below. "
                    "Record one categorical label in human_label and any ambiguity in notes. "
                    "Do not infer actions or evidence that the dialogue does not report. "
                    "If the original rules leave a boundary unclear, note that ambiguity rather than invent a new precedence rule. "
                    "Do not edit validation_id, target_artist or transcript, or discuss labels before independent completion. "
                    "The original JSON response instructions are retained verbatim for reference; enter your answer in the CSV.\n\n"
                    "## Original rubric, verbatim\n\n" + rubric + "\n")
    human = [{**{field: item[field] for field in HUMAN_FIELDS[:3]}, "human_label": "", "notes": ""}
             for item in sample]
    sample_key = [{"validation_id": item["validation_id"],
                   "stratum_PRIVATE": item["condition_type"] + "/" + item["layer"],
                   "inclusion_probability": strata[item["condition_type"] + "/" + item["layer"]]["inclusion_probability"]}
                  for item in sample]
    payloads = {"human_labeling.csv": _csv(human, HUMAN_FIELDS).encode(),
                "labeling_instructions.md": instructions.encode(),
                "inventory_PRIVATE.jsonl": b"".join(canonical_bytes(item) + b"\n" for item in inventory),
                "sample_key_PRIVATE.csv": _csv(sample_key, ["validation_id", "stratum_PRIVATE", "inclusion_probability"]).encode(),
                "validation_meta.json": canonical_bytes(public),
                "validation_meta_PRIVATE.json": canonical_bytes(private)}
    destination.mkdir(parents=True, exist_ok=False)
    for name, content in payloads.items():
        (destination / name).write_bytes(content)
    if _source_hashes(root) != before:
        raise ValueError("source collection changed during calibration preparation; package is unsealed")
    manifest = {"version": VERSION, "source_before_after_equal": True,
                "source_files_sha256": before,
                "files_sha256": {name: hashlib.sha256(content).hexdigest() for name, content in payloads.items()}}
    (destination / "validation_manifest_PRIVATE.json").write_bytes(canonical_bytes(manifest))
    return public
