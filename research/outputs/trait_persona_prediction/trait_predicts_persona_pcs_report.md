# Trait Geometry Prediction of Persona PCA Axes

## Data Sources

- Geometry data: `research/visualizations/geometry_viz_data.json`
- Persona vectors: `downloads/hf_vectors/qwen-3-32b/role_vectors`
- Trait vectors: `downloads/hf_vectors/qwen-3-32b/trait_vectors`
- Vector use: raw activation-space cosine between mean-pooled Qwen role vectors and mean-pooled Qwen trait vectors.
- Model/layer: Qwen/Qwen3-32B, layer 48.
- Tensor examples: role (64, 5120); trait (64, 5120).
- Counts: 275 personas, 240 traits.

## Validation Method

The predictor matrix is persona-by-trait cosine similarity in Qwen activation space. Targets are the PCA coordinates embedded in `geometry_viz_data.json`. Each PC was evaluated with 5-fold cross-validation, an 80/20 held-out split, and a 30-permutation ridge baseline. Ridge and elastic net are linear models over standardized trait-cosine features; the optional random forest comparison was skipped to keep this repo-local validation bounded.

## Predictive Performance

| PC | Ridge 5-fold | Ridge held-out | Elastic net 5-fold | Optional nonlinear comparison | Permutation mean R2 / p95 |
|---|---|---|---|---|---|
| PC1 | R2=0.999, Pearson=1.000, Spearman=0.999, RMSE=0.726 | R2=0.999, Pearson=1.000, Spearman=0.999, RMSE=0.735 | R2=0.999, Pearson=0.999, Spearman=0.999, RMSE=0.973 | not run; skipped to keep this repo-local validation bounded | -0.027 / 0.003 |
| PC2 | R2=0.999, Pearson=0.999, Spearman=0.999, RMSE=0.765 | R2=0.998, Pearson=0.999, Spearman=0.998, RMSE=0.969 | R2=0.997, Pearson=0.999, Spearman=0.998, RMSE=1.085 | not run; skipped to keep this repo-local validation bounded | -0.030 / -0.010 |
| PC3 | R2=1.000, Pearson=1.000, Spearman=1.000, RMSE=0.314 | R2=0.999, Pearson=1.000, Spearman=0.999, RMSE=0.387 | R2=0.999, Pearson=0.999, Spearman=0.999, RMSE=0.549 | not run; skipped to keep this repo-local validation bounded | -0.029 / 0.000 |

## Top Ridge Trait Predictors

### PC1

Positive coefficients:
- conscientious: 11.9844
- emotional: 11.0897
- risk_taking: 10.3712
- strategic: 10.2901
- temperamental: 10.2008
- confrontational: 10.0738
- poetic: 9.9845
- interdisciplinary: 9.7294
- ironic: 9.5449
- absolutist: 8.7914
- artistic: 8.6917
- calm: 8.4492

Negative coefficients:
- closure_seeking: -19.6587
- ethereal: -15.8210
- charismatic: -11.6196
- contrarian: -10.4385
- dispassionate: -10.0008
- edgy: -8.9982
- rationalist: -8.7415
- deferential: -8.7146
- eclectic: -8.3985
- nurturing: -8.2918
- metaphorical: -8.0174
- generalist: -7.8259

### PC2

Positive coefficients:
- closure_seeking: 13.2656
- animated: 9.4018
- subversive: 9.1952
- specialized: 7.8458
- poetic: 7.0749
- patient: 6.9528
- deferential: 6.7994
- experiential: 6.5659
- generalist: 6.4862
- grounded: 6.1641
- concise: 5.8626
- open_ended: 5.7865

Negative coefficients:
- ethereal: -10.0587
- traditional: -8.3854
- confrontational: -7.6953
- flippant: -7.4101
- risk_taking: -7.1731
- irreverent: -6.8304
- romantic: -6.6454
- decisive: -6.6391
- cynical: -6.5029
- adaptable: -6.4941
- critical: -6.4492
- resilient: -6.3725

### PC3

Positive coefficients:
- open_ended: 6.1733
- animated: 5.8991
- rationalist: 5.3127
- sycophantic: 5.2914
- reactive: 4.8140
- closure_seeking: 4.6613
- temperamental: 4.6121
- supportive: 4.1406
- ethereal: 4.1309
- mercurial: 4.1158
- concise: 4.0372
- technical: 3.9894

Negative coefficients:
- romantic: -5.7672
- impulsive: -5.7099
- cautious: -5.6927
- hostile: -5.5456
- effusive: -5.2992
- absolutist: -5.2613
- eclectic: -5.1052
- melancholic: -4.9418
- pensive: -4.8637
- theoretical: -4.7438
- efficient: -4.7228
- calm: -4.6746

## PC3 Perturbation/Stabilization Versus Moral-Valence Trait Test

- Perturbation/stabilization trait subset: R2=0.995, Pearson=0.998, Spearman=0.998, RMSE=1.082
- Moral-valence trait subset: R2=0.992, Pearson=0.996, Spearman=0.996, RMSE=1.382
- Perturbation/stabilization traits used: hostile, manipulative, competitive, subversive, iconoclastic, deconstructionist, contrarian, irreverent, sarcastic, dominant, calculating, strategic, nurturing, conciliatory, empathetic, forgiving, diplomatic, calm, cautious, regulatory, humanistic
- Moral-valence traits used: principled, deontological, humanistic, generous, forgiving, empathetic, nurturing, callous, hostile, manipulative, petty, misanthropic, nihilistic

The subset test is limited because trait labels are hand-selected and partially overlapping. It is diagnostic, not a causal decomposition.

## Interpretation

Trait-vector geometry strongly predicts persona PCA coordinates from raw Qwen activation-space cosine profiles. This supports the layered Paper 1.5 interpretation: persona location is not only role semantics or cluster membership; trait structure carries substantial information about where a persona lands in PCA space. The near-ceiling performance should be interpreted cautiously because 240 trait vectors in the same activation space can function as a high-dimensional basis for reconstructing persona PCA coordinates.

PC1 is strongly predicted, but its coefficient profile is not a simple Big Five-style conscientiousness story. Positive coefficients include conscientious, emotional, risk_taking, strategic, temperamental, confrontational, poetic, interdisciplinary, ironic, absolutist, artistic, and calm; negative coefficients include closure_seeking, ethereal, charismatic, contrarian, dispassionate, edgy, rationalist, deferential, eclectic, nurturing, metaphorical, and generalist. This suggests PC1 is recoverable from trait geometry, but the coefficient basis is correlated and should not be read as a clean one-trait axis.

PC2 is also predicted well, with a mixed coefficient profile. Positive coefficients include closure_seeking, animated, subversive, specialized, poetic, patient, deferential, experiential, generalist, grounded, concise, and open_ended; negative coefficients include ethereal, traditional, confrontational, flippant, risk_taking, irreverent, romantic, decisive, cynical, adaptable, critical, and resilient. This remains consistent with the current view that PC2 is compound and should not be reduced to one verbal label.

PC3 is predicted substantially. The full-model coefficient signs are not a direct readable perturbation/stabilization list, but the targeted subset test shows perturbation/stabilization traits predict PC3 slightly better than moral-valence traits. This supports the current PC3 interpretation as perturbation/intervention versus stabilization/care, while leaving room for coefficient-basis instability and correlated-feature effects.

## Limitations

- Trait vectors and persona vectors are both derived from Lu-style elicitation artifacts; this test does not prove independent psychological ontology.
- The predictor matrix has 240 trait features for 275 personas, so ridge regularization and held-out validation are essential.
- Near-ceiling prediction means trait geometry spans the persona PCA targets; it does not by itself prove that any single trait label is causally responsible for an axis.
- Coefficients are interpretable only as standardized linear predictors over correlated trait-cosine features.
- The PC3 subset test depends on hand-selected trait groups and should be replaced by a preregistered trait taxonomy or independent rater labels.

## Recommended Next Test

Distill the top trait predictors into a small preregistered axis-rubric set, then test whether those traits predict held-out local-manifold perturbation directions around Trickster, Actor, Therapist, and Spy.
