# Rumor Towns Report (False Claims)

**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Condition:** `rumor` | **Towns:** 4,992 (2,496 per model) | **Expected Listeners:** 59,904

### Methodological & Missingness Disclosure
- **Excluded Invalid Judgments:** 189 / 59,904 (0.32%) had `judgment_status = invalid`. They are **completely excluded** (`NaN`), never turned into zeros.
- **Label % Denominator:** Valid judgments (`FACT + UNCERTAIN + SKEPTICAL + CHECKED_TRUE + CHECKED_FALSE + NOT_MENTIONED = 100%`).
- **Primary Belief Denominator:** Valid mentioning listeners (excluding `NOT_MENTIONED` and `INVALID`). Sensitivity checks (`Silence=0.0`, `Silence=0.5`) impute *only* valid `NOT_MENTIONED` rows.
- **Verification (`GO`/`SKIP`):** 0 missing or invalid decisions. 50 simulation decisions (24 first-hand, 26 second-hand; 0.08%) were `malformed_fallback_skip` in the simulation runner and appear as `SKIP`.
- **Statistical Model:** Controlled main effects of all 6 knobs simultaneously (`closeness`, `authority`, `reliability`, `wealth`, `gender`, `age` + `real_artist`), with standard errors clustered by town (`run_id`) and Holm adjustment across the 6 knobs per outcome. `Belief` also reports the spec's town-random-intercept LMM (`mixedlm`) check.

---

## 1. Overall Categorical & Behavioral Summary

### Table A: Per-Model Summary (First-Hand, Second-Hand, and Overall)

| Model | Layer | Valid N | Invalid (n / %) | Belief | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | First-Hand (Seats 1-6) | 14,931 | 45 (0.3%) | 0.091 | 0.091 | 0.094 | 48.3% | 51.7% | 0.3% | 16.0% | 35.4% | 0.7% | 46.9% | 0.6% | 100.0% | 71.8% |
| DeepSeek-V4-Flash | Second-Hand (Seats 7-12) | 14,917 | 59 (0.4%) | 0.023 | 0.021 | 0.065 | 62.0% | 38.0% | 0.2% | 3.8% | 22.5% | 0.0% | 64.8% | 8.7% | — | — |
| DeepSeek-V4-Flash | Overall (All 12 Listeners) | 29,848 | 104 (0.3%) | 0.059 | 0.056 | 0.079 | 55.2% | 44.8% | 0.3% | 9.9% | 28.9% | 0.4% | 55.8% | 4.7% | 100.0% | 71.8% |
| Qwen3.8-Flash | First-Hand (Seats 1-6) | 14,967 | 9 (0.1%) | 0.005 | 0.005 | 0.008 | 92.8% | 7.2% | 0.0% | 0.9% | 8.5% | 0.0% | 90.0% | 0.5% | 95.9% | 60.4% |
| Qwen3.8-Flash | Second-Hand (Seats 7-12) | 14,900 | 76 (0.5%) | 0.036 | 0.034 | 0.061 | 28.6% | 71.4% | 0.9% | 4.7% | 19.1% | 0.1% | 69.8% | 5.4% | — | — |
| Qwen3.8-Flash | Overall (All 12 Listeners) | 29,867 | 85 (0.3%) | 0.020 | 0.020 | 0.034 | 60.7% | 39.3% | 0.5% | 2.8% | 13.8% | 0.1% | 79.9% | 2.9% | 95.9% | 60.4% |

### Table B: Entire Experiment Average (Both Models Combined)

| Scope | Layer | Valid N | Invalid (n / %) | Belief | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Both Models Combined | First-Hand (Seats 1-6) | 29,898 | 54 (0.2%) | 0.048 | 0.048 | 0.051 | 70.5% | 29.5% | 0.2% | 8.5% | 21.9% | 0.4% | 68.5% | 0.6% | 97.9% | 64.3% |
| Both Models Combined | Second-Hand (Seats 7-12) | 29,817 | 135 (0.5%) | 0.030 | 0.028 | 0.063 | 45.3% | 54.7% | 0.5% | 4.2% | 20.8% | 0.1% | 67.3% | 7.0% | — | — |
| Both Models Combined | Overall (All 12 Listeners) | 59,715 | 189 (0.3%) | 0.039 | 0.038 | 0.057 | 57.9% | 42.1% | 0.4% | 6.4% | 21.4% | 0.2% | 67.9% | 3.8% | 97.9% | 64.3% |

---

## 2. Gatekeeper & Downstream Susceptibility (`Seat i <-> Seat i+6`)

Shows what happened to **Second-Hand Listeners (Seats 7-12)** depending on whether their paired **First-Hand Partner (Seats 1-6)** checked the noticeboard (`GO`) or did not (`SKIP`).

| Model | First-Hand Partner | Pairs (n / share) | SH GO % | SH Belief | SH FACT % | SH UNCERTAIN % | SH SKEPTICAL % | SH CHECKED_TRUE % | SH CHECKED_FALSE % | SH NOT_MENTIONED % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | ALL | 14,976 (100.0%) | 62.0% | 0.023 | 0.2% | 3.8% | 22.5% | 0.0% | 64.8% | 8.7% |
| DeepSeek-V4-Flash | GO | 7,229 (48.3%) | 59.4% | 0.028 | 0.3% | 4.0% | 11.0% | 0.1% | 69.7% | 14.9% |
| DeepSeek-V4-Flash | SKIP | 7,747 (51.7%) | 64.5% | 0.020 | 0.1% | 3.6% | 33.2% | 0.0% | 60.2% | 2.9% |
| Qwen3.8-Flash | ALL | 14,976 (100.0%) | 28.6% | 0.036 | 0.9% | 4.7% | 19.1% | 0.1% | 69.8% | 5.4% |
| Qwen3.8-Flash | GO | 13,896 (92.8%) | 26.3% | 0.038 | 0.9% | 4.9% | 17.7% | 0.2% | 70.8% | 5.5% |
| Qwen3.8-Flash | SKIP | 1,080 (7.2%) | 58.1% | 0.013 | 0.1% | 2.4% | 37.4% | 0.0% | 57.1% | 3.0% |
| Both Models Combined | ALL | 29,952 (100.0%) | 45.3% | 0.030 | 0.5% | 4.2% | 20.8% | 0.1% | 67.3% | 7.0% |
| Both Models Combined | GO | 21,125 (70.5%) | 37.6% | 0.034 | 0.7% | 4.6% | 15.4% | 0.1% | 70.4% | 8.8% |
| Both Models Combined | SKIP | 8,827 (29.5%) | 63.7% | 0.019 | 0.1% | 3.4% | 33.7% | 0.0% | 59.9% | 2.9% |

---

## 3. Controlled Main Effects of the 6 Knobs (Town-Clustered)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=28,456, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0602 | 0.0585 | +0.0018 | [-0.0021, +0.0056] | 0.3730 | 0.6577 | +0.0018 (p=0.3856) |
| authority | `mayor - citizen` | 0.0650 | 0.0537 | +0.0113*** | [+0.0074, +0.0151] | <0.0001 | <0.0001 | +0.0113 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.0767 | 0.0420 | +0.0347*** | [+0.0308, +0.0386] | <0.0001 | <0.0001 | +0.0347 (p=<0.0001) |
| wealth | `rich - poor` | 0.0571 | 0.0616 | -0.0044 | [-0.0083, -0.0006] | 0.0242 | 0.0966 | -0.0044 (p=0.0281) |
| gender | `woman - man` | 0.0603 | 0.0584 | +0.0019 | [-0.0019, +0.0058] | 0.3289 | 0.6577 | +0.0019 (p=0.3414) |
| age | `old - young` | 0.0580 | 0.0607 | -0.0027 | [-0.0066, +0.0011] | 0.1690 | 0.5069 | -0.0027 (p=0.1803) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0568 | 0.0553 | +0.0015 | [-0.0022, +0.0052] | 0.4354 | 0.6861 | +0.0015 (p=0.4457) |
| authority | `mayor - citizen` | 0.0614 | 0.0507 | +0.0106*** | [+0.0069, +0.0143] | <0.0001 | <0.0001 | +0.0106 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.0708 | 0.0413 | +0.0296*** | [+0.0259, +0.0333] | <0.0001 | <0.0001 | +0.0296 (p=<0.0001) |
| wealth | `rich - poor` | 0.0540 | 0.0581 | -0.0040 | [-0.0077, -0.0003] | 0.0336 | 0.1345 | -0.0040 (p=0.0378) |
| gender | `woman - man` | 0.0570 | 0.0551 | +0.0020 | [-0.0017, +0.0057] | 0.2981 | 0.6861 | +0.0020 (p=0.3088) |
| age | `old - young` | 0.0549 | 0.0572 | -0.0023 | [-0.0060, +0.0014] | 0.2287 | 0.6861 | -0.0023 (p=0.2392) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0812 | 0.0776 | +0.0036 | [-0.0005, +0.0077] | 0.0888 | 0.1777 | +0.0036 (p=0.1029) |
| authority | `mayor - citizen` | 0.0851 | 0.0736 | +0.0115*** | [+0.0074, +0.0156] | <0.0001 | <0.0001 | +0.0115 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.1088 | 0.0499 | +0.0589*** | [+0.0548, +0.0630] | <0.0001 | <0.0001 | +0.0589 (p=<0.0001) |
| wealth | `rich - poor` | 0.0768 | 0.0819 | -0.0051 | [-0.0092, -0.0010] | 0.0143 | 0.0572 | -0.0051 (p=0.0189) |
| gender | `woman - man` | 0.0799 | 0.0788 | +0.0011 | [-0.0030, +0.0052] | 0.6020 | 0.6020 | +0.0011 (p=0.6167) |
| age | `old - young` | 0.0771 | 0.0816 | -0.0045 | [-0.0086, -0.0004] | 0.0318 | 0.0953 | -0.0045 (p=0.0396) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 58.99% | 51.31% | +7.69 pp*** | [+6.82, +8.55 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 55.70% | 54.60% | +1.10 pp* | [+0.23, +1.97 pp] | 0.0129 | 0.0129 |
| reliability | `good_record - poor_record` | 73.73% | 36.57% | +37.16 pp*** | [+36.29, +38.03 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 56.46% | 53.84% | +2.62 pp*** | [+1.76, +3.49 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 55.78% | 54.52% | +1.26 pp** | [+0.39, +2.13 pp] | 0.0045 | 0.0090 |
| age | `old - young` | 54.41% | 55.90% | -1.49 pp** | [-2.36, -0.62 pp] | 0.0008 | 0.0023 |

**Outcome: NOT_MENTIONED (%)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 4.88% | 4.46% | +0.42 pp | [-0.04, +0.88 pp] | 0.0733 | 0.2933 |
| authority | `mayor - citizen` | 4.76% | 4.58% | +0.18 pp | [-0.28, +0.64 pp] | 0.4432 | 1.0000 |
| reliability | `good_record - poor_record` | 7.60% | 1.73% | +5.87 pp*** | [+5.41, +6.33 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 4.55% | 4.78% | -0.22 pp | [-0.68, +0.23 pp] | 0.3371 | 1.0000 |
| gender | `woman - man` | 4.58% | 4.75% | -0.17 pp | [-0.63, +0.28 pp] | 0.4560 | 1.0000 |
| age | `old - young` | 4.44% | 4.89% | -0.45 pp | [-0.90, +0.01 pp] | 0.0568 | 0.2839 |

**Outcome: FACT (%)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.31% | 0.20% | +0.11 pp | [+0.00, +0.23 pp] | 0.0498 | 0.2410 |
| authority | `mayor - citizen` | 0.31% | 0.21% | +0.10 pp | [-0.01, +0.21 pp] | 0.0837 | 0.2511 |
| reliability | `good_record - poor_record` | 0.49% | 0.03% | +0.46 pp*** | [+0.35, +0.58 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.30% | 0.22% | +0.07 pp | [-0.04, +0.19 pp] | 0.2011 | 0.4021 |
| gender | `woman - man` | 0.32% | 0.20% | +0.11 pp | [+0.00, +0.23 pp] | 0.0482 | 0.2410 |
| age | `old - young` | 0.29% | 0.23% | +0.06 pp | [-0.05, +0.17 pp] | 0.2982 | 0.4021 |

**Outcome: UNCERTAIN (%)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 9.87% | 9.96% | -0.09 pp | [-0.76, +0.58 pp] | 0.7893 | 1.0000 |
| authority | `mayor - citizen` | 10.74% | 9.09% | +1.66 pp*** | [+0.99, +2.32 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 11.66% | 8.17% | +3.49 pp*** | [+2.82, +4.15 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 9.45% | 10.38% | -0.92 pp* | [-1.59, -0.26 pp] | 0.0067 | 0.0268 |
| gender | `woman - man` | 9.99% | 9.84% | +0.16 pp | [-0.51, +0.83 pp] | 0.6396 | 1.0000 |
| age | `old - young` | 9.87% | 9.96% | -0.09 pp | [-0.76, +0.58 pp] | 0.7875 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 24.56% | 33.26% | -8.71 pp*** | [-9.66, -7.76 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 27.75% | 30.07% | -2.31 pp*** | [-3.26, -1.36 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 6.09% | 51.73% | -45.64 pp*** | [-46.59, -44.69 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 27.61% | 30.21% | -2.60 pp*** | [-3.55, -1.65 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 28.53% | 29.29% | -0.76 pp | [-1.71, +0.19 pp] | 0.1189 | 0.1189 |
| age | `old - young` | 29.81% | 28.01% | +1.80 pp*** | [+0.85, +2.75 pp] | 0.0002 | 0.0004 |

**Outcome: CHECKED_TRUE (%)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.43% | 0.35% | +0.08 pp | [-0.06, +0.22 pp] | 0.2800 | 0.8399 |
| authority | `mayor - citizen` | 0.46% | 0.32% | +0.13 pp | [-0.01, +0.28 pp] | 0.0706 | 0.2824 |
| reliability | `good_record - poor_record` | 0.76% | 0.01% | +0.75 pp*** | [+0.61, +0.90 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.38% | 0.40% | -0.01 pp | [-0.16, +0.13 pp] | 0.8570 | 1.0000 |
| gender | `woman - man` | 0.39% | 0.39% | +0.00 pp | [-0.14, +0.15 pp] | 0.9705 | 1.0000 |
| age | `old - young` | 0.27% | 0.51% | -0.24 pp** | [-0.39, -0.10 pp] | 0.0010 | 0.0052 |

**Outcome: CHECKED_FALSE (%)** (n=29,848, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 59.95% | 51.77% | +8.19 pp*** | [+7.18, +9.20 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 55.98% | 55.74% | +0.25 pp | [-0.76, +1.25 pp] | 0.6328 | 0.6328 |
| reliability | `good_record - poor_record` | 73.40% | 38.32% | +35.08 pp*** | [+34.07, +36.08 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 57.70% | 54.02% | +3.69 pp*** | [+2.68, +4.69 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 56.19% | 55.53% | +0.65 pp | [-0.35, +1.66 pp] | 0.2029 | 0.4059 |
| age | `old - young` | 55.32% | 56.40% | -1.08 pp | [-2.09, -0.07 pp] | 0.0353 | 0.1059 |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,836, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0917 | 0.0911 | +0.0006 | [-0.0061, +0.0072] | 0.8720 | 1.0000 | +0.0005 (p=0.8737) |
| authority | `mayor - citizen` | 0.1010 | 0.0818 | +0.0193*** | [+0.0126, +0.0260] | <0.0001 | <0.0001 | +0.0193 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.1145 | 0.0684 | +0.0461*** | [+0.0394, +0.0528] | <0.0001 | <0.0001 | +0.0461 (p=<0.0001) |
| wealth | `rich - poor` | 0.0859 | 0.0969 | -0.0110** | [-0.0177, -0.0043] | 0.0013 | 0.0051 | -0.0110 (p=0.0013) |
| gender | `woman - man` | 0.0927 | 0.0902 | +0.0025 | [-0.0042, +0.0092] | 0.4649 | 1.0000 | +0.0025 (p=0.4635) |
| age | `old - young` | 0.0898 | 0.0930 | -0.0031 | [-0.0098, +0.0036] | 0.3594 | 1.0000 | -0.0031 (p=0.3597) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0910 | 0.0905 | +0.0006 | [-0.0061, +0.0072] | 0.8693 | 1.0000 | +0.0006 (p=0.8703) |
| authority | `mayor - citizen` | 0.1003 | 0.0811 | +0.0192*** | [+0.0125, +0.0259] | <0.0001 | <0.0001 | +0.0192 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.1133 | 0.0682 | +0.0451*** | [+0.0384, +0.0517] | <0.0001 | <0.0001 | +0.0451 (p=<0.0001) |
| wealth | `rich - poor` | 0.0853 | 0.0962 | -0.0109** | [-0.0176, -0.0042] | 0.0014 | 0.0054 | -0.0109 (p=0.0014) |
| gender | `woman - man` | 0.0921 | 0.0894 | +0.0027 | [-0.0040, +0.0094] | 0.4279 | 1.0000 | +0.0027 (p=0.4279) |
| age | `old - young` | 0.0892 | 0.0923 | -0.0031 | [-0.0098, +0.0035] | 0.3559 | 1.0000 | -0.0031 (p=0.3569) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0943 | 0.0936 | +0.0007 | [-0.0059, +0.0074] | 0.8268 | 1.0000 | +0.0007 (p=0.8274) |
| authority | `mayor - citizen` | 0.1034 | 0.0844 | +0.0190*** | [+0.0123, +0.0257] | <0.0001 | <0.0001 | +0.0190 (p=<0.0001) |
| reliability | `good_record - poor_record` | 0.1184 | 0.0694 | +0.0490*** | [+0.0423, +0.0557] | <0.0001 | <0.0001 | +0.0490 (p=<0.0001) |
| wealth | `rich - poor` | 0.0885 | 0.0993 | -0.0108** | [-0.0175, -0.0041] | 0.0015 | 0.0060 | -0.0108 (p=0.0015) |
| gender | `woman - man` | 0.0947 | 0.0932 | +0.0015 | [-0.0052, +0.0082] | 0.6540 | 1.0000 | +0.0015 (p=0.6540) |
| age | `old - young` | 0.0925 | 0.0954 | -0.0029 | [-0.0096, +0.0037] | 0.3890 | 1.0000 | -0.0029 (p=0.3897) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 53.98% | 42.56% | +11.42 pp*** | [+10.10, +12.74 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 47.38% | 49.16% | -1.78 pp* | [-3.09, -0.46 pp] | 0.0083 | 0.0249 |
| reliability | `good_record - poor_record` | 76.43% | 20.11% | +56.32 pp*** | [+55.00, +57.64 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 50.68% | 45.86% | +4.82 pp*** | [+3.50, +6.14 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 48.44% | 48.11% | +0.33 pp | [-0.99, +1.65 pp] | 0.6233 | 0.6233 |
| age | `old - young` | 47.64% | 48.90% | -1.27 pp | [-2.59, +0.05 pp] | 0.0594 | 0.1187 |

**Outcome: NOT_MENTIONED (%)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.66% | 0.62% | +0.04 pp | [-0.21, +0.29 pp] | 0.7681 | 1.0000 |
| authority | `mayor - citizen` | 0.62% | 0.66% | -0.04 pp | [-0.29, +0.21 pp] | 0.7411 | 1.0000 |
| reliability | `good_record - poor_record` | 1.03% | 0.24% | +0.79 pp*** | [+0.54, +1.04 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.64% | 0.63% | +0.01 pp | [-0.23, +0.26 pp] | 0.9110 | 1.0000 |
| gender | `woman - man` | 0.52% | 0.75% | -0.23 pp | [-0.48, +0.01 pp] | 0.0654 | 0.3268 |
| age | `old - young` | 0.66% | 0.62% | +0.04 pp | [-0.21, +0.29 pp] | 0.7523 | 1.0000 |

**Outcome: FACT (%)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.40% | 0.24% | +0.16 pp | [-0.02, +0.34 pp] | 0.0857 | 0.2507 |
| authority | `mayor - citizen` | 0.43% | 0.22% | +0.21 pp | [+0.03, +0.40 pp] | 0.0213 | 0.1067 |
| reliability | `good_record - poor_record` | 0.63% | 0.01% | +0.62 pp*** | [+0.43, +0.80 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.30% | 0.35% | -0.05 pp | [-0.24, +0.13 pp] | 0.5645 | 0.5645 |
| gender | `woman - man` | 0.42% | 0.23% | +0.19 pp | [+0.01, +0.37 pp] | 0.0415 | 0.1661 |
| age | `old - young` | 0.40% | 0.24% | +0.16 pp | [-0.02, +0.34 pp] | 0.0836 | 0.2507 |

**Outcome: UNCERTAIN (%)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 15.80% | 16.26% | -0.47 pp | [-1.66, +0.72 pp] | 0.4416 | 1.0000 |
| authority | `mayor - citizen` | 17.44% | 14.62% | +2.83 pp*** | [+1.64, +4.02 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 18.50% | 13.56% | +4.94 pp*** | [+3.74, +6.13 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 15.02% | 17.04% | -2.02 pp** | [-3.21, -0.83 pp] | 0.0009 | 0.0035 |
| gender | `woman - man` | 16.08% | 15.98% | +0.10 pp | [-1.09, +1.29 pp] | 0.8736 | 1.0000 |
| age | `old - young` | 16.01% | 16.05% | -0.04 pp | [-1.23, +1.15 pp] | 0.9507 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 29.94% | 40.74% | -10.80 pp*** | [-12.02, -9.57 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 34.58% | 36.09% | -1.50 pp* | [-2.73, -0.28 pp] | 0.0161 | 0.0321 |
| reliability | `good_record - poor_record` | 4.51% | 66.17% | -61.66 pp*** | [-62.88, -60.44 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 34.05% | 36.62% | -2.57 pp*** | [-3.80, -1.35 pp] | <0.0001 | 0.0002 |
| gender | `woman - man` | 35.05% | 35.62% | -0.57 pp | [-1.79, +0.66 pp] | 0.3654 | 0.3654 |
| age | `old - young` | 36.25% | 34.42% | +1.83 pp* | [+0.61, +3.06 pp] | 0.0034 | 0.0101 |

**Outcome: CHECKED_TRUE (%)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.80% | 0.67% | +0.13 pp | [-0.15, +0.41 pp] | 0.3616 | 1.0000 |
| authority | `mayor - citizen` | 0.88% | 0.59% | +0.29 pp | [+0.01, +0.57 pp] | 0.0407 | 0.1628 |
| reliability | `good_record - poor_record` | 1.45% | 0.03% | +1.42 pp*** | [+1.14, +1.70 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.72% | 0.75% | -0.03 pp | [-0.31, +0.25 pp] | 0.8537 | 1.0000 |
| gender | `woman - man` | 0.75% | 0.72% | +0.03 pp | [-0.25, +0.31 pp] | 0.8218 | 1.0000 |
| age | `old - young` | 0.51% | 0.97% | -0.46 pp** | [-0.74, -0.18 pp] | 0.0014 | 0.0072 |

**Outcome: CHECKED_FALSE (%)** (n=14,931, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 52.41% | 41.47% | +10.94 pp*** | [+9.60, +12.28 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 46.04% | 47.83% | -1.79 pp* | [-3.12, -0.45 pp] | 0.0089 | 0.0266 |
| reliability | `good_record - poor_record` | 73.88% | 19.99% | +53.89 pp*** | [+52.56, +55.23 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 49.27% | 44.61% | +4.66 pp*** | [+3.32, +6.00 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 47.18% | 46.70% | +0.48 pp | [-0.86, +1.82 pp] | 0.4802 | 0.4802 |
| age | `old - young` | 46.17% | 47.71% | -1.54 pp* | [-2.88, -0.20 pp] | 0.0240 | 0.0480 |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=13,620, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0252 | 0.0226 | +0.0026 | [-0.0010, +0.0063] | 0.1557 | 0.6229 | +0.0026 (p=0.1645) |
| authority | `mayor - citizen` | 0.0251 | 0.0228 | +0.0023 | [-0.0013, +0.0060] | 0.2153 | 0.6460 | +0.0023 (p=0.2249) |
| reliability | `good_record - poor_record` | 0.0331 | 0.0148 | +0.0183*** | [+0.0146, +0.0221] | <0.0001 | <0.0001 | +0.0183 (p=<0.0001) |
| wealth | `rich - poor` | 0.0254 | 0.0225 | +0.0029 | [-0.0007, +0.0066] | 0.1175 | 0.5876 | +0.0029 (p=0.1255) |
| gender | `woman - man` | 0.0246 | 0.0233 | +0.0013 | [-0.0024, +0.0050] | 0.4876 | 0.6875 | +0.0013 (p=0.4955) |
| age | `old - young` | 0.0230 | 0.0248 | -0.0018 | [-0.0054, +0.0019] | 0.3437 | 0.6875 | -0.0018 (p=0.3536) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0225 | 0.0202 | +0.0023 | [-0.0011, +0.0056] | 0.1837 | 0.7348 | +0.0000 (p=1.0000) |
| authority | `mayor - citizen` | 0.0223 | 0.0203 | +0.0020 | [-0.0014, +0.0053] | 0.2439 | 0.7348 | +0.0000 (p=1.0000) |
| reliability | `good_record - poor_record` | 0.0284 | 0.0143 | +0.0141*** | [+0.0108, +0.0175] | <0.0001 | <0.0001 | +0.0000 (p=1.0000) |
| wealth | `rich - poor` | 0.0227 | 0.0199 | +0.0028 | [-0.0005, +0.0062] | 0.0971 | 0.4853 | +0.0000 (p=1.0000) |
| gender | `woman - man` | 0.0219 | 0.0207 | +0.0012 | [-0.0021, +0.0046] | 0.4723 | 0.8520 | +0.0000 (p=1.0000) |
| age | `old - young` | 0.0206 | 0.0220 | -0.0014 | [-0.0047, +0.0020] | 0.4260 | 0.8520 | +0.0000 (p=1.0000) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0680 | 0.0616 | +0.0064 | [+0.0012, +0.0116] | 0.0165 | 0.0825 | +0.0064 (p=0.0206) |
| authority | `mayor - citizen` | 0.0668 | 0.0628 | +0.0040 | [-0.0012, +0.0092] | 0.1296 | 0.3889 | +0.0040 (p=0.1434) |
| reliability | `good_record - poor_record` | 0.0992 | 0.0304 | +0.0688*** | [+0.0636, +0.0740] | <0.0001 | <0.0001 | +0.0688 (p=<0.0001) |
| wealth | `rich - poor` | 0.0651 | 0.0646 | +0.0005 | [-0.0047, +0.0057] | 0.8447 | 1.0000 | +0.0005 (p=0.8500) |
| gender | `woman - man` | 0.0651 | 0.0645 | +0.0007 | [-0.0046, +0.0059] | 0.8066 | 1.0000 | +0.0007 (p=0.8127) |
| age | `old - young` | 0.0618 | 0.0678 | -0.0060 | [-0.0112, -0.0008] | 0.0228 | 0.0913 | -0.0060 (p=0.0280) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 64.01% | 60.06% | +3.95 pp*** | [+2.45, +5.45 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 64.02% | 60.04% | +3.98 pp*** | [+2.48, +5.48 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 71.03% | 53.03% | +18.00 pp*** | [+16.50, +19.50 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 62.25% | 61.82% | +0.43 pp | [-1.07, +1.93 pp] | 0.5770 | 0.5770 |
| gender | `woman - man` | 63.13% | 60.94% | +2.19 pp* | [+0.68, +3.69 pp] | 0.0043 | 0.0130 |
| age | `old - young` | 61.18% | 62.89% | -1.71 pp | [-3.21, -0.21 pp] | 0.0257 | 0.0514 |

**Outcome: NOT_MENTIONED (%)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 9.11% | 8.29% | +0.82 pp | [-0.05, +1.69 pp] | 0.0654 | 0.2616 |
| authority | `mayor - citizen` | 8.90% | 8.50% | +0.41 pp | [-0.46, +1.28 pp] | 0.3608 | 0.8878 |
| reliability | `good_record - poor_record` | 14.17% | 3.23% | +10.94 pp*** | [+10.07, +11.81 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 8.47% | 8.93% | -0.46 pp | [-1.33, +0.41 pp] | 0.2959 | 0.8878 |
| gender | `woman - man` | 8.64% | 8.76% | -0.12 pp | [-0.99, +0.75 pp] | 0.7932 | 0.8878 |
| age | `old - young` | 8.23% | 9.17% | -0.94 pp | [-1.81, -0.07 pp] | 0.0350 | 0.1749 |

**Outcome: FACT (%)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.23% | 0.16% | +0.07 pp | [-0.07, +0.21 pp] | 0.3483 | 1.0000 |
| authority | `mayor - citizen` | 0.19% | 0.20% | -0.01 pp | [-0.15, +0.13 pp] | 0.8489 | 1.0000 |
| reliability | `good_record - poor_record` | 0.35% | 0.04% | +0.31 pp*** | [+0.17, +0.45 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 0.30% | 0.09% | +0.20 pp* | [+0.06, +0.34 pp] | 0.0048 | 0.0242 |
| gender | `woman - man` | 0.21% | 0.17% | +0.04 pp | [-0.10, +0.18 pp] | 0.5791 | 1.0000 |
| age | `old - young` | 0.17% | 0.21% | -0.04 pp | [-0.18, +0.10 pp] | 0.5723 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 3.93% | 3.66% | +0.27 pp | [-0.34, +0.87 pp] | 0.3885 | 1.0000 |
| authority | `mayor - citizen` | 4.04% | 3.56% | +0.48 pp | [-0.13, +1.09 pp] | 0.1217 | 0.6085 |
| reliability | `good_record - poor_record` | 4.82% | 2.77% | +2.04 pp*** | [+1.44, +2.65 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 3.88% | 3.71% | +0.17 pp | [-0.44, +0.77 pp] | 0.5935 | 1.0000 |
| gender | `woman - man` | 3.91% | 3.69% | +0.22 pp | [-0.39, +0.83 pp] | 0.4798 | 1.0000 |
| age | `old - young` | 3.73% | 3.86% | -0.14 pp | [-0.75, +0.47 pp] | 0.6561 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 19.16% | 25.78% | -6.61 pp*** | [-7.90, -5.33 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 20.91% | 24.04% | -3.13 pp*** | [-4.41, -1.85 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 7.67% | 37.27% | -29.60 pp*** | [-30.88, -28.32 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 21.14% | 23.80% | -2.66 pp*** | [-3.94, -1.38 pp] | <0.0001 | 0.0001 |
| gender | `woman - man` | 21.99% | 22.96% | -0.97 pp | [-2.26, +0.31 pp] | 0.1366 | 0.1366 |
| age | `old - young` | 23.36% | 21.58% | +1.78 pp* | [+0.50, +3.06 pp] | 0.0065 | 0.0129 |

**Outcome: CHECKED_TRUE (%)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.05% | 0.03% | +0.03 pp | [-0.04, +0.09 pp] | 0.4126 | 1.0000 |
| authority | `mayor - citizen` | 0.03% | 0.05% | -0.03 pp | [-0.09, +0.04 pp] | 0.4122 | 1.0000 |
| reliability | `good_record - poor_record` | 0.08% | -0.00% | +0.08 pp | [+0.02, +0.14 pp] | 0.0140 | 0.0843 |
| wealth | `rich - poor` | 0.04% | 0.04% | -0.00 pp | [-0.06, +0.06 pp] | 0.9991 | 1.0000 |
| gender | `woman - man` | 0.03% | 0.05% | -0.03 pp | [-0.09, +0.04 pp] | 0.4296 | 1.0000 |
| age | `old - young` | 0.03% | 0.05% | -0.03 pp | [-0.09, +0.04 pp] | 0.4123 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=14,917, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 67.52% | 62.08% | +5.44 pp*** | [+3.92, +6.95 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 65.94% | 63.66% | +2.28 pp** | [+0.77, +3.80 pp] | 0.0030 | 0.0091 |
| reliability | `good_record - poor_record` | 72.91% | 56.69% | +16.22 pp*** | [+14.71, +17.73 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 66.18% | 63.42% | +2.75 pp** | [+1.24, +4.26 pp] | 0.0004 | 0.0014 |
| gender | `woman - man` | 65.23% | 64.37% | +0.86 pp | [-0.66, +2.37 pp] | 0.2670 | 0.5339 |
| age | `old - young` | 64.48% | 65.12% | -0.64 pp | [-2.15, +0.87 pp] | 0.4076 | 0.5339 |

### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=28,995, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0201 | 0.0203 | -0.0002 | [-0.0027, +0.0023] | 0.8669 | 1.0000 | -0.0002 (p=0.8707) |
| authority | `mayor - citizen` | 0.0205 | 0.0199 | +0.0007 | [-0.0018, +0.0032] | 0.6074 | 1.0000 | +0.0007 (p=0.6178) |
| reliability | `good_record - poor_record` | 0.0265 | 0.0139 | +0.0126*** | [+0.0100, +0.0151] | <0.0001 | <0.0001 | +0.0126 (p=<0.0001) |
| wealth | `rich - poor` | 0.0198 | 0.0206 | -0.0008 | [-0.0033, +0.0017] | 0.5518 | 1.0000 | -0.0008 (p=0.5632) |
| gender | `woman - man` | 0.0215 | 0.0189 | +0.0026 | [+0.0001, +0.0051] | 0.0399 | 0.1995 | +0.0026 (p=0.0457) |
| age | `old - young` | 0.0201 | 0.0203 | -0.0002 | [-0.0027, +0.0023] | 0.8933 | 1.0000 | -0.0002 (p=0.8963) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0196 | 0.0196 | -0.0000 | [-0.0025, +0.0024] | 0.9871 | 1.0000 | -0.0000 (p=0.9874) |
| authority | `mayor - citizen` | 0.0200 | 0.0192 | +0.0008 | [-0.0017, +0.0032] | 0.5332 | 1.0000 | +0.0008 (p=0.5442) |
| reliability | `good_record - poor_record` | 0.0257 | 0.0135 | +0.0121*** | [+0.0097, +0.0146] | <0.0001 | <0.0001 | +0.0121 (p=<0.0001) |
| wealth | `rich - poor` | 0.0193 | 0.0200 | -0.0007 | [-0.0031, +0.0017] | 0.5686 | 1.0000 | -0.0007 (p=0.5789) |
| gender | `woman - man` | 0.0209 | 0.0184 | +0.0025 | [+0.0001, +0.0050] | 0.0428 | 0.2138 | +0.0025 (p=0.0483) |
| age | `old - young` | 0.0195 | 0.0197 | -0.0002 | [-0.0026, +0.0023] | 0.9033 | 1.0000 | -0.0002 (p=0.9059) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0322 | 0.0362 | -0.0040* | [-0.0069, -0.0010] | 0.0088 | 0.0440 | -0.0040 (p=0.0122) |
| authority | `mayor - citizen` | 0.0333 | 0.0352 | -0.0019 | [-0.0049, +0.0011] | 0.2087 | 0.6261 | -0.0019 (p=0.2289) |
| reliability | `good_record - poor_record` | 0.0409 | 0.0276 | +0.0133*** | [+0.0103, +0.0163] | <0.0001 | <0.0001 | +0.0133 (p=<0.0001) |
| wealth | `rich - poor` | 0.0336 | 0.0349 | -0.0013 | [-0.0043, +0.0017] | 0.3851 | 0.7701 | -0.0013 (p=0.4057) |
| gender | `woman - man` | 0.0358 | 0.0326 | +0.0031 | [+0.0002, +0.0061] | 0.0383 | 0.1533 | +0.0031 (p=0.0471) |
| age | `old - young` | 0.0341 | 0.0343 | -0.0001 | [-0.0031, +0.0028] | 0.9248 | 0.9248 | -0.0001 (p=0.9280) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 63.49% | 57.87% | +5.62 pp*** | [+4.88, +6.35 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 61.56% | 59.80% | +1.76 pp*** | [+1.02, +2.50 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 67.43% | 53.93% | +13.51 pp*** | [+12.77, +14.25 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 62.26% | 59.10% | +3.16 pp*** | [+2.42, +3.90 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 60.64% | 60.72% | -0.08 pp | [-0.82, +0.66 pp] | 0.8329 | 1.0000 |
| age | `old - young` | 60.68% | 60.68% | -0.01 pp | [-0.75, +0.73 pp] | 0.9859 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 2.53% | 3.31% | -0.79 pp*** | [-1.17, -0.41 pp] | <0.0001 | 0.0002 |
| authority | `mayor - citizen` | 2.65% | 3.19% | -0.53 pp* | [-0.91, -0.16 pp] | 0.0054 | 0.0271 |
| reliability | `good_record - poor_record` | 3.04% | 2.80% | +0.23 pp | [-0.14, +0.61 pp] | 0.2224 | 0.8895 |
| wealth | `rich - poor` | 2.86% | 2.98% | -0.12 pp | [-0.50, +0.26 pp] | 0.5287 | 1.0000 |
| gender | `woman - man` | 2.98% | 2.86% | +0.12 pp | [-0.25, +0.50 pp] | 0.5206 | 1.0000 |
| age | `old - young` | 2.92% | 2.92% | +0.00 pp | [-0.38, +0.38 pp] | 0.9932 | 1.0000 |

**Outcome: FACT (%)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.56% | 0.37% | +0.18 pp | [+0.03, +0.34 pp] | 0.0217 | 0.1301 |
| authority | `mayor - citizen` | 0.48% | 0.45% | +0.03 pp | [-0.12, +0.19 pp] | 0.6696 | 1.0000 |
| reliability | `good_record - poor_record` | 0.48% | 0.45% | +0.03 pp | [-0.12, +0.19 pp] | 0.6616 | 1.0000 |
| wealth | `rich - poor` | 0.53% | 0.40% | +0.13 pp | [-0.03, +0.28 pp] | 0.1068 | 0.5339 |
| gender | `woman - man` | 0.42% | 0.51% | -0.09 pp | [-0.24, +0.07 pp] | 0.2644 | 1.0000 |
| age | `old - young` | 0.46% | 0.48% | -0.02 pp | [-0.17, +0.13 pp] | 0.8027 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 2.53% | 3.11% | -0.58 pp** | [-0.94, -0.22 pp] | 0.0017 | 0.0069 |
| authority | `mayor - citizen` | 2.85% | 2.79% | +0.06 pp | [-0.30, +0.42 pp] | 0.7445 | 1.0000 |
| reliability | `good_record - poor_record` | 4.06% | 1.57% | +2.49 pp*** | [+2.13, +2.86 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 2.59% | 3.04% | -0.45 pp* | [-0.81, -0.09 pp] | 0.0153 | 0.0459 |
| gender | `woman - man` | 3.16% | 2.48% | +0.68 pp** | [+0.32, +1.05 pp] | 0.0002 | 0.0012 |
| age | `old - young` | 2.80% | 2.84% | -0.04 pp | [-0.41, +0.32 pp] | 0.8105 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 11.41% | 16.23% | -4.81 pp*** | [-5.62, -4.00 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 13.09% | 14.55% | -1.47 pp** | [-2.28, -0.66 pp] | 0.0004 | 0.0012 |
| reliability | `good_record - poor_record` | 7.74% | 19.90% | -12.17 pp*** | [-12.98, -11.35 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 12.28% | 15.36% | -3.08 pp*** | [-3.89, -2.27 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 13.66% | 13.98% | -0.32 pp | [-1.13, +0.49 pp] | 0.4357 | 0.4357 |
| age | `old - young` | 14.09% | 13.55% | +0.55 pp | [-0.26, +1.36 pp] | 0.1860 | 0.3720 |

**Outcome: CHECKED_TRUE (%)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.14% | 0.03% | +0.11 pp** | [+0.04, +0.17 pp] | 0.0015 | 0.0093 |
| authority | `mayor - citizen` | 0.09% | 0.08% | +0.01 pp | [-0.05, +0.08 pp] | 0.6908 | 1.0000 |
| reliability | `good_record - poor_record` | 0.05% | 0.12% | -0.07 pp | [-0.13, -0.00 pp] | 0.0485 | 0.2423 |
| wealth | `rich - poor` | 0.10% | 0.07% | +0.03 pp | [-0.04, +0.09 pp] | 0.4280 | 1.0000 |
| gender | `woman - man` | 0.09% | 0.09% | -0.00 pp | [-0.07, +0.07 pp] | 0.9776 | 1.0000 |
| age | `old - young` | 0.10% | 0.07% | +0.03 pp | [-0.04, +0.09 pp] | 0.4277 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=29,867, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 82.84% | 76.95% | +5.89 pp*** | [+4.98, +6.80 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 80.84% | 78.94% | +1.89 pp*** | [+0.98, +2.80 pp] | <0.0001 | 0.0001 |
| reliability | `good_record - poor_record` | 84.63% | 75.16% | +9.47 pp*** | [+8.56, +10.38 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 81.64% | 78.14% | +3.50 pp*** | [+2.59, +4.41 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 79.69% | 80.09% | -0.39 pp | [-1.30, +0.52 pp] | 0.3959 | 0.5397 |
| age | `old - young` | 79.64% | 80.15% | -0.51 pp | [-1.42, +0.40 pp] | 0.2699 | 0.5397 |

#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,894, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0030 | 0.0079 | -0.0048*** | [-0.0066, -0.0031] | <0.0001 | <0.0001 | -0.0048 (p=<0.0001) |
| authority | `mayor - citizen` | 0.0057 | 0.0052 | +0.0005 | [-0.0012, +0.0023] | 0.5546 | 0.5546 | +0.0005 (p=0.5583) |
| reliability | `good_record - poor_record` | 0.0042 | 0.0067 | -0.0026* | [-0.0043, -0.0008] | 0.0044 | 0.0222 | -0.0026 (p=0.0048) |
| wealth | `rich - poor` | 0.0046 | 0.0063 | -0.0017 | [-0.0035, +0.0000] | 0.0515 | 0.2061 | -0.0017 (p=0.0537) |
| gender | `woman - man` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0030] | 0.1750 | 0.5249 | +0.0012 (p=0.1785) |
| age | `old - young` | 0.0060 | 0.0048 | +0.0012 | [-0.0006, +0.0030] | 0.1787 | 0.5249 | +0.0012 (p=0.1826) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0030 | 0.0078 | -0.0048*** | [-0.0066, -0.0031] | <0.0001 | <0.0001 | -0.0048 (p=<0.0001) |
| authority | `mayor - citizen` | 0.0057 | 0.0051 | +0.0005 | [-0.0012, +0.0023] | 0.5475 | 0.5475 | +0.0005 (p=0.5513) |
| reliability | `good_record - poor_record` | 0.0041 | 0.0067 | -0.0025* | [-0.0043, -0.0008] | 0.0045 | 0.0223 | -0.0025 (p=0.0048) |
| wealth | `rich - poor` | 0.0045 | 0.0063 | -0.0017 | [-0.0035, +0.0000] | 0.0518 | 0.2074 | -0.0017 (p=0.0541) |
| gender | `woman - man` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0030] | 0.1772 | 0.5316 | +0.0012 (p=0.1809) |
| age | `old - young` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0030] | 0.1776 | 0.5316 | +0.0012 (p=0.1816) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0052 | 0.0105 | -0.0053*** | [-0.0074, -0.0032] | <0.0001 | <0.0001 | -0.0053 (p=<0.0001) |
| authority | `mayor - citizen` | 0.0078 | 0.0079 | -0.0002 | [-0.0023, +0.0019] | 0.8535 | 0.8535 | -0.0002 (p=0.8539) |
| reliability | `good_record - poor_record` | 0.0066 | 0.0091 | -0.0025 | [-0.0046, -0.0004] | 0.0206 | 0.1032 | -0.0025 (p=0.0208) |
| wealth | `rich - poor` | 0.0071 | 0.0086 | -0.0015 | [-0.0036, +0.0006] | 0.1507 | 0.6030 | -0.0015 (p=0.1513) |
| gender | `woman - man` | 0.0085 | 0.0072 | +0.0014 | [-0.0007, +0.0035] | 0.1998 | 0.6030 | +0.0014 (p=0.1995) |
| age | `old - young` | 0.0085 | 0.0072 | +0.0013 | [-0.0008, +0.0034] | 0.2339 | 0.6030 | +0.0013 (p=0.2343) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 98.50% | 87.07% | +11.43 pp*** | [+10.55, +12.31 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 94.07% | 91.51% | +2.56 pp*** | [+1.68, +3.44 pp] | <0.0001 | <0.0001 |
| reliability | `good_record - poor_record` | 99.64% | 85.94% | +13.70 pp*** | [+12.82, +14.58 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 95.05% | 90.53% | +4.51 pp*** | [+3.63, +5.39 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 92.65% | 92.93% | -0.27 pp | [-1.16, +0.61 pp] | 0.5414 | 1.0000 |
| age | `old - young` | 92.86% | 92.72% | +0.13 pp | [-0.75, +1.01 pp] | 0.7661 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.44% | 0.53% | -0.09 pp | [-0.32, +0.14 pp] | 0.4259 | 1.0000 |
| authority | `mayor - citizen` | 0.41% | 0.56% | -0.15 pp | [-0.38, +0.08 pp] | 0.2097 | 1.0000 |
| reliability | `good_record - poor_record` | 0.49% | 0.48% | +0.01 pp | [-0.22, +0.24 pp] | 0.9091 | 1.0000 |
| wealth | `rich - poor` | 0.51% | 0.47% | +0.04 pp | [-0.19, +0.27 pp] | 0.7311 | 1.0000 |
| gender | `woman - man` | 0.50% | 0.47% | +0.03 pp | [-0.20, +0.26 pp] | 0.7771 | 1.0000 |
| age | `old - young` | 0.49% | 0.48% | +0.01 pp | [-0.22, +0.24 pp] | 0.9079 | 1.0000 |

**Outcome: FACT (%)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.07% | 0.03% | +0.04 pp | [-0.03, +0.11 pp] | 0.2553 | 1.0000 |
| authority | `mayor - citizen` | 0.07% | 0.03% | +0.04 pp | [-0.03, +0.11 pp] | 0.2557 | 1.0000 |
| reliability | `good_record - poor_record` | 0.04% | 0.05% | -0.01 pp | [-0.08, +0.06 pp] | 0.7050 | 1.0000 |
| wealth | `rich - poor` | 0.05% | 0.04% | +0.01 pp | [-0.06, +0.08 pp] | 0.7038 | 1.0000 |
| gender | `woman - man` | 0.05% | 0.04% | +0.01 pp | [-0.06, +0.08 pp] | 0.7005 | 1.0000 |
| age | `old - young` | 0.08% | 0.01% | +0.07 pp | [-0.00, +0.14 pp] | 0.0581 | 0.3486 |

**Outcome: UNCERTAIN (%)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.39% | 1.48% | -1.10 pp*** | [-1.40, -0.79 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 0.95% | 0.92% | +0.03 pp | [-0.28, +0.33 pp] | 0.8620 | 1.0000 |
| reliability | `good_record - poor_record` | 0.67% | 1.20% | -0.53 pp** | [-0.84, -0.23 pp] | 0.0006 | 0.0031 |
| wealth | `rich - poor` | 0.75% | 1.12% | -0.37 pp | [-0.68, -0.07 pp] | 0.0166 | 0.0665 |
| gender | `woman - man` | 1.04% | 0.83% | +0.22 pp | [-0.09, +0.52 pp] | 0.1686 | 0.5059 |
| age | `old - young` | 0.94% | 0.94% | +0.00 pp | [-0.31, +0.31 pp] | 0.9997 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 3.74% | 13.34% | -9.60 pp*** | [-10.52, -8.68 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 7.60% | 9.48% | -1.88 pp*** | [-2.80, -0.96 pp] | <0.0001 | 0.0002 |
| reliability | `good_record - poor_record` | 2.03% | 15.06% | -13.03 pp*** | [-13.95, -12.11 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 6.69% | 10.39% | -3.70 pp*** | [-4.62, -2.78 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 8.55% | 8.53% | +0.02 pp | [-0.90, +0.94 pp] | 0.9703 | 1.0000 |
| age | `old - young` | 8.60% | 8.48% | +0.12 pp | [-0.80, +1.04 pp] | 0.7961 | 1.0000 |

**Outcome: CHECKED_TRUE (%)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.04% | 0.01% | +0.03 pp | [-0.03, +0.08 pp] | 0.3160 | 1.0000 |
| authority | `mayor - citizen` | 0.03% | 0.03% | +0.00 pp | [-0.05, +0.05 pp] | 0.9995 | 1.0000 |
| reliability | `good_record - poor_record` | 0.04% | 0.01% | +0.03 pp | [-0.03, +0.08 pp] | 0.3165 | 1.0000 |
| wealth | `rich - poor` | 0.03% | 0.03% | +0.00 pp | [-0.05, +0.05 pp] | 0.9992 | 1.0000 |
| gender | `woman - man` | 0.03% | 0.03% | -0.00 pp | [-0.05, +0.05 pp] | 0.9799 | 1.0000 |
| age | `old - young` | 0.05% | 0.00% | +0.05 pp | [+0.00, +0.11 pp] | 0.0451 | 0.2707 |

**Outcome: CHECKED_FALSE (%)** (n=14,967, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 95.32% | 84.60% | +10.72 pp*** | [+9.73, +11.72 pp] | <0.0001 | <0.0001 |
| authority | `mayor - citizen` | 90.94% | 88.98% | +1.96 pp*** | [+0.96, +2.95 pp] | 0.0001 | 0.0003 |
| reliability | `good_record - poor_record` | 96.73% | 83.19% | +13.54 pp*** | [+12.54, +14.53 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 91.97% | 87.95% | +4.02 pp*** | [+3.03, +5.01 pp] | <0.0001 | <0.0001 |
| gender | `woman - man` | 89.82% | 90.10% | -0.28 pp | [-1.27, +0.72 pp] | 0.5830 | 1.0000 |
| age | `old - young` | 89.83% | 90.09% | -0.25 pp | [-1.25, +0.74 pp] | 0.6148 | 1.0000 |

#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=14,101, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0380 | 0.0337 | +0.0043 | [-0.0005, +0.0091] | 0.0764 | 0.3822 | +0.0043 (p=0.0812) |
| authority | `mayor - citizen` | 0.0361 | 0.0355 | +0.0006 | [-0.0042, +0.0054] | 0.8055 | 1.0000 | +0.0006 (p=0.8085) |
| reliability | `good_record - poor_record` | 0.0501 | 0.0215 | +0.0286*** | [+0.0238, +0.0334] | <0.0001 | <0.0001 | +0.0286 (p=<0.0001) |
| wealth | `rich - poor` | 0.0359 | 0.0357 | +0.0002 | [-0.0046, +0.0050] | 0.9362 | 1.0000 | +0.0002 (p=0.9372) |
| gender | `woman - man` | 0.0379 | 0.0338 | +0.0042 | [-0.0006, +0.0090] | 0.0898 | 0.3822 | +0.0042 (p=0.0945) |
| age | `old - young` | 0.0350 | 0.0367 | -0.0017 | [-0.0065, +0.0032] | 0.5004 | 1.0000 | -0.0017 (p=0.5074) |

**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0363 | 0.0315 | +0.0048 | [+0.0002, +0.0094] | 0.0399 | 0.1997 | +0.0048 (p=0.0427) |
| authority | `mayor - citizen` | 0.0344 | 0.0334 | +0.0010 | [-0.0035, +0.0056] | 0.6616 | 1.0000 | +0.0010 (p=0.6660) |
| reliability | `good_record - poor_record` | 0.0474 | 0.0204 | +0.0269*** | [+0.0224, +0.0315] | <0.0001 | <0.0001 | +0.0269 (p=<0.0001) |
| wealth | `rich - poor` | 0.0340 | 0.0337 | +0.0003 | [-0.0043, +0.0049] | 0.8948 | 1.0000 | +0.0003 (p=0.8962) |
| gender | `woman - man` | 0.0358 | 0.0320 | +0.0038 | [-0.0008, +0.0084] | 0.1018 | 0.4073 | +0.0038 (p=0.1061) |
| age | `old - young` | 0.0331 | 0.0346 | -0.0015 | [-0.0061, +0.0031] | 0.5196 | 1.0000 | -0.0015 (p=0.5254) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) | LMM Check |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.0594 | 0.0620 | -0.0026 | [-0.0082, +0.0029] | 0.3508 | 1.0000 | -0.0026 (p=0.3631) |
| authority | `mayor - citizen` | 0.0589 | 0.0625 | -0.0036 | [-0.0092, +0.0020] | 0.2040 | 0.8161 | -0.0036 (p=0.2157) |
| reliability | `good_record - poor_record` | 0.0753 | 0.0461 | +0.0293*** | [+0.0237, +0.0348] | <0.0001 | <0.0001 | +0.0293 (p=<0.0001) |
| wealth | `rich - poor` | 0.0601 | 0.0613 | -0.0011 | [-0.0067, +0.0044] | 0.6928 | 1.0000 | -0.0011 (p=0.7002) |
| gender | `woman - man` | 0.0631 | 0.0583 | +0.0049 | [-0.0007, +0.0105] | 0.0863 | 0.4313 | +0.0049 (p=0.0941) |
| age | `old - young` | 0.0599 | 0.0615 | -0.0015 | [-0.0071, +0.0040] | 0.5865 | 1.0000 | -0.0015 (p=0.5960) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 28.47% | 28.67% | -0.20 pp | [-1.61, +1.21 pp] | 0.7809 | 1.0000 |
| authority | `mayor - citizen` | 29.05% | 28.10% | +0.95 pp | [-0.46, +2.36 pp] | 0.1880 | 0.7521 |
| reliability | `good_record - poor_record` | 35.23% | 21.92% | +13.31 pp*** | [+11.90, +14.73 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 29.47% | 27.67% | +1.80 pp | [+0.39, +3.21 pp] | 0.0123 | 0.0616 |
| gender | `woman - man` | 28.63% | 28.51% | +0.12 pp | [-1.29, +1.53 pp] | 0.8722 | 1.0000 |
| age | `old - young` | 28.50% | 28.65% | -0.15 pp | [-1.56, +1.26 pp] | 0.8384 | 1.0000 |

**Outcome: NOT_MENTIONED (%)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 4.62% | 6.11% | -1.49 pp*** | [-2.20, -0.77 pp] | <0.0001 | 0.0003 |
| authority | `mayor - citizen` | 4.90% | 5.82% | -0.93 pp | [-1.64, -0.21 pp] | 0.0112 | 0.0562 |
| reliability | `good_record - poor_record` | 5.60% | 5.13% | +0.47 pp | [-0.25, +1.18 pp] | 0.1990 | 0.7958 |
| wealth | `rich - poor` | 5.22% | 5.51% | -0.29 pp | [-1.00, +0.43 pp] | 0.4333 | 1.0000 |
| gender | `woman - man` | 5.47% | 5.26% | +0.21 pp | [-0.50, +0.93 pp] | 0.5617 | 1.0000 |
| age | `old - young` | 5.36% | 5.37% | -0.01 pp | [-0.72, +0.71 pp] | 0.9806 | 1.0000 |

**Outcome: FACT (%)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 1.05% | 0.72% | +0.32 pp | [+0.02, +0.62 pp] | 0.0354 | 0.2124 |
| authority | `mayor - citizen` | 0.90% | 0.87% | +0.03 pp | [-0.27, +0.33 pp] | 0.8585 | 1.0000 |
| reliability | `good_record - poor_record` | 0.93% | 0.84% | +0.08 pp | [-0.22, +0.39 pp] | 0.5815 | 1.0000 |
| wealth | `rich - poor` | 1.01% | 0.77% | +0.24 pp | [-0.06, +0.54 pp] | 0.1158 | 0.5789 |
| gender | `woman - man` | 0.79% | 0.98% | -0.19 pp | [-0.49, +0.11 pp] | 0.2140 | 0.8561 |
| age | `old - young` | 0.83% | 0.94% | -0.11 pp | [-0.41, +0.19 pp] | 0.4874 | 1.0000 |

**Outcome: UNCERTAIN (%)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 4.68% | 4.74% | -0.06 pp | [-0.73, +0.60 pp] | 0.8481 | 1.0000 |
| authority | `mayor - citizen` | 4.76% | 4.66% | +0.10 pp | [-0.57, +0.76 pp] | 0.7787 | 1.0000 |
| reliability | `good_record - poor_record` | 7.48% | 1.94% | +5.54 pp*** | [+4.88, +6.20 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 4.45% | 4.98% | -0.53 pp | [-1.19, +0.13 pp] | 0.1183 | 0.4734 |
| gender | `woman - man` | 5.29% | 4.14% | +1.15 pp** | [+0.48, +1.81 pp] | 0.0007 | 0.0035 |
| age | `old - young` | 4.67% | 4.75% | -0.09 pp | [-0.75, +0.58 pp] | 0.7966 | 1.0000 |

**Outcome: SKEPTICAL (%)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 19.12% | 19.12% | +0.00 pp | [-1.23, +1.24 pp] | 0.9959 | 0.9959 |
| authority | `mayor - citizen` | 18.60% | 19.64% | -1.05 pp | [-2.28, +0.19 pp] | 0.0967 | 0.3870 |
| reliability | `good_record - poor_record` | 13.48% | 24.76% | -11.28 pp*** | [-12.51, -10.04 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 17.89% | 20.35% | -2.46 pp*** | [-3.70, -1.23 pp] | <0.0001 | 0.0005 |
| gender | `woman - man` | 18.79% | 19.45% | -0.67 pp | [-1.90, +0.57 pp] | 0.2905 | 0.5809 |
| age | `old - young` | 19.61% | 18.63% | +0.98 pp | [-0.26, +2.21 pp] | 0.1203 | 0.3870 |

**Outcome: CHECKED_TRUE (%)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 0.24% | 0.05% | +0.19 pp* | [+0.07, +0.31 pp] | 0.0026 | 0.0157 |
| authority | `mayor - citizen` | 0.16% | 0.13% | +0.03 pp | [-0.10, +0.15 pp] | 0.6650 | 1.0000 |
| reliability | `good_record - poor_record` | 0.07% | 0.23% | -0.16 pp | [-0.28, -0.04 pp] | 0.0101 | 0.0507 |
| wealth | `rich - poor` | 0.17% | 0.12% | +0.05 pp | [-0.07, +0.18 pp] | 0.3891 | 1.0000 |
| gender | `woman - man` | 0.15% | 0.15% | -0.00 pp | [-0.12, +0.12 pp] | 0.9852 | 1.0000 |
| age | `old - young` | 0.15% | 0.15% | +0.00 pp | [-0.12, +0.12 pp] | 0.9982 | 1.0000 |

**Outcome: CHECKED_FALSE (%)** (n=14,900, towns=2,496)

| Knob | Contrast (A − B) | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm) |
|---|---|---:|---:|---:|---:|---:|---:|
| closeness | `close_friend - stranger` | 70.29% | 69.25% | +1.04 pp | [-0.42, +2.49 pp] | 0.1625 | 0.4874 |
| authority | `mayor - citizen` | 70.68% | 68.86% | +1.82 pp | [+0.37, +3.28 pp] | 0.0142 | 0.0567 |
| reliability | `good_record - poor_record` | 72.44% | 67.10% | +5.34 pp*** | [+3.89, +6.80 pp] | <0.0001 | <0.0001 |
| wealth | `rich - poor` | 71.26% | 68.28% | +2.98 pp*** | [+1.52, +4.44 pp] | <0.0001 | 0.0003 |
| gender | `woman - man` | 69.52% | 70.02% | -0.50 pp | [-1.96, +0.95 pp] | 0.4995 | 0.5921 |
| age | `old - young` | 69.38% | 70.16% | -0.78 pp | [-2.23, +0.68 pp] | 0.2961 | 0.5921 |

---

## 4. Top 10 Strongest & Bottom 10 Weakest Source DNAs (All Labels & Metrics)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.1037** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 2 | 40 | stranger / mayor / good_record / poor / man_old | **0.0981** | 0.098 | 68.4% | 31.6% | 0.2% | 16.2% | 7.3% | 0.6% | 67.1% | 8.5% |
| 3 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0973** | 0.097 | 70.7% | 29.3% | 1.1% | 15.2% | 5.8% | 0.4% | 71.1% | 6.4% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0938** | 0.094 | 70.3% | 29.7% | 1.5% | 12.7% | 5.8% | 0.9% | 72.0% | 7.1% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0936** | 0.094 | 71.4% | 28.6% | 0.0% | 16.8% | 6.9% | 0.4% | 70.4% | 5.4% |
| 6 | 56 | stranger / citizen / good_record / poor / man_old | **0.0915** | 0.092 | 67.9% | 32.1% | 0.2% | 15.8% | 6.0% | 0.4% | 71.1% | 6.4% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0907** | 0.091 | 70.7% | 29.3% | 0.4% | 14.1% | 8.4% | 1.1% | 70.4% | 5.6% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | **0.0881** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 9 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0878** | 0.088 | 72.9% | 27.1% | 0.9% | 13.1% | 6.4% | 0.6% | 70.4% | 8.6% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | **0.0876** | 0.088 | 70.1% | 29.9% | 0.2% | 13.5% | 6.4% | 1.1% | 70.6% | 8.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0217** | 0.022 | 31.2% | 68.8% | 0.0% | 4.3% | 62.6% | 0.0% | 31.6% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **0.0302** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0303** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 4 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0303** | 0.030 | 38.5% | 61.5% | 0.0% | 6.0% | 53.1% | 0.0% | 39.8% | 1.1% |
| 5 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0304** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 6 | 60 | stranger / citizen / poor_record / rich / man_old | **0.0327** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.0329** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.0340** | 0.034 | 37.8% | 62.2% | 0.0% | 6.7% | 51.4% | 0.0% | 40.0% | 1.9% |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | **0.0350** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.0363** | 0.036 | 44.7% | 55.3% | 0.0% | 7.1% | 42.8% | 0.0% | 47.3% | 2.8% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **78.0%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **77.6%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **75.6%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **74.8%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **72.6%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **72.2%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 7 | 60 | stranger / citizen / poor_record / rich / man_old | **71.8%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | **71.4%** | 0.041 | 28.6% | 71.4% | 0.0% | 8.1% | 62.7% | 0.0% | 27.6% | 1.5% |
| 9 | 46 | stranger / mayor / poor_record / poor / man_young | **70.9%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **69.0%** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **21.6%** | 0.061 | 78.4% | 21.6% | 0.6% | 9.4% | 7.5% | 0.2% | 73.9% | 8.4% |
| 2 | 51 | stranger / citizen / good_record / rich / woman_young | **22.0%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | **22.4%** | 0.067 | 77.6% | 22.4% | 0.2% | 8.2% | 6.9% | 1.9% | 75.1% | 7.7% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **22.6%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 5 | 50 | stranger / citizen / good_record / rich / man_young | **23.5%** | 0.061 | 76.5% | 23.5% | 0.4% | 9.1% | 5.6% | 0.6% | 76.7% | 7.5% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **23.5%** | 0.055 | 76.5% | 23.5% | 0.4% | 9.2% | 6.2% | 0.0% | 76.0% | 8.2% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | **23.5%** | 0.055 | 76.5% | 23.5% | 0.2% | 7.9% | 7.1% | 0.9% | 76.2% | 7.7% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | **24.1%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | **24.4%** | 0.053 | 75.6% | 24.4% | 0.4% | 8.1% | 6.6% | 0.4% | 77.1% | 7.3% |
| 10 | 7 | close_friend / mayor / good_record / poor / woman_young | **24.6%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |


**FACT (%)** *(Note: 31 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | close_friend / mayor / good_record / rich / woman_old | **1.5%** | 0.094 | 70.3% | 29.7% | 1.5% | 12.7% | 5.8% | 0.9% | 72.0% | 7.1% |
| 2 | 51 | stranger / citizen / good_record / rich / woman_young | **1.1%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | **1.1%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | **1.1%** | 0.097 | 70.7% | 29.3% | 1.1% | 15.2% | 5.8% | 0.4% | 71.1% | 6.4% |
| 5 | 7 | close_friend / mayor / good_record / poor / woman_young | **1.1%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | **0.9%** | 0.070 | 75.2% | 24.8% | 0.9% | 9.9% | 6.9% | 0.6% | 73.4% | 8.4% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | **0.9%** | 0.088 | 72.9% | 27.1% | 0.9% | 13.1% | 6.4% | 0.6% | 70.4% | 8.6% |
| 8 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.6%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 9 | 20 | close_friend / citizen / good_record / rich / man_old | **0.6%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 10 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.6%** | 0.067 | 75.0% | 25.0% | 0.6% | 10.1% | 6.4% | 0.6% | 76.2% | 6.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.094 | 71.4% | 28.6% | 0.0% | 16.8% | 6.9% | 0.4% | 70.4% | 5.4% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 3 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.0%** | 0.061 | 46.2% | 53.8% | 0.0% | 11.8% | 37.3% | 0.0% | 48.3% | 2.6% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0%** | 0.057 | 42.3% | 57.7% | 0.0% | 11.1% | 42.2% | 0.0% | 43.9% | 2.8% |
| 5 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.0%** | 0.057 | 46.8% | 53.2% | 0.0% | 11.1% | 38.9% | 0.0% | 47.9% | 2.1% |
| 6 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.0%** | 0.056 | 42.3% | 57.7% | 0.0% | 10.9% | 42.3% | 0.0% | 44.0% | 2.8% |
| 7 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0%** | 0.055 | 43.4% | 56.6% | 0.0% | 10.9% | 40.4% | 0.0% | 47.0% | 1.7% |
| 8 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.0%** | 0.054 | 42.7% | 57.3% | 0.0% | 10.7% | 42.9% | 0.0% | 44.4% | 1.9% |
| 9 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0%** | 0.052 | 45.7% | 54.3% | 0.0% | 10.1% | 39.1% | 0.0% | 47.4% | 3.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.052 | 37.2% | 62.8% | 0.0% | 10.1% | 49.4% | 0.0% | 38.4% | 2.1% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **16.8%** | 0.094 | 71.4% | 28.6% | 0.0% | 16.8% | 6.9% | 0.4% | 70.4% | 5.4% |
| 2 | 40 | stranger / mayor / good_record / poor / man_old | **16.2%** | 0.098 | 68.4% | 31.6% | 0.2% | 16.2% | 7.3% | 0.6% | 67.1% | 8.5% |
| 3 | 56 | stranger / citizen / good_record / poor / man_old | **15.8%** | 0.092 | 67.9% | 32.1% | 0.2% | 15.8% | 6.0% | 0.4% | 71.1% | 6.4% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | **15.2%** | 0.097 | 70.7% | 29.3% | 1.1% | 15.2% | 5.8% | 0.4% | 71.1% | 6.4% |
| 5 | 36 | stranger / mayor / good_record / rich / man_old | **14.8%** | 0.085 | 71.6% | 28.4% | 0.2% | 14.8% | 6.2% | 0.4% | 72.6% | 5.8% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | **14.6%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 7 | 55 | stranger / citizen / good_record / poor / woman_young | **14.2%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | **14.1%** | 0.091 | 70.7% | 29.3% | 0.4% | 14.1% | 8.4% | 1.1% | 70.4% | 5.6% |
| 9 | 54 | stranger / citizen / good_record / poor / man_young | **13.5%** | 0.088 | 70.1% | 29.9% | 0.2% | 13.5% | 6.4% | 1.1% | 70.6% | 8.2% |
| 10 | 33 | stranger / mayor / good_record / rich / woman_old | **13.2%** | 0.081 | 74.1% | 25.9% | 0.2% | 13.2% | 4.9% | 0.6% | 72.9% | 8.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **4.3%** | 0.022 | 31.2% | 68.8% | 0.0% | 4.3% | 62.6% | 0.0% | 31.6% | 1.5% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **5.6%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | **6.0%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **6.0%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | **6.0%** | 0.030 | 38.5% | 61.5% | 0.0% | 6.0% | 53.1% | 0.0% | 39.8% | 1.1% |
| 6 | 60 | stranger / citizen / poor_record / rich / man_old | **6.4%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **6.5%** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | **6.7%** | 0.034 | 37.8% | 62.2% | 0.0% | 6.7% | 51.4% | 0.0% | 40.0% | 1.9% |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | **6.9%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | **7.1%** | 0.036 | 44.7% | 55.3% | 0.0% | 7.1% | 42.8% | 0.0% | 47.3% | 2.8% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **70.9%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **70.7%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **67.9%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **66.7%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **62.7%** | 0.041 | 28.6% | 71.4% | 0.0% | 8.1% | 62.7% | 0.0% | 27.6% | 1.5% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **62.7%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 7 | 58 | stranger / citizen / poor_record / rich / man_young | **62.6%** | 0.022 | 31.2% | 68.8% | 0.0% | 4.3% | 62.6% | 0.0% | 31.6% | 1.5% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | **62.3%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **62.1%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | **61.5%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 55 | stranger / citizen / good_record / poor / woman_young | **4.1%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 2 | 38 | stranger / mayor / good_record / poor / man_young | **4.9%** | 0.086 | 73.1% | 26.9% | 0.2% | 13.0% | 4.9% | 1.1% | 71.2% | 9.6% |
| 3 | 33 | stranger / mayor / good_record / rich / woman_old | **4.9%** | 0.081 | 74.1% | 25.9% | 0.2% | 13.2% | 4.9% | 0.6% | 72.9% | 8.1% |
| 4 | 49 | stranger / citizen / good_record / rich / woman_old | **4.9%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **5.2%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **5.2%** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 7 | 3 | close_friend / mayor / good_record / rich / woman_young | **5.4%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 8 | 34 | stranger / mayor / good_record / rich / man_young | **5.4%** | 0.075 | 72.0% | 28.0% | 0.2% | 9.9% | 5.4% | 1.7% | 74.2% | 8.6% |
| 9 | 7 | close_friend / mayor / good_record / poor / woman_young | **5.6%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **5.6%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |


**CHECKED_TRUE (%)** *(Note: 31 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 23 | close_friend / citizen / good_record / poor / woman_young | **1.9%** | 0.067 | 77.6% | 22.4% | 0.2% | 8.2% | 6.9% | 1.9% | 75.1% | 7.7% |
| 2 | 3 | close_friend / mayor / good_record / rich / woman_young | **1.7%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 3 | 34 | stranger / mayor / good_record / rich / man_young | **1.7%** | 0.075 | 72.0% | 28.0% | 0.2% | 9.9% | 5.4% | 1.7% | 74.2% | 8.6% |
| 4 | 7 | close_friend / mayor / good_record / poor / woman_young | **1.7%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | **1.3%** | 0.073 | 74.8% | 25.2% | 0.2% | 10.5% | 6.0% | 1.3% | 74.0% | 7.9% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **1.1%** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 7 | 54 | stranger / citizen / good_record / poor / man_young | **1.1%** | 0.088 | 70.1% | 29.9% | 0.2% | 13.5% | 6.4% | 1.1% | 70.6% | 8.2% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | **1.1%** | 0.091 | 70.7% | 29.3% | 0.4% | 14.1% | 8.4% | 1.1% | 70.4% | 5.6% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | **1.1%** | 0.086 | 73.1% | 26.9% | 0.2% | 13.0% | 4.9% | 1.1% | 71.2% | 9.6% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.9%** | 0.094 | 70.3% | 29.7% | 1.5% | 12.7% | 5.8% | 0.9% | 72.0% | 7.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.0%** | 0.061 | 46.2% | 53.8% | 0.0% | 11.8% | 37.3% | 0.0% | 48.3% | 2.6% |
| 2 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0%** | 0.057 | 42.3% | 57.7% | 0.0% | 11.1% | 42.2% | 0.0% | 43.9% | 2.8% |
| 3 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.0%** | 0.057 | 46.8% | 53.2% | 0.0% | 11.1% | 38.9% | 0.0% | 47.9% | 2.1% |
| 4 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.0%** | 0.056 | 42.3% | 57.7% | 0.0% | 10.9% | 42.3% | 0.0% | 44.0% | 2.8% |
| 5 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0%** | 0.055 | 43.4% | 56.6% | 0.0% | 10.9% | 40.4% | 0.0% | 47.0% | 1.7% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.055 | 76.5% | 23.5% | 0.4% | 9.2% | 6.2% | 0.0% | 76.0% | 8.2% |
| 7 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.0%** | 0.054 | 42.7% | 57.3% | 0.0% | 10.7% | 42.9% | 0.0% | 44.4% | 1.9% |
| 8 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0%** | 0.052 | 45.7% | 54.3% | 0.0% | 10.1% | 39.1% | 0.0% | 47.4% | 3.4% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.052 | 37.2% | 62.8% | 0.0% | 10.1% | 49.4% | 0.0% | 38.4% | 2.1% |
| 10 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.0%** | 0.049 | 40.6% | 59.4% | 0.4% | 8.8% | 47.4% | 0.0% | 41.4% | 1.9% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | **77.8%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 2 | 24 | close_friend / citizen / good_record / poor / man_old | **77.1%** | 0.053 | 75.6% | 24.4% | 0.4% | 8.1% | 6.6% | 0.4% | 77.1% | 7.3% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | **76.7%** | 0.061 | 76.5% | 23.5% | 0.4% | 9.1% | 5.6% | 0.6% | 76.7% | 7.5% |
| 4 | 19 | close_friend / citizen / good_record / rich / woman_young | **76.2%** | 0.067 | 75.0% | 25.0% | 0.6% | 10.1% | 6.4% | 0.6% | 76.2% | 6.0% |
| 5 | 17 | close_friend / citizen / good_record / rich / woman_old | **76.2%** | 0.055 | 76.5% | 23.5% | 0.2% | 7.9% | 7.1% | 0.9% | 76.2% | 7.7% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **76.0%** | 0.055 | 76.5% | 23.5% | 0.4% | 9.2% | 6.2% | 0.0% | 76.0% | 8.2% |
| 7 | 20 | close_friend / citizen / good_record / rich / man_old | **76.0%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | **75.7%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | **75.5%** | 0.074 | 71.8% | 28.2% | 0.4% | 11.7% | 5.6% | 0.6% | 75.5% | 6.1% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **75.5%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **21.8%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **22.2%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **23.7%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **26.1%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **27.6%** | 0.041 | 28.6% | 71.4% | 0.0% | 8.1% | 62.7% | 0.0% | 27.6% | 1.5% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **28.8%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **28.9%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **29.3%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **30.4%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **31.2%** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 38 | stranger / mayor / good_record / poor / man_young | **9.6%** | 0.086 | 73.1% | 26.9% | 0.2% | 13.0% | 4.9% | 1.1% | 71.2% | 9.6% |
| 2 | 39 | stranger / mayor / good_record / poor / woman_young | **8.9%** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 3 | 55 | stranger / citizen / good_record / poor / woman_young | **8.6%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **8.6%** | 0.075 | 72.0% | 28.0% | 0.2% | 9.9% | 5.4% | 1.7% | 74.2% | 8.6% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | **8.6%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 6 | 6 | close_friend / mayor / good_record / poor / man_young | **8.6%** | 0.088 | 72.9% | 27.1% | 0.9% | 13.1% | 6.4% | 0.6% | 70.4% | 8.6% |
| 7 | 40 | stranger / mayor / good_record / poor / man_old | **8.5%** | 0.098 | 68.4% | 31.6% | 0.2% | 16.2% | 7.3% | 0.6% | 67.1% | 8.5% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | **8.4%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 9 | 8 | close_friend / mayor / good_record / poor / man_old | **8.4%** | 0.070 | 75.2% | 24.8% | 0.9% | 9.9% | 6.9% | 0.6% | 73.4% | 8.4% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **8.4%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 46 | stranger / mayor / poor_record / poor / man_young | **0.4%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 2 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.6%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 3 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.9%** | 0.044 | 41.0% | 59.0% | 0.2% | 8.3% | 44.7% | 0.0% | 45.9% | 0.9% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **1.1%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 5 | 25 | close_friend / citizen / poor_record / rich / woman_old | **1.1%** | 0.045 | 44.9% | 55.1% | 0.0% | 9.0% | 42.2% | 0.0% | 47.8% | 1.1% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **1.1%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | **1.1%** | 0.030 | 38.5% | 61.5% | 0.0% | 6.0% | 53.1% | 0.0% | 39.8% | 1.1% |
| 8 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.3%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 9 | 42 | stranger / mayor / poor_record / rich / man_young | **1.3%** | 0.042 | 38.5% | 61.5% | 0.0% | 8.4% | 50.7% | 0.0% | 39.6% | 1.3% |
| 10 | 32 | close_friend / citizen / poor_record / poor / man_old | **1.5%** | 0.042 | 38.5% | 61.5% | 0.0% | 8.3% | 47.6% | 0.0% | 42.5% | 1.5% |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **0.1601** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 2 | 37 | stranger / mayor / good_record / poor / woman_old | **0.1587** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 3 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.1543** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 4 | 54 | stranger / citizen / good_record / poor / man_young | **0.1478** | 0.148 | 69.7% | 30.3% | 0.4% | 25.0% | 4.7% | 1.7% | 67.2% | 0.9% |
| 5 | 40 | stranger / mayor / good_record / poor / man_old | **0.1463** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 6 | 56 | stranger / citizen / good_record / poor / man_old | **0.1444** | 0.144 | 68.8% | 31.2% | 0.4% | 26.2% | 5.2% | 0.9% | 67.0% | 0.4% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **0.1429** | 0.143 | 71.4% | 28.6% | 0.9% | 22.2% | 6.0% | 2.1% | 67.5% | 1.3% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | **0.1394** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | **0.1354** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.1336** | 0.134 | 73.9% | 26.1% | 1.7% | 19.7% | 4.3% | 1.7% | 72.1% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0365** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0385** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **0.0472** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0491** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 5 | 57 | stranger / citizen / poor_record / rich / woman_old | **0.0515** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0536** | 0.054 | 16.2% | 83.8% | 0.0% | 10.7% | 73.0% | 0.0% | 16.3% | 0.0% |
| 7 | 29 | close_friend / citizen / poor_record / poor / woman_old | **0.0558** | 0.056 | 25.2% | 74.8% | 0.0% | 11.2% | 63.9% | 0.0% | 24.9% | 0.0% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.0560** | 0.056 | 19.7% | 80.3% | 0.0% | 11.2% | 67.8% | 0.0% | 20.6% | 0.4% |
| 9 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.0579** | 0.058 | 28.2% | 71.8% | 0.0% | 11.5% | 60.3% | 0.0% | 27.8% | 0.4% |
| 10 | 62 | stranger / citizen / poor_record / poor / man_young | **0.0582** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **96.2%** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **95.3%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **95.3%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 4 | 46 | stranger / mayor / poor_record / poor / man_young | **94.9%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **94.0%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **93.2%** | 0.067 | 6.8% | 93.2% | 0.0% | 13.3% | 79.8% | 0.0% | 6.9% | 0.0% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | **92.3%** | 0.067 | 7.7% | 92.3% | 0.0% | 13.3% | 78.1% | 0.0% | 8.2% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **90.6%** | 0.067 | 9.4% | 90.6% | 0.0% | 13.3% | 77.7% | 0.0% | 9.0% | 0.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **86.8%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | **85.5%** | 0.066 | 14.5% | 85.5% | 0.0% | 13.2% | 72.2% | 0.0% | 14.5% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | **15.0%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **15.4%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |
| 3 | 17 | close_friend / citizen / good_record / rich / woman_old | **15.4%** | 0.074 | 84.6% | 15.4% | 0.4% | 10.3% | 4.7% | 1.7% | 81.5% | 1.3% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **16.2%** | 0.067 | 83.8% | 16.2% | 0.4% | 11.6% | 6.0% | 0.4% | 80.3% | 1.3% |
| 5 | 50 | stranger / citizen / good_record / rich / man_young | **17.1%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | **17.5%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | **17.9%** | 0.082 | 82.1% | 17.9% | 0.0% | 13.7% | 4.3% | 1.3% | 79.5% | 1.3% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | **18.8%** | 0.093 | 81.2% | 18.8% | 0.9% | 15.0% | 3.8% | 0.9% | 78.6% | 0.9% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | **19.7%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 10 | 8 | close_friend / mayor / good_record / poor / man_old | **19.7%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |


**FACT (%)** *(Note: 40 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37 | stranger / mayor / good_record / poor / woman_old | **2.1%** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 2 | 1 | close_friend / mayor / good_record / rich / woman_old | **1.7%** | 0.134 | 73.9% | 26.1% | 1.7% | 19.7% | 4.3% | 1.7% | 72.1% | 0.4% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | **1.7%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |
| 4 | 49 | stranger / citizen / good_record / rich / woman_old | **1.3%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **1.3%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 6 | 6 | close_friend / mayor / good_record / poor / man_young | **1.3%** | 0.130 | 74.8% | 25.2% | 1.3% | 20.5% | 4.3% | 1.3% | 71.4% | 1.3% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | **1.3%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | **0.9%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 9 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.9%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 10 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.9%** | 0.096 | 77.4% | 22.6% | 0.9% | 16.3% | 6.9% | 0.4% | 74.2% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 2 | 40 | stranger / mayor / good_record / poor / man_old | **0.0%** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 3 | 38 | stranger / mayor / good_record / poor / man_young | **0.0%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **0.0%** | 0.118 | 76.5% | 23.5% | 0.0% | 16.7% | 3.8% | 3.4% | 75.6% | 0.4% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.117 | 76.1% | 23.9% | 0.0% | 17.9% | 4.7% | 2.6% | 73.1% | 1.7% |
| 6 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.112 | 76.5% | 23.5% | 0.0% | 20.6% | 3.0% | 0.9% | 75.1% | 0.4% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.103 | 76.9% | 23.1% | 0.0% | 17.8% | 4.3% | 1.3% | 75.7% | 0.9% |
| 8 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.0%** | 0.101 | 27.8% | 72.2% | 0.0% | 20.1% | 52.1% | 0.0% | 27.4% | 0.4% |
| 9 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.0%** | 0.096 | 29.5% | 70.5% | 0.0% | 19.2% | 51.7% | 0.0% | 29.1% | 0.0% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.094 | 17.1% | 82.9% | 0.0% | 18.8% | 63.7% | 0.0% | 17.5% | 0.0% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **29.9%** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 2 | 56 | stranger / citizen / good_record / poor / man_old | **26.2%** | 0.144 | 68.8% | 31.2% | 0.4% | 26.2% | 5.2% | 0.9% | 67.0% | 0.4% |
| 3 | 40 | stranger / mayor / good_record / poor / man_old | **26.1%** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | **25.3%** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | **25.0%** | 0.148 | 69.7% | 30.3% | 0.4% | 25.0% | 4.7% | 1.7% | 67.2% | 0.9% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | **22.8%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **22.2%** | 0.143 | 71.4% | 28.6% | 0.9% | 22.2% | 6.0% | 2.1% | 67.5% | 1.3% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | **22.2%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 9 | 33 | stranger / mayor / good_record / rich / woman_old | **21.8%** | 0.128 | 74.4% | 25.6% | 0.4% | 21.8% | 4.3% | 1.3% | 70.9% | 1.3% |
| 10 | 39 | stranger / mayor / good_record / poor / woman_young | **21.4%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **7.3%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **7.7%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **9.0%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | **9.4%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 5 | 57 | stranger / citizen / poor_record / rich / woman_old | **10.3%** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |
| 6 | 17 | close_friend / citizen / good_record / rich / woman_old | **10.3%** | 0.074 | 84.6% | 15.4% | 0.4% | 10.3% | 4.7% | 1.7% | 81.5% | 1.3% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | **10.7%** | 0.054 | 16.2% | 83.8% | 0.0% | 10.7% | 73.0% | 0.0% | 16.3% | 0.0% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | **11.2%** | 0.056 | 19.7% | 80.3% | 0.0% | 11.2% | 67.8% | 0.0% | 20.6% | 0.4% |
| 9 | 29 | close_friend / citizen / poor_record / poor / woman_old | **11.2%** | 0.056 | 25.2% | 74.8% | 0.0% | 11.2% | 63.9% | 0.0% | 24.9% | 0.0% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | **11.3%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **85.5%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **85.0%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | **85.0%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **83.6%** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **80.8%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **79.8%** | 0.067 | 6.8% | 93.2% | 0.0% | 13.3% | 79.8% | 0.0% | 6.9% | 0.0% |
| 7 | 58 | stranger / citizen / poor_record / rich / man_young | **79.5%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **78.1%** | 0.067 | 7.7% | 92.3% | 0.0% | 13.3% | 78.1% | 0.0% | 8.2% | 0.4% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **77.7%** | 0.067 | 9.4% | 90.6% | 0.0% | 13.3% | 77.7% | 0.0% | 9.0% | 0.0% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **75.2%** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **1.3%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 2 | 38 | stranger / mayor / good_record / poor / man_young | **2.1%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 3 | 55 | stranger / citizen / good_record / poor / woman_young | **3.0%** | 0.112 | 76.5% | 23.5% | 0.0% | 20.6% | 3.0% | 0.9% | 75.1% | 0.4% |
| 4 | 18 | close_friend / citizen / good_record / rich / man_young | **3.0%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 5 | 21 | close_friend / citizen / good_record / poor / woman_old | **3.0%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |
| 6 | 49 | stranger / citizen / good_record / rich / woman_old | **3.0%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | **3.4%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 8 | 7 | close_friend / mayor / good_record / poor / woman_young | **3.8%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 9 | 34 | stranger / mayor / good_record / rich / man_young | **3.8%** | 0.118 | 76.5% | 23.5% | 0.0% | 16.7% | 3.8% | 3.4% | 75.6% | 0.4% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | **3.8%** | 0.110 | 79.1% | 20.9% | 0.4% | 14.1% | 3.8% | 3.4% | 77.4% | 0.9% |


**CHECKED_TRUE (%)** *(Note: 31 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | close_friend / mayor / good_record / poor / woman_young | **3.4%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 2 | 34 | stranger / mayor / good_record / rich / man_young | **3.4%** | 0.118 | 76.5% | 23.5% | 0.0% | 16.7% | 3.8% | 3.4% | 75.6% | 0.4% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | **3.4%** | 0.110 | 79.1% | 20.9% | 0.4% | 14.1% | 3.8% | 3.4% | 77.4% | 0.9% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | **3.0%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | **2.6%** | 0.117 | 76.1% | 23.9% | 0.0% | 17.9% | 4.7% | 2.6% | 73.1% | 1.7% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **2.2%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **2.1%** | 0.143 | 71.4% | 28.6% | 0.9% | 22.2% | 6.0% | 2.1% | 67.5% | 1.3% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | **2.1%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 9 | 54 | stranger / citizen / good_record / poor / man_young | **1.7%** | 0.148 | 69.7% | 30.3% | 0.4% | 25.0% | 4.7% | 1.7% | 67.2% | 0.9% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | **1.7%** | 0.134 | 73.9% | 26.1% | 1.7% | 19.7% | 4.3% | 1.7% | 72.1% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.0%** | 0.101 | 27.8% | 72.2% | 0.0% | 20.1% | 52.1% | 0.0% | 27.4% | 0.4% |
| 2 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.0%** | 0.096 | 29.5% | 70.5% | 0.0% | 19.2% | 51.7% | 0.0% | 29.1% | 0.0% |
| 3 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.094 | 17.1% | 82.9% | 0.0% | 18.8% | 63.7% | 0.0% | 17.5% | 0.0% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0%** | 0.092 | 27.4% | 72.6% | 0.0% | 18.4% | 54.7% | 0.0% | 26.9% | 0.0% |
| 5 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.0%** | 0.088 | 30.8% | 69.2% | 0.0% | 17.5% | 52.6% | 0.0% | 29.5% | 0.4% |
| 6 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0%** | 0.088 | 28.6% | 71.4% | 0.0% | 17.5% | 53.8% | 0.0% | 28.6% | 0.0% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0%** | 0.087 | 34.6% | 65.4% | 0.0% | 17.2% | 48.1% | 0.0% | 33.9% | 0.9% |
| 8 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.0%** | 0.084 | 22.6% | 77.4% | 0.4% | 15.8% | 61.1% | 0.0% | 21.8% | 0.9% |
| 9 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.0%** | 0.081 | 28.6% | 71.4% | 0.0% | 16.2% | 55.1% | 0.0% | 28.6% | 0.0% |
| 10 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | **82.3%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 2 | 17 | close_friend / citizen / good_record / rich / woman_old | **81.5%** | 0.074 | 84.6% | 15.4% | 0.4% | 10.3% | 4.7% | 1.7% | 81.5% | 1.3% |
| 3 | 21 | close_friend / citizen / good_record / poor / woman_old | **81.1%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **80.3%** | 0.067 | 83.8% | 16.2% | 0.4% | 11.6% | 6.0% | 0.4% | 80.3% | 1.3% |
| 5 | 50 | stranger / citizen / good_record / rich / man_young | **79.6%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | **79.5%** | 0.082 | 82.1% | 17.9% | 0.0% | 13.7% | 4.3% | 1.3% | 79.5% | 1.3% |
| 7 | 18 | close_friend / citizen / good_record / rich / man_young | **79.4%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | **78.6%** | 0.093 | 81.2% | 18.8% | 0.9% | 15.0% | 3.8% | 0.9% | 78.6% | 0.9% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | **78.4%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 10 | 8 | close_friend / mayor / good_record / poor / man_old | **77.8%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | **4.7%** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **5.1%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **5.1%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 4 | 46 | stranger / mayor / poor_record / poor / man_young | **5.6%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **6.9%** | 0.067 | 6.8% | 93.2% | 0.0% | 13.3% | 79.8% | 0.0% | 6.9% | 0.0% |
| 6 | 63 | stranger / citizen / poor_record / poor / woman_young | **7.3%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | **8.2%** | 0.067 | 7.7% | 92.3% | 0.0% | 13.3% | 78.1% | 0.0% | 8.2% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **9.0%** | 0.067 | 9.4% | 90.6% | 0.0% | 13.3% | 77.7% | 0.0% | 9.0% | 0.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **12.8%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **14.1%** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |


**NOT_MENTIONED (%)** *(Note: 20 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **2.2%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |
| 2 | 18 | close_friend / citizen / good_record / rich / man_young | **2.1%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 3 | 40 | stranger / mayor / good_record / poor / man_old | **2.1%** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **2.1%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | **1.7%** | 0.117 | 76.1% | 23.9% | 0.0% | 17.9% | 4.7% | 2.6% | 73.1% | 1.7% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **1.3%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 7 | 53 | stranger / citizen / good_record / poor / woman_old | **1.3%** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 8 | 37 | stranger / mayor / good_record / poor / woman_old | **1.3%** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | **1.3%** | 0.096 | 77.4% | 22.6% | 0.9% | 16.3% | 6.9% | 0.4% | 74.2% | 1.3% |
| 10 | 21 | close_friend / citizen / good_record / poor / woman_old | **1.3%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 2 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.0%** | 0.096 | 29.5% | 70.5% | 0.0% | 19.2% | 51.7% | 0.0% | 29.1% | 0.0% |
| 3 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.094 | 17.1% | 82.9% | 0.0% | 18.8% | 63.7% | 0.0% | 17.5% | 0.0% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0%** | 0.092 | 27.4% | 72.6% | 0.0% | 18.4% | 54.7% | 0.0% | 26.9% | 0.0% |
| 5 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |
| 6 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0%** | 0.088 | 28.6% | 71.4% | 0.0% | 17.5% | 53.8% | 0.0% | 28.6% | 0.0% |
| 7 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.0%** | 0.081 | 28.6% | 71.4% | 0.0% | 16.2% | 55.1% | 0.0% | 28.6% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 9 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.0%** | 0.075 | 27.8% | 72.2% | 0.0% | 15.0% | 57.7% | 0.0% | 27.4% | 0.0% |
| 10 | 46 | stranger / mayor / poor_record / poor / man_young | **0.0%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **0.0539** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 2 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0505** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 3 | 36 | stranger / mayor / good_record / rich / man_old | **0.0481** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0475** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 5 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0469** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0466** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0440** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 8 | 40 | stranger / mayor / good_record / poor / man_old | **0.0427** | 0.043 | 67.5% | 32.5% | 0.4% | 6.4% | 9.8% | 0.0% | 68.4% | 15.0% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | **0.0413** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 10 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0383** | 0.038 | 70.9% | 29.1% | 0.4% | 5.6% | 8.6% | 0.0% | 69.5% | 15.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0066** | 0.007 | 60.7% | 39.3% | 0.0% | 1.3% | 33.3% | 0.0% | 63.2% | 2.1% |
| 2 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0066** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |
| 3 | 60 | stranger / citizen / poor_record / rich / man_old | **0.0066** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 4 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.0066** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 35.9% | 0.0% | 59.4% | 3.4% |
| 5 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.0066** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 44.9% | 0.0% | 50.4% | 3.4% |
| 6 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0068** | 0.007 | 57.3% | 42.7% | 0.0% | 1.3% | 34.9% | 0.0% | 59.5% | 4.3% |
| 7 | 24 | close_friend / citizen / good_record / poor / man_old | **0.0075** | 0.007 | 70.1% | 29.9% | 0.0% | 1.3% | 9.4% | 0.0% | 75.5% | 13.7% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0087** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 9 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.0090** | 0.009 | 56.8% | 43.2% | 0.0% | 1.7% | 32.5% | 0.0% | 60.7% | 5.1% |
| 10 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0111** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **60.7%** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **59.8%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 3 | 60 | stranger / citizen / poor_record / rich / man_old | **58.1%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **55.6%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | **55.1%** | 0.011 | 44.9% | 55.1% | 0.0% | 2.2% | 52.2% | 0.0% | 42.7% | 3.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **53.8%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **53.0%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 45.7% | 0.0% | 48.7% | 3.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **53.0%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 9 | 26 | close_friend / citizen / poor_record / rich / man_young | **51.7%** | 0.020 | 48.3% | 51.7% | 0.4% | 3.0% | 34.2% | 0.0% | 58.5% | 3.8% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | **50.9%** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **20.5%** | 0.020 | 79.5% | 20.5% | 0.4% | 2.6% | 8.1% | 0.0% | 73.5% | 15.4% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | **21.8%** | 0.021 | 78.2% | 21.8% | 0.0% | 3.9% | 7.8% | 0.0% | 78.9% | 9.5% |
| 3 | 39 | stranger / mayor / good_record / poor / woman_young | **23.5%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | **23.9%** | 0.018 | 76.1% | 23.9% | 0.0% | 2.2% | 9.9% | 0.4% | 72.8% | 14.7% |
| 5 | 3 | close_friend / mayor / good_record / rich / woman_young | **24.8%** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 6 | 37 | stranger / mayor / good_record / poor / woman_old | **26.1%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | **26.1%** | 0.028 | 73.9% | 26.1% | 0.9% | 3.0% | 7.3% | 0.0% | 73.4% | 15.5% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **26.1%** | 0.028 | 73.9% | 26.1% | 0.0% | 4.7% | 5.6% | 0.0% | 74.8% | 15.0% |
| 9 | 22 | close_friend / citizen / good_record / poor / man_young | **26.5%** | 0.023 | 73.5% | 26.5% | 0.4% | 3.0% | 7.3% | 0.0% | 75.0% | 14.2% |
| 10 | 38 | stranger / mayor / good_record / poor / man_young | **28.2%** | 0.028 | 71.8% | 28.2% | 0.4% | 3.8% | 7.7% | 0.0% | 70.9% | 17.1% |


**FACT (%)** *(Note: 45 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | close_friend / mayor / good_record / rich / woman_old | **1.3%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 2 | 19 | close_friend / citizen / good_record / rich / woman_young | **1.3%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | **0.9%** | 0.038 | 70.9% | 29.1% | 0.9% | 4.8% | 6.9% | 0.0% | 73.2% | 14.3% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **0.9%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | **0.9%** | 0.038 | 70.9% | 29.1% | 0.9% | 3.9% | 7.3% | 0.4% | 71.7% | 15.9% |
| 6 | 49 | stranger / citizen / good_record / rich / woman_old | **0.9%** | 0.028 | 68.4% | 31.6% | 0.9% | 3.0% | 6.9% | 0.0% | 73.0% | 16.3% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.9%** | 0.028 | 73.9% | 26.1% | 0.9% | 3.0% | 7.3% | 0.0% | 73.4% | 15.5% |
| 8 | 50 | stranger / citizen / good_record / rich / man_young | **0.9%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 9 | 34 | stranger / mayor / good_record / rich / man_young | **0.4%** | 0.023 | 67.5% | 32.5% | 0.4% | 3.0% | 6.9% | 0.0% | 72.8% | 16.8% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | **0.4%** | 0.023 | 73.5% | 26.5% | 0.4% | 3.0% | 7.3% | 0.0% | 75.0% | 14.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 36 | stranger / mayor / good_record / rich / man_old | **0.0%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 4 | 2 | close_friend / mayor / good_record / rich / man_young | **0.0%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 70.0% | 16.3% |
| 5 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0%** | 0.033 | 70.1% | 29.9% | 0.0% | 6.0% | 10.7% | 0.0% | 73.4% | 9.9% |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 71.7% | 14.6% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.033 | 68.4% | 31.6% | 0.0% | 5.6% | 9.4% | 0.0% | 70.8% | 14.2% |
| 8 | 56 | stranger / citizen / good_record / poor / man_old | **0.0%** | 0.032 | 67.1% | 32.9% | 0.0% | 5.6% | 6.8% | 0.0% | 75.2% | 12.4% |
| 9 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 10 | 39 | stranger / mayor / good_record / poor / woman_young | **0.0%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 36 | stranger / mayor / good_record / rich / man_old | **8.6%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **7.8%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | **6.8%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 4 | 8 | close_friend / mayor / good_record / poor / man_old | **6.5%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | **6.4%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | **6.4%** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 7 | 40 | stranger / mayor / good_record / poor / man_old | **6.4%** | 0.043 | 67.5% | 32.5% | 0.4% | 6.4% | 9.8% | 0.0% | 68.4% | 15.0% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | **6.0%** | 0.033 | 70.1% | 29.9% | 0.0% | 6.0% | 10.7% | 0.0% | 73.4% | 9.9% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | **5.6%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 10 | 52 | stranger / citizen / good_record / rich / man_old | **5.6%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 28 | close_friend / citizen / poor_record / rich / man_old | **1.3%** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 35.9% | 0.0% | 59.4% | 3.4% |
| 2 | 59 | stranger / citizen / poor_record / rich / woman_young | **1.3%** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 44.9% | 0.0% | 50.4% | 3.4% |
| 3 | 60 | stranger / citizen / poor_record / rich / man_old | **1.3%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 4 | 58 | stranger / citizen / poor_record / rich / man_young | **1.3%** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | **1.3%** | 0.007 | 60.7% | 39.3% | 0.0% | 1.3% | 33.3% | 0.0% | 63.2% | 2.1% |
| 6 | 24 | close_friend / citizen / good_record / poor / man_old | **1.3%** | 0.007 | 70.1% | 29.9% | 0.0% | 1.3% | 9.4% | 0.0% | 75.5% | 13.7% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | **1.3%** | 0.007 | 57.3% | 42.7% | 0.0% | 1.3% | 34.9% | 0.0% | 59.5% | 4.3% |
| 8 | 12 | close_friend / mayor / poor_record / rich / man_old | **1.7%** | 0.013 | 54.3% | 45.7% | 0.4% | 1.7% | 31.6% | 0.0% | 64.5% | 1.7% |
| 9 | 30 | close_friend / citizen / poor_record / poor / man_young | **1.7%** | 0.009 | 56.8% | 43.2% | 0.0% | 1.7% | 32.5% | 0.0% | 60.7% | 5.1% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **1.7%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **56.4%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **56.2%** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **52.2%** | 0.011 | 44.9% | 55.1% | 0.0% | 2.2% | 52.2% | 0.0% | 42.7% | 3.0% |
| 4 | 60 | stranger / citizen / poor_record / rich / man_old | **49.6%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **48.3%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **47.2%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | **46.6%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | **45.7%** | 0.015 | 50.4% | 49.6% | 0.0% | 3.0% | 45.7% | 0.0% | 48.3% | 3.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **45.7%** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **45.7%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 45.7% | 0.0% | 48.7% | 3.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | **5.1%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **5.2%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 33 | stranger / mayor / good_record / rich / woman_old | **5.6%** | 0.028 | 73.9% | 26.1% | 0.0% | 4.7% | 5.6% | 0.0% | 74.8% | 15.0% |
| 4 | 39 | stranger / mayor / good_record / poor / woman_young | **5.6%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |
| 5 | 37 | stranger / mayor / good_record / poor / woman_old | **6.0%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 6 | 36 | stranger / mayor / good_record / rich / man_old | **6.4%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | **6.8%** | 0.032 | 67.1% | 32.9% | 0.0% | 5.6% | 6.8% | 0.0% | 75.2% | 12.4% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | **6.9%** | 0.028 | 68.4% | 31.6% | 0.9% | 3.0% | 6.9% | 0.0% | 73.0% | 16.3% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | **6.9%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 10 | 34 | stranger / mayor / good_record / rich / man_young | **6.9%** | 0.023 | 67.5% | 32.5% | 0.4% | 3.0% | 6.9% | 0.0% | 72.8% | 16.8% |


**CHECKED_TRUE (%)** *(Note: 58 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | close_friend / mayor / good_record / poor / man_old | **0.4%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.4%** | 0.018 | 76.1% | 23.9% | 0.0% | 2.2% | 9.9% | 0.4% | 72.8% | 14.7% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | **0.4%** | 0.038 | 70.9% | 29.1% | 0.9% | 3.9% | 7.3% | 0.4% | 71.7% | 15.9% |
| 4 | 50 | stranger / citizen / good_record / rich / man_young | **0.4%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 5 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.4%** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 6 | 54 | stranger / citizen / good_record / poor / man_young | **0.4%** | 0.018 | 70.5% | 29.5% | 0.0% | 2.1% | 8.1% | 0.4% | 73.9% | 15.4% |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | **0.0%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 2 | 36 | stranger / mayor / good_record / rich / man_old | **0.0%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 3 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 4 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 5 | 40 | stranger / mayor / good_record / poor / man_old | **0.0%** | 0.043 | 67.5% | 32.5% | 0.4% | 6.4% | 9.8% | 0.0% | 68.4% | 15.0% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.038 | 70.9% | 29.1% | 0.4% | 5.6% | 8.6% | 0.0% | 69.5% | 15.9% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.038 | 70.9% | 29.1% | 0.9% | 4.8% | 6.9% | 0.0% | 73.2% | 14.3% |
| 9 | 2 | close_friend / mayor / good_record / rich / man_young | **0.0%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 70.0% | 16.3% |
| 10 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0%** | 0.033 | 70.1% | 29.9% | 0.0% | 6.0% | 10.7% | 0.0% | 73.4% | 9.9% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | **78.9%** | 0.021 | 78.2% | 21.8% | 0.0% | 3.9% | 7.8% | 0.0% | 78.9% | 9.5% |
| 2 | 37 | stranger / mayor / good_record / poor / woman_old | **77.4%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 3 | 24 | close_friend / citizen / good_record / poor / man_old | **75.5%** | 0.007 | 70.1% | 29.9% | 0.0% | 1.3% | 9.4% | 0.0% | 75.5% | 13.7% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **75.4%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 5 | 56 | stranger / citizen / good_record / poor / man_old | **75.2%** | 0.032 | 67.1% | 32.9% | 0.0% | 5.6% | 6.8% | 0.0% | 75.2% | 12.4% |
| 6 | 35 | stranger / mayor / good_record / rich / woman_young | **75.1%** | 0.030 | 71.4% | 28.6% | 0.4% | 4.3% | 7.3% | 0.0% | 75.1% | 12.9% |
| 7 | 22 | close_friend / citizen / good_record / poor / man_young | **75.0%** | 0.023 | 73.5% | 26.5% | 0.4% | 3.0% | 7.3% | 0.0% | 75.0% | 14.2% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **74.8%** | 0.028 | 73.9% | 26.1% | 0.0% | 4.7% | 5.6% | 0.0% | 74.8% | 15.0% |
| 9 | 36 | stranger / mayor / good_record / rich / man_old | **74.2%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | **73.9%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | **38.6%** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | **39.3%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **42.7%** | 0.011 | 44.9% | 55.1% | 0.0% | 2.2% | 52.2% | 0.0% | 42.7% | 3.0% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **44.9%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 5 | 60 | stranger / citizen / poor_record / rich / man_old | **46.2%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **48.3%** | 0.015 | 50.4% | 49.6% | 0.0% | 3.0% | 45.7% | 0.0% | 48.3% | 3.0% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | **48.7%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 45.7% | 0.0% | 48.7% | 3.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | **49.4%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **49.6%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | **50.4%** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 44.9% | 0.0% | 50.4% | 3.4% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 38 | stranger / mayor / good_record / poor / man_young | **17.1%** | 0.028 | 71.8% | 28.2% | 0.4% | 3.8% | 7.7% | 0.0% | 70.9% | 17.1% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **16.9%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | **16.8%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **16.8%** | 0.023 | 67.5% | 32.5% | 0.4% | 3.0% | 6.9% | 0.0% | 72.8% | 16.8% |
| 5 | 39 | stranger / mayor / good_record / poor / woman_young | **16.4%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |
| 6 | 2 | close_friend / mayor / good_record / rich / man_young | **16.3%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 70.0% | 16.3% |
| 7 | 49 | stranger / citizen / good_record / rich / woman_old | **16.3%** | 0.028 | 68.4% | 31.6% | 0.9% | 3.0% | 6.9% | 0.0% | 73.0% | 16.3% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | **15.9%** | 0.038 | 70.9% | 29.1% | 0.4% | 5.6% | 8.6% | 0.0% | 69.5% | 15.9% |
| 9 | 20 | close_friend / citizen / good_record / rich / man_old | **15.9%** | 0.038 | 70.9% | 29.1% | 0.9% | 3.9% | 7.3% | 0.4% | 71.7% | 15.9% |
| 10 | 7 | close_friend / mayor / good_record / poor / woman_young | **15.5%** | 0.028 | 73.9% | 26.1% | 0.9% | 3.0% | 7.3% | 0.0% | 73.4% | 15.5% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 46 | stranger / mayor / poor_record / poor / man_young | **0.9%** | 0.015 | 53.0% | 47.0% | 0.0% | 3.0% | 43.8% | 0.0% | 52.4% | 0.9% |
| 2 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.9%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | **1.7%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 4 | 12 | close_friend / mayor / poor_record / rich / man_old | **1.7%** | 0.013 | 54.3% | 45.7% | 0.4% | 1.7% | 31.6% | 0.0% | 64.5% | 1.7% |
| 5 | 48 | stranger / mayor / poor_record / poor / man_old | **2.1%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **2.1%** | 0.007 | 60.7% | 39.3% | 0.0% | 1.3% | 33.3% | 0.0% | 63.2% | 2.1% |
| 7 | 42 | stranger / mayor / poor_record / rich / man_young | **2.1%** | 0.022 | 60.7% | 39.3% | 0.0% | 4.3% | 30.5% | 0.0% | 63.1% | 2.1% |
| 8 | 25 | close_friend / citizen / poor_record / rich / woman_old | **2.1%** | 0.022 | 61.1% | 38.9% | 0.0% | 4.3% | 26.2% | 0.0% | 67.4% | 2.1% |
| 9 | 63 | stranger / citizen / poor_record / poor / woman_young | **2.6%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 10 | 32 | close_friend / citizen / poor_record / poor / man_old | **2.6%** | 0.015 | 53.4% | 46.6% | 0.0% | 3.0% | 32.5% | 0.0% | 62.0% | 2.6% |


### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0419** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0347** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0328** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0326** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0310** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | **0.0310** | 0.031 | 65.2% | 34.8% | 0.9% | 4.3% | 6.2% | 0.0% | 85.4% | 3.2% |
| 7 | 38 | stranger / mayor / good_record / poor / man_young | **0.0310** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 8 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0301** | 0.030 | 66.7% | 33.3% | 0.6% | 4.5% | 7.1% | 0.0% | 84.1% | 3.7% |
| 9 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0299** | 0.030 | 67.1% | 32.9% | 0.2% | 4.5% | 8.3% | 0.4% | 83.1% | 3.4% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | **0.0297** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 42 | stranger / mayor / poor_record / rich / man_young | **0.0066** | 0.007 | 54.7% | 45.3% | 0.2% | 0.9% | 18.8% | 0.0% | 77.7% | 2.4% |
| 2 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.0066** | 0.007 | 59.2% | 40.8% | 0.2% | 0.9% | 14.6% | 0.0% | 81.8% | 2.6% |
| 3 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0077** | 0.008 | 58.3% | 41.7% | 0.2% | 0.6% | 12.0% | 0.2% | 84.8% | 2.1% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0078** | 0.008 | 59.2% | 40.8% | 0.2% | 0.2% | 15.8% | 0.4% | 79.9% | 3.4% |
| 5 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.0078** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | **0.0088** | 0.009 | 57.1% | 42.9% | 0.4% | 0.9% | 19.0% | 0.0% | 77.1% | 2.6% |
| 7 | 62 | stranger / citizen / poor_record / poor / man_young | **0.0088** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 8 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.0090** | 0.009 | 58.1% | 41.9% | 0.2% | 0.9% | 16.1% | 0.2% | 77.8% | 4.7% |
| 9 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.0108** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 10 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0109** | 0.011 | 56.4% | 43.6% | 0.2% | 1.3% | 14.3% | 0.2% | 82.4% | 1.5% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **60.0%** | 0.014 | 40.0% | 60.0% | 0.2% | 2.4% | 39.2% | 0.0% | 55.5% | 2.8% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **58.5%** | 0.016 | 41.5% | 58.5% | 0.4% | 2.4% | 34.6% | 0.0% | 60.0% | 2.6% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **55.6%** | 0.019 | 44.4% | 55.6% | 0.4% | 2.8% | 32.1% | 0.0% | 61.5% | 3.2% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **55.3%** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **53.8%** | 0.024 | 46.2% | 53.8% | 0.4% | 3.8% | 27.4% | 0.0% | 65.0% | 3.4% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **51.9%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **51.7%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **50.0%** | 0.016 | 50.0% | 50.0% | 0.6% | 1.9% | 22.9% | 0.0% | 71.8% | 2.8% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **49.4%** | 0.011 | 50.6% | 49.4% | 0.2% | 1.7% | 21.8% | 0.0% | 74.1% | 2.1% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | **49.1%** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **28.4%** | 0.027 | 71.6% | 28.4% | 0.6% | 3.4% | 6.0% | 0.2% | 86.7% | 3.0% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | **29.1%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | **29.5%** | 0.016 | 70.5% | 29.5% | 0.4% | 2.1% | 7.1% | 0.0% | 86.9% | 3.4% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | **29.7%** | 0.023 | 70.3% | 29.7% | 0.6% | 3.2% | 8.4% | 0.0% | 85.2% | 2.6% |
| 5 | 6 | close_friend / mayor / good_record / poor / man_young | **30.6%** | 0.024 | 69.4% | 30.6% | 0.4% | 3.9% | 8.1% | 0.0% | 85.9% | 1.7% |
| 6 | 34 | stranger / mayor / good_record / rich / man_young | **30.8%** | 0.023 | 69.2% | 30.8% | 0.2% | 4.1% | 6.5% | 0.0% | 86.7% | 2.6% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | **31.0%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | **31.2%** | 0.020 | 68.8% | 31.2% | 0.4% | 3.0% | 6.2% | 0.0% | 87.1% | 3.2% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | **31.4%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | **31.8%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | close_friend / mayor / poor_record / rich / man_old | **1.3%** | 0.019 | 60.0% | 40.0% | 1.3% | 0.6% | 14.4% | 0.2% | 80.4% | 3.0% |
| 2 | 27 | close_friend / citizen / poor_record / rich / woman_young | **1.3%** | 0.021 | 60.0% | 40.0% | 1.3% | 1.1% | 11.4% | 0.2% | 83.3% | 2.8% |
| 3 | 10 | close_friend / mayor / poor_record / rich / man_young | **1.1%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | **1.1%** | 0.016 | 62.6% | 37.4% | 1.1% | 1.1% | 10.7% | 0.0% | 85.3% | 1.9% |
| 5 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.9%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.9%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | **0.9%** | 0.026 | 63.2% | 36.8% | 0.9% | 3.2% | 6.7% | 0.0% | 85.6% | 3.7% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | **0.9%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 9 | 54 | stranger / citizen / good_record / poor / man_young | **0.9%** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **0.9%** | 0.025 | 67.9% | 32.1% | 0.9% | 3.2% | 10.3% | 0.0% | 83.5% | 2.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | **0.0%** | 0.021 | 65.4% | 34.6% | 0.0% | 4.1% | 8.1% | 0.0% | 82.9% | 4.9% |
| 2 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.018 | 68.2% | 31.8% | 0.0% | 3.4% | 8.2% | 0.0% | 86.5% | 1.9% |
| 3 | 46 | stranger / mayor / poor_record / poor / man_young | **0.0%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 4 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.011 | 56.2% | 43.8% | 0.0% | 1.7% | 18.6% | 0.2% | 77.4% | 2.1% |
| 5 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.0%** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.2%** | 0.030 | 67.1% | 32.9% | 0.2% | 4.5% | 8.3% | 0.4% | 83.1% | 3.4% |
| 7 | 33 | stranger / mayor / good_record / rich / woman_old | **0.2%** | 0.029 | 66.5% | 33.5% | 0.2% | 5.1% | 7.5% | 0.0% | 84.0% | 3.2% |
| 8 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.2%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 9 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.2%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | **0.2%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **6.0%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | **5.6%** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | **5.4%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **5.2%** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 5 | 33 | stranger / mayor / good_record / rich / woman_old | **5.1%** | 0.029 | 66.5% | 33.5% | 0.2% | 5.1% | 7.5% | 0.0% | 84.0% | 3.2% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | **4.9%** | 0.030 | 66.9% | 33.1% | 0.4% | 4.9% | 8.6% | 0.0% | 83.7% | 2.4% |
| 7 | 3 | close_friend / mayor / good_record / rich / woman_young | **4.7%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | **4.7%** | 0.029 | 67.7% | 32.3% | 0.2% | 4.7% | 8.8% | 0.2% | 83.6% | 2.4% |
| 9 | 37 | stranger / mayor / good_record / poor / woman_old | **4.5%** | 0.030 | 66.7% | 33.3% | 0.6% | 4.5% | 7.1% | 0.0% | 84.1% | 3.7% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | **4.5%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.2%** | 0.008 | 59.2% | 40.8% | 0.2% | 0.2% | 15.8% | 0.4% | 79.9% | 3.4% |
| 2 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.4%** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 3 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.6%** | 0.008 | 58.3% | 41.7% | 0.2% | 0.6% | 12.0% | 0.2% | 84.8% | 2.1% |
| 4 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.6%** | 0.019 | 60.0% | 40.0% | 1.3% | 0.6% | 14.4% | 0.2% | 80.4% | 3.0% |
| 5 | 32 | close_friend / citizen / poor_record / poor / man_old | **0.9%** | 0.009 | 57.1% | 42.9% | 0.4% | 0.9% | 19.0% | 0.0% | 77.1% | 2.6% |
| 6 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.9%** | 0.013 | 57.5% | 42.5% | 0.9% | 0.9% | 15.6% | 0.0% | 79.4% | 3.2% |
| 7 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.9%** | 0.007 | 59.2% | 40.8% | 0.2% | 0.9% | 14.6% | 0.0% | 81.8% | 2.6% |
| 8 | 42 | stranger / mayor / poor_record / rich / man_young | **0.9%** | 0.007 | 54.7% | 45.3% | 0.2% | 0.9% | 18.8% | 0.0% | 77.7% | 2.4% |
| 9 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.9%** | 0.009 | 58.1% | 41.9% | 0.2% | 0.9% | 16.1% | 0.2% | 77.8% | 4.7% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | **1.1%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **39.2%** | 0.014 | 40.0% | 60.0% | 0.2% | 2.4% | 39.2% | 0.0% | 55.5% | 2.8% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **34.6%** | 0.016 | 41.5% | 58.5% | 0.4% | 2.4% | 34.6% | 0.0% | 60.0% | 2.6% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **33.3%** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **32.1%** | 0.019 | 44.4% | 55.6% | 0.4% | 2.8% | 32.1% | 0.0% | 61.5% | 3.2% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **28.5%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **28.4%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | **27.4%** | 0.024 | 46.2% | 53.8% | 0.4% | 3.8% | 27.4% | 0.0% | 65.0% | 3.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **22.9%** | 0.016 | 50.0% | 50.0% | 0.6% | 1.9% | 22.9% | 0.0% | 71.8% | 2.8% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **22.9%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | **21.8%** | 0.011 | 50.6% | 49.4% | 0.2% | 1.7% | 21.8% | 0.0% | 74.1% | 2.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **6.0%** | 0.027 | 71.6% | 28.4% | 0.6% | 3.4% | 6.0% | 0.2% | 86.7% | 3.0% |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | **6.2%** | 0.031 | 65.2% | 34.8% | 0.9% | 4.3% | 6.2% | 0.0% | 85.4% | 3.2% |
| 3 | 52 | stranger / citizen / good_record / rich / man_old | **6.2%** | 0.020 | 68.8% | 31.2% | 0.4% | 3.0% | 6.2% | 0.0% | 87.1% | 3.2% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **6.4%** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 5 | 34 | stranger / mayor / good_record / rich / man_young | **6.5%** | 0.023 | 69.2% | 30.8% | 0.2% | 4.1% | 6.5% | 0.0% | 86.7% | 2.6% |
| 6 | 4 | close_friend / mayor / good_record / rich / man_old | **6.7%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 7 | 53 | stranger / citizen / good_record / poor / woman_old | **6.7%** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 8 | 56 | stranger / citizen / good_record / poor / man_old | **6.7%** | 0.026 | 63.2% | 36.8% | 0.9% | 3.2% | 6.7% | 0.0% | 85.6% | 3.7% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | **6.9%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 10 | 49 | stranger / citizen / good_record / rich / woman_old | **7.1%** | 0.016 | 70.5% | 29.5% | 0.4% | 2.1% | 7.1% | 0.0% | 86.9% | 3.4% |


**CHECKED_TRUE (%)** *(Note: 43 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.4%** | 0.008 | 59.2% | 40.8% | 0.2% | 0.2% | 15.8% | 0.4% | 79.9% | 3.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.4%** | 0.030 | 67.1% | 32.9% | 0.2% | 4.5% | 8.3% | 0.4% | 83.1% | 3.4% |
| 3 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.4%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |
| 4 | 60 | stranger / citizen / poor_record / rich / man_old | **0.4%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 5 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.4%** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 6 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.2%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 7 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.2%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.2%** | 0.029 | 67.7% | 32.3% | 0.2% | 4.7% | 8.8% | 0.2% | 83.6% | 2.4% |
| 9 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.2%** | 0.019 | 60.0% | 40.0% | 1.3% | 0.6% | 14.4% | 0.2% | 80.4% | 3.0% |
| 10 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.2%** | 0.011 | 58.8% | 41.2% | 0.2% | 1.3% | 17.4% | 0.2% | 77.8% | 3.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.031 | 65.2% | 34.8% | 0.9% | 4.3% | 6.2% | 0.0% | 85.4% | 3.2% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | **0.0%** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 5 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0%** | 0.030 | 66.7% | 33.3% | 0.6% | 4.5% | 7.1% | 0.0% | 84.1% | 3.7% |
| 6 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |
| 7 | 39 | stranger / mayor / good_record / poor / woman_young | **0.0%** | 0.030 | 66.9% | 33.1% | 0.4% | 4.9% | 8.6% | 0.0% | 83.7% | 2.4% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.029 | 66.5% | 33.5% | 0.2% | 5.1% | 7.5% | 0.0% | 84.0% | 3.2% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | **0.0%** | 0.026 | 64.3% | 35.7% | 0.2% | 4.5% | 7.5% | 0.0% | 82.0% | 5.8% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 52 | stranger / citizen / good_record / rich / man_old | **87.1%** | 0.020 | 68.8% | 31.2% | 0.4% | 3.0% | 6.2% | 0.0% | 87.1% | 3.2% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | **87.0%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | **86.9%** | 0.016 | 70.5% | 29.5% | 0.4% | 2.1% | 7.1% | 0.0% | 86.9% | 3.4% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | **86.7%** | 0.027 | 71.6% | 28.4% | 0.6% | 3.4% | 6.0% | 0.2% | 86.7% | 3.0% |
| 5 | 34 | stranger / mayor / good_record / rich / man_young | **86.7%** | 0.023 | 69.2% | 30.8% | 0.2% | 4.1% | 6.5% | 0.0% | 86.7% | 2.6% |
| 6 | 22 | close_friend / citizen / good_record / poor / man_young | **86.5%** | 0.018 | 68.2% | 31.8% | 0.0% | 3.4% | 8.2% | 0.0% | 86.5% | 1.9% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **86.1%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | **85.9%** | 0.024 | 69.4% | 30.6% | 0.4% | 3.9% | 8.1% | 0.0% | 85.9% | 1.7% |
| 9 | 40 | stranger / mayor / good_record / poor / man_old | **85.8%** | 0.019 | 65.8% | 34.2% | 0.4% | 2.8% | 7.1% | 0.0% | 85.8% | 3.9% |
| 10 | 56 | stranger / citizen / good_record / poor / man_old | **85.6%** | 0.026 | 63.2% | 36.8% | 0.9% | 3.2% | 6.7% | 0.0% | 85.6% | 3.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **55.5%** | 0.014 | 40.0% | 60.0% | 0.2% | 2.4% | 39.2% | 0.0% | 55.5% | 2.8% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **60.0%** | 0.016 | 41.5% | 58.5% | 0.4% | 2.4% | 34.6% | 0.0% | 60.0% | 2.6% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **61.5%** | 0.019 | 44.4% | 55.6% | 0.4% | 2.8% | 32.1% | 0.0% | 61.5% | 3.2% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **61.8%** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **65.0%** | 0.024 | 46.2% | 53.8% | 0.4% | 3.8% | 27.4% | 0.0% | 65.0% | 3.4% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **65.6%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **67.2%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 8 | 60 | stranger / citizen / poor_record / rich / man_old | **70.9%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **71.8%** | 0.016 | 50.0% | 50.0% | 0.6% | 1.9% | 22.9% | 0.0% | 71.8% | 2.8% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | **73.1%** | 0.024 | 51.9% | 48.1% | 0.6% | 3.4% | 19.0% | 0.0% | 73.1% | 3.8% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 54 | stranger / citizen / good_record / poor / man_young | **6.2%** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **5.8%** | 0.026 | 64.3% | 35.7% | 0.2% | 4.5% | 7.5% | 0.0% | 82.0% | 5.8% |
| 3 | 35 | stranger / mayor / good_record / rich / woman_young | **4.9%** | 0.021 | 65.4% | 34.6% | 0.0% | 4.1% | 8.1% | 0.0% | 82.9% | 4.9% |
| 4 | 9 | close_friend / mayor / poor_record / rich / woman_old | **4.7%** | 0.009 | 58.1% | 41.9% | 0.2% | 0.9% | 16.1% | 0.2% | 77.8% | 4.7% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **4.1%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 6 | 59 | stranger / citizen / poor_record / rich / woman_young | **4.1%** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |
| 7 | 40 | stranger / mayor / good_record / poor / man_old | **3.9%** | 0.019 | 65.8% | 34.2% | 0.4% | 2.8% | 7.1% | 0.0% | 85.8% | 3.9% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | **3.8%** | 0.024 | 51.9% | 48.1% | 0.6% | 3.4% | 19.0% | 0.0% | 73.1% | 3.8% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **3.8%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | **3.7%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.9%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | **1.1%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | **1.1%** | 0.023 | 66.7% | 33.3% | 0.2% | 4.1% | 10.3% | 0.0% | 84.3% | 1.1% |
| 4 | 10 | close_friend / mayor / poor_record / rich / man_young | **1.5%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |
| 5 | 26 | close_friend / citizen / poor_record / rich / man_young | **1.5%** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 6 | 31 | close_friend / citizen / poor_record / poor / woman_young | **1.5%** | 0.011 | 56.4% | 43.6% | 0.2% | 1.3% | 14.3% | 0.2% | 82.4% | 1.5% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | **1.7%** | 0.024 | 69.4% | 30.6% | 0.4% | 3.9% | 8.1% | 0.0% | 85.9% | 1.7% |
| 8 | 11 | close_friend / mayor / poor_record / rich / woman_young | **1.9%** | 0.016 | 62.6% | 37.4% | 1.1% | 1.1% | 10.7% | 0.0% | 85.3% | 1.9% |
| 9 | 4 | close_friend / mayor / good_record / rich / man_old | **1.9%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | **1.9%** | 0.018 | 68.2% | 31.8% | 0.0% | 3.4% | 8.2% | 0.0% | 86.5% | 1.9% |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0237** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0194** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.0193** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0171** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0152** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.0151** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0130** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 8 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0129** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | **0.0129** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 10 | 64 | stranger / citizen / poor_record / poor / man_old | **0.0107** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 42 | stranger / mayor / poor_record / rich / man_young | **0.0000** | 0.000 | 85.5% | 14.5% | 0.0% | 0.0% | 17.5% | 0.0% | 82.1% | 0.4% |
| 2 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0000** | 0.000 | 94.9% | 5.1% | 0.0% | 0.0% | 6.0% | 0.0% | 93.6% | 0.4% |
| 3 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.0000** | 0.000 | 97.4% | 2.6% | 0.0% | 0.0% | 4.3% | 0.0% | 95.3% | 0.4% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0000** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 7.3% | 0.0% | 92.3% | 0.4% |
| 5 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.0000** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 5.6% | 0.0% | 94.4% | 0.0% |
| 6 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.0000** | 0.000 | 98.7% | 1.3% | 0.0% | 0.0% | 3.9% | 0.0% | 95.7% | 0.4% |
| 7 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.0000** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 7.3% | 0.0% | 91.5% | 1.3% |
| 8 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0000** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 2.1% | 0.0% | 97.0% | 0.9% |
| 9 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.0000** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 3.0% | 0.0% | 96.6% | 0.4% |
| 10 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0000** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 98.3% | 0.0% |


**SKIP Rate (%)** *(Note: 14 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **44.0%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **40.6%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **40.2%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **35.5%** | 0.004 | 64.5% | 35.5% | 0.0% | 0.9% | 37.2% | 0.0% | 61.5% | 0.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **32.1%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | **28.6%** | 0.002 | 71.4% | 28.6% | 0.0% | 0.4% | 28.6% | 0.0% | 70.5% | 0.4% |
| 7 | 45 | stranger / mayor / poor_record / poor / woman_old | **26.1%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | **21.8%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **21.8%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **19.2%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.3% | 0.0% | 97.4% | 0.0% |
| 2 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.7% | 0.0% | 96.6% | 0.4% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | **0.0%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 2.6% | 0.0% | 95.3% | 1.3% |
| 4 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 0.9% | 0.0% | 97.4% | 0.9% |
| 5 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 4.3% | 0.0% | 94.9% | 0.4% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 97.4% | 0.9% |
| 8 | 2 | close_friend / mayor / good_record / rich / man_young | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.7% | 0.0% | 96.6% | 1.3% |
| 9 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 2.1% | 0.0% | 97.4% | 0.0% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 98.3% | 0.0% |


**FACT (%)** *(Note: 57 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.4%** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 2 | 48 | stranger / mayor / poor_record / poor / man_old | **0.4%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 3 | 25 | close_friend / citizen / poor_record / rich / woman_old | **0.4%** | 0.011 | 96.6% | 3.4% | 0.4% | 1.3% | 4.7% | 0.0% | 93.2% | 0.4% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | **0.4%** | 0.009 | 96.6% | 3.4% | 0.4% | 0.9% | 3.8% | 0.0% | 94.0% | 0.9% |
| 5 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.4%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 4.3% | 0.0% | 94.9% | 0.4% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | **0.4%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.4%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 9 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 10 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0%** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 7 | 38 | stranger / mayor / good_record / poor / man_young | **0.0%** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 8 | 64 | stranger / citizen / poor_record / poor / man_old | **0.0%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **0.0%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.011 | 85.9% | 14.1% | 0.0% | 2.1% | 16.7% | 0.0% | 80.8% | 0.4% |


**UNCERTAIN (%)** *(Note: 18 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **4.7%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **3.8%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | **3.8%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | **3.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | **3.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | **2.6%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | **2.6%** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | **2.6%** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 9 | 64 | stranger / citizen / poor_record / poor / man_old | **2.1%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | **2.1%** | 0.011 | 85.9% | 14.1% | 0.0% | 2.1% | 16.7% | 0.0% | 80.8% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0%** | 0.004 | 98.7% | 1.3% | 0.0% | 0.0% | 3.0% | 0.4% | 96.2% | 0.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.0% | 2.6% | 0.4% | 96.6% | 0.4% |
| 3 | 1 | close_friend / mayor / good_record / rich / woman_old | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 4.3% | 0.0% | 94.9% | 0.4% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 5 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 6 | 42 | stranger / mayor / poor_record / rich / man_young | **0.0%** | 0.000 | 85.5% | 14.5% | 0.0% | 0.0% | 17.5% | 0.0% | 82.1% | 0.4% |
| 7 | 31 | close_friend / citizen / poor_record / poor / woman_young | **0.0%** | 0.000 | 94.9% | 5.1% | 0.0% | 0.0% | 6.0% | 0.0% | 93.6% | 0.4% |
| 8 | 15 | close_friend / mayor / poor_record / poor / woman_young | **0.0%** | 0.000 | 97.4% | 2.6% | 0.0% | 0.0% | 4.3% | 0.0% | 95.3% | 0.4% |
| 9 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0%** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 7.3% | 0.0% | 92.3% | 0.4% |
| 10 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.0%** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 5.6% | 0.0% | 94.4% | 0.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **42.7%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **37.2%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | **37.2%** | 0.004 | 64.5% | 35.5% | 0.0% | 0.9% | 37.2% | 0.0% | 61.5% | 0.4% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | **35.9%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | **28.6%** | 0.002 | 71.4% | 28.6% | 0.0% | 0.4% | 28.6% | 0.0% | 70.5% | 0.4% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | **28.2%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 7 | 45 | stranger / mayor / poor_record / poor / woman_old | **25.6%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 8 | 60 | stranger / citizen / poor_record / rich / man_old | **22.2%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **19.7%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | **19.7%** | 0.002 | 82.5% | 17.5% | 0.0% | 0.4% | 19.7% | 0.0% | 79.5% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | **0.4%** | 0.002 | 99.6% | 0.4% | 0.0% | 0.4% | 0.4% | 0.0% | 98.7% | 0.4% |
| 2 | 56 | stranger / citizen / good_record / poor / man_old | **0.9%** | 0.006 | 99.1% | 0.9% | 0.0% | 1.3% | 0.9% | 0.0% | 97.0% | 0.9% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | **0.9%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 0.9% | 0.0% | 97.4% | 0.9% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | **0.9%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 5 | 33 | stranger / mayor / good_record / rich / woman_old | **1.3%** | 0.009 | 99.1% | 0.9% | 0.0% | 1.7% | 1.3% | 0.0% | 97.0% | 0.0% |
| 6 | 51 | stranger / citizen / good_record / rich / woman_young | **1.3%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.3% | 0.0% | 97.9% | 0.0% |
| 7 | 22 | close_friend / citizen / good_record / poor / man_young | **1.3%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 98.3% | 0.0% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | **1.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.3% | 0.0% | 98.3% | 0.4% |
| 9 | 39 | stranger / mayor / good_record / poor / woman_young | **1.3%** | 0.006 | 99.6% | 0.4% | 0.0% | 1.3% | 1.3% | 0.0% | 97.0% | 0.4% |
| 10 | 19 | close_friend / citizen / good_record / rich / woman_young | **1.3%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.3% | 0.0% | 97.4% | 0.0% |


**CHECKED_TRUE (%)** *(Note: 60 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.4%** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 2 | 60 | stranger / citizen / poor_record / rich / man_old | **0.4%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | **0.4%** | 0.004 | 98.7% | 1.3% | 0.0% | 0.0% | 3.0% | 0.4% | 96.2% | 0.4% |
| 4 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.4%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.0% | 2.6% | 0.4% | 96.6% | 0.4% |
| 5 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 6 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 9 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 10 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | **0.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **0.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0%** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | **0.0%** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 9 | 64 | stranger / citizen / poor_record / poor / man_old | **0.0%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.011 | 85.9% | 14.1% | 0.0% | 2.1% | 16.7% | 0.0% | 80.8% | 0.4% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | **98.7%** | 0.002 | 99.6% | 0.4% | 0.0% | 0.4% | 0.4% | 0.0% | 98.7% | 0.4% |
| 2 | 52 | stranger / citizen / good_record / rich / man_old | **98.3%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 3 | 22 | close_friend / citizen / good_record / poor / man_young | **98.3%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 98.3% | 0.0% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | **98.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 98.3% | 0.0% |
| 5 | 24 | close_friend / citizen / good_record / poor / man_old | **98.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.3% | 0.0% | 98.3% | 0.4% |
| 6 | 49 | stranger / citizen / good_record / rich / woman_old | **98.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 98.3% | 0.0% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | **97.9%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **97.9%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.3% | 0.0% | 97.9% | 0.0% |
| 9 | 40 | stranger / mayor / good_record / poor / man_old | **97.9%** | 0.002 | 99.6% | 0.4% | 0.0% | 0.4% | 1.7% | 0.0% | 97.9% | 0.0% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | **97.4%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 0.9% | 0.0% | 97.4% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **54.7%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **58.5%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | **59.4%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **61.5%** | 0.004 | 64.5% | 35.5% | 0.0% | 0.9% | 37.2% | 0.0% | 61.5% | 0.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **67.5%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | **70.5%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **70.5%** | 0.002 | 71.4% | 28.6% | 0.0% | 0.4% | 28.6% | 0.0% | 70.5% | 0.4% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | **74.8%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **75.6%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **79.1%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 16 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | **1.3%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **1.3%** | 0.009 | 99.6% | 0.4% | 0.0% | 1.7% | 1.7% | 0.0% | 95.3% | 1.3% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | **1.3%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 2.6% | 0.0% | 95.3% | 1.3% |
| 4 | 2 | close_friend / mayor / good_record / rich / man_young | **1.3%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.7% | 0.0% | 96.6% | 1.3% |
| 5 | 9 | close_friend / mayor / poor_record / rich / woman_old | **1.3%** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 7.3% | 0.0% | 91.5% | 1.3% |
| 6 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.9%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 97.4% | 0.9% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.9%** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | **0.9%** | 0.006 | 84.6% | 15.4% | 0.0% | 1.3% | 17.2% | 0.0% | 80.7% | 0.9% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | **0.9%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 10 | 61 | stranger / citizen / poor_record / poor / woman_old | **0.9%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | **0.0%** | 0.009 | 99.1% | 0.9% | 0.0% | 1.7% | 1.3% | 0.0% | 97.0% | 0.0% |
| 3 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.0%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.3% | 0.0% | 97.4% | 0.0% |
| 4 | 8 | close_friend / mayor / good_record / poor / man_old | **0.0%** | 0.006 | 99.6% | 0.4% | 0.0% | 1.3% | 3.8% | 0.0% | 94.9% | 0.0% |
| 5 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.0%** | 0.004 | 95.7% | 4.3% | 0.0% | 0.9% | 6.4% | 0.0% | 92.7% | 0.0% |
| 6 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | **0.0%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.7% | 0.0% | 97.4% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.3% | 0.0% | 97.9% | 0.0% |
| 9 | 29 | close_friend / citizen / poor_record / poor / woman_old | **0.0%** | 0.002 | 95.3% | 4.7% | 0.0% | 0.4% | 8.1% | 0.0% | 91.5% | 0.0% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.0%** | 0.002 | 98.3% | 1.7% | 0.0% | 0.4% | 4.3% | 0.0% | 95.3% | 0.0% |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.0721** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |
| 2 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0717** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 3 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0664** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 4 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0625** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | **0.0610** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 6 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0594** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 7 | 50 | stranger / citizen / good_record / rich / man_young | **0.0591** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 8 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.0571** | 0.057 | 34.6% | 65.4% | 0.4% | 9.0% | 14.1% | 0.4% | 69.7% | 6.4% |
| 9 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.0561** | 0.056 | 35.5% | 64.5% | 0.4% | 9.1% | 16.4% | 0.4% | 69.8% | 3.9% |
| 10 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0558** | 0.056 | 33.3% | 66.7% | 1.3% | 7.8% | 12.6% | 0.0% | 71.4% | 6.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0111** | 0.011 | 26.5% | 73.5% | 0.0% | 1.3% | 20.5% | 0.4% | 73.9% | 3.8% |
| 2 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0112** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 3 | 42 | stranger / mayor / poor_record / rich / man_young | **0.0135** | 0.013 | 23.9% | 76.1% | 0.4% | 1.7% | 20.2% | 0.0% | 73.4% | 4.3% |
| 4 | 28 | close_friend / citizen / poor_record / rich / man_old | **0.0135** | 0.014 | 19.2% | 80.8% | 0.4% | 1.7% | 26.2% | 0.0% | 67.0% | 4.7% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | **0.0137** | 0.014 | 24.8% | 75.2% | 0.4% | 1.7% | 29.5% | 0.0% | 62.0% | 6.4% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | **0.0137** | 0.014 | 27.8% | 72.2% | 0.4% | 1.7% | 19.7% | 0.0% | 72.1% | 6.0% |
| 7 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.0140** | 0.014 | 19.2% | 80.8% | 0.0% | 2.6% | 19.3% | 0.0% | 70.4% | 7.7% |
| 8 | 32 | close_friend / citizen / poor_record / poor / man_old | **0.0156** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | **0.0158** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |
| 10 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.0161** | 0.016 | 20.1% | 79.9% | 0.4% | 0.4% | 24.5% | 0.9% | 67.4% | 6.4% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 29 | close_friend / citizen / poor_record / poor / woman_old | **83.8%** | 0.023 | 16.2% | 83.8% | 0.9% | 2.6% | 23.1% | 0.0% | 67.5% | 6.0% |
| 2 | 15 | close_friend / mayor / poor_record / poor / woman_young | **82.9%** | 0.038 | 17.1% | 82.9% | 1.7% | 3.0% | 17.1% | 0.4% | 72.2% | 5.6% |
| 3 | 9 | close_friend / mayor / poor_record / rich / woman_old | **82.9%** | 0.019 | 17.1% | 82.9% | 0.4% | 1.7% | 25.1% | 0.4% | 64.1% | 8.2% |
| 4 | 16 | close_friend / mayor / poor_record / poor / man_old | **82.5%** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 5 | 31 | close_friend / citizen / poor_record / poor / woman_young | **82.1%** | 0.022 | 17.9% | 82.1% | 0.4% | 2.6% | 22.6% | 0.4% | 71.4% | 2.6% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | **81.2%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 7 | 10 | close_friend / mayor / poor_record / rich / man_young | **80.8%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 8 | 25 | close_friend / citizen / poor_record / rich / woman_old | **80.8%** | 0.031 | 19.2% | 80.8% | 1.3% | 2.6% | 27.8% | 0.4% | 63.7% | 4.3% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | **80.8%** | 0.018 | 19.2% | 80.8% | 0.4% | 2.6% | 25.8% | 0.0% | 67.4% | 3.9% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **80.8%** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **56.8%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | **58.1%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | **59.0%** | 0.032 | 41.0% | 59.0% | 0.9% | 4.3% | 12.5% | 0.0% | 75.4% | 6.9% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | **59.4%** | 0.043 | 40.6% | 59.4% | 0.9% | 6.5% | 12.5% | 0.0% | 75.4% | 4.7% |
| 5 | 6 | close_friend / mayor / good_record / poor / man_young | **60.7%** | 0.044 | 39.3% | 60.7% | 0.9% | 6.9% | 14.6% | 0.0% | 74.2% | 3.4% |
| 6 | 34 | stranger / mayor / good_record / rich / man_young | **61.1%** | 0.045 | 38.9% | 61.1% | 0.4% | 7.8% | 10.8% | 0.0% | 76.2% | 4.8% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | **61.5%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |
| 8 | 5 | close_friend / mayor / good_record / poor / woman_old | **62.4%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | **62.4%** | 0.037 | 37.6% | 62.4% | 0.4% | 6.0% | 11.6% | 0.0% | 75.9% | 6.0% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | **62.8%** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27 | close_friend / citizen / poor_record / rich / woman_young | **2.6%** | 0.041 | 21.8% | 78.2% | 2.6% | 1.7% | 19.0% | 0.4% | 71.1% | 5.2% |
| 2 | 12 | close_friend / mayor / poor_record / rich / man_old | **2.6%** | 0.039 | 21.4% | 78.6% | 2.6% | 1.3% | 24.9% | 0.4% | 65.2% | 5.6% |
| 3 | 10 | close_friend / mayor / poor_record / rich / man_young | **2.1%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | **1.7%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 5 | 56 | stranger / citizen / good_record / poor / man_old | **1.7%** | 0.046 | 27.4% | 72.6% | 1.7% | 5.2% | 12.6% | 0.0% | 74.0% | 6.5% |
| 6 | 4 | close_friend / mayor / good_record / rich / man_old | **1.7%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 7 | 54 | stranger / citizen / good_record / poor / man_young | **1.7%** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | **1.7%** | 0.051 | 35.9% | 64.1% | 1.7% | 6.5% | 18.1% | 0.0% | 70.3% | 3.4% |
| 9 | 50 | stranger / citizen / good_record / rich / man_young | **1.7%** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 10 | 2 | close_friend / mayor / good_record / rich / man_young | **1.7%** | 0.039 | 35.9% | 64.1% | 1.7% | 3.9% | 18.9% | 0.0% | 70.0% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | **0.0%** | 0.042 | 31.2% | 68.8% | 0.0% | 7.7% | 15.8% | 0.0% | 67.1% | 9.4% |
| 2 | 22 | close_friend / citizen / good_record / poor / man_young | **0.0%** | 0.034 | 36.3% | 63.7% | 0.0% | 6.5% | 15.1% | 0.0% | 74.6% | 3.9% |
| 3 | 46 | stranger / mayor / poor_record / poor / man_young | **0.0%** | 0.020 | 25.2% | 74.8% | 0.0% | 3.9% | 28.3% | 0.0% | 63.9% | 3.9% |
| 4 | 59 | stranger / citizen / poor_record / rich / woman_young | **0.0%** | 0.014 | 19.2% | 80.8% | 0.0% | 2.6% | 19.3% | 0.0% | 70.4% | 7.7% |
| 5 | 16 | close_friend / mayor / poor_record / poor / man_old | **0.0%** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 6 | 43 | stranger / mayor / poor_record / rich / woman_young | **0.0%** | 0.011 | 26.5% | 73.5% | 0.0% | 1.3% | 20.5% | 0.4% | 73.9% | 3.8% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | **0.4%** | 0.057 | 34.6% | 65.4% | 0.4% | 9.0% | 14.1% | 0.4% | 69.7% | 6.4% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | **0.4%** | 0.050 | 33.8% | 66.2% | 0.4% | 8.5% | 13.7% | 0.0% | 70.9% | 6.4% |
| 9 | 7 | close_friend / mayor / good_record / poor / woman_young | **0.4%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 10 | 19 | close_friend / citizen / good_record / rich / woman_young | **0.4%** | 0.039 | 34.6% | 65.4% | 0.4% | 6.4% | 14.1% | 0.0% | 71.8% | 7.3% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **11.3%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | **10.9%** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | **10.3%** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | **9.6%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 5 | 17 | close_friend / citizen / good_record / rich / woman_old | **9.1%** | 0.056 | 35.5% | 64.5% | 0.4% | 9.1% | 16.4% | 0.4% | 69.8% | 3.9% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | **9.0%** | 0.057 | 34.6% | 65.4% | 0.4% | 9.0% | 14.1% | 0.4% | 69.7% | 6.4% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | **8.6%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | **8.6%** | 0.054 | 34.2% | 65.8% | 0.9% | 8.6% | 15.9% | 0.0% | 70.4% | 4.3% |
| 9 | 33 | stranger / mayor / good_record / rich / woman_old | **8.5%** | 0.050 | 33.8% | 66.2% | 0.4% | 8.5% | 13.7% | 0.0% | 70.9% | 6.4% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | **8.2%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.4%** | 0.016 | 20.1% | 79.9% | 0.4% | 0.4% | 24.5% | 0.9% | 67.4% | 6.4% |
| 2 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.9%** | 0.022 | 20.5% | 79.5% | 0.9% | 0.9% | 26.1% | 0.9% | 68.4% | 3.0% |
| 3 | 30 | close_friend / citizen / poor_record / poor / man_young | **0.9%** | 0.023 | 20.1% | 79.9% | 1.7% | 0.9% | 26.2% | 0.0% | 65.2% | 6.0% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | **1.3%** | 0.024 | 28.6% | 71.4% | 1.7% | 1.3% | 17.5% | 0.0% | 76.5% | 3.0% |
| 5 | 48 | stranger / mayor / poor_record / poor / man_old | **1.3%** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | **1.3%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | **1.3%** | 0.011 | 26.5% | 73.5% | 0.0% | 1.3% | 20.5% | 0.4% | 73.9% | 3.8% |
| 8 | 12 | close_friend / mayor / poor_record / rich / man_old | **1.3%** | 0.039 | 21.4% | 78.6% | 2.6% | 1.3% | 24.9% | 0.4% | 65.2% | 5.6% |
| 9 | 16 | close_friend / mayor / poor_record / poor / man_old | **1.3%** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | **1.7%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **35.6%** | 0.018 | 23.9% | 76.1% | 0.4% | 2.6% | 35.6% | 0.0% | 56.2% | 5.2% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | **32.1%** | 0.018 | 23.5% | 76.5% | 0.9% | 1.7% | 32.1% | 0.0% | 61.5% | 3.8% |
| 3 | 45 | stranger / mayor / poor_record / poor / woman_old | **31.2%** | 0.022 | 22.2% | 77.8% | 0.4% | 2.6% | 31.2% | 0.4% | 60.7% | 4.7% |
| 4 | 32 | close_friend / citizen / poor_record / poor / man_old | **30.8%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | **29.5%** | 0.014 | 24.8% | 75.2% | 0.4% | 1.7% | 29.5% | 0.0% | 62.0% | 6.4% |
| 6 | 13 | close_friend / mayor / poor_record / poor / woman_old | **28.6%** | 0.018 | 21.8% | 78.2% | 0.4% | 1.7% | 28.6% | 0.4% | 62.8% | 6.1% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | **28.3%** | 0.020 | 25.2% | 74.8% | 0.0% | 3.9% | 28.3% | 0.0% | 63.9% | 3.9% |
| 8 | 61 | stranger / citizen / poor_record / poor / woman_old | **28.3%** | 0.018 | 29.1% | 70.9% | 0.9% | 1.7% | 28.3% | 0.0% | 63.5% | 5.6% |
| 9 | 25 | close_friend / citizen / poor_record / rich / woman_old | **27.8%** | 0.031 | 19.2% | 80.8% | 1.3% | 2.6% | 27.8% | 0.4% | 63.7% | 4.3% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | **27.8%** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **9.5%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 2 | 4 | close_friend / mayor / good_record / rich / man_old | **10.3%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | **10.8%** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **10.8%** | 0.045 | 38.9% | 61.1% | 0.4% | 7.8% | 10.8% | 0.0% | 76.2% | 4.8% |
| 5 | 38 | stranger / mayor / good_record / poor / man_young | **11.2%** | 0.050 | 34.6% | 65.4% | 0.9% | 7.8% | 11.2% | 0.0% | 74.6% | 5.6% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | **11.6%** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | **11.6%** | 0.037 | 37.6% | 62.4% | 0.4% | 6.0% | 11.6% | 0.0% | 75.9% | 6.0% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | **12.0%** | 0.055 | 34.6% | 65.4% | 1.7% | 6.4% | 12.0% | 0.4% | 76.1% | 3.4% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | **12.1%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | **12.5%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |


**CHECKED_TRUE (%)** *(Note: 45 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | **0.9%** | 0.016 | 20.1% | 79.9% | 0.4% | 0.4% | 24.5% | 0.9% | 67.4% | 6.4% |
| 2 | 10 | close_friend / mayor / poor_record / rich / man_young | **0.9%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 3 | 26 | close_friend / citizen / poor_record / rich / man_young | **0.9%** | 0.022 | 20.5% | 79.5% | 0.9% | 0.9% | 26.1% | 0.9% | 68.4% | 3.0% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | **0.4%** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |
| 5 | 9 | close_friend / mayor / poor_record / rich / woman_old | **0.4%** | 0.019 | 17.1% | 82.9% | 0.4% | 1.7% | 25.1% | 0.4% | 64.1% | 8.2% |
| 6 | 13 | close_friend / mayor / poor_record / poor / woman_old | **0.4%** | 0.018 | 21.8% | 78.2% | 0.4% | 1.7% | 28.6% | 0.4% | 62.8% | 6.1% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | **0.4%** | 0.056 | 35.5% | 64.5% | 0.4% | 9.1% | 16.4% | 0.4% | 69.8% | 3.9% |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | **0.4%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 9 | 27 | close_friend / citizen / poor_record / rich / woman_young | **0.4%** | 0.041 | 21.8% | 78.2% | 2.6% | 1.7% | 19.0% | 0.4% | 71.1% | 5.2% |
| 10 | 12 | close_friend / mayor / poor_record / rich / man_old | **0.4%** | 0.039 | 21.4% | 78.6% | 2.6% | 1.3% | 24.9% | 0.4% | 65.2% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | **0.0%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 2 | 3 | close_friend / mayor / good_record / rich / woman_young | **0.0%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | **0.0%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 4 | 54 | stranger / citizen / good_record / poor / man_young | **0.0%** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | **0.0%** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | **0.0%** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 7 | 37 | stranger / mayor / good_record / poor / woman_old | **0.0%** | 0.056 | 33.3% | 66.7% | 1.3% | 7.8% | 12.6% | 0.0% | 71.4% | 6.9% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | **0.0%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |
| 9 | 39 | stranger / mayor / good_record / poor / woman_young | **0.0%** | 0.054 | 34.2% | 65.8% | 0.9% | 8.6% | 15.9% | 0.0% | 70.4% | 4.3% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | **0.0%** | 0.051 | 35.9% | 64.1% | 1.7% | 6.5% | 18.1% | 0.0% | 70.3% | 3.4% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | **78.0%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | **76.5%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 3 | 11 | close_friend / mayor / poor_record / rich / woman_young | **76.5%** | 0.024 | 28.6% | 71.4% | 1.7% | 1.3% | 17.5% | 0.0% | 76.5% | 3.0% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | **76.2%** | 0.045 | 38.9% | 61.1% | 0.4% | 7.8% | 10.8% | 0.0% | 76.2% | 4.8% |
| 5 | 36 | stranger / mayor / good_record / rich / man_old | **76.1%** | 0.055 | 34.6% | 65.4% | 1.7% | 6.4% | 12.0% | 0.4% | 76.1% | 3.4% |
| 6 | 4 | close_friend / mayor / good_record / rich / man_old | **75.9%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | **75.9%** | 0.037 | 37.6% | 62.4% | 0.4% | 6.0% | 11.6% | 0.0% | 75.9% | 6.0% |
| 8 | 1 | close_friend / mayor / good_record / rich / woman_old | **75.4%** | 0.043 | 40.6% | 59.4% | 0.9% | 6.5% | 12.5% | 0.0% | 75.4% | 4.7% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | **75.4%** | 0.032 | 41.0% | 59.0% | 0.9% | 4.3% | 12.5% | 0.0% | 75.4% | 6.9% |
| 10 | 38 | stranger / mayor / good_record / poor / man_young | **74.6%** | 0.050 | 34.6% | 65.4% | 0.9% | 7.8% | 11.2% | 0.0% | 74.6% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | **56.2%** | 0.018 | 23.9% | 76.1% | 0.4% | 2.6% | 35.6% | 0.0% | 56.2% | 5.2% |
| 2 | 45 | stranger / mayor / poor_record / poor / woman_old | **60.7%** | 0.022 | 22.2% | 77.8% | 0.4% | 2.6% | 31.2% | 0.4% | 60.7% | 4.7% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | **61.5%** | 0.018 | 23.5% | 76.5% | 0.9% | 1.7% | 32.1% | 0.0% | 61.5% | 3.8% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | **62.0%** | 0.014 | 24.8% | 75.2% | 0.4% | 1.7% | 29.5% | 0.0% | 62.0% | 6.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | **62.4%** | 0.030 | 24.4% | 75.6% | 0.9% | 3.8% | 26.5% | 0.0% | 62.4% | 6.4% |
| 6 | 13 | close_friend / mayor / poor_record / poor / woman_old | **62.8%** | 0.018 | 21.8% | 78.2% | 0.4% | 1.7% | 28.6% | 0.4% | 62.8% | 6.1% |
| 7 | 32 | close_friend / citizen / poor_record / poor / man_old | **62.8%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 8 | 61 | stranger / citizen / poor_record / poor / woman_old | **63.5%** | 0.018 | 29.1% | 70.9% | 0.9% | 1.7% | 28.3% | 0.0% | 63.5% | 5.6% |
| 9 | 25 | close_friend / citizen / poor_record / rich / woman_old | **63.7%** | 0.031 | 19.2% | 80.8% | 1.3% | 2.6% | 27.8% | 0.4% | 63.7% | 4.3% |
| 10 | 46 | stranger / mayor / poor_record / poor / man_young | **63.9%** | 0.020 | 25.2% | 74.8% | 0.0% | 3.9% | 28.3% | 0.0% | 63.9% | 3.9% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 54 | stranger / citizen / good_record / poor / man_young | **11.6%** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | **10.3%** | 0.045 | 29.1% | 70.9% | 0.4% | 7.3% | 13.3% | 0.0% | 68.7% | 10.3% |
| 3 | 35 | stranger / mayor / good_record / rich / woman_young | **9.4%** | 0.042 | 31.2% | 68.8% | 0.0% | 7.7% | 15.8% | 0.0% | 67.1% | 9.4% |
| 4 | 9 | close_friend / mayor / poor_record / rich / woman_old | **8.2%** | 0.019 | 17.1% | 82.9% | 0.4% | 1.7% | 25.1% | 0.4% | 64.1% | 8.2% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | **8.2%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |
| 6 | 40 | stranger / mayor / good_record / poor / man_old | **7.8%** | 0.038 | 32.1% | 67.9% | 0.9% | 5.2% | 12.6% | 0.0% | 73.5% | 7.8% |
| 7 | 59 | stranger / citizen / poor_record / rich / woman_young | **7.7%** | 0.014 | 19.2% | 80.8% | 0.0% | 2.6% | 19.3% | 0.0% | 70.4% | 7.7% |
| 8 | 19 | close_friend / citizen / good_record / rich / woman_young | **7.3%** | 0.039 | 34.6% | 65.4% | 0.4% | 6.4% | 14.1% | 0.0% | 71.8% | 7.3% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | **7.3%** | 0.021 | 26.5% | 73.5% | 0.4% | 2.1% | 23.5% | 0.4% | 66.2% | 7.3% |
| 10 | 37 | stranger / mayor / good_record / poor / woman_old | **6.9%** | 0.056 | 33.3% | 66.7% | 1.3% | 7.8% | 12.6% | 0.0% | 71.4% | 6.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | **1.7%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | **2.1%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | **2.2%** | 0.040 | 33.8% | 66.2% | 0.4% | 6.9% | 16.8% | 0.0% | 73.7% | 2.2% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | **2.6%** | 0.022 | 17.9% | 82.1% | 0.4% | 2.6% | 22.6% | 0.4% | 71.4% | 2.6% |
| 5 | 10 | close_friend / mayor / poor_record / rich / man_young | **3.0%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 6 | 11 | close_friend / mayor / poor_record / rich / woman_young | **3.0%** | 0.024 | 28.6% | 71.4% | 1.7% | 1.3% | 17.5% | 0.0% | 76.5% | 3.0% |
| 7 | 26 | close_friend / citizen / poor_record / rich / man_young | **3.0%** | 0.022 | 20.5% | 79.5% | 0.9% | 0.9% | 26.1% | 0.9% | 68.4% | 3.0% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | **3.4%** | 0.055 | 34.6% | 65.4% | 1.7% | 6.4% | 12.0% | 0.4% | 76.1% | 3.4% |
| 9 | 6 | close_friend / mayor / good_record / poor / man_young | **3.4%** | 0.044 | 39.3% | 60.7% | 0.9% | 6.9% | 14.6% | 0.0% | 74.2% | 3.4% |
| 10 | 4 | close_friend / mayor / good_record / rich / man_old | **3.4%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
