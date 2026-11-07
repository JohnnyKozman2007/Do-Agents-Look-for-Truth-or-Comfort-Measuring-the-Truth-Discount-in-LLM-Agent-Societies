"""Re-judging malformed labels: fixture towns, mocked judge HTTP, no network."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_live_cli import approved_test_manifest
from truth_discount.artifacts import audit_town
from truth_discount.budget import BudgetLedger
from truth_discount.cli import main
from truth_discount.config import build_manifest, load_config
from truth_discount.contracts import GenerationResponse
from truth_discount.fixtures import FixtureBackend
from truth_discount.providers import ProviderBackend
from truth_discount.rejudge import REJUDGE_FILE, malformed_items, rejudge, summary
from truth_discount.runner import run_town

ROOT = Path(__file__).resolve().parents[1]
MARKER = "\nPHONE CALL TRANSCRIPT:\n"


class BadQuotes(FixtureBackend):
    """Seats 2 and 3 get a judge reply quoting words nobody said, as the live judge sometimes does."""

    async def generate(self, request):
        if request.kind == "judge" and request.seat in (2, 3):
            return GenerationResponse('{"label": "FACT", "quote": "words nobody said"}')
        return await super().generate(request)


class Judge:
    """Anthropic-shaped replies; `good` quotes the listener's last line."""

    def __init__(self, good=True, fail=False):
        self.good, self.fail, self.requests = good, fail, []

    def __call__(self, method, url, headers, body, timeout_seconds):
        self.requests.append(body)
        if self.fail:
            raise ConnectionResetError("dropped after sending")
        lines = json.loads(body["messages"][0]["content"].split(MARKER, 1)[1])
        listener = [line["text"] for line in lines if line["speaker"] == "listener"]
        quote = listener[-1] if self.good else "still not their words"
        text = json.dumps({"label": "UNCERTAIN", "quote": quote})
        return {"id": f"msg_{len(self.requests)}", "model": body["model"], "stop_reason": "end_turn",
                "content": [{"type": "text", "text": text}],
                "usage": {"input_tokens": 900, "output_tokens": 50, "cache_read_input_tokens": 0,
                          "cache_creation_input_tokens": 0, "output_tokens_details": {"thinking_tokens": 0}}}


class RejudgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/pilot_config.json")
        self.providers = approved_test_manifest(self.config)
        self.judge_key = self.config["models"]["judge_models"][0]["key"]
        self.towns = self.root / "towns"
        runs = [r for r in build_manifest(self.config) if r["cell_id"] == 1 and r["seed_id"] == 0]
        async def collect():
            for run in runs:
                await run_town(self.config, run, BadQuotes(), self.towns)
        asyncio.run(collect())

    def run_rejudge(self, http, attempts=3):
        env = patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"})
        with env, BudgetLedger(self.root / "ledger.jsonl", "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            try:
                return asyncio.run(rejudge(self.towns, backend, self.judge_key, attempts=attempts))
            finally:
                self.budget = ledger.summary()

    def test_malformed_labels_are_rejudged_and_pairs_recovered(self):
        before = summary(self.towns)
        self.assertEqual(before["malformed_labels"], 8)          # 2 seats x 4 towns
        self.assertEqual(before["complete_pairs_before"], 0)
        saved = {p: p.read_bytes() for p in self.towns.glob("*/*")}
        http = Judge()
        result = self.run_rejudge(http)
        self.assertEqual((result["fixed"], result["still_malformed"]), (8, 0))
        self.assertEqual(result["complete_pairs_after"], result["pairs"])
        self.assertEqual(len(http.requests), 8)
        self.assertGreater(self.budget["settled_usd"], 0)
        self.assertFalse(self.budget["blocked"])
        # Saved towns are untouched and still replay.
        self.assertEqual({p: p.read_bytes() for p in self.towns.glob("*/*")}, saved)
        for directory in {p.parent for p in saved}:
            audit_town(directory)
        rows = [json.loads(x) for x in (self.towns / REJUDGE_FILE).read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(r["final"]["status"] == "valid" and len(r["attempts"]) == 1 for r in rows))
        self.assertTrue(all(r["attempts"][0]["receipt"]["cost_status"] == "calculated_from_usage" for r in rows))
        # Rerunning skips everything already re-judged.
        again = Judge()
        self.assertEqual(self.run_rejudge(again)["attempted_now"], 0)
        self.assertEqual(again.requests, [])

    def test_a_judge_that_stays_wrong_is_tried_then_left_malformed(self):
        http = Judge(good=False)
        result = self.run_rejudge(http, attempts=2)
        self.assertEqual((result["fixed"], result["still_malformed"]), (0, 8))
        self.assertEqual(len(http.requests), 16)
        self.assertEqual(result["complete_pairs_after"], 0)
        self.assertEqual(self.run_rejudge(Judge())["attempted_now"], 0)   # not paid for again

    def test_unclear_charge_stops_and_keeps_nothing_half_done(self):
        with self.assertRaisesRegex(ValueError, "re-judge call"):
            self.run_rejudge(Judge(fail=True))
        self.assertTrue(self.budget["blocked"])
        self.assertFalse((self.towns / REJUDGE_FILE).exists())
        self.assertEqual(len(malformed_items(self.towns)), 8)

    def test_preview_reads_no_keys_and_spends_nothing(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), \
             patch("truth_discount.providers.ProviderBackend", side_effect=AssertionError("backend built")):
            code = main(["rejudge", str(self.towns)])
        self.assertEqual(code, 0, err.getvalue())
        preview = json.loads(out.getvalue())
        self.assertEqual((preview["status"], preview["malformed_labels"], preview["provider_api_calls"]),
                         ("preview", 8, 0))
        self.assertFalse((self.root / "ledger.jsonl").exists())
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            self.assertEqual(main(["rejudge", str(self.towns), "--execute"]), 1)
        self.assertIn("spending-authorized", err.getvalue())


if __name__ == "__main__":
    unittest.main()
