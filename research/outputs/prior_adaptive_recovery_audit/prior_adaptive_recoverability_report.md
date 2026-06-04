# Prior Adaptive Recoverability Report

Startup status: **STARTUP VERIFIED**.

## Recovery Classification

| run_id | role | records | activation_vectors_present | sample_tensor_shape | score_ge2 | score_eq3 | recoverability_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trickster_phase1_1200 | trickster | 1200 | 1200 | [5120] | 64 | 33 | full_reproject_possible |
| editor_phase1_128 | editor | 128 | 128 | [5120] | 10 | 3 | full_reproject_possible |
| editor_matched64_1024 | editor | 64 | 64 | [5120] | 5 | 1 | full_reproject_possible |


## D01 Boundary Interpretation

The inspected adaptive Phase 1 scripts capture activations using a forward hook
on `model.model.layers[48]` during a full generated-sequence forward pass with
`use_cache=False`, then mean-pool over response tokens only. The later A100
boundary test resolved D01 by showing this hook corresponds to
`outputs.hidden_states[49]`, not `outputs.hidden_states[48]`.

Therefore, these hook-derived activation shards do **not** require GPU
regeneration to correct a hidden-state index error. They can be locally reused
and reprojected into the canonical Qwen PCA basis. What cannot be recovered
locally is an alternative hidden-state-boundary extraction for runs that did not
save hook vectors.

## Status Summary

| recoverability_status | count |
| --- | --- |
| full_reproject_possible | 3 |


## Family Summary

| family | count |
| --- | --- |
| procedural_professional_family | 2 |
| trickster_family | 1 |

