# AA-18 three-model consensus trait structure

## Headline decision

**A.** The matrix gate passed and the frozen MAXVAR-GCCA analysis found **13 provisional held-out all-three persona-score directions** before the first failed ordered component. **5 individually stable, trait-congruent consensus axes** meet the stricter all-three rule: C1, C2, C3, C4, C5. The separate AJIVE-like top-20 row-subspace validation finds joint rank **19**. These numbers answer different questions; the high joint rank is an in-sample, rank-20 subspace overlap and is not a claim that 19 interpretable latent factors exist.

## Phase gate and direct cross-model audit

**Observed:** All three saved matrices are exact AA-17 hash matches with 275 unique, identically ordered personas and 240 identically ordered signed trait-cosine columns. There are no missing, nonfinite, constant, or exact duplicate columns. The values share a cosine construction but differ in scale and may differ in upstream extraction details; identical labels do not establish measurement invariance. Each persona label has one saved role artifact, not an independent human observation.

Across named traits, 220/240 have minimum pairwise persona-profile Pearson r≥0.50; 9 are pairwise-only by the frozen rule, and 2 have a reversed model pair. The standardized consistency statistic is descriptive. Across personas, 271/275 have minimum pairwise 240-trait-profile Pearson r≥0.50. A small persona subset does not create the broad agreement: the maximum mean leave-one-persona trait-score change is 0.0097.

Strongest named traits by the frozen all-three score: mischievous (0.928), flirty (0.921), nihilistic (0.919), fatalistic (0.919), playful (0.913), cryptic (0.913), melancholic (0.911), edgy (0.909). Weakest by minimum pairwise Pearson: generalist (-0.090), avoidant (-0.025), vindictive (+0.094), literal (+0.105), charismatic (+0.139), curious (+0.158), inclusive (+0.180), anthropocentric (+0.266). Trait-level bootstrap intervals, raw-scale RMSE, and most influential persona for each trait are in the CSVs.

## Shared dimensions and falsification

The primary model uses training-fold column scaling, 20 training-only singular directions per model, and ridge penalty equal to training-persona count. Five-fold held-out scores, 100 persona-correspondence nulls, 100 trait-label loading nulls, eight regularization/PCA-rank sensitivities, 100 persona bootstraps, and 20 split halves are exported. No activation PCs or human outcomes selected dimensions.

| Component | Held-out weakest pair r | Weakest trait-loading Tucker | Bootstrap median axis r | Split-half median axis r | Supported? |
|---|---:|---:|---:|---:|---|
| C1 | 0.972 | 0.879 | 0.997 | 0.984 | yes |
| C2 | 0.965 | 0.824 | 0.990 | 0.930 | yes |
| C3 | 0.947 | 0.908 | 0.990 | 0.935 | yes |
| C4 | 0.887 | 0.737 | 0.982 | 0.937 | yes |
| C5 | 0.915 | 0.749 | 0.967 | 0.908 | yes |
| C6 | 0.897 | 0.682 | 0.954 | 0.826 | no |
| C7 | 0.872 | 0.383 | 0.927 | 0.732 | no |
| C8 | 0.886 | 0.044 | 0.888 | 0.678 | no |
| C9 | 0.834 | 0.402 | 0.899 | 0.632 | no |
| C10 | 0.798 | -0.108 | 0.924 | 0.748 | no |
| C11 | 0.688 | -0.238 | 0.869 | 0.598 | no |
| C12 | 0.558 | -0.426 | 0.773 | 0.525 | no |
| C13 | 0.627 | -0.282 | 0.782 | 0.590 | no |

The first five axes are the conservative interpretable core. Later components can retain highly correlated held-out persona scores while model-specific trait loadings disagree, rotate, or fail split-half stability. Thus agreement about *which personas vary together* extends farther than agreement about a unique named-trait loading pattern. The direct trait audit, covariance organization, and latent-axis organization are related but distinct results.

## Observed loading poles and bounded interpretation

Factor sign and order are conventions. The following labels are post-fit readings of stable axes; they are not causal traits or demonstrated human personality dimensions.

- **Observed C1:** positive mercurial (+0.96), spontaneous (+0.95), obsessive (+0.95), zealous (+0.94), flirty (+0.94); negative factual (-0.95), moderate (-0.94), transparent (-0.91), conciliatory (-0.90), calm (-0.88). **Interpretation:** candidate *charged expression / factual moderation*: highly charged, spontaneous, intense expression versus factual, moderate, conciliatory restraint. Plausible alternative label: *expressive intensity*. **Hypothesis:** this numerical co-expression may reflect a broader behavioral contrast; independent observations would be needed to test that.
- **Observed C2:** positive introverted (+0.97), ritualistic (+0.94), pensive (+0.92), abstract (+0.92), erudite (+0.91); negative experiential (-0.92), practical (-0.89), casual (-0.85), accessible (-0.82), gregarious (-0.72). **Interpretation:** candidate *abstract inwardness / situated practicality*: introverted, ritualistic, conceptual abstraction versus experiential, practical, accessible engagement. Plausible alternative label: *conceptual register*. **Hypothesis:** this numerical co-expression may reflect a broader behavioral contrast; independent observations would be needed to test that.
- **Observed C3:** positive forgiving (+0.90), humanistic (+0.84), nurturing (+0.75), empathetic (+0.72), open_ended (+0.71); negative blunt (-0.80), prescriptive (-0.76), materialist (-0.73), callous (-0.70), confrontational (-0.69). **Interpretation:** candidate *forgiving care / blunt prescription*: forgiving, nurturing, empathic openness versus blunt, prescriptive, callous urgency. Plausible alternative label: *care versus directive hardness*. **Hypothesis:** this numerical co-expression may reflect a broader behavioral contrast; independent observations would be needed to test that.
- **Observed C4:** positive progressive (+0.77), divergent (+0.66), interdisciplinary (+0.66), systems_thinker (+0.66), holistic (+0.65); negative traditional (-0.65), literal (-0.57), concise (-0.50), fundamentalist (-0.46), understated (-0.46). **Interpretation:** candidate *integrative exploration / literal tradition*: progressive, divergent, systems-oriented exploration versus traditional, literal, concise understatement. Plausible alternative label: *integrative scope*. **Hypothesis:** this numerical co-expression may reflect a broader behavioral contrast; independent observations would be needed to test that.
- **Observed C5:** positive decisive (+0.53), closure_seeking (+0.49), universalist (+0.45), assertive (+0.42), confident (+0.36); negative deferential (-0.41), cautious (-0.39), introspective (-0.38), circumspect (-0.36), inquisitive (-0.34). **Interpretation:** candidate *decisive closure / deferential caution*: decisive, assertive closure versus deferential, cautious, inquisitive openness. Plausible alternative label: *closure urgency*. **Hypothesis:** this numerical co-expression may reflect a broader behavioral contrast; independent observations would be needed to test that.

## Joint, pairwise, and model-specific structure

The AJIVE-like top-20 joint rank is 19; 50 persona bootstraps yielded median rank 19 (range 18–19). Its joint-score subspace overlaps the primary GCCA retained-score subspace at minimum canonical correlation 0.968. This validation uses the same saved matrices with a different estimator, so it is not independent measurement evidence.

| Model | Joint variance | Individual variance | Residual variance |
|---|---:|---:|---:|
| Qwen | 0.980 | 0.007 | 0.013 |
| Llama | 0.969 | 0.009 | 0.022 |
| Gemma | 0.972 | 0.007 | 0.021 |

These are in-sample fractions of within-model standardized profile variance under the frozen rank-20 projector decomposition. A high joint fraction means similar persona score spans, not identical trait semantics or absence of small model-specific directions. Pairwise residual subspaces and their fractions of total variance are in `pairwise_shared_structure.csv`; pairwise ranks on the small remaining variance should not be compared directly with the all-three joint rank.

Leave-one-model-out held-out reconstruction (two source models → excluded model's 240 standardized traits, five components): Qwen R²=0.893; Llama R²=0.831; Gemma R²=0.856. This target model is used to learn the training-fold readout, not to define the source components.

## Relation to AA-17

AA-17's grounded/secular versus spiritual/idealist match (Qwen F3 / Llama F2 / Gemma F6) remains in the shared persona-score span but is **split chiefly across C1 and C2**, rather than recovered as a single one-to-one axis. The Llama/Gemma cooperative-optimism match (Llama F1 / Gemma F3) overlaps C1 and, secondarily, C3; Qwen F1 also strongly overlaps C1. This supports an all-three shared portion while leaving model-specific loading combinations and rotations. See `aa17_factor_alignment.csv` for signed score correlations and Tucker congruence, and `aa17_subspace_alignment.csv` for the broader comparison. Similar words alone did not determine either match.

## Human bridge readiness only

The frozen AA-16 semantic bridge provides 45 direct and 74 direct-plus-close trait labels. Five total mapped labels overlap HiFWB composite items and remain excluded for later outcome work; source-item duplicates also require joint treatment. Neither those exclusions nor any human outcome selected components here. Loading mass and frozen-weight mapped-subset score reconstruction are descriptive coverage tests of model profiles, not human factor validity.

| Component | Direct loading mass | 74-set loading mass | 74-set mapped score r | Pole imbalance / coverage bias |
|---|---:|---:|---:|---|
| C1 | 0.197 | 0.328 | 0.990 | not flagged |
| C2 | 0.176 | 0.284 | 0.941 | not flagged |
| C3 | 0.200 | 0.316 | 0.980 | not flagged |
| C4 | 0.159 | 0.264 | 0.927 | not flagged |
| C5 | 0.131 | 0.269 | 0.812 | not flagged |

## Limitations and next gate

**Observed:** Shared labels, prompts, and saved activation-vector construction can generate strong model agreement without independent psychological measurement. Column standardization removes cross-model scale differences but does not prove measurement invariance. The original response-level extraction/filter records remain unavailable. Some higher score directions have poor loading congruence and should be handled as subspaces, not strongly named axes.

**Interpretation:** The five supported axes are credible model-only candidate common dimensions. Their matched human labels cover only a minority of total loading mass even where mapped model scores correlate highly because trait columns are redundant. A later SAPA/HiFWB comparison should be restricted to stable, pole-balanced axes, account for five HiFWB-overlap exclusions and duplicate human measures, and test human convergence independently.

The bridge is **conditionally ready for a restricted future comparison**, not for a full five-axis human interpretation: direct matches cover only 13–20% of absolute loading mass, and C4/C5 have just 8/3 direct and 16/6 total salient mapped traits. C5's total mapped-score reconstruction is weakest (r=0.812). Independent bridge review and duplicate-aware sensitivity remain necessary before human claims.

**Hypothesis:** Similar training data, instruction tuning, preference or safety tuning, chat templates, architecture, and the common English persona/trait prompts could each contribute to the observed convergence. This analysis cannot distinguish those causes. No model inference, RunPod, paid compute, HiFWB fitting, persona wellbeing scoring, respondent-level data, or viewer deployment occurred.
