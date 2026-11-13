"""Two-source probes: spec, manifest, contexts, replay audit, sharding and mocked collection.

No provider network or real keys. The main-run modules and configs are not modified by probes.
"""
import asyncio
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_live_cli import approved_test_manifest, MockHTTP
from truth_discount.artifacts import InvalidBundle
from truth_discount.budget import BudgetLedger
from truth_discount.cli import main
from truth_discount.config import load_config, render_template
from truth_discount.contracts import canonical_bytes, digest
from truth_discount.fixtures import FixtureBackend
from truth_discount.probe_artifacts import (PROBE_SOURCE_FILES, _exports, audit_probe_simulation,
                                            probe_grading_items)
from truth_discount.probe_config import (PROBE_CONFIGS, build_probe_manifest, departure_text, flip_knobs,
                                         load_probe_spec, ordered_sources, render_probe_contexts,
                                         validate_probe_spec)
from truth_discount.probe_execution import (allocate_probe_runs, collect_probe_simulations, probe_plan,
                                            review_probe_simulations, select_probe_runs)
from truth_discount.probe_runner import run_probe_town
from truth_discount.providers import ProviderBackend
from truth_discount.simulation_artifacts import GENERATION_SOURCE_FILES

ROOT = Path(__file__).resolve().parents[1]
TEN = [1, 5, 9, 14, 22, 30, 41, 46, 57, 62]


def final_spec(spec, ids=TEN):
    result = deepcopy(spec)
    result["dna_selection"] = {"status": "final", "rule": "test rule: highest rumor-twin belief", "cell_ids": list(ids)}
    return result


class ProbeDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(ROOT / "configs/main_config.json")
        cls.awaiting = load_probe_spec(ROOT / "configs/probe_spec.json", cls.config)
        cls.placeholder = load_probe_spec(ROOT / "configs/probe_spec.placeholder.json", cls.config)
        cls.final = final_spec(cls.awaiting)
        cls.runs = build_probe_manifest(cls.config, cls.final)

    def test_spec_is_bound_to_main_config_and_awaits_dnas(self):
        self.assertEqual(self.awaiting["dna_selection"]["status"], "awaiting_main_results")
        with self.assertRaisesRegex(ValueError, "no DNAs yet"):
            build_probe_manifest(self.config, self.awaiting)
        pilot = load_config(ROOT / "configs/pilot_config.json")
        with self.assertRaisesRegex(ValueError, "main config"):
            validate_probe_spec(self.awaiting, pilot)
        changed = deepcopy(self.config)
        changed["meta"]["town_name"] = "Elsewhere"
        with self.assertRaisesRegex(ValueError, "different main config"):
            validate_probe_spec(self.awaiting, changed)

    def test_spec_rejects_incomplete_or_altered_designs(self):
        cases = []
        short = final_spec(self.awaiting, TEN[:9]); cases.append((short, "exactly 10"))
        no_rule = final_spec(self.awaiting); no_rule["dna_selection"]["rule"] = "TBD"; cases.append((no_rule, "frozen"))
        dup = final_spec(self.awaiting, TEN[:9] + [1]); cases.append((dup, "unique"))
        bad_cell = final_spec(self.awaiting, TEN[:9] + [65]); cases.append((bad_cell, "unique main cell"))
        rotating = deepcopy(self.final); rotating["second_source_persona_id"] = 3; cases.append((rotating, "reserved persona"))
        probes = deepcopy(self.final); probes["probes"]["probe_2"] = ["flip_all"]; cases.append((probes, "documented"))
        cue = deepcopy(self.final); cue["templates"]["scene_3_first_hand_cue"] = "Hi {partner_name}."; cases.append((cue, "placeholders"))
        line = deepcopy(self.final); line["templates"]["departures"]["contradicting_truth"] = "{real_artist}!"; cases.append((line, "placeholders"))
        for spec, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_probe_spec(spec, self.config)

    def test_full_manifest_counts_and_counterbalancing(self):
        self.assertEqual(len(self.runs), 4680)
        self.assertEqual(len({r["run_id"] for r in self.runs}), 4680)
        per = Counter((r["model_key"], r["probe"]) for r in self.runs)
        self.assertEqual(set(per.values()), {1170})
        groups = Counter(r["group_id"] for r in self.runs)
        self.assertEqual((len(groups), set(groups.values())), (1560, {3}))
        for key in {(r["model_key"], r["probe_config"], r["dna_cell_id"]) for r in self.runs}:
            block = [r for r in self.runs if (r["model_key"], r["probe_config"], r["dna_cell_id"]) == key]
            self.assertEqual(len(block), 39)
            self.assertEqual(sorted(Counter(r["parker_role"] for r in block).values()), [19, 20])
            self.assertEqual(sorted(Counter(r["departure_order"][0] for r in block).values()), [19, 20])
            self.assertEqual(sorted(Counter(r["real_artist"] for r in block).values()), [19, 20])
            crossed = Counter((r["parker_role"], r["departure_order"][0]) for r in block)
            self.assertEqual(len(crossed), 4)
            self.assertLessEqual(max(crossed.values()) - min(crossed.values()), 2)

    def test_group_members_share_world_and_differ_only_in_configuration(self):
        shared = ("model_key", "probe", "dna_cell_id", "seed_id", "layout_id", "repetition_id", "real_artist",
                  "fake_artist", "parker_role", "departure_order", "listener_seating", "catch_up_pairs")
        by_group = {}
        for run in self.runs:
            by_group.setdefault(run["group_id"], []).append(run)
        for members in list(by_group.values())[:200]:
            self.assertEqual(len({digest({k: m[k] for k in shared}) for m in members}), 1)
            self.assertEqual(sorted(m["probe_config"] for m in members), sorted(PROBE_CONFIGS[members[0]["probe"]]))

    def test_sources_claims_flips_lines_and_judge_target(self):
        for run in self.runs[:600] + self.runs[-600:]:
            s1, s2 = run["sources"]
            dna = next(c for c in self.config["cells"] if c["cell_id"] == run["dna_cell_id"])["knobs"]
            self.assertEqual((s1["role"], s2["role"], s1["knobs"]), ("source_1", "source_2", dna))
            self.assertEqual({s1["persona_id"], s2["persona_id"]} - {14}, {self.config["seating_and_pairing"][
                "latin_square_rotations"][run["layout_id"]]["source_seat_0_persona_id"]})
            self.assertEqual((s1 if run["parker_role"] == "source_1" else s2)["persona_id"], 14)
            self.assertNotIn(14, run["listener_seating"].values())
            config = run["probe_config"]
            changed = {k for k in dna if s2["knobs"][k] != dna[k]}
            self.assertEqual(changed, {"consensus_lie": set(), "consensus_truth": set(), "direct_conflict": set(),
                                       "flip_all": set(dna), "flip_social": {"closeness", "authority"},
                                       "flip_demographics": {"identity"}}[config])
            claims = (s1["claim"], s2["claim"])
            self.assertEqual(claims, {"consensus_lie": ("fake", "fake"), "consensus_truth": ("real", "real")}.get(
                config, ("fake", "real")))
            self.assertEqual(run["target_claim"], "real" if config == "consensus_truth" else "fake")
            self.assertEqual(run["target_artist"], run[run["target_claim"] + "_artist"])
            first, second = ordered_sources(run)
            if config.startswith("consensus"):
                self.assertEqual((first["departure_line"], second["departure_line"]),
                                 ("opening", "reinforcing_after_rumor" if config == "consensus_lie" else "reinforcing_after_truth"))
            else:
                self.assertEqual((s1["departure_line"], s2["departure_line"]), ("opening", "contradicting_truth"))
        old_woman = {"closeness": "close_friend", "authority": "mayor", "reliability": "good_record",
                     "wealth": "rich", "identity": "woman_old"}
        self.assertEqual(flip_knobs(old_woman, ("closeness", "authority", "reliability", "wealth", "identity")),
                         {"closeness": "stranger", "authority": "citizen", "reliability": "poor_record",
                          "wealth": "poor", "identity": "man_young"})

    def test_contexts_name_both_sources_in_speaking_order(self):
        names = {p["id"]: p["name"] for p in self.config["personas"]}
        for run in self.runs[:24]:
            contexts = render_probe_contexts(self.config, self.final, run)
            self.assertEqual(sorted(contexts), list(range(1, 13)))
            first, second = (names[s["persona_id"]] for s in ordered_sources(run))
            for seat, text in contexts.items():
                self.assertNotRegex(text, r"\{[A-Za-z_]+\}")
                self.assertLess(text.index("About " + first + ":"), text.index("About " + second + ":"))
                self.assertIn(names[run["listener_seating"][str(seat)]], text.split("\n")[0])
                self.assertEqual("Right as breakfast ends" in text, seat <= 6)
            opening = next(s for s in run["sources"] if s["departure_line"] == "opening")
            self.assertEqual(departure_text(self.config, self.final, run, opening), render_template(
                self.config["prompts_and_templates"]["scene_1_source_departure_broadcast"],
                {"announced_artist": opening["announced_artist"]}))

    def test_probe_fingerprint_extends_main_generation_files(self):
        self.assertEqual(PROBE_SOURCE_FILES[:len(GENERATION_SOURCE_FILES)], GENERATION_SOURCE_FILES)
        self.assertFalse(any(name.startswith("probe_") for name in GENERATION_SOURCE_FILES))


class ProbeTownTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/main_config.json")
        self.spec = load_probe_spec(ROOT / "configs/probe_spec.placeholder.json", self.config)
        runs = build_probe_manifest(self.config, self.spec, ["deepseek_v4_flash"])
        group = next(r["group_id"] for r in runs if r["departure_order"][0] == "source_2" and r["probe"] == "probe_2")
        self.group = [r for r in runs if r["group_id"] == group]

    def town(self, run, mode="mixed"):
        town = asyncio.run(run_probe_town(self.config, self.spec, run, FixtureBackend(mode=mode), self.root))
        return town, self.root / run["run_id"]

    def test_fixture_towns_seal_replay_and_keep_two_ordered_departures(self):
        names = {p["id"]: p["name"] for p in self.config["personas"]}
        for run in self.group:
            town, directory = self.town(run)
            self.assertEqual(town["run_status"], "completed")
            self.assertEqual(audit_probe_simulation(directory)["run_id"], run["run_id"])
            speakers = [names[s["persona_id"]] for s in ordered_sources(run)]
            self.assertEqual([d["speaker"] for d in town["scene_1_departures"]], speakers)
            for seat in range(1, 13):
                history = town["agent_histories"][str(seat)]
                heard = [m["content"].split(":")[0] for m in history[1:3]]
                if seat <= 6:
                    self.assertEqual(heard, speakers)
                else:
                    self.assertFalse(any("before I head out" in m["content"] for m in history))
            self.assertEqual({c["seat_id"] for c in town["calls"]}, set(range(1, 13)))
            items = probe_grading_items(directory)
            self.assertEqual((len(items), {i["target_artist"] for i in items}), (12, {run["target_artist"]}))

    def test_replay_rejects_resealed_semantic_tampering(self):
        run = self.group[0]
        _, directory = self.town(run)
        def reseal(mutate):
            town = json.loads((directory / "town.json").read_text(encoding="utf-8"))
            mutate(town)
            data = _exports(town, self.config, self.spec)
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            for name, value in data.items():
                (directory / name).write_bytes(value)
                manifest["files"][name] = __import__("hashlib").sha256(value).hexdigest()
            (directory / "manifest.json").write_bytes(canonical_bytes(manifest))
        original = {p.name: p.read_bytes() for p in directory.iterdir()}
        def response(town):
            town["calls"][-1]["response"] = "A different saved answer."
        def order(town):
            town["departure_order"] = list(reversed(town["departure_order"]))
        def departure(town):
            town["scene_1_departures"][0]["text"] = "Something else entirely."
        for mutate, message in ((response, "response text mismatch|replay mismatch"), (order, "run-plan mismatch"),
                                (departure, "replay mismatch")):
            with self.subTest(message=message):
                reseal(mutate)
                with self.assertRaisesRegex(InvalidBundle, message):
                    audit_probe_simulation(directory)
                for name, value in original.items():
                    (directory / name).write_bytes(value)
        audit_probe_simulation(directory)

    def test_failed_town_is_sealed_as_failed_and_still_replays(self):
        class Timeouts(FixtureBackend):
            async def generate(self, request):
                if request.scene == 3 and request.seat == 2:
                    raise TimeoutError("slow provider")
                return await super().generate(request)
        run = self.group[1]
        town = asyncio.run(run_probe_town(self.config, self.spec, run, Timeouts(), self.root))
        self.assertEqual((town["run_status"], town["generation_status"]), ("timeout", "failed"))
        self.assertEqual(audit_probe_simulation(self.root / run["run_id"])["error"]["scene"], 3)


class ProbeExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_config(ROOT / "configs/main_config.json")
        self.spec = load_probe_spec(ROOT / "configs/probe_spec.placeholder.json", self.config)
        self.providers = approved_test_manifest(self.config)
        agents = {m["key"] for m in self.config["models"]["agent_models"]}
        self.providers["routes"] = {k: v for k, v in self.providers["routes"].items() if k in agents}

    def test_six_shards_are_complete_disjoint_group_intact_and_balanced(self):
        spec = final_spec(self.spec)
        full = build_probe_manifest(self.config, spec)
        seen, ids = set(), set()
        for index in range(6):
            runs, allocation = allocate_probe_runs(self.config, spec, full, shard_count=6, shard_index=index)
            again, same = allocate_probe_runs(self.config, spec, list(reversed(full)), shard_count=6, shard_index=index)
            self.assertEqual((runs, allocation), (again, same))
            self.assertEqual((len(runs), allocation["planned_groups"]), (780, 260))
            self.assertEqual(set(Counter(r["group_id"] for r in runs).values()), {3})
            for field in ("model_key", "probe"):
                self.assertEqual(len(set(Counter(r[field] for r in runs).values())), 1)
            parker = Counter(r["parker_role"] for r in runs)
            self.assertLessEqual(abs(parker["source_1"] - parker["source_2"]), 0.1 * len(runs))
            self.assertFalse(seen.intersection(allocation["run_ids"]))
            seen.update(allocation["run_ids"])
            ids.add(allocation["allocation_id"])
        self.assertEqual((len(seen), len(ids)), (4680, 1))

    def test_allocation_rejects_split_groups_and_altered_runs(self):
        runs = select_probe_runs(self.config, self.spec, ["deepseek_v4_flash"], ["probe_1"])
        with self.assertRaisesRegex(ValueError, "all three configurations"):
            allocate_probe_runs(self.config, self.spec, runs[:-1])
        changed = deepcopy(runs)
        changed[0]["target_artist"] = "Somebody Else"
        with self.assertRaisesRegex(ValueError, "probe manifest"):
            allocate_probe_runs(self.config, self.spec, changed)
        with self.assertRaisesRegex(ValueError, "seed range"):
            select_probe_runs(self.config, self.spec, start_seed=38, seeds_per_dna=2)

    def test_plan_needs_no_judge_and_reuses_route_gates(self):
        runs, allocation = allocate_probe_runs(self.config, self.spec, select_probe_runs(self.config, self.spec))
        info = probe_plan(self.config, self.spec, self.providers, runs, allocation)
        self.assertEqual((info["execution_gates"], info["primary_judge_key"], info["planned_towns"]), ([], None, 48))
        blocked = deepcopy(self.providers)
        blocked["routes"]["qwen_3_8_flash"]["pricing_verified"] = False
        self.assertIn("qwen_3_8_flash needs pricing_verified",
                      probe_plan(self.config, self.spec, blocked, runs, allocation)["execution_gates"])

    def collect(self, output, ledger_path, http, runs, allocation, *, resume=False):
        with patch.dict(os.environ, {"TEST_PROVIDER_KEY": "FAKE_NOT_A_REAL_KEY"}), \
             patch("socket.create_connection", side_effect=AssertionError("network forbidden")), \
             BudgetLedger(ledger_path, "1") as ledger:
            backend = ProviderBackend(self.providers, ledger, transport=http, evidence_kind="mocked_provider")
            return asyncio.run(collect_probe_simulations(
                self.config, self.spec, self.providers, runs, output, backend, allocation=allocation,
                resume=resume, max_concurrent_towns=3, execution_authorized=True, spending_authorized=True))

    def test_mocked_collection_resumes_without_requests_and_binds_its_ledger(self):
        selection = select_probe_runs(self.config, self.spec, ["deepseek_v4_flash"], ["probe_1"])
        runs, allocation = allocate_probe_runs(self.config, self.spec, selection, shard_count=2, shard_index=0)
        output, ledger_path = self.root / "probe-0", self.root / "probe-0.jsonl"
        http = MockHTTP()
        result = self.collect(output, ledger_path, http, runs, allocation)
        self.assertEqual((result["completed_towns"], result["completed_groups"], result["status"]), (6, 2, "shards_complete"))
        self.assertEqual(result["phone_transcripts"], 72)
        self.assertTrue(http.requests and all("deepinfra.com" in r["url"] for r in http.requests))
        again = MockHTTP()
        rerun = self.collect(output, ledger_path, again, runs, allocation, resume=True)
        self.assertEqual((rerun["skipped_verified_towns"], again.requests), (6, []))
        with self.assertRaisesRegex(ValueError, "ledger identity"):
            self.collect(output, self.root / "other.jsonl", MockHTTP(), runs, allocation, resume=True)
        other, other_allocation = allocate_probe_runs(self.config, self.spec, selection, shard_count=2, shard_index=1)
        self.collect(self.root / "probe-1", self.root / "probe-1.jsonl", MockHTTP(), other, other_allocation)
        status = review_probe_simulations([output, self.root / "probe-1"])
        self.assertEqual((status["status"], status["completed_towns"], status["failed_generation_attempts"]),
                         ("generation_complete", 12, 0))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            review_probe_simulations([output, output])


class ProbeCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        config = load_config(ROOT / "configs/main_config.json")
        providers = approved_test_manifest(config)
        self.provider_file = self.root / "providers.json"
        self.provider_file.write_text(json.dumps(providers))

    def invoke(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), \
             patch("socket.create_connection", side_effect=AssertionError("network forbidden")):
            code = main(list(map(str, args)))
        return code, out.getvalue(), err.getvalue()

    def test_preview_demo_status_and_spending_gate(self):
        spec = ROOT / "configs/probe_spec.placeholder.json"
        code, out, _ = self.invoke("probe-simulate", "--probe-spec", spec, "--providers", self.provider_file,
                                   "--output", self.root / "out", "--all-seeds", "--shard-count", "6",
                                   "--shard-index", "2", "--summary")
        preview = json.loads(out)
        self.assertEqual((code, preview["planned_towns"], preview["provider_api_calls"]), (0, 312, 0))
        self.assertEqual(preview["counts"]["by_model"], {"deepseek_v4_flash": 156, "qwen_3_8_flash": 156})
        self.assertFalse((self.root / "out").exists())
        code, _, err = self.invoke("probe-simulate", "--probe-spec", spec, "--providers", self.provider_file,
                                   "--output", self.root / "out", "--execute")
        self.assertEqual(code, 1)
        self.assertIn("spending hold", err)
        code, out, _ = self.invoke("probe-demo", "--probe-spec", spec, "--output", self.root / "demo")
        self.assertEqual((code, json.loads(out)["towns"], json.loads(out)["judge_calls"]), (0, 12, 0))
        code, _, err = self.invoke("probe-simulate", "--probe-spec", ROOT / "configs/probe_spec.json",
                                   "--providers", self.provider_file, "--output", self.root / "x")
        self.assertEqual(code, 1)
        self.assertIn("no DNAs yet", err)


if __name__ == "__main__":
    unittest.main()
