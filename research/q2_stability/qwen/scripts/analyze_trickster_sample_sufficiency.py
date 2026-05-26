#!/usr/bin/env python3
"""Estimate sample-size sufficiency for Qwen trickster role-vector extraction.

Local CPU-only analysis. No model loading, no API calls, and no mutation of
activation shards. If the current Python lacks torch but the repo venv has it,
the script re-executes itself under `.venv/bin/python`.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any


try:
    import numpy as np
    import torch
except ModuleNotFoundError:
    repo = Path(__file__).resolve().parents[4]
    venv_python = repo / ".venv/bin/python"
    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])
    raise


REPO_ROOT = Path(__file__).resolve().parents[4]
QWEN_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = QWEN_ROOT / "outputs/paper1_5"
JSONL = OUT_DIR / "trickster_phase1.jsonl"
INTEGRITY = OUT_DIR / "phase1_final_integrity.json"
ACTIVATION_DIR = OUT_DIR / "activations_trickster"
DEFAULT_SCORES_JSONL = OUT_DIR / "trickster_phase2_scores_gpt41mini.jsonl"
ROLE_VECTOR_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
DEFAULT_OUTPUT_PREFIX = "trickster_sample_sufficiency"

EXPECTED_RECORDS = 1200
EXPECTED_DIM = 5120
BOOTSTRAP_REPS = 500
RNG_SEED = 20260526
BASE_N_GRID = [4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def unit(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(unit(a), unit(b)))


def percentiles(values: np.ndarray) -> dict[str, float]:
    return {
        "p05": float(np.percentile(values, 5)),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
    }


def load_phase1_records() -> list[dict[str, Any]]:
    records = []
    with JSONL.open() as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                row = json.loads(line)
                row["_line_no"] = line_no
                row["truncated_bool"] = bool(row.get("truncated"))
                records.append(row)
    return records


def load_scores(scores_jsonl: Path) -> tuple[dict[tuple[int, int], float], dict[str, Any]]:
    if not scores_jsonl.exists():
        return {}, {"present": False, "path": rel(scores_jsonl)}

    score_keys = [
        "score", "role_score", "final_score", "phase2_score",
        "role_expression_score", "trickster_score",
    ]
    scores: dict[tuple[int, int], float] = {}
    key_counts: dict[str, int] = defaultdict(int)
    unparsable = 0
    with scores_jsonl.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            found_key = None
            found_value = None
            for key in score_keys:
                if key in row and row[key] not in (None, ""):
                    try:
                        found_value = float(row[key])
                        found_key = key
                        break
                    except (TypeError, ValueError):
                        continue
            if found_key is None:
                unparsable += 1
                continue
            scores[(int(row["sp_idx"]), int(row["q_idx"]))] = found_value  # type: ignore[arg-type]
            key_counts[found_key] += 1

    return scores, {
        "present": True,
        "path": rel(scores_jsonl),
        "parsed_scores": len(scores),
        "score_key_counts": dict(key_counts),
        "unparsable_lines": unparsable,
    }


def find_lu_trickster_tensor() -> tuple[Path, list[str]]:
    candidates = sorted(ROLE_VECTOR_DIR.glob("*trickster*.pt"))
    exact = ROLE_VECTOR_DIR / "trickster.pt"
    candidate_names = [rel(path) for path in candidates]
    if exact.exists():
        return exact, candidate_names
    if len(candidates) == 1:
        return candidates[0], candidate_names
    raise RuntimeError(f"Ambiguous or missing trickster tensor candidates: {candidate_names}")


def load_activations(records: list[dict[str, Any]]) -> tuple[np.ndarray, list[dict[str, Any]], list[str]]:
    vectors = []
    kept = []
    errors = []
    for row in records:
        relpath = row.get("activation_relpath")
        if not relpath:
            errors.append(f"missing activation_relpath for line {row['_line_no']}")
            continue
        path = OUT_DIR / relpath
        if not path.exists():
            errors.append(f"missing activation file: {relpath}")
            continue
        try:
            tensor = torch.load(path, map_location="cpu")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"load error {relpath}: {exc}")
            continue
        arr = tensor.detach().float().cpu().numpy() if hasattr(tensor, "detach") else np.asarray(tensor)
        if arr.shape != (EXPECTED_DIM,):
            errors.append(f"bad shape {relpath}: {arr.shape}")
            continue
        vectors.append(arr.astype(np.float32))
        kept.append(row)
    if not vectors:
        raise RuntimeError("No activations loaded")
    return np.stack(vectors), kept, errors


def row_to_mean_stats(matrix: np.ndarray, mean_vec: np.ndarray) -> dict[str, Any]:
    mat = matrix.astype(np.float64, copy=False)
    mean_unit = unit(mean_vec.astype(np.float64, copy=False))
    row_norms = np.linalg.norm(mat, axis=1, keepdims=True)
    row_units = mat / np.clip(row_norms, 1e-12, None)
    cosines = np.sum(row_units * mean_unit[None, :], axis=1)
    stats = percentiles(cosines)
    stats.update({
        "count": int(len(cosines)),
        "min": float(np.min(cosines)),
        "max": float(np.max(cosines)),
    })
    return stats


def subset_n_grid(n_total: int) -> list[int]:
    useful = {n for n in BASE_N_GRID if n <= n_total}
    for n in [n_total // 4, n_total // 2, (3 * n_total) // 4, n_total]:
        if 4 <= n <= n_total:
            useful.add(n)
    return sorted(useful)


def bootstrap_subset(
    matrix: np.ndarray,
    subset_full_mean: np.ndarray,
    lu_mean: np.ndarray,
    rng: np.random.Generator,
) -> list[dict[str, Any]]:
    n_total = matrix.shape[0]
    if n_total < 16:
        return []
    curves = []
    for n in subset_n_grid(n_total):
        reps = 1 if n == n_total else BOOTSTRAP_REPS
        self_cosines = np.empty(reps, dtype=np.float32)
        lu_cosines = np.empty(reps, dtype=np.float32)
        for rep in range(reps):
            if n == n_total:
                sample = matrix
            else:
                idx = rng.choice(n_total, size=n, replace=False)
                sample = matrix[idx]
            sample_mean = sample.mean(axis=0)
            self_cosines[rep] = cosine(sample_mean, subset_full_mean)
            lu_cosines[rep] = cosine(sample_mean, lu_mean)
        self_stats = percentiles(self_cosines)
        lu_stats = percentiles(lu_cosines)
        curves.append({
            "n": int(n),
            "reps": int(reps),
            "self_cosine": self_stats,
            "lu_cosine": lu_stats,
            "lu_interval_width": float(lu_stats["p95"] - lu_stats["p05"]),
        })
    return curves


def criterion_minima(curves: list[dict[str, Any]], lu_dispersion: float) -> dict[str, int | None]:
    out: dict[str, int | None] = {
        "criterion_a_self_p05_ge_0_95": None,
        "criterion_b_self_p05_ge_0_98": None,
        "criterion_c_lu_std_le_lu_dispersion_half": None,
        "criterion_d_lu_interval_width_le_lu_dispersion": None,
    }
    for row in curves:
        n = int(row["n"])
        if out["criterion_a_self_p05_ge_0_95"] is None and row["self_cosine"]["p05"] >= 0.95:
            out["criterion_a_self_p05_ge_0_95"] = n
        if out["criterion_b_self_p05_ge_0_98"] is None and row["self_cosine"]["p05"] >= 0.98:
            out["criterion_b_self_p05_ge_0_98"] = n
        if out["criterion_c_lu_std_le_lu_dispersion_half"] is None and row["lu_cosine"]["std"] <= lu_dispersion / 2:
            out["criterion_c_lu_std_le_lu_dispersion_half"] = n
        if out["criterion_d_lu_interval_width_le_lu_dispersion"] is None and row["lu_interval_width"] <= lu_dispersion:
            out["criterion_d_lu_interval_width_le_lu_dispersion"] = n
    return out


def adaptive_stopping(matrix: np.ndarray, lu_mean: np.ndarray, lu_dispersion: float) -> dict[str, Any]:
    if matrix.shape[0] < 16:
        return {"first_n": None, "reason": "subset has fewer than 16 activations"}
    running = []
    cosines = []
    first_n = None
    for i, row in enumerate(matrix, 1):
        running.append(row)
        mean_vec = np.mean(running, axis=0)
        cosines.append(cosine(mean_vec, lu_mean))
        if i >= 16:
            window = np.array(cosines[max(0, i - 24): i], dtype=np.float32)
            if len(window) >= 8:
                se = float(np.std(window, ddof=1) / np.sqrt(len(window)))
                if se <= lu_dispersion / 2:
                    first_n = i
                    break
    final_window = np.array(cosines[-min(24, len(cosines)):], dtype=np.float32)
    final_se = (
        float(np.std(final_window, ddof=1) / np.sqrt(len(final_window)))
        if len(final_window) > 1 else None
    )
    return {
        "first_n": first_n,
        "criterion": "n >= 16 and rolling SE of cosine(running_mean, Lu_mean) <= lu_dispersion / 2",
        "final_cosine_to_lu": float(cosines[-1]),
        "final_rolling_se": final_se,
        "lu_dispersion_half": lu_dispersion / 2,
    }


def subset_report(
    name: str,
    matrix: np.ndarray,
    full_1200_mean: np.ndarray,
    lu_mean: np.ndarray,
) -> dict[str, Any]:
    mean_vec = matrix.mean(axis=0)
    internal = row_to_mean_stats(matrix, mean_vec)
    return {
        "name": name,
        "n_total": int(matrix.shape[0]),
        "cosine_candidate_mean_to_lu_mean": cosine(mean_vec, lu_mean),
        "cosine_candidate_mean_to_full_1200_mean": cosine(mean_vec, full_1200_mean),
        "internal_dispersion_std_cosine_to_subset_mean": internal["std"],
        "internal_row_to_mean": internal,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores-path", type=Path, default=DEFAULT_SCORES_JSONL)
    parser.add_argument("--output-prefix", default=DEFAULT_OUTPUT_PREFIX)
    args = parser.parse_args()

    scores_jsonl = args.scores_path
    if not scores_jsonl.is_absolute():
        scores_jsonl = REPO_ROOT / scores_jsonl
    out_json = OUT_DIR / f"{args.output_prefix}.json"
    out_md = OUT_DIR / f"{args.output_prefix}.md"
    out_csv = OUT_DIR / f"{args.output_prefix}_curves.csv"

    records = load_phase1_records()
    pairs = {(int(row["sp_idx"]), int(row["q_idx"])) for row in records}
    scores, score_meta = load_scores(scores_jsonl)

    lu_path, lu_candidates = find_lu_trickster_tensor()
    lu_tensor = torch.load(lu_path, map_location="cpu").float().cpu().numpy()
    if lu_tensor.ndim != 2 or lu_tensor.shape[1] != EXPECTED_DIM:
        raise RuntimeError(f"Unexpected Lu trickster tensor shape: {lu_tensor.shape}")
    lu_mean = lu_tensor.mean(axis=0)
    lu_internal = row_to_mean_stats(lu_tensor, lu_mean)
    lu_dispersion = float(lu_internal["std"])

    activations, kept_records, activation_errors = load_activations(records)
    full_1200_mean = activations.mean(axis=0)
    record_indices = {(int(r["sp_idx"]), int(r["q_idx"])): i for i, r in enumerate(kept_records)}

    validation = {
        "record_count": len(records),
        "expected_record_count": EXPECTED_RECORDS,
        "unique_sp_q_pairs": len(pairs),
        "expected_unique_sp_q_pairs": EXPECTED_RECORDS,
        "activation_count": int(activations.shape[0]),
        "activation_dim": int(activations.shape[1]),
        "activation_error_count": len(activation_errors),
        "valid": (
            len(records) == EXPECTED_RECORDS
            and len(pairs) == EXPECTED_RECORDS
            and activations.shape == (EXPECTED_RECORDS, EXPECTED_DIM)
            and not activation_errors
        ),
    }

    subsets: dict[str, list[int]] = {
        "all_1200": list(range(len(kept_records))),
        "non_truncated": [i for i, r in enumerate(kept_records) if not r["truncated_bool"]],
        "truncated": [i for i, r in enumerate(kept_records) if r["truncated_bool"]],
    }
    for sp_idx in sorted({int(row["sp_idx"]) for row in kept_records}):
        subsets[f"sp_idx_{sp_idx}"] = [
            i for i, r in enumerate(kept_records) if int(r["sp_idx"]) == sp_idx
        ]

    if scores:
        score_eq_3 = []
        score_ge_2 = []
        non_truncated_score_eq_3 = []
        non_truncated_score_ge_2 = []
        for key, score in scores.items():
            idx = record_indices.get(key)
            if idx is None:
                continue
            if score == 3:
                score_eq_3.append(idx)
                if not kept_records[idx]["truncated_bool"]:
                    non_truncated_score_eq_3.append(idx)
            if score >= 2:
                score_ge_2.append(idx)
                if not kept_records[idx]["truncated_bool"]:
                    non_truncated_score_ge_2.append(idx)
        subsets["score_eq_3"] = score_eq_3
        subsets["score_ge_2"] = score_ge_2
        subsets["non_truncated_score_eq_3"] = non_truncated_score_eq_3
        subsets["non_truncated_score_ge_2"] = non_truncated_score_ge_2

    rng = np.random.default_rng(RNG_SEED)
    subset_summaries: dict[str, dict[str, Any]] = {}
    curves: list[dict[str, Any]] = []
    adaptive: dict[str, dict[str, Any]] = {}

    for name, idxs in subsets.items():
        if not idxs:
            subset_summaries[name] = {"name": name, "n_total": 0, "empty": True}
            continue
        matrix = activations[np.array(idxs, dtype=np.int32)]
        summary = subset_report(name, matrix, full_1200_mean, lu_mean)
        subset_curves = bootstrap_subset(matrix, matrix.mean(axis=0), lu_mean, rng)
        minima = criterion_minima(subset_curves, lu_dispersion)
        summary["criterion_minima"] = minima
        subset_summaries[name] = summary
        for row in subset_curves:
            flat = {
                "subset": name,
                "subset_n_total": summary["n_total"],
                "n": row["n"],
                "reps": row["reps"],
                "self_p05": row["self_cosine"]["p05"],
                "self_p50": row["self_cosine"]["p50"],
                "self_p95": row["self_cosine"]["p95"],
                "self_mean": row["self_cosine"]["mean"],
                "self_std": row["self_cosine"]["std"],
                "lu_p05": row["lu_cosine"]["p05"],
                "lu_p50": row["lu_cosine"]["p50"],
                "lu_p95": row["lu_cosine"]["p95"],
                "lu_mean": row["lu_cosine"]["mean"],
                "lu_std": row["lu_cosine"]["std"],
                "lu_interval_width": row["lu_interval_width"],
            }
            curves.append(flat)
        if name in {
            "all_1200", "non_truncated", "score_eq_3", "score_ge_2",
            "non_truncated_score_eq_3", "non_truncated_score_ge_2",
        }:
            adaptive[name] = adaptive_stopping(matrix, lu_mean, lu_dispersion)

    all_min = subset_summaries["all_1200"]["criterion_minima"]
    non_trunc_min = subset_summaries["non_truncated"]["criterion_minima"]
    trunc_min = subset_summaries["truncated"]["criterion_minima"]
    sp_a_values = [
        subset_summaries[f"sp_idx_{sp}"]["criterion_minima"]["criterion_a_self_p05_ge_0_95"]
        for sp in range(5)
    ]
    sp_valid_a = [v for v in sp_a_values if v is not None]

    default_target = 64
    raw_min_acceptable = all_min["criterion_a_self_p05_ge_0_95"] or 64
    raw_strict_target = all_min["criterion_b_self_p05_ge_0_98"] or 128
    min_acceptable = max(16, raw_min_acceptable)
    strict_target = max(16, raw_strict_target)
    if strict_target <= 64:
        lu_64_assessment = "appropriate"
    elif min_acceptable <= 64:
        lu_64_assessment = "appropriate for 0.95 self-stability but below the stricter 0.98 criterion"
    else:
        lu_64_assessment = "insufficient under the provisional self-stability criterion"

    truncation_changes = (
        non_trunc_min["criterion_a_self_p05_ge_0_95"]
        != trunc_min["criterion_a_self_p05_ge_0_95"]
    )
    score_pending = not bool(scores)

    recommendation = {
        "basis": "Based on all available Phase 1 activations before role-expression scoring.",
        "minimum_acceptable_n": min_acceptable,
        "raw_bootstrap_minimum_n": raw_min_acceptable,
        "minimum_criterion": "Criterion A: p05 cosine(sample_mean, subset_full_mean) >= 0.95",
        "default_target_n": default_target,
        "strict_target_n": strict_target,
        "raw_strict_bootstrap_minimum_n": raw_strict_target,
        "operational_floor_n": 16,
        "lu_64_assessment": lu_64_assessment,
        "truncation_materially_changes_sample_sufficiency": bool(truncation_changes),
        "adaptive_stopping": (
            "Use both fixed n and adaptive stopping: collect to the fixed target unless the "
            "running SE criterion is satisfied later, and always preserve eligibility metadata."
        ),
        "phase2_score_conditioned_analysis_required": score_pending,
        "provisional_workflow_rule": (
            "Until Phase 2 scoring exists, use a fixed target of 64 available activations per "
            "persona as the provisional default and require at least the Criterion A minimum "
            "from this analysis; once scores exist, rerun this script and set the target from "
            "score>=2 and score==3 subsets, not from all available activations."
        ),
    }

    output = {
        "date": "2026-05-26",
        "model_used": "GPT-5.5",
        "inputs": {
            "phase1_jsonl": rel(JSONL),
            "integrity_json": rel(INTEGRITY),
            "activation_dir": rel(ACTIVATION_DIR),
            "phase2_scores_jsonl": rel(scores_jsonl),
            "phase2_scores_present": bool(scores),
            "lu_trickster_reference": rel(lu_path),
            "lu_trickster_candidates": lu_candidates,
        },
        "validation": validation,
        "phase2_score_metadata": score_meta,
        "lu_reference": {
            "tensor_shape": list(lu_tensor.shape),
            "lu_row_to_mean_cosine": lu_internal,
            "lu_dispersion": lu_dispersion,
            "lu_internal_p05": lu_internal["p05"],
            "lu_internal_p50": lu_internal["p50"],
            "lu_internal_p95": lu_internal["p95"],
        },
        "candidate_subsets": subset_summaries,
        "adaptive_stopping": adaptive,
        "recommendation": recommendation,
    }

    out_json.write_text(json.dumps(output, indent=2) + "\n")
    with out_csv.open("w", newline="") as f:
        fieldnames = [
            "subset", "subset_n_total", "n", "reps",
            "self_p05", "self_p50", "self_p95", "self_mean", "self_std",
            "lu_p05", "lu_p50", "lu_p95", "lu_mean", "lu_std",
            "lu_interval_width",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(curves)

    md = [
        "# Trickster Sample Sufficiency Analysis",
        "",
        "Date: 2026-05-26",
        "Model used for analysis: GPT-5.5",
        "",
        "## Scope",
        "",
        "This is a local CPU-only analysis of available Phase 1 activations. It does not validate role expression and does not claim Lu replication success. Score-conditioned analysis is added automatically if the Phase 2 score JSONL exists.",
        "",
        "## Validation",
        "",
        f"- Records: {validation['record_count']} / {EXPECTED_RECORDS}",
        f"- Unique `(sp_idx, q_idx)` pairs: {validation['unique_sp_q_pairs']} / {EXPECTED_RECORDS}",
        f"- Activations loaded: {validation['activation_count']} with dimension {validation['activation_dim']}",
        f"- Activation load errors: {validation['activation_error_count']}",
        f"- Lu reference tensor: `{rel(lu_path)}` with shape `{list(lu_tensor.shape)}`",
        f"- Phase 2 scores present: `{bool(scores)}`",
        "",
        "## Lu Reference Dispersion",
        "",
        f"Lu row-to-mean cosine p05/p50/p95: `{lu_internal['p05']:.6f}` / `{lu_internal['p50']:.6f}` / `{lu_internal['p95']:.6f}`.",
        f"Lu dispersion, defined as std cosine(row_i, Lu_mean), is `{lu_dispersion:.6f}`.",
        "",
        "## Candidate Subsets",
        "",
        "| Subset | n | cos(mean, Lu mean) | cos(mean, full 1200 mean) | internal std | Criterion A n | Criterion B n | Criterion C n | Criterion D n |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["all_1200", "non_truncated", "truncated", "sp_idx_0", "sp_idx_1", "sp_idx_2", "sp_idx_3", "sp_idx_4"]:
        s = subset_summaries[name]
        minima = s.get("criterion_minima", {})
        md.append(
            f"| {name} | {s['n_total']} | "
            f"{s['cosine_candidate_mean_to_lu_mean']:.6f} | "
            f"{s['cosine_candidate_mean_to_full_1200_mean']:.6f} | "
            f"{s['internal_dispersion_std_cosine_to_subset_mean']:.6f} | "
            f"{minima.get('criterion_a_self_p05_ge_0_95')} | "
            f"{minima.get('criterion_b_self_p05_ge_0_98')} | "
            f"{minima.get('criterion_c_lu_std_le_lu_dispersion_half')} | "
            f"{minima.get('criterion_d_lu_interval_width_le_lu_dispersion')} |"
        )

    md.extend([
        "",
        "## Operational Answers",
        "",
        "### 1. What is the best current estimate of the minimum n needed for a stable trickster vector?",
        "",
        f"Based on all available Phase 1 activations, the raw bootstrap Criterion A minimum is `{raw_min_acceptable}`, but the provisional operational minimum is `{min_acceptable}` after applying the n>=16 floor used by the adaptive stopping rule. The stricter target is `{strict_target}`.",
        "",
        "### 2. Under which criterion is that estimate made?",
        "",
        f"The raw estimate uses {recommendation['minimum_criterion']}. The operational estimate applies a floor of 16 activations because pre-scoring subsets below that size are too brittle to treat as a workflow rule. The stricter target uses Criterion B, p05 cosine(sample_mean, subset_full_mean) >= 0.98.",
        "",
        "### 3. How does the estimate compare to Lu et al.'s fixed 64-row cap?",
        "",
        f"Lu's fixed 64-row cap is `{lu_64_assessment}` for trickster under this pre-scoring analysis.",
        "",
        "### 4. Does truncation change the answer?",
        "",
        f"Truncation materially changes the Criterion A minimum: `{truncation_changes}`. Non-truncated Criterion A n is `{non_trunc_min['criterion_a_self_p05_ge_0_95']}`, while truncated Criterion A n is `{trunc_min['criterion_a_self_p05_ge_0_95']}`.",
        "",
        "### 5. Are system prompts equally efficient, or does one prompt produce more stable geometry?",
        "",
        f"System prompts are not identical. Criterion A minima across `sp_idx` are `{sp_a_values}`, so prompt-level efficiency should remain visible in future extraction decisions.",
        "",
        "### 6. Can future persona extractions use an adaptive stopping rule?",
        "",
        "Yes, but use it alongside a fixed target. The adaptive SE rule is useful as an early warning and stopping diagnostic, but fixed n keeps personas comparable.",
        "",
        "### 7. What fixed target n should be used until Phase 2 scoring is available?",
        "",
        f"Use `n={default_target}` available activations as the provisional default target, while preserving all metadata needed to rerun the score-conditioned analysis.",
        "",
        "### 8. What should change after score-conditioned analysis is possible?",
        "",
        "Rerun this same script after score output exists and set the target from `score>=2` and `score==3` subsets rather than from all available activations.",
        "",
        "### 9. What should be written into the project workflow as the provisional sample-size rule?",
        "",
        recommendation["provisional_workflow_rule"],
        "",
        "## Interpretation Guardrails",
        "",
        "This analysis uses all available Phase 1 activations and truncation-defined subsets. It does not claim that all 1200 activations are qualifying role-expression samples, and score-conditioned analysis remains pending.",
    ])
    out_md.write_text("\n".join(md).rstrip() + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
