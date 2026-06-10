# Thread Start

Canonical startup file: yes
State role: session continuity and immediate priorities
Last updated: 2026-06-10

This is the three-minute continuity file for new GPT, Claude, and Codex threads. Read it after `RESEARCH_STATE.md` and before deeper repo archaeology.

## Current Objective

The active Paper 1.5 objective is to write **Interpreting Persona Activation Geometry**. The paper is no longer primarily an adaptive extraction replication paper. Its contribution is an interpretation of persona activation geometry after methodological stress testing: semantic structure, dispositional/trait structure, procedural/operating-mode structure, lexical/register structure, and residual developmental/liminal/collective structure.

Paper 2 is active planning, not execution. Its current scope is local centroid perturbation and local persona-manifold mapping around anchors such as Trickster, Actor, Therapist, and Spy. Older dyad contagion, attractor-collapse, conversational drift, and rumination plans are archived as future dynamics work.

## Top Findings

Qwen trickster adaptive extraction worked operationally. The run preserved 1200 rollouts and 1200 activation shards, passed integrity, and Codex/GPT-5.5 adaptive scoring reached 64 score>=2 and 33 score==3 responses in 64 scored records. The score>=2 vector matched the Lu trickster mean at cosine 0.957557, and adaptive stopping passed at n=16.

Editor adaptive extraction failed as a second-persona test. The 128-record 512-token editor run produced only 10 score>=2 and 3 score==3 responses. A matched 1024-token run sharply reduced truncation but did not improve role-expression yield. The current interpretation is weak editor anchoring or assistant-adjacent collapse, not a token-cap explanation.

Big Five-style features are the strongest compact global predictor so far, but their provenance is now caveated and the visualization path has been rebuilt. In the shared benchmark, Claude Big Five features predict canonical Qwen activation PCA3D at R2 0.613 versus semantic baseline R2 0.389, while Codex retained procedural/behavioral features reach R2 0.490. A 2026-06-05 provenance audit traced the old Big Five overlay back to `visualizations/bigfive_profiles.json`, generated from activation-derived cluster base scores plus role-name heuristic adjustments. A 2026-06-06 rebuild now provides `research/outputs/same_space_big_five_overlay/`, an activation-derived Big Five layer built from predeclared facets over the 240 released trait vectors for Qwen/Llama/Gemma. Treat the new layer as same-space trait-vector projection, not independent psychometric evidence.

The layered model is currently the best Paper 1.5 frame. A residualized trait-to-procedural hierarchy reaches R2 0.622, residual manifold hand features reach R2 0.632, and sem+BigFive+SVD15 prompt-register structure reaches R2 0.707. The SVD result is strong but lexical/register-sensitive and not yet distilled into stable human-readable factors.

Role-label exposure is a real methodology caveat. The Lu-style system prompts directly expose the target role label or normalized variant in 1280/1375 prompts, 93.1%. However, no-label prompt topology mostly survives label removal, so label exposure is not the whole structure.

Local activation-cloud geometry now supports treating personas as response-state distributions rather than only points. Across amateur, playwright, trickster, and two editor runs, matched-n cloud-shape auditing shows differences in radius, anisotropy, orientation reliability, and filter sensitivity; trickster is least directionally constrained by anisotropy/orientation criteria but is not the largest matched-n cloud.

Frozen no-label elicitation validation partially supports directional prompt design under strict prompt blinding. The 600-response Qwen/Qwen3-32B run passed 4/6 family thresholds at the preregistered 70% prompt-mean criterion, with PC3 bidirectional and PC2-positive strongest; PC1-positive and PC2-negative failed and should not be treated as clean elicitors without revision.

The no-label geometry diagnostic clarifies the PC1-positive failure mode. The published assistant baseline is already high on PC1 (33.703; 83.3rd percentile among Qwen role centroids), but the failed PC1-positive family did not merely saturate there: it moved to mean PC1=-19.352, nearest improviser/bartender/prisoner/actor/loner territory. Treat this as assistant-baseline saturation plus prompt wording that elicited ordinary explanatory/situated response modes.

## Top Open Questions

The bounded Paper 1.5 no-label elicitation validation has now run under matched direct-hook extraction conditions. It used the frozen 60-prompt packet, generated 600 independent Qwen/Qwen3-32B responses, and passed 4/6 preregistered family thresholds: PC1-negative, PC2-positive, PC3-positive, and PC3-negative passed; PC1-positive and PC2-negative failed.

The no-label geometry diagnostic under `research/outputs/no_label_elicitation_geometry_diagnostics/` should be consulted before redesigning the failed families. It shows PC3-negative care prompts strongly couple with negative PC1, and `pc3_pos_05` moved negative PC1 / positive PC2 rather than positive PC3, likely because it foregrounded self-cost/perseverance instead of consequences to others.

Evaluator-model sensitivity remains unresolved. Codex/GPT-5.5 was used as a pragmatic role-expression judge for trickster/editor; strict Lu-method identity requires `gpt-4.1-mini` scoring if API access permits.

PC2 remains the least settled axis. The current best interpretation has shifted away from simple coherent action under uncertainty and toward abstraction/integration/developmental structure. Conditional PC1-band validation found abstraction predicts residual PC2 at r=-0.618, coherent action remains weaker at r=+0.427, and uncertainty exposure fails at r=-0.026.

The Qwen PC1 x PC2 trait-region overlay now exists as a native mode inside `research/visualizations/persona_geometry_explorer.html`, not only as a standalone prototype. It remains a visualization aid, not a final PC2 result. It shows that PC1-band-relative cell labels materially differ from global enrichment labels (mean top-3 overlap 0.18), so future PC2 figures should prefer local PC1-band baselines when the question is vertical structure within comparable PC1 regions.

The new multi-model ordered-axis trait-region viewer in `research/outputs/multimodel_ordered_trait_region_viewer/` generalizes this local-label idea across Qwen, Llama, and Gemma. Its key rule is ordered-axis conditioning: the selected x-axis defines the local baseline, so PC1 x PC2 and PC2 x PC1 are different analyses rather than cosmetic rotations.

The Qwen 275-role x 240-trait profile matrix has now been provenance-audited. It is mixed: the trait names/prompts and Qwen role/trait tensors are inherited Assistant Axis / Lu et al. artifacts, but the CSV matrix used in PC2 analyses is internally generated by cosine similarity between mean-pooled released Qwen role and trait activation vectors. Treat trait-enrichment figures as same-space activation-vector overlays, not independent psychological ratings.

The old Big Five overlay has been provenance-audited. It is not derived from the 240-trait profile matrix, but it is partially dependent on activation geometry because the original scoring script uses activation-derived cluster labels as Big Five base scores. The current evidence-bearing replacement is `research/outputs/same_space_big_five_overlay/`, labeled "Activation-derived Big Five from 240 trait vectors" with the caveat "Same-space trait-vector projection, not independent psychometric rating."

SVD15 lexical/register signal is strong but not yet converted into stable explanatory features. The next useful step is distilling concrete SVD extremes into human-readable residual dimensions and retesting them under the shared splits.

## Current Interpretations

PC1 is moderately well supported as careful/evaluative/procedural control, objective certainty, disciplined expertise, and externally legible competence versus open/symbolic/expressive possibility. PC1 aligns with the assistant-axis vector at 0.802310. It should not be reduced to literal assistantness.

PC2 is currently best described as abstraction/integration/developmental structure. Lower PC2 is more abstract, world-model-like, integrated, and long-residence. Higher PC2 is more developmental, reactive, socially volatile, or less integrated. Coherent action under unresolved uncertainty is now a secondary behavioral expression, not the primary label.

PC3 is moderately supported as cooperative-care/system-stabilizing versus antagonistic/disruptive/transgressive stance. The reading-based rater study gives PC3 r=0.690, but professional-subset counterexamples show that PC3 is not only reform, critique, or perturbation.

The no-label elicitation validation provides partial activation-space support for the working PC interpretations under prompt-text-only conditions. It should be framed as a modest directional result, not proof: PC3 was strongest bidirectionally, PC2-positive worked while PC2-negative was mixed, and PC1-positive moved opposite the intended direction relative to the published assistant centroid.

The PC1-positive no-label failure should not be described as pure ceiling saturation. The assistant baseline is already high PC1, but the family mean moved substantially negative on PC1, so prompt wording and generic helpful-answer dynamics are likely part of the failure.

The cone hypothesis remains speculative. The geometry appears to narrow at high PC1 and widen as PC1 decreases, suggesting that externally specified objectives may constrain admissible configurations. This still needs quantitative variance-by-PC1 testing and sampling-artifact controls.

Persona vectors should be described as centroids of local response-state distributions when discussing activation-cloud pilots. Cloud shape metrics are promising but remain future Paper 2/local-manifold evidence until sampled across more roles under balanced conditions.

## Current Risks

Do not overstate Lu-method replication. Codex/GPT-5.5 scoring, adaptive stopping, no-label prompt ablation, and reading-based Codex ratings are methodological extensions or pragmatic substitutions.

Do not conflate prompt-space findings with activation-space causality. Semantic topology, no-label topology, and SVD/register structure are evidence about the elicitation corpus and its relation to activations, not proof that activation geometry is "just semantics."

Do not treat Big Five features as psychological ground truth or as fully independent evidence. The old overlay is cluster-conditioned and partly activation-dependent; the new activation-derived overlay is same-space trait-vector evidence and should not be described as psychometric measurement.

Do not treat the 240-trait Qwen profile matrix as independent validation of role PCA geometry. It is derived from the same Qwen activation-vector artifact family as the role PCA geometry, so strong reconstruction or enrichment is same-space evidence.

Do not treat PC2 as solved. Recent tests weakened the simple uncertainty-capacity formulation and strengthened abstraction/integration language, but independent-rater replication is still needed.

Do not rely on chat memory for state, pod status, or file paths. Use `RESEARCH_STATE.md`, this file, `CLAIMS_REGISTER.md`, `RESEARCH_INDEX.md`, and `PROVENANCE_REGISTRY.md`.

Do not rely on legacy `research/findings_log.md` as the primary record. New findings, interpretations, negative results, methodology constraints, and claim-relevant evidence should be recorded in the canonical registries: `research/FINDINGS_LEDGER.md`, `research/CLAIMS_REGISTER.md`, and `research/PROVENANCE_REGISTRY.md` as appropriate.

Material artifact changes must keep `research/REPO_NAVIGATION.md`, `research/REPO_FILE_INDEX.csv`, and `research/RAW_URL_INDEX.md` current, including artifact status assignment (`canonical`, `active`, `archive`, or `deprecated`). Significant changes to active objectives, top findings, top open questions, current interpretations, current risks, or next experiments also require this file to be updated before commit.

For PC1 x PC2 trait-region inspection, use the integrated controls in `research/visualizations/persona_geometry_explorer.html`: `Trait regions` selects Off/Top1/Top3/Top5, `Region basis` selects quantile bands or fixed explorer grid, and `Color by: Region Cluster` colors points by the region chip semantics rather than Assistant Axis projection.

For cross-model ordered-axis trait-region inspection, use `research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_viewer.html`. Prefer quantile basis as the stable default; fixed-grid views are descriptive and sparse cells are flagged.

## Next Experiments

1. Use `research/outputs/same_space_big_five_overlay/` as the evidence-bearing same-space Big Five visualization layer if Big Five overlays are needed; build blinded independent ratings only if independent psychometric-style validation is required.
2. Run an independent-rater PC2 disentanglement study over the strongest PC1-matched pairs, explicitly separating abstraction, maturity/integration, expertise, uncertainty exposure, and coherent action under uncertainty.
3. Use `research/outputs/no_label_elicitation_geometry_diagnostics/` before designing a second no-label packet: revise PC1-positive prompts against the assistant-baseline saturation/generic-helpful failure mode, separate self-cost from consequence-to-others pressure in PC3-positive prompts, and treat PC2-negative as mixed until prompt-level context is inspected.
4. Finish evaluator-sensitivity comparison between Codex/GPT-5.5 and `gpt-4.1-mini` if API quota allows.
5. Distill SVD15 prompt-register components into concrete human-readable residual features and retest under the shared benchmark splits.
5. Use Paper 2 grant/H100 work for local centroid perturbation around Trickster, Actor, Therapist, and Spy.
6. Extend the activation-cloud geometry audit to a balanced role set before making strong claims about persona-specific cloud size, anisotropy, or orientation.
