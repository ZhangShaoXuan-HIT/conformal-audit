"""Cost-sensitive reading of the fallback, from the raw/forced rows.

a_E = delta / empty_rate, threshold c_a / c_e = 1 - a_E.
"""
import json, os, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\18372\Documents\cp-audit"

def load(name):
    return json.load(open(os.path.join(ROOT, "results", name), encoding="utf-8"))["rows"]

def pairs(rows, keys):
    d = {}
    for r in rows:
        k = tuple(r[x] for x in keys)
        d.setdefault(k, {})[r["postprocess"]] = r
    return d

KEYS = ["strength", "seed", "n_cal", "alpha", "score"]
files = {"digits": "postprocess_digits.json", "cifar10": "postprocess_cifar.json", "covertype": "tabular.json"}
agg = {}
for ds, fn in files.items():
    rows = [r for r in load(fn) if abs(r["alpha"] - 0.10) < 1e-9]
    for k, v in pairs(rows, KEYS).items():
        if "raw" not in v or "forced" not in v:
            continue
        e = v["raw"]["empty_rate"]
        if e <= 0:
            continue
        delta = v["forced"]["coverage"] - v["raw"]["coverage"]
        a = min(1.0, max(0.0, delta / e))
        strength, seed, n_cal, alpha, score = k
        agg.setdefault((ds, score), []).append((e, a))

lines = ["# Table 12. Cost-sensitive reading of the fallback", "",
         "At alpha = 0.10, over cells with a non-zero raw empty rate. a_E is the",
         "conditional accuracy of the inserted label on empty sets, estimated as",
         "delta / empty rate. The threshold is the cost ratio c_a / c_e above which",
         "forcing is better than abstaining.", "",
         "| dataset | score | cells | mean empty rate | mean a_E | threshold c_a/c_e |",
         "|---|---|---|---|---|---|"]
for ds in ["digits", "cifar10", "covertype"]:
    for score in ["aps_rand", "aps_det"]:
        vals = agg.get((ds, score), [])
        if not vals:
            continue
        e = float(np.mean([x[0] for x in vals]))
        a = float(np.mean([x[1] for x in vals]))
        lines.append("| %s | %s | %d | %.3f | %.2f | %.2f |" % (ds, score, len(vals), e, a, 1 - a))
lines += ["", "The threshold is small in every dataset (0.01 to 0.06); the empty rate is not.",
          "The expected loss difference at a given cost ratio is proportional to the empty rate,",
          "so the same rule matters much more on digits than on covertype."]
open(os.path.join(ROOT, "paper", "tables", "table12_cost.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
