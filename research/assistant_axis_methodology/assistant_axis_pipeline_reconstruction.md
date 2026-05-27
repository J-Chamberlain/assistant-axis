# Assistant Axis Pipeline Reconstruction

This document reconstructs the Lu-style methodology from the paper text, local repo scripts, prompt files, and downloaded vector artifacts. It separates explicitly stated paper details from behavior inferred from code or this project's replication scripts.

## 1. Persona List Generation

The paper states that Claude Sonnet 4 generated a diverse list of 275 roles and personas. The local canonical list is `data/roles/role_list.json`, which contains 275 entries. This step is explicitly stated in paper Section 2.1.1 and represented locally by the role list JSON.

## 2. Frontier-Model Role Prompt Generation

The paper states that the same frontier model generated five distinct system prompts per role. The local canonical prompt files are under `data/roles/instructions/`; each role JSON contains `instruction`, a list of five `pos` prompts. This is explicitly stated in paper Section 2.1.1 and preserved exactly in `research/assistant_axis_methodology/prompts_and_questions/canonical_system_prompts.md`.

## 3. Extraction Question Generation

The paper states that 240 general extraction questions were generated. The local canonical file is `data/extraction_questions.jsonl`, with 240 JSONL records containing `question` and `id`. This is explicitly stated in paper Section 2.1.1 and exported to `canonical_extraction_questions.md`.

## 4. Number of System Prompts per Role

There are five system prompts per role. Code source: `pipeline/1_generate.py` defaults `prompt_indices=list(range(5))`, and each role JSON under `data/roles/instructions/` contains five `instruction[].pos` strings. Paper source: Section 2.1.1.

## 5. Number of Extraction Questions

There are 240 extraction questions. Code source: `pipeline/1_generate.py` defaults `question_count=240`. Data source: `data/extraction_questions.jsonl` has 240 records. Paper source: Section 2.1.1.

## 6. Rollout Combinatorics

The extraction design is all five system prompts crossed with all 240 questions, for 1200 responses per role. The default Assistant baseline uses the same 240 questions with five default conditions: four normal-behavior system prompts plus one no-system-prompt condition, also yielding 1200 responses. Paper source: Section 2.1.2. Code source: `pipeline/1_generate.py` and `assistant_axis/generation.py`.

## 7. Models Evaluated

The paper studies open-weight dense transformer models and names Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B. The local config source is `assistant_axis/models.py`, which defines `google/gemma-2-27b-it`, `Qwen/Qwen3-32B`, and `meta-llama/Llama-3.3-70B-Instruct`. The paper limitations section states that reasoning mode is disabled for Qwen.

## 8. Layers Used

The paper says analyses generally use the middle residual stream layer unless otherwise specified. Local configs in `assistant_axis/models.py` define target layers as Gemma layer 22 of 46, Qwen layer 32 of 64, and Llama layer 40 of 80. The downloaded HF vectors store all layers, not only the target layer. This project's Paper 1.5 replication uses Qwen layer 48 because current Qwen dyad/calibration work and the preserved Phase 1 activation path target layer 48. That is a local replication choice, not the generic local config target layer.

## 9. Activation Extraction

The code extracts activations with forward hooks rather than relying on `output_hidden_states`. Source: `assistant_axis/internals/activations.py`. Hooks are registered on full transformer blocks from `ProbingModel.get_layers()`, which returns `model.model.layers` for Gemma, Qwen, and Llama in `assistant_axis/internals/model.py`.

## 10. Residual Stream Position

The paper states mean post-MLP residual stream activations at all response tokens are used. The local hook is attached to the full decoder block output, not to an attention or MLP submodule, so the captured tensor is the post-MLP residual stream output of that block. Source: paper Section 2.1.2 and `assistant_axis/internals/activations.py`.

## 11. Token Averaging

The paper states that vectors are formed from mean post-MLP residual stream activations at all response tokens. The local implementation maps assistant spans with `SpanMapper.map_spans` and averages the assistant response-token activations. Sources: paper Section 2.1.2, `pipeline/2_activations.py`, and `assistant_axis/internals/activations.py`.

## 12. Role-Expression Filtering

The paper says responses are filtered for sufficient role expression, with fully role-playing and somewhat role-playing responses treated separately. It also says roles are kept if they have at least ten responses in at least one category. Local `pipeline/4_vectors.py` defaults to `min_count=50` and constructs ordinary role vectors from score-3 activations only, while treating default vectors separately. This is an important paper-vs-code ambiguity: the paper-level inclusion threshold and the pipeline script default are not identical in the inspected local code.

## 13. Judge Model

The paper and local code identify `gpt-4.1-mini` as the role-expression judge. Sources: paper Section 2.1.1, `pipeline/3_judge.py`, and `assistant_axis/judge.py`. This project's trickster and editor adaptive extraction used Codex GPT-5.5 Standard as a pragmatic substitute when API quota blocked gpt-4.1-mini scoring; this is a replication difference, not Lu-method identity.

## 14. Judge Label Categories

The paper names three categories: fully role-playing, somewhat role-playing, and no role-playing. The local pipeline rubric operationalizes integer scores 0-3: 0 and 1 are non-role-playing variants, 2 is somewhat role-playing, and 3 is fully role-playing. Sources: paper Section 2.1.1, `pipeline/README.md`, and role-specific `eval_prompt` fields exported in `canonical_judge_prompt.md`.

## 15. Thresholds for Qualifying Responses

Paper threshold: keep roles with at least ten responses in at least one role-expression category. Pipeline default: `pipeline/4_vectors.py` uses `min_count=50` when aggregating score-3 activations. Downloaded HF vectors are fixed-size tensors by role and layer, and the inspected local files do not include enough metadata to reconstruct exact per-role yield thresholds for the published HF artifact. This remains partially underspecified locally.

## 16. PCA Methodology

The paper standardizes role vectors by subtracting the mean role vector and performs PCA on the centered vectors. It reports n=377 to 463 vectors depending on model after filtering. Code source: `assistant_axis/pca.py`, especially `MeanScaler` and `compute_pca`. Paper source: Section 2.1.3.

## 17. Assistant-Axis Construction

The Assistant Axis is computed as the mean default Assistant activation vector minus the mean role-playing role vector, layer by layer. Paper source: Section 3.1. Code source: `pipeline/5_axis.py`. Local README gives the same formula, `axis = mean(default_vectors) - mean(role_vectors)`.

## 18. Persona Drift Measurement

Persona drift is measured by comparing activations to role vectors or to the Assistant Axis using cosine similarity/projection. The local replication uses layer-specific cosine to role/reference vectors, assistant-axis projection, and score-conditioned candidate vectors. Sources: paper Section 3, `assistant_axis/pca.py`, local Q2/Paper 1.5 scripts under `research/q2_stability/qwen/scripts/`, and validation outputs under `research/q2_stability/qwen/outputs/paper1_5/`.

## 19. Activation Capping Methodology

Activation capping subtracts only the component of the activation along a direction above a threshold tau. Local implementation: `assistant_axis/steering.py`, `ActivationSteering`, and `build_capping_steerer`. The code computes the projection onto a normalized vector, clamps excess above tau, and subtracts `excess * vector`. Qwen and Llama capping configs are referenced in `assistant_axis/models.py` and downloaded as `capping_config.pt` in the HF vector directories.

## 20. Steering Methodology

The paper's steering experiments add the Assistant Axis at the middle layer and every token position, with the vector scaled to average post-MLP residual stream norm on LMSYS-CHAT-1M. Source: paper Section 3.2.1. Local implementation support is in `assistant_axis/steering.py`.

## 21. Preprocessing and Postprocessing Details

Generation defaults in `pipeline/1_generate.py` include temperature 0.7, top_p 0.9, max_tokens 512, and max_model_len 2048. Qwen thinking mode is explicitly disabled in `assistant_axis/generation.py` and in activation extraction chat-template calls. Gemma 2 does not support system prompts in the local wrapper, so `assistant_axis/generation.py` concatenates instruction and question for models without system-prompt support. Judging parses the first integer 0-3 from the judge response. Sources: `pipeline/1_generate.py`, `assistant_axis/generation.py`, `pipeline/2_activations.py`, and `assistant_axis/judge.py`.

## 22. Hidden Ambiguities or Underspecified Steps

Several details are not fully reconstructable from local artifacts alone. First, the exact Claude Sonnet 4 prompt that generated the original role list, role prompts, and extraction questions is not present locally. Second, the paper threshold of at least ten category-qualified responses differs from the inspected `pipeline/4_vectors.py` default `min_count=50`. Third, the HF-downloaded vectors are raw tensors without local metadata specifying whether each tensor is fully-role-playing, somewhat-role-playing, merged, or fixed-capped after another processing step. Fourth, the paper reports middle-layer analysis, while later local Qwen replication uses layer 48 for Paper 1.5 and dyad work. Fifth, the exact procedure used to produce fixed 64-row downloaded tensors is not fully documented in local metadata.

## 23. Explicit vs Inferred Source Map

Explicit in paper: 275 roles, Claude Sonnet 4 prompt/question generation, five prompts per role, 240 questions, 1200 rollouts per role, gpt-4.1-mini judging, fully/somewhat/no role categories, mean post-MLP residual activations at response tokens, mean-centering before PCA, Assistant Axis formula, steering at middle layer, Qwen thinking disabled.

Explicit in repo/scripts: generation defaults, chat-template handling, Qwen thinking disable implementation, forward-hook extraction on full decoder blocks, assistant-span averaging, role-specific judge prompts, score parsing, vector aggregation script behavior, capping implementation, model config target layers.

Inferred from replication behavior: current Paper 1.5 Qwen layer-48 extraction convention, activation shard preservation pattern, adaptive stopping thresholds, score-conditioned validation workflow, and token-cap sensitivity workflow.
