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

- `research/PROVENANCE_REGISTRY.md`: artifact lineage and dependency registry.
- `research/FINDINGS_LEDGER.md`: compact status of findings, negative results, deviations, blockers, and next tests.
- `research/assistant_axis_methodology/`: Lu et al. methodology extraction, prompt audits, semantic topology, cluster overlap, no-label ablation.
- `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`: current shared feature benchmark and Big Five source data.
- `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/`: trait/procedural hierarchy.
- `research/q2_stability/qwen/outputs/residual_manifold_analysis/`: residual-manifold diagnostic.
- `research/q2_stability/qwen/outputs/residual_svd_interpretation/`: SVD15 reconstruction and interpretation.
- `research/visualizations/persona_geometry_explorer.html`: interactive Plotly viewer with PCA/UMAP, cluster, selection, and Big Five overlays.
- `research/visualizations/bigfive_geometry_overlay_data.json`: persona-aligned Big Five overlay data.

## Open Questions

- Does activation geometry survive no-label prompts under matched extraction conditions?
- How sensitive are role-expression scores to evaluator model choice, especially for assistant-adjacent roles?
- Can SVD15 lexical/register signal be distilled into stable, interpretable residual features?
- Are developmental, liminal, collective, and nonindividual roles genuinely high-residual regions or artifacts of the prompt corpus?
- Do local perturbation directions transfer across persona anchors, or is persona space strongly curved?
- Can assistant-adjacent roles such as editor be anchored without collapsing toward generic assistant behavior?

## Pending Experiments

1. Evaluator-sensitivity comparison between Codex/GPT-5.5 Standard and `gpt-4.1-mini`.
2. Bounded no-label activation-space stress test on selected anchors, bridge roles, assistant-adjacent roles, and theatrical/fantastical roles.
3. SVD15 distillation into concrete text-grounded residual features and retest under the shared splits.
4. Stage-1 role-inventory uncertainty analysis across OpenAI and Claude-generated inventories, synchronized through GitHub.
5. Paper 2 local centroid perturbation around Trickster, Actor, Therapist, and Spy.

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

PC1: Primarily separates careful/evaluative/procedural control from open, expressive, unstable, symbolic, or emotionally pressured persona organization. It overlaps with the assistant/evaluator basin but should not be reduced to literal assistantness. Conscientiousness is strongly positive; openness, extraversion, and neuroticism are strongly negative.

PC2: Less cleanly univariate. It appears to contain compound social-expression, grounded-interpersonal, and model-specific structure. Big Five improves PC2 prediction, but no single Big Five trait gives a clean interpretation.

PC3: Partly tracks cooperative-care versus antagonistic/disruptive stance. Agreeableness is the strongest Big Five correlate, but the axis should still be checked against plotted coordinates and residual cases before becoming strong paper language.

## Current Interpretation

The strongest current Paper 1.5 framing is layered: semantic topology supplies a structured prior, Big Five-style dispositional features explain broad global placement, procedural/operating-mode features explain some local residual structure, lexical/register features explain additional prompt-corpus-sensitive residual variance, and developmental/liminal/collective roles remain hard cases. This is an interpretation of representational geometry, not a claim of true psychological ontology.
