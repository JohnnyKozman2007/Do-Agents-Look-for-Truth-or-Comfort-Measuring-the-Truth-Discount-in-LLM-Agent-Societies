"""Keep a collection going through provider busy spells.

DeepInfra sometimes turns requests away for a minute or more ("engine_overloaded"). Those
rejections are free and leave the ledger unblocked, but once a call has used all its retries
the run stops. This wrapper waits, then resumes, and repeats. It stops for good on success or
on any other error (for example an unclear charge, which needs reconciling first).

Usage, from the repo folder, with the API keys in the environment; the arguments are those of
`truth_discount.cli live`, without --resume:

    python scripts/run_until_done.py --providers configs/providers.pilot.json --output outputs/pilot \
        --ledger outputs/ledgers/team.jsonl --budget-usd 200 --execute --spending-authorized \
        --full-pilot --start-pair 1 --max-concurrent-towns 8
"""
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
BUSY = "provider rejected every attempt before inference"
WAIT_SECONDS = 120
MAX_ROUNDS = 40


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--resume"]
    output = Path(args[args.index("--output") + 1]) if "--output" in args else None
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    for round_number in range(1, MAX_ROUNDS + 1):
        resume = ["--resume"] if output is not None and (output / "execution_plan.json").exists() else []
        print(f"{datetime.now():%H:%M:%S} round {round_number}{' (resume)' if resume else ''}", flush=True)
        proc = subprocess.run([sys.executable, "-m", "truth_discount.cli", "live", *args, *resume],
                              cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8")
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.stdout.flush()
        if proc.returncode == 0:
            print(f"{datetime.now():%H:%M:%S} finished", flush=True)
            return 0
        if BUSY not in proc.stderr:
            print(f"{datetime.now():%H:%M:%S} stopped for a reason other than a busy provider; not retrying",
                  flush=True)
            return proc.returncode
        print(f"{datetime.now():%H:%M:%S} provider busy; resuming in {WAIT_SECONDS}s", flush=True)
        time.sleep(WAIT_SECONDS)
    print("gave up after", MAX_ROUNDS, "rounds", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
