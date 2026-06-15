# PC1 Competing-Theories Test and Blind-Rating Validation

`model_used`: GPT-5.5 for local analysis/reporting.

## Startup Status

Startup check passed using cache-busted raw GitHub fetches for `STARTUP_MANIFEST.md`, `RESEARCH_STATE.md`, `THREAD_START.md`, and `CLAIMS_REGISTER.md`.

## Methods

Part A tested three transparent vocabulary feature families over the five role-conditioning instructions for the 273 common personas in the shared benchmark. It computed raw counts, length-normalized counts, signed contrasts, Pearson/Spearman correlations, partial correlations controlling text length, cluster-and-length controlled correlations, and held-out ridge-regression PC1 R2 using the same deterministic split assignments as `shared_latent_feature_benchmark`.

Part B was designed as a corrected blind-rating test using GPT-4.1-mini over role instructions only. Ratings were not exposed to PC coordinates, PCA labels, geometry information, cluster labels, or rankings.

## Part A Direct Comparison

| Theory | Pearson | Spearman | Cluster-controlled | Regression R2 |
|---|---:|---:|---:|---:|
| A_orderliness_conscientiousness | 0.175 | 0.166 | 0.058 | 0.774 |
| B_determination_explicit_criteria | -0.008 | 0.008 | 0.026 | 0.772 |
| C_external_standard_accountability | 0.306 | 0.342 | 0.192 | 0.781 |

## Observed

- Best Part A PC1 predictor by held-out regression R2: `C_external_standard_accountability` with R2=0.781.
- Control-only held-out regression using text length plus cluster already reaches R2=0.774; therefore theory-vocabulary incremental deltas are the stricter comparison.
- External-standard accountability incremental R2 over cluster/length controls is +0.0071, versus orderliness +0.0003 and determination -0.0023.
- External-standard accountability outperforms orderliness/conscientiousness by held-out regression R2 (0.781 vs 0.774).
- External-standard accountability outperforms determination-against-explicit-criteria by held-out regression R2 (0.781 vs 0.772).
- GPT-4.1-mini blind-rating status: `blocked`.
- Blind-rating benchmark metrics were not computed because rating status was `blocked`: OPENAI_API_KEY is not set in the local shell, so GPT-4.1-mini blind ratings were not run.

## Inferred

Vocabulary evidence alone should be treated as weak evidence because exact-word features are sparse and role-instruction wording can miss conceptual content. The stronger test is the corrected blind-rating benchmark, which requires GPT-4.1-mini ratings and the shared held-out evaluation path.

## Speculative

If blind ratings later show the external-standard-accountability dimension outperforming the orderliness and determination vocabularies and approaching prior compact-feature benchmarks, that would support elevating the PC1 interpretation. If they do not, the PC1 wording should remain provisional or be revised.

## Prior Benchmark Context

| Feature family | PC1 R2 | PC2 R2 | PC3 R2 | Mean R2 |
|---|---:|---:|---:|---:|
| semantic_baseline | 0.517 | 0.181 | 0.336 | 0.389 |
| codex_trait_replication |  |  |  | 0.398 |
| codex_retained_procedural_behavioral | 0.631 | 0.257 | 0.422 | 0.490 |
| claude_bigfive_style | 0.734 | 0.480 | 0.416 | 0.613 |
| hierarchical_trait_plus_procedural |  |  |  | 0.622 |
| residual_manifold_hand_feature |  |  |  | 0.632 |
| semantic_bigfive_svd15_prompt_register |  |  |  | 0.707 |
| gpt41mini_blind_pc_interpretation_ratings |  |  |  | blocked |

## Limitations

- Part A exact-vocabulary counts are transparent but sparse.
- Cluster-controlled correlations are residualized against Qwen cluster labels and text length; they are diagnostic, not causal.
- The blind-rating component requires local OpenAI API credentials. This run did not fabricate missing ratings.
- The corrected PC2 blind-rating direction is higher integration score -> more negative PC2.
