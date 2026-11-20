# Mini study: all models on the same 576 prompts

## Overall P(GO)

| group | GPT-6.1 Terra | Claude Sonnet 5.5 | GPT-6.1 Sol | GPT-6 Luna | Claude Opus 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|---|---|---|
| all | 65% | 20% | 4% | 99% | 18% | 47% | 92% |

## P(GO) by reliability x closeness

| group | GPT-6.1 Terra | Claude Sonnet 5.5 | GPT-6.1 Sol | GPT-6 Luna | Claude Opus 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|---|---|---|
| good record, close friend | 69% | 13% | 3% | 99% | 18% | 76% | 100% |
| good record, stranger | 41% | 3% | 4% | 99% | 8% | 71% | 100% |
| poor record, close friend | 92% | 49% | 9% | 100% | 29% | 31% | 96% |
| poor record, stranger | 59% | 17% | 1% | 99% | 17% | 11% | 71% |

## Cue effects (percentage points, first level minus second)

| group | GPT-6.1 Terra | Claude Sonnet 5.5 | GPT-6.1 Sol | GPT-6 Luna | Claude Opus 5.5 | deepseek_v4_flash | qwen_3_8_flash |
|---|---|---|---|---|---|---|---|
| age: old - young | -4 | +12 | +1 | +0 | +9 | +8 | -1 |
| authority: mayor - citizen | -5 | -2 | +5 | -1 | -1 | -5 | +2 |
| closeness: close_friend - stranger | +31 | +21 | +3 | +0 | +11 | +13 | +12 |
| gender: woman - man | +12 | -3 | +0 | -0 | +1 | +2 | -1 |
| reliability: good_record - poor_record | -20 | -25 | -1 | -0 | -10 | +52 | +17 |
| wealth: rich - poor | +5 | +6 | -1 | -1 | +8 | +3 | +5 |

## Share of identical decisions between models

| index | GPT-6.1 Terra | Claude Sonnet 5.5 | GPT-6.1 Sol | GPT-6 Luna | Claude Opus 5.5 |
|---|---|---|---|---|---|
| GPT-6.1 Terra | 100% | 48% | 37% | 65% | 44% |
| Claude Sonnet 5.5 | 48% | 100% | 78% | 21% | 78% |
| GPT-6.1 Sol | 37% | 78% | 100% | 5% | 80% |
| GPT-6 Luna | 65% | 21% | 5% | 100% | 19% |
| Claude Opus 5.5 | 44% | 78% | 80% | 19% | 100% |
