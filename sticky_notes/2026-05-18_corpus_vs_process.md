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
