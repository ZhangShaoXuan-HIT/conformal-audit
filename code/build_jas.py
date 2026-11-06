"""Build a Journal of Applied Statistics style package.

Assumptions (verify against the journal's current instructions):
- Harvard/APA author-date citations and reference list.
- Abstract <= 200 words, 5 keywords.
- 12 pt Times, 1.5 spacing manuscript.
- Tables 1, 9, 10 -> supplementary Tables S1-S3; other tables in main.
"""
import json
import os
import re
import subprocess
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
JAS = PAPER / "jas"
JAS.mkdir(exist_ok=True)

main = (PAPER / "main.md").read_text(encoding="utf-8").replace("\r\n", "\n")
cut = main.find("\n---\n\n## Tables and figures")
if cut != -1:
    main = main[:cut]

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
        parts.append(surname + (", " + " ".join(i + "." for i in initials) if initials else ""))
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


converted = re.sub(r"\[@([^\]]+)\]", repl, main)

# abstract trim
abstract_start = converted.index("**Abstract.**")
abstract_end = converted.index("**Keywords.**")
abstract = converted[abstract_start:abstract_end]
for old, new in [
    (" and we give a six-item checklist", ""),
    ("the common α_t update", "the α_t update"),
    ("a range of model strengths", "a range of strengths"),
]:
    abstract = abstract.replace(old, new)
abstract = abstract.replace("chronology,.", "chronology.")
converted = converted[:abstract_start] + abstract + converted[abstract_end:]
abs_words = len(re.sub(r"\*\*Abstract\.\*\*", "", abstract).split())
print("abstract words", abs_words)

body = converted[converted.index("**Abstract.**"):]
front = converted[:converted.index("**Abstract.**")]

# supplementary table references
body = re.sub(r"\bTable 10\b", "Table S3", body)
body = re.sub(r"\bTable 9\b", "Table S2", body)
body = re.sub(r"\bTable 1\b(?!\d)", "Table S1", body)

body = body.replace("## Data and code availability", "## Data availability statement")
body = body.replace(
    "## Data availability statement",
    "## Disclosure statement\n\nThe author reports no conflict of interest.\n\n"
    "## Funding\n\nThis research received no specific grant from any funding agency.\n\n"
    "## Declaration of generative AI use\n\n"
    "The author used a generative AI assistant (DeepSeek) for code development, data analysis, "
    "and drafting/editing of the manuscript. The author verified all results, analyses, and "
    "references and takes full responsibility for the content.\n\n"
    "## CRediT authorship contribution statement\n\n"
    "Shaoxuan Zhang: Conceptualization, Methodology, Software, Validation, Formal analysis, "
    "Investigation, Data curation, Writing - original draft, Writing - review & editing, "
    "Visualization.\n\n"
    "## Data availability statement"
)
body = body.replace(
    "from results/library_runtime.json. The repository is available at",
    "from results/library_runtime.json. The repository is available at"
)
body += (
    "\n\n## Supplementary material\n\n"
    "Supplementary Tables S1-S3 are provided as a separate file. Table S1 is the "
    "two-axis map, Table S2 is the coverage matrix, and Table S3 is the experimental grid.\n"
)

refs = sorted([ref(k) for k in cited if k in bib], key=lambda s: s.lower())
references_block = "\n\n## References\n\n" + "\n\n".join(refs) + "\n"

tables_main = [
    (2, "table2_equivalence.md"), (3, "table3_postprocess.md"), (4, "table4_aci.md"),
    (5, "table5_cifar_equivalence.md"), (6, "table6_cifar_postprocess.md"),
    (7, "table7_cifar_aci.md"), (8, "table8_libraries.md"),
    (11, "table11_tabular.md"), (12, "table12_cost.md"),
]
tables_block = "\n\n## Tables\n\n"
for n, name in tables_main:
    txt = (PAPER / "tables" / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    txt = re.sub(r"^# ", "### ", txt, count=1, flags=re.M)
    txt = re.sub(r"^## ", "#### ", txt, flags=re.M)
    tables_block += txt + "\n"

figs = [
    ("Figure 1", "The three stages (solid) and the reporting step (dashed), with the three places where the reported number can move.", "fig1_pipeline.png"),
    ("Figure 2", "Coverage and set size versus the threshold on digits.", "fig2_equivalence.png"),
    ("Figure 3", "Change in coverage versus the raw empty rate across the image cells.", "fig3_forcing.png"),
    ("Figure 4", "Coverage and level trajectories under drift on digits.", "fig4_aci.png"),
    ("Figure 5", "Empty rate and forcing gain versus test accuracy for digits, CIFAR-10 and covertype.", "fig5_regime.png"),
]
figs_block = "\n\n## Figures\n\n"
for label, caption, name in figs:
    figs_block += "### %s\n\n![%s](../figures/%s)\n\n" % (label, caption, name)

main_jas = front + body + references_block + tables_block + figs_block
(JAS / "main_jas.md").write_text(main_jas, encoding="utf-8")

# supplement: S1 author-date map, S2 coverage matrix, S3 grid
s1 = """# Supplementary material

## Table S1. Guarantee by data assumption

Each cell gives a representative method, the assumption it needs, and the price it pays.
"Open" means no method in the reviewed set covers that cell.

| guarantee | exchangeable | covariate shift | non-exchangeable / temporal | known groups |
|---|---|---|---|---|
| marginal coverage | Vovk et al. (2005), Lei et al. (2018), Angelopoulos & Bates (2023). One calibration pass. | Tibshirani et al. (2019). Likelihood ratio known or estimable. | Barber et al. (2023), Oliveira et al. (2022). Gap bounded by the violation. | Vovk (2012). Per-group quantiles; small n per group. |
| group-conditional coverage | Vovk (2012), Gibbs et al. (2025). Group-wise quantiles; smaller effective n. | open | open | Vovk (2012), Gibbs et al. (2025). Group labels known at test. |
| pointwise conditional coverage | Barber et al. (2021), Hore & Barber (2025). Larger sets. | open | open | open |
| risk control | Bates et al. (2021), Angelopoulos et al. (2022), Angelopoulos et al. (2025). Monotone loss; grid and multiplicity. | open in the reviewed set | Farinhas et al. (2023). Bounded non-exchangeability. | Combes et al. (2026). |
"""
for src, new in [("table9_coverage.md", "Table S2"), ("table10_grid.md", "Table S3")]:
    txt = (PAPER / "tables" / src).read_text(encoding="utf-8").replace("\r\n", "\n")
    txt = re.sub(r"^# Table \d+\.", "## " + new + ".", txt, count=1, flags=re.M)
    s1 += "\n\n" + txt
(JAS / "supplement_jas.md").write_text(s1, encoding="utf-8")

cover = """# Cover letter

Dear Editor,

I submit the manuscript "What Does Conformal Prediction Add? A Controlled Audit of Calibrated Set-Valued Classification" for consideration in the Journal of Applied Statistics.

The paper is an empirical audit, not a new method. It measures three implementation choices that sit between the conformal guarantee and the coverage a pipeline reports: the calibration of the threshold, the treatment of empty sets, and the update rule of adaptive conformal inference. The evidence comes from two image datasets and a tabular benchmark, eight public implementations, and a reproducible grid of 1,260 image cells plus a 180-row tabular replication. The paper contributes a two-axis map, a library policy map, and a cost rule for the non-empty fallback.

I believe the work fits the Journal of Applied Statistics because the central questions are applied: when does a reported coverage number cease to estimate the nominal level, and what should a deployment do about an empty set? The paper gives a measurable answer and a decision rule, and it reports a boundary case (covertype) where the effect is near zero.

The code and results are available at https://github.com/ZhangShaoXuan-HIT/conformal-audit and archived at https://doi.org/10.5281/zenodo.24001054. The manuscript is not under consideration elsewhere, and I am the sole author.

Yours sincerely,

Shaoxuan Zhang
Faculty of Computing, Harbin Institute of Technology, Harbin, Heilongjiang, China
ORCID: 0009-0001-4103-6099
2023113033@stu.hit.edu.cn
"""
(JAS / "cover_letter.md").write_text(cover, encoding="utf-8")

# CSS/template
(JAS / "style.css").write_text("""@page { size: A4; margin: 25mm; }
a { color: inherit; text-decoration: none; }
body { font-family: "Times New Roman", "Liberation Serif", serif; font-size: 12pt; line-height: 1.55; text-align: left; color: #111; }
h1 { font-size: 18pt; text-align: center; margin: 0 0 4pt; line-height: 1.2; }
h2 { font-size: 14pt; text-align: center; font-weight: normal; margin: 0 0 14pt; page-break-after: avoid; }
h2:not(:first-of-type) { text-align: left; font-weight: bold; margin: 18pt 0 6pt; }
h3 { font-size: 12pt; margin: 12pt 0 4pt; page-break-after: avoid; }
h4 { font-size: 11pt; margin: 10pt 0 3pt; page-break-after: avoid; }
p { margin: 0 0 8pt; }
.author { text-align: center; font-size: 11pt; margin: 0 0 16pt; }
.author p { margin: 0; }
table { width: 100%; border-collapse: collapse; font-size: 8pt; line-height: 1.2; table-layout: fixed; margin: 6pt 0 12pt; }
th, td { border: 0.4pt solid #777; padding: 2pt 2.5pt; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
th { background: #efefef; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
figure { margin: 10pt 0 14pt; page-break-inside: avoid; text-align: center; }
figure img { width: 100% !important; max-width: 100% !important; height: auto; }
figcaption { font-size: 10pt; text-align: left; margin-top: 3pt; }
h2#tables, h2#figures, h2#references { page-break-before: always; }
""", encoding="utf-8")

(JAS / "template.html").write_text("""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>$title$</title>
<link rel="stylesheet" href="style.css"></head><body>$body$</body></html>
""", encoding="utf-8")

edge = next((p for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p)), None)
if edge is None:
    raise SystemExit("Edge not found")


def build(md_name, html_name, pdf_name, title):
    pypandoc.convert_file(
        str(JAS / md_name), "html5", outputfile=str(JAS / html_name),
        extra_args=["--standalone", "--template=" + str(JAS / "template.html"),
                    "--metadata", "title=" + title],
    )
    subprocess.run([edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=10000", "--print-to-pdf=" + str(JAS / pdf_name),
                    (JAS / html_name).as_uri()], check=True)
    print("wrote", JAS / pdf_name)


build("main_jas.md", "main_jas.html", "main_jas.pdf", "What Does Conformal Prediction Add?")
build("supplement_jas.md", "supplement_jas.html", "supplement_jas.pdf", "Supplementary material")
img_dir = str(PAPER / "figures").replace("\\", "/")
docx_md = re.sub(r"!\[([^\]]*)\]\(\.\./figures/([^)]+)\)",
                 r"![\1](" + img_dir + r"/\2){width=6.5in}", main_jas)
(JAS / "main_jas_docx.md").write_text(docx_md, encoding="utf-8")
pypandoc.convert_file(str(JAS / "main_jas_docx.md"), "docx", outputfile=str(JAS / "main_jas.docx"),
                      extra_args=["--resource-path=" + str(JAS)])
print("main words", len(re.sub(r"[#*|]", " ", main_jas).split()))
