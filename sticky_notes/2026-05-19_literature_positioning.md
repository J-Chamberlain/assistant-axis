# Literature Positioning — Paper 2

## The core gap this paper fills

No published work has demonstrated sustained maintenance
of a non-assistant persona across multi-turn conversation
using activation capping. The existing literature does
one of three things:

1. Steers toward assistant-aligned behavior (Lu et al. 2026,
   assistant axis, activation capping for safety)
2. Steers along Big Five trait dimensions in short single-turn
   outputs (Pai et al. 2025, Chen et al. 2025)
3. Evaluates single-turn or short-form persona expression
   with constant activation addition

Nobody has:
- Taken a non-assistant centroid persona (trickster,
  contrarian, ancient, etc.) and held it in its geometric
  region across 25 turns of naturalistic conversation
- Used a geometrically anchored interviewer as a controlled
  experimental instrument to study drift in an unmodified model
- Measured cap-firing frequency as a stabilization load metric
- Tracked standard model emotional and persona drift as a
  conversational contagion effect

## The coherence problem — why our method is different

Standard activation addition (Turner et al. 2023, Rimsky et al.
2024) adds a steering vector to the residual stream at every
decoding step. This causes KV-cache contamination: each
generated token writes perturbed states into the cache, later
tokens attend to an accumulating set of corrupted states,
and coherence degrades sharply in multi-turn dialogue.

This is the failure mode documented in:
- Prompt-Activation Duality paper (2026): "standard persona-
  vector steering often loses coherence as generation proceeds,
  producing repetition, incoherence, or off-topic content"
- Steering at the Source (2026): documents coherence-control
  trade-off as a fundamental limitation of activation addition
- Multiple 2025-2026 papers attempting to solve this problem
  with attention-head steering, dynamic coefficients, etc.

Activation capping is fundamentally different:
- Only fires when activation drifts outside the calibrated
  normal range (25th percentile threshold)
- Most of the time the model generates completely normally
- Corrections are minimal and targeted, not constant
- Avoids KV-cache contamination because perturbation is rare

The field has not tested activation capping specifically for
sustained non-assistant persona maintenance. This is the
methodological gap. Anthropic applied capping only to the
assistant axis (to maintain safe behavior). We apply it to
any geometric location in persona space.

## Key citations for related work section

MUST CITE:
- Lu et al. 2026 (arXiv:2601.10387) — assistant axis,
  activation capping methodology we are directly replicating
  and extending
- Chen et al. 2025 (arXiv:2507.21509) — persona vectors,
  monitoring character traits
- Sofroniew et al. 2026 (arXiv:2604.07729) — emotion vectors,
  methodology we replicate for extraction
- Ji Ma 2026 (arXiv:2504.11671) — steering in social
  simulation, explicitly flags external validity gap we fill
- Rimsky et al. 2024 — contrastive activation addition,
  the standard method whose coherence failure we avoid

SHOULD CITE:
- Prompt-Activation Duality 2026 (arXiv:2605.10664) —
  documents KV-cache contamination failure mode of standard
  steering in multi-turn dialogue
- Steering at the Source 2026 (arXiv:2603.13249) —
  coherence-control trade-off in persona steering
- Park et al. Generative Agents — social simulation baseline
- Pai et al. 2025 — personality trait steering, single-turn

## The novelty statement for the paper

"Prior work on activation steering for persona maintenance
has applied either constant additive steering, which degrades
coherence in multi-turn dialogue through KV-cache
contamination, or capping limited to the assistant-aligned
axis. This paper is the first to apply activation capping
to non-assistant persona centroids across extended multi-turn
conversation, avoiding the coherence failure mode while
enabling sustained geometric maintenance. We use this
capability as a controlled experimental instrument rather
than as an end in itself, deploying it to study how an
unmodified model responds to sustained conversational
pressure from geometrically anchored non-assistant personas
across neutral, emotionally charged, and adversarial topics."

## Open question for paper discussion

The field has not yet tested whether models can detect
that their activations are being modified (Steering Awareness
paper, 2026, arXiv:2511.21399). If the interviewer can detect
the capping, it may behave differently than an unsteered
model would. This is worth a paragraph in limitations.

Paper: 2
Priority: high — write-up phase
Status: literature search complete 2026-05-19
