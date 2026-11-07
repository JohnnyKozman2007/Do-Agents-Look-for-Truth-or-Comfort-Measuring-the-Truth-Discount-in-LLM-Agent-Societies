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
        with patch("truth_discount.budget.os.fsync", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                ledger.settle(reservation, None)
        self.assertTrue(ledger.summary()["blocked"])
        self.assertIn("storage_failure", ledger.summary()["block_reasons"])
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.1)
        ledger.close()
        self.assertTrue(self.ledger().summary()["blocked"])

    def test_failed_write_during_reserve_never_sends_and_holds_after_restart(self):
        ledger = self.ledger()
        with patch("truth_discount.budget.os.fsync", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                ledger.reserve(.1)
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.1)
        ledger.close()
        # The line may have reached disk; if so it is held as interrupted, never free.
        restarted = self.ledger()
        self.assertEqual(restarted.summary()["reserved_usd"], .1)
        self.assertIn("interrupted_request", restarted.summary()["block_reasons"])

    def test_tampered_duplicate_ids_and_nonfinite_json_rejected(self):
        ledger = self.ledger()
        ledger.reserve(.1)
        ledger.close()
        lines = self.path.read_bytes().splitlines(keepends=True)
        self.path.write_bytes(b"".join(lines[:2] + [lines[1]]))
        with self.assertRaises(BudgetError):
            BudgetLedger(self.path, 1)
        self.path.write_bytes(b'{"limit_usd":NaN,"type":"header","version":2}\n')
        with self.assertRaises(BudgetError):
            BudgetLedger(self.path, 1)

    def test_journal_is_append_only(self):
        ledger = self.ledger(5)
        sizes = []
        for _ in range(50):
            before = self.path.read_bytes()
            ledger.settle(ledger.reserve(.01, {"model_key": "agent"}), .005,
                          {"cost_status": "calculated_from_usage"})
            after = self.path.read_bytes()
            self.assertTrue(after.startswith(before))
            sizes.append(len(after) - len(before))
        # Each request adds two short lines; the cost per request does not grow.
        self.assertEqual(max(sizes), min(sizes))
        self.assertLess(max(sizes), 600)
        ledger.close()
        self.assertAlmostEqual(self.ledger(5).summary()["settled_usd"], .25)

    def test_torn_final_append_is_dropped_and_pending_request_stays_held(self):
        ledger = self.ledger()
        settled = ledger.reserve(.2)
        ledger.settle(settled, .1, {"cost_status": "calculated_from_usage"})
        pending = ledger.reserve(.3)
        ledger.close()
        with self.path.open("ab") as stream:   # crash mid-way through the settle line
            stream.write(b'{"actual_usd":"0.05","id":"' + pending.encode())
        restarted = self.ledger()
        summary = restarted.summary()
        self.assertEqual(summary["settled_usd"], .1)
        self.assertEqual(summary["reserved_usd"], .3)
        self.assertEqual(summary["block_reasons"], ["interrupted_request"])
        self.assertTrue(self.path.read_bytes().endswith(b"\n"))
        self.assertEqual([row["id"] for row in restarted.unknown_reservations()], [pending])

    def test_corrupt_earlier_line_is_not_skipped(self):
        ledger = self.ledger()
        ledger.settle(ledger.reserve(.2), .1)
        ledger.reserve(.1)
        ledger.close()
        lines = self.path.read_bytes().splitlines(keepends=True)
        lines[2] = b'{"broken"\n'
        self.path.write_bytes(b"".join(lines))
        with self.assertRaisesRegex(BudgetError, "line 3"):
            BudgetLedger(self.path, 1)

    def test_reconcile_records_billed_amount_and_unblocks(self):
        ledger = self.ledger()
        unknown = ledger.reserve(.4)
        ledger.settle(unknown, None, {"cost_status": "unknown", "error_code": "request_failed"})
        with self.assertRaises(BudgetError):
            ledger.reconcile(unknown, None, "missing amount")
        with self.assertRaises(BudgetError):
            ledger.reconcile(unknown, .1, "bad\nnote")
        summary = ledger.reconcile(unknown, .02, "DeepInfra usage page, 7 Nov")
        self.assertFalse(summary["blocked"])
        self.assertEqual(summary["settled_usd"], .02)
        self.assertEqual(summary["reconciled_count"], 1)
        with self.assertRaises(BudgetError):
            ledger.reconcile(unknown, .02, "twice")
        settled = ledger.reserve(.1)
        ledger.settle(settled, .05)
        with self.assertRaises(BudgetError):
            ledger.reconcile(settled, 0, "not unknown")
        ledger.close()
        restarted = self.ledger()
        self.assertEqual(restarted.summary()["settled_usd"], .07)
        self.assertFalse(restarted.summary()["blocked"])

    def test_reconcile_above_hold_is_recorded_and_blocks(self):
        ledger = self.ledger()
        unknown = ledger.reserve(.1)
        ledger.settle(unknown, None)
        ledger.reconcile(unknown, .3, "billed more than the declared bound")
        self.assertIn("reservation_exceeded", ledger.summary()["block_reasons"])
        with self.assertRaises(BudgetBlocked):
            ledger.reserve(.01)

    def test_old_single_file_format_is_refused_not_overwritten(self):
        legacy = '{"block_reasons":[],"limit_usd":"1","reservations":[],"version":1}'
        self.path.write_text(legacy)
        with self.assertRaisesRegex(BudgetError, "old single-file"):
            BudgetLedger(self.path, 1)
        self.assertEqual(self.path.read_text(), legacy)


if __name__ == "__main__":
    unittest.main()
