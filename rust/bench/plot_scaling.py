#!/usr/bin/env python3
"""Render assets/scaling-chart.png — how long it takes to count N tokens.

Five rows (1B-50B tokens), three tools each, log-scale time axis.
Usage: plot_scaling.py results.csv out.png
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

csv_path, out_path = sys.argv[1], sys.argv[2]

syn = {}
for line in open(csv_path):
    if line.startswith("tool"):
        continue
    tool, tokens, _b, secs = line.strip().split(",")
    syn[(tool, int(tokens) // 1_000_000_000)] = float(secs)

GREEN, RED, BLUE, GRAY = "#2da44e", "#d1242f", "#2f81d6", "#6e7781"

def fmt(s):
    return f"{s*1000:.0f} ms" if s < 1 else f"{s:.1f} s"

SIZES = [50, 25, 10, 5, 1]  # top to bottom
TOOLS = [("turbotokens", GREEN), ("ccusage", RED), ("tokscale", BLUE)]

plt.rcParams.update({
    "font.family": "Menlo",
    "font.size": 13,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#d0d7de",
    "axes.grid": True,
    "grid.color": "#eaeef2",
    "grid.linewidth": 1.0,
})

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)

BAR_H = 0.27
y_ticks, y_labels = [], []
for row, n in enumerate(SIZES):
    yc = len(SIZES) - 1 - row
    y_ticks.append(yc)
    y_labels.append(f"{n}B tokens")
    for i, (tool, color) in enumerate(TOOLS):
        secs = syn[(tool, n)]
        yy = yc + (1 - i) * (BAR_H + 0.05)
        ax.barh(yy, secs, height=BAR_H, color=color)
        ax.annotate(fmt(secs), (secs, yy), textcoords="offset points", xytext=(6, -3),
                    color=color, fontsize=11, fontweight="bold")

ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, fontsize=13)
ax.set_xscale("log")
ax.set_xlim(0.03, 40)
ax.set_xticks([0.01, 0.1, 1, 10])
ax.set_xticklabels(["10 ms", "100 ms", "1 second", "10 seconds"], fontsize=11.5)
ax.set_xlabel("Time to finish (log scale) — lower is better")
ax.set_title("How long it takes to count N tokens", fontsize=17,
             fontweight="bold", loc="left", pad=32)
ax.text(0.0, 1.035, "full cost report · identical logs for every tool · no cache",
        transform=ax.transAxes, fontsize=11.5, color=GRAY)
ax.legend(handles=[mpatches.Patch(color=c, label=t) for t, c in TOOLS],
          frameon=False, loc="lower right", fontsize=11.5)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", visible=False)

fig.tight_layout()
fig.savefig(out_path)
print(f"wrote {out_path}")
