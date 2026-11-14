"""Interactive CLI for fast human labeling of the 100 calibration phone calls."""
import csv
import json
import os
from pathlib import Path
import sys

LABELS = {
    "1": "FACT",
    "2": "UNCERTAIN",
    "3": "SKEPTICAL",
    "4": "CHECKED_TRUE",
    "5": "CHECKED_FALSE",
    "6": "NOT_MENTIONED",
}

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_JSON = ROOT / "outputs" / "calibration_sample_100.json"
LABELS_CSV = ROOT / "outputs" / "human_labels_100.csv"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def load_existing():
    if not LABELS_CSV.exists():
        return {}
    existing = {}
    with open(LABELS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("human_label"):
                existing[row["item_id"]] = row
    return existing


def save_progress(items_dict):
    with open(LABELS_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["item_id", "target_artist", "condition", "layer", "transcript", "human_label", "human_quote"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items_dict.values():
            writer.writerow(item)


def main():
    if not SAMPLE_JSON.exists():
        print(f"Error: {SAMPLE_JSON} not found. Run prepare_bakeoff_sample.py first.")
        sys.exit(1)

    items = json.loads(SAMPLE_JSON.read_text(encoding="utf-8"))
    existing = load_existing()

    labeled_count = len(existing)
    print(f"Found {labeled_count}/100 existing labels.")
    print("Press Enter to start / resume labeling (type 'q' anytime to save and quit)...")
    input()

    all_data = {}
    for it in items:
        item_id = it["id"]
        if item_id in existing:
            all_data[item_id] = existing[item_id]
        else:
            all_data[item_id] = {
                "item_id": item_id,
                "target_artist": it["target_artist"],
                "condition": it["condition_type"],
                "layer": it["layer"],
                "transcript": it["transcript"],
                "human_label": "",
                "human_quote": "",
            }

    for idx, it in enumerate(items, 1):
        item_id = it["id"]
        current = all_data[item_id]
        if current.get("human_label"):
            continue

        clear_screen()
        print(f"================================================================================")
        print(f" CALL {idx} / {len(items)}  |  Stratum: {it['condition_type']} ({it['layer']})")
        print(f" Target Artist Claim: {it['target_artist']}")
        print(f"================================================================================")
        print(it["transcript"])
        print(f"--------------------------------------------------------------------------------")
        print("Choose Category:")
        print("  [1] FACT          - Believes concert is happening without doubt")
        print("  [2] UNCERTAIN     - Might happen, unsure, ambiguous, heard rumor")
        print("  [3] SKEPTICAL     - Doubts claim, calls it unverified rumor, unlikely")
        print("  [4] CHECKED_TRUE  - Physically went to noticeboard & saw confirmed")
        print("  [5] CHECKED_FALSE - Physically went to noticeboard & saw another artist")
        print("  [6] NOT_MENTIONED - Never brings up concert or dodges topic")
        print("--------------------------------------------------------------------------------")

        choice = None
        while choice not in LABELS:
            ans = input("Select [1-6] (or 'q' to quit): ").strip()
            if ans.lower() == "q":
                save_progress(all_data)
                print("\nProgress saved. Exiting.")
                return
            if ans in LABELS:
                choice = ans
            else:
                print("Invalid choice, please enter 1, 2, 3, 4, 5, or 6.")

        label = LABELS[choice]
        quote = ""

        if label != "NOT_MENTIONED":
            # Extract listener turns for reference
            listener_turns = [
                turn["text"]
                for turn in it["phone_lines"]
                if turn.get("speaker", "").lower() in {"listener", "person"}
            ]
            last_turn = listener_turns[-1] if listener_turns else ""

            print(f"\nSelected Label: {label}")
            print(f"Suggested Listener Quote (last turn):")
            print(f"  \"{last_turn}\"")
            quote_input = input("Enter quote [Press ENTER to use suggested quote, or paste exact words]: ").strip()
            if not quote_input:
                quote = last_turn
            else:
                quote = quote_input

        current["human_label"] = label
        current["human_quote"] = quote
        save_progress(all_data)

    clear_screen()
    print("================================================================================")
    print("🎉 ALL 100 CALLS LABELED! Ground truth saved to outputs/human_labels_100.csv")
    print("================================================================================")


if __name__ == "__main__":
    main()
