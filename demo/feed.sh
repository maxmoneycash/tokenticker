#!/usr/bin/env bash
# demo/feed.sh — append realistic usage lines to the demo logs forever, so
# `turbotokens live` visibly streams while you record.
#
# Cadence mimics real Claude Code usage: bursts of 2-5 events a second or two
# apart, then a pause while the human "reads". Token sizes are cache-heavy,
# like real sessions. Ctrl-C to stop.
set -eu
DIR="${CLAUDE_CONFIG_DIR:-/tmp/turbotokens-demo}"

projects="webapp api infra"
sessions="sess-1 sess-2"

pick_model() {
  case $((RANDOM % 6)) in
    0|1) echo "claude-opus-4-20250514" ;;
    *)   echo "claude-sonnet-4-20250514" ;;
  esac
}

emit() {
  local proj sess model ts in_tok out_tok cc cr cents
  proj=$(echo $projects | tr ' ' '\n' | sed -n "$((RANDOM % 3 + 1))p")
  sess=$(echo $sessions | tr ' ' '\n' | sed -n "$((RANDOM % 2 + 1))p")
  model=$(pick_model)
  ts=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)
  in_tok=$((200 + RANDOM % 1500))
  out_tok=$((60 + RANDOM % 500))
  cc=$((RANDOM % 3000))
  cr=$((3000 + RANDOM % 90000))
  cents=$(printf '%03d' $((RANDOM % 70 + 8)))
  printf '{"timestamp":"%s","version":"1.2.3","sessionId":"%s","message":{"id":"msg-%s","model":"%s","usage":{"input_tokens":%s,"output_tokens":%s,"cache_creation_input_tokens":%s,"cache_read_input_tokens":%s}},"requestId":"req-%s","costUSD":0.%s}\n' \
    "$ts" "$sess" "$RANDOM$RANDOM" "$model" "$in_tok" "$out_tok" "$cc" "$cr" "$RANDOM" "$cents" \
    >> "$DIR/projects/$proj/$sess.jsonl"
}

echo "Feeding $DIR (Ctrl-C to stop)"
while true; do
  burst=$((2 + RANDOM % 4))          # 2-5 event burst
  for _ in $(seq "$burst"); do
    emit
    sleep "0.$((RANDOM % 9 + 3))"    # 0.3-1.1s inside a burst
  done
  sleep $((3 + RANDOM % 8))          # 3-10s "human reading" pause
done
