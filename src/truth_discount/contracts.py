from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
from decimal import Decimal
from typing import Any, Protocol


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def clone(value: Any) -> Any:
    return json.loads(canonical_bytes(value))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def capture(value: Any, limit: int = 8192) -> dict[str, Any]:
    try:
        if is_dataclass(value) and not isinstance(value, type):
            value = asdict(value)
        text = json.dumps(value, ensure_ascii=True, default=lambda x: {"python_type": type(x).__name__})
    except (TypeError, ValueError, RecursionError) as exc:
        text = json.dumps({"python_type": type(value).__name__, "capture_error": type(exc).__name__})
    return {"text": text[:limit], "truncated": len(text) > limit,
            "sha256": hashlib.sha256(text.encode()).hexdigest()}


@dataclass(frozen=True)
class GenerationRequest:
    messages: list[dict[str, str]]
    settings: dict[str, Any]
    model_key: str
    kind: str
    scene: int
    seat: int | None
    turn: int


@dataclass(frozen=True)
class GenerationResponse:
    text: str
    usage: dict[str, Any] | None = None


class Backend(Protocol):
    evidence_kind: str
    async def generate(self, request: GenerationRequest) -> GenerationResponse: ...


class MalformedGeneration(ValueError):
    pass


def usage_totals(calls: list[dict[str, Any]], evidence_kind: str) -> dict[str, Any]:
    """Keep actual submissions, mocked submissions and unknown charges distinct."""
    if evidence_kind == "synthetic_fixture":
        return {"provider_api_calls": 0, "input_tokens": None, "output_tokens": None,
                "cost_usd": None, "fixture_callback_invocations": len(calls)}
    receipts = [call.get("token_usage") for call in calls]
    def total(key: str):
        values = [r.get(key) if isinstance(r, dict) else None for r in receipts]
        if any(v is None for v in values):
            return None
        if any(isinstance(v, bool) or not isinstance(v, (int, float, str)) for v in values):
            raise ValueError("invalid usage total")
        result = sum((Decimal(str(v)) for v in values), Decimal(0))
        if not result.is_finite() or result < 0:
            raise ValueError("invalid usage total")
        return float(result) if key == "cost_usd" else int(result)
    attempts = sum(call.get("provider_api_calls", 0) for call in calls)
    return {"provider_api_calls": attempts if evidence_kind == "development_pilot" else 0,
            "simulated_provider_requests": attempts if evidence_kind == "mocked_provider" else 0,
            "provider_request_attempts": attempts, "fixture_callback_invocations": 0,
            "input_tokens": total("input_tokens"), "output_tokens": total("output_tokens"),
            "cost_usd": total("cost_usd"),
            "cost_status": "known" if total("cost_usd") is not None else "unknown"}
