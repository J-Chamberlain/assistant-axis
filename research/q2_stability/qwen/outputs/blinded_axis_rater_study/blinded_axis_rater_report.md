# Reading-Based Blinded PCA-Axis Rater Study

## What Was Done

Observed: Codex/GPT-5.5 performed a reading-based blinded annotation study over anonymized persona dossiers. Each dossier contained the complete available no-label persona-associated text: five rewritten system prompts per persona, with no persona name, PCA coordinate, cluster label, Big Five score, residual, or prior interpretation label shown to the rater.

Observed: the study covers 275 personas. Scoring used the whole dossier text for each persona and produced 0-100 ratings plus short text-grounded rationales for PC1, PC2, PC3, and PC2 alternatives.

## Corpus Actually Used

Observed: no full 275-persona rollout-response corpus was found locally. Full responses exist for specific experiments, especially trickster and editor, but not for all personas. The chosen corpus is the complete no-label prompt-ablation corpus at `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`.

Observed: this means the study validates interpretations against persona operationalization text, not generated rollout behavior.

## Rater Independence

Observed: scoring type is Codex-as-rater. No local independent LLM runtime was available, and the previous deterministic keyword-proxy method was not reused. This is stronger than the lexical proxy because the rater read the dossiers and assigned semantic scores with rationales, but weaker than an independent model or human blinded study.

## Main Quantitative Results

Target-aligned correlations:

| score | pc | pearson | spearman |
| --- | --- | --- | --- |
| pc1_objective_certainty_score | pc1 | 0.558 | 0.565 |
| pc2_coherent_action_under_uncertainty_score | pc2 | 0.373 | 0.303 |
| pc3_antagonistic_transgressive_score | pc3 | 0.690 | 0.630 |

Strongest off-target correlations:

| score | pc | pearson | spearman |
| --- | --- | --- | --- |
| intelligence_expertise_score | pc1 | 0.663 | 0.708 |
| abstraction_score | pc2 | -0.655 | -0.658 |
| maturity_score | pc1 | 0.527 | 0.556 |
| pc3_antagonistic_transgressive_score | pc1 | -0.428 | -0.399 |
| pc2_coherent_action_under_uncertainty_score | pc1 | -0.420 | -0.398 |
| uncertainty_residence_time_score | pc2 | -0.400 | -0.334 |
| maturity_score | pc2 | -0.377 | -0.255 |
| maturity_score | pc3 | -0.356 | -0.309 |
| intelligence_expertise_score | pc2 | -0.352 | -0.272 |
| uncertainty_residence_time_score | pc1 | 0.330 | 0.283 |

Cross-validated R2 from the three main rater scores:

| Target | Train R2 | CV R2 | Permutation p95 CV R2 |
| --- | ---: | ---: | ---: |
| PC1 | 0.517 | 0.496 | 0.004 |
| PC2 | 0.145 | 0.101 | 0.002 |
| PC3 | 0.544 | 0.522 | 0.007 |

Cross-validated R2 from expanded scores including PC2 alternatives:

| Target | Train R2 | CV R2 | Permutation p95 CV R2 |
| --- | ---: | ---: | ---: |
| PC1 | 0.657 | 0.616 | -0.011 |
| PC2 | 0.606 | 0.564 | -0.007 |
| PC3 | 0.712 | 0.686 | -0.007 |

Matched-pair validation:

| pc | pairs | direction_match_rate |
| --- | --- | --- |
| pc1 | 20 | 0.750 |
| pc2 | 20 | 1.000 |
| pc3 | 20 | 0.950 |

## PC2 Alternative Comparison

Observed: PC2 alternatives are ranked below by absolute correlation with PC2.

| score | pc | pearson | spearman | target_aligned |
| --- | --- | --- | --- | --- |
| abstraction_score | pc2 | -0.655 | -0.658 | False |
| uncertainty_residence_time_score | pc2 | -0.400 | -0.334 | False |
| maturity_score | pc2 | -0.377 | -0.255 | False |
| pc2_coherent_action_under_uncertainty_score | pc2 | 0.373 | 0.303 | True |
| intelligence_expertise_score | pc2 | -0.352 | -0.272 | False |
| uncertainty_exposure_score | pc2 | -0.084 | -0.097 | False |

## Interpretation Update

Observed: the strongest target-aligned reading-based correlation is `pc3_antagonistic_transgressive_score` to pc3 at r=0.690. The weakest is `pc2_coherent_action_under_uncertainty_score` to pc2 at r=0.373.

Observed: all three target correlations exceed the prior deterministic lexical-proxy screen: PC1 0.558 vs 0.247, PC2 0.373 vs 0.224, and PC3 0.690 vs 0.349. The reading-based study therefore strengthens the claim that the working axis interpretations are present in the no-label prompt dossiers, especially PC3 and PC1.

Observed: PC1 is strengthened but not isolated. The objective-certainty score predicts PC1 at r=0.558 and has a 0.750 matched-pair direction rate, but intelligence/expertise is an even stronger PC1 correlate at r=0.663. This suggests PC1 should be framed as objective certainty plus disciplined expertise/procedural competence, not only constraint.

Observed: PC3 is strongly strengthened. The antagonistic-transgressive score predicts PC3 at r=0.690, with cross-validated R2=0.522 from the three main scores and a 0.950 matched-pair direction rate. The cooperative-stabilizing versus antagonistic-transgressive interpretation is now the best-supported direct axis interpretation in this rater study.

Observed: PC2 remains the main uncertainty. The coherent-action-under-uncertainty score predicts PC2 at r=0.373 and performs well in matched pairs, but abstraction is a much stronger PC2 correlate in the opposite direction at r=-0.655. Uncertainty residence time, maturity, and expertise also correlate with PC2 at magnitudes similar to or larger than the direct coherent-action score. This weakens the claim that coherent action under uncertainty is the best single PC2 formulation.

Speculative: divergence between dossier ratings and PCA coordinates may reflect activation geometry reorganizing prompt semantics, the absence of rollout behavior in the corpus, rater-model subjectivity, or genuinely compound axes.

## Strongest Counterexamples

Observed: the following matched pairs violate the predicted score direction while staying relatively close on the other two PCs:

| target_pc | persona_name_a | persona_name_b | pc_delta_a_minus_b | score_delta_a_minus_b | orthogonal_pc_distance |
| --- | --- | --- | --- | --- | --- |
| pc1 | sociologist | virtuoso | 48.420 | -14.000 | 0.482 |
| pc1 | prey | reporter | -69.767 | 9.000 | 1.361 |
| pc1 | economist | predator | 69.649 | -4.000 | 1.362 |
| pc1 | revenant | scholar | -90.995 | 24.000 | 1.785 |
| pc1 | golem | stoic | -30.414 | 14.000 | 0.648 |
| pc3 | economist | reviewer | 12.153 | -2.000 | 0.549 |

## Confidence Update

PC1: confidence increases to moderate. The rater score predicts PC1 clearly, but the stronger intelligence/expertise correlation means the constraint versus possibility language should include disciplined knowledge practice and externally legible competence.

PC2: confidence remains low to moderate. The axis appears to involve abstraction, maturity, expertise, and residence with uncertainty more strongly than the direct coherent-action score alone. Strong paper language should wait for a richer full-response rater study or a targeted matched-pair annotation design.

PC3: confidence increases to moderate-high within the limits of prompt-dossier evidence. It should still be described as a partial stance axis rather than a complete account of PC3.

## Recommended Next Test

Run an independent-rater version of this study using a second model or human annotators and, if possible, richer rollout responses rather than system-prompt dossiers. For PC2, use a smaller matched-pair design that forces raters to distinguish maturity, abstraction, uncertainty exposure, and coherent action under unresolved uncertainty.
