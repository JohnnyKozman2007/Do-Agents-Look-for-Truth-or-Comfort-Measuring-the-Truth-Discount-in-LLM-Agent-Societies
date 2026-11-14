"""Keep a collection going through provider busy spells and isolated unclear charges.

DeepInfra sometimes turns requests away for a minute or more ("engine_overloaded" or a plain
"Rate limited" 429). Those rejections are free and leave the ledger unblocked, but once a call
has used all its retries the run stops. This wrapper waits, then resumes, and repeats.

A dropped connection or timeout leaves an unclear charge that blocks the ledger by design.
With --auto-reconcile, the wrapper may use scripts/reconcile_unknowns.py to recover an audited
priced receipt. A timeout or missing priced receipt stays unknown and stops recovery. A reserved
amount is not a verified charge. Without the flag, unknown charges always require a person.
Auto-reconciliation also requires --execute, --spending-authorized and explicit output, ledger
and ceiling arguments. It never supplies spending authority or increases that ceiling.

It stops for good on success, on a budget overrun, on the same failure twice in a row with no new
towns saved, or after MAX_ROUNDS rounds.

Example after separate execution approval, using a $20 illustration rather than an authorization.
The arguments are those of `truth_discount.cli live`, without --resume. Every resumed partial
town may repeat previously paid calls. All attempts retain the same ledger and ceiling.

    python scripts/run_until_done.py --auto-reconcile --providers configs/providers.pilot.json \
        --output outputs/pilot --ledger outputs/ledgers/team.jsonl --budget-usd 20 --execute \
        --spending-authorized --full-pilot --start-pair 1 --max-concurrent-towns 8

With --simulate the wrapper drives `truth_discount.cli simulate` instead, using the same
arguments as that command. A town that ends incomplete (timeout or malformed reply) stops a
simulate run; when the ledger is not blocked, the wrapper resumes after a short wait. Sealed
failed towns are rerun only if --regenerate-failed is among the forwarded arguments, which keeps
that choice explicit and logged. Example for one shard, after separate execution approval:

    python scripts/run_until_done.py --simulate --auto-reconcile --config configs/main_config.json \
        --providers local/providers.actor.json --all-pairs --shard-count 6 --shard-index 0 \
        --output outputs/main-owner-0 --ledger outputs/ledgers/main-owner-0.jsonl --budget-usd 10 \
        --max-concurrent-towns 6 --regenerate-failed --execute --spending-authorized
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
BUSY = "provider rejected every attempt before inference"
WAIT_SECONDS = 120
MAX_ROUNDS = 60
MAX_AUTO_RECONCILES = 30
UNKNOWN_RECOVERY_ERRORS = ("budget ledger is blocked", "provider request failed; consult the sanitized receipt",
                           "budget does not permit this request")
INCOMPLETE = "simulation collection stopped after incomplete town"


def log(message: str) -> None:
    print(f"{datetime.now():%H:%M:%S} {message}", flush=True)


def value(args: list[str], flag: str) -> str | None:
    """Read a unique option without disagreeing with argparse's last-value rule."""
    found = []
    for index, argument in enumerate(args):
        if argument == flag:
            if index + 1 == len(args) or args[index + 1].startswith("--"):
                raise ValueError(f"{flag} requires a value")
            found.append(args[index + 1])
        elif argument.startswith(flag + "="):
            found.append(argument.partition("=")[2])
    if len(found) > 1:
        raise ValueError(f"{flag} must be supplied only once")
    if found and not found[0]:
        raise ValueError(f"{flag} requires a nonempty value")
    return found[0] if found else None


def repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def towns_saved(output: Path | None) -> int:
    return len(list(output.glob("*/manifest.json"))) if output and output.exists() else 0


def ledger_state(env: dict, ledger: str, cap: str) -> dict:
    # Opening BudgetLedger can append interrupted-request events. Inspect a
    # byte-for-byte copy so status reads cannot reconcile or heal the original.
    path = repo_path(ledger)
    if not path.is_file():
        return {"blocked": True, "block_reasons": ["ledger_missing"]}
    try:
        before = path.read_bytes()
        if not before.endswith(b"\n"):
            return {"blocked": True, "block_reasons": ["ledger_incomplete"]}
        with tempfile.TemporaryDirectory(prefix="pilot-ledger-inspection-") as temporary:
            snapshot = Path(temporary) / "ledger.jsonl"
            snapshot.write_bytes(before)
            proc = subprocess.run([sys.executable, "-m", "truth_discount.cli", "ledger", "--ledger", str(snapshot),
                                   "--budget-usd", cap], cwd=REPO, env=env, capture_output=True,
                                  text=True, encoding="utf-8")
        if path.read_bytes() != before:
            return {"blocked": True, "block_reasons": ["ledger_changed_during_inspection"]}
        state = json.loads(proc.stdout)["budget"] if proc.returncode == 0 else None
    except (OSError, ValueError, KeyError, TypeError):
        state = None
    return state if isinstance(state, dict) else {"blocked": True, "block_reasons": ["unreadable"]}


def main() -> int:
    auto = "--auto-reconcile" in sys.argv
    simulate = "--simulate" in sys.argv
    command = "simulate" if simulate else "live"
    args = [a for a in sys.argv[1:] if a not in ("--resume", "--auto-reconcile", "--simulate")]
    try:
        if "--" in args:
            raise ValueError(f"the recovery wrapper accepts {command} options only, without a -- positional separator")
        output_arg = value(args, "--output")
        ledger, cap = value(args, "--ledger"), value(args, "--budget-usd")
        if auto:
            if not ("--execute" in args and "--spending-authorized" in args and output_arg and ledger and cap):
                raise ValueError("--auto-reconcile requires --execute and --spending-authorized, "
                                 "plus --output, --ledger and --budget-usd")
            try:
                ceiling = Decimal(cap)
            except InvalidOperation:
                raise ValueError("--budget-usd must be a positive finite ceiling") from None
            if not ceiling.is_finite() or ceiling <= 0:
                raise ValueError("--budget-usd must be a positive finite ceiling")
    except ValueError as error:
        print("error: " + str(error), file=sys.stderr)
        return 2
    # All auto-reconciliation authority checks precede filesystem inspection,
    # environment forwarding and every subprocess.
    output = repo_path(output_arg) if output_arg else None
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    if simulate and "--execute" in args and "--regenerate-failed" not in args:
        log("note: without --regenerate-failed, the first sealed failed town stops this wrapper")
    reconciles, last_failure = 0, None
    for round_number in range(1, MAX_ROUNDS + 1):
        resume = ["--resume"] if output is not None and (output / "execution_plan.json").exists() else []
        before = towns_saved(output)
        log(f"round {round_number}{' (resume)' if resume else ''}; towns saved so far: {before}")
        proc = subprocess.run([sys.executable, "-m", "truth_discount.cli", command, *args, *resume],
                              cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8")
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.stdout.flush()
        if proc.returncode == 0:
            log("finished")
            return 0
        if proc.returncode == 2:
            log(f"invalid {command} command arguments; not inspecting or reconciling the ledger")
            return proc.returncode
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
        incomplete = simulate and INCOMPLETE in proc.stderr
        if incomplete and ledger and cap and not ledger_state(env, ledger, cap).get("blocked"):
            # No unclear charge: the town is sealed as failed; resume archives and reruns
            # it only when --regenerate-failed was forwarded.
            log("a town ended incomplete with no unclear charge; resuming in 30s")
            time.sleep(30)
            continue
        if not auto or not (incomplete or any(message in proc.stderr for message in UNKNOWN_RECOVERY_ERRORS)):
            log("stopped for a reason other than a busy provider; not retrying")
            return proc.returncode
        state = ledger_state(env, ledger, cap)
        reasons = set(state.get("block_reasons", []))
        if not state.get("blocked"):
            log("ledger not blocked; this error does not authorize automatic recovery")
            return proc.returncode
        if not reasons or not reasons <= {"unknown_charge", "interrupted_request"}:
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
