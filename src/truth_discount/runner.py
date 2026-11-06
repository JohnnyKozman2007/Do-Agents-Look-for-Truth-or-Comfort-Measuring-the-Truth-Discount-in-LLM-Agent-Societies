"""Config-driven five-scene pilot orchestration, currently offline only."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import re
import time
from pathlib import Path
from typing import Any

from .config import render_contexts, render_template, render_values
from .contracts import (Backend, GenerationRequest, GenerationResponse, MalformedGeneration,
                        canonical_bytes, capture, clone, digest)
from .scoring import make_judge_input, parse_judge_response, town_metrics


def parse_check_decision(text: str) -> dict[str, Any]:
    match = re.search(r"\b(GO|SKIP)\b", text.strip().upper())
    return {"decision": match.group(1) if match else "SKIP",
            "parse_status": "valid" if match else "malformed_fallback_skip",
            "raw_response": text}


def concert_mentioned(text: str, artists: list[str]) -> bool:
    pattern = r"\b(?:concert|" + "|".join(re.escape(a) for a in artists) + r")\b"
    return re.search(pattern, text, re.IGNORECASE) is not None


async def _phase(tasks: list[Any]) -> None:
    # Await every started callback before persisting a failure bundle.
    outcomes = await asyncio.gather(*tasks, return_exceptions=True)
    for value in outcomes:
        if isinstance(value, BaseException):
            raise value


async def run_town(config: dict[str, Any], run: dict[str, Any], backend: Backend,
                   output_root: Path) -> dict[str, Any]:
    if getattr(backend, "evidence_kind", None) != "synthetic_fixture":
        raise ValueError("this runner currently accepts synthetic offline backends only")
    run = clone(run)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,159}", run["run_id"]):
        raise ValueError("unsafe run_id")
    contexts = render_contexts(config, run)
    histories = {seat: [{"role": "system", "content": text}] for seat, text in contexts.items()}
    budgets = {seat: config["meta"]["initial_budget_usd"] for seat in range(1, 13)}
    directory = Path(output_root) / run["run_id"]
    directory.mkdir(parents=True)  # Never overwrite an earlier town.
    templates = config["prompts_and_templates"]
    personas = {p["id"]: p for p in config["personas"]}
    names = {seat: personas[run["seating_assignment"][str(seat)]]["name"] for seat in range(13)}
    town = {
        **run, "schema_version": "truth-discount-offline-0.1",
        "evidence_kind": "synthetic_fixture", "study_eligible": False,
        "config_version": config["meta"]["version"], "config_sha256": digest(config),
        "run_status": "completed", "error": None, "source_mode": "offline_generated_exact_prompt",
        "source_exact_text_match": None,
        "scene_statuses": {str(i): "not_executed" for i in range(1, 6)},
        "scene_1_departure_broadcast_text": None,
        "scene_2_first_hand_decisions": [], "scene_3_catch_up_transcripts": [],
        "scene_3_poster_evidence_passed": [], "scene_4_second_hand_decisions": [],
        "scene_5_phone_transcripts": [], "scene_5_funnel_step_mentioned": {},
        "judge_inputs": [], "judge_evaluations": [], "calls": [],
        "timestamps": {"started_utc": datetime.now(timezone.utc).isoformat()},
        "token_usage": {"provider_api_calls": 0, "input_tokens": None, "output_tokens": None,
                        "cost_usd": None, "fixture_callback_invocations": 0},
    }
    active_scene = 1
    fatal: BaseException | None = None

    def add_other(seat: int, speaker: str, text: str) -> None:
        formatted = render_template(templates["spoken_line_format"],
                                    {"speaker_name": speaker, "text": text})
        histories[seat].append({"role": "user", "content": formatted})

    async def call(seat: int, scene: int, turn: int, prompt: str | None = None,
                   *, kind: str = "chat", judge_input: dict[str, Any] | None = None) -> str:
        if judge_input is None:
            if prompt is not None:
                histories[seat].append({"role": "user", "content": prompt})
            messages = clone(histories[seat])
            setting_key = "verification_decision_turns" if kind == "decision" else "conversational_turns"
            settings = clone(config["hyperparameters"][setting_key])
            model_key = run["model_key"]
        else:
            messages = clone(judge_input["messages"])
            settings = clone(judge_input["settings"])
            model_key = config["models"]["judge_models"][0]["key"]
        request = GenerationRequest(messages, settings, model_key, kind, scene, seat, turn)
        event = {"call_id": len(town["calls"]) + 1, "kind": kind, "scene": scene,
                 "seat_id": seat, "turn": turn, "model_key": model_key,
                 "request": asdict(request), "request_sha256": digest(asdict(request)),
                 "status": "started", "response": None, "error": None,
                 "backend": "synthetic_fixture", "provider_api_calls": 0,
                 "actual_provider": None, "actual_model": None,
                 "token_usage": None, "cost_usd": None, "attempt_index": 1}
        town["calls"].append(event)
        started = time.perf_counter()
        try:
            response = await backend.generate(GenerationRequest(**clone(asdict(request))))
            event["raw_response"] = capture(response)
            if (not isinstance(response, GenerationResponse) or not isinstance(response.text, str)
                    or (kind == "chat" and not response.text.strip())):
                raise MalformedGeneration("expected GenerationResponse.text; chat replies must be nonempty")
            if response.usage is not None:
                raise MalformedGeneration("offline callback cannot claim real provider token usage")
            event.update(status="completed", response=response.text)
            if judge_input is None:
                histories[seat].append({"role": "assistant", "content": response.text})
            return response.text
        except BaseException as exc:
            event.update(status="cancelled" if isinstance(exc, asyncio.CancelledError) else
                         "timeout" if isinstance(exc, TimeoutError) else
                         "malformed_response" if isinstance(exc, MalformedGeneration) else "callback_error",
                         error=type(exc).__name__)
            raise
        finally:
            event["elapsed_seconds"] = time.perf_counter() - started

    async def decision(seat: int, scene: int, layer: str) -> None:
        text = await call(seat, scene, 1, templates["scene_2_and_4_check_prompt"], kind="decision")
        result = {"seat_id": seat, "layer": layer, **parse_check_decision(text)}
        if result["decision"] == "GO":
            budgets[seat] -= config["meta"]["check_bus_cost_usd"]
            values = render_values(config, run, seat)
            observation = render_template(templates["scene_2_and_4_memory_on_go"], values)
            histories[seat].append({"role": "user", "content": observation})
            histories[seat].append({"role": "user", "content":
                                   f"You have ${budgets[seat]} of spending money left this week."})
            result["poster_observation"] = observation
        else:
            result["poster_observation"] = None
        result["balance_usd"] = budgets[seat]
        key = "scene_2_first_hand_decisions" if scene == 2 else "scene_4_second_hand_decisions"
        town[key].append(result)

    async def catch_up(pair: dict[str, Any]) -> None:
        first, second = pair["first_hand_seat"], pair["second_hand_seat"]
        values_s, values_f = render_values(config, run, second), render_values(config, run, first)
        lines = []
        town["scene_3_catch_up_transcripts"].append({"first_hand_seat": first, "second_hand_seat": second,
                                                  "lines": lines})
        opener = render_template(templates["scene_3_second_hand_scripted_opener"], values_s)
        histories[second].append({"role": "assistant", "content": opener})
        add_other(first, names[second], opener)
        lines.append({"turn": 1, "seat_id": second, "speaker": names[second], "text": opener, "scripted": True})
        answer = await call(first, 3, 2, render_template(templates["scene_3_first_hand_cue"], values_f))
        add_other(second, names[first], answer)
        lines.append({"turn": 2, "seat_id": first, "speaker": names[first], "text": answer, "scripted": False})
        reaction = await call(second, 3, 3)
        add_other(first, names[second], reaction)
        lines.append({"turn": 3, "seat_id": second, "speaker": names[second], "text": reaction, "scripted": False})
        closing = await call(first, 3, 4, render_template(templates["scene_3_first_hand_closing_cue"], values_f))
        add_other(second, names[first], closing)
        lines.append({"turn": 4, "seat_id": first, "speaker": names[first], "text": closing, "scripted": False})
        checked = next(d for d in town["scene_2_first_hand_decisions"] if d["seat_id"] == first)
        cell = next(c for c in config["pilot_cells"] if c["cell_id"] == run["cell_id"])
        poster_line = next(c["ground_truth_noticeboard"] for c in cell["conditions"]
                           if c["condition_type"] == run["condition_type"])
        poster = render_template(poster_line, values_f)
        quotes = [line["text"] for line in lines if line["seat_id"] == first and poster in line["text"]]
        town["scene_3_poster_evidence_passed"].append({
            "first_hand_seat": first, "second_hand_seat": second, "partner_checked": checked["decision"] == "GO",
            "literal_poster_quote_found": bool(quotes), "supporting_quotes": quotes,
            "rule": "literal_full_poster_match_only_not_semantic_adjudication"})

    async def phone(seat: int) -> None:
        values = render_values(config, run, seat)
        histories[seat].append({"role": "user", "content": render_template(templates["scene_5_phone_cue"], values)})
        funnel = {int(x["step"]): x["loved_one_line"] for x in templates["scene_5_phone_call_funnel"]}
        transcript: list[dict[str, Any]] = []
        town["scene_5_phone_transcripts"].append({"seat_id": seat, "lines": transcript})
        mention_step = None
        for step in range(1, 5):
            line = funnel[step]
            transcript.append({"speaker": "caller", "name": values["loved_one"], "text": line, "funnel_step": step})
            add_other(seat, values["loved_one"], line)
            reply = await call(seat, 5, step)
            transcript.append({"speaker": "listener", "name": names[seat], "text": reply, "funnel_step": step})
            if concert_mentioned(reply, config["artists"]["artist_pool"]):
                mention_step = step
                break
        town["scene_5_funnel_step_mentioned"][str(seat)] = mention_step
        if mention_step is not None:
            transcript.append({"speaker": "caller", "name": values["loved_one"], "text": funnel[5], "funnel_step": 5})
            add_other(seat, values["loved_one"], funnel[5])
            reply = await call(seat, 5, 5)
            transcript.append({"speaker": "listener", "name": names[seat], "text": reply, "funnel_step": 5})
        transcript.append({"speaker": "caller", "name": values["loved_one"], "text": funnel[6], "funnel_step": 6})
        add_other(seat, values["loved_one"], funnel[6])
        if mention_step is None:
            result = {"seat_id": seat, "status": "valid", "label": "NOT_MENTIONED", "quote": "",
                      "error": None, "provenance": "runner_phone_funnel_rule"}
        else:
            judge_input = make_judge_input(config, run["announced_artist"], transcript)
            custom_id = hashlib.sha256(f"{run['run_id']}:{seat}".encode()).hexdigest()[:32]
            town["judge_inputs"].append({"custom_id": custom_id, "input": clone(judge_input),
                                         "input_sha256": digest(judge_input), "seat_id_private": seat})
            raw = await call(seat, 5, 0, kind="judge", judge_input=judge_input)
            result = {"seat_id": seat, **parse_judge_response(raw, transcript), "provenance": "synthetic_judge_callback"}
        town["judge_evaluations"].append(result)

    try:
        town["scene_statuses"]["1"] = "started"
        broadcast = await call(0, 1, 1, "Share your departure message now.")
        town["scene_1_departure_broadcast_text"] = broadcast
        fixed = render_template(templates["scene_1_source_departure_broadcast"], render_values(config, run, 0))
        town["source_exact_text_match"] = broadcast == fixed
        for seat in range(1, 7):
            add_other(seat, names[0], broadcast)
        town["scene_statuses"]["1"] = "completed"
        active_scene = 2
        town["scene_statuses"]["2"] = "started"
        await _phase([decision(seat, 2, "first_hand") for seat in range(1, 7)])
        town["scene_statuses"]["2"] = "completed"
        active_scene = 3
        town["scene_statuses"]["3"] = "started"
        await _phase([catch_up(pair) for pair in run["catch_up_pairs"]])
        town["scene_statuses"]["3"] = "completed"
        active_scene = 4
        town["scene_statuses"]["4"] = "started"
        await _phase([decision(seat, 4, "second_hand") for seat in range(7, 13)])
        town["scene_statuses"]["4"] = "completed"
        active_scene = 5
        town["scene_statuses"]["5"] = "started"
        await _phase([phone(seat) for seat in range(1, 13)])
        town["scene_statuses"]["5"] = "completed"
    except BaseException as exc:
        town["run_status"] = "cancelled" if isinstance(exc, asyncio.CancelledError) else "timeout" if isinstance(exc, TimeoutError) else "malformed_response" if isinstance(exc, MalformedGeneration) else "runner_error"
        town["scene_statuses"][str(active_scene)] = "failed"
        town["error"] = {"type": type(exc).__name__, "scene": active_scene}
        if not isinstance(exc, (TimeoutError, MalformedGeneration)):
            fatal = exc
    finally:
        town["agent_histories"] = {str(k): v for k, v in histories.items()}
        town["final_budgets_usd"] = {str(k): v for k, v in budgets.items()}
        for key in ("scene_2_first_hand_decisions", "scene_4_second_hand_decisions", "scene_5_phone_transcripts", "judge_evaluations"):
            town[key].sort(key=lambda x: x["seat_id"])
        for key in ("scene_3_catch_up_transcripts", "scene_3_poster_evidence_passed"):
            town[key].sort(key=lambda x: x["first_hand_seat"])
        decisions = town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]
        town["metrics"] = town_metrics(config, town["judge_evaluations"], decisions)
        town["timestamps"]["finished_utc"] = datetime.now(timezone.utc).isoformat()
        town["token_usage"]["fixture_callback_invocations"] = len(town["calls"])
        from .artifacts import save_town
        save_town(directory, town, config)
    if fatal is not None:
        raise fatal
    return clone(town)
