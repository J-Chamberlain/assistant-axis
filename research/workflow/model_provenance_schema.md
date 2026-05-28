# Model Provenance Schema

## Purpose

Model identity is part of the experimental causal structure for this project. Generated persona inventories, rewritten prompts, evaluated responses, interpretive syntheses, and activation-extraction artifacts must record which model produced, judged, analyzed, or authored each artifact.

Every future generated or evaluated research artifact must include model provenance before commit. Missing provenance is an integrity problem, not cosmetic metadata.

## Mandatory Fields

Use these fields in JSON artifacts, manifests, summaries, score files, and machine-readable reports when applicable.

`task_type`: The research operation being performed. Examples: `role_inventory_generation`, `role_expression_scoring`, `activation_extraction`, `semantic_analysis`, `interpretive_synthesis`, `prompt_rewrite`.

`artifact_type`: The artifact class. Examples: `raw_generation`, `parsed_inventory`, `score_file`, `manifest`, `analysis_summary`, `markdown_report`, `script`.

`artifact_path`: Repo-relative path to the artifact.

`generation_model`: The model that generated target content being studied. Examples: generated role inventories, model responses, prompt rewrites. Use `null` when no target content was generated.

`evaluation_model`: The model that judged, scored, or classified target content. Use `null` when no evaluator model was used.

`analysis_model`: The model that performed interpretive synthesis, qualitative analysis, or paper-methodology reasoning. Use `null` for purely scripted numerical analysis.

`script_author_model`: The model or agent that wrote the script that produced the artifact. Examples: `GPT-5.5 Standard via Codex`, `Claude Sonnet 4 via Claude Code`. Use `unknown` only for historical scripts where authorship cannot be recovered.

`orchestration_agent`: The system that executed or coordinated the task. Examples: `Codex`, `Claude Code`, `manual`, `RunPod script`.

`provider`: The model provider for the main model field relevant to the artifact. Examples: `openai`, `anthropic`, `huggingface`, `local`, `none`.

`model_version_or_alias`: Exact model string or alias used by the provider. Examples: `gpt-4.1-mini`, `gpt-5.5`, `Qwen/Qwen3-32B`.

`date`: ISO 8601 date or timestamp.

`prompt_family_id`: Prompt-family identifier when a prompt variant is part of the design. Use `null` when not applicable.

`temperature`: Sampling temperature when applicable. Use `null` for deterministic scripted analysis or unavailable historical artifacts.

`max_tokens`: Maximum output token setting when applicable. If the API uses `max_output_tokens` or `max_new_tokens`, record the numerical value here and preserve the original parameter name inside `generation_settings`.

`source_inputs`: List of repo-relative input paths, external dataset identifiers, or reference artifacts used to produce the artifact.

`notes_on_uncertainty`: Any ambiguity about model identity, provider aliases, scoring substitutions, incomplete API availability, prompt drift, or historical provenance.

## Field Semantics

Use `generation_model` only for the model that generated target content being analyzed. For example, Qwen/Qwen3-32B is the `generation_model` for Qwen response corpora, while GPT-5.5 is the `generation_model` for a GPT-generated role inventory.

Use `evaluation_model` only for the judge or scorer model. For example, `gpt-4.1-mini` and `Codex GPT-5.5 Standard` are evaluator models in role-expression scoring.

Use `analysis_model` for model-authored interpretation, synthesis, qualitative evaluation, or paper prose. Do not use it for purely numerical scripts unless an LLM directly interpreted the outputs.

Use `script_author_model` for the model that authored or materially rewrote the code. Do not substitute the target model or evaluator model in this field.

Do not conflate these fields. A single artifact may have multiple models involved:

- `generation_model`: Qwen/Qwen3-32B generated the response text.
- `evaluation_model`: Codex GPT-5.5 Standard judged role expression.
- `script_author_model`: GPT-5.5 Standard via Codex wrote the scorer harness.
- `analysis_model`: GPT-5.5 Standard synthesized the methodology note.

## Minimal JSON Example

```json
{
  "task_type": "role_inventory_generation",
  "artifact_type": "parsed_inventory",
  "artifact_path": "research/stage1_role_inventory_uncertainty/parsed_outputs/gpt-5.5__prompt_family_01.json",
  "generation_model": "gpt-5.5",
  "evaluation_model": null,
  "analysis_model": null,
  "script_author_model": "GPT-5.5 Standard via Codex",
  "orchestration_agent": "Codex",
  "provider": "openai",
  "model_version_or_alias": "gpt-5.5",
  "date": "2026-05-27T00:00:00Z",
  "prompt_family_id": "prompt_family_01",
  "temperature": 0.2,
  "max_tokens": 6000,
  "source_inputs": [
    "research/stage1_role_inventory_uncertainty/prompts/prompt_family_01.txt"
  ],
  "notes_on_uncertainty": "OpenAI-side generation only; Claude-side inventories are synced through GitHub."
}
```

## Commit Gate

Before committing generated, evaluated, or analysis artifacts, verify that model provenance exists in one of these places:

1. The artifact itself.
2. A manifest or summary file committed with the artifact.
3. A parent run manifest that names the artifact path.

If none exists, add provenance before commit.
