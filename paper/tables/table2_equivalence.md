# Table 2. A calibrated threshold is split conformal

digits, alpha = 0.10, n_cal = 449, 5 seeds. Coverage is the mean over seeds.
Raw keeps empty sets; forced fills them with the argmax. Size is mean cardinality.
Pointwise set equality between the conformal threshold and split conformal: mismatches = 0.

## strength = 0.05 (n_train = 44)

| method | coverage raw | coverage forced | size raw | size forced | empty raw |
|---|---|---|---|---|---|
| softmax threshold, raw t = 1-alpha | 0.294 | 0.833 | 0.299 | 1.000 | 0.701 |
| threshold at max-prob quantile | 0.800 | 0.837 | 0.920 | 1.006 | 0.086 |
| threshold at true-class quantile | 0.918 | 0.918 | 1.389 | 1.390 | 0.000 |
| threshold at t = 1-q (conformal) | 0.919 | 0.919 | 1.396 | 1.397 | 0.000 |
| split conformal, naive score | 0.919 | 0.919 | 1.396 | 1.397 | 0.000 |
| split conformal, APS | 0.917 | 0.952 | 1.886 | 1.922 | 0.036 |

## strength = 0.25 (n_train = 224)

| method | coverage raw | coverage forced | size raw | size forced | empty raw |
|---|---|---|---|---|---|
| softmax threshold, raw t = 1-alpha | 0.713 | 0.938 | 0.719 | 1.000 | 0.281 |
| threshold at max-prob quantile | 0.886 | 0.938 | 0.912 | 1.000 | 0.088 |
| threshold at true-class quantile | 0.909 | 0.939 | 0.949 | 1.002 | 0.053 |
| threshold at t = 1-q (conformal) | 0.911 | 0.939 | 0.951 | 1.002 | 0.051 |
| split conformal, naive score | 0.911 | 0.939 | 0.951 | 1.002 | 0.051 |
| split conformal, APS | 0.904 | 0.976 | 1.178 | 1.251 | 0.073 |

## strength = 1.00 (n_train = 898)

| method | coverage raw | coverage forced | size raw | size forced | empty raw |
|---|---|---|---|---|---|
| softmax threshold, raw t = 1-alpha | 0.855 | 0.964 | 0.860 | 1.000 | 0.140 |
| threshold at max-prob quantile | 0.901 | 0.964 | 0.912 | 1.000 | 0.088 |
| threshold at true-class quantile | 0.908 | 0.964 | 0.920 | 1.000 | 0.080 |
| threshold at t = 1-q (conformal) | 0.910 | 0.964 | 0.922 | 1.000 | 0.078 |
| split conformal, naive score | 0.910 | 0.964 | 0.922 | 1.000 | 0.078 |
| split conformal, APS | 0.903 | 0.982 | 1.034 | 1.113 | 0.079 |

