"""Durable, single-owner request budget; not a provider-side billing limit.

Reserve before sending. A timeout or a process exit with a pending request can
have incurred a charge: those reservations remain held and disable new calls.
Reconciliation is deliberately manual; constructing a new ledger never clears
an unresolved charge or changes its cap.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import tempfile
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


_META = {"model_key", "provider", "model_id", "request_sha256", "pricing_sha256",
         "attempt_index", "input_token_bound", "max_output_tokens", "evidence_kind"}
_RECEIPT = {"actual_provider", "actual_model", "request_id", "provider_api_calls",
            "input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens",
            "cost_usd", "cost_status", "pricing_sha256", "execution_mode", "error_code",
            "http_status", "cache_creation_input_tokens"}


def _safe_record(value: dict, allowed: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) - allowed:
        raise BudgetError("unsupported ledger metadata or receipt field")
    result = {}
    for key, item in value.items():
        if item is not None and not isinstance(item, (str, int, float, bool)):
            raise BudgetError("ledger records accept scalar values only")
        if isinstance(item, str) and (len(item) > 256 or any(ord(c) < 32 for c in item)):
            raise BudgetError("invalid ledger string")
        if isinstance(item, float) and not money(abs(item)).is_finite():
            raise BudgetError("invalid ledger number")
        result[key] = item
    return result


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise BudgetError("duplicate ledger JSON key")
        value[key] = item
    return value


class BudgetLedger:
    """One process owns a ledger; multiple threads may reserve concurrently."""

    def __init__(self, path: str | Path, limit_usd: Any):
        self.path = Path(path)
        self.limit = money(limit_usd, "limit_usd")
        self._mutex = threading.RLock()
        self._closed = False
        self._io_failed = False
        self._lock = None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # A stable, separate lock inode survives atomic ledger replacement.
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
            if self.path.exists():
                with self.path.open(encoding="utf-8") as stream:
                    self._data = json.load(stream, object_pairs_hook=_unique_object,
                                           parse_constant=lambda _: (_ for _ in ()).throw(BudgetError("invalid ledger number")))
                self._validate()
                pending = [row for row in self._data["reservations"] if row["status"] == "pending"]
                if pending:
                    for row in pending:
                        row["status"] = "unknown"
                        row["receipt"] = {"cost_status": "unknown", "error_code": "interrupted_request"}
                    self._data["block_reasons"].append("interrupted_request")
                    self._write(self._data)
            else:
                self._data = {"version": 1, "limit_usd": str(self.limit),
                              "reservations": [], "block_reasons": []}
                self._write(self._data)
        except BaseException:
            self.close()
            raise

    def _validate(self):
        data = self._data
        if not isinstance(data, dict) or set(data) != {"version", "limit_usd", "reservations", "block_reasons"} or data["version"] != 1:
            raise BudgetError("invalid ledger schema")
        if money(data["limit_usd"]) != self.limit:
            raise BudgetError("existing ledger cap cannot be changed")
        if not isinstance(data["reservations"], list) or not isinstance(data["block_reasons"], list):
            raise BudgetError("invalid ledger rows")
        if any(reason not in {"unknown_charge", "interrupted_request", "reservation_exceeded", "limit_exceeded"}
               for reason in data["block_reasons"]):
            raise BudgetError("invalid ledger block reason")
        seen = set()
        for row in data["reservations"]:
            if not isinstance(row, dict) or set(row) != {"id", "reserved_usd", "actual_usd", "status", "metadata", "receipt"}:
                raise BudgetError("invalid reservation schema")
            identifier = row["id"]
            if not isinstance(identifier, str) or len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier) or identifier in seen:
                raise BudgetError("invalid reservation id")
            seen.add(identifier)
            amount = money(row["reserved_usd"])
            if row["status"] not in {"pending", "settled", "unknown"}:
                raise BudgetError("invalid reservation status")
            if row["status"] == "settled":
                actual = money(row["actual_usd"])
                if actual > amount and "reservation_exceeded" not in data["block_reasons"]:
                    raise BudgetError("unrecorded reservation overrun")
            elif row["actual_usd"] is not None:
                raise BudgetError("unsettled reservation has an actual cost")
            _safe_record(row["metadata"], _META)
            _safe_record(row["receipt"], _RECEIPT)
        if any(row["status"] == "unknown" for row in data["reservations"]) and not data["block_reasons"]:
            raise BudgetError("unrecorded unknown charge")
        if self._totals(data)[0] + self._totals(data)[1] > self.limit and not data["block_reasons"]:
            raise BudgetError("unrecorded budget overrun")

    def _write(self, data):
        payload = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        temporary = None
        try:
            descriptor, temporary = tempfile.mkstemp(prefix=self.path.name + ".", suffix=".tmp", dir=self.path.parent)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            if os.name != "nt":
                directory = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        except BaseException:
            self._io_failed = True
            raise
        finally:
            if temporary is not None and os.path.exists(temporary):
                os.unlink(temporary)

    def _open(self):
        if self._closed:
            raise BudgetError("budget ledger is closed")

    @staticmethod
    def _totals(data):
        settled = sum((money(r["actual_usd"]) for r in data["reservations"] if r["status"] == "settled"), Decimal(0))
        held = sum((money(r["reserved_usd"]) for r in data["reservations"] if r["status"] != "settled"), Decimal(0))
        return settled, held

    def reserve(self, amount_usd: Any, metadata: dict | None = None) -> str:
        amount = money(amount_usd)
        metadata = _safe_record(metadata or {}, _META)
        with self._mutex:
            self._open()
            if self._io_failed or self._data["block_reasons"]:
                raise BudgetBlocked("unresolved charge or budget overrun blocks requests")
            settled, held = self._totals(self._data)
            if settled + held + amount > self.limit:
                raise BudgetExceeded("insufficient unreserved budget")
            identifier = uuid.uuid4().hex
            updated = deepcopy(self._data)
            updated["reservations"].append({"id": identifier, "reserved_usd": str(amount),
                "actual_usd": None, "status": "pending", "metadata": metadata, "receipt": {}})
            self._write(updated)
            self._data = updated
            return identifier

    def settle(self, reservation_id: str, actual_cost: Any | None, receipt: dict | None = None) -> None:
        actual = None if actual_cost is None else money(actual_cost, "actual_cost")
        receipt = _safe_record(receipt or {}, _RECEIPT)
        with self._mutex:
            self._open()
            updated = deepcopy(self._data)
            row = next((r for r in updated["reservations"] if r["id"] == reservation_id), None)
            if row is None or row["status"] != "pending":
                raise BudgetError("reservation missing or already settled; reconcile unknown charges separately")
            row.update(actual_usd=None if actual is None else str(actual),
                       status="unknown" if actual is None else "settled", receipt=receipt)
            if actual is None:
                updated["block_reasons"].append("unknown_charge")
            elif actual > money(row["reserved_usd"]):
                updated["block_reasons"].append("reservation_exceeded")
            if sum(self._totals(updated)) > self.limit:
                updated["block_reasons"].append("limit_exceeded")
            updated["block_reasons"] = sorted(set(updated["block_reasons"]))
            self._write(updated)
            self._data = updated
            if actual is not None and actual > money(row["reserved_usd"]):
                raise BudgetExceeded("actual charge exceeded its reservation; further requests blocked")

    def summary(self) -> dict:
        with self._mutex:
            self._open()
            settled, held = self._totals(self._data)
            return {"limit_usd": float(self.limit), "settled_usd": float(settled),
                    "reserved_usd": float(held), "available_usd": float(max(Decimal(0), self.limit - settled - held)),
                    "blocked": self._io_failed or bool(self._data["block_reasons"]),
                    "block_reasons": list(self._data["block_reasons"]) + (["storage_failure"] if self._io_failed else []),
                    "reservation_count": len(self._data["reservations"]),
                    "unknown_count": sum(r["status"] == "unknown" for r in self._data["reservations"])}

    def close(self):
        with self._mutex:
            if not self._closed:
                self._closed = True
                if self._lock is not None:
                    self._lock.close()

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, *args):
        self.close()
