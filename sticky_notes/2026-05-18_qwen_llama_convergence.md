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
