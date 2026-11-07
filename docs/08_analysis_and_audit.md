# Pilot analysis and human judge audit

These commands read saved bundles and make no model calls. They do not alter the source runs. The output is descriptive and exploratory. A generated report does not establish a confirmatory result, a frozen analysis specification or publication readiness.

Start with the [finished-pilot review](11_finished_pilot_review.md). Its `review-collection` command checks declared run coverage and saved receipt evidence, including whole missing pairs that an observed-only analysis cannot count. A successful command means the review ran. Read its coverage and ledger statuses before claiming the pilot is complete.

## Analysis

```bash
pip install -e ".[analysis]"    # optional statistical models and charts
PYTHONPATH=src python3 -m truth_discount.cli analyze outputs/pilot --out outputs/pilot-analysis
```

Use a finished collection snapshot and a new output directory. All active bundles, including excluded incomplete runs, must share the same configuration, provider manifest and evidence kind. Mixed fixture, mocked and development data are rejected. Saved input-manifest hashes, source hashes and dependency versions identify the analysis inputs and implementation.

| File | Contents |
| --- | --- |
| `report.md` | Descriptive tables, denominators and interpretation limits |
| `summary.json`, `cells.csv` | Paired cell estimates, counts, interval status and model diagnostics |
| `conditions.csv` | Each model/cell/condition across all completed towns, including unmatched towns |
| `pairs.csv` | Matched twin rows, with missing outcomes retained explicitly |
| `listeners.csv` | All expected listener rows, with valid, invalid and missing judgments distinguished |
| `truth_discount_by_cell.png` | Available paired cell estimates and intervals |

The conditional truth discount is the within-pair difference of expressed belief, excluding valid `NOT_MENTIONED` labels. Silence sensitivity scores assign those valid omissions 0 or 0.5. Invalid or missing judgments remain missing under every score. Show both twins' means, omissions, label counts and GO denominators alongside the difference. An incomplete belief outcome must not erase an otherwise observed verification decision.

The bootstrap resamples matched twin pairs with a recorded seed. Each estimate records its usable count. Undefined estimates, insufficient sample sizes and degenerate fixture intervals retain explicit status. Pilot comparisons with the Maximum Skepticism cell are exploratory profile comparisons. The pilot has four profiles and cannot identify all six factor effects or the planned interactions.

The optional town-intercept mixed fit preserves the existing proposed model. Its groups do not automatically capture dependence between matched twin towns. Town-clustered and twin-pair-clustered OLS are exploratory sensitivity fits. Model convergence, design rank, nonfinite coefficients and fit failures are reported. Without the optional packages, fits are marked not run. These outputs do not implement the main study's ten confirmatory contrasts or multiplicity procedure.

The generated main-study configuration can produce descriptive per-factor tables, but collection and a final confirmatory policy remain separate decisions. The fixed four-cell pilot is not a completed factorial experiment.

### Transmission and rejudging

Concert/artist mentions and board/artist keywords are diagnostic proxies. They do not establish semantic evidence transfer or an agent's internal motive. The verification price is a fixed fictional cost, with no zero-cost comparison in this pilot.

The analysis records a root `rejudged.jsonl` overlay's presence and hash, but uses original saved labels by default. It does not silently replace malformed labels with a preferred later attempt. A repaired-label analysis needs an explicit policy and separate reporting of original and repaired results, attempt counts and costs. Original bundles remain unchanged.

Archived incomplete attempts are excluded from outcome comparisons and recorded separately. Their receipts and the bound ledger still matter for total cost. Unexpected, mismatched or completed archived attempts need review rather than automatic outcome selection.

## Human judge audit

```bash
PYTHONPATH=src python3 -m truth_discount.cli audit-sample outputs/pilot --out outputs/judge-audit
PYTHONPATH=src python3 -m truth_discount.cli audit-score outputs/judge-audit sheets/alex.csv sheets/sam.csv
```

The default sample is 100 valid original LLM-judged phone calls, with 25 from each truth-condition by listener-layer stratum. Sampling uses a fixed seed and shuffled neutral audit IDs. A short stratum raises an explicit error rather than silently changing the allocation. A custom software-check sample is not automatically the declared 100-call human audit.

The pool excludes invalid or missing automated labels and rule-coded omissions that did not receive an LLM judge call. Audit agreement is therefore conditional on this pool. A separate sample would be needed to audit that omission rule or the entire labeling pipeline.

Share only the blank `labeling_sheet.csv` and `labeling_instructions.md` with raters. Private keys and metadata contain the run, model, cell, condition, automated label and provenance fingerprints. Do not share the whole audit directory. The sheet omits those metadata, while the dialogue itself may still reveal contextual clues.

The audit package binds the exact source bundle files, prompts, judge revision, sample allocation and original displayed text. Scoring verifies that binding and rejects changed source material, modified keys, altered dialogue rows, missing or extra IDs, blank labels and labels outside the rubric. It records agreement with the automated judge, between raters and within strata. Undefined kappa remains undefined.

The configured 0.85 kappa target is a diagnostic benchmark. The automated judge is not a gold-standard human answer. A low value calls for review of disagreements and an explicit subsequent decision. It does not automatically authorize another model, paid rejudging or replacement of the reported labels.

See [the writing handoff](09_writing_and_analysis_handoff.md) and [related work](10_related_work.md) for the interpretation and design-version limits.
