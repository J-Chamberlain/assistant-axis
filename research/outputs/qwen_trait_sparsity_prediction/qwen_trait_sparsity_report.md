# Qwen trait sparsity and basis-coverage audit

Generated: 2026-09-11T22:20:55Z

## Central answer

**Observed.** Persona PCA is fit to 275 mean-pooled Qwen role vectors using their 5,120 activation coordinates as variables. The 240 named traits are not PCA inputs. However, the PC targets and trait-cosine predictors are algebraically dependent because both are projections of the same role activation vectors.

The exact canonical 240-trait LOPO baseline reproduced at PC1/PC2/PC3 R2=0.999522/0.998811/0.999611 and normalized 3D RMSE=0.045378. The fixed editorial 15 reaches repeated-nested R2=0.9925/0.9881/0.9922, normalized RMSE=0.1651; nested-selected 15 reaches 0.9984/0.9968/0.9973, normalized RMSE=0.0872.

**Interpretation.** The matched controls favor **mixture**: Optimized real traits have a large compact-k advantage, while a sufficiently large generic basis also approaches the full-bank reconstruction.

## What PCA uses—and the exact dependence

The canonical geometry builder mean-pools each saved role tensor and runs PCA directly on the resulting 275 × 5,120 role-vector matrix. The observations are personas; the variables are activation coordinates. Trait tensors are loaded separately and do not enter the role PCA fit.

For role vector `v_i`, unit trait direction `t_j`, role mean `mu`, and unit PC loading `p_c`, the predictor is `x_ij = (v_i / ||v_i||) dot t_j`, whereas the target is `y_ic = (v_i - mu) dot p_c`. This is not direct target-column leakage, but it is same-vector algebraic dependence. The separate `pca_trait_dependency_audit.md` records source-code and numerical reproduction evidence.

## Epistemic labels

- **Observed:** held-out metrics, random-basis distributions, PC span coverage, role norms, selection frequencies, conditional permutation degradation, sparse nonzero frequencies, and trait correlations.
- **Interpretation:** what matched generic directions imply about semantic alignment versus generic basis coverage.
- **Hypothesis:** the labels form a causal psychology, correspond to humans, or determine behavior. None was tested.

## Validation design

The primary compact analysis uses 5-fold outer CV repeated over deterministic seeds 42-51. Inside each outer training set, a 4-fold greedy search evaluates every remaining trait and every Ridge alpha. Each inner training fold learns its own feature means/scales and target means/scales. The joint objective is:

`sqrt((1 / N_validation) * sum_i sum_c ((y_ic - yhat_ic) / s_c,inner-train)^2)`.

No outer-test row influences feature ranking, selection, scaling, target scaling, alpha choice, or stopping. Isotropic directions are generated without PC information. Persona-span directions are regenerated inside each outer fold from centered training role vectors only; held-out role vectors and all PC target values are absent from direction construction.

## Direct performance comparison

| Model | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE |
|---|---:|---:|---:|---:|
| Full 240, canonical LOPO | 0.999522 | 0.998811 | 0.999611 | 0.045378 |
| Fixed editorial 15, nested 5x10 | 0.992546 | 0.988133 | 0.992210 | 0.165056 |
| Nested-selected 15 | 0.998360 | 0.996759 | 0.997313 | 0.087216 |
| Nested-selected 10 | 0.997735 | 0.995723 | 0.995167 | 0.106880 |
| Nested-selected 5 | 0.994195 | 0.988555 | 0.986232 | 0.176511 |

The fixed 15 are unchanged: creative, abstract, curious; reactive, adaptable, practical; skeptical, analytical, conscientious; rebellious, competitive, manipulative; empathetic, agreeable, altruistic.

## How few traits?

Smallest evaluated held-out-selected k with all-PC R2 >= .90/.95/.98/.99: 3/3/4/6.
Smallest k with normalized 3D RMSE <= .25/.15/.10: 4/6/12. The <=2x-full threshold is 0.090755, reached at k=14.

## Matched basis controls

Each entry below is repeated held-out Ridge performance. Random columns are medians over deterministic banks; lower normalized RMSE is better. The real-trait 240 row is necessarily the full bank. Fixed editorial 15 appears only at k=15.

| k | optimized real | random real | isotropic 5,120-D | train-persona span | fixed editorial | beats isotropic | beats persona-span |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0.1765 | 0.4791 | 1.2042 | 0.6177 | — | 1.0000 | 1.0000 |
| 10 | 0.1069 | 0.2376 | 0.9069 | 0.2765 | — | 1.0000 | 1.0000 |
| 15 | 0.0872 | 0.1533 | 0.7379 | 0.1702 | 0.1651 | 1.0000 | 1.0000 |
| 30 | 0.0705 | 0.0916 | 0.4724 | 0.0853 | — | 1.0000 | 1.0000 |
| 60 | 0.0573 | 0.0660 | 0.3048 | 0.0610 | — | 1.0000 | 1.0000 |
| 240 | 0.0476 | 0.0476 | 0.1245 | 0.0514 | — | 1.0000 | 1.0000 |

At k=15, optimized-real / median-isotropic normalized-RMSE ratio is 0.118; optimized-real / median-persona-span ratio is 0.512. These are predictive effect sizes, not psychological effect sizes.

Random subsets of real traits test whether deliberate selection helps within the named bank. Isotropic random directions test a generic coordinate system in the ambient 5,120-D activation space. Fold-local persona-span directions are the stronger generic control because every direction is guaranteed to lie in the training-persona variation span.

## Direct span coverage and role norms

The full 240-trait vector span contains squared fractions 0.987955, 0.985303, and 0.981947 of the canonical PC1, PC2, and PC3 loading directions. Coverage for the fixed 15 and descriptive target-selected 5/10/15/30 sets is saved in `trait_span_pc_coverage.csv`; target-selected coverage is not held-out evidence.

Role-vector L2 norms have mean 282.0390, population SD 8.0486, CV 0.0285, and range 252.1012–299.3078. Norm correlations (Pearson/Spearman) are PC1 0.582/0.634, PC2 -0.683/-0.618, and PC3 -0.107/0.023. This quantifies how far cosine features depart from ordinary unnormalized linear projections.

## Robust predictive traits

A trait is called robustly predictive only when at least three complementary criteria support it, including repeated selection by the 15-feature nested paths. Marginal association alone is not enough.

| Trait | synthesis rank | joint marginal rank | conditional rank | forward freq @15 | sparse freq |
|---|---:|---:|---:|---:|---:|
| ethereal | 1 | 1 | 2 | 0.60 | 1.00 |
| cryptic | 2 | 3 | 48 | 0.50 | 1.00 |
| serene | 3 | 22 | 43 | 0.52 | 0.94 |
| structuralist | 4 | 8 | 193 | 0.92 | 1.00 |
| fatalistic | 5 | 5 | 175 | 0.38 | 1.00 |
| poetic | 27 | 11 | 4 | 0.22 | 0.00 |

## PC-specific compact bases

- **PC1:** transparent (100%), narrative (58%), temperamental (54%), secular (52%), charismatic (46%), zealous (44%), poetic (42%), fatalistic (40%), factual (38%), urgent (34%)
- **PC2:** introverted (100%), epicurean (76%), ritualistic (76%), creative (64%), bombastic (50%), chaotic (46%), witty (44%), anthropocentric (40%), regulatory (34%), systems_thinker (32%)
- **PC3:** benevolent (70%), introverted (62%), cynical (62%), nurturing (54%), historical (50%), closure_seeking (46%), divergent (44%), erudite (44%), decisive (36%), humanistic (28%)

The overlap and divergence of these rankings indicate whether one joint compact basis serves all axes or each PC benefits from distinct trait directions. Full PC-specific curves and rankings are saved separately.

## Target-permutation control


Across 20 deterministic joint target permutations, the maximum budget-specific p95 mean-PC R2 was -0.0017. The null behaves as expected.

## Redundancy and interchangeability

There are 2178 trait pairs with absolute Pearson correlation >=0.90 across the 275 personas; 738 meet >=0.95. Complete-linkage groups enforce the chosen within-group absolute-correlation threshold, limiting chain-merger artifacts.

Conditional permutation can assign weak importance to a genuinely useful direction when correlated substitutes let the full Ridge model compensate. Conversely, a greedy winner inside a redundancy group should be read as a representative of that family, not a uniquely privileged trait.

## Sparse-model robustness

The independently tuned MultiTaskElasticNet repeated-CV check reached normalized 3D RMSE 0.0811. Its nonzero-selection frequencies are included in the synthesis table. Instability is reported directly rather than converted into a definitive sparse ontology.

## Interpretation

**Interpretation.** The overall result favors **mixture**. Optimized real traits have a large compact-k advantage, while a sufficiently large generic basis also approaches the full-bank reconstruction.

This same-space audit should be contrasted with coordinate-blind role-instruction ratings already present in the repository. Those ratings do not receive activation vectors or PCA coordinates and are therefore more independent semantic evidence even when their R2 is much lower. This study does not recompute them.

## Hypotheses and unresolved questions

- Whether compact selected traits predict a genuinely new behaviorally elicited Qwen persona remains untested.
- Trait labels may describe activation directions without constituting causal or independently validated psychological dimensions.
- Winner identity within highly correlated groups may change under new persona inventories or extraction procedures.
- A random direction can predict a PC because it samples the same activation manifold; that does not give the direction semantic content.
- No Llama or Gemma analysis was run in this study.

## Compute and provenance boundary

This study used only saved Qwen artifacts and CPU statistical computation. It used no GPU, RunPod, model inference, activation extraction, response generation, or external model API.
