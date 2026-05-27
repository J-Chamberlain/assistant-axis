# Current Semantic Geometry Findings Recap

## 1. What Has Been Tested

The current semantic-geometry investigation has tested four linked questions. First, whether the Lu et al. role system prompts explicitly expose target role labels. Second, whether a no-label prompt-ablation dataset can remove those labels while preserving behavioral content. Third, whether original and no-label prompt spaces preserve the same semantic topology. Fourth, whether role-name, original-prompt, and no-label prompt semantic geometries predict available activation-space structure.

This work uses the canonical Lu et al. role files in `data/roles/instructions/*.json`, the role list in `data/roles/role_list.json`, the no-label ablation outputs in `research/assistant_axis_methodology/no_label_prompt_ablation/`, and activation-reference labels/profiles from `visualizations/full_ranking.csv` and `research/cluster_analysis/*_cluster_directionality.csv`.

The investigation also sits next to the adaptive extraction results. Trickster validates the current adaptive extraction workflow operationally. Editor fails the same workflow under the first chunk, and the matched 1024-token run shows that token cap alone does not explain the low editor yield.

## 2. What Has Been Validated

The label-exposure audit validates that direct identity-label priming is pervasive in the Lu prompt corpus. Of 1375 role prompts, 1280, or 93.1%, expose the target role label or a normalized variant. At the role level, 227/275 roles have complete 5/5 prompt exposure.

The no-label ablation dataset validates cleanly as a controlled prompt artifact. It contains 1375/1375 expected rewrites, with zero remaining normalized target-label exposure under the audit matcher. Median character length ratio is 0.842, median word count ratio is 0.786, and median lexical Jaccard is 0.714. No records are flagged for over-flattening by the validation thresholds.

Continuous semantic topology survives label removal. Original and no-label prompt spaces have distance correlation 0.956 in the three-way comparison. The prior original-vs-no-label comparison gives role-level SVD cosine median 0.998, nearest-neighbor preservation 0.924, and pairwise distance correlation 0.985.

Prompt semantics predict activation references better than role names alone, but only weakly to modestly. At k=7, ARI against activation labels is 0.010 for role names, 0.023 for role names plus descriptions, 0.111 for original prompts, and 0.130 for no-label prompts. No-label prompt distances best predict available activation centroid-profile distances, with correlations 0.230 for Gemma and 0.254 for Qwen.

## 3. What Has Been Ruled Out

The activation-space cluster structure is not recoverable from role names alone. Name-only geometry is too thin to explain the seven-cluster structure.

The no-label ablation does not collapse the prompt corpus into semantic noise. Removing explicit labels leaves a coherent prompt-space topology.

The editor failure is not explained by token cap alone. In the matched first-64 editor comparison, increasing the cap from 512 to 1024 sharply reduces truncation, but score>=2 and score==3 counts do not improve.

The current evidence does not support saying activation geometry is "just semantics." Semantic agreement with activation clusters is limited, and activation-space structure appears to reorganize semantic priors rather than merely mirror them.

## 4. What Remains Uncertain

The no-label prompt-space result does not prove no-label activation-space survival. A prompt can remain semantically coherent while failing to elicit the same internal direction in Qwen or Gemma.

Evaluator effects remain unresolved. Codex GPT-5.5 Standard scoring is a pragmatic substitute, not strict Lu-method `gpt-4.1-mini` replication.

The downloaded Lu vector tensors still lack local metadata resolving exactly how fully role-playing, somewhat role-playing, merged, or capped samples are represented.

The editor failure remains ambiguous. It may reflect assistant-adjacent collapse, insufficient anchoring, question-set mismatch, evaluator conservatism, or some combination.

## 5. Current Leading Interpretation

The best current interpretation is interactional. The role inventory and prompts create a structured semantic prior: a frontier-model-generated role manifold with strong identity-label exposure and rich behavioral descriptions. The no-label ablation shows that much of this semantic topology is carried by behavioral wording, stance, and task framing rather than by labels alone.

Activation geometry appears to preserve some of that semantic topology while reorganizing it through model-specific representational structure. This is visible in the weak-to-modest semantic prediction of activation labels and centroid profiles, plus the fact that original and no-label prompt spaces remain close while activation-cluster agreement remains limited.

This interpretation separates four things that should not be conflated: semantic topology in the prompt corpus, activation geometry in a target model, prompt artifacts such as label exposure, and evaluator effects from role-expression scoring.

## 6. Immediate Next Experiments

The next empirical test should be a small no-label activation-space stress test. Use a mixed role set: trickster as a high-yield theatrical positive control, editor as an assistant-adjacent failure case, and one or two intermediate roles. Compare no-label extracted vectors against Lu reference vectors and original-prompt behavior.

Do not scale to a full 1200-rollout no-label extraction yet. The correct next step is a bounded stress test that asks whether activation directions survive label removal at all.

Separately, design a revised editor anchoring methodology. More identical editor rollouts are unlikely to isolate the failure mode.

## Compact Table

| Finding | Current status | Key statistic |
|---|---|---:|
| Label exposure is pervasive | confirmed | 1280/1375 prompts, 93.1% |
| No-label dataset validates | confirmed | 1375/1375 rewrites, 0 normalized label exposures |
| Original/no-label topology survives continuously | confirmed prompt-space result | distance correlation 0.956 |
| Hard semantic clusters shift after label removal | confirmed prompt-space result | k=7 ARI 0.153 in prior no-label comparison |
| Semantic spaces partly predict activation labels | confirmed but modest | original k=7 ARI 0.111, no-label k=7 ARI 0.130 |
| No-label prompt distances best predict activation profiles | confirmed but modest | Gemma 0.230, Qwen 0.254 |
| Trickster adaptive extraction works | operationally validated | cosine 0.957557 to Lu mean |
| Editor adaptive extraction fails first chunk | negative result | 10 score>=2, 3 score==3 out of 128 |
