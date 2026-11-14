# Judge Model Bake-Off Report

**Date:** Sat Nov 14 2026
**Sample Size:** 100 exploratory calls sampled from main simulation shard 5
**Human Labels Available:** 100 from a single rater who could see the condition and listener layer
**Parser Version:** `quote-normalized-v1` (Smart-quote normalized)
**Historical ledger:** `outputs/ledgers/bake-off.jsonl` on the original operator's machine

## Summary Results

| Model | Valid Labels | Malformed % | Agreement w/ Human | Cohen's Kappa (κ) | Recorded Cost (100 calls) | Est. Cost / 100k calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Claude Haiku 5.5** | 91/100 | 9.0% | 71.0% (71/100) | **0.628** | $0.0134 | $17 |
| **Claude Sonnet 5.5** | 99/100 | 1.0% | 81.0% (81/100) | **0.750** | $0.3893 | $350 |
| **GPT-4o** | 94/100 | 6.0% | 74.0% (74/100) | **0.666** | $0.1950 | $250 |
| **GPT-5 Sol** | 99/100 | 1.0% | 79.0% (79/100) | **0.725** | $0.1843 | $120 |
| **Gemini 3.7 Flash** | 92/100 | 8.0% | 80.0% (80/100) | **0.737** | $0.0239 at prior configured rates | Reprice from raw usage |

DeepInfra charges $0.75 input and $3.75 output per million tokens. The earlier Gemini estimate used $0.15 input and $0.60 output. The `gemini-3.7-flash-v2` profile budgets any reported cache hits at the full input rate, pending a published discount for this model. The original runner could record provider failures at zero, so the table preserves unverified historical subtotals. Use provider usage records to check billed costs and update the estimate. [DeepInfra Gemini pricing](https://deepinfra.com/google/gemini-3.7-flash)

The bake-off used JSON object output. The proposed production profile uses strict JSON schema output and explicitly disables reasoning. Confirm the revised settings and judge performance on independently labelled, blinded pilot cases before selecting a judge for the main analysis.

To reproduce the report from saved data, put the original sample, human labels and prediction cache under the local, Git-ignored `outputs/` directory and run `python scripts/run_bakeoff.py`. The script reads those files and rebuilds the aggregate report. Keep individual calls and labels in the local study data.

## Original Comparison Rule
> **Rule:** The cheapest judge within 0.05 kappa (κ) of the best wins. Haiku wins ties.
