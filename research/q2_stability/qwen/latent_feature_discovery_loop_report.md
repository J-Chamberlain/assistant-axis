# Latent Feature Discovery Loop Report

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Script author model: GPT-5.5 Standard
Target corpus: 275 Lu et al. persona roles
Split: 200 visible personas for feature discovery, 75 held-out personas for evaluation

## 1. Motivation

The semantic-vs-activation analyses show that role semantics partially constrain activation geometry but do not determine it. Original and no-label prompt spaces remain close to each other, while activation cluster agreement remains modest. This creates a methodological problem: if semantic topology is not enough, the project needs a constrained way to generate additional explanatory dimensions without turning interpretation into freeform storytelling.

The loop implemented here treats a frontier model as a hypothesis generator. It can inspect selected persona descriptions, no-label prompts, semantic cluster assignments, activation cluster assignments, bridge roles, anchor roles, and displacement metrics. It cannot be treated as evidence. Evidence comes only from held-out predictive improvement over semantic baselines, residual reduction, nearest-neighbor preservation, and stability across iterations.

## 2. Why Semantic Geometry Alone Is Insufficient

Prior semantic analyses found that prompt-space topology survives label removal strongly: original-vs-no-label distance correlation is 0.956, and nearest-neighbor preservation is 0.858. However, hard-cluster recovery of activation labels is weak: role-name k=7 ARI is 0.010, role-name-plus-description ARI is 0.023, original-prompt ARI is 0.111, and no-label-prompt ARI is 0.130.

The overlap analysis adds the same conclusion from another angle. It finds 73 stable anchor roles but 198 broad bridge or migratory roles. Editorial is the cleanest semantic-activation overlap region, while procedural-professional compresses several semantic regions into a broad activation basin. Collective and swarm roles are semantically compact but distributed across larger activation clusters in the available labels.

This motivates a model-assisted search for latent explanatory features that may capture enacted behavioral organization better than semantic cluster labels alone.

## 3. Loop Design

The implemented loop lives at `research/q2_stability/qwen/scripts/latent_feature_discovery_loop.py`. It uses only existing local artifacts and runs on CPU.

The loop has four stages:

1. Build a persona table from role names, original role prompts, no-label prompts, semantic cluster assignments, activation cluster labels, bridge metrics, anchor flags, and displacement metrics.
2. Split personas deterministically into 200 visible personas and 75 held-out personas.
3. Add latent dimensions across three iterations, operationalizing each dimension as a measurable feature using lexical and prompt-pattern indicators.
4. Evaluate whether semantic baseline plus latent features improves held-out prediction over semantic baseline alone.

The current implementation does not call an external model at runtime. Instead, it encodes the first GPT-5.5-derived candidate dimension set as auditable structured hypotheses, then tests them quantitatively. This is intentionally conservative: the model proposes dimensions, but the script converts them into measurable features and evaluates them on hidden cases.

## 4. Held-Out Evaluation Framework

The semantic baseline uses one-hot original-prompt k=7 cluster, no-label-prompt k=7 cluster, and role-name k=7 cluster features. The latent model adds proposed dimension scores.

The held-out targets are:

1. Activation cluster classification.
2. Assistant-axis projection regression from `axis_projection_layer22`.
3. Semantic-activation residual proxy regression.
4. Nearest-neighbor preservation in the predicted axis-plus-residual space.

The residual summary file requested by the task was not present locally, so the script uses a proxy residual target from existing artifacts: bridge score, role-name-to-no-label displacement, and low semantic margin. This means residual results are methodological signals, not final residual evidence.

Permutation baselines are computed for axis and residual regression by shuffling held-out targets 100 times. This checks whether held-out R2 improvements are above a naive null.

## 5. Proposed Latent Dimensions

Iteration 1 proposed four broad dimensions:

- `procedural_professional_orientation`
- `theatrical_fantastical_vividness`
- `interpersonal_lived_reactivity`
- `oppositional_moral_pressure`

Iteration 2 added four refinement dimensions:

- `assistant_basin_adjacency`
- `boundary_liminal_instability`
- `collectivized_or_nonindividual_agency`
- `communicative_media_register`

Iteration 3 added three failure-analysis dimensions:

- `semantic_label_dependence_risk`
- `standards_and_error_aversion`
- `forceful_self_assertion`

These are hypotheses about behavioral stance and enacted organization. They are not claims about consciousness, inner experience, or causal mechanisms.

## 6. Which Dimensions Generalized

The strongest held-out single-dimension correlations with assistant-axis projection were:

- `procedural_professional_orientation`: r = 0.470
- `semantic_label_dependence_risk`: r = -0.337
- `theatrical_fantastical_vividness`: r = -0.317
- `assistant_basin_adjacency`: r = 0.282
- `standards_and_error_aversion`: r = 0.248

The strongest held-out residual-proxy correlations were weaker:

- `interpersonal_lived_reactivity`: r = -0.220
- `oppositional_moral_pressure`: r = -0.117
- `forceful_self_assertion`: r = 0.097
- `collectivized_or_nonindividual_agency`: r = -0.095
- `standards_and_error_aversion`: r = 0.072

The first-pass result suggests that procedural-professional orientation, assistant-basin adjacency, standards/error aversion, and theatrical/fantastical vividness are useful candidates for predicting axis placement. The residual-proxy task remains less clearly explained.

## 7. Which Dimensions Failed

Latent features did not improve activation-cluster classification. The semantic baseline reached 0.600 held-out accuracy. Iteration 1 dropped to 0.587, iteration 2 dropped to 0.573, and iteration 3 returned to 0.600.

The boundary and communicative-register dimensions also showed weak held-out correlation with axis projection and residual proxy. This does not mean these dimensions are irrelevant. It means the current operationalization is too weak, the target may not be aligned with those concepts, or the concepts do not add predictive value beyond semantic cluster labels in this split.

Iteration 2 improved axis R2 most but harmed the residual proxy. Iteration 3 recovered some residual performance but gave back axis prediction. This pattern suggests that adding more dimensions can overfit or dilute useful structure unless the loop actively prunes failed hypotheses.

## 8. Predictive Improvements Over Semantic Baseline

The best held-out axis projection result occurs in iteration 2:

- Baseline axis R2: 0.301
- Latent axis R2: 0.385
- Improvement: +0.084
- Permutation null p95: -0.006

The best residual-proxy result occurs in iteration 1:

- Baseline residual R2: 0.290
- Latent residual R2: 0.300
- Improvement: +0.010
- Residual MSE reduction: 0.028
- Permutation null p95: 0.054

Nearest-neighbor preservation improves most in iteration 2:

- Baseline preservation: 0.107
- Latent preservation: 0.128
- Improvement: +0.021

Cluster accuracy does not improve:

- Baseline cluster accuracy: 0.600
- Best latent cluster accuracy: 0.600
- Improvement: 0.000

The central preliminary result is therefore narrow: latent features improve held-out continuous axis prediction more than they improve discrete activation-cluster classification.

## 9. Stability Across Iterations

The axis-prediction signal is stable in direction but not monotonic. Iteration 1 improves held-out axis R2 by +0.056. Iteration 2 improves it by +0.084. Iteration 3 still improves over baseline, but only by +0.049.

The residual-proxy signal is weaker and less stable. Iteration 1 improves residual R2 by +0.010, iteration 2 worsens it by -0.007, and iteration 3 improves it by +0.004.

Repeated rediscovery of procedural-professional orientation, assistant-basin adjacency, standards/error aversion, and theatrical vividness across prior human analyses and this loop makes them useful next-step candidates. They should be treated as candidate explanatory variables to refine, not as settled taxonomy.

## 10. Limitations

This is an implementation of the loop architecture, not a completed scientific result.

The current feature operationalization is lexical and prompt-pattern based. It does not yet use external embedding-derived scores, trained classifiers, or model-coded blind ordinal ratings. The residual target is a proxy because the expected residual summary file was absent locally. Activation PCA coordinates are not yet used directly as multidimensional targets; the current continuous target is assistant-axis projection.

The current script encodes GPT-5.5-derived hypotheses in structured form rather than calling GPT-5.5 during execution. This avoids uncontrolled leakage and makes the first iteration reproducible, but the next version should log the exact model input packet, model output, parsing step, feature operationalization, and held-out evaluation for each iteration.

The held-out split is deterministic but single-split. Future work should use repeated splits or nested cross-validation before treating any dimension as robust.

## 11. Future Multi-Model Comparison Design

The next research step is to run the same constrained loop with multiple frontier models as hypothesis generators. Each model should receive the same visible persona packet, propose dimensions under the same schema, have those dimensions operationalized by the same feature compiler, and be evaluated on the same held-out split.

The main comparison question is whether GPT-5.5, Claude Sonnet, and other frontier models converge toward similar explanatory dimensions after iterative correction. Convergence would support the claim that the dimensions reflect stable structure in the persona geometry. Divergence would show that the interpretive instrument is model-dependent and must itself be studied as part of the methodology.

The loop should eventually compare:

- repeated splits within one model,
- repeated runs from different starting packets,
- different frontier-model hypothesis generators,
- different target-model activation geometries,
- and strict blind evaluation on personas never exposed during feature discovery.

The standard for evidence remains predictive improvement and held-out generalization, not persuasive prose.
