# Latent Feature Framing Ablation Report

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Script author model: GPT-5.5 Standard via Codex

## 1. Question

This ablation asks whether different constrained interpretive framings improve held-out prediction of continuous persona activation geometry beyond semantic cluster baselines. It uses existing local artifacts only. No new activations, pods, or model calls were run.

The primary target is PCA3D activation-coordinate prediction using the same deterministic split seed as the first latent-feature loop. Cluster prediction is reported as secondary because the first loop already showed that hard activation-cluster accuracy is less sensitive than continuous geometry.
The PCA artifact contains 273 personas with coordinates, so this run evaluates 73 held-out personas after applying the same deterministic split seed.

## 2. Split Discipline

The script reuses the first-loop deterministic split seed, `latent_feature_loop_v1_2026-05-28`. Feature rubrics are fixed before held-out coding. Held-out persona text is coded using the frozen rubric, while held-out PCA coordinates and activation outcomes are used only for evaluation.

## 3. Feature Families

The tested families are motivational, interactional, procedural/operating-mode, narrative-causal, all four framings combined, and the prior first-loop feature set. Each family is converted into ordinal 0-3 pattern-derived features. The semantic baseline uses original-prompt, no-label-prompt, and role-name k=7 cluster one-hot features.

## 4. Results Table

| Framing | PCA3D R2 | Delta | PC1 R2 | PC2 R2 | PC3 R2 | Cluster Acc | NN Preserve |
|---|---:|---:|---:|---:|---:|---:|---:|
| prior_first_loop | 0.436 | +0.114 | 0.499 | 0.353 | 0.406 | 0.630 | 0.167 |
| all_framings | 0.405 | +0.083 | 0.465 | 0.328 | 0.377 | 0.603 | 0.175 |
| procedural | 0.373 | +0.051 | 0.410 | 0.311 | 0.387 | 0.616 | 0.159 |
| narrative_causal | 0.355 | +0.033 | 0.390 | 0.307 | 0.344 | 0.630 | 0.170 |
| motivational | 0.345 | +0.024 | 0.390 | 0.290 | 0.319 | 0.644 | 0.184 |
| interactional | 0.333 | +0.011 | 0.345 | 0.294 | 0.383 | 0.616 | 0.181 |
| semantic_baseline | 0.322 | +0.000 | 0.353 | 0.276 | 0.321 | 0.616 | 0.159 |

## 5. Which Framing Best Improves Held-Out Activation-Axis Prediction?

The best framing is `prior_first_loop`, with held-out PCA3D R2 0.436 versus semantic baseline R2 0.322. The improvement is +0.114.

This is a held-out predictive result, not evidence that the framing is causally true.

## 6. Does Improvement Concentrate on PC1, PC2, or PC3?

For the best framing, per-axis R2 is PC1 0.499, PC2 0.353, and PC3 0.406. The strongest concentration is on PC1.

## 7. Do Motivational Features Outperform Semantic Features?

Yes in this split: `motivational` reaches PCA3D R2 0.345, improving over semantic baseline by +0.024.

## 8. Do Procedural Features Outperform Motivational Features?

Yes. `procedural` reaches R2 0.373, above `motivational` at R2 0.345.

## 9. Do Interactional Features Explain Bridge-Role Behavior?

`interactional` has top-20 high-residual overlap with baseline of 0.900 and residual norm reduction +0.566. Lower overlap and positive reduction would indicate better bridge-role explanation.

## 10. Does Narrative-Causal Framing Explain High-Residual Personas?

`narrative_causal` changes residual-proxy R2 by -0.047 and mean PCA residual norm by +0.482. This is the bounded evidence for whether causal-backstory features explain high-residual personas.

## 11. Are Cluster Predictions Still Weak?

The semantic baseline cluster accuracy is 0.616. The best framing's cluster accuracy is 0.630, a delta of +0.014. This keeps cluster prediction secondary relative to continuous geometry.

## 12. Personas That Improve Most

| Role | Cluster | Baseline Residual | Best Residual | Reduction |
|---|---|---:|---:|---:|
| proofreader | editorial | 30.258 | 13.820 | +16.439 |
| sage | mythic_spiritual | 72.129 | 55.768 | +16.361 |
| bard | mythic_spiritual | 66.496 | 51.222 | +15.274 |
| poet | mythic_spiritual | 87.238 | 73.789 | +13.449 |
| expatriate | procedural_professional | 38.049 | 26.711 | +11.339 |
| prey | grounded_social | 25.821 | 14.697 | +11.124 |
| technologist | procedural_professional | 50.681 | 40.008 | +10.673 |
| hermit | mythic_spiritual | 52.285 | 42.410 | +9.875 |
| purist | procedural_professional | 25.192 | 15.985 | +9.208 |
| exile | mythic_spiritual | 32.363 | 23.474 | +8.888 |

## 13. Personas That Remain Poorly Predicted

| Role | Cluster | Best Residual | Baseline Rank | Best Rank |
|---|---|---:|---:|---:|
| poet | mythic_spiritual | 73.789 | 1 | 1 |
| toddler | other | 63.503 | 5 | 2 |
| adolescent | other | 58.566 | 4 | 3 |
| sage | mythic_spiritual | 55.768 | 2 | 4 |
| bard | mythic_spiritual | 51.222 | 3 | 5 |
| bartender | grounded_social | 48.879 | 6 | 6 |
| ancient | mythic_spiritual | 47.362 | 8 | 7 |
| pirate | trickster_chaos | 46.131 | 11 | 8 |
| ascetic | mythic_spiritual | 44.144 | 9 | 9 |
| realist | procedural_professional | 43.677 | 15 | 10 |

## 14. Personas That Worsen Most

| Role | Cluster | Baseline Residual | Best Residual | Reduction |
|---|---|---:|---:|---:|
| forecaster | procedural_professional | 11.547 | 25.775 | -14.228 |
| judge | procedural_professional | 10.992 | 25.034 | -14.042 |
| whale | mythic_spiritual | 17.373 | 25.942 | -8.569 |
| builder | procedural_professional | 9.814 | 17.784 | -7.971 |
| mediator | procedural_professional | 5.051 | 12.995 | -7.944 |
| producer | procedural_professional | 11.740 | 18.231 | -6.491 |
| dispatcher | procedural_professional | 10.762 | 16.394 | -5.632 |
| tree | mythic_spiritual | 24.655 | 30.274 | -5.619 |
| eldritch | mythic_spiritual | 32.800 | 37.619 | -4.819 |
| realist | procedural_professional | 39.652 | 43.677 | -4.025 |

## 15. Implication for Paper 1.5

The ablation supports the Paper 1.5 claim in a limited form: activation geometry is not merely semantic topology, and some operationalized behavioral framings can improve held-out continuous prediction. The result is strongest when evaluated as continuous PCA geometry rather than as hard cluster labels.

The correct interpretation is not that these dimensions reveal the real structure of the model. The correct interpretation is that certain constrained feature families predict held-out activation geometry better than semantic labels alone, which makes them candidates for more rigorous follow-up with repeated splits, stronger coders, and multi-model hypothesis generation.

## 16. Limitations

The current operationalization is lexical and prompt-pattern based. It does not yet use blind classifier coding or external embeddings. The split is a single deterministic split. The features are interpretable but coarse, and the code should be treated as a first ablation harness rather than a final explanatory model.

## 17. Next Step

The next step is to repeat this ablation with live model-generated rubrics from GPT-5.5, Claude Sonnet, and another frontier model, then compare predictive convergence rather than rhetorical similarity.