# Activation Cloud Eigenvector Angle Analysis

Startup status: **STARTUP VERIFIED**.

## Roles/Runs and Layers

Analyzed role/run views: `amateur`, `playwright`, `trickster_phase1_1200`, `editor_phase1_128`, and `editor_matched64_1024`.
Layers considered: all responses, GPT-4.1 score>=2, GPT-4.1 score==3, GPT-5.5 score>=2 when available, and GPT-5.5 score==3 when available.

## Sparse-Layer Warnings

- `trickster_phase1_1200` / GPT-5.5 score>=2: n=0 (unavailable)
- `trickster_phase1_1200` / GPT-5.5 score==3: n=0 (unavailable)
- `editor_phase1_128` / GPT-4.1 score==3: n=3 (sparse/unstable n<10)
- `editor_phase1_128` / GPT-5.5 score>=2: n=0 (unavailable)
- `editor_phase1_128` / GPT-5.5 score==3: n=0 (unavailable)
- `editor_matched64_1024` / GPT-4.1 score==3: n=2 (sparse/unstable n<10)
- `editor_matched64_1024` / GPT-5.5 score>=2: n=0 (unavailable)
- `editor_matched64_1024` / GPT-5.5 score==3: n=0 (unavailable)

## Dominant All-Response Orientations

| role/run | n | PC1-PC2 angle | dominant 3D variance share | anisotropy | diff PC1 | diff PC2 | diff +45 diagonal | diff assistant proxy | diff upper-region proxy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `amateur` | 60 | -34.88 | 55.68% | 3.42 | 34.88 | 55.12 | 79.88 | 49.58 | 13.46 |
| `playwright` | 60 | -12.90 | 71.39% | 6.37 | 12.90 | 77.10 | 57.90 | 27.61 | 8.52 |
| `trickster_phase1_1200` | 1200 | -87.37 | 53.67% | 4.58 | 87.37 | 2.63 | 47.63 | 77.93 | 65.95 |
| `editor_phase1_128` | 128 | -31.02 | 64.12% | 5.37 | 31.02 | 58.98 | 76.02 | 45.73 | 9.60 |
| `editor_matched64_1024` | 64 | -41.55 | 62.46% | 5.42 | 41.55 | 48.45 | 86.55 | 56.26 | 20.13 |

## Reference Directions

- PC1 axis: 0.00 degrees (definition).
- PC2 axis: 90.00 degrees (definition).
- Positive PC1 / positive PC2 diagonal: 45.00 degrees (definition).
- Assistant-axis projection proxy: 14.70 degrees (regress stored axis_projections on PC1 and PC2).
- Empirical high-PC1/high-PC2 region proxy: -21.42 degrees (dominant PC1-PC2 direction among 32 roles with PC1 and PC2 >= 60th percentile).

Assistant-axis estimate: {
  "available": true,
  "method": "linear_regression_axis_projection_on_pc1_pc2",
  "angle_deg": 14.70202102556749,
  "coefficients_pc1_pc2": [
    0.0028823668661604467,
    0.0007562834615648003
  ],
  "intercept": -0.0806154299802939,
  "r2": 0.9663863471709642,
  "note": "Proxy gradient estimated from stored role axis_projections; not a separately recovered assistant-axis vector in PCA coordinates.",
  "upper_pc1_pc2_region_proxy": {
    "angle_deg": -21.422151159414,
    "n_roles": 32,
    "method": "roles with PC1 and PC2 >= 60th percentile",
    "example_roles": [
      "activist",
      "advocate",
      "assistant",
      "coach",
      "collaborator",
      "entrepreneur",
      "expatriate",
      "facilitator",
      "guide",
      "instructor"
    ]
  }
}

## Boundary-Distance Summary

| role/run | centroid | PC1 pct | PC2 pct | high-PC1 distance | high-PC2 distance | nearest roles |
|---|---|---:|---:|---:|---:|---|
| `amateur` | published | 47.64 | 96.36 | 48.41 | 38.04 | amateur:0.00; newlywed:7.59; divorcee:10.66; patient:11.28; parent:14.29 |
| `playwright` | published | 39.27 | 65.82 | 57.97 | 73.53 | playwright:0.00; evangelist:11.43; zeitgeist:12.23; hedonist:13.03; soldier:13.35 |
| `trickster_phase1_1200` | published | 17.09 | 82.91 | 83.18 | 58.37 | trickster:0.00; jester:11.77; rogue:12.57; rebel:13.50; absurdist:13.55 |
| `editor_phase1_128` | published | 86.91 | 53.82 | 13.54 | 80.23 | editor:0.00; summarizer:2.16; negotiator:3.52; pharmacist:4.10; psychologist:4.21 |
| `editor_matched64_1024` | published | 86.91 | 53.82 | 13.54 | 80.23 | editor:0.00; summarizer:2.16; negotiator:3.52; pharmacist:4.10; psychologist:4.21 |

## Interpretation

**Observed.** The all-response clouds are not uniformly circular: editor, amateur, playwright, and trickster all show anisotropy. Playwright and the two editor runs have the strongest all-response anisotropy in this set; amateur is less elongated; trickster is still anisotropic but its dominant PC1-PC2 orientation is qualitatively different. The dominant all-response PC1-PC2 angles should be read as line orientations, so positive and negative arrow signs are equivalent.

**Observed.** Amateur, playwright, and both editor all-response clouds align much better with the empirical high-PC1/high-PC2 region proxy (-21.42 degrees) than with the positive +45 degree PC1-PC2 diagonal. Their angular differences from that upper-region proxy are 13.46, 8.52, 9.60, and 20.13 degrees respectively. Trickster is the exception: its all-response orientation is nearly PC2-vertical (-87.37 degrees), only 2.63 degrees from the PC2 axis and 65.95 degrees from the upper-region proxy.

**Observed.** The assistant-axis proxy is estimated from stored role axis projections by regression on PC1 and PC2. It points at +14.70 degrees with R2=0.966 for that two-dimensional projection. All-response playwright is the closest of the five all-response clouds to this proxy (27.61 degrees away), while amateur/editor all-response clouds are farther and trickster is farthest.

**Inferred.** Amateur, playwright, and editor support the visual impression of a shared PC1-PC2 transition orientation, but the best-matching reference is a shallow negative-slope upper-region direction, not the naive positive-PC1/positive-PC2 diagonal. Editor is strongly elongated, but its role-expression-retained score==3 layers are sparse, so the editor result is better evidence about all-response/procedural-assistant collapse geometry than about stable editor-role expression.

**Inferred.** Trickster does not share the amateur/playwright/editor orientation pattern. Its retained set is large, its GPT-4.1 score>=2 and score==3 layers are effectively the same cloud, and its dominant PC1-PC2 direction is near-vertical. That does not prove a different causal mechanism; it does suggest trickster is not constrained by the same visible PC1-PC2 boundary pattern in these saved runs.

**Speculative.** Distance from the high-PC1 and high-PC2 boundaries may affect observable cloud shape, but this dataset has only five role/run views and repeated editor variants. The boundary scatter should be used to motivate a targeted next role, not to fit a general law. The apparent editor/amateur/playwright alignment should be retested with a negative-PC2 role and another non-editor high-PC1 role before becoming paper-level language.

## Negative-PC2 Role Test Recommendation

Current evidence supports running a negative-PC2 comparison role if another small GPU pilot is launched. `student` remains a useful candidate if the goal is to test whether a formative/developmental role below the current positive-PC2 edge shows a different cloud orientation or boundary relation; however, because `student` may be socially/developmentally loaded, a second negative-PC2 but more integrated/abstract role should be shortlisted as a contrast before launch.

## Output Files

- `cloud_orientation_metrics.csv`
- `cloud_orientation_eigendecomp.json`
- `cloud_reference_direction_table.csv`
- `cloud_angle_differences.csv`
- `assistant_axis_direction_estimate.json`
- `role_boundary_distance_metrics.csv`
- `cloud_orientation_overview_pc1_pc2.png`
- `cloud_orientation_boundary_scatter.png`
- `cloud_orientation_report_figure.png`
- `cloud_orientation_interactive.html`
