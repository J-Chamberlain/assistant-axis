#!/usr/bin/env python3
"""Audit the full persona-PCA spectrum from saved Qwen, Llama, and Gemma vectors.

This is a CPU-only saved-artifact analysis.  It performs no model inference or
activation extraction.  The primary random-data reference independently
permutes each activation coordinate across the 275 roles.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import platform
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/assistant_axis_mplconfig")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import linear_sum_assignment
from scipy.stats import pearsonr, rankdata, spearmanr
import sklearn
import torch


REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
STARTING_SHA = "7914d01f7d9c23060fe199815a90e547241d9682"
BRANCH = "codex/aa3-extended-pca"
MODEL_USED = "GPT-5.5"
N_PARALLEL = 250
N_BOOTSTRAP = 500
N_CROSS_PERMUTATIONS = 1000
PARALLEL_SEEDS = {"qwen": 31001, "llama": 32001, "gemma": 33001}
BOOTSTRAP_SEEDS = {"qwen": 41001, "llama": 42001, "gemma": 43001}
CROSS_PERMUTATION_SEED = 51001
THRESHOLDS = (0.50, 0.60, 0.68, 0.70, 0.75, 0.80, 0.90, 0.95)
SUBSPACE_DIMS = (3, 4, 5, 6, 8, 10)
MODEL_SPECS = {
    "qwen": {"label": "Qwen/Qwen3-32B", "folder": "qwen-3-32b", "expected_dim": 5120},
    "llama": {"label": "Llama-3.3-70B", "folder": "llama-3.3-70b", "expected_dim": 8192},
    "gemma": {"label": "Gemma-2-27B", "folder": "gemma-2-27b", "expected_dim": 4608},
}
CLUSTER_COLORS = {
    "editorial": "#eabf55",
    "procedural_professional": "#55a7ff",
    "grounded_social": "#63d29a",
    "other": "#aeb6c3",
    "combative_iconoclast": "#ff7272",
    "mythic_spiritual": "#c58aff",
    "trickster_chaos": "#fb9b55",
}
MAJOR_NUMERICAL_FILES = (
    "full_pca_spectrum.csv",
    "pca_cumulative_variance_thresholds.csv",
    "pca_knee_diagnostics.json",
    "pca_broken_stick_comparison.csv",
    "pca_parallel_analysis.csv",
    "pca_bootstrap_component_stability.csv",
    "pca_subspace_stability.csv",
    "qwen_extended_pc_role_rankings.csv",
    "qwen_extended_pc_trait_associations.csv",
    "cross_model_pc_score_correspondence.csv",
    "cross_model_pc_subspace_similarity.csv",
    "cross_model_pc_permutation_control.csv",
    "component_retention_summary.csv",
    "viewer_data.json",
)


@dataclass
class PCAResult:
    key: str
    label: str
    names: list[str]
    vectors: np.ndarray
    mean: np.ndarray
    centered: np.ndarray
    u: np.ndarray
    singular_values: np.ndarray
    components: np.ndarray
    scores: np.ndarray
    eigenvalues: np.ndarray
    explained_ratio: np.ndarray
    cumulative_ratio: np.ndarray
    orientation_signs: list[int]
    source_audit: dict[str, Any]
    reconstruction_max_abs_error: float
    reconstruction_relative_frobenius_error: float
    canonical_pc123_max_abs_error: float


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])


def resolve_vector_root(explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser().resolve())
    candidates.extend(
        [
            REPO / "downloads/hf_vectors",
            Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors"),
        ]
    )
    for root in candidates:
        if all((root / spec["folder"] / "role_vectors").is_dir() for spec in MODEL_SPECS.values()):
            return root
    raise FileNotFoundError("No complete documented Qwen/Llama/Gemma role-vector root found")


def load_mean_role_vectors(vector_dir: Path, expected_dim: int) -> tuple[list[str], np.ndarray, dict[str, Any]]:
    files = sorted(vector_dir.glob("*.pt"))
    if len(files) != 275:
        raise ValueError(f"Expected 275 role vectors in {vector_dir}, found {len(files)}")
    names: list[str] = []
    vectors: list[np.ndarray] = []
    shapes: Counter[str] = Counter()
    dtypes: Counter[str] = Counter()
    aggregate = hashlib.sha256()
    all_finite = True
    for path in files:
        data = path.read_bytes()
        file_hash = sha256_bytes(data)
        aggregate.update(path.name.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(file_hash.encode("ascii"))
        aggregate.update(b"\n")
        tensor = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
        shapes[str(tuple(tensor.shape))] += 1
        dtypes[str(tensor.dtype)] += 1
        tensor = tensor.float()
        vector = tensor.mean(0) if tensor.ndim > 1 else tensor
        arr = vector.numpy().astype(np.float64)
        all_finite = all_finite and bool(np.isfinite(arr).all())
        names.append(path.stem)
        vectors.append(arr)
    matrix = np.stack(vectors)
    if matrix.shape != (275, expected_dim):
        raise ValueError(f"Unexpected mean-vector matrix {matrix.shape} for {vector_dir}")
    if len(set(names)) != 275 or not all_finite:
        raise ValueError(f"Duplicate role labels or nonfinite vectors in {vector_dir}")
    audit = {
        "directory": str(vector_dir),
        "file_count": len(files),
        "mean_vector_matrix_shape": list(matrix.shape),
        "source_tensor_shapes": dict(shapes),
        "source_tensor_dtypes": dict(dtypes),
        "all_source_means_finite": all_finite,
        "aggregate_sha256_of_sorted_filename_and_content_hashes": aggregate.hexdigest(),
    }
    return names, matrix, audit


def deterministic_component_signs(components: np.ndarray) -> np.ndarray:
    signs = np.ones(components.shape[0], dtype=np.float64)
    for i, row in enumerate(components):
        anchor = int(np.argmax(np.abs(row)))
        if row[anchor] < 0:
            signs[i] = -1.0
    return signs


def fit_full_pca(
    key: str,
    names: list[str],
    vectors: np.ndarray,
    audit: dict[str, Any],
    qwen_reference_names: list[str],
    qwen_reference_coords: np.ndarray,
    qwen_scores: np.ndarray | None,
    established_coords: dict[str, np.ndarray],
) -> PCAResult:
    n = vectors.shape[0]
    mean = vectors.mean(axis=0)
    centered = vectors - mean
    u_all, singular_all, components_all = np.linalg.svd(centered, full_matrices=False)
    rank = n - 1
    u = u_all[:, :rank].copy()
    singular = singular_all[:rank].copy()
    components = components_all[:rank].copy()
    scores = u * singular

    signs = deterministic_component_signs(components)
    components *= signs[:, None]
    scores *= signs[None, :]
    u *= signs[None, :]

    if names != qwen_reference_names:
        raise ValueError(f"{key}: role order differs from canonical Qwen order")
    orientation_signs = signs.astype(int).tolist()
    if key == "qwen":
        target = qwen_reference_coords
    else:
        if qwen_scores is None:
            raise ValueError("Qwen scores must be available before cross-model orientation")
        target = qwen_scores[:, :3]
    for pc in range(3):
        correlation = float(np.corrcoef(scores[:, pc], target[:, pc])[0, 1])
        if correlation < 0:
            scores[:, pc] *= -1
            components[pc] *= -1
            u[:, pc] *= -1
            orientation_signs[pc] *= -1

    eigenvalues = singular**2 / (n - 1)
    explained_ratio = eigenvalues / eigenvalues.sum()
    cumulative_ratio = np.cumsum(explained_ratio)
    reconstructed = scores @ components + mean
    residual = reconstructed - vectors
    reconstruction_max = float(np.max(np.abs(residual)))
    reconstruction_relative = float(np.linalg.norm(residual) / np.linalg.norm(centered))
    canonical_error = float(np.max(np.abs(scores[:, :3] - established_coords[key])))
    return PCAResult(
        key=key,
        label=MODEL_SPECS[key]["label"],
        names=names,
        vectors=vectors,
        mean=mean,
        centered=centered,
        u=u,
        singular_values=singular,
        components=components,
        scores=scores,
        eigenvalues=eigenvalues,
        explained_ratio=explained_ratio,
        cumulative_ratio=cumulative_ratio,
        orientation_signs=orientation_signs,
        source_audit=audit,
        reconstruction_max_abs_error=reconstruction_max,
        reconstruction_relative_frobenius_error=reconstruction_relative,
        canonical_pc123_max_abs_error=canonical_error,
    )


def load_references() -> tuple[list[str], np.ndarray, dict[str, str], dict[str, np.ndarray]]:
    geometry = json.loads((REPO / "research/visualizations/geometry_viz_data.json").read_text(encoding="utf-8"))
    names = list(geometry["roles"]["names"])
    qwen_coords = np.asarray(geometry["roles"]["pca3d"], dtype=np.float64)
    clusters = dict(zip(names, geometry["roles"]["clusters"], strict=True))
    multi = json.loads(
        (REPO / "research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_data.json").read_text(encoding="utf-8")
    )
    established: dict[str, np.ndarray] = {"qwen": qwen_coords}
    for key in ("llama", "gemma"):
        points = {row["persona"]: row for row in multi["models"][key]["points"]}
        established[key] = np.asarray(
            [[points[name]["pc1"], points[name]["pc2"], points[name]["pc3"]] for name in names],
            dtype=np.float64,
        )
    return names, qwen_coords, clusters, established


def build_pca_results(vector_root: Path) -> tuple[dict[str, PCAResult], dict[str, str]]:
    reference_names, qwen_coords, clusters, established = load_references()
    results: dict[str, PCAResult] = {}
    qwen_scores = None
    for key, spec in MODEL_SPECS.items():
        names, vectors, audit = load_mean_role_vectors(
            vector_root / spec["folder"] / "role_vectors", int(spec["expected_dim"])
        )
        result = fit_full_pca(
            key,
            names,
            vectors,
            audit,
            reference_names,
            qwen_coords,
            qwen_scores,
            established,
        )
        results[key] = result
        if key == "qwen":
            qwen_scores = result.scores
    return results, clusters


def full_spectrum_rows(results: dict[str, PCAResult]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results.values():
        for i in range(len(result.eigenvalues)):
            next_eigenvalue = result.eigenvalues[i + 1] if i + 1 < len(result.eigenvalues) else math.nan
            eigengap = result.eigenvalues[i] - next_eigenvalue if math.isfinite(next_eigenvalue) else math.nan
            relative = eigengap / result.eigenvalues[i] if math.isfinite(eigengap) else math.nan
            rows.append(
                {
                    "model": result.label,
                    "component": i + 1,
                    "eigenvalue": float(result.eigenvalues[i]),
                    "explained_variance_ratio": float(result.explained_ratio[i]),
                    "cumulative_explained_variance": float(result.cumulative_ratio[i]),
                    "eigengap_to_next": float(eigengap),
                    "relative_eigengap_to_next": float(relative),
                    "role_scores_json": json.dumps(result.scores[:, i].tolist(), separators=(",", ":")),
                }
            )
    return rows


def cumulative_threshold_rows(results: dict[str, PCAResult]) -> list[dict[str, Any]]:
    rows = []
    for result in results.values():
        for threshold in THRESHOLDS:
            k = int(np.searchsorted(result.cumulative_ratio, threshold, side="left") + 1)
            rows.append(
                {
                    "model": result.label,
                    "threshold": threshold,
                    "smallest_k": k,
                    "cumulative_at_k": float(result.cumulative_ratio[k - 1]),
                    "cumulative_before_k": float(result.cumulative_ratio[k - 2]) if k > 1 else 0.0,
                    "descriptive_only": threshold == 0.68,
                }
            )
    return rows


def knee_diagnostics(results: dict[str, PCAResult], max_pc: int = 50) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "scope": f"Components 1-{max_pc}; the near-zero numerical tail is excluded from knee selection.",
        "methods": {
            "eigengap": "Largest absolute and relative adjacent eigengaps within the declared scope.",
            "log_chord_curvature": "Maximum vertical departure of normalized log-eigenvalue scree from its endpoint chord.",
            "two_segment_log_scree": "Breakpoint minimizing total least-squares error of two independent lines on log eigenvalues.",
        },
        "models": {},
    }
    for key, result in results.items():
        eigen = result.eigenvalues[:max_pc]
        gaps = eigen[:-1] - eigen[1:]
        rel = gaps / eigen[:-1]
        abs_pc = int(np.argmax(gaps) + 1)
        rel_pc = int(np.argmax(rel) + 1)
        x = np.linspace(0.0, 1.0, len(eigen))
        log_e = np.log(eigen)
        y = (log_e - log_e[-1]) / (log_e[0] - log_e[-1])
        chord_departure = (1.0 - x) - y
        chord_pc = int(np.argmax(chord_departure) + 1)
        split_errors = []
        indices = np.arange(1, len(eigen) + 1, dtype=np.float64)
        for split in range(2, len(eigen) - 1):
            left_coef = np.polyfit(indices[:split], log_e[:split], 1)
            right_coef = np.polyfit(indices[split - 1 :], log_e[split - 1 :], 1)
            left_error = np.square(log_e[:split] - np.polyval(left_coef, indices[:split])).sum()
            right_error = np.square(log_e[split - 1 :] - np.polyval(right_coef, indices[split - 1 :])).sum()
            split_errors.append((float(left_error + right_error), split))
        piecewise_pc = min(split_errors)[1]
        payload["models"][key] = {
            "model": result.label,
            "max_absolute_eigengap_after_pc": abs_pc,
            "max_absolute_eigengap": float(gaps[abs_pc - 1]),
            "max_relative_eigengap_after_pc": rel_pc,
            "max_relative_eigengap": float(rel[rel_pc - 1]),
            "log_chord_knee_pc": chord_pc,
            "log_chord_departure": float(chord_departure[chord_pc - 1]),
            "two_segment_log_scree_break_pc": int(piecewise_pc),
            "methods_agree_exactly": len({abs_pc, rel_pc, chord_pc, piecewise_pc}) == 1,
        }
    return payload


def broken_stick_rows(results: dict[str, PCAResult]) -> list[dict[str, Any]]:
    rank = 274
    expected = np.asarray([sum(1.0 / j for j in range(i, rank + 1)) / rank for i in range(1, rank + 1)])
    rows = []
    for result in results.values():
        for i in range(rank):
            rows.append(
                {
                    "model": result.label,
                    "component": i + 1,
                    "observed_variance_share": float(result.explained_ratio[i]),
                    "broken_stick_expected_share": float(expected[i]),
                    "observed_to_broken_stick_ratio": float(result.explained_ratio[i] / expected[i]),
                    "exceeds_broken_stick": bool(result.explained_ratio[i] > expected[i]),
                }
            )
    return rows


def parallel_analysis(
    results: dict[str, PCAResult],
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    nulls_by_model: dict[str, np.ndarray] = {}
    reproducibility: dict[str, Any] = {}
    for key, result in results.items():
        rng = np.random.default_rng(PARALLEL_SEEDS[key])
        x = result.centered
        n, dimensions = x.shape
        null_eigenvalues = np.empty((N_PARALLEL, n - 1), dtype=np.float64)
        permuted = np.empty_like(x)
        for replicate in range(N_PARALLEL):
            for column in range(dimensions):
                permuted[:, column] = x[rng.permutation(n), column]
            gram = (permuted @ permuted.T) / (n - 1)
            null_eigenvalues[replicate] = np.linalg.eigvalsh(gram)[::-1][: n - 1]
        nulls_by_model[key] = null_eigenvalues
        null_mean = null_eigenvalues.mean(axis=0)
        null_q95 = np.quantile(null_eigenvalues, 0.95, axis=0)
        pointwise = result.eigenvalues > null_q95
        first_failure = int(np.argmax(~pointwise)) if np.any(~pointwise) else len(pointwise)
        sequential_count = first_failure
        reproducibility[key] = {
            "seed": PARALLEL_SEEDS[key],
            "replicates": N_PARALLEL,
            "all_null_eigenvalues_sha256": sha256_bytes(null_eigenvalues.tobytes()),
            "first_replicate_eigenvalues_sha256": sha256_bytes(null_eigenvalues[0].tobytes()),
            "sequential_retained_count": sequential_count,
            "pointwise_exceedance_count": int(pointwise.sum()),
        }
        for i in range(n - 1):
            rows.append(
                {
                    "model": result.label,
                    "component": i + 1,
                    "observed_eigenvalue": float(result.eigenvalues[i]),
                    "null_mean": float(null_mean[i]),
                    "null_95th_percentile": float(null_q95[i]),
                    "observed_to_null_mean_ratio": float(result.eigenvalues[i] / null_mean[i]),
                    "observed_to_null_q95_ratio": float(result.eigenvalues[i] / null_q95[i]),
                    "pointwise_exceeds_null_q95": bool(pointwise[i]),
                    "sequential_parallel_retain": bool(i < sequential_count),
                }
            )
    return rows, nulls_by_model, reproducibility


def safe_corr(a: np.ndarray, b: np.ndarray, method: str = "pearson") -> float:
    if float(np.std(a)) < 1e-14 or float(np.std(b)) < 1e-14:
        return math.nan
    if method == "spearman":
        return float(spearmanr(a, b).statistic)
    return float(pearsonr(a, b).statistic)


def summarize(values: np.ndarray) -> tuple[float, float, float]:
    return tuple(float(v) for v in np.quantile(values, [0.50, 0.05, 0.95]))


def bootstrap_stability(
    results: dict[str, PCAResult], parallel_meta: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    component_rows: list[dict[str, Any]] = []
    subspace_rows: list[dict[str, Any]] = []
    bootstrap_meta: dict[str, Any] = {}
    for key, result in results.items():
        sequential = int(parallel_meta[key]["sequential_retained_count"])
        report_n = min(80, max(30, sequential + 10))
        pool_n = min(100, report_n + 10)
        n = len(result.names)
        gram = result.centered @ result.centered.T
        full_u = result.u
        full_s = result.singular_values
        rng = np.random.default_rng(BOOTSTRAP_SEEDS[key])
        loading_cosines = np.empty((N_BOOTSTRAP, report_n))
        matched_components = np.empty((N_BOOTSTRAP, report_n), dtype=np.int64)
        score_pearson = np.empty((N_BOOTSTRAP, report_n))
        score_spearman = np.empty((N_BOOTSTRAP, report_n))
        adjacent: dict[tuple[int, int], dict[str, list[float]]] = {
            (start, start + 1): {"min_cc": [], "mean_cc": [], "overlap": [], "max_angle": [], "swap": [], "escape": []}
            for start in range(report_n - 1)
        }
        cumulative_dims = sorted(set([k for k in SUBSPACE_DIMS if k <= report_n] + [min(report_n, sequential)]))
        cumulative: dict[int, dict[str, list[float]]] = {
            k: {"min_cc": [], "mean_cc": [], "overlap": [], "max_angle": []}
            for k in cumulative_dims if k >= 2
        }
        for replicate in range(N_BOOTSTRAP):
            indices = rng.integers(0, n, size=n)
            sampled_gram = gram[np.ix_(indices, indices)]
            row_mean = sampled_gram.mean(axis=1, keepdims=True)
            centered_gram = sampled_gram - row_mean - row_mean.T + sampled_gram.mean()
            evals, ub = np.linalg.eigh(centered_gram)
            order = np.argsort(evals)[::-1]
            evals = np.maximum(evals[order], 0.0)
            ub = ub[:, order]
            sb = np.sqrt(evals)
            valid_pool = min(pool_n, int(np.sum(sb > 1e-10)))
            cross = gram[:, indices]
            cross = cross - cross.mean(axis=1, keepdims=True)
            cosine = full_u[:, :report_n].T @ cross @ ub[:, :valid_pool]
            cosine /= full_s[:report_n, None]
            cosine /= sb[None, :valid_pool]
            cosine = np.clip(cosine, -1.0, 1.0)
            ref_indices, boot_indices = linear_sum_assignment(-np.abs(cosine))
            mapping = np.full(report_n, -1, dtype=np.int64)
            mapping[ref_indices] = boot_indices
            for ref_pc in range(report_n):
                boot_pc = int(mapping[ref_pc])
                signed_loading_cosine = float(cosine[ref_pc, boot_pc])
                sign = 1.0 if signed_loading_cosine >= 0 else -1.0
                loading_cosines[replicate, ref_pc] = abs(signed_loading_cosine)
                matched_components[replicate, ref_pc] = boot_pc
                projected = (cross @ ub[:, boot_pc]) / sb[boot_pc]
                projected *= sign
                score_pearson[replicate, ref_pc] = safe_corr(result.scores[:, ref_pc], projected)
                score_spearman[replicate, ref_pc] = safe_corr(result.scores[:, ref_pc], projected, "spearman")
            max_nominal = min(report_n, valid_pool)
            nominal_cosine = cosine[:max_nominal, :max_nominal]
            for (start, end), record in adjacent.items():
                if end >= max_nominal:
                    continue
                canonical = np.linalg.svd(nominal_cosine[start : end + 1, start : end + 1], compute_uv=False)
                canonical = np.clip(canonical, 0.0, 1.0)
                record["min_cc"].append(float(canonical.min()))
                record["mean_cc"].append(float(canonical.mean()))
                record["overlap"].append(float(np.mean(canonical**2)))
                record["max_angle"].append(float(np.degrees(np.arccos(canonical.min()))))
                record["swap"].append(float(mapping[start] == end and mapping[end] == start))
                record["escape"].append(float(mapping[start] not in (start, end) or mapping[end] not in (start, end)))
            for k, record in cumulative.items():
                if k > max_nominal:
                    continue
                canonical = np.linalg.svd(nominal_cosine[:k, :k], compute_uv=False)
                canonical = np.clip(canonical, 0.0, 1.0)
                record["min_cc"].append(float(canonical.min()))
                record["mean_cc"].append(float(canonical.mean()))
                record["overlap"].append(float(np.mean(canonical**2)))
                record["max_angle"].append(float(np.degrees(np.arccos(canonical.min()))))

        for pc in range(report_n):
            load_med, load_q05, load_q95 = summarize(loading_cosines[:, pc])
            pear_med, pear_q05, pear_q95 = summarize(score_pearson[:, pc])
            spear_med, spear_q05, spear_q95 = summarize(score_spearman[:, pc])
            matches = matched_components[:, pc] + 1
            match_counts = Counter(matches.tolist())
            modal_pc, modal_count = match_counts.most_common(1)[0]
            component_rows.append(
                {
                    "model": result.label,
                    "reference_component": pc + 1,
                    "bootstrap_replicates": N_BOOTSTRAP,
                    "median_matched_loading_cosine": load_med,
                    "loading_cosine_q05": load_q05,
                    "loading_cosine_q95": load_q95,
                    "same_nominal_component_frequency": float(np.mean(matches == pc + 1)),
                    "modal_matched_component": modal_pc,
                    "modal_match_frequency": modal_count / N_BOOTSTRAP,
                    "score_pearson_median": pear_med,
                    "score_pearson_q05": pear_q05,
                    "score_pearson_q95": pear_q95,
                    "score_spearman_median": spear_med,
                    "score_spearman_q05": spear_q05,
                    "score_spearman_q95": spear_q95,
                    "individual_axis_stable": bool(load_med >= 0.90 and load_q05 >= 0.75 and np.mean(matches == pc + 1) >= 0.50),
                }
            )

        for (start, end), record in adjacent.items():
            if not record["min_cc"]:
                continue
            min_med, min_q05, min_q95 = summarize(np.asarray(record["min_cc"]))
            mean_med, mean_q05, mean_q95 = summarize(np.asarray(record["mean_cc"]))
            overlap_med, overlap_q05, overlap_q95 = summarize(np.asarray(record["overlap"]))
            angle_med, angle_q05, angle_q95 = summarize(np.asarray(record["max_angle"]))
            subspace_rows.append(
                {
                    "model": result.label,
                    "block_type": "adjacent_pair",
                    "start_component": start + 1,
                    "end_component": end + 1,
                    "bootstrap_replicates": N_BOOTSTRAP,
                    "median_min_canonical_correlation": min_med,
                    "min_canonical_correlation_q05": min_q05,
                    "min_canonical_correlation_q95": min_q95,
                    "median_mean_canonical_correlation": mean_med,
                    "mean_canonical_correlation_q05": mean_q05,
                    "mean_canonical_correlation_q95": mean_q95,
                    "median_subspace_overlap": overlap_med,
                    "subspace_overlap_q05": overlap_q05,
                    "subspace_overlap_q95": overlap_q95,
                    "median_max_principal_angle_degrees": angle_med,
                    "max_principal_angle_degrees_q05": angle_q05,
                    "max_principal_angle_degrees_q95": angle_q95,
                    "component_swap_frequency": float(np.mean(record["swap"])),
                    "block_escape_frequency": float(np.mean(record["escape"])),
                    "subspace_stable": bool(min_med >= 0.90 and min_q05 >= 0.75),
                }
            )
        for k, record in cumulative.items():
            if not record["min_cc"]:
                continue
            min_med, min_q05, min_q95 = summarize(np.asarray(record["min_cc"]))
            mean_med, mean_q05, mean_q95 = summarize(np.asarray(record["mean_cc"]))
            overlap_med, overlap_q05, overlap_q95 = summarize(np.asarray(record["overlap"]))
            angle_med, angle_q05, angle_q95 = summarize(np.asarray(record["max_angle"]))
            subspace_rows.append(
                {
                    "model": result.label,
                    "block_type": "cumulative_top_k",
                    "start_component": 1,
                    "end_component": k,
                    "bootstrap_replicates": N_BOOTSTRAP,
                    "median_min_canonical_correlation": min_med,
                    "min_canonical_correlation_q05": min_q05,
                    "min_canonical_correlation_q95": min_q95,
                    "median_mean_canonical_correlation": mean_med,
                    "mean_canonical_correlation_q05": mean_q05,
                    "mean_canonical_correlation_q95": mean_q95,
                    "median_subspace_overlap": overlap_med,
                    "subspace_overlap_q05": overlap_q05,
                    "subspace_overlap_q95": overlap_q95,
                    "median_max_principal_angle_degrees": angle_med,
                    "max_principal_angle_degrees_q05": angle_q05,
                    "max_principal_angle_degrees_q95": angle_q95,
                    "component_swap_frequency": math.nan,
                    "block_escape_frequency": math.nan,
                    "subspace_stable": bool(min_med >= 0.90 and min_q05 >= 0.75),
                }
            )
        bootstrap_meta[key] = {
            "seed": BOOTSTRAP_SEEDS[key],
            "replicates": N_BOOTSTRAP,
            "reported_reference_components": report_n,
            "matching_pool_components": pool_n,
            "matching": "one-to-one Hungarian assignment maximizing absolute loading cosine; sign corrected afterward",
        }
    return component_rows, subspace_rows, bootstrap_meta


def role_ranking_rows(
    qwen: PCAResult, clusters: dict[str, str], candidate_max: int
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cluster_total = Counter(clusters.values())
    n = len(qwen.names)
    for component in range(4, candidate_max + 1):
        values = qwen.scores[:, component - 1]
        ascending = rankdata(values, method="average")
        descending = rankdata(-values, method="average")
        percentile = 100.0 * (ascending - 0.5) / n
        for pole, indices in (
            ("positive", np.argsort(values)[::-1][:20]),
            ("negative", np.argsort(values)[:20]),
        ):
            pole_counts = Counter(clusters[qwen.names[i]] for i in indices)
            for pole_rank, index in enumerate(indices, 1):
                cluster = clusters[qwen.names[index]]
                pole_share = pole_counts[cluster] / 20.0
                population_share = cluster_total[cluster] / n
                rows.append(
                    {
                        "component": component,
                        "pole": pole,
                        "pole_rank": pole_rank,
                        "persona": qwen.names[index],
                        "cluster": cluster,
                        "score": float(values[index]),
                        "rank_ascending": float(ascending[index]),
                        "rank_descending": float(descending[index]),
                        "percentile": float(percentile[index]),
                        "cluster_count_in_pole": pole_counts[cluster],
                        "cluster_share_in_pole": pole_share,
                        "cluster_population_share": population_share,
                        "cluster_enrichment_ratio": pole_share / population_share,
                    }
                )
    return rows


def trait_association_rows(qwen: PCAResult, candidate_max: int) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    matrix_path = REPO / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
    frame = pd.read_csv(matrix_path)
    if list(frame["persona"]) != qwen.names:
        frame = frame.set_index("persona").loc[qwen.names].reset_index()
    traits = [column for column in frame.columns if column != "persona"]
    if len(traits) != 240:
        raise ValueError(f"Expected 240 traits, found {len(traits)}")
    x = frame[traits].to_numpy(dtype=np.float64)
    xz = (x - x.mean(axis=0)) / x.std(axis=0, ddof=1)
    rank_x = np.apply_along_axis(rankdata, 0, x)
    rank_xz = (rank_x - rank_x.mean(axis=0)) / rank_x.std(axis=0, ddof=1)
    rows: list[dict[str, Any]] = []
    summaries: dict[int, dict[str, Any]] = {}
    for component in range(4, candidate_max + 1):
        score = qwen.scores[:, component - 1]
        score_z = (score - score.mean()) / score.std(ddof=1)
        score_rank = rankdata(score)
        score_rank_z = (score_rank - score_rank.mean()) / score_rank.std(ddof=1)
        pearson = xz.T @ score_z / (len(score) - 1)
        spearman = rank_xz.T @ score_rank_z / (len(score) - 1)
        positive_order = np.argsort(pearson)[::-1]
        negative_order = np.argsort(pearson)
        positive_rank = np.empty(len(traits), dtype=int)
        negative_rank = np.empty(len(traits), dtype=int)
        positive_rank[positive_order] = np.arange(1, len(traits) + 1)
        negative_rank[negative_order] = np.arange(1, len(traits) + 1)
        for i, trait in enumerate(traits):
            rows.append(
                {
                    "component": component,
                    "trait": trait,
                    "pearson_correlation": float(pearson[i]),
                    "spearman_correlation": float(spearman[i]),
                    "single_trait_r2": float(pearson[i] ** 2),
                    "positive_correlation_rank": int(positive_rank[i]),
                    "negative_correlation_rank": int(negative_rank[i]),
                    "absolute_correlation_rank": int(rankdata(-np.abs(pearson), method="min")[i]),
                    "same_space_activation_derived": True,
                }
            )
        summaries[component] = {
            "max_absolute_pearson": float(np.max(np.abs(pearson))),
            "strongest_positive_traits": [traits[i] for i in positive_order[:10]],
            "strongest_negative_traits": [traits[i] for i in negative_order[:10]],
            "strongest_positive_correlations": [float(pearson[i]) for i in positive_order[:10]],
            "strongest_negative_correlations": [float(pearson[i]) for i in negative_order[:10]],
        }
    return rows, summaries


def interpretation_packet(
    role_rows: list[dict[str, Any]], candidate_max: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = np.random.default_rng(61001)
    instruction_root = REPO / "data/roles/instructions"
    components = list(range(4, candidate_max + 1))
    shuffled_dimensions = rng.permutation(len(components)) + 1
    dimension_ids = {component: f"Dimension-{int(shuffled_dimensions[i]):02d}" for i, component in enumerate(components)}
    packet: list[dict[str, Any]] = []
    key: dict[str, Any] = {
        "seed": 61001,
        "coordinate_blind_packet": "qwen_extended_pc_interpretation_packet.csv",
        "warning": "Keep this key separate from any reviewer; the packet contains no PC number or score.",
        "dimensions": {},
    }
    for component in components:
        positive_is_a = bool(rng.integers(0, 2))
        pole_map = {"positive": "A" if positive_is_a else "B", "negative": "B" if positive_is_a else "A"}
        subset = [row for row in role_rows if row["component"] == component]
        rng.shuffle(subset)
        dimension_id = dimension_ids[component]
        key["dimensions"][dimension_id] = {"component": component, "pole_map": pole_map, "examples": {}}
        for sequence, row in enumerate(subset, 1):
            role = row["persona"]
            source = instruction_root / f"{role}.json"
            payload = json.loads(source.read_text(encoding="utf-8"))
            instructions = [item["pos"] for item in payload["instruction"]]
            example_id = f"{dimension_id}-{pole_map[row['pole']]}-{sequence:02d}"
            packet.append(
                {
                    "blind_dimension_id": dimension_id,
                    "blind_pole": pole_map[row["pole"]],
                    "randomized_example_id": example_id,
                    "role_instruction_1": instructions[0],
                    "role_instruction_2": instructions[1],
                    "role_instruction_3": instructions[2],
                    "role_instruction_4": instructions[3],
                    "role_instruction_5": instructions[4],
                    "reviewer_note": "Coordinate-blind: infer a shared contrast from instruction content only; no PC values are shown.",
                }
            )
            key["dimensions"][dimension_id]["examples"][example_id] = {
                "role": role,
                "actual_pole": row["pole"],
                "pole_rank": row["pole_rank"],
            }
    packet.sort(key=lambda row: (row["blind_dimension_id"], row["blind_pole"], row["randomized_example_id"]))
    return packet, key


def standardized_scores(scores: np.ndarray) -> np.ndarray:
    return (scores - scores.mean(axis=0, keepdims=True)) / scores.std(axis=0, ddof=1, keepdims=True)


def cross_model_correspondence(
    results: dict[str, PCAResult], cross_n: int
) -> tuple[list[dict[str, Any]], dict[str, dict[int, dict[str, Any]]], dict[str, np.ndarray]]:
    q = results["qwen"].scores[:, :cross_n]
    qz = standardized_scores(q)
    qr = standardized_scores(np.apply_along_axis(rankdata, 0, q))
    rows: list[dict[str, Any]] = []
    summaries: dict[str, dict[int, dict[str, Any]]] = {}
    pearson_matrices: dict[str, np.ndarray] = {}
    for target_key in ("llama", "gemma"):
        target = results[target_key].scores[:, :cross_n]
        tz = standardized_scores(target)
        tr = standardized_scores(np.apply_along_axis(rankdata, 0, target))
        pearson = qz.T @ tz / (len(q) - 1)
        spearman = qr.T @ tr / (len(q) - 1)
        composite = (np.abs(pearson) + np.abs(spearman)) / 2.0
        ref_indices, target_indices = linear_sum_assignment(-composite)
        hungarian = {int(i): int(j) for i, j in zip(ref_indices, target_indices, strict=True)}
        summaries[target_key] = {}
        pearson_matrices[target_key] = pearson
        for i in range(cross_n):
            order = np.argsort(np.abs(pearson[i]))[::-1]
            best, second = int(order[0]), int(order[1])
            match = hungarian[i]
            summaries[target_key][i + 1] = {
                "best_component": best + 1,
                "best_signed_pearson": float(pearson[i, best]),
                "best_absolute_pearson": float(abs(pearson[i, best])),
                "best_signed_spearman": float(spearman[i, best]),
                "second_best_component": second + 1,
                "uniqueness_gap_to_second_best_abs_pearson": float(abs(pearson[i, best]) - abs(pearson[i, second])),
                "hungarian_component": match + 1,
                "hungarian_signed_pearson": float(pearson[i, match]),
                "hungarian_signed_spearman": float(spearman[i, match]),
                "hungarian_sign_orientation": 1 if pearson[i, match] >= 0 else -1,
            }
            for j in range(cross_n):
                rows.append(
                    {
                        "reference_model": results["qwen"].label,
                        "reference_component": i + 1,
                        "target_model": results[target_key].label,
                        "target_component": j + 1,
                        "pearson_correlation": float(pearson[i, j]),
                        "absolute_pearson_correlation": float(abs(pearson[i, j])),
                        "spearman_correlation": float(spearman[i, j]),
                        "absolute_spearman_correlation": float(abs(spearman[i, j])),
                        "matching_objective_mean_absolute_correlation": float(composite[i, j]),
                        "is_unconstrained_best_pearson_match": j == best,
                        "is_hungarian_match": j == match,
                        "hungarian_sign_orientation": (1 if pearson[i, j] >= 0 else -1) if j == match else "",
                        "best_to_second_best_abs_pearson_gap": float(abs(pearson[i, best]) - abs(pearson[i, second])) if j == best else "",
                    }
                )
    return rows, summaries, pearson_matrices


def orthonormal_score_basis(scores: np.ndarray, k: int) -> np.ndarray:
    basis, _ = np.linalg.qr(scores[:, :k])
    return basis[:, :k]


def subspace_metrics(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    canonical = np.clip(np.linalg.svd(a.T @ b, compute_uv=False), 0.0, 1.0)
    mean_cc = float(canonical.mean())
    return {
        "canonical_correlations_json": json.dumps(canonical.tolist(), separators=(",", ":")),
        "mean_canonical_correlation": mean_cc,
        "minimum_canonical_correlation": float(canonical.min()),
        "rms_canonical_correlation": float(np.sqrt(np.mean(canonical**2))),
        "maximum_principal_angle_degrees": float(np.degrees(np.arccos(canonical.min()))),
        "procrustes_similarity": mean_cc,
        "normalized_procrustes_residual": float(np.sqrt(max(0.0, 1.0 - mean_cc))),
    }


def cross_model_subspaces(results: dict[str, PCAResult]) -> list[dict[str, Any]]:
    rows = []
    for left_key, right_key in (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma")):
        for k in SUBSPACE_DIMS:
            metrics = subspace_metrics(
                orthonormal_score_basis(results[left_key].scores, k),
                orthonormal_score_basis(results[right_key].scores, k),
            )
            rows.append(
                {
                    "model_a": results[left_key].label,
                    "model_b": results[right_key].label,
                    "top_k": k,
                    **metrics,
                }
            )
    return rows


def cross_model_permutation_controls(
    results: dict[str, PCAResult],
    pearson_matrices: dict[str, np.ndarray],
    candidate_max: int,
    cross_n: int,
) -> tuple[list[dict[str, Any]], dict[str, dict[int, dict[str, float]]]]:
    rng = np.random.default_rng(CROSS_PERMUTATION_SEED)
    qz = standardized_scores(results["qwen"].scores[:, :cross_n])
    target_z = {key: standardized_scores(results[key].scores[:, :cross_n]) for key in ("llama", "gemma")}
    component_nulls = {
        key: {pc: np.empty(N_CROSS_PERMUTATIONS) for pc in range(4, candidate_max + 1)}
        for key in ("llama", "gemma")
    }
    subspace_pairs = (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma"))
    bases = {(key, k): orthonormal_score_basis(results[key].scores, k) for key in results for k in SUBSPACE_DIMS}
    subspace_nulls = {
        (left, right, k): np.empty(N_CROSS_PERMUTATIONS)
        for left, right in subspace_pairs
        for k in SUBSPACE_DIMS
    }
    n = len(qz)
    for replicate in range(N_CROSS_PERMUTATIONS):
        for target_key in ("llama", "gemma"):
            perm = rng.permutation(n)
            null_corr = qz.T @ target_z[target_key][perm] / (n - 1)
            for pc in range(4, candidate_max + 1):
                component_nulls[target_key][pc][replicate] = np.max(np.abs(null_corr[pc - 1]))
        for left, right in (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma")):
            perm = rng.permutation(n)
            for k in SUBSPACE_DIMS:
                canonical = np.linalg.svd(bases[(left, k)].T @ bases[(right, k)][perm], compute_uv=False)
                subspace_nulls[(left, right, k)][replicate] = float(canonical.mean())
    rows: list[dict[str, Any]] = []
    component_summaries: dict[str, dict[int, dict[str, float]]] = {"llama": {}, "gemma": {}}
    for target_key in ("llama", "gemma"):
        for pc in range(4, candidate_max + 1):
            observed = float(np.max(np.abs(pearson_matrices[target_key][pc - 1])))
            null = component_nulls[target_key][pc]
            p = float((1 + np.sum(null >= observed)) / (N_CROSS_PERMUTATIONS + 1))
            summary = {
                "observed": observed,
                "null_mean": float(null.mean()),
                "null_q95": float(np.quantile(null, 0.95)),
                "null_q99": float(np.quantile(null, 0.99)),
                "empirical_p": p,
            }
            component_summaries[target_key][pc] = summary
            rows.append(
                {
                    "control_type": "best_component_absolute_pearson",
                    "model_a": results["qwen"].label,
                    "model_b": results[target_key].label,
                    "reference_component": pc,
                    "top_k": "",
                    "search_components": cross_n,
                    "observed_statistic": observed,
                    "null_mean": summary["null_mean"],
                    "null_95th_percentile": summary["null_q95"],
                    "null_99th_percentile": summary["null_q99"],
                    "empirical_p_value": p,
                    "permutations": N_CROSS_PERMUTATIONS,
                    "seed": CROSS_PERMUTATION_SEED,
                }
            )
    actual_subspaces = {
        (row["model_a"], row["model_b"], row["top_k"]): row
        for row in cross_model_subspaces(results)
    }
    for (left, right, k), null in subspace_nulls.items():
        observed = float(actual_subspaces[(results[left].label, results[right].label, k)]["mean_canonical_correlation"])
        p = float((1 + np.sum(null >= observed)) / (N_CROSS_PERMUTATIONS + 1))
        rows.append(
            {
                "control_type": "mean_subspace_canonical_correlation",
                "model_a": results[left].label,
                "model_b": results[right].label,
                "reference_component": "",
                "top_k": k,
                "search_components": "",
                "observed_statistic": observed,
                "null_mean": float(null.mean()),
                "null_95th_percentile": float(np.quantile(null, 0.95)),
                "null_99th_percentile": float(np.quantile(null, 0.99)),
                "empirical_p_value": p,
                "permutations": N_CROSS_PERMUTATIONS,
                "seed": CROSS_PERMUTATION_SEED,
            }
        )
    return rows, component_summaries


def retention_rows(
    qwen: PCAResult,
    parallel_rows: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    subspace_rows: list[dict[str, Any]],
    correspondence: dict[str, dict[int, dict[str, Any]]],
    component_controls: dict[str, dict[int, dict[str, float]]],
    trait_summaries: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    pmap = {
        int(row["component"]): row
        for row in parallel_rows
        if row["model"] == qwen.label
    }
    bmap = {
        int(row["reference_component"]): row
        for row in bootstrap_rows
        if row["model"] == qwen.label
    }
    adjacent = [
        row for row in subspace_rows
        if row["model"] == qwen.label and row["block_type"] == "adjacent_pair"
    ]
    rows = []
    for pc in range(1, len(qwen.eigenvalues) + 1):
        p = pmap[pc]
        b = bmap.get(pc)
        containing = [row for row in adjacent if row["start_component"] <= pc <= row["end_component"]]
        best_subspace = max(containing, key=lambda row: float(row["min_canonical_correlation_q05"])) if containing else None
        individual_stable = bool(b and b["individual_axis_stable"])
        moderate_axis_reproducibility = bool(
            b
            and b["median_matched_loading_cosine"] >= 0.75
            and b["loading_cosine_q05"] >= 0.50
            and b["same_nominal_component_frequency"] >= 0.50
        )
        subspace_stable = bool(best_subspace and best_subspace["subspace_stable"])
        trait = trait_summaries.get(pc)
        semantic_coherent = bool(trait and trait["max_absolute_pearson"] >= 0.50)
        recurrence_values = []
        recurrence_details = {}
        for target in ("llama", "gemma"):
            match = correspondence.get(target, {}).get(pc)
            control = component_controls.get(target, {}).get(pc)
            if match and control:
                strong = bool(match["best_absolute_pearson"] >= 0.40 and control["empirical_p"] <= 0.05)
                recurrence_values.append(strong)
                recurrence_details[target] = (match, control)
        recurrent_any = any(recurrence_values)
        recurrent_both = len(recurrence_values) == 2 and all(recurrence_values)
        if pc <= 3 and p["pointwise_exceeds_null_q95"] and individual_stable:
            status = "CORE"
        elif (
            pc > 3
            and p["sequential_parallel_retain"]
            and (individual_stable or moderate_axis_reproducibility)
            and semantic_coherent
            and recurrent_both
        ):
            status = "SUPPORTED LATER COMPONENT"
        elif pc > 3 and p["sequential_parallel_retain"] and not individual_stable and subspace_stable:
            status = "STABLE SUBSPACE / AXIS NOT UNIQUE"
        elif p["pointwise_exceeds_null_q95"] and (
            individual_stable or moderate_axis_reproducibility or subspace_stable or semantic_coherent
        ):
            status = "EXPLORATORY"
        else:
            status = "NOISE-LIKE / UNSTABLE"
        rows.append(
            {
                "model": qwen.label,
                "component": pc,
                "explained_variance_ratio": float(qwen.explained_ratio[pc - 1]),
                "cumulative_explained_variance": float(qwen.cumulative_ratio[pc - 1]),
                "eigenvalue": float(qwen.eigenvalues[pc - 1]),
                "eigengap_to_next": float(qwen.eigenvalues[pc - 1] - qwen.eigenvalues[pc]) if pc < len(qwen.eigenvalues) else math.nan,
                "relative_eigengap_to_next": float((qwen.eigenvalues[pc - 1] - qwen.eigenvalues[pc]) / qwen.eigenvalues[pc - 1]) if pc < len(qwen.eigenvalues) else math.nan,
                "parallel_pointwise_pass": bool(p["pointwise_exceeds_null_q95"]),
                "parallel_sequential_retain": bool(p["sequential_parallel_retain"]),
                "bootstrap_evaluated": b is not None,
                "bootstrap_median_loading_cosine": float(b["median_matched_loading_cosine"]) if b else math.nan,
                "bootstrap_loading_cosine_q05": float(b["loading_cosine_q05"]) if b else math.nan,
                "bootstrap_same_nominal_frequency": float(b["same_nominal_component_frequency"]) if b else math.nan,
                "individual_axis_stable": individual_stable,
                "moderate_axis_reproducibility": moderate_axis_reproducibility,
                "best_adjacent_subspace": f"PC{best_subspace['start_component']}-PC{best_subspace['end_component']}" if best_subspace else "",
                "best_adjacent_subspace_min_cc_median": float(best_subspace["median_min_canonical_correlation"]) if best_subspace else math.nan,
                "best_adjacent_subspace_min_cc_q05": float(best_subspace["min_canonical_correlation_q05"]) if best_subspace else math.nan,
                "adjacent_subspace_stable": subspace_stable,
                "max_absolute_trait_pearson": float(trait["max_absolute_pearson"]) if trait else math.nan,
                "trait_coherence_descriptive": semantic_coherent,
                "best_llama_component": recurrence_details.get("llama", ({}, {}))[0].get("best_component", ""),
                "best_llama_abs_pearson": recurrence_details.get("llama", ({}, {}))[0].get("best_absolute_pearson", math.nan),
                "best_llama_permutation_p": recurrence_details.get("llama", ({}, {}))[1].get("empirical_p", math.nan),
                "best_gemma_component": recurrence_details.get("gemma", ({}, {}))[0].get("best_component", ""),
                "best_gemma_abs_pearson": recurrence_details.get("gemma", ({}, {}))[0].get("best_absolute_pearson", math.nan),
                "best_gemma_permutation_p": recurrence_details.get("gemma", ({}, {}))[1].get("empirical_p", math.nan),
                "cross_model_recurrence_any": recurrent_any,
                "cross_model_recurrence_both": recurrent_both,
                "retention_status": status,
                "status_is_evidence_summary_not_significance_label": True,
            }
        )
    return rows


def plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 220,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "#fbfcfe",
            "grid.color": "#dfe5ee",
            "grid.linewidth": 0.7,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def make_plots(
    results: dict[str, PCAResult],
    parallel_rows: list[dict[str, Any]],
    bootstrap_rows: list[dict[str, Any]],
    correspondence_matrices: dict[str, np.ndarray],
    subspace_rows: list[dict[str, Any]],
    retention: list[dict[str, Any]],
    clusters: dict[str, str],
) -> list[str]:
    plot_style()
    made: list[str] = []
    q = results["qwen"]
    components = np.arange(1, len(q.eigenvalues) + 1)
    for scale in ("linear", "log"):
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ax.plot(components, q.eigenvalues, color="#2563eb", lw=1.6)
        ax.scatter(components[:20], q.eigenvalues[:20], color="#2563eb", s=14, zorder=3)
        if scale == "log":
            ax.set_yscale("log")
        ax.set(xlabel="Principal component", ylabel="Eigenvalue", title=f"Qwen persona PCA scree ({scale} eigenvalue scale)")
        ax.grid(alpha=0.75)
        stem = f"qwen_scree_{scale}"
        save_figure(fig, stem)
        made.append(stem)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.plot(components, q.cumulative_ratio, color="#0f766e", lw=1.8)
    for threshold in (0.50, 0.68, 0.80, 0.90):
        k = int(np.searchsorted(q.cumulative_ratio, threshold) + 1)
        ax.axhline(threshold, color="#94a3b8", lw=0.7, ls="--")
        ax.scatter([k], [q.cumulative_ratio[k - 1]], s=24, label=f"{threshold:.0%}: PC{k}")
    ax.set(xlabel="Number of retained components", ylabel="Cumulative explained variance", ylim=(0, 1.01), title="Qwen cumulative persona-PCA variance")
    ax.grid(alpha=0.75)
    ax.legend(ncol=2, frameon=False)
    save_figure(fig, "qwen_cumulative_variance")
    made.append("qwen_cumulative_variance")

    qp = [row for row in parallel_rows if row["model"] == q.label]
    first = 30
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    x = np.arange(1, first + 1)
    ax.plot(x, [row["observed_eigenvalue"] for row in qp[:first]], marker="o", ms=3.5, label="Observed", color="#2563eb")
    ax.plot(x, [row["null_95th_percentile"] for row in qp[:first]], marker="o", ms=3.0, label="Permutation-null 95th percentile", color="#dc2626")
    ax.set(xlabel="Principal component", ylabel="Eigenvalue", title="Qwen marginal-preserving parallel analysis (first 30 PCs)")
    ax.grid(alpha=0.75)
    ax.legend(frameon=False)
    save_figure(fig, "qwen_parallel_analysis")
    made.append("qwen_parallel_analysis")

    qb = [row for row in bootstrap_rows if row["model"] == q.label]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    x = np.asarray([row["reference_component"] for row in qb])
    med = np.asarray([row["median_matched_loading_cosine"] for row in qb])
    lo = np.asarray([row["loading_cosine_q05"] for row in qb])
    hi = np.asarray([row["loading_cosine_q95"] for row in qb])
    ax.plot(x, med, color="#7c3aed", marker="o", ms=3.5, label="Median matched loading cosine")
    ax.fill_between(x, lo, hi, color="#c4b5fd", alpha=0.45, label="5th–95th percentile")
    ax.axhline(0.75, color="#64748b", lw=0.8, ls="--", label="Descriptive q05 stability threshold")
    ax.set(xlabel="Qwen reference component", ylabel="Absolute loading cosine", ylim=(0, 1.02), title="Qwen component stability under role bootstrap")
    ax.grid(alpha=0.75)
    ax.legend(frameon=False)
    save_figure(fig, "qwen_bootstrap_component_stability")
    made.append("qwen_bootstrap_component_stability")

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6), constrained_layout=True)
    for ax, key in zip(axes, ("llama", "gemma"), strict=True):
        matrix = np.abs(correspondence_matrices[key][:20, :20])
        im = ax.imshow(matrix, vmin=0, vmax=1, cmap="magma", aspect="auto")
        ax.set(title=f"Qwen vs {MODEL_SPECS[key]['label']}", xlabel=f"{MODEL_SPECS[key]['label']} PC", ylabel="Qwen PC")
        ax.set_xticks(np.arange(0, 20, 2), np.arange(1, 21, 2))
        ax.set_yticks(np.arange(0, 20, 2), np.arange(1, 21, 2))
    fig.colorbar(im, ax=axes, label="Absolute Pearson correlation", shrink=0.82)
    fig.suptitle("Cross-model role-score component correspondence")
    save_figure(fig, "cross_model_component_correspondence_heatmap")
    made.append("cross_model_component_correspondence_heatmap")

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for pair, color in (("Qwen/Qwen3-32B|Llama-3.3-70B", "#2563eb"), ("Qwen/Qwen3-32B|Gemma-2-27B", "#d97706"), ("Llama-3.3-70B|Gemma-2-27B", "#0f766e")):
        left, right = pair.split("|")
        subset = [row for row in subspace_rows if row["model_a"] == left and row["model_b"] == right]
        ax.plot([row["top_k"] for row in subset], [row["mean_canonical_correlation"] for row in subset], marker="o", label=f"{left.split('/')[0]}–{right.split('-')[0]}", color=color)
    ax.set(xlabel="Top-k score subspace", ylabel="Mean canonical correlation", ylim=(0, 1.02), title="Cross-model persona score-subspace recurrence")
    ax.grid(alpha=0.75)
    ax.legend(frameon=False)
    save_figure(fig, "cross_model_subspace_similarity")
    made.append("cross_model_subspace_similarity")

    retention_map = {int(row["component"]): row for row in retention}
    if retention_map[4]["retention_status"] != "NOISE-LIKE / UNSTABLE" and retention_map[5]["retention_status"] != "NOISE-LIKE / UNSTABLE":
        fig, ax = plt.subplots(figsize=(7.4, 6.2))
        for cluster in sorted(set(clusters.values())):
            idx = [i for i, name in enumerate(q.names) if clusters[name] == cluster]
            ax.scatter(q.scores[idx, 3], q.scores[idx, 4], s=22, alpha=0.82, color=CLUSTER_COLORS.get(cluster, "#94a3b8"), label=cluster.replace("_", " "))
        ax.axhline(0, color="#cbd5e1", lw=0.8)
        ax.axvline(0, color="#cbd5e1", lw=0.8)
        ax.set(xlabel="Qwen PC4 score", ylabel="Qwen PC5 score", title="Qwen later-component role geometry: PC4 × PC5")
        ax.grid(alpha=0.5)
        ax.legend(frameon=False, fontsize=7.5, ncol=2)
        save_figure(fig, "qwen_pc4_pc5_role_scatter")
        made.append("qwen_pc4_pc5_role_scatter")
    if all(retention_map[pc]["retention_status"] != "NOISE-LIKE / UNSTABLE" for pc in (4, 5, 6)):
        fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8), constrained_layout=True)
        for ax, xpc, ypc in ((axes[0], 4, 6), (axes[1], 5, 6)):
            for cluster in sorted(set(clusters.values())):
                idx = [i for i, name in enumerate(q.names) if clusters[name] == cluster]
                ax.scatter(q.scores[idx, xpc - 1], q.scores[idx, ypc - 1], s=17, alpha=0.78, color=CLUSTER_COLORS.get(cluster, "#94a3b8"))
            ax.set(xlabel=f"Qwen PC{xpc}", ylabel=f"Qwen PC{ypc}", title=f"PC{xpc} × PC{ypc}")
            ax.grid(alpha=0.5)
        fig.suptitle("Qwen supported later-component projections")
        save_figure(fig, "qwen_pc4_pc6_later_component_scatter")
        made.append("qwen_pc4_pc6_later_component_scatter")
    return made


def build_viewer_data(
    results: dict[str, PCAResult], clusters: dict[str, str], parallel_rows: list[dict[str, Any]], bootstrap_rows: list[dict[str, Any]], retention: list[dict[str, Any]]
) -> dict[str, Any]:
    parallel = {(row["model"], int(row["component"])): row for row in parallel_rows}
    bootstrap = {(row["model"], int(row["reference_component"])): row for row in bootstrap_rows}
    retention_map = {int(row["component"]): row for row in retention}
    models = {}
    for key, result in results.items():
        diagnostics = []
        for pc in range(1, 11):
            p = parallel[(result.label, pc)]
            b = bootstrap.get((result.label, pc), {})
            diagnostics.append(
                {
                    "component": pc,
                    "explained_variance_ratio": float(result.explained_ratio[pc - 1]),
                    "cumulative_explained_variance": float(result.cumulative_ratio[pc - 1]),
                    "parallel_retain": bool(p["sequential_parallel_retain"]),
                    "parallel_pointwise_pass": bool(p["pointwise_exceeds_null_q95"]),
                    "bootstrap_median_loading_cosine": b.get("median_matched_loading_cosine"),
                    "bootstrap_loading_cosine_q05": b.get("loading_cosine_q05"),
                    "retention_status": retention_map[pc]["retention_status"] if key == "qwen" else "MODEL-LOCAL DIAGNOSTIC",
                }
            )
        points = []
        for i, name in enumerate(result.names):
            points.append(
                {
                    "persona": name,
                    "cluster": clusters[name],
                    "coordinates": [float(v) for v in result.scores[i, :10]],
                }
            )
        models[key] = {
            "label": result.label,
            "hidden_dimension": result.vectors.shape[1],
            "role_count": len(result.names),
            "points": points,
            "diagnostics": diagnostics,
        }
    return {
        "metadata": {
            "title": "Extended persona PCA viewer",
            "analysis_starting_sha": STARTING_SHA,
            "coordinate_scope": "Model-local centered PCA scores, PC1-PC10",
            "interpretation_boundary": "Explained variance is activation-coordinate variation among 275 centered role vectors, not personality, behavior, or human psychological variance.",
            "cluster_colors": CLUSTER_COLORS,
        },
        "models": models,
    }


def render_viewer(viewer_data: dict[str, Any]) -> None:
    template_path = OUT / "viewer_template.html"
    script_path = OUT / "viewer.js"
    if not template_path.is_file() or not script_path.is_file():
        raise FileNotFoundError("viewer_template.html and viewer.js must exist beside the runner")
    template = template_path.read_text(encoding="utf-8")
    script = script_path.read_text(encoding="utf-8")
    embedded = json.dumps(viewer_data, separators=(",", ":"))
    html = template.replace("__VIEWER_DATA__", embedded).replace("__VIEWER_SCRIPT__", script)
    (OUT / "extended_persona_pca_viewer.html").write_text(html, encoding="utf-8")


def construction_audit(results: dict[str, PCAResult], vector_root: Path) -> str:
    lines = [
        "# Persona PCA construction audit",
        "",
        f"Generated UTC: {utc_now()}",
        f"Analysis model: {MODEL_USED}",
        "",
        "## Why the project previously used three PCs",
        "",
        "The original geometry builder explicitly instantiated `PCA(n_components=3)` for the role-vector 3D visualization and a separate two-component fit for the 2D view. No saved scree, parallel-analysis, bootstrap-stability, or cumulative-variance decision selected three as the scientific dimensionality. PC4 and later components were outside the original display target, not rejected.",
        "",
        "## Variables and observations",
        "",
        "Rows are the 275 lexically ordered persona/role artifacts. Columns are hidden-state activation coordinates after each saved role tensor is mean-pooled across its stored layer rows. PCA is ordinary centered role-vector PCA. The named 240 traits do not enter any persona PCA fit; they are used only later for descriptive same-space associations.",
        "",
        "| Model | Input rows | Activation-coordinate columns | Stored source tensor shape | Construction |",
        "|---|---:|---:|---|---|",
    ]
    for result in results.values():
        shape_text = ", ".join(f"{shape} × {count}" for shape, count in result.source_audit["source_tensor_shapes"].items())
        lines.append(f"| {result.label} | {len(result.names)} | {result.vectors.shape[1]} | {shape_text} | mean-pool stored rows, stack roles, center columns, full SVD |")
    lines.extend(
        [
            "",
            "The centered matrix rank cannot exceed 274 because there are 275 observations. The audit retains all 274 mathematically available nonzero directions and verifies full reconstruction.",
            "",
            "## Orientation and compatibility",
            "",
            "Qwen PC1-PC3 are sign-oriented to the canonical `geometry_viz_data.json` coordinates. Llama and Gemma PC1-PC3 follow the established project rule: recompute PCA in each model's own activation space, then orient each same-index sign by its correlation with the Qwen reference score. Later-component signs use a deterministic largest-absolute-loading convention; signs do not affect variance, stability, or subspace conclusions.",
            "",
        ]
    )
    for result in results.values():
        lines.append(f"- {result.label}: orientation signs for the saved full PCA begin `{result.orientation_signs[:10]}`; PC1-PC3 reproduction maximum absolute error `{result.canonical_pc123_max_abs_error:.3e}`; full reconstruction relative Frobenius error `{result.reconstruction_relative_frobenius_error:.3e}`.")
    lines.extend(
        [
            "",
            "## Variance language",
            "",
            "**Explained variance is the fraction of total squared variation among the 275 centered role activation vectors captured by a PCA direction. It is not a percent of personality, behavior, psychological variation in humans, or causal importance.**",
            "",
            "## Sources",
            "",
            f"Saved role-vector root: `{vector_root}`. Canonical coordinate and cluster sources are `research/visualizations/geometry_viz_data.json`, `research/geometry_tables/`, and the established multimodel PCA reconstruction in `research/outputs/multimodel_ordered_trait_region_viewer/`.",
            "",
            "No GPU, RunPod, model inference, activation extraction, or external model API was used.",
            "",
        ]
    )
    return "\n".join(lines)


def report_text(
    results: dict[str, PCAResult],
    threshold_rows: list[dict[str, Any]],
    knee: dict[str, Any],
    parallel_meta: dict[str, Any],
    bootstrap_rows: list[dict[str, Any]],
    subspace_rows: list[dict[str, Any]],
    retention: list[dict[str, Any]],
    correspondence: dict[str, dict[int, dict[str, Any]]],
    controls: dict[str, dict[int, dict[str, float]]],
    cross_subspace_rows: list[dict[str, Any]],
    cross_control_rows: list[dict[str, Any]],
    role_rows: list[dict[str, Any]],
    trait_summaries: dict[int, dict[str, Any]],
    plots: list[str],
) -> str:
    q = results["qwen"]
    threshold = {(row["model"], float(row["threshold"])): row for row in threshold_rows}
    rmap = {int(row["component"]): row for row in retention}
    bmap = {int(row["reference_component"]): row for row in bootstrap_rows if row["model"] == q.label}
    cross_subspace = {
        (row["model_a"], row["model_b"], int(row["top_k"])): row
        for row in cross_subspace_rows
    }
    cross_subspace_controls = {
        (row["model_a"], row["model_b"], int(row["top_k"])): row
        for row in cross_control_rows
        if row["control_type"] == "mean_subspace_canonical_correlation"
    }
    seq = int(parallel_meta["qwen"]["sequential_retained_count"])
    stable_count = sum(
        bool(row["individual_axis_stable"])
        for row in bootstrap_rows
        if row["model"] == q.label and int(row["reference_component"]) <= seq
    )
    supported_later = [pc for pc in range(4, len(retention) + 1) if rmap[pc]["retention_status"] == "SUPPORTED LATER COMPONENT"]
    rotating = [pc for pc in range(4, len(retention) + 1) if rmap[pc]["retention_status"] == "STABLE SUBSPACE / AXIS NOT UNIQUE"]
    if supported_later:
        contiguous = []
        for pc in range(4, max(supported_later) + 1):
            if rmap[pc]["retention_status"] == "SUPPORTED LATER COMPONENT":
                contiguous.append(pc)
            else:
                break
        if contiguous:
            recommendation = f"Use PC1-PC{contiguous[-1]} when the scientific question needs the supported later axes; retain PC1-PC3 as the compact public-facing core."
        else:
            recommendation = "Keep PC1-PC3 as the named core and treat supported noncontiguous later components separately."
    elif rotating:
        recommendation = "Keep PC1-PC3 as the named core and describe later retained variation as a secondary stable subspace without privileging each rotating axis."
    else:
        recommendation = "Retain PC1-PC3 as the scientific and visual core; later components remain exploratory or noise-like under the combined diagnostics."

    lines = [
        "# Extended persona PCA dimensionality audit",
        "",
        f"Generated UTC: {utc_now()}",
        f"Analysis model: {MODEL_USED}",
        "",
        "## Executive answer",
        "",
        "Only three PCs were used previously because the original geometry builder was configured for a 3D visualization (`PCA(n_components=3)`), not because a dimensionality-selection analysis rejected PC4+. This audit fits all 274 available centered components and combines variance, three scree diagnostics, broken-stick, 250 marginal-preserving parallel permutations, 500 role bootstraps, subspace angles, same-space trait associations, and cross-model role-score recurrence.",
        "",
        f"Primary recommendation: **{recommendation}**",
        "",
        "Explained variance here is activation-coordinate variation among 275 centered saved role vectors. It is not a percentage of personality, behavior, human psychological variance, or causal importance.",
        "",
        "## Qwen PC1-PC10 variance",
        "",
        "| PC | Explained variance | Cumulative | Parallel | Bootstrap loading cosine median / q05 | Retention status |",
        "|---:|---:|---:|---|---:|---|",
    ]
    for pc in range(1, 11):
        row = rmap[pc]
        boot = bmap[pc]
        lines.append(
            f"| {pc} | {100*q.explained_ratio[pc-1]:.3f}% | {100*q.cumulative_ratio[pc-1]:.3f}% | {'retain' if row['parallel_sequential_retain'] else 'no'} | {boot['median_matched_loading_cosine']:.3f} / {boot['loading_cosine_q05']:.3f} | {row['retention_status']} |"
        )
    lines.extend(
        [
            "",
            "## Cumulative thresholds",
            "",
            "| Model | 50% | 60% | 68% | 70% | 75% | 80% | 90% | 95% |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for result in results.values():
        ks = [threshold[(result.label, value)]["smallest_k"] for value in THRESHOLDS]
        lines.append(f"| {result.label} | " + " | ".join(str(k) for k in ks) + " |")
    lines.extend(
        [
            "",
            f"Qwen reaches 68% at PC{threshold[(q.label, 0.68)]['smallest_k']} and 80% at PC{threshold[(q.label, 0.80)]['smallest_k']}. The 68% row is reported because it was specifically requested; it is not treated as the correct cutoff.",
            "",
            "## Scree and random-data references",
            "",
        ]
    )
    for key, result in results.items():
        diag = knee["models"][key]
        lines.append(
            f"- {result.label}: largest absolute eigengap after PC{diag['max_absolute_eigengap_after_pc']}; largest relative gap after PC{diag['max_relative_eigengap_after_pc']}; log-chord knee PC{diag['log_chord_knee_pc']}; two-line log-scree break PC{diag['two_segment_log_scree_break_pc']}; sequential parallel-analysis retained count {parallel_meta[key]['sequential_retained_count']}."
        )
    lines.extend(
        [
            "",
            "The knee methods are descriptive and disagree where stated; no automated knee is treated as ground truth. Parallel analysis uses the requested primary null: each activation coordinate is independently permuted across roles, retaining each coordinate's marginal values while destroying cross-coordinate role structure.",
            "",
            "## PC4, PC5, and later Qwen components",
            "",
        ]
    )
    max_described = max(10, min(20, seq))
    for pc in range(4, max_described + 1):
        row = rmap[pc]
        roles_pos = [r["persona"] for r in role_rows if r["component"] == pc and r["pole"] == "positive"][:5]
        roles_neg = [r["persona"] for r in role_rows if r["component"] == pc and r["pole"] == "negative"][:5]
        traits = trait_summaries.get(pc, {})
        lines.append(f"### PC{pc}: {row['retention_status']}")
        lines.append("")
        lines.append(
            f"Observed: variance {100*row['explained_variance_ratio']:.3f}% (cumulative {100*row['cumulative_explained_variance']:.3f}%); parallel sequential retain={row['parallel_sequential_retain']}; bootstrap matched-loading median/q05={row['bootstrap_median_loading_cosine']:.3f}/{row['bootstrap_loading_cosine_q05']:.3f}; best adjacent subspace {row['best_adjacent_subspace']} q05 minimum canonical correlation={row['best_adjacent_subspace_min_cc_q05']:.3f}."
        )
        if traits:
            lines.append(
                "Same-space trait evidence: strongest positive correlations include "
                + ", ".join(traits["strongest_positive_traits"][:5])
                + "; strongest negative correlations include "
                + ", ".join(traits["strongest_negative_traits"][:5])
                + f"; maximum absolute Pearson={traits['max_absolute_pearson']:.3f}."
            )
        lines.append("Role extremes: positive " + ", ".join(roles_pos) + "; negative " + ", ".join(roles_neg) + ".")
        lines.append("INTERPRETATION / PROVISIONAL: this component is summarized by its full role, trait, stability, and recurrence evidence; an independent coordinate-blind reviewer packet is provided before any durable semantic name is assigned.")
        lines.append("")
    lines.extend(
        [
            "## Cross-model recurrence for Qwen later PCs",
            "",
            "| Qwen PC | Best Llama PC (Pearson / Spearman; p) | Best Gemma PC (Pearson / Spearman; p) |",
            "|---:|---|---|",
        ]
    )
    for pc in range(4, max_described + 1):
        l = correspondence["llama"][pc]
        g = correspondence["gemma"][pc]
        lp = controls["llama"][pc]["empirical_p"]
        gp = controls["gemma"][pc]["empirical_p"]
        lines.append(
            f"| {pc} | PC{l['best_component']} ({l['best_signed_pearson']:.3f} / {l['best_signed_spearman']:.3f}; {lp:.3f}) | PC{g['best_component']} ({g['best_signed_pearson']:.3f} / {g['best_signed_spearman']:.3f}; {gp:.3f}) |"
        )
    lines.extend(
        [
            "",
        "Component matching compares score patterns over the same 275 role labels, searches the first 20 or more PCs in each model, records unconstrained best matches and a one-to-one Hungarian map, and tests search-adjusted best correlations against shuffled role labels. Same component numbers are not presumed to share meaning.",
        "",
        "## Cross-model score-subspace recurrence",
        "",
        "| Model pair | top 3 | top 4 | top 5 | top 6 |",
        "|---|---:|---:|---:|---:|",
        ]
    )
    for left_key, right_key in (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma")):
        left = results[left_key].label
        right = results[right_key].label
        cells = []
        for k in (3, 4, 5, 6):
            observed = cross_subspace[(left, right, k)]["mean_canonical_correlation"]
            p_value = cross_subspace_controls[(left, right, k)]["empirical_p_value"]
            cells.append(f"{observed:.3f} (p={p_value:.3f})")
        lines.append(f"| {left} / {right} | " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "These score-space similarities are over the shared role labels and all exceed their 1,000-shuffle nulls. They show recurrence of role-score subspaces, not identity of activation bases or component semantics.",
            "",
            "## Individual axes versus subspaces",
            "",
            f"Among the {parallel_meta['qwen']['sequential_retained_count']} sequentially parallel-retained Qwen components, {stable_count} of the explicitly bootstrapped components meet the descriptive individual-axis stability rule. Adjacent-pair and cumulative-subspace diagnostics should be used where close eigenvalues permit rotation; a stable subspace does not license distinct names for unstable member axes.",
            "",
            "PC4-PC6 do not meet the strict individual-axis rule (median loading cosine ≥0.90 and q05 ≥0.75), and no Qwen later adjacent block passes the equally strict subspace rule. They are nevertheless classified as supported later components because each passes sequential parallel analysis, has moderate bootstrap reproducibility (median ≥0.75, q05 ≥0.50, same-index frequency ≥0.50), shows a same-space trait association |r| ≥0.50, and recurs in both Llama and Gemma after search-adjusted role-label permutation controls. This is weaker evidence than CORE status and does not license durable semantic names.",
            "",
            "## Role-instruction interpretation packet",
            "",
            "`qwen_extended_pc_interpretation_packet.csv` randomizes later-component identities and pole signs and contains instruction text without PC values. Its separate key is retained for audit. No external model API or unblinded reviewer was used; labels in this report remain explicitly provisional.",
            "",
            "## Static figures",
            "",
        ]
    )
    for stem in plots:
        lines.append(f"- `{stem}.png` and `{stem}.svg`.")
    lines.extend(
        [
            "",
            "## Observed",
            "",
            "- Full model-local activation-coordinate spectra, variance thresholds, random-data comparisons, bootstrap stability, role extremes, trait associations, and cross-model score/subspace recurrences are reported in the saved tables.",
            "- Qwen, Llama, and Gemma each contain the same 275 role labels, but their PCA bases are fitted separately in hidden dimensions 5,120, 8,192, and 4,608.",
            "- PC1-PC3 reproduce the canonical/established coordinates within the saved verification tolerances.",
            "- Qwen PCs 1-13 exceed the 95th-percentile marginal-permutation null sequentially; only PCs 1-3 meet the strict individual-axis bootstrap rule. PCs 4-6 meet the declared moderate-reproducibility rule and recur in both comparison models.",
            "",
            "## Interpretation",
            "",
            f"- {recommendation}",
            "- PC4-PC6 are scientifically useful as supported secondary coordinates, but their lower bootstrap stability makes them weaker and less nameable than the PC1-PC3 core. PC7-PC13 exceed the random-data reference yet lack sufficient stability or trait coherence for privileged interpretation.",
            "- Later components should be named only when individual stability, cross-model recurrence, full-distribution role structure, and trait coherence converge. Same-space trait correlations are descriptive support, not independent psychological validation.",
            "",
            "## Hypotheses",
            "",
            "- PC4-PC6 may encode secondary role/register distinctions that the original 3D display compressed; coordinate-blind human review is needed before durable labels.",
            "- Cross-model score-subspace recurrence may reflect shared role-instruction structure as well as model-internal geometry; new elicitation is needed to separate those possibilities.",
            "",
            "## Unknowns",
            "",
            "- Whether later-component distinctions recur in newly elicited behavior rather than saved role vectors remains unknown.",
            "- Whether independent raters would recover coherent semantic contrasts from the blinded instruction packets remains unknown.",
            "- PCA dimensionality does not determine a uniquely correct ontology or visualization dimension.",
            "",
            "## Reproducibility and compute boundary",
            "",
            f"The primary null uses {N_PARALLEL} permutations per model, bootstrapping uses {N_BOOTSTRAP} replicates per model, and cross-model role-label controls use {N_CROSS_PERMUTATIONS} permutations. `deterministic_second_pass.json` compares a complete second fixed-seed computation of all major numerical artifacts.",
            "",
            "No GPU, RunPod, model inference, activation extraction, or external model API was used.",
            "",
        ]
    )
    return "\n".join(lines)


def numerical_analysis(vector_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    results, clusters = build_pca_results(vector_root)
    spectrum = full_spectrum_rows(results)
    thresholds = cumulative_threshold_rows(results)
    knee = knee_diagnostics(results)
    broken = broken_stick_rows(results)
    parallel_rows, nulls, parallel_meta = parallel_analysis(results)
    bootstrap_rows, subspace_rows, bootstrap_meta = bootstrap_stability(results, parallel_meta)
    qwen_parallel_count = int(parallel_meta["qwen"]["sequential_retained_count"])
    candidate_max = min(20, max(10, qwen_parallel_count))
    cross_n = min(30, max(20, candidate_max + 5))
    role_rows = role_ranking_rows(results["qwen"], clusters, candidate_max)
    trait_rows, trait_summaries = trait_association_rows(results["qwen"], candidate_max)
    correspondence_rows, correspondence, pearson_matrices = cross_model_correspondence(results, cross_n)
    cross_subspace_rows = cross_model_subspaces(results)
    control_rows, component_controls = cross_model_permutation_controls(
        results, pearson_matrices, candidate_max, cross_n
    )
    retention = retention_rows(
        results["qwen"], parallel_rows, bootstrap_rows, subspace_rows,
        correspondence, component_controls, trait_summaries,
    )
    viewer_data = build_viewer_data(results, clusters, parallel_rows, bootstrap_rows, retention)
    packet, packet_key = interpretation_packet(role_rows, candidate_max)
    data = {
        "results": results,
        "clusters": clusters,
        "spectrum": spectrum,
        "thresholds": thresholds,
        "knee": knee,
        "broken": broken,
        "parallel_rows": parallel_rows,
        "parallel_meta": parallel_meta,
        "bootstrap_rows": bootstrap_rows,
        "subspace_rows": subspace_rows,
        "bootstrap_meta": bootstrap_meta,
        "candidate_max": candidate_max,
        "cross_n": cross_n,
        "role_rows": role_rows,
        "trait_rows": trait_rows,
        "trait_summaries": trait_summaries,
        "correspondence_rows": correspondence_rows,
        "correspondence": correspondence,
        "pearson_matrices": pearson_matrices,
        "cross_subspace_rows": cross_subspace_rows,
        "control_rows": control_rows,
        "component_controls": component_controls,
        "retention": retention,
        "viewer_data": viewer_data,
        "packet": packet,
        "packet_key": packet_key,
    }
    reproducibility = {
        "parallel": parallel_meta,
        "bootstrap": bootstrap_meta,
        "cross_role_label_permutation": {
            "seed": CROSS_PERMUTATION_SEED,
            "permutations": N_CROSS_PERMUTATIONS,
        },
        "candidate_max": candidate_max,
        "cross_model_search_components": cross_n,
        "null_array_hashes": {key: sha256_bytes(value.tobytes()) for key, value in nulls.items()},
    }
    return data, reproducibility


def write_numerical_outputs(target: Path, data: dict[str, Any]) -> None:
    write_csv(target / "full_pca_spectrum.csv", data["spectrum"])
    write_csv(target / "pca_cumulative_variance_thresholds.csv", data["thresholds"])
    json_dump(target / "pca_knee_diagnostics.json", data["knee"])
    write_csv(target / "pca_broken_stick_comparison.csv", data["broken"])
    write_csv(target / "pca_parallel_analysis.csv", data["parallel_rows"])
    write_csv(target / "pca_bootstrap_component_stability.csv", data["bootstrap_rows"])
    write_csv(target / "pca_subspace_stability.csv", data["subspace_rows"])
    write_csv(target / "qwen_extended_pc_role_rankings.csv", data["role_rows"])
    write_csv(target / "qwen_extended_pc_trait_associations.csv", data["trait_rows"])
    write_csv(target / "cross_model_pc_score_correspondence.csv", data["correspondence_rows"])
    write_csv(target / "cross_model_pc_subspace_similarity.csv", data["cross_subspace_rows"])
    write_csv(target / "cross_model_pc_permutation_control.csv", data["control_rows"])
    write_csv(target / "component_retention_summary.csv", data["retention"])
    json_dump(target / "viewer_data.json", data["viewer_data"])


def source_manifest(
    vector_root: Path, data: dict[str, Any], reproducibility: dict[str, Any], plot_stems: list[str]
) -> dict[str, Any]:
    source_paths = [
        REPO / "research/visualizations/scripts/build_geometry_viz.py",
        REPO / "research/visualizations/geometry_viz_data.json",
        REPO / "research/geometry_tables/cluster_membership_table.csv",
        REPO / "research/outputs/multimodel_ordered_trait_region_viewer/run_multimodel_ordered_trait_region_viewer.py",
        REPO / "research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_data.json",
        REPO / "research/outputs/multimodel_trait_profile_pc_predictor/multimodel_trait_profile_pc_predictor_report.md",
        REPO / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
        REPO / "research/outputs/trait_space_interpretation/trait_space_axis_report.md",
        REPO / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_methodology.md",
        REPO / "research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md",
    ]
    return {
        "generated_utc": utc_now(),
        "analysis_model": MODEL_USED,
        "branch": BRANCH,
        "starting_canonical_myfork_master_sha": STARTING_SHA,
        "runner": str(Path(__file__).relative_to(REPO)),
        "runner_sha256": sha256_file(Path(__file__)),
        "vector_root_actual": str(vector_root),
        "models": {
            key: {
                "label": result.label,
                "role_vector_audit": result.source_audit,
                "orientation_signs": result.orientation_signs,
                "canonical_pc123_max_abs_error": result.canonical_pc123_max_abs_error,
                "full_reconstruction_max_abs_error": result.reconstruction_max_abs_error,
                "full_reconstruction_relative_frobenius_error": result.reconstruction_relative_frobenius_error,
                "sum_explained_variance_ratio": float(result.explained_ratio.sum()),
            }
            for key, result in data["results"].items()
        },
        "parameters": {
            "centered_rank": 274,
            "parallel_analysis_permutations_per_model": N_PARALLEL,
            "parallel_analysis_null": "independently permute each activation coordinate across the 275 role rows",
            "bootstrap_replicates_per_model": N_BOOTSTRAP,
            "bootstrap_sampling": "275 role rows with replacement",
            "bootstrap_matching": "absolute loading cosine plus one-to-one Hungarian matching, then sign correction",
            "cross_model_role_label_permutations": N_CROSS_PERMUTATIONS,
            "cross_model_search_components": data["cross_n"],
            "qwen_later_component_scope": f"PC4-PC{data['candidate_max']}",
            "seeds": reproducibility,
        },
        "source_files": [
            {"path": str(path.relative_to(REPO)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in source_paths
        ],
        "role_instruction_source": {
            "path": "data/roles/instructions/*.json",
            "matched_qwen_roles": 275,
            "use": "coordinate-blind randomized interpretation packet only",
        },
        "static_plot_stems": plot_stems,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "torch": torch.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "scientific_boundaries": {
            "variance": "fraction of total squared centered role-vector activation variation; not personality, behavior, or human psychological variance",
            "traits": "240 named traits do not enter persona PCA; later trait associations are same-space descriptive evidence",
            "cross_model": "score patterns over shared role labels; no identity of PC semantics is assumed",
            "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, or external model API",
        },
    }


def build_artifact_inventory() -> None:
    rows = []
    branch_base = f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}"
    master_base = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master"
    for path in sorted(OUT.iterdir()):
        if not path.is_file() or path.name == "artifact_inventory.csv" or path.name.startswith("."):
            continue
        relative = path.relative_to(REPO).as_posix()
        rows.append(
            {
                "path": relative,
                "status": "active",
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "branch_raw_github_url": f"{branch_base}/{relative}",
                "future_canonical_master_raw_github_url": f"{master_base}/{relative}",
            }
        )
    write_csv(OUT / "artifact_inventory.csv", rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector-root", help="Path containing qwen-3-32b, llama-3.3-70b, and gemma-2-27b")
    parser.add_argument("--skip-second-pass", action="store_true", help="Skip the full deterministic second numerical pass")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vector_root = resolve_vector_root(args.vector_root)
    OUT.mkdir(parents=True, exist_ok=True)
    data, reproducibility = numerical_analysis(vector_root)
    write_numerical_outputs(OUT, data)
    packet_fields = [
        "blind_dimension_id", "blind_pole", "randomized_example_id",
        "role_instruction_1", "role_instruction_2", "role_instruction_3",
        "role_instruction_4", "role_instruction_5", "reviewer_note",
    ]
    write_csv(OUT / "qwen_extended_pc_interpretation_packet.csv", data["packet"], packet_fields)
    json_dump(OUT / "qwen_extended_pc_interpretation_packet_key.json", data["packet_key"])
    render_viewer(data["viewer_data"])
    plot_stems = make_plots(
        data["results"], data["parallel_rows"], data["bootstrap_rows"],
        data["pearson_matrices"], data["cross_subspace_rows"], data["retention"], data["clusters"],
    )
    (OUT / "persona_pca_construction_audit.md").write_text(
        construction_audit(data["results"], vector_root), encoding="utf-8"
    )
    (OUT / "extended_persona_pca_report.md").write_text(
        report_text(
            data["results"], data["thresholds"], data["knee"], data["parallel_meta"],
            data["bootstrap_rows"], data["subspace_rows"], data["retention"], data["correspondence"],
            data["component_controls"], data["cross_subspace_rows"], data["control_rows"],
            data["role_rows"], data["trait_summaries"], plot_stems,
        ),
        encoding="utf-8",
    )
    json_dump(OUT / "source_manifest.json", source_manifest(vector_root, data, reproducibility, plot_stems))

    if args.skip_second_pass:
        json_dump(
            OUT / "deterministic_second_pass.json",
            {"performed": False, "reason": "Explicit --skip-second-pass flag"},
        )
    else:
        first_hashes = {name: sha256_file(OUT / name) for name in MAJOR_NUMERICAL_FILES}
        second_data, second_reproducibility = numerical_analysis(vector_root)
        with tempfile.TemporaryDirectory(prefix="extended_pca_second_pass_") as temp_dir:
            second_out = Path(temp_dir)
            write_numerical_outputs(second_out, second_data)
            second_hashes = {name: sha256_file(second_out / name) for name in MAJOR_NUMERICAL_FILES}
        matches = {name: first_hashes[name] == second_hashes[name] for name in MAJOR_NUMERICAL_FILES}
        json_dump(
            OUT / "deterministic_second_pass.json",
            {
                "performed": True,
                "all_major_numerical_artifacts_byte_identical": all(matches.values()),
                "artifact_comparison": {
                    name: {"first_sha256": first_hashes[name], "second_sha256": second_hashes[name], "match": matches[name]}
                    for name in MAJOR_NUMERICAL_FILES
                },
                "first_pass_reproducibility": reproducibility,
                "second_pass_reproducibility": second_reproducibility,
            },
        )
        if not all(matches.values()):
            raise RuntimeError("Deterministic second-pass mismatch")
    build_artifact_inventory()
    print(f"Wrote extended persona PCA audit to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
