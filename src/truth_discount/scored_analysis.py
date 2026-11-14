"""Read-only bridge from sealed simulations and separate judgments to analysis.

The bridge reads one raw town at a time and retains compact analysis towns,
never their actor histories or native responses. It does not rewrite a generation bundle to impersonate a legacy
scored bundle. Judge selection, spending and main-outcome access remain separate.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

from . import analysis
from .config import build_manifest, load_config
from .contracts import clone, digest
from .deferred_judging import (_profile, _roots, _source, _verify_source_files,
                               replay_judging)
from .scoring import town_metrics

VERSION = "truth-discount-scored-analysis-1"
ATTEMPT_POLICIES = ("first_only", "latest_sensitivity")
_IDENTITY = ("run_id", "pair_id", "model_key", "cell_id", "condition_type",
             "layout_id", "repetition_id", "seed_id", "real_artist", "fake_artist",
             "source_persona_id", "seating_assignment", "knobs", "catch_up_pairs",
             "config_sha256", "evidence_kind")


def _hashes(directory: Path) -> dict:
    names = ("judging_plan.json", "attempts.jsonl", "budget_checkpoint.json")
    return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}


def _preflight(sources, profile: dict, outcomes_authorized: bool,
               sidecar: Path, analysis_policy: dict | None, attempt_policy: str) -> None:
    if type(outcomes_authorized) is not bool:
        raise ValueError("main outcome access authorization must be boolean")
    for root in _roots(sources):
        directories = [root] if (root / "town.json").is_file() else [
            p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith("_")]
        for path in directories:
            config = load_config(path / "config.json")
            manifest = json.loads((path / "manifest.json").read_bytes())
            if config["meta"]["module"] == "main" and manifest.get("evidence_kind") == "development_pilot":
                if not outcomes_authorized:
                    raise ValueError("main outcomes remain quarantined until explicit outcome-access authorization")
                if not profile["approved"] or not profile["population_approved"]:
                    raise ValueError("main analysis requires the frozen approved judge and population")
                if analysis_policy is None:
                    raise ValueError("main outcome access requires an approved analysis policy before replay")
                from .confirmatory_analysis import validate_policy
                # Read frozen plan metadata before actor/score replay. Strict
                # replay subsequently authenticates this binding against the
                # real sources and journal, rather than trusting the header.
                frozen = json.loads((sidecar / "judging_plan.json").read_bytes())
                if frozen.get("profile_sha256") != digest(profile):
                    raise ValueError("main judge profile differs from the frozen scoring plan")
                validate_policy(analysis_policy, config, digest(profile),
                                frozen.get("source_sha256"), attempt_policy)


def _load_scored_collection(sources, judging_output: Path, profile: dict, *,
                           attempt_policy: str = "first_only",
                           outcomes_authorized: bool = False,
                           analysis_policy: dict | None = None) -> tuple[list[dict], dict, dict, dict]:
    """Strictly replay sidecars, then construct compact in-memory scored towns.

    Every generated town remains in denominators, including towns with no
    selected/valid judgment. Latest means latest, even when a repair is invalid.
    It never means the best valid result. No original ledger is opened.
    """
    if attempt_policy not in ATTEMPT_POLICIES:
        raise ValueError("attempt policy must be first_only or latest_sensitivity")
    profile = _profile(profile)
    sidecar = Path(judging_output).resolve() / profile["profile_id"]
    _preflight(sources, profile, outcomes_authorized, sidecar, analysis_policy, attempt_policy)
    initial_sidecar = _hashes(sidecar)
    audited = _source(sources, profile)
    result = replay_judging(sources, judging_output, profile, audited=audited)
    source, _, directories = audited
    if analysis_policy is not None:
        from .confirmatory_analysis import validate_policy
        first_directory = directories[source["towns"][0]["run_id"]]
        validate_policy(analysis_policy, load_config(first_directory / "config.json"),
                        digest(profile), result["source_sha256"], attempt_policy)
    grouped = defaultdict(dict)
    field = "first_evaluation" if attempt_policy == "first_only" else "latest_evaluation"
    for item in result["items"]:
        run_id, seat = item["run_id"], item["seat_id_private"]
        if seat in grouped[run_id]:
            raise ValueError("duplicate source-bound score seat")
        grouped[run_id][seat] = item
    towns, status_counts, config = [], Counter(), None
    repairs = 0
    for entry in source["towns"]:
        directory = directories[entry["run_id"]]
        # The complete source has already passed saved-response replay. Do not
        # retain thousands of towns' actor histories in the analysis process.
        raw = json.loads((directory / "town.json").read_bytes())
        if config is None:
            config = load_config(directory / "config.json")
        compact = {key: clone(raw[key]) for key in _IDENTITY}
        # Pure synthetic fixtures have no provider manifest. Native/mocked
        # provider collections retain their audited original manifest hash.
        compact["execution_manifest_sha256"] = raw.get("execution_manifest_sha256")
        for name in ("scene_2_first_hand_decisions", "scene_4_second_hand_decisions"):
            compact[name] = [{key: row[key] for key in ("seat_id", "layer", "parse_status", "decision")}
                             for row in raw[name]]
        compact["scene_3_catch_up_transcripts"] = [
            {"first_hand_seat": pair["first_hand_seat"],
             "lines": [{key: line[key] for key in ("seat_id", "text", "scripted") if key in line}
                       for line in pair["lines"]]}
            for pair in raw["scene_3_catch_up_transcripts"]]
        compact["scene_3_poster_evidence_passed"] = clone(raw["scene_3_poster_evidence_passed"])
        compact["generation_attempt_id"] = entry["generation_attempt_id"]
        compact["judgment_provenance"] = {}
        evaluations = []
        expected_seats = config["seating_and_pairing"]["first_hand_seats"] + config["seating_and_pairing"]["second_hand_seats"]
        for seat in expected_seats:
            row = grouped[entry["run_id"]].get(seat)
            if row is None:
                status_counts["unselected"] += 1
                compact["judgment_provenance"][seat] = {"item_id": None, "selected": False,
                    "saved_evaluation_status": "unselected", "attempt_count": 0}
                continue
            if row["generation_attempt_id"] != entry["generation_attempt_id"]:
                raise ValueError("score belongs to a different generation attempt")
            evaluation = row[field]
            compact["judgment_provenance"][seat] = {"item_id": row["item_id"], "selected": True,
                "saved_evaluation_status": evaluation["status"] if evaluation is not None else "not_observed",
                "attempt_count": row["attempt_count"]}
            status_counts[evaluation["status"] if evaluation is not None else "not_observed"] += 1
            repairs += int(row["attempt_count"] > 1)
            if evaluation is not None:
                evaluations.append({"seat_id": seat, **clone(evaluation)})
        compact["judge_evaluations"] = evaluations
        decisions = compact["scene_2_first_hand_decisions"] + compact["scene_4_second_hand_decisions"]
        compact["metrics"] = town_metrics(config, evaluations, decisions)
        compact["judge_profile_sha256"] = digest(profile)
        compact["judging_source_sha256"] = result["source_sha256"]
        compact["analysis_attempt_policy"] = attempt_policy
        towns.append(compact)
        del raw
    _verify_source_files(source, directories)
    if _hashes(sidecar) != initial_sidecar:
        raise ValueError("judgment sidecar changed during analysis; use a stopped, frozen collection")
    expected = {run["run_id"] for run in build_manifest(config)}
    observed = {town["run_id"] for town in towns}
    if observed - expected:
        raise ValueError("source contains run IDs outside the configured study")
    archives = [row for collection in source["collections"] for row in collection["archived_attempts"]]
    provenance = {"version": VERSION, "judge_profile_sha256": digest(profile),
        "source_sha256": result["source_sha256"], "config_sha256": source["config_sha256"],
        "evidence_kind": source["evidence_kind"], "attempt_policy": attempt_policy,
        "repaired_items": repairs, "population": profile["population"],
        "explicit_phone_selection": profile["selection"] is not None,
        "source_towns": len(towns), "expected_towns": len(expected),
        "missing_run_ids": sorted(expected - observed), "full_config_coverage": expected == observed,
        "source_phone_outcomes": len(towns) * config["meta"]["listeners_scored_per_town"],
        "selected_phone_outcomes": result["phone_outcomes"], "judgment_status_counts": dict(status_counts),
        "archived_generation_attempts": archives, "archive_count": len(archives),
        "sidecar_file_sha256": initial_sidecar, "originals_modified": False,
        "ledger_history_verified": False, "billing_verified": False, "provider_api_calls": 0,
        "study_eligible": False}
    guard = {"source": source, "directories": directories, "sidecar": sidecar,
             "sidecar_sha256": initial_sidecar}
    return towns, config, provenance, guard


def load_scored_collection(sources, judging_output: Path, profile: dict, *,
                           attempt_policy: str = "first_only", outcomes_authorized: bool = False,
                           analysis_policy: dict | None = None) -> tuple[list[dict], dict, dict]:
    """Read-only compact source/judge join. Original actor and score files remain unchanged."""
    towns, config, provenance, _ = _load_scored_collection(sources, judging_output, profile,
        attempt_policy=attempt_policy, outcomes_authorized=outcomes_authorized, analysis_policy=analysis_policy)
    return towns, config, provenance


def analyze_scored(sources, judging_output: Path, profile: dict, destination: Path, *,
                    attempt_policy: str = "first_only", analysis_policy: dict | None = None,
                    outcomes_authorized: bool = False) -> dict:
    """Write tables from a new analysis view outside immutable source/sidecars."""
    destination = Path(destination).resolve()
    for root in [*_roots(sources), Path(judging_output).resolve()]:
        if destination == root or root in destination.parents or destination in root.parents:
            raise ValueError("analysis destination must be separate from sources and judgments")
    if destination.exists():
        raise FileExistsError("analysis destination already exists")
    analysis_policy = clone(analysis_policy)
    towns, config, provenance, guard = _load_scored_collection(sources, judging_output, profile,
        attempt_policy=attempt_policy, outcomes_authorized=outcomes_authorized,
        analysis_policy=analysis_policy)
    listeners = analysis.listener_rows(towns, config)
    attempt_ids = {town["run_id"]: town["generation_attempt_id"] for town in towns}
    judgment_provenance = {town["run_id"]: town["judgment_provenance"] for town in towns}
    for row in listeners:
        row.update(judge_profile_sha256=provenance["judge_profile_sha256"],
                   judging_source_sha256=provenance["source_sha256"], analysis_attempt_policy=attempt_policy,
                   generation_attempt_id=attempt_ids[row["run_id"]])
        row.update(judgment_provenance[row["run_id"]][row["seat_id"]])
    pairs = analysis.pair_rows(towns, config)
    for row in pairs:
        row.update(truth_generation_attempt_id=attempt_ids[row["truth_run_id"]],
                   rumor_generation_attempt_id=attempt_ids[row["rumor_run_id"]],
                   judge_profile_sha256=provenance["judge_profile_sha256"],
                   judging_source_sha256=provenance["source_sha256"], analysis_attempt_policy=attempt_policy)
    conditions = analysis.condition_summary(towns, config)
    cells = analysis.cell_summary(pairs, config)
    knobs = analysis.knob_summary(pairs, config) if config["meta"]["module"] == "main" else []
    models = {"status": "blocked", "confirmatory": False,
              "reason": "explicit approved analysis policy required; additive legacy fit is not the ten-contrast model"}
    if analysis_policy is not None:
        from .confirmatory_analysis import validate_policy, planned_contrasts
        validate_policy(analysis_policy, config, provenance["judge_profile_sha256"],
                        provenance["source_sha256"], attempt_policy)
        if provenance["explicit_phone_selection"] or not provenance["full_config_coverage"]:
            models["reason"] = "calibration selection or incomplete study coverage cannot become the full confirmatory analysis"
        else:
            models = planned_contrasts(listeners, config, analysis_policy)
    summary = {**provenance, "module": config["meta"]["module"], "towns": len(towns),
        "pairs": len(pairs), "unmatched_completed_towns": len(towns) - 2 * len(pairs),
        "pairs_with_incomplete_judgments": sum(not p["judgments_complete"] for p in pairs),
        "pairs_with_undefined_conditional_belief": sum(p["truth_discount"] is None for p in pairs),
        "missing_judgments": sum(r["judgment_status"] == "missing" for r in listeners),
        "invalid_judgments": sum(r["judgment_status"] in {"invalid", "duplicate"} for r in listeners),
        "analysis_policy_sha256": digest(analysis_policy) if analysis_policy is not None else None,
        "analysis_status": "candidate_analysis_requiring_team_policy_and_access_approval",
        "analysis_source_sha256": {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
            for name in ("analysis.py", "scored_analysis.py", "confirmatory_analysis.py", "deferred_judging.py")
            if (Path(__file__).parent / name).exists()},
        "python_version": sys.version.split()[0], "measurement_limits": analysis.MEASUREMENT_LIMITS,
        "cells": cells, "conditions": conditions, "knobs": knobs, "models": models}
    # Finish every computation before creating an output. A policy rejection must
    # not leave a plausible-looking partial results package behind.
    _verify_source_files(guard["source"], guard["directories"])
    if _hashes(guard["sidecar"]) != guard["sidecar_sha256"]:
        raise ValueError("judgment sidecar changed during analysis; no results published")
    destination.mkdir(parents=True, exist_ok=False)
    for name, rows in (("listeners", listeners), ("pairs", pairs), ("cells", cells),
                       ("conditions", conditions), ("knobs", knobs)):
        (destination / (name + ".csv")).write_text(analysis._csv(rows), encoding="utf-8", newline="")
    (destination / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    (destination / "report.md").write_text(
        "# Separate-judgment analysis\n\n"
        f"Evidence: {summary['evidence_kind']}. Study eligible: false.\n\n"
        f"Generated towns: {len(towns)}. Matched pairs: {len(pairs)}. "
        f"Missing configured towns: {len(provenance['missing_run_ids'])}.\n\n"
        f"Judge profile: {provenance['judge_profile_sha256']}. Attempt policy: {attempt_policy}.\n\n"
        "Invalid, unobserved and unselected outcomes remain missing. "
        "The tables preserve all generated-town and listener denominators. "
        "Conditional listener model contrasts and equally weighted paired-town truth discount are distinct estimands.\n\n"
        f"Planned model status: {models['status']}. See summary.json for policy, fit and Holm-family diagnostics.\n",
        encoding="utf-8")
    return summary
