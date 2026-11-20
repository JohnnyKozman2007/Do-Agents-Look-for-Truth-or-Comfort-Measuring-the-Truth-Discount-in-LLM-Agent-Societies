# Mini study: P(GO) for new models, and the checking-price sweep

A cheap way to measure how often a new model pays to check a rumor (**P(GO)**). It reuses the main study's
first-hand decision prompts instead of running whole towns. This folder holds the code, the prompts and every
result collected so far for five GPT and Claude models.

- **Mini study:** 576 first-hand prompts at the main study's $5 bus fare, answered by each model.
- **Price sweep:** the same 576 prompts at five fares (free, $1, $5, $15, $35), to see how checking depends on cost.

DeepSeek-V4-Flash and Qwen3.8-Flash are not in the sweep yet. See [Adding DeepSeek and Qwen](#adding-deepseek-and-qwen).

## Design

- **Prompts.** Each prompt is the exact message a first-hand listener received in the main simulation: a poster with a
  rumor and a choice to pay the bus fare and check it (GO) or not (SKIP). These prompts are taken word for word from
  saved `agent_histories.json` files. Before seeing a poster, first-hand listeners get the same prompt whichever model
  drives the town, apart from the artist's name.
- **Cue combinations.** A 2^(6-1) half fraction of the six cues (reliability, closeness, authority, wealth, gender,
  age) gives 32 cells. There are 3 town layouts per cell, picked to cover the listener personas, and 6 first-hand
  seats per layout: 32 x 3 x 6 = **576 prompts**. One twin is used per prompt (the artist alternates), with one answer per prompt.
- **Parsing.** The answer is the first GO or SKIP word found. Anything else counts as SKIP, the same rule the main
  study uses. No answer was unreadable in any run so far.
- **The price sweep changes only the fare text**, in the two places the prompt mentions it. The weekly budget stays $40.

## Results so far

### P(GO) at the $5 fare (576 prompts per model)

| | GPT-6.1 Terra | Claude Sonnet 5.5 | GPT-6.1 Sol | GPT-6 Luna | Claude Opus 5.5 | DeepSeek-V4-Flash* | Qwen3.8-Flash* |
|---|---|---|---|---|---|---|---|
| Overall | 65% | 20% | 4% | 99% | 18% | 47% | 92% |
| Reliability effect (good minus poor record, pp) | -20 | -25 | -1 | 0 | -10 | +52 | +17 |
| Closeness effect (close friend minus stranger, pp) | +31 | +21 | +3 | 0 | +11 | +13 | +12 |

\*DeepSeek and Qwen numbers come from the same 576 decisions in the **main-study data**, not from a new run.
Full tables, including the other cues and how often models agree, are in [runs/comparison.md](runs/comparison.md).

### P(GO) by bus fare (price sweep, 2,880 answers per model)

| Model | Free | $1 | $5 | $15 | $35 | Fare where half still check |
|---|---|---|---|---|---|---|
| GPT-6 Luna | 100% | 100% | 99% | 68% | 25% | $21.8 |
| GPT-6.1 Terra | 100% | 100% | 65% | 3% | 0% | $6.1 |
| GPT-6.1 Sol | 100% | 100% | 4% | 0% | 0% | $4.2 |
| Claude Sonnet 5.5 | 100% | 99% | 20% | 0% | 0% | $3.6 |
| Claude Opus 5.5 | 97% | 99% | 18% | 0% | 0% | $3.2 |

The "half" fare comes from a logistic fit of GO on log(1 + fare). The tested fares are far apart, so treat it as rough.

**Cue effects appear only near each model's tipping price.** At free, $1 and $35 the reliability and closeness
effects are about 0 for every model. At $5 they are large for Terra, Sonnet and Opus. At $15 only Terra still shows
them (reliability -6, closeness +7). Luna shows no cue effect at any fare. So the size of a cue effect at a single
fare partly reflects where that fare sits relative to the model's own threshold.

Full tables with 95% CIs (bootstrap over the 13 listener personas) are in
[runs/sweep/sweep_report.md](runs/sweep/sweep_report.md). Charts are in `runs/sweep/sweep_report.html`: open it in a
browser.

### What was run

| Model | Endpoint | Settings |
|---|---|---|
| `gpt-6.1-terra`, `gpt-6.1-sol`, `gpt-6-luna` | OpenAI Chat Completions | default temperature and reasoning, `max_completion_tokens` 2000 |
| `claude-sonnet-5-5`, `claude-opus-5-5` | Anthropic Messages | default settings, no extended thinking, `max_tokens` 2000 |

All 14,400 calls (5 models x 5 fares x 576) succeeded. Each run's exact arguments are in its `run_args.json`.

## Folder layout

| Path | What it is |
|---|---|
| `mini_study.py` | Everything in one file, with no extra packages. `build`, `run`, `analyze` and `price` are described below. |
| `compare_models.py` | Side-by-side table of all models at $5. Writes `runs/comparison.md`. |
| `run_sweep.sh` | The price sweep for the five GPT and Claude models. |
| `run_open_models.sh` | The full sweep (all five fares) for DeepSeek and Qwen on DeepInfra. |
| `sweep_analysis.py` | Sweep report for all models with results. Writes the files in `runs/sweep/`. Needs numpy and pandas. |
| `runs/design_full/` | The 576 prompts at $5 (`design.jsonl`), plus `design_meta.json`. |
| `runs/design_min/` | A 72-prompt version that only varies reliability and closeness, for a quick smoke test. |
| `runs/design_price{0,1,15,35}/` | The 576 prompts at the other fares. |
| `runs/<model>_full/` | $5 results: `results.jsonl` (raw answers), `decisions.csv`, `summary.csv` and `report.md`. |
| `runs/sweep/<model>_price<fare>/` | Raw answers at the other fares. |

Each line of `results.jsonl` holds `item_id`, `decision`, `parse_status`, `raw_response`, `finish_reason`, `model`
and token counts.

## How to run

Every API call is saved as soon as it comes back. Rerunning a command skips finished prompts and retries failed ones.

**Measure P(GO) for a new model** (any OpenAI-compatible endpoint, or `--provider anthropic`):

```bash
python3 mini_study/mini_study.py run --design-dir mini_study/runs/design_full --model MODEL_ID --out mini_study/runs/NAME_full --limit 5
```
```bash
python3 mini_study/mini_study.py run --design-dir mini_study/runs/design_full --model MODEL_ID --out mini_study/runs/NAME_full
```
```bash
python3 mini_study/mini_study.py analyze --design-dir mini_study/runs/design_full --results mini_study/runs/NAME_full --name "Display name"
```

The first command is a 5-call smoke test. `analyze` writes `report.md`, `summary.csv` and `decisions.csv` next to the
results, and compares them with the main study's DeepSeek and Qwen decisions. Useful `run` options:

- `--base-url`, `--api-key-env` and `--provider` pick the endpoint and the key's environment variable.
- `--reasoning-effort`, `--thinking`, `--temperature` and `--max-tokens` set the model's settings.
- `--workers` sets how many calls run in parallel.

Run `python3 mini_study/mini_study.py run -h` for the full list.

**Make a new fare version** (fares 0, 1, 5, 15 and 35 have wording ready in `PRICE_TEXT` in `mini_study.py`):

```bash
python3 mini_study/mini_study.py price --design-dir mini_study/runs/design_full --price 15 --out mini_study/runs/design_price15
```

**Rebuild the prompts from simulation data** (only if the main study changes). This needs the unzipped main-study
output folders:

```bash
python3 mini_study/mini_study.py build --data PATH/TO/main-owner-0 PATH/TO/main-owner-1 --out mini_study/runs/design_full --design full --layouts 3
```

**Rebuild the reports:**

```bash
python3 mini_study/compare_models.py
```
```bash
python3 mini_study/sweep_analysis.py
```

## Adding DeepSeek and Qwen

```bash
export DEEPINFRA_API_KEY=your_key_here
```
```bash
./mini_study/run_open_models.sh smoke
```
```bash
./mini_study/run_open_models.sh
```
```bash
python3 mini_study/sweep_analysis.py
```

- The first command (`smoke`) makes 5 calls per model. Check that the answers contain GO or SKIP.
- The full run covers all five fares, $5 included, for both models: 5,760 calls. At DeepInfra prices it should cost
  about $0.35.
- At the end the script prints the number of answers per run. Each should be 576. If one is short, run the same
  command again.
- The settings follow `configs/providers.actor.proposal.json`: DeepInfra, `reasoning_effort: none` (thinking off).
  The GPT and Claude runs used their default hidden reasoning, so keep this difference in mind when comparing the
  two groups.

## Limitations

- **First-hand GO/SKIP only.** There are no towns or conversations, so second-hand belief and the truth discount
  are not measured.
- **One answer per prompt.** Answers were not repeated, so these runs cannot show how much a model's answer varies
  from one call to the next.
- **A half fraction of the cues.** Main effects and two-cue interactions are clean (assuming no five-cue or four-cue
  interactions), but each three-cue interaction is mixed with another one.
- **Few layouts per cell.** With 3 layouts per cell, only 13 listener personas appear, so the CIs bootstrap over
  personas rather than over towns.
- **Fare wording.** Each fare comes with its own comparison ("about the price of a pack of gum"), and that wording
  may itself affect the answer.
