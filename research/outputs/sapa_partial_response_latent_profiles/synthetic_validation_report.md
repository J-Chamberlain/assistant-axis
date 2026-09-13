# Synthetic validation report

Status: **PASS**

The frozen sparse product-multinomial implementation was tested on 4,000 simulated respondents, 120 six-category items, and 4 known latent classes. Heterogeneous class-independent planned missingness left 12.89% of cells observed (87.11% missing), with a median of 10 answered items. Missing cells entered neither the likelihood nor sufficient statistics.

Six deterministic starts were attempted and 6 converged monotonically. The retained seed was `2026091701` after 25 iterations. After frozen weighted Jensen–Shannon/Hungarian alignment, mean profile distance was 0.066943, adjusted Rand index was 0.878693, and aligned MAP accuracy was 0.953000.

Changing every stored value underneath the unchanged missingness mask had maximum likelihood/posterior effect 0.000e+00; this verifies that unobserved values are ignored rather than imputed. An explicit class-label permutation was recovered exactly. Median maximum posterior increased from 0.984474 in the bottom answered-count quartile to 1.000000 in the top quartile.

## Frozen-gate checks

- finite_monotone_likelihood: **PASS**
- probabilities_normalize: **PASS**
- mean_aligned_profile_distance_le_0_075: **PASS**
- adjusted_rand_index_ge_0_70: **PASS**
- aligned_map_accuracy_ge_0_80: **PASS**
- missing_storage_invariance_le_1e_12: **PASS**
- label_permutation_alignment_exact: **PASS**
- certainty_increases_with_answer_count: **PASS**

No SAPA item wording, human/model artifact, or external personality-profile literature was used.
