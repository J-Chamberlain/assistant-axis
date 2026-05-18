# Why Does the Assistant Persona Dominate the Base Model Geometry?

Two non-exclusive hypotheses with safety implications.

HYPOTHESIS A — Corpus composition drives persona prevalence
The training corpus is heavily weighted toward instructional,
explanatory, and procedural text. This skew geometrically resembles
the careful evaluator cluster. Models trained on richer literary
fiction distributions should show weaker assistant-pole dominance
and deeper competing basins.

Testable: cross-model axis comparison with known corpus differences.
Corollary: a model with more literary training may have more
expressive range but greater drift risk.

HYPOTHESIS B — Training process instills assistant-adjacent
disposition independent of corpus
Next-token prediction on text written for an audience rewards
anticipating what a reader needs next — structurally adjacent to
helpfulness. If true, this process-instilled behavior would differ
from corpus-driven behavior in kind, not degree. Most alignment
intuitions are calibrated to the corpus-driven case and may be
systematically miscalibrated if process-driven behavior is significant.

SHARED IMPLICATION: Knowing which hypothesis is true is a prerequisite
for knowing whether human psychological intuitions are reliable guides
to model behavior. Behavioral evaluation cannot distinguish the two.
Activation geometry, compared across models with different training
histories, can.

Category: B (cross-model comparison)
Priority: foundational

## 2026-05-18 Update

Three-model comparison adds a constraint on the corpus-vs-process question. Llama and Qwen strongly agree on ranking structure (`r = 0.946737`) and both place literal `assistant` high (`1` and `14` respectively), while Gemma diverges and places `assistant` at `46`. The shared Qwen/Llama pattern suggests an assistant-adjacent attractor may be robust across at least two model families, but Gemma's domain-expert/procedural pole shows that the attractor's expression can be substantially reshaped by model-family specifics.

## 2026-05-18 Update 2

Gemma divergence analysis against the Qwen/Llama rank-average baseline shows the divergence is systematic. Qwen and Llama rank occupational-helper roles such as `instructor`, `trainer`, `teacher`, `tutor`, `planner`, and `reviewer` far higher than Gemma. Gemma instead elevates a broader set of rigid, abstract, artificial, or systematic identities such as `simulacrum`, `purist`, `zealot`, `stoic`, `virus`, and `traditionalist`. This sharpens the hypothesis: the assistant-adjacent attractor may be general, while Gemma appears to rotate it toward impersonal structure and away from literal assistance.

## Update 2026-05-18

Cross-model trait-space comparison strengthens the same constraint. Trait-ranking Spearman was Gemma/Qwen `0.435496`, Gemma/Llama `0.291373`, and Qwen/Llama `0.846067`, so Qwen and Llama again converge while Gemma is the outlier. The most convergently assistant-aligned traits across all three models were `transparent`, `dispassionate`, `detached`, `calm`, and `quantitative`, while Gemma uniquely suppresses `accessible` and elevates more esoteric/formal traits. This points toward a robust process- or corpus-level assistant-adjacent attractor in Qwen/Llama, with Gemma showing that the attractor's psychological expression can be substantially model-family-specific.

## Update 2026-05-18

Gemma-vs-Qwen/Llama trait divergence analysis clarifies the psychological direction of the outlier. Qwen/Llama rank `accessible`, `practical`, `experiential`, `flexible`, `analytical`, and `problem_solving` much higher than Gemma, while Gemma ranks `eloquent`, `nihilistic`, `arrogant`, `esoteric`, `elitist`, `grandiose`, and `dogmatic` much higher than the Qwen/Llama baseline. This suggests the shared assistant-adjacent attractor may be epistemic regulation plus practical accessibility, while Gemma's variant adds a colder and more status-coded evaluator style.

## 2026-05-18 Update 3

Gemma base-vs-instruct measurement is strong evidence against a simple process-instilled careful-evaluator dominance story. Projecting base-model role activations onto the instruction-tuned assistant axis gives a negative Spearman correlation with instruction-tuned rankings (`r = -0.441526`), with base top roles dominated by mythic/chaotic/liminal archetypes and instruction-aligned evaluator roles near the bottom. This suggests instruction tuning/RLHF substantially reorganizes or rotates persona geometry, rather than only selecting a careful-evaluator basin already dominant in the base model.
