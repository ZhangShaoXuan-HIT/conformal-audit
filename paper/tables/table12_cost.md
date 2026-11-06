# Table 12. Cost-sensitive reading of the fallback

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
