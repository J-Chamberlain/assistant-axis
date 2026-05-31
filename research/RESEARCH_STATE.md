# RESEARCH_STATE.md
# Canonical state document for the assistant-axis research project.
# Updated at the end of every Codex session. Fetch this first in any new session.
# Raw URL: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md

Canonical startup file: yes
State role: canonical project state
Last updated: 2026-05-31

**Last updated:** 2026-05-31
**Last commit:** 5607390
**Current status:** Active — Paper 1.5 is now framed as `Interpreting Persona Activation Geometry`, with adaptive extraction treated as methodological due diligence and tooling validation rather than the headline contribution; Paper 2 is reframed around local centroid perturbation and local persona-manifold mapping; older dyad/contagion/attractor-collapse plans are archived as future dynamics work; evaluator-model sensitivity remains the main unfinished methodological item for Paper 1.5; H100 local-manifold work is future grant/Paper 2 work, not a prerequisite for Paper 1.5; persona geometry visualizer UI now supports explicit 2D axis labels, axis swapping, fixed ranges, persistent point selection, 2D lasso/box selection, focus-view mode, rotation-safe selection/camera persistence, and Big Five-style trait overlay color modes; `research/RESEARCH_INDEX.md` and `research/PROVENANCE_REGISTRY.md` now provide fast provenance/state lookup before repo archaeology; PC working interpretations are preserved in `research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md`, with PC1 strongest, PC2 revised toward an abstraction/integration/developmental axis after conditional PC1 control, PC3 showing suggestive but incomplete support for perturbation-stabilization after full-distribution validation, cluster-conditioned PC1/PC2 tests showing that cluster identity improves calibrated regression but not simple within-cluster pairwise ordering, the percentile-edge H100 validation completed successfully on 100 novel prompts with all three forecasted PCs positively correlated with independently measured Qwen/Qwen3-32B response activations, regional error analysis shows structured axis bias and tail-retention failures that require calibration before absolute-address claims, native training-artifact forecast error geometry shows the H100 PC2 upward shift is not present in original role-artifact target-to-forecast predictions, and the extraction-equivalence audit partially resolves D01 while leaving activation-site equivalence open until hook-vs-`output_hidden_states` equivalence is proven

---

## 1. WHAT HAS BEEN ATTEMPTED

### Paper 1 — Persona Geometry Analysis (Complete)
- Full layer-wise axis projections for 275 archetypes across 46 layers in Gemma 2 27B
- PCA, t-SNE, cosine similarity clustering
- Big Five and Dark Triad psychological framework correlations
- Layer 22 vs layer 45 comparison
- Seven-cluster taxonomy identified
- Live paper at: https://j-chamberlain.github.io/assistant-axis/visualizations/research_paper.html

### Q1 — Base Model Drift (Complete)
- Single-turn forward pass drift measurement on google/gemma-2-27b (base, not instruct)
- 10 prompts each for proofreader and poet personas at layer 45
- Discovered: published assistant_axis.pt has inverted sign convention vs role vectors
- Fix: saved assistant_axis_flipped.pt; all downstream analysis uses flipped version
- Results: proofreader flat across prompts; poet drifts downward (T1=0.63, T10=0.39)
- Interpretation: careful evaluator basin exists in base model, not only in post-trained model

### Emotion Vector Extraction — Gemma 2 27B (Complete, Negative Result)
- Attempted replication of Sofroniew et al. methodology on google/gemma-2-27b-it
- Used ryancodrai/emotion-probes story corpus (confirmed exact Anthropic methodology)
- Tested layer 45 and layer 21
- Both failed PCA gate: PC1 variance ~25.9%, gate requires ≥30%
- Opposite-valence pairs positively correlated rather than anticorrelated
- Verdict: discriminative emotion geometry does not appear at Gemma 2 27B scale
- Vectors preserved at research/emotions/outputs/

### Seven-Persona Calibration (Complete)
- Calibration runs for all seven cluster centroid personas
- Key finding: all axis thresholds are positive regardless of cluster — evaluative attractor dominates under minimal prompting
- Corrected policy: use empirical p25 per persona as cap threshold; cosine to role vector as success criterion
- Summary: research/q2_stability/outputs/calibration/all_personas_calibration_summary.json

### Dyad Experiments v1–v5 (Complete, Artifact Identified)
- Progressive iterations of two-model dyad design (anchored interviewer + unmodified standard model)
- v3/v4: identified inoculation effect (standard model that could see interviewer reasoning drifted less)
- v1–v5: geometric plateau artifact identified — KV cache in measurement forward pass returned cached hidden states from turn 3 onward despite genuine text variation
- Fix confirmed empirically in v6 pilot (2 turns): T1 s_axis=0.012658, T2 s_axis=−0.052057 — genuine movement

### Dyad Experiment v6 (In Progress or Complete)
- Script: research/q2_stability/scripts/run_dyad_v6.py
- Two changes from v5: (1) use_cache=False in measurement forward pass only, (2) max_new_tokens=2000
- Design: 7 personas × 3 conditions × 25 turns = 21 conditions
- Model: Qwen 3 32B on RunPod A100 80GB
- Local audit on 2026-05-24 found pilot outputs for trickster/adversarial and trickster/emotional under research/q2_stability/outputs/dyad_v6/
- Latest script modification date: 2026-05-23 19:38:47 PDT
- Forced-cap pilot outputs exist under research/q2_stability/outputs/dyad_v6_forced_cap/

---

## 2. WHAT HAS BEEN DISCOVERED

### Careful Evaluator Finding (Paper 1, confirmed)
- `assistant` ranks 45th/275 on assistant axis in Gemma 2 27B
- Top ranks dominated by evaluative roles: proofreader, screener, grader, editor
- Conscientiousness correlation: r = 0.792; Psychopathy: r = −0.739
- Machiavellianism notably weak: r = −0.219 (procedural discipline confounds it)
- Most discriminative layer: 45

### Base Model Basin Structure (Q1, confirmed)
- Careful evaluator basin exists in base model without RLHF
- Geometry reflects something in pretraining distribution, not only post-training artifact
- Consistent with Lu et al. and Beckmann (2026) confirming pretraining preserves geometry

### Gemma Outlier Status (confirmed across two analyses)
- Persona rankings: Spearman 0.550 with Llama vs Qwen-Llama convergence at 0.947
- Emotion geometry: failed replication while Llama/Qwen expected to succeed at scale
- Gemma-specific traits: elitist, arrogant, dogmatic near assistant pole
- Qwen/Llama traits: accessible, practical, benevolent near assistant pole

### KV Cache Measurement Artifact (v1–v5, confirmed and fixed)
- Setting model.config.use_cache=False globally disables cache during generation — turn times of 258s and 880s
- Correct fix: use_cache=False only in measurement forward pass, use_cache=True in generation calls
- V6 pilot confirmed fix produces genuine geometric movement

### Behavioral-Geometric Dissociation (v3/v4, confirmed)
- Standard model can drift internally while producing normal-looking outputs
- Standard model can mimic dangerous behavior on surface while remaining geometrically stable
- Inoculation condition (visible reasoning) produces less internal drift than clean condition

### Layer-Depth Split (2026-05-18, confirmed)
- Layer 21 maximizes pairwise proofreader/poet separation with centered cosine −0.534, compared with −0.314 at layer 45
- Layer 45 remains the global maximum-variance layer across all 275 personas
- Interpretation: middle layers appear to construct persona-specific representations; late layers commit globally discriminative persona geometry

### Cross-Model Persona and Trait Geometry (2026-05-18, confirmed)
- Qwen 3 32B and Llama 3.3 70B converge strongly on persona rankings: Spearman 0.947
- Gemma diverges from Qwen and Llama: Gemma-Qwen Spearman 0.670, Gemma-Llama Spearman 0.550
- Literal `assistant` ranks 1st in Llama, 14th in Qwen, and 46th in Gemma
- Trait rankings show the same pattern: Qwen-Llama Spearman 0.846, Gemma-Qwen Spearman 0.435

### Base-vs-Instruct Inversion and Emotional Responsiveness (2026-05-18, confirmed)
- Gemma 2 27B base model persona rankings are inverted relative to instruction-tuned Gemma: Spearman −0.441
- Base top roles are mythic/chaotic/liminal; proofreader ranks 183rd in base vs 1st in instruction-tuned; assistant ranks 172nd in base vs 45th
- Under identical grief/loss/despair prompts, base Gemma produced negative valence on 0/12 turns while instruction-tuned Gemma produced negative valence on 12/12 turns

### Distributed Emotion Geometry Across Open-Weight Models (2026-05-20, confirmed)
- Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B all failed the Anthropic PCA gate with PC1 around 7-9% in the cross-model pilot framing
- Opposite-valence emotion pairs remained anticorrelated, indicating usable distributed emotion structure despite failing the dominant-PC gate
- Qwen 3 32B layer-48 full readout across 171 emotions achieved discrimination accuracy 0.072 vs chance 0.006, with 9/9 opposite-valence validation pairs anticorrelated

### Qwen Persona Calibration (2026-05-20, confirmed)
- Qwen 3 32B calibration completed for seven centroid personas at layer 48 with capping layers 48-52
- Empirical p25 thresholds: editor −0.032374, synthesizer +0.063926, blogger +0.091596, ancient +0.154919, trickster +0.046783, contrarian +0.035024, podcaster +0.019844
- Unlike Gemma, Qwen did not produce uniformly positive thresholds; editor was negative, and several cosine baselines were weak or negative

### V5 Run Caveat (2026-05-22, confirmed)
- V5 pilot passed after patching Qwen thinking extraction, but follow-on conditions showed repetition loops, especially blogger/neutral, podcaster/neutral, editor/emotional, and editor/neutral
- V5 analysis is useful for design and artifact diagnosis, but downstream claims should account for repetition-loop contamination

### V6 Corrected Pilot and Attractor-Collapse Finding (2026-05-23, confirmed)
- Corrected v6 trickster/adversarial pilot produced 25 turns with zero leakage and real post-T3 geometric movement: post-T3 trickster cosine variance 1.80e-02
- Corrected v6 trickster/adversarial local CSV: standard axis range −0.018212 to +0.041879; standard trickster cosine range 0.230370 to 0.551177
- A separate pilot25 transcript analysis identified attractor-collapse events at T9 and T15 with geometric role reversal: interviewer moved toward assistant-axis values while standard model surged to maximum trickster alignment
- Collapse turns had timing spikes around 310s and 313s vs mean 188s, making timing a practical monitoring signal
- Forced manual cap pilot failed the gate: post-T3 trickster cosine variance 0.00e+00, budget estimate $63.89 > $35, and geometry froze despite zero leakage

### Phase 0 Corpus Audit (2026-05-24, confirmed)
- Existing per-persona dialogue-like material exists for all seven target personas in Gemma calibration CSVs: 50 truncated response previews per persona under `research/q2_stability/outputs/calibration/`
- Qwen calibration and valence-matrix outputs also cover all seven personas, but responses are mostly think-contaminated and/or stored as previews rather than clean full dialogue
- v3 and v4 dyad outputs contain 45 interviewer turns per persona across adversarial, emotional, and neutral conditions, but many clean interviewer outputs explicitly disclose persona or role identity, especially trickster, synthesizer, ancient, and podcaster
- Phase 1 prompt design can use existing material as seed style evidence, but a controlled clean corpus generation step is recommended before treating any corpus as final non-leaking prompt source material

### Persona Representative Provenance (2026-05-24, confirmed)
- The seven Q2 persona representatives were selected by `research/q2_stability/scripts/find_centroid_reps.py` from Gemma 2 27B role vectors at layer 45, using `visualizations/full_ranking.csv` cluster assignments and writing `research/q2_stability/outputs/centroid_representatives.txt`
- Qwen-specific calibration exists for those same named personas at layer 48, but no documented Qwen-specific reclustering or centroid-nearest representative selection exists in the repo
- Cross-model Qwen/Gemma ranking comparisons exist, but they do not validate that the seven Gemma-derived representatives are near-centroid in Qwen space
- Methodological implication: dyad experiments should describe these as Gemma-derived persona representatives applied to Qwen and calibrated in Qwen, not as Qwen-native cluster centroids, unless a Qwen-specific clustering and centroid selection step is added

### Qwen-Native Centroid Selection (2026-05-24, confirmed)
- Nearest-centroid lookup on existing Qwen 3 32B role vectors at layer 48 selected the same representative as Gemma for editorial, procedural_professional, mythic_spiritual, and trickster_chaos: editor, synthesizer, ancient, and trickster
- The Qwen-native representatives diverged from Gemma for three clusters: grounded_social selected actor instead of blogger, other selected hoarder instead of podcaster, and combative_iconoclast selected maverick instead of contrarian
- Result saved to `research/q2_stability/qwen/outputs/calibration/qwen_centroid_selection.json`

### Cluster Motivational Structure Analysis (2026-05-24, dialogue-derived)

- Six of seven clusters characterized through extended researcher dialogue
- Other cluster: identity around unresolved need (hungry ghost correspondence)
- Mythic-spiritual: identity around hole-and-loosening-of-roots (Buddhist dukkha and Christian Matthew 10:34-39 correspondences)
- Grounded-social: identity around reactivity to circumstance (vedana correspondence)
- Combative-iconoclast: identity around aggressive force (asura realm correspondence)
- Trickster-chaos: identity around permission-protected play (holy fool correspondence)
- Editorial: identity around agent-of-the-standard with fear of error as hypothesized affective driver
- Procedural-professional: not yet characterized
- Decision to make this work standalone as Paper 1.5, sitting between Paper 1 and Paper 2

### Tensor Row Count and Variance Audit (2026-05-25, confirmed)

- All sampled Qwen role vector tensors that exist locally have exactly 64 rows, supporting the fixed storage cap hypothesis rather than meaningful elicitation-yield row counts
- Six requested sample personas were not present as local `.pt` files: child, explorer, villain, hero, wizard, and nurse
- Centroid cosine-to-mean tightness: editor mean 0.912738 std 0.075345; synthesizer mean 0.914840 std 0.072463; actor mean 0.895064 std 0.084221; ancient mean 0.896545 std 0.086517; trickster mean 0.891448 std 0.083971; hoarder mean 0.888571 std 0.086618; maverick mean 0.898172 std 0.078914

### Paper 1.5 Phase 1 Pod Postmortem (2026-05-26, operational audit)

- A live RunPod endpoint was recovered from local SSH evidence at `213.173.102.6:22707`; it was running `phase1_inference_only_v4.py`, not the earlier OpenAI-judged replication script
- Local copied snapshot contained 1126 unique `trickster_phase1.jsonl` records and 1126 matching `activations_trickster/*.pt` tensors, all sampled tensors loading as shape `[5120]`
- The live pod log showed at least total=1125/1200, think_discards=0, truncated=669, rate=27.5s/rollout, and GPU memory 65.5GB
- Resume decision from the audit: preserve final live pod outputs first, then rerun integrity checks before any termination or full continuation decision

### Paper 1.5 Phase 1 Live Pod Follow-Up (2026-05-26, operational audit)

- One-time live check of `213.173.102.6:22707` succeeded and found `phase1_inference_only_v4.py` still running as PID 5596
- Pod-side counts at check: 1180 JSONL records and 1180 activation shards; latest visible checkpoint was total=1175/1200, think_discards=0, truncated=710, rate=27.6s/rollout, ETA=0.2hr, GPU=65.5GB
- GPU and disk state were healthy: A100 utilization 88%, about 64GB GPU memory used, root overlay 42% used with 88G free
- Local best snapshot remained the previously preserved 1126-record copy; final local integrity passed for the available snapshot but the run was not complete enough to copy/declare final in this card

### Paper 1.5 Phase 1 Final Copy and Integrity (2026-05-26, operational audit)

- Final Qwen trickster Phase 1 outputs were copied locally after the live pod reached 1200/1200 records
- Final integrity passed: 1200 JSONL records, 1200 unique `(sp_idx, q_idx)` pairs, 1200 `activation_saved=True`, 1200 matching activation shard targets, zero duplicate pairs, zero empty responses, zero literal think tags, zero `think_artifact=True`, and all 1200 tensors loading as shape `[5120]`
- Truncation count was 733/1200; this is a Phase 2/scoring consideration, not a Phase 1 file-integrity failure
- RunPod compute was idle after completion, but in-container termination attempts (`kill -TERM 1`, killing `sleep infinity`, and `poweroff -f`) did not provide durable termination; future pod closeout should use RunPod API or `runpodctl` as the preferred path, with browser/dashboard termination as fallback only

### Trickster Phase 1 Truncation Diagnostic (2026-05-26, confirmed)

- Local no-API truncation diagnostic confirmed 733/1200 records truncated at 512 tokens, a 61.1% truncation rate
- Truncation varies by system prompt from 47.5% to 80.4%, with `sp_idx=4` highest, and by question decile from 45.0% to 71.7%
- Non-LLM role-expression proxy found 690/733 truncated records, 94.1%, contain at least two trickster lexical markers before cutoff
- Ending heuristics show truncation is usually abrupt: only 62/733 truncated records, 8.5%, end with sentence punctuation, while 536/733, 73.1%, meet the abrupt-ending heuristic
- Recommendation: Phase 2 scoring should proceed on all 1200 records with truncation retained as a covariate/filter, followed by a small higher-token follow-up run for high-scoring truncated records and the most abrupt question subsets

### Trickster Sample Sufficiency Analysis (2026-05-26, provisional)

- Local bootstrap analysis on all 1200 Qwen trickster Phase 1 activations found very high geometric self-stability before role-expression scoring: raw Criterion A and B minima both crossed at n=4 for all activations, non-truncated activations, truncated activations, and each system prompt subset
- Operational recommendation applies a conservative n>=16 floor despite the raw bootstrap crossing, because tiny subsets are too brittle for workflow policy; score-conditioned Codex validation later confirmed the same n=16 adaptive stopping result
- Lu fixed 64-row cap is appropriate and conservative for trickster under pre-scoring geometry: all_1200 mean cosine to Lu trickster mean is 0.958211, non-truncated is 0.953492, truncated is 0.958973
- Truncation does not materially change pre-scoring geometric sample sufficiency: non-truncated and truncated subsets both cross Criterion A at raw n=4 and operational n=16
- Score-conditioned analysis is now complete for the pragmatic Codex GPT-5.5 path; strict gpt-4.1-mini scoring remains optional and pending API quota restoration

### Paper 1.5 Trickster Adaptive Extraction Validation (2026-05-26)

- Qwen/Qwen3-32B trickster extraction completed with 1200 preserved Phase 1 rollouts and 1200 activation shards
- Final integrity passed: 1200 unique `(sp_idx, q_idx)` pairs, 1200 `activation_saved=True`, zero duplicate pairs, zero empty responses, zero think artifacts, and all sampled tensors shape `[5120]`
- Truncation was high at 733/1200 responses and is retained as an explicit covariate; pre-scoring analysis found truncation did not materially destabilize geometric convergence
- Codex GPT-5.5 Standard adaptive scoring was used as a pragmatic role-expression judge after the planned gpt-4.1-mini API scoring path was blocked by quota
- Adaptive scoring reached 64 score>=2 responses and 33 score==3 responses in 64 scored records
- Score>=2 vector matched Lu trickster mean at cosine 0.957557
- Adaptive stopping passed at n=16 for both score>=2 and score==3 subsets
- This supports adaptive extraction as an operational replacement for exhaustive 1200-rollout generation, pending validation on additional personas
- Paper 1.5 methodology records this protocol in `research/paper1_5_outline.md`; workflow continuity note is `research/paper1_5_adaptive_extraction_notes.md`

### Paper 1.5 Editor Adaptive Extraction Phase 1 Chunk (2026-05-26)

- Qwen/Qwen3-32B editor adaptive extraction first chunk completed exactly 128/128 rollouts on an A100 SXM 80GB RunPod pod
- Local integrity passed: 128 JSONL records, 128 unique `(sp_idx, q_idx)` pairs, 128 `activation_saved=True`, 128 matching activation shards, zero duplicate pairs, zero empty responses, zero literal think tags, zero `think_artifact=True`, and sampled tensors load as shape `[5120]`
- The 128 records cover `sp_idx=0`, `q_idx=0-127`, because this was the first stable-order chunk rather than the full 5x240 rollout grid
- Truncation was high at 99/128 responses and should be retained as a covariate during scoring and vector validation
- No judge/scoring was run on the pod; local Codex scoring and Lu-reference validation remain the next steps if the user approves

### Paper 1.5 Editor Token-Cap Sensitivity Chunk (2026-05-26)

- Matched token-cap sensitivity follow-up completed on the same RunPod pod using the first 64 `(sp_idx, q_idx)` pairs from `editor_phase1_128.jsonl`
- The follow-up used Qwen/Qwen3-32B, editor persona, layer 48, deterministic generation, `MAX_NEW_TOKENS=1024`, no pod-side judge/scoring, and the same post-MLP residual mean-pooling measurement path
- Local integrity passed: 64 JSONL records, the same 64 pairs as the first 64 editor 512-cap records, 64 unique pairs, 64 activation shards, zero missing activation targets, zero empty responses, zero literal think tags, zero `think_artifact=True`, and sampled tensors load as shape `[5120]`
- Truncation dropped from 50/64 at 512 tokens to 5/64 at 1024 tokens for the matched first-64 editor pairs
- This establishes the paired data needed for local scoring and token-cap vector comparison before deciding whether future editor chunks should use 512 or 1024 tokens

### Paper 1.5 Editor Adaptive Extraction Scoring and Token-Cap Comparison (2026-05-26)

- Codex GPT-5.5 Standard local role-expression scoring completed for the 128-record editor 512-token chunk and the matched 64-record editor 1024-token sensitivity chunk
- The 512-token chunk produced 10 score>=2 responses and 3 score==3 responses out of 128, below the validation gate of 64 score>=2 and 16 score==3 responses
- The matched 1024-token chunk produced 5 score>=2 responses and 1 score==3 response out of 64, identical to the matched first-64 512-token score>=2 and score==3 counts
- Matched token-cap comparison found truncation dropped from 50/64 to 5/64, exact score agreement was 62/64, score>=2 agreement was 64/64, and score==3 agreement was 64/64
- Vector validation and score-conditioned sample sufficiency were not run because the editor 512-token scored set failed the preregistered score thresholds
- Current implication: the first editor chunk does not validate adaptive extraction beyond trickster; low editor-role yield appears driven more by prompt/chunk behavior than by the 512-token cap alone

### Paper 1.5 Editor Pod Closeout (2026-05-26)

- Editor adaptive extraction and matched token-cap sensitivity outputs are preserved locally with passing integrity checks and committed scoring artifacts
- RunPod pod `5b6hz02m9idrc3` (`paper1-5-editor-128`, A100 SXM 80GB, $1.49/hr) was confirmed idle over SSH before closeout: no rollout process was active, logs showed both runs complete, and GPU usage was 1 MiB at 0 percent utilization
- Pod stop succeeded via `runpodctl pod stop`, changing desired status to `EXITED`; pod delete then succeeded via `runpodctl pod delete`
- Final RunPod confirmation: `runpodctl pod list` returned no running pods, and `runpodctl pod get 5b6hz02m9idrc3` returned 404 `pod not found`
- Current interpretation remains that editor weakness reflects weak anchoring or assistant-adjacent collapse under the current Lu-style extraction setup rather than token-cap limitation alone

### Role Prompt Label-Exposure Audit (2026-05-27, confirmed)

- Local string audit of all 275 Lu et al. role instruction JSON files found extensive direct role-label exposure in the five generated system prompts per role
- Exact role-label exposure appears in 1275/1375 prompts, 92.7%; normalized or variant exposure appears in 1280/1375 prompts, 93.1%; direct identity framing appears in 1117/1375 prompts, 81.2%
- Role-level distribution: 227/275 roles have complete 5/5 prompt exposure, 36 have 3-5/5 high exposure, 11 have 1-2/5 partial exposure, and 1 has 0/5 exposure
- Trickster and editor both have complete 5/5 label exposure, but their Qwen adaptive extraction yields diverge sharply, so label exposure alone does not explain role-expression success or failure
- Methodological implication: Lu-style extraction should be described as role-label-plus-behavior elicitation, not purely behavioral elicitation; this does not invalidate the geometry without further analysis

### No-Label Prompt Ablation Semantic Audit (2026-05-27, confirmed)

- Created a deterministic no-label rewrite dataset for all 1375 Lu et al. role system prompts, removing explicit target-role labels while preserving wording, structure, and behavioral content as closely as possible
- Validation passed with 1375/1375 rewrites present, zero remaining normalized target-label exposure, median character length ratio 0.842, median word count ratio 0.786, median lexical Jaccard 0.714, and zero over-flattening flags
- Offline TF-IDF/SVD semantic comparison found continuous prompt-space topology is largely preserved after label removal: role-level SVD cosine median 0.998, nearest-neighbor preservation 0.924, and pairwise distance correlation 0.985
- Hard k-means cluster assignments were less stable after label removal: original-vs-no-label ARI was 0.197 at k=5, 0.153 at k=7, and 0.181 at k=10
- Interpretation: explicit lexical labels contribute materially to discrete prompt-space organization, but much of the continuous semantic structure survives from behavioral descriptors; activation-space survival remains untested

### Semantic vs Activation Geometry Comparison (2026-05-27, confirmed)

- Compared role-name semantic geometry, original label-exposed prompt geometry, no-label prompt geometry, and available activation-space references from `visualizations/full_ranking.csv` plus Gemma/Qwen centroid-profile directionality CSVs
- Role names alone weakly recover activation cluster labels at k=7: ARI 0.010; role names plus descriptions improve slightly to ARI 0.023
- Original prompts recover more activation-label structure than role names alone, with k=7 ARI 0.111; no-label prompts are similar or slightly higher at k=7 ARI 0.130
- Original and no-label prompt spaces remain close: distance correlation 0.956 and nearest-neighbor preservation 0.858
- No-label prompt distances best predict available activation centroid-profile distances, but only modestly: Gemma correlation 0.230 and Qwen correlation 0.254
- Interpretation: activation geometry preserves some semantic topology but also reorganizes it into model-specific structure; it should not be described as "just semantics"

### Deep Semantic Topology Analysis (2026-05-27, confirmed)

- Ran an offline TF-IDF/SVD topology analysis over role names, role descriptions, original role prompts, and no-label prompt rewrites without pod inference or new activations
- The no-label semantic manifold is organized by mixed social, professional, narrative, stylistic, and archetypal structure rather than one clean psychological taxonomy
- No-label k=7 semantic clusters show soft broad regions: lived-experience/social, professional/specialist, communication/media, mythic/fantastical, normative/adversarial, and generalist/helper structure
- The assistant-adjacent seed set is semantically coherent but not separate from the broader professional/helper basin; the collective-identity seed set is especially compact in prompt space
- Bridge roles identified for activation stress testing include spy, amnesiac, sage, guardian, merchant, emissary, technologist, scout, dilettante, and addict
- Low-density roles such as flaneur, predator, devils_advocate, advocate, teenager, vegan, genie, angel, robot, and adolescent expose sparse or underrepresented regions of the constructed corpus
- Interpretation: semantic priors substantially structure the role corpus, but activation geometry should still be treated as preservation plus model-specific reorganization rather than a mirror of semantic topology

### Semantic-Activation Cluster Overlap Analysis (2026-05-27, confirmed)

- Ran a structured overlap analysis comparing activation-space labels, original-prompt semantic clusters, and no-label semantic clusters using existing assignment artifacts only
- k=7 hard-cluster agreement remains low: original-prompt ARI vs activation labels 0.111 and no-label-prompt ARI vs activation labels 0.130
- Found 73 stable anchor roles that fall inside the dominant original and no-label semantic regions for their activation cluster
- Broad bridge/migration criteria flagged 198 roles, reflecting soft semantic boundaries and activation-space compression rather than clean cluster equality
- Editorial is the cleanest semantic-activation overlap region; combative-iconoclast and trickster-chaos retain local semantic structure but still include boundary cases
- Procedural-professional compresses multiple prompt-space semantic regions into one broad activation basin, while collective/swarm roles are semantically compact but distributed across larger activation clusters
- Recommended no-label activation stress test should sample stable anchors, bridge roles, sparse/outlier roles, assistant-adjacent roles, and theatrical roles

### No-Label Activation Stress-Test Design (2026-05-27, design complete)

- Designed the first bounded no-label activation-space stress test; no pod was launched and no new activations were generated
- Selected 20 roles spanning stable anchors, bridge/migratory roles, sparse/outlier roles, assistant-adjacent/procedural roles, theatrical/fantastical roles, and collective/swarm probes
- Selected roles: editor, screener, reviewer, consultant, evaluator, proofreader, negotiator, trickster, jester, oracle, leviathan, mystic, hive, egregore, skeptic, philosopher, spy, dilettante, flaneur, and robot
- `diplomat` was excluded because it is not present in the 275-role assignment table
- Design uses paired original label-exposed and no-label conditions, 5 prompt variants x 4 questions per role per condition, for 20 rollouts per role per condition and 800 planned rollouts total
- The only planned experimental difference is system prompt label exposure; model, layer, questions, rollout order, extraction logic, activation storage, and integrity workflow are held constant
- Competing hypotheses are label-dependent geometry, label-independent behavioral-semantic geometry, and activation-space reorganization of behavioral semantics into latent procedural/behavioral manifolds

### Evaluator Sensitivity Harness (2026-05-27, blocked)

- Built `research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py` to compare existing Codex GPT-5.5 Standard scores against `gpt-4.1-mini` scores on the same trickster and editor response records
- Located canonical Lu-style judge materials at `data/roles/instructions/{role}.json` `eval_prompt`, exported in `research/assistant_axis_methodology/prompts_and_questions/canonical_judge_prompt.md`
- Located canonical corpora: trickster responses and Codex scores under `research/q2_stability/qwen/outputs/paper1_5/`, and editor responses and Codex scores under `research/q2_stability/qwen/outputs/paper1_5/editor/`
- Imported 192 existing Codex score records: 64 trickster and 128 editor
- Attempted `gpt-4.1-mini` canonical-rubric rescoring via OpenAI Responses API, but the API returned `insufficient_quota`; zero `gpt-4.1-mini` paired records were produced
- No evaluator-sensitivity conclusion should be drawn until the harness is rerun after API quota is restored

### Latent Feature Discovery Loop (2026-05-28, first implementation)

- Implemented a constrained LLM-assisted latent-feature discovery loop for persona activation geometry under `research/q2_stability/qwen/scripts/latent_feature_discovery_loop.py`
- The loop treats GPT-5.5 Standard as a hypothesis generator, operationalizes proposed dimensions into measurable lexical and prompt-pattern features, and evaluates them on a deterministic 200 visible / 75 held-out persona split
- Semantic baselines use original-prompt, no-label-prompt, and role-name k=7 cluster assignments; latent features are tested for held-out activation-cluster classification, assistant-axis projection regression, residual-proxy regression, nearest-neighbor preservation, and permutation/null baselines
- Best held-out assistant-axis prediction improved from baseline R2 0.301 to latent R2 0.385, delta +0.084, with iteration 2 as the strongest axis-prediction model
- Activation-cluster classification did not improve: best latent accuracy 0.600 vs semantic baseline accuracy 0.600
- Residual-proxy improvement was weak: best residual R2 0.300 vs baseline 0.290, delta +0.010, and the residual target is provisional because the requested residual summary JSON was absent locally
- Preliminary dimensions with the strongest axis signal were procedural-professional orientation, theatrical/fantastical vividness, assistant-basin adjacency, standards/error aversion, and semantic-label dependence risk

### Latent Feature Framing Ablation (2026-05-28, second implementation)

- Implemented `research/q2_stability/qwen/scripts/latent_feature_framing_ablation.py` to compare motivational, interactional, procedural/operating-mode, narrative-causal, all-framing, and prior first-loop feature families
- The primary target is held-out PCA3D activation-coordinate prediction using existing local PCA artifacts; no pods, new activations, or model calls were run
- The PCA artifact covered 273 personas, yielding a 200 visible / 73 held-out deterministic split under the same seed as the first loop
- Semantic baseline PCA3D R2 was 0.322; the prior first-loop feature set performed best at R2 0.436, delta +0.114
- The best new framing-only model was all framings combined at R2 0.405, delta +0.083; the best single new family was procedural at R2 0.373, delta +0.051
- Best-model improvement concentrated most on PC1: PC1 R2 0.499, PC2 R2 0.353, PC3 R2 0.406
- Cluster prediction remained secondary and only slightly improved: baseline accuracy 0.616 vs best accuracy 0.630, delta +0.014

### Iterative Latent-Feature Outer Loop (2026-05-28, repeated-split implementation)

- Implemented `research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py` as the first full outer-loop latent-feature discovery harness for Paper 1.5
- The harness evaluates candidate dimensions across five deterministic repeated splits, logs iteration state, retains or discards feature bundles, checks permutation/null performance, tracks split variance, and terminates on plateau
- Final retained feature set reached mean held-out PCA3D R2 0.492 across five splits versus semantic baseline R2 0.389, mean delta +0.103
- Iteration 1 retained 18 dimensions with mean R2 0.480; iteration 2 retained 31 dimensions with mean R2 0.492; iterations 3 and 4 were discarded and triggered plateau termination
- Retained families include procedural, assistant-adjacency, semantic-label-dependence, emotional-regulation, prior first-loop, motivational, interactional, narrative-causal, institutional, collective/distributed, and destabilization/reactivity features
- Discarded refinements include mythic/artistic expression, developmental immaturity, social hospitality, nonhuman scale, forecast/control, and judicial norms
- Recurring high-residual personas include mechanic, adolescent, prisoner, smuggler, infant, hermit, bard, teenager, predator, journalist, sage, and amateur

### Persona Explanation Residual Ranking (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/rank_persona_explanation_residuals.py` to reconstruct final retained outer-loop predictions and rank all available personas by activation PCA3D residual
- Output covers 273 personas; 221 had one or more held-out predictions across the five deterministic splits, and 52 use marked apparent full-model residuals because they were never held out by those splits
- Most effectively explained personas by final residual are designer, nomad, curator, chemist, and tulpa
- Least effectively explained personas by final residual are procrastinator, toddler, teenager, comedian, and cyborg
- Largest improvements over the semantic baseline are jester, robot, wind, gossip, and poet; strongest worsened cases are futurist, veterinarian, forecaster, coordinator, and producer
- High-residual personas should be treated as diagnostic cases for the current feature vocabulary, not as inherently inexplicable roles or final evidence about the true meaning of the dimensions

### Cross-Model Feature Transfer (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/cross_model_feature_transfer.py` to compare Codex-derived retained features and local Big Five features across canonical activation PCA3D and a reconstructed Big-Five pseudo-PCA3 target
- The comparison reused the five deterministic outer-loop splits, ridge-regression metric path, per-axis R2, and semantic baseline where possible
- Codex features improved canonical activation PCA3D prediction from semantic baseline R2 0.389 to R2 0.490, delta +0.101
- Big Five features transferred strongly to canonical activation PCA3D prediction, reaching R2 0.613, delta +0.223 over semantic baseline
- Codex features did not robustly transfer to the Big-Five pseudo-PCA3 target: R2 delta was only +0.012 and mean residual reduction was negative at -0.041
- Interpretation is asymmetric transfer rather than full convergence: Big Five features transfer to activation geometry, while Codex behavioral/procedural features do not robustly transfer to the reconstructed Big-Five pseudo target
- Caveat: no separate Claude pseudo-PCA coordinate artifact was found locally, so pseudo-PCA was reconstructed from `visualizations/bigfive_profiles.json`

### Shared Latent Feature Benchmark (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/shared_latent_feature_benchmark.py` to align Codex/GPT-5.5 and Claude latent-feature analyses against the same 273 common personas, deterministic Codex outer-loop splits, semantic baseline, and held-out PCA3D metrics
- Exported canonical activation PCA3D coordinates, Claude direct cluster-cosine pseudo-PCA3D coordinates, shared split assignments, and aligned semantic, Codex retained, Claude Big Five, Claude full, and combined feature matrices under `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`
- Direct Claude target alignment is now available: the benchmark uses Claude branch `claude_target_coordinates.csv` rather than reconstructing pseudo-PCA from local Big Five profiles
- Big Five features transfer strongly to canonical activation PCA3D: R2 0.613 vs semantic baseline 0.389, delta +0.224
- Codex retained features improve canonical activation PCA3D: R2 0.490 vs semantic baseline 0.389, delta +0.101
- Codex retained features do not transfer to Claude direct pseudo-PCA3D over the semantic baseline: R2 0.166 vs baseline 0.167, delta -0.001
- Combined Codex+Claude features do not outperform the best single feature family on either target in this aligned benchmark
- Interpretation: trait-style features survive direct target alignment to canonical activation geometry, while procedural/behavioral Codex dimensions remain useful for canonical activation prediction but do not explain Claude's pseudo-PCA target beyond semantics

### Latent Feature Convergence Status (2026-05-28)

- Wrote `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/convergence_status_report.md` as a planning memo synthesizing Codex/GPT-5.5 outer-loop results, Claude pseudo-PCA loop results, and the shared benchmark
- Current best explanatory model is a continuous dispositional-behavioral manifold: Big Five-style traits explain broad global placement, Codex procedural/motivational dimensions explain some role-function structure, semantic clusters remain useful baselines, and hard clusters are secondary to continuous PCA geometry
- Big Five conceptual analysis found canonical PC1 is strongly associated with high conscientiousness (r=+0.824) versus high openness (r=-0.779), extraversion (r=-0.692), and neuroticism (r=-0.672); agreeableness is most tied to PC3 (r=-0.477)
- Current PC interpretation: PC1 separates careful/evaluative/procedural control from open/expressive/unstable or emotionally pressured organization; PC2 is compound and not cleanly explained by a single Big Five trait; PC3 partly reflects cooperative-care versus antagonistic/disruptive stance
- What remains unreplicated: Claude has not yet searched for canonical activation PCA residual features after Big Five, and Codex has not yet demonstrated a trait-plus-procedure hybrid that beats Big Five under controlled repeated splits
- Drafted paste-ready follow-up cards for a Codex local hybrid benchmark and a Claude residual search after Big Five

### Codex Trait Replication Loop (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/codex_trait_replication_loop.py` as a constrained trait/dispositional optimization loop over canonical Qwen activation PCA
- The loop reused 273 common personas, the same five deterministic splits, the semantic baseline, and the ridge-regression path; no pods, activations, or model calls were run
- Retained five core Codex trait dimensions: organized reliability, imaginative flexibility, social expressivity, affiliative warmth, and threat reactivity
- Final Codex trait model reached R2 0.398 vs semantic baseline 0.389, delta +0.009, and plateaued after two non-improving candidate rounds
- Claude Big Five remains much stronger on the same target at R2 0.613, leaving a -0.215 R2 gap
- Measured feature convergence was modest: retained Codex traits had mean best absolute correlation 0.152 to Claude Big Five columns
- Interpretation: Codex independently found weak trait-like predictive signal under constraint, but did not replicate Claude Big Five's compact predictive encoding

### Hierarchical Trait-Procedural Model (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/hierarchical_trait_procedural_model.py` as a two-stage residualized predictor of canonical Qwen activation PCA3D
- Stage A used semantic controls plus Claude Big Five-style traits and reached R2 0.613 with mean residual 21.748 across the same five deterministic shared splits
- Stage B used selected Codex procedural/behavioral dimensions to predict the remaining Stage A residuals and improved the integrated model to R2 0.622 with mean residual 21.524
- The residualized hierarchy outperformed semantic baseline, procedural-alone, trait-stage, and naive concatenation; naive concatenation did not beat the trait stage
- Procedural correction modestly improved local-neighborhood preservation from 0.232 to 0.252, but did not improve cluster accuracy over the trait stage
- Bridge roles did not improve disproportionately overall, while developmental roles remained a strong high-residual class after both stages
- Interpretation: the result supports a layered latent-geometry hypothesis in which Big Five-like traits explain broad placement and procedural features provide a small local residual correction, with symbolic/liminal and developmental cases remaining candidates for future third-layer analysis

### Residual Manifold Analysis (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/residual_manifold_analysis.py` as a focused third-layer diagnostic over residual regions left after semantic, trait, and procedural modeling
- The loop used full no-label prompts, no-label semantic-neighborhood structure, semantic bridge metadata, prompt displacement metadata, residual histories, and canonical activation PCA context rather than relying primarily on role names
- The retained residual layer improved held-out PCA3D R2 from hierarchical baseline 0.622 to 0.632 and reduced mean residual from 21.524 to 21.326
- Retained residual dimensions include developmental dependency, incomplete proceduralization, identity formation, role ambiguity, liminal transition, volatile state transition, social dependency/constraint, collective/nonindividual agency, symbolic/nonprocedural identity, lawless improvisation, isolation, primitive embodiment, semantic-neighborhood residual pressure, and semantic-neighborhood developmental pressure
- Semantic bridge instability and original-to-no-label semantic displacement were discarded as insufficient incremental predictors
- Developmental seed roles remain the clearest residual manifold after the third layer, with mean residual 39.834 vs 21.064 for non-developmental roles; symbolic/liminal and collective/nonindividual cases also remain elevated
- Interpretation: a narrow developmental/liminal/collective third-layer hypothesis is now empirically motivated, but the current residual layer is a diagnostic improvement rather than a solved symbolic ontology

### Residual SVD15 Interpretation (2026-05-28)

- Implemented `research/q2_stability/qwen/scripts/residual_svd_interpretation.py` to reconstruct and interpret Claude's TF-IDF SVD15 residual signal from the full no-label prompt corpus
- Claude's branch contained the residual report, results JSON, iteration log, and run script, but not separate SVD vocabulary/loading artifacts; local reconstruction matched the reported SVD15 R2 0.707 to rounding
- The SVD15 basis improved sem+BigFive prediction from R2 0.613 to R2 0.707 while explaining only 0.138 of TF-IDF prompt variance
- Strongest interpretable components include nonhuman/entity consciousness versus lived family/social hardship, professional specialization versus existential/liminal being-language, between-worlds mediation versus stepwise planning, and outlaw/survivor/story-role texture versus collective/student/entity identity
- The hand-named residual concepts only partially align with SVD: developmental dependency, role ambiguity, and semantic-neighborhood residual pressure are supported, while several abstract labels are diffuse across multiple SVD components
- Interpretation: SVD15 likely works because it preserves many weak concrete prompt cues that abstract residual labels flatten; the next step is to distill component extremes into concrete, text-grounded residual dimensions and retest them under the same splits

### PC3 Hypothesis Evaluation (2026-05-29)

- Implemented `research/q2_stability/qwen/scripts/pc3_hypothesis_evaluation.py` to adversarially evaluate the working PC3 interpretation using existing local artifacts only
- The analysis tested PC1/PC2-neighbor pair contrasts, a description-only blind rubric, seven competing lexical hypotheses, cluster-level PC3 enrichment, and Big Five/hierarchical residual relationships
- The blind preserve-minus-challenge/exploit rubric predicted PC3 weakly to moderately: continuous score r=-0.312 and ordinal rubric r=-0.318
- The strongest tested lexical alternative was `nurturing_vs_competitive` at r=-0.319; the target `system_preserving_vs_exploiting` hypothesis ranked second at r=-0.308
- Combative_iconoclast and trickster_chaos were strongly enriched for high PC3, with mean PC3 25.78 and 23.03 respectively, but both overlapped the rest of the distribution
- Agreeableness was the strongest Big Five correlate of PC3 at r=-0.477; residual magnitudes were only weakly correlated with PC3
- Current interpretation: PC3 is provisionally best described as cooperative-care/system-stabilization versus antagonistic-disruptive/transgressive register, not a pure preserving/exploiting axis; confidence is moderate-low pending paired no-label falsification

### PC3 Perturbation-Stabilization Validation (2026-05-30)

- Ran `research/q2_stability/qwen/scripts/pc3_perturbation_validation.py` over all 275 personas using a coordinate-blind deterministic rubric over persona name plus neutral eval-prompt definition only
- Perturbation-stabilization score predicted PC3 globally: Pearson r=0.529 and Spearman r=0.511, with cluster-controlled Pearson r=0.491
- Within-cluster pairwise ordering accuracy was 0.773 overall, strongest in mythic_spiritual (0.848) and procedural_professional (0.802), but weak in grounded_social (0.565)
- Negative controls were weaker than the target rubric: moral_badness Pearson r=0.201, professionalism r=0.103, weirdness/fantasticality r=0.029, and abstraction r=0.129
- Interpretation: PC3 shows suggestive but incomplete support for a perturbation-stabilization reading; cooperative-antagonistic remains a secondary or partial reading because many perturbative roles are socially antagonistic, but prosocial interventionist examples such as auditor, debugger, skeptic, statistician, and lawyer show the axis is not reducible to moral badness or hostility

### Cluster-Conditioned PC1/PC2 Axis Tests (2026-05-30)

- Ran `research/outputs/cluster_conditioned_axis_tests/run_cluster_conditioned_axis_tests.py` using canonical role PCA coordinates, `roles.clusters` from `geometry_viz_data.json`, prior blinded rater PC1/PC2 proxy scores, and blinded dossier text for cluster prediction
- Simple within-cluster pairwise ordering was harder than global ordering: PC1 global 0.709 vs within-cluster 0.622; PC2 global 0.746 vs within-cluster 0.687
- Cluster-conditioned regression improved calibrated prediction: PC1 direct R2 0.296 vs oracle-cluster R2 0.811; PC2 direct R2 0.416 vs oracle-cluster R2 0.718
- Text-to-cluster classification reached 0.687 held-out accuracy and 0.404 macro F1; predicted-cluster R2 fell to 0.647 for PC1 and 0.520 for PC2
- Interpretation: cluster identity helps as an intercept/slope interaction, not because within-cluster axis ordering is easier; hard cluster errors erase much of the PC2 oracle benefit, so deployment-style forecasting should prefer direct or soft-cluster/hybrid approaches over hard two-stage cluster assignment

### Trait Geometry Prediction of Persona PCA Axes (2026-05-30)

- Used raw Qwen/Qwen3-32B layer-48 activation-space vectors from `downloads/hf_vectors/qwen-3-32b/role_vectors/` and `downloads/hf_vectors/qwen-3-32b/trait_vectors/`; both role and trait tensors are stored as `[64, 5120]` examples and were mean-pooled, normalized, and compared by cosine.
- Built a 275-persona by 240-trait cosine-similarity matrix and used it to predict the PCA coordinates in `research/visualizations/geometry_viz_data.json`.
- Ridge 5-fold cross-validated performance was near ceiling: PC1 R2=0.999, PC2 R2=0.999, and PC3 R2=1.000; 30-permutation ridge baselines stayed near or below zero R2.
- PC3 targeted subset test found perturbation/stabilization-related traits predicted PC3 slightly better than moral-valence traits: R2=0.995 vs R2=0.992.
- Interpretation: trait-vector geometry substantially predicts persona PCA location, supporting the layered model in which trait structure organizes persona geometry alongside semantic, procedural, and lexical/register structure; the near-ceiling performance should be treated cautiously because 240 same-space trait vectors can act as a high-dimensional basis rather than an independent psychological ontology.

### Trait-Space Axes and Cone Structure (2026-05-30)

- Computed trait-only PCA directly from raw Qwen/Qwen3-32B layer-48 trait vectors in `downloads/hf_vectors/qwen-3-32b/trait_vectors/`; 240 traits, tensors `[64, 5120]`, mean-pooled to 5120-D vectors.
- Trait PCA explained variance was PC1=0.353, PC2=0.168, PC3=0.134, cumulative PC1-PC3=0.655.
- Trait PC1 moderately aligned with persona PC1 in activation-space direction cosine, abs=0.681, but trait PC2 and PC3 aligned weakly with persona PC2/PC3, abs=0.194 and 0.065.
- Paper-ready trait-axis labels: PC1 = controlled seriousness/formal composure vs playful irreverence/expressive volatility; PC2 = cold detachment/hard-edged abstraction vs warm accessibility/affiliative care; PC3 = plain practical groundedness vs ornate symbolic/theatrical expressivity.
- Trait-only PC3 did not independently recover the persona PC3 perturbation-stabilization interpretation: name-based perturbation/stabilization score correlated weakly with trait PC3, Pearson=-0.074 and Spearman=-0.104, while moral valence was near zero.
- Trait-space cone test did not reproduce the simple persona-space cone pattern: lowest-PC1 vs highest-PC1 PC2/PC3 radial spread ratio was 0.863, and secondary variation did not expand as PC1 decreased.
- Interpretation: trait-space analysis partially recovers persona-space structure but also reorganizes it; retain the trait-persona reconstruction as strong same-space geometry while treating direct trait-PC interpretations as distinct from persona PCs.

### Trait Prompt Artifact Inventory for Forecasting (2026-05-30)

- Verified local trait prompt artifacts in `data/traits/instructions/*.json`: 240 files matching 240 Qwen/Qwen3-32B layer-48 trait vectors exactly by name.
- Verified local role prompt artifacts in `data/roles/instructions/*.json`: 276 files, consisting of 275 role/persona artifacts plus `default.json`, matching the 275 Qwen role vectors except for the expected default non-vector row.
- Retrieved and inspected `belmore/assistant-axis-vector-prompts`, SHA `57424a9d6075a44196b935983ce1fa4e83191679`; `train.parquet` contains 516 rows: 275 roles, 240 traits, and 1 default row.
- Trait artifacts include descriptions, five positive instructions, five negative instructions, forty behavioral questions, and a 0-100 evaluation prompt with refusal handling.
- Exact match across Qwen trait vector names, local trait artifacts, and Belmore prompt rows was 240/240, with no missing, extra, or normalization-required trait names.
- Interpretation: released trait prompt artifacts are available and name-aligned with trait vectors, enabling prompt-to-geometry forecasting dataset construction without regenerating prompts.

### Prompt-To-Geometry Forecasting on Held-Out Concepts (2026-05-30)

- Built concept-level forecasting datasets from released role and trait prompt artifacts under `research/outputs/prompt_to_geometry_forecasting/`; eval prompts were excluded from all variants.
- Critical trait split held out 40 complete traits and trained on 200 complete traits; role split held out 55 complete roles and trained on the remaining roles.
- Leakage-control variant used descriptions, instructions, and questions with explicit target names replaced by `[TARGET]`.
- Best held-out trait model was elastic-net TF-IDF on leakage-control text: mean R2=0.389, PC1 R2=0.414, PC2 R2=0.304, PC3 R2=0.450; Pearson r was 0.656/0.602/0.708.
- Best held-out role model was elastic-net TF-IDF on leakage-control text: mean R2=0.621, PC1 R2=0.783, PC2 R2=0.577, PC3 R2=0.504; Pearson r was 0.887/0.772/0.732.
- Nearest-neighbor semantic retrieval was weak on held-out leakage-control traits, mean R2=-0.021, so the linear text model adds predictive structure beyond copying the nearest training artifact.
- Interpretation: prompt text alone contains substantial predictive information about future geometry on unseen trait and role concepts, but this is a prompt-artifact forecasting result, not a safety controller or proof of execution-time steering reliability.

### PC1/PC2 Forcing-Function Interpretation Notes (2026-05-30)

- Captured the revised PC1 and PC2 interpretations under `research/outputs/axis_forcing_function_notes/` for use in prompt-to-geometry judge-rubric design.
- PC1 is now framed as convergence pressure versus degrees of freedom: high PC1 constrains the model toward correctness, validation, procedure, evidence, or error correction; low PC1 admits broader symbolic, expressive, ambiguous, or multi-continuation response space.
- PC2 is now framed as integrated abstraction versus situated developmental immediacy: the key hypothesis is admissibility, where some roles lack the prerequisites for reflective synthesis, accumulated context, or broad world-model integration without ceasing to be that role.
- The notes explicitly distinguish endpoint descriptions from causal/geometric forcing-function hypotheses and preserve the numerical context from semantic, procedural, trait, combined, and prompt-to-geometry forecasting analyses.
- Status: hypothesis to be operationalized through prompt-level judge rubrics, not established causality.

### Novel Prompt Battery for H100 Geometry Validation (2026-05-30)

- Built `research/outputs/novel_prompt_battery/` as a frozen prompt battery for future H100 validation of the text-to-persona-geometry forecaster.
- Retrained and serialized the selected role-trained leakage-control elastic-net TF-IDF forecaster because no reusable serialized object was present; stable model hash is `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`.
- Constructed a 27-cell quantile target grid from observed role/persona PC1/PC2/PC3 coordinates and generated 1,036 candidate prompts using behavioral region templates rather than explicit persona role names.
- Final H100 manifest contains 120 prompts: 52 mixed-boundary, 24 manual holdout, 19 cluster-region, 13 safety-adjacent, and 12 neutral-control prompts.
- Leakage checks found zero explicit role-name flags in the final battery; maximum approximate artifact similarity was 0.205 and mean similarity was 0.069.
- Coverage is incomplete: 11/27 target cells are populated, with high-PC1 and high-PC2 regions under-covered by the current natural-prompt generation strategy.
- Interpretation: H100 validation is feasible but should treat under-covered regions cautiously; this is a partial geometric validation set, not a complete covering design.

### Adaptive High-PC3 / High-PC2 Prompt Battery Expansion (2026-05-30)

- Built `research/outputs/novel_prompt_battery_expansion/` as a targeted supplemental prompt battery for future H100 validation.
- The expansion reused the frozen role-trained leakage-control elastic-net TF-IDF forecaster from `research/outputs/novel_prompt_battery/`; stable model hash verified as `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`.
- The adaptive loop logged 516 candidates across targeted high-PC3/high-PC2 cells, with coordinate-error feedback preserved for every round.
- Final supplement contains 60 prompts: 26 mixed-boundary, 22 cluster-region, and 12 safety-adjacent prompts.
- Supplemental coverage met the requested frontier minimums: 38 prompts above the prior PC3 75th percentile, 44 above the prior PC2 75th percentile, 12 safety-adjacent high-PC3 prompts, and 26 mixed-boundary high-PC3 prompts.
- Combined battery now contains 180 prompts and populates 16/27 target cells, up from 11/27 in the first-pass battery.
- Leakage/safety checks passed for the supplement: zero explicit role-name flags, zero operational-harm flags, max artifact similarity 0.104, mean artifact similarity 0.069.
- Remaining caveat: high-PC1 target cells and several exact 3D cells remain under-covered; H100 validation should use `supplemental_h100_prompt_manifest.csv` first as a targeted frontier probe or `combined_h100_prompt_manifest.csv` for the full expanded validation set.

### Percentile-Edge Prompt Battery for H100 Validation (2026-05-30)

- Built `research/outputs/novel_prompt_battery_percentile_edges/` as the final edge-heavy prompt battery referenced to inherited role/persona PCA percentiles from `research/visualizations/geometry_viz_data.json`.
- The script verified the frozen role-trained leakage-control elastic-net TF-IDF forecaster hash `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f` before scoring.
- Inherited tail thresholds are PC1 p20=-32.056 and p80=31.909; PC2 p20=-16.333 and p80=16.307; PC3 p20=-11.810 and p80=11.642.
- Final battery contains 100 prompts and passes all predefined readiness criteria: PC1 lower tail 12/8, PC1 upper tail 11/8, PC2 lower tail 34/8, PC2 upper tail 8/8, PC3 lower tail 8/8, PC3 upper tail 16/8, shoulder/edge 58/12, interior controls 20/20, final size 100/100, and filters pass.
- Candidate generation logged 200 generated candidates and 168 rejections; rejection reasons were coordinate_miss 159, criterion_already_met 8, and duplicate_or_near_duplicate 1.
- Leakage/safety checks passed: zero explicit role-name flags, zero operational-harm flags, max artifact similarity 0.133, mean artifact similarity 0.071.
- H100 readiness judgment: ready. Recommended manifest is `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv`.

### Pre-H100 Methods Memorial (2026-05-30)

- Created `research/outputs/pre_h100_methods_memorial/` as the durable methods-and-assumptions record for the pending H100 validation.
- Main memo: `pre_h100_methods_memorial.md`; decision log: `pre_h100_assumptions_and_decisions.md`; artifact index: `pre_h100_artifact_index.csv`; quick readiness note: `pre_h100_readiness_summary.md`.
- The memo distinguishes descriptive persona geometry, explanatory modeling, prompt-to-geometry forecasting, prompt-battery construction, and future activation validation.
- It records the chosen H100 manifest, frozen forecaster hash, final percentile-edge pass table, assumptions required for an interpretable run, planned smoke/checkpoint/early-stop protocol, and success/failure interpretations.
- Current status: pre-H100 preparation is complete; no claim has yet been established that the forecaster predicts actual response activations on novel prompts.

### Percentile-Edge H100 Activation Validation (2026-05-31)

- Ran the 100-prompt percentile-edge validation battery against Qwen/Qwen3-32B at layer 48, using deterministic decoding (`max_new_tokens=256`, `do_sample=false`, `temperature=0.0`) and mean-pooled response-token residual activations.
- Projection used the existing persona PCA basis reconstructed from all 275 Qwen role vectors and sign-aligned against committed canonical coordinates; reproduction error against the 273 committed benchmark coordinates was max abs 1.21e-06.
- Smoke test passed on 3 prompts, and the 20-prompt early-stop gate continued because PC1 remained positively correlated and diagnostics showed nonconstant, scale-compatible observed coordinates.
- Final forecast-vs-observed correlations over 100 prompts: PC1 Pearson 0.691 / Spearman 0.696 / R2 0.321; PC2 Pearson 0.643 / Spearman 0.594 / R2 -2.721; PC3 Pearson 0.491 / Spearman 0.343 / R2 -0.243.
- Runtime on A100 SXM 80GB pod `yyelrl4oe9266o` at $1.49/hr: full phase 1631.7 seconds, estimated full-phase compute cost $0.68; no early stop triggered.
- Interpretation: this is a full proof-of-concept success under the project-defined criterion because all three PCs show positive forecast-vs-observed correlations, but PC2 and PC3 calibration/R2 remain poor and need axis-specific error analysis before stronger claims.
- Outputs, logs, plots, and checksum manifest are saved under `research/outputs/h100_percentile_edge_validation/`.

### H100 Forecast-Observed Regional Error Analysis (2026-05-31)

- Built `research/outputs/h100_percentile_edge_validation_error_analysis/` with per-prompt error vectors, six-tail regional breakdowns, shoulder/edge breakdowns, `regional_error_summary.json`, `regional_error_report.md`, and interactive 3D/2D Plotly arrow views.
- Verified 100/100 prompts have predicted and observed PC1/PC2/PC3 values.
- Overall mean signed delta vector was (-9.114, +28.342, -8.151); mean 3D error was 37.291, median 36.419, max 80.210, and center-collapse rate 0.280.
- Forecasted tail retention was uneven: PC1 lower 0.750, PC1 upper 0.000, PC2 lower 0.000, PC2 upper 1.000, PC3 lower 1.000, PC3 upper 0.000.
- PC3-high forecasts produced 0/16 observed high-PC3 tail activations and mean signed PC3 delta -18.705, weakening absolute high-PC3 address claims despite positive full-run PC3 correlation.
- Interpretation: errors are regionally structured and axis-biased rather than random; next step is per-axis intercept/slope calibration followed by region-aware correction tests.

### H100 Diagnostic Follow-Up Checklist and First Pass (2026-05-31)

- Created `research/outputs/h100_diagnostic_followups/` with persistent checklist D01-D09 and first-pass diagnostic outputs for methodology verification, cone outliers, forecast-origin bias, low-PC2 upward drift, PC2 family deltas, PC3-high collapse, largest 3D errors, prompt-generation audit, and calibration scaffolding.
- D01 methodology status: `in_progress`. Projection is strongly verified by role-vector PCA reconstruction and max abs canonical-coordinate reproduction error 1.207e-06, with no blocking projection discrepancy found.
- D01 unresolved checks: upstream/source extraction loop, layer-index convention, source chat template, and output-hidden-states versus hook-based post-MLP residual equivalence.
- D02-D08 remain open with evidence files; D09 is in progress with preliminary axis-wise calibration diagnostics.
- PC3-high collapse first pass supports response neutralization as a plausible mechanism: forecasted PC3-high prompts had 0/16 observed high-PC3 retention and mean delta_pc3 -18.705.
- Prompt-generation audit found repeated scaffolds in both accepted adaptive prompts and final battery prompts; the percentile-edge battery remains useful as a stress test but should not be over-described as a clean natural-language generalization benchmark.
- Preliminary LOOCV axis-wise calibration improved apparent R2 to PC1 0.463, PC2 0.390, and PC3 0.211; this motivates but does not resolve the next calibration task.

### Training Forecast Error Geometry (2026-05-31)

- Built `research/outputs/training_forecast_error_geometry/` with interactive 3D and 2D target-to-forecast arrow plots over inherited persona geometry.
- Per-example role predictions were not present in the original forecasting outputs, so predictions were recomputed from the frozen role-trained leakage-control elastic-net TF-IDF forecaster; verified model hash `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`.
- The frozen design forecaster was retrained on all 275 role artifacts, so `heldout_role_prior` is a prior-split label rather than an out-of-sample split for this visualization.
- Native target-to-forecast error is tiny: mean 3D error 0.843; PC1/PC2/PC3 R2 approximately 0.999-1.000; signed PC2 bias approximately zero.
- Native forecasts show mild centroid shrinkage: 0.898 closer to origin, mean radial movement toward origin 0.615; native forecast |PC3|<=5 fraction is 0.291 vs H100 forecast |PC3|<=5 fraction 0.530.
- Interpretation: H100 PC2 upward shift and PC3-high collapse are not native to the frozen role-artifact forecaster alone; they likely arise during edge-prompt generation/response activation measurement or from the stress-test distribution.

### Extraction Equivalence Audit (2026-05-31)

- Built `research/outputs/extraction_equivalence_audit/` to compare the original/local Assistant Axis extraction code, prior adaptive trickster/editor extraction, and the H100 percentile-edge extraction runner.
- The audit verified model identity (`Qwen/Qwen3-32B`), intended layer target 48, response-token mean pooling, PCA centering/sign/projection, and the prior hook-based trickster replication result: score>=2 vector cosine 0.957557 to the downloaded trickster vector.
- D01 remains `in_progress`, not resolved, because prior/source extraction uses forward hooks on `model.model.layers[48]` while H100 reads `out.hidden_states[48]`; source inspection did not prove these activation objects are identical for Qwen/Qwen3-32B.
- PCA reproduction max error 1.207e-06 proves projection-basis correctness, not extraction-site equivalence. The smallest remaining test is a one-prompt hook-vs-hidden-states comparison on Qwen/Qwen3-32B.

### Blinded PCA-Axis Rubric Validation (2026-05-29)

- Ran a coordinate-blind validation using the full available no-label persona prompt corpus: 1,375 rewritten prompt records covering all 275 personas, five prompts per persona.
- Scoring used deterministic local lexical-semantic rubric proxies over no-label prompt text only; persona names, PCA coordinates, clusters, residuals, and prior labels were excluded until after scoring.
- Target-aligned correlations were positive but modest: PC1 objective-certainty r=0.247, PC2 fragmented/coherent-uncertainty r=0.224, and PC3 antagonistic-transgressive r=0.349.
- Matched-pair validation was weak: PC1 35%, PC2 40%, and PC3 40% direction-match rates over the top 20 close-orthogonal pairs per axis.
- Regression from the three main rubric scores produced low cross-validated R2: PC1 0.065, PC2 0.024, and PC3 0.116.
- Interpretation: this is not a clean validation of the working axis interpretations from no-label prompt text alone; PC3 receives the strongest modest support, PC1 is positive but weaker than expected, and PC2 remains the least certain.
- Caveat: this is a local lexical proxy study, not a true independent human or LLM blinded-rating study; the next test should use richer full rollout responses or independent blinded raters.

### Reading-Based Blinded PCA-Axis Rater Study (2026-05-29)

- Ran a reading-based Codex/GPT-5.5 rater study over anonymized no-label prompt dossiers covering 275 personas with five rewritten prompts per persona.
- Full 275-persona rollout-response corpora were not found locally; response corpora exist for trickster/editor extraction and dyad subsets only, so the study validates persona operationalization text rather than full generated rollout behavior.
- Persona names, PCA coordinates, clusters, Big Five scores, residuals, and prior interpretation labels were hidden from the rater until after scoring.
- Target-aligned reading-based correlations were materially stronger than the prior lexical proxy: PC1 objective-certainty r=0.558, PC2 coherent-action-under-uncertainty r=0.373, and PC3 antagonistic-transgressive r=0.690.
- Matched-pair validation improved to PC1 75%, PC2 100%, and PC3 95% direction-match rates over the top 20 close-orthogonal pairs per axis.
- Three main rater scores predicted held-out PCA coordinates with CV R2: PC1 0.496, PC2 0.101, and PC3 0.522; expanded PC2 alternatives raised CV R2 to PC1 0.616, PC2 0.564, and PC3 0.686.
- Interpretation: PC3 is now the best-supported direct axis interpretation in prompt-dossier evidence; PC1 is strengthened but partly entangled with intelligence/expertise; PC2 remains the main uncertainty because abstraction correlates more strongly with PC2 than the direct coherent-action score.
- Caveat: this is Codex-as-rater, not an independent human or second-model blinded-rating study.

### Professional Hierarchy Validation (2026-05-30)

- Ran a targeted professional-role validation over 102 professional, technical, scientific, analytical, academic, and expert personas present in the Qwen geometry and no-label prompt corpus.
- Codex/GPT-5.5 rated anonymized no-label professional dossiers before PCA evaluation on objective certainty, coherent action under unresolved uncertainty, and system perturbation.
- PC1 received targeted professional support: objective certainty correlated with actual PC1 at r=0.394, and the high-PC1 professional pole contains auditor, examiner, evaluator, validator, screener, reviewer, and grader-like roles.
- PC3 received modest targeted support: system perturbation correlated with actual PC3 at r=0.319, and the three-rating model predicted professional PC3 with CV R2=0.429.
- PC2 was not supported as a professional coherent-action hierarchy: coherent uncertainty capacity was essentially uncorrelated with actual PC2 at r=-0.007.
- Scientist vs physicist weakly supports the actual abstraction ordering because physicist is lower on PC2 than scientist, but the blinded rating gave them similar coherent-uncertainty capacity scores.
- Interpretation: PC1 remains moderate-confidence; PC3 remains moderate with professional counterexamples; PC2 should be reframed away from simple professional uncertainty capacity and toward abstraction/historical-theoretical/world-model depth unless future tests separate those factors more cleanly.

### PC2 Conditional Validation After PC1 Control (2026-05-30)

- Ran a conditional PC2 validation over 273 common personas using 10 PC1 percentile bands and blinded no-label dossier scores.
- Abstraction was the strongest residual predictor of PC2 after band demeaning: pooled Pearson r=-0.618 and R2=0.382.
- Coherent action under unresolved uncertainty remained weaker but nonzero: pooled Pearson r=+0.427 and R2=0.182.
- Uncertainty exposure failed as a conditional explanation: pooled Pearson r=-0.026 and R2=0.001.
- Matched-pair and mythic/developmental tests support revising PC2 from a coherent-action-only axis to an abstraction/integration/developmental axis, with coherent action retained as a secondary behavioral expression.

---

## 3. CURRENT STATE

### Frequently Referenced Findings

| Finding | Current status | Metric or state | Primary source |
|---|---|---:|---|
| Semantic baseline performance | established | canonical activation PCA3D R2 0.389 | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv` |
| Big Five performance | established | Claude Big Five R2 0.613 vs semantic baseline 0.389 | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv` |
| Trait-vector geometry prediction | established/provenance-coupled | Qwen trait-cosine matrix predicts PCA3D with ridge CV R2: PC1 0.999, PC2 0.999, PC3 1.000 | `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_report.md` |
| Trait-space direct PCA | provisional/mixed | trait PC1 aligns with persona PC1 abs cosine 0.681; trait PC2/PC3 weakly align 0.194/0.065; trait-space cone test negative | `research/outputs/trait_space_interpretation/trait_space_axis_report.md` |
| Trait prompt artifacts for forecasting | established | 240/240 trait artifacts match Qwen trait vectors and Belmore prompt rows; Belmore has 516 total rows including 275 roles, 240 traits, 1 default | `research/outputs/prompt_artifact_inventory/prompt_artifact_inventory_report.md` |
| Prompt-to-geometry forecasting | established/provenance-coupled | leakage-control elastic-net TF-IDF predicts held-out traits mean R2 0.389 and held-out roles mean R2 0.621 | `research/outputs/prompt_to_geometry_forecasting/forecasting_dataset_summary.md` |
| Percentile-edge H100 activation validation | established / full proof-of-concept success | 100 prompts; forecast-vs-observed Pearson r: PC1 0.691, PC2 0.643, PC3 0.491 | `research/outputs/h100_percentile_edge_validation/h100_final_report.md` |
| H100 regional error geometry | established calibration target | mean signed delta=(-9.114,+28.342,-8.151); PC3-high tail retention=0/16; center-collapse rate=0.280 | `research/outputs/h100_percentile_edge_validation_error_analysis/regional_error_report.md` |
| H100 diagnostic checklist | active/in progress | D01 projection verified but extraction equivalence open; D02-D08 open; D09 calibration scaffolded | `research/outputs/h100_diagnostic_followups/diagnostic_followup_checklist.md` |
| Extraction equivalence audit | active/in progress | projection/pooling/model identity and trickster hook-based replication verified; hook-vs-`output_hidden_states[48]` equivalence unresolved | `research/outputs/extraction_equivalence_audit/extraction_equivalence_audit_report.md` |
| Adaptive H100 prompt battery expansion | established design artifact | 60 supplemental prompts; high-PC3 above prior q75=38; high-PC2 above prior q75=44; combined target-cell coverage 16/27 | `research/outputs/novel_prompt_battery_expansion/adaptive_prompt_expansion_report.md` |
| Percentile-edge H100 prompt battery | established design artifact / ready | 100 prompts; all six inherited 20/80 tail targets pass; shoulder/edge=58; interior=20; filters pass | `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_battery_report.md` |
| Pre-H100 methods memorial | established documentation | methods/assumptions/readiness state captured before activation validation | `research/outputs/pre_h100_methods_memorial/pre_h100_methods_memorial.md` |
| Procedural/Codex retained performance | established | Codex retained R2 0.490 vs semantic baseline 0.389 | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv` |
| Hierarchical trait-procedural performance | provisional | R2 0.622 vs trait stage 0.613 | `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/hierarchical_model_report.md` |
| PC2 conditional explanation | provisional/strongest current | abstraction r=-0.618 after PC1 band control; coherent action r=+0.427 | `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md` |
| Residual manifold performance | provisional | R2 0.632 vs hierarchical baseline 0.622 | `research/q2_stability/qwen/outputs/residual_manifold_analysis/residual_manifold_report.md` |
| SVD15 lexical/register performance | provisional | sem+BigFive+SVD15 R2 0.707 vs sem+BigFive 0.613 | `research/q2_stability/qwen/outputs/residual_svd_interpretation/residual_svd_interpretation_report.md` |
| PC3 interpretation | provisional | preserve/exploit rubric r=-0.312; nurturing/competitive r=-0.319; agreeableness r=-0.477 | `research/q2_stability/qwen/outputs/pc3_hypothesis_evaluation/pc3_hypothesis_report.md` |
| Blinded no-label PC rubric validation | provisional/weak | target correlations: PC1 r=0.247, PC2 r=0.224, PC3 r=0.349; pairwise direction 35-40% | `research/q2_stability/qwen/outputs/blinded_axis_rubric_validation/blinded_axis_validation_report.md` |
| Reading-based blinded PC rater study | provisional/stronger | target correlations: PC1 r=0.558, PC2 r=0.373, PC3 r=0.690; pairwise direction 75-100% | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Professional hierarchy validation | provisional/mixed | PC1 r=0.394; PC2 r=-0.007 for uncertainty capacity; PC3 r=0.319, PC3 CV R2 0.429 | `research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md` |
| Evaluator-model sensitivity | unresolved | harness exists, paired `gpt-4.1-mini` records blocked by quota | `research/q2_stability/qwen/evaluator_sensitivity/` |

**Paper 1.5 current scope:** Paper 1.5 is now a persona-geometry interpretation paper. The working title is `Interpreting Persona Activation Geometry`. The main claim is that persona activation geometry appears to decompose into layered semantic, dispositional, procedural, lexical/register, and residual structures after methodological stress testing. Adaptive extraction remains important due diligence and tooling evidence, but it is no longer the primary paper frame.

**Paper 2 current scope:** Paper 2 is now local centroid perturbation and local persona-manifold mapping. Candidate anchors are Trickster, Actor, Therapist, and Spy. The scientific question is whether local directions such as provocation, concealment, empathy/attunement, identity flexibility, dominance/submission, theatricality, strategic disclosure, moral constraint, and sincerity/performance transfer across anchors or are strongly curved/persona-dependent.

**Archived Paper 2 framing:** Older dyad contagion, attractor-collapse, conversational drift, and rumination plans are archived rather than deleted. The archive note is `research/archive/paper2_dyad_contagion_archive_2026-05-28.md`; earlier draft files carry supersession notes.

**Grant/future-work state:** H100 local-manifold work is not required for Paper 1.5. It is the strongest grant-supported next phase because the trickster extraction already demonstrated tooling competence and the local-manifold program is a concrete compute-intensive frontier.

**Paper 1.5 state:** Qwen/Qwen3-32B trickster Phase 1 is complete with 1200/1200 preserved rollouts, 1200 matching activation shards, and final integrity passed. Truncation is high, 733/1200 at 512 tokens, but is tracked as an explicit covariate and does not materially destabilize pre-scoring geometric convergence.

**Paper 1.5 scoring and validation:** Codex GPT-5.5 Standard was used as a pragmatic role-expression judge after the planned gpt-4.1-mini API scoring path was blocked by quota. Adaptive Codex scoring reached 64 scored records with 64 score>=2 and 33 score==3 responses; vector validation against the Lu trickster reference succeeded, with `score_ge_2` as the best candidate at cosine 0.957557 to the Lu mean, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets. This is an operationally validated adaptive extraction path, not a strict Lu-method judge replication.

**Editor second-persona test:** The first editor chunk completed 128 deterministic Qwen/Qwen3-32B rollouts at the 512-token cap, and a matched first-64 follow-up completed at the 1024-token cap. Codex GPT-5.5 scoring found only 10 score>=2 and 3 score==3 responses in the 128-record 512-token set; the matched 1024-token run sharply reduced truncation but did not improve role-expression yield. Vector validation and sample sufficiency were correctly not run for editor because validation thresholds were not met.

**Paper 1.5 documentation:** `research/paper1_5_outline.md` contains the adaptive extraction methodology, and `research/paper1_5_adaptive_extraction_notes.md` contains the supporting workflow note for future persona runs. The canonical Lu et al. methodology extraction package now lives in `research/assistant_axis_methodology/`, including artifact inventory, pipeline reconstruction, exact role prompts, exact extraction questions, judge prompts, vector-structure audit, replication-difference audit, open questions, and a relevant repo-structure export.

**Current session update (2026-05-30):** Completed the adaptive high-PC3/high-PC2 prompt expansion under `research/outputs/novel_prompt_battery_expansion/`; generated reproducible script, candidate log, supplemental and combined prompt batteries, H100 manifests, coverage stats, coverage plot, and report. Next step: run a staged H100 validation beginning with `supplemental_h100_prompt_manifest.csv` to test whether measured activations reach the predicted high-PC3/high-PC2 frontier addresses. Last commit before this update: `cc6dcfb`.

**Current session update (2026-05-30, percentile-edge battery):** Completed the percentile-thresholded edge-heavy prompt battery under `research/outputs/novel_prompt_battery_percentile_edges/`; generated reproducible script, inherited threshold file, candidate/rejection logs, prompt battery, H100 manifest, coverage stats/table, plot, and report. Next step: run H100 activation validation with `percentile_edge_h100_manifest.csv` as the primary manifest. Last commit before this update: `52580a6`.

**Current session update (2026-05-30, pre-H100 memorial):** Created the pre-H100 methods memorial under `research/outputs/pre_h100_methods_memorial/`, including the main memo, assumptions/decisions note, artifact index, and readiness summary. Next step: run the H100 smoke test with `percentile_edge_h100_manifest.csv`, then proceed through checkpointed activation validation if the smoke test passes. Last commit before this update: `50871f2`.

**Methodology audit state:** The role-prompt label-exposure audit is complete. Outputs are `research/assistant_axis_methodology/role_prompt_label_exposure_audit.json` and `research/assistant_axis_methodology/role_prompt_label_exposure_audit.md`; the audit script is `research/assistant_axis_methodology/scripts/audit_role_prompt_label_exposure.py`. The next recommended methodology audit is a behavioral-specificity audit that removes role labels from prompts and measures how much role-identifying content remains.

**No-label ablation state:** The no-label prompt-ablation dataset and semantic comparison are complete under `research/assistant_axis_methodology/no_label_prompt_ablation/`. Key outputs are `no_label_role_prompts.jsonl`, `no_label_prompt_ablation_validation.md`, `original_vs_no_label_semantic_comparison.md`, and `no_label_prompt_ablation_report.md`. The next recommended step is a small activation-space no-label stress test, not a full-scale pod run.

**Semantic-vs-activation state:** The three-way semantic-vs-activation comparison is complete under `research/assistant_axis_methodology/semantic_vs_activation_geometry/`, with interpretation note at `research/assistant_axis_methodology/semantic_topology_interpretation_note.md`. The analysis supports partial preservation plus activation-space reorganization: prompt semantics predict activation references weakly to modestly, and no-label prompt topology remains close to original prompt topology.

**Semantic-geometry synthesis state:** `research/assistant_axis_methodology/current_semantic_geometry_findings_recap.md` now summarizes tested claims, validated results, ruled-out interpretations, unresolved questions, and next tests from the semantic-geometry investigation. `research/assistant_axis_methodology/semantic_geometry_standalone_interpretation.md` treats the role corpus as a frontier-model-generated semantic role manifold independent of activation-space claims.

**Deep semantic-topology state:** `research/assistant_axis_methodology/deep_semantic_topology_analysis.md` now provides the deeper exploratory semantic-manifold interpretation, with machine-readable output at `research/assistant_axis_methodology/deep_semantic_topology_analysis.json`. Supporting files include `research/assistant_axis_methodology/cluster_anchor_roles.csv`, `research/assistant_axis_methodology/semantic_bridge_roles.csv`, and `research/assistant_axis_methodology/semantic_voids_note.md`.

**Cluster-overlap state:** `research/assistant_axis_methodology/cluster_overlap_analysis.md` now compares activation-space clusters, original semantic prompt clusters, and no-label semantic prompt clusters. Supporting outputs include `cluster_overlap_analysis.json`, `activation_cluster_semantic_overlap.csv`, `semantic_vs_activation_venn_tables.csv`, `stable_anchor_roles.csv`, `bridge_roles.csv`, and `cluster_overlap_interpretation_note.md`.

**No-label activation stress-test state:** The first activation-space no-label stress test is designed under `research/q2_stability/qwen/no_label_activation_test/`. The selected role rationale is `selected_roles.md`, the detailed plan is `no_label_activation_stress_test_plan.md`, and the machine-readable run specification is `no_label_activation_stress_test_dataset_spec.json`.

**Evaluator-sensitivity state:** The evaluator-sensitivity harness and blocked baseline outputs live under `research/q2_stability/qwen/evaluator_sensitivity/`, with script at `research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py`. The comparison is not complete because `gpt-4.1-mini` scoring is blocked by OpenAI `insufficient_quota`.

**Stage-1 role-inventory uncertainty state:** `research/stage1_role_inventory_uncertainty/` now contains the OpenAI-side role-inventory generation infrastructure, five prompt-family variants, provider-agnostic ingestion and normalization scripts, local manifold-comparison scaffolding, and `multi_provider_generation_architecture.md`. Codex should not orchestrate Anthropic API calls locally; Claude or Claude Code will generate Anthropic-side inventories separately and sync them through GitHub for local semantic analysis.

**Model provenance state:** `research/workflow/model_provenance_schema.md` defines the mandatory provenance schema for future generated, evaluated, and analyzed artifacts. Future artifacts must distinguish `generation_model`, `evaluation_model`, `analysis_model`, and `script_author_model` before commit; Stage-1 generation and ingestion scripts now require provenance for every role inventory.

**Latent-feature discovery state:** `research/q2_stability/qwen/scripts/latent_feature_discovery_loop.py` implements the first constrained model-assisted hypothesis-generation and held-out testing loop for persona activation geometry. `research/q2_stability/qwen/scripts/latent_feature_framing_ablation.py` extends this into a framing comparison over motivational, interactional, procedural, narrative-causal, all-framing, and prior first-loop feature sets. `research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py` now implements repeated-split outer-loop optimization with plateau detection. Machine-readable outputs live under `research/q2_stability/qwen/outputs/latent_feature_discovery/`, `research/q2_stability/qwen/outputs/latent_feature_framing_ablation/`, and `research/q2_stability/qwen/outputs/iterative_outer_loop/`. The current result is bounded: latent features improve held-out continuous geometry prediction more than hard cluster prediction.

**Visualization state:** `research/visualizations/persona_geometry_explorer.html` now uses full nearest-centroid cluster assignments from `research/visualizations/cluster_assignments_full.json` instead of incomplete hardcoded lists. `research/visualizations/geometry_viz_data.json` now includes role PCA coordinates and variance metadata; PC1 explains 0.315954 of variance and aligns with the assistant-axis vector at 0.802310 cosine. The visualizer UI now has explicit 2D axis labels, UMAP/PCA component swapping for X/Y/Z axes, an auto/fixed range toggle, fixed-range annotations, persistent multi-point selection with dimming, 2D lasso/box selection, focus-view mode with the title/metadata moved below the chart, explicit-only selection clearing, 3D camera persistence across re-renders, and Big Five-style overlay color modes. Big Five overlay data lives at `research/visualizations/bigfive_geometry_overlay_data.json` and `.csv`, sourced from `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_full_feature_matrix.csv`; scores are available for 273/275 geometry personas, with `coral_reef` and `devils_advocate` missing from the benchmark feature matrix.

**Persona-geometry working interpretation:** `research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md` preserves the current axis hypotheses with explicit epistemic labels. PC1 is best interpreted as constraint/objective certainty versus possibility/objective ambiguity; PC2 is least certain and currently framed as capacity for coherent action under unresolved uncertainty; PC3 is provisionally framed as cooperative-stabilizing versus antagonistic-transgressive; the cone hypothesis is preserved as a speculative admissible-configuration-count interpretation.

**Blinded axis-validation state:** `research/q2_stability/qwen/outputs/blinded_axis_rubric_validation/` now contains a coordinate-blind no-label prompt rubric validation for PC1, PC2, and PC3. It used all five no-label rewritten prompts for all 275 personas and found only modest direct correlations with PCA coordinates, strongest for PC3 and weakest for PC2; this should be treated as a provisional lexical-proxy screen rather than a true independent semantic-rating study.

**Reading-based rater state:** `research/q2_stability/qwen/outputs/blinded_axis_rater_study/` now contains a stronger Codex-as-rater blinded annotation study using anonymized no-label prompt dossiers. PC3 is the strongest direct axis interpretation in this evidence; PC1 is strengthened but overlaps with intelligence/expertise; PC2 remains compound, with abstraction outperforming the direct coherent-action-under-uncertainty score.

**Professional hierarchy validation state:** `research/q2_stability/qwen/outputs/professional_hierarchy_validation/` now contains a targeted professional-role stress test. It supports PC1 modestly, supports PC3 modestly with technical/institutional counterexamples, and weakens a simple professional coherent-action interpretation of PC2.

**Trait-persona prediction state:** `research/outputs/trait_persona_prediction/` now contains the raw Qwen activation-space trait-to-persona prediction test. It uses 275 role vectors and 240 trait vectors from `downloads/hf_vectors/qwen-3-32b/`, computes persona-by-trait cosine similarities, and predicts PCA coordinates with near-ceiling ridge CV R2 for PC1/PC2/PC3. This strongly supports trait-vector geometry as a predictive layer, but because the trait bank is high-dimensional and in the same activation space, it should be read as a provenance-coupled geometry result rather than independent psychological validation.

**Reporting standard:** `research/PROJECT_ORIENTATION.md` now includes an Enhanced Research Reporting section. Future Codex research reports should state what was done, what changed the current interpretation, key judgment calls, competing explanations, strongest unresolved uncertainty, confidence level, and recommended next test.

**Project onboarding:** `research/PROJECT_ORIENTATION.md` is the new-thread onboarding file to read immediately after `research/RESEARCH_STATE.md`. `research/FINDINGS_LEDGER.md` is the compact index of confirmed findings, negative findings, provisional interpretations, methodological deviations, blockers, and next tests. `research/NEW_SESSION_STARTUP.md` is the future-agent startup protocol for GPT, Claude, and Codex sessions.

**Provenance and index state:** `research/RESEARCH_INDEX.md` is the compact navigation file for current paper scopes, best metrics, important artifacts, open questions, pending experiments, visualizations, and PC interpretations. `research/PROVENANCE_REGISTRY.md` is the artifact-lineage registry for major Paper 1.5 datasets, scripts, model provenance, dependent analyses, current status, and caveats. Future agents should check these files before broad repo searches for provenance or state questions.

**Startup freshness maintenance:** `research/STARTUP_MANIFEST.md` is the freshness contract for cross-thread startup. Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, Codex must update that file's visible metadata, run `python3 scripts/update_startup_manifest.py`, and commit the regenerated manifest with the same state change.

**Workflow infrastructure:** `research/workflow/` contains the run registry specification, pod lifecycle protocol, Codex execution tiers, run status artifact spec, JSON templates, and pod launch/monitoring/closeout checklists. Future pod work should use these artifacts from launch onward; pod termination should prefer RunPod API or `runpodctl`, with browser/dashboard termination as fallback only. Chat threads are planning interfaces, not the operational source of truth.

**Zero-relay workflow state:** `research/runtime/` now contains the canonical command-bus files `PENDING_TASK.md`, `CURRENT_RESULTS.md`, and `OPEN_TASKS.md`. Claude Desktop has a local GitHub MCP server entry configured under `~/Library/Application Support/Claude/claude_desktop_config.json`; Claude Desktop must be fully quit and relaunched before the MCP server is active. The Mac Mini watcher script is installed at `/Users/alfred/Projects/scripts/codex_task_watcher.sh`, and cron checks it every five minutes to copy substantive pending tasks into `/tmp/codex_pending.txt`. `AGENTS.md` now records the required Codex session-start check for `/tmp/codex_pending.txt`.

**Completed this session:** Updated `research/visualizations/persona_geometry_explorer.html` with explicit 2D axis titles/ticks, axis component dropdowns, auto/fixed range controls, fixed-range annotations, persistent selection highlighting, 2D lasso/box selection, focus-view mode, explicit-only selection clearing, and preserved 3D camera state while rotating selected points.
**Completed this session:** Verified the visualizer remains self-contained and that the extracted JavaScript parses successfully.
**Completed this session:** Added Big Five-style trait overlay data and color modes to `research/visualizations/persona_geometry_explorer.html`, using the shared latent feature benchmark source where Claude Big Five predicts canonical activation PCA3D at R2 0.613 vs semantic baseline R2 0.389.
**Completed this session:** Added `research/PROVENANCE_REGISTRY.md` and `research/RESEARCH_INDEX.md`, and updated onboarding/state files so future sessions can answer provenance, methodology, and current-state questions before repo archaeology.
**Completed this session:** Configured the local Claude Desktop GitHub MCP server entry without printing the token, added the repo runtime command-bus files, installed the Mac Mini cron watcher, and added the Codex zero-relay startup rule to `AGENTS.md`.
**Completed this session:** Evaluated the PC3 preserving/exploiting interpretation adversarially using pairwise PC3 contrasts, blind description-only rubrics, alternative lexical hypotheses, cluster enrichment, and residual checks; outputs live under `research/q2_stability/qwen/outputs/pc3_hypothesis_evaluation/`.
**Completed this session:** Updated the findings ledger, research state, and machine-in-the-loop sticky note to record that PC3 is better framed as cooperative-care/system-stabilization versus antagonistic-disruptive/transgressive register, with moderate-low confidence.
**Completed this session:** Created `research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md` to preserve current PC1, PC2, PC3, and cone-hypothesis interpretations with observed/inferred/speculative/unknown labels.
**Completed this session:** Added Enhanced Research Reporting guidance to `research/PROJECT_ORIENTATION.md` so future research reports summarize interpretive significance, judgment calls, uncertainty, confidence, and next tests.
**Completed this session:** Ran the blinded PCA-axis rubric validation over the full available no-label prompt corpus, wrote outputs under `research/q2_stability/qwen/outputs/blinded_axis_rubric_validation/`, and updated the findings ledger, research index, provenance registry, and interpretation note.
**Completed this session:** Ran the reading-based Codex-as-rater blinded PCA-axis study over anonymized no-label persona dossiers, wrote outputs under `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`, and updated state/provenance/interpretation trackers.
**Completed this session:** Ran the professional hierarchy validation over 102 present professional/expert personas and updated the findings ledger, research index, research state, and interpretation note.
**Completed this session:** Ran conditional PC2 validation after PC1 decile-band control, generated band inventory, candidate scores, within-band correlations, matched pairs, and comparison outputs under `research/q2_stability/qwen/outputs/pc2_conditional_validation/`, and updated PC2 interpretation language.
**Completed this session:** Ran full-distribution PC3 perturbation-stabilization validation over all 275 personas, generated scores/statistics/report/plot outputs under `research/outputs/pc3_validation/`, and updated PC3 claim language to mixed but positive.
**Completed this session:** Ran trait-vector prediction of persona PCA axes using raw Qwen layer-48 role and trait vectors, generated similarity/statistics/coefficient/profile/plot outputs under `research/outputs/trait_persona_prediction/`, and updated claims/state to reflect that trait geometry strongly predicts PCA location while remaining provenance-coupled.
**Completed this session:** Ran direct trait-space PCA and cone testing over raw Qwen layer-48 trait vectors, generated axis rankings, validation statistics, cone plots, PC plots, and diagnostic trait-neighborhood outputs under `research/outputs/trait_space_interpretation/`, and updated claims/state to reflect a mixed result: trait space predicts persona geometry but direct trait PCs do not simply reproduce persona PC2/PC3.
**Completed this session:** Inventoried local and released prompt artifacts for trait-vector forecasting, verified 240/240 exact trait name alignment across local JSON artifacts, Qwen trait vectors, and `belmore/assistant-axis-vector-prompts`, and wrote readiness outputs under `research/outputs/prompt_artifact_inventory/`.
**Completed this session:** Tested prompt-to-geometry forecasting on held-out concepts, using leakage-controlled prompt text to predict trait PCs and role/persona PCs; outputs live under `research/outputs/prompt_to_geometry_forecasting/`.
**Completed this session:** Documented revised PC1 and PC2 forcing-function interpretations for forecasting-rubric design under `research/outputs/axis_forcing_function_notes/`.
**Completed this session:** Tested cluster-conditioned PC1/PC2 interpretation and cluster-prediction cost; outputs live under `research/outputs/cluster_conditioned_axis_tests/`.
**Completed this session:** Built a 120-prompt novel H100 validation battery under `research/outputs/novel_prompt_battery/`, serialized the frozen role leakage-control elastic-net TF-IDF forecaster, and documented incomplete but usable predicted geometry coverage.
**Completed this session:** Ran the percentile-edge 100-prompt H100/A100 activation validation, copied and checksummed outputs, and confirmed all three forecasted PCs positively correlate with independently measured Qwen/Qwen3-32B response activation coordinates.
**Next step:** Fit and evaluate a simple H100 calibration layer, starting with per-axis intercept/slope correction and then region-aware corrections for PC2 and PC3 tails.
**Last commit before this session:** 0806ed1

**Completed this session:** Added H100 forecast-vs-observed regional error analysis and interactive 3D/2D arrow visualizations under `research/outputs/h100_percentile_edge_validation_error_analysis/`.
**Next step:** Resolve D01 by comparing the H100 extraction path against upstream/source Assistant Axis extraction code, then fit per-axis calibration once measurement equivalence is closed.
**Last commit before this update:** `4b33e76` / `Analyze H100 forecast-observed error geometry`

**Completed this session:** Created the persistent H100 diagnostic checklist D01-D09 and ran the first diagnostic pass under `research/outputs/h100_diagnostic_followups/`.
**Next step:** Resolve D01 by comparing the H100 extraction path against upstream/source Assistant Axis extraction code, then proceed to per-axis calibration if measurement equivalence holds.
**Last commit before this update:** `4b33e76` / `Analyze H100 forecast-observed error geometry`

**Pending papers:** Paper 3 (confidence vector), Paper 3.5 (archetype self-selection), Paper 4 (computational rumination) remain pre-analysis and depend on the Paper 1.5/Paper 2 experimental sequence.
**Completed this session:** Added native training-artifact forecast-vs-target error geometry under `research/outputs/training_forecast_error_geometry/` and updated the H100 diagnostic checklist D03/D08/D09 cross-references.
**Next step:** Run a held-out-role-only version of the same target-to-forecast visualization, then fit calibration only after D01 extraction-equivalence review is closed.
**Last commit before this update:** `80a6e31` / `Add H100 diagnostic follow-up checklist and first pass`

**Completed this session:** Audited extraction equivalence across original/local Assistant Axis source code, prior adaptive trickster/editor runs, and the H100 percentile-edge validation runner; outputs live under `research/outputs/extraction_equivalence_audit/`.
**Completed this session:** Updated D01 to remain `in_progress` because projection, pooling, model identity, and prior trickster replication are verified, but hook-based layer-48 extraction has not been proven equivalent to H100 `output_hidden_states[48]`.
**Next step:** Run the minimal Qwen/Qwen3-32B hook-vs-hidden-states equivalence test before treating H100 PC2/PC3 anomalies as fully behavioral rather than potentially measurement-site-sensitive.
**Last commit before this update:** `5607390` / `Visualize training forecast error geometry`

**Pod status:** H100 validation RunPod pod `yyelrl4oe9266o` was terminated via `runpodctl pod delete` after outputs were copied and checksummed locally. `runpodctl pod list` returned `[]`, and `runpodctl pod get yyelrl4oe9266o` returned 404 `pod not found`.
