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
