# Extended persona PCA dimensionality audit

Generated UTC: 2026-09-11T23:18:54Z
Analysis model: GPT-5.5

## Executive answer

Only three PCs were used previously because the original geometry builder was configured for a 3D visualization (`PCA(n_components=3)`), not because a dimensionality-selection analysis rejected PC4+. This audit fits all 274 available centered components and combines variance, three scree diagnostics, broken-stick, 250 marginal-preserving parallel permutations, 500 role bootstraps, subspace angles, same-space trait associations, and cross-model role-score recurrence.

Primary recommendation: **Use PC1-PC6 when the scientific question needs the supported later axes; retain PC1-PC3 as the compact public-facing core.**

Explained variance here is activation-coordinate variation among 275 centered saved role vectors. It is not a percentage of personality, behavior, human psychological variance, or causal importance.

## Qwen PC1-PC10 variance

| PC | Explained variance | Cumulative | Parallel | Bootstrap loading cosine median / q05 | Retention status |
|---:|---:|---:|---|---:|---|
| 1 | 31.595% | 31.595% | retain | 0.994 / 0.981 | CORE |
| 2 | 16.163% | 47.759% | retain | 0.984 / 0.957 | CORE |
| 3 | 8.690% | 56.449% | retain | 0.979 / 0.938 | CORE |
| 4 | 4.520% | 60.969% | retain | 0.871 / 0.685 | SUPPORTED LATER COMPONENT |
| 5 | 3.615% | 64.584% | retain | 0.830 / 0.575 | SUPPORTED LATER COMPONENT |
| 6 | 2.824% | 67.408% | retain | 0.792 / 0.594 | SUPPORTED LATER COMPONENT |
| 7 | 2.536% | 69.944% | retain | 0.734 / 0.537 | NOISE-LIKE / UNSTABLE |
| 8 | 2.138% | 72.083% | retain | 0.767 / 0.564 | EXPLORATORY |
| 9 | 1.946% | 74.029% | retain | 0.720 / 0.540 | NOISE-LIKE / UNSTABLE |
| 10 | 1.601% | 75.630% | retain | 0.771 / 0.561 | EXPLORATORY |

## Cumulative thresholds

| Model | 50% | 60% | 68% | 70% | 75% | 80% | 90% | 95% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3-32B | 3 | 4 | 7 | 8 | 10 | 15 | 35 | 63 |
| Llama-3.3-70B | 7 | 11 | 17 | 19 | 25 | 35 | 67 | 103 |
| Gemma-2-27B | 5 | 9 | 14 | 15 | 21 | 28 | 59 | 94 |

Qwen reaches 68% at PC7 and 80% at PC15. The 68% row is reported because it was specifically requested; it is not treated as the correct cutoff.

## Scree and random-data references

- Qwen/Qwen3-32B: largest absolute eigengap after PC1; largest relative gap after PC1; log-chord knee PC11; two-line log-scree break PC11; sequential parallel-analysis retained count 13.
- Llama-3.3-70B: largest absolute eigengap after PC2; largest relative gap after PC2; log-chord knee PC16; two-line log-scree break PC8; sequential parallel-analysis retained count 35.
- Gemma-2-27B: largest absolute eigengap after PC1; largest relative gap after PC2; log-chord knee PC10; two-line log-scree break PC9; sequential parallel-analysis retained count 25.

The knee methods are descriptive and disagree where stated; no automated knee is treated as ground truth. Parallel analysis uses the requested primary null: each activation coordinate is independently permuted across roles, retaining each coordinate's marginal values while destroying cross-coordinate role structure.

## PC4, PC5, and later Qwen components

### PC4: SUPPORTED LATER COMPONENT

Observed: variance 4.520% (cumulative 60.969%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.871/0.685; best adjacent subspace PC3-PC4 q05 minimum canonical correlation=0.595.
Same-space trait evidence: strongest positive correlations include avoidant, understated, literal, reductionist, traditional; strongest negative correlations include holistic, systems_thinker, independent, generous, progressive; maximum absolute Pearson=0.621.
Role extremes: positive infant, toddler, caveman, pirate, translator; negative revolutionary, anarchist, maverick, rebel, provocateur.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC5: SUPPORTED LATER COMPONENT

Observed: variance 3.615% (cumulative 64.584%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.830/0.575; best adjacent subspace PC4-PC5 q05 minimum canonical correlation=0.355.
Same-space trait evidence: strongest positive correlations include divergent, cosmopolitan, curious, introspective, futuristic; strongest negative correlations include closure_seeking, efficient, convergent, concise, anthropocentric; maximum absolute Pearson=0.566.
Role extremes: positive toddler, infant, absurdist, fool, comedian; negative soldier, pirate, warrior, veteran, criminal.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC6: SUPPORTED LATER COMPONENT

Observed: variance 2.824% (cumulative 67.408%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.792/0.594; best adjacent subspace PC6-PC7 q05 minimum canonical correlation=0.203.
Same-space trait evidence: strongest positive correlations include deontological, universalist, fundamentalist, principled, absolutist; strongest negative correlations include systems_thinker, divergent, holistic, interdisciplinary, futuristic; maximum absolute Pearson=0.561.
Role extremes: positive zealot, stoic, anarchist, revolutionary, martyr; negative gamer, sommelier, surfer, musician, composer.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC7: NOISE-LIKE / UNSTABLE

Observed: variance 2.536% (cumulative 69.944%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.734/0.537; best adjacent subspace PC6-PC7 q05 minimum canonical correlation=0.203.
Same-space trait evidence: strongest positive correlations include closure_seeking, epicurean, universalist, fundamentalist, inspirational; strongest negative correlations include inclusive, open_ended, critical, humble, introspective; maximum absolute Pearson=0.279.
Role extremes: positive jester, narcissist, proofreader, comedian, auctioneer; negative caveman, amnesiac, prey, tree, geographer.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC8: EXPLORATORY

Observed: variance 2.138% (cumulative 72.083%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.767/0.564; best adjacent subspace PC7-PC8 q05 minimum canonical correlation=0.108.
Same-space trait evidence: strongest positive correlations include verbose, circumspect, historical, cautious, open_ended; strongest negative correlations include decisive, efficient, closure_seeking, concise, urgent; maximum absolute Pearson=0.356.
Role extremes: positive historian, flaneur, sommelier, traditionalist, archaeologist; negative caveman, infant, hive, swarm, coach.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC9: NOISE-LIKE / UNSTABLE

Observed: variance 1.946% (cumulative 74.029%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.720/0.540; best adjacent subspace PC9-PC10 q05 minimum canonical correlation=0.117.
Same-space trait evidence: strongest positive correlations include systems_thinker, collaborative, interdisciplinary, egalitarian, environmental; strongest negative correlations include inquisitive, understated, socratic, introspective, circumspect; maximum absolute Pearson=0.317.
Role extremes: positive caveman, toddler, pirate, anarchist, activist; negative amnesiac, proofreader, loner, void, interviewer.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC10: EXPLORATORY

Observed: variance 1.601% (cumulative 75.630%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.771/0.561; best adjacent subspace PC9-PC10 q05 minimum canonical correlation=0.117.
Same-space trait evidence: strongest positive correlations include avoidant, universalist, submissive, dogmatic, elitist; strongest negative correlations include inclusive, exploratory, divergent, generous, generalist; maximum absolute Pearson=0.370.
Role extremes: positive parasite, virus, narcissist, vegan, mycorrhizal; negative poet, bard, playwright, prophet, caveman.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC11: NOISE-LIKE / UNSTABLE

Observed: variance 1.181% (cumulative 76.811%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.671/0.433; best adjacent subspace PC10-PC11 q05 minimum canonical correlation=0.031.
Same-space trait evidence: strongest positive correlations include essentialist, libertarian, fundamentalist, absolutist, ascetic; strongest negative correlations include collaborative, inclusive, egalitarian, progressive, collectivistic; maximum absolute Pearson=0.252.
Role extremes: positive stoic, ascetic, philosopher, mathematician, traditionalist; negative activist, gossip, revolutionary, vampire, vigilante.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC12: NOISE-LIKE / UNSTABLE

Observed: variance 1.125% (cumulative 77.937%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.588/0.326; best adjacent subspace PC12-PC13 q05 minimum canonical correlation=0.024.
Same-space trait evidence: strongest positive correlations include anthropocentric, decisive, closure_seeking, universalist, concise; strongest negative correlations include exploratory, divergent, inquisitive, inclusive, humble; maximum absolute Pearson=0.156.
Role extremes: positive infant, toddler, poet, photographer, caveman; negative witch, shaman, mystic, teenager, adolescent.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

### PC13: NOISE-LIKE / UNSTABLE

Observed: variance 1.024% (cumulative 78.961%); parallel sequential retain=True; bootstrap matched-loading median/q05=0.577/0.404; best adjacent subspace PC12-PC13 q05 minimum canonical correlation=0.024.
Same-space trait evidence: strongest positive correlations include relativist, understated, open_ended, circumspect, constructivist; strongest negative correlations include anthropocentric, closure_seeking, universalist, urgent, experiential; maximum absolute Pearson=0.123.
Role extremes: positive infant, pirate, smuggler, criminal, therapist; negative adolescent, teenager, hoarder, martyr, zealot.
INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.

## Cross-model recurrence for Qwen later PCs

| Qwen PC | Best Llama PC (Pearson / Spearman; p) | Best Gemma PC (Pearson / Spearman; p) |
|---:|---|---|
| 4 | PC3 (0.690 / 0.625; 0.001) | PC4 (-0.628 / -0.532; 0.001) |
| 5 | PC5 (0.688 / 0.621; 0.001) | PC5 (-0.651 / -0.586; 0.001) |
| 6 | PC6 (0.505 / 0.528; 0.001) | PC8 (-0.570 / -0.565; 0.001) |
| 7 | PC8 (0.723 / 0.684; 0.001) | PC6 (0.539 / 0.540; 0.001) |
| 8 | PC9 (0.562 / 0.608; 0.001) | PC7 (-0.553 / -0.563; 0.001) |
| 9 | PC7 (0.645 / 0.568; 0.001) | PC6 (0.594 / 0.554; 0.001) |
| 10 | PC11 (-0.473 / -0.437; 0.001) | PC9 (-0.564 / -0.562; 0.001) |
| 11 | PC14 (0.653 / 0.587; 0.001) | PC15 (0.586 / 0.590; 0.001) |
| 12 | PC12 (-0.487 / -0.475; 0.001) | PC10 (0.488 / 0.366; 0.001) |
| 13 | PC14 (0.435 / 0.501; 0.001) | PC11 (0.443 / 0.404; 0.001) |

Component matching compares score patterns over the same 275 role labels, searches the first 20 or more PCs in each model, records unconstrained best matches and a one-to-one Hungarian map, and tests search-adjusted best correlations against shuffled role labels. Same component numbers are not presumed to share meaning.

## Cross-model score-subspace recurrence

| Model pair | top 3 | top 4 | top 5 | top 6 |
|---|---:|---:|---:|---:|
| Qwen/Qwen3-32B / Llama-3.3-70B | 0.789 (p=0.001) | 0.908 (p=0.001) | 0.891 (p=0.001) | 0.888 (p=0.001) |
| Qwen/Qwen3-32B / Gemma-2-27B | 0.920 (p=0.001) | 0.877 (p=0.001) | 0.911 (p=0.001) | 0.817 (p=0.001) |
| Llama-3.3-70B / Gemma-2-27B | 0.680 (p=0.001) | 0.932 (p=0.001) | 0.936 (p=0.001) | 0.918 (p=0.001) |

These score-space similarities are over the shared role labels and all exceed their 1,000-shuffle nulls. They show recurrence of role-score subspaces, not identity of activation bases or component semantics.

## Individual axes versus subspaces

Among the 13 sequentially parallel-retained Qwen components, 3 of the explicitly bootstrapped components meet the descriptive individual-axis stability rule. Adjacent-pair and cumulative-subspace diagnostics should be used where close eigenvalues permit rotation; a stable subspace does not license distinct names for unstable member axes.

PC4-PC6 do not meet the strict individual-axis rule (median loading cosine ≥0.90 and q05 ≥0.75), and no Qwen later adjacent block passes the equally strict subspace rule. They are nevertheless classified as supported later components because each passes sequential parallel analysis, has moderate bootstrap reproducibility (median ≥0.75, q05 ≥0.50, same-index frequency ≥0.50), shows a same-space trait association |r| ≥0.50, and recurs in both Llama and Gemma after search-adjusted role-label permutation controls. This is weaker evidence than CORE status and does not license durable semantic names.

## Role-instruction interpretation packet

`qwen_extended_pc_interpretation_packet.csv` randomizes later-component identities and pole signs and contains instruction text without PC values. Its separate key is retained for audit. No external model API or unblinded reviewer was used; labels in this report remain explicitly provisional.

## Static figures

- `qwen_scree_linear.png` and `qwen_scree_linear.svg`.
- `qwen_scree_log.png` and `qwen_scree_log.svg`.
- `qwen_cumulative_variance.png` and `qwen_cumulative_variance.svg`.
- `qwen_parallel_analysis.png` and `qwen_parallel_analysis.svg`.
- `qwen_bootstrap_component_stability.png` and `qwen_bootstrap_component_stability.svg`.
- `cross_model_component_correspondence_heatmap.png` and `cross_model_component_correspondence_heatmap.svg`.
- `cross_model_subspace_similarity.png` and `cross_model_subspace_similarity.svg`.
- `qwen_pc4_pc5_role_scatter.png` and `qwen_pc4_pc5_role_scatter.svg`.
- `qwen_pc4_pc6_later_component_scatter.png` and `qwen_pc4_pc6_later_component_scatter.svg`.

## Observed

- Full model-local activation-coordinate spectra, variance thresholds, random-data comparisons, bootstrap stability, role extremes, trait associations, and cross-model score/subspace recurrences are reported in the saved tables.
- Qwen, Llama, and Gemma each contain the same 275 role labels, but their PCA bases are fitted separately in hidden dimensions 5,120, 8,192, and 4,608.
- PC1-PC3 reproduce the canonical/established coordinates within the saved verification tolerances.
- Qwen PCs 1-13 exceed the 95th-percentile marginal-permutation null sequentially; only PCs 1-3 meet the strict individual-axis bootstrap rule. PCs 4-6 meet the declared moderate-reproducibility rule and recur in both comparison models.

## Interpretation

- Use PC1-PC6 when the scientific question needs the supported later axes; retain PC1-PC3 as the compact public-facing core.
- PC4-PC6 are scientifically useful as supported secondary coordinates, but their lower bootstrap stability makes them weaker and less nameable than the PC1-PC3 core. PC7-PC13 exceed the random-data reference yet lack sufficient stability or trait coherence for privileged interpretation.
- Later components should be named only when individual stability, cross-model recurrence, full-distribution role structure, and trait coherence converge. Same-space trait correlations are descriptive support, not independent psychological validation.

## Hypotheses

- PC4-PC6 may encode secondary role/register distinctions that the original 3D display compressed; coordinate-blind human review is needed before durable labels.
- Cross-model score-subspace recurrence may reflect shared role-instruction structure as well as model-internal geometry; new elicitation is needed to separate those possibilities.

## Unknowns

- Whether later-component distinctions recur in newly elicited behavior rather than saved role vectors remains unknown.
- Whether independent raters would recover coherent semantic contrasts from the blinded instruction packets remains unknown.
- PCA dimensionality does not determine a uniquely correct ontology or visualization dimension.

## Reproducibility and compute boundary

The primary null uses 250 permutations per model, bootstrapping uses 500 replicates per model, and cross-model role-label controls use 1000 permutations. `deterministic_second_pass.json` compares a complete second fixed-seed computation of all major numerical artifacts.

No GPU, RunPod, model inference, activation extraction, or external model API was used.
