"""Gated synchronous inference adapters; network is injectable for offline tests.

Primary formats: https://docs.deepinfra.com/chat/overview,
https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create,
https://platform.claude.com/docs/en/api/messages/create.

Rates and model-specific setting support are operator-verified manifest inputs,
not inferred from a model name. Calculated token charges are not invoice receipts.
The local reservation guard cannot constrain provider-side billing or other clients.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from decimal import Decimal
import inspect
import json
import os
import re
import urllib.error
import urllib.request

from .budget import BudgetError, BudgetLedger, money
from .contracts import (REJECTED_BEFORE_INFERENCE as _REJECTED_BEFORE_INFERENCE, GenerationRequest,
                        GenerationResponse, canonical_bytes, clone, digest)


class ProviderError(ValueError):
    def __init__(self, message: str, receipt: dict | None = None):
        super().__init__(message)
        self.receipt = clone(receipt or {})


@dataclass(frozen=True)
class HTTPResponse:
    status_code: int
    body: dict
    headers: dict = field(default_factory=dict)


_ENDPOINTS = {
    "DeepInfra": "https://api.deepinfra.com/v1/openai/chat/completions",
    "OpenAI": "https://api.openai.com/v1/chat/completions",
    "Anthropic": "https://api.anthropic.com/v1/messages",
}
_ROUTE_FIELDS = {"provider", "model_id", "endpoint", "api_key_env", "input_usd_per_million",
    "output_usd_per_million", "cached_input_usd_per_million", "max_input_tokens", "timeout_seconds",
    "settings_verified", "pricing_verified", "thinking_disabled_parameters", "verified_nonreasoning",
    "allow_synchronous_judge", "accepted_model_ids", "input_overhead_tokens", "anthropic_version",
    "max_output_parameter", "max_retries", "pricing_source", "settings_source", "verified_at",
    "fail_fast", "retry_backoff_seconds", "max_concurrent_requests"}
_SETTING_FIELDS = {"temperature", "top_p", "max_tokens", "presence_penalty", "frequency_penalty",
    "disable_thinking", "thinking", "structured_output", "use_batch_api", "scene", "scenes", "description"}
_LABELS = ["FACT", "UNCERTAIN", "SKEPTICAL", "CHECKED_TRUE", "CHECKED_FALSE", "NOT_MENTIONED"]
_ID = re.compile(r"[A-Za-z0-9_./:\-]{1,256}\Z")
_ENV = re.compile(r"[A-Z_][A-Z0-9_]{0,127}\Z")
_RATES = ("input_usd_per_million", "output_usd_per_million", "cached_input_usd_per_million")
DEFAULT_MAX_CONCURRENT_REQUESTS = 32


def _integer(value, name, *, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ProviderError(f"{name} must be an integer >= {minimum}")
    return value


def _identifier(value, name):
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ProviderError(f"invalid {name}")
    return value


def _number(value, name, lower=0, upper=None):
    # Manifest JSON numbers are strict: booleans and numeric strings are not rates.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProviderError(f"invalid {name}")
    try:
        result = money(value, name)
    except BudgetError:
        raise ProviderError(f"invalid {name}") from None
    if result < Decimal(str(lower)) or (upper is not None and result > Decimal(str(upper))):
        raise ProviderError(f"invalid {name}")
    return result


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward an API key to another origin or route.


def _http_transport(method, url, headers, json_body, timeout_seconds):
    request = urllib.request.Request(url, data=canonical_bytes(json_body), headers=headers, method=method)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise ValueError("provider response exceeds local limit")
            body = json.loads(raw)
            return HTTPResponse(response.status, body, dict(response.headers))
    except urllib.error.HTTPError as error:
        # Never persist an error body or headers. A 429 keeps only its error code,
        # which separates a documented pre-inference rejection from other 429s.
        if error.code != 429:
            return HTTPResponse(error.code, {}, {})
        try:
            code = _error_code(error.read(64 * 1024))
        except (OSError, ValueError):
            code = None
        return HTTPResponse(429, {"error": {"code": code}} if code else {}, {})


def _error_code(raw: bytes) -> str | None:
    try:
        body = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        return None
    error = body.get("error") if isinstance(body, dict) else None
    code = error.get("code") if isinstance(error, dict) else None
    return code if isinstance(code, str) and re.fullmatch(r"[a-z_]{1,64}", code) else None


class ProviderBackend:
    def __init__(self, manifest: dict, ledger: BudgetLedger, transport=None,
                 *, evidence_kind: str = "development_pilot"):
        if evidence_kind not in {"development_pilot", "mocked_provider"}:
            raise ProviderError("provider evidence must be development_pilot or mocked_provider")
        if evidence_kind == "mocked_provider" and transport is None:
            raise ProviderError("mocked_provider requires an explicit injected transport")
        if transport is not None and not callable(transport):
            raise ProviderError("injected transport must be callable")
        if not isinstance(manifest, dict) or set(manifest) - {"version", "approved", "routes"}:
            raise ProviderError("unsupported provider manifest fields")
        if type(manifest.get("version")) is not int or manifest["version"] != 1 or type(manifest.get("approved")) is not bool:
            raise ProviderError("invalid provider manifest version or approval")
        if not isinstance(manifest.get("routes"), dict) or not manifest["routes"]:
            raise ProviderError("provider manifest needs routes")
        # No API secrets, arbitrary headers, body overrides or credentials in URLs.
        for key, route in manifest["routes"].items():
            _identifier(key, "model key")
            if not isinstance(route, dict) or set(route) - _ROUTE_FIELDS:
                raise ProviderError("unsupported provider route fields")
            provider = route.get("provider")
            if provider not in _ENDPOINTS or route.get("endpoint") != _ENDPOINTS[provider]:
                raise ProviderError("provider endpoint must be its explicit official route")
            _identifier(route.get("model_id"), "model id")
            if not isinstance(route.get("api_key_env"), str) or not _ENV.fullmatch(route["api_key_env"]):
                raise ProviderError("invalid API key environment-variable name")
            for flag in ("settings_verified", "pricing_verified", "verified_nonreasoning", "allow_synchronous_judge"):
                if flag in route and type(route[flag]) is not bool:
                    raise ProviderError("route verification flags must be booleans")
            for field_name in _RATES:
                if route.get(field_name) is not None:
                    _number(route[field_name], field_name)
            for field_name in ("max_input_tokens", "input_overhead_tokens", "max_retries", "max_concurrent_requests"):
                if field_name in route:
                    _integer(route[field_name], field_name,
                             minimum=1 if field_name in {"max_input_tokens", "max_concurrent_requests"} else 0)
            if "fail_fast" in route and (type(route["fail_fast"]) is not bool
                                         or (route["fail_fast"] and provider not in _REJECTED_BEFORE_INFERENCE)):
                raise ProviderError("fail_fast is a boolean for routes with a documented pre-inference rejection")
            # Only a documented pre-inference rejection is retried. Timeouts and other
            # failures can be billed, so they hold their reservation and never retry.
            if route.get("max_retries", 0) > 10 or (route.get("max_retries", 0) and route.get("fail_fast") is not True):
                raise ProviderError("retries are limited to 10 after confirmed fail-fast rejections")
            if route.get("max_concurrent_requests", 1) > 200:
                raise ProviderError("max_concurrent_requests exceeds the provider's 200 per-model limit")
            if "retry_backoff_seconds" in route:
                _number(route["retry_backoff_seconds"], "retry_backoff_seconds", 0, 60)
            if "timeout_seconds" in route:
                if _number(route["timeout_seconds"], "timeout_seconds") == 0:
                    raise ProviderError("timeout_seconds must be positive")
            accepted = route.get("accepted_model_ids", [])
            if not isinstance(accepted, list):
                raise ProviderError("accepted_model_ids must be an explicit list")
            for model in accepted:
                _identifier(model, "accepted model id")
            if "thinking_disabled_parameters" in route:
                self._thinking_parameters(route)
            if "anthropic_version" in route and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(route["anthropic_version"])):
                raise ProviderError("invalid Anthropic API version")
            if route.get("max_output_parameter", "max_tokens") not in {"max_tokens", "max_completion_tokens"}:
                raise ProviderError("unsupported output token parameter")
            for field_name in ("pricing_source", "settings_source", "verified_at"):
                if field_name in route and (not isinstance(route[field_name], str) or len(route[field_name]) > 500
                    or any(ord(c) < 32 for c in route[field_name])):
                    raise ProviderError("invalid provenance field")
        try:
            self._manifest = clone(manifest)
        except (TypeError, ValueError):
            raise ProviderError("manifest must be finite JSON") from None
        self.ledger = ledger
        self.ledger.summary()  # Validate ownership/open state without key access.
        self.transport = _http_transport if transport is None else transport
        self.evidence_kind = evidence_kind
        self._sleep = asyncio.sleep
        self._slots: dict[str, asyncio.Semaphore] = {}
        self._slots_loop = None

    def _slot(self, model_key: str, route: dict) -> asyncio.Semaphore:
        """One in-flight request cap per route, shared by every town in this process."""
        loop = asyncio.get_running_loop()
        if loop is not self._slots_loop:
            self._slots, self._slots_loop = {}, loop
        if model_key not in self._slots:
            self._slots[model_key] = asyncio.Semaphore(
                route.get("max_concurrent_requests", DEFAULT_MAX_CONCURRENT_REQUESTS))
        return self._slots[model_key]

    @property
    def manifest(self):
        return clone(self._manifest)

    @staticmethod
    def _thinking_parameters(route):
        mapping = route.get("thinking_disabled_parameters")
        provider = route["provider"]
        options = [{"reasoning_effort": "none"}] if provider in {"DeepInfra", "OpenAI"} else [{"thinking": {"type": "disabled"}}]
        if provider == "DeepInfra":
            options.append({"reasoning": {"enabled": False}})
        if mapping == {} and route.get("verified_nonreasoning") is True:
            return {}
        if not isinstance(mapping, dict) or canonical_bytes(mapping) not in [canonical_bytes(option) for option in options]:
            raise ProviderError("thinking disable mapping is missing or unsupported for this route")
        return clone(mapping)

    def _prepare(self, request: GenerationRequest):
        if self._manifest["approved"] is not True:
            raise ProviderError("provider manifest is not approved")
        route = self._manifest["routes"].get(request.model_key)
        if route is None:
            raise ProviderError("request has no explicit provider route")
        if route.get("settings_verified") is not True or route.get("pricing_verified") is not True:
            raise ProviderError("provider settings and standard pricing must be verified")
        for field_name in _RATES:
            _number(route.get(field_name), field_name)
        max_input = _integer(route.get("max_input_tokens"), "max_input_tokens", minimum=1)
        if _number(route.get("timeout_seconds"), "timeout_seconds") == 0:
            raise ProviderError("timeout_seconds must be positive")
        if not isinstance(request.settings, dict) or set(request.settings) - _SETTING_FIELDS:
            raise ProviderError("unsupported generation settings")
        settings = clone(request.settings)
        max_output = _integer(settings.get("max_tokens"), "max_tokens", minimum=1)
        if not isinstance(request.messages, list) or not request.messages:
            raise ProviderError("messages must be a nonempty list")
        for message in request.messages:
            if not isinstance(message, dict) or set(message) != {"role", "content"} or message["role"] not in {"system", "user", "assistant"} or not isinstance(message["content"], str):
                raise ProviderError("unsupported message schema")
        messages = clone(request.messages)
        provider = route["provider"]
        output_parameter = route.get("max_output_parameter", "max_completion_tokens" if provider == "OpenAI" else "max_tokens")
        if provider == "Anthropic" and output_parameter != "max_tokens":
            raise ProviderError("Anthropic requires max_tokens")
        body = {"model": route["model_id"], "messages": messages, output_parameter: max_output}
        if route.get("fail_fast") is True:
            body["fail_fast"] = True
        if provider == "Anthropic":
            systems = []
            while messages and messages[0]["role"] == "system":
                systems.append(messages.pop(0)["content"])
            if not messages or any(m["role"] == "system" for m in messages):
                raise ProviderError("Anthropic supports leading system messages only")
            if systems:
                body["system"] = [{"type": "text", "text": content} for content in systems]
        for name in ("temperature", "top_p", "presence_penalty", "frequency_penalty"):
            if name not in settings:
                continue
            if provider == "Anthropic":
                raise ProviderError("Anthropic route does not accept these sampling/penalty overrides")
            value = settings[name]
            if name in {"presence_penalty", "frequency_penalty"}:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not (-2 <= value <= 2):
                    raise ProviderError("invalid penalty")
            else:
                _number(value, name, 0, 2 if name == "temperature" else 1)
            body[name] = value
        if "disable_thinking" in settings:
            if settings["disable_thinking"] is not True:
                raise ProviderError("only the declared thinking-disabled protocol is supported")
            body.update(self._thinking_parameters(route))
        if "thinking" in settings:
            if settings["thinking"] != {"type": "disabled"}:
                raise ProviderError("unsupported native thinking setting")
            if provider == "Anthropic":
                body["thinking"] = clone(settings["thinking"])
            else:
                # The abstract judge setting must also be explicitly mapped for
                # an approved nonreasoning or compatible OpenAI judge route.
                body.update(self._thinking_parameters(route))
        execution_mode = "synchronous"
        if "use_batch_api" in settings:
            if type(settings["use_batch_api"]) is not bool:
                raise ProviderError("use_batch_api must be boolean")
            if settings["use_batch_api"]:
                if route.get("allow_synchronous_judge") is not True:
                    raise ProviderError("batch requests need explicit approved synchronous judge override")
                if request.kind != "judge":
                    raise ProviderError("synchronous override is limited to judge requests")
                execution_mode = "synchronous_override"
        if "structured_output" in settings:
            declared = settings["structured_output"]
            if declared != {"label_enum_from": "judging_and_scoring.categorical_labels", "required_fields": ["label", "quote"]}:
                raise ProviderError("unsupported structured judge schema")
            schema = {"type": "object", "properties": {"label": {"type": "string", "enum": _LABELS}, "quote": {"type": "string"}},
                      "required": ["label", "quote"], "additionalProperties": False}
            if provider == "Anthropic":
                body["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
            else:
                body["response_format"] = {"type": "json_schema", "json_schema": {"name": "belief_judgment", "strict": True, "schema": schema}}
        # The declared framing allowance is conservative, not a tokenizer proof.
        # The reservation uses the whole manifest input cap, never an optimistic
        # estimate from characters. Calls exceeding this preflight bound stop.
        input_bytes_bound = len(canonical_bytes(body)) + route.get("input_overhead_tokens", 1024)
        if input_bytes_bound > max_input:
            raise ProviderError("UTF-8 payload bound plus framing allowance exceeds declared input cap")
        pricing = {name: route[name] for name in _RATES}
        pricing_sha256 = digest(pricing)
        reservation = (Decimal(max_input) * max(_number(route[_RATES[0]], _RATES[0]), _number(route[_RATES[2]], _RATES[2]))
                       + Decimal(max_output) * _number(route[_RATES[1]], _RATES[1])) / Decimal(1_000_000)
        return route, body, execution_mode, pricing_sha256, reservation

    def validate_request(self, request: GenerationRequest) -> None:
        """Pure preflight: no environment/key read, reservation or network access."""
        self._prepare(request)

    def validate_credentials(self, model_keys: list[str]) -> None:
        """After authority/preflight gates, check selected keys without a request.

        Presence is not proof of provider access. Values are neither returned nor
        stored. Unselected routes (such as the optional audit judge) are untouched.
        """
        if not isinstance(model_keys, list) or any(not isinstance(key, str) for key in model_keys):
            raise ProviderError("invalid credential-validation selection")
        if self._manifest["approved"] is not True:
            raise ProviderError("provider manifest is not approved")
        selected = []
        for model_key in sorted(set(model_keys)):
            route = self._manifest["routes"].get(model_key)
            if route is None or route.get("settings_verified") is not True or route.get("pricing_verified") is not True:
                raise ProviderError("selected provider route is not verified")
            selected.append(route)
        for route in selected:
            key = os.environ.get(route["api_key_env"])
            if not key or "\n" in key or "\r" in key:
                raise ProviderError("a selected provider credential is missing or invalid")

    @staticmethod
    def _receipt(route, execution_mode, pricing_sha256):
        return {"actual_provider": route["provider"], "actual_model": None, "request_id": None,
                "provider_api_calls": 0, "input_tokens": None, "output_tokens": None,
                "cached_input_tokens": None, "reasoning_tokens": None, "cost_usd": None,
                "cost_status": "not_submitted", "attempts": [], "pricing_sha256": pricing_sha256,
                "execution_mode": execution_mode, "cache_usage": None}

    @staticmethod
    def _usage(body, route, receipt):
        model = body.get("model")
        if isinstance(model, str) and _ID.fullmatch(model):
            receipt["actual_model"] = model
        identifier = body.get("id")
        if isinstance(identifier, str) and _ID.fullmatch(identifier):
            receipt["request_id"] = identifier
        if model not in [route["model_id"], *route.get("accepted_model_ids", [])]:
            raise ProviderError("response model differs from the approved route")
        usage = body.get("usage")
        if not isinstance(usage, dict):
            raise ProviderError("provider usage is missing")
        # A missing cache count is priced as if every input token were uncached:
        # a conservative estimate, marked so replay and summaries can see it.
        if route["provider"] == "Anthropic":
            uncached = _integer(usage.get("input_tokens"), "input_tokens")
            output = _integer(usage.get("output_tokens"), "output_tokens")
            receipt["output_tokens"] = output
            cached = usage.get("cache_read_input_tokens")
            if cached is not None:
                cached = _integer(cached, "cache_read_input_tokens")
            created = usage.get("cache_creation_input_tokens")
            created = 0 if created is None else _integer(created, "cache_creation_input_tokens")
            receipt.update(input_tokens=uncached + (cached or 0) + created, output_tokens=output,
                           cached_input_tokens=cached, cache_creation_input_tokens=created,
                           cache_usage="unreported" if cached is None else "reported")
            reasoning = usage.get("output_tokens_details", {})
            if isinstance(reasoning, dict) and "thinking_tokens" in reasoning:
                receipt["reasoning_tokens"] = _integer(reasoning["thinking_tokens"], "thinking_tokens")
            if created:
                raise ProviderError("unexpected cache creation has no approved write price")
            if usage.get("server_tool_use") not in (None, {}, {"web_search_requests": 0, "web_fetch_requests": 0}):
                raise ProviderError("unexpected server tool usage has no approved price")
        else:
            total = _integer(usage.get("prompt_tokens"), "prompt_tokens")
            output = _integer(usage.get("completion_tokens"), "completion_tokens")
            receipt.update(input_tokens=total, output_tokens=output)
            details = usage.get("prompt_tokens_details")
            if details is None:
                details = {}
            if not isinstance(details, dict):
                raise ProviderError("invalid cached input usage")
            cached = details.get("cached_tokens")
            if cached is not None:
                cached = _integer(cached, "cached_tokens")
                if cached > total:
                    raise ProviderError("cached input exceeds total input")
            receipt.update(input_tokens=total, output_tokens=output, cached_input_tokens=cached,
                           cache_usage="unreported" if cached is None else "reported")
            # Newer OpenAI APIs can bill cache writes at a separate input rate.
            # No cache-write mode is requested here; an unexpected charge stops.
            # DeepInfra reports "cache_write_tokens": null when nothing was written.
            writes = details.get("cache_write_tokens")
            created = usage.get("cache_creation_input_tokens")
            if (writes is not None and writes != 0) or (created is not None and created != 0):
                raise ProviderError("unexpected cache writes have no approved price")
            uncached = total - (cached or 0)
            reasoning = usage.get("completion_tokens_details", {})
            if isinstance(reasoning, dict) and "reasoning_tokens" in reasoning:
                receipt["reasoning_tokens"] = _integer(reasoning["reasoning_tokens"], "reasoning_tokens")
        if receipt["reasoning_tokens"] is not None and receipt["reasoning_tokens"] > output:
            raise ProviderError("reasoning usage exceeds output usage")
        cost = (Decimal(uncached) * money(route[_RATES[0]]) + Decimal(cached or 0) * money(route[_RATES[2]])
                + Decimal(output) * money(route[_RATES[1]])) / Decimal(1_000_000)
        receipt.update(cost_usd=float(cost), cost_status="calculated_from_usage")
        return cost

    @staticmethod
    def _text(body, provider):
        if provider == "Anthropic":
            content = body.get("content")
            if not isinstance(content, list) or not content or any(not isinstance(block, dict) or block.get("type") != "text" or not isinstance(block.get("text"), str) for block in content):
                raise ProviderError("provider returned unsupported nontext or missing content")
            return "".join(block["text"] for block in content)
        choices = body.get("choices")
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise ProviderError("provider returned malformed choices")
        message = choices[0].get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str) or message.get("tool_calls"):
            raise ProviderError("provider returned unsupported nontext or missing content")
        return message["content"]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        try:
            route, body, mode, pricing_hash, reserved = self._prepare(request)
        except ProviderError as error:
            receipt = {"actual_provider": None, "actual_model": None, "request_id": None,
                "provider_api_calls": 0, "input_tokens": None, "output_tokens": None,
                "cached_input_tokens": None, "reasoning_tokens": None, "cost_usd": None,
                "cost_status": "not_submitted", "attempts": [], "pricing_sha256": None,
                "execution_mode": None, "cache_usage": None}
            raise ProviderError(str(error), receipt) from None
        receipt = self._receipt(route, mode, pricing_hash)
        key = os.environ.get(route["api_key_env"])
        if not key or "\n" in key or "\r" in key:
            raise ProviderError("configured API key is missing or invalid", receipt)
        headers = {"Content-Type": "application/json"}
        if route["provider"] == "Anthropic":
            headers.update({"x-api-key": key, "anthropic-version": route.get("anthropic_version", "2023-06-01")})
        else:
            headers["Authorization"] = "Bearer " + key
        retries = route.get("max_retries", 0)
        backoff = float(route.get("retry_backoff_seconds", 2))
        for index in range(retries + 1):
            async with self._slot(request.model_key, route):
                result = await self._attempt(index, request, route, body, headers, key,
                                             pricing_hash, reserved, receipt)
            if result is not None:
                return result
            if index < retries:
                try:
                    await self._sleep(min(30.0, backoff * 2 ** index))
                except asyncio.CancelledError as error:
                    error.receipt = clone(receipt)   # keep the free attempts on record
                    raise
        raise ProviderError("provider rejected every attempt before inference", receipt)

    async def _attempt(self, index, request, route, body, headers, key, pricing_hash, reserved, receipt):
        """Send one attempt. Returns None only for a documented pre-inference rejection."""
        try:
            reservation_id = self.ledger.reserve(reserved, {"model_key": request.model_key, "provider": route["provider"],
                "model_id": route["model_id"], "request_sha256": digest(body), "pricing_sha256": pricing_hash,
                "attempt_index": index, "input_token_bound": route["max_input_tokens"],
                "max_output_tokens": request.settings["max_tokens"], "evidence_kind": self.evidence_kind})
        except (BudgetError, OSError):
            raise ProviderError("budget does not permit this request", receipt) from None
        receipt["provider_api_calls"] += 1
        receipt["cost_status"] = "unknown"
        attempt = {"attempt_index": index, "reservation_id": reservation_id, "status": "started"}
        receipt["attempts"].append(attempt)
        cost = None
        settled = False
        try:
            arguments = ("POST", route["endpoint"], headers, clone(body), route["timeout_seconds"])
            async def invoke():
                if inspect.iscoroutinefunction(self.transport):
                    return await self.transport(*arguments)
                result = await asyncio.to_thread(self.transport, *arguments)
                return await result if inspect.isawaitable(result) else result
            response = await asyncio.wait_for(invoke(), timeout=route["timeout_seconds"])
            if isinstance(response, dict):
                response = HTTPResponse(200, response)
            if not isinstance(response, HTTPResponse) or type(response.status_code) is not int:
                raise ProviderError("transport returned an invalid response")
            attempt["http_status"] = response.status_code
            if self._rejected_before_inference(route, response):
                code = _REJECTED_BEFORE_INFERENCE[route["provider"]]
                attempt.update(status="rejected", error_code=code)
                receipt.update(cost_usd=0.0, cost_status="rejected_before_inference", error_code=code)
                self._redact_receipt(receipt, key)
                self.ledger.settle(reservation_id, 0, {**self._ledger_receipt(receipt), "http_status": 429})
                settled = True
                return None
            if not 200 <= response.status_code < 300:
                raise ProviderError("provider returned a non-success HTTP status")
            if not isinstance(response.body, dict):
                raise ProviderError("provider returned invalid JSON")
            receipt.pop("error_code", None)
            cost = self._usage(response.body, route, receipt)
            # Reported usage checks protect subsequent calls even if verified
            # bounds or the provider's accounting assumptions were wrong.
            if receipt["input_tokens"] > route["max_input_tokens"] or receipt["output_tokens"] > request.settings["max_tokens"]:
                cost = None
                receipt.update(cost_usd=None, cost_status="unknown")
                raise ProviderError("provider usage exceeded declared token bounds")
            text = self._text(response.body, route["provider"])
            if key in text:
                raise ProviderError("provider returned credential-bearing content")
            attempt["status"] = "completed"
            self._redact_receipt(receipt, key)
            self.ledger.settle(reservation_id, cost, self._ledger_receipt(receipt))
            settled = True
            self._redact_receipt(receipt, key)
            return GenerationResponse(text, clone(receipt))
        except BaseException as error:
            attempt["status"] = "cancelled" if isinstance(error, asyncio.CancelledError) else "failed"
            receipt["error_code"] = "cancelled" if isinstance(error, asyncio.CancelledError) else "request_failed"
            if cost is None:
                receipt.update(cost_usd=None, cost_status="unknown")
            self._redact_receipt(receipt, key)
            if not settled:
                try:
                    self.ledger.settle(reservation_id, cost, self._ledger_receipt(receipt))
                except (BudgetError, OSError):
                    # An overrun is already persisted as blocking; an I/O error
                    # leaves the original pending reservation durable for restart.
                    receipt["ledger_settlement_error"] = True
            if isinstance(error, asyncio.CancelledError):
                error.receipt = clone(receipt)
                raise
            # Never interpolate a transport exception, HTTP body, key or headers.
            raise ProviderError("provider request failed; consult the sanitized receipt", receipt) from None

    @staticmethod
    def _rejected_before_inference(route, response) -> bool:
        """Only the provider's documented fail-fast capacity rejection is known to be free."""
        expected = _REJECTED_BEFORE_INFERENCE.get(route["provider"])
        error = response.body.get("error") if isinstance(response.body, dict) else None
        return (route.get("fail_fast") is True and expected is not None and response.status_code == 429
                and isinstance(error, dict) and error.get("code") == expected)

    @staticmethod
    def _redact_receipt(receipt, key):
        for name, value in receipt.items():
            if isinstance(value, str) and key in value:
                receipt[name] = "[REDACTED]"

    @staticmethod
    def _ledger_receipt(receipt):
        return {key: value for key, value in receipt.items() if key not in {"attempts", "ledger_settlement_error"}}
