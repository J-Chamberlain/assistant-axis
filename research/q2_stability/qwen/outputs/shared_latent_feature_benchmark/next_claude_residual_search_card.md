# Claude Card — Residual Search After Big Five on Canonical Activation PCA

You are working from the assistant-axis repo and should use the shared benchmark files produced by Codex/GPT-5.5.

GOAL
Run a controlled Claude-side residual search using canonical Qwen activation PCA as the target. Big Five is the baseline to beat. The question is whether Claude can discover non-Big-Five features that improve held-out prediction after broad trait structure is already accounted for.

Do not use Claude pseudo-PCA as the primary target.
Do not generate activations.
Do not change the split assignments.

INPUTS

Use these exact files:

- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/semantic_baseline_features.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/codex_retained_features.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_persona_residual_rankings.csv`
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/convergence_status_report.md`

METHOD

1. Treat semantic baseline and Big Five as fixed baselines.
2. Fit Big Five on the canonical activation PCA target using the canonical splits.
3. Identify residual personas and residual directions after Big Five.
4. Propose a small number of candidate residual features.
5. Operationalize each feature deterministically across all personas.
6. Test whether the candidate features improve held-out prediction over Big Five.
7. Stop if two iterations fail to improve beyond Big Five.

REQUIRED FEATURE SEARCH DISCIPLINE

Candidate features must be interpretable and nonredundant with Big Five. Possible families:

- Procedural/operating-mode features
- Developmental or maturity-state features
- Role-function features
- Social agency or imposed-agency features
- Theatrical/performance features
- Residual-specific local features for high-error personas

Do not claim the discovered dimensions are final or causal.

METRICS

Report:

- Mean held-out PCA3D R2
- Per-axis R2
- Delta versus semantic baseline
- Delta versus Big Five
- Residual reduction versus Big Five
- Split-wise consistency of improvement
- Top residual-improved personas
- Top residual-worsened personas
- Feature count and complexity penalty

PASS CRITERION

A Claude residual feature set passes only if it improves over Big Five by at least +0.02 mean held-out R2 and reduces mean residual norm in at least four of five canonical splits.

OUTPUTS

Create a directory:

`research/q2_stability/qwen/outputs/claude_canonical_residual_search/`

Write:

- `claude_canonical_residual_search_results.json`
- `claude_canonical_residual_search_summary.csv`
- `claude_canonical_residual_search_report.md`
- `claude_candidate_feature_matrix.csv`
- `claude_residual_persona_rankings.csv`

INTERPRETATION

Answer:

1. Does Claude discover anything beyond Big Five on canonical activation PCA?
2. Are the new features procedural, trait refinements, developmental, role-functional, or something else?
3. Do the features converge with Codex procedural dimensions?
4. Does the result support trait-only, trait-plus-procedure, or target-specific interpretation?

COMMIT

Commit with:

`[paper1.5] Claude residual search after Big Five on canonical PCA`

