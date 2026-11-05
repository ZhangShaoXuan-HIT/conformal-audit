"""3C literature search: ten query groups, OpenAlex + arXiv.

Saves refs/candidates_3c.json. Counts only on stdout; titles go to the JSON.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REF = os.path.join(ROOT, "refs")
UA = "cp-audit/0.1 (mailto:cp-audit@local)"

QUERIES = [
    ("foundations", "conformal prediction", 50, "cited"),
    ("split", "split conformal", 30, "relevance"),
    ("aps", "adaptive prediction sets", 30, "relevance"),
    ("risk", "conformal risk control", 30, "relevance"),
    ("conditional", "conditional coverage conformal", 30, "relevance"),
    ("group", "group conditional conformal", 30, "relevance"),
    ("aci", "adaptive conformal inference", 30, "relevance"),
    ("nonexch", "non-exchangeable conformal", 30, "relevance"),
    ("llm", "conformal language model", 30, "relevance"),
    ("survey", "conformal prediction survey", 25, "relevance"),
]
ARXIV = {
    "foundations": 'ti:"conformal prediction"',
    "split": 'ti:"split conformal"',
    "aps": 'ti:"adaptive prediction sets"',
    "risk": 'ti:"conformal risk control"',
    "conditional": 'ti:"conditional coverage" AND abs:conformal',
    "group": 'ti:group AND ti:conformal',
    "aci": 'ti:"adaptive conformal inference"',
    "nonexch": 'ti:"non-exchangeable conformal"',
    "llm": 'ti:conformal AND ti:"language model"',
    "survey": 'ti:"conformal prediction" AND ti:survey',
}


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
    for w, pl in inv.items():
        for p in pl:
            pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))


def openalex(q, n, order):
    sort = "cited_by_count:desc" if order == "cited" else "relevance_score:desc"
    url = ("https://api.openalex.org/works?filter=title.search:"
           + urllib.parse.quote(q) + ",publication_year:>2004"
           + "&per-page=" + str(n) + "&sort=" + sort)
    d = json.loads(get(url))
    out = []
    for x in d.get("results", []):
        out.append({
            "source": "openalex", "title": x.get("title"),
            "year": x.get("publication_year"), "doi": x.get("doi"),
            "venue": ((x.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "authors": [a.get("author", {}).get("display_name") for a in x.get("authorships", [])][:8],
            "abstract": reconstruct(x.get("abstract_inverted_index")),
            "url": x.get("id"), "cited_by": x.get("cited_by_count"),
        })
    return out


def arxiv(q, n=30):
    url = ("http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote_plus(q)
           + "&start=0&max_results=" + str(n) + "&sortBy=relevance")
    root = ET.fromstring(get(url))
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    out = []
    for e in root.findall("a:entry", ns):
        out.append({
            "source": "arxiv",
            "title": (e.findtext("a:title", default="", namespaces=ns) or "").strip(),
            "year": int((e.findtext("a:published", default="0000", namespaces=ns) or "0000")[:4]),
            "doi": e.findtext("arxiv:doi", default=None, namespaces=ns),
            "venue": "arXiv",
            "authors": [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)][:8],
            "abstract": (e.findtext("a:summary", default="", namespaces=ns) or "").strip(),
            "url": e.findtext("a:id", default="", namespaces=ns),
            "cited_by": None,
        })
    return out


def main():
    recs = []
    for qid, q, n, order in QUERIES:
        try:
            got = openalex(q, n, order)
        except Exception as e:
            print("FAIL", qid, "openalex", repr(e), flush=True)
            got = []
        for r in got:
            r["query"] = qid
        recs.extend(got)
        print("openalex", qid, len(got), flush=True)
        time.sleep(1.0)
        try:
            got = arxiv(ARXIV[qid], 30)
        except Exception as e:
            print("FAIL", qid, "arxiv", repr(e), flush=True)
            got = []
        for r in got:
            r["query"] = qid
        recs.extend(got)
        print("arxiv", qid, len(got), flush=True)
        time.sleep(1.5)

    groups = {}
    for r in recs:
        k = norm_title(r.get("title"))
        if not k:
            continue
        groups.setdefault(k, []).append(r)
    merged = []
    for k, v in groups.items():
        b = dict(v[0])
        b["sources"] = sorted({x["source"] for x in v})
        b["queries"] = sorted({x["query"] for x in v})
        b["n_hits"] = len(v)
        merged.append(b)
    merged.sort(key=lambda r: (-(r.get("cited_by") or 0), -(r.get("year") or 0)))
    with open(os.path.join(REF, "candidates_3c.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print("raw", len(recs), "unique", len(merged), flush=True)


if __name__ == "__main__":
    main()
