# Targeted human audit of the Gemini labels

Goal: humans label a targeted sample of phone calls blind, then we measure how often Gemini agrees
(agreement and Cohen's kappa; target kappa >= 0.85).

## What you do (raters)

You only need Python 3. No other install, no data download.

1. Pull this branch and pick your sheet: `audit/targeted/sheets/rater-N.csv`
   (the team decides who is N; one sheet per person, 5 sheets).
2. Label in the terminal (resumable, saves after every call):

   ```
   python scripts/targeted_audit.py label audit/targeted/sheets/rater-N.csv
   ```

   - You see the announced artist and the transcript. Type `1`-`6`, then optionally a note:
     `1`=FACT `2`=UNCERTAIN `3`=SKEPTICAL `4`=CHECKED_TRUE `5`=CHECKED_FALSE `6`=NOT_MENTIONED
   - Example: `5 poster named the other artist` or `3 relay of other artist`.
   - `s` skips a call, `q` saves and quits. Re-run the same command to resume.
   - The tool never shows Gemini's label. It is not in your sheet.
   - Or edit the `human_label` column of the CSV by hand (exact label names, upper case).
3. Read `audit/targeted/labeling_instructions.md` first (the label definitions).
4. Check progress: `python scripts/targeted_audit.py status`
5. When done, commit ONLY your own sheet and push:

   ```
   git add audit/targeted/sheets/rater-N.csv
   git commit -m "audit: rater N labels"
   git push
   ```

**Do not open `audit/targeted/PRIVATE/`.** It holds Gemini's labels and would bias you.
Do not label other people's sheets, and do not discuss labels until everyone is done.
Do NOT run `build` (it would redraw the sample and discard labels).

## How the shards work

- The sample is 360 calls, picked on purpose (not random): UNCERTAIN 80, NOT_MENTIONED (Gemini) 60, FACT 50,
  CHECKED_FALSE / CHECKED_TRUE / SKEPTICAL 40 each, NOT_MENTIONED (keyword rule) 20,
  broken-or-retried Gemini answers 30.
- Calls are dealt round-robin into 5 sheets, so every sheet has the same mix of all categories, both agent models,
  first/second-hand listeners and truth/rumor towns. No one gets "all the hard ones".
- 72 of the 360 calls (20%) are also given to a second person (rater N and rater N+1, wrapping 5 -> 1).
  That is why the sheets have 87, 86, 90, 81 and 88 rows (432 rows = 360 + 72 repeats).
  Those repeats measure whether two humans agree with each other.
- Each sheet's calls are shuffled and given neutral ids (`T0001`...), so you can't tell the category from the id.
- Same seed (2027) always gives the same sample. Different raters' sheets are separate files, so pushing causes no merge conflicts.

## Scoring (whoever coordinates, after all 5 sheets are pushed)

```
git pull
python scripts/targeted_audit.py score
```

Writes `audit/targeted/results/` : `report.md`, `results.json`, `disputes.csv`, `scored_items.csv`.
- Calls where the two raters disagree are listed in `disputes.csv` and left out of the Gemini comparison until resolved.
  Resolve them with a CSV `audit_id,label` and run `score --adjudicated resolved.csv`.
- "Weighted" numbers rescale the deliberate over-sampling back to all 119,808 calls. Quote those, not the raw ones.

## Rebuilding (only the person who has `outputs/judged-main/`)

```
python scripts/targeted_audit.py build --raters 5 --overlap 0.2 --force
```

Options: `--scale 2` (double every quota), `--quotas '{"UNCERTAIN": 120}'`, `--seed`, `--priority-share`.
