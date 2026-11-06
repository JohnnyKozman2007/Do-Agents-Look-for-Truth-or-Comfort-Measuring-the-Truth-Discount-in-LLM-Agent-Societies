# Offline pilot runner

The runner implements the single-source, five-scene pilot from `configs/pilot_config.json` version 1.1.0. It currently accepts only synthetic fixture backends. It does not read provider credentials, submit model requests or use credits. Every saved town carries `evidence_kind: synthetic_fixture` and `study_eligible: false`.

## Commands and run counts

Use Python 3.11 or later from the repository root. The checkout commands use only the standard library and need no installation.

```bash
bash scripts/offline_check.sh
```

This runs the unit tests, a four-town demo and an audit of that demo. The script cleans up its temporary directory. To select another interpreter:

```bash
PYTHON=python3.11 bash scripts/offline_check.sh
```

The individual commands below keep their outputs for inspection. Use new paths because the manifest and demo commands refuse existing destinations.

```bash
PYTHONPATH=src python3 -m truth_discount.cli validate
PYTHONPATH=src python3 -m truth_discount.cli manifest --output outputs/pilot-plan.jsonl
PYTHONPATH=src python3 -m truth_discount.cli demo --output outputs/demo-mixed
PYTHONPATH=src python3 -m truth_discount.cli summarize outputs/demo-mixed
```

Pass `--config path/to/pilot_config.json` to `validate`, `manifest` or `demo` to use an explicit configuration. `summarize` reads each saved town's configuration.

`validate` checks the configuration. `manifest` writes the planned 624 town records without executing them: four cells, 13 layouts, three repetitions and two truth conditions for each of two model keys. This gives 312 towns per model and 312 matched pairs overall. Each cell has a 20/19 artist split, with the majority changing between consecutive cells.

`demo` executes only four synthetic towns: both conditions for cell 1, layout 0 and repetition 0 under each model key. It uses the same fixture backend for both keys. The default `mixed` mode includes GO and SKIP decisions. `--mode all_skip` exercises the no-check path, and `--mode silent` exercises non-mention. Use a separate output directory for each invocation. These fixtures do not measure differences between the configured models.

## Scene execution and information access

1. The source's departure line is scripted, so the runner inserts it word for word without a model call. Rumor and truth twins therefore hear identical wording apart from the artist name. The source's prompt never includes its own reliability description.
2. Six first-hand listeners independently choose GO or SKIP. GO deducts $5 from that listener's $40 budget and adds the official noticeboard observation to their history.
3. Six fixed pairs have four spoken catch-up turns: a scripted second-hand opener followed by three generated responses. A complete town makes 18 catch-up generation calls. The second-hand listener receives only their partner's spoken replies, including any evidence the partner chooses to share.
4. Six second-hand listeners make their own checking decisions. Only their own GO adds a direct noticeboard observation to their history.
5. Each listener follows the evening phone funnel. The runner checks the listener's reply for a concert or either artist name. A mention at steps 1–4 leads to the follow-up at step 5 and caller wrap-up at step 6. There is no generated response after step 6. Four replies without a mention produce a runner-assigned `NOT_MENTIONED`, without a judge call. `scene_5_mention_step_confirmed` keeps the mention step only when the judge's label is not `NOT_MENTIONED`, so a reply that just repeats the step-4 question does not count as a mention.

Agent histories remain separate. Shared background uses the configured alphabetical artist order. The judge receives the rubric, the announced artist and the phone dialogue. The runner does not add source traits, the truth condition, checking actions or private histories to that input. A listener can still disclose those facts in their own dialogue.

## Saved files

Each town gets a directory named after its run ID. The runner refuses to overwrite an existing town directory.

| File | Contents |
| --- | --- |
| `town.json` | Run metadata, scene status, histories, decisions, transcripts, evaluations and metrics. Contains private condition information. |
| `config.json` | Exact configuration snapshot for the town. |
| `trace.jsonl` | Callback requests, settings, responses, request hashes, statuses and elapsed times. Contains private prompts. |
| `transcript.md` | Readable broadcast, catch-up and phone conversations. |
| `judge_requests.jsonl` | Judge messages and settings with opaque request IDs. Excludes the private run and condition crosswalk. |
| `judge_crosswalk_PRIVATE.jsonl` | Maps judge request IDs to run, seat, cell and truth condition. Keep this separate from evaluator inputs. |
| `listener_scores.csv` | Listener labels and scores with run metadata and fixture markers. |
| `manifest.json` | File hashes, source-file hashes, Python version and platform. |

The judge export is a provider-neutral input file. It is not an implemented provider batch submission. Callback counts describe synthetic invocations. Provider API calls remain zero, and actual provider identity, token usage and billed cost remain null.

`summarize` audits saved file and request hashes, run-plan identity, judge-input projection and recomputed metrics. It makes no new generation calls. Hash checks and replay do not establish the semantic correctness of a judgment.

## Decisions, failures and scores

The decision parser follows the prompt playbook: it uses the first whole-word GO or SKIP, ignoring case. A returned string with neither token, including an empty string, takes the documented operational SKIP fallback. The trace preserves the raw text and marks `parse_status: malformed_fallback_skip`. Metrics distinguish `n_valid_decisions`, `n_decision_fallbacks` and `n_operational_decisions`.

A timeout, callback exception or invalid response object is a failure, not an operational SKIP or a non-mention. The runner saves the failure state and partial evidence. When a callback fails during a concurrent phase, the runner waits for the other started calls in that phase before saving. It does not retry calls. Malformed judge output keeps an invalid evaluation without inventing a belief label.

Descriptive belief scores map FACT and CHECKED_TRUE to 1, UNCERTAIN to 0.5, and SKEPTICAL and CHECKED_FALSE to 0. NOT_MENTIONED contributes to a separate omission rate and leaves the conditional belief denominator. An all-omitted town therefore has an undefined conditional belief mean, represented as null. The summary also reports the specified 0 and 0.5 omission imputations, checking rates and matched truth-minus-rumor differences. Missing or invalid evidence leaves affected metrics undefined.

## Remaining work and method limits

Real execution still requires provider adapters, validation of model and judge access, supported settings, usage accounting and explicit funding authorization. The credit-use hold remains in place. The configured batch flag and model identifiers do not establish a working provider integration.

This implementation does not run the full 64-cell study or two-source probes. It does not implement LMM estimation, Holm correction, the human judge audit or empirical reliability analysis. The optional post-scoring manipulation check is also outside this version. Its evidence flag counts a first-hand listener who checked the board and then names the real artist and the board in one catch-up line. It is a keyword rule, not a semantic judgment.

The existing method documents make stronger claims about complete bias cancellation, deterministic model behavior and immunity to omission bias. The offline implementation does not establish those claims. Its `seed_id` identifies the planned layout, repetition and artist assignment, not a provider random seed. The fixture outputs establish software behavior only. Keep these method questions separate from implementation validation and resolve them before interpreting real results.
