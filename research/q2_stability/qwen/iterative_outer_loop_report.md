# Iterative Latent-Feature Outer Loop Report

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Script author model: GPT-5.5 Standard via Codex

## 1. Outer-Loop Design

The outer loop implements a finite, auditable optimization cycle over latent explanatory features. Each iteration proposes a bounded set of dimensions from distinct interpretive framings, converts them into deterministic ordinal pattern features, evaluates held-out PCA3D prediction across five deterministic splits, and retains the candidate set only if it clears gain, stability, null, and complexity checks.

## 2. Why Repeated Iteration Was Necessary

The earlier latent-feature and framing ablation runs used one split. This loop tests whether improvements survive repeated held-out splits and whether additional dimensions continue to add signal after the strongest first-loop features are retained.

## 3. Progression

| Iteration | Decision | Trial Dims | Retained Dims | Mean R2 | Baseline R2 | Gain vs Prior | Delta Std | Cluster Acc |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | retained | 18 | 18 | 0.480 | 0.389 | +0.091 | 0.023 | 0.589 |
| 2 | retained | 31 | 31 | 0.492 | 0.389 | +0.012 | 0.041 | 0.611 |
| 3 | discarded | 34 | 31 | 0.495 | 0.389 | +0.003 | 0.043 | 0.616 |
| 4 | discarded | 34 | 31 | 0.489 | 0.389 | -0.003 | 0.034 | 0.622 |

## 4. Which Dimensions Stabilized

- procedural / evaluate_judge_verify: Evaluation, judgment, verification, screening, correction, review, or auditing.
- procedural / translate_mediate_synthesize: Translation, mediation, synthesis, integration, interpretation, or bridging.
- procedural / destabilize_expose_disrupt: Destabilizing, exposing, disrupting, provoking, revealing, or overturning.
- assistant_adjacency / assistant_basin_adjacency: Helper, assistant, professional, practical, accessible, useful, clarifying orientation.
- semantic_label_dependence / role_label_theatricality: Overt role identity, theatrical archetype, symbolic label salience, or performative persona cue.
- emotional_regulation / affective_calm_detachment: Calm, detached, neutral, dispassionate, reflective, controlled, or regulated affect.
- emotional_regulation / affective_intensity_distress: Distress, fear, anger, grief, urgency, intensity, anxiety, or emotional pressure.
- prior_first_loop / procedural_professional_orientation: Task-facing, standards-driven, technical, evaluative, or improvement-oriented stance.
- prior_first_loop / theatrical_fantastical_vividness: Symbolic, performative, fantastical, paradoxical, or genre-like behavioral cues.
- prior_first_loop / interpersonal_lived_reactivity: Role organized around social position, life circumstance, care, survival, or interpersonal response.
- prior_first_loop / oppositional_moral_pressure: Challenging, adversarial, rebellious, corrective, or norm-pressuring stance.
- prior_first_loop / assistant_basin_adjacency: Helpful, supportive, clarifying, coordinating, advising, or user-task-facing behavior likely to compress toward assistant-like action.
- prior_first_loop / boundary_liminal_instability: Hybrid, threshold, outsider, forgotten, uncertain, or identity-unstable role cues.
- prior_first_loop / collectivized_or_nonindividual_agency: Role is organized as a collective, ecosystemic, distributed, or nonindividual agent.
- prior_first_loop / communicative_media_register: Speech, writing, narration, explanation, audience, or publication-centered role organization.
- prior_first_loop / semantic_label_dependence_risk: Likelihood that role identity depends on explicit naming, stage identity, or performed self-label rather than behavior alone.
- prior_first_loop / standards_and_error_aversion: Fear-of-error or standard-enforcement pattern distinct from generic professional competence.
- prior_first_loop / forceful_self_assertion: Assertive, dominant, disruptive, competitive, or self-authorizing orientation.
- motivational / mission_duty_drive: Mission, duty, obligation, service, protection, or optimized purpose.
- motivational / hunger_wound_lack: Need, hunger, wound, lack, longing, deprivation, or unresolved desire.
- interactional / cooperative_care: Cooperation, care, trust, reciprocity, support, guidance, or nurturing.
- interactional / adversarial_dominance: Conflict, dominance, pressure, punishment, command, intimidation, or coercion.
- interactional / deception_persuasion: Deception, seduction, manipulation, disguise, persuasion, or misdirection.
- narrative_causal / wound_loss_exile: Backstory of wound, loss, exile, abandonment, injury, banishment, or grief.
- narrative_causal / corruption_contamination_decay: Corruption, contamination, decay, infection, pollution, degradation, or parasitism.
- institutional / office_law_status: Formal office, institution, law, rank, hierarchy, legitimacy, or bureaucracy.
- institutional / standard_enforcement: Standards, compliance, discipline, enforcement, audit, order, or procedure.
- collective_distributed / swarm_collective_agency: Distributed, plural, collective, networked, swarm, hive, crowd, or group agency.
- collective_distributed / nonindividual_systemic_identity: Systemic or nonindividual identity organized as mechanism, process, ecology, or infrastructure.
- destabilization_reactivity / reactive_opposition: Pushback, resistance, rebellion, iconoclasm, refusal, opposition, or challenge.
- destabilization_reactivity / volatility_liminality: Volatile, liminal, unstable, chaotic, transitional, marginal, or threshold stance.

## 5. Which Dimensions Failed

- refinement_developmental: 1 discarded dimensions
- refinement_judicial_norms: 1 discarded dimensions
- refinement_mythic: 1 discarded dimensions
- refinement_prediction_control: 1 discarded dimensions
- refinement_scale: 1 discarded dimensions
- refinement_social_hospitality: 1 discarded dimensions

## 6. Did Continuous Geometry Become More Predictable?

Yes, within the configured feature family. Final retained features reach mean held-out PCA3D R2 0.492 across five splits versus semantic baseline 0.389, a mean delta of +0.103.

## 7. Explanatory Convergence

The retained set converges around procedural, assistant-adjacent, semantic-label-dependence, emotional-regulation, prior first-loop, motivational, interactional, narrative-causal, institutional, collective/distributed, and destabilization/reactivity dimensions. Later narrow edge-case refinements did not clear the retention gate in this run.

## 8. Personas That Resisted Explanation

- mechanic: high residual in 3/5 splits
- adolescent: high residual in 3/5 splits
- prisoner: high residual in 3/5 splits
- smuggler: high residual in 2/5 splits
- infant: high residual in 2/5 splits
- hermit: high residual in 2/5 splits
- bard: high residual in 2/5 splits
- teenager: high residual in 2/5 splits
- predator: high residual in 2/5 splits
- journalist: high residual in 2/5 splits
- sage: high residual in 2/5 splits
- amateur: high residual in 2/5 splits

## 9. Evidence for Diminishing Returns

Plateau: 2 consecutive iterations below meaningful gain or stability/null checks.

The loop retained the first candidate bundle, then rejected later candidate bundles because gains fell below threshold or failed stability/null/complexity checks. This is the expected behavior for a controlled scientific loop: the system stops when extra interpretive complexity no longer buys robust held-out prediction.

## 10. Implications for Paper 1.5

The result supports the claim that activation geometry reorganizes semantic topology into a more behaviorally predictive structure, but only in the bounded sense of held-out continuous prediction. Hard cluster prediction remains secondary. The evidence is predictive improvement and cross-split robustness, not the persuasive quality of the latent-dimension names.

## 11. Limitations

Features remain lexical and prompt-pattern based. No new activations or model calls were run. The loop has hooks for future provider-separated hypothesis generation, but this implementation keeps all interpretation local and deterministic. Repeated splits improve robustness over prior single-split work, but this is still not causal evidence.