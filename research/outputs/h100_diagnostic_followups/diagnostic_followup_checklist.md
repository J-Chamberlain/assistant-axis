# H100 Diagnostic Follow-Up Checklist

- Generated UTC: 2026-05-31T13:10:27.689619+00:00
- Model used for this diagnostic pass: GPT-5.5
- Rule: items remain open until resolved with direct evidence.
- Methodological dependency rule: D01-D09 should not be closed in isolation when the relevant T-track remains open. T01-T04 below are the governing dependencies for interpreting anomaly items.

| id | title | priority | status | conclusion | next action |
|---|---|---|---|---|---|
| D01 | Verify activation measurement methodology | critical | open | Public-source audit found a likely activation-boundary mismatch: official/prior extraction hooks `model.model.layers[48]` and captures the decoder layer-48 module output, while H100 used `outputs.hidden_states[48]`, which Transformers/Qwen3 semantics map to the input of layer 48 / output after layer 47. | Run the minimal one-prompt hook-vs-hidden-states test to confirm whether the layer-48 hook matches `hidden_states[49]`, then rerun or reinterpret the H100 validation with the corrected extraction boundary. |
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

## 2026-05-31 Public-source extraction equivalence update

- D01 is now `open` with a likely mismatch, not merely unresolved. The public-source audit found that official Assistant Axis extraction documents zero-indexed post-MLP residual stream layers and captures target layer outputs with forward hooks, while the H100 runner used `out.hidden_states[48]`.
- Hugging Face ModelOutput documentation and Transformers Qwen3 4.51.0 source semantics imply `hidden_states[48]` is the state before decoder layer 48 / after layer 47, while the `model.model.layers[48]` hook captures the decoder layer 48 output, corresponding to `hidden_states[49]` for intermediate layers.
- Evidence files: `research/outputs/public_source_extraction_equivalence/public_source_extraction_equivalence_report.md`, `research/outputs/public_source_extraction_equivalence/public_source_evidence_table.csv`, and `research/outputs/public_source_extraction_equivalence/minimal_gpu_test_if_needed.md`.

## Higher-level methodological dependencies before resolving anomaly checklist

The D01-D09 checklist remains useful, but several items depend on broader methodological questions. The current interpretation rule is: do not treat an itemized anomaly as final behavioral evidence while its governing T-track remains open.

Cross-reference outputs:

- `research/outputs/public_source_extraction_equivalence/`
- `research/outputs/extraction_equivalence_audit/`
- `research/outputs/h100_percentile_edge_validation/`
- `research/outputs/h100_percentile_edge_validation_error_analysis/`
- `research/outputs/h100_diagnostic_followups/`
- `research/outputs/role_rollout_artifact_audit/`
- `research/outputs/training_forecast_error_geometry/`

### T01. Extraction equivalence / activation boundary

- Status: open
- Priority: critical
- Description: Determine whether the H100 activation extraction site matches the inherited Assistant Axis / Qwen persona-vector extraction site. D01 remains open because public-source audit found a likely boundary mismatch: official/prior extraction hooks `model.model.layers[48]`, while the H100 runner used `outputs.hidden_states[48]`. Public Transformers/Qwen3 semantics suggest the hook may correspond to `hidden_states[49]`. Until this is verified, PC2 shifts, cone outliers, and PC3 collapse should not be treated as settled behavioral findings.
- Next action: Run only the minimal one-prompt hook-vs-hidden-states confirmation test if public-source evidence cannot close the issue. No full H100 rerun before this.

### T02. Forecaster improvement

- Status: open
- Priority: high
- Description: Improve the lightweight text-to-geometry forecaster. The current model was trained at the role-artifact/concept-package level, which is compressed relative to the original Assistant Axis rollout process. The next improvement is instance-level role-prompt training: one reconstructed instruction-question input per row, target equals the corresponding role centroid coordinate. Main validation should hold out entire roles. This can be done on the Mac Mini.
- Dependencies: Audit whether the 1,200 instruction-question input combinations per role can be reconstructed; determine whether generated responses, judge scores, or retained-response masks are public. The current role-rollout artifact audit finds the inputs reconstructable but original responses, judge scores, and retained masks not publicly available.
- Next action: Complete the role rollout artifact audit and, if inputs are reconstructable, train an instance-level prompt-to-centroid forecaster.

### T03. Prompt-battery construction

- Status: open
- Priority: high
- Description: Generate a better validation prompt battery only after improving or at least characterizing the forecaster. Earlier prompt batteries satisfied formal criteria but produced suspicious structure, incomplete coverage, and possible forecaster-exploitation/origin-plane artifacts. A revised battery should use the improved instance-level forecaster and inherited-percentile targets, with transparent failure reporting.
- Dependencies: T02 forecaster improvement or an explicit decision to proceed with the current forecaster; clear percentile-based edge/interior criteria.
- Next action: After T02, rebuild or recalibrate the prompt battery and report coverage against inherited 20/80 tails, 35/65 shoulders, and interior controls.

### T04. Response-state uncertainty / centroid versus single-sample mismatch

- Status: open
- Priority: high
- Description: Quantify the spread of actual response activations around a target region. The inherited Assistant Axis role vectors are centroids over many judged-successful responses, while the H100 validation used one deterministic response per prompt. Even with a perfect forecaster, a single response may not land near the centroid. We need to estimate the distribution of actual activations produced by repeated generations for selected prompts or roles.
- Dependencies: T01 extraction equivalence must be closed first; T02/T03 should inform which prompts or regions to sample.
- Next action: Design a small multi-sample GPU study: choose a few representative targets, generate many responses per prompt, optionally judge/filter role expression, and measure activation-coordinate spread.

### Relationship to D01-D09

- D01 is covered directly by T01.
- D02 cone-violation outliers should not be resolved until T01 is closed.
- D03 and D08 origin-plane or forecaster-exploitation concerns are partly covered by T02 and T03.
- D04 and D05 PC2 upward shift may reflect extraction mismatch, forecaster compression, prompt-battery bias, or single-sample response uncertainty; defer final interpretation until T01-T04 are considered.
- D06 PC3-high collapse may reflect response neutralization, wrong activation boundary, forecaster overprediction, or single-sample/centroid mismatch; defer final behavioral interpretation until T01 and T04 are addressed.
- D09 calibration should be considered after T01 and before any full rerun, but calibration alone should not be treated as resolving T02-T04.

### Recommended next action order

1. Close T01 with the minimal hook-vs-hidden-states confirmation test.
2. Advance T02 by training or evaluating an instance-level prompt-to-centroid forecaster from reconstructed instruction-question inputs.
3. Use T02 results to rebuild or recalibrate the prompt battery under T03.
4. Design the T04 small multi-sample GPU study to estimate response-state spread around selected targets.
5. Only then close or upgrade D02-D08 from anomaly notes into behavioral interpretations.
