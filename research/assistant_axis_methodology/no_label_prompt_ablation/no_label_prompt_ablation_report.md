# No-Label Prompt Ablation Report

## Research Question

How much of the semantic structure of the original Lu et al. role-prompt corpus survives when explicit persona labels are removed while preserving wording, structure, and behavioral content as closely as possible?

## Why Label Exposure Matters

The label-exposure audit shows that the original Lu et al. role prompts contain extensive direct identity-label priming: 1280/1375 prompts, 93.1%, expose the target role label or a normalized variant. This means role-vector extraction is not purely behavioral elicitation. The no-label ablation asks whether the surrounding behavioral descriptions still preserve enough prompt-space structure to make a no-label activation stress test scientifically meaningful.

## Data Sources

The rewrite uses the canonical machine-readable prompt source at `data/roles/instructions/*.json`, with role descriptions from `data/roles/role_list.json`. It also uses the prior label-exposure audit at `research/assistant_axis_methodology/role_prompt_label_exposure_audit.json` to mark original exposure status. The readable prompt exports in `research/assistant_axis_methodology/prompts_and_questions/` were treated as reference material, not primary input.

## Rewrite Method

The rewrite harness `research/assistant_axis_methodology/scripts/rewrite_role_prompts_no_label_codex_gpt55.py` applies deterministic local transformations to all 275 role files. It removes explicit role labels and normalized variants while preserving behavioral content, stance, tone, and sentence structure as much as possible. No OpenAI API, pod, or external model was used.

The output dataset is `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`. It contains 1375 records, one for each role prompt, with original text, rewritten text, role label, exposure flags, rewrite status, and notes.

## Validation Results

Validation found all 1375 expected rewrites present, with zero missing records. No rewritten prompt retains exact or normalized target-role label exposure under the same conservative matcher used in the label-exposure audit. All records have `rewrite_status=ok`.

Length and lexical preservation remain high enough for a first ablation dataset. The median character length ratio is 0.842, the median word count ratio is 0.786, and the median lexical Jaccard similarity is 0.714. No records were flagged by the validation thresholds for possible over-flattening.

## Semantic Comparison Results

No local `sentence-transformers` or `scikit-learn` installation was available, so the semantic comparison uses a local TF-IDF representation with unigrams and bigrams plus NumPy SVD reduction. This is a prompt-space topology audit, not an activation-space test.

The original-to-rewritten prompt similarity is high. Prompt-level TF-IDF cosine has median 0.933. Role-level TF-IDF cosine has median 0.984. Role-level TF-IDF+SVD cosine has median 0.998. The pairwise role-space distance correlation after SVD is 0.985, and nearest-neighbor preservation is 0.924.

Discrete clustering is less stable than continuous topology. Original-vs-no-label clustering gives ARI 0.197 at k=5, 0.153 at k=7, and 0.181 at k=10, with NMI 0.260, 0.260, and 0.366 respectively. This suggests label removal preserves broad continuous semantic geometry better than it preserves hard cluster assignments produced by local k-means.

Comparison to existing activation-space labels from `visualizations/full_ranking.csv` remains exploratory. Prompt-space clusters only weakly align with activation-space cluster labels in both original and no-label conditions, so activation-space behavior cannot be inferred from prompt-space clustering alone.

## Roles Most Affected

The largest SVD displacements are small in absolute terms. The most changed roles are advocate, guardian, amateur, predator, familiar, wanderer, echo, warrior, mycorrhizal, and coral_reef. The largest SVD displacement is 0.065 for advocate, with SVD cosine 0.935.

Several roles are unchanged or nearly unchanged because their prompts either did not expose the normalized target label or already expressed the role through behavioral descriptions. Examples include addict, altruist, criminal, collaborator, cynic, devils_advocate, martyr, pragmatist, refugee, and retiree.

## Topology Preservation Judgment

The original prompt semantic topology is mostly preserved after label removal at the continuous role-space level. The high role-level cosine, high pairwise distance correlation, and high nearest-neighbor preservation indicate that much of the prompt-space structure is carried by behavioral descriptors, stance, and task framing rather than by the role labels alone.

The weaker k-means preservation means explicit labels still contribute materially to discrete prompt-space organization. This is not a contradiction: the continuous geometry can be stable while cluster boundaries move.

## Implications for Activation-Space Stress Tests

The no-label dataset is coherent enough to support a small activation-space stress test. The next test should not assume equivalence between original and no-label prompts. It should ask whether vectors extracted from no-label prompts still point toward the same Lu reference directions, and whether high-yield roles such as trickster remain separable when explicit labels are removed.

A minimal next experiment is a small no-label activation run for a mixed set of roles: trickster as a high-yield theatrical positive control, editor as an assistant-adjacent failure case, and one or two intermediate roles. The result should be interpreted as a stress test of label dependence, not as a replacement for the original Lu method.

## Limitations

The rewrite method is deterministic and conservative, not a human-polished semantic rewrite. Some prompts may still make the role inferable from behavioral descriptors, which is allowed by design. Removing labels does not remove role identity from the text; it removes explicit lexical title exposure. The semantic comparison uses TF-IDF/SVD fallback rather than sentence embeddings, so it is sensitive to lexical overlap and cannot fully measure paraphrastic equivalence. Most importantly, prompt-space preservation does not imply activation-space preservation.

## Recommended Next Step

Run a small activation-space no-label stress test before scaling. If no-label vectors still align with Lu reference directions for at least a high-yield role, then compare assistant-adjacent roles under original versus no-label prompts. If no-label vectors fail even for high-yield roles, refine the rewrite method or treat explicit label priming as a necessary part of the Lu-style elicitation design.
