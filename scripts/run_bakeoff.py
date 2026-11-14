"""Rebuild the historical judge bake-off report from saved local predictions."""

import argparse
import csv
import json
import math
from pathlib import Path

OUTPUTS = Path(__file__).resolve().parents[1] / "outputs"
SAMPLE_JSON = OUTPUTS / "calibration_sample_100.json"
HUMAN_LABELS_CSV = OUTPUTS / "human_labels_100.csv"
PREDICTIONS_CACHE = OUTPUTS / "bakeoff_predictions.json"
REPORT_MD = OUTPUTS / "BAKE_OFF_REPORT.md"


def compute_kappa(y_true, y_pred):
    categories = sorted(set(y_true) | set(y_pred))
    if not y_true:
        return None
    c_to_i = {c: i for i, c in enumerate(categories)}
    n = len(y_true)
    matrix = [[0] * len(categories) for _ in categories]
    for a, b in zip(y_true, y_pred):
        matrix[c_to_i[a]][c_to_i[b]] += 1
    p_o = sum(matrix[i][i] for i in range(len(categories))) / n
    p_e = sum(
        sum(matrix[i][j] for j in range(len(categories))) * sum(matrix[j][i] for j in range(len(categories)))
        for i in range(len(categories))
    ) / (n * n)
    if p_e >= 1.0:
        return None
    return (p_o - p_e) / (1.0 - p_e)


def load_inputs():
    items = json.loads(SAMPLE_JSON.read_text(encoding="utf-8"))
    item_ids = {item["id"] for item in items}
    if not items or len(item_ids) != len(items) or not all(isinstance(item_id, str) for item_id in item_ids):
        raise ValueError("invalid sample item IDs")

    human_labels = {}
    if HUMAN_LABELS_CSV.is_file():
        label_ids = set()
        with HUMAN_LABELS_CSV.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                item_id = row["item_id"]
                if item_id not in item_ids or item_id in label_ids:
                    raise ValueError("unmatched or duplicate human label")
                label_ids.add(item_id)
                if row.get("human_label"):
                    human_labels[item_id] = row["human_label"]

    cache = json.loads(PREDICTIONS_CACHE.read_text(encoding="utf-8"))
    evaluations, costs = cache["evaluations"], cache.get("costs", {})
    if not isinstance(evaluations, dict) or not evaluations or not isinstance(costs, dict):
        raise ValueError("invalid saved model evaluations or costs")
    for rows in evaluations.values():
        if not isinstance(rows, list) or not rows:
            raise ValueError("empty or invalid saved evaluation")
        evaluated_ids = {row["item_id"] for row in rows}
        if len(evaluated_ids) != len(rows) or evaluated_ids != item_ids:
            raise ValueError("missing, unmatched or duplicate saved evaluation")
        if not all(isinstance(row["status"], str) and isinstance(row["label"], str) for row in rows):
            raise ValueError("invalid saved evaluation row")
    return items, human_labels, evaluations, costs


def render_report(items, human_labels, evaluations, costs):
    report = [
        "# Judge Model Bake-Off Report",
        "",
        "**Original run date** 14 November 2026",
        f"**Sample size** {len(items)} calls from the supplied bake-off sample",
        f"**Human labels available** {len(human_labels)}",
        "**Original parser** `quote-normalized-v1`",
        "",
        "| Model | Valid labels | Malformed or unavailable | Agreement with human labels | Cohen's κ | Historical cost record |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for model, rows in evaluations.items():
        valid = sum(row["status"] == "valid" for row in rows)
        agreement = [(human_labels[row["item_id"]], row["label"]) for row in rows if row["item_id"] in human_labels]
        comparison = kappa = "Unavailable"
        if agreement:
            agreed = sum(human == predicted for human, predicted in agreement)
            comparison = f"{agreed / len(agreement):.1%} ({agreed}/{len(agreement)})"
            coefficient = compute_kappa(*zip(*agreement))
            if coefficient is not None:
                kappa = f"{coefficient:.3f}"
        cost = costs.get(model)
        cost_record = "Unavailable"
        if type(cost) in {int, float} and math.isfinite(cost) and cost > 0:
            subtotal = "<$0.0001" if cost < 0.0001 else f"${cost:.4f}"
            cost_record = f"{subtotal} (unverified recorded subtotal)"
        unavailable = (len(rows) - valid) / len(rows)
        report.append(f"| **{model}** | {valid}/{len(rows)} | {unavailable:.1%} | {comparison} | {kappa} | {cost_record} |")
    report.extend([
        "",
        "The original tool calculated cost at the rates it used and could record provider failures at zero. "
        "Saved costs are historical subtotals. Current pricing and actual billed spend require provider usage evidence.",
        "",
        "The historical selection rule favored the cheapest judge within 0.05 κ of the best result, with ties favoring Haiku.",
        "",
    ])
    return "\n".join(report)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--no-cache", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.no_cache:
        parser.error("This script only replays saved predictions. Use the separately authorized judge-saved command for new calls.")
    if not PREDICTIONS_CACHE.is_file():
        parser.error("Missing outputs/bakeoff_predictions.json. Restore the saved predictions to rebuild the historical report.")
    if not SAMPLE_JSON.is_file():
        parser.error("Missing outputs/calibration_sample_100.json. Restore the sample used to produce the saved predictions.")
    if REPORT_MD.is_symlink():
        parser.error("The report path outputs/BAKE_OFF_REPORT.md must not be a symbolic link.")
    try:
        report = render_report(*load_inputs())
        REPORT_MD.write_text(report, encoding="utf-8")
    except (OSError, TypeError, ValueError, KeyError, OverflowError):
        parser.error("Could not rebuild the report from the saved outputs. Check the sample, labels and predictions.")
    print("Report written to outputs/BAKE_OFF_REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
