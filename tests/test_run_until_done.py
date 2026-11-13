"""Recovery wrapper checks use a fake subprocess and never call a provider."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pilot_recovery_wrapper", ROOT / "scripts/run_until_done.py")
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)


class RecoveryWrapperTests(unittest.TestCase):
    def invoke(self, args, response, *, rounds=2):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["run_until_done.py", *args]), \
             patch.dict(os.environ, {}, clear=True), \
             patch.object(wrapper.subprocess, "run", side_effect=response) as run, \
             patch.object(wrapper.time, "sleep") as sleep, \
             patch.object(wrapper, "MAX_ROUNDS", rounds), \
             redirect_stdout(out), redirect_stderr(err):
            result = wrapper.main()
        self.stdout, self.stderr = out.getvalue(), err.getvalue()
        return result, run, sleep

    def auto_args(self, temporary):
        output, ledger = Path(temporary) / "collection", Path(temporary) / "original.jsonl"
        output.mkdir()
        (output / "execution_plan.json").write_text("{}")
        ledger.write_text(json.dumps({"type": "header", "version": 2,
                                      "ledger_id": "a" * 32, "limit_usd": "20"}) + "\n")
        args = ["--auto-reconcile", "--output", str(output), "--ledger", str(ledger), "--budget-usd", "20",
                "--execute", "--spending-authorized"]
        return args, output, ledger

    def test_busy_resume_keeps_original_ledger_cap_and_explicit_flags(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "collection"
            ledger = Path(temporary) / "original.jsonl"
            args = ["--output", str(output), "--ledger", str(ledger), "--budget-usd", "20",
                    "--execute", "--spending-authorized"]

            def response(command, **kwargs):
                self.assertEqual(kwargs["env"], {"PYTHONPATH": str(ROOT / "src")})
                if not output.exists():
                    output.mkdir()
                    (output / "execution_plan.json").write_text("{}")
                    self.assertNotIn("--resume", command)
                    return SimpleNamespace(returncode=1, stdout="", stderr=wrapper.BUSY)
                self.assertIn("--resume", command)
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            code, run, sleep = self.invoke(args, response)
            self.assertEqual(code, 0)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(sleep.call_count, 1)
            for call in run.call_args_list:
                command = call.args[0]
                self.assertEqual(command[command.index("--ledger") + 1], str(ledger))
                self.assertEqual(command[command.index("--budget-usd") + 1], "20")
                self.assertIn("--execute", command)
                self.assertIn("--spending-authorized", command)
            self.assertFalse(ledger.exists())

    def test_unknown_charge_stops_without_retry(self):
        code, run, sleep = self.invoke([], [SimpleNamespace(returncode=1, stdout="", stderr="budget ledger is blocked: unknown charge")])
        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()

    def test_preview_never_adds_spending_or_execution_flags(self):
        code, run, sleep = self.invoke([], [SimpleNamespace(returncode=0, stdout="preview", stderr="")])
        self.assertEqual(code, 0)
        self.assertNotIn("--execute", run.call_args.args[0])
        self.assertNotIn("--spending-authorized", run.call_args.args[0])
        sleep.assert_not_called()

    def test_busy_retries_remain_bounded(self):
        code, run, _ = self.invoke([], [SimpleNamespace(returncode=1, stdout="", stderr=wrapper.BUSY)] * 2)
        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, 2)

    def test_auto_reconcile_authority_is_checked_before_any_work(self):
        common = ["--auto-reconcile", "--output", "not-inspected", "--ledger", "not-inspected.jsonl", "--budget-usd", "20"]
        for flags in ([], ["--execute"], ["--spending-authorized"]):
            with self.subTest(flags=flags), \
                 patch.object(wrapper, "repo_path", side_effect=AssertionError("filesystem path consulted")), \
                 patch.object(wrapper, "ledger_state", side_effect=AssertionError("ledger inspected")):
                code, run, sleep = self.invoke(common + flags, [])
            self.assertEqual(code, 2)
            self.assertIn("requires --execute and --spending-authorized", self.stderr)
            run.assert_not_called()
            sleep.assert_not_called()

    def test_auto_reconcile_needs_unique_output_ledger_and_finite_positive_cap(self):
        base = ["--auto-reconcile", "--execute", "--spending-authorized"]
        cases = (["--ledger", "l", "--budget-usd", "20"],
                 ["--output", "o", "--budget-usd", "20"],
                 ["--output", "o", "--ledger", "l"],
                 ["--output", "o", "--ledger", "l", "--budget-usd"],
                 ["--output", "o", "--ledger", "l", "--ledger=other", "--budget-usd", "20"])
        cases = [*cases, *(["--output", "o", "--ledger", "l", "--budget-usd", cap]
                            for cap in ("NaN", "Infinity", "-1", "0", "not-money"))]
        for options in cases:
            with self.subTest(options=options):
                code, run, sleep = self.invoke(base + options, [])
            self.assertEqual(code, 2)
            self.assertIn("error:", self.stderr)
            run.assert_not_called()
            sleep.assert_not_called()

    def test_authorized_equals_options_are_forwarded_without_substitution(self):
        args = ["--auto-reconcile", "--execute", "--spending-authorized", "--output=collection",
                "--ledger=original.jsonl", "--budget-usd=20.00"]
        code, run, _ = self.invoke(args, [SimpleNamespace(returncode=0, stdout="done", stderr="")])
        self.assertEqual(code, 0)
        command = run.call_args.args[0]
        self.assertIn("--ledger=original.jsonl", command)
        self.assertIn("--budget-usd=20.00", command)
        self.assertNotIn("--auto-reconcile", command)

    def test_authority_flags_after_positional_separator_are_refused(self):
        args = ["--auto-reconcile", "--output", "o", "--ledger", "l", "--budget-usd", "20",
                "--", "--execute", "--spending-authorized"]
        code, run, sleep = self.invoke(args, [])
        self.assertEqual(code, 2)
        run.assert_not_called()
        sleep.assert_not_called()

    def test_cli_argument_error_cannot_trigger_reconciliation_from_its_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, _, _ = self.auto_args(temporary)
            with patch.object(wrapper, "ledger_state", side_effect=AssertionError("ledger inspected")):
                code, run, sleep = self.invoke(args, [SimpleNamespace(returncode=2, stdout="",
                    stderr="unrecognized argument: budget ledger is blocked")])
            self.assertEqual((code, run.call_count), (2, 1))
            sleep.assert_not_called()

    def test_wrong_ledger_or_history_failure_never_invokes_reconciliation(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, _, ledger = self.auto_args(temporary)
            before = ledger.read_bytes()
            with patch.object(wrapper, "ledger_state", side_effect=AssertionError("unrelated ledger inspected")):
                code, run, sleep = self.invoke(args, [SimpleNamespace(returncode=1, stdout="",
                    stderr="error: resume requires the original ledger identity and fixed cap")])
            self.assertEqual(code, 1)
            self.assertEqual(run.call_count, 1)
            sleep.assert_not_called()
            self.assertEqual(ledger.read_bytes(), before)

    def test_auto_reconcile_stops_when_receipt_helper_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, _, ledger = self.auto_args(temporary)
            before = ledger.read_bytes()
            def response(command, **kwargs):
                if "live" in command:
                    return SimpleNamespace(returncode=1, stdout="", stderr="provider request failed; consult the sanitized receipt")
                if "ledger" in command:
                    self.assertNotEqual(command[command.index("--ledger") + 1], str(ledger))
                    return SimpleNamespace(returncode=0, stdout=json.dumps({"budget": {
                        "blocked": True, "block_reasons": ["unknown_charge"], "unknown_count": 1}}), stderr="")
                self.assertTrue(command[1].endswith("reconcile_unknowns.py"))
                self.assertEqual(command[2:4], [str(ledger), "20"])
                return SimpleNamespace(returncode=1, stdout="", stderr="no audited priced receipt")
            code, run, sleep = self.invoke(args, response)
            self.assertEqual(code, 1)
            self.assertEqual(run.call_count, 3)
            self.assertIn("could not unblock", self.stdout)
            sleep.assert_not_called()
            self.assertEqual(ledger.read_bytes(), before)

    def test_successful_receipt_recovery_preserves_original_flags_and_ceiling(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, _, ledger = self.auto_args(temporary)
            commands, live_calls, inspections = [], 0, 0
            def response(command, **kwargs):
                nonlocal live_calls, inspections
                commands.append(command)
                if "live" in command:
                    live_calls += 1
                    return SimpleNamespace(returncode=0 if live_calls == 2 else 1, stdout="",
                                           stderr="" if live_calls == 2 else "budget ledger is blocked (unknown_charge)")
                if "ledger" in command:
                    inspections += 1
                    return SimpleNamespace(returncode=0, stdout=json.dumps({"budget": {
                        "blocked": inspections == 1,
                        "block_reasons": ["unknown_charge"] if inspections == 1 else [], "unknown_count": 1}}), stderr="")
                return SimpleNamespace(returncode=0, stdout="audited priced receipt recorded", stderr="")
            code, run, sleep = self.invoke(args, response)
            self.assertEqual((code, run.call_count, live_calls, inspections), (0, 5, 2, 2))
            self.assertEqual(sleep.call_args.args, (30,))
            for command in (command for command in commands if "live" in command):
                self.assertEqual(command[command.index("--ledger") + 1], str(ledger))
                self.assertEqual(command[command.index("--budget-usd") + 1], "20")
                self.assertIn("--execute", command)
                self.assertIn("--spending-authorized", command)

    def test_budget_overrun_and_unblocked_error_do_not_enable_retries(self):
        for state in ({"blocked": True, "block_reasons": ["reservation_exceeded"]},
                      {"blocked": False, "block_reasons": []}):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as temporary:
                args, _, _ = self.auto_args(temporary)
                responses = [SimpleNamespace(returncode=1, stdout="", stderr="budget does not permit this request"),
                             SimpleNamespace(returncode=0, stdout=json.dumps({"budget": state}), stderr="")]
                code, run, sleep = self.invoke(args, responses)
                self.assertEqual((code, run.call_count), (1, 2))
                sleep.assert_not_called()

    def test_inspection_of_missing_or_torn_ledger_never_creates_or_repairs_it(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(wrapper.subprocess, "run") as run:
            path = Path(temporary) / "absent.jsonl"
            self.assertEqual(wrapper.ledger_state({}, str(path), "20")["block_reasons"], ["ledger_missing"])
            self.assertFalse(path.exists())
            path.write_bytes(b'{"type":"header"')
            before = path.read_bytes()
            self.assertEqual(wrapper.ledger_state({}, str(path), "20")["block_reasons"], ["ledger_incomplete"])
            self.assertEqual(path.read_bytes(), before)
            run.assert_not_called()

    def test_status_inspection_mutates_only_temporary_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, _, ledger = self.auto_args(temporary)
            before = ledger.read_bytes()
            def response(command, **kwargs):
                snapshot = Path(command[command.index("--ledger") + 1])
                self.assertNotEqual(snapshot, ledger)
                self.assertEqual(snapshot.read_bytes(), before)
                snapshot.write_bytes(before + b'{"type":"synthetic-interrupt"}\n')
                return SimpleNamespace(returncode=0, stdout=json.dumps({"budget": {
                    "blocked": True, "block_reasons": ["interrupted_request"]}}), stderr="")
            with patch.object(wrapper.subprocess, "run", side_effect=response):
                state = wrapper.ledger_state({}, str(ledger), "20")
            self.assertTrue(state["blocked"])
            self.assertEqual(ledger.read_bytes(), before)

    def test_status_rejects_source_change_during_inspection(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, _, ledger = self.auto_args(temporary)
            def response(command, **kwargs):
                ledger.write_bytes(ledger.read_bytes() + b'{"type":"synthetic-change"}\n')
                return SimpleNamespace(returncode=0, stdout=json.dumps({"budget": {"blocked": False}}), stderr="")
            with patch.object(wrapper.subprocess, "run", side_effect=response):
                state = wrapper.ledger_state({}, str(ledger), "20")
            self.assertEqual(state["block_reasons"], ["ledger_changed_during_inspection"])

    def simulate_args(self, temporary, *extra):
        output, ledger = Path(temporary) / "shard", Path(temporary) / "shard.jsonl"
        return ["--simulate", "--output", str(output), "--ledger", str(ledger), "--budget-usd", "10",
                *extra, "--execute", "--spending-authorized"], output

    def test_simulate_mode_runs_simulate_and_resumes_an_incomplete_town(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, output = self.simulate_args(temporary, "--regenerate-failed")
            def response(command, **kwargs):
                self.assertEqual(command[1:4], ["-m", "truth_discount.cli", "simulate"])
                self.assertIn("--regenerate-failed", command)
                self.assertNotIn("--simulate", command)
                if not output.exists():
                    output.mkdir()
                    (output / "execution_plan.json").write_text("{}")
                    self.assertNotIn("--resume", command)
                    return SimpleNamespace(returncode=1, stdout="",
                                           stderr="error: " + wrapper.INCOMPLETE + ": town-1")
                self.assertIn("--resume", command)
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            with patch.object(wrapper, "ledger_state", return_value={"blocked": False}) as state:
                code, run, sleep = self.invoke(args, response)
            self.assertEqual((code, run.call_count), (0, 2))
            self.assertEqual(sleep.call_args.args, (30,))
            state.assert_called_once()

    def test_simulate_incomplete_town_with_unclear_charge_needs_auto_reconcile(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, _ = self.simulate_args(temporary, "--regenerate-failed")
            blocked = {"blocked": True, "block_reasons": ["unknown_charge"], "unknown_count": 1}
            with patch.object(wrapper, "ledger_state", return_value=blocked):
                code, run, sleep = self.invoke(args, [SimpleNamespace(
                    returncode=1, stdout="", stderr="error: " + wrapper.INCOMPLETE + ": town-1")])
            self.assertEqual((code, run.call_count), (1, 1))
            sleep.assert_not_called()

    def test_live_mode_does_not_treat_incomplete_simulation_text_as_retryable(self):
        code, run, sleep = self.invoke([], [SimpleNamespace(returncode=1, stdout="", stderr=wrapper.INCOMPLETE)])
        self.assertEqual((code, run.call_count), (1, 1))
        self.assertIn("live", run.call_args.args[0])
        sleep.assert_not_called()

    def test_simulate_without_regenerate_flag_warns_before_running(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, _ = self.simulate_args(temporary)
            code, run, _ = self.invoke(args, [SimpleNamespace(returncode=0, stdout="", stderr="")])
            self.assertEqual(code, 0)
            self.assertIn("without --regenerate-failed", self.stdout)
            self.assertNotIn("--regenerate-failed", run.call_args.args[0])

    def test_probe_mode_drives_probe_simulate_and_resumes_an_incomplete_town(self):
        with tempfile.TemporaryDirectory() as temporary:
            args, output = self.simulate_args(temporary, "--regenerate-failed", "--probe", "probe_1")
            args = ["--probe-simulate" if a == "--simulate" else a for a in args]
            def response(command, **kwargs):
                self.assertEqual(command[1:4], ["-m", "truth_discount.cli", "probe-simulate"])
                self.assertNotIn("--probe-simulate", command)
                self.assertEqual(command[command.index("--probe") + 1], "probe_1")
                if not output.exists():
                    output.mkdir()
                    (output / "execution_plan.json").write_text("{}")
                    return SimpleNamespace(returncode=1, stdout="",
                                           stderr="error: " + wrapper.PROBE_INCOMPLETE + ": town-1")
                self.assertIn("--resume", command)
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            with patch.object(wrapper, "ledger_state", return_value={"blocked": False}):
                code, run, sleep = self.invoke(args, response)
            self.assertEqual((code, run.call_count), (0, 2))
            self.assertEqual(sleep.call_args.args, (30,))

    def test_probe_and_main_simulate_modes_are_exclusive(self):
        code, run, _ = self.invoke(["--simulate", "--probe-simulate"], [])
        self.assertEqual((code, run.call_count), (2, 0))


if __name__ == "__main__":
    unittest.main()
