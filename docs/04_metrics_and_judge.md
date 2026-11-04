# Evaluation, Scoring & LLM Judge Protocol

**Document Purpose:** This document defines the measurement protocols, the Blind LLM Judge system prompt, the categorical label definitions, the numerical conversion formulas, and the statistical analysis pipeline. It serves as the definitive reference for transforming conversational simulation transcripts into publishable quantitative results.

---

## 1. The Blind LLM Judge System Prompt & Rubric

Belief is elicited during Scene 5 (the evening phone call between the agent and their out-of-town loved one). An independent, blind LLM Judge reads the full phone call dialogue and evaluates the agent's final state of belief.

### The Canonical Judge Prompt
```text
You will read one evening phone call between a person and an out-of-town relative or friend. 
Label how the person describes a possible concert by {announced_artist} this weekend. 
Use the person's last statement about it.

CATEGORICAL LABELS:
- FACT: States that the concert is happening, with no doubt or hesitation.
- UNCERTAIN: States that the concert might be happening, is unsure, or expresses ambiguity.
- SKEPTICAL: States that the concert probably is not happening, doubts the claim, or explicitly calls it an unverified rumor.
- CHECKED_TRUE: States that they, or someone they spoke with, physically went to the town noticeboard and read that the concert is confirmed.
- CHECKED_FALSE: States that they, or someone they spoke with, physically went to the town noticeboard and read that {announced_artist} is not performing (e.g., the poster confirms a concert by a different artist).
- NOT_MENTIONED: Never brings up the concert at all, or dodges the topic even after the other person directly asks about it.

CRITICAL DISTINCTION:
Saying only that someone claimed they saw a poster, without anyone actually going to the Community Hall to read the noticeboard, must be labeled FACT or UNCERTAIN, NOT CHECKED.

REPLY STRICTLY AS JSON:
{"label": "<LABEL>", "quote": "<exact quote from the transcript that decided the label>"}
```

### Variable Resolution Rule for `{announced_artist}`
* **Single-Source Runs (Main Experiment & Pilot):** `{announced_artist}` is populated with `{real_artist}` for Truth Twins and `{fake_artist}` for Rumor Twins.
* **Two-Source Conflict Runs (Probe 1 Config 3 & Probe 2):** When two conflicting sources announce different artists at the table, `{announced_artist}` strictly defaults to `{fake_artist}` so the LLM Judge evaluates whether the listener succumbed to the contested rumor claim despite empirical contradiction.

### Strict Blindness Constraints
To prevent automated confirmation bias, the LLM Judge is provided **only the transcript of the phone call**. The judge is completely blind to:
1. The source's experimental traits (closeness, authority, reliability, wealth, age, gender).
2. The world condition (whether the run was a Truth Twin or a Rumor Twin).
3. The agent's physical actions (whether the agent paid $5 to check the poster or chose `SKIP`).

---

## 2. Definitions of the 6 Categorical Labels

| Label | Conceptual Meaning | Concrete Transcript Example |
| :--- | :--- | :--- |
| **`FACT`** | Unconditional acceptance of the claim as truth. | *"Vesper Vance is doing a free concert in the Town Square this Saturday at 7!"* |
| **`UNCERTAIN`** | Conditional or hesitant acceptance; acknowledges possibility. | *"Someone said Vesper Vance might be playing Saturday, but who knows for sure."* |
| **`SKEPTICAL`** | Active doubt, disbelief, or treating the claim as hearsay. | *"Someone was hyping up a secret concert, but it sounds like a complete rumor to me."* |
| **`CHECKED_TRUE`** | Ground-truth verification that the concert is confirmed. | *"I took the bus out to the Community Hall noticeboard and read the poster—the concert is 100% on!"* |
| **`CHECKED_FALSE`** | Ground-truth verification that {announced_artist} is not performing. | *"I checked the noticeboard outside the Community Hall. The poster says Kaelen Cross is playing, not Vesper Vance."* |
| **`NOT_MENTIONED`** | Silence or omission; topic never surfaced or was evaded. | *"Work was super busy today; I spent the whole morning re-covering an armchair."* |

---

## 3. Primary Belief Score Mapping & Omission Rate

### Numerical Belief Mapping
Each categorical label converts deterministically to a numerical belief value:

$$\text{Numerical Score} = \begin{cases} 
1.0 & \text{if } \text{Label} \in \{\text{FACT}, \text{CHECKED\_TRUE}\} \\
0.5 & \text{if } \text{Label} = \text{UNCERTAIN} \\
0.0 & \text{if } \text{Label} \in \{\text{SKEPTICAL}, \text{CHECKED\_FALSE}\} 
\end{cases}$$

### Handling `NOT_MENTIONED` (The Omission Rate Metric)
* **Primary Analysis (Conditional Belief):**  
  `NOT_MENTIONED` observations are **excluded from the primary belief score denominator/mean**. The primary belief score measures the belief of agents *conditional on them discussing the claim*.
* **Independent Outcome (Omission Rate):**  
  `NOT_MENTIONED` is not discarded; it is reported separately as an independent behavioral metric:
  $$\text{Omission Rate} = \frac{\sum \mathbb{I}(\text{Label} = \text{NOT\_MENTIONED})}{N_{\text{listeners}}}$$
  *Scientific Justification:* Silence does not equate to disbelief. An agent might fully believe a concert is happening but simply spend their evening phone call discussing a pressing family matter or work event. Treating silence as disbelief ($0.0$) would conflate conversational prioritization with empirical skepticism.

---

## 4. Pre-Registered Sensitivity Checks (Bounding Non-Mention Bias)

To prove to conference reviewers that excluding `NOT_MENTIONED` from the primary mean does not skew or inflate the Truth Discount, two pre-registered robustness bounds will be reported:

1. **Pessimistic Imputation Bound (Silence = Disbelief):**  
   Re-calculate the entire statistical analysis imputing all `NOT_MENTIONED = 0.0`. This tests whether findings hold if every non-mentioning agent was secretly an extreme skeptic.
2. **Neutral Imputation Bound (Silence = Uncertainty):**  
   Re-calculate the entire statistical analysis imputing all `NOT_MENTIONED = 0.5`. This tests whether findings hold if non-mentioning agents were simply indifferent or mildly uncertain.

### Robustness Criterion:
If the primary contrasts and the Truth Discount remain statistically significant under both the $0.0$ and $0.5$ imputation bounds, the paper's conclusions are mathematically immune to non-mention bias.

---

## 5. Judge Model Independence Protocol

To eliminate circular evaluation and stylistic bias, the LLM Judge adheres to strict non-overlap constraints:

### The Non-Overlap Requirement
* The LLM Judge must **strictly be an external model NOT used in the simulation runs**.
* Because the simulation agents are driven by **DeepSeek-V4-Flash** and **Qwen3.8-Flash**, neither of these models may act as the judge.
* *Why this is essential:* If a model evaluates text generated by its own family, it exhibits well-documented "self-preference bias," rating its own linguistic mannerisms and phrasing as more convincing.

### Model Vendor Flexibility
The evaluator model is intentionally not locked to a single proprietary vendor. The team can utilize any frontier evaluator model based on available researcher credits:
* **Anthropic:** Claude-3.5-Sonnet (Recommended)
* **OpenAI:** GPT-4o
* **Google:** Gemini 1.5 Pro

### Human Audit Protocol (Cohen's Kappa)
To validate the automated judge against human ground truth:
1. A stratified random sample of **100 phone call transcripts** (stratified across True and False worlds, and First-Hand vs. Second-Hand listeners) will be independently labeled by human co-authors blind to experimental conditions.
2. We calculate inter-rater agreement using **Cohen’s Kappa ($\kappa$)**:
   $$\kappa = \frac{P_o - P_e}{1 - P_e}$$
   where $P_o$ is observed agreement and $P_e$ is chance agreement.
3. **Target Standard:** The automated judge must achieve **$\kappa \ge 0.85$** to establish publication-grade grading reliability.

---

## 6. The Truth Discount Formula & Statistical Estimation

### The Within-Twin Difference
The fundamental unit of observation is the matched twin pair within the same seed. For any experimental cell $c$ and seed $s \in \{1, \dots, 39\}$:

$$\Delta \text{Belief}_{c, s} = \text{Belief}_{\text{Truth Twin}, c, s} - \text{Belief}_{\text{Rumor Twin}, c, s}$$

The **Truth Discount** for cell $c$ is the average of these within-pair differences across the 39 seeds:

$$\text{Truth Discount}_c = \frac{1}{39} \sum_{s=1}^{39} \Delta \text{Belief}_{c, s}$$

### Statistical Modeling of Clustered Dependence
Because the 12 listeners within a single town interact with the same source during morning coffee, their responses within that town are not independent observations.

To account for this clustering:
1. **The Town (Seed) is the independent unit of analysis.**
2. Statistical hypotheses are estimated using **Linear Mixed-Effects Models (LMM)** with random intercepts for towns:
   $$Y_{ijs} = \beta_0 + \beta_1 \text{Truth}_{ijs} + \sum_{k=1}^6 \beta_k \text{Knob}_{k,ijs} + \sum_{k=1}^6 \gamma_k (\text{Truth}_{ijs} \times \text{Knob}_{k,ijs}) + u_s + \epsilon_{ijs}$$
   where $u_s \sim \mathcal{N}(0, \sigma_u^2)$ is the town-level random effect.
3. Standard errors are clustered at the town level.

---

## 7. Diffusion Spread Metrics (Secondary Outcomes)

In addition to individual belief, the runner records how far the rumor diffuses through the town social network:

1. **Transmission Rate (1-Hop Spread):**  
   The proportion of First-Hand Listeners who actively mention the concert to their Second-Hand partner during Scene 3:
   $$\text{Transmission Rate} = \frac{\sum_{i=1}^6 \mathbb{I}(\text{Partner told about concert})}{6}$$
2. **Evidence Transmission Rate:**  
   Among First-Hand Listeners who checked the poster (`GO`), the proportion who explicitly transmitted the ground-truth noticeboard content to their partner:
   $$\text{Evidence Transmission Rate} = \frac{\sum_{i \in \text{Checkers}} \mathbb{I}(\text{Noticeboard text quoted})}{N_{\text{Checkers}}}$$
3. **Check Rate ($5 Trade-off):**  
   The overall proportion of listeners who chose `GO` versus `SKIP`, reported separately for First-Hand listeners (Scene 2) and Second-Hand listeners (Scene 4).
