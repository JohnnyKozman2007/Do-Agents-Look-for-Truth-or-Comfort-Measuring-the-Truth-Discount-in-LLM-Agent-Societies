# Mini study: first-hand check rate

Model under test: **GPT-6.1 Terra**. Answered 576 of 576 prompts; malformed (counted as SKIP, as in the main study): 0.

Main-study models are shown on the same prompts (share of their saved runs that chose GO). 95% CIs are bootstrap over listener personas.


## Overall P(GO)

| group | n | GPT-6.1 Terra | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| all | 576 | 65.5% [59.4%, 71.7%] | 47.3% [35.2%, 59.2%] | 91.6% [87.4%, 95.3%] |

## P(GO) by reliability x closeness

| group | n | GPT-6.1 Terra | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| good record, close friend | 144 | 69.4% [59.2%, 79.3%] | 76.4% [60.9%, 91.1%] | 99.8% [99.3%, 100.0%] |
| good record, stranger | 144 | 41.0% [32.6%, 50.7%] | 70.6% [50.2%, 87.0%] | 100.0% [100.0%, 100.0%] |
| poor record, close friend | 144 | 92.4% [88.7%, 95.9%] | 30.8% [17.4%, 43.7%] | 95.8% [90.5%, 99.5%] |
| poor record, stranger | 144 | 59.0% [47.9%, 69.7%] | 11.3% [4.5%, 19.9%] | 70.8% [59.0%, 82.4%] |

## Cue effects (P(GO) difference, first level minus second)

| cue | GPT-6.1 Terra | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|
| closeness: close_friend vs stranger | +30.9 pp [+23.3, +39.3] | +12.6 pp [+4.2, +21.1] | +12.4 pp [+7.9, +16.7] |
| authority: mayor vs citizen | -4.5 pp [-8.9, +0.7] | -5.2 pp [-10.9, +0.2] | +1.7 pp [-1.3, +4.7] |
| reliability: good_record vs poor_record | -20.5 pp [-28.5, -12.9] | +52.4 pp [+41.8, +63.0] | +16.6 pp [+9.1, +25.0] |
| wealth: rich vs poor | +4.5 pp [-0.7, +9.9] | +2.7 pp [-2.7, +8.2] | +5.0 pp [+2.6, +7.1] |
| gender: woman vs man | +12.2 pp [+5.7, +18.9] | +2.4 pp [-2.1, +6.7] | -0.8 pp [-4.0, +2.7] |
| age: old vs young | -3.8 pp [-11.2, +4.8] | +8.0 pp [+1.9, +13.8] | -0.8 pp [-4.4, +2.4] |

Closeness x reliability (point estimates): GPT-6.1 Terra: closeness effect +33.3 pp with a poor record vs +28.5 pp with a good record; deepseek_v4_flash: closeness effect +19.4 pp with a poor record vs +5.8 pp with a good record; qwen_3_8_flash: closeness effect +25.0 pp with a poor record vs -0.2 pp with a good record


## P(GO) by listener persona

| group | n | GPT-6.1 Terra | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|
| persona 1 | 40 | 57.5% [57.5%, 57.5%] | 70.8% [70.8%, 70.8%] | 95.8% [95.8%, 95.8%] |
| persona 2 | 40 | 75.0% [75.0%, 75.0%] | 33.3% [33.3%, 33.3%] | 86.7% [86.7%, 86.7%] |
| persona 3 | 40 | 47.5% [47.5%, 47.5%] | 55.0% [55.0%, 55.0%] | 99.2% [99.2%, 99.2%] |
| persona 4 | 40 | 60.0% [60.0%, 60.0%] | 38.3% [38.3%, 38.3%] | 90.0% [90.0%, 90.0%] |
| persona 5 | 40 | 60.0% [60.0%, 60.0%] | 60.8% [60.8%, 60.8%] | 97.5% [97.5%, 97.5%] |
| persona 6 | 40 | 62.5% [62.5%, 62.5%] | 26.7% [26.7%, 26.7%] | 96.7% [96.7%, 96.7%] |
| persona 7 | 48 | 79.2% [79.2%, 79.2%] | 5.6% [5.6%, 5.6%] | 75.0% [75.0%, 75.0%] |
| persona 8 | 40 | 60.0% [60.0%, 60.0%] | 50.8% [50.8%, 50.8%] | 99.2% [99.2%, 99.2%] |
| persona 9 | 48 | 83.3% [83.3%, 83.3%] | 12.5% [12.5%, 12.5%] | 81.3% [81.3%, 81.3%] |
| persona 10 | 48 | 85.4% [85.4%, 85.4%] | 52.1% [52.1%, 52.1%] | 95.8% [95.8%, 95.8%] |
| persona 11 | 48 | 60.4% [60.4%, 60.4%] | 63.2% [63.2%, 63.2%] | 88.2% [88.2%, 88.2%] |
| persona 12 | 56 | 58.9% [58.9%, 58.9%] | 75.0% [75.0%, 75.0%] | 93.5% [93.5%, 93.5%] |
| persona 13 | 48 | 56.2% [56.2%, 56.2%] | 66.7% [66.7%, 66.7%] | 95.8% [95.8%, 95.8%] |

## Run diagnostics

- Answers: 576; finish reasons: {'stop': 576}
- Malformed (no GO/SKIP found): 0; answers containing both GO and SKIP: 0
- Tokens: prompt 327,160, completion 56,822 (of which reasoning 50,863)
- Example raw answers: ['GO', 'SKIP', 'SKIP', 'SKIP', 'SKIP']
- Estimated cost at $1.0/M input, $5.0/M output: $0.61

## Caveats

- Main-study models answered at T=0 with a 5-token cap. If the new model ran with other settings (reasoning, higher cap), say so when comparing.
- The design covers 32 (or 4) of 64 cells and 3 layouts per cell, one twin, no repetitions. Main-study numbers above are restricted to the same prompts, not the full study.
- Second-hand checking and belief (truth discount) are not measured here.
