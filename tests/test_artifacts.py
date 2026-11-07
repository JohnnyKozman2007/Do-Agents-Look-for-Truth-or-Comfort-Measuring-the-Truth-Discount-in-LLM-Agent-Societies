"""Saved data must replay from responses, not merely agree with its own hashes."""

import asyncio
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from truth_discount.artifacts import InvalidBundle, audit_town, save_town, summarize
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import canonical_bytes, digest
from truth_discount.fixtures import FixtureBackend
from truth_discount.runner import run_town
from truth_discount.scoring import town_metrics

ROOT = Path(__file__).resolve().parents[1]


class ArtifactTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.runs = build_manifest(self.config)

    async def make(self, index=0, mode="mixed"):
        town = await run_town(self.config, self.runs[index], FixtureBackend(mode), self.root)
        return town, self.root / town["run_id"]

    def reseal_file(self, directory, name, value):
        (directory / name).write_bytes(value)
        manifest = json.loads((directory / "manifest.json").read_text())
        manifest["files"][name] = hashlib.sha256(value).hexdigest()
        (directory / "manifest.json").write_bytes(canonical_bytes(manifest))

    def save(self, directory, town):
        decisions = town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]
        town["metrics"] = town_metrics(self.config, town["judge_evaluations"], decisions)
        save_town(directory, town, self.config)

    async def test_saved_twins_replay_with_separate_judge_crosswalk_and_no_provider_usage(self):
        town, directory = await self.make()
        await self.make(1)
        self.assertEqual(audit_town(directory), town)
        report = summarize(self.root)
        self.assertEqual((report["towns"], report["pairs"], report["completed_towns"]), (2, 1, 2))
        self.assertEqual(report["provider_api_calls"], 0)
        self.assertFalse(report["study_results_generated"])
        self.assertEqual(report["paired_fixture_metrics"][0]["status"], "complete")
        requests = [json.loads(x) for x in (directory / "judge_requests.jsonl").read_text().splitlines()]
        for row in requests:
            self.assertEqual(set(row), {"custom_id", "messages", "settings"})
            self.assertEqual(len(row["custom_id"]), 32)
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertIn("runner.py", manifest["source_files_sha256"])
        self.assertIn("config.py", manifest["source_files_sha256"])

    async def test_all_silent_phones_remain_undefined_primary_with_no_judge_calls(self):
        _, directory = await self.make(mode="silent")
        town = audit_town(directory)
        self.assertIsNone(town["metrics"]["belief_mean"])
        self.assertEqual(town["metrics"]["omission_rate"], 1)
        self.assertEqual(town["judge_inputs"], [])
        self.assertEqual((directory / "judge_requests.jsonl").read_bytes(), b"")

    async def test_file_corruption_and_missing_files_fail_before_scoring(self):
        _, directory = await self.make()
        (directory / "trace.jsonl").write_text("changed")
        with self.assertRaisesRegex(InvalidBundle, "file hash mismatch"):
            audit_town(directory)
        (directory / "trace.jsonl").unlink()
        with self.assertRaises(FileNotFoundError):
            audit_town(directory)

    async def test_changed_judge_label_fails_even_after_rescoring_and_resealing(self):
        town, directory = await self.make()
        entry = next(x for x in town["judge_evaluations"] if x["provenance"] == "synthetic_judge_callback")
        entry["label"] = "FACT" if entry["label"] != "FACT" else "SKEPTICAL"
        self.save(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "judge parser replay mismatch"):
            audit_town(directory)

    async def test_changed_go_decision_fails_even_with_consistent_exports(self):
        town, directory = await self.make()
        entry = town["scene_2_first_hand_decisions"][0]
        entry["decision"] = "SKIP" if entry["decision"] == "GO" else "GO"
        self.save(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "decision parser replay mismatch"):
            audit_town(directory)

    async def test_go_cost_and_observation_are_recomputed(self):
        town, directory = await self.make()
        town["scene_2_first_hand_decisions"][0]["balance_usd"] = 40
        self.save(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "budget mismatch"):
            audit_town(directory)

    async def test_extra_private_field_in_judge_prompt_fails_reconstruction(self):
        town, directory = await self.make()
        item = town["judge_inputs"][0]
        item["input"]["messages"][0]["content"] += "\nPrivate condition: rumor"
        item["input_sha256"] = digest(item["input"])
        self.save(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "blind judge input mismatch"):
            audit_town(directory)

    async def test_missing_input_for_judge_call_cannot_disappear_from_export(self):
        town, directory = await self.make()
        town["judge_inputs"].pop()
        self.save(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "judge/callback coverage mismatch"):
            audit_town(directory)

    async def test_judge_generation_settings_must_match_frozen_config(self):
        town, directory = await self.make()
        call = next(x for x in town["calls"] if x["kind"] == "judge")
        call["request"]["settings"]["max_tokens"] += 1
        call["request_sha256"] = digest(call["request"])
        self.save(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "judge settings mismatch"):
            audit_town(directory)

    async def test_csv_crosswalk_and_markdown_are_replayed_even_if_rehashed(self):
        town, directory = await self.make()
        for filename in ("listener_scores.csv", "transcript.md", "judge_crosswalk_PRIVATE.jsonl"):
            with self.subTest(filename=filename):
                self.save(directory, town)
                raw = (directory / filename).read_bytes()
                changed = raw + b"changed" if filename != "judge_crosswalk_PRIVATE.jsonl" else b"{}\n"
                self.reseal_file(directory, filename, changed)
                with self.assertRaises(InvalidBundle):
                    audit_town(directory)

    async def test_callback_failure_preserves_missing_results_and_replays(self):
        class Broken(FixtureBackend):
            async def generate(self, request):
                if request.scene == 5 and request.seat == 1:
                    raise TimeoutError("local fixture timeout")
                return await super().generate(request)

        town = await run_town(self.config, self.runs[0], Broken(), self.root)
        directory = self.root / town["run_id"]
        self.assertEqual(audit_town(directory)["run_status"], "timeout")
        self.assertEqual(town["metrics"]["status"], "incomplete")
        self.assertIsNone(town["metrics"]["belief_mean"])

    async def test_phone_timeout_cannot_be_resealed_as_completed_nonmention(self):
        class PhoneTimeout(FixtureBackend):
            async def generate(self, request):
                if request.scene == 5 and request.seat == 1 and request.kind == "chat":
                    raise TimeoutError("local phone timeout")
                return await super().generate(request)

        town = await run_town(self.config, self.runs[0], PhoneTimeout(), self.root)
        directory = self.root / town["run_id"]
        self.assertEqual(audit_town(directory)["metrics"]["n_invalid"], 1)
        raw_calls = copy.deepcopy(town["calls"])
        phone = next(p for p in town["scene_5_phone_transcripts"] if p["seat_id"] == 1)
        self.assertFalse(any(line["speaker"] == "listener" for line in phone["lines"]))
        phone["lines"].append({
            "speaker": "caller", "name": phone["lines"][0]["name"],
            "text": self.config["prompts_and_templates"]["scene_5_phone_call_funnel"][-1]["loved_one_line"],
            "funnel_step": 6,
        })
        town["judge_evaluations"].append({
            "seat_id": 1, "status": "valid", "label": "NOT_MENTIONED", "quote": "",
            "error": None, "provenance": "runner_phone_funnel_rule",
        })
        self.save(directory, town)
        self.assertEqual(town["calls"], raw_calls)
        self.assertEqual(town["metrics"]["n_invalid"], 0)
        with self.assertRaisesRegex(InvalidBundle, "phone funnel replay mismatch"):
            audit_town(directory)

    async def test_deleted_catchup_transcripts_fail_despite_resealed_exports(self):
        town, directory = await self.make()
        raw_calls = copy.deepcopy(town["calls"])
        self.assertEqual(sum(c["scene"] == 3 and c["status"] == "completed"
                             for c in raw_calls), 18)
        self.assertEqual(len(town["scene_3_catch_up_transcripts"]), 6)
        town["scene_3_catch_up_transcripts"] = []
        self.save(directory, town)
        self.assertEqual(town["calls"], raw_calls)
        with self.assertRaisesRegex(InvalidBundle, "catch-up callback coverage mismatch"):
            audit_town(directory)

    async def test_rerun_cannot_overwrite_a_saved_town(self):
        town, directory = await self.make()
        before = (directory / "manifest.json").read_bytes()
        with self.assertRaises(FileExistsError):
            await run_town(self.config, self.runs[0], FixtureBackend(), self.root)
        self.assertEqual((directory / "manifest.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
