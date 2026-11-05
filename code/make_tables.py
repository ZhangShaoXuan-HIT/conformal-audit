"""Render tables from results JSON. No number is typed by hand."""
from __future__ import annotations

import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAB = os.path.join(ROOT, "paper", "tables")
os.makedirs(TAB, exist_ok=True)

LABELS = {
    "threshold_raw": "softmax threshold, raw t = 1-alpha",
    "threshold_maxprob": "threshold at max-prob quantile",
    "threshold_trueclass": "threshold at true-class quantile",
    "threshold_conformal": "threshold at t = 1-q (conformal)",
    "conformal_naive": "split conformal, naive score",
    "conformal_aps": "split conformal, APS",
}
ORDER = list(LABELS)
SCORES = ["naive", "aps_rand", "aps_det", "raps"]
SCORE_LABEL = {"naive": "naive", "aps_rand": "APS randomized", "aps_det": "APS deterministic", "raps": "RAPS"}
GAMMAS = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2]


def load(name):
    with open(os.path.join(ROOT, "results", name), encoding="utf-8") as f:
        return json.load(f)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else float("nan")


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
            out.append("| %s | %.3f | %.3f | %.3f | %.3f | %.3f |" % (
                LABELS[m],
                mean(cells[(s, m, "raw")]["coverage"]),
                mean(cells[(s, m, "forced")]["coverage"]),
                mean(cells[(s, m, "raw")]["size"]),
                mean(cells[(s, m, "forced")]["size"]),
                mean(cells[(s, m, "raw")]["empty"]),
            ))
        out.append("")
    path = os.path.join(TAB, "table2_equivalence.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def postprocess_table():
    data = load("postprocess_digits.json")
    rows = data["rows"]
    alpha = 0.10
    out = [
        "# Table 3. Non-empty post-processing inflates coverage",
        "",
        "digits, alpha = 0.10, 5 seeds. Delta = forced coverage - raw coverage.",
        "Raw empty is the share of sets that were empty before the argmax was forced in.",
        "",
    ]
    for strength in sorted({r["strength"] for r in rows}):
        sub = [r for r in rows if abs(r["strength"] - strength) < 1e-12 and abs(r["alpha"] - alpha) < 1e-12]
        if not sub:
            continue
        by = {}
        for r in sub:
            by[(r["seed"], r["n_cal"], r["score"], r["postprocess"])] = r
        n_train = sorted({r["n_train"] for r in sub})[0]
        n_cals = sorted({r["n_cal"] for r in sub})
        seeds = sorted({r["seed"] for r in sub})
        out += [
            "## strength = %.2f (n_train = %d)" % (strength, n_train),
            "",
            "| score | n_cal | coverage raw | coverage forced | delta | empty raw | size raw | size forced |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for score in SCORES:
            for n_cal in n_cals:
                keys = [(s, n_cal, score, "raw") for s in seeds]
                kf = [(s, n_cal, score, "forced") for s in seeds]
                if not all(k in by for k in keys + kf):
                    continue
                raw = mean([by[k]["coverage"] for k in keys])
                forced = mean([by[k]["coverage"] for k in kf])
                out.append("| %s | %d | %.3f | %.3f | %+.3f | %.3f | %.3f | %.3f |" % (
                    SCORE_LABEL[score], n_cal, raw, forced, forced - raw,
                    mean([by[k]["empty_rate"] for k in keys]),
                    mean([by[k]["size"] for k in keys]),
                    mean([by[k]["size"] for k in kf]),
                ))
        out.append("")
    path = os.path.join(TAB, "table3_postprocess.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def aci_table():
    data = load("aci_digits.json")
    rows = data["rows"]
    out = [
        "# Table 4. The alpha_t update is not ACI",
        "",
        "digits, alpha = 0.10, 5 seeds. Coverage and size are means over seeds.",
        "Min/max block are computed on the seed-averaged block curve. Clip is the share of steps at a clip bound.",
        "",
    ]
    for schedule in ["linear", "step", "abrupt"]:
        sub = [r for r in rows if r["schedule"] == schedule]
        if not sub:
            continue
        out += [
            "## schedule = %s" % schedule,
            "",
            "| update | gamma | coverage | seed SD | size | min block | max block | alpha final | clip | sets >= 9 |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        specs = [("static", None)] + [("fixed", g) for g in GAMMAS] + [("buggy", g) for g in GAMMAS]
        for update, gamma in specs:
            s2 = [r for r in sub if r["update"] == update and (gamma is None or abs(r["gamma"] - gamma) < 1e-12)]
            if not s2:
                continue
            block = np.mean([r["block_cov"] for r in s2], axis=0)
            out.append("| %s | %s | %.3f | %.3f | %.3f | %.3f | %.3f | %.4f | %.3f | %.3f |" % (
                update,
                "—" if gamma is None else "%.3f" % gamma,
                mean([r["coverage"] for r in s2]),
                float(np.std([r["coverage"] for r in s2], ddof=1)),
                mean([r["size"] for r in s2]),
                float(block.min()), float(block.max()),
                mean([r["alpha_final"] for r in s2]),
                mean([r["clip_fraction"] for r in s2]),
                mean([r["frac_sets_ge9"] for r in s2]),
            ))
        out.append("")
    path = os.path.join(TAB, "table4_aci.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def main():
    equivalence_table()
    postprocess_table()
    aci_table()


if __name__ == "__main__":
    main()
