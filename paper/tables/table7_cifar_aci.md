# Table 7. CIFAR-10-C style drift

Five corruption types (gaussian_noise, defocus_blur, contrast, brightness,
jpeg_compression), three severities (1, 3, 5), 1,000 images per block, 3,000
points per stream, 3 seeds, alpha = 0.10, gamma = 0.02. Calibration is clean.

| update | coverage | mean size | block sev 1 | block sev 3 | block sev 5 | alpha final | clip | sets >= 9 |
|---|---|---|---|---|---|---|---|---|
| static | 0.451 | 1.30 | 0.588 | 0.457 | 0.308 | — | — | 0.000 |
| fixed | 0.828 | 4.93 | 0.853 | 0.829 | 0.802 | 0.0106 | 0.13 | 0.145 |
| buggy | 0.936 | 6.97 | 0.940 | 0.939 | 0.928 | 0.0019 | 0.05 | 0.380 |

## Per corruption

Coverage and mean set size, averaged over three seeds.

| corruption | static | fixed | buggy |
|---|---|---|---|
| gaussian_noise | 0.22 / 1.3 | 0.66 / 5.4 | 0.81 / 7.0 |
| defocus_blur | 0.24 / 1.4 | 0.85 / 7.5 | 0.98 / 9.4 |
| contrast | 0.52 / 1.3 | 0.87 / 4.9 | 0.98 / 7.4 |
| brightness | 0.80 / 1.1 | 0.90 / 1.9 | 0.94 / 3.7 |
| jpeg_compression | 0.47 / 1.3 | 0.86 / 4.9 | 0.97 / 7.3 |

The incorrect update reports 10.8 points more coverage than the correct one, at a
41 percent larger mean set size, and raises the share of near-trivial sets from
14.5 to 38.0 percent. The correct update also falls short of 0.90, at 0.828.
