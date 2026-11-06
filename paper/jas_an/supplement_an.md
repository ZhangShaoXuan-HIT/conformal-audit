# Supplementary material

## Table S1. Guarantee by data assumption

Each cell gives a representative method, the assumption it needs, and the price it pays.
"Open" means no method in the reviewed set covers that cell.

| guarantee | exchangeable | covariate shift | non-exchangeable / temporal | known groups |
|---|---|---|---|---|
| marginal coverage | Vovk et al. (2005), Lei et al. (2018), Angelopoulos & Bates (2023). One calibration pass. | Tibshirani et al. (2019). Likelihood ratio known or estimable. | Barber et al. (2023), Oliveira et al. (2022). Gap bounded by the violation. | Vovk (2012). Per-group quantiles; small n per group. |
| group-conditional coverage | Vovk (2012), Gibbs et al. (2025). Group-wise quantiles; smaller effective n. | open | open | Vovk (2012), Gibbs et al. (2025). Group labels known at test. |
| pointwise conditional coverage | Barber et al. (2021), Hore & Barber (2025). Larger sets. | open | open | open |
| risk control | Bates et al. (2021), Angelopoulos et al. (2022), Angelopoulos et al. (2025). Monotone loss; grid and multiplicity. | open in the reviewed set | Farinhas et al. (2023). Bounded non-exchangeability. | Combes et al. (2026). |

### Table S2. A calibrated threshold is split conformal

digits, alpha = 0.10, n_cal = 449, 5 seeds. Coverage is the mean over seeds.
Raw keeps empty sets; forced fills them with the argmax. Size is mean cardinality.
Pointwise set equality between the conformal threshold and split conformal: mismatches = 0.

### strength = 0.05 (n_train = 44)

| method | coverage raw | coverage forced | size raw | size forced | empty raw |
|---|---|---|---|---|---|
| softmax threshold, raw t = 1-alpha | 0.294 | 0.833 | 0.299 | 1.000 | 0.701 |
| threshold at max-prob quantile | 0.800 | 0.837 | 0.920 | 1.006 | 0.086 |
| threshold at true-class quantile | 0.918 | 0.918 | 1.389 | 1.390 | 0.000 |
| threshold at t = 1-q (conformal) | 0.919 | 0.919 | 1.396 | 1.397 | 0.000 |
| split conformal, naive score | 0.919 | 0.919 | 1.396 | 1.397 | 0.000 |
| split conformal, APS | 0.917 | 0.952 | 1.886 | 1.922 | 0.036 |

### strength = 0.25 (n_train = 224)

| method | coverage raw | coverage forced | size raw | size forced | empty raw |
|---|---|---|---|---|---|
| softmax threshold, raw t = 1-alpha | 0.713 | 0.938 | 0.719 | 1.000 | 0.281 |
| threshold at max-prob quantile | 0.886 | 0.938 | 0.912 | 1.000 | 0.088 |
| threshold at true-class quantile | 0.909 | 0.939 | 0.949 | 1.002 | 0.053 |
| threshold at t = 1-q (conformal) | 0.911 | 0.939 | 0.951 | 1.002 | 0.051 |
| split conformal, naive score | 0.911 | 0.939 | 0.951 | 1.002 | 0.051 |
| split conformal, APS | 0.904 | 0.976 | 1.178 | 1.251 | 0.073 |

### strength = 1.00 (n_train = 898)

| method | coverage raw | coverage forced | size raw | size forced | empty raw |
|---|---|---|---|---|---|
| softmax threshold, raw t = 1-alpha | 0.855 | 0.964 | 0.860 | 1.000 | 0.140 |
| threshold at max-prob quantile | 0.901 | 0.964 | 0.912 | 1.000 | 0.088 |
| threshold at true-class quantile | 0.908 | 0.964 | 0.920 | 1.000 | 0.080 |
| threshold at t = 1-q (conformal) | 0.910 | 0.964 | 0.922 | 1.000 | 0.078 |
| split conformal, naive score | 0.910 | 0.964 | 0.922 | 1.000 | 0.078 |
| split conformal, APS | 0.903 | 0.982 | 1.034 | 1.113 | 0.079 |



### Table S3. Non-empty post-processing inflates coverage

digits, alpha = 0.10, 5 seeds. Delta = forced coverage - raw coverage.
Raw empty is the share of sets that were empty before the argmax was forced in.

### strength = 0.05 (n_train = 44)

| score | n_cal | coverage raw | coverage forced | delta | empty raw | size raw | size forced |
|---|---|---|---|---|---|---|---|
| naive | 100 | 0.932 | 0.932 | +0.000 | 0.000 | 1.565 | 1.565 |
| naive | 225 | 0.929 | 0.929 | +0.000 | 0.000 | 1.491 | 1.491 |
| naive | 449 | 0.919 | 0.919 | +0.000 | 0.000 | 1.396 | 1.397 |
| APS randomized | 100 | 0.914 | 0.954 | +0.040 | 0.040 | 1.983 | 2.024 |
| APS randomized | 225 | 0.918 | 0.952 | +0.033 | 0.034 | 1.864 | 1.898 |
| APS randomized | 449 | 0.920 | 0.954 | +0.033 | 0.034 | 1.922 | 1.956 |
| APS deterministic | 100 | 0.893 | 0.981 | +0.088 | 0.090 | 3.551 | 3.641 |
| APS deterministic | 225 | 0.899 | 0.984 | +0.085 | 0.086 | 3.619 | 3.705 |
| APS deterministic | 449 | 0.898 | 0.981 | +0.084 | 0.084 | 3.549 | 3.634 |
| RAPS | 100 | 0.922 | 0.952 | +0.030 | 0.031 | 1.941 | 1.972 |
| RAPS | 225 | 0.917 | 0.951 | +0.034 | 0.034 | 1.874 | 1.908 |
| RAPS | 449 | 0.911 | 0.945 | +0.034 | 0.034 | 1.781 | 1.816 |

### strength = 0.25 (n_train = 224)

| score | n_cal | coverage raw | coverage forced | delta | empty raw | size raw | size forced |
|---|---|---|---|---|---|---|---|
| naive | 100 | 0.922 | 0.947 | +0.025 | 0.044 | 0.981 | 1.025 |
| naive | 225 | 0.912 | 0.941 | +0.029 | 0.050 | 0.956 | 1.007 |
| naive | 449 | 0.911 | 0.939 | +0.028 | 0.051 | 0.951 | 1.002 |
| APS randomized | 100 | 0.911 | 0.979 | +0.068 | 0.068 | 1.236 | 1.305 |
| APS randomized | 225 | 0.901 | 0.975 | +0.074 | 0.074 | 1.193 | 1.268 |
| APS randomized | 449 | 0.919 | 0.978 | +0.059 | 0.060 | 1.239 | 1.299 |
| APS deterministic | 100 | 0.892 | 0.995 | +0.104 | 0.105 | 3.220 | 3.325 |
| APS deterministic | 225 | 0.907 | 0.996 | +0.089 | 0.090 | 3.372 | 3.463 |
| APS deterministic | 449 | 0.898 | 0.995 | +0.097 | 0.099 | 3.266 | 3.364 |
| RAPS | 100 | 0.910 | 0.975 | +0.065 | 0.065 | 1.215 | 1.280 |
| RAPS | 225 | 0.894 | 0.973 | +0.080 | 0.080 | 1.186 | 1.266 |
| RAPS | 449 | 0.896 | 0.973 | +0.077 | 0.077 | 1.148 | 1.226 |

### strength = 1.00 (n_train = 898)

| score | n_cal | coverage raw | coverage forced | delta | empty raw | size raw | size forced |
|---|---|---|---|---|---|---|---|
| naive | 100 | 0.929 | 0.964 | +0.035 | 0.056 | 0.944 | 1.000 |
| naive | 225 | 0.917 | 0.964 | +0.047 | 0.071 | 0.929 | 1.000 |
| naive | 449 | 0.910 | 0.964 | +0.054 | 0.078 | 0.922 | 1.000 |
| APS randomized | 100 | 0.903 | 0.984 | +0.081 | 0.081 | 1.049 | 1.130 |
| APS randomized | 225 | 0.899 | 0.981 | +0.082 | 0.082 | 1.044 | 1.126 |
| APS randomized | 449 | 0.913 | 0.983 | +0.070 | 0.070 | 1.068 | 1.137 |
| APS deterministic | 100 | 0.894 | 1.000 | +0.106 | 0.106 | 3.011 | 3.117 |
| APS deterministic | 225 | 0.908 | 1.000 | +0.092 | 0.092 | 3.127 | 3.218 |
| APS deterministic | 449 | 0.911 | 1.000 | +0.089 | 0.089 | 3.110 | 3.199 |
| RAPS | 100 | 0.900 | 0.982 | +0.081 | 0.082 | 1.028 | 1.110 |
| RAPS | 225 | 0.887 | 0.982 | +0.095 | 0.096 | 1.018 | 1.113 |
| RAPS | 449 | 0.884 | 0.980 | +0.096 | 0.096 | 1.001 | 1.098 |



### Table S4. The alpha_t update is not ACI

digits, alpha = 0.10, 5 seeds. Coverage and size are means over seeds.
Min/max block are computed on the seed-averaged block curve. Clip is the share of steps at a clip bound.

### schedule = linear

| update | gamma | coverage | seed SD | size | min block | max block | alpha final | clip | sets >= 9 |
|---|---|---|---|---|---|---|---|---|---|
| static | — | 0.666 | 0.100 | 1.524 | 0.388 | 0.968 | 0.1000 | 0.000 | 0.000 |
| fixed | 0.005 | 0.832 | 0.023 | 3.371 | 0.776 | 0.948 | 0.0054 | 0.045 | 0.130 |
| fixed | 0.010 | 0.840 | 0.030 | 3.598 | 0.768 | 0.932 | 0.0064 | 0.071 | 0.139 |
| fixed | 0.020 | 0.836 | 0.038 | 3.444 | 0.732 | 0.928 | 0.0074 | 0.091 | 0.108 |
| fixed | 0.050 | 0.818 | 0.049 | 3.469 | 0.684 | 0.916 | 0.0090 | 0.132 | 0.105 |
| fixed | 0.100 | 0.804 | 0.046 | 3.182 | 0.668 | 0.908 | 0.0090 | 0.156 | 0.087 |
| fixed | 0.200 | 0.775 | 0.043 | 3.103 | 0.624 | 0.904 | 0.0170 | 0.203 | 0.098 |
| buggy | 0.005 | 0.849 | 0.025 | 3.773 | 0.784 | 0.940 | 0.0010 | 0.052 | 0.176 |
| buggy | 0.010 | 0.865 | 0.031 | 4.273 | 0.780 | 0.924 | 0.0010 | 0.061 | 0.216 |
| buggy | 0.020 | 0.869 | 0.036 | 4.580 | 0.752 | 0.944 | 0.0011 | 0.065 | 0.244 |
| buggy | 0.050 | 0.870 | 0.043 | 5.169 | 0.792 | 0.956 | 0.0012 | 0.070 | 0.297 |
| buggy | 0.100 | 0.781 | 0.205 | 4.868 | 0.668 | 0.868 | 0.0014 | 0.076 | 0.279 |
| buggy | 0.200 | 0.769 | 0.153 | 4.788 | 0.476 | 0.900 | 0.0019 | 0.091 | 0.260 |

### schedule = step

| update | gamma | coverage | seed SD | size | min block | max block | alpha final | clip | sets >= 9 |
|---|---|---|---|---|---|---|---|---|---|
| static | — | 0.663 | 0.085 | 1.488 | 0.432 | 0.960 | 0.1000 | 0.000 | 0.000 |
| fixed | 0.005 | 0.830 | 0.024 | 3.358 | 0.576 | 0.948 | 0.0064 | 0.051 | 0.130 |
| fixed | 0.010 | 0.835 | 0.028 | 3.492 | 0.680 | 0.940 | 0.0102 | 0.077 | 0.132 |
| fixed | 0.020 | 0.828 | 0.039 | 3.349 | 0.732 | 0.928 | 0.0098 | 0.102 | 0.104 |
| fixed | 0.050 | 0.808 | 0.046 | 3.176 | 0.712 | 0.916 | 0.0120 | 0.138 | 0.088 |
| fixed | 0.100 | 0.790 | 0.047 | 3.013 | 0.684 | 0.916 | 0.0190 | 0.166 | 0.079 |
| fixed | 0.200 | 0.767 | 0.042 | 3.010 | 0.664 | 0.900 | 0.0170 | 0.208 | 0.084 |
| buggy | 0.005 | 0.836 | 0.028 | 3.575 | 0.564 | 0.944 | 0.0010 | 0.060 | 0.161 |
| buggy | 0.010 | 0.845 | 0.031 | 3.826 | 0.676 | 0.924 | 0.0011 | 0.072 | 0.178 |
| buggy | 0.020 | 0.839 | 0.040 | 3.928 | 0.712 | 0.924 | 0.0012 | 0.076 | 0.188 |
| buggy | 0.050 | 0.809 | 0.067 | 4.078 | 0.636 | 0.892 | 0.0016 | 0.078 | 0.202 |
| buggy | 0.100 | 0.748 | 0.183 | 4.042 | 0.620 | 0.852 | 0.0015 | 0.086 | 0.199 |
| buggy | 0.200 | 0.733 | 0.163 | 4.262 | 0.484 | 0.840 | 0.0024 | 0.092 | 0.214 |

### schedule = abrupt

| update | gamma | coverage | seed SD | size | min block | max block | alpha final | clip | sets >= 9 |
|---|---|---|---|---|---|---|---|---|---|
| static | — | 0.739 | 0.042 | 1.453 | 0.360 | 0.960 | 0.1000 | 0.000 | 0.000 |
| fixed | 0.005 | 0.831 | 0.021 | 2.411 | 0.508 | 0.948 | 0.0054 | 0.040 | 0.070 |
| fixed | 0.010 | 0.840 | 0.023 | 2.574 | 0.608 | 0.940 | 0.0064 | 0.061 | 0.073 |
| fixed | 0.020 | 0.836 | 0.029 | 2.499 | 0.640 | 0.928 | 0.0074 | 0.080 | 0.062 |
| fixed | 0.050 | 0.824 | 0.033 | 2.425 | 0.644 | 0.916 | 0.0090 | 0.103 | 0.052 |
| fixed | 0.100 | 0.816 | 0.030 | 2.398 | 0.620 | 0.916 | 0.0090 | 0.124 | 0.048 |
| fixed | 0.200 | 0.796 | 0.022 | 2.528 | 0.612 | 0.900 | 0.0170 | 0.167 | 0.061 |
| buggy | 0.005 | 0.828 | 0.024 | 2.448 | 0.492 | 0.944 | 0.0010 | 0.042 | 0.079 |
| buggy | 0.010 | 0.832 | 0.039 | 2.598 | 0.588 | 0.924 | 0.0010 | 0.052 | 0.085 |
| buggy | 0.020 | 0.807 | 0.065 | 2.580 | 0.564 | 0.924 | 0.0011 | 0.054 | 0.089 |
| buggy | 0.050 | 0.767 | 0.107 | 2.904 | 0.636 | 0.892 | 0.0012 | 0.062 | 0.115 |
| buggy | 0.100 | 0.628 | 0.320 | 2.500 | 0.492 | 0.852 | 0.3387 | 0.048 | 0.092 |
| buggy | 0.200 | 0.576 | 0.259 | 2.649 | 0.316 | 0.776 | 0.0019 | 0.066 | 0.122 |



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


### Table S7. CIFAR-10-C style drift

Five corruption types (gaussian_noise, defocus_blur, contrast, brightness,
jpeg_compression), three severities (1, 3, 5), 1,000 images per block, 3,000
points per stream, 3 seeds, alpha = 0.10, gamma = 0.02. Calibration is clean.

| update | coverage | mean size | block sev 1 | block sev 3 | block sev 5 | alpha final | clip | sets >= 9 |
|---|---|---|---|---|---|---|---|---|
| static | 0.451 | 1.30 | 0.588 | 0.457 | 0.308 | — | — | 0.000 |
| fixed | 0.828 | 4.93 | 0.853 | 0.829 | 0.802 | 0.0106 | 0.13 | 0.145 |
| buggy | 0.936 | 6.97 | 0.940 | 0.939 | 0.928 | 0.0019 | 0.05 | 0.380 |

### Per corruption

Coverage and mean set size, averaged over three seeds.

| corruption | static | fixed | buggy |
|---|---|---|---|
| gaussian_noise | 0.22 / 1.34 | 0.66 / 5.45 | 0.81 / 7.02 |
| defocus_blur | 0.24 / 1.37 | 0.85 / 7.52 | 0.98 / 9.42 |
| contrast | 0.52 / 1.33 | 0.87 / 4.94 | 0.98 / 7.42 |
| brightness | 0.80 / 1.15 | 0.90 / 1.88 | 0.94 / 3.70 |
| jpeg_compression | 0.47 / 1.32 | 0.86 / 4.87 | 0.97 / 7.28 |

The incorrect update reports 10.8 points more coverage than the correct one, at a
41 percent larger mean set size, and raises the share of near-trivial sets from
14.5 to 38.0 percent. The correct update also falls short of 0.90, at 0.828.


### Table S8. Library behavior audit

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

### MAPIE 1.6.0, five seeds, alpha = 0.10

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


### Runtime cross-check

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


### Table S9. Coverage against four surveys

Authors' assessment of topical coverage, not of quality. A circle means the topic is not
a focus of that survey, not that the survey is deficient. Symbols: full circle =
comprehensive, half circle = partial, open circle = not a focus.

| dimension | this paper | Angelopoulos & Bates 2021 | Fontana et al. 2023 | Campos et al. 2024 | Zhou et al. 2025 |
|---|---|---|---|---|---|
| foundations | half | full | full | half | full |
| scores | full | full | half | full | full |
| conditional coverage | full | half | full | half | half |
| risk control | full | half | half | half | half |
| non-exchangeable | full | open | half | half | half |
| language models | half | open | open | full | half |
| implementation audit | full | open | open | open | open |
| two-dataset experiments | full | open | open | open | open |

The last two rows are the reason this paper exists. The first six rows are the reason it
has to cite the other four.


### Table S10. Experimental grid

| dataset | train pool | strengths | calibration | test | model | scores | alpha | seeds |
|---|---|---|---|---|---|---|---|---|
| digits | 898 | 44 / 224 / 898 | 449 for A and C; 100 / 225 / 449 for B | 450 | standardiser + logistic regression | naive, APS randomized, APS deterministic, RAPS | 0.10 for A and C; 0.05 / 0.10 / 0.20 for B | 5 |
| CIFAR-10 | 30,000 | 100 / 1,000 / 5,000 / 30,000 | 2,000 for A; 500 / 2,000 / 10,000 for B; 2,000 for C | 10,000 | ResNet-18 features + logistic regression | naive, APS randomized, APS deterministic, RAPS | 0.10 for A and C; 0.05 / 0.10 / 0.20 for B | 5 for A and B; 3 for C |
| covertype | 120,000-row subset | 6,000 / 60,000 | 20,000 | 40,000 | standardiser + logistic regression | naive, APS randomized, APS deterministic | 0.05 / 0.10 / 0.20 | 5 |

The calibration column gives the sizes used in each audit. The strength column gives
the number of training points used to fit the model; the calibration and test sets are
disjoint from it.


### Table S11. Covertype audit B

120,000-row stratified subset, 54 features, 7 classes, logistic regression,
20,000 calibration points, 40,000 test points, alpha = 0.10, 5 seeds.

| train | score | raw coverage | raw empty | raw size | forced coverage | forced size | delta |
|---|---|---|---|---|---|---|---|
| 6000 | naive | 0.900 | 0.000 | 1.53 | 0.900 | 1.53 | 0.000 |
| 6000 | APS randomized | 0.901 | 0.003 | 1.67 | 0.904 | 1.68 | 0.003 |
| 6000 | APS deterministic | 0.900 | 0.004 | 1.92 | 0.903 | 1.92 | 0.004 |
| 60000 | naive | 0.901 | 0.000 | 1.51 | 0.901 | 1.51 | 0.000 |
| 60000 | APS randomized | 0.900 | 0.003 | 1.65 | 0.903 | 1.66 | 0.003 |
| 60000 | APS deterministic | 0.899 | 0.001 | 1.89 | 0.900 | 1.89 | 0.001 |

The two training sizes give test accuracies of 0.717 and 0.721.

delta is forced coverage minus raw coverage. The identity delta = empty rate x
conditional accuracy holds. The empty rate is 0.0 to 0.4 percent, so the change is
0.0 to 0.4 points. The trap is a regime effect, not a universal constant.


### Table S12. Cost-sensitive reading of the fallback

At alpha = 0.10, over cells with a non-zero raw empty rate. a_E is the
conditional accuracy of the inserted label on empty sets, estimated as
delta / empty rate. The threshold is the cost ratio c_a / c_e above which
forcing is better than abstaining.

| dataset | score | cells | mean empty rate | mean a_E | threshold c_a/c_e |
|---|---|---|---|---|---|
| digits | aps_rand | 45 | 0.060 | 0.99 | 0.01 |
| digits | aps_det | 45 | 0.093 | 0.99 | 0.01 |
| cifar10 | aps_rand | 60 | 0.020 | 0.96 | 0.04 |
| cifar10 | aps_det | 45 | 0.084 | 0.99 | 0.01 |
| covertype | aps_rand | 10 | 0.003 | 0.94 | 0.06 |
| covertype | aps_det | 10 | 0.003 | 0.94 | 0.06 |

The threshold is small in every dataset (0.01 to 0.06); the empty rate is not.
The expected loss difference at a given cost ratio is proportional to the empty rate,
so the same rule matters much more on digits than on covertype.


## Reporting checklist

1. Report the nominal level and the realized coverage, raw and forced.
2. Report the empty rate.
3. Report the calibration size and the finite-sample correction.
4. Report the score and the set-size distribution.
5. Report the update rule and its target.
6. Report the library version and its non-empty policy.

