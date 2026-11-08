# Judge validation after the reported 400-call comparison

Prepared 8 November 2026. This is a validation proposal and offline preparation workflow. It does not replace the primary judge, change a running experiment, authorize calls or register a confirmatory analysis.

## Evidence currently available

Rosh reports comparing 400 first-hand phone calls with Sonnet, Opus and GPT, oversampling the original UNCERTAIN/SKEPTICAL labels. The supplied excerpt contains the phrase `... (49 lines left)`. The full findings document, row IDs, selection script, raw alternate responses and receipts have not been supplied in this checkout. The reported kappas and truth discounts therefore remain unreproduced.

The displayed label columns each total 400. The transition tables total their declared 150 rows, and 42/400 is 10.5%. Rounded agreements are compatible with the reported kappas. These arithmetic checks do not establish whether any individual label is correct.

## Findings that affect the next step

1. **Separate rule labels from model labels.** The phone-funnel rule assigns NOT_MENTIONED when none of the listener's replies contains the literal `concert` or a complete artist name. That path makes no judge request. A reconstructed judge input for such a call is useful, but it is not a recovered original Haiku request. The existing audit deliberately samples valid LLM-judged calls and excludes this path.
2. **Keep model and procedure comparisons distinct.** Original Haiku uses label plus quote. The alternates reportedly use rationale first, different thinking settings and an 8,000-token limit. Original settings allow 250 output tokens. Equal dialogue does not make these the same evaluation procedure. Enum-valid labels also do not establish compliance with the original quote contract.
3. **Do not infer human correctness from consensus.** Cross-family agreement is useful evidence of disagreement patterns. It does not rule out shared rubric errors or establish that Sonnet is the best human-aligned judge. The existing 0.85 target concerns human-versus-judge agreement, not model-versus-model agreement. LLM-judge studies explicitly examine prompt and reasoning biases alongside human validation. [Zheng et al.](https://arxiv.org/abs/2306.05685), [G-Eval](https://aclanthology.org/2023.emnlp-main.153/).
4. **Treat the enriched sample as a diagnostic sample.** Its label quotas differ from natural prevalence. Kappa depends on marginal distributions, so enrichment need not lower it. Source-stratum sizes and inclusion probabilities are needed for population-weighted agreement. Design weighting of confusion counts differs from ordinal weighted kappa. [Cohen's definition and the official implementation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html), [Feinstein and Cicchetti](https://pubmed.ncbi.nlm.nih.gov/2348207/).
5. **Preserve the analysis population and aggregation.** The current code scores both configured listener layers. A first-hand-only primary population needs a dated design decision. A label-selected subset of 400 rows cannot establish the configured matched-town truth discount without town/pair identities, complete denominators and the aggregation rule. Report exact-label, numerical-score and omission agreement separately. FACT/CHECKED_TRUE and SKEPTICAL/CHECKED_FALSE pairs share their numerical score.
6. **Separate targeted diagnosis from broader validation.** The 42 unanimous disagreements are useful stress cases. Reviewing only them cannot reveal shared errors among agreement cases or estimate overall accuracy. Use a separate probability sample, including rule-coded omissions and invalid judgments, for whole-pipeline calibration. Selection based on the index result can bias validation. [Begg and Greenes](https://pubmed.ncbi.nlm.nih.gov/6871349/).
7. **Keep the announced proposition.** Artist-neutral treatment means applying symmetric rules to either name. A poster confirming the other artist can disprove the announced claim. A reported check must say what it confirmed or contradicted, read in the context of the final relevant statement. Actual GO actions remain a separate private diagnostic. A CHECKED label alone is not proof that an agent performed the action.

## Offline preparation

```bash
PYTHONPATH=src python3 -m truth_discount.cli prepare-judge-validation \
  outputs/pilot --out outputs/judge-validation-calibration --size 100 --seed 20261108
```

Use a finished, immutable collection snapshot. The command inventories every completed phone transcript from both layers, including rule-coded omissions and invalid or missing judge labels. It records whether an input came from an actual saved judge request or was reconstructed from the saved target claim and dialogue.

This is a separate calibration package. It does not widen or replace audit-v1, and its output must not be passed to audit-v1 scoring as though the populations were identical. The original audit's limitations remain recorded in [the audit guide](08_analysis_and_audit.md).

The probability sample uses a fixed seed and equal quotas over truth condition and listener layer. Its private metadata records each pool size, sampled count and inclusion probability. A short stratum stops preparation. The source inventory and private crosswalk retain label provenance, original prompts/settings and checking decisions. Source files remain unchanged and rejudge overlays remain unapplied.

Give raters only the blank human sheet and its instructions. Those files contain the target artist, full phone dialogue and original rubric. They omit model labels, rationales, condition metadata and actual GO decisions. The dialogue can still contain contextual clues, so metadata masking does not establish perfect blinding or independent raters.

The 42-case diagnostic set needs Rosh's actual source IDs. Do not invent that set or select cases from the aggregate tables. Keep rubric-development cases separate from any later validation used to accept a revised rubric. Record overlap if cases appear in more than one set.

## Data and control handoff

Request the complete findings file and:

- The 400 original run/seat/custom IDs, source and input hashes, actual Haiku/rule provenance, source-label pool counts, sampling seed or selection script and any exclusions.
- Exact alternate prompts, response schemas, routes/model IDs, generation settings, raw responses, parsed labels and receipts for every attempt.
- Condition, listener layer, town and twin-pair mappings in a private crosswalk, sufficient to reconstruct the stated score calculation.

The minimum missing control is Haiku on the same selected inputs under the alternates' exact format and settings, with any unsupported-setting differences recorded. That would distinguish the original pipeline from the changed Haiku pipeline and compare models under the changed format. It does not retrospectively create supporting quotes in alternate responses that never supplied them.

A cleaner subsequent comparison can use a common supporting-quote contract across models, with format and settings separately recorded. The [control proposal](judge_validation_controls.proposal.json) is deliberately non-executable and unapproved. No additional judge calls follow from preparing this package.

Use human evidence and explicit measurement criteria to choose a dated judge/rubric policy before full rescoring or the main study. Preserve original pilot labels and show revised-label analyses as separate sensitivity results. Keep human calibration, model consensus and paired pilot estimates distinct.

## Compatibility and operational boundaries

Keep historical phone conversations and funnel decisions intact. Removing the regex from conversation stopping changes which later questions were asked. Removing the forced label from future judging is a separate decision. Rejudging saved dialogue cannot reconstruct responses to questions that were never asked.

The existing town schemas are 0.1 and 0.2. The analysis bundle's 0.3 number is a different namespace. Quote parsing also changed historically from exact substring matching to ignoring whitespace. Some older malformed labels may need their actual parser revision to replay. Do not reinterpret or repair such records silently. The new package remains an immutable sidecar and does not change either historical reader or parser.

New main `61702a0` also adds optional automatic unknown-charge reconciliation. This validation work does not use or enable it. A reservation-based amount is not an independently verified invoice or a proven charge bound. The existing hold on our credit use remains in force.
