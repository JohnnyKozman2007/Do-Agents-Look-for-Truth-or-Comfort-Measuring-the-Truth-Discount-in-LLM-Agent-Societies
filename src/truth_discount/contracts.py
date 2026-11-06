from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
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
