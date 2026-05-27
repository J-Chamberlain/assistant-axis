# Role Vector Structure Audit

This audit documents the locally downloaded `lu-christina/assistant-axis-vectors` tensor structure and the implications for current replication work.

## Downloaded Tensor Layout

| Model directory | Role tensor shape | Assistant/default shape | Hidden size | Layer count | Notes |
|---|---:|---:|---:|---:|---|
| `downloads/hf_vectors/gemma-2-27b/` | `[46, 4608]` | `[46, 4608]` | 4608 | 46 | Includes role vectors, trait vectors, `assistant_axis.pt`, and `default_vector.pt` |
| `downloads/hf_vectors/qwen-3-32b/` | `[64, 5120]` | `[64, 5120]` | 5120 | 64 | Includes role vectors, trait vectors, `assistant_axis.pt`, `default_vector.pt`, and `capping_config.pt` |
| `downloads/hf_vectors/llama-3.3-70b/` | `[80, 8192]` | `[80, 8192]` | 8192 | 80 | Includes role vectors, trait vectors, `assistant_axis.pt`, `default_vector.pt`, and `capping_config.pt` |

The downloaded role-vector files inspected locally are raw PyTorch tensors, not dictionaries with embedded prompt, score, or category metadata. This differs from the local `pipeline/4_vectors.py` save path, which writes dictionaries containing `vector`, `type`, and `role`.

## Naming Conventions

Role vectors live under `role_vectors/{persona}.pt`. Trait vectors live under `trait_vectors/{trait}.pt`. Assistant/default files are top-level model files named `assistant_axis.pt` and `default_vector.pt`. Persona names use lowercase snake_case when needed, for example `devils_advocate.pt`.

## Layer Indexing

Local extraction code indexes transformer blocks with zero-indexed Python indices, for example `model.model.layers[48]` captures the 49th decoder block output. Local model configs list total layers as 46 for Gemma, 64 for Qwen, and 80 for Llama. The downloaded tensors store one vector per layer.

## Residual Position

The activation extractor hooks the full decoder block output rather than an attention-only or MLP-only submodule. For a standard transformer decoder block, this corresponds to the post-MLP residual stream output. This matches the paper's stated post-MLP residual-stream convention.

## Normalization

The stored vectors are not unit-normalized. Sample norm means are far from 1: Gemma vectors are around 19k in norm, Qwen vectors around 292-303, and Llama vectors around 10.4-10.8. Downstream cosine comparisons normalize implicitly at comparison time.

## Fully-Roleplayed vs Somewhat-Roleplayed Storage

The paper distinguishes fully role-playing and somewhat role-playing vectors. The inspected local HF tensor files do not include metadata indicating whether a given downloaded tensor is fully-role-playing, somewhat-role-playing, merged, or fixed-capped after a separate selection step. A prior tensor row-count audit found Qwen role tensors appear as fixed `[64, 5120]` layer matrices, supporting a storage convention rather than direct per-role elicitation yield. This remains an unresolved metadata limitation.

## Model Differences

Gemma, Qwen, and Llama artifacts differ in layer count, hidden size, and assistant-axis geometry. Current local research finds Qwen and Llama persona rankings converge strongly while Gemma diverges. This is relevant because several earlier Q2 persona representatives were Gemma-derived and later corrected with Qwen-native centroid lookup.

## Assistant/Default Representation

`default_vector.pt` stores the default Assistant vector by layer. `assistant_axis.pt` stores the Assistant Axis by layer. The local README and `pipeline/5_axis.py` define the axis as `mean(default_vectors) - mean(role_vectors)`.

## Separability and Assistant Adjacency

Theatrical or strongly marked personas such as trickster show high role-expression yield and stable recovery in local Qwen replication. The trickster score>=2 candidate vector reaches cosine 0.957557 to the Lu Qwen trickster mean using 64 Codex-scored responses, with adaptive stopping passing at n=16. Assistant-adjacent personas such as editor are harder to separate behaviorally: the first Qwen editor chunk produced only 10 score>=2 and 3 score==3 responses out of 128, and matched 1024-token regeneration did not improve role-expression yield. This suggests editor collapse is more likely an anchoring/assistant-basin overlap problem than a token-cap problem.

## Missing or Inconsistent Metadata

No local metadata file in `downloads/hf_vectors/` specifies the exact system prompt, judge category, response IDs, or filter category used for each downloaded role vector. The prompt and question text exists under `data/roles/instructions/` and `data/extraction_questions.jsonl`, but it is not linked record-by-record to the HF tensors in local metadata.
