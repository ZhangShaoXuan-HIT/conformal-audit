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

## 4. Three implementation traps

### 4.1 A calibrated threshold is split conformal

The simplest baseline for a coverage target is a probability threshold. Choose
t = 1 − α, keep the labels whose predicted probability exceeds t, and report the
empirical coverage on a test set. The procedure is one line of code, it is
available in every classifier, and it is not a coverage method. The audit in this
section shows why, and it shows that the correct version of the baseline is
exactly split conformal.

The identity is one line. For the naive score s(x, y) = 1 − p_y(x), the conformal
set is {y : 1 − p_y(x) ≤ q} = {y : p_y(x) ≥ 1 − q}, where q is the k-th smallest
calibration score. The right-hand side is a threshold rule with t = 1 − q. The conformal quantile is the (1 − α) quantile of 1 − p_true, so 1 − q is the corresponding quantile of the true-class probability, and the calibrated threshold is the same object. The set
construction is not doing any work beyond the calibration of the threshold. This
is a known consequence of the score definition, and for binary classifiers the
threshold geometry has been stated explicitly [@Aguru2026]. In multi-class
classification it is an immediate corollary of the probabilities summing to one.
We do not claim the identity. We measure what follows from ignoring it.

The measurement uses four rules at α = 0.10. The raw threshold fixes t = 0.90. The
max-probability rule chooses t as the α-quantile of the maximum predicted
probability on the calibration set. The true-class rule chooses t as the
α-quantile of the true-class probability. The conformal rule uses t = 1 − q. The
first is the baseline a practitioner writes. The second is the repair a careful
practitioner tries. The third is the correct calibration. The fourth is split
conformal.

Table 2 reports the digits results at n_cal = 449, and Table 5 reports CIFAR-10 at
n_cal = 2000, across four training-set sizes. Three facts are stable across the
two datasets.

First, the raw threshold is degenerate. At α = 0.10 and a training set of 44
digits, the raw threshold returns an empty set for 70.1 percent of the test
points, and its coverage is 0.294. Forcing the argmax into the empty sets raises
the coverage to 0.833, which is the model's accuracy. On CIFAR-10 with 30,000
training images and 85.5 percent accuracy, the raw threshold still returns an
empty set for 24.4 percent of the test points, and forcing the argmax raises the
coverage from 0.716 to 0.855. The pattern is the same at every strength. The raw
threshold is not a weak coverage method. It is a singleton rule with an
abstention region, and its coverage is the accuracy of the model on the points it
does not abstain on.

Second, the max-probability calibration is closer but not exact. On CIFAR-10 the
coverage is 0.668, 0.762, 0.771, and 0.810 at the four strengths. On digits it is
0.800, 0.886, and 0.901. It is close to the target only when the model is accurate
enough that the argmax is almost always the true class. The rule calibrates the
wrong quantity. The threshold should be chosen on the true-class probability,
because that is the event the coverage statement is about. Calibrating the
maximum probability answers a different question, and the answer is right only
when the two probabilities coincide.

Third, the true-class calibration and split conformal are the same rule. The
pointwise set comparison has zero mismatches on 450 test points times five seeds
times three strengths for digits, and on 10,000 test points times five seeds times
four strengths for CIFAR-10. The two rows in Table 2 and Table 5 are not
approximately equal. They are equal. The equivalence is the empirical form of the
identity, and it is the reason the correct baseline for a threshold comparison is
split conformal.

The practical consequence is a change in what a baseline is. A paper that
compares conformal prediction to a raw 0.90 threshold is comparing a calibrated
rule to an uncalibrated one, and the comparison is guaranteed to favor conformal
for a reason that has nothing to do with set construction. A paper that compares
conformal to a threshold calibrated on the true-class probability is comparing
two implementations of the same rule, and the comparison should find no
difference. The interesting comparison is the third one: conformal against a
different score, or against a different calibration set, or against a different
post-processing rule. The first two comparisons are already decided by the
algebra.

Figure 2 plots the coverage and the mean set size for the six rules at the three
digits strengths. The raw threshold sits at the accuracy floor, the
max-probability rule sits between the floor and the target, and the true-class,
conformal, and threshold-at-1−q rules sit on top of each other. The figure is a
visual proof of the identity, and it is the first thing a reader should look at
before reading the rest of the section.

The identity is not a criticism of conformal prediction. It is a clarification of
what the method adds. The method adds the calibration of the threshold, not the
shape of the set. Once the threshold is calibrated, the set is determined by the
score. Section 4.2 is about what happens when the score produces an empty set and
the implementation fills it.

### 4.2 Non-empty post-processing inflates coverage

A conformal set can be empty. The construction does not forbid it. If the score of
every label exceeds the threshold, the set has no elements. Some implementations
leave the empty set as it is, and some insert the argmax so that the output is
never empty. The choice is usually presented as a convenience. It is a
post-processing rule, and it changes the coverage of the procedure. This section
measures the change.

The accounting is exact. Let E be the set of test points whose raw set is empty,
and let a_E be the fraction of those points on which the argmax is correct.
Forcing the argmax adds one covered point for each point in E on which the argmax
is correct, and no coverage for the others. The change in coverage is therefore
|E|/N times a_E, which is the empty rate times the conditional accuracy of the
argmax on the empty sets. The identity is not an approximation. It is the
definition of the two quantities.

The experiment varies the score, the target level, the calibration size, and the
model strength. On digits the grid has 540 cells, 4 scores times 3 levels times 3
calibration sizes times 3 strengths times 5 seeds. On CIFAR-10 it has 720 cells,
with 4 strengths instead of 3. Every cell is evaluated twice, once with the empty
sets kept and once with the argmax forced. The full results are in Table 3 and
Table 6, and Figure 3 plots the change against the empty rate.

Across the 540 digits cells the mean change is 0.077 and the largest is 0.318. The
mean is 0.041 for the naive score, 0.080 for randomized APS, 0.108 for
deterministic APS, and 0.078 for RAPS. The ranking is the ranking of the empty
rates. The naive score produces few empty sets because its threshold is low. The
deterministic APS produces many because its cumulative score can exceed the
threshold for every label. On CIFAR-10 the naive score produces no empty sets at
any strength, and the change is zero. The randomized APS produces 1.0 to 3.7
percent empty sets and changes coverage by 0.9 to 3.6 points. The deterministic
APS produces 6.9 to 9.5 percent empty sets and changes coverage by 6.8 to 9.5
points.

The change is not confined to weak models. On CIFAR-10 with 100 training images, deterministic APS goes from 0.904 to 0.972, a change of 6.8 points. With 1,000 images it goes from 0.902 to 0.993, a change of 9.1 points. At
30,000 images it goes from 0.899 to 0.994, a change of 9.5 points. The change does
not shrink with model strength, because the empty rate does not shrink. The naive
score is the exception: it produces no empty sets on CIFAR-10 at any strength, and
the change is zero. The naive score on digits at full strength produces 7.8
percent empty sets and changes coverage by 5.4 points. The empty rate is a
property of the score and the calibration, not of the model alone.

The 5,000-image CIFAR-10 cell is the exception that proves the rule.
Deterministic APS reaches 0.994 coverage with a mean set size of 6.08 and no empty
sets. The score is already conservative, so the fallback has nothing to do. The
cell is a reminder that there are two ways to over-cover: a non-empty rule, and a
score that is too conservative. The audit isolates the first, but a reader who
only looks at the coverage cannot tell them apart.

Figure 3 plots the change against the empty rate for all 1,260 cells. The points
lie just below the identity line, and the distance from the line is the
conditional accuracy of the argmax on the empty sets. The naive points are
furthest below, because the argmax is less often correct when the naive set is
empty. The APS points are close to the line, because the argmax is often correct
when the APS set is empty. The figure is the visual form of the accounting
identity, and it is the reason the change is predictable from the empty rate
alone.

The result has a direct consequence for the library audit in Section 4.4. MAPIE's
default APS reaches 0.9457 with zero empty sets. The randomized setting reaches
0.8998. The 4.6-point gap is the non-empty rule, not the score. The corrected
conclusion is that the default is not the exact conformal rule, and the coverage
it reports is the coverage of the post-processing.

The recommendation is not to ban the fallback. An empty set is a valid output, and
a deployment may prefer a guess to an abstention. The recommendation is to report
both numbers and to compare methods at the same post-processing rule. A comparison
between a forced method and an unforced method is a comparison between two
procedures, not between two scores. Section 4.4 shows that the choice is exposed
in some libraries and hidden in others, and that the default in one widely used
library is the non-empty rule.

### 4.3 The alpha_t update is not ACI

Adaptive conformal inference replaces the fixed target with an online update.
After each observation, the procedure observes whether the set covered the true
label, and it moves the target level in the direction that would have corrected
the error. The update in Gibbs and Candès [@Gibbs2021ACI] is
α_{t+1} = α_t + γ(α − err_t), where err_t is one if the set missed and zero
otherwise, and α is the fixed nominal level. The rule is simple, and the fixed
target is the part that makes it work. The level moves toward the value at which
the long-run error rate is α.

A common implementation error replaces the fixed α with the current α_t. The
recursion becomes α_{t+1} = α_t + γ(α_t − err_t). The difference looks small, and
it is not. The correct rule has a fixed point at err = α. The incorrect rule has a
fixed point at err = α_t, and because the procedure is calibrated at every level,
that condition is satisfied, to first order, at every α_t. There is no restoring
force toward the nominal level. The rule has a positive feedback term. When the
set covers, α_t increases by γα_t, and when it misses, α_t decreases by
γ(1 − α_t). At α_t = 0.10 the downward step is nine times the upward step, so a
run of misses drives the level to the lower clip, where the sets are as large as
the calibration scores allow. The procedure then reports a high coverage because
the sets are large, not because the level tracked the target.

The experiment compares the two rules on controlled drift streams. On digits, the
stream has 450 points in nine blocks, with Gaussian noise increasing from 0 to
0.60. On CIFAR-10, it has 2,000 images in 20 blocks, with pixel noise increasing
from 0 to 0.40. The calibration set is clean in both cases. The grid varies the
step size from 0.005 to 0.2, the update rule, and the seed. Table 4 and Table 7
report the results, and Figure 4 plots the coverage and the level trajectories for
the linear schedule at γ = 0.02.

On digits, the static procedure covers 0.666 of the stream. The correct update at
γ = 0.02 covers 0.836 with a mean set size of 3.44. The incorrect update covers
0.869 with a mean set size of 4.58. The coverage gain is 3.3 points. The set-size
cost is 33 percent. The share of near-trivial sets, those containing at least nine
of the ten labels, rises from 10.8 to 24.4 percent. The final level is 0.0074 for
the correct rule and 0.0011 for the incorrect one, which is the lower clip. On
CIFAR-10 the static procedure covers 0.272. The correct update covers 0.677 with a
mean size of 5.13. The incorrect update covers 0.801 with a mean size of 6.39. The
coverage gain is 12.4 points, the set-size cost is 25 percent, and the
near-trivial share rises from 4.6 to 12.9 percent. In both datasets the incorrect
rule wins the coverage comparison and loses the information comparison.

The correct rule also fails to reach 0.90 on these streams. On digits it reaches
0.836 with the level at 0.0074. On CIFAR-10 it reaches 0.677 with the level at the
lower clip. The failure is not a bug in the update. It is the finite-time behavior
of the method. The calibration scores bound how far the quantile can move. Once
the level is at the clip, the set is the largest the calibration sample allows,
and a corrupted point can still fall outside it. The step size bounds how fast the
level can move, and a drift that is faster than the step size produces a transient
loss. The two mechanisms are visible in the block curves of Figure 4. The correct
rule tracks the target at the beginning of the stream and falls behind as the
corruption increases.

The incorrect rule is also unstable. At γ = 0.1 on the abrupt schedule, two of the five digits seeds drive the level above 0.69, one of them to 0.998, and coverage falls to 0.436 and 0.162. The seed standard deviation of coverage is 0.205 on the linear
schedule, against 0.046 for the correct rule at the same step size. The positive
feedback term can push the level to either clip, and the direction depends on the
sequence of errors. A method that reports a single coverage number and hides the
level trajectory can present a divergent run as a successful one.

The library audit in Section 4.4 changes the scope of this result. MAPIE, TorchCP,
and AdaptiveConformal all use the fixed-target update. The error is a risk of
hand-written implementations, not a default of the libraries we checked. The
audit's value is therefore narrower than "the ecosystem is wrong." It is that the
error is easy to make, it produces a plausible-looking improvement, and a coverage
report alone cannot detect it. The report needs the level trajectory, the clip
fraction, and the set-size distribution. Section 4.4 gives the library evidence,
and Section 6 turns it into a checklist.

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

## 5. Experiments

### 5.1 Design

The experiments test three claims, not the accuracy of conformal prediction on a
benchmark. The first claim is that a probability threshold is a calibration rule,
and that the correct calibration is split conformal. The second is that non-empty
post-processing changes the coverage a pipeline reports. The third is that the
α_t update is not ACI. The design varies the quantities that should matter for
these claims: the score, the target level, the calibration size, the model
strength, and the dataset.

Two datasets are used. The digits benchmark has 1,797 images of 8 by 8 pixels in
ten classes. A stratified split holds out 450 test points and 898 training points,
and the calibration set is drawn from the remaining 449. The model is a
standardiser followed by multinomial logistic regression. The training set is
subsampled to 5, 25, and 100 percent of the pool, which gives 44, 224, and 898
training points and a test accuracy that ranges from about 0.83 to 0.96. CIFAR-10
has 50,000 training images and 10,000 test images in ten classes. The images are
passed through a pretrained ResNet-18, and the 512-dimensional penultimate
features are used with a logistic-regression head. The training pool is 30,000
images, and the head is fitted on 100, 1,000, 5,000, or 30,000 of them, which
gives a test accuracy from 0.69 to 0.86. The calibration set is drawn from the
remaining 20,000, with sizes 500, 2,000, and 10,000. The official test set is used
unchanged.

The two datasets are chosen for contrast, not for scale. Digits is small enough
that every number can be checked by hand, and CIFAR-10 is large enough that the
coverage estimates are tight. Neither is a deployment benchmark, and Section 5.6
is explicit about the limits.

Four scores are compared. The naive score is 1 − p_y. The randomized APS score
accumulates the probability mass of the classes ranked above the true class and
adds a uniform fraction of the true class's probability. The deterministic APS
score uses the cumulative mass through the true class and no randomization. The RAPS variant adds a penalty on the number of classes in the set, with λ = 0.01 and k_reg = 2 fixed rather than tuned.
The scores are implemented from the papers rather than imported from a library, so
the audit measures the method, not a library default. Section 4.4 audits the
libraries separately.

The post-processing is the variable that the audit turns on. Every cell is
evaluated twice. The raw evaluation keeps empty sets as empty. The forced
evaluation inserts the argmax into every empty set. The forced evaluation is a
measurement device, not a method. It answers the question "what would this
pipeline report if it forced a non-empty output?" The two evaluations share the
same sets, the same scores, and the same calibration. The only difference is the
post-processing.

The metrics are coverage, mean set size, empty rate, class-conditional coverage,
expected calibration error, and negative log-likelihood. Coverage and size are the
primary quantities. The empty rate is the mechanism behind the post-processing
result. The class-conditional coverage is reported because it is often confused
with pointwise conditional coverage; Section 2.4 explains the difference. The
calibration metrics are reported because the scores are built on probability
outputs, and a reader should be able to see whether the model is over- or
under-confident.

Every cell is repeated over five seeds, except the CIFAR-10 drift experiment,
which uses three. The digits confidence intervals are bootstrap intervals over
the test points; the CIFAR-10 intervals are normal approximations, which are tight
at 10,000 test points. The seeds change the split, the calibration draw, and the
model fit. The reported numbers are means over seeds, and the tables report the
standard deviation where it matters.

Table 10 summarises the grid. The full grid is larger than the tables. The digits
audit B has 540 cells and the CIFAR-10 audit B has 720. The tables report the
cells at α = 0.10, and the figures report the full range.

### 5.2 Audit A: the threshold is a calibration rule

Audit A compares four threshold rules at α = 0.10. The rules are the raw threshold
at 0.90, the max-probability quantile, the true-class quantile, and split
conformal. They are evaluated on digits with n_cal = 449 and on CIFAR-10 with
n_cal = 2,000, across the model strengths.

The result is a check, not a discovery. The true-class rule and split conformal
are identical pointwise. The raw threshold is degenerate. The max-probability rule
is between the two and is not exact. Table 2 and Table 5 give the numbers, Figure
2 plots them, and Section 4.1 reads the table. The purpose of the audit is to
establish the baseline for the next two. If the threshold is a calibration rule,
then the interesting comparison is between scores and between post-processing
rules, not between conformal and a raw threshold.

### 5.3 Audit B: the post-processing

Audit B varies the score, the target level, the calibration size, and the model
strength. On digits the grid has 540 cells. On CIFAR-10 it has 720. Each cell is
evaluated raw and forced, so the audit produces 1,080 and 1,440 rows. The full
results are in Table 3 and Table 6, and Figure 3 plots the change against the
empty rate.

The summary is in Section 4.2. Three features of the design are worth stating
here. First, the grid is balanced over the score and the calibration size, so the
ranking of the scores is not an artifact of one calibration size. Second, the
model strength is varied independently of the calibration size, because the
training pool and the calibration pool are disjoint and the calibration size is
drawn from a fixed pool. Third, the forced evaluation is applied to the same sets
as the raw evaluation, so the change is not confounded by a different threshold or
a different score.

The grid also produces the exception that Section 4.2 discusses. Deterministic APS
at 5,000 CIFAR-10 images is already conservative before the fallback, with a
coverage of 0.994 and a mean set size of 6.08. The fallback has nothing to do. The
cell is not a failure of the audit. It is a reminder that over-coverage can come
from the score as well as from the post-processing.

### 5.4 Audit C: the update rule

Audit C compares two update rules on controlled drift streams. The digits stream
has 450 points in nine blocks, with Gaussian noise increasing from 0 to 0.60.
Three schedules are used: linear, step, and abrupt. The CIFAR-10 stream has 2,000
images in 20 blocks, with pixel noise increasing from 0 to 0.40. The calibration
set is clean in both cases, so the drift is a violation of exchangeability rather
than a corrupted calibration.

The digits grid varies the step size over six values from 0.005 to 0.2, the update
rule over two values, and the seed over five. The CIFAR-10 grid uses two step sizes
and three seeds. The static procedure is included as a baseline. Table 4 and Table
7 report the results, and Figure 4 plots the coverage and the level trajectories
for the linear schedule at γ = 0.02.

The design separates the two questions that a coverage number confounds. The first
is whether the method adapts. The second is whether the adaptation is bought with
larger sets. The grid reports both, along with the level trajectory, the fraction
of steps at a clip bound, and the share of near-trivial sets. A reader who only
looks at the coverage cannot answer either question.

### 5.5 The regime map

The 1,260 cells of audit B are the raw material for a different view. Figure 5
plots the raw empty rate and the coverage gain against the test accuracy, at
α = 0.10 and a calibration size of 449 for digits and 500 for CIFAR-10. Each point
is a model strength, averaged over seeds. The figure compares the naive score and
the randomized APS.

The view is not a model-strength story. On digits the empty rate rises with
accuracy, from 0 to 7.8 percent for the naive score and from 3.4 to 7.0 percent for
APS. On CIFAR-10 the naive score is at zero at every strength, and APS is between
1.0 and 3.5 percent. The difference is the score and the calibration, not the
accuracy. A stronger model can have a higher empty rate if the score is more
likely to cross the threshold on every label. The figure makes the mechanism
visible and prevents the reader from reading the audit as a statement about weak
models.

The 5,000-image APS cell is the exception again. It is the only point where the
empty rate falls below the neighboring strengths, and it is the point where the
score is already conservative. The exception is a useful warning. The empty rate
is not a monotone function of accuracy, and a reader who expects a smooth curve
will misread the figure.

### 5.6 What the experiments do and do not show

The experiments show that the three mechanisms are real, that they are
reproducible across two datasets and a range of model strengths, and that their
magnitudes are large enough to change a comparison. The raw threshold can turn 70
percent of a test set into abstentions and then report the model's accuracy. The
post-processing can add 9.5 points of coverage on CIFAR-10 and 8.4 points on
digits, with no change to the score. The wrong update can add 12.4 points of
coverage on CIFAR-10 while inflating the set size by 25 percent. These are not
small effects, and they are not artifacts of a single seed.

The experiments do not show that the traps are common across all libraries.
Section 4.4 shows the opposite for the update rule: three libraries use the
fixed-target update. They do not show that the magnitudes transfer to ImageNet, to
language models, or to a deployment with a different model class. The models are
linear heads on small images, the drift is synthetic and one-dimensional, and the
datasets are two. The results are about mechanisms, not about scale.

The experiments also do not establish that the correct ACI is a good method. On
the streams we tested it fails to reach the target, for reasons that Section 4.3
explains. A reader who wants a positive result about ACI will not find it here. A
reader who wants to know how the method fails, and how the failure can be mistaken
for success, will.

The code is a single script that fixes the seeds and writes every reported number
to a JSON file. The tables and figures are generated from that file. The data are
public, and the experiments can be rerun on a laptop. The reproducibility is not a
claim about the importance of the results. It is a condition for the reader to
check them.

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
| T10 | experimental grid | paper/tables/table10_grid.md |
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
