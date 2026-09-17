# AA-22 direct SAPA-linked trait bridge to HiFWB

**Headline decision: A — preliminary incremental HiFWB signal, with transport still hypothesis-bearing.** The direct bridge uses 41 AA-19 primary, unique-source, outcome-safe traits. It learns trait–HiFWB associations in the training split, evaluates a renormalized weighted trait index on held-out respondents, and transports the full-sample weights to the three saved 275×240 persona matrices.

## Human held-out comparison

| Model | Test N | R² | RMSE |
|---|---:|---:|---:|
| BigFive | 693 | 0.456 | 0.607 |
| DirectTraitIndex | 693 | 0.402 | 0.636 |
| BigFive_plus_DirectTraitIndex | 693 | 0.495 | 0.584 |

The direct-index increment over Big Five is ΔR²=+0.040, paired test-resample 95% interval [+0.016, +0.065]. In this frozen split the interval excludes zero, so the direct bridge adds signal beyond the Big Five. This is a preliminary validation result, not a causal claim or a guarantee that the increment will replicate.

## Transport

The model projection is a weighted, within-model standardized combination of the 41 named trait profiles. It is a hypothesis-bearing score for comparing persona rankings, not a calibrated wellbeing estimate. Against the AA-21 expanded Big Five baseline, direct-versus-Big-Five persona-score Pearson/Spearman correlations are: Gemma 0.943/0.932; Llama 0.953/0.936; Qwen 0.872/0.795. Results are in `persona_direct_trait_hifwb_projection.csv` and `projection_comparison_with_bigfive.csv`.

## Limits

The SAPA matrix has planned missingness; eligibility requires at least eight observed proxy traits and complete Big Five scores for the common comparison. The bridge is semantically mapped and sparse. No HiFWB items were used as predictors, no model inference or paid compute occurred, and no causal or human-equivalence claim is made.
