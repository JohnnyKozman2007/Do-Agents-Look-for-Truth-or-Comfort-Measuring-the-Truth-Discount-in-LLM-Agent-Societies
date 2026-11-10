"""Offline pilot planning, synthetic demonstrations, and saved-bundle replay."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys

from .artifacts import summarize
from .config import build_manifest, load_config
from .contracts import canonical_bytes
from .fixtures import FixtureBackend
from .runner import run_town


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "pilot_config.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="truth-discount",
        description="Plan the pilot, replay fixtures, or explicitly authorize bounded development calls.",
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG,
        help="pilot JSON for validate, manifest, or demo; summarize uses each saved bundle's config",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate the pilot config and planned run count")
    manifest = commands.add_parser("manifest", help="write the full 624-town plan as JSONL")
    manifest.add_argument("--output", type=Path, required=True, help="new JSONL file; existing paths are refused")
    demo = commands.add_parser("demo", help="save one synthetic twin pair per model (four towns)")
    demo.add_argument("--output", type=Path, required=True, help="new output directory; existing paths are refused")
    demo.add_argument("--mode", choices=("mixed", "all_skip", "silent"), default="mixed")
    replay = commands.add_parser("summarize", help="audit and summarize saved synthetic bundles")
    replay.add_argument("output_root", type=Path, help="directory containing the saved town directories")
    live = commands.add_parser("live", help="preview development collection; network requires two explicit flags")
    live.add_argument("--providers", type=Path, required=True)
    live.add_argument("--output", type=Path, required=True)
    live.add_argument("--ledger", type=Path, help="durable account budget ledger, required for execution")
    live.add_argument("--budget-usd", type=str, help="explicit overall ledger ceiling, required for execution")
    live.add_argument("--model-key", action="append", dest="model_keys")
    live.add_argument("--pairs-per-cell", type=int, default=1)
    live.add_argument("--start-pair", type=int, default=0,
                      help="declared disjoint pair range, 0..38; not automatic resume")
    live.add_argument("--full-pilot", action="store_true")
    live.add_argument("--execute", action="store_true")
    live.add_argument("--spending-authorized", action="store_true",
                      help="use only after Ahmed explicitly releases the credit-use hold")
    live.add_argument("--resume", action="store_true",
                      help="continue an existing output: skip verified completed towns, set partial ones aside")
    live.add_argument("--max-concurrent-towns", type=int, default=1,
                      help="towns run at once (1-16); route max_concurrent_requests still caps requests")
    ledger = commands.add_parser("ledger", help="show a budget ledger's unknown charges or reconcile one")
    ledger.add_argument("--ledger", type=Path, required=True)
    ledger.add_argument("--budget-usd", type=str, required=True, help="the ledger's fixed ceiling")
    ledger.add_argument("--reconcile", metavar="RESERVATION_ID",
                        help="record the billed amount for one unknown charge")
    ledger.add_argument("--actual-usd", type=str, help="billed amount from the provider's usage records")
    ledger.add_argument("--note", type=str, help="where the billed amount came from")
    analyze = commands.add_parser("analyze", help="per-cell truth discount, sensitivity bounds and model fits")
    analyze.add_argument("output_root", type=Path, help="directory containing the saved town directories")
    analyze.add_argument("--out", type=Path, required=True, help="new directory for tables, report and chart")
    review = commands.add_parser("review-collection", help="read-only saved-plan coverage and receipt review")
    review.add_argument("output_root", type=Path, help="finished collection snapshot, including archived attempts")
    review.add_argument("--out", type=Path, required=True, help="new review directory outside the collection")
    review.add_argument("--ledger-copy", type=Path,
                        help="optional saved journal copy; inspected through another temporary copy only")
    sample = commands.add_parser("audit-sample", help="stratified blind sample for the human judge audit")
    sample.add_argument("output_root", type=Path)
    sample.add_argument("--out", type=Path, required=True, help="new directory for the sheet and private key")
    sample.add_argument("--size", type=int, default=100)
    sample.add_argument("--seed", type=int, default=2027)
    validation = commands.add_parser("prepare-judge-validation",
                                     help="offline inventory and blind calibration sample of every phone-call path")
    validation.add_argument("output_root", type=Path, help="finished saved collection snapshot")
    validation.add_argument("--out", type=Path, required=True, help="new directory outside the collection")
    validation.add_argument("--size", type=int, default=100)
    validation.add_argument("--seed", type=int, default=20261108)
    score = commands.add_parser("audit-score", help="Cohen's kappa of human labels against the judge")
    score.add_argument("audit_dir", type=Path, help="directory written by audit-sample")
    score.add_argument("sheets", type=Path, nargs="+", help="one filled labeling sheet per rater")
    rejudge = commands.add_parser("rejudge", help="re-ask the judge for malformed labels; preview without --execute")
    rejudge.add_argument("output_root", type=Path, help="a finished collection directory")
    rejudge.add_argument("--providers", type=Path, help="approved provider manifest, required for execution")
    rejudge.add_argument("--ledger", type=Path, help="the same budget ledger as the collection")
    rejudge.add_argument("--budget-usd", type=str, help="that ledger's fixed ceiling")
    rejudge.add_argument("--attempts", type=int, default=3, help="tries per malformed call (1-5)")
    rejudge.add_argument("--execute", action="store_true")
    rejudge.add_argument("--spending-authorized", action="store_true")
    simulation = commands.add_parser("simulate", help="preview or explicitly authorize generation without a judge")
    simulation.add_argument("--providers", type=Path, required=True, help="approved actor routes; no judge key needed")
    simulation.add_argument("--output", type=Path, required=True)
    simulation.add_argument("--model-key", action="append", dest="model_keys")
    simulation.add_argument("--pairs-per-cell", type=int, default=1)
    simulation.add_argument("--start-pair", type=int, default=0)
    simulation.add_argument("--all-pairs", action="store_true", help="all39 pairs per configured cell")
    simulation.add_argument("--shard-count", type=int, default=1)
    simulation.add_argument("--shard-index", type=int, default=0, help="zero-based owner index, 0..shard-count-1")
    simulation.add_argument("--ledger", type=Path)
    simulation.add_argument("--budget-usd", type=str, help="this shard ledger's fixed allocation, not the project total")
    simulation.add_argument("--resume", action="store_true")
    simulation.add_argument("--max-concurrent-towns", type=int, default=1)
    simulation.add_argument("--execute", action="store_true")
    simulation.add_argument("--spending-authorized", action="store_true",
                            help="only after the separate credit-use hold is explicitly released")
    simulation.add_argument("--plan-out", type=Path, help="save the zero-call allocation plan to a new JSON file")
    simulation_demo = commands.add_parser("simulation-demo", help="four synthetic actor-only towns, zero network")
    simulation_demo.add_argument("--output", type=Path, required=True)
    simulation_demo.add_argument("--mode", choices=("mixed", "all_skip", "silent"), default="mixed")
    simulation_status = commands.add_parser("simulation-status", help="read-only replay and coverage across allocated shards")
    simulation_status.add_argument("source_roots", type=Path, nargs="+")
    judging = commands.add_parser("judge-saved", help="preview or separately authorize scoring sealed transcripts")
    judging.add_argument("source_roots", type=Path, nargs="+")
    judging.add_argument("--profile", type=Path, required=True)
    judging.add_argument("--output", type=Path, required=True)
    judging.add_argument("--ledger", type=Path)
    judging.add_argument("--budget-usd", type=str)
    judging.add_argument("--resume", action="store_true")
    judging.add_argument("--retry-invalid", action="store_true", help="explicit repair; first and latest results stay separate")
    judging.add_argument("--retry-failed", action="store_true", help="retry only after original unknown costs are reconciled")
    judging.add_argument("--execute", action="store_true")
    judging.add_argument("--spending-authorized", action="store_true")
    judge_status = commands.add_parser("judge-status", help="read-only source-bound scoring replay")
    judge_status.add_argument("source_roots", type=Path, nargs="+")
    judge_status.add_argument("--output", type=Path, required=True)
    judge_status.add_argument("--profile", type=Path, required=True)
    compare_judges = commands.add_parser("compare-judges", help="compare source-matched first judgments; not human accuracy")
    compare_judges.add_argument("source_roots", type=Path, nargs="+")
    compare_judges.add_argument("--profile", type=Path, action="append", required=True,
                               help="repeat once per judge, in the same order as --judge-output")
    compare_judges.add_argument("--judge-output", type=Path, action="append", required=True)
    panel = commands.add_parser("prepare-panel-judging", help="bind the exact blind human cases to an unapproved judge profile")
    panel.add_argument("source_roots", type=Path, nargs="+")
    panel.add_argument("--profile", type=Path, required=True)
    panel.add_argument("--profile-id", required=True, help="new distinct candidate ID")
    panel.add_argument("--panel", type=Path, required=True, help="existing blind human_labeling.csv; labels are ignored")
    panel.add_argument("--source-format", choices=("simulation", "legacy_pilot"))
    panel.add_argument("--population", choices=("historical_funnel", "all_phones"))
    panel.add_argument("--out", type=Path, required=True, help="new local candidate JSON; approval remains false")
    # Accept --config before or after a planning/demo subcommand without resetting
    # a global value when the subcommand option is absent.
    for command in (validate, manifest, demo, live, simulation, simulation_demo):
        command.add_argument("--config", type=Path, default=argparse.SUPPRESS, help="explicit pilot JSON path")
    return parser


def _print_json(value: dict) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))


async def _demo(config: dict, manifest: list[dict], output_root: Path, mode: str) -> dict:
    # Every model uses the same first configured world. Select entire pairs, never
    # take a slice that could leave a lone rumor or truth condition.
    runs = [run for run in manifest if run["cell_id"] == 1
            and run["layout_id"] == 0 and run["repetition_id"] == 0]
    if output_root.exists():
        raise FileExistsError(f"refusing existing output directory: {output_root}")
    output_root.mkdir(parents=True, exist_ok=False)
    for run in runs:
        town = await run_town(config, run, FixtureBackend(mode=mode), output_root)
        if town["run_status"] != "completed":
            raise ValueError(f"Fixture town did not complete: {town['run_id']} ({town['run_status']})")
    summary = summarize(output_root)
    return {**summary, "fixture_mode": mode, "output_root": str(output_root),
            "selected_cell_id": 1, "selected_layout_id": 0, "selected_repetition_id": 0}


def main(argv: list[str] | None = None) -> int:
    """Run the CLI; return 0 on success and 1 on config, output, or replay errors.

    argparse retains exit status 2 for invalid command-line arguments. Output is
    JSON on stdout, with errors on stderr. No environment credentials are read.
    """
    args = _parser().parse_args(argv)
    try:
        if args.command == "prepare-panel-judging":
            from .deferred_judging import load_judge_profile
            from .judge_selection import panel_profile
            if any(Path(root).resolve() in args.out.resolve().parents for root in args.source_roots):
                raise ValueError("candidate profile output must be outside the immutable source roots")
            profile = load_judge_profile(args.profile)
            if args.source_format:
                profile["source_format"] = args.source_format
            if args.population:
                profile["population"] = args.population
            candidate, report = panel_profile(args.source_roots, profile, args.panel, args.profile_id)
            with args.out.open("xb") as stream:
                stream.write(canonical_bytes(candidate))
            _print_json({**report, "profile_output": str(args.out)})
            return 0
        if args.command == "simulation-status":
            from .simulation_execution import review_simulations
            _print_json(review_simulations(args.source_roots))
            return 0
        if args.command == "compare-judges":
            from .deferred_judging import load_judge_profile, compare_judgments
            if len(args.profile) != len(args.judge_output):
                raise ValueError("supply one --judge-output for each --profile")
            selected = [(output, load_judge_profile(profile))
                        for output, profile in zip(args.judge_output, args.profile)]
            _print_json(compare_judgments(args.source_roots, selected))
            return 0
        if args.command in {"judge-saved", "judge-status"}:
            from .deferred_judging import (load_judge_profile, plan_judging,
                                           judge_collection, replay_judging)
            profile = load_judge_profile(args.profile)
            if args.command == "judge-status":
                _print_json(replay_judging(args.source_roots, args.output, profile))
                return 0
            info = plan_judging(args.source_roots, profile)
            if not args.execute:
                _print_json(info)
                return 0
            if not args.spending_authorized:
                raise ValueError("judging requires explicit release of the separate spending hold")
            if not args.ledger or not args.budget_usd:
                raise ValueError("judging requires --ledger and --budget-usd")
            from .budget import BudgetLedger
            from .providers import ProviderBackend
            with BudgetLedger(args.ledger, args.budget_usd) as ledger:
                backend = ProviderBackend(profile["provider_manifest"], ledger)
                result = asyncio.run(judge_collection(
                    args.source_roots, args.output, profile, backend, resume=args.resume,
                    retry_invalid=args.retry_invalid, retry_failed=args.retry_failed,
                    execution_authorized=True, spending_authorized=True))
                _print_json({**result, "budget": ledger.summary()})
            return 0
        if args.command == "summarize":
            _print_json(summarize(args.output_root))
            return 0
        if args.command == "analyze":
            from .analysis import analyze
            result = analyze(args.output_root, args.out)
            _print_json({k: result[k] for k in ("evidence_kind", "towns", "pairs", "excluded_towns", "plot_written")}
                        | {"model_fit": result["models"]["status"], "report": str(args.out / "report.md")})
            return 0
        if args.command == "review-collection":
            from .review import review_collection
            result = review_collection(args.output_root, args.out, args.ledger_copy)
            missing = result["coverage"]["missing_run_ids"]
            _print_json({"status": result["status"], "evidence_kind": result["evidence_kind"],
                         "selected_complete": result["coverage"]["selected_complete"],
                         "missing_towns": len(missing) if missing is not None else None,
                         "full_matrix_complete": result["coverage"]["full_matrix_coverage"]["complete"],
                         "ledger_status": result["ledger"]["status"], "issues": result["issues"],
                         "report": str(args.out / "review.md")})
            return 0
        if args.command == "audit-sample":
            from .judge_audit import make_audit
            _print_json(make_audit(args.output_root, args.out, size=args.size, seed=args.seed))
            return 0
        if args.command == "prepare-judge-validation":
            from .judge_validation import prepare_validation
            _print_json(prepare_validation(args.output_root, args.out, size=args.size, seed=args.seed))
            return 0
        if args.command == "audit-score":
            from .judge_audit import score_audit
            _print_json(score_audit(args.audit_dir, args.sheets))
            return 0
        if args.command == "ledger":
            from .budget import BudgetLedger
            if not args.ledger.is_file():
                raise ValueError("ledger file does not exist")
            if args.reconcile and (args.actual_usd is None or not args.note):
                raise ValueError("--reconcile needs --actual-usd and --note")
            if not args.reconcile and (args.actual_usd is not None or args.note):
                raise ValueError("--actual-usd and --note are only used with --reconcile")
            with BudgetLedger(args.ledger, args.budget_usd) as ledger:
                if args.reconcile:
                    ledger.reconcile(args.reconcile, args.actual_usd, args.note)
                _print_json({"budget": ledger.summary(), "unknown_reservations": ledger.unknown_reservations()})
            return 0
        if args.command == "rejudge":
            from . import rejudge as rejudging
            if not args.execute:
                _print_json({**rejudging.summary(args.output_root), "status": "preview",
                             "provider_api_calls": 0})
                return 0
            if not args.spending_authorized:
                raise ValueError("re-judging spends money; add --spending-authorized")
            if not (args.providers and args.ledger and args.budget_usd):
                raise ValueError("execution requires --providers, --ledger and --budget-usd")
            from .budget import BudgetLedger
            from .execution import load_provider_manifest
            from .providers import ProviderBackend
            providers = load_provider_manifest(args.providers)
            towns = sorted(args.output_root.glob("*/config.json"))
            if not towns:
                raise ValueError("no saved towns found")
            judge_key = load_config(towns[0])["models"]["judge_models"][0]["key"]
            with BudgetLedger(args.ledger, args.budget_usd) as ledger:
                if ledger.summary()["blocked"]:
                    raise ValueError("budget ledger is blocked; record held charges first")
                backend = ProviderBackend(providers, ledger)
                backend.validate_credentials([judge_key])
                try:
                    result = asyncio.run(rejudging.rejudge(args.output_root, backend, judge_key,
                                                           attempts=args.attempts))
                finally:
                    budget = ledger.summary()
                _print_json({**result, "budget": budget})
            return 0

        config = load_config(args.config)
        if args.command == "simulation-demo":
            from .simulation_artifacts import audit_simulation
            if args.output.exists():
                raise FileExistsError("refusing existing simulation demo directory")
            runs = [r for r in build_manifest(config) if r["cell_id"] == 1 and r["seed_id"] == 0]
            args.output.mkdir(parents=True)
            async def demonstrate():
                for run in runs:
                    await run_town(config, run, FixtureBackend(mode=args.mode), args.output,
                                   defer_judging=True)
            asyncio.run(demonstrate())
            towns = [audit_simulation(args.output / run["run_id"]) for run in runs]
            _print_json({"evidence_kind": "synthetic_fixture", "study_eligible": False,
                         "towns": len(towns), "phone_transcripts": sum(len(t["scene_5_phone_transcripts"]) for t in towns),
                         "evaluation_status": "pending", "judge_calls": 0, "provider_api_calls": 0,
                         "output_root": str(args.output)})
            return 0
        if args.command == "simulate":
            from .execution import load_provider_manifest, select_runs
            from .simulation_execution import allocate_runs, simulation_plan, collect_simulations
            providers = load_provider_manifest(args.providers)
            selection = select_runs(config, args.model_keys, args.pairs_per_cell,
                                    args.all_pairs, args.start_pair)
            runs, allocation = allocate_runs(config, selection, shard_count=args.shard_count,
                                               shard_index=args.shard_index)
            info = simulation_plan(config, providers, runs, allocation)
            if args.plan_out:
                with args.plan_out.open("xb") as stream:
                    stream.write(canonical_bytes(info))
            if not args.execute:
                _print_json(info)
                return 0
            if not args.spending_authorized:
                raise ValueError("simulation execution requires explicit release of the spending hold")
            if not args.ledger or not args.budget_usd:
                raise ValueError("simulation execution requires --ledger and --budget-usd")
            if info["execution_gates"]:
                raise ValueError("; ".join(info["execution_gates"]))
            from .budget import BudgetLedger
            from .providers import ProviderBackend
            with BudgetLedger(args.ledger, args.budget_usd) as ledger:
                backend = ProviderBackend(providers, ledger)
                result = asyncio.run(collect_simulations(
                    config, providers, runs, args.output, backend, allocation=allocation,
                    resume=args.resume, max_concurrent_towns=args.max_concurrent_towns,
                    execution_authorized=True, spending_authorized=True))
                _print_json({**result, "budget": ledger.summary()})
            return 0
        if args.command == "live":
            from .execution import load_provider_manifest, select_runs, plan, collect
            providers = load_provider_manifest(args.providers)
            runs = select_runs(config, args.model_keys, args.pairs_per_cell, args.full_pilot, args.start_pair)
            info = plan(config, providers, runs)
            if not args.execute:
                _print_json(info)
                return 0
            if not args.spending_authorized:
                raise ValueError("execution requires explicit release of the spending hold")
            if not args.ledger or not args.budget_usd:
                raise ValueError("execution requires --ledger and --budget-usd")
            if args.output.exists() and not args.resume:
                raise ValueError("refusing existing output directory; add --resume to continue it")
            if info["execution_gates"]:
                raise ValueError("; ".join(info["execution_gates"]))
            from .budget import BudgetLedger
            from .providers import ProviderBackend
            with BudgetLedger(args.ledger, args.budget_usd) as ledger:
                backend = ProviderBackend(providers, ledger)
                result = asyncio.run(collect(config, providers, runs, args.output, backend,
                                             resume=args.resume,
                                             max_concurrent_towns=args.max_concurrent_towns))
                _print_json({**result, "budget": ledger.summary()})
            return 0
        manifest = build_manifest(config)
        plan_info = {
            "config_version": config["meta"]["version"],
            "planned_towns": len(manifest),
            "planned_pairs": len({run["pair_id"] for run in manifest}),
            "model_keys": [model["key"] for model in config["models"]["agent_models"]],
            "provider_api_calls": 0,
            "study_results_generated": False,
        }
        if args.command == "validate":
            _print_json({**plan_info, "status": "valid", "config_path": str(args.config)})
        elif args.command == "manifest":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as stream:
                for run in manifest:
                    stream.write(canonical_bytes(run) + b"\n")
            _print_json({**plan_info, "status": "manifest_written", "planned_only": True,
                         "output_path": str(args.output)})
        elif args.command == "demo":
            _print_json(asyncio.run(_demo(config, manifest, args.output, args.mode)))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
