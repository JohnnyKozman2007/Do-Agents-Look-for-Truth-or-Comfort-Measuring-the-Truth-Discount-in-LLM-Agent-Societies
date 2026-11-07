"""Record every held (unknown) charge in the team ledger, using the saved receipts.

Usage, from the repo folder, after a run stops and before resuming:
    python scripts/reconcile_unknowns.py outputs/ledgers/team.jsonl 200 outputs/pilot          # preview
    python scripts/reconcile_unknowns.py outputs/ledgers/team.jsonl 200 outputs/pilot --apply  # record

A charge whose saved receipt was priced from the provider's reported usage is recorded at that cost.
A charge with no priced receipt (timeout, dropped connection, crash) is recorded at its reserved
amount, which is the most that request could have cost; the note says it is an upper bound.
"""
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from truth_discount.budget import BudgetLedger  # noqa: E402

args = [a for a in sys.argv[1:] if a != "--apply"]
apply = "--apply" in sys.argv
ledger_path, cap, outputs = Path(args[0]), args[1], [Path(a) for a in args[2:]]

receipts = {}
for output in outputs:
    for town_file in list(output.glob("*/town.json")) + list(output.glob("_incomplete/*/*/town.json")):
        town = json.loads(town_file.read_text(encoding="utf-8"))
        for call in town["calls"]:
            receipt = call.get("token_usage") or {}
            for attempt in receipt.get("attempts", []):
                if "reservation_id" in attempt:
                    receipts[attempt["reservation_id"]] = (town["run_id"], call, receipt)

with BudgetLedger(ledger_path, cap) as ledger:
    unknown = ledger.unknown_reservations()
    print(f"{len(unknown)} held charge(s)")
    total = 0.0
    for row in unknown:
        found = receipts.get(row["id"])
        if found and found[2].get("cost_status") == "calculated_from_usage" and found[2].get("cost_usd") is not None:
            run_id, call, receipt = found
            amount = receipt["cost_usd"]
            note = (f"{run_id} scene {call['scene']} seat {call['seat_id']} {call['kind']}: priced from reported usage "
                    f"({receipt['input_tokens']} in, {receipt['cached_input_tokens']} cached, {receipt['output_tokens']} out)")
        else:
            amount = row["reserved_usd"]
            where = f"{found[0]} " if found else ""
            note = f"{where}{row['reason']}: no priced receipt; reserved amount recorded as an upper bound"
        total += amount
        print(f"  {row['id']}  ${amount:.8f}  {note[:150]}")
        if apply:
            ledger.reconcile(row["id"], f"{amount:.10f}".rstrip("0"), note[:256])
    print(f"total ${total:.8f}", "recorded" if apply else "(preview only; add --apply to record)")
    summary = ledger.summary()
    print("ledger:", json.dumps({k: summary[k] for k in ("blocked", "block_reasons", "unknown_count", "settled_usd")}))
