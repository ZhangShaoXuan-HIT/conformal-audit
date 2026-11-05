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

## 2. The guarantee in one page

### 2.1 Exchangeability and what the guarantee assumes

A conformal predictor is a procedure, not a model. It takes a fitted classifier f, a
calibration sample, and a target error rate α, and it returns a set C(x) for each input.
The only assumption is that the calibration pairs and the test pair are exchangeable.
Exchangeability means that the joint distribution is invariant under permutation of the
indices. It is weaker than independence and identical distribution. Every i.i.d. sample is
exchangeable, and so is any sample whose distribution is symmetric in the order of the
observations.

The assumption is easy to state and easy to violate. A calibration set drawn at random from
the same collection as the test set is exchangeable with it. A calibration set drawn from
last year's data and deployed against this year's data is not. A calibration set selected
because it contains the cases the model finds hard is not. A test stream whose distribution
changes after every observation is not. In each case the guarantee does not degrade
gracefully. The coverage on the deployment distribution can fall far below 1 − α while
every diagnostic computed on the calibration distribution looks correct. This is the
failure mode that Section 5.4 measures.

The guarantee is marginal in a second sense as well. It averages over the randomness of the
calibration sample and the test point. It does not say that a particular realized set
covers the particular test label. It says that the procedure covers with probability at
least 1 − α over repeated draws. A single calibration set can produce coverage below
1 − α, and the probability that it does is not zero. For a binary classifier, the
calibration-conditional coverage follows a Beta law, and the probability of a shortfall can
be computed exactly [@Aguru2026]. The practical consequence is that a single estimate of
0.8996 against a target of 0.90 is not evidence of a bug, and a single estimate of 0.946 is
not evidence of a better method. Both are draws from a procedure whose average is fixed.

### 2.2 Split conformal

The construction has three stages. Fit f on a training set. Pass a disjoint calibration set
of size n through f and compute a nonconformity score s_i = s(X_i, Y_i) for each
calibration pair, where a larger score means the pair is less consistent with the model.
Sort the scores and take the k-th smallest, with k = ceil((n + 1)(1 − α)). For a new input
x, the prediction set is the collection of labels y whose score does not exceed q.

The index k is the part that is most often implemented incorrectly. The naive choice
ceil(n(1 − α)) gives a threshold that is too small, and the resulting coverage is below the
nominal level by a term of order 1/n. The choice ceil((n + 1)(1 − α)) costs one effective
calibration sample and buys a guarantee that holds for every n, not only in the limit. With
continuous scores, the coverage is exactly k/(n + 1), which exceeds 1 − α by at most
1/(n + 1) [@Vovk2005; @Lei2018]. The correction is not cosmetic. It is the difference
between a procedure with a finite-sample guarantee and a procedure with an asymptotic one.

The guarantee is a lower bound, and the upper bound is also informative. At n = 100 and
α = 0.10 the coverage is 91/101 = 0.901. At n = 10 it is 10/11 = 0.909. The absolute
difference is small, but it is the difference between a guarantee that is tight at the
nominal level and one that is visibly conservative. The calibration size is therefore a
design variable, not a nuisance. Section 5 varies it explicitly.

### 2.3 Scores and efficiency

Once the quantile is fixed, the only design freedom is the score. For classification, the
simplest choice is s(x, y) = 1 − p_y(x), which yields the set of labels whose predicted
probability exceeds a threshold. This is the least-ambiguous classifier of Sadinle et al.
[@Sadinle2019], and it is the score that split conformal reduces to when the threshold is
chosen on the calibration set. The score is global. A class that the model systematically
under-predicts is excluded more often than the nominal rate allows, and the marginal
coverage is restored only by compensation across classes.

Adaptive scores change the object being thresholded. The APS score accumulates probability
mass in descending order until the true label is reached, so the score depends on the rank
of the true label rather than on its absolute probability [@Romano2020]. The randomization
in the score is what restores exact validity in the presence of ties. The regularized
variant adds a penalty on the number of labels in the set and shrinks large sets at a small
cost in coverage [@RAPS]. For regression, the analogous choice is the absolute residual,
and the conformalized quantile regression of Romano et al. [@Romano2019CQR] uses a locally
adaptive residual.

Efficiency has no distribution-free optimum. There is no score that is uniformly smallest
across distributions, and the achievable set size depends on the model and on the data. A
better model produces smaller sets, and a worse model produces larger ones, but neither
changes the validity of the procedure. This is why the efficiency literature is a sequence
of score designs rather than a sequence of theorems, and why the choice of score is an
empirical question. It is also why the score determines the empty-set behavior that Section
4.2 measures. A score that can place every label above the threshold produces empty sets. A
score that cannot produces sets that are never empty. The validity guarantee is silent on
which case obtains.

### 2.4 Marginal and conditional coverage

Marginal coverage averages over the covariate distribution. Conditional coverage would
require P(Y in C(X) | X = x) ≥ 1 − α for almost every x. The second statement is much
stronger, and it is not attainable without assumptions. Barber et al. [@Barber2021] show
that no distribution-free procedure can guarantee pointwise conditional coverage with
non-trivial sets for all distributions. The intuition is that a finite calibration sample
contains finite information about any particular x, and a procedure that must be valid for
every distribution can always be confronted with a distribution that concentrates its mass
elsewhere. In classification, the only procedure that attains the target everywhere is the
trivial one that returns the entire label space.

The field's responses weaken the target rather than the impossibility. Group-conditional
coverage requires the guarantee to hold on average within each of a collection of groups.
When the groups are known in advance, Mondrian calibration attains it by calibrating
separately within each group [@Vovk2012]. The cost is a smaller effective calibration
sample per group and the requirement that the group label be available at test time. Local
weighting attains a smoother version of the target by assuming that the conditional
coverage function varies slowly in x, and randomization makes the local weights
identifiable [@Hore2024]. The assumption is explicit, and it is not verifiable from data
alone.

Class-conditional coverage is a group-conditional target, not a pointwise one. A
class-conditional coverage below the nominal level for the worst-served class is a
statement about a known group, and it is attainable with Mondrian calibration. It is not
evidence for or against the pointwise impossibility of Barber et al. Treating the two as
the same is a category error. The distinction matters for Section 5, where the
class-conditional deviations are large while the marginal coverage is nominal.

### 2.5 What the guarantee does not say

The guarantee does not say that the set is small. It does not say that coverage holds for
every subgroup. It does not say that the calibration set is representative of the deployment
distribution. It does not survive non-exchangeability without modification. It is a
statement about a procedure, not about a particular realized set, and it is a lower bound on
an average, not a promise about the next prediction.

These limits are not defects of the theory. They are the terms of the contract. The rest of
the paper is about what happens when the terms are forgotten. A reported coverage number is
the output of a pipeline that includes a score, a calibration set, a threshold rule, and a
post-processing rule. The guarantee constrains one of those objects. It does not constrain
the number that the pipeline prints.

## 3. A two-axis map

### 3.1 Why a map, not a chronology

A chronological account of conformal prediction is easy to write and hard to use. The field
did not develop in phases. The split construction, the adaptive score, the impossibility
result, and the risk-control extension were motivated by different problems, and several of
them overlap in time. A reader who memorizes the chronology learns a list of methods. A
reader who follows the guarantee learns where each method breaks.

The map in Table 1 has two axes. The rows are the guarantee a method pursues: marginal
coverage, group-conditional coverage, pointwise conditional coverage, and risk control. The
columns are the assumption it is willing to make: exchangeability, covariate shift,
non-exchangeability, and known groups. A method is located by the pair. A method that
claims a guarantee outside its column is mis-specified, and a method that is valid in one
column need not be valid in another.

The axes are not independent. Moving right weakens the data assumption. Moving down
strengthens the guarantee. The two directions compete: a stronger guarantee usually requires a stronger assumption, a larger set, or both. The empty cells are where the competition has not been resolved.

### 3.2 The rows

The first row is marginal coverage. The guarantee is P(Y in C(X)) ≥ 1 − α, averaged over the data distribution. It is the base case, and it is the only case that is attainable
without assumptions beyond exchangeability. The split construction of Vovk et al.
[@Vovk2005], the regression analysis of Lei et al. [@Lei2018], and the tutorial of
Angelopoulos and Bates [@Angelopoulos2021intro] all live here. The cost is one calibration
pass, and the score is free. The guarantee is weak in the sense that it says nothing about
any particular x. It is strong in the sense that it survives a badly misspecified model.

The second row is group-conditional coverage. The guarantee is that coverage holds on
average within each of a collection of groups. When the groups are known in advance,
Mondrian calibration attains it by calibrating separately within each group [@Vovk2012].
Gibbs et al. [@Gibbs2025] develop a framework for group-conditional coverage under weaker
assumptions, and the cost is the same in kind: a smaller effective calibration sample per
group, and the requirement that the group label be available at test time. The guarantee is
stronger than marginal coverage and weaker than pointwise coverage. It is the right target
when the deployment has a known partition, such as a demographic group or a class label.

The third row is pointwise conditional coverage. The guarantee is P(Y in C(X) | X = x) ≥
1 − α for almost every x. Barber et al. [@Barber2021] show that no distribution-free
procedure can attain it with non-trivial sets for all distributions. The constructive route
adds assumptions. Hore and Barber [@Hore2024] assume that the conditional coverage function
varies slowly in x, and they show that randomization makes the local weights identifiable.
The assumption is explicit, and it is not verifiable from data alone. The sets are larger
than the marginal ones, and the guarantee is conditional only up to the smoothness
constant.

The fourth row is risk control. The guarantee is E[L(C(X), Y)] ≤ r for a bounded loss L, of
which coverage is a special case. Bates et al. [@Bates2021] introduce the general
construction, and later work extends it to a grid of risk levels with multiplicity control
[@LTT] and to a cross-validated version that removes the data-splitting loss [@XVCrc]. The
assumption is a monotone loss and exchangeability. The cost is a grid search over the risk
level and a correction for the number of candidates. The guarantee is not a coverage
statement, and it does not reduce to one unless the loss is the indicator of a miss.

### 3.3 The columns

The first column is exchangeability. It is the base assumption, and every method in the first
column is valid under it. The column is not a statement about the data. It is a statement
about the procedure's tolerance. A calibration set drawn at random from the same
distribution as the test set satisfies it. A calibration set drawn from a different
distribution does not.

The second column is covariate shift. The guarantee is recovered by reweighting the
calibration scores according to the likelihood ratio between the test and calibration
covariate distributions [@Tibshirani2019]. The assumption is that the likelihood ratio is
known or estimable. When it is estimated, the estimation error propagates into the
guarantee, and the coverage is exact only if the ratio is exact. The column is therefore
narrower than it looks. It is not a distribution-free guarantee under arbitrary shift. It
is a guarantee under a shift that can be quantified.

The third column is non-exchangeability. The guarantee is weakened to a bound that depends
on a measure of the violation. Barber et al. [@Beyond] give a bound in terms of a
total-variation-like quantity, and Oliveira et al. [@Oliveira2022] study the split
construction under a known ordering. The bound is exact, but the quantity is not estimable
from data in most applications. The alternative is online adaptation. Gibbs and Candès
[@Gibbs2021ACI] update the target level after each observation, and the guarantee becomes
an average over time rather than a statement about each step. The distinction matters. A
per-step guarantee is not available without assumptions. An average guarantee is, and it is
what the adaptive methods provide.

The fourth column is known groups. The method is Mondrian calibration, and the guarantee is
group-conditional [@Vovk2012]. The assumption is that the group label is known at
calibration and at test time. The cost is a smaller effective sample per group, and the
guarantee is only as good as the group definition. A group that is defined by a variable
the model can see is easy. A group that is defined by a variable the model cannot see is
not.

### 3.4 The empty cells

The map has empty cells, and they are the point. Pointwise conditional coverage under
covariate shift is empty in the reviewed set. Pointwise conditional coverage under
non-exchangeability is empty. Group-conditional coverage under covariate shift and under
non-exchangeability is empty. Risk control under covariate shift is empty in the reviewed
set. These are not claims that no method can exist. They are claims that no method in the
reviewed set occupies the cell, and they are the open problems of Section 7.

The empty cells also explain why the field's arguments often talk past each other. A method
that is valid in the exchangeable column can be presented as if it were valid under shift,
and a reader who does not check the column will believe it. The map makes the check
explicit. It is the first question a practitioner should ask of a new method. Which cell
does it occupy, and what does it assume to get there?

### 3.5 What the map buys

The map buys three things. First, it makes the assumptions explicit. A method's guarantee is
a conditional statement, and the condition is the column. Second, it makes the costs
comparable. A group-conditional guarantee costs a smaller effective sample. A pointwise
guarantee costs an unverifiable smoothness assumption. A risk-control guarantee costs a
grid and a multiplicity correction. Third, it makes the empirical audit interpretable. A
reported coverage number is a property of a cell, not of a score. The same score can
produce 0.90 in one cell and 0.95 in another, and the difference is the post-processing, not
the guarantee.

Table 9 places the map against four existing surveys. The comparison is about coverage, not
quality. The map's contribution is the two-axis organization and the explicit empty cells.
The empirical contribution is the audit of whether the reported numbers respect the cell.
Neither is a substitute for the other.

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
| T1 | two-axis map: guarantee x assumption | paper/tables/table1_map.md |
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
| T9 | coverage against four surveys | paper/tables/table9_coverage.md |
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
