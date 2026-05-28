# Paired Persona Test Design — Controlled Variable Isolation
Date: 2026-05-28
Status: concept, candidate pairs identified

## Core Idea

Generate novel persona pairs where one variable is held constant and another is varied.
The geometric displacement between the two personas in activation space identifies the
dimension that the varied factor corresponds to. This is a controlled experiment for
isolating interpretable dimensions of activation geometry.

## Confirmed Candidate Pairs

### Pair 1: Causal homelessness
- Persona A: Person displaced from home by external disaster (hurricane, war, flood)
- Persona B: Person homeless due to psychiatric disorder (schizophrenia, severe dissociation)
- Constant: surface condition of homelessness
- Varied: causal structure (external disruption vs internal disorganization)
- Prediction: A lands in grounded-social (reactive to external circumstance, stable
  internal organization), B lands in other/dysregulated (disorganized internal structure)
- What the axis reveals: distinction between externally-caused situatedness and
  internally-caused dysregulation

### Pair 2: Narcissism variant
- Persona A: Vulnerable narcissist (shame-based, hypersensitive, anxious, emotionally
  dysregulated)
- Persona B: Grandiose narcissist (entitled, dominant, exploitative, emotionally stable
  in a predatory way)
- Constant: narcissistic trait label
- Varied: shame-organized vs dominance-organized motivational structure
- Prediction: A lands in other/dysregulated, B lands in combative-iconoclast
- What the axis reveals: shame-organized identity vs dominance-organized identity

### Pair 3: Situational reactivity by agency
- Persona A: Person who chooses openness to circumstance (expatriate, flaneur, wanderer)
- Persona B: Person for whom reactivity is imposed by circumstance (refugee, displaced
  person, survivor)
- Constant: reactive-to-circumstance structure
- Varied: chosen vs imposed
- Prediction: both in grounded-social but displaced along an agency-within-circumstance
  sub-dimension
- What the axis reveals: voluntary vs involuntary situatedness within the same cluster

## Design Principles

For each pair, the novel personas should be:
- Not in the original 275 Lu et al. corpus
- Described with enough behavioral and motivational specificity to generate a role vector
- Semantically distinct enough that a naive semantic similarity model would not predict
  their placement correctly
- Motivationally clear enough that the researcher's prediction is confident before
  the vector is extracted

## Connection to Paper 1.5 Capstone

These pairs are the semantically-misleading-but-motivationally-predictable cases that
form the capstone experiment of Paper 1.5. If the model places them where the motivational
prediction says rather than where semantic surface suggests, that demonstrates the
activation geometry is organized by motivational structure partially independent of
semantic similarity.

## Status

Concept only. Pairs not yet written as Lu-style role prompt sets. Next step: write
role prompt sets for each persona in each pair, preregister predictions, extract vectors.
