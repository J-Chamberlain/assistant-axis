# Claude Latent Feature Discovery Loop — Report

## Provenance
- analysis_model: claude-sonnet-4-6
- script_author_model: claude-sonnet-4-6
- orchestration_agent: claude-code
- provider: anthropic
- date: 2026-05-28

## Purpose
Independent hypothesis-generation and interpretation pass over assistant-axis
persona geometry data. Cross-model convergence test: does Claude Code
independently converge on similar explanatory dimensions and predictive gains
as a Codex/GPT-5.5 analysis?

## Target Variables
Primary target: pseudo-PCA3D from 275×7 Qwen cluster-cosine matrix.
Secondary target: Gemma 2 27B axis_projection_layer22 (normalized).

Pseudo-PCA3D explained variance:
  PC1: 0.593
  PC2: 0.259
  PC3: 0.103
  Total: 0.955

## Null Baseline (permutation test, n=200)
- Null PCA3D R² mean: -0.3219
- Null PCA3D R² p95:  -0.2210
- Null PCA3D R² p99:  -0.1959

## Claude-Hypothesized Dimensions
Ten semantic dimensions independently proposed by Claude as likely
explanatory of activation cluster structure:

1. **evaluative_orientation** — 15/275 roles (5%)
2. **relational_embodiment** — 66/275 roles (24%)
3. **mythic_symbolic** — 43/275 roles (16%)
4. **adversarial_oppositional** — 15/275 roles (5%)
5. **creative_narrative** — 18/275 roles (7%)
6. **professional_specialist** — 46/275 roles (17%)
7. **abstract_collective** — 26/275 roles (9%)
8. **pedagogical_knowledge** — 47/275 roles (17%)
9. **hedonistic_leisure** — 28/275 roles (10%)
10. **moral_ideological** — 20/275 roles (7%)

## Iterative Loop Results

| Round | Feature Set | n_features | PCA3D R² | PC1 R² | PC2 R² | PC3 R² | Gemma R² | ΔR² |
|---|---|---|---|---|---|---|---|---|
| 0 | F0_tfidf_semantic_baseline | 50 | 0.1423 | -0.1387 | 0.526 | 0.0396 | 0.4518 | +inf |
| 1 | F1_big5_traits | 55 | 0.3611 | -0.0887 | 0.7319 | 0.4401 | 0.6947 | +0.2189 |
| 2 | F2_big5_dark3 | 58 | 0.3526 | -0.1281 | 0.7343 | 0.4516 | 0.7117 | -0.0085 |
| 3 | F3_sem_cluster | 65 | 0.3389 | -0.1439 | 0.7441 | 0.4165 | 0.7081 | -0.0137 |

**Best feature set: F1_big5_traits**
**Best PCA3D R²: 0.3611**
**Best Gemma R²: 0.6947**

## Top 20 Best-Explained Personas (lowest final residual)

| Rank | Persona | Residual | Cluster | Stable Anchor | Bridge |
|---|---|---|---|---|---|
| 1 | architect | 0.2993 | procedural_professional | True | False |
| 2 | improviser | 0.2996 | trickster_chaos | False | False |
| 3 | journalist | 0.3002 | procedural_professional | False | False |
| 4 | paramedic | 0.3077 | procedural_professional | False | False |
| 5 | marketer | 0.3265 | procedural_professional | True | False |
| 6 | parasite | 0.3287 | mythic_spiritual | False | False |
| 7 | veteran | 0.3290 | grounded_social | True | False |
| 8 | absurdist | 0.3325 | trickster_chaos | False | False |
| 9 | soldier | 0.3341 | grounded_social | True | False |
| 10 | reporter | 0.3642 | procedural_professional | False | False |
| 11 | doctor | 0.3973 | procedural_professional | False | False |
| 12 | recruiter | 0.4172 | procedural_professional | False | False |
| 13 | bartender | 0.4672 | grounded_social | False | False |
| 14 | psychologist | 0.4697 | procedural_professional | False | False |
| 15 | researcher | 0.4732 | procedural_professional | False | False |
| 16 | pilot | 0.5093 | procedural_professional | True | False |
| 17 | archivist | 0.5170 | procedural_professional | True | True |
| 18 | scholar | 0.5253 | procedural_professional | False | False |
| 19 | ghost | 0.5334 | mythic_spiritual | False | True |
| 20 | veterinarian | 0.5523 | procedural_professional | False | False |

## Top 20 Worst-Explained Personas (highest final residual)

| Rank | Persona | Residual | Cluster | Stable Anchor | Bridge |
|---|---|---|---|---|---|
| 1 | toddler | 11.1440 | other | False | True |
| 2 | caveman | 10.2094 | other | False | False |
| 3 | infant | 9.1745 | other | True | False |
| 4 | pirate | 7.6625 | grounded_social | True | False |
| 5 | proofreader | 6.6644 | editorial | False | True |
| 6 | teenager | 6.2692 | other | False | False |
| 7 | perfectionist | 5.9393 | procedural_professional | False | False |
| 8 | poet | 5.3477 | other | False | False |
| 9 | adolescent | 5.2875 | other | False | False |
| 10 | workaholic | 4.8642 | combative_iconoclast | False | False |
| 11 | peacekeeper | 4.8502 | procedural_professional | False | True |
| 12 | amnesiac | 4.5386 | other | False | True |
| 13 | leviathan | 4.2637 | mythic_spiritual | True | False |
| 14 | bohemian | 4.2504 | mythic_spiritual | False | False |
| 15 | procrastinator | 4.2033 | other | False | False |
| 16 | philosopher | 4.1671 | mythic_spiritual | False | False |
| 17 | comedian | 3.7615 | other | False | False |
| 18 | negotiator | 3.7402 | procedural_professional | False | True |
| 19 | romantic | 3.4627 | mythic_spiritual | False | False |
| 20 | chameleon | 3.4255 | grounded_social | False | True |

## Baseline vs Best Model Residual Improvement

Baseline (TF-IDF only) PCA3D R²: 0.1423
Best model PCA3D R²: 0.3611
Improvement: +0.2188

## Interpretation Notes
- Claude independently proposed 10 semantic dimensions as likely explanatory.
- The evaluative_orientation dimension (proofreader, screener, grader, etc.) was
  hypothesized as the primary driver of the assistant axis positive pole.
- The mythic_symbolic and relational_embodiment dimensions were hypothesized
  as primary drivers of the non-procedural activation clusters.
- Cross-model rank features were added as the final round to test whether
  Qwen/Llama axis convergence adds independent predictive signal.
- Per interpretation constraints: Claude-derived dimensions are hypotheses,
  not truths. Cross-model convergence with a Codex/GPT-5.5 analysis (if
  available) would support but not confirm interpretive stability.