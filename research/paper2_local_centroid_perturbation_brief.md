# Paper 2 Local Centroid Perturbation Brief

## Purpose

Paper 2 is now framed around local centroid perturbation and local persona-manifold mapping. It follows from Paper 1.5's layered interpretation of global persona geometry by asking whether local neighborhoods around selected persona centroids have reusable directions or whether the geometry is strongly curved and anchor-dependent.

## Why This Follows From Paper 1.5

Paper 1.5 suggests that global persona geometry decomposes into semantic, dispositional, procedural, lexical/register, and residual layers. A natural next step is to stop treating centroids as isolated labels and instead map the local tangent structure around them. Local perturbation can test whether directions such as provocation, concealment, empathy, dominance, theatricality, and moral constraint behave consistently across different persona neighborhoods.

## Candidate Anchors

Trickster is the strongest initial anchor because Qwen/Qwen3-32B trickster extraction has already validated the tooling path and reproduced the Lu reference geometry under the pragmatic Codex-scored workflow. It is useful for studying destabilization, provocation, boundary testing, and playful transgression.

Actor is a strong anchor for identity flexibility, mimetic amplification, performance, role uptake, and transitions between self-presentations. It offers a local manifold likely to contain controlled directions of imitation, sincerity, theatricality, and identity instability.

Therapist is a strong anchor for attunement, receptivity, identity formation, nonreactive inquiry, containment, and cooperative transformation. It is scientifically useful because it lies near helpfulness and care without being merely editorial or procedural.

Spy is a strong anchor for concealment, strategic disclosure, asymmetric information, deception-adjacent structure, selective truthfulness, and controlled opacity. It offers a local manifold where epistemic access and social intent can be perturbed directly.

## Why Editor Is Not the Right Anchor

Editor is not a good first local-manifold anchor. The first editor adaptive extraction test produced only 10 score>=2 and 3 score==3 responses in 128 records, and the matched 1024-token follow-up reduced truncation without improving role-expression yield. The current interpretation is that assistant-adjacent editor prompts collapse toward generic assistant behavior under the current Lu-style setup. A local manifold around editor would likely be dominated by the assistant basin unless anchoring is redesigned first.

## Core Experiment

For each anchor persona, generate controlled perturbation variants around the centroid. Extract vectors for each variant under the same layer and extraction convention. Compute deviations from the anchor centroid. Estimate local basis directions and test whether those directions transfer across anchors.

Candidate local directions include provocation, deception/concealment, empathy/attunement, identity flexibility, dominance/submission, theatricality, destabilization, strategic disclosure, moral constraint, sincerity/performance, and receptivity/control.

The central scientific question is: does persona space contain reusable local directions, or is its geometry strongly curved and persona-dependent?

## H100 Requirements and Efficiency

This work is compute-intensive but bounded. It should use the validated detached execution, JSONL preservation, activation-shard preservation, integrity-check, and local-scoring workflow from the trickster and editor runs. It should not begin with exhaustive 1200-rollout extraction for every perturbation. Instead, it should use small adaptive chunks, score locally after preservation, and expand only where yield or convergence requires it.

## Grant Relevance

This is the strongest next grant-supported experimental frontier. Paper 1.5 can stand as the global geometry interpretation paper without additional H100 work. The grant can fund Paper 2's local-manifold mapping as the next phase, with a clear technical path already demonstrated by the trickster extraction run.
