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
- A muted-PC1 PC2 extremes inspection selected the central 45th-55th percentile PC1 band (n=27) and found high PC2 concentrated in situated/social/reactive roles while low PC2 concentrated in abstract/integrative/systemic/procedural roles, refining PC2 independently of the broad PC1 axis.
- A cluster-conditioned PC2 extremes diagnostic gives partial support to PC2 as situated-immediacy/formative-state versus integrated-stability: expected-direction checks pass 7/8 globally and 5/8 by cluster median, while `shapeshifter`, `chameleon`, and `elder` remain important caveats.
- A contained cross-model diagnostic finds Qwen-Llama PC2 partly transferable in a shared PC1/PC2 plane, not as a clean same-index axis: PC1/PC2 plane principal correlations are 0.977/0.905, same-index PC2 Pearson r=0.606, and same-index PC3 Pearson r=0.440.
- A cross-model cluster-topology diagnostic finds partial preservation of broad regions rather than universal hard clusters: Qwen-Llama top3 k-means ARI/NMI 0.364/0.458, top5 sensitivity 0.537/0.548, and Qwen-Gemma top3 0.637/0.656.
- Cluster-conditioned PC1/PC2 testing found that within-cluster pairwise ordering is harder than global ordering, but cluster identity substantially improves calibrated regression: PC1 direct R2 0.296 vs oracle-cluster 0.811, PC2 direct R2 0.416 vs oracle-cluster 0.718.
- Training-artifact forecast error geometry shows the frozen role forecaster has tiny in-sample target-to-forecast error and near-zero signed PC2 bias, so the H100 PC2 upward shift is not native to the original role-artifact forecast task.
- Public-source extraction-equivalence audit changes D01 from merely unresolved to likely mismatch: projection, pooling, model identity, and prior hook-based trickster replication are verified, but official/prior layer-48 hook extraction likely maps to `hidden_states[49]`, not the H100 runner's `hidden_states[48]`.
- The staged A100 hook-boundary test resolves D01 for the direct-hook workflow: `model.model.layers[48]` matches `outputs.hidden_states[49]` with mean cosine 1.000000 and zero projected-coordinate delta; the same pilot produced 60 amateur and 60 playwright response activations for response-cloud analysis.
- Posthoc analysis of the amateur/playwright activation clouds finds both unfiltered clouds are anisotropic and mostly PC1-elongated with substantial PC1-PC2 plane loading; bootstrap suggests at least 20 retained amateur and 30 retained playwright responses for stable centroids under current criteria.
- GPT-4.1 judge filtering is now complete for the amateur/playwright activation clouds: most responses were retained at score>=2, filtering reduced cloud volume and mean response distance, but filtered centroids moved farther from published role vectors, implying strong role-expression subclouds are tighter but offset.
- A standalone activation-cloud viewer and reusable no-GPU suite now exist for future persona-cloud tests; GPT-5.5 comparison was not run because the model rejected the required temperature-0 judge configuration.
- GPT-5.5 default-temperature judge comparison is complete and should be treated as model-comparison rather than deterministic replication: exact score agreement with GPT-4.1 was 0.600, retain>=2 agreement 0.875, and retain==3 agreement 0.733.
- Role-rollout artifact audit resolves the public-data boundary for original role vectors: the intended 1,200 inputs per role are reconstructable, but original generated responses, judge scores, and retained-response masks are not public; the remembered "64" count is Qwen layer count/local adaptive-count provenance, not a public retained-rollout count.
- H100 anomaly interpretation is now governed by four methodological tracks: extraction equivalence, forecaster improvement, prompt-battery construction, and response-state uncertainty. D01-D09 remain useful, but several should not be closed as final behavioral evidence while their T-track remains open.
- Within-role displacement scaffolding is prepared for a user-selected target-role study: 275 roles have five positive instructions, 240 extraction questions are inventoried, displacement scoring templates exist, and role-candidate geometry centrality flags are available.
- Playwright within-role displacement scoring is prepared: 240 shared questions, five role-specific positive instructions, and 1,200 instruction-question combinations have rubric-based predicted PC1/PC2/PC3 displacement scores ready for manual review before corrected-hook GPU measurement.
- Clean Paper 1.5 core repo copy plan is prepared for user review: it proposes a 10.01 MB canonical first-pass artifact set for a reproducible report/notebook walkthrough and explicitly excludes H100 validation, prompt batteries, extraction-boundary diagnostics, large generated responses, RunPod logs, and activation shards.
- Paper 1.5 core notebook skeleton is prepared, revised for shareability, and headlessly executed as a local-runnable pre-H100 executable appendix: it loads canonical public geometry, artifact provenance, PC axis interpretation outputs, cross-model caveats, trait/persona outputs, and forecasting baselines while excluding H100 validation, prompt batteries, extraction-boundary diagnostics, RunPod logs, and visualization edits.
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
- `research/outputs/pc2_muted_pc1_extremes/`: PC2 top/bottom role inspection within the central 45th-55th percentile PC1 band, including ranked tables, band statistics, plots, and interpretation note.
- `research/outputs/pc2_cluster_conditioned_extremes/`: global, per-cluster, and muted-PC1-within-cluster PC2 rankings with diagnostic-role checks for the stability/impressionability interpretation.
- `research/outputs/cross_model_pc2_pc3_diagnostic/`: contained Qwen/Llama/Gemma released-vector comparison for PC2/PC3 comparability, diagnostic-role ranks, expected-direction checks, and visualization feasibility.
- `research/outputs/cross_model_cluster_topology/`: bounded Qwen/Llama/Gemma cluster-topology comparison with ARI/NMI, overlap matrices, Qwen-reference mappings, region conservation checks, and visualization feasibility update.
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
- `research/outputs/positive_pc2_pilot_candidate_selection/`: positive-PC2 edge candidate shortlist for the first two-persona activation-cloud GPU pilot with playwright, including primary/alternate candidate tables, instruction excerpts, and playwright comparison coordinates.
- `research/outputs/a100_two_role_activation_cloud_pilot/`: staged A100 boundary verification and two-role response activation-cloud pilot for amateur and playwright, including raw responses, per-response coordinates, cloud summaries, covariance, plots, judge-input JSONL, runtime/cost report, and pod closeout artifacts.
- `research/outputs/a100_activation_cloud_posthoc_analysis/`: local posthoc analysis of the amateur/playwright pilot, including covariance/eigendecomposition, PC correlation matrices, outlier table, cloud plots, bootstrap sample-size convergence, GPT-4.1 judge prompt/schema/cost estimate, and sanitized API-quota failure record.
- `research/outputs/a100_activation_cloud_visualization_and_judge_compare/`: standalone activation-cloud viewer, viewer data bundle, static summary plot, projection-specific HTML files, GPT-5.5 availability/skipped report, and judge-comparison placeholders.
- `research/outputs/gpt55_judge_and_outlier_followup/`: GPT-5.5 default-temperature judge scores, GPT-4.1/GPT-5.5 agreement tables, score==3 outlier tables, instruction/question effects, and future activation-cloud protocol recommendation.
- `research/outputs/prior_adaptive_recovery_audit/`: local no-GPU audit of prior trickster/editor adaptive extraction artifacts under corrected D01, including recoverability classification, locally reprojected hook-vector PCA coordinates, cloud summaries, and GPT-4.1 rejudge-ready inputs.
- `research/tools/activation_cloud_suite/`: reusable no-GPU activation-cloud analysis scaffold with config template, judge rubric, README, and runner stub for future persona-cloud pilots.
- `research/outputs/paper15_clean_repo_copy_plan/`: copy plan for a future clean `assistant-axis-paper15-core` repo, including artifact CSV, report spine map, claim traceability table, visualization inventory, proposed tree, and excluded archive index.
- `research/notebooks/paper15_core_analysis_walkthrough.ipynb`: first-pass Paper 1.5 executable appendix / notebook walkthrough for canonical pre-H100 analysis.
- `research/notebooks/paper15_core_analysis_walkthrough.executed.ipynb`: headlessly executed Paper 1.5 core notebook.
- `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough_report_collapsed_code.html`: reader-first shareable report export with code collapsed by default and computed outputs visible.
- `research/outputs/paper15_notebook_core/`: notebook builder, dependency table, claim traceability table, build/revision reports, Jupyter execution status, environment freeze/summary, generated figures, standard/collapsed HTML exports, and artifact manifest for the Paper 1.5 core notebook.
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
2. Run blinded no-label matched-pair ratings inside the muted-PC1 and within-cluster PC2-extremes bands to test whether situated-immediacy/formative-state versus integrated-stability is recoverable without coordinates.
3. If cross-model visualization work proceeds, start with model switching or cluster-overlap/alluvial views; avoid uncaveated PC3 arrows until alignment correction exists.
4. Evaluator-sensitivity comparison between Codex/GPT-5.5 Standard and `gpt-4.1-mini`.
5. Bounded no-label activation-space stress test on selected anchors, bridge roles, assistant-adjacent roles, and theatrical/fantastical roles.
6. SVD15 distillation into concrete text-grounded residual features and retest under the shared splits.
7. Stage-1 role-inventory uncertainty analysis across OpenAI and Claude-generated inventories, synchronized through GitHub.
8. Paper 2 local centroid perturbation around Trickster, Actor, Therapist, and Spy.
9. Use the A100 boundary result to update D01/T01 language: direct layer-48 hook extraction matches `hidden_states[49]`, not `hidden_states[48]`; future response-state work should use direct hook extraction or the verified hidden-state boundary.
10. Advance T02 by building an instance-level prompt-to-centroid forecasting dataset from reconstructed role instruction-question inputs; successful-rollout-aware training requires regenerated responses/judge scores or private original artifacts.
11. Advance T03 by rebuilding or recalibrating the prompt battery against inherited 20/80 tails, 35/65 shoulders, and interior controls after T02 or an explicit decision to keep the current forecaster.
12. Inspect score==3 outliers, rejected near-centroid responses, and instruction/question effects in `research/outputs/a100_activation_cloud_posthoc_analysis/` before launching more GPU roles.
13. Inspect `research/outputs/gpt55_judge_and_outlier_followup/score3_outliers.csv`, `instruction_effects.csv`, and `question_effects.csv` before launching more GPU roles; if comparing judges in write-up, explicitly mark GPT-4.1 temperature-0 versus GPT-5.5 default-temperature as a decoding mismatch.
14. If evaluator sensitivity for prior adaptive extraction is needed, run GPT-4.1 rejudging on `research/outputs/prior_adaptive_recovery_audit/prior_adaptive_gpt41_judge_inputs.jsonl`; do not rerun GPU solely to recover hook-based trickster/editor vectors.
15. Calibrate the lightweight prompt-to-geometry forecaster using the completed H100/A100 validation data only after the T01 activation-boundary issue is resolved: start with per-axis intercept/slope correction, then compare against region-aware correction for PC2 and PC3 tails.
16. Review `research/outputs/playwright_displacement_scoring/displacement_manual_review_shortlist.csv`, especially thin PC1-negative and PC3-positive coverage, before running the corrected-hook playwright displacement study after T01/D01 extraction equivalence is resolved.
17. Select one positive-PC2 edge role from `research/outputs/positive_pc2_pilot_candidate_selection/` for the first two-persona activation-cloud GPU pilot with playwright after extraction-boundary verification.
18. Review `research/outputs/paper15_clean_repo_copy_plan/clean_repo_copy_plan.csv`; if approved, run a separate copy-only task to create `assistant-axis-paper15-core` without H100 or prompt-battery materials.
19. Review `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough_report_collapsed_code.html` as the reader-first Paper 1.5 work-in-progress report; if approved, include the source/executed notebook and collapsed-code HTML in the future clean Paper 1.5 core repo.

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
