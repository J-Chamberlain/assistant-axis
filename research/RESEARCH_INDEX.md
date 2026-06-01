# Research Index

This is the compact navigation index for the current assistant-axis research state. Use it with `research/RESEARCH_STATE.md` and `research/PROVENANCE_REGISTRY.md` before running broad repo searches.

## Current Paper Scopes

Paper 1 is complete: Gemma 2 27B persona geometry, careful-evaluator assistant-axis finding, seven-cluster taxonomy, and base-model basin evidence.

Paper 1.5 is active: **Interpreting Persona Activation Geometry**. The core contribution is layered interpretation of persona activation geometry after methodological stress testing, not adaptive extraction replication as the headline.

Paper 2 is active planning: local centroid perturbation and local persona-manifold mapping around anchors such as Trickster, Actor, Therapist, and Spy. Older dyad/contagion/attractor-collapse work is archived as future dynamics work.

## Current Best Findings

- Semantic topology partially predicts activation topology but does not explain it away.
- Explicit role-label exposure is part of the Lu-style prompt design and remains a methodological caveat.
- No-label prompt semantic topology remains close to original prompt topology, motivating activation-space no-label stress tests.
- Big Five-style LLM-assigned features are the strongest current global predictor of canonical Qwen activation PCA3D.
- Codex procedural/behavioral dimensions improve over semantic baseline but remain weaker than Big Five globally.
- A residualized hierarchical model modestly improves over Big Five, supporting a layered interpretation.
- TF-IDF/SVD15 prompt-register structure produces the strongest predictive result so far, but it is lexical/register-sensitive and not yet distilled into stable human-readable features.
- A first coordinate-blind no-label prompt rubric validation found only modest direct support for the PC interpretations, strongest for PC3 and weakest for PC2.
- A reading-based Codex/GPT-5.5 rater study over anonymized no-label prompt dossiers materially strengthened PC3 and PC1 interpretations, while showing that PC2 is better treated as a compound abstraction/integration axis than as coherent action under uncertainty alone.
- A targeted professional-hierarchy validation supports PC1 modestly and PC3 modestly inside professional roles, but does not support PC2 as a simple coherent-action-under-uncertainty hierarchy.
- A full-distribution PC3 perturbation-stabilization validation supports PC3 as mixed but positive: global Pearson r=0.529, cluster-controlled Pearson r=0.491, and within-cluster pairwise ordering accuracy 0.773.
- A conditional PC2 validation after PC1 decile control shifts the current PC2 interpretation toward abstraction/integration/developmental structure: abstraction predicts residual PC2 at r=-0.618, coherent action remains weaker at r=+0.427, and uncertainty exposure fails at r=-0.026.
- Cluster-conditioned PC1/PC2 testing found that within-cluster pairwise ordering is harder than global ordering, but cluster identity substantially improves calibrated regression: PC1 direct R2 0.296 vs oracle-cluster 0.811, PC2 direct R2 0.416 vs oracle-cluster 0.718.
- Training-artifact forecast error geometry shows the frozen role forecaster has tiny in-sample target-to-forecast error and near-zero signed PC2 bias, so the H100 PC2 upward shift is not native to the original role-artifact forecast task.
- Public-source extraction-equivalence audit changes D01 from merely unresolved to likely mismatch: projection, pooling, model identity, and prior hook-based trickster replication are verified, but official/prior layer-48 hook extraction likely maps to `hidden_states[49]`, not the H100 runner's `hidden_states[48]`.
- Role-rollout artifact audit resolves the public-data boundary for original role vectors: the intended 1,200 inputs per role are reconstructable, but original generated responses, judge scores, and retained-response masks are not public; the remembered "64" count is Qwen layer count/local adaptive-count provenance, not a public retained-rollout count.
- H100 anomaly interpretation is now governed by four methodological tracks: extraction equivalence, forecaster improvement, prompt-battery construction, and response-state uncertainty. D01-D09 remain useful, but several should not be closed as final behavioral evidence while their T-track remains open.
- Within-role displacement scaffolding is prepared for a user-selected target-role study: 275 roles have five positive instructions, 240 extraction questions are inventoried, displacement scoring templates exist, and role-candidate geometry centrality flags are available.
- Playwright within-role displacement scoring is prepared: 240 shared questions, five role-specific positive instructions, and 1,200 instruction-question combinations have rubric-based predicted PC1/PC2/PC3 displacement scores ready for manual review before corrected-hook GPU measurement.
- Clean Paper 1.5 core repo copy plan is prepared for user review: it proposes a 10.01 MB canonical first-pass artifact set for a reproducible report/notebook walkthrough and explicitly excludes H100 validation, prompt batteries, extraction-boundary diagnostics, large generated responses, RunPod logs, and activation shards.
- Trickster adaptive extraction succeeded operationally; editor adaptive extraction failed to reach validation thresholds.

## Best Predictive Metrics

All metrics below refer to held-out prediction of canonical Qwen activation PCA3D over the 273 common-persona shared benchmark unless noted.

| Feature family | Status | Mean R2 | Notes |
|---|---:|---:|---|
| Semantic baseline | established | 0.389 | Baseline reference for feature comparisons. |
| Codex trait replication | provisional/weak | 0.398 | Weak positive trait signal, not a Big Five replication. |
| Codex retained procedural/behavioral features | established | 0.490 | Useful improvement over semantics; weaker than Big Five. |
| Claude Big Five-style features | established | 0.613 | Strongest compact global predictor. |
| Hierarchical trait + procedural residual model | provisional | 0.622 | Small +0.009 over Big Five trait stage. |
| Residual manifold hand-feature layer | provisional | 0.632 | Small diagnostic improvement over hierarchy. |
| Sem + Big Five + SVD15 prompt-register basis | provisional/strong | 0.707 | Strongest predictive result, but lexical/register-sensitive. |

## Important Artifacts

- `research/THREAD_START.md`: three-minute continuity brief for new GPT/Claude/Codex threads.
- `research/CLAIMS_REGISTER.md`: compact top-claim register separating observed findings, supported interpretations, tentative claims, and speculative hypotheses.
- `research/PROVENANCE_REGISTRY.md`: artifact lineage and dependency registry.
- `research/FINDINGS_LEDGER.md`: compact status of findings, negative results, deviations, blockers, and next tests.
- `research/assistant_axis_methodology/`: Lu et al. methodology extraction, prompt audits, semantic topology, cluster overlap, no-label ablation.
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`: current shared feature benchmark and Big Five source data.
- `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/`: trait/procedural hierarchy.
- `research/q2_stability/qwen/outputs/residual_manifold_analysis/`: residual-manifold diagnostic.
- `research/q2_stability/qwen/outputs/residual_svd_interpretation/`: SVD15 reconstruction and interpretation.
- `research/q2_stability/qwen/outputs/blinded_axis_rubric_validation/`: coordinate-blind no-label prompt rubric validation of PC1, PC2, and PC3 working interpretations.
- `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`: reading-based Codex-as-rater blinded annotation study over anonymized no-label persona dossiers.
- `research/q2_stability/qwen/outputs/professional_hierarchy_validation/`: targeted professional-role validation for PC1, PC2, and PC3 interpretations.
- `research/outputs/pc3_validation/`: full-distribution perturbation-stabilization validation for PC3 with negative controls, cluster-control regression, pairwise ordering, leave-one-cluster-out checks, and diagnostic examples.
- `research/outputs/cluster_conditioned_axis_tests/`: PC1/PC2 cluster-conditioning test with pairwise global/within/across comparisons, cluster classifier accuracy, and direct/oracle/predicted-cluster regression regimes.
- `research/q2_stability/qwen/outputs/pc2_conditional_validation/`: conditional PC2 validation after PC1 band control, including candidate comparison, matched pairs, physicist test, and mythic/developmental test.
- `research/outputs/novel_prompt_battery_percentile_edges/`: current H100-ready percentile-edge prompt battery and recommended H100 manifest.
- `research/outputs/pre_h100_methods_memorial/`: durable pre-H100 methods, assumptions, artifact index, and readiness summary.
- `research/outputs/h100_percentile_edge_validation/`: completed 100-prompt activation validation with forecast-vs-observed metrics and generated responses.
- `research/outputs/h100_percentile_edge_validation_error_analysis/`: regional error analysis and interactive forecast-to-observed 3D/2D arrow visualizations.
- `research/outputs/h100_diagnostic_followups/`: persistent anomaly checklist D01-D09 and first diagnostic pass for extraction methodology, cone outliers, PC2 drift, PC3-high collapse, prompt-generation bias, and calibration.
- `research/outputs/h100_diagnostic_followups/methodological_dependency_tracks.md`: governing T01-T04 dependency map for H100 anomaly interpretation and D01-D09 closure order.
- `research/outputs/training_forecast_error_geometry/`: native frozen-forecaster target-to-forecast error geometry over original role artifacts, with interactive 3D/2D arrows and H100 comparison.
- `research/outputs/extraction_equivalence_audit/`: source/artifact audit comparing original/local Assistant Axis extraction code, prior trickster/editor adaptive extraction, and the H100 percentile-edge extraction runner.
- `research/outputs/public_source_extraction_equivalence/`: public-source audit of official Assistant Axis code, Hugging Face dataset/model metadata, Transformers Qwen3 hidden-state semantics, and D01 hook-vs-hidden-states mismatch evidence.
- `research/outputs/role_rollout_artifact_audit/`: public/local audit of reconstructable role-vector rollout inputs, missing public responses/scores/retained masks, and the resolved "64" count question.
- `research/outputs/within_role_displacement_design/`: reusable design packet for testing whether instruction/question wording predicts activation displacement around a fixed user-selected role centroid.
- `research/outputs/playwright_displacement_scoring/`: scored playwright within-role displacement packet with question scores, instruction scores, 1,200-row forecast grid, distribution summary, manual-review shortlist, report, and reproducible no-GPU scoring script.
- `research/outputs/paper15_clean_repo_copy_plan/`: copy plan for a future clean `assistant-axis-paper15-core` repo, including artifact CSV, report spine map, claim traceability table, visualization inventory, proposed tree, and excluded archive index.
- `research/visualizations/persona_geometry_explorer.html`: interactive Plotly viewer with PCA/UMAP, cluster, selection, and Big Five overlays.
- `research/visualizations/bigfive_geometry_overlay_data.json`: persona-aligned Big Five overlay data.

## Open Questions

- Does activation geometry survive no-label prompts under matched extraction conditions?
- How sensitive are role-expression scores to evaluator model choice, especially for assistant-adjacent roles?
- Can SVD15 lexical/register signal be distilled into stable, interpretable residual features?
- Do independent blinded human or second-model raters using full rollout responses replicate the Codex-as-rater prompt-dossier validation?
- Are developmental, liminal, collective, and nonindividual roles genuinely high-residual regions or artifacts of the prompt corpus?
- Do local perturbation directions transfer across persona anchors, or is persona space strongly curved?
- Can assistant-adjacent roles such as editor be anchored without collapsing toward generic assistant behavior?

## Pending Experiments

1. Independent-rater replication using human or second-model raters over the strongest PC1-matched PC2 pairs, forcing abstraction, maturity/integration, and coherent-action choices.
2. Evaluator-sensitivity comparison between Codex/GPT-5.5 Standard and `gpt-4.1-mini`.
3. Bounded no-label activation-space stress test on selected anchors, bridge roles, assistant-adjacent roles, and theatrical/fantastical roles.
4. SVD15 distillation into concrete text-grounded residual features and retest under the shared splits.
5. Stage-1 role-inventory uncertainty analysis across OpenAI and Claude-generated inventories, synchronized through GitHub.
6. Paper 2 local centroid perturbation around Trickster, Actor, Therapist, and Spy.
7. Close T01 by resolving D01 in `research/outputs/h100_diagnostic_followups/diagnostic_followup_checklist.md` with the minimal Qwen/Qwen3-32B hook-vs-`output_hidden_states` confirmation test; public sources now indicate the hook on `model.model.layers[48]` should match `hidden_states[49]`, not H100 `hidden_states[48]`.
8. Advance T02 by building an instance-level prompt-to-centroid forecasting dataset from reconstructed role instruction-question inputs; successful-rollout-aware training requires regenerated responses/judge scores or private original artifacts.
9. Advance T03 by rebuilding or recalibrating the prompt battery against inherited 20/80 tails, 35/65 shoulders, and interior controls after T02 or an explicit decision to keep the current forecaster.
10. Advance T04 by designing a small multi-sample GPU study to estimate response activation spread around selected target regions after T01 is closed.
11. Calibrate the lightweight prompt-to-geometry forecaster using the completed H100/A100 validation data only after the T01 activation-boundary issue is resolved: start with per-axis intercept/slope correction, then compare against region-aware correction for PC2 and PC3 tails.
12. Review `research/outputs/playwright_displacement_scoring/displacement_manual_review_shortlist.csv`, especially thin PC1-negative and PC3-positive coverage, before running the corrected-hook playwright displacement study after T01/D01 extraction equivalence is resolved.
13. Review `research/outputs/paper15_clean_repo_copy_plan/clean_repo_copy_plan.csv`; if approved, run a separate copy-only task to create `assistant-axis-paper15-core` without H100 or prompt-battery materials.

## Archived Directions

- Dyad contagion, attractor-collapse, conversational drift, and rumination dynamics are archived as future dynamics work, not the current Paper 2 scope.
- Full 1200-rollout adaptive extraction replication is no longer the main Paper 1.5 frame.
- Blindly extending editor rollouts is not recommended without revised anchoring methodology.

## Key Visualizations

- `research/visualizations/persona_geometry_explorer.html`: current interactive geometry viewer.
- `research/visualizations/geometry_viz_data.json`: embedded geometry source.
- `research/visualizations/bigfive_geometry_overlay_data.json`: Big Five overlay source.
- `visualizations/research_paper.html`: Paper 1 public visualization page.

## Current PC Interpretations

PC1: Primarily separates careful/evaluative/procedural control from open, expressive, unstable, symbolic, or emotionally pressured persona organization. It overlaps with the assistant/evaluator basin but should not be reduced to literal assistantness. Conscientiousness is strongly positive; openness, extraversion, and neuroticism are strongly negative. The reading-based blinded rater study strengthens PC1 as objective certainty, but intelligence/expertise is an even stronger PC1 correlate, so paper language should include disciplined knowledge practice and externally legible competence.

PC2: Least cleanly univariate, but now best described as an abstraction/integration/developmental axis rather than a coherent-action-under-uncertainty axis. Conditional PC1-band validation found abstraction is the strongest residual predictor (r=-0.618, R2=0.382), while coherent action remains weaker but nonzero (r=+0.427, R2=0.182) and uncertainty exposure fails (r=-0.026). Lower PC2 is more abstract, world-model-like, integrated, and long-residence; higher PC2 is more developmental, reactive, socially volatile, or less integrated. Coherent action under unresolved uncertainty should be retained as a secondary behavioral expression, not the primary label.

PC3: Shows suggestive but incomplete support for perturbation-stabilization. Positive PC3 emphasizes intervention, challenge, disruption, exploitation, testing, or adversarial pressure; negative PC3 emphasizes care, repair, mediation, preservation, and stabilization. Cooperative-antagonistic remains a secondary or partial reading because many perturbative roles are socially antagonistic, but prosocial interventionist examples show the axis is not reducible to hostility or moral badness.

## Current Interpretation

The strongest current Paper 1.5 framing is layered: semantic topology supplies a structured prior, Big Five-style dispositional features explain broad global placement, procedural/operating-mode features explain some local residual structure, lexical/register features explain additional prompt-corpus-sensitive residual variance, and developmental/liminal/collective roles remain hard cases. This is an interpretation of representational geometry, not a claim of true psychological ontology.

Cluster-conditioned axis tests now clarify judge-design implications: cluster identity helps calibrated numeric prediction as an interaction term, but it does not make within-cluster pairwise axis ordering easier. Direct PC1 judging remains useful for simple interpretation; PC2 should use cluster-conditioned analysis for mechanism and soft-cluster/hybrid features for deployment-style forecasting.
