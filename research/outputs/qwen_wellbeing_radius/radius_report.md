# Qwen well-being radius analysis

All 275 personas; exact cosine-based scores; fixed trait and score standardization. Five PCs primary, three PCs sensitivity. No model inference was performed.

## Results

Every compromise improves both bridge scores. In five PCs it retains at least 96.55% of each individually attainable gain across all 825 persona-radius cases (median about 97.7%). The three-PC sensitivity minimum is 96.44%. No separated second/third peaks were detected. The 45-degree alternatives retain about 71%, and none meets the 80% or 90% threshold. At the largest five-PC radius, 17 of 275 compromise paths exceed the reference coverage threshold.

| dimensions | radius_fraction | radius | compromise_min_retained_gain | compromise_median_retained_gain | compromise_both_positive | compromise_outside_support | alternatives_at_least_80pct | alternatives_at_least_90pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 0.25 | 4.1776 | 0.9652 | 0.9761 | 275 | 11 | 0 | 0 |
| 3 | 0.5 | 8.3552 | 0.9649 | 0.9759 | 275 | 18 | 0 | 0 |
| 3 | 1.0 | 16.7103 | 0.9644 | 0.9756 | 275 | 27 | 0 | 0 |
| 5 | 0.25 | 4.1776 | 0.9662 | 0.9769 | 275 | 10 | 0 | 0 |
| 5 | 0.5 | 8.3552 | 0.966 | 0.9767 | 275 | 10 | 0 | 0 |
| 5 | 1.0 | 16.7103 | 0.9655 | 0.9763 | 275 | 17 | 0 | 0 |

Across 3300 individual-bridge multistart searches, 0 detected more than one converged maximum separated by at least 15 degrees. This limited multistart test is not a mathematical proof of peak count.

Alternative counts refer to two angularly constrained candidates for each of two bridges per persona (1,100 per dimension/radius setting). They must be at least 45 degrees from their own bridge optimum and from the preceding alternative. They are different viable routes, not additional unconstrained peaks. Their retained-gain labels use the bridge for which they were optimized; the other bridge may gain less or decline.

## Read the outputs

radius_candidates.csv contains 11,550 candidates: 275 personas × two dimensionalities × three radii × seven directions. For each it records the unit PC direction, actual PC displacement, C1–C5 change in frozen Qwen consensus-score standard deviations, baseline/end/delta under both well-being bridges, each bridge’s fraction of its own attainable gain, angles to both optima, and path/endpoint support diagnostics. Delta well-being is additionally provided in each score’s original persona-population SD units. Native AA21 and AA22 score units differ; neither score delta is a demonstrated human treatment effect.

Open radius_explorer.html for a persona selector and readable candidate cards. It contains all results and works without network access. The raw CSV preserves full precision.

## Example: romantic, five PCs, medium radius

| candidate | delta_bigfive | delta_direct | bigfive_gain_fraction | direct_gain_fraction | path_outside_reference_support |
| --- | --- | --- | --- | --- | --- |
| bigfive_optimum | 0.1274 | 0.1482 | 1.0 | 0.8714 | False |
| direct_optimum | 0.111 | 0.17 | 0.8707 | 1.0 | False |
| compromise | 0.1233 | 0.1645 | 0.9672 | 0.9672 | False |
| bigfive_alternative_1 | 0.0902 | 0.1079 | 0.7082 | 0.6343 | False |
| bigfive_alternative_2 | 0.09 | 0.1205 | 0.7062 | 0.7086 | False |
| direct_alternative_1 | 0.0886 | 0.1206 | 0.695 | 0.7093 | False |
| direct_alternative_2 | 0.0791 | 0.1203 | 0.6211 | 0.7075 | False |

| candidate | delta_PC1 | delta_PC2 | delta_PC3 | delta_PC4 | delta_PC5 |
| --- | --- | --- | --- | --- | --- |
| bigfive_optimum | 5.4089 | -2.6879 | -5.5358 | 1.5746 | 0.4518 |
| direct_optimum | 1.8289 | -1.9951 | -7.6516 | 1.8125 | 0.8071 |
| compromise | 3.7429 | -2.4231 | -6.8155 | 1.7476 | 0.6505 |
| bigfive_alternative_1 | 2.9394 | -5.1907 | -4.5458 | -3.6716 | 0.2832 |
| bigfive_alternative_2 | 1.7133 | -4.7222 | -5.1208 | 0.6162 | -4.2394 |
| direct_alternative_1 | 1.8427 | -4.9487 | -5.4842 | -3.4152 | 0.4282 |
| direct_alternative_2 | 0.8555 | -4.0149 | -4.619 | -0.052 | 5.6231 |

| candidate | delta_C1_sd | delta_C2_sd | delta_C3_sd | delta_C4_sd | delta_C5_sd |
| --- | --- | --- | --- | --- | --- |
| bigfive_optimum | -0.2879 | 0.0549 | 0.2493 | -0.1572 | -0.0413 |
| direct_optimum | -0.2005 | 0.0154 | 0.3976 | -0.2319 | -0.0325 |
| compromise | -0.2524 | 0.0366 | 0.3343 | -0.2006 | -0.0382 |
| bigfive_alternative_1 | -0.1451 | 0.218 | 0.198 | 0.0526 | 0.1416 |
| bigfive_alternative_2 | -0.1876 | 0.1442 | 0.1958 | -0.3305 | 0.2611 |
| direct_alternative_1 | -0.1245 | 0.2013 | 0.2593 | 0.0167 | 0.1392 |
| direct_alternative_2 | -0.0843 | 0.1572 | 0.2902 | 0.0763 | -0.2742 |

## Geometry, controls, and limits

The three radii are 4.1776, 8.3552, 16.7103 raw activation-distance units: 0.25, 0.5, and 1 times the median fifth-neighbor distance in the original five-PC cloud. The same radii are used in three PCs. Movement is on the sphere perimeter, not rescaled PC coordinates. The original full-vector residual outside the selected PCs stays fixed.

Both bridges are scored as s(h)=b·h/||h||+c after the exact displacement h→h+Pδ. The compromise maximizes the smaller of the two achieved-gain fractions relative to each bridge’s separate optimum at that persona, radius and dimensionality. This treats the two objectives symmetrically without adding incomparable raw scores.

Consensus changes use Qwen’s frozen model-specific GCCA scoring weights and trait standardization. They describe the change in Qwen’s expression of the shared components, not a new jointly estimated consensus coordinate involving hypothetical movements in all three models. C1 expressive intensity; C2 abstract reflection; C3 compassionate understanding; C4 integrative imagination; C5 decisive commitment. Positive/negative changes refer to the established orientations.

Support is descriptive. The endpoint and five points along the path are compared with the original persona cloud using fifth-neighbor distance. The reference threshold is the 95th percentile of leave-self-out fifth-neighbor distances; queries may include the starting persona as one neighbor. Paths exceeding it are flagged, not excluded. This low-dimensional coverage check does not establish human plausibility. Geometry and bridge-weight uncertainty are not propagated in this run.

No finite-radius direction should be interpreted as an established behavioral intervention. These are changes in frozen geometric readout scores; behavioral consequences would require a separate model experiment.

## Verification

```json
{
  "pc_coordinate_max_error": 3.132578214604109e-07,
  "trait_cosine_max_error": 1.9185762617501823e-08,
  "role_norm_max_error": 2.0567546243910328e-07,
  "bridge_baseline_max_error": 2.537107046673981e-08,
  "consensus_baseline_max_error": 1.9984014443252818e-14,
  "gradient_finite_difference_max_error": 3.4678260263376615e-11,
  "endpoint_full_vector_score_max_error": 1.84297022087776e-14,
  "failed_individual_optimizer_starts": 25,
  "candidate_rows": 11550,
  "maximum_sphere_norm_error": 7.105427357601002e-15,
  "median_fifth_neighbor_distance_5pc": 16.710327697140524,
  "radii": [
    4.177581924285131,
    8.355163848570262,
    16.710327697140524
  ],
  "model_identity": "unknown",
  "no_model_inference": true,
  "saved_rows_finite_and_unique": true,
  "all_optimized_scores_beat_sampled_starts": true,
  "all_candidate_gains_bounded_by_individual_optima": true,
  "minimum_alternative_pairwise_angle_degrees": 44.999999999950184,
  "compromise_beats_both_single_objective_choices_on_maximin": true
}
```

The public Qwen tensors were hash-checked against the Hugging Face LFS manifest. A restricted tensor-only decoder reads the known bfloat16 archive format without importing arbitrary pickle classes. Complete trait vectors are reconstructed from saved trait PCA artifacts. Original role norms, PC coordinates, trait cosines, bridge baselines, and consensus scores are reproduced; analytic gradients are checked against finite differences; every endpoint score is independently recomputed from the full moved vector.

The compact qwen_mean_roles.npz and radius_geometry.npz preserve geometry and readouts; existing repository trait-PCA artifacts reconstruct the 240 trait directions. Together with run_radius.py, they allow retrieval of any candidate’s full 240-trait change without storing a redundant large table. analysis_specification.md records choices made before optimization. Source inputs and hashes are in source_manifest.json. No public viewer was changed.
