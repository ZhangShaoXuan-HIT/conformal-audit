import json, os
ROOT = r"C:\Users\18372\Documents\cp-audit"
bib = json.load(open(os.path.join(ROOT, "refs", "bib.json"), encoding="utf-8"))
bib["nonconformist2017"] = {
    "authors": "Linusson H",
    "title": "nonconformist: Python implementation of the conformal prediction framework",
    "venue": "version 2.1.0", "year": 2017, "status": "software",
    "doi": None, "arxiv": None, "url": "https://github.com/donlnz/nonconformist",
    "source": "software",
}
bib["conformal2017"] = {
    "authors": "Koul A",
    "title": "conformal: a minimal conformal prediction implementation for classification",
    "venue": "version 0.1", "year": 2017, "status": "software",
    "doi": None, "arxiv": None, "url": "https://pypi.org/project/conformal/",
    "source": "software",
}
json.dump(bib, open(os.path.join(ROOT, "refs", "bib.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cited = json.load(open(os.path.join(ROOT, "refs", "cited_keys.json"), encoding="utf-8"))
for k in ["nonconformist2017", "conformal2017"]:
    if k not in cited:
        cited.append(k)
json.dump(cited, open(os.path.join(ROOT, "refs", "cited_keys.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cited", len(cited))
