# Specification: Rumor Towns & Truth Towns Reports (Gemini 3.7 Flash Main Study)

**Status:** Agreed Source of Truth  
**Branch:** `feat/rumor-truth-reports`  
**Scope:** Standalone empirical reports for **Rumor Towns** (`condition_type = "rumor"`) and **Truth Towns** (`condition_type = "truth_twin"`), using the Gemini 3.7 Flash judge outputs.  
**Explicit Exclusions:**
- Paired **Truth Discount** ($\text{Truth} - \text{Rumor}$) comparison report is deferred to a separate step.
- **Qwen3-32B** judge outputs are excluded completely.
- **4 planned interaction terms** (`closeness × reliability`, `authority × reliability`, `wealth × reliability`, `closeness × authority`) are deferred; this phase tests the **6 main knobs** first.
- **Two-source conflict probes (Probes 1 & 2 / RQ5)** were never simulated and cannot be analyzed.

---

## 1. Input Data & Denominator / Missingness Policy

**Source files:**
- `results/main-gemini-3.7-flash/listeners.csv` (119,808 listener rows across 9,984 towns: 4,992 Rumor towns, 4,992 Truth towns; 64 cells × 39 pairs × 2 agent models × 2 conditions).
- `results/main-gemini-3.7-flash/conditions.csv` (condition-level transmission, evidence transmission, and simulation-decision audit counts).

**Honest Handling of Invalid / Fallback Outputs (No Zero-Imputation):**
1. **Judge `INVALID` outputs (402 / 119,808 = 0.34%):**
   - Invalid rows (`judgment_status != "valid"`, `belief = NaN`, `mentioned = NaN`) are **completely excluded** from both numerators and denominators for categorical label percentages, `Belief` means, and regressions. They are **never** converted to zeros (`0`).
   - Counts and percentages of `INVALID` rows are reported explicitly in the top summary tables for transparency.
2. **Valid `NOT_MENTIONED` omissions (2,408 / 119,808 = 2.01%):**
   - Excluded from the primary conditional `Belief` score denominator per spec (`docs/04_metrics_and_judge.md`).
   - Tracked separately as the `NOT_MENTIONED %` outcome among valid judgments.
   - Two pre-registered sensitivity checks (`Silence = 0.0` and `Silence = 0.5`) assign `0.0` or `0.5` **only** to valid `NOT_MENTIONED` rows—never to `INVALID` rows.
3. **Categorical Label Shares:**
   - Denominator = valid judged listeners (`FACT + UNCERTAIN + SKEPTICAL + CHECKED_TRUE + CHECKED_FALSE + NOT_MENTIONED = 100.0%`).
4. **Verification Decisions (`GO` / `SKIP`):**
   - Denominator = all expected listeners (`N = 14,976` per condition × model × layer; `0` missing or invalid verification decisions).
   - Runner disclosure from `conditions.csv`: 98 of 119,808 listener decisions (0.08%: 45 first-hand, 53 second-hand) had `malformed_fallback_skip` during simulation and appear as `SKIP` in `listeners.csv`; this exact count is disclosed in the report metadata.

---

## 2. Architecture: 2 Reports × 4 Layers

### Two Reports
1. **Report 1 — Rumor Towns** (`reports/rumor_towns/`): False claims (`condition_type = "rumor"`). Measures who persuades agents to believe a falsehood or skip checking, who stops it, and who gets fooled.
2. **Report 2 — Truth Towns** (`reports/truth_towns/`): True claims (`condition_type = "truth_twin"`). Measures who gets believed, who verifies, and where true claims fail to persuade or get dropped.

### Top-Level Summary Tables (Included at the Top of Both Reports)
- **Table A — Per-Model Summary (`deepseek_v4_flash` and `qwen_3_8_flash`):**
  - Shown for **First-Hand only** (seats 1–6), **Second-Hand only** (seats 7–12), and **Overall (both layers combined, seats 1–12)**.
  - Metrics: Valid `N`, `INVALID` count & `%`, all 6 categorical label `%`, conditional `Belief` mean, `Belief (Silence = 0.0)`, `Belief (Silence = 0.5)`, `GO %`, `SKIP %`, plus town-level `Transmission %` and `Evidence Transmission %`.
- **Table B — Experiment-Wide Average (Both Models Combined):**
  - Pooled 50/50 across `deepseek_v4_flash` and `qwen_3_8_flash` for **First-Hand only**, **Second-Hand only**, and **Overall**.

### Three Pipeline POVs (Each Split by `DeepSeek-V4-Flash` vs. `Qwen3.8-Flash`)
1. **POV 1 — Source POV (All 12 Listeners, Seats 1–12):**
   - Which Source DNAs (out of 64) and 6 traits spread the claim best and suppress `$5` noticeboard verification across the town as a whole.
2. **POV 2 — First-Hand Listener POV (Seats 1–6 — Fooled + Gatekeeper):**
   - **Fooled:** First-hand `Belief`, label distribution, and `$5` `GO %` / `SKIP %`.
   - **Gatekeeper Role:** Whether first-hand listeners passed the concert claim on (`transmission_keyword_rate`), passed poster evidence on when they checked (`evidence_keyword_rate`), and the **dyadic gatekeeper effect** (`Seat i <-> Seat i+6`) showing Second-Hand `Belief`, `FACT %`, and `GO %` conditional on First-Hand `GO` vs. `SKIP`.
3. **POV 3 — Second-Hand Listener POV (Seats 7–12 — Downstream Susceptibility):**
   - How easily second-hand listeners believed, verified, doubted, or omitted the claim (`NOT_MENTIONED %`) without ever meeting the Source, plus susceptibility broken down by paired First-Hand partner decision (`GO` vs. `SKIP`).

---

## 3. Required Analyses Inside Every Model × POV

### Part 1: Top 10 Strongest & Bottom 10 Weakest Source DNAs (64 Cells)
For each `Model × POV`, rank all 64 Source DNAs (`Strongest = Highest`, `Weakest = Lowest`) and output Top 10 and Bottom 10 for:
- `Belief` (conditional mean; **tie-breaker:** higher `SKIP %` / lower `GO %`, then `cell_id`)
- `SKIP %` (with `GO %` shown alongside)
- **All 6 categorical labels individually:** `FACT %`, `UNCERTAIN %`, `SKEPTICAL %`, `CHECKED_TRUE %`, `CHECKED_FALSE %`, `NOT_MENTIONED %` (**tie-breaker:** higher `Belief`, then higher `SKIP %`, then `cell_id`; any `0.0%` tie counts > 10 explicitly noted).

Full 64-cell tables are exported to CSV for every `Model × POV`.

### Part 2: Controlled Main Effects of the 6 Knobs (With Town Clustering)
For each `Model × POV`, estimate the controlled effect of each of the 6 binary knobs while simultaneously controlling for the other 5 knobs and `real_artist` (`Vesper Vance` vs. `Kaelen Cross`):

| Knob | Level A (Positive in Contrast) | Level B (Reference) | Contrast Direction |
| :--- | :--- | :--- | :--- |
| `closeness` | `close_friend` | `stranger` | `close_friend − stranger` |
| `authority` | `mayor` | `citizen` | `mayor − citizen` |
| `reliability` | `good_record` | `poor_record` | `good_record − poor_record` |
| `wealth` | `rich` | `poor` | `rich − poor` |
| `gender` | `woman` | `man` | `woman − man` |
| `age` | `old` | `young` | `old − young` |

*(Contrast directions match `configs/analysis_policy.main.json`.)*

**Statistical Models (Clustering by Town `run_id`):**
- Formula: `outcome ~ C(closeness) + C(authority) + C(reliability) + C(wealth) + C(gender) + C(age) + C(real_artist)`
- **Town-Clustered OLS / Linear Probability Model** (`cov_type="cluster", cov_kwds={"groups": run_id}`) for **all** outcomes:
  - `Belief` (conditional), `Belief (Silence = 0.0)`, `Belief (Silence = 0.5)`
  - `GO %` (with `SKIP %` = `-GO %`)
  - `NOT_MENTIONED %`, `FACT %`, `UNCERTAIN %`, `SKEPTICAL %`, `CHECKED_TRUE %`, `CHECKED_FALSE %`
  - Plus town-level `Evidence Transmission %` (for First-Hand POV, where one row per checker/town applies; clustered by `run_id`).
- **Companion Linear Mixed-Effects Model (LMM)** with `run_id` random intercept (`smf.mixedlm(..., groups=run_id)`) on conditional `Belief`, matching the spec (`docs/04_metrics_and_judge.md`), reported alongside Town-Clustered OLS to verify agreement.
- **Reported columns per knob:** Adjusted Mean (Level A), Adjusted Mean (Level B), Controlled Effect (`A − B`), Cluster-Robust SE, 95% CI, raw clustered `p`-value, and **Holm-adjusted `p`-value** across the 6 knobs per outcome × model × POV.

---

## 4. Deliverables

- `scripts/build_condition_reports.py`: Reproducible builder script reading `results/main-gemini-3.7-flash/` (no LLM calls).
- `tests/test_condition_reports.py`: Automated tests validating zero-exclusion of `INVALID` rows, tie-breaking rules, controlled means/Holm adjustments, and dyadic pairing logic.
- `reports/rumor_towns/`:
  - `report.html` (interactive Model / POV / Metric-Label tabs + full tables)
  - `report.md` (clean Markdown tables)
  - `csv/` (`summary_by_model_layer.csv`, `summary_experiment_overall.csv`, `dyadic_gatekeeper.csv`, `knob_effects.csv`, `dna_rankings_all64.csv`)
- `reports/truth_towns/`:
  - `report.html`, `report.md`, `csv/` (same exact structure)
