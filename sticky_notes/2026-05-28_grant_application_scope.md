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

## Update 2026-09-11

The same CPU-only complete-profile mapping now replicates in the saved Llama-3.3-70B and Gemma-2-27B vector sets using each model's own verified persona PCA. Raw Ridge LOPO normalized 3D RMSE is 0.1245 for Llama and 0.1278 for Gemma, whole Qwen-canonical role-family holdout is harder, and endpoint-held-out synthetic mixtures remain predictable; Ridge stays sufficient in both. This is factual cross-model same-space feasibility evidence for the local-mapping program, not a claim that any model has more sophisticated or human-like psychology, and it still does not replace the proposed behavioral elicitation experiment.

## Update 2026-09-11 — Dimensionality Scope for Local Mapping

The full-rank CPU-only PCA audit shows that the existing three-PC convention came from the original 3D display, not a dimensionality cutoff. Qwen PC1-PC3 remain the strict bootstrap-stable core (56.449% cumulative centered role-activation variance), while PC4-PC6 form a weaker supported secondary set under combined null, moderate-bootstrap, trait-coherence, and cross-model role-score recurrence evidence (67.408% cumulative). Later Qwen PCs are exploratory or unstable despite some exceeding the random-data reference.

Grant and Paper 2 local-manifold designs should therefore preregister PC1-PC3 as the primary coordinate outcomes and may include PC4-PC6 as secondary outcomes rather than silently truncating them or elevating them to equal status. This is a factual design refinement, not a new grant claim: PC4-PC6 do not yet have independently validated semantic labels, and shared role instructions may contribute to their cross-model recurrence. No additional H100 work is required for the current Paper 1.5 dimensionality result.

## Update 2026-09-11 — Compact Traits and Basis Coverage

The Qwen sparsity and matched-basis audit materially narrows the grant claim. Compact selected real trait directions are genuinely useful within the saved 275-role inventory: selected 15 reaches normalized RMSE 0.0872 and beats every matched random-real, isotropic, and fold-local persona-span bank. But a 240-direction fold-local persona-span random basis reaches 0.0514 versus repeated full-real 0.0476, and the full trait span covers more than 98% of each PC loading. Grant language should therefore present compact traits as efficient predictive coordinates, not as a validated causal psychology; near-ceiling complete-profile accuracy is substantially high-dimensional basis coverage. This strengthens the case for the proposed new-behavior experiment: freeze compact and full-profile predictions, then test both against newly elicited activation coordinates without refitting.

## Update 2026-09-12 — AA-7 Human-Supported Convergence Gate

AA-7 narrows the human-convergence grant case. The 12 labels frozen from prior human psychometric support do not outperform matched random-real k=12 subsets in any model/scope and outperform fold-local persona-span controls only for Qwen/Gemma PC1-PC3. Do not claim that human psychometric defensibility identifies unusually efficient model coordinates, and do not use AA-7 to justify a human-respondent projection study; its preregistered design gate failed.

The model-only cross-model result is stronger: held-out PC1-PC6 role-score alignment exceeds permutation, the corresponding activation-derived human-supported and strict Big Five directions recur after rotation, and Agreeableness's local-PC mismatch reconciles. This may support a bounded Paper 1.5 appendix and future cross-model replication, but it does not replace behavioral elicitation/local-manifold experiments and should not be framed as human/model equivalence.
