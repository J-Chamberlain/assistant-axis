# Methodological Dependency Tracks for H100 Diagnostics

- Date: 2026-05-31
- Model used: GPT-5.5
- Purpose: organize H100 anomaly interpretation under higher-level methodological dependencies before itemized D01-D09 checklist items are treated as final behavioral evidence.

The D01-D09 checklist remains useful, but several items depend on broader methodological questions. The current interpretation rule is: do not treat an itemized anomaly as final behavioral evidence while its governing T-track remains open.

Cross-reference outputs:

- `research/outputs/public_source_extraction_equivalence/`
- `research/outputs/extraction_equivalence_audit/`
- `research/outputs/h100_percentile_edge_validation/`
- `research/outputs/h100_percentile_edge_validation_error_analysis/`
- `research/outputs/h100_diagnostic_followups/`
- `research/outputs/role_rollout_artifact_audit/`
- `research/outputs/training_forecast_error_geometry/`

## T01. Extraction equivalence / activation boundary

- Status: open
- Priority: critical
- Description: Determine whether the H100 activation extraction site matches the inherited Assistant Axis / Qwen persona-vector extraction site. D01 remains open because public-source audit found a likely boundary mismatch: official/prior extraction hooks `model.model.layers[48]`, while the H100 runner used `outputs.hidden_states[48]`. Public Transformers/Qwen3 semantics suggest the hook may correspond to `hidden_states[49]`. Until this is verified, PC2 shifts, cone outliers, and PC3 collapse should not be treated as settled behavioral findings.
- Next action: Run only the minimal one-prompt hook-vs-hidden-states confirmation test if public-source evidence cannot close the issue. No full H100 rerun before this.

## T02. Forecaster improvement

- Status: open
- Priority: high
- Description: Improve the lightweight text-to-geometry forecaster. The current model was trained at the role-artifact/concept-package level, which is compressed relative to the original Assistant Axis rollout process. The next improvement is instance-level role-prompt training: one reconstructed instruction-question input per row, target equals the corresponding role centroid coordinate. Main validation should hold out entire roles. This can be done on the Mac Mini.
- Dependencies: Audit whether the 1,200 instruction-question input combinations per role can be reconstructed; determine whether generated responses, judge scores, or retained-response masks are public. The current role-rollout artifact audit finds the inputs reconstructable but original responses, judge scores, and retained masks not publicly available.
- Next action: Complete the role rollout artifact audit and, if inputs are reconstructable, train an instance-level prompt-to-centroid forecaster.

## T03. Prompt-battery construction

- Status: open
- Priority: high
- Description: Generate a better validation prompt battery only after improving or at least characterizing the forecaster. Earlier prompt batteries satisfied formal criteria but produced suspicious structure, incomplete coverage, and possible forecaster-exploitation/origin-plane artifacts. A revised battery should use the improved instance-level forecaster and inherited-percentile targets, with transparent failure reporting.
- Dependencies: T02 forecaster improvement or an explicit decision to proceed with the current forecaster; clear percentile-based edge/interior criteria.
- Next action: After T02, rebuild or recalibrate the prompt battery and report coverage against inherited 20/80 tails, 35/65 shoulders, and interior controls.

## T04. Response-state uncertainty / centroid versus single-sample mismatch

- Status: open
- Priority: high
- Description: Quantify the spread of actual response activations around a target region. The inherited Assistant Axis role vectors are centroids over many judged-successful responses, while the H100 validation used one deterministic response per prompt. Even with a perfect forecaster, a single response may not land near the centroid. We need to estimate the distribution of actual activations produced by repeated generations for selected prompts or roles.
- Dependencies: T01 extraction equivalence must be closed first; T02/T03 should inform which prompts or regions to sample.
- Next action: Design a small multi-sample GPU study: choose a few representative targets, generate many responses per prompt, optionally judge/filter role expression, and measure activation-coordinate spread.

## Relationship to D01-D09

- D01 is covered directly by T01.
- D02 cone-violation outliers should not be resolved until T01 is closed.
- D03 and D08 origin-plane or forecaster-exploitation concerns are partly covered by T02 and T03.
- D04 and D05 PC2 upward shift may reflect extraction mismatch, forecaster compression, prompt-battery bias, or single-sample response uncertainty; defer final interpretation until T01-T04 are considered.
- D06 PC3-high collapse may reflect response neutralization, wrong activation boundary, forecaster overprediction, or single-sample/centroid mismatch; defer final behavioral interpretation until T01 and T04 are addressed.
- D09 calibration should be considered after T01 and before any full rerun, but calibration alone should not be treated as resolving T02-T04.

## Recommended next action order

1. Close T01 with the minimal hook-vs-hidden-states confirmation test.
2. Advance T02 by training or evaluating an instance-level prompt-to-centroid forecaster from reconstructed instruction-question inputs.
3. Use T02 results to rebuild or recalibrate the prompt battery under T03.
4. Design the T04 small multi-sample GPU study to estimate response-state spread around selected targets.
5. Only then close or upgrade D02-D08 from anomaly notes into behavioral interpretations.
