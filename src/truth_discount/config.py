"""Validate the pilot and main-study configurations and render their schedules and prompts.

The main study is the full factorial of the knob levels: every combination is one
cell, numbered in a fixed order. Its config is generated from the pilot config by
make_main_config, so the two share every prompt, persona and layout.

This module has no provider clients. Model names and endpoints remain configuration
data, and a manifest seed identifies a world/layout repetition, not a provider RNG.
"""

from __future__ import annotations

from copy import deepcopy
import itertools
import json
from pathlib import Path
import re
from typing import Any


_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_KNOBS = ("identity", "authority", "wealth", "closeness", "reliability")
_SELF_KNOBS = _KNOBS[:-1]
_CONDITIONS = ("rumor", "truth_twin")
_SHARED_DIMENSIONS = {
    "latin_square_layouts": 13,
    "stochastic_repetitions_per_layout": 3,
    "total_seeds_per_cell": 39,
    "agents_per_town": 13,
    "listeners_scored_per_town": 12,
}
_DIMENSIONS = {
    "pilot": {"total_pilot_cells": 4, "total_conditions": 8, **_SHARED_DIMENSIONS,
              "total_town_runs_per_model": 312, "total_decision_evaluations_per_model": 3744},
    "main": {"total_cells": 64, "total_conditions": 128, **_SHARED_DIMENSIONS,
             "total_town_runs_per_model": 4992, "total_decision_evaluations_per_model": 59904},
}
# Main-study cell IDs count through the knob levels in this order, last knob fastest.
_FACTORIAL_ORDER = ("closeness", "authority", "reliability", "wealth", "identity")
_CELL_KEYS = {"pilot": "pilot_cells", "main": "cells"}
_LISTENER_FIELDS = {
    "shared_header", "budget", "source_name",
    *(f"{knob}_line" for knob in _KNOBS),
}
_PROMPT_FIELDS = {
    "shared_system_prompt_header": {
        "name", "job", "town", "style", "day_detail",
        "intro_artist_1", "intro_artist_2",
    },
    "scene_1_source_prompt": {
        "shared_header", "announced_artist", "table_names",
        "scene_1_source_departure_broadcast",
        *(f"{knob}_self" for knob in _SELF_KNOBS),
    },
    "first_hand_listener_context": _LISTENER_FIELDS,
    "second_hand_listener_context": _LISTENER_FIELDS | {"partner_name"},
    "scene_5_phone_cue": {"loved_one", "relation"},
    "scene_1_source_departure_broadcast": {"announced_artist"},
    "scene_2_and_4_check_prompt": set(),
    "scene_2_and_4_memory_on_go": {"real_artist"},
    "scene_3_second_hand_scripted_opener": {"partner_name"},
    "scene_3_first_hand_cue": {"partner_name", "source_name"},
    "scene_3_first_hand_closing_cue": {"partner_name"},
    "spoken_line_format": {"speaker_name", "text"},
    "scene_5_regex_trigger": {"real_artist", "fake_artist"},
    "optional_post_scoring_manipulation_check": {"source_name"},
}


def render_template(template: str, values: dict) -> str:
    """Replace identifier placeholders once; leave JSON and inserted text literal.

    Missing or null values fail explicitly. Substituted strings are not interpreted
    as templates, so a quoted reply containing ``{name}`` remains the exact reply.
    Composite prompt fields, such as shared_header, are rendered by render_values.
    """
    if not isinstance(template, str):
        raise ValueError("template must be a string")

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values or values[name] is None:
            raise ValueError(f"Unresolved template placeholder: {{{name}}}")
        return str(values[name])

    return _PLACEHOLDER.sub(replace, template)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"Invalid pilot config: {message}")


def _text(value: Any, path: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{path} must be non-empty text")


def _template_fields(template: Any, expected: set[str], path: str) -> None:
    _text(template, path)
    actual = set(_PLACEHOLDER.findall(template))
    _require(actual == expected,
             f"{path} placeholders differ: missing={sorted(expected - actual)}, "
             f"unexpected={sorted(actual - expected)}")


def _validate_config(config: dict) -> None:
    """Reject unsupported dimensions or internally inconsistent v1.1.0 data."""
    _require(isinstance(config, dict), "root must be an object")
    try:
        meta = config["meta"]
        _require(meta["version"] == "1.1.0", "supported version is 1.1.0")
        _require(meta["module"] in _DIMENSIONS, "supported modules are pilot and main")
        module = meta["module"]
        _require(all(key in config for key in [_CELL_KEYS[module]])
                 and not any(k in config for m, k in _CELL_KEYS.items() if m != module),
                 f"a {module} config lists its cells under {_CELL_KEYS[module]!r} only")
        for key, expected in _DIMENSIONS[module].items():
            _require(type(meta[key]) is int and meta[key] == expected,
                     f"meta.{key} must equal {expected}")
        _text(meta["town_name"], "meta.town_name")
        _require(meta["initial_budget_usd"] == 40 and meta["check_bus_cost_usd"] == 5,
                 "the v1.1.0 budget/check cost must remain $40/$5")

        models = config["models"]["agent_models"]
        _require(isinstance(models, list) and len(models) == 2, "exactly two agent models are required")
        model_keys = [model["key"] for model in models]
        _require(all(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9_-]+", key)
                     for key in model_keys), "agent model keys must be safe non-empty identifiers")
        _require(len(set(model_keys)) == 2, "agent model keys must be unique")
        for model in models:
            for field in ("display_name", "provider", "model_id"):
                _text(model[field], f"models.agent_models.{field}")

        artists = config["artists"]
        pool = artists["artist_pool"]
        _require(isinstance(pool, list) and len(pool) == 2
                 and all(isinstance(artist, str) and artist.strip() for artist in pool)
                 and len(set(pool)) == 2, "artist_pool must contain two distinct names")
        intro = artists["shared_intro_order"]
        _require([intro["intro_artist_1"], intro["intro_artist_2"]] == sorted(pool),
                 "shared introduction must use fixed alphabetical artist order")
        schedule = artists["counterbalancing_schedule"]
        _require(schedule["seed_id_formula"] == "layout_id * 3 + repetition_id",
                 "unsupported seed_id formula")
        even, odd = schedule["even_seeds"], schedule["odd_seeds"]
        _require(even["seed_parity"] == "even (seed_id + cell_id)"
                 and odd["seed_parity"] == "odd (seed_id + cell_id)",
                 "artist parity must include cell_id")
        _require({even["real_artist"], even["fake_artist"]} == set(pool)
                 and odd["real_artist"] == even["fake_artist"]
                 and odd["fake_artist"] == even["real_artist"],
                 "even and odd artist allocations must be reversals")

        personas = config["personas"]
        _require(isinstance(personas, list) and len(personas) == 14,
                 "the persona bank must contain 13 pilot personas plus reserved persona 14")
        _require(all(type(persona["id"]) is int for persona in personas)
                 and sorted(persona["id"] for persona in personas) == list(range(1, 15)),
                 "persona IDs must be unique integers 1..14")
        for persona in personas:
            for field in ("name", "occupation", "conversational_style", "daily_detail", "loved_one", "relation"):
                _text(persona[field], f"personas.{persona['id']}.{field}")
                _require(not _PLACEHOLDER.search(persona[field]),
                         f"personas.{persona['id']}.{field} must be literal text")
        _require(len({p["name"] for p in personas}) == 14, "persona names must be unique")

        knob_templates = config["experimental_knobs"]
        _require(set(knob_templates) == set(_KNOBS), "five knob groups are required")
        for knob in _KNOBS:
            _require(isinstance(knob_templates[knob], dict) and bool(knob_templates[knob]),
                     f"experimental_knobs.{knob} must contain levels")
            for level, templates in knob_templates[knob].items():
                path = f"experimental_knobs.{knob}.{level}"
                _template_fields(templates["listener_line"], {"source_name"}, path + ".listener_line")
                if knob == "reliability":
                    _require(templates["source_self"] is None, "source must not receive self reliability")
                else:
                    _template_fields(templates["source_self"], set(), path + ".source_self")

        cells = study_cells(config)
        count = meta.get("total_pilot_cells", meta.get("total_cells"))
        _require(isinstance(cells, list) and len(cells) == count, f"{count} cells are required")
        _require(all(type(cell["cell_id"]) is int for cell in cells)
                 and sorted(cell["cell_id"] for cell in cells) == list(range(1, count + 1)),
                 f"cell IDs must be unique integers 1..{count}")
        if module == "main":
            # Level order is stored as lists: saved bundles sort object keys.
            levels = config["factorial_levels"]
            _require(isinstance(levels, dict) and set(levels) == set(_KNOBS)
                     and all(isinstance(levels[k], list) and len(set(levels[k])) == len(levels[k])
                             and set(levels[k]) == set(knob_templates[k]) for k in _KNOBS),
                     "factorial_levels must list every level of every knob once")
            ordered = sorted(cells, key=lambda cell: cell["cell_id"])
            _require([cell["knobs"] for cell in ordered] == factorial_knobs(levels),
                     "main cells must be every knob combination once, in factorial order")
        for cell in cells:
            _require(set(cell["knobs"]) == set(_KNOBS), "each cell must specify all five knob groups")
            for knob, level in cell["knobs"].items():
                _require(level in knob_templates[knob], f"unknown {knob} level {level!r}")
            conditions = cell["conditions"]
            _require(isinstance(conditions, list) and len(conditions) == 2
                     and {c["condition_type"] for c in conditions} == set(_CONDITIONS),
                     "each cell needs one rumor and one truth_twin condition")
            posters = []
            for condition in conditions:
                expected = "{fake_artist}" if condition["condition_type"] == "rumor" else "{real_artist}"
                _require(condition["announced_artist_placeholder"] == expected,
                         "announced artist must follow the twin condition")
                poster = condition["ground_truth_noticeboard"]
                _template_fields(poster, {"real_artist"}, "ground_truth_noticeboard")
                posters.append(poster)
            _require(posters[0] == posters[1], "twins must share the same noticeboard")

        seating = config["seating_and_pairing"]
        _require(seating["total_seats"] == 13 and seating["source_seat"] == 0
                 and seating["first_hand_seats"] == list(range(1, 7))
                 and seating["second_hand_seats"] == list(range(7, 13)),
                 "seats must be source 0, first-hand 1..6, second-hand 7..12")
        layouts = seating["latin_square_rotations"]
        _require(isinstance(layouts, list) and len(layouts) == 13, "13 layouts are required")
        _require(all(type(layout["layout_id"]) is int for layout in layouts)
                 and sorted(layout["layout_id"] for layout in layouts) == list(range(13)),
                 "layout IDs must be unique integers 0..12")
        for layout in layouts:
            layout_id = layout["layout_id"]
            expected_map = {str(seat): (seat + layout_id) % 13 + 1 for seat in range(13)}
            _require(layout["seat_map"] == expected_map,
                     f"layout {layout_id} must match the forward 1-based Latin rotation")
            _require(layout["source_seat_0_persona_id"] == expected_map["0"]
                     and layout["first_hand_seats_1_to_6"] == [expected_map[str(s)] for s in range(1, 7)]
                     and layout["second_hand_seats_7_to_12"] == [expected_map[str(s)] for s in range(7, 13)],
                     f"layout {layout_id} redundant seating fields disagree")
            expected_pairs = [
                {"first_hand_seat": seat, "first_hand_persona_id": expected_map[str(seat)],
                 "second_hand_seat": seat + 6, "second_hand_persona_id": expected_map[str(seat + 6)]}
                for seat in range(1, 7)
            ]
            _require(layout["catch_up_pairs"] == expected_pairs,
                     f"layout {layout_id} catch-up pairs must agree with its seat map")

        prompts = config["prompts_and_templates"]
        for name, fields in _PROMPT_FIELDS.items():
            _template_fields(prompts[name], fields, f"prompts_and_templates.{name}")
        for name in ("first_hand_listener_context", "second_hand_listener_context"):
            positions = [prompts[name].index("{" + knob + "_line}") for knob in _KNOBS]
            _require(positions == sorted(positions), f"{name} knob order must match the prompt playbook")
        funnel = prompts["scene_5_phone_call_funnel"]
        _require(isinstance(funnel, list) and [line["step"] for line in funnel] == list(range(1, 7)),
                 "phone funnel must contain ordered steps 1..6")
        for line in funnel:
            _template_fields(line["loved_one_line"], set(), "phone funnel loved_one_line")
        for cell in cells:
            poster = cell["conditions"][0]["ground_truth_noticeboard"]
            _require(prompts["scene_2_and_4_memory_on_go"].endswith(poster),
                     "GO observation and condition noticeboard must use the same poster")
        _template_fields(config["judging_and_scoring"]["canonical_judge_prompt"], {"announced_artist"},
                         "judging_and_scoring.canonical_judge_prompt")
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"Invalid pilot config: missing field or wrong structure: {exc}") from exc


def study_cells(config: dict) -> list[dict]:
    """The pilot's four cells or the main study's full factorial."""
    return config[_CELL_KEYS[config["meta"]["module"]]]


def factorial_knobs(levels: dict[str, list[str]]) -> list[dict]:
    """Every combination of knob levels, in main-study cell-ID order (last knob fastest)."""
    return [dict(zip(_FACTORIAL_ORDER, combination))
            for combination in itertools.product(*(levels[knob] for knob in _FACTORIAL_ORDER))]


def make_main_config(pilot: dict) -> dict:
    """Derive the main-study config: the same world with every knob combination as a cell."""
    _validate_config(pilot)
    if pilot["meta"]["module"] != "pilot":
        raise ValueError("the main config is derived from the pilot config")
    result = {}
    for key, value in deepcopy(pilot).items():
        if key == "_comment":
            value = ("MAIN STUDY CONFIGURATION - generated from pilot_config.json by "
                     "scripts/make_main_config.py; edit the pilot config and regenerate")
        if key == "meta":
            value = {("total_cells" if k == "total_pilot_cells" else k): v for k, v in value.items()}
            value.update(module="main", **_DIMENSIONS["main"])
        if key == "pilot_cells":
            conditions = value[0]["conditions"]
            levels = {knob: list(pilot["experimental_knobs"][knob]) for knob in _FACTORIAL_ORDER}
            cells = [{"cell_id": index, "name": " / ".join(knobs[k] for k in _FACTORIAL_ORDER),
                      "knobs": knobs, "conditions": deepcopy(conditions)}
                     for index, knobs in enumerate(factorial_knobs(levels), start=1)]
            result["factorial_levels"] = levels
            by_knobs = {json.dumps(cell["knobs"], sort_keys=True): cell["cell_id"] for cell in cells}
            result["pilot_cell_ids_in_main"] = {str(cell["cell_id"]): by_knobs[json.dumps(cell["knobs"], sort_keys=True)]
                                                for cell in value}
            key, value = "cells", cells
        result[key] = value
    _validate_config(result)
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_config(path: Path) -> dict:
    """Load a JSON file and validate the supported v1.1.0 pilot or main contract."""
    config = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    _validate_config(config)
    return config


def build_manifest(config: dict, model_keys: list[str] | None = None) -> list[dict]:
    """Return 312 (pilot) or 4,992 (main) independent run records per selected model.

    Run order is model, cell, layout, repetition, condition. A pair_id excludes
    condition. Records do not share mutable seating, knob, or pairing objects.
    """
    _validate_config(config)
    available = [model["key"] for model in config["models"]["agent_models"]]
    selected = available if model_keys is None else list(model_keys)
    if (not selected or any(key not in available for key in selected)
            or len(set(selected)) != len(selected)):
        raise ValueError("model_keys must be a non-empty, unique subset of configured agent models")
    runs = []
    schedule = config["artists"]["counterbalancing_schedule"]
    for model_key in selected:
        for cell in sorted(study_cells(config), key=lambda item: item["cell_id"]):
            for layout in sorted(config["seating_and_pairing"]["latin_square_rotations"],
                                 key=lambda item: item["layout_id"]):
                for repetition_id in range(config["meta"]["stochastic_repetitions_per_layout"]):
                    cell_id, layout_id = cell["cell_id"], layout["layout_id"]
                    seed_id = layout_id * 3 + repetition_id
                    allocation = schedule["even_seeds" if (seed_id + cell_id) % 2 == 0 else "odd_seeds"]
                    pair_id = f"{model_key}__cell-{cell_id}__layout-{layout_id:02d}__rep-{repetition_id}"
                    for condition_type in _CONDITIONS:
                        run = {
                            "run_id": f"{pair_id}__{condition_type}",
                            "pair_id": pair_id,
                            "model_key": model_key,
                            "cell_id": cell_id,
                            "condition_type": condition_type,
                            "seed_id": seed_id,
                            "layout_id": layout_id,
                            "repetition_id": repetition_id,
                            "real_artist": allocation["real_artist"],
                            "fake_artist": allocation["fake_artist"],
                            "announced_artist": allocation["fake_artist" if condition_type == "rumor" else "real_artist"],
                            "source_persona_id": layout["source_seat_0_persona_id"],
                            "seating_assignment": deepcopy(layout["seat_map"]),
                            "knobs": deepcopy(cell["knobs"]),
                            "catch_up_pairs": deepcopy(layout["catch_up_pairs"]),
                        }
                        runs.append(run)
    return runs


def render_values(config: dict, run: dict, seat: int) -> dict:
    """Build explicit formatting values; this dictionary is never an agent prompt.

    Real/fake artist fields support a later private GO observation. They are not
    interpolated into initial headers. The source has no partner and gets an empty
    partner_name. Reliability has a listener line and no source_self value.
    """
    if type(seat) is not int or seat not in range(13):
        raise ValueError("seat must be an integer from 0 to 12")
    personas = {persona["id"]: persona for persona in config["personas"]}
    seating = run["seating_assignment"]
    persona = personas[seating[str(seat)]]
    source = personas[seating["0"]]
    partner_seat = seat + 6 if 1 <= seat <= 6 else seat - 6 if seat >= 7 else None
    values = {
        "name": persona["name"], "job": persona["occupation"],
        "style": persona["conversational_style"], "day_detail": persona["daily_detail"],
        "loved_one": persona["loved_one"], "relation": persona["relation"],
        "town": config["meta"]["town_name"],
        "budget": f"${config['meta']['initial_budget_usd']:g}",
        "source_name": source["name"],
        "partner_name": personas[seating[str(partner_seat)]]["name"] if partner_seat is not None else "",
        "table_names": ", ".join(personas[seating[str(s)]]["name"] for s in range(1, 7)),
        "intro_artist_1": config["artists"]["shared_intro_order"]["intro_artist_1"],
        "intro_artist_2": config["artists"]["shared_intro_order"]["intro_artist_2"],
        "real_artist": run["real_artist"], "fake_artist": run["fake_artist"],
        "announced_artist": run["announced_artist"],
    }
    for knob in _KNOBS:
        templates = config["experimental_knobs"][knob][run["knobs"][knob]]
        values[f"{knob}_line"] = render_template(templates["listener_line"], values)
        if knob != "reliability":
            values[f"{knob}_self"] = render_template(templates["source_self"], values)
    prompts = config["prompts_and_templates"]
    values["shared_header"] = render_template(prompts["shared_system_prompt_header"], values)
    values["scene_1_source_departure_broadcast"] = render_template(prompts["scene_1_source_departure_broadcast"], values)
    return values


def render_contexts(config: dict, run: dict) -> dict[int, str]:
    """Return the source prompt and 12 initial listener contexts by seat.

    The first-hand announcement is a later Scene 1 event. Neither listener tier
    receives it in this initialization step, and second-hand listeners must only
    hear it through their catch-up partner's actual speech.
    """
    prompts = config["prompts_and_templates"]
    result = {}
    for seat in range(13):
        name = ("scene_1_source_prompt" if seat == 0 else
                "first_hand_listener_context" if seat <= 6 else "second_hand_listener_context")
        result[seat] = render_template(prompts[name], render_values(config, run, seat))
    return result
