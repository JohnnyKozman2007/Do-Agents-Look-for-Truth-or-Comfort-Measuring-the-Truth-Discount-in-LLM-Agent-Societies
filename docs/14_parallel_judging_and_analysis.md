# Concurrent saved judging and analysis handoff

PR #10 fixes the simulation workflow. Main commit
`8151c3951cb88e0ec86d721d8b3b3faeb4d24a6a` contains its reviewed resume and source
integrity changes. Use that generation revision for the shared allocation. This
follow-up changes judging, analysis and CLI files only. It preserves the eight
generation modules that the actor bundles fingerprint.

The spending hold remains. Neither this document nor a proposed $10 personal
cap authorizes a provider call. The approximately $6.20 actor cost per shard
comes from scaling old pilot receipts. Different failures, token counts and
provider load can change costs and runtime. Judge costs require a separate
allocation. Confirm the shared actor manifest, six owners and their disjoint
indices before any separately authorized integration test.

`configs/providers.actor.proposal.json` extracts the two agreed actor routes
from the existing pilot manifest. It contains environment-variable names rather
than keys. Approval remains false and prices require current verification.
Its copied rates describe the earlier pilot settings, not a new pricing check.
After the team approves one common copy, use that exact file on every shard.

## Bounded concurrent judging

The preview accepts `--max-concurrent-judgments` between 1 and 32. The frozen
native route can impose a lower concurrency limit. One profile output retains
one original ledger and cap. Its append-only journal retains every started and
finished attempt. A worker failure stops new scheduling and drains calls that
already started so their receipts survive.

```sh
truth-discount judge-saved outputs/main-owner-0 outputs/main-owner-1 \
  --profile local/approved-judge.json --output outputs/judgments \
  --max-concurrent-judgments 4
```

This command previews without credentials or calls. Execution still needs both
authority flags and the original ledger/cap. Resume must retain the original
requested concurrency. Read-only replay recovers it from the saved plan. A
different judging implementation remains a different freeze. Do not modify
saved source hashes to bypass an implementation mismatch.

First attempts remain the default analysis population. `--retry-invalid` and
`--retry-failed` authorize explicit repairs only after the original costs and
unknown reservations permit them. An interruption without a terminal receipt
still needs operator reconciliation. Concurrency does not make resubmission of
an uncertain charge safe.

## Join labels without changing actor files

`analyze-scored` audits the original bundles, strict judge replay and exact
generation-attempt/phone identities. It constructs compact analysis views
without retaining the full actor histories in memory. The new output contains
listener, matched-pair, condition, cell and main-factor tables. It keeps
unselected, unobserved and invalid outcomes missing and reports all generated
towns and expected listeners in its denominators.

```sh
truth-discount analyze-scored outputs/main-owner-0 outputs/main-owner-1 \
  --profile local/frozen-judge.json --judge-output outputs/judgments \
  --out outputs/analysis-first
```

The output directory must sit outside all source and judgment roots. Source
payloads and judge journals must remain unchanged during the read. The default
`first_only` policy uses first attempts even when later repairs succeed. A
separate output with `--attempt-policy latest_sensitivity` uses the latest
attempt, including its failures. It never selects the best valid retry.

Main development outcomes require `--outcomes-authorized` after the team freezes
judge selection, rubric, analysis and access rules. An approved profile alone
does not supply this authorization. A 100-phone human calibration selection is
not full-town main data. Partial shards and selected panels remain incomplete
in the coverage table and cannot produce a full confirmatory model.

## Resolve the model policy before main outcome access

The specification lists six main truth-discount contrasts and four factor-pair
interactions. The earlier additive listener model cannot estimate those four
interactions. The candidate model adds the corresponding factor-pair terms and
truth-by-factor-by-factor terms. The proposed contrasts average predictions
over the fixed factorial grid and both artist identities rather than using
the observed sample prevalence as weights.

The policy generator writes an **unapproved proposal** without reading outcomes:

```sh
truth-discount analysis-policy --config configs/main_config.json \
  --profile-sha256 "$JUDGE_PROFILE_SHA256" --source-sha256 "$SOURCE_SHA256" \
  --out local/analysis-policy.proposal.json
```

The team still needs to decide:

- Whether the Holm family contains 10 tests per actor or all 20 paperwide tests.
- Contrast directions, two-sided testing, equal grid weighting and the model's
  conditional-listener estimand. That estimand differs from an equally weighted
  mean of paired-town truth discounts when mentioning-listener counts differ.
- The available-listener cohort, first-attempt policy and separate repair
  sensitivity. Invalid and unobserved judgments never become silence.
- The town-intercept model covariance and treatment of matched-twin dependence.
  The candidate uses model-based covariance. It does not claim to implement
  cluster-robust LMM standard errors. The existing pair-clustered exploratory
  analysis is a separate sensitivity, not a substitute without agreement.

Approval requires clearing the explicit unresolved list and binding the exact
configuration, judge profile, source and attempt policy. The model uses all
ten planned contrast slots per actor. A failed or unavailable test retains its
slot in Holm's family. Rank-deficient designs, nonconvergence, singular fits,
nonfinite values and zero standard errors remain unavailable rather than
becoming significant results. The proposal implements no outcome-driven model
selection and makes no claim about novelty or empirical findings.

Without an approved policy, `analyze-scored` writes descriptive tables and a
blocked model status. With a valid approved policy and complete study coverage,
`--analysis-policy local/frozen-analysis-policy.json` connects the saved labels
to the planned model and Holm output. An offline test never approves that
policy or establishes judge accuracy.

## Independent human confirmation and release gates

Two raters label the same pilot cases independently. Preserve untouched
confirmation cases before changing a rubric or choosing a judge. Reconcile
disagreements under a recorded rule and compare candidates on the same phone
IDs. Agreement between two models is not human-label accuracy. The new code
does not fill human labels or choose Haiku, Sonnet or an OpenAI model.

Before bulk execution, confirm funding, each person's cap and API access, the
common actor manifest and source revision, custody/resume ownership and a
separately authorized small integration test. Measure real cost, native
receipts, GO/SKIP behavior and throughput there. Saturday remains a target
until those measurements establish a feasible schedule.
