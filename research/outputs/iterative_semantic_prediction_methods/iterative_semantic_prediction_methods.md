# Methods: Iterative Semantic Prediction of Persona Activation Geometry

`model_used`: GPT-5.5 for archival/report generation. No model APIs, GPU work, response generation, activation extraction, projection reruns, or new benchmark fitting were performed for this archive.

## Purpose

This note memorializes the iterative semantic-prediction benchmark sequence used in Paper 1.5 planning. It is derived from the canonical summary in `research/RESEARCH_INDEX.md` and the artifact lineage in `research/PROVENANCE_REGISTRY.md`.

## Benchmark Definition

To test whether persona activation geometry could be predicted from interpretable semantic features, the project constructed a sequence of held-out prediction benchmarks over canonical Qwen activation PCA coordinates. The target variable was the three-dimensional activation geometry of the common persona set, represented by PC1, PC2, and PC3 coordinates in the reconstructed Qwen persona space.

The benchmark used 273 common personas and five deterministic train/test split assignments. Performance was evaluated using held-out mean R2 across the activation PCA dimensions. For readability, the table below also reports approximate R as the positive square root of R2.

## Iterative Results

| Feature family | Status | Mean R2 | Approx R | Interpretation |
|---|---|---:|---:|---|
| Semantic baseline | established | 0.389 | 0.624 | Baseline reference; semantic topology partially predicts activation topology but does not fully explain it. |
| Codex trait replication | provisional/weak | 0.398 | 0.631 | Weak positive trait signal; not a successful replication of stronger Big Five-style results. |
| Codex retained procedural/behavioral features | established | 0.490 | 0.700 | Procedural and behavioral features improve substantially over semantic baseline. |
| Claude Big Five-style features | established | 0.613 | 0.783 | Strongest compact global predictor; useful but not independent psychometric evidence. |
| Hierarchical trait-plus-procedural model | provisional | 0.622 | 0.789 | Small residual improvement over Big Five-style stage, supporting layered structure. |
| Residual-manifold hand-feature layer | provisional/diagnostic | 0.632 | 0.795 | Small diagnostic improvement over hierarchy; useful for residual regions, not a solved third-layer model. |
| Semantic + Big Five + SVD15 prompt-register basis | provisional/strong | 0.707 | 0.841 | Strongest predictive result; lexical/register-sensitive and not yet distilled into stable human-readable features. |

## Interpretation

The semantic baseline established that ordinary lexical or semantic topology partially predicts activation topology, but does not fully explain it. The constrained Codex trait replication improved only slightly over that baseline and should be treated as weak positive trait signal rather than a successful replication of the stronger Big Five-style feature result.

Codex-retained procedural and behavioral features produced a larger improvement over semantic baseline, supporting the view that activation geometry contains interpretable operating-mode structure beyond ordinary semantic similarity. Claude Big Five-style features were the strongest compact global predictor, but they remain structured descriptors for prediction rather than independent psychometric measurements.

The hierarchical trait-plus-procedural model and residual-manifold hand-feature layer produced modest incremental gains. These are best framed as evidence for layered residual structure, not as a solved ontology. The strongest observed predictive result came from adding a 15-dimensional SVD prompt/register basis to semantic and Big Five-style predictors. Because this basis is lexical and register-sensitive, it should be interpreted as evidence that residual activation geometry remains partly predictable from prompt/register structure, pending distillation into stable human-readable features.

## Bottom Line

Across iterations, held-out mean R2 increased from 0.389 for the semantic baseline to 0.707 for the semantic + Big Five + SVD15 prompt-register model. This supports a layered interpretation of persona activation geometry: semantic similarity explains a meaningful baseline portion; compact trait-style descriptors explain substantially more; procedural and residual features add smaller increments; and lexical/register-sensitive SVD features currently give the strongest prediction while requiring caution.

## Caveats

- These are held-out prediction results over the canonical shared benchmark, not execution-time activation validation.
- Big Five-style and SVD/register features are useful predictors but should not be treated as causal psychological ontology.
- The SVD15 result may capture prompt-corpus or register structure; it needs distillation and retesting before being elevated to a stable interpretation.
- R values are reported only as approximate square roots of R2 for interpretive convenience.
