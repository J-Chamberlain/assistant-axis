# RESEARCH_STATE.md
# Canonical state document for the assistant-axis research project.
# Updated at the end of every Codex session. Fetch this first in any new session.
# Raw URL: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md

**Last updated:** 2026-05-24
**Last commit:** e37af1a
**Current status:** Active — Paper 2 methodology v2 created; q2_stability split by model provenance; Qwen-native centroid representatives selected; role instruction prompts for all seven v2 personas found and printed for Phase 1 prompt design; cluster synthesis inputs assembled; non-leaking cluster background prompts v1, v2, and motivational-depth v3 saved for comparison; recalibration for actor/hoarder/maverick not yet run; v6 pilot outputs present; full 21-condition v6 grid not present locally

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

---

## 3. CURRENT STATE

**In progress:** v6 dyad design remains active, but local outputs show only trickster/adversarial 25-turn pilots plus a partial trickster/emotional run; the full 7 personas × 3 conditions × 25 turns grid is not present locally.
**Completed this session:** Terminated the stopped RunPod A100 SXM pod `professional_sapphire_peafowl` after the interrupted recalibration attempt.
**Completed this session:** Audited the interrupted recalibration status and confirmed that `actor_calibration.csv`, `hoarder_calibration.csv`, `maverick_calibration.csv`, and `all_personas_calibration_summary_v2.json` do not exist locally.
**Completed this session:** Confirmed that `research/paper2_methods_v2.md`, `research/q2_stability/README.md`, and `research/q2_stability/qwen/outputs/calibration/CENTROID_NOTE.md` are present from prior committed work.
**Completed this session:** Audited Lu et al. prompt/transcript availability and found local role instruction JSONs for all seven v2 personas under `data/roles/instructions/`, each with five positive system prompts and 40 role-specific questions.
**Completed this session:** Confirmed that `downloads/hf_vectors/` and the HuggingFace cache contain vector tensors and metadata only, while local transcripts under `transcripts/` are paper case studies/persona-drift examples rather than seven-role extraction rollouts.
**Completed this session:** Printed the full contents of the seven v2 persona instruction files and the first 20 lines of `data/extraction_questions.jsonl` for Phase 1 prompt drafting.
**Completed this session:** Assembled `research/q2_stability/qwen/outputs/calibration/cluster_synthesis_inputs.json` from `visualizations/full_ranking.csv`, `visualizations/cluster_trait_profiles.csv`, and all 275 role instruction files.
**Completed this session:** Synthesized seven non-leaking interviewer background prompts directly from role instructions and trait-space profiles, validated them against role names, cluster labels, and trait labels, and saved `research/q2_stability/qwen/outputs/calibration/cluster_background_prompts_v1.json`.
**Completed this session:** Added the Codex analytical-work model specification to `AGENTS.md` and corrected `cluster_background_prompts_v1.json` model metadata to `GPT-5.3-Codex`.
**Completed this session:** Updated the Codex analytical-work model specification to `GPT-5.5` and corrected `cluster_background_prompts_v1.json` model metadata to `GPT-5.5`.
**Completed this session:** Reran cluster synthesis as GPT-5.5 from `cluster_synthesis_inputs.json`, saved `cluster_background_prompts_v2.json`, and updated v1 model provenance to note the retroactive correction.
**Completed this session:** Produced motivational-depth cluster synthesis v3 as GPT-5.5 and saved `research/q2_stability/qwen/outputs/calibration/cluster_background_prompts_v3.json`.
**Completed this session:** Appended the dialogue-derived characterization of the other cluster to `research/paper2_methods_v2.md` and created `research/paper4_research_notes.md` with the Buddhist-framework connection for Paper 4.
**Next step:** Review v1, v2, and v3 prompts, choose the canonical background prompt version for dyad experiments, then append the cluster synthesis methodology section to `research/paper2_methods_v2.md`.
**Pending papers:** Paper 3 (confidence vector), Paper 3.5 (archetype self-selection), Paper 4 (computational rumination) — all pre-analysis, depend on v6 data
**Pod status:** No RunPod compute is running for the interrupted recalibration attempt; the stopped pod was terminated from the RunPod UI on 2026-05-24.
**Last commit before this session:** 290e934
