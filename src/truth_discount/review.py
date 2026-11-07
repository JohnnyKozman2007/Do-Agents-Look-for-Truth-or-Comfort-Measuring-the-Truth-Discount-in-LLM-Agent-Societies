"""Read-only review of one saved collection, without inference or label repair.

Receipt replay is not an invoice reconciliation. A supplied journal is read
into a temporary copy because opening BudgetLedger can perform crash recovery.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import tempfile

from .artifacts import archived_attempt_paths, audit_town, summarize
from .budget import BudgetLedger, money
from .config import build_manifest, load_config
from .contracts import digest
from .execution import load_provider_manifest, plan


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _inventory(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("review requires a fixed source tree without symlinks")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = _sha(path.read_bytes())
    return result


def _validated_plan(root: Path, towns: list[dict], config: dict) -> dict | None:
    path = root / "execution_plan.json"
    if not path.exists():
        return None
    saved = load_provider_manifest(path)
    if saved.get("execution_plan_version") != 2:
        raise ValueError("execution plan version has no verifiable ledger binding")
    runs = saved.get("runs")
    if not isinstance(runs, list) or not runs or any(not isinstance(row, dict) for row in runs):
        raise ValueError("execution plan has no valid selected run list")
    ids = [row.get("run_id") for row in runs]
    if any(not isinstance(identifier, str) for identifier in ids) or len(set(ids)) != len(ids):
        raise ValueError("execution plan has invalid or duplicate run identities")
    configured = {row["run_id"]: row for row in build_manifest(config)}
    if any(identifier not in configured or digest(row) != digest(configured[identifier])
           for identifier, row in zip(ids, runs)):
        raise ValueError("execution plan selection differs from the saved configuration")
    pair_conditions = defaultdict(list)
    for row in runs:
        pair_conditions[(row["model_key"], row["pair_id"])].append(row["condition_type"])
    if any(sorted(conditions) != ["rumor", "truth_twin"] for conditions in pair_conditions.values()):
        raise ValueError("execution plan selection must preserve matched twins")
    providers = towns[0].get("execution_manifest")
    if not isinstance(providers, dict):
        raise ValueError("execution plan lacks saved provider provenance")
    binding = saved.get("ledger_binding")
    if (not isinstance(binding, dict) or set(binding) != {"ledger_id", "limit_usd"}
            or not isinstance(binding["ledger_id"], str) or len(binding["ledger_id"]) != 32
            or any(c not in "0123456789abcdef" for c in binding["ledger_id"])):
        raise ValueError("invalid execution plan ledger binding")
    if money(binding["limit_usd"], "execution plan limit_usd") <= 0:
        raise ValueError("execution plan limit_usd must be positive")
    expected = plan(config, providers, runs)
    if expected["execution_gates"]:
        raise ValueError("saved execution plan has unresolved provider gates")
    expected.update(execution_plan_version=2, evidence_kind=towns[0]["evidence_kind"],
                    ledger_binding=binding)
    if digest(saved) != digest(expected):
        raise ValueError("execution plan differs from its saved config, providers or selected runs")
    anchor_path = root / "budget_checkpoint.json"
    if anchor_path.exists():
        anchor = load_provider_manifest(anchor_path)
        if (set(anchor) != {"execution_plan_sha256", "ledger_checkpoint"}
                or anchor["execution_plan_sha256"] != digest(saved)):
            raise ValueError("budget checkpoint differs from the saved execution plan")
        checkpoint = anchor["ledger_checkpoint"]
        if (not isinstance(checkpoint, dict)
                or checkpoint.get("ledger_id") != binding["ledger_id"]
                or money(checkpoint.get("limit_usd"), "checkpoint limit_usd") != money(binding["limit_usd"])):
            raise ValueError("budget checkpoint differs from the execution plan ledger binding")
    return saved


def _coverage(towns: list[dict], config: dict, saved: dict | None) -> dict:
    observed = Counter(town["run_id"] for town in towns)
    completed = {town["run_id"] for town in towns if town["run_status"] == "completed"}
    incomplete = sorted(town["run_id"] for town in towns if town["run_status"] != "completed")
    base = {"observed_active_towns": len(towns), "completed_active_towns": len(completed),
            "incomplete_run_ids": incomplete,
            "duplicate_active_run_ids": sorted(identifier for identifier, n in observed.items() if n > 1),
            "scope": "one collection only; other batches require separate or explicit union reconciliation"}
    if saved is None:
        return {**base, "plan_status": "unavailable", "selected_expected_towns": None,
                "selected_complete": None, "configured_run_count": None,
                "missing_run_ids": None, "missing_entire_pairs": None,
                "unexpected_run_ids": None,
                "full_matrix_coverage": {"status": "unavailable_without_execution_plan",
                                         "complete": None, "expected_towns": None}}
    expected = {row["run_id"] for row in saved["runs"]}
    grouped = defaultdict(set)
    for row in saved["runs"]:
        grouped[(row["model_key"], row["pair_id"])].add(row["run_id"])
    missing_pairs = [{"model_key": model, "pair_id": pair}
                     for (model, pair), ids in sorted(grouped.items()) if not ids.intersection(observed)]
    configured = {row["run_id"] for row in build_manifest(config)}
    unexpected = sorted(set(observed) - expected)
    selected_complete = expected <= completed and not unexpected and not base["duplicate_active_run_ids"]
    return {**base, "plan_status": "verified", "selected_expected_towns": len(expected),
            "selected_expected_pairs": len(grouped), "selected_complete": selected_complete,
            "configured_run_count": len(configured),
            "missing_run_ids": sorted(expected - set(observed)),
            "expected_not_completed_run_ids": sorted(expected - completed),
            "missing_entire_pairs": missing_pairs, "unexpected_run_ids": unexpected,
            "full_matrix_coverage": {"status": "complete" if configured <= completed and not unexpected else "incomplete",
                                     "complete": configured <= completed and not unexpected,
                                     "expected_towns": len(configured),
                                     "completed_configured_towns": len(configured & completed),
                                     "missing_or_incomplete_run_ids": sorted(configured - completed)}}


def _ledger_review(root: Path, saved: dict | None, raw: bytes | None) -> dict:
    result = {"provided": raw is not None, "status": "not_provided", "source_sha256": None,
              "checkpoint_verified": False, "billing_verified": False,
              "provider_billing_reconciled": False, "inspection": "temporary_copy_only",
              "budget": None, "unknown_reservations": None,
              "limitation": "Local journal replay and operator notes do not verify provider invoices."}
    if raw is None:
        return result
    result["source_sha256"] = _sha(raw)
    if not raw or not raw.endswith(b"\n"):
        return {**result, "status": "incomplete_or_torn_journal"}
    if saved is None:
        return {**result, "status": "unavailable_without_execution_plan"}
    anchor_path = root / "budget_checkpoint.json"
    if not anchor_path.is_file():
        return {**result, "status": "missing_checkpoint"}
    anchor = load_provider_manifest(anchor_path)
    if (set(anchor) != {"execution_plan_sha256", "ledger_checkpoint"}
            or anchor["execution_plan_sha256"] != digest(saved)):
        raise ValueError("budget checkpoint differs from the saved execution plan")
    # This copy may gain interrupt/identity events during replay. The supplied
    # journal is never opened by BudgetLedger and its bytes are checked again.
    with tempfile.TemporaryDirectory(prefix="truth-discount-review-ledger-") as temporary:
        target = Path(temporary) / "journal.jsonl"
        target.write_bytes(raw)
        try:
            with BudgetLedger(target, saved["ledger_binding"]["limit_usd"]) as ledger:
                checkpoint = ledger.checkpoint()
                if checkpoint["ledger_id"] != saved["ledger_binding"]["ledger_id"]:
                    raise ValueError("supplied ledger identity differs from the execution plan")
                ledger.verify_checkpoint(anchor["ledger_checkpoint"])
                result.update(status="verified_local_journal", checkpoint_verified=True,
                              budget=ledger.summary(), unknown_reservations=ledger.unknown_reservations(),
                              temporary_recovery_events_added=target.read_bytes() != raw)
        except ValueError as error:
            raise ValueError("supplied ledger cannot verify the saved collection: " + str(error)) from error
    return result


def review_collection(output_root: Path, destination: Path, ledger_copy: Path | None = None) -> dict:
    """Review frozen saved data, writing a new report outside every input.

    No inference, credential access, label replacement or journal reconciliation
    occurs. A source change during review fails before the output is created.
    """
    root, destination = Path(output_root).resolve(), Path(destination).resolve()
    if not root.is_dir():
        raise ValueError("saved collection is not a directory")
    if destination == root or root in destination.parents:
        raise ValueError("review destination must stay outside the saved collection")
    if destination.exists():
        raise FileExistsError("refusing existing review destination")
    before = _inventory(root)
    ledger_path = Path(ledger_copy).resolve() if ledger_copy is not None else None
    ledger_raw = ledger_path.read_bytes() if ledger_path is not None else None
    active_paths = sorted(path for path in root.iterdir() if path.is_dir() and path.name != "_incomplete")
    if not active_paths:
        raise ValueError("no saved active town bundles to review")
    if any(not (path / "manifest.json").is_file() for path in active_paths):
        raise ValueError("unaccounted active directory lacks a town manifest")
    towns = [audit_town(path) for path in active_paths]
    archive_paths = archived_attempt_paths(root)
    archived = [audit_town(path) for path in archive_paths]
    all_towns = towns + archived
    for key in ("config_sha256", "execution_manifest_sha256", "evidence_kind"):
        if len({town.get(key) for town in all_towns}) != 1:
            raise ValueError("collection attempts have inconsistent provenance: " + key)
    config = load_config(active_paths[0] / "config.json")
    saved = _validated_plan(root, all_towns, config)
    coverage = _coverage(towns, config, saved)
    expected = {row["run_id"] for row in saved["runs"]} if saved else None
    unexpected_archives = sorted({town["run_id"] for town in archived
                                  if expected is not None and town["run_id"] not in expected})
    completed_archives = [path.relative_to(root).as_posix() for path, town in zip(archive_paths, archived)
                          if town["run_status"] == "completed"]
    replay = summarize(root)
    overlay_files = []
    for path in sorted([root / "rejudged.jsonl", *root.glob("*/rejudged.jsonl")]):
        if path.exists():
            data = path.read_bytes()
            overlay_files.append({"path": path.relative_to(root).as_posix(), "sha256": _sha(data),
                                  "nonempty_lines": sum(bool(line.strip()) for line in data.splitlines())})
    ledger = _ledger_review(root, saved, ledger_raw)
    if _inventory(root) != before:
        raise ValueError("source collection changed during review; use a finished snapshot")
    if ledger_path is not None and ledger_path.read_bytes() != ledger_raw:
        raise ValueError("supplied journal changed during review; use a finished copy")
    issues = []
    if coverage["selected_complete"] is not True:
        issues.append("selected_plan_incomplete_or_unavailable")
    if unexpected_archives:
        issues.append("archived_attempts_outside_selected_plan")
    if completed_archives:
        issues.append("completed_archived_attempts_require_selection_review")
    if ledger["checkpoint_verified"] is not True:
        issues.append("bound_ledger_not_verified")
    elif ledger["budget"]["blocked"]:
        issues.append("ledger_has_unresolved_or_overrun_charges")
    result = {"review_version": "truth-discount-collection-review-1",
              "status": "needs_review" if issues else "reviewed_declared_selection",
              "issues": issues, "evidence_kind": towns[0]["evidence_kind"],
              "study_eligible": False, "study_results_generated": False,
              "review_provider_api_calls": 0, "source_unchanged": True,
              "source_files_sha256": before, "config_sha256": towns[0]["config_sha256"],
              "provider_manifest_sha256": towns[0].get("execution_manifest_sha256"),
              "execution_plan_sha256": digest(saved) if saved is not None else None,
              "coverage": coverage, "ledger": ledger,
              "receipt_accounting": replay["receipt_accounting"],
              "archive_review": {"unexpected_run_ids": unexpected_archives,
                                 "completed_attempt_paths": completed_archives,
                                 "outcome_policy": "active_original_bundles_only_no_best_attempt_selection"},
              "labels": {"policy": "original_saved_labels_only", "overlays_applied": False,
                         "overlay_files": overlay_files, "overlay_provenance_validated": False,
                         "limitation": "Town receipt totals exclude rejudge overlays; retain their additional receipts and bound-ledger costs separately."},
              "review_source_sha256": _sha(Path(__file__).read_bytes()),
              "limitations": ["One collection is not a union of separately operated batches.",
                              "Review completeness is not confirmatory analysis, human-audit completion or publication readiness.",
                              "Before/after byte hashes require a quiescent snapshot; they are not a provider-side billing audit."]}
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "review.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (destination / "review.md").write_text(
        "# Saved collection review\n\n"
        f"Status: {result['status']}. Evidence: {result['evidence_kind']}.\n\n"
        f"Observed active towns: {coverage['observed_active_towns']}; completed: {coverage['completed_active_towns']}. "
        f"Declared selection: {coverage['selected_expected_towns']}; configured matrix: {coverage['configured_run_count']}.\n\n"
        f"Declared selection complete: {coverage['selected_complete']}. "
        f"Full configured matrix complete: {coverage['full_matrix_coverage']['complete']}.\n\n"
        f"Ledger: {ledger['status']}. Billing verified: false.\n\n"
        "Original saved labels retained; rejudge overlays were not applied. "
        "Unknown receipt charges remain unknown. See review.json for coverage IDs, archived attempts, costs and input hashes.\n",
        encoding="utf-8")
    return result
