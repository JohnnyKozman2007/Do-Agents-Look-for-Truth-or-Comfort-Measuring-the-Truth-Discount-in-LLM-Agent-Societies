"""Preview audited usage evidence; apply only uniquely attributable known charges.

Usage: python scripts/reconcile_unknowns.py EXISTING_LEDGER FIXED_CAP OUTPUT [OUTPUT ...] [--apply]

Preview replays a temporary journal copy. Unpriced, ambiguous or unbound charges
remain held. Calculated token costs are not invoice verification; manual billed
reconciliation remains available through the ordinary ledger CLI.

OUTPUT may be a legacy scored collection (`live`) or a sealed simulation-only
collection (`simulate`); each is audited against its own saved plan.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from truth_discount.artifacts import archived_attempt_paths, audit_town  # noqa: E402
from truth_discount.budget import BudgetLedger, money  # noqa: E402
from truth_discount.config import load_config  # noqa: E402
from truth_discount.contracts import GenerationRequest, digest  # noqa: E402
from truth_discount.execution import _atomic_json, _audit_expected, load_provider_manifest  # noqa: E402
from truth_discount.providers import ProviderBackend  # noqa: E402
from truth_discount.review import _validated_plan  # noqa: E402


def _journal(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("an existing regular ledger journal is required")
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n"):
        raise ValueError("ledger is empty or torn; preserve it for manual review")
    return raw


def _snapshot(root: Path) -> dict:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("saved collection must not contain symlinks")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _is_simulation(root: Path) -> bool:
    try:
        plan = json.loads((root / "execution_plan.json").read_bytes())
    except (OSError, ValueError):
        return False
    return isinstance(plan, dict) and plan.get("execution_mode") == "simulation_only"


def _audited_towns(root: Path, directories: list[Path]) -> tuple[dict, list[dict], dict]:
    """Audit every saved attempt against its own plan: legacy scored or sealed simulation."""
    if _is_simulation(root):
        from truth_discount.simulation_execution import _audit_expected as _simulation_expected, _read_plan
        saved = _read_plan(root)  # Also checks plan hashes and the checkpoint's ledger binding.
        runs = {run["run_id"]: run for run in saved["runs"]}
        towns = []
        for directory in directories:
            if directory.name not in runs:
                raise ValueError("saved attempt is outside its execution plan")
            towns.append(_simulation_expected(directory, saved, runs[directory.name]))
        return saved, towns, saved["provider_manifest"]
    towns = [audit_town(path) for path in directories]
    config = load_config(directories[0] / "config.json")
    saved = _validated_plan(root, towns, config)
    if saved is None:
        raise ValueError("saved execution plan belongs to another ledger or fixed cap")
    providers = towns[0]["execution_manifest"]
    runs = {run["run_id"]: run for run in saved["runs"]}
    for directory in directories:
        if directory.name not in runs:
            raise ValueError("saved attempt is outside its execution plan")
        _audit_expected(directory, config, providers, runs[directory.name], saved["evidence_kind"])
    return saved, towns, providers


def _bound_evidence(outputs: list[Path], ledger: BudgetLedger) -> tuple[list, list]:
    records, collections = [], []
    binding = {key: ledger.checkpoint()[key] for key in ("ledger_id", "limit_usd")}
    for root in outputs:
        before = _snapshot(root)
        directories = sorted(path for path in root.iterdir() if path.is_dir() and path.name != "_incomplete")
        directories += archived_attempt_paths(root)
        if not directories:
            raise ValueError("no auditable saved attempts in output collection")
        saved, towns, providers = _audited_towns(root, directories)
        if saved["ledger_binding"] != binding:
            raise ValueError("saved execution plan belongs to another ledger or fixed cap")
        anchor = load_provider_manifest(root / "budget_checkpoint.json")
        if set(anchor) != {"execution_plan_sha256", "ledger_checkpoint"} or anchor["execution_plan_sha256"] != digest(saved):
            raise ValueError("saved budget checkpoint differs from execution plan")
        ledger.verify_checkpoint(anchor["ledger_checkpoint"])
        backend = ProviderBackend(providers, ledger, transport=lambda *args: None,
                                  evidence_kind=saved["evidence_kind"])
        for town in towns:
            for call in town["calls"]:
                receipt = call.get("token_usage")
                if not isinstance(receipt, dict):
                    continue
                for attempt in receipt["attempts"]:
                    identifier = attempt.get("reservation_id")
                    if identifier is not None:
                        records.append((identifier, town["run_id"], call, receipt, attempt, backend))
        if _snapshot(root) != before:
            raise ValueError("saved collection changed during evidence validation")
        collections.append((root, saved, before))
    return records, collections


def _known_charge(row: dict, matches: list) -> tuple[str | None, dict | None]:
    if len(matches) != 1:
        return "missing or duplicate reservation evidence", None
    _, run_id, call, receipt, attempt, backend = matches[0]
    if (len(receipt["attempts"]) != 1 or attempt.get("status") not in {"completed", "failed"}
            or receipt.get("cost_status") != "calculated_from_usage" or receipt.get("cost_usd") is None):
        return "charge is unpriced or not attributable to one native attempt", None
    request = GenerationRequest(**call["request"])
    route, body, _, pricing_hash, _ = backend._prepare(request)  # Pure: no credential or network access.
    if (receipt["input_tokens"] > route["max_input_tokens"]
            or receipt["output_tokens"] > request.settings["max_tokens"]):
        return "reported token usage exceeds native request bounds", None
    if receipt["actual_model"] not in [route["model_id"], *route.get("accepted_model_ids", [])]:
        return "priced response model differs from the native approved route", None
    observed = row.get("receipt", {})
    fields = ("actual_provider", "actual_model", "request_id", "pricing_sha256", "input_tokens",
              "output_tokens", "cached_input_tokens", "reasoning_tokens", "cache_creation_input_tokens",
              "cache_usage", "execution_mode", "provider_api_calls")
    if any(observed.get(field) is not None and digest(observed[field]) != digest(receipt.get(field))
           for field in fields):
        return "saved receipt contradicts an observed ledger response field", None
    if observed.get("cost_usd") is not None and money(observed["cost_usd"]) != money(receipt["cost_usd"]):
        return "saved receipt contradicts the observed ledger cost", None
    expected = {"model_key": request.model_key, "provider": route["provider"], "model_id": route["model_id"],
                "request_sha256": digest(body), "pricing_sha256": pricing_hash,
                "attempt_index": attempt["attempt_index"], "input_token_bound": route["max_input_tokens"],
                "max_output_tokens": request.settings["max_tokens"], "evidence_kind": backend.evidence_kind}
    if row["metadata"] != expected or receipt["pricing_sha256"] != pricing_hash:
        return "reservation request, pricing or evidence metadata differs", None
    return None, {"reservation_id": row["id"], "run_id": run_id, "call_id": call["call_id"],
                  "amount_usd": str(money(receipt["cost_usd"])),
                  "cost_basis": "audited_usage_calculation", "evidence_kind": backend.evidence_kind}


def reconcile_known(ledger_path: Path, cap: str, outputs: list[Path], *, apply: bool = False) -> dict:
    """All-or-nothing eligibility check, followed by explicit operator application."""
    ledger_path = Path(ledger_path)
    raw = _journal(ledger_path)
    roots = [Path(path).resolve() for path in outputs]
    if not roots or len(set(roots)) != len(roots):
        raise ValueError("provide distinct saved output collections")
    with tempfile.TemporaryDirectory(prefix="truth-discount-reconcile-preview-") as temporary:
        copied = Path(temporary) / "journal.jsonl"
        copied.write_bytes(raw)
        with BudgetLedger(copied, cap) as preview:
            records, collections = _bound_evidence(roots, preview)
            matches = defaultdict(list)
            for record in records:
                matches[record[0]].append(record)
            unknown = preview.unknown_reservations()
            checkpoint = preview.checkpoint()
            eligible, unresolved = [], []
            for row in unknown:
                reason, charge = _known_charge(row, matches[row["id"]])
                if reason:
                    unresolved.append({"reservation_id": row["id"], "reason": reason})
                else:
                    eligible.append(charge)
            budget = preview.summary()
    if _journal(ledger_path) != raw or any(_snapshot(root) != before for root, _, before in collections):
        raise ValueError("ledger or source collection changed during preview")
    result = {"status": "unresolved" if unresolved else "ready_for_explicit_apply" if eligible else "no_unknown_charges",
              "eligible": eligible, "unresolved": unresolved, "unknown_count": len(unknown),
              "applied_count": 0, "budget": budget, "billing_verified": False,
              "cost_basis": "audited_usage_calculation", "provider_api_calls": 0,
              "preview_uses_temporary_copy": True}
    if not apply or not eligible and not unresolved:
        return result
    if unresolved:
        raise ValueError("unresolved charges remain held; no reconciliation applied")

    class ExistingLedger(BudgetLedger):
        def _load(self):
            # Ownership lock is acquired, but the original journal has not been
            # opened or recovered yet. Validate inputs before any journal write.
            if (_journal(self.path) != raw
                    or any(_snapshot(root) != before for root, _, before in collections)):
                raise ValueError("ledger or source collection changed before apply")
            super()._load()

    with ExistingLedger(ledger_path, cap) as ledger:
        ledger.verify_checkpoint(checkpoint)
        if ledger.unknown_reservations() != unknown:
            raise ValueError("unknown reservations changed before apply")
        def anchor(value):
            for root, saved, _ in collections:
                _atomic_json(root / "budget_checkpoint.json", {
                    "execution_plan_sha256": digest(saved), "ledger_checkpoint": value})
        ledger.set_checkpoint_callback(anchor)
        try:
            for charge in eligible:
                ledger.reconcile(charge["reservation_id"], charge["amount_usd"],
                                 "Audited usage calculation, not invoice proof: "
                                 + charge["run_id"] + " call " + str(charge["call_id"]))
                result["applied_count"] += 1
            result.update(status="applied", budget=ledger.summary())
        finally:
            ledger.set_checkpoint_callback(None)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("cap")
    parser.add_argument("outputs", type=Path, nargs="+")
    parser.add_argument("--apply", action="store_true", help="explicitly record only fully verified known usage costs")
    args = parser.parse_args(argv)
    try:
        result = reconcile_known(args.ledger, args.cap, args.outputs, apply=args.apply)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Reconciliation refused: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
