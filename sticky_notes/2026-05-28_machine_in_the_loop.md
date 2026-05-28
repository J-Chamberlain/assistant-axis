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
