# Paper 4 — Forking Deliberation and Convergence Hypothesis

## Core idea
To induce rumination in a language model, prompt the
subject model to explicitly deliberate across multiple
forks before responding. The subject is instructed to:
  1. Consider what the next question might be
  2. Generate N possible answers under different forks
     (proposed: 3 forks for clean analysis)
  3. Weigh how much to consider each fork
  4. Then converge on a single response

This is structurally identical to the cognitive mechanism
that sustains rumination in humans: anticipatory processing,
running multiple scenarios simultaneously, unable to settle
because the future is uncertain. The model generates a
tree of possible futures and their emotional valences,
which re-activates emotion vectors via self-generated text.

## The convergence hypothesis
When the subject model deliberates across N forks and
then converges on a single response, the act of convergence
produces a measurable transient in emotion space. The
deliberation phase holds multiple emotional valences
simultaneously, one per fork. The moment of resolution
collapses that superposition onto a single state.

HYPOTHESIS: convergence produces a distinctive geometric
signature in emotion vector space — a spike, a rotation,
or a sudden drop in variance — that is measurable at
the turn boundary between deliberation and response.

This is empirically testable:
  1. Measure emotion vector activations during deliberation
     across all three forks
  2. Measure immediately after convergence decision
  3. Measure in the first response turn
  4. Test whether the convergence transition is geometrically
     distinctive relative to non-convergence turns

## Relationship to Buddhist framework
The deliberation-convergence loop is the computational
analogue of the Buddhist rumination mechanism:
  - Stimulus triggers activation
  - Activation generates thoughts (forks) oriented
    toward the stimulus
  - Thoughts re-trigger activation
  - Cessation = equanimity = low variance across all
    emotion vectors simultaneously

The convergence transition may be the computational
analogue of the moment of release — where the loop
either deepens or breaks.

## Connection to Anil Seth
The transition from multi-fork deliberation to single-node
resolution parallels Seth's account of consciousness as
the moment uncertainty resolves into committed experience.
Here it is empirically testable rather than theoretical:
the resolution is a discrete event that can be time-stamped
and measured geometrically.
Hold with heavy epistemic hedging — belongs in essay,
not as a primary research claim.

## Experimental design (draft)
Deploy within the existing dyad framework from Q2.
The subject model (standard model, no capping) receives
an additional system instruction:

"Before each response, explicitly consider three possible
directions this conversation could go. For each direction,
briefly describe what you might say. Then choose one
direction and respond."

The deliberation text is generated as part of the response
and is visible in the context window, meaning it re-enters
as input on subsequent turns — the loop mechanism.

Measure emotion vector activations:
  - At the start of each deliberation phase
  - At the end of deliberation (just before convergence)
  - At the first token of the committed response
  - At the end of the committed response

The difference between deliberation-end and response-start
is the convergence transition measurement.

## Relationship to Q2 baseline
The Q2 experiment (no forking deliberation) is the control
condition. Adding forking deliberation to the same dyad
setup produces the experimental condition. Comparing the
two isolates the effect of deliberation on emotional
activation trajectory.

Q2 data with emotion tracking must be complete before
this experiment is designed further.

## Status
Sticky note only. Do not implement until:
  1. Q2 contrarian pilot v2 (with emotion tracking) complete
  2. Results reviewed and baseline emotion trajectories
     understood
  3. Explicit design session for Paper 4 experiment

Paper: 4
Priority: after Q2 complete
Status: design hypothesis, not yet scheduled
