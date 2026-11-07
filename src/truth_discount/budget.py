"""Durable, single-owner request budget; not a provider-side billing limit.

The ledger is an append-only JSON Lines journal. Its first line fixes the cap;
every reserve, settle, interrupt or reconcile event is then appended and
fsynced, and nothing earlier is ever rewritten. Reopening replays the journal,
so reservations, earlier spending and the cap all survive a crash.

Reserve before sending. A timeout or a process exit with a pending request can
have incurred a charge: those reservations stay held and block new calls until
an operator records the billed amount with reconcile(). Constructing a new
ledger never clears an unresolved charge or changes its cap.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import threading
import uuid
from typing import Any


class BudgetError(ValueError):
    pass


class BudgetExceeded(BudgetError):
    pass


class BudgetBlocked(BudgetError):
    pass


class LedgerLocked(BudgetError):
    pass


def money(value: Any, name: str = "amount") -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise BudgetError(f"{name} must be a finite nonnegative number")
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise BudgetError(f"{name} must be a finite nonnegative number") from None
    if not result.is_finite() or result < 0:
        raise BudgetError(f"{name} must be a finite nonnegative number")
    return result


LEDGER_VERSION = 2
_META = {"model_key", "provider", "model_id", "request_sha256", "pricing_sha256",
         "attempt_index", "input_token_bound", "max_output_tokens", "evidence_kind"}
_RECEIPT = {"actual_provider", "actual_model", "request_id", "provider_api_calls",
            "input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens",
            "cost_usd", "cost_status", "pricing_sha256", "execution_mode", "error_code",
            "http_status", "cache_creation_input_tokens", "cache_usage"}
_INTERRUPTED = {"cost_status": "unknown", "error_code": "interrupted_request"}


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) > 256 or any(ord(c) < 32 for c in value):
        raise BudgetError(f"invalid {name}")
    return value


def _safe_record(value: dict, allowed: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) - allowed:
        raise BudgetError("unsupported ledger metadata or receipt field")
    result = {}
    for key, item in value.items():
        if item is not None and not isinstance(item, (str, int, float, bool)):
            raise BudgetError("ledger records accept scalar values only")
        if isinstance(item, str):
            _text(item, "ledger string")
        if isinstance(item, float) and not money(abs(item)).is_finite():
            raise BudgetError("invalid ledger number")
        result[key] = item
    return result


def _identifier(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 32 or any(c not in "0123456789abcdef" for c in value):
        raise BudgetError("invalid reservation id")
    return value


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise BudgetError("duplicate ledger JSON key")
        value[key] = item
    return value


def _parse(line: bytes) -> Any:
    def reject(_):
        raise BudgetError("invalid ledger number")
    try:
        return json.loads(line, object_pairs_hook=_unique_object, parse_constant=reject)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BudgetError("invalid ledger JSON") from None


def _encode(event: dict) -> bytes:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"


class BudgetLedger:
    """One process owns a ledger; multiple threads may reserve concurrently."""

    def __init__(self, path: str | Path, limit_usd: Any):
        self.path = Path(path)
        self.limit = money(limit_usd, "limit_usd")
        self._mutex = threading.RLock()
        self._closed = False
        self._io_failed = False
        self._lock = None
        self._stream = None
        self._rows: dict[str, dict] = {}
        self._unknown: dict[str, str] = {}   # reservation id -> block reason
        self._settled = Decimal(0)
        self._held = Decimal(0)
        self._exceeded = False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # A stable, separate lock file guards the journal against a second owner.
            self._lock = open(str(self.path) + ".lock", "a+b")
            if os.name == "nt":
                import msvcrt
                self._lock.seek(0)
                if not self._lock.read(1):
                    self._lock.write(b"\0")
                    self._lock.flush()
                self._lock.seek(0)
                msvcrt.locking(self._lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            if self._lock is not None:
                self._lock.close()
            self._closed = True
            raise LedgerLocked("budget ledger is already in use or cannot be locked") from None
        try:
            self._load()
        except BaseException:
            self.close()
            raise

    def _load(self):
        created = not self.path.exists()
        descriptor = os.open(self.path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o600)
        self._stream = os.fdopen(descriptor, "r+b")
        raw = self._stream.read()
        *complete, tail = raw.split(b"\n")
        if not complete:
            # Nothing was ever acknowledged: an empty file or a torn header.
            if tail.strip():
                try:
                    legacy = _parse(tail)
                except BudgetError:
                    legacy = None
                if isinstance(legacy, dict) and "reservations" in legacy:
                    raise BudgetError("old single-file ledger format; keep it and start a new ledger path")
            self._stream.seek(0)
            self._stream.truncate()
            self._append({"type": "header", "version": LEDGER_VERSION, "limit_usd": str(self.limit)})
            if created and os.name != "nt":
                directory = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
            return
        header = _parse(complete[0])
        if (not isinstance(header, dict) or set(header) != {"type", "version", "limit_usd"}
                or header["type"] != "header" or header["version"] != LEDGER_VERSION):
            raise BudgetError("invalid ledger header")
        if money(header["limit_usd"], "limit_usd") != self.limit:
            raise BudgetError("existing ledger cap cannot be changed")
        for number, line in enumerate(complete[1:], start=2):
            try:
                self._apply(_parse(line))
            except BudgetError as error:
                raise BudgetError(f"invalid ledger event at line {number}: {error}") from None
        if tail:
            # Only the final append can be torn. It was never acknowledged, so no
            # request was sent on its strength; dropping it errs toward holding money.
            self._stream.seek(len(raw) - len(tail))
            self._stream.truncate()
        self._stream.seek(0, os.SEEK_END)
        pending = sorted(i for i, row in self._rows.items() if row["status"] == "pending")
        if pending:
            self._apply({"type": "interrupt", "ids": pending}, write=True)

    def _append(self, event: dict) -> None:
        if self._io_failed:
            raise BudgetBlocked("ledger storage failed earlier; reopen the ledger to recover")
        line = _encode(event)
        try:
            self._stream.write(line)
            self._stream.flush()
            os.fsync(self._stream.fileno())
        except BaseException:
            self._io_failed = True
            raise

    def _apply(self, event: Any, *, write: bool = False) -> dict | None:
        """Validate one event, optionally append it durably, then update state."""
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise BudgetError("invalid ledger event")
        kind = event["type"]
        fields = {"reserve": {"type", "id", "reserved_usd", "metadata"},
                  "settle": {"type", "id", "actual_usd", "receipt"},
                  "interrupt": {"type", "ids"},
                  "reconcile": {"type", "id", "actual_usd", "note"}}.get(kind)
        if fields is None or set(event) != fields:
            raise BudgetError("invalid ledger event schema")
        if kind == "interrupt":
            ids = event["ids"]
            if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids):
                raise BudgetError("invalid interrupted reservations")
            for identifier in ids:
                row = self._rows.get(_identifier(identifier))
                if row is None or row["status"] != "pending":
                    raise BudgetError("interrupt names a reservation that is not pending")
            if write:
                self._append(event)
            for identifier in ids:
                self._rows[identifier].update(status="unknown", receipt=dict(_INTERRUPTED))
                self._unknown[identifier] = "interrupted_request"
            return None
        identifier = _identifier(event["id"])
        row = self._rows.get(identifier)
        if kind == "reserve":
            if row is not None:
                raise BudgetError("duplicate reservation id")
            amount = money(event["reserved_usd"])
            metadata = _safe_record(event["metadata"], _META)
            if write:
                self._append(event)
            row = {"id": identifier, "reserved_usd": amount, "actual_usd": None,
                   "status": "pending", "metadata": metadata, "receipt": {}}
            self._rows[identifier] = row
            self._held += amount
            return row
        actual = None if event["actual_usd"] is None else money(event["actual_usd"], "actual_cost")
        if kind == "settle":
            if row is None or row["status"] != "pending":
                raise BudgetError("reservation missing or already settled; reconcile unknown charges separately")
            receipt = _safe_record(event["receipt"], _RECEIPT)
        else:
            if row is None or row["status"] != "unknown":
                raise BudgetError("only an unknown charge can be reconciled")
            if actual is None:
                raise BudgetError("reconciliation needs the billed amount")
            note = _text(event["note"], "reconciliation note")
        if write:
            self._append(event)
        if kind == "reconcile":
            row["reconciliation"] = {"actual_usd": actual, "note": note,
                                     "reason": self._unknown.pop(identifier)}
        else:
            row["receipt"] = receipt
        if actual is None:
            row["status"] = "unknown"
            self._unknown[identifier] = "unknown_charge"
            return row
        row.update(status="settled", actual_usd=actual)
        self._held -= row["reserved_usd"]
        self._settled += actual
        if actual > row["reserved_usd"]:
            self._exceeded = True
        return row

    def _open(self):
        if self._closed:
            raise BudgetError("budget ledger is closed")

    def _block_reasons(self) -> list[str]:
        reasons = set(self._unknown.values())
        if self._exceeded:
            reasons.add("reservation_exceeded")
        if self._settled + self._held > self.limit:
            reasons.add("limit_exceeded")
        return sorted(reasons)

    def reserve(self, amount_usd: Any, metadata: dict | None = None) -> str:
        amount = money(amount_usd)
        metadata = _safe_record(metadata or {}, _META)
        with self._mutex:
            self._open()
            if self._io_failed or self._block_reasons():
                raise BudgetBlocked("unresolved charge or budget overrun blocks requests")
            if self._settled + self._held + amount > self.limit:
                raise BudgetExceeded("insufficient unreserved budget")
            identifier = uuid.uuid4().hex
            self._apply({"type": "reserve", "id": identifier, "reserved_usd": str(amount),
                         "metadata": metadata}, write=True)
            return identifier

    def settle(self, reservation_id: str, actual_cost: Any | None, receipt: dict | None = None) -> None:
        actual = None if actual_cost is None else money(actual_cost, "actual_cost")
        receipt = _safe_record(receipt or {}, _RECEIPT)
        with self._mutex:
            self._open()
            row = self._apply({"type": "settle", "id": reservation_id,
                               "actual_usd": None if actual is None else str(actual),
                               "receipt": receipt}, write=True)
            if actual is not None and actual > row["reserved_usd"]:
                raise BudgetExceeded("actual charge exceeded its reservation; further requests blocked")

    def reconcile(self, reservation_id: str, actual_cost: Any, note: str) -> dict:
        """Record the billed amount for an unknown charge, e.g. from the provider dashboard."""
        actual = money(actual_cost, "actual_cost")
        with self._mutex:
            self._open()
            self._apply({"type": "reconcile", "id": reservation_id, "actual_usd": str(actual),
                         "note": note}, write=True)
            return self.summary()

    def unknown_reservations(self) -> list[dict]:
        with self._mutex:
            self._open()
            return [{"id": i, "reason": reason, "reserved_usd": float(self._rows[i]["reserved_usd"]),
                     "metadata": dict(self._rows[i]["metadata"]),
                     "receipt": dict(self._rows[i]["receipt"])}
                    for i, reason in sorted(self._unknown.items())]

    def summary(self) -> dict:
        with self._mutex:
            self._open()
            reasons = self._block_reasons()
            return {"limit_usd": float(self.limit), "settled_usd": float(self._settled),
                    "reserved_usd": float(self._held),
                    "available_usd": float(max(Decimal(0), self.limit - self._settled - self._held)),
                    "blocked": self._io_failed or bool(reasons),
                    "block_reasons": reasons + (["storage_failure"] if self._io_failed else []),
                    "reservation_count": len(self._rows), "unknown_count": len(self._unknown),
                    "reconciled_count": sum("reconciliation" in r for r in self._rows.values())}

    def close(self):
        with self._mutex:
            if not self._closed:
                self._closed = True
                for handle in (self._stream, self._lock):
                    if handle is not None:
                        handle.close()

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, *args):
        self.close()
