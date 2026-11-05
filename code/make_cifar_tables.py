"""Render CIFAR-10 tables from results JSON."""
from __future__ import annotations

import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAB = os.path.join(ROOT, "paper", "tables")
os.makedirs(TAB, exist_ok=True)

METHODS = ["threshold_raw", "threshold_maxprob", "threshold_trueclass",
           "threshold_conformal", "conformal_naive", "conformal_aps"]
METHOD_LABEL = {
    "threshold_raw": "raw threshold 0.90",
    "threshold_maxprob": "max-prob quantile",
    "threshold_trueclass": "true-class quantile",
    "threshold_conformal": "t = 1-q",
    "conformal_naive": "split conformal",
    "conformal_aps": "APS",
}
SCORES = ["naive", "aps_rand", "aps_det", "raps"]
SCORE_LABEL = {"naive": "naive", "aps_rand": "APS randomized", "aps_det": "APS deterministic", "raps": "RAPS"}


def load(name):
    with open(os.path.join(ROOT, "results", name), encoding="utf-8") as f:
        return json.load(f)


def mean(xs):
    return float(np.mean(xs)) if xs else float("nan")


def group(rows, keys):
    out = defaultdict(list)
    for r in rows:
        out[tuple(r[k] for k in keys)].append(r)
    return out


def equivalence_table():
    rows = load("equiv_cifar.json")["rows"]
    out = [
        "# CIFAR-10, audit A: a calibrated threshold is split conformal",
        "",
        "alpha = 0.10, n_cal = 2000, 5 seeds, 10k official test set.",
        "Coverage is the mean over seeds. Raw keeps empty sets; forced fills them with the argmax.",
        "",
        "| n_train | method | coverage raw | coverage forced | size raw | empty raw |",
        "|---|---|---|---|---|---|",
    ]
    for n_train in sorted({r["n_train"] for r in rows}):
        sub = [r for r in rows if r["n_train"] == n_train]
        acc = mean([r["accuracy"] for r in sub if r["postprocess"] == "raw"])
        for m in METHODS:
            raw = [r for r in sub if r["score"] == m and r["postprocess"] == "raw"]
            frc = [r for r in sub if r["score"] == m and r["postprocess"] == "forced"]
            out.append("| %d | %s | %.3f | %.3f | %.3f | %.3f |" % (
                n_train, METHOD_LABEL[m],
                mean([r["coverage"] for r in raw]),
                mean([r["coverage"] for r in frc]),
                mean([r["size"] for r in raw]),
                mean([r["empty_rate"] for r in raw]),
            ))
        out.append("| %d | **accuracy** | **%.3f** | | | |" % (n_train, acc))
        out.append("")
    path = os.path.join(TAB, "table5_cifar_equivalence.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def postprocess_table():
    rows = load("postprocess_cifar.json")["rows"]
    out = [
        "# CIFAR-10, audit B: non-empty post-processing inflates coverage",
        "",
        "alpha = 0.10, n_cal = 2000, 5 seeds, 10k official test set.",
        "Delta = forced coverage - raw coverage. Raw empty is the share of empty sets.",
        "",
        "| n_train | score | coverage raw | coverage forced | delta | empty raw | size raw | size forced |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for n_train in sorted({r["n_train"] for r in rows}):
        sub = [r for r in rows if r["n_train"] == n_train and abs(r["alpha"] - 0.10) < 1e-9 and r["n_cal"] == 2000]
        for s in SCORES:
            raw = [r for r in sub if r["score"] == s and r["postprocess"] == "raw"]
            frc = [r for r in sub if r["score"] == s and r["postprocess"] == "forced"]
            if not raw:
                continue
            out.append("| %d | %s | %.3f | %.3f | %+.3f | %.3f | %.3f | %.3f |" % (
                n_train, SCORE_LABEL[s],
                mean([r["coverage"] for r in raw]),
                mean([r["coverage"] for r in frc]),
                mean([r["coverage"] for r in frc]) - mean([r["coverage"] for r in raw]),
                mean([r["empty_rate"] for r in raw]),
                mean([r["size"] for r in raw]),
                mean([r["size"] for r in frc]),
            ))
        out.append("")
    path = os.path.join(TAB, "table6_cifar_postprocess.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def aci_table():
    rows = load("aci_cifar.json")["rows"]
    out = [
        "# CIFAR-10, audit C: the alpha_t update is not ACI",
        "",
        "2,000 test images in 20 blocks, Gaussian pixel noise ramping from 0 to 0.40.",
        "3 seeds, alpha = 0.10. Min/max block are computed on the seed-averaged block curve.",
        "",
        "| update | gamma | coverage | seed SD | size | min block | max block | alpha final | clip | sets >= 9 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    specs = [("static", None), ("fixed", 0.02), ("fixed", 0.05), ("buggy", 0.02), ("buggy", 0.05)]
    for update, gamma in specs:
        s2 = [r for r in rows if r["update"] == update and (gamma is None or abs(r["gamma"] - gamma) < 1e-12)]
        if not s2:
            continue
        block = np.mean([r["block_cov"] for r in s2], axis=0)
        out.append("| %s | %s | %.3f | %.3f | %.2f | %.3f | %.3f | %.4f | %.2f | %.3f |" % (
            update, "—" if gamma is None else "%.2f" % gamma,
            mean([r["coverage"] for r in s2]),
            float(np.std([r["coverage"] for r in s2], ddof=1)),
            mean([r["size"] for r in s2]),
            float(block.min()), float(block.max()),
            mean([r["alpha_final"] for r in s2]),
            mean([r["clip_fraction"] for r in s2]),
            mean([r["frac_sets_ge9"] for r in s2]),
        ))
    out.append("")
    path = os.path.join(TAB, "table7_cifar_aci.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def main():
    equivalence_table()
    postprocess_table()
    aci_table()


if __name__ == "__main__":
    main()
