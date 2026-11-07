"""Persist and replay versioned fixtures and non-study development bundles."""

from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlsplit

from .config import build_manifest, load_config, render_template, render_values
from .contracts import canonical_bytes, digest
from .scoring import make_judge_input, paired_metrics, parse_judge_response, town_metrics


class InvalidBundle(ValueError):
    pass


LEGACY_SCHEMA = "truth-discount-offline-0.1"
CURRENT_SCHEMA = "truth-discount-0.2"
EVIDENCE_KINDS = {"synthetic_fixture", "mocked_provider", "development_pilot"}
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_USAGE_COUNTERS = ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")


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
                         "quote": e.get("quote"), "evidence_kind": town["evidence_kind"],
                         "study_eligible": town["study_eligible"]})
    return stream.getvalue()


def _crosswalk(town: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"custom_id": x["custom_id"], "run_id": town["run_id"], "seat_id": x["seat_id_private"],
             "condition_type": town["condition_type"], "cell_id": town["cell_id"]}
            for x in town["judge_inputs"]]


def _transcript(town: dict[str, Any]) -> str:
    heading = {"synthetic_fixture": "# Synthetic town trace",
               "mocked_provider": "# Mocked provider town trace",
               "development_pilot": "# Development pilot town trace"}[town["evidence_kind"]]
    notice = ("Not empirical study data." if town["evidence_kind"] == "synthetic_fixture" else
              "Mocked provider responses only. No actual provider calls or study-eligible data."
              if town["evidence_kind"] == "mocked_provider" else
              "Development pilot only. Not study-eligible data.")
    text = [heading, "", notice, "", "## Cafe broadcast", "",
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
    manifest = {"schema_version": town["schema_version"], "evidence_kind": town["evidence_kind"],
                "study_eligible": town["study_eligible"],
                "runtime": {"python": sys.version.split()[0], "platform": sys.platform},
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},
                "source_files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in sorted(Path(__file__).parent.glob("*.py"))}}
    (directory / "manifest.json").write_bytes(canonical_bytes(manifest))


def _hash(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _optional_number(value: Any, *, integer: bool = False) -> bool:
    return value is None or (type(value) in ((int,) if integer else (int, float))
                             and value >= 0 and math.isfinite(value))


def _execution_manifest(town: dict[str, Any]) -> dict[str, Any] | None:
    if town["evidence_kind"] == "synthetic_fixture":
        _require(town.get("execution_manifest") is None and town.get("execution_manifest_sha256") is None,
                 "fixture must not claim a provider execution manifest")
        return None
    execution = town.get("execution_manifest")
    _require(isinstance(execution, dict) and digest(execution) == town.get("execution_manifest_sha256"),
             "execution manifest hash mismatch")
    _require(execution.get("version") == 1 and type(execution.get("approved")) is bool,
             "invalid execution manifest version or approval")
    routes = execution.get("routes")
    _require(isinstance(routes, dict) and bool(routes), "execution manifest has no routes")

    def no_secrets(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                _require(key.lower() not in {"api_key", "authorization", "access_token", "secret", "password"},
                         "execution manifest contains a secret field")
                no_secrets(child)
        elif isinstance(value, list):
            for child in value:
                no_secrets(child)

    no_secrets(execution)
    for route in routes.values():
        _require(isinstance(route, dict), "invalid execution route")
        _require(all(isinstance(route.get(k), str) and route[k] for k in ("provider", "model_id", "endpoint")),
                 "execution route identity missing")
        endpoint = urlsplit(route["endpoint"])
        _require(endpoint.scheme == "https" and bool(endpoint.hostname) and endpoint.username is None
                 and endpoint.password is None and not endpoint.query and not endpoint.fragment,
                 "execution endpoint must not contain credentials or query data")
        _require(isinstance(route.get("api_key_env"), str)
                 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", route["api_key_env"]) is not None,
                 "execution route must name a key environment variable")
        if town["evidence_kind"] == "development_pilot":
            _require(execution["approved"] is True and route.get("settings_verified") is True
                     and route.get("pricing_verified") is True,
                     "development execution lacks approved verified settings/pricing")
    return execution


def _raw_response(call: dict[str, Any]) -> dict[str, Any] | None:
    raw = call.get("raw_response")
    if raw is None:
        _require(call["status"] != "completed", "completed call lacks raw response")
        return None
    _require(isinstance(raw, dict) and isinstance(raw.get("text"), str)
             and type(raw.get("truncated")) is bool and _hash(raw.get("sha256")),
             "invalid raw response capture")
    if raw["truncated"]:
        # A prefix cannot authenticate its missing suffix or reconstruct usage.
        _require(call["status"] != "completed", "completed raw response is truncated")
        return None
    _require(hashlib.sha256(raw["text"].encode()).hexdigest() == raw["sha256"],
             "raw response hash mismatch")
    decoded = json.loads(raw["text"])
    if call["status"] == "completed":
        _require(isinstance(decoded, dict) and decoded.get("text") == call["response"],
                 "raw response text mismatch")
    return decoded if isinstance(decoded, dict) else None


def _provider_receipt(call: dict[str, Any], execution: dict[str, Any]) -> None:
    receipt = call.get("token_usage")
    _require(receipt is None or isinstance(receipt, dict), "invalid provider usage receipt")
    raw = _raw_response(call)
    if call["status"] == "completed":
        _require(raw is not None and "usage" in raw, "raw response usage missing")
    # A paid response can fail text validation after its receipt was recorded.
    # Its captured usage remains authoritative even when the call is malformed.
    if raw is not None and "usage" in raw:
        _require(canonical_bytes(raw["usage"]) == canonical_bytes(receipt),
                 "raw response usage mismatch")
    if "provider_receipt" in call:
        _require(canonical_bytes(call["provider_receipt"]) == canonical_bytes(receipt),
                 "failure receipt mismatch")
    route = execution["routes"].get(call["model_key"])
    if receipt is None:
        _require(call["status"] != "completed", "completed provider call lacks receipt")
        _require(call["provider_api_calls"] == 0 and all(call.get(k) is None
                 for k in ("actual_provider", "actual_model", "cost_usd")),
                 "unobserved provider call invents metadata")
        return
    required = {"actual_provider", "actual_model", "request_id", "provider_api_calls",
                *_USAGE_COUNTERS, "cost_usd", "cost_status", "attempts", "pricing_sha256"}
    _require(required <= set(receipt), "provider receipt fields missing")
    _require(type(receipt["provider_api_calls"]) is int and receipt["provider_api_calls"] >= 0,
             "invalid provider request count")
    _require(all(_optional_number(receipt[k], integer=True) for k in _USAGE_COUNTERS),
             "invalid provider token usage")
    _require(_optional_number(receipt["cost_usd"]), "invalid provider cost")
    _require(receipt["cost_status"] in {"calculated_from_usage", "unknown", "not_submitted"},
             "invalid provider cost status")
    _require(receipt["request_id"] is None or isinstance(receipt["request_id"], str),
             "invalid provider request identity")
    _require(isinstance(receipt["attempts"], list)
             and all(isinstance(a, dict) for a in receipt["attempts"]), "invalid provider attempts")
    attempts = receipt["attempts"]
    _require(len(attempts) == receipt["provider_api_calls"], "provider attempt count mismatch")
    _require(all(type(a.get("attempt_index")) is int and a["attempt_index"] >= 0
                 and a.get("status") in {"completed", "failed", "cancelled"} for a in attempts)
             and len({a["attempt_index"] for a in attempts}) == len(attempts),
             "invalid terminal provider attempt")
    for key in ("actual_provider", "actual_model", "provider_api_calls", "cost_usd"):
        _require(canonical_bytes(call.get(key)) == canonical_bytes(receipt[key]),
                 "provider receipt projection mismatch: " + key)
    if receipt["provider_api_calls"] == 0:
        _require(call["status"] != "completed" and receipt["cost_status"] == "not_submitted"
                 and receipt["cost_usd"] in (None, 0)
                 and all(receipt[k] in (None, 0) for k in _USAGE_COUNTERS),
                 "zero-submission failure invents usage")
        _require(receipt["pricing_sha256"] is None or _hash(receipt["pricing_sha256"]),
                 "invalid unsubmitted pricing hash")
        return
    _require(isinstance(route, dict), "call has no execution route")
    pricing = {key: route.get(key) for key in ("input_usd_per_million", "output_usd_per_million",
                                             "cached_input_usd_per_million")}
    _require(all(_optional_number(v) and v is not None for v in pricing.values()),
             "execution pricing missing or invalid")
    _require(receipt["pricing_sha256"] == digest(pricing), "provider pricing hash mismatch")
    _require(receipt.get("execution_mode") in {"synchronous", "synchronous_override"},
             "provider execution mode missing")
    expected_mode = "synchronous_override" if call["request"]["settings"].get("use_batch_api") else "synchronous"
    _require(receipt["execution_mode"] == expected_mode, "provider execution mode mismatch")
    if expected_mode == "synchronous_override":
        _require(call["kind"] == "judge" and route.get("allow_synchronous_judge") is True,
                 "synchronous judge override lacks approval")
    _require(receipt["actual_provider"] == route["provider"], "actual provider does not match execution route")
    _require(receipt["actual_model"] is None or isinstance(receipt["actual_model"], str),
             "invalid actual model")
    if call["status"] == "completed":
        _require(receipt["actual_model"] in [route["model_id"], *route.get("accepted_model_ids", [])],
                 "completed provider receipt lacks observed identity/request")
    if receipt["cached_input_tokens"] is not None and receipt["input_tokens"] is not None:
        _require(receipt["cached_input_tokens"] <= receipt["input_tokens"], "cached usage exceeds input")
    if receipt["reasoning_tokens"] is not None and receipt["output_tokens"] is not None:
        _require(receipt["reasoning_tokens"] <= receipt["output_tokens"], "reasoning usage exceeds output")
    if receipt["cost_status"] == "calculated_from_usage":
        _require(all(receipt[k] is not None for k in ("input_tokens", "output_tokens", "cached_input_tokens"))
                 and receipt.get("cache_creation_input_tokens", 0) == 0,
                 "calculated cost lacks priced usage")
        uncached = receipt["input_tokens"] - receipt["cached_input_tokens"]
        expected_cost = float((Decimal(uncached) * Decimal(str(pricing["input_usd_per_million"]))
                               + Decimal(receipt["cached_input_tokens"]) * Decimal(str(pricing["cached_input_usd_per_million"]))
                               + Decimal(receipt["output_tokens"]) * Decimal(str(pricing["output_usd_per_million"])))
                              / Decimal(1_000_000))
        _require(receipt["cost_usd"] == expected_cost, "provider usage-derived cost mismatch")
    else:
        _require(receipt["cost_status"] == "unknown" and receipt["cost_usd"] is None,
                 "unobserved provider cost must remain unknown")


def _known_sum(receipts: list[dict[str, Any] | None], key: str) -> int | float | None:
    values = [r.get(key) if r is not None else None for r in receipts]
    if any(v is None for v in values):
        return None
    result = sum((Decimal(str(v)) for v in values), Decimal(0))
    return float(result) if key == "cost_usd" else int(result)


def _aggregate_usage(town: dict[str, Any]) -> None:
    calls, usage, kind = town["calls"], town["token_usage"], town["evidence_kind"]
    _require(isinstance(usage, dict), "town token usage missing")
    if kind == "synthetic_fixture":
        _require(usage.get("provider_api_calls") == 0, "fixture claims provider calls")
        _require(usage.get("fixture_callback_invocations") == len(calls), "callback count mismatch")
        _require(all(usage.get(k) is None for k in (*_USAGE_COUNTERS, "cost_usd")),
                 "fixture claims billed usage")
        _require(usage.get("simulated_provider_requests", 0) == 0
                 and usage.get("provider_request_attempts", 0) == 0, "fixture claims provider attempts")
        return
    receipts = [c.get("token_usage") for c in calls]
    requests = sum(c["provider_api_calls"] for c in calls)
    _require(usage.get("provider_api_calls") == (requests if kind == "development_pilot" else 0),
             "actual provider call total mismatch")
    _require(usage.get("simulated_provider_requests", 0) == (requests if kind == "mocked_provider" else 0),
             "simulated provider request total mismatch")
    _require(usage.get("fixture_callback_invocations", 0) == 0, "provider bundle claims fixture callbacks")
    _require(usage.get("provider_request_attempts") == requests,
             "provider attempt total mismatch")
    for key in ("input_tokens", "output_tokens", "cost_usd"):
        _require(canonical_bytes(usage.get(key)) == canonical_bytes(_known_sum(receipts, key)),
                 "provider usage aggregate mismatch: " + key)


def audit_town(directory: Path) -> dict[str, Any]:
    try:
        return _audit_town(Path(directory))
    except InvalidBundle:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise InvalidBundle(f"invalid saved town: {type(exc).__name__}: {exc}") from exc


def _audit_town(directory: Path) -> dict[str, Any]:
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    required = {"town.json", "config.json", "trace.jsonl", "judge_requests.jsonl",
                "judge_crosswalk_PRIVATE.jsonl", "listener_scores.csv", "transcript.md"}
    _require(set(manifest.get("files", {})) == required, "unexpected manifest files")
    version = manifest.get("schema_version")
    _require(version in {LEGACY_SCHEMA, CURRENT_SCHEMA}, "unsupported schema")
    _require(manifest.get("evidence_kind") in EVIDENCE_KINDS and manifest.get("study_eligible") is False,
             "only non-study evidence is supported")
    _require(version != LEGACY_SCHEMA or manifest["evidence_kind"] == "synthetic_fixture",
             "legacy schema only supports fixtures")
    hashes = manifest.get("source_files_sha256")
    _require(isinstance(hashes, dict) and {"runner.py", "config.py", "artifacts.py"} <= set(hashes)
             and all(isinstance(k, str) and Path(k).name == k and _hash(v) for k, v in hashes.items()),
             "invalid saved source hashes")
    for name, value in manifest["files"].items():
        _require(hashlib.sha256((directory / name).read_bytes()).hexdigest() == value,
                 "file hash mismatch: " + name)
    town = json.loads((directory / "town.json").read_text())
    _require(town.get("schema_version") == manifest["schema_version"], "schema mismatch")
    _require(town.get("evidence_kind") == manifest["evidence_kind"] and town.get("study_eligible") is False,
             "evidence markers mismatch")
    _require(town["run_id"] == directory.name, "run identifier mismatch")
    execution = _execution_manifest(town) if version == CURRENT_SCHEMA else None
    if version == CURRENT_SCHEMA:
        _require(town.get("diagnostic_limits") == {
            "scene_5_mention_step_confirmed": "Regex trigger filtered by final whole-dialogue judgment, not earliest substantive mention",
            "scene_3_poster_evidence_passed": "Checked plus artist/board keywords, not semantic evidence-transfer adjudication",
        }, "diagnostic interpretation mismatch")
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
        _require(all(call[key] == call["request"][request_key] for key, request_key in
                     (("kind", "kind"), ("scene", "scene"), ("seat_id", "seat"),
                      ("turn", "turn"), ("model_key", "model_key"))), "call coordinates mismatch")
        _require(call["backend"] == town["evidence_kind"], "invalid call evidence")
        _require(call["status"] in {"completed", "cancelled", "timeout", "malformed_response", "callback_error"},
                 "call has no terminal status")
        if town["evidence_kind"] == "synthetic_fixture":
            _require(call["provider_api_calls"] == 0 and
                     all(call.get(k) is None for k in ("actual_provider", "actual_model", "token_usage", "cost_usd")),
                     "fixture claims provider metadata")
            if version == CURRENT_SCHEMA:
                raw = _raw_response(call)
                if call["status"] == "completed":
                    _require(raw.get("usage") is None, "fixture raw response claims provider usage")
        else:
            _provider_receipt(call, execution)
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

    fixed = render_template(config["prompts_and_templates"]["scene_1_source_departure_broadcast"],
                            render_values(config, town, 0))
    source_calls = [c for c in calls if c["scene"] == 1]
    if town["source_mode"] == "scripted_insert":
        _require(not source_calls, "scripted broadcast must not call a model")
        _require(town["scene_1_departure_broadcast_text"] == fixed and town["source_exact_text_match"] is True,
                 "broadcast replay mismatch")
    else:
        _require(version == LEGACY_SCHEMA and town["source_mode"] == "offline_generated_exact_prompt",
                 "unsupported source mode")
        _require(len(source_calls) == 1 and source_calls[0]["seat_id"] == 0
                 and source_calls[0]["kind"] == "chat" and source_calls[0]["turn"] == 1,
                 "legacy source callback mismatch")
        observed = completed(1, 0, "chat", 1)
        broadcast = observed[0]["response"] if observed else None
        _require(town["scene_1_departure_broadcast_text"] == broadcast
                 and town["source_exact_text_match"] == (broadcast == fixed if observed else None),
                 "legacy broadcast replay mismatch")

    from .runner import concert_mentioned, evidence_line, parse_check_decision
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
    seen_pairs = set()
    allowed_pairs = {(p["first_hand_seat"], p["second_hand_seat"]) for p in town["catch_up_pairs"]}
    for pair in town["scene_3_catch_up_transcripts"]:
        pair_key = (pair["first_hand_seat"], pair["second_hand_seat"])
        _require(pair_key in allowed_pairs and pair_key not in seen_pairs, "invalid catch-up pair")
        seen_pairs.add(pair_key)
        first, second = pair_key
        seats = [second, first, second, first]
        _require(1 <= len(pair["lines"]) <= 4, "invalid catch-up transcript length")
        for index, line in enumerate(pair["lines"]):
            values = render_values(config, town, seats[index])
            _require(line["turn"] == index + 1 and line["seat_id"] == seats[index]
                     and line["speaker"] == values["name"] and line["scripted"] is (index == 0),
                     "catch-up transcript coordinate mismatch")
            if index == 0:
                opener = render_template(config["prompts_and_templates"]["scene_3_second_hand_scripted_opener"], values)
                _require(line["text"] == opener, "scripted catch-up opener mismatch")
        for line in pair["lines"]:
            if not line["scripted"]:
                observed = completed(3, line["seat_id"], "chat", line["turn"])
                _require(len(observed) == 1 and observed[0]["response"] == line["text"],
                         "catch-up transcript replay mismatch")
                catchup_coverage.append((line["seat_id"], line["turn"]))
    _require(sorted(catchup_coverage) == sorted((c["seat_id"], c["turn"]) for c in calls
             if c["scene"] == 3 and c["kind"] == "chat" and c["status"] == "completed"),
             "catch-up callback coverage mismatch")
    if version == CURRENT_SCHEMA or "scene_3_poster_evidence_passed" in town:
        rows = town.get("scene_3_poster_evidence_passed")
        _require(isinstance(rows, list), "poster evidence diagnostics missing")
        finished_pairs = [p for p in town["scene_3_catch_up_transcripts"]
                          if any(line["turn"] == 4 for line in p["lines"])]
        _require(sorted((r["first_hand_seat"], r["second_hand_seat"]) for r in rows)
                 == sorted((p["first_hand_seat"], p["second_hand_seat"]) for p in finished_pairs),
                 "poster evidence diagnostic coverage mismatch")
        for row in rows:
            first, second = row["first_hand_seat"], row["second_hand_seat"]
            pair = next(p for p in finished_pairs if p["first_hand_seat"] == first
                        and p["second_hand_seat"] == second)
            checked = next(d for d in town["scene_2_first_hand_decisions"] if d["seat_id"] == first)
            is_checked = checked["decision"] == "GO"
            if version == LEGACY_SCHEMA and "literal_poster_quote_found" in row:
                cell = next(c for c in config["pilot_cells"] if c["cell_id"] == town["cell_id"])
                condition = next(c for c in cell["conditions"] if c["condition_type"] == town["condition_type"])
                poster = render_template(condition["ground_truth_noticeboard"], render_values(config, town, first))
                quotes = [line["text"] for line in pair["lines"]
                          if line["seat_id"] == first and poster in line["text"]]
                expected = {"partner_checked": is_checked, "literal_poster_quote_found": bool(quotes),
                            "supporting_quotes": quotes,
                            "rule": "literal_full_poster_match_only_not_semantic_adjudication"}
            else:
                quotes = [line["text"] for line in pair["lines"]
                          if line["seat_id"] == first and evidence_line(line["text"], town["real_artist"])]
                expected = {"partner_checked": is_checked, "evidence_passed": is_checked and bool(quotes),
                            "supporting_quotes": quotes,
                            "rule": "checked_then_named_real_artist_and_board_in_one_line"}
            _require(all(canonical_bytes(row.get(k)) == canonical_bytes(v) for k, v in expected.items()),
                     "poster evidence diagnostic replay mismatch")
    exported_judges = [json.loads(x) for x in (directory / "judge_requests.jsonl").read_text().splitlines()]
    projected = [{"custom_id": x["custom_id"], **x["input"]} for x in town["judge_inputs"]]
    _require(canonical_bytes(exported_judges) == canonical_bytes(projected), "judge request export mismatch")
    phones = {x["seat_id"]: x["lines"] for x in town["scene_5_phone_transcripts"]}
    _require(len(phones) == len(town["scene_5_phone_transcripts"]), "duplicate phone transcript")
    phone_coverage = []
    completed_phone_seats = set()
    trigger_steps = {}
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
            trigger_steps[str(seat)] = reached_mention
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
    _require(canonical_bytes(town["scene_5_funnel_step_mentioned"]) == canonical_bytes(trigger_steps),
             "phone trigger coverage mismatch")
    _require(len({x["custom_id"] for x in town["judge_inputs"]}) == len(town["judge_inputs"]),
             "duplicate judge identity")
    _require(sorted(c["seat_id"] for c in calls if c["kind"] == "judge")
             == sorted(x["seat_id_private"] for x in town["judge_inputs"]), "judge/callback coverage mismatch")
    judge_provenance = {"synthetic_fixture": "synthetic_judge_callback",
                        "development_pilot": "provider_judge_callback",
                        "mocked_provider": "mocked_provider_judge_callback"}[town["evidence_kind"]]
    _require(sorted(c["seat_id"] for c in calls if c["kind"] == "judge" and c["status"] == "completed")
             == sorted(e["seat_id"] for e in town["judge_evaluations"]
                       if e["provenance"] == judge_provenance), "judgment/callback coverage mismatch")
    for item in town["judge_inputs"]:
        expected = make_judge_input(config, town["announced_artist"], phones[item["seat_id_private"]])
        _require(canonical_bytes(item["input"]) == canonical_bytes(expected), "blind judge input mismatch")
        _require(digest(expected) == item["input_sha256"], "judge input hash mismatch")
        actual_calls = [c for c in calls if c["kind"] == "judge" and c["seat_id"] == item["seat_id_private"]]
        _require(len(actual_calls) == 1, "judge request/call count mismatch")
        _require(actual_calls[0]["request"]["messages"] == expected["messages"], "judge prompt mismatch")
        _require(actual_calls[0]["request"]["settings"] == expected["settings"], "judge settings mismatch")
    confirmed_steps = {}
    _require(len({e["seat_id"] for e in town["judge_evaluations"]}) == len(town["judge_evaluations"]),
             "duplicate listener judgment")
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
            _require(row["provenance"] == judge_provenance, "unknown judge provenance")
            observed = completed(5, seat, "judge", 0)
            _require(len(observed) == 1, "judgment has no unique completed callback")
            expected_label = parse_judge_response(observed[0]["response"], lines)
        _require(all(row.get(k) == v for k, v in expected_label.items()), "judge parser replay mismatch")
        confirmed = expected_label["status"] == "valid" and expected_label["label"] != "NOT_MENTIONED"
        confirmed_steps[str(seat)] = town["scene_5_funnel_step_mentioned"][str(seat)] if confirmed else None
    if version == CURRENT_SCHEMA or "scene_5_mention_step_confirmed" in town:
        _require(canonical_bytes(town.get("scene_5_mention_step_confirmed")) == canonical_bytes(confirmed_steps),
                 "confirmed mention step mismatch")
    crosswalk = [json.loads(x) for x in (directory / "judge_crosswalk_PRIVATE.jsonl").read_text().splitlines()]
    _require(canonical_bytes(crosswalk) == canonical_bytes(_crosswalk(town)), "private crosswalk mismatch")
    _require((directory / "listener_scores.csv").read_bytes() == _score_csv(town, config).encode("utf-8"),
             "score CSV replay mismatch")
    _require((directory / "transcript.md").read_text(encoding="utf-8") == _transcript(town),
             "transcript export mismatch")
    expected_metrics = town_metrics(config, town["judge_evaluations"], decisions)
    _require(canonical_bytes(town["metrics"]) == canonical_bytes(expected_metrics), "metric replay mismatch")
    if town["run_status"] == "completed":
        _require(len(decisions) == 12 and len(seen_pairs) == 6 and len(completed_phone_seats) == 12
                 and len(town["judge_evaluations"]) == 12
                 and all(town["scene_statuses"].get(str(i)) == "completed" for i in range(1, 6)),
                 "completed town has incomplete scene coverage")
    _aggregate_usage(town)
    return town


def summarize(output_root: Path) -> dict[str, Any]:
    paths = sorted(p.parent for p in Path(output_root).glob("*/manifest.json"))
    _require(bool(paths), "no saved towns found")
    towns = [audit_town(p) for p in paths]
    evidence_kinds = {t["evidence_kind"] for t in towns}
    _require(len(evidence_kinds) == 1, "cannot pool fixture, mocked-provider and development-pilot evidence")
    evidence_kind = next(iter(evidence_kinds))
    pairs = paired_metrics(towns)
    result = {"evidence_kind": evidence_kind, "study_results_generated": False,
            "provider_api_calls": sum(t["token_usage"]["provider_api_calls"] for t in towns),
            "towns": len(towns), "pairs": len(pairs),
            "completed_towns": sum(t["run_status"] == "completed" for t in towns),
            "fixture_callbacks": sum(t["token_usage"]["fixture_callback_invocations"] for t in towns),
            "judged_phone_inputs": sum(len(t["judge_inputs"]) for t in towns),
            "paired_fixture_metrics" if evidence_kind == "synthetic_fixture" else
            "paired_mock_metrics" if evidence_kind == "mocked_provider" else "paired_development_metrics": pairs,
            "town_summaries": [{k: t[k] for k in ["run_id", "pair_id", "model_key", "condition_type", "metrics"]}
                               for t in towns]}
    if evidence_kind != "synthetic_fixture":
        result.update(actual_provider_api_calls=result["provider_api_calls"],
                      simulated_provider_requests=sum(t["token_usage"].get("simulated_provider_requests", 0)
                                                      for t in towns),
                      provider_request_attempts=sum(t["token_usage"]["provider_request_attempts"] for t in towns))
        for key in ("input_tokens", "output_tokens", "cost_usd"):
            result[key] = _known_sum([t["token_usage"] for t in towns], key)
        result["cost_status"] = "calculated_from_usage" if result["cost_usd"] is not None else "unknown"
        result["billing_verified"] = False
        if evidence_kind == "mocked_provider":
            # Adapter estimates are useful fixture evidence, never billed charges.
            result["simulated_cost_usd"] = result.pop("cost_usd")
            result["cost_usd"] = None
            result["cost_status"] = "simulated_calculation" if result["simulated_cost_usd"] is not None else "unknown"
    return result
