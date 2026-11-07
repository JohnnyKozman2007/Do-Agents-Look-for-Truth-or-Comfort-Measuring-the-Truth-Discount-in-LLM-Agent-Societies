"""Schedule and prompt-visibility checks against the repository pilot config."""

from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.config import build_manifest, load_config, render_contexts, render_template, render_values


CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "pilot_config.json"


class ConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(CONFIG_PATH)
        cls.manifest = build_manifest(cls.config)

    def invalid_config(self, config, expected):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, expected):
                load_config(path)

    def test_schedule_has_exact_counts_and_unique_stable_ids(self):
        self.assertEqual(len(self.manifest), 624)
        self.assertEqual(len({run["run_id"] for run in self.manifest}), 624)
        self.assertEqual(len({run["pair_id"] for run in self.manifest}), 312)
        self.assertEqual(set(Counter(run["model_key"] for run in self.manifest).values()), {312})
        self.assertEqual(set(Counter((r["model_key"], r["cell_id"], r["condition_type"])
                                    for r in self.manifest).values()), {39})
        self.assertEqual(self.manifest, build_manifest(self.config))

    def test_twins_share_world_seating_seed_knobs_and_change_only_claim(self):
        pairs = defaultdict(list)
        for run in self.manifest:
            pairs[run["pair_id"]].append(run)
        for twins in pairs.values():
            self.assertEqual(len(twins), 2)
            rumor, truth = twins
            self.assertEqual((rumor["condition_type"], truth["condition_type"]), ("rumor", "truth_twin"))
            self.assertEqual(rumor["announced_artist"], rumor["fake_artist"])
            self.assertEqual(truth["announced_artist"], truth["real_artist"])
            differing = {key for key in rumor if rumor[key] != truth[key]}
            self.assertEqual(differing, {"run_id", "condition_type", "announced_artist"})

    def test_artist_allocation_flips_odd_cell_majority_and_balances_each_model(self):
        for model_key in {run["model_key"] for run in self.manifest}:
            runs = [run for run in self.manifest if run["model_key"] == model_key]
            self.assertEqual(Counter(run["real_artist"] for run in runs),
                             {"Vesper Vance": 156, "Kaelen Cross": 156})
            for cell_id in range(1, 5):
                worlds = [r for r in runs if r["cell_id"] == cell_id and r["condition_type"] == "rumor"]
                counts = Counter(r["real_artist"] for r in worlds)
                self.assertEqual(counts["Vesper Vance"], 20 if cell_id % 2 == 0 else 19)
                self.assertEqual(set(r["seed_id"] for r in worlds), set(range(39)))
                for run in worlds:
                    self.assertEqual(run["seed_id"], run["layout_id"] * 3 + run["repetition_id"])

    def test_latin_rotation_covers_all_personas_and_pairs_remain_local(self):
        runs = [run for run in self.manifest if run["model_key"] == self.manifest[0]["model_key"]
                and run["cell_id"] == 1 and run["repetition_id"] == 0 and run["condition_type"] == "rumor"]
        for seat in range(13):
            self.assertEqual({r["seating_assignment"][str(seat)] for r in runs}, set(range(1, 14)))
        for run in runs:
            self.assertNotIn(14, run["seating_assignment"].values())
            self.assertEqual(run["source_persona_id"], run["seating_assignment"]["0"])
            self.assertEqual(len(run["catch_up_pairs"]), 6)
            for pair in run["catch_up_pairs"]:
                first, second = pair["first_hand_seat"], pair["second_hand_seat"]
                self.assertEqual(second, first + 6)
                self.assertEqual(pair["first_hand_persona_id"], run["seating_assignment"][str(first)])
                self.assertEqual(pair["second_hand_persona_id"], run["seating_assignment"][str(second)])

    def test_model_selection_rejects_empty_unknown_and_duplicates(self):
        key = self.manifest[0]["model_key"]
        self.assertEqual(len(build_manifest(self.config, [key])), 312)
        for selection in ([], ["unknown"], [key, key]):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                build_manifest(self.config, selection)

    def test_manifest_mutation_does_not_change_twin_or_configuration(self):
        manifest = build_manifest(self.config)
        before = deepcopy(manifest[1])
        manifest[0]["seating_assignment"]["1"] = 99
        manifest[0]["knobs"]["reliability"] = "changed"
        manifest[0]["catch_up_pairs"][0]["second_hand_seat"] = 99
        self.assertEqual(manifest[1], before)
        self.assertEqual(self.config["seating_and_pairing"]["latin_square_rotations"][0]["seat_map"]["1"], 2)

    def test_contexts_are_complete_and_initial_listeners_are_identical_across_twins(self):
        for rumor, truth in zip(self.manifest[::2], self.manifest[1::2]):
            rumor_contexts = render_contexts(self.config, rumor)
            truth_contexts = render_contexts(self.config, truth)
            self.assertEqual(set(rumor_contexts), set(range(13)))
            for seat in range(1, 13):
                self.assertEqual(rumor_contexts[seat], truth_contexts[seat])
                self.assertIn("You have $40 of spending money", rumor_contexts[seat])
                self.assertNotIn("From the bus window", rumor_contexts[seat])
            for context in rumor_contexts.values():
                self.assertNotRegex(context, r"\{[A-Za-z_][A-Za-z0-9_]*\}")
                self.assertIn("Kaelen Cross and Vesper Vance", context)
                for private_key in ("truth_twin", "real_artist", "fake_artist", "seed_id", "cell_id"):
                    self.assertNotIn(private_key, context)

    def test_source_has_self_knobs_and_scripted_claim_but_no_reliability(self):
        run = self.manifest[0]
        values = render_values(self.config, run, 0)
        source_context = render_contexts(self.config, run)[0]
        for knob in ("identity", "authority", "wealth", "closeness"):
            self.assertIn(values[f"{knob}_self"], source_context)
        self.assertNotIn("reliability_self", values)
        self.assertNotIn(values["reliability_line"], source_context)
        self.assertIn(values["scene_1_source_departure_broadcast"], source_context)
        self.assertEqual(values["table_names"], "Sam, Jordan, Casey, Riley, Taylor, Morgan")
        changed = deepcopy(run)
        changed["knobs"]["reliability"] = "poor_record"
        self.assertEqual(source_context, render_contexts(self.config, changed)[0])
        self.assertNotEqual(render_contexts(self.config, run)[1], render_contexts(self.config, changed)[1])

    def test_partner_names_follow_the_seats_in_both_directions(self):
        run = self.manifest[0]
        self.assertEqual(render_values(self.config, run, 1)["partner_name"], "Jamie")
        self.assertEqual(render_values(self.config, run, 7)["partner_name"], "Sam")
        self.assertIn("You have just run into Sam.", render_contexts(self.config, run)[7])
        self.assertEqual(render_values(self.config, run, 0)["partner_name"], "")
        for seat in (-1, 13, True, "1"):
            with self.subTest(seat=seat), self.assertRaises(ValueError):
                render_values(self.config, run, seat)

    def test_literal_json_and_inserted_response_braces_are_preserved(self):
        template = 'Judge {announced_artist}. Reply {"label": "<LABEL>", "quote": "<exact quote>"}'
        self.assertEqual(render_template(template, {"announced_artist": "Vesper Vance"}),
                         'Judge Vesper Vance. Reply {"label": "<LABEL>", "quote": "<exact quote>"}')
        self.assertEqual(render_template('{speaker_name}: "{text}"', {"speaker_name": "Alex", "text": "I said {name}."}),
                         'Alex: "I said {name}."')
        for values in ({}, {"missing": None}):
            with self.assertRaisesRegex(ValueError, "Unresolved.*missing"):
                render_template("Hello {missing}", values)

    def test_validation_rejects_unsupported_version_dimensions_and_artist_schedule(self):
        for key, value in (("version", "2.0.0"), ("total_town_runs_per_model", 156), ("agents_per_town", 14)):
            config = deepcopy(self.config)
            config["meta"][key] = value
            self.invalid_config(config, "supported version|meta\\.")
        config = deepcopy(self.config)
        config["artists"]["counterbalancing_schedule"]["even_seeds"]["seed_parity"] = "even seed_id"
        self.invalid_config(config, "parity")
        config = deepcopy(self.config)
        config["artists"]["shared_intro_order"]["intro_artist_1"] = "Vesper Vance"
        self.invalid_config(config, "alphabetical")

    def test_validation_rejects_reserved_persona_seat_drift_and_pair_mismatch(self):
        for mutation in ("reserved", "wrong_pair", "wrong_redundant_field"):
            config = deepcopy(self.config)
            layout = config["seating_and_pairing"]["latin_square_rotations"][0]
            if mutation == "reserved":
                layout["seat_map"]["0"] = 14
            elif mutation == "wrong_pair":
                layout["catch_up_pairs"][0]["second_hand_persona_id"] = 9
            else:
                layout["first_hand_seats_1_to_6"][0] = 9
            with self.subTest(mutation=mutation):
                self.invalid_config(config, "layout 0")

    def test_validation_rejects_ground_truth_leak_missing_context_and_wrong_knob_order(self):
        for name, suffix in (("shared_system_prompt_header", " {real_artist}"),
                             ("second_hand_listener_context", " {scene_1_source_departure_broadcast}"),
                             ("scene_1_source_prompt", " {reliability_line}")):
            config = deepcopy(self.config)
            config["prompts_and_templates"][name] += suffix
            self.invalid_config(config, "placeholders differ")
        config = deepcopy(self.config)
        config["prompts_and_templates"]["second_hand_listener_context"] = "{shared_header}"
        self.invalid_config(config, "placeholders differ")
        config = deepcopy(self.config)
        config["prompts_and_templates"]["first_hand_listener_context"] = config["prompts_and_templates"]["first_hand_listener_context"].replace(
            "{identity_line} {authority_line}", "{authority_line} {identity_line}")
        self.invalid_config(config, "knob order")

    def test_validation_rejects_nonshared_twin_world_and_incomplete_conditions(self):
        config = deepcopy(self.config)
        config["pilot_cells"][0]["conditions"][1]["ground_truth_noticeboard"] += " EXTRA"
        self.invalid_config(config, "same noticeboard")
        config = deepcopy(self.config)
        config["pilot_cells"][0]["conditions"].pop()
        self.invalid_config(config, "one rumor and one truth_twin")

    def test_duplicate_json_fields_are_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text('{"meta": {}, "meta": {}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key: meta"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
