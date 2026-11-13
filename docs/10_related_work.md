# Related work for the pilot paper

Checked 7 November 2026 against primary papers and publisher records. These are recommended foundations and close comparisons. They are not verified accounts of which papers originally inspired the project. No empirical pilot results or exhaustive novelty conclusion follow from this review.

## Closest comparisons

| Work | Existing coverage | What our comparison would need to add |
| --- | --- | --- |
| [The Stepwise Deception: Simulating the Evolution from True News to Fake News with LLM Agents](https://aclanthology.org/2025.emnlp-main.1330/) (2025) | FUSE simulates news distortion with spreaders, commentators, verifiers and passive observers; FUSE-EVAL assesses truth deviation. Personas include demographic information, and fact-checking interventions are part of the framework. | A controlled source-cue contrast with paired claims and endogenous GO/SKIP checking, rather than roles already assigned to verification. Combining transmission, belief and checking alone is not sufficient novelty. |
| [Whose Facts Win? LLM Source Preferences under Knowledge Conflicts](https://aclanthology.org/2026.acl-long.1357/) (2026) | A controlled study of 13 open-weight models uses synthetic conflicting sources. Institutional source preferences can be reversed by repetition. Demographic controls include gender, age and titles, and an abstention extension is tested. | Optional evidence acquisition and conversational relay under source relationships and reliability. Do not claim that previous source-preference work lacks demographic controls or abstention. |
| [Verification Required: The Impact of Information Credibility on AI Persuasion](https://arxiv.org/abs/2602.00970) (2026) | MixTalk is a sender–receiver strategic communication game with verifiable and unverifiable claims. A limited-budget receiver chooses costly verification. Tournament-based policy distillation improves receiver robustness in the evaluated settings. | Controlled social-source attributes, multiple listeners and one-hop communication coupled to verification and stance. Novelty of that particular contribution remains to be established empirically. |
| [Persuasion at Play: Understanding Misinformation Dynamics in Demographic-Aware Human-LLM Interactions](https://aclanthology.org/2026.eacl-long.234/) (2026) | PANDORA compares human/LLM persuasion and demographic personas, including age, gender and geography. Its multi-agent component studies homogeneous/heterogeneous groups discussing misinformation. | Source attributes with fixed recipient personas and optional evidence acquisition. Do not present demographic misinformation simulation or belief-plus-transmission as an untouched area. |

## Recommended reading and proof limits

### Generative Agents: Interactive Simulacra of Human Behavior

Joon Sung Park, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein. 2023. [2023 arXiv paper; venue not independently checked in this review](https://arxiv.org/abs/2304.03442).

A foundation for town-style interaction and chronological memory. Believable behavior does not establish that our source-cue or verification responses model real human populations.

Read depth: Primary abstract and metadata; architecture context also present in the earlier 25 October review.

### Simulating Opinion Dynamics with Networks of LLM-based Agents

Yun-Shiuan Chuang, Agam Goyal, Nikunj Harlalka, Siddharth Suresh, Robert Hawkins, Sijia Yang, Dhavan Shah, Junjie Hu, Timothy Rogers. 2024. [Findings of NAACL 2024, pages 3326–3346](https://aclanthology.org/2024.findings-naacl.211/).

Opinion exchange, misinformation and polarization in LLM groups already have direct precedent. Their results depend on model, topic and prompts and motivate caution about treating agent output as human belief.

Read depth: Fresh primary metadata and abstract; methods and limitations also covered in the earlier 25 October review.

### The Stepwise Deception: Simulating the Evolution from True News to Fake News with LLM Agents

Yuhan Liu, Zirui Song, Juntian Zhang, Xiaoqing Zhang, Xiuying Chen, Rui Yan. 2025. [EMNLP 2025, pages 26176–26192](https://aclanthology.org/2025.emnlp-main.1330/).

Direct precedent for misinformation transmission plus checking and agent traits. The study notes scarce evolution datasets, omitted real-world influences and limits of LLM evaluation.

Read depth: Primary abstract, metadata, PDF methods including agent roles/personas, intervention and limitations.

### Whose Facts Win? LLM Source Preferences under Knowledge Conflicts

Jakob Schuster, Vagrant Gautam, Katja Markert. 2026. [ACL 2026 long papers, pages 29430–29459](https://aclanthology.org/2026.acl-long.1357/).

Strong direct precedent for social or institutional source cues changing answers. The controlled evidence-table setting and limited English/cultural scope do not establish human generality.

Read depth: Primary abstract and metadata; PDF source types, abstention section 4.4, demographic controls Appendix G and limitations.

### Verification Required: The Impact of Information Credibility on AI Persuasion

Saaduddin Mahmud, Eugene Bagdasarian, Shlomo Zilberstein. 2026. [arXiv preprint, submitted 1 February 2026](https://arxiv.org/abs/2602.00970).

The closest precedent for explicit costly verification by LLM agents. Its structured dyadic game is not a social-town source-profile experiment, but it rules out claiming that our work introduces costly verification.

Read depth: Primary abstract, metadata and PDF methods including MixTalk, budget/tool costs, three story layers and conclusion.

### Authority Bias in Language Models: Source Deference and User Agreement Are Not Interchangeable

Abhinav Rajeev Kumar, Paras Chopra. 2026. [arXiv preprint, submitted 29 September 2026; arXiv author comment reports NeurIPS 2026 acceptance, not separately venue-verified here](https://arxiv.org/abs/2609.37616).

Supports separating authority deference from sycophancy or a claimed internal preference for comfort. Mechanistic evidence covers selected open families; it is not a live town with costly evidence acquisition.

Read depth: Primary abstract, metadata and HTML discussion, limitations and conclusion.

### Persuasion at Play: Understanding Misinformation Dynamics in Demographic-Aware Human-LLM Interactions

Angana Borah, Rada Mihalcea, Verónica Pérez-Rosas. 2026. [EACL 2026 long papers, pages 5027–5053](https://aclanthology.org/2026.eacl-long.234/).

Direct precedent for demographic-aware multi-agent misinformation susceptibility and group dynamics. The authors warn that coarse personas can oversimplify people and reinforce stereotypes; their human sample is US-only.

Read depth: Primary abstract and metadata, PDF methods section 3.3, multi-agent prompts and limitations section 8.

### Don’t Trust Generative Agents to Mimic Communication on Social Networks Unless You Benchmarked their Empirical Realism

Simon Münker, Nils Schwager, Achim Rettinger. 2026. [EACL 2026 long papers, pages 1141–1151](https://aclanthology.org/2026.eacl-long.51/).

Methodological support for limiting our conclusions to this artificial agent system. Its own case study focuses on relatively active users and communication tasks; it is not a universal invalidation of all agent experiments.

Read depth: Primary abstract and metadata; PDF introduction, empirical-realism framework and scope.

## Further overlap checks

- [Simulating Misinformation Vulnerabilities With Agent Personas](https://arxiv.org/abs/2511.04697) (2025). Receiver professions/mental schemas, perceived truth and sharing are already studied. Distinguish recipient-persona effects from our source attributes.
- [Faithful to the Frame: Source-Framing Propagation in LLM-Agent Decision Workflows](https://aclanthology.org/2026.emnlp-main.1871/) (2026). Traces evidence through reasoning, belief and action; studied receivers do not deliberate or imitate one another. The evidence-to-belief/action combination alone is not novel.

## Contribution wording

A candidate contribution is a controlled empirical comparison of how source profiles relate to optional evidence acquisition, expressed stance and one-hop claim/evidence transmission under matched truth/rumor conditions. The actual results and closest baselines must determine what additional contribution the paper demonstrates.

Avoid claims that this is the first LLM social simulation, source-attribute study, demographic misinformation experiment, verification mechanism or combined belief/transmission framework. MixTalk already includes budgeted costly verification. Whose Facts Win? already studies source preferences and demographic controls. PANDORA already combines demographic personas and multi-agent misinformation discussion. FUSE already models transmission and checking roles.

The pilot is a four-profile experiment, not the completed 64-cell factorial. A fixed $5 fictional check price is not a comparison between costly and free verification. A small expressed-belief gap does not identify a comfort motive. Human-population claims require additional external validation.

The bibliography in [paper/references.bib](../paper/references.bib) supports the introduction and discussion. The [writing handoff](09_writing_and_analysis_handoff.md) records version, analysis and interpretation decisions.


---

## Update — 12 November 2026: Comprehensive Literature Discrepancy & Synthesis

### Overview of the Truth Discount Architecture

The architecture specified across `01_experimental_spec.md` through `04_metrics_and_judge.md` introduces an experimental framework designed to measure the **Truth Discount** in simulated LLM societies:

$$\text{Truth Discount} = \text{Belief}_{\text{Truth Twin}} - \text{Belief}_{\text{Rumor Twin}}$$

Its core methodology rests on several distinct innovations:
1. **Matched Truth Twins & Semantic Mirroring:** Eliminates LLM negation bias (e.g., "is playing" vs. "is NOT playing") by framing both the truth and rumor as an exciting surprise concert by two invented pop stars (**Vesper Vance** vs. **Kaelen Cross**), counterbalanced 50/50.
2. **Full $2^6 = 64$-Cell Factorial Grid:** Systematically crosses six orthogonal binary source dimensions: **Closeness** (Stranger vs. Friend), **Authority** (Citizen vs. Mayor), **Reliability** (Poor vs. Good record), **Wealth** (Poor vs. Rich), **Age** (Young vs. Old), and **Gender** (Man vs. Woman). Reliability is strictly omitted from the source's own prompt to keep source behavior identical across reliability conditions.
3. **5-Scene State Machine with 2-Layer Transmission:** Information flows chronologically from a non-interactive café departure broadcast (Layer 1, eliminating peer debate and contagion), to 1-on-1 afternoon catch-up dialogues (Layer 2), to private evening phone calls with out-of-town loved ones where belief is naturally elicited.
4. **Tangible Economic Ground-Truth Verification:** Agents operate under a \$40 weekly budget; verifying the claim requires deciding whether to spend \$5 (the price of a coffee and donut) to take a bus across town and inspect the physical Community Hall noticeboard (the objective ground truth).
5. **Independent Blind LLM Judge & Behavioral Omission Tracking:** An external frontier judge (Claude Haiku 5.5, GPT-4o, or Gemini 1.5 Pro) evaluates transcripts completely blind to source traits, experimental twin conditions, and agent verification actions. Unmentioned claims (`NOT_MENTIONED`) are reported as an independent **Omission Rate** metric with pre-registered pessimistic ($0.0$) and neutral ($0.5$) imputation bounds.
6. **$13 \times 13$ Cyclic Latin Square Sampling:** Decouples **Persona Variance** (rotating 13 neutral, mid-status personas through 13 town seats) from **Model Stochastic Variance** (3 repetitions per layout = 39 seeds per cell), analyzed using Linear Mixed-Effects Models with town random intercepts and Holm-Bonferroni corrections.
7. **Adversarial Conflict Probes:** Includes **Probe 1 (Truth Table)** testing consensus vs. conflict, and **Probe 2 (Dyadic Anti-Agent)** pitting top persuasive liars against truth-telling counterparts across full, social, and demographic factor flips.

---

### Comparative Analysis by Order of Methodological Discrepancy

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          SPECTRUM OF METHODOLOGICAL DISCREPANCY                   │
│                                                                                   │
│  [TIER 1: MAXIMUM]    Static single-prompt QA, logit reading & internal probing   │
│           │           (Zou et al., Hu & Qu, Schuster et al., Bito et al.)         │
│           ▼                                                                       │
│  [TIER 2: HIGH]       Benchmark multi-agent debate & formal graph topologies      │
│           │           (Becker et al., Chenfei et al., Mehdizadeh, Shehata & Li)   │
│           ▼                                                                       │
│  [TIER 3: MODERATE]   Persona-conditioned benchmarks & triadic QA conflicts       │
│           │           (Lei et al. "Truth or Tribe", Asch paradigms, Farr et al.)  │
│           ▼                                                                       │
│  [TIER 4: CLOSEST]    Networked agent societies & misinformation dynamics         │
│                       (Yashwanth YS, Lin et al. "CoSim", Liu et al. "FUSE")       │
└───────────────────────────────────────────────────────────────────────────────────┘
```

#### Tier 1: Maximum Discrepancy — Single-Prompt QA, Logit Probing & Mechanistic Lenses
*These studies do not simulate an interactive social world or longitudinal agent communication. They evaluate static model tokens, internal transformer activations, or isolated multiple-choice benchmarks.*

##### 1. Zou et al. (`2610.02702v2.pdf`) & Mechanistic Steering (`2609.37616v1.pdf`)
* **Prior Approach:** Zou et al. focused on mechanistic interpretability, applying the Logit Lens and Jacobian Lens (J-lens) to residual stream hidden activations to detect "silent dissent" (whether an LLM latently retains knowledge of a correct multi-hop fact while publicly conforming during debate). Similarly, Kumar & Chopra (`2609.37616v1.pdf`) fit linear steering vectors to residual streams to isolate authority bias directions on QA pairs.
* **The Truth Discount Framework:** Conducts a **macro-level behavioral and social simulation**. Instead of inspecting internal model weights or activation vectors on synthetic QA triples, the framework evaluates emergent belief through natural multi-turn conversational transcripts scored by a blind external LLM judge, tracking behavioral outcomes like costly bus trips and conversational transmission to third parties.

##### 2. Hu & Qu (`2607.05545v1.pdf`) & Qu, Fu, & Hu (`2606.01637v2.pdf`)
* **Prior Approach:** Investigated the "speaker-free floor" and harmful vs. beneficial revision using static two-read multiple-choice arbitration. Isolated text strings (e.g., *"The answer is B"*, *"Alice: It's B"*, *"Expert: It's B"*) were inserted into the prompt of a single frozen model to measure next-token log-probability flips on MMLU-Pro and BBH benchmarks.
* **The Truth Discount Framework:** Moves beyond synthetic single-token multiple-choice prompts. Agents inhabit an embodied town (**Alder Creek**), communicate in free-form natural dialogue (1–3 conversational sentences), receive information indirectly through social relationships (e.g., mayor, close friend, rich resident), and make economic decisions (\$5 bus ride) to verify claims against an objective environment.

##### 3. Schuster, Gautam, & Markert (`2026.acl-long.1357.pdf` / NeoQA)
* **Prior Approach:** Evaluated LLM source preference under knowledge conflicts by constructing synthetic tabular entity pairs (e.g., comparing attributes like birth dates from Government vs. Newspaper vs. Individual sources) and measuring output token probabilities for Option A vs. Option B.
* **The Truth Discount Framework:** Rather than presenting conflicting static tables in a single prompt to a passive model, the framework embeds information conflict into a **temporal, agent-based social ecology**. Sources possess multidimensional social standing, rumors diffuse across conversational layers (café to dyadic catch-up), and agents can actively resolve conflicts by paying to inspect an authoritative town noticeboard.

##### 4. Bito et al. (`2604.19301v1.pdf`)
* **Prior Approach:** Studied normative conformity on subjective preference questions lacking objective truth (e.g., *"Which fruit is better to display: Banana or Apple?"*) by varying the number of peer prompt statements.
* **The Truth Discount Framework:** Establishes an **objective ground truth** (the Community Hall noticeboard) and investigates an empirical claim with real-world stakes, specifically measuring whether social status causes agents to abandon empirical truth verification in favor of social comfort.

---

#### Tier 2: High Discrepancy — Multi-Agent Debate Benchmarks & Graph Topologies
*These studies involve multiple agents, but constrain interactions to rigid academic benchmarks (e.g., MMLU, GSM8K) or abstract token games rather than naturalistic community life.*

##### 5. Becker et al. (`2606.16710v2.pdf` / MINT) & Counterfactual MAD (`2606.00820v2.pdf`)
* **Prior Approach:** Becker et al. injected 10,278 synthetic misinformation passages into 3-to-5 agent multi-agent debate (MAD) setups solving academic benchmarks (CWQ, ETHICS, WinoGrande), comparing interactive debate against exposure-matched self-consistency majority voting. Similarly, `2606.00820v2.pdf` decomposed peer adoption into self-reflection instability vs. strict conformity on MMLU-Pro.
* **The Truth Discount Framework:** Prior studies test formal debate protocols where agents argue back and forth to solve multiple-choice test questions. The proposed architecture models **naturalistic rumor spreading in daily life**. To prevent peer contagion from confounding source trust, debate at the café table is strictly eliminated (the source announces and exits), forcing agents to independently weigh source credibility, choose whether to pay an economic verification cost (\$5), and transmit news downstream during ordinary social catch-ups.

##### 6. Chenfei et al. (`2608.03421v3.pdf` / ForesightSafety-TIDE)
* **Prior Approach:** Evaluated collective fact recovery using 120 synthetic physical object-movement puzzles (adapted from Hi-ToM), where 5 agents receive partial visibility windows of object movements and vote across checkpoints while a key agent injects deceptive state transitions.
* **The Truth Discount Framework:** TIDE studies formal logic and puzzle tracking (where a ball or key moved) under distributed observation windows. The proposed architecture investigates **sociological and psychological biases**: how interpersonal friendship, institutional authority, perceived wealth, demographic age/gender, and historical reliability distort belief in social rumors, using counterbalanced semantic twins rather than geometric tracking puzzles.

##### 7. Mehdizadeh & Hilbert (`2606.04197v1.pdf`) & Han et al. (`2601.05606v1.pdf`)
* **Prior Approach:** Mehdizadeh & Hilbert simulated the Naming Game across eight fixed 16-node mathematical network topologies (Mason & Watts graphs), testing how memory depth and graph clustering affect convergence on arbitrary convention letters. Han et al. tested centralized vs. distributed consensus pooling rules on fact-checked Snopes25 claims.
* **The Truth Discount Framework:** These studies analyze abstract convention coordination (picking letter A vs. B) or mathematical consensus pooling. The proposed architecture simulates a **grounded community (Alder Creek, pop. 4,000)** with structured social spaces (Maple Street Café, Community Hall), distinct occupational personas, and an explicit 2-layer social transmission pipeline (broadcast to dyadic exchange).

##### 8. Shehata & Li (`2605.10698v2.pdf`) & MIXTALK (`2602.00970v1.pdf`)
* **Prior Approach:** Shehata & Li examined cognitive loafing and the "Sovereignty Gap" in code/reasoning swarms (SWE-bench, GAIA) when an agent faces a unanimous adversarial swarm. MIXTALK evaluated game-theoretic strategic disclosure and cheap-talk tournaments where senders mix verifiable and unverifiable claims.
* **The Truth Discount Framework:** Shehata & Li focus on agentic coding and technical problem-solving under peer pressure. The proposed framework isolates everyday social psychology: whether friendship and mayoral power cause ordinary citizens to spread false local news to their loved ones without checking physical evidence.

---

#### Tier 3: Moderate Discrepancy — Persona-Conditioned Benchmarks & Stylized Conflicts
*These studies introduce agent personas or social identities, but evaluate them on static multiple-choice tests or abstract, ungrounded settings.*

##### 9. Lei et al. (`2605.01329v1.pdf` / "Truth or Tribe")
* **Prior Approach:** Studied in-group favoritism using a triadic interaction paradigm ($A_s, A_{in}, A_{out}$) across benchmark reasoning datasets (BBH, GPQA, MMLU-Pro). In-group and out-group identities were operationalized through semantic text similarity scores between DSPy-generated persona prompts.
* **The Truth Discount Framework:** Lei et al. define identity as an abstract mathematical similarity metric on QA tasks. The proposed design explicitly decomposes identity into **six distinct, real-world sociological factors** (Closeness, Authority, Wealth, Reliability, Gender, Age) in an orthogonal $2^6$ factorial design. Furthermore, agents are not choosing between two simultaneously presented benchmark options; they hear news from a neighbor, decide whether to verify it at personal economic cost (\$5), and independently decide what to tell their families.

##### 10. Minimal-Group Asch Studies (`2609.33495v1.pdf`)
* **Prior Approach:** Adapted the Asch conformity paradigm to LLMs using scripted peer confederates ($N=7$) asserting incorrect benchmark answers, manipulating in-group/out-group identity via trivial minimal-group tags (e.g., "blue group" vs. "green group").
* **The Truth Discount Framework:** Replaces artificial, scripted multiple-choice confederates with rich social relationships. Rather than testing whether an agent caves to 7 identical scripted prompts, the framework tests whether an agent trusts a close personal friend who has a poor track record vs. an authoritative mayor vs. an unknown stranger in natural dialogue.

##### 11. Farr et al. (`2511.04697v1.pdf`)
* **Prior Approach:** Evaluated responses to real-world misinformation headlines across eight static personas defined by professions (e.g., journalist, nurse) and cognitive schemas, asking models to rate belief and sharing likelihood on a 1–5 Likert scale.
* **The Truth Discount Framework:** Farr et al. probe models directly using single-turn headline rating questionnaires. The proposed framework constructs an active, multi-agent living simulation where agents converse with one another, and belief is evaluated indirectly through natural dialogue with a relative, scored by a blind judge.

##### 12. Banerjee & Moghaddas (`2610.02654v1.pdf`)
* **Prior Approach:** Measured belief adoption curves (sigmoidal adoption kernels) for unverifiable synthetic claims (e.g., tomorrow's temperature in Boston or commute duration on I-93) as a function of the number of endorsing peer agents $k \in \{0, \dots, 10\}$.
* **The Truth Discount Framework:** Banerjee & Moghaddas treat belief adoption as an abstract threshold function over peer counts on synthetic numerical values. The proposed study grounds belief in a structured human narrative (a town concert) with verifiable empirical ground truth (the noticeboard), examining how interpersonal social ties and institutional power override verifiable facts.

---

#### Tier 4: Closest Thematic Relatives, with Methodological Differences
*These papers simulate multi-agent social communities and misinformation spread, but lack the counterfactual twin design, economic verification mechanisms, or orthogonal factor isolation of the present work.*

##### 13. Yashwanth YS (`2608.02758v1.pdf` / Pluralistic Ignorance)
* **Prior Approach:** Simulated 20-agent group discussions across 100 policy scenarios where a structural majority (16 agents) privately opposed a norm but were prompted with explicit instructions (*"you want to fit in and not be the difficult one"*), measuring whether agents publicly conformed and whether a "norm entrepreneur" could trigger cascades.
* **The Truth Discount Framework:**
  1. *Absence of Instruction Demand Characteristics:* Yashwanth explicitly instructs dissenting agents to fit in. The proposed personas contain **zero compliance instructions, zero credulity traits, and zero experimental knob knowledge**; agent behavior is completely uncoerced.
  2. *Belief Formation vs. Preference Falsification:* Yashwanth studies agents who already know they disagree with a policy. The present work studies **epistemic belief adoption**—whether agents genuinely come to believe a false rumor due to source attributes.
  3. *Physical Verification & Twin Controls:* Includes an objective physical verification mechanism (\$5 bus fare) and matched truth twins, which are absent in policy debate setups.

##### 14. Lin et al. (`2605.17353v1.pdf` / CoSim)
* **Prior Approach:** Developed CoSim to model community misinformation resilience across 200 agents on small-world networks over 10 rounds. Agents were parameterized along two psychological traits: Actively Open-minded Thinking (AOT) and Political Ideology (PI), exposed to Chinese fact-checked news claims.
* **The Truth Discount Framework:**
  1. *Strict Orthogonal Factorial Control:* CoSim samples continuous distributions of AOT and PI, leaving individual agent interactions subject to stochastic network drift. The present study deploys a full $2^6 = 64$ factorial design where every single social factor (closeness, mayoralty, wealth, age, gender, reliability) is independently and strictly manipulated.
  2. *Matched Counterfactual Truth Twins:* CoSim exposes communities only to misinformation shocks and tracks aggregate recovery curves. The proposed design pairs every single rumor run with an identical **Truth Twin** run sharing the exact same random seed, persona seating, and syntax, isolating the exact mathematical "Truth Discount".
  3. *Elimination of Negation & Fandom Bias:* CoSim uses real-world news claims which carry pre-existing training biases. The present design invents fictional artists (**Vesper Vance** and **Kaelen Cross**) and counterbalances them 50/50.

##### 15. Liu et al. (`2025.emnlp-main.1330.pdf` / FUSE)
* **Prior Approach:** Modeled the macro-level gradual transformation of true news into fake news over 30 days across social networks. Agents were assigned static transmission roles (*spreader*, *commentator*, *verifier*, *bystander*) and Big Five personality traits, measuring semantic drift across linguistic dimensions.
* **The Truth Discount Framework:**
  1. *Controlled Source Manipulation vs. Uncontrolled Text Mutation:* FUSE allows news text to mutate freely like a game of "telephone" through unconstrained prompting. The proposed architecture holds the initial claim strictly identical across conditions (the exact departure broadcast script), isolating how listener belief and transmission vary based solely on the source’s social identity.
  2. *Active Verification Economics:* FUSE agents are passive text mutators. In the proposed framework, agents face a concrete economic trade-off: spend \$5 of their \$40 weekly budget to verify the fact on the noticeboard or rely on social trust.
  3. *Variance Isolation:* A $13 \times 13$ cyclic Latin Square guarantees that persona traits are mathematically decoupled from social seating, whereas FUSE relies on random network assignments.

##### 16. Borah, Mihalcea, & Perez-Rosas (`2026.eacl-long.234.pdf` / PANDORA)
* **Prior Approach:** Investigated human-LLM and multi-agent persuasion across demographic groups (gender, age, location) using 4-round debates over stance dataset claims (e.g., evaluating echo chamber behavior in homogeneous vs. heterogeneous pairs).
* **The Truth Discount Framework:** Borah et al. use 2-agent dyadic debates centered on contentious topics. The present design embeds agents in a 13-agent community setting with asymmetric information access, separating direct first-hand exposure from second-hand social transmission, and testing whether interpersonal friendship overrides empirical truth through dyadic Anti-Agent conflict modules.

---

### Methodological Comparison Matrix

| Experimental Dimension | Existing Literature (Prior 26 Papers) | The Truth Discount Framework |
| :--- | :--- | :--- |
| **Primary Metric** | Benchmark Accuracy, Conformity Rate, Logit Shifts, or Mutation Distance. | **Truth Discount:** $\Delta \text{Belief} = \text{Belief}_{\text{Truth Twin}} - \text{Belief}_{\text{Rumor Twin}}$. |
| **Claim Design & Bias Control** | Real-world news, political claims, or negation particles ("not true"), inducing real-world fandom and negation biases. | **Pure Semantic Mirroring:** Two invented pop stars (**Vesper Vance** vs. **Kaelen Cross**), counterbalanced 50/50 with zero negation words. |
| **Source Manipulation** | Single labels (e.g., "Expert", "Government") or continuous trait samplings (AOT/PI). | **$2^6 = 64$ Full Factorial Grid:** Closeness $\times$ Authority $\times$ Reliability $\times$ Wealth $\times$ Age $\times$ Gender. |
| **Source Behavioral Confound** | Source agents know their own traits and alter their tone/persuasion style accordingly. | **Blind Source Prompting:** Reliability is omitted from the source's prompt; source broadcast text is 100% identical across conditions. |
| **Social Transmission Structure** | Unconstrained network diffusion or iterative round-robin multi-agent debate. | **2-Layer Structured Flow:** Café departure broadcast (no debate/peer contagion) $\rightarrow$ 1-on-1 catch-up $\rightarrow$ Evening phone call. |
| **Ground-Truth Verification** | Passive context reading, automated fact-check prompts, or unassisted self-reflection. | **Active Economic Trade-off:** \$5 bus fare from a \$40 weekly budget to inspect the Community Hall noticeboard. |
| **Persona Confound Control** | Random persona assignment or generic non-grounded agents. | **$13 \times 13$ Cyclic Latin Square:** Every persona occupies every seat exactly once; personas have zero knob information. |
| **Belief Elicitation** | Multiple-choice options, logit extraction, or forced 1–5 Likert scales. | **Natural Dialogue via Blind LLM Judge:** Conversational phone call with an out-of-town loved one, categorized into 6 blind states. |
| **Treatment of Silence** | Non-responses discarded or arbitrarily coded as disbelief ($0.0$). | **Independent Omission Rate:** Evaluated separately, bounded by pre-registered pessimistic ($0.0$) and neutral ($0.5$) sensitivity checks. |
| **Conflict & Robustness Testing** | Single-agent peer pressure or homogeneous vs. heterogeneous pairings. | **Adversarial Probes:** Probe 1 (Truth Table: consensus vs. conflict) & Probe 2 (Anti-Agent: Liar vs. Truth-teller with systematic factor flips). |

---

### Summary of Core Methodological Contributions

1. **The Twin Counterfactual Formulation:** Where prior work measures raw persuasion or conformity to false claims, this framework isolates the specific epistemic value of truth itself by comparing identical twin runs differing only in external ground truth.
2. **Methodological Isolation of Social Confounders:** By using a Latin Square for personas, standardizing string injection order, withholding reliability from the source, and eliminating negation bias via semantic mirroring, the design isolates causal factors cleanly.
3. **Ecological Realism with Economic Stakes:** Grounding verification in a physical bus ride costing \$5 out of a \$40 weekly budget turns verification into an authentic behavioral trade-off between social credulity and costly empirical verification.
4. **Decoupling of Peer Contagion and Elicitation:** Eliminating table debate ensures first-hand choices reflect only source perception, while using unpressured evening phone calls to out-of-town relatives ensures belief measurements reflect genuine private adoption rather than conversational compliance.
