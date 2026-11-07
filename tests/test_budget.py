from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.budget import BudgetLedger, BudgetError, BudgetExceeded, BudgetBlocked, LedgerLocked


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.json"

    def ledger(self, limit=1):
        ledger = BudgetLedger(self.path, limit)
        self.addCleanup(ledger.close)
        return ledger

    def test_reserve_settle_and_restart_preserve_cost(self):
        ledger = self.ledger()
        reservation = ledger.reserve("0.7", {"model_key": "agent"})
        self.assertAlmostEqual(ledger.summary()["available_usd"], .3)
        with self.assertRaises(BudgetExceeded):
            ledger.reserve(.4)
        ledger.settle(reservation, .2, {"cost_status": "calculated_from_usage"})
        self.assertAlmostEqual(ledger.summary()["available_usd"], .8)
        ledger.close()
        restarted = self.ledger()
        self.assertEqual(restarted.summary()["settled_usd"], .2)
        self.assertFalse(restarted.summary()["blocked"])
        with self.assertRaises(BudgetError):
            restarted.settle(reservation, 0)

    def test_unknown_charge_retains_reservation_and_blocks(self):
        ledger = self.ledger()
        reservation = ledger.reserve(.4)
        ledger.settle(reservation, None, {"cost_status": "unknown"})
        self.assertEqual(ledger.summary()["reserved_usd"], .4)
        self.assertEqual(ledger.summary()["settled_usd"], 0)
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.01)
        ledger.close()
        restarted = self.ledger()
        self.assertEqual(restarted.summary()["unknown_count"], 1)
        with self.assertRaises(BudgetBlocked):
            restarted.reserve(0)

    def test_unfinished_request_on_restart_is_unknown_not_free(self):
        ledger = self.ledger()
        ledger.reserve(.25)
        ledger.close()
        restarted = self.ledger()
        self.assertEqual(restarted.summary()["reserved_usd"], .25)
        self.assertIn("interrupted_request", restarted.summary()["block_reasons"])
        with self.assertRaises(BudgetBlocked):
            restarted.reserve(.1)

    def test_exclusive_owner_and_unchangeable_cap(self):
        ledger = self.ledger()
        with self.assertRaises(LedgerLocked):
            BudgetLedger(self.path, 1)
        ledger.close()
        with self.assertRaises(BudgetError):
            BudgetLedger(self.path, 2)
        self.assertEqual(self.ledger().summary()["limit_usd"], 1)

    def test_threads_cannot_oversubscribe(self):
        ledger = self.ledger()
        def attempt(_):
            try:
                return ledger.reserve(.1)
            except BudgetExceeded:
                return None
        with ThreadPoolExecutor(max_workers=12) as pool:
            identifiers = list(pool.map(attempt, range(20)))
        self.assertEqual(sum(item is not None for item in identifiers), 10)
        self.assertEqual(ledger.summary()["available_usd"], 0)
        self.assertEqual(ledger.summary()["reserved_usd"], 1)

    def test_actual_overrun_recorded_and_stops_future_requests(self):
        ledger = self.ledger()
        reservation = ledger.reserve(.1)
        with self.assertRaises(BudgetExceeded):
            ledger.settle(reservation, .2)
        self.assertEqual(ledger.summary()["settled_usd"], .2)
        self.assertIn("reservation_exceeded", ledger.summary()["block_reasons"])
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.01)

    def test_strict_amounts_secret_fields_and_no_partial_mutation(self):
        ledger = self.ledger()
        for value in (True, False, -1, float("nan"), float("inf"), "NaN", "-0.1", None):
            with self.subTest(value=value), self.assertRaises(BudgetError):
                ledger.reserve(value)
        with self.assertRaises(BudgetError):
            ledger.reserve(.1, {"Authorization": "secret"})
        self.assertEqual(ledger.summary()["reservation_count"], 0)
        reservation = ledger.reserve(.1)
        with self.assertRaises(BudgetError):
            ledger.settle(reservation, .01, {"error_body": "secret"})
        self.assertNotIn("secret", self.path.read_text())

    def test_failed_durable_write_prevents_later_requests(self):
        ledger = self.ledger()
        reservation = ledger.reserve(.1)
        with patch("truth_discount.budget.os.replace", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                ledger.settle(reservation, None)
        self.assertTrue(ledger.summary()["blocked"])
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.1)
        ledger.close()
        self.assertTrue(self.ledger().summary()["blocked"])

    def test_tampered_duplicate_ids_and_nonfinite_json_rejected(self):
        ledger = self.ledger()
        ledger.reserve(.1)
        ledger.close()
        data = json.loads(self.path.read_text())
        data["reservations"].append(data["reservations"][0])
        self.path.write_text(json.dumps(data))
        with self.assertRaises(BudgetError):
            BudgetLedger(self.path, 1)
        self.path.write_text('{"version":1,"limit_usd":NaN,"reservations":[],"block_reasons":[]}')
        with self.assertRaises(BudgetError):
            BudgetLedger(self.path, 1)

    def test_tempfile_failure_during_settlement_also_blocks(self):
        ledger = self.ledger()
        reservation = ledger.reserve(.1)
        with patch("truth_discount.budget.tempfile.mkstemp", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                ledger.settle(reservation, None)
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.1)


if __name__ == "__main__":
    unittest.main()
