"""Re-ask the judge for phone calls whose saved label was malformed.

The live judge sometimes returns a quote that is not the listener's words (it quotes the
caller, or adds a word, or changes an apostrophe). One malformed label leaves its town's
judge metrics incomplete, which drops the whole twin pair. The exact judge input for every
call is saved, so those calls can be asked again later without collecting anything anew.

Saved towns are never modified, so their replay check stays valid. Each re-judged call is
appended to <output>/rejudged.jsonl with every attempt's reply and receipt. Spending goes
through the same ledger, request limits and receipts as a paid run. Rerunning skips calls
already in the file, so a stopped re-judge can simply be started again.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from .artifacts import audit_town
from .config import load_config
from .contracts import GenerationRequest, clone, digest
from .scoring import paired_metrics, parse_judge_response, town_metrics

REJUDGE_FILE = "rejudged.jsonl"
PROVENANCE = "provider_rejudge_callback"


def _towns(output_root: Path) -> list[tuple[Path, dict]]:
    """Every saved, replay-verified, completed town in one output directory."""
    towns = []
    for directory in sorted(p.parent for p in Path(output_root).glob("*/manifest.json")):
        town = audit_town(directory)
        if town["run_status"] == "completed":
            towns.append((directory, town))
    return towns


def malformed_items(output_root: Path, towns: list | None = None) -> list[dict]:
    items = []
    for _, town in (towns if towns is not None else _towns(output_root)):
        inputs = {x["seat_id_private"]: x for x in town["judge_inputs"]}
        for evaluation in town["judge_evaluations"]:
            if evaluation.get("status") == "valid":
                continue
            seat = evaluation["seat_id"]
            judged = inputs[seat]
            phone = next(p for p in town["scene_5_phone_transcripts"] if p["seat_id"] == seat)
            items.append({"run_id": town["run_id"], "seat_id": seat, "custom_id": judged["custom_id"],
                          "input": judged["input"], "input_sha256": judged["input_sha256"],
                          "lines": phone["lines"], "original_error": evaluation.get("error")})
    return items


def read_rejudged(output_root: Path) -> dict[str, dict]:
    path = Path(output_root) / REJUDGE_FILE
    if not path.exists():
        return {}
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["custom_id"]] = row
    return rows


def _append(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


async def rejudge(output_root: Path, backend, judge_key: str, *, attempts: int = 3) -> dict:
    """Re-ask each malformed call up to `attempts` times; stop on any unclear charge."""
    if type(attempts) is not int or not 1 <= attempts <= 5:
        raise ValueError("attempts must be an integer from 1 to 5")
    output_root = Path(output_root)
    done = read_rejudged(output_root)
    towns = _towns(output_root)
    todo = [item for item in malformed_items(output_root, towns) if item["custom_id"] not in done]
    target = output_root / REJUDGE_FILE
    manifest_sha256 = digest(backend.manifest)

    async def one(item: dict) -> None:
        tries = []
        for turn in range(1, attempts + 1):
            request = GenerationRequest(clone(item["input"]["messages"]), clone(item["input"]["settings"]),
                                        judge_key, "judge", 5, item["seat_id"], turn)
            response = await backend.generate(request)
            parsed = parse_judge_response(response.text, item["lines"])
            tries.append({"turn": turn, "response": response.text, "receipt": clone(response.usage), "parsed": parsed})
            if parsed["status"] == "valid":
                break
        final = tries[-1]["parsed"]
        _append(target, {"run_id": item["run_id"], "seat_id": item["seat_id"], "custom_id": item["custom_id"],
                         "input_sha256": item["input_sha256"], "original_error": item["original_error"],
                         "attempts": tries, "final": {**final, "provenance": PROVENANCE},
                         "evidence_kind": backend.evidence_kind, "provider_manifest_sha256": manifest_sha256,
                         "cost_usd": sum(t["receipt"].get("cost_usd") or 0 for t in tries)})

    outcomes = await asyncio.gather(*(one(item) for item in todo), return_exceptions=True)
    failures = [o for o in outcomes if isinstance(o, BaseException)]
    result = summary(output_root, towns)
    result.update(attempted_now=len(todo), failed_now=len(failures))
    if failures:
        raise ValueError(f"{len(failures)} re-judge call(s) failed; record held charges, then rerun "
                           f"(finished calls are kept): {type(failures[0]).__name__}: {failures[0]}")
    return result


def merged_evaluations(town: dict, rejudged: dict[str, dict]) -> list[dict]:
    """The town's judge evaluations with valid re-judged labels in place of malformed ones."""
    by_seat = {x["seat_id_private"]: x["custom_id"] for x in town["judge_inputs"]}
    merged = []
    for evaluation in town["judge_evaluations"]:
        row = rejudged.get(by_seat.get(evaluation["seat_id"]))
        if evaluation.get("status") != "valid" and row and row["final"]["status"] == "valid":
            merged.append({"seat_id": evaluation["seat_id"], **row["final"]})
        else:
            merged.append(evaluation)
    return merged


def summary(output_root: Path, towns: list | None = None) -> dict[str, Any]:
    """Complete twin pairs before and after using the re-judged labels."""
    output_root = Path(output_root)
    rejudged = read_rejudged(output_root)
    towns = towns if towns is not None else _towns(output_root)
    if not towns:
        return {"output_root": str(output_root), "towns": 0}
    config = load_config(towns[0][0] / "config.json")
    before, after = [], []
    for _, town in towns:
        decisions = town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]
        before.append(town)
        after.append({**town, "metrics": town_metrics(config, merged_evaluations(town, rejudged), decisions)})
    items = malformed_items(output_root, towns)
    fixed = sum(1 for i in items if rejudged.get(i["custom_id"], {}).get("final", {}).get("status") == "valid")
    return {"output_root": str(output_root), "towns": len(towns), "malformed_labels": len(items),
            "rejudged": sum(1 for i in items if i["custom_id"] in rejudged), "fixed": fixed,
            "still_malformed": len(items) - fixed,
            "complete_pairs_before": sum(p["status"] == "complete" for p in paired_metrics(before)),
            "complete_pairs_after": sum(p["status"] == "complete" for p in paired_metrics(after)),
            "pairs": len(paired_metrics(before)),
            "rejudge_cost_usd": round(sum(r.get("cost_usd", 0) for r in rejudged.values()), 8)}
