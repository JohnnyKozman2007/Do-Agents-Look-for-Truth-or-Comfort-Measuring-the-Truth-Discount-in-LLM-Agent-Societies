#!/bin/bash
# Price sweep for DeepSeek-V4-Flash and Qwen3.8-Flash on DeepInfra.
#   ./run_open_models.sh smoke   -> 5 calls per model at $5 (check the key and settings, about $0.001)
#   ./run_open_models.sh         -> full run: 5 fares x 576 prompts x 2 models = 5,760 calls (about $0.35)
# Resumable: rerun the same command to retry failed calls; finished answers are never redone.
set -u
cd "$(dirname "$0")"
: "${DEEPINFRA_API_KEY:?set DEEPINFRA_API_KEY first (export DEEPINFRA_API_KEY=...)}"
PY=${PYTHON:-python3}
WORKERS=${WORKERS:-8}
COMMON=(--provider openai --base-url https://api.deepinfra.com/v1/openai --api-key-env DEEPINFRA_API_KEY
        --reasoning-effort none --max-tokens 2000 --max-tokens-field max_tokens --workers "$WORKERS")
MODELS=("deepseek deepseek-ai/DeepSeek-V4-Flash" "qwen Qwen/Qwen3.8-Flash")
mkdir -p runs/sweep runs/sweep_logs

if [ "${1:-}" = "smoke" ]; then
  for m in "${MODELS[@]}"; do
    set -- $m
    $PY mini_study.py run --design-dir runs/design_full --model "$2" --out runs/smoke_$1 --limit 5 "${COMMON[@]}"
    echo "--- $1 answers:"; if [ -s runs/smoke_$1/results.jsonl ]; then cut -c1-200 runs/smoke_$1/results.jsonl; else echo "no answers; first error:"; head -1 runs/smoke_$1/errors.jsonl | cut -c1-300; fi
  done
  exit 0
fi

run_model () {  # tag model_id
  for p in 5 0 1 15 35; do
    if [ "$p" = 5 ]; then d=runs/design_full; o=runs/$1_full; else d=runs/design_price$p; o=runs/sweep/$1_price$p; fi
    $PY mini_study.py run --design-dir $d --model "$2" --out $o "${COMMON[@]}"
  done > runs/sweep_logs/$1.log 2>&1
  echo "ALL DONE" >> runs/sweep_logs/$1.log
}
for m in "${MODELS[@]}"; do run_model $m & done
echo "running in the background; follow progress with: tail -f runs/sweep_logs/deepseek.log runs/sweep_logs/qwen.log"
wait
echo "finished. Answers per run (576 expected; rerun this script if any are short):"
for f in runs/deepseek_full runs/qwen_full runs/sweep/deepseek_* runs/sweep/qwen_*; do
  printf "  %-28s %4s\n" "$f" "$(wc -l < $f/results.jsonl 2>/dev/null || echo 0)"
done
echo "now build the report: $PY sweep_analysis.py"
