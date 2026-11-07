# Writing and analysis handoff

Prepared 7 November 2026 from the repository and current design-document snapshot. This is a proposed writing and analysis brief. It does not register hypotheses, change an experiment already running, or report pilot findings.

## Research question and contribution

A defensible question is: **How do source profiles influence optional verification, expressed stance and the transmission of claims and evidence in a controlled LLM dialogue setting?**

The contribution to evaluate is the joint empirical measurement of these outcomes under matched truth/rumor runs and declared source profiles. The eventual paper needs measured results and comparison with close prior work before claiming an additional contribution. Social simulation, source bias, misinformation persuasion and costly verification already have relevant literature. The team has not established that any one of these ingredients is new.

The current setup offers verification at one fixed simulated price, $5 from a $40 character budget. It does not vary the verification price or establish an effect of actual financial loss. A causal cost-response claim would need a separately specified comparison.

## What the truth discount means

The configured score subtracts the rumor town's mean expressed belief from its matched truth town's mean. The main conditional mean excludes valid `NOT_MENTIONED` judgments. The two declared silence sensitivity scores instead assign omissions 0 or 0.5. Invalid, failed or missing judgments are not omissions and must remain missing.

A small difference can arise when agents endorse both claims, reject both, express uncertainty, omit the topic or lack verified evidence. It does not identify a preference for social comfort, dishonesty or an internal value. Report each condition's stance distribution, omission rate and valid verification decisions alongside the paired difference.

GO/SKIP decisions identify recorded direct checking. A partner's GO does not prove the partner communicated the evidence. The existing concert-name and board-name checks are keyword diagnostics, not semantic adjudication of evidence transmission. Comparisons restricted to voluntary checkers are descriptive because checking can itself respond to the source profile.

## Pilot scope and future factorial study

The pilot has four profiles, 13 seating layouts, three repetitions and two truth conditions. That is 312 towns per model and 624 across the two configured agent models. It is not the full 64-cell experiment.

| Pilot comparison | What varies | Interpretation |
| --- | --- | --- |
| Cell 3 versus Cell 2 | Closeness | Local closeness comparison at the shared low-reliability citizen profile and fixed demographics |
| Cell 4 versus Cell 2 | Authority | Local authority comparison at the shared stranger/low-reliability profile and fixed demographics |
| Cell 1 versus Cell 2 | All six attributes | Bundled profile comparison, not a separate estimate for every attribute |

The generated 64-cell main configuration is a future plan with 4,992 towns per model. Its existence does not establish collection, funding, a completed factorial evaluation or authorization to run it. The ten planned confirmatory contrasts and multiplicity policy need a dated analysis specification before that study. Pilot tables and exploratory model fits do not implement or replace those ten tests.

## Which version should the paper describe?

Use the actual run manifest, configuration, prepared prompts, provider settings and code revision for the experiment being reported. Cite an immutable repository revision and explain any departures from the earlier Google Doc. Do not silently combine the two twin designs below.

| Source | Twin construction |
| --- | --- |
| Google Doc, `Updated Personas & Prompts`, modified 4 November 2026 | The same source announcement in both twins, with the poster changing |
| Repository pilot config and runner reviewed 7 November 2026 | The rumor announces the fake artist and the truth twin announces the real artist, with the same real-artist noticeboard in both |

The latter is the implemented configuration, but the actual pilot exports must confirm what ran. The old Google Doc also retains a tab explicitly marked superseded. Its content is not a current implementation specification. The team should confirm the intended paper description and retain a dated design reconciliation rather than edit history after seeing outcomes.

Aarushi reports that the smoke test passed after runner edits and that the pilot is running. The reviewed repository contains those code changes and a pilot provider manifest. That report does not supply the raw pilot outcomes, receipts, exact executed configuration or human-audit results. No empirical result follows from the offline checks in this branch.

## Analysis checks and interpretation

- Analyze one coherent configuration/provider/evidence population at a time. Keep synthetic fixtures and mocked provider responses distinct from actual development collection.
- Preserve complete truth/rumor pairing. Report missing twins, incomplete runs, invalid judgments, missing outcomes and each denominator. Use all completed towns for descriptive condition-level GO and transmission tables rather than selecting only pairs with usable belief scores.
- Resample matched twin pairs for paired outcome intervals. Do not count twelve listeners as twelve independent experimental replicates. Cell contrasts use the stated resampling rule and are exploratory.
- Keep the declared town-intercept mixed fit identifiable as exploratory. It does not automatically account for dependence across matched twin towns. Pair-clustered OLS is an additional sensitivity analysis, not a retrospectively registered confirmatory procedure. Singular, nonconverged or nonfinite fits need explicit status.
- Retain original judge outputs. Detect `rejudged.jsonl` as a separate artifact and record its hash. The default analysis does not apply it. Any repaired-label analysis requires an explicit policy, separate reporting of first-pass and repair results, and the additional judge receipts and costs.
- Generate the human audit from frozen source inputs. Raters receive the announced artist, dialogue, definitions and blank label fields. Keep source IDs, model, cell, truth condition and judge labels private. Dialogue itself may still reveal contextual cues, so metadata masking does not guarantee perfect blinding.
- Report agreement with the judge and between human raters. The judge is not a gold-standard human answer. A kappa target is a diagnostic threshold, not an automatic authorization to change models or relabel outcomes. Report the sample strata and any sampling restrictions.
- Preserve raw bundle receipts, archived partial attempts and reconciliation separately. A final run folder without earlier attempts cannot establish total experiment cost.

## Writing workflow

No LaTeX project, manuscript or Overleaf link was found in the tracked repository reviewed for this handoff. That does not rule out a separate shared workspace. Confirm its location with the coordinator before creating a duplicate.

The introduction can start with the practical problem, close prior work, the specific unresolved comparison being tested and the planned operational measurements. Put dataset and model counts in Methods only after checking the actual exports. A preliminary abstract can describe the question and design, but should leave findings unwritten until validated analysis exists. The person assigned the introduction and abstract should retain ownership of those sections.

The accompanying related-work note and bibliography distinguish recommended foundations from the papers that actually inspired the project. Only the original project author can confirm that historical motivation.
