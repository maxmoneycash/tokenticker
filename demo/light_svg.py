#!/usr/bin/env python3
"""Convert turbotokens' dark SVG cards to the light macOS-Tahoe README style.

Swaps the known dark palettes to GitHub-light equivalents and injects a
traffic-light header band when the card lacks one (heatmap). The product's
own SVG output is unchanged — this is a presentation transform for assets/.
Usage: light_svg.py in.svg out.svg
"""
import re, sys

PALETTE = {
    # heatmap: github dark -> github light (intensity ramp inverted)
    "#0d1117": "#ffffff",
    "#161b22": "#ebedf0",
    "#0e4429": "#9be9a8",
    "#006d32": "#40c463",
    "#26a641": "#30a14e",
    "#39d353": "#216e39",
    "#8b949e": "#57606a",
    # wrapped: tokyonight-ish -> light
    "#1a1b26": "#ffffff",
    "#c0caf5": "#1f2328",
    "#565f89": "#6e7781",
    "#7aa2f7": "#0969da",
    "#9ece6a": "#1a7f37",
    "#f7768e": "#ff5f57",
    "#e0af68": "#febc2e",
}
DOTS = ('<circle cx="26" cy="17" r="6" fill="#ff5f57"/>'
        '<circle cx="46" cy="17" r="6" fill="#febc2e"/>'
        '<circle cx="66" cy="17" r="6" fill="#28c840"/>')
HEADER = 34

def main():
    src, dst = sys.argv[1], sys.argv[2]
    svg = open(src).read()

    if "#f7768e" not in svg and "#ff5f57" not in svg:
        # no traffic lights: add a header band above the content
        tag = re.search(r'<svg[^>]*>', svg).group(0)
        w = float(re.search(r'width="([\d.]+)"', tag).group(1))
        h = float(re.search(r'height="([\d.]+)"', tag).group(1))
        new_tag = (tag
                   .replace(f'height="{h:g}"', f'height="{h + HEADER:g}"')
                   .replace(f'viewBox="0 0 {w:g} {h:g}"', f'viewBox="0 0 {w:g} {h + HEADER:g}"'))
        svg = svg.replace(tag, new_tag, 1)
        # extend the full-canvas background rect
        bg = re.search(r'<rect width="[\d.]+" height="[\d.]+"[^>]*>', svg).group(0)
        bg_end = svg.index(bg) + len(bg)
        svg = svg[:bg_end - len(bg)] + re.sub(r'height="[\d.]+"', f'height="{h + HEADER:g}"', bg) + svg[bg_end:]
        # shift all remaining content below the header, dots above it
        after_bg = bg_end
        close = svg.rindex("</svg>")
        svg = (svg[:after_bg] + f'\n<g transform="translate(0,{HEADER})">'
               + svg[after_bg:close] + "</g>\n" + svg[close:])
        insert_at = svg.index("</g>\n</svg>") + len("</g>\n")
        svg = svg[:insert_at] + DOTS + "\n" + svg[insert_at:]

    for old, new in PALETTE.items():
        svg = svg.replace(old, new)

    open(dst, "w").write(svg)
    print(f"wrote {dst}")

if __name__ == "__main__":
    main()
