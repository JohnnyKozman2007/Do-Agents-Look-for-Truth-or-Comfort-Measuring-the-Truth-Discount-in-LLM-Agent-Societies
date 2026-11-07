"""Offline checks for the blinded judge and town/pair estimands."""

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from truth_discount.scoring import (  # noqa: E402
    LABELS, make_judge_input, paired_metrics, parse_judge_response, town_metrics,
)


def load_config():
    return json.loads((ROOT / "configs" / "pilot_config.json").read_text())


def evaluations(labels):
    return [{"seat_id": seat, "status": "valid", "label": label, "quote": "quote"}
            for seat, label in enumerate(labels, 1)]


def decisions():
    return [{"seat_id": seat, "layer": "first_hand" if seat <= 6 else "second_hand",
             "decision": "GO" if seat % 2 else "SKIP", "parse_status": "valid"}
            for seat in range(1, 13)]


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.phone = [
            {"speaker": "caller", "text": "The concert is certain!"},
            {"speaker": "listener", "text": "I doubt the concert is happening."},
        ]

    def test_input_projects_only_phone_and_rubric_and_detaches_settings(self):
        self.config["private_condition"] = "PRIVATE_WORLD_SENTINEL"
        self.phone[1]["decision"] = "PRIVATE_ACTION_SENTINEL"
        before = copy.deepcopy(self.config)
        result = make_judge_input(self.config, "Artist {Z}", self.phone)
        text = result["messages"][0]["content"]
        self.assertIn("Artist {Z}", text)
        self.assertNotIn("{announced_artist}", text)
        self.assertIn('{"label": "<LABEL>", "quote":', text)
        self.assertNotIn("PRIVATE_", text)
        self.assertEqual(set(result), {"messages", "settings"})
        self.assertEqual(result["messages"][0]["role"], "user")
        result["settings"]["thinking"]["type"] = "adaptive"
        self.assertEqual(self.config, before)

    def test_all_labels_with_exact_listener_evidence(self):
        for label in LABELS:
            with self.subTest(label=label):
                result = parse_judge_response(json.dumps({
                    "label": label, "quote": "I doubt the concert is happening."
                }), self.phone)
                self.assertEqual(result["status"], "valid")
                self.assertEqual(result["label"], label)

    def test_person_alias_and_exact_unicode_quote(self):
        phone = [{"speaker": "person", "text": "I’m unsure—perhaps Saturday?"}]
        result = parse_judge_response(
            '{"label":"UNCERTAIN","quote":"I’m unsure—perhaps Saturday?"}', phone
        )
        self.assertEqual(result["status"], "valid")

    def test_caller_only_and_approximate_or_cross_turn_quotes_rejected(self):
        phone = self.phone + [{"speaker": "listener", "text": "We will see."}]
        for quote in ("The concert is certain!", "I DOUBT the concert is happening.",
                      "happening. We will see.", "invented evidence"):
            with self.subTest(quote=quote):
                result = parse_judge_response(json.dumps({"label": "FACT", "quote": quote}), phone)
                self.assertEqual(result["status"], "malformed")
                self.assertIsNone(result["label"])

    def test_empty_omission_quote_structural_only(self):
        result = parse_judge_response('{"label":"NOT_MENTIONED","quote":""}', self.phone)
        self.assertEqual(result["status"], "valid")
        for quote in ("", "  ", "\n"):
            self.assertEqual(parse_judge_response(json.dumps({
                "label": "FACT", "quote": quote
            }), self.phone)["status"], "malformed")

    def test_strict_json_rejects_fences_extras_duplicates_and_nonfinite(self):
        good = '{"label":"FACT","quote":"I doubt the concert is happening."}'
        invalid = ["```json\n" + good + "\n```", good + good, "[]", "null", "42",
                   '{"label":"FACT","quote":"x","extra":1}',
                   '{"label":"FACT","label":"SKEPTICAL","quote":"x"}',
                   '{"label":"FACT","quote":NaN}',
                   '{"label":"FACT","quote":null}',
                   '{"label":["FACT"],"quote":"x"}',
                   '{"label":"fact","quote":"x"}',
                   '{"label":"FACT","quote":"x",}', "not json", None]
        for response in invalid:
            with self.subTest(response=response):
                self.assertEqual(parse_judge_response(response, self.phone)["status"], "malformed")


class TownTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_mapping_and_denominators_include_checked_false_and_omissions(self):
        labels = list(LABELS) * 2
        result = town_metrics(self.config, evaluations(labels), decisions())
        self.assertEqual(result["status"], "complete")
        self.assertEqual((result["n_listeners"], result["n_valid"], result["n_mentioned"]), (12, 12, 10))
        self.assertAlmostEqual(result["belief_mean"], 0.5)
        self.assertAlmostEqual(result["omission_rate"], 2 / 12)
        self.assertAlmostEqual(result["sensitivity_lower"], 5 / 12)
        self.assertAlmostEqual(result["sensitivity_neutral"], 6 / 12)
        self.assertEqual(result["go_count"], 6)
        self.assertEqual(result["go_rate_first_hand"], 0.5)
        self.assertEqual(result["go_rate_second_hand"], 0.5)

    def test_all_omitted_is_undefined_conditional_belief_not_zero(self):
        result = town_metrics(self.config, evaluations(["NOT_MENTIONED"] * 12), decisions())
        self.assertEqual(result["status"], "complete")
        self.assertIsNone(result["belief_mean"])
        self.assertEqual(result["omission_rate"], 1)
        self.assertEqual(result["sensitivity_lower"], 0)
        self.assertEqual(result["sensitivity_neutral"], 0.5)

    def test_missing_malformed_unknown_and_duplicate_judges_never_become_omission(self):
        base = evaluations(["FACT"] * 12)
        variants = [base[:-1], copy.deepcopy(base), copy.deepcopy(base), base + [base[0]]]
        variants[1][0].update(status="malformed", label=None)
        variants[2][0]["label"] = "SURPRISE"
        for rows in variants:
            with self.subTest(rows=rows):
                result = town_metrics(self.config, rows, decisions())
                self.assertEqual(result["status"], "incomplete")
                self.assertEqual(result["n_invalid"], 1)
                self.assertEqual(result["n_omitted"], 0)
                for key in ("belief_mean", "omission_rate", "sensitivity_lower", "sensitivity_neutral"):
                    self.assertIsNone(result[key])
                self.assertEqual(result["go_count"], 6)

    def test_empty_judges_and_invalid_seat_types_are_not_zero(self):
        result = town_metrics(self.config, [], [])
        self.assertEqual(result["n_invalid"], 12)
        self.assertIsNone(result["omission_rate"])
        self.assertIsNone(result["go_count"])
        rows = evaluations(["FACT"] * 12)
        rows[0]["seat_id"] = True
        result = town_metrics(self.config, rows, decisions())
        self.assertEqual(result["n_invalid"], 1)
        self.assertEqual(result["n_unexpected_evaluations"], 1)

    def test_unexpected_source_evaluation_cannot_silently_change_denominator(self):
        rows = evaluations(["FACT"] * 12) + [{"seat_id": 0, "status": "valid", "label": "FACT"}]
        result = town_metrics(self.config, rows, decisions())
        self.assertEqual(result["n_valid"], 12)
        self.assertEqual(result["n_unexpected_evaluations"], 1)
        self.assertIsNone(result["belief_mean"])

    def test_bad_decision_only_nulls_affected_layer_and_total(self):
        rows = decisions()
        rows[0].update(parse_status="malformed", decision=None)
        result = town_metrics(self.config, evaluations(["FACT"] * 12), rows)
        self.assertEqual(result["belief_mean"], 1)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["decision_status"], "incomplete")
        self.assertIsNone(result["go_rate_first_hand"])
        self.assertEqual(result["go_rate_second_hand"], 0.5)
        self.assertIsNone(result["go_count"])
        self.assertEqual(result["go_count_valid"], 5)
        self.assertEqual(result["n_invalid_decisions"], 1)

    def test_duplicate_or_wrong_layer_decision_is_unavailable(self):
        variants = [decisions(), decisions()]
        variants[0].append(copy.deepcopy(variants[0][0]))
        variants[1][0]["layer"] = "second_hand"
        for rows in variants:
            result = town_metrics(self.config, evaluations(["FACT"] * 12), rows)
            self.assertIsNone(result["go_rate_first_hand"])
            self.assertIsNone(result["go_count"])

    def test_documented_malformed_fallback_skip_counts_operationally(self):
        rows = decisions()
        rows[0].update(parse_status="malformed_fallback_skip", decision="SKIP")
        result = town_metrics(self.config, evaluations(["FACT"] * 12), rows)
        self.assertEqual(result["decision_status"], "complete")
        self.assertEqual(result["n_valid_decisions"], 11)
        self.assertEqual(result["n_decision_fallbacks"], 1)
        self.assertEqual(result["n_operational_decisions"], 12)
        self.assertEqual(result["n_invalid_decisions"], 0)
        self.assertAlmostEqual(result["go_rate_first_hand"], 2 / 6)
        self.assertEqual(result["go_rate_second_hand"], 0.5)
        self.assertEqual(result["go_count"], 5)

    def test_timeout_error_or_fallback_go_is_not_an_operational_skip(self):
        for status, decision in (("timeout", "SKIP"), ("api_error", "SKIP"),
                                 ("callback_error", "SKIP"),
                                 ("malformed_fallback_skip", "GO")):
            with self.subTest(status=status, decision=decision):
                rows = decisions()
                rows[0].update(parse_status=status, decision=decision)
                result = town_metrics(self.config, evaluations(["FACT"] * 12), rows)
                self.assertEqual(result["decision_status"], "incomplete")
                self.assertEqual(result["n_decision_fallbacks"], 0)
                self.assertEqual(result["n_invalid_decisions"], 1)
                self.assertIsNone(result["go_rate_first_hand"])
                self.assertIsNone(result["go_count"])

    def test_decision_fallback_does_not_rescue_invalid_judgment(self):
        rows = decisions()
        rows[0].update(parse_status="malformed_fallback_skip", decision="SKIP")
        judges = evaluations(["FACT"] * 12)
        judges[0].update(status="malformed", label=None)
        result = town_metrics(self.config, judges, rows)
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["belief_mean"])
        self.assertIsNone(result["omission_rate"])
        self.assertEqual(result["decision_status"], "complete")
        self.assertEqual(result["n_decision_fallbacks"], 1)


class PairTests(unittest.TestCase):
    def town(self, condition, label="FACT", model="m1", pair="p1"):
        return {
            "run_id": f"{model}-{pair}-{condition}", "pair_id": pair,
            "model_key": model, "condition_type": condition,
            "metrics": town_metrics(load_config(), evaluations([label] * 12), decisions()),
        }

    def test_pair_truth_minus_rumor_with_model_isolation(self):
        rows = [self.town("rumor", "SKEPTICAL"), self.town("truth_twin"),
                self.town("truth_twin", "UNCERTAIN", model="m2"),
                self.town("rumor", "FACT", model="m2")]
        result = paired_metrics(rows)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["truth_discount"], 1)
        self.assertEqual(result[1]["truth_discount"], -0.5)
        self.assertTrue(all(row["status"] == "complete" for row in result))

    def test_missing_duplicate_or_incomplete_twin_has_no_contrast(self):
        truth = self.town("truth_twin")
        rumor = self.town("rumor", "SKEPTICAL")
        bad = copy.deepcopy(rumor)
        bad["metrics"]["status"] = "incomplete"
        variants = [[truth], [truth, rumor, copy.deepcopy(rumor)], [truth, bad]]
        for rows in variants:
            result = paired_metrics(rows)[0]
            self.assertEqual(result["status"], "incomplete")
            self.assertIsNone(result["truth_discount"])
            self.assertTrue(result["errors"])

    def test_all_omitted_pair_keeps_undefined_belief_and_defined_other_contrasts(self):
        result = paired_metrics([self.town("truth_twin", "NOT_MENTIONED"), self.town("rumor")])[0]
        self.assertEqual(result["status"], "complete")
        self.assertIsNone(result["truth_discount"])
        self.assertEqual(result["omission_rate_difference"], 1)
        self.assertEqual(result["sensitivity_lower_difference"], -1)
        self.assertEqual(result["sensitivity_neutral_difference"], -0.5)

    def test_duplicate_run_identity_and_nonfinite_metric_rejected(self):
        truth, rumor = self.town("truth_twin"), self.town("rumor")
        rumor["run_id"] = truth["run_id"]
        self.assertEqual(paired_metrics([truth, rumor])[0]["status"], "incomplete")
        rumor = self.town("rumor")
        rumor["metrics"]["belief_mean"] = float("nan")
        self.assertEqual(paired_metrics([truth, rumor])[0]["status"], "incomplete")

    def test_missing_pair_identity_raises_instead_of_cross_pair_pooling(self):
        row = self.town("truth_twin")
        del row["pair_id"]
        with self.assertRaises(ValueError):
            paired_metrics([row])
        self.assertEqual(paired_metrics([]), [])


if __name__ == "__main__":
    unittest.main()
