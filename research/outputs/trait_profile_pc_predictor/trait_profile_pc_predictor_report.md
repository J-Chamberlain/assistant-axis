# Trait-profile -> persona-PC predictor: held-out generalization and counterfactual projection

Generated: 2026-09-11T18:31:44Z

## Central question and answer

**Observed.** Given a complete activation-derived Qwen trait profile, a leakage-safe Ridge model predicts canonical Qwen persona PC1/PC2/PC3 accurately for personas excluded from fitting. The result is a reusable same-space mapping, not independent psychological validation.

Raw-cosine LOPO R2 is 0.999522/0.998811/0.999611 for PC1/PC2/PC3; normalized 3D RMSE is 0.045378. Fold-safe quantile LOPO R2 is 0.997556/0.988048/0.989209; normalized 3D RMSE is 0.159028.

## Epistemic framing

- **Observed:** metrics, coordinates, errors, neighbors, distances, and counterfactual point estimates computed from existing Qwen role/trait activation-vector artifacts and canonical PCA targets.
- **Interpretation:** held-out accuracy within the existing persona inventory, harder cluster-family transfer, and local synthetic/profile interpolation under this same-space mapping.
- **Hypothesis:** performance on genuinely new behaviorally elicited personas, other models, frontier models, or humans. None was tested here.

The scientific statement is: **Given an activation-derived trait profile, how accurately can canonical persona PCA location be predicted?** It is not a claim that psychological traits independently cause PCA position.

## Data integrity and provenance

All 275 personas and 240 traits are unique, finite, and exactly aligned across the matrix, geometry, and cluster table. No coordinate, cluster, role, or persona metadata column appears among features. Matrix reproduction from source vectors had max absolute error 5.551e-16.

Source persona/trait activations: Qwen/Qwen3-32B released/local role and trait tensors. Trait profiles: 240 activation-space cosines (or a fold-local empirical quantile transform). Targets: canonical Qwen role PCA coordinates from `geometry_viz_data.json`. Both X and Y share role-vector provenance, so near-ceiling accuracy can reflect geometric basis coverage.

New model inference: none. GPU: none. RunPod: none. External model API calls: none.

## Validation design

- Nested model comparison: 5 outer folds repeated over 10 deterministic seeds; 4-fold inner tuning. Quantile transformation, scaling, and all hyperparameter selection occur inside training folds.
- LOPO: each persona removed completely; Ridge alpha chosen by 4-fold CV on the remaining 274; fold-local OOD PCA and training-only nearest profiles.
- Leave-one-cluster-out: each canonical cluster removed completely; all four model families evaluated with training-only tuning.
- Permutation: 100 deterministic joint target-row permutations through nested 5x4 Ridge validation.

## Nested model comparison

| Representation | Model | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE |
|---|---|---:|---:|---:|---:|
| raw cosine | ridge | 0.999465 | 0.998718 | 0.999567 | 0.047591 |
| raw cosine | pls | 0.999412 | 0.998579 | 0.999383 | 0.051386 |
| raw cosine | kernel_ridge | 0.999007 | 0.997325 | 0.998562 | 0.071954 |
| raw cosine | knn | 0.964476 | 0.936286 | 0.932079 | 0.410986 |
| fold-safe quantile | ridge | 0.997233 | 0.986419 | 0.988478 | 0.168139 |
| fold-safe quantile | pls | 0.996576 | 0.985693 | 0.987075 | 0.176304 |
| fold-safe quantile | kernel_ridge | 0.997813 | 0.993149 | 0.994666 | 0.120828 |
| fold-safe quantile | knn | 0.962978 | 0.931747 | 0.933128 | 0.417413 |

**Model decision:** Ridge remains V1 because no challenger cleared the predeclared material-improvement rule without a harder-holdout penalty. The selected canonical V1 model is `ridge` with raw-cosine input. Best challenger reduction versus Ridge was 0.00% under ordinary nested CV; the predeclared threshold was 10%.

## Direct decision questions

**Q1 — held-out existing personas. Observed:** Yes. Raw Ridge LOPO R2 is 0.999522, 0.998811, and 0.999611; RMSE is 0.6567, 0.7406, and 0.3108.

**Q2 — LOPO versus prior five-fold. Observed:** Prior R2 was 0.999415/0.998730/0.999603. LOPO changes are +0.000107/+0.000081/+0.000007. This is not a large degradation.

**Q3 — quantile profiles. Observed:** Fold-safe quantiles preserve strong information: LOPO normalized 3D RMSE 0.159028 versus 0.045378 raw. The CLI therefore supports percentile input/editing via the all-corpus final empirical reference, while the production predictor remains raw-cosine Ridge.

**Q4 — nonlinear/latent/local alternatives. Observed:** Best ordinary nested-CV model was `ridge`; its normalized-RMSE reduction versus Ridge was 0.00%. It did not justify replacing Ridge under the predeclared rule.

**Q5 — cluster shift. Observed:** Ridge aggregate leave-cluster-out normalized 3D RMSE is 0.067997, 1.68x the mean LOPO error. Individual cluster errors are below.

| Cluster | n | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE | vs LOPO mean |
|---|---:|---:|---:|---:|---:|---:|
| combative_iconoclast | 15 | 0.9958 | 0.9968 | 0.9960 | 0.0611 | 1.24x |
| editorial | 13 | 0.9348 | 0.9414 | 0.9977 | 0.1062 | 1.12x |
| grounded_social | 54 | 0.9982 | 0.9972 | 0.9994 | 0.0493 | 1.27x |
| mythic_spiritual | 51 | 0.9948 | 0.9795 | 0.9991 | 0.0842 | 2.02x |
| other | 6 | 0.9768 | 0.9956 | 0.9963 | 0.0899 | 1.34x |
| procedural_professional | 126 | 0.9924 | 0.9937 | 0.9993 | 0.0616 | 2.03x |
| trickster_chaos | 10 | 0.9947 | 0.9964 | 0.9968 | 0.0698 | 1.37x |

**Q6 — manifold distance. Observed:** LOPO normalized error versus fold-local 5-NN profile distance has Pearson r=0.2431 and Spearman rho=0.2627. This is association, not calibrated uncertainty.

**Q7 — modified profiles. Observed:** The deterministic four-anchor sweep labels 0 of 4 profiles edge/OOD at 10 percentile points per edited trait, 1 at 20 points, 1 at 30 points, and 2 at an attempted 100 points (with percentile clamping reported). These labels combine retained-space distance and discarded-space reconstruction residual; they remain heuristic and direction/anchor-specific.

**Q8 — synthetic activation interpolation. Observed:** Run after strict PCA reproduction (max error 1.207e-06). Across 120 mixes whose two endpoints were excluded from fitting, PC R2 was 0.995266/0.984377/0.997144 and normalized 3D RMSE was 0.149728. These are synthetic activation-space interpolations, not elicited personas.

**Q9 — canonical V1. Interpretation:** `ridge` on the raw-cosine profile is V1 because it is transparent, near-ceiling on ordinary held-out personas, explicitly tested under LOPO and cluster shift, and no alternative cleared the material-improvement rule.

## Permutation control

Across 100 permutations, mean per-PC R2 was -0.0244, the 95th percentile was -0.0075, and mean normalized 3D RMSE was 1.7614. The observed Ridge result is far outside this null; no leakage anomaly was detected.

## OOD diagnostic and empirical error reference

Profiles are standardized on training data, projected into 5 PCA components explaining 0.9625 of profile variance, and compared by nearest/mean-5-neighbor distance plus PCA reconstruction residual. Labels use >90th percentile on either diagnostic as edge and >99th (or >=5 out-of-range traits) as OOD. They are heuristic geometric diagnostics, not probabilities.

Each CLI prediction includes the primary point estimate, nearest personas, OOD context, model-family disagreement, and a per-PC empirical LOPO error reference (median, q90, q95 absolute error). The q95 band is not a confidence or credible interval.

## Counterfactual interface

The saved examples use trickster, actor, therapist, and spy, all verified in canonical geometry. Their modified coordinates are labeled **PREDICTED COUNTERFACTUAL LOCATION**. Example:

```bash
.venv/bin/python research/outputs/trait_profile_pc_predictor/predict_trait_profile.py \
  --persona therapist \
  --delta-percentile empathetic=10,agreeable=10,reactive=-10
```

External profiles must provide all 240 unique named traits as raw cosines or percentiles; missing, duplicate, extra, and nonfinite traits are rejected.

## Leakage and provenance audit

- PCA targets and trait cosines share the same Qwen role vectors; this is explicit shared provenance, not software target leakage.
- Role identity, PC coordinates, and cluster labels do not enter X. Cluster labels only construct holdouts.
- StandardScaler and QuantileTransformer live inside the estimator pipeline fitted separately in every inner/outer training partition.
- Hyperparameters are chosen only on outer-training data; each LOPO persona and each omitted cluster is absent from fitting and tuning.
- OOD StandardScaler/PCA is fit only on training profiles for LOPO diagnostics. The final all-corpus reference is used only for deployed-profile context.
- The clean 100-permutation null argues against accidental target-column or outer-test leakage.

## Observed findings

- Complete activation-derived profiles predict held-out canonical persona coordinates with near-ceiling accuracy.
- Fold-safe quantile profiles retain strong predictive information, enabling an intuitive percentile-edit layer.
- Withholding whole persona families is harder and yields cluster-specific bias/error that ordinary random/LOPO validation understates.
- The permutation control is near chance and the source matrix exactly reproduces from the released tensors.

## Interpretations

- The 240-trait bank provides broad basis coverage of the existing Qwen role-vector manifold.
- Counterfactual profile edits can be mapped reproducibly within this learned relationship; proximity diagnostics indicate how much corpus support surrounds a prediction.
- Harder cluster and synthetic endpoint holdouts are better evidence for interpolation/generalization inside the artifact family than ordinary random folds alone.

## Hypotheses and unresolved questions

- Whether a newly behaviorally elicited Qwen persona will occupy its predicted coordinate remains untested and is the next scientific experiment.
- Transfer to Llama, Gemma, frontier models, or humans is untested.
- Trait edits are not causal interventions; correlated feature geometry can make coefficient-level stories unstable.
- OOD labels and empirical error bands are descriptive references, not formal predictive coverage guarantees.
