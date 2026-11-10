"""Public staged-workflow commands, with every native request mocked."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
import io
import csv
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_deferred_judging import profile, HTTP, inventory
from truth_discount.budget import BudgetLedger
from truth_discount.cli import main
from truth_discount.config import load_config
from truth_discount.deferred_judging import judge_collection
from truth_discount.deferred_judging import plan_judging, load_judge_profile
from truth_discount.contracts import digest
from truth_discount.judge_selection import panel_profile
from truth_discount.providers import ProviderBackend

ROOT = Path(__file__).resolve().parents[1]


class DeferredCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        code, result, error = self.invoke("simulation-demo", "--output", self.source)
        self.assertEqual(code, 0, error)
        self.assertEqual((result["towns"], result["phone_transcripts"], result["judge_calls"]), (4, 48, 0))

    def invoke(self, *args):
        out, error = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(error):
            code = main(list(map(str, args)))
        text = out.getvalue()
        return code, json.loads(text) if text else None, error.getvalue()

    def test_all_candidate_templates_preview_without_credentials_or_spending(self):
        original = inventory(self.source)
        for path in sorted((ROOT / "configs/judges").glob("*.example.json")):
            with self.subTest(profile=path.name), patch.dict(os.environ, {}, clear=True), \
                 patch("truth_discount.providers.ProviderBackend.validate_credentials",
                       side_effect=AssertionError("read credentials")), \
                 patch("truth_discount.budget.BudgetLedger", side_effect=AssertionError("opened ledger")):
                code, report, error = self.invoke("judge-saved", self.source, "--profile", path,
                                                  "--output", self.root / "judgments")
                self.assertEqual(code, 0, error)
                self.assertEqual((report["phone_outcomes"], report["provider_api_calls"]), (48, 0))
                self.assertEqual(report["status"], "blocked")
                self.assertFalse(report["spending_authorized_by_planning"])
        self.assertEqual(inventory(self.source), original)
        self.assertFalse((self.root / "judgments").exists())

    def test_judging_execution_without_hold_release_does_not_open_ledger(self):
        with patch("truth_discount.budget.BudgetLedger", side_effect=AssertionError("opened ledger")):
            code, _, error = self.invoke("judge-saved", self.source, "--profile",
                ROOT / "configs/judges/haiku.example.json", "--output", self.root/"judgments", "--execute")
        self.assertEqual(code, 1)
        self.assertIn("spending hold", error)
        self.assertFalse((self.root/"judgments").exists())

    def test_multi_profile_cli_replay_and_comparison_use_saved_outputs_only(self):
        config = load_config(ROOT / "configs/pilot_config.json")
        originals = inventory(self.source)
        profiles = []
        for name in ("first", "second"):
            current = profile(config, "Anthropic" if name == "first" else "OpenAI", name=name)
            file = self.root / (name+".json")
            file.write_text(json.dumps(current))
            profiles.append(file)
            with patch.dict(os.environ, {"DEFERRED_TEST_KEY": "FAKE_NOT_REAL"}), \
                 BudgetLedger(self.root/(name+"-ledger.jsonl"), "1") as ledger:
                backend = ProviderBackend(current["provider_manifest"], ledger, transport=HTTP(),
                                          evidence_kind="mocked_provider")
                asyncio.run(judge_collection(self.source, self.root/"judgments", current, backend,
                              execution_authorized=True, spending_authorized=True))
            code, report, error = self.invoke("judge-status", self.source, "--profile", file,
                                               "--output", self.root/"judgments")
            self.assertEqual(code, 0, error)
            self.assertEqual(report["phone_outcomes"], 48)
        code, comparison, error = self.invoke("compare-judges", self.source,
            "--profile", profiles[0], "--judge-output", self.root/"judgments",
            "--profile", profiles[1], "--judge-output", self.root/"judgments")
        self.assertEqual(code, 0, error)
        self.assertFalse(comparison["semantic_accuracy_established"])
        self.assertEqual(inventory(self.source), originals)

    def panel(self):
        current = profile(load_config(ROOT / "configs/pilot_config.json"))
        items = plan_judging(self.source, current)["items"][:2]
        rows = [{"validation_id": digest({"run_id": item["run_id"], "seat_id": item["seat_id_private"],
                                          "target_artist": item["target_artist"], "phone": item["phone_transcript"]}),
                 "target_artist": item["target_artist"],
                 "transcript": "\n".join(f"{line['speaker']}: {line['text']}" for line in item["phone_transcript"]),
                 "human_label": "", "notes": ""} for item in items]
        path = self.root / "human.csv"
        return current, rows, path

    def write_panel(self, rows, path):
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_exact_human_panel_mapping_ignores_labels_and_stays_unapproved(self):
        current, rows, path = self.panel()
        self.write_panel(rows, path)
        prepared, receipt = panel_profile(self.source, current, path, "panel-a")
        self.assertEqual(receipt["selected_phone_outcomes"], 2)
        self.assertFalse(prepared["approved"])
        self.assertFalse(prepared["selection"]["approved"])
        self.assertFalse(prepared["provider_manifest"]["approved"])
        for row in rows:
            row["human_label"] = "CHECKED_FALSE"
            row["notes"] = "Edited label must not change which cases are chosen."
        self.write_panel(rows, path)
        self.assertEqual(panel_profile(self.source, current, path, "panel-a")[0], prepared)

    def test_human_panel_duplicate_or_changed_transcript_is_rejected(self):
        current, rows, path = self.panel()
        self.write_panel([rows[0], rows[0]], path)
        with self.assertRaisesRegex(ValueError, "duplicate or foreign"):
            panel_profile(self.source, current, path, "panel-a")
        rows[0]["transcript"] += "Changed question"
        self.write_panel(rows, path)
        with self.assertRaisesRegex(ValueError, "transcript differs"):
            panel_profile(self.source, current, path, "panel-a")


if __name__ == "__main__":
    unittest.main()
