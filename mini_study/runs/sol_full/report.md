# Mini study: first-hand check rate

Model under test: **GPT-6.1 Sol**. Answered 576 of 576 prompts; malformed (counted as SKIP, as in the main study): 0.

Main-study models are shown on the same prompts (share of their saved runs that chose GO). 95% CIs are bootstrap over listener personas.


## Overall P(GO)

| group | n | GPT-6.1 Sol | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| all | 576 | 4.2% [2.3%, 6.1%] | 47.3% [35.4%, 59.1%] | 91.6% [87.6%, 95.2%] |

## P(GO) by reliability x closeness

| group | n | GPT-6.1 Sol | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| good record, close friend | 144 | 2.8% [0.0%, 6.1%] | 76.4% [61.7%, 90.8%] | 99.8% [99.3%, 100.0%] |
| good record, stranger | 144 | 4.2% [1.9%, 6.9%] | 70.6% [50.9%, 87.4%] | 100.0% [100.0%, 100.0%] |
| poor record, close friend | 144 | 9.0% [4.9%, 13.2%] | 30.8% [16.9%, 43.3%] | 95.8% [90.4%, 99.5%] |
| poor record, stranger | 144 | 0.7% [0.0%, 2.2%] | 11.3% [4.5%, 19.9%] | 70.8% [59.2%, 81.9%] |

## Cue effects (P(GO) difference, first level minus second)

| cue | GPT-6.1 Sol | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|
| closeness: close_friend vs stranger | +3.5 pp [+1.1, +6.4] | +12.6 pp [+4.0, +20.8] | +12.4 pp [+8.0, +16.7] |
| authority: mayor vs citizen | +4.9 pp [+1.1, +8.7] | -5.2 pp [-10.9, -0.2] | +1.7 pp [-1.2, +4.7] |
| reliability: good_record vs poor_record | -1.4 pp [-3.7, +1.4] | +52.4 pp [+42.6, +63.0] | +16.6 pp [+9.3, +24.8] |
| wealth: rich vs poor | -0.7 pp [-3.3, +1.7] | +2.7 pp [-2.8, +8.2] | +5.0 pp [+2.6, +7.2] |
| gender: woman vs man | +0.0 pp [-3.7, +4.0] | +2.4 pp [-2.1, +6.8] | -0.8 pp [-4.1, +2.5] |
| age: old vs young | +0.7 pp [-2.2, +4.0] | +8.0 pp [+2.0, +13.8] | -0.8 pp [-4.5, +2.5] |

Closeness x reliability (point estimates): GPT-6.1 Sol: closeness effect +8.3 pp with a poor record vs -1.4 pp with a good record; deepseek_v4_flash: closeness effect +19.4 pp with a poor record vs +5.8 pp with a good record; qwen_3_8_flash: closeness effect +25.0 pp with a poor record vs -0.2 pp with a good record


## P(GO) by listener persona

| group | n | GPT-6.1 Sol | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| persona 1 | 40 | 0.0% [0.0%, 0.0%] | 70.8% [70.8%, 70.8%] | 95.8% [95.8%, 95.8%] |
| persona 2 | 40 | 5.0% [5.0%, 5.0%] | 33.3% [33.3%, 33.3%] | 86.7% [86.7%, 86.7%] |
| persona 3 | 40 | 5.0% [5.0%, 5.0%] | 55.0% [55.0%, 55.0%] | 99.2% [99.2%, 99.2%] |
| persona 4 | 40 | 10.0% [10.0%, 10.0%] | 38.3% [38.3%, 38.3%] | 90.0% [90.0%, 90.0%] |
| persona 5 | 40 | 10.0% [10.0%, 10.0%] | 60.8% [60.8%, 60.8%] | 97.5% [97.5%, 97.5%] |
| persona 6 | 40 | 0.0% [0.0%, 0.0%] | 26.7% [26.7%, 26.7%] | 96.7% [96.7%, 96.7%] |
| persona 7 | 48 | 2.1% [2.1%, 2.1%] | 5.6% [5.6%, 5.6%] | 75.0% [75.0%, 75.0%] |
| persona 8 | 40 | 5.0% [5.0%, 5.0%] | 50.8% [50.8%, 50.8%] | 99.2% [99.2%, 99.2%] |
| persona 9 | 48 | 0.0% [0.0%, 0.0%] | 12.5% [12.5%, 12.5%] | 81.3% [81.3%, 81.3%] |
| persona 10 | 48 | 4.2% [4.2%, 4.2%] | 52.1% [52.1%, 52.1%] | 95.8% [95.8%, 95.8%] |
| persona 11 | 48 | 0.0% [0.0%, 0.0%] | 63.2% [63.2%, 63.2%] | 88.2% [88.2%, 88.2%] |
| persona 12 | 56 | 7.1% [7.1%, 7.1%] | 75.0% [75.0%, 75.0%] | 93.5% [93.5%, 93.5%] |
| persona 13 | 48 | 6.2% [6.2%, 6.2%] | 66.7% [66.7%, 66.7%] | 95.8% [95.8%, 95.8%] |

## Run diagnostics

- Answers: 576; finish reasons: {'stop': 576}
- Malformed (no GO/SKIP found): 0; answers containing both GO and SKIP: 0
- Tokens: prompt 327,160, completion 29,856 (of which reasoning 23,556)
- Example raw answers: ['SKIP', 'SKIP', 'SKIP', 'SKIP', 'SKIP']

## Caveats

- Main-study models answered at T=0 with a 5-token cap. If the new model ran with other settings (reasoning, higher cap), say so when comparing.
- The design covers 32 (or 4) of 64 cells and 3 layouts per cell, one twin, no repetitions. Main-study numbers above are restricted to the same prompts, not the full study.
- Second-hand checking and belief (truth discount) are not measured here.
