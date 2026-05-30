# Forecasting Dataset Feasibility

## Judgment

Ready. Trait prompt artifacts are available locally and from the released Belmore prompt dataset, and they exactly match the 240 Qwen trait vector names.

## Minimum Dataset

- Input: trait description + positive instruction texts + behavioral questions.
- Target: trait PC1/PC2/PC3 from `research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv`.
- Split: hold out entire traits.

## Stronger Dataset

- Input: serialized full trait artifact including positive/negative instruction pairs and eval prompt.
- Target: mean-pooled 5120-D trait vector and trait PCA coordinates.
- Optional auxiliary target: similarity profile against 275 persona vectors.

## Caveats

- Eval prompts reveal the intended trait label and should be excluded from strict prompt-to-geometry forecasting if the goal is semantic generalization without target-label leakage.
- Negative instructions encode contrastive trait structure and may be predictive; include polarity explicitly.
- Forecasting from prompt text to released geometry tests artifact-to-vector predictability, not whether a target model would produce the same vector under new sampling.
