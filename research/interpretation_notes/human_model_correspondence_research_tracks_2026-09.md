# Human/Model Correspondence Research Tracks

Date: 2026-09-13  
Thread: AA-11  
Artifact status: active  
Purpose: preserve three distinct research tracks for continuity and scope control. Only Track 1 is active; Tracks 2 and 3 are deliberately parked.

## Scientific context

Existing analyses have established substantial cross-model convergence in persona geometry across Qwen 3 32B, LLaMA 3.3 70B, and Gemma 2 27B. The current interpretation is that these models exhibit recurring low-dimensional organization of role-conditioned behavior, while exact principal-component ordering and orientation remain model-local. This motivates—but does not establish—the hypothesis that recurring model geometry may reflect durable statistical structure in human behavioral descriptions rather than arbitrary model-specific geometry. The human-data program is intended to test whether independently derived human survey structure provides evidence consistent with that hypothesis.

## Track 1 — Independent profile-group correspondence

**Status: ACTIVE**

Independently derive behavioral-profile groupings in (A) human survey data and (B) model persona data, then test whether the independently derived groups show recognizable multivariate correspondence.

Do not begin by forcing the human data into Qwen PC1/PC2/PC3 categories. Derive groups statistically within each domain and compare their profile structures afterward. The intended unit of comparison is a behavioral profile or cluster centroid, not an isolated named trait.

The following design questions remain explicitly unresolved: how to select human respondents or items under SAPA planned missingness; what common human/model feature representation to use; which clustering method and distance metric to freeze; whether to reuse existing model persona clusters or recompute them in the common feature space; how many clusters to permit rather than impose; and how to evaluate correspondence statistically.

The number of human clusters need not equal the number of model clusters. The 275 model roles are not a population sample, so model-cluster prevalence must not be compared directly with human-population prevalence.

This is the only active correspondence track after AA-11.

## Track 2 — PC-pole profile correspondence

**Status: PARKED**

Use already established model geometry to define relatively pure neighborhoods around the positive and negative poles of PC1, PC2, and PC3; characterize the stable multivariate behavioral signatures of those neighborhoods; then test whether comparable human survey profiles occur.

The preserved methodological idea is to prefer relatively pure pole neighborhoods—for example, a strong target-PC position without simultaneous extremity on the other major PCs—rather than merely selecting the few most extreme personas. The intended evidence is a multivariate behavioral signature, not one-to-one trait-name matching.

This track is recorded only. It is not operationalized or developed in AA-11.

## Track 3 — Trait-relationship structural correspondence

**Status: PARKED**

Compare the relational structure among behavioral variables across humans and models. Conceptually: if human respondents who endorse behavioral tendency A also tend to endorse B and oppose C, does the model represent A, B, and C with a corresponding relational organization?

This track could eventually use item-by-item covariance or similarity matrices and could be substantially label-blind. It is distinct from clustering people or personas and from matching PC-pole profiles.

This track is recorded only. It is not operationalized or developed in AA-11.

## Cross-track compatibility principle

Where practical, all three tracks should eventually use the same frozen human/model feature representation, or **common feature space**, so their results can be compared cleanly.

AA-11 does not choose that representation. It does not decide among 126 constructs, 696 SAPA items, an item subset, model traits, derived behavioral dimensions, imputed human profiles, or another representation. Constructing the shared feature/profile representation is the immediate methodological question for Track 1 and belongs to subsequent work.

## Epistemic status

- **Observed:** Cross-model persona-geometry convergence has already been established in existing analyses.
- **Interpretation:** Persona geometry appears constrained rather than arbitrary across these models.
- **Hypothesis:** Recurring model geometry may reflect durable statistical organization in human behavioral variation or human-generated behavioral language.
- **Unknown:** Whether corresponding latent organization occurs in human respondent data; whether human and model dimensions are homologous; the causal origin of cross-model convergence; and generalization to other model families, architectures, scales, languages, or training regimes.

## AA-11 scope boundary

AA-11 is a planning and continuity task only. It performs no human-respondent analysis or scoring, clustering, candidate/respondent or SAPA-item selection, IRT/FIML, imputation, human-to-model projection, model PCA or trait-specificity rerun, semantic matching, model inference, activation extraction, external model API call, GPU/RunPod work, statistical-threshold selection, full Track 1 experiment design, finding, or new scientific claim.
