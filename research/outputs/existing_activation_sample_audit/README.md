# Audit bundle

Start with report.md; methods.md contains the detailed methodological audit. inventory.csv explicitly covers every expected persona/trait in each model and distinguishes original release aggregates, missing original sample sets, later project runs and third-party candidates.

The classes describe retained representations, not mutually independent datasets: text, coordinates and summaries can refer to the same response IDs. Do not sum inventory rows as sample counts. The missing original-sample entries mean not found in audited sources, not never retained or published. Default runs and noncanonical conditions do not increase the 275-persona count.

Verification:
    PYTHONDONTWRITEBYTECODE=1 python3 research/outputs/existing_activation_sample_audit/validate_audit.py
    PYTHONDONTWRITEBYTECODE=1 python3 research/outputs/existing_activation_sample_audit/check_linkage.py

audit_local.py prints fresh local metadata JSON; audit_scores.py counts saved score files. audit_remote.py performs bounded public metadata/header inspection, not model execution or full tensor downloading. It discovers the current remote revision and pins its subsequent file requests; use the preserved source_manifest.json revisions for this audit's historical evidence. These scripts do not regenerate the editorial inventory CSV or report.

source_manifest.json records per-input hashes and release metadata. run_metadata.json, remote_metadata.json, validation_summary.json and verification_result.json contain check details. disk_preservation.json, disk_usage_summary.md and cleanup_candidates.json record exactly which single presented package-download cache entry was removed. unrelated_work_snapshot.json supports preservation checks; it stores only filenames/status/hashes, not user file contents. HANDOFF.md preserves successor correction gates and identifies a possible later analysis without authorizing it.

No raw responses, activation tensors, weights, human records or caches are copied into this bundle. No push occurred.
