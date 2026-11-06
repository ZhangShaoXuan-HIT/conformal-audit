"""Build the Application Note supplement and cover letter."""
import re
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
AN = PAPER / "jas_an"
AN.mkdir(exist_ok=True)

jas_supp = (PAPER / "jas" / "supplement_jas.md").read_text(encoding="utf-8")
s1 = jas_supp.split("## Table S2")[0].rstrip()
parts = [s1]

table_map = [
    ("S2", "table2_equivalence.md"), ("S3", "table3_postprocess.md"),
    ("S4", "table4_aci.md"), ("S5", "table5_cifar_equivalence.md"),
    ("S6", "table6_cifar_postprocess.md"), ("S7", "table7_cifar_aci.md"),
    ("S8", "table8_libraries.md"), ("S9", "table9_coverage.md"),
    ("S10", "table10_grid.md"), ("S11", "table11_tabular.md"),
    ("S12", "table12_cost.md"),
]
for new, name in table_map:
    txt = (PAPER / "tables" / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    txt = re.sub(r"^# Table \d+\.", "## Table " + new + ".", txt, count=1, flags=re.M)
    txt = re.sub(r"^## ", "### ", txt, flags=re.M)
    parts.append(txt)

parts.append("""## Reporting checklist

1. Report the nominal level and the realized coverage, raw and forced.
2. Report the empty rate.
3. Report the calibration size and the finite-sample correction.
4. Report the score and the set-size distribution.
5. Report the update rule and its target.
6. Report the library version and its non-empty policy.
""")
(AN / "supplement_an.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")

pypandoc.convert_file(str(AN / "supplement_an.md"), "html5", outputfile=str(AN / "supplement_an.html"),
                      extra_args=["--standalone", "--template=" + str(AN / "template.html"),
                                  "--metadata", "title=Supplementary material"])
import os, subprocess
edge = next((p for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p)), None)
subprocess.run([edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                "--virtual-time-budget=10000", "--print-to-pdf=" + str(AN / "supplement_an.pdf"),
                (AN / "supplement_an.html").as_uri()], check=True)
print("wrote supplement", (AN / "supplement_an.pdf").stat().st_size)

cover = """# Cover letter

Dear Editor,

I submit the manuscript "When Reported Coverage Is Not Coverage: A Controlled Audit of Conformal Prediction Implementations" as an Application Note for the Journal of Applied Statistics.

The data challenge is practical. A practitioner sets a 0.90 coverage target, thresholds the output, and reports the fraction of test points on which the true label is in the set. The number looks like a coverage guarantee, but it is a property of the threshold rule. Three implementation choices move it without changing the guarantee: the calibration of the threshold, the treatment of empty sets, and the update rule of adaptive conformal inference.

The Approach is an audit protocol that uses existing conformal constructions as probes. It composes a threshold probe, an empty-set probe and an update probe with a coverage accounting identity and a cost rule. The protocol is not a new estimator; it is an innovative use of existing methods to answer a question that a standard application does not answer: whether the reported number estimates the nominal level.

I apply the protocol to digits, CIFAR-10 and covertype, and to eight public implementations. The main text is 15 pages. The supplementary file contains the full tables, the two-axis map, the complete grid, the per-corruption results and a reporting checklist.

The code and results are available at https://github.com/ZhangShaoXuan-HIT/conformal-audit and archived at https://doi.org/10.5281/zenodo.24001054. The manuscript is not under consideration elsewhere, and I am the sole author. The required declaration of generative AI use is included in the manuscript.

Yours sincerely,

Shaoxuan Zhang
Faculty of Computing, Harbin Institute of Technology, Harbin, Heilongjiang, China
ORCID: 0009-0001-4103-6099
2023113033@stu.hit.edu.cn
"""
(AN / "cover_letter.md").write_text(cover, encoding="utf-8")
print("wrote cover letter")
