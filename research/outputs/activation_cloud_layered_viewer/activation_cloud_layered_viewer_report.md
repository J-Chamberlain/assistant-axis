# Activation Cloud Layered Viewer Report

Startup status: **STARTUP VERIFIED**.

## Source Files Used

- `research/visualizations/geometry_viz_data.json`
- `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`
- `research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv`
- `research/outputs/gpt55_judge_and_outlier_followup/gpt55_judge_scores.csv`
- `research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv`
- `research/outputs/recovered_role_cloud_analysis/recovered_gpt41_scores.csv`
- `research/outputs/a100_activation_cloud_visualization_and_judge_compare/activation_cloud_viewer.html`
- `research/outputs/a100_activation_cloud_visualization_and_judge_compare/activation_cloud_viewer_data.json`

## Available Roles/Runs

`amateur`, `editor_matched64_1024`, `editor_phase1_128`, `playwright`, `trickster_phase1_1200`

## Available Judge Models

| role/run | GPT-4.1 | GPT-5.5 |
|---|---:|---:|
| amateur | True | True |
| editor_matched64_1024 | True | False |
| editor_phase1_128 | True | False |
| playwright | True | True |
| trickster_phase1_1200 | True | False |

## Layer Counts

| role/run | layer | n | warning |
|---|---|---:|---|
| amateur | All responses | 60 |  |
| amateur | GPT-4.1 score>=2 | 59 |  |
| amateur | GPT-4.1 score==3 | 34 |  |
| amateur | GPT-5.5 score>=2 | 44 |  |
| amateur | GPT-5.5 score==3 | 11 |  |
| editor_matched64_1024 | All responses | 64 |  |
| editor_matched64_1024 | GPT-4.1 score>=2 | 36 |  |
| editor_matched64_1024 | GPT-4.1 score==3 | 2 | sparse centroid n=2 |
| editor_matched64_1024 | GPT-5.5 score>=2 | 0 | layer unavailable |
| editor_matched64_1024 | GPT-5.5 score==3 | 0 | layer unavailable |
| editor_phase1_128 | All responses | 128 |  |
| editor_phase1_128 | GPT-4.1 score>=2 | 57 |  |
| editor_phase1_128 | GPT-4.1 score==3 | 3 | sparse centroid n=3 |
| editor_phase1_128 | GPT-5.5 score>=2 | 0 | layer unavailable |
| editor_phase1_128 | GPT-5.5 score==3 | 0 | layer unavailable |
| playwright | All responses | 60 |  |
| playwright | GPT-4.1 score>=2 | 54 |  |
| playwright | GPT-4.1 score==3 | 49 |  |
| playwright | GPT-5.5 score>=2 | 54 |  |
| playwright | GPT-5.5 score==3 | 40 |  |
| trickster_phase1_1200 | All responses | 1200 |  |
| trickster_phase1_1200 | GPT-4.1 score>=2 | 1200 |  |
| trickster_phase1_1200 | GPT-4.1 score==3 | 1198 |  |
| trickster_phase1_1200 | GPT-5.5 score>=2 | 0 | layer unavailable |
| trickster_phase1_1200 | GPT-5.5 score==3 | 0 | layer unavailable |

## Centroid Counts

Centroids are computed for each available non-empty layer. Published centroids are included separately for each role/run. Computed centroids with n < 5 are shown but marked sparse.

## Sparse-Layer Warnings

- `editor_matched64_1024` / GPT-4.1 score==3: sparse centroid n=2
- `editor_matched64_1024` / GPT-5.5 score>=2: layer unavailable
- `editor_matched64_1024` / GPT-5.5 score==3: layer unavailable
- `editor_phase1_128` / GPT-4.1 score==3: sparse centroid n=3
- `editor_phase1_128` / GPT-5.5 score>=2: layer unavailable
- `editor_phase1_128` / GPT-5.5 score==3: layer unavailable
- `trickster_phase1_1200` / GPT-5.5 score>=2: layer unavailable
- `trickster_phase1_1200` / GPT-5.5 score==3: layer unavailable

Sparse editor score==3 layers should be used as visual reference points only, not as stable centroid estimates.

## Viewer

Viewer path: `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer.html`

Local open instructions:

```bash
open research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer.html
```

The viewer has role/run and projection selectors, toggleable layers for published centroids, all-response clouds, GPT-4.1 layers, GPT-5.5 layers when available, and covariance ellipses where n is sufficient.

## Main Geometry Viewer

The main persona geometry explorer was **not modified**. This task created a new standalone layered activation-cloud viewer.
