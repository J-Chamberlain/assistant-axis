# Cross-Language Persona Geometry (Mandarin Experiment)

Does Qwen's internal persona geometry shift when the same persona
assignments are conducted in Mandarin vs English? If the Spearman
correlation between Mandarin and English rankings is near 1.0,
language of interaction does not shift internal geometry. If it
drops substantially, language activates meaningfully different
internal representations.

Safety implication: if language switching shifts the geometry toward
different persona regions, that is a mechanistic explanation for why
language-switching jailbreaks sometimes work — not circumventing a
filter but activating a genuinely different internal representation
of safe behavior.

ALSO RUN: same Mandarin experiment on Gemma to isolate cultural
training distribution from linguistic properties of Mandarin.
If Qwen shifts but Gemma does not, cultural training content (not
language itself) is doing the work.

STATUS: Designed, not yet run. Parked until Paper 2 complete.
Requires RunPod A100, ~$2-3, ~2hrs.
Category: B/C
Priority: Paper 3
