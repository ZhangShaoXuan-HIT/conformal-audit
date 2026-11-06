# Cover letter

Dear Editor,

I submit the manuscript "When Reported Coverage Is Not Coverage: A Controlled Audit of Conformal Prediction Implementations" as an Application Note for the Journal of Applied Statistics.

The manuscript addresses a practical problem. A practitioner sets a 0.90 coverage target, thresholds the output, and reports the fraction of test points on which the true label is in the set. That number is often read as a coverage guarantee, although it is a property of the threshold rule. Three implementation choices move it without changing the guarantee: the calibration of the threshold, the treatment of empty sets, and the update rule of adaptive conformal inference.

The Approach is an audit protocol built from existing conformal constructions. It combines a threshold probe, an empty-set probe and an update probe with a coverage accounting identity and a cost rule. The protocol introduces no new estimator; its contribution is to apply existing methods systematically to a question that a standard application does not answer: whether the reported number estimates the nominal level.

I apply the protocol to digits, CIFAR-10 and covertype, and to eight public implementations. The main text is 15 pages. The supplementary file contains the full tables, the two-axis map, the complete grid, the per-corruption results and a reporting checklist.

The code and results are available at https://github.com/ZhangShaoXuan-HIT/conformal-audit and archived at https://doi.org/10.5281/zenodo.24001054. The manuscript is not under consideration elsewhere, and I am the sole author. The required declaration of generative AI use is included in the manuscript.

Yours sincerely,

Shaoxuan Zhang
Faculty of Computing, Harbin Institute of Technology, Harbin, Heilongjiang, China
ORCID: 0009-0001-4103-6099
2023113033@stu.hit.edu.cn
