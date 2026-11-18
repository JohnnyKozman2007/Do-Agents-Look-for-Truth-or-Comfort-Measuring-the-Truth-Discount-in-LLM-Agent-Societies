# Rumor Towns Report (False Claims)

**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Condition:** `rumor` | **Towns:** 4,992 (2,496 per model) | **Expected Listeners:** 59,904

### Methodological & Missingness Disclosure
- **Excluded Invalid Judgments:** 189 / 59,904 (0.32%) had `judgment_status = invalid`. They are **completely excluded** (`NaN`), never turned into zeros.
- **Three Dynamic Denominators (Never Hardcoded):** `Expected N` = all listeners in slice (used for `GO %`/`SKIP %`); `Valid N` = `Expected N - Invalid` (used for all 6 label `%` and `Silence=0.0/0.5`); `Mentioned N` = `Valid N - NOT_MENTIONED` (used for primary conditional `Belief`).
- **Verification (`GO`/`SKIP`):** 0 missing or invalid decisions. 50 simulation decisions (24 first-hand, 26 second-hand; 0.08%) were `malformed_fallback_skip` in the simulation runner and appear as `SKIP`.
- **Statistical Model (Section 3):** 10-term OLS / Linear Probability Model (`6 main knobs + 4 interactions + real_artist`) with standard errors clustered by town (`run_id`), two-sided Wald z-tests, and Holm adjustment across all 10 planned contrasts per outcome. `Belief` also reports the spec's REML LMM (`1 | run_id`) companion check.

---

## 1. Overall Categorical & Behavioral Summary

*Estimator: Descriptive Means (`Belief` over `Mentioned N`; `Silence=0.0/0.5` over `Valid N`) & Shares (`GO/SKIP` over `Expected N`; 6 Labels over `Valid N`).*

### Table A: Per-Model Summary (First-Hand, Second-Hand, and Overall)

| Model | Layer | Towns | Expected N | Valid N | Invalid (n / %) | Mentioned N | Belief (0-1 Mean) | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | First-Hand (Seats 1-6) | 2,496 | 14,976 | 14,931 | 45 (0.3%) | 14,836 | 0.091 | 0.091 | 0.094 | 48.3% | 51.7% | 0.3% | 16.0% | 35.4% | 0.7% | 46.9% | 0.6% | 100.0% | 71.8% |
| DeepSeek-V4-Flash | Second-Hand (Seats 7-12) | 2,496 | 14,976 | 14,917 | 59 (0.4%) | 13,620 | 0.023 | 0.021 | 0.065 | 62.0% | 38.0% | 0.2% | 3.8% | 22.5% | 0.0% | 64.8% | 8.7% | — | — |
| DeepSeek-V4-Flash | Overall (All 12 Listeners) | 2,496 | 29,952 | 29,848 | 104 (0.3%) | 28,456 | 0.059 | 0.056 | 0.079 | 55.2% | 44.8% | 0.3% | 9.9% | 28.9% | 0.4% | 55.8% | 4.7% | 100.0% | 71.8% |
| Qwen3.8-Flash | First-Hand (Seats 1-6) | 2,496 | 14,976 | 14,967 | 9 (0.1%) | 14,894 | 0.005 | 0.005 | 0.008 | 92.8% | 7.2% | 0.0% | 0.9% | 8.5% | 0.0% | 90.0% | 0.5% | 95.9% | 60.4% |
| Qwen3.8-Flash | Second-Hand (Seats 7-12) | 2,496 | 14,976 | 14,900 | 76 (0.5%) | 14,101 | 0.036 | 0.034 | 0.061 | 28.6% | 71.4% | 0.9% | 4.7% | 19.1% | 0.1% | 69.8% | 5.4% | — | — |
| Qwen3.8-Flash | Overall (All 12 Listeners) | 2,496 | 29,952 | 29,867 | 85 (0.3%) | 28,995 | 0.020 | 0.020 | 0.034 | 60.7% | 39.3% | 0.5% | 2.8% | 13.8% | 0.1% | 79.9% | 2.9% | 95.9% | 60.4% |

### Table B: Entire Experiment Average (Both Models Combined)

| Scope | Layer | Towns | Expected N | Valid N | Invalid (n / %) | Mentioned N | Belief (0-1 Mean) | Sil=0.0 | Sil=0.5 | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % | Trans % | Evid Trans % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Both Models Combined | First-Hand (Seats 1-6) | 4,992 | 29,952 | 29,898 | 54 (0.2%) | 29,730 | 0.048 | 0.048 | 0.051 | 70.5% | 29.5% | 0.2% | 8.5% | 21.9% | 0.4% | 68.5% | 0.6% | 97.9% | 64.3% |
| Both Models Combined | Second-Hand (Seats 7-12) | 4,992 | 29,952 | 29,817 | 135 (0.5%) | 27,721 | 0.030 | 0.028 | 0.063 | 45.3% | 54.7% | 0.5% | 4.2% | 20.8% | 0.1% | 67.3% | 7.0% | — | — |
| Both Models Combined | Overall (All 12 Listeners) | 4,992 | 59,904 | 59,715 | 189 (0.3%) | 57,451 | 0.039 | 0.038 | 0.057 | 57.9% | 42.1% | 0.4% | 6.4% | 21.4% | 0.2% | 67.9% | 3.8% | 97.9% | 64.3% |

---

## 2. Gatekeeper & Downstream Susceptibility (`Seat i <-> Seat i+6`)

*Estimator: Descriptive Means & Shares of Second-Hand Listeners (Seats 7-12) grouped by paired First-Hand Partner decision (`GO` vs `SKIP`). No hypothesis test.*

| Model | First-Hand Partner | Pairs (n / share) | SH Valid N | SH Mentioned N | SH GO % | SH Belief | SH FACT % | SH UNCERTAIN % | SH SKEPTICAL % | SH CHECKED_TRUE % | SH CHECKED_FALSE % | SH NOT_MENTIONED % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash | ALL | 14,976 (100.0%) | 14,917 | 13,620 | 62.0% | 0.023 | 0.2% | 3.8% | 22.5% | 0.0% | 64.8% | 8.7% |
| DeepSeek-V4-Flash | GO | 7,229 (48.3%) | 7,192 | 6,117 | 59.4% | 0.028 | 0.3% | 4.0% | 11.0% | 0.1% | 69.7% | 14.9% |
| DeepSeek-V4-Flash | SKIP | 7,747 (51.7%) | 7,725 | 7,503 | 64.5% | 0.020 | 0.1% | 3.6% | 33.2% | 0.0% | 60.2% | 2.9% |
| Qwen3.8-Flash | ALL | 14,976 (100.0%) | 14,900 | 14,101 | 28.6% | 0.036 | 0.9% | 4.7% | 19.1% | 0.1% | 69.8% | 5.4% |
| Qwen3.8-Flash | GO | 13,896 (92.8%) | 13,820 | 13,053 | 26.3% | 0.038 | 0.9% | 4.9% | 17.7% | 0.2% | 70.8% | 5.5% |
| Qwen3.8-Flash | SKIP | 1,080 (7.2%) | 1,080 | 1,048 | 58.1% | 0.013 | 0.1% | 2.4% | 37.4% | 0.0% | 57.1% | 3.0% |
| Both Models Combined | ALL | 29,952 (100.0%) | 29,817 | 27,721 | 45.3% | 0.030 | 0.5% | 4.2% | 20.8% | 0.1% | 67.3% | 7.0% |
| Both Models Combined | GO | 21,125 (70.5%) | 21,012 | 19,170 | 37.6% | 0.034 | 0.7% | 4.6% | 15.4% | 0.1% | 70.4% | 8.8% |
| Both Models Combined | SKIP | 8,827 (29.5%) | 8,805 | 8,551 | 63.7% | 0.019 | 0.1% | 3.4% | 33.7% | 0.0% | 59.9% | 2.9% |

---

## 3. Controlled Effects: 6 Main Knobs + 4 Planned Interactions (Town-Clustered)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=28,456, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0600 | 0.0587 | +0.0014 | [-0.0025, +0.0052] | 0.4847 | 0.9772 | +0.0014 (p=0.4944) |
| main | authority | `mayor - citizen` | 0.0651 | 0.0536 | +0.0114*** | [+0.0076, +0.0153] | <0.0001 | <0.0001 | +0.0114 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.0767 | 0.0420 | +0.0347*** | [+0.0308, +0.0385] | <0.0001 | <0.0001 | +0.0347 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0571 | 0.0616 | -0.0045 | [-0.0084, -0.0006] | 0.0230 | 0.1612 | -0.0045 (p=0.0263) |
| main | gender | `woman - man` | 0.0603 | 0.0584 | +0.0019 | [-0.0019, +0.0057] | 0.3257 | 0.9772 | +0.0019 (p=0.3418) |
| main | age | `old - young` | 0.0580 | 0.0607 | -0.0027 | [-0.0066, +0.0011] | 0.1591 | 0.7957 | -0.0027 (p=0.1735) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0101 | +0.0129 | -0.0230*** | [-0.0307, -0.0153] | <0.0001 | <0.0001 | -0.0230 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0156 | +0.0073 | +0.0083 | [+0.0006, +0.0161] | 0.0346 | 0.2078 | +0.0083 (p=0.0388) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0057 | -0.0033 | -0.0024 | [-0.0102, +0.0053] | 0.5366 | 0.9772 | -0.0024 (p=0.5458) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0038 | -0.0011 | +0.0049 | [-0.0028, +0.0125] | 0.2104 | 0.8415 | +0.0049 (p=0.2259) |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=6,890, 624 towns) = **0.0716** [0.0672, 0.0760] | `close_friend + poor_record` (n=7,319, 624 towns) = **0.0484** [0.0453, 0.0516] | `stranger + good_record` (n=6,884, 624 towns) = **0.0817** [0.0770, 0.0865] | `stranger + poor_record` (n=7,363, 624 towns) = **0.0356** [0.0327, 0.0385]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,319 / 7,363 | +0.0129*** | [+0.0086, +0.0172] | <0.0001 |
| `closeness effect | reliability=good_record` | 6,890 / 6,884 | -0.0101** | [-0.0166, -0.0037] | 0.0021 |
| `reliability effect | closeness=stranger` | 6,884 / 7,363 | +0.0462*** | [+0.0406, +0.0517] | <0.0001 |
| `reliability effect | closeness=close_friend` | 6,890 / 7,319 | +0.0232*** | [+0.0178, +0.0286] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=6,886, 624 towns) = **0.0845** [0.0797, 0.0892] | `mayor + poor_record` (n=7,335, 624 towns) = **0.0456** [0.0425, 0.0488] | `citizen + good_record` (n=6,888, 624 towns) = **0.0689** [0.0645, 0.0733] | `citizen + poor_record` (n=7,347, 624 towns) = **0.0384** [0.0355, 0.0413]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,335 / 7,347 | +0.0073*** | [+0.0030, +0.0115] | 0.0009 |
| `authority effect | reliability=good_record` | 6,886 / 6,888 | +0.0156*** | [+0.0091, +0.0220] | <0.0001 |
| `reliability effect | authority=citizen` | 6,888 / 7,347 | +0.0305*** | [+0.0252, +0.0357] | <0.0001 |
| `reliability effect | authority=mayor` | 6,886 / 7,335 | +0.0388*** | [+0.0332, +0.0445] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=6,906, 624 towns) = **0.0738** [0.0692, 0.0784] | `rich + poor_record` (n=7,333, 624 towns) = **0.0404** [0.0375, 0.0432] | `poor + good_record` (n=6,868, 624 towns) = **0.0795** [0.0750, 0.0840] | `poor + poor_record` (n=7,349, 624 towns) = **0.0436** [0.0405, 0.0468]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,333 / 7,349 | -0.0033 | [-0.0075, +0.0010] | 0.1342 |
| `wealth effect | reliability=good_record` | 6,906 / 6,868 | -0.0057 | [-0.0122, +0.0007] | 0.0829 |
| `reliability effect | wealth=poor` | 6,868 / 7,349 | +0.0359*** | [+0.0304, +0.0414] | <0.0001 |
| `reliability effect | wealth=rich` | 6,906 / 7,333 | +0.0334*** | [+0.0280, +0.0389] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,098, 624 towns) = **0.0670** [0.0630, 0.0709] | `close_friend + citizen` (n=7,111, 624 towns) = **0.0531** [0.0494, 0.0568] | `stranger + mayor` (n=7,123, 624 towns) = **0.0631** [0.0591, 0.0672] | `stranger + citizen` (n=7,124, 624 towns) = **0.0542** [0.0505, 0.0579]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,111 / 7,124 | -0.0011 | [-0.0063, +0.0042] | 0.6895 |
| `closeness effect | authority=mayor` | 7,098 / 7,123 | +0.0038 | [-0.0018, +0.0095] | 0.1849 |
| `authority effect | closeness=stranger` | 7,123 / 7,124 | +0.0090** | [+0.0035, +0.0145] | 0.0014 |
| `authority effect | closeness=close_friend` | 7,098 / 7,111 | +0.0139*** | [+0.0085, +0.0192] | <0.0001 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0568 | 0.0553 | +0.0015 | [-0.0022, +0.0051] | 0.4357 | 1.0000 | +0.0015 (p=0.4491) |
| main | authority | `mayor - citizen` | 0.0614 | 0.0507 | +0.0106*** | [+0.0069, +0.0143] | <0.0001 | <0.0001 | +0.0106 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.0708 | 0.0413 | +0.0296*** | [+0.0259, +0.0333] | <0.0001 | <0.0001 | +0.0296 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0540 | 0.0581 | -0.0040 | [-0.0077, -0.0003] | 0.0324 | 0.2265 | -0.0040 (p=0.0377) |
| main | gender | `woman - man` | 0.0570 | 0.0551 | +0.0020 | [-0.0017, +0.0056] | 0.2936 | 1.0000 | +0.0020 (p=0.3077) |
| main | age | `old - young` | 0.0549 | 0.0572 | -0.0023 | [-0.0060, +0.0014] | 0.2244 | 1.0000 | -0.0023 (p=0.2382) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0094 | +0.0123 | -0.0217*** | [-0.0291, -0.0144] | <0.0001 | <0.0001 | -0.0217 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0142 | +0.0071 | +0.0071 | [-0.0002, +0.0145] | 0.0580 | 0.3479 | +0.0071 (p=0.0656) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0048 | -0.0032 | -0.0016 | [-0.0089, +0.0058] | 0.6788 | 1.0000 | -0.0016 (p=0.6876) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0038 | -0.0009 | +0.0048 | [-0.0026, +0.0121] | 0.2040 | 1.0000 | +0.0048 (p=0.2176) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0812 | 0.0776 | +0.0036 | [-0.0005, +0.0076] | 0.0875 | 0.3501 | +0.0036 (p=0.1039) |
| main | authority | `mayor - citizen` | 0.0851 | 0.0736 | +0.0115*** | [+0.0074, +0.0156] | <0.0001 | <0.0001 | +0.0115 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.1088 | 0.0499 | +0.0589*** | [+0.0548, +0.0630] | <0.0001 | <0.0001 | +0.0589 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0768 | 0.0820 | -0.0051 | [-0.0092, -0.0011] | 0.0135 | 0.0947 | -0.0051 (p=0.0188) |
| main | gender | `woman - man` | 0.0799 | 0.0788 | +0.0011 | [-0.0030, +0.0052] | 0.5971 | 0.6833 | +0.0011 (p=0.6146) |
| main | age | `old - young` | 0.0771 | 0.0816 | -0.0045 | [-0.0086, -0.0004] | 0.0303 | 0.1815 | -0.0045 (p=0.0393) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0088 | +0.0159 | -0.0246*** | [-0.0328, -0.0165] | <0.0001 | <0.0001 | -0.0246 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0155 | +0.0075 | +0.0080 | [-0.0002, +0.0161] | 0.0560 | 0.2800 | +0.0080 (p=0.0690) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0076 | -0.0026 | -0.0050 | [-0.0132, +0.0031] | 0.2278 | 0.6833 | -0.0050 (p=0.2510) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0058 | +0.0013 | +0.0046 | [-0.0036, +0.0127] | 0.2726 | 0.6833 | +0.0046 (p=0.2966) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 58.99% | 51.31% | +7.69 pp*** | [+6.85, +8.52 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 55.70% | 54.60% | +1.10 pp** | [+0.27, +1.93 pp] | 0.0094 | 0.0094 |
| main | reliability | `good_record - poor_record` | 73.73% | 36.57% | +37.16 pp*** | [+36.33, +37.99 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 56.46% | 53.84% | +2.62 pp*** | [+1.79, +3.46 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 55.78% | 54.52% | +1.26 pp** | [+0.43, +2.09 pp] | 0.0030 | 0.0060 |
| main | age | `old - young` | 54.41% | 55.90% | -1.49 pp** | [-2.32, -0.66 pp] | 0.0004 | 0.0013 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +2.46 pp | +12.91 pp | -10.46 pp*** | [-12.12, -8.79 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.50 pp | +3.70 pp | -5.19 pp*** | [-6.86, -3.53 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.64 pp | +4.61 pp | -3.97 pp*** | [-5.63, -2.30 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +6.12 pp | +9.25 pp | -3.14 pp*** | [-4.80, -1.48 pp] | 0.0002 | 0.0009 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,488, 624 towns) = **74.96%** [74.19, 75.73%] | `close_friend + poor_record` (n=7,488, 624 towns) = **43.03%** [42.14, 43.92%] | `stranger + good_record` (n=7,488, 624 towns) = **72.50%** [71.73, 73.28%] | `stranger + poor_record` (n=7,488, 624 towns) = **30.11%** [29.23, 31.00%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,488 / 7,488 | +12.91 pp*** | [+11.66, +14.17 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,488 / 7,488 | +2.46 pp*** | [+1.37, +3.55 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 7,488 / 7,488 | +42.39 pp*** | [+41.21, +43.57 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,488 / 7,488 | +31.93 pp*** | [+30.76, +33.10 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,488, 624 towns) = **72.98%** [72.23, 73.74%] | `mayor + poor_record` (n=7,488, 624 towns) = **38.42%** [37.54, 39.30%] | `citizen + good_record` (n=7,488, 624 towns) = **74.48%** [73.69, 75.27%] | `citizen + poor_record` (n=7,488, 624 towns) = **34.72%** [33.82, 35.62%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,488 / 7,488 | +3.70 pp*** | [+2.44, +4.96 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 7,488 / 7,488 | -1.50 pp** | [-2.59, -0.41 pp] | 0.0072 |
| `reliability effect | authority=citizen` | 7,488 / 7,488 | +39.76 pp*** | [+38.56, +40.95 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,488 / 7,488 | +34.56 pp*** | [+33.41, +35.72 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,488, 624 towns) = **74.05%** [73.28, 74.82%] | `rich + poor_record` (n=7,488, 624 towns) = **38.88%** [37.98, 39.77%] | `poor + good_record` (n=7,488, 624 towns) = **73.41%** [72.64, 74.18%] | `poor + poor_record` (n=7,488, 624 towns) = **34.27%** [33.39, 35.15%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,488 / 7,488 | +4.61 pp*** | [+3.35, +5.86 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 7,488 / 7,488 | +0.64 pp | [-0.45, +1.73 pp] | 0.2491 |
| `reliability effect | wealth=poor` | 7,488 / 7,488 | +39.14 pp*** | [+37.97, +40.32 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,488 / 7,488 | +35.18 pp*** | [+34.00, +36.35 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,488, 624 towns) = **58.76%** [57.95, 59.57%] | `close_friend + citizen` (n=7,488, 624 towns) = **59.23%** [58.38, 60.08%] | `stranger + mayor` (n=7,488, 624 towns) = **52.64%** [51.82, 53.47%] | `stranger + citizen` (n=7,488, 624 towns) = **49.97%** [49.13, 50.81%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,488 / 7,488 | +9.25 pp*** | [+8.06, +10.45 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 7,488 / 7,488 | +6.12 pp*** | [+4.96, +7.27 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 7,488 / 7,488 | +2.67 pp*** | [+1.49, +3.85 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 7,488 / 7,488 | -0.47 pp | [-1.64, +0.70 pp] | 0.4343 |


**Outcome: NOT_MENTIONED (%)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 4.88% | 4.46% | +0.42 pp | [-0.04, +0.88 pp] | 0.0735 | 0.5877 |
| main | authority | `mayor - citizen` | 4.76% | 4.58% | +0.18 pp | [-0.28, +0.64 pp] | 0.4430 | 1.0000 |
| main | reliability | `good_record - poor_record` | 7.60% | 1.73% | +5.87 pp*** | [+5.41, +6.33 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 4.55% | 4.78% | -0.22 pp | [-0.68, +0.23 pp] | 0.3363 | 1.0000 |
| main | gender | `woman - man` | 4.58% | 4.75% | -0.17 pp | [-0.63, +0.28 pp] | 0.4568 | 1.0000 |
| main | age | `old - young` | 4.44% | 4.89% | -0.45 pp | [-0.90, +0.01 pp] | 0.0565 | 0.5089 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.13 pp | +0.71 pp | -0.58 pp | [-1.49, +0.34 pp] | 0.2173 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.26 pp | +0.10 pp | +0.17 pp | [-0.75, +1.08 pp] | 0.7194 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.57 pp | +0.12 pp | -0.69 pp | [-1.61, +0.22 pp] | 0.1384 | 0.9685 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.40 pp | +0.44 pp | -0.04 pp | [-0.96, +0.88 pp] | 0.9320 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,462, 624 towns) = **7.67%** [7.08, 8.25%] | `close_friend + poor_record` (n=7,475, 624 towns) = **2.09%** [1.77, 2.41%] | `stranger + good_record` (n=7,445, 624 towns) = **7.54%** [6.96, 8.11%] | `stranger + poor_record` (n=7,466, 624 towns) = **1.38%** [1.12, 1.64%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,475 / 7,466 | +0.71 pp*** | [+0.29, +1.12 pp] | 0.0008 |
| `closeness effect | reliability=good_record` | 7,462 / 7,445 | +0.13 pp | [-0.69, +0.95 pp] | 0.7555 |
| `reliability effect | closeness=stranger` | 7,445 / 7,466 | +6.16 pp*** | [+5.52, +6.79 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,462 / 7,475 | +5.58 pp*** | [+4.92, +6.24 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,463, 624 towns) = **7.73%** [7.17, 8.29%] | `mayor + poor_record` (n=7,468, 624 towns) = **1.78%** [1.49, 2.07%] | `citizen + good_record` (n=7,444, 624 towns) = **7.47%** [6.87, 8.07%] | `citizen + poor_record` (n=7,473, 624 towns) = **1.69%** [1.40, 1.97%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,468 / 7,473 | +0.10 pp | [-0.32, +0.51 pp] | 0.6503 |
| `authority effect | reliability=good_record` | 7,463 / 7,444 | +0.26 pp | [-0.56, +1.08 pp] | 0.5283 |
| `reliability effect | authority=citizen` | 7,444 / 7,473 | +5.78 pp*** | [+5.12, +6.45 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,463 / 7,468 | +5.95 pp*** | [+5.32, +6.58 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,451, 624 towns) = **7.31%** [6.74, 7.89%] | `rich + poor_record` (n=7,467, 624 towns) = **1.79%** [1.49, 2.10%] | `poor + good_record` (n=7,456, 624 towns) = **7.89%** [7.30, 8.47%] | `poor + poor_record` (n=7,474, 624 towns) = **1.67%** [1.39, 1.95%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,467 / 7,474 | +0.12 pp | [-0.29, +0.53 pp] | 0.5630 |
| `wealth effect | reliability=good_record` | 7,451 / 7,456 | -0.57 pp | [-1.39, +0.25 pp] | 0.1713 |
| `reliability effect | wealth=poor` | 7,456 / 7,474 | +6.21 pp*** | [+5.57, +6.86 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,451 / 7,467 | +5.52 pp*** | [+4.87, +6.17 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,468, 624 towns) = **4.96%** [4.50, 5.41%] | `close_friend + citizen` (n=7,469, 624 towns) = **4.80%** [4.31, 5.28%] | `stranger + mayor` (n=7,463, 624 towns) = **4.56%** [4.11, 5.00%] | `stranger + citizen` (n=7,448, 624 towns) = **4.36%** [3.91, 4.81%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,469 / 7,448 | +0.44 pp | [-0.22, +1.10 pp] | 0.1948 |
| `closeness effect | authority=mayor` | 7,468 / 7,463 | +0.40 pp | [-0.23, +1.03 pp] | 0.2169 |
| `authority effect | closeness=stranger` | 7,463 / 7,448 | +0.20 pp | [-0.43, +0.83 pp] | 0.5368 |
| `authority effect | closeness=close_friend` | 7,468 / 7,469 | +0.16 pp | [-0.50, +0.82 pp] | 0.6374 |


**Outcome: FACT (%)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.31% | 0.20% | +0.11 pp | [+0.00, +0.23 pp] | 0.0496 | 0.3839 |
| main | authority | `mayor - citizen` | 0.31% | 0.21% | +0.10 pp | [-0.01, +0.21 pp] | 0.0836 | 0.5014 |
| main | reliability | `good_record - poor_record` | 0.49% | 0.03% | +0.46 pp*** | [+0.35, +0.58 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.30% | 0.22% | +0.07 pp | [-0.04, +0.19 pp] | 0.2007 | 1.0000 |
| main | gender | `woman - man` | 0.32% | 0.20% | +0.11 pp | [+0.00, +0.23 pp] | 0.0480 | 0.3839 |
| main | age | `old - young` | 0.29% | 0.23% | +0.06 pp | [-0.05, +0.17 pp] | 0.2970 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.17 pp | +0.05 pp | +0.12 pp | [-0.11, +0.35 pp] | 0.3000 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.17 pp | +0.03 pp | +0.15 pp | [-0.08, +0.37 pp] | 0.2050 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.09 pp | +0.05 pp | +0.04 pp | [-0.19, +0.27 pp] | 0.7263 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.24 pp | -0.01 pp | +0.26 pp | [+0.03, +0.48 pp] | 0.0270 | 0.2428 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,462, 624 towns) = **0.58%** [0.41, 0.74%] | `close_friend + poor_record` (n=7,475, 624 towns) = **0.05%** [0.00, 0.11%] | `stranger + good_record` (n=7,445, 624 towns) = **0.40%** [0.26, 0.55%] | `stranger + poor_record` (n=7,466, 624 towns) = **0.00%** [-0.01, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,475 / 7,466 | +0.05 pp* | [+0.00, +0.11 pp] | 0.0473 |
| `closeness effect | reliability=good_record` | 7,462 / 7,445 | +0.17 pp | [-0.05, +0.39 pp] | 0.1229 |
| `reliability effect | closeness=stranger` | 7,445 / 7,466 | +0.40 pp*** | [+0.26, +0.55 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,462 / 7,475 | +0.52 pp*** | [+0.35, +0.70 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,463, 624 towns) = **0.58%** [0.41, 0.75%] | `mayor + poor_record` (n=7,468, 624 towns) = **0.04%** [-0.01, 0.09%] | `citizen + good_record` (n=7,444, 624 towns) = **0.40%** [0.26, 0.54%] | `citizen + poor_record` (n=7,473, 624 towns) = **0.01%** [-0.01, 0.04%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,468 / 7,473 | +0.03 pp | [-0.03, +0.08 pp] | 0.3224 |
| `authority effect | reliability=good_record` | 7,463 / 7,444 | +0.17 pp | [-0.05, +0.39 pp] | 0.1232 |
| `reliability effect | authority=citizen` | 7,444 / 7,473 | +0.39 pp*** | [+0.25, +0.53 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,463 / 7,468 | +0.54 pp*** | [+0.36, +0.71 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,451, 624 towns) = **0.54%** [0.38, 0.70%] | `rich + poor_record` (n=7,467, 624 towns) = **0.05%** [0.00, 0.11%] | `poor + good_record` (n=7,456, 624 towns) = **0.44%** [0.29, 0.59%] | `poor + poor_record` (n=7,474, 624 towns) = **-0.00%** [-0.01, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,467 / 7,474 | +0.05 pp* | [+0.00, +0.11 pp] | 0.0469 |
| `wealth effect | reliability=good_record` | 7,451 / 7,456 | +0.09 pp | [-0.13, +0.31 pp] | 0.4020 |
| `reliability effect | wealth=poor` | 7,456 / 7,474 | +0.44 pp*** | [+0.29, +0.59 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,451 / 7,467 | +0.48 pp*** | [+0.31, +0.65 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,468, 624 towns) = **0.43%** [0.29, 0.57%] | `close_friend + citizen` (n=7,469, 624 towns) = **0.20%** [0.10, 0.30%] | `stranger + mayor` (n=7,463, 624 towns) = **0.19%** [0.08, 0.29%] | `stranger + citizen` (n=7,448, 624 towns) = **0.22%** [0.11, 0.32%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,469 / 7,448 | -0.01 pp | [-0.16, +0.13 pp] | 0.8455 |
| `closeness effect | authority=mayor` | 7,468 / 7,463 | +0.24 pp** | [+0.07, +0.42 pp] | 0.0071 |
| `authority effect | closeness=stranger` | 7,463 / 7,448 | -0.03 pp | [-0.17, +0.12 pp] | 0.7089 |
| `authority effect | closeness=close_friend` | 7,468 / 7,469 | +0.23 pp* | [+0.05, +0.40 pp] | 0.0101 |


**Outcome: UNCERTAIN (%)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 9.87% | 9.96% | -0.09 pp | [-0.76, +0.57 pp] | 0.7808 | 1.0000 |
| main | authority | `mayor - citizen` | 10.74% | 9.09% | +1.66 pp*** | [+0.99, +2.32 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 11.66% | 8.17% | +3.49 pp*** | [+2.83, +4.15 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 9.45% | 10.38% | -0.92 pp* | [-1.58, -0.26 pp] | 0.0062 | 0.0431 |
| main | gender | `woman - man` | 10.00% | 9.84% | +0.16 pp | [-0.50, +0.82 pp] | 0.6344 | 1.0000 |
| main | age | `old - young` | 9.87% | 9.96% | -0.09 pp | [-0.75, +0.57 pp] | 0.7832 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -2.55 pp | +2.36 pp | -4.91 pp*** | [-6.23, -3.58 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.90 pp | +1.41 pp | +0.49 pp | [-0.83, +1.81 pp] | 0.4685 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -1.09 pp | -0.75 pp | -0.34 pp | [-1.66, +0.98 pp] | 0.6158 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.18 pp | -0.37 pp | +0.55 pp | [-0.77, +1.87 pp] | 0.4169 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,462, 624 towns) = **10.39%** [9.70, 11.07%] | `close_friend + poor_record` (n=7,475, 624 towns) = **9.35%** [8.74, 9.96%] | `stranger + good_record` (n=7,445, 624 towns) = **12.93%** [12.17, 13.70%] | `stranger + poor_record` (n=7,466, 624 towns) = **6.99%** [6.42, 7.56%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,475 / 7,466 | +2.36 pp*** | [+1.52, +3.20 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,462 / 7,445 | -2.55 pp*** | [-3.57, -1.52 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 7,445 / 7,466 | +5.94 pp*** | [+4.99, +6.89 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,462 / 7,475 | +1.03 pp* | [+0.12, +1.95 pp] | 0.0272 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,463, 624 towns) = **12.61%** [11.88, 13.34%] | `mayor + poor_record` (n=7,468, 624 towns) = **8.88%** [8.26, 9.49%] | `citizen + good_record` (n=7,444, 624 towns) = **10.71%** [9.99, 11.43%] | `citizen + poor_record` (n=7,473, 624 towns) = **7.47%** [6.90, 8.03%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,468 / 7,473 | +1.41 pp*** | [+0.58, +2.25 pp] | 0.0009 |
| `authority effect | reliability=good_record` | 7,463 / 7,444 | +1.90 pp*** | [+0.88, +2.92 pp] | 0.0003 |
| `reliability effect | authority=citizen` | 7,444 / 7,473 | +3.24 pp*** | [+2.33, +4.16 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,463 / 7,468 | +3.73 pp*** | [+2.78, +4.69 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,451, 624 towns) = **11.11%** [10.41, 11.82%] | `rich + poor_record` (n=7,467, 624 towns) = **7.79%** [7.24, 8.35%] | `poor + good_record` (n=7,456, 624 towns) = **12.21%** [11.46, 12.95%] | `poor + poor_record` (n=7,474, 624 towns) = **8.55%** [7.92, 9.18%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,467 / 7,474 | -0.75 pp | [-1.59, +0.08 pp] | 0.0768 |
| `wealth effect | reliability=good_record` | 7,451 / 7,456 | -1.09 pp* | [-2.12, -0.07 pp] | 0.0365 |
| `reliability effect | wealth=poor` | 7,456 / 7,474 | +3.66 pp*** | [+2.68, +4.63 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,451 / 7,467 | +3.32 pp*** | [+2.42, +4.21 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,468, 624 towns) = **10.83%** [10.17, 11.49%] | `close_friend + citizen` (n=7,469, 624 towns) = **8.90%** [8.27, 9.54%] | `stranger + mayor` (n=7,463, 624 towns) = **10.65%** [9.96, 11.34%] | `stranger + citizen` (n=7,448, 624 towns) = **9.27%** [8.62, 9.93%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,469 / 7,448 | -0.37 pp | [-1.28, +0.55 pp] | 0.4304 |
| `closeness effect | authority=mayor` | 7,468 / 7,463 | +0.18 pp | [-0.78, +1.14 pp] | 0.7121 |
| `authority effect | closeness=stranger` | 7,463 / 7,448 | +1.38 pp** | [+0.43, +2.33 pp] | 0.0044 |
| `authority effect | closeness=close_friend` | 7,468 / 7,469 | +1.93 pp*** | [+1.01, +2.85 pp] | <0.0001 |


**Outcome: SKEPTICAL (%)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 24.56% | 33.26% | -8.70 pp*** | [-9.56, -7.84 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 27.75% | 30.06% | -2.31 pp*** | [-3.17, -1.45 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 6.08% | 51.73% | -45.65 pp*** | [-46.51, -44.79 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 27.61% | 30.21% | -2.60 pp*** | [-3.46, -1.74 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 28.53% | 29.29% | -0.76 pp | [-1.62, +0.10 pp] | 0.0828 | 0.0828 |
| main | age | `old - young` | 29.81% | 28.01% | +1.80 pp*** | [+0.95, +2.66 pp] | <0.0001 | 0.0001 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.86 pp | -18.25 pp | +19.11 pp*** | [+17.40, +20.83 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.13 pp | -4.75 pp | +4.88 pp*** | [+3.16, +6.59 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.17 pp | -5.03 pp | +4.86 pp*** | [+3.14, +6.58 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -7.00 pp | -10.40 pp | +3.40 pp*** | [+1.68, +5.11 pp] | 0.0001 | 0.0002 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,462, 624 towns) = **6.51%** [5.98, 7.05%] | `close_friend + poor_record` (n=7,475, 624 towns) = **42.61%** [41.52, 43.70%] | `stranger + good_record` (n=7,445, 624 towns) = **5.65%** [5.14, 6.17%] | `stranger + poor_record` (n=7,466, 624 towns) = **60.86%** [59.76, 61.96%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,475 / 7,466 | -18.25 pp*** | [-19.80, -16.71 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,462 / 7,445 | +0.86 pp* | [+0.12, +1.60 pp] | 0.0236 |
| `reliability effect | closeness=stranger` | 7,445 / 7,466 | -55.21 pp*** | [-56.42, -53.99 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,462 / 7,475 | -36.09 pp*** | [-37.31, -34.88 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,463, 624 towns) = **6.15%** [5.63, 6.67%] | `mayor + poor_record` (n=7,468, 624 towns) = **49.36%** [48.25, 50.47%] | `citizen + good_record` (n=7,444, 624 towns) = **6.02%** [5.49, 6.55%] | `citizen + poor_record` (n=7,473, 624 towns) = **54.11%** [53.03, 55.18%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,468 / 7,473 | -4.75 pp*** | [-6.30, -3.20 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 7,463 / 7,444 | +0.13 pp | [-0.61, +0.87 pp] | 0.7331 |
| `reliability effect | authority=citizen` | 7,444 / 7,473 | -48.09 pp*** | [-49.29, -46.89 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,463 / 7,468 | -43.21 pp*** | [-44.44, -41.98 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,451, 624 towns) = **6.00%** [5.47, 6.52%] | `rich + poor_record` (n=7,467, 624 towns) = **49.22%** [48.12, 50.32%] | `poor + good_record` (n=7,456, 624 towns) = **6.17%** [5.64, 6.69%] | `poor + poor_record` (n=7,474, 624 towns) = **54.25%** [53.16, 55.34%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,467 / 7,474 | -5.03 pp*** | [-6.58, -3.48 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 7,451 / 7,456 | -0.17 pp | [-0.91, +0.57 pp] | 0.6568 |
| `reliability effect | wealth=poor` | 7,456 / 7,474 | -48.08 pp*** | [-49.29, -46.87 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,451 / 7,467 | -43.22 pp*** | [-44.44, -42.00 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,468, 624 towns) = **24.25%** [23.38, 25.13%] | `close_friend + citizen` (n=7,469, 624 towns) = **24.87%** [24.02, 25.71%] | `stranger + mayor` (n=7,463, 624 towns) = **31.25%** [30.39, 32.12%] | `stranger + citizen` (n=7,448, 624 towns) = **35.26%** [34.41, 36.11%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,469 / 7,448 | -10.40 pp*** | [-11.60, -9.19 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 7,468 / 7,463 | -7.00 pp*** | [-8.23, -5.77 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 7,463 / 7,448 | -4.01 pp*** | [-5.22, -2.79 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 7,468 / 7,469 | -0.61 pp | [-1.83, +0.60 pp] | 0.3238 |


**Outcome: CHECKED_TRUE (%)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.43% | 0.35% | +0.08 pp | [-0.06, +0.22 pp] | 0.2788 | 1.0000 |
| main | authority | `mayor - citizen` | 0.46% | 0.32% | +0.13 pp | [-0.01, +0.28 pp] | 0.0700 | 0.4901 |
| main | reliability | `good_record - poor_record` | 0.76% | 0.01% | +0.75 pp*** | [+0.61, +0.90 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.38% | 0.40% | -0.01 pp | [-0.16, +0.13 pp] | 0.8562 | 1.0000 |
| main | gender | `woman - man` | 0.39% | 0.39% | +0.00 pp | [-0.14, +0.15 pp] | 0.9703 | 1.0000 |
| main | age | `old - young` | 0.27% | 0.51% | -0.24 pp** | [-0.39, -0.10 pp] | 0.0010 | 0.0092 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.16 pp | +0.00 pp | +0.16 pp | [-0.13, +0.45 pp] | 0.2789 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.29 pp | -0.03 pp | +0.32 pp | [+0.03, +0.61 pp] | 0.0296 | 0.2372 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.03 pp | -0.00 pp | -0.03 pp | [-0.32, +0.26 pp] | 0.8570 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.05 pp | +0.11 pp | -0.05 pp | [-0.34, +0.24 pp] | 0.7200 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,462, 624 towns) = **0.84%** [0.63, 1.06%] | `close_friend + poor_record` (n=7,475, 624 towns) = **0.01%** [-0.01, 0.04%] | `stranger + good_record` (n=7,445, 624 towns) = **0.68%** [0.50, 0.87%] | `stranger + poor_record` (n=7,466, 624 towns) = **0.01%** [-0.01, 0.04%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,475 / 7,466 | +0.00 pp | [-0.04, +0.04 pp] | 0.9989 |
| `closeness effect | reliability=good_record` | 7,462 / 7,445 | +0.16 pp | [-0.13, +0.45 pp] | 0.2743 |
| `reliability effect | closeness=stranger` | 7,445 / 7,466 | +0.67 pp*** | [+0.48, +0.86 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,462 / 7,475 | +0.83 pp*** | [+0.61, +1.05 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,463, 624 towns) = **0.91%** [0.69, 1.13%] | `mayor + poor_record` (n=7,468, 624 towns) = **-0.00%** [-0.01, 0.01%] | `citizen + good_record` (n=7,444, 624 towns) = **0.62%** [0.44, 0.80%] | `citizen + poor_record` (n=7,473, 624 towns) = **0.03%** [-0.01, 0.06%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,468 / 7,473 | -0.03 pp | [-0.07, +0.01 pp] | 0.1848 |
| `authority effect | reliability=good_record` | 7,463 / 7,444 | +0.29 pp* | [+0.01, +0.58 pp] | 0.0442 |
| `reliability effect | authority=citizen` | 7,444 / 7,473 | +0.59 pp*** | [+0.41, +0.77 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,463 / 7,468 | +0.91 pp*** | [+0.69, +1.13 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,451, 624 towns) = **0.75%** [0.55, 0.95%] | `rich + poor_record` (n=7,467, 624 towns) = **0.01%** [-0.01, 0.04%] | `poor + good_record` (n=7,456, 624 towns) = **0.78%** [0.57, 0.98%] | `poor + poor_record` (n=7,474, 624 towns) = **0.01%** [-0.01, 0.04%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,467 / 7,474 | -0.00 pp | [-0.04, +0.04 pp] | 0.9969 |
| `wealth effect | reliability=good_record` | 7,451 / 7,456 | -0.03 pp | [-0.31, +0.26 pp] | 0.8552 |
| `reliability effect | wealth=poor` | 7,456 / 7,474 | +0.76 pp*** | [+0.56, +0.97 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,451 / 7,467 | +0.74 pp*** | [+0.54, +0.94 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,468, 624 towns) = **0.48%** [0.32, 0.65%] | `close_friend + citizen` (n=7,469, 624 towns) = **0.38%** [0.23, 0.52%] | `stranger + mayor` (n=7,463, 624 towns) = **0.43%** [0.28, 0.58%] | `stranger + citizen` (n=7,448, 624 towns) = **0.27%** [0.15, 0.38%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,469 / 7,448 | +0.11 pp | [-0.08, +0.29 pp] | 0.2553 |
| `closeness effect | authority=mayor` | 7,468 / 7,463 | +0.05 pp | [-0.17, +0.28 pp] | 0.6392 |
| `authority effect | closeness=stranger` | 7,463 / 7,448 | +0.16 pp | [-0.03, +0.35 pp] | 0.0966 |
| `authority effect | closeness=close_friend` | 7,468 / 7,469 | +0.11 pp | [-0.11, +0.33 pp] | 0.3368 |


**Outcome: CHECKED_FALSE (%)** (n=29,848, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 59.95% | 51.77% | +8.18 pp*** | [+7.22, +9.14 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 55.98% | 55.74% | +0.24 pp | [-0.71, +1.20 pp] | 0.6209 | 0.6209 |
| main | reliability | `good_record - poor_record` | 73.40% | 38.32% | +35.08 pp*** | [+34.13, +36.04 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 57.71% | 54.02% | +3.69 pp*** | [+2.73, +4.64 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 56.19% | 55.53% | +0.66 pp | [-0.30, +1.61 pp] | 0.1770 | 0.3541 |
| main | age | `old - young` | 55.32% | 56.40% | -1.08 pp | [-2.04, -0.13 pp] | 0.0261 | 0.0784 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.23 pp | +15.13 pp | -13.91 pp*** | [-15.82, -12.00 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -2.76 pp | +3.24 pp | -6.00 pp*** | [-7.91, -4.09 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +1.77 pp | +5.61 pp | -3.84 pp*** | [-5.75, -1.93 pp] | <0.0001 | 0.0003 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +6.13 pp | +10.23 pp | -4.11 pp*** | [-6.02, -2.19 pp] | <0.0001 | 0.0001 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,462, 624 towns) = **74.02%** [73.13, 74.90%] | `close_friend + poor_record` (n=7,475, 624 towns) = **45.89%** [44.86, 46.92%] | `stranger + good_record` (n=7,445, 624 towns) = **72.79%** [71.86, 73.72%] | `stranger + poor_record` (n=7,466, 624 towns) = **30.75%** [29.79, 31.72%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,475 / 7,466 | +15.13 pp*** | [+13.72, +16.55 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,462 / 7,445 | +1.23 pp | [-0.06, +2.51 pp] | 0.0610 |
| `reliability effect | closeness=stranger` | 7,445 / 7,466 | +42.04 pp*** | [+40.69, +43.38 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,462 / 7,475 | +28.13 pp*** | [+26.77, +29.49 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,463, 624 towns) = **72.02%** [71.11, 72.94%] | `mayor + poor_record` (n=7,468, 624 towns) = **39.94%** [38.94, 40.94%] | `citizen + good_record` (n=7,444, 624 towns) = **74.78%** [73.88, 75.68%] | `citizen + poor_record` (n=7,473, 624 towns) = **36.70%** [35.70, 37.70%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,468 / 7,473 | +3.24 pp*** | [+1.82, +4.66 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 7,463 / 7,444 | -2.76 pp*** | [-4.04, -1.48 pp] | <0.0001 |
| `reliability effect | authority=citizen` | 7,444 / 7,473 | +38.08 pp*** | [+36.73, +39.43 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,463 / 7,468 | +32.08 pp*** | [+30.73, +33.44 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,451, 624 towns) = **74.29%** [73.38, 75.20%] | `rich + poor_record` (n=7,467, 624 towns) = **41.13%** [40.08, 42.17%] | `poor + good_record` (n=7,456, 624 towns) = **72.52%** [71.62, 73.42%] | `poor + poor_record` (n=7,474, 624 towns) = **35.52%** [34.56, 36.48%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,467 / 7,474 | +5.61 pp*** | [+4.19, +7.02 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 7,451 / 7,456 | +1.77 pp** | [+0.48, +3.05 pp] | 0.0070 |
| `reliability effect | wealth=poor` | 7,456 / 7,474 | +37.00 pp*** | [+35.68, +38.32 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,451 / 7,467 | +33.16 pp*** | [+31.78, +34.54 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,468, 624 towns) = **59.05%** [58.09, 60.00%] | `close_friend + citizen` (n=7,469, 624 towns) = **60.86%** [59.89, 61.83%] | `stranger + mayor` (n=7,463, 624 towns) = **52.92%** [51.95, 53.88%] | `stranger + citizen` (n=7,448, 624 towns) = **50.63%** [49.69, 51.56%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,469 / 7,448 | +10.23 pp*** | [+8.89, +11.58 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 7,468 / 7,463 | +6.13 pp*** | [+4.77, +7.48 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 7,463 / 7,448 | +2.29 pp*** | [+0.95, +3.64 pp] | 0.0008 |
| `authority effect | closeness=close_friend` | 7,468 / 7,469 | -1.81 pp** | [-3.17, -0.45 pp] | 0.0091 |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,836, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0916 | 0.0912 | +0.0004 | [-0.0062, +0.0071] | 0.8986 | 1.0000 | +0.0004 (p=0.8991) |
| main | authority | `mayor - citizen` | 0.1011 | 0.0818 | +0.0193*** | [+0.0127, +0.0260] | <0.0001 | <0.0001 | +0.0193 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.1145 | 0.0684 | +0.0461*** | [+0.0394, +0.0528] | <0.0001 | <0.0001 | +0.0461 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0859 | 0.0970 | -0.0111** | [-0.0177, -0.0044] | 0.0011 | 0.0078 | -0.0111 (p=0.0011) |
| main | gender | `woman - man` | 0.0927 | 0.0902 | +0.0025 | [-0.0041, +0.0091] | 0.4611 | 1.0000 | +0.0025 (p=0.4607) |
| main | age | `old - young` | 0.0899 | 0.0930 | -0.0031 | [-0.0098, +0.0035] | 0.3560 | 1.0000 | -0.0031 (p=0.3567) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0184 | +0.0193 | -0.0377*** | [-0.0510, -0.0244] | <0.0001 | <0.0001 | -0.0377 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0266 | +0.0121 | +0.0145 | [+0.0012, +0.0278] | 0.0327 | 0.1633 | +0.0145 (p=0.0328) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0187 | -0.0035 | -0.0152 | [-0.0285, -0.0019] | 0.0254 | 0.1521 | -0.0152 (p=0.0253) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0022 | -0.0013 | +0.0035 | [-0.0097, +0.0168] | 0.6019 | 1.0000 | +0.0035 (p=0.6013) |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,698, 624 towns) = **0.1053** [0.0976, 0.1129] | `close_friend + poor_record` (n=3,730, 624 towns) = **0.0780** [0.0723, 0.0837] | `stranger + good_record` (n=3,679, 624 towns) = **0.1237** [0.1159, 0.1315] | `stranger + poor_record` (n=3,729, 624 towns) = **0.0587** [0.0536, 0.0638]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,730 / 3,729 | +0.0193*** | [+0.0116, +0.0269] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,698 / 3,679 | -0.0184*** | [-0.0293, -0.0075] | 0.0009 |
| `reliability effect | closeness=stranger` | 3,679 / 3,729 | +0.0650*** | [+0.0556, +0.0743] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,698 / 3,730 | +0.0272*** | [+0.0177, +0.0367] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,696, 624 towns) = **0.1278** [0.1197, 0.1359] | `mayor + poor_record` (n=3,729, 624 towns) = **0.0744** [0.0688, 0.0800] | `citizen + good_record` (n=3,681, 624 towns) = **0.1012** [0.0939, 0.1085] | `citizen + poor_record` (n=3,730, 624 towns) = **0.0623** [0.0571, 0.0675]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,729 / 3,730 | +0.0121** | [+0.0044, +0.0197] | 0.0019 |
| `authority effect | reliability=good_record` | 3,696 / 3,681 | +0.0266*** | [+0.0157, +0.0375] | <0.0001 |
| `reliability effect | authority=citizen` | 3,681 / 3,730 | +0.0388*** | [+0.0299, +0.0478] | <0.0001 |
| `reliability effect | authority=mayor` | 3,696 / 3,729 | +0.0533*** | [+0.0435, +0.0632] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,688, 624 towns) = **0.1051** [0.0977, 0.1126] | `rich + poor_record` (n=3,729, 624 towns) = **0.0666** [0.0614, 0.0718] | `poor + good_record` (n=3,689, 624 towns) = **0.1238** [0.1158, 0.1317] | `poor + poor_record` (n=3,730, 624 towns) = **0.0701** [0.0645, 0.0757]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,729 / 3,730 | -0.0035 | [-0.0111, +0.0042] | 0.3729 |
| `wealth effect | reliability=good_record` | 3,688 / 3,689 | -0.0187*** | [-0.0296, -0.0078] | 0.0008 |
| `reliability effect | wealth=poor` | 3,689 / 3,730 | +0.0537*** | [+0.0440, +0.0634] | <0.0001 |
| `reliability effect | wealth=rich` | 3,688 / 3,729 | +0.0385*** | [+0.0294, +0.0476] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **0.1022** [0.0952, 0.1092] | `close_friend + citizen` (n=3,708, 624 towns) = **0.0811** [0.0746, 0.0875] | `stranger + mayor` (n=3,705, 624 towns) = **0.1000** [0.0930, 0.1069] | `stranger + citizen` (n=3,703, 624 towns) = **0.0824** [0.0762, 0.0886]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,708 / 3,703 | -0.0013 | [-0.0103, +0.0076] | 0.7698 |
| `closeness effect | authority=mayor` | 3,720 / 3,705 | +0.0022 | [-0.0076, +0.0120] | 0.6612 |
| `authority effect | closeness=stranger` | 3,705 / 3,703 | +0.0176*** | [+0.0083, +0.0269] | 0.0002 |
| `authority effect | closeness=close_friend` | 3,720 / 3,708 | +0.0211*** | [+0.0116, +0.0306] | <0.0001 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0910 | 0.0905 | +0.0005 | [-0.0061, +0.0072] | 0.8741 | 1.0000 | +0.0005 (p=0.8747) |
| main | authority | `mayor - citizen` | 0.1003 | 0.0812 | +0.0192*** | [+0.0126, +0.0258] | <0.0001 | <0.0001 | +0.0192 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.1133 | 0.0682 | +0.0451*** | [+0.0385, +0.0517] | <0.0001 | <0.0001 | +0.0451 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0853 | 0.0962 | -0.0109** | [-0.0175, -0.0043] | 0.0012 | 0.0086 | -0.0109 (p=0.0012) |
| main | gender | `woman - man` | 0.0921 | 0.0894 | +0.0027 | [-0.0039, +0.0093] | 0.4227 | 1.0000 | +0.0027 (p=0.4232) |
| main | age | `old - young` | 0.0892 | 0.0923 | -0.0032 | [-0.0098, +0.0035] | 0.3506 | 1.0000 | -0.0031 (p=0.3518) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0181 | +0.0192 | -0.0373*** | [-0.0505, -0.0240] | <0.0001 | <0.0001 | -0.0373 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0263 | +0.0120 | +0.0143 | [+0.0011, +0.0275] | 0.0344 | 0.1721 | +0.0143 (p=0.0346) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0183 | -0.0035 | -0.0148 | [-0.0280, -0.0015] | 0.0287 | 0.1721 | -0.0148 (p=0.0288) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0026 | -0.0015 | +0.0041 | [-0.0091, +0.0174] | 0.5410 | 1.0000 | +0.0041 (p=0.5414) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0943 | 0.0936 | +0.0007 | [-0.0059, +0.0074] | 0.8311 | 1.0000 | +0.0007 (p=0.8315) |
| main | authority | `mayor - citizen` | 0.1034 | 0.0844 | +0.0190*** | [+0.0123, +0.0256] | <0.0001 | <0.0001 | +0.0190 (p=<0.0001) |
| main | reliability | `good_record - poor_record` | 0.1185 | 0.0694 | +0.0491*** | [+0.0424, +0.0557] | <0.0001 | <0.0001 | +0.0491 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0885 | 0.0994 | -0.0109** | [-0.0175, -0.0042] | 0.0014 | 0.0095 | -0.0109 (p=0.0014) |
| main | gender | `woman - man` | 0.0947 | 0.0932 | +0.0015 | [-0.0051, +0.0082] | 0.6492 | 1.0000 | +0.0015 (p=0.6496) |
| main | age | `old - young` | 0.0925 | 0.0954 | -0.0029 | [-0.0096, +0.0037] | 0.3836 | 1.0000 | -0.0029 (p=0.3846) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0183 | +0.0197 | -0.0380*** | [-0.0512, -0.0247] | <0.0001 | <0.0001 | -0.0380 (p=<0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0259 | +0.0120 | +0.0139 | [+0.0006, +0.0271] | 0.0406 | 0.2032 | +0.0139 (p=0.0409) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0187 | -0.0030 | -0.0157 | [-0.0290, -0.0024] | 0.0204 | 0.1226 | -0.0157 (p=0.0206) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0015 | -0.0001 | +0.0016 | [-0.0117, +0.0149] | 0.8132 | 1.0000 | +0.0016 (p=0.8134) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 53.98% | 42.56% | +11.42 pp*** | [+10.13, +12.70 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 47.38% | 49.16% | -1.78 pp* | [-3.06, -0.49 pp] | 0.0067 | 0.0334 |
| main | reliability | `good_record - poor_record` | 76.43% | 20.11% | +56.32 pp*** | [+55.03, +57.60 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 50.68% | 45.86% | +4.82 pp*** | [+3.54, +6.10 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 48.44% | 48.11% | +0.33 pp | [-0.95, +1.61 pp] | 0.6138 | 0.6138 |
| main | age | `old - young` | 47.64% | 48.90% | -1.27 pp | [-2.55, +0.01 pp] | 0.0527 | 0.1581 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +4.46 pp | +18.38 pp | -13.92 pp*** | [-16.48, -11.35 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -4.46 pp | +0.91 pp | -5.37 pp*** | [-7.94, -2.80 pp] | <0.0001 | 0.0002 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +3.77 pp | +5.88 pp | -2.11 pp | [-4.68, +0.46 pp] | 0.1072 | 0.2144 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +9.67 pp | +13.17 pp | -3.50 pp* | [-6.07, -0.93 pp] | 0.0076 | 0.0334 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,744, 624 towns) = **78.66%** [77.36, 79.96%] | `close_friend + poor_record` (n=3,744, 624 towns) = **29.30%** [27.88, 30.72%] | `stranger + good_record` (n=3,744, 624 towns) = **74.20%** [72.78, 75.62%] | `stranger + poor_record` (n=3,744, 624 towns) = **10.92%** [9.98, 11.86%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,744 / 3,744 | +18.38 pp*** | [+16.68, +20.08 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,744 / 3,744 | +4.46 pp*** | [+2.54, +6.38 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 3,744 / 3,744 | +63.27 pp*** | [+61.57, +64.98 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,744 / 3,744 | +49.36 pp*** | [+47.44, +51.28 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,744, 624 towns) = **74.20%** [72.82, 75.58%] | `mayor + poor_record` (n=3,744, 624 towns) = **20.57%** [19.37, 21.76%] | `citizen + good_record` (n=3,744, 624 towns) = **78.66%** [77.31, 80.00%] | `citizen + poor_record` (n=3,744, 624 towns) = **19.66%** [18.45, 20.87%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,744 / 3,744 | +0.91 pp | [-0.79, +2.61 pp] | 0.2948 |
| `authority effect | reliability=good_record` | 3,744 / 3,744 | -4.46 pp*** | [-6.38, -2.54 pp] | <0.0001 |
| `reliability effect | authority=citizen` | 3,744 / 3,744 | +59.00 pp*** | [+57.19, +60.81 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,744 / 3,744 | +53.63 pp*** | [+51.81, +55.45 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,744, 624 towns) = **78.31%** [76.99, 79.63%] | `rich + poor_record` (n=3,744, 624 towns) = **23.05%** [21.77, 24.33%] | `poor + good_record` (n=3,744, 624 towns) = **74.55%** [73.15, 75.94%] | `poor + poor_record` (n=3,744, 624 towns) = **17.17%** [16.06, 18.29%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,744 / 3,744 | +5.88 pp*** | [+4.18, +7.58 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,744 / 3,744 | +3.77 pp*** | [+1.84, +5.69 pp] | 0.0001 |
| `reliability effect | wealth=poor` | 3,744 / 3,744 | +57.37 pp*** | [+55.58, +59.16 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,744 / 3,744 | +55.26 pp*** | [+53.42, +57.10 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,744, 624 towns) = **52.22%** [50.87, 53.56%] | `close_friend + citizen` (n=3,744, 624 towns) = **55.74%** [54.37, 57.11%] | `stranger + mayor` (n=3,744, 624 towns) = **42.55%** [41.32, 43.78%] | `stranger + citizen` (n=3,744, 624 towns) = **42.57%** [41.39, 43.76%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,744 / 3,744 | +13.17 pp*** | [+11.36, +14.98 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,744 / 3,744 | +9.67 pp*** | [+7.85, +11.49 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,744 / 3,744 | -0.03 pp | [-1.73, +1.68 pp] | 0.9755 |
| `authority effect | closeness=close_friend` | 3,744 / 3,744 | -3.53 pp*** | [-5.45, -1.61 pp] | 0.0003 |


**Outcome: NOT_MENTIONED (%)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.66% | 0.62% | +0.04 pp | [-0.21, +0.29 pp] | 0.7679 | 1.0000 |
| main | authority | `mayor - citizen` | 0.62% | 0.66% | -0.04 pp | [-0.29, +0.21 pp] | 0.7429 | 1.0000 |
| main | reliability | `good_record - poor_record` | 1.03% | 0.24% | +0.79 pp*** | [+0.54, +1.04 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.64% | 0.63% | +0.01 pp | [-0.23, +0.26 pp] | 0.9127 | 1.0000 |
| main | gender | `woman - man` | 0.52% | 0.75% | -0.23 pp | [-0.48, +0.01 pp] | 0.0654 | 0.5229 |
| main | age | `old - young` | 0.66% | 0.62% | +0.04 pp | [-0.21, +0.29 pp] | 0.7518 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.03 pp | +0.11 pp | -0.14 pp | [-0.64, +0.36 pp] | 0.5866 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.08 pp | +0.00 pp | -0.08 pp | [-0.58, +0.41 pp] | 0.7412 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.08 pp | +0.11 pp | -0.19 pp | [-0.68, +0.31 pp] | 0.4645 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.22 pp | +0.29 pp | -0.51 pp | [-1.00, -0.01 pp] | 0.0463 | 0.4164 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,736, 624 towns) = **1.02%** [0.70, 1.33%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.29%** [0.12, 0.47%] | `stranger + good_record` (n=3,718, 624 towns) = **1.05%** [0.73, 1.37%] | `stranger + poor_record` (n=3,736, 624 towns) = **0.19%** [0.05, 0.33%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,736 | +0.11 pp | [-0.12, +0.33 pp] | 0.3465 |
| `closeness effect | reliability=good_record` | 3,736 / 3,718 | -0.03 pp | [-0.48, +0.41 pp] | 0.8896 |
| `reliability effect | closeness=stranger` | 3,718 / 3,736 | +0.86 pp*** | [+0.51, +1.21 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,736 / 3,741 | +0.72 pp*** | [+0.37, +1.08 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,733, 624 towns) = **0.99%** [0.68, 1.30%] | `mayor + poor_record` (n=3,738, 624 towns) = **0.24%** [0.08, 0.40%] | `citizen + good_record` (n=3,721, 624 towns) = **1.07%** [0.75, 1.40%] | `citizen + poor_record` (n=3,739, 624 towns) = **0.24%** [0.08, 0.40%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,738 / 3,739 | +0.00 pp | [-0.22, +0.22 pp] | 0.9981 |
| `authority effect | reliability=good_record` | 3,733 / 3,721 | -0.08 pp | [-0.53, +0.36 pp] | 0.7131 |
| `reliability effect | authority=citizen` | 3,721 / 3,739 | +0.83 pp*** | [+0.48, +1.19 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,733 / 3,738 | +0.75 pp*** | [+0.40, +1.10 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,725, 624 towns) = **0.99%** [0.68, 1.30%] | `rich + poor_record` (n=3,740, 624 towns) = **0.29%** [0.12, 0.47%] | `poor + good_record` (n=3,729, 624 towns) = **1.07%** [0.75, 1.39%] | `poor + poor_record` (n=3,737, 624 towns) = **0.19%** [0.05, 0.33%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,740 / 3,737 | +0.11 pp | [-0.11, +0.33 pp] | 0.3450 |
| `wealth effect | reliability=good_record` | 3,725 / 3,729 | -0.08 pp | [-0.52, +0.37 pp] | 0.7284 |
| `reliability effect | wealth=poor` | 3,729 / 3,737 | +0.88 pp*** | [+0.54, +1.23 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,725 / 3,740 | +0.70 pp*** | [+0.34, +1.05 pp] | 0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,739, 624 towns) = **0.51%** [0.28, 0.73%] | `close_friend + citizen` (n=3,738, 624 towns) = **0.80%** [0.53, 1.08%] | `stranger + mayor` (n=3,732, 624 towns) = **0.72%** [0.46, 0.99%] | `stranger + citizen` (n=3,722, 624 towns) = **0.51%** [0.29, 0.74%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,738 / 3,722 | +0.29 pp | [-0.07, +0.65 pp] | 0.1112 |
| `closeness effect | authority=mayor` | 3,739 / 3,732 | -0.22 pp | [-0.56, +0.13 pp] | 0.2229 |
| `authority effect | closeness=stranger` | 3,732 / 3,722 | +0.21 pp | [-0.14, +0.56 pp] | 0.2324 |
| `authority effect | closeness=close_friend` | 3,739 / 3,738 | -0.29 pp | [-0.65, +0.06 pp] | 0.1059 |


**Outcome: FACT (%)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.40% | 0.24% | +0.16 pp | [-0.02, +0.34 pp] | 0.0851 | 0.4952 |
| main | authority | `mayor - citizen` | 0.43% | 0.21% | +0.21 pp | [+0.03, +0.40 pp] | 0.0212 | 0.1905 |
| main | reliability | `good_record - poor_record` | 0.63% | 0.01% | +0.62 pp*** | [+0.43, +0.80 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.29% | 0.35% | -0.05 pp | [-0.24, +0.13 pp] | 0.5637 | 0.7733 |
| main | gender | `woman - man` | 0.42% | 0.23% | +0.19 pp | [+0.01, +0.37 pp] | 0.0411 | 0.3292 |
| main | age | `old - young` | 0.40% | 0.24% | +0.16 pp | [-0.02, +0.34 pp] | 0.0832 | 0.4952 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.29 pp | +0.03 pp | +0.27 pp | [-0.10, +0.63 pp] | 0.1520 | 0.4952 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.40 pp | +0.03 pp | +0.37 pp | [+0.01, +0.74 pp] | 0.0438 | 0.3292 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.13 pp | +0.03 pp | -0.16 pp | [-0.52, +0.20 pp] | 0.3866 | 0.7733 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.32 pp | -0.00 pp | +0.32 pp | [-0.04, +0.68 pp] | 0.0825 | 0.4952 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,736, 624 towns) = **0.78%** [0.50, 1.05%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + good_record` (n=3,718, 624 towns) = **0.48%** [0.25, 0.72%] | `stranger + poor_record` (n=3,736, 624 towns) = **-0.00%** [-0.01, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,736 | +0.03 pp | [-0.03, +0.08 pp] | 0.3311 |
| `closeness effect | reliability=good_record` | 3,736 / 3,718 | +0.29 pp | [-0.07, +0.65 pp] | 0.1107 |
| `reliability effect | closeness=stranger` | 3,718 / 3,736 | +0.48 pp*** | [+0.25, +0.72 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,736 / 3,741 | +0.75 pp*** | [+0.47, +1.03 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,733, 624 towns) = **0.83%** [0.54, 1.12%] | `mayor + poor_record` (n=3,738, 624 towns) = **0.03%** [-0.03, 0.08%] | `citizen + good_record` (n=3,721, 624 towns) = **0.43%** [0.22, 0.64%] | `citizen + poor_record` (n=3,739, 624 towns) = **-0.00%** [-0.01, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,738 / 3,739 | +0.03 pp | [-0.03, +0.08 pp] | 0.3321 |
| `authority effect | reliability=good_record` | 3,733 / 3,721 | +0.40 pp* | [+0.04, +0.76 pp] | 0.0289 |
| `reliability effect | authority=citizen` | 3,721 / 3,739 | +0.43 pp*** | [+0.22, +0.64 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,733 / 3,738 | +0.80 pp*** | [+0.51, +1.10 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,725, 624 towns) = **0.56%** [0.33, 0.80%] | `rich + poor_record` (n=3,740, 624 towns) = **0.03%** [-0.03, 0.08%] | `poor + good_record` (n=3,729, 624 towns) = **0.70%** [0.43, 0.97%] | `poor + poor_record` (n=3,737, 624 towns) = **-0.00%** [-0.01, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,740 / 3,737 | +0.03 pp | [-0.03, +0.08 pp] | 0.3320 |
| `wealth effect | reliability=good_record` | 3,725 / 3,729 | -0.13 pp | [-0.49, +0.23 pp] | 0.4656 |
| `reliability effect | wealth=poor` | 3,729 / 3,737 | +0.70 pp*** | [+0.43, +0.97 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,725 / 3,740 | +0.54 pp*** | [+0.29, +0.78 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,739, 624 towns) = **0.59%** [0.35, 0.83%] | `close_friend + citizen` (n=3,738, 624 towns) = **0.21%** [0.07, 0.36%] | `stranger + mayor` (n=3,732, 624 towns) = **0.27%** [0.09, 0.45%] | `stranger + citizen` (n=3,722, 624 towns) = **0.22%** [0.07, 0.36%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,738 / 3,722 | -0.00 pp | [-0.21, +0.21 pp] | 0.9917 |
| `closeness effect | authority=mayor` | 3,739 / 3,732 | +0.32 pp* | [+0.02, +0.62 pp] | 0.0349 |
| `authority effect | closeness=stranger` | 3,732 / 3,722 | +0.05 pp | [-0.18, +0.29 pp] | 0.6544 |
| `authority effect | closeness=close_friend` | 3,739 / 3,738 | +0.37 pp** | [+0.10, +0.65 pp] | 0.0086 |


**Outcome: UNCERTAIN (%)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 15.79% | 16.27% | -0.47 pp | [-1.65, +0.70 pp] | 0.4303 | 1.0000 |
| main | authority | `mayor - citizen` | 17.44% | 14.62% | +2.82 pp*** | [+1.64, +4.00 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 18.50% | 13.56% | +4.94 pp*** | [+3.76, +6.12 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 15.02% | 17.04% | -2.02 pp** | [-3.20, -0.84 pp] | 0.0008 | 0.0054 |
| main | gender | `woman - man` | 16.08% | 15.98% | +0.10 pp | [-1.08, +1.28 pp] | 0.8708 | 1.0000 |
| main | age | `old - young` | 16.01% | 16.05% | -0.04 pp | [-1.22, +1.14 pp] | 0.9483 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -4.73 pp | +3.78 pp | -8.51 pp*** | [-10.87, -6.15 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +3.18 pp | +2.46 pp | +0.72 pp | [-1.64, +3.08 pp] | 0.5491 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -3.29 pp | -0.76 pp | -2.53 pp | [-4.89, -0.17 pp] | 0.0356 | 0.2137 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.23 pp | -0.72 pp | +0.50 pp | [-1.86, +2.86 pp] | 0.6786 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,736, 624 towns) = **16.14%** [14.91, 17.36%] | `close_friend + poor_record` (n=3,741, 624 towns) = **15.45%** [14.33, 16.57%] | `stranger + good_record` (n=3,718, 624 towns) = **20.87%** [19.54, 22.20%] | `stranger + poor_record` (n=3,736, 624 towns) = **11.67%** [10.65, 12.69%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,736 | +3.78 pp*** | [+2.27, +5.29 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,736 / 3,718 | -4.73 pp*** | [-6.54, -2.92 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 3,718 / 3,736 | +9.20 pp*** | [+7.52, +10.87 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,736 / 3,741 | +0.69 pp | [-0.97, +2.35 pp] | 0.4165 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,733, 624 towns) = **20.09%** [18.80, 21.39%] | `mayor + poor_record` (n=3,738, 624 towns) = **14.79%** [13.68, 15.90%] | `citizen + good_record` (n=3,721, 624 towns) = **16.91%** [15.65, 18.17%] | `citizen + poor_record` (n=3,739, 624 towns) = **12.33%** [11.30, 13.36%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,738 / 3,739 | +2.46 pp** | [+0.95, +3.98 pp] | 0.0014 |
| `authority effect | reliability=good_record` | 3,733 / 3,721 | +3.18 pp*** | [+1.38, +4.99 pp] | 0.0006 |
| `reliability effect | authority=citizen` | 3,721 / 3,739 | +4.58 pp*** | [+2.95, +6.21 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,733 / 3,738 | +5.30 pp*** | [+3.60, +7.01 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,725, 624 towns) = **16.86%** [15.65, 18.07%] | `rich + poor_record` (n=3,740, 624 towns) = **13.18%** [12.16, 14.20%] | `poor + good_record` (n=3,729, 624 towns) = **20.15%** [18.80, 21.49%] | `poor + poor_record` (n=3,737, 624 towns) = **13.94%** [12.83, 15.06%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,740 / 3,737 | -0.76 pp | [-2.27, +0.75 pp] | 0.3255 |
| `wealth effect | reliability=good_record` | 3,725 / 3,729 | -3.29 pp*** | [-5.09, -1.48 pp] | 0.0004 |
| `reliability effect | wealth=poor` | 3,729 / 3,737 | +6.21 pp*** | [+4.46, +7.95 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,725 / 3,740 | +3.68 pp*** | [+2.09, +5.26 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,739, 624 towns) = **17.33%** [16.13, 18.53%] | `close_friend + citizen` (n=3,738, 624 towns) = **14.26%** [13.11, 15.41%] | `stranger + mayor` (n=3,732, 624 towns) = **17.56%** [16.34, 18.77%] | `stranger + citizen` (n=3,722, 624 towns) = **14.98%** [13.83, 16.14%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,738 / 3,722 | -0.72 pp | [-2.35, +0.91 pp] | 0.3840 |
| `closeness effect | authority=mayor` | 3,739 / 3,732 | -0.23 pp | [-1.93, +1.48 pp] | 0.7957 |
| `authority effect | closeness=stranger` | 3,732 / 3,722 | +2.57 pp** | [+0.90, +4.25 pp] | 0.0026 |
| `authority effect | closeness=close_friend` | 3,739 / 3,738 | +3.07 pp*** | [+1.41, +4.73 pp] | 0.0003 |


**Outcome: SKEPTICAL (%)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 29.94% | 40.72% | -10.78 pp*** | [-11.92, -9.64 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 34.59% | 36.08% | -1.49 pp* | [-2.64, -0.35 pp] | 0.0102 | 0.0306 |
| main | reliability | `good_record - poor_record` | 4.49% | 66.17% | -61.68 pp*** | [-62.82, -60.54 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 34.05% | 36.62% | -2.57 pp*** | [-3.71, -1.42 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 35.05% | 35.62% | -0.57 pp | [-1.71, +0.58 pp] | 0.3302 | 0.3302 |
| main | age | `old - young` | 36.25% | 34.42% | +1.83 pp** | [+0.69, +2.98 pp] | 0.0016 | 0.0082 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.00 pp | -21.57 pp | +21.57 pp*** | [+19.29, +23.85 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.33 pp | -3.32 pp | +3.65 pp** | [+1.36, +5.93 pp] | 0.0017 | 0.0082 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.13 pp | -5.00 pp | +4.88 pp*** | [+2.59, +7.16 pp] | <0.0001 | 0.0002 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -9.30 pp | -12.26 pp | +2.96 pp* | [+0.68, +5.25 pp] | 0.0110 | 0.0306 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,736, 624 towns) = **4.50%** [3.81, 5.18%] | `close_friend + poor_record` (n=3,741, 624 towns) = **55.39%** [53.81, 56.97%] | `stranger + good_record` (n=3,718, 624 towns) = **4.49%** [3.80, 5.19%] | `stranger + poor_record` (n=3,736, 624 towns) = **76.95%** [75.63, 78.28%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,736 | -21.57 pp*** | [-23.63, -19.50 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,736 / 3,718 | +0.00 pp | [-0.97, +0.98 pp] | 0.9925 |
| `reliability effect | closeness=stranger` | 3,718 / 3,736 | -72.46 pp*** | [-73.96, -70.97 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,736 / 3,741 | -50.89 pp*** | [-52.62, -49.17 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,733, 624 towns) = **4.66%** [3.98, 5.33%] | `mayor + poor_record` (n=3,738, 624 towns) = **64.51%** [63.04, 65.98%] | `citizen + good_record` (n=3,721, 624 towns) = **4.33%** [3.62, 5.04%] | `citizen + poor_record` (n=3,739, 624 towns) = **67.83%** [66.38, 69.28%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,738 / 3,739 | -3.32 pp** | [-5.38, -1.26 pp] | 0.0016 |
| `authority effect | reliability=good_record` | 3,733 / 3,721 | +0.33 pp | [-0.65, +1.30 pp] | 0.5103 |
| `reliability effect | authority=citizen` | 3,721 / 3,739 | -63.50 pp*** | [-65.11, -61.89 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,733 / 3,738 | -59.85 pp*** | [-61.47, -58.24 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,725, 624 towns) = **4.43%** [3.73, 5.13%] | `rich + poor_record` (n=3,740, 624 towns) = **63.67%** [62.19, 65.15%] | `poor + good_record` (n=3,729, 624 towns) = **4.56%** [3.88, 5.23%] | `poor + poor_record` (n=3,737, 624 towns) = **68.67%** [67.24, 70.11%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,740 / 3,737 | -5.00 pp*** | [-7.07, -2.94 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,725 / 3,729 | -0.13 pp | [-1.10, +0.85 pp] | 0.7970 |
| `reliability effect | wealth=poor` | 3,729 / 3,737 | -64.11 pp*** | [-65.70, -62.53 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,725 / 3,740 | -59.24 pp*** | [-60.88, -57.60 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,739, 624 towns) = **29.94%** [28.72, 31.15%] | `close_friend + citizen` (n=3,738, 624 towns) = **29.95%** [28.73, 31.17%] | `stranger + mayor` (n=3,732, 624 towns) = **39.24%** [38.17, 40.30%] | `stranger + citizen` (n=3,722, 624 towns) = **42.21%** [41.16, 43.26%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,738 / 3,722 | -12.26 pp*** | [-13.87, -10.65 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,739 / 3,732 | -9.30 pp*** | [-10.92, -7.68 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,732 / 3,722 | -2.98 pp*** | [-4.47, -1.48 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,739 / 3,738 | -0.01 pp | [-1.74, +1.71 pp] | 0.9871 |


**Outcome: CHECKED_TRUE (%)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.80% | 0.67% | +0.13 pp | [-0.15, +0.41 pp] | 0.3594 | 1.0000 |
| main | authority | `mayor - citizen` | 0.88% | 0.59% | +0.29 pp | [+0.01, +0.57 pp] | 0.0401 | 0.2810 |
| main | reliability | `good_record - poor_record` | 1.45% | 0.03% | +1.42 pp*** | [+1.14, +1.70 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 0.72% | 0.75% | -0.03 pp | [-0.31, +0.25 pp] | 0.8523 | 1.0000 |
| main | gender | `woman - man` | 0.75% | 0.72% | +0.03 pp | [-0.25, +0.31 pp] | 0.8199 | 1.0000 |
| main | age | `old - young` | 0.51% | 0.97% | -0.46 pp* | [-0.74, -0.18 pp] | 0.0014 | 0.0127 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.26 pp | +0.00 pp | +0.26 pp | [-0.30, +0.82 pp] | 0.3594 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.64 pp | -0.05 pp | +0.69 pp | [+0.13, +1.25 pp] | 0.0152 | 0.1216 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.05 pp | -0.00 pp | -0.05 pp | [-0.61, +0.51 pp] | 0.8530 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.05 pp | +0.21 pp | -0.16 pp | [-0.72, +0.40 pp] | 0.5798 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,736, 624 towns) = **1.58%** [1.16, 2.00%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + good_record` (n=3,718, 624 towns) = **1.32%** [0.95, 1.68%] | `stranger + poor_record` (n=3,736, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,736 | +0.00 pp | [-0.08, +0.08 pp] | 0.9998 |
| `closeness effect | reliability=good_record` | 3,736 / 3,718 | +0.26 pp | [-0.29, +0.82 pp] | 0.3547 |
| `reliability effect | closeness=stranger` | 3,718 / 3,736 | +1.29 pp*** | [+0.92, +1.66 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,736 / 3,741 | +1.55 pp*** | [+1.13, +1.97 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,733, 624 towns) = **1.77%** [1.33, 2.20%] | `mayor + poor_record` (n=3,738, 624 towns) = **-0.00%** [-0.02, 0.02%] | `citizen + good_record` (n=3,721, 624 towns) = **1.13%** [0.78, 1.47%] | `citizen + poor_record` (n=3,739, 624 towns) = **0.05%** [-0.02, 0.13%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,738 / 3,739 | -0.05 pp | [-0.13, +0.02 pp] | 0.1800 |
| `authority effect | reliability=good_record` | 3,733 / 3,721 | +0.64 pp* | [+0.09, +1.20 pp] | 0.0237 |
| `reliability effect | authority=citizen` | 3,721 / 3,739 | +1.07 pp*** | [+0.72, +1.43 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,733 / 3,738 | +1.77 pp*** | [+1.33, +2.20 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,725, 624 towns) = **1.42%** [1.04, 1.81%] | `rich + poor_record` (n=3,740, 624 towns) = **0.03%** [-0.03, 0.08%] | `poor + good_record` (n=3,729, 624 towns) = **1.47%** [1.08, 1.87%] | `poor + poor_record` (n=3,737, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,740 / 3,737 | -0.00 pp | [-0.08, +0.08 pp] | 0.9973 |
| `wealth effect | reliability=good_record` | 3,725 / 3,729 | -0.05 pp | [-0.61, +0.50 pp] | 0.8512 |
| `reliability effect | wealth=poor` | 3,729 / 3,737 | +1.45 pp*** | [+1.05, +1.85 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,725 / 3,740 | +1.39 pp*** | [+1.00, +1.78 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,739, 624 towns) = **0.91%** [0.59, 1.23%] | `close_friend + citizen` (n=3,738, 624 towns) = **0.70%** [0.42, 0.97%] | `stranger + mayor` (n=3,732, 624 towns) = **0.86%** [0.56, 1.16%] | `stranger + citizen` (n=3,722, 624 towns) = **0.49%** [0.27, 0.70%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,738 / 3,722 | +0.21 pp | [-0.14, +0.56 pp] | 0.2429 |
| `closeness effect | authority=mayor` | 3,739 / 3,732 | +0.05 pp | [-0.38, +0.49 pp] | 0.8148 |
| `authority effect | closeness=stranger` | 3,732 / 3,722 | +0.37 pp* | [+0.00, +0.74 pp] | 0.0490 |
| `authority effect | closeness=close_friend` | 3,739 / 3,738 | +0.21 pp | [-0.21, +0.63 pp] | 0.3168 |


**Outcome: CHECKED_FALSE (%)** (n=14,931, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 52.40% | 41.48% | +10.93 pp*** | [+9.62, +12.23 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 46.04% | 47.84% | -1.79 pp* | [-3.10, -0.49 pp] | 0.0071 | 0.0353 |
| main | reliability | `good_record - poor_record` | 73.89% | 19.99% | +53.90 pp*** | [+52.60, +55.21 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 49.27% | 44.61% | +4.66 pp*** | [+3.35, +5.96 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 47.18% | 46.70% | +0.48 pp | [-0.82, +1.79 pp] | 0.4692 | 0.4692 |
| main | age | `old - young` | 46.17% | 47.71% | -1.54 pp | [-2.85, -0.24 pp] | 0.0207 | 0.0768 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +4.20 pp | +17.65 pp | -13.45 pp*** | [-16.06, -10.84 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -4.47 pp | +0.88 pp | -5.35 pp*** | [-7.96, -2.74 pp] | <0.0001 | 0.0004 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +3.68 pp | +5.63 pp | -1.95 pp | [-4.56, +0.66 pp] | 0.1437 | 0.2873 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +9.37 pp | +12.49 pp | -3.12 pp | [-5.73, -0.51 pp] | 0.0192 | 0.0768 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,736, 624 towns) = **75.99%** [74.64, 77.35%] | `close_friend + poor_record` (n=3,741, 624 towns) = **28.81%** [27.40, 30.22%] | `stranger + good_record` (n=3,718, 624 towns) = **71.79%** [70.35, 73.23%] | `stranger + poor_record` (n=3,736, 624 towns) = **11.16%** [10.21, 12.12%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,736 | +17.65 pp*** | [+15.95, +19.36 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,736 / 3,718 | +4.20 pp*** | [+2.22, +6.18 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 3,718 / 3,736 | +60.63 pp*** | [+58.90, +62.36 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,736 / 3,741 | +47.18 pp*** | [+45.22, +49.13 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,733, 624 towns) = **71.66%** [70.25, 73.07%] | `mayor + poor_record` (n=3,738, 624 towns) = **20.43%** [19.22, 21.64%] | `citizen + good_record` (n=3,721, 624 towns) = **76.13%** [74.74, 77.51%] | `citizen + poor_record` (n=3,739, 624 towns) = **19.55%** [18.35, 20.74%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,738 / 3,739 | +0.88 pp | [-0.82, +2.58 pp] | 0.3104 |
| `authority effect | reliability=good_record` | 3,733 / 3,721 | -4.47 pp*** | [-6.45, -2.49 pp] | <0.0001 |
| `reliability effect | authority=citizen` | 3,721 / 3,739 | +56.58 pp*** | [+54.75, +58.41 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,733 / 3,738 | +51.23 pp*** | [+49.37, +53.09 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,725, 624 towns) = **75.73%** [74.37, 77.10%] | `rich + poor_record` (n=3,740, 624 towns) = **22.80%** [21.51, 24.09%] | `poor + good_record` (n=3,729, 624 towns) = **72.05%** [70.62, 73.49%] | `poor + poor_record` (n=3,737, 624 towns) = **17.17%** [16.06, 18.29%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,740 / 3,737 | +5.63 pp*** | [+3.93, +7.33 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,725 / 3,729 | +3.68 pp*** | [+1.70, +5.66 pp] | 0.0003 |
| `reliability effect | wealth=poor` | 3,729 / 3,737 | +54.88 pp*** | [+53.06, +56.69 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,725 / 3,740 | +52.93 pp*** | [+51.06, +54.81 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,739, 624 towns) = **50.73%** [49.35, 52.11%] | `close_friend + citizen` (n=3,738, 624 towns) = **54.08%** [52.69, 55.47%] | `stranger + mayor` (n=3,732, 624 towns) = **41.36%** [40.11, 42.61%] | `stranger + citizen` (n=3,722, 624 towns) = **41.59%** [40.40, 42.79%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,738 / 3,722 | +12.49 pp*** | [+10.65, +14.32 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,739 / 3,732 | +9.37 pp*** | [+7.51, +11.23 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,732 / 3,722 | -0.23 pp | [-1.96, +1.49 pp] | 0.7901 |
| `authority effect | closeness=close_friend` | 3,739 / 3,738 | -3.35 pp*** | [-5.31, -1.40 pp] | 0.0008 |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=13,620, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0251 | 0.0227 | +0.0024 | [-0.0013, +0.0062] | 0.2005 | 1.0000 | +0.0024 (p=0.2002) |
| main | authority | `mayor - citizen` | 0.0251 | 0.0227 | +0.0023 | [-0.0014, +0.0061] | 0.2231 | 1.0000 | +0.0023 (p=0.2225) |
| main | reliability | `good_record - poor_record` | 0.0330 | 0.0148 | +0.0183*** | [+0.0145, +0.0220] | <0.0001 | <0.0001 | +0.0183 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0256 | 0.0223 | +0.0033 | [-0.0004, +0.0070] | 0.0834 | 0.5839 | +0.0033 (p=0.0832) |
| main | gender | `woman - man` | 0.0246 | 0.0233 | +0.0013 | [-0.0024, +0.0049] | 0.4874 | 1.0000 | +0.0013 (p=0.4966) |
| main | age | `old - young` | 0.0230 | 0.0248 | -0.0018 | [-0.0054, +0.0019] | 0.3419 | 1.0000 | -0.0018 (p=0.3532) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0010 | +0.0059 | -0.0069 | [-0.0144, +0.0006] | 0.0709 | 0.5669 | -0.0069 (p=0.0706) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0025 | +0.0022 | +0.0003 | [-0.0072, +0.0078] | 0.9323 | 1.0000 | +0.0003 (p=0.9322) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0097 | -0.0031 | +0.0129** | [+0.0054, +0.0204] | 0.0007 | 0.0066 | +0.0129 (p=0.0007) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0054 | -0.0005 | +0.0060 | [-0.0013, +0.0132] | 0.1081 | 0.6489 | +0.0060 (p=0.1167) |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,192, 624 towns) = **0.0325** [0.0281, 0.0370] | `close_friend + poor_record` (n=3,589, 624 towns) = **0.0177** [0.0148, 0.0207] | `stranger + good_record` (n=3,205, 624 towns) = **0.0335** [0.0290, 0.0381] | `stranger + poor_record` (n=3,634, 624 towns) = **0.0118** [0.0093, 0.0144]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,589 / 3,634 | +0.0059** | [+0.0020, +0.0098] | 0.0031 |
| `closeness effect | reliability=good_record` | 3,192 / 3,205 | -0.0010 | [-0.0074, +0.0054] | 0.7576 |
| `reliability effect | closeness=stranger` | 3,205 / 3,634 | +0.0217*** | [+0.0165, +0.0270] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,192 / 3,589 | +0.0148*** | [+0.0095, +0.0202] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,190, 624 towns) = **0.0343** [0.0299, 0.0387] | `mayor + poor_record` (n=3,606, 624 towns) = **0.0159** [0.0132, 0.0185] | `citizen + good_record` (n=3,207, 624 towns) = **0.0318** [0.0272, 0.0364] | `citizen + poor_record` (n=3,617, 624 towns) = **0.0137** [0.0109, 0.0165]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,606 / 3,617 | +0.0022 | [-0.0017, +0.0061] | 0.2770 |
| `authority effect | reliability=good_record` | 3,190 / 3,207 | +0.0025 | [-0.0039, +0.0089] | 0.4451 |
| `reliability effect | authority=citizen` | 3,207 / 3,617 | +0.0181*** | [+0.0127, +0.0235] | <0.0001 |
| `reliability effect | authority=mayor` | 3,190 / 3,606 | +0.0184*** | [+0.0132, +0.0236] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,218, 624 towns) = **0.0379** [0.0331, 0.0427] | `rich + poor_record` (n=3,604, 624 towns) = **0.0132** [0.0106, 0.0158] | `poor + good_record` (n=3,179, 624 towns) = **0.0282** [0.0240, 0.0323] | `poor + poor_record` (n=3,619, 624 towns) = **0.0163** [0.0134, 0.0193]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,604 / 3,619 | -0.0031 | [-0.0070, +0.0008] | 0.1142 |
| `wealth effect | reliability=good_record` | 3,218 / 3,179 | +0.0097** | [+0.0034, +0.0161] | 0.0028 |
| `reliability effect | wealth=poor` | 3,179 / 3,619 | +0.0118*** | [+0.0067, +0.0169] | <0.0001 |
| `reliability effect | wealth=rich` | 3,218 / 3,604 | +0.0247*** | [+0.0192, +0.0302] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,378, 624 towns) = **0.0278** [0.0240, 0.0316] | `close_friend + citizen` (n=3,403, 624 towns) = **0.0225** [0.0188, 0.0262] | `stranger + mayor` (n=3,418, 624 towns) = **0.0224** [0.0189, 0.0258] | `stranger + citizen` (n=3,421, 624 towns) = **0.0230** [0.0192, 0.0269]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,403 / 3,421 | -0.0005 | [-0.0059, +0.0048] | 0.8411 |
| `closeness effect | authority=mayor` | 3,378 / 3,418 | +0.0054* | [+0.0003, +0.0105] | 0.0379 |
| `authority effect | closeness=stranger` | 3,418 / 3,421 | -0.0007 | [-0.0058, +0.0045] | 0.8022 |
| `authority effect | closeness=close_friend` | 3,378 / 3,403 | +0.0053* | [+0.0000, +0.0106] | 0.0487 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0225 | 0.0202 | +0.0023 | [-0.0011, +0.0056] | 0.1834 | 0.9171 | +0.0023 (p=0.1928) |
| main | authority | `mayor - citizen` | 0.0223 | 0.0203 | +0.0020 | [-0.0013, +0.0053] | 0.2424 | 0.9694 | +0.0020 (p=0.2524) |
| main | reliability | `good_record - poor_record` | 0.0284 | 0.0143 | +0.0141*** | [+0.0108, +0.0175] | <0.0001 | <0.0001 | +0.0141 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0227 | 0.0199 | +0.0028 | [-0.0005, +0.0062] | 0.0953 | 0.6674 | +0.0028 (p=0.1025) |
| main | gender | `woman - man` | 0.0219 | 0.0207 | +0.0012 | [-0.0021, +0.0046] | 0.4729 | 1.0000 | +0.0012 (p=0.4813) |
| main | age | `old - young` | 0.0206 | 0.0220 | -0.0014 | [-0.0047, +0.0020] | 0.4248 | 1.0000 | -0.0014 (p=0.4348) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0009 | +0.0055 | -0.0064 | [-0.0131, +0.0003] | 0.0598 | 0.4782 | -0.0064 (p=0.0653) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0020 | +0.0020 | -0.0001 | [-0.0068, +0.0066] | 0.9848 | 1.0000 | -0.0001 (p=0.9851) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0087 | -0.0030 | +0.0118** | [+0.0051, +0.0185] | 0.0006 | 0.0050 | +0.0118 (p=0.0007) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0050 | -0.0004 | +0.0054 | [-0.0013, +0.0121] | 0.1130 | 0.6782 | +0.0054 (p=0.1209) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0680 | 0.0616 | +0.0064 | [+0.0012, +0.0116] | 0.0165 | 0.1484 | +0.0064 (p=0.0207) |
| main | authority | `mayor - citizen` | 0.0668 | 0.0628 | +0.0040 | [-0.0012, +0.0092] | 0.1292 | 0.7750 | +0.0040 (p=0.1433) |
| main | reliability | `good_record - poor_record` | 0.0992 | 0.0304 | +0.0688*** | [+0.0636, +0.0740] | <0.0001 | <0.0001 | +0.0688 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0651 | 0.0646 | +0.0005 | [-0.0047, +0.0057] | 0.8432 | 1.0000 | +0.0005 (p=0.8487) |
| main | gender | `woman - man` | 0.0651 | 0.0645 | +0.0007 | [-0.0046, +0.0059] | 0.8066 | 1.0000 | +0.0007 (p=0.8130) |
| main | age | `old - young` | 0.0618 | 0.0678 | -0.0060 | [-0.0112, -0.0008] | 0.0227 | 0.1813 | -0.0060 (p=0.0280) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0007 | +0.0120 | -0.0113 | [-0.0217, -0.0010] | 0.0324 | 0.2266 | -0.0113 (p=0.0390) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0051 | +0.0030 | +0.0021 | [-0.0083, +0.0125] | 0.6971 | 1.0000 | +0.0021 (p=0.7073) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.0034 | -0.0023 | +0.0057 | [-0.0047, +0.0161] | 0.2817 | 1.0000 | +0.0057 (p=0.2991) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0101 | +0.0026 | +0.0075 | [-0.0029, +0.0179] | 0.1587 | 0.7934 | +0.0075 (p=0.1741) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 64.01% | 60.06% | +3.95 pp*** | [+2.47, +5.44 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 64.02% | 60.04% | +3.98 pp*** | [+2.49, +5.47 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 71.03% | 53.03% | +18.00 pp*** | [+16.52, +19.49 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 62.25% | 61.82% | +0.43 pp | [-1.06, +1.91 pp] | 0.5733 | 0.5733 |
| main | gender | `woman - man` | 63.13% | 60.94% | +2.19 pp* | [+0.70, +3.67 pp] | 0.0040 | 0.0159 |
| main | age | `old - young` | 61.18% | 62.89% | -1.71 pp | [-3.20, -0.22 pp] | 0.0243 | 0.0728 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.45 pp | +7.45 pp | -7.00 pp*** | [-9.97, -4.02 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.47 pp | +6.49 pp | -5.02 pp** | [-8.00, -2.05 pp] | 0.0009 | 0.0047 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -2.48 pp | +3.34 pp | -5.82 pp*** | [-8.80, -2.85 pp] | 0.0001 | 0.0007 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +2.56 pp | +5.34 pp | -2.78 pp | [-5.75, +0.20 pp] | 0.0672 | 0.1343 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,744, 624 towns) = **71.26%** [69.85, 72.67%] | `close_friend + poor_record` (n=3,744, 624 towns) = **56.76%** [55.21, 58.31%] | `stranger + good_record` (n=3,744, 624 towns) = **70.81%** [69.46, 72.16%] | `stranger + poor_record` (n=3,744, 624 towns) = **49.31%** [47.68, 50.93%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,744 / 3,744 | +7.45 pp*** | [+5.21, +9.70 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,744 / 3,744 | +0.45 pp | [-1.50, +2.40 pp] | 0.6481 |
| `reliability effect | closeness=stranger` | 3,744 / 3,744 | +21.50 pp*** | [+19.39, +23.61 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,744 / 3,744 | +14.50 pp*** | [+12.41, +16.60 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,744, 624 towns) = **71.77%** [70.39, 73.15%] | `mayor + poor_record` (n=3,744, 624 towns) = **56.28%** [54.75, 57.80%] | `citizen + good_record` (n=3,744, 624 towns) = **70.30%** [68.92, 71.68%] | `citizen + poor_record` (n=3,744, 624 towns) = **49.79%** [48.14, 51.44%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,744 / 3,744 | +6.49 pp*** | [+4.24, +8.74 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 3,744 / 3,744 | +1.47 pp | [-0.48, +3.42 pp] | 0.1398 |
| `reliability effect | authority=citizen` | 3,744 / 3,744 | +20.51 pp*** | [+18.36, +22.66 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,744 / 3,744 | +15.49 pp*** | [+13.44, +17.55 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,744, 624 towns) = **69.79%** [68.35, 71.23%] | `rich + poor_record` (n=3,744, 624 towns) = **54.70%** [53.10, 56.30%] | `poor + good_record` (n=3,744, 624 towns) = **72.28%** [70.96, 73.59%] | `poor + poor_record` (n=3,744, 624 towns) = **51.36%** [49.79, 52.94%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,744 / 3,744 | +3.34 pp** | [+1.09, +5.58 pp] | 0.0036 |
| `wealth effect | reliability=good_record` | 3,744 / 3,744 | -2.48 pp* | [-4.43, -0.53 pp] | 0.0125 |
| `reliability effect | wealth=poor` | 3,744 / 3,744 | +20.91 pp*** | [+18.86, +22.96 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,744 / 3,744 | +15.09 pp*** | [+12.94, +17.24 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,744, 624 towns) = **65.30%** [63.85, 66.76%] | `close_friend + citizen` (n=3,744, 624 towns) = **62.71%** [61.20, 64.22%] | `stranger + mayor` (n=3,744, 624 towns) = **62.74%** [61.28, 64.20%] | `stranger + citizen` (n=3,744, 624 towns) = **57.37%** [55.84, 58.90%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,744 / 3,744 | +5.34 pp*** | [+3.19, +7.49 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,744 / 3,744 | +2.56 pp* | [+0.51, +4.62 pp] | 0.0145 |
| `authority effect | closeness=stranger` | 3,744 / 3,744 | +5.37 pp*** | [+3.26, +7.48 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,744 / 3,744 | +2.59 pp* | [+0.50, +4.68 pp] | 0.0153 |


**Outcome: NOT_MENTIONED (%)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 9.11% | 8.29% | +0.82 pp | [-0.05, +1.69 pp] | 0.0654 | 0.5232 |
| main | authority | `mayor - citizen` | 8.90% | 8.50% | +0.41 pp | [-0.46, +1.28 pp] | 0.3606 | 1.0000 |
| main | reliability | `good_record - poor_record` | 14.17% | 3.23% | +10.94 pp*** | [+10.07, +11.81 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 8.47% | 8.93% | -0.46 pp | [-1.33, +0.41 pp] | 0.2956 | 1.0000 |
| main | gender | `woman - man` | 8.64% | 8.76% | -0.12 pp | [-0.99, +0.75 pp] | 0.7949 | 1.0000 |
| main | age | `old - young` | 8.23% | 9.17% | -0.94 pp | [-1.80, -0.07 pp] | 0.0349 | 0.3139 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.33 pp | +1.31 pp | -0.98 pp | [-2.72, +0.75 pp] | 0.2672 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.62 pp | +0.19 pp | +0.43 pp | [-1.31, +2.16 pp] | 0.6315 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -1.07 pp | +0.14 pp | -1.21 pp | [-2.95, +0.53 pp] | 0.1718 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +1.02 pp | +0.61 pp | +0.41 pp | [-1.33, +2.15 pp] | 0.6413 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,726, 624 towns) = **14.33%** [13.22, 15.44%] | `close_friend + poor_record` (n=3,734, 624 towns) = **3.88%** [3.28, 4.48%] | `stranger + good_record` (n=3,727, 624 towns) = **14.01%** [12.92, 15.09%] | `stranger + poor_record` (n=3,730, 624 towns) = **2.57%** [2.07, 3.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,734 / 3,730 | +1.31 pp** | [+0.52, +2.10 pp] | 0.0011 |
| `closeness effect | reliability=good_record` | 3,726 / 3,727 | +0.33 pp | [-1.23, +1.88 pp] | 0.6812 |
| `reliability effect | closeness=stranger` | 3,727 / 3,730 | +11.43 pp*** | [+10.24, +12.63 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,726 / 3,734 | +10.45 pp*** | [+9.19, +11.71 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,730, 624 towns) = **14.48%** [13.40, 15.56%] | `mayor + poor_record` (n=3,730, 624 towns) = **3.32%** [2.77, 3.88%] | `citizen + good_record` (n=3,723, 624 towns) = **13.86%** [12.75, 14.98%] | `citizen + poor_record` (n=3,734, 624 towns) = **3.13%** [2.58, 3.69%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,730 / 3,734 | +0.19 pp | [-0.59, +0.98 pp] | 0.6308 |
| `authority effect | reliability=good_record` | 3,730 / 3,723 | +0.62 pp | [-0.93, +2.17 pp] | 0.4346 |
| `reliability effect | authority=citizen` | 3,723 / 3,734 | +10.73 pp*** | [+9.48, +11.97 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,730 / 3,730 | +11.15 pp*** | [+9.94, +12.37 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,726, 624 towns) = **13.63%** [12.53, 14.74%] | `rich + poor_record` (n=3,727, 624 towns) = **3.30%** [2.73, 3.87%] | `poor + good_record` (n=3,727, 624 towns) = **14.70%** [13.62, 15.79%] | `poor + poor_record` (n=3,737, 624 towns) = **3.16%** [2.62, 3.70%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,727 / 3,737 | +0.14 pp | [-0.64, +0.93 pp] | 0.7230 |
| `wealth effect | reliability=good_record` | 3,726 / 3,727 | -1.07 pp | [-2.62, +0.48 pp] | 0.1763 |
| `reliability effect | wealth=poor` | 3,727 / 3,737 | +11.55 pp*** | [+10.34, +12.76 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,726 / 3,727 | +10.33 pp*** | [+9.09, +11.58 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,729, 624 towns) = **9.41%** [8.52, 10.30%] | `close_friend + citizen` (n=3,731, 624 towns) = **8.80%** [7.91, 9.69%] | `stranger + mayor` (n=3,731, 624 towns) = **8.39%** [7.56, 9.22%] | `stranger + citizen` (n=3,726, 624 towns) = **8.19%** [7.32, 9.06%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,731 / 3,726 | +0.61 pp | [-0.63, +1.86 pp] | 0.3364 |
| `closeness effect | authority=mayor` | 3,729 / 3,731 | +1.02 pp | [-0.19, +2.24 pp] | 0.0981 |
| `authority effect | closeness=stranger` | 3,731 / 3,726 | +0.20 pp | [-1.00, +1.40 pp] | 0.7447 |
| `authority effect | closeness=close_friend` | 3,729 / 3,731 | +0.61 pp | [-0.65, +1.87 pp] | 0.3410 |


**Outcome: FACT (%)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.23% | 0.16% | +0.07 pp | [-0.07, +0.21 pp] | 0.3488 | 1.0000 |
| main | authority | `mayor - citizen` | 0.19% | 0.20% | -0.01 pp | [-0.15, +0.13 pp] | 0.8484 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.35% | 0.04% | +0.31 pp*** | [+0.17, +0.45 pp] | <0.0001 | 0.0002 |
| main | wealth | `rich - poor` | 0.30% | 0.09% | +0.20 pp* | [+0.06, +0.34 pp] | 0.0048 | 0.0433 |
| main | gender | `woman - man` | 0.21% | 0.17% | +0.04 pp | [-0.10, +0.18 pp] | 0.5797 | 1.0000 |
| main | age | `old - young` | 0.17% | 0.21% | -0.04 pp | [-0.18, +0.10 pp] | 0.5726 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.05 pp | +0.08 pp | -0.03 pp | [-0.31, +0.25 pp] | 0.8495 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.05 pp | +0.03 pp | -0.08 pp | [-0.36, +0.20 pp] | 0.5701 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.32 pp | +0.08 pp | +0.24 pp | [-0.04, +0.52 pp] | 0.0907 | 0.7258 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.16 pp | -0.03 pp | +0.19 pp | [-0.09, +0.47 pp] | 0.1879 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,726, 624 towns) = **0.38%** [0.18, 0.57%] | `close_friend + poor_record` (n=3,734, 624 towns) = **0.08%** [-0.01, 0.17%] | `stranger + good_record` (n=3,727, 624 towns) = **0.32%** [0.14, 0.50%] | `stranger + poor_record` (n=3,730, 624 towns) = **0.00%** [-0.00, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,734 / 3,730 | +0.08 pp | [-0.01, +0.17 pp] | 0.0828 |
| `closeness effect | reliability=good_record` | 3,726 / 3,727 | +0.05 pp | [-0.21, +0.32 pp] | 0.6928 |
| `reliability effect | closeness=stranger` | 3,727 / 3,730 | +0.32 pp*** | [+0.14, +0.50 pp] | 0.0004 |
| `reliability effect | closeness=close_friend` | 3,726 / 3,734 | +0.30 pp** | [+0.08, +0.51 pp] | 0.0070 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,730, 624 towns) = **0.32%** [0.14, 0.50%] | `mayor + poor_record` (n=3,730, 624 towns) = **0.05%** [-0.02, 0.13%] | `citizen + good_record` (n=3,723, 624 towns) = **0.38%** [0.18, 0.57%] | `citizen + poor_record` (n=3,734, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,730 / 3,734 | +0.03 pp | [-0.06, +0.12 pp] | 0.5619 |
| `authority effect | reliability=good_record` | 3,730 / 3,723 | -0.05 pp | [-0.32, +0.21 pp] | 0.6882 |
| `reliability effect | authority=citizen` | 3,723 / 3,734 | +0.35 pp*** | [+0.15, +0.55 pp] | 0.0006 |
| `reliability effect | authority=mayor` | 3,730 / 3,730 | +0.27 pp** | [+0.07, +0.46 pp] | 0.0071 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,726, 624 towns) = **0.51%** [0.28, 0.74%] | `rich + poor_record` (n=3,727, 624 towns) = **0.08%** [-0.01, 0.17%] | `poor + good_record` (n=3,727, 624 towns) = **0.19%** [0.05, 0.33%] | `poor + poor_record` (n=3,737, 624 towns) = **0.00%** [-0.01, 0.01%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,727 / 3,737 | +0.08 pp | [-0.01, +0.17 pp] | 0.0826 |
| `wealth effect | reliability=good_record` | 3,726 / 3,727 | +0.32 pp* | [+0.06, +0.59 pp] | 0.0171 |
| `reliability effect | wealth=poor` | 3,727 / 3,737 | +0.19 pp** | [+0.05, +0.33 pp] | 0.0078 |
| `reliability effect | wealth=rich` | 3,726 / 3,727 | +0.43 pp*** | [+0.19, +0.67 pp] | 0.0005 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,729, 624 towns) = **0.27%** [0.10, 0.43%] | `close_friend + citizen` (n=3,731, 624 towns) = **0.19%** [0.05, 0.33%] | `stranger + mayor` (n=3,731, 624 towns) = **0.11%** [0.00, 0.21%] | `stranger + citizen` (n=3,726, 624 towns) = **0.21%** [0.07, 0.36%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,731 / 3,726 | -0.03 pp | [-0.23, +0.17 pp] | 0.7912 |
| `closeness effect | authority=mayor` | 3,729 / 3,731 | +0.16 pp | [-0.03, +0.36 pp] | 0.1062 |
| `authority effect | closeness=stranger` | 3,731 / 3,726 | -0.11 pp | [-0.29, +0.07 pp] | 0.2405 |
| `authority effect | closeness=close_friend` | 3,729 / 3,731 | +0.08 pp | [-0.13, +0.29 pp] | 0.4628 |


**Outcome: UNCERTAIN (%)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 3.93% | 3.66% | +0.27 pp | [-0.34, +0.87 pp] | 0.3890 | 1.0000 |
| main | authority | `mayor - citizen` | 4.03% | 3.55% | +0.48 pp | [-0.13, +1.09 pp] | 0.1206 | 0.8442 |
| main | reliability | `good_record - poor_record` | 4.82% | 2.77% | +2.04 pp*** | [+1.44, +2.65 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 3.88% | 3.71% | +0.17 pp | [-0.44, +0.77 pp] | 0.5903 | 1.0000 |
| main | gender | `woman - man` | 3.90% | 3.69% | +0.22 pp | [-0.39, +0.83 pp] | 0.4805 | 1.0000 |
| main | age | `old - young` | 3.73% | 3.86% | -0.14 pp | [-0.74, +0.47 pp] | 0.6553 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.40 pp | +0.93 pp | -1.34 pp | [-2.55, -0.13 pp] | 0.0305 | 0.2442 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.61 pp | +0.35 pp | +0.26 pp | [-0.96, +1.47 pp] | 0.6780 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +1.10 pp | -0.77 pp | +1.87 pp* | [+0.66, +3.08 pp] | 0.0025 | 0.0223 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.57 pp | -0.03 pp | +0.60 pp | [-0.61, +1.81 pp] | 0.3336 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,726, 624 towns) = **4.62%** [3.96, 5.27%] | `close_friend + poor_record` (n=3,734, 624 towns) = **3.24%** [2.70, 3.78%] | `stranger + good_record` (n=3,727, 624 towns) = **5.02%** [4.32, 5.72%] | `stranger + poor_record` (n=3,730, 624 towns) = **2.31%** [1.81, 2.80%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,734 / 3,730 | +0.93 pp* | [+0.20, +1.67 pp] | 0.0129 |
| `closeness effect | reliability=good_record` | 3,726 / 3,727 | -0.40 pp | [-1.36, +0.56 pp] | 0.4124 |
| `reliability effect | closeness=stranger` | 3,727 / 3,730 | +2.71 pp*** | [+1.85, +3.57 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,726 / 3,734 | +1.38 pp** | [+0.52, +2.23 pp] | 0.0016 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,730, 624 towns) = **5.12%** [4.43, 5.81%] | `mayor + poor_record` (n=3,730, 624 towns) = **2.95%** [2.45, 3.45%] | `citizen + good_record` (n=3,723, 624 towns) = **4.51%** [3.84, 5.18%] | `citizen + poor_record` (n=3,734, 624 towns) = **2.60%** [2.06, 3.14%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,730 / 3,734 | +0.35 pp | [-0.39, +1.09 pp] | 0.3497 |
| `authority effect | reliability=good_record` | 3,730 / 3,723 | +0.61 pp | [-0.35, +1.57 pp] | 0.2153 |
| `reliability effect | authority=citizen` | 3,723 / 3,734 | +1.92 pp*** | [+1.06, +2.77 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,730 / 3,730 | +2.17 pp*** | [+1.32, +3.03 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,726, 624 towns) = **5.37%** [4.66, 6.07%] | `rich + poor_record` (n=3,727, 624 towns) = **2.39%** [1.92, 2.86%] | `poor + good_record` (n=3,727, 624 towns) = **4.27%** [3.61, 4.92%] | `poor + poor_record` (n=3,737, 624 towns) = **3.16%** [2.59, 3.72%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,727 / 3,737 | -0.77 pp* | [-1.51, -0.03 pp] | 0.0407 |
| `wealth effect | reliability=good_record` | 3,726 / 3,727 | +1.10 pp* | [+0.14, +2.06 pp] | 0.0248 |
| `reliability effect | wealth=poor` | 3,727 / 3,737 | +1.11 pp* | [+0.24, +1.98 pp] | 0.0122 |
| `reliability effect | wealth=rich` | 3,726 / 3,727 | +2.98 pp*** | [+2.13, +3.83 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,729, 624 towns) = **4.32%** [3.71, 4.93%] | `close_friend + citizen` (n=3,731, 624 towns) = **3.54%** [2.94, 4.13%] | `stranger + mayor` (n=3,731, 624 towns) = **3.75%** [3.15, 4.35%] | `stranger + citizen` (n=3,726, 624 towns) = **3.57%** [2.95, 4.19%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,731 / 3,726 | -0.03 pp | [-0.89, +0.83 pp] | 0.9408 |
| `closeness effect | authority=mayor` | 3,729 / 3,731 | +0.57 pp | [-0.29, +1.42 pp] | 0.1950 |
| `authority effect | closeness=stranger` | 3,731 / 3,726 | +0.18 pp | [-0.68, +1.04 pp] | 0.6800 |
| `authority effect | closeness=close_friend` | 3,729 / 3,731 | +0.78 pp | [-0.07, +1.63 pp] | 0.0736 |


**Outcome: SKEPTICAL (%)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 19.17% | 25.78% | -6.61 pp*** | [-7.84, -5.38 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 20.91% | 24.04% | -3.13 pp*** | [-4.35, -1.90 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 7.67% | 37.27% | -29.60 pp*** | [-30.82, -28.37 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 21.14% | 23.80% | -2.66 pp*** | [-3.88, -1.43 pp] | <0.0001 | 0.0001 |
| main | gender | `woman - man` | 21.98% | 22.96% | -0.98 pp | [-2.21, +0.24 pp] | 0.1167 | 0.1167 |
| main | age | `old - young` | 23.37% | 21.58% | +1.79 pp** | [+0.56, +3.01 pp] | 0.0043 | 0.0086 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.72 pp | -14.94 pp | +16.66 pp*** | [+14.21, +19.11 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.07 pp | -6.19 pp | +6.12 pp*** | [+3.67, +8.57 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.21 pp | -5.11 pp | +4.89 pp*** | [+2.44, +7.34 pp] | <0.0001 | 0.0004 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -4.71 pp | -8.51 pp | +3.80 pp** | [+1.35, +6.25 pp] | 0.0024 | 0.0071 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,726, 624 towns) = **8.53%** [7.65, 9.41%] | `close_friend + poor_record` (n=3,734, 624 towns) = **29.80%** [28.38, 31.22%] | `stranger + good_record` (n=3,727, 624 towns) = **6.81%** [6.04, 7.59%] | `stranger + poor_record` (n=3,730, 624 towns) = **44.74%** [43.13, 46.36%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,734 / 3,730 | -14.94 pp*** | [-17.09, -12.79 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,726 / 3,727 | +1.72 pp** | [+0.55, +2.89 pp] | 0.0040 |
| `reliability effect | closeness=stranger` | 3,727 / 3,730 | -37.93 pp*** | [-39.72, -36.14 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,726 / 3,734 | -21.27 pp*** | [-22.94, -19.59 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,730, 624 towns) = **7.64%** [6.81, 8.47%] | `mayor + poor_record` (n=3,730, 624 towns) = **34.18%** [32.67, 35.68%] | `citizen + good_record` (n=3,723, 624 towns) = **7.71%** [6.88, 8.54%] | `citizen + poor_record` (n=3,734, 624 towns) = **40.37%** [38.82, 41.91%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,730 / 3,734 | -6.19 pp*** | [-8.34, -4.04 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 3,730 / 3,723 | -0.07 pp | [-1.24, +1.11 pp] | 0.9106 |
| `reliability effect | authority=citizen` | 3,723 / 3,734 | -32.66 pp*** | [-34.41, -30.91 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,730 / 3,730 | -26.54 pp*** | [-28.25, -24.82 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,726, 624 towns) = **7.57%** [6.73, 8.41%] | `rich + poor_record` (n=3,727, 624 towns) = **34.72%** [33.20, 36.23%] | `poor + good_record` (n=3,727, 624 towns) = **7.78%** [6.96, 8.60%] | `poor + poor_record` (n=3,737, 624 towns) = **39.82%** [38.30, 41.35%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,727 / 3,737 | -5.11 pp*** | [-7.26, -2.95 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,726 / 3,727 | -0.21 pp | [-1.38, +0.96 pp] | 0.7237 |
| `reliability effect | wealth=poor` | 3,727 / 3,737 | -32.04 pp*** | [-33.78, -30.31 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,726 / 3,727 | -27.15 pp*** | [-28.88, -25.42 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,729, 624 towns) = **18.55%** [17.37, 19.74%] | `close_friend + citizen` (n=3,731, 624 towns) = **19.78%** [18.60, 20.96%] | `stranger + mayor` (n=3,731, 624 towns) = **23.26%** [22.02, 24.51%] | `stranger + citizen` (n=3,726, 624 towns) = **28.29%** [27.00, 29.58%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,731 / 3,726 | -8.51 pp*** | [-10.26, -6.76 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,729 / 3,731 | -4.71 pp*** | [-6.43, -2.99 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,731 / 3,726 | -5.03 pp*** | [-6.82, -3.24 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,729 / 3,731 | -1.23 pp | [-2.90, +0.45 pp] | 0.1505 |


**Outcome: CHECKED_TRUE (%)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.05% | 0.03% | +0.03 pp | [-0.04, +0.09 pp] | 0.4126 | 1.0000 |
| main | authority | `mayor - citizen` | 0.03% | 0.05% | -0.03 pp | [-0.09, +0.04 pp] | 0.4119 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.08% | -0.00% | +0.08 pp | [+0.02, +0.14 pp] | 0.0140 | 0.1402 |
| main | wealth | `rich - poor` | 0.04% | 0.04% | -0.00 pp | [-0.06, +0.06 pp] | 0.9987 | 1.0000 |
| main | gender | `woman - man` | 0.03% | 0.05% | -0.03 pp | [-0.09, +0.04 pp] | 0.4294 | 1.0000 |
| main | age | `old - young` | 0.03% | 0.05% | -0.03 pp | [-0.09, +0.04 pp] | 0.4126 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.05 pp | +0.00 pp | +0.05 pp | [-0.07, +0.18 pp] | 0.4133 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.05 pp | +0.00 pp | -0.05 pp | [-0.18, +0.07 pp] | 0.4120 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.00 pp | -0.00 pp | +0.00 pp | [-0.13, +0.13 pp] | 0.9994 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.05 pp | +0.00 pp | +0.05 pp | [-0.07, +0.18 pp] | 0.4128 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,726, 624 towns) = **0.11%** [0.00, 0.21%] | `close_friend + poor_record` (n=3,734, 624 towns) = **0.00%** [-0.00, 0.00%] | `stranger + good_record` (n=3,727, 624 towns) = **0.05%** [-0.02, 0.13%] | `stranger + poor_record` (n=3,730, 624 towns) = **-0.00%** [-0.00, 0.00%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,734 / 3,730 | +0.00 pp | [-0.00, +0.00 pp] | 0.9812 |
| `closeness effect | reliability=good_record` | 3,726 / 3,727 | +0.05 pp | [-0.07, +0.18 pp] | 0.4128 |
| `reliability effect | closeness=stranger` | 3,727 / 3,730 | +0.05 pp | [-0.02, +0.13 pp] | 0.1561 |
| `reliability effect | closeness=close_friend` | 3,726 / 3,734 | +0.11 pp* | [+0.00, +0.21 pp] | 0.0449 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,730, 624 towns) = **0.05%** [-0.02, 0.13%] | `mayor + poor_record` (n=3,730, 624 towns) = **0.00%** [-0.00, 0.00%] | `citizen + good_record` (n=3,723, 624 towns) = **0.11%** [0.00, 0.21%] | `citizen + poor_record` (n=3,734, 624 towns) = **-0.00%** [-0.00, 0.00%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,730 / 3,734 | +0.00 pp | [-0.00, +0.00 pp] | 0.9962 |
| `authority effect | reliability=good_record` | 3,730 / 3,723 | -0.05 pp | [-0.18, +0.07 pp] | 0.4119 |
| `reliability effect | authority=citizen` | 3,723 / 3,734 | +0.11 pp* | [+0.00, +0.21 pp] | 0.0448 |
| `reliability effect | authority=mayor` | 3,730 / 3,730 | +0.05 pp | [-0.02, +0.13 pp] | 0.1566 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,726, 624 towns) = **0.08%** [-0.01, 0.17%] | `rich + poor_record` (n=3,727, 624 towns) = **-0.00%** [-0.00, 0.00%] | `poor + good_record` (n=3,727, 624 towns) = **0.08%** [-0.01, 0.17%] | `poor + poor_record` (n=3,737, 624 towns) = **0.00%** [-0.00, 0.00%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,727 / 3,737 | -0.00 pp | [-0.00, +0.00 pp] | 0.9590 |
| `wealth effect | reliability=good_record` | 3,726 / 3,727 | -0.00 pp | [-0.13, +0.13 pp] | 0.9996 |
| `reliability effect | wealth=poor` | 3,727 / 3,737 | +0.08 pp | [-0.01, +0.17 pp] | 0.0823 |
| `reliability effect | wealth=rich` | 3,726 / 3,727 | +0.08 pp | [-0.01, +0.17 pp] | 0.0823 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,729, 624 towns) = **0.05%** [-0.02, 0.13%] | `close_friend + citizen` (n=3,731, 624 towns) = **0.05%** [-0.02, 0.13%] | `stranger + mayor` (n=3,731, 624 towns) = **-0.00%** [-0.00, 0.00%] | `stranger + citizen` (n=3,726, 624 towns) = **0.05%** [-0.02, 0.13%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,731 / 3,726 | +0.00 pp | [-0.10, +0.10 pp] | 0.9994 |
| `closeness effect | authority=mayor` | 3,729 / 3,731 | +0.05 pp | [-0.02, +0.13 pp] | 0.1564 |
| `authority effect | closeness=stranger` | 3,731 / 3,726 | -0.05 pp | [-0.13, +0.02 pp] | 0.1556 |
| `authority effect | closeness=close_friend` | 3,729 / 3,731 | -0.00 pp | [-0.10, +0.10 pp] | 0.9988 |


**Outcome: CHECKED_FALSE (%)** (n=14,917, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 67.52% | 62.08% | +5.43 pp*** | [+3.96, +6.90 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 65.94% | 63.66% | +2.28 pp** | [+0.81, +3.75 pp] | 0.0024 | 0.0071 |
| main | reliability | `good_record - poor_record` | 72.91% | 56.69% | +16.22 pp*** | [+14.75, +17.69 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 66.18% | 63.42% | +2.75 pp** | [+1.28, +4.23 pp] | 0.0002 | 0.0012 |
| main | gender | `woman - man` | 65.23% | 64.37% | +0.87 pp | [-0.61, +2.34 pp] | 0.2494 | 0.4988 |
| main | age | `old - young` | 64.48% | 65.12% | -0.65 pp | [-2.12, +0.83 pp] | 0.3896 | 0.4988 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -1.75 pp | +12.62 pp | -14.37 pp*** | [-17.31, -11.43 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.05 pp | +5.62 pp | -6.67 pp*** | [-9.61, -3.73 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.14 pp | +5.65 pp | -5.79 pp*** | [-8.74, -2.85 pp] | 0.0001 | 0.0007 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +2.91 pp | +7.96 pp | -5.05 pp** | [-8.00, -2.11 pp] | 0.0008 | 0.0031 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,726, 624 towns) = **72.04%** [70.64, 73.44%] | `close_friend + poor_record` (n=3,734, 624 towns) = **63.00%** [61.49, 64.51%] | `stranger + good_record` (n=3,727, 624 towns) = **73.79%** [72.44, 75.13%] | `stranger + poor_record` (n=3,730, 624 towns) = **50.38%** [48.77, 51.99%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,734 / 3,730 | +12.62 pp*** | [+10.41, +14.82 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,726 / 3,727 | -1.75 pp | [-3.69, +0.19 pp] | 0.0775 |
| `reliability effect | closeness=stranger` | 3,727 / 3,730 | +23.41 pp*** | [+21.31, +25.51 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,726 / 3,734 | +9.04 pp*** | [+6.98, +11.10 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,730, 624 towns) = **72.38%** [71.00, 73.77%] | `mayor + poor_record` (n=3,730, 624 towns) = **59.50%** [57.98, 61.02%] | `citizen + good_record` (n=3,723, 624 towns) = **73.44%** [72.07, 74.80%] | `citizen + poor_record` (n=3,734, 624 towns) = **53.88%** [52.28, 55.48%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,730 / 3,734 | +5.62 pp*** | [+3.41, +7.83 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 3,730 / 3,723 | -1.05 pp | [-3.00, +0.89 pp] | 0.2891 |
| `reliability effect | authority=citizen` | 3,723 / 3,734 | +19.56 pp*** | [+17.46, +21.66 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,730 / 3,730 | +12.89 pp*** | [+10.83, +14.95 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,726, 624 towns) = **72.84%** [71.45, 74.23%] | `rich + poor_record` (n=3,727, 624 towns) = **59.51%** [57.96, 61.07%] | `poor + good_record` (n=3,727, 624 towns) = **72.98%** [71.63, 74.34%] | `poor + poor_record` (n=3,737, 624 towns) = **53.86%** [52.30, 55.43%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,727 / 3,737 | +5.65 pp*** | [+3.44, +7.86 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,726 / 3,727 | -0.14 pp | [-2.09, +1.80 pp] | 0.8861 |
| `reliability effect | wealth=poor` | 3,727 / 3,737 | +19.12 pp*** | [+17.05, +21.19 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,726 / 3,727 | +13.33 pp*** | [+11.24, +15.42 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,729, 624 towns) = **67.39%** [65.93, 68.85%] | `close_friend + citizen` (n=3,731, 624 towns) = **67.64%** [66.18, 69.09%] | `stranger + mayor` (n=3,731, 624 towns) = **64.49%** [63.04, 65.94%] | `stranger + citizen` (n=3,726, 624 towns) = **59.68%** [58.16, 61.20%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,731 / 3,726 | +7.96 pp*** | [+5.86, +10.06 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,729 / 3,731 | +2.91 pp** | [+0.85, +4.96 pp] | 0.0056 |
| `authority effect | closeness=stranger` | 3,731 / 3,726 | +4.81 pp*** | [+2.71, +6.91 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,729 / 3,731 | -0.24 pp | [-2.30, +1.82 pp] | 0.8166 |


### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Outcome: Belief Score (Valid Mentioning)** (n=28,995, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0201 | 0.0203 | -0.0002 | [-0.0027, +0.0023] | 0.8654 | 1.0000 | -0.0002 (p=0.8692) |
| main | authority | `mayor - citizen` | 0.0205 | 0.0199 | +0.0007 | [-0.0018, +0.0032] | 0.6097 | 1.0000 | +0.0007 (p=0.6200) |
| main | reliability | `good_record - poor_record` | 0.0265 | 0.0139 | +0.0125*** | [+0.0100, +0.0150] | <0.0001 | <0.0001 | +0.0125 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0198 | 0.0206 | -0.0008 | [-0.0033, +0.0017] | 0.5517 | 1.0000 | -0.0008 (p=0.5630) |
| main | gender | `woman - man` | 0.0215 | 0.0189 | +0.0026 | [+0.0001, +0.0051] | 0.0400 | 0.3600 | +0.0026 (p=0.0458) |
| main | age | `old - young` | 0.0201 | 0.0203 | -0.0002 | [-0.0027, +0.0023] | 0.8943 | 1.0000 | -0.0002 (p=0.8973) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0006 | -0.0011 | +0.0017 | [-0.0033, +0.0067] | 0.5076 | 1.0000 | +0.0017 (p=0.5197) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0011 | +0.0002 | +0.0009 | [-0.0041, +0.0059] | 0.7283 | 1.0000 | +0.0009 (p=0.7358) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0020 | +0.0005 | -0.0025 | [-0.0075, +0.0025] | 0.3277 | 1.0000 | -0.0025 (p=0.3414) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0003 | -0.0008 | +0.0011 | [-0.0039, +0.0061] | 0.6745 | 1.0000 | +0.0011 (p=0.6835) |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,276, 624 towns) = **0.0268** [0.0240, 0.0296] | `close_friend + poor_record` (n=7,275, 624 towns) = **0.0134** [0.0111, 0.0157] | `stranger + good_record` (n=7,186, 624 towns) = **0.0262** [0.0234, 0.0289] | `stranger + poor_record` (n=7,258, 624 towns) = **0.0145** [0.0124, 0.0166]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,275 / 7,258 | -0.0011 | [-0.0042, +0.0020] | 0.5023 |
| `closeness effect | reliability=good_record` | 7,276 / 7,186 | +0.0006 | [-0.0033, +0.0046] | 0.7533 |
| `reliability effect | closeness=stranger` | 7,186 / 7,258 | +0.0117*** | [+0.0082, +0.0152] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,276 / 7,275 | +0.0134*** | [+0.0098, +0.0170] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,269, 624 towns) = **0.0270** [0.0241, 0.0299] | `mayor + poor_record` (n=7,266, 624 towns) = **0.0140** [0.0119, 0.0162] | `citizen + good_record` (n=7,193, 624 towns) = **0.0259** [0.0233, 0.0286] | `citizen + poor_record` (n=7,267, 624 towns) = **0.0138** [0.0116, 0.0160]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,266 / 7,267 | +0.0002 | [-0.0029, +0.0033] | 0.8955 |
| `authority effect | reliability=good_record` | 7,269 / 7,193 | +0.0011 | [-0.0028, +0.0050] | 0.5844 |
| `reliability effect | authority=citizen` | 7,193 / 7,267 | +0.0121*** | [+0.0087, +0.0156] | <0.0001 |
| `reliability effect | authority=mayor` | 7,269 / 7,266 | +0.0130*** | [+0.0094, +0.0166] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,242, 624 towns) = **0.0255** [0.0227, 0.0282] | `rich + poor_record` (n=7,265, 624 towns) = **0.0142** [0.0119, 0.0165] | `poor + good_record` (n=7,220, 624 towns) = **0.0275** [0.0247, 0.0303] | `poor + poor_record` (n=7,268, 624 towns) = **0.0137** [0.0116, 0.0158]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,265 / 7,268 | +0.0005 | [-0.0026, +0.0036] | 0.7570 |
| `wealth effect | reliability=good_record` | 7,242 / 7,220 | -0.0020 | [-0.0059, +0.0019] | 0.3158 |
| `reliability effect | wealth=poor` | 7,220 / 7,268 | +0.0138*** | [+0.0103, +0.0173] | <0.0001 |
| `reliability effect | wealth=rich` | 7,242 / 7,265 | +0.0113*** | [+0.0077, +0.0149] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,286, 624 towns) = **0.0207** [0.0180, 0.0234] | `close_friend + citizen` (n=7,265, 624 towns) = **0.0195** [0.0171, 0.0220] | `stranger + mayor` (n=7,249, 624 towns) = **0.0204** [0.0179, 0.0228] | `stranger + citizen` (n=7,195, 624 towns) = **0.0203** [0.0178, 0.0227]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,265 / 7,195 | -0.0008 | [-0.0042, +0.0027] | 0.6695 |
| `closeness effect | authority=mayor` | 7,286 / 7,249 | +0.0003 | [-0.0033, +0.0039] | 0.8627 |
| `authority effect | closeness=stranger` | 7,249 / 7,195 | +0.0001 | [-0.0033, +0.0036] | 0.9475 |
| `authority effect | closeness=close_friend` | 7,286 / 7,265 | +0.0012 | [-0.0024, +0.0048] | 0.5203 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0196 | 0.0196 | -0.0000 | [-0.0025, +0.0024] | 0.9875 | 1.0000 | -0.0000 (p=0.9879) |
| main | authority | `mayor - citizen` | 0.0200 | 0.0192 | +0.0008 | [-0.0017, +0.0032] | 0.5326 | 1.0000 | +0.0008 (p=0.5437) |
| main | reliability | `good_record - poor_record` | 0.0257 | 0.0135 | +0.0121*** | [+0.0097, +0.0146] | <0.0001 | <0.0001 | +0.0121 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0193 | 0.0200 | -0.0007 | [-0.0031, +0.0017] | 0.5679 | 1.0000 | -0.0007 (p=0.5783) |
| main | gender | `woman - man` | 0.0209 | 0.0184 | +0.0025 | [+0.0001, +0.0050] | 0.0427 | 0.3840 | +0.0025 (p=0.0483) |
| main | age | `old - young` | 0.0195 | 0.0197 | -0.0002 | [-0.0026, +0.0023] | 0.9035 | 1.0000 | -0.0002 (p=0.9061) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0009 | -0.0010 | +0.0019 | [-0.0029, +0.0068] | 0.4351 | 1.0000 | +0.0019 (p=0.4475) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0013 | +0.0002 | +0.0011 | [-0.0037, +0.0060] | 0.6496 | 1.0000 | +0.0011 (p=0.6584) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0019 | +0.0005 | -0.0024 | [-0.0072, +0.0025] | 0.3400 | 1.0000 | -0.0024 (p=0.3530) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0005 | -0.0005 | +0.0010 | [-0.0038, +0.0059] | 0.6814 | 1.0000 | +0.0010 (p=0.6895) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0322 | 0.0362 | -0.0040 | [-0.0069, -0.0010] | 0.0087 | 0.0786 | -0.0040 (p=0.0121) |
| main | authority | `mayor - citizen` | 0.0333 | 0.0352 | -0.0019 | [-0.0049, +0.0011] | 0.2082 | 1.0000 | -0.0019 (p=0.2286) |
| main | reliability | `good_record - poor_record` | 0.0409 | 0.0276 | +0.0133*** | [+0.0103, +0.0163] | <0.0001 | <0.0001 | +0.0133 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0336 | 0.0349 | -0.0013 | [-0.0043, +0.0016] | 0.3840 | 1.0000 | -0.0013 (p=0.4050) |
| main | gender | `woman - man` | 0.0358 | 0.0326 | +0.0031 | [+0.0002, +0.0061] | 0.0382 | 0.3056 | +0.0031 (p=0.0471) |
| main | age | `old - young` | 0.0341 | 0.0343 | -0.0001 | [-0.0031, +0.0028] | 0.9259 | 1.0000 | -0.0001 (p=0.9292) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0053 | -0.0026 | -0.0026 | [-0.0086, +0.0033] | 0.3825 | 1.0000 | -0.0026 (p=0.4035) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0037 | -0.0001 | -0.0036 | [-0.0095, +0.0023] | 0.2359 | 1.0000 | -0.0036 (p=0.2569) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0030 | +0.0004 | -0.0035 | [-0.0094, +0.0025] | 0.2515 | 1.0000 | -0.0035 (p=0.2727) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.0026 | -0.0054 | +0.0028 | [-0.0031, +0.0087] | 0.3587 | 1.0000 | +0.0028 (p=0.3801) |

**Outcome: GO Rate (Verification %)** (n=29,952, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 63.49% | 57.87% | +5.62 pp*** | [+4.90, +6.34 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 61.56% | 59.80% | +1.76 pp*** | [+1.04, +2.48 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 67.43% | 53.93% | +13.51 pp*** | [+12.79, +14.23 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 62.26% | 59.10% | +3.16 pp*** | [+2.44, +3.88 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 60.64% | 60.72% | -0.08 pp | [-0.80, +0.64 pp] | 0.8285 | 1.0000 |
| main | age | `old - young` | 60.68% | 60.68% | -0.01 pp | [-0.73, +0.71 pp] | 0.9855 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +2.04 pp | +9.19 pp | -7.14 pp*** | [-8.58, -5.71 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.60 pp | +2.91 pp | -2.31 pp** | [-3.75, -0.87 pp] | 0.0017 | 0.0066 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +1.38 pp | +4.94 pp | -3.57 pp*** | [-5.01, -2.13 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +4.69 pp | +6.54 pp | -1.86 pp* | [-3.30, -0.42 pp] | 0.0115 | 0.0345 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,488, 624 towns) = **68.46%** [67.68, 69.23%] | `close_friend + poor_record` (n=7,488, 624 towns) = **58.52%** [57.90, 59.14%] | `stranger + good_record` (n=7,488, 624 towns) = **66.41%** [65.65, 67.17%] | `stranger + poor_record` (n=7,488, 624 towns) = **49.33%** [48.62, 50.04%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,488 / 7,488 | +9.19 pp*** | [+8.24, +10.13 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,488 / 7,488 | +2.04 pp*** | [+0.96, +3.13 pp] | 0.0002 |
| `reliability effect | closeness=stranger` | 7,488 / 7,488 | +17.08 pp*** | [+16.04, +18.12 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,488 / 7,488 | +9.94 pp*** | [+8.94, +10.93 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,488, 624 towns) = **67.74%** [66.96, 68.51%] | `mayor + poor_record` (n=7,488, 624 towns) = **55.38%** [54.72, 56.04%] | `citizen + good_record` (n=7,488, 624 towns) = **67.13%** [66.38, 67.89%] | `citizen + poor_record` (n=7,488, 624 towns) = **52.47%** [51.80, 53.15%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,488 / 7,488 | +2.91 pp*** | [+1.97, +3.86 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 7,488 / 7,488 | +0.60 pp | [-0.48, +1.69 pp] | 0.2779 |
| `reliability effect | authority=citizen` | 7,488 / 7,488 | +14.66 pp*** | [+13.65, +15.68 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,488 / 7,488 | +12.35 pp*** | [+11.33, +13.37 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,488, 624 towns) = **68.12%** [67.35, 68.90%] | `rich + poor_record` (n=7,488, 624 towns) = **56.40%** [55.75, 57.04%] | `poor + good_record` (n=7,488, 624 towns) = **66.75%** [65.98, 67.51%] | `poor + poor_record` (n=7,488, 624 towns) = **51.46%** [50.76, 52.15%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,488 / 7,488 | +4.94 pp*** | [+4.00, +5.89 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 7,488 / 7,488 | +1.38 pp* | [+0.29, +2.46 pp] | 0.0130 |
| `reliability effect | wealth=poor` | 7,488 / 7,488 | +15.29 pp*** | [+14.26, +16.32 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,488 / 7,488 | +11.73 pp*** | [+10.72, +12.73 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,488, 624 towns) = **63.90%** [63.19, 64.62%] | `close_friend + citizen` (n=7,488, 624 towns) = **63.07%** [62.39, 63.76%] | `stranger + mayor` (n=7,488, 624 towns) = **59.21%** [58.49, 59.94%] | `stranger + citizen` (n=7,488, 624 towns) = **56.53%** [55.78, 57.28%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,488 / 7,488 | +6.54 pp*** | [+5.53, +7.56 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 7,488 / 7,488 | +4.69 pp*** | [+3.67, +5.71 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 7,488 / 7,488 | +2.68 pp*** | [+1.64, +3.73 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 7,488 / 7,488 | +0.83 pp | [-0.16, +1.82 pp] | 0.1021 |


**Outcome: NOT_MENTIONED (%)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 2.53% | 3.31% | -0.79 pp*** | [-1.16, -0.41 pp] | <0.0001 | 0.0004 |
| main | authority | `mayor - citizen` | 2.65% | 3.19% | -0.54 pp* | [-0.91, -0.16 pp] | 0.0053 | 0.0474 |
| main | reliability | `good_record - poor_record` | 3.04% | 2.80% | +0.23 pp | [-0.14, +0.61 pp] | 0.2217 | 1.0000 |
| main | wealth | `rich - poor` | 2.86% | 2.98% | -0.12 pp | [-0.50, +0.25 pp] | 0.5271 | 1.0000 |
| main | gender | `woman - man` | 2.98% | 2.86% | +0.12 pp | [-0.25, +0.50 pp] | 0.5200 | 1.0000 |
| main | age | `old - young` | 2.92% | 2.92% | +0.00 pp | [-0.37, +0.38 pp] | 0.9918 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -1.25 pp | -0.33 pp | -0.92 pp | [-1.67, -0.16 pp] | 0.0171 | 0.1194 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.01 pp | -0.06 pp | -0.94 pp | [-1.69, -0.19 pp] | 0.0141 | 0.1128 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.23 pp | -0.01 pp | -0.22 pp | [-0.97, +0.53 pp] | 0.5675 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.61 pp | -0.96 pp | +0.35 pp | [-0.40, +1.10 pp] | 0.3603 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,456, 624 towns) = **2.41%** [2.07, 2.76%] | `close_friend + poor_record` (n=7,472, 624 towns) = **2.64%** [2.27, 3.00%] | `stranger + good_record` (n=7,459, 624 towns) = **3.66%** [3.24, 4.08%] | `stranger + poor_record` (n=7,480, 624 towns) = **2.97%** [2.60, 3.34%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,472 / 7,480 | -0.33 pp | [-0.85, +0.19 pp] | 0.2119 |
| `closeness effect | reliability=good_record` | 7,456 / 7,459 | -1.25 pp*** | [-1.79, -0.70 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 7,459 / 7,480 | +0.69 pp* | [+0.13, +1.25 pp] | 0.0152 |
| `reliability effect | closeness=close_friend` | 7,456 / 7,472 | -0.22 pp | [-0.73, +0.28 pp] | 0.3847 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,458, 624 towns) = **2.53%** [2.19, 2.88%] | `mayor + poor_record` (n=7,473, 624 towns) = **2.77%** [2.40, 3.14%] | `citizen + good_record` (n=7,457, 624 towns) = **3.54%** [3.12, 3.96%] | `citizen + poor_record` (n=7,479, 624 towns) = **2.83%** [2.47, 3.20%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,473 / 7,479 | -0.06 pp | [-0.58, +0.46 pp] | 0.8084 |
| `authority effect | reliability=good_record` | 7,458 / 7,457 | -1.01 pp*** | [-1.55, -0.46 pp] | 0.0003 |
| `reliability effect | authority=citizen` | 7,457 / 7,479 | +0.71 pp* | [+0.15, +1.26 pp] | 0.0127 |
| `reliability effect | authority=mayor` | 7,458 / 7,473 | -0.24 pp | [-0.74, +0.27 pp] | 0.3609 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,460, 624 towns) = **2.92%** [2.55, 3.29%] | `rich + poor_record` (n=7,474, 624 towns) = **2.80%** [2.43, 3.16%] | `poor + good_record` (n=7,455, 624 towns) = **3.15%** [2.75, 3.55%] | `poor + poor_record` (n=7,478, 624 towns) = **2.81%** [2.44, 3.18%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,474 / 7,478 | -0.01 pp | [-0.53, +0.51 pp] | 0.9650 |
| `wealth effect | reliability=good_record` | 7,460 / 7,455 | -0.23 pp | [-0.77, +0.31 pp] | 0.4048 |
| `reliability effect | wealth=poor` | 7,455 / 7,478 | +0.34 pp | [-0.20, +0.89 pp] | 0.2145 |
| `reliability effect | wealth=rich` | 7,460 / 7,474 | +0.12 pp | [-0.40, +0.64 pp] | 0.6383 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,461, 624 towns) = **2.35%** [2.00, 2.69%] | `close_friend + citizen` (n=7,467, 624 towns) = **2.71%** [2.34, 3.07%] | `stranger + mayor` (n=7,470, 624 towns) = **2.96%** [2.59, 3.33%] | `stranger + citizen` (n=7,469, 624 towns) = **3.67%** [3.25, 4.09%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,467 / 7,469 | -0.96 pp*** | [-1.52, -0.41 pp] | 0.0007 |
| `closeness effect | authority=mayor` | 7,461 / 7,470 | -0.61 pp* | [-1.12, -0.11 pp] | 0.0178 |
| `authority effect | closeness=stranger` | 7,470 / 7,469 | -0.71 pp* | [-1.27, -0.15 pp] | 0.0126 |
| `authority effect | closeness=close_friend` | 7,461 / 7,467 | -0.36 pp | [-0.86, +0.14 pp] | 0.1612 |


**Outcome: FACT (%)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.56% | 0.37% | +0.18 pp | [+0.03, +0.34 pp] | 0.0217 | 0.2168 |
| main | authority | `mayor - citizen` | 0.48% | 0.45% | +0.03 pp | [-0.12, +0.19 pp] | 0.6684 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.48% | 0.45% | +0.03 pp | [-0.12, +0.19 pp] | 0.6619 | 1.0000 |
| main | wealth | `rich - poor` | 0.53% | 0.40% | +0.13 pp | [-0.03, +0.28 pp] | 0.1066 | 0.8529 |
| main | gender | `woman - man` | 0.42% | 0.51% | -0.09 pp | [-0.24, +0.07 pp] | 0.2638 | 1.0000 |
| main | age | `old - young` | 0.46% | 0.48% | -0.02 pp | [-0.17, +0.13 pp] | 0.8036 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.03 pp | +0.33 pp | -0.31 pp | [-0.62, +0.00 pp] | 0.0508 | 0.4569 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.05 pp | +0.01 pp | +0.04 pp | [-0.27, +0.35 pp] | 0.8019 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.11 pp | +0.15 pp | -0.04 pp | [-0.35, +0.27 pp] | 0.7977 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.30 pp | +0.07 pp | +0.23 pp | [-0.08, +0.54 pp] | 0.1476 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,456, 624 towns) = **0.50%** [0.33, 0.66%] | `close_friend + poor_record` (n=7,472, 624 towns) = **0.62%** [0.44, 0.79%] | `stranger + good_record` (n=7,459, 624 towns) = **0.47%** [0.31, 0.62%] | `stranger + poor_record` (n=7,480, 624 towns) = **0.28%** [0.16, 0.40%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,472 / 7,480 | +0.33 pp** | [+0.12, +0.55 pp] | 0.0019 |
| `closeness effect | reliability=good_record` | 7,456 / 7,459 | +0.03 pp | [-0.20, +0.25 pp] | 0.8143 |
| `reliability effect | closeness=stranger` | 7,459 / 7,480 | +0.19 pp | [-0.01, +0.38 pp] | 0.0588 |
| `reliability effect | closeness=close_friend` | 7,456 / 7,472 | -0.12 pp | [-0.36, +0.12 pp] | 0.3276 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,458, 624 towns) = **0.51%** [0.34, 0.68%] | `mayor + poor_record` (n=7,473, 624 towns) = **0.46%** [0.31, 0.60%] | `citizen + good_record` (n=7,457, 624 towns) = **0.46%** [0.31, 0.60%] | `citizen + poor_record` (n=7,479, 624 towns) = **0.44%** [0.29, 0.59%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,473 / 7,479 | +0.01 pp | [-0.20, +0.23 pp] | 0.8968 |
| `authority effect | reliability=good_record` | 7,458 / 7,457 | +0.05 pp | [-0.17, +0.28 pp] | 0.6414 |
| `reliability effect | authority=citizen` | 7,457 / 7,479 | +0.01 pp | [-0.20, +0.23 pp] | 0.8919 |
| `reliability effect | authority=mayor` | 7,458 / 7,473 | +0.05 pp | [-0.17, +0.28 pp] | 0.6365 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,460, 624 towns) = **0.54%** [0.36, 0.71%] | `rich + poor_record` (n=7,474, 624 towns) = **0.52%** [0.36, 0.68%] | `poor + good_record` (n=7,455, 624 towns) = **0.43%** [0.28, 0.57%] | `poor + poor_record` (n=7,478, 624 towns) = **0.37%** [0.24, 0.51%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,474 / 7,478 | +0.15 pp | [-0.06, +0.36 pp] | 0.1717 |
| `wealth effect | reliability=good_record` | 7,460 / 7,455 | +0.11 pp | [-0.12, +0.33 pp] | 0.3522 |
| `reliability effect | wealth=poor` | 7,455 / 7,478 | +0.05 pp | [-0.14, +0.25 pp] | 0.5898 |
| `reliability effect | wealth=rich` | 7,460 / 7,474 | +0.01 pp | [-0.22, +0.25 pp] | 0.9059 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,461, 624 towns) = **0.63%** [0.45, 0.81%] | `close_friend + citizen` (n=7,467, 624 towns) = **0.48%** [0.33, 0.64%] | `stranger + mayor` (n=7,470, 624 towns) = **0.33%** [0.20, 0.47%] | `stranger + citizen` (n=7,469, 624 towns) = **0.42%** [0.27, 0.56%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,467 / 7,469 | +0.07 pp | [-0.14, +0.28 pp] | 0.5361 |
| `closeness effect | authority=mayor` | 7,461 / 7,470 | +0.30 pp* | [+0.07, +0.52 pp] | 0.0101 |
| `authority effect | closeness=stranger` | 7,470 / 7,469 | -0.08 pp | [-0.28, +0.12 pp] | 0.4201 |
| `authority effect | closeness=close_friend` | 7,461 / 7,467 | +0.15 pp | [-0.09, +0.39 pp] | 0.2258 |


**Outcome: UNCERTAIN (%)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 2.53% | 3.11% | -0.58 pp* | [-0.94, -0.22 pp] | 0.0017 | 0.0138 |
| main | authority | `mayor - citizen` | 2.85% | 2.79% | +0.06 pp | [-0.30, +0.42 pp] | 0.7437 | 1.0000 |
| main | reliability | `good_record - poor_record` | 4.06% | 1.57% | +2.49 pp*** | [+2.13, +2.85 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 2.59% | 3.04% | -0.45 pp | [-0.81, -0.09 pp] | 0.0151 | 0.0908 |
| main | gender | `woman - man` | 3.16% | 2.48% | +0.68 pp** | [+0.32, +1.05 pp] | 0.0002 | 0.0020 |
| main | age | `old - young` | 2.79% | 2.84% | -0.04 pp | [-0.41, +0.32 pp] | 0.8093 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.03 pp | -1.14 pp | +1.11 pp* | [+0.38, +1.84 pp] | 0.0027 | 0.0190 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.21 pp | -0.09 pp | +0.31 pp | [-0.42, +1.03 pp] | 0.4062 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.59 pp | -0.31 pp | -0.29 pp | [-1.01, +0.44 pp] | 0.4401 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.71 pp | -0.45 pp | -0.25 pp | [-0.98, +0.47 pp] | 0.4939 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,456, 624 towns) = **4.05%** [3.63, 4.47%] | `close_friend + poor_record` (n=7,472, 624 towns) = **1.00%** [0.78, 1.23%] | `stranger + good_record` (n=7,459, 624 towns) = **4.08%** [3.63, 4.52%] | `stranger + poor_record` (n=7,480, 624 towns) = **2.14%** [1.82, 2.46%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,472 / 7,480 | -1.14 pp*** | [-1.53, -0.74 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,456 / 7,459 | -0.03 pp | [-0.64, +0.59 pp] | 0.9361 |
| `reliability effect | closeness=stranger` | 7,459 / 7,480 | +1.94 pp*** | [+1.39, +2.49 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,456 / 7,472 | +3.05 pp*** | [+2.57, +3.52 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,458, 624 towns) = **4.17%** [3.73, 4.61%] | `mayor + poor_record` (n=7,473, 624 towns) = **1.52%** [1.26, 1.79%] | `citizen + good_record` (n=7,457, 624 towns) = **3.96%** [3.53, 4.38%] | `citizen + poor_record` (n=7,479, 624 towns) = **1.62%** [1.33, 1.90%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,473 / 7,479 | -0.09 pp | [-0.48, +0.30 pp] | 0.6398 |
| `authority effect | reliability=good_record` | 7,458 / 7,457 | +0.21 pp | [-0.40, +0.83 pp] | 0.4923 |
| `reliability effect | authority=citizen` | 7,457 / 7,479 | +2.34 pp*** | [+1.83, +2.85 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,458 / 7,473 | +2.65 pp*** | [+2.13, +3.16 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,460, 624 towns) = **3.77%** [3.36, 4.17%] | `rich + poor_record` (n=7,474, 624 towns) = **1.42%** [1.14, 1.69%] | `poor + good_record` (n=7,455, 624 towns) = **4.36%** [3.90, 4.82%] | `poor + poor_record` (n=7,478, 624 towns) = **1.72%** [1.45, 2.00%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,474 / 7,478 | -0.31 pp | [-0.70, +0.08 pp] | 0.1236 |
| `wealth effect | reliability=good_record` | 7,460 / 7,455 | -0.59 pp | [-1.20, +0.02 pp] | 0.0576 |
| `reliability effect | wealth=poor` | 7,455 / 7,478 | +2.63 pp*** | [+2.10, +3.17 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,460 / 7,474 | +2.35 pp*** | [+1.86, +2.84 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,461, 624 towns) = **2.49%** [2.16, 2.82%] | `close_friend + citizen` (n=7,467, 624 towns) = **2.56%** [2.22, 2.90%] | `stranger + mayor` (n=7,470, 624 towns) = **3.20%** [2.80, 3.60%] | `stranger + citizen` (n=7,469, 624 towns) = **3.01%** [2.63, 3.39%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,467 / 7,469 | -0.45 pp | [-0.96, +0.06 pp] | 0.0807 |
| `closeness effect | authority=mayor` | 7,461 / 7,470 | -0.71 pp** | [-1.22, -0.19 pp] | 0.0074 |
| `authority effect | closeness=stranger` | 7,470 / 7,469 | +0.19 pp | [-0.36, +0.74 pp] | 0.5041 |
| `authority effect | closeness=close_friend` | 7,461 / 7,467 | -0.07 pp | [-0.54, +0.41 pp] | 0.7849 |


**Outcome: SKEPTICAL (%)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 11.42% | 16.22% | -4.80 pp*** | [-5.57, -4.04 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 13.09% | 14.55% | -1.47 pp*** | [-2.23, -0.70 pp] | 0.0002 | 0.0007 |
| main | reliability | `good_record - poor_record` | 7.74% | 19.90% | -12.16 pp*** | [-12.93, -11.40 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 12.28% | 15.36% | -3.07 pp*** | [-3.84, -2.31 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 13.66% | 13.98% | -0.32 pp | [-1.09, +0.44 pp] | 0.4118 | 0.4118 |
| main | age | `old - young` | 14.09% | 13.55% | +0.55 pp | [-0.22, +1.31 pp] | 0.1620 | 0.3240 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.05 pp | -10.65 pp | +11.70 pp*** | [+10.17, +13.23 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.40 pp | -3.33 pp | +3.73 pp*** | [+2.20, +5.26 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.09 pp | -6.06 pp | +5.98 pp*** | [+4.45, +7.51 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -3.95 pp | -5.65 pp | +1.70 pp | [+0.17, +3.23 pp] | 0.0293 | 0.0879 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,456, 624 towns) = **8.26%** [7.65, 8.88%] | `close_friend + poor_record` (n=7,472, 624 towns) = **14.57%** [13.81, 15.34%] | `stranger + good_record` (n=7,459, 624 towns) = **7.21%** [6.64, 7.78%] | `stranger + poor_record` (n=7,480, 624 towns) = **25.23%** [24.20, 26.25%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,472 / 7,480 | -10.65 pp*** | [-11.93, -9.38 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,456 / 7,459 | +1.05 pp* | [+0.21, +1.89 pp] | 0.0142 |
| `reliability effect | closeness=stranger` | 7,459 / 7,480 | -18.01 pp*** | [-19.19, -16.84 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,456 / 7,472 | -6.31 pp*** | [-7.29, -5.33 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,458, 624 towns) = **7.94%** [7.34, 8.54%] | `mayor + poor_record` (n=7,473, 624 towns) = **18.23%** [17.36, 19.11%] | `citizen + good_record` (n=7,457, 624 towns) = **7.54%** [6.95, 8.12%] | `citizen + poor_record` (n=7,479, 624 towns) = **21.57%** [20.63, 22.50%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,473 / 7,479 | -3.33 pp*** | [-4.61, -2.05 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 7,458 / 7,457 | +0.40 pp | [-0.44, +1.24 pp] | 0.3479 |
| `reliability effect | authority=citizen` | 7,457 / 7,479 | -14.03 pp*** | [-15.13, -12.93 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,458 / 7,473 | -10.30 pp*** | [-11.35, -9.24 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,460, 624 towns) = **7.69%** [7.10, 8.29%] | `rich + poor_record` (n=7,474, 624 towns) = **16.87%** [16.05, 17.69%] | `poor + good_record` (n=7,455, 624 towns) = **7.78%** [7.19, 8.37%] | `poor + poor_record` (n=7,478, 624 towns) = **22.93%** [21.95, 23.91%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,474 / 7,478 | -6.06 pp*** | [-7.34, -4.78 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 7,460 / 7,455 | -0.09 pp | [-0.92, +0.75 pp] | 0.8416 |
| `reliability effect | wealth=poor` | 7,455 / 7,478 | -15.15 pp*** | [-16.30, -14.00 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,460 / 7,474 | -9.17 pp*** | [-10.18, -8.17 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,461, 624 towns) = **11.11%** [10.41, 11.81%] | `close_friend + citizen` (n=7,467, 624 towns) = **11.72%** [11.04, 12.41%] | `stranger + mayor` (n=7,470, 624 towns) = **15.06%** [14.27, 15.86%] | `stranger + citizen` (n=7,469, 624 towns) = **17.38%** [16.52, 18.24%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,467 / 7,469 | -5.65 pp*** | [-6.76, -4.55 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 7,461 / 7,470 | -3.95 pp*** | [-5.01, -2.89 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 7,470 / 7,469 | -2.32 pp*** | [-3.49, -1.14 pp] | 0.0001 |
| `authority effect | closeness=close_friend` | 7,461 / 7,467 | -0.62 pp | [-1.60, +0.37 pp] | 0.2188 |


**Outcome: CHECKED_TRUE (%)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.14% | 0.03% | +0.11 pp* | [+0.04, +0.17 pp] | 0.0015 | 0.0154 |
| main | authority | `mayor - citizen` | 0.09% | 0.08% | +0.01 pp | [-0.05, +0.08 pp] | 0.6914 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.05% | 0.12% | -0.07 pp | [-0.13, -0.00 pp] | 0.0484 | 0.4352 |
| main | wealth | `rich - poor` | 0.10% | 0.07% | +0.03 pp | [-0.04, +0.09 pp] | 0.4281 | 1.0000 |
| main | gender | `woman - man` | 0.09% | 0.09% | -0.00 pp | [-0.07, +0.07 pp] | 0.9772 | 1.0000 |
| main | age | `old - young` | 0.10% | 0.07% | +0.03 pp | [-0.04, +0.09 pp] | 0.4271 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.08 pp | +0.13 pp | -0.05 pp | [-0.19, +0.08 pp] | 0.4294 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.03 pp | +0.05 pp | -0.08 pp | [-0.21, +0.05 pp] | 0.2340 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.00 pp | +0.05 pp | -0.05 pp | [-0.19, +0.08 pp] | 0.4283 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.11 pp | +0.11 pp | +0.00 pp | [-0.13, +0.13 pp] | 0.9973 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,456, 624 towns) = **0.09%** [0.02, 0.16%] | `close_friend + poor_record` (n=7,472, 624 towns) = **0.19%** [0.09, 0.28%] | `stranger + good_record` (n=7,459, 624 towns) = **0.01%** [-0.01, 0.04%] | `stranger + poor_record` (n=7,480, 624 towns) = **0.05%** [0.00, 0.11%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,472 / 7,480 | +0.13 pp* | [+0.02, +0.24 pp] | 0.0172 |
| `closeness effect | reliability=good_record` | 7,456 / 7,459 | +0.08 pp* | [+0.01, +0.15 pp] | 0.0329 |
| `reliability effect | closeness=stranger` | 7,459 / 7,480 | -0.04 pp | [-0.10, +0.02 pp] | 0.1793 |
| `reliability effect | closeness=close_friend` | 7,456 / 7,472 | -0.09 pp | [-0.21, +0.03 pp] | 0.1236 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,458, 624 towns) = **0.04%** [-0.01, 0.09%] | `mayor + poor_record` (n=7,473, 624 towns) = **0.15%** [0.06, 0.23%] | `citizen + good_record` (n=7,457, 624 towns) = **0.07%** [0.01, 0.13%] | `citizen + poor_record` (n=7,479, 624 towns) = **0.09%** [0.02, 0.16%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,473 / 7,479 | +0.05 pp | [-0.06, +0.16 pp] | 0.3394 |
| `authority effect | reliability=good_record` | 7,458 / 7,457 | -0.03 pp | [-0.10, +0.05 pp] | 0.4766 |
| `reliability effect | authority=citizen` | 7,457 / 7,479 | -0.03 pp | [-0.12, +0.06 pp] | 0.5643 |
| `reliability effect | authority=mayor` | 7,458 / 7,473 | -0.11 pp* | [-0.20, -0.01 pp] | 0.0308 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,460, 624 towns) = **0.05%** [0.00, 0.11%] | `rich + poor_record` (n=7,474, 624 towns) = **0.15%** [0.06, 0.23%] | `poor + good_record` (n=7,455, 624 towns) = **0.05%** [0.00, 0.11%] | `poor + poor_record` (n=7,478, 624 towns) = **0.09%** [0.03, 0.16%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,474 / 7,478 | +0.05 pp | [-0.06, +0.16 pp] | 0.3401 |
| `wealth effect | reliability=good_record` | 7,460 / 7,455 | +0.00 pp | [-0.07, +0.07 pp] | 0.9997 |
| `reliability effect | wealth=poor` | 7,455 / 7,478 | -0.04 pp | [-0.13, +0.05 pp] | 0.3631 |
| `reliability effect | wealth=rich` | 7,460 / 7,474 | -0.09 pp | [-0.19, +0.01 pp] | 0.0686 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,461, 624 towns) = **0.15%** [0.06, 0.23%] | `close_friend + citizen` (n=7,467, 624 towns) = **0.13%** [0.05, 0.22%] | `stranger + mayor` (n=7,470, 624 towns) = **0.04%** [-0.01, 0.09%] | `stranger + citizen` (n=7,469, 624 towns) = **0.03%** [-0.01, 0.06%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,467 / 7,469 | +0.11 pp* | [+0.02, +0.20 pp] | 0.0201 |
| `closeness effect | authority=mayor` | 7,461 / 7,470 | +0.11 pp* | [+0.01, +0.20 pp] | 0.0305 |
| `authority effect | closeness=stranger` | 7,470 / 7,469 | +0.01 pp | [-0.05, +0.07 pp] | 0.6554 |
| `authority effect | closeness=close_friend` | 7,461 / 7,467 | +0.01 pp | [-0.11, +0.13 pp] | 0.8236 |


**Outcome: CHECKED_FALSE (%)** (n=29,867, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 82.83% | 76.95% | +5.88 pp*** | [+5.01, +6.75 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 80.84% | 78.95% | +1.89 pp*** | [+1.02, +2.76 pp] | <0.0001 | 0.0001 |
| main | reliability | `good_record - poor_record` | 84.63% | 75.16% | +9.47 pp*** | [+8.60, +10.34 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 81.64% | 78.15% | +3.49 pp*** | [+2.62, +4.36 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 79.69% | 80.09% | -0.40 pp | [-1.27, +0.48 pp] | 0.3726 | 0.5016 |
| main | age | `old - young` | 79.64% | 80.15% | -0.51 pp | [-1.38, +0.36 pp] | 0.2508 | 0.5016 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.12 pp | +11.65 pp | -11.53 pp*** | [-13.28, -9.79 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.36 pp | +3.42 pp | -3.06 pp** | [-4.80, -1.32 pp] | 0.0006 | 0.0023 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.80 pp | +6.18 pp | -5.38 pp*** | [-7.12, -3.64 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +4.87 pp | +6.90 pp | -2.03 pp | [-3.77, -0.29 pp] | 0.0225 | 0.0676 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=7,456, 624 towns) = **84.68%** [83.93, 85.44%] | `close_friend + poor_record` (n=7,472, 624 towns) = **80.98%** [80.13, 81.83%] | `stranger + good_record` (n=7,459, 624 towns) = **84.57%** [83.82, 85.32%] | `stranger + poor_record` (n=7,480, 624 towns) = **69.33%** [68.25, 70.42%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 7,472 / 7,480 | +11.65 pp*** | [+10.27, +13.03 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 7,456 / 7,459 | +0.12 pp | [-0.95, +1.18 pp] | 0.8306 |
| `reliability effect | closeness=stranger` | 7,459 / 7,480 | +15.24 pp*** | [+13.92, +16.56 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 7,456 / 7,472 | +3.70 pp*** | [+2.57, +4.84 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=7,458, 624 towns) = **84.81%** [84.06, 85.56%] | `mayor + poor_record` (n=7,473, 624 towns) = **76.87%** [75.93, 77.81%] | `citizen + good_record` (n=7,457, 624 towns) = **84.44%** [83.69, 85.20%] | `citizen + poor_record` (n=7,479, 624 towns) = **73.45%** [72.44, 74.46%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 7,473 / 7,479 | +3.42 pp*** | [+2.04, +4.80 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 7,458 / 7,457 | +0.36 pp | [-0.70, +1.43 pp] | 0.5027 |
| `reliability effect | authority=citizen` | 7,457 / 7,479 | +11.00 pp*** | [+9.74, +12.26 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 7,458 / 7,473 | +7.94 pp*** | [+6.74, +9.14 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=7,460, 624 towns) = **85.03%** [84.28, 85.78%] | `rich + poor_record` (n=7,474, 624 towns) = **78.25%** [77.34, 79.15%] | `poor + good_record` (n=7,455, 624 towns) = **84.23%** [83.47, 84.98%] | `poor + poor_record` (n=7,478, 624 towns) = **72.07%** [71.03, 73.11%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 7,474 / 7,478 | +6.18 pp*** | [+4.80, +7.56 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 7,460 / 7,455 | +0.80 pp | [-0.26, +1.87 pp] | 0.1398 |
| `reliability effect | wealth=poor` | 7,455 / 7,478 | +12.16 pp*** | [+10.87, +13.44 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 7,460 / 7,474 | +6.78 pp*** | [+5.61, +7.95 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=7,461, 624 towns) = **83.27%** [82.49, 84.06%] | `close_friend + citizen` (n=7,467, 624 towns) = **82.39%** [81.58, 83.21%] | `stranger + mayor` (n=7,470, 624 towns) = **78.40%** [77.49, 79.31%] | `stranger + citizen` (n=7,469, 624 towns) = **75.50%** [74.54, 76.45%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 7,467 / 7,469 | +6.90 pp*** | [+5.64, +8.16 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 7,461 / 7,470 | +4.87 pp*** | [+3.67, +6.07 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 7,470 / 7,469 | +2.91 pp*** | [+1.59, +4.23 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 7,461 / 7,467 | +0.88 pp | [-0.26, +2.02 pp] | 0.1292 |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Outcome: Belief Score (Valid Mentioning)** (n=14,894, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0030 | 0.0079 | -0.0048*** | [-0.0066, -0.0031] | <0.0001 | <0.0001 | +0.0000 (p=1.0000) |
| main | authority | `mayor - citizen` | 0.0057 | 0.0052 | +0.0005 | [-0.0012, +0.0023] | 0.5543 | 1.0000 | +0.0000 (p=1.0000) |
| main | reliability | `good_record - poor_record` | 0.0042 | 0.0067 | -0.0026* | [-0.0043, -0.0008] | 0.0043 | 0.0343 | +0.0000 (p=1.0000) |
| main | wealth | `rich - poor` | 0.0046 | 0.0063 | -0.0017 | [-0.0035, +0.0000] | 0.0510 | 0.3567 | +0.0000 (p=1.0000) |
| main | gender | `woman - man` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0030] | 0.1731 | 1.0000 | +0.0000 (p=1.0000) |
| main | age | `old - young` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0030] | 0.1768 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0013 | -0.0083 | +0.0070*** | [+0.0035, +0.0105] | <0.0001 | 0.0008 | +0.0000 (p=1.0000) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0016 | -0.0005 | +0.0021 | [-0.0014, +0.0056] | 0.2307 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0019 | -0.0016 | -0.0003 | [-0.0038, +0.0032] | 0.8776 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.0044 | -0.0052 | +0.0008 | [-0.0027, +0.0043] | 0.6492 | 1.0000 | +0.0000 (p=1.0000) |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,722, 624 towns) = **0.0035** [0.0019, 0.0051] | `close_friend + poor_record` (n=3,726, 624 towns) = **0.0025** [0.0012, 0.0039] | `stranger + good_record` (n=3,724, 624 towns) = **0.0048** [0.0033, 0.0064] | `stranger + poor_record` (n=3,722, 624 towns) = **0.0109** [0.0085, 0.0132]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,726 / 3,722 | -0.0083*** | [-0.0110, -0.0056] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,722 / 3,724 | -0.0013 | [-0.0036, +0.0009] | 0.2404 |
| `reliability effect | closeness=stranger` | 3,724 / 3,722 | -0.0060*** | [-0.0089, -0.0032] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,722 / 3,726 | +0.0009 | [-0.0011, +0.0030] | 0.3701 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,728, 624 towns) = **0.0050** [0.0032, 0.0067] | `mayor + poor_record` (n=3,724, 624 towns) = **0.0064** [0.0045, 0.0084] | `citizen + good_record` (n=3,718, 624 towns) = **0.0034** [0.0020, 0.0048] | `citizen + poor_record` (n=3,724, 624 towns) = **0.0070** [0.0051, 0.0089]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,724 / 3,724 | -0.0005 | [-0.0032, +0.0022] | 0.6929 |
| `authority effect | reliability=good_record` | 3,728 / 3,718 | +0.0016 | [-0.0006, +0.0038] | 0.1617 |
| `reliability effect | authority=citizen` | 3,718 / 3,724 | -0.0036** | [-0.0060, -0.0013] | 0.0026 |
| `reliability effect | authority=mayor` | 3,728 / 3,724 | -0.0015 | [-0.0041, +0.0011] | 0.2624 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,722, 624 towns) = **0.0032** [0.0018, 0.0046] | `rich + poor_record` (n=3,722, 624 towns) = **0.0059** [0.0040, 0.0078] | `poor + good_record` (n=3,724, 624 towns) = **0.0051** [0.0034, 0.0068] | `poor + poor_record` (n=3,726, 624 towns) = **0.0075** [0.0056, 0.0095]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,722 / 3,726 | -0.0016 | [-0.0043, +0.0011] | 0.2421 |
| `wealth effect | reliability=good_record` | 3,722 / 3,724 | -0.0019 | [-0.0041, +0.0004] | 0.0998 |
| `reliability effect | wealth=poor` | 3,724 / 3,726 | -0.0024 | [-0.0050, +0.0002] | 0.0685 |
| `reliability effect | wealth=rich` | 3,722 / 3,722 | -0.0027* | [-0.0050, -0.0003] | 0.0248 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,726, 624 towns) = **0.0035** [0.0019, 0.0051] | `close_friend + citizen` (n=3,722, 624 towns) = **0.0026** [0.0013, 0.0038] | `stranger + mayor` (n=3,726, 624 towns) = **0.0079** [0.0059, 0.0099] | `stranger + citizen` (n=3,720, 624 towns) = **0.0078** [0.0058, 0.0098]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,722 / 3,720 | -0.0052*** | [-0.0076, -0.0029] | <0.0001 |
| `closeness effect | authority=mayor` | 3,726 / 3,726 | -0.0044*** | [-0.0070, -0.0018] | 0.0008 |
| `authority effect | closeness=stranger` | 3,726 / 3,720 | +0.0001 | [-0.0027, +0.0030] | 0.9329 |
| `authority effect | closeness=close_friend` | 3,726 / 3,722 | +0.0009 | [-0.0011, +0.0030] | 0.3728 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0030 | 0.0078 | -0.0048*** | [-0.0066, -0.0031] | <0.0001 | <0.0001 | -0.0048 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.0057 | 0.0051 | +0.0005 | [-0.0012, +0.0023] | 0.5465 | 1.0000 | +0.0005 (p=0.5514) |
| main | reliability | `good_record - poor_record` | 0.0041 | 0.0067 | -0.0025* | [-0.0043, -0.0008] | 0.0043 | 0.0348 | -0.0025 (p=0.0048) |
| main | wealth | `rich - poor` | 0.0045 | 0.0063 | -0.0017 | [-0.0035, +0.0000] | 0.0511 | 0.3576 | -0.0017 (p=0.0540) |
| main | gender | `woman - man` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0030] | 0.1754 | 1.0000 | +0.0012 (p=0.1804) |
| main | age | `old - young` | 0.0060 | 0.0048 | +0.0012 | [-0.0005, +0.0029] | 0.1760 | 1.0000 | +0.0012 (p=0.1813) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0013 | -0.0083 | +0.0069*** | [+0.0035, +0.0104] | <0.0001 | 0.0008 | +0.0069 (p=0.0001) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0016 | -0.0005 | +0.0021 | [-0.0014, +0.0056] | 0.2301 | 1.0000 | +0.0021 (p=0.2357) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0019 | -0.0016 | -0.0003 | [-0.0038, +0.0032] | 0.8787 | 1.0000 | -0.0003 (p=0.8802) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.0044 | -0.0052 | +0.0008 | [-0.0027, +0.0043] | 0.6544 | 1.0000 | +0.0008 (p=0.6583) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0052 | 0.0105 | -0.0053*** | [-0.0074, -0.0032] | <0.0001 | <0.0001 | -0.0053 (p=<0.0001) |
| main | authority | `mayor - citizen` | 0.0078 | 0.0079 | -0.0002 | [-0.0023, +0.0019] | 0.8529 | 1.0000 | -0.0002 (p=0.8533) |
| main | reliability | `good_record - poor_record` | 0.0066 | 0.0091 | -0.0025 | [-0.0046, -0.0004] | 0.0204 | 0.1629 | -0.0025 (p=0.0206) |
| main | wealth | `rich - poor` | 0.0071 | 0.0086 | -0.0015 | [-0.0036, +0.0006] | 0.1498 | 1.0000 | -0.0015 (p=0.1506) |
| main | gender | `woman - man` | 0.0085 | 0.0072 | +0.0014 | [-0.0007, +0.0035] | 0.1983 | 1.0000 | +0.0014 (p=0.1983) |
| main | age | `old - young` | 0.0085 | 0.0072 | +0.0013 | [-0.0008, +0.0034] | 0.2324 | 1.0000 | +0.0013 (p=0.2332) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0015 | -0.0091 | +0.0076** | [+0.0034, +0.0118] | 0.0003 | 0.0031 | +0.0076 (p=0.0004) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0004 | -0.0008 | +0.0012 | [-0.0030, +0.0054] | 0.5737 | 1.0000 | +0.0012 (p=0.5746) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0017 | -0.0013 | -0.0004 | [-0.0046, +0.0038] | 0.8487 | 1.0000 | -0.0004 (p=0.8488) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.0045 | -0.0060 | +0.0015 | [-0.0027, +0.0056] | 0.4923 | 1.0000 | +0.0015 (p=0.4933) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 98.50% | 87.07% | +11.43 pp*** | [+10.70, +12.16 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 94.07% | 91.51% | +2.56 pp*** | [+1.83, +3.30 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 99.64% | 85.94% | +13.70 pp*** | [+12.97, +14.43 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 95.05% | 90.53% | +4.51 pp*** | [+3.78, +5.25 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 92.65% | 92.93% | -0.27 pp | [-1.01, +0.46 pp] | 0.4632 | 0.9263 |
| main | age | `old - young` | 92.86% | 92.72% | +0.13 pp | [-0.60, +0.87 pp] | 0.7209 | 0.9263 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.24 pp | +22.62 pp | -22.38 pp*** | [-23.85, -20.92 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.08 pp | +5.21 pp | -5.29 pp*** | [-6.75, -3.82 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.24 pp | +8.79 pp | -8.55 pp*** | [-10.01, -7.08 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +9.46 pp | +13.41 pp | -3.95 pp*** | [-5.42, -2.49 pp] | <0.0001 | <0.0001 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,744, 624 towns) = **99.76%** [99.59, 99.93%] | `close_friend + poor_record` (n=3,744, 624 towns) = **97.25%** [96.67, 97.82%] | `stranger + good_record` (n=3,744, 624 towns) = **99.52%** [99.29, 99.75%] | `stranger + poor_record` (n=3,744, 624 towns) = **74.63%** [73.31, 75.94%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,744 / 3,744 | +22.62 pp*** | [+21.19, +24.06 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,744 / 3,744 | +0.24 pp | [-0.05, +0.53 pp] | 0.1039 |
| `reliability effect | closeness=stranger` | 3,744 / 3,744 | +24.89 pp*** | [+23.56, +26.23 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,744 / 3,744 | +2.51 pp*** | [+1.91, +3.11 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,744, 624 towns) = **99.60%** [99.38, 99.81%] | `mayor + poor_record` (n=3,744, 624 towns) = **88.54%** [87.62, 89.47%] | `citizen + good_record` (n=3,744, 624 towns) = **99.68%** [99.48, 99.87%] | `citizen + poor_record` (n=3,744, 624 towns) = **83.33%** [82.23, 84.43%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,744 / 3,744 | +5.21 pp*** | [+3.77, +6.64 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 3,744 / 3,744 | -0.08 pp | [-0.37, +0.21 pp] | 0.5878 |
| `reliability effect | authority=citizen` | 3,744 / 3,744 | +16.35 pp*** | [+15.23, +17.46 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,744 / 3,744 | +11.06 pp*** | [+10.11, +12.01 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,744, 624 towns) = **99.76%** [99.58, 99.94%] | `rich + poor_record` (n=3,744, 624 towns) = **90.33%** [89.43, 91.23%] | `poor + good_record` (n=3,744, 624 towns) = **99.52%** [99.29, 99.75%] | `poor + poor_record` (n=3,744, 624 towns) = **81.54%** [80.42, 82.67%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,744 / 3,744 | +8.79 pp*** | [+7.35, +10.22 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,744 / 3,744 | +0.24 pp | [-0.05, +0.53 pp] | 0.1039 |
| `reliability effect | wealth=poor` | 3,744 / 3,744 | +17.98 pp*** | [+16.83, +19.12 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,744 / 3,744 | +9.43 pp*** | [+8.51, +10.34 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,744, 624 towns) = **98.80%** [98.38, 99.21%] | `close_friend + citizen` (n=3,744, 624 towns) = **98.21%** [97.78, 98.65%] | `stranger + mayor` (n=3,744, 624 towns) = **89.34%** [88.49, 90.20%] | `stranger + citizen` (n=3,744, 624 towns) = **84.80%** [83.77, 85.83%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,744 / 3,744 | +13.41 pp*** | [+12.29, +14.52 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,744 / 3,744 | +9.46 pp*** | [+8.51, +10.40 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,744 / 3,744 | +4.54 pp*** | [+3.20, +5.88 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,744 / 3,744 | +0.59 pp | [-0.01, +1.19 pp] | 0.0553 |


**Outcome: NOT_MENTIONED (%)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.44% | 0.53% | -0.09 pp | [-0.32, +0.14 pp] | 0.4259 | 1.0000 |
| main | authority | `mayor - citizen` | 0.41% | 0.56% | -0.15 pp | [-0.38, +0.08 pp] | 0.2097 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.49% | 0.48% | +0.01 pp | [-0.22, +0.24 pp] | 0.9091 | 1.0000 |
| main | wealth | `rich - poor` | 0.51% | 0.47% | +0.04 pp | [-0.19, +0.27 pp] | 0.7307 | 1.0000 |
| main | gender | `woman - man` | 0.50% | 0.47% | +0.03 pp | [-0.20, +0.26 pp] | 0.7771 | 1.0000 |
| main | age | `old - young` | 0.49% | 0.48% | +0.01 pp | [-0.22, +0.24 pp] | 0.9075 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.03 pp | -0.16 pp | +0.13 pp | [-0.33, +0.59 pp] | 0.5679 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.24 pp | -0.05 pp | -0.19 pp | [-0.65, +0.27 pp] | 0.4232 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.03 pp | +0.05 pp | -0.03 pp | [-0.49, +0.43 pp] | 0.9083 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.03 pp | -0.16 pp | +0.13 pp | [-0.33, +0.59 pp] | 0.5693 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,740, 624 towns) = **0.48%** [0.26, 0.70%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.40%** [0.18, 0.63%] | `stranger + good_record` (n=3,743, 624 towns) = **0.51%** [0.27, 0.74%] | `stranger + poor_record` (n=3,743, 624 towns) = **0.56%** [0.33, 0.80%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,743 | -0.16 pp | [-0.49, +0.17 pp] | 0.3367 |
| `closeness effect | reliability=good_record` | 3,740 / 3,743 | -0.03 pp | [-0.35, +0.30 pp] | 0.8728 |
| `reliability effect | closeness=stranger` | 3,743 / 3,743 | -0.05 pp | [-0.39, +0.28 pp] | 0.7536 |
| `reliability effect | closeness=close_friend` | 3,740 / 3,741 | +0.08 pp | [-0.23, +0.39 pp] | 0.6172 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,742, 624 towns) = **0.37%** [0.18, 0.57%] | `mayor + poor_record` (n=3,741, 624 towns) = **0.45%** [0.23, 0.68%] | `citizen + good_record` (n=3,741, 624 towns) = **0.61%** [0.36, 0.87%] | `citizen + poor_record` (n=3,743, 624 towns) = **0.51%** [0.27, 0.74%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,741 / 3,743 | -0.05 pp | [-0.38, +0.27 pp] | 0.7500 |
| `authority effect | reliability=good_record` | 3,742 / 3,741 | -0.24 pp | [-0.56, +0.08 pp] | 0.1434 |
| `reliability effect | authority=citizen` | 3,741 / 3,743 | +0.11 pp | [-0.24, +0.46 pp] | 0.5480 |
| `reliability effect | authority=mayor` | 3,742 / 3,741 | -0.08 pp | [-0.38, +0.22 pp] | 0.5962 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,741, 624 towns) = **0.51%** [0.28, 0.73%] | `rich + poor_record` (n=3,741, 624 towns) = **0.51%** [0.27, 0.74%] | `poor + good_record` (n=3,742, 624 towns) = **0.48%** [0.25, 0.71%] | `poor + poor_record` (n=3,743, 624 towns) = **0.45%** [0.23, 0.68%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,741 / 3,743 | +0.05 pp | [-0.27, +0.38 pp] | 0.7469 |
| `wealth effect | reliability=good_record` | 3,741 / 3,742 | +0.03 pp | [-0.30, +0.35 pp] | 0.8705 |
| `reliability effect | wealth=poor` | 3,742 / 3,743 | +0.03 pp | [-0.29, +0.35 pp] | 0.8701 |
| `reliability effect | wealth=rich` | 3,741 / 3,741 | -0.00 pp | [-0.33, +0.33 pp] | 0.9994 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,741, 624 towns) = **0.40%** [0.19, 0.61%] | `close_friend + citizen` (n=3,740, 624 towns) = **0.48%** [0.25, 0.71%] | `stranger + mayor` (n=3,742, 624 towns) = **0.43%** [0.22, 0.63%] | `stranger + citizen` (n=3,744, 624 towns) = **0.64%** [0.38, 0.90%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,740 / 3,744 | -0.16 pp | [-0.51, +0.19 pp] | 0.3702 |
| `closeness effect | authority=mayor` | 3,741 / 3,742 | -0.03 pp | [-0.32, +0.27 pp] | 0.8609 |
| `authority effect | closeness=stranger` | 3,742 / 3,744 | -0.21 pp | [-0.55, +0.12 pp] | 0.2103 |
| `authority effect | closeness=close_friend` | 3,741 / 3,740 | -0.08 pp | [-0.39, +0.23 pp] | 0.6172 |


**Outcome: FACT (%)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.07% | 0.03% | +0.04 pp | [-0.03, +0.11 pp] | 0.2551 | 1.0000 |
| main | authority | `mayor - citizen` | 0.07% | 0.03% | +0.04 pp | [-0.03, +0.11 pp] | 0.2554 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.04% | 0.05% | -0.01 pp | [-0.08, +0.06 pp] | 0.7047 | 1.0000 |
| main | wealth | `rich - poor` | 0.05% | 0.04% | +0.01 pp | [-0.06, +0.08 pp] | 0.7036 | 1.0000 |
| main | gender | `woman - man` | 0.05% | 0.04% | +0.01 pp | [-0.06, +0.08 pp] | 0.7008 | 1.0000 |
| main | age | `old - young` | 0.08% | 0.01% | +0.07 pp | [-0.00, +0.14 pp] | 0.0580 | 0.5799 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.03 pp | +0.05 pp | -0.03 pp | [-0.16, +0.11 pp] | 0.7052 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.03 pp | +0.05 pp | -0.03 pp | [-0.17, +0.11 pp] | 0.7036 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.03 pp | +0.00 pp | +0.03 pp | [-0.11, +0.16 pp] | 0.7055 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.08 pp | +0.00 pp | +0.08 pp | [-0.06, +0.22 pp] | 0.2555 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,740, 624 towns) = **0.05%** [-0.02, 0.13%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.08%** [-0.01, 0.17%] | `stranger + good_record` (n=3,743, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + poor_record` (n=3,743, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,743 | +0.05 pp | [-0.05, +0.16 pp] | 0.3162 |
| `closeness effect | reliability=good_record` | 3,740 / 3,743 | +0.03 pp | [-0.06, +0.12 pp] | 0.5613 |
| `reliability effect | closeness=stranger` | 3,743 / 3,743 | -0.00 pp | [-0.07, +0.07 pp] | 0.9995 |
| `reliability effect | closeness=close_friend` | 3,740 / 3,741 | -0.03 pp | [-0.14, +0.09 pp] | 0.6540 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,742, 624 towns) = **0.05%** [-0.02, 0.13%] | `mayor + poor_record` (n=3,741, 624 towns) = **0.08%** [-0.01, 0.17%] | `citizen + good_record` (n=3,741, 624 towns) = **0.03%** [-0.03, 0.08%] | `citizen + poor_record` (n=3,743, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,741 / 3,743 | +0.05 pp | [-0.05, +0.16 pp] | 0.3159 |
| `authority effect | reliability=good_record` | 3,742 / 3,741 | +0.03 pp | [-0.06, +0.12 pp] | 0.5628 |
| `reliability effect | authority=citizen` | 3,741 / 3,743 | +0.00 pp | [-0.07, +0.07 pp] | 0.9990 |
| `reliability effect | authority=mayor` | 3,742 / 3,741 | -0.03 pp | [-0.14, +0.09 pp] | 0.6531 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,741, 624 towns) = **0.05%** [-0.02, 0.13%] | `rich + poor_record` (n=3,741, 624 towns) = **0.05%** [-0.02, 0.13%] | `poor + good_record` (n=3,742, 624 towns) = **0.03%** [-0.03, 0.08%] | `poor + poor_record` (n=3,743, 624 towns) = **0.05%** [-0.02, 0.13%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,741 / 3,743 | +0.00 pp | [-0.10, +0.10 pp] | 0.9986 |
| `wealth effect | reliability=good_record` | 3,741 / 3,742 | +0.03 pp | [-0.06, +0.12 pp] | 0.5623 |
| `reliability effect | wealth=poor` | 3,742 / 3,743 | -0.03 pp | [-0.12, +0.06 pp] | 0.5631 |
| `reliability effect | wealth=rich` | 3,741 / 3,741 | -0.00 pp | [-0.10, +0.10 pp] | 0.9993 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,741, 624 towns) = **0.11%** [0.00, 0.21%] | `close_friend + citizen` (n=3,740, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + mayor` (n=3,742, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + citizen` (n=3,744, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,740 / 3,744 | +0.00 pp | [-0.07, +0.07 pp] | 0.9990 |
| `closeness effect | authority=mayor` | 3,741 / 3,742 | +0.08 pp | [-0.04, +0.20 pp] | 0.1782 |
| `authority effect | closeness=stranger` | 3,742 / 3,744 | +0.00 pp | [-0.07, +0.07 pp] | 0.9998 |
| `authority effect | closeness=close_friend` | 3,741 / 3,740 | +0.08 pp | [-0.04, +0.20 pp] | 0.1782 |


**Outcome: UNCERTAIN (%)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.39% | 1.48% | -1.10 pp*** | [-1.40, -0.79 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 0.95% | 0.92% | +0.03 pp | [-0.28, +0.33 pp] | 0.8622 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.67% | 1.20% | -0.53 pp** | [-0.84, -0.23 pp] | 0.0006 | 0.0048 |
| main | wealth | `rich - poor` | 0.75% | 1.12% | -0.37 pp | [-0.68, -0.07 pp] | 0.0163 | 0.1139 |
| main | gender | `woman - man` | 1.04% | 0.83% | +0.22 pp | [-0.09, +0.52 pp] | 0.1668 | 1.0000 |
| main | age | `old - young` | 0.94% | 0.94% | +0.00 pp | [-0.30, +0.31 pp] | 0.9995 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.48 pp | -1.71 pp | +1.23 pp*** | [+0.62, +1.84 pp] | <0.0001 | 0.0007 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.21 pp | -0.16 pp | +0.37 pp | [-0.24, +0.98 pp] | 0.2296 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.37 pp | -0.37 pp | -0.00 pp | [-0.61, +0.61 pp] | 0.9984 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -1.15 pp | -1.04 pp | -0.11 pp | [-0.72, +0.50 pp] | 0.7287 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,740, 624 towns) = **0.43%** [0.21, 0.65%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.35%** [0.16, 0.53%] | `stranger + good_record` (n=3,743, 624 towns) = **0.91%** [0.61, 1.20%] | `stranger + poor_record` (n=3,743, 624 towns) = **2.06%** [1.61, 2.51%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,743 | -1.71 pp*** | [-2.20, -1.22 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,740 / 3,743 | -0.48 pp* | [-0.85, -0.11 pp] | 0.0107 |
| `reliability effect | closeness=stranger` | 3,743 / 3,743 | -1.15 pp*** | [-1.69, -0.61 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,740 / 3,741 | +0.08 pp | [-0.21, +0.37 pp] | 0.5859 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,742, 624 towns) = **0.78%** [0.49, 1.06%] | `mayor + poor_record` (n=3,741, 624 towns) = **1.12%** [0.79, 1.46%] | `citizen + good_record` (n=3,741, 624 towns) = **0.56%** [0.33, 0.80%] | `citizen + poor_record` (n=3,743, 624 towns) = **1.28%** [0.93, 1.63%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,741 / 3,743 | -0.16 pp | [-0.65, +0.33 pp] | 0.5186 |
| `authority effect | reliability=good_record` | 3,742 / 3,741 | +0.21 pp | [-0.15, +0.58 pp] | 0.2556 |
| `reliability effect | authority=citizen` | 3,741 / 3,743 | -0.72 pp*** | [-1.14, -0.30 pp] | 0.0008 |
| `reliability effect | authority=mayor` | 3,742 / 3,741 | -0.35 pp | [-0.79, +0.09 pp] | 0.1223 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,741, 624 towns) = **0.48%** [0.26, 0.70%] | `rich + poor_record` (n=3,741, 624 towns) = **1.02%** [0.69, 1.34%] | `poor + good_record` (n=3,742, 624 towns) = **0.86%** [0.56, 1.15%] | `poor + poor_record` (n=3,743, 624 towns) = **1.39%** [1.03, 1.75%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,741 / 3,743 | -0.37 pp | [-0.86, +0.11 pp] | 0.1317 |
| `wealth effect | reliability=good_record` | 3,741 / 3,742 | -0.37 pp* | [-0.74, -0.01 pp] | 0.0468 |
| `reliability effect | wealth=poor` | 3,742 / 3,743 | -0.53 pp* | [-1.00, -0.07 pp] | 0.0247 |
| `reliability effect | wealth=rich` | 3,741 / 3,741 | -0.53 pp** | [-0.93, -0.14 pp] | 0.0078 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,741, 624 towns) = **0.37%** [0.17, 0.58%] | `close_friend + citizen` (n=3,740, 624 towns) = **0.40%** [0.20, 0.60%] | `stranger + mayor` (n=3,742, 624 towns) = **1.52%** [1.13, 1.91%] | `stranger + citizen` (n=3,744, 624 towns) = **1.44%** [1.07, 1.81%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,740 / 3,744 | -1.04 pp*** | [-1.46, -0.62 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,741 / 3,742 | -1.15 pp*** | [-1.59, -0.71 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,742 / 3,744 | +0.08 pp | [-0.46, +0.62 pp] | 0.7675 |
| `authority effect | closeness=close_friend` | 3,741 / 3,740 | -0.03 pp | [-0.32, +0.26 pp] | 0.8551 |


**Outcome: SKEPTICAL (%)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 3.74% | 13.34% | -9.60 pp*** | [-10.41, -8.80 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 7.60% | 9.48% | -1.88 pp*** | [-2.69, -1.08 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 2.03% | 15.05% | -13.02 pp*** | [-13.83, -12.22 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 6.69% | 10.39% | -3.70 pp*** | [-4.50, -2.89 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 8.55% | 8.53% | +0.02 pp | [-0.78, +0.83 pp] | 0.9593 | 1.0000 |
| main | age | `old - young` | 8.60% | 8.48% | +0.12 pp | [-0.68, +0.93 pp] | 0.7663 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.59 pp | -19.79 pp | +20.38 pp*** | [+18.77, +21.99 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.64 pp | -4.40 pp | +5.05 pp*** | [+3.44, +6.66 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.05 pp | -7.34 pp | +7.29 pp*** | [+5.68, +8.90 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -7.56 pp | -11.64 pp | +4.08 pp*** | [+2.47, +5.69 pp] | <0.0001 | <0.0001 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,740, 624 towns) = **2.33%** [1.86, 2.79%] | `close_friend + poor_record` (n=3,741, 624 towns) = **5.16%** [4.45, 5.86%] | `stranger + good_record` (n=3,743, 624 towns) = **1.74%** [1.33, 2.15%] | `stranger + poor_record` (n=3,743, 624 towns) = **24.95%** [23.64, 26.26%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,743 | -19.79 pp*** | [-21.28, -18.31 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,740 / 3,743 | +0.59 pp | [-0.03, +1.21 pp] | 0.0624 |
| `reliability effect | closeness=stranger` | 3,743 / 3,743 | -23.22 pp*** | [-24.58, -21.85 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,740 / 3,741 | -2.83 pp*** | [-3.68, -1.99 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,742, 624 towns) = **2.35%** [1.89, 2.82%] | `mayor + poor_record` (n=3,741, 624 towns) = **12.85%** [11.86, 13.84%] | `citizen + good_record` (n=3,741, 624 towns) = **1.71%** [1.30, 2.12%] | `citizen + poor_record` (n=3,743, 624 towns) = **17.26%** [16.15, 18.36%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,741 / 3,743 | -4.40 pp*** | [-5.89, -2.92 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 3,742 / 3,741 | +0.64 pp* | [+0.02, +1.26 pp] | 0.0421 |
| `reliability effect | authority=citizen` | 3,741 / 3,743 | -15.55 pp*** | [-16.73, -14.37 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,742 / 3,741 | -10.50 pp*** | [-11.59, -9.41 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,741, 624 towns) = **2.00%** [1.56, 2.45%] | `rich + poor_record` (n=3,741, 624 towns) = **11.38%** [10.43, 12.33%] | `poor + good_record` (n=3,742, 624 towns) = **2.06%** [1.63, 2.49%] | `poor + poor_record` (n=3,743, 624 towns) = **18.73%** [17.59, 19.87%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,741 / 3,743 | -7.34 pp*** | [-8.83, -5.86 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,741 / 3,742 | -0.05 pp | [-0.67, +0.56 pp] | 0.8630 |
| `reliability effect | wealth=poor` | 3,742 / 3,743 | -16.67 pp*** | [-17.89, -15.45 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,741 / 3,741 | -9.38 pp*** | [-10.43, -8.33 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,741, 624 towns) = **3.82%** [3.21, 4.43%] | `close_friend + citizen` (n=3,740, 624 towns) = **3.66%** [3.08, 4.25%] | `stranger + mayor` (n=3,742, 624 towns) = **11.38%** [10.47, 12.29%] | `stranger + citizen` (n=3,744, 624 towns) = **15.30%** [14.28, 16.33%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,740 / 3,744 | -11.64 pp*** | [-12.82, -10.46 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,741 / 3,742 | -7.56 pp*** | [-8.66, -6.47 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,742 / 3,744 | -3.92 pp*** | [-5.29, -2.55 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,741 / 3,740 | +0.16 pp | [-0.68, +1.00 pp] | 0.7123 |


**Outcome: CHECKED_TRUE (%)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.04% | 0.01% | +0.03 pp | [-0.03, +0.08 pp] | 0.3155 | 1.0000 |
| main | authority | `mayor - citizen` | 0.03% | 0.03% | +0.00 pp | [-0.05, +0.05 pp] | 0.9990 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.04% | 0.01% | +0.03 pp | [-0.03, +0.08 pp] | 0.3158 | 1.0000 |
| main | wealth | `rich - poor` | 0.03% | 0.03% | +0.00 pp | [-0.05, +0.05 pp] | 0.9995 | 1.0000 |
| main | gender | `woman - man` | 0.03% | 0.03% | -0.00 pp | [-0.05, +0.05 pp] | 0.9800 | 1.0000 |
| main | age | `old - young` | 0.05% | -0.00% | +0.05 pp | [+0.00, +0.11 pp] | 0.0448 | 0.4484 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.08 pp | -0.03 pp | +0.11 pp | [+0.00, +0.21 pp] | 0.0448 | 0.4484 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.03 pp | -0.03 pp | +0.05 pp | [-0.05, +0.16 pp] | 0.3162 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.03 pp | +0.03 pp | -0.05 pp | [-0.16, +0.05 pp] | 0.3154 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.05 pp | +0.00 pp | +0.05 pp | [-0.05, +0.16 pp] | 0.3160 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,740, 624 towns) = **0.08%** [-0.01, 0.17%] | `close_friend + poor_record` (n=3,741, 624 towns) = **0.00%** [-0.00, 0.00%] | `stranger + good_record` (n=3,743, 624 towns) = **-0.00%** [-0.00, 0.00%] | `stranger + poor_record` (n=3,743, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,743 | -0.03 pp | [-0.08, +0.03 pp] | 0.3174 |
| `closeness effect | reliability=good_record` | 3,740 / 3,743 | +0.08 pp | [-0.01, +0.17 pp] | 0.0820 |
| `reliability effect | closeness=stranger` | 3,743 / 3,743 | -0.03 pp | [-0.08, +0.03 pp] | 0.3171 |
| `reliability effect | closeness=close_friend` | 3,740 / 3,741 | +0.08 pp | [-0.01, +0.17 pp] | 0.0821 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,742, 624 towns) = **0.05%** [-0.02, 0.13%] | `mayor + poor_record` (n=3,741, 624 towns) = **0.00%** [-0.00, 0.00%] | `citizen + good_record` (n=3,741, 624 towns) = **0.03%** [-0.03, 0.08%] | `citizen + poor_record` (n=3,743, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,741 / 3,743 | -0.03 pp | [-0.08, +0.03 pp] | 0.3178 |
| `authority effect | reliability=good_record` | 3,742 / 3,741 | +0.03 pp | [-0.06, +0.12 pp] | 0.5622 |
| `reliability effect | authority=citizen` | 3,741 / 3,743 | +0.00 pp | [-0.07, +0.07 pp] | 0.9992 |
| `reliability effect | authority=mayor` | 3,742 / 3,741 | +0.05 pp | [-0.02, +0.13 pp] | 0.1558 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,741, 624 towns) = **0.03%** [-0.03, 0.08%] | `rich + poor_record` (n=3,741, 624 towns) = **0.03%** [-0.03, 0.08%] | `poor + good_record` (n=3,742, 624 towns) = **0.05%** [-0.02, 0.13%] | `poor + poor_record` (n=3,743, 624 towns) = **-0.00%** [-0.00, 0.00%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,741 / 3,743 | +0.03 pp | [-0.03, +0.08 pp] | 0.3166 |
| `wealth effect | reliability=good_record` | 3,741 / 3,742 | -0.03 pp | [-0.12, +0.06 pp] | 0.5620 |
| `reliability effect | wealth=poor` | 3,742 / 3,743 | +0.05 pp | [-0.02, +0.13 pp] | 0.1558 |
| `reliability effect | wealth=rich` | 3,741 / 3,741 | -0.00 pp | [-0.07, +0.07 pp] | 0.9997 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,741, 624 towns) = **0.05%** [-0.02, 0.13%] | `close_friend + citizen` (n=3,740, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + mayor` (n=3,742, 624 towns) = **0.00%** [-0.00, 0.00%] | `stranger + citizen` (n=3,744, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,740 / 3,744 | +0.00 pp | [-0.07, +0.07 pp] | 0.9996 |
| `closeness effect | authority=mayor` | 3,741 / 3,742 | +0.05 pp | [-0.02, +0.13 pp] | 0.1556 |
| `authority effect | closeness=stranger` | 3,742 / 3,744 | -0.03 pp | [-0.08, +0.03 pp] | 0.3175 |
| `authority effect | closeness=close_friend` | 3,741 / 3,740 | +0.03 pp | [-0.06, +0.12 pp] | 0.5618 |


**Outcome: CHECKED_FALSE (%)** (n=14,967, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 95.32% | 84.60% | +10.72 pp*** | [+9.85, +11.60 pp] | <0.0001 | <0.0001 |
| main | authority | `mayor - citizen` | 90.94% | 88.98% | +1.96 pp*** | [+1.09, +2.84 pp] | <0.0001 | <0.0001 |
| main | reliability | `good_record - poor_record` | 96.73% | 83.19% | +13.53 pp*** | [+12.66, +14.41 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 91.97% | 87.95% | +4.02 pp*** | [+3.14, +4.89 pp] | <0.0001 | <0.0001 |
| main | gender | `woman - man` | 89.82% | 90.10% | -0.28 pp | [-1.16, +0.59 pp] | 0.5274 | 1.0000 |
| main | age | `old - young` | 89.83% | 90.09% | -0.26 pp | [-1.13, +0.62 pp] | 0.5662 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.19 pp | +21.64 pp | -21.83 pp*** | [-23.57, -20.08 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.67 pp | +4.59 pp | -5.26 pp*** | [-7.01, -3.51 pp] | <0.0001 | <0.0001 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.40 pp | +7.64 pp | -7.23 pp*** | [-8.98, -5.48 pp] | <0.0001 | <0.0001 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +8.60 pp | +12.84 pp | -4.24 pp*** | [-5.99, -2.49 pp] | <0.0001 | <0.0001 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,740, 624 towns) = **96.63%** [96.07, 97.20%] | `close_friend + poor_record` (n=3,741, 624 towns) = **94.01%** [93.26, 94.77%] | `stranger + good_record` (n=3,743, 624 towns) = **96.82%** [96.27, 97.37%] | `stranger + poor_record` (n=3,743, 624 towns) = **72.38%** [71.01, 73.74%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,741 / 3,743 | +21.64 pp*** | [+20.07, +23.20 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,740 / 3,743 | -0.19 pp | [-0.98, +0.60 pp] | 0.6382 |
| `reliability effect | closeness=stranger` | 3,743 / 3,743 | +24.44 pp*** | [+22.97, +25.92 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,740 / 3,741 | +2.62 pp*** | [+1.68, +3.56 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,742, 624 towns) = **96.39%** [95.81, 96.97%] | `mayor + poor_record` (n=3,741, 624 towns) = **85.49%** [84.44, 86.54%] | `citizen + good_record` (n=3,741, 624 towns) = **97.06%** [96.53, 97.59%] | `citizen + poor_record` (n=3,743, 624 towns) = **80.90%** [79.74, 82.05%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,741 / 3,743 | +4.59 pp*** | [+3.03, +6.15 pp] | <0.0001 |
| `authority effect | reliability=good_record` | 3,742 / 3,741 | -0.67 pp | [-1.46, +0.12 pp] | 0.0955 |
| `reliability effect | authority=citizen` | 3,741 / 3,743 | +16.16 pp*** | [+14.89, +17.43 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,742 / 3,741 | +10.90 pp*** | [+9.70, +12.10 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,741, 624 towns) = **96.93%** [96.38, 97.48%] | `rich + poor_record` (n=3,741, 624 towns) = **87.01%** [86.00, 88.03%] | `poor + good_record` (n=3,742, 624 towns) = **96.53%** [95.96, 97.09%] | `poor + poor_record` (n=3,743, 624 towns) = **79.38%** [78.19, 80.57%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,741 / 3,743 | +7.64 pp*** | [+6.07, +9.20 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,741 / 3,742 | +0.40 pp | [-0.38, +1.19 pp] | 0.3166 |
| `reliability effect | wealth=poor` | 3,742 / 3,743 | +17.15 pp*** | [+15.83, +18.47 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,741 / 3,741 | +9.91 pp*** | [+8.76, +11.07 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,741, 624 towns) = **95.24%** [94.56, 95.92%] | `close_friend + citizen` (n=3,740, 624 towns) = **95.40%** [94.75, 96.06%] | `stranger + mayor` (n=3,742, 624 towns) = **86.64%** [85.65, 87.63%] | `stranger + citizen` (n=3,744, 624 towns) = **82.56%** [81.47, 83.65%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,740 / 3,744 | +12.84 pp*** | [+11.57, +14.11 pp] | <0.0001 |
| `closeness effect | authority=mayor` | 3,741 / 3,742 | +8.60 pp*** | [+7.40, +9.81 pp] | <0.0001 |
| `authority effect | closeness=stranger` | 3,742 / 3,744 | +4.08 pp*** | [+2.61, +5.55 pp] | <0.0001 |
| `authority effect | closeness=close_friend` | 3,741 / 3,740 | -0.16 pp | [-1.10, +0.78 pp] | 0.7420 |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Outcome: Belief Score (Valid Mentioning)** (n=14,101, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0380 | 0.0337 | +0.0043 | [-0.0005, +0.0091] | 0.0782 | 0.7034 | +0.0043 (p=0.0828) |
| main | authority | `mayor - citizen` | 0.0361 | 0.0355 | +0.0006 | [-0.0042, +0.0054] | 0.8088 | 1.0000 | +0.0006 (p=0.8117) |
| main | reliability | `good_record - poor_record` | 0.0502 | 0.0215 | +0.0287*** | [+0.0238, +0.0335] | <0.0001 | <0.0001 | +0.0287 (p=<0.0001) |
| main | wealth | `rich - poor` | 0.0359 | 0.0358 | +0.0002 | [-0.0046, +0.0050] | 0.9427 | 1.0000 | +0.0002 (p=0.9436) |
| main | gender | `woman - man` | 0.0379 | 0.0338 | +0.0042 | [-0.0006, +0.0090] | 0.0898 | 0.7182 | +0.0042 (p=0.0946) |
| main | age | `old - young` | 0.0350 | 0.0367 | -0.0016 | [-0.0064, +0.0032] | 0.5018 | 1.0000 | -0.0016 (p=0.5088) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0021 | +0.0066 | -0.0045 | [-0.0141, +0.0051] | 0.3613 | 1.0000 | -0.0045 (p=0.3686) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0002 | +0.0010 | -0.0009 | [-0.0105, +0.0088] | 0.8605 | 1.0000 | -0.0009 (p=0.8625) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0023 | +0.0027 | -0.0050 | [-0.0146, +0.0047] | 0.3120 | 1.0000 | -0.0050 (p=0.3189) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0050 | +0.0036 | +0.0014 | [-0.0082, +0.0110] | 0.7772 | 1.0000 | +0.0014 (p=0.7807) |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, Belief Score (Valid Mentioning)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,554, 624 towns) = **0.0512** [0.0458, 0.0566] | `close_friend + poor_record` (n=3,549, 624 towns) = **0.0248** [0.0202, 0.0294] | `stranger + good_record` (n=3,462, 624 towns) = **0.0491** [0.0436, 0.0546] | `stranger + poor_record` (n=3,536, 624 towns) = **0.0182** [0.0147, 0.0218]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,549 / 3,536 | +0.0066* | [+0.0008, +0.0123] | 0.0259 |
| `closeness effect | reliability=good_record` | 3,554 / 3,462 | +0.0021 | [-0.0056, +0.0098] | 0.5959 |
| `reliability effect | closeness=stranger` | 3,462 / 3,536 | +0.0309*** | [+0.0244, +0.0374] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,554 / 3,549 | +0.0264*** | [+0.0193, +0.0335] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,541, 624 towns) = **0.0503** [0.0447, 0.0558] | `mayor + poor_record` (n=3,542, 624 towns) = **0.0220** [0.0179, 0.0261] | `citizen + good_record` (n=3,475, 624 towns) = **0.0501** [0.0448, 0.0554] | `citizen + poor_record` (n=3,543, 624 towns) = **0.0210** [0.0169, 0.0251]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,542 / 3,543 | +0.0010 | [-0.0048, +0.0068] | 0.7281 |
| `authority effect | reliability=good_record` | 3,541 / 3,475 | +0.0002 | [-0.0075, +0.0079] | 0.9671 |
| `reliability effect | authority=citizen` | 3,475 / 3,543 | +0.0291*** | [+0.0224, +0.0358] | <0.0001 |
| `reliability effect | authority=mayor` | 3,541 / 3,542 | +0.0282*** | [+0.0213, +0.0351] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,520, 624 towns) = **0.0490** [0.0436, 0.0544] | `rich + poor_record` (n=3,543, 624 towns) = **0.0228** [0.0185, 0.0272] | `poor + good_record` (n=3,496, 624 towns) = **0.0513** [0.0458, 0.0568] | `poor + poor_record` (n=3,542, 624 towns) = **0.0202** [0.0163, 0.0240]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,543 / 3,542 | +0.0027 | [-0.0031, +0.0084] | 0.3669 |
| `wealth effect | reliability=good_record` | 3,520 / 3,496 | -0.0023 | [-0.0100, +0.0054] | 0.5570 |
| `reliability effect | wealth=poor` | 3,496 / 3,542 | +0.0311*** | [+0.0244, +0.0379] | <0.0001 |
| `reliability effect | wealth=rich` | 3,520 / 3,543 | +0.0262*** | [+0.0193, +0.0331] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,560, 624 towns) = **0.0386** [0.0335, 0.0437] | `close_friend + citizen` (n=3,543, 624 towns) = **0.0374** [0.0325, 0.0422] | `stranger + mayor` (n=3,523, 624 towns) = **0.0336** [0.0290, 0.0383] | `stranger + citizen` (n=3,475, 624 towns) = **0.0337** [0.0291, 0.0383]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,543 / 3,475 | +0.0036 | [-0.0031, +0.0103] | 0.2888 |
| `closeness effect | authority=mayor` | 3,560 / 3,523 | +0.0050 | [-0.0019, +0.0119] | 0.1535 |
| `authority effect | closeness=stranger` | 3,523 / 3,475 | -0.0001 | [-0.0066, +0.0064] | 0.9760 |
| `authority effect | closeness=close_friend` | 3,560 / 3,543 | +0.0013 | [-0.0058, +0.0084] | 0.7211 |


**Outcome: Belief (Silence=0.0 Sensitivity)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0363 | 0.0315 | +0.0048 | [+0.0002, +0.0093] | 0.0403 | 0.3623 | +0.0000 (p=1.0000) |
| main | authority | `mayor - citizen` | 0.0344 | 0.0334 | +0.0010 | [-0.0035, +0.0056] | 0.6616 | 1.0000 | +0.0000 (p=1.0000) |
| main | reliability | `good_record - poor_record` | 0.0474 | 0.0204 | +0.0269*** | [+0.0224, +0.0315] | <0.0001 | <0.0001 | +0.0000 (p=1.0000) |
| main | wealth | `rich - poor` | 0.0340 | 0.0337 | +0.0003 | [-0.0043, +0.0049] | 0.8970 | 1.0000 | +0.0000 (p=1.0000) |
| main | gender | `woman - man` | 0.0358 | 0.0320 | +0.0038 | [-0.0008, +0.0084] | 0.1017 | 0.8138 | +0.0000 (p=1.0000) |
| main | age | `old - young` | 0.0331 | 0.0346 | -0.0015 | [-0.0061, +0.0031] | 0.5202 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.0032 | +0.0063 | -0.0031 | [-0.0122, +0.0060] | 0.5065 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.0011 | +0.0010 | +0.0001 | [-0.0090, +0.0093] | 0.9800 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0020 | +0.0026 | -0.0045 | [-0.0136, +0.0046] | 0.3333 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.0054 | +0.0041 | +0.0013 | [-0.0078, +0.0104] | 0.7808 | 1.0000 | +0.0000 (p=1.0000) |

**Outcome: Belief (Silence=0.5 Sensitivity)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) | LMM Check |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.0594 | 0.0620 | -0.0027 | [-0.0082, +0.0029] | 0.3471 | 1.0000 | +0.0000 (p=1.0000) |
| main | authority | `mayor - citizen` | 0.0589 | 0.0625 | -0.0036 | [-0.0092, +0.0019] | 0.2024 | 1.0000 | +0.0000 (p=1.0000) |
| main | reliability | `good_record - poor_record` | 0.0753 | 0.0461 | +0.0293*** | [+0.0237, +0.0348] | <0.0001 | <0.0001 | +0.0000 (p=1.0000) |
| main | wealth | `rich - poor` | 0.0601 | 0.0613 | -0.0011 | [-0.0067, +0.0044] | 0.6894 | 1.0000 | +0.0000 (p=1.0000) |
| main | gender | `woman - man` | 0.0631 | 0.0583 | +0.0049 | [-0.0007, +0.0104] | 0.0857 | 0.6857 | +0.0000 (p=1.0000) |
| main | age | `old - young` | 0.0599 | 0.0615 | -0.0015 | [-0.0071, +0.0040] | 0.5878 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -0.0092 | +0.0038 | -0.0130 | [-0.0241, -0.0019] | 0.0220 | 0.1978 | +0.0000 (p=1.0000) |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.0078 | +0.0006 | -0.0084 | [-0.0195, +0.0027] | 0.1380 | 0.9660 | +0.0000 (p=1.0000) |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.0044 | +0.0022 | -0.0066 | [-0.0177, +0.0045] | 0.2440 | 1.0000 | +0.0000 (p=1.0000) |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.0006 | -0.0048 | +0.0042 | [-0.0069, +0.0153] | 0.4599 | 1.0000 | +0.0000 (p=1.0000) |

**Outcome: GO Rate (Verification %)** (n=14,976, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 28.47% | 28.67% | -0.20 pp | [-1.60, +1.20 pp] | 0.7795 | 1.0000 |
| main | authority | `mayor - citizen` | 29.05% | 28.10% | +0.95 pp | [-0.45, +2.35 pp] | 0.1852 | 1.0000 |
| main | reliability | `good_record - poor_record` | 35.23% | 21.92% | +13.31 pp*** | [+11.91, +14.72 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 29.47% | 27.67% | +1.80 pp | [+0.40, +3.21 pp] | 0.0118 | 0.0941 |
| main | gender | `woman - man` | 28.63% | 28.51% | +0.12 pp | [-1.29, +1.52 pp] | 0.8713 | 1.0000 |
| main | age | `old - young` | 28.50% | 28.65% | -0.15 pp | [-1.55, +1.26 pp] | 0.8374 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +3.85 pp | -4.25 pp | +8.09 pp*** | [+5.29, +10.90 pp] | <0.0001 | <0.0001 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.28 pp | +0.61 pp | +0.67 pp | [-2.14, +3.47 pp] | 0.6408 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +2.51 pp | +1.10 pp | +1.42 pp | [-1.39, +4.22 pp] | 0.3226 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.08 pp | -0.32 pp | +0.24 pp | [-2.56, +3.05 pp] | 0.8666 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, GO Rate (Verification %)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,744, 624 towns) = **37.15%** [35.61, 38.69%] | `close_friend + poor_record` (n=3,744, 624 towns) = **19.79%** [18.57, 21.01%] | `stranger + good_record` (n=3,744, 624 towns) = **33.31%** [31.78, 34.83%] | `stranger + poor_record` (n=3,744, 624 towns) = **24.04%** [22.74, 25.34%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,744 / 3,744 | -4.25 pp*** | [-6.03, -2.47 pp] | <0.0001 |
| `closeness effect | reliability=good_record` | 3,744 / 3,744 | +3.85 pp*** | [+1.68, +6.01 pp] | 0.0005 |
| `reliability effect | closeness=stranger` | 3,744 / 3,744 | +9.27 pp*** | [+7.27, +11.27 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,744 / 3,744 | +17.36 pp*** | [+15.40, +19.33 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,744, 624 towns) = **35.87%** [34.32, 37.42%] | `mayor + poor_record` (n=3,744, 624 towns) = **22.22%** [20.94, 23.51%] | `citizen + good_record` (n=3,744, 624 towns) = **34.59%** [33.08, 36.10%] | `citizen + poor_record` (n=3,744, 624 towns) = **21.61%** [20.37, 22.84%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,744 / 3,744 | +0.61 pp | [-1.17, +2.40 pp] | 0.4991 |
| `authority effect | reliability=good_record` | 3,744 / 3,744 | +1.28 pp | [-0.88, +3.45 pp] | 0.2462 |
| `reliability effect | authority=citizen` | 3,744 / 3,744 | +12.98 pp*** | [+11.03, +14.93 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,744 / 3,744 | +13.65 pp*** | [+11.64, +15.66 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,744, 624 towns) = **36.49%** [34.93, 38.04%] | `rich + poor_record` (n=3,744, 624 towns) = **22.46%** [21.19, 23.74%] | `poor + good_record` (n=3,744, 624 towns) = **33.97%** [32.46, 35.48%] | `poor + poor_record` (n=3,744, 624 towns) = **21.37%** [20.12, 22.61%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,744 / 3,744 | +1.10 pp | [-0.69, +2.88 pp] | 0.2283 |
| `wealth effect | reliability=good_record` | 3,744 / 3,744 | +2.51 pp* | [+0.34, +4.68 pp] | 0.0231 |
| `reliability effect | wealth=poor` | 3,744 / 3,744 | +12.61 pp*** | [+10.65, +14.56 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,744 / 3,744 | +14.02 pp*** | [+12.01, +16.03 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,744, 624 towns) = **29.01%** [27.58, 30.43%] | `close_friend + citizen` (n=3,744, 624 towns) = **27.94%** [26.58, 29.29%] | `stranger + mayor` (n=3,744, 624 towns) = **29.09%** [27.66, 30.51%] | `stranger + citizen` (n=3,744, 624 towns) = **28.26%** [26.85, 29.67%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,744 / 3,744 | -0.32 pp | [-2.27, +1.63 pp] | 0.7478 |
| `closeness effect | authority=mayor` | 3,744 / 3,744 | -0.08 pp | [-2.09, +1.93 pp] | 0.9378 |
| `authority effect | closeness=stranger` | 3,744 / 3,744 | +0.83 pp | [-1.17, +2.83 pp] | 0.4177 |
| `authority effect | closeness=close_friend` | 3,744 / 3,744 | +1.07 pp | [-0.90, +3.03 pp] | 0.2864 |


**Outcome: NOT_MENTIONED (%)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 4.62% | 6.11% | -1.49 pp*** | [-2.20, -0.78 pp] | <0.0001 | 0.0004 |
| main | authority | `mayor - citizen` | 4.90% | 5.83% | -0.93 pp | [-1.64, -0.21 pp] | 0.0109 | 0.0870 |
| main | reliability | `good_record - poor_record` | 5.60% | 5.13% | +0.47 pp | [-0.25, +1.18 pp] | 0.1984 | 1.0000 |
| main | wealth | `rich - poor` | 5.22% | 5.51% | -0.29 pp | [-1.00, +0.43 pp] | 0.4305 | 1.0000 |
| main | gender | `woman - man` | 5.47% | 5.26% | +0.21 pp | [-0.50, +0.93 pp] | 0.5608 | 1.0000 |
| main | age | `old - young` | 5.36% | 5.37% | -0.01 pp | [-0.72, +0.71 pp] | 0.9830 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | -2.48 pp | -0.50 pp | -1.98 pp | [-3.41, -0.55 pp] | 0.0066 | 0.0591 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -1.78 pp | -0.07 pp | -1.71 pp | [-3.13, -0.28 pp] | 0.0191 | 0.1340 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.50 pp | -0.08 pp | -0.42 pp | [-1.85, +1.01 pp] | 0.5644 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -1.20 pp | -1.78 pp | +0.58 pp | [-0.85, +2.00 pp] | 0.4267 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, NOT_MENTIONED (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,716, 624 towns) = **4.36%** [3.69, 5.02%] | `close_friend + poor_record` (n=3,731, 624 towns) = **4.88%** [4.19, 5.57%] | `stranger + good_record` (n=3,716, 624 towns) = **6.84%** [6.03, 7.64%] | `stranger + poor_record` (n=3,737, 624 towns) = **5.38%** [4.69, 6.07%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,731 / 3,737 | -0.50 pp | [-1.47, +0.47 pp] | 0.3142 |
| `closeness effect | reliability=good_record` | 3,716 / 3,716 | -2.48 pp*** | [-3.52, -1.44 pp] | <0.0001 |
| `reliability effect | closeness=stranger` | 3,716 / 3,737 | +1.46 pp** | [+0.40, +2.52 pp] | 0.0070 |
| `reliability effect | closeness=close_friend` | 3,716 / 3,731 | -0.52 pp | [-1.48, +0.43 pp] | 0.2847 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,716, 624 towns) = **4.71%** [4.03, 5.38%] | `mayor + poor_record` (n=3,732, 624 towns) = **5.09%** [4.39, 5.79%] | `citizen + good_record` (n=3,716, 624 towns) = **6.49%** [5.69, 7.28%] | `citizen + poor_record` (n=3,736, 624 towns) = **5.17%** [4.49, 5.84%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,732 / 3,736 | -0.07 pp | [-1.05, +0.90 pp] | 0.8813 |
| `authority effect | reliability=good_record` | 3,716 / 3,716 | -1.78 pp*** | [-2.82, -0.74 pp] | 0.0008 |
| `reliability effect | authority=citizen` | 3,716 / 3,736 | +1.32 pp* | [+0.28, +2.37 pp] | 0.0132 |
| `reliability effect | authority=mayor` | 3,716 / 3,732 | -0.38 pp | [-1.36, +0.59 pp] | 0.4379 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,719, 624 towns) = **5.35%** [4.64, 6.05%] | `rich + poor_record` (n=3,733, 624 towns) = **5.09%** [4.40, 5.78%] | `poor + good_record` (n=3,713, 624 towns) = **5.85%** [5.08, 6.61%] | `poor + poor_record` (n=3,735, 624 towns) = **5.17%** [4.48, 5.85%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,733 / 3,735 | -0.08 pp | [-1.05, +0.90 pp] | 0.8765 |
| `wealth effect | reliability=good_record` | 3,719 / 3,713 | -0.50 pp | [-1.54, +0.55 pp] | 0.3506 |
| `reliability effect | wealth=poor` | 3,713 / 3,735 | +0.68 pp | [-0.35, +1.71 pp] | 0.1967 |
| `reliability effect | wealth=rich` | 3,719 / 3,733 | +0.26 pp | [-0.73, +1.25 pp] | 0.6083 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **4.30%** [3.65, 4.95%] | `close_friend + citizen` (n=3,727, 624 towns) = **4.94%** [4.24, 5.63%] | `stranger + mayor` (n=3,728, 624 towns) = **5.50%** [4.78, 6.22%] | `stranger + citizen` (n=3,725, 624 towns) = **6.72%** [5.94, 7.49%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,727 / 3,725 | -1.78 pp*** | [-2.82, -0.73 pp] | 0.0008 |
| `closeness effect | authority=mayor` | 3,720 / 3,728 | -1.20 pp* | [-2.17, -0.23 pp] | 0.0155 |
| `authority effect | closeness=stranger` | 3,728 / 3,725 | -1.22 pp* | [-2.28, -0.16 pp] | 0.0245 |
| `authority effect | closeness=close_friend` | 3,720 / 3,727 | -0.64 pp | [-1.59, +0.32 pp] | 0.1906 |


**Outcome: FACT (%)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 1.05% | 0.73% | +0.32 pp | [+0.02, +0.62 pp] | 0.0357 | 0.3565 |
| main | authority | `mayor - citizen` | 0.90% | 0.87% | +0.03 pp | [-0.27, +0.33 pp] | 0.8572 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.93% | 0.84% | +0.08 pp | [-0.22, +0.38 pp] | 0.5817 | 1.0000 |
| main | wealth | `rich - poor` | 1.01% | 0.77% | +0.24 pp | [-0.06, +0.54 pp] | 0.1159 | 0.9271 |
| main | gender | `woman - man` | 0.79% | 0.98% | -0.19 pp | [-0.49, +0.11 pp] | 0.2139 | 1.0000 |
| main | age | `old - young` | 0.83% | 0.94% | -0.11 pp | [-0.41, +0.19 pp] | 0.4887 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.03 pp | +0.62 pp | -0.59 pp | [-1.19, +0.01 pp] | 0.0542 | 0.4878 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.08 pp | -0.03 pp | +0.11 pp | [-0.50, +0.71 pp] | 0.7302 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.19 pp | +0.29 pp | -0.11 pp | [-0.71, +0.49 pp] | 0.7252 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.51 pp | +0.13 pp | +0.38 pp | [-0.22, +0.98 pp] | 0.2175 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, FACT (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,716, 624 towns) = **0.94%** [0.63, 1.25%] | `close_friend + poor_record` (n=3,731, 624 towns) = **1.15%** [0.81, 1.49%] | `stranger + good_record` (n=3,716, 624 towns) = **0.91%** [0.61, 1.22%] | `stranger + poor_record` (n=3,737, 624 towns) = **0.54%** [0.30, 0.77%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,731 / 3,737 | +0.62 pp** | [+0.21, +1.03 pp] | 0.0033 |
| `closeness effect | reliability=good_record` | 3,716 / 3,716 | +0.03 pp | [-0.41, +0.46 pp] | 0.9040 |
| `reliability effect | closeness=stranger` | 3,716 / 3,737 | +0.38 pp | [-0.01, +0.77 pp] | 0.0536 |
| `reliability effect | closeness=close_friend` | 3,716 / 3,731 | -0.21 pp | [-0.67, +0.25 pp] | 0.3702 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,716, 624 towns) = **0.97%** [0.64, 1.29%] | `mayor + poor_record` (n=3,732, 624 towns) = **0.83%** [0.55, 1.12%] | `citizen + good_record` (n=3,716, 624 towns) = **0.89%** [0.59, 1.18%] | `citizen + poor_record` (n=3,736, 624 towns) = **0.86%** [0.56, 1.15%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,732 / 3,736 | -0.03 pp | [-0.44, +0.39 pp] | 0.9042 |
| `authority effect | reliability=good_record` | 3,716 / 3,716 | +0.08 pp | [-0.36, +0.52 pp] | 0.7186 |
| `reliability effect | authority=citizen` | 3,716 / 3,736 | +0.03 pp | [-0.39, +0.45 pp] | 0.8825 |
| `reliability effect | authority=mayor` | 3,716 / 3,732 | +0.14 pp | [-0.29, +0.57 pp] | 0.5322 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,719, 624 towns) = **1.02%** [0.69, 1.35%] | `rich + poor_record` (n=3,733, 624 towns) = **0.99%** [0.67, 1.31%] | `poor + good_record` (n=3,713, 624 towns) = **0.83%** [0.55, 1.12%] | `poor + poor_record` (n=3,735, 624 towns) = **0.70%** [0.43, 0.96%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,733 / 3,735 | +0.29 pp | [-0.12, +0.71 pp] | 0.1603 |
| `wealth effect | reliability=good_record` | 3,719 / 3,713 | +0.19 pp | [-0.25, +0.62 pp] | 0.4022 |
| `reliability effect | wealth=poor` | 3,713 / 3,735 | +0.14 pp | [-0.25, +0.53 pp] | 0.4858 |
| `reliability effect | wealth=rich` | 3,719 / 3,733 | +0.03 pp | [-0.43, +0.49 pp] | 0.8960 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **1.16%** [0.81, 1.50%] | `close_friend + citizen` (n=3,727, 624 towns) = **0.94%** [0.63, 1.25%] | `stranger + mayor` (n=3,728, 624 towns) = **0.64%** [0.38, 0.91%] | `stranger + citizen` (n=3,725, 624 towns) = **0.81%** [0.53, 1.09%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,727 / 3,725 | +0.13 pp | [-0.29, +0.55 pp] | 0.5332 |
| `closeness effect | authority=mayor` | 3,720 / 3,728 | +0.51 pp* | [+0.08, +0.94 pp] | 0.0201 |
| `authority effect | closeness=stranger` | 3,728 / 3,725 | -0.16 pp | [-0.55, +0.22 pp] | 0.4116 |
| `authority effect | closeness=close_friend` | 3,720 / 3,727 | +0.22 pp | [-0.24, +0.68 pp] | 0.3571 |


**Outcome: UNCERTAIN (%)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 4.68% | 4.74% | -0.06 pp | [-0.73, +0.60 pp] | 0.8504 | 1.0000 |
| main | authority | `mayor - citizen` | 4.76% | 4.66% | +0.10 pp | [-0.57, +0.76 pp] | 0.7786 | 1.0000 |
| main | reliability | `good_record - poor_record` | 7.48% | 1.94% | +5.54 pp*** | [+4.88, +6.20 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 4.45% | 4.98% | -0.53 pp | [-1.19, +0.13 pp] | 0.1183 | 0.9466 |
| main | gender | `woman - man` | 5.29% | 4.14% | +1.15 pp** | [+0.49, +1.81 pp] | 0.0007 | 0.0062 |
| main | age | `old - young` | 4.67% | 4.76% | -0.09 pp | [-0.75, +0.58 pp] | 0.7956 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.43 pp | -0.56 pp | +0.99 pp | [-0.34, +2.32 pp] | 0.1437 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.22 pp | -0.03 pp | +0.24 pp | [-1.09, +1.57 pp] | 0.7207 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.82 pp | -0.24 pp | -0.58 pp | [-1.91, +0.75 pp] | 0.3926 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.26 pp | +0.13 pp | -0.39 pp | [-1.72, +0.93 pp] | 0.5634 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, UNCERTAIN (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,716, 624 towns) = **7.70%** [6.89, 8.51%] | `close_friend + poor_record` (n=3,731, 624 towns) = **1.66%** [1.25, 2.07%] | `stranger + good_record` (n=3,716, 624 towns) = **7.27%** [6.42, 8.11%] | `stranger + poor_record` (n=3,737, 624 towns) = **2.22%** [1.76, 2.69%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,731 / 3,737 | -0.56 pp | [-1.18, +0.06 pp] | 0.0776 |
| `closeness effect | reliability=good_record` | 3,716 / 3,716 | +0.43 pp | [-0.74, +1.60 pp] | 0.4713 |
| `reliability effect | closeness=stranger` | 3,716 / 3,737 | +5.04 pp*** | [+4.08, +6.01 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,716 / 3,731 | +6.04 pp*** | [+5.13, +6.94 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,716, 624 towns) = **7.59%** [6.76, 8.42%] | `mayor + poor_record` (n=3,732, 624 towns) = **1.93%** [1.49, 2.37%] | `citizen + good_record` (n=3,716, 624 towns) = **7.37%** [6.55, 8.20%] | `citizen + poor_record` (n=3,736, 624 towns) = **1.95%** [1.51, 2.39%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,732 / 3,736 | -0.03 pp | [-0.65, +0.59 pp] | 0.9349 |
| `authority effect | reliability=good_record` | 3,716 / 3,716 | +0.22 pp | [-0.96, +1.39 pp] | 0.7179 |
| `reliability effect | authority=citizen` | 3,716 / 3,736 | +5.42 pp*** | [+4.48, +6.36 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,716 / 3,732 | +5.66 pp*** | [+4.72, +6.60 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,719, 624 towns) = **7.07%** [6.28, 7.86%] | `rich + poor_record` (n=3,733, 624 towns) = **1.82%** [1.39, 2.25%] | `poor + good_record` (n=3,713, 624 towns) = **7.89%** [7.02, 8.76%] | `poor + poor_record` (n=3,735, 624 towns) = **2.06%** [1.61, 2.51%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,733 / 3,735 | -0.24 pp | [-0.86, +0.38 pp] | 0.4498 |
| `wealth effect | reliability=good_record` | 3,719 / 3,713 | -0.82 pp | [-1.99, +0.36 pp] | 0.1716 |
| `reliability effect | wealth=poor` | 3,713 / 3,735 | +5.83 pp*** | [+4.85, +6.81 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,719 / 3,733 | +5.25 pp*** | [+4.35, +6.15 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **4.63%** [4.00, 5.26%] | `close_friend + citizen` (n=3,727, 624 towns) = **4.73%** [4.07, 5.38%] | `stranger + mayor` (n=3,728, 624 towns) = **4.89%** [4.19, 5.59%] | `stranger + citizen` (n=3,725, 624 towns) = **4.60%** [3.93, 5.27%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,727 / 3,725 | +0.13 pp | [-0.81, +1.07 pp] | 0.7832 |
| `closeness effect | authority=mayor` | 3,720 / 3,728 | -0.26 pp | [-1.20, +0.68 pp] | 0.5884 |
| `authority effect | closeness=stranger` | 3,728 / 3,725 | +0.29 pp | [-0.68, +1.26 pp] | 0.5557 |
| `authority effect | closeness=close_friend` | 3,720 / 3,727 | -0.10 pp | [-1.01, +0.81 pp] | 0.8288 |


**Outcome: SKEPTICAL (%)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 19.12% | 19.12% | +0.01 pp | [-1.22, +1.24 pp] | 0.9896 | 1.0000 |
| main | authority | `mayor - citizen` | 18.60% | 19.64% | -1.04 pp | [-2.27, +0.18 pp] | 0.0959 | 0.4796 |
| main | reliability | `good_record - poor_record` | 13.48% | 24.76% | -11.28 pp*** | [-12.50, -10.05 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 17.89% | 20.35% | -2.45 pp*** | [-3.68, -1.23 pp] | <0.0001 | 0.0008 |
| main | gender | `woman - man` | 18.79% | 19.45% | -0.67 pp | [-1.90, +0.56 pp] | 0.2883 | 0.8649 |
| main | age | `old - young` | 19.61% | 18.63% | +0.98 pp | [-0.25, +2.21 pp] | 0.1196 | 0.4796 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +1.50 pp | -1.49 pp | +2.99 pp | [+0.54, +5.45 pp] | 0.0170 | 0.1189 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +0.16 pp | -2.25 pp | +2.41 pp | [-0.05, +4.87 pp] | 0.0546 | 0.3277 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | -0.13 pp | -4.78 pp | +4.65 pp** | [+2.19, +7.11 pp] | 0.0002 | 0.0017 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | -0.33 pp | +0.34 pp | -0.67 pp | [-3.13, +1.79 pp] | 0.5939 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, SKEPTICAL (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,716, 624 towns) = **14.23%** [13.08, 15.39%] | `close_friend + poor_record` (n=3,731, 624 towns) = **24.01%** [22.66, 25.36%] | `stranger + good_record` (n=3,716, 624 towns) = **12.73%** [11.67, 13.79%] | `stranger + poor_record` (n=3,737, 624 towns) = **25.50%** [24.17, 26.83%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,731 / 3,737 | -1.49 pp | [-3.38, +0.41 pp] | 0.1235 |
| `closeness effect | reliability=good_record` | 3,716 / 3,716 | +1.50 pp | [-0.06, +3.07 pp] | 0.0596 |
| `reliability effect | closeness=stranger` | 3,716 / 3,737 | -12.77 pp*** | [-14.47, -11.07 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,716 / 3,731 | -9.78 pp*** | [-11.56, -8.00 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,716, 624 towns) = **13.56%** [12.44, 14.68%] | `mayor + poor_record` (n=3,732, 624 towns) = **23.63%** [22.30, 24.97%] | `citizen + good_record` (n=3,716, 624 towns) = **13.40%** [12.31, 14.49%] | `citizen + poor_record` (n=3,736, 624 towns) = **25.88%** [24.54, 27.22%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,732 / 3,736 | -2.25 pp* | [-4.14, -0.35 pp] | 0.0200 |
| `authority effect | reliability=good_record` | 3,716 / 3,716 | +0.16 pp | [-1.40, +1.73 pp] | 0.8402 |
| `reliability effect | authority=citizen` | 3,716 / 3,736 | -12.48 pp*** | [-14.21, -10.75 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,716 / 3,732 | -10.07 pp*** | [-11.82, -8.33 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,719, 624 towns) = **13.42%** [12.31, 14.53%] | `rich + poor_record` (n=3,733, 624 towns) = **22.37%** [21.11, 23.62%] | `poor + good_record` (n=3,713, 624 towns) = **13.55%** [12.44, 14.65%] | `poor + poor_record` (n=3,735, 624 towns) = **27.15%** [25.73, 28.56%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,733 / 3,735 | -4.78 pp*** | [-6.67, -2.89 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,719 / 3,713 | -0.13 pp | [-1.70, +1.44 pp] | 0.8712 |
| `reliability effect | wealth=poor` | 3,713 / 3,735 | -13.60 pp*** | [-15.40, -11.80 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,719 / 3,733 | -8.95 pp*** | [-10.63, -7.27 pp] | <0.0001 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **18.43%** [17.18, 19.69%] | `close_friend + citizen` (n=3,727, 624 towns) = **19.81%** [18.56, 21.07%] | `stranger + mayor` (n=3,728, 624 towns) = **18.76%** [17.55, 19.97%] | `stranger + citizen` (n=3,725, 624 towns) = **19.47%** [18.28, 20.66%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,727 / 3,725 | +0.34 pp | [-1.39, +2.07 pp] | 0.6980 |
| `closeness effect | authority=mayor` | 3,720 / 3,728 | -0.33 pp | [-2.07, +1.42 pp] | 0.7142 |
| `authority effect | closeness=stranger` | 3,728 / 3,725 | -0.71 pp | [-2.41, +0.99 pp] | 0.4131 |
| `authority effect | closeness=close_friend` | 3,720 / 3,727 | -1.38 pp | [-3.15, +0.40 pp] | 0.1284 |


**Outcome: CHECKED_TRUE (%)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 0.24% | 0.05% | +0.19 pp* | [+0.07, +0.31 pp] | 0.0026 | 0.0259 |
| main | authority | `mayor - citizen` | 0.16% | 0.13% | +0.03 pp | [-0.10, +0.15 pp] | 0.6673 | 1.0000 |
| main | reliability | `good_record - poor_record` | 0.07% | 0.23% | -0.16 pp | [-0.28, -0.04 pp] | 0.0100 | 0.0904 |
| main | wealth | `rich - poor` | 0.17% | 0.12% | +0.05 pp | [-0.07, +0.18 pp] | 0.3892 | 1.0000 |
| main | gender | `woman - man` | 0.15% | 0.15% | -0.00 pp | [-0.12, +0.12 pp] | 0.9843 | 1.0000 |
| main | age | `old - young` | 0.15% | 0.15% | +0.00 pp | [-0.12, +0.12 pp] | 0.9976 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.08 pp | +0.30 pp | -0.21 pp | [-0.46, +0.03 pp] | 0.0857 | 0.6762 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | -0.08 pp | +0.13 pp | -0.22 pp | [-0.46, +0.03 pp] | 0.0845 | 0.6762 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +0.03 pp | +0.08 pp | -0.05 pp | [-0.30, +0.19 pp] | 0.6673 | 1.0000 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +0.16 pp | +0.21 pp | -0.05 pp | [-0.30, +0.19 pp] | 0.6714 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_TRUE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,716, 624 towns) = **0.11%** [0.00, 0.21%] | `close_friend + poor_record` (n=3,731, 624 towns) = **0.38%** [0.18, 0.57%] | `stranger + good_record` (n=3,716, 624 towns) = **0.03%** [-0.03, 0.08%] | `stranger + poor_record` (n=3,737, 624 towns) = **0.08%** [-0.01, 0.17%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,731 / 3,737 | +0.30 pp** | [+0.08, +0.51 pp] | 0.0070 |
| `closeness effect | reliability=good_record` | 3,716 / 3,716 | +0.08 pp | [-0.04, +0.20 pp] | 0.1785 |
| `reliability effect | closeness=stranger` | 3,716 / 3,737 | -0.05 pp | [-0.16, +0.05 pp] | 0.3187 |
| `reliability effect | closeness=close_friend` | 3,716 / 3,731 | -0.27 pp* | [-0.49, -0.05 pp] | 0.0175 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,716, 624 towns) = **0.03%** [-0.03, 0.08%] | `mayor + poor_record` (n=3,732, 624 towns) = **0.29%** [0.12, 0.47%] | `citizen + good_record` (n=3,716, 624 towns) = **0.11%** [0.00, 0.21%] | `citizen + poor_record` (n=3,736, 624 towns) = **0.16%** [0.03, 0.29%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,732 / 3,736 | +0.13 pp | [-0.08, +0.35 pp] | 0.2192 |
| `authority effect | reliability=good_record` | 3,716 / 3,716 | -0.08 pp | [-0.20, +0.04 pp] | 0.1777 |
| `reliability effect | authority=citizen` | 3,716 / 3,736 | -0.05 pp | [-0.22, +0.11 pp] | 0.5297 |
| `reliability effect | authority=mayor` | 3,716 / 3,732 | -0.27 pp** | [-0.45, -0.09 pp] | 0.0035 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,719, 624 towns) = **0.08%** [-0.01, 0.17%] | `rich + poor_record` (n=3,733, 624 towns) = **0.27%** [0.10, 0.43%] | `poor + good_record` (n=3,713, 624 towns) = **0.05%** [-0.02, 0.13%] | `poor + poor_record` (n=3,735, 624 towns) = **0.19%** [0.05, 0.33%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,733 / 3,735 | +0.08 pp | [-0.13, +0.29 pp] | 0.4617 |
| `wealth effect | reliability=good_record` | 3,719 / 3,713 | +0.03 pp | [-0.09, +0.14 pp] | 0.6539 |
| `reliability effect | wealth=poor` | 3,713 / 3,735 | -0.13 pp | [-0.29, +0.02 pp] | 0.0936 |
| `reliability effect | wealth=rich` | 3,719 / 3,733 | -0.19 pp | [-0.38, +0.00 pp] | 0.0506 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **0.24%** [0.09, 0.40%] | `close_friend + citizen` (n=3,727, 624 towns) = **0.24%** [0.08, 0.40%] | `stranger + mayor` (n=3,728, 624 towns) = **0.08%** [-0.01, 0.17%] | `stranger + citizen` (n=3,725, 624 towns) = **0.03%** [-0.03, 0.08%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,727 / 3,725 | +0.21 pp* | [+0.05, +0.38 pp] | 0.0110 |
| `closeness effect | authority=mayor` | 3,720 / 3,728 | +0.16 pp | [-0.02, +0.34 pp] | 0.0793 |
| `authority effect | closeness=stranger` | 3,728 / 3,725 | +0.05 pp | [-0.05, +0.16 pp] | 0.3196 |
| `authority effect | closeness=close_friend` | 3,720 / 3,727 | +0.00 pp | [-0.22, +0.22 pp] | 0.9977 |


**Outcome: CHECKED_FALSE (%)** (n=14,900, towns=2,496)

| Type | Contrast | Contrast Detail | Mean A | Mean B | Effect (A − B) | 95% CI | p (clustered) | p (Holm 10) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| main | closeness | `close_friend - stranger` | 70.29% | 69.25% | +1.03 pp | [-0.42, +2.49 pp] | 0.1630 | 0.9779 |
| main | authority | `mayor - citizen` | 70.68% | 68.86% | +1.82 pp | [+0.37, +3.27 pp] | 0.0141 | 0.1128 |
| main | reliability | `good_record - poor_record` | 72.44% | 67.10% | +5.34 pp*** | [+3.89, +6.80 pp] | <0.0001 | <0.0001 |
| main | wealth | `rich - poor` | 71.26% | 68.28% | +2.98 pp*** | [+1.52, +4.43 pp] | <0.0001 | 0.0005 |
| main | gender | `woman - man` | 69.52% | 70.02% | -0.50 pp | [-1.96, +0.95 pp] | 0.4990 | 1.0000 |
| main | age | `old - young` | 69.38% | 70.16% | -0.77 pp | [-2.23, +0.68 pp] | 0.2963 | 1.0000 |
| interaction | closeness_by_reliability | `(close_friend-stranger | good_record) - (close_friend-stranger | poor_record)` | +0.44 pp | +1.63 pp | -1.20 pp | [-4.11, +1.71 pp] | 0.4187 | 1.0000 |
| interaction | authority_by_reliability | `(mayor-citizen | good_record) - (mayor-citizen | poor_record)` | +1.40 pp | +2.24 pp | -0.84 pp | [-3.74, +2.07 pp] | 0.5727 | 1.0000 |
| interaction | wealth_by_reliability | `(rich-poor | good_record) - (rich-poor | poor_record)` | +1.23 pp | +4.72 pp | -3.49 pp | [-6.40, -0.58 pp] | 0.0187 | 0.1306 |
| interaction | closeness_by_authority | `(close_friend-stranger | mayor) - (close_friend-stranger | citizen)` | +1.11 pp | +0.96 pp | +0.16 pp | [-2.75, +3.06 pp] | 0.9161 | 1.0000 |

*4 Planned Interaction Pairs — 16-DNA Combo Adjusted Means (OLS marginal predictions) & Conditional Wald z-Tests (`groups=run_id`, CHECKED_FALSE (%)):*

- **`closeness × reliability` — Controlled Combos:** `close_friend + good_record` (n=3,716, 624 towns) = **72.66%** [71.22, 74.10%] | `close_friend + poor_record` (n=3,731, 624 towns) = **67.92%** [66.42, 69.41%] | `stranger + good_record` (n=3,716, 624 towns) = **72.23%** [70.82, 73.63%] | `stranger + poor_record` (n=3,737, 624 towns) = **66.28%** [64.81, 67.76%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | reliability=poor_record` | 3,731 / 3,737 | +1.63 pp | [-0.46, +3.73 pp] | 0.1270 |
| `closeness effect | reliability=good_record` | 3,716 / 3,716 | +0.44 pp | [-1.58, +2.45 pp] | 0.6717 |
| `reliability effect | closeness=stranger` | 3,716 / 3,737 | +5.94 pp*** | [+3.91, +7.98 pp] | <0.0001 |
| `reliability effect | closeness=close_friend` | 3,716 / 3,731 | +4.74 pp*** | [+2.67, +6.82 pp] | <0.0001 |

- **`authority × reliability` — Controlled Combos:** `mayor + good_record` (n=3,716, 624 towns) = **73.15%** [71.72, 74.57%] | `mayor + poor_record` (n=3,732, 624 towns) = **68.22%** [66.76, 69.68%] | `citizen + good_record` (n=3,716, 624 towns) = **71.74%** [70.32, 73.16%] | `citizen + poor_record` (n=3,736, 624 towns) = **65.98%** [64.47, 67.49%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `authority effect | reliability=poor_record` | 3,732 / 3,736 | +2.24 pp* | [+0.14, +4.34 pp] | 0.0366 |
| `authority effect | reliability=good_record` | 3,716 / 3,716 | +1.40 pp | [-0.61, +3.41 pp] | 0.1718 |
| `reliability effect | authority=citizen` | 3,716 / 3,736 | +5.76 pp*** | [+3.69, +7.84 pp] | <0.0001 |
| `reliability effect | authority=mayor` | 3,716 / 3,732 | +4.93 pp*** | [+2.89, +6.96 pp] | <0.0001 |

- **`wealth × reliability` — Controlled Combos:** `rich + good_record` (n=3,719, 624 towns) = **73.06%** [71.65, 74.47%] | `rich + poor_record` (n=3,733, 624 towns) = **69.46%** [68.03, 70.89%] | `poor + good_record` (n=3,713, 624 towns) = **71.83%** [70.40, 73.26%] | `poor + poor_record` (n=3,735, 624 towns) = **64.74%** [63.21, 66.27%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `wealth effect | reliability=poor_record` | 3,733 / 3,735 | +4.72 pp*** | [+2.62, +6.82 pp] | <0.0001 |
| `wealth effect | reliability=good_record` | 3,719 / 3,713 | +1.23 pp | [-0.78, +3.24 pp] | 0.2305 |
| `reliability effect | wealth=poor` | 3,713 / 3,735 | +7.09 pp*** | [+4.99, +9.19 pp] | <0.0001 |
| `reliability effect | wealth=rich` | 3,719 / 3,733 | +3.60 pp*** | [+1.59, +5.61 pp] | 0.0005 |

- **`closeness × authority` — Controlled Combos:** `close_friend + mayor` (n=3,720, 624 towns) = **71.24%** [69.81, 72.67%] | `close_friend + citizen` (n=3,727, 624 towns) = **69.34%** [67.84, 70.84%] | `stranger + mayor` (n=3,728, 624 towns) = **70.13%** [68.68, 71.58%] | `stranger + citizen` (n=3,725, 624 towns) = **68.38%** [66.95, 69.81%]

| Conditional Comparison | N (Hi / Lo) | Diff | 95% CI | p (clustered) |
|---|---:|---:|---:|---:|
| `closeness effect | authority=citizen` | 3,727 / 3,725 | +0.96 pp | [-1.12, +3.03 pp] | 0.3658 |
| `closeness effect | authority=mayor` | 3,720 / 3,728 | +1.11 pp | [-0.93, +3.15 pp] | 0.2846 |
| `authority effect | closeness=stranger` | 3,728 / 3,725 | +1.74 pp | [-0.30, +3.78 pp] | 0.0937 |
| `authority effect | closeness=close_friend` | 3,720 / 3,727 | +1.90 pp | [-0.18, +3.97 pp] | 0.0728 |


---

## 4. Top 10 Strongest & Bottom 10 Weakest Source DNAs (Descriptive Per-Cell Means & Shares; No Hypothesis Test)

### Model: DeepSeek-V4-Flash

#### Source POV (All 12 Listeners)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 466 | 434 | **0.1037** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 2 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 468 | 428 | **0.0981** | 0.098 | 68.4% | 31.6% | 0.2% | 16.2% | 7.3% | 0.6% | 67.1% | 8.5% |
| 3 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 467 | 437 | **0.0973** | 0.097 | 70.7% | 29.3% | 1.1% | 15.2% | 5.8% | 0.4% | 71.1% | 6.4% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 465 | 432 | **0.0938** | 0.094 | 70.3% | 29.7% | 1.5% | 12.7% | 5.8% | 0.9% | 72.0% | 7.1% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 463 | 438 | **0.0936** | 0.094 | 71.4% | 28.6% | 0.0% | 16.8% | 6.9% | 0.4% | 70.4% | 5.4% |
| 6 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 467 | 437 | **0.0915** | 0.092 | 67.9% | 32.1% | 0.2% | 15.8% | 6.0% | 0.4% | 71.1% | 6.4% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 467 | 441 | **0.0907** | 0.091 | 70.7% | 29.3% | 0.4% | 14.1% | 8.4% | 1.1% | 70.4% | 5.6% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 461 | 420 | **0.0881** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 9 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 467 | 427 | **0.0878** | 0.088 | 72.9% | 27.1% | 0.9% | 13.1% | 6.4% | 0.6% | 70.4% | 8.6% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 428 | **0.0876** | 0.088 | 70.1% | 29.9% | 0.2% | 13.5% | 6.4% | 1.1% | 70.6% | 8.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **0.0217** | 0.022 | 31.2% | 68.8% | 0.0% | 4.3% | 62.6% | 0.0% | 31.6% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 468 | 463 | **0.0302** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 462 | **0.0303** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 4 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 467 | 462 | **0.0303** | 0.030 | 38.5% | 61.5% | 0.0% | 6.0% | 53.1% | 0.0% | 39.8% | 1.1% |
| 5 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 460 | **0.0304** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 6 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 467 | 459 | **0.0327** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 464 | 456 | **0.0329** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | 39 | 465 | 456 | **0.0340** | 0.034 | 37.8% | 62.2% | 0.0% | 6.7% | 51.4% | 0.0% | 40.0% | 1.9% |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 464 | 457 | **0.0350** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 467 | 454 | **0.0363** | 0.036 | 44.7% | 55.3% | 0.0% | 7.1% | 42.8% | 0.0% | 47.3% | 2.8% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 460 | **78.0%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 468 | 463 | **77.6%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 464 | 457 | **75.6%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 462 | **74.8%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 466 | 463 | **72.6%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 467 | 462 | **72.2%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 7 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 467 | 459 | **71.8%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 467 | 460 | **71.4%** | 0.041 | 28.6% | 71.4% | 0.0% | 8.1% | 62.7% | 0.0% | 27.6% | 1.5% |
| 9 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 465 | **70.9%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 464 | 456 | **69.0%** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 467 | 428 | **21.6%** | 0.061 | 78.4% | 21.6% | 0.6% | 9.4% | 7.5% | 0.2% | 73.9% | 8.4% |
| 2 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 463 | 430 | **22.0%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 466 | 430 | **22.4%** | 0.067 | 77.6% | 22.4% | 0.2% | 8.2% | 6.9% | 1.9% | 75.1% | 7.7% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 426 | **22.6%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 5 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 464 | 429 | **23.5%** | 0.061 | 76.5% | 23.5% | 0.4% | 9.1% | 5.6% | 0.6% | 76.7% | 7.5% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 466 | 428 | **23.5%** | 0.055 | 76.5% | 23.5% | 0.4% | 9.2% | 6.2% | 0.0% | 76.0% | 8.2% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 466 | 430 | **23.5%** | 0.055 | 76.5% | 23.5% | 0.2% | 7.9% | 7.1% | 0.9% | 76.2% | 7.7% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 466 | 427 | **24.1%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |
| 9 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 467 | 433 | **24.4%** | 0.053 | 75.6% | 24.4% | 0.4% | 8.1% | 6.6% | 0.4% | 77.1% | 7.3% |
| 10 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 467 | 431 | **24.6%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |


**FACT (%)** *(Note: 31 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 465 | 432 | **1.5%** | 0.094 | 70.3% | 29.7% | 1.5% | 12.7% | 5.8% | 0.9% | 72.0% | 7.1% |
| 2 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 463 | 430 | **1.1%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 465 | 426 | **1.1%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 467 | 437 | **1.1%** | 0.097 | 70.7% | 29.3% | 1.1% | 15.2% | 5.8% | 0.4% | 71.1% | 6.4% |
| 5 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 467 | 431 | **1.1%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |
| 6 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 466 | 427 | **0.9%** | 0.070 | 75.2% | 24.8% | 0.9% | 9.9% | 6.9% | 0.6% | 73.4% | 8.4% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 467 | 427 | **0.9%** | 0.088 | 72.9% | 27.1% | 0.9% | 13.1% | 6.4% | 0.6% | 70.4% | 8.6% |
| 8 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 466 | 434 | **0.6%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 9 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 426 | **0.6%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 10 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 467 | 439 | **0.6%** | 0.067 | 75.0% | 25.0% | 0.6% | 10.1% | 6.4% | 0.6% | 76.2% | 6.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 463 | 438 | **0.0%** | 0.094 | 71.4% | 28.6% | 0.0% | 16.8% | 6.9% | 0.4% | 70.4% | 5.4% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 464 | 424 | **0.0%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 3 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 466 | 454 | **0.0%** | 0.061 | 46.2% | 53.8% | 0.0% | 11.8% | 37.3% | 0.0% | 48.3% | 2.6% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 467 | 454 | **0.0%** | 0.057 | 42.3% | 57.7% | 0.0% | 11.1% | 42.2% | 0.0% | 43.9% | 2.8% |
| 5 | 15 | close_friend / mayor / poor_record / poor / woman_young | 39 | 468 | 458 | **0.0%** | 0.057 | 46.8% | 53.2% | 0.0% | 11.1% | 38.9% | 0.0% | 47.9% | 2.1% |
| 6 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 468 | 455 | **0.0%** | 0.056 | 42.3% | 57.7% | 0.0% | 10.9% | 42.3% | 0.0% | 44.0% | 2.8% |
| 7 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 468 | 460 | **0.0%** | 0.055 | 43.4% | 56.6% | 0.0% | 10.9% | 40.4% | 0.0% | 47.0% | 1.7% |
| 8 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 468 | 459 | **0.0%** | 0.054 | 42.7% | 57.3% | 0.0% | 10.7% | 42.9% | 0.0% | 44.4% | 1.9% |
| 9 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 466 | 450 | **0.0%** | 0.052 | 45.7% | 54.3% | 0.0% | 10.1% | 39.1% | 0.0% | 47.4% | 3.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 466 | 456 | **0.0%** | 0.052 | 37.2% | 62.8% | 0.0% | 10.1% | 49.4% | 0.0% | 38.4% | 2.1% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 463 | 438 | **16.8%** | 0.094 | 71.4% | 28.6% | 0.0% | 16.8% | 6.9% | 0.4% | 70.4% | 5.4% |
| 2 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 468 | 428 | **16.2%** | 0.098 | 68.4% | 31.6% | 0.2% | 16.2% | 7.3% | 0.6% | 67.1% | 8.5% |
| 3 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 467 | 437 | **15.8%** | 0.092 | 67.9% | 32.1% | 0.2% | 15.8% | 6.0% | 0.4% | 71.1% | 6.4% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 467 | 437 | **15.2%** | 0.097 | 70.7% | 29.3% | 1.1% | 15.2% | 5.8% | 0.4% | 71.1% | 6.4% |
| 5 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 467 | 440 | **14.8%** | 0.085 | 71.6% | 28.4% | 0.2% | 14.8% | 6.2% | 0.4% | 72.6% | 5.8% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 466 | 434 | **14.6%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 7 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 464 | 424 | **14.2%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 467 | 441 | **14.1%** | 0.091 | 70.7% | 29.3% | 0.4% | 14.1% | 8.4% | 1.1% | 70.4% | 5.6% |
| 9 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 428 | **13.5%** | 0.088 | 70.1% | 29.9% | 0.2% | 13.5% | 6.4% | 1.1% | 70.6% | 8.2% |
| 10 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 468 | 430 | **13.2%** | 0.081 | 74.1% | 25.9% | 0.2% | 13.2% | 4.9% | 0.6% | 72.9% | 8.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **4.3%** | 0.022 | 31.2% | 68.8% | 0.0% | 4.3% | 62.6% | 0.0% | 31.6% | 1.5% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 460 | **5.6%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 462 | **6.0%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 468 | 463 | **6.0%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 467 | 462 | **6.0%** | 0.030 | 38.5% | 61.5% | 0.0% | 6.0% | 53.1% | 0.0% | 39.8% | 1.1% |
| 6 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 467 | 459 | **6.4%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 464 | 456 | **6.5%** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | 39 | 465 | 456 | **6.7%** | 0.034 | 37.8% | 62.2% | 0.0% | 6.7% | 51.4% | 0.0% | 40.0% | 1.9% |
| 9 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 464 | 457 | **6.9%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 467 | 454 | **7.1%** | 0.036 | 44.7% | 55.3% | 0.0% | 7.1% | 42.8% | 0.0% | 47.3% | 2.8% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 460 | **70.9%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 468 | 463 | **70.7%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 464 | 457 | **67.9%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 462 | **66.7%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 467 | 460 | **62.7%** | 0.041 | 28.6% | 71.4% | 0.0% | 8.1% | 62.7% | 0.0% | 27.6% | 1.5% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 466 | 463 | **62.7%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 7 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **62.6%** | 0.022 | 31.2% | 68.8% | 0.0% | 4.3% | 62.6% | 0.0% | 31.6% | 1.5% |
| 8 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 465 | **62.3%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 467 | 462 | **62.1%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 467 | 459 | **61.5%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 464 | 424 | **4.1%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 2 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 468 | 423 | **4.9%** | 0.086 | 73.1% | 26.9% | 0.2% | 13.0% | 4.9% | 1.1% | 71.2% | 9.6% |
| 3 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 468 | 430 | **4.9%** | 0.081 | 74.1% | 25.9% | 0.2% | 13.2% | 4.9% | 0.6% | 72.9% | 8.1% |
| 4 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 465 | 426 | **4.9%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 463 | 430 | **5.2%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 461 | 420 | **5.2%** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 7 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 466 | 434 | **5.4%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 8 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 466 | 426 | **5.4%** | 0.075 | 72.0% | 28.0% | 0.2% | 9.9% | 5.4% | 1.7% | 74.2% | 8.6% |
| 9 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 467 | 431 | **5.6%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 466 | 427 | **5.6%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |


**CHECKED_TRUE (%)** *(Note: 31 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 466 | 430 | **1.9%** | 0.067 | 77.6% | 22.4% | 0.2% | 8.2% | 6.9% | 1.9% | 75.1% | 7.7% |
| 2 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 466 | 434 | **1.7%** | 0.104 | 74.6% | 25.4% | 0.6% | 14.6% | 5.4% | 1.7% | 70.8% | 6.9% |
| 3 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 466 | 426 | **1.7%** | 0.075 | 72.0% | 28.0% | 0.2% | 9.9% | 5.4% | 1.7% | 74.2% | 8.6% |
| 4 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 467 | 431 | **1.7%** | 0.079 | 75.4% | 24.6% | 1.1% | 9.0% | 5.6% | 1.7% | 74.9% | 7.7% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 466 | 429 | **1.3%** | 0.073 | 74.8% | 25.2% | 0.2% | 10.5% | 6.0% | 1.3% | 74.0% | 7.9% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 461 | 420 | **1.1%** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 7 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 428 | **1.1%** | 0.088 | 70.1% | 29.9% | 0.2% | 13.5% | 6.4% | 1.1% | 70.6% | 8.2% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 467 | 441 | **1.1%** | 0.091 | 70.7% | 29.3% | 0.4% | 14.1% | 8.4% | 1.1% | 70.4% | 5.6% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 468 | 423 | **1.1%** | 0.086 | 73.1% | 26.9% | 0.2% | 13.0% | 4.9% | 1.1% | 71.2% | 9.6% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 465 | 432 | **0.9%** | 0.094 | 70.3% | 29.7% | 1.5% | 12.7% | 5.8% | 0.9% | 72.0% | 7.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 466 | 454 | **0.0%** | 0.061 | 46.2% | 53.8% | 0.0% | 11.8% | 37.3% | 0.0% | 48.3% | 2.6% |
| 2 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 467 | 454 | **0.0%** | 0.057 | 42.3% | 57.7% | 0.0% | 11.1% | 42.2% | 0.0% | 43.9% | 2.8% |
| 3 | 15 | close_friend / mayor / poor_record / poor / woman_young | 39 | 468 | 458 | **0.0%** | 0.057 | 46.8% | 53.2% | 0.0% | 11.1% | 38.9% | 0.0% | 47.9% | 2.1% |
| 4 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 468 | 455 | **0.0%** | 0.056 | 42.3% | 57.7% | 0.0% | 10.9% | 42.3% | 0.0% | 44.0% | 2.8% |
| 5 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 468 | 460 | **0.0%** | 0.055 | 43.4% | 56.6% | 0.0% | 10.9% | 40.4% | 0.0% | 47.0% | 1.7% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 466 | 428 | **0.0%** | 0.055 | 76.5% | 23.5% | 0.4% | 9.2% | 6.2% | 0.0% | 76.0% | 8.2% |
| 7 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 468 | 459 | **0.0%** | 0.054 | 42.7% | 57.3% | 0.0% | 10.7% | 42.9% | 0.0% | 44.4% | 1.9% |
| 8 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 466 | 450 | **0.0%** | 0.052 | 45.7% | 54.3% | 0.0% | 10.1% | 39.1% | 0.0% | 47.4% | 3.4% |
| 9 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 466 | 456 | **0.0%** | 0.052 | 37.2% | 62.8% | 0.0% | 10.1% | 49.4% | 0.0% | 38.4% | 2.1% |
| 10 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 466 | 457 | **0.0%** | 0.049 | 40.6% | 59.4% | 0.4% | 8.8% | 47.4% | 0.0% | 41.4% | 1.9% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 463 | 430 | **77.8%** | 0.060 | 78.0% | 22.0% | 1.1% | 8.6% | 5.2% | 0.2% | 77.8% | 7.1% |
| 2 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 467 | 433 | **77.1%** | 0.053 | 75.6% | 24.4% | 0.4% | 8.1% | 6.6% | 0.4% | 77.1% | 7.3% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 464 | 429 | **76.7%** | 0.061 | 76.5% | 23.5% | 0.4% | 9.1% | 5.6% | 0.6% | 76.7% | 7.5% |
| 4 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 467 | 439 | **76.2%** | 0.067 | 75.0% | 25.0% | 0.6% | 10.1% | 6.4% | 0.6% | 76.2% | 6.0% |
| 5 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 466 | 430 | **76.2%** | 0.055 | 76.5% | 23.5% | 0.2% | 7.9% | 7.1% | 0.9% | 76.2% | 7.7% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 466 | 428 | **76.0%** | 0.055 | 76.5% | 23.5% | 0.4% | 9.2% | 6.2% | 0.0% | 76.0% | 8.2% |
| 7 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 426 | **76.0%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 465 | 426 | **75.7%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 462 | 434 | **75.5%** | 0.074 | 71.8% | 28.2% | 0.4% | 11.7% | 5.6% | 0.6% | 75.5% | 6.1% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 466 | 427 | **75.5%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 460 | **21.8%** | 0.030 | 22.0% | 78.0% | 0.0% | 5.6% | 70.9% | 0.2% | 21.8% | 1.5% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 468 | 463 | **22.2%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 464 | 457 | **23.7%** | 0.035 | 24.4% | 75.6% | 0.0% | 6.9% | 67.9% | 0.0% | 23.7% | 1.5% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 462 | **26.1%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 467 | 460 | **27.6%** | 0.041 | 28.6% | 71.4% | 0.0% | 8.1% | 62.7% | 0.0% | 27.6% | 1.5% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 466 | 463 | **28.8%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 465 | **28.9%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 467 | 462 | **29.3%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 467 | 459 | **30.4%** | 0.033 | 28.2% | 71.8% | 0.0% | 6.4% | 61.5% | 0.0% | 30.4% | 1.7% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 464 | 456 | **31.2%** | 0.033 | 31.0% | 69.0% | 0.0% | 6.5% | 60.6% | 0.0% | 31.2% | 1.7% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 468 | 423 | **9.6%** | 0.086 | 73.1% | 26.9% | 0.2% | 13.0% | 4.9% | 1.1% | 71.2% | 9.6% |
| 2 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 461 | 420 | **8.9%** | 0.088 | 74.1% | 25.9% | 0.4% | 13.0% | 5.2% | 1.1% | 71.4% | 8.9% |
| 3 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 464 | 424 | **8.6%** | 0.083 | 72.4% | 27.6% | 0.0% | 14.2% | 4.1% | 0.4% | 72.6% | 8.6% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 466 | 426 | **8.6%** | 0.075 | 72.0% | 28.0% | 0.2% | 9.9% | 5.4% | 1.7% | 74.2% | 8.6% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 426 | **8.6%** | 0.054 | 77.4% | 22.6% | 0.6% | 7.7% | 6.7% | 0.4% | 76.0% | 8.6% |
| 6 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 467 | 427 | **8.6%** | 0.088 | 72.9% | 27.1% | 0.9% | 13.1% | 6.4% | 0.6% | 70.4% | 8.6% |
| 7 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 468 | 428 | **8.5%** | 0.098 | 68.4% | 31.6% | 0.2% | 16.2% | 7.3% | 0.6% | 67.1% | 8.5% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 465 | 426 | **8.4%** | 0.067 | 74.4% | 25.6% | 1.1% | 9.7% | 4.9% | 0.2% | 75.7% | 8.4% |
| 9 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 466 | 427 | **8.4%** | 0.070 | 75.2% | 24.8% | 0.9% | 9.9% | 6.9% | 0.6% | 73.4% | 8.4% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 466 | 427 | **8.4%** | 0.060 | 75.9% | 24.1% | 0.2% | 10.1% | 5.6% | 0.2% | 75.5% | 8.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 465 | **0.4%** | 0.042 | 29.1% | 70.9% | 0.0% | 8.4% | 62.3% | 0.0% | 28.9% | 0.4% |
| 2 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 466 | 463 | **0.6%** | 0.040 | 27.4% | 72.6% | 0.0% | 7.9% | 62.7% | 0.0% | 28.8% | 0.6% |
| 3 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 468 | 464 | **0.9%** | 0.044 | 41.0% | 59.0% | 0.2% | 8.3% | 44.7% | 0.0% | 45.9% | 0.9% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 468 | 463 | **1.1%** | 0.030 | 22.4% | 77.6% | 0.0% | 6.0% | 70.7% | 0.0% | 22.2% | 1.1% |
| 5 | 25 | close_friend / citizen / poor_record / rich / woman_old | 39 | 467 | 462 | **1.1%** | 0.045 | 44.9% | 55.1% | 0.0% | 9.0% | 42.2% | 0.0% | 47.8% | 1.1% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 467 | 462 | **1.1%** | 0.038 | 27.8% | 72.2% | 0.0% | 7.5% | 62.1% | 0.0% | 29.3% | 1.1% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 467 | 462 | **1.1%** | 0.030 | 38.5% | 61.5% | 0.0% | 6.0% | 53.1% | 0.0% | 39.8% | 1.1% |
| 8 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 462 | **1.3%** | 0.030 | 25.2% | 74.8% | 0.0% | 6.0% | 66.7% | 0.0% | 26.1% | 1.3% |
| 9 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 467 | 461 | **1.3%** | 0.042 | 38.5% | 61.5% | 0.0% | 8.4% | 50.7% | 0.0% | 39.6% | 1.3% |
| 10 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 468 | 461 | **1.5%** | 0.042 | 38.5% | 61.5% | 0.0% | 8.3% | 47.6% | 0.0% | 42.5% | 1.5% |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 231 | 228 | **0.1601** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 2 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 233 | 230 | **0.1587** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 3 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 232 | 230 | **0.1543** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 4 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 230 | **0.1478** | 0.148 | 69.7% | 30.3% | 0.4% | 25.0% | 4.7% | 1.7% | 67.2% | 0.9% |
| 5 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 229 | **0.1463** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 6 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 233 | 232 | **0.1444** | 0.144 | 68.8% | 31.2% | 0.4% | 26.2% | 5.2% | 0.9% | 67.0% | 0.4% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 234 | 231 | **0.1429** | 0.143 | 71.4% | 28.6% | 0.9% | 22.2% | 6.0% | 2.1% | 67.5% | 1.3% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 229 | 226 | **0.1394** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 229 | **0.1354** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 233 | 232 | **0.1336** | 0.134 | 73.9% | 26.1% | 1.7% | 19.7% | 4.3% | 1.7% | 72.1% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 233 | **0.0365** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **0.0385** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **0.0472** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 234 | **0.0491** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 5 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 234 | 233 | **0.0515** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 233 | 233 | **0.0536** | 0.054 | 16.2% | 83.8% | 0.0% | 10.7% | 73.0% | 0.0% | 16.3% | 0.0% |
| 7 | 29 | close_friend / citizen / poor_record / poor / woman_old | 39 | 233 | 233 | **0.0558** | 0.056 | 25.2% | 74.8% | 0.0% | 11.2% | 63.9% | 0.0% | 24.9% | 0.0% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | 39 | 233 | 232 | **0.0560** | 0.056 | 19.7% | 80.3% | 0.0% | 11.2% | 67.8% | 0.0% | 20.6% | 0.4% |
| 9 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 233 | **0.0579** | 0.058 | 28.2% | 71.8% | 0.0% | 11.5% | 60.3% | 0.0% | 27.8% | 0.4% |
| 10 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 232 | **0.0582** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 232 | **96.2%** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 234 | **95.3%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **95.3%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 4 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 234 | **94.9%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **94.0%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 233 | 233 | **93.2%** | 0.067 | 6.8% | 93.2% | 0.0% | 13.3% | 79.8% | 0.0% | 6.9% | 0.0% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 232 | **92.3%** | 0.067 | 7.7% | 92.3% | 0.0% | 13.3% | 78.1% | 0.0% | 8.2% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 233 | 233 | **90.6%** | 0.067 | 9.4% | 90.6% | 0.0% | 13.3% | 77.7% | 0.0% | 9.0% | 0.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 233 | **86.8%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 234 | 234 | **85.5%** | 0.066 | 14.5% | 85.5% | 0.0% | 13.2% | 72.2% | 0.0% | 14.5% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 232 | **15.0%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 233 | 230 | **15.4%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |
| 3 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 233 | 230 | **15.4%** | 0.074 | 84.6% | 15.4% | 0.4% | 10.3% | 4.7% | 1.7% | 81.5% | 1.3% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 233 | 230 | **16.2%** | 0.067 | 83.8% | 16.2% | 0.4% | 11.6% | 6.0% | 0.4% | 80.3% | 1.3% |
| 5 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 230 | 225 | **17.1%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 233 | 228 | **17.5%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 234 | 231 | **17.9%** | 0.082 | 82.1% | 17.9% | 0.0% | 13.7% | 4.3% | 1.3% | 79.5% | 1.3% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 234 | 232 | **18.8%** | 0.093 | 81.2% | 18.8% | 0.9% | 15.0% | 3.8% | 0.9% | 78.6% | 0.9% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 232 | 231 | **19.7%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 10 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 234 | 234 | **19.7%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |


**FACT (%)** *(Note: 40 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 233 | 230 | **2.1%** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 2 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 233 | 232 | **1.7%** | 0.134 | 73.9% | 26.1% | 1.7% | 19.7% | 4.3% | 1.7% | 72.1% | 0.4% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 234 | 234 | **1.7%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |
| 4 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 232 | 231 | **1.3%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 232 | **1.3%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 6 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 234 | 231 | **1.3%** | 0.130 | 74.8% | 25.2% | 1.3% | 20.5% | 4.3% | 1.3% | 71.4% | 1.3% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 234 | **1.3%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 229 | 226 | **0.9%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 9 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 232 | 230 | **0.9%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 10 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 233 | 230 | **0.9%** | 0.096 | 77.4% | 22.6% | 0.9% | 16.3% | 6.9% | 0.4% | 74.2% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 231 | 228 | **0.0%** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 2 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 229 | **0.0%** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 3 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 229 | **0.0%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 234 | 233 | **0.0%** | 0.118 | 76.5% | 23.5% | 0.0% | 16.7% | 3.8% | 3.4% | 75.6% | 0.4% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 234 | 230 | **0.0%** | 0.117 | 76.1% | 23.9% | 0.0% | 17.9% | 4.7% | 2.6% | 73.1% | 1.7% |
| 6 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 233 | 232 | **0.0%** | 0.112 | 76.5% | 23.5% | 0.0% | 20.6% | 3.0% | 0.9% | 75.1% | 0.4% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 230 | 228 | **0.0%** | 0.103 | 76.9% | 23.1% | 0.0% | 17.8% | 4.3% | 1.3% | 75.7% | 0.9% |
| 8 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 234 | 233 | **0.0%** | 0.101 | 27.8% | 72.2% | 0.0% | 20.1% | 52.1% | 0.0% | 27.4% | 0.4% |
| 9 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.096 | 29.5% | 70.5% | 0.0% | 19.2% | 51.7% | 0.0% | 29.1% | 0.0% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.094 | 17.1% | 82.9% | 0.0% | 18.8% | 63.7% | 0.0% | 17.5% | 0.0% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 231 | 228 | **29.9%** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 2 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 233 | 232 | **26.2%** | 0.144 | 68.8% | 31.2% | 0.4% | 26.2% | 5.2% | 0.9% | 67.0% | 0.4% |
| 3 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 229 | **26.1%** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 4 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 233 | 230 | **25.3%** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 230 | **25.0%** | 0.148 | 69.7% | 30.3% | 0.4% | 25.0% | 4.7% | 1.7% | 67.2% | 0.9% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 232 | 230 | **22.8%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 234 | 231 | **22.2%** | 0.143 | 71.4% | 28.6% | 0.9% | 22.2% | 6.0% | 2.1% | 67.5% | 1.3% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 229 | **22.2%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 9 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 231 | **21.8%** | 0.128 | 74.4% | 25.6% | 0.4% | 21.8% | 4.3% | 1.3% | 70.9% | 1.3% |
| 10 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 229 | 226 | **21.4%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 233 | **7.3%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **7.7%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 234 | **9.0%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 4 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **9.4%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 5 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 234 | 233 | **10.3%** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |
| 6 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 233 | 230 | **10.3%** | 0.074 | 84.6% | 15.4% | 0.4% | 10.3% | 4.7% | 1.7% | 81.5% | 1.3% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 233 | 233 | **10.7%** | 0.054 | 16.2% | 83.8% | 0.0% | 10.7% | 73.0% | 0.0% | 16.3% | 0.0% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | 39 | 233 | 232 | **11.2%** | 0.056 | 19.7% | 80.3% | 0.0% | 11.2% | 67.8% | 0.0% | 20.6% | 0.4% |
| 9 | 29 | close_friend / citizen / poor_record / poor / woman_old | 39 | 233 | 233 | **11.2%** | 0.056 | 25.2% | 74.8% | 0.0% | 11.2% | 63.9% | 0.0% | 24.9% | 0.0% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 230 | 225 | **11.3%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 234 | **85.5%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **85.0%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **85.0%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 232 | **83.6%** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 234 | **80.8%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 233 | 233 | **79.8%** | 0.067 | 6.8% | 93.2% | 0.0% | 13.3% | 79.8% | 0.0% | 6.9% | 0.0% |
| 7 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 233 | **79.5%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 232 | **78.1%** | 0.067 | 7.7% | 92.3% | 0.0% | 13.3% | 78.1% | 0.0% | 8.2% | 0.4% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 233 | 233 | **77.7%** | 0.067 | 9.4% | 90.6% | 0.0% | 13.3% | 77.7% | 0.0% | 9.0% | 0.0% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 234 | 233 | **75.2%** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 232 | 230 | **1.3%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 2 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 229 | **2.1%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 3 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 233 | 232 | **3.0%** | 0.112 | 76.5% | 23.5% | 0.0% | 20.6% | 3.0% | 0.9% | 75.1% | 0.4% |
| 4 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 233 | 228 | **3.0%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 5 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 233 | 230 | **3.0%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |
| 6 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 232 | 231 | **3.0%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 232 | **3.4%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 8 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 234 | **3.8%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 9 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 234 | 233 | **3.8%** | 0.118 | 76.5% | 23.5% | 0.0% | 16.7% | 3.8% | 3.4% | 75.6% | 0.4% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 234 | 232 | **3.8%** | 0.110 | 79.1% | 20.9% | 0.4% | 14.1% | 3.8% | 3.4% | 77.4% | 0.9% |


**CHECKED_TRUE (%)** *(Note: 31 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 234 | **3.4%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 2 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 234 | 233 | **3.4%** | 0.118 | 76.5% | 23.5% | 0.0% | 16.7% | 3.8% | 3.4% | 75.6% | 0.4% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 234 | 232 | **3.4%** | 0.110 | 79.1% | 20.9% | 0.4% | 14.1% | 3.8% | 3.4% | 77.4% | 0.9% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 232 | 230 | **3.0%** | 0.154 | 73.9% | 26.1% | 0.9% | 22.8% | 1.3% | 3.0% | 71.1% | 0.9% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 234 | 230 | **2.6%** | 0.117 | 76.1% | 23.9% | 0.0% | 17.9% | 4.7% | 2.6% | 73.1% | 1.7% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 229 | 226 | **2.2%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 234 | 231 | **2.1%** | 0.143 | 71.4% | 28.6% | 0.9% | 22.2% | 6.0% | 2.1% | 67.5% | 1.3% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 229 | **2.1%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 9 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 230 | **1.7%** | 0.148 | 69.7% | 30.3% | 0.4% | 25.0% | 4.7% | 1.7% | 67.2% | 0.9% |
| 10 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 233 | 232 | **1.7%** | 0.134 | 73.9% | 26.1% | 1.7% | 19.7% | 4.3% | 1.7% | 72.1% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 234 | 233 | **0.0%** | 0.101 | 27.8% | 72.2% | 0.0% | 20.1% | 52.1% | 0.0% | 27.4% | 0.4% |
| 2 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.096 | 29.5% | 70.5% | 0.0% | 19.2% | 51.7% | 0.0% | 29.1% | 0.0% |
| 3 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.094 | 17.1% | 82.9% | 0.0% | 18.8% | 63.7% | 0.0% | 17.5% | 0.0% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **0.0%** | 0.092 | 27.4% | 72.6% | 0.0% | 18.4% | 54.7% | 0.0% | 26.9% | 0.0% |
| 5 | 15 | close_friend / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0%** | 0.088 | 30.8% | 69.2% | 0.0% | 17.5% | 52.6% | 0.0% | 29.5% | 0.4% |
| 6 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 234 | 234 | **0.0%** | 0.088 | 28.6% | 71.4% | 0.0% | 17.5% | 53.8% | 0.0% | 28.6% | 0.0% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 233 | 231 | **0.0%** | 0.087 | 34.6% | 65.4% | 0.0% | 17.2% | 48.1% | 0.0% | 33.9% | 0.9% |
| 8 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 234 | 232 | **0.0%** | 0.084 | 22.6% | 77.4% | 0.4% | 15.8% | 61.1% | 0.0% | 21.8% | 0.9% |
| 9 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 234 | 234 | **0.0%** | 0.081 | 28.6% | 71.4% | 0.0% | 16.2% | 55.1% | 0.0% | 28.6% | 0.0% |
| 10 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 233 | 230 | **0.0%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 232 | **82.3%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 2 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 233 | 230 | **81.5%** | 0.074 | 84.6% | 15.4% | 0.4% | 10.3% | 4.7% | 1.7% | 81.5% | 1.3% |
| 3 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 233 | 230 | **81.1%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 233 | 230 | **80.3%** | 0.067 | 83.8% | 16.2% | 0.4% | 11.6% | 6.0% | 0.4% | 80.3% | 1.3% |
| 5 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 230 | 225 | **79.6%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |
| 6 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 234 | 231 | **79.5%** | 0.082 | 82.1% | 17.9% | 0.0% | 13.7% | 4.3% | 1.3% | 79.5% | 1.3% |
| 7 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 233 | 228 | **79.4%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 234 | 232 | **78.6%** | 0.093 | 81.2% | 18.8% | 0.9% | 15.0% | 3.8% | 0.9% | 78.6% | 0.9% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 232 | 231 | **78.4%** | 0.100 | 80.3% | 19.7% | 1.3% | 16.4% | 3.0% | 0.4% | 78.4% | 0.4% |
| 10 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 234 | 234 | **77.8%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 232 | **4.7%** | 0.058 | 3.8% | 96.2% | 0.0% | 11.6% | 83.6% | 0.0% | 4.7% | 0.0% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 234 | **5.1%** | 0.049 | 4.7% | 95.3% | 0.0% | 9.0% | 85.5% | 0.4% | 5.1% | 0.0% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **5.1%** | 0.047 | 4.7% | 95.3% | 0.0% | 9.4% | 85.0% | 0.0% | 5.1% | 0.4% |
| 4 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 234 | **5.6%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 233 | 233 | **6.9%** | 0.067 | 6.8% | 93.2% | 0.0% | 13.3% | 79.8% | 0.0% | 6.9% | 0.0% |
| 6 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **7.3%** | 0.038 | 6.0% | 94.0% | 0.0% | 7.7% | 85.0% | 0.0% | 7.3% | 0.0% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 232 | **8.2%** | 0.067 | 7.7% | 92.3% | 0.0% | 13.3% | 78.1% | 0.0% | 8.2% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 233 | 233 | **9.0%** | 0.067 | 9.4% | 90.6% | 0.0% | 13.3% | 77.7% | 0.0% | 9.0% | 0.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 233 | **12.8%** | 0.036 | 13.2% | 86.8% | 0.0% | 7.3% | 79.5% | 0.0% | 12.8% | 0.4% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 234 | 233 | **14.1%** | 0.052 | 15.0% | 85.0% | 0.0% | 10.3% | 75.2% | 0.0% | 14.1% | 0.4% |


**NOT_MENTIONED (%)** *(Note: 20 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 230 | 225 | **2.2%** | 0.067 | 82.9% | 17.1% | 0.0% | 11.3% | 6.1% | 0.9% | 79.6% | 2.2% |
| 2 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 233 | 228 | **2.1%** | 0.083 | 82.5% | 17.5% | 0.4% | 14.6% | 3.0% | 0.4% | 79.4% | 2.1% |
| 3 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 229 | **2.1%** | 0.146 | 69.2% | 30.8% | 0.0% | 26.1% | 4.7% | 1.3% | 65.8% | 2.1% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 229 | **2.1%** | 0.135 | 74.4% | 25.6% | 0.0% | 22.2% | 2.1% | 2.1% | 71.4% | 2.1% |
| 5 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 234 | 230 | **1.7%** | 0.117 | 76.1% | 23.9% | 0.0% | 17.9% | 4.7% | 2.6% | 73.1% | 1.7% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 229 | 226 | **1.3%** | 0.139 | 71.8% | 28.2% | 0.9% | 21.4% | 4.8% | 2.2% | 69.4% | 1.3% |
| 7 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 231 | 228 | **1.3%** | 0.160 | 64.5% | 35.5% | 0.0% | 29.9% | 6.1% | 0.9% | 61.9% | 1.3% |
| 8 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 233 | 230 | **1.3%** | 0.159 | 67.5% | 32.5% | 2.1% | 25.3% | 5.6% | 0.9% | 64.8% | 1.3% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 233 | 230 | **1.3%** | 0.096 | 77.4% | 22.6% | 0.9% | 16.3% | 6.9% | 0.4% | 74.2% | 1.3% |
| 10 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 233 | 230 | **1.3%** | 0.078 | 84.6% | 15.4% | 0.9% | 13.7% | 3.0% | 0.0% | 81.1% | 1.3% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 234 | **0.0%** | 0.122 | 76.9% | 23.1% | 1.3% | 15.0% | 3.8% | 3.4% | 76.5% | 0.0% |
| 2 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.096 | 29.5% | 70.5% | 0.0% | 19.2% | 51.7% | 0.0% | 29.1% | 0.0% |
| 3 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.094 | 17.1% | 82.9% | 0.0% | 18.8% | 63.7% | 0.0% | 17.5% | 0.0% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 234 | 234 | **0.0%** | 0.092 | 27.4% | 72.6% | 0.0% | 18.4% | 54.7% | 0.0% | 26.9% | 0.0% |
| 5 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.092 | 80.3% | 19.7% | 1.7% | 13.2% | 6.4% | 0.9% | 77.8% | 0.0% |
| 6 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 234 | 234 | **0.0%** | 0.088 | 28.6% | 71.4% | 0.0% | 17.5% | 53.8% | 0.0% | 28.6% | 0.0% |
| 7 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 234 | 234 | **0.0%** | 0.081 | 28.6% | 71.4% | 0.0% | 16.2% | 55.1% | 0.0% | 28.6% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 232 | **0.0%** | 0.080 | 85.0% | 15.0% | 1.3% | 12.5% | 3.4% | 0.4% | 82.3% | 0.0% |
| 9 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 234 | 234 | **0.0%** | 0.075 | 27.8% | 72.2% | 0.0% | 15.0% | 57.7% | 0.0% | 27.4% | 0.0% |
| 10 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 234 | **0.0%** | 0.068 | 5.1% | 94.9% | 0.0% | 13.7% | 80.8% | 0.0% | 5.6% | 0.0% |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 204 | **0.0539** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 2 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 208 | **0.0505** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 3 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **0.0481** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 200 | **0.0475** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 5 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **0.0469** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 234 | 204 | **0.0466** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 7 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 232 | 193 | **0.0440** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 8 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 199 | **0.0427** | 0.043 | 67.5% | 32.5% | 0.4% | 6.4% | 9.8% | 0.0% | 68.4% | 15.0% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 206 | **0.0413** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 10 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 233 | 196 | **0.0383** | 0.038 | 70.9% | 29.1% | 0.4% | 5.6% | 8.6% | 0.0% | 69.5% | 15.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 229 | **0.0066** | 0.007 | 60.7% | 39.3% | 0.0% | 1.3% | 33.3% | 0.0% | 63.2% | 2.1% |
| 2 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 228 | **0.0066** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |
| 3 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 227 | **0.0066** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 4 | 28 | close_friend / citizen / poor_record / rich / man_old | 39 | 234 | 226 | **0.0066** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 35.9% | 0.0% | 59.4% | 3.4% |
| 5 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 234 | 226 | **0.0066** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 44.9% | 0.0% | 50.4% | 3.4% |
| 6 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 232 | 222 | **0.0068** | 0.007 | 57.3% | 42.7% | 0.0% | 1.3% | 34.9% | 0.0% | 59.5% | 4.3% |
| 7 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 233 | 201 | **0.0075** | 0.007 | 70.1% | 29.9% | 0.0% | 1.3% | 9.4% | 0.0% | 75.5% | 13.7% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 229 | **0.0087** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 9 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 234 | 222 | **0.0090** | 0.009 | 56.8% | 43.2% | 0.0% | 1.7% | 32.5% | 0.0% | 60.7% | 5.1% |
| 10 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 233 | 226 | **0.0111** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 233 | 226 | **60.7%** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 230 | **59.8%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 3 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 227 | **58.1%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 228 | **55.6%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 225 | **55.1%** | 0.011 | 44.9% | 55.1% | 0.0% | 2.2% | 52.2% | 0.0% | 42.7% | 3.0% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 229 | **53.8%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 230 | 223 | **53.0%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 45.7% | 0.0% | 48.7% | 3.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 231 | **53.0%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 9 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 234 | 225 | **51.7%** | 0.020 | 48.3% | 51.7% | 0.4% | 3.0% | 34.2% | 0.0% | 58.5% | 3.8% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 228 | **50.9%** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 234 | 198 | **20.5%** | 0.020 | 79.5% | 20.5% | 0.4% | 2.6% | 8.1% | 0.0% | 73.5% | 15.4% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 232 | 210 | **21.8%** | 0.021 | 78.2% | 21.8% | 0.0% | 3.9% | 7.8% | 0.0% | 78.9% | 9.5% |
| 3 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 232 | 194 | **23.5%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 232 | 198 | **23.9%** | 0.018 | 76.1% | 23.9% | 0.0% | 2.2% | 9.9% | 0.4% | 72.8% | 14.7% |
| 5 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 234 | 204 | **24.8%** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 6 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 234 | 207 | **26.1%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 233 | 197 | **26.1%** | 0.028 | 73.9% | 26.1% | 0.9% | 3.0% | 7.3% | 0.0% | 73.4% | 15.5% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 199 | **26.1%** | 0.028 | 73.9% | 26.1% | 0.0% | 4.7% | 5.6% | 0.0% | 74.8% | 15.0% |
| 9 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 232 | 199 | **26.5%** | 0.023 | 73.5% | 26.5% | 0.4% | 3.0% | 7.3% | 0.0% | 75.0% | 14.2% |
| 10 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 194 | **28.2%** | 0.028 | 71.8% | 28.2% | 0.4% | 3.8% | 7.7% | 0.0% | 70.9% | 17.1% |


**FACT (%)** *(Note: 45 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 200 | **1.3%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 2 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 208 | **1.3%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 3 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 231 | 198 | **0.9%** | 0.038 | 70.9% | 29.1% | 0.9% | 4.8% | 6.9% | 0.0% | 73.2% | 14.3% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 206 | **0.9%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 5 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 233 | 196 | **0.9%** | 0.038 | 70.9% | 29.1% | 0.9% | 3.9% | 7.3% | 0.4% | 71.7% | 15.9% |
| 6 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 233 | 195 | **0.9%** | 0.028 | 68.4% | 31.6% | 0.9% | 3.0% | 6.9% | 0.0% | 73.0% | 16.3% |
| 7 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 233 | 197 | **0.9%** | 0.028 | 73.9% | 26.1% | 0.9% | 3.0% | 7.3% | 0.0% | 73.4% | 15.5% |
| 8 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 204 | **0.9%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 9 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 232 | 193 | **0.4%** | 0.023 | 67.5% | 32.5% | 0.4% | 3.0% | 6.9% | 0.0% | 72.8% | 16.8% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 232 | 199 | **0.4%** | 0.023 | 73.5% | 26.5% | 0.4% | 3.0% | 7.3% | 0.0% | 75.0% | 14.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **0.0%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **0.0%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 232 | 193 | **0.0%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 4 | 2 | close_friend / mayor / good_record / rich / man_young | 39 | 233 | 195 | **0.0%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 70.0% | 16.3% |
| 5 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 233 | 210 | **0.0%** | 0.033 | 70.1% | 29.9% | 0.0% | 6.0% | 10.7% | 0.0% | 73.4% | 9.9% |
| 6 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 233 | 199 | **0.0%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 71.7% | 14.6% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 233 | 200 | **0.0%** | 0.033 | 68.4% | 31.6% | 0.0% | 5.6% | 9.4% | 0.0% | 70.8% | 14.2% |
| 8 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 234 | 205 | **0.0%** | 0.032 | 67.1% | 32.9% | 0.0% | 5.6% | 6.8% | 0.0% | 75.2% | 12.4% |
| 9 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 234 | 207 | **0.0%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 10 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 232 | 194 | **0.0%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **8.6%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **7.8%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 204 | **6.8%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 4 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 232 | 193 | **6.5%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 5 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 208 | **6.4%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 234 | 204 | **6.4%** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 7 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 199 | **6.4%** | 0.043 | 67.5% | 32.5% | 0.4% | 6.4% | 9.8% | 0.0% | 68.4% | 15.0% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 233 | 210 | **6.0%** | 0.033 | 70.1% | 29.9% | 0.0% | 6.0% | 10.7% | 0.0% | 73.4% | 9.9% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 200 | **5.6%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 10 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 206 | **5.6%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 28 | close_friend / citizen / poor_record / rich / man_old | 39 | 234 | 226 | **1.3%** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 35.9% | 0.0% | 59.4% | 3.4% |
| 2 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 234 | 226 | **1.3%** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 44.9% | 0.0% | 50.4% | 3.4% |
| 3 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 227 | **1.3%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 4 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 228 | **1.3%** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |
| 5 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 229 | **1.3%** | 0.007 | 60.7% | 39.3% | 0.0% | 1.3% | 33.3% | 0.0% | 63.2% | 2.1% |
| 6 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 233 | 201 | **1.3%** | 0.007 | 70.1% | 29.9% | 0.0% | 1.3% | 9.4% | 0.0% | 75.5% | 13.7% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 232 | 222 | **1.3%** | 0.007 | 57.3% | 42.7% | 0.0% | 1.3% | 34.9% | 0.0% | 59.5% | 4.3% |
| 8 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 234 | 230 | **1.7%** | 0.013 | 54.3% | 45.7% | 0.4% | 1.7% | 31.6% | 0.0% | 64.5% | 1.7% |
| 9 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 234 | 222 | **1.7%** | 0.009 | 56.8% | 43.2% | 0.0% | 1.7% | 32.5% | 0.0% | 60.7% | 5.1% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 229 | **1.7%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 230 | **56.4%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 233 | 226 | **56.2%** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 225 | **52.2%** | 0.011 | 44.9% | 55.1% | 0.0% | 2.2% | 52.2% | 0.0% | 42.7% | 3.0% |
| 4 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 227 | **49.6%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 228 | **48.3%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 231 | **47.2%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 7 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 229 | **46.6%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 8 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 227 | **45.7%** | 0.015 | 50.4% | 49.6% | 0.0% | 3.0% | 45.7% | 0.0% | 48.3% | 3.0% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 228 | **45.7%** | 0.007 | 49.1% | 50.9% | 0.0% | 1.3% | 45.7% | 0.0% | 50.4% | 2.6% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 230 | 223 | **45.7%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 45.7% | 0.0% | 48.7% | 3.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 204 | **5.1%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **5.2%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 199 | **5.6%** | 0.028 | 73.9% | 26.1% | 0.0% | 4.7% | 5.6% | 0.0% | 74.8% | 15.0% |
| 4 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 232 | 194 | **5.6%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |
| 5 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 234 | 207 | **6.0%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 6 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **6.4%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 234 | 205 | **6.8%** | 0.032 | 67.1% | 32.9% | 0.0% | 5.6% | 6.8% | 0.0% | 75.2% | 12.4% |
| 8 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 233 | 195 | **6.9%** | 0.028 | 68.4% | 31.6% | 0.9% | 3.0% | 6.9% | 0.0% | 73.0% | 16.3% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 206 | **6.9%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 10 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 232 | 193 | **6.9%** | 0.023 | 67.5% | 32.5% | 0.4% | 3.0% | 6.9% | 0.0% | 72.8% | 16.8% |


**CHECKED_TRUE (%)** *(Note: 58 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 232 | 193 | **0.4%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 232 | 198 | **0.4%** | 0.018 | 76.1% | 23.9% | 0.0% | 2.2% | 9.9% | 0.4% | 72.8% | 14.7% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 233 | 196 | **0.4%** | 0.038 | 70.9% | 29.1% | 0.9% | 3.9% | 7.3% | 0.4% | 71.7% | 15.9% |
| 4 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 204 | **0.4%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |
| 5 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 234 | 204 | **0.4%** | 0.047 | 75.2% | 24.8% | 0.4% | 6.4% | 9.4% | 0.4% | 70.5% | 12.8% |
| 6 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 234 | 198 | **0.4%** | 0.018 | 70.5% | 29.5% | 0.0% | 2.1% | 8.1% | 0.4% | 73.9% | 15.4% |
| 7 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 208 | **0.0%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **0.0%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 9 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 200 | **0.0%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **0.0%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 208 | **0.0%** | 0.050 | 67.9% | 32.1% | 1.3% | 6.4% | 8.6% | 0.0% | 73.0% | 10.7% |
| 2 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **0.0%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 3 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 200 | **0.0%** | 0.048 | 66.7% | 33.3% | 1.3% | 5.6% | 7.3% | 0.0% | 72.0% | 13.8% |
| 4 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **0.0%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 5 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 199 | **0.0%** | 0.043 | 67.5% | 32.5% | 0.4% | 6.4% | 9.8% | 0.0% | 68.4% | 15.0% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 206 | **0.0%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 233 | 196 | **0.0%** | 0.038 | 70.9% | 29.1% | 0.4% | 5.6% | 8.6% | 0.0% | 69.5% | 15.9% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 231 | 198 | **0.0%** | 0.038 | 70.9% | 29.1% | 0.9% | 4.8% | 6.9% | 0.0% | 73.2% | 14.3% |
| 9 | 2 | close_friend / mayor / good_record / rich / man_young | 39 | 233 | 195 | **0.0%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 70.0% | 16.3% |
| 10 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 233 | 210 | **0.0%** | 0.033 | 70.1% | 29.9% | 0.0% | 6.0% | 10.7% | 0.0% | 73.4% | 9.9% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 232 | 210 | **78.9%** | 0.021 | 78.2% | 21.8% | 0.0% | 3.9% | 7.8% | 0.0% | 78.9% | 9.5% |
| 2 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 234 | 207 | **77.4%** | 0.029 | 73.9% | 26.1% | 0.0% | 5.1% | 6.0% | 0.0% | 77.4% | 11.5% |
| 3 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 233 | 201 | **75.5%** | 0.007 | 70.1% | 29.9% | 0.0% | 1.3% | 9.4% | 0.0% | 75.5% | 13.7% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 206 | **75.4%** | 0.041 | 66.7% | 33.3% | 0.9% | 5.6% | 6.9% | 0.0% | 75.4% | 11.2% |
| 5 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 234 | 205 | **75.2%** | 0.032 | 67.1% | 32.9% | 0.0% | 5.6% | 6.8% | 0.0% | 75.2% | 12.4% |
| 6 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 233 | 203 | **75.1%** | 0.030 | 71.4% | 28.6% | 0.4% | 4.3% | 7.3% | 0.0% | 75.1% | 12.9% |
| 7 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 232 | 199 | **75.0%** | 0.023 | 73.5% | 26.5% | 0.4% | 3.0% | 7.3% | 0.0% | 75.0% | 14.2% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 199 | **74.8%** | 0.028 | 73.9% | 26.1% | 0.0% | 4.7% | 5.6% | 0.0% | 74.8% | 15.0% |
| 9 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 233 | 208 | **74.2%** | 0.048 | 70.1% | 29.9% | 0.0% | 8.6% | 6.4% | 0.0% | 74.2% | 10.7% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 204 | **73.9%** | 0.054 | 70.1% | 29.9% | 0.9% | 6.8% | 5.1% | 0.4% | 73.9% | 12.8% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 233 | 226 | **38.6%** | 0.011 | 39.3% | 60.7% | 0.0% | 2.1% | 56.2% | 0.0% | 38.6% | 3.0% |
| 2 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 230 | **39.3%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 232 | 225 | **42.7%** | 0.011 | 44.9% | 55.1% | 0.0% | 2.2% | 52.2% | 0.0% | 42.7% | 3.0% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 228 | **44.9%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 5 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 227 | **46.2%** | 0.007 | 41.9% | 58.1% | 0.0% | 1.3% | 49.6% | 0.0% | 46.2% | 3.0% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 227 | **48.3%** | 0.015 | 50.4% | 49.6% | 0.0% | 3.0% | 45.7% | 0.0% | 48.3% | 3.0% |
| 7 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 230 | 223 | **48.7%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 45.7% | 0.0% | 48.7% | 3.0% |
| 8 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 231 | **49.4%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 229 | **49.6%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 234 | 226 | **50.4%** | 0.007 | 50.9% | 49.1% | 0.0% | 1.3% | 44.9% | 0.0% | 50.4% | 3.4% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 194 | **17.1%** | 0.028 | 71.8% | 28.2% | 0.4% | 3.8% | 7.7% | 0.0% | 70.9% | 17.1% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 231 | 192 | **16.9%** | 0.047 | 68.4% | 31.6% | 0.0% | 7.8% | 5.2% | 0.0% | 70.1% | 16.9% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 232 | 193 | **16.8%** | 0.044 | 70.1% | 29.9% | 0.0% | 6.5% | 7.3% | 0.4% | 69.0% | 16.8% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 232 | 193 | **16.8%** | 0.023 | 67.5% | 32.5% | 0.4% | 3.0% | 6.9% | 0.0% | 72.8% | 16.8% |
| 5 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 232 | 194 | **16.4%** | 0.028 | 76.5% | 23.5% | 0.0% | 4.7% | 5.6% | 0.0% | 73.3% | 16.4% |
| 6 | 2 | close_friend / mayor / good_record / rich / man_young | 39 | 233 | 195 | **16.3%** | 0.033 | 69.2% | 30.8% | 0.0% | 5.6% | 8.2% | 0.0% | 70.0% | 16.3% |
| 7 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 233 | 195 | **16.3%** | 0.028 | 68.4% | 31.6% | 0.9% | 3.0% | 6.9% | 0.0% | 73.0% | 16.3% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 233 | 196 | **15.9%** | 0.038 | 70.9% | 29.1% | 0.4% | 5.6% | 8.6% | 0.0% | 69.5% | 15.9% |
| 9 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 233 | 196 | **15.9%** | 0.038 | 70.9% | 29.1% | 0.9% | 3.9% | 7.3% | 0.4% | 71.7% | 15.9% |
| 10 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 233 | 197 | **15.5%** | 0.028 | 73.9% | 26.1% | 0.9% | 3.0% | 7.3% | 0.0% | 73.4% | 15.5% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 233 | 231 | **0.9%** | 0.015 | 53.0% | 47.0% | 0.0% | 3.0% | 43.8% | 0.0% | 52.4% | 0.9% |
| 2 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 233 | 231 | **0.9%** | 0.013 | 47.0% | 53.0% | 0.0% | 2.6% | 47.2% | 0.0% | 49.4% | 0.9% |
| 3 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 230 | **1.7%** | 0.013 | 40.2% | 59.8% | 0.0% | 2.6% | 56.4% | 0.0% | 39.3% | 1.7% |
| 4 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 234 | 230 | **1.7%** | 0.013 | 54.3% | 45.7% | 0.4% | 1.7% | 31.6% | 0.0% | 64.5% | 1.7% |
| 5 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 229 | **2.1%** | 0.009 | 46.2% | 53.8% | 0.0% | 1.7% | 46.6% | 0.0% | 49.6% | 2.1% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 229 | **2.1%** | 0.007 | 60.7% | 39.3% | 0.0% | 1.3% | 33.3% | 0.0% | 63.2% | 2.1% |
| 7 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 233 | 228 | **2.1%** | 0.022 | 60.7% | 39.3% | 0.0% | 4.3% | 30.5% | 0.0% | 63.1% | 2.1% |
| 8 | 25 | close_friend / citizen / poor_record / rich / woman_old | 39 | 233 | 228 | **2.1%** | 0.022 | 61.1% | 38.9% | 0.0% | 4.3% | 26.2% | 0.0% | 67.4% | 2.1% |
| 9 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 228 | **2.6%** | 0.022 | 44.4% | 55.6% | 0.0% | 4.3% | 48.3% | 0.0% | 44.9% | 2.6% |
| 10 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 234 | 228 | **2.6%** | 0.015 | 53.4% | 46.6% | 0.0% | 3.0% | 32.5% | 0.0% | 62.0% | 2.6% |


### Model: Qwen3.8-Flash

#### Source POV (All 12 Listeners)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 464 | 454 | **0.0419** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 464 | 447 | **0.0347** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 466 | 457 | **0.0328** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 464 | 460 | **0.0326** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 466 | 451 | **0.0310** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 467 | 452 | **0.0310** | 0.031 | 65.2% | 34.8% | 0.9% | 4.3% | 6.2% | 0.0% | 85.4% | 3.2% |
| 7 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 466 | 452 | **0.0310** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 8 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 465 | 448 | **0.0301** | 0.030 | 66.7% | 33.3% | 0.6% | 4.5% | 7.1% | 0.0% | 84.1% | 3.7% |
| 9 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 468 | 452 | **0.0299** | 0.030 | 67.1% | 32.9% | 0.2% | 4.5% | 8.3% | 0.4% | 83.1% | 3.4% |
| 10 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 437 | **0.0297** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 467 | 456 | **0.0066** | 0.007 | 54.7% | 45.3% | 0.2% | 0.9% | 18.8% | 0.0% | 77.7% | 2.4% |
| 2 | 28 | close_friend / citizen / poor_record / rich / man_old | 39 | 467 | 455 | **0.0066** | 0.007 | 59.2% | 40.8% | 0.2% | 0.9% | 14.6% | 0.0% | 81.8% | 2.6% |
| 3 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 467 | 457 | **0.0077** | 0.008 | 58.3% | 41.7% | 0.2% | 0.6% | 12.0% | 0.2% | 84.8% | 2.1% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 467 | 451 | **0.0078** | 0.008 | 59.2% | 40.8% | 0.2% | 0.2% | 15.8% | 0.4% | 79.9% | 3.4% |
| 5 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 467 | 448 | **0.0078** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 468 | 456 | **0.0088** | 0.009 | 57.1% | 42.9% | 0.4% | 0.9% | 19.0% | 0.0% | 77.1% | 2.6% |
| 7 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 468 | 452 | **0.0088** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 8 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 465 | 443 | **0.0090** | 0.009 | 58.1% | 41.9% | 0.2% | 0.9% | 16.1% | 0.2% | 77.8% | 4.7% |
| 9 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **0.0108** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 10 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 467 | 460 | **0.0109** | 0.011 | 56.4% | 43.6% | 0.2% | 1.3% | 14.3% | 0.2% | 82.4% | 1.5% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 467 | 454 | **60.0%** | 0.014 | 40.0% | 60.0% | 0.2% | 2.4% | 39.2% | 0.0% | 55.5% | 2.8% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 456 | **58.5%** | 0.016 | 41.5% | 58.5% | 0.4% | 2.4% | 34.6% | 0.0% | 60.0% | 2.6% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 452 | **55.6%** | 0.019 | 44.4% | 55.6% | 0.4% | 2.8% | 32.1% | 0.0% | 61.5% | 3.2% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 468 | 452 | **55.3%** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 468 | 452 | **53.8%** | 0.024 | 46.2% | 53.8% | 0.4% | 3.8% | 27.4% | 0.0% | 65.0% | 3.4% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 468 | 455 | **51.9%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 457 | **51.7%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 468 | 455 | **50.0%** | 0.016 | 50.0% | 50.0% | 0.6% | 1.9% | 22.9% | 0.0% | 71.8% | 2.8% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 467 | 457 | **49.4%** | 0.011 | 50.6% | 49.4% | 0.2% | 1.7% | 21.8% | 0.0% | 74.1% | 2.1% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 467 | 448 | **49.1%** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 452 | **28.4%** | 0.027 | 71.6% | 28.4% | 0.6% | 3.4% | 6.0% | 0.2% | 86.7% | 3.0% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 468 | 463 | **29.1%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 466 | 450 | **29.5%** | 0.016 | 70.5% | 29.5% | 0.4% | 2.1% | 7.1% | 0.0% | 86.9% | 3.4% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 466 | 454 | **29.7%** | 0.023 | 70.3% | 29.7% | 0.6% | 3.2% | 8.4% | 0.0% | 85.2% | 2.6% |
| 5 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 467 | 459 | **30.6%** | 0.024 | 69.4% | 30.6% | 0.4% | 3.9% | 8.1% | 0.0% | 85.9% | 1.7% |
| 6 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 465 | 453 | **30.8%** | 0.023 | 69.2% | 30.8% | 0.2% | 4.1% | 6.5% | 0.0% | 86.7% | 2.6% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 466 | 447 | **31.0%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 8 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 466 | 451 | **31.2%** | 0.020 | 68.8% | 31.2% | 0.4% | 3.0% | 6.2% | 0.0% | 87.1% | 3.2% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 464 | 454 | **31.4%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 464 | 447 | **31.8%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 465 | 451 | **1.3%** | 0.019 | 60.0% | 40.0% | 1.3% | 0.6% | 14.4% | 0.2% | 80.4% | 3.0% |
| 2 | 27 | close_friend / citizen / poor_record / rich / woman_young | 39 | 466 | 453 | **1.3%** | 0.021 | 60.0% | 40.0% | 1.3% | 1.1% | 11.4% | 0.2% | 83.3% | 2.8% |
| 3 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 468 | 461 | **1.1%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 468 | 459 | **1.1%** | 0.016 | 62.6% | 37.4% | 1.1% | 1.1% | 10.7% | 0.0% | 85.3% | 1.9% |
| 5 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 464 | 454 | **0.9%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 6 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 464 | 460 | **0.9%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 7 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 465 | 448 | **0.9%** | 0.026 | 63.2% | 36.8% | 0.9% | 3.2% | 6.7% | 0.0% | 85.6% | 3.7% |
| 8 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 466 | 457 | **0.9%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 9 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 437 | **0.9%** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 466 | 456 | **0.9%** | 0.025 | 67.9% | 32.1% | 0.9% | 3.2% | 10.3% | 0.0% | 83.5% | 2.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 468 | 445 | **0.0%** | 0.021 | 65.4% | 34.6% | 0.0% | 4.1% | 8.1% | 0.0% | 82.9% | 4.9% |
| 2 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 466 | 457 | **0.0%** | 0.018 | 68.2% | 31.8% | 0.0% | 3.4% | 8.2% | 0.0% | 86.5% | 1.9% |
| 3 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 457 | **0.0%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 4 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 468 | 458 | **0.0%** | 0.011 | 56.2% | 43.8% | 0.0% | 1.7% | 18.6% | 0.2% | 77.4% | 2.1% |
| 5 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 467 | 448 | **0.0%** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 468 | 452 | **0.2%** | 0.030 | 67.1% | 32.9% | 0.2% | 4.5% | 8.3% | 0.4% | 83.1% | 3.4% |
| 7 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 468 | 453 | **0.2%** | 0.029 | 66.5% | 33.5% | 0.2% | 5.1% | 7.5% | 0.0% | 84.0% | 3.2% |
| 8 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 468 | 463 | **0.2%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 9 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 468 | 455 | **0.2%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 10 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 468 | 450 | **0.2%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 464 | 454 | **6.0%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 466 | 451 | **5.6%** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 3 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 464 | 447 | **5.4%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 466 | 452 | **5.2%** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 5 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 468 | 453 | **5.1%** | 0.029 | 66.5% | 33.5% | 0.2% | 5.1% | 7.5% | 0.0% | 84.0% | 3.2% |
| 6 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 466 | 455 | **4.9%** | 0.030 | 66.9% | 33.1% | 0.4% | 4.9% | 8.6% | 0.0% | 83.7% | 2.4% |
| 7 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 464 | 460 | **4.7%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 464 | 453 | **4.7%** | 0.029 | 67.7% | 32.3% | 0.2% | 4.7% | 8.8% | 0.2% | 83.6% | 2.4% |
| 9 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 465 | 448 | **4.5%** | 0.030 | 66.7% | 33.3% | 0.6% | 4.5% | 7.1% | 0.0% | 84.1% | 3.7% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 466 | 447 | **4.5%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 467 | 451 | **0.2%** | 0.008 | 59.2% | 40.8% | 0.2% | 0.2% | 15.8% | 0.4% | 79.9% | 3.4% |
| 2 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **0.4%** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 3 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 467 | 457 | **0.6%** | 0.008 | 58.3% | 41.7% | 0.2% | 0.6% | 12.0% | 0.2% | 84.8% | 2.1% |
| 4 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 465 | 451 | **0.6%** | 0.019 | 60.0% | 40.0% | 1.3% | 0.6% | 14.4% | 0.2% | 80.4% | 3.0% |
| 5 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 468 | 456 | **0.9%** | 0.009 | 57.1% | 42.9% | 0.4% | 0.9% | 19.0% | 0.0% | 77.1% | 2.6% |
| 6 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 467 | 452 | **0.9%** | 0.013 | 57.5% | 42.5% | 0.9% | 0.9% | 15.6% | 0.0% | 79.4% | 3.2% |
| 7 | 28 | close_friend / citizen / poor_record / rich / man_old | 39 | 467 | 455 | **0.9%** | 0.007 | 59.2% | 40.8% | 0.2% | 0.9% | 14.6% | 0.0% | 81.8% | 2.6% |
| 8 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 467 | 456 | **0.9%** | 0.007 | 54.7% | 45.3% | 0.2% | 0.9% | 18.8% | 0.0% | 77.7% | 2.4% |
| 9 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 465 | 443 | **0.9%** | 0.009 | 58.1% | 41.9% | 0.2% | 0.9% | 16.1% | 0.2% | 77.8% | 4.7% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 468 | 461 | **1.1%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 467 | 454 | **39.2%** | 0.014 | 40.0% | 60.0% | 0.2% | 2.4% | 39.2% | 0.0% | 55.5% | 2.8% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 456 | **34.6%** | 0.016 | 41.5% | 58.5% | 0.4% | 2.4% | 34.6% | 0.0% | 60.0% | 2.6% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 468 | 452 | **33.3%** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 452 | **32.1%** | 0.019 | 44.4% | 55.6% | 0.4% | 2.8% | 32.1% | 0.0% | 61.5% | 3.2% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 457 | **28.5%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 468 | 455 | **28.4%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 468 | 452 | **27.4%** | 0.024 | 46.2% | 53.8% | 0.4% | 3.8% | 27.4% | 0.0% | 65.0% | 3.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 468 | 455 | **22.9%** | 0.016 | 50.0% | 50.0% | 0.6% | 1.9% | 22.9% | 0.0% | 71.8% | 2.8% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 468 | 450 | **22.9%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 10 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 467 | 457 | **21.8%** | 0.011 | 50.6% | 49.4% | 0.2% | 1.7% | 21.8% | 0.0% | 74.1% | 2.1% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 452 | **6.0%** | 0.027 | 71.6% | 28.4% | 0.6% | 3.4% | 6.0% | 0.2% | 86.7% | 3.0% |
| 2 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 467 | 452 | **6.2%** | 0.031 | 65.2% | 34.8% | 0.9% | 4.3% | 6.2% | 0.0% | 85.4% | 3.2% |
| 3 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 466 | 451 | **6.2%** | 0.020 | 68.8% | 31.2% | 0.4% | 3.0% | 6.2% | 0.0% | 87.1% | 3.2% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 466 | 452 | **6.4%** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 5 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 465 | 453 | **6.5%** | 0.023 | 69.2% | 30.8% | 0.2% | 4.1% | 6.5% | 0.0% | 86.7% | 2.6% |
| 6 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 466 | 457 | **6.7%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 7 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 466 | 451 | **6.7%** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 8 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 465 | 448 | **6.7%** | 0.026 | 63.2% | 36.8% | 0.9% | 3.2% | 6.7% | 0.0% | 85.6% | 3.7% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 466 | 447 | **6.9%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 10 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 466 | 450 | **7.1%** | 0.016 | 70.5% | 29.5% | 0.4% | 2.1% | 7.1% | 0.0% | 86.9% | 3.4% |


**CHECKED_TRUE (%)** *(Note: 43 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 467 | 451 | **0.4%** | 0.008 | 59.2% | 40.8% | 0.2% | 0.2% | 15.8% | 0.4% | 79.9% | 3.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 468 | 452 | **0.4%** | 0.030 | 67.1% | 32.9% | 0.2% | 4.5% | 8.3% | 0.4% | 83.1% | 3.4% |
| 3 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 468 | 461 | **0.4%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |
| 4 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 468 | 450 | **0.4%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 5 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **0.4%** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 6 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 464 | 454 | **0.2%** | 0.042 | 68.6% | 31.4% | 0.9% | 6.0% | 8.0% | 0.2% | 82.8% | 2.2% |
| 7 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 464 | 447 | **0.2%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |
| 8 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 464 | 453 | **0.2%** | 0.029 | 67.7% | 32.3% | 0.2% | 4.7% | 8.8% | 0.2% | 83.6% | 2.4% |
| 9 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 465 | 451 | **0.2%** | 0.019 | 60.0% | 40.0% | 1.3% | 0.6% | 14.4% | 0.2% | 80.4% | 3.0% |
| 10 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 465 | 451 | **0.2%** | 0.011 | 58.8% | 41.2% | 0.2% | 1.3% | 17.4% | 0.2% | 77.8% | 3.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 464 | 460 | **0.0%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 2 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 466 | 451 | **0.0%** | 0.031 | 65.0% | 35.0% | 0.2% | 5.6% | 6.7% | 0.0% | 84.3% | 3.2% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 467 | 452 | **0.0%** | 0.031 | 65.2% | 34.8% | 0.9% | 4.3% | 6.2% | 0.0% | 85.4% | 3.2% |
| 4 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 466 | 452 | **0.0%** | 0.031 | 66.9% | 33.1% | 0.4% | 5.2% | 6.4% | 0.0% | 85.0% | 3.0% |
| 5 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 465 | 448 | **0.0%** | 0.030 | 66.7% | 33.3% | 0.6% | 4.5% | 7.1% | 0.0% | 84.1% | 3.7% |
| 6 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 437 | **0.0%** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |
| 7 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 466 | 455 | **0.0%** | 0.030 | 66.9% | 33.1% | 0.4% | 4.9% | 8.6% | 0.0% | 83.7% | 2.4% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 468 | 453 | **0.0%** | 0.029 | 66.5% | 33.5% | 0.2% | 5.1% | 7.5% | 0.0% | 84.0% | 3.2% |
| 9 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 466 | 447 | **0.0%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 10 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 467 | 440 | **0.0%** | 0.026 | 64.3% | 35.7% | 0.2% | 4.5% | 7.5% | 0.0% | 82.0% | 5.8% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 466 | 451 | **87.1%** | 0.020 | 68.8% | 31.2% | 0.4% | 3.0% | 6.2% | 0.0% | 87.1% | 3.2% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 468 | 463 | **87.0%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 466 | 450 | **86.9%** | 0.016 | 70.5% | 29.5% | 0.4% | 2.1% | 7.1% | 0.0% | 86.9% | 3.4% |
| 4 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 466 | 452 | **86.7%** | 0.027 | 71.6% | 28.4% | 0.6% | 3.4% | 6.0% | 0.2% | 86.7% | 3.0% |
| 5 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 465 | 453 | **86.7%** | 0.023 | 69.2% | 30.8% | 0.2% | 4.1% | 6.5% | 0.0% | 86.7% | 2.6% |
| 6 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 466 | 457 | **86.5%** | 0.018 | 68.2% | 31.8% | 0.0% | 3.4% | 8.2% | 0.0% | 86.5% | 1.9% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 466 | 457 | **86.1%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 8 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 467 | 459 | **85.9%** | 0.024 | 69.4% | 30.6% | 0.4% | 3.9% | 8.1% | 0.0% | 85.9% | 1.7% |
| 9 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 464 | 446 | **85.8%** | 0.019 | 65.8% | 34.2% | 0.4% | 2.8% | 7.1% | 0.0% | 85.8% | 3.9% |
| 10 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 465 | 448 | **85.6%** | 0.026 | 63.2% | 36.8% | 0.9% | 3.2% | 6.7% | 0.0% | 85.6% | 3.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 467 | 454 | **55.5%** | 0.014 | 40.0% | 60.0% | 0.2% | 2.4% | 39.2% | 0.0% | 55.5% | 2.8% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 468 | 456 | **60.0%** | 0.016 | 41.5% | 58.5% | 0.4% | 2.4% | 34.6% | 0.0% | 60.0% | 2.6% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 467 | 452 | **61.5%** | 0.019 | 44.4% | 55.6% | 0.4% | 2.8% | 32.1% | 0.0% | 61.5% | 3.2% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 468 | 452 | **61.8%** | 0.009 | 44.7% | 55.3% | 0.2% | 1.3% | 33.3% | 0.0% | 61.8% | 3.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 468 | 452 | **65.0%** | 0.024 | 46.2% | 53.8% | 0.4% | 3.8% | 27.4% | 0.0% | 65.0% | 3.4% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 468 | 455 | **65.6%** | 0.019 | 48.1% | 51.9% | 0.2% | 2.8% | 28.4% | 0.2% | 65.6% | 2.8% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 467 | 457 | **67.2%** | 0.011 | 48.3% | 51.7% | 0.0% | 2.1% | 28.5% | 0.0% | 67.2% | 2.1% |
| 8 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 468 | 450 | **70.9%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 468 | 455 | **71.8%** | 0.016 | 50.0% | 50.0% | 0.6% | 1.9% | 22.9% | 0.0% | 71.8% | 2.8% |
| 10 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 468 | 450 | **73.1%** | 0.024 | 51.9% | 48.1% | 0.6% | 3.4% | 19.0% | 0.0% | 73.1% | 3.8% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 466 | 437 | **6.2%** | 0.030 | 62.2% | 37.8% | 0.9% | 3.9% | 8.4% | 0.0% | 80.7% | 6.2% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 467 | 440 | **5.8%** | 0.026 | 64.3% | 35.7% | 0.2% | 4.5% | 7.5% | 0.0% | 82.0% | 5.8% |
| 3 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 468 | 445 | **4.9%** | 0.021 | 65.4% | 34.6% | 0.0% | 4.1% | 8.1% | 0.0% | 82.9% | 4.9% |
| 4 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 465 | 443 | **4.7%** | 0.009 | 58.1% | 41.9% | 0.2% | 0.9% | 16.1% | 0.2% | 77.8% | 4.7% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 466 | 447 | **4.1%** | 0.028 | 69.0% | 31.0% | 0.4% | 4.5% | 6.9% | 0.0% | 84.1% | 4.1% |
| 6 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 467 | 448 | **4.1%** | 0.008 | 50.9% | 49.1% | 0.0% | 1.5% | 19.5% | 0.0% | 74.9% | 4.1% |
| 7 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 464 | 446 | **3.9%** | 0.019 | 65.8% | 34.2% | 0.4% | 2.8% | 7.1% | 0.0% | 85.8% | 3.9% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 468 | 450 | **3.8%** | 0.024 | 51.9% | 48.1% | 0.6% | 3.4% | 19.0% | 0.0% | 73.1% | 3.8% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 468 | 450 | **3.8%** | 0.016 | 52.4% | 47.6% | 0.2% | 1.7% | 22.9% | 0.4% | 70.9% | 3.8% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 464 | 447 | **3.7%** | 0.035 | 68.2% | 31.8% | 0.4% | 5.4% | 7.3% | 0.2% | 83.0% | 3.7% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 464 | 460 | **0.9%** | 0.033 | 67.5% | 32.5% | 0.9% | 4.7% | 8.0% | 0.0% | 85.6% | 0.9% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 468 | 463 | **1.1%** | 0.024 | 70.9% | 29.1% | 0.2% | 4.3% | 7.5% | 0.0% | 87.0% | 1.1% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 466 | 461 | **1.1%** | 0.023 | 66.7% | 33.3% | 0.2% | 4.1% | 10.3% | 0.0% | 84.3% | 1.1% |
| 4 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 468 | 461 | **1.5%** | 0.021 | 58.8% | 41.2% | 1.1% | 1.1% | 13.5% | 0.4% | 82.5% | 1.5% |
| 5 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 468 | 461 | **1.5%** | 0.011 | 59.4% | 40.6% | 0.4% | 0.4% | 15.8% | 0.4% | 81.4% | 1.5% |
| 6 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 467 | 460 | **1.5%** | 0.011 | 56.4% | 43.6% | 0.2% | 1.3% | 14.3% | 0.2% | 82.4% | 1.5% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 467 | 459 | **1.7%** | 0.024 | 69.4% | 30.6% | 0.4% | 3.9% | 8.1% | 0.0% | 85.9% | 1.7% |
| 8 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 468 | 459 | **1.9%** | 0.016 | 62.6% | 37.4% | 1.1% | 1.1% | 10.7% | 0.0% | 85.3% | 1.9% |
| 9 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 466 | 457 | **1.9%** | 0.033 | 67.9% | 32.1% | 0.9% | 4.3% | 6.7% | 0.2% | 86.1% | 1.9% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 466 | 457 | **1.9%** | 0.018 | 68.2% | 31.8% | 0.0% | 3.4% | 8.2% | 0.0% | 86.5% | 1.9% |


#### First-Hand POV (Seats 1-6: Fooled & Gatekeeper)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **0.0237** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0194** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0193** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.0171** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **0.0152** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0151** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 233 | 231 | **0.0130** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 8 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 233 | **0.0129** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 9 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 233 | **0.0129** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 10 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **0.0107** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 234 | 233 | **0.0000** | 0.000 | 85.5% | 14.5% | 0.0% | 0.0% | 17.5% | 0.0% | 82.1% | 0.4% |
| 2 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 233 | 232 | **0.0000** | 0.000 | 94.9% | 5.1% | 0.0% | 0.0% | 6.0% | 0.0% | 93.6% | 0.4% |
| 3 | 15 | close_friend / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0000** | 0.000 | 97.4% | 2.6% | 0.0% | 0.0% | 4.3% | 0.0% | 95.3% | 0.4% |
| 4 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 234 | 233 | **0.0000** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 7.3% | 0.0% | 92.3% | 0.4% |
| 5 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 234 | 234 | **0.0000** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 5.6% | 0.0% | 94.4% | 0.0% |
| 6 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 232 | 231 | **0.0000** | 0.000 | 98.7% | 1.3% | 0.0% | 0.0% | 3.9% | 0.0% | 95.7% | 0.4% |
| 7 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 234 | 231 | **0.0000** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 7.3% | 0.0% | 91.5% | 1.3% |
| 8 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 234 | 232 | **0.0000** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 2.1% | 0.0% | 97.0% | 0.9% |
| 9 | 28 | close_friend / citizen / poor_record / rich / man_old | 39 | 234 | 233 | **0.0000** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 3.0% | 0.0% | 96.6% | 0.4% |
| 10 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 234 | 234 | **0.0000** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 98.3% | 0.0% |


**SKIP Rate (%)** *(Note: 14 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **44.0%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **40.6%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **40.2%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 234 | 233 | **35.5%** | 0.004 | 64.5% | 35.5% | 0.0% | 0.9% | 37.2% | 0.0% | 61.5% | 0.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **32.1%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 6 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 233 | **28.6%** | 0.002 | 71.4% | 28.6% | 0.0% | 0.4% | 28.6% | 0.0% | 70.5% | 0.4% |
| 7 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **26.1%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **21.8%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 233 | **21.8%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **19.2%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 233 | **0.0%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.3% | 0.0% | 97.4% | 0.0% |
| 2 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 234 | 233 | **0.0%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.7% | 0.0% | 96.6% | 0.4% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 234 | 231 | **0.0%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 2.6% | 0.0% | 95.3% | 1.3% |
| 4 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 232 | **0.0%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 0.9% | 0.0% | 97.4% | 0.9% |
| 5 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 234 | 233 | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 4.3% | 0.0% | 94.9% | 0.4% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 234 | 233 | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 232 | 230 | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 97.4% | 0.9% |
| 8 | 2 | close_friend / mayor / good_record / rich / man_young | 39 | 234 | 231 | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.7% | 0.0% | 96.6% | 1.3% |
| 9 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 234 | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 2.1% | 0.0% | 97.4% | 0.0% |
| 10 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 234 | 234 | **0.0%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 98.3% | 0.0% |


**FACT (%)** *(Note: 57 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 233 | 231 | **0.4%** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 2 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.4%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 3 | 25 | close_friend / citizen / poor_record / rich / woman_old | 39 | 234 | 233 | **0.4%** | 0.011 | 96.6% | 3.4% | 0.4% | 1.3% | 4.7% | 0.0% | 93.2% | 0.4% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 232 | **0.4%** | 0.009 | 96.6% | 3.4% | 0.4% | 0.9% | 3.8% | 0.0% | 94.0% | 0.9% |
| 5 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 234 | 233 | **0.4%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 4.3% | 0.0% | 94.9% | 0.4% |
| 6 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 234 | 233 | **0.4%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.4%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 9 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 10 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **0.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 233 | **0.0%** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 7 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 233 | **0.0%** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 8 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **0.0%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 233 | **0.0%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 233 | **0.0%** | 0.011 | 85.9% | 14.1% | 0.0% | 2.1% | 16.7% | 0.0% | 80.8% | 0.4% |


**UNCERTAIN (%)** *(Note: 18 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **4.7%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **3.8%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **3.8%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **3.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 5 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **3.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 6 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **2.6%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 233 | **2.6%** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 233 | **2.6%** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 9 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **2.1%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 233 | **2.1%** | 0.011 | 85.9% | 14.1% | 0.0% | 2.1% | 16.7% | 0.0% | 80.8% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 234 | 233 | **0.0%** | 0.004 | 98.7% | 1.3% | 0.0% | 0.0% | 3.0% | 0.4% | 96.2% | 0.4% |
| 2 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 234 | 233 | **0.0%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.0% | 2.6% | 0.4% | 96.6% | 0.4% |
| 3 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 234 | 233 | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 4.3% | 0.0% | 94.9% | 0.4% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 234 | 233 | **0.0%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 5 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 6 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 234 | 233 | **0.0%** | 0.000 | 85.5% | 14.5% | 0.0% | 0.0% | 17.5% | 0.0% | 82.1% | 0.4% |
| 7 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 233 | 232 | **0.0%** | 0.000 | 94.9% | 5.1% | 0.0% | 0.0% | 6.0% | 0.0% | 93.6% | 0.4% |
| 8 | 15 | close_friend / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0%** | 0.000 | 97.4% | 2.6% | 0.0% | 0.0% | 4.3% | 0.0% | 95.3% | 0.4% |
| 9 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 234 | 233 | **0.0%** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 7.3% | 0.0% | 92.3% | 0.4% |
| 10 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 234 | 234 | **0.0%** | 0.000 | 98.3% | 1.7% | 0.0% | 0.0% | 5.6% | 0.0% | 94.4% | 0.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **42.7%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **37.2%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 3 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 234 | 233 | **37.2%** | 0.004 | 64.5% | 35.5% | 0.0% | 0.9% | 37.2% | 0.0% | 61.5% | 0.4% |
| 4 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **35.9%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 5 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 233 | **28.6%** | 0.002 | 71.4% | 28.6% | 0.0% | 0.4% | 28.6% | 0.0% | 70.5% | 0.4% |
| 6 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **28.2%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 7 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **25.6%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 8 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 233 | **22.2%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **19.7%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 10 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 234 | 233 | **19.7%** | 0.002 | 82.5% | 17.5% | 0.0% | 0.4% | 19.7% | 0.0% | 79.5% | 0.4% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 234 | 233 | **0.4%** | 0.002 | 99.6% | 0.4% | 0.0% | 0.4% | 0.4% | 0.0% | 98.7% | 0.4% |
| 2 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 234 | 232 | **0.9%** | 0.006 | 99.1% | 0.9% | 0.0% | 1.3% | 0.9% | 0.0% | 97.0% | 0.9% |
| 3 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 232 | **0.9%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 0.9% | 0.0% | 97.4% | 0.9% |
| 4 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 234 | 233 | **0.9%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 5 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 234 | **1.3%** | 0.009 | 99.1% | 0.9% | 0.0% | 1.7% | 1.3% | 0.0% | 97.0% | 0.0% |
| 6 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 234 | 234 | **1.3%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.3% | 0.0% | 97.9% | 0.0% |
| 7 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 234 | 234 | **1.3%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 98.3% | 0.0% |
| 8 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 234 | 233 | **1.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.3% | 0.0% | 98.3% | 0.4% |
| 9 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 233 | 232 | **1.3%** | 0.006 | 99.6% | 0.4% | 0.0% | 1.3% | 1.3% | 0.0% | 97.0% | 0.4% |
| 10 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 233 | **1.3%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.3% | 0.0% | 97.4% | 0.0% |


**CHECKED_TRUE (%)** *(Note: 60 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 233 | 231 | **0.4%** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 2 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 233 | **0.4%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 234 | 233 | **0.4%** | 0.004 | 98.7% | 1.3% | 0.0% | 0.0% | 3.0% | 0.4% | 96.2% | 0.4% |
| 4 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 234 | 233 | **0.4%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.0% | 2.6% | 0.4% | 96.6% | 0.4% |
| 5 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 6 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 7 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 8 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 9 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **0.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 10 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **0.0%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 2 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 3 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **0.0%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 4 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 5 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **0.0%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **0.0%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 7 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 234 | 233 | **0.0%** | 0.013 | 83.3% | 16.7% | 0.0% | 2.6% | 15.0% | 0.0% | 82.1% | 0.4% |
| 8 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 234 | 233 | **0.0%** | 0.013 | 99.1% | 0.9% | 0.0% | 2.6% | 1.7% | 0.0% | 95.3% | 0.4% |
| 9 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **0.0%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 10 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 233 | **0.0%** | 0.011 | 85.9% | 14.1% | 0.0% | 2.1% | 16.7% | 0.0% | 80.8% | 0.4% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 234 | 233 | **98.7%** | 0.002 | 99.6% | 0.4% | 0.0% | 0.4% | 0.4% | 0.0% | 98.7% | 0.4% |
| 2 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 234 | 233 | **98.3%** | 0.004 | 100.0% | 0.0% | 0.4% | 0.0% | 0.9% | 0.0% | 98.3% | 0.4% |
| 3 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 234 | 234 | **98.3%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 98.3% | 0.0% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 234 | 234 | **98.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 98.3% | 0.0% |
| 5 | 24 | close_friend / citizen / good_record / poor / man_old | 39 | 234 | 233 | **98.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.3% | 0.0% | 98.3% | 0.4% |
| 6 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 234 | 234 | **98.3%** | 0.000 | 100.0% | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 98.3% | 0.0% |
| 7 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **97.9%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 234 | 234 | **97.9%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.3% | 0.0% | 97.9% | 0.0% |
| 9 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 234 | 234 | **97.9%** | 0.002 | 99.6% | 0.4% | 0.0% | 0.4% | 1.7% | 0.0% | 97.9% | 0.0% |
| 10 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 234 | 232 | **97.4%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 0.9% | 0.0% | 97.4% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 234 | 233 | **54.7%** | 0.011 | 56.0% | 44.0% | 0.0% | 2.1% | 42.7% | 0.0% | 54.7% | 0.4% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **58.5%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 3 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **59.4%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 234 | 233 | **61.5%** | 0.004 | 64.5% | 35.5% | 0.0% | 0.9% | 37.2% | 0.0% | 61.5% | 0.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 233 | **67.5%** | 0.019 | 67.9% | 32.1% | 0.0% | 3.8% | 28.2% | 0.0% | 67.5% | 0.4% |
| 6 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 232 | **70.5%** | 0.015 | 73.9% | 26.1% | 0.0% | 3.0% | 25.6% | 0.0% | 70.5% | 0.9% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 234 | 233 | **70.5%** | 0.002 | 71.4% | 28.6% | 0.0% | 0.4% | 28.6% | 0.0% | 70.5% | 0.4% |
| 8 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **74.8%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 233 | **75.6%** | 0.011 | 78.2% | 21.8% | 0.0% | 1.3% | 22.2% | 0.4% | 75.6% | 0.4% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **79.1%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |


**NOT_MENTIONED (%)** *(Note: 16 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 231 | **1.3%** | 0.015 | 59.4% | 40.6% | 0.0% | 3.0% | 37.2% | 0.0% | 58.5% | 1.3% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 234 | 231 | **1.3%** | 0.009 | 99.6% | 0.4% | 0.0% | 1.7% | 1.7% | 0.0% | 95.3% | 1.3% |
| 3 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 234 | 231 | **1.3%** | 0.004 | 100.0% | 0.0% | 0.0% | 0.9% | 2.6% | 0.0% | 95.3% | 1.3% |
| 4 | 2 | close_friend / mayor / good_record / rich / man_young | 39 | 234 | 231 | **1.3%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.7% | 0.0% | 96.6% | 1.3% |
| 5 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 234 | 231 | **1.3%** | 0.000 | 99.1% | 0.9% | 0.0% | 0.0% | 7.3% | 0.0% | 91.5% | 1.3% |
| 6 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 232 | 230 | **0.9%** | 0.002 | 100.0% | 0.0% | 0.0% | 0.4% | 1.3% | 0.0% | 97.4% | 0.9% |
| 7 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 233 | 231 | **0.9%** | 0.013 | 99.6% | 0.4% | 0.4% | 0.9% | 3.9% | 0.4% | 93.6% | 0.9% |
| 8 | 41 | stranger / mayor / poor_record / rich / woman_old | 39 | 233 | 231 | **0.9%** | 0.006 | 84.6% | 15.4% | 0.0% | 1.3% | 17.2% | 0.0% | 80.7% | 0.9% |
| 9 | 58 | stranger / citizen / poor_record / rich / man_young | 39 | 234 | 232 | **0.9%** | 0.024 | 78.2% | 21.8% | 0.0% | 4.7% | 19.7% | 0.0% | 74.8% | 0.9% |
| 10 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 234 | 232 | **0.9%** | 0.019 | 59.8% | 40.2% | 0.0% | 3.8% | 35.9% | 0.0% | 59.4% | 0.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.017 | 80.8% | 19.2% | 0.4% | 2.6% | 17.9% | 0.0% | 79.1% | 0.0% |
| 2 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 234 | **0.0%** | 0.009 | 99.1% | 0.9% | 0.0% | 1.7% | 1.3% | 0.0% | 97.0% | 0.0% |
| 3 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 233 | 233 | **0.0%** | 0.006 | 100.0% | 0.0% | 0.0% | 1.3% | 1.3% | 0.0% | 97.4% | 0.0% |
| 4 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.006 | 99.6% | 0.4% | 0.0% | 1.3% | 3.8% | 0.0% | 94.9% | 0.0% |
| 5 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 234 | 234 | **0.0%** | 0.004 | 95.7% | 4.3% | 0.0% | 0.9% | 6.4% | 0.0% | 92.7% | 0.0% |
| 6 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 234 | 234 | **0.0%** | 0.004 | 99.1% | 0.9% | 0.4% | 0.0% | 1.7% | 0.0% | 97.9% | 0.0% |
| 7 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 234 | 234 | **0.0%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.7% | 0.0% | 97.4% | 0.0% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 234 | 234 | **0.0%** | 0.004 | 99.6% | 0.4% | 0.0% | 0.9% | 1.3% | 0.0% | 97.9% | 0.0% |
| 9 | 29 | close_friend / citizen / poor_record / poor / woman_old | 39 | 234 | 234 | **0.0%** | 0.002 | 95.3% | 4.7% | 0.0% | 0.4% | 8.1% | 0.0% | 91.5% | 0.0% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 234 | **0.0%** | 0.002 | 98.3% | 1.7% | 0.0% | 0.4% | 4.3% | 0.0% | 95.3% | 0.0% |


#### Second-Hand POV (Seats 7-12: Downstream Susceptibility)

**Belief Score (0-1)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 230 | 215 | **0.0721** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |
| 2 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 231 | 223 | **0.0717** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 3 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 230 | 226 | **0.0664** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 4 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **0.0625** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 5 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 205 | **0.0610** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 6 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 232 | 219 | **0.0594** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 7 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 233 | 220 | **0.0591** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 8 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 234 | 219 | **0.0571** | 0.057 | 34.6% | 65.4% | 0.4% | 9.0% | 14.1% | 0.4% | 69.7% | 6.4% |
| 9 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 232 | 223 | **0.0561** | 0.056 | 35.5% | 64.5% | 0.4% | 9.1% | 16.4% | 0.4% | 69.8% | 3.9% |
| 10 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 231 | 215 | **0.0558** | 0.056 | 33.3% | 66.7% | 1.3% | 7.8% | 12.6% | 0.0% | 71.4% | 6.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 225 | **0.0111** | 0.011 | 26.5% | 73.5% | 0.0% | 1.3% | 20.5% | 0.4% | 73.9% | 3.8% |
| 2 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 233 | 223 | **0.0112** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 3 | 42 | stranger / mayor / poor_record / rich / man_young | 39 | 233 | 223 | **0.0135** | 0.013 | 23.9% | 76.1% | 0.4% | 1.7% | 20.2% | 0.0% | 73.4% | 4.3% |
| 4 | 28 | close_friend / citizen / poor_record / rich / man_old | 39 | 233 | 222 | **0.0135** | 0.014 | 19.2% | 80.8% | 0.4% | 1.7% | 26.2% | 0.0% | 67.0% | 4.7% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 234 | 219 | **0.0137** | 0.014 | 24.8% | 75.2% | 0.4% | 1.7% | 29.5% | 0.0% | 62.0% | 6.4% |
| 6 | 44 | stranger / mayor / poor_record / rich / man_old | 39 | 233 | 219 | **0.0137** | 0.014 | 27.8% | 72.2% | 0.4% | 1.7% | 19.7% | 0.0% | 72.1% | 6.0% |
| 7 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 233 | 215 | **0.0140** | 0.014 | 19.2% | 80.8% | 0.0% | 2.6% | 19.3% | 0.0% | 70.4% | 7.7% |
| 8 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 234 | 224 | **0.0156** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 9 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 221 | **0.0158** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |
| 10 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 233 | 218 | **0.0161** | 0.016 | 20.1% | 79.9% | 0.4% | 0.4% | 24.5% | 0.9% | 67.4% | 6.4% |


**SKIP Rate (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 29 | close_friend / citizen / poor_record / poor / woman_old | 39 | 234 | 220 | **83.8%** | 0.023 | 16.2% | 83.8% | 0.9% | 2.6% | 23.1% | 0.0% | 67.5% | 6.0% |
| 2 | 15 | close_friend / mayor / poor_record / poor / woman_young | 39 | 234 | 221 | **82.9%** | 0.038 | 17.1% | 82.9% | 1.7% | 3.0% | 17.1% | 0.4% | 72.2% | 5.6% |
| 3 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 231 | 212 | **82.9%** | 0.019 | 17.1% | 82.9% | 0.4% | 1.7% | 25.1% | 0.4% | 64.1% | 8.2% |
| 4 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 233 | 223 | **82.5%** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 5 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 234 | 228 | **82.1%** | 0.022 | 17.9% | 82.1% | 0.4% | 2.6% | 22.6% | 0.4% | 71.4% | 2.6% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 234 | 224 | **81.2%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 7 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 227 | **80.8%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 8 | 25 | close_friend / citizen / poor_record / rich / woman_old | 39 | 234 | 224 | **80.8%** | 0.031 | 19.2% | 80.8% | 1.3% | 2.6% | 27.8% | 0.4% | 63.7% | 4.3% |
| 9 | 57 | stranger / citizen / poor_record / rich / woman_old | 39 | 233 | 224 | **80.8%** | 0.018 | 19.2% | 80.8% | 0.4% | 2.6% | 25.8% | 0.0% | 67.4% | 3.9% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 221 | **80.8%** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 232 | 221 | **56.8%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 229 | **58.1%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 3 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 232 | 216 | **59.0%** | 0.032 | 41.0% | 59.0% | 0.9% | 4.3% | 12.5% | 0.0% | 75.4% | 6.9% |
| 4 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 221 | **59.4%** | 0.043 | 40.6% | 59.4% | 0.9% | 6.5% | 12.5% | 0.0% | 75.4% | 4.7% |
| 5 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 233 | 225 | **60.7%** | 0.044 | 39.3% | 60.7% | 0.9% | 6.9% | 14.6% | 0.0% | 74.2% | 3.4% |
| 6 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 231 | 220 | **61.1%** | 0.045 | 38.9% | 61.1% | 0.4% | 7.8% | 10.8% | 0.0% | 76.2% | 4.8% |
| 7 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 213 | **61.5%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |
| 8 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 231 | 223 | **62.4%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 9 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 218 | **62.4%** | 0.037 | 37.6% | 62.4% | 0.4% | 6.0% | 11.6% | 0.0% | 75.9% | 6.0% |
| 10 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 230 | 215 | **62.8%** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |


**FACT (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27 | close_friend / citizen / poor_record / rich / woman_young | 39 | 232 | 220 | **2.6%** | 0.041 | 21.8% | 78.2% | 2.6% | 1.7% | 19.0% | 0.4% | 71.1% | 5.2% |
| 2 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 233 | 220 | **2.6%** | 0.039 | 21.4% | 78.6% | 2.6% | 1.3% | 24.9% | 0.4% | 65.2% | 5.6% |
| 3 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 227 | **2.1%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 230 | 226 | **1.7%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 5 | 56 | stranger / citizen / good_record / poor / man_old | 39 | 231 | 216 | **1.7%** | 0.046 | 27.4% | 72.6% | 1.7% | 5.2% | 12.6% | 0.0% | 74.0% | 6.5% |
| 6 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **1.7%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 7 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 205 | **1.7%** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 8 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 232 | 224 | **1.7%** | 0.051 | 35.9% | 64.1% | 1.7% | 6.5% | 18.1% | 0.0% | 70.3% | 3.4% |
| 9 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 233 | 220 | **1.7%** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 10 | 2 | close_friend / mayor / good_record / rich / man_young | 39 | 233 | 220 | **1.7%** | 0.039 | 35.9% | 64.1% | 1.7% | 3.9% | 18.9% | 0.0% | 70.0% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 234 | 212 | **0.0%** | 0.042 | 31.2% | 68.8% | 0.0% | 7.7% | 15.8% | 0.0% | 67.1% | 9.4% |
| 2 | 22 | close_friend / citizen / good_record / poor / man_young | 39 | 232 | 223 | **0.0%** | 0.034 | 36.3% | 63.7% | 0.0% | 6.5% | 15.1% | 0.0% | 74.6% | 3.9% |
| 3 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 233 | 224 | **0.0%** | 0.020 | 25.2% | 74.8% | 0.0% | 3.9% | 28.3% | 0.0% | 63.9% | 3.9% |
| 4 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 233 | 215 | **0.0%** | 0.014 | 19.2% | 80.8% | 0.0% | 2.6% | 19.3% | 0.0% | 70.4% | 7.7% |
| 5 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 233 | 223 | **0.0%** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 6 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 225 | **0.0%** | 0.011 | 26.5% | 73.5% | 0.0% | 1.3% | 20.5% | 0.4% | 73.9% | 3.8% |
| 7 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 234 | 219 | **0.4%** | 0.057 | 34.6% | 65.4% | 0.4% | 9.0% | 14.1% | 0.4% | 69.7% | 6.4% |
| 8 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 219 | **0.4%** | 0.050 | 33.8% | 66.2% | 0.4% | 8.5% | 13.7% | 0.0% | 70.9% | 6.4% |
| 9 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 229 | **0.4%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 10 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 234 | 217 | **0.4%** | 0.039 | 34.6% | 65.4% | 0.4% | 6.4% | 14.1% | 0.0% | 71.8% | 7.3% |


**UNCERTAIN (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 231 | 223 | **11.3%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 2 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 230 | 215 | **10.9%** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 232 | 219 | **10.3%** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 4 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 230 | 226 | **9.6%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 5 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 232 | 223 | **9.1%** | 0.056 | 35.5% | 64.5% | 0.4% | 9.1% | 16.4% | 0.4% | 69.8% | 3.9% |
| 6 | 21 | close_friend / citizen / good_record / poor / woman_old | 39 | 234 | 219 | **9.0%** | 0.057 | 34.6% | 65.4% | 0.4% | 9.0% | 14.1% | 0.4% | 69.7% | 6.4% |
| 7 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **8.6%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 8 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 233 | 223 | **8.6%** | 0.054 | 34.2% | 65.8% | 0.9% | 8.6% | 15.9% | 0.0% | 70.4% | 4.3% |
| 9 | 33 | stranger / mayor / good_record / rich / woman_old | 39 | 234 | 219 | **8.5%** | 0.050 | 33.8% | 66.2% | 0.4% | 8.5% | 13.7% | 0.0% | 70.9% | 6.4% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 213 | **8.2%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 233 | 218 | **0.4%** | 0.016 | 20.1% | 79.9% | 0.4% | 0.4% | 24.5% | 0.9% | 67.4% | 6.4% |
| 2 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 234 | 227 | **0.9%** | 0.022 | 20.5% | 79.5% | 0.9% | 0.9% | 26.1% | 0.9% | 68.4% | 3.0% |
| 3 | 30 | close_friend / citizen / poor_record / poor / man_young | 39 | 233 | 219 | **0.9%** | 0.023 | 20.1% | 79.9% | 1.7% | 0.9% | 26.2% | 0.0% | 65.2% | 6.0% |
| 4 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 227 | **1.3%** | 0.024 | 28.6% | 71.4% | 1.7% | 1.3% | 17.5% | 0.0% | 76.5% | 3.0% |
| 5 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 221 | **1.3%** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |
| 6 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 234 | 224 | **1.3%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 7 | 43 | stranger / mayor / poor_record / rich / woman_young | 39 | 234 | 225 | **1.3%** | 0.011 | 26.5% | 73.5% | 0.0% | 1.3% | 20.5% | 0.4% | 73.9% | 3.8% |
| 8 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 233 | 220 | **1.3%** | 0.039 | 21.4% | 78.6% | 2.6% | 1.3% | 24.9% | 0.4% | 65.2% | 5.6% |
| 9 | 16 | close_friend / mayor / poor_record / poor / man_old | 39 | 233 | 223 | **1.3%** | 0.011 | 17.5% | 82.5% | 0.0% | 1.3% | 22.3% | 0.4% | 71.7% | 4.3% |
| 10 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 227 | **1.7%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |


**SKEPTICAL (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 233 | 221 | **35.6%** | 0.018 | 23.9% | 76.1% | 0.4% | 2.6% | 35.6% | 0.0% | 56.2% | 5.2% |
| 2 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 225 | **32.1%** | 0.018 | 23.5% | 76.5% | 0.9% | 1.7% | 32.1% | 0.0% | 61.5% | 3.8% |
| 3 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 223 | **31.2%** | 0.022 | 22.2% | 77.8% | 0.4% | 2.6% | 31.2% | 0.4% | 60.7% | 4.7% |
| 4 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 234 | 224 | **30.8%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 5 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 234 | 219 | **29.5%** | 0.014 | 24.8% | 75.2% | 0.4% | 1.7% | 29.5% | 0.0% | 62.0% | 6.4% |
| 6 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 231 | 217 | **28.6%** | 0.018 | 21.8% | 78.2% | 0.4% | 1.7% | 28.6% | 0.4% | 62.8% | 6.1% |
| 7 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 233 | 224 | **28.3%** | 0.020 | 25.2% | 74.8% | 0.0% | 3.9% | 28.3% | 0.0% | 63.9% | 3.9% |
| 8 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 233 | 220 | **28.3%** | 0.018 | 29.1% | 70.9% | 0.9% | 1.7% | 28.3% | 0.0% | 63.5% | 5.6% |
| 9 | 25 | close_friend / citizen / poor_record / rich / woman_old | 39 | 234 | 224 | **27.8%** | 0.031 | 19.2% | 80.8% | 1.3% | 2.6% | 27.8% | 0.4% | 63.7% | 4.3% |
| 10 | 48 | stranger / mayor / poor_record / poor / man_old | 39 | 234 | 221 | **27.8%** | 0.016 | 19.2% | 80.8% | 0.9% | 1.3% | 27.8% | 0.0% | 64.5% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 232 | 221 | **9.5%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 2 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **10.3%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 3 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 232 | 219 | **10.8%** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 231 | 220 | **10.8%** | 0.045 | 38.9% | 61.1% | 0.4% | 7.8% | 10.8% | 0.0% | 76.2% | 4.8% |
| 5 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 232 | 219 | **11.2%** | 0.050 | 34.6% | 65.4% | 0.9% | 7.8% | 11.2% | 0.0% | 74.6% | 5.6% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 233 | 220 | **11.6%** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 218 | **11.6%** | 0.037 | 37.6% | 62.4% | 0.4% | 6.0% | 11.6% | 0.0% | 75.9% | 6.0% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 234 | 226 | **12.0%** | 0.055 | 34.6% | 65.4% | 1.7% | 6.4% | 12.0% | 0.4% | 76.1% | 3.4% |
| 9 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 231 | 223 | **12.1%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 10 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 213 | **12.5%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |


**CHECKED_TRUE (%)** *(Note: 45 of 64 cells are 0.0%)*

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | close_friend / mayor / poor_record / poor / man_young | 39 | 233 | 218 | **0.9%** | 0.016 | 20.1% | 79.9% | 0.4% | 0.4% | 24.5% | 0.9% | 67.4% | 6.4% |
| 2 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 227 | **0.9%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 3 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 234 | 227 | **0.9%** | 0.022 | 20.5% | 79.5% | 0.9% | 0.9% | 26.1% | 0.9% | 68.4% | 3.0% |
| 4 | 23 | close_friend / citizen / good_record / poor / woman_young | 39 | 230 | 215 | **0.4%** | 0.072 | 37.2% | 62.8% | 0.9% | 10.9% | 12.6% | 0.4% | 68.7% | 6.5% |
| 5 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 231 | 212 | **0.4%** | 0.019 | 17.1% | 82.9% | 0.4% | 1.7% | 25.1% | 0.4% | 64.1% | 8.2% |
| 6 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 231 | 217 | **0.4%** | 0.018 | 21.8% | 78.2% | 0.4% | 1.7% | 28.6% | 0.4% | 62.8% | 6.1% |
| 7 | 17 | close_friend / citizen / good_record / rich / woman_old | 39 | 232 | 223 | **0.4%** | 0.056 | 35.5% | 64.5% | 0.4% | 9.1% | 16.4% | 0.4% | 69.8% | 3.9% |
| 8 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 232 | 221 | **0.4%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 9 | 27 | close_friend / citizen / poor_record / rich / woman_young | 39 | 232 | 220 | **0.4%** | 0.041 | 21.8% | 78.2% | 2.6% | 1.7% | 19.0% | 0.4% | 71.1% | 5.2% |
| 10 | 12 | close_friend / mayor / poor_record / rich / man_old | 39 | 233 | 220 | **0.4%** | 0.039 | 21.4% | 78.6% | 2.6% | 1.3% | 24.9% | 0.4% | 65.2% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5 | close_friend / mayor / good_record / poor / woman_old | 39 | 231 | 223 | **0.0%** | 0.072 | 37.6% | 62.4% | 1.3% | 11.3% | 12.1% | 0.0% | 71.9% | 3.5% |
| 2 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 230 | 226 | **0.0%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 3 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **0.0%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 4 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 205 | **0.0%** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 5 | 53 | stranger / citizen / good_record / poor / woman_old | 39 | 232 | 219 | **0.0%** | 0.059 | 31.2% | 68.8% | 0.4% | 10.3% | 10.8% | 0.0% | 72.8% | 5.6% |
| 6 | 50 | stranger / citizen / good_record / rich / man_young | 39 | 233 | 220 | **0.0%** | 0.059 | 30.3% | 69.7% | 1.7% | 7.7% | 11.6% | 0.0% | 73.4% | 5.6% |
| 7 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 231 | 215 | **0.0%** | 0.056 | 33.3% | 66.7% | 1.3% | 7.8% | 12.6% | 0.0% | 71.4% | 6.9% |
| 8 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 213 | **0.0%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |
| 9 | 39 | stranger / mayor / good_record / poor / woman_young | 39 | 233 | 223 | **0.0%** | 0.054 | 34.2% | 65.8% | 0.9% | 8.6% | 15.9% | 0.0% | 70.4% | 4.3% |
| 10 | 18 | close_friend / citizen / good_record / rich / man_young | 39 | 232 | 224 | **0.0%** | 0.051 | 35.9% | 64.1% | 1.7% | 6.5% | 18.1% | 0.0% | 70.3% | 3.4% |


**CHECKED_FALSE (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | close_friend / citizen / good_record / rich / man_old | 39 | 232 | 221 | **78.0%** | 0.050 | 43.2% | 56.8% | 1.3% | 6.0% | 9.5% | 0.4% | 78.0% | 4.7% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 229 | **76.5%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 3 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 227 | **76.5%** | 0.024 | 28.6% | 71.4% | 1.7% | 1.3% | 17.5% | 0.0% | 76.5% | 3.0% |
| 4 | 34 | stranger / mayor / good_record / rich / man_young | 39 | 231 | 220 | **76.2%** | 0.045 | 38.9% | 61.1% | 0.4% | 7.8% | 10.8% | 0.0% | 76.2% | 4.8% |
| 5 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 234 | 226 | **76.1%** | 0.055 | 34.6% | 65.4% | 1.7% | 6.4% | 12.0% | 0.4% | 76.1% | 3.4% |
| 6 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **75.9%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
| 7 | 52 | stranger / citizen / good_record / rich / man_old | 39 | 232 | 218 | **75.9%** | 0.037 | 37.6% | 62.4% | 0.4% | 6.0% | 11.6% | 0.0% | 75.9% | 6.0% |
| 8 | 1 | close_friend / mayor / good_record / rich / woman_old | 39 | 232 | 221 | **75.4%** | 0.043 | 40.6% | 59.4% | 0.9% | 6.5% | 12.5% | 0.0% | 75.4% | 4.7% |
| 9 | 49 | stranger / citizen / good_record / rich / woman_old | 39 | 232 | 216 | **75.4%** | 0.032 | 41.0% | 59.0% | 0.9% | 4.3% | 12.5% | 0.0% | 75.4% | 6.9% |
| 10 | 38 | stranger / mayor / good_record / poor / man_young | 39 | 232 | 219 | **74.6%** | 0.050 | 34.6% | 65.4% | 0.9% | 7.8% | 11.2% | 0.0% | 74.6% | 5.6% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64 | stranger / citizen / poor_record / poor / man_old | 39 | 233 | 221 | **56.2%** | 0.018 | 23.9% | 76.1% | 0.4% | 2.6% | 35.6% | 0.0% | 56.2% | 5.2% |
| 2 | 45 | stranger / mayor / poor_record / poor / woman_old | 39 | 234 | 223 | **60.7%** | 0.022 | 22.2% | 77.8% | 0.4% | 2.6% | 31.2% | 0.4% | 60.7% | 4.7% |
| 3 | 63 | stranger / citizen / poor_record / poor / woman_young | 39 | 234 | 225 | **61.5%** | 0.018 | 23.5% | 76.5% | 0.9% | 1.7% | 32.1% | 0.0% | 61.5% | 3.8% |
| 4 | 62 | stranger / citizen / poor_record / poor / man_young | 39 | 234 | 219 | **62.0%** | 0.014 | 24.8% | 75.2% | 0.4% | 1.7% | 29.5% | 0.0% | 62.0% | 6.4% |
| 5 | 47 | stranger / mayor / poor_record / poor / woman_young | 39 | 234 | 219 | **62.4%** | 0.030 | 24.4% | 75.6% | 0.9% | 3.8% | 26.5% | 0.0% | 62.4% | 6.4% |
| 6 | 13 | close_friend / mayor / poor_record / poor / woman_old | 39 | 231 | 217 | **62.8%** | 0.018 | 21.8% | 78.2% | 0.4% | 1.7% | 28.6% | 0.4% | 62.8% | 6.1% |
| 7 | 32 | close_friend / citizen / poor_record / poor / man_old | 39 | 234 | 224 | **62.8%** | 0.016 | 18.8% | 81.2% | 0.9% | 1.3% | 30.8% | 0.0% | 62.8% | 4.3% |
| 8 | 61 | stranger / citizen / poor_record / poor / woman_old | 39 | 233 | 220 | **63.5%** | 0.018 | 29.1% | 70.9% | 0.9% | 1.7% | 28.3% | 0.0% | 63.5% | 5.6% |
| 9 | 25 | close_friend / citizen / poor_record / rich / woman_old | 39 | 234 | 224 | **63.7%** | 0.031 | 19.2% | 80.8% | 1.3% | 2.6% | 27.8% | 0.4% | 63.7% | 4.3% |
| 10 | 46 | stranger / mayor / poor_record / poor / man_young | 39 | 233 | 224 | **63.9%** | 0.020 | 25.2% | 74.8% | 0.0% | 3.9% | 28.3% | 0.0% | 63.9% | 3.9% |


**NOT_MENTIONED (%)**

*Top 10 Strongest (Highest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 54 | stranger / citizen / good_record / poor / man_young | 39 | 232 | 205 | **11.6%** | 0.061 | 25.2% | 74.8% | 1.7% | 7.3% | 14.2% | 0.0% | 65.1% | 11.6% |
| 2 | 55 | stranger / citizen / good_record / poor / woman_young | 39 | 233 | 209 | **10.3%** | 0.045 | 29.1% | 70.9% | 0.4% | 7.3% | 13.3% | 0.0% | 68.7% | 10.3% |
| 3 | 35 | stranger / mayor / good_record / rich / woman_young | 39 | 234 | 212 | **9.4%** | 0.042 | 31.2% | 68.8% | 0.0% | 7.7% | 15.8% | 0.0% | 67.1% | 9.4% |
| 4 | 9 | close_friend / mayor / poor_record / rich / woman_old | 39 | 231 | 212 | **8.2%** | 0.019 | 17.1% | 82.9% | 0.4% | 1.7% | 25.1% | 0.4% | 64.1% | 8.2% |
| 5 | 51 | stranger / citizen / good_record / rich / woman_young | 39 | 232 | 213 | **8.2%** | 0.054 | 38.5% | 61.5% | 0.9% | 8.2% | 12.5% | 0.0% | 70.3% | 8.2% |
| 6 | 40 | stranger / mayor / good_record / poor / man_old | 39 | 230 | 212 | **7.8%** | 0.038 | 32.1% | 67.9% | 0.9% | 5.2% | 12.6% | 0.0% | 73.5% | 7.8% |
| 7 | 59 | stranger / citizen / poor_record / rich / woman_young | 39 | 233 | 215 | **7.7%** | 0.014 | 19.2% | 80.8% | 0.0% | 2.6% | 19.3% | 0.0% | 70.4% | 7.7% |
| 8 | 19 | close_friend / citizen / good_record / rich / woman_young | 39 | 234 | 217 | **7.3%** | 0.039 | 34.6% | 65.4% | 0.4% | 6.4% | 14.1% | 0.0% | 71.8% | 7.3% |
| 9 | 60 | stranger / citizen / poor_record / rich / man_old | 39 | 234 | 217 | **7.3%** | 0.021 | 26.5% | 73.5% | 0.4% | 2.1% | 23.5% | 0.4% | 66.2% | 7.3% |
| 10 | 37 | stranger / mayor / good_record / poor / woman_old | 39 | 231 | 215 | **6.9%** | 0.056 | 33.3% | 66.7% | 1.3% | 7.8% | 12.6% | 0.0% | 71.4% | 6.9% |

*Bottom 10 Weakest (Lowest):*

| Rank | Cell | DNA (Closeness / Authority / Reliability / Wealth / Identity) | Towns | Valid N | Ment. N | Target | Belief | GO % | SKIP % | FACT % | UNCERTAIN % | SKEPTICAL % | CHECKED_TRUE % | CHECKED_FALSE % | NOT_MENTIONED % |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | close_friend / mayor / good_record / rich / woman_young | 39 | 230 | 226 | **1.7%** | 0.066 | 35.0% | 65.0% | 1.7% | 9.6% | 14.3% | 0.0% | 72.6% | 1.7% |
| 2 | 7 | close_friend / mayor / good_record / poor / woman_young | 39 | 234 | 229 | **2.1%** | 0.046 | 41.9% | 58.1% | 0.4% | 8.1% | 12.8% | 0.0% | 76.5% | 2.1% |
| 3 | 8 | close_friend / mayor / good_record / poor / man_old | 39 | 232 | 227 | **2.2%** | 0.040 | 33.8% | 66.2% | 0.4% | 6.9% | 16.8% | 0.0% | 73.7% | 2.2% |
| 4 | 31 | close_friend / citizen / poor_record / poor / woman_young | 39 | 234 | 228 | **2.6%** | 0.022 | 17.9% | 82.1% | 0.4% | 2.6% | 22.6% | 0.4% | 71.4% | 2.6% |
| 5 | 10 | close_friend / mayor / poor_record / rich / man_young | 39 | 234 | 227 | **3.0%** | 0.040 | 19.2% | 80.8% | 2.1% | 1.7% | 22.6% | 0.9% | 69.7% | 3.0% |
| 6 | 11 | close_friend / mayor / poor_record / rich / woman_young | 39 | 234 | 227 | **3.0%** | 0.024 | 28.6% | 71.4% | 1.7% | 1.3% | 17.5% | 0.0% | 76.5% | 3.0% |
| 7 | 26 | close_friend / citizen / poor_record / rich / man_young | 39 | 234 | 227 | **3.0%** | 0.022 | 20.5% | 79.5% | 0.9% | 0.9% | 26.1% | 0.9% | 68.4% | 3.0% |
| 8 | 36 | stranger / mayor / good_record / rich / man_old | 39 | 234 | 226 | **3.4%** | 0.055 | 34.6% | 65.4% | 1.7% | 6.4% | 12.0% | 0.4% | 76.1% | 3.4% |
| 9 | 6 | close_friend / mayor / good_record / poor / man_young | 39 | 233 | 225 | **3.4%** | 0.044 | 39.3% | 60.7% | 0.9% | 6.9% | 14.6% | 0.0% | 74.2% | 3.4% |
| 10 | 4 | close_friend / mayor / good_record / rich / man_old | 39 | 232 | 224 | **3.4%** | 0.062 | 37.2% | 62.8% | 1.7% | 8.6% | 10.3% | 0.0% | 75.9% | 3.4% |
