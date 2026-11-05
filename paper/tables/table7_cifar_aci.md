# CIFAR-10, audit C: the alpha_t update is not ACI

2,000 test images in 20 blocks, Gaussian pixel noise ramping from 0 to 0.40.
3 seeds, alpha = 0.10. Min/max block are computed on the seed-averaged block curve.

| update | gamma | coverage | seed SD | size | min block | max block | alpha final | clip | sets >= 9 |
|---|---|---|---|---|---|---|---|---|---|
| static | — | 0.272 | 0.002 | 1.33 | 0.063 | 0.927 | 0.1000 | 0.00 | 0.000 |
| fixed | 0.02 | 0.677 | 0.025 | 5.13 | 0.563 | 0.910 | 0.0010 | 0.31 | 0.046 |
| fixed | 0.05 | 0.639 | 0.017 | 4.78 | 0.517 | 0.900 | 0.0010 | 0.35 | 0.048 |
| buggy | 0.02 | 0.801 | 0.061 | 6.39 | 0.687 | 0.950 | 0.0010 | 0.19 | 0.129 |
| buggy | 0.05 | 0.799 | 0.058 | 6.43 | 0.687 | 0.953 | 0.0010 | 0.19 | 0.125 |

