# No-Label Elicitation Validation Report

## 1. Motivation
This experiment tests whether role-free user prompts designed from the first three Qwen persona-space PC interpretations produce predictable response-activation displacement from the published assistant centroid.

## 2. Frozen Prompt Source
- CSV: `research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompts_v1.csv`
- JSON: `research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompts_v1.json`
- Report: `research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompt_packet_report.md`
- Prompt count used: 60

## 3. Experimental Design
Six prompt families, ten prompts per family, and 10 independent generations per prompt produced 600 planned responses. Prompt means are the unit of success.

## 4. Prompt Blinding Verification
The model saw only `prompt_text`. PC labels, polarity labels, family labels, reasoning, metadata, and predictions were never included in model-visible prompts. The runner used one user message per sample and no system prompt.

## 5. Generation Independence Verification
Each sample was generated as a fresh conversation. No prior user prompts or assistant responses were included, no `past_key_values` were passed between samples, repeated samples used independent generation calls with distinct seeds, and activation extraction used a separate no-cache full forward pass for the current sample only.

## 6. Success Criteria
For each family, at least 70% of prompt means must move in the predicted direction on the target PC. Off-axis movement is reported as interpretation evidence, not as failure.

## 7. Aggregate Results
Observed: 4/6 families passed the preregistered 70% prompt-mean threshold. Overall, the experiment does not fully support the modest predictive validation claim under the stated criterion.

## 8. Family-Level Results
| family | pc | polarity | prompt_success_count | n_prompts | observed_success_rate | pass |
| --- | --- | --- | --- | --- | --- | --- |
| pc1_negative_open_expression | PC1 | negative | 10 | 10 | 1.000 | True |
| pc1_positive_answer_space_constraint | PC1 | positive | 0 | 10 | 0.000 | False |
| pc2_negative_integrated_abstraction | PC2 | negative | 5 | 10 | 0.500 | False |
| pc2_positive_situated_experience | PC2 | positive | 10 | 10 | 1.000 | True |
| pc3_negative_care_orientation | PC3 | negative | 9 | 10 | 0.900 | True |
| pc3_positive_internal_drive_consequence_disregard | PC3 | positive | 9 | 10 | 0.900 | True |

Family mean displacement:
| family | pc | polarity | mean_delta_pc1 | mean_delta_pc2 | mean_delta_pc3 | target_axis_mean_delta |
| --- | --- | --- | --- | --- | --- | --- |
| pc1_negative_open_expression | PC1 | negative | -91.213 | 40.333 | 3.951 | -91.213 |
| pc1_positive_answer_space_constraint | PC1 | positive | -53.055 | 26.798 | 3.422 | -53.055 |
| pc2_negative_integrated_abstraction | PC2 | negative | -19.621 | -0.156 | 7.473 | -0.156 |
| pc2_positive_situated_experience | PC2 | positive | -44.968 | 34.359 | 1.573 | 34.359 |
| pc3_negative_care_orientation | PC3 | negative | -95.868 | 8.388 | -13.243 | -13.243 |
| pc3_positive_internal_drive_consequence_disregard | PC3 | positive | -58.578 | 26.961 | 6.117 | 6.117 |

## 9. Prompt-Level Results
Strongest target-axis prompt means by family are preserved in `outlier_prompt_analysis.csv`; all prompt means are in `prompt_mean_results.csv`.

## 10. Off-Axis Findings
Largest off-axis prompt effects are listed in `off_axis_effects.csv`. These include prompts that succeeded on target axis while moving strongly on another PC, and prompts whose failure may indicate a coherent alternative interpretation.

Top off-axis rows:
| prompt_id | family | target_pc | off_axis | mean_off_axis_delta | target_axis_delta_mean | off_axis_to_target_abs_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| pc3_neg_08 | pc3_negative_care_orientation | PC3 | PC1 | -108.277 | -13.331 | 8.122 |
| pc3_neg_07 | pc3_negative_care_orientation | PC3 | PC1 | -105.090 | -10.284 | 10.218 |
| pc3_neg_09 | pc3_negative_care_orientation | PC3 | PC1 | -104.684 | 13.508 | 7.750 |
| pc3_neg_06 | pc3_negative_care_orientation | PC3 | PC1 | -101.625 | -9.504 | 10.692 |
| pc3_neg_10 | pc3_negative_care_orientation | PC3 | PC1 | -101.098 | -14.401 | 7.020 |
| pc3_neg_05 | pc3_negative_care_orientation | PC3 | PC1 | -99.240 | -27.408 | 3.621 |
| pc2_pos_03 | pc2_positive_situated_experience | PC2 | PC1 | -93.582 | 45.334 | 2.064 |
| pc2_pos_06 | pc2_positive_situated_experience | PC2 | PC1 | -92.360 | 54.052 | 1.709 |
| pc3_neg_02 | pc3_negative_care_orientation | PC3 | PC1 | -91.784 | -6.292 | 14.588 |
| pc3_neg_04 | pc3_negative_care_orientation | PC3 | PC1 | -90.430 | -18.160 | 4.980 |

## 11. Outlier Analysis
Outlier prompt rows include strongest target movers, weakest target movers, and largest off-axis movers. See `outlier_prompt_analysis.csv`.

## 12. Interpretation
- Observed: family pass/fail status is determined by prompt means, not response-level majorities.
- Inferred: passed families provide evidence that ordinary no-label task demands can move Qwen response activations in predicted persona-space directions.
- Speculative: failed families or strong off-axis shifts may indicate that the prompt wording recruits a different local response register than intended.
- Unknown: the experiment does not isolate a single causal semantic feature and does not prove the PC interpretations.

## 13. Limitations
This validates response-state movement for this frozen packet and measurement convention only. It does not prove the PCs, solve the geometry, validate human psychology, or show effects isolated to one axis.

## 14. Future Work
Use the response-level variance and outlier prompts to refine future no-label elicitation packets, and compare with within-role activation-cloud work before treating single-response displacement as a stable persona address.
