"""Regenerate configs/main_config.json from configs/pilot_config.json.

Run after any change to the pilot config, so both studies keep identical prompts,
personas and layouts:

    PYTHONPATH=src python3 scripts/make_main_config.py
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from truth_discount.config import load_config, make_main_config  # noqa: E402

main = make_main_config(load_config(ROOT / "configs" / "pilot_config.json"))
target = ROOT / "configs" / "main_config.json"
target.write_text(json.dumps(main, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target.relative_to(ROOT)}: {len(main['cells'])} cells, "
      f"{main['meta']['total_town_runs_per_model']} towns per model; pilot cells -> main IDs "
      f"{main['pilot_cell_ids_in_main']}")
