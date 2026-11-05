# Table 1. Guarantee by data assumption

Each cell gives a representative method, the assumption it needs, and the price it pays.
"Open" means no method in the reviewed set covers that cell. The empty cells are the
open problems of Section 7, not gaps in the table.

| guarantee | exchangeable | covariate shift | non-exchangeable / temporal | known groups |
|---|---|---|---|---|
| marginal coverage | Vovk2005, Lei2018, Angelopoulos2021intro. One calibration pass. | Tibshirani2019. Likelihood ratio known or estimable. | Beyond (Barber et al. 2023), Oliveira2022. Gap bounded by the violation. | Vovk2012 (Mondrian). Per-group quantiles; small n per group. |
| group-conditional coverage | Vovk2012, Gibbs2025. Group-wise quantiles; smaller effective n. | open | open | Vovk2012, Gibbs2025. Group labels known at test. |
| pointwise conditional coverage | Barber2021 (impossible without assumptions), Hore2024 (local weights and smoothness). Larger sets. | open | open | open (implied by pointwise) |
| risk control | Bates2021, CRC (Angelopoulos et al. 2022), LTT (Angelopoulos et al. 2025). Monotone loss; grid and multiplicity. | open in the reviewed set | NonExchgCRC (Farinhas et al. 2023). Bounded non-exchangeability. | Combes2026 (Macro Mondrian CRC). |
