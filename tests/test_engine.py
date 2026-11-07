"""Offline state-machine checks using controlled responses, never provider APIs."""

import asyncio
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from truth_discount.config import build_manifest, load_config  # noqa: E402
from truth_discount.contracts import GenerationResponse  # noqa: E402
from truth_discount.fixtures import FixtureBackend  # noqa: E402
from truth_discount.runner import run_town  # noqa: E402


def prompt_text(request):
    return "\n".join(message["content"] for message in request.messages)


def judge_request(request):
    return "judge" in request.kind


class ControlledBackend:
    """Known speech lets tests distinguish permitted relays from private memory."""

    evidence_kind = "synthetic_fixture"

    def __init__(self, config, run, *, go_seats=(), silent=False, relay=False, mention_step=1):
        self.config = config
        self.run = run
        self.go_seats = set(go_seats)
        self.silent = silent
        self.relay = relay
        self.mention_step = mention_step
        self.requests = []
        self.responses = []
        self.counts = {}
        self.poster = config["prompts_and_templates"]["scene_2_and_4_memory_on_go"].format(
            real_artist=run["real_artist"]
        )
        self.broadcast = config["prompts_and_templates"]["scene_1_source_departure_broadcast"].format(
            announced_artist=run["announced_artist"]
        )

    async def generate(self, request):
        self.requests.append(copy.deepcopy(request))
        key = (request.scene, request.seat, request.kind)
        self.counts[key] = self.counts.get(key, 0) + 1
        if judge_request(request):
            text = json.dumps({"label": "UNCERTAIN", "quote": "The concert might happen, but I am not sure."})
        elif request.scene == 1:
            text = self.broadcast
        elif request.scene in (2, 4):
            text = "GO" if request.seat in self.go_seats else "SKIP"
        elif request.scene == 3:
            if request.seat <= 6:
                text = f"PAIR_{request.seat}_ONLY. I had a busy morning."
                if self.relay and request.seat == 1:
                    text += f" I read the noticeboard: FREE SURPRISE CONCERT: {self.run['real_artist']}."
            else:
                text = "Thanks for telling me. I had a busy morning too."
        elif request.scene == 5:
            if self.silent or request.turn < self.mention_step:
                text = "Work kept me busy. The afternoon passed quickly."
            elif request.turn == self.mention_step:
                text = "I heard about a concert this weekend."
            else:
                text = "The concert might happen, but I am not sure."
        else:
            raise AssertionError(f"Unexpected generation request: {request!r}")
        response = GenerationResponse(text=text)
        self.responses.append((copy.deepcopy(request), copy.deepcopy(response)))
        return response


class EngineTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = load_config(ROOT / "configs" / "pilot_config.json")
        self.run = build_manifest(self.config)[0]
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.output_root = Path(self.tempdir.name)

    async def execute(self, backend, *, config=None, run=None):
        return await run_town(config or self.config, run or self.run, backend, self.output_root)

    async def test_all_five_scenes_and_exact_catchup_call_count(self):
        backend = ControlledBackend(self.config, self.run)
        result = await self.execute(backend)
        self.assertEqual(result["run_status"], "completed")
        self.assertEqual(result["scene_statuses"], {str(scene): "completed" for scene in range(1, 6)})
        self.assertEqual({request.scene for request in backend.requests if not judge_request(request)}, {2, 3, 4, 5})
        self.assertTrue(result["source_exact_text_match"])
        self.assertEqual(result["scene_1_departure_broadcast_text"], backend.broadcast)
        for seat in range(1, 7):
            self.assertIn(backend.broadcast, result["agent_histories"][str(seat)][1]["content"])
        catchup = [request for request in backend.requests if request.scene == 3]
        self.assertEqual(len(catchup), 18)
        for seat in range(1, 7):
            self.assertEqual(sum(request.seat == seat for request in catchup), 2)
            self.assertEqual(sum(request.seat == seat + 6 for request in catchup), 1)
        self.assertEqual(len(result["scene_3_catch_up_transcripts"]), 6)
        for pair in result["scene_3_catch_up_transcripts"]:
            first, second = pair["first_hand_seat"], pair["second_hand_seat"]
            self.assertEqual(second, first + 6)
            self.assertEqual([line["turn"] for line in pair["lines"]], [1, 2, 3, 4])
            self.assertEqual([line["seat_id"] for line in pair["lines"]], [second, first, second, first])
            self.assertEqual([line["scripted"] for line in pair["lines"]], [True, False, False, False])

    async def test_only_go_debits_the_budget_and_receives_direct_poster(self):
        backend = ControlledBackend(self.config, self.run, go_seats={1, 8})
        result = await self.execute(backend)
        decisions = result["scene_2_first_hand_decisions"] + result["scene_4_second_hand_decisions"]
        self.assertEqual(len(decisions), 12)
        self.assertEqual({row["seat_id"] for row in decisions if row["decision"] == "GO"}, {1, 8})
        for row in decisions:
            expected = 35 if row["seat_id"] in {1, 8} else 40
            self.assertEqual(row["balance_usd"], expected)
            self.assertEqual(result["final_budgets_usd"][str(row["seat_id"])], expected)
            self.assertEqual(row["poster_observation"], backend.poster if row["decision"] == "GO" else None)
        for request in backend.requests:
            if judge_request(request) or request.seat is None:
                continue
            text = prompt_text(request)
            if request.seat == 1 and request.scene in (3, 5):
                self.assertIn(backend.poster, text)
            elif request.seat == 8 and request.scene == 5:
                self.assertIn(backend.poster, text)
            elif request.seat in range(1, 13):
                self.assertNotIn(backend.poster, text)

    async def test_secondhand_gets_only_its_partner_speech_before_own_check(self):
        backend = ControlledBackend(self.config, self.run, go_seats={1, 8}, relay=True)
        await self.execute(backend)
        for request in backend.requests:
            if judge_request(request) or request.seat not in range(7, 13):
                continue
            text = prompt_text(request)
            self.assertNotIn(backend.broadcast, text)
            self.assertIn(f"PAIR_{request.seat - 6}_ONLY", text)
            for other_pair in set(range(1, 7)) - {request.seat - 6}:
                self.assertNotIn(f"PAIR_{other_pair}_ONLY", text)
            if request.scene in (3, 4):
                self.assertNotIn(backend.poster, text)
                if request.seat == 7:
                    self.assertIn(f"FREE SURPRISE CONCERT: {self.run['real_artist']}", text)
                else:
                    self.assertNotIn("FREE SURPRISE CONCERT:", text)

    async def test_source_does_not_receive_its_reliability(self):
        config = copy.deepcopy(self.config)
        for values in config["experimental_knobs"]["reliability"].values():
            values["listener_line"] += " PRIVATE_RELIABILITY_SENTINEL."
        backend = ControlledBackend(config, self.run)
        result = await self.execute(backend, config=config)
        self.assertFalse(any(request.scene == 1 for request in backend.requests))
        self.assertNotIn("PRIVATE_RELIABILITY_SENTINEL", result["agent_histories"]["0"][0]["content"])
        listener_decisions = [request for request in backend.requests if request.scene == 2]
        self.assertEqual(len(listener_decisions), 6)
        self.assertTrue(all("PRIVATE_RELIABILITY_SENTINEL" in prompt_text(request) for request in listener_decisions))

    async def test_evidence_passed_needs_a_check_plus_artist_and_board(self):
        backend = ControlledBackend(self.config, self.run, go_seats={1}, relay=True)
        result = await self.execute(backend)
        flags = {p["first_hand_seat"]: p["evidence_passed"] for p in result["scene_3_poster_evidence_passed"]}
        self.assertEqual(flags, {seat: seat == 1 for seat in range(1, 7)})
        run = copy.deepcopy(self.run)
        run["run_id"] += "-no-check"
        result = await self.execute(ControlledBackend(self.config, run, relay=True), run=run)
        self.assertFalse(any(p["evidence_passed"] for p in result["scene_3_poster_evidence_passed"]))

    async def test_judge_receives_phone_and_rubric_without_private_context(self):
        config = copy.deepcopy(self.config)
        for values in config["experimental_knobs"]["reliability"].values():
            values["listener_line"] += " PRIVATE_RELIABILITY_SENTINEL."
        backend = ControlledBackend(config, self.run, go_seats={1, 8})
        await self.execute(backend, config=config)
        judges = [request for request in backend.requests if judge_request(request)]
        self.assertEqual(len(judges), 12)
        for request in judges:
            text = prompt_text(request)
            self.assertIn(self.run["announced_artist"], text)
            self.assertIn("The concert might happen, but I am not sure.", text)
            for forbidden in ("PRIVATE_RELIABILITY_SENTINEL", backend.broadcast, backend.poster,
                              "PAIR_", "condition_type", "source_persona_id", "budget_after"):
                self.assertNotIn(forbidden, text)
            self.assertNotEqual(request.model_key, self.run["model_key"])

    async def test_early_mention_jumps_to_followup_and_never_generates_after_wrap(self):
        backend = ControlledBackend(self.config, self.run)
        await self.execute(backend)
        calls = [request for request in backend.requests if request.scene == 5 and not judge_request(request)]
        self.assertEqual(len(calls), 24)
        for seat in range(1, 13):
            turns = [request for request in calls if request.seat == seat]
            self.assertEqual(len(turns), 2)
            self.assertIn("Hey you! How was your day?", prompt_text(turns[0]))
            self.assertIn("Oh really? What's the story there?", prompt_text(turns[1]))
            for request in turns:
                self.assertNotIn("Anything else going on in town?", prompt_text(request))
                self.assertNotIn("Anything fun happening this weekend?", prompt_text(request))
                self.assertNotIn("Did you hear anything about a concert?", prompt_text(request))
                self.assertNotIn("Haha okay, well I'll let you go. Talk soon!", prompt_text(request))

    async def test_caller_direct_question_does_not_trigger_a_listener_mention(self):
        backend = ControlledBackend(self.config, self.run, silent=True)
        result = await self.execute(backend)
        calls = [request for request in backend.requests if request.scene == 5 and not judge_request(request)]
        self.assertEqual(len(calls), 48)
        self.assertFalse(any(judge_request(request) for request in backend.requests))
        for seat in range(1, 13):
            turns = [request for request in calls if request.seat == seat]
            self.assertEqual(len(turns), 4)
            self.assertIn("Did you hear anything about a concert?", prompt_text(turns[-1]))
            self.assertNotIn("Oh really? What's the story there?", prompt_text(turns[-1]))
        self.assertEqual(len(result["judge_evaluations"]), 12)
        self.assertTrue(all(row["label"] == "NOT_MENTIONED" for row in result["judge_evaluations"]))
        self.assertTrue(all(row["provenance"] == "runner_phone_funnel_rule" for row in result["judge_evaluations"]))
        self.assertEqual(result["scene_5_funnel_step_mentioned"], {str(seat): None for seat in range(1, 13)})

    async def test_late_listener_mention_records_the_actual_funnel_step(self):
        backend = ControlledBackend(self.config, self.run, mention_step=4)
        result = await self.execute(backend)
        self.assertEqual(result["scene_5_funnel_step_mentioned"], {str(seat): 4 for seat in range(1, 13)})
        self.assertEqual(result["scene_5_mention_step_confirmed"], {str(seat): 4 for seat in range(1, 13)})
        for phone in result["scene_5_phone_transcripts"]:
            lines = phone["lines"]
            self.assertEqual([line["funnel_step"] for line in lines if line["speaker"] == "listener"], [1, 2, 3, 4, 5])
            self.assertEqual(lines[-1]["speaker"], "caller")
            self.assertEqual(lines[-1]["funnel_step"], 6)

    async def test_step_four_echo_judged_not_mentioned_is_not_confirmed(self):
        class EchoBackend(ControlledBackend):
            async def generate(self, request):
                if not judge_request(request):
                    return await super().generate(request)
                self.requests.append(copy.deepcopy(request))
                response = GenerationResponse(text=json.dumps({"label": "NOT_MENTIONED", "quote": ""}))
                self.responses.append((copy.deepcopy(request), copy.deepcopy(response)))
                return response

        result = await self.execute(EchoBackend(self.config, self.run, mention_step=4))
        self.assertEqual(result["scene_5_funnel_step_mentioned"], {str(seat): 4 for seat in range(1, 13)})
        self.assertEqual(result["scene_5_mention_step_confirmed"], {str(seat): None for seat in range(1, 13)})

    async def test_fixture_modes_execute_without_any_network_connection(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network forbidden in offline test")):
            for index, mode in enumerate(("mixed", "all_skip", "silent")):
                with self.subTest(mode=mode):
                    manifest = copy.deepcopy(self.run)
                    manifest["run_id"] += f"-fixture-{index}"
                    result = await self.execute(FixtureBackend(mode=mode), run=manifest)
                    self.assertEqual(result["run_status"], "completed")
                    if mode == "mixed":
                        self.assertGreater(result["metrics"]["n_mentioned"], 0)
                        self.assertTrue(any(row["label"] in {"CHECKED_TRUE", "CHECKED_FALSE"}
                                            for row in result["judge_evaluations"]))
                    if mode == "all_skip":
                        self.assertEqual(result["metrics"]["go_count"], 0)
                        self.assertEqual(set(result["final_budgets_usd"].values()), {40})
                    if mode == "silent":
                        self.assertEqual(result["metrics"]["n_omitted"], 12)
                        self.assertEqual(result["metrics"]["omission_rate"], 1)
                        self.assertIsNone(result["metrics"]["belief_mean"])

    async def test_each_request_uses_its_configured_generation_settings(self):
        backend = ControlledBackend(self.config, self.run)
        await self.execute(backend)
        for request in backend.requests:
            key = ("blind_judge_turns" if judge_request(request) else
                   "verification_decision_turns" if request.scene in (2, 4) else
                   "conversational_turns")
            self.assertEqual(request.settings, self.config["hyperparameters"][key])
            if request.scene in (2, 4):
                self.assertEqual(request.settings["temperature"], 0.0)
            elif not judge_request(request):
                self.assertEqual(request.settings["temperature"], 0.7)

    async def test_raw_call_evidence_matches_requests_and_zero_provider_usage(self):
        backend = ControlledBackend(self.config, self.run)
        result = await self.execute(backend)
        self.assertEqual(len(result["calls"]), len(backend.responses))
        directory = self.output_root / self.run["run_id"]
        self.assertEqual(json.loads((directory / "town.json").read_text(encoding="utf-8")), result)
        self.assertEqual([json.loads(line) for line in (directory / "trace.jsonl").read_text(encoding="utf-8").splitlines()], result["calls"])
        self.assertEqual(result["evidence_kind"], "synthetic_fixture")
        self.assertIs(result["study_eligible"], False)
        self.assertEqual(result["token_usage"]["provider_api_calls"], 0)
        self.assertEqual(result["token_usage"]["fixture_callback_invocations"], len(backend.responses))
        self.assertIsNone(result["token_usage"]["cost_usd"])
        self.assertIsNone(result["token_usage"]["input_tokens"])
        self.assertIsNone(result["token_usage"]["output_tokens"])
        for event, (request, response) in zip(result["calls"], backend.responses):
            self.assertEqual(event["status"], "completed")
            self.assertEqual(event["response"], response.text)
            self.assertEqual(event["request"]["messages"], request.messages)
            self.assertEqual(event["request"]["settings"], request.settings)
            payload = json.dumps(event["request"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            self.assertEqual(event["request_sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(json.loads(event["raw_response"]["text"]), {"text": response.text, "usage": None})
            self.assertEqual(event["provider_api_calls"], 0)
            self.assertIsNone(event["actual_provider"])
            self.assertIsNone(event["actual_model"])
            self.assertIsNone(event["cost_usd"])
            self.assertIsNone(event["token_usage"])

    async def test_nonfixture_backend_is_rejected_before_callbacks_or_output(self):
        backend = ControlledBackend(self.config, self.run)
        backend.evidence_kind = "provider_response"
        with self.assertRaisesRegex(ValueError, "offline|synthetic"):
            await self.execute(backend)
        self.assertEqual(backend.requests, [])
        self.assertEqual(list(self.output_root.iterdir()), [])

    async def test_invalid_generation_and_timeout_do_not_become_skip(self):
        for index, fault in enumerate((GenerationResponse(text=None), GenerationResponse(text="GO", usage={"input_tokens": 1}), TimeoutError("test timeout"))):
            with self.subTest(fault=fault):
                backend = FaultBackend(self.config, self.run, scene=2, fault=fault)
                run = copy.deepcopy(self.run)
                run["run_id"] += f"-fault-{index}"
                result = await self.execute(backend, run=run)
                self.assertIn(result["run_status"], {"malformed_response", "timeout"})
                self.assertEqual(result["scene_statuses"]["2"], "failed")
                self.assertEqual(result["scene_statuses"]["3"], "not_executed")
                self.assertNotIn(1, {row["seat_id"] for row in result["scene_2_first_hand_decisions"]})
                self.assertEqual(result["final_budgets_usd"]["1"], 40)
                self.assertEqual(result["judge_evaluations"], [])
                self.assertIsNone(result["metrics"]["belief_mean"])
                self.assertIsNone(result["metrics"]["go_count"])

    async def test_configured_malformed_decision_fallback_is_explicitly_counted(self):
        for index, text in enumerate(("", "MAYBE", "   ")):
            with self.subTest(text=text):
                backend = FaultBackend(self.config, self.run, scene=2, fault=GenerationResponse(text=text))
                run = copy.deepcopy(self.run)
                run["run_id"] += f"-parse-{index}"
                result = await self.execute(backend, run=run)
                self.assertEqual(result["run_status"], "completed")
                row = next(row for row in result["scene_2_first_hand_decisions"] if row["seat_id"] == 1)
                self.assertEqual(row["parse_status"], "malformed_fallback_skip")
                self.assertEqual(row["raw_response"], text)
                self.assertEqual(row["balance_usd"], 40)
                self.assertIsNone(row["poster_observation"])
                self.assertEqual(row["decision"], "SKIP")
                self.assertEqual(result["metrics"]["decision_status"], "complete")
                self.assertEqual(result["metrics"]["n_valid_decisions"], 11)
                self.assertEqual(result["metrics"]["n_decision_fallbacks"], 1)
                self.assertEqual(result["metrics"]["n_operational_decisions"], 12)
                self.assertEqual(result["metrics"]["go_count"], 0)
                self.assertEqual(result["metrics"]["go_rate_first_hand"], 0)
                self.assertEqual(result["metrics"]["go_rate_second_hand"], 0)

    async def test_phone_timeout_is_missing_evidence_not_nonmention(self):
        backend = FaultBackend(self.config, self.run, scene=5, fault=TimeoutError("phone timeout"))
        result = await self.execute(backend)
        self.assertEqual(result["run_status"], "timeout")
        self.assertEqual(result["scene_statuses"]["5"], "failed")
        self.assertNotIn(1, {row["seat_id"] for row in result["judge_evaluations"]})
        self.assertNotIn("1", result["scene_5_funnel_step_mentioned"])
        self.assertIsNone(result["metrics"]["belief_mean"])
        self.assertIsNone(result["metrics"]["omission_rate"])

    async def test_malformed_judge_output_remains_invalid_evidence(self):
        backend = FaultBackend(self.config, self.run, scene=5,
                               fault=GenerationResponse(text="not a JSON judgment"), kind="judge")
        result = await self.execute(backend)
        row = next(row for row in result["judge_evaluations"] if row["seat_id"] == 1)
        self.assertEqual(row["status"], "malformed")
        self.assertIsNone(row["label"])
        self.assertEqual(result["metrics"]["n_invalid"], 1)
        self.assertEqual(result["metrics"]["n_omitted"], 0)
        self.assertIsNone(result["metrics"]["belief_mean"])

    async def test_failed_phase_settles_every_started_call_before_saving(self):
        from truth_discount.artifacts import save_town

        backend = BarrierFailureBackend(self.config, self.run)
        with patch("truth_discount.artifacts.save_town", wraps=save_town) as saved:
            task = asyncio.create_task(self.execute(backend))
            try:
                await asyncio.wait_for(backend.all_started.wait(), timeout=2)
                await asyncio.wait_for(backend.failure_raised.wait(), timeout=2)
                await asyncio.sleep(0)
                self.assertFalse(task.done())
                saved.assert_not_called()
                self.assertEqual(backend.started, set(range(1, 7)))
            finally:
                backend.release.set()
                try:
                    with self.assertRaisesRegex(RuntimeError, "controlled phase failure"):
                        await asyncio.wait_for(task, timeout=2)
                finally:
                    if not task.done():
                        task.cancel()
                        await asyncio.gather(task, return_exceptions=True)
            self.assertEqual(backend.settled, set(range(1, 7)))
            saved.assert_called_once()
            town = saved.call_args.args[1]
            phase_calls = [call for call in town["calls"] if call["scene"] == 2]
            self.assertEqual(len(phase_calls), 6)
            self.assertEqual(sum(call["status"] == "callback_error" for call in phase_calls), 1)
            self.assertEqual(sum(call["status"] == "completed" for call in phase_calls), 5)
            self.assertNotIn("started", {call["status"] for call in town["calls"]})
            self.assertEqual(town["run_status"], "runner_error")

    async def test_callback_cancellation_is_persisted_and_propagated(self):
        class CancelBackend(ControlledBackend):
            async def generate(self, request):
                if request.scene == 2 and request.seat == 1:
                    raise asyncio.CancelledError()
                return await super().generate(request)

        with self.assertRaises(asyncio.CancelledError):
            await self.execute(CancelBackend(self.config, self.run))
        path = self.output_root / self.run["run_id"] / "town.json"
        town = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(town["run_status"], "cancelled")
        self.assertEqual(town["scene_statuses"]["2"], "failed")
        self.assertEqual(town["scene_statuses"]["3"], "not_executed")
        cancelled = next(c for c in town["calls"] if c["scene"] == 2 and c["seat_id"] == 1)
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(cancelled["error"], "CancelledError")
        self.assertNotIn("started", {c["status"] for c in town["calls"]})
        self.assertNotIn(1, {d["seat_id"] for d in town["scene_2_first_hand_decisions"]})
        self.assertEqual(town["metrics"]["n_decision_fallbacks"], 0)
        self.assertIsNone(town["metrics"]["go_count"])

    async def test_external_cancellation_settles_active_calls_before_persisting(self):
        class WaitingBackend(ControlledBackend):
            def __init__(self, config, run):
                super().__init__(config, run)
                self.started = set()
                self.settled = set()
                self.all_started = asyncio.Event()
                self.never_release = asyncio.Event()

            async def generate(self, request):
                if request.scene != 2:
                    return await super().generate(request)
                self.started.add(request.seat)
                if len(self.started) == 6:
                    self.all_started.set()
                try:
                    await self.never_release.wait()
                finally:
                    self.settled.add(request.seat)

        backend = WaitingBackend(self.config, self.run)
        task = asyncio.create_task(self.execute(backend))
        try:
            await asyncio.wait_for(backend.all_started.wait(), timeout=2)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
        self.assertEqual(backend.settled, set(range(1, 7)))
        town = json.loads((self.output_root / self.run["run_id"] / "town.json").read_text(encoding="utf-8"))
        self.assertEqual(town["run_status"], "cancelled")
        self.assertEqual(town["scene_statuses"]["2"], "failed")
        active_calls = [c for c in town["calls"] if c["scene"] == 2]
        self.assertEqual(len(active_calls), 6)
        self.assertTrue(all(c["status"] == "cancelled" for c in active_calls))
        self.assertEqual(town["scene_2_first_hand_decisions"], [])

    async def test_partial_catchup_keeps_observed_lines_when_closing_times_out(self):
        class ClosingTimeoutBackend(ControlledBackend):
            async def generate(self, request):
                if request.scene == 3 and request.seat == 1 and request.turn == 4:
                    raise TimeoutError("controlled closing failure")
                return await super().generate(request)

        town = await self.execute(ClosingTimeoutBackend(self.config, self.run))
        self.assertEqual(town["run_status"], "timeout")
        self.assertEqual(town["scene_statuses"]["3"], "failed")
        self.assertEqual(town["scene_statuses"]["4"], "not_executed")
        pair = next(p for p in town["scene_3_catch_up_transcripts"] if p["first_hand_seat"] == 1)
        self.assertEqual([line["turn"] for line in pair["lines"]], [1, 2, 3])
        self.assertEqual([line["seat_id"] for line in pair["lines"]], [7, 1, 7])
        for line in pair["lines"][1:]:
            call = next(c for c in town["calls"] if c["scene"] == 3
                        and c["seat_id"] == line["seat_id"] and c["turn"] == line["turn"])
            self.assertEqual(call["status"], "completed")
            self.assertEqual(line["text"], call["response"])
        saved = json.loads((self.output_root / self.run["run_id"] / "town.json").read_text(encoding="utf-8"))
        saved_pair = next(p for p in saved["scene_3_catch_up_transcripts"] if p["first_hand_seat"] == 1)
        self.assertEqual(saved_pair, pair)
        self.assertNotIn(1, {p["first_hand_seat"] for p in saved["scene_3_poster_evidence_passed"]})


class FaultBackend(ControlledBackend):
    def __init__(self, config, run, *, scene, fault, kind=None):
        super().__init__(config, run)
        self.failure_scene = scene
        self.fault = fault
        self.failure_kind = kind

    async def generate(self, request):
        matches_kind = request.kind == self.failure_kind if self.failure_kind else not judge_request(request)
        if request.scene == self.failure_scene and request.seat == 1 and matches_kind:
            self.requests.append(copy.deepcopy(request))
            if isinstance(self.fault, Exception):
                raise self.fault
            return self.fault
        return await super().generate(request)


class BarrierFailureBackend(ControlledBackend):
    def __init__(self, config, run):
        super().__init__(config, run)
        self.started = set()
        self.settled = set()
        self.all_started = asyncio.Event()
        self.failure_raised = asyncio.Event()
        self.release = asyncio.Event()

    async def generate(self, request):
        if request.scene != 2:
            return await super().generate(request)
        self.started.add(request.seat)
        if len(self.started) == 6:
            self.all_started.set()
        try:
            await self.all_started.wait()
            if request.seat == 1:
                self.failure_raised.set()
                raise RuntimeError("controlled phase failure")
            await self.release.wait()
            return await super().generate(request)
        finally:
            self.settled.add(request.seat)


if __name__ == "__main__":
    unittest.main()
