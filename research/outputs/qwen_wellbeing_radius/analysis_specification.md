# Qwen finite-radius analysis specification

Frozen before optimization, 2026-09-21. Scope: all 275 Qwen personas, five original persona PCs primary; first three PCs sensitivity. Both frozen AA21 primary expanded and corrected AA22 direct-trait scores are evaluated for every movement. No model inference or causal claim.

Use Euclidean distance in raw activation PC units. Radii are 0.25, 0.5, and 1 times the median fifth-nearest-neighbor distance among the original 275 five-PC points. Use the same numerical radii in three PCs for comparability. These are exploratory scale choices, not human-plausibility thresholds. Standardizations remain fixed across all movements.

Hold each persona's residual outside the selected PCs fixed. Move h to h+P delta and recompute its norm and all 240 signed-cosine traits. Score with the exact frozen readouts and compute C1–C5 differences with Qwen's frozen AA18 model-specific trait scoring weights, not consensus trait loadings. Consensus changes are in original persona-population score SD units. The baseline/endpoint and delta for both well-being scores, plus changes in each PC and C1–C5, are saved.

Optimize over the sphere at each specified radius (the user's perimeter question). Also include a no-movement baseline in the summaries: no positive improvement is not a recommendation to move. Three starts per bridge: top separated directions from a reproducible 512-direction sphere sample, including gradient directions. Report optimizer status, constraint residuals, and distinct converged local maxima separated by at least 15 degrees within each objective; a multistart search is evidence of detected solutions, not a proof of peak count.

Three primary candidates: maximum Big Five gain, maximum direct-trait gain, and maximum minimum fraction of each bridge's individually attainable gain. This compromise uses gain fractions because the two score scales differ. If either best gain is nonpositive, flag rather than silently divide by it.

For each individual bridge, seek two additional sphere directions with at least 45 degrees separation from its optimum and each preceding alternative. Label alternatives by whether they retain at least 90% or 80% of that bridge's best gain. These angularly constrained alternatives are not additional unconstrained peaks. Score all alternatives under both bridges.

Support diagnostics: fifth-neighbor distance at endpoint and at five equally spaced path points; flag when it exceeds the 95th percentile of leave-self-out fifth-neighbor distances at original personas. This descriptive low-dimensional coverage flag is not a human-plausibility or safety test; it is not imposed as an optimization constraint.

Verification: hash public role tensors; reproduce original PC coordinates, role norms, all 240 trait profiles, both bridge scores, and frozen consensus scores. Numerically compare analytic score gradients to finite differences and verify all reported endpoints via direct full-vector recomputation. CPU-only. Model identity/effort unavailable; recorded unknown.
