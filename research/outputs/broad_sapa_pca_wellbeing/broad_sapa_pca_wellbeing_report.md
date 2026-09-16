# AA-13 bounded report

The external SAPA V5 matrix exactly matches the frozen AA-10/AA-12 dependency fingerprint (23,679 rows × 719 columns; 696 psychological item columns plus administrative fields) and reproduces the frozen 13-item HiFWB eligibility count (8,664) and five-domain terrain eligibility count (8,585). The broad inventory contained 92 administered constructs; 79 were reconstructable after outcome-item overlap, duplicate, and coverage exclusions. The pairwise missingness-aware PCA retained 20 eigenvalues above one; PC1–PC3 are the visualization core.

The original first-pass 20-PC result is preserved: Big Five R²=0.447, broad PCs R²=0.211, combined R²=0.462, ΔR²=0.015 (N=783). Missingness-preserving parallel analysis used 200 deterministic within-construct permutations and retained K=26 (83.8 seconds); eigenvalue>1 retained K=30. With K=26, test R² was 0.447 Big Five, 0.203 broad PCs, and 0.454 combined. The 2,000 paired fixed-test bootstrap gave ΔR² mean 0.007, 95% interval [-0.007, 0.022], positive fraction 0.819.

Fifty training split-halves gave median K=3 subspace canonical correlation 0.940. This supports a stable low-dimensional subspace, while individual-axis stability and residual/instrument-balanced refits remain unresolved. The bounded incremental-validity conclusion is **C: no reliable incremental structure** pending deferred repeated-split and residual/instrument-balanced analyses.

BFAS alignment was omitted because no frozen, reproducible respondent-level BFAS scoring definition was available. No respondent identifiers or raw rows were written or committed, and no paid compute was used.
