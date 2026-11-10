"""Resealed synthetic tampering cannot bypass actor semantic replay."""

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import stat
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from truth_discount.artifacts import InvalidBundle, audit_town
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import GenerationResponse, canonical_bytes, capture, digest, usage_totals
from truth_discount.fixtures import FixtureBackend
from truth_discount.runner import run_town
from truth_discount.simulation_artifacts import (_configured_run_index, _exports, audit_simulation,
                                                 grading_items, save_simulation)
from test_replay_versions import MockReceipts


class SimulationArtifactTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.run = build_manifest(self.config)[0]

    async def make(self, backend=None):
        town = await run_town(self.config, self.run, backend or FixtureBackend(), self.root, defer_judging=True)
        return town, self.root / town["run_id"]

    def reseal(self, directory, town):
        # Model an editor who updates every exported checksum after tampering.
        for name, value in _exports(town, self.config).items():
            (directory / name).write_bytes(value)
        manifest = json.loads((directory / "manifest.json").read_bytes())
        for name in manifest["files"]:
            manifest["files"][name] = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        (directory / "manifest.json").write_bytes(canonical_bytes(manifest))

    async def test_items_are_stable_attempt_bound_and_contain_all_phones(self):
        town, directory = await self.make()
        before = {p.name: p.read_bytes() for p in directory.iterdir()}
        items = grading_items(directory)
        self.assertEqual(items, grading_items(directory))
        self.assertEqual({x["seat_id_private"] for x in items}, set(range(1, 13)))
        self.assertEqual(len({x["item_id"] for x in items}), 12)
        for item in items:
            self.assertEqual(set(item), {"item_id", "run_id", "generation_attempt_id", "seat_id_private",
                                         "target_artist", "phone_transcript", "phone_sha256", "funnel_trigger_step"})
            self.assertEqual(item["phone_sha256"], digest(item["phone_transcript"]))
            self.assertEqual(item["generation_attempt_id"], town["generation_attempt_id"])
            self.assertEqual(item["target_artist"], town["announced_artist"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
        with self.assertRaisesRegex(InvalidBundle, "manifest files|unsupported schema"):
            audit_town(directory)

    async def test_actor_source_runtime_fingerprint_and_immutable_save(self):
        town, directory = await self.make()
        manifest = json.loads((directory / "manifest.json").read_bytes())
        self.assertEqual(manifest["source_runtime_sha256"], digest({k: manifest[k] for k in
                                                                  ["runtime", "source_files_sha256"]}))
        self.assertIn("runner.py", manifest["source_files_sha256"])
        with self.assertRaisesRegex(InvalidBundle, "overwrite"):
            save_simulation(directory, town, self.config)
        manifest["runtime"]["python"] = "changed"
        (directory / "manifest.json").write_bytes(canonical_bytes(manifest))
        with self.assertRaisesRegex(InvalidBundle, "fingerprint"):
            audit_simulation(directory)

    async def test_seal_fsyncs_all_payloads_before_publishing_manifest(self):
        town, _ = await self.make()
        directory = self.root / "durable" / town["run_id"]
        events, descriptor_names = [], {}
        real_open, real_fsync = Path.open, os.fsync

        def opened(path, *args, **kwargs):
            stream = real_open(path, *args, **kwargs)
            descriptor_names[stream.fileno()] = path.name
            return stream

        def synced(descriptor):
            regular = stat.S_ISREG(os.fstat(descriptor).st_mode)
            events.append(descriptor_names.get(descriptor) if regular else "DIRECTORY")
            real_fsync(descriptor)

        with patch.object(Path, "open", new=opened), \
             patch("truth_discount.simulation_artifacts.os.fsync", side_effect=synced):
            save_simulation(directory, town, self.config)
        files = [event for event in events if event != "DIRECTORY"]
        self.assertEqual(set(files[:-1]), {"town.json", "config.json", "trace.jsonl", "agent_histories.json",
                                          "phone_transcripts.json", "grading_items_PRIVATE.jsonl"})
        self.assertEqual(files[-1], ".manifest.pending")
        if os.name != "nt":
            self.assertEqual(events[-2:], ["DIRECTORY", "DIRECTORY"])
        self.assertFalse((directory / ".manifest.pending").exists())
        self.assertEqual(audit_simulation(directory), town)

    async def test_payload_or_manifest_sync_failure_cannot_publish_a_valid_seal(self):
        town, _ = await self.make()
        real_fsync = os.fsync
        for fail_at in (1, 7):
            directory = self.root / f"sync-failure-{fail_at}" / town["run_id"]
            regular_count = 0

            def failed_sync(descriptor):
                nonlocal regular_count
                if stat.S_ISREG(os.fstat(descriptor).st_mode):
                    regular_count += 1
                    if regular_count == fail_at:
                        raise OSError("synthetic persistence failure")
                real_fsync(descriptor)

            with patch("truth_discount.simulation_artifacts.os.fsync", side_effect=failed_sync):
                with self.assertRaisesRegex(OSError, "persistence failure"):
                    save_simulation(directory, town, self.config)
            self.assertFalse((directory / "manifest.json").exists())
            with self.assertRaises(InvalidBundle):
                audit_simulation(directory)
            with self.assertRaisesRegex(InvalidBundle, "overwrite"):
                save_simulation(directory, town, self.config)

    async def test_resealed_actor_request_cannot_invent_a_private_context(self):
        town, directory = await self.make()
        call = town["calls"][0]
        call["request"]["messages"][0]["content"] += " Fabricated private state."
        call["request_sha256"] = digest(call["request"])
        self.reseal(directory, town)
        with self.assertRaises(InvalidBundle):
            audit_simulation(directory)

    async def test_run_index_cache_is_immutable_bounded_and_full_config_bound(self):
        first, directory = await self.make()
        second_run = build_manifest(self.config)[1]
        second = await run_town(self.config, second_run, FixtureBackend(), self.root, defer_judging=True)
        _configured_run_index.cache_clear()
        with patch("truth_discount.simulation_artifacts.build_manifest", wraps=build_manifest) as builder:
            audited = audit_simulation(directory)
            audit_simulation(self.root / second["run_id"])
            self.assertEqual(builder.call_count, 1)
            index = _configured_run_index(canonical_bytes(self.config), first["model_key"])
            with self.assertRaises(TypeError):
                index[first["run_id"]] = b"{}"
            audited["seed_id"] = 999
            self.assertEqual(audit_simulation(directory)["seed_id"], first["seed_id"])
            self.config = copy.deepcopy(self.config)
            self.config["meta"]["town_name"] = "Changed town context"
            first["config_sha256"] = digest(self.config)
            self.reseal(directory, first)
            with self.assertRaises(InvalidBundle):
                audit_simulation(directory)
            self.assertEqual(builder.call_count, 2)
        self.assertEqual(_configured_run_index.cache_info().maxsize, 4)

    async def test_resealed_history_phone_decision_and_missing_coverage_are_rejected(self):
        original, directory = await self.make()
        for defect in ("history", "phone", "decision", "missing_phone", "duplicate_phone", "callback_removed"):
            with self.subTest(defect=defect):
                town = copy.deepcopy(original)
                if defect == "history":
                    town["agent_histories"]["1"].append({"role": "user", "content": "Invented feedback."})
                elif defect == "phone":
                    town["scene_5_phone_transcripts"][0]["lines"][1]["text"] = "Fabricated listener reply."
                elif defect == "decision":
                    town["scene_2_first_hand_decisions"][0]["decision"] = "SKIP"
                elif defect == "missing_phone":
                    town["scene_5_phone_transcripts"].pop()
                elif defect == "duplicate_phone":
                    town["scene_5_phone_transcripts"].append(copy.deepcopy(town["scene_5_phone_transcripts"][0]))
                else:
                    town["calls"].pop()
                    town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
                self.reseal(directory, town)
                with self.assertRaises(InvalidBundle):
                    audit_simulation(directory)

    async def test_pending_data_cannot_be_resealed_as_judged_or_study_eligible(self):
        original, directory = await self.make()
        for key, value in [("metrics", {"belief_mean": 1}), ("judge_evaluations", [{"label": "FACT"}]),
                           ("study_eligible", True), ("evaluation_status", "completed")]:
            with self.subTest(key=key):
                town = copy.deepcopy(original)
                town[key] = value
                self.reseal(directory, town)
                with self.assertRaises(InvalidBundle):
                    audit_simulation(directory)

    async def test_resealed_config_and_call_model_swap_is_not_an_actor_run(self):
        town, directory = await self.make()
        call = town["calls"][0]
        call["kind"] = call["request"]["kind"] = "judge"
        call["request_sha256"] = digest(call["request"])
        self.reseal(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "judge or non-actor"):
            audit_simulation(directory)

    async def test_mocked_receipts_are_replayed_but_not_claimed_as_live_calls(self):
        town, directory = await self.make(MockReceipts(self.config))
        self.assertEqual(audit_simulation(directory), town)
        self.assertEqual(town["token_usage"]["provider_api_calls"], 0)
        self.assertGreater(town["token_usage"]["simulated_provider_requests"], 0)
        call = town["calls"][0]
        call["token_usage"]["input_tokens"] += 1
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        self.reseal(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "raw response usage"):
            audit_simulation(directory)

    async def test_unknown_partial_charge_is_preserved_without_grading(self):
        class ReceiptFailure(RuntimeError):
            pass

        class Failing(MockReceipts):
            async def generate(self, request):
                if request.scene == 2 and request.seat == 1:
                    receipt = self.receipt(request)
                    receipt.update(actual_model=None, request_id=None, input_tokens=None, output_tokens=None,
                                   cached_input_tokens=None, cost_usd=None, cost_status="unknown",
                                   attempts=[{"attempt_index": 1, "status": "failed"}])
                    error = ReceiptFailure("synthetic unknown provider result")
                    error.receipt = receipt
                    raise error
                return await super().generate(request)

        with self.assertRaises(ReceiptFailure):
            await self.make(Failing(self.config))
        directory = self.root / self.run["run_id"]
        town = audit_simulation(directory)
        self.assertIsNone(town["token_usage"]["cost_usd"])
        self.assertEqual(town["generation_status"], "failed")
        self.assertEqual((directory / "grading_items_PRIVATE.jsonl").read_bytes(), b"")
        with self.assertRaisesRegex(InvalidBundle, "incomplete generation"):
            grading_items(directory)

    async def test_resealed_priced_usage_cannot_exceed_the_actual_request_cap(self):
        town, directory = await self.make(MockReceipts(self.config))
        call = town["calls"][0]  # GO/SKIP has a five-token cap.
        call["token_usage"]["output_tokens"] = 6
        call["cost_usd"] = call["token_usage"]["cost_usd"] = 0.0000022
        call["raw_response"] = capture(GenerationResponse(call["response"], call["token_usage"]))
        town["token_usage"] = usage_totals(town["calls"], town["evidence_kind"])
        self.reseal(directory, town)
        with self.assertRaisesRegex(InvalidBundle, "native request bounds"):
            audit_simulation(directory)

    async def test_unknown_export_or_invalid_hash_never_enters_handover(self):
        _, directory = await self.make()
        (directory / "unsealed.json").write_text("{}")
        with self.assertRaisesRegex(InvalidBundle, "unexpected simulation artifact"):
            audit_simulation(directory)
        (directory / "unsealed.json").unlink()
        (directory / "trace.jsonl").write_text("{}\n")
        with self.assertRaisesRegex(InvalidBundle, "file hash mismatch"):
            audit_simulation(directory)


if __name__ == "__main__":
    unittest.main()
