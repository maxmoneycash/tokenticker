#!/usr/bin/env bash
# scaling-bench.sh — how long does counting N tokens of Claude-format logs take?
#
# Datasets come from gen_scaling_data.py (realistic ~2KB-content transcript
# lines). Times a full cost report (both tools' --json daily report) with any
# cache disabled: turbotokens cold = TURBOTOKENS_CACHE=off; ccusage re-parses
# everything every run by design.
#
# Usage: SIZES="1 5 10 25 50" rust/bench/scaling-bench.sh
# Env:   DATA=/tmp/tt-scaling  TT=./rust/target/release/turbotokens
#        CCUSAGE="bunx --bun ccusage@20.0.20"  OUT=/tmp/tt-scaling/results.csv
set -u
cd "$(dirname "$0")/../.." || exit 1

SIZES="${SIZES:-1 5 10 25 50}"
DATA="${DATA:-/tmp/tt-scaling}"
TT="${TT:-./rust/target/release/turbotokens}"
CCUSAGE="${CCUSAGE:-bunx --bun ccusage@20.0.20}"
OUT="${OUT:-$DATA/results.csv}"

time_cmd() { # prints seconds to stdout
  local start end
  start=$(python3 -c 'import time; print(time.time())')
  "$@" >/dev/null 2>&1
  end=$(python3 -c 'import time; print(time.time())')
  python3 -c "print(f'{$end - $start:.3f}')"
}

median3() { printf '%s\n' "$1" "$2" "$3" | sort -n | sed -n 2p; }

echo "tool,tokens,bytes,seconds" | tee "$OUT"
for n in $SIZES; do
  dir="$DATA/tok-${n}B"
  [ -d "$dir" ] || { echo "missing $dir (run gen_scaling_data.py)"; continue; }
  tokens=$(cat "$dir/TOTAL_TOKENS")
  bytes=$(find "$dir" -name '*.jsonl' -exec stat -f%z {} + | awk '{s+=$1} END {print s}')

  t1=$(time_cmd env TURBOTOKENS_CACHE=off CLAUDE_CONFIG_DIR="$dir" $TT claude daily --offline --json)
  t2=$(time_cmd env TURBOTOKENS_CACHE=off CLAUDE_CONFIG_DIR="$dir" $TT claude daily --offline --json)
  t3=$(time_cmd env TURBOTOKENS_CACHE=off CLAUDE_CONFIG_DIR="$dir" $TT claude daily --offline --json)
  tt=$(median3 "$t1" "$t2" "$t3")
  echo "turbotokens,$tokens,$bytes,$tt" | tee -a "$OUT"

  c1=$(time_cmd env HOME=/tmp/tt-fakehome CLAUDE_CONFIG_DIR="$dir" $CCUSAGE daily --json --offline)
  echo "ccusage,$tokens,$bytes,$c1" | tee -a "$OUT"

  # parity check: both tools must count the same tokens
  tt_tot=$(env TURBOTOKENS_CACHE=off CLAUDE_CONFIG_DIR="$dir" $TT claude daily --offline --json 2>/dev/null \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["totals"]["totalTokens"])')
  cc_tot=$(env HOME=/tmp/tt-fakehome CLAUDE_CONFIG_DIR="$dir" $CCUSAGE daily --json --offline 2>/dev/null \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["totals"]["totalTokens"])')
  echo "  parity: turbotokens=$tt_tot ccusage=$cc_tot (generated=$tokens)"
done
