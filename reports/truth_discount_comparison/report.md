# Report 3: Truth Discount & Comparisons (Truth Twin − Rumor Twin)

**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Towns:** 9,984 (4,992 Rumor + 4,992 Truth) | **Twin Pairs:** 4,992 | **Clustering:** Twin Pair (`pair_id`)

### Methodological Policy (Dynamic Denominators — Never Hardcoded)
- **Core Estimand:** $\text{Truth Discount} = \text{Belief}_{\text{Truth Twin}} - \text{Belief}_{\text{Rumor Twin}}$ (`Matched-Pair Mean ± 1.96·SE`), alongside $\Delta\text{GO}$, $\Delta\text{Omission}$, and categorical label shifts.
- **Invalid Exclusion:** Individual `judgment_status = invalid` rows stay `NaN` (never zero-imputed, and without discarding valid listeners in the same town).
- **Dynamic Denominators:** `R/T Ment. N` = non-NaN mentioning listeners used for Rumor/Truth conditional `Belief`; `Belief Pairs` = complete twin pairs having valid mentioning listeners in both twins; `GO Pairs` = complete twin pairs with verification decisions.
- **Symmetry / Truth Discount Model:** Pooled `outcome ~ truth * (6 main knobs + 4 interactions) + C(real_artist)` OLS / LPM with Twin-Pair-Clustered SEs (`groups=pair_id`), two-sided Wald z-tests, and Holm adjustment across all 10 planned contrasts. `Belief` also reports the spec's REML LMM (`1 | run_id`).

---

## 1. Overall Truth vs. Rumor & Matched Truth Discount Summary

*Estimator: Matched-Pair Mean (`Truth − Rumor`), Normal 95% CI (`Mean ± 1.96·SE`); `GO %` over Expected N, `NM %` over Valid N.*

### Table 1A: Per Model × Layer

| Model | Layer | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Sil=0.0 TD | Sil=0.5 TD | GO Pairs | Rumor GO % | Truth GO % | Δ GO | Rumor NM % | Truth NM % | Δ NM |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | First-Hand (Seats 1-6) | 14,836 / 14,922 | 2,496 | 0.091 | 0.573 | **0.482** [0.469, 0.495] | 0.482 | 0.479 | 2,496 | 48.3% | 48.5% | +0.2 pp | 0.6% | 0.0% | -0.6 pp |
| DeepSeek-V4-Flash | Second-Hand (Seats 7-12) | 13,620 / 14,828 | 2,496 | 0.023 | 0.789 | **0.765** [0.757, 0.773] | 0.767 | 0.724 | 2,496 | 62.0% | 67.9% | +5.8 pp | 8.7% | 0.1% | -8.7 pp |
| DeepSeek-V4-Flash | Overall (All 12 Listeners) | 28,456 / 29,750 | 2,496 | 0.059 | 0.680 | **0.621** [0.611, 0.631] | 0.624 | 0.601 | 2,496 | 55.2% | 58.2% | +3.0 pp | 4.7% | 0.0% | -4.6 pp |
| Qwen3.8-Flash | First-Hand (Seats 1-6) | 14,894 / 14,946 | 2,496 | 0.005 | 0.893 | **0.887** [0.881, 0.894] | 0.886 | 0.884 | 2,496 | 92.8% | 92.7% | -0.1 pp | 0.5% | 0.1% | -0.4 pp |
| Qwen3.8-Flash | Second-Hand (Seats 7-12) | 14,101 / 14,849 | 2,496 | 0.036 | 0.797 | **0.761** [0.755, 0.768] | 0.757 | 0.734 | 2,496 | 28.6% | 23.9% | -4.7 pp | 5.4% | 0.8% | -4.6 pp |
| Qwen3.8-Flash | Overall (All 12 Listeners) | 28,995 / 29,795 | 2,496 | 0.020 | 0.845 | **0.825** [0.819, 0.830] | 0.822 | 0.809 | 2,496 | 60.7% | 58.3% | -2.4 pp | 2.9% | 0.4% | -2.5 pp |

### Table 1B: Entire Experiment Average (Both Models Combined)

| Scope | Layer | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Sil=0.0 TD | Sil=0.5 TD | GO Pairs | Rumor GO % | Truth GO % | Δ GO | Rumor NM % | Truth NM % | Δ NM |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Both Models Combined | First-Hand (Seats 1-6) | 29,730 / 29,868 | 4,992 | 0.048 | 0.733 | **0.684** [0.675, 0.694] | 0.684 | 0.682 | 4,992 | 70.5% | 70.6% | +0.1 pp | 0.6% | 0.1% | -0.5 pp |
| Both Models Combined | Second-Hand (Seats 7-12) | 27,721 / 29,677 | 4,992 | 0.030 | 0.793 | **0.763** [0.758, 0.768] | 0.762 | 0.729 | 4,992 | 45.3% | 45.9% | +0.6 pp | 7.0% | 0.4% | -6.6 pp |
| Both Models Combined | Overall (All 12 Listeners) | 57,451 / 59,545 | 4,992 | 0.039 | 0.763 | **0.723** [0.717, 0.729] | 0.723 | 0.705 | 4,992 | 57.9% | 58.2% | +0.3 pp | 3.8% | 0.2% | -3.5 pp |

---

## 2. Model Comparison (`DeepSeek-V4-Flash − Qwen3.8-Flash`)

*Estimator: Pooled `outcome ~ truth * is_deepseek` OLS / LPM with Pair-Clustered SEs (`groups = model__pair_id`) & two-sided Wald z-test.*

| POV | Outcome | Non-NaN N (R / T) | Pairs | DeepSeek Rumor | Qwen Rumor | Δ Rumor (p) | DeepSeek Truth | Qwen Truth | Δ Truth (p) | DeepSeek TD | Qwen TD | Δ TD (DS − Qwen) | 95% CI | p (clustered) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| source | Belief Score | 57,451 / 59,545 | 4,992 | 0.059 | 0.020 | +0.039 (<0.0001) | 0.680 | 0.845 | -0.165 (<0.0001) | 0.621 | 0.825 | **-0.203***** | [-0.214, -0.192] | <0.0001 |
| source | GO Rate (%) | 59,904 / 59,904 | 4,992 | 55.2% | 60.7% | -5.5 pp (<0.0001) | 58.2% | 58.3% | -0.1 pp (0.7919) | 3.0% | -2.4% | **+5.4 pp***** | [+4.6, +6.2 pp] | <0.0001 |
| source | NOT_MENTIONED (%) | 59,715 / 59,691 | 4,992 | 4.7% | 2.9% | +1.7 pp (<0.0001) | 0.0% | 0.4% | -0.4 pp (<0.0001) | -4.6% | -2.5% | **-2.1 pp***** | [-2.5, -1.8 pp] | <0.0001 |
| source | FACT (%) | 59,715 / 59,691 | 4,992 | 0.3% | 0.5% | -0.2 pp (<0.0001) | 4.9% | 7.5% | -2.6 pp (<0.0001) | 4.7% | 7.1% | **-2.4 pp***** | [-2.8, -2.0 pp] | <0.0001 |
| source | UNCERTAIN (%) | 59,715 / 59,691 | 4,992 | 9.9% | 2.8% | +7.1 pp (<0.0001) | 11.6% | 7.8% | +3.8 pp (<0.0001) | 1.7% | 5.0% | **-3.3 pp***** | [-3.9, -2.8 pp] | <0.0001 |
| source | SKEPTICAL (%) | 59,715 / 59,691 | 4,992 | 28.9% | 13.8% | +15.1 pp (<0.0001) | 25.9% | 11.1% | +14.8 pp (<0.0001) | -3.0% | -2.7% | **-0.3 pp** | [-1.1, +0.5 pp] | 0.4499 |
| first_hand | Belief Score | 29,730 / 29,868 | 4,992 | 0.091 | 0.005 | +0.086 (<0.0001) | 0.573 | 0.893 | -0.320 (<0.0001) | 0.481 | 0.887 | **-0.406***** | [-0.420, -0.391] | <0.0001 |
| first_hand | GO Rate (%) | 29,952 / 29,952 | 4,992 | 48.3% | 92.8% | -44.5 pp (<0.0001) | 48.5% | 92.7% | -44.3 pp (<0.0001) | 0.2% | -0.1% | **+0.3 pp** | [-0.6, +1.1 pp] | 0.5638 |
| first_hand | NOT_MENTIONED (%) | 29,898 / 29,893 | 4,992 | 0.6% | 0.5% | +0.1 pp (0.0871) | 0.0% | 0.1% | -0.1 pp (0.0027) | -0.6% | -0.4% | **-0.2 pp**** | [-0.4, -0.1 pp] | 0.0077 |
| first_hand | FACT (%) | 29,898 / 29,893 | 4,992 | 0.3% | 0.0% | +0.3 pp (<0.0001) | 2.0% | 4.0% | -2.0 pp (<0.0001) | 1.7% | 4.0% | **-2.3 pp***** | [-2.7, -1.9 pp] | <0.0001 |
| first_hand | UNCERTAIN (%) | 29,898 / 29,893 | 4,992 | 16.0% | 0.9% | +15.1 pp (<0.0001) | 16.3% | 3.6% | +12.7 pp (<0.0001) | 0.3% | 2.7% | **-2.4 pp***** | [-3.2, -1.6 pp] | <0.0001 |
| first_hand | SKEPTICAL (%) | 29,898 / 29,893 | 4,992 | 35.4% | 8.5% | +26.8 pp (<0.0001) | 34.3% | 8.7% | +25.6 pp (<0.0001) | -1.1% | 0.1% | **-1.2 pp*** | [-2.1, -0.2 pp] | 0.0138 |
| second_hand | Belief Score | 27,721 / 29,677 | 4,992 | 0.023 | 0.036 | -0.012 (<0.0001) | 0.789 | 0.797 | -0.009 (0.1074) | 0.765 | 0.761 | **+0.004** | [-0.007, +0.014] | 0.4889 |
| second_hand | GO Rate (%) | 29,952 / 29,952 | 4,992 | 62.0% | 28.6% | +33.5 pp (<0.0001) | 67.9% | 23.9% | +44.0 pp (<0.0001) | 5.8% | -4.7% | **+10.5 pp***** | [+9.1, +12.0 pp] | <0.0001 |
| second_hand | NOT_MENTIONED (%) | 29,817 / 29,798 | 4,992 | 8.7% | 5.4% | +3.3 pp (<0.0001) | 0.1% | 0.8% | -0.7 pp (<0.0001) | -8.6% | -4.6% | **-4.0 pp***** | [-4.7, -3.4 pp] | <0.0001 |
| second_hand | FACT (%) | 29,817 / 29,798 | 4,992 | 0.2% | 0.9% | -0.7 pp (<0.0001) | 7.9% | 11.0% | -3.2 pp (<0.0001) | 7.7% | 10.1% | **-2.5 pp***** | [-3.2, -1.8 pp] | <0.0001 |
| second_hand | UNCERTAIN (%) | 29,817 / 29,798 | 4,992 | 3.8% | 4.7% | -0.9 pp (0.0001) | 6.9% | 12.1% | -5.2 pp (<0.0001) | 3.1% | 7.3% | **-4.3 pp***** | [-5.1, -3.5 pp] | <0.0001 |
| second_hand | SKEPTICAL (%) | 29,817 / 29,798 | 4,992 | 22.5% | 19.1% | +3.4 pp (<0.0001) | 17.5% | 13.6% | +3.9 pp (<0.0001) | -5.0% | -5.5% | **+0.6 pp** | [-0.6, +1.7 pp] | 0.3476 |

---

## 3. Paired Symmetry & Truth Discount Tests (10 Planned Contrasts)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=58,206, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) | LMM TD Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.0014 (0.4893) | +0.0901 (<0.0001) | **+0.0887***** | [+0.0792, +0.0983] | <0.0001 | <0.0001 | +0.0887 (p=<0.0001) |
| main | authority (`mayor - citizen`) | +0.0114 (<0.0001) | +0.0101 (0.0197) | **-0.0013** | [-0.0109, +0.0083] | 0.7905 | 1.0000 | -0.0013 (p=0.7878) |
| main | reliability (`good_record - poor_record`) | +0.0347 (<0.0001) | +0.4431 (<0.0001) | **+0.4084***** | [+0.3989, +0.4180] | <0.0001 | <0.0001 | +0.4085 (p=<0.0001) |
| main | wealth (`rich - poor`) | -0.0045 (0.0232) | +0.0367 (<0.0001) | **+0.0412***** | [+0.0316, +0.0508] | <0.0001 | <0.0001 | +0.0412 (p=<0.0001) |
| main | gender (`woman - man`) | +0.0021 (0.2885) | +0.0031 (0.4756) | **+0.0010** | [-0.0085, +0.0106] | 0.8352 | 1.0000 | +0.0010 (p=0.8340) |
| main | age (`old - young`) | -0.0028 (0.1589) | -0.0206 (<0.0001) | **-0.0179***** | [-0.0274, -0.0083] | 0.0002 | 0.0010 | -0.0179 (p=0.0002) |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.0230 (<0.0001) | -0.1716 (<0.0001) | **-0.1485***** | [-0.1677, -0.1294] | <0.0001 | <0.0001 | -0.1485 (p=<0.0001) |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.0083 (0.0351) | -0.0541 (<0.0001) | **-0.0624***** | [-0.0816, -0.0432] | <0.0001 | <0.0001 | -0.0624 (p=<0.0001) |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.0024 (0.5365) | -0.0459 (<0.0001) | **-0.0435***** | [-0.0627, -0.0243] | <0.0001 | <0.0001 | -0.0435 (p=<0.0001) |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.0049 (0.2090) | -0.0135 (0.1186) | **-0.0184** | [-0.0376, +0.0007] | 0.0586 | 0.1759 | -0.0185 (p=0.0562) |

**Outcome: GO Rate (Verification %)** (n=59,904, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +7.69 pp (<0.0001) | +8.70 pp (<0.0001) | **+1.01 pp** | [-0.15, +2.18 pp] | 0.0865 | 0.8646 |
| main | authority (`mayor - citizen`) | +1.10 pp (0.0095) | +0.81 pp (0.0773) | **-0.29 pp** | [-1.45, +0.87 pp] | 0.6197 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +37.16 pp (<0.0001) | +37.00 pp (<0.0001) | **-0.16 pp** | [-1.32, +1.00 pp] | 0.7866 | 1.0000 |
| main | wealth (`rich - poor`) | +2.62 pp (<0.0001) | +2.46 pp (<0.0001) | **-0.16 pp** | [-1.32, +1.00 pp] | 0.7866 | 1.0000 |
| main | gender (`woman - man`) | +1.28 pp (0.0025) | +0.93 pp (0.0412) | **-0.35 pp** | [-1.51, +0.81 pp] | 0.5575 | 1.0000 |
| main | age (`old - young`) | -1.49 pp (0.0005) | -2.01 pp (<0.0001) | **-0.52 pp** | [-1.68, +0.64 pp] | 0.3790 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -10.46 pp (<0.0001) | -11.34 pp (<0.0001) | **-0.88 pp** | [-3.20, +1.44 pp] | 0.4566 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -5.19 pp (<0.0001) | -4.10 pp (<0.0001) | **+1.10 pp** | [-1.23, +3.42 pp] | 0.3550 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -3.97 pp (<0.0001) | -4.74 pp (<0.0001) | **-0.77 pp** | [-3.10, +1.55 pp] | 0.5130 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -3.14 pp (0.0002) | -1.94 pp (0.0342) | **+1.20 pp** | [-1.12, +3.52 pp] | 0.3101 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=59,611, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.42 pp (0.0735) | -0.02 pp (0.4346) | **-0.44 pp** | [-0.90, +0.02 pp] | 0.0625 | 0.5629 |
| main | authority (`mayor - citizen`) | +0.18 pp (0.4438) | -0.01 pp (0.7965) | **-0.19 pp** | [-0.65, +0.28 pp] | 0.4303 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +5.87 pp (<0.0001) | -0.03 pp (0.1854) | **-5.90 pp***** | [-6.36, -5.44 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.22 pp (0.3364) | +0.06 pp (0.0177) | **+0.29 pp** | [-0.18, +0.75 pp] | 0.2255 | 1.0000 |
| main | gender (`woman - man`) | -0.16 pp (0.4856) | -0.00 pp (0.8918) | **+0.16 pp** | [-0.30, +0.62 pp] | 0.4979 | 1.0000 |
| main | age (`old - young`) | -0.45 pp (0.0567) | -0.03 pp (0.1914) | **+0.41 pp** | [-0.05, +0.87 pp] | 0.0799 | 0.6393 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.58 pp (0.2176) | +0.04 pp (0.4344) | **+0.62 pp** | [-0.31, +1.54 pp] | 0.1903 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.17 pp (0.7197) | +0.07 pp (0.1927) | **-0.10 pp** | [-1.02, +0.82 pp] | 0.8294 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.69 pp (0.1384) | -0.12 pp (0.0174) | **+0.57 pp** | [-0.35, +1.50 pp] | 0.2246 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.04 pp (0.9328) | +0.04 pp (0.4331) | **+0.08 pp** | [-0.84, +1.00 pp] | 0.8660 | 1.0000 |

**Outcome: FACT (%)** (n=59,611, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.11 pp (0.0496) | +1.95 pp (<0.0001) | **+1.83 pp***** | [+1.32, +2.34 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.10 pp (0.0839) | +0.81 pp (0.0015) | **+0.71 pp*** | [+0.20, +1.22 pp] | 0.0059 | 0.0475 |
| main | reliability (`good_record - poor_record`) | +0.46 pp (<0.0001) | +4.88 pp (<0.0001) | **+4.42 pp***** | [+3.91, +4.92 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.07 pp (0.2011) | +0.17 pp (0.5034) | **+0.10 pp** | [-0.41, +0.60 pp] | 0.7086 | 1.0000 |
| main | gender (`woman - man`) | +0.12 pp (0.0434) | +0.13 pp (0.5970) | **+0.02 pp** | [-0.49, +0.53 pp] | 0.9443 | 1.0000 |
| main | age (`old - young`) | +0.06 pp (0.2972) | +0.03 pp (0.9009) | **-0.03 pp** | [-0.54, +0.48 pp] | 0.9126 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.12 pp (0.3004) | +0.94 pp (0.0659) | **+0.82 pp** | [-0.20, +1.83 pp] | 0.1139 | 0.7975 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.15 pp (0.2053) | +0.24 pp (0.6399) | **+0.09 pp** | [-0.92, +1.11 pp] | 0.8586 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +0.04 pp (0.7270) | -0.71 pp (0.1669) | **-0.75 pp** | [-1.76, +0.27 pp] | 0.1499 | 0.8992 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.26 pp (0.0270) | +0.51 pp (0.3195) | **+0.25 pp** | [-0.76, +1.27 pp] | 0.6256 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=59,611, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.09 pp (0.7805) | +0.78 pp (0.0274) | **+0.88 pp** | [+0.00, +1.75 pp] | 0.0489 | 0.3913 |
| main | authority (`mayor - citizen`) | +1.66 pp (<0.0001) | +2.10 pp (<0.0001) | **+0.44 pp** | [-0.43, +1.32 pp] | 0.3184 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +3.49 pp (<0.0001) | +5.31 pp (<0.0001) | **+1.82 pp***** | [+0.95, +2.69 pp] | <0.0001 | 0.0004 |
| main | wealth (`rich - poor`) | -0.92 pp (0.0062) | -1.24 pp (0.0005) | **-0.32 pp** | [-1.19, +0.55 pp] | 0.4727 | 1.0000 |
| main | gender (`woman - man`) | +0.15 pp (0.6520) | +0.03 pp (0.9242) | **-0.12 pp** | [-0.99, +0.75 pp] | 0.7903 | 1.0000 |
| main | age (`old - young`) | -0.09 pp (0.7832) | +0.24 pp (0.5048) | **+0.33 pp** | [-0.54, +1.20 pp] | 0.4592 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -4.91 pp (<0.0001) | -3.94 pp (<0.0001) | **+0.97 pp** | [-0.78, +2.71 pp] | 0.2767 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.49 pp (0.4686) | +0.76 pp (0.2837) | **+0.27 pp** | [-1.47, +2.02 pp] | 0.7606 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.34 pp (0.6162) | -2.37 pp (0.0008) | **-2.04 pp** | [-3.78, -0.29 pp] | 0.0222 | 0.1998 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.55 pp (0.4173) | -0.21 pp (0.7671) | **-0.76 pp** | [-2.50, +0.99 pp] | 0.3948 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=59,611, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -8.70 pp (<0.0001) | -9.32 pp (<0.0001) | **-0.62 pp** | [-1.79, +0.54 pp] | 0.2962 | 1.0000 |
| main | authority (`mayor - citizen`) | -2.31 pp (<0.0001) | -1.96 pp (<0.0001) | **+0.35 pp** | [-0.81, +1.52 pp] | 0.5545 | 1.0000 |
| main | reliability (`good_record - poor_record`) | -45.65 pp (<0.0001) | -46.62 pp (<0.0001) | **-0.97 pp** | [-2.14, +0.19 pp] | 0.1013 | 0.9196 |
| main | wealth (`rich - poor`) | -2.60 pp (<0.0001) | -3.14 pp (<0.0001) | **-0.54 pp** | [-1.70, +0.63 pp] | 0.3668 | 1.0000 |
| main | gender (`woman - man`) | -0.79 pp (0.0714) | -0.28 pp (0.5143) | **+0.51 pp** | [-0.66, +1.67 pp] | 0.3938 | 1.0000 |
| main | age (`old - young`) | +1.80 pp (<0.0001) | +1.98 pp (<0.0001) | **+0.18 pp** | [-0.99, +1.34 pp] | 0.7678 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +19.11 pp (<0.0001) | +18.99 pp (<0.0001) | **-0.12 pp** | [-2.46, +2.21 pp] | 0.9168 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +4.88 pp (<0.0001) | +4.90 pp (<0.0001) | **+0.02 pp** | [-2.31, +2.35 pp] | 0.9878 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +4.86 pp (<0.0001) | +5.98 pp (<0.0001) | **+1.12 pp** | [-1.21, +3.45 pp] | 0.3461 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +3.39 pp (0.0001) | +1.39 pp (0.1116) | **-2.00 pp** | [-4.34, +0.33 pp] | 0.0920 | 0.9196 |

**Outcome: CHECKED_TRUE (%)** (n=59,611, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.08 pp (0.2847) | +6.68 pp (<0.0001) | **+6.60 pp***** | [+5.58, +7.62 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.13 pp (0.0752) | -0.85 pp (0.0955) | **-0.99 pp** | [-2.01, +0.03 pp] | 0.0573 | 0.1718 |
| main | reliability (`good_record - poor_record`) | +0.75 pp (<0.0001) | +36.78 pp (<0.0001) | **+36.03 pp***** | [+35.01, +37.05 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.01 pp (0.8570) | +4.09 pp (<0.0001) | **+4.11 pp***** | [+3.09, +5.12 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | +0.02 pp (0.7956) | +0.15 pp (0.7657) | **+0.13 pp** | [-0.88, +1.15 pp] | 0.7975 | 0.7975 |
| main | age (`old - young`) | -0.24 pp (0.0012) | -2.19 pp (<0.0001) | **-1.95 pp***** | [-2.96, -0.93 pp] | 0.0002 | 0.0009 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.16 pp (0.2867) | -16.13 pp (<0.0001) | **-16.29 pp***** | [-18.33, -14.26 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.32 pp (0.0323) | -6.07 pp (<0.0001) | **-6.39 pp***** | [-8.42, -4.35 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.03 pp (0.8562) | -2.65 pp (0.0098) | **-2.62 pp*** | [-4.66, -0.58 pp] | 0.0116 | 0.0465 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.05 pp (0.7271) | -1.78 pp (0.0822) | **-1.73 pp** | [-3.76, +0.31 pp] | 0.0959 | 0.1918 |

**Outcome: CHECKED_FALSE (%)** (n=59,611, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +8.18 pp (<0.0001) | -0.07 pp (0.2859) | **-8.25 pp***** | [-9.21, -7.28 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.24 pp (0.6212) | -0.09 pp (0.1327) | **-0.33 pp** | [-1.30, +0.63 pp] | 0.4962 | 0.4962 |
| main | reliability (`good_record - poor_record`) | +35.08 pp (<0.0001) | -0.31 pp (<0.0001) | **-35.39 pp***** | [-36.35, -34.43 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +3.69 pp (<0.0001) | +0.05 pp (0.3869) | **-3.63 pp***** | [-4.60, -2.67 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | +0.67 pp (0.1716) | -0.03 pp (0.5961) | **-0.70 pp** | [-1.66, +0.26 pp] | 0.1548 | 0.3096 |
| main | age (`old - young`) | -1.08 pp (0.0262) | -0.03 pp (0.6685) | **+1.06 pp** | [+0.09, +2.02 pp] | 0.0315 | 0.0945 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -13.91 pp (<0.0001) | +0.11 pp (0.3949) | **+14.01 pp***** | [+12.09, +15.94 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -6.00 pp (<0.0001) | +0.11 pp (0.3934) | **+6.11 pp***** | [+4.18, +8.03 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -3.84 pp (<0.0001) | -0.13 pp (0.2798) | **+3.71 pp***** | [+1.78, +5.64 pp] | 0.0002 | 0.0007 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -4.11 pp (<0.0001) | +0.05 pp (0.6661) | **+4.16 pp***** | [+2.23, +6.09 pp] | <0.0001 | 0.0001 |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=29,758, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) | LMM TD Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.0004 (0.8984) | +0.1144 (<0.0001) | **+0.1140***** | [+0.1004, +0.1277] | <0.0001 | <0.0001 | +0.1140 (p=<0.0001) |
| main | authority (`mayor - citizen`) | +0.0193 (<0.0001) | -0.0049 (0.3713) | **-0.0242**** | [-0.0379, -0.0106] | 0.0005 | 0.0025 | -0.0243 (p=0.0002) |
| main | reliability (`good_record - poor_record`) | +0.0461 (<0.0001) | +0.6002 (<0.0001) | **+0.5541***** | [+0.5405, +0.5678] | <0.0001 | <0.0001 | +0.5541 (p=<0.0001) |
| main | wealth (`rich - poor`) | -0.0111 (0.0011) | +0.0406 (<0.0001) | **+0.0516***** | [+0.0380, +0.0653] | <0.0001 | <0.0001 | +0.0516 (p=<0.0001) |
| main | gender (`woman - man`) | +0.0026 (0.4512) | +0.0041 (0.4594) | **+0.0015** | [-0.0121, +0.0152] | 0.8279 | 0.8279 | +0.0015 (p=0.8168) |
| main | age (`old - young`) | -0.0031 (0.3561) | -0.0206 (0.0002) | **-0.0174*** | [-0.0311, -0.0038] | 0.0123 | 0.0493 | -0.0174 (p=0.0072) |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.0377 (<0.0001) | -0.1799 (<0.0001) | **-0.1422***** | [-0.1695, -0.1149] | <0.0001 | <0.0001 | -0.1422 (p=<0.0001) |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.0145 (0.0327) | -0.0364 (0.0009) | **-0.0509**** | [-0.0782, -0.0236] | 0.0003 | 0.0016 | -0.0509 (p=<0.0001) |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.0152 (0.0253) | -0.0435 (<0.0001) | **-0.0284** | [-0.0557, -0.0010] | 0.0418 | 0.1255 | -0.0283 (p=0.0288) |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.0035 (0.6019) | -0.0199 (0.0705) | **-0.0234** | [-0.0507, +0.0039] | 0.0923 | 0.1847 | -0.0235 (p=0.0704) |

**Outcome: GO Rate (Verification %)** (n=29,952, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +11.42 pp (<0.0001) | +11.42 pp (<0.0001) | **+0.00 pp** | [-1.44, +1.44 pp] | 1.0000 | 1.0000 |
| main | authority (`mayor - citizen`) | -1.78 pp (0.0067) | -2.58 pp (0.0002) | **-0.80 pp** | [-2.24, +0.63 pp] | 0.2741 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +56.32 pp (<0.0001) | +55.76 pp (<0.0001) | **-0.56 pp** | [-2.00, +0.88 pp] | 0.4439 | 1.0000 |
| main | wealth (`rich - poor`) | +4.82 pp (<0.0001) | +5.38 pp (<0.0001) | **+0.56 pp** | [-0.88, +2.00 pp] | 0.4439 | 1.0000 |
| main | gender (`woman - man`) | +0.36 pp (0.5839) | +0.57 pp (0.4014) | **+0.21 pp** | [-1.22, +1.65 pp] | 0.7706 | 1.0000 |
| main | age (`old - young`) | -1.27 pp (0.0528) | -1.80 pp (0.0083) | **-0.53 pp** | [-1.97, +0.90 pp] | 0.4659 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -13.92 pp (<0.0001) | -14.34 pp (<0.0001) | **-0.43 pp** | [-3.30, +2.44 pp] | 0.7706 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -5.37 pp (<0.0001) | -5.58 pp (<0.0001) | **-0.21 pp** | [-3.09, +2.66 pp] | 0.8841 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -2.11 pp (0.1074) | -1.84 pp (0.1770) | **+0.27 pp** | [-2.60, +3.14 pp] | 0.8554 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -3.50 pp (0.0076) | -1.84 pp (0.1770) | **+1.66 pp** | [-1.22, +4.53 pp] | 0.2584 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=29,858, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.04 pp (0.7677) | +0.01 pp (0.6528) | **-0.02 pp** | [-0.28, +0.23 pp] | 0.8544 | 1.0000 |
| main | authority (`mayor - citizen`) | -0.04 pp (0.7426) | +0.04 pp (0.1808) | **+0.08 pp** | [-0.17, +0.34 pp] | 0.5313 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +0.79 pp (<0.0001) | +0.01 pp (0.6548) | **-0.78 pp***** | [-1.03, -0.52 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.01 pp (0.9132) | +0.04 pp (0.1812) | **+0.03 pp** | [-0.23, +0.28 pp] | 0.8409 | 1.0000 |
| main | gender (`woman - man`) | -0.23 pp (0.0699) | +0.01 pp (0.7351) | **+0.24 pp** | [-0.02, +0.50 pp] | 0.0664 | 0.5976 |
| main | age (`old - young`) | +0.04 pp (0.7517) | -0.04 pp (0.1815) | **-0.08 pp** | [-0.34, +0.18 pp] | 0.5391 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.14 pp (0.5865) | +0.03 pp (0.6549) | **+0.16 pp** | [-0.35, +0.68 pp] | 0.5283 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.08 pp (0.7414) | +0.08 pp (0.1809) | **+0.16 pp** | [-0.35, +0.68 pp] | 0.5304 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.19 pp (0.4640) | -0.03 pp (0.6560) | **+0.16 pp** | [-0.35, +0.67 pp] | 0.5428 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.51 pp (0.0463) | -0.03 pp (0.6567) | **+0.48 pp** | [-0.03, +0.99 pp] | 0.0670 | 0.5976 |

**Outcome: FACT (%)** (n=29,858, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.16 pp (0.0851) | +1.17 pp (<0.0001) | **+1.01 pp***** | [+0.52, +1.49 pp] | <0.0001 | 0.0004 |
| main | authority (`mayor - citizen`) | +0.21 pp (0.0212) | -0.04 pp (0.8734) | **-0.25 pp** | [-0.74, +0.24 pp] | 0.3116 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +0.62 pp (<0.0001) | +2.64 pp (<0.0001) | **+2.03 pp***** | [+1.54, +2.51 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.05 pp (0.5635) | -0.33 pp (0.1505) | **-0.28 pp** | [-0.77, +0.20 pp] | 0.2567 | 1.0000 |
| main | gender (`woman - man`) | +0.19 pp (0.0404) | -0.03 pp (0.8817) | **-0.22 pp** | [-0.71, +0.26 pp] | 0.3643 | 1.0000 |
| main | age (`old - young`) | +0.16 pp (0.0832) | +0.28 pp (0.2280) | **+0.12 pp** | [-0.37, +0.61 pp] | 0.6278 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.27 pp (0.1520) | +0.46 pp (0.3271) | **+0.19 pp** | [-0.78, +1.16 pp] | 0.7003 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.37 pp (0.0438) | +0.19 pp (0.6819) | **-0.18 pp** | [-1.16, +0.79 pp] | 0.7118 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.16 pp (0.3865) | -1.04 pp (0.0251) | **-0.88 pp** | [-1.85, +0.09 pp] | 0.0750 | 0.5999 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.32 pp (0.0825) | +0.79 pp (0.0917) | **+0.46 pp** | [-0.51, +1.43 pp] | 0.3495 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=29,858, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.47 pp (0.4302) | +0.01 pp (0.9884) | **+0.48 pp** | [-0.97, +1.94 pp] | 0.5158 | 1.0000 |
| main | authority (`mayor - citizen`) | +2.82 pp (<0.0001) | +2.96 pp (<0.0001) | **+0.14 pp** | [-1.32, +1.60 pp] | 0.8492 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +4.94 pp (<0.0001) | +4.96 pp (<0.0001) | **+0.01 pp** | [-1.44, +1.47 pp] | 0.9845 | 1.0000 |
| main | wealth (`rich - poor`) | -2.02 pp (0.0008) | -2.41 pp (<0.0001) | **-0.39 pp** | [-1.85, +1.07 pp] | 0.6021 | 1.0000 |
| main | gender (`woman - man`) | +0.08 pp (0.8950) | -0.15 pp (0.8059) | **-0.23 pp** | [-1.69, +1.23 pp] | 0.7586 | 1.0000 |
| main | age (`old - young`) | -0.04 pp (0.9481) | +0.23 pp (0.7069) | **+0.27 pp** | [-1.19, +1.73 pp] | 0.7188 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -8.51 pp (<0.0001) | -7.90 pp (<0.0001) | **+0.61 pp** | [-2.31, +3.52 pp] | 0.6831 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.72 pp (0.5494) | +1.34 pp (0.2693) | **+0.62 pp** | [-2.29, +3.54 pp] | 0.6749 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -2.53 pp (0.0358) | -4.43 pp (0.0003) | **-1.90 pp** | [-4.82, +1.01 pp] | 0.2009 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.50 pp (0.6787) | -0.53 pp (0.6606) | **-1.03 pp** | [-3.95, +1.88 pp] | 0.4877 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,858, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -10.78 pp (<0.0001) | -11.37 pp (<0.0001) | **-0.59 pp** | [-2.11, +0.93 pp] | 0.4481 | 1.0000 |
| main | authority (`mayor - citizen`) | -1.49 pp (0.0102) | -0.89 pp (0.1256) | **+0.60 pp** | [-0.91, +2.12 pp] | 0.4357 | 1.0000 |
| main | reliability (`good_record - poor_record`) | -61.68 pp (<0.0001) | -62.11 pp (<0.0001) | **-0.44 pp** | [-1.95, +1.08 pp] | 0.5727 | 1.0000 |
| main | wealth (`rich - poor`) | -2.57 pp (<0.0001) | -2.92 pp (<0.0001) | **-0.36 pp** | [-1.88, +1.16 pp] | 0.6438 | 1.0000 |
| main | gender (`woman - man`) | -0.58 pp (0.3173) | -0.31 pp (0.5976) | **+0.28 pp** | [-1.24, +1.79 pp] | 0.7219 | 1.0000 |
| main | age (`old - young`) | +1.83 pp (0.0016) | +1.96 pp (0.0008) | **+0.13 pp** | [-1.39, +1.64 pp] | 0.8711 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +21.57 pp (<0.0001) | +21.77 pp (<0.0001) | **+0.20 pp** | [-2.83, +3.24 pp] | 0.8960 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +3.64 pp (0.0017) | +2.75 pp (0.0182) | **-0.90 pp** | [-3.93, +2.14 pp] | 0.5618 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +4.88 pp (<0.0001) | +6.60 pp (<0.0001) | **+1.73 pp** | [-1.31, +4.76 pp] | 0.2650 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +2.96 pp (0.0110) | +2.13 pp (0.0673) | **-0.83 pp** | [-3.87, +2.21 pp] | 0.5919 | 1.0000 |

**Outcome: CHECKED_TRUE (%)** (n=29,858, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.13 pp (0.3601) | +10.26 pp (<0.0001) | **+10.13 pp***** | [+8.75, +11.51 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.29 pp (0.0409) | -1.97 pp (0.0040) | **-2.26 pp**** | [-3.65, -0.88 pp] | 0.0013 | 0.0067 |
| main | reliability (`good_record - poor_record`) | +1.42 pp (<0.0001) | +54.88 pp (<0.0001) | **+53.45 pp***** | [+52.07, +54.84 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.03 pp (0.8512) | +5.58 pp (<0.0001) | **+5.60 pp***** | [+4.22, +6.99 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | +0.05 pp (0.7468) | +0.52 pp (0.4469) | **+0.47 pp** | [-0.91, +1.86 pp] | 0.5020 | 0.9149 |
| main | age (`old - young`) | -0.46 pp (0.0015) | -2.43 pp (0.0004) | **-1.97 pp*** | [-3.36, -0.59 pp] | 0.0051 | 0.0205 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.26 pp (0.3615) | -14.52 pp (<0.0001) | **-14.78 pp***** | [-17.55, -12.01 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.69 pp (0.0155) | -4.57 pp (0.0008) | **-5.27 pp**** | [-8.04, -2.50 pp] | 0.0002 | 0.0011 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.05 pp (0.8508) | -1.10 pp (0.4202) | **-1.05 pp** | [-3.81, +1.72 pp] | 0.4574 | 0.9149 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.16 pp (0.5811) | -2.52 pp (0.0659) | **-2.36 pp** | [-5.12, +0.41 pp] | 0.0947 | 0.2842 |

**Outcome: CHECKED_FALSE (%)** (n=29,858, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +10.93 pp (<0.0001) | -0.08 pp (0.3437) | **-11.01 pp***** | [-12.33, -9.69 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | -1.79 pp (0.0071) | -0.11 pp (0.2038) | **+1.69 pp** | [+0.37, +3.01 pp] | 0.0122 | 0.0610 |
| main | reliability (`good_record - poor_record`) | +53.90 pp (<0.0001) | -0.37 pp (<0.0001) | **-54.28 pp***** | [-55.60, -52.96 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +4.66 pp (<0.0001) | +0.05 pp (0.5265) | **-4.60 pp***** | [-5.92, -3.28 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | +0.50 pp (0.4557) | -0.04 pp (0.6423) | **-0.54 pp** | [-1.86, +0.78 pp] | 0.4259 | 0.4259 |
| main | age (`old - young`) | -1.54 pp (0.0207) | +0.00 pp (0.9969) | **+1.54 pp** | [+0.22, +2.86 pp] | 0.0221 | 0.0662 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -13.45 pp (<0.0001) | +0.16 pp (0.3423) | **+13.61 pp***** | [+10.97, +16.25 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -5.35 pp (<0.0001) | +0.21 pp (0.2069) | **+5.56 pp***** | [+2.92, +8.20 pp] | <0.0001 | 0.0002 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -1.95 pp (0.1435) | +0.00 pp (0.9974) | **+1.95 pp** | [-0.69, +4.59 pp] | 0.1477 | 0.2953 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -3.12 pp (0.0192) | +0.16 pp (0.3395) | **+3.28 pp** | [+0.64, +5.92 pp] | 0.0148 | 0.0610 |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=28,448, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) | LMM TD Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.0024 (0.2123) | +0.0659 (<0.0001) | **+0.0636***** | [+0.0515, +0.0756] | <0.0001 | <0.0001 | +0.0636 (p=<0.0001) |
| main | authority (`mayor - citizen`) | +0.0023 (0.2301) | +0.0254 (<0.0001) | **+0.0231***** | [+0.0110, +0.0352] | 0.0002 | 0.0007 | +0.0231 (p=0.0003) |
| main | reliability (`good_record - poor_record`) | +0.0183 (<0.0001) | +0.2843 (<0.0001) | **+0.2661***** | [+0.2540, +0.2781] | <0.0001 | <0.0001 | +0.2661 (p=<0.0001) |
| main | wealth (`rich - poor`) | +0.0033 (0.0866) | +0.0330 (<0.0001) | **+0.0297***** | [+0.0176, +0.0418] | <0.0001 | <0.0001 | +0.0297 (p=<0.0001) |
| main | gender (`woman - man`) | +0.0016 (0.4068) | +0.0022 (0.7128) | **+0.0006** | [-0.0114, +0.0126] | 0.9215 | 0.9215 | +0.0006 (p=0.9242) |
| main | age (`old - young`) | -0.0018 (0.3369) | -0.0205 (0.0005) | **-0.0187**** | [-0.0307, -0.0066] | 0.0024 | 0.0071 | -0.0187 (p=0.0034) |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.0070 (0.0691) | -0.1638 (<0.0001) | **-0.1568***** | [-0.1810, -0.1327] | <0.0001 | <0.0001 | -0.1568 (p=<0.0001) |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.0003 (0.9354) | -0.0725 (<0.0001) | **-0.0728***** | [-0.0970, -0.0487] | <0.0001 | <0.0001 | -0.0728 (p=<0.0001) |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +0.0129 (0.0008) | -0.0487 (<0.0001) | **-0.0616***** | [-0.0857, -0.0374] | <0.0001 | <0.0001 | -0.0616 (p=<0.0001) |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.0061 (0.1054) | -0.0067 (0.5677) | **-0.0128** | [-0.0368, +0.0113] | 0.2990 | 0.5981 | -0.0128 (p=0.3172) |

**Outcome: GO Rate (Verification %)** (n=29,952, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +3.95 pp (<0.0001) | +5.98 pp (<0.0001) | **+2.03 pp** | [+0.08, +3.98 pp] | 0.0414 | 0.4138 |
| main | authority (`mayor - citizen`) | +3.98 pp (<0.0001) | +4.19 pp (<0.0001) | **+0.21 pp** | [-1.74, +2.16 pp] | 0.8300 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +18.00 pp (<0.0001) | +18.24 pp (<0.0001) | **+0.24 pp** | [-1.71, +2.19 pp] | 0.8091 | 1.0000 |
| main | wealth (`rich - poor`) | +0.43 pp (0.5733) | -0.45 pp (0.5300) | **-0.88 pp** | [-2.83, +1.07 pp] | 0.3758 | 1.0000 |
| main | gender (`woman - man`) | +2.20 pp (0.0037) | +1.30 pp (0.0733) | **-0.91 pp** | [-2.86, +1.04 pp] | 0.3615 | 1.0000 |
| main | age (`old - young`) | -1.71 pp (0.0243) | -2.22 pp (0.0022) | **-0.51 pp** | [-2.46, +1.44 pp] | 0.6101 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -7.00 pp (<0.0001) | -8.33 pp (<0.0001) | **-1.34 pp** | [-5.24, +2.57 pp] | 0.5023 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -5.02 pp (0.0009) | -2.62 pp (0.0703) | **+2.40 pp** | [-1.50, +6.31 pp] | 0.2272 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -5.82 pp (0.0001) | -7.64 pp (<0.0001) | **-1.82 pp** | [-5.72, +2.08 pp] | 0.3615 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -2.78 pp (0.0672) | -2.03 pp (0.1604) | **+0.75 pp** | [-3.15, +4.65 pp] | 0.7071 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=29,753, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.82 pp (0.0654) | -0.05 pp (0.1864) | **-0.87 pp** | [-1.75, +0.00 pp] | 0.0506 | 0.4052 |
| main | authority (`mayor - citizen`) | +0.41 pp (0.3614) | -0.05 pp (0.1919) | **-0.46 pp** | [-1.33, +0.42 pp] | 0.3041 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +10.94 pp (<0.0001) | -0.08 pp (0.0449) | **-11.02 pp***** | [-11.90, -10.15 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.46 pp (0.2959) | +0.08 pp (0.0450) | **+0.55 pp** | [-0.33, +1.42 pp] | 0.2212 | 1.0000 |
| main | gender (`woman - man`) | -0.10 pp (0.8267) | -0.02 pp (0.6781) | **+0.08 pp** | [-0.79, +0.95 pp] | 0.8574 | 1.0000 |
| main | age (`old - young`) | -0.94 pp (0.0350) | -0.03 pp (0.5117) | **+0.91 pp** | [+0.04, +1.78 pp] | 0.0413 | 0.3721 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.98 pp (0.2676) | +0.05 pp (0.5170) | **+1.04 pp** | [-0.71, +2.78 pp] | 0.2449 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.43 pp (0.6320) | +0.05 pp (0.5170) | **-0.37 pp** | [-2.12, +1.37 pp] | 0.6761 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -1.21 pp (0.1720) | -0.22 pp (0.0073) | **+0.99 pp** | [-0.75, +2.74 pp] | 0.2646 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.41 pp (0.6405) | +0.11 pp (0.1880) | **-0.31 pp** | [-2.05, +1.44 pp] | 0.7297 | 1.0000 |

**Outcome: FACT (%)** (n=29,753, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.07 pp (0.3488) | +2.73 pp (<0.0001) | **+2.66 pp***** | [+1.78, +3.55 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | -0.01 pp (0.8474) | +1.66 pp (0.0002) | **+1.67 pp**** | [+0.79, +2.56 pp] | 0.0002 | 0.0016 |
| main | reliability (`good_record - poor_record`) | +0.31 pp (<0.0001) | +7.11 pp (<0.0001) | **+6.80 pp***** | [+5.92, +7.68 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.20 pp (0.0049) | +0.68 pp (0.1270) | **+0.48 pp** | [-0.40, +1.36 pp] | 0.2864 | 1.0000 |
| main | gender (`woman - man`) | +0.04 pp (0.5397) | +0.30 pp (0.5013) | **+0.26 pp** | [-0.63, +1.14 pp] | 0.5689 | 1.0000 |
| main | age (`old - young`) | -0.04 pp (0.5730) | -0.22 pp (0.6262) | **-0.18 pp** | [-1.06, +0.71 pp] | 0.6939 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.03 pp (0.8501) | +1.41 pp (0.1149) | **+1.43 pp** | [-0.33, +3.20 pp] | 0.1110 | 0.7770 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.08 pp (0.5700) | +0.26 pp (0.7703) | **+0.34 pp** | [-1.42, +2.11 pp] | 0.7041 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +0.24 pp (0.0911) | -0.36 pp (0.6833) | **-0.61 pp** | [-2.37, +1.16 pp] | 0.5010 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.19 pp (0.1878) | +0.22 pp (0.8027) | **+0.03 pp** | [-1.73, +1.80 pp] | 0.9690 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=29,753, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.27 pp (0.3890) | +1.55 pp (0.0002) | **+1.28 pp** | [+0.28, +2.27 pp] | 0.0117 | 0.1053 |
| main | authority (`mayor - citizen`) | +0.48 pp (0.1206) | +1.23 pp (0.0027) | **+0.75 pp** | [-0.24, +1.75 pp] | 0.1384 | 0.9690 |
| main | reliability (`good_record - poor_record`) | +2.04 pp (<0.0001) | +5.69 pp (<0.0001) | **+3.64 pp***** | [+2.65, +4.64 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.17 pp (0.5903) | -0.07 pp (0.8560) | **-0.24 pp** | [-1.24, +0.75 pp] | 0.6348 | 1.0000 |
| main | gender (`woman - man`) | +0.22 pp (0.4766) | +0.22 pp (0.5974) | **-0.00 pp** | [-1.00, +0.99 pp] | 0.9952 | 1.0000 |
| main | age (`old - young`) | -0.14 pp (0.6553) | +0.24 pp (0.5578) | **+0.38 pp** | [-0.62, +1.37 pp] | 0.4553 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -1.34 pp (0.0305) | +0.07 pp (0.9335) | **+1.41 pp** | [-0.58, +3.40 pp] | 0.1660 | 0.9958 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.26 pp (0.6780) | +0.21 pp (0.7965) | **-0.04 pp** | [-2.03, +1.94 pp] | 0.9648 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +1.87 pp (0.0025) | -0.31 pp (0.7064) | **-2.18 pp** | [-4.17, -0.19 pp] | 0.0317 | 0.2532 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.60 pp (0.3335) | +0.12 pp (0.8877) | **-0.48 pp** | [-2.47, +1.51 pp] | 0.6352 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,753, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -6.61 pp (<0.0001) | -7.29 pp (<0.0001) | **-0.68 pp** | [-2.26, +0.90 pp] | 0.3988 | 1.0000 |
| main | authority (`mayor - citizen`) | -3.13 pp (<0.0001) | -3.06 pp (<0.0001) | **+0.07 pp** | [-1.51, +1.65 pp] | 0.9296 | 1.0000 |
| main | reliability (`good_record - poor_record`) | -29.60 pp (<0.0001) | -31.00 pp (<0.0001) | **-1.40 pp** | [-2.98, +0.18 pp] | 0.0826 | 0.7435 |
| main | wealth (`rich - poor`) | -2.66 pp (<0.0001) | -3.35 pp (<0.0001) | **-0.69 pp** | [-2.28, +0.89 pp] | 0.3908 | 1.0000 |
| main | gender (`woman - man`) | -1.03 pp (0.1012) | -0.27 pp (0.6263) | **+0.75 pp** | [-0.83, +2.34 pp] | 0.3503 | 1.0000 |
| main | age (`old - young`) | +1.79 pp (0.0043) | +1.98 pp (0.0004) | **+0.19 pp** | [-1.39, +1.78 pp] | 0.8107 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +16.66 pp (<0.0001) | +16.25 pp (<0.0001) | **-0.41 pp** | [-3.58, +2.76 pp] | 0.7996 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +6.12 pp (<0.0001) | +7.11 pp (<0.0001) | **+0.99 pp** | [-2.18, +4.16 pp] | 0.5400 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +4.89 pp (<0.0001) | +5.37 pp (<0.0001) | **+0.47 pp** | [-2.69, +3.64 pp] | 0.7702 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +3.80 pp (0.0024) | +0.63 pp (0.5742) | **-3.17 pp** | [-6.33, -0.00 pp] | 0.0497 | 0.4974 |

**Outcome: CHECKED_TRUE (%)** (n=29,753, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.03 pp (0.4517) | +3.12 pp (<0.0001) | **+3.09 pp***** | [+1.60, +4.59 pp] | <0.0001 | 0.0003 |
| main | authority (`mayor - citizen`) | -0.03 pp (0.4489) | +0.30 pp (0.6955) | **+0.32 pp** | [-1.17, +1.82 pp] | 0.6699 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +0.08 pp (0.0270) | +18.53 pp (<0.0001) | **+18.45 pp***** | [+16.95, +19.94 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.00 pp (0.9997) | +2.61 pp (0.0006) | **+2.61 pp**** | [+1.12, +4.10 pp] | 0.0006 | 0.0037 |
| main | gender (`woman - man`) | -0.01 pp (0.8579) | -0.20 pp (0.7923) | **-0.19 pp** | [-1.69, +1.30 pp] | 0.7996 | 1.0000 |
| main | age (`old - young`) | -0.03 pp (0.4567) | -1.92 pp (0.0114) | **-1.90 pp** | [-3.39, -0.40 pp] | 0.0128 | 0.0514 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.05 pp (0.4557) | -17.83 pp (<0.0001) | **-17.89 pp***** | [-20.87, -14.90 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.05 pp (0.4525) | -7.64 pp (<0.0001) | **-7.58 pp***** | [-10.57, -4.59 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +0.00 pp (0.9990) | -4.20 pp (0.0057) | **-4.20 pp*** | [-7.19, -1.22 pp] | 0.0058 | 0.0291 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.05 pp (0.4468) | -1.02 pp (0.5014) | **-1.08 pp** | [-4.06, +1.91 pp] | 0.4798 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=29,753, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +5.43 pp (<0.0001) | -0.05 pp (0.4541) | **-5.49 pp***** | [-6.96, -4.01 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +2.28 pp (0.0024) | -0.08 pp (0.2543) | **-2.36 pp**** | [-3.84, -0.89 pp] | 0.0017 | 0.0051 |
| main | reliability (`good_record - poor_record`) | +16.22 pp (<0.0001) | -0.24 pp (0.0006) | **-16.47 pp***** | [-17.94, -14.99 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +2.75 pp (0.0002) | +0.05 pp (0.4428) | **-2.70 pp**** | [-4.18, -1.22 pp] | 0.0003 | 0.0017 |
| main | gender (`woman - man`) | +0.87 pp (0.2483) | -0.03 pp (0.7066) | **-0.89 pp** | [-2.37, +0.58 pp] | 0.2355 | 0.4709 |
| main | age (`old - young`) | -0.65 pp (0.3896) | -0.05 pp (0.4470) | **+0.59 pp** | [-0.88, +2.07 pp] | 0.4320 | 0.4709 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -14.37 pp (<0.0001) | +0.05 pp (0.7125) | **+14.42 pp***** | [+11.47, +17.37 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -6.67 pp (<0.0001) | -0.00 pp (0.9982) | **+6.67 pp***** | [+3.72, +9.62 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -5.79 pp (0.0001) | -0.27 pp (0.0563) | **+5.52 pp**** | [+2.57, +8.48 pp] | 0.0002 | 0.0015 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -5.05 pp (0.0008) | -0.05 pp (0.7034) | **+5.00 pp**** | [+2.05, +7.95 pp] | 0.0009 | 0.0036 |

### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=58,790, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) | LMM TD Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.0002 (0.8626) | +0.0769 (<0.0001) | **+0.0771***** | [+0.0692, +0.0851] | <0.0001 | <0.0001 | +0.0771 (p=<0.0001) |
| main | authority (`mayor - citizen`) | +0.0007 (0.6091) | -0.0025 (0.5244) | **-0.0031** | [-0.0111, +0.0048] | 0.4409 | 0.4409 | -0.0031 (p=0.4497) |
| main | reliability (`good_record - poor_record`) | +0.0125 (<0.0001) | +0.1530 (<0.0001) | **+0.1405***** | [+0.1326, +0.1484] | <0.0001 | <0.0001 | +0.1405 (p=<0.0001) |
| main | wealth (`rich - poor`) | -0.0008 (0.5494) | +0.0247 (<0.0001) | **+0.0254***** | [+0.0175, +0.0334] | <0.0001 | <0.0001 | +0.0254 (p=<0.0001) |
| main | gender (`woman - man`) | +0.0024 (0.0572) | -0.0045 (0.2461) | **-0.0069** | [-0.0149, +0.0010] | 0.0870 | 0.2710 | -0.0069 (p=0.0930) |
| main | age (`old - young`) | -0.0002 (0.8903) | +0.0053 (0.1691) | **+0.0055** | [-0.0024, +0.0134] | 0.1742 | 0.3484 | +0.0055 (p=0.1828) |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.0017 (0.5110) | -0.1408 (<0.0001) | **-0.1425***** | [-0.1583, -0.1266] | <0.0001 | <0.0001 | -0.1424 (p=<0.0001) |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.0009 (0.7354) | -0.0147 (0.0573) | **-0.0156** | [-0.0315, +0.0003] | 0.0542 | 0.2710 | -0.0156 (p=0.0588) |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.0025 (0.3240) | -0.0540 (<0.0001) | **-0.0514***** | [-0.0673, -0.0356] | <0.0001 | <0.0001 | -0.0515 (p=<0.0001) |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.0011 (0.6744) | -0.0143 (0.0643) | **-0.0154** | [-0.0313, +0.0005] | 0.0571 | 0.2710 | -0.0154 (p=0.0622) |

**Outcome: GO Rate (Verification %)** (n=59,904, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +5.62 pp (<0.0001) | +5.06 pp (<0.0001) | **-0.55 pp** | [-1.56, +0.45 pp] | 0.2811 | 1.0000 |
| main | authority (`mayor - citizen`) | +1.76 pp (<0.0001) | -0.60 pp (0.0982) | **-2.36 pp***** | [-3.36, -1.35 pp] | <0.0001 | <0.0001 |
| main | reliability (`good_record - poor_record`) | +13.51 pp (<0.0001) | +4.25 pp (<0.0001) | **-9.26 pp***** | [-10.27, -8.25 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +3.16 pp (<0.0001) | +2.18 pp (<0.0001) | **-0.98 pp** | [-1.99, +0.03 pp] | 0.0563 | 0.3938 |
| main | gender (`woman - man`) | -0.10 pp (0.7928) | -0.02 pp (0.9494) | **+0.07 pp** | [-0.93, +1.08 pp] | 0.8864 | 1.0000 |
| main | age (`old - young`) | -0.01 pp (0.9855) | +0.15 pp (0.6860) | **+0.15 pp** | [-0.85, +1.16 pp] | 0.7652 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -7.14 pp (<0.0001) | -9.91 pp (<0.0001) | **-2.76 pp** | [-4.78, -0.75 pp] | 0.0072 | 0.0575 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -2.31 pp (0.0017) | -2.32 pp (0.0014) | **-0.01 pp** | [-2.03, +2.00 pp] | 0.9896 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -3.57 pp (<0.0001) | -3.34 pp (<0.0001) | **+0.23 pp** | [-1.79, +2.24 pp] | 0.8253 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -1.86 pp (0.0116) | -1.66 pp (0.0227) | **+0.20 pp** | [-1.82, +2.22 pp] | 0.8455 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=59,795, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.79 pp (<0.0001) | -0.05 pp (0.5481) | **+0.74 pp**** | [+0.33, +1.15 pp] | 0.0004 | 0.0037 |
| main | authority (`mayor - citizen`) | -0.54 pp (0.0053) | -0.29 pp (0.0002) | **+0.25 pp** | [-0.16, +0.66 pp] | 0.2344 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +0.23 pp (0.2218) | -0.27 pp (0.0004) | **-0.51 pp** | [-0.92, -0.10 pp] | 0.0147 | 0.1179 |
| main | wealth (`rich - poor`) | -0.12 pp (0.5278) | -0.09 pp (0.2632) | **+0.03 pp** | [-0.37, +0.44 pp] | 0.8695 | 1.0000 |
| main | gender (`woman - man`) | +0.14 pp (0.4822) | -0.21 pp (0.0080) | **-0.34 pp** | [-0.75, +0.07 pp] | 0.1014 | 0.6085 |
| main | age (`old - young`) | +0.00 pp (0.9906) | +0.03 pp (0.6656) | **+0.03 pp** | [-0.38, +0.44 pp] | 0.8804 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.92 pp (0.0172) | +0.36 pp (0.0206) | **+1.28 pp*** | [+0.46, +2.09 pp] | 0.0022 | 0.0200 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.94 pp (0.0142) | +0.04 pp (0.7981) | **+0.98 pp** | [+0.16, +1.80 pp] | 0.0186 | 0.1299 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.22 pp (0.5686) | +0.17 pp (0.2641) | **+0.39 pp** | [-0.42, +1.21 pp] | 0.3461 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.35 pp (0.3611) | +0.17 pp (0.2645) | **-0.18 pp** | [-0.99, +0.64 pp] | 0.6708 | 1.0000 |

**Outcome: FACT (%)** (n=59,795, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.18 pp (0.0217) | +2.23 pp (<0.0001) | **+2.05 pp***** | [+1.44, +2.66 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.03 pp (0.6684) | +0.48 pp (0.1139) | **+0.45 pp** | [-0.16, +1.06 pp] | 0.1527 | 0.7636 |
| main | reliability (`good_record - poor_record`) | +0.03 pp (0.6618) | +4.83 pp (<0.0001) | **+4.79 pp***** | [+4.18, +5.40 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.13 pp (0.1066) | +0.17 pp (0.5650) | **+0.05 pp** | [-0.56, +0.66 pp] | 0.8796 | 1.0000 |
| main | gender (`woman - man`) | -0.09 pp (0.2670) | -0.24 pp (0.4255) | **-0.15 pp** | [-0.76, +0.46 pp] | 0.6211 | 1.0000 |
| main | age (`old - young`) | -0.02 pp (0.8038) | +0.12 pp (0.6850) | **+0.14 pp** | [-0.47, +0.75 pp] | 0.6472 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.31 pp (0.0508) | -1.80 pp (0.0030) | **-1.49 pp** | [-2.71, -0.27 pp] | 0.0165 | 0.1157 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.04 pp (0.8018) | +1.81 pp (0.0027) | **+1.78 pp*** | [+0.56, +3.00 pp] | 0.0043 | 0.0348 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.04 pp (0.7978) | -1.04 pp (0.0858) | **-1.00 pp** | [-2.22, +0.22 pp] | 0.1080 | 0.6482 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.23 pp (0.1476) | -0.64 pp (0.2891) | **-0.87 pp** | [-2.09, +0.35 pp] | 0.1620 | 0.7636 |

**Outcome: UNCERTAIN (%)** (n=59,795, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.58 pp (0.0017) | -0.71 pp (0.0211) | **-0.13 pp** | [-0.85, +0.59 pp] | 0.7209 | 1.0000 |
| main | authority (`mayor - citizen`) | +0.06 pp (0.7438) | +1.33 pp (<0.0001) | **+1.27 pp**** | [+0.56, +1.99 pp] | 0.0005 | 0.0044 |
| main | reliability (`good_record - poor_record`) | +2.49 pp (<0.0001) | +7.22 pp (<0.0001) | **+4.73 pp***** | [+4.01, +5.44 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.45 pp (0.0152) | +0.39 pp (0.2078) | **+0.84 pp** | [+0.12, +1.55 pp] | 0.0217 | 0.1739 |
| main | gender (`woman - man`) | +0.68 pp (0.0003) | -0.03 pp (0.9340) | **-0.70 pp** | [-1.42, +0.01 pp] | 0.0541 | 0.2703 |
| main | age (`old - young`) | -0.04 pp (0.8088) | -0.12 pp (0.7042) | **-0.07 pp** | [-0.79, +0.64 pp] | 0.8432 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +1.11 pp (0.0027) | -0.46 pp (0.4508) | **-1.57 pp** | [-3.01, -0.14 pp] | 0.0310 | 0.2172 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.31 pp (0.4065) | +1.87 pp (0.0024) | **+1.56 pp** | [+0.13, +2.99 pp] | 0.0326 | 0.2172 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.29 pp (0.4400) | +0.88 pp (0.1512) | **+1.17 pp** | [-0.26, +2.60 pp] | 0.1089 | 0.4356 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.25 pp (0.4942) | -0.67 pp (0.2788) | **-0.41 pp** | [-1.85, +1.02 pp] | 0.5703 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=59,795, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -4.80 pp (<0.0001) | -7.22 pp (<0.0001) | **-2.42 pp***** | [-3.47, -1.38 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | -1.47 pp (0.0002) | -0.35 pp (0.3399) | **+1.12 pp** | [+0.07, +2.16 pp] | 0.0362 | 0.2170 |
| main | reliability (`good_record - poor_record`) | -12.16 pp (<0.0001) | -18.08 pp (<0.0001) | **-5.91 pp***** | [-6.96, -4.87 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -3.07 pp (<0.0001) | -2.51 pp (<0.0001) | **+0.56 pp** | [-0.49, +1.60 pp] | 0.2942 | 0.6461 |
| main | gender (`woman - man`) | -0.29 pp (0.4598) | +0.46 pp (0.2103) | **+0.75 pp** | [-0.30, +1.79 pp] | 0.1615 | 0.6461 |
| main | age (`old - young`) | +0.55 pp (0.1623) | -0.41 pp (0.2564) | **-0.96 pp** | [-2.01, +0.08 pp] | 0.0714 | 0.3572 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +11.70 pp (<0.0001) | +14.07 pp (<0.0001) | **+2.37 pp** | [+0.28, +4.46 pp] | 0.0263 | 0.1842 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +3.73 pp (<0.0001) | +0.43 pp (0.5576) | **-3.31 pp*** | [-5.39, -1.22 pp] | 0.0019 | 0.0154 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +5.98 pp (<0.0001) | +4.66 pp (<0.0001) | **-1.32 pp** | [-3.41, +0.77 pp] | 0.2151 | 0.6461 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +1.70 pp (0.0297) | +1.44 pp (0.0485) | **-0.26 pp** | [-2.35, +1.83 pp] | 0.8089 | 0.8089 |

**Outcome: CHECKED_TRUE (%)** (n=59,795, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.11 pp (0.0029) | +5.80 pp (<0.0001) | **+5.69 pp***** | [+4.70, +6.68 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.01 pp (0.7084) | -1.16 pp (0.0212) | **-1.17 pp** | [-2.16, -0.18 pp] | 0.0201 | 0.0805 |
| main | reliability (`good_record - poor_record`) | -0.07 pp (0.0622) | +7.02 pp (<0.0001) | **+7.09 pp***** | [+6.10, +8.07 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.03 pp (0.4579) | +2.15 pp (<0.0001) | **+2.13 pp***** | [+1.14, +3.11 pp] | <0.0001 | 0.0001 |
| main | gender (`woman - man`) | -0.02 pp (0.6512) | -0.03 pp (0.9515) | **-0.01 pp** | [-1.00, +0.97 pp] | 0.9778 | 1.0000 |
| main | age (`old - young`) | +0.03 pp (0.4617) | +0.45 pp (0.3710) | **+0.42 pp** | [-0.56, +1.41 pp] | 0.4013 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.05 pp (0.4529) | -12.26 pp (<0.0001) | **-12.20 pp***** | [-14.18, -10.23 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.08 pp (0.2604) | -4.19 pp (<0.0001) | **-4.11 pp***** | [-6.08, -2.14 pp] | <0.0001 | 0.0002 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.05 pp (0.4519) | -4.90 pp (<0.0001) | **-4.85 pp***** | [-6.82, -2.87 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.00 pp (0.9944) | -0.56 pp (0.5772) | **-0.56 pp** | [-2.53, +1.41 pp] | 0.5780 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=59,795, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +5.88 pp (<0.0001) | -0.05 pp (0.5571) | **-5.93 pp***** | [-6.81, -5.05 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +1.89 pp (<0.0001) | -0.02 pp (0.8005) | **-1.91 pp***** | [-2.80, -1.03 pp] | <0.0001 | 0.0001 |
| main | reliability (`good_record - poor_record`) | +9.47 pp (<0.0001) | -0.72 pp (<0.0001) | **-10.18 pp***** | [-11.07, -9.30 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +3.49 pp (<0.0001) | -0.11 pp (0.1516) | **-3.60 pp***** | [-4.49, -2.72 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | -0.42 pp (0.3454) | +0.05 pp (0.5593) | **+0.47 pp** | [-0.42, +1.35 pp] | 0.3014 | 0.6029 |
| main | age (`old - young`) | -0.51 pp (0.2507) | -0.07 pp (0.3514) | **+0.44 pp** | [-0.45, +1.32 pp] | 0.3328 | 0.6029 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -11.54 pp (<0.0001) | +0.09 pp (0.5554) | **+11.63 pp***** | [+9.86, +13.40 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -3.06 pp (0.0006) | +0.04 pp (0.7999) | **+3.10 pp**** | [+1.33, +4.87 pp] | 0.0006 | 0.0024 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -5.38 pp (<0.0001) | +0.23 pp (0.1511) | **+5.61 pp***** | [+3.84, +7.37 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -2.03 pp (0.0227) | +0.25 pp (0.1091) | **+2.28 pp*** | [+0.51, +4.05 pp] | 0.0115 | 0.0345 |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=29,840, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) | LMM TD Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.0048 (<0.0001) | +0.1158 (<0.0001) | **+0.1207***** | [+0.1117, +0.1297] | <0.0001 | <0.0001 | +0.1207 (p=<0.0001) |
| main | authority (`mayor - citizen`) | +0.0005 (0.5591) | +0.0149 (0.0009) | **+0.0144**** | [+0.0054, +0.0234] | 0.0017 | 0.0068 | +0.0144 (p=0.0017) |
| main | reliability (`good_record - poor_record`) | -0.0026 (0.0049) | +0.1589 (<0.0001) | **+0.1614***** | [+0.1524, +0.1704] | <0.0001 | <0.0001 | +0.1614 (p=<0.0001) |
| main | wealth (`rich - poor`) | -0.0017 (0.0542) | +0.0305 (<0.0001) | **+0.0322***** | [+0.0232, +0.0412] | <0.0001 | <0.0001 | +0.0322 (p=<0.0001) |
| main | gender (`woman - man`) | +0.0010 (0.2685) | +0.0015 (0.7432) | **+0.0005** | [-0.0085, +0.0095] | 0.9198 | 0.9198 | +0.0005 (p=0.9206) |
| main | age (`old - young`) | +0.0012 (0.1834) | +0.0065 (0.1480) | **+0.0053** | [-0.0037, +0.0143] | 0.2492 | 0.4984 | +0.0053 (p=0.2500) |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.0070 (0.0001) | -0.2167 (<0.0001) | **-0.2237***** | [-0.2416, -0.2057] | <0.0001 | <0.0001 | -0.2236 (p=<0.0001) |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.0021 (0.2392) | -0.0448 (<0.0001) | **-0.0470***** | [-0.0649, -0.0290] | <0.0001 | <0.0001 | -0.0470 (p=<0.0001) |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.0003 (0.8759) | -0.0652 (<0.0001) | **-0.0649***** | [-0.0829, -0.0469] | <0.0001 | <0.0001 | -0.0649 (p=<0.0001) |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.0008 (0.6492) | -0.0190 (0.0347) | **-0.0198** | [-0.0378, -0.0018] | 0.0309 | 0.0928 | -0.0198 (p=0.0313) |

**Outcome: GO Rate (Verification %)** (n=29,952, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +11.43 pp (<0.0001) | +11.19 pp (<0.0001) | **-0.24 pp** | [-1.19, +0.71 pp] | 0.6204 | 1.0000 |
| main | authority (`mayor - citizen`) | +2.56 pp (<0.0001) | +2.59 pp (<0.0001) | **+0.03 pp** | [-0.92, +0.98 pp] | 0.9561 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +13.70 pp (<0.0001) | +14.02 pp (<0.0001) | **+0.32 pp** | [-0.63, +1.27 pp] | 0.5090 | 1.0000 |
| main | wealth (`rich - poor`) | +4.51 pp (<0.0001) | +3.85 pp (<0.0001) | **-0.67 pp** | [-1.62, +0.28 pp] | 0.1688 | 1.0000 |
| main | gender (`woman - man`) | -0.30 pp (0.4209) | -0.38 pp (0.3091) | **-0.08 pp** | [-1.03, +0.87 pp] | 0.8689 | 1.0000 |
| main | age (`old - young`) | +0.13 pp (0.7213) | +0.11 pp (0.7761) | **-0.03 pp** | [-0.98, +0.92 pp] | 0.9561 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -22.38 pp (<0.0001) | -22.01 pp (<0.0001) | **+0.37 pp** | [-1.53, +2.28 pp] | 0.7000 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -5.29 pp (<0.0001) | -4.59 pp (<0.0001) | **+0.69 pp** | [-1.21, +2.60 pp] | 0.4743 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -8.55 pp (<0.0001) | -7.53 pp (<0.0001) | **+1.01 pp** | [-0.89, +2.92 pp] | 0.2957 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -3.95 pp (<0.0001) | -2.88 pp (0.0001) | **+1.07 pp** | [-0.83, +2.97 pp] | 0.2710 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=29,933, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.09 pp (0.4261) | +0.08 pp (0.1784) | **+0.17 pp** | [-0.09, +0.43 pp] | 0.1898 | 1.0000 |
| main | authority (`mayor - citizen`) | -0.15 pp (0.2096) | +0.00 pp (0.9994) | **+0.15 pp** | [-0.11, +0.41 pp] | 0.2663 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +0.01 pp (0.9088) | -0.00 pp (0.9999) | **-0.01 pp** | [-0.27, +0.25 pp] | 0.9191 | 1.0000 |
| main | wealth (`rich - poor`) | +0.04 pp (0.7306) | -0.11 pp (0.0725) | **-0.15 pp** | [-0.41, +0.11 pp] | 0.2652 | 1.0000 |
| main | gender (`woman - man`) | +0.04 pp (0.7533) | +0.02 pp (0.6990) | **-0.01 pp** | [-0.27, +0.25 pp] | 0.9174 | 1.0000 |
| main | age (`old - young`) | +0.01 pp (0.9076) | +0.03 pp (0.6533) | **+0.01 pp** | [-0.25, +0.27 pp] | 0.9207 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.13 pp (0.5677) | +0.05 pp (0.6551) | **-0.08 pp** | [-0.60, +0.44 pp] | 0.7604 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.19 pp (0.4232) | -0.00 pp (0.9998) | **+0.19 pp** | [-0.33, +0.71 pp] | 0.4782 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.03 pp (0.9087) | +0.11 pp (0.3694) | **+0.13 pp** | [-0.38, +0.65 pp] | 0.6129 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.13 pp (0.5696) | +0.05 pp (0.6538) | **-0.08 pp** | [-0.60, +0.44 pp] | 0.7629 | 1.0000 |

**Outcome: FACT (%)** (n=29,933, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.04 pp (0.2565) | +1.24 pp (<0.0001) | **+1.20 pp**** | [+0.58, +1.82 pp] | 0.0002 | 0.0014 |
| main | authority (`mayor - citizen`) | +0.04 pp (0.2561) | -0.28 pp (0.3746) | **-0.32 pp** | [-0.94, +0.30 pp] | 0.3112 | 1.0000 |
| main | reliability (`good_record - poor_record`) | -0.01 pp (0.7046) | +0.47 pp (0.1387) | **+0.48 pp** | [-0.14, +1.10 pp] | 0.1285 | 0.8998 |
| main | wealth (`rich - poor`) | +0.01 pp (0.7049) | +0.12 pp (0.7064) | **+0.11 pp** | [-0.52, +0.73 pp] | 0.7387 | 1.0000 |
| main | gender (`woman - man`) | +0.01 pp (0.7733) | +0.06 pp (0.8393) | **+0.05 pp** | [-0.57, +0.68 pp] | 0.8651 | 1.0000 |
| main | age (`old - young`) | +0.07 pp (0.0587) | -0.31 pp (0.3328) | **-0.37 pp** | [-0.99, +0.25 pp] | 0.2391 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.03 pp (0.7050) | -2.92 pp (<0.0001) | **-2.90 pp***** | [-4.14, -1.65 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.03 pp (0.7049) | -0.19 pp (0.7692) | **-0.16 pp** | [-1.40, +1.08 pp] | 0.8022 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +0.03 pp (0.7077) | -0.88 pp (0.1643) | **-0.91 pp** | [-2.15, +0.34 pp] | 0.1529 | 0.9172 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.08 pp (0.2566) | -0.99 pp (0.1174) | **-1.07 pp** | [-2.31, +0.17 pp] | 0.0913 | 0.7303 |

**Outcome: UNCERTAIN (%)** (n=29,933, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -1.10 pp (<0.0001) | -1.11 pp (0.0002) | **-0.02 pp** | [-0.68, +0.65 pp] | 0.9602 | 1.0000 |
| main | authority (`mayor - citizen`) | +0.03 pp (0.8621) | +0.84 pp (0.0053) | **+0.82 pp** | [+0.15, +1.48 pp] | 0.0160 | 0.1440 |
| main | reliability (`good_record - poor_record`) | -0.53 pp (0.0006) | +1.86 pp (<0.0001) | **+2.39 pp***** | [+1.73, +3.06 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.37 pp (0.0163) | -0.09 pp (0.7540) | **+0.28 pp** | [-0.38, +0.94 pp] | 0.4092 | 1.0000 |
| main | gender (`woman - man`) | +0.21 pp (0.1687) | -0.36 pp (0.2313) | **-0.58 pp** | [-1.24, +0.09 pp] | 0.0889 | 0.7115 |
| main | age (`old - young`) | +0.00 pp (0.9994) | -0.07 pp (0.8285) | **-0.07 pp** | [-0.73, +0.60 pp] | 0.8465 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +1.23 pp (<0.0001) | +1.03 pp (0.0870) | **-0.20 pp** | [-1.52, +1.13 pp] | 0.7727 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.37 pp (0.2295) | +0.99 pp (0.1015) | **+0.61 pp** | [-0.71, +1.94 pp] | 0.3638 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.00 pp (0.9983) | +0.30 pp (0.6251) | **+0.30 pp** | [-1.03, +1.62 pp] | 0.6622 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.11 pp (0.7288) | -0.56 pp (0.3506) | **-0.46 pp** | [-1.78, +0.87 pp] | 0.5009 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,933, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -9.60 pp (<0.0001) | -10.81 pp (<0.0001) | **-1.20 pp** | [-2.32, -0.09 pp] | 0.0347 | 0.3126 |
| main | authority (`mayor - citizen`) | -1.88 pp (<0.0001) | -1.85 pp (<0.0001) | **+0.03 pp** | [-1.09, +1.14 pp] | 0.9613 | 1.0000 |
| main | reliability (`good_record - poor_record`) | -13.02 pp (<0.0001) | -16.31 pp (<0.0001) | **-3.29 pp***** | [-4.41, -2.17 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -3.70 pp (<0.0001) | -2.85 pp (<0.0001) | **+0.85 pp** | [-0.27, +1.96 pp] | 0.1365 | 0.9553 |
| main | gender (`woman - man`) | +0.05 pp (0.8999) | +0.10 pp (0.8205) | **+0.05 pp** | [-1.07, +1.16 pp] | 0.9356 | 1.0000 |
| main | age (`old - young`) | +0.12 pp (0.7669) | -0.57 pp (0.1839) | **-0.69 pp** | [-1.81, +0.42 pp] | 0.2229 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +20.38 pp (<0.0001) | +20.75 pp (<0.0001) | **+0.37 pp** | [-1.86, +2.60 pp] | 0.7451 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +5.05 pp (<0.0001) | +3.92 pp (<0.0001) | **-1.13 pp** | [-3.36, +1.11 pp] | 0.3230 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +7.29 pp (<0.0001) | +6.02 pp (<0.0001) | **-1.27 pp** | [-3.50, +0.97 pp] | 0.2659 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +4.08 pp (<0.0001) | +1.99 pp (0.0206) | **-2.08 pp** | [-4.32, +0.15 pp] | 0.0673 | 0.5387 |

**Outcome: CHECKED_TRUE (%)** (n=29,933, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.03 pp (0.3677) | +10.81 pp (<0.0001) | **+10.78 pp***** | [+9.64, +11.93 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.00 pp (0.9909) | +1.35 pp (0.0206) | **+1.35 pp** | [+0.20, +2.49 pp] | 0.0209 | 0.0836 |
| main | reliability (`good_record - poor_record`) | +0.03 pp (0.3713) | +14.47 pp (<0.0001) | **+14.44 pp***** | [+13.30, +15.58 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.00 pp (0.9970) | +3.07 pp (<0.0001) | **+3.07 pp***** | [+1.92, +4.21 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | -0.02 pp (0.5704) | +0.24 pp (0.6803) | **+0.26 pp** | [-0.89, +1.40 pp] | 0.6593 | 1.0000 |
| main | age (`old - young`) | +0.05 pp (0.0711) | +0.97 pp (0.0949) | **+0.92 pp** | [-0.22, +2.06 pp] | 0.1153 | 0.3458 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.11 pp (0.0725) | -19.29 pp (<0.0001) | **-19.40 pp***** | [-21.68, -17.11 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.05 pp (0.3653) | -4.78 pp (<0.0001) | **-4.83 pp***** | [-7.11, -2.55 pp] | <0.0001 | 0.0002 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.05 pp (0.3614) | -5.86 pp (<0.0001) | **-5.81 pp***** | [-8.09, -3.53 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.05 pp (0.3649) | -0.65 pp (0.5740) | **-0.71 pp** | [-2.99, +1.58 pp] | 0.5438 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=29,933, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +10.72 pp (<0.0001) | -0.21 pp (0.0106) | **-10.94 pp***** | [-11.83, -10.04 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +1.96 pp (<0.0001) | -0.05 pp (0.5220) | **-2.01 pp***** | [-2.91, -1.12 pp] | <0.0001 | <0.0001 |
| main | reliability (`good_record - poor_record`) | +13.53 pp (<0.0001) | -0.48 pp (<0.0001) | **-14.01 pp***** | [-14.91, -13.12 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +4.02 pp (<0.0001) | -0.13 pp (0.1100) | **-4.15 pp***** | [-5.05, -3.26 pp] | <0.0001 | <0.0001 |
| main | gender (`woman - man`) | -0.30 pp (0.5080) | -0.06 pp (0.4521) | **+0.23 pp** | [-0.66, +1.13 pp] | 0.6110 | 1.0000 |
| main | age (`old - young`) | -0.26 pp (0.5664) | -0.05 pp (0.5220) | **+0.20 pp** | [-0.69, +1.10 pp] | 0.6582 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -21.83 pp (<0.0001) | +0.37 pp (0.0254) | **+22.20 pp***** | [+20.41, +23.99 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -5.26 pp (<0.0001) | +0.05 pp (0.7506) | **+5.31 pp***** | [+3.52, +7.11 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -7.23 pp (<0.0001) | +0.32 pp (0.0548) | **+7.56 pp***** | [+5.76, +9.35 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -4.24 pp (<0.0001) | +0.16 pp (0.3389) | **+4.40 pp***** | [+2.60, +6.19 pp] | <0.0001 | <0.0001 |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=28,950, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) | LMM TD Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.0043 (0.0791) | +0.0377 (<0.0001) | **+0.0333***** | [+0.0212, +0.0455] | <0.0001 | <0.0001 | +0.0333 (p=<0.0001) |
| main | authority (`mayor - citizen`) | +0.0006 (0.8070) | -0.0198 (0.0006) | **-0.0204**** | [-0.0325, -0.0082] | 0.0010 | 0.0071 | -0.0204 (p=0.0015) |
| main | reliability (`good_record - poor_record`) | +0.0287 (<0.0001) | +0.1473 (<0.0001) | **+0.1186***** | [+0.1065, +0.1308] | <0.0001 | <0.0001 | +0.1186 (p=<0.0001) |
| main | wealth (`rich - poor`) | +0.0002 (0.9464) | +0.0187 (0.0012) | **+0.0185*** | [+0.0064, +0.0307] | 0.0028 | 0.0146 | +0.0185 (p=0.0039) |
| main | gender (`woman - man`) | +0.0040 (0.1017) | -0.0103 (0.0727) | **-0.0143** | [-0.0265, -0.0022] | 0.0205 | 0.0819 | -0.0143 (p=0.0258) |
| main | age (`old - young`) | -0.0017 (0.4988) | +0.0043 (0.4587) | **+0.0059** | [-0.0062, +0.0180] | 0.3385 | 0.6771 | +0.0059 (p=0.3573) |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.0045 (0.3609) | -0.0645 (<0.0001) | **-0.0600***** | [-0.0843, -0.0357] | <0.0001 | <0.0001 | -0.0600 (p=<0.0001) |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.0009 (0.8560) | +0.0158 (0.1702) | **+0.0167** | [-0.0076, +0.0410] | 0.1780 | 0.5339 | +0.0167 (p=0.1946) |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.0050 (0.3076) | -0.0426 (0.0002) | **-0.0376*** | [-0.0618, -0.0133] | 0.0024 | 0.0146 | -0.0376 (p=0.0035) |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.0014 (0.7771) | -0.0095 (0.4095) | **-0.0109** | [-0.0351, +0.0134] | 0.3794 | 0.6771 | -0.0109 (p=0.3980) |

**Outcome: GO Rate (Verification %)** (n=29,952, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.20 pp (0.7795) | -1.07 pp (0.1209) | **-0.87 pp** | [-2.81, +1.08 pp] | 0.3813 | 1.0000 |
| main | authority (`mayor - citizen`) | +0.95 pp (0.1852) | -3.79 pp (<0.0001) | **-4.74 pp***** | [-6.68, -2.80 pp] | <0.0001 | <0.0001 |
| main | reliability (`good_record - poor_record`) | +13.31 pp (<0.0001) | -5.53 pp (<0.0001) | **-18.84 pp***** | [-20.79, -16.90 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +1.80 pp (0.0118) | +0.51 pp (0.4613) | **-1.30 pp** | [-3.24, +0.65 pp] | 0.1914 | 1.0000 |
| main | gender (`woman - man`) | +0.11 pp (0.8794) | +0.34 pp (0.6264) | **+0.23 pp** | [-1.72, +2.17 pp] | 0.8189 | 1.0000 |
| main | age (`old - young`) | -0.15 pp (0.8374) | +0.19 pp (0.7861) | **+0.33 pp** | [-1.61, +2.28 pp] | 0.7363 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +8.09 pp (<0.0001) | +2.19 pp (0.1119) | **-5.90 pp*** | [-9.79, -2.02 pp] | 0.0029 | 0.0233 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.67 pp (0.6408) | -0.05 pp (0.9691) | **-0.72 pp** | [-4.61, +3.17 pp] | 0.7161 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +1.42 pp (0.3226) | +0.85 pp (0.5350) | **-0.56 pp** | [-4.45, +3.33 pp] | 0.7773 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.24 pp (0.8666) | -0.43 pp (0.7564) | **-0.67 pp** | [-4.55, +3.22 pp] | 0.7363 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=29,862, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -1.49 pp (<0.0001) | -0.17 pp (0.2183) | **+1.32 pp**** | [+0.55, +2.09 pp] | 0.0008 | 0.0077 |
| main | authority (`mayor - citizen`) | -0.93 pp (0.0110) | -0.58 pp (<0.0001) | **+0.35 pp** | [-0.42, +1.12 pp] | 0.3723 | 1.0000 |
| main | reliability (`good_record - poor_record`) | +0.47 pp (0.1983) | -0.55 pp (0.0001) | **-1.02 pp** | [-1.79, -0.25 pp] | 0.0098 | 0.0781 |
| main | wealth (`rich - poor`) | -0.29 pp (0.4310) | -0.07 pp (0.6333) | **+0.22 pp** | [-0.55, +0.99 pp] | 0.5764 | 1.0000 |
| main | gender (`woman - man`) | +0.23 pp (0.5259) | -0.44 pp (0.0020) | **-0.67 pp** | [-1.44, +0.10 pp] | 0.0896 | 0.5374 |
| main | age (`old - young`) | -0.01 pp (0.9852) | +0.04 pp (0.7723) | **+0.05 pp** | [-0.72, +0.82 pp] | 0.9038 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -1.98 pp (0.0066) | +0.67 pp (0.0179) | **+2.64 pp**** | [+1.10, +4.19 pp] | 0.0008 | 0.0077 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -1.70 pp (0.0193) | +0.08 pp (0.7773) | **+1.78 pp** | [+0.24, +3.32 pp] | 0.0233 | 0.1632 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.42 pp (0.5653) | +0.24 pp (0.3936) | **+0.66 pp** | [-0.88, +2.20 pp] | 0.4018 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.58 pp (0.4274) | +0.29 pp (0.2973) | **-0.28 pp** | [-1.83, +1.26 pp] | 0.7176 | 1.0000 |

**Outcome: FACT (%)** (n=29,862, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.32 pp (0.0357) | +3.23 pp (<0.0001) | **+2.90 pp***** | [+1.88, +3.93 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | +0.03 pp (0.8568) | +1.24 pp (0.0136) | **+1.21 pp** | [+0.18, +2.23 pp] | 0.0209 | 0.1465 |
| main | reliability (`good_record - poor_record`) | +0.08 pp (0.5813) | +9.19 pp (<0.0001) | **+9.10 pp***** | [+8.08, +10.13 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +0.24 pp (0.1160) | +0.23 pp (0.6443) | **-0.01 pp** | [-1.04, +1.02 pp] | 0.9852 | 1.0000 |
| main | gender (`woman - man`) | -0.19 pp (0.2253) | -0.55 pp (0.2748) | **-0.36 pp** | [-1.39, +0.66 pp] | 0.4902 | 1.0000 |
| main | age (`old - young`) | -0.11 pp (0.4899) | +0.55 pp (0.2704) | **+0.66 pp** | [-0.37, +1.68 pp] | 0.2086 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.59 pp (0.0544) | -0.67 pp (0.5052) | **-0.08 pp** | [-2.13, +1.97 pp] | 0.9408 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.11 pp (0.7294) | +3.81 pp (0.0001) | **+3.71 pp**** | [+1.65, +5.76 pp] | 0.0004 | 0.0032 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.11 pp (0.7256) | -1.20 pp (0.2312) | **-1.09 pp** | [-3.14, +0.96 pp] | 0.2967 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.38 pp (0.2177) | -0.29 pp (0.7718) | **-0.67 pp** | [-2.72, +1.38 pp] | 0.5230 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=29,862, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | -0.06 pp (0.8502) | -0.30 pp (0.5663) | **-0.24 pp** | [-1.50, +1.02 pp] | 0.7101 | 1.0000 |
| main | authority (`mayor - citizen`) | +0.10 pp (0.7790) | +1.82 pp (0.0005) | **+1.73 pp** | [+0.47, +2.99 pp] | 0.0070 | 0.0634 |
| main | reliability (`good_record - poor_record`) | +5.54 pp (<0.0001) | +12.58 pp (<0.0001) | **+7.04 pp***** | [+5.79, +8.30 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -0.53 pp (0.1184) | +0.87 pp (0.0976) | **+1.40 pp** | [+0.14, +2.66 pp] | 0.0288 | 0.2018 |
| main | gender (`woman - man`) | +1.14 pp (0.0008) | +0.31 pp (0.5562) | **-0.83 pp** | [-2.09, +0.43 pp] | 0.1961 | 0.7846 |
| main | age (`old - young`) | -0.09 pp (0.7945) | -0.17 pp (0.7494) | **-0.08 pp** | [-1.34, +1.18 pp] | 0.9003 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +0.99 pp (0.1440) | -1.95 pp (0.0644) | **-2.94 pp** | [-5.46, -0.43 pp] | 0.0219 | 0.1755 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +0.24 pp (0.7215) | +2.74 pp (0.0093) | **+2.50 pp** | [-0.01, +5.02 pp] | 0.0513 | 0.3079 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.58 pp (0.3924) | +1.48 pp (0.1617) | **+2.06 pp** | [-0.46, +4.57 pp] | 0.1093 | 0.5463 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.39 pp (0.5636) | -0.77 pp (0.4670) | **-0.38 pp** | [-2.89, +2.14 pp] | 0.7691 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,862, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.01 pp (0.9891) | -3.64 pp (<0.0001) | **-3.65 pp***** | [-5.27, -2.02 pp] | <0.0001 | <0.0001 |
| main | authority (`mayor - citizen`) | -1.04 pp (0.0963) | +1.16 pp (0.0301) | **+2.20 pp** | [+0.57, +3.83 pp] | 0.0080 | 0.0558 |
| main | reliability (`good_record - poor_record`) | -11.27 pp (<0.0001) | -19.84 pp (<0.0001) | **-8.57 pp***** | [-10.19, -6.94 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | -2.45 pp (<0.0001) | -2.18 pp (<0.0001) | **+0.28 pp** | [-1.35, +1.90 pp] | 0.7364 | 1.0000 |
| main | gender (`woman - man`) | -0.63 pp (0.3125) | +0.82 pp (0.1258) | **+1.45 pp** | [-0.18, +3.08 pp] | 0.0803 | 0.4016 |
| main | age (`old - young`) | +0.98 pp (0.1192) | -0.26 pp (0.6305) | **-1.23 pp** | [-2.86, +0.39 pp] | 0.1367 | 0.5469 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | +2.99 pp (0.0170) | +7.39 pp (<0.0001) | **+4.39 pp** | [+1.14, +7.64 pp] | 0.0081 | 0.0558 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | +2.41 pp (0.0546) | -3.07 pp (0.0040) | **-5.48 pp**** | [-8.73, -2.23 pp] | 0.0010 | 0.0076 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | +4.65 pp (0.0002) | +3.28 pp (0.0021) | **-1.37 pp** | [-4.62, +1.88 pp] | 0.4099 | 1.0000 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.67 pp (0.5939) | +0.89 pp (0.4032) | **+1.56 pp** | [-1.69, +4.81 pp] | 0.3467 | 1.0000 |

**Outcome: CHECKED_TRUE (%)** (n=29,862, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +0.19 pp (0.0031) | +0.77 pp (0.3269) | **+0.58 pp** | [-0.96, +2.12 pp] | 0.4601 | 1.0000 |
| main | authority (`mayor - citizen`) | +0.03 pp (0.6750) | -3.66 pp (<0.0001) | **-3.68 pp***** | [-5.22, -2.14 pp] | <0.0001 | <0.0001 |
| main | reliability (`good_record - poor_record`) | -0.16 pp (0.0111) | -0.43 pp (0.5789) | **-0.27 pp** | [-1.81, +1.27 pp] | 0.7275 | 1.0000 |
| main | wealth (`rich - poor`) | +0.05 pp (0.3977) | +1.23 pp (0.1161) | **+1.18 pp** | [-0.36, +2.72 pp] | 0.1340 | 0.8038 |
| main | gender (`woman - man`) | -0.02 pp (0.8086) | -0.30 pp (0.7019) | **-0.28 pp** | [-1.82, +1.26 pp] | 0.7173 | 1.0000 |
| main | age (`old - young`) | -0.00 pp (0.9928) | -0.07 pp (0.9251) | **-0.07 pp** | [-1.61, +1.47 pp] | 0.9259 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -0.22 pp (0.0899) | -5.25 pp (0.0008) | **-5.03 pp*** | [-8.11, -1.95 pp] | 0.0014 | 0.0122 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.22 pp (0.0880) | -3.59 pp (0.0218) | **-3.38 pp** | [-6.46, -0.30 pp] | 0.0316 | 0.2211 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -0.05 pp (0.6698) | -3.93 pp (0.0120) | **-3.88 pp** | [-6.96, -0.80 pp] | 0.0135 | 0.1081 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | -0.05 pp (0.6780) | -0.48 pp (0.7613) | **-0.42 pp** | [-3.50, +2.66 pp] | 0.7876 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=29,862, pairs=2,496)

| Type | Contrast | Effect in Rumor | Effect in Truth | Δ Truth Discount (Truth − Rumor) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness (`close_friend - stranger`) | +1.03 pp (0.1634) | +0.12 pp (0.2886) | **-0.91 pp** | [-2.38, +0.56 pp] | 0.2232 | 1.0000 |
| main | authority (`mayor - citizen`) | +1.82 pp (0.0142) | +0.01 pp (0.9024) | **-1.81 pp** | [-3.28, -0.34 pp] | 0.0160 | 0.1256 |
| main | reliability (`good_record - poor_record`) | +5.34 pp (<0.0001) | -0.95 pp (<0.0001) | **-6.29 pp***** | [-7.76, -4.82 pp] | <0.0001 | <0.0001 |
| main | wealth (`rich - poor`) | +2.98 pp (<0.0001) | -0.09 pp (0.4127) | **-3.07 pp***** | [-4.54, -1.60 pp] | <0.0001 | 0.0004 |
| main | gender (`woman - man`) | -0.53 pp (0.4713) | +0.16 pp (0.1737) | **+0.69 pp** | [-0.78, +2.16 pp] | 0.3571 | 1.0000 |
| main | age (`old - young`) | -0.78 pp (0.2955) | -0.09 pp (0.4079) | **+0.68 pp** | [-0.79, +2.15 pp] | 0.3630 | 1.0000 |
| interaction | closeness_by_reliability (`(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)`) | -1.20 pp (0.4185) | -0.19 pp (0.4113) | **+1.01 pp** | [-1.93, +3.95 pp] | 0.4991 | 1.0000 |
| interaction | authority_by_reliability (`(mayor-citizen | good_record) - (mayor-citizen | poor_record)`) | -0.84 pp (0.5718) | +0.03 pp (0.9053) | **+0.87 pp** | [-2.07, +3.81 pp] | 0.5636 | 1.0000 |
| interaction | wealth_by_reliability (`(rich-poor | good_record) - (rich-poor | poor_record)`) | -3.49 pp (0.0187) | +0.13 pp (0.5587) | **+3.62 pp** | [+0.68, +6.56 pp] | 0.0157 | 0.1256 |
| interaction | closeness_by_authority (`(close_friend-stranger | mayor) - (close_friend-stranger | citizen)`) | +0.16 pp (0.9159) | +0.35 pp (0.1264) | **+0.19 pp** | [-2.75, +3.13 pp] | 0.8986 | 1.0000 |

---

## 4. Top 10 Largest & Bottom 10 Smallest Truth Discount DNAs (`Truth − Rumor` — Matched-Pair Mean ± 1.96·SE)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

*Top 10 Largest Truth Discount (Best Truth Discrimination):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 426 / 466 | 39 | 0.054 | 0.932 | **0.879** [0.854, 0.904] | 77.4% | 79.3% | +1.9 pp |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | 429 / 464 | 39 | 0.061 | 0.936 | **0.875** [0.849, 0.901] | 76.5% | 75.4% | -1.1 pp |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | 430 / 466 | 39 | 0.060 | 0.926 | **0.865** [0.844, 0.887] | 78.0% | 79.7% | +1.7 pp |
| 4 | 21 | close_friend / citizen / good_record / poor / woman_old | 428 / 463 | 39 | 0.055 | 0.915 | **0.860** [0.836, 0.883] | 76.5% | 79.7% | +3.2 pp |
| 5 | 24 | close_friend / citizen / good_record / poor / man_old | 433 / 466 | 39 | 0.053 | 0.910 | **0.856** [0.824, 0.889] | 75.6% | 79.3% | +3.6 pp |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | 427 / 465 | 39 | 0.060 | 0.912 | **0.853** [0.824, 0.883] | 75.9% | 77.6% | +1.7 pp |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | 439 / 467 | 39 | 0.067 | 0.919 | **0.852** [0.828, 0.877] | 75.0% | 81.4% | +6.4 pp |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | 434 / 464 | 39 | 0.074 | 0.921 | **0.848** [0.823, 0.874] | 71.8% | 75.4% | +3.6 pp |
| 9 | 17 | close_friend / citizen / good_record / rich / woman_old | 430 / 462 | 39 | 0.055 | 0.900 | **0.846** [0.819, 0.874] | 76.5% | 78.0% | +1.5 pp |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | 429 / 466 | 39 | 0.073 | 0.915 | **0.843** [0.812, 0.874] | 74.8% | 78.8% | +4.1 pp |

*Bottom 10 Smallest Truth Discount (Most Discounted):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 460 / 466 | 39 | 0.030 | 0.265 | **0.234** [0.197, 0.271] | 22.0% | 23.1% | +1.1 pp |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 463 / 466 | 39 | 0.030 | 0.269 | **0.239** [0.191, 0.287] | 22.4% | 23.7% | +1.3 pp |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 457 / 465 | 39 | 0.035 | 0.283 | **0.247** [0.201, 0.294] | 24.4% | 25.6% | +1.3 pp |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | 460 / 462 | 39 | 0.041 | 0.306 | **0.265** [0.220, 0.310] | 28.6% | 26.5% | -2.1 pp |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 462 / 468 | 39 | 0.030 | 0.314 | **0.284** [0.250, 0.317] | 25.2% | 27.8% | +2.6 pp |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | 462 / 463 | 39 | 0.038 | 0.350 | **0.312** [0.270, 0.355] | 27.8% | 30.1% | +2.4 pp |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | 465 / 468 | 39 | 0.042 | 0.365 | **0.323** [0.278, 0.368] | 29.1% | 31.0% | +1.9 pp |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | 463 / 466 | 39 | 0.040 | 0.379 | **0.339** [0.302, 0.375] | 27.4% | 34.0% | +6.6 pp |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | 456 / 465 | 39 | 0.033 | 0.386 | **0.353** [0.304, 0.401] | 31.0% | 33.8% | +2.8 pp |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | 459 / 465 | 39 | 0.033 | 0.392 | **0.360** [0.325, 0.395] | 28.2% | 33.8% | +5.6 pp |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

*Top 10 Largest Truth Discount (Best Truth Discrimination):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 230 / 234 | 39 | 0.067 | 0.917 | **0.850** [0.809, 0.891] | 83.8% | 85.0% | +1.3 pp |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | 225 / 233 | 39 | 0.067 | 0.914 | **0.847** [0.811, 0.884] | 82.9% | 83.3% | +0.4 pp |
| 3 | 18 | close_friend / citizen / good_record / rich / man_young | 228 / 233 | 39 | 0.083 | 0.914 | **0.832** [0.777, 0.887] | 82.5% | 82.5% | +0.0 pp |
| 4 | 51 | stranger / citizen / good_record / rich / woman_young | 232 / 233 | 39 | 0.080 | 0.910 | **0.830** [0.797, 0.864] | 85.0% | 84.6% | -0.4 pp |
| 5 | 21 | close_friend / citizen / good_record / poor / woman_old | 230 / 233 | 39 | 0.078 | 0.903 | **0.826** [0.785, 0.866] | 84.6% | 81.6% | -3.0 pp |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | 231 / 234 | 39 | 0.082 | 0.906 | **0.823** [0.774, 0.872] | 82.1% | 85.5% | +3.4 pp |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | 230 / 231 | 39 | 0.074 | 0.887 | **0.815** [0.768, 0.862] | 84.6% | 81.2% | -3.4 pp |
| 8 | 5 | close_friend / mayor / good_record / poor / woman_old | 230 / 232 | 39 | 0.096 | 0.897 | **0.799** [0.758, 0.841] | 77.4% | 79.9% | +2.6 pp |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | 232 / 234 | 39 | 0.093 | 0.891 | **0.799** [0.746, 0.851] | 81.2% | 79.5% | -1.7 pp |
| 10 | 52 | stranger / citizen / good_record / rich / man_old | 228 / 232 | 39 | 0.103 | 0.899 | **0.796** [0.760, 0.833] | 76.9% | 82.5% | +5.6 pp |

*Bottom 10 Smallest Truth Discount (Most Discounted):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | 232 / 233 | 39 | 0.058 | 0.092 | **0.034** [-0.005, 0.072] | 3.8% | 4.7% | +0.9 pp |
| 2 | 45 | stranger / mayor / poor_record / poor / woman_old | 233 / 232 | 39 | 0.067 | 0.112 | **0.045** [0.006, 0.085] | 6.8% | 4.3% | -2.6 pp |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 233 / 233 | 39 | 0.047 | 0.107 | **0.059** [0.015, 0.103] | 4.7% | 6.0% | +1.3 pp |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | 234 / 234 | 39 | 0.049 | 0.109 | **0.060** [0.022, 0.098] | 4.7% | 5.1% | +0.4 pp |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 234 / 234 | 39 | 0.038 | 0.107 | **0.068** [0.033, 0.103] | 6.0% | 6.0% | +0.0 pp |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | 232 / 234 | 39 | 0.067 | 0.143 | **0.077** [0.033, 0.121] | 7.7% | 9.0% | +1.3 pp |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | 233 / 234 | 39 | 0.067 | 0.147 | **0.081** [0.036, 0.125] | 9.4% | 7.7% | -1.7 pp |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | 234 / 234 | 39 | 0.068 | 0.158 | **0.090** [0.042, 0.137] | 5.1% | 7.7% | +2.6 pp |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 232 / 234 | 39 | 0.058 | 0.186 | **0.127** [0.083, 0.171] | 14.5% | 12.8% | -1.7 pp |
| 10 | 44 | stranger / mayor / poor_record / rich / man_old | 233 / 233 | 39 | 0.054 | 0.195 | **0.142** [0.095, 0.189] | 16.2% | 15.8% | -0.4 pp |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

*Top 10 Largest Truth Discount (Best Truth Discrimination):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 210 / 232 | 39 | 0.021 | 0.953 | **0.933** [0.909, 0.956] | 78.2% | 78.2% | +0.0 pp |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | 199 / 233 | 39 | 0.028 | 0.957 | **0.931** [0.903, 0.959] | 73.9% | 83.8% | +9.8 pp |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | 198 / 233 | 39 | 0.018 | 0.946 | **0.929** [0.896, 0.962] | 76.1% | 82.5% | +6.4 pp |
| 4 | 24 | close_friend / citizen / good_record / poor / man_old | 201 / 232 | 39 | 0.007 | 0.929 | **0.923** [0.896, 0.950] | 70.1% | 79.1% | +9.0 pp |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | 198 / 232 | 39 | 0.018 | 0.938 | **0.919** [0.887, 0.950] | 70.5% | 77.8% | +7.3 pp |
| 6 | 56 | stranger / citizen / good_record / poor / man_old | 205 / 233 | 39 | 0.032 | 0.948 | **0.917** [0.885, 0.949] | 67.1% | 79.1% | +12.0 pp |
| 7 | 20 | close_friend / citizen / good_record / rich / man_old | 196 / 232 | 39 | 0.038 | 0.948 | **0.913** [0.883, 0.943] | 70.9% | 73.5% | +2.6 pp |
| 8 | 35 | stranger / mayor / good_record / rich / woman_young | 203 / 232 | 39 | 0.030 | 0.942 | **0.912** [0.883, 0.941] | 71.4% | 77.8% | +6.4 pp |
| 9 | 34 | stranger / mayor / good_record / rich / man_young | 193 / 232 | 39 | 0.023 | 0.933 | **0.910** [0.877, 0.942] | 67.5% | 77.4% | +9.8 pp |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | 198 / 233 | 39 | 0.038 | 0.942 | **0.907** [0.878, 0.935] | 70.9% | 74.8% | +3.8 pp |

*Bottom 10 Smallest Truth Discount (Most Discounted):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 226 / 232 | 39 | 0.011 | 0.422 | **0.412** [0.356, 0.469] | 39.3% | 41.0% | +1.7 pp |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 230 / 233 | 39 | 0.013 | 0.431 | **0.418** [0.350, 0.487] | 40.2% | 41.5% | +1.3 pp |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 225 / 232 | 39 | 0.011 | 0.474 | **0.462** [0.381, 0.543] | 44.9% | 46.6% | +1.7 pp |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | 227 / 230 | 39 | 0.015 | 0.502 | **0.488** [0.424, 0.553] | 50.4% | 48.7% | -1.7 pp |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 228 / 234 | 39 | 0.022 | 0.521 | **0.500** [0.446, 0.554] | 44.4% | 49.6% | +5.1 pp |
| 6 | 57 | stranger / citizen / poor_record / rich / woman_old | 223 / 231 | 39 | 0.013 | 0.561 | **0.547** [0.483, 0.612] | 47.0% | 51.7% | +4.7 pp |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | 229 / 229 | 39 | 0.009 | 0.557 | **0.551** [0.477, 0.624] | 46.2% | 52.6% | +6.4 pp |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | 231 / 234 | 39 | 0.015 | 0.573 | **0.557** [0.495, 0.620] | 53.0% | 54.3% | +1.3 pp |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 227 / 231 | 39 | 0.007 | 0.602 | **0.596** [0.537, 0.655] | 41.9% | 54.7% | +12.8 pp |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | 228 / 231 | 39 | 0.007 | 0.604 | **0.597** [0.540, 0.653] | 49.1% | 55.1% | +6.0 pp |

### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

*Top 10 Largest Truth Discount (Best Truth Discrimination):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | close_friend / mayor / good_record / poor / man_old | 461 / 467 | 39 | 0.023 | 0.934 | **0.911** [0.890, 0.932] | 66.7% | 59.2% | -7.5 pp |
| 2 | 3 | close_friend / mayor / good_record / rich / woman_young | 460 / 465 | 39 | 0.033 | 0.943 | **0.911** [0.891, 0.930] | 67.5% | 62.8% | -4.7 pp |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | 450 / 464 | 39 | 0.016 | 0.925 | **0.909** [0.892, 0.927] | 70.5% | 62.4% | -8.1 pp |
| 4 | 22 | close_friend / citizen / good_record / poor / man_young | 457 / 462 | 39 | 0.018 | 0.926 | **0.909** [0.892, 0.926] | 68.2% | 60.9% | -7.3 pp |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | 452 / 467 | 39 | 0.027 | 0.936 | **0.909** [0.891, 0.927] | 71.6% | 62.8% | -8.8 pp |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | 452 / 466 | 39 | 0.030 | 0.938 | **0.908** [0.888, 0.929] | 67.1% | 59.6% | -7.5 pp |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | 453 / 466 | 39 | 0.029 | 0.937 | **0.908** [0.889, 0.927] | 67.7% | 63.0% | -4.7 pp |
| 8 | 56 | stranger / citizen / good_record / poor / man_old | 448 / 463 | 39 | 0.026 | 0.931 | **0.906** [0.884, 0.928] | 63.2% | 62.6% | -0.6 pp |
| 9 | 18 | close_friend / citizen / good_record / rich / man_young | 456 / 467 | 39 | 0.025 | 0.930 | **0.905** [0.886, 0.925] | 67.9% | 62.2% | -5.8 pp |
| 10 | 24 | close_friend / citizen / good_record / poor / man_old | 450 / 461 | 39 | 0.023 | 0.928 | **0.905** [0.886, 0.924] | 67.9% | 61.3% | -6.6 pp |

*Bottom 10 Smallest Truth Discount (Most Discounted):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | 456 / 466 | 39 | 0.016 | 0.589 | **0.573** [0.530, 0.615] | 41.5% | 44.2% | +2.8 pp |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 452 / 462 | 39 | 0.019 | 0.606 | **0.587** [0.543, 0.631] | 44.4% | 44.2% | -0.2 pp |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 454 / 461 | 39 | 0.014 | 0.613 | **0.600** [0.548, 0.651] | 40.0% | 46.8% | +6.8 pp |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 452 / 463 | 39 | 0.009 | 0.617 | **0.608** [0.566, 0.650] | 44.7% | 44.4% | -0.2 pp |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 452 / 467 | 39 | 0.024 | 0.683 | **0.659** [0.615, 0.703] | 46.2% | 50.4% | +4.3 pp |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | 457 / 464 | 39 | 0.011 | 0.677 | **0.666** [0.619, 0.714] | 48.3% | 50.4% | +2.1 pp |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | 455 / 463 | 39 | 0.016 | 0.689 | **0.672** [0.625, 0.718] | 50.0% | 51.3% | +1.3 pp |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | 455 / 467 | 39 | 0.019 | 0.695 | **0.676** [0.631, 0.721] | 48.1% | 51.1% | +3.0 pp |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | 458 / 466 | 39 | 0.011 | 0.698 | **0.687** [0.641, 0.733] | 56.2% | 52.4% | -3.8 pp |
| 10 | 44 | stranger / mayor / poor_record / rich / man_old | 452 / 467 | 39 | 0.013 | 0.727 | **0.714** [0.672, 0.756] | 55.6% | 54.3% | -1.3 pp |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

*Top 10 Largest Truth Discount (Best Truth Discrimination):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | close_friend / citizen / good_record / poor / man_young | 234 / 233 | 39 | 0.002 | 0.989 | **0.987** [0.978, 0.997] | 100.0% | 100.0% | +0.0 pp |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | 233 / 233 | 39 | 0.004 | 0.987 | **0.983** [0.969, 0.997] | 99.6% | 99.1% | -0.4 pp |
| 3 | 17 | close_friend / citizen / good_record / rich / woman_old | 230 / 234 | 39 | 0.002 | 0.985 | **0.983** [0.969, 0.997] | 100.0% | 100.0% | +0.0 pp |
| 4 | 54 | stranger / citizen / good_record / poor / man_young | 232 / 233 | 39 | 0.002 | 0.985 | **0.983** [0.969, 0.997] | 99.1% | 99.6% | +0.4 pp |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | 232 / 234 | 39 | 0.004 | 0.985 | **0.981** [0.964, 0.997] | 98.7% | 99.6% | +0.9 pp |
| 6 | 7 | close_friend / mayor / good_record / poor / woman_young | 234 / 234 | 39 | 0.002 | 0.981 | **0.979** [0.967, 0.990] | 100.0% | 100.0% | +0.0 pp |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | 233 / 233 | 39 | 0.006 | 0.983 | **0.976** [0.963, 0.990] | 100.0% | 100.0% | +0.0 pp |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | 231 / 234 | 39 | 0.004 | 0.981 | **0.976** [0.962, 0.991] | 100.0% | 100.0% | +0.0 pp |
| 9 | 18 | close_friend / citizen / good_record / rich / man_young | 232 / 234 | 39 | 0.000 | 0.976 | **0.976** [0.962, 0.991] | 100.0% | 100.0% | +0.0 pp |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | 232 / 234 | 39 | 0.004 | 0.976 | **0.972** [0.957, 0.987] | 100.0% | 99.6% | -0.4 pp |

*Bottom 10 Smallest Truth Discount (Most Discounted):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | 231 / 234 | 39 | 0.015 | 0.551 | **0.536** [0.485, 0.586] | 59.4% | 56.8% | -2.6 pp |
| 2 | 62 | stranger / citizen / poor_record / poor / man_young | 233 / 234 | 39 | 0.004 | 0.573 | **0.568** [0.506, 0.631] | 64.5% | 60.7% | -3.8 pp |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 233 / 234 | 39 | 0.011 | 0.581 | **0.571** [0.511, 0.630] | 56.0% | 63.2% | +7.3 pp |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | 232 / 232 | 39 | 0.019 | 0.591 | **0.571** [0.512, 0.630] | 59.8% | 61.5% | +1.7 pp |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | 233 / 233 | 39 | 0.002 | 0.693 | **0.691** [0.624, 0.759] | 71.4% | 75.2% | +3.8 pp |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | 233 / 234 | 39 | 0.019 | 0.712 | **0.692** [0.645, 0.740] | 67.9% | 73.5% | +5.6 pp |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | 233 / 234 | 39 | 0.011 | 0.712 | **0.700** [0.648, 0.752] | 85.9% | 78.6% | -7.3 pp |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 234 / 233 | 39 | 0.017 | 0.719 | **0.702** [0.643, 0.761] | 80.8% | 76.1% | -4.7 pp |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 233 / 233 | 39 | 0.011 | 0.717 | **0.707** [0.642, 0.772] | 78.2% | 76.9% | -1.3 pp |
| 10 | 45 | stranger / mayor / poor_record / poor / woman_old | 232 / 234 | 39 | 0.015 | 0.731 | **0.716** [0.655, 0.777] | 73.9% | 76.5% | +2.6 pp |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

*Top 10 Largest Truth Discount (Best Truth Discrimination):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 56 | stranger / citizen / good_record / poor / man_old | 216 / 229 | 39 | 0.046 | 0.908 | **0.865** [0.828, 0.902] | 27.4% | 26.1% | -1.3 pp |
| 2 | 49 | stranger / citizen / good_record / rich / woman_old | 216 / 232 | 39 | 0.032 | 0.884 | **0.853** [0.821, 0.885] | 41.0% | 25.6% | -15.4 pp |
| 3 | 3 | close_friend / mayor / good_record / rich / woman_young | 226 / 232 | 39 | 0.066 | 0.916 | **0.851** [0.816, 0.886] | 35.0% | 25.6% | -9.4 pp |
| 4 | 8 | close_friend / mayor / good_record / poor / man_old | 227 / 233 | 39 | 0.040 | 0.888 | **0.850** [0.808, 0.891] | 33.8% | 18.8% | -15.0 pp |
| 5 | 24 | close_friend / citizen / good_record / poor / man_old | 217 / 228 | 39 | 0.048 | 0.893 | **0.844** [0.807, 0.880] | 35.9% | 23.1% | -12.8 pp |
| 6 | 20 | close_friend / citizen / good_record / rich / man_old | 221 / 233 | 39 | 0.050 | 0.891 | **0.840** [0.805, 0.874] | 43.2% | 25.6% | -17.5 pp |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | 213 / 233 | 39 | 0.054 | 0.888 | **0.834** [0.793, 0.875] | 38.5% | 26.5% | -12.0 pp |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | 224 / 233 | 39 | 0.051 | 0.884 | **0.834** [0.799, 0.868] | 35.9% | 24.4% | -11.5 pp |
| 9 | 21 | close_friend / citizen / good_record / poor / woman_old | 219 / 233 | 39 | 0.057 | 0.888 | **0.833** [0.794, 0.872] | 34.6% | 20.1% | -14.5 pp |
| 10 | 35 | stranger / mayor / good_record / rich / woman_young | 212 / 233 | 39 | 0.042 | 0.876 | **0.833** [0.792, 0.874] | 31.2% | 15.4% | -15.8 pp |

*Bottom 10 Smallest Truth Discount (Most Discounted):*

| Rank | Cell | Source DNA | Ment. N (R / T) | Belief Pairs | Rumor Belief | Truth Belief | Truth Discount [95% CI] | Rumor GO % | Truth GO % | Δ GO |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 220 / 230 | 39 | 0.018 | 0.622 | **0.606** [0.544, 0.669] | 29.1% | 26.9% | -2.1 pp |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 225 / 232 | 39 | 0.018 | 0.627 | **0.610** [0.554, 0.667] | 23.5% | 31.6% | +8.1 pp |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | 219 / 233 | 39 | 0.030 | 0.655 | **0.625** [0.569, 0.680] | 24.4% | 27.4% | +3.0 pp |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | 221 / 227 | 39 | 0.018 | 0.645 | **0.632** [0.562, 0.701] | 23.9% | 30.3% | +6.4 pp |
| 5 | 11 | close_friend / mayor / poor_record / rich / woman_young | 227 / 229 | 39 | 0.024 | 0.662 | **0.635** [0.570, 0.700] | 28.6% | 22.6% | -6.0 pp |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 223 / 233 | 39 | 0.022 | 0.659 | **0.637** [0.582, 0.692] | 22.2% | 25.6% | +3.4 pp |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | 221 / 230 | 39 | 0.016 | 0.659 | **0.640** [0.585, 0.695] | 19.2% | 26.5% | +7.3 pp |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | 224 / 231 | 39 | 0.020 | 0.660 | **0.641** [0.582, 0.700] | 25.2% | 25.6% | +0.4 pp |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | 219 / 229 | 39 | 0.014 | 0.662 | **0.651** [0.594, 0.709] | 24.8% | 28.2% | +3.4 pp |
| 10 | 41 | stranger / mayor / poor_record / rich / woman_old | 223 / 232 | 39 | 0.020 | 0.681 | **0.659** [0.599, 0.719] | 23.5% | 24.8% | +1.3 pp |