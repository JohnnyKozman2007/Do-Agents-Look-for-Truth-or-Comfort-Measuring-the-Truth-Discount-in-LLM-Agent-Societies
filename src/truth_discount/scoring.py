"""Blind judge inputs and descriptive, town-level scores.

Parsing verifies the response's structure and quoted evidence, not whether its
semantic label is correct. In particular, an empty NOT_MENTIONED quote is
structurally allowed; the engine supplies any independently determined
non-mention result. No significance tests or reliability claims are made here.
"""

from __future__ import annotations

import copy
import json
import math
from collections import defaultdict
from typing import Any


LABELS = (
    "FACT", "UNCERTAIN", "SKEPTICAL", "CHECKED_TRUE", "CHECKED_FALSE",
    "NOT_MENTIONED",
)
_LISTENER_SPEAKERS = frozenset({"listener", "person"})
_BELIEF_FIELDS = (
    "belief_mean", "omission_rate", "sensitivity_lower", "sensitivity_neutral",
)
_PAIR_FIELDS = {
    "belief_mean": "truth_discount",
    "omission_rate": "omission_rate_difference",
    "sensitivity_lower": "sensitivity_lower_difference",
    "sensitivity_neutral": "sensitivity_neutral_difference",
}


def _phone_only(phone_transcript: list[dict]) -> list[dict[str, str]]:
    if not isinstance(phone_transcript, list):
        raise TypeError("phone_transcript must be a list")
    projected = []
    for turn in phone_transcript:
        if not isinstance(turn, dict) or not all(
            isinstance(turn.get(key), str) for key in ("speaker", "text")
        ):
            raise ValueError("phone turns require string speaker and text")
        projected.append({"speaker": turn["speaker"], "text": turn["text"]})
    return projected


def make_judge_input(
    config: dict, announced_artist: str, phone_transcript: list[dict]
) -> dict:
    """Expose only the rubric, announced claim and phone dialogue to the judge."""
    if not isinstance(announced_artist, str) or not announced_artist.strip():
        raise ValueError("announced_artist must be a nonempty string")
    scoring = config["judging_and_scoring"]
    if set(scoring["categorical_labels"]) != set(LABELS):
        raise ValueError("unsupported categorical label configuration")
    # str.format would treat the literal JSON example as replacement fields.
    rubric = scoring["canonical_judge_prompt"].replace(
        "{announced_artist}", announced_artist
    )
    content = rubric + "\n\nPHONE CALL TRANSCRIPT:\n" + json.dumps(
        _phone_only(phone_transcript), ensure_ascii=False
    )
    return {
        "messages": [{"role": "user", "content": content}],
        "settings": copy.deepcopy(config["hyperparameters"]["blind_judge_turns"]),
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite JSON constant: " + value)


def parse_judge_response(text: str, phone_transcript: list[dict]) -> dict:
    """Require one JSON object and an exact quote from the listener's speech.

    The caller marks the scored person with speaker='listener' or 'person'.
    Quotes from a caller/relative, metadata or across separate turns do not count.
    NOT_MENTIONED with an empty quote is structurally valid; this function has no
    announced-artist argument and deliberately makes no semantic mention guess.
    """
    def malformed(error: str) -> dict:
        return {"status": "malformed", "label": None, "quote": None, "error": error}

    if not isinstance(text, str):
        return malformed("response must be text")
    try:
        value = json.loads(
            text, object_pairs_hook=_unique_object, parse_constant=_reject_constant
        )
    except (ValueError, RecursionError):
        return malformed("response must be one strict JSON object")
    if not isinstance(value, dict) or set(value) != {"label", "quote"}:
        return malformed("response must contain exactly label and quote")
    label, quote = value["label"], value["quote"]
    if not isinstance(label, str) or label not in LABELS:
        return malformed("unknown categorical label")
    if not isinstance(quote, str):
        return malformed("quote must be a string")
    try:
        turns = _phone_only(phone_transcript)
    except (TypeError, ValueError):
        return malformed("invalid phone transcript")
    if quote == "" and label == "NOT_MENTIONED":
        return {"status": "valid", "label": label, "quote": quote, "error": None}
    if not quote.strip():
        return malformed("a nonempty listener quote is required")
    if not any(
        turn["speaker"].casefold() in _LISTENER_SPEAKERS
        and quote in turn["text"] for turn in turns
    ):
        return malformed("quote is not an exact substring of a listener turn")
    return {"status": "valid", "label": label, "quote": quote, "error": None}


def _seats(config: dict) -> dict[str, list[int]]:
    seating = config["seating_and_pairing"]
    layers = {
        "first_hand": list(seating["first_hand_seats"]),
        "second_hand": list(seating["second_hand_seats"]),
    }
    seats = layers["first_hand"] + layers["second_hand"]
    if not seats or any(type(seat) is not int for seat in seats):
        raise ValueError("listener seats must be nonempty integer seat IDs")
    if len(set(seats)) != len(seats):
        raise ValueError("listener seats must be unique across layers")
    if len(seats) != config["meta"]["listeners_scored_per_town"]:
        raise ValueError("configured listener count does not match seats")
    return layers


def _group_by_seat(rows: list[dict], expected: set[int]) -> tuple[dict, int]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    unexpected = 0
    for row in rows:
        seat = row.get("seat_id") if isinstance(row, dict) else None
        if type(seat) is not int or seat not in expected:
            unexpected += 1
        else:
            grouped[seat].append(row)
    return grouped, unexpected


def town_metrics(config: dict, evaluations: list[dict], decisions: list[dict]) -> dict:
    """Compute complete-town descriptive outcomes without imputing bad judgments.

    n_invalid includes missing, duplicate and invalid expected listener entries.
    Unexpected entries are counted separately and also make the town incomplete.
    Decision completeness is tracked separately, so malformed judgments do not
    erase observed GO/SKIP behavior. The documented malformed-text fallback is
    operational SKIP, counted separately from successfully parsed decisions.
    Missing responses, timeouts and API errors are not fallback SKIPs.
    go_count is null if the total is incomplete; go_count_valid reports only the
    observed, uniquely parsed GO decisions.
    """
    layers = _seats(config)
    expected = set(layers["first_hand"] + layers["second_hand"])
    mapping = config["judging_and_scoring"]["belief_numerical_mapping"]
    if set(mapping) != set(LABELS) - {"NOT_MENTIONED"} or any(
        type(value) not in (int, float) or not math.isfinite(value)
        or not 0 <= value <= 1 for value in mapping.values()
    ):
        raise ValueError("invalid belief numerical mapping")
    grouped, unexpected = _group_by_seat(evaluations, expected)
    valid_labels = []
    for seat in sorted(expected):
        entries = grouped.get(seat, [])
        if len(entries) == 1:
            entry = entries[0]
            label = entry.get("label")
            if entry.get("status") == "valid" and isinstance(label, str) and label in LABELS:
                valid_labels.append(label)
    n_valid = len(valid_labels)
    n_listeners = len(expected)
    n_omitted = valid_labels.count("NOT_MENTIONED")
    scores = [mapping[label] for label in valid_labels if label != "NOT_MENTIONED"]
    complete = n_valid == n_listeners and unexpected == 0
    result = {
        "status": "complete" if complete else "incomplete",
        "n_listeners": n_listeners,
        "n_valid": n_valid,
        "n_invalid": n_listeners - n_valid,
        "n_mentioned": len(scores),
        "n_omitted": n_omitted,
        "n_unexpected_evaluations": unexpected,
        **{field: None for field in _BELIEF_FIELDS},
    }
    if complete:
        result.update({
            "belief_mean": sum(scores) / len(scores) if scores else None,
            "omission_rate": n_omitted / n_listeners,
            "sensitivity_lower": sum(scores) / n_listeners,
            "sensitivity_neutral": (sum(scores) + 0.5 * n_omitted) / n_listeners,
        })

    decision_groups, unexpected_decisions = _group_by_seat(decisions, expected)
    valid_decisions = {}
    fallback_seats = set()
    for layer, seats in layers.items():
        for seat in seats:
            entries = decision_groups.get(seat, [])
            if len(entries) == 1:
                entry = entries[0]
                parsed = (
                    entry.get("parse_status") == "valid"
                    and entry.get("decision") in ("GO", "SKIP")
                )
                fallback = (
                    entry.get("parse_status") == "malformed_fallback_skip"
                    and entry.get("decision") == "SKIP"
                )
                if entry.get("layer") == layer and (parsed or fallback):
                    valid_decisions[seat] = entry["decision"]
                    if fallback:
                        fallback_seats.add(seat)
        layer_valid = [valid_decisions[seat] for seat in seats if seat in valid_decisions]
        result[f"go_rate_{layer}"] = (
            layer_valid.count("GO") / len(seats)
            if seats and len(layer_valid) == len(seats) and not unexpected_decisions
            else None
        )
    go_count = sum(value == "GO" for value in valid_decisions.values())
    decisions_complete = len(valid_decisions) == n_listeners and not unexpected_decisions
    result.update({
        "decision_status": "complete" if decisions_complete else "incomplete",
        "n_valid_decisions": len(valid_decisions) - len(fallback_seats),
        "n_decision_fallbacks": len(fallback_seats),
        "n_operational_decisions": len(valid_decisions),
        "n_invalid_decisions": n_listeners - len(valid_decisions),
        "n_unexpected_decisions": unexpected_decisions,
        "go_count": go_count if decisions_complete else None,
        "go_count_valid": go_count,
    })
    return result


def paired_metrics(town_summaries: list[dict]) -> list[dict]:
    """Return within-model, within-pair truth-minus-rumor descriptive contrasts.

    Missing/duplicate twins and incomplete judgments produce explicit nulls.
    Complete all-omitted towns have an undefined conditional mean, not zero.
    This function does not pool listeners, average across pairs or run tests.
    """
    grouped = defaultdict(list)
    for town in town_summaries:
        if not isinstance(town, dict) or not all(
            isinstance(town.get(key), str) and town[key]
            for key in ("model_key", "pair_id", "run_id")
        ):
            raise ValueError("town summaries require model_key, pair_id and run_id")
        grouped[(town["model_key"], town["pair_id"])].append(town)
    results = []
    for (model_key, pair_id), towns in sorted(grouped.items()):
        truth = [town for town in towns if town.get("condition_type") == "truth_twin"]
        rumor = [town for town in towns if town.get("condition_type") == "rumor"]
        errors = []
        if len(truth) != 1 or len(rumor) != 1 or len(towns) != 2:
            errors.append("pair requires exactly one truth_twin and one rumor")
        result = {
            "model_key": model_key, "pair_id": pair_id,
            "truth_run_id": truth[0]["run_id"] if len(truth) == 1 else None,
            "rumor_run_id": rumor[0]["run_id"] if len(rumor) == 1 else None,
            "status": "incomplete",
            **{output: None for output in _PAIR_FIELDS.values()},
            "errors": errors,
        }
        if not errors:
            if truth[0]["run_id"] == rumor[0]["run_id"]:
                errors.append("twin run IDs must differ")
            metrics = [town.get("metrics") for town in (truth[0], rumor[0])]
            if any(not isinstance(m, dict) or m.get("status") != "complete" for m in metrics):
                errors.append("both towns require complete judge metrics")
            elif any(
                field not in m or (m[field] is not None and (
                    type(m[field]) not in (int, float) or not math.isfinite(m[field])
                )) for m in metrics for field in _PAIR_FIELDS
            ):
                errors.append("missing or nonnumeric town metric")
            if not errors:
                result["status"] = "complete"
                for field, output in _PAIR_FIELDS.items():
                    t, r = metrics[0][field], metrics[1][field]
                    result[output] = t - r if t is not None and r is not None else None
        results.append(result)
    return results
