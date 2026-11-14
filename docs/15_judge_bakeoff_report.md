# Judge Model Bake-Off Report

**Date:** Sat Nov 14 2026
**Sample Size:** 100 stratified pilot calls
**Human Labels Available:** 100
**Parser Version:** `quote-normalized-v1` (Smart-quote normalized)
**Ledger Path:** `C:\Users\Sidho\OneDrive\Desktop\RESEARCH\truth-discount-pr11\outputs\ledgers\bake-off.jsonl`

## Summary Results

| Model | Valid Labels | Malformed % | Agreement w/ Human | Cohen's Kappa (κ) | Measured Cost (100 calls) | Est. Cost / 100k calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Claude Haiku 5.5** | 91/100 | 9.0% | 71.0% (71/100) | **0.628** | $0.0134 | $17 |
| **Claude Sonnet 5.5** | 99/100 | 1.0% | 81.0% (81/100) | **0.750** | $0.3893 | $350 |
| **GPT-4o** | 94/100 | 6.0% | 74.0% (74/100) | **0.666** | $0.1950 | $250 |
| **GPT-5 Sol** | 99/100 | 1.0% | 79.0% (79/100) | **0.725** | $0.1843 | $120 |
| **Gemini 3.7 Flash** | 92/100 | 8.0% | 80.0% (80/100) | **0.737** | $0.0239 | $25 |

## Selection Rule Applied
> **Rule:** The cheapest judge within 0.05 kappa (κ) of the best wins. Haiku wins ties.
