#!/usr/bin/env python3
"""Generate the README badge SVGs, themed to match the terminal assets."""
import os

OUT_DIR = "assets/badges"
FONT_STACK = "Menlo, 'SF Mono', 'Cascadia Code', Consolas, monospace"
LABEL_BG = "#24283b"
LABEL_FG = "#a9b1d6"
VALUE_FG = "#1a1b26"
H, FS, PAD = 20, 11, 6
CW = FS * 0.6  # Menlo advance

def badge(name, label, value, accent):
    lw = round(len(label) * CW) + PAD * 2
    vw = round(len(value) * CW) + PAD * 2
    w = lw + vw
    y = 14  # baseline
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" font-family="{FONT_STACK}" font-size="{FS}">
  <clipPath id="r"><rect width="{w}" height="{H}" rx="3"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{lw}" height="{H}" fill="{LABEL_BG}"/>
    <rect x="{lw}" width="{vw}" height="{H}" fill="{accent}"/>
  </g>
  <text x="{lw / 2:.1f}" y="{y}" text-anchor="middle" fill="{LABEL_FG}">{label}</text>
  <text x="{lw + vw / 2:.1f}" y="{y}" text-anchor="middle" fill="{VALUE_FG}" font-weight="bold">{value}</text>
</svg>
'''
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        f.write(svg)
    print(f"wrote {path} {w}x{H}")

os.makedirs(OUT_DIR, exist_ok=True)
badge("version.svg", "version", "v1.0.0", "#7aa2f7")
badge("agents.svg", "agents", "16", "#9ece6a")
badge("speed.svg", "cold report", "170 ms", "#7aa2f7")
badge("rust.svg", "built with", "Rust", "#bb9af7")
