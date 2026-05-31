# Reconstructed Role Input Schema

- Generated UTC: 2026-05-31T15:02:53.318157+00:00
- model_used: GPT-5.5

## Available Inputs

- Role instruction files: `276` including `default.json`; `275` non-default roles.
- Positive instructions per non-default role: `5` for `275` / `275` roles.
- Global extraction questions: `240` with IDs `0` through `239`.
- Theoretical combinations per non-default role: `5 x 240 = 1200`.

## Message Structure

The public generation code constructs one conversation per instruction-question pair:

```json
[
  {"role": "system", "content": "<role positive instruction>"},
  {"role": "user", "content": "<extraction question>"}
]
```

If the tokenizer does not support system messages, the code concatenates the instruction and question into a user message. For Qwen-family models, the generation helper passes `enable_thinking=False` when supported by the tokenizer chat template.

## Exactness Caveat

The semantic message-level input distribution is reconstructable. Exact token-level prompts depend on the target tokenizer/chat template, vLLM version, model short-name substitution for `{model_name}`, and generation settings. The public repository provides the code and prompt artifacts needed to reconstruct these inputs, but not the already-rendered token strings from the original runs.
