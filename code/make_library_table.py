"""Render Table 8: library behavior audit.

The MAPIE numbers come from results/mapie_empty.json. The source evidence is
static and version-specific; line numbers refer to the versions in _libs/src.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAB = os.path.join(ROOT, "paper", "tables")
os.makedirs(TAB, exist_ok=True)

with open(os.path.join(ROOT, "results", "mapie_empty.json"), encoding="utf-8") as f:
    mapie = json.load(f)
summary = {(r["score"], r["include_last_label"]): r for r in mapie["summary"]}

LIBS = [
    ("MAPIE", "1.6.0", "classification",
     "LAC yes; APS policy-dependent",
     "APS default include_last_label=True: no empty sets, coverage 0.9457 vs 0.90",
     "classification.py:238-283; aps.py:355-358; lac.py:205-207; results/mapie_empty.json",
     "fixed alpha_0 (time_series_regression.py:329)"),
    ("TorchCP", "1.2.1", "classification",
     "yes",
     "no forcing; boolean mask (scores <= q_hat)",
     "classification/predictor/base.py:111",
     "fixed alpha (regression/predictor/aci.py:197)"),
    ("puncc", "0.9.3", "classification",
     "yes",
     "no forcing; index lists, empty when no class passes",
     "api/prediction_sets.py:70-78, 112-119",
     "not implemented"),
    ("crepes", "0.9.1", "classification",
     "yes",
     "no forcing; boolean mask (p_values >= 1-confidence)",
     "base.py:340",
     "not implemented"),
    ("coverforest", "0.0.3", "classification",
     "yes by default",
     "allow_empty_sets=True default; False avoids empty sets; docs warn to use it sparingly",
     "_forest.py:1457, 2006-2008",
     "not applicable"),
    ("AdaptiveConformal", "GitHub main", "regression intervals",
     "not applicable",
     "not applicable",
     "R/aci_algorithm.R:78-81",
     "fixed alpha (correct)"),
]

out = [
    "# Table 8. Library behavior audit",
    "",
    "Versions checked on 2026-11-06. Line numbers refer to the sources in _libs/src.",
    "Only MAPIE was run; the other rows are source inspection.",
    "",
    "| library | version | task | empty sets possible | default policy | evidence | ACI update |",
    "|---|---|---|---|---|---|---|",
]
for row in LIBS:
    out.append("| " + " | ".join(row) + " |")

out += [
    "",
    "## MAPIE 1.6.0, five seeds, alpha = 0.10",
    "",
    "Synthetic five-class data, logistic regression, 2,000 test points per seed.",
    "The correct randomised APS is the last row. The default is the second row.",
    "",
    "| score | include_last_label | coverage (mean +/- SD) | empty rate | size |",
    "|---|---|---|---|---|",
]
for score, inc, label in [
    ("lac", "True", "LAC"),
    ("aps", "True", "APS, default"),
    ("aps", "False", "APS"),
    ("aps", "randomized", "APS, randomized"),
]:
    r = summary[(score, inc)]
    out.append("| %s | %s | %.4f +/- %.4f | %.4f | %.3f |" % (
        label, inc, r["coverage_mean"], r["coverage_sd"], r["empty_rate_mean"], r["size_mean"]))

out += [
    "",
    "The default APS setting over-covers by 4.6 points with zero empty sets. The randomised",
    "setting, which is the exact conformal rule, lands on the target. The difference is the",
    "non-empty post-processing, not the score.",
]

path = os.path.join(TAB, "table8_libraries.md")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
