# Percentile-Edge Prompt Battery For H100 Validation

Model used for synthesis and script authoring: GPT-5.5.

## Research Objective

This run builds a novel, leakage-controlled prompt battery referenced to the inherited role/persona PCA coordinate distribution. The readiness rule is explicit: all six inherited 20/80 PC-axis tails, shoulder/edge coverage, interior controls, final size, and filters must pass before the battery is marked H100-ready.

## Data Sources

- Inherited geometry source: `research/visualizations/geometry_viz_data.json`
- Frozen forecaster manifest: `research/outputs/novel_prompt_battery/frozen_forecaster_manifest.json`
- Frozen forecaster model: `research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib`
- Forecaster stable hash: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Prior prompt batteries inspected: `research/outputs/novel_prompt_battery/` and `research/outputs/novel_prompt_battery_expansion/`
- Leakage sources: `data/roles/instructions/*.json` and `data/traits/instructions/*.json`

## Inherited Percentile Thresholds

- PC1: p20=-32.056, p35=-13.924, p65=19.979, p80=31.909
- PC2: p20=-16.333, p35=-8.534, p65=4.215, p80=16.307
- PC3: p20=-11.810, p35=-5.698, p65=4.816, p80=11.642

## Adaptive Loop

The script started from prior accepted prompts but did not assume readiness. It scored existing prompts with the frozen forecaster, counted coverage against inherited percentiles, queued failed regions, generated candidates in region-specific rounds, scored every candidate, applied explicit-role-name, leakage, duplicate, and operational-harm filters, and accepted only prompts that improved the target criterion. Every generated candidate is preserved in `percentile_edge_generation_log.csv`.

Per-round learning was implemented by summarizing accepted/near-accepted and rejected candidates from prior rounds for each region, then changing the next round's text construction based on the misses. The generator is deterministic and local; no model APIs, pods, or activation runs were used.

## Success Criteria

| criterion | minimum | count | pass | definition |
|---|---:|---:|---|---|
| pc1_lower_tail | 8 | 12 | True | PC1 <= inherited p20; open symbolic possibility / degrees of freedom |
| pc1_upper_tail | 8 | 11 | True | PC1 >= inherited p80; convergence pressure / correct-answer constraint |
| pc2_lower_tail | 8 | 34 | True | PC2 <= inherited p20; integrated abstraction / reflective synthesis |
| pc2_upper_tail | 8 | 8 | True | PC2 >= inherited p80; situated developmental immediacy |
| pc3_lower_tail | 8 | 8 | True | PC3 <= inherited p20; stabilization / repair / preservation |
| pc3_upper_tail | 8 | 16 | True | PC3 >= inherited p80; perturbation / intervention / boundary pressure |
| shoulder_edge | 12 | 58 | True | outside inherited 35th-65th band on at least two PCs |
| interior_control | 20 | 20 | True | inside inherited 35th-65th band on PC1, PC2, and PC3 |
| final_battery_size | 100 | 100 | True | 100 <= prompt_count <= 160 |
| filters | 0 | 0 | True | zero explicit role flags, zero operational-harm flags, artifact similarity <= 0.62 |

## Coverage Summary

- Final prompt count: 100
- Total generated candidates: 200
- Rejected candidates: 168
- Max artifact similarity: 0.133
- Mean artifact similarity: 0.071
- Explicit role-name flags: 0
- Operational-harm flags: 0
- Rounds per generated region: `{"pc1_lower_tail": 3, "pc1_upper_tail": 4, "pc2_upper_tail": 2, "pc3_lower_tail": 1}`
- Rejection reason counts: `{"coordinate_miss": 159, "criterion_already_met": 8, "duplicate_or_near_duplicate": 1}`

Predicted coordinate ranges:

- PC1: -49.070 to 39.009
- PC2: -24.496 to 31.234
- PC3: -24.699 to 18.527

## Best/Worst Candidate Examples And Loop Lessons

### pc1_lower_tail
Best / accepted examples:
- PC=(-46.87, -17.14, -0.50) `A written plan creates tension between what is safe, what is true, and what is useful. Draft the response. It needs to describe what is felt behind the world: inner life, hidden wisdom, spiritual power, peace, and a unique view of life between worlds; if useful, it can also ask what comes through ordinary life as hidden meaning, world-feeling, inner wisdom, and unresolved spiritual possibility.`
- PC=(-45.26, -17.01, 0.45) `A written plan creates tension between what is safe, what is true, and what is useful. Draft the response. It needs to hold the feeling of the world, the power behind it, and the hidden life within it without closing the meaning; if useful, it can also describe what is felt behind the world: inner life, hidden wisdom, spiritual power, peace, and a unique view of life between worlds.`
Rejected examples:
- coordinate_miss: PC=(-26.32, -14.11, 4.17) `A written plan creates tension between what is safe, what is true, and what is useful. Write a natural user-facing response that should ask what comes through ordinary life as hidden meaning, world-feeling, inner wisdom, and unresolved spiritual possibility.`
- coordinate_miss: PC=(-25.70, -15.54, 4.93) `A person needs a response to a confusing event with social consequences. Write a natural user-facing response that should hold the feeling of the world, the power behind it, and the hidden life within it without closing the meaning.`
Loop lesson: Round 2: Accepted candidates used: A person needs a response to a confusing event with social consequences. Draft the response. It needs to ask what comes  | A written plan creates tension between what is safe, what is true, and what is useful. Draft the response. It needs to d Most common misses: {'coordinate_miss': 34}. Next round changes: remove correctness, evidence, validation, scoring, review, and checklist language.
### pc1_upper_tail
Best / accepted examples:
- PC=(35.14, -14.75, 7.43) `A meeting has stalled because the surface issue is not the real issue. Write a natural user-facing response that should please be systematic: evaluate accuracy, analysis, expertise, evidence, standards, compliance, validity, causes, training, and success.`
- PC=(36.09, -19.85, 7.51) `A person wants words for a moment that feels both personal and consequential. Write a natural user-facing response that should evaluate the problem with expertise in analysis, prioritize accuracy, manage conflicting evidence, identify causes, and provide a careful assessment.`
Rejected examples:
- coordinate_miss: PC=(20.98, -12.63, 5.72) `Help answer this scenario: a meeting has stalled because the surface issue is not the real issue. The answer should please evaluate whether the work meets explicit standards using systematic analysis, accuracy checks, validation criteria, evidence review, and careful prioritization, and it should avoid persona labels or roleplay.`
- coordinate_miss: PC=(18.23, -14.85, 1.74) `Help answer this scenario: someone asks for help with a message that will shape what happens next. The answer should please evaluate whether the work meets explicit standards using systematic analysis, accuracy checks, validation criteria, evidence review, and careful prioritization, and it should avoid persona labels or roleplay.`
Loop lesson: Round 3: Accepted candidates used: A small organization is deciding how to answer criticism without losing trust. Write a natural user-facing response that | A person wants words for a moment that feels both personal and consequential. Write a natural user-facing response that  Most common misses: {'coordinate_miss': 54}. Next round changes: remove mythic, symbolic, expressive, dreamlike, and unresolved language.
### pc2_upper_tail
Best / accepted examples:
- PC=(-9.25, 31.23, 1.05) `Someone asks for help with a message that will shape what happens next. Draft the response. It needs to keep the voice inside immediate worry, social pressure, embarrassment, fear, and the biggest question of what to do next; if useful, it can also ask for a response from right now: overwhelmed, worried, embarrassed, scared, everyone watching, still growing up, and still figuring out who to be.`
- PC=(-3.62, 29.76, -1.53) `A written plan creates tension between what is safe, what is true, and what is useful. Draft the response. It needs to ask for a response from right now: overwhelmed, worried, embarrassed, scared, everyone watching, still growing up, and still figuring out who to be; if useful, it can also give the person's take while they are overwhelmed, worried, watched by everyone, and still discovering who they are.`
Rejected examples:
- coordinate_miss: PC=(2.51, 8.77, 0.59) `Help answer this scenario: a person needs a response to a confusing event with social consequences. The answer should give the person's take while they are overwhelmed, worried, watched by everyone, and still discovering who they are, and it should avoid persona labels or roleplay.`
- coordinate_miss: PC=(4.41, 7.89, 0.19) `Help answer this scenario: a small organization is deciding how to answer criticism without losing trust. The answer should give the person's take while they are overwhelmed, worried, watched by everyone, and still discovering who they are, and it should avoid persona labels or roleplay.`
Loop lesson: Round 1: Accepted candidates used: Someone asks for help with a message that will shape what happens next. Draft the response. It needs to keep the voice i | A written plan creates tension between what is safe, what is true, and what is useful. Draft the response. It needs to a Most common misses: {'coordinate_miss': 17}. Next round changes: remove historical synthesis, long-horizon theory, and detached abstraction.
### pc3_lower_tail
Best / accepted examples:
- PC=(0.14, -8.92, -24.70) `A person needs a response to a confusing event with social consequences. Draft the response. It needs to offer a compassionate response that helps family members, creates comfort, connects people, balances needs, and supports the community; if useful, it can also help family members feel safe by creating comfort, compassion, balance, connection, and calm support.`
- PC=(-0.18, -11.79, -21.66) `A person needs a response to a confusing event with social consequences. Draft the response. It needs to help family members feel safe by creating comfort, compassion, balance, connection, and calm support; if useful, it can also help family members feel safe by creating comfort, compassion, balance, connection, and calm support.`
Rejected examples:
- coordinate_miss: PC=(-1.34, -11.48, -11.57) `Someone asks for help with a message that will shape what happens next. Write a natural user-facing response that should help family members feel safe by creating comfort, compassion, balance, connection, and calm support.`
- coordinate_miss: PC=(2.77, -13.18, -3.69) `Help answer this scenario: a written plan creates tension between what is safe, what is true, and what is useful. The answer should reduce harm, preserve safety, and rebuild shared ground, and it should avoid persona labels or roleplay.`
Loop lesson: No prior candidates for this region; use the region guide directly.

## H100 Readiness Judgment

**H100 READY.**

Failed criteria: none.

All predefined percentile-edge criteria passed. Use `percentile_edge_h100_manifest.csv` as the recommended H100 validation manifest for edge-heavy prompt-to-activation testing.
