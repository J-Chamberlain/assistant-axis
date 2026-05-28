# Findings Ledger

This is a compact index of project claims and their status. Use `research/RESEARCH_STATE.md` for full history and exact supporting paths.

## Confirmed Findings

### Careful Evaluator Finding

Gemma 2 27B's assistant axis is dominated by evaluative roles, especially proofreader, screener, grader, and editor. `assistant` ranks 45th out of 275 on the assistant axis, and the top pole correlates strongly with conscientiousness and negatively with psychopathy.

### Base Model Basin Finding

The careful-evaluator basin appears in Gemma 2 27B base model behavior, not only in instruction-tuned behavior. This supports the interpretation that the geometry reflects pretraining distribution structure as well as post-training.

### Qwen/Llama Convergence and Gemma Divergence

Qwen 3 32B and Llama 3.3 70B converge strongly on persona rankings, while Gemma diverges. This matters for any claim that transfers cluster representatives from Gemma into Qwen without Qwen-native validation.

### Trickster Adaptive Extraction Success

Qwen/Qwen3-32B trickster Phase 1 completed 1200 rollouts and 1200 activation shards with final integrity passed. Codex GPT-5.5 Standard adaptive scoring reached 64 score>=2 and 33 score==3 responses in 64 scored records. The score>=2 vector matched the Lu trickster reference mean at cosine 0.957557, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets.

### Pod Workflow Lessons

Detached execution, response JSONL preservation, separate activation shards, local integrity checks, explicit run artifacts, and RunPod API or `runpodctl` termination are now validated workflow requirements. Browser/dashboard termination is fallback only.

## Negative Findings

### Gemma Emotion PCA Gate Failure

Gemma 2 27B failed the Anthropic/Sofroniew emotion-vector PCA gate at tested layers. This is a negative result for dominant-PC emotion geometry in Gemma at this scale, though distributed emotion structure remains a separate possibility.

### Editor Adaptive Extraction Failure

The first Qwen editor adaptive extraction chunk did not meet validation thresholds. The 128-record 512-token run produced only 10 score>=2 and 3 score==3 responses, so vector validation and sample sufficiency were correctly not run.

### Token-Cap Sensitivity Result for Editor

The matched first-64 editor rerun at 1024 tokens reduced truncation from 50/64 to 5/64, but score>=2 and score==3 counts did not improve. Token cap alone does not explain editor's low role-expression yield.

### Forced Manual Cap Pilot Failure

The forced manual cap pilot froze geometry despite zero leakage, with post-T3 trickster cosine variance at 0.00e+00. It should not be treated as a valid stabilizing result.

## Provisional Interpretations

### Assistant-Adjacent Collapse

Editor weakness may reflect collapse toward generic assistant behavior for assistant-adjacent personas under the current Lu-style extraction setup. This is plausible but still provisional because only one editor chunk and one matched token-cap follow-up have been tested.

### Adaptive Extraction Generality

Adaptive extraction is operationally validated for trickster but not yet generally validated across persona types. It should be treated as a workflow candidate pending additional high-yield, mid-yield, and assistant-adjacent persona tests.

### Cluster Motivational Structure

Six of seven clusters have dialogue-derived motivational characterizations. These are useful for hypothesis generation and Paper 1.5 framing, but empirical verification remains pending.

## Methodological Deviations

### Role-Prompt Label Exposure

The Lu et al. role system prompts contain extensive direct identity-label exposure. A local audit of 275 role files found 1280/1375 prompts, 93.1%, expose the target role label or a normalized variant, and 227/275 roles have 5/5 prompt exposure. This means the elicitation design should be described as role-label-plus-behavior elicitation rather than purely behavioral elicitation; it does not by itself show that activation geometry is invalid or reducible to labels.

### No-Label Prompt Ablation

A deterministic no-label prompt-ablation dataset now exists for all 1375 Lu et al. role prompts. Validation found zero remaining normalized target-label exposure, median character length ratio 0.842, median lexical Jaccard 0.714, and no over-flattening flags. Offline TF-IDF/SVD comparison found continuous prompt-space topology is largely preserved after label removal, with role-level SVD cosine median 0.998, nearest-neighbor preservation 0.924, and pairwise distance correlation 0.985, while hard k-means cluster assignments are much less stable.

### Semantic vs Activation Geometry

Three-way comparison of role-name, original-prompt, no-label prompt, and available activation-reference geometry finds that semantic topology is preserved strongly between original and no-label prompt spaces, but activation cluster structure is only partially recoverable from semantics. At k=7, ARI against activation labels is 0.010 for role names, 0.023 for role names plus descriptions, 0.111 for original prompts, and 0.130 for no-label prompts. No-label prompt distances best predict available activation centroid-profile distances, but correlations remain modest: 0.230 for Gemma and 0.254 for Qwen.

### Semantic Role Manifold Interpretation

The Lu et al. role corpus now has a standalone interpretation as a frontier-model-generated semantic role manifold. It contains meaningful prompt-space topology before activations are considered, and that topology mostly survives label removal. The current interpretation is that activation experiments test how target models internalize, compress, sharpen, or reorganize this semantic manifold rather than revealing a structure independent of the elicitation corpus.

### Deep Semantic Topology

A deeper no-label semantic topology analysis found that the role corpus is organized by mixed social, professional, narrative, stylistic, and archetypal structure rather than by a single psychological taxonomy. The no-label k=7 semantic manifold shows broad professional/helper, lived-experience/social, communicative/media, mythic/fantastical, adversarial/normative, and generalist/helper regions, with soft boundaries and bridge roles such as spy, amnesiac, sage, guardian, merchant, and emissary. Dense pockets include professional and migration/survival neighborhoods; sparse roles include flaneur, predator, devils_advocate, advocate, teenager, vegan, genie, angel, robot, and adolescent. This supports treating the role list as a constructed semantic manifold whose topology partially constrains, but does not determine, activation geometry.

### Semantic-Activation Overlap Structure

Structured overlap analysis between activation clusters, original prompt clusters, and no-label prompt clusters found 73 stable anchor roles and 198 bridge or migratory roles under broad overlap criteria. Editorial is the cleanest semantic-activation overlap region, while procedural-professional compresses several semantic regions into one broad activation basin. Collective/swarm roles are semantically compact but distributed across larger activation clusters rather than forming a dedicated activation cluster in the available labels. This supports the interpretation that activation geometry preserves local semantic anchors while reorganizing broad prompt-space topology around enacted behavioral structure.

### No-Label Activation Stress Test Design

The first no-label activation-space stress test is designed but not launched. It selects 20 roles covering stable anchors, bridge/migratory roles, sparse/outlier roles, assistant-adjacent/procedural roles, theatrical/fantastical roles, and collective/swarm roles: editor, screener, reviewer, consultant, evaluator, proofreader, negotiator, trickster, jester, oracle, leviathan, mystic, hive, egregore, skeptic, philosopher, spy, dilettante, flaneur, and robot. The design uses paired original label-exposed and no-label conditions with 20 rollouts per role per condition, for 800 planned Qwen/Qwen3-32B layer-48 rollouts. The only intended experimental difference is system prompt label exposure.

### Codex GPT-5.5 Judge Substitution

The Lu et al. path uses `gpt-4.1-mini` as the role-expression judge. Current trickster and editor adaptive scoring used Codex GPT-5.5 Standard as a pragmatic substitute. This must be disclosed and should not be described as strict Lu-method replication.

### Adaptive Stopping

The project now uses an adaptive extraction protocol for operational efficiency. The provisional rule is 64 qualifying responses as a conservative target, with adaptive stopping permitted once convergence criteria pass at n>=16. This is a methodological extension beyond the fixed Lu-style rollout framing.

### Chunked Generation

Editor was tested with a 128-rollout chunk rather than a full 1200-rollout run. This was intentional for the second-persona generalization test and should not be conflated with exhaustive Lu-style extraction.

### Truncation as Covariate

High truncation is tracked explicitly rather than silently filtered. Trickster truncation did not materially destabilize geometry; editor token-cap results suggest truncation reduction does not necessarily improve role-expression yield.

### Claude Latent Feature Discovery Loop (2026-05-28)

Claude Code independently ran the latent feature discovery loop using existing local
artifacts only (no pods, no new inference). Key results:

- Pseudo-PCA3D target: PCA on 275×7 Qwen cluster-cosine matrix (95.5% cumulative EV).
- Null baseline (permutation, n=200): PCA3D R² mean=-0.322, p95=-0.221.
- TF-IDF semantic baseline: PCA3D R²=0.142, Gemma axis R²=0.452.
- Best model (TF-IDF + BigFive): PCA3D R²=0.361, Gemma axis R²=0.695. Improvement +0.219.
- PC1 R²=-0.089 (unpredicted); PC2 R²=0.732; PC3 R²=0.440.
- Plateau triggered at round 3; DarkTriad and semantic cluster membership add no signal beyond BigFive.
- Best-explained roles: procedural_professional archetypes (architect, journalist, paramedic, marketer).
- Worst-explained: "other" cluster developmental stages (toddler, caveman, infant, teenager), editorial outlier (proofreader).
- Codex/GPT-5.5 results not found in repository; direct comparison deferred.
- Artifacts: `research/q2_stability/qwen/outputs/claude_latent_feature_loop/`

### BigFive as Dominant Explanatory Framework (provisional, 2026-05-28)

BigFive psychological traits (literature-derived, LLM-assigned during Paper 1) are
the single most predictive feature set for PC2 and PC3 of the Qwen cluster-cosine
space and for the Gemma assistant axis (R²=0.695). DarkTriad adds no independent
signal. Semantic cluster membership adds no signal beyond BigFive. This supports
treating BigFive as the primary psychological lens for activation geometry, though
it does not establish that the geometry is truly psychological (the BigFive profiles
were assigned by LLM and may reflect the assigning model's stereotypes).

### PC1 of Qwen Cluster-Cosine Space is Not Explained by Available Features (RETRACTED TARGET-SPECIFIC CLAIM, 2026-05-28)

The pseudo-PCA PC1 failure (R²=-0.089) was target-specific: on the canonical Qwen
activation PCA, BigFive explains PC1 R²=0.734. The pseudo-PCA PC1 (derived from
275×7 cosine-matrix PCA) captured cosine-magnitude structure not present in the
canonical activation PCA. The general claim that "PC1 is unexplained by human-legible
features" does not hold for the canonical activation target.

### Cross-Model Convergence: BigFive Outperforms Codex on Canonical Target (confirmed, 2026-05-28)

BigFive psychological traits (5-dim, LLM-assigned) achieve R²=0.613 on canonical Qwen
activation PCA (N=273), outperforming Codex/GPT-5.5's 31 behavioral/motivational
dimensions (R²=0.490) by +0.123. Both feature sets outperform the semantic cluster
baseline (R²=0.389). Per-axis: BigFive PC1=0.734 vs Codex PC1=0.631; BigFive
PC2=0.480 vs Codex PC2=0.257; PC3 is essentially tied (BigFive 0.415, Codex 0.422).
Critical caveat: BigFive scores were LLM-assigned and may share priors with activation
geometry; the advantage is real but may be partially circular.
Artifact: `research/q2_stability/qwen/outputs/claude_latent_feature_loop/claude_on_shared_benchmark_report.md`

### Claude Procedural Replication: Evaluation Dominates Under Operating-Mode Constraint (confirmed, 2026-05-28)

Claude constrained to 20 procedural/operating-mode dimensions (no BigFive) retained 3:
evaluation, guidance, care — reaching R²=0.4139 on canonical Qwen activation PCA.
All 20 dims together ceiling at R²=0.4148 (keyword saturation). Codex procedural R²=0.490.
Key convergence: both independently selected evaluation/verify/audit as the primary retained
procedural dimension. Key divergence: Claude reaches a keyword ceiling at ~0.41 that Codex
surpasses because its 31-dim vocabulary is richer and less sparse.
Developmental/other cluster remains worst-explained under procedural constraint as well.
Artifact: `research/q2_stability/qwen/outputs/claude_procedural_replication/`

### Developmental Personas Are Hardest to Explain Across Both Models (confirmed, 2026-05-28)

6 personas appear in both Claude's and Codex's worst-explained lists: toddler, caveman,
infant, teenager, poet, procrastinator. These are roles without coherent adult trait
profiles (developmental stages) or roles with idiosyncratic activation geometry. This
convergence holds across different targets and different feature generation methods,
making it the strongest qualitative cross-model finding. Procedural-professional cluster
is the best-explained basin under both models.
Artifact: `research/q2_stability/qwen/outputs/claude_latent_feature_loop/claude_on_shared_benchmark_report.md`

## Current Blockers

The next editor experiment is blocked on revised anchoring methodology. More identical editor rollouts are unlikely to answer the failure mode cleanly.

Strict Lu-method replication remains blocked unless `gpt-4.1-mini` judge scoring is restored and run with documented filter choices.

Evaluator-sensitivity comparison remains blocked by OpenAI API quota. The local harness, canonical corpora mapping, Codex-side imported baseline, and output schema now exist under `research/q2_stability/qwen/evaluator_sensitivity/`, but `gpt-4.1-mini` returned `insufficient_quota` and produced zero paired judge records.

Downloaded Lu vector metadata remains underspecified locally: the exact fully-roleplaying versus somewhat-roleplaying storage category and fixed 64-row selection procedure are not documented in local HF metadata.

## Next Empirical Tests

1. Design a revised editor anchoring methodology that can test assistant-adjacent role extraction without immediate collapse into generic assistant behavior.
2. Run at least one additional non-trickster persona adaptive extraction after the revised methodology is specified.
3. Restore or compare `gpt-4.1-mini` scoring if API access permits, to estimate judge sensitivity relative to Codex GPT-5.5 Standard.
4. Test whether cluster-synthesized background prompts improve low-yield persona anchoring without leaking role identity.
5. Launch the bounded 800-rollout no-label activation-space stress test once compute is approved.
6. Continue Paper 1.5 validation before relying on adaptive extraction as a general persona-vector workflow.
7. ~~Push Codex/GPT-5.5 latent feature loop reports to the repo so Claude-vs-Codex cross-model comparison can be completed.~~ DONE: comparison complete in `claude_on_shared_benchmark_report.md`.
8. Disambiguate Qwen PC1: canonical PC1 is well-predicted by BigFive (R²=0.734); pseudo-PCA PC1 failure was target-specific. Remaining open: does canonical PC1 correspond to the Qwen assistant axis direction? Direct projection comparison (requires torch) would confirm.
9. Test Claude's 10 hypothesized binary dimensions independently as a targeted feature block (separate from the BigFive-dominated loop).
10. Test whether BigFive + TF-IDF (combined) improves further over BigFive alone on canonical activation PCA (the transfer analysis only tested BigFive-only).
