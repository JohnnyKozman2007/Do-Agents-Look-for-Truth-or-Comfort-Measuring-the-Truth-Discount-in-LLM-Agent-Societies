# Do Agents Look for Truth or Comfort?

This project studies how source traits and verification affect belief in LLM agent societies. The experimental specification and pilot configuration live in `docs/` and `configs/`.

The current runner implements the five-scene pilot with **synthetic fixtures only**. It records prompts, responses, isolated agent histories, checking decisions and descriptive scores. It has no live provider adapter and makes no model API calls or credit purchases. Fixture scores are software checks, not empirical findings.

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

PR6's scripted broadcast and diagnostics are integrated on the feature branch. The runner now supports versioned replay, native provider adapters and a durable budget guard. Mocked HTTP tests verify the integration without consuming credits. No real model access, paid pilot or empirical result is claimed.

See [live-pilot gates and commands](docs/06_live_pilot.md) and [published rates and budget scenarios](docs/07_pricing_and_budget.md). `configs/providers.example.json` intentionally leaves execution unapproved. The credit-use hold remains.
