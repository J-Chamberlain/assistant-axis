# Codex Card — Trait-Plus-Procedure Hybrid Benchmark

You are working in the assistant-axis repo on the Mac Mini.

GOAL
Run a small local benchmark to test whether a controlled trait-plus-procedure hybrid can improve canonical Qwen activation PCA prediction beyond Claude Big Five features.

Do not run pods.
Do not generate activations.
Use existing shared benchmark artifacts only.

STARTUP

Run:

```bash
cd /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis
pwd && git remote -v
git status --short
git log -8 --oneline
```

INPUTS

Use:

- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/semantic_baseline_features.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/codex_retained_features.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/combined_codex_claude_features.csv`

TASK

Create:

`research/q2_stability/qwen/scripts/trait_plus_procedure_hybrid_benchmark.py`

Evaluate these feature families on canonical activation PCA only:

1. Semantic baseline
2. Big Five only
3. Codex procedural/behavioral only
4. Big Five + Codex procedural
5. Big Five + selected nonredundant Codex features
6. Big Five x predeclared procedural interaction terms
7. Big Five + residual-specific features for high-error personas

Use the same five canonical splits from `shared_split_assignments.csv`.

MODELS

Run:

- Ridge regression with internal alpha selection
- ElasticNet or Lasso if available locally through sklearn
- If sklearn is unavailable, use Ridge only and document the gap

REPORT

For each feature family report:

- Mean held-out PCA3D R2
- Per-axis R2
- Delta versus semantic baseline
- Delta versus Big Five
- Mean residual norm
- Residual reduction versus Big Five
- Split-wise deltas versus Big Five
- Feature count
- Improvement per added feature
- Top 15 residual-improved personas versus Big Five
- Top 15 residual-worsened personas versus Big Five

PASS CRITERION

The hybrid passes only if it beats Big Five by at least +0.02 mean held-out R2 and reduces mean residual norm in at least four of five splits. If improvement is axis-specific, say so.

OUTPUTS

Write:

- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/hybrid_benchmark_results.json`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/hybrid_benchmark_summary.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/hybrid_benchmark_report.md`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/hybrid_persona_residuals.csv`

UPDATE

Update:

- `research/FINDINGS_LEDGER.md`
- `research/RESEARCH_STATE.md`

COMMIT

Commit:

```bash
git add research/q2_stability/qwen/scripts/trait_plus_procedure_hybrid_benchmark.py
git add -f research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/hybrid_*
git add research/FINDINGS_LEDGER.md research/RESEARCH_STATE.md
git commit -m "[paper1.5] test trait-plus-procedure hybrid benchmark"
git push myfork master
```

REPORT BACK

Report whether any hybrid model beats Big Five under the pass criterion, and include the raw GitHub URL for `hybrid_benchmark_report.md`.

