# Simulation-only collection and separate judging

This workflow preserves the existing actor models, prompts, GO/SKIP settings and
phone-call funnel. It changes how outputs are saved and judged. It does not
approve a main run, choose a judge, release a spending hold or establish human
validation. Synthetic and mocked demonstrations remain non-study evidence.

## 1. Freeze one allocation before dividing the work

The main configuration contains 9,984 towns: 4,992 truth/rumour pairs across two
actor models. `pair-stratified-round-robin-v1` assigns complete pairs in canonical
model/real-artist/cell/seed order. Six shards contain 832 pairs and 1,664 towns
each, including 832 towns per actor model and 832 per real artist (416 per
actor-model/real-artist combination). There are at most 19,968 phone outcomes per shard.
These counts exclude additional probes, repairs and incomplete attempts.

Use the same config, source revision, actor model identifiers, settings, native
route and retention rules for every owner. Planning does not validate account
access. Each owner supplies their own credentials locally; never put keys in a
manifest, shared archive, repository or group message.

This is a **zero-call preview** for owner 0. Change only `--shard-index` for the
other five allocations, and use distinct output/ledger paths. The index is
zero-based, so valid owner indices are 0 through 5.

```sh
truth-discount simulate --config configs/main_config.json \
  --providers local/providers.actor.json --all-pairs \
  --shard-count 6 --shard-index 0 --output outputs/main-owner-0 \
  --plan-out local/main-owner-0-plan.json
```

Prepare `local/providers.actor.json` from the existing provider template, retaining
the agreed actor IDs and verified settings/prices. A judge route/key is not
required for simulation. The saved allocation records the source selection,
exact assigned IDs, algorithm version, config hash and allocation hash. The code
recomputes these fields instead of trusting claimed totals or shard ownership.
Changing model selection, pair range or shard count produces a different plan.

Execution additionally requires `--execute`, `--spending-authorized`, `--ledger`
and `--budget-usd`. Those flags are only for an operator who already has explicit
permission to spend. A preview or this documentation is not that permission.
Agree each person's fixed budget allocation first. **Do not give six independent
ledgers the entire project budget.** Their caps must fit the approved total;
the prior pilot budget is not automatically a main-run budget.

Start with the separately authorized small integration check before bulk
collection. Each route still enforces its request limits and conservative
reservation bounds. Provider rate limits, current availability and actual runtime
need measurement; a Saturday target is not a measured completion estimate.

## 2. Understand what is sealed

The additive `truth-discount-simulation-0.1` schema records:

- Original run and pair IDs, a unique generation-attempt ID and actor histories.
- All twelve phone transcripts, including regex-negative paths.
- Exact requests, responses, native usage/receipts, source hashes and runtime.
- `generation_status`, `evaluation_status: pending` and `metrics: null`.
- A private grading-item export bound to the exact attempt and transcript hash.

No judge is called during generation. Pending judgments are never represented as
`NOT_MENTIONED`, a zero score or a complete analysis. Historical phone branching
is preserved; later judging cannot recover a question that was never asked.
The historical 0.1/0.2 scored artifact contracts remain unchanged.

Payloads and the manifest are flushed to disk, with the manifest published last.
Read-only replay reconstructs actor requests, contexts, decisions, histories and
phone branches from the saved responses. File consistency and local receipts do
not independently authenticate provider weights or invoices.

## 3. Resume and hand over one shard

Resume uses the original command plus `--resume`, the same output directory,
the original ledger and its fixed cap. It skips verified completed generations.
If a sealed town failed (timeout, malformed reply, provider error), resume stops
and names it. Rerunning failed towns keeps only successful attempts, so it needs
the explicit `--regenerate-failed` flag; each failed attempt is retained under
`_incomplete`, logged in `resume_log.jsonl`, and counted per cell and status by
`simulation-status` (`failed_generation_attempts_by_cell`), so the analysis can
report it. Judge failures never trigger actor regeneration.

To ride out DeepInfra busy spells and incomplete towns without watching the
terminal, wrap the same `simulate` arguments with the recovery script. It waits
and resumes after busy rejections and after incomplete towns with no unclear
charge. With `--auto-reconcile` it also records unclear charges that have an
audited priced receipt (`scripts/reconcile_unknowns.py` now reads simulation
collections). A timeout without a priced receipt still stops for a person.

```sh
python scripts/run_until_done.py --simulate --auto-reconcile \
  --config configs/main_config.json --providers configs/providers.actor.json \
  --all-pairs --shard-count 6 --shard-index 0 --output outputs/main-owner-0 \
  --ledger outputs/ledgers/main-owner-0.jsonl --budget-usd 10 \
  --max-concurrent-towns 6 --regenerate-failed --execute --spending-authorized
```

For a custody transfer:

1. Stop the previous owner and confirm they will not resume their copy.
2. Transfer the complete output directory, execution plan, budget checkpoint,
   resume log, all archived attempts and the **original ledger journal** together.
3. Retain the same source revision, Python/OS runtime, config and provider
   manifest. The recipient injects their own credentials using the original
   environment-variable names. A different-runtime handover needs a separately
   reviewed migration; do not edit the saved runtime to bypass the check.
4. Inspect the transferred files with `simulation-status`, then resume with the
   original ledger identity and cap. Reconcile any held/unknown charges using
   the original provider records before resuming.

Do not discard/reset the ledger, truncate attempts, overwrite completed towns or
run duplicated custody copies. Local locks cannot coordinate two machines. A
hard crash before a valid seal can leave an unsealed directory; automatic resume
then fails closed. Preserve that directory and the original ledger for operator
review rather than deleting it and paying to start over unnoticed.

```sh
truth-discount simulation-status outputs/main-owner-0
truth-discount simulation-status outputs/main-owner-0 outputs/main-owner-1
```

Status reads `generation_complete` only when every shard of the allocation is
supplied and finished; finished shards without the rest read `shards_complete`.
Source versions are fingerprinted over the generation modules only (actor,
config, provider, contract, budget, scoring and bundle code) with line endings
normalized, so Windows and macOS/Linux checkouts of one commit match and later
CLI or judging edits do not block resume.

Cross-shard review rejects overlapping allocations, duplicates, incompatible
configs, source versions and used actor routes. Only the local credential
environment-variable name may differ in used route comparisons. It records
different Python/OS runtimes explicitly; identical environment behavior is not
inferred from matching source. Same-shard resume binds its exact runtime too.
Read-only status does not open or mutate a ledger and does not claim invoice or
complete ledger-history verification.

## 4. Judge saved phones with explicit profiles

Each profile pins model/route, request settings, output cap, rubric text/hash,
parser version/hash, source format and scoring population. Candidate templates
in `configs/judges/` are **unapproved**, with unknown prices and unverified account
access. They illustrate Haiku, adaptive Sonnet and OpenAI judge routes; none is a
selected primary judge or permission to execute.

`historical_funnel` preserves the existing rule-coded non-mention path;
`all_phones` sends every phone to the judge. These are distinct measurement
choices. The template's population is not approved automatically. A team-approved
policy must state which comparison/primary analysis uses which population. The
actor questions remain the same either way.

Preview does not read keys, reserve funds or make calls:

```sh
truth-discount judge-saved outputs/main-owner-0 \
  --profile configs/judges/haiku.example.json --output outputs/judgments
```

Multiple source roots can be listed. Duplicate sources, different retained
attempts under the same run ID and incompatible source contracts are rejected.
For the existing scored pilot only, use an explicit `source_format: legacy_pilot`
profile; the sources and original labels remain unchanged.

To compare the exact cases already sent to human raters, prepare a new candidate
from that existing `human_labeling.csv`. Matching uses the validation ID, target
and exact shown transcript; human/machine labels are never used for selection.
For the existing pilot example:

```sh
truth-discount prepare-panel-judging local/pilot-copy \
  --profile configs/judges/openai-luna.example.json \
  --source-format legacy_pilot --population all_phones \
  --profile-id luna-human-panel-candidate-v1 \
  --panel local/human_labeling.csv --out local/luna-panel-candidate.json
```

This writes an **unapproved** exact item-ID/source/hash selection. The example
all-phone population is a calibration candidate, not a change to the study's
primary population. Prepare the same panel for each candidate model and keep
separate untouched cases for final confirmation. Invalid, duplicate, foreign or
altered cases fail rather than being matched approximately. Without an explicit
selection, `judge-saved` plans the full supplied town collection.

Scoring execution has its own approval flags, verified route, credentials,
original bound ledger and spending cap. Results are saved under
`OUTPUT/profile_id`. New profiles coexist; changing a frozen profile in place is
rejected. Main outcomes stay outside judge selection. Only collect/inspect them
under the agreed access policy; this implementation supplies no such approval.

```sh
truth-discount judge-status outputs/main-owner-0 \
  --profile local/approved-judge-v1.json --output outputs/judgments
truth-discount compare-judges outputs/main-owner-0 \
  --profile local/judge-a.json --judge-output outputs/judgments \
  --profile local/judge-b.json --judge-output outputs/judgments
```

Judging resume reuses existing matching score items. Invalid labels are distinct
from missing/unobserved calls; they are not filled with zero. Repairs require
explicit `--retry-invalid` or `--retry-failed`, and unknown charges still block.
Every attempt remains in the append-only journal. First and latest results are
reported separately, without automatically choosing a favorable valid retry.
Sidecars retain native model responses, stop reasons and usage, bound to the
source attempt. A stopped judge never changes sealed actor files.

Comparisons report matched label/score/omission agreement and disagreements;
agreement between models is not human accuracy. Descriptive town/twin summaries
are not automatic approval for a primary analysis or a replacement for the
paper's final analysis policy.

## 5. Judge settings and human checks

Two independent human raters can complete the planned audit. Each labels without
the machine labels, condition identifiers or the other rater's answers.
Retain disagreements before adjudication and report human-human agreement.
Cases used to choose a judge or tune its rubric cannot also be an untouched
confirmation set. Do not change the existing audit threshold or claim it is a
universal publication requirement.

Different models need explicit compatible profiles, not a model-name swap.
Current Anthropic documentation supports adaptive thinking and explicit effort
for Sonnet 5.5/Opus 5.5; both reject disabled thinking. Thinking consumes the
output cap and billing even when hidden. The adapter merges `output_config.effort`
with `output_config.format`. Refusals, exhausted output budgets and malformed
evidence remain observed failures, with costs retained.

OpenAI judges use an explicit `reasoning_effort` and native structured-output
profile without changing actor settings. GPT-6 Astra is a strong reference
candidate and GPT-6 Luna is a lower-cost candidate, subject to agreement with the
human labels. Neither is selected merely because a template exists. Native Batch
is not implemented by this synchronous workflow; no Batch discount is assumed.

Primary documentation checked 10 November 2026:

- [Anthropic thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
- [Anthropic effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Anthropic structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenAI GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [OpenAI GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)

## 6. Offline verification

`simulation-demo` produces four synthetic towns without a ledger or network.
The tests inject fake native HTTP responses, block actual network access, compare
actor behavior with the historical runner, and exercise resume, handover,
tampering, multiple profiles, malformed outputs and unknown-charge holds.
These checks are software evidence, not a real smoke test, a human audit or a
completed main experiment.
