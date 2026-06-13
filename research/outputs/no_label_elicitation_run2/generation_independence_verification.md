# Run 2 Generation Independence Verification

- Verified UTC: 2026-06-13T10:59:16.529995+00:00
- Each sample is generated from a fresh one-message conversation containing only the current prompt text.
- No prior user prompts are included.
- No prior assistant responses are included.
- No `past_key_values` are passed between samples.
- Repeated samples of the same prompt use independent generation calls and distinct deterministic seeds.
- Different prompts use independent generation calls and distinct deterministic seeds.
- Activation extraction uses a separate no-cache full forward pass over only the current generated sequence.
- The script runs samples sequentially and does not concatenate examples or batch neighboring prompts.

Status: pass for the committed script path; execution remains blocked until a RunPod API key is configured.
