"""Render figures from results JSON. No number is typed by hand."""
from __future__ import annotations

import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "paper", "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150, "font.size": 9, "axes.grid": True,
    "grid.alpha": 0.25, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})

METHOD_COLOR = {
    "threshold_raw": "#8C8C8C",
    "threshold_maxprob": "#B279A2",
    "threshold_trueclass": "#54A24B",
    "threshold_conformal": "#4C78A8",
    "conformal_naive": "#1F4E79",
    "conformal_aps": "#E45756",
}
METHOD_LABEL = {
    "threshold_raw": "raw threshold 0.90",
    "threshold_maxprob": "max-prob quantile",
    "threshold_trueclass": "true-class quantile",
    "threshold_conformal": "t = 1-q",
    "conformal_naive": "split conformal",
    "conformal_aps": "APS",
}
SCORE_COLOR = {"naive": "#4C78A8", "aps_rand": "#E45756", "aps_det": "#54A24B", "raps": "#B279A2"}
SCORE_LABEL = {"naive": "naive", "aps_rand": "APS randomized", "aps_det": "APS deterministic", "raps": "RAPS"}
STRENGTH_MARKER = {0.05: "o", 0.25: "s", 1.0: "^"}
STRENGTH_LABEL = {0.05: "strength 0.05 (44)", 0.25: "strength 0.25 (224)", 1.0: "strength 1.00 (898)"}


def load(name):
    with open(os.path.join(ROOT, "results", name), encoding="utf-8") as f:
        return json.load(f)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else float("nan")


def fig_equivalence():
    data = load("equiv_digits.json")["rows"]
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    for m in METHOD_COLOR:
        for s in STRENGTH_MARKER:
            sub = [r for r in data if r["score"] == m and r["strength"] == s and r["postprocess"] == "raw"]
            if not sub:
                continue
            ax.scatter(mean([r["size"] for r in sub]), mean([r["coverage"] for r in sub]),
                       s=52, marker=STRENGTH_MARKER[s], color=METHOD_COLOR[m],
                       edgecolor="white", linewidth=0.7, zorder=3)
    ax.axhline(0.90, color="#333333", linestyle="--", linewidth=1.0, zorder=1)
    ax.text(0.25, 0.906, "target 0.90", fontsize=7.5, color="#333333")
    ax.annotate("true-class = conformal = t = 1-q", xy=(1.39, 0.918), xytext=(1.40, 0.83),
                fontsize=7, color="#333333",
                arrowprops=dict(arrowstyle="-", color="#666666", linewidth=0.8))
    ax.set_xlabel("mean prediction-set size")
    ax.set_ylabel("empirical coverage")
    ax.set_xlim(0.15, 2.15)
    ax.set_ylim(0.25, 1.02)
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=METHOD_LABEL[m], markersize=5)
               for m, c in METHOD_COLOR.items()]
    handles += [plt.Line2D([], [], marker=mk, linestyle="", color="#666666",
                           label=STRENGTH_LABEL[s], markersize=5)
                for s, mk in STRENGTH_MARKER.items()]
    ax.legend(handles=handles, fontsize=6.3, ncol=2, loc="lower right", frameon=False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, "fig2_equivalence." + ext), bbox_inches="tight")
    plt.close(fig)
    print("[fig] fig2_equivalence")


def fig_forcing():
    rows = load("postprocess_digits.json")["rows"]
    pairs = {}
    for r in rows:
        key = (r["strength"], r["seed"], r["n_cal"], r["alpha"], r["score"])
        pairs.setdefault(key, {})[r["postprocess"]] = r
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    xs_all, ys_all = [], []
    for score, color in SCORE_COLOR.items():
        for strength, marker in STRENGTH_MARKER.items():
            xs, ys = [], []
            for key, v in pairs.items():
                if key[0] != strength or key[4] != score:
                    continue
                if "raw" not in v or "forced" not in v:
                    continue
                xs.append(v["raw"]["empty_rate"])
                ys.append(v["forced"]["coverage"] - v["raw"]["coverage"])
            if xs:
                ax.scatter(xs, ys, s=16, color=color, marker=marker, alpha=0.7, edgecolor="none")
                xs_all += xs
                ys_all += ys
    xs_all, ys_all = np.array(xs_all), np.array(ys_all)
    lim = max(0.05, float(np.nanmax(np.concatenate([xs_all, ys_all]))) * 1.05)
    ax.plot([0, lim], [0, lim], color="#333333", linestyle="--", linewidth=1.0)
    ax.text(lim * 0.50, lim * 0.56, "upper bound: delta = empty rate", fontsize=7.2, color="#333333")
    ax.set_xlabel("raw empty-set rate")
    ax.set_ylabel("coverage gain from forcing argmax")
    ax.set_xlim(-0.01, lim)
    ax.set_ylim(-0.01, lim)
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=SCORE_LABEL[s], markersize=5)
               for s, c in SCORE_COLOR.items()]
    handles += [plt.Line2D([], [], marker=mk, linestyle="", color="#666666",
                           label=STRENGTH_LABEL[s], markersize=5)
                for s, mk in STRENGTH_MARKER.items()]
    ax.legend(handles=handles, fontsize=6.3, ncol=2, loc="lower right", frameon=False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, "fig3_forcing." + ext), bbox_inches="tight")
    plt.close(fig)
    print("[fig] fig3_forcing  n=", len(xs_all), " mean delta=", round(float(ys_all.mean()), 3))


def fig_aci():
    data = load("aci_digits.json")["rows"]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.5))
    blocks = np.arange(1, 10)
    series = [("static", None, "#8C8C8C", "static calibration"),
              ("fixed", 0.02, "#1F9E75", "ACI, fixed alpha"),
              ("buggy", 0.02, "#E45756", "update with alpha_t")]
    for update, gamma, color, label in series:
        sub = [r for r in data if r["schedule"] == "linear" and r["update"] == update]
        if gamma is not None:
            sub = [r for r in sub if abs(r["gamma"] - gamma) < 1e-12]
        if not sub:
            continue
        cov = np.mean([r["block_cov"] for r in sub], axis=0)
        alp = np.mean([r["alpha_block"] for r in sub], axis=0)
        axes[0].plot(blocks, cov, marker="o", markersize=3, color=color, label=label)
        axes[1].plot(blocks, alp, marker="o", markersize=3, color=color, label=label)
    axes[0].axhline(0.90, color="#333333", linestyle="--", linewidth=1.0)
    axes[0].set_xlabel("block (noise sigma 0 -> 0.60)")
    axes[0].set_ylabel("block coverage")
    axes[0].set_ylim(0.20, 1.02)
    axes[0].set_title("coverage under progressive corruption", fontsize=9)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("block")
    axes[1].set_ylabel("alpha at block end (log)")
    axes[1].set_title("adaptation level", fontsize=9)
    axes[1].axhline(0.10, color="#333333", linestyle="--", linewidth=1.0)
    for ax in axes:
        ax.set_xticks(blocks)
        ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, "fig4_aci." + ext), bbox_inches="tight")
    plt.close(fig)
    print("[fig] fig4_aci")


def main():
    fig_equivalence()
    fig_forcing()
    fig_aci()


if __name__ == "__main__":
    main()
