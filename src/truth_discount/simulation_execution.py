"""Pair-complete actor allocations, resumable collection and read-only handover checks.

Different people may use different account credentials in otherwise identical
routes. Same-shard resume still requires its exact original plan and ledger.
No local file lock can coordinate copies running on two different machines.
"""
from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import itertools
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

from .config import build_manifest
from .contracts import clone, digest, usage_totals
from .budget import money
from .execution import (_atomic_json, load_provider_manifest, plan,
                        validate_backend)
from .simulation_artifacts import (durable_mkdir, generation_source_hashes,
                                   sync_directory as _sync_directory)


ALLOCATION_VERSION = "pair-stratified-round-robin-v1"


def allocate_runs(config: dict, runs: list[dict], *, shard_count: int = 1,
                  shard_index: int = 0) -> tuple[list[dict], dict]:
    if (type(shard_count) is not int or shard_count < 1 or type(shard_index) is not int
            or not 0 <= shard_index < shard_count):
        raise ValueError("shard index is zero-based and must be less than a positive shard count")
    if not runs or len({r["run_id"] for r in runs}) != len(runs):
        raise ValueError("allocation requires a nonempty unique run selection")
    canonical = {r["run_id"]: r for r in build_manifest(config)}
    groups: dict[str, list[dict]] = {}
    for run in runs:
        if run["run_id"] not in canonical or digest(run) != digest(canonical[run["run_id"]]):
            raise ValueError("allocation run differs from configured source manifest")
        groups.setdefault(run["pair_id"], []).append(run)
    for group in groups.values():
        if len(group) != 2 or {r["condition_type"] for r in group} != {"rumor", "truth_twin"}:
            raise ValueError("allocation must contain both twins of every pair")
    if shard_count > len(groups):
        raise ValueError("shard count exceeds the number of complete pairs")
    ordered = sorted(groups, key=lambda p: (groups[p][0]["model_key"],
                                            groups[p][0]["real_artist"], groups[p][0]["cell_id"],
                                            groups[p][0]["seed_id"]))
    selection = [r for pair in ordered for r in sorted(groups[pair], key=lambda r: r["condition_type"])]
    assigned_pairs = ordered[shard_index::shard_count]
    selected = [r for pair in assigned_pairs for r in sorted(groups[pair], key=lambda r: r["condition_type"])]
    allocation = {
        "version": ALLOCATION_VERSION, "config_sha256": digest(config),
        "source_selection_sha256": digest(selection), "source_towns": len(selection),
        "source_run_ids": [r["run_id"] for r in selection],
        "source_pairs": len(groups), "shard_count": shard_count, "shard_index": shard_index,
        "pair_ids": assigned_pairs, "run_ids": [r["run_id"] for r in selected],
        "planned_towns": len(selected), "planned_pairs": len(assigned_pairs),
        "max_phone_outcomes": len(selected) * 12,
    }
    allocation["allocation_id"] = digest({k: allocation[k] for k in (
        "version", "config_sha256", "source_selection_sha256", "shard_count")})
    allocation["shard_sha256"] = digest(allocation)
    return clone(selected), allocation


def simulation_plan(config: dict, providers: dict, runs: list[dict],
                    allocation: dict | None = None) -> dict:
    if allocation is None:
        ordered, allocation = allocate_runs(config, runs)
        if digest(ordered) != digest(runs):
            raise ValueError("simulation run order must match its canonical pair allocation")
    else:
        source = {r["run_id"]: r for r in build_manifest(config)}
        ids = allocation.get("source_run_ids")
        if not isinstance(ids, list) or not ids or any(r not in source for r in ids):
            raise ValueError("allocation needs its original configured source run identities")
        assigned, rebuilt = allocate_runs(config, [source[r] for r in ids],
                                           shard_count=allocation.get("shard_count"),
                                           shard_index=allocation.get("shard_index"))
        if digest(assigned) != digest(runs) or digest(rebuilt) != digest(allocation):
            raise ValueError("allocation differs from the deterministic configured source selection")
    info = plan(config, providers, runs, include_judge=False)
    info.update(execution_mode="simulation_only", evaluation_status="pending",
                allocation=clone(allocation), planned_phone_outcomes=12 * len(runs))
    return info


def _source_hashes() -> dict[str, str]:
    # Same generation-only, line-ending-normalized fingerprint as each sealed bundle.
    return generation_source_hashes()


def _runtime() -> dict[str, str]:
    return {"python": sys.version.split()[0], "implementation": sys.implementation.name,
            "platform": sys.platform}


def _durable_mkdir(path: Path, *, exist_ok: bool = False) -> None:
    durable_mkdir(path, exist_ok=exist_ok)


def _archive_partial(output: Path, directory: Path) -> str:
    for attempt in itertools.count(1):
        target = output / "_incomplete" / f"attempt-{attempt}" / directory.name
        if not target.exists():
            _durable_mkdir(target.parent, exist_ok=True)
            directory.rename(target)
            _sync_directory(target.parent)
            _sync_directory(directory.parent)
            return target.relative_to(output).as_posix()


def _audit_expected(directory: Path, info: dict, run: dict) -> dict:
    from .simulation_artifacts import audit_simulation
    town = audit_simulation(directory)
    for key, expected in (("config_sha256", info["config_sha256"]),
                          ("execution_manifest_sha256", info["provider_manifest_sha256"]),
                          ("evidence_kind", info["evidence_kind"])):
        if town.get(key) != expected:
            raise ValueError("saved simulation differs from execution plan: " + key)
    if any(digest(town.get(k)) != digest(v) for k, v in run.items()):
        raise ValueError("saved simulation run differs from execution plan")
    manifest = load_provider_manifest(directory / "manifest.json")
    if manifest.get("source_files_sha256") != info["source_files_sha256"]:
        raise ValueError("saved simulation runtime source differs from the execution plan")
    if (manifest.get("runtime") != info["runtime"]
            or manifest.get("source_runtime_sha256") != info["source_runtime_sha256"]):
        raise ValueError("saved simulation runtime fingerprint differs from the execution plan")
    return town


def _read_plan(root: Path) -> dict:
    if any((root / name).is_symlink() for name in ("execution_plan.json", "budget_checkpoint.json")):
        raise ValueError("simulation control files cannot be symbolic links")
    info = load_provider_manifest(root / "execution_plan.json")
    if info.get("execution_plan_version") != 3 or info.get("execution_mode") != "simulation_only":
        raise ValueError("expected a versioned simulation-only execution plan")
    if digest(info["config"]) != info["config_sha256"]:
        raise ValueError("simulation plan config hash mismatch")
    if digest(info["provider_manifest"]) != info["provider_manifest_sha256"]:
        raise ValueError("simulation plan provider hash mismatch")
    if digest(info["runs"]) != info["run_manifest_sha256"]:
        raise ValueError("simulation plan run hash mismatch")
    if info.get("source_runtime_sha256") != digest({"runtime": info.get("runtime"),
                                                    "source_files_sha256": info.get("source_files_sha256")}):
        raise ValueError("simulation plan runtime fingerprint mismatch")
    if simulation_plan(info["config"], info["provider_manifest"], info["runs"],
                       info["allocation"])["execution_gates"]:
        raise ValueError("saved simulation plan has unresolved gates")
    anchor = load_provider_manifest(root / "budget_checkpoint.json")
    if (set(anchor) != {"execution_plan_sha256", "ledger_checkpoint"}
            or anchor["execution_plan_sha256"] != digest(info)):
        raise ValueError("simulation budget checkpoint does not bind its plan")
    binding = info.get("ledger_binding", {})
    cp = anchor["ledger_checkpoint"]
    if (not isinstance(binding, dict) or set(binding) != {"ledger_id", "limit_usd"}
            or not isinstance(binding["ledger_id"], str)
            or re.fullmatch(r"[0-9a-f]{32}", binding["ledger_id"]) is None
            or not isinstance(binding["limit_usd"], str)
            or money(binding["limit_usd"]) < 0
            or not isinstance(cp, dict)
            or set(cp) != {"ledger_id", "limit_usd", "event_count", "history_sha256"}
            or type(cp["event_count"]) is not int or cp["event_count"] < 1
            or not isinstance(cp["history_sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", cp["history_sha256"]) is None):
        raise ValueError("simulation plan needs a valid original ledger binding and checkpoint")
    if any(anchor["ledger_checkpoint"].get(k) != v for k, v in binding.items()):
        raise ValueError("simulation checkpoint ledger identity or cap mismatch")
    allocation = info["allocation"]
    if allocation:
        if allocation["run_ids"] != [r["run_id"] for r in info["runs"]]:
            raise ValueError("allocation run identities differ from execution plan")
        original = {k: v for k, v in allocation.items() if k != "shard_sha256"}
        if digest(original) != allocation["shard_sha256"]:
            raise ValueError("allocation hash mismatch")
    return info


def review_simulations(roots: Path | list[Path]) -> dict[str, Any]:
    """Read sealed generations without producing or consuming any judge scores."""
    roots = [roots] if isinstance(roots, (str, Path)) else roots
    if not roots:
        raise ValueError("at least one simulation collection is required")
    roots = [Path(p).resolve() for p in roots]
    if len(set(roots)) != len(roots):
        raise ValueError("duplicate simulation collection")
    seen_runs, routes, files, configs, kinds = set(), {}, None, set(), set()
    town_count, completed_count, phone_count = 0, 0, 0
    pair_counts, aggregated_usage = Counter(), {}
    # Failed attempts, current or archived, so selection by success is visible.
    failed_by_cell, failed_by_status = Counter(), Counter()
    reports, selections, runtimes = [], set(), {}
    allocated, source_total, allocation_seen = set(), None, set()
    for root in roots:
        info = _read_plan(root)
        configs.add(info["config_sha256"])
        kinds.add(info["evidence_kind"])
        runtimes[digest(info["runtime"])] = info["runtime"]
        if files is None:
            files = info["source_files_sha256"]
        elif files != info["source_files_sha256"]:
            raise ValueError("simulation shards use different runtime source versions")
        expected = {r["run_id"]: r for r in info["runs"]}
        if len(expected) != len(info["runs"]):
            raise ValueError("duplicate planned simulation identity")
        overlap = allocated.intersection(expected)
        if overlap:
            raise ValueError("simulation allocations overlap: " + sorted(overlap)[0])
        allocated.update(expected)
        allocation = info.get("allocation")
        if allocation:
            selections.add(allocation["allocation_id"])
            marker = (allocation["allocation_id"], allocation["shard_index"])
            if marker in allocation_seen:
                raise ValueError("duplicate allocation shard")
            allocation_seen.add(marker)
            source_total = allocation["source_towns"]
        elif len(roots) > 1:
            raise ValueError("multiple collections need an explicit shared allocation")
        for model in {r["model_key"] for r in info["runs"]}:
            # Account values never enter manifests. Only this local env-var label
            # may differ across shards; prices and generation controls must match.
            route = {k: v for k, v in info["provider_manifest"]["routes"][model].items()
                     if k != "api_key_env"}
            if model in routes and routes[model] != route:
                raise ValueError("actor route differs across shards: " + model)
            routes[model] = route
        present = set()
        completed = set()
        for path in sorted(root.iterdir()):
            if path.is_symlink():
                raise ValueError("simulation collection contains a symbolic link")
            if not path.is_dir() or path.name == "_incomplete":
                continue
            if path.name not in expected:
                raise ValueError("unplanned simulation directory: " + path.name)
            town = _audit_expected(path, info, expected[path.name])
            present.add(path.name)
            if path.name in seen_runs:
                raise ValueError("duplicate completed simulation identity")
            seen_runs.add(path.name)
            town_count += 1
            if town["generation_status"] == "completed":
                completed.add(path.name)
                completed_count += 1
                pair_counts[town["pair_id"]] += 1
                phone_count += len(town["scene_5_phone_transcripts"])
            else:
                failed_by_cell[str(town["cell_id"])] += 1
                failed_by_status[town["run_status"]] += 1
            # Keep one town in memory at a time; actor histories can be large.
            usage = usage_totals(town["calls"], town["evidence_kind"])
            for key, value in usage.items():
                if key == "cost_status":
                    continue
                if key not in aggregated_usage:
                    aggregated_usage[key] = None if value is None else Decimal(str(value))
                elif aggregated_usage[key] is None or value is None:
                    aggregated_usage[key] = None
                else:
                    aggregated_usage[key] += Decimal(str(value))
        from .artifacts import archived_attempt_paths
        archived = archived_attempt_paths(root)
        for path in archived:
            if path.name not in expected or path.is_symlink():
                raise ValueError("unplanned archived simulation attempt")
            past = _audit_expected(path, info, expected[path.name])
            if past["generation_status"] != "completed":
                failed_by_cell[str(past["cell_id"])] += 1
                failed_by_status[past["run_status"]] += 1
        reports.append({"root": str(root), "planned_towns": len(expected),
                        "completed_towns": len(completed), "missing_run_ids": sorted(set(expected) - present),
                        "incomplete_run_ids": sorted(present - completed), "archived_attempts": len(archived),
                        "ledger_binding": info["ledger_binding"],
                        "ledger_history_verified": False, "billing_verified": False,
                        "execution_plan_sha256": digest(info), "allocation": allocation})
    if len(configs) != 1 or len(kinds) != 1 or len(selections) > 1:
        raise ValueError("simulation shards have incompatible config, evidence or allocation")
    usage = {k: None if v is None else float(v) if k == "cost_usd" else int(v)
             for k, v in aggregated_usage.items()}
    if next(iter(kinds)) != "synthetic_fixture":
        usage["cost_status"] = "known" if usage.get("cost_usd") is not None else "unknown"
    full_allocation = source_total is not None and len(allocated) == source_total
    # Supplied shards can all be finished while other shards of the study are absent.
    if completed_count != len(allocated):
        status = "generation_incomplete"
    else:
        status = "generation_complete" if full_allocation else "shards_complete"
    return {"status": status,
            "evidence_kind": next(iter(kinds)), "study_eligible": False,
            "study_results_generated": False, "evaluation_status": "pending",
            "towns": town_count, "completed_towns": completed_count,
            "completed_pairs": sum(n == 2 for n in pair_counts.values()),
            "unpaired_completed_pair_ids": sorted(p for p, n in pair_counts.items() if n != 2),
            "planned_towns": len(allocated), "source_selection_towns": source_total,
            "full_allocation_present": full_allocation,
            "phone_transcripts": phone_count,
            "failed_generation_attempts": sum(failed_by_cell.values()),
            "failed_generation_attempts_by_cell": dict(sorted(failed_by_cell.items(), key=lambda x: int(x[0]))),
            "failed_generation_attempts_by_status": dict(sorted(failed_by_status.items())),
            "judge_calls": 0, "metrics_available": False, "collections": reports,
            "runtime_profiles": [runtimes[k] for k in sorted(runtimes)],
            "runtime_variation": len(runtimes) > 1,
            "current_attempt_usage": usage}


async def collect_simulations(config: dict, providers: dict, runs: list[dict], output: Path,
                              backend, *, allocation: dict | None = None, resume: bool = False,
                              max_concurrent_towns: int = 1, execution_authorized: bool = False,
                              spending_authorized: bool = False, regenerate_failed: bool = False) -> dict:
    from .artifacts import archived_attempt_paths
    from .runner import run_town
    if execution_authorized is not True or spending_authorized is not True:
        raise ValueError("simulation execution and spending authorization are required; hold remains")
    if type(regenerate_failed) is not bool:
        raise ValueError("regenerate_failed must be a boolean")
    output = Path(output)
    if type(max_concurrent_towns) is not int or not 1 <= max_concurrent_towns <= 16:
        raise ValueError("max-concurrent-towns must be an integer from 1 to 16")
    # Even direct callers must use a configured, complete-pair selection.
    allocate_runs(config, runs)
    if output.exists() and not resume:
        raise FileExistsError("refusing existing simulation directory; use resume")
    if resume and not (output / "execution_plan.json").is_file():
        raise ValueError("nothing to resume: no simulation execution plan")
    if digest(providers) != digest(backend.manifest):
        raise ValueError("backend manifest differs from the approved simulation plan")
    info = simulation_plan(config, providers, runs, allocation)
    if info["execution_gates"]:
        raise ValueError("; ".join(info["execution_gates"]))
    ledger = backend.ledger
    checkpoint = ledger.checkpoint()
    binding = {key: checkpoint[key] for key in ("ledger_id", "limit_usd")}
    info.update(execution_plan_version=3, evidence_kind=backend.evidence_kind,
                ledger_binding=binding, config=clone(config), provider_manifest=clone(providers),
                source_files_sha256=_source_hashes(), runtime=_runtime())
    info["source_runtime_sha256"] = digest({"runtime": info["runtime"],
                                           "source_files_sha256": info["source_files_sha256"]})
    if resume:
        saved = _read_plan(output)
        if digest(saved) != digest(info):
            raise ValueError("resume requires the exact original plan, source version, ledger identity and cap")
        ledger.verify_checkpoint(load_provider_manifest(output / "budget_checkpoint.json")["ledger_checkpoint"])
    if ledger.summary()["blocked"]:
        raise ValueError("budget ledger is blocked; reconcile original unknown charges first")
    expected = {r["run_id"]: r for r in runs}
    if len(expected) != len(runs):
        raise ValueError("duplicate simulation run identity")
    for path in sorted(output.iterdir()) if resume else []:
        if path.is_symlink():
            raise ValueError("simulation collection contains a symbolic link")
        if path.is_dir() and path.name != "_incomplete" and path.name not in expected:
            raise ValueError("unplanned simulation directory")
    archived_failed_run_ids = set()
    for path in archived_attempt_paths(output) if resume else []:
        if path.name not in expected or path.is_symlink():
            raise ValueError("unplanned archived simulation attempt")
        past = _audit_expected(path, info, expected[path.name])
        if past["generation_status"] != "completed":
            archived_failed_run_ids.add(past["run_id"])
    pending, skipped, partial = [], [], []
    for run in runs:
        path = output / run["run_id"]
        if not path.exists():
            pending.append(run)
        elif _audit_expected(path, info, run)["generation_status"] == "completed":
            skipped.append(run["run_id"])
        else:
            partial.append(path)
            pending.append(run)
    regenerated_run_ids = sorted({path.name for path in partial}
                                | (archived_failed_run_ids & {run["run_id"] for run in pending}))
    if regenerated_run_ids and not regenerate_failed:
        # Rerunning only failed towns keeps a success-selected sample, so it
        # must be an explicit, logged choice rather than a side effect of resume.
        # A crash after archival but before the next attempt must not make a
        # previously failed allocation look like a never-started town.
        raise ValueError(f"{len(regenerated_run_ids)} sealed failed generation(s), e.g. {regenerated_run_ids[0]}; "
                         "rerun them only with explicit regenerate_failed (--regenerate-failed)")
    # No judge route, judge key or judge preflight is needed at this stage.
    if pending:
        validate_backend(config, pending, backend, include_judge=False)
        backend.validate_credentials(sorted({r["model_key"] for r in pending}))
    if not resume:
        _durable_mkdir(output)
        _atomic_json(output / "execution_plan.json", info)
    plan_hash = digest(info)
    def anchor(value):
        _atomic_json(output / "budget_checkpoint.json", {
            "execution_plan_sha256": plan_hash, "ledger_checkpoint": value})
    anchor(ledger.checkpoint())
    set_aside = [_archive_partial(output, path) for path in partial]
    if resume:
        with (output / "resume_log.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"resumed_utc": datetime.now(timezone.utc).isoformat(),
                                     "skipped_run_ids": skipped, "archived": set_aside,
                                     "regenerate_failed": regenerate_failed,
                                     "regenerated_run_ids": regenerated_run_ids,
                                     "pending_towns": len(pending)}) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        _sync_directory(output)
    queue, failures = list(pending), []
    async def worker():
        while queue and not failures:
            run = queue.pop(0)
            try:
                town = await run_town(config, run, backend, output, defer_judging=True)
                if town["generation_status"] != "completed":
                    raise ValueError("simulation collection stopped after incomplete town: " + run["run_id"])
            except Exception as error:
                failures.append(error)
    ledger.set_checkpoint_callback(anchor)
    try:
        await asyncio.gather(*(worker() for _ in range(max(1, min(max_concurrent_towns, len(pending))))))
    finally:
        ledger.set_checkpoint_callback(None)
    if failures:
        raise failures[0]
    return {**review_simulations(output), "output_root": str(output), "resumed": resume,
            "skipped_verified_towns": len(skipped), "set_aside_towns": set_aside,
            "budget_accounting": {"scope": "entire_original_bound_ledger", "billing_verified": False,
                                  "ledger_id": binding["ledger_id"], "budget": ledger.summary()}}
