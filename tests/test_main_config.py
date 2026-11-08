"""The 64-cell main-study config: generation, validation, schedule and replay."""
import asyncio
from collections import Counter
from copy import deepcopy
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from truth_discount.artifacts import audit_town
from truth_discount.config import build_manifest, load_config, make_main_config, render_contexts
from truth_discount.contracts import canonical_bytes
from truth_discount.fixtures import FixtureBackend
from truth_discount.runner import run_town

CONFIGS = Path(__file__).resolve().parents[1] / "configs"


class MainConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = load_config(CONFIGS / "pilot_config.json")
        cls.main = load_config(CONFIGS / "main_config.json")
        cls.runs = build_manifest(cls.main)

    def invalid(self, config, expected):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, expected):
                load_config(path)

    def test_committed_main_config_matches_the_generator(self):
        self.assertEqual(self.main, make_main_config(self.pilot),
                         "regenerate with scripts/make_main_config.py after changing the pilot config")
        for key in ("prompts_and_templates", "personas", "experimental_knobs", "seating_and_pairing",
                    "judging_and_scoring", "artists", "models", "hyperparameters"):
            self.assertEqual(self.main[key], self.pilot[key], key)

    def test_cells_are_every_knob_combination_once(self):
        cells = sorted(self.main["cells"], key=lambda cell: cell["cell_id"])
        self.assertEqual([c["cell_id"] for c in cells], list(range(1, 65)))
        levels = self.main["factorial_levels"]
        expected = [dict(zip(levels, combo)) for combo in itertools.product(*levels.values())]
        self.assertEqual(sorted(map(canonical_bytes, (c["knobs"] for c in cells))),
                         sorted(map(canonical_bytes, expected)))
        self.assertEqual(cells[0]["knobs"], {"closeness": "close_friend", "authority": "mayor",
                                             "reliability": "good_record", "wealth": "rich", "identity": "woman_old"})
        for pilot_id, main_id in self.main["pilot_cell_ids_in_main"].items():
            pilot_cell = next(c for c in self.pilot["pilot_cells"] if c["cell_id"] == int(pilot_id))
            self.assertEqual(cells[main_id - 1]["knobs"], pilot_cell["knobs"])

    def test_schedule_counts_ids_and_artist_balance(self):
        self.assertEqual(len(self.runs), 9984)
        self.assertEqual(len({r["run_id"] for r in self.runs}), 9984)
        per_model = Counter(r["model_key"] for r in self.runs)
        self.assertEqual(set(per_model.values()), {4992})
        model = self.runs[0]["model_key"]
        for cell in range(1, 65):
            rumors = [r for r in self.runs if r["model_key"] == model and r["cell_id"] == cell
                      and r["condition_type"] == "rumor"]
            self.assertEqual(len({r["seed_id"] for r in rumors}), 39)
            split = Counter(r["real_artist"] for r in rumors)
            self.assertEqual(sorted(split.values()), [19, 20])
            majority = max(split, key=split.get)
            self.assertEqual(majority, "Kaelen Cross" if cell % 2 else "Vesper Vance")

    def test_pilot_cells_give_listeners_the_same_prompts_in_the_main_study(self):
        pilot_runs = build_manifest(self.pilot, [self.pilot["models"]["agent_models"][0]["key"]])
        main_runs = {(r["cell_id"], r["seed_id"], r["condition_type"]): r for r in self.runs
                     if r["model_key"] == pilot_runs[0]["model_key"]}
        for pilot_id, main_id in self.main["pilot_cell_ids_in_main"].items():
            run = next(r for r in pilot_runs if r["cell_id"] == int(pilot_id) and r["seed_id"] == 4)
            twin = main_runs[(main_id, 4, run["condition_type"])]
            pilot_contexts, main_contexts = render_contexts(self.pilot, run), render_contexts(self.main, twin)
            self.assertEqual([pilot_contexts[s] for s in range(1, 13)], [main_contexts[s] for s in range(1, 13)])

    def test_sorted_keys_in_saved_bundles_keep_the_cell_numbering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_bytes(canonical_bytes(self.main))
            reloaded = load_config(path)
        self.assertEqual([r["run_id"] for r in build_manifest(reloaded)], [r["run_id"] for r in self.runs])

    def test_validation_rejects_a_broken_factorial(self):
        swapped = deepcopy(self.main)
        swapped["cells"][0]["knobs"], swapped["cells"][1]["knobs"] = swapped["cells"][1]["knobs"], swapped["cells"][0]["knobs"]
        self.invalid(swapped, "factorial order")
        dropped = deepcopy(self.main)
        dropped["cells"].pop()
        self.invalid(dropped, "64 cells")
        levels = deepcopy(self.main)
        levels["factorial_levels"]["identity"].append("woman_old")
        self.invalid(levels, "factorial_levels")
        mixed = deepcopy(self.main)
        mixed["pilot_cells"] = deepcopy(self.pilot["pilot_cells"])
        self.invalid(mixed, "'cells' only")
        counts = deepcopy(self.main)
        counts["meta"]["total_town_runs_per_model"] = 312
        self.invalid(counts, "meta.total_town_runs_per_model")
        with self.assertRaisesRegex(ValueError, "derived from the pilot"):
            make_main_config(self.main)

    def test_a_main_study_town_runs_and_replays(self):
        run = next(r for r in self.runs if r["cell_id"] == 62 and r["condition_type"] == "rumor")
        with tempfile.TemporaryDirectory() as directory:
            town = asyncio.run(run_town(self.main, run, FixtureBackend(), Path(directory)))
            self.assertEqual(town["run_status"], "completed")
            self.assertEqual(audit_town(Path(directory) / run["run_id"])["cell_id"], 62)


if __name__ == "__main__":
    unittest.main()
