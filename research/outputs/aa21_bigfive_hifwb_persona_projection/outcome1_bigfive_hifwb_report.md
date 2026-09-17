# Outcome 1: Big Five–transported HiFWB persona profiles

## Decision

**Proceed.** A Big Five–based human-associated wellbeing gradient transports coherently into all three model persona spaces. The result is robust to the 42-trait versus 109-trait Big Five construction and to the choice of the full-overlap versus AA-20-common human coefficient fit.

The score is an estimate of the human HiFWB level statistically associated with a persona's behavioral profile. It is not evidence that a model persona experiences wellbeing.

## Human model

The frozen 13-item HiFWB composite and official IPIP100 Big Five keys were reconstructed from the hash-matched SAPA source. The primary complete-overlap sample contained 3,972 respondents. A prespecified 60/20/20 split selected unregularized regression and achieved held-out R² = 0.395 (RMSE = 0.762 standardized HiFWB units).

Standardized full-sample coefficients were:

| Domain | Coefficient |
|---|---:|
| Emotional stability | +0.396 |
| Extraversion | +0.276 |
| Conscientiousness | +0.182 |
| Agreeableness | +0.085 |
| Openness | +0.022 |

The separately reconstructed AA-20-common ridge coefficients produced persona rankings correlated at Pearson r = 0.9995–0.9997 with the primary fit across the six model-by-construction combinations.

## Trait-construction sensitivity

Persona wellbeing rankings from the strict 42-trait construction and expanded 109-trait construction were strongly concordant:

| Model | Pearson r | Spearman rho | Top-10 overlap | Bottom-10 overlap |
|---|---:|---:|---:|---:|
| Qwen | 0.977 | 0.970 | 7 | 8 |
| Gemma | 0.953 | 0.935 | 7 | 7 |
| Llama | 0.949 | 0.865 | 3 | 9 |

Llama's low top-10 overlap despite a high global correlation indicates instability near the extreme upper cutoff, not a different overall gradient.

## Cross-model convergence

For the expanded construction, cross-model persona-score Pearson correlations were 0.919 (Gemma–Llama), 0.948 (Gemma–Qwen), and 0.847 (Llama–Qwen). For the strict construction they were 0.923, 0.940, and 0.814 respectively. Thus, the same named personas are ordered similarly across independently analyzed models, with Llama–Qwen consistently the weakest pair.

The expanded construction's upper extreme repeatedly included healer, pacifist, peacekeeper, emissary, optimist, coach, facilitator, ambassador, and collaborator. Its lower extreme repeatedly included cynic, procrastinator, caveman, infant, criminal, and narcissist. These labels summarize profile locations; they are not validated prescriptions or causal findings.

## Interpretation

Outcome 1 establishes a stable baseline suitable for comparison with later mappings. Most of the transported gradient is driven by emotional stability, extraversion, and conscientiousness. The expanded trait vocabulary changes local rankings but does not overturn the broad wellbeing ordering. The next independent outcome should test the direct SAPA-linked trait bridge and quantify where it agrees with or departs from this Big Five baseline.

## Artifacts

- `human_bigfive_hifwb_coefficients.csv`
- `persona_bigfive_hifwb_projection.csv`
- `construction_sensitivity.csv`
- `cross_model_convergence.csv`
- `human_model_metrics.json`
- `run_bigfive_hifwb_projection.py`

