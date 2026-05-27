# No-Label Activation-Space Stress Test Plan

## 1. Research Question

Does Qwen/Qwen3-32B activation-space persona geometry survive when explicit role-label exposure is removed from the role-elicitation system prompts?

The experiment compares two paired conditions for the same roles and question pairs:

1. Original Lu-style label-exposed system prompts.
2. No-label prompt rewrites that preserve behavioral content while removing explicit role names and normalized variants.

The core methodological question is whether the original activation directions are primarily driven by explicit lexical identity labels, by behavioral semantics that remain after label removal, or by a model-specific latent organization of enacted behavioral stance.

## 2. Why Label Exposure Matters

The local label-exposure audit found that 1280/1375 Lu et al. role prompts, 93.1 percent, expose the target role label or a normalized variant. This means the original elicitation procedure is not purely behavioral. It is more accurately described as role-label-plus-behavior elicitation.

The no-label prompt-ablation audit then showed that prompt-space semantic topology mostly survives label removal at the continuous level. Role-level SVD cosine has median 0.998, nearest-neighbor preservation is 0.924, and pairwise distance correlation is 0.985. However, hard semantic clusters shift substantially. Prompt-space survival therefore does not settle the activation-space question. This experiment tests that directly.

## 3. Prior Findings Motivating the Test

The semantic-vs-activation comparison found only partial hard-cluster agreement between prompt-space semantics and activation-space labels. At k=7, ARI against activation labels is 0.111 for original prompt clusters and 0.130 for no-label prompt clusters. No-label prompt distances best predict available Gemma and Qwen centroid-profile distances among tested semantic spaces, but only modestly.

The cluster-overlap analysis found 73 stable activation-semantic anchor roles and 198 broad bridge or migratory roles. Editorial is the cleanest overlap region, procedural-professional compresses several semantic regions into one broad activation basin, and collective/swarm roles are semantically compact but distributed across larger activation clusters.

The prior Qwen extraction results add a critical contrast. Trickster validated cleanly against the Lu reference with `score>=2` cosine 0.957557 to the Lu mean. Editor, despite complete label exposure and clear prompt semantics, produced only 10 score>=2 and 3 score==3 responses in 128 scored records. This suggests that label exposure alone does not guarantee successful role-vector recovery.

## 4. Role Selection Rationale

The selected 20-role set is documented in `selected_roles.md` and machine-readable form in `no_label_activation_stress_test_dataset_spec.json`.

The set covers:

- Stable anchors: `screener`, `trickster`, `jester`, `leviathan`
- Assistant-adjacent and procedural roles: `editor`, `screener`, `reviewer`, `consultant`, `evaluator`, `proofreader`, `negotiator`, `skeptic`
- Theatrical and fantastical roles: `trickster`, `jester`, `oracle`, `leviathan`, `mystic`
- Collective/swarm roles: `hive`, `egregore`
- Bridge and migratory roles: `proofreader`, `negotiator`, `consultant`, `oracle`, `mystic`, `skeptic`, `philosopher`, `spy`, `dilettante`
- Sparse/outlier roles: `flaneur`, `robot`

`diplomat` is excluded because it is not present in the 275-role assignment table.

## 5. Experimental Controls

The experiment alters only explicit role-label exposure in the system prompt text.

Held constant:

- Model: `Qwen/Qwen3-32B`
- Layer: 48
- Activation extraction: full transformer block output at `model.model.layers[48]`, mean-pooled over response tokens
- Measurement pass: `use_cache=False`
- Generation: deterministic
- Thinking mode: disabled through the same validated Qwen chat-template path where supported
- Questions: same extraction question indices in both conditions
- Prompt indices: same five system-prompt slots in both conditions
- Rollout order: stable deterministic `(role, condition, sp_idx, q_idx)` order
- Activation storage: one `.pt` shard per rollout, separate from JSONL
- Scoring: no judge calls on pod
- Integrity: local preservation and integrity before scoring or validation

Changed:

- `condition=original_label_exposed` uses `data/roles/instructions/{role}.json`
- `condition=no_label_ablation` uses the corresponding no-label rewritten prompts from `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`

## 6. Extraction Design

This is a small targeted run, not a full 1200-rollout replication.

Planned design:

- 20 roles
- 2 conditions per role
- 5 system-prompt variants per role and condition
- 4 extraction questions per system prompt
- 20 rollouts per role per condition
- 40 rollouts per role total
- 800 total rollouts

Rollout pairs per condition:

- `sp_idx=0, q_idx=0-3`
- `sp_idx=1, q_idx=0-3`
- `sp_idx=2, q_idx=0-3`
- `sp_idx=3, q_idx=0-3`
- `sp_idx=4, q_idx=0-3`

This preserves the five-prompt structure from Lu et al. while keeping the question subset small and exactly matched across original and no-label conditions.

## 7. Output Schema

Recommended output directory:

`research/q2_stability/qwen/outputs/paper1_5/no_label_activation_stress_test/`

Recommended pod outputs:

- `no_label_activation_phase1.jsonl`
- `no_label_activation_phase1_manifest.json`
- `no_label_activation_phase1.log`
- `activations_no_label_stress_test/`

Each JSONL record should include:

- `role`
- `condition`
- `sp_idx`
- `q_idx`
- `question_id`
- `question`
- `system_prompt`
- `prompt_source`
- `generation_model`
- `script_author_model`
- `layer`
- `max_new_tokens`
- `response_text`
- `response_length_chars`
- `truncated`
- `think_artifact`
- `activation_saved`
- `activation_relpath`
- `created_at`

The manifest should include:

- selected role list
- condition list
- rollout pairs
- model name
- layer
- tokenizer/chat-template thinking-disable settings
- script git commit
- pod ID
- GPU type
- launch time
- output paths
- total expected rollouts

## 8. Integrity Plan

Local integrity checks should run only after the pod outputs have been copied back.

Required checks:

- 800 JSONL records
- 20 roles represented
- 2 conditions per role
- 20 records per `(role, condition)`
- 800 unique `(role, condition, sp_idx, q_idx)` tuples
- No missing system prompt text
- No missing response text
- `activation_saved=True` count equals JSONL count
- 800 activation shards exist locally
- Sampled activation tensors load as shape `[5120]`
- No literal `<think>` or `</think>` artifacts
- Truncation count recorded by role and condition
- Activation shards are gitignored and not staged

## 9. Comparison Metrics

Primary per-role comparisons:

- `cosine(original_condition_mean, Lu_reference_mean)`
- `cosine(no_label_condition_mean, Lu_reference_mean)`
- `cosine(original_condition_mean, no_label_condition_mean)`
- Change in cosine to Lu reference after label removal
- Change in nearest reference role among the selected role set
- Change in nearest activation cluster centroid among the seven Lu clusters, where local references are available
- Within-condition dispersion: cosine of each rollout activation to the condition mean
- Original-vs-no-label dispersion shift

Cross-role comparisons:

- Pairwise distance correlation between original and no-label role means
- Nearest-neighbor preservation among selected roles
- Cluster/basin preservation using selected-role activation reference profiles
- Role separability under original vs no-label conditions
- Whether bridge roles move more than stable anchors
- Whether assistant-adjacent roles move toward the assistant/procedural basin
- Whether theatrical roles remain separable without explicit labels

Optional scoring:

No scoring should run on the pod. If role-expression scoring is needed after integrity passes, use local Codex GPT-5.5 Standard scoring as an explicitly marked pragmatic judge, or use restored gpt-4.1-mini scoring only if the user chooses strict Lu-method comparison.

## 10. Competing Hypotheses

### H1: Activation geometry depends strongly on explicit lexical identity labels

Predictions:

- No-label vectors show large cosine drops relative to Lu reference means.
- Original-vs-no-label role means diverge substantially.
- Nearest-neighbor preservation falls sharply.
- Theatrical roles such as `trickster`, `jester`, and `oracle` lose separability.
- Bridge and sparse roles collapse toward generic assistant/procedural directions or become noisy.

Support for H1 would weaken claims that Lu-style activation geometry is recovered from behavioral elicitation alone. It would not invalidate the original method, but it would require describing the method as label-dependent role elicitation.

### H2: Activation geometry primarily tracks behavioral semantics independent of explicit labels

Predictions:

- No-label vectors remain close to Lu reference means for most roles.
- Original-vs-no-label role means remain close.
- Pairwise topology and nearest neighbors are largely preserved.
- Stable anchors and theatrical roles remain separable.
- Bridge roles do not move more than anchors except where the no-label rewrite removed essential behavioral content.

Support for H2 would show that explicit labels are not necessary for recovering at least local activation directions when behavioral descriptions remain intact.

### H3: Activation geometry reorganizes semantic behavioral structure into latent procedural or behavioral manifolds

Predictions:

- Some no-label vectors preserve reference directions while others reorganize.
- Stable anchors outperform bridge roles.
- Assistant-adjacent roles move toward the procedural/default assistant basin more than theatrical roles.
- Collective/swarm roles remain semantically coherent but distribute across activation basins.
- Bridge roles either snap into clear activation basins or show high dispersion.

Support for H3 would fit the current semantic-overlap findings: prompt-space semantics constrain the run, but activation space compresses, sharpens, or reorganizes those semantics around enacted behavioral stance.

## 11. Expected Outcomes Under Competing Interpretations

The strongest possible result for label independence would be high original-vs-no-label cosine and high Lu-reference cosine for `trickster`, `jester`, `screener`, `leviathan`, and at least one assistant-adjacent role. The strongest possible result for label dependence would be broad collapse across theatrical and stable-anchor roles after label removal. The most likely outcome based on prior work is mixed: high-yield theatrical anchors survive better than assistant-adjacent and bridge roles.

## 12. Runtime and Cost Estimate

The completed trickster Phase 1 run averaged about 27.5 seconds per rollout on an A100 80GB. This stress test plans 800 rollouts.

Estimated generation time:

- Raw rollout time: about 6.1 hours at 27.5 seconds per rollout
- Setup, model load, validation, preservation overhead: 0.5 to 1.5 hours
- Expected pod wall time: 7 to 8 hours

Estimated cost:

- A100 SXM 80GB at $1.49/hr: about $10 to $12
- A100 PCIe 80GB: similar or slightly lower/higher depending market price
- H100 PCIe under $2.50/hr: about $18 to $20 if used

Pod requirement:

- Minimum 80GB VRAM
- A100 SXM 80GB preferred
- A100 PCIe 80GB acceptable
- No spot instance
- No OpenAI API key on pod

## 13. Risks and Failure Modes

The largest methodological risk is that 20 rollouts per condition may be too few for low-yield roles. This is acceptable because this is a stress test, not a final extraction run. The design should identify whether the signal is obviously preserved, obviously label-dependent, or mixed enough to require a larger follow-up.

Other risks:

- No-label rewrites may preserve enough behavioral cues that role identity remains inferable.
- Some roles may have low role-expression yield even in the original condition.
- Assistant-adjacent roles may collapse toward generic assistant behavior in both conditions.
- Bridge roles may show high variance with small n.
- Deterministic first-four-question subset may bias results toward specific question styles.
- Higher token caps may be needed for some roles, though editor results suggest token cap alone does not guarantee role-expression recovery.

## 14. Success Criteria

The run is successful if:

- All 800 planned records are generated and preserved.
- All matching activation shards are preserved locally.
- Integrity checks pass.
- Original and no-label conditions are exactly paired by role, prompt index, and question index.
- At least the high-yield control roles produce analyzable no-label vectors.
- The comparison can classify each selected role as preserved, degraded, collapsed, or reorganized under label removal.

The run should not be considered a full Lu replication. It is a targeted methodological stress test.

## 15. Ready-to-Launch Status

The experiment is ready to launch after the user approves compute.

Required next implementation step:

Create a pod-run script based on the validated inference-only framework that reads `no_label_activation_stress_test_dataset_spec.json`, loads original and no-label prompts, generates the 800 planned paired rollouts, saves activation shards, writes the manifest, and stops after integrity-preservable outputs are complete.

Do not score on the pod. Do not continue beyond the 800 planned rollouts without a separate user instruction.
