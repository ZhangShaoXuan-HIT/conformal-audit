# cp-audit

A controlled audit of conformal prediction implementations.

## Design rules

1. `build_sets` never forces non-empty sets. Forcing is a separate step.
2. Every result row records `postprocess = raw | forced`.
3. Every table and figure is generated from `results/*.json`.
4. No number is typed into the manuscript by hand.

## Quickstart

```
python code/exp_equiv.py
python code/make_tables.py
```

or simply:

```
python code/run_all.py
```

## Structure

```
paper/main.md              single source of truth
paper/tables/              generated tables
paper/figures/             generated figures
code/common.py             data, models, scores, sets, metrics
code/exp_equiv.py          audit A: calibrated threshold = split conformal
code/exp_postprocess.py    audit B: non-empty post-processing
code/exp_aci.py            audit C: ACI update comparison
code/exp_cifar.py          phase 2: CIFAR-10 replication
code/make_tables.py        JSON to Markdown tables
code/make_figures.py       JSON to figures
code/audit.py              manuscript-number reconciliation
code/refcheck.py           bibliography verification
results/                   every number, as JSON
refs/                      bibliography and screening log
legacy/                    frozen old manuscript, read-only
```

## Environment

Python 3.12.14, numpy 2.3.5, scipy 1.18.1, scikit-learn 1.9.1, matplotlib 3.11.2.
`requirements.txt` is the contract. CIFAR-10 will add torch in phase 2.

## Status

Phase 0 complete: scaffold, legacy freeze, audit A on digits.
Next: phase 1, audits B and C.
