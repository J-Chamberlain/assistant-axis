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

Downloaded Lu vector metadata remains underspecified locally: the exact fully-roleplaying versus somewhat-roleplaying storage category and fixed 64-row selection procedure are not documented in local HF metadata.

## Next Empirical Tests

1. Finish evaluator-model sensitivity if API access permits, because it is the main unfinished methodological item for Paper 1.5.
2. Draft Paper 1.5 around layered persona-geometry interpretation rather than adaptive extraction replication.
3. Prepare local centroid perturbation experiments around Trickster, Actor, Therapist, and Spy as Paper 2 or grant-supported work.
4. Launch the bounded 800-rollout no-label activation-space stress test once compute is approved.
5. Run OpenAI-side Stage-1 role-inventory generation and ingest Claude-generated inventories once they are synced through GitHub.
6. Design a revised editor anchoring methodology only if assistant-adjacent extraction becomes an explicit follow-up target.
