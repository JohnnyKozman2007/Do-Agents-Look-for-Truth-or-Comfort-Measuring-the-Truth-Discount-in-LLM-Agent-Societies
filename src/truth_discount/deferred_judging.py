"""Separate, profile-bound adjudication of immutable saved simulations.

Planning and replay never read credentials or open a budget journal. Execution
requires two explicit authority flags and an existing ProviderBackend. Each
profile has its own append-only attempt log; original generation is never edited.
The first attempt remains the descriptive reference after an explicit retry.
"""
from __future__ import annotations

from dataclasses import asdict
from contextlib import contextmanager
from collections import deque
import asyncio
import hashlib
import inspect
import json
import os
from pathlib import Path
import platform
import re
import sys
import threading
from typing import Any

from . import scoring
from .artifacts import _provider_receipt, archived_attempt_paths, audit_town
from .contracts import GenerationRequest, GenerationResponse, canonical_bytes, capture, clone, digest, usage_totals
from .execution import _atomic_json
from .providers import DEFAULT_MAX_CONCURRENT_REQUESTS, ProviderBackend
from .scoring import LABELS, make_judge_input, paired_metrics, parse_judge_response, town_metrics
from .simulation_artifacts import GENERATION_SOURCE_FILES, durable_mkdir, source_sha256

VERSION = "truth-discount-deferred-judging-1"
PARSER_VERSION = "legacy-label-quote-v1"
NORMALIZED_PARSER_VERSION = "quote-normalized-v1"
SUPPORTED_PARSER_VERSIONS = {PARSER_VERSION, NORMALIZED_PARSER_VERSION}
JUDGING_SOURCE_FILES = tuple(sorted(set(GENERATION_SOURCE_FILES) | {
    "deferred_judging.py", "execution.py", "simulation_execution.py",
}))
_ID = re.compile(r"[A-Za-z0-9_.-]{1,100}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_PROFILE_FIELDS = {"version", "profile_id", "approved", "model_key", "provider_manifest", "settings",
                   "rubric", "parser", "population", "population_approved", "source_format", "selection"}


def _normalize_quotes(text: str) -> str:
    """Normalize smart/curly quotes, apostrophes, and accents to standard ASCII quotes."""
    return (
        text.replace("’", "'")
        .replace("‘", "'")
        .replace("´", "'")
        .replace("`", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("„", '"')
        .replace("‟", '"')
    )


def _parse_quote_normalized(text: str, phone_transcript: list[dict]) -> dict:
    """Parse judge response normalizing smart quotes and whitespace."""
    def malformed(error: str) -> dict:
        return {"status": "malformed", "label": None, "quote": None, "error": error}

    if not isinstance(text, str):
        return malformed("response must be text")
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")].strip()
    try:
        value = json.loads(
            cleaned, object_pairs_hook=_unique, parse_constant=scoring._reject_constant
        )
    except (ValueError, RecursionError):
        return malformed("response must be one strict JSON object")
    if not isinstance(value, dict) or set(value) != {"label", "quote"}:
        return malformed("response must contain exactly label and quote")
    label, quote = value["label"], value["quote"]
    if not isinstance(label, str) or label not in LABELS:
        return malformed("unknown categorical label")
    if not isinstance(quote, str):
        return malformed("quote must be a string")
    try:
        turns = scoring._phone_only(phone_transcript)
    except (TypeError, ValueError):
        return malformed("invalid phone transcript")
    if quote == "" and label == "NOT_MENTIONED":
        return {"status": "valid", "label": label, "quote": quote, "error": None}
    if not quote.strip():
        return malformed("a nonempty listener quote is required")
    squashed_quote = "".join(_normalize_quotes(quote).split())
    if not any(
        turn["speaker"].casefold() in scoring._LISTENER_SPEAKERS
        and squashed_quote in "".join(_normalize_quotes(turn["text"]).split())
        for turn in turns
    ):
        return malformed("quote is not a substring of a listener turn, ignoring whitespace and quote variants")
    return {"status": "valid", "label": label, "quote": quote, "error": None}


def parser_sha256(version: str = PARSER_VERSION) -> str:
    """Fingerprint the parser implementation, normalized across line endings."""
    if version == PARSER_VERSION:
        return source_sha256(Path(scoring.__file__))
    if version == NORMALIZED_PARSER_VERSION:
        code = inspect.getsource(_parse_quote_normalized).replace("\r\n", "\n").encode("utf-8")
        return hashlib.sha256(code).hexdigest()
    raise ValueError(f"unsupported parser version: {version}")


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _json(raw: bytes | str) -> Any:
    def reject(_):
        raise ValueError("nonfinite JSON number")
    return json.loads(raw, object_pairs_hook=_unique, parse_constant=reject)


def _profile(value: dict) -> dict:
    if not isinstance(value, dict) or set(value) - _PROFILE_FIELDS:
        raise ValueError("unsupported judge profile fields")
    result = clone(value)
    if type(result.get("version")) is not int or result["version"] != 1:
        raise ValueError("unsupported judge profile version")
    for key in ("profile_id", "model_key"):
        if not isinstance(result.get(key), str) or not _ID.fullmatch(result[key]):
            raise ValueError("invalid judge profile " + key)
    if type(result.get("approved")) is not bool:
        raise ValueError("judge profile approval must be explicit")
    result.setdefault("population", "historical_funnel")
    result.setdefault("population_approved", False)
    result.setdefault("source_format", "simulation")
    result.setdefault("selection", None)
    if result["population"] not in {"historical_funnel", "all_phones"}:
        raise ValueError("unknown judge scoring population")
    if type(result["population_approved"]) is not bool:
        raise ValueError("population approval must be boolean")
    if result["source_format"] not in {"simulation", "legacy_pilot"}:
        raise ValueError("source_format must explicitly select simulation or legacy_pilot")
    selection = result["selection"]
    if selection is not None:
        if (not isinstance(selection, dict) or set(selection) != {
                "version", "approved", "source_sha256", "item_ids", "items_sha256"}
                or type(selection["version"]) is not int or selection["version"] != 1
                or type(selection["approved"]) is not bool
                or any(not isinstance(selection[key], str) or not _HASH.fullmatch(selection[key])
                       for key in ("source_sha256", "items_sha256"))
                or not isinstance(selection["item_ids"], list) or not selection["item_ids"]
                or any(not isinstance(key, str) or not re.fullmatch(r"[0-9a-f]{32}", key)
                       for key in selection["item_ids"])
                or len(set(selection["item_ids"])) != len(selection["item_ids"])):
            raise ValueError("invalid or duplicate explicit judge item selection")
        if selection["item_ids"] != sorted(selection["item_ids"]):
            raise ValueError("explicit judge item IDs must be in canonical sorted order")
    rubric = result.get("rubric")
    if (not isinstance(rubric, dict) or set(rubric) != {"version", "prompt", "sha256"}
            or not isinstance(rubric["version"], str) or not rubric["version"].strip()
            or not isinstance(rubric["prompt"], str) or not rubric["prompt"].strip()
            or rubric["sha256"] != hashlib.sha256(rubric["prompt"].encode()).hexdigest()):
        raise ValueError("rubric version or UTF-8 prompt hash mismatch")
    parser = result.get("parser")
    if not isinstance(parser, dict) or set(parser) != {"version", "sha256"}:
        raise ValueError("judge profile parser must specify version and sha256")
    version = parser.get("version")
    if version not in SUPPORTED_PARSER_VERSIONS or parser.get("sha256") != parser_sha256(version):
        raise ValueError("unsupported parser version or implementation hash")
    if not isinstance(result.get("settings"), dict):
        raise ValueError("judge settings must be explicit")
    manifest = result.get("provider_manifest")
    if (not isinstance(manifest, dict) or not isinstance(manifest.get("routes"), dict)
            or set(manifest["routes"]) != {result["model_key"]}):
        raise ValueError("judge profile must contain only its selected judge route")
    # Constructor checks route structure without key access or network activity.
    ProviderBackend(manifest, _PlanningLedger())
    return result


def load_judge_profile(path: Path) -> dict:
    return _profile(_json(Path(path).read_bytes()))


class _PlanningLedger:
    def summary(self):
        return {"blocked": False}


def _request(item: dict, profile: dict) -> GenerationRequest:
    minimal = {"judging_and_scoring": {"canonical_judge_prompt": profile["rubric"]["prompt"],
                                       "categorical_labels": list(LABELS)},
               "hyperparameters": {"blind_judge_turns": profile["settings"]}}
    blind = make_judge_input(minimal, item["target_artist"], item["phone_transcript"])
    # Neither private seat nor originating actor identity is sent to the backend.
    return GenerationRequest(blind["messages"], blind["settings"], profile["model_key"], "judge", 5, None, 0)


def _roots(source_root) -> list[Path]:
    values = source_root if isinstance(source_root, (list, tuple)) else [source_root]
    if not values:
        raise ValueError("at least one source root is required")
    roots = [Path(p).resolve() for p in values]
    if len(set(roots)) != len(roots):
        raise ValueError("duplicate source root")
    return roots


def _planned_town(town: dict, info: dict, expected: dict) -> None:
    run = expected.get(town["run_id"])
    if run is None or any(digest(town.get(k)) != digest(v) for k, v in run.items()):
        raise ValueError("source town lies outside or differs from the original collection plan")
    for town_key, plan_key in (("config_sha256", "config_sha256"),
                               ("execution_manifest_sha256", "provider_manifest_sha256"),
                               ("evidence_kind", "evidence_kind")):
        if town.get(town_key) != info.get(plan_key):
            raise ValueError("source town differs from its collection's " + plan_key)


def _source_inventory(root: Path) -> list[dict]:
    """Record names and types without opening an original budget journal."""
    inventory = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("immutable source contains a symbolic link")
        kind = "file" if path.is_file() else "directory" if path.is_dir() else None
        if kind is None:
            raise ValueError("immutable source contains an unsupported filesystem entry")
        inventory.append({"path": path.relative_to(root).as_posix(), "kind": kind})
    return inventory


def _bind_payloads(bound: dict, root: Path, directory: Path, manifest: dict,
                   manifest_bytes: bytes) -> None:
    files = {**manifest["files"], "manifest.json": hashlib.sha256(manifest_bytes).hexdigest()}
    for name, expected in files.items():
        relative = (directory / name).relative_to(root).as_posix()
        if relative in bound and bound[relative] != expected:
            raise ValueError("conflicting immutable source file binding")
        bound[relative] = expected


def _verify_source_files(source: dict, directories: dict[str, Path]) -> None:
    """Check all original payloads and collection controls without actor replay."""
    for collection in source["collections"]:
        directory = directories[collection["run_ids"][0]]
        root = directory if collection["source_root_kind"] == "town" else directory.parent
        if _source_inventory(root) != collection["file_inventory"]:
            raise ValueError("immutable source file/archive inventory changed during judging")
        for relative, expected in collection["bound_files_sha256"].items():
            path = root / relative
            if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError("immutable source payload or control changed during judging: " + relative)


def _source(source_root, profile: dict) -> tuple[dict, list[dict], dict[str, Path]]:
    items, sources, directories = [], {}, {}
    common_config = common_evidence = common_implementation = None
    actor_routes, score_config, collections = {}, None, []
    allocation_ids = set()
    for root in _roots(source_root):
        if not root.is_dir():
            raise ValueError("source root is missing")
        candidates = [root] if (root / "town.json").is_file() else [
            p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith("_")]
        if not candidates:
            raise ValueError("source contains no saved towns")
        collection_plan, expected = None, {}
        if (root / "execution_plan.json").exists():
            if profile["source_format"] == "simulation":
                from .simulation_execution import _read_plan
                collection_plan = _read_plan(root)
            else:
                collection_plan = _json((root / "execution_plan.json").read_bytes())
                if (collection_plan.get("execution_plan_version") != 2
                        or digest(collection_plan.get("runs")) != collection_plan.get("run_manifest_sha256")):
                    raise ValueError("legacy source plan requires a valid bound run selection")
            expected = {run["run_id"]: run for run in collection_plan["runs"]}
            if not expected or len(expected) != len(collection_plan["runs"]):
                raise ValueError("source collection plan has duplicate or missing run identities")
        root_runs, bound_files = [], {}
        for directory in candidates:
            if not (directory / "town.json").is_file() or not (directory / "manifest.json").is_file():
                raise ValueError("unexpected source directory without a complete bundle")
            if profile["source_format"] == "simulation":
                from .simulation_artifacts import audit_simulation, _grading_items
                town = audit_simulation(directory)
                if town.get("generation_status") != "completed":
                    raise ValueError("source generation is incomplete")
                generated = _grading_items(town)
            else:
                town = audit_town(directory)
                attempt_id = digest({"legacy_manifest": _json((directory / "manifest.json").read_bytes()),
                                     "run_id": town["run_id"]})[:32]
                generated = []
                for phone in town["scene_5_phone_transcripts"]:
                    seat = phone["seat_id"]
                    row = {"run_id": town["run_id"], "generation_attempt_id": attempt_id,
                           "seat_id_private": seat, "target_artist": town["announced_artist"],
                           "phone_transcript": clone(phone["lines"]), "phone_sha256": digest(phone["lines"]),
                           "funnel_trigger_step": town["scene_5_funnel_step_mentioned"].get(str(seat))}
                    row["item_id"] = digest(row)[:32]
                    generated.append(row)
            if town.get("run_status") != "completed":
                raise ValueError("source contains an incomplete generation attempt; preserve and resolve it first")
            run_id = town["run_id"]
            root_runs.append(run_id)
            if collection_plan is not None:
                _planned_town(town, collection_plan, expected)
            if run_id in sources:
                raise ValueError("duplicate or overlapping source run ID, including identical copies")
            if common_config is None:
                common_config, common_evidence = town["config_sha256"], town["evidence_kind"]
            if town["config_sha256"] != common_config or town["evidence_kind"] != common_evidence:
                raise ValueError("source configuration or evidence kinds differ")
            execution = town.get("execution_manifest") or {"routes": {}}
            for key, route in execution["routes"].items():
                if not any(c.get("kind") in {"chat", "decision"} and c.get("model_key") == key
                           for c in town.get("calls", [])):
                    continue
                semantic = {k: v for k, v in route.items() if k != "api_key_env"}
                if key in actor_routes and actor_routes[key] != semantic:
                    raise ValueError("actor route, settings or pricing differs across source shards")
                actor_routes[key] = semantic
            manifest_bytes = (directory / "manifest.json").read_bytes()
            manifest = _json(manifest_bytes)
            _bind_payloads(bound_files, root, directory, manifest, manifest_bytes)
            if collection_plan is not None and profile["source_format"] == "simulation":
                if (manifest.get("source_files_sha256") != collection_plan.get("source_files_sha256")
                        or manifest.get("runtime") != collection_plan.get("runtime")):
                    raise ValueError("source generation runtime differs from its original collection plan")
            if profile["source_format"] == "simulation":
                source_hashes = manifest.get("source_files_sha256", {})
                code = {name: source_hashes.get(name) for name in GENERATION_SOURCE_FILES}
                if any(not isinstance(value, str) or not _HASH.fullmatch(value) for value in code.values()):
                    raise ValueError("generation protocol source fingerprints are missing")
                implementation = digest(code)
                if common_implementation is not None and implementation != common_implementation:
                    raise ValueError("generation protocol implementation differs across source shards")
                common_implementation = implementation
            entry = {"run_id": run_id, "manifest_sha256": digest(manifest),
                     "town_sha256": hashlib.sha256((directory / "town.json").read_bytes()).hexdigest(),
                     "generation_attempt_id": generated[0]["generation_attempt_id"] if generated else None,
                     "config_sha256": town["config_sha256"], "evidence_kind": town["evidence_kind"],
                     "original_provider_manifest_sha256": town.get("execution_manifest_sha256"),
                     "score_context_PRIVATE": {key: clone(town[key]) for key in
                         ("model_key", "pair_id", "cell_id", "condition_type", "run_id", "layout_id", "repetition_id")},
                     "decisions_PRIVATE": clone(town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"])}
            if score_config is None:
                config = _json((directory / "config.json").read_bytes())
                score_config = {"meta": {"listeners_scored_per_town": config["meta"]["listeners_scored_per_town"]},
                    "seating_and_pairing": {key: clone(config["seating_and_pairing"][key])
                                           for key in ("first_hand_seats", "second_hand_seats")},
                    "judging_and_scoring": {"belief_numerical_mapping": clone(config["judging_and_scoring"]["belief_numerical_mapping"])}}
            critical = ("config.json", "grading_items_PRIVATE.jsonl", "phone_transcripts.json") if profile["source_format"] == "simulation" else ("config.json", "town.json")
            entry["critical_files_sha256"] = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                                               for name in critical}
            if len(generated) != 12 or len({x["seat_id_private"] for x in generated}) != 12:
                raise ValueError("every completed source town must expose all twelve phones")
            for item in generated:
                if (item.get("run_id") != run_id or item.get("phone_sha256") != digest(item.get("phone_transcript"))
                        or not isinstance(item.get("item_id"), str) or not item["item_id"]):
                    raise ValueError("invalid grading item binding")
                item = clone(item)
                item["source_manifest_sha256"] = entry["manifest_sha256"]
                items.append(item)
            sources[run_id], directories[run_id] = entry, directory
        if collection_plan is not None and set(root_runs) != set(expected):
            raise ValueError("source collection has missing planned generations; no silent partial selection")
        archived = archived_attempt_paths(root)
        if archived and collection_plan is None:
            raise ValueError("archived source attempts require their original collection plan")
        archives = []
        for path in archived:
            if profile["source_format"] == "simulation":
                from .simulation_artifacts import audit_simulation
                past = audit_simulation(path)
            else:
                past = audit_town(path)
            _planned_town(past, collection_plan, expected)
            manifest_bytes = (path / "manifest.json").read_bytes()
            archived_manifest = _json(manifest_bytes)
            _bind_payloads(bound_files, root, path, archived_manifest, manifest_bytes)
            archives.append({"relative_path": path.relative_to(root).as_posix(), "run_id": past["run_id"],
                             "manifest_sha256": digest(archived_manifest),
                             "run_status": past["run_status"]})
        allocation = collection_plan.get("allocation") if collection_plan else None
        if allocation:
            allocation_ids.add(allocation["allocation_id"])
        controls = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                    for name in ("execution_plan.json", "budget_checkpoint.json", "resume_log.jsonl")
                    if (root / name).is_file()}
        bound_files.update(controls)
        collections.append({"run_ids": sorted(root_runs), "control_file_sha256": controls,
                            "allocation": clone(allocation), "archived_attempts": archives,
                             "source_root_kind": "town" if (root / "town.json").is_file() else "collection",
                             "file_inventory": _source_inventory(root),
                             "bound_files_sha256": dict(sorted(bound_files.items())),
                            "collection_plan_verified": collection_plan is not None,
                            "ledger_history_verified": False, "billing_verified": False})
    if len(allocation_ids) > 1:
        raise ValueError("source collections belong to different approved allocations")
    if len({x["item_id"] for x in items}) != len(items):
        raise ValueError("duplicate grading item ID")
    _check_judge_independent(actor_routes, profile)
    binding = {"config_sha256": common_config, "evidence_kind": common_evidence,
               "source_format": profile["source_format"], "actor_routes": actor_routes,
               "generation_implementation_sha256": common_implementation,
               "score_config": score_config,
               "collections": sorted(collections, key=digest),
               "towns": [sources[k] for k in sorted(sources)]}
    return binding, sorted(items, key=lambda x: x["item_id"]), directories


def _check_judge_independent(actor_routes: dict, profile: dict) -> None:
    judge_route = profile["provider_manifest"]["routes"][profile["model_key"]]
    if any(route.get("provider") == judge_route["provider"] and route.get("model_id") == judge_route["model_id"]
           for route in actor_routes.values()):
        raise ValueError("judge model must be independent of the simulation actors")


def _unchanged(directory: Path, entry: dict) -> None:
    if digest(_json((directory / "manifest.json").read_bytes())) != entry["manifest_sha256"]:
        raise ValueError("source manifest changed during judging")
    if hashlib.sha256((directory / "town.json").read_bytes()).hexdigest() != entry["town_sha256"]:
        raise ValueError("source town changed during judging")
    if any(hashlib.sha256((directory / name).read_bytes()).hexdigest() != value
           for name, value in entry["critical_files_sha256"].items()):
        raise ValueError("source transcript or config changed during judging")


def make_judge_selection(source_root, profile: dict, item_ids: list[str], *, approved: bool = False) -> dict:
    """Build a zero-call exact subset manifest; approval remains a separate act."""
    if (type(approved) is not bool or not isinstance(item_ids, list) or not item_ids
            or any(not isinstance(key, str) for key in item_ids) or len(set(item_ids)) != len(item_ids)):
        raise ValueError("selection needs unique nonempty explicit item IDs and boolean approval")
    profile = _profile(profile)
    source, full, _ = _source(source_root, profile)
    wanted = set(item_ids)
    selected = [item for item in full if item["item_id"] in wanted]
    if len(selected) != len(wanted):
        raise ValueError("selection item ID is missing from the frozen source")
    return {"version": 1, "approved": approved, "source_sha256": digest(source),
            "item_ids": sorted(item_ids), "items_sha256": digest(selected)}


def _concurrency(value: int) -> int:
    if type(value) is not int or not 1 <= value <= 32:
        raise ValueError("max-concurrent-judgments must be an integer from 1 to 32")
    return value


def _execution_controls(profile: dict, maximum: int) -> dict:
    maximum = _concurrency(maximum)
    route = profile["provider_manifest"]["routes"][profile["model_key"]]
    return {"version": 1, "max_concurrent_judgments": maximum,
            "effective_max_concurrent_judgments": min(maximum, route.get(
                "max_concurrent_requests", DEFAULT_MAX_CONCURRENT_REQUESTS)),
            "failure_policy": "stop_new_items_and_drain_started_attempts"}


def _saved_concurrency(output: Path, profile: dict) -> int:
    """Read-only replay follows the saved execution version, never a new cap."""
    _, path, _, _ = _paths(output, profile)
    info = _json(path.read_bytes())
    controls = info.get("execution_controls")
    if controls is None:
        return 1
    if (not isinstance(controls, dict)
            or controls != _execution_controls(profile, controls.get("max_concurrent_judgments"))
            or controls["max_concurrent_judgments"] == 1):
        raise ValueError("invalid versioned judging execution controls")
    return controls["max_concurrent_judgments"]


def plan_judging(source_root, profile: dict, *, audited: tuple | None = None,
                 max_concurrent_judgments: int = 1) -> dict:
    """Plan one profile. `audited` reuses a `_source` result from this same call path,
    so a single command replays each source town once instead of once per check."""
    profile = _profile(profile)
    maximum = _concurrency(max_concurrent_judgments)
    if audited is not None:
        if audited[0]["source_format"] != profile["source_format"]:
            raise ValueError("reused source audit has a different source format")
        # The per-profile independence check still runs for a reused audit.
        _check_judge_independent(audited[0]["actor_routes"], profile)
    source, full_items, _ = audited if audited is not None else _source(source_root, profile)
    items = full_items
    errors = []
    if not profile["approved"]:
        errors.append("judge profile is not approved")
    if not profile["population_approved"]:
        errors.append("scoring population remains an unapproved policy choice")
    selection = profile["selection"]
    if selection is not None:
        if selection["source_sha256"] != digest(source):
            raise ValueError("item selection belongs to a different frozen source")
        wanted = set(selection["item_ids"])
        items = [item for item in full_items if item["item_id"] in wanted]
        if len(items) != len(wanted):
            raise ValueError("selected item is missing from the frozen source")
        if digest(items) != selection["items_sha256"]:
            raise ValueError("selected item/transcript hashes differ from the frozen subset")
        if not selection["approved"]:
            errors.append("explicit judge item selection is not approved")
    backend = ProviderBackend(profile["provider_manifest"], _PlanningLedger())
    for item in items:
        if profile["population"] == "historical_funnel" and item["funnel_trigger_step"] is None:
            continue
        try:
            backend.validate_request(_request(item, profile))
        except ValueError as error:
            errors.append(str(error))
            break
    rules = sum(profile["population"] == "historical_funnel" and x["funnel_trigger_step"] is None for x in items)
    implementation = {"version": VERSION,
        "runtime": {"python": sys.version.split()[0], "implementation": platform.python_implementation()},
        "source_files_sha256": {name: source_sha256(Path(__file__).parent / name)
                                for name in JUDGING_SOURCE_FILES}}
    result = {"version": VERSION, "status": "blocked" if errors else "ready_for_access_validation",
            "judging_implementation": implementation,
            "execution_gates": errors, "profile": profile, "profile_sha256": digest(profile),
            "source": source, "source_sha256": digest(source), "items_sha256": digest(items),
            "items": items, "source_towns": len(source["towns"]), "source_phone_outcomes": len(full_items),
            "planned_towns": len({item["run_id"] for item in items}), "phone_outcomes": len(items),
            "item_selection_policy": "explicit_frozen_item_ids" if selection is not None else "all_phones_of_supplied_towns",
            "planned_model_judgments": len(items) - rules, "planned_rule_labels": rules,
            "scoring_population": profile["population"], "provider_api_calls": 0,
            "api_access_validated": False, "spending_authorized_by_planning": False, "study_eligible": False}
    # Serial plans retain their existing field layout. Parallel execution is
    # explicitly versioned and frozen; resume never rewrites a saved choice.
    if maximum != 1:
        result["execution_controls"] = _execution_controls(profile, maximum)
    return result


def _events(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError("judging attempt journal is missing")
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n"):
        raise ValueError("interrupted or empty judging journal; preserve it for reconciliation")
    events, previous = [], None
    for seq, line in enumerate(raw.splitlines()):
        event = _json(line)
        if (not isinstance(event, dict) or set(event) != {"seq", "prev_sha256", "event", "sha256"}
                or event["seq"] != seq or type(event["seq"]) is not int or event["prev_sha256"] != previous):
            raise ValueError("conflicting judging journal sequence")
        expected = digest({k: v for k, v in event.items() if k != "sha256"})
        if event["sha256"] != expected:
            raise ValueError("judging journal hash mismatch")
        events.append(event)
        previous = expected
    return events


def _append(path: Path, events: list[dict], payload: dict) -> None:
    row = {"seq": len(events), "prev_sha256": events[-1]["sha256"] if events else None,
           "event": clone(payload)}
    row["sha256"] = digest(row)
    with path.open("ab") as stream:
        stream.write(canonical_bytes(row) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    events.append(row)


def _journal_checkpoint(events: list[dict]) -> dict:
    return {"event_count": len(events), "last_sha256": events[-1]["sha256"] if events else None}


def _stop_reason(call: dict, profile: dict) -> str | None:
    native = call.get("native_response")
    if not isinstance(native, dict):
        return None
    provider = profile["provider_manifest"]["routes"][profile["model_key"]]["provider"]
    if provider == "Anthropic":
        value = native.get("stop_reason")
    else:
        choices = native.get("choices")
        value = choices[0].get("finish_reason") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
    return value if isinstance(value, str) or value is None else "invalid_native_stop_reason"


def _evaluation(call: dict, item: dict, profile: dict) -> dict:
    if call["status"] != "completed":
        return {"status": "unobserved", "label": None, "quote": None, "error": "provider_failure"}
    stop = _stop_reason(call, profile)
    if stop in {"max_tokens", "model_context_window_exceeded", "length"}:
        return {"status": "malformed", "label": None, "quote": None, "error": "native_output_limit"}
    if stop in {"refusal", "content_filter"}:
        return {"status": "unobserved", "label": None, "quote": None, "error": "native_refusal"}
    if stop is not None and stop not in {"end_turn", "stop_sequence", "stop"}:
        return {"status": "unobserved", "label": None, "quote": None, "error": "native_nonterminal_or_unknown_stop"}
    parser_ver = profile.get("parser", {}).get("version", PARSER_VERSION)
    if parser_ver == NORMALIZED_PARSER_VERSION:
        return _parse_quote_normalized(call["response"], item["phone_transcript"])
    return parse_judge_response(call["response"], item["phone_transcript"])


def _native_receipt(call: dict, profile: dict) -> None:
    native = call.get("native_response")
    if native is not None and not isinstance(native, dict):
        raise ValueError("native judge response must be a JSON object or unobserved")
    route = profile["provider_manifest"]["routes"][profile["model_key"]]
    receipt = call.get("token_usage")
    if isinstance(receipt, dict) and receipt.get("cost_status") == "calculated_from_usage":
        if (receipt["input_tokens"] > route["max_input_tokens"]
                or receipt["output_tokens"] > profile["settings"]["max_tokens"]):
            raise ValueError("priced judge receipt exceeds the frozen request token bounds")
    if call["status"] != "completed":
        return
    captured = _json(call["raw_response"]["text"])
    if captured.get("native_response") != native:
        raise ValueError("native judge response differs from the durable raw capture")
    if native is None:
        return  # Explicitly unreported native metadata, never an invented stop reason.
    if ProviderBackend._text(native, route["provider"],
                             allow_thinking=profile["settings"].get("thinking") == {"type": "adaptive"}) != call["response"]:
        raise ValueError("native judge text differs from the parsed response text")
    derived = ProviderBackend._receipt(route, receipt["execution_mode"], receipt["pricing_sha256"])
    ProviderBackend._usage(native, route, derived)
    for key in ("actual_model", "request_id", "input_tokens", "output_tokens", "cached_input_tokens",
                "reasoning_tokens", "cache_creation_input_tokens", "cache_usage", "cost_usd", "cost_status"):
        if derived.get(key) != receipt.get(key):
            raise ValueError("native judge usage or identity differs from the durable receipt: " + key)


def _fold(info: dict, events: list[dict]) -> dict[str, list[dict]]:
    if not events or events[0]["event"] != {"type": "header", "plan_sha256": digest(info)}:
        raise ValueError("judging journal belongs to a different frozen plan")
    expected = {x["item_id"]: x for x in info["items"]}
    histories = {key: [] for key in expected}
    active = {}
    profile = info["profile"]
    for wrapped in events[1:]:
        row = wrapped["event"]
        if not isinstance(row, dict) or row.get("item_id") not in expected:
            raise ValueError("unexpected grading row outside the frozen source")
        key = row["item_id"]
        item = expected[key]
        rules = profile["population"] == "historical_funnel" and item["funnel_trigger_step"] is None
        kind = row.get("type")
        if kind == "rule":
            if set(row) != {"type", "item_id", "evaluation"} or not rules or histories[key] or key in active:
                raise ValueError("duplicate or conflicting rule-coded judgment")
            value = {"status": "valid", "label": "NOT_MENTIONED", "quote": "", "error": None,
                     "provenance": "historical_phone_funnel_rule"}
            if row["evaluation"] != value:
                raise ValueError("rule-coded outcome differs from the declared historical policy")
            histories[key].append(row)
        elif kind == "start":
            if (set(row) != {"type", "item_id", "attempt", "request_sha256", "retry_reason"}
                    or rules or key in active or type(row["attempt"]) is not int
                    or row["attempt"] != len(histories[key]) + 1
                    or row["request_sha256"] != digest(asdict(_request(item, profile)))):
                raise ValueError("duplicate, conflicting or changed judging attempt")
            if row["attempt"] == 1:
                if row["retry_reason"] is not None:
                    raise ValueError("first attempt cannot claim a retry")
            elif row["retry_reason"] not in {"explicit_invalid_retry", "explicit_failure_retry"}:
                raise ValueError("later attempt requires an explicit retry reason")
            else:
                prior = histories[key][-1]
                if prior["type"] != "finish" or prior["evaluation"]["status"] not in {"malformed", "unobserved"}:
                    raise ValueError("a valid judgment cannot be silently resampled")
                expected_reason = ("explicit_invalid_retry" if prior["evaluation"]["status"] == "malformed"
                                   else "explicit_failure_retry")
                if row["retry_reason"] != expected_reason:
                    raise ValueError("retry reason does not match the previous terminal outcome")
            active[key] = row
        elif kind == "finish":
            if set(row) != {"type", "item_id", "attempt", "call", "evaluation"} or key not in active:
                raise ValueError("duplicate or unstarted terminal judgment")
            start = active.pop(key)
            call = row["call"]
            if (row["attempt"] != start["attempt"] or not isinstance(call, dict)
                    or call.get("request") != asdict(_request(item, profile))
                    or call.get("kind") != "judge" or call.get("model_key") != profile["model_key"]
                    or call.get("status") not in {"completed", "failed"}):
                raise ValueError("terminal judgment request or attempt mismatch")
            _provider_receipt(call, profile["provider_manifest"])
            _native_receipt(call, profile)
            if call.get("native_stop_reason") != _stop_reason(call, profile):
                raise ValueError("saved native stop reason differs from the native response")
            parsed = _evaluation(call, item, profile)
            parser_ver = profile.get("parser", {}).get("version", PARSER_VERSION)
            parser_fn = _parse_quote_normalized if parser_ver == NORMALIZED_PARSER_VERSION else parse_judge_response
            parser_only = parser_fn(call["response"], item["phone_transcript"]) if call["status"] == "completed" else None
            if call.get("parser_evaluation") != parser_only:
                raise ValueError("saved historical parser evaluation cannot be reproduced")
            if row["evaluation"] != parsed:
                raise ValueError("saved judgment cannot be replayed from the original response")
            histories[key].append(row)
        else:
            raise ValueError("unsupported judging journal event")
    if active:
        raise ValueError("interrupted judging attempt has no terminal receipt; no automatic resubmission")
    return histories


def _summary(info: dict, events: list[dict]) -> dict:
    histories = _fold(info, events)
    rows, calls = [], []
    for item in info["items"]:
        history = histories[item["item_id"]]
        first = history[0]["evaluation"] if history else None
        latest = history[-1]["evaluation"] if history else None
        rows.append({"item_id": item["item_id"], "run_id": item["run_id"],
                     "generation_attempt_id": item["generation_attempt_id"], "seat_id_private": item["seat_id_private"],
                     "historical_rule_applied": bool(history and history[0]["type"] == "rule"),
                     "original_funnel_trigger_step": item["funnel_trigger_step"],
                     "attempt_count": sum(x["type"] == "finish" for x in history),
                     "first_evaluation": clone(first), "latest_evaluation": clone(latest),
                     "status": first["status"] if first else "not_observed"})
        calls.extend(x["call"] for x in history if x["type"] == "finish")
    evidence = info["evidence_kind"]
    usage = usage_totals(calls, evidence)
    stops = {}
    for call in calls:
        reason = call.get("native_stop_reason") or "unreported"
        stops[reason] = stops.get(reason, 0) + 1
    by_run = {}
    for row in rows:
        by_run.setdefault(row["run_id"], []).append(row)
    def descriptive(field):
        towns = []
        for source in info["source"]["towns"]:
            if source["run_id"] not in by_run:
                continue
            evaluated = [{"seat_id": row["seat_id_private"], **row[field]}
                         for row in by_run[source["run_id"]] if row[field] is not None]
            towns.append({**source["score_context_PRIVATE"],
                          "selected_phone_outcomes": len(by_run[source["run_id"]]),
                          "unselected_phone_outcomes": 12 - len(by_run[source["run_id"]]),
                          "metrics": town_metrics(info["source"]["score_config"], evaluated,
                                                  source["decisions_PRIVATE"])})
        pairs = paired_metrics(towns)
        return {"towns": towns, "paired_metrics": pairs,
                "complete_towns": sum(t["metrics"]["status"] == "complete" for t in towns),
                "complete_pairs": sum(p["status"] == "complete" for p in pairs),
                "defined_conditional_pairs": sum(p["truth_discount"] is not None for p in pairs)}
    return {"version": VERSION, "profile_id": info["profile"]["profile_id"],
            "profile_sha256": info["profile_sha256"], "source_sha256": info["source_sha256"],
            "evidence_kind": evidence, "study_eligible": False,
            "analysis_status": "descriptive only; no primary selection, inferential test or analysis.py study export",
            "validity_policy": "Known native truncation/refusal/nonterminal outcomes remain unavailable; historical parser result retained separately",
            "scoring_population": info["profile"]["population"],
            "source_phone_outcomes": info["source_phone_outcomes"],
            "item_selection_policy": info["item_selection_policy"],
            "selection_policy": "first_attempt_only; latest attempts shown separately, never best-valid selection",
            "phone_outcomes": len(rows), "valid_first_attempt": sum(r["status"] == "valid" for r in rows),
            "malformed_first_attempt": sum(r["status"] == "malformed" for r in rows),
            "unobserved_first_attempt": sum(r["status"] == "unobserved" for r in rows),
            "not_observed": sum(r["status"] == "not_observed" for r in rows),
            "attempts": len(calls), "items": rows,
            "native_stop_reasons": stops,
            "descriptive_first_attempt": descriptive("first_evaluation"),
            "descriptive_latest_attempt": descriptive("latest_evaluation"), **usage}


def _paths(output: Path, profile: dict) -> tuple[Path, Path, Path, Path]:
    directory = Path(output).resolve() / profile["profile_id"]
    return directory, directory / "judging_plan.json", directory / "attempts.jsonl", directory / "budget_checkpoint.json"


def _without_runtime(implementation):
    if not isinstance(implementation, dict):
        return implementation
    return {k: v for k, v in implementation.items() if k != "runtime"}


def _verify_saved(source_root, output: Path, profile: dict | None = None, *,
                  candidate: dict | None = None, strict_runtime: bool = True) -> tuple[dict, list[dict]]:
    """Check a saved plan and journal. Resume binds the exact interpreter build;
    a read-only replay (strict_runtime=False) only reports a different build,
    because every saved judgment is recomputed from its stored response."""
    if profile is None:
        raise ValueError("replay requires the explicit judge profile")
    profile = _profile(profile)
    _, path, journal, anchor = _paths(output, profile)
    info = _json(path.read_bytes())
    if candidate is None:
        candidate = plan_judging(source_root, profile,
                                 max_concurrent_judgments=_saved_concurrency(output, profile))
    for key in candidate:
        saved, current = info.get(key), candidate[key]
        if key == "judging_implementation" and not strict_runtime:
            saved, current = _without_runtime(saved), _without_runtime(current)
        if saved != current:
            raise ValueError("saved judging source/profile differs from the frozen plan: " + key)
    if set(info) != set(candidate) | {"evidence_kind", "ledger_binding"}:
        raise ValueError("unexpected frozen judging plan fields")
    events = _events(journal)
    checkpoint = _json(anchor.read_bytes())
    if (set(checkpoint) != {"plan_sha256", "ledger_checkpoint", "journal_checkpoint"}
            or checkpoint["plan_sha256"] != digest(info)
            or checkpoint["journal_checkpoint"] != _journal_checkpoint(events)):
        raise ValueError("judging journal differs from the durable checkpoint")
    _fold(info, events)
    return info, events


def replay_judging(source_root, output: Path, profile: dict | None = None, *,
                   audited: tuple | None = None) -> dict:
    """Read-only strict replay. Never opens the original ledger or credentials."""
    if profile is None:
        raise ValueError("replay requires the explicit judge profile")
    profile = _profile(profile)
    audited = _source(source_root, profile) if audited is None else audited
    candidate = plan_judging(source_root, profile, audited=audited,
                             max_concurrent_judgments=_saved_concurrency(output, profile))
    info, events = _verify_saved(source_root, output, profile, candidate=candidate, strict_runtime=False)
    _verify_source_files(candidate["source"], audited[2])
    return _with_runtime(_summary(info, events), info, candidate)


def _with_runtime(result: dict, info: dict, candidate: dict) -> dict:
    planned = (info.get("judging_implementation") or {}).get("runtime")
    replayed = candidate["judging_implementation"]["runtime"]
    return {**result, "replay_runtime": {"planned": planned, "replay": replayed,
                                         "matches_plan": planned == replayed}}


async def _judge_collection(source_root, output: Path, profile: dict, backend, *, resume: bool = False,
                           retry_invalid: bool = False, retry_failed: bool = False,
                           max_concurrent_judgments: int = 1,
                           execution_authorized: bool = False, spending_authorized: bool = False) -> dict:
    """Run only saved judge inputs after authority, source and ledger checks.

    Known failures need explicit retry_failed; malformed responses need explicit
    retry_invalid. Unknown reservations still block at the bound original ledger.
    Missing terminal log entries are never automatically repeated.
    """
    if execution_authorized is not True or spending_authorized is not True:
        raise ValueError("separate execution and spending authorization are required; spending hold remains")
    for value in (resume, retry_invalid, retry_failed):
        if type(value) is not bool:
            raise ValueError("resume and retry choices must be booleans")
    profile = _profile(profile)
    maximum = _concurrency(max_concurrent_judgments)
    # Audit (replay) every source town once for this whole invocation.
    audited = _source(source_root, profile)
    candidate = plan_judging(source_root, profile, audited=audited,
                             max_concurrent_judgments=maximum)
    if candidate["execution_gates"]:
        raise ValueError("; ".join(candidate["execution_gates"]))
    if digest(backend.manifest) != digest(profile["provider_manifest"]):
        raise ValueError("backend provider manifest differs from the judge profile")
    if backend.evidence_kind not in {"development_pilot", "mocked_provider"}:
        raise ValueError("deferred judging requires explicit provider evidence")
    if candidate["source"]["evidence_kind"] in {"synthetic_fixture", "mocked_provider"} and backend.evidence_kind != "mocked_provider":
        raise ValueError("synthetic/mock sources cannot be submitted to live providers")
    directory, plan_path, journal, anchor = _paths(output, profile)
    for root in _roots(source_root):
        if directory == root or root in directory.parents or directory in root.parents:
            raise ValueError("judging output must be outside the immutable source roots")
    ledger = backend.ledger
    cp = ledger.checkpoint()
    binding = {k: cp[k] for k in ("ledger_id", "limit_usd")}
    if resume:
        info, events = _verify_saved(source_root, output, profile, candidate=candidate)
        if info["ledger_binding"] != binding or info["evidence_kind"] != backend.evidence_kind:
            raise ValueError("resume requires original ledger identity, fixed cap and evidence kind")
        ledger.verify_checkpoint(_json(anchor.read_bytes())["ledger_checkpoint"])
    else:
        if directory.exists():
            raise FileExistsError("existing profile output requires explicit resume")
        info = {**candidate, "ledger_binding": binding, "evidence_kind": backend.evidence_kind}
        events = []
    if ledger.summary()["blocked"]:
        raise ValueError("bound ledger has unresolved charges or storage failure; no calls may resume")
    histories = _fold(info, events) if resume else {x["item_id"]: [] for x in info["items"]}
    directories = audited[2]
    source_entries = {x["run_id"]: x for x in info["source"]["towns"]}
    pending = []
    for item in info["items"]:
        history = histories[item["item_id"]]
        if not history:
            pending.append((item, None))
        elif history[-1]["type"] == "finish":
            status = history[-1]["evaluation"]["status"]
            if status == "malformed" and retry_invalid:
                pending.append((item, "explicit_invalid_retry"))
            elif status == "unobserved" and retry_failed:
                pending.append((item, "explicit_failure_retry"))
    for item, _ in pending:
        if not (profile["population"] == "historical_funnel" and item["funnel_trigger_step"] is None):
            backend.validate_request(_request(item, profile))
    # Only the selected judge key is touched; actor credentials are irrelevant.
    if any(not (profile["population"] == "historical_funnel" and i["funnel_trigger_step"] is None)
           for i, _ in pending):
        backend.validate_credentials([profile["model_key"]])
    if not resume:
        _durable_mkdir(directory, exist_ok=False)
        _atomic_json(plan_path, info)
        _append(journal, events, {"type": "header", "plan_sha256": digest(info)})
    plan_hash = digest(info)
    journal_mutex = threading.RLock()
    latest_checkpoint = clone(ledger.checkpoint())
    def checkpoint_locked(value):
        nonlocal latest_checkpoint
        if any(value.get(key) != binding[key] for key in ("ledger_id", "limit_usd")):
            raise ValueError("judging checkpoint changed the original ledger binding")
        if value["event_count"] > latest_checkpoint["event_count"]:
            latest_checkpoint = clone(value)
        elif (value["event_count"] == latest_checkpoint["event_count"]
                and value != latest_checkpoint):
            raise ValueError("conflicting ledger history at the same checkpoint")
        _atomic_json(anchor, {"plan_sha256": plan_hash, "ledger_checkpoint": latest_checkpoint,
                              "journal_checkpoint": _journal_checkpoint(events)})
    def checkpoint(value):
        # A ledger callback already holds its ledger mutex. Never acquire that
        # mutex while holding journal_mutex: this order also supports callbacks
        # from another thread without a ledger/journal lock inversion.
        with journal_mutex:
            checkpoint_locked(value)
    def record(payload):
        value = ledger.checkpoint()
        with journal_mutex:
            _append(journal, events, payload)
            # Another callback may have advanced since value was read. The
            # cached checkpoint is monotone, so this write cannot rewind it.
            checkpoint_locked(value)
    checkpoint(ledger.checkpoint())
    ledger.set_checkpoint_callback(checkpoint)
    async def one(item, retry_reason):
        # Bound per-call work to this town's small input exports. Full saved
        # response replay is done once for the source collection, not N times.
        _unchanged(directories[item["run_id"]], source_entries[item["run_id"]])
        key = item["item_id"]
        if profile["population"] == "historical_funnel" and item["funnel_trigger_step"] is None:
            record({"type": "rule", "item_id": key,
                    "evaluation": {"status": "valid", "label": "NOT_MENTIONED", "quote": "", "error": None,
                                   "provenance": "historical_phone_funnel_rule"}})
            return
        request = _request(item, profile)
        attempt = len(histories[key]) + 1
        record({"type": "start", "item_id": key, "attempt": attempt,
                "request_sha256": digest(asdict(request)), "retry_reason": retry_reason})
        call = {"kind": "judge", "model_key": profile["model_key"], "request": asdict(request),
                "status": "failed", "response": None, "raw_response": None, "token_usage": None,
                "native_response": None,
                "actual_provider": None, "actual_model": None, "provider_api_calls": 0, "cost_usd": None}
        failure = None
        try:
            response = await backend.generate(request)
            if not isinstance(response, GenerationResponse) or not isinstance(response.text, str):
                raise ValueError("provider returned an unsupported generation response")
            call.update(status="completed", response=response.text, token_usage=clone(response.usage),
                        native_response=clone(getattr(response, "native_response", None)),
                        raw_response=capture(response, limit=1_000_000))
        except BaseException as error:
            failure = error
            call["native_response"] = clone(getattr(error, "native_response", None))
            receipt = getattr(error, "receipt", None)
            if isinstance(receipt, dict) and receipt:
                call["token_usage"] = clone(receipt)
                call["provider_receipt"] = clone(receipt)
        if isinstance(call["token_usage"], dict):
            call.update({k: call["token_usage"].get(k) for k in
                         ("actual_provider", "actual_model", "provider_api_calls", "cost_usd")})
        call["native_stop_reason"] = _stop_reason(call, profile)
        parser_ver = profile.get("parser", {}).get("version", PARSER_VERSION)
        parser_fn = _parse_quote_normalized if parser_ver == NORMALIZED_PARSER_VERSION else parse_judge_response
        call["parser_evaluation"] = (parser_fn(call["response"], item["phone_transcript"])
                                     if call["status"] == "completed" else None)
        parsed = _evaluation(call, item, profile)
        record({"type": "finish", "item_id": key, "attempt": attempt,
                "call": call, "evaluation": parsed})
        if failure is not None:
            raise ValueError("judging stopped after a provider failure; preserve receipts and reconcile before explicit retry") from None
        _provider_receipt(call, profile["provider_manifest"])
    queue, failures = deque(pending), []
    async def worker():
        # Queue ownership and this stop flag live on this one event loop. No
        # await separates the failure check from taking the next unique item.
        while queue and not failures:
            item, retry_reason = queue.popleft()
            try:
                await one(item, retry_reason)
            except BaseException as error:
                failures.append(error)
                return
    effective = _execution_controls(profile, maximum)["effective_max_concurrent_judgments"]
    workers = [asyncio.create_task(worker()) for _ in range(min(effective, len(pending)))]
    try:
        try:
            await asyncio.gather(*workers)
        except BaseException:
            # Do not detach the durable budget anchor while a started worker
            # is still preserving its cancellation/failure receipt.
            failures.append(ValueError("judging invocation interrupted"))
            await asyncio.shield(asyncio.gather(*workers, return_exceptions=True))
            raise
    finally:
        ledger.set_checkpoint_callback(None)
    if failures:
        raise failures[0]
    # Sources were fully audited once above; confirm no bound file changed since,
    # then strictly re-verify the plan, checkpoint and journal.
    for run_id, source_directory in directories.items():
        _unchanged(source_directory, source_entries[run_id])
    _verify_source_files(candidate["source"], directories)
    final_info, final_events = _verify_saved(source_root, output, profile, candidate=candidate)
    result = _with_runtime(_summary(final_info, final_events), final_info, candidate)
    return {**result, "profile_output": str(directory), "resumed": resume,
            "budget_accounting": {"scope": "entire_original_bound_ledger", "ledger_id": binding["ledger_id"],
                                  "budget": ledger.summary(), "billing_verified": False}}


@contextmanager
def _writer_lock(path: Path):
    stream = path.open("a+b")
    try:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            if not stream.read(1):
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        stream.close()
        raise ValueError("judge profile output is already owned by another process") from None
    try:
        yield
    finally:
        # Release explicitly: Windows frees a closed handle's byte locks only
        # asynchronously, so an immediate rerun could be refused otherwise.
        try:
            if os.name == "nt":
                import msvcrt
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            stream.close()


def _durable_mkdir(path: Path, *, exist_ok: bool = True) -> None:
    durable_mkdir(path, exist_ok=exist_ok)


async def judge_collection(source_root, output: Path, profile: dict, backend, *, resume: bool = False,
                           retry_invalid: bool = False, retry_failed: bool = False,
                           max_concurrent_judgments: int = 1,
                           execution_authorized: bool = False, spending_authorized: bool = False) -> dict:
    if execution_authorized is not True or spending_authorized is not True:
        raise ValueError("separate execution and spending authorization are required; spending hold remains")
    maximum = _concurrency(max_concurrent_judgments)
    profile = _profile(profile)
    target, _, _, _ = _paths(output, profile)
    for root in _roots(source_root):
        if target == root or root in target.parents or target in root.parents:
            raise ValueError("judging output must be outside the immutable source roots")
    # Refuse a concurrent writer even if it chose a different ledger. The
    # profile lock does not confer spending authority or touch any source.
    _durable_mkdir(Path(output))
    with _writer_lock(Path(output) / ("." + profile["profile_id"] + ".lock")):
        return await _judge_collection(source_root, output, profile, backend, resume=resume,
            retry_invalid=retry_invalid, retry_failed=retry_failed,
            max_concurrent_judgments=maximum,
            execution_authorized=execution_authorized, spending_authorized=spending_authorized)


def compare_judgments(source_root, collections: list[tuple[Path, dict]]) -> dict:
    """Read-only matched profile agreement, never human correctness or gold."""
    if not isinstance(collections, list) or len(collections) < 2:
        raise ValueError("comparison requires at least two explicit profile outputs")
    profiles = [_profile(profile) for _, profile in collections]
    # Audit the shared source once per source format, not once per profile.
    audited = {}
    for profile in profiles:
        if profile["source_format"] not in audited:
            audited[profile["source_format"]] = _source(source_root, profile)
    reports = [replay_judging(source_root, output, profile, audited=audited[profile["source_format"]])
               for (output, _), profile in zip(collections, profiles)]
    if len({x["profile_id"] for x in reports}) != len(reports):
        raise ValueError("comparison profile IDs must be unique")
    if len({x["source_sha256"] for x in reports}) != 1 or len({p["population"] for p in profiles}) != 1:
        raise ValueError("matched comparison needs identical source inputs and scoring population")
    scores = {"FACT": 1., "CHECKED_TRUE": 1., "UNCERTAIN": .5, "SKEPTICAL": 0., "CHECKED_FALSE": 0.}
    comparisons = []
    for index, left in enumerate(reports):
        for right in reports[index + 1:]:
            right_rows = {r["item_id"]: r for r in right["items"]}
            if set(right_rows) != {r["item_id"] for r in left["items"]}:
                raise ValueError("comparison row identities differ")
            matched, model_only, disagreements, rules = [], [], [], 0
            for a in left["items"]:
                b = right_rows[a["item_id"]]
                x, y = a["first_evaluation"], b["first_evaluation"]
                if x and y and x["status"] == y["status"] == "valid":
                    matched.append((x["label"], y["label"]))
                    if a["historical_rule_applied"] and b["historical_rule_applied"]:
                        rules += 1
                    elif not a["historical_rule_applied"] and not b["historical_rule_applied"]:
                        model_only.append((x["label"], y["label"]))
                    if x["label"] != y["label"]:
                        disagreements.append({"item_id": a["item_id"], "run_id": a["run_id"],
                                              "seat_id_private": a["seat_id_private"],
                                              "left": clone(x), "right": clone(y)})
            n = len(matched)
            agree = sum(a == b for a, b in matched)
            expected = sum(sum(a == label for a, _ in matched) * sum(b == label for _, b in matched)
                           for label in LABELS) / n ** 2 if n else None
            kappa = ((agree / n - expected) / (1 - expected)
                     if n and expected != 1 else None)
            numeric = [(scores[a], scores[b]) for a, b in matched if a in scores and b in scores]
            comparisons.append({"left_profile": left["profile_id"], "right_profile": right["profile_id"],
                "total_phone_outcomes": left["phone_outcomes"], "valid_both": n,
                "excluded_missing_or_invalid": left["phone_outcomes"] - n,
                "rule_coded_both": rules, "model_judged_both": len(model_only),
                "model_only_label_agreement": sum(a == b for a, b in model_only) / len(model_only) if model_only else None,
                "label_agreement": agree / n if n else None,
                "cohens_kappa": kappa, "kappa_status": "defined" if kappa is not None else "undefined",
                "numeric_score_valid_both_non_omitted": len(numeric),
                "numeric_score_agreement": sum(a == b for a, b in numeric) / len(numeric) if numeric else None,
                "omission_agreement": sum((a == "NOT_MENTIONED") == (b == "NOT_MENTIONED") for a, b in matched) / n if n else None,
                "disagreements": disagreements})
    return {"version": VERSION, "source_sha256": reports[0]["source_sha256"],
            "comparison_policy": "first attempts only; valid-both denominators explicit; no human-gold claim",
            "profile_hashes": {r["profile_id"]: r["profile_sha256"] for r in reports},
            "comparisons": comparisons, "provider_api_calls": 0,
            "semantic_accuracy_established": False, "study_eligible": False}
