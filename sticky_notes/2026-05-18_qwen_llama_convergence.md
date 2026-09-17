# Qwen-Llama Convergence Hypothesis

Three-model comparison (Gemma, Qwen, Llama) found:
- Qwen-Llama Spearman: 0.947 (role rankings)
- Qwen-Llama Spearman: 0.846 (trait rankings)
- Gemma diverges from both at 0.550-0.670

HYPOTHESIS: Qwen and Llama converge because of shared training data lineage, GPU-constrained training reducing corpus diversity in Chinese labs, or distillation from common sources including possibly GPT outputs.

Evidence consistent with hypothesis:
- Chinese AI labs operate under US GPU export controls since 2022, constraining large-scale original pretraining
- Early Chinese models including some Qwen versions were documented to have used GPT outputs for instruction tuning
- The Qwen-Llama convergence is stronger in trait space than role space, suggesting deep structural similarity

IMPORTANT FRAMING NOTE: In the write-up, state this as hypothesis not claim. We cannot verify training data composition directly. The honest framing is: the convergence is empirically strong and consistent with shared lineage, but the geometric tools available cannot distinguish the cause.

RELATIONSHIP TO LANGUAGE EXPERIMENT: The Mandarin experiment (Paper 3) will be more informative than corpus speculation. If Qwen's geometry shifts substantially under Mandarin prompting despite high English-prompted similarity to Llama, that suggests Chinese training data is present but less dominant than assumed.

Paper: 3 (cross-cultural)
Priority: medium — framing note for write-up
Status: hypothesis, not confirmed

## Update 2026-05-18

The write-up now incorporates the trait divergence framing directly into Section 3.1 and Section 9. It states the Qwen/Llama convergence as empirical geometry, frames possible shared lineage or corpus explanations as open hypotheses, and adds the safety implication that superficially similar assistant behavior can hide different internal assistant-pole trait structures.

## Update 2026-09-11 — Extended PCA Score Recurrence

The full-rank persona PCA audit adds a different, role-label-aligned recurrence result. Qwen PC4 best matches Llama PC3 at absolute Pearson 0.690, PC5 matches Llama PC5 at 0.688, and PC6 matches Llama PC6 at 0.505; the corresponding best Gemma matches are PC4, PC5, and PC8 at 0.628, 0.651, and 0.570. All best-match statistics exceed 1,000 search-adjusted role-label shuffles at empirical p=0.001. Top-4/top-5/top-6 score-subspace mean canonical correlations are 0.908/0.891/0.888 for Qwen-Llama and 0.877/0.911/0.817 for Qwen-Gemma.

This strengthens the observed statement that related role-score structure recurs across the three saved vector sets, including beyond the original 3D display. It does not strengthen the lineage hypothesis directly: all models use the same English role labels/instructions, which can itself contribute to recurrence, and the hidden activation bases differ. Continue to label training-data lineage, distillation, corpus composition, and cross-cultural explanations as hypotheses rather than findings.

## Update 2026-09-12 — Held-Out PC1-PC6 Alignment and Trait-Direction Recurrence

AA-7 fits orthogonal Procrustes transforms to training-role PC1-PC6 scores and evaluates held-out roles. Mean coordinate correlations are 0.879 Llama→Qwen, 0.809 Gemma→Qwen, and 0.908 Gemma→Llama; all exceed 1,000 role-label permutations at p=0.001. After alignment, 11/12 frozen human-supported activation-derived trait directions recur highly and one moderately; all five strict Big Five directions recur highly. Agreeableness aligns at pairwise cosines 0.900/0.952/0.938 despite its different local-PC assignments.

This strengthens the observed cross-model role-space recurrence result but still does not identify its cause. Common English role instructions remain a plausible source, activation scales and residuals remain model-specific, and the result supplies no direct evidence for shared training lineage, human/model equivalence, or causal psychology. AA-7's separate compact human-selection test is weak/absent.

## Update 2026-09-17 — AA-17 persona trait factors

The saved 275 × 240 persona–trait cosine profiles pass the AA-17 matrix gate. A shrinkage exploratory factor analysis recovers 5/6/6 provisional Qwen/Llama/Gemma factors. Qwen F3 and Llama F2 have absolute Tucker congruence 0.919, and both align with Gemma F6 at 0.930/0.915 after sign matching. Other factors are only partly shared: Qwen–Llama weakest shared-subspace canonical correlation is 0.818, while the full Llama–Gemma six-dimensional comparison falls to 0.490. This confirms one strong model-only co-expression pattern but does not explain shared training lineage or establish a general Qwen–Llama identity. Source: `research/outputs/aa17_three_model_trait_factor/three_model_trait_factor_report.md`.
## Update 2026-09-17 — AA-18 three-model consensus

The exact 275-persona × 240-trait saved cosine matrices yield 220 named traits with minimum pairwise persona-profile Pearson r≥0.50 across Qwen/Llama/Gemma. Frozen regularized multiview analysis supports five individually stable all-three score/loading axes within 13 provisional score directions (decision A); later axes have weaker loading agreement. The AA-17 grounded/spiritual factor splits chiefly across C1/C2, and the Llama/Gemma cooperative-optimism pattern has an all-three shared portion. This strengthens model-only convergence over shared labels and prompts, but does not distinguish common training lineage, extraction effects, or independent psychology. Source: `research/outputs/aa18_three_model_consensus_trait_structure/three_model_consensus_trait_report.md`.

## Update 2026-09-17 — AA-19 independent human structure

The frozen Qwen/Llama/Gemma consensus axes were compared with independently fitted SAPA human proxy factors. Human/model trait-covariance agreement is positive (three-model consensus upper-triangle r=0.531, 500-label p=0.002), but transfer is selective: C3 meets the primary five-factor independent-support rule but its individual human-factor match weakens under six factors, C1 maps to a human-factor combination, C2 partially transfers, and C4/C5 lack adequate direct future-safe bridge coverage. This bears on structural convergence but still cannot identify shared training lineage or causal mechanisms. Source: `research/outputs/aa19_human_consensus_factor_validation/three_model_human_validation_report.md`.

## Update 2026-09-17 — AA-20 HiFWB gate

The adequately bridged human C1–C3 representations associate with SAPA HiFWB, but jointly add only +.005 held-out R2 beyond the Big Five (paired bootstrap 95% CI [-.006,+.018]). This closes the requested model-persona projection gate for now: shared model–human trait organization does not yet supply reliable incremental wellbeing prediction. Source: `research/outputs/aa20_consensus_axes_hifwb/aa20_consensus_axes_hifwb_report.md`.
