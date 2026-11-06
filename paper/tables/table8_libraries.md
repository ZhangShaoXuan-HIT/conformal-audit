# Table 8. Library behavior audit

Versions checked on 2026-11-06. Line numbers refer to the named files in the
package versions listed; the source snapshots were downloaded locally for the audit.
Runtime: MAPIE, puncc, crepes, nonconformist, and conformal. Source inspection:
TorchCP, coverforest, and AdaptiveConformal.

| library | version | task | empty sets possible | default policy | evidence | ACI update |
|---|---|---|---|---|---|---|
| MAPIE | 1.6.0 | classification | LAC yes; APS policy-dependent | APS default include_last_label=True: no empty sets, coverage 0.9457 vs 0.90 | classification.py:238-283; aps.py:355-358; lac.py:205-207; results/mapie_empty.json | fixed alpha_0 (time_series_regression.py:329) |
| TorchCP | 1.2.1 | classification | yes | no forcing; boolean mask (scores <= q_hat) | classification/predictor/base.py:111 | fixed alpha (regression/predictor/aci.py:197) |
| puncc | 0.9.3 | classification | yes | no forcing; index lists, empty when no class passes | api/prediction_sets.py:70-78, 112-119 | not implemented |
| crepes | 0.9.1 | classification | yes | no forcing; boolean mask (p_values >= 1-confidence) | base.py:340 | not implemented |
| nonconformist | 2.1.0 | classification | yes | no forcing; boolean matrix of p-values > significance; smoothing=True | icp.py:199-250 | not implemented |
| conformal | 0.1 | classification | yes (empty list possible) | no forcing; per-label thresholds at 100 - epsilon percentile | __init__.py:76-93, 95-108 | not implemented |
| coverforest | 0.0.3 | classification | yes by default | allow_empty_sets=True default; False avoids empty sets; docs warn to use it sparingly | _forest.py:1457, 2006-2008 | not applicable |
| AdaptiveConformal | GitHub main | regression intervals | not applicable | not applicable | R/aci_algorithm.R:78-81 | fixed alpha (correct) |

## MAPIE 1.6.0, five seeds, alpha = 0.10

Synthetic five-class data, logistic regression, 2,000 test points per seed.
The correct randomised APS is the last row. The default is the second row.

| score | include_last_label | coverage (mean +/- SD) | empty rate | size |
|---|---|---|---|---|
| LAC | True | 0.9016 +/- 0.0080 | 0.0000 | 3.151 |
| APS, default | True | 0.9457 +/- 0.0107 | 0.0000 | 3.676 |
| APS | False | 0.8284 +/- 0.0150 | 0.0000 | 2.684 |
| APS, randomized | randomized | 0.8998 +/- 0.0105 | 0.0004 | 3.232 |

The default APS setting over-covers by 4.6 points with zero empty sets. The randomised
setting, which is the exact conformal rule, lands on the target. The difference is the
non-empty post-processing, not the score.


## Runtime cross-check

Same synthetic five-class task for all libraries: 8,000 samples, logistic
regression, 2,000 test points, alpha = 0.10, test accuracy 0.487. One seed for every library in this table; the MAPIE numbers in the table above
use five seeds. The puncc randomized row has no fixed seed; its empty rate was
0.0 to 0.2 percent across runs.

| library | setting | coverage | empty rate | mean size |
|---|---|---|---|---|
| MAPIE | LAC | 0.895 | 0.000 | 2.87 |
| MAPIE | APS, include_last_label=True (default) | 0.949 | 0.000 | 3.46 |
| MAPIE | APS, include_last_label=False | 0.809 | 0.000 | 2.48 |
| MAPIE | APS, randomized | 0.892 | 0.001 | 3.02 |
| puncc | LAC | 0.895 | 0.000 | 2.87 |
| puncc | APS, rand=True | 0.889 | 0.000 | 2.99 |
| puncc | APS, rand=False | 0.977 | 0.000 | 4.06 |
| crepes | LAC (hinge), p >= alpha | 0.895 | 0.000 | 2.87 |
| nonconformist | ICP margin, smoothing=True | 0.890 | 0.000 | 3.50 |
| conformal | per-label thresholds, epsilon=10 | 0.890 | 0.000 | 3.02 |

coverforest 0.0.3 could not be run on scikit-learn 1.9: its forest code calls
_get_n_samples_bootstrap without the sample_weight argument that the installed
scikit-learn requires. TorchCP 1.2.1 was not run: its optional graph dependencies
(torch_geometric) are not installed. Both were read at the source level.
