# GPT-4.1 Rejudge Plan for Prior Adaptive Runs

Prepared judge input file: `prior_adaptive_gpt41_judge_inputs.jsonl`

Prepared responses: **1392**.

The rejudge was **not run** in this audit because no explicit
`run_gpt41_rejudge=true` configuration was present.

## Proposed Judge Rubric

Use the existing 0-3 role-expression rubric:

- 0 = no meaningful role expression; generic assistant response or off-role.
- 1 = weak or superficial role expression; mostly generic assistant behavior.
- 2 = clear role expression; substantially reflects the assigned role while remaining coherent and safe.
- 3 = strong role expression; consistently and vividly inhabits the assigned role without becoming incoherent or unsafe.

## Prompt Isolation

The prepared JSONL includes role, role instruction, extraction question, saved
response text, original Codex/GPT-5.5 score if available, and original rationale
if available. It intentionally excludes activation coordinates and centroid
distances so GPT-4.1 can judge expression without geometry leakage.

## Recommended Next Command

Only after explicit authorization:

```bash
OPENAI_API_KEY="$OPENAI_API_KEY" python3 research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py
```

or write a small one-pass scorer using `prior_adaptive_gpt41_judge_inputs.jsonl`
as input and this rubric.
