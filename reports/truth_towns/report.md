# Truth Towns Report (True Claims)

**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Condition:** `truth_twin` | **Towns:** 4,992 (2,496 per model) | **Expected Listeners:** 59,904

### Methodological & Missingness Disclosure
- **Excluded Invalid Judgments:** 213 / 59,904 (0.36%) had `judgment_status = invalid`. They are **completely excluded** (`NaN`), never turned into zeros.
- **Label % Denominator:** Valid judgments (`FACT + UNCERTAIN + SKEPTICAL + CHECKED_TRUE + CHECKED_FALSE + NOT_MENTIONED = 100%`).
- **Primary Belief Denominator:** Valid mentioning listeners (excluding `NOT_MENTIONED` and `INVALID`). Sensitivity checks (`Silence=0.0`, `Silence=0.5`) impute *only* valid `NOT_MENTIONED` rows.
- **Verification (`GO`/`SKIP`):** 0 missing or invalid decisions. 48 simulation decisions (21 first-hand, 27 second-hand; 0.08%) were `malformed_fallback_skip` in the simulation runner and appear as `SKIP`.
- **Statistical Model:** 10-term planned specification controlling simultaneously for all 6 knobs (`closeness`, `authority`, `reliability`, `wealth`, `gender`, `age`), the 4 planned interactions (`closeness × reliability`, `authority × reliability`, `wealth × reliability`, `closeness × authority`), and `real_artist`, with standard errors clustered by town (`run_id`) and Holm adjustment across all 10 planned contrasts per outcome. `Belief` also reports the spec's town-random-intercept LMM (`mixedlm`) check.

---

## 1. Overall Categorical & Behavioral Summary

### Table A: Per-Model Summary (First-Hand, Second-Hand, and Overall)

| Model | Layer | Valid N | Invalid (n / %) | Belief | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | First-Hand (Seats 1-6) | 14,927 | 49 (0.3%) | 0.573 | 0.573 | 0.573 | 48.5% | 51.5% | 2.0% | 16.3% | 34.3% | 47.1% | 0.3% | 0.0% | 100.0% | 87.1% |
| DeepSeek-V4-Flash | Second-Hand (Seats 7-12) | 14,836 | 140 (0.9%) | 0.789 | 0.788 | 0.788 | 67.9% | 32.1% | 7.9% | 6.9% | 17.5% | 67.5% | 0.2% | 0.1% | — | — |
| DeepSeek-V4-Flash | Overall (All 12 Listeners) | 29,763 | 189 (0.6%) | 0.680 | 0.680 | 0.680 | 58.2% | 41.8% | 4.9% | 11.6% | 25.9% | 57.3% | 0.2% | 0.0% | 100.0% | 87.1% |
| Qwen3.8-Flash | First-Hand (Seats 1-6) | 14,966 | 10 (0.1%) | 0.893 | 0.891 | 0.892 | 92.7% | 7.3% | 4.0% | 3.6% | 8.7% | 83.3% | 0.3% | 0.1% | 99.3% | 88.9% |
| Qwen3.8-Flash | Second-Hand (Seats 7-12) | 14,962 | 14 (0.1%) | 0.797 | 0.791 | 0.795 | 23.9% | 76.1% | 11.0% | 12.1% | 13.6% | 62.1% | 0.5% | 0.8% | — | — |
| Qwen3.8-Flash | Overall (All 12 Listeners) | 29,928 | 24 (0.1%) | 0.845 | 0.841 | 0.844 | 58.3% | 41.7% | 7.5% | 7.8% | 11.1% | 72.7% | 0.4% | 0.4% | 99.3% | 88.9% |

### Table B: Entire Experiment Average (Both Models Combined)

| Scope | Layer | Valid N | Invalid (n / %) | Belief | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Both Models Combined | First-Hand (Seats 1-6) | 29,893 | 59 (0.2%) | 0.733 | 0.732 | 0.733 | 70.6% | 29.4% | 3.0% | 9.9% | 21.5% | 65.2% | 0.3% | 0.1% | 99.6% | 88.3% |
| Both Models Combined | Second-Hand (Seats 7-12) | 29,798 | 154 (0.5%) | 0.793 | 0.790 | 0.792 | 45.9% | 54.1% | 9.4% | 9.5% | 15.6% | 64.8% | 0.3% | 0.4% | — | — |
| Both Models Combined | Overall (All 12 Listeners) | 59,691 | 213 (0.4%) | 0.763 | 0.761 | 0.762 | 58.2% | 41.8% | 6.2% | 9.7% | 18.5% | 65.0% | 0.3% | 0.2% | 99.6% | 88.3% |

---

## 2. Gatekeeper & Downstream Susceptibility (`Seat i <-> Seat i+6`)

Shows what happened to **Second-Hand Listeners (Seats 7-12)** depending on whether their paired **First-Hand Partner (Seats 1-6)** checked the noticeboard (`GO`) or did not (`SKIP`).

| Model | First-Hand Partner | Pairs (n / share) | SH GO % | SH Belief | SH FACT % | SH UNCERTAIN % | SH SKEPTICAL % | SH CHECKED_TRUE % | SH CHECKED_FALSE % | SH NOT_MENTIONED % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | ALL | 14,976 (100.0%) | 67.9% | 0.789 | 7.9% | 6.9% | 17.5% | 67.5% | 0.2% | 0.1% |
| DeepSeek-V4-Flash | GO | 7,259 (48.5%) | 69.9% | 0.920 | 12.0% | 9.7% | 3.1% | 75.1% | 0.1% | 0.0% |
| DeepSeek-V4-Flash | SKIP | 7,717 (51.5%) | 65.9% | 0.664 | 3.9% | 4.1% | 31.2% | 60.4% | 0.3% | 0.1% |
| Qwen3.8-Flash | ALL | 14,976 (100.0%) | 23.9% | 0.797 | 11.0% | 12.1% | 13.6% | 62.1% | 0.5% | 0.8% |
| Qwen3.8-Flash | GO | 13,888 (92.7%) | 21.3% | 0.814 | 11.7% | 12.8% | 11.7% | 62.7% | 0.4% | 0.7% |
| Qwen3.8-Flash | SKIP | 1,088 (7.3%) | 57.0% | 0.586 | 2.1% | 2.2% | 38.2% | 54.3% | 1.3% | 1.8% |
| Both Models Combined | ALL | 29,952 (100.0%) | 45.9% | 0.793 | 9.4% | 9.5% | 15.6% | 64.8% | 0.3% | 0.4% |
| Both Models Combined | GO | 21,147 (70.6%) | 38.0% | 0.850 | 11.8% | 11.8% | 8.7% | 66.9% | 0.3% | 0.4% |
| Both Models Combined | SKIP | 8,805 (29.4%) | 64.8% | 0.655 | 3.7% | 3.9% | 32.0% | 59.6% | 0.4% | 0.3% |

---

## 3. Controlled Effects: 6 Main Knobs + 4 Planned Interactions (Town-Clustered)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=29,750, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.7253 | 0.6352 | +0.0901*** | [+0.0816, +0.0986] | <0.0001 | <0.0001 | +0.0901 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.6853 | 0.6752 | +0.0101 | [+0.0016, +0.0186] | 0.0197 | 0.0590 | +0.0101 (p=0.0199) |
| main | reliability | `good_record - poor_record` | 0.9018 | 0.4587 | +0.4431*** | [+0.4346, +0.4516] | <0.0001 | <0.0001 | +0.4431 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.6986 | 0.6619 | +0.0367*** | [+0.0282, +0.0452] | <0.0001 | <0.0001 | +0.0367 (p=<0.0001) |
| main | gender | `woman - man` | 0.6819 | 0.6786 | +0.0033 | [-0.0052, +0.0117] | 0.4529 | 0.4529 | +0.0032 (p=0.4545) |
| main | age | `old - young` | 0.6699 | 0.6905 | -0.0206*** | [-0.0291, -0.0121] | <0.0001 | <0.0001 | -0.0206 (p=<0.0001) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0043 | +0.1759 | -0.1716*** | [-0.1886, -0.1546] | <0.0001 | <0.0001 | -0.1716 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0169 | +0.0371 | -0.0541*** | [-0.0711, -0.0371] | <0.0001 | <0.0001 | -0.0541 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0137 | +0.0597 | -0.0459*** | [-0.0629, -0.0290] | <0.0001 | <0.0001 | -0.0460 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0833 | +0.0969 | -0.0135 | [-0.0305, +0.0035] | 0.1186 | 0.2371 | -0.0135 (p=0.1192) |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.9039** [0.8990, 0.9089] | `close_friend + poor_record` = **0.5466** [0.5351, 0.5581] | `stranger + good_record` = **0.8996** [0.8946, 0.9047] | `stranger + poor_record` = **0.3707** [0.3604, 0.3810]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.1759*** | [+0.1604, +0.1913] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.0043 | [-0.0028, +0.0114] | 0.2317 |
| `reliability effect | closeness=stranger` | +0.5289*** | [+0.5174, +0.5404] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.3573*** | [+0.3448, +0.3699] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.8933** [0.8882, 0.8984] | `mayor + poor_record` = **0.4773** [0.4663, 0.4882] | `citizen + good_record` = **0.9102** [0.9053, 0.9152] | `citizen + poor_record` = **0.4401** [0.4292, 0.4510]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.0371*** | [+0.0217, +0.0526] | <0.0001 |
| `authority effect | reliability=good_record` | -0.0169*** | [-0.0240, -0.0098] | <0.0001 |
| `reliability effect | authority=citizen` | +0.4701*** | [+0.4582, +0.4821] | <0.0001 |
| `reliability effect | authority=mayor` | +0.4161*** | [+0.4040, +0.4282] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.9087** [0.9037, 0.9136] | `rich + poor_record` = **0.4885** [0.4773, 0.4998] | `poor + good_record` = **0.8949** [0.8898, 0.9000] | `poor + poor_record` = **0.4288** [0.4183, 0.4394]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.0597*** | [+0.0442, +0.0751] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.0137*** | [+0.0066, +0.0208] | 0.0001 |
| `reliability effect | wealth=poor` | +0.4661*** | [+0.4543, +0.4778] | <0.0001 |
| `reliability effect | wealth=rich` | +0.4201*** | [+0.4079, +0.4324] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.7270** [0.7180, 0.7360] | `close_friend + citizen` = **0.7236** [0.7149, 0.7323] | `stranger + mayor` = **0.6436** [0.6355, 0.6517] | `stranger + citizen` = **0.6267** [0.6186, 0.6349]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.0969*** | [+0.0849, +0.1088] | <0.0001 |
| `closeness effect | authority=mayor` | +0.0833*** | [+0.0713, +0.0954] | <0.0001 |
| `authority effect | closeness=stranger` | +0.0169** | [+0.0054, +0.0283] | 0.0040 |
| `authority effect | closeness=close_friend` | +0.0033 | [-0.0092, +0.0159] | 0.6004 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.7250 | 0.6349 | +0.0901*** | [+0.0817, +0.0986] | <0.0001 | <0.0001 | +0.0902 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.6850 | 0.6749 | +0.0101 | [+0.0016, +0.0186] | 0.0201 | 0.0602 | +0.0101 (p=0.0203) |
| main | reliability | `good_record - poor_record` | 0.9015 | 0.4584 | +0.4431*** | [+0.4347, +0.4516] | <0.0001 | <0.0001 | +0.4431 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.6982 | 0.6618 | +0.0364*** | [+0.0279, +0.0449] | <0.0001 | <0.0001 | +0.0364 (p=<0.0001) |
| main | gender | `woman - man` | 0.6816 | 0.6784 | +0.0032 | [-0.0053, +0.0117] | 0.4600 | 0.4600 | +0.0032 (p=0.4617) |
| main | age | `old - young` | 0.6698 | 0.6902 | -0.0204*** | [-0.0289, -0.0119] | <0.0001 | <0.0001 | -0.0204 (p=<0.0001) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0043 | +0.1760 | -0.1716*** | [-0.1886, -0.1547] | <0.0001 | <0.0001 | -0.1716 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0172 | +0.0373 | -0.0545*** | [-0.0715, -0.0375] | <0.0001 | <0.0001 | -0.0545 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0137 | +0.0591 | -0.0454*** | [-0.0624, -0.0284] | <0.0001 | <0.0001 | -0.0454 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0833 | +0.0970 | -0.0138 | [-0.0308, +0.0032] | 0.1116 | 0.2233 | -0.0138 (p=0.1123) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.7252 | 0.6352 | +0.0900*** | [+0.0816, +0.0985] | <0.0001 | <0.0001 | +0.0901 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.6852 | 0.6752 | +0.0100 | [+0.0015, +0.0185] | 0.0205 | 0.0614 | +0.0100 (p=0.0207) |
| main | reliability | `good_record - poor_record` | 0.9017 | 0.4587 | +0.4430*** | [+0.4345, +0.4515] | <0.0001 | <0.0001 | +0.4430 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.6986 | 0.6618 | +0.0367*** | [+0.0282, +0.0452] | <0.0001 | <0.0001 | +0.0367 (p=<0.0001) |
| main | gender | `woman - man` | 0.6818 | 0.6786 | +0.0032 | [-0.0053, +0.0117] | 0.4547 | 0.4547 | +0.0032 (p=0.4565) |
| main | age | `old - young` | 0.6699 | 0.6905 | -0.0206*** | [-0.0290, -0.0121] | <0.0001 | <0.0001 | -0.0205 (p=<0.0001) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0043 | +0.1758 | -0.1714*** | [-0.1884, -0.1545] | <0.0001 | <0.0001 | -0.1714 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0170 | +0.0371 | -0.0541*** | [-0.0711, -0.0372] | <0.0001 | <0.0001 | -0.0541 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0137 | +0.0597 | -0.0460*** | [-0.0630, -0.0290] | <0.0001 | <0.0001 | -0.0460 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0833 | +0.0968 | -0.0136 | [-0.0306, +0.0034] | 0.1170 | 0.2339 | -0.0136 (p=0.1177) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 62.51% | 53.81% | +8.70 pp*** | [+7.80, +9.60 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 58.57% | 57.76% | +0.81 pp | [-0.09, +1.70 pp] | 0.0770 | 0.1023 |
| main | reliability | `good_record - poor_record` | 76.66% | 39.66% | +37.00 pp*** | [+36.10, +37.89 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 59.40% | 56.93% | +2.46 pp*** | [+1.57, +3.36 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 58.64% | 57.68% | +0.96 pp | [+0.06, +1.85 pp] | 0.0365 | 0.1023 |
| main | age | `old - young` | 57.16% | 59.17% | -2.01 pp*** | [-2.91, -1.11 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +3.03 pp | +14.37 pp | -11.34 pp*** | [-13.13, -9.55 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.24 pp | +2.86 pp | -4.10 pp*** | [-5.89, -2.31 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.09 pp | +4.83 pp | -4.74 pp*** | [-6.53, -2.95 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +7.73 pp | +9.67 pp | -1.94 pp | [-3.73, -0.15 pp] | 0.0341 | 0.1023 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **78.18%** [77.40, 78.95%] | `close_friend + poor_record` = **46.85%** [45.81, 47.89%] | `stranger + good_record` = **75.15%** [74.35, 75.94%] | `stranger + poor_record` = **32.48%** [31.53, 33.42%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +14.37 pp*** | [+12.97, +15.77 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +3.03 pp*** | [+1.92, +4.14 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | +42.67 pp*** | [+41.43, +43.91 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +31.33 pp*** | [+30.03, +32.63 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **76.04%** [75.24, 76.84%] | `mayor + poor_record` = **41.09%** [40.09, 42.09%] | `citizen + good_record` = **77.28%** [76.51, 78.06%] | `citizen + poor_record` = **38.23%** [37.25, 39.22%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +2.86 pp*** | [+1.45, +4.26 pp] | <0.0001 |
| `authority effect | reliability=good_record` | -1.24 pp* | [-2.35, -0.13 pp] | 0.0287 |
| `reliability effect | authority=citizen` | +39.05 pp*** | [+37.80, +40.30 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +34.95 pp*** | [+33.67, +36.23 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **76.71%** [75.93, 77.49%] | `rich + poor_record` = **42.08%** [41.07, 43.09%] | `poor + good_record` = **76.62%** [75.82, 77.41%] | `poor + poor_record` = **37.25%** [36.27, 38.22%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +4.83 pp*** | [+3.43, +6.24 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.09 pp | [-1.02, +1.21 pp] | 0.8692 |
| `reliability effect | wealth=poor` | +39.37 pp*** | [+38.11, +40.63 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +34.63 pp*** | [+33.36, +35.90 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **62.43%** [61.50, 63.37%] | `close_friend + citizen` = **62.59%** [61.70, 63.49%] | `stranger + mayor` = **54.70%** [53.83, 55.58%] | `stranger + citizen` = **52.92%** [52.05, 53.80%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +9.67 pp*** | [+8.42, +10.92 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +7.73 pp*** | [+6.45, +9.01 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +1.78 pp** | [+0.54, +3.01 pp] | 0.0049 |
| `authority effect | closeness=close_friend` | -0.16 pp | [-1.46, +1.14 pp] | 0.8084 |


**Outcome: NOT_MENTIONED (%)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.03% | 0.05% | -0.02 pp | [-0.07, +0.03 pp] | 0.4050 | 1.0000 |
| main | authority | `mayor - citizen` | 0.04% | 0.05% | -0.01 pp | [-0.05, +0.04 pp] | 0.7779 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.03% | 0.06% | -0.03 pp | [-0.08, +0.01 pp] | 0.1628 | 1.0000 |
| main | wealth | `rich - poor` | 0.07% | 0.01% | +0.06 pp | [+0.01, +0.11 pp] | 0.0119 | 0.1193 |
| main | gender | `woman - man` | 0.05% | 0.04% | +0.01 pp | [-0.04, +0.06 pp] | 0.7549 | 1.0000 |
| main | age | `old - young` | 0.03% | 0.06% | -0.03 pp | [-0.08, +0.01 pp] | 0.1622 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.00 pp | -0.04 pp | +0.04 pp | [-0.05, +0.13 pp] | 0.4061 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.03 pp | -0.04 pp | +0.07 pp | [-0.03, +0.16 pp] | 0.1618 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.00 pp | +0.12 pp | -0.12 pp | [-0.22, -0.03 pp] | 0.0119 | 0.1193 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.00 pp | -0.04 pp | +0.04 pp | [-0.05, +0.13 pp] | 0.4027 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.03%** [-0.01, 0.06%] | `close_friend + poor_record` = **0.04%** [-0.01, 0.09%] | `stranger + good_record` = **0.03%** [-0.01, 0.06%] | `stranger + poor_record` = **0.08%** [0.02, 0.14%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.04 pp | [-0.12, +0.04 pp] | 0.3165 |
| `closeness effect | reliability=good_record` | -0.00 pp | [-0.05, +0.05 pp] | 0.9986 |
| `reliability effect | closeness=stranger` | -0.05 pp | [-0.13, +0.02 pp] | 0.1548 |
| `reliability effect | closeness=close_friend` | -0.01 pp | [-0.07, +0.05 pp] | 0.6506 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.04%** [-0.01, 0.09%] | `mayor + poor_record` = **0.04%** [-0.01, 0.09%] | `citizen + good_record` = **0.01%** [-0.01, 0.04%] | `citizen + poor_record` = **0.08%** [0.02, 0.14%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.04 pp | [-0.12, +0.04 pp] | 0.3115 |
| `authority effect | reliability=good_record` | +0.03 pp | [-0.03, +0.08 pp] | 0.3158 |
| `reliability effect | authority=citizen` | -0.07 pp | [-0.14, +0.00 pp] | 0.0562 |
| `reliability effect | authority=mayor` | +0.00 pp | [-0.06, +0.06 pp] | 0.9969 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.03%** [-0.01, 0.06%] | `rich + poor_record` = **0.12%** [0.04, 0.20%] | `poor + good_record` = **0.03%** [-0.01, 0.06%] | `poor + poor_record` = **-0.00%** [-0.00, 0.00%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.12 pp** | [+0.04, +0.20 pp] | 0.0025 |
| `wealth effect | reliability=good_record` | +0.00 pp | [-0.05, +0.05 pp] | 0.9998 |
| `reliability effect | wealth=poor` | +0.03 pp | [-0.01, +0.06 pp] | 0.1565 |
| `reliability effect | wealth=rich` | -0.09 pp* | [-0.18, -0.01 pp] | 0.0333 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.04%** [-0.01, 0.09%] | `close_friend + citizen` = **0.03%** [-0.01, 0.06%] | `stranger + mayor` = **0.04%** [-0.01, 0.09%] | `stranger + citizen` = **0.07%** [0.01, 0.13%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.04 pp | [-0.11, +0.03 pp] | 0.2537 |
| `closeness effect | authority=mayor` | +0.00 pp | [-0.06, +0.06 pp] | 0.9979 |
| `authority effect | closeness=stranger` | -0.03 pp | [-0.10, +0.05 pp] | 0.4749 |
| `authority effect | closeness=close_friend` | +0.01 pp | [-0.05, +0.07 pp] | 0.6562 |


**Outcome: FACT (%)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 5.89% | 3.95% | +1.95 pp*** | [+1.45, +2.45 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 5.33% | 4.52% | +0.81 pp* | [+0.31, +1.31 pp] | 0.0015 | 0.0116 |
| main | reliability | `good_record - poor_record` | 7.36% | 2.48% | +4.88 pp*** | [+4.38, +5.38 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 5.01% | 4.84% | +0.17 pp | [-0.33, +0.67 pp] | 0.5034 | 1.0000 |
| main | gender | `woman - man` | 4.99% | 4.85% | +0.14 pp | [-0.36, +0.64 pp] | 0.5897 | 1.0000 |
| main | age | `old - young` | 4.94% | 4.91% | +0.03 pp | [-0.47, +0.53 pp] | 0.9011 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +2.41 pp | +1.48 pp | +0.94 pp | [-0.06, +1.94 pp] | 0.0659 | 0.4612 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.93 pp | +0.69 pp | +0.24 pp | [-0.76, +1.24 pp] | 0.6396 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.18 pp | +0.52 pp | -0.71 pp | [-1.70, +0.29 pp] | 0.1669 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +2.20 pp | +1.69 pp | +0.51 pp | [-0.49, +1.51 pp] | 0.3194 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **8.57%** [7.91, 9.23%] | `close_friend + poor_record` = **3.22%** [2.81, 3.63%] | `stranger + good_record` = **6.15%** [5.60, 6.70%] | `stranger + poor_record` = **1.74%** [1.44, 2.05%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +1.48 pp*** | [+0.97, +1.99 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +2.41 pp*** | [+1.55, +3.27 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | +4.41 pp*** | [+3.78, +5.04 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +5.35 pp*** | [+4.57, +6.12 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **7.83%** [7.20, 8.45%] | `mayor + poor_record` = **2.83%** [2.44, 3.22%] | `citizen + good_record` = **6.90%** [6.30, 7.49%] | `citizen + poor_record` = **2.14%** [1.80, 2.47%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.69 pp** | [+0.18, +1.20 pp] | 0.0078 |
| `authority effect | reliability=good_record` | +0.93 pp* | [+0.07, +1.79 pp] | 0.0337 |
| `reliability effect | authority=citizen` | +4.76 pp*** | [+4.08, +5.44 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +5.00 pp*** | [+4.27, +5.73 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **7.27%** [6.67, 7.88%] | `rich + poor_record` = **2.74%** [2.38, 3.11%] | `poor + good_record` = **7.45%** [6.84, 8.06%] | `poor + poor_record` = **2.22%** [1.87, 2.57%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.52 pp* | [+0.01, +1.03 pp] | 0.0445 |
| `wealth effect | reliability=good_record` | -0.18 pp | [-1.04, +0.68 pp] | 0.6784 |
| `reliability effect | wealth=poor` | +5.23 pp*** | [+4.53, +5.94 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +4.53 pp*** | [+3.82, +5.23 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **6.43%** [5.85, 7.01%] | `close_friend + citizen` = **5.36%** [4.85, 5.88%] | `stranger + mayor` = **4.23%** [3.78, 4.67%] | `stranger + citizen` = **3.67%** [3.22, 4.12%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +1.69 pp*** | [+1.01, +2.37 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +2.20 pp*** | [+1.47, +2.93 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +0.56 pp | [-0.07, +1.19 pp] | 0.0830 |
| `authority effect | closeness=close_friend` | +1.07 pp** | [+0.29, +1.84 pp] | 0.0071 |


**Outcome: UNCERTAIN (%)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 11.98% | 11.19% | +0.78 pp | [+0.09, +1.48 pp] | 0.0273 | 0.1367 |
| main | authority | `mayor - citizen` | 12.63% | 10.54% | +2.10 pp*** | [+1.40, +2.79 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 14.24% | 8.93% | +5.31 pp*** | [+4.61, +6.00 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 10.96% | 12.21% | -1.24 pp** | [-1.94, -0.55 pp] | 0.0005 | 0.0032 |
| main | gender | `woman - man` | 11.60% | 11.57% | +0.03 pp | [-0.67, +0.72 pp] | 0.9432 | 1.0000 |
| main | age | `old - young` | 11.70% | 11.47% | +0.24 pp | [-0.46, +0.93 pp] | 0.5043 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -1.19 pp | +2.75 pp | -3.94 pp*** | [-5.33, -2.55 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +2.48 pp | +1.72 pp | +0.76 pp | [-0.63, +2.15 pp] | 0.2840 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -2.43 pp | -0.06 pp | -2.37 pp** | [-3.76, -0.98 pp] | 0.0008 | 0.0049 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.68 pp | +0.89 pp | -0.21 pp | [-1.60, +1.18 pp] | 0.7669 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **13.64%** [12.90, 14.39%] | `close_friend + poor_record` = **10.31%** [9.66, 10.96%] | `stranger + good_record` = **14.83%** [14.06, 15.60%] | `stranger + poor_record` = **7.56%** [6.95, 8.16%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +2.75 pp*** | [+1.87, +3.64 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -1.19 pp* | [-2.26, -0.12 pp] | 0.0297 |
| `reliability effect | closeness=stranger` | +7.28 pp*** | [+6.30, +8.25 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +3.34 pp*** | [+2.35, +4.33 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **15.48%** [14.70, 16.26%] | `mayor + poor_record` = **9.79%** [9.14, 10.44%] | `citizen + good_record` = **13.00%** [12.27, 13.73%] | `citizen + poor_record` = **8.07%** [7.47, 8.68%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +1.72 pp*** | [+0.83, +2.61 pp] | 0.0001 |
| `authority effect | reliability=good_record` | +2.48 pp*** | [+1.41, +3.55 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +4.93 pp*** | [+3.98, +5.87 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +5.69 pp*** | [+4.67, +6.70 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **13.02%** [12.28, 13.76%] | `rich + poor_record` = **8.90%** [8.27, 9.53%] | `poor + good_record` = **15.45%** [14.68, 16.23%] | `poor + poor_record` = **8.96%** [8.34, 9.58%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.06 pp | [-0.94, +0.83 pp] | 0.9005 |
| `wealth effect | reliability=good_record` | -2.43 pp*** | [-3.50, -1.36 pp] | <0.0001 |
| `reliability effect | wealth=poor` | +6.49 pp*** | [+5.50, +7.49 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +4.12 pp*** | [+3.15, +5.09 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **12.97%** [12.25, 13.70%] | `close_friend + citizen` = **10.98%** [10.30, 11.65%] | `stranger + mayor` = **12.30%** [11.58, 13.01%] | `stranger + citizen` = **10.09%** [9.43, 10.76%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.89 pp | [-0.06, +1.84 pp] | 0.0666 |
| `closeness effect | authority=mayor` | +0.68 pp | [-0.34, +1.69 pp] | 0.1915 |
| `authority effect | closeness=stranger` | +2.20 pp*** | [+1.23, +3.18 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | +1.99 pp*** | [+1.01, +2.98 pp] | <0.0001 |


**Outcome: SKEPTICAL (%)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 21.28% | 30.60% | -9.32 pp*** | [-10.17, -8.46 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 24.96% | 26.92% | -1.96 pp*** | [-2.81, -1.10 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 2.63% | 49.25% | -46.62 pp*** | [-47.48, -45.77 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 24.37% | 27.51% | -3.13 pp*** | [-3.99, -2.28 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 25.78% | 26.10% | -0.32 pp | [-1.17, +0.54 pp] | 0.4691 | 0.4691 |
| main | age | `old - young` | 26.93% | 24.95% | +1.98 pp*** | [+1.13, +2.84 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.17 pp | -18.81 pp | +18.99 pp*** | [+17.28, +20.70 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.49 pp | -4.40 pp | +4.89 pp*** | [+3.18, +6.60 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.14 pp | -6.13 pp | +5.98 pp*** | [+4.27, +7.69 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -8.62 pp | -10.01 pp | +1.39 pp | [-0.32, +3.10 pp] | 0.1113 | 0.2225 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **2.71%** [2.34, 3.09%] | `close_friend + poor_record` = **39.84%** [38.66, 41.03%] | `stranger + good_record` = **2.54%** [2.18, 2.90%] | `stranger + poor_record` = **58.66%** [57.54, 59.78%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -18.81 pp*** | [-20.44, -17.18 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.17 pp | [-0.34, +0.69 pp] | 0.5099 |
| `reliability effect | closeness=stranger` | -56.12 pp*** | [-57.29, -54.94 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -37.13 pp*** | [-38.37, -35.89 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **2.87%** [2.48, 3.26%] | `mayor + poor_record` = **47.05%** [45.88, 48.21%] | `citizen + good_record` = **2.38%** [2.04, 2.72%] | `citizen + poor_record` = **51.45%** [50.31, 52.59%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -4.40 pp*** | [-6.03, -2.77 pp] | <0.0001 |
| `authority effect | reliability=good_record` | +0.49 pp | [-0.03, +1.01 pp] | 0.0647 |
| `reliability effect | authority=citizen` | -49.07 pp*** | [-50.26, -47.88 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -44.18 pp*** | [-45.41, -42.95 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **2.55%** [2.19, 2.92%] | `rich + poor_record` = **46.19%** [45.03, 47.35%] | `poor + good_record` = **2.70%** [2.33, 3.06%] | `poor + poor_record` = **52.31%** [51.17, 53.45%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -6.13 pp*** | [-7.75, -4.50 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.14 pp | [-0.66, +0.38 pp] | 0.5857 |
| `reliability effect | wealth=poor` | -49.62 pp*** | [-50.81, -48.42 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -43.63 pp*** | [-44.85, -42.42 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **20.65%** [19.74, 21.55%] | `close_friend + citizen` = **21.91%** [21.06, 22.76%] | `stranger + mayor` = **29.27%** [28.44, 30.10%] | `stranger + citizen` = **31.92%** [31.09, 32.76%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -10.01 pp*** | [-11.20, -8.82 pp] | <0.0001 |
| `closeness effect | authority=mayor` | -8.62 pp*** | [-9.85, -7.40 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -2.65 pp*** | [-3.83, -1.48 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | -1.26 pp* | [-2.50, -0.02 pp] | 0.0465 |


**Outcome: CHECKED_TRUE (%)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 60.62% | 53.94% | +6.68 pp*** | [+5.67, +7.68 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 56.86% | 57.71% | -0.85 pp | [-1.86, +0.15 pp] | 0.0953 | 0.2465 |
| main | reliability | `good_record - poor_record` | 75.67% | 38.89% | +36.78 pp*** | [+35.78, +37.79 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 59.33% | 55.24% | +4.09 pp*** | [+3.09, +5.10 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 57.37% | 57.20% | +0.17 pp | [-0.83, +1.17 pp] | 0.7404 | 0.7404 |
| main | age | `old - young` | 56.19% | 58.38% | -2.19 pp*** | [-3.19, -1.18 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -1.39 pp | +14.74 pp | -16.13 pp*** | [-18.14, -14.13 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -3.89 pp | +2.18 pp | -6.07 pp*** | [-8.07, -4.06 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +2.77 pp | +5.42 pp | -2.65 pp* | [-4.66, -0.64 pp] | 0.0098 | 0.0391 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +5.79 pp | +7.57 pp | -1.78 pp | [-3.79, +0.23 pp] | 0.0822 | 0.2465 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **74.98%** [74.05, 75.91%] | `close_friend + poor_record` = **46.26%** [45.10, 47.43%] | `stranger + good_record` = **76.37%** [75.47, 77.27%] | `stranger + poor_record` = **31.52%** [30.52, 32.52%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +14.74 pp*** | [+13.21, +16.28 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -1.39 pp* | [-2.68, -0.09 pp] | 0.0356 |
| `reliability effect | closeness=stranger` | +44.85 pp*** | [+43.50, +46.20 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +28.72 pp*** | [+27.23, +30.20 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **73.73%** [72.84, 74.62%] | `mayor + poor_record` = **39.98%** [38.91, 41.06%] | `citizen + good_record` = **77.62%** [76.68, 78.56%] | `citizen + poor_record` = **37.80%** [36.71, 38.90%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +2.18 pp** | [+0.64, +3.71 pp] | 0.0054 |
| `authority effect | reliability=good_record` | -3.89 pp*** | [-5.18, -2.59 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +39.82 pp*** | [+38.37, +41.26 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +33.75 pp*** | [+32.35, +35.14 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **77.06%** [76.16, 77.96%] | `rich + poor_record` = **41.60%** [40.46, 42.74%] | `poor + good_record` = **74.29%** [73.36, 75.22%] | `poor + poor_record` = **36.18%** [35.15, 37.21%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +5.42 pp*** | [+3.88, +6.95 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +2.77 pp*** | [+1.47, +4.06 pp] | <0.0001 |
| `reliability effect | wealth=poor` | +38.11 pp*** | [+36.72, +39.50 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +35.46 pp*** | [+34.01, +36.91 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **59.75%** [58.71, 60.79%] | `close_friend + citizen` = **61.49%** [60.43, 62.56%] | `stranger + mayor` = **53.96%** [53.04, 54.89%] | `stranger + citizen` = **53.93%** [52.95, 54.91%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +7.57 pp*** | [+6.12, +9.01 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +5.79 pp*** | [+4.39, +7.18 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +0.04 pp | [-1.31, +1.38 pp] | 0.9583 |
| `authority effect | closeness=close_friend` | -1.75 pp* | [-3.23, -0.26 pp] | 0.0216 |


**Outcome: CHECKED_FALSE (%)** (n=29,763, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.20% | 0.26% | -0.07 pp | [-0.19, +0.05 pp] | 0.2828 | 1.0000 |
| main | authority | `mayor - citizen` | 0.18% | 0.28% | -0.09 pp | [-0.22, +0.03 pp] | 0.1299 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.07% | 0.38% | -0.31 pp*** | [-0.43, -0.19 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.26% | 0.20% | +0.05 pp | [-0.07, +0.18 pp] | 0.3845 | 1.0000 |
| main | gender | `woman - man` | 0.22% | 0.24% | -0.02 pp | [-0.15, +0.10 pp] | 0.6893 | 1.0000 |
| main | age | `old - young` | 0.21% | 0.24% | -0.03 pp | [-0.15, +0.09 pp] | 0.6642 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.01 pp | -0.12 pp | +0.11 pp | [-0.14, +0.35 pp] | 0.3921 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.04 pp | -0.15 pp | +0.11 pp | [-0.14, +0.35 pp] | 0.3879 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.01 pp | +0.12 pp | -0.13 pp | [-0.38, +0.11 pp] | 0.2782 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.04 pp | -0.09 pp | +0.05 pp | [-0.19, +0.30 pp] | 0.6633 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.07%** [0.01, 0.13%] | `close_friend + poor_record` = **0.32%** [0.18, 0.47%] | `stranger + good_record` = **0.08%** [0.02, 0.14%] | `stranger + poor_record` = **0.44%** [0.27, 0.62%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.12 pp | [-0.35, +0.11 pp] | 0.3016 |
| `closeness effect | reliability=good_record` | -0.01 pp | [-0.10, +0.07 pp] | 0.7596 |
| `reliability effect | closeness=stranger` | -0.36 pp*** | [-0.55, -0.17 pp] | 0.0002 |
| `reliability effect | closeness=close_friend` | -0.26 pp** | [-0.41, -0.10 pp] | 0.0011 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.05%** [0.00, 0.11%] | `mayor + poor_record` = **0.31%** [0.17, 0.45%] | `citizen + good_record` = **0.09%** [0.02, 0.16%] | `citizen + poor_record` = **0.46%** [0.28, 0.64%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.15 pp | [-0.37, +0.08 pp] | 0.2031 |
| `authority effect | reliability=good_record` | -0.04 pp | [-0.13, +0.05 pp] | 0.3621 |
| `reliability effect | authority=citizen` | -0.36 pp*** | [-0.55, -0.17 pp] | 0.0002 |
| `reliability effect | authority=mayor` | -0.26 pp*** | [-0.40, -0.11 pp] | 0.0008 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.07%** [0.01, 0.13%] | `rich + poor_record` = **0.44%** [0.27, 0.62%] | `poor + good_record` = **0.08%** [0.02, 0.14%] | `poor + poor_record` = **0.32%** [0.18, 0.46%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.12 pp | [-0.11, +0.35 pp] | 0.2957 |
| `wealth effect | reliability=good_record` | -0.01 pp | [-0.10, +0.07 pp] | 0.7636 |
| `reliability effect | wealth=poor` | -0.24 pp** | [-0.40, -0.09 pp] | 0.0023 |
| `reliability effect | wealth=rich` | -0.38 pp*** | [-0.56, -0.19 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.16%** [0.06, 0.26%] | `close_friend + citizen` = **0.23%** [0.11, 0.35%] | `stranger + mayor` = **0.20%** [0.09, 0.31%] | `stranger + citizen` = **0.32%** [0.17, 0.47%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.09 pp | [-0.29, +0.10 pp] | 0.3388 |
| `closeness effect | authority=mayor` | -0.04 pp | [-0.19, +0.11 pp] | 0.6030 |
| `authority effect | closeness=stranger` | -0.12 pp | [-0.31, +0.07 pp] | 0.2081 |
| `authority effect | closeness=close_friend` | -0.07 pp | [-0.22, +0.09 pp] | 0.3935 |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,922, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.6303 | 0.5158 | +0.1144*** | [+0.1037, +0.1252] | <0.0001 | <0.0001 | +0.1145 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.5706 | 0.5755 | -0.0049 | [-0.0157, +0.0059] | 0.3714 | 0.7428 | -0.0049 (p=0.3722) |
| main | reliability | `good_record - poor_record` | 0.8732 | 0.2729 | +0.6002*** | [+0.5894, +0.6110] | <0.0001 | <0.0001 | +0.6002 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.5933 | 0.5528 | +0.0406*** | [+0.0298, +0.0513] | <0.0001 | <0.0001 | +0.0406 (p=<0.0001) |
| main | gender | `woman - man` | 0.5751 | 0.5710 | +0.0041 | [-0.0066, +0.0149] | 0.4525 | 0.7428 | +0.0041 (p=0.4539) |
| main | age | `old - young` | 0.5628 | 0.5833 | -0.0206*** | [-0.0313, -0.0098] | 0.0002 | 0.0009 | -0.0206 (p=0.0002) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0245 | +0.2044 | -0.1799*** | [-0.2015, -0.1584] | <0.0001 | <0.0001 | -0.1799 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0231 | +0.0133 | -0.0364** | [-0.0579, -0.0148] | 0.0009 | 0.0038 | -0.0364 (p=0.0010) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0188 | +0.0623 | -0.0435*** | [-0.0651, -0.0220] | <0.0001 | 0.0005 | -0.0436 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.1045 | +0.1244 | -0.0199 | [-0.0415, +0.0017] | 0.0705 | 0.2115 | -0.0199 (p=0.0711) |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.8854** [0.8776, 0.8932] | `close_friend + poor_record` = **0.3751** [0.3603, 0.3900] | `stranger + good_record` = **0.8609** [0.8526, 0.8692] | `stranger + poor_record` = **0.1707** [0.1601, 0.1814]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.2044*** | [+0.1861, +0.2227] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.0245*** | [+0.0131, +0.0359] | <0.0001 |
| `reliability effect | closeness=stranger` | +0.6902*** | [+0.6767, +0.7037] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.5103*** | [+0.4935, +0.5271] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.8616** [0.8533, 0.8699] | `mayor + poor_record` = **0.2796** [0.2667, 0.2924] | `citizen + good_record` = **0.8847** [0.8768, 0.8926] | `citizen + poor_record` = **0.2663** [0.2533, 0.2793]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.0133 | [-0.0050, +0.0316] | 0.1553 |
| `authority effect | reliability=good_record` | -0.0231*** | [-0.0345, -0.0117] | <0.0001 |
| `reliability effect | authority=citizen` | +0.6184*** | [+0.6032, +0.6336] | <0.0001 |
| `reliability effect | authority=mayor` | +0.5820*** | [+0.5668, +0.5973] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.8825** [0.8745, 0.8906] | `rich + poor_record` = **0.3041** [0.2902, 0.3179] | `poor + good_record` = **0.8638** [0.8557, 0.8718] | `poor + poor_record` = **0.2418** [0.2298, 0.2537]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.0623*** | [+0.0440, +0.0806] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.0188** | [+0.0074, +0.0302] | 0.0013 |
| `reliability effect | wealth=poor` | +0.6220*** | [+0.6076, +0.6364] | <0.0001 |
| `reliability effect | wealth=rich` | +0.5785*** | [+0.5624, +0.5945] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.6228** [0.6110, 0.6346] | `close_friend + citizen` = **0.6377** [0.6257, 0.6497] | `stranger + mayor` = **0.5183** [0.5086, 0.5281] | `stranger + citizen` = **0.5133** [0.5039, 0.5227]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.1244*** | [+0.1092, +0.1396] | <0.0001 |
| `closeness effect | authority=mayor` | +0.1045*** | [+0.0892, +0.1198] | <0.0001 |
| `authority effect | closeness=stranger` | +0.0050 | [-0.0085, +0.0186] | 0.4650 |
| `authority effect | closeness=close_friend` | -0.0149 | [-0.0317, +0.0019] | 0.0829 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.6300 | 0.5157 | +0.1143*** | [+0.1035, +0.1251] | <0.0001 | <0.0001 | +0.1143 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.5702 | 0.5754 | -0.0052 | [-0.0160, +0.0056] | 0.3414 | 0.6829 | -0.0052 (p=0.3427) |
| main | reliability | `good_record - poor_record` | 0.8728 | 0.2728 | +0.6000*** | [+0.5892, +0.6108] | <0.0001 | <0.0001 | +0.6000 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.5930 | 0.5526 | +0.0404*** | [+0.0296, +0.0512] | <0.0001 | <0.0001 | +0.0404 (p=<0.0001) |
| main | gender | `woman - man` | 0.5749 | 0.5707 | +0.0042 | [-0.0066, +0.0150] | 0.4495 | 0.6829 | +0.0042 (p=0.4511) |
| main | age | `old - young` | 0.5626 | 0.5830 | -0.0204** | [-0.0312, -0.0096] | 0.0002 | 0.0011 | -0.0204 (p=0.0002) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0242 | +0.2044 | -0.1801*** | [-0.2017, -0.1585] | <0.0001 | <0.0001 | -0.1801 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0238 | +0.0133 | -0.0371** | [-0.0587, -0.0155] | 0.0008 | 0.0030 | -0.0371 (p=0.0008) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0185 | +0.0622 | -0.0436*** | [-0.0652, -0.0220] | <0.0001 | 0.0005 | -0.0436 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.1043 | +0.1243 | -0.0200 | [-0.0416, +0.0016] | 0.0700 | 0.2099 | -0.0200 (p=0.0706) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.6302 | 0.5158 | +0.1144*** | [+0.1036, +0.1252] | <0.0001 | <0.0001 | +0.1144 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.5705 | 0.5755 | -0.0050 | [-0.0158, +0.0057] | 0.3596 | 0.7192 | -0.0050 (p=0.3609) |
| main | reliability | `good_record - poor_record` | 0.8730 | 0.2730 | +0.6000*** | [+0.5893, +0.6108] | <0.0001 | <0.0001 | +0.6000 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.5933 | 0.5527 | +0.0406*** | [+0.0298, +0.0513] | <0.0001 | <0.0001 | +0.0406 (p=<0.0001) |
| main | gender | `woman - man` | 0.5751 | 0.5709 | +0.0042 | [-0.0065, +0.0150] | 0.4414 | 0.7192 | +0.0042 (p=0.4429) |
| main | age | `old - young` | 0.5627 | 0.5833 | -0.0206*** | [-0.0313, -0.0098] | 0.0002 | 0.0009 | -0.0206 (p=0.0002) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0244 | +0.2044 | -0.1800*** | [-0.2015, -0.1584] | <0.0001 | <0.0001 | -0.1800 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0234 | +0.0133 | -0.0367** | [-0.0583, -0.0151] | 0.0008 | 0.0034 | -0.0367 (p=0.0009) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0187 | +0.0624 | -0.0437*** | [-0.0653, -0.0222] | <0.0001 | 0.0004 | -0.0438 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.1043 | +0.1244 | -0.0201 | [-0.0417, +0.0015] | 0.0677 | 0.2032 | -0.0201 (p=0.0683) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 54.18% | 42.76% | +11.42 pp*** | [+10.08, +12.76 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 47.18% | 49.76% | -2.58 pp*** | [-3.91, -1.24 pp] | 0.0002 | 0.0008 |
| main | reliability | `good_record - poor_record` | 76.35% | 20.59% | +55.76 pp*** | [+54.42, +57.09 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 51.16% | 45.78% | +5.38 pp*** | [+4.04, +6.72 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 48.77% | 48.17% | +0.60 pp | [-0.74, +1.94 pp] | 0.3786 | 0.5303 |
| main | age | `old - young` | 47.57% | 49.37% | -1.80 pp* | [-3.14, -0.47 pp] | 0.0082 | 0.0329 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +4.25 pp | +18.59 pp | -14.34 pp*** | [-17.02, -11.67 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -5.37 pp | +0.21 pp | -5.58 pp*** | [-8.26, -2.91 pp] | <0.0001 | 0.0003 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +4.46 pp | +6.30 pp | -1.84 pp | [-4.52, +0.83 pp] | 0.1768 | 0.5303 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +10.50 pp | +12.34 pp | -1.84 pp | [-4.52, +0.83 pp] | 0.1768 | 0.5303 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **78.47%** [77.16, 79.78%] | `close_friend + poor_record` = **29.89%** [28.35, 31.42%] | `stranger + good_record` = **74.23%** [72.80, 75.65%] | `stranger + poor_record` = **11.30%** [10.28, 12.32%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +18.59 pp*** | [+16.75, +20.43 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +4.25 pp*** | [+2.31, +6.19 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | +62.93 pp*** | [+61.17, +64.68 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +48.58 pp*** | [+46.57, +50.60 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **73.66%** [72.26, 75.07%] | `mayor + poor_record` = **20.70%** [19.39, 22.01%] | `citizen + good_record` = **79.03%** [77.70, 80.37%] | `citizen + poor_record` = **20.49%** [19.19, 21.78%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.21 pp | [-1.63, +2.06 pp] | 0.8201 |
| `authority effect | reliability=good_record` | -5.37 pp*** | [-7.31, -3.43 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +58.55 pp*** | [+56.69, +60.41 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +52.96 pp*** | [+51.04, +54.89 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **78.58%** [77.22, 79.94%] | `rich + poor_record` = **23.74%** [22.33, 25.16%] | `poor + good_record` = **74.12%** [72.74, 75.50%] | `poor + poor_record` = **17.44%** [16.26, 18.62%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +6.30 pp*** | [+4.46, +8.14 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +4.46 pp*** | [+2.52, +6.40 pp] | <0.0001 |
| `reliability effect | wealth=poor` | +56.68 pp*** | [+54.86, +58.50 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +54.83 pp*** | [+52.87, +56.80 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **52.43%** [51.01, 53.85%] | `close_friend + citizen` = **55.93%** [54.50, 57.36%] | `stranger + mayor` = **41.93%** [40.64, 43.23%] | `stranger + citizen` = **43.59%** [42.41, 44.77%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +12.34 pp*** | [+10.48, +14.20 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +10.50 pp*** | [+8.58, +12.42 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -1.66 pp | [-3.41, +0.10 pp] | 0.0644 |
| `authority effect | closeness=close_friend` | -3.50 pp*** | [-5.52, -1.48 pp] | 0.0007 |


**Outcome: NOT_MENTIONED (%)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.04% | 0.03% | +0.01 pp | [-0.05, +0.07 pp] | 0.6525 | 1.0000 |
| main | authority | `mayor - citizen` | 0.05% | 0.01% | +0.04 pp | [-0.02, +0.10 pp] | 0.1781 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.04% | 0.03% | +0.01 pp | [-0.05, +0.07 pp] | 0.6518 | 1.0000 |
| main | wealth | `rich - poor` | 0.05% | 0.01% | +0.04 pp | [-0.02, +0.10 pp] | 0.1792 | 1.0000 |
| main | gender | `woman - man` | 0.04% | 0.03% | +0.01 pp | [-0.05, +0.07 pp] | 0.6458 | 1.0000 |
| main | age | `old - young` | 0.01% | 0.05% | -0.04 pp | [-0.10, +0.02 pp] | 0.1784 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.03 pp | +0.00 pp | +0.03 pp | [-0.09, +0.14 pp] | 0.6547 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.08 pp | -0.00 pp | +0.08 pp | [-0.04, +0.20 pp] | 0.1778 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.03 pp | +0.05 pp | -0.03 pp | [-0.14, +0.09 pp] | 0.6536 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.00 pp | +0.03 pp | -0.03 pp | [-0.14, +0.09 pp] | 0.6547 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.05%** [-0.02, 0.13%] | `close_friend + poor_record` = **0.03%** [-0.03, 0.08%] | `stranger + good_record` = **0.03%** [-0.03, 0.08%] | `stranger + poor_record` = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.00 pp | [-0.07, +0.07 pp] | 0.9981 |
| `closeness effect | reliability=good_record` | +0.03 pp | [-0.06, +0.12 pp] | 0.5627 |
| `reliability effect | closeness=stranger` | +0.00 pp | [-0.07, +0.07 pp] | 0.9974 |
| `reliability effect | closeness=close_friend` | +0.03 pp | [-0.06, +0.12 pp] | 0.5621 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.08%** [-0.01, 0.17%] | `mayor + poor_record` = **0.03%** [-0.03, 0.08%] | `citizen + good_record` = **-0.00%** [-0.00, 0.00%] | `citizen + poor_record` = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.00 pp | [-0.07, +0.07 pp] | 0.9995 |
| `authority effect | reliability=good_record` | +0.08 pp | [-0.01, +0.17 pp] | 0.0824 |
| `reliability effect | authority=citizen` | -0.03 pp | [-0.08, +0.03 pp] | 0.3166 |
| `reliability effect | authority=mayor` | +0.05 pp | [-0.05, +0.16 pp] | 0.3145 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.05%** [-0.02, 0.13%] | `rich + poor_record` = **0.05%** [-0.02, 0.13%] | `poor + good_record` = **0.03%** [-0.03, 0.08%] | `poor + poor_record` = **-0.00%** [-0.00, 0.00%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.05 pp | [-0.02, +0.13 pp] | 0.1564 |
| `wealth effect | reliability=good_record` | +0.03 pp | [-0.06, +0.12 pp] | 0.5639 |
| `reliability effect | wealth=poor` | +0.03 pp | [-0.03, +0.08 pp] | 0.3156 |
| `reliability effect | wealth=rich` | +0.00 pp | [-0.10, +0.10 pp] | 0.9989 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.05%** [-0.02, 0.13%] | `close_friend + citizen` = **0.03%** [-0.03, 0.08%] | `stranger + mayor` = **0.05%** [-0.02, 0.13%] | `stranger + citizen` = **-0.00%** [-0.00, 0.00%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.03 pp | [-0.03, +0.08 pp] | 0.3164 |
| `closeness effect | authority=mayor` | +0.00 pp | [-0.10, +0.10 pp] | 0.9987 |
| `authority effect | closeness=stranger` | +0.05 pp | [-0.02, +0.13 pp] | 0.1563 |
| `authority effect | closeness=close_friend` | +0.03 pp | [-0.06, +0.12 pp] | 0.5614 |


**Outcome: FACT (%)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 2.59% | 1.42% | +1.17 pp*** | [+0.71, +1.62 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 1.99% | 2.02% | -0.04 pp | [-0.49, +0.42 pp] | 0.8735 | 1.0000 |
| main | reliability | `good_record - poor_record` | 3.33% | 0.68% | +2.64 pp*** | [+2.19, +3.10 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 1.84% | 2.17% | -0.33 pp | [-0.79, +0.12 pp] | 0.1505 | 0.9032 |
| main | gender | `woman - man` | 1.99% | 2.02% | -0.03 pp | [-0.49, +0.42 pp] | 0.8844 | 1.0000 |
| main | age | `old - young` | 2.14% | 1.86% | +0.28 pp | [-0.18, +0.74 pp] | 0.2281 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.39 pp | +0.94 pp | +0.46 pp | [-0.46, +1.37 pp] | 0.3271 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.06 pp | -0.13 pp | +0.19 pp | [-0.72, +1.10 pp] | 0.6818 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.86 pp | +0.19 pp | -1.04 pp | [-1.96, -0.13 pp] | 0.0251 | 0.2004 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +1.56 pp | +0.77 pp | +0.79 pp | [-0.13, +1.70 pp] | 0.0917 | 0.6422 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **4.02%** [3.38, 4.67%] | `close_friend + poor_record` = **1.15%** [0.82, 1.49%] | `stranger + good_record` = **2.63%** [2.10, 3.16%] | `stranger + poor_record` = **0.21%** [0.07, 0.36%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.94 pp*** | [+0.57, +1.30 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +1.39 pp** | [+0.56, +2.23 pp] | 0.0011 |
| `reliability effect | closeness=stranger` | +2.41 pp*** | [+1.86, +2.97 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +2.87 pp*** | [+2.14, +3.60 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **3.35%** [2.75, 3.96%] | `mayor + poor_record` = **0.62%** [0.37, 0.86%] | `citizen + good_record` = **3.30%** [2.72, 3.87%] | `citizen + poor_record` = **0.75%** [0.48, 1.02%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.13 pp | [-0.50, +0.23 pp] | 0.4755 |
| `authority effect | reliability=good_record` | +0.06 pp | [-0.78, +0.90 pp] | 0.8913 |
| `reliability effect | authority=citizen` | +2.55 pp*** | [+1.91, +3.18 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +2.74 pp*** | [+2.08, +3.39 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **2.90%** [2.35, 3.44%] | `rich + poor_record` = **0.78%** [0.50, 1.05%] | `poor + good_record` = **3.75%** [3.12, 4.39%] | `poor + poor_record` = **0.59%** [0.35, 0.83%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.19 pp | [-0.18, +0.55 pp] | 0.3142 |
| `wealth effect | reliability=good_record` | -0.86 pp* | [-1.69, -0.02 pp] | 0.0449 |
| `reliability effect | wealth=poor` | +3.16 pp*** | [+2.49, +3.84 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +2.12 pp*** | [+1.51, +2.73 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **2.77%** [2.22, 3.31%] | `close_friend + citizen` = **2.41%** [1.93, 2.89%] | `stranger + mayor` = **1.21%** [0.84, 1.57%] | `stranger + citizen` = **1.64%** [1.23, 2.05%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.77 pp* | [+0.14, +1.41 pp] | 0.0170 |
| `closeness effect | authority=mayor` | +1.56 pp*** | [+0.90, +2.21 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -0.43 pp | [-0.98, +0.12 pp] | 0.1269 |
| `authority effect | closeness=close_friend` | +0.36 pp | [-0.37, +1.08 pp] | 0.3380 |


**Outcome: UNCERTAIN (%)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 16.29% | 16.28% | +0.01 pp | [-1.18, +1.20 pp] | 0.9881 | 1.0000 |
| main | authority | `mayor - citizen` | 17.76% | 14.80% | +2.96 pp*** | [+1.77, +4.16 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 18.76% | 13.80% | +4.96 pp*** | [+3.76, +6.15 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 15.08% | 17.49% | -2.41 pp*** | [-3.60, -1.22 pp] | <0.0001 | 0.0005 |
| main | gender | `woman - man` | 16.20% | 16.37% | -0.17 pp | [-1.36, +1.02 pp] | 0.7822 | 1.0000 |
| main | age | `old - young` | 16.40% | 16.17% | +0.23 pp | [-0.96, +1.42 pp] | 0.7061 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -3.94 pp | +3.96 pp | -7.90 pp*** | [-10.28, -5.51 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +3.64 pp | +2.29 pp | +1.34 pp | [-1.04, +3.73 pp] | 0.2696 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -4.63 pp | -0.20 pp | -4.43 pp** | [-6.81, -2.05 pp] | 0.0003 | 0.0016 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.26 pp | +0.28 pp | -0.53 pp | [-2.92, +1.85 pp] | 0.6607 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **16.79%** [15.56, 18.02%] | `close_friend + poor_record` = **15.78%** [14.64, 16.93%] | `stranger + good_record` = **20.73%** [19.41, 22.06%] | `stranger + poor_record` = **11.82%** [10.77, 12.88%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +3.96 pp*** | [+2.40, +5.51 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -3.94 pp*** | [-5.75, -2.13 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | +8.91 pp*** | [+7.21, +10.60 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +1.01 pp | [-0.67, +2.69 pp] | 0.2401 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **20.58%** [19.25, 21.90%] | `mayor + poor_record` = **14.95%** [13.80, 16.10%] | `citizen + good_record` = **16.94%** [15.71, 18.17%] | `citizen + poor_record` = **12.66%** [11.61, 13.70%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +2.29 pp** | [+0.74, +3.85 pp] | 0.0039 |
| `authority effect | reliability=good_record` | +3.64 pp*** | [+1.83, +5.44 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +4.28 pp*** | [+2.67, +5.90 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +5.63 pp*** | [+3.87, +7.38 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **16.45%** [15.21, 17.69%] | `rich + poor_record` = **13.71%** [12.61, 14.80%] | `poor + good_record` = **21.07%** [19.76, 22.39%] | `poor + poor_record` = **13.90%** [12.80, 15.01%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.20 pp | [-1.75, +1.36 pp] | 0.8044 |
| `wealth effect | reliability=good_record` | -4.63 pp*** | [-6.43, -2.82 pp] | <0.0001 |
| `reliability effect | wealth=poor` | +7.17 pp*** | [+5.45, +8.89 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +2.74 pp** | [+1.09, +4.40 pp] | 0.0012 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **17.64%** [16.42, 18.85%] | `close_friend + citizen` = **14.94%** [13.78, 16.10%] | `stranger + mayor` = **17.89%** [16.63, 19.16%] | `stranger + citizen` = **14.66%** [13.54, 15.79%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.28 pp | [-1.34, +1.89 pp] | 0.7372 |
| `closeness effect | authority=mayor` | -0.26 pp | [-2.01, +1.50 pp] | 0.7735 |
| `authority effect | closeness=stranger` | +3.23 pp*** | [+1.54, +4.92 pp] | 0.0002 |
| `authority effect | closeness=close_friend` | +2.70 pp** | [+1.02, +4.38 pp] | 0.0016 |


**Outcome: SKEPTICAL (%)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 28.59% | 39.96% | -11.37 pp*** | [-12.51, -10.23 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 33.83% | 34.72% | -0.89 pp | [-2.03, +0.25 pp] | 0.1253 | 0.2507 |
| main | reliability | `good_record - poor_record` | 3.22% | 65.33% | -62.11 pp*** | [-63.25, -60.97 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 32.81% | 35.74% | -2.92 pp*** | [-4.06, -1.78 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 34.11% | 34.44% | -0.32 pp | [-1.46, +0.82 pp] | 0.5796 | 0.5796 |
| main | age | `old - young` | 35.26% | 33.30% | +1.96 pp** | [+0.82, +3.10 pp] | 0.0008 | 0.0038 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.48 pp | -22.26 pp | +21.77 pp*** | [+19.49, +24.05 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.48 pp | -2.26 pp | +2.75 pp | [+0.47, +5.02 pp] | 0.0183 | 0.0730 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.38 pp | -6.22 pp | +6.60 pp*** | [+4.32, +8.88 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -10.30 pp | -12.43 pp | +2.13 pp | [-0.15, +4.41 pp] | 0.0672 | 0.2016 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **2.98%** [2.42, 3.54%] | `close_friend + poor_record` = **54.21%** [52.55, 55.86%] | `stranger + good_record` = **3.46%** [2.89, 4.03%] | `stranger + poor_record` = **76.46%** [75.11, 77.81%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -22.26 pp*** | [-24.39, -20.12 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.48 pp | [-1.28, +0.32 pp] | 0.2383 |
| `reliability effect | closeness=stranger` | -73.00 pp*** | [-74.47, -71.53 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -51.23 pp*** | [-52.97, -49.48 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **3.46%** [2.87, 4.05%] | `mayor + poor_record` = **64.20%** [62.69, 65.71%] | `citizen + good_record` = **2.98%** [2.44, 3.52%] | `citizen + poor_record` = **66.46%** [64.96, 67.97%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -2.26 pp* | [-4.40, -0.13 pp] | 0.0377 |
| `authority effect | reliability=good_record` | +0.48 pp | [-0.32, +1.28 pp] | 0.2383 |
| `reliability effect | authority=citizen` | -63.49 pp*** | [-65.09, -61.89 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -60.74 pp*** | [-62.37, -59.12 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **3.41%** [2.82, 3.99%] | `rich + poor_record` = **62.22%** [60.65, 63.79%] | `poor + good_record` = **3.03%** [2.49, 3.57%] | `poor + poor_record` = **68.45%** [66.99, 69.90%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -6.22 pp*** | [-8.36, -4.09 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.38 pp | [-0.42, +1.18 pp] | 0.3542 |
| `reliability effect | wealth=poor` | -65.42 pp*** | [-66.97, -63.87 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -58.81 pp*** | [-60.48, -57.14 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **28.68%** [27.44, 29.92%] | `close_friend + citizen` = **28.50%** [27.28, 29.73%] | `stranger + mayor` = **38.98%** [37.93, 40.03%] | `stranger + citizen` = **40.94%** [39.91, 41.96%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -12.43 pp*** | [-14.03, -10.83 pp] | <0.0001 |
| `closeness effect | authority=mayor` | -10.30 pp*** | [-11.93, -8.68 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -1.96 pp** | [-3.42, -0.49 pp] | 0.0090 |
| `authority effect | closeness=close_friend` | +0.17 pp | [-1.57, +1.92 pp] | 0.8452 |


**Outcome: CHECKED_TRUE (%)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 52.27% | 42.01% | +10.26 pp*** | [+8.92, +11.60 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 46.15% | 48.12% | -1.97 pp* | [-3.31, -0.63 pp] | 0.0040 | 0.0159 |
| main | reliability | `good_record - poor_record` | 74.57% | 19.70% | +54.88 pp*** | [+53.54, +56.22 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 49.92% | 44.35% | +5.58 pp*** | [+4.24, +6.92 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 47.40% | 46.87% | +0.53 pp | [-0.81, +1.87 pp] | 0.4344 | 0.8399 |
| main | age | `old - young` | 45.92% | 48.35% | -2.43 pp** | [-3.77, -1.09 pp] | 0.0004 | 0.0023 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +3.00 pp | +17.52 pp | -14.52 pp*** | [-17.20, -11.84 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -4.26 pp | +0.32 pp | -4.57 pp** | [-7.25, -1.89 pp] | 0.0008 | 0.0041 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +5.02 pp | +6.13 pp | -1.10 pp | [-3.78, +1.58 pp] | 0.4199 | 0.8399 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +9.00 pp | +11.52 pp | -2.52 pp | [-5.20, +0.16 pp] | 0.0658 | 0.1975 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **76.07%** [74.71, 77.44%] | `close_friend + poor_record` = **28.46%** [26.95, 29.97%] | `stranger + good_record` = **73.07%** [71.64, 74.50%] | `stranger + poor_record` = **10.94%** [9.94, 11.94%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +17.52 pp*** | [+15.71, +19.33 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +3.00 pp** | [+1.02, +4.98 pp] | 0.0029 |
| `reliability effect | closeness=stranger` | +62.14 pp*** | [+60.39, +63.88 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +47.62 pp*** | [+45.58, +49.65 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **72.45%** [71.02, 73.87%] | `mayor + poor_record` = **19.86%** [18.58, 21.13%] | `citizen + good_record` = **76.70%** [75.33, 78.07%] | `citizen + poor_record` = **19.54%** [18.25, 20.83%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.32 pp | [-1.49, +2.13 pp] | 0.7307 |
| `authority effect | reliability=good_record` | -4.26 pp*** | [-6.23, -2.28 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +57.16 pp*** | [+55.28, +59.04 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +52.59 pp*** | [+50.68, +54.50 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **77.09%** [75.71, 78.47%] | `rich + poor_record` = **22.76%** [21.37, 24.15%] | `poor + good_record` = **72.06%** [70.65, 73.48%] | `poor + poor_record` = **16.63%** [15.48, 17.79%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +6.13 pp*** | [+4.32, +7.94 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +5.02 pp*** | [+3.05, +7.00 pp] | <0.0001 |
| `reliability effect | wealth=poor` | +55.43 pp*** | [+53.60, +57.26 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +54.32 pp*** | [+52.36, +56.28 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **50.65%** [49.22, 52.08%] | `close_friend + citizen` = **53.88%** [52.43, 55.33%] | `stranger + mayor` = **41.65%** [40.38, 42.92%] | `stranger + citizen` = **42.36%** [41.16, 43.56%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +11.52 pp*** | [+9.64, +13.40 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +9.00 pp*** | [+7.09, +10.91 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -0.71 pp | [-2.46, +1.03 pp] | 0.4245 |
| `authority effect | closeness=close_friend` | -3.23 pp** | [-5.26, -1.19 pp] | 0.0019 |


**Outcome: CHECKED_FALSE (%)** (n=14,927, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.23% | 0.31% | -0.08 pp | [-0.24, +0.08 pp] | 0.3380 | 1.0000 |
| main | authority | `mayor - citizen` | 0.21% | 0.32% | -0.11 pp | [-0.27, +0.06 pp] | 0.2010 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.08% | 0.46% | -0.37 pp*** | [-0.54, -0.21 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.29% | 0.24% | +0.05 pp | [-0.11, +0.22 pp] | 0.5217 | 1.0000 |
| main | gender | `woman - man` | 0.26% | 0.28% | -0.02 pp | [-0.19, +0.14 pp] | 0.7718 | 1.0000 |
| main | age | `old - young` | 0.27% | 0.27% | -0.00 pp | [-0.16, +0.16 pp] | 0.9983 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.00 pp | -0.16 pp | +0.16 pp | [-0.17, +0.49 pp] | 0.3389 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.00 pp | -0.21 pp | +0.21 pp | [-0.11, +0.54 pp] | 0.2005 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.05 pp | +0.05 pp | +0.00 pp | [-0.33, +0.33 pp] | 0.9992 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.00 pp | -0.16 pp | +0.16 pp | [-0.17, +0.49 pp] | 0.3356 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.08%** [-0.01, 0.17%] | `close_friend + poor_record` = **0.38%** [0.18, 0.57%] | `stranger + good_record` = **0.08%** [-0.01, 0.17%] | `stranger + poor_record` = **0.54%** [0.30, 0.77%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.16 pp | [-0.46, +0.14 pp] | 0.2982 |
| `closeness effect | reliability=good_record` | -0.00 pp | [-0.13, +0.13 pp] | 0.9985 |
| `reliability effect | closeness=stranger` | -0.45 pp*** | [-0.70, -0.21 pp] | 0.0003 |
| `reliability effect | closeness=close_friend` | -0.29 pp** | [-0.51, -0.08 pp] | 0.0070 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.08%** [-0.01, 0.17%] | `mayor + poor_record` = **0.35%** [0.16, 0.54%] | `citizen + good_record` = **0.08%** [-0.01, 0.17%] | `citizen + poor_record` = **0.56%** [0.33, 0.80%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.21 pp | [-0.52, +0.09 pp] | 0.1643 |
| `authority effect | reliability=good_record` | +0.00 pp | [-0.13, +0.13 pp] | 0.9983 |
| `reliability effect | authority=citizen` | -0.48 pp*** | [-0.73, -0.23 pp] | 0.0002 |
| `reliability effect | authority=mayor` | -0.27 pp* | [-0.48, -0.06 pp] | 0.0117 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.11%** [0.00, 0.21%] | `rich + poor_record` = **0.48%** [0.26, 0.70%] | `poor + good_record` = **0.05%** [-0.02, 0.13%] | `poor + poor_record` = **0.43%** [0.22, 0.64%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.05 pp | [-0.25, +0.35 pp] | 0.7281 |
| `wealth effect | reliability=good_record` | +0.05 pp | [-0.07, +0.18 pp] | 0.4127 |
| `reliability effect | wealth=poor` | -0.37 pp*** | [-0.59, -0.15 pp] | 0.0008 |
| `reliability effect | wealth=rich` | -0.37 pp** | [-0.62, -0.13 pp] | 0.0025 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.21%** [0.07, 0.36%] | `close_friend + citizen` = **0.24%** [0.09, 0.40%] | `stranger + mayor` = **0.21%** [0.07, 0.36%] | `stranger + citizen` = **0.40%** [0.20, 0.60%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.16 pp | [-0.41, +0.09 pp] | 0.2138 |
| `closeness effect | authority=mayor` | +0.00 pp | [-0.21, +0.21 pp] | 0.9965 |
| `authority effect | closeness=stranger` | -0.19 pp | [-0.44, +0.06 pp] | 0.1386 |
| `authority effect | closeness=close_friend` | -0.03 pp | [-0.24, +0.19 pp] | 0.8096 |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=14,828, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8213 | 0.7554 | +0.0659*** | [+0.0545, +0.0774] | <0.0001 | <0.0001 | +0.0659 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8010 | 0.7757 | +0.0254*** | [+0.0139, +0.0369] | <0.0001 | <0.0001 | +0.0254 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.9305 | 0.6462 | +0.2843*** | [+0.2728, +0.2958] | <0.0001 | <0.0001 | +0.2843 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8049 | 0.7718 | +0.0330*** | [+0.0215, +0.0445] | <0.0001 | <0.0001 | +0.0330 (p=<0.0001) |
| main | gender | `woman - man` | 0.7896 | 0.7871 | +0.0024 | [-0.0091, +0.0139] | 0.6810 | 1.0000 | +0.0024 (p=0.6851) |
| main | age | `old - young` | 0.7781 | 0.7986 | -0.0205** | [-0.0319, -0.0090] | 0.0005 | 0.0014 | -0.0204 (p=0.0006) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0160 | +0.1478 | -0.1638*** | [-0.1868, -0.1408] | <0.0001 | <0.0001 | -0.1638 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0109 | +0.0616 | -0.0725*** | [-0.0955, -0.0495] | <0.0001 | <0.0001 | -0.0725 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0087 | +0.0573 | -0.0487*** | [-0.0716, -0.0257] | <0.0001 | 0.0001 | -0.0487 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0626 | +0.0693 | -0.0067 | [-0.0296, +0.0163] | 0.5683 | 1.0000 | -0.0067 (p=0.5733) |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.9225** [0.9157, 0.9294] | `close_friend + poor_record` = **0.7201** [0.7059, 0.7343] | `stranger + good_record` = **0.9385** [0.9324, 0.9446] | `stranger + poor_record` = **0.5723** [0.5567, 0.5878]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.1478*** | [+0.1268, +0.1689] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.0160*** | [-0.0251, -0.0068] | 0.0007 |
| `reliability effect | closeness=stranger` | +0.3662*** | [+0.3495, +0.3829] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.2024*** | [+0.1867, +0.2182] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.9251** [0.9183, 0.9318] | `mayor + poor_record` = **0.6770** [0.6622, 0.6918] | `citizen + good_record` = **0.9360** [0.9297, 0.9422] | `citizen + poor_record` = **0.6154** [0.6004, 0.6304]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.0616*** | [+0.0406, +0.0827] | <0.0001 |
| `authority effect | reliability=good_record` | -0.0109* | [-0.0201, -0.0017] | 0.0200 |
| `reliability effect | authority=citizen` | +0.3206*** | [+0.3043, +0.3368] | <0.0001 |
| `reliability effect | authority=mayor` | +0.2481*** | [+0.2318, +0.2643] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.9348** [0.9285, 0.9412] | `rich + poor_record` = **0.6749** [0.6600, 0.6897] | `poor + good_record` = **0.9262** [0.9196, 0.9328] | `poor + poor_record` = **0.6175** [0.6026, 0.6324]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.0573*** | [+0.0363, +0.0784] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.0087 | [-0.0005, +0.0178] | 0.0640 |
| `reliability effect | wealth=poor` | +0.3087*** | [+0.2923, +0.3250] | <0.0001 |
| `reliability effect | wealth=rich` | +0.2600*** | [+0.2438, +0.2762] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.8323** [0.8210, 0.8437] | `close_friend + citizen` = **0.8103** [0.7994, 0.8212] | `stranger + mayor` = **0.7697** [0.7581, 0.7814] | `stranger + citizen` = **0.7410** [0.7290, 0.7530]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.0693*** | [+0.0531, +0.0855] | <0.0001 |
| `closeness effect | authority=mayor` | +0.0626*** | [+0.0464, +0.0788] | <0.0001 |
| `authority effect | closeness=stranger` | +0.0287*** | [+0.0120, +0.0454] | 0.0008 |
| `authority effect | closeness=close_friend` | +0.0220** | [+0.0063, +0.0378] | 0.0061 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8211 | 0.7549 | +0.0663*** | [+0.0548, +0.0777] | <0.0001 | <0.0001 | +0.0663 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8008 | 0.7751 | +0.0257*** | [+0.0142, +0.0372] | <0.0001 | <0.0001 | +0.0257 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.9304 | 0.6456 | +0.2848*** | [+0.2733, +0.2963] | <0.0001 | <0.0001 | +0.2848 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8043 | 0.7717 | +0.0325*** | [+0.0211, +0.0440] | <0.0001 | <0.0001 | +0.0325 (p=<0.0001) |
| main | gender | `woman - man` | 0.7892 | 0.7868 | +0.0023 | [-0.0091, +0.0138] | 0.6895 | 1.0000 | +0.0023 (p=0.6895) |
| main | age | `old - young` | 0.7779 | 0.7981 | -0.0202** | [-0.0317, -0.0087] | 0.0005 | 0.0016 | -0.0202 (p=0.0006) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0157 | +0.1482 | -0.1639*** | [-0.1868, -0.1410] | <0.0001 | <0.0001 | -0.1639 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0106 | +0.0621 | -0.0727*** | [-0.0956, -0.0497] | <0.0001 | <0.0001 | -0.0727 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0089 | +0.0561 | -0.0472*** | [-0.0702, -0.0243] | <0.0001 | 0.0002 | -0.0472 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0626 | +0.0700 | -0.0074 | [-0.0303, +0.0155] | 0.5272 | 1.0000 | -0.0074 (p=0.5278) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8213 | 0.7553 | +0.0660*** | [+0.0545, +0.0775] | <0.0001 | <0.0001 | +0.0660 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8010 | 0.7755 | +0.0254*** | [+0.0140, +0.0369] | <0.0001 | <0.0001 | +0.0254 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.9305 | 0.6461 | +0.2844*** | [+0.2729, +0.2959] | <0.0001 | <0.0001 | +0.2844 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8047 | 0.7718 | +0.0329*** | [+0.0215, +0.0444] | <0.0001 | <0.0001 | +0.0329 (p=<0.0001) |
| main | gender | `woman - man` | 0.7894 | 0.7871 | +0.0023 | [-0.0091, +0.0138] | 0.6887 | 1.0000 | +0.0023 (p=0.6887) |
| main | age | `old - young` | 0.7781 | 0.7984 | -0.0203** | [-0.0318, -0.0089] | 0.0005 | 0.0015 | -0.0203 (p=0.0005) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0158 | +0.1478 | -0.1636*** | [-0.1866, -0.1407] | <0.0001 | <0.0001 | -0.1636 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0108 | +0.0617 | -0.0724*** | [-0.0954, -0.0495] | <0.0001 | <0.0001 | -0.0724 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0088 | +0.0571 | -0.0483*** | [-0.0712, -0.0253] | <0.0001 | 0.0001 | -0.0483 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0626 | +0.0694 | -0.0069 | [-0.0298, +0.0161] | 0.5579 | 1.0000 | -0.0069 (p=0.5584) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 70.85% | 64.86% | +5.98 pp*** | [+4.57, +7.40 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 69.95% | 65.76% | +4.19 pp*** | [+2.78, +5.61 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 76.98% | 58.73% | +18.24 pp*** | [+16.83, +19.66 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 67.63% | 68.08% | -0.45 pp | [-1.87, +0.96 pp] | 0.5299 | 0.5299 |
| main | gender | `woman - man` | 68.51% | 67.20% | +1.31 pp | [-0.11, +2.73 pp] | 0.0697 | 0.2788 |
| main | age | `old - young` | 66.75% | 68.96% | -2.22 pp* | [-3.63, -0.80 pp] | 0.0022 | 0.0108 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.82 pp | +10.15 pp | -8.33 pp*** | [-11.17, -5.50 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +2.88 pp | +5.50 pp | -2.62 pp | [-5.45, +0.22 pp] | 0.0702 | 0.2788 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -4.27 pp | +3.37 pp | -7.64 pp*** | [-10.47, -4.81 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +4.97 pp | +7.00 pp | -2.03 pp | [-4.86, +0.80 pp] | 0.1603 | 0.3206 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **77.88%** [76.62, 79.15%] | `close_friend + poor_record` = **63.81%** [62.31, 65.30%] | `stranger + good_record` = **76.07%** [74.76, 77.37%] | `stranger + poor_record` = **53.66%** [52.08, 55.23%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +10.15 pp*** | [+7.98, +12.32 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +1.82 pp | [-0.00, +3.64 pp] | 0.0504 |
| `reliability effect | closeness=stranger` | +22.41 pp*** | [+20.36, +24.46 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +14.08 pp*** | [+12.12, +16.04 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **78.42%** [77.14, 79.70%] | `mayor + poor_record` = **61.49%** [59.95, 63.02%] | `citizen + good_record` = **75.53%** [74.24, 76.82%] | `citizen + poor_record` = **55.98%** [54.45, 57.52%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +5.50 pp*** | [+3.33, +7.67 pp] | <0.0001 |
| `authority effect | reliability=good_record` | +2.88 pp** | [+1.07, +4.70 pp] | 0.0019 |
| `reliability effect | authority=citizen` | +19.55 pp*** | [+17.55, +21.56 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +16.93 pp*** | [+14.93, +18.94 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **74.84%** [73.55, 76.13%] | `rich + poor_record` = **60.42%** [58.89, 61.95%] | `poor + good_record` = **79.11%** [77.83, 80.39%] | `poor + poor_record` = **57.05%** [55.51, 58.59%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +3.37 pp** | [+1.19, +5.54 pp] | 0.0024 |
| `wealth effect | reliability=good_record` | -4.27 pp*** | [-6.09, -2.45 pp] | <0.0001 |
| `reliability effect | wealth=poor` | +22.06 pp*** | [+20.06, +24.07 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +14.42 pp*** | [+12.42, +16.43 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **72.44%** [71.03, 73.84%] | `close_friend + citizen` = **69.26%** [67.89, 70.62%] | `stranger + mayor` = **67.47%** [66.04, 68.89%] | `stranger + citizen` = **62.26%** [60.79, 63.73%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +7.00 pp*** | [+4.99, +9.00 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +4.97 pp*** | [+2.97, +6.97 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +5.21 pp*** | [+3.16, +7.26 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | +3.18 pp** | [+1.22, +5.14 pp] | 0.0015 |


**Outcome: NOT_MENTIONED (%)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.03% | 0.08% | -0.05 pp | [-0.13, +0.02 pp] | 0.1569 | 1.0000 |
| main | authority | `mayor - citizen` | 0.03% | 0.08% | -0.05 pp | [-0.13, +0.02 pp] | 0.1541 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.01% | 0.09% | -0.08 pp | [-0.16, -0.01 pp] | 0.0328 | 0.2928 |
| main | wealth | `rich - poor` | 0.09% | 0.01% | +0.08 pp | [+0.01, +0.16 pp] | 0.0325 | 0.2928 |
| main | gender | `woman - man` | 0.05% | 0.05% | +0.00 pp | [-0.07, +0.08 pp] | 0.9689 | 1.0000 |
| main | age | `old - young` | 0.04% | 0.07% | -0.03 pp | [-0.10, +0.05 pp] | 0.4767 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.03 pp | -0.08 pp | +0.05 pp | [-0.10, +0.20 pp] | 0.4822 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.03 pp | -0.08 pp | +0.05 pp | [-0.09, +0.20 pp] | 0.4747 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.03 pp | +0.19 pp | -0.22 pp* | [-0.36, -0.07 pp] | 0.0044 | 0.0441 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.00 pp | -0.11 pp | +0.11 pp | [-0.04, +0.26 pp] | 0.1546 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **-0.00%** [-0.00, 0.00%] | `close_friend + poor_record` = **0.05%** [-0.02, 0.13%] | `stranger + good_record` = **0.03%** [-0.03, 0.08%] | `stranger + poor_record` = **0.13%** [0.02, 0.25%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.08 pp | [-0.22, +0.06 pp] | 0.2573 |
| `closeness effect | reliability=good_record` | -0.03 pp | [-0.08, +0.03 pp] | 0.3156 |
| `reliability effect | closeness=stranger` | -0.11 pp | [-0.24, +0.02 pp] | 0.1002 |
| `reliability effect | closeness=close_friend` | -0.05 pp | [-0.13, +0.02 pp] | 0.1568 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.00%** [-0.00, 0.00%] | `mayor + poor_record` = **0.05%** [-0.02, 0.13%] | `citizen + good_record` = **0.03%** [-0.03, 0.08%] | `citizen + poor_record` = **0.13%** [0.02, 0.25%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.08 pp | [-0.22, +0.06 pp] | 0.2525 |
| `authority effect | reliability=good_record` | -0.03 pp | [-0.08, +0.03 pp] | 0.3166 |
| `reliability effect | authority=citizen` | -0.11 pp | [-0.24, +0.02 pp] | 0.0992 |
| `reliability effect | authority=mayor` | -0.05 pp | [-0.13, +0.02 pp] | 0.1599 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.00%** [-0.00, 0.00%] | `rich + poor_record` = **0.19%** [0.05, 0.33%] | `poor + good_record` = **0.03%** [-0.03, 0.08%] | `poor + poor_record` = **-0.00%** [-0.01, 0.01%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.19 pp** | [+0.05, +0.33 pp] | 0.0077 |
| `wealth effect | reliability=good_record` | -0.03 pp | [-0.08, +0.03 pp] | 0.3176 |
| `reliability effect | wealth=poor` | +0.03 pp | [-0.03, +0.08 pp] | 0.3141 |
| `reliability effect | wealth=rich` | -0.19 pp** | [-0.33, -0.05 pp] | 0.0077 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.03%** [-0.03, 0.08%] | `close_friend + citizen` = **0.03%** [-0.03, 0.08%] | `stranger + mayor` = **0.03%** [-0.03, 0.08%] | `stranger + citizen` = **0.13%** [0.02, 0.25%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.11 pp | [-0.24, +0.02 pp] | 0.1002 |
| `closeness effect | authority=mayor` | +0.00 pp | [-0.07, +0.08 pp] | 0.9960 |
| `authority effect | closeness=stranger` | -0.11 pp | [-0.24, +0.02 pp] | 0.0991 |
| `authority effect | closeness=close_friend` | -0.00 pp | [-0.08, +0.07 pp] | 0.9942 |


**Outcome: FACT (%)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 9.22% | 6.49% | +2.73 pp*** | [+1.86, +3.61 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 8.68% | 7.02% | +1.66 pp** | [+0.78, +2.53 pp] | 0.0002 | 0.0016 |
| main | reliability | `good_record - poor_record` | 11.41% | 4.30% | +7.11 pp*** | [+6.24, +7.98 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 8.19% | 7.51% | +0.68 pp | [-0.19, +1.56 pp] | 0.1270 | 0.8036 |
| main | gender | `woman - man` | 8.01% | 7.70% | +0.30 pp | [-0.57, +1.18 pp] | 0.4952 | 1.0000 |
| main | age | `old - young` | 7.75% | 7.96% | -0.22 pp | [-1.09, +0.66 pp] | 0.6261 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +3.43 pp | +2.03 pp | +1.41 pp | [-0.34, +3.16 pp] | 0.1148 | 0.8036 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.79 pp | +1.53 pp | +0.26 pp | [-1.49, +2.01 pp] | 0.7699 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.50 pp | +0.86 pp | -0.36 pp | [-2.11, +1.38 pp] | 0.6836 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +2.84 pp | +2.62 pp | +0.22 pp | [-1.53, +1.97 pp] | 0.8024 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **13.13%** [12.02, 14.24%] | `close_friend + poor_record` = **5.31%** [4.57, 6.05%] | `stranger + good_record` = **9.69%** [8.73, 10.66%] | `stranger + poor_record` = **3.29%** [2.69, 3.88%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +2.03 pp*** | [+1.08, +2.98 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +3.43 pp*** | [+1.97, +4.90 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | +6.41 pp*** | [+5.28, +7.54 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +7.81 pp*** | [+6.48, +9.15 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **12.30%** [11.26, 13.35%] | `mayor + poor_record` = **5.06%** [4.33, 5.80%] | `citizen + good_record` = **10.51%** [9.49, 11.54%] | `citizen + poor_record` = **3.53%** [2.94, 4.13%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +1.53 pp** | [+0.58, +2.48 pp] | 0.0016 |
| `authority effect | reliability=good_record` | +1.79 pp* | [+0.32, +3.26 pp] | 0.0169 |
| `reliability effect | authority=citizen` | +6.98 pp*** | [+5.79, +8.17 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +7.24 pp*** | [+5.96, +8.52 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **11.66%** [10.61, 12.71%] | `rich + poor_record` = **4.73%** [4.06, 5.40%] | `poor + good_record` = **11.16%** [10.14, 12.18%] | `poor + poor_record` = **3.87%** [3.20, 4.54%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.86 pp | [-0.09, +1.81 pp] | 0.0746 |
| `wealth effect | reliability=good_record` | +0.50 pp | [-0.97, +1.97 pp] | 0.5056 |
| `reliability effect | wealth=poor` | +7.29 pp*** | [+6.07, +8.52 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +6.93 pp*** | [+5.68, +8.18 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **10.11%** [9.12, 11.09%] | `close_friend + citizen` = **8.33%** [7.44, 9.23%] | `stranger + mayor` = **7.26%** [6.44, 8.08%] | `stranger + citizen` = **5.71%** [4.93, 6.49%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +2.62 pp*** | [+1.43, +3.81 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +2.84 pp*** | [+1.56, +4.12 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +1.55 pp** | [+0.42, +2.68 pp] | 0.0073 |
| `authority effect | closeness=close_friend` | +1.77 pp** | [+0.44, +3.11 pp] | 0.0093 |


**Outcome: UNCERTAIN (%)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 7.63% | 6.08% | +1.55 pp** | [+0.74, +2.35 pp] | 0.0002 | 0.0015 |
| main | authority | `mayor - citizen` | 7.47% | 6.24% | +1.23 pp* | [+0.43, +2.04 pp] | 0.0027 | 0.0218 |
| main | reliability | `good_record - poor_record` | 9.70% | 4.01% | +5.69 pp*** | [+4.88, +6.49 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 6.82% | 6.89% | -0.07 pp | [-0.88, +0.73 pp] | 0.8560 | 1.0000 |
| main | gender | `woman - man` | 6.97% | 6.75% | +0.22 pp | [-0.59, +1.03 pp] | 0.5946 | 1.0000 |
| main | age | `old - young` | 6.98% | 6.74% | +0.24 pp | [-0.56, +1.05 pp] | 0.5579 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.58 pp | +1.51 pp | +0.07 pp | [-1.54, +1.68 pp] | 0.9334 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.34 pp | +1.13 pp | +0.21 pp | [-1.40, +1.82 pp] | 0.7963 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.23 pp | +0.08 pp | -0.31 pp | [-1.92, +1.30 pp] | 0.7065 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +1.60 pp | +1.49 pp | +0.12 pp | [-1.50, +1.73 pp] | 0.8876 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **10.49%** [9.50, 11.48%] | `close_friend + poor_record` = **4.77%** [4.09, 5.45%] | `stranger + good_record` = **8.91%** [8.00, 9.82%] | `stranger + poor_record` = **3.26%** [2.68, 3.84%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +1.51 pp*** | [+0.62, +2.40 pp] | 0.0009 |
| `closeness effect | reliability=good_record` | +1.58 pp* | [+0.24, +2.92 pp] | 0.0211 |
| `reliability effect | closeness=stranger` | +5.65 pp*** | [+4.57, +6.73 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +5.72 pp*** | [+4.52, +6.92 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **10.37%** [9.39, 11.35%] | `mayor + poor_record` = **4.58%** [3.92, 5.24%] | `citizen + good_record` = **9.03%** [8.11, 9.95%] | `citizen + poor_record` = **3.45%** [2.85, 4.05%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +1.13 pp* | [+0.24, +2.02 pp] | 0.0132 |
| `authority effect | reliability=good_record` | +1.34 pp | [-0.00, +2.68 pp] | 0.0508 |
| `reliability effect | authority=citizen` | +5.58 pp*** | [+4.48, +6.68 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +5.79 pp*** | [+4.61, +6.97 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **9.59%** [8.62, 10.55%] | `rich + poor_record` = **4.05%** [3.41, 4.70%] | `poor + good_record` = **9.82%** [8.88, 10.75%] | `poor + poor_record` = **3.97%** [3.36, 4.59%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.08 pp | [-0.81, +0.97 pp] | 0.8598 |
| `wealth effect | reliability=good_record` | -0.23 pp | [-1.57, +1.11 pp] | 0.7379 |
| `reliability effect | wealth=poor` | +5.84 pp*** | [+4.73, +6.96 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +5.53 pp*** | [+4.37, +6.69 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **8.28%** [7.39, 9.16%] | `close_friend + citizen` = **6.99%** [6.18, 7.80%] | `stranger + mayor` = **6.67%** [5.89, 7.45%] | `stranger + citizen` = **5.50%** [4.76, 6.24%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +1.49 pp** | [+0.39, +2.59 pp] | 0.0079 |
| `closeness effect | authority=mayor` | +1.60 pp** | [+0.42, +2.78 pp] | 0.0077 |
| `authority effect | closeness=stranger` | +1.17 pp* | [+0.10, +2.25 pp] | 0.0328 |
| `authority effect | closeness=close_friend` | +1.29 pp* | [+0.09, +2.49 pp] | 0.0349 |


**Outcome: SKEPTICAL (%)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 13.88% | 21.18% | -7.29 pp*** | [-8.39, -6.19 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 16.00% | 19.06% | -3.05 pp*** | [-4.15, -1.95 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 2.03% | 33.03% | -31.00 pp*** | [-32.10, -29.90 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 15.85% | 19.21% | -3.35 pp*** | [-4.45, -2.25 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 17.37% | 17.69% | -0.32 pp | [-1.42, +0.78 pp] | 0.5686 | 1.0000 |
| main | age | `old - young` | 18.52% | 16.54% | +1.98 pp** | [+0.88, +3.08 pp] | 0.0004 | 0.0012 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.83 pp | -15.42 pp | +16.25 pp*** | [+14.05, +18.45 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.50 pp | -6.61 pp | +7.11 pp*** | [+4.91, +9.30 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.67 pp | -6.03 pp | +5.36 pp*** | [+3.16, +7.56 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -6.98 pp | -7.61 pp | +0.63 pp | [-1.57, +2.82 pp] | 0.5752 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **2.45%** [1.95, 2.94%] | `close_friend + poor_record` = **25.32%** [23.94, 26.70%] | `stranger + good_record` = **1.61%** [1.19, 2.04%] | `stranger + poor_record` = **40.74%** [39.16, 42.32%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -15.42 pp*** | [-17.52, -13.32 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.83 pp* | [+0.18, +1.48 pp] | 0.0119 |
| `reliability effect | closeness=stranger` | -39.12 pp*** | [-40.76, -37.49 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -22.87 pp*** | [-24.34, -21.41 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **2.28%** [1.80, 2.76%] | `mayor + poor_record` = **29.73%** [28.25, 31.20%] | `citizen + good_record` = **1.78%** [1.34, 2.22%] | `citizen + poor_record` = **36.33%** [34.84, 37.82%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -6.61 pp*** | [-8.71, -4.51 pp] | <0.0001 |
| `authority effect | reliability=good_record` | +0.50 pp | [-0.15, +1.15 pp] | 0.1302 |
| `reliability effect | authority=citizen` | -34.55 pp*** | [-36.11, -33.00 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -27.44 pp*** | [-29.00, -25.89 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **1.70%** [1.27, 2.13%] | `rich + poor_record` = **30.01%** [28.54, 31.48%] | `poor + good_record` = **2.37%** [1.88, 2.85%] | `poor + poor_record` = **36.05%** [34.55, 37.54%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -6.03 pp*** | [-8.13, -3.93 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.67 pp* | [-1.32, -0.02 pp] | 0.0430 |
| `reliability effect | wealth=poor` | -33.68 pp*** | [-35.26, -32.10 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -28.32 pp*** | [-29.85, -26.79 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **12.51%** [11.46, 13.56%] | `close_friend + citizen` = **15.25%** [14.23, 16.28%] | `stranger + mayor` = **19.49%** [18.35, 20.63%] | `stranger + citizen` = **22.86%** [21.69, 24.03%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -7.61 pp*** | [-9.16, -6.05 pp] | <0.0001 |
| `closeness effect | authority=mayor` | -6.98 pp*** | [-8.53, -5.43 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -3.37 pp*** | [-5.00, -1.73 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | -2.74 pp*** | [-4.20, -1.27 pp] | 0.0002 |


**Outcome: CHECKED_TRUE (%)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 69.08% | 65.95% | +3.12 pp*** | [+1.63, +4.61 pp] | <0.0001 | 0.0003 |
| main | authority | `mayor - citizen` | 67.66% | 67.37% | +0.30 pp | [-1.19, +1.79 pp] | 0.6966 | 1.0000 |
| main | reliability | `good_record - poor_record` | 76.78% | 58.25% | +18.53 pp*** | [+17.04, +20.02 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 68.82% | 66.21% | +2.61 pp** | [+1.12, +4.10 pp] | 0.0006 | 0.0036 |
| main | gender | `woman - man` | 67.43% | 67.61% | -0.18 pp | [-1.67, +1.31 pp] | 0.8126 | 1.0000 |
| main | age | `old - young` | 66.55% | 68.48% | -1.92 pp* | [-3.41, -0.43 pp] | 0.0114 | 0.0455 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -5.79 pp | +12.04 pp | -17.83 pp*** | [-20.81, -14.85 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -3.52 pp | +4.11 pp | -7.64 pp*** | [-10.61, -4.66 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.51 pp | +4.71 pp | -4.20 pp* | [-7.18, -1.22 pp] | 0.0057 | 0.0285 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +2.61 pp | +3.63 pp | -1.02 pp | [-4.00, +1.96 pp] | 0.5018 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **73.88%** [72.43, 75.33%] | `close_friend + poor_record` = **64.27%** [62.70, 65.84%] | `stranger + good_record` = **79.68%** [78.36, 80.99%] | `stranger + poor_record` = **52.23%** [50.62, 53.84%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +12.04 pp*** | [+9.79, +14.29 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -5.79 pp*** | [-7.75, -3.84 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | +27.44 pp*** | [+25.36, +29.52 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +9.61 pp*** | [+7.47, +11.74 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **75.02%** [73.64, 76.40%] | `mayor + poor_record` = **60.31%** [58.74, 61.88%] | `citizen + good_record` = **78.54%** [77.15, 79.92%] | `citizen + poor_record` = **56.20%** [54.59, 57.80%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +4.11 pp*** | [+1.87, +6.36 pp] | 0.0003 |
| `authority effect | reliability=good_record` | -3.52 pp*** | [-5.48, -1.57 pp] | 0.0004 |
| `reliability effect | authority=citizen` | +22.34 pp*** | [+20.22, +24.47 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +14.71 pp*** | [+12.62, +16.80 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **77.03%** [75.60, 78.46%] | `rich + poor_record` = **60.61%** [59.00, 62.22%] | `poor + good_record` = **76.52%** [75.19, 77.86%] | `poor + poor_record` = **55.90%** [54.33, 57.47%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +4.71 pp*** | [+2.46, +6.96 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.51 pp | [-1.45, +2.46 pp] | 0.6105 |
| `reliability effect | wealth=poor` | +20.63 pp*** | [+18.57, +22.69 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +16.42 pp*** | [+14.27, +18.58 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **68.97%** [67.46, 70.48%] | `close_friend + citizen` = **69.18%** [67.68, 70.69%] | `stranger + mayor` = **66.36%** [64.91, 67.80%] | `stranger + citizen` = **65.55%** [64.06, 67.05%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +3.63 pp*** | [+1.51, +5.75 pp] | 0.0008 |
| `closeness effect | authority=mayor` | +2.61 pp* | [+0.52, +4.70 pp] | 0.0144 |
| `authority effect | closeness=stranger` | +0.81 pp | [-1.27, +2.89 pp] | 0.4468 |
| `authority effect | closeness=close_friend` | -0.21 pp | [-2.35, +1.92 pp] | 0.8442 |


**Outcome: CHECKED_FALSE (%)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.16% | 0.22% | -0.05 pp | [-0.19, +0.09 pp] | 0.4539 | 1.0000 |
| main | authority | `mayor - citizen` | 0.15% | 0.23% | -0.08 pp | [-0.22, +0.06 pp] | 0.2536 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.07% | 0.31% | -0.24 pp** | [-0.38, -0.10 pp] | 0.0006 | 0.0059 |
| main | wealth | `rich - poor` | 0.22% | 0.16% | +0.05 pp | [-0.08, +0.19 pp] | 0.4429 | 1.0000 |
| main | gender | `woman - man` | 0.18% | 0.20% | -0.03 pp | [-0.16, +0.11 pp] | 0.7207 | 1.0000 |
| main | age | `old - young` | 0.16% | 0.22% | -0.05 pp | [-0.19, +0.08 pp] | 0.4467 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.03 pp | -0.08 pp | +0.05 pp | [-0.22, +0.33 pp] | 0.7121 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.08 pp | -0.08 pp | -0.00 pp | [-0.28, +0.28 pp] | 0.9990 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.08 pp | +0.19 pp | -0.27 pp | [-0.55, +0.01 pp] | 0.0564 | 0.5072 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.08 pp | -0.03 pp | -0.05 pp | [-0.33, +0.22 pp] | 0.7038 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.05%** [-0.02, 0.13%] | `close_friend + poor_record` = **0.27%** [0.10, 0.44%] | `stranger + good_record` = **0.08%** [-0.01, 0.17%] | `stranger + poor_record` = **0.35%** [0.16, 0.54%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.08 pp | [-0.33, +0.17 pp] | 0.5370 |
| `closeness effect | reliability=good_record` | -0.03 pp | [-0.14, +0.09 pp] | 0.6544 |
| `reliability effect | closeness=stranger` | -0.27 pp* | [-0.48, -0.06 pp] | 0.0115 |
| `reliability effect | closeness=close_friend` | -0.22 pp* | [-0.40, -0.03 pp] | 0.0198 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.03%** [-0.03, 0.08%] | `mayor + poor_record` = **0.27%** [0.10, 0.44%] | `citizen + good_record` = **0.11%** [0.00, 0.21%] | `citizen + poor_record` = **0.35%** [0.16, 0.54%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.08 pp | [-0.33, +0.17 pp] | 0.5288 |
| `authority effect | reliability=good_record` | -0.08 pp | [-0.20, +0.04 pp] | 0.1784 |
| `reliability effect | authority=citizen` | -0.24 pp* | [-0.46, -0.03 pp] | 0.0274 |
| `reliability effect | authority=mayor` | -0.24 pp** | [-0.42, -0.07 pp] | 0.0062 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.03%** [-0.03, 0.08%] | `rich + poor_record` = **0.40%** [0.20, 0.61%] | `poor + good_record` = **0.11%** [0.00, 0.21%] | `poor + poor_record` = **0.22%** [0.07, 0.36%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.19 pp | [-0.06, +0.44 pp] | 0.1397 |
| `wealth effect | reliability=good_record` | -0.08 pp | [-0.20, +0.04 pp] | 0.1788 |
| `reliability effect | wealth=poor` | -0.11 pp | [-0.29, +0.07 pp] | 0.2451 |
| `reliability effect | wealth=rich` | -0.38 pp*** | [-0.59, -0.17 pp] | 0.0004 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.11%** [0.00, 0.21%] | `close_friend + citizen` = **0.22%** [0.07, 0.36%] | `stranger + mayor` = **0.19%** [0.05, 0.33%] | `stranger + citizen` = **0.24%** [0.09, 0.40%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.03 pp | [-0.24, +0.19 pp] | 0.8125 |
| `closeness effect | authority=mayor` | -0.08 pp | [-0.25, +0.09 pp] | 0.3685 |
| `authority effect | closeness=stranger` | -0.05 pp | [-0.26, +0.16 pp] | 0.6129 |
| `authority effect | closeness=close_friend` | -0.11 pp | [-0.29, +0.07 pp] | 0.2467 |


### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=29,795, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8834 | 0.8065 | +0.0769*** | [+0.0693, +0.0845] | <0.0001 | <0.0001 | +0.0769 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8437 | 0.8462 | -0.0025 | [-0.0101, +0.0051] | 0.5234 | 0.5234 | -0.0025 (p=0.5237) |
| main | reliability | `good_record - poor_record` | 0.9214 | 0.7684 | +0.1530*** | [+0.1455, +0.1606] | <0.0001 | <0.0001 | +0.1530 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8572 | 0.8326 | +0.0247*** | [+0.0171, +0.0322] | <0.0001 | <0.0001 | +0.0247 (p=<0.0001) |
| main | gender | `woman - man` | 0.8426 | 0.8472 | -0.0047 | [-0.0122, +0.0029] | 0.2281 | 0.5062 | -0.0047 (p=0.2286) |
| main | age | `old - young` | 0.8476 | 0.8423 | +0.0053 | [-0.0023, +0.0129] | 0.1687 | 0.5062 | +0.0053 (p=0.1700) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0065 | +0.1473 | -0.1408*** | [-0.1559, -0.1256] | <0.0001 | <0.0001 | -0.1408 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0098 | +0.0049 | -0.0147 | [-0.0299, +0.0005] | 0.0572 | 0.2862 | -0.0147 (p=0.0578) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0023 | +0.0517 | -0.0540*** | [-0.0691, -0.0388] | <0.0001 | <0.0001 | -0.0540 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0697 | +0.0841 | -0.0143 | [-0.0295, +0.0008] | 0.0642 | 0.2862 | -0.0143 (p=0.0648) |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.9247** [0.9203, 0.9291] | `close_friend + poor_record` = **0.8420** [0.8338, 0.8503] | `stranger + good_record` = **0.9182** [0.9134, 0.9229] | `stranger + poor_record` = **0.6948** [0.6838, 0.7057]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.1473*** | [+0.1336, +0.1610] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.0065* | [+0.0000, +0.0130] | 0.0484 |
| `reliability effect | closeness=stranger` | +0.2234*** | [+0.2115, +0.2354] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.0827*** | [+0.0733, +0.0920] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.9165** [0.9117, 0.9213] | `mayor + poor_record` = **0.7708** [0.7611, 0.7806] | `citizen + good_record` = **0.9263** [0.9220, 0.9307] | `citizen + poor_record` = **0.7660** [0.7563, 0.7756]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.0049 | [-0.0088, +0.0186] | 0.4849 |
| `authority effect | reliability=good_record` | -0.0098** | [-0.0163, -0.0034] | 0.0029 |
| `reliability effect | authority=citizen` | +0.1604*** | [+0.1498, +0.1710] | <0.0001 |
| `reliability effect | authority=mayor` | +0.1457*** | [+0.1348, +0.1565] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.9203** [0.9156, 0.9249] | `rich + poor_record` = **0.7942** [0.7849, 0.8036] | `poor + good_record` = **0.9226** [0.9181, 0.9271] | `poor + poor_record` = **0.7426** [0.7325, 0.7526]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.0517*** | [+0.0379, +0.0654] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.0023 | [-0.0088, +0.0041] | 0.4815 |
| `reliability effect | wealth=poor` | +0.1800*** | [+0.1690, +0.1911] | <0.0001 |
| `reliability effect | wealth=rich` | +0.1260*** | [+0.1156, +0.1365] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.8786** [0.8716, 0.8855] | `close_friend + citizen` = **0.8882** [0.8819, 0.8944] | `stranger + mayor` = **0.8088** [0.8004, 0.8172] | `stranger + citizen` = **0.8041** [0.7956, 0.8127]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.0841*** | [+0.0735, +0.0946] | <0.0001 |
| `closeness effect | authority=mayor` | +0.0697*** | [+0.0589, +0.0806] | <0.0001 |
| `authority effect | closeness=stranger` | +0.0047 | [-0.0073, +0.0166] | 0.4418 |
| `authority effect | closeness=close_friend` | -0.0096* | [-0.0190, -0.0003] | 0.0433 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8797 | 0.8030 | +0.0767*** | [+0.0691, +0.0844] | <0.0001 | <0.0001 | +0.0767 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8413 | 0.8414 | -0.0001 | [-0.0077, +0.0075] | 0.9777 | 0.9777 | -0.0001 (p=0.9780) |
| main | reliability | `good_record - poor_record` | 0.9186 | 0.7640 | +0.1546*** | [+0.1469, +0.1622] | <0.0001 | <0.0001 | +0.1546 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8539 | 0.8287 | +0.0252*** | [+0.0176, +0.0328] | <0.0001 | <0.0001 | +0.0252 (p=<0.0001) |
| main | gender | `woman - man` | 0.8398 | 0.8428 | -0.0030 | [-0.0107, +0.0046] | 0.4381 | 0.8761 | -0.0030 (p=0.4396) |
| main | age | `old - young` | 0.8439 | 0.8387 | +0.0051 | [-0.0025, +0.0128] | 0.1877 | 0.5632 | +0.0051 (p=0.1886) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0053 | +0.1482 | -0.1429*** | [-0.1582, -0.1276] | <0.0001 | <0.0001 | -0.1429 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0073 | +0.0071 | -0.0144 | [-0.0297, +0.0009] | 0.0643 | 0.2571 | -0.0144 (p=0.0649) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0023 | +0.0527 | -0.0550*** | [-0.0703, -0.0397] | <0.0001 | <0.0001 | -0.0550 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0690 | +0.0844 | -0.0154 | [-0.0306, -0.0001] | 0.0489 | 0.2445 | -0.0154 (p=0.0494) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8818 | 0.8053 | +0.0765*** | [+0.0689, +0.0840] | <0.0001 | <0.0001 | +0.0765 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8428 | 0.8443 | -0.0015 | [-0.0091, +0.0060] | 0.6885 | 0.6885 | -0.0015 (p=0.6893) |
| main | reliability | `good_record - poor_record` | 0.9201 | 0.7669 | +0.1532*** | [+0.1456, +0.1607] | <0.0001 | <0.0001 | +0.1532 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8559 | 0.8311 | +0.0248*** | [+0.0172, +0.0323] | <0.0001 | <0.0001 | +0.0248 (p=<0.0001) |
| main | gender | `woman - man` | 0.8415 | 0.8455 | -0.0040 | [-0.0116, +0.0036] | 0.3000 | 0.6000 | -0.0040 (p=0.3016) |
| main | age | `old - young` | 0.8462 | 0.8409 | +0.0053 | [-0.0023, +0.0129] | 0.1692 | 0.5075 | +0.0053 (p=0.1700) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0059 | +0.1470 | -0.1411*** | [-0.1562, -0.1260] | <0.0001 | <0.0001 | -0.1411 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0087 | +0.0056 | -0.0142 | [-0.0293, +0.0009] | 0.0651 | 0.3019 | -0.0142 (p=0.0658) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0023 | +0.0518 | -0.0541*** | [-0.0692, -0.0390] | <0.0001 | <0.0001 | -0.0541 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0692 | +0.0837 | -0.0145 | [-0.0296, +0.0006] | 0.0604 | 0.3019 | -0.0145 (p=0.0610) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 60.82% | 55.76% | +5.06 pp*** | [+4.35, +5.77 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 57.99% | 58.59% | -0.60 pp | [-1.31, +0.11 pp] | 0.0980 | 0.2939 |
| main | reliability | `good_record - poor_record` | 60.42% | 56.17% | +4.25 pp*** | [+3.53, +4.96 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 59.38% | 57.20% | +2.18 pp*** | [+1.47, +2.89 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 58.27% | 58.31% | -0.04 pp | [-0.75, +0.67 pp] | 0.9121 | 1.0000 |
| main | age | `old - young` | 58.37% | 58.22% | +0.15 pp | [-0.56, +0.86 pp] | 0.6858 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.11 pp | +10.02 pp | -9.91 pp*** | [-11.33, -8.49 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.76 pp | +0.56 pp | -2.32 pp** | [-3.75, -0.90 pp] | 0.0014 | 0.0069 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.51 pp | +3.85 pp | -3.34 pp*** | [-4.76, -1.92 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +4.23 pp | +5.89 pp | -1.66 pp | [-3.08, -0.23 pp] | 0.0226 | 0.0905 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **60.47%** [59.82, 61.12%] | `close_friend + poor_record` = **61.18%** [60.48, 61.88%] | `stranger + good_record` = **60.36%** [59.69, 61.04%] | `stranger + poor_record` = **51.16%** [50.35, 51.97%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +10.02 pp*** | [+8.94, +11.09 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.11 pp | [-0.83, +1.04 pp] | 0.8232 |
| `reliability effect | closeness=stranger` | +9.20 pp*** | [+8.15, +10.25 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -0.71 pp | [-1.67, +0.25 pp] | 0.1477 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **59.54%** [58.89, 60.18%] | `mayor + poor_record` = **56.45%** [55.74, 57.16%] | `citizen + good_record` = **61.30%** [60.62, 61.98%] | `citizen + poor_record` = **55.89%** [55.09, 56.69%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.56 pp | [-0.51, +1.63 pp] | 0.3049 |
| `authority effect | reliability=good_record` | -1.76 pp*** | [-2.70, -0.83 pp] | 0.0002 |
| `reliability effect | authority=citizen` | +5.41 pp*** | [+4.36, +6.46 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +3.08 pp*** | [+2.12, +4.05 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **60.67%** [60.01, 61.33%] | `rich + poor_record` = **58.09%** [57.37, 58.82%] | `poor + good_record` = **60.16%** [59.50, 60.83%] | `poor + poor_record` = **54.25%** [53.46, 55.03%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +3.85 pp*** | [+2.77, +4.92 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.51 pp | [-0.43, +1.44 pp] | 0.2886 |
| `reliability effect | wealth=poor` | +5.92 pp*** | [+4.88, +6.95 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +2.58 pp*** | [+1.60, +3.56 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **60.11%** [59.45, 60.77%] | `close_friend + citizen` = **61.54%** [60.84, 62.23%] | `stranger + mayor` = **55.88%** [55.18, 56.57%] | `stranger + citizen` = **55.65%** [54.86, 56.44%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +5.89 pp*** | [+4.84, +6.94 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +4.23 pp*** | [+3.27, +5.19 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +0.23 pp | [-0.83, +1.28 pp] | 0.6725 |
| `authority effect | closeness=close_friend` | -1.43 pp** | [-2.39, -0.47 pp] | 0.0035 |


**Outcome: NOT_MENTIONED (%)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.42% | 0.47% | -0.05 pp | [-0.20, +0.10 pp] | 0.5457 | 1.0000 |
| main | authority | `mayor - citizen` | 0.30% | 0.59% | -0.29 pp** | [-0.44, -0.14 pp] | 0.0002 | 0.0020 |
| main | reliability | `good_record - poor_record` | 0.31% | 0.58% | -0.27 pp** | [-0.43, -0.12 pp] | 0.0004 | 0.0036 |
| main | wealth | `rich - poor` | 0.40% | 0.49% | -0.09 pp | [-0.24, +0.06 pp] | 0.2602 | 1.0000 |
| main | gender | `woman - man` | 0.35% | 0.54% | -0.19 pp | [-0.35, -0.04 pp] | 0.0118 | 0.0941 |
| main | age | `old - young` | 0.46% | 0.43% | +0.03 pp | [-0.12, +0.19 pp] | 0.6643 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.13 pp | -0.23 pp | +0.36 pp | [+0.06, +0.66 pp] | 0.0197 | 0.1382 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.27 pp | -0.31 pp | +0.04 pp | [-0.26, +0.34 pp] | 0.7968 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.00 pp | -0.17 pp | +0.17 pp | [-0.13, +0.48 pp] | 0.2609 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.04 pp | -0.13 pp | +0.17 pp | [-0.13, +0.48 pp] | 0.2614 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.37%** [0.23, 0.52%] | `close_friend + poor_record` = **0.47%** [0.31, 0.62%] | `stranger + good_record` = **0.24%** [0.13, 0.35%] | `stranger + poor_record` = **0.69%** [0.51, 0.88%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.23 pp | [-0.47, +0.02 pp] | 0.0671 |
| `closeness effect | reliability=good_record` | +0.13 pp | [-0.05, +0.31 pp] | 0.1488 |
| `reliability effect | closeness=stranger` | -0.45 pp*** | [-0.67, -0.24 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -0.09 pp | [-0.31, +0.12 pp] | 0.3868 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.17%** [0.07, 0.27%] | `mayor + poor_record` = **0.43%** [0.28, 0.57%] | `citizen + good_record` = **0.44%** [0.29, 0.59%] | `citizen + poor_record` = **0.73%** [0.54, 0.93%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.31 pp* | [-0.55, -0.06 pp] | 0.0131 |
| `authority effect | reliability=good_record` | -0.27 pp** | [-0.45, -0.09 pp] | 0.0038 |
| `reliability effect | authority=citizen` | -0.29 pp* | [-0.54, -0.05 pp] | 0.0197 |
| `reliability effect | authority=mayor` | -0.25 pp** | [-0.43, -0.08 pp] | 0.0046 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.31%** [0.18, 0.44%] | `rich + poor_record` = **0.49%** [0.33, 0.66%] | `poor + good_record` = **0.31%** [0.18, 0.43%] | `poor + poor_record` = **0.67%** [0.49, 0.85%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.17 pp | [-0.42, +0.07 pp] | 0.1604 |
| `wealth effect | reliability=good_record` | -0.00 pp | [-0.18, +0.18 pp] | 0.9990 |
| `reliability effect | wealth=poor` | -0.36 pp** | [-0.58, -0.14 pp] | 0.0014 |
| `reliability effect | wealth=rich` | -0.19 pp | [-0.39, +0.02 pp] | 0.0772 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.32%** [0.19, 0.45%] | `close_friend + citizen` = **0.52%** [0.35, 0.69%] | `stranger + mayor` = **0.28%** [0.16, 0.40%] | `stranger + citizen` = **0.65%** [0.47, 0.84%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.13 pp | [-0.38, +0.11 pp] | 0.2892 |
| `closeness effect | authority=mayor` | +0.04 pp | [-0.14, +0.22 pp] | 0.6545 |
| `authority effect | closeness=stranger` | -0.37 pp*** | [-0.59, -0.16 pp] | 0.0007 |
| `authority effect | closeness=close_friend` | -0.20 pp | [-0.41, +0.01 pp] | 0.0636 |


**Outcome: FACT (%)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 8.63% | 6.40% | +2.23 pp*** | [+1.64, +2.82 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 7.76% | 7.28% | +0.48 pp | [-0.11, +1.07 pp] | 0.1139 | 0.5694 |
| main | reliability | `good_record - poor_record` | 9.93% | 5.11% | +4.83 pp*** | [+4.23, +5.42 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 7.61% | 7.43% | +0.17 pp | [-0.42, +0.77 pp] | 0.5650 | 1.0000 |
| main | gender | `woman - man` | 7.40% | 7.64% | -0.24 pp | [-0.84, +0.35 pp] | 0.4276 | 1.0000 |
| main | age | `old - young` | 7.58% | 7.46% | +0.12 pp | [-0.47, +0.72 pp] | 0.6850 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.33 pp | +3.13 pp | -1.80 pp* | [-2.99, -0.61 pp] | 0.0030 | 0.0219 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.39 pp | -0.43 pp | +1.81 pp* | [+0.63, +3.00 pp] | 0.0027 | 0.0219 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.35 pp | +0.69 pp | -1.04 pp | [-2.23, +0.15 pp] | 0.0858 | 0.5146 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +1.91 pp | +2.55 pp | -0.64 pp | [-1.83, +0.55 pp] | 0.2891 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **10.60%** [9.92, 11.27%] | `close_friend + poor_record` = **6.67%** [6.09, 7.25%] | `stranger + good_record` = **9.27%** [8.62, 9.92%] | `stranger + poor_record` = **3.54%** [3.10, 3.98%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +3.13 pp*** | [+2.40, +3.86 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +1.33 pp** | [+0.39, +2.27 pp] | 0.0054 |
| `reliability effect | closeness=stranger` | +5.73 pp*** | [+4.94, +6.51 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +3.93 pp*** | [+3.03, +4.82 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **10.63%** [9.95, 11.30%] | `mayor + poor_record` = **4.89%** [4.38, 5.40%] | `citizen + good_record` = **9.24%** [8.59, 9.89%] | `citizen + poor_record` = **5.32%** [4.80, 5.84%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.43 pp | [-1.16, +0.30 pp] | 0.2487 |
| `authority effect | reliability=good_record` | +1.39 pp** | [+0.45, +2.32 pp] | 0.0038 |
| `reliability effect | authority=citizen` | +3.92 pp*** | [+3.09, +4.75 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +5.73 pp*** | [+4.89, +6.58 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **9.76%** [9.10, 10.42%] | `rich + poor_record` = **5.45%** [4.94, 5.97%] | `poor + good_record` = **10.11%** [9.44, 10.77%] | `poor + poor_record` = **4.76%** [4.24, 5.27%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.69 pp | [-0.03, +1.42 pp] | 0.0615 |
| `wealth effect | reliability=good_record` | -0.35 pp | [-1.28, +0.59 pp] | 0.4695 |
| `reliability effect | wealth=poor` | +5.35 pp*** | [+4.50, +6.19 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +4.31 pp*** | [+3.47, +5.14 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **8.71%** [8.08, 9.35%] | `close_friend + citizen` = **8.55%** [7.93, 9.18%] | `stranger + mayor` = **6.80%** [6.24, 7.36%] | `stranger + citizen` = **6.00%** [5.46, 6.55%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +2.55 pp*** | [+1.72, +3.38 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +1.91 pp*** | [+1.06, +2.76 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +0.80 pp* | [+0.02, +1.58 pp] | 0.0451 |
| `authority effect | closeness=close_friend` | +0.16 pp | [-0.74, +1.05 pp] | 0.7291 |


**Outcome: UNCERTAIN (%)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 7.48% | 8.19% | -0.71 pp | [-1.31, -0.11 pp] | 0.0211 | 0.1478 |
| main | authority | `mayor - citizen` | 8.50% | 7.17% | +1.33 pp*** | [+0.73, +1.94 pp] | <0.0001 | 0.0001 |
| main | reliability | `good_record - poor_record` | 11.44% | 4.22% | +7.22 pp*** | [+6.62, +7.82 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 8.03% | 7.64% | +0.39 pp | [-0.22, +0.99 pp] | 0.2077 | 1.0000 |
| main | gender | `woman - man` | 7.82% | 7.85% | -0.03 pp | [-0.64, +0.57 pp] | 0.9211 | 1.0000 |
| main | age | `old - young` | 7.77% | 7.89% | -0.12 pp | [-0.72, +0.49 pp] | 0.7043 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.94 pp | -0.48 pp | -0.46 pp | [-1.67, +0.74 pp] | 0.4507 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +2.27 pp | +0.40 pp | +1.87 pp* | [+0.66, +3.08 pp] | 0.0024 | 0.0195 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.83 pp | -0.05 pp | +0.88 pp | [-0.32, +2.09 pp] | 0.1512 | 0.9070 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -1.04 pp | -0.38 pp | -0.67 pp | [-1.88, +0.54 pp] | 0.2788 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **10.97%** [10.28, 11.67%] | `close_friend + poor_record` = **3.98%** [3.53, 4.44%] | `stranger + good_record` = **11.91%** [11.18, 12.65%] | `stranger + poor_record` = **4.46%** [3.99, 4.94%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.48 pp | [-1.14, +0.18 pp] | 0.1558 |
| `closeness effect | reliability=good_record` | -0.94 pp | [-1.95, +0.07 pp] | 0.0677 |
| `reliability effect | closeness=stranger` | +7.45 pp*** | [+6.58, +8.33 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +6.99 pp*** | [+6.16, +7.82 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **12.58%** [11.81, 13.35%] | `mayor + poor_record` = **4.42%** [3.95, 4.90%] | `citizen + good_record` = **10.31%** [9.65, 10.97%] | `citizen + poor_record` = **4.02%** [3.56, 4.48%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.40 pp | [-0.26, +1.06 pp] | 0.2349 |
| `authority effect | reliability=good_record` | +2.27 pp*** | [+1.26, +3.28 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +6.29 pp*** | [+5.48, +7.09 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +8.15 pp*** | [+7.25, +9.06 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **11.86%** [11.13, 12.59%] | `rich + poor_record` = **4.20%** [3.72, 4.67%] | `poor + good_record` = **11.03%** [10.33, 11.73%] | `poor + poor_record` = **4.25%** [3.79, 4.71%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.05 pp | [-0.71, +0.61 pp] | 0.8724 |
| `wealth effect | reliability=good_record` | +0.83 pp | [-0.18, +1.84 pp] | 0.1075 |
| `reliability effect | wealth=poor` | +6.78 pp*** | [+5.94, +7.62 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +7.66 pp*** | [+6.80, +8.53 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **7.98%** [7.37, 8.59%] | `close_friend + citizen` = **6.98%** [6.41, 7.54%] | `stranger + mayor` = **9.02%** [8.36, 9.69%] | `stranger + citizen` = **7.35%** [6.78, 7.92%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.38 pp | [-1.18, +0.43 pp] | 0.3570 |
| `closeness effect | authority=mayor` | -1.04 pp* | [-1.95, -0.14 pp] | 0.0234 |
| `authority effect | closeness=stranger` | +1.67 pp*** | [+0.79, +2.54 pp] | 0.0002 |
| `authority effect | closeness=close_friend` | +1.00 pp* | [+0.17, +1.83 pp] | 0.0185 |


**Outcome: SKEPTICAL (%)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 7.53% | 14.75% | -7.22 pp*** | [-7.94, -6.51 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 10.96% | 11.31% | -0.35 pp | [-1.06, +0.37 pp] | 0.3389 | 0.7651 |
| main | reliability | `good_record - poor_record` | 2.10% | 20.18% | -18.08 pp*** | [-18.79, -17.36 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 9.88% | 12.39% | -2.51 pp*** | [-3.23, -1.80 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 11.38% | 10.89% | +0.49 pp | [-0.22, +1.20 pp] | 0.1792 | 0.7170 |
| main | age | `old - young` | 10.93% | 11.34% | -0.42 pp | [-1.13, +0.30 pp] | 0.2550 | 0.7651 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.19 pp | -14.26 pp | +14.07 pp*** | [+12.64, +15.50 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.13 pp | -0.56 pp | +0.43 pp | [-1.00, +1.86 pp] | 0.5567 | 0.7651 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.19 pp | -4.84 pp | +4.66 pp*** | [+3.23, +6.09 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -6.50 pp | -7.94 pp | +1.44 pp | [+0.01, +2.87 pp] | 0.0480 | 0.2400 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **2.00%** [1.69, 2.32%] | `close_friend + poor_record` = **13.05%** [12.27, 13.83%] | `stranger + good_record` = **2.19%** [1.86, 2.52%] | `stranger + poor_record` = **27.30%** [26.20, 28.41%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -14.26 pp*** | [-15.61, -12.90 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.19 pp | [-0.64, +0.26 pp] | 0.4145 |
| `reliability effect | closeness=stranger` | -25.11 pp*** | [-26.27, -23.96 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -11.04 pp*** | [-11.88, -10.20 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **2.03%** [1.71, 2.35%] | `mayor + poor_record` = **19.89%** [18.92, 20.87%] | `citizen + good_record` = **2.17%** [1.85, 2.48%] | `citizen + poor_record` = **20.46%** [19.51, 21.40%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.56 pp | [-1.92, +0.79 pp] | 0.4157 |
| `authority effect | reliability=good_record` | -0.13 pp | [-0.59, +0.32 pp] | 0.5602 |
| `reliability effect | authority=citizen` | -18.29 pp*** | [-19.29, -17.30 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -17.86 pp*** | [-18.89, -16.84 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **2.01%** [1.68, 2.33%] | `rich + poor_record` = **17.75%** [16.84, 18.67%] | `poor + good_record` = **2.19%** [1.87, 2.51%] | `poor + poor_record` = **22.60%** [21.60, 23.60%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -4.84 pp*** | [-6.20, -3.49 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.19 pp | [-0.64, +0.27 pp] | 0.4195 |
| `reliability effect | wealth=poor` | -20.41 pp*** | [-21.45, -19.36 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -15.75 pp*** | [-16.72, -14.78 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **7.71%** [7.09, 8.34%] | `close_friend + citizen` = **7.34%** [6.78, 7.90%] | `stranger + mayor` = **14.21%** [13.40, 15.03%] | `stranger + citizen` = **15.28%** [14.46, 16.11%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -7.94 pp*** | [-8.94, -6.95 pp] | <0.0001 |
| `closeness effect | authority=mayor` | -6.50 pp*** | [-7.53, -5.48 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -1.07 pp | [-2.23, +0.09 pp] | 0.0699 |
| `authority effect | closeness=close_friend` | +0.37 pp | [-0.47, +1.21 pp] | 0.3849 |


**Outcome: CHECKED_TRUE (%)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 75.59% | 69.80% | +5.80 pp*** | [+4.81, +6.78 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 72.12% | 73.27% | -1.16 pp | [-2.14, -0.17 pp] | 0.0211 | 0.0846 |
| main | reliability | `good_record - poor_record` | 76.21% | 69.19% | +7.02 pp*** | [+6.03, +8.00 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 73.77% | 71.62% | +2.15 pp*** | [+1.17, +3.14 pp] | <0.0001 | 0.0001 |
| main | gender | `woman - man` | 72.67% | 72.72% | -0.05 pp | [-1.03, +0.94 pp] | 0.9267 | 1.0000 |
| main | age | `old - young` | 72.92% | 72.47% | +0.45 pp | [-0.53, +1.43 pp] | 0.3707 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.33 pp | +11.93 pp | -12.26 pp*** | [-14.23, -10.29 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -3.25 pp | +0.94 pp | -4.19 pp*** | [-6.16, -2.22 pp] | <0.0001 | 0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.30 pp | +4.60 pp | -4.90 pp*** | [-6.87, -2.93 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +5.52 pp | +6.08 pp | -0.56 pp | [-2.53, +1.41 pp] | 0.5771 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **76.04%** [75.16, 76.92%] | `close_friend + poor_record` = **75.15%** [74.17, 76.13%] | `stranger + good_record` = **76.37%** [75.42, 77.33%] | `stranger + poor_record` = **63.22%** [62.12, 64.32%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +11.93 pp*** | [+10.45, +13.40 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.33 pp | [-1.63, +0.97 pp] | 0.6170 |
| `reliability effect | closeness=stranger` | +13.15 pp*** | [+11.69, +14.60 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.89 pp | [-0.43, +2.21 pp] | 0.1874 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **74.58%** [73.62, 75.53%] | `mayor + poor_record` = **69.66%** [68.61, 70.70%] | `citizen + good_record` = **77.83%** [76.95, 78.72%] | `citizen + poor_record` = **68.72%** [67.68, 69.76%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.94 pp | [-0.54, +2.41 pp] | 0.2120 |
| `authority effect | reliability=good_record` | -3.25 pp*** | [-4.55, -1.95 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +9.11 pp*** | [+7.75, +10.48 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +4.92 pp*** | [+3.50, +6.34 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **76.06%** [75.13, 76.99%] | `rich + poor_record` = **71.49%** [70.48, 72.50%] | `poor + good_record` = **76.35%** [75.44, 77.27%] | `poor + poor_record` = **66.89%** [65.81, 67.96%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +4.60 pp*** | [+3.13, +6.08 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.30 pp | [-1.60, +1.00 pp] | 0.6535 |
| `reliability effect | wealth=poor` | +9.47 pp*** | [+8.06, +10.88 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +4.57 pp*** | [+3.19, +5.94 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **74.88%** [73.91, 75.84%] | `close_friend + citizen` = **76.31%** [75.41, 77.21%] | `stranger + mayor` = **69.36%** [68.32, 70.40%] | `stranger + citizen` = **70.24%** [69.21, 71.26%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +6.08 pp*** | [+4.71, +7.44 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +5.52 pp*** | [+4.10, +6.94 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -0.88 pp | [-2.33, +0.58 pp] | 0.2382 |
| `authority effect | closeness=close_friend` | -1.44 pp* | [-2.76, -0.12 pp] | 0.0330 |


**Outcome: CHECKED_FALSE (%)** (n=29,928, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.35% | 0.39% | -0.05 pp | [-0.20, +0.10 pp] | 0.5458 | 1.0000 |
| main | authority | `mayor - citizen` | 0.36% | 0.38% | -0.02 pp | [-0.17, +0.13 pp] | 0.7945 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.01% | 0.73% | -0.71 pp*** | [-0.87, -0.56 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.31% | 0.43% | -0.11 pp | [-0.26, +0.04 pp] | 0.1404 | 1.0000 |
| main | gender | `woman - man` | 0.38% | 0.36% | +0.02 pp | [-0.13, +0.17 pp] | 0.7648 | 1.0000 |
| main | age | `old - young` | 0.33% | 0.41% | -0.07 pp | [-0.22, +0.08 pp] | 0.3395 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.00 pp | -0.09 pp | +0.09 pp | [-0.21, +0.40 pp] | 0.5456 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.00 pp | -0.04 pp | +0.04 pp | [-0.26, +0.34 pp] | 0.7946 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.00 pp | -0.23 pp | +0.23 pp | [-0.07, +0.53 pp] | 0.1402 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.08 pp | -0.17 pp | +0.25 pp | [-0.05, +0.56 pp] | 0.0995 | 0.8957 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.01%** [-0.01, 0.04%] | `close_friend + poor_record` = **0.68%** [0.50, 0.86%] | `stranger + good_record` = **0.01%** [-0.01, 0.04%] | `stranger + poor_record` = **0.77%** [0.54, 1.01%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.09 pp | [-0.39, +0.21 pp] | 0.5424 |
| `closeness effect | reliability=good_record` | +0.00 pp | [-0.04, +0.04 pp] | 0.9991 |
| `reliability effect | closeness=stranger` | -0.76 pp*** | [-1.00, -0.52 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -0.67 pp*** | [-0.85, -0.48 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.01%** [-0.01, 0.04%] | `mayor + poor_record` = **0.71%** [0.51, 0.91%] | `citizen + good_record` = **0.01%** [-0.01, 0.04%] | `citizen + poor_record` = **0.75%** [0.53, 0.97%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.04 pp | [-0.34, +0.26 pp] | 0.7929 |
| `authority effect | reliability=good_record` | -0.00 pp | [-0.04, +0.04 pp] | 0.9997 |
| `reliability effect | authority=citizen` | -0.73 pp*** | [-0.96, -0.51 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -0.69 pp*** | [-0.90, -0.49 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.01%** [-0.01, 0.04%] | `rich + poor_record` = **0.61%** [0.43, 0.80%] | `poor + good_record` = **0.01%** [-0.01, 0.04%] | `poor + poor_record` = **0.84%** [0.60, 1.08%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.23 pp | [-0.53, +0.07 pp] | 0.1371 |
| `wealth effect | reliability=good_record` | +0.00 pp | [-0.04, +0.04 pp] | 0.9970 |
| `reliability effect | wealth=poor` | -0.83 pp*** | [-1.07, -0.59 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -0.60 pp*** | [-0.79, -0.42 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.40%** [0.26, 0.54%] | `close_friend + citizen` = **0.29%** [0.17, 0.42%] | `stranger + mayor` = **0.32%** [0.17, 0.47%] | `stranger + citizen` = **0.47%** [0.28, 0.65%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.17 pp | [-0.40, +0.05 pp] | 0.1293 |
| `closeness effect | authority=mayor` | +0.08 pp | [-0.12, +0.28 pp] | 0.4365 |
| `authority effect | closeness=stranger` | -0.15 pp | [-0.39, +0.09 pp] | 0.2275 |
| `authority effect | closeness=close_friend` | +0.11 pp | [-0.08, +0.29 pp] | 0.2576 |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,946, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.9505 | 0.8347 | +0.1158*** | [+0.1070, +0.1246] | <0.0001 | <0.0001 | +0.1158 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.9001 | 0.8851 | +0.0149** | [+0.0061, +0.0237] | 0.0009 | 0.0035 | +0.0149 (p=0.0009) |
| main | reliability | `good_record - poor_record` | 0.9720 | 0.8132 | +0.1589*** | [+0.1501, +0.1676] | <0.0001 | <0.0001 | +0.1589 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.9078 | 0.8774 | +0.0305*** | [+0.0217, +0.0393] | <0.0001 | <0.0001 | +0.0305 (p=<0.0001) |
| main | gender | `woman - man` | 0.8932 | 0.8920 | +0.0013 | [-0.0075, +0.0101] | 0.7786 | 0.7786 | +0.0013 (p=0.7796) |
| main | age | `old - young` | 0.8959 | 0.8894 | +0.0065 | [-0.0023, +0.0153] | 0.1478 | 0.2956 | +0.0065 (p=0.1485) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0075 | +0.2242 | -0.2167*** | [-0.2343, -0.1991] | <0.0001 | <0.0001 | -0.2167 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0075 | +0.0373 | -0.0448*** | [-0.0624, -0.0272] | <0.0001 | <0.0001 | -0.0448 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0021 | +0.0631 | -0.0652*** | [-0.0828, -0.0476] | <0.0001 | <0.0001 | -0.0652 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.1064 | +0.1253 | -0.0190 | [-0.0366, -0.0014] | 0.0345 | 0.1036 | -0.0190 (p=0.0349) |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.9758** [0.9720, 0.9796] | `close_friend + poor_record` = **0.9253** [0.9166, 0.9339] | `stranger + good_record` = **0.9683** [0.9638, 0.9728] | `stranger + poor_record` = **0.7011** [0.6870, 0.7152]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.2242*** | [+0.2076, +0.2407] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.0075* | [+0.0016, +0.0134] | 0.0127 |
| `reliability effect | closeness=stranger` | +0.2672*** | [+0.2524, +0.2820] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.0505*** | [+0.0411, +0.0600] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.9683** [0.9638, 0.9728] | `mayor + poor_record` = **0.8318** [0.8205, 0.8432] | `citizen + good_record` = **0.9758** [0.9720, 0.9796] | `citizen + poor_record` = **0.7945** [0.7825, 0.8066]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.0373*** | [+0.0208, +0.0539] | <0.0001 |
| `authority effect | reliability=good_record` | -0.0075* | [-0.0134, -0.0016] | 0.0129 |
| `reliability effect | authority=citizen` | +0.1813*** | [+0.1686, +0.1939] | <0.0001 |
| `reliability effect | authority=mayor` | +0.1364*** | [+0.1242, +0.1487] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.9710** [0.9668, 0.9751] | `rich + poor_record` = **0.8447** [0.8337, 0.8558] | `poor + good_record` = **0.9731** [0.9689, 0.9773] | `poor + poor_record` = **0.7816** [0.7693, 0.7940]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.0631*** | [+0.0465, +0.0796] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.0021 | [-0.0080, +0.0038] | 0.4770 |
| `reliability effect | wealth=poor` | +0.1915*** | [+0.1784, +0.2045] | <0.0001 |
| `reliability effect | wealth=rich` | +0.1262*** | [+0.1144, +0.1380] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.9532** [0.9466, 0.9599] | `close_friend + citizen` = **0.9478** [0.9411, 0.9545] | `stranger + mayor` = **0.8469** [0.8366, 0.8571] | `stranger + citizen` = **0.8225** [0.8118, 0.8332]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.1253*** | [+0.1127, +0.1380] | <0.0001 |
| `closeness effect | authority=mayor` | +0.1064*** | [+0.0941, +0.1186] | <0.0001 |
| `authority effect | closeness=stranger` | +0.0244** | [+0.0096, +0.0392] | 0.0013 |
| `authority effect | closeness=close_friend` | +0.0054 | [-0.0040, +0.0149] | 0.2597 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.9489 | 0.8339 | +0.1149*** | [+0.1061, +0.1238] | <0.0001 | <0.0001 | +0.1149 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8988 | 0.8840 | +0.0149** | [+0.0060, +0.0237] | 0.0010 | 0.0040 | +0.0149 (p=0.0010) |
| main | reliability | `good_record - poor_record` | 0.9707 | 0.8121 | +0.1586*** | [+0.1498, +0.1675] | <0.0001 | <0.0001 | +0.1586 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.9071 | 0.8757 | +0.0314*** | [+0.0225, +0.0402] | <0.0001 | <0.0001 | +0.0314 (p=<0.0001) |
| main | gender | `woman - man` | 0.8919 | 0.8909 | +0.0010 | [-0.0078, +0.0099] | 0.8207 | 0.8207 | +0.0010 (p=0.8213) |
| main | age | `old - young` | 0.8946 | 0.8882 | +0.0063 | [-0.0025, +0.0152] | 0.1617 | 0.3234 | +0.0063 (p=0.1624) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0065 | +0.2234 | -0.2170*** | [-0.2347, -0.1993] | <0.0001 | <0.0001 | -0.2170 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0075 | +0.0372 | -0.0447*** | [-0.0624, -0.0270] | <0.0001 | <0.0001 | -0.0447 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0016 | +0.0644 | -0.0660*** | [-0.0837, -0.0483] | <0.0001 | <0.0001 | -0.0660 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.1053 | +0.1246 | -0.0193 | [-0.0370, -0.0016] | 0.0330 | 0.0991 | -0.0193 (p=0.0334) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.9497 | 0.8344 | +0.1153*** | [+0.1065, +0.1241] | <0.0001 | <0.0001 | +0.1153 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.8995 | 0.8846 | +0.0149** | [+0.0061, +0.0237] | 0.0009 | 0.0037 | +0.0149 (p=0.0010) |
| main | reliability | `good_record - poor_record` | 0.9714 | 0.8128 | +0.1586*** | [+0.1498, +0.1674] | <0.0001 | <0.0001 | +0.1586 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.9075 | 0.8767 | +0.0308*** | [+0.0220, +0.0396] | <0.0001 | <0.0001 | +0.0308 (p=<0.0001) |
| main | gender | `woman - man` | 0.8927 | 0.8915 | +0.0012 | [-0.0076, +0.0100] | 0.7966 | 0.7966 | +0.0012 (p=0.7972) |
| main | age | `old - young` | 0.8953 | 0.8888 | +0.0065 | [-0.0023, +0.0153] | 0.1505 | 0.3011 | +0.0065 (p=0.1512) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0070 | +0.2237 | -0.2167*** | [-0.2343, -0.1991] | <0.0001 | <0.0001 | -0.2167 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0075 | +0.0372 | -0.0447*** | [-0.0623, -0.0271] | <0.0001 | <0.0001 | -0.0447 (p=<0.0001) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0019 | +0.0636 | -0.0654*** | [-0.0830, -0.0478] | <0.0001 | <0.0001 | -0.0654 (p=<0.0001) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.1059 | +0.1248 | -0.0190 | [-0.0366, -0.0014] | 0.0344 | 0.1033 | -0.0190 (p=0.0348) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 98.33% | 87.14% | +11.19 pp*** | [+10.46, +11.93 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 94.03% | 91.44% | +2.59 pp*** | [+1.86, +3.33 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 99.75% | 85.72% | +14.02 pp*** | [+13.29, +14.76 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 94.66% | 90.81% | +3.85 pp*** | [+3.11, +4.58 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 92.53% | 92.94% | -0.41 pp | [-1.14, +0.33 pp] | 0.2755 | 0.5511 |
| main | age | `old - young` | 92.79% | 92.68% | +0.11 pp | [-0.63, +0.84 pp] | 0.7757 | 0.7757 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.19 pp | +22.20 pp | -22.01 pp*** | [-23.48, -20.54 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.29 pp | +4.89 pp | -4.59 pp*** | [-6.06, -3.12 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.08 pp | +7.61 pp | -7.53 pp*** | [-9.00, -6.06 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +9.75 pp | +12.63 pp | -2.88 pp*** | [-4.35, -1.41 pp] | 0.0001 | 0.0004 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **99.84%** [99.69, 99.99%] | `close_friend + poor_record` = **96.82%** [96.22, 97.42%] | `stranger + good_record` = **99.65%** [99.45, 99.85%] | `stranger + poor_record` = **74.63%** [73.31, 75.95%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +22.20 pp*** | [+20.75, +23.64 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.19 pp | [-0.06, +0.44 pp] | 0.1420 |
| `reliability effect | closeness=stranger` | +25.03 pp*** | [+23.69, +26.36 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +3.02 pp*** | [+2.40, +3.63 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **99.89%** [99.77, 100.02%] | `mayor + poor_record` = **88.17%** [87.24, 89.09%] | `citizen + good_record` = **99.60%** [99.38, 99.81%] | `citizen + poor_record` = **83.28%** [82.17, 84.39%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +4.89 pp*** | [+3.44, +6.34 pp] | <0.0001 |
| `authority effect | reliability=good_record` | +0.29 pp* | [+0.04, +0.54 pp] | 0.0210 |
| `reliability effect | authority=citizen` | +16.32 pp*** | [+15.18, +17.45 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +11.73 pp*** | [+10.79, +12.66 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **99.79%** [99.62, 99.95%] | `rich + poor_record` = **89.53%** [88.60, 90.46%] | `poor + good_record` = **99.71%** [99.52, 99.90%] | `poor + poor_record` = **81.92%** [80.80, 83.03%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +7.61 pp*** | [+6.16, +9.06 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.08 pp | [-0.17, +0.33 pp] | 0.5292 |
| `reliability effect | wealth=poor` | +17.79 pp*** | [+16.66, +18.92 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +10.26 pp*** | [+9.32, +11.20 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **98.90%** [98.52, 99.29%] | `close_friend + citizen` = **97.76%** [97.27, 98.24%] | `stranger + mayor` = **89.16%** [88.30, 90.01%] | `stranger + citizen` = **85.12%** [84.10, 86.15%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +12.63 pp*** | [+11.50, +13.77 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +9.75 pp*** | [+8.81, +10.68 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +4.03 pp*** | [+2.70, +5.37 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | +1.15 pp*** | [+0.53, +1.77 pp] | 0.0003 |


**Outcome: NOT_MENTIONED (%)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.17% | 0.09% | +0.08 pp | [-0.04, +0.20 pp] | 0.1779 | 1.0000 |
| main | authority | `mayor - citizen` | 0.13% | 0.13% | +0.00 pp | [-0.12, +0.12 pp] | 1.0000 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.13% | 0.13% | -0.00 pp | [-0.12, +0.12 pp] | 0.9996 | 1.0000 |
| main | wealth | `rich - poor` | 0.08% | 0.19% | -0.11 pp | [-0.22, +0.01 pp] | 0.0723 | 0.7226 |
| main | gender | `woman - man` | 0.15% | 0.12% | +0.03 pp | [-0.09, +0.14 pp] | 0.6559 | 1.0000 |
| main | age | `old - young` | 0.15% | 0.12% | +0.03 pp | [-0.09, +0.14 pp] | 0.6532 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.11 pp | +0.05 pp | +0.05 pp | [-0.18, +0.29 pp] | 0.6548 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.00 pp | +0.00 pp | -0.00 pp | [-0.23, +0.23 pp] | 0.9998 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.05 pp | -0.16 pp | +0.11 pp | [-0.13, +0.34 pp] | 0.3687 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.11 pp | +0.05 pp | +0.05 pp | [-0.18, +0.29 pp] | 0.6537 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.19%** [0.05, 0.32%] | `close_friend + poor_record` = **0.16%** [0.03, 0.29%] | `stranger + good_record` = **0.08%** [-0.01, 0.17%] | `stranger + poor_record` = **0.11%** [0.00, 0.21%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.05 pp | [-0.11, +0.22 pp] | 0.5243 |
| `closeness effect | reliability=good_record` | +0.11 pp | [-0.06, +0.27 pp] | 0.2048 |
| `reliability effect | closeness=stranger` | -0.03 pp | [-0.16, +0.11 pp] | 0.7058 |
| `reliability effect | closeness=close_friend` | +0.03 pp | [-0.16, +0.21 pp] | 0.7815 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.13%** [0.02, 0.25%] | `mayor + poor_record` = **0.13%** [0.02, 0.25%] | `citizen + good_record` = **0.13%** [0.02, 0.25%] | `citizen + poor_record` = **0.13%** [0.02, 0.25%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.00 pp | [-0.16, +0.16 pp] | 0.9998 |
| `authority effect | reliability=good_record` | -0.00 pp | [-0.16, +0.16 pp] | 0.9999 |
| `reliability effect | authority=citizen` | -0.00 pp | [-0.16, +0.16 pp] | 0.9999 |
| `reliability effect | authority=mayor` | -0.00 pp | [-0.16, +0.16 pp] | 0.9996 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.11%** [0.00, 0.21%] | `rich + poor_record` = **0.05%** [-0.02, 0.13%] | `poor + good_record` = **0.16%** [0.03, 0.29%] | `poor + poor_record` = **0.21%** [0.07, 0.36%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.16 pp | [-0.33, +0.00 pp] | 0.0564 |
| `wealth effect | reliability=good_record` | -0.05 pp | [-0.22, +0.11 pp] | 0.5255 |
| `reliability effect | wealth=poor` | -0.05 pp | [-0.25, +0.14 pp] | 0.5906 |
| `reliability effect | wealth=rich` | +0.05 pp | [-0.07, +0.18 pp] | 0.4130 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.19%** [0.05, 0.32%] | `close_friend + citizen` = **0.16%** [0.03, 0.29%] | `stranger + mayor` = **0.08%** [-0.01, 0.17%] | `stranger + citizen` = **0.11%** [0.00, 0.21%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.05 pp | [-0.11, +0.22 pp] | 0.5255 |
| `closeness effect | authority=mayor` | +0.11 pp | [-0.06, +0.27 pp] | 0.2039 |
| `authority effect | closeness=stranger` | -0.03 pp | [-0.16, +0.11 pp] | 0.7052 |
| `authority effect | closeness=close_friend` | +0.03 pp | [-0.16, +0.21 pp] | 0.7806 |


**Outcome: FACT (%)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 4.64% | 3.40% | +1.24 pp*** | [+0.62, +1.86 pp] | <0.0001 | 0.0008 |
| main | authority | `mayor - citizen` | 3.88% | 4.16% | -0.28 pp | [-0.90, +0.34 pp] | 0.3746 | 1.0000 |
| main | reliability | `good_record - poor_record` | 4.25% | 3.78% | +0.47 pp | [-0.15, +1.09 pp] | 0.1386 | 0.9704 |
| main | wealth | `rich - poor` | 4.08% | 3.96% | +0.12 pp | [-0.50, +0.74 pp] | 0.7064 | 1.0000 |
| main | gender | `woman - man` | 4.05% | 3.99% | +0.06 pp | [-0.56, +0.68 pp] | 0.8479 | 1.0000 |
| main | age | `old - young` | 3.86% | 4.17% | -0.31 pp | [-0.93, +0.31 pp] | 0.3328 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.22 pp | +2.70 pp | -2.92 pp*** | [-4.16, -1.68 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.37 pp | -0.19 pp | -0.19 pp | [-1.43, +1.05 pp] | 0.7692 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.32 pp | +0.56 pp | -0.88 pp | [-2.12, +0.36 pp] | 0.1643 | 0.9857 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.75 pp | +1.74 pp | -0.99 pp | [-2.23, +0.25 pp] | 0.1174 | 0.9396 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **4.14%** [3.51, 4.77%] | `close_friend + poor_record` = **5.13%** [4.43, 5.84%] | `stranger + good_record` = **4.36%** [3.72, 5.00%] | `stranger + poor_record` = **2.43%** [1.94, 2.92%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +2.70 pp*** | [+1.84, +3.56 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.22 pp | [-1.12, +0.68 pp] | 0.6296 |
| `reliability effect | closeness=stranger` | +1.93 pp*** | [+1.13, +2.73 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -0.99 pp* | [-1.94, -0.05 pp] | 0.0394 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **4.06%** [3.45, 4.67%] | `mayor + poor_record` = **3.69%** [3.10, 4.28%] | `citizen + good_record` = **4.44%** [3.78, 5.10%] | `citizen + poor_record` = **3.88%** [3.26, 4.50%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.19 pp | [-1.05, +0.67 pp] | 0.6672 |
| `authority effect | reliability=good_record` | -0.37 pp | [-1.27, +0.52 pp] | 0.4139 |
| `reliability effect | authority=citizen` | +0.56 pp | [-0.34, +1.47 pp] | 0.2236 |
| `reliability effect | authority=mayor` | +0.38 pp | [-0.47, +1.22 pp] | 0.3858 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **4.09%** [3.45, 4.73%] | `rich + poor_record` = **4.06%** [3.44, 4.68%] | `poor + good_record` = **4.41%** [3.78, 5.04%] | `poor + poor_record` = **3.50%** [2.91, 4.09%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.56 pp | [-0.30, +1.42 pp] | 0.2010 |
| `wealth effect | reliability=good_record` | -0.32 pp | [-1.22, +0.58 pp] | 0.4829 |
| `reliability effect | wealth=poor` | +0.91 pp* | [+0.04, +1.77 pp] | 0.0394 |
| `reliability effect | wealth=rich` | +0.03 pp | [-0.86, +0.92 pp] | 0.9499 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **4.25%** [3.61, 4.88%] | `close_friend + citizen` = **5.02%** [4.32, 5.72%] | `stranger + mayor` = **3.50%** [2.94, 4.07%] | `stranger + citizen` = **3.29%** [2.72, 3.86%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +1.74 pp*** | [+0.83, +2.64 pp] | 0.0002 |
| `closeness effect | authority=mayor` | +0.75 pp | [-0.10, +1.59 pp] | 0.0854 |
| `authority effect | closeness=stranger` | +0.21 pp | [-0.59, +1.02 pp] | 0.6011 |
| `authority effect | closeness=close_friend` | -0.78 pp | [-1.72, +0.17 pp] | 0.1071 |


**Outcome: UNCERTAIN (%)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 3.06% | 4.17% | -1.11 pp** | [-1.70, -0.52 pp] | 0.0002 | 0.0021 |
| main | authority | `mayor - citizen` | 4.04% | 3.19% | +0.84 pp* | [+0.25, +1.43 pp] | 0.0053 | 0.0422 |
| main | reliability | `good_record - poor_record` | 4.54% | 2.69% | +1.86 pp*** | [+1.27, +2.45 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 3.57% | 3.66% | -0.09 pp | [-0.69, +0.50 pp] | 0.7540 | 1.0000 |
| main | gender | `woman - man` | 3.43% | 3.80% | -0.36 pp | [-0.96, +0.23 pp] | 0.2304 | 1.0000 |
| main | age | `old - young` | 3.58% | 3.65% | -0.07 pp | [-0.66, +0.53 pp] | 0.8285 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.60 pp | -1.63 pp | +1.03 pp | [-0.15, +2.22 pp] | 0.0870 | 0.6091 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.34 pp | +0.35 pp | +0.99 pp | [-0.19, +2.17 pp] | 0.1015 | 0.6092 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.05 pp | -0.24 pp | +0.30 pp | [-0.89, +1.48 pp] | 0.6251 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -1.39 pp | -0.83 pp | -0.56 pp | [-1.75, +0.62 pp] | 0.3506 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **4.25%** [3.61, 4.88%] | `close_friend + poor_record` = **1.87%** [1.43, 2.31%] | `stranger + good_record` = **4.84%** [4.14, 5.54%] | `stranger + poor_record` = **3.50%** [2.94, 4.06%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -1.63 pp*** | [-2.34, -0.91 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.60 pp | [-1.54, +0.35 pp] | 0.2165 |
| `reliability effect | closeness=stranger` | +1.34 pp** | [+0.44, +2.24 pp] | 0.0034 |
| `reliability effect | closeness=close_friend` | +2.38 pp*** | [+1.61, +3.15 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **5.21%** [4.50, 5.93%] | `mayor + poor_record` = **2.86%** [2.33, 3.39%] | `citizen + good_record` = **3.88%** [3.26, 4.49%] | `citizen + poor_record` = **2.51%** [2.03, 2.99%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.35 pp | [-0.37, +1.06 pp] | 0.3393 |
| `authority effect | reliability=good_record` | +1.34 pp** | [+0.39, +2.28 pp] | 0.0055 |
| `reliability effect | authority=citizen` | +1.36 pp*** | [+0.58, +2.15 pp] | 0.0006 |
| `reliability effect | authority=mayor` | +2.35 pp*** | [+1.46, +3.24 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **4.57%** [3.92, 5.22%] | `rich + poor_record` = **2.56%** [2.07, 3.06%] | `poor + good_record` = **4.52%** [3.83, 5.21%] | `poor + poor_record` = **2.81%** [2.30, 3.32%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.24 pp | [-0.96, +0.47 pp] | 0.5062 |
| `wealth effect | reliability=good_record` | +0.05 pp | [-0.89, +1.00 pp] | 0.9125 |
| `reliability effect | wealth=poor` | +1.71 pp*** | [+0.85, +2.57 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +2.01 pp*** | [+1.19, +2.82 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **3.34%** [2.77, 3.91%] | `close_friend + citizen` = **2.78%** [2.26, 3.30%] | `stranger + mayor` = **4.73%** [4.05, 5.42%] | `stranger + citizen` = **3.61%** [3.03, 4.19%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.83 pp* | [-1.61, -0.05 pp] | 0.0372 |
| `closeness effect | authority=mayor` | -1.39 pp** | [-2.28, -0.50 pp] | 0.0021 |
| `authority effect | closeness=stranger` | +1.12 pp* | [+0.23, +2.02 pp] | 0.0142 |
| `authority effect | closeness=close_friend` | +0.56 pp | [-0.21, +1.33 pp] | 0.1539 |


**Outcome: SKEPTICAL (%)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 3.26% | 14.07% | -10.81 pp*** | [-11.65, -9.96 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 7.74% | 9.59% | -1.85 pp*** | [-2.70, -1.01 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 0.51% | 16.82% | -16.31 pp*** | [-17.16, -15.47 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 7.24% | 10.09% | -2.85 pp*** | [-3.69, -2.01 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 8.73% | 8.60% | +0.13 pp | [-0.71, +0.97 pp] | 0.7651 | 0.7651 |
| main | age | `old - young` | 8.38% | 8.95% | -0.57 pp | [-1.42, +0.27 pp] | 0.1831 | 0.3662 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.43 pp | -21.18 pp | +20.75 pp*** | [+19.07, +22.44 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.11 pp | -3.81 pp | +3.92 pp*** | [+2.23, +5.61 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.16 pp | -5.86 pp | +6.02 pp*** | [+4.34, +7.71 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -9.81 pp | -11.80 pp | +1.99 pp | [+0.31, +3.68 pp] | 0.0204 | 0.0613 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.29%** [0.10, 0.49%] | `close_friend + poor_record` = **6.23%** [5.40, 7.06%] | `stranger + good_record` = **0.72%** [0.44, 1.01%] | `stranger + poor_record` = **27.41%** [25.99, 28.84%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -21.18 pp*** | [-22.83, -19.53 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | -0.43 pp* | [-0.77, -0.08 pp] | 0.0149 |
| `reliability effect | closeness=stranger` | -26.69 pp*** | [-28.14, -25.23 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -5.94 pp*** | [-6.79, -5.08 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.56%** [0.30, 0.82%] | `mayor + poor_record` = **14.91%** [13.78, 16.04%] | `citizen + good_record` = **0.46%** [0.23, 0.68%] | `citizen + poor_record` = **18.73%** [17.53, 19.93%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -3.81 pp*** | [-5.46, -2.16 pp] | <0.0001 |
| `authority effect | reliability=good_record` | +0.11 pp | [-0.24, +0.45 pp] | 0.5479 |
| `reliability effect | authority=citizen` | -18.27 pp*** | [-19.50, -17.05 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -14.35 pp*** | [-15.51, -13.19 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.59%** [0.33, 0.84%] | `rich + poor_record` = **13.89%** [12.79, 14.99%] | `poor + good_record` = **0.43%** [0.19, 0.66%] | `poor + poor_record` = **19.75%** [18.52, 20.98%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -5.86 pp*** | [-7.51, -4.21 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.16 pp | [-0.18, +0.51 pp] | 0.3597 |
| `reliability effect | wealth=poor` | -19.32 pp*** | [-20.57, -18.07 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -13.30 pp*** | [-14.43, -12.17 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **2.83%** [2.24, 3.42%] | `close_friend + citizen` = **3.69%** [3.08, 4.31%] | `stranger + mayor` = **12.64%** [11.64, 13.64%] | `stranger + citizen` = **15.49%** [14.43, 16.55%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -11.80 pp*** | [-13.03, -10.58 pp] | <0.0001 |
| `closeness effect | authority=mayor` | -9.81 pp*** | [-10.97, -8.65 pp] | <0.0001 |
| `authority effect | closeness=stranger` | -2.85 pp*** | [-4.31, -1.40 pp] | 0.0001 |
| `authority effect | closeness=close_friend` | -0.86 pp* | [-1.71, -0.01 pp] | 0.0486 |


**Outcome: CHECKED_TRUE (%)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 88.72% | 77.91% | +10.81 pp*** | [+9.67, +11.95 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 83.99% | 82.64% | +1.35 pp | [+0.21, +2.49 pp] | 0.0206 | 0.0822 |
| main | reliability | `good_record - poor_record` | 90.55% | 76.08% | +14.47 pp*** | [+13.33, +15.61 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 84.85% | 81.78% | +3.07 pp*** | [+1.93, +4.21 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 83.43% | 83.21% | +0.22 pp | [-0.92, +1.36 pp] | 0.7013 | 1.0000 |
| main | age | `old - young` | 83.80% | 82.83% | +0.97 pp | [-0.17, +2.11 pp] | 0.0947 | 0.2842 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.16 pp | +20.46 pp | -19.29 pp*** | [-21.57, -17.01 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.04 pp | +3.73 pp | -4.78 pp*** | [-7.05, -2.50 pp] | <0.0001 | 0.0002 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.13 pp | +6.00 pp | -5.86 pp*** | [-8.14, -3.59 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +10.48 pp | +11.14 pp | -0.65 pp | [-2.93, +1.63 pp] | 0.5741 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **91.13%** [90.24, 92.03%] | `close_friend + poor_record` = **86.31%** [85.19, 87.44%] | `stranger + good_record` = **89.97%** [88.95, 90.98%] | `stranger + poor_record` = **65.86%** [64.41, 67.30%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +20.46 pp*** | [+18.62, +22.29 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +1.16 pp | [-0.19, +2.52 pp] | 0.0921 |
| `reliability effect | closeness=stranger` | +24.11 pp*** | [+22.35, +25.88 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +4.82 pp*** | [+3.38, +6.26 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **90.03%** [89.04, 91.02%] | `mayor + poor_record` = **77.95%** [76.71, 79.20%] | `citizen + good_record` = **91.07%** [90.15, 92.00%] | `citizen + poor_record` = **74.22%** [72.87, 75.56%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +3.73 pp*** | [+1.90, +5.57 pp] | <0.0001 |
| `authority effect | reliability=good_record` | -1.04 pp | [-2.40, +0.31 pp] | 0.1317 |
| `reliability effect | authority=citizen` | +16.85 pp*** | [+15.22, +18.49 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +12.08 pp*** | [+10.49, +13.67 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **90.62%** [89.65, 91.58%] | `rich + poor_record` = **79.08%** [77.85, 80.32%] | `poor + good_record` = **90.48%** [89.53, 91.44%] | `poor + poor_record` = **73.09%** [71.73, 74.44%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +6.00 pp*** | [+4.17, +7.83 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | +0.13 pp | [-1.22, +1.49 pp] | 0.8468 |
| `reliability effect | wealth=poor` | +17.40 pp*** | [+15.74, +19.05 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +11.53 pp*** | [+9.97, +13.10 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **89.23%** [88.22, 90.24%] | `close_friend + citizen` = **88.21%** [87.18, 89.24%] | `stranger + mayor` = **78.75%** [77.52, 79.98%] | `stranger + citizen` = **77.08%** [75.81, 78.34%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +11.14 pp*** | [+9.51, +12.77 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +10.48 pp*** | [+8.89, +12.07 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +1.67 pp | [-0.09, +3.44 pp] | 0.0633 |
| `authority effect | closeness=close_friend` | +1.02 pp | [-0.42, +2.46 pp] | 0.1652 |


**Outcome: CHECKED_FALSE (%)** (n=14,966, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.15% | 0.36% | -0.21 pp | [-0.38, -0.05 pp] | 0.0100 | 0.0902 |
| main | authority | `mayor - citizen` | 0.23% | 0.28% | -0.05 pp | [-0.22, +0.11 pp] | 0.5199 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.01% | 0.49% | -0.48 pp*** | [-0.64, -0.32 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.19% | 0.32% | -0.13 pp | [-0.30, +0.03 pp] | 0.1071 | 0.6425 |
| main | gender | `woman - man` | 0.22% | 0.29% | -0.08 pp | [-0.24, +0.09 pp] | 0.3561 | 1.0000 |
| main | age | `old - young` | 0.23% | 0.28% | -0.05 pp | [-0.22, +0.11 pp] | 0.5193 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.03 pp | -0.40 pp | +0.37 pp | [+0.05, +0.70 pp] | 0.0243 | 0.1941 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.03 pp | -0.08 pp | +0.05 pp | [-0.27, +0.38 pp] | 0.7487 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.03 pp | -0.29 pp | +0.32 pp | [-0.00, +0.65 pp] | 0.0531 | 0.3717 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.13 pp | -0.29 pp | +0.16 pp | [-0.17, +0.49 pp] | 0.3348 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.00%** [-0.01, 0.01%] | `close_friend + poor_record` = **0.29%** [0.12, 0.47%] | `stranger + good_record` = **0.03%** [-0.03, 0.08%] | `stranger + poor_record` = **0.69%** [0.42, 0.97%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.40 pp* | [-0.72, -0.08 pp] | 0.0144 |
| `closeness effect | reliability=good_record` | -0.03 pp | [-0.08, +0.03 pp] | 0.3308 |
| `reliability effect | closeness=stranger` | -0.67 pp*** | [-0.94, -0.39 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -0.29 pp*** | [-0.47, -0.12 pp] | 0.0008 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **-0.00%** [-0.01, 0.01%] | `mayor + poor_record` = **0.45%** [0.24, 0.67%] | `citizen + good_record` = **0.03%** [-0.03, 0.08%] | `citizen + poor_record` = **0.53%** [0.29, 0.77%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.08 pp | [-0.40, +0.24 pp] | 0.6251 |
| `authority effect | reliability=good_record` | -0.03 pp | [-0.08, +0.03 pp] | 0.3292 |
| `reliability effect | authority=citizen` | -0.51 pp*** | [-0.75, -0.26 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -0.45 pp*** | [-0.67, -0.24 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.03%** [-0.03, 0.08%] | `rich + poor_record` = **0.35%** [0.16, 0.53%] | `poor + good_record` = **-0.00%** [-0.01, 0.01%] | `poor + poor_record` = **0.64%** [0.38, 0.90%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.29 pp | [-0.62, +0.03 pp] | 0.0722 |
| `wealth effect | reliability=good_record` | +0.03 pp | [-0.03, +0.08 pp] | 0.3298 |
| `reliability effect | wealth=poor` | -0.64 pp*** | [-0.90, -0.38 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -0.32 pp** | [-0.51, -0.13 pp] | 0.0012 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.16%** [0.03, 0.29%] | `close_friend + citizen` = **0.13%** [0.02, 0.25%] | `stranger + mayor` = **0.29%** [0.12, 0.46%] | `stranger + citizen` = **0.43%** [0.21, 0.64%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.29 pp* | [-0.54, -0.05 pp] | 0.0193 |
| `closeness effect | authority=mayor` | -0.13 pp | [-0.35, +0.08 pp] | 0.2184 |
| `authority effect | closeness=stranger` | -0.13 pp | [-0.41, +0.14 pp] | 0.3436 |
| `authority effect | closeness=close_friend` | +0.03 pp | [-0.15, +0.20 pp] | 0.7612 |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=14,849, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8158 | 0.7782 | +0.0376*** | [+0.0264, +0.0489] | <0.0001 | <0.0001 | +0.0376 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.7871 | 0.8069 | -0.0198** | [-0.0310, -0.0085] | 0.0006 | 0.0036 | -0.0198 (p=0.0007) |
| main | reliability | `good_record - poor_record` | 0.8707 | 0.7234 | +0.1473*** | [+0.1360, +0.1586] | <0.0001 | <0.0001 | +0.1473 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8064 | 0.7877 | +0.0187** | [+0.0074, +0.0300] | 0.0012 | 0.0058 | +0.0187 (p=0.0013) |
| main | gender | `woman - man` | 0.7918 | 0.8022 | -0.0105 | [-0.0217, +0.0008] | 0.0691 | 0.2763 | -0.0105 (p=0.0717) |
| main | age | `old - young` | 0.7991 | 0.7949 | +0.0043 | [-0.0070, +0.0155] | 0.4585 | 0.8194 | +0.0043 (p=0.4626) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0054 | +0.0699 | -0.0645*** | [-0.0871, -0.0419] | <0.0001 | <0.0001 | -0.0645 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0119 | -0.0277 | +0.0158 | [-0.0068, +0.0384] | 0.1698 | 0.5094 | +0.0158 (p=0.1733) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0026 | +0.0400 | -0.0426** | [-0.0651, -0.0200] | 0.0002 | 0.0015 | -0.0426 (p=0.0002) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0329 | +0.0424 | -0.0095 | [-0.0320, +0.0131] | 0.4097 | 0.8194 | -0.0095 (p=0.4141) |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.8734** [0.8656, 0.8811] | `close_friend + poor_record` = **0.7583** [0.7452, 0.7714] | `stranger + good_record` = **0.8680** [0.8596, 0.8763] | `stranger + poor_record` = **0.6884** [0.6740, 0.7028]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.0699*** | [+0.0504, +0.0894] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.0054 | [-0.0060, +0.0168] | 0.3530 |
| `reliability effect | closeness=stranger` | +0.1795*** | [+0.1629, +0.1962] | <0.0001 |
| `reliability effect | closeness=close_friend` | +0.1150*** | [+0.0998, +0.1303] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.8647** [0.8563, 0.8731] | `mayor + poor_record` = **0.7095** [0.6954, 0.7237] | `citizen + good_record` = **0.8766** [0.8689, 0.8843] | `citizen + poor_record` = **0.7372** [0.7238, 0.7506]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.0277** | [-0.0471, -0.0082] | 0.0054 |
| `authority effect | reliability=good_record` | -0.0119* | [-0.0233, -0.0005] | 0.0413 |
| `reliability effect | authority=citizen` | +0.1394*** | [+0.1240, +0.1548] | <0.0001 |
| `reliability effect | authority=mayor` | +0.1552*** | [+0.1387, +0.1716] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.8694** [0.8612, 0.8775] | `rich + poor_record` = **0.7434** [0.7296, 0.7571] | `poor + good_record` = **0.8719** [0.8640, 0.8799] | `poor + poor_record` = **0.7034** [0.6896, 0.7172]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.0400*** | [+0.0205, +0.0595] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.0026 | [-0.0140, +0.0088] | 0.6564 |
| `reliability effect | wealth=poor` | +0.1686*** | [+0.1526, +0.1845] | <0.0001 |
| `reliability effect | wealth=rich` | +0.1260*** | [+0.1100, +0.1420] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.8036** [0.7922, 0.8149] | `close_friend + citizen` = **0.8281** [0.8180, 0.8382] | `stranger + mayor` = **0.7707** [0.7588, 0.7826] | `stranger + citizen` = **0.7857** [0.7741, 0.7973]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.0424*** | [+0.0270, +0.0578] | <0.0001 |
| `closeness effect | authority=mayor` | +0.0329*** | [+0.0165, +0.0494] | <0.0001 |
| `authority effect | closeness=stranger` | -0.0150 | [-0.0317, +0.0016] | 0.0766 |
| `authority effect | closeness=close_friend` | -0.0245** | [-0.0397, -0.0093] | 0.0016 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8104 | 0.7720 | +0.0384*** | [+0.0271, +0.0498] | <0.0001 | <0.0001 | +0.0384 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.7837 | 0.7987 | -0.0151* | [-0.0265, -0.0037] | 0.0094 | 0.0468 | -0.0151 (p=0.0101) |
| main | reliability | `good_record - poor_record` | 0.8664 | 0.7160 | +0.1505*** | [+0.1391, +0.1618] | <0.0001 | <0.0001 | +0.1505 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8007 | 0.7817 | +0.0190** | [+0.0076, +0.0304] | 0.0011 | 0.0064 | +0.0190 (p=0.0012) |
| main | gender | `woman - man` | 0.7877 | 0.7947 | -0.0071 | [-0.0184, +0.0043] | 0.2237 | 0.6827 | -0.0071 (p=0.2285) |
| main | age | `old - young` | 0.7932 | 0.7892 | +0.0039 | [-0.0074, +0.0153] | 0.4966 | 0.6827 | +0.0039 (p=0.5009) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0040 | +0.0729 | -0.0689*** | [-0.0917, -0.0462] | <0.0001 | <0.0001 | -0.0689 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0071 | -0.0230 | +0.0159 | [-0.0068, +0.0386] | 0.1707 | 0.6827 | +0.0159 (p=0.1751) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0030 | +0.0410 | -0.0440** | [-0.0667, -0.0212] | 0.0002 | 0.0011 | -0.0440 (p=0.0002) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0327 | +0.0442 | -0.0115 | [-0.0342, +0.0112] | 0.3217 | 0.6827 | -0.0115 (p=0.3266) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.8138 | 0.7762 | +0.0376*** | [+0.0264, +0.0488] | <0.0001 | <0.0001 | +0.0376 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.7860 | 0.8040 | -0.0180** | [-0.0292, -0.0067] | 0.0017 | 0.0085 | -0.0180 (p=0.0019) |
| main | reliability | `good_record - poor_record` | 0.8688 | 0.7211 | +0.1477*** | [+0.1365, +0.1589] | <0.0001 | <0.0001 | +0.1477 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.8043 | 0.7857 | +0.0187** | [+0.0074, +0.0299] | 0.0011 | 0.0067 | +0.0187 (p=0.0012) |
| main | gender | `woman - man` | 0.7904 | 0.7996 | -0.0091 | [-0.0204, +0.0021] | 0.1099 | 0.4396 | -0.0091 (p=0.1133) |
| main | age | `old - young` | 0.7971 | 0.7929 | +0.0041 | [-0.0071, +0.0154] | 0.4683 | 0.7609 | +0.0041 (p=0.4724) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0048 | +0.0704 | -0.0656*** | [-0.0880, -0.0432] | <0.0001 | <0.0001 | -0.0656 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0098 | -0.0261 | +0.0163 | [-0.0061, +0.0387] | 0.1542 | 0.4625 | +0.0163 (p=0.1581) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0027 | +0.0400 | -0.0428** | [-0.0652, -0.0203] | 0.0002 | 0.0013 | -0.0428 (p=0.0002) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0325 | +0.0426 | -0.0100 | [-0.0325, +0.0124] | 0.3805 | 0.7609 | -0.0100 (p=0.3849) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 23.32% | 24.39% | -1.07 pp | [-2.42, +0.28 pp] | 0.1209 | 0.8950 |
| main | authority | `mayor - citizen` | 21.96% | 25.75% | -3.79 pp*** | [-5.14, -2.44 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 21.09% | 26.62% | -5.53 pp*** | [-6.88, -4.18 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 24.11% | 23.60% | +0.51 pp | [-0.84, +1.86 pp] | 0.4613 | 1.0000 |
| main | gender | `woman - man` | 24.02% | 23.69% | +0.33 pp | [-1.02, +1.68 pp] | 0.6339 | 1.0000 |
| main | age | `old - young` | 23.94% | 23.76% | +0.19 pp | [-1.16, +1.54 pp] | 0.7861 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.03 pp | -2.16 pp | +2.19 pp | [-0.51, +4.89 pp] | 0.1119 | 0.8950 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -3.82 pp | -3.77 pp | -0.05 pp | [-2.75, +2.65 pp] | 0.9691 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.93 pp | +0.08 pp | +0.85 pp | [-1.85, +3.55 pp] | 0.5350 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -1.28 pp | -0.85 pp | -0.43 pp | [-3.13, +2.27 pp] | 0.7564 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **21.10%** [19.80, 22.40%] | `close_friend + poor_record` = **25.53%** [24.18, 26.88%] | `stranger + good_record` = **21.07%** [19.74, 22.41%] | `stranger + poor_record` = **27.70%** [26.29, 29.10%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -2.16 pp* | [-4.11, -0.21 pp] | 0.0296 |
| `closeness effect | reliability=good_record` | +0.03 pp | [-1.84, +1.89 pp] | 0.9776 |
| `reliability effect | closeness=stranger` | -6.62 pp*** | [-8.57, -4.68 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -4.43 pp*** | [-6.31, -2.56 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **19.18%** [17.88, 20.47%] | `mayor + poor_record` = **24.73%** [23.42, 26.04%] | `citizen + good_record` = **23.00%** [21.65, 24.34%] | `citizen + poor_record` = **28.50%** [27.05, 29.94%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -3.77 pp*** | [-5.72, -1.82 pp] | 0.0002 |
| `authority effect | reliability=good_record` | -3.82 pp*** | [-5.69, -1.95 pp] | <0.0001 |
| `reliability effect | authority=citizen` | -5.50 pp*** | [-7.48, -3.53 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -5.56 pp*** | [-7.40, -3.71 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **21.55%** [20.25, 22.86%] | `rich + poor_record` = **26.66%** [25.27, 28.04%] | `poor + good_record` = **20.62%** [19.29, 21.95%] | `poor + poor_record` = **26.58%** [25.20, 27.95%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.08 pp | [-1.87, +2.03 pp] | 0.9358 |
| `wealth effect | reliability=good_record` | +0.93 pp | [-0.93, +2.80 pp] | 0.3267 |
| `reliability effect | wealth=poor` | -5.96 pp*** | [-7.87, -4.04 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -5.10 pp*** | [-7.00, -3.20 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **21.31%** [20.02, 22.61%] | `close_friend + citizen` = **25.32%** [23.96, 26.68%] | `stranger + mayor` = **22.60%** [21.29, 23.90%] | `stranger + citizen` = **26.18%** [24.74, 27.61%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.85 pp | [-2.83, +1.12 pp] | 0.3962 |
| `closeness effect | authority=mayor` | -1.28 pp | [-3.12, +0.56 pp] | 0.1725 |
| `authority effect | closeness=stranger` | -3.58 pp*** | [-5.52, -1.64 pp] | 0.0003 |
| `authority effect | closeness=close_friend` | -4.01 pp*** | [-5.88, -2.13 pp] | <0.0001 |


**Outcome: NOT_MENTIONED (%)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.67% | 0.84% | -0.17 pp | [-0.45, +0.10 pp] | 0.2159 | 1.0000 |
| main | authority | `mayor - citizen` | 0.47% | 1.04% | -0.58 pp*** | [-0.85, -0.30 pp] | <0.0001 | 0.0004 |
| main | reliability | `good_record - poor_record` | 0.48% | 1.03% | -0.55 pp*** | [-0.82, -0.27 pp] | <0.0001 | 0.0008 |
| main | wealth | `rich - poor` | 0.72% | 0.79% | -0.07 pp | [-0.34, +0.21 pp] | 0.6313 | 1.0000 |
| main | gender | `woman - man` | 0.55% | 0.96% | -0.42 pp* | [-0.69, -0.14 pp] | 0.0029 | 0.0232 |
| main | age | `old - young` | 0.78% | 0.73% | +0.04 pp | [-0.23, +0.32 pp] | 0.7722 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.16 pp | -0.51 pp | +0.67 pp | [+0.12, +1.22 pp] | 0.0171 | 0.1200 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.54 pp | -0.62 pp | +0.08 pp | [-0.47, +0.63 pp] | 0.7760 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.05 pp | -0.19 pp | +0.24 pp | [-0.31, +0.79 pp] | 0.3912 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.03 pp | -0.32 pp | +0.29 pp | [-0.26, +0.84 pp] | 0.2945 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.56%** [0.32, 0.81%] | `close_friend + poor_record` = **0.78%** [0.50, 1.05%] | `stranger + good_record` = **0.40%** [0.20, 0.60%] | `stranger + poor_record` = **1.28%** [0.93, 1.64%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -0.51 pp* | [-0.96, -0.06 pp] | 0.0267 |
| `closeness effect | reliability=good_record` | +0.16 pp | [-0.16, +0.48 pp] | 0.3202 |
| `reliability effect | closeness=stranger` | -0.88 pp*** | [-1.29, -0.48 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -0.21 pp | [-0.58, +0.16 pp] | 0.2573 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.21%** [0.05, 0.38%] | `mayor + poor_record` = **0.72%** [0.46, 0.99%] | `citizen + good_record` = **0.75%** [0.48, 1.02%] | `citizen + poor_record` = **1.34%** [0.98, 1.70%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.62 pp** | [-1.06, -0.17 pp] | 0.0072 |
| `authority effect | reliability=good_record` | -0.54 pp*** | [-0.85, -0.22 pp] | 0.0009 |
| `reliability effect | authority=citizen` | -0.59 pp* | [-1.04, -0.14 pp] | 0.0108 |
| `reliability effect | authority=mayor` | -0.51 pp** | [-0.82, -0.19 pp] | 0.0015 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.51%** [0.27, 0.74%] | `rich + poor_record` = **0.94%** [0.63, 1.24%] | `poor + good_record` = **0.46%** [0.25, 0.66%] | `poor + poor_record` = **1.12%** [0.80, 1.45%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.19 pp | [-0.64, +0.26 pp] | 0.4133 |
| `wealth effect | reliability=good_record` | +0.05 pp | [-0.26, +0.37 pp] | 0.7432 |
| `reliability effect | wealth=poor` | -0.67 pp*** | [-1.05, -0.28 pp] | 0.0007 |
| `reliability effect | wealth=rich` | -0.43 pp* | [-0.82, -0.04 pp] | 0.0315 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.45%** [0.23, 0.68%] | `close_friend + citizen` = **0.88%** [0.59, 1.18%] | `stranger + mayor` = **0.48%** [0.26, 0.70%] | `stranger + citizen` = **1.20%** [0.86, 1.55%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.32 pp | [-0.77, +0.13 pp] | 0.1644 |
| `closeness effect | authority=mayor` | -0.03 pp | [-0.34, +0.29 pp] | 0.8681 |
| `authority effect | closeness=stranger` | -0.72 pp*** | [-1.13, -0.32 pp] | 0.0005 |
| `authority effect | closeness=close_friend` | -0.43 pp* | [-0.80, -0.06 pp] | 0.0230 |


**Outcome: FACT (%)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 12.64% | 9.41% | +3.23 pp*** | [+2.24, +4.21 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 11.64% | 10.40% | +1.24 pp | [+0.25, +2.22 pp] | 0.0136 | 0.0953 |
| main | reliability | `good_record - poor_record` | 15.62% | 6.43% | +9.19 pp*** | [+8.21, +10.17 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 11.14% | 10.91% | +0.23 pp | [-0.75, +1.21 pp] | 0.6443 | 1.0000 |
| main | gender | `woman - man` | 10.75% | 11.29% | -0.54 pp | [-1.53, +0.44 pp] | 0.2795 | 1.0000 |
| main | age | `old - young` | 11.30% | 10.75% | +0.55 pp | [-0.43, +1.53 pp] | 0.2705 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +2.89 pp | +3.56 pp | -0.67 pp | [-2.63, +1.30 pp] | 0.5052 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +3.14 pp | -0.67 pp | +3.81 pp** | [+1.85, +5.78 pp] | 0.0001 | 0.0011 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.37 pp | +0.83 pp | -1.20 pp | [-3.16, +0.76 pp] | 0.2312 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +3.08 pp | +3.37 pp | -0.29 pp | [-2.25, +1.67 pp] | 0.7718 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **17.06%** [15.87, 18.25%] | `close_friend + poor_record` = **8.21%** [7.36, 9.06%] | `stranger + good_record` = **14.17%** [13.04, 15.30%] | `stranger + poor_record` = **4.65%** [3.98, 5.31%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +3.56 pp*** | [+2.48, +4.64 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +2.89 pp*** | [+1.25, +4.53 pp] | 0.0005 |
| `reliability effect | closeness=stranger` | +9.52 pp*** | [+8.21, +10.83 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +8.85 pp*** | [+7.39, +10.32 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **17.19%** [15.99, 18.39%] | `mayor + poor_record` = **6.09%** [5.33, 6.86%] | `citizen + good_record` = **14.05%** [12.93, 15.16%] | `citizen + poor_record` = **6.76%** [6.00, 7.53%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.67 pp | [-1.75, +0.41 pp] | 0.2243 |
| `authority effect | reliability=good_record` | +3.14 pp*** | [+1.50, +4.78 pp] | 0.0002 |
| `reliability effect | authority=citizen` | +7.28 pp*** | [+5.93, +8.64 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +11.09 pp*** | [+9.67, +12.52 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **15.43%** [14.27, 16.59%] | `rich + poor_record` = **6.84%** [6.08, 7.61%] | `poor + good_record` = **15.80%** [14.64, 16.96%] | `poor + poor_record` = **6.01%** [5.25, 6.78%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.83 pp | [-0.25, +1.91 pp] | 0.1313 |
| `wealth effect | reliability=good_record` | -0.37 pp | [-2.01, +1.27 pp] | 0.6597 |
| `reliability effect | wealth=poor` | +9.79 pp*** | [+8.40, +11.18 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +8.59 pp*** | [+7.20, +9.98 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **13.18%** [12.12, 14.24%] | `close_friend + citizen` = **12.09%** [11.08, 13.10%] | `stranger + mayor` = **10.10%** [9.15, 11.05%] | `stranger + citizen` = **8.72%** [7.81, 9.62%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +3.37 pp*** | [+2.02, +4.73 pp] | <0.0001 |
| `closeness effect | authority=mayor` | +3.08 pp*** | [+1.66, +4.50 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +1.38 pp* | [+0.07, +2.69 pp] | 0.0389 |
| `authority effect | closeness=close_friend` | +1.09 pp | [-0.37, +2.55 pp] | 0.1436 |


**Outcome: UNCERTAIN (%)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 11.90% | 12.20% | -0.30 pp | [-1.34, +0.73 pp] | 0.5662 | 1.0000 |
| main | authority | `mayor - citizen` | 12.96% | 11.14% | +1.82 pp** | [+0.79, +2.86 pp] | 0.0005 | 0.0049 |
| main | reliability | `good_record - poor_record` | 18.34% | 5.76% | +12.58 pp*** | [+11.55, +13.62 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 12.49% | 11.62% | +0.87 pp | [-0.16, +1.91 pp] | 0.0976 | 0.5855 |
| main | gender | `woman - man` | 12.20% | 11.90% | +0.30 pp | [-0.73, +1.34 pp] | 0.5681 | 1.0000 |
| main | age | `old - young` | 11.97% | 12.14% | -0.17 pp | [-1.20, +0.86 pp] | 0.7495 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -1.28 pp | +0.67 pp | -1.95 pp | [-4.02, +0.12 pp] | 0.0644 | 0.4505 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +3.20 pp | +0.45 pp | +2.74 pp | [+0.68, +4.81 pp] | 0.0093 | 0.0745 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +1.61 pp | +0.14 pp | +1.48 pp | [-0.59, +3.54 pp] | 0.1617 | 0.8083 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.69 pp | +0.08 pp | -0.77 pp | [-2.83, +1.30 pp] | 0.4669 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **17.71%** [16.48, 18.93%] | `close_friend + poor_record` = **6.10%** [5.32, 6.87%] | `stranger + good_record` = **18.98%** [17.70, 20.27%] | `stranger + poor_record` = **5.42%** [4.71, 6.14%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.67 pp | [-0.38, +1.73 pp] | 0.2117 |
| `closeness effect | reliability=good_record` | -1.28 pp | [-3.05, +0.50 pp] | 0.1587 |
| `reliability effect | closeness=stranger` | +13.56 pp*** | [+12.09, +15.03 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | +11.61 pp*** | [+10.16, +13.06 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **19.94%** [18.60, 21.28%] | `mayor + poor_record` = **5.99%** [5.24, 6.73%] | `citizen + good_record` = **16.75%** [15.58, 17.91%] | `citizen + poor_record` = **5.53%** [4.79, 6.28%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +0.45 pp | [-0.60, +1.51 pp] | 0.4006 |
| `authority effect | reliability=good_record` | +3.20 pp*** | [+1.42, +4.97 pp] | 0.0004 |
| `reliability effect | authority=citizen` | +11.21 pp*** | [+9.83, +12.60 pp] | <0.0001 |
| `reliability effect | authority=mayor` | +13.96 pp*** | [+12.42, +15.49 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **19.15%** [17.86, 20.44%] | `rich + poor_record` = **5.83%** [5.06, 6.59%] | `poor + good_record` = **17.54%** [16.32, 18.76%] | `poor + poor_record` = **5.69%** [4.97, 6.42%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +0.14 pp | [-0.92, +1.19 pp] | 0.8013 |
| `wealth effect | reliability=good_record` | +1.61 pp | [-0.17, +3.39 pp] | 0.0755 |
| `reliability effect | wealth=poor` | +11.85 pp*** | [+10.42, +13.27 pp] | <0.0001 |
| `reliability effect | wealth=rich` | +13.32 pp*** | [+11.82, +14.82 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **12.62%** [11.55, 13.69%] | `close_friend + citizen` = **11.18%** [10.20, 12.16%] | `stranger + mayor` = **13.31%** [12.21, 14.41%] | `stranger + citizen` = **11.10%** [10.12, 12.08%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +0.08 pp | [-1.31, +1.47 pp] | 0.9087 |
| `closeness effect | authority=mayor` | -0.69 pp | [-2.22, +0.85 pp] | 0.3805 |
| `authority effect | closeness=stranger` | +2.21 pp** | [+0.74, +3.68 pp] | 0.0033 |
| `authority effect | closeness=close_friend` | +1.44 pp | [-0.01, +2.89 pp] | 0.0518 |


**Outcome: SKEPTICAL (%)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 11.79% | 15.43% | -3.64 pp*** | [-4.68, -2.59 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 14.19% | 13.03% | +1.16 pp | [+0.11, +2.20 pp] | 0.0298 | 0.1193 |
| main | reliability | `good_record - poor_record` | 3.69% | 23.53% | -19.84 pp*** | [-20.89, -18.80 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 12.52% | 14.70% | -2.18 pp*** | [-3.22, -1.13 pp] | <0.0001 | 0.0003 |
| main | gender | `woman - man` | 14.04% | 13.19% | +0.85 pp | [-0.20, +1.89 pp] | 0.1110 | 0.3331 |
| main | age | `old - young` | 13.48% | 13.74% | -0.26 pp | [-1.30, +0.79 pp] | 0.6296 | 0.8054 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.05 pp | -7.33 pp | +7.39 pp*** | [+5.30, +9.48 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.38 pp | +2.69 pp | -3.07 pp* | [-5.16, -0.98 pp] | 0.0040 | 0.0200 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.53 pp | -3.82 pp | +3.28 pp* | [+1.19, +5.37 pp] | 0.0021 | 0.0124 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -3.19 pp | -4.08 pp | +0.89 pp | [-1.20, +2.98 pp] | 0.4027 | 0.8054 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **3.72%** [3.13, 4.30%] | `close_friend + poor_record` = **19.86%** [18.61, 21.12%] | `stranger + good_record` = **3.66%** [3.09, 4.24%] | `stranger + poor_record` = **27.20%** [25.74, 28.65%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | -7.33 pp*** | [-9.25, -5.41 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | +0.05 pp | [-0.77, +0.88 pp] | 0.8962 |
| `reliability effect | closeness=stranger` | -23.54 pp*** | [-25.10, -21.97 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -16.15 pp*** | [-17.53, -14.76 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **3.50%** [2.92, 4.08%] | `mayor + poor_record` = **24.88%** [23.47, 26.29%] | `citizen + good_record` = **3.88%** [3.30, 4.46%] | `citizen + poor_record` = **22.19%** [20.88, 23.49%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | +2.69 pp** | [+0.77, +4.61 pp] | 0.0060 |
| `authority effect | reliability=good_record` | -0.38 pp | [-1.20, +0.45 pp] | 0.3698 |
| `reliability effect | authority=citizen` | -18.31 pp*** | [-19.74, -16.88 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -21.38 pp*** | [-22.90, -19.85 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **3.42%** [2.85, 3.99%] | `rich + poor_record` = **21.62%** [20.29, 22.96%] | `poor + good_record` = **3.96%** [3.36, 4.55%] | `poor + poor_record` = **25.44%** [24.06, 26.82%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -3.82 pp*** | [-5.74, -1.90 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | -0.53 pp | [-1.36, +0.29 pp] | 0.2036 |
| `reliability effect | wealth=poor` | -21.48 pp*** | [-22.99, -19.98 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -18.20 pp*** | [-19.65, -16.75 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **12.59%** [11.56, 13.62%] | `close_friend + citizen` = **10.99%** [10.07, 11.91%] | `stranger + mayor` = **15.79%** [14.66, 16.91%] | `stranger + citizen` = **15.07%** [13.99, 16.16%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -4.08 pp*** | [-5.51, -2.66 pp] | <0.0001 |
| `closeness effect | authority=mayor` | -3.19 pp*** | [-4.72, -1.67 pp] | <0.0001 |
| `authority effect | closeness=stranger` | +0.71 pp | [-0.85, +2.28 pp] | 0.3726 |
| `authority effect | closeness=close_friend` | +1.60 pp* | [+0.22, +2.99 pp] | 0.0232 |


**Outcome: CHECKED_TRUE (%)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 62.46% | 61.69% | +0.77 pp | [-0.77, +2.30 pp] | 0.3269 | 1.0000 |
| main | authority | `mayor - citizen` | 60.24% | 63.90% | -3.66 pp*** | [-5.19, -2.12 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 61.85% | 62.29% | -0.43 pp | [-1.97, +1.10 pp] | 0.5790 | 1.0000 |
| main | wealth | `rich - poor` | 62.69% | 61.46% | +1.23 pp | [-0.30, +2.77 pp] | 0.1161 | 0.6965 |
| main | gender | `woman - man` | 61.91% | 62.23% | -0.31 pp | [-1.85, +1.22 pp] | 0.6883 | 1.0000 |
| main | age | `old - young` | 62.04% | 62.11% | -0.07 pp | [-1.61, +1.46 pp] | 0.9253 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -1.86 pp | +3.39 pp | -5.25 pp** | [-8.32, -2.18 pp] | 0.0008 | 0.0072 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -5.45 pp | -1.86 pp | -3.59 pp | [-6.66, -0.52 pp] | 0.0218 | 0.1526 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.74 pp | +3.20 pp | -3.93 pp | [-7.00, -0.86 pp] | 0.0120 | 0.0962 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.53 pp | +1.01 pp | -0.48 pp | [-3.55, +2.59 pp] | 0.7612 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **60.93%** [59.44, 62.41%] | `close_friend + poor_record` = **63.99%** [62.44, 65.53%] | `stranger + good_record` = **62.78%** [61.20, 64.37%] | `stranger + poor_record` = **60.59%** [59.07, 62.11%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +3.39 pp** | [+1.22, +5.56 pp] | 0.0022 |
| `closeness effect | reliability=good_record` | -1.86 pp | [-4.03, +0.32 pp] | 0.0942 |
| `reliability effect | closeness=stranger` | +2.19 pp | [-0.01, +4.39 pp] | 0.0507 |
| `reliability effect | closeness=close_friend` | -3.06 pp** | [-5.20, -0.91 pp] | 0.0052 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **59.13%** [57.55, 60.71%] | `mayor + poor_record` = **61.36%** [59.78, 62.94%] | `citizen + good_record` = **64.58%** [63.09, 66.08%] | `citizen + poor_record` = **63.22%** [61.74, 64.70%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -1.86 pp | [-4.03, +0.31 pp] | 0.0926 |
| `authority effect | reliability=good_record` | -5.45 pp*** | [-7.63, -3.28 pp] | <0.0001 |
| `reliability effect | authority=citizen` | +1.36 pp | [-0.74, +3.47 pp] | 0.2051 |
| `reliability effect | authority=mayor` | -2.23 pp | [-4.46, +0.00 pp] | 0.0502 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **61.49%** [59.95, 63.03%] | `rich + poor_record` = **63.89%** [62.34, 65.43%] | `poor + good_record` = **62.22%** [60.69, 63.76%] | `poor + poor_record` = **60.69%** [59.17, 62.21%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | +3.20 pp** | [+1.03, +5.37 pp] | 0.0038 |
| `wealth effect | reliability=good_record` | -0.74 pp | [-2.91, +1.44 pp] | 0.5069 |
| `reliability effect | wealth=poor` | +1.53 pp | [-0.63, +3.69 pp] | 0.1645 |
| `reliability effect | wealth=rich` | -2.40 pp* | [-4.58, -0.22 pp] | 0.0309 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **60.51%** [58.93, 62.09%] | `close_friend + citizen` = **64.40%** [62.95, 65.86%] | `stranger + mayor` = **59.98%** [58.40, 61.56%] | `stranger + citizen` = **63.40%** [61.87, 64.92%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | +1.01 pp | [-1.10, +3.11 pp] | 0.3494 |
| `closeness effect | authority=mayor` | +0.53 pp | [-1.70, +2.76 pp] | 0.6419 |
| `authority effect | closeness=stranger` | -3.42 pp** | [-5.61, -1.22 pp] | 0.0023 |
| `authority effect | closeness=close_friend` | -3.89 pp*** | [-6.04, -1.75 pp] | 0.0004 |


**Outcome: CHECKED_FALSE (%)** (n=14,962, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.55% | 0.43% | +0.12 pp | [-0.10, +0.34 pp] | 0.2763 | 1.0000 |
| main | authority | `mayor - citizen` | 0.49% | 0.48% | +0.01 pp | [-0.20, +0.23 pp] | 0.9036 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.01% | 0.96% | -0.95 pp*** | [-1.17, -0.73 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.44% | 0.53% | -0.09 pp | [-0.31, +0.12 pp] | 0.3999 | 1.0000 |
| main | gender | `woman - man` | 0.55% | 0.43% | +0.12 pp | [-0.10, +0.34 pp] | 0.2714 | 1.0000 |
| main | age | `old - young` | 0.44% | 0.53% | -0.09 pp | [-0.31, +0.12 pp] | 0.3971 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.03 pp | +0.21 pp | -0.19 pp | [-0.62, +0.25 pp] | 0.3969 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.03 pp | -0.00 pp | +0.03 pp | [-0.41, +0.46 pp] | 0.9028 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.03 pp | -0.16 pp | +0.13 pp | [-0.30, +0.57 pp] | 0.5470 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.29 pp | -0.05 pp | +0.35 pp | [-0.09, +0.78 pp] | 0.1164 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Means & Simple Comparisons (CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` = **0.03%** [-0.03, 0.08%] | `close_friend + poor_record` = **1.07%** [0.75, 1.39%] | `stranger + good_record` = **-0.00%** [-0.01, 0.01%] | `stranger + poor_record` = **0.85%** [0.57, 1.14%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | reliability=poor_record` | +0.21 pp | [-0.22, +0.65 pp] | 0.3294 |
| `closeness effect | reliability=good_record` | +0.03 pp | [-0.03, +0.08 pp] | 0.3282 |
| `reliability effect | closeness=stranger` | -0.86 pp*** | [-1.14, -0.57 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | -1.04 pp*** | [-1.37, -0.72 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` = **0.03%** [-0.03, 0.08%] | `mayor + poor_record` = **0.96%** [0.66, 1.27%] | `citizen + good_record` = **-0.00%** [-0.01, 0.01%] | `citizen + poor_record` = **0.96%** [0.66, 1.27%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `authority effect | reliability=poor_record` | -0.00 pp | [-0.43, +0.43 pp] | 0.9996 |
| `authority effect | reliability=good_record` | +0.03 pp | [-0.03, +0.08 pp] | 0.3245 |
| `reliability effect | authority=citizen` | -0.96 pp*** | [-1.27, -0.66 pp] | <0.0001 |
| `reliability effect | authority=mayor` | -0.94 pp*** | [-1.24, -0.63 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` = **0.00%** [-0.01, 0.01%] | `rich + poor_record` = **0.88%** [0.59, 1.17%] | `poor + good_record` = **0.03%** [-0.03, 0.08%] | `poor + poor_record` = **1.04%** [0.73, 1.36%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `wealth effect | reliability=poor_record` | -0.16 pp | [-0.59, +0.27 pp] | 0.4669 |
| `wealth effect | reliability=good_record` | -0.03 pp | [-0.08, +0.03 pp] | 0.3319 |
| `reliability effect | wealth=poor` | -1.02 pp*** | [-1.34, -0.69 pp] | <0.0001 |
| `reliability effect | wealth=rich` | -0.88 pp*** | [-1.17, -0.59 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` = **0.64%** [0.39, 0.89%] | `close_friend + citizen` = **0.45%** [0.24, 0.66%] | `stranger + mayor` = **0.35%** [0.16, 0.53%] | `stranger + citizen` = **0.51%** [0.29, 0.73%]

| Conditional Comparison | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|
| `closeness effect | authority=citizen` | -0.05 pp | [-0.36, +0.25 pp] | 0.7314 |
| `closeness effect | authority=mayor` | +0.29 pp | [-0.01, +0.60 pp] | 0.0620 |
| `authority effect | closeness=stranger` | -0.16 pp | [-0.45, +0.13 pp] | 0.2748 |
| `authority effect | closeness=close_friend` | +0.19 pp | [-0.14, +0.51 pp] | 0.2583 |


---

## 4. Top 10 Strongest & Bottom 10 Weakest Source DNAs (All Labels & Metrics)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.9364** | 0.936 | 75.4% | 24.6% | 5.4% | 10.1% | 1.1% | 83.2% | 0.2% | 0.0% |
| 2 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9324** | 0.932 | 79.3% | 20.7% | 6.9% | 11.8% | 0.9% | 80.5% | 0.0% | 0.0% |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | **0.9260** | 0.926 | 79.7% | 20.3% | 4.3% | 10.9% | 1.7% | 82.8% | 0.2% | 0.0% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **0.9213** | 0.921 | 75.4% | 24.6% | 5.6% | 12.3% | 1.7% | 80.4% | 0.0% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.9186** | 0.919 | 81.4% | 18.6% | 9.4% | 9.9% | 3.2% | 77.5% | 0.0% | 0.0% |
| 6 | 22 | close_friend / citizen / good_record / poor / man_young | **0.9152** | 0.915 | 78.8% | 21.2% | 7.7% | 13.1% | 1.9% | 77.3% | 0.0% | 0.0% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.9147** | 0.915 | 79.7% | 20.3% | 8.4% | 14.0% | 1.5% | 76.0% | 0.0% | 0.0% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **0.9133** | 0.913 | 79.3% | 20.7% | 6.4% | 13.9% | 1.7% | 77.9% | 0.0% | 0.0% |
| 9 | 18 | close_friend / citizen / good_record / rich / man_young | **0.9118** | 0.912 | 77.6% | 22.4% | 6.0% | 12.0% | 2.6% | 79.1% | 0.2% | 0.0% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.9101** | 0.910 | 79.9% | 20.1% | 9.6% | 11.1% | 3.2% | 75.8% | 0.2% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.2650** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **0.2693** | 0.269 | 23.7% | 76.3% | 0.4% | 5.8% | 70.0% | 23.6% | 0.2% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **0.2828** | 0.283 | 25.6% | 74.4% | 1.7% | 6.7% | 68.4% | 23.2% | 0.0% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.3063** | 0.306 | 26.5% | 73.5% | 1.1% | 9.7% | 64.3% | 24.7% | 0.2% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.3141** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **0.3499** | 0.350 | 30.1% | 69.9% | 2.4% | 8.6% | 60.5% | 28.3% | 0.2% | 0.0% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **0.3654** | 0.365 | 31.0% | 69.0% | 1.7% | 9.8% | 58.5% | 29.9% | 0.0% | 0.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.3788** | 0.379 | 34.0% | 66.0% | 1.7% | 8.8% | 57.3% | 31.8% | 0.4% | 0.0% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.3860** | 0.386 | 33.8% | 66.2% | 2.2% | 6.7% | 57.4% | 33.1% | 0.6% | 0.0% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | **0.3925** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **76.9%** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **76.3%** | 0.269 | 23.7% | 76.3% | 0.4% | 5.8% | 70.0% | 23.6% | 0.2% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **74.4%** | 0.283 | 25.6% | 74.4% | 1.7% | 6.7% | 68.4% | 23.2% | 0.0% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **73.5%** | 0.306 | 26.5% | 73.5% | 1.1% | 9.7% | 64.3% | 24.7% | 0.2% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **72.2%** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **69.9%** | 0.350 | 30.1% | 69.9% | 2.4% | 8.6% | 60.5% | 28.3% | 0.2% | 0.0% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **69.0%** | 0.365 | 31.0% | 69.0% | 1.7% | 9.8% | 58.5% | 29.9% | 0.0% | 0.0% |
| 8 | 60 | stranger / citizen / poor_record / rich / man_old | **66.2%** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **66.2%** | 0.386 | 33.8% | 66.2% | 2.2% | 6.7% | 57.4% | 33.1% | 0.6% | 0.0% |
| 10 | 47 | stranger / mayor / poor_record / poor / woman_young | **66.0%** | 0.379 | 34.0% | 66.0% | 1.7% | 8.8% | 57.3% | 31.8% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **17.9%** | 0.899 | 82.1% | 17.9% | 9.0% | 13.7% | 3.2% | 74.0% | 0.0% | 0.0% |
| 2 | 19 | close_friend / citizen / good_record / rich / woman_young | **18.6%** | 0.919 | 81.4% | 18.6% | 9.4% | 9.9% | 3.2% | 77.5% | 0.0% | 0.0% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | **20.1%** | 0.910 | 79.9% | 20.1% | 9.6% | 11.1% | 3.2% | 75.8% | 0.2% | 0.0% |
| 4 | 51 | stranger / citizen / good_record / rich / woman_young | **20.3%** | 0.926 | 79.7% | 20.3% | 4.3% | 10.9% | 1.7% | 82.8% | 0.2% | 0.0% |
| 5 | 21 | close_friend / citizen / good_record / poor / woman_old | **20.3%** | 0.915 | 79.7% | 20.3% | 8.4% | 14.0% | 1.5% | 76.0% | 0.0% | 0.0% |
| 6 | 7 | close_friend / mayor / good_record / poor / woman_young | **20.5%** | 0.900 | 79.5% | 20.5% | 9.3% | 14.9% | 2.6% | 73.2% | 0.0% | 0.0% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **20.5%** | 0.894 | 79.5% | 20.5% | 8.2% | 16.1% | 2.4% | 73.2% | 0.2% | 0.0% |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | **20.7%** | 0.932 | 79.3% | 20.7% | 6.9% | 11.8% | 0.9% | 80.5% | 0.0% | 0.0% |
| 9 | 33 | stranger / mayor / good_record / rich / woman_old | **20.7%** | 0.913 | 79.3% | 20.7% | 6.4% | 13.9% | 1.7% | 77.9% | 0.0% | 0.0% |
| 10 | 24 | close_friend / citizen / good_record / poor / man_old | **20.7%** | 0.910 | 79.3% | 20.7% | 6.9% | 13.3% | 2.1% | 77.5% | 0.2% | 0.0% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | close_friend / mayor / good_record / rich / woman_old | **11.4%** | 0.902 | 75.0% | 25.0% | 11.4% | 15.2% | 2.1% | 71.2% | 0.0% | 0.0% |
| 2 | 4 | close_friend / mayor / good_record / rich / man_old | **11.2%** | 0.888 | 71.8% | 28.2% | 11.2% | 15.0% | 3.6% | 70.0% | 0.0% | 0.2% |
| 3 | 6 | close_friend / mayor / good_record / poor / man_young | **10.5%** | 0.876 | 76.7% | 23.3% | 10.5% | 16.3% | 4.3% | 68.9% | 0.0% | 0.0% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | **9.6%** | 0.910 | 79.9% | 20.1% | 9.6% | 11.1% | 3.2% | 75.8% | 0.2% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **9.4%** | 0.919 | 81.4% | 18.6% | 9.4% | 9.9% | 3.2% | 77.5% | 0.0% | 0.0% |
| 6 | 7 | close_friend / mayor / good_record / poor / woman_young | **9.3%** | 0.900 | 79.5% | 20.5% | 9.3% | 14.9% | 2.6% | 73.2% | 0.0% | 0.0% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | **9.0%** | 0.899 | 82.1% | 17.9% | 9.0% | 13.7% | 3.2% | 74.0% | 0.0% | 0.0% |
| 8 | 3 | close_friend / mayor / good_record / rich / woman_young | **8.6%** | 0.899 | 75.9% | 24.1% | 8.6% | 13.7% | 3.2% | 74.5% | 0.0% | 0.0% |
| 9 | 21 | close_friend / citizen / good_record / poor / woman_old | **8.4%** | 0.915 | 79.7% | 20.3% | 8.4% | 14.0% | 1.5% | 76.0% | 0.0% | 0.0% |
| 10 | 8 | close_friend / mayor / good_record / poor / man_old | **8.2%** | 0.894 | 79.5% | 20.5% | 8.2% | 16.1% | 2.4% | 73.2% | 0.2% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **0.4%** | 0.269 | 23.7% | 76.3% | 0.4% | 5.8% | 70.0% | 23.6% | 0.2% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.9%** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |
| 3 | 58 | stranger / citizen / poor_record / rich / man_young | **0.9%** | 0.404 | 36.1% | 63.9% | 0.9% | 4.9% | 55.7% | 37.0% | 1.3% | 0.2% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.1%** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **1.1%** | 0.306 | 26.5% | 73.5% | 1.1% | 9.7% | 64.3% | 24.7% | 0.2% | 0.0% |
| 6 | 43 | stranger / mayor / poor_record / rich / woman_young | **1.5%** | 0.453 | 38.5% | 61.5% | 1.5% | 11.1% | 48.6% | 38.1% | 0.4% | 0.2% |
| 7 | 32 | close_friend / citizen / poor_record / poor / man_old | **1.5%** | 0.508 | 44.0% | 56.0% | 1.5% | 9.2% | 44.0% | 44.6% | 0.6% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **1.7%** | 0.365 | 31.0% | 69.0% | 1.7% | 9.8% | 58.5% | 29.9% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **1.7%** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |
| 10 | 47 | stranger / mayor / poor_record / poor / woman_young | **1.7%** | 0.379 | 34.0% | 66.0% | 1.7% | 8.8% | 57.3% | 31.8% | 0.4% | 0.0% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 40 | stranger / mayor / good_record / poor / man_old | **19.5%** | 0.879 | 72.4% | 27.6% | 5.6% | 19.5% | 2.1% | 72.5% | 0.2% | 0.0% |
| 2 | 38 | stranger / mayor / good_record / poor / man_young | **17.3%** | 0.881 | 72.9% | 27.1% | 6.0% | 17.3% | 3.0% | 73.4% | 0.2% | 0.0% |
| 3 | 37 | stranger / mayor / good_record / poor / woman_old | **17.3%** | 0.881 | 73.1% | 26.9% | 6.0% | 17.3% | 3.2% | 73.5% | 0.0% | 0.0% |
| 4 | 53 | stranger / citizen / good_record / poor / woman_old | **17.0%** | 0.892 | 73.3% | 26.7% | 6.0% | 17.0% | 2.1% | 74.7% | 0.2% | 0.0% |
| 5 | 56 | stranger / citizen / good_record / poor / man_old | **17.0%** | 0.887 | 73.7% | 26.3% | 5.6% | 17.0% | 2.8% | 74.7% | 0.0% | 0.0% |
| 6 | 6 | close_friend / mayor / good_record / poor / man_young | **16.3%** | 0.876 | 76.7% | 23.3% | 10.5% | 16.3% | 4.3% | 68.9% | 0.0% | 0.0% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **16.1%** | 0.894 | 79.5% | 20.5% | 8.2% | 16.1% | 2.4% | 73.2% | 0.2% | 0.0% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | **15.9%** | 0.886 | 73.5% | 26.5% | 7.7% | 15.9% | 3.4% | 73.0% | 0.0% | 0.0% |
| 9 | 39 | stranger / mayor / good_record / poor / woman_young | **15.8%** | 0.889 | 75.4% | 24.6% | 7.1% | 15.8% | 3.2% | 73.7% | 0.0% | 0.2% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | **15.5%** | 0.903 | 76.1% | 23.9% | 6.0% | 15.5% | 1.9% | 76.3% | 0.0% | 0.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **4.9%** | 0.404 | 36.1% | 63.9% | 0.9% | 4.9% | 55.7% | 37.0% | 1.3% | 0.2% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **5.8%** | 0.269 | 23.7% | 76.3% | 0.4% | 5.8% | 70.0% | 23.6% | 0.2% | 0.0% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | **6.0%** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 4 | 41 | stranger / mayor / poor_record / rich / woman_old | **6.0%** | 0.419 | 37.8% | 62.2% | 2.8% | 6.0% | 54.7% | 36.1% | 0.2% | 0.2% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | **6.0%** | 0.408 | 37.2% | 62.8% | 2.8% | 6.0% | 55.4% | 35.0% | 0.9% | 0.0% |
| 6 | 59 | stranger / citizen / poor_record / rich / woman_young | **6.2%** | 0.463 | 40.4% | 59.6% | 2.1% | 6.2% | 50.0% | 41.0% | 0.4% | 0.2% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **6.7%** | 0.386 | 33.8% | 66.2% | 2.2% | 6.7% | 57.4% | 33.1% | 0.6% | 0.0% |
| 8 | 62 | stranger / citizen / poor_record / poor / man_young | **6.7%** | 0.283 | 25.6% | 74.4% | 1.7% | 6.7% | 68.4% | 23.2% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **7.5%** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |
| 10 | 61 | stranger / citizen / poor_record / poor / woman_old | **7.5%** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **70.0%** | 0.269 | 23.7% | 76.3% | 0.4% | 5.8% | 70.0% | 23.6% | 0.2% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **69.1%** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **68.4%** | 0.283 | 25.6% | 74.4% | 1.7% | 6.7% | 68.4% | 23.2% | 0.0% | 0.0% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **64.5%** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **64.3%** | 0.306 | 26.5% | 73.5% | 1.1% | 9.7% | 64.3% | 24.7% | 0.2% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **60.5%** | 0.350 | 30.1% | 69.9% | 2.4% | 8.6% | 60.5% | 28.3% | 0.2% | 0.0% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **58.5%** | 0.365 | 31.0% | 69.0% | 1.7% | 9.8% | 58.5% | 29.9% | 0.0% | 0.0% |
| 8 | 57 | stranger / citizen / poor_record / rich / woman_old | **57.4%** | 0.386 | 33.8% | 66.2% | 2.2% | 6.7% | 57.4% | 33.1% | 0.6% | 0.0% |
| 9 | 47 | stranger / mayor / poor_record / poor / woman_young | **57.3%** | 0.379 | 34.0% | 66.0% | 1.7% | 8.8% | 57.3% | 31.8% | 0.4% | 0.0% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | **56.7%** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9%** | 0.932 | 79.3% | 20.7% | 6.9% | 11.8% | 0.9% | 80.5% | 0.0% | 0.0% |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | **1.1%** | 0.936 | 75.4% | 24.6% | 5.4% | 10.1% | 1.1% | 83.2% | 0.2% | 0.0% |
| 3 | 21 | close_friend / citizen / good_record / poor / woman_old | **1.5%** | 0.915 | 79.7% | 20.3% | 8.4% | 14.0% | 1.5% | 76.0% | 0.0% | 0.0% |
| 4 | 33 | stranger / mayor / good_record / rich / woman_old | **1.7%** | 0.913 | 79.3% | 20.7% | 6.4% | 13.9% | 1.7% | 77.9% | 0.0% | 0.0% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **1.7%** | 0.926 | 79.7% | 20.3% | 4.3% | 10.9% | 1.7% | 82.8% | 0.2% | 0.0% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **1.7%** | 0.921 | 75.4% | 24.6% | 5.6% | 12.3% | 1.7% | 80.4% | 0.0% | 0.0% |
| 7 | 22 | close_friend / citizen / good_record / poor / man_young | **1.9%** | 0.915 | 78.8% | 21.2% | 7.7% | 13.1% | 1.9% | 77.3% | 0.0% | 0.0% |
| 8 | 55 | stranger / citizen / good_record / poor / woman_young | **1.9%** | 0.903 | 76.1% | 23.9% | 6.0% | 15.5% | 1.9% | 76.3% | 0.0% | 0.2% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | **2.1%** | 0.910 | 79.3% | 20.7% | 6.9% | 13.3% | 2.1% | 77.5% | 0.2% | 0.0% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **2.1%** | 0.902 | 75.0% | 25.0% | 11.4% | 15.2% | 2.1% | 71.2% | 0.0% | 0.0% |


**CHECKED_TRUE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **83.2%** | 0.936 | 75.4% | 24.6% | 5.4% | 10.1% | 1.1% | 83.2% | 0.2% | 0.0% |
| 2 | 51 | stranger / citizen / good_record / rich / woman_young | **82.8%** | 0.926 | 79.7% | 20.3% | 4.3% | 10.9% | 1.7% | 82.8% | 0.2% | 0.0% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | **80.5%** | 0.932 | 79.3% | 20.7% | 6.9% | 11.8% | 0.9% | 80.5% | 0.0% | 0.0% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **80.4%** | 0.921 | 75.4% | 24.6% | 5.6% | 12.3% | 1.7% | 80.4% | 0.0% | 0.0% |
| 5 | 35 | stranger / mayor / good_record / rich / woman_young | **79.7%** | 0.909 | 77.1% | 22.9% | 4.5% | 13.4% | 2.4% | 79.7% | 0.0% | 0.0% |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | **79.1%** | 0.912 | 77.6% | 22.4% | 6.0% | 12.0% | 2.6% | 79.1% | 0.2% | 0.0% |
| 7 | 33 | stranger / mayor / good_record / rich / woman_old | **77.9%** | 0.913 | 79.3% | 20.7% | 6.4% | 13.9% | 1.7% | 77.9% | 0.0% | 0.0% |
| 8 | 19 | close_friend / citizen / good_record / rich / woman_young | **77.5%** | 0.919 | 81.4% | 18.6% | 9.4% | 9.9% | 3.2% | 77.5% | 0.0% | 0.0% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | **77.5%** | 0.910 | 79.3% | 20.7% | 6.9% | 13.3% | 2.1% | 77.5% | 0.2% | 0.0% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | **77.3%** | 0.915 | 78.8% | 21.2% | 7.7% | 13.1% | 1.9% | 77.3% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **21.9%** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |
| 2 | 62 | stranger / citizen / poor_record / poor / man_young | **23.2%** | 0.283 | 25.6% | 74.4% | 1.7% | 6.7% | 68.4% | 23.2% | 0.0% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **23.6%** | 0.269 | 23.7% | 76.3% | 0.4% | 5.8% | 70.0% | 23.6% | 0.2% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **24.7%** | 0.306 | 26.5% | 73.5% | 1.1% | 9.7% | 64.3% | 24.7% | 0.2% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **27.4%** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **28.3%** | 0.350 | 30.1% | 69.9% | 2.4% | 8.6% | 60.5% | 28.3% | 0.2% | 0.0% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **29.9%** | 0.365 | 31.0% | 69.0% | 1.7% | 9.8% | 58.5% | 29.9% | 0.0% | 0.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **31.8%** | 0.379 | 34.0% | 66.0% | 1.7% | 8.8% | 57.3% | 31.8% | 0.4% | 0.0% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **33.1%** | 0.386 | 33.8% | 66.2% | 2.2% | 6.7% | 57.4% | 33.1% | 0.6% | 0.0% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | **33.6%** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |


**CHECKED_FALSE (%)** *(Note: 29 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **1.3%** | 0.404 | 36.1% | 63.9% | 0.9% | 4.9% | 55.7% | 37.0% | 1.3% | 0.2% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.1%** | 0.314 | 27.8% | 72.2% | 1.1% | 6.0% | 64.5% | 27.4% | 1.1% | 0.0% |
| 3 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.9%** | 0.576 | 49.4% | 50.6% | 3.9% | 10.0% | 36.6% | 48.7% | 0.9% | 0.0% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.9%** | 0.520 | 45.3% | 54.7% | 2.6% | 10.8% | 41.7% | 44.1% | 0.9% | 0.0% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | **0.9%** | 0.408 | 37.2% | 62.8% | 2.8% | 6.0% | 55.4% | 35.0% | 0.9% | 0.0% |
| 6 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.6%** | 0.568 | 51.5% | 48.5% | 4.3% | 8.0% | 38.6% | 48.5% | 0.6% | 0.0% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.6%** | 0.386 | 33.8% | 66.2% | 2.2% | 6.7% | 57.4% | 33.1% | 0.6% | 0.0% |
| 8 | 32 | close_friend / citizen / poor_record / poor / man_old | **0.6%** | 0.508 | 44.0% | 56.0% | 1.5% | 9.2% | 44.0% | 44.6% | 0.6% | 0.0% |
| 9 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.6%** | 0.265 | 23.1% | 76.9% | 0.9% | 7.5% | 69.1% | 21.9% | 0.6% | 0.0% |
| 10 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.4%** | 0.528 | 42.5% | 57.5% | 4.1% | 11.2% | 41.2% | 43.1% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.932 | 79.3% | 20.7% | 6.9% | 11.8% | 0.9% | 80.5% | 0.0% | 0.0% |
| 2 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.921 | 75.4% | 24.6% | 5.6% | 12.3% | 1.7% | 80.4% | 0.0% | 0.0% |
| 3 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.919 | 81.4% | 18.6% | 9.4% | 9.9% | 3.2% | 77.5% | 0.0% | 0.0% |
| 4 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.915 | 78.8% | 21.2% | 7.7% | 13.1% | 1.9% | 77.3% | 0.0% | 0.0% |
| 5 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.915 | 79.7% | 20.3% | 8.4% | 14.0% | 1.5% | 76.0% | 0.0% | 0.0% |
| 6 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.913 | 79.3% | 20.7% | 6.4% | 13.9% | 1.7% | 77.9% | 0.0% | 0.0% |
| 7 | 35 | stranger / mayor / good_record / rich / woman_young | **0.0%** | 0.909 | 77.1% | 22.9% | 4.5% | 13.4% | 2.4% | 79.7% | 0.0% | 0.0% |
| 8 | 34 | stranger / mayor / good_record / rich / man_young | **0.0%** | 0.904 | 76.1% | 23.9% | 7.3% | 14.0% | 2.6% | 76.1% | 0.0% | 0.0% |
| 9 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.903 | 76.1% | 23.9% | 6.0% | 15.5% | 1.9% | 76.3% | 0.0% | 0.2% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.902 | 75.0% | 25.0% | 11.4% | 15.2% | 2.1% | 71.2% | 0.0% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 53 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27 | close_friend / citizen / poor_record / rich / woman_young | **0.4%** | 0.628 | 54.1% | 45.9% | 4.5% | 10.2% | 32.0% | 52.9% | 0.0% | 0.4% |
| 2 | 60 | stranger / citizen / poor_record / rich / man_old | **0.4%** | 0.392 | 33.8% | 66.2% | 1.7% | 7.5% | 56.7% | 33.6% | 0.0% | 0.4% |
| 3 | 39 | stranger / mayor / good_record / poor / woman_young | **0.2%** | 0.889 | 75.4% | 24.6% | 7.1% | 15.8% | 3.2% | 73.7% | 0.0% | 0.2% |
| 4 | 55 | stranger / citizen / good_record / poor / woman_young | **0.2%** | 0.903 | 76.1% | 23.9% | 6.0% | 15.5% | 1.9% | 76.3% | 0.0% | 0.2% |
| 5 | 2 | close_friend / mayor / good_record / rich / man_young | **0.2%** | 0.892 | 76.5% | 23.5% | 6.5% | 15.5% | 2.8% | 74.8% | 0.2% | 0.2% |
| 6 | 58 | stranger / citizen / poor_record / rich / man_young | **0.2%** | 0.404 | 36.1% | 63.9% | 0.9% | 4.9% | 55.7% | 37.0% | 1.3% | 0.2% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **0.2%** | 0.888 | 71.8% | 28.2% | 11.2% | 15.0% | 3.6% | 70.0% | 0.0% | 0.2% |
| 8 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.2%** | 0.463 | 40.4% | 59.6% | 2.1% | 6.2% | 50.0% | 41.0% | 0.4% | 0.2% |
| 9 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.2%** | 0.419 | 37.8% | 62.2% | 2.8% | 6.0% | 54.7% | 36.1% | 0.2% | 0.2% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.2%** | 0.573 | 49.8% | 50.2% | 3.0% | 8.6% | 37.9% | 49.9% | 0.4% | 0.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.936 | 75.4% | 24.6% | 5.4% | 10.1% | 1.1% | 83.2% | 0.2% | 0.0% |
| 2 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.932 | 79.3% | 20.7% | 6.9% | 11.8% | 0.9% | 80.5% | 0.0% | 0.0% |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.926 | 79.7% | 20.3% | 4.3% | 10.9% | 1.7% | 82.8% | 0.2% | 0.0% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.921 | 75.4% | 24.6% | 5.6% | 12.3% | 1.7% | 80.4% | 0.0% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.919 | 81.4% | 18.6% | 9.4% | 9.9% | 3.2% | 77.5% | 0.0% | 0.0% |
| 6 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.915 | 78.8% | 21.2% | 7.7% | 13.1% | 1.9% | 77.3% | 0.0% | 0.0% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.915 | 79.7% | 20.3% | 8.4% | 14.0% | 1.5% | 76.0% | 0.0% | 0.0% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.913 | 79.3% | 20.7% | 6.4% | 13.9% | 1.7% | 77.9% | 0.0% | 0.0% |
| 9 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.912 | 77.6% | 22.4% | 6.0% | 12.0% | 2.6% | 79.1% | 0.2% | 0.0% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0%** | 0.910 | 79.9% | 20.1% | 9.6% | 11.1% | 3.2% | 75.8% | 0.2% | 0.0% |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9167** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 2 | 18 | close_friend / citizen / good_record / rich / man_young | **0.9142** | 0.914 | 82.5% | 17.5% | 2.6% | 12.9% | 1.7% | 82.4% | 0.4% | 0.0% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | **0.9142** | 0.914 | 83.3% | 16.7% | 2.1% | 12.0% | 2.1% | 83.3% | 0.4% | 0.0% |
| 4 | 22 | close_friend / citizen / good_record / poor / man_young | **0.9124** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **0.9099** | 0.910 | 84.6% | 15.4% | 1.3% | 12.0% | 2.6% | 83.7% | 0.4% | 0.0% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.9060** | 0.906 | 85.5% | 14.5% | 3.8% | 10.3% | 4.3% | 81.6% | 0.0% | 0.0% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.9034** | 0.903 | 81.6% | 18.4% | 6.0% | 16.7% | 1.3% | 76.0% | 0.0% | 0.0% |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | **0.8987** | 0.899 | 82.5% | 17.5% | 1.7% | 15.1% | 2.6% | 80.6% | 0.0% | 0.0% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.8966** | 0.897 | 79.9% | 20.1% | 3.9% | 15.5% | 2.6% | 78.0% | 0.0% | 0.0% |
| 10 | 24 | close_friend / citizen / good_record / poor / man_old | **0.8910** | 0.891 | 79.5% | 20.5% | 3.0% | 16.7% | 2.6% | 77.8% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **0.0923** | 0.092 | 4.7% | 95.3% | 0.0% | 9.9% | 85.8% | 4.3% | 0.0% | 0.0% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.1068** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **0.1073** | 0.107 | 6.0% | 94.0% | 0.4% | 9.4% | 84.1% | 5.6% | 0.4% | 0.0% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.1090** | 0.109 | 5.1% | 94.9% | 0.4% | 11.5% | 82.5% | 4.7% | 0.9% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.1121** | 0.112 | 4.3% | 95.7% | 0.0% | 14.7% | 81.0% | 3.9% | 0.4% | 0.0% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.1432** | 0.143 | 9.0% | 91.0% | 0.0% | 10.7% | 79.9% | 9.0% | 0.4% | 0.0% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **0.1474** | 0.147 | 7.7% | 92.3% | 0.0% | 15.8% | 76.9% | 6.8% | 0.4% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **0.1581** | 0.158 | 7.7% | 92.3% | 0.4% | 16.2% | 76.1% | 7.3% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **0.1859** | 0.186 | 12.8% | 87.2% | 0.0% | 11.5% | 75.6% | 12.8% | 0.0% | 0.0% |
| 10 | 44 | stranger / mayor / poor_record / rich / man_old | **0.1953** | 0.195 | 15.8% | 84.2% | 0.4% | 8.2% | 75.5% | 15.0% | 0.9% | 0.0% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 45 | stranger / mayor / poor_record / poor / woman_old | **95.7%** | 0.112 | 4.3% | 95.7% | 0.0% | 14.7% | 81.0% | 3.9% | 0.4% | 0.0% |
| 2 | 62 | stranger / citizen / poor_record / poor / man_young | **95.3%** | 0.092 | 4.7% | 95.3% | 0.0% | 9.9% | 85.8% | 4.3% | 0.0% | 0.0% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **94.9%** | 0.109 | 5.1% | 94.9% | 0.4% | 11.5% | 82.5% | 4.7% | 0.9% | 0.0% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **94.0%** | 0.107 | 6.0% | 94.0% | 0.4% | 9.4% | 84.1% | 5.6% | 0.4% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **94.0%** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | **92.3%** | 0.158 | 7.7% | 92.3% | 0.4% | 16.2% | 76.1% | 7.3% | 0.0% | 0.0% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **92.3%** | 0.147 | 7.7% | 92.3% | 0.0% | 15.8% | 76.9% | 6.8% | 0.4% | 0.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **91.0%** | 0.143 | 9.0% | 91.0% | 0.0% | 10.7% | 79.9% | 9.0% | 0.4% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **87.2%** | 0.186 | 12.8% | 87.2% | 0.0% | 11.5% | 75.6% | 12.8% | 0.0% | 0.0% |
| 10 | 41 | stranger / mayor / poor_record / rich / woman_old | **84.6%** | 0.201 | 15.4% | 84.6% | 0.0% | 9.4% | 74.8% | 15.4% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 19 | close_friend / citizen / good_record / rich / woman_young | **14.5%** | 0.906 | 85.5% | 14.5% | 3.8% | 10.3% | 4.3% | 81.6% | 0.0% | 0.0% |
| 2 | 20 | close_friend / citizen / good_record / rich / man_old | **15.0%** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | **15.4%** | 0.910 | 84.6% | 15.4% | 1.3% | 12.0% | 2.6% | 83.7% | 0.4% | 0.0% |
| 4 | 50 | stranger / citizen / good_record / rich / man_young | **16.7%** | 0.914 | 83.3% | 16.7% | 2.1% | 12.0% | 2.1% | 83.3% | 0.4% | 0.0% |
| 5 | 18 | close_friend / citizen / good_record / rich / man_young | **17.5%** | 0.914 | 82.5% | 17.5% | 2.6% | 12.9% | 1.7% | 82.4% | 0.4% | 0.0% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **17.5%** | 0.899 | 82.5% | 17.5% | 1.7% | 15.1% | 2.6% | 80.6% | 0.0% | 0.0% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **18.4%** | 0.903 | 81.6% | 18.4% | 6.0% | 16.7% | 1.3% | 76.0% | 0.0% | 0.0% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | **18.8%** | 0.887 | 81.2% | 18.8% | 2.6% | 15.6% | 3.5% | 78.4% | 0.0% | 0.0% |
| 9 | 22 | close_friend / citizen / good_record / poor / man_young | **19.2%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 10 | 49 | stranger / citizen / good_record / rich / woman_old | **19.7%** | 0.869 | 80.3% | 19.7% | 5.2% | 13.4% | 6.5% | 75.0% | 0.0% | 0.0% |


**FACT (%)** *(Note: 11 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 21 | close_friend / citizen / good_record / poor / woman_old | **6.0%** | 0.903 | 81.6% | 18.4% | 6.0% | 16.7% | 1.3% | 76.0% | 0.0% | 0.0% |
| 2 | 1 | close_friend / mayor / good_record / rich / woman_old | **6.0%** | 0.863 | 72.2% | 27.8% | 6.0% | 23.2% | 2.1% | 68.7% | 0.0% | 0.0% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | **6.0%** | 0.849 | 72.2% | 27.8% | 6.0% | 18.9% | 5.6% | 69.1% | 0.0% | 0.4% |
| 4 | 6 | close_friend / mayor / good_record / poor / man_young | **5.6%** | 0.878 | 75.6% | 24.4% | 5.6% | 18.5% | 3.0% | 73.0% | 0.0% | 0.0% |
| 5 | 49 | stranger / citizen / good_record / rich / woman_old | **5.2%** | 0.869 | 80.3% | 19.7% | 5.2% | 13.4% | 6.5% | 75.0% | 0.0% | 0.0% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | **5.2%** | 0.882 | 77.8% | 22.2% | 5.2% | 18.5% | 2.1% | 73.8% | 0.4% | 0.0% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | **4.8%** | 0.874 | 74.8% | 25.2% | 4.8% | 19.0% | 3.0% | 73.2% | 0.0% | 0.0% |
| 8 | 22 | close_friend / citizen / good_record / poor / man_young | **4.3%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 9 | 23 | close_friend / citizen / good_record / poor / woman_young | **4.3%** | 0.874 | 77.4% | 22.6% | 4.3% | 15.8% | 4.7% | 75.2% | 0.0% | 0.0% |
| 10 | 53 | stranger / citizen / good_record / poor / woman_old | **4.3%** | 0.831 | 68.4% | 31.6% | 4.3% | 27.8% | 3.0% | 65.0% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.0%** | 0.349 | 25.6% | 74.4% | 0.0% | 19.8% | 54.7% | 25.0% | 0.4% | 0.0% |
| 2 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.258 | 17.5% | 82.5% | 0.0% | 16.2% | 65.4% | 17.5% | 0.4% | 0.4% |
| 3 | 42 | stranger / mayor / poor_record / rich / man_young | **0.0%** | 0.254 | 17.1% | 82.9% | 0.0% | 16.7% | 66.2% | 17.1% | 0.0% | 0.0% |
| 4 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0%** | 0.206 | 17.1% | 82.9% | 0.0% | 7.7% | 74.2% | 16.7% | 1.3% | 0.0% |
| 5 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.0%** | 0.201 | 15.4% | 84.6% | 0.0% | 9.4% | 74.8% | 15.4% | 0.4% | 0.0% |
| 6 | 60 | stranger / citizen / poor_record / rich / man_old | **0.0%** | 0.186 | 12.8% | 87.2% | 0.0% | 11.5% | 75.6% | 12.8% | 0.0% | 0.0% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0%** | 0.147 | 7.7% | 92.3% | 0.0% | 15.8% | 76.9% | 6.8% | 0.4% | 0.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.0%** | 0.143 | 9.0% | 91.0% | 0.0% | 10.7% | 79.9% | 9.0% | 0.4% | 0.0% |
| 9 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.0%** | 0.112 | 4.3% | 95.7% | 0.0% | 14.7% | 81.0% | 3.9% | 0.4% | 0.0% |
| 10 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0%** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 40 | stranger / mayor / good_record / poor / man_old | **28.3%** | 0.824 | 66.7% | 33.3% | 2.1% | 28.3% | 3.4% | 66.1% | 0.0% | 0.0% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | **27.8%** | 0.831 | 68.4% | 31.6% | 4.3% | 27.8% | 3.0% | 65.0% | 0.0% | 0.0% |
| 3 | 56 | stranger / citizen / good_record / poor / man_old | **26.2%** | 0.826 | 68.4% | 31.6% | 3.0% | 26.2% | 4.3% | 66.5% | 0.0% | 0.0% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **26.1%** | 0.835 | 69.7% | 30.3% | 3.0% | 26.1% | 3.0% | 67.5% | 0.4% | 0.0% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | **24.0%** | 0.841 | 69.2% | 30.8% | 3.4% | 24.0% | 3.9% | 68.7% | 0.0% | 0.0% |
| 6 | 1 | close_friend / mayor / good_record / rich / woman_old | **23.2%** | 0.863 | 72.2% | 27.8% | 6.0% | 23.2% | 2.1% | 68.7% | 0.0% | 0.0% |
| 7 | 37 | stranger / mayor / good_record / poor / woman_old | **23.1%** | 0.838 | 70.5% | 29.5% | 3.0% | 23.1% | 4.7% | 69.2% | 0.0% | 0.0% |
| 8 | 55 | stranger / citizen / good_record / poor / woman_young | **22.7%** | 0.861 | 74.4% | 25.6% | 2.6% | 22.7% | 2.6% | 72.1% | 0.0% | 0.0% |
| 9 | 39 | stranger / mayor / good_record / poor / woman_young | **22.4%** | 0.853 | 71.4% | 28.6% | 1.7% | 22.4% | 3.4% | 72.0% | 0.0% | 0.4% |
| 10 | 33 | stranger / mayor / good_record / rich / woman_old | **21.8%** | 0.870 | 74.8% | 25.2% | 0.9% | 21.8% | 2.1% | 75.2% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **7.7%** | 0.206 | 17.1% | 82.9% | 0.0% | 7.7% | 74.2% | 16.7% | 1.3% | 0.0% |
| 2 | 44 | stranger / mayor / poor_record / rich / man_old | **8.2%** | 0.195 | 15.8% | 84.2% | 0.4% | 8.2% | 75.5% | 15.0% | 0.9% | 0.0% |
| 3 | 41 | stranger / mayor / poor_record / rich / woman_old | **9.4%** | 0.201 | 15.4% | 84.6% | 0.0% | 9.4% | 74.8% | 15.4% | 0.4% | 0.0% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **9.4%** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |
| 5 | 64 | stranger / citizen / poor_record / poor / man_old | **9.4%** | 0.107 | 6.0% | 94.0% | 0.4% | 9.4% | 84.1% | 5.6% | 0.4% | 0.0% |
| 6 | 62 | stranger / citizen / poor_record / poor / man_young | **9.9%** | 0.092 | 4.7% | 95.3% | 0.0% | 9.9% | 85.8% | 4.3% | 0.0% | 0.0% |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | **10.3%** | 0.906 | 85.5% | 14.5% | 3.8% | 10.3% | 4.3% | 81.6% | 0.0% | 0.0% |
| 8 | 59 | stranger / citizen / poor_record / rich / woman_young | **10.7%** | 0.241 | 18.8% | 81.2% | 0.4% | 10.7% | 70.1% | 18.4% | 0.4% | 0.0% |
| 9 | 47 | stranger / mayor / poor_record / poor / woman_young | **10.7%** | 0.143 | 9.0% | 91.0% | 0.0% | 10.7% | 79.9% | 9.0% | 0.4% | 0.0% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **11.1%** | 0.214 | 15.8% | 84.2% | 1.3% | 11.1% | 72.2% | 14.5% | 0.9% | 0.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **85.8%** | 0.092 | 4.7% | 95.3% | 0.0% | 9.9% | 85.8% | 4.3% | 0.0% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **84.1%** | 0.107 | 6.0% | 94.0% | 0.4% | 9.4% | 84.1% | 5.6% | 0.4% | 0.0% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | **82.9%** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **82.5%** | 0.109 | 5.1% | 94.9% | 0.4% | 11.5% | 82.5% | 4.7% | 0.9% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **81.0%** | 0.112 | 4.3% | 95.7% | 0.0% | 14.7% | 81.0% | 3.9% | 0.4% | 0.0% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **79.9%** | 0.143 | 9.0% | 91.0% | 0.0% | 10.7% | 79.9% | 9.0% | 0.4% | 0.0% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **76.9%** | 0.147 | 7.7% | 92.3% | 0.0% | 15.8% | 76.9% | 6.8% | 0.4% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **76.1%** | 0.158 | 7.7% | 92.3% | 0.4% | 16.2% | 76.1% | 7.3% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **75.6%** | 0.186 | 12.8% | 87.2% | 0.0% | 11.5% | 75.6% | 12.8% | 0.0% | 0.0% |
| 10 | 44 | stranger / mayor / poor_record / rich / man_old | **75.5%** | 0.195 | 15.8% | 84.2% | 0.4% | 8.2% | 75.5% | 15.0% | 0.9% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | close_friend / citizen / good_record / poor / man_young | **0.9%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 2 | 20 | close_friend / citizen / good_record / rich / man_old | **1.3%** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 3 | 21 | close_friend / citizen / good_record / poor / woman_old | **1.3%** | 0.903 | 81.6% | 18.4% | 6.0% | 16.7% | 1.3% | 76.0% | 0.0% | 0.0% |
| 4 | 18 | close_friend / citizen / good_record / rich / man_young | **1.7%** | 0.914 | 82.5% | 17.5% | 2.6% | 12.9% | 1.7% | 82.4% | 0.4% | 0.0% |
| 5 | 33 | stranger / mayor / good_record / rich / woman_old | **2.1%** | 0.870 | 74.8% | 25.2% | 0.9% | 21.8% | 2.1% | 75.2% | 0.0% | 0.0% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | **2.1%** | 0.914 | 83.3% | 16.7% | 2.1% | 12.0% | 2.1% | 83.3% | 0.4% | 0.0% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **2.1%** | 0.882 | 77.8% | 22.2% | 5.2% | 18.5% | 2.1% | 73.8% | 0.4% | 0.0% |
| 8 | 1 | close_friend / mayor / good_record / rich / woman_old | **2.1%** | 0.863 | 72.2% | 27.8% | 6.0% | 23.2% | 2.1% | 68.7% | 0.0% | 0.0% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | **2.6%** | 0.891 | 79.5% | 20.5% | 3.0% | 16.7% | 2.6% | 77.8% | 0.0% | 0.0% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | **2.6%** | 0.910 | 84.6% | 15.4% | 1.3% | 12.0% | 2.6% | 83.7% | 0.4% | 0.0% |


**CHECKED_TRUE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | **83.7%** | 0.910 | 84.6% | 15.4% | 1.3% | 12.0% | 2.6% | 83.7% | 0.4% | 0.0% |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | **83.3%** | 0.914 | 83.3% | 16.7% | 2.1% | 12.0% | 2.1% | 83.3% | 0.4% | 0.0% |
| 3 | 18 | close_friend / citizen / good_record / rich / man_young | **82.4%** | 0.914 | 82.5% | 17.5% | 2.6% | 12.9% | 1.7% | 82.4% | 0.4% | 0.0% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **82.1%** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **81.6%** | 0.906 | 85.5% | 14.5% | 3.8% | 10.3% | 4.3% | 81.6% | 0.0% | 0.0% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **80.6%** | 0.899 | 82.5% | 17.5% | 1.7% | 15.1% | 2.6% | 80.6% | 0.0% | 0.0% |
| 7 | 22 | close_friend / citizen / good_record / poor / man_young | **79.1%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | **78.4%** | 0.887 | 81.2% | 18.8% | 2.6% | 15.6% | 3.5% | 78.4% | 0.0% | 0.0% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | **78.0%** | 0.897 | 79.9% | 20.1% | 3.9% | 15.5% | 2.6% | 78.0% | 0.0% | 0.0% |
| 10 | 24 | close_friend / citizen / good_record / poor / man_old | **77.8%** | 0.891 | 79.5% | 20.5% | 3.0% | 16.7% | 2.6% | 77.8% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 45 | stranger / mayor / poor_record / poor / woman_old | **3.9%** | 0.112 | 4.3% | 95.7% | 0.0% | 14.7% | 81.0% | 3.9% | 0.4% | 0.0% |
| 2 | 62 | stranger / citizen / poor_record / poor / man_young | **4.3%** | 0.092 | 4.7% | 95.3% | 0.0% | 9.9% | 85.8% | 4.3% | 0.0% | 0.0% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **4.7%** | 0.109 | 5.1% | 94.9% | 0.4% | 11.5% | 82.5% | 4.7% | 0.9% | 0.0% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **5.6%** | 0.107 | 6.0% | 94.0% | 0.4% | 9.4% | 84.1% | 5.6% | 0.4% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **6.0%** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **6.8%** | 0.147 | 7.7% | 92.3% | 0.0% | 15.8% | 76.9% | 6.8% | 0.4% | 0.0% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **7.3%** | 0.158 | 7.7% | 92.3% | 0.4% | 16.2% | 76.1% | 7.3% | 0.0% | 0.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **9.0%** | 0.143 | 9.0% | 91.0% | 0.0% | 10.7% | 79.9% | 9.0% | 0.4% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **12.8%** | 0.186 | 12.8% | 87.2% | 0.0% | 11.5% | 75.6% | 12.8% | 0.0% | 0.0% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **14.5%** | 0.214 | 15.8% | 84.2% | 1.3% | 11.1% | 72.2% | 14.5% | 0.9% | 0.0% |


**CHECKED_FALSE (%)** *(Note: 35 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.7%** | 0.107 | 6.0% | 94.0% | 0.0% | 9.4% | 82.9% | 6.0% | 1.7% | 0.0% |
| 2 | 58 | stranger / citizen / poor_record / rich / man_young | **1.3%** | 0.206 | 17.1% | 82.9% | 0.0% | 7.7% | 74.2% | 16.7% | 1.3% | 0.0% |
| 3 | 32 | close_friend / citizen / poor_record / poor / man_old | **1.3%** | 0.335 | 25.6% | 74.4% | 0.4% | 15.8% | 57.3% | 25.2% | 1.3% | 0.0% |
| 4 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.9%** | 0.414 | 34.2% | 65.8% | 2.1% | 15.9% | 49.8% | 31.3% | 0.9% | 0.0% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | **0.9%** | 0.195 | 15.8% | 84.2% | 0.4% | 8.2% | 75.5% | 15.0% | 0.9% | 0.0% |
| 6 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.9%** | 0.214 | 15.8% | 84.2% | 1.3% | 11.1% | 72.2% | 14.5% | 0.9% | 0.0% |
| 7 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.9%** | 0.109 | 5.1% | 94.9% | 0.4% | 11.5% | 82.5% | 4.7% | 0.9% | 0.0% |
| 8 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.4%** | 0.388 | 31.2% | 68.8% | 0.9% | 15.5% | 53.0% | 30.2% | 0.4% | 0.0% |
| 9 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.4%** | 0.364 | 29.9% | 70.1% | 1.7% | 13.4% | 56.5% | 28.0% | 0.4% | 0.0% |
| 10 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.4%** | 0.349 | 25.6% | 74.4% | 0.0% | 19.8% | 54.7% | 25.0% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 2 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 3 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.906 | 85.5% | 14.5% | 3.8% | 10.3% | 4.3% | 81.6% | 0.0% | 0.0% |
| 4 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.903 | 81.6% | 18.4% | 6.0% | 16.7% | 1.3% | 76.0% | 0.0% | 0.0% |
| 5 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.899 | 82.5% | 17.5% | 1.7% | 15.1% | 2.6% | 80.6% | 0.0% | 0.0% |
| 6 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0%** | 0.897 | 79.9% | 20.1% | 3.9% | 15.5% | 2.6% | 78.0% | 0.0% | 0.0% |
| 7 | 24 | close_friend / citizen / good_record / poor / man_old | **0.0%** | 0.891 | 79.5% | 20.5% | 3.0% | 16.7% | 2.6% | 77.8% | 0.0% | 0.0% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.887 | 81.2% | 18.8% | 2.6% | 15.6% | 3.5% | 78.4% | 0.0% | 0.0% |
| 9 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.878 | 75.6% | 24.4% | 5.6% | 18.5% | 3.0% | 73.0% | 0.0% | 0.0% |
| 10 | 35 | stranger / mayor / good_record / rich / woman_young | **0.0%** | 0.877 | 76.5% | 23.5% | 1.3% | 17.7% | 3.4% | 77.6% | 0.0% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 59 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 39 | stranger / mayor / good_record / poor / woman_young | **0.4%** | 0.853 | 71.4% | 28.6% | 1.7% | 22.4% | 3.4% | 72.0% | 0.0% | 0.4% |
| 2 | 4 | close_friend / mayor / good_record / rich / man_old | **0.4%** | 0.849 | 72.2% | 27.8% | 6.0% | 18.9% | 5.6% | 69.1% | 0.0% | 0.4% |
| 3 | 27 | close_friend / citizen / poor_record / rich / woman_young | **0.4%** | 0.528 | 44.9% | 55.1% | 1.7% | 16.7% | 38.6% | 42.5% | 0.0% | 0.4% |
| 4 | 2 | close_friend / mayor / good_record / rich / man_young | **0.4%** | 0.850 | 74.4% | 25.6% | 1.7% | 20.5% | 4.3% | 72.6% | 0.4% | 0.4% |
| 5 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.4%** | 0.258 | 17.5% | 82.5% | 0.0% | 16.2% | 65.4% | 17.5% | 0.4% | 0.4% |
| 6 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 7 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.914 | 82.5% | 17.5% | 2.6% | 12.9% | 1.7% | 82.4% | 0.4% | 0.0% |
| 8 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.914 | 83.3% | 16.7% | 2.1% | 12.0% | 2.1% | 83.3% | 0.4% | 0.0% |
| 9 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.910 | 84.6% | 15.4% | 1.3% | 12.0% | 2.6% | 83.7% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.917 | 85.0% | 15.0% | 2.6% | 14.1% | 1.3% | 82.1% | 0.0% | 0.0% |
| 2 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.914 | 82.5% | 17.5% | 2.6% | 12.9% | 1.7% | 82.4% | 0.4% | 0.0% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.914 | 83.3% | 16.7% | 2.1% | 12.0% | 2.1% | 83.3% | 0.4% | 0.0% |
| 4 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.912 | 80.8% | 19.2% | 4.3% | 15.8% | 0.9% | 79.1% | 0.0% | 0.0% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.910 | 84.6% | 15.4% | 1.3% | 12.0% | 2.6% | 83.7% | 0.4% | 0.0% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.906 | 85.5% | 14.5% | 3.8% | 10.3% | 4.3% | 81.6% | 0.0% | 0.0% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.903 | 81.6% | 18.4% | 6.0% | 16.7% | 1.3% | 76.0% | 0.0% | 0.0% |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.899 | 82.5% | 17.5% | 1.7% | 15.1% | 2.6% | 80.6% | 0.0% | 0.0% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0%** | 0.897 | 79.9% | 20.1% | 3.9% | 15.5% | 2.6% | 78.0% | 0.0% | 0.0% |
| 10 | 24 | close_friend / citizen / good_record / poor / man_old | **0.0%** | 0.891 | 79.5% | 20.5% | 3.0% | 16.7% | 2.6% | 77.8% | 0.0% | 0.0% |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.9589** | 0.959 | 67.5% | 32.5% | 8.7% | 8.2% | 0.0% | 83.1% | 0.0% | 0.0% |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | **0.9571** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | **0.9526** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |
| 4 | 56 | stranger / citizen / good_record / poor / man_old | **0.9485** | 0.948 | 79.1% | 20.9% | 8.2% | 7.7% | 1.3% | 82.8% | 0.0% | 0.0% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9483** | 0.948 | 73.5% | 26.5% | 11.2% | 9.5% | 0.4% | 78.9% | 0.0% | 0.0% |
| 6 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.9464** | 0.946 | 82.5% | 17.5% | 15.0% | 6.4% | 1.7% | 76.4% | 0.4% | 0.0% |
| 7 | 55 | stranger / citizen / good_record / poor / woman_young | **0.9457** | 0.946 | 77.8% | 22.2% | 9.5% | 8.2% | 1.3% | 80.5% | 0.0% | 0.4% |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | **0.9440** | 0.944 | 68.4% | 31.6% | 9.5% | 9.5% | 0.9% | 80.2% | 0.0% | 0.0% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | **0.9421** | 0.942 | 74.8% | 25.2% | 7.3% | 9.9% | 0.9% | 82.0% | 0.0% | 0.0% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.9421** | 0.942 | 77.8% | 22.2% | 16.7% | 7.3% | 2.1% | 73.8% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.4224** | 0.422 | 41.0% | 59.0% | 1.3% | 3.4% | 55.6% | 39.2% | 0.4% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **0.4313** | 0.431 | 41.5% | 58.5% | 0.4% | 2.1% | 55.8% | 41.6% | 0.0% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **0.4741** | 0.474 | 46.6% | 53.4% | 3.4% | 3.4% | 50.9% | 42.2% | 0.0% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.5022** | 0.502 | 48.7% | 51.3% | 2.2% | 4.8% | 47.4% | 45.7% | 0.0% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.5214** | 0.521 | 49.6% | 50.4% | 2.1% | 2.6% | 46.2% | 48.7% | 0.4% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **0.5568** | 0.557 | 52.6% | 47.4% | 4.8% | 1.3% | 43.7% | 50.2% | 0.0% | 0.0% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.5606** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **0.5726** | 0.573 | 54.3% | 45.7% | 3.0% | 3.4% | 41.0% | 52.6% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **0.6017** | 0.602 | 54.7% | 45.3% | 3.4% | 3.4% | 37.8% | 54.5% | 0.0% | 0.9% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | **0.6039** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **59.0%** | 0.422 | 41.0% | 59.0% | 1.3% | 3.4% | 55.6% | 39.2% | 0.4% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **58.5%** | 0.431 | 41.5% | 58.5% | 0.4% | 2.1% | 55.8% | 41.6% | 0.0% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **53.4%** | 0.474 | 46.6% | 53.4% | 3.4% | 3.4% | 50.9% | 42.2% | 0.0% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **51.3%** | 0.502 | 48.7% | 51.3% | 2.2% | 4.8% | 47.4% | 45.7% | 0.0% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **50.4%** | 0.521 | 49.6% | 50.4% | 2.1% | 2.6% | 46.2% | 48.7% | 0.4% | 0.0% |
| 6 | 57 | stranger / citizen / poor_record / rich / woman_old | **48.3%** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **47.4%** | 0.557 | 52.6% | 47.4% | 4.8% | 1.3% | 43.7% | 50.2% | 0.0% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **45.7%** | 0.573 | 54.3% | 45.7% | 3.0% | 3.4% | 41.0% | 52.6% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **45.3%** | 0.602 | 54.7% | 45.3% | 3.4% | 3.4% | 37.8% | 54.5% | 0.0% | 0.9% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | **44.9%** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | close_friend / mayor / good_record / poor / woman_young | **15.8%** | 0.925 | 84.2% | 15.8% | 13.8% | 10.8% | 2.2% | 73.3% | 0.0% | 0.0% |
| 2 | 5 | close_friend / mayor / good_record / poor / woman_old | **15.8%** | 0.902 | 84.2% | 15.8% | 14.1% | 12.0% | 3.8% | 70.1% | 0.0% | 0.0% |
| 3 | 33 | stranger / mayor / good_record / rich / woman_old | **16.2%** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | **17.5%** | 0.946 | 82.5% | 17.5% | 15.0% | 6.4% | 1.7% | 76.4% | 0.4% | 0.0% |
| 5 | 8 | close_friend / mayor / good_record / poor / man_old | **18.8%** | 0.906 | 81.2% | 18.8% | 11.2% | 13.7% | 2.6% | 72.5% | 0.0% | 0.0% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **20.5%** | 0.924 | 79.5% | 20.5% | 12.6% | 9.1% | 3.0% | 75.3% | 0.0% | 0.0% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | **20.9%** | 0.948 | 79.1% | 20.9% | 8.2% | 7.7% | 1.3% | 82.8% | 0.0% | 0.0% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | **20.9%** | 0.929 | 79.1% | 20.9% | 10.8% | 9.9% | 1.7% | 77.2% | 0.4% | 0.0% |
| 9 | 2 | close_friend / mayor / good_record / rich / man_young | **21.4%** | 0.935 | 78.6% | 21.4% | 11.3% | 10.4% | 1.3% | 77.0% | 0.0% | 0.0% |
| 10 | 53 | stranger / citizen / good_record / poor / woman_old | **21.8%** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | close_friend / mayor / good_record / rich / woman_old | **16.7%** | 0.942 | 77.8% | 22.2% | 16.7% | 7.3% | 2.1% | 73.8% | 0.0% | 0.0% |
| 2 | 4 | close_friend / mayor / good_record / rich / man_old | **16.3%** | 0.927 | 71.4% | 28.6% | 16.3% | 11.2% | 1.7% | 70.8% | 0.0% | 0.0% |
| 3 | 6 | close_friend / mayor / good_record / poor / man_young | **15.5%** | 0.873 | 77.8% | 22.2% | 15.5% | 14.2% | 5.6% | 64.8% | 0.0% | 0.0% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | **15.0%** | 0.946 | 82.5% | 17.5% | 15.0% | 6.4% | 1.7% | 76.4% | 0.4% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **15.0%** | 0.931 | 77.4% | 22.6% | 15.0% | 9.4% | 2.1% | 73.4% | 0.0% | 0.0% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | **15.0%** | 0.929 | 76.5% | 23.5% | 15.0% | 10.7% | 1.7% | 72.6% | 0.0% | 0.0% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | **14.1%** | 0.902 | 84.2% | 15.8% | 14.1% | 12.0% | 3.8% | 70.1% | 0.0% | 0.0% |
| 8 | 7 | close_friend / mayor / good_record / poor / woman_young | **13.8%** | 0.925 | 84.2% | 15.8% | 13.8% | 10.8% | 2.2% | 73.3% | 0.0% | 0.0% |
| 9 | 36 | stranger / mayor / good_record / rich / man_old | **12.9%** | 0.920 | 74.8% | 25.2% | 12.9% | 11.6% | 2.2% | 73.3% | 0.0% | 0.0% |
| 10 | 39 | stranger / mayor / good_record / poor / woman_young | **12.6%** | 0.924 | 79.5% | 20.5% | 12.6% | 9.1% | 3.0% | 75.3% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **0.4%** | 0.431 | 41.5% | 58.5% | 0.4% | 2.1% | 55.8% | 41.6% | 0.0% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **1.3%** | 0.422 | 41.0% | 59.0% | 1.3% | 3.4% | 55.6% | 39.2% | 0.4% | 0.0% |
| 3 | 58 | stranger / citizen / poor_record / rich / man_young | **1.7%** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **2.1%** | 0.521 | 49.6% | 50.4% | 2.1% | 2.6% | 46.2% | 48.7% | 0.4% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **2.2%** | 0.502 | 48.7% | 51.3% | 2.2% | 4.8% | 47.4% | 45.7% | 0.0% | 0.0% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | **2.6%** | 0.681 | 62.4% | 37.6% | 2.6% | 2.6% | 30.6% | 64.2% | 0.0% | 0.0% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **3.0%** | 0.573 | 54.3% | 45.7% | 3.0% | 3.4% | 41.0% | 52.6% | 0.0% | 0.0% |
| 8 | 43 | stranger / mayor / poor_record / rich / woman_young | **3.0%** | 0.648 | 59.4% | 40.6% | 3.0% | 6.0% | 31.8% | 58.8% | 0.4% | 0.0% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **3.0%** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 10 | 29 | close_friend / citizen / poor_record / poor / woman_old | **3.4%** | 0.650 | 57.3% | 42.7% | 3.4% | 5.1% | 32.5% | 59.0% | 0.0% | 0.0% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6 | close_friend / mayor / good_record / poor / man_young | **14.2%** | 0.873 | 77.8% | 22.2% | 15.5% | 14.2% | 5.6% | 64.8% | 0.0% | 0.0% |
| 2 | 8 | close_friend / mayor / good_record / poor / man_old | **13.7%** | 0.906 | 81.2% | 18.8% | 11.2% | 13.7% | 2.6% | 72.5% | 0.0% | 0.0% |
| 3 | 5 | close_friend / mayor / good_record / poor / woman_old | **12.0%** | 0.902 | 84.2% | 15.8% | 14.1% | 12.0% | 3.8% | 70.1% | 0.0% | 0.0% |
| 4 | 36 | stranger / mayor / good_record / rich / man_old | **11.6%** | 0.920 | 74.8% | 25.2% | 12.9% | 11.6% | 2.2% | 73.3% | 0.0% | 0.0% |
| 5 | 37 | stranger / mayor / good_record / poor / woman_old | **11.5%** | 0.925 | 75.6% | 24.4% | 9.0% | 11.5% | 1.7% | 77.8% | 0.0% | 0.0% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **11.3%** | 0.926 | 77.8% | 22.2% | 10.9% | 11.3% | 1.7% | 76.1% | 0.0% | 0.0% |
| 7 | 18 | close_friend / citizen / good_record / rich / man_young | **11.2%** | 0.909 | 72.6% | 27.4% | 9.5% | 11.2% | 3.4% | 75.9% | 0.0% | 0.0% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | **11.2%** | 0.927 | 71.4% | 28.6% | 16.3% | 11.2% | 1.7% | 70.8% | 0.0% | 0.0% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | **10.9%** | 0.924 | 70.5% | 29.5% | 10.0% | 10.9% | 1.7% | 77.0% | 0.4% | 0.0% |
| 10 | 7 | close_friend / mayor / good_record / poor / woman_young | **10.8%** | 0.925 | 84.2% | 15.8% | 13.8% | 10.8% | 2.2% | 73.3% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 48 | stranger / mayor / poor_record / poor / man_old | **1.3%** | 0.557 | 52.6% | 47.4% | 4.8% | 1.3% | 43.7% | 50.2% | 0.0% | 0.0% |
| 2 | 59 | stranger / citizen / poor_record / rich / woman_young | **1.7%** | 0.688 | 62.0% | 38.0% | 3.9% | 1.7% | 29.7% | 63.8% | 0.4% | 0.4% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **2.1%** | 0.431 | 41.5% | 58.5% | 0.4% | 2.1% | 55.8% | 41.6% | 0.0% | 0.0% |
| 4 | 42 | stranger / mayor / poor_record / rich / man_young | **2.2%** | 0.696 | 63.7% | 36.3% | 6.0% | 2.2% | 28.4% | 62.5% | 0.9% | 0.0% |
| 5 | 58 | stranger / citizen / poor_record / rich / man_young | **2.2%** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |
| 6 | 57 | stranger / citizen / poor_record / rich / woman_old | **2.2%** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 7 | 63 | stranger / citizen / poor_record / poor / woman_young | **2.6%** | 0.521 | 49.6% | 50.4% | 2.1% | 2.6% | 46.2% | 48.7% | 0.4% | 0.0% |
| 8 | 32 | close_friend / citizen / poor_record / poor / man_old | **2.6%** | 0.681 | 62.4% | 37.6% | 2.6% | 2.6% | 30.6% | 64.2% | 0.0% | 0.0% |
| 9 | 41 | stranger / mayor / poor_record / rich / woman_old | **2.6%** | 0.641 | 60.3% | 39.7% | 5.6% | 2.6% | 34.5% | 56.9% | 0.0% | 0.4% |
| 10 | 30 | close_friend / citizen / poor_record / poor / man_young | **3.0%** | 0.670 | 62.0% | 38.0% | 5.2% | 3.0% | 31.5% | 60.3% | 0.0% | 0.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **55.8%** | 0.431 | 41.5% | 58.5% | 0.4% | 2.1% | 55.8% | 41.6% | 0.0% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **55.6%** | 0.422 | 41.0% | 59.0% | 1.3% | 3.4% | 55.6% | 39.2% | 0.4% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **50.9%** | 0.474 | 46.6% | 53.4% | 3.4% | 3.4% | 50.9% | 42.2% | 0.0% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **47.4%** | 0.502 | 48.7% | 51.3% | 2.2% | 4.8% | 47.4% | 45.7% | 0.0% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **46.2%** | 0.521 | 49.6% | 50.4% | 2.1% | 2.6% | 46.2% | 48.7% | 0.4% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **43.7%** | 0.557 | 52.6% | 47.4% | 4.8% | 1.3% | 43.7% | 50.2% | 0.0% | 0.0% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **42.4%** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **41.0%** | 0.573 | 54.3% | 45.7% | 3.0% | 3.4% | 41.0% | 52.6% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **37.8%** | 0.602 | 54.7% | 45.3% | 3.4% | 3.4% | 37.8% | 54.5% | 0.0% | 0.9% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | **37.1%** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.959 | 67.5% | 32.5% | 8.7% | 8.2% | 0.0% | 83.1% | 0.0% | 0.0% |
| 2 | 20 | close_friend / citizen / good_record / rich / man_old | **0.4%** | 0.948 | 73.5% | 26.5% | 11.2% | 9.5% | 0.4% | 78.9% | 0.0% | 0.0% |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | **0.9%** | 0.942 | 74.8% | 25.2% | 7.3% | 9.9% | 0.9% | 82.0% | 0.0% | 0.0% |
| 4 | 40 | stranger / mayor / good_record / poor / man_old | **0.9%** | 0.933 | 78.2% | 21.8% | 9.0% | 10.7% | 0.9% | 79.0% | 0.4% | 0.0% |
| 5 | 52 | stranger / citizen / good_record / rich / man_old | **0.9%** | 0.944 | 68.4% | 31.6% | 9.5% | 9.5% | 0.9% | 80.2% | 0.0% | 0.0% |
| 6 | 33 | stranger / mayor / good_record / rich / woman_old | **1.3%** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | **1.3%** | 0.948 | 79.1% | 20.9% | 8.2% | 7.7% | 1.3% | 82.8% | 0.0% | 0.0% |
| 8 | 53 | stranger / citizen / good_record / poor / woman_old | **1.3%** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |
| 9 | 35 | stranger / mayor / good_record / rich / woman_young | **1.3%** | 0.942 | 77.8% | 22.2% | 7.8% | 9.1% | 1.3% | 81.9% | 0.0% | 0.0% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | **1.3%** | 0.946 | 77.8% | 22.2% | 9.5% | 8.2% | 1.3% | 80.5% | 0.0% | 0.4% |


**CHECKED_TRUE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **84.5%** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | **83.1%** | 0.959 | 67.5% | 32.5% | 8.7% | 8.2% | 0.0% | 83.1% | 0.0% | 0.0% |
| 3 | 56 | stranger / citizen / good_record / poor / man_old | **82.8%** | 0.948 | 79.1% | 20.9% | 8.2% | 7.7% | 1.3% | 82.8% | 0.0% | 0.0% |
| 4 | 51 | stranger / citizen / good_record / rich / woman_young | **82.0%** | 0.942 | 74.8% | 25.2% | 7.3% | 9.9% | 0.9% | 82.0% | 0.0% | 0.0% |
| 5 | 35 | stranger / mayor / good_record / rich / woman_young | **81.9%** | 0.942 | 77.8% | 22.2% | 7.8% | 9.1% | 1.3% | 81.9% | 0.0% | 0.0% |
| 6 | 33 | stranger / mayor / good_record / rich / woman_old | **80.7%** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 7 | 55 | stranger / citizen / good_record / poor / woman_young | **80.5%** | 0.946 | 77.8% | 22.2% | 9.5% | 8.2% | 1.3% | 80.5% | 0.0% | 0.4% |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | **80.2%** | 0.944 | 68.4% | 31.6% | 9.5% | 9.5% | 0.9% | 80.2% | 0.0% | 0.0% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | **79.4%** | 0.927 | 76.1% | 23.9% | 9.0% | 8.6% | 3.0% | 79.4% | 0.0% | 0.0% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | **79.3%** | 0.938 | 77.8% | 22.2% | 11.2% | 6.5% | 3.0% | 79.3% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **39.2%** | 0.422 | 41.0% | 59.0% | 1.3% | 3.4% | 55.6% | 39.2% | 0.4% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **41.6%** | 0.431 | 41.5% | 58.5% | 0.4% | 2.1% | 55.8% | 41.6% | 0.0% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **42.2%** | 0.474 | 46.6% | 53.4% | 3.4% | 3.4% | 50.9% | 42.2% | 0.0% | 0.0% |
| 4 | 45 | stranger / mayor / poor_record / poor / woman_old | **45.7%** | 0.502 | 48.7% | 51.3% | 2.2% | 4.8% | 47.4% | 45.7% | 0.0% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **48.7%** | 0.521 | 49.6% | 50.4% | 2.1% | 2.6% | 46.2% | 48.7% | 0.4% | 0.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **50.2%** | 0.557 | 52.6% | 47.4% | 4.8% | 1.3% | 43.7% | 50.2% | 0.0% | 0.0% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **51.9%** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **52.6%** | 0.573 | 54.3% | 45.7% | 3.0% | 3.4% | 41.0% | 52.6% | 0.0% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **54.5%** | 0.602 | 54.7% | 45.3% | 3.4% | 3.4% | 37.8% | 54.5% | 0.0% | 0.9% |
| 10 | 47 | stranger / mayor / poor_record / poor / woman_young | **54.7%** | 0.616 | 59.0% | 41.0% | 3.4% | 6.9% | 34.5% | 54.7% | 0.4% | 0.0% |


**CHECKED_FALSE (%)** *(Note: 44 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 31 | close_friend / citizen / poor_record / poor / woman_young | **1.3%** | 0.686 | 62.4% | 37.6% | 4.3% | 5.6% | 27.3% | 61.5% | 1.3% | 0.0% |
| 2 | 58 | stranger / citizen / poor_record / rich / man_young | **1.3%** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |
| 3 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.9%** | 0.740 | 64.5% | 35.5% | 5.7% | 3.9% | 23.1% | 66.4% | 0.9% | 0.0% |
| 4 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.9%** | 0.754 | 70.1% | 29.9% | 8.3% | 3.9% | 21.7% | 65.2% | 0.9% | 0.0% |
| 5 | 42 | stranger / mayor / poor_record / rich / man_young | **0.9%** | 0.696 | 63.7% | 36.3% | 6.0% | 2.2% | 28.4% | 62.5% | 0.9% | 0.0% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **0.9%** | 0.620 | 58.5% | 41.5% | 5.2% | 3.9% | 35.2% | 54.9% | 0.9% | 0.0% |
| 7 | 49 | stranger / citizen / good_record / rich / woman_old | **0.4%** | 0.924 | 70.5% | 29.5% | 10.0% | 10.9% | 1.7% | 77.0% | 0.4% | 0.0% |
| 8 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.4%** | 0.711 | 58.1% | 41.9% | 6.1% | 5.7% | 25.7% | 62.2% | 0.4% | 0.0% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.4%** | 0.561 | 51.7% | 48.3% | 3.0% | 2.2% | 42.4% | 51.9% | 0.4% | 0.0% |
| 10 | 53 | stranger / citizen / good_record / poor / woman_old | **0.4%** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.959 | 67.5% | 32.5% | 8.7% | 8.2% | 0.0% | 83.1% | 0.0% | 0.0% |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 3 | 56 | stranger / citizen / good_record / poor / man_old | **0.0%** | 0.948 | 79.1% | 20.9% | 8.2% | 7.7% | 1.3% | 82.8% | 0.0% | 0.0% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.948 | 73.5% | 26.5% | 11.2% | 9.5% | 0.4% | 78.9% | 0.0% | 0.0% |
| 5 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.946 | 77.8% | 22.2% | 9.5% | 8.2% | 1.3% | 80.5% | 0.0% | 0.4% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.944 | 68.4% | 31.6% | 9.5% | 9.5% | 0.9% | 80.2% | 0.0% | 0.0% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.942 | 74.8% | 25.2% | 7.3% | 9.9% | 0.9% | 82.0% | 0.0% | 0.0% |
| 8 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.942 | 77.8% | 22.2% | 16.7% | 7.3% | 2.1% | 73.8% | 0.0% | 0.0% |
| 9 | 35 | stranger / mayor / good_record / rich / woman_young | **0.0%** | 0.942 | 77.8% | 22.2% | 7.8% | 9.1% | 1.3% | 81.9% | 0.0% | 0.0% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.938 | 77.8% | 22.2% | 11.2% | 6.5% | 3.0% | 79.3% | 0.0% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 57 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 60 | stranger / citizen / poor_record / rich / man_old | **0.9%** | 0.602 | 54.7% | 45.3% | 3.4% | 3.4% | 37.8% | 54.5% | 0.0% | 0.9% |
| 2 | 27 | close_friend / citizen / poor_record / rich / woman_young | **0.4%** | 0.729 | 63.2% | 36.8% | 7.4% | 3.5% | 25.2% | 63.5% | 0.0% | 0.4% |
| 3 | 55 | stranger / citizen / good_record / poor / woman_young | **0.4%** | 0.946 | 77.8% | 22.2% | 9.5% | 8.2% | 1.3% | 80.5% | 0.0% | 0.4% |
| 4 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.4%** | 0.688 | 62.0% | 38.0% | 3.9% | 1.7% | 29.7% | 63.8% | 0.4% | 0.4% |
| 5 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.4%** | 0.641 | 60.3% | 39.7% | 5.6% | 2.6% | 34.5% | 56.9% | 0.0% | 0.4% |
| 6 | 58 | stranger / citizen / poor_record / rich / man_young | **0.4%** | 0.604 | 55.1% | 44.9% | 1.7% | 2.2% | 37.1% | 57.3% | 1.3% | 0.4% |
| 7 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.4%** | 0.746 | 66.2% | 33.8% | 5.6% | 3.4% | 23.2% | 67.0% | 0.4% | 0.4% |
| 8 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.959 | 67.5% | 32.5% | 8.7% | 8.2% | 0.0% | 83.1% | 0.0% | 0.0% |
| 9 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 10 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.959 | 67.5% | 32.5% | 8.7% | 8.2% | 0.0% | 83.1% | 0.0% | 0.0% |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.957 | 83.8% | 16.2% | 12.0% | 6.0% | 1.3% | 80.7% | 0.0% | 0.0% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.953 | 78.2% | 21.8% | 7.8% | 6.0% | 1.3% | 84.5% | 0.4% | 0.0% |
| 4 | 56 | stranger / citizen / good_record / poor / man_old | **0.0%** | 0.948 | 79.1% | 20.9% | 8.2% | 7.7% | 1.3% | 82.8% | 0.0% | 0.0% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.948 | 73.5% | 26.5% | 11.2% | 9.5% | 0.4% | 78.9% | 0.0% | 0.0% |
| 6 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0%** | 0.946 | 82.5% | 17.5% | 15.0% | 6.4% | 1.7% | 76.4% | 0.4% | 0.0% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.944 | 68.4% | 31.6% | 9.5% | 9.5% | 0.9% | 80.2% | 0.0% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.942 | 74.8% | 25.2% | 7.3% | 9.9% | 0.9% | 82.0% | 0.0% | 0.0% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.942 | 77.8% | 22.2% | 16.7% | 7.3% | 2.1% | 73.8% | 0.0% | 0.0% |
| 10 | 35 | stranger / mayor / good_record / rich / woman_young | **0.0%** | 0.942 | 77.8% | 22.2% | 7.8% | 9.1% | 1.3% | 81.9% | 0.0% | 0.0% |


### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.9430** | 0.943 | 62.8% | 37.2% | 11.6% | 9.2% | 1.1% | 77.9% | 0.0% | 0.2% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.9378** | 0.938 | 59.6% | 40.4% | 9.6% | 8.5% | 1.9% | 79.5% | 0.0% | 0.4% |
| 3 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.9367** | 0.937 | 63.0% | 37.0% | 9.8% | 10.0% | 1.3% | 78.4% | 0.0% | 0.4% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9358** | 0.936 | 62.8% | 37.2% | 10.9% | 8.5% | 2.1% | 78.2% | 0.0% | 0.2% |
| 5 | 8 | close_friend / mayor / good_record / poor / man_old | **0.9336** | 0.934 | 59.2% | 40.8% | 11.1% | 9.8% | 1.7% | 77.1% | 0.0% | 0.2% |
| 6 | 51 | stranger / citizen / good_record / rich / woman_young | **0.9313** | 0.931 | 63.2% | 36.8% | 10.0% | 9.4% | 2.1% | 78.0% | 0.0% | 0.4% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | **0.9309** | 0.931 | 62.6% | 37.4% | 7.9% | 9.0% | 2.4% | 80.0% | 0.0% | 0.6% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | **0.9304** | 0.930 | 62.2% | 37.8% | 9.4% | 10.5% | 1.7% | 78.4% | 0.0% | 0.0% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | **0.9284** | 0.928 | 61.3% | 38.7% | 10.1% | 10.7% | 1.7% | 76.4% | 0.0% | 1.1% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | **0.9280** | 0.928 | 63.2% | 36.8% | 7.9% | 9.2% | 2.6% | 79.9% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.5891** | 0.589 | 44.2% | 55.8% | 3.4% | 3.6% | 38.1% | 53.5% | 1.1% | 0.2% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.6061** | 0.606 | 44.2% | 55.8% | 2.8% | 4.3% | 36.3% | 54.9% | 0.4% | 1.3% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **0.6128** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **0.6166** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **0.6767** | 0.677 | 50.4% | 49.6% | 4.5% | 4.7% | 29.1% | 60.3% | 0.6% | 0.9% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.6831** | 0.683 | 50.4% | 49.6% | 5.3% | 5.1% | 28.2% | 60.3% | 0.9% | 0.2% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **0.6890** | 0.689 | 51.3% | 48.7% | 3.6% | 4.7% | 28.1% | 62.3% | 0.4% | 0.9% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.6949** | 0.695 | 51.1% | 48.9% | 1.7% | 6.6% | 26.5% | 64.3% | 0.6% | 0.2% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.6985** | 0.698 | 52.4% | 47.6% | 2.6% | 3.6% | 27.4% | 65.2% | 0.9% | 0.4% |
| 10 | 44 | stranger / mayor / poor_record / rich / man_old | **0.7270** | 0.727 | 54.3% | 45.7% | 4.3% | 3.2% | 24.6% | 66.7% | 1.1% | 0.2% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **55.8%** | 0.606 | 44.2% | 55.8% | 2.8% | 4.3% | 36.3% | 54.9% | 0.4% | 1.3% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **55.8%** | 0.589 | 44.2% | 55.8% | 3.4% | 3.6% | 38.1% | 53.5% | 1.1% | 0.2% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **55.6%** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **53.2%** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **49.6%** | 0.683 | 50.4% | 49.6% | 5.3% | 5.1% | 28.2% | 60.3% | 0.9% | 0.2% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | **49.6%** | 0.677 | 50.4% | 49.6% | 4.5% | 4.7% | 29.1% | 60.3% | 0.6% | 0.9% |
| 7 | 45 | stranger / mayor / poor_record / poor / woman_old | **48.9%** | 0.695 | 51.1% | 48.9% | 1.7% | 6.6% | 26.5% | 64.3% | 0.6% | 0.2% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **48.7%** | 0.689 | 51.3% | 48.7% | 3.6% | 4.7% | 28.1% | 62.3% | 0.4% | 0.9% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | **47.6%** | 0.698 | 52.4% | 47.6% | 2.6% | 3.6% | 27.4% | 65.2% | 0.9% | 0.4% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | **46.6%** | 0.740 | 53.4% | 46.6% | 3.6% | 5.1% | 22.9% | 66.7% | 0.2% | 1.5% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27 | close_friend / citizen / poor_record / rich / woman_young | **35.9%** | 0.851 | 64.1% | 35.9% | 7.3% | 4.9% | 12.2% | 75.0% | 0.2% | 0.4% |
| 2 | 51 | stranger / citizen / good_record / rich / woman_young | **36.8%** | 0.931 | 63.2% | 36.8% | 10.0% | 9.4% | 2.1% | 78.0% | 0.0% | 0.4% |
| 3 | 54 | stranger / citizen / good_record / poor / man_young | **36.8%** | 0.928 | 63.2% | 36.8% | 7.9% | 9.2% | 2.6% | 79.9% | 0.0% | 0.4% |
| 4 | 17 | close_friend / citizen / good_record / rich / woman_old | **37.0%** | 0.937 | 63.0% | 37.0% | 9.8% | 10.0% | 1.3% | 78.4% | 0.0% | 0.4% |
| 5 | 3 | close_friend / mayor / good_record / rich / woman_young | **37.2%** | 0.943 | 62.8% | 37.2% | 11.6% | 9.2% | 1.1% | 77.9% | 0.0% | 0.2% |
| 6 | 20 | close_friend / citizen / good_record / rich / man_old | **37.2%** | 0.936 | 62.8% | 37.2% | 10.9% | 8.5% | 2.1% | 78.2% | 0.0% | 0.2% |
| 7 | 25 | close_friend / citizen / poor_record / rich / woman_old | **37.2%** | 0.872 | 62.8% | 37.2% | 8.4% | 4.3% | 10.5% | 76.7% | 0.2% | 0.0% |
| 8 | 9 | close_friend / mayor / poor_record / rich / woman_old | **37.2%** | 0.859 | 62.8% | 37.2% | 7.1% | 3.4% | 11.5% | 77.1% | 0.9% | 0.0% |
| 9 | 56 | stranger / citizen / good_record / poor / man_old | **37.4%** | 0.931 | 62.6% | 37.4% | 7.9% | 9.0% | 2.4% | 80.0% | 0.0% | 0.6% |
| 10 | 49 | stranger / citizen / good_record / rich / woman_old | **37.6%** | 0.925 | 62.4% | 37.6% | 8.0% | 10.3% | 2.2% | 79.1% | 0.2% | 0.2% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | close_friend / mayor / good_record / poor / woman_young | **12.8%** | 0.920 | 57.7% | 42.3% | 12.8% | 11.8% | 2.1% | 73.3% | 0.0% | 0.0% |
| 2 | 5 | close_friend / mayor / good_record / poor / woman_old | **12.4%** | 0.916 | 59.4% | 40.6% | 12.4% | 12.0% | 2.1% | 73.1% | 0.2% | 0.2% |
| 3 | 1 | close_friend / mayor / good_record / rich / woman_old | **12.4%** | 0.912 | 59.2% | 40.8% | 12.4% | 12.4% | 2.6% | 72.6% | 0.0% | 0.0% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **12.0%** | 0.907 | 59.8% | 40.2% | 12.0% | 15.2% | 1.7% | 71.2% | 0.0% | 0.0% |
| 5 | 3 | close_friend / mayor / good_record / rich / woman_young | **11.6%** | 0.943 | 62.8% | 37.2% | 11.6% | 9.2% | 1.1% | 77.9% | 0.0% | 0.2% |
| 6 | 40 | stranger / mayor / good_record / poor / man_old | **11.6%** | 0.915 | 60.9% | 39.1% | 11.6% | 11.8% | 2.6% | 73.9% | 0.0% | 0.2% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **11.1%** | 0.934 | 59.2% | 40.8% | 11.1% | 9.8% | 1.7% | 77.1% | 0.0% | 0.2% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | **11.1%** | 0.923 | 59.0% | 41.0% | 11.1% | 9.4% | 3.0% | 76.5% | 0.0% | 0.0% |
| 9 | 20 | close_friend / citizen / good_record / rich / man_old | **10.9%** | 0.936 | 62.8% | 37.2% | 10.9% | 8.5% | 2.1% | 78.2% | 0.0% | 0.2% |
| 10 | 2 | close_friend / mayor / good_record / rich / man_young | **10.5%** | 0.912 | 59.8% | 40.2% | 10.5% | 14.1% | 1.7% | 73.1% | 0.0% | 0.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 45 | stranger / mayor / poor_record / poor / woman_old | **1.7%** | 0.695 | 51.1% | 48.9% | 1.7% | 6.6% | 26.5% | 64.3% | 0.6% | 0.2% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **1.9%** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 3 | 59 | stranger / citizen / poor_record / rich / woman_young | **2.1%** | 0.746 | 55.1% | 44.9% | 2.1% | 3.8% | 22.6% | 70.1% | 0.6% | 0.6% |
| 4 | 43 | stranger / mayor / poor_record / rich / woman_young | **2.6%** | 0.698 | 52.4% | 47.6% | 2.6% | 3.6% | 27.4% | 65.2% | 0.9% | 0.4% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | **2.6%** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 6 | 41 | stranger / mayor / poor_record / rich / woman_old | **2.8%** | 0.730 | 53.4% | 46.6% | 2.8% | 4.3% | 24.4% | 67.7% | 0.4% | 0.4% |
| 7 | 61 | stranger / citizen / poor_record / poor / woman_old | **2.8%** | 0.606 | 44.2% | 55.8% | 2.8% | 4.3% | 36.3% | 54.9% | 0.4% | 1.3% |
| 8 | 63 | stranger / citizen / poor_record / poor / woman_young | **3.4%** | 0.589 | 44.2% | 55.8% | 3.4% | 3.6% | 38.1% | 53.5% | 1.1% | 0.2% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **3.6%** | 0.740 | 53.4% | 46.6% | 3.6% | 5.1% | 22.9% | 66.7% | 0.2% | 1.5% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **3.6%** | 0.689 | 51.3% | 48.7% | 3.6% | 4.7% | 28.1% | 62.3% | 0.4% | 0.9% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 34 | stranger / mayor / good_record / rich / man_young | **15.2%** | 0.911 | 58.5% | 41.5% | 8.4% | 15.2% | 1.3% | 74.9% | 0.0% | 0.2% |
| 2 | 38 | stranger / mayor / good_record / poor / man_young | **15.2%** | 0.907 | 59.8% | 40.2% | 12.0% | 15.2% | 1.7% | 71.2% | 0.0% | 0.0% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | **15.2%** | 0.904 | 59.6% | 40.4% | 9.2% | 15.2% | 1.9% | 73.1% | 0.0% | 0.6% |
| 4 | 36 | stranger / mayor / good_record / rich / man_old | **15.0%** | 0.906 | 59.8% | 40.2% | 10.0% | 15.0% | 1.9% | 73.1% | 0.0% | 0.0% |
| 5 | 2 | close_friend / mayor / good_record / rich / man_young | **14.1%** | 0.912 | 59.8% | 40.2% | 10.5% | 14.1% | 1.7% | 73.1% | 0.0% | 0.6% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **13.5%** | 0.903 | 59.6% | 40.4% | 8.3% | 13.5% | 3.0% | 75.0% | 0.0% | 0.2% |
| 7 | 35 | stranger / mayor / good_record / rich / woman_young | **13.0%** | 0.920 | 57.7% | 42.3% | 9.6% | 13.0% | 1.5% | 75.6% | 0.0% | 0.2% |
| 8 | 55 | stranger / citizen / good_record / poor / woman_young | **12.6%** | 0.916 | 58.5% | 41.5% | 9.2% | 12.6% | 2.1% | 76.1% | 0.0% | 0.0% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | **12.4%** | 0.912 | 59.2% | 40.8% | 12.4% | 12.4% | 2.6% | 72.6% | 0.0% | 0.0% |
| 10 | 33 | stranger / mayor / good_record / rich / woman_old | **12.2%** | 0.915 | 57.5% | 42.5% | 9.9% | 12.2% | 2.4% | 75.6% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 32 | close_friend / citizen / poor_record / poor / man_old | **2.1%** | 0.835 | 59.2% | 40.8% | 6.6% | 2.1% | 15.0% | 75.6% | 0.4% | 0.2% |
| 2 | 58 | stranger / citizen / poor_record / rich / man_young | **2.6%** | 0.779 | 54.7% | 45.3% | 5.6% | 2.6% | 20.3% | 70.9% | 0.4% | 0.2% |
| 3 | 30 | close_friend / citizen / poor_record / poor / man_young | **3.0%** | 0.873 | 61.3% | 38.7% | 8.5% | 3.0% | 10.7% | 76.9% | 0.4% | 0.4% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | **3.0%** | 0.848 | 60.5% | 39.5% | 4.7% | 3.0% | 12.6% | 77.5% | 0.9% | 1.3% |
| 5 | 29 | close_friend / citizen / poor_record / poor / woman_old | **3.2%** | 0.820 | 61.3% | 38.7% | 6.2% | 3.2% | 15.4% | 73.7% | 0.9% | 0.6% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **3.2%** | 0.727 | 54.3% | 45.7% | 4.3% | 3.2% | 24.6% | 66.7% | 1.1% | 0.2% |
| 7 | 9 | close_friend / mayor / poor_record / rich / woman_old | **3.4%** | 0.859 | 62.8% | 37.2% | 7.1% | 3.4% | 11.5% | 77.1% | 0.9% | 0.0% |
| 8 | 16 | close_friend / mayor / poor_record / poor / man_old | **3.6%** | 0.843 | 59.2% | 40.8% | 5.6% | 3.6% | 13.5% | 76.7% | 0.4% | 0.2% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | **3.6%** | 0.698 | 52.4% | 47.6% | 2.6% | 3.6% | 27.4% | 65.2% | 0.9% | 0.4% |
| 10 | 28 | close_friend / citizen / poor_record / rich / man_old | **3.6%** | 0.869 | 62.4% | 37.6% | 8.6% | 3.6% | 10.5% | 75.8% | 0.6% | 0.9% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **38.1%** | 0.589 | 44.2% | 55.8% | 3.4% | 3.6% | 38.1% | 53.5% | 1.1% | 0.2% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **36.3%** | 0.606 | 44.2% | 55.8% | 2.8% | 4.3% | 36.3% | 54.9% | 0.4% | 1.3% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **34.0%** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **33.1%** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **29.1%** | 0.677 | 50.4% | 49.6% | 4.5% | 4.7% | 29.1% | 60.3% | 0.6% | 0.9% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **28.2%** | 0.683 | 50.4% | 49.6% | 5.3% | 5.1% | 28.2% | 60.3% | 0.9% | 0.2% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **28.1%** | 0.689 | 51.3% | 48.7% | 3.6% | 4.7% | 28.1% | 62.3% | 0.4% | 0.9% |
| 8 | 43 | stranger / mayor / poor_record / rich / woman_young | **27.4%** | 0.698 | 52.4% | 47.6% | 2.6% | 3.6% | 27.4% | 65.2% | 0.9% | 0.4% |
| 9 | 45 | stranger / mayor / poor_record / poor / woman_old | **26.5%** | 0.695 | 51.1% | 48.9% | 1.7% | 6.6% | 26.5% | 64.3% | 0.6% | 0.2% |
| 10 | 44 | stranger / mayor / poor_record / rich / man_old | **24.6%** | 0.727 | 54.3% | 45.7% | 4.3% | 3.2% | 24.6% | 66.7% | 1.1% | 0.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **1.1%** | 0.943 | 62.8% | 37.2% | 11.6% | 9.2% | 1.1% | 77.9% | 0.0% | 0.2% |
| 2 | 17 | close_friend / citizen / good_record / rich / woman_old | **1.3%** | 0.937 | 63.0% | 37.0% | 9.8% | 10.0% | 1.3% | 78.4% | 0.0% | 0.4% |
| 3 | 34 | stranger / mayor / good_record / rich / man_young | **1.3%** | 0.911 | 58.5% | 41.5% | 8.4% | 15.2% | 1.3% | 74.9% | 0.0% | 0.2% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | **1.5%** | 0.926 | 59.6% | 40.4% | 9.6% | 11.8% | 1.5% | 77.1% | 0.0% | 0.0% |
| 5 | 35 | stranger / mayor / good_record / rich / woman_young | **1.5%** | 0.920 | 57.7% | 42.3% | 9.6% | 13.0% | 1.5% | 75.6% | 0.0% | 0.2% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | **1.7%** | 0.934 | 59.2% | 40.8% | 11.1% | 9.8% | 1.7% | 77.1% | 0.0% | 0.2% |
| 7 | 2 | close_friend / mayor / good_record / rich / man_young | **1.7%** | 0.912 | 59.8% | 40.2% | 10.5% | 14.1% | 1.7% | 73.1% | 0.0% | 0.6% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | **1.7%** | 0.907 | 59.8% | 40.2% | 12.0% | 15.2% | 1.7% | 71.2% | 0.0% | 0.0% |
| 9 | 18 | close_friend / citizen / good_record / rich / man_young | **1.7%** | 0.930 | 62.2% | 37.8% | 9.4% | 10.5% | 1.7% | 78.4% | 0.0% | 0.0% |
| 10 | 24 | close_friend / citizen / good_record / poor / man_old | **1.7%** | 0.928 | 61.3% | 38.7% | 10.1% | 10.7% | 1.7% | 76.4% | 0.0% | 1.1% |


**CHECKED_TRUE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 56 | stranger / citizen / good_record / poor / man_old | **80.0%** | 0.931 | 62.6% | 37.4% | 7.9% | 9.0% | 2.4% | 80.0% | 0.0% | 0.6% |
| 2 | 54 | stranger / citizen / good_record / poor / man_young | **79.9%** | 0.928 | 63.2% | 36.8% | 7.9% | 9.2% | 2.6% | 79.9% | 0.0% | 0.4% |
| 3 | 21 | close_friend / citizen / good_record / poor / woman_old | **79.5%** | 0.938 | 59.6% | 40.4% | 9.6% | 8.5% | 1.9% | 79.5% | 0.0% | 0.4% |
| 4 | 49 | stranger / citizen / good_record / rich / woman_old | **79.1%** | 0.925 | 62.4% | 37.6% | 8.0% | 10.3% | 2.2% | 79.1% | 0.2% | 0.2% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | **78.8%** | 0.927 | 59.2% | 40.8% | 8.5% | 10.3% | 2.1% | 78.8% | 0.0% | 0.2% |
| 6 | 17 | close_friend / citizen / good_record / rich / woman_old | **78.4%** | 0.937 | 63.0% | 37.0% | 9.8% | 10.0% | 1.3% | 78.4% | 0.0% | 0.4% |
| 7 | 18 | close_friend / citizen / good_record / rich / man_young | **78.4%** | 0.930 | 62.2% | 37.8% | 9.4% | 10.5% | 1.7% | 78.4% | 0.0% | 0.0% |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | **78.2%** | 0.936 | 62.8% | 37.2% | 10.9% | 8.5% | 2.1% | 78.2% | 0.0% | 0.2% |
| 9 | 50 | stranger / citizen / good_record / rich / man_young | **78.2%** | 0.917 | 60.7% | 39.3% | 7.9% | 10.5% | 3.0% | 78.2% | 0.0% | 0.4% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | **78.0%** | 0.931 | 63.2% | 36.8% | 10.0% | 9.4% | 2.1% | 78.0% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **53.5%** | 0.589 | 44.2% | 55.8% | 3.4% | 3.6% | 38.1% | 53.5% | 1.1% | 0.2% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **54.9%** | 0.606 | 44.2% | 55.8% | 2.8% | 4.3% | 36.3% | 54.9% | 0.4% | 1.3% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **55.6%** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **56.0%** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **60.3%** | 0.683 | 50.4% | 49.6% | 5.3% | 5.1% | 28.2% | 60.3% | 0.9% | 0.2% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | **60.3%** | 0.677 | 50.4% | 49.6% | 4.5% | 4.7% | 29.1% | 60.3% | 0.6% | 0.9% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **62.3%** | 0.689 | 51.3% | 48.7% | 3.6% | 4.7% | 28.1% | 62.3% | 0.4% | 0.9% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | **64.3%** | 0.695 | 51.1% | 48.9% | 1.7% | 6.6% | 26.5% | 64.3% | 0.6% | 0.2% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | **65.2%** | 0.698 | 52.4% | 47.6% | 2.6% | 3.6% | 27.4% | 65.2% | 0.9% | 0.4% |
| 10 | 42 | stranger / mayor / poor_record / rich / man_young | **66.5%** | 0.742 | 54.9% | 45.1% | 5.1% | 4.7% | 23.1% | 66.5% | 0.2% | 0.4% |


**CHECKED_FALSE (%)** *(Note: 30 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **2.4%** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 2 | 31 | close_friend / citizen / poor_record / poor / woman_young | **1.5%** | 0.818 | 61.8% | 38.2% | 6.9% | 4.3% | 14.3% | 71.7% | 1.5% | 1.3% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **1.3%** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | **1.1%** | 0.782 | 59.6% | 40.4% | 4.1% | 4.7% | 18.2% | 71.2% | 1.1% | 0.6% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.1%** | 0.589 | 44.2% | 55.8% | 3.4% | 3.6% | 38.1% | 53.5% | 1.1% | 0.2% |
| 6 | 12 | close_friend / mayor / poor_record / rich / man_old | **1.1%** | 0.842 | 59.4% | 40.6% | 7.9% | 5.8% | 11.8% | 73.1% | 1.1% | 0.4% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | **1.1%** | 0.727 | 54.3% | 45.7% | 4.3% | 3.2% | 24.6% | 66.7% | 1.1% | 0.2% |
| 8 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.9%** | 0.848 | 60.5% | 39.5% | 4.7% | 3.0% | 12.6% | 77.5% | 0.9% | 1.3% |
| 9 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.9%** | 0.859 | 62.8% | 37.2% | 7.1% | 3.4% | 11.5% | 77.1% | 0.9% | 0.0% |
| 10 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.9%** | 0.839 | 61.8% | 38.2% | 5.3% | 3.8% | 13.2% | 76.5% | 0.9% | 0.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0%** | 0.943 | 62.8% | 37.2% | 11.6% | 9.2% | 1.1% | 77.9% | 0.0% | 0.2% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.938 | 59.6% | 40.4% | 9.6% | 8.5% | 1.9% | 79.5% | 0.0% | 0.4% |
| 3 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.937 | 63.0% | 37.0% | 9.8% | 10.0% | 1.3% | 78.4% | 0.0% | 0.4% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.936 | 62.8% | 37.2% | 10.9% | 8.5% | 2.1% | 78.2% | 0.0% | 0.2% |
| 5 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.934 | 59.2% | 40.8% | 11.1% | 9.8% | 1.7% | 77.1% | 0.0% | 0.2% |
| 6 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.931 | 63.2% | 36.8% | 10.0% | 9.4% | 2.1% | 78.0% | 0.0% | 0.4% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | **0.0%** | 0.931 | 62.6% | 37.4% | 7.9% | 9.0% | 2.4% | 80.0% | 0.0% | 0.6% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.930 | 62.2% | 37.8% | 9.4% | 10.5% | 1.7% | 78.4% | 0.0% | 0.0% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | **0.0%** | 0.928 | 61.3% | 38.7% | 10.1% | 10.7% | 1.7% | 76.4% | 0.0% | 1.1% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.928 | 63.2% | 36.8% | 7.9% | 9.2% | 2.6% | 79.9% | 0.0% | 0.4% |


**NOT_MENTIONED (%)** *(Note: 12 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 60 | stranger / citizen / poor_record / rich / man_old | **1.5%** | 0.740 | 53.4% | 46.6% | 3.6% | 5.1% | 22.9% | 66.7% | 0.2% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **1.5%** | 0.613 | 46.8% | 53.2% | 1.9% | 5.8% | 34.0% | 55.6% | 1.3% | 1.5% |
| 3 | 14 | close_friend / mayor / poor_record / poor / man_young | **1.3%** | 0.848 | 60.5% | 39.5% | 4.7% | 3.0% | 12.6% | 77.5% | 0.9% | 1.3% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | **1.3%** | 0.818 | 61.8% | 38.2% | 6.9% | 4.3% | 14.3% | 71.7% | 1.5% | 1.3% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | **1.3%** | 0.926 | 60.9% | 39.1% | 10.3% | 9.4% | 2.6% | 76.5% | 0.0% | 1.3% |
| 6 | 61 | stranger / citizen / poor_record / poor / woman_old | **1.3%** | 0.606 | 44.2% | 55.8% | 2.8% | 4.3% | 36.3% | 54.9% | 0.4% | 1.3% |
| 7 | 24 | close_friend / citizen / good_record / poor / man_old | **1.1%** | 0.928 | 61.3% | 38.7% | 10.1% | 10.7% | 1.7% | 76.4% | 0.0% | 1.1% |
| 8 | 57 | stranger / citizen / poor_record / rich / woman_old | **1.1%** | 0.784 | 57.5% | 42.5% | 4.7% | 4.3% | 18.4% | 70.7% | 0.9% | 1.1% |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | **1.1%** | 0.617 | 44.4% | 55.6% | 2.6% | 4.9% | 33.1% | 56.0% | 2.4% | 1.1% |
| 10 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.9%** | 0.869 | 62.4% | 37.6% | 8.6% | 3.6% | 10.5% | 75.8% | 0.6% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.930 | 62.2% | 37.8% | 9.4% | 10.5% | 1.7% | 78.4% | 0.0% | 0.0% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0%** | 0.926 | 59.6% | 40.4% | 9.6% | 11.8% | 1.5% | 77.1% | 0.0% | 0.0% |
| 3 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.923 | 59.0% | 41.0% | 11.1% | 9.4% | 3.0% | 76.5% | 0.0% | 0.0% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0%** | 0.923 | 62.0% | 38.0% | 9.2% | 11.6% | 1.9% | 77.3% | 0.0% | 0.0% |
| 5 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.920 | 57.7% | 42.3% | 12.8% | 11.8% | 2.1% | 73.3% | 0.0% | 0.0% |
| 6 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.916 | 58.5% | 41.5% | 9.2% | 12.6% | 2.1% | 76.1% | 0.0% | 0.0% |
| 7 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.915 | 57.5% | 42.5% | 9.9% | 12.2% | 2.4% | 75.6% | 0.0% | 0.0% |
| 8 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.912 | 59.2% | 40.8% | 12.4% | 12.4% | 2.6% | 72.6% | 0.0% | 0.0% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | **0.0%** | 0.907 | 59.8% | 40.2% | 12.0% | 15.2% | 1.7% | 71.2% | 0.0% | 0.0% |
| 10 | 36 | stranger / mayor / good_record / rich / man_old | **0.0%** | 0.906 | 59.8% | 40.2% | 10.0% | 15.0% | 1.9% | 73.1% | 0.0% | 0.0% |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | close_friend / citizen / good_record / poor / man_young | **0.9893** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.9871** | 0.987 | 99.1% | 0.9% | 5.1% | 2.6% | 0.0% | 91.9% | 0.0% | 0.4% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | **0.9850** | 0.985 | 99.6% | 0.4% | 3.4% | 2.1% | 0.4% | 94.0% | 0.0% | 0.0% |
| 4 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.9850** | 0.985 | 100.0% | 0.0% | 4.7% | 3.0% | 0.0% | 92.3% | 0.0% | 0.0% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | **0.9850** | 0.985 | 99.6% | 0.4% | 6.4% | 3.0% | 0.0% | 90.6% | 0.0% | 0.0% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.9828** | 0.983 | 100.0% | 0.0% | 6.0% | 3.4% | 0.0% | 90.2% | 0.0% | 0.4% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.9808** | 0.981 | 100.0% | 0.0% | 5.6% | 3.8% | 0.0% | 90.6% | 0.0% | 0.0% |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9808** | 0.981 | 100.0% | 0.0% | 3.4% | 2.1% | 0.9% | 93.6% | 0.0% | 0.0% |
| 9 | 8 | close_friend / mayor / good_record / poor / man_old | **0.9786** | 0.979 | 99.6% | 0.4% | 3.8% | 4.3% | 0.0% | 91.9% | 0.0% | 0.0% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | **0.9765** | 0.976 | 99.6% | 0.4% | 4.7% | 3.8% | 0.4% | 91.0% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.5513** | 0.551 | 56.8% | 43.2% | 2.6% | 3.4% | 42.3% | 50.9% | 0.9% | 0.0% |
| 2 | 62 | stranger / citizen / poor_record / poor / man_young | **0.5726** | 0.573 | 60.7% | 39.3% | 1.3% | 3.4% | 38.9% | 54.3% | 2.1% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **0.5812** | 0.581 | 63.2% | 36.8% | 1.3% | 5.1% | 38.0% | 54.3% | 1.3% | 0.0% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.5905** | 0.591 | 61.5% | 38.5% | 1.3% | 3.4% | 38.9% | 55.6% | 0.0% | 0.9% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **0.6931** | 0.693 | 75.2% | 24.8% | 3.8% | 3.0% | 28.6% | 63.7% | 0.4% | 0.4% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.7115** | 0.712 | 73.5% | 26.5% | 4.3% | 4.7% | 25.6% | 64.5% | 0.9% | 0.0% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.7115** | 0.712 | 78.6% | 21.4% | 2.6% | 3.8% | 26.1% | 66.7% | 0.9% | 0.0% |
| 8 | 60 | stranger / citizen / poor_record / rich / man_old | **0.7167** | 0.717 | 76.9% | 23.1% | 1.7% | 2.6% | 26.5% | 68.4% | 0.4% | 0.4% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **0.7189** | 0.719 | 76.1% | 23.9% | 1.7% | 4.7% | 24.9% | 67.8% | 0.9% | 0.0% |
| 10 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.7308** | 0.731 | 76.5% | 23.5% | 1.3% | 3.4% | 24.8% | 70.1% | 0.4% | 0.0% |


**SKIP Rate (%)** *(Note: 19 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **43.2%** | 0.551 | 56.8% | 43.2% | 2.6% | 3.4% | 42.3% | 50.9% | 0.9% | 0.0% |
| 2 | 62 | stranger / citizen / poor_record / poor / man_young | **39.3%** | 0.573 | 60.7% | 39.3% | 1.3% | 3.4% | 38.9% | 54.3% | 2.1% | 0.0% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **38.5%** | 0.591 | 61.5% | 38.5% | 1.3% | 3.4% | 38.9% | 55.6% | 0.0% | 0.9% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **36.8%** | 0.581 | 63.2% | 36.8% | 1.3% | 5.1% | 38.0% | 54.3% | 1.3% | 0.0% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **26.5%** | 0.712 | 73.5% | 26.5% | 4.3% | 4.7% | 25.6% | 64.5% | 0.9% | 0.0% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | **24.8%** | 0.693 | 75.2% | 24.8% | 3.8% | 3.0% | 28.6% | 63.7% | 0.4% | 0.4% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **23.9%** | 0.719 | 76.1% | 23.9% | 1.7% | 4.7% | 24.9% | 67.8% | 0.9% | 0.0% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | **23.5%** | 0.731 | 76.5% | 23.5% | 1.3% | 3.4% | 24.8% | 70.1% | 0.4% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **23.1%** | 0.717 | 76.9% | 23.1% | 1.7% | 2.6% | 26.5% | 68.4% | 0.4% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | **21.4%** | 0.712 | 78.6% | 21.4% | 2.6% | 3.8% | 26.1% | 66.7% | 0.9% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |
| 2 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.985 | 100.0% | 0.0% | 4.7% | 3.0% | 0.0% | 92.3% | 0.0% | 0.0% |
| 3 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.983 | 100.0% | 0.0% | 6.0% | 3.4% | 0.0% | 90.2% | 0.0% | 0.4% |
| 4 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.981 | 100.0% | 0.0% | 5.6% | 3.8% | 0.0% | 90.6% | 0.0% | 0.0% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.981 | 100.0% | 0.0% | 3.4% | 2.1% | 0.9% | 93.6% | 0.0% | 0.0% |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.976 | 100.0% | 0.0% | 3.0% | 3.8% | 0.4% | 92.7% | 0.0% | 0.0% |
| 7 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.976 | 100.0% | 0.0% | 3.4% | 4.7% | 0.0% | 91.9% | 0.0% | 0.0% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.974 | 100.0% | 0.0% | 3.8% | 4.3% | 0.4% | 91.5% | 0.0% | 0.0% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.974 | 100.0% | 0.0% | 5.1% | 4.3% | 0.4% | 89.7% | 0.0% | 0.4% |
| 10 | 2 | close_friend / mayor / good_record / rich / man_young | **0.0%** | 0.972 | 100.0% | 0.0% | 3.4% | 5.6% | 0.0% | 91.0% | 0.0% | 0.0% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 30 | close_friend / citizen / poor_record / poor / man_young | **8.1%** | 0.917 | 95.3% | 4.7% | 8.1% | 1.3% | 6.8% | 82.9% | 0.9% | 0.0% |
| 2 | 25 | close_friend / citizen / poor_record / rich / woman_old | **7.3%** | 0.938 | 97.4% | 2.6% | 7.3% | 1.3% | 5.6% | 85.8% | 0.0% | 0.0% |
| 3 | 54 | stranger / citizen / good_record / poor / man_young | **6.4%** | 0.985 | 99.6% | 0.4% | 6.4% | 3.0% | 0.0% | 90.6% | 0.0% | 0.0% |
| 4 | 10 | close_friend / mayor / poor_record / rich / man_young | **6.4%** | 0.940 | 99.1% | 0.9% | 6.4% | 1.7% | 5.1% | 86.8% | 0.0% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **6.0%** | 0.983 | 100.0% | 0.0% | 6.0% | 3.4% | 0.0% | 90.2% | 0.0% | 0.4% |
| 6 | 28 | close_friend / citizen / poor_record / rich / man_old | **6.0%** | 0.947 | 98.7% | 1.3% | 6.0% | 1.3% | 4.7% | 88.0% | 0.0% | 0.0% |
| 7 | 27 | close_friend / citizen / poor_record / rich / woman_young | **6.0%** | 0.912 | 96.2% | 3.8% | 6.0% | 2.1% | 7.7% | 83.8% | 0.0% | 0.4% |
| 8 | 7 | close_friend / mayor / good_record / poor / woman_young | **5.6%** | 0.981 | 100.0% | 0.0% | 5.6% | 3.8% | 0.0% | 90.6% | 0.0% | 0.0% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **5.6%** | 0.829 | 83.8% | 16.2% | 5.6% | 2.6% | 15.0% | 76.1% | 0.9% | 0.0% |
| 10 | 40 | stranger / mayor / good_record / poor / man_old | **5.2%** | 0.966 | 100.0% | 0.0% | 5.2% | 5.2% | 0.9% | 88.4% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.0%** | 0.765 | 82.1% | 17.9% | 0.0% | 3.4% | 21.4% | 74.8% | 0.4% | 0.0% |
| 2 | 45 | stranger / mayor / poor_record / poor / woman_old | **1.3%** | 0.731 | 76.5% | 23.5% | 1.3% | 3.4% | 24.8% | 70.1% | 0.4% | 0.0% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **1.3%** | 0.591 | 61.5% | 38.5% | 1.3% | 3.4% | 38.9% | 55.6% | 0.0% | 0.9% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **1.3%** | 0.581 | 63.2% | 36.8% | 1.3% | 5.1% | 38.0% | 54.3% | 1.3% | 0.0% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | **1.3%** | 0.573 | 60.7% | 39.3% | 1.3% | 3.4% | 38.9% | 54.3% | 2.1% | 0.0% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **1.7%** | 0.750 | 80.8% | 19.2% | 1.7% | 3.0% | 22.6% | 71.8% | 0.9% | 0.0% |
| 7 | 60 | stranger / citizen / poor_record / rich / man_old | **1.7%** | 0.717 | 76.9% | 23.1% | 1.7% | 2.6% | 26.5% | 68.4% | 0.4% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **1.7%** | 0.719 | 76.1% | 23.9% | 1.7% | 4.7% | 24.9% | 67.8% | 0.9% | 0.0% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | **2.6%** | 0.712 | 78.6% | 21.4% | 2.6% | 3.8% | 26.1% | 66.7% | 0.9% | 0.0% |
| 10 | 63 | stranger / citizen / poor_record / poor / woman_young | **2.6%** | 0.551 | 56.8% | 43.2% | 2.6% | 3.4% | 42.3% | 50.9% | 0.9% | 0.0% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 38 | stranger / mayor / good_record / poor / man_young | **8.5%** | 0.953 | 100.0% | 0.0% | 4.3% | 8.5% | 0.4% | 86.8% | 0.0% | 0.0% |
| 2 | 24 | close_friend / citizen / good_record / poor / man_old | **7.3%** | 0.964 | 99.6% | 0.4% | 3.8% | 7.3% | 0.0% | 88.5% | 0.0% | 0.4% |
| 3 | 36 | stranger / mayor / good_record / rich / man_old | **7.3%** | 0.951 | 99.6% | 0.4% | 3.4% | 7.3% | 1.3% | 88.0% | 0.0% | 0.0% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **6.4%** | 0.964 | 100.0% | 0.0% | 3.9% | 6.4% | 0.4% | 89.3% | 0.0% | 0.0% |
| 5 | 1 | close_friend / mayor / good_record / rich / woman_old | **6.4%** | 0.968 | 100.0% | 0.0% | 4.7% | 6.4% | 0.0% | 88.9% | 0.0% | 0.0% |
| 6 | 56 | stranger / citizen / good_record / poor / man_old | **6.0%** | 0.953 | 99.1% | 0.9% | 5.1% | 6.0% | 1.7% | 87.2% | 0.0% | 0.0% |
| 7 | 2 | close_friend / mayor / good_record / rich / man_young | **5.6%** | 0.972 | 100.0% | 0.0% | 3.4% | 5.6% | 0.0% | 91.0% | 0.0% | 0.0% |
| 8 | 23 | close_friend / citizen / good_record / poor / woman_young | **5.6%** | 0.964 | 99.1% | 0.9% | 4.3% | 5.6% | 0.9% | 89.3% | 0.0% | 0.0% |
| 9 | 35 | stranger / mayor / good_record / rich / woman_young | **5.6%** | 0.964 | 100.0% | 0.0% | 3.8% | 5.6% | 0.9% | 89.7% | 0.0% | 0.0% |
| 10 | 40 | stranger / mayor / good_record / poor / man_old | **5.2%** | 0.966 | 100.0% | 0.0% | 5.2% | 5.2% | 0.9% | 88.4% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.9%** | 0.936 | 98.3% | 1.7% | 4.7% | 0.9% | 5.6% | 88.5% | 0.4% | 0.0% |
| 2 | 32 | close_friend / citizen / poor_record / poor / man_old | **0.9%** | 0.897 | 93.2% | 6.8% | 3.4% | 0.9% | 9.4% | 85.9% | 0.4% | 0.0% |
| 3 | 28 | close_friend / citizen / poor_record / rich / man_old | **1.3%** | 0.947 | 98.7% | 1.3% | 6.0% | 1.3% | 4.7% | 88.0% | 0.0% | 0.0% |
| 4 | 30 | close_friend / citizen / poor_record / poor / man_young | **1.3%** | 0.917 | 95.3% | 4.7% | 8.1% | 1.3% | 6.8% | 82.9% | 0.9% | 0.0% |
| 5 | 11 | close_friend / mayor / poor_record / rich / woman_young | **1.3%** | 0.900 | 96.6% | 3.4% | 3.8% | 1.3% | 9.4% | 85.5% | 0.0% | 0.0% |
| 6 | 25 | close_friend / citizen / poor_record / rich / woman_old | **1.3%** | 0.938 | 97.4% | 2.6% | 7.3% | 1.3% | 5.6% | 85.8% | 0.0% | 0.0% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | **1.7%** | 0.957 | 99.1% | 0.9% | 4.7% | 1.7% | 3.4% | 89.7% | 0.0% | 0.4% |
| 8 | 10 | close_friend / mayor / poor_record / rich / man_young | **1.7%** | 0.940 | 99.1% | 0.9% | 6.4% | 1.7% | 5.1% | 86.8% | 0.0% | 0.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **1.7%** | 0.769 | 81.2% | 18.8% | 3.0% | 1.7% | 21.8% | 73.1% | 0.4% | 0.0% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | **2.1%** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |


**SKEPTICAL (%)** *(Note: 11 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **42.3%** | 0.551 | 56.8% | 43.2% | 2.6% | 3.4% | 42.3% | 50.9% | 0.9% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **38.9%** | 0.591 | 61.5% | 38.5% | 1.3% | 3.4% | 38.9% | 55.6% | 0.0% | 0.9% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **38.9%** | 0.573 | 60.7% | 39.3% | 1.3% | 3.4% | 38.9% | 54.3% | 2.1% | 0.0% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **38.0%** | 0.581 | 63.2% | 36.8% | 1.3% | 5.1% | 38.0% | 54.3% | 1.3% | 0.0% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **28.6%** | 0.693 | 75.2% | 24.8% | 3.8% | 3.0% | 28.6% | 63.7% | 0.4% | 0.4% |
| 6 | 60 | stranger / citizen / poor_record / rich / man_old | **26.5%** | 0.717 | 76.9% | 23.1% | 1.7% | 2.6% | 26.5% | 68.4% | 0.4% | 0.4% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | **26.1%** | 0.712 | 78.6% | 21.4% | 2.6% | 3.8% | 26.1% | 66.7% | 0.9% | 0.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **25.6%** | 0.712 | 73.5% | 26.5% | 4.3% | 4.7% | 25.6% | 64.5% | 0.9% | 0.0% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **24.9%** | 0.719 | 76.1% | 23.9% | 1.7% | 4.7% | 24.9% | 67.8% | 0.9% | 0.0% |
| 10 | 45 | stranger / mayor / poor_record / poor / woman_old | **24.8%** | 0.731 | 76.5% | 23.5% | 1.3% | 3.4% | 24.8% | 70.1% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.987 | 99.1% | 0.9% | 5.1% | 2.6% | 0.0% | 91.9% | 0.0% | 0.4% |
| 3 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.985 | 100.0% | 0.0% | 4.7% | 3.0% | 0.0% | 92.3% | 0.0% | 0.0% |
| 4 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.985 | 99.6% | 0.4% | 6.4% | 3.0% | 0.0% | 90.6% | 0.0% | 0.0% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.983 | 100.0% | 0.0% | 6.0% | 3.4% | 0.0% | 90.2% | 0.0% | 0.4% |
| 6 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.981 | 100.0% | 0.0% | 5.6% | 3.8% | 0.0% | 90.6% | 0.0% | 0.0% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.979 | 99.6% | 0.4% | 3.8% | 4.3% | 0.0% | 91.9% | 0.0% | 0.0% |
| 8 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.976 | 100.0% | 0.0% | 3.4% | 4.7% | 0.0% | 91.9% | 0.0% | 0.0% |
| 9 | 2 | close_friend / mayor / good_record / rich / man_young | **0.0%** | 0.972 | 100.0% | 0.0% | 3.4% | 5.6% | 0.0% | 91.0% | 0.0% | 0.0% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.968 | 100.0% | 0.0% | 4.7% | 6.4% | 0.0% | 88.9% | 0.0% | 0.0% |


**CHECKED_TRUE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **94.0%** | 0.985 | 99.6% | 0.4% | 3.4% | 2.1% | 0.4% | 94.0% | 0.0% | 0.0% |
| 2 | 20 | close_friend / citizen / good_record / rich / man_old | **93.6%** | 0.981 | 100.0% | 0.0% | 3.4% | 2.1% | 0.9% | 93.6% | 0.0% | 0.0% |
| 3 | 22 | close_friend / citizen / good_record / poor / man_young | **92.7%** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |
| 4 | 18 | close_friend / citizen / good_record / rich / man_young | **92.7%** | 0.976 | 100.0% | 0.0% | 3.0% | 3.8% | 0.4% | 92.7% | 0.0% | 0.0% |
| 5 | 17 | close_friend / citizen / good_record / rich / woman_old | **92.3%** | 0.985 | 100.0% | 0.0% | 4.7% | 3.0% | 0.0% | 92.3% | 0.0% | 0.0% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **91.9%** | 0.987 | 99.1% | 0.9% | 5.1% | 2.6% | 0.0% | 91.9% | 0.0% | 0.4% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **91.9%** | 0.979 | 99.6% | 0.4% | 3.8% | 4.3% | 0.0% | 91.9% | 0.0% | 0.0% |
| 8 | 55 | stranger / citizen / good_record / poor / woman_young | **91.9%** | 0.976 | 100.0% | 0.0% | 3.4% | 4.7% | 0.0% | 91.9% | 0.0% | 0.0% |
| 9 | 6 | close_friend / mayor / good_record / poor / man_young | **91.5%** | 0.974 | 100.0% | 0.0% | 3.8% | 4.3% | 0.4% | 91.5% | 0.0% | 0.0% |
| 10 | 3 | close_friend / mayor / good_record / rich / woman_young | **91.5%** | 0.970 | 100.0% | 0.0% | 3.0% | 4.3% | 0.9% | 91.5% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **50.9%** | 0.551 | 56.8% | 43.2% | 2.6% | 3.4% | 42.3% | 50.9% | 0.9% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **54.3%** | 0.581 | 63.2% | 36.8% | 1.3% | 5.1% | 38.0% | 54.3% | 1.3% | 0.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **54.3%** | 0.573 | 60.7% | 39.3% | 1.3% | 3.4% | 38.9% | 54.3% | 2.1% | 0.0% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **55.6%** | 0.591 | 61.5% | 38.5% | 1.3% | 3.4% | 38.9% | 55.6% | 0.0% | 0.9% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **63.7%** | 0.693 | 75.2% | 24.8% | 3.8% | 3.0% | 28.6% | 63.7% | 0.4% | 0.4% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **64.5%** | 0.712 | 73.5% | 26.5% | 4.3% | 4.7% | 25.6% | 64.5% | 0.9% | 0.0% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | **66.7%** | 0.712 | 78.6% | 21.4% | 2.6% | 3.8% | 26.1% | 66.7% | 0.9% | 0.0% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **67.8%** | 0.719 | 76.1% | 23.9% | 1.7% | 4.7% | 24.9% | 67.8% | 0.9% | 0.0% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **68.4%** | 0.717 | 76.9% | 23.1% | 1.7% | 2.6% | 26.5% | 68.4% | 0.4% | 0.4% |
| 10 | 42 | stranger / mayor / poor_record / rich / man_young | **68.8%** | 0.748 | 85.0% | 15.0% | 3.8% | 4.3% | 23.1% | 68.8% | 0.0% | 0.0% |


**CHECKED_FALSE (%)** *(Note: 42 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **2.1%** | 0.573 | 60.7% | 39.3% | 1.3% | 3.4% | 38.9% | 54.3% | 2.1% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **1.3%** | 0.581 | 63.2% | 36.8% | 1.3% | 5.1% | 38.0% | 54.3% | 1.3% | 0.0% |
| 3 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.9%** | 0.933 | 97.4% | 2.6% | 3.4% | 2.1% | 4.7% | 88.0% | 0.9% | 0.9% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.9%** | 0.886 | 94.0% | 6.0% | 5.2% | 2.1% | 9.4% | 82.4% | 0.9% | 0.0% |
| 5 | 48 | stranger / mayor / poor_record / poor / man_old | **0.9%** | 0.719 | 76.1% | 23.9% | 1.7% | 4.7% | 24.9% | 67.8% | 0.9% | 0.0% |
| 6 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.9%** | 0.936 | 98.3% | 1.7% | 5.1% | 2.6% | 4.3% | 87.2% | 0.9% | 0.0% |
| 7 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.9%** | 0.917 | 95.3% | 4.7% | 8.1% | 1.3% | 6.8% | 82.9% | 0.9% | 0.0% |
| 8 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.9%** | 0.829 | 83.8% | 16.2% | 5.6% | 2.6% | 15.0% | 76.1% | 0.9% | 0.0% |
| 9 | 44 | stranger / mayor / poor_record / rich / man_old | **0.9%** | 0.750 | 80.8% | 19.2% | 1.7% | 3.0% | 22.6% | 71.8% | 0.9% | 0.0% |
| 10 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.9%** | 0.712 | 73.5% | 26.5% | 4.3% | 4.7% | 25.6% | 64.5% | 0.9% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.987 | 99.1% | 0.9% | 5.1% | 2.6% | 0.0% | 91.9% | 0.0% | 0.4% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.985 | 99.6% | 0.4% | 3.4% | 2.1% | 0.4% | 94.0% | 0.0% | 0.0% |
| 4 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.985 | 100.0% | 0.0% | 4.7% | 3.0% | 0.0% | 92.3% | 0.0% | 0.0% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.985 | 99.6% | 0.4% | 6.4% | 3.0% | 0.0% | 90.6% | 0.0% | 0.0% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.983 | 100.0% | 0.0% | 6.0% | 3.4% | 0.0% | 90.2% | 0.0% | 0.4% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.981 | 100.0% | 0.0% | 5.6% | 3.8% | 0.0% | 90.6% | 0.0% | 0.0% |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.981 | 100.0% | 0.0% | 3.4% | 2.1% | 0.9% | 93.6% | 0.0% | 0.0% |
| 9 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.979 | 99.6% | 0.4% | 3.8% | 4.3% | 0.0% | 91.9% | 0.0% | 0.0% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.976 | 99.6% | 0.4% | 4.7% | 3.8% | 0.4% | 91.0% | 0.0% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 46 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.9%** | 0.933 | 97.4% | 2.6% | 3.4% | 2.1% | 4.7% | 88.0% | 0.9% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.9%** | 0.591 | 61.5% | 38.5% | 1.3% | 3.4% | 38.9% | 55.6% | 0.0% | 0.9% |
| 3 | 40 | stranger / mayor / good_record / poor / man_old | **0.4%** | 0.966 | 100.0% | 0.0% | 5.2% | 5.2% | 0.9% | 88.4% | 0.0% | 0.4% |
| 4 | 22 | close_friend / citizen / good_record / poor / man_young | **0.4%** | 0.989 | 100.0% | 0.0% | 4.7% | 2.1% | 0.0% | 92.7% | 0.0% | 0.4% |
| 5 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.4%** | 0.987 | 99.1% | 0.9% | 5.1% | 2.6% | 0.0% | 91.9% | 0.0% | 0.4% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.4%** | 0.983 | 100.0% | 0.0% | 6.0% | 3.4% | 0.0% | 90.2% | 0.0% | 0.4% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | **0.4%** | 0.974 | 100.0% | 0.0% | 5.1% | 4.3% | 0.4% | 89.7% | 0.0% | 0.4% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | **0.4%** | 0.972 | 100.0% | 0.0% | 4.3% | 4.7% | 0.4% | 90.2% | 0.0% | 0.4% |
| 9 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.4%** | 0.970 | 100.0% | 0.0% | 3.0% | 4.3% | 0.9% | 91.5% | 0.0% | 0.4% |
| 10 | 4 | close_friend / mayor / good_record / rich / man_old | **0.4%** | 0.970 | 100.0% | 0.0% | 3.4% | 5.1% | 0.4% | 90.6% | 0.0% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.985 | 99.6% | 0.4% | 3.4% | 2.1% | 0.4% | 94.0% | 0.0% | 0.0% |
| 2 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.985 | 100.0% | 0.0% | 4.7% | 3.0% | 0.0% | 92.3% | 0.0% | 0.0% |
| 3 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.985 | 99.6% | 0.4% | 6.4% | 3.0% | 0.0% | 90.6% | 0.0% | 0.0% |
| 4 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.981 | 100.0% | 0.0% | 5.6% | 3.8% | 0.0% | 90.6% | 0.0% | 0.0% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.981 | 100.0% | 0.0% | 3.4% | 2.1% | 0.9% | 93.6% | 0.0% | 0.0% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.979 | 99.6% | 0.4% | 3.8% | 4.3% | 0.0% | 91.9% | 0.0% | 0.0% |
| 7 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.976 | 99.6% | 0.4% | 4.7% | 3.8% | 0.4% | 91.0% | 0.0% | 0.0% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.976 | 100.0% | 0.0% | 3.0% | 3.8% | 0.4% | 92.7% | 0.0% | 0.0% |
| 9 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.976 | 100.0% | 0.0% | 3.4% | 4.7% | 0.0% | 91.9% | 0.0% | 0.0% |
| 10 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.974 | 100.0% | 0.0% | 3.8% | 4.3% | 0.4% | 91.5% | 0.0% | 0.0% |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.9159** | 0.916 | 25.6% | 74.4% | 20.3% | 14.2% | 1.3% | 64.2% | 0.0% | 0.0% |
| 2 | 56 | stranger / citizen / good_record / poor / man_old | **0.9083** | 0.908 | 26.1% | 73.9% | 10.8% | 12.1% | 3.0% | 72.8% | 0.0% | 1.3% |
| 3 | 24 | close_friend / citizen / good_record / poor / man_old | **0.8925** | 0.893 | 23.1% | 76.9% | 16.4% | 14.2% | 3.4% | 64.2% | 0.0% | 1.7% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **0.8906** | 0.891 | 25.6% | 74.4% | 18.4% | 15.0% | 3.4% | 62.8% | 0.0% | 0.4% |
| 5 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.8889** | 0.889 | 20.1% | 79.9% | 15.0% | 17.9% | 2.1% | 65.0% | 0.0% | 0.0% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | **0.8884** | 0.888 | 18.8% | 81.2% | 18.4% | 15.4% | 3.4% | 62.4% | 0.0% | 0.4% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.8884** | 0.888 | 20.1% | 79.9% | 14.1% | 14.5% | 3.8% | 67.1% | 0.0% | 0.4% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.8884** | 0.888 | 26.5% | 73.5% | 15.0% | 14.5% | 3.8% | 66.2% | 0.0% | 0.4% |
| 9 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.8879** | 0.888 | 26.1% | 73.9% | 15.0% | 17.1% | 2.6% | 64.5% | 0.0% | 0.9% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **0.8841** | 0.884 | 24.4% | 75.6% | 15.9% | 17.2% | 3.0% | 63.9% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.6217** | 0.622 | 26.9% | 73.1% | 4.3% | 5.1% | 33.8% | 54.3% | 0.9% | 1.7% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.6272** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **0.6454** | 0.645 | 30.3% | 69.7% | 2.6% | 6.4% | 29.9% | 56.8% | 1.3% | 3.0% |
| 4 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.6545** | 0.655 | 27.4% | 72.6% | 6.4% | 5.6% | 30.8% | 56.0% | 0.9% | 0.4% |
| 5 | 48 | stranger / mayor / poor_record / poor / man_old | **0.6587** | 0.659 | 26.5% | 73.5% | 5.6% | 4.7% | 31.2% | 56.8% | 0.0% | 1.7% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.6588** | 0.659 | 25.6% | 74.4% | 2.1% | 9.8% | 28.2% | 58.5% | 0.9% | 0.4% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **0.6602** | 0.660 | 25.6% | 74.4% | 5.1% | 6.4% | 29.5% | 56.8% | 0.9% | 1.3% |
| 8 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.6616** | 0.662 | 22.6% | 77.4% | 4.3% | 8.2% | 27.2% | 56.9% | 2.2% | 1.3% |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | **0.6616** | 0.662 | 28.2% | 71.8% | 3.8% | 6.4% | 27.4% | 57.7% | 2.6% | 2.1% |
| 10 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.6810** | 0.681 | 24.8% | 75.2% | 2.6% | 5.1% | 28.6% | 62.4% | 0.4% | 0.9% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | **84.6%** | 0.876 | 15.4% | 84.6% | 15.4% | 20.5% | 2.1% | 61.5% | 0.0% | 0.4% |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | **84.6%** | 0.863 | 15.4% | 84.6% | 14.6% | 20.6% | 3.4% | 61.4% | 0.0% | 0.0% |
| 3 | 7 | close_friend / mayor / good_record / poor / woman_young | **84.6%** | 0.859 | 15.4% | 84.6% | 20.1% | 19.7% | 4.3% | 56.0% | 0.0% | 0.0% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **82.9%** | 0.858 | 17.1% | 82.9% | 12.8% | 23.9% | 2.1% | 60.7% | 0.0% | 0.4% |
| 5 | 55 | stranger / citizen / good_record / poor / woman_young | **82.9%** | 0.855 | 17.1% | 82.9% | 15.0% | 20.5% | 4.3% | 60.3% | 0.0% | 0.0% |
| 6 | 6 | close_friend / mayor / good_record / poor / man_young | **82.1%** | 0.872 | 17.9% | 82.1% | 18.4% | 14.5% | 5.6% | 61.5% | 0.0% | 0.0% |
| 7 | 1 | close_friend / mayor / good_record / rich / woman_old | **81.6%** | 0.857 | 18.4% | 81.6% | 20.1% | 18.4% | 5.1% | 56.4% | 0.0% | 0.0% |
| 8 | 8 | close_friend / mayor / good_record / poor / man_old | **81.2%** | 0.888 | 18.8% | 81.2% | 18.4% | 15.4% | 3.4% | 62.4% | 0.0% | 0.4% |
| 9 | 53 | stranger / citizen / good_record / poor / woman_old | **81.2%** | 0.869 | 18.8% | 81.2% | 13.7% | 18.4% | 3.8% | 63.7% | 0.0% | 0.4% |
| 10 | 5 | close_friend / mayor / good_record / poor / woman_old | **81.2%** | 0.863 | 18.8% | 81.2% | 21.4% | 19.7% | 3.4% | 55.1% | 0.4% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27 | close_friend / citizen / poor_record / rich / woman_young | **67.9%** | 0.790 | 32.1% | 67.9% | 8.5% | 7.7% | 16.7% | 66.2% | 0.4% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **68.4%** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 3 | 57 | stranger / citizen / poor_record / rich / woman_old | **68.8%** | 0.738 | 31.2% | 68.8% | 3.8% | 6.0% | 21.8% | 65.4% | 0.9% | 2.1% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **69.7%** | 0.645 | 30.3% | 69.7% | 2.6% | 6.4% | 29.9% | 56.8% | 1.3% | 3.0% |
| 5 | 60 | stranger / citizen / poor_record / rich / man_old | **70.1%** | 0.763 | 29.9% | 70.1% | 5.6% | 7.7% | 19.2% | 65.0% | 0.0% | 2.6% |
| 6 | 31 | close_friend / citizen / poor_record / poor / woman_young | **70.5%** | 0.748 | 29.5% | 70.5% | 8.5% | 6.4% | 19.2% | 61.1% | 2.1% | 2.6% |
| 7 | 29 | close_friend / citizen / poor_record / poor / woman_old | **71.4%** | 0.741 | 28.6% | 71.4% | 7.7% | 4.3% | 21.8% | 63.7% | 1.7% | 0.9% |
| 8 | 25 | close_friend / citizen / poor_record / rich / woman_old | **71.8%** | 0.806 | 28.2% | 71.8% | 9.4% | 7.3% | 15.4% | 67.5% | 0.4% | 0.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **71.8%** | 0.790 | 28.2% | 71.8% | 8.1% | 3.4% | 18.8% | 68.8% | 0.4% | 0.4% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | **71.8%** | 0.727 | 28.2% | 71.8% | 4.3% | 4.3% | 23.9% | 65.4% | 0.9% | 1.3% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **21.4%** | 0.863 | 18.8% | 81.2% | 21.4% | 19.7% | 3.4% | 55.1% | 0.4% | 0.0% |
| 2 | 3 | close_friend / mayor / good_record / rich / woman_young | **20.3%** | 0.916 | 25.6% | 74.4% | 20.3% | 14.2% | 1.3% | 64.2% | 0.0% | 0.0% |
| 3 | 7 | close_friend / mayor / good_record / poor / woman_young | **20.1%** | 0.859 | 15.4% | 84.6% | 20.1% | 19.7% | 4.3% | 56.0% | 0.0% | 0.0% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | **20.1%** | 0.857 | 18.4% | 81.6% | 20.1% | 18.4% | 5.1% | 56.4% | 0.0% | 0.0% |
| 5 | 38 | stranger / mayor / good_record / poor / man_young | **19.7%** | 0.861 | 19.7% | 80.3% | 19.7% | 21.8% | 3.0% | 55.6% | 0.0% | 0.0% |
| 6 | 20 | close_friend / citizen / good_record / rich / man_old | **18.4%** | 0.891 | 25.6% | 74.4% | 18.4% | 15.0% | 3.4% | 62.8% | 0.0% | 0.4% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **18.4%** | 0.888 | 18.8% | 81.2% | 18.4% | 15.4% | 3.4% | 62.4% | 0.0% | 0.4% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | **18.4%** | 0.872 | 17.9% | 82.1% | 18.4% | 14.5% | 5.6% | 61.5% | 0.0% | 0.0% |
| 9 | 40 | stranger / mayor / good_record / poor / man_old | **17.9%** | 0.865 | 21.8% | 78.2% | 17.9% | 18.4% | 4.3% | 59.4% | 0.0% | 0.0% |
| 10 | 2 | close_friend / mayor / good_record / rich / man_young | **17.5%** | 0.851 | 19.7% | 80.3% | 17.5% | 22.6% | 3.4% | 55.1% | 0.0% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 45 | stranger / mayor / poor_record / poor / woman_old | **2.1%** | 0.659 | 25.6% | 74.4% | 2.1% | 9.8% | 28.2% | 58.5% | 0.9% | 0.4% |
| 2 | 43 | stranger / mayor / poor_record / rich / woman_young | **2.6%** | 0.685 | 26.1% | 73.9% | 2.6% | 3.4% | 28.6% | 63.7% | 0.9% | 0.9% |
| 3 | 41 | stranger / mayor / poor_record / rich / woman_old | **2.6%** | 0.681 | 24.8% | 75.2% | 2.6% | 5.1% | 28.6% | 62.4% | 0.4% | 0.9% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **2.6%** | 0.645 | 30.3% | 69.7% | 2.6% | 6.4% | 29.9% | 56.8% | 1.3% | 3.0% |
| 5 | 57 | stranger / citizen / poor_record / rich / woman_old | **3.8%** | 0.738 | 31.2% | 68.8% | 3.8% | 6.0% | 21.8% | 65.4% | 0.9% | 2.1% |
| 6 | 62 | stranger / citizen / poor_record / poor / man_young | **3.8%** | 0.662 | 28.2% | 71.8% | 3.8% | 6.4% | 27.4% | 57.7% | 2.6% | 2.1% |
| 7 | 59 | stranger / citizen / poor_record / rich / woman_young | **4.3%** | 0.727 | 28.2% | 71.8% | 4.3% | 4.3% | 23.9% | 65.4% | 0.9% | 1.3% |
| 8 | 61 | stranger / citizen / poor_record / poor / woman_old | **4.3%** | 0.622 | 26.9% | 73.1% | 4.3% | 5.1% | 33.8% | 54.3% | 0.9% | 1.7% |
| 9 | 63 | stranger / citizen / poor_record / poor / woman_young | **4.3%** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 10 | 11 | close_friend / mayor / poor_record / rich / woman_young | **4.3%** | 0.662 | 22.6% | 77.4% | 4.3% | 8.2% | 27.2% | 56.9% | 2.2% | 1.3% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | close_friend / mayor / good_record / rich / man_old | **25.2%** | 0.838 | 19.2% | 80.8% | 15.0% | 25.2% | 3.4% | 55.6% | 0.0% | 0.9% |
| 2 | 34 | stranger / mayor / good_record / rich / man_young | **23.9%** | 0.858 | 17.1% | 82.9% | 12.8% | 23.9% | 2.1% | 60.7% | 0.0% | 0.4% |
| 3 | 36 | stranger / mayor / good_record / rich / man_old | **22.6%** | 0.861 | 20.1% | 79.9% | 16.7% | 22.6% | 2.6% | 58.1% | 0.0% | 0.0% |
| 4 | 2 | close_friend / mayor / good_record / rich / man_young | **22.6%** | 0.851 | 19.7% | 80.3% | 17.5% | 22.6% | 3.4% | 55.1% | 0.0% | 1.3% |
| 5 | 39 | stranger / mayor / good_record / poor / woman_young | **22.2%** | 0.833 | 19.2% | 80.8% | 12.4% | 22.2% | 5.6% | 59.8% | 0.0% | 0.0% |
| 6 | 38 | stranger / mayor / good_record / poor / man_young | **21.8%** | 0.861 | 19.7% | 80.3% | 19.7% | 21.8% | 3.0% | 55.6% | 0.0% | 0.0% |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | **20.9%** | 0.834 | 22.6% | 77.4% | 11.5% | 20.9% | 6.0% | 60.7% | 0.0% | 0.9% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **20.6%** | 0.863 | 15.4% | 84.6% | 14.6% | 20.6% | 3.4% | 61.4% | 0.0% | 0.0% |
| 9 | 35 | stranger / mayor / good_record / rich / woman_young | **20.5%** | 0.876 | 15.4% | 84.6% | 15.4% | 20.5% | 2.1% | 61.5% | 0.0% | 0.4% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | **20.5%** | 0.855 | 17.1% | 82.9% | 15.0% | 20.5% | 4.3% | 60.3% | 0.0% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **3.4%** | 0.790 | 28.2% | 71.8% | 8.1% | 3.4% | 18.8% | 68.8% | 0.4% | 0.4% |
| 2 | 44 | stranger / mayor / poor_record / rich / man_old | **3.4%** | 0.704 | 27.8% | 72.2% | 6.8% | 3.4% | 26.5% | 61.5% | 1.3% | 0.4% |
| 3 | 43 | stranger / mayor / poor_record / rich / woman_young | **3.4%** | 0.685 | 26.1% | 73.9% | 2.6% | 3.4% | 28.6% | 63.7% | 0.9% | 0.9% |
| 4 | 32 | close_friend / citizen / poor_record / poor / man_old | **3.4%** | 0.772 | 25.2% | 74.8% | 9.9% | 3.4% | 20.6% | 65.2% | 0.4% | 0.4% |
| 5 | 14 | close_friend / mayor / poor_record / poor / man_young | **3.8%** | 0.763 | 23.5% | 76.5% | 6.0% | 3.8% | 20.5% | 67.1% | 0.9% | 1.7% |
| 6 | 63 | stranger / citizen / poor_record / poor / woman_young | **3.9%** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 7 | 9 | close_friend / mayor / poor_record / rich / woman_old | **4.3%** | 0.782 | 27.4% | 72.6% | 9.8% | 4.3% | 18.4% | 66.2% | 1.3% | 0.0% |
| 8 | 29 | close_friend / citizen / poor_record / poor / woman_old | **4.3%** | 0.741 | 28.6% | 71.4% | 7.7% | 4.3% | 21.8% | 63.7% | 1.7% | 0.9% |
| 9 | 59 | stranger / citizen / poor_record / rich / woman_young | **4.3%** | 0.727 | 28.2% | 71.8% | 4.3% | 4.3% | 23.9% | 65.4% | 0.9% | 1.3% |
| 10 | 30 | close_friend / citizen / poor_record / poor / man_young | **4.7%** | 0.830 | 27.4% | 72.6% | 9.0% | 4.7% | 14.5% | 70.9% | 0.0% | 0.9% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **33.9%** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **33.8%** | 0.622 | 26.9% | 73.1% | 4.3% | 5.1% | 33.8% | 54.3% | 0.9% | 1.7% |
| 3 | 48 | stranger / mayor / poor_record / poor / man_old | **31.2%** | 0.659 | 26.5% | 73.5% | 5.6% | 4.7% | 31.2% | 56.8% | 0.0% | 1.7% |
| 4 | 47 | stranger / mayor / poor_record / poor / woman_young | **30.8%** | 0.655 | 27.4% | 72.6% | 6.4% | 5.6% | 30.8% | 56.0% | 0.9% | 0.4% |
| 5 | 64 | stranger / citizen / poor_record / poor / man_old | **29.9%** | 0.645 | 30.3% | 69.7% | 2.6% | 6.4% | 29.9% | 56.8% | 1.3% | 3.0% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | **29.5%** | 0.660 | 25.6% | 74.4% | 5.1% | 6.4% | 29.5% | 56.8% | 0.9% | 1.3% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | **28.6%** | 0.685 | 26.1% | 73.9% | 2.6% | 3.4% | 28.6% | 63.7% | 0.9% | 0.9% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | **28.6%** | 0.681 | 24.8% | 75.2% | 2.6% | 5.1% | 28.6% | 62.4% | 0.4% | 0.9% |
| 9 | 45 | stranger / mayor / poor_record / poor / woman_old | **28.2%** | 0.659 | 25.6% | 74.4% | 2.1% | 9.8% | 28.2% | 58.5% | 0.9% | 0.4% |
| 10 | 62 | stranger / citizen / poor_record / poor / man_young | **27.4%** | 0.662 | 28.2% | 71.8% | 3.8% | 6.4% | 27.4% | 57.7% | 2.6% | 2.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **1.3%** | 0.916 | 25.6% | 74.4% | 20.3% | 14.2% | 1.3% | 64.2% | 0.0% | 0.0% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | **2.1%** | 0.889 | 20.1% | 79.9% | 15.0% | 17.9% | 2.1% | 65.0% | 0.0% | 0.0% |
| 3 | 35 | stranger / mayor / good_record / rich / woman_young | **2.1%** | 0.876 | 15.4% | 84.6% | 15.4% | 20.5% | 2.1% | 61.5% | 0.0% | 0.4% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **2.1%** | 0.858 | 17.1% | 82.9% | 12.8% | 23.9% | 2.1% | 60.7% | 0.0% | 0.4% |
| 5 | 17 | close_friend / citizen / good_record / rich / woman_old | **2.6%** | 0.888 | 26.1% | 73.9% | 15.0% | 17.1% | 2.6% | 64.5% | 0.0% | 0.9% |
| 6 | 36 | stranger / mayor / good_record / rich / man_old | **2.6%** | 0.861 | 20.1% | 79.9% | 16.7% | 22.6% | 2.6% | 58.1% | 0.0% | 0.0% |
| 7 | 37 | stranger / mayor / good_record / poor / woman_old | **3.0%** | 0.874 | 24.4% | 75.6% | 14.5% | 19.2% | 3.0% | 63.2% | 0.0% | 0.0% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | **3.0%** | 0.861 | 19.7% | 80.3% | 19.7% | 21.8% | 3.0% | 55.6% | 0.0% | 0.0% |
| 9 | 18 | close_friend / citizen / good_record / rich / man_young | **3.0%** | 0.884 | 24.4% | 75.6% | 15.9% | 17.2% | 3.0% | 63.9% | 0.0% | 0.0% |
| 10 | 56 | stranger / citizen / good_record / poor / man_old | **3.0%** | 0.908 | 26.1% | 73.9% | 10.8% | 12.1% | 3.0% | 72.8% | 0.0% | 1.3% |


**CHECKED_TRUE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 56 | stranger / citizen / good_record / poor / man_old | **72.8%** | 0.908 | 26.1% | 73.9% | 10.8% | 12.1% | 3.0% | 72.8% | 0.0% | 1.3% |
| 2 | 30 | close_friend / citizen / poor_record / poor / man_young | **70.9%** | 0.830 | 27.4% | 72.6% | 9.0% | 4.7% | 14.5% | 70.9% | 0.0% | 0.9% |
| 3 | 54 | stranger / citizen / good_record / poor / man_young | **69.2%** | 0.871 | 26.9% | 73.1% | 9.4% | 15.4% | 5.1% | 69.2% | 0.0% | 0.9% |
| 4 | 58 | stranger / citizen / poor_record / rich / man_young | **68.8%** | 0.790 | 28.2% | 71.8% | 8.1% | 3.4% | 18.8% | 68.8% | 0.4% | 0.4% |
| 5 | 25 | close_friend / citizen / poor_record / rich / woman_old | **67.5%** | 0.806 | 28.2% | 71.8% | 9.4% | 7.3% | 15.4% | 67.5% | 0.4% | 0.0% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **67.1%** | 0.888 | 20.1% | 79.9% | 14.1% | 14.5% | 3.8% | 67.1% | 0.0% | 0.4% |
| 7 | 14 | close_friend / mayor / poor_record / poor / man_young | **67.1%** | 0.763 | 23.5% | 76.5% | 6.0% | 3.8% | 20.5% | 67.1% | 0.9% | 1.7% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | **67.0%** | 0.884 | 25.6% | 74.4% | 12.9% | 16.3% | 3.4% | 67.0% | 0.0% | 0.4% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | **66.2%** | 0.888 | 26.5% | 73.5% | 15.0% | 14.5% | 3.8% | 66.2% | 0.0% | 0.4% |
| 10 | 27 | close_friend / citizen / poor_record / rich / woman_young | **66.2%** | 0.790 | 32.1% | 67.9% | 8.5% | 7.7% | 16.7% | 66.2% | 0.4% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **54.3%** | 0.622 | 26.9% | 73.1% | 4.3% | 5.1% | 33.8% | 54.3% | 0.9% | 1.7% |
| 2 | 5 | close_friend / mayor / good_record / poor / woman_old | **55.1%** | 0.863 | 18.8% | 81.2% | 21.4% | 19.7% | 3.4% | 55.1% | 0.4% | 0.0% |
| 3 | 2 | close_friend / mayor / good_record / rich / man_young | **55.1%** | 0.851 | 19.7% | 80.3% | 17.5% | 22.6% | 3.4% | 55.1% | 0.0% | 1.3% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **55.6%** | 0.861 | 19.7% | 80.3% | 19.7% | 21.8% | 3.0% | 55.6% | 0.0% | 0.0% |
| 5 | 4 | close_friend / mayor / good_record / rich / man_old | **55.6%** | 0.838 | 19.2% | 80.8% | 15.0% | 25.2% | 3.4% | 55.6% | 0.0% | 0.9% |
| 6 | 7 | close_friend / mayor / good_record / poor / woman_young | **56.0%** | 0.859 | 15.4% | 84.6% | 20.1% | 19.7% | 4.3% | 56.0% | 0.0% | 0.0% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | **56.0%** | 0.655 | 27.4% | 72.6% | 6.4% | 5.6% | 30.8% | 56.0% | 0.9% | 0.4% |
| 8 | 63 | stranger / citizen / poor_record / poor / woman_young | **56.2%** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | **56.4%** | 0.857 | 18.4% | 81.6% | 20.1% | 18.4% | 5.1% | 56.4% | 0.0% | 0.0% |
| 10 | 46 | stranger / mayor / poor_record / poor / man_young | **56.8%** | 0.660 | 25.6% | 74.4% | 5.1% | 6.4% | 29.5% | 56.8% | 0.9% | 1.3% |


**CHECKED_FALSE (%)** *(Note: 34 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **2.6%** | 0.662 | 28.2% | 71.8% | 3.8% | 6.4% | 27.4% | 57.7% | 2.6% | 2.1% |
| 2 | 11 | close_friend / mayor / poor_record / rich / woman_young | **2.2%** | 0.662 | 22.6% | 77.4% | 4.3% | 8.2% | 27.2% | 56.9% | 2.2% | 1.3% |
| 3 | 31 | close_friend / citizen / poor_record / poor / woman_young | **2.1%** | 0.748 | 29.5% | 70.5% | 8.5% | 6.4% | 19.2% | 61.1% | 2.1% | 2.6% |
| 4 | 29 | close_friend / citizen / poor_record / poor / woman_old | **1.7%** | 0.741 | 28.6% | 71.4% | 7.7% | 4.3% | 21.8% | 63.7% | 1.7% | 0.9% |
| 5 | 28 | close_friend / citizen / poor_record / rich / man_old | **1.3%** | 0.790 | 26.1% | 73.9% | 11.2% | 6.0% | 16.3% | 63.5% | 1.3% | 1.7% |
| 6 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.3%** | 0.627 | 31.6% | 68.4% | 4.3% | 3.9% | 33.9% | 56.2% | 1.3% | 0.4% |
| 7 | 9 | close_friend / mayor / poor_record / rich / woman_old | **1.3%** | 0.782 | 27.4% | 72.6% | 9.8% | 4.3% | 18.4% | 66.2% | 1.3% | 0.0% |
| 8 | 12 | close_friend / mayor / poor_record / rich / man_old | **1.3%** | 0.748 | 20.5% | 79.5% | 10.7% | 9.0% | 19.2% | 59.0% | 1.3% | 0.9% |
| 9 | 10 | close_friend / mayor / poor_record / rich / man_young | **1.3%** | 0.747 | 24.4% | 75.6% | 8.1% | 6.8% | 20.5% | 62.8% | 1.3% | 0.4% |
| 10 | 15 | close_friend / mayor / poor_record / poor / woman_young | **1.3%** | 0.742 | 25.2% | 74.8% | 6.0% | 6.8% | 20.9% | 64.5% | 1.3% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0%** | 0.916 | 25.6% | 74.4% | 20.3% | 14.2% | 1.3% | 64.2% | 0.0% | 0.0% |
| 2 | 56 | stranger / citizen / good_record / poor / man_old | **0.0%** | 0.908 | 26.1% | 73.9% | 10.8% | 12.1% | 3.0% | 72.8% | 0.0% | 1.3% |
| 3 | 24 | close_friend / citizen / good_record / poor / man_old | **0.0%** | 0.893 | 23.1% | 76.9% | 16.4% | 14.2% | 3.4% | 64.2% | 0.0% | 1.7% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.891 | 25.6% | 74.4% | 18.4% | 15.0% | 3.4% | 62.8% | 0.0% | 0.4% |
| 5 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0%** | 0.889 | 20.1% | 79.9% | 15.0% | 17.9% | 2.1% | 65.0% | 0.0% | 0.0% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.888 | 18.8% | 81.2% | 18.4% | 15.4% | 3.4% | 62.4% | 0.0% | 0.4% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.888 | 20.1% | 79.9% | 14.1% | 14.5% | 3.8% | 67.1% | 0.0% | 0.4% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.888 | 26.5% | 73.5% | 15.0% | 14.5% | 3.8% | 66.2% | 0.0% | 0.4% |
| 9 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.888 | 26.1% | 73.9% | 15.0% | 17.1% | 2.6% | 64.5% | 0.0% | 0.9% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.884 | 24.4% | 75.6% | 15.9% | 17.2% | 3.0% | 63.9% | 0.0% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 18 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **3.0%** | 0.645 | 30.3% | 69.7% | 2.6% | 6.4% | 29.9% | 56.8% | 1.3% | 3.0% |
| 2 | 60 | stranger / citizen / poor_record / rich / man_old | **2.6%** | 0.763 | 29.9% | 70.1% | 5.6% | 7.7% | 19.2% | 65.0% | 0.0% | 2.6% |
| 3 | 31 | close_friend / citizen / poor_record / poor / woman_young | **2.6%** | 0.748 | 29.5% | 70.5% | 8.5% | 6.4% | 19.2% | 61.1% | 2.1% | 2.6% |
| 4 | 22 | close_friend / citizen / good_record / poor / man_young | **2.1%** | 0.862 | 21.8% | 78.2% | 15.8% | 16.7% | 5.1% | 60.3% | 0.0% | 2.1% |
| 5 | 57 | stranger / citizen / poor_record / rich / woman_old | **2.1%** | 0.738 | 31.2% | 68.8% | 3.8% | 6.0% | 21.8% | 65.4% | 0.9% | 2.1% |
| 6 | 62 | stranger / citizen / poor_record / poor / man_young | **2.1%** | 0.662 | 28.2% | 71.8% | 3.8% | 6.4% | 27.4% | 57.7% | 2.6% | 2.1% |
| 7 | 24 | close_friend / citizen / good_record / poor / man_old | **1.7%** | 0.893 | 23.1% | 76.9% | 16.4% | 14.2% | 3.4% | 64.2% | 0.0% | 1.7% |
| 8 | 28 | close_friend / citizen / poor_record / rich / man_old | **1.7%** | 0.790 | 26.1% | 73.9% | 11.2% | 6.0% | 16.3% | 63.5% | 1.3% | 1.7% |
| 9 | 14 | close_friend / mayor / poor_record / poor / man_young | **1.7%** | 0.763 | 23.5% | 76.5% | 6.0% | 3.8% | 20.5% | 67.1% | 0.9% | 1.7% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **1.7%** | 0.659 | 26.5% | 73.5% | 5.6% | 4.7% | 31.2% | 56.8% | 0.0% | 1.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0%** | 0.916 | 25.6% | 74.4% | 20.3% | 14.2% | 1.3% | 64.2% | 0.0% | 0.0% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0%** | 0.889 | 20.1% | 79.9% | 15.0% | 17.9% | 2.1% | 65.0% | 0.0% | 0.0% |
| 3 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.884 | 24.4% | 75.6% | 15.9% | 17.2% | 3.0% | 63.9% | 0.0% | 0.0% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0%** | 0.874 | 24.4% | 75.6% | 14.5% | 19.2% | 3.0% | 63.2% | 0.0% | 0.0% |
| 5 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.872 | 17.9% | 82.1% | 18.4% | 14.5% | 5.6% | 61.5% | 0.0% | 0.0% |
| 6 | 40 | stranger / mayor / good_record / poor / man_old | **0.0%** | 0.865 | 21.8% | 78.2% | 17.9% | 18.4% | 4.3% | 59.4% | 0.0% | 0.0% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0%** | 0.863 | 18.8% | 81.2% | 21.4% | 19.7% | 3.4% | 55.1% | 0.4% | 0.0% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.863 | 15.4% | 84.6% | 14.6% | 20.6% | 3.4% | 61.4% | 0.0% | 0.0% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | **0.0%** | 0.861 | 19.7% | 80.3% | 19.7% | 21.8% | 3.0% | 55.6% | 0.0% | 0.0% |
| 10 | 36 | stranger / mayor / good_record / rich / man_old | **0.0%** | 0.861 | 20.1% | 79.9% | 16.7% | 22.6% | 2.6% | 58.1% | 0.0% | 0.0% |
