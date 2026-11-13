# Two-source probes (Probes 1 and 2)

Branch `feat/two-source-probes`. Everything here was built before main-run results exist. The
only missing input is the list of 10 probe DNAs, which comes from the frozen main analysis.

## What is safe

- **Main run:** no main-run generation file changes. The 8 fingerprinted modules
  (`artifacts`, `budget`, `config`, `contracts`, `providers`, `runner`, `scoring`,
  `simulation_artifacts`) and `configs/main_config.json` are byte-identical to `main`.
  - Sealed shards, resume and the last main shard are therefore unaffected.
  - The branch can merge whenever the team likes.
- **Changed files:** `cli.py` gains new commands, and `scripts/run_until_done.py` gains a new
  flag. Neither file is fingerprinted, and existing commands behave as before.
- **Probe fingerprint:** probe towns record their own fingerprint, which is the 8 main files
  plus `probe_artifacts.py`, `probe_config.py` and `probe_runner.py`.

## Design as implemented

The design follows docs/01–04.

- **Towns:** 14 agents per town, made of 2 scripted sources and the main study's 12 listeners
  with the same 6 catch-up pairs and Latin-square layouts.
- **Sources:** both sources are scripted. Their departure lines are inserted word for word, so
  sources make no model calls and keep no history.
- **Source DNAs:** Source 1 carries the probe DNA, which is a main cell's knobs.
  - In Probe 1, Source 2 has the same DNA.
  - In Probe 2, Source 2 is the anti-agent, with `flip_all` (all 6 factors),
    `flip_social` (closeness and authority) or `flip_demographics` (gender and age) flipped.
- **Parker and speaking order:** both are counterbalanced on independent bits of the seed.
  Each (model, configuration, DNA) block of 39 seeds splits 20/19 on each, and the two cross.
  - Parker (persona 14) plays Source 1 in half the towns and Source 2 in the other half.
  - The layout's seat-0 persona plays the other source.
- **Departure lines:**
  - Consensus configurations are positional: the first speaker uses the main departure line
    and the second speaker reinforces it, so "too" and "that same poster" always follow the
    first speaker.
  - Conflict configurations are role-based: the liar uses the main line and the truth-teller
    the contradicting line.
- **Listener contexts:** they describe both sources, using the main knob lines, in speaking
  order. The Scene 3 cue names both sources. Scenes 2–5 are otherwise the main ones.
- **Judge target** (stored with each town and its grading items):
  - the fake artist for consensus lie and every conflict configuration;
  - the real artist for consensus truth, where both sources announce it.
- **Groups:** a group is one (model, probe, DNA, seed) holding its 3 configurations. Groups
  are never split across shards, like main-run twin pairs.
- **Sharding:** the round robin is stratified by model, probe, artist, Parker role and order,
  so each shard is near 50/50 on its own.
- **Size:** with 10 DNAs there are 4,680 towns, which is 1,170 per probe per model and
  780 per shard across 6 shards.

## Commands

Previews read no keys and make no calls.

```sh
# Offline demo: one group per probe per model, synthetic replies, full replay audit
truth-discount probe-demo --probe-spec configs/probe_spec.placeholder.json --output outputs/probe-demo

# Zero-call preview of one shard (counts only)
truth-discount probe-simulate --probe-spec configs/probe_spec.json --providers configs/providers.actor.json \
  --all-seeds --shard-count 6 --shard-index 0 --output outputs/probe-owner-0 --summary

# Paid smoke test on the placeholder DNAs (pilot cells 1, 30, 46, 62): 48 towns, about $0.20
truth-discount probe-simulate --probe-spec configs/probe_spec.placeholder.json \
  --providers configs/providers.actor.json --seeds-per-dna 1 --output outputs/probe-smoke \
  --ledger outputs/ledgers/probe-smoke.jsonl --budget-usd 1 --max-concurrent-towns 6 \
  --execute --spending-authorized

# One real shard, unattended (same recovery wrapper as the main run)
python scripts/run_until_done.py --probe-simulate --probe-spec configs/probe_spec.json \
  --providers configs/providers.actor.json --all-seeds --shard-count 6 --shard-index 0 \
  --output outputs/probe-owner-0 --ledger outputs/ledgers/probe-owner-0.jsonl --budget-usd 5 \
  --max-concurrent-towns 6 --regenerate-failed --execute --spending-authorized

# Read-only status across shards
truth-discount probe-status outputs/probe-owner-0 outputs/probe-owner-1
```

Execution needs the same explicit `--execute`, `--spending-authorized`, ledger and cap as the
main run. Each shard uses its own ledger.

## On Sunday

0. Before anything else, the team settles the open two-mayor question under "Decisions for
   the team". If the team picks option 1, the code change and tests must land before step 2.
1. In `configs/probe_spec.json`, fill in the DNA selection:
   - set `dna_selection.status` to `final`;
   - list the 10 main cell IDs;
   - copy the frozen selection rule from the analysis plan into `rule`.

   The spec refuses to build towns until then, and a final spec needs exactly 10 DNAs and a rule.
2. Commit the spec. Everyone checks out the same commit.
3. Each owner runs the zero-call preview for their shard index, checks the counts, then runs
   the shard.
4. `probe-status` across all six should read `generation_complete`.

## Paid smoke test (13 Nov 2026)

The smoke test used the placeholder DNAs (pilot cells 1, 30, 46 and 62), both models, all
6 configs and 1 seed: 48 towns.
- **Result:** all 48 completed, and `probe-status` reads `generation_complete` with the full
  replay audit passing.
- **Timeouts:** 4 Qwen requests hit the 60 s timeout during a DeepInfra latency spike. They
  were priced from billing at $0.000325, and the 5 affected towns were regenerated with
  `--resume --regenerate-failed`.
- **Cost:** $0.2206 including the failed attempts, which matches DeepInfra billing to the token.
  - Per town: $0.0023 on DeepSeek and $0.0057 on Qwen, about $0.0040 on average.
  - Full probes (4,680 towns): about $19 of actor calls, about $3.10 per shard.
- **Dialogue:** listeners hear both departures in order and report the conflict sensibly,
  e.g. "Kaelen Cross is playing Saturday. Parker guessed wrong, but Alex was right."

## Decisions for the team

These are drafts, and nothing above depends on them being final, except the first item.

- **Two mayors (open: needs team discussion).** When the DNA has `authority = mayor`, both
  sources are described as "the town's elected mayor" in all 3 Probe 1 configs and in Probe 2
  `flip_demographics`.
  - That happened in 16 of the 48 smoke towns.
  - A listener noticed: "Wait, hold on—Parker *and* Alex are both the mayor? That's a weird
    mix-up."
  - **Status:** not decided. The code currently uses the verbatim wording, which is option 2.
  - This is an incoherent world rather than a manipulation, so the team must decide before the
    probe DNAs are frozen on Sunday. Options:
    1. Give the second identical-authority source an equal-status distinct role, such as
       "the town's elected council president". This needs one new listener line.
    2. Keep it verbatim and report it as a limitation.
    3. Exclude mayor DNAs from the top 10.

- **Two-source context wording** (`templates` in the spec): "Apart from A and B…", one "About"
  paragraph per source in speaking order, "A and then B stand up, share news about a concert…".
- **Truth-teller's line when it speaks first:** "just so you know about that poster" assumes the
  poster was already mentioned. Either keep it verbatim from docs/03, as now, or add a
  first-position variant.
- **Probe judging:** the target is stored as above, but judge-saved reads main-run collections
  only. Scoring probe towns needs a small reader for `truth-discount-probe-simulation-0.1`
  bundles, with the frozen judge profile.
- **Budget:** each probe shard is about 780 towns, about $3.10 of actor calls at the
  smoke test's measured cost. A $5 per-shard cap leaves room for retries. Judging is extra:
  about 56k calls, around $8 on Haiku.

## Not yet done

- **Auto-reconcile:** `scripts/reconcile_unknowns.py` reads main-run collections only. In a
  probe run, a timeout's unclear charge therefore stops the wrapper for a person, as main-run
  timeouts already do.
- **Judging and analysis of probe towns:** these come after the main judge and analysis plan
  are frozen.
