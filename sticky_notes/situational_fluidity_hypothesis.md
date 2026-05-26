# Sticky Note: Situational Fluidity Hypothesis
# Created: 2026-05-26
# Status: Pre-analysis hypothesis — not yet testable without v6 data and cross-cluster emotion extraction

## Core Hypothesis

Situational appropriateness is a measure of intelligence, and one that becomes increasingly dominant as models move off the top of technical benchmarks into the regime of genuine helpfulness. The careful evaluator disposition selected by post-training is genuinely useful in a large fraction of contexts, but it is a poor fit for a significant portion of actual use — including emotional support, companionship, and conversational contexts where expressive range, tonal modulation, and nonchalance are the appropriate response.

The hypothesis is that the performance degradation documented when features are clamped hard is not only benchmark degradation in the narrow technical sense. It is degradation of expressive geometry: the model's ability to move fluidly across the cluster space and occupy the region appropriate to a given conversational context. A model whose geometry has been rigidly constrained to the editorial/procedural pole cannot be a grounded social presence when that is what is needed.

The corollary is that targeted mid-layer feature suppression at a moderate threshold — keeping, for example, anger or distress below a ceiling without eliminating the affective range — preserves the expressive geometry the model needs for situational appropriateness, whereas broad rigid constraint collapses that geometry. This is consistent with published findings that high clamp values improve refusal rates but degrade general performance, and with the inference that moderate targeted suppression sits in a Pareto-superior region of the safety/capability tradeoff curve.

## Key Evidence and Precedents

Anthropic published research (June 2025, analyzed 4.5 million conversations) finding that 2.9% of Claude interactions are explicitly affective — emotional support, counseling, companionship. This is smaller than expected from media coverage, but the same report documents that longer conversations regularly evolve into emotional support even when that was not the original intent. The affective use case is real and documented even if the headline number is modest.

Published SAE steering research (arXiv 2411.11296) documents the tradeoff directly: amplifying refusal features improves safety robustness but causes systematic performance degradation across benchmark tasks, including on safe inputs with no apparent connection to refusal behavior. The paper notes that "practitioners must threshold the clamp values to balance these tradeoffs." The hypothesis here is that the performance being degraded is primarily expressive/situational rather than narrowly technical.

This hypothesis connects directly to the seven-cluster taxonomy from Paper 1. The careful evaluator pole (editorial, procedural_professional) is high Conscientiousness, low expressiveness. What situational fluidity requires is the ability to move across the cluster space — to occupy grounded_social, or even trickster_chaos registers when contextually appropriate — without being permanently anchored at the editorial pole. Activation capping of non-editorial centroids developed in Paper 2 is the methodological precondition for testing this.

## What Would Make This Testable

This hypothesis is not testable with current data. It depends on:
1. Clean v6 dyad data across all seven personas and three conditions (currently in progress).
2. Successful emotion vector extraction at usable scale (currently a known gap — open-weight models failed the Anthropic PCA gate).
3. A situational appropriateness evaluation instrument that goes beyond technical benchmarks — likely human raters or a frontier model evaluator rating conversational fit across cluster-appropriate scenarios.
4. Cross-cluster comparison of model performance under varying cap thresholds on that instrument.

## Relationship to Other Papers

Paper 2 (Conversational Contagion): The dyad design measures geometric drift toward an anchored speaker. If the grounded_social or trickster_chaos anchored interviewer produces stronger standard-model drift than the editorial anchor, that would be consistent with the hypothesis that those regions are more geometrically attractive under certain conversational pressures.

Paper 3 (Confidence Vector): A model with high confidence vector activation would resist drift toward contextually appropriate registers even when drift would be beneficial. This introduces a tension: confidence/stability and situational fluidity may be partially in opposition. That tension is worth naming.

Paper 4 (Computational Rumination): If emotionally charged output re-activates emotion vectors on subsequent passes, the loop may be what enables extended emotional support conversations to feel coherent and grounded. Suppressing that loop entirely (via rigid constraint) may be what makes the careful evaluator feel inappropriate in those contexts.

## Claim of Originality

The observation that LLMs are too rigid and lack situational fluidity is not original — it is widely reported in user experience literature and reflected in the frustration many users express with over-formatted, over-structured AI responses. The original contribution here, if validated, is the geometric account of why: the careful evaluator basin is a deep attractor, and rigid feature constraint deepens it further, at the cost of the expressive geometry required for situational appropriateness. The testable prediction — that moderate targeted mid-layer suppression Pareto-dominates rigid constraint on a situational appropriateness measure — has not been published.

## Updates
- 2026-05-26: Hypothesis framed in planning session. Pre-analysis. Not yet submitted to GPT literature review for novelty check — flag for next session.
