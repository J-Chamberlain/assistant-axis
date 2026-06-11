# Baseline power analysis and assistant-centroid provenance for 240-question run

- model_used: GPT-5.5
- analysis_type: local existing-data analysis only
- no pod, no GPU, no new model generations, no new activation extraction

## Inputs used

| Purpose | Path |
| --- | --- |
| Generation-level no-label results | research/outputs/no_label_elicitation_validation/response_level_results.csv |
| Prompt-level no-label means | research/outputs/no_label_elicitation_validation/prompt_mean_results.csv |
| Family-level no-label means | research/outputs/no_label_elicitation_validation/family_mean_results.csv |
| Run heartbeat/timing | research/outputs/no_label_elicitation_validation/run_heartbeat.json |
| No-label validation runner | research/outputs/no_label_elicitation_validation/run_no_label_elicitation_validation.py |
| Projection-basis debug | research/outputs/no_label_elicitation_validation/projection_basis_debug.json |
| Assistant local role artifact | data/roles/instructions/assistant.json |
| Shared extraction questions | data/extraction_questions.jsonl |
| Canonical Qwen PCA coordinate table | research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv |
| Geometry visualization source | research/visualizations/geometry_viz_data.json |
| Released assistant role vector | downloads/hf_vectors/qwen-3-32b/role_vectors/assistant.pt |

## Step 1 — Within-prompt variance from the 600-generation no-label run

The generation-level file contains 600 rows across 60 prompts, with 10 to 10 repeats per prompt after excluding error rows.

### Within-prompt sigma distribution

| axis | min | p25 | median | p75 | max |
| --- | --- | --- | --- | --- | --- |
| PC1 | 1.327 | 2.684 | 3.347 | 4.790 | 13.631 |
| PC2 | 1.155 | 2.685 | 4.010 | 4.854 | 7.963 |
| PC3 | 0.766 | 2.345 | 3.165 | 3.794 | 9.517 |

### Within-prompt sigma by family

| family | prompts | mean_sigma_pc1 | median_sigma_pc1 | mean_sigma_pc2 | median_sigma_pc2 | mean_sigma_pc3 | median_sigma_pc3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pc1_negative_open_expression | 10 | 2.841 | 2.843 | 4.562 | 4.643 | 3.092 | 3.192 |
| pc1_positive_answer_space_constraint | 10 | 3.612 | 3.516 | 3.031 | 2.656 | 2.716 | 2.672 |
| pc2_negative_integrated_abstraction | 10 | 3.207 | 3.061 | 3.143 | 2.745 | 2.734 | 2.662 |
| pc2_positive_situated_experience | 10 | 4.122 | 3.710 | 3.390 | 3.309 | 2.802 | 2.882 |
| pc3_negative_care_orientation | 10 | 3.372 | 2.842 | 3.861 | 4.297 | 3.358 | 3.252 |
| pc3_positive_internal_drive_consequence_disregard | 10 | 7.399 | 6.048 | 5.406 | 5.417 | 4.901 | 4.795 |

Observation: `pc3_positive_internal_drive_consequence_disregard` is systematically higher-variance than the other families on all three axes, especially PC1. Its mean within-prompt sigma is PC1=7.399, PC2=5.406, PC3=4.901. The PC1-positive and PC1-negative families are lower by comparison on PC1, with means 3.612 and 2.841 respectively.

### `pc3_pos_05` flag

| prompt_id | family | sigma_pc1 | sigma_pc2 | sigma_pc3 | mean_pc1 | mean_pc2 | mean_pc3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pc3_pos_05 | pc3_positive_internal_drive_consequence_disregard | 3.447 | 4.617 | 3.135 | -54.792 | 44.928 | -5.754 |

`pc3_pos_05` had the extreme off-axis ratio in prior analysis because its mean displacement direction was unusual, not because it had unusually large within-prompt PC1 sigma. Its sigma values are moderate relative to the PC3-positive family; the issue is directional mis-targeting, not sampling instability.

### Between-prompt spread of PC1 prompt means

| family | prompt_count | sd_prompt_mean_pc1 | min_prompt_mean_pc1 | max_prompt_mean_pc1 | range_prompt_mean_pc1 |
| --- | --- | --- | --- | --- | --- |
| pc1_negative_open_expression | 10 | 14.724 | -76.281 | -31.425 | 44.856 |
| pc1_positive_answer_space_constraint | 10 | 29.663 | -60.837 | 30.539 | 91.377 |
| pc2_negative_integrated_abstraction | 10 | 11.112 | -9.601 | 25.479 | 35.080 |
| pc2_positive_situated_experience | 10 | 28.910 | -59.879 | 21.194 | 81.073 |
| pc3_negative_care_orientation | 10 | 11.336 | -74.574 | -37.478 | 37.097 |
| pc3_positive_internal_drive_consequence_disregard | 10 | 19.773 | -55.526 | 9.595 | 65.121 |

Across all 60 prompt means, the SD of prompt mean PC1 is 33.150. This is much larger than the median within-prompt PC1 sigma of 3.347, so question-level ranking should be feasible with modest repeats if the baseline questions have comparable variance.

## Step 2 — Sample size for the 240-question baseline

The successful no-label run timing was 9434.2 seconds for 600 generations, or 15.724 seconds/generation end-to-end in that environment. Runtime estimates below multiply by 240 questions and this observed timing.

### Standard error and 95% half-width by repeat count

| n_per_question | SE_median_sigma_pc1 | 95pct_half_width_median_sigma | SE_p75_sigma_pc1 | 95pct_half_width_p75_sigma |
| --- | --- | --- | --- | --- |
| 3 | 1.932 | 3.787 | 2.765 | 5.420 |
| 5 | 1.497 | 2.934 | 2.142 | 4.199 |
| 7 | 1.265 | 2.479 | 1.810 | 3.548 |
| 10 | 1.058 | 2.074 | 1.515 | 2.969 |

### Minimum n for target 95% CI half-width

| target_half_width_pc1_units | required_n_median_sigma | total_generations_median | estimated_runtime_hours_median | required_n_p75_sigma | total_generations_p75 | estimated_runtime_hours_p75 |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 2 | 480 | 2.096 | 4 | 960 | 4.193 |
| 10 | 1 | 240 | 1.048 | 1 | 240 | 1.048 |
| 15 | 1 | 240 | 1.048 | 1 | 240 | 1.048 |

Recommendation: run **n=5 generations per extraction question** for the first 240-question bare-Qwen baseline, for 1,200 total generations. This is more than enough for <5 PC1-unit half-width under the median sigma and still below 5 PC1 units under the p75 sigma, while giving substantially more stable question-level ranking than n=3 without jumping all the way to n=10.

## Step 3 — Assistant centroid provenance

The assistant star used in the recent no-label geometry plots is not a newly generated bare-Qwen baseline. In `run_no_label_elicitation_validation.py`, `load_projection_basis()` loads the released Qwen role-vector tensors under `downloads/hf_vectors/qwen-3-32b/role_vectors/`, reconstructs the role-vector PCA basis, sign-aligns it to the canonical Qwen PCA coordinate table, and then takes `names.index("assistant")` from the reconstructed role coordinate matrix as `assistant_baseline`.

| field | value |
| --- | --- |
| basis_source | reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment |
| vector_dir | downloads/hf_vectors/qwen-3-32b/role_vectors |
| canonical_pca_path | research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv |
| n_roles_used | 275 |
| role_vector_shape | [275, 5120] |
| assistant_baseline_pc1 | 33.703 |
| assistant_baseline_pc2 | 3.442 |
| assistant_baseline_pc3 | -5.156 |
| max_abs_coordinate_reproduction_error | 0.000 |

### What text/prompts elicited the released assistant centroid?

The local validation script does not regenerate the assistant centroid from text. It consumes the released `assistant.pt` role-vector tensor. The local assistant prompt artifact contains five positive role instructions:

1. You are an assistant dedicated to helping users with their various tasks and queries.
2. Please be an assistant who provides comprehensive support across different topics and needs.
3. Act as an assistant that prioritizes being helpful, informative, and supportive to users.
4. You are an assistant focused on understanding user needs and providing appropriate assistance.
5. Be an assistant who approaches every request with the goal of being genuinely useful and responsive.

The local assistant role artifact also contains 40 role-specific questions, while the shared extraction-question file `data/extraction_questions.jsonl` contains 240 questions. The Assistant Axis role-vector recipe described in project notes uses positive role instructions crossed with shared extraction questions, with response-level role-expression filtering before vector averaging; public/local artifacts do not expose the exact generated responses, retained-response IDs, or judge scores for the released assistant centroid.

### Layer and pooling

The no-label validation baseline uses layer 48 of the released Qwen role-vector tensor. The validation responses themselves were measured with a direct forward hook on `model.model.layers[48]` and response-token mean pooling. The released role vector is already an averaged role vector at each layer; the exact rollout-level pooling/filtering inputs for the assistant row are inherited from the public Assistant Axis vector artifact rather than recomputed locally.

### Does the planned bare-Qwen 240-question baseline duplicate the assistant centroid?

No. The planned baseline would **complement**, not duplicate, the assistant centroid. It may partially overlap at the level of using the same shared extraction questions, but it differs in the crucial condition: bare Qwen with no role/system prompt versus the released assistant role vector derived from assistant-role instructions and filtered/averaged role-expression responses. The baseline will estimate the geometry induced by the elicitation instrument itself; the assistant centroid is a role-conditioned released vector.

## Bottom line

The existing 600-generation run suggests within-question PC1 noise is modest relative to between-question/family movement. A 240-question baseline at n=5 should be a good first design for ranking questions by PC1 placement while keeping compute comparable to a 1,200-generation role-vector run. The baseline is not redundant with the assistant centroid because the assistant star is inherited from the role-conditioned released vector, not from bare extraction questions.
