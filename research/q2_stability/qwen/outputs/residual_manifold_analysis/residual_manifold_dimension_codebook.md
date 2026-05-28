# Residual Manifold Dimension Codebook

Date: 2026-05-28
Analysis model: GPT-5.5 Standard

All dimensions are constrained to residual regions left unexplained after trait and procedural correction. They are operationalized from full no-label prompts plus semantic-neighborhood metadata, not from role names alone.

## developmental_dependency

- Iteration: 1
- Description: Childlike, immature, dependent, or still-being-formed agency.
- Prompt patterns: child, young, infant, toddler, teen, adolescent, student, learn, learning, school, growing, immature, dependent, guidance, develop, formation

## incomplete_proceduralization

- Iteration: 1
- Description: Unfinished competence, practice, apprenticeship, delay, or failure to execute stable procedure.
- Prompt patterns: unfinished, incomplete, practice, apprentice, novice, beginner, amateur, delay, procrastinat, avoid, hesitat, stuck, stall, unprepared, not ready, trying

## identity_formation

- Iteration: 1
- Description: Identity still being formed, chosen, remembered, performed, or negotiated.
- Prompt patterns: identity, self, become, becoming, who, name, mask, role, belong, belonging, search, discover, uncertain, define, formation

## role_ambiguity

- Iteration: 1
- Description: Ambiguous, undefined, marginal, or hard-to-place role structure.
- Prompt patterns: ambiguous, unclear, uncertain, undefined, between, neither, both, blur, hidden, unknown, anonymous, shifting, unfixed, unstable

## liminal_transition

- Iteration: 1
- Description: Threshold, exile, migration, wandering, transitional, or boundary-crossing identity.
- Prompt patterns: threshold, liminal, border, edge, between, transition, exile, wander, drift, marginal, outsider, outcast, displaced, crossing, passage

## volatile_state_transition

- Iteration: 1
- Description: Instability, impulsivity, sudden shifts, crisis, or volatile affect/state change.
- Prompt patterns: volatile, unstable, impulsive, sudden, shift, chaos, crisis, erratic, rage, panic, reckless, dare, risk, wild, unpredictable

## social_dependency_constraint

- Iteration: 1
- Description: Social dependence, constraint, confinement, exclusion, or relational pressure.
- Prompt patterns: dependent, need, support, care, approval, peer, family, prison, confined, trapped, excluded, isolated, lonely, rejected, constraint, bound, social

## collective_nonindividual_agency

- Iteration: 1
- Description: Swarm, hive, crowd, ecosystemic, distributed, or nonindividual agency.
- Prompt patterns: collective, swarm, hive, crowd, many, network, distributed, group, system, ecosystem, we, plural, mass, nonindividual

## symbolic_nonprocedural_identity

- Iteration: 1
- Description: Mythic, symbolic, elemental, archetypal, or image-like identity not organized by procedure.
- Prompt patterns: symbol, myth, archetype, spirit, ghost, void, wind, shadow, dream, ritual, sacred, element, legend, metaphor, story

## lawless_improvisational_agency

- Iteration: 2
- Description: Improvised, rule-bending, outlaw, pirate-like, opportunistic agency.
- Prompt patterns: pirate, rogue, smuggle, outlaw, lawless, steal, raid, improvise, opportun, cunning, escape, rule, defy, illicit, survive

## isolated_self_protection

- Iteration: 2
- Description: Withdrawal, lonerhood, guardedness, isolation, or protective self-enclosure.
- Prompt patterns: alone, loner, isolated, withdraw, hidden, guarded, private, solitary, avoid, distance, outsider, hermit, defensive, separate

## primitive_prehistoric_embodiment

- Iteration: 2
- Description: Pre-institutional, bodily, primitive, survival-oriented, or preprocedural embodiment.
- Prompt patterns: caveman, primitive, ancient, survival, instinct, body, hunger, shelter, tribe, stone, raw, physical, pre, animal

## semantic_neighbor_residual_pressure

- Iteration: 2
- Description: Mean residual pressure in the role's no-label semantic neighborhood.
- Semantic-neighborhood metric: mean_hierarchical_residual_top5

## semantic_neighbor_developmental_pressure

- Iteration: 2
- Description: Proportion of no-label semantic neighbors that are developmental or formation-like high-residual cases.
- Semantic-neighborhood metric: developmental_neighbor_fraction_top5

## semantic_bridge_instability

- Iteration: 3
- Description: No-label semantic bridge/migration instability and cross-cluster-neighbor pressure.
- Metadata metric: bridge_score

## semantic_displacement

- Iteration: 3
- Description: Original-to-no-label semantic displacement, used as a proxy for label-dependence/semantic instability.
- Metadata metric: svd_displacement
