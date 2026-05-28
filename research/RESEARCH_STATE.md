# RESEARCH_STATE.md
# Canonical state document for the assistant-axis research project.
# Updated at the end of every Codex session. Fetch this first in any new session.
# Raw URL: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md

**Last updated:** 2026-05-28
**Last commit:** see git log
**Current status:** Active — Cross-model latent feature comparison COMPLETE: BigFive R²=0.613 outperforms Codex 31-dim R²=0.490 on canonical activation PCA; developmental personas are hardest to explain across both models; pseudo-PCA PC1 failure was target-specific artifact (canonical PC1 R²=0.734 with BigFive). Stage 1 inventory sensitivity scaffold ready. Paper 1.5 trickster validation complete; editor extraction below threshold; evaluator-sensitivity blocked by OpenAI quota.

---

## 1. WHAT HAS BEEN ATTEMPTED

### Claude Latent Feature Discovery Loop (2026-05-28, Complete)
- Independent hypothesis-generation and interpretation pass over existing local artifacts
- Target: pseudo-PCA3D from 275×7 Qwen cluster-cosine matrix (95.5% total EV)
- Null: permutation R²=-0.322 mean, p95=-0.221
- TF-IDF semantic baseline: PCA3D R²=0.142
- Best model (TF-IDF + BigFive): PCA3D R²=0.361, Gemma axis R²=0.695
- Key finding: PC1 is unpredicted (R²=-0.089); PC2 R²=0.732; PC3 R²=0.440
- Plateau at round 3; DarkTriad and semantic cluster add no signal over BigFive
- Best-explained: procedural_professional (architect, journalist, paramedic, marketer)
- Worst-explained: "other" cluster developmental stages; proofreader (editorial outlier)
- Cross-model comparison complete (2026-05-28): BigFive R²=0.613 on canonical PCA > Codex 31-dim R²=0.490
- Pseudo-PCA PC1 failure (R²=-0.089) was target-specific; canonical PC1 BigFive R²=0.734
- 6 worst-explained personas overlap between Claude and Codex: toddler, caveman, infant, teenager, poet, procrastinator
- Artifacts: `research/q2_stability/qwen/outputs/claude_latent_feature_loop/` (including `claude_on_shared_benchmark_report.md`)

### Stage 1 Inventory Sensitivity Scaffold (2026-05-28, Complete)
- Generation script + analysis script for 5 models × 5 prompts × 3 runs (75 API calls)
- Ready to run; awaits API key configuration
- Artifacts: `research/stage1_inventory_sensitivity/`

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

---

## 3. CURRENT STATE

**Paper 1.5 state:** Qwen/Qwen3-32B trickster Phase 1 is complete with 1200/1200 preserved rollouts, 1200 matching activation shards, and final integrity passed. Truncation is high, 733/1200 at 512 tokens, but is tracked as an explicit covariate and does not materially destabilize pre-scoring geometric convergence.

**Paper 1.5 scoring and validation:** Codex GPT-5.5 Standard was used as a pragmatic role-expression judge after the planned gpt-4.1-mini API scoring path was blocked by quota. Adaptive Codex scoring reached 64 scored records with 64 score>=2 and 33 score==3 responses; vector validation against the Lu trickster reference succeeded, with `score_ge_2` as the best candidate at cosine 0.957557 to the Lu mean, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets. This is an operationally validated adaptive extraction path, not a strict Lu-method judge replication.

**Editor second-persona test:** The first editor chunk completed 128 deterministic Qwen/Qwen3-32B rollouts at the 512-token cap, and a matched first-64 follow-up completed at the 1024-token cap. Codex GPT-5.5 scoring found only 10 score>=2 and 3 score==3 responses in the 128-record 512-token set; the matched 1024-token run sharply reduced truncation but did not improve role-expression yield. Vector validation and sample sufficiency were correctly not run for editor because validation thresholds were not met.

**Paper 1.5 documentation:** `research/paper1_5_outline.md` contains the adaptive extraction methodology, and `research/paper1_5_adaptive_extraction_notes.md` contains the supporting workflow note for future persona runs. The canonical Lu et al. methodology extraction package now lives in `research/assistant_axis_methodology/`, including artifact inventory, pipeline reconstruction, exact role prompts, exact extraction questions, judge prompts, vector-structure audit, replication-difference audit, open questions, and a relevant repo-structure export.

**Methodology audit state:** The role-prompt label-exposure audit is complete. Outputs are `research/assistant_axis_methodology/role_prompt_label_exposure_audit.json` and `research/assistant_axis_methodology/role_prompt_label_exposure_audit.md`; the audit script is `research/assistant_axis_methodology/scripts/audit_role_prompt_label_exposure.py`. The next recommended methodology audit is a behavioral-specificity audit that removes role labels from prompts and measures how much role-identifying content remains.

**No-label ablation state:** The no-label prompt-ablation dataset and semantic comparison are complete under `research/assistant_axis_methodology/no_label_prompt_ablation/`. Key outputs are `no_label_role_prompts.jsonl`, `no_label_prompt_ablation_validation.md`, `original_vs_no_label_semantic_comparison.md`, and `no_label_prompt_ablation_report.md`. The next recommended step is a small activation-space no-label stress test, not a full-scale pod run.

**Semantic-vs-activation state:** The three-way semantic-vs-activation comparison is complete under `research/assistant_axis_methodology/semantic_vs_activation_geometry/`, with interpretation note at `research/assistant_axis_methodology/semantic_topology_interpretation_note.md`. The analysis supports partial preservation plus activation-space reorganization: prompt semantics predict activation references weakly to modestly, and no-label prompt topology remains close to original prompt topology.

**Semantic-geometry synthesis state:** `research/assistant_axis_methodology/current_semantic_geometry_findings_recap.md` now summarizes tested claims, validated results, ruled-out interpretations, unresolved questions, and next tests from the semantic-geometry investigation. `research/assistant_axis_methodology/semantic_geometry_standalone_interpretation.md` treats the role corpus as a frontier-model-generated semantic role manifold independent of activation-space claims.

**Deep semantic-topology state:** `research/assistant_axis_methodology/deep_semantic_topology_analysis.md` now provides the deeper exploratory semantic-manifold interpretation, with machine-readable output at `research/assistant_axis_methodology/deep_semantic_topology_analysis.json`. Supporting files include `research/assistant_axis_methodology/cluster_anchor_roles.csv`, `research/assistant_axis_methodology/semantic_bridge_roles.csv`, and `research/assistant_axis_methodology/semantic_voids_note.md`.

**Cluster-overlap state:** `research/assistant_axis_methodology/cluster_overlap_analysis.md` now compares activation-space clusters, original semantic prompt clusters, and no-label semantic prompt clusters. Supporting outputs include `cluster_overlap_analysis.json`, `activation_cluster_semantic_overlap.csv`, `semantic_vs_activation_venn_tables.csv`, `stable_anchor_roles.csv`, `bridge_roles.csv`, and `cluster_overlap_interpretation_note.md`.

**No-label activation stress-test state:** The first activation-space no-label stress test is designed under `research/q2_stability/qwen/no_label_activation_test/`. The selected role rationale is `selected_roles.md`, the detailed plan is `no_label_activation_stress_test_plan.md`, and the machine-readable run specification is `no_label_activation_stress_test_dataset_spec.json`.

**Evaluator-sensitivity state:** The evaluator-sensitivity harness and blocked baseline outputs live under `research/q2_stability/qwen/evaluator_sensitivity/`, with script at `research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py`. The comparison is not complete because `gpt-4.1-mini` scoring is blocked by OpenAI `insufficient_quota`.

**Project onboarding:** `research/PROJECT_ORIENTATION.md` is the new-thread onboarding file to read immediately after `research/RESEARCH_STATE.md`. `research/FINDINGS_LEDGER.md` is the compact index of confirmed findings, negative findings, provisional interpretations, methodological deviations, blockers, and next tests. `research/NEW_SESSION_STARTUP.md` is the future-agent startup protocol for GPT, Claude, and Codex sessions.

**Workflow infrastructure:** `research/workflow/` contains the run registry specification, pod lifecycle protocol, Codex execution tiers, run status artifact spec, JSON templates, and pod launch/monitoring/closeout checklists. Future pod work should use these artifacts from launch onward; pod termination should prefer RunPod API or `runpodctl`, with browser/dashboard termination as fallback only. Chat threads are planning interfaces, not the operational source of truth.

**Completed this session:** Built the evaluator-sensitivity harness and verified canonical judge prompt, trickster corpus, and editor corpus paths.
**Completed this session:** Imported 192 existing Codex GPT-5.5 score records into `research/q2_stability/qwen/evaluator_sensitivity/evaluator_sensitivity_results.jsonl`.
**Completed this session:** Attempted `gpt-4.1-mini` canonical-rubric rescoring, but OpenAI returned `insufficient_quota`, so no paired evaluator comparison was completed.
**Next step:** Rerun `python3 research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py` after OpenAI API quota is restored; separately launch the bounded no-label activation stress-test pod after user approval.
**Last commit before this session:** 77879d6

**Pending papers:** Paper 3 (confidence vector), Paper 3.5 (archetype self-selection), Paper 4 (computational rumination) remain pre-analysis and depend on the Paper 1.5/Paper 2 experimental sequence.
**Pod status:** Editor RunPod pod `5b6hz02m9idrc3` is terminated. `runpodctl pod list` returns no running pods, and `runpodctl pod get 5b6hz02m9idrc3` returns 404 `pod not found`.
