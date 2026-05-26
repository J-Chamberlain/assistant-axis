# Editor Adaptive Extraction Pod Closeout

Date: 2026-05-26

## Scope

This closeout covers the Qwen/Qwen3-32B editor adaptive extraction pod run, including the 128-record 512-token Phase 1 chunk, the matched 64-record 1024-token sensitivity follow-up, local Codex GPT-5.5 scoring, and token-cap comparison.

## Preserved Outputs

The 512-token editor chunk is preserved locally at `research/q2_stability/qwen/outputs/paper1_5/editor/` with JSONL records, manifest, integrity JSON, integrity Markdown, scoring JSONL, scoring summary, and scoring report. The matched 1024-token sensitivity run is preserved locally at `research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/` with JSONL records, manifest, integrity outputs, scoring outputs, and token-cap comparison outputs.

Activation shards are present locally for both runs and remain gitignored:

- `research/q2_stability/qwen/outputs/paper1_5/editor/activations_editor/`
- `research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/activations_editor_1024/`

## Empirical Result

The 512-token editor chunk produced 10 score>=2 responses and 3 score==3 responses out of 128 scored records, below the validation threshold of 64 score>=2 and 16 score==3 responses. The matched 1024-token follow-up reduced truncation from 50/64 to 5/64 for the same first 64 pairs, but the score>=2 and score==3 counts did not improve. The matched comparison therefore suggests that token cap alone does not explain the low editor-role expression.

Vector validation and score-conditioned sample sufficiency were not run because the preregistered score thresholds were not met.

## Pod Termination

RunPod pod `5b6hz02m9idrc3`, named `paper1-5-editor-128`, was confirmed idle over SSH before termination. No rollout process was active, both editor logs showed completed runs, and GPU usage was 1 MiB at 0 percent utilization.

The pod was stopped with `runpodctl pod stop 5b6hz02m9idrc3`, which moved desired status to `EXITED`. It was then deleted with `runpodctl pod delete 5b6hz02m9idrc3`. Final confirmation showed `runpodctl pod list` returning no running pods and `runpodctl pod get 5b6hz02m9idrc3` returning 404 `pod not found`.

## Next Step

The next empirical step is a revised editor anchoring design rather than more rollout generation under the same setup. The current result suggests that assistant-adjacent personas may collapse back toward generic assistant behavior under this Lu-style extraction setup, and editor likely needs a stronger or different anchoring methodology before additional pod time is spent.
