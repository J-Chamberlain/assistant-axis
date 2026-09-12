# AA-7 — Human-supported trait convergence and cross-model aligned-subspace study

## Primary convergence answer

Preregistered evidence classification: **WEAK / ABSENT**.

The frozen 12 do **not** form an unusually efficient compact coordinate system under the primary matched test: they beat neither the random-real k=12 null in any model/scope nor the fold-local persona-span null beyond the Qwen and Gemma core-only comparisons. They do beat the isotropic ambient baseline in all six model/scope comparisons. Thus AA-7 finds weak/absent evidence that human psychometric support itself identifies geometrically privileged compact traits, even though the model-derived directions recur strongly after cross-model subspace alignment.

The table below is the primary fixed-split matched comparison. Aggregate nRMSE is fold-standardized Euclidean geometric error, so lower is better. Empirical p-values are one-sided against 500 target-independent matched banks.

| Model | Scope | Human 12 mean R² | Human 12 nRMSE | random median | random percentile | p vs random | persona-span median | span percentile | p vs span | optimized 12 nRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3-32B | core | 0.9906 | 0.1679 | 0.1917 | 76.2 | 0.2395 | 0.2150 | 98.0 | 0.0220 | 0.1042 |
| Qwen/Qwen3-32B | extended | 0.9076 | 0.7455 | 0.8112 | 74.0 | 0.2615 | 0.7835 | 73.6 | 0.2655 | 0.4506 |
| Llama-3.3-70B | core | 0.9158 | 0.5086 | 0.4553 | 26.0 | 0.7405 | 0.4439 | 11.2 | 0.8882 | 0.2943 |
| Llama-3.3-70B | extended | 0.7801 | 1.1610 | 1.2014 | 64.8 | 0.3533 | 1.0688 | 6.8 | 0.9321 | 0.8633 |
| Gemma-2-27B | core | 0.9464 | 0.4003 | 0.4620 | 85.2 | 0.1497 | 0.4760 | 97.4 | 0.0279 | 0.3105 |
| Gemma-2-27B | extended | 0.8192 | 1.0478 | 1.1714 | 87.6 | 0.1257 | 1.0215 | 33.0 | 0.6707 | 0.7006 |

Percentile is the percentage of null banks with error at least as large as the human-supported error; higher is better. Across the six comparisons, the frozen set passes 0/6 random-real tests, 2/6 persona-span tests (Qwen and Gemma core only), and 6/6 isotropic tests at p≤0.05.

## Absolute feature-family context

The next table reports held-out mean per-PC R² and aggregate nRMSE. Random/generic entries are distribution medians and therefore have no single R² in this compact summary.

| Model | Scope | human 12 R² / nRMSE | optimized 12 R² / nRMSE | random 12 median | span 12 median | isotropic 12 median | Big Five 5 R² / nRMSE | direct 45 R² / nRMSE | full 240 R² / nRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3-32B | core | 0.991 / 0.168 | 0.996 / 0.104 | 0.192 | 0.215 | 0.822 | 0.745 / 0.874 | 0.998 / 0.079 | 0.999 / 0.047 |
| Qwen/Qwen3-32B | extended | 0.908 / 0.745 | 0.967 / 0.451 | 0.811 | 0.784 | 1.552 | 0.538 / 1.677 | 0.990 / 0.249 | 0.998 / 0.116 |
| Llama-3.3-70B | core | 0.916 / 0.509 | 0.972 / 0.294 | 0.455 | 0.444 | 1.121 | 0.671 / 1.002 | 0.984 / 0.222 | 0.993 / 0.147 |
| Llama-3.3-70B | extended | 0.780 / 1.161 | 0.880 / 0.863 | 1.201 | 1.069 | 1.847 | 0.491 / 1.768 | 0.934 / 0.643 | 0.982 / 0.338 |
| Gemma-2-27B | core | 0.946 / 0.400 | 0.968 / 0.311 | 0.462 | 0.476 | 1.068 | 0.702 / 0.947 | 0.978 / 0.255 | 0.994 / 0.138 |
| Gemma-2-27B | extended | 0.819 / 1.048 | 0.920 / 0.701 | 1.171 | 1.022 | 1.785 | 0.496 / 1.759 | 0.956 / 0.519 | 0.991 / 0.238 |

Geometry-optimized 12-trait sets outperform the frozen 12 in every model/scope. The 45 direct semantic features recover substantially more geometry, and the full 240-feature basis is best. PC4–PC6 are materially harder for the frozen set than PC1–PC3; all per-PC R², RMSE, nRMSE, and MAE values are in `local_pc_prediction_per_pc.csv` and matched-control per-PC distributions are in the three control CSVs.

Big Five uses five features and is not treated as an equal-budget comparison with 12 features. At k=5 in PC1–PC6, its nRMSE is 1.677/1.768/1.759 for Qwen/Llama/Gemma, versus random-real medians 1.537/1.754/1.747 and optimized-real values 1.235/1.535/1.377. It is compact but does not beat matched random-real k=5 on this coverage metric.

## Individual traits and human-support level

- Qwen/Qwen3-32B: pessimistic–PC3 (r=0.913), manipulative–PC1 (r=-0.881), optimistic–PC3 (r=-0.864).
- Llama-3.3-70B: impulsive–PC2 (r=0.971), grandiose–PC1 (r=-0.929), manipulative–PC2 (r=0.928).
- Gemma-2-27B: grandiose–PC1 (r=-0.937), adventurous–PC1 (r=-0.782), altruistic–PC2 (r=-0.746).

- Qwen/Qwen3-32B AA-1 support versus extended geometric utility: Spearman rho=0.028; high mean=0.160, moderate mean=0.155. N=12; descriptive only.
- Llama-3.3-70B AA-1 support versus extended geometric utility: Spearman rho=0.195; high mean=0.140, moderate mean=0.137. N=12; descriptive only.
- Gemma-2-27B AA-1 support versus extended geometric utility: Spearman rho=0.195; high mean=0.144, moderate mean=0.125. N=12; descriptive only.

- Qwen/Qwen3-32B largest leave-one-trait-out degradations: pessimistic (ΔnRMSE=0.393), optimistic (ΔnRMSE=0.259), judgmental (ΔnRMSE=0.202). Leaders differ by model, so performance is not reducible to one universal trait.
- Llama-3.3-70B largest leave-one-trait-out degradations: grandiose (ΔnRMSE=0.160), judgmental (ΔnRMSE=0.142), optimistic (ΔnRMSE=0.103). Leaders differ by model, so performance is not reducible to one universal trait.
- Gemma-2-27B largest leave-one-trait-out degradations: impulsive (ΔnRMSE=0.184), grandiose (ΔnRMSE=0.179), optimistic (ΔnRMSE=0.159). Leaders differ by model, so performance is not reducible to one universal trait.

- Qwen/Qwen3-32B AA-1 support category versus extended utility across all 45 direct traits: Spearman rho=-0.211, Kruskal p=0.358.
- Llama-3.3-70B AA-1 support category versus extended utility across all 45 direct traits: Spearman rho=-0.165, Kruskal p=0.573.
- Gemma-2-27B AA-1 support category versus extended utility across all 45 direct traits: Spearman rho=-0.269, Kruskal p=0.246.

## Phase 2 — held-out role-score subspace alignment

Primary alignment uses centered raw model-local PC scores; variance-standardized alignment is a declared sensitivity. Values below average the ten repeated role-held-out folds for PC1–PC6. Raw RMSE is not comparable across pairs because saved activation magnitudes differ sharply by architecture; correlations and the standardized sensitivity are the scale-robust diagnostics.

| Pair | coordinate r | distance r | geometric RMSE | NN Jaccard@10 | permutation p (coordinate r) | standardized coordinate r / RMSE |
|---|---:|---:|---:|---:|---:|---:|
| llama_to_qwen | 0.879 | 0.858 | 42.265 | 0.339 | 0.0010 | 0.883 / 1.211 |
| gemma_to_qwen | 0.809 | 0.904 | 751.750 | 0.307 | 0.0010 | 0.811 / 1.539 |
| gemma_to_llama | 0.908 | 0.933 | 789.662 | 0.363 | 0.0010 | 0.913 / 1.044 |

Human-supported recurrence: 11 high, 1 moderate, 0 weak/model-specific.
Big Five recurrence: 5 high, 0 moderate, 0 weak/model-specific.

## Focal Agreeableness result

Preregistered decision: **RECONCILED**. Aligned pairwise cosines are Qwen–Llama 0.900, Qwen–Gemma 0.952, and Llama–Gemma 0.938. The full local and aligned six-dimensional vectors and squared-cosine consensus fractions are in `aligned_agreeableness_focal_test.json`.
The consensus contains 0.948 of Qwen, 0.939 of Llama, and 0.973 of Gemma Agreeableness direction (squared cosine). Alignment therefore reconciles the previously different local-PC assignments within this model-only six-dimensional role-score space.

## Core versus secondary coordinates

- human_supported_12: mean aligned direction cosine change from PC1–PC3 to PC1–PC6 = 0.233; preregistered material-improvement flag = True.
- externally_anchored_big_five_5: mean aligned direction cosine change from PC1–PC3 to PC1–PC6 = 0.184; preregistered material-improvement flag = True.
- agreeableness_focal: mean aligned direction cosine change from PC1–PC3 to PC1–PC6 = 0.108; preregistered material-improvement flag = True.

## Big Five versus the frozen 12

The Big Five role-score span captures 0.388/0.379/0.379 of the human-supported 12 span in Qwen/Llama/Gemma, whereas the human-supported span captures 0.932/0.908/0.909 of the Big Five span. The 17-feature union remains full rank and improves held-out PC1–PC6 nRMSE over the human 12 from 0.745→0.540, 1.161→0.912, and 1.048→0.795. The 12 are therefore broader than Big Five, although they contain most—not all—Big Five role-score structure. `feature_family_subspace_coverage.csv` reports held-out coverage, numerical rank, condition number, redundancy, and error reductions.

## Observed

All numerical statements above are measurements on existing model role vectors, model trait directions, and model-local role-score coordinates. The random-real and generic controls are matched and target-independent; persona-span directions are constructed inside each outer training fold.

## Interpretation

AA-7 provides weak/absent evidence for the primary claim that human psychometric defensibility selects unusually efficient compact model coordinates: the human-supported 12 behave like ordinary real-trait subsets. It provides strong, separate evidence that once projected into held-out-alignable model-local PC1–PC6 role-score subspaces, the corresponding activation-derived human-supported and Big Five directions recur across Qwen, Llama, and Gemma. This aligned recurrence is cross-model, broader than Big Five, and not Qwen-specific—but it is model-only representational convergence, not human/model equivalence.

## Hypotheses

Cross-model recurrence after rotation is consistent with shared organization over the 275 role labels. It does not identify a causal latent mechanism, and shared role prompts remain a possible common source of structure.

## Unknown

Independent expert review may further contract the AA-1 bridge. Behavioral realization, causal control, respondent-level transfer, and generalization beyond the three saved-vector releases remain unknown.

## Later human-respondent study gate

AA-7 does not satisfy the preregistered gate for designing a human-respondent projection study.

## Scientific boundary

The 12-trait set was frozen from prior human-data evidence before AA-7 geometry analysis. No human respondent or human occupational centroid was projected into model geometry. No respondent-level human microdata were committed. No GPU, RunPod, model inference, activation extraction, response generation, external model API, or human outcome prediction was used.
