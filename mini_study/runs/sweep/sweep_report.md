# Checking-price sweep

Same 576 first-hand prompts per model at each bus fare (budget stays $40). 95% CIs bootstrap over the 13 listener personas.

## P(GO) by fare

| model | free | $1 | $5 | $15 | $35 |
|---|---|---|---|---|---|
| GPT-6.1 Terra | 100% | 100% | 65% | 3% | 0% |
| GPT-6.1 Sol | 100% | 100% | 4% | 0% | 0% |
| GPT-6 Luna | 100% | 100% | 99% | 68% | 25% |
| Claude Sonnet 5.5 | 100% | 99% | 20% | 0% | 0% |
| Claude Opus 5.5 | 97% | 99% | 18% | 0% | 0% |

## Reliability effect by fare (P(GO) good_record minus poor_record, percentage points)

| model | free | $1 | $5 | $15 | $35 |
|---|---|---|---|---|---|
| GPT-6.1 Terra | +0 [+0, +0] | +0 [+0, +0] | -20 [-28, -12] | -6 [-8, -4] | -0 [-1, +0] |
| GPT-6.1 Sol | +0 [+0, +0] | +0 [+0, +0] | -1 [-4, +1] | +0 [+0, +0] | +0 [+0, +0] |
| GPT-6 Luna | +0 [+0, +0] | +0 [+0, +0] | -0 [-2, +1] | -2 [-11, +5] | +3 [-6, +12] |
| Claude Sonnet 5.5 | -1 [-2, +0] | -1 [-3, -0] | -25 [-34, -17] | +0 [+0, +0] | +0 [+0, +0] |
| Claude Opus 5.5 | -0 [-2, +1] | -1 [-2, +0] | -10 [-14, -7] | +0 [+0, +0] | +0 [+0, +0] |

## Closeness effect by fare (P(GO) close_friend minus stranger, percentage points)

| model | free | $1 | $5 | $15 | $35 |
|---|---|---|---|---|---|
| GPT-6.1 Terra | +0 [+0, +0] | +0 [+0, +0] | +31 [+24, +39] | +7 [+5, +9] | +0 [+0, +1] |
| GPT-6.1 Sol | +0 [+0, +0] | +0 [+0, +0] | +3 [+1, +6] | +0 [+0, +0] | +0 [+0, +0] |
| GPT-6 Luna | +0 [+0, +0] | +0 [+0, +0] | +0 [+0, +1] | +3 [-4, +9] | +3 [-4, +11] |
| Claude Sonnet 5.5 | +0 [+0, +0] | +0 [-1, +1] | +21 [+15, +27] | +0 [+0, +0] | +0 [+0, +0] |
| Claude Opus 5.5 | +4 [-1, +10] | +0 [-1, +2] | +11 [+6, +16] | +0 [+0, +0] | +0 [+0, +0] |

## Half price (fare at which half of listeners still check)

From a logistic fit of GO on log(1 + fare); 'n/a' when checking never crosses 50% or does not fall with price.

| model | half price | 95% CI | P(GO) free | P(GO) $35 |
|---|---|---|---|---|
| GPT-6.1 Terra | $6.1 | $5.7 to $6.5 | 100% | 0% |
| GPT-6.1 Sol | $4.2 | $4.1 to $4.3 | 100% | 0% |
| GPT-6 Luna | $21.8 | $20.2 to $23.4 | 100% | 25% |
| Claude Sonnet 5.5 | $3.6 | $3.2 to $4.1 | 100% | 0% |
| Claude Opus 5.5 | $3.2 | $2.7 to $3.9 | 97% | 0% |

## Coverage

Answers per model and fare (576 expected):

price               0    1    5    15   35
model                                     
Claude Opus 5.5    576  576  576  576  576
Claude Sonnet 5.5  576  576  576  576  576
GPT-6 Luna         576  576  576  576  576
GPT-6.1 Sol        576  576  576  576  576
GPT-6.1 Terra      576  576  576  576  576

Malformed answers (counted as SKIP): 0.
