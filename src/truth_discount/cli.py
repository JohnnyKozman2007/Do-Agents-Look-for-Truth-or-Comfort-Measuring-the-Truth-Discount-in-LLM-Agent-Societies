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
    # Accept --config before or after a planning/demo subcommand without resetting
    # a global value when the subcommand option is absent.
    for command in (validate, manifest, demo, live):
        command.add_argument("--config", type=Path, default=argparse.SUPPRESS, help="explicit pilot JSON path")
    return parser


def _print_json(value: dict) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))


async def _demo(config: dict, manifest: list[dict], output_root: Path, mode: str) -> dict:
    # Every model uses the same first configured world. Select entire pairs, never
    # take a slice that could leave a lone rumor or truth condition.
    runs = [run for run in manifest if run["cell_id"] == 1
            and run["layout_id"] == 0 and run["repetition_id"] == 0]
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
        if args.command == "summarize":
            _print_json(summarize(args.output_root))
            return 0

        config = load_config(args.config)
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
            if args.output.exists():
                raise ValueError("refusing existing output directory")
            if info["execution_gates"]:
                raise ValueError("; ".join(info["execution_gates"]))
            from .budget import BudgetLedger
            from .providers import ProviderBackend
            with BudgetLedger(args.ledger, args.budget_usd) as ledger:
                backend = ProviderBackend(providers, ledger)
                result = asyncio.run(collect(config, providers, runs, args.output, backend))
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
