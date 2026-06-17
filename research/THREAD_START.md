# Thread Start

Canonical startup file: yes
State role: session continuity and immediate priorities
Last updated: 2026-06-17

This is the three-minute continuity file for new GPT, Claude, and Codex threads. Read it after `RESEARCH_STATE.md` and before deeper repo archaeology.

## Current Objective

The active Paper 1.5 objective is to write **Interpreting Persona Activation Geometry**. The paper is no longer primarily an adaptive extraction replication paper. Its contribution is an interpretation of persona activation geometry after methodological stress testing: semantic structure, dispositional/trait structure, procedural/operating-mode structure, lexical/register structure, and residual developmental/liminal/collective structure.

Paper 2 is active planning, not execution. Its current scope is local centroid perturbation and local persona-manifold mapping around anchors such as Trickster, Actor, Therapist, and Spy. Older dyad contagion, attractor-collapse, conversational drift, and rumination plans are archived as future dynamics work.

The canonical writing-phase source for Paper 1.5 is now `research/paper15_content_ledger.md`, with source inventory in `research/paper15_content_ledger_artifact_inventory.csv`. Use it before drafting prose. It separates observed findings, interpretations, hypotheses, caveats, rejected explanations, claims inventory, open questions, and inclusion recommendations.

## Top Findings

Qwen trickster adaptive extraction worked operationally. The run preserved 1200 rollouts and 1200 activation shards, passed integrity, and Codex/GPT-5.5 adaptive scoring reached 64 score>=2 and 33 score==3 responses in 64 scored records. The score>=2 vector matched the Lu trickster mean at cosine 0.957557, and adaptive stopping passed at n=16.

Editor adaptive extraction failed as a second-persona test. The 128-record 512-token editor run produced only 10 score>=2 and 3 score==3 responses. A matched 1024-token run sharply reduced truncation but did not improve role-expression yield. The current interpretation is weak editor anchoring or assistant-adjacent collapse, not a token-cap explanation.

Big Five-style features are the strongest compact global predictor so far, but their provenance is now caveated and the visualization path has been rebuilt. In the shared benchmark, Claude Big Five features predict canonical Qwen activation PCA3D at R2 0.613 versus semantic baseline R2 0.389, while Codex retained procedural/behavioral features reach R2 0.490. A 2026-06-05 provenance audit traced the old Big Five overlay back to `visualizations/bigfive_profiles.json`, generated from activation-derived cluster base scores plus role-name heuristic adjustments. A 2026-06-06 rebuild now provides `research/outputs/same_space_big_five_overlay/`, an activation-derived Big Five layer built from predeclared facets over the 240 released trait vectors for Qwen/Llama/Gemma. Treat the new layer as same-space trait-vector projection, not independent psychometric evidence.

The layered model is currently the best Paper 1.5 frame. A residualized trait-to-procedural hierarchy reaches R2 0.622, residual manifold hand features reach R2 0.632, and sem+BigFive+SVD15 prompt-register structure reaches R2 0.707. The SVD result is strong but lexical/register-sensitive and not yet distilled into stable human-readable factors.

The GPT-5.5 coordinate-blind PC interpretation rating benchmark is now complete. Using only the five role instructions per persona and no coordinate/geometry/ranking/cluster targets, three ratings recover meaningful canonical Qwen activation geometry under the shared deterministic splits: PC1 external-standard accountability R2=0.704, PC2 signed integration/coherence R2=0.423, PC3 internal-objective-vs-care R2=0.393, and joint mean R2=0.525. This is stronger than semantic baseline and Codex retained procedural features, but weaker than Big Five, hierarchical, residual-manifold, and SVD15 feature families.

The focused PC1 accountability activation validation is now complete. Under the same Qwen/Qwen3-32B direct layer-48 hook extraction protocol as Run 2, accountability/scrutiny framing moved PC1 more positive than determination framing in 5/5 matched pairs (mean B-A +3.297, 95% CI [1.574, 5.020]) and more positive than arithmetic/checking framing in 5/5 matched pairs (mean B-A +9.551, 95% CI [7.592, 11.510]), with zero errors over 200 generations.

Role-label exposure is a real methodology caveat. The Lu-style system prompts directly expose the target role label or normalized variant in 1280/1375 prompts, 93.1%. However, no-label prompt topology mostly survives label removal, so label exposure is not the whole structure.

Local activation-cloud geometry now supports treating personas as response-state distributions rather than only points. Across amateur, playwright, trickster, and two editor runs, matched-n cloud-shape auditing shows differences in radius, anisotropy, orientation reliability, and filter sensitivity; trickster is least directionally constrained by anisotropy/orientation criteria but is not the largest matched-n cloud.

Frozen no-label elicitation validation partially supports directional prompt design under strict prompt blinding. The 600-response Qwen/Qwen3-32B run passed 4/6 family thresholds at the preregistered 70% prompt-mean criterion, with PC3 bidirectional and PC2-positive strongest; PC1-positive and PC2-negative failed and should not be treated as clean elicitors without revision.

The no-label geometry diagnostic clarifies the PC1-positive failure mode. The published assistant baseline is already high on PC1 (33.703; 83.3rd percentile among Qwen role centroids), but the failed PC1-positive family did not merely saturate there: it moved to mean PC1=-19.352, nearest improviser/bartender/prisoner/actor/loner territory. Treat this as assistant-baseline saturation plus prompt wording that elicited ordinary explanatory/situated response modes.

The assistant baseline/centroid used in Paper 1.5 is now provenance-audited. It is the released Qwen `assistant` role/persona vector selected from reconstructed canonical role coordinates, not bare Qwen, not `default_vector.pt`, and not `assistant_axis.pt`. Future no-label interpretation should say "movement relative to the assistant role centroid" unless a separate bare-Qwen/default baseline is used.

Run 2 of the no-label elicitation program is now completed. The frozen package under `research/outputs/no_label_elicitation_run2/` produced 1,690/1,690 Qwen/Qwen3-32B generations with zero errors and preserved 1,690 local gitignored activation shards; the bare-Qwen 240-question baseline centroid is PC1=23.510, PC2=14.041, PC3=-2.460.

The default Assistant baseline audit is complete. `downloads/hf_vectors/qwen-3-32b/default_vector.pt` is the released Lu et al. default/no-role vector, while `assistant_axis.pt` is a direction/difference vector rather than a centroid. Projected into the canonical Paper 1.5 Qwen PCA basis, the default vector is PC1=27.131, PC2=8.005, PC3=-6.631. It is distinct from both the role-conditioned assistant centroid and the stricter Run 2 bare no-system centroid, so Paper 1.5 should keep all three reference points rather than replacing the bare baseline with Lu's default vector.

## Top Open Questions

The current PC1 external-standard accountability interpretation now has three related diagnostics: the sparse-vocabulary competing-theories screen under `research/outputs/pc1_competing_theories_test/`, the stronger GPT-5.5 coordinate-blind rating benchmark under `research/outputs/blind_pc_interpretation_rating_benchmark/`, and the execution-time activation diagnostic under `research/outputs/pc1_accountability_validation/`. Exact vocabulary evidence is weak after controls, but the direct blind rating gives PC1 R2=0.704 and the activation diagnostic separates accountability/scrutiny from determination and arithmetic/checking in 10/10 matched pair contrasts. Do not describe PC1 as proven; do treat external-standard accountability as the strongest current compact PC1 wording.


The bounded Paper 1.5 no-label elicitation validation has now run under matched direct-hook extraction conditions. It used the frozen 60-prompt packet, generated 600 independent Qwen/Qwen3-32B responses, and passed 4/6 preregistered family thresholds: PC1-negative, PC2-positive, PC3-positive, and PC3-negative passed; PC1-positive and PC2-negative failed.

The no-label geometry diagnostic under `research/outputs/no_label_elicitation_geometry_diagnostics/` should be consulted before redesigning the failed families. It shows PC3-negative care prompts strongly couple with negative PC1, and `pc3_pos_05` moved negative PC1 / positive PC2 rather than positive PC3, likely because it foregrounded self-cost/perseverance instead of consequences to others.

The 240-question bare-Qwen extraction-question baseline is now a foundational prerequisite for future no-label elicitation interpretation, not optional exploratory cleanup. The existing assistant star/centroid is role-conditioned, so the planned baseline is needed to determine the instrument's default/bare response distribution.

Before discussing Run 2 results, start with `research/outputs/no_label_elicitation_run2/run2_report.md`, `run2_execution_status.json`, `run2_family_mean_results.csv`, `run2_pairwise_effects.csv`, and `run2_local_integrity_check.json`. As of 2026-06-13, total completed generations are 1,690/1,690 with zero error flags. For baseline-provenance language, also consult `research/outputs/default_assistant_baseline_audit/default_assistant_baseline_audit_report.md`.

Evaluator-model sensitivity remains unresolved. Codex/GPT-5.5 was used as a pragmatic role-expression judge for trickster/editor; strict Lu-method identity requires `gpt-4.1-mini` scoring if API access permits.

PC2 remains the least settled axis. The current best interpretation has shifted away from simple coherent action under uncertainty and toward abstraction/integration/developmental structure. Conditional PC1-band validation found abstraction predicts residual PC2 at r=-0.618, coherent action remains weaker at r=+0.427, and uncertainty exposure fails at r=-0.026.

The Qwen PC1 x PC2 trait-region overlay now exists as a native mode inside `research/visualizations/persona_geometry_explorer.html`, not only as a standalone prototype. It remains a visualization aid, not a final PC2 result. It shows that PC1-band-relative cell labels materially differ from global enrichment labels (mean top-3 overlap 0.18), so future PC2 figures should prefer local PC1-band baselines when the question is vertical structure within comparable PC1 regions.

The new multi-model ordered-axis trait-region viewer in `research/outputs/multimodel_ordered_trait_region_viewer/` generalizes this local-label idea across Qwen, Llama, and Gemma. Its key rule is ordered-axis conditioning: the selected x-axis defines the local baseline, so PC1 x PC2 and PC2 x PC1 are different analyses rather than cosmetic rotations.

The Qwen 275-role x 240-trait profile matrix has now been provenance-audited. It is mixed: the trait names/prompts and Qwen role/trait tensors are inherited Assistant Axis / Lu et al. artifacts, but the CSV matrix used in PC2 analyses is internally generated by cosine similarity between mean-pooled released Qwen role and trait activation vectors. Treat trait-enrichment figures as same-space activation-vector overlays, not independent psychological ratings.

The old Big Five overlay has been provenance-audited. It is not derived from the 240-trait profile matrix, but it is partially dependent on activation geometry because the original scoring script uses activation-derived cluster labels as Big Five base scores. The current evidence-bearing replacement is `research/outputs/same_space_big_five_overlay/`, labeled "Activation-derived Big Five from 240 trait vectors" with the caveat "Same-space trait-vector projection, not independent psychometric rating."

SVD15 lexical/register signal is strong but not yet converted into stable explanatory features. The next useful step is distilling concrete SVD extremes into human-readable residual dimensions and retesting them under the shared splits.

## Current Interpretations

PC1 is moderately well supported as careful/evaluative/procedural control, objective certainty, disciplined expertise, external-standard accountability, and externally legible competence versus open/symbolic/expressive possibility. PC1 aligns with the assistant-axis vector at 0.802310, a coordinate-blind GPT-5.5 role-instruction rating recovers PC1 at R2=0.704, and a focused Qwen activation diagnostic shows accountability/scrutiny wording moves PC1 more positive than determination or arithmetic/checking wording under matched scenarios. It should not be reduced to literal assistantness.

PC2 is currently best described as abstraction/integration/developmental structure. Lower PC2 is more abstract, world-model-like, integrated, and long-residence. Higher PC2 is more developmental, reactive, socially volatile, or less integrated. A coordinate-blind GPT-5.5 integration/coherence rating predicts PC2 at R2=0.423 after signing high integration toward negative PC2. Coherent action under unresolved uncertainty is now a secondary behavioral expression, not the primary label.

PC3 is moderately supported as cooperative-care/system-stabilizing versus internal-objective/disruptive/transgressive stance. The reading-based rater study gives PC3 r=0.690, and the coordinate-blind GPT-5.5 internal-objective-vs-care rating predicts PC3 at R2=0.393. Professional-subset counterexamples show that PC3 is not only reform, critique, or perturbation.

The no-label elicitation validation provides partial activation-space support for the working PC interpretations under prompt-text-only conditions. It should be framed as a modest directional result, not proof: Run 1 showed PC3 strongest bidirectionally, PC2-positive working while PC2-negative was mixed, and PC1-positive moving opposite the intended direction relative to the published assistant centroid. Run 2 adds a foundational bare-Qwen baseline and shows PC2-negative/integrative-whole prompts are much cleaner relative to bare Qwen, while PC1 minimal directive swaps remain weak.

The PC1-positive no-label failure should not be described as pure ceiling saturation. The role-conditioned assistant baseline is already high PC1, but the family mean moved substantially negative on PC1, so prompt wording and generic helpful-answer dynamics are likely part of the failure. Do not generalize this as bare-Qwen PC1 saturation until the 240-question bare baseline is measured.

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

For Paper 1.5 writing, start from `research/paper15_content_ledger.md` rather than reconstructing evidence from chat history, commits, or individual output reports. Treat it as the source ledger, not as draft prose.

As of 2026-06-16, `research/paper15_content_ledger.md` has been completed for methods-section drafting support. It now includes the missing design/procedure details Claude flagged for PC2 conditional validation, blinded rater studies, professional hierarchy validation, PC1 competing-theories vocabulary controls, PC3 rubric validation, PC1 accountability intervention prompts, muted-PC1 PC2 extremes, and the blind PC interpretation benchmark. It also records the current PC1 "rigor" wording, the PC1-PC2 diagonal observation, and the PC3 cost-bearer refinement. Use the ledger for methods prose, but do not treat it as new empirical evidence or as a paper draft.

## Next Experiments

1. Use `research/outputs/same_space_big_five_overlay/` as the evidence-bearing same-space Big Five visualization layer if Big Five overlays are needed; build blinded independent ratings only if independent psychometric-style validation is required.
2. Run an independent-rater PC2 disentanglement study over the strongest PC1-matched pairs, explicitly separating abstraction, maturity/integration, expertise, uncertainty exposure, and coherent action under uncertainty.
3. Use `research/outputs/no_label_elicitation_geometry_diagnostics/` before designing a second no-label packet: revise PC1-positive prompts against the assistant-baseline saturation/generic-helpful failure mode, separate self-cost from consequence-to-others pressure in PC3-positive prompts, and treat PC2-negative as mixed until prompt-level context is inspected.
4. Interpret the completed Run 2 outputs under `research/outputs/no_label_elicitation_run2/`, using the bare-Qwen centroid as the default-behavior baseline and treating the released assistant centroid as a role/persona reference point.
5. Finish evaluator-sensitivity comparison between Codex/GPT-5.5 and `gpt-4.1-mini` if API quota allows.
6. Distill SVD15 prompt-register components into concrete human-readable residual features and retest under the shared benchmark splits.
7. Use Paper 2 grant/H100 work for local centroid perturbation around Trickster, Actor, Therapist, and Spy.
8. Extend the activation-cloud geometry audit to a balanced role set before making strong claims about persona-specific cloud size, anisotropy, or orientation.
