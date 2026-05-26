# Run Status Artifact Specification

Purpose: every long-running extraction or dyad run should emit machine-readable artifacts that make recovery independent of chat context.

## `manifest.json`

Minimum fields: `run_id`, `created_at`, `repo_commit`, `script_path`, `script_sha256`, `model`, `model_revision`, `target_persona_or_condition`, `planned_records`, `output_dir`, `activation_dir`, `generation_settings`, `extraction_layer`, `hook_description`, `hardware`, `operator_notes`.

## `heartbeat.json`

Minimum fields: `run_id`, `timestamp`, `pid`, `status`, `latest_record_count`, `latest_activation_count`, `latest_work_unit`, `planned_records`, `truncated_count`, `discard_count`, `error_count`, `tokens_per_second_or_seconds_per_rollout`, `eta`, `gpu_memory_gb`, `disk_free_gb`, `log_path`.

## `integrity.json`

Minimum fields: `run_id`, `timestamp`, `input_jsonl`, `record_count`, `expected_record_count`, `unique_key_count`, `duplicate_keys`, `empty_response_count`, `think_artifact_count`, `activation_saved_count`, `activation_file_count`, `missing_activation_files`, `tensor_shape_checks`, `passed`, `notes`.

## `preservation.json`

Minimum fields: `run_id`, `timestamp`, `source_endpoint`, `destination_dir`, `files_copied`, `directories_copied`, `jsonl_count_after_copy`, `activation_count_after_copy`, `log_copied`, `script_copied`, `manifest_copied`, `copy_method`, `passed`, `notes`.

## `termination.json`

Minimum fields: `run_id`, `timestamp`, `pod_id`, `ssh_endpoint`, `termination_method`, `termination_requested_by`, `pre_termination_preservation_status`, `confirmation_method`, `confirmed_not_running`, `dashboard_evidence`, `api_response`, `notes`.

## `scoring_summary.json`

Minimum fields: `run_id`, `timestamp`, `judge_model`, `judge_context`, `score_file`, `records_scored`, `total_records`, `score_distribution`, `qualifying_rule`, `qualifying_count`, `strong_count`, `truncation_split`, `complete`, `notes`.

## `validation_summary.json`

Minimum fields: `run_id`, `timestamp`, `validation_script`, `score_file`, `reference_vector`, `candidate_vectors`, `best_candidate`, `cosine_to_reference`, `adaptive_stopping`, `passed`, `methodological_caveats`, `notes`.

## Naming Rule

Use stable names for canonical latest artifacts and timestamped names for snapshots. Example: write `heartbeat.json` repeatedly during the run and preserve timestamped copies such as `heartbeat_2026-05-26T060000.json` during monitoring checkpoints.
