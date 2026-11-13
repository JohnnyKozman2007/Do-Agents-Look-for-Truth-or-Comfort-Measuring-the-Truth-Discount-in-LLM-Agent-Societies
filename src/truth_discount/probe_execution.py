"""Group-complete probe allocations, resumable collection and read-only status.

Mirrors simulation_execution for the main run. A group (model, probe, DNA, seed) holds its three
configurations and is never split across shards, like a main-run twin pair.
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
from typing import Any

from .budget import money
from .contracts import GenerationRequest, clone, digest, usage_totals
from .execution import _atomic_json, load_provider_manifest, plan
from .probe_artifacts import probe_source_hashes
from .probe_config import PROBE_CONFIGS, build_probe_manifest, render_probe_contexts
from .simulation_artifacts import durable_mkdir, sync_directory
from .simulation_execution import _runtime

ALLOCATION_VERSION = "probe-group-round-robin-v1"
EXECUTION_MODE = "probe_simulation_only"
INCOMPLETE = "probe collection stopped after incomplete town: "


def select_probe_runs(config: dict, spec: dict, model_keys: list[str] | None = None,
                      probes: list[str] | None = None, seeds_per_dna: int = 1,
                      start_seed: int = 0, all_seeds: bool = False) -> list[dict]:
    """A declared prefix of seeds for every selected probe, DNA and configuration."""
    if type(seeds_per_dna) is not int or not 1 <= seeds_per_dna <= 39:
        raise ValueError("seeds-per-dna must be an integer from 1 to 39")
    if type(start_seed) is not int or not 0 <= start_seed <= 38:
        raise ValueError("start-seed must be an integer from 0 to 38")
    end = 39 if all_seeds else start_seed + seeds_per_dna
    if end > 39:
        raise ValueError("seed range exceeds the configured 39 seeds per DNA")
    chosen = list(PROBE_CONFIGS) if not probes else list(probes)
    if any(p not in PROBE_CONFIGS for p in chosen) or len(set(chosen)) != len(chosen):
        raise ValueError("probes must be a unique subset of probe_1 and probe_2")
    return [r for r in build_probe_manifest(config, spec, model_keys)
            if r["probe"] in chosen and (0 if all_seeds else start_seed) <= r["seed_id"] < end]


def allocate_probe_runs(config: dict, spec: dict, runs: list[dict], *, shard_count: int = 1,
                        shard_index: int = 0) -> tuple[list[dict], dict]:
    if (type(shard_count) is not int or shard_count < 1 or type(shard_index) is not int
            or not 0 <= shard_index < shard_count):
        raise ValueError("shard index is zero-based and must be less than a positive shard count")
    if not runs or len({r["run_id"] for r in runs}) != len(runs):
        raise ValueError("allocation requires a nonempty unique run selection")
    canonical = {r["run_id"]: r for r in build_probe_manifest(config, spec)}
    groups: dict[str, list[dict]] = {}
    for run in runs:
        if run["run_id"] not in canonical or digest(run) != digest(canonical[run["run_id"]]):
            raise ValueError("allocation run differs from the configured probe manifest")
        groups.setdefault(run["group_id"], []).append(run)
    for group in groups.values():
        if sorted(r["probe_config"] for r in group) != sorted(PROBE_CONFIGS[group[0]["probe"]]):
            raise ValueError("allocation must contain all three configurations of every group")
    if shard_count > len(groups):
        raise ValueError("shard count exceeds the number of complete groups")
    order = {name: i for configs in PROBE_CONFIGS.values() for i, name in enumerate(configs)}
    # Stratify the round robin by the counterbalancing factors too, so each shard on its own
    # stays close to the 50/50 Parker-role, speaking-order and artist splits.
    ordered = sorted(groups, key=lambda g: (groups[g][0]["model_key"], groups[g][0]["probe"],
                                            groups[g][0]["real_artist"], groups[g][0]["parker_role"],
                                            groups[g][0]["departure_order"][0], groups[g][0]["dna_cell_id"],
                                            groups[g][0]["seed_id"]))
    def members(group_id):
        return sorted(groups[group_id], key=lambda r: order[r["probe_config"]])
    selection = [r for g in ordered for r in members(g)]
    assigned = ordered[shard_index::shard_count]
    selected = [r for g in assigned for r in members(g)]
    allocation = {
        "version": ALLOCATION_VERSION, "config_sha256": digest(config), "probe_spec_sha256": digest(spec),
        "source_selection_sha256": digest(selection), "source_towns": len(selection),
        "source_run_ids": [r["run_id"] for r in selection], "source_groups": len(groups),
        "shard_count": shard_count, "shard_index": shard_index, "group_ids": assigned,
        "run_ids": [r["run_id"] for r in selected], "planned_towns": len(selected),
        "planned_groups": len(assigned), "max_phone_outcomes": 12 * len(selected),
    }
    allocation["allocation_id"] = digest({k: allocation[k] for k in (
        "version", "config_sha256", "probe_spec_sha256", "source_selection_sha256", "shard_count")})
    allocation["shard_sha256"] = digest(allocation)
    return clone(selected), allocation


def probe_plan(config: dict, spec: dict, providers: dict, runs: list[dict],
               allocation: dict | None = None) -> dict:
    if allocation is None:
        ordered, allocation = allocate_probe_runs(config, spec, runs)
        if digest(ordered) != digest(runs):
            raise ValueError("probe run order must match its canonical group allocation")
    else:
        source = {r["run_id"]: r for r in build_probe_manifest(config, spec)}
        ids = allocation.get("source_run_ids")
        if not isinstance(ids, list) or not ids or any(r not in source for r in ids):
            raise ValueError("allocation needs its original configured source run identities")
        assigned, rebuilt = allocate_probe_runs(config, spec, [source[r] for r in ids],
                                                shard_count=allocation.get("shard_count"),
                                                shard_index=allocation.get("shard_index"))
        if digest(assigned) != digest(runs) or digest(rebuilt) != digest(allocation):
            raise ValueError("allocation differs from the deterministic configured probe selection")
    # Reuse the main route gates (approval, model IDs, verified settings and prices) per actor model.
    gates = plan(config, providers, [{"model_key": k, "pair_id": k} for k in sorted({r["model_key"] for r in runs})],
                 include_judge=False)["execution_gates"]
    return {"status": "blocked" if gates else "ready_for_access_validation", "execution_gates": gates,
            "execution_mode": EXECUTION_MODE, "evaluation_status": "pending",
            "planned_towns": len(runs), "planned_groups": len({r["group_id"] for r in runs}),
            "planned_phone_outcomes": 12 * len(runs), "model_keys": sorted({r["model_key"] for r in runs}),
            "primary_judge_key": None, "dna_selection": clone(spec["dna_selection"]),
            "config_sha256": digest(config), "probe_spec_sha256": digest(spec),
            "provider_manifest_sha256": digest(providers), "run_manifest_sha256": digest(runs),
            "runs": runs, "allocation": clone(allocation), "provider_api_calls": 0,
            "study_eligible": False, "spending_authorized_by_planning": False, "api_access_validated": False}


def validate_probe_backend(config: dict, spec: dict, runs: list[dict], backend) -> None:
    """Check both actor request kinds per model before the first paid call."""
    for key in sorted({r["model_key"] for r in runs}):
        run = next(r for r in runs if r["model_key"] == key)
        contexts = render_probe_contexts(config, spec, run)
        for kind, setting_key in (("chat", "conversational_turns"), ("decision", "verification_decision_turns")):
            backend.validate_request(GenerationRequest(
                [{"role": "system", "content": contexts[1]}, {"role": "user", "content": "Preflight validation only."}],
                clone(config["hyperparameters"][setting_key]), key, kind, 2 if kind == "decision" else 3, 1, 1))


def _archive_partial(output: Path, directory: Path) -> str:
    for attempt in itertools.count(1):
        target = output / "_incomplete" / f"attempt-{attempt}" / directory.name
        if not target.exists():
            durable_mkdir(target.parent, exist_ok=True)
            directory.rename(target)
            sync_directory(target.parent)
            sync_directory(directory.parent)
            return target.relative_to(output).as_posix()


def _audit_expected(directory: Path, info: dict, run: dict) -> dict:
    from .probe_artifacts import audit_probe_simulation
    town = audit_probe_simulation(directory)
    for key, expected in (("config_sha256", info["config_sha256"]), ("probe_spec_sha256", info["probe_spec_sha256"]),
                          ("execution_manifest_sha256", info["provider_manifest_sha256"]),
                          ("evidence_kind", info["evidence_kind"])):
        if town.get(key) != expected:
            raise ValueError("saved probe town differs from execution plan: " + key)
    if any(digest(town.get(k)) != digest(v) for k, v in run.items()):
        raise ValueError("saved probe town run differs from execution plan")
    manifest = load_provider_manifest(directory / "manifest.json")
    if manifest.get("source_files_sha256") != info["source_files_sha256"]:
        raise ValueError("saved probe town source differs from the execution plan")
    if (manifest.get("runtime") != info["runtime"]
            or manifest.get("source_runtime_sha256") != info["source_runtime_sha256"]):
        raise ValueError("saved probe town runtime fingerprint differs from the execution plan")
    return town


def read_probe_plan(root: Path) -> dict:
    root = Path(root)
    if any((root / name).is_symlink() for name in ("execution_plan.json", "budget_checkpoint.json")):
        raise ValueError("probe control files cannot be symbolic links")
    info = load_provider_manifest(root / "execution_plan.json")
    if info.get("execution_plan_version") != 1 or info.get("execution_mode") != EXECUTION_MODE:
        raise ValueError("expected a versioned probe simulation execution plan")
    for key, value in (("config_sha256", info["config"]), ("probe_spec_sha256", info["probe_spec"]),
                       ("provider_manifest_sha256", info["provider_manifest"]), ("run_manifest_sha256", info["runs"])):
        if digest(value) != info[key]:
            raise ValueError("probe plan hash mismatch: " + key)
    if info.get("source_runtime_sha256") != digest({"runtime": info.get("runtime"),
                                                    "source_files_sha256": info.get("source_files_sha256")}):
        raise ValueError("probe plan runtime fingerprint mismatch")
    if probe_plan(info["config"], info["probe_spec"], info["provider_manifest"], info["runs"],
                  info["allocation"])["execution_gates"]:
        raise ValueError("saved probe plan has unresolved gates")
    anchor = load_provider_manifest(root / "budget_checkpoint.json")
    if set(anchor) != {"execution_plan_sha256", "ledger_checkpoint"} or anchor["execution_plan_sha256"] != digest(info):
        raise ValueError("probe budget checkpoint does not bind its plan")
    binding, cp = info.get("ledger_binding", {}), anchor["ledger_checkpoint"]
    if (not isinstance(binding, dict) or set(binding) != {"ledger_id", "limit_usd"}
            or not isinstance(binding["ledger_id"], str) or re.fullmatch(r"[0-9a-f]{32}", binding["ledger_id"]) is None
            or not isinstance(binding["limit_usd"], str) or money(binding["limit_usd"]) < 0
            or not isinstance(cp, dict) or set(cp) != {"ledger_id", "limit_usd", "event_count", "history_sha256"}
            or type(cp["event_count"]) is not int or cp["event_count"] < 1
            or not isinstance(cp["history_sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", cp["history_sha256"]) is None
            or any(cp.get(k) != v for k, v in binding.items())):
        raise ValueError("probe plan needs a valid original ledger binding and checkpoint")
    allocation = info["allocation"]
    if allocation["run_ids"] != [r["run_id"] for r in info["runs"]]:
        raise ValueError("allocation run identities differ from execution plan")
    if digest({k: v for k, v in allocation.items() if k != "shard_sha256"}) != allocation["shard_sha256"]:
        raise ValueError("allocation hash mismatch")
    return info


def review_probe_simulations(roots: Path | list[Path]) -> dict[str, Any]:
    """Read sealed probe towns across shards without producing or consuming any judge scores."""
    from .artifacts import archived_attempt_paths
    roots = [roots] if isinstance(roots, (str, Path)) else roots
    if not roots:
        raise ValueError("at least one probe collection is required")
    roots = [Path(p).resolve() for p in roots]
    if len(set(roots)) != len(roots):
        raise ValueError("duplicate probe collection")
    files, configs, specs, kinds, selections = None, set(), set(), set(), set()
    routes, runtimes, allocated, markers, seen = {}, {}, set(), set(), set()
    town_count = completed_count = phone_count = 0
    group_counts, usage_total = Counter(), {}
    failed_by_config, failed_by_status, reports, source_total = Counter(), Counter(), [], None
    for root in roots:
        info = read_probe_plan(root)
        configs.add(info["config_sha256"])
        specs.add(info["probe_spec_sha256"])
        kinds.add(info["evidence_kind"])
        runtimes[digest(info["runtime"])] = info["runtime"]
        if files is None:
            files = info["source_files_sha256"]
        elif files != info["source_files_sha256"]:
            raise ValueError("probe shards use different source versions")
        expected = {r["run_id"]: r for r in info["runs"]}
        if allocated.intersection(expected):
            raise ValueError("probe allocations overlap: " + sorted(allocated.intersection(expected))[0])
        allocated.update(expected)
        allocation = info["allocation"]
        selections.add(allocation["allocation_id"])
        marker = (allocation["allocation_id"], allocation["shard_index"])
        if marker in markers:
            raise ValueError("duplicate allocation shard")
        markers.add(marker)
        source_total = allocation["source_towns"]
        for model in {r["model_key"] for r in info["runs"]}:
            route = {k: v for k, v in info["provider_manifest"]["routes"][model].items() if k != "api_key_env"}
            if model in routes and routes[model] != route:
                raise ValueError("actor route differs across shards: " + model)
            routes[model] = route
        present, completed = set(), set()
        for path in sorted(root.iterdir()):
            if path.is_symlink():
                raise ValueError("probe collection contains a symbolic link")
            if not path.is_dir() or path.name == "_incomplete":
                continue
            if path.name not in expected:
                raise ValueError("unplanned probe directory: " + path.name)
            town = _audit_expected(path, info, expected[path.name])
            present.add(path.name)
            if path.name in seen:
                raise ValueError("duplicate completed probe identity")
            seen.add(path.name)
            town_count += 1
            if town["generation_status"] == "completed":
                completed.add(path.name)
                completed_count += 1
                group_counts[town["group_id"]] += 1
                phone_count += len(town["scene_5_phone_transcripts"])
            else:
                failed_by_config[town["probe_config"]] += 1
                failed_by_status[town["run_status"]] += 1
            for key, value in usage_totals(town["calls"], town["evidence_kind"]).items():
                if key == "cost_status":
                    continue
                if key not in usage_total:
                    usage_total[key] = None if value is None else Decimal(str(value))
                elif usage_total[key] is None or value is None:
                    usage_total[key] = None
                else:
                    usage_total[key] += Decimal(str(value))
        archived = archived_attempt_paths(root)
        for path in archived:
            if path.name not in expected or path.is_symlink():
                raise ValueError("unplanned archived probe attempt")
            past = _audit_expected(path, info, expected[path.name])
            if past["generation_status"] != "completed":
                failed_by_config[past["probe_config"]] += 1
                failed_by_status[past["run_status"]] += 1
        reports.append({"root": str(root), "planned_towns": len(expected), "completed_towns": len(completed),
                        "missing_run_ids": sorted(set(expected) - present),
                        "incomplete_run_ids": sorted(present - completed), "archived_attempts": len(archived),
                        "ledger_binding": info["ledger_binding"], "billing_verified": False,
                        "execution_plan_sha256": digest(info), "allocation_shard_index": allocation["shard_index"]})
    if len(configs) != 1 or len(specs) != 1 or len(kinds) != 1 or len(selections) != 1:
        raise ValueError("probe shards have incompatible config, spec, evidence or allocation")
    usage = {k: None if v is None else float(v) if k == "cost_usd" else int(v) for k, v in usage_total.items()}
    if next(iter(kinds)) != "synthetic_fixture":
        usage["cost_status"] = "known" if usage.get("cost_usd") is not None else "unknown"
    full = source_total is not None and len(allocated) == source_total
    status = ("generation_incomplete" if completed_count != len(allocated)
              else "generation_complete" if full else "shards_complete")
    return {"status": status, "execution_mode": EXECUTION_MODE, "evidence_kind": next(iter(kinds)),
            "study_eligible": False, "study_results_generated": False, "evaluation_status": "pending",
            "towns": town_count, "completed_towns": completed_count,
            "completed_groups": sum(n == 3 for n in group_counts.values()),
            "partial_group_ids": sorted(g for g, n in group_counts.items() if n != 3),
            "planned_towns": len(allocated), "source_selection_towns": source_total,
            "full_allocation_present": full, "phone_transcripts": phone_count,
            "failed_generation_attempts": sum(failed_by_config.values()),
            "failed_generation_attempts_by_config": dict(sorted(failed_by_config.items())),
            "failed_generation_attempts_by_status": dict(sorted(failed_by_status.items())),
            "judge_calls": 0, "metrics_available": False, "collections": reports,
            "runtime_profiles": [runtimes[k] for k in sorted(runtimes)], "runtime_variation": len(runtimes) > 1,
            "current_attempt_usage": usage}


async def collect_probe_simulations(config: dict, spec: dict, providers: dict, runs: list[dict], output: Path,
                                    backend, *, allocation: dict | None = None, resume: bool = False,
                                    max_concurrent_towns: int = 1, execution_authorized: bool = False,
                                    spending_authorized: bool = False, regenerate_failed: bool = False) -> dict:
    from .artifacts import archived_attempt_paths
    from .probe_runner import run_probe_town
    if execution_authorized is not True or spending_authorized is not True:
        raise ValueError("probe execution and spending authorization are required; hold remains")
    if type(regenerate_failed) is not bool:
        raise ValueError("regenerate_failed must be a boolean")
    output = Path(output)
    if type(max_concurrent_towns) is not int or not 1 <= max_concurrent_towns <= 16:
        raise ValueError("max-concurrent-towns must be an integer from 1 to 16")
    allocate_probe_runs(config, spec, runs)  # Even direct callers need complete configured groups.
    if output.exists() and not resume:
        raise FileExistsError("refusing existing probe directory; use resume")
    if resume and not (output / "execution_plan.json").is_file():
        raise ValueError("nothing to resume: no probe execution plan")
    if digest(providers) != digest(backend.manifest):
        raise ValueError("backend manifest differs from the approved probe plan")
    info = probe_plan(config, spec, providers, runs, allocation)
    if info["execution_gates"]:
        raise ValueError("; ".join(info["execution_gates"]))
    ledger = backend.ledger
    checkpoint = ledger.checkpoint()
    binding = {key: checkpoint[key] for key in ("ledger_id", "limit_usd")}
    info.update(execution_plan_version=1, evidence_kind=backend.evidence_kind, ledger_binding=binding,
                config=clone(config), probe_spec=clone(spec), provider_manifest=clone(providers),
                source_files_sha256=probe_source_hashes(), runtime=_runtime())
    info["source_runtime_sha256"] = digest({"runtime": info["runtime"], "source_files_sha256": info["source_files_sha256"]})
    if resume:
        saved = read_probe_plan(output)
        if digest(saved) != digest(info):
            raise ValueError("resume requires the exact original plan, source version, ledger identity and cap")
        ledger.verify_checkpoint(load_provider_manifest(output / "budget_checkpoint.json")["ledger_checkpoint"])
    if ledger.summary()["blocked"]:
        raise ValueError("budget ledger is blocked; reconcile original unknown charges first")
    expected = {r["run_id"]: r for r in runs}
    for path in sorted(output.iterdir()) if resume else []:
        if path.is_symlink():
            raise ValueError("probe collection contains a symbolic link")
        if path.is_dir() and path.name != "_incomplete" and path.name not in expected:
            raise ValueError("unplanned probe directory")
    archived_failed = set()
    for path in archived_attempt_paths(output) if resume else []:
        if path.name not in expected or path.is_symlink():
            raise ValueError("unplanned archived probe attempt")
        if _audit_expected(path, info, expected[path.name])["generation_status"] != "completed":
            archived_failed.add(path.name)
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
    regenerated = sorted({p.name for p in partial} | (archived_failed & {r["run_id"] for r in pending}))
    if regenerated and not regenerate_failed:
        raise ValueError(f"{len(regenerated)} sealed failed generation(s), e.g. {regenerated[0]}; "
                         "rerun them only with explicit regenerate_failed (--regenerate-failed)")
    if pending:
        validate_probe_backend(config, spec, pending, backend)
        backend.validate_credentials(sorted({r["model_key"] for r in pending}))
    if not resume:
        durable_mkdir(output, exist_ok=False)
        _atomic_json(output / "execution_plan.json", info)
    plan_hash = digest(info)
    def anchor(value):
        _atomic_json(output / "budget_checkpoint.json", {"execution_plan_sha256": plan_hash, "ledger_checkpoint": value})
    anchor(ledger.checkpoint())
    set_aside = [_archive_partial(output, path) for path in partial]
    if resume:
        with (output / "resume_log.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"resumed_utc": datetime.now(timezone.utc).isoformat(), "skipped_run_ids": skipped,
                                     "archived": set_aside, "regenerate_failed": regenerate_failed,
                                     "regenerated_run_ids": regenerated, "pending_towns": len(pending)}) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        sync_directory(output)
    queue, failures = list(pending), []
    async def worker():
        while queue and not failures:
            run = queue.pop(0)
            try:
                town = await run_probe_town(config, spec, run, backend, output)
                if town["generation_status"] != "completed":
                    raise ValueError(INCOMPLETE + run["run_id"])
            except Exception as error:
                failures.append(error)
    ledger.set_checkpoint_callback(anchor)
    try:
        await asyncio.gather(*(worker() for _ in range(max(1, min(max_concurrent_towns, len(pending))))))
    finally:
        ledger.set_checkpoint_callback(None)
    if failures:
        raise failures[0]
    return {**review_probe_simulations(output), "output_root": str(output), "resumed": resume,
            "skipped_verified_towns": len(skipped), "set_aside_towns": set_aside,
            "budget_accounting": {"scope": "entire_original_bound_ledger", "billing_verified": False,
                                  "ledger_id": binding["ledger_id"], "budget": ledger.summary()}}
