import json, os
ROOT = r"C:\Users\18372\Documents\cp-audit"
bib = json.load(open(os.path.join(ROOT, "refs", "bib.json"), encoding="utf-8"))
bib["Blackard1998"] = {
    "authors": "Blackard J A", "title": "Covertype",
    "venue": "UCI Machine Learning Repository", "year": 1998,
    "status": "dataset", "doi": "10.24432/C50K5N",
    "url": "https://doi.org/10.24432/C50K5N",
}
json.dump(bib, open(os.path.join(ROOT, "refs", "bib.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cited = json.load(open(os.path.join(ROOT, "refs", "cited_keys.json"), encoding="utf-8"))
if "Blackard1998" not in cited:
    cited.append("Blackard1998")
json.dump(cited, open(os.path.join(ROOT, "refs", "cited_keys.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cited", len(cited))
