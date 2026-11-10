"""Crash-boundary regeneration checks with fake transports and sockets blocked."""
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from test_live_cli import approved_test_manifest, MockHTTP
from test_pr10_review_fixes import _FirstChatEmpty
from truth_discount import simulation_execution
from truth_discount.artifacts import archived_attempt_paths
from truth_discount.budget import BudgetLedger
from truth_discount.config import load_config
from truth_discount.execution import select_runs
from truth_discount.providers import ProviderBackend
from truth_discount.simulation_artifacts import audit_simulation
from truth_discount.simulation_execution import allocate_runs, collect_simulations, review_simulations


class ResumeCrashReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output, self.ledger = self.root / "output", self.root / "ledger.jsonl"
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.providers = approved_test_manifest(self.config)
        self.providers["routes"] = {k: v for k, v in self.providers["routes"].items()
                                    if k in {m["key"] for m in self.config["models"]["agent_models"]}}
        selection = select_runs(self.config, [self.config["models"]["agent_models"][0]["key"]])[:4]
        self.runs, self.allocation = allocate_runs(self.config, selection)

    def collect(self, http, *, ledger=None, cap="1", **flags):
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("network forbidden")), \
             BudgetLedger(ledger or self.ledger, cap) as budget:
            backend = ProviderBackend(self.providers, budget, transport=http, evidence_kind="mocked_provider")
            return asyncio.run(collect_simulations(self.config, self.providers, self.runs,
                self.output, backend, allocation=self.allocation, max_concurrent_towns=1,
                execution_authorized=True, spending_authorized=True, **flags))

    def fail_known(self):
        with self.assertRaisesRegex(ValueError, "incomplete town"):
            self.collect(_FirstChatEmpty())

    def test_crash_after_archive_does_not_implicitly_authorize_regeneration(self):
        self.fail_known()
        binding = json.loads((self.output / "execution_plan.json").read_bytes())["ledger_binding"]
        journal = self.ledger.read_bytes()
        real_archive = simulation_execution._archive_partial

        def archive_then_crash(output, directory):
            real_archive(output, directory)
            raise OSError("synthetic crash after durable archive, before resume log")

        crash_http = MockHTTP()
        with patch.object(simulation_execution, "_archive_partial", side_effect=archive_then_crash):
            with self.assertRaisesRegex(OSError, "synthetic crash"):
                self.collect(crash_http, resume=True, regenerate_failed=True)
        self.assertEqual(crash_http.requests, [])
        archived = archived_attempt_paths(self.output)
        self.assertEqual(len(archived), 1)
        past = audit_simulation(archived[0])
        self.assertFalse((self.output / past["run_id"]).exists())
        self.assertEqual(self.ledger.read_bytes(), journal)

        ordinary = MockHTTP()
        with self.assertRaisesRegex(ValueError, "regenerate"):
            self.collect(ordinary, resume=True)
        self.assertEqual(ordinary.requests, [])
        self.assertEqual(self.ledger.read_bytes(), journal)

        result = self.collect(MockHTTP(), resume=True, regenerate_failed=True)
        self.assertEqual(result["status"], "generation_complete")
        self.assertEqual(result["failed_generation_attempts"], 1)
        self.assertEqual(result["failed_generation_attempts_by_cell"], {str(past["cell_id"]): 1})
        current = audit_simulation(self.output / past["run_id"])
        self.assertNotEqual(current["generation_attempt_id"], past["generation_attempt_id"])
        self.assertEqual(json.loads((self.output / "execution_plan.json").read_bytes())["ledger_binding"], binding)
        log = [json.loads(line) for line in (self.output / "resume_log.jsonl").read_text().splitlines()]
        self.assertTrue(log[-1]["regenerate_failed"])
        self.assertIn(past["run_id"], log[-1]["regenerated_run_ids"])
        # A later normal resume skips the successful generations, preserving
        # both the paid-attempt record and all sealed actor files.
        sealed = {p.relative_to(self.output): p.read_bytes()
                  for p in self.output.glob("*/*") if p.is_file()}
        successful_journal = self.ledger.read_bytes()
        again = MockHTTP()
        rerun = self.collect(again, resume=True)
        self.assertEqual((rerun["skipped_verified_towns"], again.requests), (4, []))
        self.assertEqual(self.ledger.read_bytes(), successful_journal)
        self.assertEqual(sealed, {p: (self.output / p).read_bytes() for p in sealed})

    def test_explicit_regeneration_cannot_replace_original_ledger_or_cap(self):
        self.fail_known()
        original = self.ledger.read_bytes()
        fresh_http = MockHTTP()
        with self.assertRaisesRegex(ValueError, "original plan|ledger identity"):
            self.collect(fresh_http, ledger=self.root / "fresh.jsonl", resume=True, regenerate_failed=True)
        self.assertEqual(fresh_http.requests, [])
        changed_cap_http = MockHTTP()
        with self.assertRaisesRegex(ValueError, "cap|ceiling|limit"):
            self.collect(changed_cap_http, cap="2", resume=True, regenerate_failed=True)
        self.assertEqual(changed_cap_http.requests, [])
        self.assertEqual(self.ledger.read_bytes(), original)

    def test_explicit_regeneration_does_not_bypass_original_checkpoint(self):
        self.fail_known()
        checkpoint = self.output / "budget_checkpoint.json"
        value = json.loads(checkpoint.read_bytes())
        value["ledger_checkpoint"]["history_sha256"] = "0" * 64
        checkpoint.write_text(json.dumps(value))
        journal = self.ledger.read_bytes()
        http = MockHTTP()
        with self.assertRaisesRegex(ValueError, "checkpoint|history"):
            self.collect(http, resume=True, regenerate_failed=True)
        self.assertEqual(http.requests, [])
        self.assertEqual(self.ledger.read_bytes(), journal)

    def test_explicit_regeneration_never_clears_unknown_charge_hold(self):
        class Timeout(MockHTTP):
            def __call__(self, *args):
                super().__call__(*args)
                raise TimeoutError("synthetic uncertain provider delivery")

        with self.assertRaises(ValueError):
            self.collect(Timeout())
        http = MockHTTP()
        with self.assertRaisesRegex(ValueError, "blocked|unknown"):
            self.collect(http, resume=True, regenerate_failed=True)
        self.assertEqual(http.requests, [])
        self.assertEqual(review_simulations(self.output)["failed_generation_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
