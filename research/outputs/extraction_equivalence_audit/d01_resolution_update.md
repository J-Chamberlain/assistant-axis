# D01 Resolution Update

Status: `in_progress`.

The audit resolves several pieces of D01:

- Model identity matches Qwen/Qwen3-32B.
- Layer target is consistently recorded as 48.
- Prior adaptive trickster/editor extraction used response-token mean pooling and disabled thinking.
- Current H100 projection centering/sign/basis is strongly verified by canonical coordinate reproduction at max abs error 1.207e-06.
- Prior trickster adaptive extraction successfully matched the Lu/downloaded trickster vector at cosine 0.957557.

The audit does not resolve the activation-site equivalence question:

- Local source and prior adaptive extraction use forward hooks on transformer layer outputs.
- Current H100 validation uses `output_hidden_states[48]`.
- The exact hook-vs-hidden-state boundary for Qwen/Qwen3-32B was not proven in local source inspection.

Conclusion: D01 should not be closed yet. H100 results remain informative, but PC2 shift, cone outliers, and PC3 collapse should continue to carry an activation-site caveat until the minimal equivalence test is run or source-level proof is found.
