# H100 Vs Prior Extraction Difference

## Shared Elements

- Model ID: `Qwen/Qwen3-32B`.
- Target layer number: 48.
- Thinking disabled at chat-template/generation time.
- Deterministic generation.
- Response-token mean pooling excludes prompt tokens.
- Raw mean activation vectors are used without L2 normalization before PCA projection.

## Differences

- Prior trickster/editor adaptive extraction captured activations using `model.model.layers[48].register_forward_hook(...)`.
- H100 validation captured activations from `out.hidden_states[48]` after a second forward pass with `output_hidden_states=True`.
- Prior adaptive extraction used system+user role-instruction prompts and 512 max new tokens; H100 used novel user-only prompts and 256 max new tokens.
- Prior adaptive extraction pooled multiple qualifying rollouts into role vectors; H100 used one measured response vector per prompt.
- Prior extraction filtered by role-expression score; H100 did not filter prompts/responses by role expression.

## Interpretation

The prompt, filtering, and rollout-pooling differences are expected by design. The activation-site difference is the unresolved methodological issue for D01.
