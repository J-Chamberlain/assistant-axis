# Machine in the Loop — Iterative Motivational Hypothesis Testing
Date: 2026-05-28
Status: concept, pre-design

## Core Idea

An iterative interpretive loop in which a frontier model (GPT-5.5 or equivalent) generates
natural-language motivational hypotheses about what animates geometric regions of the
activation space, those hypotheses are tested against per-persona geometric placement,
the residuals reveal where the hypothesis fails, and the model uses those failures to
generate a revised hypothesis. The loop continues until the hypothesis achieves stable
predictive accuracy across the persona corpus.

## What Is Being Learned

Not a weight matrix. An interpretive theory: a natural language account of what motivational
structure causes the model to place certain personas in certain geometric regions. The test
of the theory is geometric prediction accuracy. The feedback is which personas the theory
mislabels. The revision is a refined natural language characterization of the animating
principle.

## Why "Machine in the Loop"

An inversion of the standard human-in-the-loop framing. Here the machine performs the
interpretive work that is usually reserved for humans. The loop structure is what gives
the interpretation scientific grounding rather than making it an ungrounded assertion.
The researcher designs the loop and evaluates convergence; the machine generates and
revises the theories.

## Methodological Distinctiveness

Each iteration produces a hypothesis, a test result, and a revision. That record is
auditable and publishable as a methodology, not just the final result. The iterative
process itself is the contribution: a systematic procedure for grounding natural-language
interpretations of activation geometry in geometric prediction accuracy.

## Connection to Existing Work

Depends on per-persona semantic-activation residuals (sticky note:
2026-05-28_semantic_activation_residuals.md). The residuals provide the feedback signal
for each iteration. The motivational cluster characterizations developed in Paper 1.5
dialogue sessions are the initial hypothesis set from which the loop begins.

## Paired Persona Design (Related)

A specific application of this loop is the paired persona test: hold one variable constant,
vary another, measure the geometric displacement. Examples developed so far:

- Situationally displaced homeless person vs psychiatrically homeless person: same surface
  condition, different causal structure. Hypothesis: separates on grounded-social vs
  other/dysregulated axis.

- Vulnerable narcissist vs grandiose narcissist: same trait label, different motivational
  and emotional architecture. Hypothesis: separates on shame-organized vs
  dominance-organized axis, approximately other/dysregulated vs combative-iconoclast.

- Reactive by circumstance by choice vs reactive by circumstance by necessity (e.g.
  expatriate vs refugee): same situatedness, different agency structure. Hypothesis:
  separates on an agency-within-circumstance dimension not visible in semantic space.

Each pair is a controlled experiment isolating one dimension of activation space. The
axis of displacement between the two personas in the geometry identifies that dimension.

## Open Questions

- What is the right convergence criterion for the iterative loop?
- How many iterations are needed before a hypothesis stabilizes?
- Does the loop converge to the same hypothesis from different starting points?
- Can the loop recover the seven-cluster taxonomy without being initialized with it?
- Is the resulting theory human-interpretable or does it drift toward opaque descriptions?

## Status

Concept only. Depends on: per-persona residuals (complete), PCA projection mode in
visualizer (in progress), and a loop execution design (not yet written).

## Update 2026-05-28

Implemented the first offline latent-feature discovery loop at `research/q2_stability/qwen/scripts/latent_feature_discovery_loop.py`. The concept has moved from pre-design to an initial constrained framework: GPT-5.5-derived candidate dimensions are operationalized as measurable features and evaluated on a deterministic 200/75 visible-heldout split. First-pass evidence is bounded: latent features improve held-out assistant-axis R2 from 0.301 to 0.385 at best, but do not improve activation-cluster accuracy over the semantic baseline.

## Update 2026-05-28

Implemented the second-stage framing ablation at `research/q2_stability/qwen/scripts/latent_feature_framing_ablation.py`. The ablation compares motivational, interactional, procedural, narrative-causal, all-framing, and prior first-loop feature sets on held-out PCA3D prediction. The best result is the prior first-loop feature set at R2 0.436 versus semantic baseline R2 0.322; among new framings, all framings combined performs best at R2 0.405 and procedural is the best single family at R2 0.373.

## Update 2026-05-28

Implemented the first full iterative outer-loop harness at `research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py`. The loop evaluates candidate latent dimensions across five deterministic splits, retains or discards dimensions based on gain, stability, null, and complexity checks, and stops on plateau. Final retained features reached mean PCA3D R2 0.492 versus semantic baseline 0.389, then plateaued after two failed refinement rounds.

## Update 2026-05-28

Implemented the first residual-focused third-layer diagnostic at `research/q2_stability/qwen/scripts/residual_manifold_analysis.py`. After the hierarchical trait-plus-procedural model reached R2 0.622, the residual loop used full no-label prompts, semantic-neighborhood residual pressure, and constrained developmental/liminal/collective candidate dimensions to reach R2 0.632. This is a concrete example of the machine-in-the-loop method: residual failures generated the next bounded hypothesis set, which was retained only where it improved held-out geometric prediction.

## Update 2026-05-28

Interpreted Claude's successful TF-IDF SVD15 residual layer in `research/q2_stability/qwen/outputs/residual_svd_interpretation/`. The SVD result shows a productive tension in the machine-in-the-loop method: abstract human-readable residual labels underfit the geometry, while concrete text-basis components predict much better but require a separate distillation step to become interpretable theory. The next loop should translate SVD extremes into concrete, text-grounded residual dimensions and test whether they recover some of the SVD15 gain.
