# CURRENT_RESULTS.md
# Codex writes results here after completing a task.
# Claude and GPT fetch this file directly via raw GitHub URL.
# Raw URL: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/runtime/CURRENT_RESULTS.md
# Status: COMPLETE

## 2026-09-11 — Human-only SAPA bridge psychometric structure audit

Completed `research/outputs/sapa_bridge_psychometric_audit/` using only official SAPA V5 item responses, scoring keys, and the frozen Phase-1b bridge. Under a rubric frozen before covariance inspection, 12/45 direct links survive at moderate-or-better human-measurement support (9 high, 3 moderate), 30 are redundant/broad, and 3 single-item links are insufficient. The direct human proxy matrix retains 6 parallel-analysis components and participation-ratio rank 12.44; adding 29 close links contributes only 5 more moderate links. Planned missingness prevents complete profiles (median 10/96 direct items observed; median direct item-pair overlap 490). Deterministic reproduction and privacy/source/scoring checks pass. This is human-data structural support only: no model geometry or human-to-model projection was used, and no respondent-level data were committed.

## 2026-09-11 — SAPA Category-3 coordinate-blind second-pass review

Integrated the AA-1 human-data feasibility audit on top of the AA-2/AA-3 canonical state and froze a fixed-seed, decision-free packet for all 78 original SAPA Category-3 candidates before adjudication. The same-workflow Codex GPT-5.5 blinded semantic review retained 45 `ACCEPT_DIRECT` and 29 separately flagged `ACCEPT_CLOSE` links, downgraded 1 to broad, rejected 3, and left 0 ambiguous. The 74 retained links use 129 distinct items and 78 source scales, but planned missingness is substantial: respondents observe a median 13/129 retained items and none observes all 129. The bridge remains provisional; genuinely independent external review of the frozen packet is the next gate. No respondent-level data were committed and no human-to-model projection, respondent persona assignment, GPU, RunPod, model inference, activation extraction, or external model API was used.

## 2026-09-11 — Trait-profile to persona-PC predictor

Completed `research/outputs/trait_profile_pc_predictor/` using only existing Qwen/Qwen3-32B role/trait activation-vector artifacts and canonical PCA geometry. The transparent raw-cosine Ridge V1 reaches LOPO R2=0.999522/0.998811/0.999611 for PC1/PC2/PC3; fold-safe quantile LOPO remains strong but less precise; whole-cluster holdouts increase mean normalized error to 1.68x LOPO; the 100-permutation null is clean; and 120 pair-endpoint-held-out synthetic activation interpolations remain strongly predicted. The CLI supports existing personas, complete raw/percentile profiles, deterministic percentile edits, empirical LOPO error references, model disagreement, and OOD diagnostics. No GPU, RunPod, new model inference, new activations, or external model API was used.

## 2026-09-11 — SAPA/NLSY97 human-data feasibility audit

Completed `research/outputs/human_trait_dataset_feasibility/` from official Harvard Dataverse SAPA V5 and an official NLS Investigator public-use NLSY97 extraction. SAPA verifies at 23,679 respondents, 696 items, and 92 administered constructs; reviewed 240-trait coverage is 78 direct/near-direct, 49 close narrow, 41 broad-only, and 72 no-defensible-match. NLSY97 contains 7,044 complete Round-12 TIPI respondents and 6,261 with valid same-wave occupation, but only 2/98 translated persona-role rows reach N>=100 and both share one occupation cell; 71 are below N=20. Proceed only to independent review/preregistration of a restricted construct and occupation set. Raw human microdata remain gitignored; no human-to-model projection, respondent persona assignment, outcome association, GPU, RunPod, model inference, activation extraction, or external model API was used.
