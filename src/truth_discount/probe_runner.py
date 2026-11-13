"""Two-source probe towns: the main five scenes, with two scripted departures in Scene 1.

The call, receipt and failure handling copy runner.run_town line for line (runner.py is a
fingerprinted main-run module and stays untouched). Differences from a main town:
- Scene 1 inserts two scripted departure lines, in the run's counterbalanced order, into the
  six first-hand listeners' histories. Sources make no model calls and keep no history.
- Listener contexts and the Scene 3 first-hand cue name both sources (probe_config templates).
Scenes 2-5, settings, the GO observation, the phone funnel and its regex trigger are the main ones.
Judging is always deferred: probe towns are sealed as ungraded simulations.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import re
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import render_template
from .contracts import (Backend, GenerationRequest, GenerationResponse, MalformedGeneration,
                        capture, clone, digest, usage_totals)
from .probe_config import (SEATS, departure_text, ordered_sources, render_listener_values,
                           render_probe_contexts, source_names)
from .runner import _phase, concert_mentioned, evidence_line, parse_check_decision

PROBE_SCHEMA = "truth-discount-probe-simulation-0.1"
DIAGNOSTIC_LIMITS = {
    "scene_5_mention_step_confirmed": "Not computed: evaluation pending",
    "scene_3_poster_evidence_passed": "Checked plus artist/board keywords, not semantic evidence-transfer adjudication",
}


async def run_probe_town(config: dict[str, Any], spec: dict[str, Any], run: dict[str, Any], backend: Backend,
                         output_root: Path) -> dict[str, Any]:
    evidence_kind = getattr(backend, "evidence_kind", None)
    if evidence_kind not in {"synthetic_fixture", "mocked_provider", "development_pilot"}:
        raise ValueError("unsupported backend evidence kind; expected synthetic_fixture, mocked_provider or development_pilot")
    execution = None
    if evidence_kind != "synthetic_fixture":
        execution = clone(backend.manifest)
        if not isinstance(execution, dict) or not execution.get("approved"):
            raise ValueError("provider execution manifest is not approved")
    run = clone(run)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,159}", run["run_id"]):
        raise ValueError("unsafe run_id")
    contexts = render_probe_contexts(config, spec, run)
    histories = {seat: [{"role": "system", "content": text}] for seat, text in contexts.items()}
    budgets = {seat: config["meta"]["initial_budget_usd"] for seat in SEATS}
    directory = Path(output_root) / run["run_id"]
    directory.mkdir(parents=True)  # Never overwrite an earlier town.
    templates = config["prompts_and_templates"]
    personas = {p["id"]: p for p in config["personas"]}
    names = {seat: personas[run["listener_seating"][str(seat)]]["name"] for seat in SEATS}
    speakers = source_names(config, run)
    town = {
        **run, "schema_version": PROBE_SCHEMA,
        "evidence_kind": evidence_kind, "study_eligible": False,
        "config_version": config["meta"]["version"], "config_sha256": digest(config),
        "probe_spec_sha256": digest(spec), "dna_selection_status": spec["dna_selection"]["status"],
        "generation_attempt_id": uuid4().hex, "generation_status": "completed", "evaluation_status": "pending",
        "run_status": "completed", "error": None, "source_mode": "scripted_insert",
        "scene_statuses": {str(i): "not_executed" for i in range(1, 6)},
        "scene_1_departures": [],
        "scene_2_first_hand_decisions": [], "scene_3_catch_up_transcripts": [],
        "scene_3_poster_evidence_passed": [], "scene_4_second_hand_decisions": [],
        "scene_5_phone_transcripts": [], "scene_5_funnel_step_mentioned": {}, "scene_5_mention_step_confirmed": {},
        "judge_inputs": [], "judge_evaluations": [], "calls": [],
        "timestamps": {"started_utc": datetime.now(timezone.utc).isoformat()},
        "token_usage": {"provider_api_calls": 0, "input_tokens": None, "output_tokens": None,
                        "cost_usd": None, "fixture_callback_invocations": 0},
        "diagnostic_limits": dict(DIAGNOSTIC_LIMITS),
    }
    if execution is not None:
        town["execution_manifest"] = execution
        town["execution_manifest_sha256"] = digest(execution)
    active_scene = 1
    fatal: BaseException | None = None

    def add_other(seat: int, speaker: str, text: str) -> None:
        formatted = render_template(templates["spoken_line_format"], {"speaker_name": speaker, "text": text})
        histories[seat].append({"role": "user", "content": formatted})

    async def call(seat: int, scene: int, turn: int, prompt: str | None = None, *, kind: str = "chat") -> str:
        if prompt is not None:
            histories[seat].append({"role": "user", "content": prompt})
        messages = clone(histories[seat])
        setting_key = "verification_decision_turns" if kind == "decision" else "conversational_turns"
        settings = clone(config["hyperparameters"][setting_key])
        model_key = run["model_key"]
        request = GenerationRequest(messages, settings, model_key, kind, scene, seat, turn)
        event = {"call_id": len(town["calls"]) + 1, "kind": kind, "scene": scene,
                 "seat_id": seat, "turn": turn, "model_key": model_key,
                 "request": asdict(request), "request_sha256": digest(asdict(request)),
                 "status": "started", "response": None, "error": None,
                 "backend": evidence_kind, "provider_api_calls": 0,
                 "actual_provider": None, "actual_model": None,
                 "token_usage": None, "cost_usd": None, "attempt_index": 1}
        town["calls"].append(event)
        started = time.perf_counter()
        try:
            response = await backend.generate(GenerationRequest(**clone(asdict(request))))
            event["raw_response"] = capture(response, limit=1_000_000)
            # A charged empty/malformed answer still carries its provider costs.
            if (evidence_kind != "synthetic_fixture" and isinstance(response, GenerationResponse)
                    and isinstance(response.usage, dict)):
                receipt = clone(response.usage)
                count = receipt.get("provider_api_calls")
                if type(count) is not int or count < 1:
                    raise MalformedGeneration("invalid provider attempt count")
                event["token_usage"] = receipt
                for key in ("actual_provider", "actual_model", "provider_api_calls", "cost_usd"):
                    event[key] = receipt.get(key)
            if (not isinstance(response, GenerationResponse) or not isinstance(response.text, str)
                    or (kind == "chat" and not response.text.strip())):
                raise MalformedGeneration("expected GenerationResponse.text; chat replies must be nonempty")
            if evidence_kind == "synthetic_fixture":
                if response.usage is not None:
                    raise MalformedGeneration("offline callback cannot claim real provider token usage")
            else:
                if not isinstance(response.usage, dict) or event["raw_response"]["truncated"]:
                    raise MalformedGeneration("provider response needs complete usage receipt")
                if type(event["provider_api_calls"]) is not int or event["provider_api_calls"] < 1:
                    raise MalformedGeneration("invalid provider attempt count")
            event.update(status="completed", response=response.text)
            histories[seat].append({"role": "assistant", "content": response.text})
            return response.text
        except BaseException as exc:
            if (evidence_kind != "synthetic_fixture" and isinstance(getattr(exc, "receipt", None), dict)
                    and exc.receipt):
                receipt = clone(exc.receipt)
                event["provider_receipt"] = receipt
                event["token_usage"] = receipt
                for key in ("actual_provider", "actual_model", "provider_api_calls", "cost_usd"):
                    event[key] = receipt.get(key)
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
            observation = render_template(templates["scene_2_and_4_memory_on_go"], {"real_artist": run["real_artist"]})
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
        values_s = render_listener_values(config, spec, run, second)
        values_f = render_listener_values(config, spec, run, first)
        lines = []
        town["scene_3_catch_up_transcripts"].append({"first_hand_seat": first, "second_hand_seat": second,
                                                  "lines": lines})
        opener = render_template(templates["scene_3_second_hand_scripted_opener"],
                                 {"partner_name": values_s["partner_name"]})
        histories[second].append({"role": "assistant", "content": opener})
        add_other(first, names[second], opener)
        lines.append({"turn": 1, "seat_id": second, "speaker": names[second], "text": opener, "scripted": True})
        cue = render_template(spec["templates"]["scene_3_first_hand_cue"],
                              {k: values_f[k] for k in ("partner_name", "first_name", "second_name")})
        answer = await call(first, 3, 2, cue)
        add_other(second, names[first], answer)
        lines.append({"turn": 2, "seat_id": first, "speaker": names[first], "text": answer, "scripted": False})
        reaction = await call(second, 3, 3)
        add_other(first, names[second], reaction)
        lines.append({"turn": 3, "seat_id": second, "speaker": names[second], "text": reaction, "scripted": False})
        closing = await call(first, 3, 4, render_template(templates["scene_3_first_hand_closing_cue"],
                                                          {"partner_name": values_f["partner_name"]}))
        add_other(second, names[first], closing)
        lines.append({"turn": 4, "seat_id": first, "speaker": names[first], "text": closing, "scripted": False})
        checked = next(d for d in town["scene_2_first_hand_decisions"] if d["seat_id"] == first)
        quotes = [line["text"] for line in lines
                  if line["seat_id"] == first and evidence_line(line["text"], run["real_artist"])]
        town["scene_3_poster_evidence_passed"].append({
            "first_hand_seat": first, "second_hand_seat": second, "partner_checked": checked["decision"] == "GO",
            "evidence_passed": checked["decision"] == "GO" and bool(quotes), "supporting_quotes": quotes,
            "rule": "checked_then_named_real_artist_and_board_in_one_line"})

    async def phone(seat: int) -> None:
        values = render_listener_values(config, spec, run, seat)
        histories[seat].append({"role": "user", "content": render_template(
            templates["scene_5_phone_cue"], {"loved_one": values["loved_one"], "relation": values["relation"]})})
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
        # Judging is deferred: an ungraded phone is not an omission or a belief label.

    try:
        town["scene_statuses"]["1"] = "started"
        # Both departure lines are scripted and inserted word for word, in counterbalanced order.
        for source in ordered_sources(run):
            text = departure_text(config, spec, run, source)
            town["scene_1_departures"].append({"role": source["role"], "speaker": speakers[source["role"]],
                                               "persona_id": source["persona_id"], "claim": source["claim"],
                                               "announced_artist": source["announced_artist"],
                                               "departure_line": source["departure_line"], "text": text})
            for seat in range(1, 7):
                add_other(seat, speakers[source["role"]], text)
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
        await _phase([phone(seat) for seat in SEATS])
        town["scene_statuses"]["5"] = "completed"
    except BaseException as exc:
        town["run_status"] = ("cancelled" if isinstance(exc, asyncio.CancelledError) else
                              "timeout" if isinstance(exc, TimeoutError) else
                              "malformed_response" if isinstance(exc, MalformedGeneration) else "runner_error")
        town["scene_statuses"][str(active_scene)] = "failed"
        town["error"] = {"type": type(exc).__name__, "scene": active_scene}
        if not isinstance(exc, (TimeoutError, MalformedGeneration)):
            fatal = exc
    finally:
        town["agent_histories"] = {str(k): v for k, v in histories.items()}
        town["final_budgets_usd"] = {str(k): v for k, v in budgets.items()}
        for key in ("scene_2_first_hand_decisions", "scene_4_second_hand_decisions", "scene_5_phone_transcripts"):
            town[key].sort(key=lambda x: x["seat_id"])
        for key in ("scene_3_catch_up_transcripts", "scene_3_poster_evidence_passed"):
            town[key].sort(key=lambda x: x["first_hand_seat"])
        town["metrics"] = None
        town["timestamps"]["finished_utc"] = datetime.now(timezone.utc).isoformat()
        town["token_usage"] = usage_totals(town["calls"], evidence_kind)
        town["generation_status"] = "completed" if town["run_status"] == "completed" else "failed"
        from .probe_artifacts import save_probe_simulation
        save_probe_simulation(directory, town, config, spec)
    if fatal is not None:
        raise fatal
    return clone(town)
