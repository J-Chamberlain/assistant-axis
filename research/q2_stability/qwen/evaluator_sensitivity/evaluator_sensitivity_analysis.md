# Evaluator Sensitivity Analysis

## Research Question

How sensitive are role-expression judgments to evaluator model choice when comparing Codex GPT-5.5 Standard and `gpt-4.1-mini` on the same Qwen trickster and editor response corpora?

## Canonical Judge Materials

The `gpt-4.1-mini` rescoring uses the canonical role-specific `eval_prompt` fields from `data/roles/instructions/{role}.json`, exported in `research/assistant_axis_methodology/prompts_and_questions/canonical_judge_prompt.md`. These prompts define scores 0-3 and instruct the judge to return only a number.

## Important Limitation

Codex GPT-5.5 is not callable from Python; Codex scores are imported from existing audited score files, while gpt-4.1-mini is newly scored with canonical Lu eval prompts.

This means the comparison is controlled on response corpus and parsing, and canonical on the `gpt-4.1-mini` side. It is not a perfect same-prompt re-run of Codex because Codex cannot be invoked programmatically from the local script.

## Overall Metrics

- Paired records: 0
- Agreement metrics: not computed because no `gpt-4.1-mini` paired scores were produced.
- API status: the attempted `gpt-4.1-mini` call returned OpenAI `insufficient_quota`; the script preserved the Codex-side baseline and stopped without fabricating scores.

## Canonical Corpora Located

- `trickster` responses: `research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl`
- `trickster` Codex scores: `research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_codex_gpt55.jsonl`
- `editor` responses: `research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128.jsonl`
- `editor` Codex scores: `research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55.jsonl`

## Per-Role Baseline Inventory

| Role | Codex scored | Codex score>=2 | Codex score==3 | gpt-4.1-mini scored | Status |
|---|---:|---:|---:|---:|---|
| `editor` | 128 | 10 | 3 | 0 | blocked by API quota |
| `trickster` | 64 | 64 | 33 | 0 | blocked by API quota |

## Interpretation

The evaluator-sensitivity experiment is not complete. The reproducible harness, canonical corpora selection, Codex baseline import, and output schema are in place, but `gpt-4.1-mini` scoring could not run because the OpenAI API returned `insufficient_quota`.

No claim should be made about evaluator sensitivity, editor ambiguity, or trickster/editor threshold robustness until `gpt-4.1-mini` scores are successfully generated for the paired records.
