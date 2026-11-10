"""Deferred judging uses synthetic actors and injected provider HTTP only."""
from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.budget import BudgetLedger
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import canonical_bytes, digest
from truth_discount.deferred_judging import (PARSER_VERSION, compare_judgments, judge_collection,
    load_judge_profile, make_judge_selection, parser_sha256, plan_judging, replay_judging)
from truth_discount.fixtures import FixtureBackend
from truth_discount.providers import ProviderBackend
from truth_discount.runner import run_town

ROOT = Path(__file__).resolve().parents[1]
KEY = "sk-FAKE-DEFERRED-UNIT-TEST-ONLY"


def profile(config, provider="Anthropic", *, name="judge-a", population="historical_funnel"):
    endpoints = {"Anthropic": "https://api.anthropic.com/v1/messages",
                 "OpenAI": "https://api.openai.com/v1/chat/completions",
                 "DeepInfra": "https://api.deepinfra.com/v1/openai/chat/completions"}
    rubric = config["judging_and_scoring"]["canonical_judge_prompt"]
    settings = copy.deepcopy(config["hyperparameters"]["blind_judge_turns"])
    settings["use_batch_api"] = False
    return {"version": 1, "profile_id": name, "approved": True, "model_key": "external_judge",
            "provider_manifest": {"version": 1, "approved": True, "routes": {"external_judge": {
                "provider": provider, "model_id": "test-external-judge-v1", "endpoint": endpoints[provider],
                "api_key_env": "DEFERRED_TEST_KEY", "settings_verified": True, "pricing_verified": True,
                "input_usd_per_million": .1, "output_usd_per_million": .5, "cached_input_usd_per_million": .01,
                "max_input_tokens": 8192, "timeout_seconds": 1,
                "thinking_disabled_parameters": {"thinking": {"type": "disabled"}} if provider == "Anthropic" else {"reasoning_effort": "none"}}}},
            "settings": settings, "rubric": {"version": "original-v1", "prompt": rubric,
                "sha256": hashlib.sha256(rubric.encode()).hexdigest()},
            "parser": {"version": PARSER_VERSION, "sha256": parser_sha256()},
            "population": population, "population_approved": True, "source_format": "simulation"}


class HTTP:
    def __init__(self, *, malformed=False, timeout=False, force=None, stop=None):
        self.requests = []
        self.malformed, self.timeout, self.force = malformed, timeout, force
        self.stop = stop

    def __call__(self, method, url, headers, body, timeout_seconds):
        self.requests.append(copy.deepcopy(body))
        if self.timeout:
            raise TimeoutError("fake timeout")
        text = (self.force if self.force is not None else "not JSON" if self.malformed else
                FixtureBackend._judge(body["messages"][-1]["content"]))
        if "anthropic" in url:
            return {"id": "msg_fake_unit", "model": body["model"], "content": [{"type": "text", "text": text}],
                    "stop_reason": self.stop,
                    "usage": {"input_tokens": 1100, "output_tokens": 60, "cache_read_input_tokens": 0}}
        return {"id": "req_fake_unit", "model": body["model"], "choices": [{"message": {"content": text}, "finish_reason": self.stop}],
                "usage": {"prompt_tokens": 1100, "completion_tokens": 60}}


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class DeferredJudgingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / "source", self.root / "grading"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.run = build_manifest(self.config)[0]
        self.town = await run_town(self.config, self.run, FixtureBackend(), self.source, defer_judging=True)
        self.profile = profile(self.config)
        self.before = inventory(self.source)
        self.env = patch.dict(os.environ, {"DEFERRED_TEST_KEY": KEY})
        self.env.start()
        self.addCleanup(self.env.stop)

    async def collect(self, http=None, *, current=None, resume=False, retry_invalid=False,
                      retry_failed=False, ledger_path=None, budget="1", sources=None):
        current = current or self.profile
        http = http or HTTP()
        with BudgetLedger(ledger_path or self.root / "judging-ledger.jsonl", budget) as ledger:
            backend = ProviderBackend(current["provider_manifest"], ledger, transport=http,
                                      evidence_kind="mocked_provider")
            try:
                return await judge_collection(sources or self.source, self.output, current, backend,
                    resume=resume, retry_invalid=retry_invalid, retry_failed=retry_failed,
                    execution_authorized=True, spending_authorized=True)
            finally:
                self.last_budget = ledger.summary()

    def test_planning_and_profile_loading_are_keyless_and_zero_mutation(self):
        p = self.root / "profile.json"
        p.write_bytes(canonical_bytes(self.profile))
        with patch.dict(os.environ, {}, clear=True), patch("socket.create_connection", side_effect=AssertionError("network")):
            loaded = load_judge_profile(p)
            planned = plan_judging(self.source, loaded)
        self.assertEqual(planned["phone_outcomes"], 12)
        self.assertEqual(planned["planned_model_judgments"] + planned["planned_rule_labels"], 12)
        self.assertEqual(planned["provider_api_calls"], 0)
        self.assertFalse(planned["api_access_validated"])
        self.assertFalse(self.output.exists())
        self.assertEqual(self.before, inventory(self.source))

    def test_unapproved_profile_population_and_changed_hash_are_not_silent_defaults(self):
        p = copy.deepcopy(self.profile)
        p.pop("population");p.pop("population_approved")
        self.assertIn("population", " ".join(plan_judging(self.source, p)["execution_gates"]))
        for key in ["rubric", "parser"]:
            bad = copy.deepcopy(self.profile);bad[key]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "hash"):
                plan_judging(self.source, bad)
        bad = copy.deepcopy(self.profile);bad["provider_manifest"]["routes"]["external_judge"]["endpoint"] = "https://evil.invalid/"
        with self.assertRaises(ValueError):
            plan_judging(self.source, bad)

    async def test_execution_cannot_release_hold_by_approved_profile_alone(self):
        for flags in [{}, {"execution_authorized": True}, {"spending_authorized": True}]:
            with self.assertRaisesRegex(ValueError, "spending"):
                await judge_collection(self.source, self.output, self.profile, None, **flags)
        self.assertFalse(self.output.exists())

    async def test_mocked_anthropic_roundtrip_never_mutates_or_regenerates_actors(self):
        http = HTTP()
        result = await self.collect(http)
        self.assertEqual(result["phone_outcomes"], 12)
        self.assertEqual(result["valid_first_attempt"], 12)
        self.assertEqual(result["provider_api_calls"], 0)
        self.assertGreater(result["simulated_provider_requests"], 0)
        self.assertEqual(len(http.requests), plan_judging(self.source, self.profile)["planned_model_judgments"])
        self.assertEqual(self.before, inventory(self.source))
        replay = replay_judging(self.source, self.output, self.profile)
        self.assertEqual(replay["items"], result["items"])
        self.assertFalse(replay["study_eligible"])
        for request in http.requests:
            self.assertEqual(set(request["messages"][0]), {"role", "content"})
            text = request["messages"][0]["content"]
            for forbidden in [self.run["run_id"], "condition_type", "seat_id_private", "model_key", "generation_attempt_id"]:
                self.assertNotIn(forbidden, text)
        self.assertNotIn(KEY, "".join(p.read_text() for p in self.output.rglob("*") if p.is_file()))
        events = [json.loads(line)["event"] for line in
                  (self.output / self.profile["profile_id"] / "attempts.jsonl").read_text().splitlines()]
        finals = [e for e in events if e["type"] == "finish"]
        self.assertTrue(all(e["call"]["native_response"]["usage"]["output_tokens"] == 60 for e in finals))

    async def test_existing_three_provider_adapters_get_real_shaped_receipts(self):
        for name in ["OpenAI", "DeepInfra"]:
            p = profile(self.config, name, name=name)
            result = await self.collect(current=p)
            self.assertEqual(result["valid_first_attempt"], 12)
            self.assertEqual(result["provider_api_calls"], 0)
            self.assertEqual(replay_judging(self.source, self.output, p)["attempts"], result["attempts"])

    async def test_adaptive_native_judge_roundtrip_preserves_thinking_and_structured_format(self):
        class AdaptiveHTTP(HTTP):
            def __call__(self, *args):
                response = super().__call__(*args)
                response["content"].insert(0, {"type": "thinking", "thinking": "Synthetic test reasoning.",
                                              "signature": "fake-unit-signature"})
                response["usage"]["output_tokens_details"] = {"thinking_tokens": 8}
                return response
        p = copy.deepcopy(self.profile)
        p["settings"]["thinking"] = {"type": "adaptive"}
        p["settings"]["effort"] = "low"
        http = AdaptiveHTTP(stop="end_turn")
        result = await self.collect(http, current=p)
        self.assertEqual(result["valid_first_attempt"], 12)
        self.assertTrue(all(r["output_config"]["effort"] == "low" and
                            r["output_config"]["format"]["type"] == "json_schema" for r in http.requests))
        journal = self.output / p["profile_id"] / "attempts.jsonl"
        finals = [json.loads(line)["event"] for line in journal.read_text().splitlines()
                  if json.loads(line)["event"]["type"] == "finish"]
        self.assertTrue(all(e["call"]["native_response"]["content"][0]["type"] == "thinking" for e in finals))
        self.assertEqual(replay_judging(self.source, self.output, p)["items"], result["items"])

    async def test_all_phones_is_explicit_and_can_judge_original_regex_negatives(self):
        silent = self.root / "silent"
        await run_town(self.config, self.run, FixtureBackend("silent"), silent, defer_judging=True)
        historical = plan_judging(silent, self.profile)
        self.assertEqual(historical["planned_rule_labels"], 12)
        p = profile(self.config, name="all", population="all_phones")
        result = await self.collect(current=p, sources=silent)
        self.assertEqual(result["attempts"], 12)
        self.assertEqual(result["valid_first_attempt"], 12)

    async def test_historical_silent_town_requires_no_judge_key_and_has_undefined_conditional_belief(self):
        silent = self.root / "silent"
        await run_town(self.config, self.run, FixtureBackend("silent"), silent, defer_judging=True)
        http = HTTP()
        with patch.dict(os.environ, {}, clear=True):
            result = await self.collect(http, sources=silent)
        self.assertEqual(http.requests, [])
        self.assertEqual(result["attempts"], 0)
        self.assertTrue(all(r["historical_rule_applied"] for r in result["items"]))
        metrics = result["descriptive_first_attempt"]["towns"][0]["metrics"]
        self.assertEqual(metrics["status"], "complete")
        self.assertIsNone(metrics["belief_mean"])
        self.assertEqual(metrics["omission_rate"], 1)

    async def test_resume_skips_valid_results_without_credentials_or_new_calls(self):
        await self.collect()
        http = HTTP()
        with patch.dict(os.environ, {}, clear=True):
            result = await self.collect(http, resume=True)
        self.assertEqual(http.requests, [])
        self.assertEqual(result["valid_first_attempt"], 12)
        self.assertEqual(self.before, inventory(self.source))

    async def test_fresh_same_cap_ledger_cannot_reset_existing_collection(self):
        await self.collect()
        http = HTTP()
        with self.assertRaisesRegex(ValueError, "original ledger"):
            await self.collect(http, resume=True, ledger_path=self.root / "fresh.jsonl")
        self.assertEqual(http.requests, [])

    async def test_rewound_original_ledger_is_detected_before_any_request(self):
        await self.collect()
        path = self.root / "judging-ledger.jsonl"
        lines = path.read_bytes().splitlines(keepends=True)
        path.write_bytes(b"".join(lines[:1]))
        http = HTTP()
        with self.assertRaisesRegex(ValueError, "shorter"):
            await self.collect(http, resume=True)
        self.assertEqual(http.requests, [])

    async def test_timeout_preserves_terminal_unknown_receipt_and_blocks_resume(self):
        http = HTTP(timeout=True)
        with self.assertRaisesRegex(ValueError, "provider failure"):
            await self.collect(http)
        self.assertEqual(len(http.requests), 1)
        self.assertTrue(self.last_budget["blocked"])
        replay = replay_judging(self.source, self.output, self.profile)
        self.assertEqual(replay["unobserved_first_attempt"], 1)
        self.assertGreater(replay["not_observed"], 0)
        self.assertIsNone(replay["cost_usd"])
        again = HTTP()
        with self.assertRaisesRegex(ValueError, "unresolved charges"):
            await self.collect(again, resume=True, retry_failed=True)
        self.assertEqual(again.requests, [])
        self.assertEqual(self.before, inventory(self.source))

    async def test_invalid_retry_is_explicit_keeps_first_and_preserves_every_receipt(self):
        initial = await self.collect(HTTP(malformed=True))
        self.assertGreater(initial["malformed_first_attempt"], 0)
        skipped = HTTP()
        await self.collect(skipped, resume=True)
        self.assertEqual(skipped.requests, [])
        fixed = await self.collect(resume=True, retry_invalid=True)
        self.assertEqual(fixed["malformed_first_attempt"], initial["malformed_first_attempt"])
        self.assertTrue(all(r["latest_evaluation"]["status"] == "valid" for r in fixed["items"]))
        self.assertEqual(fixed["attempts"], 2 * initial["attempts"])
        self.assertIn("first_attempt_only", fixed["selection_policy"])
        self.assertEqual(fixed["descriptive_first_attempt"]["complete_towns"], 0)
        self.assertEqual(fixed["descriptive_latest_attempt"]["complete_towns"], 1)

    async def test_changed_profile_same_id_is_refused(self):
        await self.collect()
        changed = copy.deepcopy(self.profile);changed["settings"]["max_tokens"] += 1
        http = HTTP()
        with self.assertRaisesRegex(ValueError, "differs"):
            await self.collect(http, current=changed, resume=True)
        self.assertEqual(http.requests, [])

    async def test_changed_judging_implementation_is_not_silently_resumed(self):
        await self.collect()
        from truth_discount import deferred_judging
        actual = deferred_judging.plan_judging
        def changed(*args, **kwargs):
            value = actual(*args, **kwargs)
            value["judging_implementation"]["source_files_sha256"]["providers.py"] = "0" * 64
            return value
        http = HTTP()
        with patch("truth_discount.deferred_judging.plan_judging", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "judging_implementation"):
                await self.collect(http, resume=True)
        self.assertEqual(http.requests, [])

    async def test_changed_source_and_extra_or_torn_rows_fail_replay(self):
        await self.collect()
        journal = self.output / self.profile["profile_id"] / "attempts.jsonl"
        raw = journal.read_bytes()
        journal.write_bytes(raw + b'{"unfinished":')
        with self.assertRaisesRegex(ValueError, "interrupted"):
            replay_judging(self.source, self.output, self.profile)
        journal.write_bytes(raw + raw.splitlines(keepends=True)[-1])
        with self.assertRaises(ValueError):
            replay_judging(self.source, self.output, self.profile)
        journal.write_bytes(raw)
        phone = self.source / self.run["run_id"] / "phone_transcripts.json"
        phone.write_bytes(phone.read_bytes() + b" ")
        with self.assertRaises(ValueError):
            replay_judging(self.source, self.output, self.profile)

    async def test_duplicate_identical_shards_and_config_mismatch_are_refused(self):
        duplicate = self.root / "duplicate"
        shutil.copytree(self.source, duplicate)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            plan_judging([self.source, duplicate], self.profile)
        with self.assertRaisesRegex(ValueError, "duplicate source root"):
            plan_judging([self.source, self.source], self.profile)
        altered = copy.deepcopy(self.config)
        altered["hyperparameters"]["conversational_turns"]["max_tokens"] = 121
        second = self.root / "different-config"
        await run_town(altered, build_manifest(altered)[1], FixtureBackend(), second, defer_judging=True)
        with self.assertRaisesRegex(ValueError, "configuration"):
            plan_judging([self.source, second], self.profile)

    def rewrite_journal(self, mutate):
        base = self.output / self.profile["profile_id"]
        rows = [json.loads(line) for line in (base / "attempts.jsonl").read_text().splitlines()]
        events = [row["event"] for row in rows]
        mutate(events)
        rebuilt = []
        for number, event in enumerate(events):
            row = {"seq": number, "prev_sha256": rebuilt[-1]["sha256"] if rebuilt else None,
                   "event": event}
            row["sha256"] = digest(row)
            rebuilt.append(row)
        (base / "attempts.jsonl").write_bytes(b"".join(canonical_bytes(r) + b"\n" for r in rebuilt))
        anchor = json.loads((base / "budget_checkpoint.json").read_text())
        anchor["journal_checkpoint"] = {"event_count": len(rebuilt), "last_sha256": rebuilt[-1]["sha256"]}
        (base / "budget_checkpoint.json").write_bytes(canonical_bytes(anchor))

    async def test_interrupted_started_attempt_is_not_automatically_reissued_even_if_ledger_settled(self):
        await self.collect()
        self.rewrite_journal(lambda events: events.pop(next(i for i, e in enumerate(events) if e["type"] == "finish")))
        http = HTTP()
        with self.assertRaisesRegex(ValueError, "interrupted judging attempt"):
            await self.collect(http, resume=True, retry_failed=True)
        self.assertEqual(http.requests, [])

    async def test_resealed_label_and_duplicate_terminal_row_are_semantically_rejected(self):
        await self.collect()
        def alter(events):
            e = next(x for x in events if x["type"] == "finish")
            e["evaluation"]["label"] = "FACT" if e["evaluation"]["label"] != "FACT" else "UNCERTAIN"
        self.rewrite_journal(alter)
        with self.assertRaisesRegex(ValueError, "cannot be replayed"):
            replay_judging(self.source, self.output, self.profile)

    @staticmethod
    def reseal_raw(call):
        raw = json.loads(call["raw_response"]["text"])
        raw["usage"] = copy.deepcopy(call["token_usage"])
        raw["native_response"] = copy.deepcopy(call["native_response"])
        text = json.dumps(raw)
        call["raw_response"] = {"text": text, "truncated": False, "sha256": hashlib.sha256(text.encode()).hexdigest()}

    async def test_resealed_native_text_contradiction_cannot_survive_replay(self):
        await self.collect()
        def alter(events):
            call = next(e["call"] for e in events if e["type"] == "finish")
            call["native_response"]["content"][0]["text"] = "CONTRADICTORY NATIVE TEXT"
            self.reseal_raw(call)
        self.rewrite_journal(alter)
        with self.assertRaisesRegex(ValueError, "native judge text differs"):
            replay_judging(self.source, self.output, self.profile)

    async def test_resealed_native_usage_contradiction_cannot_survive_replay(self):
        await self.collect()
        def alter(events):
            call = next(e["call"] for e in events if e["type"] == "finish")
            call["native_response"]["usage"]["input_tokens"] += 1
            self.reseal_raw(call)
        self.rewrite_journal(alter)
        with self.assertRaisesRegex(ValueError, "native judge usage or identity"):
            replay_judging(self.source, self.output, self.profile)

    async def test_consistently_resealed_priced_overcap_response_is_rejected(self):
        await self.collect()
        def alter(events):
            call = next(e["call"] for e in events if e["type"] == "finish")
            call["token_usage"]["output_tokens"] = 251
            call["token_usage"]["cost_usd"] = (1100 * .1 + 251 * .5) / 1000000
            call["cost_usd"] = call["token_usage"]["cost_usd"]
            call["native_response"]["usage"]["output_tokens"] = 251
            self.reseal_raw(call)
        self.rewrite_journal(alter)
        with self.assertRaisesRegex(ValueError, "token bounds"):
            replay_judging(self.source, self.output, self.profile)

    async def test_known_truncation_and_refusal_are_not_valid_labels_even_with_parseable_json(self):
        result = await self.collect(HTTP(stop="max_tokens"))
        self.assertGreater(result["malformed_first_attempt"], 0)
        self.assertGreater(result["native_stop_reasons"]["max_tokens"], 0)
        self.assertTrue(all(r["first_evaluation"]["error"] == "native_output_limit"
                            for r in result["items"] if not r["historical_rule_applied"]))
        p = profile(self.config, name="refused")
        refused = await self.collect(HTTP(stop="refusal"), current=p)
        self.assertGreater(refused["unobserved_first_attempt"], 0)
        self.assertEqual(refused["not_observed"], 0)

    async def test_lost_journal_checkpoint_blocks_replay_without_repairing_it(self):
        await self.collect()
        checkpoint = self.output / self.profile["profile_id"] / "budget_checkpoint.json"
        checkpoint.unlink()
        with self.assertRaises(OSError):
            replay_judging(self.source, self.output, self.profile)
        self.assertFalse(checkpoint.exists())

    async def test_checkpoint_storage_failure_cannot_submit_an_unanchored_request(self):
        from truth_discount.execution import _atomic_json
        http = HTTP()
        def fail_reservation(path, value):
            if path.name == "budget_checkpoint.json" and value["ledger_checkpoint"]["event_count"] > 1:
                raise OSError("synthetic anchor failure")
            return _atomic_json(path, value)
        with patch("truth_discount.deferred_judging._atomic_json", side_effect=fail_reservation):
            with self.assertRaises((OSError, ValueError)):
                await self.collect(http)
        self.assertEqual(http.requests, [])
        self.assertTrue(self.last_budget["blocked"])
        self.assertGreater(self.last_budget["reserved_usd"], 0)
        self.assertEqual(self.before, inventory(self.source))

    async def test_nonoverlapping_saved_shards_join_and_portable_source_copy_replays(self):
        second = self.root / "second"
        await run_town(self.config, build_manifest(self.config)[1], FixtureBackend(), second, defer_judging=True)
        p = plan_judging([second, self.source], self.profile)
        self.assertEqual(p["phone_outcomes"], 24)
        await self.collect(sources=[self.source, second])
        copied = self.root / "portable-copy"
        shutil.copytree(self.source, copied)
        result = replay_judging([second, copied], self.output, self.profile)
        self.assertEqual(result["phone_outcomes"], 24)
        self.assertEqual(result["descriptive_first_attempt"]["complete_pairs"], 1)
        self.assertEqual(result["descriptive_first_attempt"]["defined_conditional_pairs"], 1)

    async def test_approved_collection_lineage_is_bound_and_missing_planned_town_rejected(self):
        from test_live_cli import approved_test_manifest, MockHTTP
        from truth_discount.simulation_execution import allocate_runs, collect_simulations
        actor_manifest = approved_test_manifest(self.config)
        actor_keys = {m["key"] for m in self.config["models"]["agent_models"]}
        actor_manifest["routes"] = {k: v for k, v in actor_manifest["routes"].items() if k in actor_keys}
        selection = build_manifest(self.config)[:2]
        runs, allocation = allocate_runs(self.config, selection)
        source = self.root / "planned-collection"
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE-ACTOR-KEY"}), \
             BudgetLedger(self.root / "actor-ledger.jsonl", 1) as ledger:
            actor = ProviderBackend(actor_manifest, ledger, transport=MockHTTP(), evidence_kind="mocked_provider")
            await collect_simulations(self.config, actor_manifest, runs, source, actor,
                allocation=allocation, execution_authorized=True, spending_authorized=True)
        p = plan_judging(source, self.profile)
        lineage = p["source"]["collections"][0]
        self.assertTrue(lineage["collection_plan_verified"])
        self.assertFalse(lineage["ledger_history_verified"])
        self.assertEqual(lineage["allocation"]["allocation_id"], allocation["allocation_id"])
        self.assertIn("budget_checkpoint.json", lineage["control_file_sha256"])
        shutil.rmtree(source / runs[-1]["run_id"])
        with self.assertRaisesRegex(ValueError, "missing planned generations"):
            plan_judging(source, self.profile)

    async def test_grading_cannot_write_inside_source(self):
        with BudgetLedger(self.root / "l.jsonl", 1) as ledger:
            b = ProviderBackend(self.profile["provider_manifest"], ledger, transport=HTTP(), evidence_kind="mocked_provider")
            with self.assertRaisesRegex(ValueError, "outside"):
                await judge_collection(self.source, self.source / "grades", self.profile, b,
                    execution_authorized=True, spending_authorized=True)
        self.assertEqual(self.before, inventory(self.source))

    async def test_legacy_pilot_needs_explicit_source_format_and_keeps_all_twelve(self):
        legacy = self.root / "legacy"
        await run_town(self.config, self.run, FixtureBackend(), legacy)
        with self.assertRaises(ValueError):
            plan_judging(legacy, self.profile)
        p = copy.deepcopy(self.profile);p["source_format"] = "legacy_pilot"
        planned = plan_judging(legacy, p)
        self.assertEqual(planned["phone_outcomes"], 12)
        result = await self.collect(current=p, sources=legacy)
        self.assertEqual(result["valid_first_attempt"], 12)

    async def test_comparison_reports_model_agreement_not_semantic_gold(self):
        await self.collect()
        other = profile(self.config, name="judge-b")
        await self.collect(current=other, http=HTTP(force=json.dumps({"label": "NOT_MENTIONED", "quote": ""})))
        info = compare_judgments(self.source, [(self.output, self.profile), (self.output, other)])
        self.assertFalse(info["semantic_accuracy_established"])
        self.assertEqual(info["provider_api_calls"], 0)
        compared = info["comparisons"][0]
        self.assertEqual(compared["valid_both"], 12)
        self.assertGreater(len(compared["disagreements"]), 0)
        self.assertIsNone(compared["numeric_score_agreement"])

    async def test_explicit_partial_phone_selection_is_exact_and_does_not_invent_complete_towns(self):
        p = profile(self.config, population="all_phones")
        original = plan_judging(self.source, p)
        ids = [x["item_id"] for x in original["items"][:5]]
        p["selection"] = make_judge_selection(self.source, p, ids, approved=True)
        selected = plan_judging(self.source, p)
        self.assertEqual((selected["source_phone_outcomes"], selected["phone_outcomes"]), (12, 5))
        self.assertEqual(selected["planned_model_judgments"], 5)
        http = HTTP()
        result = await self.collect(http, current=p)
        self.assertEqual(len(http.requests), 5)
        self.assertEqual(result["phone_outcomes"], 5)
        self.assertEqual({r["item_id"] for r in result["items"]}, set(ids))
        self.assertEqual(result["descriptive_first_attempt"]["complete_towns"], 0)
        town = result["descriptive_first_attempt"]["towns"][0]
        self.assertEqual(town["unselected_phone_outcomes"], 7)
        self.assertIsNone(town["metrics"]["belief_mean"])
        self.assertEqual(self.before, inventory(self.source))

    def test_selection_missing_duplicate_source_and_item_hashes_cannot_be_silently_repaired(self):
        p = copy.deepcopy(self.profile)
        ids = [x["item_id"] for x in plan_judging(self.source, p)["items"][:3]]
        p["selection"] = make_judge_selection(self.source, p, ids)
        self.assertIn("selection", " ".join(plan_judging(self.source, p)["execution_gates"]))
        for field, value in (("source_sha256", "0" * 64), ("items_sha256", "0" * 64),
                             ("item_ids", ["0" * 32]), ("item_ids", [ids[0], ids[0]])):
            with self.subTest(field=field, value=value):
                wrong = copy.deepcopy(p);wrong["selection"][field] = value
                with self.assertRaises(ValueError):
                    plan_judging(self.source, wrong)
        with self.assertRaises(ValueError):
            make_judge_selection(self.source, self.profile, [ids[0], ids[0]])

    async def test_matched_profiles_can_compare_same_frozen_subset_and_reject_different_selections(self):
        first = profile(self.config, population="all_phones")
        ids = [x["item_id"] for x in plan_judging(self.source, first)["items"][:5]]
        first["selection"] = make_judge_selection(self.source, first, ids, approved=True)
        second = copy.deepcopy(first);second["profile_id"] = "second-subset"
        await self.collect(current=first)
        await self.collect(current=second)
        matched = compare_judgments(self.source, [(self.output, first), (self.output, second)])
        self.assertEqual(matched["comparisons"][0]["valid_both"], 5)
        third = profile(self.config, name="different-subset", population="all_phones")
        all_items = plan_judging(self.source, third)["items"]
        third["selection"] = make_judge_selection(self.source, third, [i["item_id"] for i in all_items[1:6]], approved=True)
        await self.collect(current=third)
        with self.assertRaisesRegex(ValueError, "row identities"):
            compare_judgments(self.source, [(self.output, first), (self.output, third)])


if __name__ == "__main__":
    unittest.main()
