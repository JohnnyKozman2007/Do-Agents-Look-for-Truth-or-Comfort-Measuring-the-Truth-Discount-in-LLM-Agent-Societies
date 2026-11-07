"""CLI integration checks use only temporary synthetic output bundles."""

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.cli import main


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "pilot_config.json"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def invoke(self, *arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main([str(arg) for arg in arguments])
        return status, stdout.getvalue(), stderr.getvalue()

    def successful(self, *arguments):
        status, stdout, stderr = self.invoke(*arguments)
        self.assertEqual(status, 0, stderr)
        self.assertEqual(stderr, "")
        return json.loads(stdout)

    def test_validate_accepts_explicit_config_before_or_after_subcommand(self):
        for arguments in (("--config", CONFIG_PATH, "validate"),
                          ("validate", "--config", CONFIG_PATH)):
            with self.subTest(arguments=arguments):
                result = self.successful(*arguments)
                self.assertEqual(result["status"], "valid")
                self.assertEqual(result["planned_towns"], 624)
                self.assertEqual(result["planned_pairs"], 312)
                self.assertEqual(result["provider_api_calls"], 0)
                self.assertFalse(result["study_results_generated"])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_module_entry_works_from_outside_checkout(self):
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT / "src")
        result = subprocess.run([sys.executable, "-m", "truth_discount.cli", "validate"],
                                cwd=self.root, env=environment, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["planned_towns"], 624)

    def test_manifest_writes_complete_plan_and_refuses_overwrite(self):
        path = self.root / "plan.jsonl"
        result = self.successful("manifest", "--output", path, "--config", CONFIG_PATH)
        self.assertTrue(result["planned_only"])
        content = path.read_bytes()
        rows = [json.loads(line) for line in content.splitlines()]
        self.assertEqual(len(rows), 624)
        self.assertEqual(len({row["run_id"] for row in rows}), 624)
        self.assertEqual(len({row["pair_id"] for row in rows}), 312)
        for pair_id in {row["pair_id"] for row in rows}:
            self.assertEqual({row["condition_type"] for row in rows if row["pair_id"] == pair_id},
                             {"rumor", "truth_twin"})
        status, stdout, stderr = self.invoke("manifest", "--output", path)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("File exists", stderr)
        self.assertEqual(path.read_bytes(), content)

    def test_default_demo_saves_four_nonstudy_towns_without_network(self):
        output = self.root / "demo"
        with patch("socket.create_connection", side_effect=AssertionError("network access forbidden")), \
                patch("urllib.request.urlopen", side_effect=AssertionError("network access forbidden")):
            result = self.successful("demo", "--output", output)
        self.assertEqual(result["towns"], 4)
        self.assertEqual(result["completed_towns"], 4)
        self.assertEqual(result["pairs"], 2)
        self.assertEqual(result["provider_api_calls"], 0)
        self.assertEqual(result["evidence_kind"], "synthetic_fixture")
        self.assertFalse(result["study_results_generated"])
        towns = [json.loads(path.read_text(encoding="utf-8")) for path in output.glob("*/town.json")]
        self.assertEqual(len(towns), 4)
        self.assertEqual({(t["cell_id"], t["layout_id"], t["repetition_id"]) for t in towns}, {(1, 0, 0)})
        self.assertEqual(len({town["model_key"] for town in towns}), 2)
        for town in towns:
            self.assertFalse(town["study_eligible"])
            self.assertEqual(town["evidence_kind"], "synthetic_fixture")
            self.assertEqual(town["token_usage"]["provider_api_calls"], 0)
            self.assertIsNone(town["token_usage"]["cost_usd"])
            for call in town["calls"]:
                self.assertEqual(call["backend"], "synthetic_fixture")
                self.assertIsNone(call["actual_provider"])
                self.assertIsNone(call["actual_model"])
        replay = self.successful("summarize", output)
        for key in ("towns", "pairs", "completed_towns", "provider_api_calls", "paired_fixture_metrics"):
            self.assertEqual(replay[key], result[key])

    def test_all_skip_mode_never_spends_fixture_budgets(self):
        output = self.root / "skips"
        result = self.successful("demo", "--output", output, "--mode", "all_skip")
        self.assertEqual(result["fixture_mode"], "all_skip")
        for path in output.glob("*/town.json"):
            town = json.loads(path.read_text(encoding="utf-8"))
            decisions = town["scene_2_first_hand_decisions"] + town["scene_4_second_hand_decisions"]
            self.assertEqual(len(decisions), 12)
            self.assertTrue(all(row["decision"] == "SKIP" for row in decisions))
            self.assertEqual(set(town["final_budgets_usd"].values()), {40})

    def test_silent_mode_uses_omission_rule_and_has_no_judge_callbacks(self):
        output = self.root / "silent"
        result = self.successful("demo", "--output", output, "--mode", "silent")
        self.assertEqual(result["towns"], 4)
        self.assertEqual(result["judged_phone_inputs"], 0)
        for path in output.glob("*/town.json"):
            town = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(town["judge_evaluations"]), 12)
            self.assertEqual({row["label"] for row in town["judge_evaluations"]}, {"NOT_MENTIONED"})
            self.assertFalse(any(call["kind"] == "judge" for call in town["calls"]))

    def test_demo_refuses_existing_root_before_any_fixture_callback(self):
        for populated in (False, True):
            with self.subTest(populated=populated):
                output = self.root / ("populated" if populated else "empty")
                output.mkdir()
                if populated:
                    (output / "sentinel.txt").write_text("keep this")
                before = {p.name: p.read_bytes() for p in output.iterdir()}
                with patch("truth_discount.cli.FixtureBackend", side_effect=AssertionError("must refuse before backend")):
                    status, stdout, stderr = self.invoke("demo", "--output", output)
                self.assertEqual(status, 1)
                self.assertEqual(stdout, "")
                self.assertIn("refusing existing output directory", stderr)
                self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, before)

    def test_invalid_config_fails_before_creating_any_output(self):
        path = self.root / "invalid.json"
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config["meta"]["version"] = "unsupported"
        path.write_text(json.dumps(config))
        output = self.root / "not-created"
        status, stdout, stderr = self.invoke("demo", "--config", path, "--output", output)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("supported version", stderr)
        self.assertFalse(output.exists())

    def test_live_provider_and_unsupported_modes_are_not_cli_options(self):
        for extra in (("--live",), ("--provider", "anything"), ("--mode", "live")):
            with self.subTest(extra=extra), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main(["demo", "--output", str(self.root / "forbidden"), *extra])
                self.assertEqual(raised.exception.code, 2)
        self.assertFalse((self.root / "forbidden").exists())

    def test_summarize_rejects_missing_and_corrupted_bundles(self):
        status, stdout, stderr = self.invoke("summarize", self.root)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("no saved towns", stderr)
        output = self.root / "demo"
        self.successful("demo", "--output", output)
        path = next(output.glob("*/town.json"))
        original = hashlib.sha256(path.read_bytes()).hexdigest()
        path.write_text("{}")
        status, stdout, stderr = self.invoke("summarize", output)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("file hash mismatch", stderr)
        self.assertNotEqual(hashlib.sha256(path.read_bytes()).hexdigest(), original)


if __name__ == "__main__":
    unittest.main()
