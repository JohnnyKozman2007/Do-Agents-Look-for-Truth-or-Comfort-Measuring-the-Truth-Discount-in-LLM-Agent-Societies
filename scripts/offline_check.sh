#!/usr/bin/env bash
# Check only local synthetic software behavior. No provider credentials or calls.
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "$script_dir/.." && pwd)"
cd "$repo_root"
export PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}"
python_cmd="${PYTHON:-python3}"

"$python_cmd" -m unittest discover -s tests -v

check_tmp="$(mktemp -d "${TMPDIR:-/tmp}/truth-discount-offline.XXXXXX")"
trap 'rm -rf -- "$check_tmp"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

"$python_cmd" -m truth_discount.cli demo --config "$repo_root/configs/pilot_config.json" --output "$check_tmp/demo"
"$python_cmd" -m truth_discount.cli summarize "$check_tmp/demo"
