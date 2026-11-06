"""Build a clean submission PDF from paper/main.md.

Strips the working notes, converts [@key] citations to numbered references,
appends tables and figures, and renders via Pandoc HTML + Edge headless.
"""
import os
import re
import subprocess
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
SUB = PAPER / "submission"
SUB.mkdir(exist_ok=True)

main = (PAPER / "main.md").read_text(encoding="utf-8").replace("\r\n", "\n")
cut = main.find("\n---\n\n## Tables and figures")
if cut != -1:
    main = main[:cut]

refs = (PAPER / "references.md").read_text(encoding="utf-8").replace("\r\n", "\n")
mapping = {}
for line in refs.splitlines():
    m = re.match(r"^(\d+)\. .*<!--\s*(\w+)\s*-->", line)
    if m:
        mapping[m.group(2)] = int(m.group(1))


def cite(m):
    keys = [x.strip().lstrip("@") for x in m.group(1).split(";")]
    nums = [str(mapping[k]) for k in keys if k in mapping]
    missing = [k for k in keys if k not in mapping]
    if missing:
        print("missing citation keys:", missing)
    return "[" + ", ".join(nums) + "]"


main = re.sub(r"\[@([^\]]+)\]", cite, main)

subtitle = "## A Controlled Audit of Calibrated Set-Valued Classification"
author = """

::: {.author}
**Author:** [Name]  
**Affiliation:** [Institution]  
**Corresponding author:** [email]
:::
"""
main = main.replace(subtitle, subtitle + author, 1)

tables = [
    (1, "table1_map.md"), (2, "table2_equivalence.md"), (3, "table3_postprocess.md"),
    (4, "table4_aci.md"), (5, "table5_cifar_equivalence.md"),
    (6, "table6_cifar_postprocess.md"), (7, "table7_cifar_aci.md"),
    (8, "table8_libraries.md"), (9, "table9_coverage.md"), (10, "table10_grid.md"),
    (11, "table11_tabular.md"), (12, "table12_cost.md"),
]
parts = [main, "\n\n## Tables\n\n"]
for n, name in tables:
    txt = (PAPER / "tables" / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    txt = re.sub(r"^# ", "### ", txt, count=1, flags=re.M)
    txt = re.sub(r"^## ", "#### ", txt, flags=re.M)
    if n == 1:
        for key, num in mapping.items():
            txt = re.sub(r"\b" + re.escape(key) + r"\b", "[%d]" % num, txt)
    parts.append(txt + "\n")

figs = [
    ("Figure 1", "The three stages (solid) and the reporting step (dashed), with the three places where the reported number can move.", "fig1_pipeline.png"),
    ("Figure 2", "Coverage and set size versus the threshold on digits.", "fig2_equivalence.png"),
    ("Figure 3", "Change in coverage versus the raw empty rate across the image cells.", "fig3_forcing.png"),
    ("Figure 4", "Coverage and level trajectories under drift on digits.", "fig4_aci.png"),
    ("Figure 5", "Empty rate and forcing gain versus test accuracy for digits, CIFAR-10 and covertype.", "fig5_regime.png"),
]
parts.append("\n## Figures\n\n")
for label, caption, name in figs:
    parts.append("### %s\n\n![%s](../figures/%s)\n\n" % (label, caption, name))

refs_clean = re.sub(r"<!--.*?-->", "", refs)
refs_clean = re.sub(r"^# References\s*", "", refs_clean, flags=re.M).strip()
parts.append("\n## References\n\n" + refs_clean + "\n")

md = "\n".join(parts)
(SUB / "submission.md").write_text(md, encoding="utf-8")

pypandoc.convert_file(
    str(SUB / "submission.md"), "html5", outputfile=str(SUB / "submission.html"),
    extra_args=["--standalone", "--template=" + str(SUB / "template.html"),
                "--metadata", "title=What Does Conformal Prediction Add?"],
)

edge_candidates = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
edge = next((p for p in edge_candidates if os.path.exists(p)), None)
if edge is None:
    raise SystemExit("Microsoft Edge not found")
pdf = SUB / "submission.pdf"
subprocess.run([
    edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
    "--virtual-time-budget=10000", "--print-to-pdf=" + str(pdf),
    (SUB / "submission.html").as_uri(),
], check=True)
print("wrote", pdf, pdf.stat().st_size, "bytes")
