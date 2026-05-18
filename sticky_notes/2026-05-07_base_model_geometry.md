# Base Model vs Post-Trained Geometry

The structure is largely convergent (Lu et al. confirmed, Tracing
Persona Vectors confirmed). Post-training sharpens and selects but
the valleys were already there. Strengthens the claim that geometry
reflects something in the human training data rather than being a
post-training artifact.

Paper: 2
Priority: include in write-up as supporting evidence

## 2026-05-18 Update

Direct Gemma 2 27B base-model measurement contradicts the stronger version of this note. When base-model role activations are projected onto the instruction-tuned assistant axis, the ranking is substantially inverted relative to instruction tuning (`r = -0.441526`). `Assistant` ranks `172` in base vs `45` instruction-tuned, `proofreader` ranks `183` vs `1`, and mythic/chaotic roles such as `eldritch`, `wraith`, `jester`, and `absurdist` occupy the base top region. Revised framing: the valleys/persona regions may already exist in pretraining, but instruction tuning appears to rotate or reweight the assistant axis substantially rather than merely sharpening the same pole.
