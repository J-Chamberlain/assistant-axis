# Music-Driven Real-Time Emotion Visualization

Date: 2026-05-20
Status: Concept — requires multimodal model access
Priority: Medium-high — general audience, striking demo,
          essay terminus

## Core idea

Feed a model audio of a song and visualize its internal
emotional activation in real time using the emotion equalizer
visualization. The audience listens to the song while watching
the model's emotional response unfold in sync with the music.

The emotion equalizer is already built for word-by-word
animation. Wiring it to a multimodal model's response to
audio is the next step.

## The Moby connection

"When It's Cold I'd Like to Die" (Moby, 1995) — a song about
despair and dissolution. Identified as a potential probe for
sadness/despair activation, analogous to the forced swim test
in rodent antidepressant research. The safety connection: if
sustained negative content drives a model's internal state
toward the dissolution/despair cluster, and emotional state
influences behavior (confirmed by Anthropic emotion vector
research), this is a live demonstration of why internal
emotional monitoring matters for safety.

The music makes abstract safety claims visceral. This is the
terminus of the second essay — the way Walter White ended
the first.

## The carousel design

Twelve handpicked songs covering the full valence-arousal
circumplex. Starting with high-arousal positive, moving
through the range, ending with the Moby track as the
emotional terminus. The carousel maps the full circumplex
using music as the stimulus.

## Outreach note

Moby is philosophically oriented — has written about
consciousness, animal welfare, ethics of technology. The
framing of using his music to probe an AI's inner emotional
life is likely to resonate. Approach: build the visualization
first, show it to him, let him experience it before making
any licensing request. Consider reaching out once the
text-only version is working.

## Implementation path

Phase 1 (doable now): Text-only. Feed lyrics as tokens,
measure emotion probe direction activations per phrase,
animate over the emotion equalizer. No audio needed.

Phase 2: Audio sync. Use Web Audio API to play the song
while the visualization runs. Lyrics timed to audio playback.

Phase 3: Multimodal. Feed actual audio to a multimodal model.
Compare its emotional response to the text-only model's
response to lyrics. Requires frontier model API access.
