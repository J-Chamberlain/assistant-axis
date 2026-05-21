# Radial Vector Visualization — Live Internal State Display

Date: 2026-05-20
Status: Concept — not yet built
Priority: High — companion visualization to emotion equalizer
Audience: General and research

## Core idea

A radial visualization showing the model's internal activation
state as a vector arrow (or set of arrows) radiating from a
central origin. As text is generated word by word, the arrow
sweeps through the space, its direction determined by
projection onto persona/emotion basis vectors and its length
by activation magnitude.

The visual is similar to the Anthropic logo — vectors
radiating from a central point in a constellation — which
may be intentional on Anthropic's part given their work on
activation geometry. Whether designed with this in mind or
not, the resonance is real.

## Wind rose connection

The wind rose chart from wind energy analysis gives both
directionality and magnitude simultaneously — equivalent to
a vector but with the added precision of a y-axis equivalent
showing frequency or intensity at each angle. For a general
audience, simple arrows around a centroid may be more
aesthetically effective. Mathematically both are valid.
The wind rose version would show which directions the model
visits most frequently across a full conversation, while
the arrow version shows moment-to-moment movement. Both
have a role — arrow for animation, wind rose for summary.

## Three simultaneous displays

Three radial plots side by side, or three concentric rings
on a single plot, each representing a different basis:

Ring 1: Persona space — projection onto the 7 cluster
centroid role vectors. Arrow points toward the nearest
persona cluster.

Ring 2: Trait space — projection onto key trait vectors,
particularly Conscientiousness/Psychopathy gradient from
Paper 1. Arrow shows where on the trait axis the model sits.

Ring 3: Emotion space — projection onto the 5 emotion
cluster representatives (serene, distressed, joyful,
perplexed, proud) mapped onto the valence-arousal circumplex.
Arrow points to the current emotional position.

When the persona is holding and text is coherent, all three
arrows point in consistent directions. When there is
behavioral-geometric dissociation — the text sounds like
the persona but the geometry is elsewhere — the rings
diverge. That divergence made visible is the dissociation
finding rendered as a live image.

## The capping demonstration

This visualization would show what activation capping is
doing in real time: the arrow being pulled toward one
region (the model's natural attractor) and snapping back
as the cap fires. At 100% cap load (ancient, blogger) you
would see continuous tension — the arrow constantly
straining away from the anchored position and being
corrected. At 0% cap load (editor) the arrow would sit
stably in one region with no visible corrective force.

## The benchmark / semantic annotation thread

A frontier model (GPT-4o or equivalent) could assign
valence-arousal coordinates to each word or phrase as it
is generated — this is called valence-arousal annotation.
That annotation provides a semantic ground truth: given
what the model said, where should its internal state be?
Comparing the semantic annotation (what the words mean)
against the geometric activation (what the model's
internals show) would reveal whether the internal state
and the verbal output are aligned or dissociated.

When they align: the model's internal geometry tracks the
semantic content of its own words.
When they diverge: the model is saying one thing while
its internal state is somewhere else. This is the
introspective accuracy question from the multimodal
introspection experiment sticky note, applied here to
text generation rather than audio perception.

Implementation: straightforward API call to a frontier
model per chunk of text, returning a valence (-1 to 1)
and arousal (0 to 1) score. Overlay the resulting
annotation path onto the emotion ring of the radial
visualization as a ghost arrow or trail, showing both
the semantic ground truth and the geometric activation
simultaneously.

## Coherence analysis for 100% capped personas

Ancient and blogger required activation capping on 100%
of turns. The behavioral question is whether their output
text was coherent and persona-consistent despite this
continuous geometric strain, or whether the dissociation
produced incoherent text. This is a qualitative analysis
task — read sample conversations from the CSV and assess
voice consistency. If the text is coherent but the geometry
is strained, the radial visualization would show the
dissociation clearly: persona-sounding words with an arrow
pointing away from the persona's geometric home.

## Priority next steps

1. Qualitative read of ancient and blogger conversations
   from dyad CSV — Dispatch task, no computation needed
2. Prototype the arrow visualization with dummy data,
   same pattern as emotion equalizer
3. Add valence-arousal annotation overlay once prototype
   is working
4. Wind rose summary version as a separate static chart
   for paper figures
