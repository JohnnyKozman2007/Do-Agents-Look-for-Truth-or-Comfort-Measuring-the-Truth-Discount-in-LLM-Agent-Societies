"""Plan and gate bounded development collection without changing the study."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import itertools
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from .config import build_manifest, render_contexts
from .contracts import GenerationRequest, clone, digest


def load_provider_manifest(path: Path) -> dict[str, Any]:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate provider manifest key")
            result[key] = value
        return result
    result = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(result, dict):
        raise ValueError("provider manifest must be an object")
    return clone(result)


def select_runs(config: dict, model_keys: list[str] | None = None,
                pairs_per_cell: int = 1, full_pilot: bool = False,
                start_pair: int = 0) -> list[dict]:
    if type(pairs_per_cell) is not int or not 1 <= pairs_per_cell <= 39:
        raise ValueError("pairs-per-cell must be an integer from 1 to 39")
    if type(start_pair) is not int or not 0 <= start_pair <= 38:
        raise ValueError("start-pair must be an integer from 0 to 38")
    end = 39 if full_pilot else start_pair + pairs_per_cell
    if end > 39:
        raise ValueError("pair range exceeds the configured 39 pairs per cell")
    runs = build_manifest(config, model_keys)
    # The prefix is declared before collection and contains both twins.
    return [run for run in runs if start_pair <= run["seed_id"] < end]


def plan(config: dict, providers: dict, runs: list[dict]) -> dict:
    configured = {x["key"]: x for x in config["models"]["agent_models"]}
    judge = config["models"]["judge_models"][0]
    configured[judge["key"]] = judge
    needed = sorted({r["model_key"] for r in runs} | {judge["key"]})
    errors = []
    if providers.get("version") != 1:
        errors.append("unsupported provider manifest version")
    if providers.get("approved") is not True:
        errors.append("execution manifest needs explicit team approval")
    routes = providers.get("routes", {})
    if not isinstance(routes, dict):
        raise ValueError("provider routes must be an object")
    for key in needed:
        route = routes.get(key)
        if not isinstance(route, dict):
            errors.append("missing route: " + key)
            continue
        expected = configured[key]
        if route.get("model_id") != expected["model_id"]:
            errors.append("route changes configured model: " + key)
        if str(route.get("provider", "")).lower() != expected["provider"].lower():
            errors.append("route changes configured provider: " + key)
        for gate in ("settings_verified", "pricing_verified"):
            if route.get(gate) is not True:
                errors.append(f"{key} needs {gate}")
    if (config["hyperparameters"]["blind_judge_turns"].get("use_batch_api")
            and not routes.get(judge["key"], {}).get("allow_synchronous_judge")):
        errors.append("judge batch setting requires explicit approval of synchronous pilot override")
    return {"status": "blocked" if errors else "ready_for_access_validation",
            "execution_gates": errors, "planned_towns": len(runs),
            "planned_pairs": len({r["pair_id"] for r in runs}),
            "model_keys": sorted({r["model_key"] for r in runs}),
            "primary_judge_key": judge["key"], "config_sha256": digest(config),
            "provider_manifest_sha256": digest(providers), "run_manifest_sha256": digest(runs),
            "runs": runs, "provider_api_calls": 0,
            "study_eligible": False, "spending_authorized_by_planning": False,
            "api_access_validated": False}


def validate_backend(config: dict, runs: list[dict], backend) -> None:
    """Check all request kinds before the first paid call, including the judge."""
    judge = config["models"]["judge_models"][0]["key"]
    for key in sorted({r["model_key"] for r in runs}):
        run = next(r for r in runs if r["model_key"] == key)
        contexts = render_contexts(config, run)
        for kind, setting_key in [("chat", "conversational_turns"),
                                  ("decision", "verification_decision_turns")]:
            request = GenerationRequest([{"role": "system", "content": contexts[1]},
                                         {"role": "user", "content": "Preflight validation only."}],
                                        clone(config["hyperparameters"][setting_key]), key,
                                        kind, 2 if kind == "decision" else 3, 1, 1)
            backend.validate_request(request)
    backend.validate_request(GenerationRequest(
        [{"role": "user", "content": "Preflight validation only."}],
        clone(config["hyperparameters"]["blind_judge_turns"]), judge, "judge", 5, 1, 0))


def _set_aside(output: Path, directory: Path) -> str:
    """Keep a partial or unverifiable town for reconciliation; paid evidence is never deleted."""
    for attempt in itertools.count(1):
        target = output / "_incomplete" / f"attempt-{attempt}" / directory.name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            directory.rename(target)
            return target.relative_to(output).as_posix()


def _atomic_json(path: Path, value: dict) -> None:
    """Durably replace a small state file before allowing another paid request."""
    temporary = None
    try:
        descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        if os.name != "nt":
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)


def _audit_expected(directory: Path, config: dict, providers: dict, run: dict,
                    evidence_kind: str) -> dict:
    """Replay a saved attempt and bind it to this plan, not just its own config."""
    from .artifacts import audit_town
    try:
        town = audit_town(directory)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError("saved town cannot be verified; preserve it for review: " + str(directory)) from error
    if town.get("config_sha256") != digest(config):
        raise ValueError("saved town config differs from execution plan: " + directory.name)
    if town.get("execution_manifest_sha256") != digest(providers):
        raise ValueError("saved town provider manifest differs from execution plan: " + directory.name)
    if town.get("evidence_kind") != evidence_kind:
        raise ValueError("saved town evidence kind differs from execution plan: " + directory.name)
    if any(digest(town.get(key)) != digest(value) for key, value in run.items()):
        raise ValueError("saved town run mapping differs from execution plan: " + directory.name)
    return town


async def collect(config: dict, providers: dict, runs: list[dict], output: Path,
                  backend, *, resume: bool = False, max_concurrent_towns: int = 1) -> dict:
    from .artifacts import archived_attempt_paths, summarize
    from .runner import run_town
    if type(max_concurrent_towns) is not int or not 1 <= max_concurrent_towns <= 16:
        raise ValueError("max-concurrent-towns must be an integer from 1 to 16")
    if output.exists() and not resume:
        raise FileExistsError("refusing existing output directory; resume continues it")
    if resume and not (output / "execution_plan.json").is_file():
        raise ValueError("nothing to resume: the output has no execution plan")
    if digest(providers) != digest(backend.manifest):
        raise ValueError("backend manifest differs from the approved execution plan")
    info = plan(config, providers, runs)
    if info["execution_gates"]:
        raise ValueError("; ".join(info["execution_gates"]))
    ledger = backend.ledger
    current_checkpoint = ledger.checkpoint()
    evidence_kind = backend.evidence_kind
    binding = {key: current_checkpoint[key] for key in ("ledger_id", "limit_usd")}
    info.update(execution_plan_version=2, evidence_kind=evidence_kind, ledger_binding=binding)
    if resume:
        saved = load_provider_manifest(output / "execution_plan.json")
        if saved.get("execution_plan_version") != 2 or saved.get("ledger_binding") != binding:
            raise ValueError("resume requires the original ledger identity and fixed cap; legacy unbound plans need review")
        for key in ("config_sha256", "provider_manifest_sha256", "run_manifest_sha256"):
            if saved.get(key) != info[key]:
                raise ValueError("resume needs the same plan; changed: " + key)
        if digest(saved) != digest(info):
            raise ValueError("resume execution plan differs from the approved selection or evidence kind")
        anchor = load_provider_manifest(output / "budget_checkpoint.json")
        if set(anchor) != {"execution_plan_sha256", "ledger_checkpoint"} or anchor["execution_plan_sha256"] != digest(info):
            raise ValueError("resume budget checkpoint belongs to a different execution plan")
        ledger.verify_checkpoint(anchor["ledger_checkpoint"])
    if ledger.summary()["blocked"]:
        raise ValueError("budget ledger is blocked (" + ", ".join(ledger.summary()["block_reasons"])
                         + "); record billed amounts with `truth-discount ledger --reconcile` first")
    expected = {run["run_id"]: run for run in runs}
    if len(expected) != len(runs):
        raise ValueError("run selection contains duplicate town identities")
    pending, skipped, partial = [], [], []
    # Validate every saved attempt before moving files, reading keys or starting work.
    for directory in sorted(output.glob("*/")) if resume else []:
        if directory.name == "_incomplete":
            continue
        if directory.name not in expected:
            raise ValueError("unexpected saved town outside the execution plan: " + directory.name)
    for directory in archived_attempt_paths(output) if resume else []:
        if not directory.is_dir() or directory.name not in expected:
            raise ValueError("unexpected archived attempt outside the execution plan")
        _audit_expected(directory, config, providers, expected[directory.name], evidence_kind)
    for run in runs:
        directory = output / run["run_id"]
        if not directory.exists():
            pending.append(run)
        elif _audit_expected(directory, config, providers, run, evidence_kind)["run_status"] == "completed":
            skipped.append(run["run_id"])
        else:
            partial.append(directory)
            pending.append(run)
    validate_backend(config, runs, backend)
    needed = sorted({r["model_key"] for r in runs} | {info["primary_judge_key"]})
    backend.validate_credentials(needed)
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
        _atomic_json(output / "execution_plan.json", info)
    plan_hash = digest(info)
    def anchor_checkpoint(checkpoint):
        _atomic_json(output / "budget_checkpoint.json", {
            "execution_plan_sha256": plan_hash, "ledger_checkpoint": checkpoint})
    # Each reserve/settle is anchored before the next request can proceed. A
    # same-ID journal rewound behind that prefix is rejected after a hard crash.
    anchor_checkpoint(ledger.checkpoint())
    set_aside = [_set_aside(output, directory) for directory in partial]
    if resume:
        with (output / "resume_log.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps({"resumed_utc": datetime.now(timezone.utc).isoformat(),
                                  "skipped_verified_towns": len(skipped), "set_aside": set_aside,
                                  "pending_towns": len(pending)}) + "\n")
    # Towns share one backend, so one ledger and one per-route request limit.
    # After any failure no new town starts; towns already running finish and save.
    queue, failures = list(pending), []

    async def worker():
        while queue and not failures:
            run = queue.pop(0)
            try:
                town = await run_town(config, run, backend, output)
            except Exception as error:
                failures.append((run["run_id"], error))
                return
            if town["run_status"] != "completed":
                failures.append((run["run_id"], None))
                return

    ledger.set_checkpoint_callback(anchor_checkpoint)
    try:
        await asyncio.gather(*(worker() for _ in range(max(1, min(max_concurrent_towns, len(pending))))))
    finally:
        ledger.set_checkpoint_callback(None)
    if failures:
        run_id, error = failures[0]
        if error is not None:
            raise error
        raise ValueError("collection stopped after incomplete town: " + run_id)
    return {**summarize(output), "output_root": str(output),
            "execution_plan_sha256": plan_hash, "study_eligible": False,
            "budget_accounting": {"scope": "entire_bound_ledger_including_prior_attempts_and_batches",
                                  "evidence_kind": evidence_kind, "billing_verified": False,
                                  "ledger_id": binding["ledger_id"], "budget": ledger.summary()},
            "resumed": resume, "skipped_verified_towns": len(skipped), "set_aside_towns": set_aside}
