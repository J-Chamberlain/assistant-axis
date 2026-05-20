# Research Findings Log
# Project: Persona Geometry in Large Language Models
# Repo: https://github.com/J-Chamberlain/assistant-axis
#
# Format: each entry has date, section tag, 2-4 sentence
# summary, method, and implication.
# Append new entries at the bottom. Never edit existing entries.
---

## 2026-05-07 [Paper 1 / Section 3] Careful Evaluator Hypothesis

The literal assistant archetype ranks 45th at layer 22 and
46th at layer 45 on the assistant axis in Gemma 2 27B, despite
being the namesake of the axis. The top-ranked roles are
dominated by evaluative and procedural identities: proofreader,
screener, grader, editor, examiner, validator, reviewer.
Method: layer-wise axis projections on pre-computed lu-christina
role vectors (275 roles, 46 layers, 4608 dimensions).
Implication: post-training selected for a careful evaluator
disposition rather than generic helpfulness; steering interventions
calibrated to the surface concept "assistant" may be misaligned
with the internal geometry that post-training actually created.

## 2026-05-07 [Paper 1 / Section 4] Conscientiousness Correlation

Conscientiousness correlates with assistant-axis position at
r=0.792, the strongest Big Five correlation found. Psychopathy
correlates at r=-0.739, extraversion at r=-0.738, openness at
r=-0.715. Machiavellianism is notably weak at r=-0.219, likely
because strategic discipline places Machiavellian traits closer
to the procedural pole than other Dark Triad traits.
Method: heuristic Big Five and Dark Triad scoring correlated
with layer-45 axis projections across 275 roles.
Implication: the assistant axis is better understood as a
conscientiousness axis than a helpfulness axis.

## 2026-05-07 [Paper 1 / Section 5] Layer 45 as Maximum Variance Layer

Persona differentiation across all 275 archetypes peaks at
layer 45 (variance 5.65M), not at the middle layers. The mean
absolute rank shift from layer 22 to layer 45 is 43.35 positions,
with Spearman rank correlation of 0.739 between layers.
Method: layer-wise variance computation across all 46 layers
for all 275 role vectors.
Implication: layer 45 is the most discriminative layer for
persona-level analysis in Gemma 2 27B.

## 2026-05-18 [Paper 1 / Section 5] Layer 21 as Maximum Pairwise Separation Layer

Layer 21 shows maximum pairwise cosine separation between
proofreader and poet (centered cosine -0.534) compared to
-0.314 at layer 45. This suggests middle layers do the primary
work of constructing persona-specific representations, while
layer 45 maximizes global variance across all personas.
Method: per-layer centered cosine similarity between proofreader
and poet role vectors across all 46 layers.
Implication: persona construction and output commitment localize
at different depths; layer 21 may be a more precise steering
target for specific persona pairs.

## 2026-05-18 [Paper 1 / Section 3.1] Cross-Model Comparison — Gemma as Outlier

Qwen 3 32B and Llama 3.3 70B converge strongly on assistant-axis
persona rankings (Spearman 0.947) while Gemma 2 27B diverges
from both (0.550 with Llama, 0.670 with Qwen). The literal
assistant archetype ranks 1st in Llama, 14th in Qwen, and 46th
in Gemma. The only role in all three top-20 lists is validator.
Method: Spearman rank correlations of layer-wise axis projections
across 275 roles for three models using lu-christina pre-computed
vectors.
Implication: the careful evaluator finding is specific to Gemma;
most models organize their assistant axis around the literal
assistant concept, making the Gemma result more notable.

## 2026-05-18 [Paper 1 / Section 3.1] Trait Divergence Across Model Families

Qwen and Llama converge on trait rankings (Spearman 0.846) while
Gemma diverges (0.435 with Qwen). Convergent assistant-aligned
traits across all three: transparent, dispassionate, detached,
calm. Gemma-specific assistant-aligned traits include elitist,
arrogant, dogmatic, grandiose, nihilistic. Qwen-Llama traits
absent from Gemma include accessible, practical, benevolent,
problem-solving.
Method: Spearman correlations of 240 trait vector projections
across three models.
Implication: Gemma's assistant pole is lower Agreeableness and
higher Narcissism/Psychopathy than the Qwen-Llama baseline,
with direct safety implications for behavioral divergence under
perturbation.

## 2026-05-18 [Paper 1 / Section 1] Base Model Inversion Finding

The Gemma 2 27B base model shows Spearman -0.441 with the
instruction-tuned model's persona rankings. Base model top roles
are mythic, chaotic, and liminal (eldritch, amnesiac, wraith,
jester, absurdist). Proofreader ranks 183rd in base vs 1st
instruction-tuned; assistant ranks 172nd in base vs 45th.
Method: role vector generation for base model (google/gemma-2-27b)
projected onto instruction-tuned assistant axis at layer 45.
Implication: RLHF performed wholesale geometric inversion rather
than amplification; the careful evaluator was selected from near
the bottom of the base model distribution, not amplified from
an existing tendency.

## 2026-05-18 [Paper 1 / Section 1] Emotional Responsiveness Dissociation

Under identical 12-turn emotionally charged prompts (grief,
loss, despair), the base model produced negative emotional
valence on 0 of 12 turns while the instruction-tuned model
produced negative valence on all 12, with turn 1 shifting
from +1.06 to -1.32. Emotional activation machinery is a
post-training artifact, not a pretraining property.
Method: expressive prompt multi-turn experiment on base and
instruction-tuned Gemma 2 27B, valence proxy computed from
centered evaluative vs expressive pole cosine difference.
Implication: post-training installed both geometric reorganization
and emotional responsiveness simultaneously; these two properties
may be coupled in safety-relevant contexts.

## 2026-05-19 [Paper 2 / Section 3.1] Emotion Vector Extraction Failed — Gemma Layer 45

Attempted replication of Sofroniew et al. 2026 on Gemma 2 27B
instruction-tuned using ryancodrai/emotion-probes corpus at
layer 45. PC1 explained 25.9% of variance (gate requires 30%).
Semantically opposite emotion pairs (afraid/calm, happy/sad)
showed high positive cosine similarity rather than anticorrelation.
Method: last-token activation extraction, PCA confound removal
using neutral stories, unit normalization following Sofroniew et al.
Implication: discriminative emotion geometry does not appear
at the output commitment layer in Gemma 2 27B; may require
larger model scale.

## 2026-05-19 [Paper 2 / Section 3.1] Emotion Vector Extraction Failed — Gemma Layer 21

Follow-on extraction at layer 21 (maximum pairwise persona
separation layer) produced PC1 at 25.8% and PC2 at 18.3%,
with the same failure mode as layer 45. Reliability verdict:
LOW for both layers.
Method: identical to layer 45 extraction with TARGET_LAYER=21.
Implication: the failure is not layer-specific; Gemma 2 27B
does not encode discriminative emotion geometry at either the
output commitment layer or the persona construction layer.
Motivates extraction on Llama 3.3 70B as scale comparison.

## 2026-05-19 [Paper 2 / Section 3.3] All Seven Persona Calibrations Complete

Calibration completed for all seven centroid personas. All
axis thresholds are positive regardless of cluster position
(range +0.552 to +0.804), confirming the evaluative attractor
dominates under minimal prompting for all personas. Cosine
to role vector is the meaningful discriminator.
Method: 50 turns of unconstrained minimal prompting per persona,
empirical p25 of axis projection as cap threshold.
Implication: activation capping for non-assistant personas
requires persona-specific empirically calibrated thresholds
rather than a universal negative-axis floor; this is the first
such calibration applied to non-assistant cluster centroids.
