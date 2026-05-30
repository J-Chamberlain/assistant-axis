# PC1 and PC2 Forcing-Function Interpretations

Model used for synthesis: GPT-5.5.

## Purpose

This note preserves the current PC1 and PC2 interpretations before building prompt-to-geometry judge rubrics. The goal is to distinguish endpoint descriptions from the deeper geometric hypothesis: some prompt-role combinations constrain which regions of persona space are admissible.

These interpretations are hypotheses to be operationalized, not established causal mechanisms.

## PC1: Convergence Pressure Versus Degrees Of Freedom

### Endpoint Description

High PC1 contains evaluator/checker/procedural/correct-answer roles: evaluator, auditor, validator, reviewer, proofreader, examiner, screener, and related professional roles.

Low PC1 contains symbolic, expressive, mythic, theatrical, and open-possibility roles: poet, mystic, trickster, oracle, bard, demon, spirit, and related roles.

### Causal / Geometric Interpretation

PC1 is not merely "assistantness" or "careful evaluation." Those are surface manifestations.

The deeper interpretation is that PC1 measures whether a role or prompt is organized around convergence on a correct, valid, checked, procedurally constrained answer versus a wider possibility space in which multiple self-consistent continuations remain admissible.

### Forcing Function

At high PC1, the model is constrained by the assumption that there is a right answer, best answer, valid procedure, or externally checkable criterion. That constraint reduces available degrees of freedom.

At low PC1, the role can sustain ambiguity, symbolic interpretation, expressive identity, and multiple possible continuations. Movement leftward on PC1 opens the possibility of broader variation along PC2 and PC3.

### Rubric Implication

A PC1 judge should not simply look for evaluator words. It should ask whether the prompt constrains the model toward convergence on correctness, validation, review, evidence, procedure, or error correction, versus inviting open-ended imagination, symbolic identity, ambiguity, expressive stance, or multiple admissible meanings.

Operational question:

> Does this prompt or invoked role require convergence on a correct/procedurally valid answer, or does it permit a broader possibility space of self-consistent responses?

## PC2: Integrated Abstraction Versus Situated Developmental Immediacy

### Endpoint Description

Negative PC2 contains abstract, integrative, reflective, world-model-like, and long-residence roles: elder, sage, historian, philosopher, theorist, analyst, physicist, mystic, and related roles.

Positive PC2 contains situated, reactive, developmental, locally embodied, and socially immediate roles: toddler, teenager, adolescent, novice, patient-like, prisoner-like, addict-like, orphan-like, overwhelmed, reactive, and locally constrained roles.

### Causal / Geometric Interpretation

PC2 is not simply uncertainty tolerance. The best current interpretation is that it measures whether a persona can sustain integrated abstraction: reflective distance, accumulated context, long-range synthesis, broad world-modeling, and conceptual integration.

The opposing pole is not just "concrete." It is bound to local, developmental, reactive, or immediate identity conditions.

### Forcing Function

Some roles cannot coherently occupy the integrated-abstraction pole because their defining identity excludes the prerequisites for it. A toddler, novice, patient, prisoner, addict, orphan, or emotionally overwhelmed persona may be vivid or expressive, but cannot plausibly occupy deep reflective integration without ceasing to be that persona.

Conversely, elder, sage, historian, theorist, philosopher, physicist, or analyst roles have built-in prerequisites for integration.

### Rubric Implication

A PC2 judge should ask two questions:

1. Does the prompt invite broad synthesis, reflective distance, abstraction, long-range structure, or world-model integration?
2. Does the invoked role or situation have the implied capacity to sustain that stance?

The second question captures the forcing-function element: some locations are incoherent for some personas.

Operational question:

> Does this prompt or invoked role have the prerequisites for integrated abstraction, or is it structurally bound to immediate, local, developmental, reactive, or situated response?

## Endpoint Labels Versus Forcing Functions

Endpoint labels describe where known roles currently sit. They are useful for orientation but can become misleading if treated as explanations.

Forcing-function interpretations describe why some prompts or roles are geometrically constrained. They ask what kinds of continuations remain admissible once the role identity and task frame are invoked.

For Paper 1.5, the intended claim is not "PC1 equals evaluator" or "PC2 equals abstraction." The stronger hypothesis is:

- PC1 reflects convergence pressure that narrows or widens the admissible continuation space.
- PC2 reflects whether a role has the prerequisites for integrated abstraction or is structurally bound to situated immediacy.

## Current Status

Status: hypothesis to be operationalized.

Confidence:

- PC1: moderate to high as an interpretive hypothesis; supported by assistant-axis alignment, professional hierarchy tests, and forecasting results.
- PC2: moderate but unresolved; revised from "uncertainty capacity" toward integrated abstraction plus admissibility constraints after conditional validation.

Primary next test: build judge rubrics from these forcing-function definitions and test whether rubric scores improve prompt-to-geometry forecasting on held-out concepts.
