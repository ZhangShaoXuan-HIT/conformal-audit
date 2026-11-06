# CIFAR-10, audit B: non-empty post-processing inflates coverage

alpha = 0.10, n_cal = 2000, 5 seeds, 10k official test set.
Delta = forced coverage - raw coverage. Raw empty is the share of empty sets.

| n_train | score | coverage raw | coverage forced | delta | empty raw | size raw | size forced |
|---|---|---|---|---|---|---|---|
| 100 | naive | 0.898 | 0.898 | +0.000 | 0.000 | 2.090 | 2.090 |
| 100 | APS randomized | 0.898 | 0.913 | +0.015 | 0.015 | 2.482 | 2.497 |
| 100 | APS deterministic | 0.904 | 0.972 | +0.068 | 0.069 | 4.437 | 4.506 |
| 100 | RAPS | 0.899 | 0.911 | +0.012 | 0.013 | 2.403 | 2.415 |
| 1000 | naive | 0.894 | 0.894 | +0.000 | 0.000 | 1.346 | 1.346 |
| 1000 | APS randomized | 0.896 | 0.914 | +0.018 | 0.019 | 1.515 | 1.534 |
| 1000 | APS deterministic | 0.902 | 0.993 | +0.091 | 0.091 | 4.654 | 4.745 |
| 1000 | RAPS | 0.897 | 0.913 | +0.016 | 0.016 | 1.490 | 1.506 |
| 5000 | naive | 0.899 | 0.899 | +0.000 | 0.000 | 1.287 | 1.287 |
| 5000 | APS randomized | 0.900 | 0.909 | +0.009 | 0.010 | 1.362 | 1.372 |
| 5000 | APS deterministic | 0.994 | 0.994 | +0.000 | 0.000 | 6.083 | 6.083 |
| 5000 | RAPS | 0.899 | 0.907 | +0.008 | 0.008 | 1.338 | 1.346 |
| 30000 | naive | 0.888 | 0.888 | +0.000 | 0.000 | 1.090 | 1.091 |
| 30000 | APS randomized | 0.893 | 0.930 | +0.036 | 0.037 | 1.271 | 1.309 |
| 30000 | APS deterministic | 0.899 | 0.994 | +0.095 | 0.095 | 3.967 | 4.061 |
| 30000 | RAPS | 0.894 | 0.929 | +0.035 | 0.036 | 1.261 | 1.297 |
