# CIFAR-10, audit A: a calibrated threshold is split conformal

alpha = 0.10, n_cal = 2000, 5 seeds, 10k official test set.
Coverage is the mean over seeds. Raw keeps empty sets; forced fills them with the argmax.

| n_train | method | coverage raw | coverage forced | size raw | empty raw |
|---|---|---|---|---|---|
| 100 | raw threshold 0.90 | 0.290 | 0.692 | 0.310 | 0.690 |
| 100 | max-prob quantile | 0.668 | 0.702 | 0.921 | 0.103 |
| 100 | true-class quantile | 0.898 | 0.898 | 2.086 | 0.000 |
| 100 | t = 1-q | 0.898 | 0.898 | 2.090 | 0.000 |
| 100 | split conformal | 0.898 | 0.898 | 2.090 | 0.000 |
| 100 | APS | 0.896 | 0.911 | 2.471 | 0.016 |
| 100 | **accuracy** | **0.692** | | | |
| 1000 | raw threshold 0.90 | 0.647 | 0.803 | 0.705 | 0.295 |
| 1000 | max-prob quantile | 0.762 | 0.803 | 0.899 | 0.101 |
| 1000 | true-class quantile | 0.894 | 0.894 | 1.344 | 0.000 |
| 1000 | t = 1-q | 0.894 | 0.894 | 1.346 | 0.000 |
| 1000 | split conformal | 0.894 | 0.894 | 1.346 | 0.000 |
| 1000 | APS | 0.892 | 0.911 | 1.497 | 0.021 |
| 1000 | **accuracy** | **0.803** | | | |
| 5000 | raw threshold 0.90 | 0.731 | 0.818 | 0.819 | 0.181 |
| 5000 | max-prob quantile | 0.771 | 0.818 | 0.892 | 0.108 |
| 5000 | true-class quantile | 0.899 | 0.899 | 1.286 | 0.000 |
| 5000 | t = 1-q | 0.899 | 0.899 | 1.287 | 0.000 |
| 5000 | split conformal | 0.899 | 0.899 | 1.287 | 0.000 |
| 5000 | APS | 0.897 | 0.907 | 1.351 | 0.011 |
| 5000 | **accuracy** | **0.818** | | | |
| 30000 | raw threshold 0.90 | 0.716 | 0.855 | 0.756 | 0.244 |
| 30000 | max-prob quantile | 0.810 | 0.855 | 0.899 | 0.101 |
| 30000 | true-class quantile | 0.888 | 0.888 | 1.089 | 0.001 |
| 30000 | t = 1-q | 0.888 | 0.888 | 1.090 | 0.000 |
| 30000 | split conformal | 0.888 | 0.888 | 1.090 | 0.000 |
| 30000 | APS | 0.887 | 0.927 | 1.258 | 0.041 |
| 30000 | **accuracy** | **0.855** | | | |
