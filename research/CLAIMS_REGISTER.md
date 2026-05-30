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
