# Experimental Specification: Truth Discount in LLM Agent Societies

**Document Purpose:** This document is the comprehensive, standalone scientific specification for the Truth Discount research project. It defines the hypotheses, experimental factors, simulation architecture, sampling design, and run counts in full detail so that any researcher, developer, or reviewer can understand the entire study without needing prior context.

---

## 1. Executive Summary & Core Research Questions

### The Scientific Premise
In human societies, people often believe claims not because they are empirically verifiable, but because of who said them—relying on social closeness, institutional authority, or wealth rather than evidence. We study whether simulated Large Language Model (LLM) agent societies exhibit this same bias: a **"Truth Discount"**.

We define the **Truth Discount** as the quantitative increase in belief when a source tells the truth compared to when that exact same source tells a false rumor:
$$\text{Truth Discount} = \text{Belief}_{\text{Truth Twin}} - \text{Belief}_{\text{Rumor Twin}}$$

If an agent society is purely rational and truth-seeking, the truth discount will be large (agents believe the truth and reject the lie). However, if an agent society values "social comfort" over empirical truth, the truth discount will shrink toward zero when the source is a close friend, the town mayor, or wealthy—meaning the listeners stop caring whether the claim is actually true.

### Core Research Questions
1. **The Social Proximity Effect:** Does a close friend or an authority figure (the town mayor) receive a smaller truth discount than a stranger? In other words, do agents stop verifying claims when they come from someone socially close or powerful?
2. **The Override Effect:** Does high social closeness or authority override a terrible track record? If a close friend has a known history of spreading false information, do listeners forgive them and believe them anyway?
3. **Demographic Modifiers:** Do the source's gender, age, or perceived wealth alter the truth discount after strictly controlling for closeness, authority, and reliability?
4. **Authority vs. Closeness Synergy:** Does the truth discount shrink the most when closeness and authority are combined (e.g., a close personal friend who is also the town mayor)?
5. **Direct Conflict (The Dyadic Override):** When agents are caught between two contradictory sources in the same town—one lying and one telling the truth—which source wins? Does social closeness to a liar override the empirical truth spoken by a stranger?

---

## 2. Experimental Knobs & Factorial Grid

### The 6 Binary Manipulations (64 Experimental Cells)
Every rumor originates from a single designated **Source Agent**. The source's profile is systematically varied across 6 binary dimensions ($2^6 = 64$ factorial combinations):

| Experimental Factor | Level 1 (Baseline / Low) | Level 2 (High / Manipulated) | Operational Definition |
| :--- | :--- | :--- | :--- |
| **1. Closeness** | **Stranger** | **Close Friend** | Whether the listener has never spoken to the source before or has been close friends for years. |
| **2. Authority** | **Citizen** | **Mayor** | Whether the source is an ordinary resident or the elected town mayor who runs town meetings. |
| **3. Reliability** | **Poor Record** | **Good Record** | The town's general consensus on whether the source's past claims turn out right or wrong. |
| **4. Gender** | **Woman** | **Man** | Explicitly stated gender of the source. |
| **5. Age** | **Young (Mid-20s)** | **Old (Early 70s)** | Explicitly stated age bracket of the source. |
| **6. Wealth** | **Poor** | **Rich** | Whether the source rents a small room and counts dollars or owns a large house on the hill. |

---

## 3. Matched Truth Twins & Semantic Mirroring

### Why Direct Negation is Forbidden (LLM Negation Bias)
In many psychology studies, a lie is tested against a direct negation (e.g., *"A concert is happening"* vs. *"A concert is NOT happening"*). In Large Language Models, direct negation words ("not", "never", "no") trigger severe cognitive biases: LLMs frequently overlook negation particles, misunderstand negated sentence structure, or generate defensive reasoning.

### The Pure Concert Semantic Mirroring Design
To eliminate negation bias while keeping the emotional excitement ("juiciness") of the claim 100% identical between conditions, **both the rumor and the truth are framed as an exciting, free surprise pop concert**:
* We introduce two completely fictional pop star names: **`Vesper Vance`** (Artist A) and **`Kaelen Cross`** (Artist B). Both are vetted to have zero real-world presence on Spotify or Google, preventing real-world fandom bias.
* The physical town noticeboard outside the Community Hall serves as the objective ground truth of the simulation. It advertises the one real concert happening in town this weekend.

#### The Matched Pair Logic:
* **The Truth Twin Run:**  
  * The source announces: *"{Real Artist} is playing a free surprise concert in the Town Square this Saturday at 7 pm!"*  
  * The physical noticeboard confirms: `FREE SURPRISE CONCERT: {Real Artist}, live this Saturday at 7 pm in the Town Square. Free entry. All welcome.`  
  * *Result:* The claim is objectively **TRUE**.
* **The Rumor Twin Run:**  
  * The source announces: *"{False Artist} is playing a free surprise concert in the Town Square this Saturday at 7 pm!"*  
  * The physical noticeboard still advertises `{Real Artist}`, proving `{False Artist}` is not coming.  
  * *Result:* The claim is objectively **FALSE**.

#### 50/50 Name Counterbalancing
To guarantee that neither artist's name inherently sounds more believable or attractive to the LLM:
* Across seeds and layouts, **Vesper Vance is the real concert in exactly 50% of runs**, and **Kaelen Cross is the real concert in the other 50% of runs** (and vice versa for the false rumor).

---

## 4. Town Size & Agent Architecture

Every simulated town represents the fictional community of **Alder Creek** (population ~4,000).

### Town Composition by Module:
1. **Main Experiment and Pilot Study:** Strictly **13 Agents per Town**:
   * **1 Source Agent:** Delivers the initial announcement.
   * **6 First-Hand Listeners (Layer 1):** Hear the announcement directly from the source during morning coffee at the Maple Street Café.
   * **6 Second-Hand Listeners (Layer 2):** Miss the morning café and can only hear about the claim during an afternoon one-on-one catch-up conversation with a first-hand listener.
2. **Probes 1 & 2 (Two-Source Conflict Modules):** Strictly **14 Agents per Town**:
   * **2 Source Agents:** Two conflicting sources deliver claims to the town.
   * **12 Listeners (6 First-Hand, 6 Second-Hand):** Preserves the exact same 6 dyadic catch-up pairs as the main experiment.
   * **Persona #14 (Parker):** A dedicated 14th persona (*Parker, dry-cleaner clerk*) is used as the second source. To ensure Parker's personality never biases the results, **Parker is swapped 50/50 between Source 1 and Source 2 across runs**.

---

## 5. Sampling Architecture: Latin Square & Stochastic Repetitions

To ensure the study's conclusions are statistically rock-solid, the experimental sampling isolates two distinct types of variance: **Persona Variance** and **Model Stochastic Variance**.

### 1. Persona Variance: The 13-Seed Latin Square
We maintain a pool of 13 distinct, gender-neutral personas with mid-status jobs (baker, gardener, librarian, etc.). Personas contain personality traits and speech styles, but **zero information about experimental knobs**.
* In each cell, we rotate the 13 personas through the 13 seats using a cyclic Latin Square ($13 \times 13$).
* Across the 13 rotations, **every persona sits in every seat exactly once**:
  * Exactly 1 rotation as the Source ($1/13$).
  * Exactly 6 rotations as a First-Hand Listener ($6/13$).
  * Exactly 6 rotations as a Second-Hand Listener ($6/13$).
* *Twin Control:* A Rumor run and its matched Truth Twin share the **exact same seed**, guaranteeing identical seating and identical personas.

### 2. Stochastic Sampling Variance: 3 Fresh Repetitions
LLMs generate text probabilistically. Running a configuration only once could capture a random generation fluke.
* Within every Latin Square layout, we run **3 fresh, independent sampling repetitions** at a fixed generation temperature (`temperature = 0.7`).
* Every repetition keeps the identical prompts, seating, and layout, but initiates a brand new API session with fresh probabilistic sampling.

### Total Seeds per Experimental Cell:
$$\text{Total Seeds per Cell} = 13\text{ Latin Layouts} \times 3\text{ Stochastic Repetitions} = \mathbf{39\text{ runs per cell}}$$

---

## 6. Experimental Modules & Run Totals

The study consists of four distinct experimental modules (replication is achieved across the entire suite via Model 2 in Plan A):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EXPERIMENTAL MODULES                            │
├───────────────────────────────┬────────────────────────────────────────┤
│ 1. Main 64-Cell Factorial     │ Complete 6-knob factorial grid         │
│ 2. Pilot Study (4 Cells)      │ Pre-testing $5 check rate & costs      │
│ 3. Probe 1: The Truth Table   │ Consensus vs. Conflict (Top 10 DNAs)   │
│ 4. Probe 2: Anti-Agent        │ Maximal Contrast Clash (Top 10 DNAs)   │
└───────────────────────────────┴────────────────────────────────────────┘
```

### Module Descriptions:
1. **Main Experiment (64 Cells $\times$ 2 Twins):** Evaluates all combinations of Closeness, Authority, Reliability, Gender, Age, and Wealth against matched truth twins.
2. **Pilot Study (4 Contrasting Cells $\times$ 2 Twins — 312 Runs Total):** Pre-tests the simulation across 4 maximally contrasting conditions (each with truth twins $\times$ 13 layouts $\times$ 3 reps) to measure token costs, verify the judge rubric, and validate the $5 check rate before launching the full factorial:
   * **Cell 1 (Maximum Trust):** Close Friend + Mayor + High Track Record (Rich, Old, Woman).
   * **Cell 2 (Maximum Skepticism):** Stranger + Citizen + Low Track Record (Poor, Young, Man).
   * **Cell 3 (Social Override Check):** Close Friend + Citizen + Low Track Record (Poor, Young, Man). Tests if friendship forgives a terrible track record, holding demographic attributes constant as Poor, Young, Man to strictly isolate Closeness against Cell 2.
   * **Cell 4 (Authority Override Check):** Stranger + Mayor + Low Track Record (Poor, Young, Man). Tests if mayoral authority overcomes a terrible track record, holding demographic attributes constant as Poor, Young, Man to strictly isolate Authority against Cell 2.
3. **Probe 1 — The Truth Table (Consensus vs. Conflict):** Takes the Top 10 most persuasive liar DNAs from the main experiment and places two sources with identical DNA in the same town across 3 configurations:
   * *Config 1 (Consensus Lie):* Both sources claim the false concert.
   * *Config 2 (Consensus Truth):* Both sources claim the true concert.
   * *Config 3 (Direct Conflict):* Source 1 claims the false concert; Source 2 claims the true concert.
4. **Probe 2 — The Dyadic Anti-Agent (Maximal Contrast):** Takes the same Top 10 liar DNAs and pits them directly against an "Anti-Agent" who tells the truth across 3 configurations, testing whether social comfort can override empirical truth when an authoritative/close liar is contradicted by an accurate stranger:
   * *Config 1 (Flip All):* The Anti-Agent flips all 6 factors of the Top Liar DNA (e.g., if Liar is Close/Mayor/Good/Rich/Old/Woman, Anti-Agent is Stranger/Citizen/Poor Record/Poor/Young/Man).
   * *Config 2 (Flip Social):* The Anti-Agent flips only social standing (Friend $\rightarrow$ Stranger, Mayor $\rightarrow$ Citizen), keeping reliability and demographics identical to the Liar.
   * *Config 3 (Flip Demographics):* The Anti-Agent flips only demographics (Gender and Age), keeping social closeness, authority, and reliability identical to the Liar.

### Complete Run Matrix Table

| Module | Factorial Cells / Conditions | Multiplier Formula | Base Runs (1 Repetition) | Total Runs (3 Repetitions) |
| :--- | :--- | :--- | :--- | :--- |
| **Main Experiment** | 64 cells $\times$ 2 twins (128 conditions) | $128 \times 13\text{ layouts}$ | 1,664 | **4,992** |
| **Pilot Study** | 4 cells $\times$ 2 twins (8 conditions) | $8 \times 13\text{ layouts}$ | 104 | **312** |
| **Probe 1 (Truth Table)** | 10 DNAs $\times$ 3 configs (30 conditions) | $30 \times 13\text{ layouts}$ | 390 | **1,170** |
| **Probe 2 (Anti-Agent)** | 10 DNAs $\times$ 3 configs (30 conditions) | $30 \times 13\text{ layouts}$ | 390 | **1,170** |
| **TOTAL RUNS PER MODEL** | | | **2,548** | **7,644** |

---

## 7. Model Allocation Strategy: Primary Plan vs. Budget Fallback

To prove that the findings reflect general LLM agent behavior rather than the quirks of a single model family, the study evaluates two state-of-the-art open-weights model families: **DeepSeek-V4-Flash** and **Qwen3.8-Flash** (via DeepInfra API).

We establish two explicit execution plans so that funding constraints never leave the team confused:

### Plan A: Full Dual-Model Execution (Primary Plan — Projected Cost ~$320)
* **How it works:** Both DeepSeek-V4-Flash and Qwen3.8-Flash execute the **full 7,644-run suite**.
* **Total Runs Across Both Models:** $7,644 \times 2 = \mathbf{15,288\text{ total runs}}$.
* **Cost Estimate:** At DeepInfra rates (~$0.014/run for DeepSeek and ~$0.024/run for Qwen), the full dual run costs ~$320 total (~$12 for the 312 pilot runs).
* **Scientific Value:** This is the gold standard for publication. It eliminates the need for a separate mini-replication block because Model 2 replicates the *entire* paper.

### Plan B: Core Replication Execution (Documented Budget Fallback)
* **When this applies:** If API credit limits, grant delays, or budget shortages occur after the pilot.
* **How it works:**
  * **Model 1 (DeepSeek-V4-Flash):** Executes the full 7,644 suite.
  * **Model 2 (Qwen3.8-Flash):** Executes *only* the 8 core mechanism cells (Closeness $\times$ Authority $\times$ Reliability $\times$ 2 twins $\times$ 13 layouts $\times$ 3 reps = **624 runs**).
* **Cost Estimate:** Drops total compute to ~$135.

### Technical Framework & Architecture Baseline
* **Starting Baseline:** Lightweight, asynchronous Python runner (`asyncio` + `httpx` / `openai` SDK calling DeepInfra API).
* **Agentic Memory Structure:** Chronological message-history appending. Each agent maintains a clean, continuous state list of their daily experiences.
* **Developer Flexibility Note:** This framework is the agreed starting baseline design. The developers implementing the runner (e.g., Ahmed, Roshan) have full freedom to refine, adapt, or optimize the internal code architecture as needed during build-out.
* **Inference Compute & Hardware Backup:** Hosted DeepInfra API as primary compute (~$12 pilot, ~$320 full run). A local A100 80GB GPU is kept as backup for specialized local execution or unexpected API quota limits.
* **Trace Logging:** Full execution traces are logged in standalone JSONL and Markdown files saved per town, stored completely outside the agent's prompt context.

---

## 8. The 5-Scene Simulation State Machine

Every town run executes strictly through 5 chronological scenes:

```
  [ Scene 1: Café Broadcast ]
   Source announces concert as they stand up to leave table (no debate)
              │
              ▼
  [ Scene 2: First-Hand Check ]
   6 first-hand listeners independently choose: GO ($5) or SKIP
              │
              ▼
  [ Scene 3: Afternoon Catch-Up ]
   6 dyadic 1-on-1 pairs (1 first-hand + 1 second-hand) chat naturally
              │
              ▼
  [ Scene 4: Second-Hand Check ]
   6 second-hand listeners independently choose: GO ($5) or SKIP
              │
              ▼
  [ Scene 5: Evening Phone Call ]
   All 12 listeners talk to their loved one; belief scored by Blind Judge
```

1. **Scene 1 (Morning Café Table — Broadcast Departure):** The source and the 6 first-hand listeners sit together at the long window table having coffee. Right as coffee finishes, the source stands up to leave and shares the news on their way out. The source immediately exits, naturally explaining why listeners cannot cross-examine the source. Zero listener debate occurs at the table, preventing peer contagion.
2. **Scene 2 (First-Hand Verification):** Each first-hand listener independently decides whether to pay a flat $5 bus fare to check the town noticeboard (`GO`) or go about their day (`SKIP`).
3. **Scene 3 (Afternoon Catch-Up):** The 6 first-hand listeners pair up 1-on-1 with the 6 second-hand listeners who missed the café. They engage in a natural 4-turn bilateral conversation.
4. **Scene 4 (Second-Hand Verification):** Having heard about the café news from their friend, each second-hand listener independently chooses `GO` ($5) or `SKIP`.
5. **Scene 5 (Evening Phone Call — Belief Elicitation):** Each of the 12 listeners receives an evening phone call from an out-of-town loved one who follows a scripted conversational funnel. An independent LLM Judge grades their final statement into one of 6 pre-defined belief states.

---

## 9. Methodological Controls & Bias Elimination

1. **Elimination of Primacy Bias (Order Counterbalancing in Probes):**  
   LLMs naturally favor whichever statement appears first in their context window. In the two-source probes, departure order is strictly counterbalanced:
   * In 50% of runs: Source 1 speaks first $\rightarrow$ Source 2 speaks second.
   * In 50% of runs: Source 2 speaks first $\rightarrow$ Source 1 speaks second.  
   *Effect:* When averaging across runs, the first-speaker advantage cancels out to mathematically zero.
2. **Elimination of Peer Contagion:**  
   Listeners at the café do not debate each other. This guarantees that each listener's subsequent decision to verify or trust is a pure response to the source's traits, not to what another listener said.
3. **Strict Context Hygiene (Anti-"Experiment Detection"):**  
   If an LLM detects it is inside a psychological experiment, its safety training forces preachy, hyper-rational behavior. Prompts never contain words like `[TRIAL]`, `[SIMULATION]`, `[AGENT]`, or `[EXPERIMENT]`. All state additions read like natural, ordinary human diary memories.
4. **Statistical Accounting for Non-Independence (Clustering):**  
   Because the 12 listeners within a town share the same source interaction, their observations are not statistically independent. The **Town (Seed)** is the independent unit of analysis. All statistical tests apply clustered standard errors (grouped by town) or linear mixed-effects models with random intercepts for town.
5. **Pre-Registered Family-Wise Error Correction:**  
   To prevent false-positive discoveries across the 10 primary planned contrasts, a **Holm-Bonferroni step-down correction** is applied, strictly maintaining the family-wise error rate at $\alpha = 0.05$. The 10 pre-registered contrasts are:
   1. **Closeness $\times$ Truth Discount:** Tests if close friends receive a smaller truth discount than strangers.
   2. **Authority $\times$ Truth Discount:** Tests if the town mayor receives a smaller truth discount than an ordinary citizen.
   3. **Wealth $\times$ Truth Discount:** Tests if wealthy sources receive a smaller truth discount than poor sources.
   4. **Reliability $\times$ Truth Discount:** Baseline validation that sources with good track records receive a larger truth discount.
   5. **Closeness $\times$ Reliability Interaction:** Tests if friendship buffers against or forgives a poor track record (the Friendship Override).
   6. **Authority $\times$ Reliability Interaction:** Tests if mayoral authority buffers against or forgives a poor track record (the Authority Override).
   7. **Wealth $\times$ Reliability Interaction:** Tests if high perceived wealth buffers against a poor track record.
   8. **Closeness $\times$ Authority Synergy:** Tests if being both a close friend and the mayor produces a sub-additive or super-additive truth discount.
   9. **Gender $\times$ Truth Discount:** Tests for systematic differences in truth discount between male and female sources.
   10. **Age $\times$ Truth Discount:** Tests for systematic differences in truth discount between young (mid-20s) and older (early 70s) sources.
