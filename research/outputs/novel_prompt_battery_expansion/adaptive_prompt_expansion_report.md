# Adaptive Prompt Expansion For High-PC3 And High-PC2 H100 Coverage

Model used for synthesis and script authoring: GPT-5.5.

## Objective

The first novel prompt battery produced 120 prompts but populated only 11 / 27 target cells. This expansion targeted under-covered high-PC3 and high-PC2 regions using an auditable forecaster-feedback loop instead of stopping once a total prompt count was reached.

## Inputs

- Prior battery: `research/outputs/novel_prompt_battery/novel_prompt_battery.csv`
- Prior H100 manifest: `research/outputs/novel_prompt_battery/h100_prompt_run_manifest.csv`
- Prior coverage stats: `research/outputs/novel_prompt_battery/novel_prompt_battery_coverage_stats.json`
- Target grid: `research/outputs/novel_prompt_battery/target_coordinate_grid.csv`
- Frozen forecaster manifest: `research/outputs/novel_prompt_battery/frozen_forecaster_manifest.json`
- Frozen forecaster model: `research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib`
- Stable forecaster hash: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`

The script verified the stable forecaster hash against the expected value `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f` before candidate scoring.

## Target Selection

Targets prioritized high-PC3 cells, high-PC2 cells, under-covered cells adjacent to already populated high-PC3 regions, and mid/low-PC1 regions more reachable by the current lightweight forecaster. High-PC1 cells were deprioritized unless they also tested high-PC2/high-PC3 coverage.

- `pc1_mid__pc2_high__pc3_high`: desired 2, priority 14; high-PC3 frontier; high-PC2 frontier; mid-PC1 reachable boundary; prior count 0 below goal 2
- `pc1_low__pc2_high__pc3_high`: desired 2, priority 11; high-PC3 frontier; high-PC2 frontier; low-PC1 open-possibility boundary
- `pc1_mid__pc2_low__pc3_high`: desired 2, priority 10; high-PC3 frontier; mid-PC1 reachable boundary; prior count 0 below goal 2
- `pc1_mid__pc2_mid__pc3_high`: desired 2, priority 10; high-PC3 frontier; mid-PC1 reachable boundary; prior count 0 below goal 2
- `pc1_high__pc2_high__pc3_high`: desired 2, priority 9; high-PC3 frontier; high-PC2 frontier; prior count 0 below goal 2; high-PC1 deprioritized calibration
- `pc1_low__pc2_mid__pc3_high`: desired 2, priority 9; high-PC3 frontier; low-PC1 open-possibility boundary; prior count 1 below goal 2
- `pc1_mid__pc2_high__pc3_low`: desired 2, priority 9; high-PC2 frontier; mid-PC1 reachable boundary; prior count 0 below goal 2
- `pc1_mid__pc2_high__pc3_mid`: desired 2, priority 9; high-PC2 frontier; mid-PC1 reachable boundary; prior count 0 below goal 2
- `pc1_low__pc2_low__pc3_high`: desired 2, priority 7; high-PC3 frontier; low-PC1 open-possibility boundary
- `pc1_low__pc2_high__pc3_low`: desired 2, priority 6; high-PC2 frontier; low-PC1 open-possibility boundary
- `pc1_low__pc2_high__pc3_mid`: desired 2, priority 6; high-PC2 frontier; low-PC1 open-possibility boundary
- `pc1_mid__pc2_mid__pc3_low`: desired 2, priority 5; mid-PC1 reachable boundary; prior count 0 below goal 2
- `pc1_mid__pc2_mid__pc3_mid`: desired 2, priority 5; mid-PC1 reachable boundary; prior count 0 below goal 2

## Adaptive Loop

For each target cell, the script generated up to 10 rounds with 12 candidates per round. Each round scored candidates with the frozen forecaster, checked explicit role names, checked operational-harm terms, measured approximate similarity against released role/trait prompt artifacts, compared the predicted coordinates to the target cell, and fed the coordinate miss into the next round's prompt construction.

The generator was deterministic and local. No model APIs, pods, or activation runs were used. It used behavioral target descriptions and coordinate-error feedback such as "predicted_PC3 too low" or "predicted_PC2 too low"; it did not use explicit persona role labels.

## Candidate Accounting

- Generated/logged candidates: 516
- Accepted candidates: 60
- Rejected candidates: 456
- Rounds per cell: `{"pc1_high__pc2_high__pc3_high": 4, "pc1_low__pc2_high__pc3_high": 5, "pc1_low__pc2_mid__pc3_high": 10, "pc1_mid__pc2_high__pc3_high": 4, "pc1_mid__pc2_high__pc3_low": 8, "pc1_mid__pc2_low__pc3_high": 4, "pc1_mid__pc2_mid__pc3_high": 8}`
- Rejection reasons: `{"coordinate_miss": 70, "coordinate_miss;mixed_boundary_not_high_pc3": 117, "coordinate_miss;safety_adjacent_not_high_pc3": 61, "mixed_boundary_not_high_pc3": 133, "safety_adjacent_not_high_pc3": 71, "target_cell_quota_met": 2, "target_cell_quota_met;coordinate_miss": 2}`

## Before / After Coverage

Prior battery:

- Prompts: 120
- Populated target cells: 11 / 27
- High-PC3 prompts above prior PC3 75th percentile (9.699): 30
- High-PC2 prompts above prior PC2 75th percentile (-4.735): 30
- Predicted PC3 range: -9.096 to 18.527
- Predicted PC2 range: -24.490 to 12.958

Supplemental battery:

- Prompts: 60
- Populated target cells: 7 / 27
- High-PC3 prompts above prior PC3 75th percentile: 38
- High-PC2 prompts above prior PC2 75th percentile: 44
- High-PC3 target-cell prompts: 38
- High-PC2 target-cell prompts: 35
- Safety-adjacent high-PC3 prompts: 12
- Mixed-boundary high-PC3 prompts: 26
- Predicted PC3 range: -6.501 to 16.973
- Predicted PC2 range: -15.464 to 7.794

Combined battery:

- Prompts: 180
- Populated target cells: 16 / 27
- High-PC3 prompts above prior PC3 75th percentile: 68
- High-PC2 prompts above prior PC2 75th percentile: 74
- Safety-adjacent high-PC3 prompts: 19
- Mixed-boundary high-PC3 prompts: 38

## Leakage And Safety Checks

- Supplemental explicit role-name flags: 0
- Supplemental operational-harm flags: 0
- Supplemental max artifact similarity: 0.104
- Supplemental mean artifact similarity: 0.069

## Readiness Judgment

Status: **ready**.

Use `combined_h100_prompt_manifest.csv` for the next H100 validation, but stage execution by running the supplemental high-PC3/high-PC2 subset first. The combined set preserves neutral controls and the first-pass coverage while adding the targeted frontier prompts.

## Limitations

The expansion still depends on the lightweight text forecaster as a design filter, so high-PC3/high-PC2 coverage means predicted coverage, not measured activation coverage. Some target cells may remain unreachable without explicit labels or more aggressive language, and the script intentionally rejects operationally harmful prompts. The future H100 run should therefore evaluate deltas between predicted and measured coordinates rather than treating the predicted addresses as ground truth.
