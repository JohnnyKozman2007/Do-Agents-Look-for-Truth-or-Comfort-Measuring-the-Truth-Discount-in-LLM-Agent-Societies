"""Plan and gate bounded development collection without changing the study."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
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


def _verified_complete(directory: Path) -> bool:
    from .artifacts import InvalidBundle, audit_town
    try:
        return audit_town(directory)["run_status"] == "completed"
    except (InvalidBundle, OSError, ValueError):
        return False


async def collect(config: dict, providers: dict, runs: list[dict], output: Path,
                  backend, *, resume: bool = False, max_concurrent_towns: int = 1) -> dict:
    from .artifacts import summarize
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
    if resume:
        saved = json.loads((output / "execution_plan.json").read_text(encoding="utf-8"))
        for key in ("config_sha256", "provider_manifest_sha256", "run_manifest_sha256"):
            if saved.get(key) != info[key]:
                raise ValueError("resume needs the same plan; changed: " + key)
    validate_backend(config, runs, backend)
    needed = sorted({r["model_key"] for r in runs} | {info["primary_judge_key"]})
    backend.validate_credentials(needed)
    ledger = getattr(backend, "ledger", None)
    if ledger is not None and ledger.summary()["blocked"]:
        raise ValueError("budget ledger is blocked (" + ", ".join(ledger.summary()["block_reasons"])
                         + "); record billed amounts with `truth-discount ledger --reconcile` first")
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
        (output / "execution_plan.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    pending, skipped, set_aside = [], [], []
    for run in runs:
        directory = output / run["run_id"]
        if not directory.exists():
            pending.append(run)
        elif _verified_complete(directory):
            skipped.append(run["run_id"])
        else:
            set_aside.append(_set_aside(output, directory))
            pending.append(run)
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

    await asyncio.gather(*(worker() for _ in range(max(1, min(max_concurrent_towns, len(pending))))))
    if failures:
        run_id, error = failures[0]
        if error is not None:
            raise error
        raise ValueError("collection stopped after incomplete town: " + run_id)
    return {**summarize(output), "output_root": str(output),
            "execution_plan_sha256": digest(info), "study_eligible": False,
            "resumed": resume, "skipped_verified_towns": len(skipped), "set_aside_towns": set_aside}
