# When Reported Coverage Is Not Coverage: A Controlled Audit of Conformal Prediction Implementations

::: {.author}
Shaoxuan Zhang

Faculty of Computing, Harbin Institute of Technology, Harbin, Heilongjiang, China

ORCID: 0009-0001-4103-6099

Corresponding author: 2023113033@stu.hit.edu.cn
:::

**Abstract.** A conformal predictor comes with a finite-sample coverage guarantee. The number a pipeline reports does not. We present an audit protocol for three implementation choices between the guarantee and the reported number: the calibration of the threshold, the treatment of empty sets, and the update rule of adaptive conformal inference. The protocol composes existing conformal constructions with a coverage accounting identity and a cost rule for the empty-set fallback. We apply it to digits, CIFAR-10 and covertype, and to eight public implementations. A fixed probability threshold is not a coverage method; a true-class threshold is exactly split conformal; forcing the argmax into empty sets raises the reported coverage by up to 9.7 points on the image benchmarks, while a tabular benchmark shows the effect is near zero when the empty rate is near zero; the common alpha_t update is not ACI and reports higher coverage by inflating sets. Three of the eight libraries use the correct fixed-target update.

**Keywords.** conformal prediction; coverage; calibration; post-processing; adaptive conformal inference; implementation audit.

## 1. Introduction

### 1.1 The data challenge

A practitioner sets a 0.90 coverage target. The simplest way to meet it is to threshold the softmax at 0.90, keep the labels above the threshold, and report the fraction of test points on which the true label is in the set. The reported number is usually close to the model's accuracy, and it is often presented as evidence that the pipeline is calibrated. It is not. The threshold is a fixed probability, not a calibrated quantile, and the set it produces is a singleton or empty. The number is a property of the threshold rule, not of the guarantee.

The conformal alternative replaces the fixed threshold with a quantile of the calibration scores. The resulting set satisfies a finite-sample coverage guarantee under exchangeability [@Vovk2005; @Angelopoulos2021intro]. The guarantee is real. It is also a statement about the procedure, not about the number a particular pipeline prints. Between the procedure and the number sit at least three choices: how the threshold is calibrated, what the implementation does with an empty set, and how an adaptive method updates its target. Each choice can move the reported coverage without changing the guarantee. The resulting data challenge is practical: a deployment that compares methods, or that decides whether to abstain, cannot tell from the printed number whether the guarantee is doing any work.

### 1.2 Relevant data

We study the challenge on three public datasets. Digits is small enough to check by hand. CIFAR-10 is large enough that the coverage estimates are tight. Covertype is a tabular benchmark that tests whether the mechanism survives a different modality. We vary the score, the target level, the calibration size and the model strength, and we evaluate every cell twice, once with the empty sets kept and once with the argmax forced. The image grid has 1,260 cells; the tabular replication adds 180 rows. We also run eight public implementations on a common synthetic task. The data, code and every table are available at https://github.com/ZhangShaoXuan-HIT/conformal-audit and archived at https://doi.org/10.5281/zenodo.24001054.

### 1.3 Approach and contributions

The approach is an audit protocol, not a new estimator. It uses existing conformal constructions as probes. The first probe asks which threshold is calibrated. The second asks what the implementation does when the set is empty. The third asks whether an adaptive method updates a fixed target or its own current target. The protocol returns coverage, set size, empty rate, the conditional accuracy of the inserted label, and a cost rule for the fallback. This is an innovative use of existing methods: the object of study is the implementation, and the output is a decision, not a new predictor.

The paper makes four contributions. First, the protocol: three probes and an accounting identity that separate the score from the post-processing. Second, an empirical audit on three datasets and 1,260 image cells. Third, a library policy map over eight implementations, five of which were run. Fourth, a cost rule that turns the empty-set decision into a comparison of two losses. The audit complements four surveys and tutorials [@Angelopoulos2021intro; @Fontana2023; @Campos2024; @Zhou2025] and the closest 2025-2026 work [@Aguru2026; @Mehrtens2025; @Gauthier2025; @Bataineh2026; @Boman2026]. It does not claim the threshold identity as new; it measures what follows from using the wrong threshold, the wrong post-processing, or the wrong update.

## 2. Methodology/Approach

### 2.1 The audit protocol

A conformal pipeline has three stages: fit a model f, calibrate a quantile q on held-out data, and form the set C(x) = {y : s(x,y) <= q}. The protocol probes each stage with a counterfactual that a practitioner might plausibly use.

Probe 1, threshold calibration. We compare four rules: a raw threshold at 0.90, a quantile of the maximum probability, a quantile of the true-class probability, and split conformal with the naive score. The first returns a singleton or an empty set. The second is a quantile of the wrong quantity. The third is exactly split conformal: for the naive score s(x,y) = 1 - p_y, the true-class threshold t satisfies p_y >= 1 - q, which is the conformal set. We verify the identity pointwise, not only in coverage.

Probe 2, empty-set post-processing. We keep the raw set and the forced set, where forcing inserts the argmax only when the raw set is empty. Let e be the empty rate and a_E the fraction of empty-set points on which the argmax is correct. Forcing adds one covered point for each empty point on which the argmax is correct, so the coverage gain is exactly delta = e a_E. The identity is not an approximation. It also gives a cost rule. Let c_a be the loss of abstaining and c_e the loss of a wrong answer. Forcing is better than abstaining exactly when c_e (1 - a_E) < c_a, or c_a / c_e > 1 - a_E. The audit estimates a_E as delta / e.

Probe 3, adaptive conformal inference. The published update is alpha_{t+1} = alpha_t + gamma (alpha - err_t), where err_t is one if the set missed. The fixed target alpha is what creates a restoring force. A common implementation replaces it with the current level, alpha_{t+1} = alpha_t + gamma (alpha_t - err_t). The replacement removes the restoring force and adds a positive feedback term. We compare the static procedure, the correct update and the incorrect update on controlled streams, and we report coverage, set size, the share of near-trivial sets containing at least nine of the ten labels, and the final level.

Figure 1 shows the pipeline and the three probes. The protocol is the methodological contribution. It does not require a new score or a new estimator; it requires that the implementation be treated as the object of study, and that the reported number be decomposed into the quantities that produce it.

### 2.2 Data and experimental grid

Digits has 1,797 images of 8 by 8 pixels in ten classes. A stratified split holds out 450 test points and 898 training points; the calibration set is drawn from the remaining 449. The model is a standardiser followed by multinomial logistic regression. The training set is subsampled to 5, 25 and 100 percent, giving 44, 224 and 898 training points. CIFAR-10 has 50,000 training and 10,000 test images. A pretrained ResNet-18 provides 512-dimensional features; a logistic-regression head is fitted on 100, 1,000, 5,000 or 30,000 images. The calibration set is drawn from the remaining 20,000, with sizes 500, 2,000 and 10,000. Covertype is a 581,012-row, 54-feature, seven-class tabular dataset. We use a 120,000-row stratified subset, a logistic regression, training sizes of 6,000 and 60,000, a calibration set of 20,000 and a test set of 40,000.

Four scores are compared: the naive score 1 - p_y, randomized APS, deterministic APS, and RAPS. The grid varies the score, the target level (0.05, 0.10, 0.20), the calibration size and the model strength. Audit A uses alpha = 0.10 and the four threshold rules. Audit B uses the full score-by-level-by-calibration-by-strength grid: 540 digits cells and 720 CIFAR-10 cells, each evaluated raw and forced. Audit C uses controlled drift streams. The digits stream has 450 points in nine blocks, with Gaussian noise increasing from 0 to 0.60; the CIFAR-10 stream has 3,000 images in three blocks, one for each severity of a corruption type, across five corruption types. Seeds are five for audits A and B, three for the CIFAR-10 drift stream.

The grid is also the simulation study. It varies the factors that should matter, and it includes regimes in which the effect should be large and regimes in which it should vanish. The tabular replication is the stress test: a different modality, a different model and a different empty rate.

### 2.3 Implementations

We inspect eight implementations: MAPIE 1.6.0, TorchCP 1.2.1, puncc 0.9.3, crepes 0.9.1, coverforest 0.0.3, nonconformist 2.1.0, conformal 0.1 and the AdaptiveConformal R package. All eight were read at the source level. MAPIE, puncc, crepes, nonconformist and conformal were run on a common synthetic five-class task; MAPIE was run with five seeds, the others with one. TorchCP, coverforest and AdaptiveConformal were read only. The sample includes two older, smaller packages on purpose; it is a sample of public implementations, not a census.

### 2.4 Metrics and the cost rule

For each cell we record coverage, mean set size, the raw empty rate, the share of near-trivial sets, class coverage, expected calibration error and negative log-likelihood. For each raw/forced pair we record delta = coverage_forced - coverage_raw and a_E = delta / e. The cost rule is the threshold c_a / c_e = 1 - a_E. A deployment that reports both numbers can apply the rule; a deployment that reports only coverage cannot.

## 3. Application of the Methodology

### 3.1 Threshold calibration

On digits with 44 training points, the raw 0.90 threshold returns an empty set for 70.1 percent of the test points and covers 0.294; forcing the argmax raises coverage to 0.833, which is the model's accuracy. The max-probability rule reaches 0.668. The true-class rule reaches 0.800 and has no empty sets. At 898 training points the raw threshold covers 0.855 with 14.0 percent empty; the max-probability rule reaches 0.771; the true-class rule reaches 0.901. At a calibration size of 449, the true-class rule and split conformal coincide at 0.919, and the pointwise set comparison has zero mismatches over 450 test points times five seeds times three strengths.

On CIFAR-10 with 30,000 training images, the raw threshold returns an empty set for 24.4 percent of the test points even though the model is 85.5 percent accurate; its coverage is 0.716 and forcing the argmax raises it to 0.855. The max-probability rule reaches 0.810 at a target of 0.90. The true-class rule and split conformal agree pointwise over 10,000 test points times five seeds times four strengths.

Table 1 summarises the threshold results. The first finding is therefore simple and uncomfortable: a fixed probability threshold is not a coverage method, and the number it reports is accuracy on the points on which the model does not abstain. A quantile of the maximum probability is not a repair. The only correct calibration of the naive score is a quantile of the true-class probability.

### 3.2 Empty-set post-processing

On digits, across the 540 cells, the mean coverage gain from forcing is 0.077 and the largest is 0.318. The mean is 0.041 for the naive score, 0.080 for randomized APS, 0.108 for deterministic APS and 0.078 for RAPS. The ranking is the ranking of the empty rates: the naive score produces few empty sets, deterministic APS produces many. On CIFAR-10 the naive score produces no empty sets at any strength. Randomized APS produces 1.0 to 3.7 percent empty sets and changes coverage by 0.9 to 3.6 points. Deterministic APS produces 6.9 to 9.5 percent empty sets and changes coverage by 6.8 to 9.5 points. The 5,000-image APS cell is the exception: it is already conservative at 0.994 coverage and a mean size of 6.08, so the fallback has nothing to do.

The accounting identity explains the pattern. The gain is the empty rate times the conditional accuracy of the argmax on the empty sets. The conditional accuracy is high, between 0.94 and 0.99, because the model is usually right even when the set is empty. The empty rate is the mediator. On covertype the mean empty rate is 0.3 percent and the gain is 0.0 to 0.4 points; the same post-processing is nearly invisible.

The library audit shows the same mechanism in released code. MAPIE's APS default inserts the last label that crosses the quantile, so it never returns an empty set; over five seeds it reaches 0.9457 with zero empty sets, against 0.8998 for the randomized rule, a 4.6-point gap. puncc's APS with randomization off reaches 0.977 with no empty sets; with randomization on it reaches 0.889. The LAC implementations of MAPIE, puncc and crepes agree to three decimals at 0.895 and a mean size of 2.87, which is a consistency check on the audit. nonconformist and conformal also return no empty sets on the common task.

Table 2 summarises the library behaviour. The second finding is that the empty-set policy is a decision, not a detail. It changes the reported coverage by several points when the empty rate is high, and by almost nothing when it is low. The empty rate is the diagnostic.

### 3.3 Adaptive conformal inference

On digits, the static procedure covers 0.666 of the stream. The correct update at gamma = 0.02 covers 0.836 with a mean size of 3.44. The incorrect update covers 0.869 with a mean size of 4.58. The gain is 3.3 points; the size cost is 33 percent; the share of near-trivial sets rises from 10.8 to 24.4 percent. The final level is 0.0074 for the correct rule and 0.0011 for the incorrect one, which is the lower clip. At gamma = 0.1, two of the five digits seeds drive the level above 0.69, one of them to 0.998, and coverage falls to 0.436 and 0.162.

On CIFAR-10 with five corruption types and three severities, the static procedure covers 0.451. The correct update covers 0.828 with a mean size of 4.93. The incorrect update covers 0.936 with a mean size of 6.97. The gain is 10.8 points; the size cost is 41 percent; the near-trivial share rises from 14.5 to 38.0 percent. The block coverage of the correct rule is 0.853, 0.829 and 0.802 at the three severities; the incorrect rule is 0.940, 0.939 and 0.928. The correct rule does not reach 0.90. The incorrect rule does, by inflating the sets.

Table 3 summarises the update results. The third finding is that the incorrect update is not a harmless variant. It removes the fixed target that creates the restoring force, drives the level to a clip, and reports a higher coverage because the sets are larger. Three of the eight implementations (MAPIE, TorchCP and AdaptiveConformal) use the correct fixed-target update; the others do not implement ACI. The correct rule also fails to reach the target on these streams; the failure is finite-time behaviour and calibration support, not a bug. A reader who wants a positive result about ACI will not find it here. A reader who wants to know how the method fails, and how the failure can be mistaken for success, will.

### 3.4 The cost rule

The audit also supplies the quantity that a deployment needs. On digits the mean a_E is 0.99, so the threshold c_a / c_e is 0.01. On CIFAR-10 it is 0.96 to 0.99, so the threshold is 0.01 to 0.04. On covertype it is 0.94, so the threshold is 0.06. Forcing is better than abstaining unless abstaining costs less than one to six percent of an error. The defaults are therefore rational for most deployments; the problem is that the decision is made silently and that the reported coverage no longer estimates the nominal level.

Table 4 gives the cost threshold. A per-point version of the rule, using the model's maximum probability as a proxy for a_E, coincides with uniform forcing at or above c_a / c_e = 0.05 on all three datasets. The proxy does not improve on the population rule. The audit supports the average rule, not a per-point heuristic.

### 3.5 Simulation and the boundary

Figure 2, Figure 3 and Figure 4 show the threshold, forcing and update results. The 1,260 image cells are the simulation component: they hold the data fixed and vary the score, the target level, the calibration size and the model strength. The effect is not a model-strength story: a stronger model can have a higher empty rate if the score is more likely to cross the threshold on every label. The grid shows that the ranking of the scores is the ranking of the empty rates, and that the forced evaluation can reverse the ranking of two methods that differ only in their post-processing.

The covertype replication is the boundary. At alpha = 0.10 the empty rate is 0.0 to 0.4 percent and the forcing gain is 0.0 to 0.4 points. The identity holds; the magnitude is governed by the empty rate. This is what the protocol predicts, not a failure of the protocol. A method that reports a large gain on images and a near-zero gain on a well-calibrated tabular model is not inconsistent; it is telling the deployment where the exposure is.

## 4. Conclusion and Discussion

The guarantee constrains the procedure, not the number that the pipeline prints. The audit protocol separates the number into three choices, and the three choices have different signatures. The threshold probe shows that a fixed probability threshold is not a coverage method and that the true-class threshold is split conformal. The empty-set probe shows that the reported coverage can be raised by several points without changing the score, and that the gain is the empty rate times the conditional accuracy of the inserted label. The update probe shows that the common alpha_t recursion is not ACI, and that it can report a higher coverage by inflating the sets. The library audit shows that these are not hypothetical: a widely used default over-covers by 4.6 points, and a second library's randomization switch changes coverage by 8.8 points.

The practical recommendation is a reporting rule. Report raw and forced coverage, the empty rate, the conditional accuracy of the inserted label, and the set size. Report the cost ratio at which the fallback is optimal. Make the non-empty rule an explicit option; the default should be the exact rule that carries the guarantee. A pipeline that reports only coverage cannot be checked.

The limitations are those of an audit, not a benchmark. The datasets are three, the models are linear heads on small images and a tabular benchmark, and the drift is synthetic on digits and a corruption family on CIFAR-10. The library sample is eight implementations, not a census. The audit does not prove a theorem about finite-time ACI; it measures the behaviour of the implementations we tested. The covertype boundary is a reminder that the magnitude is regime-dependent. The protocol is the contribution; the numbers are evidence for it.

Three extensions would strengthen the work: a larger library census, a theoretical bound on the finite-time gap of ACI, and a deployment study that uses the cost rule with real costs. The first is engineering, the second is theory, the third is field work. The audit is a condition for all three: it makes the reported number visible enough to be studied.

## Acknowledgments

The author thanks the maintainers of the audited libraries for public code and documentation.

## Declaration of interest

The author reports no competing interests to declare.

## Funding

This research received no specific grant from any funding agency.

## Declaration of generative AI use

The author used a generative AI assistant (DeepSeek) for code development, data analysis, and drafting/editing of the manuscript. The author verified all results, analyses, and references and takes full responsibility for the content.

## CRediT authorship contribution statement

Shaoxuan Zhang: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing - original draft, Writing - review & editing, Visualization.

## Data availability statement

The code, results and tables are available at https://github.com/ZhangShaoXuan-HIT/conformal-audit and archived at https://doi.org/10.5281/zenodo.24001054.

## Supplementary material

The supplementary file contains the full tables, the two-axis map, the complete experimental grid, the per-corruption results and the checklist. The main text reports the cells needed for the argument.

## References

<!-- REFERENCES -->

## Tables

### Table 1. Threshold calibration

| dataset | training | rule | coverage | empty |
|---|---|---|---|---|
| digits | 44 | raw 0.90 | 0.294 | 0.701 |
| digits | 44 | max-probability | 0.668 | 0.086 |
| digits | 44 | true-class | 0.800 | 0.000 |
| digits | 898 | raw 0.90 | 0.855 | 0.140 |
| digits | 898 | max-probability | 0.771 | 0.008 |
| digits | 898 | true-class | 0.901 | 0.000 |
| CIFAR-10 | 30,000 | raw 0.90 | 0.716 | 0.244 |
| CIFAR-10 | 30,000 | max-probability | 0.810 | 0.000 |
| CIFAR-10 | 30,000 | true-class | 0.899 | 0.000 |

The true-class rule and split conformal are identical pointwise. The raw threshold is a singleton or empty; its coverage is accuracy on non-abstentions.

### Table 2. Library behaviour

| implementation | setting | coverage | empty | size |
|---|---|---|---|---|
| MAPIE | APS default | 0.9457 | 0.0000 | 3.68 |
| MAPIE | APS randomized | 0.8998 | 0.0004 | 3.23 |
| puncc | APS randomization off | 0.977 | 0.000 | 4.06 |
| puncc | APS randomization on | 0.889 | 0.002 | 2.98 |
| crepes | LAC | 0.895 | 0.000 | 2.87 |
| nonconformist | ICP margin | 0.890 | 0.000 | 3.50 |
| conformal | per-label thresholds | 0.890 | 0.000 | 3.02 |

MAPIE rows are five seeds; the other rows are one seed on the common synthetic task. The LAC implementations of MAPIE, puncc and crepes agree at 0.895 and a size of 2.87.

### Table 3. ACI update

| dataset | update | coverage | size | near-trivial | alpha final |
|---|---|---|---|---|---|
| digits | static | 0.666 | — | — | — |
| digits | correct | 0.836 | 3.44 | 0.108 | 0.0074 |
| digits | incorrect | 0.869 | 4.58 | 0.244 | 0.0011 |
| CIFAR-10 | static | 0.451 | 1.30 | 0.000 | — |
| CIFAR-10 | correct | 0.828 | 4.93 | 0.145 | 0.0106 |
| CIFAR-10 | incorrect | 0.936 | 6.97 | 0.380 | 0.0019 |

The incorrect update reports more coverage at a larger size and a larger near-trivial share. The correct update also falls short of 0.90.

### Table 4. Cost rule

| dataset | mean a_E | threshold c_a / c_e |
|---|---|---|
| digits | 0.99 | 0.01 |
| CIFAR-10 | 0.96 to 0.99 | 0.01 to 0.04 |
| covertype | 0.94 | 0.06 |

Forcing is better than abstaining when c_a / c_e exceeds 1 - a_E. The threshold is small in every dataset; the empty rate determines the exposure.

## Figures

<!-- FIGURES -->

## Figure captions

**Figure 1.** The three stages (solid) and the reporting step (dashed), with the three places where the reported number can move.

**Figure 2.** Coverage and set size versus the threshold on digits.

**Figure 3.** Change in coverage versus the raw empty rate across the image cells.

**Figure 4.** Coverage and level trajectories under drift on digits.
