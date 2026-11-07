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
- a new output directory, preventing an accidental overwrite of paid runs.

The CLI checks all required request kinds, manifest equality and key presence before collection. It never selects an alternative model or silently retries a failed request. Actual account access and provider response compatibility still require a separately authorized live smoke test.

## Cost control and failures

Each request reserves its declared maximum input/output cost before submission. A process lock protects the ledger against concurrent writers, and a thread lock protects concurrent calls in one process. The cap remains fixed when the ledger is reopened. Reservations use the input cap, not an optimistic character estimate.

Successful receipts record provider/model/request IDs, token categories, calculated token cost, request attempts and the pricing hash. Cache and reasoning counts are not double-counted. Calculated charges from usage are not verified invoices. The local guard does not impose an account-wide or provider-enforced limit on other clients.

Missing usage, HTTP failures, timeouts or cancellations can leave the actual charge unknown. The ledger retains the reservation and blocks new requests. Unresolved reservations also block collection after a restart. Do not delete that state or retry ambiguous calls to make a run appear complete. Paid empty or malformed model responses still retain their usage and cost records. Partial towns remain saved for inspection.

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

These are explicit work assignments, not automatic resume. Operators still need one shared completion/cost ledger, identical configuration/model manifests and an agreed handover. Never rerun an ambiguous paid town automatically. Native batch jobs, automated cross-person resume, human audit selection, GPT-4o audit execution and final statistical inference remain separate tasks.

See [published rates and planning scenarios](07_pricing_and_budget.md) before agreeing a funding amount.
