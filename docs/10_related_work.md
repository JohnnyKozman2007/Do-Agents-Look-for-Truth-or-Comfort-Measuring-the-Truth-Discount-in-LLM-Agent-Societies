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
