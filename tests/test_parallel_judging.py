"""Bounded overlapping judge requests with fake HTTP and temporary ledgers only."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_deferred_judging import HTTP, KEY, inventory, profile
from truth_discount.budget import BudgetLedger
from truth_discount.config import build_manifest, load_config
from truth_discount.deferred_judging import judge_collection, plan_judging, replay_judging
from truth_discount.fixtures import FixtureBackend
from truth_discount.providers import ProviderBackend
from truth_discount.runner import run_town


class OverlappingHTTP(HTTP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active = self.peak = self.started = 0

    async def __call__(self, *args):
        self.started += 1
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(.03)
            return super().__call__(*args)
        finally:
            self.active -= 1


class FailFirstWave(HTTP):
    """The first request fails only after the entire initial wave has started."""
    def __init__(self, wave):
        super().__init__()
        self.wave, self.started, self.completed = wave, 0, 0
        self.ready = asyncio.Event()

    async def __call__(self, *args):
        self.started += 1
        ordinal = self.started
        if ordinal == self.wave:
            self.ready.set()
        await self.ready.wait()
        if ordinal == 1:
            raise TimeoutError("synthetic unknown-charge failure")
        # Already-started siblings return and are durably recorded after the
        # first failure. They must not be cancelled or followed by new items.
        await asyncio.sleep(.06)
        result = super().__call__(*args)
        self.completed += 1
        return result


class ParallelJudgingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / "source", self.root / "grading"
        self.config = load_config(Path(__file__).resolve().parents[1] / "configs/pilot_config.json")
        await run_town(self.config, build_manifest(self.config)[0], FixtureBackend(), self.source, defer_judging=True)
        self.before = inventory(self.source)
        self.profile = profile(self.config, population="all_phones")
        env = patch.dict(os.environ, {"DEFERRED_TEST_KEY": KEY})
        env.start()
        self.addCleanup(env.stop)
        self.last_budget = None

    async def collect(self, http, *, maximum=3, resume=False, retry_invalid=False, ledger_path=None):
        with BudgetLedger(ledger_path or self.root / "parallel-budget.jsonl", "1") as ledger:
            backend = ProviderBackend(self.profile["provider_manifest"], ledger, transport=http,
                                      evidence_kind="mocked_provider")
            try:
                return await judge_collection(self.source, self.output, self.profile, backend,
                    execution_authorized=True, spending_authorized=True,
                    max_concurrent_judgments=maximum, resume=resume, retry_invalid=retry_invalid)
            finally:
                self.last_budget = ledger.summary()
                self.last_checkpoint = ledger.checkpoint()

    async def test_requests_really_overlap_with_a_fixed_bound_and_complete_receipts(self):
        http = OverlappingHTTP()
        result = await self.collect(http, maximum=3)
        self.assertGreaterEqual(http.peak, 2)
        self.assertLessEqual(http.peak, 3)
        self.assertEqual((http.started, result["attempts"], result["valid_first_attempt"]), (12, 12, 12))
        self.assertEqual(result["provider_api_calls"], 0)
        self.assertEqual(result["simulated_provider_requests"], 12)
        self.assertFalse(self.last_budget["blocked"])
        directory = self.output / self.profile["profile_id"]
        saved = json.loads((directory / "judging_plan.json").read_text())
        self.assertEqual(saved["execution_controls"]["max_concurrent_judgments"], 3)
        events = [json.loads(line) for line in (directory / "attempts.jsonl").read_text().splitlines()]
        self.assertEqual([e["seq"] for e in events], list(range(len(events))))
        self.assertEqual(sum(e["event"]["type"] == "start" for e in events), 12)
        self.assertEqual(sum(e["event"]["type"] == "finish" for e in events), 12)
        checkpoint = json.loads((directory / "budget_checkpoint.json").read_text())
        self.assertEqual(checkpoint["ledger_checkpoint"], self.last_checkpoint)
        self.assertEqual(inventory(self.source), self.before)

    async def test_native_route_cap_is_respected_even_when_requested_limit_is_larger(self):
        route = self.profile["provider_manifest"]["routes"][self.profile["model_key"]]
        route["max_concurrent_requests"] = 2
        planned = plan_judging(self.source, self.profile, max_concurrent_judgments=8)
        self.assertEqual(planned["execution_controls"]["effective_max_concurrent_judgments"], 2)
        http = OverlappingHTTP()
        await self.collect(http, maximum=8)
        self.assertEqual(http.peak, 2)

    async def test_failure_stops_new_items_but_drains_started_receipts_and_keeps_unknown_hold(self):
        http = FailFirstWave(3)
        with self.assertRaisesRegex(ValueError, "provider failure"):
            await asyncio.wait_for(self.collect(http, maximum=3), 5)
        self.assertEqual((http.started, http.completed), (3, 2))
        self.assertTrue(self.last_budget["blocked"])
        self.assertEqual(self.last_budget["unknown_count"], 1)
        report = replay_judging(self.source, self.output, self.profile)
        self.assertEqual((report["attempts"], report["unobserved_first_attempt"],
                          report["valid_first_attempt"], report["not_observed"]), (3, 1, 2, 9))
        self.assertIsNone(report["cost_usd"])
        again = OverlappingHTTP()
        with self.assertRaisesRegex(ValueError, "unresolved charges"):
            await self.collect(again, maximum=3, resume=True)
        self.assertEqual(again.started, 0)
        self.assertEqual(inventory(self.source), self.before)

    async def test_cancellation_keeps_every_started_attempt_receipt_before_releasing_anchor(self):
        class WaitingHTTP(HTTP):
            def __init__(self):
                super().__init__()
                self.started = 0
                self.ready = asyncio.Event()
            async def __call__(self, *args):
                self.started += 1
                if self.started == 3:
                    self.ready.set()
                await asyncio.sleep(10)
                return super().__call__(*args)
        http = WaitingHTTP()
        task = asyncio.create_task(self.collect(http, maximum=3))
        await asyncio.wait_for(http.ready.wait(), 3)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(http.started, 3)
        self.assertEqual(self.last_budget["unknown_count"], 3)
        report = replay_judging(self.source, self.output, self.profile)
        self.assertEqual((report["attempts"], report["unobserved_first_attempt"], report["not_observed"]), (3, 3, 9))
        directory = self.output / self.profile["profile_id"]
        anchor = json.loads((directory / "budget_checkpoint.json").read_text())
        self.assertEqual(anchor["ledger_checkpoint"], self.last_checkpoint)

    async def test_resume_same_parallel_plan_needs_no_keys_or_extra_requests(self):
        await self.collect(OverlappingHTTP(), maximum=4)
        initial = inventory(self.output)
        again = OverlappingHTTP()
        with patch.dict(os.environ, {}, clear=True):
            result = await self.collect(again, maximum=4, resume=True)
            readonly = replay_judging(self.source, self.output, self.profile)
        self.assertEqual(again.started, 0)
        self.assertEqual(result["items"], readonly["items"])
        self.assertEqual(initial, inventory(self.output))

    async def test_changing_parallel_controls_or_ledger_cannot_replan_saved_work(self):
        await self.collect(OverlappingHTTP(), maximum=3)
        original = inventory(self.output)
        for maximum in [1, 2, 4]:
            with self.subTest(maximum=maximum), self.assertRaises(ValueError):
                await self.collect(OverlappingHTTP(), maximum=maximum, resume=True)
        with self.assertRaisesRegex(ValueError, "original ledger"):
            await self.collect(OverlappingHTTP(), maximum=3, resume=True,
                               ledger_path=self.root / "new-budget.jsonl")
        self.assertEqual(original, inventory(self.output))

    async def test_serial_default_preserves_existing_plan_layout_and_bad_limits_do_not_write(self):
        self.assertNotIn("execution_controls", plan_judging(self.source, self.profile))
        self.assertEqual(plan_judging(self.source, self.profile, max_concurrent_judgments=32)
                         ["execution_controls"]["max_concurrent_judgments"], 32)
        for maximum in [0, 33, True, 1.5, "3"]:
            with self.subTest(maximum=maximum), self.assertRaises(ValueError):
                plan_judging(self.source, self.profile, max_concurrent_judgments=maximum)
        for maximum in [0, 33, True]:
            with self.subTest(maximum=maximum), self.assertRaises(ValueError):
                await judge_collection(self.source, self.output, self.profile, None,
                    max_concurrent_judgments=maximum, execution_authorized=True, spending_authorized=True)
        self.assertFalse(self.output.exists())
        http = OverlappingHTTP()
        result = await self.collect(http, maximum=1)
        self.assertEqual(http.peak, 1)
        self.assertEqual(result["valid_first_attempt"], 12)

    async def test_parallel_explicit_repair_preserves_first_attempt_and_all_costs(self):
        first = await self.collect(OverlappingHTTP(malformed=True), maximum=3)
        self.assertEqual(first["malformed_first_attempt"], 12)
        repaired = await self.collect(OverlappingHTTP(), maximum=3, resume=True, retry_invalid=True)
        self.assertEqual(repaired["malformed_first_attempt"], 12)
        self.assertEqual(repaired["attempts"], 24)
        self.assertTrue(all(r["attempt_count"] == 2 and r["latest_evaluation"]["status"] == "valid"
                            for r in repaired["items"]))
        self.assertGreater(repaired["cost_usd"], first["cost_usd"])

    async def test_callbacks_from_transport_threads_do_not_deadlock_or_rewind_anchor(self):
        with BudgetLedger(self.root / "thread-budget.jsonl", "1") as ledger:
            class ThreadedHTTP(HTTP):
                def __call__(self, *args):
                    reservation = ledger.reserve(0, {"model_key": "synthetic-thread-callback"})
                    ledger.settle(reservation, 0)
                    return super().__call__(*args)
            http = ThreadedHTTP()
            backend = ProviderBackend(self.profile["provider_manifest"], ledger, transport=http,
                                      evidence_kind="mocked_provider")
            result = await asyncio.wait_for(judge_collection(self.source, self.output, self.profile, backend,
                execution_authorized=True, spending_authorized=True, max_concurrent_judgments=4), 5)
            checkpoint = json.loads((self.output / self.profile["profile_id"] / "budget_checkpoint.json").read_text())
            self.assertEqual(checkpoint["ledger_checkpoint"], ledger.checkpoint())
            self.assertEqual(ledger.summary()["reservation_count"], 24)
            self.assertFalse(ledger.summary()["blocked"])
        self.assertEqual(result["attempts"], 12)
        self.assertEqual(replay_judging(self.source, self.output, self.profile)["valid_first_attempt"], 12)


if __name__ == "__main__":
    unittest.main()
