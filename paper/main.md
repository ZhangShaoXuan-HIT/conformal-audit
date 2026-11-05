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

ACI uses a fixed target alpha. Replacing it with alpha_t removes the
target-tracking guarantee and can look successful by collapsing to the clip.

<!-- phase 1, average over three schedules, gamma 0.02: fixed = 0.833 cov, 3.10 size, alpha 0.0082; buggy = 0.838 cov, 3.70 size, alpha 0.0011, near-trivial 17.3% vs 9.1%. At gamma 0.1 the buggy update diverges (seed SD 0.205). -->

### 4.4 Do real libraries do this?

The audit so far uses our own set constructor. A reader may ask whether the
behaviour is an artifact of that choice. We inspected six implementations:
MAPIE 1.6.0, TorchCP 1.2.1, puncc 0.9.3, crepes 0.9.1, coverforest 0.0.3,
and the AdaptiveConformal R package. All six were read at the source level.
MAPIE was also run, with five seeds on a synthetic five-class problem.

The first finding is that the empty-set policy is a design choice, not a
universal. MAPIE's APS implementation defaults to include_last_label=True,
which adds the label that crosses the quantile and therefore never returns an
empty set. TorchCP returns the boolean mask scores <= q_hat. puncc returns
index lists. crepes returns p_values >= 1 - confidence. All three can return
empty sets. coverforest exposes the choice directly, with allow_empty_sets=True
as the default and documentation that recommends using False sparingly.
Table 8 summarises the six implementations. It is a policy map, not a defect
list.

The second finding is that MAPIE's default is a non-empty rule of a different
kind from the argmax fallback studied in Section 4.2. It does not insert the
argmax. It inserts the last label whose cumulative mass crosses the threshold.
The effect is nevertheless the same in kind. Over five seeds at alpha = 0.10,
the default reaches 0.9457 +/- 0.0107 with zero empty sets and a mean size of
3.676. The randomized setting, which is the exact conformal rule, reaches
0.8998 +/- 0.0105 with an empty rate of 0.0004 and a mean size of 3.232. The
False setting reaches 0.8284 +/- 0.0150, below the target. The two
non-randomized settings therefore err in opposite directions. The default
over-covers by 4.6 points; the exact rule lands on the target.

The MAPIE documentation acknowledges that True and False "may result in a
coverage higher than 1 - alpha", because neither creates empty sets. It does
not quantify the gap, and it does not say that the default differs from the
exact rule by enough to change a comparison between methods. That is the gap
this section fills.

This matters for how the result should be read. The phenomenon in Section 4.2
is not specific to our argmax fallback. Any non-empty rule changes the
coverage of the sets it produces, and the direction and size of the change
depend on the rule. The argmax fallback produces the identity derived in
Section 4.2, where the gain is the empty rate times the conditional accuracy
of the argmax. The MAPIE default produces a different accounting, but the same
qualitative outcome: coverage above the nominal level, larger sets, and a
reported number that belongs to the post-processing rather than to the
guarantee.

The third finding concerns the ACI update. MAPIE's time-series regressor
updates the level with a fixed target, alpha_t + gamma * (alpha_0 - error).
TorchCP does the same with a fixed alpha. The AdaptiveConformal R package
updates a quantile level against a fixed alpha. None of the three uses the
alpha_t recursion studied in Section 4.3. The error is therefore a risk of
hand-written implementations, not a default of the libraries we checked. That
narrows the claim of Section 4.3. The value of the audit is not that the
libraries are wrong. It is that the error is easy to make, produces a
plausible-looking improvement, and is invisible in a coverage report alone.

Two practical consequences follow. A user of MAPIE's default APS should report
0.946, not 0.90, and should say that the number comes from a non-empty rule. A
user who wants the exact guarantee should select the randomized setting, or
report both the unmodified sets and the non-empty version. More generally, a
coverage report is not interpretable without the set-construction rule that
produced it. The rule is part of the method, and it belongs in the methods
section.

The audit has limits. Five of the six implementations were read but not run.
The versions are those available on 2026-11-06, and line numbers will move.
The MAPIE experiment uses synthetic data, so the 4.6-point gap should be read
as an illustration of the mechanism rather than an estimate for a particular
application. The claim we defend is narrow: in the implementations we audited,
the non-empty policy varies, one widely used default over-covers by 4.6 points,
and the three ACI implementations we checked use the correct fixed-target
update.

<!-- cite: mapie2026, torchcp2026, puncc2026, crepes2026, coverforest2026, adaptiveconformal2023 -->

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
