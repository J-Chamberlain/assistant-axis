# Role Rollout Artifact Audit Report

- Generated UTC: 2026-05-31T15:02:53.318157+00:00
- model_used: GPT-5.5
- Scope: public/local source inventory only; no pods, no activation generation, no model APIs.

## Direct Answers

1. Do we have the exact 1,200 input combinations per role? Yes at the message-schema level: public artifacts provide 5 positive role instructions per non-default role and 240 extraction questions, and public generation code combines them as system/user conversations. Exact rendered token strings depend on tokenizer/chat-template/runtime version.
2. Can we reconstruct them if not directly stored? Yes. The intended 5 x 240 instruction-question combinations are reconstructable for all 275 non-default roles and for the default prompts.
3. Do we have generated responses? No public original role-vector rollout responses were found. The official repo includes paper case-study transcripts and generation code, not the 275 x 1,200 role-vector response JSONL outputs. Local project trickster/editor responses exist but are later project-generated artifacts, not original public Assistant Axis rollouts.
4. Do we have response-level judge scores? No public original response-level score files were found. The role eval prompts and judge script are public; original score JSONs are not.
5. Do we have retained-response masks/IDs? No public retained response IDs or masks were found. The vector dataset exposes aggregate vectors, not instance-level filters.

## Count Summary

| Item | Count |
|---|---:|
| Role instruction JSON files, including default | 276 |
| Non-default role instruction files | 275 |
| Non-default roles with 5 positive instructions | 275 |
| Extraction questions | 240 |
| Theoretical combinations per non-default role | 1200 |
| Public original generated role-vector responses found | 0 |
| Public original response-level judge scores found | 0 |
| Public retained-response masks/IDs found | 0 |

## Public Recipe Verification

The paper describes 275 roles, five system prompts per role, shared extraction questions, LLM judge role-expression labels, filtering of insufficiently role-expressive responses, and mean post-MLP residual stream activations over response tokens. The official repository implements the core public pipeline:

- `pipeline/1_generate.py` generates 1,200 responses per role by default.
- `assistant_axis/generation.py` formats system/user conversations from positive instructions and questions, uses vLLM, and disables Qwen thinking mode when supported.
- `pipeline/3_judge.py` scores generated responses with a 0-3 role-expression rubric.
- `pipeline/4_vectors.py` computes vectors from high-scoring responses in the public code path.

One caveat: the paper text says fully and somewhat role-playing responses are treated separately with at least ten responses in a category, while the current public pipeline README/code emphasizes score-3 responses for regular role vectors with a default `--min_count 50`. This audit does not resolve whether released Hugging Face vectors were generated with exactly the current public code defaults or an earlier internal variant; the response-level scores needed to verify that are not public.

## What “64” Refers To

The most relevant public-source 64 is Qwen/Qwen3-32B's total layer count. The released local Qwen role vectors load as `[64, 5120]`, which is `num_layers x hidden_dim`, not 64 retained responses. The remembered 64 also appears in local project adaptive extraction as a pragmatic target/count: trickster reached 64 score>=2 responses in 64 scored records, and editor used a matched first-64 token-cap sensitivity subset. Those are local project methodology choices, not original public Assistant Axis filter masks.

The audit found no public-source evidence that the original Assistant Axis role vectors used exactly 64 retained responses per role. Earlier project language about a fixed 64-row cap should be treated as a corrected misinterpretation of the `[64, 5120]` layer-by-hidden tensor shape unless future private metadata says otherwise.

## Implications For Forecaster Training

Instance-level prompt-to-centroid training can proceed on the Mac Mini by reconstructing intended instruction-question inputs and mapping each row to the released role centroid/PCA target. This would increase training examples from 275 role-level rows to 330,000 role-input rows, but the target is still role-level and not response-success-specific.

Successful-rollout-only training is not possible from public data because generated responses, judge scores, and retained IDs are absent. To train that dataset, the project must regenerate rollouts and judge scores, or obtain the original private rollout artifacts.

## Source Files And URLs Inspected

- Official GitHub: `https://github.com/safety-research/assistant-axis`
- Official paper/arXiv: `https://arxiv.org/abs/2601.10387`
- Official vectors dataset: `https://huggingface.co/datasets/lu-christina/assistant-axis-vectors`
- Prompt artifact dataset: `https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts`
- Local prompt inventory: `research/outputs/prompt_artifact_inventory/`
- Local extraction-equivalence audit: `research/outputs/extraction_equivalence_audit/`
- Local project state: `research/RESEARCH_STATE.md`, `research/FINDINGS_LEDGER.md`
- Local adaptive extraction artifacts under `research/q2_stability/qwen/outputs/paper1_5/`

Detailed tables are saved beside this report.
