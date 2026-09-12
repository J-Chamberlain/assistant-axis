# Externally Anchored Big Five Audit

## Scientific answer

Yes: a substantially stricter, geometry-blind, human/psychometric-anchored Big Five construction recovers recognizable structure in all three persona spaces. The clearest focal result is Qwen Agreeableness versus negative PC3. Under the frozen `ACCEPT_DIRECT` construction, the activation-direction cosine is **-0.847133**, role-score Pearson **r=-0.881714**, Spearman **rho=-0.837526**, and single-domain **R2=0.777420**. In the joint five-domain model the standardized Agreeableness coefficient is **-0.894047**, its in-sample partial R2 is **0.533524**, and its leakage-safe held-out partial R2 is **0.524122**. The single-domain fit leaves **22.258%** of Qwen PC3 variance unexplained, so the warranted conclusion is that negative PC3 has a strong Agreeableness-related component, not that PC3 simply *is* Agreeableness.

This relationship is robust to the frozen facet construction in Qwen, but it is not a universal PC3 identity. Gemma shows a moderate negative-PC3 relationship; Llama does not, and Llama Agreeableness instead aligns strongly with negative PC2. Cross-model signs use the project's established corresponding-PC orientation, but corresponding axes are not assumed to have identical psychological semantics.

## Startup and preregistered freeze

Startup passed against the four canonical raw-master files before work began and again after the AA-1 dependency clarification. The starting canonical commit is `7914d01f7d9c23060fe199815a90e547241d9682`.

The mapping was completed before any new geometry analysis and frozen at commit `636c5c1d9b832a1199e8d5b35dea993a41f94d4b` (timestamp `2026-09-11T22:58:36Z`). The mapping generator reads only canonical trait definitions, the reviewed SAPA bridge, and frozen external taxonomy metadata. It has no persona coordinate, PC ranking, score, cluster, surface, ridge, screenshot, or AA-4 input.

The three new constructions are:

- **Human-anchored strict:** 42 traits; only defensible Big Five assignments among reviewed SAPA `ACCEPT_DIRECT` links.
- **Human-anchored extended:** 67 traits; the strict set plus 25 separately flagged defensible `ACCEPT_CLOSE` links.
- **External-taxonomy expanded:** all 240 traits reviewed against the IPIP-NEO hierarchy; 109 high-confidence direct indicators included, 75 proxy candidates recorded but excluded, and 56 traits left unmapped.

The historical hand-predeclared activation composite is retained unchanged as a comparator, not used to tune A/B/C.

## External psychometric anchor

The principal taxonomy is the public-domain IPIP/IPIP-NEO five-domain, 30-facet hierarchy. Exact URLs, access timestamp, retrieved byte counts, and SHA256 hashes are in `external_big_five_reference_manifest.json`.

- [IPIP NEO combined domain/facet key](https://ipip.ori.org/newNEOKey.htm)
- [IPIP NEO facet key](https://ipip.ori.org/newNEOFacetsKey.htm)
- [IPIP NEO domain key](https://ipip.ori.org/newNEODomainsKey.htm)
- [Johnson IPIP-NEO-120 facet key](https://ipip.ori.org/30FacetNEO-PI-RItems.htm), associated with Johnson (2014), *Journal of Research in Personality* 51, 78–89, [doi:10.1016/j.jrp.2014.05.003](https://doi.org/10.1016/j.jrp.2014.05.003)
- [IPIP public-domain permission statement](https://ipip.ori.org/newPermission.htm)

No proprietary NEO item bank is reproduced. “Openness” is reported as Openness to Experience / Intellect; Neuroticism is the inverse-pole framing of Emotional Stability.

## Focal Agreeableness–PC3 test

| Model | Direction cosine | Pearson r | Spearman rho | Single R2 | Joint standardized beta | Partial R2 | Held-out partial R2 | Remaining single-domain variance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen | -0.847133 | -0.881714 | -0.837526 | 0.777420 | -0.894047 | 0.533524 | 0.524122 | 0.222580 |
| Llama | -0.192846 | -0.163861 | -0.018593 | 0.026850 | -0.278558 | 0.030692 | 0.005790 | 0.973150 |
| Gemma | -0.690086 | -0.570857 | -0.524702 | 0.325878 | -0.662888 | 0.223282 | 0.199173 | 0.674122 |

For Qwen PC3 the competing strict-domain single-predictor R2 values are Openness 0.117726, Conscientiousness 0.000146, Extraversion 0.000084, Agreeableness 0.777420, and Neuroticism 0.112668. Agreeableness is therefore the dominant Big Five correlate of Qwen PC3 under the frozen primary construction.

For Llama PC3, Extraversion is stronger (r=-0.612485, R2=0.375137) than Agreeableness. For Gemma PC3, Agreeableness is the strongest of the five focal single-domain comparisons, but its relationship is moderate and Gemma Agreeableness also correlates with PC1 (r=0.639). This is replication of a broad Big Five-related organization, not replication of identical PC3 semantics.

## Construction sensitivity for Qwen Agreeableness–PC3

| Construction | Direction cosine | Pearson r | Spearman rho | Single R2 | Joint beta | Partial R2 | Held-out partial R2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Human-anchored strict | -0.847133 | -0.881714 | -0.837526 | 0.777420 | -0.894047 | 0.533524 | 0.524122 |
| Human-anchored extended | -0.871309 | -0.894312 | -0.854241 | 0.799793 | -0.869856 | 0.448076 | 0.441772 |
| External-taxonomy expanded | -0.831767 | -0.827072 | -0.760112 | 0.684048 | -0.838843 | 0.612892 | 0.609711 |
| Historical hand-predeclared | -0.845722 | -0.907201 | -0.879299 | 0.823014 | -1.399874 | 0.829692 | 0.825128 |

The direct-only and direct+close Qwen Agreeableness directions have cosine 0.988055 and role-score Pearson 0.997526. Across strict Agreeableness leave-one-trait omissions, the minimum role-score Pearson is 0.986251. Leaving out an entire facet has minimum direction cosine 0.931411 and role-score Pearson 0.930403; A4 Cooperation is the largest facet-level contributor. Positive-only versus bipolar Agreeableness retains direction cosine 0.948874 and role-score Pearson 0.903189. The focal conclusion is therefore not driven by the single `agreeable` trait, although the Cooperation facet materially contributes.

## Primary strict geometry across all domains

The table reports each domain's strongest absolute role-score association and the activation-direction cosine to that same PC loading. Full PC1/PC2/PC3 Pearson, Spearman, and direction-cosine tables are saved separately.

| Model | Domain | Strongest PC | Pearson r | Spearman rho | Direction cosine |
|---|---|---|---:|---:|---:|
| Qwen | Openness | PC1 | -0.704 | -0.748 | -0.305 |
| Qwen | Conscientiousness | PC1 | 0.748 | 0.821 | 0.526 |
| Qwen | Extraversion | PC1 | -0.817 | -0.853 | -0.575 |
| Qwen | Agreeableness | PC3 | -0.882 | -0.838 | -0.847 |
| Qwen | Neuroticism | PC1 | -0.758 | -0.834 | -0.532 |
| Llama | Openness | PC1 | -0.522 | -0.664 | -0.223 |
| Llama | Conscientiousness | PC2 | -0.951 | -0.950 | -0.756 |
| Llama | Extraversion | PC2 | 0.623 | 0.759 | 0.300 |
| Llama | Agreeableness | PC2 | -0.814 | -0.816 | -0.562 |
| Llama | Neuroticism | PC2 | 0.959 | 0.952 | 0.718 |
| Gemma | Openness | PC1 | -0.454 | -0.574 | -0.154 |
| Gemma | Conscientiousness | PC2 | -0.860 | -0.726 | -0.623 |
| Gemma | Extraversion | PC2 | 0.663 | 0.573 | 0.506 |
| Gemma | Agreeableness | PC1 | 0.639 | 0.718 | 0.317 |
| Gemma | Neuroticism | PC2 | 0.760 | 0.604 | 0.667 |

The role-score/direction-cosine gap is scientifically important. For example, Qwen Openness has r=-0.704 with PC1 but direction cosine only -0.305. Persona occupancy can amplify a score-coordinate correlation even when the underlying activation direction is not close to the PCA loading. Qwen Agreeableness–PC3 is unusual here because both levels are large.

## Held-out five-domain PC description

Ten-fold fixed-seed out-of-fold R2 for joint linear models:

| Construction | Model | PC1 | PC2 | PC3 | Condition number | Maximum VIF |
|---|---|---:|---:|---:|---:|---:|
| Strict | Qwen | 0.732 | 0.612 | 0.905 | 17.58 | 42.56 |
| Strict | Llama | 0.479 | 0.952 | 0.615 | 11.94 | 29.58 |
| Strict | Gemma | 0.669 | 0.763 | 0.722 | 11.01 | 21.37 |
| Extended | Qwen | 0.713 | 0.378 | 0.935 | 20.78 | 55.51 |
| Extended | Llama | 0.518 | 0.972 | 0.457 | 10.02 | 22.26 |
| Extended | Gemma | 0.602 | 0.588 | 0.763 | 11.85 | 19.82 |
| External expanded | Qwen | 0.842 | 0.736 | 0.922 | 17.13 | 40.51 |
| External expanded | Llama | 0.707 | 0.969 | 0.414 | 11.02 | 26.86 |
| External expanded | Gemma | 0.751 | 0.812 | 0.662 | 10.79 | 18.35 |
| Historical | Qwen | 0.910 | 0.850 | 0.947 | 25.97 | 101.49 |
| Historical | Llama | 0.690 | 0.970 | 0.511 | 14.68 | 43.29 |
| Historical | Gemma | 0.851 | 0.885 | 0.662 | 16.34 | 37.93 |

The five scores are not orthogonalized. High VIFs and condition numbers show substantial same-space domain intercorrelation, so individual joint coefficients are conditional descriptors rather than isolated causal effects. In the strict set the strongest domain intercorrelations are Qwen Conscientiousness–Extraversion r=-0.963, Llama Conscientiousness–Neuroticism r=-0.942, and Gemma Conscientiousness–Neuroticism r=-0.878.

## Surface and flat-plane diagnostics

For Qwen strict Agreeableness, node-level flat-plane fits are:

| Projection | Plane R2 | Node RMSE percentile points |
|---|---:|---:|
| PC1 x PC3 | 0.894573 | 9.373098 |
| PC2 x PC3 | 0.717009 | 15.356527 |
| PC1 x PC2 | 0.178453 | 26.165115 |

The fixed-camera PNG/SVG artifacts show the same 275 exact persona nodes, a balanced masked surface, and an independently fitted red flat-plane wireframe. All three projections were generated so the focal interpretation is not based on one selected view.

## Viewer integration

The canonical ridge viewer retains its Qwen/editorial default and adds a no-reload **Big Five** profile set for Qwen, Llama, and Gemma. It exposes all four frozen constructions, displays within-model composite percentiles, retains raw projection scores in hover text, and lists constituent traits, polarity, and facet labels. The selected role persists by persona name across models, profile sets, and constructions.

The canonical 3D surface/flat-plane viewer also retains its original Qwen/editorial default. Its Big Five mode displays the preregistered primary human-anchored strict domains. For every model, PC pair, domain, and smoothing level, the exact node heights, thin-plate fabric, support mask, flat plane, fit gaps, and flat-adherence diagnostics are recomputed from that model's coordinates and Big Five scores. The Agreeableness surface does not reuse the editorial Affiliation plane.

## Method summary

For each construction/domain/model, normalized positive-pole trait vectors are averaged, normalized negative-pole trait vectors are averaged, and the final direction is the normalized positive mean minus negative mean. If a sensitivity omission removes one pole, the alternative is explicitly one-sided; no opposite pole is fabricated. Each normalized role vector is projected onto the saved float32 direction. Raw projections are retained; visualization heights are within-model midrank percentiles.

Qwen displays canonical `geometry_viz_data` coordinates. Qwen PCA loadings are recomputed from its own layer-mean role vectors and sign-oriented to canonical Qwen coordinates for direction-cosine tests. Llama and Gemma use their own layer-mean role-vector PCA and the exact established corresponding-axis Qwen sign-orientation procedure. Coordinate agreement with the established multimodel viewer is exact to the enforced 1e-10 tolerance.

## Scientific interpretation

### Observed

- The frozen strict construction recovers strong, recognizable Big Five-related organization in each model, but the dominant axis varies by model and domain.
- Qwen negative PC3 is strongly aligned with externally anchored activation-derived Agreeableness at both the role-score and activation-direction levels.
- Qwen Agreeableness–PC3 remains strong across direct-only, direct+close, externally expanded, historical, positive-only, leave-one-trait, and leave-one-facet constructions.
- Gemma gives a moderate Agreeableness–PC3 replication; Llama PC3 does not. Llama Agreeableness instead aligns with negative PC2.
- Five-domain held-out models explain substantial variance, while strong domain intercorrelation limits clean coefficient-level separation.

### Interpretation

Qwen PC3 has a strong Agreeableness-related component, especially on its negative pole. This sharpens but does not replace the broader cooperative-care/system-stabilizing versus disruptive/internal-objective interpretation: Agreeableness captures a major component, while non-Agreeableness variance and the broader perturbation evidence remain.

### Hypothesis

The recurring broad-domain organization may reflect model representations that inherit human-described dispositional regularities from training data. This would require independent behavioral or human psychometric correspondence tests; it is not established here.

### Unknown

It remains unknown whether these activation-derived directions correspond to independently measured human Big Five traits, whether behavior elicited without persona labels exhibits the same organization, and why corresponding PC labels differ across models.

## Verification and compute boundary

The analysis verified 240 canonical traits, 275 identical role names per model, exact frozen mapping hashes, valid reviewed SAPA items/scales, exact reconstruction of all saved role scores and percentiles from saved directions, bounded direction cosines, finite metrics, established-coordinate agreement, and byte-identical deterministic analytical CSV/JSON outputs across a complete rerun. Viewer tests verified zero Qwen/editorial numerical drift, exact Big Five source nodes, 270 model/profile surface variants, model/profile-specific masks and planes, stale-trace rejection, camera persistence, and persona-name selection persistence. Actual Chrome 152 loaded both self-contained viewers with real Plotly WebGL, switched all models/profile sets (and all ridge constructions), reset to Qwen/editorial, and reported no page errors. DOM-double results are recorded separately from this actual-browser verification.

No GPU, RunPod, new model inference, response generation, activation extraction, or external model API was used. Computation was CPU-only over saved local released vectors.
