#!/bin/bash
# Price sweep: every model x every new price. Resumable (rerun the script to retry failures).
cd "$(dirname "$0")"
run_model () {  # tag provider model
  for p in 0 1 15 35; do
    python3 mini_study.py run --design-dir runs/design_price$p --provider $2 --model $3 --out runs/sweep/$1_price$p --workers 8
  done > runs/sweep_logs/$1.log 2>&1
  echo "ALL DONE" >> runs/sweep_logs/$1.log
}
run_model terra openai gpt-6.1-terra &
run_model sol openai gpt-6.1-sol &
run_model luna openai gpt-6-luna &
run_model sonnet anthropic claude-sonnet-5-5 &
run_model opus anthropic claude-opus-5-5 &
wait
