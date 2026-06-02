# Paper 1.5 Notebook Execution Verification Report

Generated UTC: 2026-06-02T12:41:09+00:00
Startup status: STARTUP VERIFIED
Branch: `master`

## Environment

- Virtualenv path: `.venv-notebook`
- Python executable: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/.venv-notebook/bin/python`
- Kernel: `paper15-notebook`
- Kernelspec path: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/.venv-notebook/share/jupyter/kernels/paper15-notebook`
- Packages installed/requested: jupyter, nbformat, nbclient, ipykernel, pandas, numpy, matplotlib, plotly

## Notebook Execution

- Notebook path: `research/notebooks/paper15_core_analysis_walkthrough.ipynb`
- Executed notebook path: `research/notebooks/paper15_core_analysis_walkthrough.executed.ipynb`
- HTML export path: `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough.html`
- Execution runtime: 1.933 seconds
- Code cells executed: 12 / 12
- Errors: 0
- Warnings in final execution log: 0
- Guarded/skipped markers detected in notebook output: none

## Artifact Verification

- Executed notebook written: True (69244 bytes)
- HTML export written: True (411933 bytes)
- HTML title: `paper15_core_analysis_walkthrough.executed`
- HTML first H1: `Assistant Axis Reanalysis: Public Geometry, Axis Interpretation, and Forecasting Baselines¶`
- Execution log: `research/outputs/paper15_notebook_core/notebook_execution_log.txt`
- Environment freeze: `research/outputs/paper15_notebook_core/notebook_environment_freeze.txt`
- Environment summary: `research/outputs/paper15_notebook_core/notebook_environment_summary.json`

## Code Fixes Made

- Added deterministic notebook cell IDs in `research/outputs/paper15_notebook_core/run_build_paper15_notebook.py` and regenerated the source notebook. This was a mechanical metadata fix to remove nbformat's `MissingIDFieldWarning`; no claims, analyses, or substantive notebook content were changed.

## Missing Dependencies or Inputs

- Required notebook input files: none missing.
- Runtime package dependencies: installed into `.venv-notebook`.

## User Review Items

- Open `research/notebooks/paper15_core_analysis_walkthrough.executed.ipynb` in VS Code/Jupyter to review narrative flow, table readability, and generated figures.
- Open `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough.html` for a browser-style rendered view.
- The notebook remains pre-H100: H100 validation, prompt batteries, extraction-boundary diagnostics, RunPod logs, and visualization edits are intentionally excluded.

## Verdict

Headless notebook execution and HTML export succeeded with zero errors and zero final execution-log warnings.
