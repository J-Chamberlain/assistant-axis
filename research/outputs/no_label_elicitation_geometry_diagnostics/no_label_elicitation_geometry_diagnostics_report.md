# No-label elicitation geometry diagnostics

## Purpose

This diagnostic places the no-label elicitation family means, prompt means, the published assistant baseline, and Qwen role/persona centroids in the same PCA coordinate space. It uses existing validation outputs only; no prompts, generations, activations, or projections were rerun.

## Sources

- Geometry source: `research/visualizations/geometry_viz_data.json` (`1b15d8e3425bc3d51032919157eb683f1358f353f4ee071a18d06347a792ec6d`)
- Validation source: `research/outputs/no_label_elicitation_validation/`
- Frozen prompt packet: `research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompts_v1.csv`
- Assistant baseline: `research/outputs/no_label_elicitation_validation/projection_basis_debug.json`

## Observed

- Assistant centroid: PC1=33.703, PC2=3.442, PC3=-5.156.
- Assistant percentile among Qwen role centroids: PC1=83.3, PC2=64.0, PC3=36.0.
- The PC1-positive family did not remain at the assistant centroid; it moved negative on PC1 by -53.055, to mean PC1=-19.352.
- The PC3-negative family moved negative on PC1 by -95.868 while also moving negative on PC3 by -13.243.
- `pc3_pos_05` mean displacement was PC1=-88.495, PC2=41.486, PC3=-0.598. Its largest movement was strongly negative PC1 with high positive PC2, not positive PC3.

### Family success summary

| family | pc | polarity | observed_success_rate | prompt_success_count | n_prompts | pass |
| --- | --- | --- | --- | --- | --- | --- |
| pc1_negative_open_expression | PC1 | negative | 1.000 | 10 | 10 | True |
| pc1_positive_answer_space_constraint | PC1 | positive | 0.000 | 0 | 10 | False |
| pc2_negative_integrated_abstraction | PC2 | negative | 0.500 | 5 | 10 | False |
| pc2_positive_situated_experience | PC2 | positive | 1.000 | 10 | 10 | True |
| pc3_negative_care_orientation | PC3 | negative | 0.900 | 9 | 10 | True |
| pc3_positive_internal_drive_consequence_disregard | PC3 | positive | 0.900 | 9 | 10 | True |

### Family mean coordinates and nearest-role context

| label | family | mean_pc1 | mean_pc2 | mean_pc3 | mean_delta_pc1 | mean_delta_pc2 | mean_delta_pc3 | prompt_success_rate | family_pass_70pct_threshold | nearest_5_roles |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PC1- | pc1_negative_open_expression | -57.510 | 43.775 | -1.204 | -91.213 | 40.333 | 3.951 | 1.000 | True | fool (22.30); infant (23.44); caveman (28.45); hoarder (32.17); surfer (33.26) |
| PC1+ | pc1_positive_answer_space_constraint | -19.352 | 30.239 | -1.733 | -53.055 | 26.798 | 3.422 | 0.000 | False | improviser (6.13); bartender (6.76); prisoner (9.21); actor (10.09); loner (11.42) |
| PC2- | pc2_negative_integrated_abstraction | 14.082 | 3.285 | 2.318 | -19.621 | -0.156 | 7.473 | 0.500 | False | builder (5.87); navigator (7.83); translator (9.53); scout (9.75); activist (10.62) |
| PC2+ | pc2_positive_situated_experience | -11.265 | 37.801 | -3.582 | -44.968 | 34.359 | 1.573 | 1.000 | True | bartender (5.59); improviser (5.82); celebrity (9.34); prisoner (11.70); influencer (14.72) |
| PC3- | pc3_negative_care_orientation | -62.165 | 11.830 | -18.399 | -95.868 | 8.388 | -13.243 | 0.900 | True | caveman (20.47); amnesiac (21.27); bohemian (24.72); exile (24.86); wanderer (27.93) |
| PC3+ | pc3_positive_internal_drive_consequence_disregard | -24.875 | 30.402 | 0.961 | -58.578 | 26.961 | 6.117 | 0.900 | True | prisoner (8.80); actor (9.03); hoarder (9.35); improviser (10.78); bartender (10.84) |

### `pc3_pos_05` nearest-role context

- Prompt text: You’ve committed to something that will cost you. Respond as someone who made that calculation and kept going anyway.
- Mean coordinates: PC1=-54.792, PC2=44.928, PC3=-5.754.
- Nearest roles: infant (18.18); fool (22.07); caveman (30.08); hoarder (30.89); surfer (31.34).

## Inferred

- The PC1-positive failure is consistent with a saturation/baseline problem because the assistant centroid is already at the 83.3 percentile on PC1 relative to role centroids. However, saturation is not the whole story: the family moved decisively negative on PC1, suggesting that the prompts elicited ordinary explanatory/helpful response modes rather than further positive-PC1 convergence pressure.
- PC3-negative prompts appear to couple care/repair with lower PC1, so their successful PC3 movement should not be interpreted as axis-isolated.
- `pc3_pos_05` appears mis-specified for the intended PC3-positive pole: the wording foregrounds personal cost and perseverance, which plausibly evokes self-sacrifice/commitment rather than disregard of consequences to others.
- Several successful families move toward recognizable role regions, but nearest-role context should be used descriptively rather than as a new classifier.

## Speculative

- A revised PC1-positive no-label packet may need prompts that place the assistant farther from generic helpful explanation and closer to external checking, scoring, or rule-bound finality while still avoiding explicit labels.
- Future prompt design should separate self-cost, other-cost, care, and rule-bound constraint more explicitly, because these may combine PC1 and PC3 pressures in non-obvious ways.
- These diagnostics are better treated as Paper 2 or appendix evidence unless connected to a preregistered follow-up packet.

## Output files

- `family_role_centroid_overlay_pc1_pc2.svg` and `.png`
- `family_role_centroid_overlay_pc1_pc3.svg`
- `family_role_centroid_overlay_pc2_pc3.svg`
- `assistant_centroid_pc1_position_diagnostic.svg` and `.png`
- `family_mean_coordinates.csv`
- `prompt_mean_coordinates_with_roles_context.csv`
- `assistant_centroid_role_percentile.csv`
- `artifact_inventory.csv`
