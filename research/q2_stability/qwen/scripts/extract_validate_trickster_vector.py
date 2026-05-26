#!/usr/bin/env python3
"""Extract and validate Qwen trickster vectors against Lu et al. reference.

This script is intentionally dependency-gated on complete Phase 2 scoring.
It will not compute vectors from unscored or partially scored Phase 1 records.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


MODEL_USED = "GPT-5.5"
REPO_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_DIR = REPO_ROOT / "research/q2_stability/qwen/outputs/paper1_5"
PHASE1_PATH = OUTPUT_DIR / "trickster_phase1.jsonl"
PHASE2_PATH = OUTPUT_DIR / "trickster_phase2_scores_gpt41mini.jsonl"
INTEGRITY_PATHS = [
    OUTPUT_DIR / "phase1_final_integrity.json",
    OUTPUT_DIR / "final_phase1_integrity.json",
]
ACTIVATION_BASE = OUTPUT_DIR
VECTOR_OUT_DIR = OUTPUT_DIR / "vector_candidates"
ROLE_VECTOR_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
LU_PERSONA = "trickster"
EXPECTED_RECORDS = 1200
EXPECTED_HIDDEN_DIM = 5120
BOOTSTRAP_SAMPLES = 1000
BOOTSTRAP_SEED = 20260526


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rec["_line_no"] = line_no
            records.append(rec)
    return records


def score_from_record(rec: dict[str, Any]) -> int | None:
    """Read a Phase 2 role-expression score from known plausible fields."""

    candidate_keys = [
        "score",
        "phase2_score",
        "trickster_score",
        "role_score",
        "role_expression_score",
        "expression_score",
        "qualifying_score",
    ]
    for key in candidate_keys:
        if key in rec and rec[key] is not None:
            try:
                return int(rec[key])
            except (TypeError, ValueError):
                pass

    # Some judge outputs store nested structured data.
    for parent_key in ("judge", "judgment", "result", "scores"):
        parent = rec.get(parent_key)
        if isinstance(parent, dict):
            nested = score_from_record(parent)
            if nested is not None:
                return nested

    return None


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    a = a.float()
    b = b.float()
    return float(torch.nn.functional.cosine_similarity(a, b, dim=0).item())


def normalize_rows(x: torch.Tensor) -> torch.Tensor:
    x = x.float()
    return x / x.norm(dim=1, keepdim=True).clamp_min(1e-12)


def load_activation(rec: dict[str, Any]) -> torch.Tensor:
    rel = rec.get("activation_relpath")
    if not rel:
        raise ValueError(f"Missing activation_relpath for {(rec.get('sp_idx'), rec.get('q_idx'))}")
    path = ACTIVATION_BASE / rel
    if not path.exists():
        raise FileNotFoundError(path)
    tensor = torch.load(path, map_location="cpu").float()
    if tuple(tensor.shape) != (EXPECTED_HIDDEN_DIM,):
        raise ValueError(f"{path} has shape {tuple(tensor.shape)}, expected ({EXPECTED_HIDDEN_DIM},)")
    return tensor


def find_lu_trickster_tensor() -> Path:
    plausible = sorted(
        set(ROLE_VECTOR_DIR.glob("*trickster*.pt"))
        | set(ROLE_VECTOR_DIR.glob("*jester*.pt"))
    )
    exact = ROLE_VECTOR_DIR / "trickster.pt"
    if exact.exists():
        return exact
    names = [p.name for p in plausible]
    raise FileNotFoundError(
        "Could not find canonical Lu trickster tensor at "
        f"{exact}. Plausible role-vector files found: {names}"
    )


def pairwise_cosine_dispersion(activations: torch.Tensor) -> dict[str, float | None]:
    n = activations.shape[0]
    if n < 2:
        return {"pairwise_cosine_mean": None, "pairwise_cosine_std": None}
    x = normalize_rows(activations)
    sims = x @ x.T
    upper = sims[torch.triu_indices(n, n, offset=1).unbind()]
    return {
        "pairwise_cosine_mean": float(upper.mean().item()),
        "pairwise_cosine_std": float(upper.std(unbiased=False).item()),
    }


def bootstrap_cosine_ci(
    activations: torch.Tensor,
    lu_mean: torch.Tensor,
    n_samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, float | None]:
    n = activations.shape[0]
    if n < 2:
        return {"bootstrap_n": 0, "cosine_ci_low": None, "cosine_ci_high": None}

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    values: list[float] = []
    for _ in range(n_samples):
        idx = torch.from_numpy(rng.integers(0, n, size=n)).long()
        mean = activations[idx].mean(dim=0)
        values.append(cosine(mean, lu_mean))
    arr = np.asarray(values, dtype=np.float64)
    return {
        "bootstrap_n": int(n_samples),
        "cosine_ci_low": float(np.percentile(arr, 2.5)),
        "cosine_ci_high": float(np.percentile(arr, 97.5)),
    }


def running_stop(
    rows: list[dict[str, Any]],
    lu_mean: torch.Tensor,
    lu_dispersion: float,
) -> dict[str, Any]:
    """Deterministic rollout-order stopping based on running cosine SE."""

    if not rows:
        return {
            "passes": False,
            "n_stop": None,
            "se_threshold": lu_dispersion / 2,
            "cosine_to_lu_at_stop": None,
            "reason": "no qualifying rows",
        }

    running: list[torch.Tensor] = []
    cos_values: list[float] = []
    threshold = lu_dispersion / 2
    for row in rows:
        act = load_activation(row)
        running.append(act)
        cos_values.append(cosine(act, lu_mean))
        n = len(running)
        if n < 2:
            continue
        se = float(np.std(cos_values, ddof=1) / math.sqrt(n))
        if n >= 16 and se <= threshold:
            mean = torch.stack(running).mean(dim=0)
            return {
                "passes": True,
                "n_stop": n,
                "se_threshold": threshold,
                "running_cosine_se_at_stop": se,
                "cosine_to_lu_at_stop": cosine(mean, lu_mean),
            }

    return {
        "passes": False,
        "n_stop": None,
        "se_threshold": threshold,
        "running_cosine_se_final": float(np.std(cos_values, ddof=1) / math.sqrt(len(cos_values)))
        if len(cos_values) >= 2
        else None,
        "reason": "criterion not reached",
    }


def summarize_candidate(
    name: str,
    rows: list[dict[str, Any]],
    lu_mean: torch.Tensor,
    save_vector: bool,
) -> dict[str, Any]:
    summary: dict[str, Any] = {"name": name, "n_qualifying": len(rows)}
    if not rows:
        summary.update(
            {
                "vector_path": None,
                "cosine_to_lu_mean": None,
                "pairwise_cosine_mean": None,
                "pairwise_cosine_std": None,
                "bootstrap_n": 0,
                "cosine_ci_low": None,
                "cosine_ci_high": None,
            }
        )
        return summary

    activations = torch.stack([load_activation(row) for row in rows])
    mean = activations.mean(dim=0)
    vector_path = VECTOR_OUT_DIR / f"{name}.pt"
    if save_vector:
        VECTOR_OUT_DIR.mkdir(parents=True, exist_ok=True)
        torch.save(mean, vector_path)
    summary.update(
        {
            "vector_path": str(vector_path.relative_to(REPO_ROOT)) if save_vector else None,
            "cosine_to_lu_mean": cosine(mean, lu_mean),
        }
    )
    summary.update(pairwise_cosine_dispersion(activations))
    summary.update(bootstrap_cosine_ci(activations, lu_mean))
    return summary


def main() -> None:
    if not PHASE1_PATH.exists():
        raise FileNotFoundError(PHASE1_PATH)
    if not PHASE2_PATH.exists():
        raise SystemExit(
            f"Phase 2 scoring not complete; missing {PHASE2_PATH}. "
            "Vector validation script prepared but not run."
        )

    phase1 = load_jsonl(PHASE1_PATH)
    scores = load_jsonl(PHASE2_PATH)
    if len(scores) < EXPECTED_RECORDS:
        raise SystemExit(
            f"Phase 2 scoring not complete; found {len(scores)} scored records, "
            f"expected {EXPECTED_RECORDS}. Vector validation script prepared but not run."
        )

    global np, torch
    import numpy as np
    import torch

    phase1_by_key = {(r["sp_idx"], r["q_idx"]): r for r in phase1}
    score_by_key: dict[tuple[int, int], dict[str, Any]] = {}
    missing_score_fields: list[dict[str, Any]] = []
    for rec in scores:
        key = (rec.get("sp_idx"), rec.get("q_idx"))
        score = score_from_record(rec)
        if score is None:
            missing_score_fields.append({"sp_idx": key[0], "q_idx": key[1], "line_no": rec.get("_line_no")})
        rec["_parsed_score"] = score
        score_by_key[key] = rec

    if missing_score_fields:
        raise ValueError(f"Could not parse score from {len(missing_score_fields)} records: {missing_score_fields[:10]}")

    joined: list[dict[str, Any]] = []
    missing_phase1: list[tuple[int, int]] = []
    for key, score_rec in score_by_key.items():
        p1 = phase1_by_key.get(key)
        if p1 is None:
            missing_phase1.append(key)
            continue
        joined.append({**p1, "score": score_rec["_parsed_score"], "score_record": score_rec})
    if missing_phase1:
        raise ValueError(f"Scores without Phase 1 records: {missing_phase1[:10]}")

    joined.sort(key=lambda r: (r["sp_idx"], r["q_idx"]))

    lu_path = find_lu_trickster_tensor()
    lu_tensor = torch.load(lu_path, map_location="cpu").float()
    if lu_tensor.ndim != 2:
        raise ValueError(f"Lu tensor {lu_path} has shape {tuple(lu_tensor.shape)}, expected 2D")
    if lu_tensor.shape[1] != EXPECTED_HIDDEN_DIM:
        raise ValueError(f"Lu tensor hidden dimension {lu_tensor.shape[1]}, expected {EXPECTED_HIDDEN_DIM}")
    lu_mean = lu_tensor.mean(dim=0)
    lu_row_cos = torch.tensor([cosine(row, lu_mean) for row in lu_tensor])
    lu_dispersion = float(lu_row_cos.std(unbiased=False).item())

    sets = {
        "score_eq_3": [r for r in joined if r["score"] == 3],
        "score_ge_2": [r for r in joined if r["score"] >= 2],
        "nontruncated_score_eq_3": [r for r in joined if r["score"] == 3 and not bool(r.get("truncated"))],
        "nontruncated_score_ge_2": [r for r in joined if r["score"] >= 2 and not bool(r.get("truncated"))],
    }

    candidates = {
        name: summarize_candidate(name, rows, lu_mean, save_vector=True)
        for name, rows in sets.items()
    }
    best_name = max(
        (name for name, item in candidates.items() if item["cosine_to_lu_mean"] is not None),
        key=lambda n: candidates[n]["cosine_to_lu_mean"],
        default=None,
    )

    adaptive = {
        "score_eq_3": running_stop(sets["score_eq_3"], lu_mean, lu_dispersion),
        "score_ge_2": running_stop(sets["score_ge_2"], lu_mean, lu_dispersion),
    }
    for name, stop in adaptive.items():
        if stop.get("passes") and stop.get("n_stop"):
            rows = sets[name]
            stop_vec = torch.stack([load_activation(row) for row in rows[: int(stop["n_stop"])]]
                                   ).mean(dim=0)
            full_vec = torch.stack([load_activation(row) for row in rows]).mean(dim=0)
            stop_path = VECTOR_OUT_DIR / f"{name}_adaptive_stop_n{stop['n_stop']}.pt"
            torch.save(stop_vec, stop_path)
            stop["adaptive_vector_path"] = str(stop_path.relative_to(REPO_ROOT))
            stop["cosine_adaptive_to_full_qualified"] = cosine(stop_vec, full_vec)

    validation = {
        "model_used": MODEL_USED,
        "phase1_path": str(PHASE1_PATH.relative_to(REPO_ROOT)),
        "phase2_path": str(PHASE2_PATH.relative_to(REPO_ROOT)),
        "integrity_paths_checked": [
            str(p.relative_to(REPO_ROOT)) for p in INTEGRITY_PATHS if p.exists()
        ],
        "phase1_records": len(phase1),
        "phase2_scored_records": len(scores),
        "joined_records": len(joined),
        "score_counts": dict(sorted(Counter(r["score"] for r in joined).items())),
        "lu_reference_path": str(lu_path.relative_to(REPO_ROOT)),
        "lu_tensor_shape": list(lu_tensor.shape),
        "lu_hidden_dimension": int(lu_tensor.shape[1]),
        "lu_dispersion": lu_dispersion,
        "candidate_sets": candidates,
        "best_matching_candidate": best_name,
        "adaptive_stopping": adaptive,
        "truncation_counts": {
            "all_records_truncated": sum(1 for r in joined if bool(r.get("truncated"))),
            "score_eq_3_truncated": sum(1 for r in sets["score_eq_3"] if bool(r.get("truncated"))),
            "score_ge_2_truncated": sum(1 for r in sets["score_ge_2"] if bool(r.get("truncated"))),
        },
    }
    (OUTPUT_DIR / "trickster_vector_validation.json").write_text(json.dumps(validation, indent=2) + "\n")

    s3 = candidates["score_eq_3"]
    s2 = candidates["score_ge_2"]
    ns3 = candidates["nontruncated_score_eq_3"]
    ns2 = candidates["nontruncated_score_ge_2"]
    truncation_delta_s3 = (
        None if s3["cosine_to_lu_mean"] is None or ns3["cosine_to_lu_mean"] is None
        else ns3["cosine_to_lu_mean"] - s3["cosine_to_lu_mean"]
    )
    truncation_delta_s2 = (
        None if s2["cosine_to_lu_mean"] is None or ns2["cosine_to_lu_mean"] is None
        else ns2["cosine_to_lu_mean"] - s2["cosine_to_lu_mean"]
    )

    report = f"""# Trickster vector validation against Lu reference

Generated by: {MODEL_USED}

## Inputs

- Phase 1 records: `{PHASE1_PATH.relative_to(REPO_ROOT)}` ({len(phase1)} records)
- Phase 2 scores: `{PHASE2_PATH.relative_to(REPO_ROOT)}` ({len(scores)} records)
- Lu reference tensor: `{lu_path.relative_to(REPO_ROOT)}` shape `{list(lu_tensor.shape)}`

## Core answers

1. Score-3 responses: {s3['n_qualifying']}
2. Score >= 2 responses: {s2['n_qualifying']}
3. Non-truncated score-3 responses: {ns3['n_qualifying']}; non-truncated score >= 2 responses: {ns2['n_qualifying']}
4. Lu dispersion: {lu_dispersion:.6f}
5. Best matching candidate vector: `{best_name}` with cosine {candidates[best_name]['cosine_to_lu_mean']:.6f}
6. Adaptive stopping score==3 passes: {adaptive['score_eq_3'].get('passes')}; score>=2 passes: {adaptive['score_ge_2'].get('passes')}
7. Adaptive stop n score==3: {adaptive['score_eq_3'].get('n_stop')}; score>=2: {adaptive['score_ge_2'].get('n_stop')}
8. Truncation cosine delta score==3: {truncation_delta_s3}; score>=2: {truncation_delta_s2}
9. Replication status: {'validated strongly enough to proceed to Paper 1.5' if best_name and candidates[best_name]['cosine_to_lu_mean'] is not None and (adaptive['score_eq_3'].get('passes') or adaptive['score_ge_2'].get('passes')) else 'requires manual review before Paper 1.5 claims'}
10. Before extracting additional personas: reuse the same Phase 2 completeness gate, record exact score-field schema, preserve activation-shard ignore rules, and compare truncated vs non-truncated candidates before choosing a canonical vector.

## Candidate summary

| candidate | n | cosine_to_lu | pairwise_mean | pairwise_std | 95% bootstrap CI |
|---|---:|---:|---:|---:|---|
"""
    for name, item in candidates.items():
        ci = (
            "n/a"
            if item["cosine_ci_low"] is None
            else f"[{item['cosine_ci_low']:.6f}, {item['cosine_ci_high']:.6f}]"
        )
        report += (
            f"| {name} | {item['n_qualifying']} | {item['cosine_to_lu_mean']} | "
            f"{item['pairwise_cosine_mean']} | {item['pairwise_cosine_std']} | {ci} |\n"
        )

    (OUTPUT_DIR / "trickster_vector_validation.md").write_text(report)
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
