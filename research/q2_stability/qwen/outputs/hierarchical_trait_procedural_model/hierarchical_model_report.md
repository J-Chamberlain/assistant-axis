# Hierarchical Trait + Procedural Model Report

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Script author model: GPT-5.5 Standard via Codex

## 1. Research Question

This experiment tests whether canonical persona activation geometry factorizes into a broad dispositional trait baseline plus a procedural/operating-mode residual correction. It is not framed as Big Five versus procedural structure; it asks whether procedural features explain what remains after trait-like features establish broad placement.

## 2. Method

Stage A fits canonical activation PCA coordinates from semantic controls plus Claude Big-Five-style trait features. Stage B computes train-set residuals from Stage A and fits selected Codex procedural/behavioral dimensions to those residuals. On held-out personas, the final prediction is Stage A trait prediction plus Stage B residual correction. The same canonical splits and ridge regularization path are used throughout.

## 3. Model Comparison

| Model | Mean R2 | PC1 | PC2 | PC3 | Mean residual | NN preserve | Cluster acc | Delta vs trait |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| semantic_baseline | 0.389 | 0.517 | 0.181 | 0.336 | 27.213 | 0.156 | 0.584 | -0.224 |
| trait_stage | 0.613 | 0.734 | 0.480 | 0.416 | 21.748 | 0.232 | 0.715 | +0.000 |
| procedural_alone | 0.418 | 0.573 | 0.164 | 0.348 | 26.687 | 0.171 | 0.608 | -0.195 |
| naive_concat | 0.613 | 0.747 | 0.441 | 0.441 | 21.768 | 0.245 | 0.704 | -0.000 |
| hierarchical | 0.622 | 0.745 | 0.482 | 0.426 | 21.524 | 0.252 | 0.704 | +0.009 |

## 4. Specific Questions

1. Traits alone explain mean held-out PCA3D R2 0.613.
2. Procedural residual correction changes R2 by +0.009 and changes mean residual by +0.224.
3. Personas improving most after procedural correction: wind (+9.42), auditor (+9.41), visionary (+8.33), exile (+7.47), examiner (+7.38), robot (+6.47), specialist (+6.26), criminal (+5.88), graduate (+5.72), evangelist (+5.56), bard (+5.48), teacher (+5.25).
4. Personas remaining most unexplained after both stages: procrastinator (64.71), toddler (58.88), teenager (54.93), adolescent (50.18), smuggler (48.52), infant (45.15), swarm (44.68), loner (44.62), caveman (44.43), daredevil (44.05), pirate (42.88), student (41.54).
5. Bridge roles do not improve disproportionately: bridge mean improvement 0.049 vs non-bridge 0.553.
6. Developmental roles remain high residual: mean hierarchical residual 52.281 vs non-developmental 21.112.
7. Local-neighborhood preservation changes from trait 0.232 to hierarchical 0.252.
8. The integrated model outperforms Big Five alone, outperforms Codex procedural alone, and outperforms naive concatenation.

## 5. Optional Third-Layer Residual Analysis

Among the top 25 residual personas after Stage B, cluster counts are {'other': 6, 'grounded_social': 5, 'procedural_professional': 7, 'trickster_chaos': 2, 'combative_iconoclast': 1, 'editorial': 1, 'mythic_spiritual': 3}. Developmental roles account for 4, symbolic/liminal clusters for 11, and bridge roles for 20. This suggests whether a future symbolic/liminal or developmental layer is plausible, but no third-layer model is fit here.

## 6. Interpretation

The result should be read as a hierarchical residualization test, not a competition. If Stage B improves over Stage A, that supports a layered model in which traits establish broad latent placement and procedural features refine local behavioral topology. If Stage B fails to improve, it means the selected procedural columns do not explain held-out trait residuals under this operationalization, even if procedural features remain useful in direct prediction.

## 7. Final Interpretive Questions

- Clean factorization: supported.
- BigFive-like broad placement: supported by the Stage A performance.
- Procedural local differentiation: supported.
- Symbolic/liminal residual: see top-residual cluster counts above; this remains descriptive, not modeled.
- Overall geometry: the evidence continues to favor continuous behavioral manifolds over discrete persona taxonomies, because continuous PCA prediction is where signal is strongest.