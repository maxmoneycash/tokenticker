#!/usr/bin/env python3
"""Render assets/scaling-chart.png — one organized grouped-bar chart.

Sections: synthetic scaling series (1B-50B, from scaling-bench results CSV),
then real-world runs (real folder, repeat, daemon, production pipeline).
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
    if s <= 0.001:
        return "<1 ms"
    if s < 1:
        return f"{s*1000:.0f} ms"
    return f"{s:.1f} s" if s < 60 else f"{s/60:.0f}+ min"

# (kind, label, {tool: seconds or None}, note)
# kind: "header" or "bars"
ROWS = [
    ("header", "Real logs & production", {}, ""),
    ("bars", "68.2B-token pipeline · 9 agents", {"turbotokens": 14.0, "ccusage": 1800.0}, ""),
    ("bars", "Real folder, 2.3 GB · first run", {"turbotokens": 0.170, "ccusage": 7.0}, ""),
    ("bars", "Same folder · repeat run", {"turbotokens": 0.010, "ccusage": 7.0}, ""),
    ("bars", "Same folder · via daemon", {"turbotokens": 0.001, "ccusage": None}, "ccusage: no daemon, full re-parse"),
    ("header", "Synthetic logs, identical for all tools", {}, ""),
    ("bars", "50B tokens", {"turbotokens": syn[("turbotokens", 50)], "ccusage": syn[("ccusage", 50)], "tokscale": syn[("tokscale", 50)]}, ""),
    ("bars", "25B tokens", {"turbotokens": syn[("turbotokens", 25)], "ccusage": syn[("ccusage", 25)], "tokscale": syn[("tokscale", 25)]}, ""),
    ("bars", "10B tokens", {"turbotokens": syn[("turbotokens", 10)], "ccusage": syn[("ccusage", 10)], "tokscale": syn[("tokscale", 10)]}, ""),
    ("bars", "1B tokens", {"turbotokens": syn[("turbotokens", 1)], "ccusage": syn[("ccusage", 1)], "tokscale": syn[("tokscale", 1)]}, ""),
]

TOOLS = [("turbotokens", GREEN), ("ccusage", RED), ("tokscale", BLUE)]

plt.rcParams.update({
    "font.family": "Menlo", "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": "#d0d7de", "axes.grid": True, "grid.color": "#e5e7eb",
    "grid.linewidth": 0.8, "font.size": 12,
})

fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=150)

BAR_H, GAP = 0.22, 0.05
y = 0.0
y_ticks, y_labels = [], []
for kind, label, data, note in ROWS:
    if kind == "header":
        ax.text(9e-4, y, label, fontsize=12.5, fontweight="bold", color=GRAY,
                va="center")
        y -= 0.55
        continue
    y_ticks.append(y)
    y_labels.append(label)
    present = [(t, c) for t, c in TOOLS if t in data]
    for i, (tool, color) in enumerate(present):
        secs = data[tool]
        yy = y + (len(present) - 1 - i) * (BAR_H + GAP) - (len(present) * (BAR_H + GAP)) / 2 + BAR_H / 2
        if secs is None:
            ax.barh(yy, 7.0, height=BAR_H, color=color, alpha=0.22)
            ax.annotate(note, (7.0, yy), textcoords="offset points",
                        xytext=(6, -3), color=color, fontsize=10, style="italic")
        else:
            ax.barh(yy, secs, height=BAR_H, color=color)
            ax.annotate(fmt(secs), (secs, yy), textcoords="offset points",
                        xytext=(5, -3), color=color, fontsize=10.5, fontweight="bold")
    y -= 1.0

ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, fontsize=11.5)
ax.set_xscale("log")
ax.set_xlim(8e-4, 5000)
ax.set_xticks([0.001, 0.01, 0.1, 1, 10, 60, 600, 3600])
ax.set_xticklabels(["1 ms", "10 ms", "100 ms", "1 s", "10 s", "1 min", "10 min", "1 h"],
                   fontsize=10.5)
ax.set_xlabel("Wall time, log scale — lower is better")
ax.set_title("Time for a full token-usage report", fontsize=15, pad=34)
ax.text(0.0, 1.045, "median of measured runs · identical logs for all tools · cache disabled",
        transform=ax.transAxes, fontsize=10.5, color=GRAY)
ax.legend(handles=[mpatches.Patch(color=c, label=t) for t, c in TOOLS],
          frameon=False, loc="lower right", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", visible=False)

fig.tight_layout()
fig.savefig(out_path)
print(f"wrote {out_path}")
