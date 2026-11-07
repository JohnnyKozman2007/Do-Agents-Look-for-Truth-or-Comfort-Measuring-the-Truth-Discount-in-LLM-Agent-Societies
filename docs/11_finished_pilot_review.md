# Reviewing the finished pilot

This workflow inspects saved exports. It makes no model calls, changes no labels and authorizes no spending. Use a finished snapshot from the person running the pilot. Do not point these commands at an actively changing collection.

## Export handoff

Keep each collection's `execution_plan.json`, `budget_checkpoint.json`, active town folders, `_incomplete/` attempts and any `rejudged.jsonl` together. Include the executed config and provider snapshots stored in the town bundles. Preserve the code revision and any local modifications used for collection. Keep an unmodified copy of the matching budget journal separately. Do not include `.env` files or API keys.

The smoke test and later batch may have separate plans. Review both plans. A complete 16-town smoke test does not establish a complete 624-town pilot. Check that the batches use the same config, provider manifest and evidence kind, that their run IDs do not overlap and that their union contains the intended matched pairs. Do not silently combine different versions or choose the best attempt for a town.

## Coverage and receipt review

```bash
PYTHONPATH=src python3 -m truth_discount.cli review-collection \
  outputs/pilot --out outputs/pilot-review \
  --ledger-copy exports/pilot-budget.jsonl
```

The optional `--ledger-copy` is a supplied saved journal, not a key or provider connection. The review inspects another temporary copy so opening the budget journal cannot repair or alter the supplied file. Without it, ledger verification remains unavailable.

Check the saved plan against its config/provider hashes and configured run mappings. Compare every expected ID with the exported towns, including pairs where both twins are absent. Report incomplete and unexpected runs. A missing or unverifiable plan prevents a claim that collection coverage is complete.

Keep receipt costs, unknown charges and the entire bound ledger distinct. The ledger can include other batches and later judge attempts. Its total therefore need not equal the active town receipt subtotal. Neither receipt replay nor a matching ledger establishes an independently verified provider invoice. Preserve original and archived attempts even when the final active run completed.

The review records a rejudge overlay without replacing original labels. It does not establish a repaired-label analysis policy or verify that the overlay includes every extra charge. Check the original failures, repair attempts, receipts and ledger together before describing their costs or outcomes.

## Descriptive analysis and human audit

After resolving coverage and provenance problems, use a separate new output directory:

```bash
PYTHONPATH=src python3 -m truth_discount.cli analyze \
  outputs/pilot --out outputs/pilot-analysis
PYTHONPATH=src python3 -m truth_discount.cli audit-sample \
  outputs/pilot --out outputs/pilot-human-audit
```

The analysis uses original saved labels. Read each estimate with its available and missing counts. Failed or unobserved judgments are not silence. The four pilot profiles support the comparisons documented in the [writing handoff](09_writing_and_analysis_handoff.md), not six independent attribute effects or the future main study's confirmatory tests.

The human audit requires 100 eligible original LLM-judged calls, 25 per truth-condition and listener-layer stratum. A short stratum stops sampling. Do not reduce the target or substitute rule-coded omissions to make the command succeed. The pool restriction means this audit does not validate the whole omission-detection pipeline.

Share only `labeling_sheet.csv` and `labeling_instructions.md` with raters. Keep the private files and the original sample unchanged. After raters independently return their completed sheets:

```bash
PYTHONPATH=src python3 -m truth_discount.cli audit-score \
  outputs/pilot-human-audit sheets/rater-one.csv sheets/rater-two.csv
```

No human agreement result exists until real raters supply labels. Agreement with the automated judge is not accuracy against a human gold standard.

## Paper handoff

Describe the actual executed twin construction, prompts, model settings and revisions. The updated Google Doc and repository differ on which part of the twin changes. Preserve that discrepancy and reconcile it against the exports. Do not change a running or completed experiment to make the sources agree.

Use the [related-work comparison](10_related_work.md) and [bibliography](../paper/references.bib) for the introduction. Confirm the shared paper workspace with the coordinator. Leave findings out of the abstract until the actual data review is complete. Any main-study inference, multiplicity or label-repair policy still needs a dated prospective decision before that study.
