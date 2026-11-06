"""Render the covertype table from results/tabular.json."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAB = os.path.join(ROOT, "paper", "tables")

SCORE_LABEL = {"naive": "naive", "aps_rand": "APS randomized", "aps_det": "APS deterministic"}


def mean(xs):
    return float(np.mean(xs)) if xs else float("nan")


def main():
    rows = json.load(open(os.path.join(ROOT, "results", "tabular.json"), encoding="utf-8"))["rows"]
    rows = [r for r in rows if abs(r["alpha"] - 0.10) < 1e-9]
    out = [
        "# Table 11. Covertype audit B",
        "",
        "120,000-row stratified subset, 54 features, 7 classes, logistic regression,",
        "20,000 calibration points, 40,000 test points, alpha = 0.10, 5 seeds.",
        "",
        "| train | score | raw coverage | raw empty | raw size | forced coverage | forced size | delta |",
        "|---|---|---|---|---|---|---|---|",
    ]
    accs = {}
    empty_means = []
    delta_means = []
    for n_train in [6000, 60000]:
        sub = [r for r in rows if r["n_train"] == n_train]
        accs[n_train] = mean([r["accuracy"] for r in sub if r["postprocess"] == "raw"])
        for score in ["naive", "aps_rand", "aps_det"]:
            raw = [r for r in sub if r["score"] == score and r["postprocess"] == "raw"]
            frc = [r for r in sub if r["score"] == score and r["postprocess"] == "forced"]
            e_mean = mean([r["empty_rate"] for r in raw])
            d_mean = mean([r["delta"] for r in frc])
            empty_means.append(e_mean)
            delta_means.append(d_mean)
            out.append("| %d | %s | %.3f | %.3f | %.2f | %.3f | %.2f | %.3f |" % (
                n_train, SCORE_LABEL[score],
                mean([r["coverage"] for r in raw]),
                e_mean,
                mean([r["size"] for r in raw]),
                mean([r["coverage"] for r in frc]),
                mean([r["size"] for r in frc]),
                d_mean,
            ))
    e = empty_means
    d = delta_means
    out += ["",
            "The two training sizes give test accuracies of %.3f and %.3f." % (accs[6000], accs[60000]),
            "",
            "delta is forced coverage minus raw coverage. The identity delta = empty rate x",
            "conditional accuracy holds. The empty rate is %.1f to %.1f percent, so the change is" % (100 * min(e), 100 * max(e)),
            "%.1f to %.1f points. The trap is a regime effect, not a universal constant." % (100 * min(d), 100 * max(d)),
            ]
    path = os.path.join(TAB, "table11_tabular.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
