"""Bind an existing blind human panel to exact saved phone identities, offline."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from .contracts import clone, digest
from .deferred_judging import plan_judging


def panel_profile(source_roots, profile: dict, panel_path: Path, profile_id: str) -> tuple[dict, dict]:
    """Create an unapproved candidate for the same cases human raters received.

    Human/machine labels and notes are never used for selection. Both the opaque
    validation ID and exact shown transcript/target must match the audited source.
    """
    candidate = clone(profile)
    candidate["selection"] = None
    candidate["profile_id"] = profile_id
    candidate["approved"] = False
    candidate["population_approved"] = False
    candidate["provider_manifest"]["approved"] = False
    info = plan_judging(source_roots, candidate)
    available = {}
    for item in info["items"]:
        identity = digest({"run_id": item["run_id"], "seat_id": item["seat_id_private"],
                           "target_artist": item["target_artist"], "phone": item["phone_transcript"]})
        if identity in available:
            raise ValueError("duplicate human-panel identity in source")
        available[identity] = item
    panel_bytes = Path(panel_path).read_bytes()
    with Path(panel_path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not {"validation_id", "target_artist", "transcript"} <= set(reader.fieldnames or []):
            raise ValueError("human panel needs validation_id, target_artist and transcript columns")
        rows = list(reader)
    if not rows:
        raise ValueError("human panel is empty")
    chosen = set()
    for row in rows:
        identity = row["validation_id"]
        if identity in chosen or identity not in available:
            raise ValueError("duplicate or foreign human-panel case identity")
        chosen.add(identity)
        item = available[identity]
        shown = "\n".join(f"{line['speaker']}: {line['text']}" for line in item["phone_transcript"])
        if row["target_artist"] != item["target_artist"] or row["transcript"] != shown:
            raise ValueError("human-panel target or shown transcript differs from saved source")
    selected_ids = {available[key]["item_id"] for key in chosen}
    selected = [item for item in info["items"] if item["item_id"] in selected_ids]
    candidate["selection"] = {"version": 1, "approved": False,
        "source_sha256": info["source_sha256"], "item_ids": sorted(selected_ids),
        "items_sha256": digest(selected)}
    if Path(panel_path).read_bytes() != panel_bytes:
        raise ValueError("human panel changed during preparation")
    return candidate, {"status": "prepared_unapproved", "selected_phone_outcomes": len(selected),
        "source_phone_outcomes": len(info["items"]), "source_sha256": info["source_sha256"],
        "panel_sha256": hashlib.sha256(panel_bytes).hexdigest(), "profile_sha256": digest(candidate),
        "labels_used_for_selection": False, "provider_api_calls": 0, "study_eligible": False}
