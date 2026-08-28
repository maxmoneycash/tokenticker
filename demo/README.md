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

## Regenerating the README images

The images in `assets/` are real terminal captures, framed with
[freeze](https://github.com/charmbracelet/freeze) (macOS window chrome,
rounded corners, xcode light theme). Pipeline:

```bash
demo/seed.sh
(env -u NO_COLOR CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo demo/feed.sh &)

# record the live dashboard and the daily report (colors need
# `env -u NO_COLOR` if your shell sets NO_COLOR)
asciinema rec --overwrite -q --cols 100 --rows 32 \
  -c 'sh -c "env -u NO_COLOR TERM=xterm-256color CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo turbotokens live --offline & p=$!; sleep 12; kill $p"' \
  /tmp/tt-live.cast
asciinema rec --overwrite -q --cols 100 --rows 40 \
  -c 'env -u NO_COLOR TERM=xterm-256color CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo turbotokens claude daily --offline' \
  /tmp/tt-daily.cast

# final cast frame -> ANSI -> freeze
python3 demo/cast_to_ansi.py /tmp/tt-live.cast 100 32 | \
  freeze --window --theme xcode --language ansi --font.size 14 \
    --border.radius 10 --margin 24 -o assets/live-dashboard.png
python3 demo/cast_to_ansi.py /tmp/tt-daily.cast 100 40 | \
  freeze --window --theme xcode --language ansi --font.size 14 \
    --border.radius 10 --margin 24 -o assets/daily-report.png

# social card + animated demo + badges
python3 demo/social_card.py        # composites the dashboard PNG, 1280x640
agg --font-size 16 --speed 1.2 /tmp/tt-live.cast assets/live-demo.gif
python3 demo/badges.py             # rewrites assets/badges/*.svg
```

`cast_to_ansi.py` needs `pyte`, `social_card.py` needs `Pillow` (a venv
works fine). freeze is a single static binary from GitHub releases.
`cast_to_ansi.py` remaps ANSI yellow to an olive truecolor — the stock
light themes render it unreadably pale.

There are also two homegrown renderers kept for reference:
`render_svg.py` (cast → flat SVG, vector box-drawing, grid-pinned text)
and `render_cast.py` (cast → PNG via Pillow). The README images use the
freeze pipeline above.
