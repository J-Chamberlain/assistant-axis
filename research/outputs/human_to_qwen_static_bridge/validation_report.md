# Human-to-Qwen Static Bridge V1 — Validation Status

Status: **INCOMPLETE — PRIMARY NULL FAMILY REFS PENDING**

The frozen CPU-only validation was run after freeze commit `77318ff22f0e4a30a0186d7fa32241d770a1ae66`. It used the verified local SAPA V5 respondent file and saved Qwen vectors only; no new inference, activation extraction, GPU, RunPod, HRS, LISS, HILDA, MIDUS, or SOEP data were used.

## Observed

At the preregistered six-anchor threshold, 1,935 respondents yielded 17,209 respondent-target predictions. The preliminary equal-weight Fisher-z macro-average Pearson correlation is 0.0996. The respondent-cluster bootstrap used 2,000 draws and produced a 95% interval of [0.0796, 0.1198]. Per-trait sample sizes range from 1,069 to 1,616.

## Interpretation

These preliminary held-out correlations are positive but small and are not a completed claim-gate result. The target-shuffle null is complete (1,000 draws; empirical p=0.0010), but that alone is insufficient for the preregistered bridge decision.

## Hypothesis

If the bridge survives all three preregistered null families, sparse observed human profiles may carry limited transferable ordering information into Qwen PC geography. This remains untested until the bridge-label and model-joint-structure null families are run.

## Unknown

The bridge-label permutation and model-joint-structure-destruction nulls were not run in this pass because they require separate model refits per draw and exceeded the reasonable CPU budget of the current implementation. They are explicitly marked `NOT_RUN_CPU_BUDGET` in `null_summary.csv`; no shortcut was substituted. Therefore no `SUPPORTED`, `MIXED`, or `WEAK / ABSENT` final classification is asserted here, and no descriptive human projection or viewer has been produced.

Respondent-level predictions remain local only at `data_external/human_validation/sapa/derived/human_to_qwen_static_bridge_v1/heldout_predictions.parquet` and are not tracked by Git.
