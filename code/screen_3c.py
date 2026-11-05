"""3C first-pass screening. Automatic relevance score, not a final decision."""
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REF = os.path.join(ROOT, "refs")

with open(os.path.join(REF, "candidates_3c.json"), encoding="utf-8") as f:
    rows = json.load(f)

WEIGHTS = [
    ("split conformal", 6), ("adaptive prediction set", 6), ("aps", 4), ("raps", 4),
    ("conditional coverage", 5), ("group", 3), ("mondrian", 4), ("risk control", 5),
    ("adaptive conformal", 5), ("non-exchangeable", 5), ("covariate shift", 4),
    ("language model", 4), ("llm", 4), ("survey", 3), ("review", 2),
    ("calibration", 2), ("coverage", 2), ("classification", 2), ("prediction set", 3),
]
NON_ML = ["finite element", "geometry", "antenna", "manifold", "lattice", "harmonic",
          "conformal mapping", "conformal field", "conformal laplacian"]

TITLE_OK = ["conformal", "coverage", "prediction set", "risk control", "calibration", "uncertainty"]
APP = ["herbal", "mask", "botanical", "cancer", "water", "crop", "weed", "solar", "wind",
       "market", "patient", "medical", "clinical", "forecast", "traffic", "energy",
       "mental", "skin", "lung", "agricultur", "groundwater", "weather"]

def score_row(r):
    title = (r.get("title") or "").lower()
    abstract = (r.get("abstract") or "").lower()
    text = title + " " + abstract
    if "conformal" not in text:
        return -1.0, "no conformal"
    if any(k in title for k in NON_ML) and "prediction" not in text:
        return -1.0, "non-ML conformal"
    if not any(k in title for k in TITLE_OK):
        if not ((r.get("cited_by") or 0) > 300 and "conformal" in abstract):
            return -1.0, "title off-topic"
    s = 0.0
    for kw, w in WEIGHTS:
        if kw in title:
            s += w
        elif kw in abstract:
            s += w * 0.5
    s += min((r.get("cited_by") or 0) / 100.0, 6.0)
    if any(k in title for k in APP):
        s -= 4.0
    return s, "ok"

scored = []
for r in rows:
    s, reason = score_row(r)
    scored.append((s, reason, r))
scored.sort(key=lambda x: -x[0])

out = []
for i, (s, reason, r) in enumerate(scored, 1):
    decision = "shortlist" if s >= 7.0 else ("borderline" if s >= 4.0 else "reject")
    out.append({
        "id": i, "score": round(s, 2), "decision": decision, "reason": reason,
        "title": r.get("title"), "year": r.get("year"), "venue": r.get("venue"),
        "doi": r.get("doi"), "url": r.get("url"),
        "queries": ";".join(r.get("queries", [])), "sources": ";".join(r.get("sources", [])),
        "cited_by": r.get("cited_by"),
    })

path = os.path.join(REF, "screening_3c.csv")
with open(path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

counts = {}
for r in out:
    counts[r["decision"]] = counts.get(r["decision"], 0) + 1
print("counts", counts, "total", len(out))
print("\ntop 40:")
for r in out[:40]:
    print("%s | %s | %s" % (r["score"], r["year"], (r["title"] or "")[:130]))
