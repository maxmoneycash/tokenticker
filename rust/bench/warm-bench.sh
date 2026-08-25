#!/usr/bin/env bash
# Warm-vs-uncached benchmark for the turbotokens parse cache.
# Usage: rust/bench/warm-bench.sh [runs]
# Uses /usr/bin/time so the measurement covers only the benchmarked process,
# not shell scheduling noise. Prints medians and the speedup ratio; writes
# /tmp/bench-{uncached,warm}.json for parity diffing.
set -euo pipefail

RUNS="${1:-10}"
BIN="$(dirname "$0")/../target/release/turbotokens"
export LOG_LEVEL=0 COLUMNS=200 NO_COLOR=1 TZ=UTC
export CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

median() {  # reads times from stdin (one per line)
  sort -n | awk '{a[NR]=$1} END {print (NR%2 ? a[(NR+1)/2] : (a[NR/2]+a[NR/2+1])/2)}'
}

run_timed() { # $1 = extra env ("off" or ""), $2 = out file
  if [ "$1" = off ]; then
    /usr/bin/time -p env TURBOTOKENS_CACHE=off "$BIN" claude daily --offline --json > "$2" 2>/tmp/bench-time.txt
  else
    /usr/bin/time -p "$BIN" claude daily --offline --json > "$2" 2>/tmp/bench-time.txt
  fi
  awk '/^real / {printf "%d", $2 * 1000}' /tmp/bench-time.txt
}

# Warm up OS page cache and populate the parse/report caches.
"$BIN" claude daily --offline --json > /dev/null
TURBOTOKENS_CACHE=off "$BIN" claude daily --offline --json > /dev/null

uncached=()
for _ in $(seq "$RUNS"); do uncached+=("$(run_timed off /tmp/bench-uncached.json)"); done
warm=()
for _ in $(seq "$RUNS"); do warm+=("$(run_timed on /tmp/bench-warm.json)"); done

u_med=$(printf '%s\n' "${uncached[@]}" | median)
w_med=$(printf '%s\n' "${warm[@]}" | median)
ratio=$(python3 -c "print(f'{$u_med / max($w_med, 1):.2f}')")

echo "uncached median: ${u_med} ms  (runs: ${uncached[*]})"
echo "warm median:     ${w_med} ms  (runs: ${warm[*]})"
echo "speedup:         ${ratio}x"
if cmp -s /tmp/bench-uncached.json /tmp/bench-warm.json; then
  echo "parity:          OK (byte-identical)"
else
  echo "parity:          FAILED"
  exit 1
fi
