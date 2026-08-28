#!/usr/bin/env python3
"""Emit the final frame of an asciicast v2 file as ANSI text on stdout.

Colors are re-emitted as standard 16-color SGR codes so downstream tools
(e.g. freeze) can apply their own theme palette.
Usage: cast_to_ansi.py in.cast [cols rows]
"""
import json, sys
import pyte

CAST = sys.argv[1]
COLS = int(sys.argv[2]) if len(sys.argv) > 2 else 100
ROWS = int(sys.argv[3]) if len(sys.argv) > 3 else 32

FG_CODES = {
    "black": 30, "red": 31, "green": 32, "brown": 33, "blue": 34,
    "magenta": 35, "cyan": 36, "white": 37,
    "brightblack": 90, "brightred": 91, "brightgreen": 92, "brightbrown": 93,
    "brightyellow": 93, "brightblue": 94, "brightmagenta": 95,
    "brightcyan": 96, "brightwhite": 97,
}
# truecolor overrides: some palette entries are unreadable on light themes
# (terminals remap palette colors per theme; this is the same idea)
FG_TRUECOLOR = {
    "brown": (181, 137, 0),   # ANSI yellow -> readable olive on white
}

screen = pyte.Screen(COLS, ROWS)
stream = pyte.Stream(screen)
with open(CAST) as f:
    json.loads(f.readline())  # header
    for line in f:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if len(ev) >= 3 and ev[1] == "o":
            stream.feed(ev[2])

out = []
for y in range(ROWS):
    row = []
    cur = None
    for x in range(COLS):
        ch = screen.buffer[y][x]
        tc = FG_TRUECOLOR.get(ch.fg)
        if tc:
            fg = f"38;2;{tc[0]};{tc[1]};{tc[2]}"
        else:
            fg = FG_CODES.get(ch.fg, 39)
        bg = FG_CODES.get(ch.bg, None)
        bg = (bg + 10) if bg is not None else 49
        if ch.reverse:
            fg, bg = (bg - 10 if bg != 49 else 30), (fg + 10 if fg != 39 and not isinstance(fg, str) else 49)
        bold = bool(ch.bold)
        style = (fg, bg, bold)
        if style != cur:
            seq = f"\x1b[0;{fg};{bg}m" + ("\x1b[1m" if bold else "")
            row.append(seq)
            cur = style
        row.append(ch.data)
    out.append("".join(row).rstrip() + "\x1b[0m")

# trim trailing blank rows (strip escape sequences before testing)
import re
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
while out and not ANSI_RE.sub("", out[-1]).strip():
    out.pop()
sys.stdout.write("\n".join(out) + "\n")
