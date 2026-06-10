# Generation Independence Verification

- Verified UTC: 2026-06-10T00:45:32.209817+00:00
- Each generation call creates a fresh `messages` list containing only the current sample's user prompt.
- No previous user prompts are included.
- No previous assistant responses are included.
- The script does not pass `past_key_values` between generations.
- The script generates samples sequentially; it does not concatenate examples into a batch.
- The generation call may use KV cache internally for the current sample only (`use_cache=True`).
- Activation extraction is a separate full forward pass over only the current generated sequence with `use_cache=False`.
- Repeated samples of the same prompt receive distinct seeds and independent generation calls.
- Different prompts receive distinct seeds and independent generation calls.

Status: pass, conditional on using this script without modification.
