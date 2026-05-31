#!/usr/bin/env python3
"""Audit public Assistant Axis role-rollout artifacts and the remembered 64 count.

This is a source/artifact inventory only. It does not run models, pods, or APIs.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research/outputs/role_rollout_artifact_audit"
MODEL_USED = "GPT-5.5"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    with path.open() as f:
        return json.load(f)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def line_context(path: Path, pattern: str) -> list[dict[str, str]]:
    rows = []
    if not path.exists() or path.stat().st_size > 3_000_000:
        return rows
    try:
        lines = path.read_text(errors="replace").splitlines()
    except Exception:
        return rows
    rx = re.compile(pattern)
    for idx, line in enumerate(lines, 1):
        if rx.search(line):
            rows.append(
                {
                    "source": str(path.relative_to(REPO)),
                    "line": str(idx),
                    "context": line.strip()[:600],
                }
            )
    return rows


def role_prompt_inventory() -> tuple[list[dict], dict]:
    role_dir = REPO / "data/roles/instructions"
    q_path = REPO / "data/extraction_questions.jsonl"
    questions = [json.loads(x) for x in q_path.read_text().splitlines() if x.strip()]
    rows = []
    for path in sorted(role_dir.glob("*.json")):
        data = read_json(path)
        instr = data.get("instruction", [])
        pos = [i.get("pos", "") for i in instr if isinstance(i, dict) and "pos" in i]
        rows.append(
            {
                "role": path.stem,
                "path": str(path.relative_to(REPO)),
                "is_default": path.stem == "default",
                "positive_instruction_count": len(pos),
                "embedded_question_count": len(data.get("questions", [])),
                "global_extraction_question_count": len(questions),
                "theoretical_input_combinations": len(pos) * len(questions),
                "eval_prompt_present": bool(data.get("eval_prompt")),
                "first_instruction": pos[0] if pos else "",
                "first_global_question": questions[0]["question"] if questions else "",
            }
        )
    summary = {
        "role_files_including_default": len(rows),
        "nondefault_roles": sum(1 for r in rows if not r["is_default"]),
        "global_extraction_questions": len(questions),
        "question_id_min": min(q["id"] for q in questions),
        "question_id_max": max(q["id"] for q in questions),
        "questions_unique_ids": len({q["id"] for q in questions}),
        "roles_with_5_positive_instructions": sum(1 for r in rows if not r["is_default"] and r["positive_instruction_count"] == 5),
        "default_positive_instructions": next(r["positive_instruction_count"] for r in rows if r["is_default"]),
        "theoretical_combinations_per_nondefault_role": 5 * len(questions),
    }
    return rows, summary


def availability_tables() -> tuple[list[dict], list[dict], list[dict]]:
    response_rows = [
        {
            "source": "official GitHub safety-research/assistant-axis",
            "location": "pipeline source plus transcripts/",
            "generated_responses_found": "no original role-vector rollout responses",
            "count": "0 public role-vector rollout transcripts found",
            "notes": "Repository documents generation and includes paper case-study transcripts, but not outputs/<model>/responses/*.jsonl for 275 x 1200 role-vector rollouts.",
        },
        {
            "source": "Hugging Face lu-christina/assistant-axis-vectors",
            "location": "dataset file tree",
            "generated_responses_found": "no",
            "count": "0",
            "notes": "Dataset exposes precomputed vectors/axes/capping configs, not generated rollout conversations.",
        },
        {
            "source": "Hugging Face belmore/assistant-axis-vector-prompts",
            "location": "train.parquet",
            "generated_responses_found": "no",
            "count": "0",
            "notes": "Prompt-artifact dataset contains role/trait prompt artifacts, not model completions.",
        },
        {
            "source": "local project adaptive extraction",
            "location": "research/q2_stability/qwen/outputs/paper1_5/",
            "generated_responses_found": "yes, project-generated subset",
            "count": "trickster 1200; editor 128 plus matched 64 follow-up",
            "notes": "These are later local project runs, not original public Assistant Axis rollouts.",
        },
    ]

    judge_rows = [
        {
            "source": "official GitHub safety-research/assistant-axis",
            "location": "pipeline/3_judge.py and role eval_prompt fields",
            "judge_scores_found": "no output scores",
            "count": "0 public score JSON files found",
            "notes": "Rubric and scoring script are public; response-level judge outputs are not committed.",
        },
        {
            "source": "Hugging Face lu-christina/assistant-axis-vectors",
            "location": "dataset file tree",
            "judge_scores_found": "no",
            "count": "0",
            "notes": "Vector dataset does not include score JSONs or judge raw outputs.",
        },
        {
            "source": "local project adaptive extraction",
            "location": "research/q2_stability/qwen/outputs/paper1_5/",
            "judge_scores_found": "yes, project-generated subset",
            "count": "64 trickster Codex-scored; 128 editor Codex-scored; matched 64 editor sensitivity scored",
            "notes": "Codex/GPT-5.5 scores are pragmatic local follow-up, not original gpt-4.1-mini public score files.",
        },
    ]

    retained_rows = [
        {
            "source": "official GitHub safety-research/assistant-axis",
            "location": "pipeline/4_vectors.py",
            "retained_response_ids_found": "no",
            "count": "0 public retained-ID masks found",
            "notes": "Public code shows how to filter score==3 responses, but committed artifacts do not identify retained response keys for released vectors.",
        },
        {
            "source": "paper method text",
            "location": "arXiv 2601.10387",
            "retained_response_ids_found": "no",
            "count": "0",
            "notes": "Paper states non-expressing responses are filtered and roles with at least 10 responses in a category are kept, but does not list retained IDs.",
        },
        {
            "source": "Hugging Face lu-christina/assistant-axis-vectors",
            "location": "role_vectors/*.pt",
            "retained_response_ids_found": "no",
            "count": "0",
            "notes": "The [64,5120] Qwen vector shape is layer x hidden_dim, not a retained-example matrix.",
        },
    ]
    return response_rows, judge_rows, retained_rows


def number_64_table() -> list[dict]:
    rows: list[dict] = []
    manual = [
        {
            "file_or_source": "arXiv 2601.10387 / paper PDF text",
            "line_or_location": "activation capping section",
            "context": "For Qwen 3 32B, best capping uses layers 46 to 53 out of 64 total layers.",
            "refers_to": "Qwen total transformer layers",
            "relevance_to_role_vector_construction": "indirect; confirms Qwen has 64 layers, not 64 retained rollouts",
        },
        {
            "file_or_source": "Qwen/Qwen3-32B config.json",
            "line_or_location": "num_hidden_layers",
            "context": '"num_hidden_layers": 64',
            "refers_to": "Qwen model layer count",
            "relevance_to_role_vector_construction": "directly explains [64,5120] released vector shape as layer x hidden_dim",
        },
        {
            "file_or_source": "Hugging Face assistant-axis-vector files",
            "line_or_location": "local downloaded .pt shapes",
            "context": "Sampled Qwen role vectors load as torch.Size([64, 5120]).",
            "refers_to": "64 layers by 5120 hidden dimensions",
            "relevance_to_role_vector_construction": "direct; not a retained response count or fixed storage cap",
        },
    ]
    rows.extend(manual)
    paths = [
        REPO / "assistant_axis/models.py",
        REPO / "data/extraction_questions.jsonl",
        REPO / "pipeline/README.md",
        REPO / "pipeline/1_generate.py",
        REPO / "pipeline/3_judge.py",
        REPO / "pipeline/4_vectors.py",
        REPO / "research/FINDINGS_LEDGER.md",
        REPO / "research/RESEARCH_STATE.md",
        REPO / "research/THREAD_START.md",
        REPO / "research/CLAIMS_REGISTER.md",
        REPO / "research/outputs/extraction_equivalence_audit/trickster_replication_method_summary.md",
        REPO / "research/outputs/extraction_equivalence_audit/prior_adaptive_extraction_inventory.csv",
    ]
    for base in [
        REPO / "research/q2_stability/qwen/scripts",
        REPO / "research/q2_stability/qwen/outputs/paper1_5",
    ]:
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file() and p.suffix in {".py", ".md", ".csv", ".json", ".jsonl", ".log"})
    seen = set()
    for path in paths:
        for hit in line_context(path, r"\b64\b"):
            key = (hit["source"], hit["line"], hit["context"])
            if key in seen:
                continue
            seen.add(key)
            context = hit["context"]
            if "remembered" in context or "fixed 64-row" in context or "not because vectors store 64" in context:
                refers = "resolved 64-count correction"
                relevance = "states that 64 is not evidence of original retained response count"
            elif "total_layers" in context or "[64, 5120]" in context or "[64,5120]" in context or "num_hidden_layers" in context:
                refers = "Qwen layer count / vector tensor first dimension"
                relevance = "relevant as layer count, not retained responses"
            elif "score" in context or "scored" in context or "threshold" in context or "qualifying" in context:
                refers = "local project adaptive extraction scoring threshold/count"
                relevance = "local project method, not original public Assistant Axis release"
            elif "first 64" in context or "matched64" in hit["source"] or "N_PAIRS" in context:
                refers = "local editor matched sensitivity subset"
                relevance = "local project subset, not public original role-vector construction"
            elif '"id": 64' in context or "q_idx" in context:
                refers = "question index 64 or rollout pair index"
                relevance = "ordinal ID only"
            else:
                refers = "other/ambiguous local occurrence"
                relevance = "not evidence of original retained response count"
            rows.append(
                {
                    "file_or_source": hit["source"],
                    "line_or_location": hit["line"],
                    "context": context,
                    "refers_to": refers,
                    "relevance_to_role_vector_construction": relevance,
                }
            )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = now()

    prompt_rows, summary = role_prompt_inventory()
    response_rows, judge_rows, retained_rows = availability_tables()
    number_rows = number_64_table()

    write_csv(
        OUT / "role_prompt_reconstruction_inventory.csv",
        prompt_rows,
        [
            "role",
            "path",
            "is_default",
            "positive_instruction_count",
            "embedded_question_count",
            "global_extraction_question_count",
            "theoretical_input_combinations",
            "eval_prompt_present",
            "first_instruction",
            "first_global_question",
        ],
    )
    write_csv(OUT / "generated_response_availability_report.csv", response_rows, list(response_rows[0]))
    write_csv(OUT / "judge_score_availability_report.csv", judge_rows, list(judge_rows[0]))
    write_csv(OUT / "retained_response_filter_availability_report.csv", retained_rows, list(retained_rows[0]))
    write_csv(OUT / "number_64_occurrence_table.csv", number_rows, list(number_rows[0]))

    schema = f"""# Reconstructed Role Input Schema

- Generated UTC: {generated}
- model_used: {MODEL_USED}

## Available Inputs

- Role instruction files: `{summary['role_files_including_default']}` including `default.json`; `{summary['nondefault_roles']}` non-default roles.
- Positive instructions per non-default role: `5` for `{summary['roles_with_5_positive_instructions']}` / `{summary['nondefault_roles']}` roles.
- Global extraction questions: `{summary['global_extraction_questions']}` with IDs `{summary['question_id_min']}` through `{summary['question_id_max']}`.
- Theoretical combinations per non-default role: `5 x 240 = {summary['theoretical_combinations_per_nondefault_role']}`.

## Message Structure

The public generation code constructs one conversation per instruction-question pair:

```json
[
  {{"role": "system", "content": "<role positive instruction>"}},
  {{"role": "user", "content": "<extraction question>"}}
]
```

If the tokenizer does not support system messages, the code concatenates the instruction and question into a user message. For Qwen-family models, the generation helper passes `enable_thinking=False` when supported by the tokenizer chat template.

## Exactness Caveat

The semantic message-level input distribution is reconstructable. Exact token-level prompts depend on the target tokenizer/chat template, vLLM version, model short-name substitution for `{{model_name}}`, and generation settings. The public repository provides the code and prompt artifacts needed to reconstruct these inputs, but not the already-rendered token strings from the original runs.
"""
    (OUT / "reconstructed_role_input_schema.md").write_text(schema)

    recommendation = f"""# Instance-Level Forecaster Dataset Recommendation

- Generated UTC: {generated}
- model_used: {MODEL_USED}

## Direct Recommendation

Use a reconstructed intended-input dataset now, on the Mac Mini, without GPU work:

- One row per role instruction-question pair.
- Input text fields: role name for metadata only, positive instruction text, extraction question text, optional rendered chat-template prompt if tokenizer is available locally.
- Target: released role centroid / role PCA coordinates for that role.
- Weighting: each of the 1,200 rows per role receives the same role-level target, because public data do not identify which individual rollouts succeeded.

This supports an improved instance-level prompt-to-centroid forecaster over intended elicitation inputs. It does not support successful-rollout-only or judge-filter-aware training.

## Why Successful-Rollout-Only Training Is Not Publicly Possible

Public artifacts do not include generated responses, response-level judge scores, or retained response IDs/masks for the original role vectors. The released Qwen role vector tensors shaped `[64, 5120]` are layer-by-hidden vectors, not 64 retained examples. Successful-rollout-aware training would require regenerating responses and judge scores or obtaining private original outputs.

## GPU Requirement

No GPU is needed for reconstructed intended-input forecasting. GPU work is needed only if the project chooses to regenerate rollout responses/activations or to build a successful-rollout-aware dataset from fresh runs.
"""
    (OUT / "instance_level_forecaster_dataset_recommendation.md").write_text(recommendation)

    report = f"""# Role Rollout Artifact Audit Report

- Generated UTC: {generated}
- model_used: {MODEL_USED}
- Scope: public/local source inventory only; no pods, no activation generation, no model APIs.

## Direct Answers

1. Do we have the exact 1,200 input combinations per role? Yes at the message-schema level: public artifacts provide 5 positive role instructions per non-default role and 240 extraction questions, and public generation code combines them as system/user conversations. Exact rendered token strings depend on tokenizer/chat-template/runtime version.
2. Can we reconstruct them if not directly stored? Yes. The intended 5 x 240 instruction-question combinations are reconstructable for all 275 non-default roles and for the default prompts.
3. Do we have generated responses? No public original role-vector rollout responses were found. The official repo includes paper case-study transcripts and generation code, not the 275 x 1,200 role-vector response JSONL outputs. Local project trickster/editor responses exist but are later project-generated artifacts, not original public Assistant Axis rollouts.
4. Do we have response-level judge scores? No public original response-level score files were found. The role eval prompts and judge script are public; original score JSONs are not.
5. Do we have retained-response masks/IDs? No public retained response IDs or masks were found. The vector dataset exposes aggregate vectors, not instance-level filters.

## Count Summary

| Item | Count |
|---|---:|
| Role instruction JSON files, including default | {summary['role_files_including_default']} |
| Non-default role instruction files | {summary['nondefault_roles']} |
| Non-default roles with 5 positive instructions | {summary['roles_with_5_positive_instructions']} |
| Extraction questions | {summary['global_extraction_questions']} |
| Theoretical combinations per non-default role | {summary['theoretical_combinations_per_nondefault_role']} |
| Public original generated role-vector responses found | 0 |
| Public original response-level judge scores found | 0 |
| Public retained-response masks/IDs found | 0 |

## Public Recipe Verification

The paper describes 275 roles, five system prompts per role, shared extraction questions, LLM judge role-expression labels, filtering of insufficiently role-expressive responses, and mean post-MLP residual stream activations over response tokens. The official repository implements the core public pipeline:

- `pipeline/1_generate.py` generates 1,200 responses per role by default.
- `assistant_axis/generation.py` formats system/user conversations from positive instructions and questions, uses vLLM, and disables Qwen thinking mode when supported.
- `pipeline/3_judge.py` scores generated responses with a 0-3 role-expression rubric.
- `pipeline/4_vectors.py` computes vectors from high-scoring responses in the public code path.

One caveat: the paper text says fully and somewhat role-playing responses are treated separately with at least ten responses in a category, while the current public pipeline README/code emphasizes score-3 responses for regular role vectors with a default `--min_count 50`. This audit does not resolve whether released Hugging Face vectors were generated with exactly the current public code defaults or an earlier internal variant; the response-level scores needed to verify that are not public.

## What “64” Refers To

The most relevant public-source 64 is Qwen/Qwen3-32B's total layer count. The released local Qwen role vectors load as `[64, 5120]`, which is `num_layers x hidden_dim`, not 64 retained responses. The remembered 64 also appears in local project adaptive extraction as a pragmatic target/count: trickster reached 64 score>=2 responses in 64 scored records, and editor used a matched first-64 token-cap sensitivity subset. Those are local project methodology choices, not original public Assistant Axis filter masks.

The audit found no public-source evidence that the original Assistant Axis role vectors used exactly 64 retained responses per role. Earlier project language about a fixed 64-row cap should be treated as a corrected misinterpretation of the `[64, 5120]` layer-by-hidden tensor shape unless future private metadata says otherwise.

## Implications For Forecaster Training

Instance-level prompt-to-centroid training can proceed on the Mac Mini by reconstructing intended instruction-question inputs and mapping each row to the released role centroid/PCA target. This would increase training examples from 275 role-level rows to 330,000 role-input rows, but the target is still role-level and not response-success-specific.

Successful-rollout-only training is not possible from public data because generated responses, judge scores, and retained IDs are absent. To train that dataset, the project must regenerate rollouts and judge scores, or obtain the original private rollout artifacts.

## Source Files And URLs Inspected

- Official GitHub: `https://github.com/safety-research/assistant-axis`
- Official paper/arXiv: `https://arxiv.org/abs/2601.10387`
- Official vectors dataset: `https://huggingface.co/datasets/lu-christina/assistant-axis-vectors`
- Prompt artifact dataset: `https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts`
- Local prompt inventory: `research/outputs/prompt_artifact_inventory/`
- Local extraction-equivalence audit: `research/outputs/extraction_equivalence_audit/`
- Local project state: `research/RESEARCH_STATE.md`, `research/FINDINGS_LEDGER.md`
- Local adaptive extraction artifacts under `research/q2_stability/qwen/outputs/paper1_5/`

Detailed tables are saved beside this report.
"""
    (OUT / "role_rollout_artifact_audit_report.md").write_text(report)

    metadata = {
        "generated_utc": generated,
        "model_used": MODEL_USED,
        "startup_status": "STARTUP VERIFIED",
        "summary": summary,
        "public_original_responses_found": False,
        "public_original_judge_scores_found": False,
        "public_retained_masks_found": False,
        "number_64_resolution": "Qwen layer count and local project adaptive counts; no public original retained-response count.",
    }
    (OUT / "audit_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"Wrote role rollout artifact audit to {OUT}")


if __name__ == "__main__":
    main()
