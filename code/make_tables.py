"""Render tables from results JSON. No number is typed by hand."""
from __future__ import annotations

import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LABELS = {
    "threshold_raw": "softmax threshold, raw t = 1-alpha",
    "threshold_maxprob": "threshold at max-prob quantile",
    "threshold_trueclass": "threshold at true-class quantile",
    "threshold_conformal": "threshold at t = 1-q (conformal)",
    "conformal_naive": "split conformal, naive score",
    "conformal_aps": "split conformal, APS",
}
ORDER = list(LABELS)


def load(name):
    with open(os.path.join(ROOT, "results", name), encoding="utf-8") as f:
        return json.load(f)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def equivalence_table():
    data = load("equiv_digits.json")
    rows = data["rows"]
    checks = data.get("checks", {})
    cells = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = (r["strength"], r["score"], r["postprocess"])
        cells[key]["coverage"].append(r["coverage"])
        cells[key]["size"].append(r["size"])
        cells[key]["empty"].append(r["empty_rate"])

    strengths = sorted({r["strength"] for r in rows})
    alpha = rows[0]["alpha"]
    n_cal = rows[0]["n_cal"]
    out = [
        "# Table 2. A calibrated threshold is split conformal",
        "",
        "digits, alpha = %.2f, n_cal = %d, 5 seeds. Coverage is the mean over seeds." % (alpha, n_cal),
        "Raw keeps empty sets; forced fills them with the argmax. Size is mean cardinality.",
        "Pointwise set equality between the conformal threshold and split conformal: mismatches = %s." % checks.get("set_mismatches", "n/a"),
        "",
    ]
    for s in strengths:
        n_train = sorted({r["n_train"] for r in rows if r["strength"] == s})[0]
        out += [
            "## strength = %.2f (n_train = %d)" % (s, n_train),
            "",
            "| method | coverage raw | coverage forced | size raw | size forced | empty raw |",
            "|---|---|---|---|---|---|",
        ]
        for m in ORDER:
            c_raw = mean(cells[(s, m, "raw")]["coverage"])
            c_for = mean(cells[(s, m, "forced")]["coverage"])
            z_raw = mean(cells[(s, m, "raw")]["size"])
            z_for = mean(cells[(s, m, "forced")]["size"])
            e_raw = mean(cells[(s, m, "raw")]["empty"])
            out.append("| %s | %.3f | %.3f | %.3f | %.3f | %.3f |" % (
                LABELS[m], c_raw, c_for, z_raw, z_for, e_raw))
        out.append("")
    os.makedirs(os.path.join(ROOT, "paper", "tables"), exist_ok=True)
    path = os.path.join(ROOT, "paper", "tables", "table2_equivalence.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    print("\nwritten:", path)


if __name__ == "__main__":
    equivalence_table()
