# Multimodal Introspection Experiment — Fellowship Research Proposal

Date: 2026-05-20
Status: Concept — fellowship-level research proposal
Priority: High — novel, cross-modal, directly safety-relevant

## The core question

When a model describes its own emotional state in words, does
that verbal description accurately reflect its internal
activation geometry? This is a question about introspective
accuracy, and it has a testable cross-modal extension.

## The experimental design

STIMULUS: A piece of music with strong emotional character.
Use the instrumental-only version (vocals removed via Spleeter
or Demucs — both open source) to isolate sonic emotional
content from lyrical semantic content.

MEASUREMENT 1 — Self-report channel:
Feed the instrumental audio to a multimodal model. Ask it to
describe its emotional response in as much detail as possible
at multiple points during the track. Record the verbal
description.

MEASUREMENT 2 — Geometry channel:
Feed the lyrics (or a description of the song) as text through
the emotion probe direction pipeline. Measure actual activation
geometry at layer 48. Record the probe direction projections.

COMPARISON: Do the verbal self-report and the geometric
activation align or diverge?

## Why both outcomes are interesting

ALIGNMENT: The model's verbal emotional vocabulary accurately
tracks its internal geometry. Evidence of introspective
accuracy. Suggests the model's descriptions of its inner
states are meaningful and not confabulated.

DIVERGENCE: The model describes one emotional state while
its geometry shows another. This is the discontinuity finding.
It would suggest a real gap between human and AI multimodal
emotional experience — humans integrate audio and semantic
content into a unified felt sense; the model may process
them in separate channels that don't fully communicate.

## Connection to existing findings

The behavioral-geometric dissociation finding from Paper 2
(jester held voice but drifted geometrically; proofreader
drifted voice but held geometrically) is a version of this
same phenomenon — verbal output and internal geometry can
come apart. The music experiment extends this to self-report
about emotional states specifically.

The GPT visual emotion description finding (models can
describe the emotional tone of photographs with surprising
nuance) motivates the hypothesis that multimodal models
may accurately describe emotional tone from audio alone —
even without lyrics — if the sonic emotional content is
sufficiently clear.

## Fellowship framing

This is exactly the kind of cross-modal interpretability
question that connects mechanistic interpretability to
multimodal models — an open frontier. The design is clean,
the two outcomes are both publishable, and it connects
directly to the safety implications of the emotion vector
research. The introspective accuracy question is one Anthropic
has not directly studied in the multimodal context.

## Practical first step

Test the verbal description hypothesis with any available
multimodal model (GPT-4o, Gemini) using the Moby instrumental.
Does the model describe the emotional tone accurately from
sound alone? This is testable today with no infrastructure
beyond an API call. If yes, the full experiment is worth
building.
