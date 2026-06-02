# Paper 1.5 Notebook Revision Report

Generated UTC: 2026-06-02T14:21:27+00:00
Startup status: STARTUP VERIFIED
Branch: `master`

## Paths

- Notebook source: `research/notebooks/paper15_core_analysis_walkthrough.ipynb`
- Executed notebook: `research/notebooks/paper15_core_analysis_walkthrough.executed.ipynb`
- Standard HTML: `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough.html`
- Shareable collapsed-code HTML: `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough_report_collapsed_code.html`

## Sections Revised

- N01 Public Geometry and Artifact Reconstruction
- N02 Cross-Model Scope and Caveats
- N06 Trait/Persona Relationship
- N07 Prediction-Improvement Sequence
- N10 Summary of Claims, Confidence, and Next Tests

## Markdown Clarifications Added

- Clarified that `source_model: Qwen/Qwen3-32B` is the geometry source model, while `model_used: GPT-5.5` is project/helper metadata for the visualization artifact.
- Clarified that the cross-model PC table is a local coordinate/best-match diagnostic, not identical to Lu et al.'s published role-composition comparison; PCA axes may rotate, flip sign, or swap index inside a shared low-dimensional subspace.
- Clarified that high-dimensional trait cosine profiles can reconstruct persona coordinates without proving trait causality or psychological ontology.
- Clarified that the public role-vector recipe is 5 positive instructions x 240 shared questions = 1,200 candidate rollouts per role, while `64 stored vectors` refers to local tensor/shard representation rather than rollout count.
- Renamed the N07 display subsection from `Non-verified rows` to `Optional or not-yet-core rows`.
- Updated the N10 summary caveats for cross-model PCA alignment, trait-only PCA, and optional forecasting status.

## Execution Status

- Runtime: 2.315 seconds
- Code cells executed: 12 / 12
- Errors: 0
- Warnings in final execution log: 0
- Guarded/skipped cells detected: none
- Missing required inputs: none

## Shareable HTML Verification

- Shareable HTML exists: True (417439 bytes)
- Collapsed code toggles: 12
- Computed-output check passed: True
- Final claims section present: True
- H100-only sections added: False
- Visualization files modified: false
- H100 headings detected: none

## PDF Status

- PDF regenerated: False
- PDF status: skipped: nbconvert webpdf requires Playwright, which is outside the authorized package list for this task
- PDF export log: `research/outputs/paper15_notebook_core/notebook_pdf_export_log.txt`

## Boundary Confirmation

The notebook remains a pre-H100 executable appendix. H100 validation outputs, prompt-battery outputs, extraction-boundary diagnostics, RunPod logs, and forecast-vs-observed arrow viewers remain excluded.

## User Review Items

- Review `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough_report_collapsed_code.html` as the reader-first artifact.
- PDF was not regenerated because the local `webpdf` exporter requires Playwright, which was not in the authorized package list.
