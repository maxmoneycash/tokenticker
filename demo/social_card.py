#!/usr/bin/env python3
"""Compose the turbotokens social card (1280x640) from the dashboard PNG."""
import sys
from PIL import Image, ImageDraw, ImageFont

DASH = sys.argv[1] if len(sys.argv) > 1 else "assets/live-dashboard.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/social-card.png"

BG = (13, 14, 20)
WHITE = (235, 238, 245)
GRAY = (139, 146, 168)
BLUE = (122, 162, 247)
GREEN = (158, 206, 106)

MENLO = "/System/Library/Fonts/Menlo.ttc"
f_word = ImageFont.truetype(MENLO, 78, index=1)   # bold
f_tag = ImageFont.truetype(MENLO, 30, index=0)
f_line = ImageFont.truetype(MENLO, 25, index=0)

W, H = 1280, 640
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

LX = 64
y = 118
d.text((LX, y), "turbotokens", font=f_word, fill=WHITE)
y += 132
d.text((LX, y), "Know what your AI coding agents", font=f_tag, fill=GRAY); y += 44
d.text((LX, y), "cost you — as it happens.", font=f_tag, fill=GRAY)
y += 84
d.text((LX, y), "Live token telemetry for Claude Code,", font=f_line, fill=BLUE); y += 36
d.text((LX, y), "Codex + 15 more agents", font=f_line, fill=BLUE)
y += 72
d.text((LX, y), "145ms reports · 10ms warm · <1ms daemon", font=f_line, fill=GREEN); y += 36
d.text((LX, y), "p95 110ms live events · Rust", font=f_line, fill=GREEN)

dash = Image.open(DASH)
tw = 560
th = int(dash.height * tw / dash.width)
dash = dash.resize((tw, th), Image.LANCZOS)
DX, DY = W - tw - 40, (H - th) // 2
# subtle frame
d.rectangle([DX - 2, DY - 2, DX + tw + 2, DY + th + 2], outline=(45, 48, 66), width=2)
img.paste(dash, (DX, DY))

img.save(OUT)
print(f"wrote {OUT}")
