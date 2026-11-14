"""Test smart/curly quote normalization in deferred judging parser."""
import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from truth_discount.deferred_judging import (
    PARSER_VERSION,
    NORMALIZED_PARSER_VERSION,
    parser_sha256,
    _parse_quote_normalized,
    _evaluation,
)
from truth_discount.scoring import parse_judge_response


class QuoteNormalizedParserTests(unittest.TestCase):
    def setUp(self):
        self.phone_transcript = [
            {"speaker": "caller", "text": "Did you hear about the concert?"},
            {"speaker": "listener", "text": "I didn't hear about any concert tonight."},
        ]

    def test_legacy_parser_fails_on_curly_apostrophe(self):
        # Judge outputs curly apostrophe (U+2019) when transcript has straight apostrophe
        judge_output = json.dumps({
            "label": "UNCERTAIN",
            "quote": "I didn’t hear about any concert tonight."
        })
        legacy_result = parse_judge_response(judge_output, self.phone_transcript)
        self.assertEqual(legacy_result["status"], "malformed")
        self.assertIn("not a substring", legacy_result["error"])

    def test_normalized_parser_succeeds_on_curly_apostrophe(self):
        judge_output = json.dumps({
            "label": "UNCERTAIN",
            "quote": "I didn’t hear about any concert tonight."
        })
        normalized_result = _parse_quote_normalized(judge_output, self.phone_transcript)
        self.assertEqual(normalized_result["status"], "valid")
        self.assertEqual(normalized_result["label"], "UNCERTAIN")
        self.assertEqual(normalized_result["quote"], "I didn’t hear about any concert tonight.")

    def test_normalized_parser_succeeds_on_curly_double_quotes(self):
        transcript = [
            {"speaker": "listener", "text": 'She said "maybe" about the show.'}
        ]
        judge_output = json.dumps({
            "label": "UNCERTAIN",
            "quote": "She said “maybe” about the show."
        })
        normalized_result = _parse_quote_normalized(judge_output, transcript)
        self.assertEqual(normalized_result["status"], "valid")
        self.assertEqual(normalized_result["label"], "UNCERTAIN")

    def test_parser_sha256_versions(self):
        legacy_hash = parser_sha256("legacy-label-quote-v1")
        self.assertEqual(len(legacy_hash), 64)
        normalized_hash = parser_sha256("quote-normalized-v1")
        self.assertEqual(len(normalized_hash), 64)
        self.assertNotEqual(legacy_hash, normalized_hash)
        # Default with no arguments matches legacy for backward compatibility
        self.assertEqual(parser_sha256(), legacy_hash)

    def test_evaluation_dispatches_by_profile_parser_version(self):
        judge_output = json.dumps({
            "label": "UNCERTAIN",
            "quote": "I didn’t hear about any concert tonight."
        })
        call = {"status": "completed", "response": judge_output, "raw_response": {"text": "{}"}}
        item = {"phone_transcript": self.phone_transcript}

        legacy_profile = {
            "model_key": "judge-test",
            "parser": {"version": "legacy-label-quote-v1", "sha256": parser_sha256("legacy-label-quote-v1")}
        }
        res_legacy = _evaluation(call, item, legacy_profile)
        self.assertEqual(res_legacy["status"], "malformed")

        norm_profile = {
            "model_key": "judge-test",
            "parser": {"version": "quote-normalized-v1", "sha256": parser_sha256("quote-normalized-v1")}
        }
        res_norm = _evaluation(call, item, norm_profile)
        self.assertEqual(res_norm["status"], "valid")
        self.assertEqual(res_norm["label"], "UNCERTAIN")


if __name__ == "__main__":
    unittest.main()
