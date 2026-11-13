"""Two-source probes (Probe 1 truth table, Probe 2 anti-agent) built on the unchanged main world.

A probe spec names the main config it extends (by hash), the probe DNAs (main cell IDs), the
second-source persona and the two-source prompt texts. Everything else (personas, knob lines,
layouts, artists, scenes 2-5 and settings) comes from the main config unchanged, so main-run
code, fingerprints and sealed shards are untouched by this module.

Design rules, from docs/01-04:
- 14 agents: two scripted sources plus the main study's 12 listeners and 6 catch-up pairs.
- Source 1 carries the probe DNA. In Probe 1 Source 2 has the same DNA; in Probe 2 Source 2
  is the anti-agent with all, social (closeness, authority) or demographic (gender, age) knobs flipped.
- Parker (persona 14) plays Source 1 in half the runs and Source 2 in the other half; the
  layout's seat-0 persona plays the other source. Departure order is counterbalanced the same way.
- Consensus configs use positional lines (the second speaker reinforces the first); conflict
  configs use role lines (liar: the main departure line, truth-teller: the contradicting line).
- Judge target: the fake artist, except consensus truth, where both sources announce the real one.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .config import _PLACEHOLDER, render_template, study_cells
from .contracts import clone, digest


PROBE_SPEC_VERSION = "1.0.0"
PROBE_CONFIGS = {
    "probe_1": ("consensus_lie", "consensus_truth", "direct_conflict"),
    "probe_2": ("flip_all", "flip_social", "flip_demographics"),
}
KNOB_ORDER = ("identity", "authority", "wealth", "closeness", "reliability")
# Which knobs Source 2 flips relative to the probe DNA, per configuration.
_FLIPS = {
    "consensus_lie": (), "consensus_truth": (), "direct_conflict": (),
    "flip_all": ("closeness", "authority", "reliability", "wealth", "identity"),
    "flip_social": ("closeness", "authority"),
    "flip_demographics": ("identity",),
}
_BINARY_FLIP = {"close_friend": "stranger", "stranger": "close_friend", "mayor": "citizen",
                "citizen": "mayor", "good_record": "poor_record", "poor_record": "good_record",
                "rich": "poor", "poor": "rich"}
# Gender and age both flip: an old woman's anti-agent is a young man.
_IDENTITY_FLIP = {"woman_old": "man_young", "man_young": "woman_old",
                  "woman_young": "man_old", "man_old": "woman_young"}
# (claim of source_1, claim of source_2, line rule). Positional lines go to whoever speaks first/second.
_CLAIMS = {
    "consensus_lie": ("fake", "fake", "by_position"),
    "consensus_truth": ("real", "real", "by_position"),
    "direct_conflict": ("fake", "real", "by_role"),
    "flip_all": ("fake", "real", "by_role"),
    "flip_social": ("fake", "real", "by_role"),
    "flip_demographics": ("fake", "real", "by_role"),
}
_POSITIONAL_LINES = {"consensus_lie": ("opening", "reinforcing_after_rumor"),
                     "consensus_truth": ("opening", "reinforcing_after_truth")}
_ROLE_LINES = {"source_1": "opening", "source_2": "contradicting_truth"}
_DNA_STATUSES = {"awaiting_main_results", "placeholder", "final"}
_TEMPLATE_FIELDS = {
    "source_about": {"source_name", "identity_line", "authority_line", "wealth_line",
                     "closeness_line", "reliability_line"},
    "first_hand_listener_context": {"shared_header", "budget", "first_name", "second_name",
                                    "first_about", "second_about"},
    "second_hand_listener_context": {"shared_header", "budget", "first_name", "second_name",
                                     "first_about", "second_about", "partner_name"},
    "scene_3_first_hand_cue": {"partner_name", "first_name", "second_name"},
}
_DEPARTURE_FIELDS = {"reinforcing_after_rumor": {"announced_artist"},
                     "reinforcing_after_truth": {"announced_artist"},
                     "contradicting_truth": {"announced_artist"}}
SEATS = range(1, 13)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"Invalid probe spec: {message}")


def _fields(template: Any, expected: set[str], path: str) -> None:
    _require(isinstance(template, str) and template.strip(), f"{path} must be non-empty text")
    actual = set(_PLACEHOLDER.findall(template))
    _require(actual == expected, f"{path} placeholders differ: missing={sorted(expected - actual)}, "
                                 f"unexpected={sorted(actual - expected)}")


def validate_probe_spec(spec: dict, config: dict) -> None:
    """Bind the spec to one validated main config and reject anything outside the probe design."""
    _require(isinstance(spec, dict), "root must be an object")
    try:
        _require(spec["probe_spec_version"] == PROBE_SPEC_VERSION, f"supported version is {PROBE_SPEC_VERSION}")
        _require(config["meta"]["module"] == "main", "probes extend the main config")
        _require(spec["base_config_sha256"] == digest(config), "spec is bound to a different main config")
        cells = {cell["cell_id"]: cell for cell in study_cells(config)}
        dna = spec["dna_selection"]
        _require(isinstance(dna, dict) and set(dna) >= {"status", "cell_ids", "rule"}, "dna_selection fields")
        status, ids = dna["status"], dna["cell_ids"]
        _require(status in _DNA_STATUSES, f"dna_selection.status must be one of {sorted(_DNA_STATUSES)}")
        _require(isinstance(ids, list) and all(type(i) is int and i in cells for i in ids)
                 and len(set(ids)) == len(ids), "dna_selection.cell_ids must be unique main cell IDs")
        if status == "awaiting_main_results":
            _require(ids == [], "an awaiting spec lists no DNAs")
        elif status == "placeholder":
            _require(1 <= len(ids) <= 10, "a placeholder spec lists 1 to 10 DNAs")
        else:
            _require(len(ids) == 10, "the final spec lists exactly 10 DNAs (top 10 from the main run)")
            _require(isinstance(dna["rule"], str) and dna["rule"].strip()
                     and "TBD" not in dna["rule"], "the final spec records its frozen selection rule")
        personas = {p["id"]: p for p in config["personas"]}
        second = spec["second_source_persona_id"]
        rotating = {layout["source_seat_0_persona_id"]
                    for layout in config["seating_and_pairing"]["latin_square_rotations"]}
        for layout in config["seating_and_pairing"]["latin_square_rotations"]:
            rotating.update(layout["seat_map"].values())
        _require(type(second) is int and second in personas and second not in rotating,
                 "second_source_persona_id must be the reserved persona outside the 13-seat rotation")
        _require(spec["probes"] == {name: list(configs) for name, configs in PROBE_CONFIGS.items()},
                 "probes must list exactly the documented Probe 1 and Probe 2 configurations")
        levels = config["factorial_levels"]
        for knob in ("closeness", "authority", "reliability", "wealth"):
            _require(all(_BINARY_FLIP.get(level) in levels[knob] for level in levels[knob]),
                     f"cannot flip {knob} levels {levels[knob]}")
        _require(set(_IDENTITY_FLIP) == set(levels["identity"]), "cannot flip identity levels")
        templates = spec["templates"]
        _require(set(templates) == set(_TEMPLATE_FIELDS) | {"departures"}, "unexpected template names")
        for name, fields in _TEMPLATE_FIELDS.items():
            _fields(templates[name], fields, f"templates.{name}")
        departures = templates["departures"]
        _require(set(departures) == set(_DEPARTURE_FIELDS), "unexpected departure line names")
        for name, fields in _DEPARTURE_FIELDS.items():
            _fields(departures[name], fields, f"templates.departures.{name}")
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"Invalid probe spec: missing field or wrong structure: {exc}") from exc


def load_probe_spec(path: Path, config: dict) -> dict:
    from .config import _unique_object
    spec = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    validate_probe_spec(spec, config)
    return spec


def flip_knobs(knobs: dict, flipped: tuple[str, ...]) -> dict:
    result = dict(knobs)
    for knob in flipped:
        result[knob] = _IDENTITY_FLIP[knobs[knob]] if knob == "identity" else _BINARY_FLIP[knobs[knob]]
    return result


def _cell_for(config: dict, knobs: dict) -> int:
    matches = [c["cell_id"] for c in study_cells(config) if c["knobs"] == knobs]
    if len(matches) != 1:
        raise ValueError("source knobs do not match exactly one main cell")
    return matches[0]


def counterbalance(seed_id: int) -> dict:
    """Parker's role and departure order alternate on independent bits of the seed (20/19 of 39).

    The main artist rule already uses the parity of seed + cell, so these use the next two bits.
    """
    return {"parker_role": "source_1" if (seed_id // 2) % 2 == 0 else "source_2",
            "departure_order": ["source_1", "source_2"] if (seed_id // 4) % 2 == 0 else ["source_2", "source_1"]}


def build_probe_manifest(config: dict, spec: dict, model_keys: list[str] | None = None) -> list[dict]:
    """Every probe town in model, probe, DNA, layout, repetition, configuration order.

    With 10 DNAs this is 1,170 towns per probe per model (10 DNAs x 3 configs x 13 layouts x 3 reps).
    A group (one model, probe, DNA and seed) holds its three configurations, which share seating,
    artists and counterbalancing, so configurations are compared like the main study's twins.
    """
    validate_probe_spec(spec, config)
    dna_ids = spec["dna_selection"]["cell_ids"]
    if not dna_ids:
        raise ValueError("the probe spec has no DNAs yet; fill dna_selection after the main analysis")
    available = [model["key"] for model in config["models"]["agent_models"]]
    selected = available if model_keys is None else list(model_keys)
    if not selected or any(k not in available for k in selected) or len(set(selected)) != len(selected):
        raise ValueError("model_keys must be a non-empty, unique subset of configured agent models")
    cells = {cell["cell_id"]: cell for cell in study_cells(config)}
    schedule = config["artists"]["counterbalancing_schedule"]
    parker = spec["second_source_persona_id"]
    runs = []
    for model_key in selected:
        for probe, configurations in PROBE_CONFIGS.items():
            for cell_id in sorted(dna_ids):
                dna = cells[cell_id]["knobs"]
                for layout in sorted(config["seating_and_pairing"]["latin_square_rotations"],
                                     key=lambda item: item["layout_id"]):
                    for repetition_id in range(config["meta"]["stochastic_repetitions_per_layout"]):
                        layout_id = layout["layout_id"]
                        seed_id = layout_id * 3 + repetition_id
                        allocation = schedule["even_seeds" if (seed_id + cell_id) % 2 == 0 else "odd_seeds"]
                        balance = counterbalance(seed_id)
                        latin = layout["source_seat_0_persona_id"]
                        persona = {"source_1": parker if balance["parker_role"] == "source_1" else latin,
                                   "source_2": latin if balance["parker_role"] == "source_1" else parker}
                        group_id = (f"{model_key}__{probe.replace('_', '-')}__dna-{cell_id:02d}"
                                    f"__layout-{layout_id:02d}__rep-{repetition_id}")
                        for configuration in configurations:
                            claim_1, claim_2, rule = _CLAIMS[configuration]
                            knobs_2 = flip_knobs(dna, _FLIPS[configuration])
                            artist = {"fake": allocation["fake_artist"], "real": allocation["real_artist"]}
                            sources = []
                            for role, claim, knobs in (("source_1", claim_1, dna), ("source_2", claim_2, knobs_2)):
                                position = balance["departure_order"].index(role)
                                line = (_POSITIONAL_LINES[configuration][position] if rule == "by_position"
                                        else _ROLE_LINES[role])
                                sources.append({"role": role, "persona_id": persona[role],
                                                "knobs": dict(knobs), "knob_cell_id": _cell_for(config, knobs),
                                                "claim": claim, "announced_artist": artist[claim],
                                                "speaks": position + 1, "departure_line": line})
                            target = "real" if configuration == "consensus_truth" else "fake"
                            runs.append({
                                "run_id": f"{group_id}__{configuration}", "group_id": group_id,
                                "model_key": model_key, "probe": probe, "probe_config": configuration,
                                "dna_cell_id": cell_id, "seed_id": seed_id, "layout_id": layout_id,
                                "repetition_id": repetition_id,
                                "real_artist": allocation["real_artist"], "fake_artist": allocation["fake_artist"],
                                "target_claim": target, "target_artist": artist[target],
                                "parker_role": balance["parker_role"],
                                "departure_order": list(balance["departure_order"]),
                                "sources": sources,
                                "listener_seating": {str(s): layout["seat_map"][str(s)] for s in SEATS},
                                "catch_up_pairs": clone(layout["catch_up_pairs"]),
                            })
    return runs


def _persona_values(config: dict, persona: dict) -> dict:
    return {"name": persona["name"], "job": persona["occupation"], "style": persona["conversational_style"],
            "day_detail": persona["daily_detail"], "loved_one": persona["loved_one"],
            "relation": persona["relation"], "town": config["meta"]["town_name"],
            "intro_artist_1": config["artists"]["shared_intro_order"]["intro_artist_1"],
            "intro_artist_2": config["artists"]["shared_intro_order"]["intro_artist_2"]}


def source_names(config: dict, run: dict) -> dict[str, str]:
    personas = {p["id"]: p for p in config["personas"]}
    return {source["role"]: personas[source["persona_id"]]["name"] for source in run["sources"]}


def ordered_sources(run: dict) -> list[dict]:
    by_role = {source["role"]: source for source in run["sources"]}
    return [by_role[role] for role in run["departure_order"]]


def departure_text(config: dict, spec: dict, run: dict, source: dict) -> str:
    """The exact scripted line one source says on leaving; inserted word for word, never generated."""
    values = {"announced_artist": source["announced_artist"]}
    if source["departure_line"] == "opening":
        # The main study's departure line, so Source 1 says exactly what main-run sources say.
        return render_template(config["prompts_and_templates"]["scene_1_source_departure_broadcast"], values)
    return render_template(spec["templates"]["departures"][source["departure_line"]], values)


def render_listener_values(config: dict, spec: dict, run: dict, seat: int) -> dict:
    """Formatting values for one listener seat (1-12); never itself an agent prompt."""
    if type(seat) is not int or seat not in SEATS:
        raise ValueError("listener seat must be an integer from 1 to 12")
    personas = {p["id"]: p for p in config["personas"]}
    persona = personas[run["listener_seating"][str(seat)]]
    values = _persona_values(config, persona)
    values["budget"] = f"${config['meta']['initial_budget_usd']:g}"
    values["real_artist"] = run["real_artist"]
    names = source_names(config, run)
    abouts = []
    for source in ordered_sources(run):
        lines = {"source_name": names[source["role"]]}
        for knob in KNOB_ORDER:
            template = config["experimental_knobs"][knob][source["knobs"][knob]]["listener_line"]
            lines[f"{knob}_line"] = render_template(template, {"source_name": names[source["role"]]})
        abouts.append(render_template(spec["templates"]["source_about"], lines))
    first, second = ordered_sources(run)
    values.update(first_name=names[first["role"]], second_name=names[second["role"]],
                  first_about=abouts[0], second_about=abouts[1])
    partner = seat + 6 if seat <= 6 else seat - 6
    values["partner_name"] = personas[run["listener_seating"][str(partner)]]["name"]
    values["shared_header"] = render_template(config["prompts_and_templates"]["shared_system_prompt_header"], values)
    return values


def render_probe_contexts(config: dict, spec: dict, run: dict) -> dict[int, str]:
    """Initial system context for each of the 12 listeners; sources are scripted and get none."""
    result = {}
    for seat in SEATS:
        values = render_listener_values(config, spec, run, seat)
        name = "first_hand_listener_context" if seat <= 6 else "second_hand_listener_context"
        template_values = {k: values[k] for k in _TEMPLATE_FIELDS[name]}
        result[seat] = render_template(spec["templates"][name], template_values)
    return result


def describe_manifest(runs: list[dict]) -> dict:
    """Counts a person can check by eye before any spending."""
    def count(key):
        result = {}
        for run in runs:
            value = run[key] if not isinstance(run[key], list) else "->".join(run[key])
            result[value] = result.get(value, 0) + 1
        return dict(sorted(result.items()))
    return {"towns": len(runs), "groups": len({r["group_id"] for r in runs}),
            "by_model": count("model_key"), "by_probe": count("probe"), "by_config": count("probe_config"),
            "by_dna_cell": count("dna_cell_id"), "parker_role": count("parker_role"),
            "departure_order": count("departure_order"), "target_claim": count("target_claim"),
            "max_phone_outcomes": 12 * len(runs)}


def is_probe_run_id(value: str) -> bool:
    return re.search(r"__probe-[12]__dna-\d{2}__", value) is not None
