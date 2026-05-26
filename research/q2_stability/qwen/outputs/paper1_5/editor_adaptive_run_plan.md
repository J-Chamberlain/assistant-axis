# Editor Adaptive Extraction Run Plan

Date: 2026-05-26
Status: prepared, not launched

## Purpose

The editor run is the second-persona generalization test for the adaptive extraction workflow validated on trickster. Trickster is a high-signal, anti-assistant persona. Editor is quieter, assistant-adjacent, and closer to the careful-evaluator basin, so it tests whether adaptive extraction works outside an expressive, easily judged role.

## Fixed Run Parameters

- Persona: editor
- Generation model: Qwen/Qwen3-32B
- Extraction layer: 48
- Role instruction file: `data/roles/instructions/editor.json`
- Lu reference tensor: `downloads/hf_vectors/qwen-3-32b/role_vectors/editor.pt`
- Pod API usage: no OpenAI or external judge calls on pod
- Generation mode: deterministic inference
- Thinking mode: disabled with `enable_thinking=False` where supported
- Measurement pass: `use_cache=False`
- Activation persistence: one `.pt` shard per rollout, gitignored
- Response persistence: full `response_text` in JSONL records
- Execution mode: detached pod execution only, via `nohup`, `tmux`, or equivalent

## Chunking Strategy

The editor run should not begin with a full fixed 1200-rollout extraction. The initial pod chunk is 128 rollouts, preserving the same Lu-style input design of five system prompts and 240 extraction questions but stopping early for local scoring and geometric validation.

After local preservation, integrity checking, and Codex scoring, additional chunks are launched only if the qualifying yield or convergence checks fail. This preserves the validated adaptive workflow while avoiding unnecessary pod time.

## Initial Targets

- Initial rollout target: 128 records
- Local judge after preservation: Codex GPT-5.5 Standard
- Preferred qualifying threshold:
  - at least 64 score>=2 responses
  - at least 16 score==3 responses
  - adaptive stopping passes at n>=16
- Escalation trigger:
  - fewer than 64 score>=2 responses
  - fewer than 16 score==3 responses
  - adaptive stopping fails for both score>=2 and score==3 subsets
  - vector validation against Lu editor reference is materially weaker than expected

## Preservation and Integrity

The pod writes resumable JSONL response records and activation shards during inference. Before any termination decision, outputs must be copied locally and validated with an integrity check covering record count, unique `(sp_idx, q_idx)` pairs, activation shard existence, tensor shape `[5120]`, non-empty response text, no literal think tags, and no `think_artifact=True` records.

Activation shards must not be committed. JSONL records, manifests, integrity summaries, scoring summaries, validation summaries, and methodology reports may be committed when they are small enough and do not contain secrets.

## Scoring and Validation

Scoring happens locally after preservation, not on the pod. Codex GPT-5.5 Standard scores editor role expression as a pragmatic judge, with the judge substitution recorded explicitly. The validation step compares score-conditioned candidate vectors against the Lu editor reference tensor and reports score>=2, score==3, non-truncated score>=2, and non-truncated score==3 candidate vectors.

The run succeeds as a second-persona adaptive extraction test if a score-conditioned editor vector reaches stable convergence at or below the conservative 64-qualifying-response target and matches the Lu editor reference strongly enough to justify continuing the adaptive workflow for additional personas.

## Pod Lifecycle Requirements

The run must follow `research/workflow/pod_lifecycle_protocol.md`. Pod termination requires preserved local outputs, integrity results, committed safe artifacts, and explicit user approval. Preferred termination path is RunPod API or `runpodctl`; browser/dashboard termination is fallback only.
