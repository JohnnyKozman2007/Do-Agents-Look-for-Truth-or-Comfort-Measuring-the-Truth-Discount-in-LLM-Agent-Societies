"""Sealed, ungraded probe towns: write once, then audit by replaying the saved replies.

Same contract as simulation_artifacts (manifest last, export replay, coordinate-bound actor
replay), with the probe spec saved beside the main config and a fingerprint that adds the
probe modules to the main generation files.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from types import MappingProxyType
from typing import Any

from .artifacts import (EVIDENCE_KINDS, InvalidBundle, _aggregate_usage, _execution_manifest, _hash,
                        _provider_receipt, _raw_response, _require)
from .config import load_config
from .contracts import GenerationResponse, MalformedGeneration, canonical_bytes, clone, digest
from .probe_config import build_probe_manifest, validate_probe_spec
from .probe_runner import DIAGNOSTIC_LIMITS, PROBE_SCHEMA
from .simulation_artifacts import (GENERATION_SOURCE_FILES, _coordinate, _rows, _semantic, source_sha256,
                                   sync_directory)

_FILES = {"town.json", "config.json", "probe_spec.json", "trace.jsonl", "agent_histories.json",
          "phone_transcripts.json", "grading_items_PRIVATE.jsonl"}
# The main generation modules plus every module that shapes a probe town or its bundle.
PROBE_SOURCE_FILES = GENERATION_SOURCE_FILES + ("probe_artifacts.py", "probe_config.py", "probe_runner.py")
_SEATS = set(range(1, 13))


def probe_source_hashes() -> dict[str, str]:
    here = Path(__file__).parent
    return {name: source_sha256(here / name) for name in PROBE_SOURCE_FILES}


def _grading_items(town: dict) -> list[dict]:
    if town["generation_status"] != "completed":
        return []
    items = []
    for phone in town["scene_5_phone_transcripts"]:
        seat = phone["seat_id"]
        item = {"run_id": town["run_id"], "generation_attempt_id": town["generation_attempt_id"],
                "seat_id_private": seat, "target_artist": town["target_artist"],
                "target_claim": town["target_claim"], "phone_transcript": clone(phone["lines"]),
                "phone_sha256": digest(phone["lines"]),
                "funnel_trigger_step": town["scene_5_funnel_step_mentioned"][str(seat)]}
        item["item_id"] = digest({"schema_version": PROBE_SCHEMA, **item})[:32]
        items.append(item)
    return items


def _exports(town: dict, config: dict, spec: dict) -> dict[str, bytes]:
    return {"town.json": canonical_bytes(town), "config.json": canonical_bytes(config),
            "probe_spec.json": canonical_bytes(spec), "trace.jsonl": _rows(town["calls"]),
            "agent_histories.json": canonical_bytes(town["agent_histories"]),
            "phone_transcripts.json": canonical_bytes(town["scene_5_phone_transcripts"]),
            "grading_items_PRIVATE.jsonl": _rows(_grading_items(town))}


def _pending(town: dict) -> None:
    _require(town.get("schema_version") == PROBE_SCHEMA, "unsupported probe schema")
    _require(town.get("evidence_kind") in EVIDENCE_KINDS and town.get("study_eligible") is False,
             "probe town must remain non-study evidence")
    _require(isinstance(town.get("generation_attempt_id"), str)
             and re.fullmatch(r"[0-9a-f]{32}", town["generation_attempt_id"]) is not None,
             "invalid generation attempt identity")
    _require(town.get("run_status") in {"completed", "cancelled", "timeout", "malformed_response", "runner_error"},
             "invalid actor run status")
    _require(town.get("generation_status") == ("completed" if town["run_status"] == "completed" else "failed"),
             "generation status mismatch")
    _require(town.get("evaluation_status") == "pending" and town.get("metrics") is None
             and town.get("judge_inputs") == [] and town.get("judge_evaluations") == []
             and town.get("scene_5_mention_step_confirmed") == {},
             "ungraded probe town contains evaluation results")
    _require(town.get("diagnostic_limits") == DIAGNOSTIC_LIMITS, "diagnostic interpretation mismatch")


def save_probe_simulation(directory: Path, town: dict, config: dict, spec: dict) -> None:
    """Write a new immutable bundle, manifest last; a failed attempt is preserved too."""
    _pending(town)
    directory = Path(directory)
    created, ancestor = [], directory
    while not ancestor.exists():
        created.append(ancestor)
        ancestor = ancestor.parent
    directory.mkdir(parents=True, exist_ok=True)
    _require(not directory.is_symlink() and not any(directory.iterdir()), "refusing to overwrite probe artifact")
    for path in reversed(created):
        sync_directory(path.parent)
    sync_directory(directory.parent)
    data = _exports(town, config, spec)
    sources = probe_source_hashes()
    runtime = {"python": sys.version.split()[0], "implementation": sys.implementation.name, "platform": sys.platform}
    manifest = {"schema_version": PROBE_SCHEMA, "evidence_kind": town["evidence_kind"],
                "study_eligible": False, "generation_status": town["generation_status"],
                "evaluation_status": "pending", "generation_attempt_id": town["generation_attempt_id"],
                "runtime": runtime, "source_files_sha256": sources,
                "source_runtime_sha256": digest({"runtime": runtime, "source_files_sha256": sources}),
                "files": {name: hashlib.sha256(value).hexdigest() for name, value in sorted(data.items())}}
    for name, value in data.items():
        with (directory / name).open("xb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
    sync_directory(directory)
    pending_manifest = directory / ".manifest.pending"
    with pending_manifest.open("xb") as stream:
        stream.write(canonical_bytes(manifest))
        stream.flush()
        os.fsync(stream.fileno())
    pending_manifest.rename(directory / "manifest.json")
    sync_directory(directory)
    sync_directory(directory.parent)


@lru_cache(maxsize=4)
def _run_index(config_bytes: bytes, spec_bytes: bytes, model_key: str) -> MappingProxyType:
    config, spec = json.loads(config_bytes), json.loads(spec_bytes)
    return MappingProxyType({run["run_id"]: canonical_bytes(run)
                             for run in build_probe_manifest(config, spec, [model_key])})


def _replay(config: dict, spec: dict, town: dict, run_plan: dict) -> dict:
    """Re-run the probe state machine against coordinate-bound saved replies, including failures."""
    from .probe_runner import run_probe_town

    calls = {_coordinate(call): call for call in town["calls"]}
    seen = set()

    class SavedResponses:
        evidence_kind = town["evidence_kind"]
        manifest = town.get("execution_manifest")

        async def generate(self, request):
            coordinates = (request.scene, request.seat, request.kind, request.turn)
            _require(coordinates in calls and coordinates not in seen, "actor replay missing or duplicate callback")
            seen.add(coordinates)
            call = calls[coordinates]
            _require(canonical_bytes(asdict(request)) == canonical_bytes(call["request"]),
                     "actor request/context replay mismatch")
            if call["status"] == "completed":
                return GenerationResponse(call["response"], clone(call["token_usage"]))
            base = {"timeout": TimeoutError, "cancelled": asyncio.CancelledError,
                    "malformed_response": MalformedGeneration, "callback_error": RuntimeError}[call["status"]]
            error = type(call["error"], (base,), {})("saved actor callback failure")
            if call.get("token_usage") is not None:
                error.receipt = clone(call["token_usage"])
            raise error

    async def run(destination: Path) -> dict:
        try:
            await run_probe_town(config, spec, run_plan, SavedResponses(), destination)
        except BaseException:
            pass
        _require(seen == set(calls), "actor replay did not consume every saved callback")
        path = destination / town["run_id"] / "town.json"
        _require(path.is_file(), "actor replay failed before preserving its output")
        return json.loads(path.read_bytes())

    with tempfile.TemporaryDirectory(prefix="truth-discount-probe-replay-") as temp:
        destination = Path(temp)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(run(destination))
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(run(destination))).result()


def audit_probe_simulation(directory: Path) -> dict:
    """Audit one sealed probe town: hashes, plan membership, exports and a full actor replay."""
    try:
        directory = Path(directory)
        names = _FILES | {"manifest.json"}
        _require(directory.is_dir() and not directory.is_symlink()
                 and {p.name for p in directory.iterdir()} == names
                 and all(p.is_file() and not p.is_symlink() for p in directory.iterdir()),
                 "unexpected probe artifact files")
        snapshot = {name: (directory / name).read_bytes() for name in names}
        manifest = json.loads(snapshot["manifest.json"])
        _require(manifest.get("schema_version") == PROBE_SCHEMA, "unsupported probe schema")
        _require(set(manifest.get("files", {})) == _FILES, "unexpected probe manifest files")
        for name, expected in manifest["files"].items():
            _require(_hash(expected) and hashlib.sha256(snapshot[name]).hexdigest() == expected,
                     "probe file hash mismatch: " + name)
        sources, runtime = manifest.get("source_files_sha256"), manifest.get("runtime")
        _require(isinstance(sources, dict) and set(PROBE_SOURCE_FILES) <= set(sources)
                 and all(isinstance(k, str) and Path(k).name == k and _hash(v) for k, v in sources.items()),
                 "invalid probe source hashes")
        _require(isinstance(runtime, dict) and set(runtime) == {"python", "implementation", "platform"}
                 and all(isinstance(v, str) and v for v in runtime.values())
                 and manifest.get("source_runtime_sha256") == digest({"runtime": runtime, "source_files_sha256": sources}),
                 "probe source/runtime fingerprint mismatch")
        town = json.loads(snapshot["town.json"])
        _pending(town)
        for key in ("evidence_kind", "study_eligible", "generation_status", "evaluation_status", "generation_attempt_id"):
            _require(town[key] == manifest.get(key), "probe manifest marker mismatch: " + key)
        _require(town["run_id"] == directory.name, "run identifier mismatch")
        config = load_config(directory / "config.json")
        _require(digest(config) == town["config_sha256"], "configuration hash mismatch")
        spec = json.loads(snapshot["probe_spec.json"])
        validate_probe_spec(spec, config)
        _require(digest(spec) == town["probe_spec_sha256"], "probe spec hash mismatch")
        encoded = _run_index(canonical_bytes(config), canonical_bytes(spec), town["model_key"]).get(town["run_id"])
        _require(encoded is not None, "probe town does not belong to its configured plan")
        run = json.loads(encoded)
        for key, value in run.items():
            _require(canonical_bytes(town.get(key)) == canonical_bytes(value), "run-plan mismatch: " + key)
        for name, expected in _exports(town, config, spec).items():
            _require(snapshot[name] == expected, "probe export replay mismatch: " + name)
        execution = _execution_manifest(town)
        calls = town["calls"]
        _require([c["call_id"] for c in calls] == list(range(1, len(calls) + 1)), "invalid call identities")
        _require(len({_coordinate(c) for c in calls}) == len(calls), "duplicate callback coordinates")
        for call in calls:
            _require(call["kind"] in {"chat", "decision"} and call["model_key"] == town["model_key"]
                     and call["seat_id"] in _SEATS, "probe town contains a judge, source or non-actor call")
            _require(call["status"] in {"completed", "cancelled", "timeout", "malformed_response", "callback_error"},
                     "actor call has no terminal status")
            _require(digest(call["request"]) == call["request_sha256"], "actor request hash mismatch")
            _require(all(call[key] == call["request"][request_key] for key, request_key in
                         (("kind", "kind"), ("scene", "scene"), ("seat_id", "seat"),
                          ("turn", "turn"), ("model_key", "model_key"))), "actor call coordinate mismatch")
            _require(call["backend"] == town["evidence_kind"], "actor evidence kind mismatch")
            if town["evidence_kind"] == "synthetic_fixture":
                _require(call["provider_api_calls"] == 0 and all(call.get(k) is None for k in
                         ("actual_provider", "actual_model", "token_usage", "cost_usd")),
                         "synthetic actor claims provider usage")
                raw = _raw_response(call)
                if raw is not None:
                    _require(raw.get("usage") is None, "synthetic raw response claims provider usage")
            else:
                _provider_receipt(call, execution)
                receipt = call.get("token_usage")
                if receipt is not None and receipt.get("cost_status") == "calculated_from_usage":
                    route = execution["routes"][call["model_key"]]
                    _require(receipt["input_tokens"] <= route["max_input_tokens"]
                             and receipt["output_tokens"] <= call["request"]["settings"]["max_tokens"],
                             "priced actor usage exceeds the native request bounds")
            if call["status"] == "completed":
                _require(isinstance(call["response"], str) and (call["kind"] != "chat" or call["response"].strip()),
                         "invalid completed actor response")
            else:
                _require(call.get("response") is None and isinstance(call.get("error"), str) and call["error"],
                         "failed actor callback has invalid response/error")
        _aggregate_usage(town)
        replayed = _replay(config, spec, town, run)
        _require(canonical_bytes(_semantic(town)) == canonical_bytes(_semantic(replayed)),
                 "probe actor state/history/phone replay mismatch")
        if town["generation_status"] == "completed":
            _require(len(town["scene_5_phone_transcripts"]) == 12
                     and {p["seat_id"] for p in town["scene_5_phone_transcripts"]} == _SEATS
                     and len(town["scene_1_departures"]) == 2,
                     "completed probe town lacks its two departures or twelve phones")
        _require(all((directory / name).read_bytes() == data for name, data in snapshot.items()),
                 "probe source changed during audit")
        return town
    except InvalidBundle:
        raise
    except (OSError, KeyError, TypeError, ValueError, OverflowError) as exc:
        raise InvalidBundle(f"invalid probe artifact: {type(exc).__name__}: {exc}") from exc


def probe_grading_items(directory: Path) -> list[dict[str, Any]]:
    """All twelve unlabelled phones of a completed probe town, with its judge target."""
    town = audit_probe_simulation(directory)
    _require(town["generation_status"] == "completed", "cannot grade incomplete generation")
    return _grading_items(town)
