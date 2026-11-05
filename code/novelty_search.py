"""Phase 3A: targeted novelty check.

Six query groups, OpenAlex + arXiv + Crossref. Raw responses are cached in
refs/raw/, normalized records in refs/candidates.json. No screening yet.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REF = os.path.join(ROOT, "refs")
RAW = os.path.join(REF, "raw")
os.makedirs(RAW, exist_ok=True)
UA = "cp-audit/0.1 (mailto:cp-audit@local)"

QUERIES = [
    ("empty_sets", "empty prediction sets conformal",
     'all:"empty prediction sets"'),
    ("postprocess", "conformal prediction non-empty set argmax post-processing",
     'all:conformal AND all:"non-empty"'),
    ("aci_impl", "adaptive conformal inference implementation update",
     'all:"adaptive conformal inference"'),
    ("pitfalls", "conformal prediction pitfalls common mistakes",
     'all:"conformal prediction" AND all:pitfalls'),
    ("inflation", "conformal prediction coverage inflation post-processing",
     'all:"coverage inflation" AND all:conformal'),
    ("benchmark", "conformal prediction empirical benchmark evaluation",
     'all:"conformal prediction" AND all:benchmark'),
]


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def reconstruct(inv):
    if not inv:
        return ""
    pos = {}
    for word, plist in inv.items():
        for p in plist:
            pos[p] = word
    return " ".join(pos[i] for i in sorted(pos))


def openalex(q):
    url = ("https://api.openalex.org/works?filter=title_and_abstract.search:"
           + urllib.parse.quote(q) + "&per-page=25&sort=relevance_score:desc")
    d = json.loads(get(url))
    out = []
    for x in d.get("results", []):
        out.append({
            "source": "openalex", "title": x.get("title"),
            "year": x.get("publication_year"), "doi": x.get("doi"),
            "venue": ((x.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "authors": [a.get("author", {}).get("display_name") for a in x.get("authorships", [])][:6],
            "abstract": reconstruct(x.get("abstract_inverted_index")),
            "url": x.get("id"),
            "cited_by": x.get("cited_by_count"),
        })
    return out


def arxiv(q):
    url = ("http://export.arxiv.org/api/query?search_query="
           + urllib.parse.quote_plus(q) + "&start=0&max_results=25&sortBy=relevance")
    t = get(url)
    root = ET.fromstring(t)
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    out = []
    for e in root.findall("a:entry", ns):
        out.append({
            "source": "arxiv",
            "title": (e.findtext("a:title", default="", namespaces=ns) or "").strip(),
            "year": int((e.findtext("a:published", default="0000", namespaces=ns) or "0000")[:4]),
            "doi": e.findtext("arxiv:doi", default=None, namespaces=ns),
            "venue": "arXiv",
            "authors": [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)][:6],
            "abstract": (e.findtext("a:summary", default="", namespaces=ns) or "").strip(),
            "url": e.findtext("a:id", default="", namespaces=ns),
            "cited_by": None,
        })
    return out


def crossref(q):
    url = ("https://api.crossref.org/works?query.bibliographic="
           + urllib.parse.quote_plus(q) + "&rows=10&select=DOI,title,author,issued,container-title,abstract")
    d = json.loads(get(url))
    out = []
    for x in d.get("message", {}).get("items", []):
        out.append({
            "source": "crossref",
            "title": (x.get("title") or [""])[0],
            "year": (x.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "doi": x.get("DOI"),
            "venue": (x.get("container-title") or [""])[0],
            "authors": [a.get("family", "") for a in x.get("author", [])][:6],
            "abstract": re.sub("<[^>]+>", " ", x.get("abstract", "") or ""),
            "url": "https://doi.org/" + str(x.get("DOI")),
            "cited_by": None,
        })
    return out


def main():
    all_records = []
    for qid, qtext, aq in QUERIES:
        for source, fn in (("openalex", openalex), ("arxiv", arxiv), ("crossref", crossref)):
            try:
                recs = fn(qtext if source != "arxiv" else aq)
            except Exception as e:
                print("FAIL", qid, source, repr(e), flush=True)
                recs = []
            for r in recs:
                r["query"] = qid
            all_records.extend(recs)
            print(qid, source, len(recs), flush=True)
            time.sleep(1.0)

    # dedupe by title
    groups = {}
    for r in all_records:
        key = norm_title(r.get("title"))
        if not key:
            continue
        groups.setdefault(key, []).append(r)
    merged = []
    for key, recs in groups.items():
        base = dict(recs[0])
        base["sources"] = sorted({x["source"] for x in recs})
        base["queries"] = sorted({x["query"] for x in recs})
        base["n_hits"] = len(recs)
        merged.append(base)
    merged.sort(key=lambda r: (-(r.get("cited_by") or 0), -(r.get("year") or 0)))

    with open(os.path.join(REF, "candidates.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print("total raw", len(all_records), "unique", len(merged), flush=True)

    # print titles that look dangerous
    keywords = ["empty", "post-process", "postprocess", "argmax", "pitfall", "mistake",
                "audit", "inflat", "non-empty", "adaptive conformal", "aci", "benchmark"]
    print("\n=== keyword hits ===")
    seen = 0
    for r in merged:
        t = (r.get("title") or "").lower()
        if any(k in t for k in keywords):
            print("%s | %s | %s | %s" % (r.get("year"), (r.get("venue") or "")[:40], r.get("title"), ",".join(r.get("sources", []))))
            seen += 1
            if seen >= 40:
                break


if __name__ == "__main__":
    main()
