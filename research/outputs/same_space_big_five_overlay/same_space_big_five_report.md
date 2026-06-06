# Same-Space Activation-Derived Big Five Overlay

## Startup Status

Startup verification passed against the canonical raw files listed in `research/STARTUP_MANIFEST.md` before this analysis began.

## Overview

This rebuild constructs Big Five directions directly from the released 240 trait vectors for Qwen, Llama, and Gemma. For each dimension, positive facet trait vectors are averaged, negative facet trait vectors are averaged, and the normalized difference is used as an activation-space direction. Role vectors are then projected onto those directions.

Required label: **Activation-derived Big Five from 240 trait vectors**.

Required caveat: **Same-space trait-vector projection, not independent psychometric rating.**

## Data Sources

- Qwen role/trait vectors: `downloads/hf_vectors/qwen-3-32b/`
- Llama role/trait vectors: `downloads/hf_vectors/llama-3.3-70b/`
- Gemma role/trait vectors: `downloads/hf_vectors/gemma-2-27b/`
- Coordinates/clusters: `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`
- Old heuristic overlay for comparison only: `research/visualizations/bigfive_geometry_overlay_data.csv`

The old heuristic source was not used to construct directions or scores.

## Models Generated

- Qwen/Qwen3-32B
- Llama-3.3-70B
- Gemma-2-27B

Each model has 275 role vectors and 240 trait vectors available locally.

## Facet Sets

See `big_five_trait_facet_sets.csv` for every included positive/negative trait, rationale, polarity convention, and missing desired trait. All included facets are present in the 240-trait inventory.

## PC Correlations

Largest activation-derived Big Five versus PC correlations:

model         dimension target   n  pearson_r  spearman_r
llama conscientiousness    pc2 275  -0.938976   -0.947211
llama       neuroticism    pc2 275   0.937731    0.950319
 qwen     agreeableness    pc3 275  -0.907201   -0.879299
 qwen          openness    pc1 275  -0.886957   -0.902858
 qwen conscientiousness    pc1 275   0.873581    0.903624
 qwen       neuroticism    pc1 275  -0.873298   -0.901477
gemma          openness    pc1 275  -0.804406   -0.849936
llama     agreeableness    pc2 275  -0.792958   -0.746514
gemma       neuroticism    pc1 275  -0.777656   -0.837279
 qwen      extraversion    pc1 275  -0.777066   -0.828594
llama          openness    pc1 275  -0.735804   -0.821222
gemma      extraversion    pc2 275   0.711701    0.612089
gemma conscientiousness    pc1 275   0.698183    0.772833
gemma conscientiousness    pc2 275  -0.665450   -0.531545
gemma     agreeableness    pc3 275  -0.627053   -0.593826
gemma     agreeableness    pc1 275   0.616476    0.671810
llama      extraversion    pc3 275  -0.609063   -0.700240
llama      extraversion    pc2 275   0.583822    0.683983

## Old Heuristic Overlay Comparison

See `same_space_big_five_old_overlay_comparison.csv`. Agreement with the old heuristic overlay is reported only as descriptive continuity, not validation. The old overlay remains partly activation-cluster-derived and role-name heuristic.

## Stability and Facet Sensitivity

Stable dimension/model combinations with leave-one-facet minimum role-score Pearson >= 0.95 and direction cosine >= 0.90:

model         dimension  min_direction_cosine  min_role_score_pearson  median_role_score_pearson  facets_tested
gemma     agreeableness              0.996845                0.998720                   0.999680             20
gemma conscientiousness              0.994572                0.998840                   0.999233             15
gemma      extraversion              0.990631                0.992106                   0.998667             14
gemma       neuroticism              0.993749                0.992499                   0.998786             19
gemma          openness              0.988463                0.990239                   0.998122             18
llama     agreeableness              0.997340                0.998868                   0.999776             20
llama conscientiousness              0.993634                0.997789                   0.998977             15
llama      extraversion              0.987754                0.983253                   0.995957             14
llama       neuroticism              0.993256                0.993586                   0.998941             19
llama          openness              0.991638                0.990214                   0.998589             18
 qwen     agreeableness              0.998163                0.997953                   0.999472             20
 qwen conscientiousness              0.995128                0.999105                   0.999621             15
 qwen      extraversion              0.990259                0.996571                   0.999303             14
 qwen       neuroticism              0.993623                0.996238                   0.998892             19
 qwen          openness              0.990163                0.992422                   0.998695             18

Potentially weak or facet-sensitive combinations:

None under the weak threshold.

## PC1-Band Checks for Extraversion and Neuroticism

Extraversion PC2-related checks:

model                 target   n  pearson_r  spearman_r
gemma                    pc2 275   0.711701    0.612089
gemma  pc2_central_pc1_10pct  27   0.869989    0.831502
gemma  pc2_central_pc1_20pct  55   0.852579    0.795382
gemma  pc2_central_pc1_40pct 109   0.851934    0.844287
gemma pc2_residual_after_pc1 275   0.711701    0.612089
llama                    pc2 275   0.583822    0.683983
llama  pc2_central_pc1_10pct  27   0.347984    0.536630
llama  pc2_central_pc1_20pct  55   0.502906    0.618326
llama  pc2_central_pc1_40pct 109   0.538652    0.674655
llama pc2_residual_after_pc1 275   0.583822    0.683983
 qwen                    pc2 275   0.571833    0.460546
 qwen  pc2_central_pc1_10pct  27   0.911617    0.860806
 qwen  pc2_central_pc1_20pct  55   0.881852    0.852742
 qwen  pc2_central_pc1_40pct 109   0.825302    0.774460
 qwen pc2_residual_after_pc1 275   0.571833    0.460546

Neuroticism PC2-related checks:

model                 target   n  pearson_r  spearman_r
gemma                    pc2 275   0.577802    0.451024
gemma  pc2_central_pc1_10pct  27   0.909110    0.872405
gemma  pc2_central_pc1_20pct  55   0.911877    0.876623
gemma  pc2_central_pc1_40pct 109   0.888194    0.872931
gemma pc2_residual_after_pc1 275   0.577802    0.451024
llama                    pc2 275   0.937731    0.950319
llama  pc2_central_pc1_10pct  27   0.952169    0.916972
llama  pc2_central_pc1_20pct  55   0.915487    0.953391
llama  pc2_central_pc1_40pct 109   0.935425    0.946038
llama pc2_residual_after_pc1 275   0.937731    0.950319
 qwen                    pc2 275   0.313040    0.191663
 qwen  pc2_central_pc1_10pct  27   0.466232    0.485348
 qwen  pc2_central_pc1_20pct  55   0.421513    0.458586
 qwen  pc2_central_pc1_40pct 109   0.537874    0.435826
 qwen pc2_residual_after_pc1 275   0.313040    0.191663

## Interpretation

### Observed

- Activation-derived Big Five directions can be built for all three released-vector model spaces using only available 240-trait facets.
- Qwen, Llama, and Gemma all produce overlay-ready role scores for all 275 roles.
- Several dimensions show strong PC relationships, but the signs and axis associations should be read as same-space trait-composite geometry, not psychometrics.
- Leave-one-facet sensitivity is generally strong when many facets are available; dimensions with fewer or more semantically substituted facets should be treated more cautiously.

### Inferred

- This activation-derived layer should replace the old heuristic overlay for evidence-bearing same-space trait-vector visualization.
- The old heuristic overlay can remain only as a historical or heuristic semantic layer if explicitly labeled as such.
- Extraversion and Neuroticism PC2 relevance should be read through PC1-band/residual checks because global correlations can be PC1-entangled.

### Speculative

- A future stronger Big Five layer would compare this same-space vector composite against blinded independent role or response ratings. That would test whether activation-derived trait-vector composites correspond to external Big Five judgments.

### Unknown

- Whether these activation-space Big Five directions correspond to human psychometric constructs beyond the selected trait vocabulary.
- Whether generated behavior, rather than role vectors, would show the same Big Five projections.

## Recommendation

Use this layer to **replace** the current heuristic cluster-conditioned Big Five overlay when the goal is activation-derived same-space evidence. Keep it clearly labeled beside, not as, independent psychometric validation.
