"""Actor-only tests use deterministic fixtures; no network or credentials."""

import asyncio
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from truth_discount.artifacts import InvalidBundle, audit_town
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import GenerationResponse
from truth_discount.fixtures import FixtureBackend
from truth_discount.runner import run_town
from truth_discount.simulation_artifacts import audit_simulation, grading_items


class NoJudgeBackend(FixtureBackend):
    def __init__(self, mode="mixed"):
        super().__init__(mode)
        self.requests = []

    async def generate(self, request):
        self.requests.append(copy.deepcopy(request))
        if request.kind == "judge":
            raise AssertionError("generation must not call a judge")
        return await super().generate(request)


class SimulationRunnerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.run = build_manifest(self.config)[0]

    async def test_unchanged_actor_requests_and_dialogues_match_legacy_execution(self):
        keys = ["agent_histories", "final_budgets_usd", "scene_1_departure_broadcast_text",
                "scene_2_first_hand_decisions", "scene_3_catch_up_transcripts",
                "scene_3_poster_evidence_passed", "scene_4_second_hand_decisions",
                "scene_5_phone_transcripts", "scene_5_funnel_step_mentioned"]
        for mode in ("mixed", "all_skip", "silent"):
            with self.subTest(mode=mode):
                legacy = await run_town(self.config, self.run, FixtureBackend(mode), self.root / (mode + "-legacy"))
                backend = NoJudgeBackend(mode)
                deferred = await run_town(self.config, self.run, backend, self.root / mode, defer_judging=True)
                for key in keys:
                    self.assertEqual(deferred[key], legacy[key], key)
                def actors(town):
                    return sorted([(c["scene"], c["seat_id"], c["turn"], c["kind"], c["request"], c["response"])
                                   for c in town["calls"] if c["kind"] != "judge"])
                self.assertEqual(actors(deferred), actors(legacy))
                self.assertTrue(all(r.kind != "judge" for r in backend.requests))
                self.assertEqual(audit_simulation(self.root / mode / self.run["run_id"]), deferred)
                self.assertEqual(audit_town(self.root / (mode + "-legacy") / self.run["run_id"]), legacy)

    async def test_all_twelve_silent_phones_remain_pending_not_omissions(self):
        town = await run_town(self.config, self.run, NoJudgeBackend("silent"), self.root, defer_judging=True)
        self.assertEqual((town["run_status"], town["generation_status"], town["evaluation_status"]),
                         ("completed", "completed", "pending"))
        self.assertIsNone(town["metrics"])
        self.assertEqual(town["judge_inputs"], [])
        self.assertEqual(town["judge_evaluations"], [])
        self.assertEqual(town["scene_5_mention_step_confirmed"], {})
        items = grading_items(self.root / town["run_id"])
        self.assertEqual(len(items), 12)
        self.assertTrue(all(item["funnel_trigger_step"] is None for item in items))
        self.assertTrue(all(item["phone_transcript"][-1]["funnel_step"] == 6 for item in items))
        self.assertFalse(any("label" in item for item in items))
        self.assertEqual(town["token_usage"]["provider_api_calls"], 0)

    async def test_retry_same_allocation_gets_a_new_generation_attempt_and_item_identity(self):
        one = await run_town(self.config, self.run, NoJudgeBackend(), self.root / "one", defer_judging=True)
        two = await run_town(self.config, self.run, NoJudgeBackend(), self.root / "two", defer_judging=True)
        self.assertEqual(one["run_id"], two["run_id"])
        self.assertEqual(one["scene_5_phone_transcripts"], two["scene_5_phone_transcripts"])
        self.assertNotEqual(one["generation_attempt_id"], two["generation_attempt_id"])
        first = grading_items(self.root / "one" / one["run_id"])
        second = grading_items(self.root / "two" / two["run_id"])
        self.assertFalse({x["item_id"] for x in first} & {x["item_id"] for x in second})

    async def test_late_direct_question_keeps_the_same_follow_up_branch(self):
        class Late(FixtureBackend):
            async def generate(self, request):
                if request.kind == "chat" and request.scene == 5:
                    return GenerationResponse("A concert might happen." if request.turn >= 4 else
                                              "Work kept me busy this week.")
                return await super().generate(request)

        old = await run_town(self.config, self.run, Late(), self.root / "old")
        new = await run_town(self.config, self.run, Late(), self.root / "new", defer_judging=True)
        self.assertEqual(new["scene_5_phone_transcripts"], old["scene_5_phone_transcripts"])
        self.assertEqual(new["agent_histories"], old["agent_histories"])
        self.assertEqual(set(new["scene_5_funnel_step_mentioned"].values()), {4})
        self.assertTrue(all(x["funnel_trigger_step"] == 4 for x in
                            grading_items(self.root / "new" / self.run["run_id"])))

    async def test_phone_failure_preserves_partial_actor_output_without_labels(self):
        class Timeout(NoJudgeBackend):
            async def generate(self, request):
                if request.scene == 5 and request.seat == 1:
                    raise TimeoutError("synthetic phone failure")
                return await super().generate(request)

        town = await run_town(self.config, self.run, Timeout(), self.root, defer_judging=True)
        self.assertEqual((town["generation_status"], town["evaluation_status"]), ("failed", "pending"))
        self.assertEqual(town["run_status"], "timeout")
        self.assertIsNone(town["metrics"])
        directory = self.root / town["run_id"]
        self.assertEqual(audit_simulation(directory), town)
        with self.assertRaisesRegex(InvalidBundle, "incomplete generation"):
            grading_items(directory)

    async def test_cancelled_actor_phase_is_sealed_and_auditable(self):
        class Cancel(NoJudgeBackend):
            async def generate(self, request):
                if request.scene == 2 and request.seat == 1:
                    raise asyncio.CancelledError()
                return await super().generate(request)

        with self.assertRaises(asyncio.CancelledError):
            await run_town(self.config, self.run, Cancel(), self.root, defer_judging=True)
        town = audit_simulation(self.root / self.run["run_id"])
        self.assertEqual(town["generation_status"], "failed")
        self.assertEqual(town["run_status"], "cancelled")
        self.assertEqual(town["scene_5_phone_transcripts"], [])

    async def test_malformed_actor_answer_is_preserved_as_failure(self):
        class EmptyChat(NoJudgeBackend):
            async def generate(self, request):
                if request.scene == 3 and request.turn == 4 and request.seat == 1:
                    return GenerationResponse("")
                return await super().generate(request)

        town = await run_town(self.config, self.run, EmptyChat(), self.root, defer_judging=True)
        self.assertEqual(audit_simulation(self.root / town["run_id"]), town)
        self.assertEqual(town["run_status"], "malformed_response")
        self.assertIsNone(town["metrics"])

    async def test_defer_flag_is_explicit_and_cannot_be_a_truthy_string(self):
        with self.assertRaisesRegex(ValueError, "boolean"):
            await run_town(self.config, self.run, NoJudgeBackend(), self.root, defer_judging="false")
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
