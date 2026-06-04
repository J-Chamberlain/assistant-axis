# Prior Adaptive Recovery Decision Report

## Decision

The trickster adaptive extraction run is recoverable and reusable for local
analysis under the corrected D01 boundary because it saved 1200 hook-derived
activation vectors and full response text. The editor/procedural-adjacent runs
are also locally reprojectable, but their role-expression yield remains weak;
their failure is better interpreted as an elicitation/judge-yield problem than
as a D01 boundary problem.

## Evidence

| run_id | role | records | responses_present | activation_vectors_present | score_ge2 | score_eq3 | recoverability_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trickster_phase1_1200 | trickster | 1200 | 1200 | 1200 | 64 | 33 | full_reproject_possible |
| editor_phase1_128 | editor | 128 | 128 | 128 | 10 | 3 | full_reproject_possible |
| editor_matched64_1024 | editor | 64 | 64 | 64 | 5 | 1 | full_reproject_possible |


## Corrected Cloud Summary

| run_id | subset | n | mean_pc1 | mean_pc2 | mean_pc3 | sd_pc1 | sd_pc2 | sd_pc3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| editor_matched64_1024 | all | 64 | 24.954721 | 8.081047 | -5.964654 | 18.206528 | 17.498712 | 14.414791 |
| editor_matched64_1024 | score_eq3 | 1 | 36.829499 | -7.283571 | 6.605426 | 0.000000 | 0.000000 | 0.000000 |
| editor_matched64_1024 | score_ge2 | 5 | 32.155854 | 13.569825 | -8.426029 | 5.233921 | 16.193849 | 13.409728 |
| editor_phase1_128 | all | 128 | 25.502039 | 8.010257 | -4.857668 | 21.187814 | 17.680357 | 15.206740 |
| editor_phase1_128 | score_eq3 | 3 | 32.987572 | 1.534582 | -2.683001 | 10.840785 | 24.757115 | 9.623802 |
| editor_phase1_128 | score_ge2 | 10 | 28.346119 | 12.334288 | -6.579218 | 12.416772 | 20.579213 | 10.068737 |
| trickster_phase1_1200 | all | 1200 | -41.589259 | 31.237387 | 17.642344 | 12.134168 | 14.701303 | 10.196260 |
| trickster_phase1_1200 | score_eq3 | 33 | -40.530161 | 30.183983 | 18.360512 | 12.107438 | 10.389575 | 8.740781 |
| trickster_phase1_1200 | score_ge2 | 64 | -37.598494 | 30.517688 | 16.598729 | 13.116568 | 10.452166 | 9.086126 |


## Recommended Next Action

Do not rerun GPU just to recover these prior adaptive runs. Instead:

1. If evaluator sensitivity matters for Paper 1.5, run GPT-4.1 rejudging on the prepared JSONL.
2. Use the existing hook-derived vectors for local PCA/cloud comparisons.
3. Reserve GPU for new no-label or activation-cloud experiments where raw activations are not already saved.
