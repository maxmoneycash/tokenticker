#!/usr/bin/env bash
# End-to-end latency probe for `turbotokens live --json`.
# Appends valid usage lines to a watched JSONL file and measures the time from
# write to the event appearing on stdout. Prints p50/p95 over N samples.
set -euo pipefail

SAMPLES="${1:-20}"
INTERVAL_MS="${2:-100}"
BIN="$(dirname "$0")/../target/release/turbotokens"
DIR=/tmp/turbotokens-latency-probe
export LOG_LEVEL=0 NO_COLOR=1 TZ=UTC
export CLAUDE_CONFIG_DIR="$DIR"

rm -rf "$DIR" /tmp/latency-out.ndjson
mkdir -p "$DIR/projects/probe"
: > "$DIR/projects/probe/sess.jsonl"

"$BIN" live --json --interval "$INTERVAL_MS" > /tmp/latency-out.ndjson 2>/dev/null &
LIVE_PID=$!
trap 'kill $LIVE_PID 2>/dev/null || true' EXIT
sleep 2  # let it seed

python3 - "$SAMPLES" <<'EOF'
import json, subprocess, sys, time

samples = int(sys.argv[1])
path = "/tmp/turbotokens-latency-probe/projects/probe/sess.jsonl"
lat = []
for i in range(samples):
    before = sum(1 for _ in open("/tmp/latency-out.ndjson", "rb"))
    line = (
        '{"timestamp":"2026-07-28T10:00:%02d.000Z","version":"1.2.3","sessionId":"sess",'
        '"message":{"id":"msg-%d","model":"claude-sonnet-4-20250514","usage":{"input_tokens":1,'
        '"output_tokens":2,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}},'
        '"requestId":"req-%d","costUSD":0.001}\n' % (i % 60, i, i)
    )
    t0 = time.perf_counter()
    with open(path, "a") as f:
        f.write(line)
    deadline = t0 + 5
    while time.perf_counter() < deadline:
        n = sum(1 for _ in open("/tmp/latency-out.ndjson", "rb"))
        if n > before:
            lat.append((time.perf_counter() - t0) * 1000)
            break
        time.sleep(0.005)
    else:
        print(f"sample {i}: TIMEOUT")
lat.sort()
if lat:
    p50 = lat[len(lat) // 2]
    p95 = lat[min(len(lat) - 1, int(len(lat) * 0.95))]
    print(f"samples: {len(lat)}/{samples}")
    print(f"p50: {p50:.0f} ms  p95: {p95:.0f} ms  max: {lat[-1]:.0f} ms")
    print("PASS" if p95 < 250 else "FAIL: p95 >= 250ms")
else:
    print("FAIL: no samples")
EOF
