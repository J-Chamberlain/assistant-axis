# Auxiliary diagnostic implementation correction

Date: 2026-09-13
Stage: after the pre-fit methodology commit; before the numerical/profile freeze
Semantic status: item-ID blind

The first item-ID-only run exposed floating-point overflow and nonconvergence in the auxiliary dense logistic diagnostic because answered-item count (0–311) was combined directly with response proportions (0–1). This is an implementation defect in an auxiliary diagnostic, not evidence about K or item content.

Before freezing any numerical result, dense classifier columns are now centered and scaled using discovery-split means and standard deviations, then the frozen L2, `C=1`, `lbfgs`, class-balanced logistic model is fit. Scaling parameters are learned from discovery rows only. The sparse 696-column binary administration-mask model remains in its natural 0/1 units.

This correction does not change the categorical latent-class likelihood, missing-value treatment, candidate K range, seeds, starts, EM settings, eligibility rules, profile alignment, numerical model-selection rules, class probabilities, anonymous profile values, or semantic blinding. The complete analysis is rerun from raw SAPA data before the numerical/profile freeze.
