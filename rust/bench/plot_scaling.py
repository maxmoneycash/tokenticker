#!/usr/bin/env python3
"""Render assets/scaling-chart.png — time to count N tokens, grouped bars.

Five rows (1B-50B tokens), three tools each, log-scale time axis.
One message: turbotokens is fastest at every size.
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

GREEN, RED, BLUE, GRAY = "#1a7f37", "#cf222e", "#0969da", "#57606a"

def fmt(s):
    return f"{s*1000:.0f} ms" if s < 1 else f"{s:.1f} s"

SIZES = [50, 25, 10, 5, 1]  # top to bottom
TOOLS = [("turbotokens", GREEN), ("ccusage", RED), ("tokscale", BLUE)]

plt.rcParams.update({
    "font.family": "Menlo", "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": "#d0d7de", "axes.grid": True, "grid.color": "#e5e7eb",
    "grid.linewidth": 0.8, "font.size": 13,
})

fig, ax = plt.subplots(figsize=(11, 6), dpi=150)

BAR_H = 0.24
y_ticks, y_labels = [], []
for row, n in enumerate(SIZES):
    yc = len(SIZES) - 1 - row
    y_ticks.append(yc)
    y_labels.append(f"{n}B tokens")
    for i, (tool, color) in enumerate(TOOLS):
        secs = syn[(tool, n)]
        yy = yc + (1 - i) * (BAR_H + 0.04)
        ax.barh(yy, secs, height=BAR_H, color=color)
        ax.annotate(fmt(secs), (secs, yy), textcoords="offset points", xytext=(5, -3),
                    color=color, fontsize=10.5, fontweight="bold")

ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, fontsize=12.5)
ax.set_xscale("log")
ax.set_xlim(0.03, 40)
ax.set_xticks([0.01, 0.1, 1, 10])
ax.set_xticklabels(["10 ms", "100 ms", "1 s", "10 s"], fontsize=11)
ax.set_xlabel("Wall time (log scale) — lower is better")
ax.set_title("Time to count N tokens — full cost report, no cache, identical logs", pad=12)
ax.legend(handles=[mpatches.Patch(color=c, label=t) for t, c in TOOLS],
          frameon=False, loc="lower right", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", visible=False)

fig.tight_layout()
fig.savefig(out_path)
print(f"wrote {out_path}")
