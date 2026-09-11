# Grant Application Scope

Paper 1.5 is now strong enough to stand as a persona-geometry interpretation paper without requiring additional H100 work. The existing trickster extraction demonstrated that the project can launch, preserve, score, validate, and audit Qwen/Qwen3-32B persona-vector runs. That result should be presented as evidence of tooling competence, not as the main intellectual claim of Paper 1.5.

The grant-supported next phase should fund local centroid perturbation experiments around selected persona anchors. The strongest candidate anchors are Trickster, Actor, Therapist, and Spy.

Trickster is the validated high-signal anchor and is scientifically useful for studying destabilization, provocation, boundary testing, and playful transgression.

Actor is useful for studying identity flexibility, mimetic amplification, performance, role uptake, and movement between selves.

Therapist is useful for studying attunement, receptivity, identity formation, nonreactive inquiry, and the geometry of inquiry that changes the subject without forcing it.

Spy is useful for studying concealment, strategic disclosure, asymmetric information, deception-adjacent structure, and controlled opacity.

The grant framing should distinguish the current Paper 1.5 from future H100 work. Paper 1.5 is a global geometry interpretation paper: it asks how persona activation geometry decomposes into semantic, dispositional, procedural, lexical/register, and residual structures after methodological stress testing. Paper 2 and the grant-supported work should become the local geometry program: map the neighborhood around selected centroids, perturb controlled persona features, extract local basis directions, and test whether those directions transfer across anchors.

Local-manifold H100 work is not required for Paper 1.5. It strengthens the grant proposal because it shows a concrete next experimental frontier that follows naturally from the Paper 1.5 interpretation and from the demonstrated ability to run and preserve persona-vector experiments.

## Update 2026-09-11

Completed the CPU-only first-stage profile-to-geometry predictor under `research/outputs/trait_profile_pc_predictor/`. A transparent raw-cosine Ridge model now maps complete 240-trait activation-derived profiles to canonical Qwen PC1/PC2/PC3 with all-persona LOPO R2=0.999522/0.998811/0.999611, harder canonical-cluster holdouts, OOD/error context, and deterministic percentile-edit examples for Trickster, Actor, Therapist, and Spy. Synthetic activation interpolation was also validated after exact PCA-basis reproduction, with both source endpoints excluded from each fit. This strengthens the grant's local-mapping feasibility case but does not replace the proposed H100 behavioral experiment: a newly elicited persona has not yet been compared with its frozen predicted coordinate.
