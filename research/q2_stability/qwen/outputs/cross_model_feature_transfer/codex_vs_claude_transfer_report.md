# Codex vs Claude Feature Transfer Report

Date: 2026-05-28
Model used: GPT-5.5 Standard

## 1. Research Question

This comparison asks whether feature vocabularies transfer across targets. Specifically, it tests whether Claude Big Five features improve prediction of canonical Qwen activation PCA geometry, and whether Codex-derived behavioral/procedural latent features improve prediction of the Big-Five-derived pseudo-PCA target.

## 2. Method

The analysis reuses the iterative outer-loop persona loader, five deterministic split seeds, train size, ridge regression selection, per-axis R2, and semantic baseline. The semantic baseline is the same available one-hot cluster feature set: original-prompt k=7, no-label-prompt k=7, and role-name k=7. Codex features are the final 31 retained iterative outer-loop dimensions. Claude Big Five features are the five role-level scores in `visualizations/bigfive_profiles.json`. The pseudo-PCA target is reconstructed by PCA over those five Big Five dimensions because no separate Claude pseudo-PCA coordinate artifact was found locally.

## 3. Results

| feature_family | target | mean_r2 | semantic_baseline_r2 | delta_vs_semantic_baseline | axis1_r2 | axis2_r2 | axis3_r2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex_derived_outer_loop_features | canonical_activation_pca3 | 0.49009 | 0.389397 | 0.100693 | 0.631205 | 0.257221 | 0.422097 |
| claude_big_five_features | canonical_activation_pca3 | 0.612861 | 0.389397 | 0.223464 | 0.733919 | 0.480416 | 0.414677 |
| codex_derived_outer_loop_features | claude_big_five_pseudo_pca3 | 0.280223 | 0.268704 | 0.01152 | 0.401787 | -0.190897 | 0.073905 |
| claude_big_five_features | claude_big_five_pseudo_pca3 | 1.0 | 0.268704 | 0.731296 | 1.0 | 1.0 | 1.0 |

## 4. Per-Axis Pattern

- codex_derived_outer_loop_features on canonical_activation_pca3: axis1=0.631, axis2=0.257, axis3=0.422; baseline axes=(0.517, 0.181, 0.336).
- claude_big_five_features on canonical_activation_pca3: axis1=0.734, axis2=0.480, axis3=0.415; baseline axes=(0.517, 0.181, 0.336).
- codex_derived_outer_loop_features on claude_big_five_pseudo_pca3: axis1=0.402, axis2=-0.191, axis3=0.074; baseline axes=(0.338, 0.056, 0.063).
- claude_big_five_features on claude_big_five_pseudo_pca3: axis1=1.000, axis2=1.000, axis3=1.000; baseline axes=(0.338, 0.056, 0.063).

## 5. Interpretation

Codex-derived features improve canonical activation PCA prediction by +0.101 R2 over the semantic baseline. Claude Big Five features change canonical activation PCA prediction by +0.223 R2 over the same baseline. Codex-derived features change the Big-Five pseudo-PCA target by +0.012 R2, while Big Five features change their own pseudo-PCA target by +0.731 R2.

The result should be read as mixed transfer only if both off-diagonal conditions improve R2 and reduce residuals relative to the semantic baseline. If only one off-diagonal condition passes both checks, the evidence supports asymmetric transfer. If neither off-diagonal condition passes, the evidence supports target specificity or semantic-baseline dominance under this operationalization.

This run's categorical conclusion is: **big five transfers to activation but codex does not transfer to pseudo pca**.

## 6. Limitations

- The local Big Five profile JSON does not carry explicit Claude provenance metadata, so the analysis labels it as the available Claude/Big-Five feature source requested by the task.
- The pseudo-PCA target is reconstructed from Big Five scores, not loaded from a dedicated Claude pseudo-PCA artifact.
- Big-Five-on-pseudo-PCA is therefore a positive-control condition and should not be interpreted as independent evidence of transfer.
- The comparison uses the existing lexical/ordinal Codex feature compiler and should be repeated with blind model-coded features if this result becomes central.

## 7. Recommended Follow-Ups

- Locate or generate a separately committed Claude pseudo-PCA artifact if one exists outside this repo snapshot, then rerun the same script without target reconstruction.
- Add feature-score correlation analysis between Codex retained dimensions and Big Five dimensions.
- Repeat the transfer matrix with leave-one-role-out coverage if all-persona held-out evidence is needed.
- Add a third feature family from another model to distinguish Claude-specificity from Big-Five-specificity.
