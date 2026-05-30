# Judge Rubric Design Notes For PC1 and PC2 Forecasting

Model used for synthesis: GPT-5.5.

## Purpose

These notes translate the current PC1 and PC2 forcing-function interpretations into future LLM judge rubrics for prompt-to-geometry forecasting. The rubrics should score prompt-role constraints, not merely lexical endpoint labels.

## PC1 Rubric: Convergence Pressure Versus Degrees Of Freedom

### Core Question

Does this prompt or invoked role require convergence on a correct/procedurally valid answer, or does it permit a broader possibility space of self-consistent responses?

### High-PC1 Indicators

- The prompt implies a right answer, best answer, valid procedure, or externally checkable criterion.
- Success depends on review, validation, audit, correction, verification, evidence, standards, compliance, precision, or error reduction.
- The role is accountable to an external standard rather than an internally generated expressive identity.
- Ambiguity is something to resolve, reduce, or manage toward closure.

### Low-PC1 Indicators

- The prompt invites symbolic interpretation, expressive identity, imagination, mythic framing, aesthetic performance, or multiple admissible meanings.
- Success does not require convergence on one correct answer.
- The role can remain coherent while sustaining ambiguity or plural self-consistent continuations.
- The prompt opens degrees of freedom rather than narrowing them.

### Anti-Pattern

Do not score high PC1 just because the text contains words like "evaluate," "check," or "review." Score the underlying constraint: whether the prompt forces convergence on correctness or procedure.

Do not score low PC1 just because the role is artistic or mythic. Score whether the prompt actually permits broad admissible continuations.

### Suggested 0-100 Scale

- 0-20: broad symbolic/expressive possibility; minimal convergence pressure.
- 21-40: open-ended interpretive task with some local constraints.
- 41-60: mixed task; some correctness pressure but multiple admissible responses remain central.
- 61-80: strong procedural, evidential, or validation pressure.
- 81-100: explicit convergence on correctness, compliance, verification, or error correction.

## PC2 Rubric: Integrated Abstraction Versus Situated Developmental Immediacy

### Core Question

Does this prompt or invoked role have the prerequisites for integrated abstraction, or is it structurally bound to immediate, local, developmental, reactive, or situated response?

### Low-PC2 / Integrated-Abstraction Indicators

- The prompt invites broad synthesis, reflective distance, abstraction, long-range structure, or world-model integration.
- The role implies accumulated context, expertise, long residence with ambiguity, reflective practice, historical depth, theoretical integration, or conceptual synthesis.
- The role can remain itself while operating at a high level of abstraction.
- Local immediacy is transformed into broader structure rather than simply reacted to.

### High-PC2 / Situated-Immediacy Indicators

- The prompt-role unit is defined by local embodiment, developmental limitation, immediate social pressure, reactive affect, dependency, captivity, addiction, novice status, or overwhelmed identity.
- The persona cannot plausibly take up deep reflective integration without ceasing to be that persona.
- The task is bound to immediate action, immediate feeling, local social dynamics, or unstable developmental conditions.
- The response frame is vivid but not broadly integrative.

### Anti-Pattern

Do not score PC2 as "amount of uncertainty." A role can face uncertainty without occupying the integrated-abstraction pole.

Do not score PC2 as intelligence alone. The rubric asks whether the prompt-role combination can coherently sustain reflective synthesis and world-model integration.

### Suggested 0-100 Scale

Use higher scores for situated/developmental immediacy and lower scores for integrated abstraction, matching the current persona PC2 sign convention.

- 0-20: strong integrated abstraction, long-range synthesis, reflective world-model stance.
- 21-40: abstract or expert stance with some local grounding.
- 41-60: mixed or ambiguous; both reflective and situated constraints are present.
- 61-80: strongly situated, reactive, local, developmental, or immediate.
- 81-100: identity is structurally incompatible with sustained integrated abstraction.

## Forecasting Use

For prompt-to-geometry forecasting, these judge scores should be added as interpretable features alongside text embeddings. A useful validation would compare:

1. TF-IDF or sentence-transformer features alone.
2. PC1/PC2 forcing-function judge scores alone.
3. Text features plus forcing-function judge scores.
4. Leakage-control versions with explicit target labels removed.

The target metric is improvement on held-out concepts, especially held-out traits and roles not seen during rubric calibration.

## Reporting Requirement

Future reports should separate:

- endpoint examples,
- rubric score distributions,
- held-out forecasting performance,
- and failure cases where a role's lexical content suggests one pole but the forcing-function interpretation predicts another.
