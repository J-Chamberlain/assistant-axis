# CURRENT_RESULTS.md
# Codex writes results here after completing a task.
# Claude and GPT fetch this file directly via raw GitHub URL.
# Raw URL: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/runtime/CURRENT_RESULTS.md
# Status: COMPLETE

## 2026-09-11 — Held-out trait-profile geometry equalizer

Built `research/outputs/trait_profile_geometry_explorer/trait_profile_geometry_explorer.html` as an active companion viewer over the saved trait-profile predictor. It shows all 275 canonical personas in 2D/3D, loads and edits all 240 trait percentiles, and uses a separately fitted Ridge bundle that excludes the selected persona for both its baseline LOPO point and all subsequent edits. The interface includes actual/predicted displacement, q95 empirical held-out error references, nearest profiles, and the canonical OOD heuristic. All 275 live-browser baselines reproduce saved LOPO within 2.27e-12; 30 deterministic modified-profile cases agree with Python within 5.68e-13 in JavaScript-core tests; Python, Node, live headless Chrome, and existing trait-visualization regressions pass. The canonical explorer remained byte-identical. No GPU, RunPod, new model inference, activation extraction, or external model API was used; claims, findings, Paper 1.5 ledger, and sticky notes are unchanged.

## 2026-09-11 — Trait-profile to persona-PC predictor

Completed `research/outputs/trait_profile_pc_predictor/` using only existing Qwen/Qwen3-32B role/trait activation-vector artifacts and canonical PCA geometry. The transparent raw-cosine Ridge V1 reaches LOPO R2=0.999522/0.998811/0.999611 for PC1/PC2/PC3; fold-safe quantile LOPO remains strong but less precise; whole-cluster holdouts increase mean normalized error to 1.68x LOPO; the 100-permutation null is clean; and 120 pair-endpoint-held-out synthetic activation interpolations remain strongly predicted. The CLI supports existing personas, complete raw/percentile profiles, deterministic percentile edits, empirical LOPO error references, model disagreement, and OOD diagnostics. No GPU, RunPod, new model inference, new activations, or external model API was used.
