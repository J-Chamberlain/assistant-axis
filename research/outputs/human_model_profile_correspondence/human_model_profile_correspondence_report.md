# AA-12 Follow-up 4: preregistered aggregate human ↔ reconciled-model profile correspondence

Date: 2026-09-13  
Track: Track 1 — independent profile-group correspondence  
Status: complete, aggregate-only  
Model used for analytical synthesis: GPT-5.5

## Executive result

The preregistered aggregate profile-shape test meets the frozen `STRONG AGGREGATE CORRESPONDENCE` rule. Across the 45 frozen direct bridge traits, the best injective four-family assignment occurs at eligible human K=10: mean Fisher-z=0.576571, back-transformed mean r=0.520169. None of 20,000 bridge-permutation draws produced an equal or larger maximum after repeating the full profile assignment and six-K search (p=0.000050).

This is strong evidence under the frozen test that the independently recovered human and reconciled-model aggregate profiles share nonrandom multivariate shape in the pre-existing semantic bridge. It is not evidence that the domains share psychometric scales, prevalences, natural personality types, individual geometry, or a causal latent mechanism.

The signal is not a clean one-to-one taxonomy. A and D have recognizable counterparts, B is marginal after family-specific search adjustment, and C's strongest unconstrained human counterpart is the same H10_I profile claimed much more strongly by D. The conservative 12-trait global signal is stronger, but its optimal assignment changes three of four K=10 pair identities. The most defensible conclusion is therefore strong aggregate organization with resolution-sensitive exact pairing.

## Frozen design and inputs

The method was frozen at commit `c71bcf9568cfed478d706bc559606de01af48f04` before any human/model correlation was calculated. Aggregate common-space profiles were frozen at `ba095f60783bd70f0003e14a88eb2e041b65cd42`, primary numerical results at `96c3e0d8595dfdfd15974c6bc66e31b58f0af065`, and robustness results at `e1d10da957ac9b31486bb17bcdaabf1306f29a03` before joint semantic inspection.

Human inputs are the unchanged AA-12 K=4–10 six-category observed-cell mixture profiles. Primary K values are exactly 4, 5, 6, 7, 8, and 10; K=9 remains diagnostic/ineligible. Model inputs are unchanged reconciled families A-D; E is secondary. The common vocabulary is exactly 45 `ACCEPT_DIRECT` mappings. The 12-trait sensitivity contains the frozen 9 high- and 3 moderate-support human measurements. No `ACCEPT_CLOSE` row, PC geometry, new item, new trait, or new mapping entered the analysis.

The SAPA normalization used the verified Harvard Dataverse V5 respondent artifact `sapaTempData696items08dec2013thru26jul2014.tab` (DOI `10.7910/DVN/SD7SVE`; SHA256 `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`). Its 23,679 rows were read only to estimate observed-only means and sample SDs for the 96 mapped items. Empty cells were omitted, no values were imputed, and only aggregate moments were saved.

Human trait values are equal-weight means of the frozen orientation-corrected item z-scores. Model values reuse within-model role-level trait standardization and frozen family aggregation; A-D are simple Qwen/LLaMA/Gemma means. E uses the already frozen cross-resolution recurrence Q07_G/L09_I/G06_A. The three single-item direct mappings (`curious`, `dramatic`, `patient`) remain included with their limitation flagged. The 30 redundant/broad mappings remain unweighted in the primary 45-trait vocabulary.

## Primary eligible-K scan

| Human K | Mean Fisher-z | Back-transformed mean r | Frozen human stability |
|---:|---:|---:|---|
| 4 | 0.267519 | 0.261315 | moderate; BIC/ICL anchor |
| 5 | 0.400591 | 0.380454 | moderate |
| 6 | 0.482629 | 0.448347 | moderate |
| 7 | 0.466360 | 0.435254 | low |
| 8 | 0.427786 | 0.403470 | low |
| 10 | **0.576571** | **0.520169** | low; predictive-likelihood anchor |

The maximizer is K=10, but this does not identify a true human K. The 20,000-draw null median maximum Fisher-z is 0.223367, its 95th percentile is 0.326369, and its 99.9th percentile is 0.444033; the observed 0.576571 lies beyond all draws.

## Primary K=10 injective assignment

| Model family | Distinct human profile | Pearson r | Spearman rho |
|---|---|---:|---:|
| MFamily_A | H10_C | 0.519496 | 0.472743 |
| MFamily_B | H10_J | 0.394457 | 0.501334 |
| MFamily_C | H10_G | 0.318677 | 0.283013 |
| MFamily_D | H10_I | 0.754532 | 0.734873 |

The assignment maximizes total raw Pearson r subject to four distinct human profiles; each K score is the mean Fisher transform of the four selected r values. No class-prevalence weight is used because the designed 275-role family proportions are not population prevalences.

## Family-specific max-search inference

| Family | Strongest eligible human counterpart | K | r | rho | Search-adjusted p | Passes p<=.05? |
|---|---|---:|---:|---:|---:|---|
| A | H06_A | 6 | 0.623662 | 0.592378 | 0.000150 | yes |
| B | H10_J | 10 | 0.394457 | 0.501334 | 0.053497 | no |
| C | H10_I | 10 | 0.555653 | 0.524128 | 0.000900 | yes |
| D | H10_I | 10 | 0.754532 | 0.734873 | 0.000050 | yes |

Three of four families pass the frozen family-specific rule. The C and D maxima collide on H10_I, which is exactly why the primary global assignment was injective. C's distinct injected counterpart H10_G is weaker; family-specific evidence for C should not be misread as evidence for a separate C-specific human group. B falls just outside the frozen .05 cutoff.

## Conservative 12-trait sensitivity

The complete 12-trait pipeline also maximizes at K=10: mean Fisher-z=0.998105, back-transformed mean r=0.760797, with 12 of 20,000 null maxima at least as large (p=0.000650).

| Model family | 12-trait optimal human profile | r | rho |
|---|---|---:|---:|
| A | H10_C | 0.926835 | 0.867133 |
| B | H10_A | 0.576900 | 0.671329 |
| C | H10_D | 0.335159 | 0.391608 |
| D | H10_J | 0.874178 | 0.678322 |

Only A retains the same optimal pair identity as the 45-trait assignment. Evaluated at the four primary 45-trait pair identities, all four 12-trait Pearson correlations are positive (A 0.926835, B 0.540080, C 0.072945, D 0.700408), so the preregistered directional-concordance condition passes. C is nearly absent on this fixed-pair sensitivity, and the substantial reassignment shows that exact correspondence depends on which measurement tier is emphasized. On family-specific 12-trait max tests, only A (p=0.000200) and D (p=0.004400) pass; B (p=0.279036) and C (p=0.798410) do not.

## Human-stability sensitivity and K=9 diagnostic

Restricting the 45-trait search to the moderate-stability K=4–6 solutions selects K=6: mean Fisher-z=0.482629, back-transformed mean r=0.448347, p=0.000050. This is 86.2% of the primary mean-r and exceeds the preregistered 80% retention criterion. The aggregate result therefore does not depend entirely on low-stability K=7/8/10 solutions, although the exact K=10 profile identities remain low-stability estimates.

K=9, calculated only after the primary freeze, gives mean Fisher-z=0.479777 and back-transformed mean r=0.446065. It remains `DIAGNOSTIC / INELIGIBLE` and affects no p-value, tier, assignment choice, or claim.

## Model-specific replication

The K=10 pair identities were held fixed; no model-specific reassignment was allowed.

| Pair | Consensus r | Qwen r | LLaMA r | Gemma r | Model range | Sign agreement |
|---|---:|---:|---:|---:|---:|---|
| A ↔ H10_C | 0.519496 | 0.399572 | 0.560230 | 0.561814 | 0.162242 | all positive |
| B ↔ H10_J | 0.394457 | 0.321845 | 0.363679 | 0.412255 | 0.090410 | all positive |
| C ↔ H10_G | 0.318677 | 0.140744 | 0.394513 | 0.367103 | 0.253769 | all positive |
| D ↔ H10_I | 0.754532 | 0.728865 | 0.766595 | 0.725305 | 0.041290 | all positive |

All pairs keep the same sign in Qwen, LLaMA, and Gemma, and leave-one-model-out correlations are also saved. D is nearly identical in strength across models. C is weakest in Qwen, but no single model reverses or solely creates the consensus result.

## Cross-resolution persistence and relaxed structure

The existing mutual-nearest human continuity graph gives a mixed picture:

- A's selected H10_C lineage extends through H09_D to H08_D and remains closest to A at all three resolutions.
- B's H10_J lineage extends through K=5–10, but it is closest to B only at H06_E; at K=10 H10_J is actually closer to D. This is an injective-assignment compromise, not a persistent B-specific lineage.
- C's H10_G lineage extends through K=6–10 but is closest to D at every node, so the selected C link is not persistent as an unconstrained nearest-family correspondence.
- D's H10_I has no mutual-nearest adjacent-K edge in the frozen continuity table. Its strong profile correlation is cross-model-replicated but not a traced neighboring-K lineage.

In relaxed many-to-one browsing, A and D absorb most human profiles. B is the nearest family for only H06_E, where its adjusted family p does not pass; C is nearest for H07_G, H08_H, and H10_F, with small top-two margins in all three. Seven human profiles have a preregistered ambiguous top-two margin <=0.10. This supports broad split/merge structure rather than a clean flat four-by-four taxonomy.

## MFamily_E secondary result

E's strongest eligible counterpart is H10_I (r=0.747647, rho=0.737969, adjusted p=0.000050). This is adjusted evidence for profile similarity, but it does not identify a distinct human counterpart: H10_I is already D's strongest and primary assigned profile. E remains a small, resolution-sensitive developmental/literal model outlier and cannot redefine the primary A-D family set.

The rejected creative/conceptual near-consensus region was not tested and was not promoted.

## Post-freeze descriptive interpretation

The numerical checkpoints preceded joint wording inspection. The separate semantic packet reports exact elevated/depressed traits and literal SAPA statements.

- A ↔ H10_C shares orderly, patient, prosocial, and low-manipulation/low-impulsivity patterning, with model-specific reserved/secular differences.
- B ↔ H10_J shares grandiose/dramatic patterning, but the model's creative/theatrical emphasis and the human profile's rebellious/manipulative emphasis differ substantially.
- C ↔ H10_G shares anxious/neurotic/emotional elevation, while reserved versus gregarious structure disagrees.
- D ↔ H10_I is the most coherent pair, combining negative-affect/antagonistic elevation with low calm, patience, optimism, and prosociality.

These are descriptive themes, not new class labels or construct-equivalence claims.

## Response-style caveat

No separate response-style-corrected correspondence statistic was run because no clean transform had been frozen in the 45-trait proxy space. Creating one after seeing the primary result would add discretionary modeling. The human construction subtracts observed item means, and Pearson profile correlation removes profile-wide additive elevation, but neither guarantees removal of relative response-style effects. The earlier human study's material response-style warning therefore remains active, alongside its observation that item-centering retained approximately 96.5%–99.0% of between-profile item-pattern variance.

## Decision-tier audit

| Frozen strong-tier condition | Result |
|---|---|
| 45-trait global p <= .05 | pass (0.000050) |
| At least 3/4 A-D family-specific adjusted positives | pass (3/4) |
| 12-trait directional concordance | pass (positive global score; 4/4 fixed pairs positive) |
| K=4–6 sensitivity retains recognizable correspondence | pass (p=0.000050; 86.2% mean-r retention) |

Result tier: **STRONG AGGREGATE CORRESPONDENCE under the frozen rule**, with material qualifications about B, C/D overlap, exact assignment sensitivity, low K=10 human stability, bridge redundancy, and response style.

## Boundaries

- No individual respondent was scored, imputed, or projected into model geometry.
- No respondent-level row, identifier, response mask, posterior membership, or derived profile was committed.
- No human/model prevalence comparison was made.
- No bridge row was added, removed, reweighted, or reoriented after results.
- No `ACCEPT_CLOSE` mapping entered the primary or conservative analysis.
- No model PC coordinate, interpretation, or context-enriched mapping entered the analysis.
- No human or model profile was refit, reclustered, merged, split, or relabeled.
- No new model inference, prompt generation, activation extraction, external model API, GPU, or RunPod work occurred.
- The result does not establish psychometric equivalence, shared mechanisms, population types, longitudinal change, wellbeing topology, or individual-level correspondence.

## Output guide

- `analysis_preregistration.md`: immutable pre-result method.
- `human_trait_profiles_45.csv`, `human_trait_profiles_12.csv`: aggregate human common-space profiles.
- `human_sapa_item_profile_values.csv`: aggregate latent item expectations and observed-only normalization metadata.
- `model_family_trait_profiles_45.csv`, `model_family_trait_profiles_12.csv`: frozen model-specific and consensus vectors.
- `profile_similarity_45.csv`, `profile_similarity_12.csv`: complete eligible-K matrices.
- `primary_assignments_by_k.csv`, `primary_assignments_12_by_k.csv`: injective assignments.
- `bridge_permutation_null_45.csv`, `bridge_permutation_null_12.csv`: complete maximum-stat nulls.
- `family_specific_results.csv`: primary family-specific adjusted results.
- `human_stability_sensitivity.csv`, `k9_diagnostic.csv`, `model_specific_replication.csv`, `cross_resolution_human_persistence.csv`, `relaxed_split_merge_browsing.csv`, `mfamily_e_secondary.csv`, and `response_style_sensitivity.csv`: frozen robustness and descriptive outputs.
- `human_sapa_item_visualization_order.csv`: searchable exact wording and frozen trait organization for the 96 unique items.
- `semantic_profile_summary.md`: post-freeze descriptive interpretation.
- `figures/`: 20 deterministic descriptive figures covering every required view.
