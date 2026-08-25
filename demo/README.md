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

The images in `assets/` are rendered from real terminal captures, not mockups:

```bash
demo/seed.sh
(CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo demo/feed.sh &)   # keep data flowing

# record a live session, then render the final frame
asciinema rec --overwrite -q --cols 100 --rows 32 \
  -c 'sh -c "CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo turbotokens live --offline & p=$!; sleep 12; kill $p"' \
  /tmp/tt-live.cast
python3 demo/render_svg.py /tmp/tt-live.cast assets/live-dashboard.svg 100 32 15
python3 demo/render_cast.py /tmp/tt-live.cast assets/live-dashboard.png 100 32 30

# daily report
asciinema rec --overwrite -q --cols 100 --rows 40 \
  -c 'env CLAUDE_CONFIG_DIR=/tmp/turbotokens-demo turbotokens claude daily --offline' \
  /tmp/tt-daily.cast
python3 demo/render_svg.py /tmp/tt-daily.cast assets/daily-report.svg 100 40 15 trim

# social card + animated demo + badges
python3 demo/social_card.py        # composites the dashboard PNG, 1280x640
agg --font-size 16 --speed 1.2 /tmp/tt-live.cast assets/live-demo.gif
python3 demo/badges.py             # rewrites assets/badges/*.svg
```

`render_svg.py` needs `pyte`; `render_cast.py`/`social_card.py` also need
`Pillow` (a venv works fine). Font: Menlo. The SVG renderer draws box-drawing
characters as vectors and pins every word to the terminal grid with
`textLength`, so tables stay aligned in any browser.
