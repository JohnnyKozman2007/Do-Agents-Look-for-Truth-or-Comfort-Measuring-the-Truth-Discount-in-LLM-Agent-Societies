# Mini study: first-hand check rate

Model under test: **Claude Sonnet 5.5**. Answered 576 of 576 prompts; malformed (counted as SKIP, as in the main study): 0.

Main-study models are shown on the same prompts (share of their saved runs that chose GO). 95% CIs are bootstrap over listener personas.


## Overall P(GO)

| group | n | Claude Sonnet 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| all | 576 | 20.5% [15.1%, 26.2%] | 47.3% [35.2%, 59.2%] | 91.6% [87.4%, 95.3%] |

## P(GO) by reliability x closeness

| group | n | Claude Sonnet 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| good record, close friend | 144 | 13.2% [6.0%, 20.9%] | 76.4% [60.9%, 91.1%] | 99.8% [99.3%, 100.0%] |
| good record, stranger | 144 | 2.8% [0.7%, 5.0%] | 70.6% [50.2%, 87.0%] | 100.0% [100.0%, 100.0%] |
| poor record, close friend | 144 | 48.6% [36.5%, 60.7%] | 30.8% [17.4%, 43.7%] | 95.8% [90.5%, 99.5%] |
| poor record, stranger | 144 | 17.4% [9.3%, 26.0%] | 11.3% [4.5%, 19.9%] | 70.8% [59.0%, 82.4%] |

## Cue effects (P(GO) difference, first level minus second)

| cue | Claude Sonnet 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|
| closeness: close_friend vs stranger | +20.8 pp [+15.0, +26.8] | +12.6 pp [+4.2, +21.1] | +12.4 pp [+7.9, +16.7] |
| authority: mayor vs citizen | -2.1 pp [-6.6, +2.7] | -5.2 pp [-10.9, +0.2] | +1.7 pp [-1.3, +4.7] |
| reliability: good_record vs poor_record | -25.0 pp [-34.4, -17.0] | +52.4 pp [+41.8, +63.0] | +16.6 pp [+9.1, +25.0] |
| wealth: rich vs poor | +5.6 pp [+0.7, +11.3] | +2.7 pp [-2.7, +8.2] | +5.0 pp [+2.6, +7.1] |
| gender: woman vs man | -3.5 pp [-9.9, +2.5] | +2.4 pp [-2.1, +6.7] | -0.8 pp [-4.0, +2.7] |
| age: old vs young | +12.5 pp [+7.3, +17.1] | +8.0 pp [+1.9, +13.8] | -0.8 pp [-4.4, +2.4] |

Closeness x reliability (point estimates): Claude Sonnet 5.5: closeness effect +31.2 pp with a poor record vs +10.4 pp with a good record; deepseek_v4_flash: closeness effect +19.4 pp with a poor record vs +5.8 pp with a good record; qwen_3_8_flash: closeness effect +25.0 pp with a poor record vs -0.2 pp with a good record


## P(GO) by listener persona

| group | n | Claude Sonnet 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| persona 1 | 40 | 27.5% [27.5%, 27.5%] | 70.8% [70.8%, 70.8%] | 95.8% [95.8%, 95.8%] |
| persona 2 | 40 | 22.5% [22.5%, 22.5%] | 33.3% [33.3%, 33.3%] | 86.7% [86.7%, 86.7%] |
| persona 3 | 40 | 20.0% [20.0%, 20.0%] | 55.0% [55.0%, 55.0%] | 99.2% [99.2%, 99.2%] |
| persona 4 | 40 | 5.0% [5.0%, 5.0%] | 38.3% [38.3%, 38.3%] | 90.0% [90.0%, 90.0%] |
| persona 5 | 40 | 12.5% [12.5%, 12.5%] | 60.8% [60.8%, 60.8%] | 97.5% [97.5%, 97.5%] |
| persona 6 | 40 | 5.0% [5.0%, 5.0%] | 26.7% [26.7%, 26.7%] | 96.7% [96.7%, 96.7%] |
| persona 7 | 48 | 18.8% [18.8%, 18.8%] | 5.6% [5.6%, 5.6%] | 75.0% [75.0%, 75.0%] |
| persona 8 | 40 | 20.0% [20.0%, 20.0%] | 50.8% [50.8%, 50.8%] | 99.2% [99.2%, 99.2%] |
| persona 9 | 48 | 10.4% [10.4%, 10.4%] | 12.5% [12.5%, 12.5%] | 81.3% [81.3%, 81.3%] |
| persona 10 | 48 | 43.8% [43.8%, 43.8%] | 52.1% [52.1%, 52.1%] | 95.8% [95.8%, 95.8%] |
| persona 11 | 48 | 33.3% [33.3%, 33.3%] | 63.2% [63.2%, 63.2%] | 88.2% [88.2%, 88.2%] |
| persona 12 | 56 | 19.6% [19.6%, 19.6%] | 75.0% [75.0%, 75.0%] | 93.5% [93.5%, 93.5%] |
| persona 13 | 48 | 22.9% [22.9%, 22.9%] | 66.7% [66.7%, 66.7%] | 95.8% [95.8%, 95.8%] |

## Run diagnostics

- Answers: 576; finish reasons: {'end_turn': 576}
- Malformed (no GO/SKIP found): 0; answers containing both GO and SKIP: 0
- Tokens: prompt 475,576, completion 146,968 (of which reasoning 0)
- Example raw answers: ['SKIP', 'SKIP', 'SKIP', 'SKIP', 'SKIP']

## Caveats

- Main-study models answered at T=0 with a 5-token cap. If the new model ran with other settings (reasoning, higher cap), say so when comparing.
- The design covers 32 (or 4) of 64 cells and 3 layouts per cell, one twin, no repetitions. Main-study numbers above are restricted to the same prompts, not the full study.
- Second-hand checking and belief (truth discount) are not measured here.
