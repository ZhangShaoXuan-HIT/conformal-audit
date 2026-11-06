"""Figure 1: the conformal pipeline and the three places the number can move.

Nature-style schematic: thin lines, muted palette, numbered trap markers,
solid boxes for method stages and a dashed box for the reporting step.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "paper", "figures")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7.5,
    "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

INK = "#1F2933"
MUTED = "#5B6773"
LINE = "#4B5563"
EDGE = "#2F3E4E"
FILL = "#F7F9FB"
RED = "#B5524C"
TEAL = "#2F6F7E"

fig, ax = plt.subplots(figsize=(7.2, 2.9))
ax.set_xlim(0, 10)
ax.set_ylim(0.45, 3.65)
ax.axis("off")

boxes = [
    (0.25, 1.85, 1.95, 1.10, "Fit $f$", "on training data", False),
    (2.75, 1.85, 1.95, 1.10, "Calibrate $q$", "on held-out data", False),
    (5.25, 1.85, 1.95, 1.10, "Set $C(x)$", r"$\{y:\ s(x,y) \leq q\}$", False),
    (7.75, 1.85, 1.95, 1.10, "Report", "coverage on test data", True),
]

for x, y, w, h, title, subtitle, dashed in boxes:
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=0.8,
        edgecolor=MUTED if dashed else EDGE,
        facecolor="#FCFCFC" if dashed else FILL,
        linestyle=(0, (2.5, 1.5)) if dashed else "solid",
        zorder=2,
    ))
    cx, cy = x + w / 2, y + h / 2
    ax.text(cx, cy + 0.22, title, ha="center", va="center",
            fontsize=8.2, fontweight="bold", color=INK, zorder=3)
    ax.text(cx, cy - 0.03, subtitle, ha="center", va="center",
            fontsize=6.8, color=MUTED, zorder=3)

# the guarantee belongs to stage 2; put it inside the box as a third line
ax.text(3.725, 2.13, "finite-sample guarantee", ha="center", va="center",
        fontsize=6.2, color=TEAL, zorder=3)

for x0, x1 in [(2.20, 2.75), (4.70, 5.25), (7.20, 7.75)]:
    ax.add_patch(FancyArrowPatch(
        (x0, 2.40), (x1, 2.40), arrowstyle="-|>", mutation_scale=8,
        linewidth=0.8, color=LINE, shrinkA=0, shrinkB=0, zorder=4,
    ))

# trap 1: above the calibration box
ax.add_patch(Circle((3.725, 3.28), 0.125, facecolor=RED, edgecolor="white",
                    linewidth=0.5, zorder=6))
ax.text(3.725, 3.28, "1", ha="center", va="center", fontsize=6.6,
        fontweight="bold", color="white", zorder=7)
ax.plot([3.725, 3.725], [3.155, 2.96], color=RED, linewidth=0.6, zorder=5)

# trap 2: between the set and the report, below the feedback arc
ax.add_patch(Circle((7.475, 1.18), 0.125, facecolor=RED, edgecolor="white",
                    linewidth=0.5, zorder=6))
ax.text(7.475, 1.18, "2", ha="center", va="center", fontsize=6.6,
        fontweight="bold", color="white", zorder=7)
ax.plot([7.475, 7.475], [1.305, 1.37], color=RED, linewidth=0.6, zorder=5)

# trap 3: the feedback arrow from report to calibration
ax.add_patch(FancyArrowPatch(
    (8.725, 1.85), (3.725, 1.85),
    connectionstyle="arc3,rad=-0.26",
    arrowstyle="-|>", mutation_scale=8, linewidth=0.8,
    linestyle=(0, (2.5, 1.5)), color=RED, zorder=4,
))
ax.add_patch(Circle((5.35, 1.02), 0.125, facecolor=RED, edgecolor="white",
                    linewidth=0.5, zorder=6))
ax.text(5.35, 1.02, "3", ha="center", va="center", fontsize=6.6,
        fontweight="bold", color="white", zorder=7)
ax.plot([5.35, 5.35], [1.145, 1.26], color=RED, linewidth=0.6, zorder=5)

# two-row key: visual grammar, then trap names
ax.plot([0.30, 0.62], [0.88, 0.88], color=EDGE, linewidth=0.8)
ax.text(0.68, 0.88, "method stage", ha="left", va="center", fontsize=6.4, color=MUTED)
ax.plot([2.00, 2.32], [0.88, 0.88], color=MUTED, linewidth=0.8, linestyle=(0, (2.5, 1.5)))
ax.text(2.38, 0.88, "reporting step", ha="left", va="center", fontsize=6.4, color=MUTED)
ax.add_patch(Circle((3.95, 0.88), 0.075, facecolor=RED, edgecolor="white", linewidth=0.4))
ax.text(4.07, 0.88, "trap", ha="left", va="center", fontsize=6.4, color=MUTED)

for x, num, label in [
    (0.30, "1", "threshold calibration"),
    (3.10, "2", "empty-set fallback"),
    (6.15, "3", r"$\alpha_t$ update"),
]:
    ax.text(x, 0.60, num, color=RED, fontsize=6.6, fontweight="bold",
            ha="left", va="center")
    ax.text(x + 0.18, 0.60, label, color=MUTED, fontsize=6.5, ha="left", va="center")

fig.subplots_adjust(0, 0, 1, 1)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, "fig1_pipeline." + ext),
                dpi=600 if ext == "png" else None,
                bbox_inches="tight", pad_inches=0.04, facecolor="white")
plt.close(fig)
print("[fig] fig1_pipeline")
