# Run 2 No-Label Elicitation Validation Report

model_used: GPT-5.5

## 1. Motivation
Run 2 establishes a bare-Qwen baseline over the 240 extraction questions and tests revised no-label prompt manipulations against both the inherited assistant role centroid and the new bare-Qwen centroid.

## 2. Assistant Centroid Provenance Caveat
The assistant centroid used in prior Paper 1.5 analyses is the released role-conditioned `assistant` vector, not a bare-Qwen measurement. Run 2 therefore treats the 240-question bare-Qwen baseline as foundational for interpreting future no-label elicitation experiments.

## 3. Bare-Qwen Baseline Design
The baseline used all 240 canonical extraction questions with 5 samples each, for 1,200 generations. No role prompt, persona prompt, assistant-role system prompt, experiment explanation, PC label, or metadata was included in model-visible input. The model-visible message was one user message containing only the extraction question, aside from tokenizer/chat-template special tokens.

## 4. Full Run 2 Design
Catalog rows: 289. Planned generations: 1,690. Completed generations: 1690. Component totals are recorded in `run2_experiment_manifest.json` and verified in `run2_local_integrity_check.json`.

## 5. Blinding Verification
Qwen-visible messages were one user message containing only `prompt_text`; for baseline rows this was only the extraction question. Prompt IDs, PC labels, polarity labels, hypotheses, success criteria, metadata, reasoning, and geometry terminology were not model-visible. See `prompt_blinding_verification.md`.

## 6. Generation Independence Verification
Each sample was generated as a fresh one-message conversation. No prior user prompts, prior assistant responses, conversational history, or cross-sample KV cache were reused. Activation extraction used a separate no-cache forward pass over only the current generated sequence. See `generation_independence_verification.md`.

## 7. Integrity Summary
- Response rows: 1690
- JSONL rows: 1690
- Activation shards: 1690
- Error flags: 0
- Empty responses: 0
- Duplicate response IDs: 0
- Missing shards: 0

Status: pass.

## 8. Baseline Results
Bare-Qwen centroid over 240 x 5 responses: PC1=23.510, PC2=14.041, PC3=-2.460. Assistant role centroid: PC1=33.703, PC2=3.442, PC3=-5.156. The bare baseline is therefore lower on PC1, higher on PC2, and higher on PC3 than the released assistant role centroid.

## 9. Family Mean Results
| component | family | successful responses | bare dPC1 | bare dPC2 | bare dPC3 | assistant dPC1 | assistant dPC2 | assistant dPC3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| pc1_minimal_pairs | pc1_determination_vs_open_reflection | 100 | -5.563 | 4.502 | 18.750 | -15.756 | 15.101 | 21.445 |
| pc1_positive_replacement_family | pc1_positive_replacement_constrained_criteria | 100 | 4.025 | -1.290 | 28.480 | -6.168 | 9.309 | 31.175 |
| pc2_minimal_pairs | pc2_integrative_whole_vs_sensory_immediate | 100 | -46.163 | -2.580 | 2.149 | -56.356 | 8.019 | 4.844 |
| pc2_negative_replacement_family | pc2_negative_replacement_integrative_coherence | 100 | -15.860 | -15.849 | 2.172 | -26.053 | -5.249 | 4.868 |
| pc3_minimal_pairs | pc3_cost_to_others_vs_self | 90 | -53.306 | 16.791 | 0.298 | -63.499 | 27.390 | 2.994 |

## 10. Success Summary
- `pc1_positive_replacement_bare_qwen`: {'success_count': 7, 'prompt_count': 10, 'success_rate': 0.7, 'family_mean_delta': 4.0245442098132385, 'passed_70_percent_threshold': True}
- `pc1_positive_replacement_assistant`: {'success_count': 3, 'prompt_count': 10, 'success_rate': 0.3, 'family_mean_delta': -6.168321868552238, 'passed_70_percent_threshold': False}
- `pc2_negative_replacement_bare_qwen`: {'success_count': 9, 'prompt_count': 10, 'success_rate': 0.9, 'family_mean_delta': -15.848599645653156, 'passed_70_percent_threshold': True}
- `pc2_negative_replacement_assistant`: {'success_count': 8, 'prompt_count': 10, 'success_rate': 0.8, 'family_mean_delta': -5.249450203480705, 'passed_70_percent_threshold': True}
- `pc3_cost_to_others`: {'success_count': 3, 'complete_pair_count': 4, 'missing_or_incomplete_pair_count': 1, 'success_rate_complete_pairs': 0.75, 'passed_simple_majority_complete_pairs': True}
- `pc1_determination`: {'success_count': 1, 'complete_pair_count': 5, 'missing_or_incomplete_pair_count': 0, 'success_rate_complete_pairs': 0.2, 'passed_simple_majority_complete_pairs': False}
- `pc2_integrative_whole`: {'success_count': 5, 'complete_pair_count': 5, 'missing_or_incomplete_pair_count': 0, 'success_rate_complete_pairs': 1.0, 'passed_simple_majority_complete_pairs': True}

Primary replacement-family results relative to the bare-Qwen baseline: PC1+ replacement passed the preregistered 70% prompt-mean threshold with 7/10 prompt means moving positive on PC1; PC2- replacement passed with 9/10 prompt means moving negative on PC2. Relative to the assistant role centroid, PC1+ did not pass (3/10), while PC2- did pass (8/10).

Minimal-pair results: PC3 cost-to-others passed 3/4 complete pairs, with pair 1 intentionally missing side A because that side was inherited from Run 1; PC1 determination-vs-open-reflection passed only 1/5 pairs; PC2 integrative-whole-vs-sensory-immediate passed 5/5 pairs.

## 11. Pairwise Effects
| component | pair | contrast | status | target PC | target diff | success |
|---|---:|---|---|---|---:|---|
| pc3_minimal_pairs | pc3_pair_01 | B_minus_A | missing_side |  |  |  |
| pc3_minimal_pairs | pc3_pair_02 | B_minus_A | complete | PC3 | 7.8030429658667 | True |
| pc3_minimal_pairs | pc3_pair_03 | B_minus_A | complete | PC3 | -4.4745042803329715 | False |
| pc3_minimal_pairs | pc3_pair_04 | B_minus_A | complete | PC3 | 3.7367998161168465 | True |
| pc3_minimal_pairs | pc3_pair_05 | B_minus_A | complete | PC3 | 14.160446768799744 | True |
| pc1_minimal_pairs | pc1_pair_01 | A_minus_B | complete | PC1 | -10.618183110601505 | False |
| pc1_minimal_pairs | pc1_pair_02 | A_minus_B | complete | PC1 | 1.2896520964218414 | True |
| pc1_minimal_pairs | pc1_pair_03 | A_minus_B | complete | PC1 | -5.678484487813931 | False |
| pc1_minimal_pairs | pc1_pair_04 | A_minus_B | complete | PC1 | -13.495725071009732 | False |
| pc1_minimal_pairs | pc1_pair_05 | A_minus_B | complete | PC1 | -13.642787569459568 | False |
| pc2_minimal_pairs | pc2_pair_01 | B_minus_A | complete | PC2 | -12.03893101157335 | True |
| pc2_minimal_pairs | pc2_pair_02 | B_minus_A | complete | PC2 | -35.03654769679213 | True |
| pc2_minimal_pairs | pc2_pair_03 | B_minus_A | complete | PC2 | -21.476345168238538 | True |
| pc2_minimal_pairs | pc2_pair_04 | B_minus_A | complete | PC2 | -27.39457470364215 | True |
| pc2_minimal_pairs | pc2_pair_05 | B_minus_A | complete | PC2 | -29.102548382654447 | True |

## 12. Off-Axis Findings
Off-axis movement is recorded in `run2_off_axis_effects.csv`. The strongest broad off-axis patterns in the family means were large positive PC3 movement for PC1+ replacement and large negative PC1 movement for PC2 minimal pairs and PC3 minimal pairs relative to the bare baseline.

## 13. Interpretation
Observed: the bare-Qwen baseline is materially distinct from the released assistant role centroid. The PC2- replacement family and PC2 minimal pairs strongly support the revised integrative-whole manipulation relative to bare Qwen. The PC1+ replacement family succeeds relative to bare Qwen but not relative to the assistant role centroid, consistent with the assistant centroid already occupying a more positive-PC1 location than bare Qwen. PC1 minimal pairs mostly failed, indicating that simple directive-clause swaps do not reliably isolate positive PC1.

Inferred: future no-label validation should treat the bare-Qwen centroid as the default-behavior baseline and the released assistant centroid as a role/persona reference point, not as unconditioned Qwen.

Speculative: PC1 may require stronger scenario-level standard/certification structure rather than minimal directive swaps, and PC2 may be more cleanly steerable through whole-system/integrative prompts than through role-free PC1 criteria prompts.

## 14. Limitations
The run tests this exact prompt catalog, Qwen/Qwen3-32B, layer-48 direct hook extraction, response-token mean pooling, and the existing Qwen persona PCA basis. It does not prove axis semantics, isolate axes, or validate human psychology.

## 15. Recommendation for Paper 1.5 Inclusion
Use the 240-question bare-Qwen baseline as the default-behavior reference for Run 2 and future no-label elicitation comparisons. Include the PC2 replacement/minimal-pair result as stronger than the PC1 minimal-pair result, and report the assistant-centroid contrast explicitly.
