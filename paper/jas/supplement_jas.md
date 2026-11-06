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


## Table S2. Coverage against four surveys

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


## Table S3. Experimental grid

| dataset | train pool | strengths | calibration | test | model | scores | alpha | seeds |
|---|---|---|---|---|---|---|---|---|
| digits | 898 | 44 / 224 / 898 | 449 for A and C; 100 / 225 / 449 for B | 450 | standardiser + logistic regression | naive, APS randomized, APS deterministic, RAPS | 0.10 for A and C; 0.05 / 0.10 / 0.20 for B | 5 |
| CIFAR-10 | 30,000 | 100 / 1,000 / 5,000 / 30,000 | 2,000 for A; 500 / 2,000 / 10,000 for B; 2,000 for C | 10,000 | ResNet-18 features + logistic regression | naive, APS randomized, APS deterministic, RAPS | 0.10 for A and C; 0.05 / 0.10 / 0.20 for B | 5 for A and B; 3 for C |
| covertype | 120,000-row subset | 6,000 / 60,000 | 20,000 | 40,000 | standardiser + logistic regression | naive, APS randomized, APS deterministic | 0.05 / 0.10 / 0.20 | 5 |

The calibration column gives the sizes used in each audit. The strength column gives
the number of training points used to fit the model; the calibration and test sets are
disjoint from it.
