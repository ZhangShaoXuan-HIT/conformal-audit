"""Build the JAS Application Note package: PDF and DOCX."""
import json
import os
import re
import subprocess
from pathlib import Path

import pypandoc
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
AN = PAPER / "jas_an"
AN.mkdir(exist_ok=True)

md = (AN / "main_an.md").read_text(encoding="utf-8").replace("\r\n", "\n")
bib = json.load(open(ROOT / "refs" / "bib.json", encoding="utf-8"))
cited = json.load(open(ROOT / "refs" / "cited_keys.json", encoding="utf-8"))


def parse_names(authors):
    out = []
    for part in [p.strip() for p in authors.split(",") if p.strip()]:
        if part.lower().startswith("et al"):
            continue
        m = re.match(r"^(.*?)\s+((?:[A-Z]\.?\s*)+)$", part)
        if m:
            out.append((m.group(1).strip(), re.findall(r"[A-Z]", m.group(2))))
        else:
            out.append((part, []))
    return out


def intext(key):
    v = bib[key]
    sur = [n[0] for n in parse_names(v["authors"])]
    if len(sur) == 1:
        who = sur[0]
    elif len(sur) == 2:
        who = sur[0] + " & " + sur[1]
    else:
        who = sur[0] + " et al."
    return who + ", " + str(v["year"])


def ref(key):
    v = bib[key]
    names = parse_names(v["authors"])
    parts = []
    for surname, initials in names:
        parts.append(surname + (", " + " ".join(i + "." for i in initials) if initials else "."))
    if len(parts) == 1:
        authors = parts[0]
    elif len(parts) == 2:
        authors = parts[0] + ", & " + parts[1]
    else:
        authors = ", ".join(parts[:-1]) + ", & " + parts[-1]
    bits = [authors + " (" + str(v["year"]) + "). " + v["title"].rstrip(".") + "."]
    venue = (v.get("venue") or "").rstrip(".")
    if venue and not venue.lower().startswith("arxiv"):
        bits.append(venue + ".")
    if v.get("doi"):
        bits.append("https://doi.org/" + v["doi"])
    elif v.get("arxiv"):
        bits.append("arXiv:" + v["arxiv"] + ".")
    elif v.get("url"):
        bits.append(v["url"])
    if v.get("status") == "preprint":
        bits.append("Preprint.")
    return " ".join(bits).replace("--", "–")


def repl(m):
    keys = [x.strip().lstrip("@") for x in m.group(1).split(";")]
    keys = [k for k in keys if k in bib]
    if not keys:
        return m.group(0)
    if len(keys) == 1:
        v = bib[keys[0]]
        names = parse_names(v["authors"])
        first = names[0][0] if names else ""
        before = m.string[max(0, m.start() - 70):m.start()]
        if first and first.lower() in before.lower():
            return "(" + str(v["year"]) + ")"
        return "(" + intext(keys[0]) + ")"
    return "(" + "; ".join(intext(k) for k in keys) + ")"


text_keys = []
for m in re.finditer(r"\[@([^\]]+)\]", md):
    for k in m.group(1).split(";"):
        k = k.strip().lstrip("@")
        if k in bib:
            text_keys.append(k)
text_keys = sorted(set(text_keys))
md = re.sub(r"\[@([^\]]+)\]", repl, md)
refs = sorted([ref(k) for k in text_keys], key=lambda s: s.lower())
print("references", len(refs))
md = md.replace("<!-- REFERENCES -->", "\n\n".join(refs))

figs = [
    ("fig1_pipeline.png", "The three stages (solid) and the reporting step (dashed), with the three places where the reported number can move."),
    ("fig2_equivalence.png", "Coverage and set size versus the threshold on digits."),
    ("fig3_forcing.png", "Change in coverage versus the raw empty rate across the image cells."),
    ("fig4_aci.png", "Coverage and level trajectories under drift on digits."),
]
fig_block = ""
for name, cap in figs:
    fig_block += "![%s](../figures/%s)\n\n" % (cap, name)
md = md.replace("<!-- FIGURES -->", fig_block)
(AN / "main_an_built.md").write_text(md, encoding="utf-8")

(AN / "style.css").write_text("""@page { size: A4; margin: 22mm; }
a { color: inherit; text-decoration: none; }
body { font-family: "Times New Roman", "Liberation Serif", serif; font-size: 11.5pt; line-height: 1.3; text-align: left; color: #111; }
h1 { font-size: 17pt; text-align: center; margin: 0 0 6pt; line-height: 1.2; }
h2 { font-size: 13pt; text-align: left; font-weight: bold; margin: 16pt 0 6pt; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 12pt 0 4pt; page-break-after: avoid; }
.keep { page-break-inside: avoid; }
p { margin: 0 0 7pt; }
.author { text-align: center; font-size: 11pt; margin: 0 0 14pt; }
.author p { margin: 0; }
table { width: 100%; border-collapse: collapse; font-size: 8pt; line-height: 1.2; table-layout: fixed; margin: 6pt 0 10pt; border-top: 1.2pt solid #000; border-bottom: 1.2pt solid #000; }
th, td { border: none; padding: 2pt 3pt; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
th { background: none; border-bottom: 0.7pt solid #000; font-weight: bold; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
figure { margin: 8pt 0 10pt; page-break-inside: avoid; text-align: center; }
figure img { width: 92% !important; max-width: 92% !important; height: auto; }
figcaption { font-size: 10pt; text-align: left; margin-top: 2pt; }
h2#references, h2#tables, h2#figures, h2#figure-captions { page-break-before: always; }
""", encoding="utf-8")
(AN / "template.html").write_text("""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>$title$</title>
<link rel="stylesheet" href="style.css"></head><body>$body$</body></html>
""", encoding="utf-8")

pypandoc.convert_file(str(AN / "main_an_built.md"), "html5", outputfile=str(AN / "main_an.html"),
                      extra_args=["--standalone", "--template=" + str(AN / "template.html"),
                                  "--metadata", "title=When Reported Coverage Is Not Coverage"])
edge = next((p for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p)), None)
if edge is None:
    raise SystemExit("Edge not found")
subprocess.run([edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                "--virtual-time-budget=10000", "--print-to-pdf=" + str(AN / "main_an.pdf"),
                (AN / "main_an.html").as_uri()], check=True)

img_dir = str(PAPER / "figures").replace("\\", "/")
docx_md = re.sub(r"!\[([^\]]*)\]\(\.\./figures/([^)]+)\)",
                 r"![\1](" + img_dir + r"/\2){width=6.5in}", md)
(AN / "main_an_docx.md").write_text(docx_md, encoding="utf-8")
pypandoc.convert_file(str(AN / "main_an_docx.md"), "docx", outputfile=str(AN / "main_an.docx"),
                      extra_args=["--resource-path=" + str(AN)])

doc = Document(str(AN / "main_an.docx"))
for table in doc.tables:
    tblPr = table._tbl.tblPr
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge, sz, val in [("top", 12, "single"), ("bottom", 12, "single"),
                          ("left", 0, "none"), ("right", 0, "none"),
                          ("insideH", 0, "none"), ("insideV", 0, "none")]:
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), val)
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)
    for ri, row in enumerate(table.rows):
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            for shd in tcPr.findall(qn("w:shd")):
                tcPr.remove(shd)
            if ri == 0:
                for old in tcPr.findall(qn("w:tcBorders")):
                    tcPr.remove(old)
                tcB = OxmlElement("w:tcBorders")
                bottom = OxmlElement("w:bottom")
                bottom.set(qn("w:val"), "single")
                bottom.set(qn("w:sz"), "6")
                bottom.set(qn("w:space"), "0")
                bottom.set(qn("w:color"), "000000")
                tcB.append(bottom)
                tcPr.append(tcB)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.bold = True
doc.save(str(AN / "main_an.docx"))
print("wrote", AN / "main_an.pdf", (AN / "main_an.pdf").stat().st_size)
print("wrote", AN / "main_an.docx", (AN / "main_an.docx").stat().st_size)
print("body words", len(re.sub(r"[#*|]", " ", md.split("## References")[0]).split()))
