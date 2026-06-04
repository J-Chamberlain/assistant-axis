#!/usr/bin/env python3
"""Audit prior adaptive extraction artifacts for D01 recoverability.

This is an offline analysis script. It does not call model APIs, start pods, or
generate new activations. It inventories saved response/activation artifacts and
determines whether they can be reused under the corrected D01 understanding:
`model.model.layers[48]` hook output matches `outputs.hidden_states[49]`.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.request import urlopen

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "research/outputs/prior_adaptive_recovery_audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAPER15_DIR = REPO_ROOT / "research/q2_stability/qwen/outputs/paper1_5"
VECTOR_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
CANONICAL_PCA_PATH = (
    REPO_ROOT
    / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"
)
INSTRUCTIONS_DIR = REPO_ROOT / "data/roles/instructions"
QUESTIONS_PATH = REPO_ROOT / "data/extraction_questions.jsonl"

RAW_URLS = {
    "STARTUP_MANIFEST.md": "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/STARTUP_MANIFEST.md",
    "RESEARCH_STATE.md": "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md",
    "THREAD_START.md": "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md",
    "CLAIMS_REGISTER.md": "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md",
}

RUNS = [
    {
        "run_id": "trickster_phase1_1200",
        "role": "trickster",
        "family": "trickster_family",
        "phase1": PAPER15_DIR / "trickster_phase1.jsonl",
        "scores": PAPER15_DIR / "trickster_phase2_scores_codex_gpt55.jsonl",
        "manifest": PAPER15_DIR / "trickster_phase1_manifest.json",
        "script": REPO_ROOT / "research/q2_stability/qwen/scripts/phase1_inference_only_v4.py",
        "activation_base": PAPER15_DIR,
        "notes": "Full Qwen trickster Phase 1 inference-only run.",
    },
    {
        "run_id": "editor_phase1_128",
        "role": "editor",
        "family": "procedural_professional_family",
        "phase1": PAPER15_DIR / "editor/editor_phase1_128.jsonl",
        "scores": PAPER15_DIR / "editor/editor_phase2_scores_codex_gpt55.jsonl",
        "manifest": PAPER15_DIR / "editor/editor_phase1_128_manifest.json",
        "script": REPO_ROOT / "research/q2_stability/qwen/scripts/phase1_inference_only_editor.py",
        "activation_base": PAPER15_DIR,
        "notes": "Editor/procedural-adjacent first adaptive chunk.",
    },
    {
        "run_id": "editor_matched64_1024",
        "role": "editor",
        "family": "procedural_professional_family",
        "phase1": PAPER15_DIR / "editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl",
        "scores": PAPER15_DIR / "editor_token_cap_sensitivity/editor_phase2_scores_1024_codex_gpt55.jsonl",
        "manifest": PAPER15_DIR / "editor_token_cap_sensitivity/editor_phase1_matched64_1024_manifest.json",
        "script": REPO_ROOT / "research/q2_stability/qwen/scripts/phase1_inference_editor_matched64_1024.py",
        "activation_base": PAPER15_DIR,
        "notes": "Matched 64-record editor token-cap sensitivity rerun at 1024 max_new_tokens.",
    },
]

TARGET_TERMS = [
    "trickster",
    "jester",
    "joker",
    "chaos",
    "procedural",
    "professional",
    "administrator",
    "admin",
    "worker",
    "worker_bee",
    "evaluator",
    "assistant",
    "bureaucrat",
    "adaptive",
    "phase1",
    "paper1_5",
    "editor",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_startup_status() -> dict[str, Any]:
    fetched: dict[str, dict[str, Any]] = {}
    for name, url in RAW_URLS.items():
        data = urlopen(url, timeout=30).read()
        fetched[name] = {"url": url, "sha256": sha256_bytes(data), "bytes": len(data)}

    manifest_text = urlopen(RAW_URLS["STARTUP_MANIFEST.md"], timeout=30).read().decode("utf-8")
    expected: dict[str, str] = {}
    current_file = None
    for line in manifest_text.splitlines():
        m = re.match(r"### `research/(.+)`", line)
        if m:
            current_file = m.group(1)
            continue
        if current_file and "SHA256 content hash:" in line:
            expected[current_file] = line.split("`")[1]
            current_file = None

    mismatches = []
    for name in ["RESEARCH_STATE.md", "THREAD_START.md", "CLAIMS_REGISTER.md"]:
        if expected.get(name) != fetched[name]["sha256"]:
            mismatches.append(
                {
                    "file": name,
                    "expected": expected.get(name),
                    "observed": fetched[name]["sha256"],
                }
            )
    return {
        "status": "STARTUP VERIFIED" if not mismatches else "STARTUP STALE",
        "fetched": fetched,
        "expected_hashes": expected,
        "mismatches": mismatches,
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"_decode_error": line[:200]})
    return rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_questions() -> list[str]:
    with QUESTIONS_PATH.open() as f:
        return [json.loads(line)["question"] for line in f if line.strip()]


def load_instructions(role: str) -> list[str]:
    path = INSTRUCTIONS_DIR / f"{role}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [item["pos"] for item in data.get("instruction", []) if "pos" in item]


def resolve_activation_path(row: dict[str, Any], run: dict[str, Any]) -> Path | None:
    rel = row.get("activation_relpath")
    if rel:
        candidate = run["activation_base"] / str(rel)
        if candidate.exists():
            return candidate
    raw = row.get("activation_path")
    if raw:
        raw_path = Path(str(raw))
        marker = Path("research/q2_stability/qwen/outputs/paper1_5")
        raw_parts = raw_path.parts
        marker_parts = marker.parts
        for i in range(len(raw_parts) - len(marker_parts) + 1):
            if raw_parts[i : i + len(marker_parts)] == marker_parts:
                candidate = REPO_ROOT / Path(*raw_parts[i:])
                if candidate.exists():
                    return candidate
        if raw_path.exists():
            return raw_path
    return None


def score_index(score_rows: list[dict[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    out = {}
    for row in score_rows:
        try:
            out[(int(row["sp_idx"]), int(row["q_idx"]))] = row
        except Exception:
            continue
    return out


def inspect_tensor(path: Path | None) -> tuple[bool, str, int | None]:
    if not path or not path.exists():
        return False, "", None
    try:
        tensor = torch.load(path, map_location="cpu")
        shape = list(tensor.shape)
        return True, str(shape), int(tensor.numel())
    except Exception as exc:  # pragma: no cover - defensive inventory
        return False, f"load_error:{exc}", None


def read_script_evidence(path: Path) -> dict[str, bool]:
    text = path.read_text() if path.exists() else ""
    return {
        "script_exists": path.exists(),
        "uses_layer48_hook": "model.model.layers[LAYER].register_forward_hook" in text
        or "model.model.layers[48].register_forward_hook" in text,
        "uses_full_forward_use_cache_false": "use_cache=False" in text and "model(input_ids=out" in text,
        "mean_response_tokens": "response_h.mean(0)" in text or "response_h.mean" in text,
        "thinking_disabled": "enable_thinking=False" in text,
    }


def load_basis() -> dict[str, Any]:
    canonical_rows = read_csv_rows(CANONICAL_PCA_PATH)
    canonical = {
        r["persona"]: np.array(
            [
                float(r["activation_pc1"]),
                float(r["activation_pc2"]),
                float(r["activation_pc3"]),
            ],
            dtype=np.float64,
        )
        for r in canonical_rows
    }
    names = sorted([p.stem for p in VECTOR_DIR.glob("*.pt")])
    vectors = []
    for name in names:
        t = torch.load(VECTOR_DIR / f"{name}.pt", map_location="cpu").float()
        vec = t.mean(0) if t.dim() > 1 else t
        vectors.append(np.nan_to_num(vec.numpy().astype(np.float64)))
    x = np.stack(vectors)
    mean = x.mean(axis=0)
    centered = x - mean
    with np.errstate(all="ignore"):
        gram = centered @ centered.T
    eigvals, eigvecs = np.linalg.eigh(gram)
    order = np.argsort(eigvals)[::-1][:3]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = []
    for i in range(3):
        scale = math.sqrt(max(float(eigvals[i]), 1e-12))
        with np.errstate(all="ignore"):
            comp = centered.T @ eigvecs[:, i] / scale
        comp = comp / (np.linalg.norm(comp) + 1e-12)
        components.append(comp)
    components = np.stack(components)
    with np.errstate(all="ignore"):
        reconstructed = centered @ components.T
    verify_idx = [i for i, n in enumerate(names) if n in canonical]
    target = np.stack([canonical[names[i]] for i in verify_idx])
    signs = []
    for i in range(3):
        corr = np.corrcoef(reconstructed[verify_idx, i], target[:, i])[0, 1]
        sign = -1.0 if corr < 0 else 1.0
        signs.append(sign)
        components[i] *= sign
        reconstructed[:, i] *= sign
    abs_err = np.abs(reconstructed[verify_idx] - target)
    return {
        "mean": mean,
        "components": components,
        "debug": {
            "basis_source": "reconstructed_from_qwen_role_vectors_with_sign_alignment_to_canonical_activation_pca3d",
            "canonical_pca_path": str(CANONICAL_PCA_PATH.relative_to(REPO_ROOT)),
            "vector_dir": str(VECTOR_DIR.relative_to(REPO_ROOT)),
            "n_roles_used": len(names),
            "max_abs_coordinate_reproduction_error": float(abs_err.max()),
            "mean_abs_coordinate_reproduction_error": float(abs_err.mean()),
            "sign_alignment": signs,
        },
    }


def project(vec: np.ndarray, basis: dict[str, Any]) -> np.ndarray:
    return (vec.astype(np.float64) - basis["mean"]) @ basis["components"].T


def inventory_candidate_files() -> list[dict[str, Any]]:
    roots = [
        REPO_ROOT / "research/q2_stability/qwen/outputs/paper1_5",
        REPO_ROOT / "research/outputs/extraction_equivalence_audit",
        REPO_ROOT / "research/outputs/public_source_extraction_equivalence",
        REPO_ROOT / "research/outputs/h100_diagnostic_followups",
        REPO_ROOT / "research/q2_stability/qwen/outputs/professional_hierarchy_validation",
    ]
    rows = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel = str(path.relative_to(REPO_ROOT))
            rel_l = rel.lower()
            if not any(term in rel_l for term in TARGET_TERMS):
                continue
            suffix = path.suffix.lower()
            row: dict[str, Any] = {
                "path": rel,
                "artifact_type": suffix.lstrip(".") or "unknown",
                "size_bytes": path.stat().st_size,
                "target_term_hits": ";".join([t for t in TARGET_TERMS if t in rel_l]),
            }
            if suffix == ".jsonl":
                rows_json = read_jsonl(path)
                row["record_count"] = len(rows_json)
                row["sample_keys"] = ";".join(sorted(rows_json[0].keys())) if rows_json else ""
                row["response_text_present"] = any(
                    "response_text" in r or "generated_response" in r for r in rows_json[:10]
                )
                row["score_fields_present"] = any("score" in r or "score_0_to_3" in r for r in rows_json[:10])
            elif suffix == ".csv":
                rows_csv = read_csv_rows(path)
                row["record_count"] = len(rows_csv)
                row["sample_keys"] = ";".join(rows_csv[0].keys()) if rows_csv else ""
            elif suffix == ".pt":
                ok, shape, numel = inspect_tensor(path)
                row["tensor_loadable"] = ok
                row["tensor_shape"] = shape
                row["tensor_numel"] = numel
            rows.append(row)
    return rows


def classify_run(
    run: dict[str, Any],
    phase_rows: list[dict[str, Any]],
    score_rows: list[dict[str, Any]],
    sample_tensor_path: Path | None,
) -> dict[str, Any]:
    script_evidence = read_script_evidence(run["script"])
    activation_count = 0
    response_count = 0
    think_count = 0
    truncation_count = 0
    for row in phase_rows:
        if row.get("response_text"):
            response_count += 1
        if row.get("think_artifact"):
            think_count += 1
        if row.get("truncated"):
            truncation_count += 1
        if resolve_activation_path(row, run):
            activation_count += 1
    sample_ok, sample_shape, sample_numel = inspect_tensor(sample_tensor_path)
    scores = [int(r["score"]) for r in score_rows if str(r.get("score", "")).lstrip("-").isdigit()]
    score_counts = Counter(scores)
    if activation_count == len(phase_rows) and response_count == len(phase_rows) and script_evidence["uses_layer48_hook"]:
        status = "full_reproject_possible"
        explanation = (
            "Saved response text and hook-derived 5120-d activation vectors are present. "
            "Because D01 says the layer-48 hook is the corrected source, these vectors can be locally reprojected without GPU."
        )
    elif response_count == len(phase_rows) and phase_rows:
        status = "judge_only_possible"
        explanation = "Saved response text exists, but usable activation vectors were not found for all records."
    else:
        status = "not_recoverable"
        explanation = "Missing enough response text and activation evidence for reliable local recovery."
    return {
        "run_id": run["run_id"],
        "role": run["role"],
        "family": run["family"],
        "phase1_path": str(run["phase1"].relative_to(REPO_ROOT)),
        "scores_path": str(run["scores"].relative_to(REPO_ROOT)) if run["scores"].exists() else "",
        "manifest_path": str(run["manifest"].relative_to(REPO_ROOT)) if run["manifest"].exists() else "",
        "script_path": str(run["script"].relative_to(REPO_ROOT)) if run["script"].exists() else "",
        "records": len(phase_rows),
        "responses_present": response_count,
        "activation_vectors_present": activation_count,
        "sample_tensor_shape": sample_shape,
        "sample_tensor_numel": sample_numel,
        "think_artifacts": think_count,
        "truncated": truncation_count,
        "score_records": len(score_rows),
        "score0": score_counts.get(0, 0),
        "score1": score_counts.get(1, 0),
        "score2": score_counts.get(2, 0),
        "score3": score_counts.get(3, 0),
        "score_ge2": sum(1 for s in scores if s >= 2),
        "score_eq3": score_counts.get(3, 0),
        "extraction_method_evidence": "; ".join(k for k, v in script_evidence.items() if v),
        "recoverability_status": status,
        "recoverability_explanation": explanation,
        "notes": run["notes"],
    }


def summarize_coordinates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["run_id"], "all")].append(row)
        score = row.get("original_score")
        if isinstance(score, int) or (isinstance(score, str) and score.isdigit()):
            score_int = int(score)
            if score_int >= 2:
                grouped[(row["run_id"], "score_ge2")].append(row)
            if score_int == 3:
                grouped[(row["run_id"], "score_eq3")].append(row)
    out = []
    for (run_id, subset), group in sorted(grouped.items()):
        arr = np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in group])
        out.append(
            {
                "run_id": run_id,
                "subset": subset,
                "n": len(group),
                "mean_pc1": float(arr[:, 0].mean()),
                "mean_pc2": float(arr[:, 1].mean()),
                "mean_pc3": float(arr[:, 2].mean()),
                "sd_pc1": float(arr[:, 0].std(ddof=1)) if len(group) > 1 else 0.0,
                "sd_pc2": float(arr[:, 1].std(ddof=1)) if len(group) > 1 else 0.0,
                "sd_pc3": float(arr[:, 2].std(ddof=1)) if len(group) > 1 else 0.0,
            }
        )
    return out


def main() -> None:
    startup_status = fetch_startup_status()
    if startup_status["status"] != "STARTUP VERIFIED":
        raise SystemExit(f"Startup mismatch: {startup_status['mismatches']}")

    artifact_rows = inventory_candidate_files()
    write_csv(OUTPUT_DIR / "prior_adaptive_artifact_inventory.csv", artifact_rows)

    questions = load_questions()
    instruction_cache = {role: load_instructions(role) for role in {run["role"] for run in RUNS}}
    basis = load_basis()

    recoverability_rows = []
    coordinate_rows = []
    judge_inputs = []
    all_run_context: dict[str, dict[str, Any]] = {}

    for run in RUNS:
        phase_rows = read_jsonl(run["phase1"])
        score_rows = read_jsonl(run["scores"])
        scores_by_pair = score_index(score_rows)
        sample_tensor_path = None
        for row in phase_rows:
            sample_tensor_path = resolve_activation_path(row, run)
            if sample_tensor_path:
                break
        recoverability_rows.append(classify_run(run, phase_rows, score_rows, sample_tensor_path))

        all_run_context[run["run_id"]] = {
            "phase_rows": len(phase_rows),
            "score_rows": len(score_rows),
        }

        for idx, row in enumerate(phase_rows):
            try:
                sp_idx = int(row["sp_idx"])
                q_idx = int(row["q_idx"])
            except Exception:
                continue
            score_row = scores_by_pair.get((sp_idx, q_idx), {})
            response = row.get("response_text") or row.get("generated_response") or ""
            activation_path = resolve_activation_path(row, run)
            response_id = f"{run['run_id']}:sp{sp_idx}_q{q_idx}"

            judge_inputs.append(
                {
                    "source_run_id": run["run_id"],
                    "response_id": response_id,
                    "role": run["role"],
                    "role_family": run["family"],
                    "system_prompt_index": sp_idx,
                    "question_index": q_idx,
                    "role_instruction": instruction_cache.get(run["role"], [""] * (sp_idx + 1))[sp_idx]
                    if sp_idx < len(instruction_cache.get(run["role"], []))
                    else "",
                    "extraction_question": questions[q_idx] if q_idx < len(questions) else "",
                    "generated_response": response,
                    "original_score": score_row.get("score"),
                    "original_judge": score_row.get("judge_model"),
                    "original_rationale": score_row.get("rationale"),
                    "truncated": row.get("truncated"),
                    "think_artifact": row.get("think_artifact"),
                }
            )

            if activation_path and activation_path.exists():
                tensor = torch.load(activation_path, map_location="cpu").float()
                vec = tensor.numpy().astype(np.float64)
                coords = project(vec, basis)
                score = score_row.get("score")
                score_class = ""
                if isinstance(score, int) or (isinstance(score, str) and score.isdigit()):
                    score_int = int(score)
                    if score_int >= 2:
                        score_class = "score_ge2"
                    if score_int == 3:
                        score_class = "score_eq3"
                coordinate_rows.append(
                    {
                        "run_id": run["run_id"],
                        "role": run["role"],
                        "family": run["family"],
                        "response_id": response_id,
                        "sp_idx": sp_idx,
                        "q_idx": q_idx,
                        "original_score": score,
                        "score_class": score_class,
                        "truncated": row.get("truncated"),
                        "activation_relpath": str(activation_path.relative_to(REPO_ROOT)),
                        "pc1": float(coords[0]),
                        "pc2": float(coords[1]),
                        "pc3": float(coords[2]),
                    }
                )

    write_csv(OUTPUT_DIR / "prior_adaptive_recoverability_table.csv", recoverability_rows)
    write_csv(OUTPUT_DIR / "prior_adaptive_corrected_coordinates.csv", coordinate_rows)
    summary_rows = summarize_coordinates(coordinate_rows)
    write_csv(OUTPUT_DIR / "prior_adaptive_corrected_cloud_summary.csv", summary_rows)

    with (OUTPUT_DIR / "prior_adaptive_gpt41_judge_inputs.jsonl").open("w") as f:
        for row in judge_inputs:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    debug = {
        "startup_status": startup_status,
        "pca_basis_debug": basis["debug"],
        "run_context": all_run_context,
        "gpt41_rejudge_run": False,
        "gpt41_rejudge_reason": "No explicit run_gpt41_rejudge=true configuration was present; this audit only prepared judge inputs.",
    }
    (OUTPUT_DIR / "audit_debug.json").write_text(json.dumps(debug, indent=2) + "\n")

    write_reports(startup_status, recoverability_rows, summary_rows, artifact_rows, len(judge_inputs), basis["debug"])


def md_table(rows: list[dict[str, Any]], cols: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rows:
        vals = []
        for col in cols:
            val = row.get(col, "")
            if isinstance(val, float):
                val = f"{val:.6f}"
            vals.append(str(val).replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def write_reports(
    startup_status: dict[str, Any],
    recoverability_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    artifact_rows: list[dict[str, Any]],
    judge_input_count: int,
    basis_debug: dict[str, Any],
) -> None:
    inventory_summary = Counter(row.get("artifact_type", "unknown") for row in artifact_rows)
    family_summary = Counter(row["family"] for row in recoverability_rows)
    status_summary = Counter(row["recoverability_status"] for row in recoverability_rows)

    inventory_report = f"""# Prior Adaptive Run Inventory

Startup status: **{startup_status['status']}**.

This audit searched prior adaptive and adjacent extraction artifacts for the
trickster family (`trickster`, `jester`, `joker`, `chaos`) and
procedural/professional family (`editor`, `evaluator`, `assistant`,
`professional`, `administrator`, `worker`, `bureaucrat`, and related terms).

## Candidate Artifact Counts

{md_table([{'artifact_type': k, 'count': v} for k, v in sorted(inventory_summary.items())], ['artifact_type', 'count'])}

## Explicit Prior Adaptive Runs Found

{md_table(recoverability_rows, ['run_id', 'role', 'family', 'records', 'score_records', 'score_ge2', 'score_eq3', 'truncated', 'think_artifacts'])}

Notes:

- No local adaptive extraction run was found for `jester`, `joker`, or a literal `procedural` persona.
- The procedural-professional recovery evidence is represented by the `editor` adaptive runs plus separate professional-hierarchy validation artifacts.
- Full file-level inventory is in `prior_adaptive_artifact_inventory.csv`.
"""
    (OUTPUT_DIR / "prior_adaptive_run_inventory_report.md").write_text(inventory_report)

    recoverability_report = f"""# Prior Adaptive Recoverability Report

Startup status: **{startup_status['status']}**.

## Recovery Classification

{md_table(recoverability_rows, ['run_id', 'role', 'records', 'activation_vectors_present', 'sample_tensor_shape', 'score_ge2', 'score_eq3', 'recoverability_status'])}

## D01 Boundary Interpretation

The inspected adaptive Phase 1 scripts capture activations using a forward hook
on `model.model.layers[48]` during a full generated-sequence forward pass with
`use_cache=False`, then mean-pool over response tokens only. The later A100
boundary test resolved D01 by showing this hook corresponds to
`outputs.hidden_states[49]`, not `outputs.hidden_states[48]`.

Therefore, these hook-derived activation shards do **not** require GPU
regeneration to correct a hidden-state index error. They can be locally reused
and reprojected into the canonical Qwen PCA basis. What cannot be recovered
locally is an alternative hidden-state-boundary extraction for runs that did not
save hook vectors.

## Status Summary

{md_table([{'recoverability_status': k, 'count': v} for k, v in sorted(status_summary.items())], ['recoverability_status', 'count'])}

## Family Summary

{md_table([{'family': k, 'count': v} for k, v in sorted(family_summary.items())], ['family', 'count'])}
"""
    (OUTPUT_DIR / "prior_adaptive_recoverability_report.md").write_text(recoverability_report)

    rejudge_plan = f"""# GPT-4.1 Rejudge Plan for Prior Adaptive Runs

Prepared judge input file: `prior_adaptive_gpt41_judge_inputs.jsonl`

Prepared responses: **{judge_input_count}**.

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
OPENAI_API_KEY=\"$OPENAI_API_KEY\" python3 research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py
```

or write a small one-pass scorer using `prior_adaptive_gpt41_judge_inputs.jsonl`
as input and this rubric.
"""
    (OUTPUT_DIR / "prior_adaptive_gpt41_rejudge_plan.md").write_text(rejudge_plan)

    boundary_report = f"""# Prior Adaptive Boundary Shift Report

## Conclusion

The prior adaptive Phase 1 activation shards for trickster and editor are
already hook-derived `model.model.layers[48]` response-token pooled vectors.
Under the corrected D01 boundary result, these correspond to the corrected
source (`hidden_states[49]` equivalent), not the mistaken `hidden_states[48]`
boundary.

## Local Reprojection

The audit reconstructed the canonical Qwen PCA basis from the committed
Qwen role vectors and aligned signs against
`canonical_activation_pca3d.csv`.

Basis reproduction debug:

```json
{json.dumps(basis_debug, indent=2)}
```

Corrected/local coordinates are written to
`prior_adaptive_corrected_coordinates.csv`, and cloud summaries are written to
`prior_adaptive_corrected_cloud_summary.csv`.

## What Would Still Require GPU

If a future question requires raw token-level hidden states or direct comparison
against `outputs.hidden_states[48]`/`[49]` for these exact prompts, that cannot be
recovered from the mean-pooled activation shards. It would require regenerating
or rerunning forward passes on GPU.
"""
    (OUTPUT_DIR / "prior_adaptive_boundary_shift_report.md").write_text(boundary_report)

    decision_report = f"""# Prior Adaptive Recovery Decision Report

## Decision

The trickster adaptive extraction run is recoverable and reusable for local
analysis under the corrected D01 boundary because it saved 1200 hook-derived
activation vectors and full response text. The editor/procedural-adjacent runs
are also locally reprojectable, but their role-expression yield remains weak;
their failure is better interpreted as an elicitation/judge-yield problem than
as a D01 boundary problem.

## Evidence

{md_table(recoverability_rows, ['run_id', 'role', 'records', 'responses_present', 'activation_vectors_present', 'score_ge2', 'score_eq3', 'recoverability_status'])}

## Corrected Cloud Summary

{md_table(summary_rows, ['run_id', 'subset', 'n', 'mean_pc1', 'mean_pc2', 'mean_pc3', 'sd_pc1', 'sd_pc2', 'sd_pc3'])}

## Recommended Next Action

Do not rerun GPU just to recover these prior adaptive runs. Instead:

1. If evaluator sensitivity matters for Paper 1.5, run GPT-4.1 rejudging on the prepared JSONL.
2. Use the existing hook-derived vectors for local PCA/cloud comparisons.
3. Reserve GPU for new no-label or activation-cloud experiments where raw activations are not already saved.
"""
    (OUTPUT_DIR / "prior_adaptive_recovery_decision_report.md").write_text(decision_report)


if __name__ == "__main__":
    main()
