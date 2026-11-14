"""Extract a 100-call stratified calibration sample quickly from completed towns."""
import csv
import json
from pathlib import Path
import random

SEED = 20261108
SAMPLE_PER_STRATUM = 25
POOL_TARGET = 50

SOURCE_DIR = Path(
    r"C:\Users\Sidho\OneDrive\Desktop\RESEARCH\Do Agents Look for Truth or Comfort Measuring the Truth Discount in LLM Agent Societies\outputs\main-owner-5"
)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pools = {
        ("rumor", "first_hand"): [],
        ("rumor", "second_hand"): [],
        ("truth_twin", "first_hand"): [],
        ("truth_twin", "second_hand"): [],
    }

    town_dirs = [d for d in SOURCE_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")]
    print(f"Sampling across completed towns in Shard 5...", flush=True)

    for d in town_dirs:
        if all(len(items) >= POOL_TARGET for items in pools.values()):
            break
        try:
            town_data = json.loads((d / "town.json").read_text(encoding="utf-8"))
            phone_data = json.loads((d / "phone_transcripts.json").read_text(encoding="utf-8"))
            config = json.loads((d / "config.json").read_text(encoding="utf-8"))
        except Exception:
            continue

        cond = town_data["condition_type"]
        artist = town_data["announced_artist"]
        first_seats = set(config["seating_and_pairing"]["first_hand_seats"])

        for phone in phone_data:
            seat = phone["seat_id"]
            layer = "first_hand" if seat in first_seats else "second_hand"
            key = (cond, layer)
            if key in pools and len(pools[key]) < POOL_TARGET:
                lines = phone.get("lines", [])
                transcript_text = "\n".join(f"[{turn['speaker']}]: {turn['text']}" for turn in lines)
                pools[key].append({
                    "id": f"{town_data['run_id']}_seat_{seat}",
                    "run_id": town_data["run_id"],
                    "seat_id": seat,
                    "target_artist": artist,
                    "condition_type": cond,
                    "layer": layer,
                    "transcript": transcript_text,
                    "phone_lines": lines,
                })

    rng = random.Random(SEED)
    sampled = []
    print("\nStrata sample pools:", flush=True)
    for (cond, layer), items in pools.items():
        print(f"  {cond:10s} / {layer:12s}: collected {len(items)}, sampling {SAMPLE_PER_STRATUM}", flush=True)
        sampled.extend(rng.sample(sorted(items, key=lambda x: x["id"]), SAMPLE_PER_STRATUM))

    rng.shuffle(sampled)

    sample_json_path = OUTPUT_DIR / "calibration_sample_100.json"
    sample_json_path.write_text(json.dumps(sampled, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved full sample JSON to: {sample_json_path}", flush=True)

    csv_path = OUTPUT_DIR / "human_rating_sheet.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["item_id", "target_artist", "condition", "layer", "transcript", "human_label", "human_quote"]
        )
        writer.writeheader()
        for item in sampled:
            writer.writerow({
                "item_id": item["id"],
                "target_artist": item["target_artist"],
                "condition": item["condition_type"],
                "layer": item["layer"],
                "transcript": item["transcript"],
                "human_label": "",
                "human_quote": "",
            })
    print(f"Saved blank rating sheet CSV to: {csv_path}", flush=True)
    print(f"Total calls ready for labeling: {len(sampled)}", flush=True)


if __name__ == "__main__":
    main()
