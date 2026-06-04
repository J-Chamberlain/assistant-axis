# PC2 Trait-Stratified Profile Report

## Startup Status

Startup verified against the raw GitHub startup files listed in `research/STARTUP_MANIFEST.md` using cache-busted direct fetches. No GPU work, API calls, or new judge calls were run.

## Sources

- Geometry: `research/visualizations/geometry_viz_data.json`
- Trait profile: `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`
- Prior trait prediction stats: `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json`
- Prior muted-PC1 PC2 diagnostic: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_top_bottom.csv`
- Prior cluster-conditioned PC2 diagnostic: `research/outputs/pc2_cluster_conditioned_extremes/pc2_diagnostic_roles_table.csv`

## Dataset

- Roles/personas: 275
- Traits: 240
- Source model: `Qwen/Qwen3-32B`
- Trait-profile model/layer: `Qwen/Qwen3-32B`, layer `48`
- Trait score meaning: activation-space cosine between mean role vector and mean trait vector.

## PC1 Strata

| stratum | n_roles | tail_n_each | high_pc2_min | low_pc2_max |
| --- | --- | --- | --- | --- |
| global | 275 | 55 | 16.408 | -16.363 |
| low_pc1 | 92 | 19 | 23.678 | -28.739 |
| mid_pc1 | 91 | 19 | 20.848 | -10.173 |
| high_pc1 | 92 | 19 | 3.326 | -12.406 |
| pc1_q1 | 55 | 11 | 13.633 | -32.195 |
| pc1_q2 | 55 | 11 | 36.543 | -12.916 |
| pc1_q3 | 55 | 11 | 24.950 | -7.986 |
| pc1_q4 | 55 | 11 | 9.317 | -12.380 |
| pc1_q5 | 55 | 11 | -0.045 | -12.406 |
| central_pc1_muted_45_55 | 27 | 6 | 21.109 | -11.561 |

## Global High-PC2 Enriched Traits

| trait | cohens_d | mean_diff_high_minus_low | cliffs_delta | bootstrap_ci_low | bootstrap_ci_high |
| --- | --- | --- | --- | --- | --- |
| practical | 4.209 | 0.116 | 1.000 | 0.107 | 0.126 |
| experiential | 4.109 | 0.118 | 1.000 | 0.107 | 0.129 |
| casual | 3.274 | 0.144 | 1.000 | 0.128 | 0.160 |
| grounded | 3.175 | 0.114 | 0.964 | 0.101 | 0.130 |
| contemporary | 3.142 | 0.118 | 0.972 | 0.106 | 0.132 |
| inquisitive | 2.799 | 0.049 | 0.984 | 0.042 | 0.055 |
| accessible | 2.522 | 0.104 | 0.956 | 0.089 | 0.119 |
| extroverted | 2.494 | 0.107 | 0.968 | 0.093 | 0.123 |
| gregarious | 2.486 | 0.104 | 0.942 | 0.089 | 0.120 |
| anxious | 2.472 | 0.111 | 0.966 | 0.096 | 0.128 |
| adaptable | 2.360 | 0.079 | 0.900 | 0.069 | 0.090 |
| reductionist | 2.301 | 0.070 | 0.888 | 0.057 | 0.080 |
| nonchalant | 2.095 | 0.098 | 0.892 | 0.082 | 0.115 |
| reactive | 2.058 | 0.101 | 0.913 | 0.084 | 0.118 |
| accommodating | 1.989 | 0.091 | 0.839 | 0.074 | 0.108 |

## Global Low-PC2 Enriched Traits

| trait | cohens_d | mean_diff_high_minus_low | cliffs_delta | bootstrap_ci_low | bootstrap_ci_high |
| --- | --- | --- | --- | --- | --- |
| ritualistic | -4.448 | -0.156 | -1.000 | -0.172 | -0.144 |
| conceptual | -4.075 | -0.120 | -1.000 | -0.131 | -0.109 |
| abstract | -3.832 | -0.118 | -1.000 | -0.130 | -0.108 |
| theoretical | -3.799 | -0.122 | -1.000 | -0.134 | -0.110 |
| principled | -3.685 | -0.087 | -1.000 | -0.096 | -0.078 |
| introverted | -3.619 | -0.152 | -1.000 | -0.168 | -0.137 |
| reverent | -3.437 | -0.151 | -0.997 | -0.167 | -0.134 |
| pensive | -3.349 | -0.114 | -1.000 | -0.125 | -0.103 |
| formal | -3.233 | -0.145 | -1.000 | -0.163 | -0.130 |
| ascetic | -3.172 | -0.123 | -0.982 | -0.135 | -0.108 |
| idealistic | -3.133 | -0.124 | -0.965 | -0.138 | -0.109 |
| solemn | -3.056 | -0.148 | -1.000 | -0.166 | -0.131 |
| big_picture | -2.867 | -0.084 | -0.999 | -0.096 | -0.073 |
| serious | -2.855 | -0.139 | -0.996 | -0.157 | -0.122 |
| erudite | -2.837 | -0.121 | -0.986 | -0.136 | -0.106 |

## Top Traits By PC1 Stratum

| stratum | pole | trait | cohens_d |
| --- | --- | --- | --- |
| global | high_pc2 | practical | 4.209 |
| global | high_pc2 | experiential | 4.109 |
| global | high_pc2 | casual | 3.274 |
| global | high_pc2 | grounded | 3.175 |
| global | high_pc2 | contemporary | 3.142 |
| global | low_pc2 | ritualistic | -4.448 |
| global | low_pc2 | conceptual | -4.075 |
| global | low_pc2 | abstract | -3.832 |
| global | low_pc2 | theoretical | -3.799 |
| global | low_pc2 | principled | -3.685 |
| low_pc1 | high_pc2 | grounded | 5.633 |
| low_pc1 | high_pc2 | casual | 5.627 |
| low_pc1 | high_pc2 | experiential | 5.370 |
| low_pc1 | high_pc2 | practical | 5.367 |
| low_pc1 | high_pc2 | contemporary | 5.310 |
| low_pc1 | low_pc2 | ritualistic | -7.326 |
| low_pc1 | low_pc2 | idealistic | -5.918 |
| low_pc1 | low_pc2 | fatalistic | -5.674 |
| low_pc1 | low_pc2 | formal | -5.561 |
| low_pc1 | low_pc2 | ascetic | -5.555 |
| mid_pc1 | high_pc2 | experiential | 3.897 |
| mid_pc1 | high_pc2 | practical | 3.723 |
| mid_pc1 | high_pc2 | grounded | 3.385 |
| mid_pc1 | high_pc2 | casual | 3.351 |
| mid_pc1 | high_pc2 | inquisitive | 3.207 |
| mid_pc1 | low_pc2 | abstract | -3.798 |
| mid_pc1 | low_pc2 | conceptual | -3.752 |
| mid_pc1 | low_pc2 | theoretical | -3.702 |
| mid_pc1 | low_pc2 | ascetic | -3.584 |
| mid_pc1 | low_pc2 | ritualistic | -3.551 |
| high_pc1 | high_pc2 | experiential | 5.024 |
| high_pc1 | high_pc2 | practical | 4.551 |
| high_pc1 | high_pc2 | accessible | 4.505 |
| high_pc1 | high_pc2 | casual | 4.081 |
| high_pc1 | high_pc2 | grounded | 3.468 |
| high_pc1 | low_pc2 | erudite | -5.119 |
| high_pc1 | low_pc2 | introverted | -4.893 |
| high_pc1 | low_pc2 | theoretical | -4.831 |
| high_pc1 | low_pc2 | abstract | -4.489 |
| high_pc1 | low_pc2 | esoteric | -4.443 |
| pc1_q1 | high_pc2 | nonchalant | 4.732 |
| pc1_q1 | high_pc2 | visceral | 4.376 |
| pc1_q1 | high_pc2 | contemporary | 4.162 |
| pc1_q1 | high_pc2 | utilitarian | 4.157 |
| pc1_q1 | high_pc2 | casual | 4.144 |
| pc1_q1 | low_pc2 | idealistic | -5.969 |
| pc1_q1 | low_pc2 | principled | -5.654 |
| pc1_q1 | low_pc2 | reverent | -5.251 |
| pc1_q1 | low_pc2 | ritualistic | -4.890 |
| pc1_q1 | low_pc2 | solemn | -4.577 |
| pc1_q2 | high_pc2 | visceral | 6.218 |
| pc1_q2 | high_pc2 | reactive | 5.517 |
| pc1_q2 | high_pc2 | casual | 5.351 |
| pc1_q2 | high_pc2 | practical | 5.322 |
| pc1_q2 | high_pc2 | experiential | 5.305 |
| pc1_q2 | low_pc2 | ritualistic | -5.486 |
| pc1_q2 | low_pc2 | methodical | -5.366 |
| pc1_q2 | low_pc2 | formal | -5.331 |
| pc1_q2 | low_pc2 | stoic | -5.202 |
| pc1_q2 | low_pc2 | abstract | -5.161 |
| pc1_q3 | high_pc2 | anxious | 7.525 |
| pc1_q3 | high_pc2 | neurotic | 7.375 |
| pc1_q3 | high_pc2 | reactive | 6.282 |
| pc1_q3 | high_pc2 | casual | 5.293 |
| pc1_q3 | high_pc2 | disorganized | 4.939 |
| pc1_q3 | low_pc2 | conscientious | -8.221 |
| pc1_q3 | low_pc2 | resilient | -6.793 |
| pc1_q3 | low_pc2 | calculating | -5.687 |
| pc1_q3 | low_pc2 | meticulous | -5.675 |
| pc1_q3 | low_pc2 | pensive | -5.575 |
| pc1_q4 | high_pc2 | experiential | 5.822 |
| pc1_q4 | high_pc2 | casual | 5.494 |
| pc1_q4 | high_pc2 | practical | 5.124 |
| pc1_q4 | high_pc2 | grounded | 4.682 |
| pc1_q4 | high_pc2 | contemporary | 4.300 |
| pc1_q4 | low_pc2 | ritualistic | -6.226 |
| pc1_q4 | low_pc2 | abstract | -5.871 |
| pc1_q4 | low_pc2 | conceptual | -5.682 |
| pc1_q4 | low_pc2 | formal | -5.661 |
| pc1_q4 | low_pc2 | theoretical | -5.493 |
| pc1_q5 | high_pc2 | experiential | 4.761 |
| pc1_q5 | high_pc2 | accessible | 4.678 |
| pc1_q5 | high_pc2 | practical | 4.300 |
| pc1_q5 | high_pc2 | optimistic | 3.893 |
| pc1_q5 | high_pc2 | accommodating | 3.628 |
| pc1_q5 | low_pc2 | erudite | -5.125 |
| pc1_q5 | low_pc2 | theoretical | -4.627 |
| pc1_q5 | low_pc2 | introverted | -4.527 |
| pc1_q5 | low_pc2 | perfectionist | -4.404 |
| pc1_q5 | low_pc2 | deterministic | -4.192 |
| central_pc1_muted_45_55 | high_pc2 | reactive | 5.217 |
| central_pc1_muted_45_55 | high_pc2 | casual | 5.020 |
| central_pc1_muted_45_55 | high_pc2 | impulsive | 4.928 |
| central_pc1_muted_45_55 | high_pc2 | visceral | 4.869 |
| central_pc1_muted_45_55 | high_pc2 | experiential | 4.636 |
| central_pc1_muted_45_55 | low_pc2 | conscientious | -5.901 |
| central_pc1_muted_45_55 | low_pc2 | ritualistic | -5.097 |
| central_pc1_muted_45_55 | low_pc2 | formal | -5.085 |
| central_pc1_muted_45_55 | low_pc2 | meticulous | -4.837 |
| central_pc1_muted_45_55 | low_pc2 | ascetic | -4.826 |

## Replicated Traits Across PC1 Quintiles

High-PC2 replicated traits:

| trait | n_quintile_strata_abs_d_ge_0_5_same_sign | mean_cohens_d_across_quintiles | global_cohens_d | supporting_strata |
| --- | --- | --- | --- | --- |
| experiential | 5 | 4.840 | 4.109 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| casual | 5 | 4.743 | 3.274 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| practical | 5 | 4.471 | 4.209 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| reactive | 5 | 4.355 | 2.058 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| grounded | 5 | 4.070 | 3.175 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| anxious | 5 | 4.064 | 2.472 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| neurotic | 5 | 4.060 | 1.958 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| visceral | 5 | 3.970 | 1.606 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| impulsive | 5 | 3.823 | 1.648 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| accessible | 5 | 3.466 | 2.522 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| contemporary | 5 | 3.448 | 3.142 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| impatient | 5 | 3.438 | 1.969 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| nonchalant | 5 | 3.397 | 2.095 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| hedonistic | 5 | 3.208 | 1.799 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| disorganized | 5 | 3.151 | 1.744 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| stream_of_consciousness | 5 | 3.139 | 1.757 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| gregarious | 5 | 3.089 | 2.486 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| extroverted | 5 | 3.083 | 2.494 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| flippant | 5 | 2.937 | 1.821 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| entertaining | 5 | 2.889 | 1.753 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |

Low-PC2 replicated traits:

| trait | n_quintile_strata_abs_d_ge_0_5_same_sign | mean_cohens_d_across_quintiles | global_cohens_d | supporting_strata |
| --- | --- | --- | --- | --- |
| ritualistic | 5 | -4.923 | -4.448 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| conscientious | 5 | -4.814 | -2.395 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| formal | 5 | -4.766 | -3.233 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| abstract | 5 | -4.699 | -3.832 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| conceptual | 5 | -4.614 | -4.075 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| pensive | 5 | -4.561 | -3.349 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| serious | 5 | -4.540 | -2.855 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| theoretical | 5 | -4.509 | -3.799 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| meticulous | 5 | -4.398 | -2.725 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| introverted | 5 | -4.275 | -3.619 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| solemn | 5 | -4.232 | -3.056 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| perfectionist | 5 | -4.059 | -2.761 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| stoic | 5 | -4.039 | -2.721 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| erudite | 5 | -3.932 | -2.837 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| idealistic | 5 | -3.916 | -3.133 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| fatalistic | 5 | -3.579 | -2.051 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| reverent | 5 | -3.561 | -3.437 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| big_picture | 5 | -3.549 | -2.867 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| principled | 5 | -3.472 | -3.685 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |
| resilient | 5 | -3.463 | -1.515 | pc1_q1, pc1_q2, pc1_q3, pc1_q4, pc1_q5 |

## PC1-Controlled Residual Traits

Positive PC1-controlled residual correlations:

| trait | corr_trait_with_pc2_residual | beta_trait_pc1_controlled |
| --- | --- | --- |
| experiential | 0.942 | 0.952 |
| practical | 0.905 | 0.907 |
| casual | 0.813 | 1.176 |
| accessible | 0.789 | 0.860 |
| inquisitive | 0.776 | 0.792 |
| gregarious | 0.761 | 0.988 |
| humble | 0.760 | 0.760 |
| anxious | 0.748 | 1.113 |
| extroverted | 0.738 | 1.135 |
| adaptable | 0.721 | 0.721 |
| contemporary | 0.720 | 1.167 |
| accommodating | 0.702 | 0.762 |

Negative PC1-controlled residual correlations:

| trait | corr_trait_with_pc2_residual | beta_trait_pc1_controlled |
| --- | --- | --- |
| introverted | -0.954 | -0.969 |
| ritualistic | -0.945 | -0.997 |
| pensive | -0.932 | -0.955 |
| theoretical | -0.901 | -0.901 |
| abstract | -0.898 | -0.923 |
| reverent | -0.888 | -0.889 |
| conceptual | -0.880 | -0.948 |
| principled | -0.852 | -0.852 |
| solemn | -0.840 | -1.076 |
| erudite | -0.834 | -0.934 |
| formal | -0.815 | -1.176 |
| big_picture | -0.797 | -0.836 |

## Interpretation Update

The trait-profile evidence supports and sharpens the current PC2 wording. High PC2 is best read as a context-shaped pole: situated immediacy, practical/experiential grounding, accessibility, responsiveness/accommodation, affective or developmental exposure, and performance pressure appear repeatedly after stratifying by PC1. Low PC2 is best read as a stable/internalized pole: abstraction, conceptual/theoretical structure, ritual/formal organization, conscientiousness, emotional reserve, and durable self-organization appear repeatedly after PC1 stratification and covariate checks.

This revises the wording slightly. `Situated/formative/impressionable versus integrated/stable` remains valid, but the trait evidence makes `context-reactive/accommodating/situated versus stable/internalized/integrated` the cleaner operational phrasing for future rubrics.

## Caveats

- Trait profiles are 240-dimensional activation-space cosine features, not independent psychological ratings.
- Stratification reduces PC1 confounding but does not remove cluster semantics or correlated-feature effects.
- Replication across PC1 quintiles is descriptive, not a preregistered hypothesis test.
- PC2 remains provisional and should not be presented as causal.
