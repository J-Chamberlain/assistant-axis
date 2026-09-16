# AA-14 extraction provenance erratum · 2026-09-16

This erratum is added on the AA-15 branch. It does **not** alter the AA-14
branch, fitted PCA, exported coordinates, or deployed viewer. The frozen
AA-14 source commit is `4488ff8a828b9f690d64ab52814721c2bd7c47de`.

## Observed: what AA-14 actually fitted

`research/outputs/three_model_trait_pca/run_analysis.py` loads each released
trait and role `.pt` tensor, casts it to float32, and calls `mean(0)` before
fitting PCA or projecting personas. The saved trait tensors are bare bf16
PyTorch tensors of shape Qwen `[64, 5120]`, Llama `[80, 8192]`, and Gemma
`[46, 4608]`. These first dimensions are distinct saved decoder-layer rows,
not response tokens or samples: their counts equal the model layer counts in
`assistant_axis/models.py`, and layer 0 differs materially from an intermediate
layer in every model. The tensor has no embedded prompt, response ID, filter,
or token-span metadata.

`audit_aa14_vector_provenance.py` independently recomputes PC1–PC3 from the
mean of **all** rows and from one selected row. All-row PCA reproduces AA-14
explained-variance fractions to <5e-16 for each model. Selected-layer PCA
does not: maximum PC1–PC3 ratio differences are 0.0393 for Qwen layer 48,
0.00872 for Llama layer 40, and 0.0843 for Gemma layer 22. The frozen trait
means also match all-row means (up to float32 export precision) and not the
selected-layer means. Machine-readable results, including source hashes, are
in `aa14_vector_layer_audit.json`.

**Classification: mislabeled inventory entry, not an incorrect AA-14
calculation.** `source_inventory.json` calls Qwen `"layer": 48`, even though
the adjacent load path averages 64 rows for Qwen, just as it averages 80 and
46 for Llama and Gemma. The older
`research/outputs/trait_space_interpretation/run_trait_space_interpretation.py`
introduced the same mismatch: its docstring calls the source "layer-48"
while its `load_vector_dir()` uses `tensor.mean(0)`. Its report similarly
calls `[64,5120]` a "layer-48 trait tensor" while stating that it was
mean-pooled to 5120 dimensions. That older file was introduced in commit
`e564dd7b79d61afeb988dbaccfb52395fdd9671d`; AA-14 inherited the
numerical reference and the misleading label. No AA-14 spectrum or projection
should be replaced with a layer-48-only result.

## Recovered original procedure

The original paper's Appendix A and C.1, `data/traits/instructions/*.json`,
and `research/outputs/prompt_artifact_inventory/` establish the original
trait-elicitation design. Each of the 240 traits has a description, five
**positive/negative system-instruction pairs**, 40 behavioral questions, and
a 0–100 trait-expression evaluation prompt. Model responses were generated
under these prompts; the source paper reports 2,400 positive and 2,400
negative rollouts per trait. It retained traits having at least ten prompt
pairs with a score difference of at least 50, then took the mean post-MLP
residual-stream activation over **assistant response tokens** and formed a
contrast vector as mean positively elicited activation minus mean negatively
elicited activation, at each layer. The paper states Qwen thinking was
disabled. See [Lu et al., Appendix C.1](https://arxiv.org/html/2601.10387#A3.SS1)
and [prompt artifacts](https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts).

The public `pipeline/1_generate.py`, `pipeline/2_activations.py`,
`assistant_axis/internals/activations.py`, and
`assistant_axis/internals/spans.py` support a **response-generation and
response-token hook-extraction convention**: forward hooks on full decoder
blocks capture post-MLP residual outputs; `SpanMapper.map_spans` averages
assistant span tokens. The public pipeline is explicitly role-oriented, not
a fully specified release recipe for the trait vectors. Model identifiers in
`assistant_axis/models.py` are `Qwen/Qwen3-32B`,
`meta-llama/Llama-3.3-70B-Instruct`, and `google/gemma-2-27b-it`.
Recommended *single* middle layers 32/40/22 in that file concern downstream
axis use; the released trait files and AA-14 fit use all saved layers.

## Inferred but supported, and still unresolved

The original paper plus source strongly support that the released first
tensor dimension indexes post-block residual-stream layers, and that each
layer's trait vector is a positive-minus-negative contrast of generated
assistant response-token activations. This is supported inference about the
**released tensors**, not a record-level re-extraction. The public role
extraction scripts are a likely implementation analogue, not proof that the
same exact script version, generation settings, and scorer were used for the
released trait tensors.

No per-trait response IDs, judge scores, selected prompt-pair membership,
exact rollout-to-vector aggregation weights, sampling seeds, or generation
logs accompany the bare tensors. The paper's 2,400-per-polarity rollout
count is not explained by the preserved five instruction pairs × 40
questions alone. The original complete trait-vector construction is thus
**not exactly recoverable** from the inspected public repo, git history,
local and sibling worktrees, Hugging Face cache metadata, manifests, prior
reports, and tensors. The cache metadata gives a dataset revision and file
integrity hash, not the missing response-level lineage.

## Consequence for AA-15

AA-15 may use a *prospectively frozen analogue*, as separately authorized,
but must not call new HiFWB vectors method-matched replicas of the original
traits. The analogue should use the same three model IDs; generate actual
responses to positive/negative system prompts; hook all decoder-layer
outputs; average assistant response tokens; form a positive-minus-negative
contrast at every layer; then average the saved layer rows to match the
**frozen AA-14 feature construction** before subtracting AA-14's trait mean
and projecting on its unchanged directions. Prompt count, behavioral
questions, scoring, and robustness variants must be frozen and disclosed.
Even then, an extraction-method shift could dominate an apparent HiFWB
location or cluster compactness, and comparison against the original trait
cloud is conditional on that limitation.
