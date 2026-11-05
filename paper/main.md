# What Does Conformal Prediction Add?
## A Controlled Audit of Calibrated Set-Valued Classification

**Status**: phase 0. Skeleton and first experiment only. No prose yet.
**Core claim**: 共形预测增加的是有限样本覆盖保证，不是准确率，也不是集合构造本身。

---

## 1. Introduction (800 words)

A practitioner sets a 0.90 coverage target, thresholds the softmax at 0.90, and
reports the model's accuracy. The number looks like a coverage guarantee and is
not one. Three different mistakes produce this outcome, and all three are common
in released code.

### Positioning against the closest work

<!-- phase 3A. Do not claim the threshold geometry as new.
- Aguru 2026 (Zenodo, binary): proves threshold >= 1/2 implies singleton or empty.
  Cite it; start from the multi-class corollary and the empirical consequences.
- Mehrtens et al. 2025 (arXiv 2506.18162): pitfalls in medical imaging, different set.
- Gauthier, Bach & Jordan 2025 (arXiv 2510.04318): empty sets as a low-coverage outcome.
- Al Bataineh 2026 (IEEE Sensors Letters): empty sets as a drift alarm.
- Susmann, Chambaz & Josse 2023 (arXiv 2312.00448): AdaptiveConformal R package.
- Avoid the word "pitfalls" in the title and abstract; use "audit" or "accounting".
-->

## 2. The guarantee in one page (1200 words)

Exchangeability, the finite-sample quantile correction, the difference between
marginal and conditional coverage, and why the guarantee is a lower bound rather
than an equality. No history, no generations.

## 3. A two-axis map (1200 words)

Rows: marginal, group-conditional, pointwise, risk control.
Columns: exchangeable, covariate shift, non-exchangeable, known groups.
Each cell: representative method, assumption, cost, reference.
This replaces the four-generation narrative.

## 4. Three implementation traps (2500 words)

### 4.1 A calibrated threshold is split conformal
<!-- cite Aguru 2026 for the binary threshold fact; our contribution is the multi-class consequence and the equivalence in practice, not the geometry. -->
The set {y : p_y >= 1-q} with q the conformal quantile of 1-p_true is exactly
the naive split conformal set. The distinction is calibration, not set
construction. Calibrating on the max probability instead of the true-class
probability fails to reach the target.

### 4.2 Non-empty post-processing inflates coverage
<!-- novel core. Cite Gauthier 2025 and Al Bataineh 2026 for empty sets as a known phenomenon; distinguish: they use or avoid empty sets, we measure forced non-empty reporting. -->
Forcing the argmax into empty sets raises coverage and size. The inflation grows
with alpha and with the empty rate. Report both raw and forced numbers.
<!-- phase 1: mean delta 0.077, max 0.318; naive 0.041, APS rand 0.080, APS det 0.108, RAPS 0.078 -->

### 4.3 The alpha_t update is not ACI
<!-- cite Susmann et al. 2023 (AdaptiveConformal). The update rule is not new; the audit of implementations is. -->

### 4.4 Do real libraries do this?
<!-- phase 3B. MAPIE 1.6.0 APS default include_last_label=True: 0.9457 +/- 0.0107 with
0 empty sets; randomized: 0.8998 +/- 0.0105. TorchCP, puncc and crepes allow empty sets.
coverforest exposes allow_empty_sets. MAPIE, TorchCP and AdaptiveConformal use fixed-alpha
ACI; the alpha_t bug is a hand-written error, not an ecosystem default. See Table 8. -->
ACI uses a fixed target alpha. Replacing it with alpha_t removes the
target-tracking guarantee and can look successful by collapsing to the clip.
<!-- phase 1, average over three schedules, gamma 0.02: fixed = 0.833 cov, 3.10 size, alpha 0.0082; buggy = 0.838 cov, 3.70 size, alpha 0.0011, near-trivial 17.3% vs 9.1%. At gamma 0.1 the buggy update diverges (seed SD 0.205). -->

## 5. Experiments (1800 words)

5.1 Setup: digits and CIFAR-10, two model strengths, n_cal sweep, 5 seeds.
5.2 Audit A on digits and CIFAR.
5.3 Audit B on digits and CIFAR.
5.4 Audit C on controlled drift streams.
5.5 Regime map: when do the traps matter?
<!-- phase 2: empty rate, not accuracy, governs the forcing trap. CIFAR raw threshold empty 18-69%; conformal naive near zero; APS detached 7-9%. -->

## 6. A checklist for practitioners (600 words)

1. Report the empty rate before any post-processing.
2. Calibrate the threshold on the true-class probability, not the max probability.
3. State the update rule and the target it is supposed to track.
4. Match marginal coverage before comparing conditional coverage.
5. Report the set-size distribution, not only its mean.

## 7. Open problems (500 words)

Three problems, all stated as measurable gaps. No "does not exist" claims from
the absence of a reference in this bibliography.

---

## Tables and figures

| id | content | source |
|---|---|---|
| T1 | regime map: dataset, model strength, accuracy, ECE, alpha where sets become singleton | results/*.json |
| T2 | calibrated threshold equals split conformal | paper/tables/table2_equivalence.md |
| T3 | post-processing inflation grid | results/postprocess_digits.json |
| T4 | ACI update comparison | results/aci_digits.json |
| F1 | pipeline and the three trap locations | paper/figures/fig1_pipeline |
| F2 | coverage and size versus threshold | paper/figures/fig2_equivalence |
| F3 | delta coverage versus raw empty rate | paper/figures/fig3_forcing |
| F4 | coverage and alpha trajectories under drift | paper/figures/fig4_aci |
| T5 | CIFAR audit A | paper/tables/table5_cifar_equivalence.md |
| T6 | CIFAR audit B | paper/tables/table6_cifar_postprocess.md |
| T7 | CIFAR audit C | paper/tables/table7_cifar_aci.md |
| T8 | library behavior audit | paper/tables/table8_libraries.md |
| F5 | trap visibility versus empty rate | paper/figures/fig5_regime |

## Claims ledger

| id | claim | evidence | status |
|---|---|---|---|
| C1 | a calibrated true-class threshold is split conformal | T2, exact set equality | supported |
| C2 | max-prob calibration misses the target | T2 | supported (digits) |
| C3 | non-empty forcing inflates coverage | T3, F3 | supported (mean delta 0.077, max 0.318) |
| C4 | the alpha_t update does not track the target | T4, F4 | supported (alpha collapses to clip, size +19%) |
| C5 | the forcing trap is governed by the empty rate, not by model strength alone | T3, T6, F5 | supported (CIFAR naive near zero, APS 1-4%) |
| C6 | real libraries expose or default to non-empty sets | T8, results/mapie_empty.json | supported (MAPIE default 0.9457 vs 0.90, 0 empties) |
| C7 | the alpha_t bug is a hand-written error, not an ecosystem default | T8 source audit | supported (MAPIE, TorchCP, AdaptiveConformal use fixed alpha) |
