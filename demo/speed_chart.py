#!/usr/bin/env python3
"""Render assets/speed-chart.png — white, macOS-styled timing comparison."""
import math
from PIL import Image, ImageDraw, ImageFont

MENLO = "/System/Library/Fonts/Menlo.ttc"
f_label = ImageFont.truetype(MENLO, 26, index=0)
f_value = ImageFont.truetype(MENLO, 26, index=1)   # bold
f_group = ImageFont.truetype(MENLO, 24, index=0)
f_note = ImageFont.truetype(MENLO, 20, index=0)

DARK = (31, 35, 40)
GRAY = (87, 96, 106)
BLUE = (9, 105, 218)
GREEN = (26, 127, 55)
RED = (207, 34, 46)
GRID = (229, 231, 235)

# (label, seconds, color, display)
GROUP1 = "Full cost report — 2.3 GB of Claude Code logs"
BARS1 = [
    ("turbotokens, warm cache", 0.010, GREEN, "10 ms"),
    ("turbotokens, cold (no cache)", 0.170, BLUE, "170 ms"),
    ("ccusage", 8.0, RED, "6.2–9.9 s"),
]
GROUP2 = "Production pipeline scan — 68.2B tokens, 9 agents"
BARS2 = [
    ("turbotokens", 14.0, GREEN, "14 s"),
    ("ccusage", 1800.0, RED, "30+ min"),
]

W, H = 1400, 760
img = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(img)

LABEL_X = 60
BAR_X = 620
BAR_W_MAX = 640
BAR_H = 44
LOG_MIN = math.log10(0.010)      # 10 ms
LOG_MAX = math.log10(1800.0)     # 30 min

def barw(seconds):
    return max(8, int(BAR_W_MAX * (math.log10(seconds) - LOG_MIN) / (LOG_MAX - LOG_MIN)))

def draw_group(y, title, bars):
    d.text((LABEL_X, y), title, font=f_group, fill=GRAY)
    y += 48
    for label, secs, color, disp in bars:
        cy = y + BAR_H // 2
        d.text((LABEL_X, y + 6), label, font=f_label, fill=DARK)
        w = barw(secs)
        d.rounded_rectangle([BAR_X, y, BAR_X + w, y + BAR_H], radius=8, fill=color)
        d.text((BAR_X + w + 18, y + 6), disp, font=f_value, fill=DARK)
        y += BAR_H + 28
    return y

y = draw_group(56, GROUP1, BARS1)
y += 30
d.line([LABEL_X, y, W - 60, y], fill=GRID, width=2)
y += 30
y = draw_group(y, GROUP2, BARS2)

# log-scale ticks
tick_y = y + 16
for t, name in [(0.01, "10 ms"), (0.1, "100 ms"), (1, "1 s"), (10, "10 s"), (60, "1 min"), (600, "10 min")]:
    tx = BAR_X + barw(t)
    d.line([tx, tick_y, tx, tick_y + 10], fill=GRID, width=2)
    tw = d.textlength(name, font=f_note)
    d.text((tx - tw / 2, tick_y + 16), name, font=f_note, fill=GRAY)
d.text((LABEL_X, H - 48), "Median of repeated runs, same machine. Log scale. turbotokens cold = cache disabled (worst case).", font=f_note, fill=GRAY)

img.save("assets/speed-chart.png")
print("wrote assets/speed-chart.png")
