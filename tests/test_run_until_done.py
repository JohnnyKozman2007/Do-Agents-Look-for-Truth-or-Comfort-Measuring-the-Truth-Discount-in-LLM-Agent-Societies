"""Recovery wrapper checks use a fake subprocess and never call a provider."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
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
        with patch.object(sys, "argv", ["run_until_done.py", *args]), \
             patch.dict(os.environ, {}, clear=True), \
             patch.object(wrapper.subprocess, "run", side_effect=response) as run, \
             patch.object(wrapper.time, "sleep") as sleep, \
             patch.object(wrapper, "MAX_ROUNDS", rounds), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            result = wrapper.main()
        return result, run, sleep

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


if __name__ == "__main__":
    unittest.main()
