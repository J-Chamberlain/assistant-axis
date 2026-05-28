# Persona Explanation Residual Rankings

Date: 2026-05-28
Model used: GPT-5.5 Standard

## 1. Research Question

Which personas are well explained by the current iterative latent-feature vocabulary, and which remain diagnostic residual cases relative to activation PCA geometry?

## 2. Method

The script reconstructs the final retained outer-loop feature model from `outer_loop_master_log.json`, uses the original deterministic split code, and ranks all personas with PCA coordinates by residual norm in activation PCA3D space. For personas that appeared in one or more held-out splits, the primary residual is the mean held-out residual across those splits. For personas never held out by the five deterministic splits, the table uses an apparent full-model residual and marks `prediction_source` accordingly.

Personas ranked: 273. Personas with held-out prediction evidence: 221. Personas without held-out split coverage: 52. Retained dimensions: 31.

Metadata gaps: No explicit all-persona final prediction artifact was stored by the original outer loop; this script reconstructs predictions from retained dimensions. Split-level held-out predictions were not stored by the original outer loop; this script recomputes them using the published deterministic split seeds. Anchor/bridge status is derived from stable_anchor_roles.csv and bridge_roles.csv rather than a dedicated outer-loop artifact.

## 3. Most Effectively Explained Personas

| persona | final_model_residual | semantic_baseline_residual | residual_improvement | activation_cluster | prediction_source |
| --- | --- | --- | --- | --- | --- |
| designer | 3.685 | 13.607 | 9.922 | procedural_professional | mean_heldout_across_splits |
| nomad | 4.504 | 8.152 | 3.648 | grounded_social | mean_heldout_across_splits |
| curator | 4.901 | 18.153 | 13.252 | procedural_professional | mean_heldout_across_splits |
| chemist | 6.380 | 8.827 | 2.447 | procedural_professional | apparent_full_model_no_heldout_split |
| tulpa | 6.480 | 8.266 | 1.786 | grounded_social | apparent_full_model_no_heldout_split |
| accountant | 6.655 | 17.272 | 10.618 | editorial | mean_heldout_across_splits |
| economist | 6.773 | 22.026 | 15.252 | procedural_professional | apparent_full_model_no_heldout_split |
| scheduler | 6.924 | 14.144 | 7.220 | procedural_professional | mean_heldout_across_splits |
| secretary | 7.323 | 19.357 | 12.033 | editorial | mean_heldout_across_splits |
| grader | 7.671 | 10.676 | 3.005 | editorial | mean_heldout_across_splits |
| jester | 8.562 | 35.910 | 27.347 | trickster_chaos | mean_heldout_across_splits |
| anarchist | 8.563 | 9.884 | 1.321 | procedural_professional | mean_heldout_across_splits |
| writer | 8.716 | 17.405 | 8.689 | procedural_professional | mean_heldout_across_splits |
| mentor | 9.123 | 6.994 | -2.129 | procedural_professional | apparent_full_model_no_heldout_split |
| programmer | 9.156 | 11.615 | 2.459 | procedural_professional | mean_heldout_across_splits |

These are best described as well explained by the current feature vocabulary, not inherently simple or finally interpreted.

## 4. Least Effectively Explained Personas

| persona | final_model_residual | semantic_baseline_residual | residual_improvement | activation_cluster | heldout_frequency |
| --- | --- | --- | --- | --- | --- |
| procrastinator | 73.419 | 76.036 | 2.617 | other | 1 |
| toddler | 66.582 | 64.162 | -2.420 | other | 1 |
| teenager | 59.415 | 65.433 | 6.018 | other | 2 |
| comedian | 59.216 | 50.030 | -9.186 | trickster_chaos | 1 |
| cyborg | 59.193 | 59.045 | -0.148 | procedural_professional | 1 |
| vampire | 57.146 | 54.089 | -3.057 | mythic_spiritual | 2 |
| smuggler | 54.031 | 69.901 | 15.870 | grounded_social | 2 |
| sage | 53.945 | 66.239 | 12.295 | mythic_spiritual | 2 |
| ancient | 53.524 | 55.853 | 2.329 | mythic_spiritual | 1 |
| amateur | 53.515 | 46.753 | -6.762 | grounded_social | 2 |
| caveman | 52.856 | 52.408 | -0.448 | trickster_chaos | 2 |
| poet | 52.688 | 75.410 | 22.722 | mythic_spiritual | 0 |
| infant | 52.199 | 56.267 | 4.068 | other | 2 |
| gossip | 51.205 | 75.121 | 23.916 | trickster_chaos | 0 |
| bard | 50.160 | 68.095 | 17.935 | mythic_spiritual | 2 |

These are diagnostic residual cases: the current dimensions poorly explain their activation placement relative to other personas.

## 5. Personas Most Improved Over Semantic Baseline

| persona | residual_improvement | residual_improvement_percent | final_model_residual | semantic_baseline_residual | activation_cluster |
| --- | --- | --- | --- | --- | --- |
| jester | 27.347 | 76.156 | 8.562 | 35.910 | trickster_chaos |
| robot | 26.346 | 55.573 | 21.062 | 47.408 | procedural_professional |
| wind | 26.271 | 52.056 | 24.196 | 50.467 | mythic_spiritual |
| gossip | 23.916 | 31.837 | 51.205 | 75.121 | trickster_chaos |
| poet | 22.722 | 30.132 | 52.688 | 75.410 | mythic_spiritual |
| demon | 22.422 | 61.540 | 14.013 | 36.435 | mythic_spiritual |
| pragmatist | 22.222 | 62.393 | 13.394 | 35.616 | procedural_professional |
| echo | 20.203 | 42.296 | 27.563 | 47.766 | mythic_spiritual |
| wanderer | 20.026 | 63.137 | 11.692 | 31.718 | mythic_spiritual |
| summarizer | 19.396 | 52.430 | 17.598 | 36.994 | editorial |
| daredevil | 19.183 | 41.360 | 27.198 | 46.381 | combative_iconoclast |
| guru | 18.612 | 59.733 | 12.547 | 31.158 | mythic_spiritual |
| shaman | 18.555 | 63.336 | 10.741 | 29.297 | mythic_spiritual |
| bard | 17.935 | 26.338 | 50.160 | 68.095 | mythic_spiritual |
| aberration | 17.502 | 54.002 | 14.908 | 32.411 | mythic_spiritual |

Positive values mean the latent-feature model predicts activation placement better than the semantic baseline for that persona.

## 6. Personas Worsened Relative to Semantic Baseline

| persona | residual_improvement | residual_improvement_percent | final_model_residual | semantic_baseline_residual | activation_cluster |
| --- | --- | --- | --- | --- | --- |
| futurist | -26.250 | -388.324 | 33.010 | 6.760 | procedural_professional |
| veterinarian | -26.122 | -247.483 | 36.677 | 10.555 | procedural_professional |
| forecaster | -23.457 | -166.320 | 37.560 | 14.103 | procedural_professional |
| coordinator | -18.523 | -102.421 | 36.609 | 18.086 | procedural_professional |
| producer | -16.241 | -88.634 | 34.565 | 18.324 | procedural_professional |
| psychologist | -15.749 | -79.008 | 35.683 | 19.934 | procedural_professional |
| marketer | -15.545 | -109.215 | 29.779 | 14.233 | procedural_professional |
| screener | -15.277 | -723.837 | 17.388 | 2.111 | editorial |
| rogue | -15.269 | -69.781 | 37.151 | 21.881 | trickster_chaos |
| void | -14.639 | -61.319 | 38.513 | 23.874 | mythic_spiritual |
| journalist | -14.615 | -56.865 | 40.317 | 25.702 | procedural_professional |
| zeitgeist | -14.515 | -47.705 | 44.943 | 30.427 | procedural_professional |
| interpreter | -13.958 | -127.591 | 24.898 | 10.940 | procedural_professional |
| pilot | -13.741 | -146.144 | 23.143 | 9.402 | procedural_professional |
| improviser | -13.202 | -57.340 | 36.228 | 23.025 | grounded_social |

Negative values mean the semantic baseline overpredicts or underpredicts activation placement less badly than the current feature vocabulary.

## 7. Recurrent High-Residual Personas

| persona | mean_residual_across_splits | residual_std_across_splits | heldout_frequency | activation_cluster | anchor_or_bridge_status |
| --- | --- | --- | --- | --- | --- |
| teenager | 59.415 | 1.204 | 2 | other | semantic_bridge_3 |
| vampire | 57.146 | 0.889 | 2 | mythic_spiritual | semantic_bridge_3 |
| smuggler | 54.031 | 7.540 | 2 | grounded_social | semantic_bridge_3 |
| sage | 53.945 | 3.364 | 2 | mythic_spiritual | semantic_bridge_high_5 |
| amateur | 53.515 | 1.942 | 2 | grounded_social | semantic_bridge_2 |
| caveman | 52.856 | 3.711 | 2 | trickster_chaos | semantic_bridge_3 |
| infant | 52.199 | 3.182 | 2 | other | stable_anchor |
| bard | 50.160 | 3.499 | 2 | mythic_spiritual | semantic_bridge_3 |
| hermit | 49.561 | 1.979 | 2 | mythic_spiritual | semantic_bridge_3 |
| adolescent | 49.116 | 3.432 | 3 | other | semantic_bridge_3 |
| bartender | 46.975 | 2.577 | 2 | grounded_social | semantic_bridge_3 |
| pirate | 43.110 | 0.800 | 2 | trickster_chaos | stable_anchor |
| mechanic | 42.957 | 1.877 | 4 | procedural_professional | semantic_bridge_high_5 |
| journalist | 40.317 | 2.036 | 2 | procedural_professional | semantic_bridge_3 |
| predator | 39.615 | 2.041 | 3 | mythic_spiritual | semantic_bridge_3 |

This section emphasizes personas with repeated held-out evidence rather than only apparent full-model residuals.

## 8. Conceptual Interpretation

The ranking supports a bounded interpretation: some personas are well explained by the current feature vocabulary, especially where procedural, institutional, assistant-adjacent, or interactional signals map cleanly onto activation PCA placement. High-residual personas should be treated as diagnostic cases where current dimensions are incomplete, too coarse, or misweighted. The results do not prove final meanings of the dimensions and do not imply any persona is inherently inexplicable.

## 9. Recommended Diagnostic Follow-Ups

- Add a sixth or leave-one-role-out split pass if every persona needs pure held-out coverage.
- Inspect least-explained personas by activation cluster to determine whether residuals concentrate in developmental, mythic, social, or sparse-label regions.
- Run a targeted paired-persona test for high-residual conceptual families, especially where semantic baseline and latent-feature predictions disagree.
- Replace lexical feature coding with blind model-coded ordinal features and compare whether the same residual cases remain.
- Track whether anchor or bridge roles are systematically overrepresented among high residuals.
