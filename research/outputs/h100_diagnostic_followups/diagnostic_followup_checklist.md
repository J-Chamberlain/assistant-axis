# H100 Diagnostic Follow-Up Checklist

- Generated UTC: 2026-05-31T13:10:27.689619+00:00
- Model used for this diagnostic pass: GPT-5.5
- Rule: items remain open until resolved with direct evidence.

| id | title | priority | status | conclusion | next action |
|---|---|---|---|---|---|
| D01 | Verify activation measurement methodology | critical | in_progress | Extraction audit verified model identity, layer target, response-token pooling, PCA centering/sign/projection, and prior hook-based trickster replication; activation-site equivalence remains unresolved because prior/source extraction uses forward hooks while H100 reads `output_hidden_states[48]`. | Run the minimal Qwen hook-vs-hidden-states equivalence test, or locate source-level proof that `output_hidden_states[48]` matches the layer-48 hook output. |
| D02 | Investigate observed high-PC1/high-PC2 cone-violation outliers | critical | open | Cone-violation candidates identified; several are generic/procedural observed responses in high PC1/PC2 regions. | Inspect whether these are genuine admissible states or projection/pooling artifacts. |
| D03 | Inspect forecasted extreme-PC1 / near-zero-PC3 prompts | high | open | Extreme-PC1/near-zero-PC3 cases exist and often show coefficient-aligned lexical construction. | Decide whether to downweight or redesign these prompts in the next battery. |
| D04 | Inspect lowest predicted-PC2 prompts near PC1 approx 0 | high | open | Low-PC2 near-zero-PC1 cases generally drift upward on PC2 after generation. | Compare prompt-intended abstraction against actual response style with second rater or calibrated model. |
| D05 | Analyze prompt families driving largest positive PC2 deltas | high | open | PC2 upward shift is family/group dependent; neutral and cluster-region prompts show large positive deltas. | Use family/cell diagnostics in calibration. |
| D06 | Inspect largest downward PC3 errors among forecasted PC3-high prompts | high | open | Forecasted PC3-high prompts frequently become abstract/generic/stabilizing and fail observed high-PC3 retention. | Test more direct non-operational perturbative prompts or response-style controls. |
| D07 | Inspect largest 3D-error prompts overall | medium | open | Largest 3D errors are dominated mostly by PC2 upward drift and PC3 collapse. | Use these as calibration stress cases. |
| D08 | Audit prompt-generation loop for forecaster exploitation or origin bias | high | open | Generation loop and final battery show repeated scaffolds and some forecaster-facing lexical patterns; evidence suggests possible design bias but not enough to discard the battery. | Create a human-naturalness review or regenerate a no-feedback holdout edge subset. |
| D09 | Distinguish calibration failure from true directional failure | medium | in_progress | Axis-wise calibration diagnostics were scaffolded and run; held-out calibration should be treated as preliminary. | Run proper train/test or nested calibration on a larger validation set. |

## 2026-05-31 Training forecast error geometry update

- D03 forecasted extreme-PC1 / near-zero-PC3 prompts: compare H100 cases against `research/outputs/training_forecast_error_geometry/training_forecast_error_3d_arrows.html` to determine whether near-zero PC3 forecasts are already present in native role-artifact forecaster predictions.
- D08 prompt-generation loop forecaster exploitation or origin bias: use `training_forecast_per_example_errors.csv` and the 2D arrow views to separate native forecaster shrinkage from prompt-generation loop artifacts.
- D09 calibration failure versus directional failure: native target-to-forecast signed bias and H100 observed-minus-forecast signed bias are now directly comparable in `training_forecast_error_summary.json`.

## 2026-05-31 Extraction equivalence audit update

- D01 remains `in_progress`, not resolved. The audit found no projection discrepancy and verified that the prior successful trickster replication used Qwen/Qwen3-32B layer 48, response-token mean pooling, thinking disabled, and a hook-based extraction path that matched the downloaded trickster vector at cosine 0.957557.
- The remaining gap is activation-site equivalence: local source and prior adaptive extraction use forward hooks on `model.model.layers[48]`, while the H100 validation used `out.hidden_states[48]`. PCA reproduction max error 1.207e-06 proves projection-basis correctness, not extraction-site equivalence.
- Evidence files: `research/outputs/extraction_equivalence_audit/extraction_equivalence_audit_report.md`, `research/outputs/extraction_equivalence_audit/extraction_equivalence_table.csv`, and `research/outputs/extraction_equivalence_audit/proposed_minimal_empirical_test.md`.
