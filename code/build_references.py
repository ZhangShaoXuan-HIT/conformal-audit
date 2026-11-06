import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\18372\Documents\cp-audit"
bib = json.load(open(os.path.join(ROOT, "refs", "bib.json"), encoding="utf-8"))

# verified metadata fixes
bib["Angelopoulos2021intro"].update({
    "title": "Conformal Prediction: A Gentle Introduction",
    "venue": "Foundations and Trends in Machine Learning 16(4), 494-591",
    "year": 2023, "status": "published",
    "doi": "10.1561/2200000101", "arxiv": "2107.07511",
    "url": "https://doi.org/10.1561/2200000101",
})
bib["Campos2024"]["venue"] = "Transactions of the Association for Computational Linguistics 12, 1497-1516"
bib["Hore2024"]["year"] = 2025
bib["Mehrtens2025"].update({"doi": None, "arxiv": "2506.18162",
                            "url": "https://arxiv.org/abs/2506.18162", "status": "preprint"})
for k in ["Combes2026", "Gauthier2025", "Oliveira2022"]:
    if k in bib and bib[k].get("venue") == "arXiv (Cornell University)":
        bib[k]["venue"] = "arXiv preprint"
bib["adaptiveconformal2023"]["venue"] = "arXiv preprint"

software = {
    "mapie2026": {"authors": "MAPIE contributors", "title": "MAPIE: a scikit-learn-contrib package for conformal prediction", "venue": "version 1.6.0", "year": 2026, "status": "software", "doi": None, "arxiv": None, "url": "https://pypi.org/project/mapie/", "source": "software"},
    "torchcp2026": {"authors": "TorchCP contributors", "title": "TorchCP: a Python library for conformal prediction", "venue": "version 1.2.1", "year": 2026, "status": "software", "doi": None, "arxiv": None, "url": "https://pypi.org/project/torchcp/", "source": "software"},
    "puncc2026": {"authors": "puncc contributors", "title": "puncc: predictive uncertainty calibration and conformal prediction", "venue": "version 0.9.3", "year": 2026, "status": "software", "doi": None, "arxiv": None, "url": "https://pypi.org/project/puncc/", "source": "software"},
    "crepes2026": {"authors": "crepes contributors", "title": "crepes: conformal regressors and predictive systems", "venue": "version 0.9.1", "year": 2026, "status": "software", "doi": None, "arxiv": None, "url": "https://pypi.org/project/crepes/", "source": "software"},
    "coverforest2026": {"authors": "coverforest contributors", "title": "coverforest: conformal prediction with random forests", "venue": "version 0.0.3", "year": 2026, "status": "software", "doi": None, "arxiv": None, "url": "https://pypi.org/project/coverforest/", "source": "software"},
    "adaptiveconformal2023": {"authors": "Susmann H, Chambaz A, Josse J", "title": "AdaptiveConformal: an R package for adaptive conformal inference", "venue": "arXiv preprint", "year": 2023, "status": "preprint", "doi": None, "arxiv": "2312.00448", "url": "https://github.com/herbps10/AdaptiveConformal", "source": "software"},
}
bib.update(software)
json.dump(bib, open(os.path.join(ROOT, "refs", "bib.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

cited = json.load(open(os.path.join(ROOT, "refs", "cited_keys.json"), encoding="utf-8"))
missing = [k for k in cited if k not in bib]
rows = sorted([(k, bib[k]) for k in cited], key=lambda x: x[1]["authors"].lower())

def fmt(v):
    authors = v["authors"].rstrip(".")
    bits = [authors + ".", v["title"] + "."]
    if v.get("venue"):
        bits.append(v["venue"] + ", " + str(v["year"]) + ".")
    if v.get("doi"):
        bits.append("DOI " + v["doi"] + ".")
    elif v.get("arxiv"):
        bits.append("arXiv:" + v["arxiv"] + ".")
    elif v.get("url"):
        bits.append(v["url"] + ".")
    if v.get("status") == "preprint":
        bits.append("Preprint.")
    return " ".join(bits).replace("--", "–")

lines = ["# References", ""]
for i, (k, v) in enumerate(rows, 1):
    lines.append(str(i) + ". " + fmt(v) + " <!-- " + k + " -->")
open(os.path.join(ROOT, "paper", "references.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("cited", len(cited), "missing", missing, "bib entries", len(bib))
print("\n".join(lines))
