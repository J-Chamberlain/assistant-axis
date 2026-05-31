# Activation Methodology Verification

## Direct Answer

No blocking discrepancy was found in the local H100 runner or projection debug artifacts. The PCA projection convention is strongly verified by max absolute coordinate reproduction error 1.207e-06 against committed canonical coordinates. However, D01 remains `in_progress`, not resolved, because the exact upstream Assistant Axis extraction loop, layer-index convention, and chat-template convention were not independently compared line by line.

| check | expected | observed | status | evidence/caveat |
|---|---|---|---|---|
| Model identifier | Qwen/Qwen3-32B | `Qwen/Qwen3-32B` | matched | Run config and runner constant match. |
| Layer index | Qwen layer 48 hidden state | `48` | partially verified | Runner uses out.hidden_states[LAYER]; local ActivationExtractor indexes model_layers[layer_idx] with hooks, so hidden_states-vs-module index equivalence needs source-pipeline confirmation. |
| Representation | post-MLP residual / hidden-state vector | `transformers output_hidden_states hidden state` | partially verified | Methodology notes describe mean post-MLP residual activations; H100 used output_hidden_states rather than the local hook extractor, likely equivalent to layer output but not proven line-by-line. |
| Pooling | mean over response tokens only | `hidden[:, prompt_len:, :].mean(axis=0)` | matched in runner | Prompt tokens excluded after chat-template prompt_len. |
| Chat template | Qwen chat template with generation prompt | `tokenizer.apply_chat_template(... add_generation_prompt=True, enable_thinking=False)` | matched to run design | Source Assistant Axis generation template not directly verified. |
| PCA basis | loaded/reconstructed, not refit on prompts | `reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment` | matched | Basis reconstructed from 275 role vectors; prompt observations projected into this basis. |
| Preprocessing | mean centering, no standardization/L2 | `project_activation subtracts role-vector mean and dots components` | matched to reproduced coordinates | Reproduction error is the strongest evidence for preprocessing match. |
| Sign convention | canonical committed coordinates | `[-1.0, 1.0, -1.0]` | matched | Sign aligned to canonical PCA CSV. |
| PCA reproduction | near-exact reproduction | `1.2070328558877463e-06` | matched | Max abs reproduction error 1.207e-06 over 273 committed coordinates. |
| Source code comparison | assistant_axis/pca.py, internals/activations.py, replication_differences_vs_lu.md | `local source inspected` | partial | Local utility supports mean centering and response-span pooling; local extractor prefers hooks while H100 runner used output_hidden_states. |

## Unresolved Methodological Discrepancies

- Hidden-state index convention is internally consistent but still needs upstream source comparison for whether layer 48 refers to `hidden_states[48]`, hooked module index 48, or another block convention.
- The source Assistant Axis chat template / prompt wrapper used to produce released vectors was not directly verified in this pass.
- Local methodology notes describe mean post-MLP residual activations; the H100 runner used `output_hidden_states=True` rather than the local hook-based `ActivationExtractor.batch_conversations()` path. This is not yet shown to explain the PC2 shift, but it remains a live implementation-equivalence check.

Confidence level: medium-high for PCA projection convention; medium for full activation-extraction equivalence.
