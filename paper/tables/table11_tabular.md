# Table 11. Covertype audit B

120,000-row stratified subset, 54 features, 7 classes, logistic regression,
20,000 calibration points, 40,000 test points, alpha = 0.10, 5 seeds. The two
training sizes give test accuracies of 0.717 and 0.721.

| train | score | raw coverage | raw empty | raw size | forced coverage | forced size | delta |
|---|---|---|---|---|---|---|---|
| 6,000 | naive | 0.900 | 0.000 | 1.53 | 0.900 | 1.53 | 0.000 |
| 6,000 | APS randomized | 0.901 | 0.003 | 1.67 | 0.904 | 1.68 | 0.003 |
| 6,000 | APS deterministic | 0.900 | 0.004 | 1.92 | 0.903 | 1.92 | 0.004 |
| 60,000 | naive | 0.901 | 0.000 | 1.51 | 0.901 | 1.51 | 0.000 |
| 60,000 | APS randomized | 0.900 | 0.003 | 1.65 | 0.903 | 1.66 | 0.003 |
| 60,000 | APS deterministic | 0.899 | 0.001 | 1.89 | 0.900 | 1.89 | 0.001 |

delta is forced coverage minus raw coverage. The identity delta = empty rate x
conditional accuracy holds. The empty rate is 0.0 to 0.4 percent, so the change is
0.0 to 0.4 points. The trap is a regime effect, not a universal constant.
