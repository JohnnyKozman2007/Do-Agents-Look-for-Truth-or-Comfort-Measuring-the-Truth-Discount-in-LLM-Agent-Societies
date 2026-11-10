"""Sealed, ungraded actor output; never reinterpret it as legacy scored data.

Replay uses only saved responses and the actor state machine, never a provider.
Hashes establish consistency with a retained manifest, not provider authenticity.
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

from .artifacts import (EVIDENCE_KINDS, InvalidBundle, _aggregate_usage,
                        _execution_manifest, _hash, _provider_receipt, _raw_response,
                        _require)
from .config import build_manifest, load_config
from .contracts import (GenerationResponse, MalformedGeneration, canonical_bytes,
                        clone, digest)


SIMULATION_SCHEMA = "truth-discount-simulation-0.1"
_FILES = {"town.json", "config.json", "trace.jsonl", "agent_histories.json",
          "phone_transcripts.json", "grading_items_PRIVATE.jsonl"}
_DIAGNOSTIC_LIMITS = {
    "scene_5_mention_step_confirmed": "Not computed: evaluation pending",
    "scene_3_poster_evidence_passed": "Checked plus artist/board keywords, not semantic evidence-transfer adjudication",
}


def _rows(rows: list[dict]) -> bytes:
    return b"".join(canonical_bytes(row) + b"\n" for row in rows)


def _grading_items(town: dict) -> list[dict]:
    if town["generation_status"] != "completed":
        return []
    items = []
    for phone in town["scene_5_phone_transcripts"]:
        seat = phone["seat_id"]
        item = {"run_id": town["run_id"],
                "generation_attempt_id": town["generation_attempt_id"],
                "seat_id_private": seat, "target_artist": town["announced_artist"],
                "phone_transcript": clone(phone["lines"]),
                "phone_sha256": digest(phone["lines"]),
                "funnel_trigger_step": town["scene_5_funnel_step_mentioned"][str(seat)]}
        item["item_id"] = digest({"schema_version": SIMULATION_SCHEMA, **item})[:32]
        items.append(item)
    return items


def _exports(town: dict, config: dict) -> dict[str, bytes]:
    return {"town.json": canonical_bytes(town), "config.json": canonical_bytes(config),
            "trace.jsonl": _rows(town["calls"]),
            "agent_histories.json": canonical_bytes(town["agent_histories"]),
            "phone_transcripts.json": canonical_bytes(town["scene_5_phone_transcripts"]),
            "grading_items_PRIVATE.jsonl": _rows(_grading_items(town))}


def _pending(town: dict) -> None:
    _require(town.get("schema_version") == SIMULATION_SCHEMA, "unsupported simulation schema")
    _require(town.get("evidence_kind") in EVIDENCE_KINDS and town.get("study_eligible") is False,
             "simulation must remain non-study evidence")
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
             "ungraded simulation contains evaluation results")
    _require(town.get("diagnostic_limits") == _DIAGNOSTIC_LIMITS,
             "diagnostic interpretation mismatch")


# Only modules that shape actor requests, replies, receipts or saved bundles.
# Collector, CLI and judging code may change without invalidating sealed shards.
GENERATION_SOURCE_FILES = ("artifacts.py", "budget.py", "config.py", "contracts.py",
                           "providers.py", "runner.py", "scoring.py", "simulation_artifacts.py")


def source_sha256(path: Path) -> str:
    """Hash source text with LF line endings, so CRLF and LF checkouts of one commit match."""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def generation_source_hashes() -> dict[str, str]:
    here = Path(__file__).parent
    return {name: source_sha256(here / name) for name in GENERATION_SOURCE_FILES}


def sync_directory(directory: Path) -> None:
    # Windows does not support opening directories for fsync through os.open.
    if os.name != "nt":
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


_sync_directory = sync_directory


def durable_mkdir(path: Path, *, exist_ok: bool) -> None:
    """Create a directory and flush each newly created level and its parent."""
    path = Path(path)
    missing, current = [], path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=exist_ok)
    for created in reversed(missing):
        sync_directory(created)
        sync_directory(created.parent)


def save_simulation(directory: Path, town: dict, config: dict) -> None:
    """Write a new immutable bundle, with the manifest written last.

    A failed actor run is also preserved. Re-execution needs a new attempt;
    this function never replaces a previously sealed or partially written one.
    """
    _pending(town)
    directory = Path(directory)
    created = []
    ancestor = directory
    while not ancestor.exists():
        created.append(ancestor)
        ancestor = ancestor.parent
    directory.mkdir(parents=True, exist_ok=True)
    _require(not directory.is_symlink() and not any(directory.iterdir()),
             "refusing to overwrite simulation artifact")
    for path in reversed(created):
        _sync_directory(path.parent)
    _sync_directory(directory.parent)
    data = _exports(town, config)
    sources = generation_source_hashes()
    runtime = {"python": sys.version.split()[0], "implementation": sys.implementation.name,
               "platform": sys.platform}
    manifest = {"schema_version": SIMULATION_SCHEMA, "evidence_kind": town["evidence_kind"],
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
    _sync_directory(directory)
    # An interrupted manifest write remains visibly unsealed. Publish the
    # manifest only after both payload files and the manifest bytes are durable.
    pending_manifest = directory / ".manifest.pending"
    with pending_manifest.open("xb") as stream:
        stream.write(canonical_bytes(manifest))
        stream.flush()
        os.fsync(stream.fileno())
    pending_manifest.rename(directory / "manifest.json")
    _sync_directory(directory)
    _sync_directory(directory.parent)


def _coordinate(call: dict) -> tuple:
    return call["scene"], call["seat_id"], call["kind"], call["turn"]


@lru_cache(maxsize=4)
def _configured_run_index(config_bytes: bytes, model_key: str) -> MappingProxyType:
    # Immutable values prevent one returned audit result from poisoning later
    # audits. The full canonical configuration is the key, not a mutable dict or
    # only the model name. Four entries bound both main/pilot model indexes.
    config = json.loads(config_bytes)
    return MappingProxyType({run["run_id"]: canonical_bytes(run)
                             for run in build_manifest(config, [model_key])})


def _semantic(town: dict) -> dict:
    result = clone(town)
    # These identify the physical attempt and wall clock, not actor behavior.
    for key in ("timestamps", "generation_attempt_id"):
        result.pop(key, None)
    calls = []
    for call in result["calls"]:
        for key in ("call_id", "elapsed_seconds", "raw_response", "provider_receipt"):
            call.pop(key, None)
        calls.append(call)
    result["calls"] = sorted(calls, key=_coordinate)
    return result


def _replay(config: dict, town: dict, run_plan: dict) -> dict:
    """Re-run actors against coordinate-bound saved replies, including failures."""
    from .runner import run_town

    calls = {_coordinate(call): call for call in town["calls"]}
    seen = set()

    class SavedResponses:
        evidence_kind = town["evidence_kind"]
        manifest = town.get("execution_manifest")

        async def generate(self, request):
            coordinates = (request.scene, request.seat, request.kind, request.turn)
            _require(coordinates in calls and coordinates not in seen,
                     "actor replay missing or duplicate callback")
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
        # Failed callbacks retain a bundle before their exception is propagated.
        try:
            await run_town(config, run_plan, SavedResponses(), destination, defer_judging=True)
        except BaseException:
            pass
        _require(seen == set(calls), "actor replay did not consume every saved callback")
        path = destination / town["run_id"] / "town.json"
        _require(path.is_file(), "actor replay failed before preserving its output")
        return json.loads(path.read_bytes())

    with tempfile.TemporaryDirectory(prefix="truth-discount-actor-replay-") as temp:
        destination = Path(temp)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(run(destination))
        # audit_simulation is also safe to call from async collectors/tests.
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(run(destination))).result()


def audit_simulation(directory: Path) -> dict:
    """Audit an ungraded bundle independently of the legacy scored schema."""
    try:
        directory = Path(directory)
        names = _FILES | {"manifest.json"}
        _require(directory.is_dir() and not directory.is_symlink()
                 and {p.name for p in directory.iterdir()} == names
                 and all(p.is_file() and not p.is_symlink() for p in directory.iterdir()),
                 "unexpected simulation artifact files")
        snapshot = {name: (directory / name).read_bytes() for name in names}
        manifest = json.loads(snapshot["manifest.json"])
        _require(manifest.get("schema_version") == SIMULATION_SCHEMA, "unsupported simulation schema")
        _require(set(manifest.get("files", {})) == _FILES, "unexpected simulation manifest files")
        for name, expected in manifest["files"].items():
            _require(_hash(expected) and hashlib.sha256(snapshot[name]).hexdigest() == expected,
                     "simulation file hash mismatch: " + name)
        sources, runtime = manifest.get("source_files_sha256"), manifest.get("runtime")
        _require(isinstance(sources, dict) and {"runner.py", "config.py", "simulation_artifacts.py"} <= set(sources)
                 and all(isinstance(k, str) and Path(k).name == k and _hash(v) for k, v in sources.items()),
                 "invalid simulation source hashes")
        _require(isinstance(runtime, dict) and set(runtime) == {"python", "implementation", "platform"}
                 and all(isinstance(v, str) and v for v in runtime.values())
                 and manifest.get("source_runtime_sha256") == digest({"runtime": runtime, "source_files_sha256": sources}),
                 "simulation source/runtime fingerprint mismatch")
        town = json.loads(snapshot["town.json"])
        _pending(town)
        for key in ("evidence_kind", "study_eligible", "generation_status", "evaluation_status", "generation_attempt_id"):
            _require(town[key] == manifest.get(key), "simulation manifest marker mismatch: " + key)
        _require(town["run_id"] == directory.name, "run identifier mismatch")
        config = load_config(directory / "config.json")
        _require(digest(config) == town["config_sha256"], "configuration hash mismatch")
        encoded_run = _configured_run_index(canonical_bytes(config), town["model_key"]).get(town["run_id"])
        run = json.loads(encoded_run) if encoded_run is not None else None
        _require(run is not None, "simulation run does not belong to configured plan")
        for key, value in run.items():
            _require(canonical_bytes(town.get(key)) == canonical_bytes(value), "run-plan mismatch: " + key)
        for name, expected in _exports(town, config).items():
            _require(snapshot[name] == expected, "simulation export replay mismatch: " + name)
        execution = _execution_manifest(town)
        calls = town["calls"]
        _require([c["call_id"] for c in calls] == list(range(1, len(calls) + 1)), "invalid call identities")
        _require(len({_coordinate(c) for c in calls}) == len(calls), "duplicate callback coordinates")
        for call in calls:
            _require(call["kind"] in {"chat", "decision"} and call["model_key"] == town["model_key"],
                     "simulation contains a judge or non-actor call")
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
        replayed = _replay(config, town, run)
        _require(canonical_bytes(_semantic(town)) == canonical_bytes(_semantic(replayed)),
                 "actor state/history/phone replay mismatch")
        if town["generation_status"] == "completed":
            _require(len(town["scene_5_phone_transcripts"]) == 12
                     and {p["seat_id"] for p in town["scene_5_phone_transcripts"]} == set(range(1, 13)),
                     "completed generation lacks all twelve phones")
        _require(all((directory / name).read_bytes() == data for name, data in snapshot.items()),
                 "simulation source changed during audit")
        return town
    except InvalidBundle:
        raise
    except (OSError, KeyError, TypeError, ValueError, OverflowError) as exc:
        raise InvalidBundle(f"invalid simulation artifact: {type(exc).__name__}: {exc}") from exc


def grading_items(directory: Path) -> list[dict[str, Any]]:
    """Return all twelve unlabelled phones; partial actor runs are not gradeable."""
    town = audit_simulation(directory)
    _require(town["generation_status"] == "completed", "cannot grade incomplete generation")
    return _grading_items(town)
