"""Figure 1: the three-stage pipeline and the three trap locations."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "paper", "figures")

fig, ax = plt.subplots(figsize=(7.4, 3.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")

boxes = [
    (0.4, 2.2, 2.9, 1.5, "Fit f\non training data"),
    (3.7, 2.2, 2.9, 1.5, "Calibrate q\non held-out data"),
    (7.0, 2.2, 2.7, 1.5, "Threshold\nC(x) = {y : s(x,y) ≤ q}"),
]
for x, y, w, h, label in boxes:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                                linewidth=1.2, edgecolor="#1F4E79", facecolor="#EAF2FB"))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9, color="#1F3864")

for x1, x2 in [(3.3, 3.7), (6.6, 7.0)]:
    ax.add_patch(FancyArrowPatch((x1, 2.95), (x2, 2.95), arrowstyle="-|>",
                                 mutation_scale=12, linewidth=1.2, color="#1F4E79"))

ax.text(5.15, 4.25, "trap 1: which threshold is calibrated",
        ha="center", va="center", fontsize=8.5, color="#E45756")
ax.add_patch(FancyArrowPatch((5.15, 4.05), (5.15, 3.75), arrowstyle="-|>",
                             mutation_scale=10, linewidth=1.0, color="#E45756"))

ax.text(8.35, 1.55, "trap 2: empty set → argmax",
        ha="center", va="center", fontsize=8.5, color="#E45756")
ax.add_patch(FancyArrowPatch((8.35, 1.75), (8.35, 2.15), arrowstyle="-|>",
                             mutation_scale=10, linewidth=1.0, color="#E45756"))

ax.add_patch(FancyArrowPatch((8.35, 2.1), (5.15, 2.1), connectionstyle="arc3,rad=0.35",
                             arrowstyle="-|>", mutation_scale=11, linewidth=1.1, color="#E45756"))
ax.text(6.75, 0.95, "trap 3: α_t instead of α", ha="center", va="center",
        fontsize=8.5, color="#E45756")

ax.text(5.0, 0.25, "the same three stages in every method; the guarantee comes from the middle one",
        ha="center", va="center", fontsize=8, color="#444444")

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, "fig1_pipeline." + ext), bbox_inches="tight")
plt.close(fig)
print("[fig] fig1_pipeline")
