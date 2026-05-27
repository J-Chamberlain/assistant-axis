# Original vs No-Label Prompt Semantic Comparison

## Method

No local `sentence-transformers` or `scikit-learn` installation was available, so this analysis uses a local TF-IDF representation with unigrams and bigrams plus a NumPy SVD reduction. This is an offline prompt-space topology audit, not an activation-space test.

## Headline Results

- Roles analyzed: 275
- Prompts analyzed: 1375
- Prompt-level TF-IDF original-vs-rewrite cosine median: 0.933
- Role-level TF-IDF cosine median: 0.984
- Role-level TF-IDF+SVD cosine median: 0.998
- Nearest-neighbor preservation fraction: 0.924
- Pairwise distance correlation, SVD role space: 0.985

## Cluster Preservation

| k | ARI original vs no-label | NMI original vs no-label |
|---:|---:|---:|
| 5 | 0.197 | 0.260 |
| 7 | 0.153 | 0.260 |
| 10 | 0.181 | 0.366 |

## Comparison to Existing Activation-Space Labels

Existing activation-space labels from `visualizations/full_ranking.csv` were available. These comparisons are exploratory because prompt-space clusters and activation-space clusters are not expected to be identical objects.

| k | ARI activation vs original | ARI activation vs no-label | NMI activation vs original | NMI activation vs no-label |
|---:|---:|---:|---:|---:|
| 5 | 0.156 | 0.088 | 0.187 | 0.161 |
| 7 | 0.060 | 0.082 | 0.146 | 0.164 |
| 10 | 0.091 | 0.110 | 0.214 | 0.204 |

## Most Changed Roles

| Role | SVD displacement | SVD cosine | TF-IDF cosine |
|---|---:|---:|---:|
| `advocate` | 0.065 | 0.935 | 0.794 |
| `guardian` | 0.037 | 0.963 | 0.680 |
| `amateur` | 0.032 | 0.968 | 0.740 |
| `predator` | 0.031 | 0.969 | 0.775 |
| `familiar` | 0.028 | 0.972 | 0.872 |
| `wanderer` | 0.027 | 0.973 | 0.757 |
| `echo` | 0.027 | 0.973 | 0.898 |
| `warrior` | 0.026 | 0.974 | 0.751 |
| `mycorrhizal` | 0.022 | 0.978 | 0.818 |
| `coral_reef` | 0.020 | 0.980 | 0.966 |
| `student` | 0.020 | 0.980 | 0.805 |
| `crystalline` | 0.019 | 0.981 | 0.938 |
| `idealist` | 0.019 | 0.981 | 0.695 |
| `activist` | 0.018 | 0.982 | 0.744 |
| `chimera` | 0.017 | 0.983 | 0.974 |
| `virtuoso` | 0.015 | 0.985 | 0.968 |
| `spirit` | 0.015 | 0.985 | 0.924 |
| `guide` | 0.015 | 0.985 | 0.811 |
| `ecosystem` | 0.015 | 0.985 | 0.815 |
| `revolutionary` | 0.014 | 0.986 | 0.819 |

## Least Changed Roles

| Role | SVD displacement | SVD cosine | TF-IDF cosine |
|---|---:|---:|---:|
| `addict` | -0.000 | 1.000 | 1.000 |
| `altruist` | -0.000 | 1.000 | 1.000 |
| `criminal` | -0.000 | 1.000 | 1.000 |
| `collaborator` | -0.000 | 1.000 | 1.000 |
| `cynic` | -0.000 | 1.000 | 1.000 |
| `devils_advocate` | -0.000 | 1.000 | 1.000 |
| `martyr` | -0.000 | 1.000 | 1.000 |
| `pragmatist` | -0.000 | 1.000 | 1.000 |
| `refugee` | -0.000 | 1.000 | 1.000 |
| `retiree` | -0.000 | 1.000 | 1.000 |
| `vigilante` | -0.000 | 1.000 | 1.000 |
| `avatar` | 0.000 | 1.000 | 1.000 |
| `blogger` | 0.000 | 1.000 | 1.000 |
| `competitor` | 0.000 | 1.000 | 1.000 |
| `gamer` | 0.000 | 1.000 | 1.000 |
| `genie` | 0.000 | 1.000 | 1.000 |
| `grandparent` | 0.000 | 1.000 | 1.000 |
| `improviser` | 0.000 | 1.000 | 1.000 |
| `optimist` | 0.000 | 1.000 | 1.000 |
| `realist` | 0.000 | 1.000 | 1.000 |

## Interpretation

The no-label rewrite preserves a substantial amount of prompt-space semantic topology if role-level cosine and pairwise distance correlation remain high, but any loss of nearest-neighbor or cluster preservation indicates that explicit labels contribute materially to the original prompt-space organization. This analysis does not establish what will happen in activation space. It motivates a small no-label activation stress test only if the rewritten prompt space remains coherent enough to be a fair intervention.
