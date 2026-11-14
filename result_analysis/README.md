# Result analysis

Analysis code for the simulation output: how often listeners check the noticeboard (Tier 2), how much they believe the truth versus the rumor (Tier 3), and how robust and mechanistic those results are (Tier 4). Every metric reads saved run folders and, for the belief metrics, a file of belief labels. **Nothing here makes a model call.**

Each run produces a self-contained HTML report (inline SVG charts, light and dark theme, no external assets) plus a CSV for every table. `run_all.py` runs all tiers and writes **one combined report**; the per-tier scripts write separate reports.

| Tier | Needs labels? | Metrics | Entry point |
|---|---|---|---|
| 2: behavioral outcomes | No | 7 first-hand check rates, 8 second-hand behavior, 9 who checks | `tier2/run_tier2.py` |
| 3: truth discount | Yes | 10 primary truth discount, 11 checkers vs non-checkers, 12 ten planned contrasts, 13 asymmetry, 14 override and cell map, 15 second-hand truth discount | `tier3_4/run_tier34.py` |
| 4: robustness and mechanism | Mostly | 16 model comparison, 17 variance and seed planning, 18 keyword transcript pass, 20 top-10 DNA rule | `tier3_4/run_tier34.py` |

All tiers in one report: `run_all.py`. Metric numbers follow the analysis plan. Metrics 1-6 (data audit and judge validation), 19, 21 and 22 are not part of this folder.

## Contents

- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Inputs](#inputs)
- [Core definitions](#core-definitions)
- [Tier 2 metrics](#tier-2-metrics-no-labels-needed)
- [Tier 3 metrics](#tier-3-metrics-truth-discount)
- [Tier 4 metrics](#tier-4-metrics-robustness-and-mechanism)
- [Statistical methods](#statistical-methods)
- [Outputs](#outputs)
- [Limitations and interpretation](#limitations-and-interpretation)
- [Testing](#testing)
- [Layout and extending](#layout-and-extending)

## Requirements

Python 3.11 or later, plus `numpy` and `pandas` (see `requirements.txt`). No statsmodels, scipy or matplotlib: the bootstrap, logistic and linear regressions, Holm correction, chi-square tail and charts are implemented in `common/`. This folder is independent of the repository's standard-library-only runtime; install its two dependencies separately:

```bash
pip install -r result_analysis/requirements.txt
```

## Quick start

Run from anywhere; paths below are examples.

```bash
# Everything in one combined report (omit --labels to run Tier 2 only)
python3 result_analysis/run_all.py \
  --data /path/to/shard-0/outputs/main-owner-0 /path/to/shard-1/outputs/main-owner-1 \
  --labels labels_shard0.csv labels_shard1.csv \
  --judge-name "Gemini 3.7 Flash" \
  --out ./analysis_out/all

# Or one tier at a time, each with its own report.
# Tier 2: behavioral, no labels
python3 result_analysis/tier2/run_tier2.py \
  --data /path/to/shard-0/outputs/main-owner-0 /path/to/shard-1/outputs/main-owner-1 \
  --out ./analysis_out/tier2

# Tiers 3 and 4: belief-based, needs labels
python3 result_analysis/tier3_4/run_tier34.py \
  --data /path/to/shard-0/outputs/main-owner-0 /path/to/shard-1/outputs/main-owner-1 \
  --labels labels_shard0.csv labels_shard1.csv \
  --judge-name "Gemini 3.7 Flash" \
  --out ./analysis_out/tier34
```

Open `result_analysis_report.html` (combined), `tier2_report.html` or `tier34_report.html` in a browser. On a single 1,664-town shard, Tier 2 takes about 15 seconds, and Tier 3/4 about 25 seconds on a first run (7 seconds once the listener and text tables are cached).

| Option | Applies to | Meaning |
|---|---|---|
| `--data DIR [DIR ...]` | both | Folders that hold the run directories. Pass several to pool shards; the code stops if a `(run_id, seat)` appears twice. |
| `--out DIR` | both | Output folder (created if needed). |
| `--labels FILE [FILE ...]` | all, 3/4 | Belief label files, see [labels](#belief-labels). Optional for `run_all.py` (omitted = Tier 2 only). |
| `--judge-name TEXT` | all, 3/4 | Judge name shown in the report header. |
| `--boot N` | both | Bootstrap resamples (default 2000). |
| `--refresh` | both | Rebuild the cached listener and text tables. |
| `--only m10,m12` | `run_tier34.py` | Run only these metrics. |
| `--no-text` | all, 3/4 | Skip the keyword pass (metric 18), which re-reads every `town.json`. |

The listener table is cached in the output folder as `listeners_<hash>.csv`, keyed by the set of `--data` folders. Rerun with `--refresh` if the underlying runs change. A console line reports label coverage; under 95% labeled triggers a warning and pairs missing a twin's labels are dropped and counted.

## Inputs

### Run folders

`--data` points at a folder such as `outputs/main-owner-0` that contains one directory per town, named `<model>__cell-<n>__layout-<n>__rep-<n>__<condition>` (condition is `rumor` or `truth_twin`). Other entries (`_incomplete/`, ledgers, checkpoints) are ignored. Per town the code reads:

| File | Fields used |
|---|---|
| `town.json` | `run_id`, `pair_id`, `model_key`, `condition_type`, `cell_id`, `layout_id`, `repetition_id`, `announced_artist`, `real_artist`, `source_persona_id`, `knobs`, `seating_assignment`, `catch_up_pairs`, `scene_2_first_hand_decisions`, `scene_3_poster_evidence_passed`, `scene_4_second_hand_decisions`, and for metric 18 only `scene_3_catch_up_transcripts` and `scene_5_phone_transcripts` |
| `config.json` | the persona table (id, name, occupation, conversational style); read once from the first run |

Twin towns of one pair share `pair_id`. Each town has 12 listeners: seats 1-6 hear the source first-hand and decide GO/SKIP before seeing any poster; seats 7-12 each hear from one first-hand partner at the afternoon catch-up and then decide.

### Belief labels

Tier 3/4 needs one label per listener phone call, as a `.csv` or `.jsonl` file with at least:

| Column | Notes |
|---|---|
| `run_id` | the town directory name |
| `seat` | 1-12 (`seat_id` and `seat_id_private` are also accepted) |
| `label` | one of `FACT`, `UNCERTAIN`, `SKEPTICAL`, `CHECKED_TRUE`, `CHECKED_FALSE`, `NOT_MENTIONED` (`choice` is also accepted) |

Other columns are ignored. Torn `.jsonl` lines are skipped, labels outside the rubric are dropped with a warning, and duplicates keep the last row. Unlabeled listeners stay missing in every estimate; they are never imputed.

## Core definitions

- **Listener row.** One row per listener per town (12 per town), carrying the town's knobs, the listener's persona and seat, decision, and for second-hand listeners the partner's decision and the runner's `evidence_passed` flag.
- **Knobs.** Six source cues: closeness (close friend vs stranger), authority (mayor vs citizen), reliability (good vs poor record), wealth (rich vs poor), gender and age. A **cell** is one combination of the six (64 cells); a **DNA** is a cell viewed as a source profile.
- **Belief score.** `FACT` and `CHECKED_TRUE` = 1, `UNCERTAIN` = 0.5, `SKEPTICAL` and `CHECKED_FALSE` = 0 (from `docs/04_metrics_and_judge.md`). `NOT_MENTIONED` is excluded from the primary mean and reported as an omission rate. Sensitivity scores set it to 0 (`NOT_MENTIONED=0`) or 0.5 (`NOT_MENTIONED=0.5`).
- **Truth discount (TD).** Mean belief in the truth twin minus mean belief in the rumor twin, computed per twin pair from the listeners with a valid score. A pair is usable when both twins have at least one valid score. A smaller TD means the rumor is believed relatively more.
- **Independent unit.** The twin pair. Listeners in a town share one source interaction, so they are not treated as independent.
- **Placebo.** First-hand listeners choose GO/SKIP before seeing any poster, so rumor and truth twins differ at that choice only by sampling noise. This is used as a built-in noise floor in metrics 7 and 11.

## Tier 2 metrics (no labels needed)

All Tier 2 metrics use the GO/SKIP decisions already in `town.json`.

### Metric 7: first-hand check rates

*Which source cues make listeners pay the $5 fare to check?* First-hand listeners only.

- Check (GO) rate by model and twin, with cluster-bootstrap CIs.
- **Placebo test:** truth-twin minus rumor-twin check rate, expected near 0.
- Knob contrasts: rate differences for each of the six knobs, pooled and per model.
- Adjusted effects: additive logistic regression with cluster-robust SEs, reported as odds ratios.
- Four planned 2x2 interactions (closeness x reliability, authority x reliability, wealth x reliability, closeness x authority) as difference-in-differences, plus 2x2 heatmaps.
- 64-cell heatmaps of check rate per model, and a malformed-decision table (malformed decisions are kept as SKIP, as the runner defined).

Tables: `m7_overall_rates`, `m7_placebo_truth_vs_rumor`, `m7_twin_agreement`, `m7_knob_contrasts`, `m7_logit_additive`, `m7_interactions`, `m7_cell_rates`, `m7_malformed_decisions`.

### Metric 8: second-hand behavior

*How does evidence spread one hop, and does it change a second-hand listener's choice to check?*

- Funnel: partner checked, evidence passed on, second-hand listener checked.
- Second-hand GO rate by partner state (partner skipped; checked, evidence not passed; checked, evidence passed), and truth-minus-rumor difference within each stratum.
- How strongly listeners follow their partner's decision, knob contrasts at second hand, and an adjusted logistic model.
- `evidence_passed` is the runner's keyword rule over the catch-up transcript, not a semantic judgment.

Tables: `m8_funnel`, `m8_go_by_partner_state_<model>`, `m8_truth_minus_rumor`, `m8_partner_following`, `m8_knob_contrasts`, `m8_logit`.

### Metric 9: who checks

*Do character traits beat the knobs?*

- Check rate by listener persona, seat and source persona, with joint Wald tests (knobs adjusted, cluster-robust by pair).
- Variance shares: McFadden pseudo-R-squared for the knobs alone and what persona, seat and source persona each add on top.
- Budget note: every listener starts with the same $40 and the check costs a flat $5, so budget cannot predict the decision.

Tables: `m9_personas`, `m9_persona_rates`, `m9_seat_rates`, `m9_source_persona_rates`, `m9_heterogeneity_tests`, `m9_variance_share`.

## Tier 3 metrics (truth discount)

These need belief labels. Unless stated, they use first-hand listeners, the primary score and pair-level bootstrap CIs over twin pairs.

### Metric 10: primary truth discount (`m10_primary_td`)

Pair-level TD per model and pooled, under the primary score and both omission bounds, so the report can say whether the sign and the exclusion of zero survive any treatment of silence. A denominator table shows listeners, labeled count, omission rate, GO rate and label counts per twin.

Tables: `m10_primary_td`, `m10_denominators`.

### Metric 11: checkers vs non-checkers (`m11_checkers`)

TD among listeners who checked (GO) and those who did not (SKIP). First-hand non-checkers saw no poster, so their TD is the **noise floor** (expected near 0); checkers' TD is what the poster adds. A second table checks the labels against the GO/SKIP log: GO listeners should be labeled `CHECKED_TRUE` in the truth twin and `CHECKED_FALSE` in the rumor twin, SKIP listeners should carry no CHECKED label. Strata are post-treatment choices, so use them descriptively.

Tables: `m11_strata_td`, `m11_label_vs_go_log`.

### Metric 12: ten planned contrasts (`m12_contrasts`)

The ten contrasts of `docs/01_experimental_spec.md` section 9: closeness, authority, wealth, reliability, closeness x reliability, authority x reliability, wealth x reliability, closeness x authority, gender and age, each on TD.

- Pair-level TD regressed on six effect-coded knobs (+0.5 / -0.5) and the four planned interactions, with HC1-robust SEs. A main-effect coefficient equals the difference between knob levels (averaged over the others); an interaction coefficient equals a difference-in-differences.
- **Holm-Bonferroni** adjusted p-values across the ten contrasts; `significant_holm_05` flags those that survive at 0.05.
- Sensitivity columns for the NOT_MENTIONED = 0 and 0.5 scores, and an estimate adjusted for layout and repetition (and model when pooled).
- Per model and pooled. This is an exploratory fit, not the confirmatory test; see [limitations](#limitations-and-interpretation).

Table: `m12_planned_contrasts`.

### Metric 13: asymmetry (`m13_asymmetry`)

*Do listeners err toward credulity or toward skepticism?* Perfect listeners believe the truth (1) and reject the rumor (0), so:

- over-belief in rumors = mean rumor-twin belief,
- under-belief in truths = 1 - mean truth-twin belief,
- net credulity = their difference; positive means more belief than the truth warrants.

Reported per layer and model, and as knob-level differences in over- and under-belief separately, to show which cues are pure credulity cues.

Tables: `m13_asymmetry`, `m13_asymmetry_by_knob`.

### Metric 14: override and cell map (`m14_cell_map`)

Exploratory. TD and rumor-belief for each of the 64 cells per model (heatmaps and a table), flags `comfort_wins` (TD <= 0) and `rumor_believed` (mean rumor-twin belief >= 0.5), and the friendship and authority override questions restricted to poor-record and good-record sources. Cells hold few twin pairs, so use the maps for pattern-spotting, not for testing individual cells. The formal override tests are contrasts 5 and 6 in metric 12.

Tables: `m14_cell_td`, `m14_override`.

### Metric 15: second-hand truth discount (`m15_second_hand_td`)

Second-hand TD under all three scores, **decay** (first-hand TD minus second-hand TD on pairs where both exist, paired), TD by partner state, evidence passed and the listener's own decision, and **certainty decay**: certainty is 1 when the listener commits to a belief and 0 when `UNCERTAIN`, compared across layers. Strata partly depend on the twin, so they are descriptive.

Tables: `m15_second_hand_td`, `m15_second_hand_strata`, `m15_certainty`.

## Tier 4 metrics (robustness and mechanism)

### Metric 16: model comparison (`m16_model_comparison`)

Belief side of the comparison between the two models: TD by model and layer and its difference (independent bootstraps), label mix by model, layer and twin, and whether the ten planned contrasts replicate across models (difference test between the two models' estimates). A behavioral recap and a design-balance table (pairs per model and repetition, layouts covered) show whether model and source persona are confounded by layout. Full behavioral comparison is metrics 7-9. Needs both models in the data.

Tables: `m16_td_by_model`, `m16_label_mix`, `m16_contrast_replication`, `m16_check_rate_recap`, `m16_design_balance`.

### Metric 17: variance decomposition and seed planning (`m17_variance`)

1. **ICC** (one-way ANOVA estimator for unbalanced groups, cluster-bootstrap CI) of listener-level belief within towns, twin pairs, cells, layouts, listener personas, seats and source personas. The town ICC is the non-independence that justifies using the pair as the unit; the design effect is how much it would inflate variances if listeners were treated as independent.
2. **Variance in pair-level TD** explained by the knobs (six main effects and four interactions), layout, repetition and source persona, as R-squared alone and added last. Layout and source persona are partly collinear (the layout fixes the source persona).
3. **Seed planning** from the planned contrasts: minimum detectable effect at 80% power (alpha 0.05 raw and a conservative Holm stand-in of 0.05/10), projected to the planned 39 pairs per cell, and pairs per cell needed to detect 0.05 and 0.10 belief points. It assumes the observed pair-level variance, which includes any judge noise.

Tables: `m17_icc`, `m17_td_variance_explained`, `m17_power_planning`.

### Metric 18: keyword transcript pass (`m18_keywords`)

A **keyword-only, no-LLM** pass. The saved runs hold no hidden reasoning, only what agents said, so this scans each listener's own spoken lines (catch-up and phone call) with regular expressions for eight families: checking and noticeboard, cost of checking, hedging and rumor, trust in the source, distrust of the source, authority cue, closeness cue and confirmation (the patterns are in `FAMILIES` in `m18_keywords.py`). Views:

- how common each family is by model and layer,
- family hit-rate difference between listeners who checked and did not (cluster bootstrap),
- whether cue language moves with the manipulated knob it names (for example "mayor" language when the source is the mayor),
- hedging, checking, confirmation and distrust hit rates by belief label, a rough validity check on the labels.

A keyword hit is a lexical proxy, not a motive. Keyword flags are cached as `text_flags_<hash>.csv`.

Tables: `m18_family_rates`, `m18_language_by_decision`, `m18_language_by_knob`, `m18_language_by_label`.

### Metric 20: top-10 DNA rule (`m20_dna_ranking`)

Ranks the 64 source profiles per model by mean rumor-twin belief (the most persuasive liars). A split-sample test ranks on a random half of each cell's pairs and again on the other half (500 splits) and reports top-10 overlap against chance, the rank correlation between halves, and the selection regret; a bootstrap gives each cell's probability of being in the top 10. A cross-model overlap is also reported. High overlap and rank correlation mean the selection is stable at the current sample size.

Tables: `m20_ranking_<model>`, `m20_split_sample`.

## Statistical methods

| Method | Used for |
|---|---|
| Percentile bootstrap over twin pairs (default 2000 resamples) | TD, belief means and their differences |
| Cluster bootstrap by pair over listeners | check-rate and hit-rate differences (listener-level outcomes) |
| Independent-group bootstrap | differences between models or knob levels (disjoint pairs) |
| Logistic regression (IRLS) with cluster-robust sandwich SEs, odds ratios | check decisions (metrics 7, 8) |
| Joint Wald tests with a hand-written chi-square survival function | persona, seat and source-persona effects (metric 9) |
| McFadden pseudo-R-squared | variance shares of check decisions (metric 9) |
| OLS with HC1-robust SEs, effect coding | planned contrasts (metrics 12, 16, 17) |
| Holm-Bonferroni step-down | the ten planned contrasts |
| ANOVA-estimator ICC with group bootstrap | clustering of belief (metric 17) |

## Outputs

Each run writes to `--out`:

- `result_analysis_report.html` (from `run_all.py`), `tier2_report.html` or `tier34_report.html`: charts, tables, a "Key takeaways" box per metric and a "Read this first" box of caveats.
- `tables/*.csv`: one file per table, named as listed under each metric. Tier 3/4 also writes `label_coverage.csv`.
- Cached inputs: `listeners_<hash>.csv` and, for metric 18, `text_flags_<hash>.csv`.

Generated folders (`output/`) are git-ignored.

## Limitations and interpretation

- **Exploratory.** The report is descriptive; a dated analysis specification is still needed before treating the ten contrasts as confirmatory. Development-pilot data (`evidence_kind = development_pilot`) is not study-eligible.
- **Partial design.** Runs may cover only part of the planned design (a handful of twin pairs per cell versus 39 planned). Single cells are noisy; shards pooled with `--data` increase pairs per cell.
- **Confounding.** If a model ran only some layouts, model and source persona are partly confounded; metric 16 prints the design balance.
- **Judge error.** Belief labels come from a single LLM judge, and judge error is not propagated into the confidence intervals. Intervals reflect sampling variation over twin pairs only. Use metric 11's label-vs-GO check and metric 18's label-language check as validity probes.
- **No probabilities.** The metrics use only the label, so any judge works. Analyses that need label probabilities or margins are not included.
- **Keyword rules.** `evidence_passed` (runner) and metric 18 are keyword proxies, not semantic coding.
- **Post-treatment strata.** GO/SKIP strata (metrics 11, 15) and partner-state strata are consequences of the experiment, not randomized, so they are descriptive.

## Testing

```bash
python3 result_analysis/tier3_4/test_t3lib.py
```

Checks Holm correction, the normal quantile, pair construction, recovery of planted contrast effects, ICC recovery, bootstrap coverage and the label reader, all on simulated data with known answers (under a few seconds).

To exercise the whole Tier 3/4 pipeline before real labels exist, generate random placeholder labels and run into a scratch folder:

```bash
python3 result_analysis/tier3_4/make_fixture.py --data /path/to/outputs/main-owner-0 --out /tmp/labels_SYNTHETIC.csv
python3 result_analysis/tier3_4/run_tier34.py --data /path/to/outputs/main-owner-0 --labels /tmp/labels_SYNTHETIC.csv --out /tmp/t34_test --boot 200
```

The placeholder labels are random (apart from a crude GO to CHECKED link), and the report prints a banner when the label file name contains `SYNTHETIC`. Never use them for results.

## Layout and extending

```
result_analysis/
  README.md
  requirements.txt
  run_all.py              all tiers, one combined report
  common/                 shared by both tiers
    t2lib.py              run loading, bootstrap, logistic regression, Wald tests
    charts.py             dependency-free inline-SVG charts
    styles.py             report CSS
  tier2/
    m7_check_rates.py  m8_second_hand.py  m9_who_checks.py
    build_report.py  run_tier2.py
  tier3_4/
    t3lib.py              labels, scores, pair table, OLS, Holm, ICC
    m10_primary_td.py ... m20_dna_ranking.py   one module per metric
    build_report34.py  run_tier34.py  make_fixture.py  test_t3lib.py
```

A metric module exposes `run(...)` returning `dict(id, title, summary, blocks, tables)`: `summary` is a list of takeaway sentences, `blocks` is a list of `("h3" | "h4" | "p" | "svg" | "table" | "grid", ...)` items rendered in order, and `tables` maps a CSV name to a DataFrame. Register a new module in `run_metrics` of the matching runner (`tier2/run_tier2.py` or `tier3_4/run_tier34.py`); `run_all.py` picks it up automatically. Reading-guide caveats live in `caveats()` of `tier2/build_report.py` and `tier3_4/build_report34.py`.
