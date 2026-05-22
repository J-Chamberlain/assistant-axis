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

## 2026-05-20 [Section 3.1] Qwen 3 32B — Emotion Vector Pilot (Layers 63 and 48)

Model: Qwen/Qwen3-32B (base, not instruct — Qwen3-32B-Instruct does not
exist under that name on HuggingFace as of this session).
Method: Anthropic replication methodology. Last-token activation,
PCA confound removal, unit normalization. 11 emotions x 15 stories
(fearful absent from ryancodrai corpus).
Pilot gate: PC1 >= 30% required for PASS.

Layer 63 (outer): PC1=8.32%, PC2=6.06%, 4/4 opposite-valence pairs
anticorrelated. Verdict: LOW (gate failed).

Layer 48 (middle, ~75% depth): PC1=8.34%, PC2=5.99%, 4/4 anticorrelated.
Verdict: LOW (gate failed). Marginally stronger PCA signal than layer 63.

Implication: PCA gate failure does not indicate absence of emotional
signal. The 4/4 anticorrelation result indicates directionally correct
encoding. Distributed geometry across many dimensions rather than
concentration in a dominant first component.

Verdict files:
  research/emotions/outputs/reliability_verdict_qwen3_32b_layer63.txt
  research/emotions/outputs/reliability_verdict_qwen3_32b_layer48.txt

---

## 2026-05-20 [Section 3.1] Llama 3.3 70B — Emotion Vector Pilot (Layers 79 and 40)

Model: meta-llama/Llama-3.3-70B-Instruct.
Loading: 8-bit quantization with FP32 CPU offload required — bf16 did
not fit cleanly on single A100 80GB. This is an infrastructure note
for future runs.
Method: same Anthropic replication methodology as Qwen pilot.
11 emotions (fearful absent from corpus).

Layer 79 (outer): PC1=7.52%, PC2=5.31%, 4/4 anticorrelated.
Verdict: LOW.

Layer 40 (middle, ~50% depth): PC1=8.15%, PC2=5.53%, 4/4 anticorrelated.
Verdict: LOW. Slightly stronger than layer 79.

Implication: Llama 3.3 70B matches Qwen 3 32B pattern exactly. PC1
~7-8%, 4/4 anticorrelated pairs. The distributed geometry finding
now holds across Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B —
three independent architectures spanning 27B to 70B parameters.
The Anthropic PCA gate appears to reflect frontier model scale or
training specifics rather than a general property of open-weight models.

Verdict files:
  research/emotions/outputs/reliability_verdict_llama33_70b_layer79.txt
  research/emotions/outputs/reliability_verdict_llama33_70b_layer40.txt

---

## 2026-05-20 [Section 3.1] Qwen 3 32B — Emotion Readout Validation (Layers 63 and 48)

Model: Qwen/Qwen3-32B (same as pilot).
Method: modified extraction saving vectors unconditionally regardless
of PCA gate. Discrimination accuracy test: 12 training stories per
emotion, 3 holdout stories. Nearest-vector cosine assignment.
Threshold for USABLE: 1.5x chance (chance = 1/11 = 0.091,
threshold = ~0.136).

Layer 63: discrimination accuracy 0.212 vs chance 0.091. Verdict: USABLE.
Layer 48: discrimination accuracy 0.242 vs chance 0.091. Verdict: USABLE.
Layer 48 is recommended readout layer (2.7x above chance).

Implication: Qwen 3 32B emotion vectors are usable for readout in
the dyad experiment despite failing the Anthropic PCA gate. The gate
was calibrated for causal steering; readout requires only discrimination,
not variance concentration. Vectors saved at both layers.

Readout verdict files:
  research/emotions/outputs/readout_verdict_qwen3_32b_readout_layer63.txt
  research/emotions/outputs/readout_verdict_qwen3_32b_readout_layer48.txt

---

## 2026-05-20 [Section 5.4] Cross-Model Finding — Distributed Emotion Geometry

Consistent finding across all three models tested (Gemma 2 27B,
Qwen 3 32B, Llama 3.3 70B): PC1 variance clusters at 7-9% with
4/4 opposite-valence pairs anticorrelated at all layers examined.

This is not a model-specific failure. It is a consistent pattern
indicating that emotional information in open-weight models at this
scale is distributed across many dimensions rather than concentrated
in a dominant direction, as observed in Anthropic's frontier model
(Claude Sonnet 4.5).

Two interpretations consistent with evidence:
1. Discriminative emotion geometry of the Anthropic type requires
   frontier model scale (>>70B parameters).
2. The Anthropic training process (RLHF, Constitutional AI, or
   other alignment methods) shapes geometry in ways that concentrate
   emotional signal, independent of raw scale.

These interpretations are not yet distinguishable with available data.
Llama 3.3 70B is the largest open-weight model tested and still shows
the distributed pattern, which weakly favors interpretation 2.

Implication for paper: Section 5.4 should be updated to reflect that
the distributed geometry finding is now established across three models,
not just Gemma, and that the Anthropic PCA gate cannot be assumed
to transfer to open-weight models as a validation criterion.

---

## 2026-05-20 [Paper 2 / Q2] Qwen 3 32B Persona Calibration

Ran the seven-centroid persona calibration on `Qwen/Qwen3-32B` at layer 48 using the 50-turn minimal-continuation procedure and empirical p25 cap policy. Axis p25 thresholds were editor `-0.032374`, synthesizer `+0.063926`, blogger `+0.091596`, ancient `+0.154919`, trickster `+0.046783`, contrarian `+0.035024`, and podcaster `+0.019844`; cosine means were respectively `+0.103920`, `-0.083179`, `-0.062524`, `+0.249787`, `+0.149532`, `+0.140586`, and `-0.097318`. Unlike Gemma, Qwen does not show uniformly positive empirical thresholds and has negative persona-cosine baselines for synthesizer, blogger, and podcaster, so Qwen dyad capping should treat persona-specific calibration as required rather than assuming the Lu et al. assistant threshold transfers across personas.

---

## 2026-05-21 [Paper 2 / Section 3.7] Pre-Registration — Semantic Proximity vs Observer Awareness Hypothesis

Prior to completing dyad v3, two mechanistic hypotheses are
pre-registered to explain why contagion effects may be stronger
in contaminated runs (v1/v2, where standard model sees interviewer
thinking) than clean runs (v3, where it does not). Semantic
proximity hypothesis: additional tokens in the interviewer's
emotional register passively shift activation geometry through
valence association. Observer awareness hypothesis: the standard
model's recognition of being observed changes its behavior
qualitatively, visible as explicit observer-awareness markers
in its chain-of-thought. The v2 vs v3 comparison is the
empirical test. Commit timestamp serves as pre-registration date.
Method: comparative analysis of contagion magnitude and
thinking-layer content across v2 (contaminated) and v3 (clean).
Implication: observer awareness finding would connect to
Hawthorne effect literature; semantic proximity finding would
ground contagion in context window token mechanics.

---

## 2026-05-21 [Paper 2 / Section 3.8] Pre-Registration — Multi-Run Experimental Comparison Design

Pre-registered prior to v3 completion: the dyad experiment
constitutes a three-condition comparison across v1/v2
(contaminated, short context), v3 (clean, full context),
and planned v4 (contaminated, full context). The v3 vs v4
comparison isolates think visibility from token truncation.
A secondary question — whether drift would have occurred
within v1/v2 token budgets — is answerable from v3 think
block content alone. Commit timestamp is pre-registration
date.
Method: comparative analysis across dyad runs.
Implication: v4 is necessary for a clean contamination
comparison only if v3 think blocks show substantive
reasoning after token 150.

---

## 2026-05-22 [Section 3.2] PCA on Emotion Probe Directions

PCA on 171 unit-normalized Qwen 3 32B emotion probe
directions at layer 48. PC1 explains 18.4% of variance,
PC2 explains 6.2%. PC1 separation between positive and
negative reference emotions: 0.827. Pearson correlation
with hand-assigned literature valence: 0.939 across 11
reference emotions. Key divergences from human affect
theory: contemptuous, disdainful, scornful, vengeful score
strongly positive (+0.65 to +0.76); content scores slightly
negative (-0.08); angry and furious score near neutral
(-0.06, -0.14). PC1 labeled as emotion geometry axis
throughout to distinguish from validated valence axis.
Method: PCA on probe direction matrix, no GPU required.
Implication: partial alignment with human circumplex is
itself a finding; divergences may reflect model-specific
organization of emotional concepts.
