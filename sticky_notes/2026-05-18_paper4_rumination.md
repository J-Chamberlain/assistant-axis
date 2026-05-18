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
