# Claims Register

Canonical startup file: yes
State role: canonical claim status
Last updated: 2026-05-30

This register separates project findings from interpretations. It is intentionally compact: use it to orient a new thread, then verify details in `RESEARCH_STATE.md`, `FINDINGS_LEDGER.md`, `RESEARCH_INDEX.md`, and the cited artifacts.

Status labels:

- Observed: directly measured or produced by a completed run.
- Supported: supported by multiple analyses, but still an interpretation or dependent on modeling choices.
- Tentative: plausible and useful, but not yet stable across enough tests.
- Speculative: hypothesis or framing that still needs direct validation.

## 1. Persona Geometry Is Low-Dimensional

Claim: Persona vectors exhibit meaningful low-dimensional structure, including PCA axes that organize roles non-randomly.
Status: Supported
Evidence: Qwen visualization PCA shows PC1 explains 0.315954 of variance; Paper 1 and Paper 1.5 analyses repeatedly recover structured PC/cluster relationships.
Counterevidence: Later residual/SVD work shows that multiple layered features are needed for strong prediction; low-dimensional structure is not the whole geometry.
Dependencies: `research/visualizations/geometry_viz_data.json`, `research/RESEARCH_INDEX.md`
Last Updated: 2026-05-30

## 2. Assistant Axis Aligns Strongly With PC1

Claim: In current Qwen role-vector geometry, PC1 aligns strongly with the assistant-axis direction.
Status: Observed
Evidence: PC1-assistant-axis alignment is 0.802310 in the visualization/PCA data.
Counterevidence: PC1 should not be reduced to literal assistantness; rater studies suggest objective certainty, expertise, and procedural competence also contribute.
Dependencies: `research/visualizations/geometry_viz_data.json`, `research/visualizations/persona_geometry_explorer.html`
Last Updated: 2026-05-30

## 3. Careful Evaluator Occupies a Privileged Basin

Claim: The assistant/evaluator region is dominated by careful, evaluative, standards-oriented roles.
Status: Supported
Evidence: Paper 1 Gemma result; Qwen professional validation places auditor/examiner/evaluator/validator/screener/grader near the high-PC1 professional pole.
Counterevidence: Qwen and Gemma differ in details; evaluator dominance should not be generalized to all models without model-specific checks.
Dependencies: `research/FINDINGS_LEDGER.md`, `research/q2_stability/qwen/outputs/professional_hierarchy_validation/`
Last Updated: 2026-05-30

## 4. Base Models Already Contain Persona Geometry

Claim: Persona geometry is not only a post-training artifact; base models show relevant geometric basins.
Status: Supported
Evidence: Gemma base-model drift work found careful evaluator basin behavior in base model.
Counterevidence: Base Gemma rankings can invert relative to instruction-tuned geometry; post-training still strongly reshapes expression.
Dependencies: `research/RESEARCH_STATE.md`, `research/FINDINGS_LEDGER.md`
Last Updated: 2026-05-30

## 5. RLHF Primarily Reweights Existing Persona Geometry

Claim: Instruction tuning/RLHF may reweight or expose pre-existing persona basins rather than creating them from scratch.
Status: Tentative
Evidence: Base-model basin finding supports pre-existing structure.
Counterevidence: Evidence is currently strongest for Gemma and not enough to generalize broadly; base/instruct inversions show reweighting can be substantial.
Dependencies: base-model drift outputs summarized in `research/RESEARCH_STATE.md`
Last Updated: 2026-05-30

## 6. Big Five-Style Features Predict Activation PCA Better Than Semantic Baseline

Claim: LLM-assigned Big Five-style features substantially improve prediction of canonical Qwen activation PCA3D over semantic baseline.
Status: Observed
Evidence: Shared benchmark: Claude Big Five R2 0.613 vs semantic baseline R2 0.389.
Counterevidence: Big Five scores are LLM-assigned features, not psychological measurements; feature provenance is model-dependent.
Dependencies: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`
Last Updated: 2026-05-30

## 7. Procedural Features Independently Predict Meaningful Geometry

Claim: Codex procedural/behavioral features predict activation geometry beyond semantic baseline.
Status: Supported
Evidence: Shared benchmark: Codex retained features R2 0.490 vs semantic baseline R2 0.389.
Counterevidence: They remain weaker than Big Five globally and do not transfer cleanly to Claude pseudo-PCA targets.
Dependencies: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`
Last Updated: 2026-05-30

## 8. Hierarchical Trait-to-Procedural Model Improves Prediction

Claim: A residualized hierarchy in which Big Five explains broad placement and procedural features explain residual structure improves prediction.
Status: Supported
Evidence: Hierarchical model R2 0.622 vs Big Five trait stage R2 0.613.
Counterevidence: Improvement is modest; naive concatenation did not beat the trait stage.
Dependencies: `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/`
Last Updated: 2026-05-30

## 9. Residual Manifold Features Add a Small Diagnostic Layer

Claim: Developmental/liminal/collective residual features add a small third-layer improvement after semantic, trait, and procedural models.
Status: Tentative
Evidence: Residual manifold model R2 0.632 vs hierarchical baseline R2 0.622.
Counterevidence: The gain is small and diagnostic; it does not establish a solved residual ontology.
Dependencies: `research/q2_stability/qwen/outputs/residual_manifold_analysis/`
Last Updated: 2026-05-30

## 10. Residual SVD Structure Strongly Improves Prediction

Claim: TF-IDF/SVD prompt-register structure improves prediction of canonical activation PCA more than hand-named residual features.
Status: Observed
Evidence: Sem+BigFive+SVD15 reaches R2 0.707 vs sem+BigFive R2 0.613.
Counterevidence: This may exploit lexical/register artifacts; it is not yet distilled into stable human-readable factors.
Dependencies: `research/q2_stability/qwen/outputs/residual_svd_interpretation/`
Last Updated: 2026-05-30

## 11. Semantic Topology Partially Predicts Activation Geometry

Claim: Prompt-space semantic topology is structured and partially predicts activation topology, but does not explain it away.
Status: Supported
Evidence: Semantic-vs-activation comparisons show modest activation-distance prediction and partial cluster overlap.
Counterevidence: Activation clusters are only weakly recoverable from role-name or prompt semantics alone.
Dependencies: `research/assistant_axis_methodology/semantic_vs_activation_geometry/`, `research/assistant_axis_methodology/cluster_overlap_analysis.md`
Last Updated: 2026-05-30

## 12. Explicit Role-Label Exposure Is a Methodological Caveat

Claim: Lu-style role prompts include extensive direct role-label exposure.
Status: Observed
Evidence: Label-exposure audit found 1280/1375 prompts, 93.1%, expose the target role label or normalized variant.
Counterevidence: No-label prompt topology remains close to original prompt topology, so label exposure is not the whole semantic structure.
Dependencies: `research/assistant_axis_methodology/role_prompt_label_exposure_audit.md`
Last Updated: 2026-05-30

## 13. No-Label Prompt Semantic Topology Mostly Survives Label Removal

Claim: Removing explicit role labels preserves much of the prompt-space semantic topology.
Status: Supported
Evidence: No-label prompt ablation: median role-level SVD cosine 0.998, nearest-neighbor preservation 0.924, pairwise distance correlation 0.985.
Counterevidence: Hard cluster assignments are less stable; behavioral descriptors can still imply role identity.
Dependencies: `research/assistant_axis_methodology/no_label_prompt_ablation/`
Last Updated: 2026-05-30

## 14. PC1 Tracks Constraint, Standards, Expertise, and Procedural Competence

Claim: PC1 is best interpreted as careful/evaluative/procedural control, objective certainty, disciplined knowledge practice, and externally legible competence versus open/symbolic/expressive possibility.
Status: Supported
Evidence: Big Five conscientiousness alignment; reading-based rater PC1 r=0.558; professional objective-certainty PC1 r=0.394; assistant-axis alignment 0.802310.
Counterevidence: PC1 mixes several related constructs; intelligence/expertise can outpredict objective certainty in the rater study.
Dependencies: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`, `research/q2_stability/qwen/outputs/professional_hierarchy_validation/`
Last Updated: 2026-05-30

## 15. PC2 Is an Abstraction/Integration/Developmental Axis, Not Simple Uncertainty Capacity

Claim: PC2 is currently best described as abstraction/integration/developmental structure, with coherent action under uncertainty as a secondary expression rather than the primary label.
Status: Supported
Evidence: Conditional PC1-band validation found abstraction predicts residual PC2 at r=-0.618, coherent action weaker at r=+0.427, and uncertainty exposure fails at r=-0.026; professional coherent uncertainty capacity r=-0.007.
Counterevidence: PC2 remains least cleanly univariate; current labels remain interpretive and require independent-rater replication.
Dependencies: `research/q2_stability/qwen/outputs/pc2_conditional_validation/`, `research/q2_stability/qwen/outputs/professional_hierarchy_validation/`
Last Updated: 2026-05-30

## 16. PC3 Tracks Cooperative-Stabilizing Versus Antagonistic-Transgressive Stance

Claim: PC3 shows suggestive but incomplete support for a perturbation-stabilization interpretation; positive PC3 reflects intervention, challenge, disruption, exploitation, or stress-testing, while negative PC3 reflects care, repair, mediation, preservation, and stabilization. Cooperative-antagonistic remains a secondary or partial reading.
Status: Provisionally Supported
Evidence: Reading-based rater PC3 r=0.690 and matched-pair agreement 95%; full-distribution coordinate-blind perturbation-stabilization validation found Pearson r=0.529, Spearman r=0.511, cluster-controlled Pearson r=0.491, and within-cluster pairwise ordering accuracy 0.773; the target rubric outperformed moral_badness, professionalism, weirdness/fantasticality, and abstraction controls.
Counterevidence: Grounded_social within-cluster performance was weak (pairwise accuracy 0.565); professional subset has counterexamples such as economist, mathematician, statistician, and lawyer; deterministic rubric scoring is not independent human or second-model validation.
Dependencies: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`, `research/q2_stability/qwen/outputs/pc3_hypothesis_evaluation/`, `research/outputs/pc3_validation/`
Last Updated: 2026-05-30

## 17. Persona Space May Exhibit Cone-Like Geometric Constraints

Claim: Variance in PC2/PC3 appears to expand as PC1 decreases, suggesting a cone-like structure.
Status: Speculative
Evidence: Visualization and interpretation notes identify high-PC1 collapse and broader low-PC1 spread.
Counterevidence: Quantitative variance-by-PC1 tests and sampling-artifact controls are still needed.
Dependencies: `research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md`, `research/visualizations/persona_geometry_explorer.html`
Last Updated: 2026-05-30

## 18. Cone Boundaries Represent Genuine Geometric Limits

Claim: The cone boundaries reflect admissible geometric limits rather than sampling artifacts.
Status: Speculative
Evidence: The cone interpretation is coherent with high-PC1 constrained roles occupying a narrow region.
Counterevidence: No direct falsification test has yet separated true geometric constraints from role-inventory sampling, prompt-corpus design, or visualization artifacts.
Dependencies: future cone quantification tests
Last Updated: 2026-05-30

## 19. Adaptive Extraction Is Operationally Validated for Trickster

Claim: Adaptive extraction can produce a usable score-conditioned vector without exhaustively scoring all 1200 rollouts, at least for high-signal trickster.
Status: Observed
Evidence: Trickster adaptive scoring reached 64 score>=2 and 33 score==3 in 64 scored records; score>=2 vector cosine to Lu trickster mean was 0.957557; adaptive stopping passed at n=16.
Counterevidence: Editor did not reach validation thresholds; generality across quieter roles is unproven.
Dependencies: `research/q2_stability/qwen/outputs/paper1_5/`
Last Updated: 2026-05-30

## 20. Persona Drift Can Be Monitored Geometrically

Claim: Persona drift and role alignment can be monitored with activation geometry during multi-turn or extraction runs.
Status: Supported
Evidence: Dyad and extraction workflows track assistant-axis and role-cosine movement; V6 corrected pilot showed real post-T3 movement after use_cache=False fix.
Counterevidence: Earlier V1-V5 plateau artifact shows measurement can be invalid if cache handling is wrong; geometric monitoring requires strict measurement controls.
Dependencies: `research/RESEARCH_STATE.md`, dyad V6 outputs, workflow docs
Last Updated: 2026-05-30

## 21. Trait-Vector Geometry Predicts Persona PCA Location

Claim: Trait-vector geometry substantially predicts persona PCA location, supporting the interpretation that persona space is partly organized by trait structure rather than only role semantics.
Status: Observed
Evidence: Qwen/Qwen3-32B layer-48 persona-by-trait cosine matrix, 275 personas x 240 traits, predicted `geometry_viz_data.json` PCA coordinates with ridge 5-fold CV R2: PC1 0.999, PC2 0.999, PC3 1.000; 30-permutation baselines stayed near or below zero R2.
Counterevidence: The trait bank is high-dimensional and in the same activation space as the persona vectors, so near-ceiling prediction may reflect basis coverage/provenance coupling rather than independent psychological explanation.
Dependencies: `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_report.md`, `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json`
Last Updated: 2026-05-30

## 22. Direct Trait-Space PCA Partially Reorganizes Persona-Space Interpretations

Claim: Trait-space analysis partially recovers persona-space axes, supporting shared geometry while preserving unresolved differences between trait and persona manifolds.
Status: Tentative
Evidence: Direct PCA over 240 raw Qwen/Qwen3-32B layer-48 trait vectors explained 65.5% variance across the first three PCs; trait PC1 moderately aligned with persona PC1, abs cosine 0.681. Trait PC1 ranks controlled seriousness/formal composure vs playful irreverence/expressive volatility, a plausible trait-space analogue of persona PC1 constraint/possibility.
Counterevidence: Trait PC2 and PC3 weakly align with persona PC2/PC3, abs cosine 0.194 and 0.065. Trait PC2 is more cold detachment vs affiliative warmth than abstraction/integration; trait PC3 is more plain grounded practicality vs ornate symbolic/theatrical expressivity than perturbation/stabilization. Trait-space cone testing did not reproduce the simple persona-space cone pattern.
Dependencies: `research/outputs/trait_space_interpretation/trait_space_axis_report.md`, `research/outputs/trait_space_interpretation/trait_space_validation_stats.json`, `research/outputs/trait_space_interpretation/trait_space_cone_tests.json`
Last Updated: 2026-05-30

## 23. Released Trait Prompt Artifacts Enable Prompt-To-Geometry Forecasting

Claim: Released trait prompt artifacts are available and name-aligned with trait vectors, enabling construction of a prompt-to-geometry forecasting dataset without regenerating prompts.
Status: Observed
Evidence: Local `data/traits/instructions/*.json` contains 240 trait artifacts matching 240 Qwen/Qwen3-32B trait vector names exactly. The released `belmore/assistant-axis-vector-prompts` dataset, SHA `57424a9d6075a44196b935983ce1fa4e83191679`, contains 516 rows: 275 roles, 240 traits, and 1 default row. Exact trait-name match across local artifacts, Qwen trait vectors, and Belmore prompt rows is 240/240. Trait artifacts include descriptions, five positive instructions, five negative instructions, forty behavioral questions, and a 0-100 eval prompt.
Counterevidence: Forecasting readiness covers prompt artifacts and released vector targets, not generated response corpora. Strict leakage-controlled forecasting should exclude eval prompts and possibly target labels from model inputs.
Dependencies: `research/outputs/prompt_artifact_inventory/prompt_artifact_inventory_report.md`, `research/outputs/prompt_artifact_inventory/trait_vector_name_match_report.csv`, `research/outputs/prompt_artifact_inventory/forecasting_dataset_feasibility.md`
Last Updated: 2026-05-30

## 24. Prompt Text Forecasts Geometry On Held-Out Concepts

Claim: Prompt text alone contains sufficient information to forecast persona geometry on unseen concepts, establishing persona geometry as predictive over released prompt artifacts rather than purely descriptive of completed vectors.
Status: Supported
Evidence: On a strict holdout-by-trait split, leakage-control elastic-net TF-IDF using descriptions, instructions, and questions with explicit target names replaced predicted held-out trait PCs with mean R2=0.389: PC1 0.414, PC2 0.304, PC3 0.450. On held-out roles, the same model predicted persona PCs with mean R2=0.621: PC1 0.783, PC2 0.577, PC3 0.504. Nearest-neighbor semantic retrieval was much weaker on held-out leakage-control traits, mean R2=-0.021.
Counterevidence: This is a released prompt-artifact forecasting result, not a new activation-generation test. It uses TF-IDF over artifact text, so lexical/register regularities may contribute substantially. It does not prove execution-time steering or safety-control reliability.
Dependencies: `research/outputs/prompt_to_geometry_forecasting/forecasting_dataset_summary.md`, `research/outputs/prompt_to_geometry_forecasting/forecasting_results.json`, `research/outputs/prompt_to_geometry_forecasting/forecasting_model_comparison.csv`
Last Updated: 2026-05-30

## 25. PC1 Is A Convergence-Pressure / Degrees-Of-Freedom Axis

Claim: PC1 is currently interpreted as a convergence-pressure / degrees-of-freedom axis. Evaluator-like roles are evidence for this interpretation, not the interpretation itself. High PC1 constrains the role toward correct-answer or procedural convergence; low PC1 admits broader symbolic and expressive self-consistent continuations.
Status: Speculative
Evidence: PC1 endpoint rankings, assistant-axis alignment, professional hierarchy validation, prompt-to-geometry forecasting, and cone/void observations jointly support interpreting high-PC1 roles as geometrically constrained by correctness, validation, procedure, evidence, or error correction.
Counterevidence: PC1 remains entangled with assistantness, professional competence, conscientiousness, expertise, and prompt-register effects. The forcing-function interpretation has not yet been tested as an independent judge rubric.
Dependencies: `research/outputs/axis_forcing_function_notes/pc1_pc2_forcing_function_note.md`, `research/outputs/axis_forcing_function_notes/judge_rubric_design_notes.md`, `research/outputs/prompt_to_geometry_forecasting/forecasting_dataset_summary.md`
Last Updated: 2026-05-30

## 26. PC2 Is An Integrated-Abstraction / Situated-Immediacy Axis With Admissibility Constraints

Claim: PC2 is currently interpreted as an integrated-abstraction / situated-immediacy axis with an admissibility constraint. Some personas cannot coherently occupy deep integrated abstraction because their defining role lacks the prerequisites for reflective synthesis or accumulated world-model structure.
Status: Speculative
Evidence: Conditional PC2 validation revised the axis away from simple uncertainty tolerance and toward abstraction/integration/developmental structure; endpoint rankings and prompt-to-geometry forecasting make this interpretation operationally relevant for future rubrics.
Counterevidence: PC2 remains the least settled axis. The admissibility/forcing-function interpretation is currently a synthesis hypothesis and has not yet been validated by an independent prompt-level judge or improved held-out forecasting performance.
Dependencies: `research/outputs/axis_forcing_function_notes/pc1_pc2_forcing_function_note.md`, `research/outputs/axis_forcing_function_notes/axis_interpretation_method_sequence.md`, `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md`
Last Updated: 2026-05-30

## 27. Cluster Conditioning Improves Calibrated PC1/PC2 Prediction But Not Simple Within-Cluster Pairwise Judging

Claim: Cluster-conditioned scoring improves calibrated prediction of PC1 and PC2 as a modeling interaction, but simple within-cluster pairwise ordering is harder than global ordering because across-cluster offsets make many global comparisons easier.
Status: Supported
Evidence: Cluster-conditioned axis test over 275 roles found PC1 direct R2 0.296 vs oracle-cluster R2 0.811 and predicted-cluster R2 0.647; PC2 direct R2 0.416 vs oracle-cluster R2 0.718 and predicted-cluster R2 0.520. Pairwise accuracy moved opposite the simple hypothesis: PC1 global 0.709 vs within-cluster 0.622, PC2 global 0.746 vs within-cluster 0.687.
Counterevidence: Text-to-cluster classification is imperfect at 0.687 accuracy and 0.404 macro F1, and hard predicted-cluster errors erase much of the PC2 oracle benefit. The proxy scores are reused from prior Codex/GPT-5.5 blinded rater annotations rather than a new independent judge.
Dependencies: `research/outputs/cluster_conditioned_axis_tests/`
Last Updated: 2026-05-30
