# Codex Execution Tiers

Purpose: choose the right Codex settings and workflow posture for each type of task.

## Tier A: Lightweight Operations

Use for monitoring, copying files, checking logs, listing directories, SCP, heartbeat inspection, and simple status reports.

Recommended setting: GPT-5.5 Standard when available, but Fast is acceptable only when the user explicitly requests speed and the task has no research interpretation component.

Operational style: short commands, read-only where possible, frequent status updates, no prose synthesis beyond facts observed. Do not make paper claims from Tier A work.

Overnight example: checking whether `phase1_inference_only_v4.py` was still running, counting JSONL rows and activation shards, checking GPU memory, and reporting that the run was at 1180/1200.

## Tier B: Bounded Engineering

Use for script writing, integrity validation, local analysis, scoring harnesses, path updates, resumable output handling, and repo-safe execution.

Recommended setting: GPT-5.5 Standard. Do not use Fast unless the user explicitly requests it and the script is trivial.

Operational style: read existing code first, make scoped edits, run scripts locally, preserve outputs, commit and push meaningful units. Avoid touching unrelated dirty files.

Overnight example: writing the truncation diagnostic, sample sufficiency script, Codex scoring harness, and validation script path updates.

## Tier C: Research, Methodology, and Interpretation

Use for paper prose, methodology revision, operational canon, research design, empirical interpretation, workflow architecture, and synthesis of findings.

Recommended setting: GPT-5.5 Standard. Use the full reasoning budget. Do not use Fast.

Operational style: distinguish empirical findings from interpretation, preserve caveats, write publication-ready prose, and update `RESEARCH_STATE.md`. Do not hide judge substitutions, artifact caveats, or failed paths.

Overnight example: converting the trickster extraction result into Paper 1.5 adaptive extraction methodology and distinguishing strict Lu-method replication from operationally validated adaptive extraction.

## Escalation Rule

If a Tier A monitoring task produces a surprising empirical result, promote it to Tier B or Tier C before analysis. If a Tier B script produces a paper-relevant finding, update `RESEARCH_STATE.md` and write a durable note or report. If a Tier C decision changes future operations, create a context update card or commit a workflow note.

## Model Provenance Rule

Every future generated, evaluated, or analyzed research artifact must record model provenance before commit. Use `research/workflow/model_provenance_schema.md` and keep `generation_model`, `evaluation_model`, `analysis_model`, and `script_author_model` distinct. Do not describe Codex-authored scripts, Qwen-generated responses, OpenAI judge scores, and Claude-authored inventories with a single ambiguous `model` field.
