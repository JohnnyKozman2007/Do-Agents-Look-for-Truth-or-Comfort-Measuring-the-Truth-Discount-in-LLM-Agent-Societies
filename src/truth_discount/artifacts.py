"""Persist, audit and replay synthetic pilot bundles."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from typing import Any

from .config import build_manifest, load_config, render_template, render_values
from .contracts import canonical_bytes, digest
from .scoring import make_judge_input, paired_metrics, parse_judge_response, town_metrics


class InvalidBundle(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidBundle(message)


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_bytes(b"".join(canonical_bytes(r) + b"\n" for r in rows))


def _score_csv(town: dict[str, Any], config: dict[str, Any]) -> str:
    stream = io.StringIO(newline="")
    fields = ["run_id", "pair_id", "model_key", "cell_id", "condition_type", "seat_id", "layer",
              "status", "label", "belief", "quote", "evidence_kind", "study_eligible"]
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    evaluations = {x["seat_id"]: x for x in town["judge_evaluations"]}
    for seat in range(1, 13):
        e = evaluations.get(seat, {})
        label = e.get("label") if e.get("status") == "valid" else None
        writer.writerow({**{k: town[k] for k in ["run_id", "pair_id", "model_key", "cell_id", "condition_type"]},
                         "seat_id": seat, "layer": "first_hand" if seat <= 6 else "second_hand",
                         "status": e.get("status", "not_observed"), "label": label,
                         "belief": config["judging_and_scoring"]["belief_numerical_mapping"].get(label),
                         "quote": e.get("quote"), "evidence_kind": "synthetic_fixture", "study_eligible": False})
    return stream.getvalue()


def _crosswalk(town: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"custom_id": x["custom_id"], "run_id": town["run_id"], "seat_id": x["seat_id_private"],
             "condition_type": town["condition_type"], "cell_id": town["cell_id"]}
            for x in town["judge_inputs"]]


def _transcript(town: dict[str, Any]) -> str:
    text = ["# Synthetic town trace", "", "Not empirical study data.", "", "## Cafe broadcast", "",
            town["scene_1_departure_broadcast_text"] or "Not observed."]
    for pair in town["scene_3_catch_up_transcripts"]:
        text.extend(["", f"## Catch-up seats {pair['first_hand_seat']} and {pair['second_hand_seat']}", ""])
        text.extend(f"{x['speaker']}: {x['text']}" for x in pair["lines"])
    for phone in town["scene_5_phone_transcripts"]:
        text.extend(["", f"## Phone call seat {phone['seat_id']}", ""])
        text.extend(f"{x['speaker']}: {x['text']}" for x in phone["lines"])
    return "\n".join(text) + "\n"


def save_town(directory: Path, town: dict[str, Any], config: dict[str, Any]) -> None:
    (directory / "town.json").write_bytes(canonical_bytes(town))
    (directory / "config.json").write_bytes(canonical_bytes(config))
    _write_rows(directory / "trace.jsonl", town["calls"])
    _write_rows(directory / "judge_requests.jsonl", [{"custom_id": x["custom_id"], **x["input"]}
                                                    for x in town["judge_inputs"]])
    _write_rows(directory / "judge_crosswalk_PRIVATE.jsonl", _crosswalk(town))
    (directory / "listener_scores.csv").write_bytes(_score_csv(town, config).encode("utf-8"))
    (directory / "transcript.md").write_text(_transcript(town), encoding="utf-8")
    files = [p for p in directory.iterdir() if p.is_file() and p.name != "manifest.json"]
    manifest = {"schema_version": "truth-discount-offline-0.1", "evidence_kind": "synthetic_fixture",
                "study_eligible": False, "runtime": {"python": sys.version.split()[0], "platform": sys.platform},
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},
                "source_files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in sorted(Path(__file__).parent.glob("*.py"))}}
    (directory / "manifest.json").write_bytes(canonical_bytes(manifest))


def audit_town(directory: Path) -> dict[str, Any]:
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    required = {"town.json", "config.json", "trace.jsonl", "judge_requests.jsonl",
                "judge_crosswalk_PRIVATE.jsonl", "listener_scores.csv", "transcript.md"}
    _require(set(manifest.get("files", {})) == required, "unexpected manifest files")
    _require(manifest.get("schema_version") == "truth-discount-offline-0.1", "unsupported schema")
    _require(manifest.get("evidence_kind") == "synthetic_fixture" and manifest.get("study_eligible") is False,
             "only non-study fixtures are supported")
    for name, value in manifest["files"].items():
        _require(hashlib.sha256((directory / name).read_bytes()).hexdigest() == value,
                 "file hash mismatch: " + name)
    town = json.loads((directory / "town.json").read_text())
    _require(town.get("schema_version") == manifest["schema_version"], "schema mismatch")
    _require(town.get("evidence_kind") == "synthetic_fixture" and town.get("study_eligible") is False,
             "fixture evidence markers missing")
    _require(town["run_id"] == directory.name, "run identifier mismatch")
    _require(town["token_usage"]["provider_api_calls"] == 0, "fixture claims provider calls")
    config = load_config(directory / "config.json")
    _require(digest(config) == town["config_sha256"], "configuration hash mismatch")
    expected_run = next((r for r in build_manifest(config, [town["model_key"]]) if r["run_id"] == town["run_id"]), None)
    _require(expected_run is not None, "run does not belong to the configured plan")
    for key, value in expected_run.items():
        _require(canonical_bytes(town.get(key)) == canonical_bytes(value), "run-plan mismatch: " + key)
    calls = [json.loads(x) for x in (directory / "trace.jsonl").read_text().splitlines()]
    _require(canonical_bytes(calls) == canonical_bytes(town["calls"]), "trace export mismatch")
    for call in calls:
        _require(digest(call["request"]) == call["request_sha256"], "request hash mismatch")
        _require(call["provider_api_calls"] == 0 and call["backend"] == "synthetic_fixture", "invalid call evidence")
        _require(call["status"] in {"completed", "cancelled", "timeout", "malformed_response", "callback_error"},
                 "call has no terminal status")
        _require(all(call.get(k) is None for k in ("actual_provider", "actual_model", "token_usage", "cost_usd")),
                 "fixture claims provider metadata")
        if call["status"] == "completed":
            _require(isinstance(call["response"], str), "completed call has no response text")
    _require(len({c["call_id"] for c in calls}) == len(calls), "duplicate call identity")
    _require(len({(c["scene"], c["seat_id"], c["kind"], c["turn"]) for c in calls}) == len(calls),
             "duplicate callback coordinates")
    _require(town["run_status"] != "completed" or all(c["status"] == "completed" for c in calls),
             "completed town contains failed callbacks")

    def completed(scene: int, seat: int, kind: str, turn: int | None = None) -> list[dict]:
        return [c for c in calls if c["scene"] == scene and c["seat_id"] == seat and c["kind"] == kind
                and c["status"] == "completed" and (turn is None or c["turn"] == turn)]

    source = completed(1, 0, "chat", 1)
    broadcast = source[0]["response"] if len(source) == 1 else None
    _require(town["scene_1_departure_broadcast_text"] == broadcast, "broadcast replay mismatch")
    fixed = render_template(config["prompts_and_templates"]["scene_1_source_departure_broadcast"],
                            render_values(config, town, 0))
    _require(town["source_exact_text_match"] == (broadcast == fixed if broadcast is not None else None),
             "broadcast adherence mismatch")

    from .runner import concert_mentioned, parse_check_decision
    decisions = town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]
    _require(sorted(c["seat_id"] for c in calls if c["kind"] == "decision" and c["status"] == "completed")
             == sorted(row["seat_id"] for row in decisions), "decision/callback coverage mismatch")
    for row in decisions:
        seat = row["seat_id"]
        observed = completed(2 if seat <= 6 else 4, seat, "decision", 1)
        _require(len(observed) == 1, "decision has no unique completed callback")
        parsed = parse_check_decision(observed[0]["response"])
        _require(all(row.get(k) == v for k, v in parsed.items()), "decision parser replay mismatch")
        expected_balance = config["meta"]["initial_budget_usd"]
        expected_observation = None
        if parsed["decision"] == "GO":
            expected_balance -= config["meta"]["check_bus_cost_usd"]
            expected_observation = render_template(config["prompts_and_templates"]["scene_2_and_4_memory_on_go"],
                                                   render_values(config, town, seat))
        _require(row["balance_usd"] == expected_balance and row["poster_observation"] == expected_observation,
                 "decision observation or budget mismatch")
        _require(town["final_budgets_usd"][str(seat)] == expected_balance, "final budget mismatch")
    catchup_coverage = []
    for pair in town["scene_3_catch_up_transcripts"]:
        for line in pair["lines"]:
            if not line["scripted"]:
                observed = completed(3, line["seat_id"], "chat", line["turn"])
                _require(len(observed) == 1 and observed[0]["response"] == line["text"],
                         "catch-up transcript replay mismatch")
                catchup_coverage.append((line["seat_id"], line["turn"]))
    _require(sorted(catchup_coverage) == sorted((c["seat_id"], c["turn"]) for c in calls
             if c["scene"] == 3 and c["kind"] == "chat" and c["status"] == "completed"),
             "catch-up callback coverage mismatch")
    exported_judges = [json.loads(x) for x in (directory / "judge_requests.jsonl").read_text().splitlines()]
    projected = [{"custom_id": x["custom_id"], **x["input"]} for x in town["judge_inputs"]]
    _require(canonical_bytes(exported_judges) == canonical_bytes(projected), "judge request export mismatch")
    phones = {x["seat_id"]: x["lines"] for x in town["scene_5_phone_transcripts"]}
    _require(len(phones) == len(town["scene_5_phone_transcripts"]), "duplicate phone transcript")
    phone_coverage = []
    completed_phone_seats = set()
    funnel = {int(x["step"]): x["loved_one_line"]
              for x in config["prompts_and_templates"]["scene_5_phone_call_funnel"]}
    for seat, lines in phones.items():
        values = render_values(config, town, seat)
        rebuilt = []
        reached_mention = None
        finished = True

        def phone_turn(step):
            rebuilt.append({"speaker": "caller", "name": values["loved_one"],
                            "text": funnel[step], "funnel_step": step})
            observed = completed(5, seat, "chat", step)
            if len(observed) != 1:
                return None
            rebuilt.append({"speaker": "listener", "name": values["name"],
                            "text": observed[0]["response"], "funnel_step": step})
            return observed[0]["response"]

        for step in range(1, 5):
            reply = phone_turn(step)
            if reply is None:
                finished = False
                break
            if concert_mentioned(reply, config["artists"]["artist_pool"]):
                reached_mention = step
                break
        if finished:
            _require(str(seat) in town["scene_5_funnel_step_mentioned"] and
                     town["scene_5_funnel_step_mentioned"][str(seat)] == reached_mention,
                     "phone mention step replay mismatch")
            if reached_mention is not None:
                finished = phone_turn(5) is not None
            if finished:
                rebuilt.append({"speaker": "caller", "name": values["loved_one"],
                                "text": funnel[6], "funnel_step": 6})
                completed_phone_seats.add(seat)
        _require(canonical_bytes(lines) == canonical_bytes(rebuilt), "phone funnel replay mismatch")
        for line in lines:
            if line["speaker"] == "listener":
                observed = completed(5, seat, "chat", line["funnel_step"])
                _require(len(observed) == 1 and observed[0]["response"] == line["text"],
                         "phone transcript replay mismatch")
                phone_coverage.append((seat, line["funnel_step"]))
    _require(sorted(phone_coverage) == sorted((c["seat_id"], c["turn"]) for c in calls
             if c["scene"] == 5 and c["kind"] == "chat" and c["status"] == "completed"),
             "phone callback coverage mismatch")
    _require(len({x["custom_id"] for x in town["judge_inputs"]}) == len(town["judge_inputs"]),
             "duplicate judge identity")
    _require(sorted(c["seat_id"] for c in calls if c["kind"] == "judge")
             == sorted(x["seat_id_private"] for x in town["judge_inputs"]), "judge/callback coverage mismatch")
    _require(sorted(c["seat_id"] for c in calls if c["kind"] == "judge" and c["status"] == "completed")
             == sorted(e["seat_id"] for e in town["judge_evaluations"]
                       if e["provenance"] == "synthetic_judge_callback"), "judgment/callback coverage mismatch")
    for item in town["judge_inputs"]:
        expected = make_judge_input(config, town["announced_artist"], phones[item["seat_id_private"]])
        _require(canonical_bytes(item["input"]) == canonical_bytes(expected), "blind judge input mismatch")
        _require(digest(expected) == item["input_sha256"], "judge input hash mismatch")
        actual_calls = [c for c in calls if c["kind"] == "judge" and c["seat_id"] == item["seat_id_private"]]
        _require(len(actual_calls) == 1, "judge request/call count mismatch")
        _require(actual_calls[0]["request"]["messages"] == expected["messages"], "judge prompt mismatch")
        _require(actual_calls[0]["request"]["settings"] == expected["settings"], "judge settings mismatch")
    for row in town["judge_evaluations"]:
        seat = row["seat_id"]
        _require(seat in completed_phone_seats, "unfinished phone cannot have a judgment")
        lines = phones[seat]
        if row["provenance"] == "runner_phone_funnel_rule":
            _require(not any(concert_mentioned(x["text"], config["artists"]["artist_pool"])
                             for x in lines if x["speaker"] == "listener"), "invented omission")
            _require(lines[-1]["speaker"] == "caller" and lines[-1]["funnel_step"] == 6,
                     "unfinished phone cannot be an omission")
            expected_label = {"status": "valid", "label": "NOT_MENTIONED", "quote": "", "error": None}
        else:
            _require(row["provenance"] == "synthetic_judge_callback", "unknown judge provenance")
            observed = completed(5, seat, "judge", 0)
            _require(len(observed) == 1, "judgment has no unique completed callback")
            expected_label = parse_judge_response(observed[0]["response"], lines)
        _require(all(row.get(k) == v for k, v in expected_label.items()), "judge parser replay mismatch")
    crosswalk = [json.loads(x) for x in (directory / "judge_crosswalk_PRIVATE.jsonl").read_text().splitlines()]
    _require(canonical_bytes(crosswalk) == canonical_bytes(_crosswalk(town)), "private crosswalk mismatch")
    _require((directory / "listener_scores.csv").read_bytes() == _score_csv(town, config).encode("utf-8"),
             "score CSV replay mismatch")
    _require((directory / "transcript.md").read_text(encoding="utf-8") == _transcript(town),
             "transcript export mismatch")
    expected_metrics = town_metrics(config, town["judge_evaluations"], decisions)
    _require(canonical_bytes(town["metrics"]) == canonical_bytes(expected_metrics), "metric replay mismatch")
    _require(town["token_usage"]["fixture_callback_invocations"] == len(calls), "callback count mismatch")
    return town


def summarize(output_root: Path) -> dict[str, Any]:
    paths = sorted(p.parent for p in Path(output_root).glob("*/manifest.json"))
    _require(bool(paths), "no saved towns found")
    towns = [audit_town(p) for p in paths]
    pairs = paired_metrics(towns)
    return {"evidence_kind": "synthetic_fixture", "study_results_generated": False,
            "provider_api_calls": 0, "towns": len(towns), "pairs": len(pairs),
            "completed_towns": sum(t["run_status"] == "completed" for t in towns),
            "fixture_callbacks": sum(len(t["calls"]) for t in towns),
            "judged_phone_inputs": sum(len(t["judge_inputs"]) for t in towns),
            "paired_fixture_metrics": pairs,
            "town_summaries": [{k: t[k] for k in ["run_id", "pair_id", "model_key", "condition_type", "metrics"]}
                               for t in towns]}
