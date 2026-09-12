# AA-8 Analysis Specification

Date frozen: 2026-09-12

Model used for interpretive synthesis: GPT-5.5

## Scope

AA-8 reinterprets Qwen PC1 and PC2 as whole bipolar axes and revisits their available SAPA measurement analogues. It does not rerun, retune, or replace either completed specificity analysis. It does not score human respondents, project humans into Qwen geometry, compare Qwen with another model, use AA-7 alignment to choose an interpretation, or select a next experiment.

PC3 remains outside selection and remapping scope. Its documented Affiliation composite is used only as a reference example of a comparatively clean bipolar bridge.

## Frozen model-side evidence hierarchy

1. PC-associated: 328 signed memberships from AA-1.
2. PC-defining / target-dominant: 202 memberships at source commit `db782414c6708f6fd2c46f3e5b08d0e61668b14d`.
3. Strict axis-specific: 88 memberships passing the frozen six-PC purity threshold of .70 at source commit `6497d28383aac33ea9f61b6ce2ac2ff195dccae4`.
4. Highly concentrated: 70 memberships from the target-dominance analysis with observed PC1-PC6 concentration at least .75.

Interpretation prioritizes levels 3 and 4, uses level 2 as supporting context, and uses level 1 only as broad context. Differences between levels are treated as different specificity resolutions, not contradictory results.

## Frozen PC2 coordinate-blind diagnostic

The coordinate-blind source contains only role names and the five positive role-conditioning instructions. Coordinates, ranks, clusters, existing axis interpretations, trait correlations, and specificity outcomes are excluded until ratings are committed.

Five dimensions are rated separately on the ordinal 1-5 anchors in `pc2_coordinate_blind_role_rating_rubric.md`:

- embodied physical engagement
- practical concrete engagement
- social outward engagement
- abstract conceptual engagement
- ritual formal mediation

The primary diagnostic is descriptive Pearson and Spearman association with PC2. PC1 and PC3 are controls. A partial PC2 association controlling PC1 is reported. The incremental contribution of embodied physical engagement beyond practical/concrete and social/outward engagement is evaluated by nested ordinary least squares. These analyses are interpretive diagnostics, not independent validation.

## Frozen bipolar human-match rubric

Every serious human candidate is assessed separately on marker-pole coverage, opposite-pole coherence, coverage of highly concentrated and strict markers, role/persona coherence, prior model-side evidence, human construct-definition fit, item-content fit, contradictions, and model-specific residuals. No opaque aggregate score is computed.

Allowed overall judgments:

- `STRONG_BIPOLAR_MATCH`
- `PLAUSIBLE_BIPOLAR_MATCH`
- `PARTIAL_COMPONENT`
- `WEAK_OR_NONSPECIFIC`
- `POOR_MATCH`
- `NO_DIRECT_HUMAN_MEASURE`

Single questionnaire items are labeled `ITEM_LEVEL_EVIDENCE_ONLY` and are never promoted to validated construct status.

## Epistemic labels

- Observed: saved marker metrics, role geometry, prior completed model-side results, construct definitions, item availability, and the frozen coordinate-blind role ratings.
- Interpretation: bipolar semantic descriptions and proposed human measurement analogues.
- Hypothesis: PC1 as procedural/external-standard disciplined cognition; PC2 as containing embodied/experiential engagement; any shared latent property between a SAPA construct and a Qwen PC.
- Unknown: respondent correspondence, causal mechanism, behavioral realization, and cross-model generalization.

