"""Regression coverage for the historical bake-off's offline entry point."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_bakeoff.py"


class BakeoffSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.script = self.root / "scripts" / SCRIPT.name
        self.script.parent.mkdir()
        shutil.copyfile(SCRIPT, self.script)
        self.outputs = self.root / "outputs"
        self.outputs.mkdir()
        self.report = self.outputs / "BAKE_OFF_REPORT.md"
        self.predictions = self.outputs / "bakeoff_predictions.json"

    def invoke(self, *args):
        return subprocess.run([sys.executable, "-I", str(self.script), *args],
                              capture_output=True, text=True, check=False)

    def saved_inputs(self):
        (self.outputs / "calibration_sample_100.json").write_text(
            json.dumps([{"id": "call-1"}, {"id": "call-2"}]), encoding="utf-8")
        (self.outputs / "human_labels_100.csv").write_text(
            "item_id,human_label\ncall-1,FACT\ncall-2,UNCERTAIN\n", encoding="utf-8")
        rows = [
            {"item_id": "call-1", "status": "valid", "label": "FACT"},
            {"item_id": "call-2", "status": "error", "label": "ERROR", "raw": "private provider error"},
        ]
        self.predictions.write_text(
            json.dumps({"evaluations": {"Gemini": rows, "Other": rows}, "costs": {"Gemini": 0.0239, "Other": 0}}),
            encoding="utf-8")
        return rows

    def test_cache_miss_refuses_even_with_local_provider_keys(self):
        self.saved_inputs()
        self.predictions.unlink()
        (self.root / ".env").write_text("DEEPINFRA_API_KEY=synthetic-key\n", encoding="utf-8")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing outputs/bakeoff_predictions.json", result.stderr)
        self.assertFalse(self.report.exists())
        self.assertFalse((self.outputs / "ledgers").exists())

    def test_live_flag_refuses_without_replacing_existing_report(self):
        self.saved_inputs()
        self.report.write_text("existing", encoding="utf-8")
        result = self.invoke("--no-cache")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only replays saved predictions", result.stderr)
        self.assertEqual(self.report.read_text(encoding="utf-8"), "existing")

    def test_replays_saved_metrics_without_credentials_or_zero_cost_claim(self):
        self.saved_inputs()
        cached_bytes = self.predictions.read_bytes()
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report.read_text(encoding="utf-8")
        self.assertIn("1/2 | 50.0% | 50.0% (1/2) | 0.333", report)
        self.assertIn("$0.0239 (unverified recorded subtotal)", report)
        self.assertIn("| **Other** | 1/2 | 50.0% | 50.0% (1/2) | 0.333 | Unavailable |", report)
        self.assertNotIn("private provider error", report + result.stdout + result.stderr)
        self.assertEqual(self.predictions.read_bytes(), cached_bytes)
        self.assertFalse((self.outputs / "ledgers").exists())

    def test_incomplete_predictions_preserve_existing_report(self):
        rows = self.saved_inputs()
        self.report.write_text("existing", encoding="utf-8")
        self.predictions.write_text(json.dumps({"evaluations": {"Gemini": rows[:1]}}), encoding="utf-8")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.report.read_text(encoding="utf-8"), "existing")

    def test_duplicate_labels_preserve_existing_report(self):
        self.saved_inputs()
        self.report.write_text("existing", encoding="utf-8")
        (self.outputs / "human_labels_100.csv").write_text(
            "item_id,human_label\ncall-1,\ncall-1,FACT\n", encoding="utf-8")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.report.read_text(encoding="utf-8"), "existing")

    def test_undefined_kappa_is_unavailable(self):
        rows = self.saved_inputs()
        rows[1].update(status="valid", label="FACT")
        self.predictions.write_text(json.dumps({"evaluations": {"Gemini": rows}}), encoding="utf-8")
        human_labels = self.outputs / "human_labels_100.csv"
        human_labels.write_text("item_id,human_label\ncall-1,FACT\ncall-2,FACT\n", encoding="utf-8")
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("100.0% (2/2) | Unavailable |", self.report.read_text(encoding="utf-8"))
        human_labels.unlink()
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2/2 | 0.0% | Unavailable | Unavailable |", self.report.read_text(encoding="utf-8"))
