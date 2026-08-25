# Recording a demo

Three steps, two minutes.

## 1. Fresh fake data + a live feed

```bash
demo/seed.sh                                  # one time per take
export CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo

demo/feed.sh                                  # tab 2 — keeps appending
```

## 2. Record (tab 1)

```bash
turbotokens doctor
turbotokens claude daily
turbotokens live        # the money shot — let it run 15-20s
```

## 3. Reset for another take

Ctrl-C everything, then `demo/seed.sh && clear`.

Notes: use a big font, ~100 columns, colors on (no NO_COLOR). Let feed.sh
run 10-15s before the live segment so the burn rate is non-zero.
