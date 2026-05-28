# Run Registry Specification

Purpose: keep every long-running pod or local extraction run visible outside chat context. The run registry is the canonical operational index for active, paused, completed, and failed runs.

Recommended location: `research/workflow/run_registry.jsonl`.

Each line is one JSON object. Update by appending a new event-style row when state changes, or by maintaining a single latest-state JSON object per run if a script owns the file. For manual operations, append-only JSONL is preferred.

## Required Fields

`run_id`: Stable human-readable identifier. Example: `paper1_5_qwen_trickster_phase1_2026-05-26`.

`pod_id`: RunPod pod identifier when available. Use `null` for local-only runs.

`ssh_endpoint`: SSH host and port. Example: `213.173.102.6:22707`. Use `null` when not applicable.

`gpu_type`: GPU class and count. Example: `A100 SXM 80GB x1`.

`start_time`: ISO 8601 timestamp for launch or local run start.

`latest_heartbeat`: ISO 8601 timestamp of the most recent observed heartbeat.

`latest_rollout`: Latest completed rollout or work unit. Include both count and denominator when known.

`current_status`: One of the canonical run states below.

`local_snapshot_status`: Whether current outputs have been copied locally, with path and count summary.

`integrity_status`: Latest integrity result. Example: `passed 1200 records, 1200 shards, shape [5120]`.

`preservation_status`: Whether source script, logs, manifest, JSONL, activation shards, and decision notes are preserved.

`termination_status`: `not_started`, `not_applicable`, `requested`, `confirmed`, `failed`, or `unknown`.

`expected_completion`: ETA or planned completion condition.

`scoring_status`: Not started, in progress, blocked, complete, or not applicable, with score-file path when present.

`validation_status`: Not started, blocked, passed, failed, or not applicable, with output path when present.

`notes`: Short free-text notes for risks, caveats, and next action.

`model_provenance`: Required for any run that generates, scores, analyzes, or validates research artifacts. Follow `research/workflow/model_provenance_schema.md` and distinguish `generation_model`, `evaluation_model`, `analysis_model`, and `script_author_model`.

## Canonical Run States

`planned`: Run is designed but not launched.

`launched`: Pod or local process started, but first heartbeat is not yet confirmed.

`running`: Heartbeat confirms active progress.

`preserved`: Outputs have been copied or checkpointed to local durable storage.

`integrity_checked`: Local integrity script or equivalent audit has passed or failed and the result is recorded.

`scored`: Role-expression or other downstream scoring has produced the required score artifact.

`validated`: Vector, metric, or paper-specific validation has completed.

`terminated`: Pod or background process is confirmed stopped after preservation.

`failed`: Run cannot continue or produced invalid outputs. Failure cause must be recorded in `notes`.

## Minimal Example

```json
{
  "run_id": "paper1_5_qwen_trickster_phase1_2026-05-26",
  "pod_id": "unknown",
  "ssh_endpoint": "213.173.102.6:22707",
  "gpu_type": "A100 80GB",
  "start_time": "2026-05-25T22:00:00-07:00",
  "latest_heartbeat": "2026-05-26T06:00:00-07:00",
  "latest_rollout": "1200/1200",
  "current_status": "validated",
  "local_snapshot_status": "copied locally under research/q2_stability/qwen/outputs/paper1_5",
  "integrity_status": "passed 1200 records, 1200 activation shards, shape [5120]",
  "preservation_status": "manifest, log, JSONL, script, activations, integrity outputs preserved",
  "termination_status": "confirmed",
  "expected_completion": "complete",
  "scoring_status": "Codex GPT-5.5 adaptive scoring complete at 64 scored records",
  "validation_status": "passed, Lu cosine 0.957557 for score>=2 vector",
  "model_provenance": {
    "generation_model": "Qwen/Qwen3-32B",
    "evaluation_model": "Codex GPT-5.5 Standard",
    "analysis_model": null,
    "script_author_model": "GPT-5.5 Standard via Codex",
    "orchestration_agent": "Codex",
    "provider": "huggingface",
    "model_version_or_alias": "Qwen/Qwen3-32B"
  },
  "notes": "Strict gpt-4.1-mini scoring remains blocked by API quota."
}
```
