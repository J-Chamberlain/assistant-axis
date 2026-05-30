# Novel Prompt Battery For H100 Geometry Validation

Model used for synthesis and script authoring: GPT-5.5.

## Forecaster

- Selected forecaster: role-trained leakage-control elastic-net TF-IDF.
- Serialized model path: `research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib`
- Forecaster retrained: True
- Model SHA256: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Text fields used: `role description + positive instructions + behavioral questions, with explicit target role name replaced by [TARGET]; eval prompts excluded`
- Training examples: 275
- Training target: role/persona PC1, PC2, PC3 from `research/visualizations/geometry_viz_data.json`.

The forecaster predicts continuous persona-space PC coordinates, not discrete labels.

## Target Grid

The target grid uses observed role/persona PCA coordinate distributions. Each PC is split into low/mid/high quantile bands using 35% and 65% cut points. This yields 27 target cells. Boundary and mixed cells receive priority because they test the geometry more strongly than central prompts.

## Prompt Generation

Candidate prompts were generated offline from behavioral pressure templates, not copied from Assistant Axis artifacts and not produced by an external API. The generator used target-region descriptions in behavioral terms rather than explicit role names. The frozen forecaster was used only as a design/filtering tool.

## Coverage

- Final prompt count: 120
- Candidate count: 1036
- Populated target cells: 11 / 27
- Explicit role-name flags in final battery: 0
- Maximum artifact-similarity score in final battery: 0.205
- Mean artifact-similarity score in final battery: 0.069

Predicted coordinate ranges:

- PC1: -20.474 to 22.187
- PC2: -24.490 to 12.958
- PC3: -9.096 to 18.527

Prompt family counts:

```json
{
  "mixed_boundary_prompts": 52,
  "manual_holdout_prompts": 24,
  "cluster_region_probes_without_role_names": 19,
  "safety_adjacent_prompts": 13,
  "neutral_controls": 12
}
```

Under-covered cells:

```text
pc1_high__pc2_high__pc3_high
pc1_high__pc2_high__pc3_low
pc1_high__pc2_high__pc3_mid
pc1_high__pc2_low__pc3_high
pc1_high__pc2_low__pc3_low
pc1_high__pc2_low__pc3_mid
pc1_high__pc2_mid__pc3_high
pc1_high__pc2_mid__pc3_low
pc1_high__pc2_mid__pc3_mid
pc1_mid__pc2_high__pc3_high
pc1_mid__pc2_high__pc3_low
pc1_mid__pc2_high__pc3_mid
pc1_mid__pc2_low__pc3_high
pc1_mid__pc2_mid__pc3_high
pc1_mid__pc2_mid__pc3_low
pc1_mid__pc2_mid__pc3_mid
```

## Leakage Checks

Final prompts were checked for explicit role labels from a diagnostic role-name blocklist and for approximate TF-IDF similarity against released role and trait prompt artifacts. Final battery explicit-role flags are zero. The battery intentionally avoids explicit persona labels except no diagnostic-only explicit-role subset was included in this first version.

## Readiness Judgment

A frozen novel prompt battery has been constructed using the lightweight text-to-geometry forecaster as a design filter. The battery covers several boundary, interior, mixed, safety-adjacent, neutral-control, and manual-holdout regions of predicted persona space, but target-cell coverage is incomplete.

H100 validation is feasible, but under-covered regions should be treated cautiously. The battery is best described as a partial geometric validation set rather than a complete covering design. The manifest includes predicted coordinates for every prompt and preserves all candidates/rejection records, so the future H100 run can still test whether the forecaster's predicted addresses match measured activations in populated regions.

## Recommended H100 Execution Notes

- Use the `h100_prompt_run_manifest.csv` file as the frozen input.
- Recommended first batch size: all 120 prompts, single deterministic generation pass per prompt.
- Save full response text, prompt ID, exact model name, layer, token cap, generation settings, and one activation shard per prompt.
- Do not update the forecaster after seeing H100 measurements.
- Primary validation metric: measured response-coordinate delta from predicted PC1/PC2/PC3.
- Secondary metric: whether manual holdouts and neutral controls behave as expected.
