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

The ledger is an append-only JSON Lines journal. Its header fixes a random identity and the cap. Each reserve and settlement adds one durable event. Incremental hashing avoids rewriting or rehashing the full history per request. Collection also atomically refreshes a small external `budget_checkpoint.json` after every ledger mutation, before a reservation can return and submit a request. If that anchor cannot be saved, collection holds the reservation and blocks later requests. On Windows, an antivirus scan, search indexer or editor can hold the file open for a moment. A replace refused for that reason is retried for up to about 10 seconds before it counts as a storage failure. Filesystem latency still affects performance.

Reopening replays the journal, preserving earlier spending and held reservations. An incomplete final append is discarded, and any pending request becomes an `interrupted_request` that stays held. Valid older v2 journals gain an appended identity event without rewriting their history. Older single-file ledgers are refused. Do not replace a paid ledger to bypass this check. A reviewed migration must preserve its spending and unresolved charges.

Successful receipts record provider/model/request IDs, token categories, calculated token cost, request attempts and the pricing hash. Cache and reasoning counts are not double-counted. Calculated charges from usage are not verified invoices. The local guard does not impose an account-wide or provider-enforced limit on other clients.

Missing usage, HTTP failures, timeouts or cancellations can leave the actual charge unknown. The ledger keeps the reservation and blocks new requests, including after a restart. Never delete the ledger or start a new one to get past this. Instead, look up the billed amount in the provider's usage records and record it:

```bash
python3 scripts/reconcile_unknowns.py ledgers/pilot.jsonl 20 outputs/pilot
PYTHONPATH=src python3 -m truth_discount.cli ledger --ledger ledgers/pilot.jsonl --budget-usd 20 \
  --reconcile "RESERVATION_ID" --actual-usd 0.0004 --note "Provider usage record reference"
```

The first command previews source-bound receipt evidence through a temporary journal copy. It does not change the supplied journal. The second records one manually verified billed amount after replacing the example ID, amount and note. If the charge cannot be established, keep the reservation held. The general `ledger` command opens the journal for recovery and must not be used as a read-only evidence inspection tool. Paid empty or malformed model responses still retain their usage and cost records.

`reconcile_unknowns.py --apply` accepts only a uniquely attributable priced receipt from audited active or archived bundles, with matching execution plan, journal identity, request and pricing. It does not guess from the reserved amount or apply a call-level aggregate cost to multiple reservations. Unresolved evidence leaves the hold in place. Usage-priced local accounting is still separate from provider invoice verification.

The optional `scripts/run_until_done.py --auto-reconcile` requires explicit `--execute` and `--spending-authorized` flags plus the original ledger, cap and output. Preview or incomplete authority cannot invoke recovery. Only documented free-busy failures or successful source-bound reconciliation allow another attempt. Other failures stop. Retrying a partial town can repeat earlier paid calls, which remain in the same journal and archived attempts.

### Rejections and retries

DeepInfra routes send `fail_fast: true`. When a model has no spare capacity, DeepInfra then answers at once with HTTP 429 and error code `engine_overloaded`. DeepInfra documents that such a request never reaches the model and is not billed ([fail fast](https://docs.deepinfra.com/chat/overview#fail-fast)). Only that exact answer is recorded as $0 and retried, up to `max_retries` times with doubling waits from `retry_backoff_seconds`. Each attempt has its own reservation. Every other failure holds its reservation and is never retried. This includes 429 `Rate limited`, 5xx errors, dropped connections and timeouts. The HTTP client keeps only the error code from a 429 body, never the body or headers.

### Missing cache counts

DeepInfra's usage may omit `prompt_tokens_details.cached_tokens`. When valid total prompt/output counts are present, a response without a cache count is priced as if every input token were uncached. The receipt records the conservative estimate with `cache_usage: "unreported"`. Replay recomputes that price, and `summarize` reports `cache_usage_unreported_calls`. Missing input or output token counts still leave the charge unknown. Native Anthropic cache counters follow a different format, and the current native route does not request cache writes.

### Resume and several towns at once

`--resume` continues an existing output directory only with its original ledger identity and fixed cap. It verifies the exact journal prefix recorded in `budget_checkpoint.json`, allowing new reconciliations and later events but rejecting a replacement ledger or rewound/rewritten spending history. The execution plan must retain identical configuration, provider manifest, run selection and evidence kind. Legacy output plans without this binding require review and do not automatically resume.

Before reading credentials or making requests, collection audits every active and archived attempt against that plan. Completed towns are skipped only when their configuration/provider hashes, evidence kind and full run mapping match. A valid incomplete town can be preserved under `_incomplete/attempt-N/<run id>/` and rerun after any unknown charge is reconciled. A mismatched, corrupt or unverifiable town stops collection for review without moving or deleting its evidence. Each resume appends a line to `resume_log.jsonl`.

Existing top-level summary fields continue to describe active town directories. `receipt_accounting` separately reports active towns, completed active towns, archived attempts and all saved attempts. Archived attempts never enter paired outcome metrics. Unknown archived charges keep all-attempt cost unknown, with known subtotals reported separately. The collector's `budget_accounting` gives the entire bound ledger, including prior batches, partial attempts and operator reconciliation. Bundle receipt totals do not establish reconciled billing, and mocked costs remain simulated.

`--max-concurrent-towns N` (1-16) runs several towns at once. They share one ledger and one per-route request limit, `max_concurrent_requests`, which defaults to 32. The example manifest sets 150 for each DeepInfra model, below the 200 per-model account limit, and 8 for the judge. Once any town fails, no new town starts. Towns already running finish and save.

The supplied routes limit input to 32,768 tokens, keeping Haiku within its published short-prompt price tier. The byte/framing check is a conservative local preflight, not a proof of provider tokenization. Unexpected token overruns or cache-write charges stop further collection.

### Re-judging malformed labels

The live judge occasionally returns a quote that is not the listener's words. It may quote the caller, add a word, or use a curly apostrophe for a straight one. That label is malformed, so its town's judge metrics are incomplete and the twin pair drops out. In the 16-town smoke test this was 4 of 190 labels and 4 of 8 pairs. Every judge input is saved, so after collection those calls can be asked again without collecting anything anew:

```bash
PYTHONPATH=src python3 -m truth_discount.cli rejudge outputs/pilot
PYTHONPATH=src python3 -m truth_discount.cli rejudge outputs/pilot --providers configs/providers.pilot.json   --ledger outputs/ledgers/team.jsonl --budget-usd 20 --execute --spending-authorized
```

The first command previews the malformed count and complete pairs before and after, with no keys or spending. The second re-asks each malformed call up to 3 times. It spends through the same ledger and request limits, and appends every attempt with its receipt to `rejudged.jsonl` in the output directory. Saved towns are never modified, so they still replay. A rerun skips calls already re-judged. If an unclear charge stops it, reconcile and run it again.

## Evidence and replay

New bundles use `truth-discount-0.2`. Original generated-source v0.1 bundles and the scripted-source PR6 variant remain replayable without modifying their saved files.

- `synthetic_fixture` records deterministic software fixtures.
- `mocked_provider` records injected HTTP responses, simulated token charges and zero actual provider calls. Mocked mode requires an explicit injected transport.
- `development_pilot` records actual development-provider receipts when an authorized operator runs it.

All remain `study_eligible: false`. Summaries refuse to pool these evidence kinds. A real development pilot does not automatically qualify as the final study or a held-out evaluation.

The phone regex trigger and its final-judgment filter remain diagnostics. They do not identify the first substantive mention. The checked-plus-artist/board field is a keyword diagnostic, not semantic proof that evidence was transmitted. Replay checks both derived fields against the saved messages.

## Disjoint batches and handover

`--start-pair` and `--pairs-per-cell` declare disjoint ranges of the 39 configured pairs per cell. The default first batch has 16 towns. After verifying its actual completion, `--full-pilot --start-pair 1` selects the remaining 608 without selecting those first 16 IDs again.

These are explicit work assignments between operators. `--resume` only continues one bound output directory with its original ledger. Operators still need one shared completion/cost ledger, identical configuration/model manifests and an agreed handover. A partial town is rerun only after its unknown charges are reconciled, and its original bundle is kept. Native batch jobs, automated cross-person resume and GPT-4o audit execution remain separate tasks. The [analysis and the human judge audit](08_analysis_and_audit.md) read finished outputs.

## Main study

`configs/main_config.json` is the 64-cell factorial: every combination of closeness, authority, reliability, wealth and identity (gender × age). That is 4,992 towns per model and 9,984 in total. It is generated from the pilot config, so prompts, personas, layouts and models are identical:

```bash
PYTHONPATH=src python3 scripts/make_main_config.py
```

Regenerate it after any pilot-config change. A test fails if the two drift apart. Cell IDs count through `factorial_levels` with identity changing fastest. The pilot's four cells are main cells 1, 62, 30 and 46 (`pilot_cell_ids_in_main`). Artist allocation follows `seed_id + cell_id` parity, so main cell 30 swaps real and fake artists relative to pilot cell 3. Pilot towns are therefore not reused as main-study towns.

Every command above accepts `--config configs/main_config.json`. The default selection is one pair per cell per model, which is 256 towns, and `--full-pilot` selects all 9,984. Use a new output directory. The ledger can be shared with the pilot only if its cap was set high enough at creation, because the cap can never be raised.

See [published rates and planning scenarios](07_pricing_and_budget.md) before agreeing a funding amount.
