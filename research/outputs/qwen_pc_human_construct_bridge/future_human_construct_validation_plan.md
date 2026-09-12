# Future validation plan for the frozen Qwen-derived human-construct hypotheses

Status: design only; nothing in this plan was executed  
Frozen discovery input: `qwen_derived_human_construct_hypotheses_v1.csv`  
Required validation label until completion: `DISCOVERY_ONLY / NOT YET CROSS-MODEL VALIDATED`

## Purpose

Test whether the construct hypotheses selected from Qwen PC1-PC6 survive evidence that was not used to select them. The plan separates semantic, model, behavioral, and human-measurement validation because success in one does not imply success in the others.

## Gate 1 — independent human expert review

Before any respondent projection, give an independently recruited personality/psychometrics reviewer:

- the authoritative human construct definitions and item content;
- anonymized Qwen pole signatures with PC numbers, role labels, coefficients, cross-model results, and downstream performance hidden;
- the frozen rubric and a preregistered adjudication form.

The reviewer should judge construct coverage, important mismatches, hierarchy, and whether missing constructs need different instruments. Agreement with the present mapping must be reported, including disagreements; discordant rows must not be silently retained. Claude's genuinely separate semantic review is valuable for the earlier literal trait links, but it is not a substitute for human psychometric expertise on this new domain-level bridge.

## Gate 2 — choose one genuinely held-out model test

The choice should be preregistered before inspecting candidate-model results.

### Option A: new Qwen role inventory

Create a new role inventory with preregistered role descriptions targeting the frozen construct poles without reusing the 275 labels. Elicit and extract activations only in a future authorized compute run. Fit the old Qwen PCA projection without refitting axes, then test whether blinded human-construct ratings predict the corresponding frozen PCs.

Strength: directly tests generalization beyond the discovery role inventory while holding model family fixed.  
Risk: Qwen-family specificity and prompt-template dependence remain.

### Option B: a new model family

Use a model family and role inventory not involved in discovery, fit its geometry independently, and preregister a role-score/subspace correspondence test. Do not choose components post hoc by semantic convenience without a search-adjusted null.

Strength: stronger architecture-level independence.  
Risk: axes may rotate; subspace tests may be more appropriate than one-to-one PC matching.

### Option C: Llama or Gemma saved artifacts

Llama or Gemma can provide a lower-cost frozen-artifact comparison after this hypothesis file is committed. However, they share the role labels and broader project pipeline, and prior cross-model analyses already exist elsewhere in the repository. To preserve a meaningful held-out claim, the future analyst must preregister the exact mapping metric before opening those result files and must treat any pre-existing analyst exposure as a limitation.

Strength: deterministic and inexpensive.  
Risk: weaker independence; shared role prompts can drive recurrence. AA-7 is therefore not automatically the preferred next test.

### Option D: behaviorally elicited Qwen responses

Obtain blinded ratings or independent behavioral measures from new elicited responses, then test their relation to the frozen axes and constructs.

Strength: tests realized behavior rather than saved role-vector semantics.  
Risk: requires new inference, scoring reliability, and strict separation of construct labels from raters.

## Gate 3 — human measurement model under SAPA planned missingness

For the SAPA-available constructs, estimate a hierarchical human measurement model without using any Qwen coordinate as a target:

1. reproduce official item directions and scale keys;
2. model the randomized planned-missing design using full-information factor/IRT methods or a prevalidated partial-information alternative;
3. estimate domain/aspect/facet scores with uncertainty;
4. evaluate measurement invariance and reliability where demographic comparisons are contemplated;
5. reserve a held-out human subsample for scoring-model checks.

Ordinary complete-case scoring is inappropriate: the median selected construct has one administered item per respondent, and almost no one completes a full key. Pairwise covariance supports structure estimation but does not by itself yield reliable individual profiles.

Need for Cognitive Closure, the most plausible unavailable PC6 candidate, requires a different dataset or a newly administered dedicated instrument. It must not be approximated by SAPA Traditionalism or interpersonal Flexibility merely to obtain coverage.

## Gate 4 — preregister a human/model correspondence test

Only after Gates 1-3:

- freeze the human measurement model, construct hierarchy, polarity, and any composite definitions;
- state the unit of analysis and null model;
- specify how uncertainty in human scores and model-axis instability enters the test;
- separate domain-level, aspect/facet, and model-specific residual hypotheses;
- reserve a genuinely held-out human or model dataset for confirmatory evaluation.

The test must not select constructs, signs, weights, or occupations by maximizing correspondence to Qwen coordinates.

## Candidate independent human sources

- A dataset administering complete IPIP-NEO/BFAS/HEXACO scales could validate the PC1/PC3 hierarchies with much less planned missingness than SAPA.
- A dataset administering the Need for Closure Scale would address the PC6 residual candidate.
- NLSY97 is useful for later external outcomes and adequately sized preregistered occupation families, but its brief personality inventory is not a 126-construct bridge.
- A new targeted public-domain survey could administer only the frozen PC-specific constructs and preserve a clean confirmatory sample, subject to ethics and privacy review.

## Decision rule

Proceed to respondent-to-model projection only if independent expert review retains a coherent subset, the human measurement model produces sufficiently reliable scores under planned missingness, and at least one model-side held-out test supports the preregistered construct pattern. Otherwise report the bridge as descriptive and revise it without looking at respondent-to-Qwen outcomes.

This plan does not select Llama, Gemma, or any other source as the required next test. Independence, preregistration, and measurement quality determine that choice.
