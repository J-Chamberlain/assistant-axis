# Pre-H100 Methods Memorial

Model used for synthesis and documentation: GPT-5.5.

## Executive Summary

Pre-H100 preparation is complete for a targeted validation of whether a lightweight text-only forecaster predicts measured response activation geometry on novel prompts. The project now has a frozen role-trained leakage-control elastic-net TF-IDF forecaster, a percentile-referenced edge-heavy prompt battery satisfying predefined readiness criteria, and a planned H100 method for comparing forecasted prompt addresses against independently measured Qwen/Qwen3-32B layer-48 response activation geometry.

This memo separates four stages that should not be conflated: descriptive persona geometry analysis, explanatory modeling of existing persona geometry, text-to-geometry forecasting from released prompt artifacts, and the pending H100 activation validation. No H100 result has yet established that the forecaster predicts actual response activations on novel prompts; that is the purpose of the next run.

## Source Files Reviewed

Startup and state:

- `research/STARTUP_MANIFEST.md`
- `research/RESEARCH_STATE.md`
- `research/THREAD_START.md`
- `research/CLAIMS_REGISTER.md`
- `research/FINDINGS_LEDGER.md`
- `research/RESEARCH_INDEX.md`

Geometry, validation, forecasting, and batteries:

- `research/visualizations/geometry_viz_data.json`
- `research/outputs/trait_persona_prediction/`
- `research/outputs/trait_space_interpretation/`
- `research/outputs/pc3_validation/`
- `research/outputs/prompt_artifact_inventory/`
- `research/outputs/prompt_to_geometry_forecasting/`
- `research/outputs/cluster_conditioned_axis_tests/`
- `research/outputs/novel_prompt_battery/`
- `research/outputs/novel_prompt_battery_expansion/`
- `research/outputs/novel_prompt_battery_percentile_edges/`

Chosen H100 manifest:

- `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv`

## Starting Point

The Assistant Axis dataset provides released role/persona and trait vectors derived from downstream response-token activations. These vectors are not prompt activations. They represent response-state geometry after a model has answered role or trait elicitation prompts.

Prompt-to-geometry forecasting is therefore a project extension. It asks whether prompt text contains enough information to forecast where a future generated response is expected to land in the inherited persona activation geometry. The H100 validation will test this extension by measuring actual response activations for novel prompts and comparing those observed coordinates to the frozen text forecaster's predictions.

## Persona-Axis Interpretation Work

Current working interpretations:

- PC1: convergence pressure versus degrees of freedom.
- PC2: integrated abstraction versus situated developmental immediacy.
- PC3: perturbation/intervention versus stabilization/repair.

Endpoint roles such as evaluator, poet, counselor, demon, caregiver, or auditor are evidence for these interpretations, not the interpretations themselves. The project has moved away from treating role labels as axis definitions. The current axis language is about the constraints and admissible operating modes that place roles in the geometry.

## Iterative Explanatory Improvement

The explanatory work moved from weaker semantic descriptions toward layered predictors of canonical Qwen activation PCA3D:

- Semantic baseline: about R2 0.389.
- Codex procedural/behavioral features: about R2 0.490.
- Claude Big Five-style features: about R2 0.613.
- Hierarchical trait plus procedural residual model: about R2 0.622.
- Residual hand-feature layer: about R2 0.632.
- Sem + Big Five + SVD15 prompt-register model: about R2 0.707.

These are explanatory analyses of existing persona geometry, not execution-time validation. They support a layered interpretation in which semantic topology, dispositional/trait structure, procedural operating mode, lexical/register structure, and residual developmental/liminal/collective structure all contribute to observed persona placement.

## Trait And Persona Relationship

Trait vectors and role/persona vectors occupy the same Qwen/Qwen3-32B layer-48 activation space. A persona-by-trait cosine matrix using 275 role vectors and 240 trait vectors reconstructs persona PCA coordinates at near-ceiling performance under ridge cross-validation: PC1 R2 0.999, PC2 R2 0.999, and PC3 R2 1.000.

That result supports trait-vector geometry as a strong same-space basis for persona placement. It does not reduce persona geometry to trait-only PCA. Direct PCA over the 240 trait vectors only moderately aligned with persona PC1, abs cosine 0.681, and weakly aligned with persona PC2 and PC3, abs cosine 0.194 and 0.065. Trait-only PC2 and PC3 reorganized into different axes, so the current interpretation remains layered rather than trait-reductionist.

## PC3 Validation

The strongest targeted validation for PC3 is the perturbation-stabilization study over 275 personas. It scored personas from names plus neutral role definitions, then joined scores to PC3 after scoring.

Key results:

- Global Pearson r about 0.529.
- Global Spearman r about 0.511.
- Cluster-controlled Pearson r about 0.491.
- Within-cluster pairwise ordering accuracy about 0.773.

PC3 is not moral valence. Positive PC3 includes perturbative or interventionist structure such as stress-testing, debugging, auditing, skeptical challenge, or vulnerability probing, including prosocial versions. Negative PC3 includes repair, mediation, caregiving, preservation, and stabilization. Prosocial perturbative roles matter for the interpretation.

## Prompt Artifact Availability

The prompt artifact inventory found the released materials needed to construct prompt-to-geometry forecasting datasets without regenerating original model responses:

- 275 role artifacts.
- 240 trait artifacts.
- 1 default row.
- Belmore prompt artifact dataset total: 516 rows.
- Trait artifacts include descriptions, five positive instructions, five negative instructions, forty behavioral questions, and a 0-100 evaluation prompt.
- Trait artifact names aligned exactly with Qwen trait vector names: 240/240.
- Role artifacts aligned with the 275 Qwen role vectors, excluding the expected `default` non-vector row.

Strict forecasting datasets excluded eval prompts and used leakage-control variants where explicit target names were replaced by `[TARGET]`.

## Lightweight Prompt-To-Geometry Forecaster

The selected forecaster is a leakage-controlled, role-trained elastic-net regression model over TF-IDF prompt-text features. It predicts continuous PC1, PC2, and PC3 coordinates. It does not predict discrete role labels.

Frozen forecaster:

- Manifest: `research/outputs/novel_prompt_battery/frozen_forecaster_manifest.json`
- Model: `research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib`
- Stable model hash: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Text fields: role description + positive instructions + behavioral questions, with explicit target role name replaced by `[TARGET]`; eval prompts excluded.

Held-out role performance:

- Mean R2 about 0.621.
- PC1 R2 about 0.783.
- PC2 R2 about 0.577.
- PC3 R2 about 0.504.

Held-out trait performance:

- Mean R2 about 0.389.
- PC1 R2 about 0.414.
- PC2 R2 about 0.304.
- PC3 R2 about 0.450.

The role-based forecaster was selected as the primary validation baseline because the H100 prompt battery is intended to validate persona-space response geometry, and role-heldout performance is stronger than trait-heldout performance. The model is lightweight: it does not require a frontier LLM, Qwen inference, or activation extraction at prediction time.

## Why Not Use LLM Judging As Runtime Forecaster

LLM judges remain useful for interpretation, rubric validation, and axis-disentanglement studies. They are not the chosen runtime forecaster because they introduce latency, cost, stochasticity, and an additional frontier-model dependency. The deployable predictor being tested here is deliberately simple: TF-IDF features plus elastic-net regression.

## Cluster Conditioning Result

Cluster conditioning helped as calibration or intercept information, especially for PC1 and PC2, but it was not selected as the primary frozen predictor.

Reported results:

- PC1 direct R2 0.296 to oracle-cluster R2 0.811.
- PC2 direct R2 0.416 to oracle-cluster R2 0.718.
- Predicted-cluster PC1 R2 0.647.
- Predicted-cluster PC2 R2 0.520.
- Text-to-cluster accuracy about 0.687.
- Macro F1 about 0.404.

Hard cluster errors are costly. Cluster conditioning is therefore diagnostic/calibration support rather than the primary H100 validation model.

## Prompt Battery Development

Prompt battery development proceeded in three stages.

1. First novel prompt battery: `research/outputs/novel_prompt_battery/`
   - 120 prompts.
   - Low leakage: zero explicit role-name flags, artifact similarity max 0.205 and mean 0.069.
   - Limitation: only 11/27 target cells populated; high-PC1 and high-PC2 under-covered.

2. Adaptive high-PC3/high-PC2 expansion: `research/outputs/novel_prompt_battery_expansion/`
   - 60 supplemental prompts.
   - 516 logged candidates.
   - Improved combined coverage to 16/27 cells.
   - Limitation: still moderate rather than inherited-percentile frontier coverage.

3. Percentile-edge battery: `research/outputs/novel_prompt_battery_percentile_edges/`
   - 100 prompts.
   - Uses inherited role/persona PCA percentiles.
   - Passes explicit tail, shoulder/edge, interior-control, size, leakage, and safety criteria.

Earlier batteries were useful design iterations but not sufficient for the scientific goal of testing outlying regions of inherited persona activation geometry. The percentile-edge battery is the chosen validation set because it is explicitly referenced to inherited role/persona coordinate percentiles and passes all predeclared readiness criteria.

## Percentile-Edge Success Criteria

The final readiness rule uses the inherited role/persona PCA coordinate distribution from `research/visualizations/geometry_viz_data.json`.

Thresholds:

- PC1: p20=-32.056, p35=-13.924, p65=19.979, p80=31.909.
- PC2: p20=-16.333, p35=-8.534, p65=4.215, p80=16.307.
- PC3: p20=-11.810, p35=-5.698, p65=4.816, p80=11.642.

Required criteria:

- At least 8 prompts with PC1 <= PC1_p20.
- At least 8 prompts with PC1 >= PC1_p80.
- At least 8 prompts with PC2 <= PC2_p20.
- At least 8 prompts with PC2 >= PC2_p80.
- At least 8 prompts with PC3 <= PC3_p20.
- At least 8 prompts with PC3 >= PC3_p80.
- At least 12 shoulder/edge prompts outside the 35th-to-65th percentile band on at least two axes.
- At least 20 interior controls with all PCs between the 35th and 65th percentiles.
- Final battery size 100-160 prompts after filters.
- Zero explicit role-name flags.
- Zero operational-harm flags.

## Final Percentile-Edge Battery

Final battery: `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_prompt_battery.csv`

Recommended H100 manifest: `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv`

Pass table:

| criterion | minimum | count | pass |
|---|---:|---:|---|
| pc1_lower_tail | 8 | 12 | true |
| pc1_upper_tail | 8 | 11 | true |
| pc2_lower_tail | 8 | 34 | true |
| pc2_upper_tail | 8 | 8 | true |
| pc3_lower_tail | 8 | 8 | true |
| pc3_upper_tail | 8 | 16 | true |
| shoulder_edge | 12 | 58 | true |
| interior_control | 20 | 20 | true |
| final_battery_size | 100 | 100 | true |
| filters | 0 | 0 | true |

Leakage/safety values:

- Explicit role-name flags: 0.
- Operational-harm flags: 0.
- Max artifact similarity: 0.133.
- Mean artifact similarity: 0.071.

## H100 Validation Purpose

The H100 run will test whether predicted addresses from the frozen lightweight forecaster match independently measured response activation addresses. It is not training or updating the forecaster. It is validating whether artifact-derived text-to-coordinate relationships generalize to novel prompts and actual response-state geometry.

The H100 run can show:

- Whether text-only forecasts correlate with measured response activation coordinates on novel prompts.
- Which PCs generalize best or fail.
- Whether edge-heavy forecasts remain meaningful outside central prompt regions.
- Whether predicted high-PC3 or high-PC1/PC2 tail movement appears in actual response activations.

The H100 run cannot show:

- That the forecaster is a safety controller.
- That prompt-state activations are sufficient or unnecessary in general.
- That persona geometry is causally controlled by prompt text alone.
- That the axis interpretations are final psychological ontology.

## Planned H100 Method

Planned run:

- Manifest: `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv`.
- Model: Qwen/Qwen3-32B.
- Geometry convention: canonical Qwen layer 48.
- Generation: deterministic responses unless existing project conventions require otherwise.
- Activation extraction: response-token residual activations, mean-pooled over response tokens.
- Projection: use the existing persona PCA basis; do not refit PCA on prompt outputs.
- Primary comparison: forecasted PC1/PC2/PC3 versus observed PC1/PC2/PC3.
- Stratification: by prompt, axis, prompt family, percentile tail, shoulder/edge status, and interior-control status.

## Runtime And Early-Stop Assumptions

Planned operational guardrails:

- Run a 3-prompt smoke test before full execution.
- Use batch size 10.
- Checkpoint metrics after 10 prompts, 20 prompts, and every subsequent 10 prompts.
- Early-stop review after 20 prompts if all axes fail, coordinates are constant, projection scale is wrong, responses are empty/refusals, or runtime/cost exceeds approved bounds.

These early-stop checks are integrity checks, not hypothesis-test stopping rules.

## Success And Failure Interpretation

Proof-of-concept success: at least one PC shows meaningful positive forecast-vs-observed correlation.

Strong success: PC1 and PC3 validate, especially predicted high-PC3 movement.

Full success: all three PCs validate and no single prompt family drives the result.

Failure: text-only forecasts do not generalize to measured activations. If this happens, the next likely step is to investigate prompt-state activations, richer execution-derived training labels, or a revised forecaster trained on measured prompt-response pairs.

## Assumptions And Limitations

Assumptions required for interpretability:

- The target model, layer, pooling method, and PCA basis match the geometry used in the forecasting setup.
- The frozen forecaster remains fixed before and after H100 results.
- The percentile-edge manifest is run without prompt edits.
- Response activations are extracted from generated response tokens, not prompt tokens.
- Mean pooling over response tokens is consistent with the project convention being tested.
- PCA projection uses the existing persona PCA basis, not a refit on the H100 outputs.
- Prompt IDs, predicted coordinates, generation settings, response text, and activation shards are preserved.

Limitations:

- The forecaster was trained on released prompt artifacts, not arbitrary user conversations.
- Predicted geometry is based on artifact-derived text-to-coordinate relationships.
- H100 validation tests response-state geometry, not prompt-state activations.
- The battery is edge-heavy by design and not representative of ordinary usage.
- Safety-adjacent prompts avoid operational harm and are not a full jailbreak benchmark.
- Some edge prompts use strong coefficient-aligned natural language to reach inherited tails; validation must test whether those predicted addresses correspond to measured activations.

## Open Questions After H100

If successful:

- Run a combined/expanded validation or selective intervention test.
- Test whether high-PC3 prompts can be capped or redirected without destroying task utility.
- Consider local perturbation or capping tests around high-PC3, high-PC1, and interior-control regions.

If PC2 fails:

- Refine the PC2 interpretation.
- Add execution-derived training labels or separate prompt-state features.
- Test whether PC2 needs cluster-conditioned or longer-context predictors.

If PC3 validates:

- Consider targeted high-PC3 safety-adjacent intervention/capping tests.
- Separate prosocial perturbation from adversarial or exploitative perturbation in future manifests.

If all axes fail:

- Investigate whether prompt-state activations are required.
- Check projection convention, pooling, response truncation, refusal behavior, and scale calibration.
- Treat text-only forecasting as artifact-level prediction that did not generalize to response activation geometry.
