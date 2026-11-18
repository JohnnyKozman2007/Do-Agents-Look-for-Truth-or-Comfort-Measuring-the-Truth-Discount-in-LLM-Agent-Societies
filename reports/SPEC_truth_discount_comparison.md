# Specification: Report 3 — Truth Discount & Comparisons (Gemini 3.7 Flash)

**Status:** Agreed Source of Truth  
**Branch:** `feat/rumor-truth-reports`  
**Scope:** Formal comparison between **Truth Towns** (`truth = 1`) and **Rumor Towns** (`truth = 0`), plus **DeepSeek-V4-Flash vs. Qwen3.8-Flash** comparisons, using Gemini 3.7 Flash judge outputs.  
**Explicit Exclusions:** Qwen3-32B judge outputs and Two-Source Probes (Probes 1 & 2) are excluded.

---

## 1. Core Estimand & Missingness Policy
- **Truth Discount (Matched Pair & Marginal):** $\text{Truth Discount} = \text{Belief}_{\text{Truth Twin}} - \text{Belief}_{\text{Rumor Twin}}$.
  - Also computed for `GO %` ($\Delta\text{GO} = \text{GO}_{\text{Truth}} - \text{GO}_{\text{Rumor}}$), `NOT_MENTIONED %` ($\Delta\text{Omission}$), and every categorical label rate (`FACT`, `UNCERTAIN`, `SKEPTICAL`, `CHECKED_TRUE`, `CHECKED_FALSE`).
- **No Zero-Imputation of Invalids:** Individual `judgment_status = invalid` listener rows remain `NaN` and are excluded without discarding the remaining valid listeners in that town. Valid `NOT_MENTIONED` rows remain excluded from primary conditional `Belief`, and are checked separately under `Silence = 0.0` and `Silence = 0.5`.

---

## 2. Architecture & Sections (`reports/truth_discount_comparison/`)

1. **Section 1 — Top Summary Tables (`Table 1A` Per Model × Layer, `Table 1B` Combined):**
   - Side-by-side `Rumor`, `Truth`, and **Matched-Pair Difference (`Truth − Rumor` + 95% pair-clustered CI)** for `First-Hand`, `Second-Hand`, and `Overall (All 12)` across `Belief`, `Silence=0.0`, `Silence=0.5`, `GO %`, `SKIP %`, `Transmission %`, `Evidence Transmission %`, and all 6 categorical labels.
2. **Section 2 — Butterfly (Mirror Bar) Comparison Charts (Offline SVG):**
   - **Chart 2A — Categorical Labels & Verification Butterfly:** Rumor (left) vs. Truth (right) back-to-back bars across `Model × Layer`.
   - **Chart 2B — 64-DNA Truth Discount Butterfly:** All 64 DNAs sorted by Truth Discount (`Truth − Rumor`), showing Rumor on the left, Truth on the right, and the net Truth Discount gap in the center across `Model × POV` and outcomes (`Belief`, `GO %`, `SKEPTICAL %`, `NOT_MENTIONED %`).
3. **Section 3 — Paired Symmetry & Truth Discount Tests (10 Planned Contrasts, Pair-Clustered):**
   - Pooled model over all listeners (`truth ∈ {0, 1}`):
     `outcome ~ truth * (6 main knobs + 4 planned interactions) + C(real_artist)`
   - **Clustering:** Standard errors clustered by matched twin pair (`pair_id`, capturing both within-town correlation across listeners AND within-seed correlation across matched Truth/Rumor twins). Companion **spec LMM** (`smf.mixedlm(..., groups=run_id)`) reported alongside for conditional `Belief`.
   - **Outputs per contrast (`Model × POV × Outcome`):**
     - `Effect in Rumor` (with 95% CI & p)
     - `Effect in Truth` (with 95% CI & p)
     - **`Δ Truth Discount = Effect_Truth − Effect_Rumor`** (`truth × contrast` interaction — directly tests whether the factor affects Truth and Rumor equally or asymmetrically!) + 95% CI + pair-clustered `p` + **Holm-adjusted `p` across all 10 planned contrasts**.
   - **Paired Forest / Dumbbell SVG Plot:** Visualizes `Effect in Rumor` vs. `Effect in Truth` and `Δ Truth Discount` for all 10 contrasts.
   - **Section 3B — 4 Interaction Pairs (16-DNA Combo Comparison):** Shows each of the 4 combos (`(a1,b1)`, `(a1,b0)`, `(a0,b1)`, `(a0,b0)`) across `Rumor`, `Truth`, and `Truth Discount (Truth − Rumor)`, plus whether the simple effects differ between Truth and Rumor.
4. **Section 4 — Top 10 Largest & Bottom 10 Smallest Truth Discount DNAs (`Model × POV`):**
   - Ranks all 64 cells by matched-pair `Truth Discount` (`Truth − Rumor` inside each `pair_id`), alongside `Rumor Mean`, `Truth Mean`, `Rumor GO %`, `Truth GO %`, `Δ GO %`, and pair-clustered 95% CI.
5. **Section 5 — Model Comparison (`DeepSeek-V4-Flash − Qwen3.8-Flash`):**
   - Pair-clustered comparison of the two AI societies on `Rumor`, `Truth`, and `Truth Discount` across `First-Hand`, `Second-Hand`, and `Source (All 12)` for `Belief`, `GO %`, `NOT_MENTIONED %`, `FACT %`, and `SKEPTICAL %`.
