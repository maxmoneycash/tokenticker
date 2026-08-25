#!/usr/bin/env python3
"""Render the final frame of an asciicast v2 file to a PNG (retina 2x)."""
import json, sys
import pyte
from PIL import Image, ImageDraw, ImageFont

CAST, OUT = sys.argv[1], sys.argv[2]
COLS = int(sys.argv[3]) if len(sys.argv) > 3 else 100
ROWS = int(sys.argv[4]) if len(sys.argv) > 4 else 32
FONT_SIZE = int(sys.argv[5]) if len(sys.argv) > 5 else 30  # 2x of 15px
TRIM_BOTTOM = len(sys.argv) > 6 and sys.argv[6] == "trim"

# --- theme (tokyo-night-ish, matches old assets) ---
BG = (26, 27, 38)          # #1a1b26
FG = (192, 202, 245)       # #c0caf5
BASE16 = {
    "black": (21, 23, 36), "red": (247, 118, 142), "green": (158, 206, 106),
    "yellow": (224, 175, 104), "blue": (122, 162, 247), "magenta": (187, 154, 247),
    "cyan": (125, 207, 255), "white": (169, 177, 214),
    "brightblack": (65, 72, 104), "brightred": (247, 118, 142),
    "brightgreen": (158, 206, 106), "brightyellow": (224, 175, 104),
    "brightblue": (122, 162, 247), "brightmagenta": (187, 154, 247),
    "brightcyan": (125, 207, 255), "brightwhite": (192, 202, 245),
}

def xterm256(n):
    if n < 16:
        return list(BASE16.values())[n]
    if n < 232:
        n -= 16
        r, g, b = n // 36, (n % 36) // 6, n % 6
        conv = lambda v: 55 + v * 40 if v else 0
        return (conv(r), conv(g), conv(b))
    v = 8 + (n - 232) * 10
    return (v, v, v)

def resolve(c, default):
    if c == "default" or c is None:
        return default
    if c in BASE16:
        return BASE16[c]
    if isinstance(c, str) and c.isdigit():
        return xterm256(int(c))
    if isinstance(c, str) and len(c) == 6:
        try:
            return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            pass
    return default

# --- compose final frame ---
screen = pyte.Screen(COLS, ROWS)
stream = pyte.Stream(screen)
with open(CAST) as f:
    header = json.loads(f.readline())
    for line in f:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if len(ev) >= 3 and ev[1] == "o":
            stream.feed(ev[2])

lines = []
for y in range(ROWS):
    lines.append([screen.display[y]])

# trim fully-blank bottom rows if asked
disp = screen.display
last_nonempty = max((i for i, row in enumerate(disp) if row.strip()), default=0)
nrows = (last_nonempty + 1) if TRIM_BOTTOM else ROWS

# --- fonts ---
MENLO = "/System/Library/Fonts/Menlo.ttc"
font = ImageFont.truetype(MENLO, FONT_SIZE, index=0)
bold = ImageFont.truetype(MENLO, FONT_SIZE, index=1)
cw = font.getlength("M")
ascent, descent = font.getmetrics()
lh = ascent + descent + int(FONT_SIZE * 0.22)

PADX, PADY = int(FONT_SIZE * 1.2), int(FONT_SIZE * 0.9)
W = int(COLS * cw) + PADX * 2
H = nrows * lh + PADY * 2

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# --- vector-draw box-drawing chars so lines connect perfectly ---
LINE_W = max(2, int(FONT_SIZE * 0.075))

def draw_box(ch, px, py, w, h, color):
    cx, cy = px + w / 2, py + h / 2
    L = R = T = B = False
    ARC = None
    if ch in "─━┄┅┈┉╌╍": L = R = True
    elif ch in "│┃┆┇┊┋╎╏": T = B = True
    elif ch in "┌┍┎┏": R = B = True
    elif ch in "┐┑┒┓": L = B = True
    elif ch in "└┕┖┗": R = T = True
    elif ch in "┘┙┚┛": L = T = True
    elif ch in "├┝┞┟┠┡┢┣": T = B = R = True
    elif ch in "┤┥┦┧┨┩┪┫": T = B = L = True
    elif ch in "┬┭┮┯┰┱┲┳": L = R = B = True
    elif ch in "┴┵┶┷┸┹┺┻": L = R = T = True
    elif ch in "┼╀╁╂╃╄╅╆╇╈╉╊╋": L = R = T = B = True
    elif ch == "╭": ARC = (px, py, px + w, py + h); ST, EN = 0, 90
    elif ch == "╮": ARC = (px, py, px + w, py + h); ST, EN = 90, 180
    elif ch == "╰": ARC = (px, py, px + w, py + h); ST, EN = 270, 360
    elif ch == "╯": ARC = (px, py, px + w, py + h); ST, EN = 180, 270
    else:
        return False
    if ARC:
        x0, y0, x1, y1 = ARC
        d.arc([x0 - LINE_W / 2, y0 - LINE_W / 2, x1 + LINE_W / 2, y1 + LINE_W / 2],
              ST, EN, fill=color, width=LINE_W)
        return True
    hw = LINE_W / 2
    if L: d.rectangle([px, cy - hw, cx + hw, cy + hw], fill=color)
    if R: d.rectangle([cx - hw, cy - hw, px + w, cy + hw], fill=color)
    if T: d.rectangle([cx - hw, py, cx + hw, cy + hw], fill=color)
    if B: d.rectangle([cx - hw, cy - hw, cx + hw, py + h], fill=color)
    return True

for y in range(nrows):
    row = disp[y]
    for x in range(min(COLS, len(row))):
        ch = screen.buffer[y][x]
        if ch.data == " " and ch.bg in ("default", None):
            continue
        px, py = PADX + x * cw, PADY + y * lh
        fg = resolve(ch.fg, FG)
        bg = resolve(ch.bg, BG)
        if ch.reverse:
            fg, bg = bg, fg
        if bg != BG or ch.reverse:
            d.rectangle([px, py, px + cw, py + lh], fill=bg)
        if ch.data.strip():
            if len(ch.data) == 1 and draw_box(ch.data, px, py, cw, lh, fg):
                continue
            d.text((px, py), ch.data, font=bold if ch.bold else font, fill=fg)
img.save(OUT)
print(f"wrote {OUT} {W}x{H}")
