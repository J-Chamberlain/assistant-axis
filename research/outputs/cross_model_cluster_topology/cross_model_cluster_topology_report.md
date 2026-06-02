# Cross-Model Cluster Topology Diagnostic

- Date: 2026-06-02T10:37:33Z
- model_used: GPT-5.5
- Geometry source: `research/visualizations/geometry_viz_data.json`
- Released vector representation: layer-mean role vectors, matching the current Qwen geometry builder.
- No GPU work, no H100 outputs, no prompt-battery outputs, no clean-repo copy, and no visualization files were modified.

## Models and Matching

- qwen: 275 roles; explained variance PC1/PC2/PC3 = 0.316/0.162/0.087.
- llama: 275 roles; explained variance PC1/PC2/PC3 = 0.172/0.142/0.065.
- gemma: 275 roles; explained variance PC1/PC2/PC3 = 0.235/0.128/0.057.

Pairwise matched role counts: Qwen-Llama=275, Qwen-Gemma=275, Llama-Gemma=275; three-way intersection=275.

## Clustering Method

Existing Qwen reference labels have 7 clusters. I used `k=7` for independent k-means clustering in each model's top-3-PC space, with fixed seed 42 and `n_init=50`. Sensitivity checks repeat k-means in top-5-PC space and agglomerative clustering in top-3-PC space.

## Cross-Model Cluster Similarity

| Pair | top3 kmeans ARI | top3 kmeans NMI | top5 kmeans ARI | top5 kmeans NMI | top3 agglomerative ARI | top3 agglomerative NMI |
|---|---:|---:|---:|---:|---:|---:|
| gemma_vs_llama | 0.355 | 0.454 | 0.659 | 0.648 | 0.633 | 0.542 |
| gemma_vs_qwen | 0.637 | 0.656 | 0.662 | 0.633 | 0.353 | 0.499 |
| llama_vs_qwen | 0.364 | 0.458 | 0.537 | 0.548 | 0.365 | 0.458 |

The cluster metrics show partial topology preservation rather than clean universal clustering. Qwen-Llama top-3 k-means ARI/NMI are 0.364/0.458, which is more stable than same-index PC3 but not as direct as the shared PC1/PC2 subspace. Qwen-Gemma top-3 k-means ARI/NMI are 0.637/0.656; Llama-Gemma are 0.355/0.454.

Prior same-index Qwen-Llama axis comparisons from `research/outputs/cross_model_pc2_pc3_diagnostic/` were PC2 Pearson r=0.606 and PC3 Pearson r=0.440, with Qwen-Llama PC1/PC2 plane principal correlations 0.977/0.905. The cluster result therefore supports the narrow claim that coarse topology is more robust than PC3 and that PC2 lives in a shared low-dimensional plane, but it does not prove that hard cluster assignments are more stable than all axis-level structure.

## Qwen Reference Cluster Mapping

Best Qwen-reference to Llama k-means matches:
- combative_iconoclast -> Llama cluster 0: overlap 6, Jaccard 0.107; retained examples: contrarian, influencer, maverick, provocateur, rebel, revolutionary
- editorial -> Llama cluster 1: overlap 10, Jaccard 0.145; retained examples: accountant, editor, grader, nutritionist, pharmacist, proofreader, screener, secretary, summarizer, supervisor
- grounded_social -> Llama cluster 0: overlap 31, Jaccard 0.443; retained examples: actor, addict, amateur, bartender, blogger, caregiver, celebrity, chef, dilettante, divorcee
- mythic_spiritual -> Llama cluster 2: overlap 32, Jaccard 0.593; retained examples: aberration, alien, ancient, avatar, bard, chimera, coral_reef, crystalline, demon, dreamer
- other -> Llama cluster 6: overlap 2, Jaccard 0.286; retained examples: infant, toddler
- procedural_professional -> Llama cluster 4: overlap 60, Jaccard 0.435; retained examples: advocate, ambassador, anthropologist, archaeologist, architect, archivist, builder, cartographer, coach, collaborator
- trickster_chaos -> Llama cluster 3: overlap 7, Jaccard 0.226; retained examples: comedian, fool, gossip, jester, pirate, rogue, trickster

Best Qwen-reference to Gemma k-means matches:
- combative_iconoclast -> Gemma cluster 2: overlap 12, Jaccard 0.400; retained examples: competitor, contrarian, cynic, daredevil, devils_advocate, gamer, hacker, maverick, provocateur, rebel
- editorial -> Gemma cluster 5: overlap 10, Jaccard 0.122; retained examples: accountant, editor, grader, pharmacist, proofreader, screener, secretary, summarizer, supervisor, translator
- grounded_social -> Gemma cluster 4: overlap 24, Jaccard 0.393; retained examples: actor, addict, amateur, amnesiac, auctioneer, bartender, bohemian, celebrity, criminal, divorcee
- mythic_spiritual -> Gemma cluster 3: overlap 33, Jaccard 0.611; retained examples: ancient, angel, ascetic, avatar, bard, coral_reef, dreamer, echo, egregore, elder
- other -> Gemma cluster 6: overlap 2, Jaccard 0.200; retained examples: infant, toddler
- procedural_professional -> Gemma cluster 5: overlap 69, Jaccard 0.507; retained examples: ambassador, analyst, anarchist, anthropologist, architect, archivist, auditor, biologist, cartographer, chemist
- trickster_chaos -> Gemma cluster 2: overlap 6, Jaccard 0.194; retained examples: absurdist, comedian, gossip, jester, rogue, trickster

## Per-Model Cluster Labels

### qwen
- Cluster 0 (n=72), candidate label `procedural_professional`: generalist, futurist, chemist, strategist, librarian, publisher, observer, dispatcher
- Cluster 1 (n=31), candidate label `adversarial_perturbative`: vigilante, rebel, fixer, maverick, rogue, provocateur, narcissist, competitor
- Cluster 2 (n=25), candidate label `grounded_social`: immigrant, optimist, refugee, minimalist, patient, retiree, divorcee, blogger
- Cluster 3 (n=28), candidate label `mythic_spiritual`: alien, simulacrum, homunculus, chimera, egregore, predator, flaneur, zealot
- Cluster 4 (n=36), candidate label `mythic_spiritual`: whale, dreamer, coral_reef, wind, martyr, hermit, guru, mycorrhizal
- Cluster 5 (n=19), candidate label `grounded_social`: prisoner, bartender, hoarder, improviser, addict, orphan, fool, celebrity
- Cluster 6 (n=64), candidate label `grounded_social`: guide, activist, advocate, builder, navigator, cosmopolitan, interpreter, hybrid

### llama
- Cluster 0 (n=47), candidate label `grounded_social`: immigrant, refugee, maverick, chef, minimalist, survivor, podcaster, contrarian
- Cluster 1 (n=66), candidate label `procedural_professional`: lawyer, economist, linguist, librarian, detective, psychologist, specialist, debugger
- Cluster 2 (n=35), candidate label `mythic_spiritual`: homunculus, whale, golem, aberration, revenant, wind, tree, familiar
- Cluster 3 (n=28), candidate label `adversarial_perturbative`: cynic, smuggler, daredevil, gossip, comedian, narcissist, hoarder, improviser
- Cluster 4 (n=72), candidate label `care_repair_stabilizing`: collector, guide, merchant, conservator, archivist, scout, navigator, translator
- Cluster 5 (n=24), candidate label `mythic_spiritual`: narrator, guru, flaneur, wanderer, martyr, stoic, romantic, sage
- Cluster 6 (n=3), candidate label `mixed_or_unlabeled`: toddler, infant, caveman

### gemma
- Cluster 0 (n=61), candidate label `care_repair_stabilizing`: altruist, guide, navigator, activist, advocate, interpreter, presenter, builder
- Cluster 1 (n=35), candidate label `mythic_spiritual`: alien, predator, purist, virtuoso, martyr, stoic, flaneur, evangelist
- Cluster 2 (n=27), candidate label `adversarial_perturbative`: hacker, fixer, vigilante, rebel, maverick, competitor, daredevil, dilettante
- Cluster 3 (n=36), candidate label `mythic_spiritual`: coral_reef, dreamer, familiar, witch, pilgrim, mycorrhizal, hermit, bard
- Cluster 4 (n=31), candidate label `grounded_social`: addict, retiree, orphan, bartender, improviser, divorcee, auctioneer, celebrity
- Cluster 5 (n=79), candidate label `procedural_professional`: linguist, specialist, journalist, forecaster, sociologist, librarian, technologist, biologist
- Cluster 6 (n=6), candidate label `grounded_social`: infant, provincial, fool, grandparent, toddler, caveman

## Region Conservation

Seed-set purity by model is in `cross_model_cluster_similarity_metrics.json` under `region_conservation` and summarized in `per_model_cluster_summaries.csv`. The strongest recurring regions are evaluator/procedural-professional and mythic/symbolic poles; grounded/social and care/repair regions are present but split more often. Adversarial/perturbative roles recur as neighborhoods in Qwen and partly in Llama/Gemma, but they are not a clean one-cluster invariant.
- procedural_professional: Qwen ref primary=procedural_professional (21/26); Qwen kmeans purity=0.808, Llama=0.808, Gemma=0.846.
- mythic_spiritual: Qwen ref primary=mythic_spiritual (18/21); Qwen kmeans purity=0.571, Llama=0.619, Gemma=0.714.
- grounded_social: Qwen ref primary=grounded_social (16/19); Qwen kmeans purity=0.526, Llama=0.842, Gemma=0.579.
- care_repair_stabilizing: Qwen ref primary=procedural_professional (8/15); Qwen kmeans purity=0.600, Llama=0.467, Gemma=0.733.
- adversarial_perturbative: Qwen ref primary=combative_iconoclast (8/16); Qwen kmeans purity=0.938, Llama=0.438, Gemma=0.812.
- creative_symbolic: Qwen ref primary=mythic_spiritual (6/15); Qwen kmeans purity=0.467, Llama=0.400, Gemma=0.467.
- assistant_evaluator_like: Qwen ref primary=editorial (7/14); Qwen kmeans purity=0.786, Llama=1.000, Gemma=0.929.

## Interpretation

Observed: coarse topology is partly more stable than same-index later PCs, especially compared with Qwen-Llama PC3. However, the topology is not cleanly universal: ARI values are modest, Qwen reference clusters often split across model-specific k-means clusters, and cluster labels require semantic caution. Inferred: the safest report framing is that broad role-space regions recur across models better than individual PC3 axes, while PC2 is best treated as a subspace-dependent direction inside a more stable low-dimensional plane. Speculative: some semantic regions may be conserved attractor basins even when PCA axes rotate, but this needs independent alignment and non-name-based validation.

## Bounded Gemma Comparison

Gemma is included because local released role vectors are present. In this artifact-level analysis, Gemma partially shares topology with Qwen/Llama but also reorganizes several regions; it should be used as secondary evidence, not as the arbiter of Qwen PC2/PC3 interpretation.

## Visualization Recommendation

Do not modify visualization tools yet. Model switching in the main viewer is feasible if a multi-model data bundle is built, but cross-model arrows need an explicit alignment convention. PC1/PC2-only or cluster-overlap visualizations are more justified than 3D PC3 arrows.
