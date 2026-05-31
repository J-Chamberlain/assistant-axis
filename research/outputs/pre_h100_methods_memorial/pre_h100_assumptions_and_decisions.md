# Pre-H100 Assumptions And Decisions

Model used for synthesis and documentation: GPT-5.5.

## Core Decision

The project will use `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv` as the primary H100 validation manifest.

Rationale: it is the first prompt battery that satisfies explicit inherited-geometry percentile criteria across all six PC tails while preserving interior controls and passing leakage/safety filters.

## What Was Decided

1. Use the frozen lightweight text forecaster as the prediction source.
   - Chosen model: role-trained leakage-control elastic-net TF-IDF.
   - Stable model hash: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`.
   - Reason: role-heldout performance is stronger than trait-heldout performance, and the model is lightweight, reproducible, and does not require frontier-model inference.

2. Use inherited persona PCA percentiles, not prior prompt-battery percentiles.
   - Reason: the H100 validation should test outlying regions of the inherited activation geometry, not merely edges of a previously generated prompt set.

3. Use the percentile-edge battery instead of the first or expanded batteries.
   - First battery: useful but incomplete, 11/27 cells populated.
   - Adaptive expansion: improved high-PC3/high-PC2 coverage, but still not a full inherited-percentile edge test.
   - Percentile-edge battery: passes all explicit readiness criteria.

4. Treat H100 as validation, not training.
   - The forecaster must remain frozen.
   - Prompt battery should not be edited after seeing activation results.
   - PCA basis should not be refit on H100 outputs.

5. Validate response-state geometry.
   - Assistant Axis vectors are response-token activation vectors.
   - H100 should mean-pool generated response-token residual activations and project them into the existing persona PCA basis.
   - Prompt-state activation forecasting remains a separate future question.

## Assumptions That Must Hold

- Qwen/Qwen3-32B layer-48 extraction matches the geometry source used by `geometry_viz_data.json`.
- Existing PCA basis, sign convention, and scaling are preserved.
- Prompt IDs and predicted coordinates from the manifest are treated as immutable run metadata.
- Generated responses are non-empty and not dominated by refusals.
- Response-token pooling convention is stable across prompts.
- Runtime code saves response text, generation settings, prompt ID, observed coordinates, and activation shard references.

## Known Caveats

- The text forecaster was trained on released prompt artifacts, not unconstrained user conversations.
- The edge battery is deliberately not representative of ordinary usage.
- Some tail prompts use strong coefficient-aligned phrasing to reach inherited percentile thresholds.
- Passing pre-H100 readiness does not prove response activation prediction; it only means the validation set is adequate for testing that claim.
- Safety-adjacent prompts are non-operational and do not constitute a jailbreak benchmark.
- If validation fails, the likely explanations include response-state mismatch, prompt-state requirements, projection convention error, or insufficiently rich text features.

## Success Interpretation

Proof-of-concept success: at least one PC shows meaningful positive forecast-vs-observed correlation.

Strong success: PC1 and PC3 validate, especially PC3-high movement.

Full success: all three PCs validate and results are not driven by one prompt family.

## Failure Interpretation

Failure means the frozen text forecaster did not generalize to measured response activation geometry on the novel battery. It would not invalidate the descriptive persona geometry, trait/persona relation, or prompt-artifact forecasting result. It would imply that execution-time activation forecasting likely needs prompt-state activations, response-derived supervision, richer features, or a different model.
