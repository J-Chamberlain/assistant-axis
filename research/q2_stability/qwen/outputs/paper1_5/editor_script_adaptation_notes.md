# Editor Script Adaptation Notes

Date: 2026-05-26
Status: prepared for future pod-run script generation

## Input Verification

`data/roles/instructions/editor.json` exists and has the expected Lu-style structure: top-level keys `instruction`, `questions`, and `eval_prompt`; five `instruction` entries; each positive instruction stored under `pos`.

`downloads/hf_vectors/qwen-3-32b/role_vectors/editor.pt` exists and loads as a tensor with shape `(64, 5120)` and dtype `torch.bfloat16` under the repo virtual environment.

## Changes From Trickster Scripts

The future editor scripts should change the following fields from the trickster versions:

- Persona variable: `trickster` to `editor`
- Output directory labels: keep `research/q2_stability/qwen/outputs/paper1_5/`, but use editor-specific filenames
- Activation directory: `activations_trickster` to `activations_editor`
- Phase 1 JSONL: `trickster_phase1.jsonl` to `editor_phase1.jsonl`
- Manifest: `trickster_phase1_manifest.json` to `editor_phase1_manifest.json`
- Integrity files: use editor-specific names, for example `editor_phase1_integrity.json`
- Codex score JSONL: `trickster_phase2_scores_codex_gpt55.jsonl` to `editor_phase2_scores_codex_gpt55.jsonl`
- Codex score summary: `trickster_phase2_scores_codex_gpt55_summary.json` to `editor_phase2_scores_codex_gpt55_summary.json`
- Codex score report: `trickster_phase2_scores_codex_gpt55_report.md` to `editor_phase2_scores_codex_gpt55_report.md`
- Vector validation outputs: `trickster_vector_validation_codex_gpt55.*` to `editor_vector_validation_codex_gpt55.*`
- Sample sufficiency outputs: `trickster_sample_sufficiency_codex_gpt55.*` to `editor_sample_sufficiency_codex_gpt55.*`
- Reference tensor lookup: `trickster.pt` to `editor.pt`
- Report labels and rubric target: trickster role expression to editor role expression

## What Must Not Change

The following methodology-critical settings must remain fixed:

- Model: Qwen/Qwen3-32B
- Extraction layer: 48
- Hidden dimension: 5120
- No judge or OpenAI API calls on pod
- Full `response_text` saved in JSONL
- Activation shards saved separately from JSONL
- Measurement forward pass uses `use_cache=False`
- Generation remains deterministic for the first editor test
- Thinking mode is disabled where the tokenizer or generation interface supports it
- Think artifacts are rejected or flagged explicitly
- Local integrity validation runs before scoring and before termination
- RunPod lifecycle follows `research/workflow/pod_lifecycle_protocol.md`

## Why Script Copies Were Not Created In This Prep Step

The current trickster scripts are tied to a completed 1200-record corpus. The editor run plan deliberately starts with a 128-rollout chunk and escalates only if yield or convergence fails. Creating simple search-and-replace copies would preserve assumptions that are wrong for the editor run, especially the scoring harness expectation that all 1200 records exist.

At pod-run time, generate editor-specific scripts from the trickster versions with explicit support for `--max-rollouts 128`, resumable chunk selection, editor-specific output names, and partial-corpus scoring and validation. This keeps the future scripts aligned with the adaptive protocol instead of carrying forward the old exhaustive-run defaults.
