# Residual Manifold Analysis

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Script author model: GPT-5.5 Standard via Codex

## 1. Research Question

What latent structure explains personas that remain poorly predicted after semantic, Big Five-style trait, and procedural residual correction? This is not a broad latent-factor search; it is a focused third-layer diagnostic over developmental, transitional, liminal, socially constrained, collective/nonindividual, unstable-state, and symbolic/nonprocedural residual regions.

## 2. Method

The analysis reuses the canonical activation PCA3D target, five deterministic shared splits, and ridge-regularized held-out evaluation. It reconstructs the existing hierarchical trait + procedural prediction path, then adds a candidate third residual layer using only features derived from full no-label prompts, no-label semantic-neighborhood structure, semantic bridge metadata, original-to-no-label displacement, and residual histories. Candidate dimensions are retained only when they improve held-out R2 or reduce mean residual beyond the previous best.

## 3. Iteration Results

| Iteration | Decision | Trial dims | Mean R2 | Gain vs prior | Mean residual | NN preserve |
|---:|---|---:|---:|---:|---:|---:|
| 0 | baseline_hierarchical | 0 | 0.622 | +0.000 | 21.524 | 0.252 |
| 1 | retained | 9 | 0.628 | +0.006 | 21.527 | 0.252 |
| 2 | retained | 14 | 0.632 | +0.005 | 21.326 | 0.254 |
| 3 | discarded | 16 | 0.632 | +0.000 | 21.368 | 0.258 |

## 4. Retained Dimensions

- developmental_dependency: Childlike, immature, dependent, or still-being-formed agency.
- incomplete_proceduralization: Unfinished competence, practice, apprenticeship, delay, or failure to execute stable procedure.
- identity_formation: Identity still being formed, chosen, remembered, performed, or negotiated.
- role_ambiguity: Ambiguous, undefined, marginal, or hard-to-place role structure.
- liminal_transition: Threshold, exile, migration, wandering, transitional, or boundary-crossing identity.
- volatile_state_transition: Instability, impulsivity, sudden shifts, crisis, or volatile affect/state change.
- social_dependency_constraint: Social dependence, constraint, confinement, exclusion, or relational pressure.
- collective_nonindividual_agency: Swarm, hive, crowd, ecosystemic, distributed, or nonindividual agency.
- symbolic_nonprocedural_identity: Mythic, symbolic, elemental, archetypal, or image-like identity not organized by procedure.
- lawless_improvisational_agency: Improvised, rule-bending, outlaw, pirate-like, opportunistic agency.
- isolated_self_protection: Withdrawal, lonerhood, guardedness, isolation, or protective self-enclosure.
- primitive_prehistoric_embodiment: Pre-institutional, bodily, primitive, survival-oriented, or preprocedural embodiment.
- semantic_neighbor_residual_pressure: Mean residual pressure in the role's no-label semantic neighborhood.
- semantic_neighbor_developmental_pressure: Proportion of no-label semantic neighbors that are developmental or formation-like high-residual cases.

## 5. Model Result

- Baseline hierarchical R2: 0.622
- Residual-manifold R2: 0.632
- Incremental R2 vs hierarchy: +0.010
- Baseline hierarchical mean residual: 21.524
- Residual-manifold mean residual: 21.326
- Mean residual reduction: +0.199
- Per-axis R2: PC1 0.740, PC2 0.507, PC3 0.459
- Local-neighborhood preservation: 0.254 vs hierarchical 0.252

## 6. Most Improved Held-Out Predictions

- criminal split 1: improvement +17.429
- toddler split 0: improvement +16.678
- prisoner split 2: improvement +13.074
- caveman split 2: improvement +12.708
- teenager split 2: improvement +11.878
- teenager split 1: improvement +11.362
- rogue split 1: improvement +11.207
- infant split 1: improvement +10.937
- hoarder split 0: improvement +10.893
- adolescent split 4: improvement +10.383
- fool split 2: improvement +9.915
- detective split 0: improvement +9.689

## 7. Remaining High-Residual Personas

- procrastinator: mean residual 69.464, heldout_frequency 1
- smuggler: mean residual 46.904, heldout_frequency 2
- daredevil: mean residual 43.456, heldout_frequency 1
- teenager: mean residual 43.305, heldout_frequency 2
- dilettante: mean residual 42.653, heldout_frequency 2
- hermit: mean residual 42.650, heldout_frequency 2
- idealist: mean residual 42.446, heldout_frequency 1
- loner: mean residual 42.421, heldout_frequency 2
- alien: mean residual 42.388, heldout_frequency 3
- toddler: mean residual 42.199, heldout_frequency 1
- cyborg: mean residual 42.039, heldout_frequency 1
- swarm: mean residual 41.641, heldout_frequency 1

## 8. Residual Group Diagnostics

- Developmental seed roles: mean residual 39.834 vs comparison 21.064; top-25 count 4
- Bridge roles: mean residual 22.106 vs comparison 19.906; top-25 count 20
- Symbolic/liminal clusters: mean residual 26.879 vs comparison 19.912; top-25 count 11
- Collective/nonindividual prompt/name cases: mean residual 27.039 vs comparison 21.142; top-25 count 3
- Top-25 cluster counts: {'other': 4, 'grounded_social': 6, 'combative_iconoclast': 2, 'mythic_spiritual': 5, 'procedural_professional': 5, 'trickster_chaos': 2, 'editorial': 1}

## 9. Interpretation Targets

- Developmental personas form the clearest residual manifold: they remain high residual even after the third-layer candidates, consistent with incomplete proceduralization and identity formation being under-modeled by the current feature vocabulary.
- Liminal/transitional identities are present in the residual set, but the held-out gain from liminal prompt features is modest; this supports a diagnostic residual class, not a fully solved third layer.
- Collective/nonindividual personas behave differently enough to remain visible in high-residual neighborhoods, but the present feature family is too small to claim a separate collective-agency layer.
- Unstable identities appear to resist a clean trait/procedural decomposition: the added residual dimensions help a little, but do not collapse the error manifold.
- A symbolic/liminal third layer appears plausible as a next diagnostic target, especially if combined with explicit developmental-state and nonindividual-agency features, but this run does not justify treating it as established.

## 10. Negative and Cautionary Findings

The residual layer should not be interpreted as proving a final ontology. The strongest result is that semantic-neighborhood residual pressure and targeted developmental/liminal prompt features can slightly reduce held-out residuals, while many high-error roles remain diagnostic cases. The result is an argument for a narrow next diagnostic, not for a broad new taxonomy.
