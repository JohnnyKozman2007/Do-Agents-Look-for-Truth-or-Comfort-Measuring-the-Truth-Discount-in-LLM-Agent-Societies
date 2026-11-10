# Do Agents Look for Truth or Comfort?

This project studies how source traits and verification affect belief in LLM agent societies. The experimental specification and pilot configuration live in `docs/` and `configs/`.

The runner implements the five-scene pilot with synthetic fixtures and explicitly authorized provider execution. It records prompts, responses, isolated agent histories, checking decisions and usage receipts. The offline checks below make no model calls. Fixture and mocked scores are software checks, not empirical findings.

## Local check

Use Python **3.11 or later**. The runtime and tests use the standard library. No package installation or credentials are required for these commands, run from the repository root:

```bash
bash scripts/offline_check.sh
```

The script runs the tests, executes four synthetic towns in a temporary directory, audits their saved bundles and removes the temporary files. Set `PYTHON=python3.11` if needed.

To retain a demo for inspection, choose a new output directory:

```bash
PYTHONPATH=src python3 -m truth_discount.cli validate
PYTHONPATH=src python3 -m truth_discount.cli demo --output outputs/demo-mixed
PYTHONPATH=src python3 -m truth_discount.cli summarize outputs/demo-mixed
```

The configuration plans **624 towns**: 312 per model. A demo executes **four fixture towns**, one rumor/truth pair under each configured model key. Those keys label fixtures here and do not invoke the named models.

See [the offline runner guide](docs/05_offline_runner.md) for the manifest command, output files, parser behavior and remaining work. The study specification remains in [experimental design](docs/01_experimental_spec.md), [personas and world](docs/02_personas_and_world.md), [prompts](docs/03_prompts_and_templates.md) and [metrics and judge](docs/04_metrics_and_judge.md).

## Development provider integration

The scripted broadcast, versioned replay, native provider adapters, budget guard and resume checks are integrated. Later smoke-test fixes preserve the analysis and rejudge commands together. Mocked HTTP tests verify software behavior without consuming credits. Validate actual pilot claims against the saved run manifests and receipts.

See [live-pilot gates and commands](docs/06_live_pilot.md) and [published rates and budget scenarios](docs/07_pricing_and_budget.md). `configs/providers.example.json` intentionally leaves execution unapproved. The separate pilot provider file records the team's selected settings. Neither a configuration file nor a code review authorizes spending by another operator.

After a run, [pilot analysis and the judge audit](docs/08_analysis_and_audit.md) produce descriptive tables and measure human/automated-label agreement. The generated 64-cell main study remains a separate future plan, not a completed pilot result or execution instruction. See the [writing handoff](docs/09_writing_and_analysis_handoff.md), [related work](docs/10_related_work.md) and [bibliography](paper/references.bib) before framing the paper's contribution.

Use the [finished-pilot workflow](docs/11_finished_pilot_review.md) to check the exported plan, missing towns and saved costs before analysis. It also explains the separate smoke/main-batch coverage and human-label handoff.

The [judge-validation workflow](docs/12_judge_validation_plan.md) prepares an offline inventory and separate blind calibration sample that includes rule-coded omissions. The proposed controls remain unapproved and make no model calls.

## Generation without a judge

The [staged collection and handover guide](docs/13_deferred_judging_and_handover.md)
describes `simulate`, `simulation-status`, `judge-saved`, `judge-status` and
`compare-judges`. Simulation-only output preserves all twelve phone calls with
pending evaluations; later judge profiles save separate, source-bound results.
The existing actor prompts, phone branching and historical scored bundles are
unchanged.

The 9,984-town main plan can be allocated into six disjoint shards of 1,664 towns,
keeping truth/rumour pairs together. Resume preserves completed generations,
original ledger identity/cap and every archived attempt. Different native judge
profiles can score the same sealed phones without generating towns again.

Candidate profiles in `configs/judges/` are deliberately unapproved and have no
verified prices or account access. The new commands preview by default; paid
execution requires separate explicit authority. Offline tests and synthetic
demonstrations do not establish a real smoke test, completed human audit, main
collection or paper result.
