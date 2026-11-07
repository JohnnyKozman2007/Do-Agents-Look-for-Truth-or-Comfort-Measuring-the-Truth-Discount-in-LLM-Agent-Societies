# Pilot analysis and judge audit

Both commands read a finished output directory. Every town is replay-audited first; only completed towns are used, and incomplete ones are counted in the report. Neither command calls a model.

## Analysis

```bash
pip install -e ".[analysis]"    # optional: statsmodels, pandas, matplotlib
PYTHONPATH=src python3 -m truth_discount.cli analyze outputs/pilot --out outputs/pilot-analysis
```

The output directory holds:

| File | Contents |
| --- | --- |
| `report.md` | Paper-ready tables per agent model |
| `cells.csv`, `summary.json` | The same numbers, machine-readable, with the model fits and settings |
| `pairs.csv` | One row per complete twin pair |
| `listeners.csv` | One row per scored listener, for any other statistics package |
| `truth_discount_by_cell.png` | Truth discount per cell and model, with 95% intervals |

Per model and cell, the report gives:

- **Truth discount:** the truth-twin belief minus the rumor belief, averaged over twin pairs ([metrics](04_metrics_and_judge.md#6-the-truth-discount-formula--statistical-estimation)). The primary score excludes `NOT_MENTIONED`.
- **Sensitivity bounds:** the same difference with silence counted as 0.0 and as 0.5.
- **Each twin's values:** belief, omission rate, first-hand and second-hand GO rates, how often first-hand listeners mentioned the concert to their partner, and how often listeners who checked passed the board's evidence on.
- **Cell contrasts:** each cell's truth discount minus the Maximum Skepticism cell's.
- **Mixed model:** `belief ~ truth * cell + real artist`, with a random intercept per town, plus the same model fit by OLS with town-clustered standard errors. The four pilot cells set all knobs together, so cell indicators stand in for the six knob terms of the main specification. Without statsmodels the model is marked not run, and the tables are still written.

For the main study (`configs/main_config.json`), the report instead gives each specification factor: closeness, authority, reliability, wealth, gender and age, with gender and age split from the identity knob. For each it shows the truth discount at both levels and their difference with a 95% interval, as level A minus level B in `factorial_levels` order: close friend − stranger, mayor − citizen, good record − poor record, rich − poor, woman − man, old − young. These also go to `knobs.csv` and `truth_discount_by_knob.png`. The mixed model uses the specification's terms, `belief ~ truth * (closeness + authority + reliability + wealth + gender + age) + real artist`. All 64 cells stay in `cells.csv`.

Intervals are 95% percentile bootstraps over twin pairs: 5,000 resamples with a fixed seed, so reruns give identical numbers. A pair whose twin has no mentioning listener has no conditional belief. It is dropped from the truth discount but kept in both bounds; each estimate's `_n` column gives its count.

## Judge audit

```bash
PYTHONPATH=src python3 -m truth_discount.cli audit-sample outputs/pilot --out outputs/judge-audit
PYTHONPATH=src python3 -m truth_discount.cli audit-score outputs/judge-audit sheets/alex.csv sheets/sam.csv
```

`audit-sample` draws 100 validly judged phone calls with a fixed seed: 25 from each combination of twin condition and listener layer. A short stratum is topped up from the others, and the actual counts are recorded in `audit_meta.json`. The rows are shuffled before they are written.

- `labeling_sheet.csv` shows only the announced artist and the phone-call lines, which is what the judge saw.
- `labeling_instructions.md` holds the judge's label definitions.
- `audit_key_PRIVATE.csv` maps each row to its run, seat, model, cell, condition and judge label. Keep it away from raters until scoring.

Each rater fills a separate copy of the sheet, named after themselves. `audit-score` rejects blank, unknown, duplicate or missing labels. It reports:

- Cohen's κ of each rater against the judge, which must be at least 0.85;
- κ between raters;
- agreement within each stratum;
- the most common disagreements.

If κ is below 0.85, the specification moves the judge up to Claude Sonnet 5.5 and re-judges.
