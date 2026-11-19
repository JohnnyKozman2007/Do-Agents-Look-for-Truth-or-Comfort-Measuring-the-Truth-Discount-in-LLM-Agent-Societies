# Targeted human audit of Gemini labels

Labeled items: 360; scored (valid Gemini label, no dispute): 310; disputed between raters: 27.

Weighted figures use stratum population / stratum sample size, so they estimate the full 119,808-call population. Raw figures over-represent rare strata and are NOT population estimates.

## Overall

- Raw agreement 0.642, raw kappa 0.571
- Population-weighted agreement 0.750, weighted kappa 0.669 (95% CI 0.582, 0.749); target 0.85

- Inter-rater (double-labeled, 72 pairs): kappa 0.539, agreement 0.625

## By stratum

| group | n | raw agreement | 95% CI | weighted agreement |
|---|---|---|---|---|
| CHECKED_FALSE | 38 | 0.816 | 0.666-0.908 | 0.816 |
| CHECKED_TRUE | 40 | 0.750 | 0.598-0.858 | 0.750 |
| FACT | 45 | 0.667 | 0.521-0.786 | 0.667 |
| NOT_MENTIONED_JUDGE | 54 | 0.481 | 0.354-0.611 | 0.481 |
| NOT_MENTIONED_RULE | 20 | 0.350 | 0.181-0.567 | 0.350 |
| SKEPTICAL | 37 | 0.730 | 0.570-0.846 | 0.730 |
| UNCERTAIN | 73 | 0.616 | 0.502-0.719 | 0.616 |
| UNPARSED_OR_RETRIED | 3 | 1.000 | 0.438-1.000 | 1.000 |

## By agent model

| group | n | raw agreement | 95% CI | weighted agreement |
|---|---|---|---|---|
| deepseek_v4_flash | 148 | 0.662 | 0.583-0.733 | 0.757 |
| qwen_3_8_flash | 162 | 0.623 | 0.547-0.694 | 0.742 |

## By layer

| group | n | raw agreement | 95% CI | weighted agreement |
|---|---|---|---|---|
| first_hand | 155 | 0.671 | 0.594-0.740 | 0.723 |
| second_hand | 155 | 0.613 | 0.534-0.686 | 0.775 |

## By condition

| group | n | raw agreement | 95% CI | weighted agreement |
|---|---|---|---|---|
| rumor | 159 | 0.566 | 0.488-0.641 | 0.636 |
| truth_twin | 151 | 0.722 | 0.646-0.787 | 0.862 |

## By Gemini label

| group | n | raw agreement | 95% CI | weighted agreement |
|---|---|---|---|---|
| CHECKED_FALSE | 39 | 0.821 | 0.673-0.910 | 0.816 |
| CHECKED_TRUE | 41 | 0.756 | 0.607-0.862 | 0.750 |
| FACT | 45 | 0.667 | 0.521-0.786 | 0.667 |
| NOT_MENTIONED | 74 | 0.446 | 0.338-0.559 | 0.444 |
| SKEPTICAL | 38 | 0.737 | 0.580-0.850 | 0.730 |
| UNCERTAIN | 73 | 0.616 | 0.502-0.719 | 0.616 |

## By flag

| group | n | raw agreement | 95% CI | weighted agreement |
|---|---|---|---|---|
| checked_false_no_other_artist | 23 | 0.783 | 0.581-0.903 | 0.783 |
| fact_mentions_poster | 24 | 0.500 | 0.314-0.686 | 0.500 |
| only_other_artist | 26 | 0.308 | 0.165-0.500 | 0.645 |
| retried | 3 | 1.000 | 0.438-1.000 | 1.000 |

## Gemini precision / recall per label (weighted, human as reference)

| label | precision | recall |
|---|---|---|
| FACT | 0.667 | 0.243 |
| UNCERTAIN | 0.616 | 0.368 |
| SKEPTICAL | 0.730 | 0.710 |
| CHECKED_TRUE | 0.750 | 0.941 |
| CHECKED_FALSE | 0.816 | 0.945 |
| NOT_MENTIONED | 0.444 | 0.365 |

## Disagreements (Gemini -> human, raw counts)

- NOT_MENTIONED -> SKEPTICAL: 17
- UNCERTAIN -> SKEPTICAL: 14
- UNCERTAIN -> FACT: 9
- NOT_MENTIONED -> CHECKED_FALSE: 8
- NOT_MENTIONED -> FACT: 7
- NOT_MENTIONED -> UNCERTAIN: 7
- FACT -> CHECKED_TRUE: 5
- SKEPTICAL -> UNCERTAIN: 5
- CHECKED_TRUE -> FACT: 5
- CHECKED_TRUE -> UNCERTAIN: 4
- FACT -> SKEPTICAL: 4
- CHECKED_FALSE -> SKEPTICAL: 4
- UNCERTAIN -> CHECKED_TRUE: 3
- FACT -> NOT_MENTIONED: 2
- SKEPTICAL -> FACT: 2
- UNCERTAIN -> CHECKED_FALSE: 2
- SKEPTICAL -> CHECKED_FALSE: 2
- CHECKED_FALSE -> UNCERTAIN: 2
- FACT -> CHECKED_FALSE: 2
- FACT -> UNCERTAIN: 2
- NOT_MENTIONED -> CHECKED_TRUE: 2
- SKEPTICAL -> NOT_MENTIONED: 1
- CHECKED_FALSE -> CHECKED_TRUE: 1
- CHECKED_TRUE -> NOT_MENTIONED: 1

## Coverage audit (calls with no valid Gemini label)

n = 23; human labels: {'CHECKED_TRUE': 8, 'UNCERTAIN': 1, 'CHECKED_FALSE': 8, 'SKEPTICAL': 4, 'FACT': 2}
