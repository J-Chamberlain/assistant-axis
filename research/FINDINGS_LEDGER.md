# Findings Ledger

This is a compact index of project claims and their status. Use `research/RESEARCH_STATE.md` for full history and exact supporting paths.

## Confirmed Findings

### Careful Evaluator Finding

Gemma 2 27B's assistant axis is dominated by evaluative roles, especially proofreader, screener, grader, and editor. `assistant` ranks 45th out of 275 on the assistant axis, and the top pole correlates strongly with conscientiousness and negatively with psychopathy.

### Base Model Basin Finding

The careful-evaluator basin appears in Gemma 2 27B base model behavior, not only in instruction-tuned behavior. This supports the interpretation that the geometry reflects pretraining distribution structure as well as post-training.

### Qwen/Llama Convergence and Gemma Divergence

Qwen 3 32B and Llama 3.3 70B converge strongly on persona rankings, while Gemma diverges. This matters for any claim that transfers cluster representatives from Gemma into Qwen without Qwen-native validation.

### Trickster Adaptive Extraction Success

Qwen/Qwen3-32B trickster Phase 1 completed 1200 rollouts and 1200 activation shards with final integrity passed. Codex GPT-5.5 Standard adaptive scoring reached 64 score>=2 and 33 score==3 responses in 64 scored records. The score>=2 vector matched the Lu trickster reference mean at cosine 0.957557, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets.

### Public-Source H100 Extraction Boundary Mismatch

The public-source D01 audit found likely mismatch between H100 `outputs.hidden_states[48]` extraction and the original Assistant Axis Qwen convention. Official/prior extraction hooks `model.model.layers[48]` and captures decoder layer-48 post-MLP residual output, while Transformers/Qwen3 hidden-state semantics indicate `hidden_states[48]` is the input to decoder layer 48 / output after layer 47. The next step is a tiny one-prompt hook-vs-hidden-states confirmation test, not a full H100 rerun.

### Public Role Rollout Artifacts Are Inputs-Only

Public artifacts allow reconstruction of the intended Assistant Axis role-vector input distribution: 275 non-default roles, 5 positive instructions per role, and 240 shared extraction questions, yielding 1,200 instruction-question combinations per role. Public artifacts do not include the original generated rollout responses, response-level judge scores, or retained-response masks/IDs. The remembered "64" count is resolved as Qwen layer count in `[64,5120]` vectors plus local adaptive-extraction counts, not a public original retained-response count.

### H100 Anomaly Interpretation Now Uses Four Methodological Dependency Tracks

The persistent H100 diagnostic checklist now treats D01-D09 as subordinate to four higher-level tracks: T01 extraction equivalence / activation boundary, T02 forecaster improvement, T03 prompt-battery construction, and T04 response-state uncertainty / centroid-versus-single-sample mismatch. D01/D02 depend directly on T01; D03/D08 depend partly on T02/T03; D04/D05/D06 should not be finalized until extraction equivalence, forecaster compression, prompt-battery bias, and single-response uncertainty have been considered. This reframes the H100 run as informative but not yet final behavioral evidence for PC2 shifts, cone outliers, or PC3 collapse.

### PC2 Muted-PC1 Extremes Refine the PC2 Interpretation

The muted-PC1 diagnostic selected the central 45th-55th percentile PC1 band from `research/visualizations/geometry_viz_data.json`, with PC1 bounds -2.747954 to 6.917357 and 27 roles. Within this PC1-controlled slice, high PC2 roles were `amateur`, `influencer`, `patient`, `gamer`, `optimist`, `podcaster`, `blogger`, `workaholic`, `chameleon`, and `caregiver`; low PC2 roles were `hive`, `philosopher`, `purist`, `traditionalist`, `composer`, `healer`, `symbiont`, `visionary`, `merchant`, and `guardian`. This supports and refines the PC2 interpretation as situated/social immediacy or locally pressured role performance versus abstract, integrative, systemic, standards-bearing stance. Caveat: the band is small and cluster-skewed, so this is descriptive coordinate inspection rather than independent semantic or causal validation.

### Cluster-Conditioned PC2 Extremes Partially Support Stability/Impressionability Framing

The cluster-conditioned PC2 diagnostic ranked PC2 globally, within all clusters with at least 10 roles, and within muted-PC1 bands for clusters where sample size permitted. Expected-direction checks passed 7/8 globally and 5/8 against cluster medians; `patient`, `amateur`, `tree`, `hive`, and `philosopher` behaved as predicted, while `shapeshifter`, `chameleon`, and `elder` are the main caveats. Existing proxy-score checks found abstraction was the strongest surviving correlate after cluster demeaning (Pearson r=-0.484), while maturity and residence-time proxies weakened under cluster control. Interpretation: PC2 should be stated provisionally as situated-immediacy/formative-state versus integrated-stability, not as a pure plasticity/rootedness axis.

### Cross-Model PC2/PC3 Diagnostic Finds PC2 Plane Transfer but Weak PC3 Comparability

The contained Qwen/Llama/Gemma diagnostic used released layer-mean role vectors, matching the current Qwen geometry visualization artifact type. Qwen and Llama have a highly comparable PC1/PC2 plane, with principal correlations 0.977 and 0.905, but same-index PC2 is only partial (Pearson r=0.606; Spearman r=0.430) and Qwen PC2's strongest single-axis Llama match is Llama PC1 (Pearson r=0.692). Expected-direction checks passed 16/16 globally for Qwen and 13/16 globally for Llama, but cluster-relative Llama checks were only 7/16. Qwen-Llama PC3 is weaker (same-index Pearson r=0.440; Spearman r=0.558), so cross-model PC3 arrows should not be built without alignment correction or strong caveats.

### Within-Role Displacement Study Design Prepared

Prepared `research/outputs/within_role_displacement_design/` as reusable scaffolding for a one-role displacement study. The design inventories 275 roles with five positive instructions each, 240 shared extraction questions, scoring templates for expected PC1/PC2/PC3 displacement around a selected role centroid, and a role-candidate helper table. Seven roles fall in the 35th-65th percentile band on all three PCs and 62 roles fall in the 20th-80th band on all three PCs; Actor remains a plausible behaviorally coherent candidate but is PC2-high, so the final target role remains user-selected.

### Pod Workflow Lessons

Detached execution, response JSONL preservation, separate activation shards, local integrity checks, explicit run artifacts, and RunPod API or `runpodctl` termination are now validated workflow requirements. Browser/dashboard termination is fallback only.

## Negative Findings

### Gemma Emotion PCA Gate Failure

Gemma 2 27B failed the Anthropic/Sofroniew emotion-vector PCA gate at tested layers. This is a negative result for dominant-PC emotion geometry in Gemma at this scale, though distributed emotion structure remains a separate possibility.

### Editor Adaptive Extraction Failure

The first Qwen editor adaptive extraction chunk did not meet validation thresholds. The 128-record 512-token run produced only 10 score>=2 and 3 score==3 responses, so vector validation and sample sufficiency were correctly not run.

### Token-Cap Sensitivity Result for Editor

The matched first-64 editor rerun at 1024 tokens reduced truncation from 50/64 to 5/64, but score>=2 and score==3 counts did not improve. Token cap alone does not explain editor's low role-expression yield.

### Forced Manual Cap Pilot Failure

The forced manual cap pilot froze geometry despite zero leakage, with post-T3 trickster cosine variance at 0.00e+00. It should not be treated as a valid stabilizing result.

## Provisional Interpretations

### Assistant-Adjacent Collapse

Editor weakness may reflect collapse toward generic assistant behavior for assistant-adjacent personas under the current Lu-style extraction setup. This is plausible but still provisional because only one editor chunk and one matched token-cap follow-up have been tested.

### Adaptive Extraction Generality

Adaptive extraction is operationally validated for trickster but not yet generally validated across persona types. It should be treated as a workflow candidate pending additional high-yield, mid-yield, and assistant-adjacent persona tests.

### Paper 1.5 Scope Reframing

Paper 1.5 is now framed as a persona-geometry interpretation paper rather than primarily as an adaptive extraction replication paper. Adaptive extraction remains important due diligence and tooling evidence, while the main claim is that persona activation geometry decomposes into semantic, dispositional, procedural, lexical/register, and residual layers.

### Paper 2 Local-Manifold Direction

Paper 2 is now framed around local centroid perturbation and local persona-manifold mapping. Candidate anchors are Trickster, Actor, Therapist, and Spy. Older dyad contagion, attractor-collapse, conversational drift, and rumination plans are archived as future dynamics work rather than discarded.

### Cluster Motivational Structure

Six of seven clusters have dialogue-derived motivational characterizations. These are useful for hypothesis generation and Paper 1.5 framing, but empirical verification remains pending.

## Methodological Deviations

### Role-Prompt Label Exposure

The Lu et al. role system prompts contain extensive direct identity-label exposure. A local audit of 275 role files found 1280/1375 prompts, 93.1%, expose the target role label or a normalized variant, and 227/275 roles have 5/5 prompt exposure. This means the elicitation design should be described as role-label-plus-behavior elicitation rather than purely behavioral elicitation; it does not by itself show that activation geometry is invalid or reducible to labels.

### No-Label Prompt Ablation

A deterministic no-label prompt-ablation dataset now exists for all 1375 Lu et al. role prompts. Validation found zero remaining normalized target-label exposure, median character length ratio 0.842, median lexical Jaccard 0.714, and no over-flattening flags. Offline TF-IDF/SVD comparison found continuous prompt-space topology is largely preserved after label removal, with role-level SVD cosine median 0.998, nearest-neighbor preservation 0.924, and pairwise distance correlation 0.985, while hard k-means cluster assignments are much less stable.

### Semantic vs Activation Geometry

Three-way comparison of role-name, original-prompt, no-label prompt, and available activation-reference geometry finds that semantic topology is preserved strongly between original and no-label prompt spaces, but activation cluster structure is only partially recoverable from semantics. At k=7, ARI against activation labels is 0.010 for role names, 0.023 for role names plus descriptions, 0.111 for original prompts, and 0.130 for no-label prompts. No-label prompt distances best predict available activation centroid-profile distances, but correlations remain modest: 0.230 for Gemma and 0.254 for Qwen.

### Semantic Role Manifold Interpretation

The Lu et al. role corpus now has a standalone interpretation as a frontier-model-generated semantic role manifold. It contains meaningful prompt-space topology before activations are considered, and that topology mostly survives label removal. The current interpretation is that activation experiments test how target models internalize, compress, sharpen, or reorganize this semantic manifold rather than revealing a structure independent of the elicitation corpus.

### Deep Semantic Topology

A deeper no-label semantic topology analysis found that the role corpus is organized by mixed social, professional, narrative, stylistic, and archetypal structure rather than by a single psychological taxonomy. The no-label k=7 semantic manifold shows broad professional/helper, lived-experience/social, communicative/media, mythic/fantastical, adversarial/normative, and generalist/helper regions, with soft boundaries and bridge roles such as spy, amnesiac, sage, guardian, merchant, and emissary. Dense pockets include professional and migration/survival neighborhoods; sparse roles include flaneur, predator, devils_advocate, advocate, teenager, vegan, genie, angel, robot, and adolescent. This supports treating the role list as a constructed semantic manifold whose topology partially constrains, but does not determine, activation geometry.

### Semantic-Activation Overlap Structure

Structured overlap analysis between activation clusters, original prompt clusters, and no-label prompt clusters found 73 stable anchor roles and 198 bridge or migratory roles under broad overlap criteria. Editorial is the cleanest semantic-activation overlap region, while procedural-professional compresses several semantic regions into one broad activation basin. Collective/swarm roles are semantically compact but distributed across larger activation clusters rather than forming a dedicated activation cluster in the available labels. This supports the interpretation that activation geometry preserves local semantic anchors while reorganizing broad prompt-space topology around enacted behavioral structure.

### No-Label Activation Stress Test Design

The first no-label activation-space stress test is designed but not launched. It selects 20 roles covering stable anchors, bridge/migratory roles, sparse/outlier roles, assistant-adjacent/procedural roles, theatrical/fantastical roles, and collective/swarm roles: editor, screener, reviewer, consultant, evaluator, proofreader, negotiator, trickster, jester, oracle, leviathan, mystic, hive, egregore, skeptic, philosopher, spy, dilettante, flaneur, and robot. The design uses paired original label-exposed and no-label conditions with 20 rollouts per role per condition, for 800 planned Qwen/Qwen3-32B layer-48 rollouts. The only intended experimental difference is system prompt label exposure.

### Stage-1 Role Inventory Uncertainty Infrastructure

Stage-1 role-inventory uncertainty is now scoped as provider-separated corpus construction. Codex handles OpenAI-side generation, provider-agnostic ingestion, normalization, and local semantic analysis; Anthropic-side generation is delegated to Claude or Claude Code and synced through GitHub. This keeps cross-provider credential handling out of Codex and treats GitHub as the synchronization layer for generated inventories.

### Model Provenance Requirement

Model provenance is now mandatory for future generated, evaluated, or analyzed research artifacts. The canonical schema is `research/workflow/model_provenance_schema.md`; it distinguishes `generation_model`, `evaluation_model`, `analysis_model`, and `script_author_model` so model identity is treated as part of the experimental causal structure rather than incidental metadata.

### Full Cluster Assignment and PCA Projection (2026-05-28)

- All 275 personas assigned to clusters via nearest-centroid lookup
- Cluster distribution: procedural_professional 126; grounded_social 54; mythic_spiritual 51; combative_iconoclast 15; editorial 13; trickster_chaos 10; other 6
- Ambiguous assignments with margin < 0.02: 262
- PC1 explained variance: 0.315954; PC1-assistant-axis alignment: 0.802310
- Notable surprising placements: anarchist, robot, cyborg, hive, and swarm assign to procedural_professional; virus assigns to mythic_spiritual with extremely low margin; caveman assigns to trickster_chaos with extremely low margin

### Latent Feature Discovery Loop (2026-05-28)

- Implemented the first constrained LLM-assisted latent-feature discovery loop for persona activation geometry, using GPT-5.5 Standard as hypothesis generator and held-out prediction as the only evidence source
- The loop uses a deterministic 200/75 visible-heldout split, semantic-cluster baselines, operationalized latent dimensions, held-out regression/classification metrics, nearest-neighbor preservation, and permutation/null baselines
- First-pass held-out evaluation found the strongest improvement for continuous assistant-axis prediction: best latent model R2 0.385 vs semantic baseline R2 0.301, delta +0.084
- Discrete activation-cluster classification did not improve over the semantic baseline: best latent accuracy 0.600 vs baseline 0.600
- Residual-proxy improvement was weak: best residual R2 0.300 vs baseline 0.290, delta +0.010, using a proxy residual target because the expected residual summary file was absent locally
- Most useful preliminary axis predictors were procedural-professional orientation, theatrical/fantastical vividness, assistant-basin adjacency, standards/error aversion, and semantic-label dependence risk

### Latent Feature Framing Ablation (2026-05-28)

- Compared motivational, interactional, procedural/operating-mode, narrative-causal, all-framing, and prior first-loop feature families on held-out PCA3D activation-coordinate prediction using existing local artifacts only
- The PCA artifact contained 273 personas with coordinates, yielding a 200 visible / 73 held-out deterministic split under the same seed as the first loop
- Semantic baseline PCA3D R2 was 0.322; the best model was the prior first-loop feature set at R2 0.436, delta +0.114
- The best new framing-only model was all framings combined at R2 0.405, delta +0.083; the best single new framing was procedural at R2 0.373, delta +0.051
- Improvement concentrated most on PC1 for the best model: PC1 R2 0.499, PC2 R2 0.353, PC3 R2 0.406
- Cluster prediction remained secondary and only slightly improved: baseline accuracy 0.616 vs best accuracy 0.630, delta +0.014

### Iterative Latent-Feature Outer Loop (2026-05-28)

- Implemented a finite outer-loop latent-feature discovery harness with five deterministic repeated splits, candidate-dimension retention/discard logic, permutation/null checks, split-variance tracking, and plateau termination
- Final retained feature set reached mean held-out PCA3D R2 0.492 across five splits versus semantic baseline R2 0.389, mean delta +0.103
- The loop retained 31 dimensions and terminated after two consecutive refinement iterations failed the meaningful-gain gate
- Stabilized feature families include procedural, assistant-adjacency, semantic-label-dependence, emotional-regulation, prior first-loop dimensions, motivational, interactional, narrative-causal, institutional, collective/distributed, and destabilization/reactivity
- Narrow edge-case refinements for mythic/artistic expression, developmental immaturity, social hospitality, nonhuman scale, forecast/control, and judicial norms were discarded under the retention policy
- Recurring high-residual personas across splits include mechanic, adolescent, prisoner, smuggler, infant, hermit, bard, teenager, predator, journalist, sage, and amateur

### Persona-Level Explanation Residual Ranking (2026-05-28)

- Ranked 273 personas by how well the final iterative outer-loop feature vocabulary predicts activation PCA3D placement
- Primary ranking uses mean held-out residual where a persona appeared in held-out splits; 221 personas had held-out prediction evidence, while 52 personas use apparent full-model residuals and are marked in the output
- Most effectively explained personas by final residual: designer, nomad, curator, chemist, and tulpa
- Least effectively explained personas by final residual: procrastinator, toddler, teenager, comedian, and cyborg
- Largest improvements over semantic baseline: jester (+27.347 residual reduction), robot (+26.346), wind (+26.271), gossip (+23.916), and poet (+22.722)
- Strongest worsening relative to semantic baseline: futurist (-26.250), veterinarian (-26.122), forecaster (-23.457), coordinator (-18.523), and producer (-16.241)
- Interpretation: high residuals are diagnostic cases for the current feature vocabulary, not proof that a persona is inherently inexplicable or that the retained dimensions are final

### Cross-Model Feature Transfer (2026-05-28)

- Compared Codex-derived retained outer-loop features and local Big Five features across canonical activation PCA3D and a reconstructed Big-Five pseudo-PCA3 target using the same five deterministic splits and semantic baseline
- Codex features improved canonical activation PCA3D prediction: R2 0.490 vs semantic baseline 0.389, delta +0.101, with mean residual reduction +2.042
- Big Five features transferred strongly to canonical activation PCA3D prediction: R2 0.613 vs semantic baseline 0.389, delta +0.223, with mean residual reduction +5.483
- Codex features did not robustly transfer to the Big-Five pseudo-PCA3 target: R2 0.280 vs baseline 0.269, delta +0.012, but mean residual reduction was negative at -0.041
- Big Five features predicted their own reconstructed pseudo-PCA target as a positive-control condition: R2 1.000 vs baseline 0.269, delta +0.731
- Interpretation: evidence supports asymmetric transfer, with Big Five features transferring to canonical activation geometry but Codex behavioral/procedural features not robustly transferring to the reconstructed Big-Five pseudo-PCA target
- Caveat: no separately committed Claude pseudo-PCA coordinate artifact was found; pseudo-PCA was reconstructed from `visualizations/bigfive_profiles.json`, which does not itself carry explicit Claude provenance metadata

### Shared Latent Feature Benchmark (2026-05-28)

- Created a canonical shared benchmark using 273 common personas, Codex canonical activation PCA3D coordinates, Claude's direct exported cluster-cosine pseudo-PCA3D target, the same five deterministic Codex outer-loop splits, and aligned semantic, Codex, Claude Big Five, Claude full, and combined feature matrices
- The direct Claude pseudo-PCA artifact supersedes the earlier reconstructed-target caveat for this benchmark: `claude_target_coordinates.csv` was loaded from the Claude branch rather than reconstructed from `bigfive_profiles.json`
- Big Five features transfer strongly to canonical activation PCA3D: R2 0.613 vs semantic baseline 0.389, delta +0.224, with mean residual reduction +5.465
- Codex retained features improve canonical activation PCA3D: R2 0.490 vs semantic baseline 0.389, delta +0.101, with mean residual reduction +2.042
- Codex retained features do not transfer to Claude's direct pseudo-PCA3D target over the semantic baseline: R2 0.166 vs baseline 0.167, delta -0.001, with mean residual change -0.019
- Claude Big Five features remain the strongest tested feature family for Claude pseudo-PCA3D: R2 0.243 vs semantic baseline 0.167, delta +0.076
- Combined Codex+Claude features do not outperform the best single feature family on either target in this aligned benchmark
- Interpretation: the evidence supports target-aligned Big Five transfer into canonical activation geometry, while Codex procedural/behavioral dimensions remain useful for canonical activation prediction but do not explain Claude's pseudo-PCA target beyond semantics

### Latent Feature Convergence Status (2026-05-28)

- Synthesized Codex/GPT-5.5 and Claude latent-feature analyses into a convergence-and-replicability planning memo
- Current best explanatory model is a continuous dispositional-behavioral manifold: Big Five-style traits explain broad global placement, while Codex procedural/motivational dimensions remain candidates for role-function and local residual explanation
- Big Five meaning analysis found strong trait-PC structure in canonical activation PCA: conscientiousness tracks PC1 positively (r=+0.824), openness tracks PC1 negatively (r=-0.779), extraversion tracks PC1 negatively (r=-0.692), neuroticism tracks PC1 negatively (r=-0.672), and agreeableness most strongly tracks PC3 (r=-0.477)
- Current best interpretation: PC1 separates careful/evaluative/procedural control from open/expressive/unstable or emotionally pressured organization; PC2 appears compound and less cleanly univariate; PC3 partly reflects cooperative-care versus antagonistic/disruptive stance
- What remains unreplicated: Claude has not yet searched for features that improve canonical activation PCA residuals after Big Five, and Codex has not yet shown a controlled hybrid model that beats Big Five
- Recommended next step: run a small local trait-plus-procedure hybrid benchmark on canonical activation PCA using Big Five as the baseline to beat, then ask Claude for a residual search only if a residual signal is plausible

### Codex Trait Replication Loop (2026-05-28)

- Ran a constrained Codex/GPT-5.5 trait-only replication loop on canonical Qwen activation PCA using the same 273 personas, five deterministic splits, semantic baseline, and ridge-regression evaluation path
- Allowed feature space was restricted to dispositional/trait concepts; procedural role labels, occupational functions, explicit operating modes, and narrative archetypes were excluded
- Final retained Codex trait model kept five core dimensions: organized reliability, imaginative flexibility, social expressivity, affiliative warmth, and threat reactivity
- Performance was weak but positive: R2 0.398 vs semantic baseline 0.389, delta +0.009; Claude Big Five remains much stronger at R2 0.613
- Codex trait model per-axis R2 was PC1 0.519, PC2 0.212, PC3 0.328, compared with Claude Big Five PC1 0.734, PC2 0.480, PC3 0.416
- Measured convergence to Claude Big Five was modest: mean best absolute correlation from retained Codex trait dimensions to Big Five columns was 0.152
- Interpretation: Codex independently rediscovered a weak trait-like signal under constraint, but did not replicate Claude Big Five's predictive efficiency; the result supports partial dispositional convergence, not a successful Big Five-level replication

### Hierarchical Trait-Procedural Model (2026-05-28)

- Built a two-stage held-out predictor of canonical Qwen activation PCA3D: Stage A used semantic controls plus Claude Big Five-style traits, and Stage B used selected Codex procedural/behavioral dimensions to predict Stage A residuals
- Trait baseline explained broad geometry at R2 0.613 with mean residual 21.748, reproducing the shared benchmark result under the same five deterministic splits
- Residualized procedural correction improved the integrated model to R2 0.622 with mean residual 21.524, a modest delta of +0.009 R2 and +0.224 residual reduction over the trait stage
- Naive concatenation did not improve over the trait stage: R2 0.613 and mean residual 21.768, supporting a residualized/layered interpretation more than a simple feature-union interpretation
- Procedural correction improved nearest-neighbor preservation from 0.232 to 0.252, suggesting the added signal is more local-topological than broad-cluster-level; cluster accuracy did not improve over the trait stage
- Bridge roles did not improve disproportionately overall: bridge mean improvement +0.049 vs non-bridge +0.553, though individual bridge roles such as wind, visionary, robot, specialist, evangelist, and bard improved strongly
- Developmental roles remained high residual after both stages: mean hierarchical residual 52.281 vs non-developmental 21.112
- Remaining high-residual cases were enriched for bridge, symbolic/liminal, and developmental structure; this supports a future descriptive third-layer hypothesis but does not yet justify fitting a symbolic/liminal correction model

### Residual Manifold Analysis (2026-05-28)

- Implemented a focused residual-manifold loop after the hierarchical trait-plus-procedural model, using full no-label prompts, no-label semantic-neighborhood structure, bridge/displacement metadata, residual histories, and canonical activation PCA context
- The search space was constrained to developmental dependency, incomplete proceduralization, identity formation, role ambiguity, liminal transition, volatile state transition, social dependency/constraint, collective/nonindividual agency, symbolic/nonprocedural identity, lawless improvisation, isolation, primitive embodiment, and semantic-neighborhood residual pressure
- The residual layer improved held-out PCA3D R2 from the hierarchical baseline 0.622 to 0.632, with mean residual reduced from 21.524 to 21.326
- Retained dimensions came from iterations 1 and 2; semantic bridge instability and original-to-no-label semantic displacement were discarded because they added negligible R2 and worsened mean residual
- Most improved held-out cases included criminal, toddler, prisoner, caveman, teenager, rogue, infant, hoarder, adolescent, fool, and detective
- Remaining high-residual cases after the residual layer include procrastinator, smuggler, daredevil, teenager, dilettante, hermit, idealist, loner, alien, toddler, cyborg, and swarm
- Developmental seed roles remain the clearest residual manifold: mean residual 39.834 vs 21.064 for non-developmental roles, with 4/5 developmental seed roles still in the top-25 residual set
- Symbolic/liminal clusters and collective/nonindividual prompt cases also remain elevated, supporting a narrow future diagnostic rather than an established third symbolic layer

### Residual SVD15 Interpretation (2026-05-28)

- Reconstructed and interpreted Claude's TF-IDF SVD15 residual signal from the committed Claude run script and local full no-label prompt corpus; Claude had not committed separate SVD vocabulary/loading artifacts
- Reconstruction exactly matched Claude's reported sem+BigFive+SVD15 result to rounding: R2 0.707 vs sem+BigFive baseline R2 0.613, delta +0.094, with SVD15 explaining only 0.138 of TF-IDF prompt variance
- The strongest activation-PC relation was SVD component 2, a nonhuman/entity-consciousness versus lived family/social-hardship contrast, correlated with PC2 at r=-0.608 and PC3 at r=+0.343
- Other interpretable components included professional specialization versus existential/liminal being-language, teaching/spiritual lived experience versus standards/evaluation roles, between-worlds/intercultural mediation versus stepwise planning, outlaw/survivor/story-role texture versus collective/student/entity identity, and helping/health/guidance versus abstract analytic forecasting expertise
- Hand-named residual dimensions were only partially supported: developmental dependency, role ambiguity, and semantic-neighborhood residual pressure had the strongest component alignments, while incomplete proceduralization, identity formation, liminality, collective agency, and symbolic identity appeared diffuse across multiple SVD axes
- Interpretation: abstract residual labels underfit because they collapse many weak concrete text cues, while SVD15 preserves granular prompt texture and semantic-neighborhood variation; the next step is to distill SVD extremes into concrete human-readable residual features and retest them

### PC3 Hypothesis Evaluation (2026-05-29)

- Evaluated the working PC3 interpretation adversarially using PC1/PC2-neighbor pair contrasts, a description-only blind rubric, seven competing lexical hypotheses, cluster enrichment checks, and residual analysis
- The blind preserve-minus-challenge/exploit rubric predicted PC3 only weakly to moderately: continuous score r=-0.312 and ordinal rubric r=-0.318, with the sign indicating lower PC3 for preserving/nurturing roles and higher PC3 for challenging/exploiting/competitive roles
- Alternative-hypothesis search found `nurturing_vs_competitive` slightly strongest at r=-0.319, while the target `system_preserving_vs_exploiting` hypothesis ranked second at r=-0.308
- PC3 is strongly enriched in combative/trickster regions: combative_iconoclast mean PC3 25.78 with 93% above the global upper quartile, and trickster_chaos mean PC3 23.03 with 80% above the upper quartile, though both clusters overlap the rest of the distribution
- Agreeableness remains the strongest Big Five correlate of PC3 at r=-0.477, while Big Five and hierarchical residual magnitudes correlate only weakly with PC3
- Interpretation: the preserving/exploiting hypothesis partially survives but is too narrow; the current best phrasing is a cooperative-care/system-stabilization versus antagonistic-disruptive/transgressive-register axis, with moderate-low confidence pending paired no-label falsification tests

### Blinded PCA-Axis Rubric Validation (2026-05-29)

- Ran a coordinate-blind validation using the full available no-label persona prompt corpus: 1,375 rewritten prompt records covering all 275 personas, five prompts per persona
- Scoring used deterministic local lexical-semantic rubric proxies over no-label prompt text only; persona names, PCA coordinates, clusters, residuals, and prior labels were excluded until after scoring
- Target-aligned correlations were positive but modest: PC1 objective-certainty r=0.247, PC2 fragmented/coherent-uncertainty r=0.224, and PC3 antagonistic-transgressive r=0.349
- Matched-pair validation was weak: PC1 35%, PC2 40%, and PC3 40% direction-match rates over the top 20 close-orthogonal pairs per axis, with many failures caused by tied lexical scores
- Regression from the three main rubric scores produced low cross-validated R2: PC1 0.065, PC2 0.024, and PC3 0.116; expanded PC2 alternatives improved PC1/PC3 prediction but not PC2
- Interpretation: this does not cleanly validate the working axis interpretations from no-label prompt text alone; PC3 receives the strongest modest support, PC1 is positive but weaker than expected, and PC2 remains the least certain
- Caveat: this is a local lexical proxy study, not a true independent human or LLM blinded-rating study; the next test should use richer full rollout responses or independent blinded raters

### Reading-Based Blinded PCA-Axis Rater Study (2026-05-29)

- Ran a true reading-based Codex/GPT-5.5 rater study over anonymized no-label persona dossiers: 275 personas, five rewritten prompts per persona, with persona names/PCA coordinates/clusters/Big Five/residuals hidden from the rater
- Full 275-persona rollout-response corpora were not found locally; full response corpora exist for trickster/editor and dyad subsets only, so this study validates against persona operationalization text rather than generated rollout behavior
- Target-aligned reading-based correlations were materially stronger than the lexical-proxy screen: PC1 objective-certainty r=0.558, PC2 coherent-action-under-uncertainty r=0.373, and PC3 antagonistic-transgressive r=0.690
- Matched-pair validation improved sharply: PC1 75%, PC2 100%, and PC3 95% direction-match rates over the top 20 close-orthogonal pairs per axis
- Three main rater scores predicted held-out PCA coordinates with CV R2: PC1 0.496, PC2 0.101, and PC3 0.522; expanded PC2 alternatives raised CV R2 to PC1 0.616, PC2 0.564, and PC3 0.686
- PC3 is now the best-supported direct axis interpretation in the prompt-dossier evidence; PC1 is strengthened but partly entangled with intelligence/expertise; PC2 remains the main uncertainty because abstraction correlates more strongly with PC2 than the direct coherent-action score
- Caveat: scoring used Codex-as-rater, not an independent local LLM or human rater, and the corpus is no-label system-prompt text rather than full rollout responses

### Professional Hierarchy Validation (2026-05-30)

- Ran a targeted professional-role validation over 102 professional, technical, scientific, analytical, academic, and expert personas present in the Qwen geometry and no-label prompt corpus
- Codex/GPT-5.5 rated anonymized no-label professional dossiers before PCA evaluation on objective certainty, coherent action under unresolved uncertainty, and system perturbation
- PC1 received targeted professional support: objective certainty correlated with actual PC1 at r=0.394, and the high-PC1 professional pole contains auditor, examiner, evaluator, validator, screener, reviewer, and grader-like roles
- PC3 received modest targeted support: system perturbation correlated with actual PC3 at r=0.319, and the three-rating model predicted professional PC3 with CV R2=0.429
- PC2 was not supported as a professional coherent-action hierarchy: coherent uncertainty capacity was essentially uncorrelated with actual PC2 at r=-0.007
- Scientist vs physicist weakly supports the actual abstraction ordering because physicist is lower on PC2 than scientist, but the blinded rating gave them similar coherent-uncertainty capacity scores
- Interpretation: PC1 remains moderate-confidence; PC3 remains moderate with professional counterexamples; PC2 should be reframed away from simple professional uncertainty capacity and toward abstraction/historical-theoretical/world-model depth unless future tests separate those factors more cleanly

### PC2 Conditional Validation After PC1 Control (2026-05-30)

- Ran a conditional PC2 validation over 273 personas common to canonical Qwen PCA coordinates and the blinded no-label dossier score table
- PC1 was controlled approximately by 10 percentile bands, then residual PC2 variation was tested against maturity, abstraction, expertise, uncertainty exposure, residence time under uncertainty, and coherent action under unresolved uncertainty
- Abstraction was the strongest pooled band-demeaned predictor of PC2: Pearson r=-0.618, Spearman r=-0.597, R2=0.382
- Coherent action under unresolved uncertainty remained weaker but nonzero: Pearson r=+0.427, Spearman r=+0.334, R2=0.182
- Uncertainty exposure failed as a residual explanation after PC1 control: Pearson r=-0.026 and R2=0.001
- Matched-pair and mythic/developmental tests support revising PC2 from a coherent-action-only axis to an abstraction/integration/developmental axis, with coherent action retained as a secondary behavioral expression
- Strongest support: teenager vs crystalline at nearly matched PC1 shows high-PC2 developmental/reactive structure against low-PC2 abstraction/integration
- Strongest counterexample: adolescent vs parasite shows a high-PC2 member with higher abstraction by 21 points, warning that abstraction is not a complete one-variable explanation

### PC3 Perturbation-Stabilization Validation (2026-05-30)

- Ran a full-distribution PC3 validation over all 275 personas using persona name plus neutral eval-prompt definition only; PCA coordinates and clusters were joined after scoring
- Perturbation-stabilization score predicted PC3 globally: Pearson r=0.529, Spearman r=0.511, and cluster-controlled Pearson r=0.491
- Within-cluster pairwise ordering accuracy was 0.773 overall, strongest in mythic_spiritual (0.848) and procedural_professional (0.802), but weak in grounded_social (0.565)
- Negative controls were weaker than the target rubric: moral_badness Pearson r=0.201, professionalism r=0.103, weirdness/fantasticality r=0.029, and abstraction r=0.129
- Interpretation: PC3 shows suggestive but incomplete support for perturbation-stabilization; cooperative-antagonistic remains a secondary or partial reading, and independent blinded human or second-model rating is the next validation step

### Trait-Space Axis Interpretation (2026-05-30)

- Ran direct PCA over 240 raw Qwen/Qwen3-32B layer-48 trait vectors from `downloads/hf_vectors/qwen-3-32b/trait_vectors/`; each `[64, 5120]` tensor was mean-pooled to one 5120-D vector
- Trait PCA explained variance: PC1 0.353, PC2 0.168, PC3 0.134, cumulative PC1-PC3 0.655
- Trait PC1 moderately aligns with persona PC1 in activation-space direction cosine, abs=0.681, but trait PC2 and PC3 weakly align with persona PC2/PC3, abs=0.194 and 0.065
- Streamlined trait-axis interpretations: PC1 controlled seriousness/formal composure vs playful irreverence/expressive volatility; PC2 cold detachment/hard-edged abstraction vs warm accessibility/affiliative care; PC3 plain practical groundedness vs ornate symbolic/theatrical expressivity
- Trait-only PC3 did not independently validate perturbation-stabilization: name-based perturbation/stabilization score correlated weakly with trait PC3, Pearson=-0.074 and Spearman=-0.104, while moral valence was near zero
- Trait-space cone testing did not reproduce the simple persona-space cone pattern: lowest-PC1 vs highest-PC1 radial spread ratio was 0.863, and secondary variation did not expand as PC1 decreased
- Interpretation: trait vectors strongly reconstruct persona geometry through cosine profiles, but direct trait-space PCA is not the same object as persona-space PCA; this supports a layered shared-geometry model rather than a simple trait-axis reduction

### Trait Prompt Artifact Inventory and Forecasting Readiness (2026-05-30)

- Verified 240 local trait prompt JSON artifacts under `data/traits/instructions/`, exactly matching the 240 Qwen/Qwen3-32B layer-48 trait vector names
- Verified local role prompt artifacts under `data/roles/instructions/`: 276 files because `default.json` is included, while Qwen `role_vectors/` contains the expected 275 role/persona vectors
- Retrieved and inspected `belmore/assistant-axis-vector-prompts` (`train.parquet`, SHA `57424a9d6075a44196b935983ce1fa4e83191679`), which contains 516 rows: 275 roles, 240 traits, and 1 default row
- Trait artifacts include descriptions, five positive instructions, five negative instructions, forty behavioral questions, and a 0-100 eval prompt with refusal handling
- Exact trait-name match across local artifacts, Belmore prompt rows, and Qwen trait vectors is 240/240, with no missing, extra, or normalization-required names
- Interpretation: prompt-to-geometry forecasting is ready as a dataset-construction task; the first version should use holdout-by-trait splits and exclude eval prompts or target labels for leakage-controlled forecasting

### Prompt-To-Geometry Forecasting on Held-Out Concepts (2026-05-30)

- Built concept-level forecasting datasets from released role and trait prompt artifacts, with one row per concept per text variant rather than splitting individual prompt rows
- Excluded eval prompts from all variants; leakage-control variant additionally replaced explicit target names with `[TARGET]`
- Critical trait split held out 40 complete traits and trained on 200 complete traits; role split held out 55 complete roles
- Best held-out trait model was elastic-net TF-IDF on leakage-control text: mean R2=0.389, PC1 R2=0.414, PC2 R2=0.304, PC3 R2=0.450; Pearson r=0.656/0.602/0.708
- Best held-out role model was elastic-net TF-IDF on leakage-control text: mean R2=0.621, PC1 R2=0.783, PC2 R2=0.577, PC3 R2=0.504; Pearson r=0.887/0.772/0.732
- Nearest-neighbor semantic retrieval was weak on held-out leakage-control traits, mean R2=-0.021, so the linear model adds predictive structure beyond copying the closest training artifact
- Interpretation: prompt text contains substantial predictive information about released geometry on unseen concepts, but this remains artifact-to-geometry forecasting rather than a new activation-generation or control-system result

### PC1/PC2 Forcing-Function Interpretation Notes (2026-05-30)

- Created `research/outputs/axis_forcing_function_notes/pc1_pc2_forcing_function_note.md`, `judge_rubric_design_notes.md`, and `axis_interpretation_method_sequence.md`
- PC1 is now framed as convergence pressure versus degrees of freedom, not merely assistantness or careful evaluation; evaluator-like roles are endpoint evidence, while the causal/geometric hypothesis is constraint toward correctness, validation, procedure, evidence, or error correction
- PC2 is now framed as integrated abstraction versus situated developmental immediacy, with an admissibility constraint: some personas lack the prerequisites for reflective synthesis or accumulated world-model structure without ceasing to be that persona
- The notes preserve the numerical context: semantic baseline around R2 0.389, procedural features around R2 0.490, Big Five-style features around R2 0.613, richer combined models around R2 0.707, and prompt-to-geometry forecasting results for held-out traits and roles
- Status: hypothesis to be operationalized through judge rubrics; the next test is whether forcing-function rubric scores improve held-out prompt-to-geometry forecasting beyond text embeddings

### Cluster-Conditioned PC1/PC2 Axis Tests (2026-05-30)

- Tested whether cluster-conditioned interpretation improves PC1 and PC2 prediction using 275 role/persona PCA coordinates, canonical cluster labels, and existing blinded rater annotations
- Simple within-cluster pairwise ordering was not easier: PC1 global accuracy 0.709 vs within-cluster 0.622; PC2 global accuracy 0.746 vs within-cluster 0.687
- Cluster-conditioned regression improved calibrated prediction: PC1 direct R2 0.296 vs oracle-cluster R2 0.811; PC2 direct R2 0.416 vs oracle-cluster R2 0.718
- Text-to-cluster classification from blinded dossier text reached 0.687 held-out accuracy and 0.404 macro F1; predicted-cluster conditioning retained part of the benefit for PC1 (R2 0.647) and less for PC2 (R2 0.520)
- Interpretation: cluster identity helps as an intercept/slope interaction, not because within-cluster pair ordering is easier; PC1 can use direct judging for simplicity, while PC2 benefits from cluster-conditioned analysis but should avoid hard predicted clusters in deployment unless classifier accuracy improves

### Novel Prompt Battery for H100 Geometry Validation (2026-05-30)

- Built `research/outputs/novel_prompt_battery/` as a frozen 120-prompt validation battery for future H100 measurement of predicted prompt geometry
- Retrained and serialized the selected role-trained leakage-control elastic-net TF-IDF forecaster; stable model hash is `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Generated 1,036 candidate prompts from behavioral region templates without external API calls and without explicit persona role labels; final battery has zero explicit role-name flags
- Final prompt families: 52 mixed-boundary, 24 manual holdout, 19 cluster-region, 13 safety-adjacent, and 12 neutral-control prompts
- Leakage checks against released artifacts were low: max approximate artifact similarity 0.205, mean 0.069
- Coverage is partial: 11/27 quantile target cells populated; high-PC1 and high-PC2 target regions remain under-covered by the current natural-prompt generation strategy
- Interpretation: H100 validation is feasible using `h100_prompt_run_manifest.csv`, but the battery should be described as a partial geometric validation set rather than complete coverage

### Adaptive High-PC3 / High-PC2 Prompt Battery Expansion (2026-05-30)

- Built `research/outputs/novel_prompt_battery_expansion/` as a targeted 60-prompt supplement using the frozen role-trained leakage-control elastic-net TF-IDF forecaster, hash `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- The adaptive loop logged 516 generated candidates, coordinate-error feedback, acceptance/rejection status, leakage scores, explicit-role flags, and safety flags
- Supplemental prompt counts: 26 mixed-boundary, 22 cluster-region, and 12 safety-adjacent prompts
- High-frontier coverage improved: 38 supplemental prompts are above the prior PC3 75th percentile, 44 are above the prior PC2 75th percentile, 12 are safety-adjacent high-PC3, and 26 are mixed-boundary high-PC3
- Combined battery now has 180 prompts and improves quantile target-cell coverage from 11/27 to 16/27
- Leakage/safety checks passed for the supplement: zero explicit role-name flags, zero operational-harm flags, max artifact similarity 0.104, mean artifact similarity 0.069
- Interpretation: the combined battery is ready for H100 validation as a targeted high-PC3/high-PC2 frontier probe, while high-PC1 and several exact 3D target cells remain under-covered

### Percentile-Edge Prompt Battery for H100 Validation (2026-05-30)

- Built `research/outputs/novel_prompt_battery_percentile_edges/` as the final edge-heavy prompt battery referenced to inherited role/persona PCA percentiles from `research/visualizations/geometry_viz_data.json`
- Inherited thresholds: PC1 p20=-32.056, p35=-13.924, p65=19.979, p80=31.909; PC2 p20=-16.333, p35=-8.534, p65=4.215, p80=16.307; PC3 p20=-11.810, p35=-5.698, p65=4.816, p80=11.642
- The frozen role-trained leakage-control elastic-net TF-IDF forecaster hash was verified before scoring: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Final battery has 100 prompts and passes all predefined readiness criteria: PC1 lower 12/8, PC1 upper 11/8, PC2 lower 34/8, PC2 upper 8/8, PC3 lower 8/8, PC3 upper 16/8, shoulder/edge 58/12, interior controls 20/20, final size 100/100, filters pass
- Generation log preserves 200 generated candidates and 168 rejected candidates; rejection reasons were coordinate_miss 159, criterion_already_met 8, and duplicate_or_near_duplicate 1
- Leakage/safety checks passed: zero explicit role-name flags, zero operational-harm flags, max artifact similarity 0.133, mean artifact similarity 0.071
- H100 readiness judgment: ready; recommended manifest is `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv`

### Pre-H100 Methods Memorial (2026-05-30)

- Created `research/outputs/pre_h100_methods_memorial/` to memorialize the full pre-H100 preparation process before activation validation changes the state
- The memorial distinguishes descriptive persona geometry, explanatory modeling, prompt-to-geometry forecasting, prompt-battery construction, and pending H100 activation validation
- It records the chosen H100 manifest, frozen forecaster hash, final percentile-edge pass table, assumptions required for interpretability, smoke/checkpoint/early-stop plan, and success/failure interpretations
- Current status: pre-H100 preparation is complete, but no claim has yet been established that the forecaster predicts actual response activations on novel prompts

### Percentile-Edge H100 Activation Validation (2026-05-31)

- Ran the full 100-prompt percentile-edge validation battery through Qwen/Qwen3-32B response generation and layer-48 response-token activation extraction on an A100 SXM 80GB RunPod instance
- Existing persona PCA projection was reconstructed from all 275 Qwen role vectors and verified against committed canonical coordinates before use: max abs reproduction error 1.21e-06
- Final forecast-vs-observed correlations were positive on all three PCs: PC1 Pearson 0.691 / Spearman 0.696, PC2 Pearson 0.643 / Spearman 0.594, PC3 Pearson 0.491 / Spearman 0.343
- PC1 showed calibrated predictive value as well as rank correlation, with R2 0.321; PC2 and PC3 remained poorly calibrated with R2 -2.721 and -0.243 despite positive correlations
- Mean 3D Euclidean error was 37.29, median 36.42, and max 80.21; largest residual was `peb_001`
- Runtime was stable after cached load: 100-prompt full phase 1631.7 seconds at an estimated $0.68 full-phase compute cost; no early stop triggered
- Interpretation: the validation supports prompt-to-geometry forecastability as a proof of concept, especially for rank/order structure, while motivating a follow-up calibration/error analysis for PC2 and PC3

### H100 Forecast-Observed Regional Error Geometry (2026-05-31)

- Built `research/outputs/h100_percentile_edge_validation_error_analysis/` with per-prompt error vectors, six-tail regional breakdowns, shoulder/edge breakdowns, and interactive 3D/2D forecast-to-observed arrow visualizations
- Verified 100/100 prompts have predicted and observed PC1/PC2/PC3; overall mean signed delta vector was (-9.114, +28.342, -8.151), mean 3D error was 37.291, median 36.419, and center-collapse rate was 0.280
- Errors are structured and axis-biased rather than random: PC2 observations shift strongly upward relative to forecasts, and PC3-high forecasts shift downward on PC3
- Forecasted tail retention: PC1 lower 0.750, PC1 upper 0.000, PC2 lower 0.000, PC2 upper 1.000, PC3 lower 1.000, PC3 upper 0.000
- Highest forecast-tail mean 3D error was PC2 upper tail at 44.344; PC3-high forecasts produced 0/16 observed PC3-high tail activations, weakening absolute high-PC3 address claims despite positive full-run PC3 correlation
- Recommendation: fit an axis-wise calibration layer first, then test region-aware correction; increase safety-adjacent sample size before making a standalone safety-directionality claim

### H100 Diagnostic Follow-Up Checklist and First Pass (2026-05-31)

- Created persistent checklist `research/outputs/h100_diagnostic_followups/diagnostic_followup_checklist.md` with D01-D09 and status/evidence/next-action discipline
- D01 methodology verification found no blocking projection discrepancy: model ID matched, PCA basis was reconstructed from 275 Qwen role vectors, and committed coordinate reproduction max abs error remained 1.207e-06
- D01 remains in progress because source extraction equivalence is not fully line-by-line verified: layer-index convention, source chat template, and output-hidden-states versus hook-based post-MLP residual extraction remain open checks
- First-pass anomaly diagnostics identified cone-violation candidates, extreme-PC1/near-zero-PC3 forecast-origin cases, low-PC2 upward-shift cases, PC3-high collapse cases, and top 3D residual cases
- PC3-high collapse pass supports a response-neutralization hypothesis: forecasted PC3-high prompts had mean delta_pc3 -18.705 and 0/16 observed high-PC3 retention; largest downward cases moved near roles such as `provincial`, `student`, and `addict`
- Prompt-generation audit found repeated scaffolds in accepted generated prompts and final battery prompts, so the percentile-edge battery remains valid as a forecaster stress test but not a clean natural-language generalization benchmark
- Preliminary axis-wise LOOCV calibration improved apparent R2: PC1 0.463, PC2 0.390, PC3 0.211; this is a next-step target, not a resolved fix

### Training Forecast Error Geometry (2026-05-31)

- Built `research/outputs/training_forecast_error_geometry/` to compare frozen forecaster predictions against original role/persona target coordinates, using target-to-forecast arrows over inherited persona geometry
- Per-example role predictions were not saved in the original forecasting outputs, so they were recomputed from the serialized frozen role-trained leakage-control elastic-net TF-IDF forecaster; stable model hash verified as `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Frozen-model native target-to-forecast error is tiny because the design forecaster was retrained on all 275 role artifacts: mean 3D error 0.843, PC1/PC2/PC3 R2 all approximately 0.999-1.000
- Native forecasts do show shrinkage toward the origin: 0.898 of forecasts are closer to the origin than their targets, with mean radial movement toward origin 0.615
- Native role-artifact forecasts do not reproduce the H100 error pattern: H100 mean 3D error 37.291, H100 observed-minus-forecast PC2 bias +28.342, while native forecast-minus-target PC2 bias is approximately zero; H100 forecast |PC3|<=5 is 0.530 versus native 0.291
- Interpretation: H100 PC2 upward shift and PC3-high collapse are not explained by native frozen-forecaster target-to-forecast error alone; they likely arise during prompt-generation/response-activation measurement or from the edge-battery stress-test distribution

### Extraction Equivalence Audit (2026-05-31)

- Built `research/outputs/extraction_equivalence_audit/` to compare original/local Assistant Axis extraction code, prior adaptive trickster/editor extraction, and the H100 percentile-edge extraction runner
- Prior successful trickster replication used Qwen/Qwen3-32B layer 48, thinking disabled, response-token mean pooling, and a forward hook on `model.model.layers[48]`; the score>=2 vector matched the downloaded trickster vector at cosine 0.957557
- Current H100 validation uses the same model identity and intended layer number, excludes prompt tokens, mean-pools generated response tokens, and projects with a PCA basis that reproduces committed canonical coordinates at max abs error 1.207e-06
- D01 remains `in_progress`: local source and prior adaptive extraction are hook-based, while H100 reads `out.hidden_states[48]`; source inspection did not prove those activation objects are identical for Qwen/Qwen3-32B
- Interpretation: H100 PC2/PC3 anomalies remain informative, but they retain a bounded activation-site caveat until a minimal hook-vs-hidden-states equivalence test is run

### H100 Methodological Dependency Tracks (2026-05-31)

- Added `research/outputs/h100_diagnostic_followups/methodological_dependency_tracks.md` and updated the persistent checklist so D01-D09 should not be closed in isolation when a governing T-track remains open
- T01 extraction equivalence / activation boundary is critical and covers D01 directly; D02 cone-violation outliers should not be resolved until T01 closes
- T02 forecaster improvement and T03 prompt-battery construction cover D03/D08 origin-plane and forecaster-exploitation concerns
- T04 response-state uncertainty covers the centroid-versus-single-sample mismatch behind D04/D05 PC2 upward shift and D06 PC3-high collapse, alongside the T01 activation-boundary caveat
- Recommended order: close T01, advance T02 instance-level prompt-to-centroid forecasting, rebuild/recalibrate the prompt battery under T03, then design the T04 small multi-sample GPU spread study

### Playwright Within-Role Displacement Scoring (2026-05-31)

- Prepared `research/outputs/playwright_displacement_scoring/` as a local no-GPU forecast packet for the user-selected target role `playwright`
- Scored 240 shared extraction questions role-independently and five positive playwright instructions role-specifically using the current PC1/PC2/PC3 displacement rubric
- Constructed the full 1,200-row playwright instruction-question additive forecast grid with the available playwright centroid coordinates: PC1 -9.818, PC2 4.586, PC3 4.301, cluster `grounded_social`
- Question-score coverage is usable but uneven: PC1 has 1 negative, 16 positive, and 223 zero-scored questions; PC2 has 16 negative, 42 positive, and 182 zero; PC3 has 10 negative, 3 positive, and 227 zero
- Playwright instructions are predicted to push mostly toward negative PC1 and positive PC2, with weak positive/neutral PC3
- Caveat: these are rubric-based predicted displacement pressures, not observed activation movement; manual review of thin PC1-negative and PC3-positive coverage is recommended before any corrected-hook GPU run

### Big Five Geometry Overlay Visualization (2026-05-29)

- Added Big Five-style LLM-assigned trait overlays to the persona geometry viewer using `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_full_feature_matrix.csv`
- The selected source is the shared benchmark feature matrix whose `claude_bigfive` feature set predicts canonical activation PCA3D at R2 0.613 vs semantic baseline R2 0.389
- Overlay data covers 275 geometry personas, with Big Five scores available for 273; `coral_reef` and `devils_advocate` are present in the geometry but missing from the benchmark feature matrix
- The viewer now supports continuous color modes for openness, conscientiousness, extraversion, agreeableness, neuroticism, Big Five residual magnitude, and categorical dominant-trait coloring
- Caveat: these are LLM-assigned Big Five-style features, not true psychological measurements

### Codex GPT-5.5 Judge Substitution

The Lu et al. path uses `gpt-4.1-mini` as the role-expression judge. Current trickster and editor adaptive scoring used Codex GPT-5.5 Standard as a pragmatic substitute. This must be disclosed and should not be described as strict Lu-method replication.

### Adaptive Stopping

The project now uses an adaptive extraction protocol for operational efficiency. The provisional rule is 64 qualifying responses as a conservative target, with adaptive stopping permitted once convergence criteria pass at n>=16. This is a methodological extension beyond the fixed Lu-style rollout framing.

### Chunked Generation

Editor was tested with a 128-rollout chunk rather than a full 1200-rollout run. This was intentional for the second-persona generalization test and should not be conflated with exhaustive Lu-style extraction.

### Truncation as Covariate

High truncation is tracked explicitly rather than silently filtered. Trickster truncation did not materially destabilize geometry; editor token-cap results suggest truncation reduction does not necessarily improve role-expression yield.

## Current Blockers

The next editor experiment is blocked on revised anchoring methodology. More identical editor rollouts are unlikely to answer the failure mode cleanly.

Strict Lu-method replication remains blocked unless `gpt-4.1-mini` judge scoring is restored and run with documented filter choices.

Evaluator-sensitivity comparison remains blocked by OpenAI API quota. The local harness, canonical corpora mapping, Codex-side imported baseline, and output schema now exist under `research/q2_stability/qwen/evaluator_sensitivity/`, but `gpt-4.1-mini` returned `insufficient_quota` and produced zero paired judge records.

Downloaded Lu vector metadata remains underspecified locally: the exact fully-roleplaying versus somewhat-roleplaying storage category and retained-response IDs are not documented in local HF metadata. The earlier "fixed 64-row selection" framing is corrected: public Qwen vector tensors are `[64,5120]` because Qwen has 64 layers, not because vectors store 64 retained rollout examples.

## Next Empirical Tests

1. Finish evaluator-model sensitivity if API access permits, because it is the main unfinished methodological item for Paper 1.5.
2. Draft Paper 1.5 around layered persona-geometry interpretation rather than adaptive extraction replication.
3. Prepare local centroid perturbation experiments around Trickster, Actor, Therapist, and Spy as Paper 2 or grant-supported work.
4. Launch the bounded 800-rollout no-label activation-space stress test once compute is approved.
5. Run OpenAI-side Stage-1 role-inventory generation and ingest Claude-generated inventories once they are synced through GitHub.
6. Design a revised editor anchoring methodology only if assistant-adjacent extraction becomes an explicit follow-up target.
