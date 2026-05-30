# Blinded Axis Rubric Validation Report

## What Was Done

Observed: this study tested whether coordinate-blind scores from the full available no-label persona prompt corpus predict actual Qwen persona PCA coordinates. It used all 275 personas and all five no-label rewritten prompts per persona. It did not use persona names, PCA coordinates, clusters, residuals, or prior labels during scoring.

Observed: no pods were launched, no activations were generated, and no external model APIs were called.

## Corpus Used

| corpus_path | personas_covered | total_prompt_records | corpus_type | sampling_decision |
| --- | --- | --- | --- | --- |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl | 275 | 1375 | no-label rewritten system prompts, not full rollout responses | No sampling; all five no-label rewritten prompts per persona were concatenated. |

Unknown: a complete 275-persona rollout-response corpus was not located from the canonical state files during this pass. The strongest available full text corpus is therefore the no-label system-prompt corpus, which captures operationalized persona instructions rather than model responses.

## Main Quantitative Results

Target-aligned correlations:

| score | pc | pearson | spearman |
| --- | --- | --- | --- |
| pc1_objective_certainty_score | pc1 | 0.247 | 0.226 |
| pc2_coherent_action_under_uncertainty_score | pc2 | 0.224 | 0.198 |
| pc3_antagonistic_transgressive_score | pc3 | 0.349 | 0.276 |

Strongest off-axis correlations among rubric scores:

| score | pc | pearson | spearman |
| --- | --- | --- | --- |
| pc2_intelligence_expertise_score | pc1 | 0.384 | 0.389 |
| pc2_abstraction_score | pc3 | 0.221 | 0.210 |
| pc2_maturity_risk_score | pc2 | 0.216 | 0.165 |
| pc2_maturity_risk_score | pc1 | -0.209 | -0.222 |
| pc2_abstraction_score | pc2 | -0.172 | -0.191 |
| pc2_maturity_risk_score | pc3 | 0.161 | 0.161 |
| pc2_intelligence_expertise_score | pc2 | -0.151 | -0.141 |
| pc2_intelligence_expertise_score | pc3 | 0.150 | 0.161 |
| pc1_objective_certainty_score | pc3 | 0.145 | 0.163 |
| pc2_coherent_action_under_uncertainty_score | pc1 | -0.141 | -0.123 |

PC2 alternative rubric correlations with PC2:

| score | pc | pearson | spearman |
| --- | --- | --- | --- |
| pc2_coherent_action_under_uncertainty_score | pc2 | 0.224 | 0.198 |
| pc2_maturity_risk_score | pc2 | 0.216 | 0.165 |
| pc2_abstraction_score | pc2 | -0.172 | -0.191 |
| pc2_intelligence_expertise_score | pc2 | -0.151 | -0.141 |
| pc2_integrated_uncertainty_alt_score | pc2 | -0.134 | -0.149 |
| pc2_openness_proxy_score | pc2 | 0.096 | 0.146 |
| pc2_uncertainty_residence_time_score | pc2 | -0.076 | -0.082 |
| pc2_uncertainty_exposure_score | pc2 | 0.052 | 0.057 |

Matched-pair validation summary:

| pc | pairs | direction_match_rate |
| --- | --- | --- |
| pc1 | 20 | 0.350 |
| pc2 | 20 | 0.400 |
| pc3 | 20 | 0.400 |

Regression results are saved in `axis_rubric_regression_results.json`.

## Interpretation

Observed: the target-aligned rubric correlations are positive but modest: PC1 r=0.247, PC2 r=0.224, and PC3 r=0.349. The simple three-score regression has cross-validated R2 values of PC1=0.065, PC2=0.024, and PC3=0.116. The expanded score set improves PC1 and PC3 cross-validated prediction to 0.182 and 0.176, but does not improve PC2, which falls to -0.016.

Observed: matched-pair validation is weak, with direction-match rates of PC1=0.350, PC2=0.400, and PC3=0.400. Many failures are ties produced by the coarse lexical proxy, so the pairwise result mainly limits confidence in the proxy scorer rather than falsifying the axis interpretations.

Observed: PC3 is the strongest of the three target rubrics in direct correlation, which modestly supports the cooperative-stabilizing versus antagonistic-transgressive interpretation. PC1 remains positive but weaker than expected, and PC2 remains the weakest and most methodologically fragile interpretation.

Observed: among PC2 alternatives, the current coherent-action-under-uncertainty proxy is the strongest PC2 correlate in this lexical implementation (r=0.224 for `pc2_coherent_action_under_uncertainty_score`), but it only narrowly exceeds maturity risk and does not produce useful cross-validated PC2 prediction.

Inferred: this study weakens any strong claim that the current axis interpretations are recoverable from simple no-label prompt-text rubrics alone. It does not weaken the broader layered-geometry interpretation, because earlier benchmark work already shows that semantic, trait, procedural, and lexical/register features jointly predict activation geometry better than any single simple rubric.

Speculative: the weak pairwise results may reflect the limits of lexical proxies, the short five-prompt corpus, or genuinely mixed axis structure. A richer blinded human or LLM rater using full rollout responses could produce stronger evidence either for or against the current interpretations.

## Key Judgment Calls

Observed: the study used no-label prompts instead of original label-exposed prompts to avoid direct role-name leakage. It used all prompts rather than sampling. It used deterministic lexical-semantic proxies because no local independent LLM judge was available and API calls were outside the task constraints.

Inferred: this makes the study conservative for semantic richness and weaker for nuanced judgment. It is best treated as an initial validation screen before a true blinded human or multi-model rater study.

## Axis-Level Confidence Update

PC1: confidence is unchanged to slightly weakened by this validation. The target correlation is positive, but the matched-pair test is weak and an expertise/procedural proxy has a stronger off-axis relationship with PC1 than the direct PC1 rubric.

PC2: confidence remains low. The current formulation slightly outperforms the simpler PC2 alternatives in direct correlation, but the effect is modest and cross-validated regression is poor.

PC3: confidence remains moderate. It is the strongest direct rubric correlation in this validation, but the pairwise result is not strong enough to treat the interpretation as settled.

## Strongest Counterexamples

Observed: top matched-pair failures and off-axis correlations should be inspected before using the scores as confirmatory evidence. Examples include PC1 pairs where large PCA separation receives tied rubric scores, such as merchant versus novelist and amnesiac versus expatriate; PC2 pairs such as maverick versus virus and gossip versus rebel; and PC3 pairs such as familiar versus pilgrim and fixer versus refugee. See `axis_rubric_pairwise_validation.csv` for the full concrete pair list.

## Competing Explanations Still Viable

Unknown: prompt-register artifacts may explain part of the predictive signal. Unknown: LLM-assigned or lexical trait features may conflate role operationalization with target-model geometry. Unknown: a full rollout-response corpus could produce different results from the system-prompt corpus used here.

## Recommended Next Test

Run a true blinded rating study using an independent evaluator or human annotation on full rollout responses where available, then compare it against this prompt-corpus proxy. For PC2 specifically, use matched pairs and force raters to distinguish uncertainty exposure, immaturity, abstraction, and coherent action under unresolved uncertainty.
