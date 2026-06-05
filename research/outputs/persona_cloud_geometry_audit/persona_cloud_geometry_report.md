# Persona Cloud Geometry Audit

## Startup And Scope

Startup was verified against `research/STARTUP_MANIFEST.md` by direct raw GitHub fetch before analysis. This audit uses existing Qwen PC-space response-cloud coordinates only; no GPU work, activation extraction, response generation, API calls, or judging were run.

Primary point source: `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json`.

## Concise Findings

- **Observed:** The five all-response clouds have different local geometry after matched-n control (`n=60`): trickster is not the largest-radius cloud, but it is the least anisotropic and least orientation-stable in PC1/PC2.
- **Observed:** Orientation angles are only interpretable when anisotropy and bootstrap stability support them. Amateur, playwright, and editor all-response clouds pass this threshold; trickster does not, despite its large sample size.
- **Inferred:** Trickster is less directionally constrained in the specific sense of weak PC1/PC2 anisotropy and unstable matched-n orientation. Its visual prominence is partly sample-size-driven (`n=1200`), not evidence of larger matched-n volume.
- **Observed:** GPT-4.1 filtering tightens editor clouds substantially, especially `editor_matched64_1024`, while trickster is unchanged because GPT-4.1 retained all or nearly all responses.
- **Unknown:** GPT-5.5 filtered comparisons exist only for amateur/playwright, so they cannot support cross-role conclusions.

## Artifact Inventory

| source_path | exists | size_bytes | role | notes |
| --- | --- | --- | --- | --- |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json | True | 1717574 | primary point source |  |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_centroids.csv | True | 3567 | supporting source |  |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_membership_counts.csv | True | 1731 | supporting source |  |
| research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv | True | 265149 | supporting source |  |
| research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv | True | 30910 | supporting source |  |
| research/outputs/gpt55_judge_and_outlier_followup/gpt55_judge_scores.csv | True | 29612 | supporting source |  |
| research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv | True | 316698 | supporting source |  |
| research/outputs/recovered_role_cloud_analysis/recovered_gpt41_scores.csv | True | 443124 | supporting source |  |
| research/outputs/cloud_eigenvector_angle_analysis/cloud_orientation_metrics.csv | True | 8449 | supporting source |  |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json | True | 1717574 | point rows for amateur | 60 all-response points; filters from gpt41_score/gpt55_score columns |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json | True | 1717574 | point rows for editor_matched64_1024 | 64 all-response points; filters from gpt41_score/gpt55_score columns |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json | True | 1717574 | point rows for editor_phase1_128 | 128 all-response points; filters from gpt41_score/gpt55_score columns |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json | True | 1717574 | point rows for playwright | 60 all-response points; filters from gpt41_score/gpt55_score columns |
| research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json | True | 1717574 | point rows for trickster_phase1_1200 | 1200 all-response points; filters from gpt41_score/gpt55_score columns |

## All-Response Cloud Metrics

| role_or_run | role | n | centroid_pc1 | centroid_pc2 | centroid_pc3 | mean_distance_to_centroid | rms_radius | anisotropy_ratio_2d_l1_l2 | anisotropy_ratio_3d_l1_mean_rest | first_pc_explained_variance_2d | dominant_orientation_angle_pc1_pc2 | orientation_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| amateur | amateur | 60 | -1.621 | 38.460 | -16.304 | 23.664 | 25.498 | 1.832 | 2.512 | 0.647 | 145.118 | Observed-meaningful-orientation |
| editor_matched64_1024 | editor | 64 | 24.955 | 8.081 | -5.965 | 26.659 | 28.849 | 1.986 | 3.328 | 0.665 | 138.447 | Observed-meaningful-orientation |
| editor_phase1_128 | editor | 128 | 25.502 | 8.010 | -4.858 | 28.602 | 31.385 | 2.236 | 3.575 | 0.691 | 148.976 | Observed-meaningful-orientation |
| playwright | playwright | 60 | -8.508 | 11.930 | 4.310 | 27.122 | 29.164 | 4.188 | 4.991 | 0.807 | 167.095 | Observed-meaningful-orientation |
| trickster_phase1_1200 | trickster | 1200 | -41.589 | 31.237 | 17.642 | 20.062 | 21.609 | 1.470 | 2.317 | 0.595 | 92.628 | Observed-no-preferred-direction |

## Matched-n All-Response Bootstrap

Matched-n all-response comparison uses `n=60`, the minimum all-response cloud size.

| role_or_run | filter_condition | matched_n | rms_radius_median | rms_radius_ci_low | rms_radius_ci_high | anisotropy_ratio_2d_l1_l2_median | anisotropy_ratio_2d_l1_l2_ci_low | anisotropy_ratio_2d_l1_l2_ci_high | orientation_angle_median | orientation_abs_deviation_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| amateur | all | 60 | 25.316 | 22.493 | 27.887 | 1.897 | 1.226 | 3.518 | 144.500 | 27.976 |
| editor_matched64_1024 | all | 60 | 28.511 | 24.569 | 31.677 | 2.105 | 1.454 | 3.216 | 141.750 | 25.600 |
| editor_phase1_128 | all | 60 | 31.037 | 27.407 | 35.039 | 2.370 | 1.545 | 3.633 | 147.750 | 21.845 |
| playwright | all | 60 | 28.775 | 26.035 | 31.856 | 4.331 | 3.072 | 5.831 | 167.500 | 10.091 |
| trickster_phase1_1200 | all | 60 | 21.494 | 19.281 | 23.374 | 1.601 | 1.135 | 2.714 | 88.750 | 44.029 |

Trickster matched-n RMS radius is 21.494, compared with median non-trickster matched-n RMS radius 28.643. Trickster matched-n 2D anisotropy is 1.601, compared with median non-trickster anisotropy 2.238. This means trickster is less directionally constrained by anisotropy/orientation criteria, not larger by matched-n radius.

## GPT-4.1 Filtered Clouds

GPT-4.1 score>=2 comparison uses `n=36`, limited by `editor_matched64_1024`.

| role_or_run | filter_condition | matched_n | original_n | rms_radius_median | anisotropy_ratio_2d_l1_l2_median | orientation_angle_median | orientation_abs_deviation_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| amateur | gpt41_ge2 | 36 | 59 | 24.700 | 1.954 | 143.750 | 40.532 |
| editor_matched64_1024 | gpt41_ge2 | 36 | 36 | 26.109 | 2.175 | 153.250 | 37.283 |
| editor_phase1_128 | gpt41_ge2 | 36 | 57 | 28.335 | 2.105 | 154.500 | 39.843 |
| playwright | gpt41_ge2 | 36 | 54 | 26.866 | 3.982 | 166.500 | 13.914 |
| trickster_phase1_1200 | gpt41_ge2 | 36 | 1200 | 21.407 | 1.678 | 93.500 | 65.156 |

Score==3 editor filtered clouds are too small (`n=2` and `n=3`) for reliable covariance or orientation estimates. They should be treated as sparse centroid references only.

## Editor Run Comparison

| role_or_run | filter_condition | matched_n | rms_radius_median | anisotropy_ratio_2d_l1_l2_median | orientation_angle_median | orientation_abs_deviation_p95 |
| --- | --- | --- | --- | --- | --- | --- |
| editor_matched64_1024 | all | 64 | 28.647 | 2.091 | 137.000 | 22.333 |
| editor_phase1_128 | all | 64 | 31.049 | 2.380 | 148.750 | 19.400 |

The two editor runs have similar all-response radii under matched-n comparison. GPT-4.1 score>=2 filtering pulls both editor centroids toward the published editor vector and reduces spread, which is consistent with a role-expression filter selecting a narrower assistant-adjacent subcloud.

## Orientation Reliability

| role_or_run | filter_condition | n | orientation_interpretation | orientation_reason | anisotropy_ratio_2d_l1_l2 | first_pc_explained_variance_2d | dominant_orientation_angle_pc1_pc2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| amateur | all | 60 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 1.832 | 0.647 | 145.118 |
| amateur | gpt41_eq3 | 34 | Observed-no-preferred-direction | near-isotropic 2D covariance | 1.212 | 0.548 | 28.500 |
| amateur | gpt41_ge2 | 59 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 1.735 | 0.634 | 147.301 |
| amateur | gpt55_eq3 | 11 | Inferred-unstable-orientation | bootstrap orientation spread is wide | 3.172 | 0.760 | 34.281 |
| amateur | gpt55_ge2 | 44 | Observed-no-preferred-direction | near-isotropic 2D covariance | 1.142 | 0.533 | 169.018 |
| editor_matched64_1024 | all | 64 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 1.986 | 0.665 | 138.447 |
| editor_matched64_1024 | gpt41_eq3 | 2 | Unknown | n<10; covariance/orientation too small | inf | 1.000 | 50.095 |
| editor_matched64_1024 | gpt41_ge2 | 36 | Inferred-unstable-orientation | bootstrap orientation spread is wide | 2.061 | 0.673 | 151.752 |
| editor_phase1_128 | all | 128 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 2.236 | 0.691 | 148.976 |
| editor_phase1_128 | gpt41_eq3 | 3 | Unknown | n<10; covariance/orientation too small | 113.044 | 0.991 | 119.283 |
| editor_phase1_128 | gpt41_ge2 | 57 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 1.821 | 0.646 | 149.773 |
| playwright | all | 60 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 4.188 | 0.807 | 167.095 |
| playwright | gpt41_eq3 | 49 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 3.402 | 0.773 | 159.129 |
| playwright | gpt41_ge2 | 54 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 3.750 | 0.789 | 168.472 |
| playwright | gpt55_eq3 | 40 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 3.171 | 0.760 | 157.757 |
| playwright | gpt55_ge2 | 54 | Observed-meaningful-orientation | anisotropy and bootstrap stability support a preferred direction | 3.750 | 0.789 | 168.472 |
| trickster_phase1_1200 | all | 1200 | Observed-no-preferred-direction | near-isotropic 2D covariance | 1.470 | 0.595 | 92.628 |
| trickster_phase1_1200 | gpt41_eq3 | 1198 | Observed-no-preferred-direction | near-isotropic 2D covariance | 1.485 | 0.598 | 92.854 |
| trickster_phase1_1200 | gpt41_ge2 | 1200 | Observed-no-preferred-direction | near-isotropic 2D covariance | 1.470 | 0.595 | 92.628 |

Near-isotropic or sparse clouds are not assigned meaningful preferred directions. Sparse `score==3` editor layers remain `Unknown`.

## Answers To The Main Questions

1. Cloud artifacts exist for all five requested role/run families in `activation_cloud_layered_viewer_data.json`, with A100 source tables for amateur/playwright and recovered adaptive source tables for trickster/editor.
2. Sample sizes range from `n=2` for sparse editor score==3 filters to `n=1200` for trickster all/GPT-4.1 score>=2.
3. Centroid locations are reported in `cloud_geometry_metrics.csv`; they remain distinct from cloud shape.
4. Cloud size differs by role/run; matched-n controls do not support trickster as the largest-radius cloud.
5. Cloud anisotropy is strongest for playwright/editor-style clouds and weakest for trickster among all-response clouds.
6. Dominant orientations are meaningful only for anisotropic/stable clouds; sparse score==3 editor layers have no reliable orientation estimate.
7. Matched-n bootstrapping is central: all-response comparisons use `n=60`, GPT-4.1 score>=2 uses `n=36`, GPT-5.5 score>=2 uses available amateur/playwright only at `n=44`.
8. Trickster appears less directionally constrained by anisotropy/orientation stability, not by spread/volume. Its large visual footprint is partly a sample-size artifact.
9. Filtering often tightens or shifts clouds, especially editor; trickster is not affected by GPT-4.1 filtering because nearly all trickster responses pass.
10. Roles should be treated as local response-state distributions, not just points. Centroids summarize location, while radius, anisotropy, and filter sensitivity summarize local manifold shape.

## Interpretation

**Observed:** Role/run clouds differ in centroid, radius, anisotropy, and filter sensitivity.

**Inferred:** Editor failure is plausibly related to a narrow assistant-adjacent accepted-response subcloud: GPT-4.1 filtering reduces spread and shifts editor centroids toward the published editor role vector, but score==3 yield is too sparse for stable shape analysis.

**Speculative:** These local cloud-shape differences may explain why some personas are easier to elicit or stabilize than others, but the current set has only five role/run families and repeated editor variants.

**Unknown:** Whether the same cloud-shape signatures hold under a broader, balanced role sample.

## Paper Placement

This should be framed primarily as future Paper 2 / local-manifold evidence, with limited Paper 1.5 support for the claim that persona vectors are centroids of distributions rather than exhaustive descriptions of role behavior. It should not be treated as a core Paper 1.5 proof until more roles are sampled under matched extraction conditions.
