"""Mocked actor collection and custody checks. No provider network or real keys."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_live_cli import approved_test_manifest, MockHTTP
from truth_discount.budget import BudgetLedger
from truth_discount.cli import main
from truth_discount.config import build_manifest, load_config
from truth_discount.execution import select_runs
from truth_discount.contracts import digest
from truth_discount.providers import ProviderBackend
from truth_discount.simulation_execution import (allocate_runs, collect_simulations,
                                                 review_simulations, simulation_plan)

ROOT = Path(__file__).resolve().parents[1]


class SimulationExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.providers = approved_test_manifest(self.config)
        self.providers["routes"] = {k: v for k, v in self.providers["routes"].items()
                                    if k in {r["key"] for r in self.config["models"]["agent_models"]}}
        selection = select_runs(self.config, [self.config["models"]["agent_models"][0]["key"]])[:4]
        self.runs, self.allocation = allocate_runs(self.config, selection)

    def test_six_main_allocations_are_complete_disjoint_balanced_and_order_independent(self):
        config = load_config(ROOT / "configs/main_config.json")
        full = build_manifest(config)
        seen, allocation_ids = set(), set()
        for index in range(6):
            runs, allocation = allocate_runs(config, full, shard_count=6, shard_index=index)
            reversed_runs, same = allocate_runs(config, list(reversed(full)), shard_count=6, shard_index=index)
            self.assertEqual((runs, allocation), (reversed_runs, same))
            self.assertEqual((len(runs), allocation["planned_pairs"], allocation["max_phone_outcomes"]),
                             (1664, 832, 19968))
            for model in {r["model_key"] for r in full}:
                self.assertEqual(sum(r["model_key"] == model for r in runs), 832)
                for artist in config["artists"]["artist_pool"]:
                    self.assertEqual(sum(r["model_key"] == model and r["real_artist"] == artist for r in runs), 416)
            for artist in config["artists"]["artist_pool"]:
                self.assertEqual(sum(r["real_artist"] == artist for r in runs), 832)
            self.assertEqual(sum(r["condition_type"] == "rumor" for r in runs), 832)
            self.assertFalse(seen.intersection(allocation["run_ids"]))
            seen.update(allocation["run_ids"])
            allocation_ids.add(allocation["allocation_id"])
        self.assertEqual(len(seen), 9984)
        self.assertEqual(len(allocation_ids), 1)

    def test_invalid_or_unpaired_allocations_reject(self):
        for count, index in ((0, 0), (2, 2), (True, 0), (2, -1)):
            with self.assertRaises(ValueError):
                allocate_runs(self.config, self.runs, shard_count=count, shard_index=index)
        with self.assertRaisesRegex(ValueError, "both twins"):
            allocate_runs(self.config, self.runs[:1])
        changed = deepcopy(self.runs)
        changed[0]["announced_artist"] = "Changed stimulus"
        with self.assertRaisesRegex(ValueError, "source manifest"):
            allocate_runs(self.config, changed)

    def test_actor_plan_has_no_judge_key_or_batch_gate(self):
        info = simulation_plan(self.config, self.providers, self.runs, self.allocation)
        self.assertEqual(info["execution_gates"], [])
        self.assertIsNone(info["primary_judge_key"])
        self.assertEqual(info["execution_mode"], "simulation_only")

    def test_forged_allocation_metadata_is_recomputed_not_trusted(self):
        for field, value in (("source_towns", 9984), ("source_pairs", 4992),
                             ("shard_index", 1), ("version", "invented-algorithm"),
                             ("allocation_id", "0"*64)):
            with self.subTest(field=field):
                forged = deepcopy(self.allocation)
                forged[field] = value
                forged["shard_sha256"] = digest({k: v for k, v in forged.items() if k != "shard_sha256"})
                with self.assertRaises(ValueError):
                    simulation_plan(self.config, self.providers, self.runs, forged)

    def test_resealed_runtime_mismatch_and_empty_ledger_binding_are_rejected(self):
        output = self.root / "output"
        self.collect(output, self.root / "ledger.jsonl", MockHTTP())
        directory = output / self.runs[0]["run_id"]
        path = directory / "manifest.json"
        original = path.read_bytes()
        altered = json.loads(original)
        altered["runtime"]["python"] = "different-version"
        altered["source_runtime_sha256"] = digest({"runtime": altered["runtime"],
                                                   "source_files_sha256": altered["source_files_sha256"]})
        path.write_text(json.dumps(altered))
        with self.assertRaisesRegex(ValueError, "runtime fingerprint"):
            review_simulations(output)
        path.write_bytes(original)
        plan_file, cp_file = output / "execution_plan.json", output / "budget_checkpoint.json"
        plan_value, checkpoint = json.loads(plan_file.read_text()), json.loads(cp_file.read_text())
        plan_value["ledger_binding"] = {}
        checkpoint["execution_plan_sha256"] = digest(plan_value)
        plan_file.write_text(json.dumps(plan_value))
        cp_file.write_text(json.dumps(checkpoint))
        with self.assertRaisesRegex(ValueError, "ledger binding"):
            review_simulations(output)

    def collect(self, output, ledger_path, http, *, resume=False, runs=None, allocation=None):
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY",
                                     "OTHER_TEST_PROVIDER_KEY": "FAKE_SECOND_ACCOUNT"}), \
             patch("socket.create_connection", side_effect=AssertionError("network forbidden")), \
             BudgetLedger(ledger_path, "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            return asyncio.run(collect_simulations(self.config, self.providers,
                self.runs if runs is None else runs, output, backend,
                allocation=self.allocation if allocation is None else allocation,
                resume=resume, max_concurrent_towns=2,
                execution_authorized=True, spending_authorized=True))

    def test_mocked_actor_only_collection_resume_and_custody_transfer(self):
        output, ledger_path = self.root / "output", self.root / "ledger.jsonl"
        http = MockHTTP()
        result = self.collect(output, ledger_path, http)
        self.assertEqual(result["completed_towns"], 4)
        self.assertEqual(result["phone_transcripts"], 48)
        self.assertEqual(result["current_attempt_usage"]["provider_api_calls"], 0)
        self.assertFalse(result["study_results_generated"])
        self.assertEqual(result["evaluation_status"], "pending")
        self.assertTrue(all("deepinfra.com" in r["url"] for r in http.requests))
        original = {p.relative_to(output): p.read_bytes() for p in output.glob("*/*") if p.is_file()}
        again = MockHTTP()
        rerun = self.collect(output, ledger_path, again, resume=True)
        self.assertEqual((rerun["skipped_verified_towns"], again.requests), (4, []))
        self.assertEqual(original, {p: (output/p).read_bytes() for p in original})
        # Move, rather than copy and concurrently spend from, the custody unit.
        moved = self.root / "new-owner"
        moved.mkdir()
        shutil.move(str(output), str(moved / "output"))
        shutil.move(str(ledger_path), str(moved / "ledger.jsonl"))
        handover = self.collect(moved / "output", moved / "ledger.jsonl", MockHTTP(), resume=True)
        self.assertEqual(handover["skipped_verified_towns"], 4)
        with self.assertRaisesRegex(ValueError, "ledger identity"):
            self.collect(moved / "output", self.root / "fresh-ledger.jsonl", MockHTTP(), resume=True)

    def test_two_shards_accept_personal_env_labels_but_reject_overlap_and_route_changes(self):
        selection = self.runs
        for i in range(2):
            if i == 1:
                for route in self.providers["routes"].values():
                    route["api_key_env"] = "OTHER_TEST_PROVIDER_KEY"
            runs, allocation = allocate_runs(self.config, selection, shard_count=2, shard_index=i)
            self.collect(self.root / str(i), self.root / f"ledger-{i}.jsonl", MockHTTP(),
                         runs=runs, allocation=allocation)
        result = review_simulations([self.root / "0", self.root / "1"])
        self.assertTrue(result["full_allocation_present"])
        self.assertEqual(result["completed_pairs"], 2)
        self.assertFalse(any(c["ledger_history_verified"] for c in result["collections"]))
        duplicate = self.root / "duplicate"
        shutil.copytree(self.root / "0", duplicate)
        with self.assertRaisesRegex(ValueError, "overlap"):
            review_simulations([self.root / "0", duplicate])
        # A different operational route is not excused as a local account label.
        key = self.runs[0]["model_key"]
        self.providers["routes"][key]["timeout_seconds"] += 1
        runs, allocation = allocate_runs(self.config, selection, shard_count=2, shard_index=1)
        self.collect(self.root / "different-route", self.root / "different-route-ledger.jsonl", MockHTTP(),
                     runs=runs, allocation=allocation)
        with self.assertRaisesRegex(ValueError, "actor route differs"):
            review_simulations([self.root / "0", self.root / "different-route"])

    def test_direct_noncanonical_selection_rejects_before_model_submission(self):
        http = MockHTTP()
        with BudgetLedger(self.root / "ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            with self.assertRaisesRegex(ValueError, "canonical pair allocation"):
                asyncio.run(collect_simulations(self.config, self.providers, list(reversed(self.runs)),
                    self.root / "output", backend, execution_authorized=True, spending_authorized=True))
        self.assertEqual(http.requests, [])
        self.assertFalse((self.root / "output").exists())

    def test_preview_and_hold_gate_never_open_budget_or_backend(self):
        path = self.root / "providers.json"
        path.write_text(json.dumps(self.providers))
        args = ["simulate", "--providers", str(path), "--output", str(self.root / "preview")]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), \
             patch("truth_discount.providers.ProviderBackend", side_effect=AssertionError("backend built")), \
             patch("truth_discount.budget.BudgetLedger", side_effect=AssertionError("ledger opened")):
            self.assertEqual(main(args), 0, err.getvalue())
            self.assertEqual(main(args + ["--execute"]), 1)
        self.assertEqual(json.loads(out.getvalue())["provider_api_calls"], 0)
        self.assertIn("spending hold", err.getvalue())
        self.assertFalse((self.root / "preview").exists())


if __name__ == "__main__":
    unittest.main()
