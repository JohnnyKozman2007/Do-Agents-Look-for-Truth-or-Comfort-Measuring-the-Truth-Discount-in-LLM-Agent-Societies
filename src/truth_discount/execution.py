"""Plan and gate bounded development collection without changing the study."""
from __future__ import annotations

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


async def collect(config: dict, providers: dict, runs: list[dict], output: Path,
                  backend) -> dict:
    from .artifacts import summarize
    from .runner import run_town
    if output.exists():
        raise FileExistsError("refusing existing output directory")
    if digest(providers) != digest(backend.manifest):
        raise ValueError("backend manifest differs from the approved execution plan")
    info = plan(config, providers, runs)
    if info["execution_gates"]:
        raise ValueError("; ".join(info["execution_gates"]))
    validate_backend(config, runs, backend)
    needed = sorted({r["model_key"] for r in runs} | {info["primary_judge_key"]})
    backend.validate_credentials(needed)
    output.mkdir(parents=True, exist_ok=False)
    (output / "execution_plan.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    for run in runs:
        town = await run_town(config, run, backend, output)
        if town["run_status"] != "completed":
            raise ValueError("collection stopped after incomplete town: " + run["run_id"])
    return {**summarize(output), "output_root": str(output),
            "execution_plan_sha256": digest(info), "study_eligible": False}
