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
