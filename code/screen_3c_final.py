"""Attach final decisions to the 3C search log.

include: selected into bib.json
defer:   shortlisted but not read; not rejected
exclude: auto-screened out
"""
import csv, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\18372\Documents\cp-audit"
REF = os.path.join(ROOT, "refs")

with open(os.path.join(REF, "bib.json"), encoding="utf-8") as f:
    bib = json.load(f)
def norm(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())
by_title = {norm(v["title"]): k for k, v in bib.items()}

with open(os.path.join(REF, "screening_3c.csv"), encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

counts = {}
for r in rows:
    key = by_title.get(norm(r["title"]))
    if key:
        r["final_decision"] = "include"
        r["bib_key"] = key
        r["bib_source"] = bib[key]["source"]
    elif r["decision"] in ("shortlist", "borderline"):
        r["final_decision"] = "defer"
        r["bib_key"] = ""
        r["bib_source"] = ""
    else:
        r["final_decision"] = "exclude"
        r["bib_key"] = ""
        r["bib_source"] = ""
    counts[r["final_decision"]] = counts.get(r["final_decision"], 0) + 1

fields = list(rows[0].keys())
with open(os.path.join(REF, "screening_3c_final.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(rows)
print("counts", counts, "rows", len(rows))
for r in rows:
    if r["final_decision"] == "include":
        print(r["bib_key"], "|", r["year"], "|", (r["title"] or "")[:110])
