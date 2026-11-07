# Bounded development collection

The runner now has adapters for DeepInfra/OpenAI Chat Completions and native Anthropic Messages. Mocked HTTP tests exercise their request formats, response accounting, saved traces and replay. No real provider call was used to validate this implementation. Public model availability is verified separately from account access.

The existing credit-use hold remains. A budget discussion or a successful test does not authorize spending. The execution flags below are for a future operator after explicit spending authorization, route approval and account setup.

## Preview without credentials or network

```bash
PYTHONPATH=src python3 -m truth_discount.cli live \
  --providers configs/providers.example.json \
  --output outputs/pilot-first-batch
```

This command only prints the planned runs, hashes and outstanding gates. It does not read API keys, create output, open a ledger or make requests. The supplied example intentionally has `approved: false` and `settings_verified: false`. It contains published rates and environment-variable names, never key values.

The default selection is one matched pair per cell per model: 16 towns across both models and all four cells. This is a declared development subset, not the full 624-town pilot. `--model-key` selects an explicitly recorded subset of configured models. No model substitutions are permitted by the collection entry point.

## Approval and execution

Before execution, the team must approve the exact provider manifest, validate account/model access and settings, confirm a payer and ceiling, and release the spending hold. Required environment variables are checked together before the first town. Do not commit credentials or send them with a handover.

The configured judge requests batch execution. This implementation supports synchronous requests only. The judge route therefore requires an explicit approved `allow_synchronous_judge: true` override for a development pilot. That override records `synchronous_override` in receipts and uses standard rates. It does not receive a batch discount or implement the later Batch API stage.

Once the hold has been explicitly released, execution requires all of:

- `--execute` and `--spending-authorized`;
- an approved manifest with verified pricing/settings and unchanged configured model IDs/providers;
- `--ledger` pointing to a durable budget ledger and an explicit `--budget-usd` ceiling;
- a new output directory, preventing an accidental overwrite of paid runs, or `--resume` to continue one (see below).

The CLI checks all required request kinds, manifest equality and key presence before collection. It never selects an alternative model. The only retried failure is a documented pre-inference rejection (see below). Actual account access and provider response compatibility still require a separately authorized live smoke test. That smoke test should also confirm Qwen's GO/SKIP replies are non-empty with the explicit `reasoning_effort: none` setting.

## Cost control and failures

Each request reserves its declared maximum input/output cost before submission. Reservations use the input cap, not an optimistic character estimate. A process lock protects the ledger against concurrent writers, and a thread lock protects concurrent calls in one process.

The ledger is an append-only JSON Lines journal. Its first line fixes the cap, and each reserve and settlement adds one line, flushed to disk before the request is sent. Earlier lines are never rewritten, so recording a request takes the same time at request 50,000 as at request 1. Reopening replays the journal: the cap, earlier spending and held reservations all survive a crash. A crash can tear only the last line. That line was never acknowledged, so it is dropped, and any request still pending becomes an `interrupted_request` that stays held. Older single-file ledgers are refused rather than overwritten. Start a new ledger path for them.

Successful receipts record provider/model/request IDs, token categories, calculated token cost, request attempts and the pricing hash. Cache and reasoning counts are not double-counted. Calculated charges from usage are not verified invoices. The local guard does not impose an account-wide or provider-enforced limit on other clients.

Missing usage, HTTP failures, timeouts or cancellations can leave the actual charge unknown. The ledger keeps the reservation and blocks new requests, including after a restart. Never delete the ledger or start a new one to get past this. Instead, look up the billed amount in the provider's usage records and record it:

```bash
PYTHONPATH=src python3 -m truth_discount.cli ledger --ledger ledgers/pilot.jsonl --budget-usd 20
PYTHONPATH=src python3 -m truth_discount.cli ledger --ledger ledgers/pilot.jsonl --budget-usd 20 \
  --reconcile <reservation id> --actual-usd 0.0004 --note "DeepInfra usage page, 19 Nov"
```

The first command lists unknown charges. The second records one. If the billed amount cannot be found, record the reserved amount, which is an upper bound. Paid empty or malformed model responses still retain their usage and cost records.

### Rejections and retries

DeepInfra routes send `fail_fast: true`. When a model has no spare capacity, DeepInfra then answers at once with HTTP 429 and error code `engine_overloaded`. DeepInfra documents that such a request never reaches the model and is not billed ([fail fast](https://docs.deepinfra.com/chat/overview#fail-fast)). Only that exact answer is recorded as $0 and retried, up to `max_retries` times with doubling waits from `retry_backoff_seconds`. Each attempt has its own reservation. Every other failure holds its reservation and is never retried. This includes 429 `Rate limited`, 5xx errors, dropped connections and timeouts. The HTTP client keeps only the error code from a 429 body, never the body or headers.

### Missing cache counts

DeepInfra's usage may omit `prompt_tokens_details.cached_tokens`. A response without a cache count is still a known bill. It is priced as if every input token were uncached, which is the full input rate and a conservative estimate, and the receipt is marked `cache_usage: "unreported"`. Replay recomputes that price, and `summarize` reports `cache_usage_unreported_calls`. Missing input or output token counts still leave the charge unknown.

### Resume and several towns at once

`--resume` continues an existing output directory. The config, provider manifest and run selection must hash the same as its saved `execution_plan.json`, and the ledger must not be blocked. Towns that pass the full replay audit as completed are skipped. A partial or unverifiable town is moved, unchanged, to `_incomplete/attempt-N/<run id>/` for reconciliation, then rerun. Each resume appends a line to `resume_log.jsonl`.

`--max-concurrent-towns N` (1-16) runs several towns at once. They share one ledger and one per-route request limit, `max_concurrent_requests`, which defaults to 32. The example manifest sets 150 for each DeepInfra model, below the 200 per-model account limit, and 8 for the judge. Once any town fails, no new town starts. Towns already running finish and save.

The supplied routes limit input to 32,768 tokens, keeping Haiku within its published short-prompt price tier. The byte/framing check is a conservative local preflight, not a proof of provider tokenization. Unexpected token overruns or cache-write charges stop further collection.

## Evidence and replay

New bundles use `truth-discount-0.2`. Original generated-source v0.1 bundles and the scripted-source PR6 variant remain replayable without modifying their saved files.

- `synthetic_fixture` records deterministic software fixtures.
- `mocked_provider` records injected HTTP responses, simulated token charges and zero actual provider calls. Mocked mode requires an explicit injected transport.
- `development_pilot` records actual development-provider receipts when an authorized operator runs it.

All remain `study_eligible: false`. Summaries refuse to pool these evidence kinds. A real development pilot does not automatically qualify as the final study or a held-out evaluation.

The phone regex trigger and its final-judgment filter remain diagnostics. They do not identify the first substantive mention. The checked-plus-artist/board field is a keyword diagnostic, not semantic proof that evidence was transmitted. Replay checks both derived fields against the saved messages.

## Disjoint batches and handover

`--start-pair` and `--pairs-per-cell` declare disjoint ranges of the 39 configured pairs per cell. The default first batch has 16 towns. After verifying its actual completion, `--full-pilot --start-pair 1` selects the remaining 608 without selecting those first 16 IDs again.

These are explicit work assignments between operators. `--resume` only continues one output directory with one ledger. Operators still need one shared completion/cost ledger, identical configuration/model manifests and an agreed handover. A partial town is rerun only after its unknown charges are reconciled, and its original bundle is kept. Native batch jobs, automated cross-person resume and GPT-4o audit execution remain separate tasks. The [analysis and the human judge audit](08_analysis_and_audit.md) read finished outputs.

## Main study

`configs/main_config.json` is the 64-cell factorial: every combination of closeness, authority, reliability, wealth and identity (gender × age). That is 4,992 towns per model and 9,984 in total. It is generated from the pilot config, so prompts, personas, layouts and models are identical:

```bash
PYTHONPATH=src python3 scripts/make_main_config.py
```

Regenerate it after any pilot-config change. A test fails if the two drift apart. Cell IDs count through `factorial_levels` with identity changing fastest. The pilot's four cells are main cells 1, 62, 30 and 46 (`pilot_cell_ids_in_main`). Artist allocation follows `seed_id + cell_id` parity, so main cell 30 swaps real and fake artists relative to pilot cell 3. Pilot towns are therefore not reused as main-study towns.

Every command above accepts `--config configs/main_config.json`. The default selection is one pair per cell per model, which is 256 towns, and `--full-pilot` selects all 9,984. Use a new output directory. The ledger can be shared with the pilot only if its cap was set high enough at creation, because the cap can never be raised.

See [published rates and planning scenarios](07_pricing_and_budget.md) before agreeing a funding amount.
