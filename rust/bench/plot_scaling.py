#!/usr/bin/env python3
"""Render assets/scaling-chart.png — two panels:

Left:  bulk scaling lines from the scaling-bench results CSV
       (time to count N tokens, single shot, no cache).
Right: real-world workloads where architecture dominates — real log folder,
       repeat runs, daemon, production pipeline (all measured).

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
    "ccusage": {"color": "#cf222e", "marker": "^", "label": "ccusage"},
    "tokscale": {"color": "#0969da", "marker": "s", "label": "tokscale"},
}
GREEN, RED, GRAY = "#1a7f37", "#cf222e", "#57606a"

plt.rcParams.update({
    "font.family": "Menlo", "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": "#d0d7de", "axes.grid": True, "grid.color": "#e5e7eb",
    "grid.linewidth": 0.8, "font.size": 12.5,
})

fig, (axl, axr) = plt.subplots(
    1, 2, figsize=(15.5, 6.4), dpi=150,
    gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.16},
)

# ---------------- left: bulk scaling ----------------
for tool, pts in series.items():
    pts.sort()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    st = STYLE.get(tool, {"color": GRAY, "marker": "o", "label": tool})
    axl.plot(xs, ys, marker=st["marker"], color=st["color"], linewidth=2.5,
             markersize=8, label=st["label"])
    for i, (x, y) in enumerate(zip(xs, ys)):
        label = f"{y*1000:.0f} ms" if y < 1 else f"{y:.1f} s"
        offset = (8, -16) if i == 0 else (8, 8)
        axl.annotate(label, (x, y), textcoords="offset points", xytext=offset,
                     color=st["color"], fontsize=10.5, fontweight="bold")

axl.set_yscale("log")
axl.set_xlabel("Tokens counted (billions)")
axl.set_ylabel("Wall time (log scale)")
axl.set_title("One giant report, once — synthetic logs", fontsize=14, pad=12)
axl.legend(frameon=False, loc="upper left")
axl.spines[["top", "right"]].set_visible(False)

# ---------------- right: real-world workloads ----------------
# (label, turbotokens s, ccusage s or None, ccusage note)
ROWS = [
    ("Real folder, 2.3 GB / 1,648 files\nfirst run", 0.170, 7.0, None),
    ("Same folder, nothing changed\nrepeat run", 0.010, 7.0, "re-parses everything"),
    ("Same folder, daemon-served", 0.001, None, "no daemon — full re-parse"),
    ("68.2B-token production scan\n9 agents, real pipeline", 14.0, 1800.0, None),
]

def fmt(s):
    if s < 0.01:
        return "<1 ms" if s <= 0.001 else f"{s*1000:.0f} ms"
    if s < 1:
        return f"{s*1000:.0f} ms"
    return f"{s:.0f} s" if s < 60 else f"{s/60:.0f}+ min"

y_pos = list(range(len(ROWS)))[::-1]
for (label, tt, cc, note), y in zip(ROWS, y_pos):
    axr.barh(y + 0.19, tt, height=0.34, color=GREEN)
    axr.annotate(fmt(tt), (tt, y + 0.19), textcoords="offset points",
                 xytext=(6, -3), color=GREEN, fontsize=11, fontweight="bold")
    if cc is not None:
        axr.barh(y - 0.19, cc, height=0.34, color=RED)
        txt = fmt(cc) + (f"  ({note})" if note else "")
        axr.annotate(txt, (cc, y - 0.19), textcoords="offset points",
                     xytext=(6, -3), color=RED, fontsize=11, fontweight="bold")
    else:
        axr.barh(y - 0.19, 7.0, height=0.34, color="#cf222e", alpha=0.25)
        axr.annotate(note, (7.0, y - 0.19), textcoords="offset points",
                     xytext=(6, -3), color=RED, fontsize=10.5, style="italic")

axr.set_yticks(y_pos)
axr.set_yticklabels([r[0] for r in ROWS], fontsize=11)
axr.set_xscale("log")
axr.set_xlim(8e-4, 8000)
axr.set_xlabel("Wall time (log scale)")
axr.set_title("The workloads you actually have", fontsize=14, pad=12)
axr.spines[["top", "right"]].set_visible(False)
axr.grid(axis="y", visible=False)
axr.set_xticks([0.001, 0.01, 0.1, 1, 10, 60, 600, 3600])
axr.set_xticklabels(["1 ms", "10 ms", "100 ms", "1 s", "10 s", "1 min", "10 min", "1 h"],
                    fontsize=10.5)

import matplotlib.patches as mpatches
axr.legend(handles=[mpatches.Patch(color=GREEN, label="turbotokens"),
                    mpatches.Patch(color=RED, label="ccusage")],
           frameon=False, loc="upper right", bbox_to_anchor=(0.99, 0.90))

fig.suptitle("Time to count N tokens — full cost report, no cache, identical logs (all measured)",
             fontsize=15, y=0.98)
fig.subplots_adjust(left=0.07, right=0.99, bottom=0.12, top=0.86)
fig.savefig(out_path)
print(f"wrote {out_path}")
