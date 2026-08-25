#!/usr/bin/env bash
# demo/seed.sh — create a fresh demo dataset for recording.
# Usage: demo/seed.sh [dir]   (default: /tmp/turbotokens-demo)
set -eu
DIR="${1:-/tmp/turbotokens-demo}"

rm -rf "$DIR"
mkdir -p "$DIR/projects/webapp" "$DIR/projects/api" "$DIR/projects/infra"

TODAY=$(date -u +%Y-%m-%d)

line() { # project session model minutes_ago input output cc cr cents
  local ts
  ts=$(date -u -v-"$4"M +%Y-%m-%dT%H:%M:%S.000Z 2>/dev/null || date -u -d "$4 minutes ago" +%Y-%m-%dT%H:%M:%S.000Z)
  printf '{"timestamp":"%s","version":"1.2.3","sessionId":"%s","message":{"id":"msg-%s","model":"%s","usage":{"input_tokens":%s,"output_tokens":%s,"cache_creation_input_tokens":%s,"cache_read_input_tokens":%s}},"requestId":"req-%s","costUSD":0.%s}\n' \
    "$ts" "$2" "$RANDOM$RANDOM" "$3" "$5" "$6" "$7" "$8" "$RANDOM" "$9"
}

# A believable morning: steady sonnet work in webapp/api, an opus spike in infra.
seed_file() { # file project model base_minutes
  local f="$1" proj="$2" model="$3" mins="$4"
  : > "$f"
  local n=0
  while [ "$mins" -gt 5 ]; do
    n=$((n+1))
    line "$proj" "$(basename "$f" .jsonl)" "$model" "$mins" \
      $((300 + RANDOM % 1200)) $((80 + RANDOM % 400)) \
      $((RANDOM % 2000)) $((4000 + RANDOM % 60000)) \
      $(printf '%03d' $((RANDOM % 60 + 5))) >> "$f"
    mins=$((mins - 3 - RANDOM % 9))
  done
}

seed_file "$DIR/projects/webapp/sess-1.jsonl"  webapp claude-sonnet-4.6-20260416 180
seed_file "$DIR/projects/webapp/sess-2.jsonl"  webapp claude-sonnet-4.6-20260416 90
seed_file "$DIR/projects/api/sess-1.jsonl"     api    claude-sonnet-4.6-20260416 150
seed_file "$DIR/projects/api/sess-2.jsonl"     api    claude-opus-4.8-20260528   60
seed_file "$DIR/projects/infra/sess-1.jsonl"   infra  claude-opus-4.8-20260528   45

echo "Seeded $DIR — point CLAUDE_CONFIG_DIR at it:"
echo "  export CLAUDE_CONFIG_DIR=$DIR"
