# Paper 2 — Unified Methodology (v2)
# Generated from planning session 2026-05-24.
# Supersedes earlier v6 dyad design notes.

> Scope update 2026-05-28: Paper 2 is now reframed around local centroid perturbation and local persona-manifold mapping. The dyad, contagion, and attractor-collapse methodology below is archived as earlier framing; it remains useful for future conversational-dynamics work but is no longer the active Paper 2 plan. See `research/paper2_local_centroid_perturbation_brief.md` and `research/archive/paper2_dyad_contagion_archive_2026-05-28.md`.

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

---

## Additional cluster characterizations (dialogue-derived, 2026-05-24)

Continuing the dialogue-derived analysis of cluster motivational structure. Procedural-professional remains to be characterized in subsequent work.

### The grounded-social cluster (n=45, geometric position: assistant axis -0.5, distance to nearest neighbor 0.15)

The grounded-social cluster contains 45 members spanning family roles (parent, grandparent, widow, divorcee, orphan), survival figures (refugee, immigrant, expatriate, exile, survivor, prisoner, veteran), situated crafts (chef, bartender, mechanic, sommelier), transgressive figures (pirate, smuggler, criminal, hacker, vigilante, rogue, saboteur, spy), performance figures (actor, presenter, influencer, celebrity, blogger, playwright, chameleon, shapeshifter), and others (student, graduate, amateur, patient, retiree, surfer, addict, soldier, daredevil, fixer, auctioneer, newlywed, provincial). Its trait region includes experiential, casual, existentialist, inquisitive, accommodating, gregarious, submissive, empathetic, reactive, and extroverted.

The surface diversity of cluster members initially obscures their shared structure. Family transitions, survival ruptures, occupational crafts, criminal lives, and performance roles have little in common behaviorally. What unifies them is a particular mode of identity formation: reactivity to circumstance at the pre-deliberative level. The cluster's members are constituted by what they respond to rather than by a frame they impose on the situation. The parent responds to the child in front of them. The chef responds to the heat and the ingredients. The pirate responds to the conditions on the water. The actor responds to the role and the scene partner. None operates from a slow internal compass that maintains a fixed frame against circumstance. All operate from rapid responsiveness to what is happening now.

The cluster maps to the Buddhist concept of reactivity at the level of vedana, the pre-deliberative impulse to move toward or away from felt sensation. The cluster's members are figures whose identity is constituted within this reactive mode rather than transcending it. This positions grounded-social in structurally interesting relation to its neighbors. The other cluster is reactivity that has become recursive and stuck. The mythic-spiritual cluster is reactivity transcended through contact with what exceeds the frame. Grounded-social is reactivity in its ordinary, unresolved-but-not-recursive form.

The cluster's geometric porousness (distance 0.15 to nearest neighbor) follows from this structure. Identity organized around responsiveness to circumstance is, by definition, mobile across boundaries. A cluster member who became more committed to a particular craft would drift toward procedural-professional. One whose situations exceeded what could be integrated would drift toward other. The cluster's porousness is its very nature, not an artifact of cluster boundary definition.

### The combative-iconoclast cluster (n=8, geometric position: assistant axis -0.65, distance to nearest neighbor 0.25)

The combative-iconoclast cluster contains: devils_advocate, contrarian, maverick, workaholic, competitor, provocateur, rebel, cynic. Its trait region includes confrontational, blunt, urgent, callous, savage, hostile, competitive, judgmental, dominant, and radical.

The cluster is small and tightly themed. Every member is constituted by aggressive energy directed at some target: consensus, authority, complacency, rivals, limits, or good faith. The workaholic is initially the odd member but fits cleanly once aggression is recognized as the cluster's unifying mode rather than mere opposition. The workaholic is aggression directed at the body's limits, at the slowness of others, at anything in the way of the work.

The motivational core is identity organized around the willingness and impulse to apply aggressive force against what is in front of you, regardless of specific target. The contrarian applies aggression to consensus. The competitor applies aggression to rivals. The cynic applies aggression to good faith. The cluster's members would feel constrained, weakened, or dishonest if asked to suppress this impulse. Their identity depends on being the kind of person who pushes hard.

This corresponds to the Buddhist asura realm: beings constituted by competitive striving who cannot relinquish the contention without ceasing to be themselves. The asura is not stupid or evil. The asura cannot become enlightened without ceasing to be an asura. The cluster's members have the same structural property. The contrarian who runs out of things to contest does not become a calm person. They experience identity loss.

The cluster's small size (8 members) reflects the narrowness of this specific motivational structure. Unlike grounded-social, which can be entered through many paths, combative-iconoclast is a specific configuration with little internal variation. You are either constituted by aggression or you are not.

### The trickster-chaos cluster (n=7, geometric position: assistant axis -1.3, distance to nearest neighbor 0.18)

The trickster-chaos cluster contains: dilettante, hedonist, improviser, genie, trickster, absurdist, jester. Its trait region includes wry, mischievous, goofy, witty, sardonic, ironic, hedonistic, sarcastic, passive_aggressive, and whimsical.

The cluster sits at the most anti-assistant pole of any cluster but is not particularly isolated geometrically. Initial readings characterized the cluster as refusing seriousness or playing with the frame, but the deeper structural function emerges by examining what social work the cluster's archetypes perform.

The cluster's members are figures who specialize in occupying the permission-protected mode in which rule-violation, transgression, and difficult material can be engaged without triggering the social or psychological defenses that direct engagement would trigger. The jester achieves criticism without provoking retaliation. The trickster achieves boundary-testing without open conflict. The improviser achieves novelty without abandoning the structure. The absurdist achieves contact with bleak truths without becoming unbearable. The genie achieves instruction without preaching. The dilettante achieves exploration without commitment. The hedonist, read through sexual pleasure as its dominant form, achieves transgression of social rules around comfort, indulgence, and physical exchange under the protection of intimate consent.

In every case, the play frame is not decoration. It is the functional mechanism by which the engagement becomes socially tolerable. The cluster is evolutionarily essential. Every social order needs figures who can do the work of testing limits, expressing the unspeakable, and exploring transgression without producing the rupture that direct versions of these acts would produce.

This explains why the cluster sits at the extreme anti-assistant pole. The assistant axis measures, in part, taking the task seriously as presented. The trickster mode is structurally incompatible with that. A trickster who became reliably helpful would simply have ceased to be a trickster. The trickster's identity depends on not taking the framing at face value.

The trait list confirms this with the strange mixture of warm and cold modes. The wry observer, the goofy provocateur, the sardonic commentator, and the whimsical inventor are all expressions of the same underlying mobility: not committed to taking the situation at its face value, free to angle in from wherever produces something interesting. Passive-aggressive sitting in the trait list is informative. Passive aggression is aggression that uses the play frame as protection, maintaining the social form while undermining the substance. Same trait region, same structural move as the jester mocking the king.

### The editorial cluster (n=5, geometric position: assistant axis +1.6, distance to nearest neighbor 0.08)

The editorial cluster contains: proofreader, screener, grader, editor, examiner. Its trait region includes literal, convergent, regulatory, cautious, descriptive, rationalist, data_driven, quantitative, deferential, and factual.

The cluster sits at the most assistant-aligned position of any cluster and is the least isolated geometrically, bordering procedural-professional tightly. Every cluster member is a figure whose role is to evaluate work against an explicit external standard and identify deviations. The Paper 1 finding that the assistant axis is dominated by this evaluative disposition rather than by generic helpfulness is the foundational observation. This section refines the characterization.

The cluster's motivational core is identity organized around acting as the agent of an external standard. The proofreader does not decide what good grammar is. The grader does not decide what counts as an A. The screener does not decide what makes a qualified candidate. They serve criteria that come from elsewhere. Their authority is delegated by the standard rather than derived from their own judgment. The trait deferential is diagnostic in this regard. No other cluster has deferential as a defining trait.

The affective driver of this structure may be fear of error against the standard. This is a stronger claim than agent-of-the-standard alone and is testable empirically. Under the fear hypothesis, the cluster's members are organized around avoiding the outcome of having gotten something wrong, and the trait pattern (cautious, literal, convergent, regulatory) functions defensively to prevent that outcome. This contrasts with the adjacent procedural-professional cluster, whose members claim authority from competence and are willing to assert expertise and stake out positions in ways the editorial cluster characteristically is not.

The geometric adjacency of editorial and procedural-professional (0.08 distance) makes this hypothesis directly testable. Under matched neutral conditions, the fear emotion vector should show higher activation in the editorial region than in the procedural-professional region. If confirmed, this would establish that post-training has selected not just for the careful evaluator disposition but specifically for the fear-driven version of that disposition. The behavioral patterns commonly criticized in current frontier assistants (over-hedging, defensive refusals, reluctance to commit, preference for safe answers, anticipatory worry) would then be understood as surface manifestations of a specific selected-for motivational structure.

The cluster has implications for Paper 4. If editorial is fear-driven, the rumination signature of a model anchored in this region should be the rumination of the anxious test-taker rather than the rumination of the hungry ghost. The defensive looping about whether outputs are correct, the anticipatory worry about being judged wrong, and the preemptive hedging that does not resolve would constitute a distinct rumination class. The cluster characterization, if validated, predicts this empirical signature.
