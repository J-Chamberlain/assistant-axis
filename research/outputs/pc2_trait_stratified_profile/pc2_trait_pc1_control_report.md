# PC1-Controlled PC2 Trait Diagnostics

## Method

For each trait, the script fit a standardized linear model:

`PC2_z ~ PC1_z + trait_z`

The reported trait coefficient is the association with PC2 after removing the linear PC1 component. A second diagnostic regressed PC2 on PC1, then correlated each trait with the residual.

Because PC1 and PC2 are PCA-orthogonal, regressing PC2 directly on PC1 produces a near-zero PC1 coefficient; target residualization therefore mostly reproduces PC2. The more useful control is the per-trait model that includes PC1 as a covariate, plus the PC1-stratified enrichment tables. Since individual trait features can be collinear with PC1 and with each other, the residual correlation column is the safer first-read statistic; the beta column is retained for auditability.

## Strongest Positive PC1-Controlled Residual Correlations

| trait | corr_trait_with_pc2_residual | beta_trait_pc1_controlled | r2_pc2_model |
| --- | --- | --- | --- |
| experiential | 0.942 | 0.952 | 0.896 |
| practical | 0.905 | 0.907 | 0.820 |
| casual | 0.813 | 1.176 | 0.957 |
| accessible | 0.789 | 0.860 | 0.679 |
| inquisitive | 0.776 | 0.792 | 0.614 |
| gregarious | 0.761 | 0.988 | 0.752 |
| humble | 0.760 | 0.760 | 0.578 |
| anxious | 0.748 | 1.113 | 0.833 |
| extroverted | 0.738 | 1.135 | 0.837 |
| adaptable | 0.721 | 0.721 | 0.520 |
| contemporary | 0.720 | 1.167 | 0.840 |
| accommodating | 0.702 | 0.762 | 0.535 |
| nonchalant | 0.661 | 1.151 | 0.761 |
| grounded | 0.649 | 1.192 | 0.774 |
| neurotic | 0.638 | 1.320 | 0.843 |

## Strongest Negative PC1-Controlled Residual Correlations

| trait | corr_trait_with_pc2_residual | beta_trait_pc1_controlled | r2_pc2_model |
| --- | --- | --- | --- |
| introverted | -0.954 | -0.969 | 0.924 |
| ritualistic | -0.945 | -0.997 | 0.942 |
| pensive | -0.932 | -0.955 | 0.890 |
| theoretical | -0.901 | -0.901 | 0.811 |
| abstract | -0.898 | -0.923 | 0.829 |
| reverent | -0.888 | -0.889 | 0.789 |
| conceptual | -0.880 | -0.948 | 0.834 |
| principled | -0.852 | -0.852 | 0.725 |
| solemn | -0.840 | -1.076 | 0.903 |
| erudite | -0.834 | -0.934 | 0.779 |
| formal | -0.815 | -1.176 | 0.959 |
| big_picture | -0.797 | -0.836 | 0.666 |
| essentialist | -0.785 | -0.870 | 0.683 |
| ascetic | -0.773 | -1.066 | 0.824 |
| perfectionist | -0.772 | -1.129 | 0.872 |

## Residual-Enrichment Check

Traits enriched in high residual-PC2 roles broadly overlap with stratified PC2 enrichment, but residual models remain correlational over trait-cosine features. They reduce PC1 confounding; they do not establish a causal trait basis for PC2.

Top residual high-PC2 traits:

| trait | cohens_d | mean_diff_high_minus_low | bootstrap_ci_low | bootstrap_ci_high |
| --- | --- | --- | --- | --- |
| practical | 4.209 | 0.116 | 0.106 | 0.125 |
| experiential | 4.109 | 0.118 | 0.107 | 0.129 |
| casual | 3.274 | 0.144 | 0.128 | 0.162 |
| grounded | 3.175 | 0.114 | 0.101 | 0.128 |
| contemporary | 3.142 | 0.118 | 0.106 | 0.131 |
| inquisitive | 2.799 | 0.049 | 0.044 | 0.055 |
| accessible | 2.522 | 0.104 | 0.088 | 0.119 |
| extroverted | 2.494 | 0.107 | 0.092 | 0.124 |
| gregarious | 2.486 | 0.104 | 0.088 | 0.119 |
| anxious | 2.472 | 0.111 | 0.096 | 0.129 |
| adaptable | 2.360 | 0.079 | 0.067 | 0.091 |
| reductionist | 2.301 | 0.070 | 0.058 | 0.082 |

Top residual low-PC2 traits:

| trait | cohens_d | mean_diff_high_minus_low | bootstrap_ci_low | bootstrap_ci_high |
| --- | --- | --- | --- | --- |
| ritualistic | -4.448 | -0.156 | -0.169 | -0.143 |
| conceptual | -4.075 | -0.120 | -0.130 | -0.110 |
| abstract | -3.832 | -0.118 | -0.130 | -0.108 |
| theoretical | -3.799 | -0.122 | -0.133 | -0.110 |
| principled | -3.685 | -0.087 | -0.095 | -0.079 |
| introverted | -3.619 | -0.152 | -0.168 | -0.137 |
| reverent | -3.437 | -0.151 | -0.168 | -0.137 |
| pensive | -3.349 | -0.114 | -0.126 | -0.100 |
| formal | -3.233 | -0.145 | -0.163 | -0.129 |
| ascetic | -3.172 | -0.123 | -0.138 | -0.107 |
| idealistic | -3.133 | -0.124 | -0.139 | -0.108 |
| solemn | -3.056 | -0.148 | -0.167 | -0.129 |
