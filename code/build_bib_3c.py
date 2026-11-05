"""Build refs/bib.json: 35 seeds + 6 classics + selected 2023-2026 methods."""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\18372\Documents\cp-audit"
SRC = r"C:\Users\18372\WorkBuddy AI\2026-11-04-14-19-29\共形预测综述_完整材料包\03_文献清单与检索"

with open(os.path.join(SRC, "refs_complete_35条.json"), encoding="utf-8") as f:
    seed = json.load(f)["refs"]

def parse_ids(extra):
    doi = None; arx = None
    m = re.search(r"10\.\d{4,9}/[^\s,;]+", extra or "")
    if m: doi = m.group(0).rstrip(".")
    m = re.search(r"arXiv:(\d{4}\.\d{4,5})", extra or "")
    if m: arx = m.group(1)
    return doi, arx

bib = {}
for r in seed:
    doi, arx = parse_ids(r.get("extra", ""))
    bib[r["key"]] = {
        "authors": r["authors"], "title": r["title"], "venue": r["venue"],
        "year": r["year"], "status": r.get("status", "published"),
        "doi": doi, "arxiv": arx,
        "url": ("https://doi.org/" + doi) if doi else (("https://arxiv.org/abs/" + arx) if arx else ""),
        "source": "seed",
    }

CLASSICS = {
    "Papadopoulos2002": {
        "authors": "Papadopoulos H, Proedrou K, Vovk V, Gammerman A",
        "title": "Inductive Confidence Machines for Regression",
        "venue": "ECML 2002, Lecture Notes in Computer Science 2430, 345-356",
        "year": 2002, "status": "published",
        "doi": "10.1007/3-540-36755-1_29", "arxiv": None,
        "url": "https://doi.org/10.1007/3-540-36755-1_29", "source": "classic",
    },
    "Balasubramanian2014": {
        "authors": "Balasubramanian V N, Ho S-S, Vovk V",
        "title": "Conformal Prediction for Reliable Machine Learning: Theory, Adaptations and Applications",
        "venue": "Morgan Kaufmann",
        "year": 2014, "status": "published",
        "doi": "10.1016/C2012-0-00234-7", "arxiv": None,
        "url": "https://doi.org/10.1016/C2012-0-00234-7", "source": "classic",
    },
    "Vovk2012": {
        "authors": "Vovk V",
        "title": "Conditional validity of inductive conformal predictors",
        "venue": "ACML 2012, PMLR 25, 475-490",
        "year": 2012, "status": "published",
        "doi": None, "arxiv": None,
        "url": "https://proceedings.mlr.press/v25/vovk12.html", "source": "classic",
    },
    "Barber2021Jackknife": {
        "authors": "Barber R F, Candes E J, Ramdas A, Tibshirani R J",
        "title": "Predictive inference with the jackknife+",
        "venue": "Annals of Statistics 49(1), 486-507",
        "year": 2021, "status": "published",
        "doi": "10.1214/20-AOS1965", "arxiv": "1905.02928",
        "url": "https://doi.org/10.1214/20-AOS1965", "source": "classic",
    },
    "Romano2019CQR": {
        "authors": "Romano Y, Patterson E, Candes E J",
        "title": "Conformalized Quantile Regression",
        "venue": "Advances in Neural Information Processing Systems 32 (NeurIPS 2019)",
        "year": 2019, "status": "published",
        "doi": None, "arxiv": "1905.03222",
        "url": "https://arxiv.org/abs/1905.03222", "source": "classic",
    },
    "Fontana2023": {
        "authors": "Fontana M, Zeni G, Vantini S",
        "title": "Conformal prediction: A unified review of theory and new challenges",
        "venue": "Bernoulli 29(1), 1-23",
        "year": 2023, "status": "published",
        "doi": "10.3150/21-BEJ1447", "arxiv": "2005.07972",
        "url": "https://doi.org/10.3150/21-BEJ1447", "source": "classic",
    },
}
bib.update(CLASSICS)

# merge all candidate files for matching
cands = []
for name in ["candidates.json", "candidates2.json", "candidates_3c.json"]:
    p = os.path.join(ROOT, "refs", name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            cands.extend(json.load(f))

def norm(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())

RECENT = [
    "Pitfalls of Conformal Predictions for Medical Image Classification",
    "What Split Conformal Prediction Guarantees",
    "Adaptive Coverage Policies in Conformal Prediction",
    "Certified Label-Free Drift Alarms",
    "Benchmarking non-conformity score functions",
    "Kandinsky Conformal Prediction",
    "A Unified Theory of Conditional Coverage",
    "Conformal Prediction Sets with Improved Conditional Coverage using Trust Scores",
    "Sample-Conditional Coverage in Split-Conformal Prediction",
    "Conformal Prediction for Class-wise Coverage via Augmented Label Rank Calibration",
    "Beyond conformal predictors: Adaptive Conformal Inference",
    "Adaptive Conformal Inference through the Lens of Blackwell Approachability",
    "Automatically Adaptive Conformal Risk Control",
    "Multiply Robust Conformal Risk Control",
    "Macro Mondrian Conformal Risk Control",
    "Split Conformal Prediction under Data Contamination",
    "Sharp training-conditional coverage",
    "Training-Conditional Coverage Bounds under Covariate Shift",
    "Split Conformal Prediction and Non-Exchangeable Data",
    "Conformal Tail Risk Control for Large Language Model Alignment",
    "Multi-LLM Adaptive Conformal Inference",
    "Beyond Aggregate Risk: Role-Stratified Conformal Risk Control",
    "Confidence on the Focal",
    "A Few Observations on Sample-Conditional Coverage",
    "Spectral Adaptive Conformal Prediction",
    "Hybrid Adaptive Prediction Sets",
    "Ensuring Calibration Robustness in Split Conformal Prediction",
    "Locally Adaptive Conformal Inference for Operator Models",
]

def fmt_authors(names):
    out = []
    for n in (names or [])[:6]:
        s = str(n).strip()
        if "," in s:
            surname, given = s.split(",", 1)
            initials = "".join(p[0] for p in re.split(r"[\s.]+", given.strip()) if p)
        else:
            parts = re.split(r"\s+", s)
            if len(parts) >= 2:
                surname = parts[-1]
                initials = "".join(p[0] for p in parts[:-1] if p)
            else:
                surname, initials = s, ""
        out.append((surname.strip() + " " + initials).strip())
    return ", ".join(out)

def find(title_part):
    key = norm(title_part)
    best = None
    for c in cands:
        if key in norm(c.get("title")):
            if best is None or (c.get("year") or 0) > (best.get("year") or 0):
                best = c
    return best

used = set()
missing = []
for title in RECENT:
    c = find(title)
    if c is None:
        missing.append(title); continue
    year = c.get("year") or 0
    authors = fmt_authors(c.get("authors"))
    surname = authors.split(",")[0].split()[0] if authors else "Anon"
    surname = re.sub(r"[^A-Za-z]", "", surname) or "Anon"
    key = surname + str(year)
    while key in bib or key in used:
        key += "x"
    used.add(key)
    doi = c.get("doi")
    if doi and "openalex.org" in doi:
        doi = None
    if doi and doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")
    arx = None
    m = re.search(r"abs/(\d{4}\.\d{4,5})", c.get("url") or "")
    if m: arx = m.group(1)
    venue = c.get("venue") or ""
    status = "preprint" if (venue.startswith("arXiv")
        or any(k in venue for k in ["Zenodo", "SSRN", "Research Square"])
        or (doi is None and arx)) else "published"
    bib[key] = {
        "authors": authors, "title": c.get("title"), "venue": venue,
        "year": year, "status": status, "doi": doi, "arxiv": arx,
        "url": c.get("url") or (("https://doi.org/" + doi) if doi else ""),
        "source": "recent",
    }

# manual metadata fixes
if "Duchi2025" in bib:
    bib["Duchi2025"]["authors"] = "Duchi J"
if "Bataineh2026" in bib:
    bib["Bataineh2026"]["authors"] = "Al Bataineh A"
if "Messoudi2026" in bib:
    bib["Messoudi2026"]["status"] = "preprint"
    bib["Messoudi2026"]["venue"] = "HAL preprint"

with open(os.path.join(ROOT, "refs", "bib.json"), "w", encoding="utf-8") as f:
    json.dump(bib, f, ensure_ascii=False, indent=1)

print("bib entries", len(bib), "| seed", sum(1 for v in bib.values() if v["source"]=="seed"),
      "| classic", sum(1 for v in bib.values() if v["source"]=="classic"),
      "| recent", sum(1 for v in bib.values() if v["source"]=="recent"))
print("missing:", missing)
for k, v in bib.items():
    if v["source"] == "recent":
        print(k, "|", v["year"], "|", v["status"], "|", (v["title"] or "")[:100])
