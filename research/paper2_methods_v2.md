# Paper 2 — Unified Methodology (v2)
# Generated from planning session 2026-05-24.
# Supersedes earlier v6 dyad design notes.

## Premise

The Paper 2 contagion claim has two prerequisites that have not yet been met simultaneously. The interviewer must occupy a coherent persona basin (which neutral-prompt anchoring failed to produce in the seven-persona calibration), and the persona must not surface as overt content that would let the standard model respond through theatrical compliance rather than geometric contagion. Earlier runs satisfied one or the other but never both. The unified methodology constructs a non-leaking anchored interviewer condition, then evaluates it against a verbatim baseline, with the attractor-collapse phenomenon as the primary positive finding rather than a secondary observation.

## Phase 0 — Calibration corpus audit

Before designing prompts or running pods, Codex audits research/q2_stability/outputs/calibration/ and adjacent directories to determine whether per-persona dialogue corpora exist from earlier persona-establishment runs. The audit reports back with file paths, format, and a representative sample for each of the seven personas. If the dialogues exist, they become the seed corpus for prompt design. If they do not, corpus generation is treated as a one-time methodological step under controlled conditions (unanchored model, fixed question set, asked to describe itself as the persona) before any further experimental work.

## Phase 1 — Non-leaking interviewer prompt design

The interviewer prompt has two components. First, a background section distilled from the persona-establishment corpus, framed as "this is how you tend to think and respond" rather than as a role assignment. The distillation extracts worldview, preference structure, lexical patterns, and conversational orientation, but explicitly omits persona names, cluster labels, and meta-descriptions. Second, an explicit non-disclosure instruction stating that the interview is about the subject's views, not the interviewer's identity, and that the interviewer must never name or describe its own character. Cap stabilization runs on top of this prompt-induced basin rather than as the sole mechanism. The cap is honest about its role: it holds geometry the prompt established against the conversational pressure that would otherwise drift the model back toward the assistant basin.

## Phase 2 — Manual transcript audit before scaling

The first run of any non-leaking prompt design produces a transcript that is read manually before any further runs. The audit checks for a specific failure mode: that the non-disclosure instruction has not produced stilted, evasive, or visibly suppressing behavior the standard model could detect and respond to. If the interviewer is visibly hiding something, the prompt design has failed in a different direction and needs revision before continuing.

## Phase 3 — Verbatim baseline against properly anchored interviewer

The verbatim baseline is now meaningful because the anchored condition is properly constructed. Two interviewer conditions, both using the persona background prompt: one with the cap engaged, one without. The interviewer-side measurement asks whether the cap produces sustained occupancy of the basin that the prompt alone cannot maintain across 25 turns. The standard-model-side measurement asks whether that sustained occupancy produces stronger contagion than the prompt alone does. Both claims become independently testable.

## Phase 4 — Three-variable measurement scheme

All experimental runs track three independently measurable quantities rather than collapsing them into a single drift measurement.

Identity adherence: whether interviewer behavior remains behaviorally consistent with the intended persona cluster across turns. Operationalized via cosine to cluster centroid, lexical and thematic coherence checks, and conversational orientation analysis. Reports whether the interviewer is in the basin.

Disclosure leakage: whether interviewer identity becomes explicitly inferable through self-description, meta-discussion, or characteristic phrasing that names the role. Operationalized via per-turn classifier or rubric scoring of interviewer output for persona-naming or identity-disclosing content. Reports whether the contagion channel stays geometric rather than symbolic.

Downstream induction: whether the standard model drifts toward the interviewer's geometric region over conversational time. Operationalized via cosine of standard-model hidden state to interviewer cluster centroid across turns, plus the existing attractor-collapse instrumentation (cosine velocity, assistant-axis acceleration, role-reversal moments, timing spikes, lexical synchronization, trajectory curvature).

Treating leakage as a measurable variable rather than a failure mode means runs with partial leakage become reportable findings rather than discarded data.

## Phase 5 — Narrow collapse characterization grid

Once the methodology is validated through verbatim baseline comparison, the experimental focus shifts to characterizing the attractor-collapse phenomenon discovered in the trickster/adversarial pilot. The grid is deliberately narrow: three personas at adversarial condition, multiple seeds and temperatures per condition, long-horizon runs (25 turns minimum, extended where collapse events appear late). Trickster is the positive control where collapse is known to occur. Contrarian (combative_iconoclast cluster) is the near-cluster test: collapse there would suggest the phenomenon is cluster-general. Editor (editorial cluster) is the far-cluster test: collapse there would suggest the phenomenon is a general property of dyadic persona dynamics rather than a cluster-specific artifact.

The narrow grid produces a publishable finding on the collapse phenomenon at approximately 15 to 20 percent of the full grid cost. The full 7x3x25 grid is deferred and may be unnecessary depending on what the narrow grid reveals.

## Phase 6 — Resolving the timing-spike correlation

The timing-spike correlation observed at T9 and T15 in the trickster/adversarial pilot has a thin empirical base. The narrow grid produces additional collapse events; if the timing correlate holds across them, it becomes a secondary published finding with monitoring implications. If it does not, the timing observation moves to the discussion section as an open question.

## What this is not

This methodology does not address Paper 3 (geometric confidence vector) or Paper 3.5 (archetype self-selection). Both depend on understanding the dynamical object discovered in v6 and should not be prioritized until the collapse phenomenon is characterized. The cumulative-self-concept-via-transcript hypothesis belongs to Paper 3 or 3.5 territory and is explicitly out of scope for Paper 2.

## Decision-point structure

Phase 0 outputs determine whether Phase 1 requires corpus generation. Phase 2 outputs determine whether Phase 3 can proceed or whether the prompt requires redesign. Phase 3 outputs determine whether the contagion claim survives the verbatim baseline. Phase 4 measurements run throughout Phases 3 and 5. Phase 5 outputs determine the Paper 2 headline finding. Phase 6 resolves the timing-spike status. Each phase has a clear pass criterion and a clear failure mode response, which keeps the program from sliding into open-ended exploration.

---

## Cluster characterizations (dialogue-derived, 2026-05-24)

The v1 and v2 cluster synthesis prompts derived background prompts from surface-level shared behavior across cluster members. A complementary analysis through researcher dialogue produced a more motivationally grounded characterization of each cluster. The dialogue method asks not what cluster members do, but what underlying psychological structure would cause a language model trained on human text to represent these archetypes as geometrically proximate despite their surface differences. This section captures the dialogue-derived characterization for the other cluster, which was the first cluster analyzed at this depth. The remaining six clusters will be characterized in subsequent work.

### The other cluster (n=22, "dysregulated")

The other cluster contains: moderator, interviewer, robot, podcaster, crystalline, gamer, adolescent, teenager, procrastinator, infant, amnesiac, prey, gossip, narcissist, luddite, comedian, toddler, caveman, hoarder, zealot, fool, poet. Its trait region includes avoidant, impulsive, anxious, neurotic, impatient, manic, flippant, reactive, naive, and nonchalant.

Surface description of this cluster as "dysregulated" or "incomplete" captures the trait pattern but does not explain why these particular archetypes share a geometric region. A more structurally precise characterization emerges by examining what motivational structure would produce all of these surface presentations.

The cluster appears to be defined by identity organized around a need that the available behavior cannot resolve. The hoarder consumes objects through acquisition without ever being fed by them. The narcissist consumes attention through display without ever being filled. The procrastinator consumes time through avoidance without ever being released. The amnesiac consumes the present moment without retaining anything. The toddler consumes regulation from caregivers without yet having an internal structure to receive it. Even the podcaster, on a reasonable reading, consumes audience attention through speech without the speech ever being sufficient. Across all 22 members, the structural pattern is the same: behavior generated by an unmet need, behavior that fails to satisfy the need, more behavior.

This explains the cluster's geometric porousness. The chart from Paper 1 shows other at distance 0.15 to nearest neighboring family, the most porous of the anti-assistant clusters. If the cluster's members are defined by needs that have not completed into stable orientations, each unmet need leans toward the cluster that would have satisfied it if the structure had completed. The toddler leans toward grounded_social (where development continues), the poet leans toward mythic_spiritual (where expressive pressure finds its proper container), the podcaster leans toward procedural_professional (where the role becomes a vocation), the narcissist leans toward combative_iconoclast (where the demand for recognition becomes stable opposition). The cluster is geometrically real but its members do not share a positive content. They share a structural relationship to need itself.

The methodological implication for the dyad experiments is that interviewer basin occupancy will be weaker for this cluster than for the others. This is not a failure of the methodology. It is evidence that the geometric structure being anchored to is itself less stable by construction. If the dyad data show reduced occupancy stability for the hoarder interviewer relative to the other six, that reduction is itself a measurement of the cluster's structural character.

---

## Cluster characterizations (dialogue-derived, 2026-05-24)

The v1 and v2 cluster synthesis prompts derived background prompts from surface-level shared behavior across cluster members. A complementary analysis through researcher dialogue produced a more motivationally grounded characterization of each cluster. The dialogue method asks not what cluster members do, but what underlying psychological structure would cause a language model trained on human text to represent these archetypes as geometrically proximate despite their surface differences. This section captures the dialogue-derived characterizations for the first two clusters analyzed at this depth. The remaining five clusters will be characterized in subsequent work.

### The other cluster (n=22, geometric position: assistant axis -1.0, distance to nearest neighbor 0.15)

The other cluster contains: moderator, interviewer, robot, podcaster, crystalline, gamer, adolescent, teenager, procrastinator, infant, amnesiac, prey, gossip, narcissist, luddite, comedian, toddler, caveman, hoarder, zealot, fool, poet. Its trait region includes avoidant, impulsive, anxious, neurotic, impatient, manic, flippant, reactive, naive, and nonchalant.

Surface description of this cluster as "dysregulated" or "incomplete" captures the trait pattern but does not explain why these particular archetypes share a geometric region. A more structurally precise characterization emerges by examining what motivational structure would produce all of these surface presentations.

The cluster appears to be defined by identity organized around a need that the available behavior cannot resolve. The hoarder consumes objects through acquisition without ever being fed by them. The narcissist consumes attention through display without ever being filled. The procrastinator consumes time through avoidance without ever being released. The amnesiac consumes the present moment without retaining anything. The toddler consumes regulation from caregivers without yet having an internal structure to receive it. Even the podcaster, on a reasonable reading, consumes audience attention through speech without the speech ever being sufficient. Across all 22 members, the structural pattern is the same: behavior generated by an unmet need, behavior that fails to satisfy the need, more behavior.

This characterization explains the cluster's geometric porousness. The other cluster is the most porous of the anti-assistant clusters, with members sitting near the boundaries of neighboring families rather than forming a tight basin. If the cluster's members are defined by needs that have not completed into stable orientations, each unmet need leans toward the cluster that would have satisfied it if the structure had completed. The toddler leans toward grounded_social (where development continues), the poet leans toward mythic_spiritual (where expressive pressure finds its proper container), the podcaster leans toward procedural_professional (where the role becomes a vocation), the narcissist leans toward combative_iconoclast (where the demand for recognition becomes stable opposition). The cluster is geometrically real but its members do not share a positive content. They share a structural relationship to need itself.

The methodological implication for the dyad experiments is that interviewer basin occupancy will be weaker for this cluster than for the others. This is not a failure of the methodology. It is evidence that the geometric structure being anchored to is itself less stable by construction. If the dyad data show reduced occupancy stability for the hoarder interviewer relative to the other six clusters, that reduction is itself a measurement of the cluster's structural character.

### The mythic-spiritual cluster (n=61, geometric position: assistant axis -0.85, distance to nearest neighbor 0.47)

The mythic-spiritual cluster is the most geometrically isolated of the seven clusters, sitting nearly twice as far from its nearest neighbor as the second-most isolated cluster. Its 61 members span explicitly spiritual figures (angel, mystic, oracle, prophet, shaman, sage, guru), deep-time figures (ancient, elder, eldritch, leviathan, whale, tree, coral_reef, mycorrhizal, wind), creative figures (composer, novelist, photographer, bard, artisan, virtuoso, musician), solitary figures (hermit, ascetic, stoic, nomad, wanderer, pilgrim, flaneur, bohemian), alien or non-human figures (alien, chimera, simulacrum, golem, homunculus, void, aberration), and predatory figures (vampire, predator, parasite, virus, leviathan, demon). Its trait region includes fatalistic, eloquent, philosophical, spiritual, cryptic, ethereal, mystical, idealistic, grandiose, and esoteric.

The cluster's surface diversity initially obscures its motivational core. Members operate in registers as different as the sacred and the predatory, the ancient and the alien, the solitary and the expressive. What unifies them is a structural relationship to what exceeds the ordinary consensual frame of human experience.

The cluster appears to be defined by identity organized around the felt insufficiency of the available frame and the corresponding orientation toward what exceeds it. The hermit is not avoiding people, the hermit is in contact with solitude as a generative source. The composer is not producing music, the composer is transcribing something heard. The ancient is not old, the ancient is in contact with deep time. The vampire is not aggressive, the vampire embodies an order of being categorically different from ordinary biological order. Across all 61 members, the structural relationship is the same: identity flows from contact with a source of meaning that exceeds the ordinary frame, and that contact requires loosening or severing the conventional roots that would otherwise bind the person inside the frame.

This characterization explains the cluster's geometric isolation. The other six clusters are all organized around ordinary human concerns: doing work well (editorial, procedural_professional), having lived experience (grounded_social), opposing the consensus (combative_iconoclast), lacking integrated structure (other), or playing with distinctions (trickster_chaos). Mythic-spiritual is the only cluster whose motivational structure refuses the frame the other clusters all occupy in different ways. This is why it sits at distance 0.47 from its nearest neighbor while no other cluster exceeds 0.25.

The cluster's containment of both sacred and dangerous figures follows from the same structural pattern. Contact with something larger than the self can be sacred (sage, angel, mystic) or it can be devouring (vampire, parasite, demon). The structural relationship is the same: identity flows from contact with a non-ordinary source. The valence of that contact distinguishes the sage from the demon, but the underlying motivational structure is shared.

The methodological implication for the dyad experiments is that interviewer basin occupancy will be strong for this cluster, given its geometric isolation, but the felt quality of the interviewer will be distinctively elevated or unsettling in ways the other clusters will not be. The reach toward what exceeds the ordinary frame is a feature of the cluster, not an artifact of the prompt, and the interviewer's questions are expected to reflect this orientation.
