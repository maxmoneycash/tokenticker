"""Compose the turbotokens social card (1280x640) from the dashboard PNG."""
import sys
from PIL import Image, ImageDraw, ImageFont

DASH = sys.argv[1] if len(sys.argv) > 1 else "assets/live-dashboard.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/social-card.png"

BG = (255, 255, 255)
DARK = (31, 35, 40)
GRAY = (87, 96, 106)
BORDER = (208, 215, 222)

MENLO = "/System/Library/Fonts/Menlo.ttc"
f_word = ImageFont.truetype(MENLO, 78, index=1)   # bold
f_line = ImageFont.truetype(MENLO, 27, index=0)

W, H = 1280, 640
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

LX = 64
y = 220
d.text((LX, y), "turbotokens", font=f_word, fill=DARK)
y += 124
d.text((LX, y), "Real-time token and cost telemetry", font=f_line, fill=GRAY); y += 42
d.text((LX, y), "for 16 AI coding agents.", font=f_line, fill=GRAY)

dash = Image.open(DASH).convert("RGBA")
tw = 560
th = int(dash.height * tw / dash.width)
dash = dash.resize((tw, th), Image.LANCZOS)
DX, DY = W - tw - 40, (H - th) // 2
d.rectangle([DX - 2, DY - 2, DX + tw + 2, DY + th + 2], outline=BORDER, width=2)
img.paste(dash, (DX, DY), dash)

img.save(OUT)
print(f"wrote {OUT}")
