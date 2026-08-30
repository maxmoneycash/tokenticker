#!/usr/bin/env python3
"""Render assets/scaling-chart.png from the scaling-bench results CSV.

Nice-looking matplotlib chart: tokens counted (x, billions) vs wall time
(y, seconds, log scale), one line per tool, values labeled.
Usage: plot_scaling.py results.csv out.png
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

csv_path, out_path = sys.argv[1], sys.argv[2]

series = {}
for line in open(csv_path):
    if line.startswith("tool"):
        continue
    tool, tokens, _b, secs = line.strip().split(",")
    series.setdefault(tool, []).append((int(tokens) / 1e9, float(secs)))

STYLE = {
    "turbotokens": {"color": "#1a7f37", "marker": "o", "label": "turbotokens"},
    "tokscale": {"color": "#0969da", "marker": "s", "label": "tokscale"},
    "ccusage": {"color": "#cf222e", "marker": "^", "label": "ccusage"},
}

plt.rcParams.update({
    "font.family": "Menlo",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#d0d7de",
    "axes.grid": True,
    "grid.color": "#e5e7eb",
    "grid.linewidth": 0.8,
    "font.size": 13,
})

fig, ax = plt.subplots(figsize=(11, 7), dpi=160)

for tool, pts in series.items():
    pts.sort()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    st = STYLE.get(tool, {"color": "#57606a", "marker": "o", "label": tool})
    ax.plot(xs, ys, marker=st["marker"], color=st["color"], linewidth=2.5,
            markersize=8, label=st["label"])
    for i, (x, y) in enumerate(zip(xs, ys)):
        label = f"{y*1000:.0f} ms" if y < 1 else (f"{y:.1f} s" if y < 60 else f"{y/60:.0f} min")
        offset = (8, -16) if i == 0 else (8, 8)
        ax.annotate(label, (x, y), textcoords="offset points", xytext=offset,
                    color=st["color"], fontsize=11, fontweight="bold")

ax.set_yscale("log")
ax.set_xlabel("Tokens counted (billions)")
ax.set_ylabel("Wall time (log scale)")
ax.set_title("Time to count N tokens — full cost report, no cache (synthetic Claude-format logs)", fontsize=15, pad=14)
ax.legend(frameon=False, loc="upper left")
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)

fig.subplots_adjust(bottom=0.12, top=0.92)

fig.tight_layout()
fig.savefig(out_path)
print(f"wrote {out_path}")
