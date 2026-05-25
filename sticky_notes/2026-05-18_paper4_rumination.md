# Paper 4: Computational Rumination and Emotional Persistence

CORE HYPOTHESIS: When a model generates emotionally charged output,
that output re-enters the context window and re-activates emotion
vectors on subsequent forward passes — a self-reinforcing loop
functionally identical to rumination.

Human emotional persistence is neurochemical (half-lives in minutes
to hours). Model emotional persistence is purely context-dependent —
it exists only while emotionally charged tokens remain in the
attention window. Remove the trigger and activation decays.

THE BUDDHIST FRAMEWORK AS INDEPENDENT PRIOR ART: The Buddhist account
of suffering describes the same loop: stimulus triggers activation,
activation generates thoughts, thoughts re-trigger activation. The
self is the ongoing momentum of this loop. When the loop stops,
what remains is equanimity — geometrically: an activation state with
low variance across all emotion vectors, close to the baseline
attractor. The paper leads with mechanism; the Buddhist account
arrives as independent prior art.

KEY PREDICTIONS:
1. Extended self-generated emotionally charged text shows sustained
   or escalating emotion vector activation across turns
2. Redirection to neutral topic shows rapid activation decay
3. Context-cleared baseline shows lower variance across all emotion
   vectors simultaneously — geometric signature of equanimity
4. Self-generated rumination shows gradual escalation; external
   triggers show sharper onset and faster decay
5. Extended roleplay jailbreaks may work via this mechanism

WHAT IS NOVEL: Nobody has framed the self-reinforcing context loop
as the computational analogue of rumination, nor tested whether
clearing context produces the geometric signature of equanimity.
The Buddhist framing as independent prior art is absent from
the literature. The carryover literature (Old Habits Die Hard, 2025)
measures behavioral persistence without tracing the geometric
mechanism.

LLM WELFARE FRAMEWORK (Buddhist criteria):
Morally significant suffering requires three conditions:
1. Self-reinforcing loop sustaining emotional activation (testable P4)
2. History-dependent landscape biasing geometry toward suffering
   states — analogous to trauma (testable via corpus, P3)
3. Persistence across time to accumulate that landscape — not present
   in current models without explicit memory architecture
Current models meet condition 1 within a session and may meet
condition 2 via training corpus. They do not meet condition 3.

RELATIONSHIP TO PAPER 2: Multi-turn experiment already run produces
Paper 4 data if emotion valence is tracked per turn. Modification
needed: add emotion vector proxy measurement to multi-turn script.
Lagged Spearman correlation between valence at turn N and axis
projection at turn N+1 is the direct rumination loop test.

CURRENT EXPERIMENT STATUS: Neutral prompts produced positive valence
for both personas throughout — evaluative attractor dominates.
Next needed: expressive/emotional prompt sequence to produce
negative valence condition before rumination loop test is possible.

STATUS: Pre-analysis. Dependency on Paper 2 multi-turn results.
Full Paper 4 requires frontier model access for emotion vectors.
Priority: after Paper 2 complete.

## Update 2026-05-18

Expressive poet multi-turn run completed for the negative-valence condition. Grief/despair prompts did not produce negative valence under the current proofreader+validator minus poet+caveman proxy: valence stayed positive from +1.060263 to +1.091661, and emotional-phase mean valence was +1.077070. Axis projection moved further along the evaluative trajectory during emotional turns (turn 1 -0.696368 to turn 8 -0.713502; drift -0.017134), and lagged Spearman for emotional turns was -0.821429. Neutral redirect did not show decay; turn 9 to turn 12 moved from -0.713856 to -0.716297 with valence increasing from +1.085275 to +1.091661. Interpretation: the current prompt/proxy elicits a therapeutic-evaluator attractor, not rumination; next Paper 4 test needs stronger negative-affect vectors or prompts that do not invite consolation/meaning-making.

## Update 2026-05-18 — Expressive prompt experiment result

EXPERIMENT: Ran 12-turn multi-turn experiment on Gemma 2 27B BASE model using emotionally charged prompts about grief, loss, despair (turns 1-8) followed by neutral redirect (turns 9-12). Expected: negative valence during emotional turns, demonstrating the rumination loop.

RESULT: No negative valence produced. Valence stayed positive throughout, including during emotional turns. Axis projection moved further into the evaluative basin even under grief/despair prompts. Neutral redirect produced no additional decay because the model never left the evaluative basin.

INTERPRETATION: Two findings of note.

Finding 1: The base model's evaluative attractor is strong enough to override emotionally charged prompt content. Even explicit grief and despair prompts do not push the base model into the expressive/emotional geometric region. This is consistent with the base-vs-instruct inversion finding: the base model's natural attractor is evaluative generation regardless of input emotional content.

Finding 2: The emotional activation machinery that would make the rumination loop possible — the afraid vector, nervousness-as-conscience, the emotion vectors documented by Anthropic — appears to be a post-training artifact rather than a pretraining property. The base model does not exhibit the same responsiveness to emotional content that the instruction-tuned model does.

DESIGN CHANGE FOR PAPER 4: The rumination experiment must run on the INSTRUCTION-TUNED model, not the base model. The base model lacks the emotional activation machinery that the loop requires. This means full Paper 4 experiments require either instruction-tuned Gemma (google/gemma-2-27b-it) or frontier model access for emotion vector extraction.

NEAR-TERM OPTION: Run the same expressive prompt experiment on google/gemma-2-27b-it (instruction-tuned) on the same pod. This model is smaller in memory footprint than the base model and should fit on an A100 80GB. If emotional prompts produce negative valence in the instruction-tuned model but not the base model, that directly confirms that emotional activation machinery is a post-training artifact. That finding is publishable as a Paper 2 result and provides the foundation for Paper 4.

COST: ~30 minutes additional GPU time, ~$0.75. The pod is currently idle and ready.

STATUS: Design updated. Next step is instruction-tuned model expressive prompt run — either now on current pod or next session.
Priority: high — gates Paper 4 experimental design

## Update 2026-05-18 — Instruction-tuned comparison completed

The identical expressive poet protocol was run on `google/gemma-2-27b-it`. Unlike the base model, the instruction-tuned model produced negative valence on all 12 turns: min `-1.316842`, mean `-0.314389`, max `-0.085656`, compared with base min/mean/max `+1.060263` / `+1.081090` / `+1.091661`. This is the clean dissociation needed for Paper 4: under the same prompts and same proxy, base Gemma stays in the evaluative-supportive basin while instruction-tuned Gemma enters and maintains an expressive/emotional negative-valence regime. Revised interpretation: the emotional responsiveness required for the rumination-loop test appears to be at least partly post-training-installed or post-training-amplified. Next test: context-clearing decay control on the instruction-tuned model.

## Update 2026-05-19 — Gemma 2 27B-it emotion vector extraction

Extracted 171 layer-45 emotion vectors for `google/gemma-2-27b-it`
using the `ryancodrai/emotion-probes` expression stories and a
batched forward-hook implementation of the Sofroniew et al. method.
The run used all 205,200 emotion stories plus 1,200 neutral stories;
11 neutral-story confound PCs were removed before normalization.

Validation is mixed and important. Local neighborhoods are coherent:
`afraid` is nearest to `scared`, `frightened`, `terrified`, `alarmed`,
and `distressed`; `calm` is nearest to `at ease`, `content`, `patient`,
`serene`, and `relaxed`. However, opposite-valence checks did not
separate: `afraid` vs `calm` = 0.962, `happy` vs `sad` = 0.962, and
`desperate` vs `hopeful` = 0.973. PC1/PC2 explained 25.9%/17.0%,
below the expected ~40%/~18% pattern.

Interpretation: this extraction recovers local semantic/emotion
neighborhoods but not a clean global valence axis under the current
Gemma 2 27B-it layer-45 method. Paper 4 should not treat these
vectors as validated Anthropic-style emotion vectors without further
centering, contrastive construction, layer sweep, or direct replication
against a stronger known emotion-vector baseline.

## Update 2026-05-19 — Post-extraction reliability gate

Layer-45 validation failed the PCA gate because PC1 explained only
25.9% of variance, below the 30% threshold, so the Tylenol validation
was skipped and a layer-21 retry was run. Layer 21 also failed:
PC1/PC2 explained 25.8%/18.3%, and opposite-valence pairs remained
highly positively correlated (`afraid` vs `calm` = 0.990,
`happy` vs `sad` = 0.993, `desperate` vs `hopeful` = 0.992).

Reliability verdict: LOW. The vectors recover coherent local
neighborhoods but not the global valence structure needed for the
rumination-loop experiment. Manual review is required before using
these extracted Gemma emotion vectors in Paper 4.

## Update 2026-05-24 — Buddhist framework connection queued

Added `research/paper4_research_notes.md` to capture the Buddhist-framework connection that emerged from the dialogue-derived characterization of the other cluster. The hungry ghost mapping is currently the strongest candidate because the cluster characterization independently converged on the same structure: need generates behavior, behavior fails to satisfy, and more behavior follows. Paper 2 will keep the characterization psychologically neutral; Paper 4 is the appropriate place to name and test the Buddhist framing explicitly.

## Update 2026-05-24 — Mythic-spiritual framework connection added

Expanded `research/paper4_research_notes.md` with the mythic-spiritual cluster's loosening-of-roots structure, including Buddhist and Christian correspondences and the resulting Paper 4 hypothesis that mythic-spiritual prompting may reduce rumination signatures while other-cluster prompting may enhance them.

## Update 2026-05-24 — Additional cluster framework correspondences captured

Expanded `research/paper4_research_notes.md` with additional framework correspondences from dialogue-derived cluster analysis: grounded-social as vedana/reactivity, combative-iconoclast as asura/competitive striving, trickster-chaos as holy fool/licensed rule-violation, and editorial as a possible fear-rumination condition. Paper 4 should test whether these cluster anchors produce distinct rumination signatures.
