# Multi-Model Latent Feature Comparison Plan

Date: 2026-05-28
Status: Future plan only

## Purpose

The first latent-feature discovery loop uses GPT-5.5 Standard as the hypothesis generator and evaluates proposed dimensions against held-out persona activation geometry. The next methodological question is whether the same loop converges to similar latent explanatory dimensions when different frontier models are used as hypothesis generators.

The future comparison should test convergence across:

- GPT-5.5 Standard
- Claude Sonnet
- at least one additional frontier model

The models are not evidence sources. They are interpretive instruments whose outputs must be operationalized and tested.

## Core Question

Do different frontier models converge toward similar latent explanatory dimensions under iterative correction?

Convergence would suggest that the discovered dimensions are not only artifacts of one model's interpretive style. Divergence would show that model identity affects the hypotheses and that model provenance must be treated as part of the experimental design.

## Shared Input Packet

Each model receives the same visible split of personas and the same fields:

- role name
- no-label prompt summary
- semantic cluster assignments
- activation cluster assignment
- assistant-axis projection band
- bridge or anchor status
- nearest semantic neighbors
- nearest activation neighbors where available
- residual-proxy rank band

The held-out evaluation split is never shown to the hypothesis-generating model.

## Output Schema

Each model must return candidate dimensions in a structured schema:

- stable dimension name
- concise description
- expected high-scoring personas
- expected low-scoring personas
- operationalization rule candidates
- predicted target relevance
- known failure modes

Freeform essays are not accepted as analysis artifacts. Any prose must be converted into measurable features before evaluation.

## Operationalization

All model outputs pass through the same feature compiler. Candidate operationalizations include:

- binary lexical indicators
- ordinal prompt-pattern scores
- embedding-derived similarity scores
- blind model-coded ordinal ratings
- simple trained classifiers with held-out validation

No model is allowed to directly predict arbitrary coordinates. It can propose dimensions, but prediction is done by the evaluation harness.

## Evaluation

Each model's proposed feature set is evaluated against identical held-out targets:

- activation cluster classification accuracy
- assistant-axis or PCA-coordinate held-out R2
- semantic-activation residual reduction
- nearest-neighbor preservation
- permutation or shuffled-label null baselines

The comparison should report absolute performance and improvement over the semantic baseline.

## Iterative Correction

Each model receives only aggregate failure summaries from the previous iteration, not the hidden labels for individual held-out personas. The loop records:

- which dimensions recur across iterations,
- which dimensions are pruned,
- which dimensions improve held-out prediction,
- which dimensions fail under operationalization,
- and whether returns diminish after two or three iterations.

## Convergence Metrics

Convergence can be measured at several levels:

- name-level overlap after normalization,
- description embedding similarity,
- correlation between operationalized feature scores,
- agreement on top predictive dimensions,
- agreement on failure cases,
- and held-out performance similarity.

The strongest convergence evidence would be independent models proposing different wording that operationalizes into highly correlated feature scores and similar held-out gains.

## Required Controls

The comparison should include:

- identical visible and held-out splits,
- identical feature compiler,
- identical evaluation metrics,
- identical prompt templates,
- recorded model provenance,
- repeated runs for stochastic models,
- and a null condition using randomized or shuffled dimensions.

## Expected Outcomes

Three outcomes are possible.

First, frontier models converge on dimensions such as procedural orientation, theatrical vividness, assistant-basin adjacency, standards/error aversion, and interpersonal reactivity. This would make those dimensions stronger candidates for formal testing.

Second, frontier models disagree, but each improves prediction in different target regions. This would suggest that persona geometry has multiple partial explanatory decompositions.

Third, dimensions do not generalize beyond the semantic baseline. This would be a negative result for model-assisted interpretive discovery under the current feature compiler.

## Next Implementation Step

The next implementation should add a model-call mode to `latent_feature_discovery_loop.py` that writes the exact visible packet, prompt, raw model response, parsed dimensions, feature operationalization, and evaluation results for each iteration. The default mode should remain offline and reproducible.
