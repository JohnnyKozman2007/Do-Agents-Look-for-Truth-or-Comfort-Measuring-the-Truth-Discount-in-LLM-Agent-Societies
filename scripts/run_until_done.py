"""Keep a collection going through provider busy spells and isolated unclear charges.

DeepInfra sometimes turns requests away for a minute or more ("engine_overloaded"). Those
rejections are free and leave the ledger unblocked, but once a call has used all its retries
the run stops. This wrapper waits, then resumes, and repeats.

A dropped connection or timeout leaves an unclear charge that blocks the ledger by design.
With --auto-reconcile, the wrapper records each such charge the way an operator would, using
scripts/reconcile_unknowns.py: the exact cost from a saved receipt when there is one, otherwise
the reserved amount as a noted upper bound (never zero), and then resumes. Without the flag it
stops and leaves that step to a person.

It stops for good on success, on a budget overrun, on the same failure twice in a row with no new
towns saved, or after MAX_ROUNDS rounds.

Usage, from the repo folder, with the API keys in the environment; the arguments are those of
`truth_discount.cli live`, without --resume:

    python scripts/run_until_done.py --auto-reconcile --providers configs/providers.pilot.json \
        --output outputs/pilot --ledger outputs/ledgers/team.jsonl --budget-usd 200 --execute \
        --spending-authorized --full-pilot --start-pair 1 --max-concurrent-towns 8
"""
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
BUSY = "provider rejected every attempt before inference"
WAIT_SECONDS = 120
MAX_ROUNDS = 60
MAX_AUTO_RECONCILES = 30


def log(message: str) -> None:
    print(f"{datetime.now():%H:%M:%S} {message}", flush=True)


def value(args: list[str], flag: str) -> str | None:
    return args[args.index(flag) + 1] if flag in args else None


def towns_saved(output: Path | None) -> int:
    return len(list(output.glob("*/manifest.json"))) if output and output.exists() else 0


def ledger_state(env: dict, ledger: str, cap: str) -> dict:
    proc = subprocess.run([sys.executable, "-m", "truth_discount.cli", "ledger", "--ledger", ledger,
                           "--budget-usd", cap], cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8")
    return json.loads(proc.stdout)["budget"] if proc.returncode == 0 else {"blocked": True, "block_reasons": ["unreadable"]}


def main() -> int:
    auto = "--auto-reconcile" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--resume", "--auto-reconcile")]
    output = Path(value(args, "--output")) if value(args, "--output") else None
    ledger, cap = value(args, "--ledger"), value(args, "--budget-usd")
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    reconciles, last_failure = 0, None
    for round_number in range(1, MAX_ROUNDS + 1):
        resume = ["--resume"] if output is not None and (output / "execution_plan.json").exists() else []
        before = towns_saved(output)
        log(f"round {round_number}{' (resume)' if resume else ''}; towns saved so far: {before}")
        proc = subprocess.run([sys.executable, "-m", "truth_discount.cli", "live", *args, *resume],
                              cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8")
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.stdout.flush()
        if proc.returncode == 0:
            log("finished")
            return 0
        failure = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"exit {proc.returncode}"
        progressed = towns_saved(output) > before
        if failure == last_failure and not progressed:
            log("same failure twice with no new towns; stopping for a person to look")
            return proc.returncode
        last_failure = failure
        if BUSY in proc.stderr:
            log(f"provider busy; resuming in {WAIT_SECONDS}s")
            time.sleep(WAIT_SECONDS)
            continue
        if not auto or not (ledger and cap and output):
            log("stopped for a reason other than a busy provider; not retrying")
            return proc.returncode
        state = ledger_state(env, ledger, cap)
        reasons = set(state.get("block_reasons", []))
        if not state.get("blocked"):
            log("ledger not blocked; resuming in 30s")
            time.sleep(30)
            continue
        if not reasons <= {"unknown_charge", "interrupted_request"}:
            log(f"ledger blocked for {sorted(reasons)}; that needs a person, stopping")
            return proc.returncode
        if reconciles >= MAX_AUTO_RECONCILES:
            log("too many unclear charges; stopping for a person to look")
            return proc.returncode
        reconciles += 1
        log(f"recording {state.get('unknown_count')} unclear charge(s) (auto-reconcile {reconciles})")
        rec = subprocess.run([sys.executable, str(REPO / "scripts" / "reconcile_unknowns.py"), ledger, cap, str(output),
                              "--apply"], cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8")
        sys.stdout.write(rec.stdout)
        sys.stderr.write(rec.stderr)
        if rec.returncode != 0 or ledger_state(env, ledger, cap).get("blocked"):
            log("could not unblock the ledger; stopping for a person to look")
            return 1
        log("resuming in 30s")
        time.sleep(30)
    log(f"gave up after {MAX_ROUNDS} rounds")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
