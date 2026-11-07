# Synthetic review examples

These examples come from the mixed offline demo on 6 November 2026, using pilot configuration 1.1.0. The demo completed four synthetic towns, with one matched pair under each configured model key. It invoked no provider API or named model.

`review-receipt.json` records the observed validation counts. The two Markdown transcripts show the rumor and truth-twin scenes for the first model key. `judge-input.json` shows one exported judge request, with the rubric and phone dialogue only. The opaque request ID maps to private run information in the full local bundle.

Run `bash scripts/offline_check.sh` to repeat the tests and generate fresh temporary bundles. To keep all four bundles, run:

```bash
PYTHONPATH=src python3 -m truth_discount.cli demo --output outputs/review-demo
PYTHONPATH=src python3 -m truth_discount.cli summarize outputs/review-demo
```

The generated timestamps and elapsed times will differ. Fixture responses and descriptive scores follow the deterministic local backend. These files provide software-validation examples and cannot support empirical research claims.
