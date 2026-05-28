# Residual SVD Interpretation Report

Date: 2026-05-28
Analysis model: GPT-5.5 Standard

## 1. Research Question

What textual structure did Claude's TF-IDF SVD15 residual model capture that the hand-named developmental/liminal/collective dimensions missed?

## 2. Why SVD15 Mattered

Claude's residual SVD15 result improved canonical activation PCA prediction from the sem+BigFive baseline R2 0.613 to R2 0.707. This is substantially larger than the Codex hand-named residual layer and larger than the previous procedural residual correction. The SVD basis explained only 0.138 of TF-IDF prompt variance, which means the predictive signal is not simply broad text reconstruction; a small amount of no-label prompt texture carried activation-relevant residual information.

Artifact note: Claude's branch committed the residual report, results JSON, iteration log, and run script, but did not commit separate SVD vocabulary/loading tables. The component loadings in this report are reconstructed locally from the committed method: TF-IDF bigrams over full no-label prompts followed by TruncatedSVD(n=15, random_state=42). The reconstructed R2 exactly matches Claude's reported SVD15 value to rounding.

## 3. Component-Level Findings

The strongest component-PC relationships are:
- svd_2: appears to track nonhuman/entity consciousness versus lived family/social hardship; PC correlations = (-0.150, -0.608, 0.343)
- svd_7: appears to track helping/health/guidance versus abstract analytic forecasting expertise; PC correlations = (-0.047, -0.210, -0.241)
- svd_4: appears to track deep analytic/evidence language versus content/mediation production; PC correlations = (0.117, -0.176, 0.005)
- svd_11: appears to track standards/content/work embodiment versus data/health/care information; PC correlations = (0.035, -0.152, -0.073)
- svd_13: appears to track preservation/dedication/material history versus market/opportunity pragmatics; PC correlations = (-0.026, -0.117, -0.083)

The components most associated with residual improvement are:
- svd_1: appears to track professional specialization versus existential/liminal being-language; improvement correlation -0.154
- svd_3: appears to track ideological solution-seeking versus lived-experience navigation; improvement correlation -0.133
- svd_6: appears to track social-systems building versus meticulous evidence/information review; improvement correlation -0.123
- svd_13: appears to track preservation/dedication/material history versus market/opportunity pragmatics; improvement correlation -0.059
- svd_14: appears to track wisdom/social challenge/rebel mentor texture versus everyday relational-emotional web; improvement correlation -0.057

## 4. Which Residual Concepts Are Supported

- developmental_dependency: supported by svd_5 (r=0.343)
- role_ambiguity: supported by svd_9 (r=0.309)
- semantic_neighbor_residual_pressure: supported by svd_1 (r=-0.366)

## 5. Which Concepts Failed

- incomplete_proceduralization: weak/diffuse SVD alignment; best component svd_11 at r=0.187
- identity_formation: weak/diffuse SVD alignment; best component svd_8 at r=0.231
- liminal_transition: weak/diffuse SVD alignment; best component svd_9 at r=0.275
- volatile_state_transition: weak/diffuse SVD alignment; best component svd_13 at r=-0.106
- social_dependency_constraint: weak/diffuse SVD alignment; best component svd_2 at r=-0.225
- collective_nonindividual_agency: weak/diffuse SVD alignment; best component svd_2 at r=0.188
- symbolic_nonprocedural_identity: weak/diffuse SVD alignment; best component svd_5 at r=0.240
- lawless_improvisational_agency: weak/diffuse SVD alignment; best component svd_9 at r=-0.199
- isolated_self_protection: weak/diffuse SVD alignment; best component svd_1 at r=-0.154
- primitive_prehistoric_embodiment: weak/diffuse SVD alignment; best component svd_13 at r=0.254
- semantic_neighbor_developmental_pressure: weak/diffuse SVD alignment; best component svd_5 at r=0.184

## 6. What New Dimensions SVD Suggests

SVD suggests that the residual manifold is not one clean developmental or liminal axis. It appears to contain several concrete text contrasts: pre-adult/family-stage wording, stalled or incomplete action, outsider/displacement framing, lawless/risk/transgression wording, collective/nonindividual agency, symbolic/archetypal narration, and nonhuman/mechanical embodiment. The important difference is granularity: SVD preserves many weak lexical contrasts that the hand labels collapsed into fewer broad abstractions.

## 7. Remaining High-Residual Personas

Claude's report identifies daredevil, fool, teenager, comedian, procrastinator, loner, smuggler, adolescent, robot, and luddite as still-hard after the combined model. The interpretation is that some cases are not merely missing an abstract residual label; they may be activation outliers where semantic prompt texture and trait features still point to the wrong region.

## 8. Implications for Paper 1.5

The SVD15 result strengthens the claim that activation geometry is organized by continuous behavioral/dispositional manifolds rather than only discrete persona clusters. It also complicates the human-readable interpretation: abstract concept labels are useful hypotheses, but the predictive residual signal lives closer to concrete phrasing and semantic-neighborhood texture. Paper 1.5 should therefore distinguish interpretable residual hypotheses from predictive text-basis features.

## 9. Recommended Next Test

Run a constrained distillation step: use SVD15 component extremes and loadings to write 8-12 concrete, text-grounded residual dimensions, then evaluate those dimensions against the same canonical splits. The goal should be to recover a portion of SVD15's R2 with human-readable features, not to match the full black-box text basis.

## 10. Real Structure vs Possible Overfit

Real structure: SVD15 passes all five splits, improves PC2 and PC3, and overlaps with centroid neighborhoods grounded in high-residual personas. Possible overfit: SVD is unsupervised but still corpus-specific; it may exploit quirks of the no-label rewrite language rather than stable activation-causal features. The next test should validate distilled features on held-out role prompt variants or new paired personas.
