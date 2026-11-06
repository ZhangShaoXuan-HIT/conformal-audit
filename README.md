# cp-audit

Code and results for **What Does Conformal Prediction Add? A Controlled Audit of
Calibrated Set-Valued Classification**.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24001054.svg)](https://doi.org/10.5281/zenodo.24001054)

The paper audits three implementation choices that sit between the conformal
guarantee and the coverage a pipeline reports: the calibration of the threshold,
the treatment of empty sets, and the update rule of adaptive conformal inference.
It uses three datasets (digits, CIFAR-10, covertype), eight public implementations,
and a cost rule for the non-empty fallback.

## Quick start

```bash
python code/run_paper.py --dry-run   # print the full step list
python code/run_paper.py             # full pipeline, about 20 minutes on the reference machine
```

Partial runs:

```bash
python code/run_all.py               # digits: audits A/B/C, tables 2-4, figures 2-5 (~90 s)
python code/cifar_features.py        # once, after data/cifar10 is present
python code/run_cifar.py             # CIFAR: audits A/B/C, tables 5-7
python code/exp_tabular.py           # covertype: table 11 (~30 s after the OpenML cache)
python code/exp_cifar_c.py           # CIFAR-10-C style drift: table 7
python code/exp_library_runtime.py   # eight-library runtime audit: table 8 rows
python code/exp_mapie_empty.py       # MAPIE five-seed empty-set experiment
python code/exp_cost_perpoint.py     # per-point cost check (Section 6.2)
python code/make_tables.py           # tables 2-4
python code/make_cifar_tables.py     # tables 5-7
python code/make_tabular_table.py    # table 11
python code/make_cost_table.py       # table 12
python code/make_fig1.py             # figure 1
python code/make_figures.py          # figures 2-5
python code/build_references.py      # paper/references.md
```

`run_all.py` regenerates figure 5 with covertype only if
`results/tabular.json` exists; otherwise the figure uses digits and CIFAR-10.

## Environment

The reference run used Python 3.12.14, numpy 2.3.5, scipy 1.18.1,
scikit-learn 1.9.1, matplotlib 3.11.2, torch 2.5.1+cu121,
torchvision 0.20.1+cu121, and a single RTX 4060 (8 GB). The CIFAR feature
extraction uses CUDA; the rest runs on CPU.

```bash
pip install -r requirements.txt
```

For CUDA 12.1, install torch first:

```bash
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
```

`coverforest` 0.0.3 builds, but its forest code is incompatible with
scikit-learn 1.9 at runtime; the library audit records it as source-only.
`torchcp` and `AdaptiveConformal` are source-only for the same kind of reason
(optional graph dependencies; R not installed).

## Data

- **digits**: bundled with scikit-learn; no download.
- **CIFAR-10**: the fast.ai PNG mirror, because the Toronto server was slow from
  this machine.

```bash
curl -L -o data/cifar10.tgz https://s3.amazonaws.com/fast-ai-imageclas/cifar10.tgz
tar -xzf data/cifar10.tgz -C data
python code/cifar_features.py
```

  This gives `data/cifar10/train|test/<class>/*.png` and
  `data/cifar10_features.npz` (50k train, 10k test, 512-d ResNet-18 features).
  Both are gitignored and can be regenerated.
- **CIFAR-10-C style corruptions**: generated locally with `imagecorruptions`
  from the CIFAR-10 test PNGs; the 2.9 GB official archive is not needed.
- **covertype**: `sklearn.datasets.fetch_openml("covertype", version=3)`;
  scikit-learn caches it after the first run.

## Tables and figures

| output | source |
|---|---|
| Table 1, two-axis map | conceptual; `paper/tables/table1_map.md` |
| Tables 2-4, digits audits A/B/C | `code/make_tables.py` from `results/*.json` |
| Tables 5-6, CIFAR audits A/B | `code/make_cifar_tables.py` |
| Table 7, CIFAR-10-C style drift | `code/make_cifar_tables.py` from `results/aci_cifar_c.json` |
| Table 8, library audit | source-policy columns curated from the package versions listed; runtime rows from `results/library_runtime.json` |
| Table 9, coverage matrix | conceptual; `paper/tables/table9_coverage.md` |
| Table 10, experimental grid | design table; `paper/tables/table10_grid.md` |
| Table 11, covertype audit | `code/make_tabular_table.py` from `results/tabular.json` |
| Table 12, cost-sensitive reading | `code/make_cost_table.py` from `results/*.json` |
| Figure 1, pipeline | `code/make_fig1.py` |
| Figures 2-5 | `code/make_figures.py` |

## Submission PDF

```bash
python code/build_submission.py
```

This writes `paper/submission/submission.pdf`: the working notes after the final
`---` are stripped, `[@key]` citations are converted to numbers, author
placeholders are inserted, and Tables 1-12 and Figures 1-5 are appended. It uses
`pypandoc-binary` (Pandoc 3.9) and Microsoft Edge headless; the current script
hard-codes the Windows Edge path, so another OS needs a different browser path.

## Journal of Applied Statistics package

```bash
python code/build_jas.py
```

This builds `paper/jas/main_jas.pdf` (manuscript, author-date references,
186-word abstract), `paper/jas/main_jas.docx` (editable Word manuscript with
embedded figures), and `paper/jas/supplement_jas.pdf` (Tables S1-S3), plus
`paper/jas/cover_letter.md`. The DOCX includes the required declaration of
generative AI use. The package uses Harvard/APA author-date citations,
12 pt Times at 1.55 spacing, and 8 pt tables. T&F's author-instructions page was
not accessible at build time; verify the journal's exact reference style, page
limit and spacing before submission.

## Journal of Applied Statistics Application Note

```bash
python code/build_jas_an.py
python code/build_an_supplement.py
```

Outputs `paper/jas_an/main_an.pdf` (13 pages, about 3740 words of prose, 4 tables and 4 figures embedded at first reference),
`main_an.docx`, `supplement_an.pdf` (9 pages) and `cover_letter.md`. The full
tables, two-axis map, complete grid, per-corruption results and reporting
checklist are in the supplement. The prose was revised to remove AI-style
patterns, and the abstract is 172 words.

## Design rules

1. `build_sets` never forces non-empty sets; forcing is a separate
   post-processing step, tagged `postprocess = raw | forced` in every row.
2. Quantitative tables 2-7, 11 and 12 are generated from `results/*.json`.
3. Table 8's source-policy columns are a curated reading of the code; its
   runtime rows come from `results/library_runtime.json`.
4. Tables 1, 9 and 10 are conceptual or design tables.
5. The JSON files are the source of truth for every empirical number in the
   manuscript.

## Notes and limits

- The library sample is eight public implementations, not a census. Five were
  run (MAPIE, puncc, crepes, nonconformist, conformal); three were read at the
  source level (TorchCP, coverforest, AdaptiveConformal).
- The CIFAR-10-C experiment uses `imagecorruptions` on the local CIFAR-10 test
  images. It follows the corruption families of CIFAR-10-C but is not the
  official archive.
- Seeds: five for audits A/B, three for the CIFAR-10-C stream, one for the
  library runtime. The paper states this in Section 5.
- `data/` and `_libs/` are not included. The source snapshots in `_libs/src` were
  downloaded locally for the Table 8 audit; the table records the package
  versions and line numbers, and the packages are public on PyPI/GitHub.
- `legacy/` is the frozen earlier manuscript, kept for comparison and not part
  of the paper.

## Citation

The paper is in preparation. Author: Shaoxuan Zhang (ORCID:
https://orcid.org/0009-0001-4103-6099; email: 2023113033@stu.hit.edu.cn). The code and results are at
https://github.com/ZhangShaoXuan-HIT/conformal-audit and archived at
https://doi.org/10.5281/zenodo.24001054 (v1.0.0; concept DOI
https://doi.org/10.5281/zenodo.24001053). The reference list is
`paper/references.md`; author and venue information will be added at submission.

## License

Code: MIT (see `LICENSE`). Manuscript text, tables and figures: CC BY 4.0
(see `LICENSE-paper`).
