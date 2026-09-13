# AA-12 Human ↔ Model Correspondence Visualization and Inspection Packet

Date: 2026-09-13  
Status: complete reader-first visualization of a frozen inferential result  
Scope: aggregate human/model profiles only; no new correspondence test

## What this packet does

This packet makes the completed AA-12 follow-up-4 correspondence analysis inspectable without changing it. All displayed values are copied, checked, joined, ordered, or descriptively decomposed from committed aggregate artifacts under `research/outputs/human_model_profile_correspondence/`. No human profile was refit, no model was reclustered, no family or K was redefined, no bridge mapping changed, and no new null or matching objective was calculated.

The reader-first entry point is `human_model_profile_visualization.html`. It is a self-contained local HTML file: all CSS, JavaScript, source data, and 22 displayed PNGs are embedded, and it makes no network requests.

## Frozen result reproduced

The source-data extraction passed 20 exact numerical checks. The eligible human-K scores are:

| Human K | Mean Fisher-z | Back-transformed mean r | Frozen stability |
|---:|---:|---:|---|
| 4 | 0.267519 | 0.261315 | moderate; BIC/ICL anchor |
| 5 | 0.400591 | 0.380454 | moderate |
| 6 | 0.482629 | 0.448347 | moderate |
| 7 | 0.466360 | 0.435254 | low |
| 8 | 0.427786 | 0.403470 | low |
| 10 | 0.576571 | 0.520169 | low; predictive anchor and primary maximum |

K=9 is displayed only as `DIAGNOSTIC / INELIGIBLE` (`mean r=0.446065`) and never enters the primary scan.

The frozen K=10 injective assignment is reproduced exactly:

| Model family | Assigned human profile | Pearson r | Spearman ρ |
|---|---|---:|---:|
| MFamily_A | H10_C | 0.519496 | 0.472743 |
| MFamily_B | H10_J | 0.394457 | 0.501334 |
| MFamily_C | H10_G | 0.318677 | 0.283013 |
| MFamily_D | H10_I | 0.754532 | 0.734873 |

The complete 20,000-draw maximum-statistic null is reproduced without rerunning permutations. Its median is 0.223367, its 95th percentile is 0.326369, its 99.9th percentile is 0.444033, and no null maximum reaches the observed Fisher-z of 0.576571. The frozen empirical p-value remains `1 / 20,001 = 0.000050`.

The packet also reproduces:

- family-specific maxima: A–H06_A (`r=0.623662`, adjusted `p=0.000150`), B–H10_J (`r=0.394457`, `p=0.053497`), C–H10_I (`r=0.555653`, `p=0.000900`), and D–H10_I (`r=0.754532`, `p=0.000050`);
- the independent 12-trait result (`K=10`, mean `r=0.760797`, adjusted `p=0.000650`);
- the moderate-stability K=4–6 result (`K=6`, mean `r=0.448347`, adjusted `p=0.000050`);
- secondary MFamily_E–H10_I (`r=0.747647`, adjusted `p=0.000050`); and
- every fixed K=10 pair's consensus, Qwen, LLaMA, and Gemma correlations, with no model-specific reassignment.

## Figure guide

1. `01_primary_matched_shapes_canonical`: A–D human/model profiles over the same canonical 45-trait order.
2. `01b_primary_matched_shapes_measurement_grouped`: the same values grouped only by frozen pre-result measurement-support metadata.
3. `02_trait_decomposition_all_traits`: all 45 centered covariance contributions and signed human-minus-model differences.
4. `02b_top_trait_drivers`: the eight largest positive contribution terms and eight largest absolute disagreements for each pair.
5. `03_primary_pair_heatmap`: a one-page paired model/human heatmap, with the 12-trait core marked.
6. `04_k_progression`: eligible-K global scores, stability ratings, K4/K10 anchors, and visibly excluded K9.
7. `05_family_best_across_k`: unconstrained best available human-profile correlation for each A–D family at each eligible K.
8. `06_assignment_evolution_matrix`: frozen injective assignments across K, with displaced unconstrained maxima noted.
9. `07_human_profile_continuity_reused`: the prior frozen mutual-nearest human-continuity view, reused byte-for-byte.
10. `08_similarity_matrix_k04` through `k10`: all human profiles against A–D and secondary E, marking injective and unconstrained matches.
11. `09_cde_competition`: the deterministically selected K10 C/D/E region and the H10_I/C/D/E trait shapes, with H10_G as the injective C comparator.
12. `10_ad_exemplars`: A–H10_C versus stronger A–H06_A, and the strong D–H10_I pair.
13. `11_trait_set_comparison`: separate 45/12-trait injective assignments and the fixed 45-trait pairs evaluated on the 12-trait core.
14. `12_model_specific_replication_reused`: the prior fixed-pair consensus/Qwen/LLaMA/Gemma plot, reused byte-for-byte.
15. `13_primary_permutation_null`: annotated full-search null with median, 95th, 99.9th, and observed lines.
16. `14_family_specific_statistics`: family-specific maximum r and correctly search-adjusted p-values.
17. `15_sapa_language_profiles`: all 96 exact SAPA item wordings for H10_C, H10_J, H10_G, H10_I, and A's strongest counterpart H06_A.

Every newly generated substantive plot is available in PNG and SVG. `figure_inventory.csv` records exact source tables, hashes, sizes, and whether a figure was created or reused.

## What the plots make visible

These are descriptive decompositions of the frozen result, not new tested claims.

### MFamily_A

A has a recognizable broad correspondence that is stronger at H06_A/K6 (`r=0.624`) than at its primary maximizing-K counterpart H10_C (`r=0.519`). Positive covariance terms include patient, conscientious, agreeable, manipulative, traditional, rebellious, meticulous, and altruistic. Large differences remain for secular, emotional, reserved, calm, empathetic, playful, artistic, and resilient. The H08_D→H09_D→H10_C frozen lineage remains closest to A, making broad A persistence more visually stable than one exact profile identity.

### MFamily_B

B is positive but visibly weaker and resolution-sensitive. Its strongest pair is the primary H10_J pair (`r=0.394`), but the family-specific adjusted result is marginal (`p=0.053497`). Grandiose, agreeable, patient, traditional, theatrical, empathetic, optimistic, and dramatic contribute positively; secular, melancholic, artistic, dramatic, theatrical, forgiving, grandiose, and altruistic also contain large scale-specific disagreements.

### MFamily_C

C's primary injective H10_G match is modest (`r=0.319`), while its unconstrained maximum is H10_I (`r=0.556`). Anxious, neurotic, stoic, dominant, resilient, temperamental, conscientious, and calm contribute positively in the primary pair, while gregarious/extroverted/reserved differences are conspicuous. The heatmaps show that C's significant family-level maximum does not establish a distinct human counterpart because D also selects H10_I.

### MFamily_D

D–H10_I is the clearest pair (`r=0.755`, `ρ=0.735`) and is consistently positive in Qwen (`r=0.729`), LLaMA (`r=0.767`), and Gemma (`r=0.725`). Patient, serene, calm, resilient, stoic, temperamental, conscientious, and pessimistic are large positive covariance contributors. Even this strong shape match contains large absolute disagreements, notably for altruistic, agreeable, assertive, judgmental, cynical, callous, paranoid, and serene.

### MFamily_E

Secondary E also selects H10_I (`r=0.748`). The dedicated panel shows that E's apparent human correspondence is not a distinct fifth region: it competes directly with D and C around H10_I. E remains secondary and excluded from the primary A–D statistic.

### Resolution, measurement, and model replication

- The global score generally rises from K4 to K10 but is not monotone; K7 and K8 fall below K6 before K10 increases.
- The stable K4–6 subset retains 86.2% of the primary mean-r and remains separated from its preregistered null.
- The 12-trait global result is directionally strong, but only A retains the same K10 assigned profile. All four fixed 45-trait pairs remain Pearson-positive on the 12 traits, while C's fixed-pair value is near zero (`r=0.072945`).
- D is highly consistent across all three models. C is materially weaker in Qwen; A and B retain positive signs in every model.
- The observed Fisher-z is well beyond the frozen null's 99.9th percentile, visually clarifying that `p=0.000050` is a full-search maximum-statistic result rather than a generic correlation p-value.

## HTML controls

The standalone HTML provides:

- A–D family selection;
- canonical versus frozen measurement-grouped trait ordering;
- consensus/Qwen/LLaMA/Gemma fixed-pair profile toggling;
- selectable K4/K5/K6/K7/K8/K10 full similarity matrices;
- 45-versus-12 assignment toggling;
- family-filtered top-contributor/disagreement tables; and
- exact-wording SAPA search with human-profile selection.

Headless Google Chrome rendered the file locally, executed the embedded JavaScript, populated the interactive SVG and tables, and produced a 1440×1200 screenshot. The source contains 22 embedded PNG data URIs and no external image source.

## Reproducibility

From the repository root:

```bash
../assistant-axis/.venv/bin/python research/outputs/human_model_profile_visualization/analysis/extract_visualization_data.py
../assistant-axis/.venv/bin/python research/outputs/human_model_profile_visualization/analysis/build_static_figures.py
../assistant-axis/.venv/bin/python research/outputs/human_model_profile_visualization/analysis/build_html_report.py
```

The source-data, static-figure, figure-inventory, and HTML hashes are stable across immediate deterministic reruns.

## Boundaries

- Aggregate class/family profiles only; no respondent projection, IDs, rows, masks, posteriors, scores, or imputations.
- No new correspondence test, matching optimization, bridge permutation, K selection, family construction, human refit, or model reclustering.
- No bridge, orientation, reverse-scoring, normalization, or eligibility change; no `ACCEPT_CLOSE` or context/PC-informed remapping.
- Correlation is relative profile-shape similarity, not percent identity, variance explained, prevalence, probability of equivalence, or psychometric equivalence.
- Trait-level contributions are descriptive decomposition terms, not independent hypothesis tests.
- No new inference, prompts, activation extraction, external model API, GPU, or RunPod work.
- No new scientific claim is introduced by this visualization packet.
