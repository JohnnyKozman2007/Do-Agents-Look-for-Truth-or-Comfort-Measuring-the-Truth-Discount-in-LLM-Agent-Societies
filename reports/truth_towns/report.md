# Truth Towns Report (True Claims)

**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Condition:** `truth_twin` | **Towns:** 4,992 (2,496 per model) | **Expected Listeners:** 59,904

### Methodological & Missingness Disclosure
- **Excluded Invalid Judgments:** 213 / 59,904 (0.36%) had `judgment_status = invalid`. They are **completely excluded** (`NaN`), never turned into zeros.
- **Label % Denominator:** Valid judgments (`FACT + UNCERTAIN + SKEPTICAL + CHECKED_TRUE + CHECKED_FALSE + NOT_MENTIONED = 100%`).
- **Primary Belief Denominator:** Valid mentioning listeners (excluding `NOT_MENTIONED` and `INVALID`). Sensitivity checks (`Silence=0.0`, `Silence=0.5`) impute *only* valid `NOT_MENTIONED` rows.
- **Verification (`GO`/`SKIP`):** 0 missing or invalid decisions. 48 simulation decisions (21 first-hand, 27 second-hand; 0.08%) were `malformed_fallback_skip` in the simulation runner and appear as `SKIP`.
- **Statistical Model:** Controlled main effects of all 6 knobs simultaneously (`closeness`, `authority`, `reliability`, `wealth`, `gender`, `age` + `real_artist`), with standard errors clustered by town (`run_id`) and Holm adjustment across the 6 knobs per outcome. `Belief` also reports the spec's town-random-intercept LMM (`mixedlm`) check.

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

## 3. Controlled Main Effects of the 6 Knobs (Town-Clustered)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=29,750, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.7252 | 0.6352 | +0.0900*** | [+0.0808, +0.0993] | <0.0001 | <0.0001 | +0.0901 (p=<0.0001) |
| authority | `mayor - citizen` | 0.6852 | 0.6751 | +0.0101 | [+0.0009, +0.0193] | 0.0321 | 0.0642 | +0.0101 (p=0.0324) |
| reliability | `good_record - poor_record` | 0.9018 | 0.4586 | +0.4432*** | [+0.4339, +0.4524] | <0.0001 | <0.0001 | +0.4432 (p=<0.0001) |
| wealth | `rich - poor` | 0.6985 | 0.6618 | +0.0367*** | [+0.0274, +0.0459] | <0.0001 | <0.0001 | +0.0367 (p=<0.0001) |
| gender | `woman - man` | 0.6818 | 0.6786 | +0.0032 | [-0.0061, +0.0124] | 0.4983 | 0.4983 | +0.0032 (p=0.5001) |
| age | `old - young` | 0.6699 | 0.6905 | -0.0206*** | [-0.0298, -0.0113] | <0.0001 | <0.0001 | -0.0206 (p=<0.0001) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.7250 | 0.6349 | +0.0901*** | [+0.0809, +0.0993] | <0.0001 | <0.0001 | +0.0901 (p=<0.0001) |
| authority | `mayor - citizen` | 0.6850 | 0.6749 | +0.0101 | [+0.0008, +0.0193] | 0.0327 | 0.0654 | +0.0101 (p=0.0330) |
| reliability | `good_record - poor_record` | 0.9015 | 0.4583 | +0.4432*** | [+0.4340, +0.4525] | <0.0001 | <0.0001 | +0.4432 (p=<0.0001) |
| wealth | `rich - poor` | 0.6981 | 0.6617 | +0.0364*** | [+0.0271, +0.0456] | <0.0001 | <0.0001 | +0.0364 (p=<0.0001) |
| gender | `woman - man` | 0.6815 | 0.6783 | +0.0032 | [-0.0061, +0.0124] | 0.5022 | 0.5022 | +0.0031 (p=0.5049) |
| age | `old - young` | 0.6698 | 0.6901 | -0.0203*** | [-0.0296, -0.0111] | <0.0001 | <0.0001 | -0.0203 (p=<0.0001) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.7251 | 0.6351 | +0.0900*** | [+0.0808, +0.0992] | <0.0001 | <0.0001 | +0.0900 (p=<0.0001) |
| authority | `mayor - citizen` | 0.6852 | 0.6751 | +0.0100 | [+0.0008, +0.0193] | 0.0333 | 0.0666 | +0.0100 (p=0.0336) |
| reliability | `good_record - poor_record` | 0.9017 | 0.4586 | +0.4431*** | [+0.4338, +0.4523] | <0.0001 | <0.0001 | +0.4430 (p=<0.0001) |
| wealth | `rich - poor` | 0.6985 | 0.6618 | +0.0367*** | [+0.0274, +0.0459] | <0.0001 | <0.0001 | +0.0367 (p=<0.0001) |
| gender | `woman - man` | 0.6817 | 0.6785 | +0.0032 | [-0.0060, +0.0124] | 0.4970 | 0.4970 | +0.0032 (p=0.4997) |
| age | `old - young` | 0.6699 | 0.6904 | -0.0205*** | [-0.0297, -0.0113] | <0.0001 | <0.0001 | -0.0205 (p=<0.0001) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 62.51% | 53.81% | +8.70 pp*** | [+7.77, +9.63 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 58.57% | 57.76% | +0.81 pp | [-0.12, +1.74 pp] | 0.0892 | 0.0892 |
| reliability | `good_record - poor_record` | 76.66% | 39.66% | +37.00 pp*** | [+36.07, +37.93 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 59.40% | 56.93% | +2.46 pp*** | [+1.53, +3.40 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 58.64% | 57.68% | +0.96 pp | [+0.02, +1.89 pp] | 0.0444 | 0.0888 |
| age | `old - young` | 57.16% | 59.17% | -2.01 pp*** | [-2.94, -1.08 pp] | <0.0001 | <0.0001 |

**Outcome: NOT_MENTIONED (%)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.03% | 0.05% | -0.02 pp | [-0.07, +0.03 pp] | 0.4054 | 1.0000 |
| authority | `mayor - citizen` | 0.04% | 0.05% | -0.01 pp | [-0.05, +0.04 pp] | 0.7796 | 1.0000 |
| reliability | `good_record - poor_record` | 0.03% | 0.06% | -0.03 pp | [-0.08, +0.01 pp] | 0.1635 | 0.8167 |
| wealth | `rich - poor` | 0.07% | 0.01% | +0.06 pp | [+0.01, +0.11 pp] | 0.0121 | 0.0728 |
| gender | `woman - man` | 0.05% | 0.04% | +0.01 pp | [-0.04, +0.06 pp] | 0.7552 | 1.0000 |
| age | `old - young` | 0.03% | 0.06% | -0.03 pp | [-0.08, +0.01 pp] | 0.1633 | 0.8167 |

**Outcome: FACT (%)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 5.89% | 3.95% | +1.95 pp*** | [+1.44, +2.45 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 5.33% | 4.52% | +0.81 pp** | [+0.31, +1.31 pp] | 0.0015 | 0.0059 |
| reliability | `good_record - poor_record` | 7.36% | 2.48% | +4.88 pp*** | [+4.38, +5.38 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 5.01% | 4.84% | +0.17 pp | [-0.33, +0.67 pp] | 0.5037 | 1.0000 |
| gender | `woman - man` | 4.99% | 4.85% | +0.14 pp | [-0.36, +0.64 pp] | 0.5903 | 1.0000 |
| age | `old - young` | 4.94% | 4.91% | +0.03 pp | [-0.47, +0.53 pp] | 0.9016 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 11.97% | 11.19% | +0.78 pp | [+0.08, +1.48 pp] | 0.0290 | 0.0869 |
| authority | `mayor - citizen` | 12.63% | 10.53% | +2.10 pp*** | [+1.40, +2.80 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 14.24% | 8.93% | +5.31 pp*** | [+4.61, +6.01 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 10.96% | 12.21% | -1.25 pp** | [-1.95, -0.54 pp] | 0.0005 | 0.0020 |
| gender | `woman - man` | 11.60% | 11.57% | +0.03 pp | [-0.68, +0.73 pp] | 0.9442 | 1.0000 |
| age | `old - young` | 11.70% | 11.46% | +0.24 pp | [-0.46, +0.94 pp] | 0.5029 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 21.29% | 30.60% | -9.31 pp*** | [-10.26, -8.37 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 24.97% | 26.92% | -1.96 pp*** | [-2.90, -1.01 pp] | <0.0001 | 0.0001 |
| reliability | `good_record - poor_record` | 2.63% | 49.26% | -46.63 pp*** | [-47.58, -45.69 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 24.38% | 27.51% | -3.13 pp*** | [-4.08, -2.19 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 25.79% | 26.10% | -0.31 pp | [-1.26, +0.63 pp] | 0.5176 | 0.5176 |
| age | `old - young` | 26.93% | 24.96% | +1.97 pp*** | [+1.03, +2.92 pp] | <0.0001 | 0.0001 |

**Outcome: CHECKED_TRUE (%)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 60.61% | 53.94% | +6.67 pp*** | [+5.61, +7.74 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 56.85% | 57.71% | -0.86 pp | [-1.92, +0.21 pp] | 0.1141 | 0.2282 |
| reliability | `good_record - poor_record` | 75.67% | 38.88% | +36.79 pp*** | [+35.73, +37.85 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 59.32% | 55.23% | +4.09 pp*** | [+3.03, +5.15 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 57.36% | 57.19% | +0.17 pp | [-0.90, +1.23 pp] | 0.7586 | 0.7586 |
| age | `old - young` | 56.19% | 58.37% | -2.18 pp*** | [-3.25, -1.12 pp] | <0.0001 | 0.0002 |

**Outcome: CHECKED_FALSE (%)** (n=29,763, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.20% | 0.26% | -0.07 pp | [-0.19, +0.05 pp] | 0.2829 | 1.0000 |
| authority | `mayor - citizen` | 0.18% | 0.28% | -0.09 pp | [-0.22, +0.03 pp] | 0.1303 | 0.6514 |
| reliability | `good_record - poor_record` | 0.07% | 0.38% | -0.31 pp*** | [-0.43, -0.19 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.26% | 0.20% | +0.05 pp | [-0.07, +0.18 pp] | 0.3848 | 1.0000 |
| gender | `woman - man` | 0.22% | 0.24% | -0.02 pp | [-0.15, +0.10 pp] | 0.6897 | 1.0000 |
| age | `old - young` | 0.22% | 0.24% | -0.03 pp | [-0.15, +0.09 pp] | 0.6649 | 1.0000 |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,922, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.6303 | 0.5158 | +0.1145*** | [+0.1031, +0.1260] | <0.0001 | <0.0001 | +0.1146 (p=<0.0001) |
| authority | `mayor - citizen` | 0.5706 | 0.5755 | -0.0049 | [-0.0163, +0.0065] | 0.4037 | 0.8074 | -0.0049 (p=0.4029) |
| reliability | `good_record - poor_record` | 0.8732 | 0.2729 | +0.6003*** | [+0.5889, +0.6117] | <0.0001 | <0.0001 | +0.6003 (p=<0.0001) |
| wealth | `rich - poor` | 0.5933 | 0.5528 | +0.0405*** | [+0.0291, +0.0520] | <0.0001 | <0.0001 | +0.0405 (p=<0.0001) |
| gender | `woman - man` | 0.5751 | 0.5710 | +0.0041 | [-0.0073, +0.0155] | 0.4794 | 0.8074 | +0.0041 (p=0.4799) |
| age | `old - young` | 0.5628 | 0.5833 | -0.0205** | [-0.0319, -0.0091] | 0.0004 | 0.0013 | -0.0205 (p=0.0004) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.6300 | 0.5156 | +0.1144*** | [+0.1029, +0.1258] | <0.0001 | <0.0001 | +0.1144 (p=<0.0001) |
| authority | `mayor - citizen` | 0.5702 | 0.5754 | -0.0052 | [-0.0166, +0.0062] | 0.3719 | 0.7439 | -0.0052 (p=0.3728) |
| reliability | `good_record - poor_record` | 0.8728 | 0.2728 | +0.6000*** | [+0.5886, +0.6114] | <0.0001 | <0.0001 | +0.6000 (p=<0.0001) |
| wealth | `rich - poor` | 0.5930 | 0.5526 | +0.0403*** | [+0.0289, +0.0517] | <0.0001 | <0.0001 | +0.0403 (p=<0.0001) |
| gender | `woman - man` | 0.5749 | 0.5707 | +0.0042 | [-0.0072, +0.0156] | 0.4733 | 0.7439 | +0.0042 (p=0.4747) |
| age | `old - young` | 0.5627 | 0.5829 | -0.0203** | [-0.0317, -0.0089] | 0.0005 | 0.0015 | -0.0203 (p=0.0005) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.6302 | 0.5157 | +0.1144*** | [+0.1030, +0.1259] | <0.0001 | <0.0001 | +0.1145 (p=<0.0001) |
| authority | `mayor - citizen` | 0.5705 | 0.5755 | -0.0050 | [-0.0164, +0.0064] | 0.3901 | 0.7801 | -0.0050 (p=0.3907) |
| reliability | `good_record - poor_record` | 0.8730 | 0.2729 | +0.6001*** | [+0.5887, +0.6115] | <0.0001 | <0.0001 | +0.6001 (p=<0.0001) |
| wealth | `rich - poor` | 0.5932 | 0.5527 | +0.0405*** | [+0.0291, +0.0519] | <0.0001 | <0.0001 | +0.0405 (p=<0.0001) |
| gender | `woman - man` | 0.5751 | 0.5708 | +0.0042 | [-0.0072, +0.0156] | 0.4654 | 0.7801 | +0.0042 (p=0.4666) |
| age | `old - young` | 0.5627 | 0.5832 | -0.0205** | [-0.0319, -0.0091] | 0.0004 | 0.0013 | -0.0205 (p=0.0004) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 54.18% | 42.76% | +11.42 pp*** | [+10.05, +12.79 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 47.18% | 49.76% | -2.58 pp*** | [-3.95, -1.21 pp] | 0.0002 | 0.0007 |
| reliability | `good_record - poor_record` | 76.35% | 20.59% | +55.76 pp*** | [+54.38, +57.13 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 51.16% | 45.78% | +5.38 pp*** | [+4.01, +6.75 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 48.77% | 48.17% | +0.60 pp | [-0.77, +1.97 pp] | 0.3907 | 0.3907 |
| age | `old - young` | 47.57% | 49.37% | -1.80 pp* | [-3.17, -0.43 pp] | 0.0100 | 0.0200 |

**Outcome: NOT_MENTIONED (%)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.04% | 0.03% | +0.01 pp | [-0.05, +0.07 pp] | 0.6529 | 1.0000 |
| authority | `mayor - citizen` | 0.05% | 0.01% | +0.04 pp | [-0.02, +0.10 pp] | 0.1784 | 1.0000 |
| reliability | `good_record - poor_record` | 0.04% | 0.03% | +0.01 pp | [-0.05, +0.07 pp] | 0.6522 | 1.0000 |
| wealth | `rich - poor` | 0.05% | 0.01% | +0.04 pp | [-0.02, +0.10 pp] | 0.1794 | 1.0000 |
| gender | `woman - man` | 0.04% | 0.03% | +0.01 pp | [-0.05, +0.07 pp] | 0.6455 | 1.0000 |
| age | `old - young` | 0.01% | 0.05% | -0.04 pp | [-0.10, +0.02 pp] | 0.1785 | 1.0000 |

**Outcome: FACT (%)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 2.59% | 1.42% | +1.17 pp*** | [+0.71, +1.62 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 1.99% | 2.02% | -0.04 pp | [-0.49, +0.42 pp] | 0.8726 | 1.0000 |
| reliability | `good_record - poor_record` | 3.33% | 0.68% | +2.64 pp*** | [+2.19, +3.10 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 1.84% | 2.17% | -0.33 pp | [-0.79, +0.12 pp] | 0.1520 | 0.6082 |
| gender | `woman - man` | 1.99% | 2.02% | -0.03 pp | [-0.49, +0.42 pp] | 0.8848 | 1.0000 |
| age | `old - young` | 2.14% | 1.86% | +0.28 pp | [-0.18, +0.74 pp] | 0.2286 | 0.6857 |

**Outcome: UNCERTAIN (%)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 16.29% | 16.28% | +0.01 pp | [-1.19, +1.22 pp] | 0.9851 | 1.0000 |
| authority | `mayor - citizen` | 17.76% | 14.80% | +2.96 pp*** | [+1.76, +4.17 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 18.76% | 13.80% | +4.96 pp*** | [+3.75, +6.16 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 15.08% | 17.49% | -2.41 pp*** | [-3.62, -1.21 pp] | <0.0001 | 0.0004 |
| gender | `woman - man` | 16.20% | 16.37% | -0.17 pp | [-1.37, +1.04 pp] | 0.7864 | 1.0000 |
| age | `old - young` | 16.40% | 16.17% | +0.23 pp | [-0.97, +1.44 pp] | 0.7037 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 28.59% | 39.97% | -11.38 pp*** | [-12.60, -10.15 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 33.83% | 34.72% | -0.89 pp | [-2.12, +0.33 pp] | 0.1527 | 0.3053 |
| reliability | `good_record - poor_record` | 3.22% | 65.34% | -62.12 pp*** | [-63.34, -60.89 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 32.82% | 35.74% | -2.92 pp*** | [-4.15, -1.69 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 34.12% | 34.44% | -0.32 pp | [-1.55, +0.90 pp] | 0.6042 | 0.6042 |
| age | `old - young` | 35.25% | 33.30% | +1.95 pp** | [+0.73, +3.18 pp] | 0.0018 | 0.0055 |

**Outcome: CHECKED_TRUE (%)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 52.27% | 42.00% | +10.27 pp*** | [+8.89, +11.64 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 46.15% | 48.12% | -1.97 pp* | [-3.34, -0.59 pp] | 0.0050 | 0.0101 |
| reliability | `good_record - poor_record` | 74.57% | 19.69% | +54.88 pp*** | [+53.51, +56.25 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 49.92% | 44.35% | +5.57 pp*** | [+4.20, +6.95 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 47.40% | 46.87% | +0.53 pp | [-0.84, +1.91 pp] | 0.4454 | 0.4454 |
| age | `old - young` | 45.92% | 48.35% | -2.43 pp** | [-3.80, -1.05 pp] | 0.0005 | 0.0016 |

**Outcome: CHECKED_FALSE (%)** (n=14,927, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.23% | 0.31% | -0.08 pp | [-0.24, +0.08 pp] | 0.3378 | 1.0000 |
| authority | `mayor - citizen` | 0.21% | 0.32% | -0.11 pp | [-0.27, +0.06 pp] | 0.2010 | 1.0000 |
| reliability | `good_record - poor_record` | 0.08% | 0.46% | -0.37 pp*** | [-0.54, -0.21 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.29% | 0.24% | +0.05 pp | [-0.11, +0.22 pp] | 0.5213 | 1.0000 |
| gender | `woman - man` | 0.26% | 0.28% | -0.02 pp | [-0.19, +0.14 pp] | 0.7721 | 1.0000 |
| age | `old - young` | 0.27% | 0.27% | -0.00 pp | [-0.16, +0.16 pp] | 0.9985 | 1.0000 |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=14,828, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8211 | 0.7554 | +0.0657*** | [+0.0537, +0.0778] | <0.0001 | <0.0001 | +0.0658 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8009 | 0.7756 | +0.0253*** | [+0.0132, +0.0373] | <0.0001 | 0.0001 | +0.0253 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.9305 | 0.6460 | +0.2844*** | [+0.2724, +0.2965] | <0.0001 | <0.0001 | +0.2844 (p=<0.0001) |
| wealth | `rich - poor` | 0.8047 | 0.7718 | +0.0330*** | [+0.0210, +0.0450] | <0.0001 | <0.0001 | +0.0330 (p=<0.0001) |
| gender | `woman - man` | 0.7894 | 0.7871 | +0.0023 | [-0.0098, +0.0144] | 0.7078 | 0.7078 | +0.0023 (p=0.7070) |
| age | `old - young` | 0.7780 | 0.7985 | -0.0204** | [-0.0324, -0.0084] | 0.0009 | 0.0018 | -0.0204 (p=0.0009) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8209 | 0.7548 | +0.0661*** | [+0.0541, +0.0781] | <0.0001 | <0.0001 | +0.0661 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8007 | 0.7751 | +0.0256*** | [+0.0136, +0.0377] | <0.0001 | <0.0001 | +0.0257 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.9303 | 0.6454 | +0.2849*** | [+0.2729, +0.2969] | <0.0001 | <0.0001 | +0.2849 (p=<0.0001) |
| wealth | `rich - poor` | 0.8041 | 0.7716 | +0.0325*** | [+0.0205, +0.0445] | <0.0001 | <0.0001 | +0.0325 (p=<0.0001) |
| gender | `woman - man` | 0.7890 | 0.7868 | +0.0023 | [-0.0098, +0.0143] | 0.7139 | 0.7139 | +0.0023 (p=0.7127) |
| age | `old - young` | 0.7778 | 0.7980 | -0.0202** | [-0.0322, -0.0082] | 0.0010 | 0.0020 | -0.0202 (p=0.0010) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8211 | 0.7552 | +0.0658*** | [+0.0538, +0.0778] | <0.0001 | <0.0001 | +0.0658 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8008 | 0.7755 | +0.0254*** | [+0.0134, +0.0374] | <0.0001 | 0.0001 | +0.0254 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.9304 | 0.6459 | +0.2845*** | [+0.2725, +0.2965] | <0.0001 | <0.0001 | +0.2845 (p=<0.0001) |
| wealth | `rich - poor` | 0.8046 | 0.7717 | +0.0329*** | [+0.0209, +0.0449] | <0.0001 | <0.0001 | +0.0329 (p=<0.0001) |
| gender | `woman - man` | 0.7893 | 0.7870 | +0.0023 | [-0.0098, +0.0143] | 0.7131 | 0.7131 | +0.0023 (p=0.7119) |
| age | `old - young` | 0.7780 | 0.7983 | -0.0203** | [-0.0323, -0.0083] | 0.0009 | 0.0019 | -0.0203 (p=0.0010) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 70.85% | 64.86% | +5.98 pp*** | [+4.55, +7.42 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 69.95% | 65.76% | +4.19 pp*** | [+2.76, +5.63 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 76.98% | 58.73% | +18.24 pp*** | [+16.81, +19.68 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 67.63% | 68.08% | -0.45 pp | [-1.89, +0.98 pp] | 0.5352 | 0.5352 |
| gender | `woman - man` | 68.51% | 67.20% | +1.31 pp | [-0.12, +2.75 pp] | 0.0734 | 0.1469 |
| age | `old - young` | 66.75% | 68.96% | -2.22 pp** | [-3.65, -0.78 pp] | 0.0025 | 0.0074 |

**Outcome: NOT_MENTIONED (%)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.03% | 0.08% | -0.05 pp | [-0.13, +0.02 pp] | 0.1573 | 0.6222 |
| authority | `mayor - citizen` | 0.03% | 0.08% | -0.05 pp | [-0.13, +0.02 pp] | 0.1555 | 0.6222 |
| reliability | `good_record - poor_record` | 0.01% | 0.09% | -0.08 pp | [-0.16, -0.01 pp] | 0.0333 | 0.1984 |
| wealth | `rich - poor` | 0.09% | 0.01% | +0.08 pp | [+0.01, +0.16 pp] | 0.0331 | 0.1984 |
| gender | `woman - man` | 0.05% | 0.05% | +0.00 pp | [-0.07, +0.08 pp] | 0.9704 | 0.9704 |
| age | `old - young` | 0.04% | 0.07% | -0.03 pp | [-0.10, +0.05 pp] | 0.4785 | 0.9570 |

**Outcome: FACT (%)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 9.22% | 6.49% | +2.73 pp*** | [+1.86, +3.61 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 8.69% | 7.03% | +1.66 pp*** | [+0.78, +2.54 pp] | 0.0002 | 0.0008 |
| reliability | `good_record - poor_record` | 11.41% | 4.30% | +7.11 pp*** | [+6.24, +7.98 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 8.20% | 7.51% | +0.68 pp | [-0.19, +1.56 pp] | 0.1275 | 0.3825 |
| gender | `woman - man` | 8.01% | 7.70% | +0.30 pp | [-0.57, +1.18 pp] | 0.4951 | 0.9902 |
| age | `old - young` | 7.75% | 7.96% | -0.22 pp | [-1.09, +0.66 pp] | 0.6256 | 0.9902 |

**Outcome: UNCERTAIN (%)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 7.63% | 6.09% | +1.55 pp*** | [+0.74, +2.35 pp] | 0.0002 | 0.0009 |
| authority | `mayor - citizen` | 7.47% | 6.24% | +1.23 pp* | [+0.43, +2.04 pp] | 0.0027 | 0.0109 |
| reliability | `good_record - poor_record` | 9.70% | 4.01% | +5.69 pp*** | [+4.88, +6.49 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 6.82% | 6.90% | -0.07 pp | [-0.88, +0.73 pp] | 0.8553 | 1.0000 |
| gender | `woman - man` | 6.97% | 6.75% | +0.22 pp | [-0.59, +1.03 pp] | 0.5946 | 1.0000 |
| age | `old - young` | 6.98% | 6.74% | +0.24 pp | [-0.56, +1.05 pp] | 0.5575 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 13.90% | 21.18% | -7.27 pp*** | [-8.43, -6.12 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 16.02% | 19.06% | -3.05 pp*** | [-4.20, -1.89 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 2.03% | 33.05% | -31.01 pp*** | [-32.17, -29.85 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 15.87% | 19.21% | -3.35 pp*** | [-4.50, -2.19 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 17.38% | 17.70% | -0.31 pp | [-1.47, +0.85 pp] | 0.5988 | 0.5988 |
| age | `old - young` | 18.53% | 16.55% | +1.98 pp** | [+0.82, +3.13 pp] | 0.0008 | 0.0016 |

**Outcome: CHECKED_TRUE (%)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 69.06% | 65.95% | +3.10 pp*** | [+1.56, +4.64 pp] | <0.0001 | 0.0004 |
| authority | `mayor - citizen` | 67.65% | 67.36% | +0.29 pp | [-1.25, +1.83 pp] | 0.7133 | 1.0000 |
| reliability | `good_record - poor_record` | 76.77% | 58.23% | +18.54 pp*** | [+17.00, +20.08 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 68.81% | 66.20% | +2.61 pp** | [+1.07, +4.15 pp] | 0.0009 | 0.0036 |
| gender | `woman - man` | 67.41% | 67.60% | -0.19 pp | [-1.73, +1.35 pp] | 0.8099 | 1.0000 |
| age | `old - young` | 66.54% | 68.46% | -1.92 pp* | [-3.46, -0.38 pp] | 0.0145 | 0.0435 |

**Outcome: CHECKED_FALSE (%)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.16% | 0.22% | -0.05 pp | [-0.19, +0.09 pp] | 0.4536 | 1.0000 |
| authority | `mayor - citizen` | 0.15% | 0.23% | -0.08 pp | [-0.22, +0.06 pp] | 0.2550 | 1.0000 |
| reliability | `good_record - poor_record` | 0.07% | 0.31% | -0.24 pp** | [-0.38, -0.10 pp] | 0.0006 | 0.0036 |
| wealth | `rich - poor` | 0.22% | 0.16% | +0.05 pp | [-0.08, +0.19 pp] | 0.4446 | 1.0000 |
| gender | `woman - man` | 0.18% | 0.20% | -0.03 pp | [-0.16, +0.11 pp] | 0.7201 | 1.0000 |
| age | `old - young` | 0.16% | 0.22% | -0.05 pp | [-0.19, +0.08 pp] | 0.4470 | 1.0000 |

### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=29,795, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8833 | 0.8065 | +0.0768*** | [+0.0687, +0.0849] | <0.0001 | <0.0001 | +0.0768 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8437 | 0.8462 | -0.0025 | [-0.0106, +0.0057] | 0.5482 | 0.5920 | -0.0025 (p=0.5491) |
| reliability | `good_record - poor_record` | 0.9214 | 0.7684 | +0.1530*** | [+0.1448, +0.1611] | <0.0001 | <0.0001 | +0.1530 (p=<0.0001) |
| wealth | `rich - poor` | 0.8573 | 0.8326 | +0.0246*** | [+0.0165, +0.0328] | <0.0001 | <0.0001 | +0.0247 (p=<0.0001) |
| gender | `woman - man` | 0.8426 | 0.8473 | -0.0047 | [-0.0128, +0.0035] | 0.2604 | 0.5920 | -0.0047 (p=0.2596) |
| age | `old - young` | 0.8476 | 0.8423 | +0.0054 | [-0.0028, +0.0135] | 0.1973 | 0.5920 | +0.0053 (p=0.1996) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8797 | 0.8029 | +0.0767*** | [+0.0685, +0.0850] | <0.0001 | <0.0001 | +0.0767 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8413 | 0.8414 | -0.0001 | [-0.0083, +0.0081] | 0.9808 | 0.9808 | -0.0001 (p=0.9811) |
| reliability | `good_record - poor_record` | 0.9186 | 0.7640 | +0.1546*** | [+0.1463, +0.1628] | <0.0001 | <0.0001 | +0.1546 (p=<0.0001) |
| wealth | `rich - poor` | 0.8539 | 0.8287 | +0.0252*** | [+0.0170, +0.0334] | <0.0001 | <0.0001 | +0.0252 (p=<0.0001) |
| gender | `woman - man` | 0.8398 | 0.8428 | -0.0030 | [-0.0112, +0.0052] | 0.4719 | 0.9437 | -0.0030 (p=0.4730) |
| age | `old - young` | 0.8439 | 0.8387 | +0.0051 | [-0.0031, +0.0133] | 0.2228 | 0.6684 | +0.0051 (p=0.2230) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8818 | 0.8053 | +0.0765*** | [+0.0684, +0.0846] | <0.0001 | <0.0001 | +0.0765 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8428 | 0.8443 | -0.0015 | [-0.0097, +0.0066] | 0.7108 | 0.7108 | -0.0015 (p=0.7113) |
| reliability | `good_record - poor_record` | 0.9201 | 0.7669 | +0.1532*** | [+0.1451, +0.1613] | <0.0001 | <0.0001 | +0.1532 (p=<0.0001) |
| wealth | `rich - poor` | 0.8559 | 0.8311 | +0.0248*** | [+0.0166, +0.0329] | <0.0001 | <0.0001 | +0.0248 (p=<0.0001) |
| gender | `woman - man` | 0.8415 | 0.8455 | -0.0040 | [-0.0121, +0.0041] | 0.3359 | 0.6718 | -0.0040 (p=0.3370) |
| age | `old - young` | 0.8462 | 0.8409 | +0.0053 | [-0.0028, +0.0134] | 0.2030 | 0.6089 | +0.0053 (p=0.2031) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 60.82% | 55.76% | +5.06 pp*** | [+4.32, +5.80 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 57.99% | 58.59% | -0.60 pp | [-1.34, +0.14 pp] | 0.1128 | 0.3385 |
| reliability | `good_record - poor_record` | 60.42% | 56.17% | +4.25 pp*** | [+3.50, +4.99 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 59.38% | 57.20% | +2.18 pp*** | [+1.43, +2.92 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 58.27% | 58.31% | -0.04 pp | [-0.78, +0.70 pp] | 0.9158 | 1.0000 |
| age | `old - young` | 58.37% | 58.22% | +0.15 pp | [-0.60, +0.89 pp] | 0.6983 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.42% | 0.47% | -0.05 pp | [-0.20, +0.10 pp] | 0.5462 | 1.0000 |
| authority | `mayor - citizen` | 0.30% | 0.59% | -0.29 pp** | [-0.44, -0.14 pp] | 0.0002 | 0.0012 |
| reliability | `good_record - poor_record` | 0.31% | 0.58% | -0.27 pp** | [-0.43, -0.12 pp] | 0.0004 | 0.0020 |
| wealth | `rich - poor` | 0.40% | 0.49% | -0.09 pp | [-0.24, +0.06 pp] | 0.2609 | 0.7827 |
| gender | `woman - man` | 0.35% | 0.54% | -0.19 pp* | [-0.35, -0.04 pp] | 0.0119 | 0.0475 |
| age | `old - young` | 0.46% | 0.43% | +0.03 pp | [-0.12, +0.19 pp] | 0.6641 | 1.0000 |

**Outcome: FACT (%)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 8.63% | 6.40% | +2.23 pp*** | [+1.63, +2.83 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 7.76% | 7.28% | +0.48 pp | [-0.12, +1.07 pp] | 0.1155 | 0.4620 |
| reliability | `good_record - poor_record` | 9.93% | 5.10% | +4.83 pp*** | [+4.23, +5.42 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 7.61% | 7.43% | +0.17 pp | [-0.42, +0.77 pp] | 0.5666 | 1.0000 |
| gender | `woman - man` | 7.40% | 7.64% | -0.24 pp | [-0.84, +0.36 pp] | 0.4295 | 1.0000 |
| age | `old - young` | 7.58% | 7.46% | +0.12 pp | [-0.47, +0.72 pp] | 0.6870 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 7.48% | 8.19% | -0.71 pp | [-1.32, -0.11 pp] | 0.0214 | 0.0857 |
| authority | `mayor - citizen` | 8.50% | 7.17% | +1.33 pp*** | [+0.73, +1.94 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 11.44% | 4.22% | +7.22 pp*** | [+6.62, +7.83 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 8.03% | 7.64% | +0.39 pp | [-0.22, +0.99 pp] | 0.2090 | 0.6270 |
| gender | `woman - man` | 7.82% | 7.85% | -0.03 pp | [-0.64, +0.58 pp] | 0.9208 | 1.0000 |
| age | `old - young` | 7.77% | 7.89% | -0.12 pp | [-0.72, +0.49 pp] | 0.7051 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 7.53% | 14.75% | -7.22 pp*** | [-8.00, -6.45 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 10.96% | 11.31% | -0.35 pp | [-1.12, +0.42 pp] | 0.3752 | 0.6428 |
| reliability | `good_record - poor_record` | 2.10% | 20.18% | -18.08 pp*** | [-18.85, -17.31 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 9.88% | 12.40% | -2.51 pp*** | [-3.29, -1.74 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 11.38% | 10.89% | +0.49 pp | [-0.28, +1.26 pp] | 0.2143 | 0.6428 |
| age | `old - young` | 10.93% | 11.34% | -0.41 pp | [-1.19, +0.36 pp] | 0.2945 | 0.6428 |

**Outcome: CHECKED_TRUE (%)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 75.59% | 69.80% | +5.80 pp*** | [+4.78, +6.82 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 72.12% | 73.27% | -1.16 pp | [-2.18, -0.14 pp] | 0.0264 | 0.0792 |
| reliability | `good_record - poor_record` | 76.20% | 69.19% | +7.02 pp*** | [+6.00, +8.04 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 73.77% | 71.62% | +2.15 pp*** | [+1.13, +3.17 pp] | <0.0001 | 0.0001 |
| gender | `woman - man` | 72.67% | 72.72% | -0.05 pp | [-1.07, +0.98 pp] | 0.9302 | 0.9302 |
| age | `old - young` | 72.92% | 72.47% | +0.45 pp | [-0.57, +1.47 pp] | 0.3903 | 0.7805 |

**Outcome: CHECKED_FALSE (%)** (n=29,928, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.35% | 0.39% | -0.05 pp | [-0.20, +0.10 pp] | 0.5464 | 1.0000 |
| authority | `mayor - citizen` | 0.36% | 0.38% | -0.02 pp | [-0.17, +0.13 pp] | 0.7946 | 1.0000 |
| reliability | `good_record - poor_record` | 0.01% | 0.73% | -0.71 pp*** | [-0.87, -0.56 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.31% | 0.43% | -0.11 pp | [-0.26, +0.04 pp] | 0.1408 | 0.7038 |
| gender | `woman - man` | 0.38% | 0.36% | +0.02 pp | [-0.13, +0.17 pp] | 0.7656 | 1.0000 |
| age | `old - young` | 0.33% | 0.41% | -0.07 pp | [-0.22, +0.08 pp] | 0.3404 | 1.0000 |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,946, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.9505 | 0.8347 | +0.1159*** | [+0.1060, +0.1258] | <0.0001 | <0.0001 | +0.1158 (p=<0.0001) |
| authority | `mayor - citizen` | 0.9000 | 0.8851 | +0.0149** | [+0.0050, +0.0248] | 0.0032 | 0.0095 | +0.0149 (p=0.0032) |
| reliability | `good_record - poor_record` | 0.9720 | 0.8132 | +0.1588*** | [+0.1489, +0.1687] | <0.0001 | <0.0001 | +0.1589 (p=<0.0001) |
| wealth | `rich - poor` | 0.9078 | 0.8773 | +0.0305*** | [+0.0206, +0.0404] | <0.0001 | <0.0001 | +0.0305 (p=<0.0001) |
| gender | `woman - man` | 0.8932 | 0.8920 | +0.0013 | [-0.0086, +0.0112] | 0.8022 | 0.8022 | +0.0012 (p=0.8058) |
| age | `old - young` | 0.8959 | 0.8893 | +0.0065 | [-0.0034, +0.0164] | 0.1964 | 0.3927 | +0.0065 (p=0.1969) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.9489 | 0.8339 | +0.1150*** | [+0.1050, +0.1249] | <0.0001 | <0.0001 | +0.1149 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8988 | 0.8839 | +0.0149* | [+0.0049, +0.0248] | 0.0034 | 0.0102 | +0.0149 (p=0.0034) |
| reliability | `good_record - poor_record` | 0.9707 | 0.8121 | +0.1586*** | [+0.1487, +0.1686] | <0.0001 | <0.0001 | +0.1586 (p=<0.0001) |
| wealth | `rich - poor` | 0.9071 | 0.8757 | +0.0314*** | [+0.0214, +0.0413] | <0.0001 | <0.0001 | +0.0314 (p=<0.0001) |
| gender | `woman - man` | 0.8919 | 0.8909 | +0.0010 | [-0.0089, +0.0110] | 0.8420 | 0.8420 | +0.0010 (p=0.8429) |
| age | `old - young` | 0.8945 | 0.8882 | +0.0063 | [-0.0036, +0.0163] | 0.2137 | 0.4274 | +0.0063 (p=0.2134) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.9497 | 0.8344 | +0.1154*** | [+0.1055, +0.1253] | <0.0001 | <0.0001 | +0.1153 (p=<0.0001) |
| authority | `mayor - citizen` | 0.8995 | 0.8846 | +0.0149** | [+0.0050, +0.0248] | 0.0032 | 0.0097 | +0.0149 (p=0.0033) |
| reliability | `good_record - poor_record` | 0.9714 | 0.8127 | +0.1586*** | [+0.1487, +0.1685] | <0.0001 | <0.0001 | +0.1586 (p=<0.0001) |
| wealth | `rich - poor` | 0.9075 | 0.8766 | +0.0308*** | [+0.0209, +0.0408] | <0.0001 | <0.0001 | +0.0309 (p=<0.0001) |
| gender | `woman - man` | 0.8926 | 0.8915 | +0.0011 | [-0.0088, +0.0110] | 0.8205 | 0.8205 | +0.0011 (p=0.8215) |
| age | `old - young` | 0.8953 | 0.8888 | +0.0064 | [-0.0035, +0.0164] | 0.2018 | 0.4036 | +0.0065 (p=0.2015) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 98.33% | 87.14% | +11.19 pp*** | [+10.32, +12.06 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 94.03% | 91.44% | +2.59 pp*** | [+1.72, +3.46 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 99.75% | 85.72% | +14.02 pp*** | [+13.15, +14.89 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 94.66% | 90.81% | +3.85 pp*** | [+2.97, +4.72 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 92.53% | 92.94% | -0.41 pp | [-1.28, +0.46 pp] | 0.3578 | 0.7157 |
| age | `old - young` | 92.79% | 92.68% | +0.11 pp | [-0.76, +0.98 pp] | 0.8101 | 0.8101 |

**Outcome: NOT_MENTIONED (%)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.17% | 0.09% | +0.08 pp | [-0.04, +0.20 pp] | 0.1780 | 0.8901 |
| authority | `mayor - citizen` | 0.13% | 0.13% | +0.00 pp | [-0.12, +0.12 pp] | 0.9999 | 1.0000 |
| reliability | `good_record - poor_record` | 0.13% | 0.13% | -0.00 pp | [-0.12, +0.12 pp] | 0.9998 | 1.0000 |
| wealth | `rich - poor` | 0.08% | 0.19% | -0.11 pp | [-0.22, +0.01 pp] | 0.0723 | 0.4335 |
| gender | `woman - man` | 0.15% | 0.12% | +0.03 pp | [-0.09, +0.14 pp] | 0.6559 | 1.0000 |
| age | `old - young` | 0.15% | 0.12% | +0.03 pp | [-0.09, +0.14 pp] | 0.6531 | 1.0000 |

**Outcome: FACT (%)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 4.64% | 3.40% | +1.24 pp*** | [+0.62, +1.86 pp] | <0.0001 | 0.0006 |
| authority | `mayor - citizen` | 3.88% | 4.16% | -0.28 pp | [-0.90, +0.34 pp] | 0.3772 | 1.0000 |
| reliability | `good_record - poor_record` | 4.25% | 3.78% | +0.47 pp | [-0.16, +1.09 pp] | 0.1410 | 0.7048 |
| wealth | `rich - poor` | 4.08% | 3.96% | +0.12 pp | [-0.50, +0.74 pp] | 0.7076 | 1.0000 |
| gender | `woman - man` | 4.05% | 3.99% | +0.06 pp | [-0.56, +0.68 pp] | 0.8491 | 1.0000 |
| age | `old - young` | 3.86% | 4.17% | -0.31 pp | [-0.93, +0.32 pp] | 0.3351 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 3.06% | 4.17% | -1.11 pp** | [-1.70, -0.52 pp] | 0.0002 | 0.0012 |
| authority | `mayor - citizen` | 4.04% | 3.19% | +0.84 pp* | [+0.25, +1.43 pp] | 0.0053 | 0.0213 |
| reliability | `good_record - poor_record` | 4.54% | 2.69% | +1.86 pp*** | [+1.27, +2.45 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 3.57% | 3.66% | -0.09 pp | [-0.69, +0.50 pp] | 0.7543 | 1.0000 |
| gender | `woman - man` | 3.43% | 3.80% | -0.36 pp | [-0.96, +0.23 pp] | 0.2309 | 0.6928 |
| age | `old - young` | 3.58% | 3.65% | -0.07 pp | [-0.66, +0.53 pp] | 0.8287 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 3.26% | 14.07% | -10.81 pp*** | [-11.75, -9.86 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 7.74% | 9.59% | -1.86 pp*** | [-2.80, -0.91 pp] | 0.0001 | 0.0004 |
| reliability | `good_record - poor_record` | 0.51% | 16.82% | -16.31 pp*** | [-17.26, -15.36 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 7.24% | 10.09% | -2.85 pp*** | [-3.80, -1.90 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 8.73% | 8.60% | +0.13 pp | [-0.82, +1.08 pp] | 0.7886 | 0.7886 |
| age | `old - young` | 8.38% | 8.95% | -0.57 pp | [-1.52, +0.38 pp] | 0.2367 | 0.4734 |

**Outcome: CHECKED_TRUE (%)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 88.72% | 77.91% | +10.81 pp*** | [+9.60, +12.02 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 83.99% | 82.64% | +1.35 pp | [+0.14, +2.56 pp] | 0.0290 | 0.0869 |
| reliability | `good_record - poor_record` | 90.55% | 76.08% | +14.46 pp*** | [+13.25, +15.67 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 84.85% | 81.78% | +3.07 pp*** | [+1.86, +4.28 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 83.43% | 83.20% | +0.22 pp | [-0.99, +1.43 pp] | 0.7191 | 0.7191 |
| age | `old - young` | 83.80% | 82.83% | +0.97 pp | [-0.24, +2.18 pp] | 0.1157 | 0.2314 |

**Outcome: CHECKED_FALSE (%)** (n=14,966, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.15% | 0.36% | -0.21 pp | [-0.38, -0.05 pp] | 0.0102 | 0.0508 |
| authority | `mayor - citizen` | 0.23% | 0.28% | -0.05 pp | [-0.22, +0.11 pp] | 0.5206 | 1.0000 |
| reliability | `good_record - poor_record` | 0.01% | 0.49% | -0.48 pp*** | [-0.64, -0.32 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.19% | 0.32% | -0.13 pp | [-0.30, +0.03 pp] | 0.1077 | 0.4308 |
| gender | `woman - man` | 0.22% | 0.29% | -0.08 pp | [-0.24, +0.09 pp] | 0.3571 | 1.0000 |
| age | `old - young` | 0.23% | 0.28% | -0.05 pp | [-0.22, +0.11 pp] | 0.5203 | 1.0000 |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=14,849, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8158 | 0.7783 | +0.0375*** | [+0.0262, +0.0489] | <0.0001 | <0.0001 | +0.0375 (p=<0.0001) |
| authority | `mayor - citizen` | 0.7872 | 0.8069 | -0.0198** | [-0.0311, -0.0084] | 0.0007 | 0.0027 | -0.0198 (p=0.0007) |
| reliability | `good_record - poor_record` | 0.8707 | 0.7234 | +0.1473*** | [+0.1359, +0.1587] | <0.0001 | <0.0001 | +0.1473 (p=<0.0001) |
| wealth | `rich - poor` | 0.8064 | 0.7877 | +0.0186** | [+0.0073, +0.0300] | 0.0013 | 0.0040 | +0.0186 (p=0.0013) |
| gender | `woman - man` | 0.7918 | 0.8023 | -0.0105 | [-0.0219, +0.0009] | 0.0712 | 0.1424 | -0.0105 (p=0.0716) |
| age | `old - young` | 0.7992 | 0.7949 | +0.0043 | [-0.0071, +0.0156] | 0.4615 | 0.4615 | +0.0043 (p=0.4621) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8104 | 0.7720 | +0.0384*** | [+0.0269, +0.0499] | <0.0001 | <0.0001 | +0.0384 (p=<0.0001) |
| authority | `mayor - citizen` | 0.7837 | 0.7987 | -0.0151* | [-0.0266, -0.0036] | 0.0101 | 0.0304 | -0.0151 (p=0.0102) |
| reliability | `good_record - poor_record` | 0.8664 | 0.7160 | +0.1505*** | [+0.1390, +0.1620] | <0.0001 | <0.0001 | +0.1505 (p=<0.0001) |
| wealth | `rich - poor` | 0.8007 | 0.7817 | +0.0190** | [+0.0075, +0.0305] | 0.0012 | 0.0048 | +0.0190 (p=0.0012) |
| gender | `woman - man` | 0.7877 | 0.7947 | -0.0071 | [-0.0185, +0.0044] | 0.2292 | 0.4585 | -0.0071 (p=0.2299) |
| age | `old - young` | 0.7932 | 0.7892 | +0.0039 | [-0.0076, +0.0154] | 0.5033 | 0.5033 | +0.0039 (p=0.5039) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.8138 | 0.7762 | +0.0376*** | [+0.0262, +0.0489] | <0.0001 | <0.0001 | +0.0376 (p=<0.0001) |
| authority | `mayor - citizen` | 0.7860 | 0.8040 | -0.0180** | [-0.0293, -0.0066] | 0.0019 | 0.0056 | -0.0180 (p=0.0019) |
| reliability | `good_record - poor_record` | 0.8688 | 0.7211 | +0.1477*** | [+0.1364, +0.1591] | <0.0001 | <0.0001 | +0.1477 (p=<0.0001) |
| wealth | `rich - poor` | 0.8043 | 0.7857 | +0.0187** | [+0.0073, +0.0300] | 0.0012 | 0.0050 | +0.0187 (p=0.0013) |
| gender | `woman - man` | 0.7904 | 0.7995 | -0.0091 | [-0.0205, +0.0022] | 0.1138 | 0.2277 | -0.0091 (p=0.1143) |
| age | `old - young` | 0.7970 | 0.7929 | +0.0041 | [-0.0072, +0.0154] | 0.4747 | 0.4747 | +0.0041 (p=0.4753) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 23.32% | 24.39% | -1.07 pp | [-2.42, +0.28 pp] | 0.1211 | 0.4843 |
| authority | `mayor - citizen` | 21.96% | 25.75% | -3.79 pp*** | [-5.14, -2.44 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 21.09% | 26.62% | -5.53 pp*** | [-6.88, -4.18 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 24.11% | 23.60% | +0.51 pp | [-0.84, +1.86 pp] | 0.4615 | 1.0000 |
| gender | `woman - man` | 24.02% | 23.69% | +0.33 pp | [-1.02, +1.68 pp] | 0.6340 | 1.0000 |
| age | `old - young` | 23.94% | 23.76% | +0.19 pp | [-1.16, +1.54 pp] | 0.7862 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.67% | 0.84% | -0.17 pp | [-0.45, +0.10 pp] | 0.2165 | 0.6495 |
| authority | `mayor - citizen` | 0.47% | 1.04% | -0.58 pp*** | [-0.85, -0.30 pp] | <0.0001 | 0.0002 |
| reliability | `good_record - poor_record` | 0.48% | 1.03% | -0.55 pp*** | [-0.82, -0.27 pp] | <0.0001 | 0.0005 |
| wealth | `rich - poor` | 0.72% | 0.79% | -0.07 pp | [-0.34, +0.21 pp] | 0.6318 | 1.0000 |
| gender | `woman - man` | 0.55% | 0.96% | -0.42 pp* | [-0.69, -0.14 pp] | 0.0029 | 0.0118 |
| age | `old - young` | 0.78% | 0.73% | +0.04 pp | [-0.23, +0.32 pp] | 0.7713 | 1.0000 |

**Outcome: FACT (%)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 12.64% | 9.41% | +3.23 pp*** | [+2.24, +4.21 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 11.64% | 10.40% | +1.24 pp | [+0.25, +2.22 pp] | 0.0139 | 0.0557 |
| reliability | `good_record - poor_record` | 15.62% | 6.43% | +9.19 pp*** | [+8.20, +10.17 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 11.14% | 10.91% | +0.23 pp | [-0.75, +1.22 pp] | 0.6455 | 0.8161 |
| gender | `woman - man` | 10.75% | 11.29% | -0.54 pp | [-1.53, +0.44 pp] | 0.2809 | 0.8161 |
| age | `old - young` | 11.30% | 10.75% | +0.55 pp | [-0.43, +1.54 pp] | 0.2720 | 0.8161 |

**Outcome: UNCERTAIN (%)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 11.90% | 12.20% | -0.30 pp | [-1.34, +0.73 pp] | 0.5674 | 1.0000 |
| authority | `mayor - citizen` | 12.96% | 11.14% | +1.82 pp** | [+0.79, +2.86 pp] | 0.0006 | 0.0028 |
| reliability | `good_record - poor_record` | 18.34% | 5.76% | +12.58 pp*** | [+11.55, +13.62 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 12.49% | 11.62% | +0.87 pp | [-0.16, +1.91 pp] | 0.0985 | 0.3941 |
| gender | `woman - man` | 12.20% | 11.90% | +0.30 pp | [-0.74, +1.34 pp] | 0.5696 | 1.0000 |
| age | `old - young` | 11.97% | 12.14% | -0.17 pp | [-1.20, +0.87 pp] | 0.7498 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 11.79% | 15.43% | -3.64 pp*** | [-4.70, -2.58 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 14.19% | 13.03% | +1.16 pp | [+0.10, +2.22 pp] | 0.0320 | 0.0961 |
| reliability | `good_record - poor_record` | 3.69% | 23.53% | -19.84 pp*** | [-20.90, -18.78 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 12.52% | 14.70% | -2.18 pp*** | [-3.23, -1.12 pp] | <0.0001 | 0.0002 |
| gender | `woman - man` | 14.04% | 13.19% | +0.85 pp | [-0.21, +1.91 pp] | 0.1160 | 0.2320 |
| age | `old - young` | 13.48% | 13.74% | -0.26 pp | [-1.31, +0.80 pp] | 0.6365 | 0.6365 |

**Outcome: CHECKED_TRUE (%)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 62.46% | 61.69% | +0.77 pp | [-0.77, +2.31 pp] | 0.3288 | 1.0000 |
| authority | `mayor - citizen` | 60.24% | 63.90% | -3.66 pp*** | [-5.20, -2.11 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 61.85% | 62.29% | -0.43 pp | [-1.98, +1.11 pp] | 0.5811 | 1.0000 |
| wealth | `rich - poor` | 62.69% | 61.46% | +1.23 pp | [-0.31, +2.77 pp] | 0.1176 | 0.5878 |
| gender | `woman - man` | 61.91% | 62.23% | -0.31 pp | [-1.86, +1.23 pp] | 0.6910 | 1.0000 |
| age | `old - young` | 62.03% | 62.11% | -0.08 pp | [-1.62, +1.47 pp] | 0.9237 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=14,962, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.55% | 0.43% | +0.12 pp | [-0.10, +0.34 pp] | 0.2763 | 1.0000 |
| authority | `mayor - citizen` | 0.49% | 0.48% | +0.01 pp | [-0.20, +0.23 pp] | 0.9041 | 1.0000 |
| reliability | `good_record - poor_record` | 0.01% | 0.96% | -0.95 pp*** | [-1.17, -0.73 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.44% | 0.53% | -0.09 pp | [-0.31, +0.12 pp] | 0.4001 | 1.0000 |
| gender | `woman - man` | 0.55% | 0.43% | +0.12 pp | [-0.10, +0.34 pp] | 0.2721 | 1.0000 |
| age | `old - young` | 0.44% | 0.53% | -0.09 pp | [-0.31, +0.12 pp] | 0.3976 | 1.0000 |

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
