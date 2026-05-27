# RESEARCH_STATE.md
# Canonical state document for the assistant-axis research project.
# Updated at the end of every Codex session. Fetch this first in any new session.
# Raw URL: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md

**Last updated:** 2026-05-27
**Last commit:** 926a6f2
**Current status:** Active — Paper 1.5 trickster adaptive extraction validation complete; editor first-chunk adaptive extraction and matched token-cap sensitivity are complete but did not meet validation thresholds; workflow infrastructure now exists under `research/workflow/`; a canonical Lu et al. Assistant Axis methodology extraction package now exists under `research/assistant_axis_methodology/`

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

---

## 3. CURRENT STATE

**Paper 1.5 state:** Qwen/Qwen3-32B trickster Phase 1 is complete with 1200/1200 preserved rollouts, 1200 matching activation shards, and final integrity passed. Truncation is high, 733/1200 at 512 tokens, but is tracked as an explicit covariate and does not materially destabilize pre-scoring geometric convergence.

**Paper 1.5 scoring and validation:** Codex GPT-5.5 Standard was used as a pragmatic role-expression judge after the planned gpt-4.1-mini API scoring path was blocked by quota. Adaptive Codex scoring reached 64 scored records with 64 score>=2 and 33 score==3 responses; vector validation against the Lu trickster reference succeeded, with `score_ge_2` as the best candidate at cosine 0.957557 to the Lu mean, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets. This is an operationally validated adaptive extraction path, not a strict Lu-method judge replication.

**Editor second-persona test:** The first editor chunk completed 128 deterministic Qwen/Qwen3-32B rollouts at the 512-token cap, and a matched first-64 follow-up completed at the 1024-token cap. Codex GPT-5.5 scoring found only 10 score>=2 and 3 score==3 responses in the 128-record 512-token set; the matched 1024-token run sharply reduced truncation but did not improve role-expression yield. Vector validation and sample sufficiency were correctly not run for editor because validation thresholds were not met.

**Paper 1.5 documentation:** `research/paper1_5_outline.md` contains the adaptive extraction methodology, and `research/paper1_5_adaptive_extraction_notes.md` contains the supporting workflow note for future persona runs. The canonical Lu et al. methodology extraction package now lives in `research/assistant_axis_methodology/`, including artifact inventory, pipeline reconstruction, exact role prompts, exact extraction questions, judge prompts, vector-structure audit, replication-difference audit, open questions, and a relevant repo-structure export.

**Workflow infrastructure:** `research/workflow/` contains the run registry specification, pod lifecycle protocol, Codex execution tiers, run status artifact spec, JSON templates, and pod launch/monitoring/closeout checklists. Future pod work should use these artifacts from launch onward; pod termination should prefer RunPod API or `runpodctl`, with browser/dashboard termination as fallback only. Chat threads are planning interfaces, not the operational source of truth.

**Completed this session:** Created `research/assistant_axis_methodology/` as a canonical methodology extraction package for Lu et al. (2026), including exact prompt/question exports and source-cited reconstruction notes.
**Completed this session:** Audited local Lu et al. paper copies, repo pipeline scripts, prompt JSONs, extraction questions, judge prompts, downloaded HF vectors, notebooks, and Paper 1.5 replication artifacts into `artifact_inventory.md`.
**Completed this session:** Documented explicit Lu-method steps versus uncertain or locally inferred behavior, including residual-stream position, judging categories, vector filtering ambiguity, and local adaptive-extraction differences.
**Next step:** Use the methodology package as the canonical reference for future GPT/Claude planning; separately design a revised editor anchoring methodology before any further editor rollout generation.
**Last commit before this session:** 926a6f2

**Pending papers:** Paper 3 (confidence vector), Paper 3.5 (archetype self-selection), Paper 4 (computational rumination) remain pre-analysis and depend on the Paper 1.5/Paper 2 experimental sequence.
**Pod status:** Editor RunPod pod `5b6hz02m9idrc3` is terminated. `runpodctl pod list` returns no running pods, and `runpodctl pod get 5b6hz02m9idrc3` returns 404 `pod not found`.
