# Prompt-To-Geometry Forecasting Dataset Summary

Model used for analysis scripting: GPT-5.5.

## Exact Artifacts Used

- Trait prompts: `data/traits/instructions/*.json`
- Trait descriptions: `data/traits/trait_list.json`
- Role prompts: `data/roles/instructions/*.json`
- Role descriptions: `data/roles/role_list.json`
- Prompt inventory: `research/outputs/prompt_artifact_inventory/`
- Trait PCA targets: `research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv`
- Persona/role PCA targets: `research/visualizations/geometry_viz_data.json`

## Dataset Construction

One row was created per concept per text variant. This is a concept-level forecasting test, not an individual prompt-row memorization test.

Variants:

- `description_only`
- `description_plus_instructions`
- `description_plus_questions`
- `description_plus_instructions_plus_questions`
- `leakage_control`: description + instructions + questions with exact target names replaced by `[TARGET]`; eval prompts excluded.

Eval prompts were excluded from all variants because they directly reveal target labels and scoring rubrics. The leakage-control variant additionally removes explicit target names where feasible.

## Holdout Methodology

- Trait test: exactly 40 complete held-out traits; 200 complete train traits.
- Role test: 20% held-out roles by concept using a fixed random seed.
- No train/test split occurs at the individual prompt level.

Held-out trait names: adventurous, analytical, animated, ascetic, benevolent, big_picture, callous, calm, charismatic, contemporary, data_driven, dramatic, emotional, esoteric, extroverted, flexible, generalist, grounded, hostile, humanistic, inquisitive, interdisciplinary, metaphorical, mystical, narrative, neurotic, pensive, philosophical, poetic, practical, provocative, radical, reserved, sassy, skeptical, transparent, universalist, verbose, visceral, witty

## Best Held-Out Results

Best trait model: `elastic_net_tfidf` on `leakage_control`, mean R2=0.389; PC1 R2=0.414, PC2 R2=0.304, PC3 R2=0.450.

Best role model: `elastic_net_tfidf` on `leakage_control`, mean R2=0.621; PC1 R2=0.783, PC2 R2=0.577, PC3 R2=0.504.

Best leakage-control trait model: `elastic_net_tfidf`, mean R2=0.389; PC1 R2=0.414, PC2 R2=0.304, PC3 R2=0.450.

## Top Held-Out Model Rows

```text
concept_type                                      variant             model  mean_R2   PC1_R2   PC2_R2   PC3_R2  PC1_Pearson_r  PC2_Pearson_r  PC3_Pearson_r
        role                              leakage_control elastic_net_tfidf 0.621473 0.783467 0.576538 0.504413       0.887057       0.771674       0.731975
        role description_plus_instructions_plus_questions elastic_net_tfidf 0.619755 0.784421 0.572405 0.502439       0.886791       0.767678       0.725561
        role description_plus_instructions_plus_questions       ridge_tfidf 0.616100 0.798423 0.559955 0.489922       0.897371       0.759655       0.726714
        role                              leakage_control       ridge_tfidf 0.612532 0.792364 0.558845 0.486388       0.894893       0.761254       0.730585
        role description_plus_instructions_plus_questions   small_mlp_tfidf 0.592798 0.792448 0.522996 0.462950       0.905565       0.744186       0.721529
        role                              leakage_control   small_mlp_tfidf 0.588842 0.788698 0.520646 0.457182       0.904480       0.746797       0.726220
        role                description_plus_instructions   small_mlp_tfidf 0.547953 0.703648 0.511166 0.429044       0.855672       0.782536       0.712329
        role                description_plus_instructions       ridge_tfidf 0.545366 0.627162 0.553724 0.455213       0.844436       0.780473       0.690490
        role                   description_plus_questions elastic_net_tfidf 0.537953 0.720707 0.502209 0.390943       0.851670       0.712757       0.647976
        role                description_plus_instructions elastic_net_tfidf 0.534683 0.593086 0.566503 0.444461       0.846970       0.777339       0.667691
        role                   description_plus_questions       ridge_tfidf 0.533274 0.726644 0.485603 0.387573       0.858420       0.703833       0.662672
        role                   description_plus_questions   small_mlp_tfidf 0.512768 0.723255 0.464691 0.350357       0.867935       0.704503       0.642396
```

## Interpretation

The forecasting test should be interpreted as a prompt-artifact predictability study. Positive held-out performance means the released prompt text contains geometry-relevant information before generation. It does not prove that a new model execution would land at the same geometry under different sampling, nor does it create a safety controller.
