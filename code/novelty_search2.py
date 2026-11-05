"""Phase 3A, second pass: precise queries."""
import json, os, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REF = os.path.join(ROOT, "refs")
UA = "cp-audit/0.1 (mailto:cp-audit@local)"

QUERIES = [
    ("empty_set", "conformal empty set", 'abs:conformal AND abs:"empty set"'),
    ("postproc", "conformal post-processing", 'abs:conformal AND abs:"post-processing"'),
    ("impl", "conformal implementation", 'abs:conformal AND abs:implementation'),
    ("audit", "conformal audit", 'abs:conformal AND abs:audit'),
    ("inflate", "conformal coverage inflation", 'abs:conformal AND abs:"coverage inflation"'),
]


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def reconstruct(inv):
    if not inv: return ""
    pos = {}
    for w, pl in inv.items():
        for p in pl: pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))


def openalex(q):
    url = ("https://api.openalex.org/works?filter=title_and_abstract.search:"
           + urllib.parse.quote(q) + "&per-page=25&sort=relevance_score:desc")
    d = json.loads(get(url))
    return [{
        "source": "openalex", "title": x.get("title"), "year": x.get("publication_year"),
        "doi": x.get("doi"),
        "venue": ((x.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "authors": [a.get("author", {}).get("display_name") for a in x.get("authorships", [])][:6],
        "abstract": reconstruct(x.get("abstract_inverted_index")),
        "url": x.get("id"), "cited_by": x.get("cited_by_count"),
    } for x in d.get("results", [])]


def arxiv(q):
    url = ("http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote_plus(q)
           + "&start=0&max_results=25&sortBy=relevance")
    root = ET.fromstring(get(url))
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    out = []
    for e in root.findall("a:entry", ns):
        out.append({
            "source": "arxiv", "title": (e.findtext("a:title", default="", namespaces=ns) or "").strip(),
            "year": int((e.findtext("a:published", default="0000", namespaces=ns) or "0000")[:4]),
            "doi": e.findtext("arxiv:doi", default=None, namespaces=ns), "venue": "arXiv",
            "authors": [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)][:6],
            "abstract": (e.findtext("a:summary", default="", namespaces=ns) or "").strip(),
            "url": e.findtext("a:id", default="", namespaces=ns), "cited_by": None,
        })
    return out


def main():
    recs = []
    for qid, oq, aq in QUERIES:
        for source, fn, q in (("openalex", openalex, oq), ("arxiv", arxiv, aq)):
            try:
                got = fn(q)
            except Exception as e:
                print("FAIL", qid, source, repr(e), flush=True); got = []
            for r in got: r["query"] = qid
            recs.extend(got)
            print(qid, source, len(got), flush=True)
            time.sleep(1.0)
    groups = {}
    for r in recs:
        k = norm_title(r.get("title"))
        if k: groups.setdefault(k, []).append(r)
    merged = []
    for k, v in groups.items():
        b = dict(v[0]); b["sources"] = sorted({x["source"] for x in v})
        b["queries"] = sorted({x["query"] for x in v}); b["n_hits"] = len(v)
        merged.append(b)
    with open(os.path.join(REF, "candidates2.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print("unique", len(merged), flush=True)
    for r in merged:
        print("%s | %s | %s" % (r.get("year"), (r.get("venue") or "")[:35], r.get("title")), flush=True)


if __name__ == "__main__":
    main()
