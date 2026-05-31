# Public-Source Extraction Equivalence Audit

- Generated UTC: 2026-05-31T14:32:47.986206+00:00
- model_used: GPT-5.5
- Scope: public-source and local-source audit only; no pods, no new activations, no model APIs.

## Direct Answer

The public-source audit finds a likely extraction-boundary mismatch, not equivalence. The official Assistant Axis pipeline and prior successful trickster replication use forward hooks on `model.model.layers[48]`, capturing the decoder layer 48 module output. The H100 percentile-edge runner used `outputs.hidden_states[48]`.

Under Hugging Face ModelOutput documentation and the Transformers 4.51.0 Qwen3 source behavior, `outputs.hidden_states[48]` is the state before decoder layer 48, equivalently the output after decoder layer 47. The layer-48 module-output hook corresponds to the output after decoder layer 48, which maps to `outputs.hidden_states[49]` for intermediate layers. Therefore D01 should not be closed as resolved-equivalent; it should be marked open with mismatch details and rerun implications.

## Sources Inspected

The audit inspected the official Assistant Axis GitHub repository, including pipeline files, internals helpers, vector construction, PCA utilities, generation helpers, steering/capping code, and notebooks. It inspected the Hugging Face Assistant Axis vector dataset and prompt-artifact dataset metadata. It inspected the Qwen/Qwen3-32B config and the Transformers Qwen3 model source behavior relevant to decoder-layer outputs and hidden-state indexing. It also compared current H100 code against prior project trickster/editor adaptive extraction artifacts and the previous D01 audit.

Full source inventory is saved in `source_file_inventory.csv`.

## Evidence Summary

| Evidence question | Finding | D01 implication |
| --- | --- | --- |
| Official representation | `pipeline/README.md` documents zero-indexed post-MLP residual-stream layers. | Released vectors target decoder-block outputs, not arbitrary hidden-state tuple indices. |
| Official extraction path | `ActivationExtractor` registers forward hooks on target layers and captures module outputs. | Official extraction is hook-based. |
| Prior successful replication | Trickster replication hooks `model.model.layers[48]` and reached cosine 0.957557 to the downloaded trickster vector. | The hook path is empirically aligned with released vectors. |
| H100 extraction path | H100 runner uses `out.hidden_states[48]` after a second full forward pass. | H100 used hidden-state tuple indexing, not hook capture. |
| Qwen3 hidden-state mapping | HF docs and Qwen3 source imply hidden states include embeddings and then layer-boundary outputs. | `hidden_states[48]` is one decoder block earlier than layer-48 hook output. |

## Does `outputs.hidden_states[48]` Equal The Layer-48 Hook Tensor?

Observed: the Qwen3 decoder layer returns the post-attention-residual and post-MLP-residual hidden state. A forward hook on `model.model.layers[48]` captures that returned tensor.

Observed: Transformers hidden states include an initial embedding state plus per-layer states. In the Qwen3 4.51.0 source, the current hidden state is appended before each decoder layer, then the decoder layer updates it.

Inferred: for intermediate layers, `hidden_states[48]` is the output of layer 47 / input to layer 48. The output of `model.model.layers[48]` corresponds to `hidden_states[49]`.

Conclusion: no, public evidence indicates `outputs.hidden_states[48]` does not equal the Assistant Axis layer-48 hook tensor.

## What PCA Reproduction Proves

The H100 PCA reproduction error of 1.207e-06 proves that the committed projection basis, centering, and sign orientation reproduce canonical role coordinates. It does not prove that new H100 activations were measured at the same activation site or layer boundary as the released role vectors.

## Does Prior Trickster/Jester Replication Resolve This?

No. It helps in the opposite direction: it validates the hook-based extraction path as compatible with released Qwen vectors. It does not validate H100 `hidden_states[48]`; rather, it makes the H100 hidden-state path more suspect because it differs from the path that already matched a released role vector.

## D01 Decision

D01 should be marked `open` with likely mismatch found. The mismatch is source-backed enough to block further interpretation of H100 PC2/PC3 anomalies as model-behavior results until the extraction boundary is corrected or empirically checked.

## Remaining Test

Run the minimal one-prompt hook-vs-hidden-states comparison in `minimal_gpu_test_if_needed.md`. If the hook output matches `hidden_states[49]`, rerun or reinterpret the H100 validation with the corrected extraction boundary. A full H100 rerun is not the next step; a tiny verification is.

## Bottom Line

Public-source evidence strongly suggests the H100 runner measured one layer boundary earlier than the official Assistant Axis Qwen layer-48 vector convention. This could plausibly contribute to the observed PC2 shift, cone outliers, and PC3 collapse, so those anomalies should remain methodologically caveated until corrected.
