#!/usr/bin/env python3
"""Build anonymous cross-resolution spherical-K-means model banks.

This numerical phase deliberately writes opaque role IDs only. Role filenames
are used mechanically to verify the shared inventory but are not emitted until
the separately committed post-freeze semantic phase.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path

for variable in (
    "VECLIB_MAXIMUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[variable] = "1"

import numpy as np
import pandas as pd
import sklearn
import torch
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


MODELS = {
    "qwen": {"index": 0, "prefix": "Q", "directory": "qwen-3-32b"},
    "llama": {"index": 1, "prefix": "L", "directory": "llama-3.3-70b"},
    "gemma": {"index": 2, "prefix": "G", "directory": "gemma-2-27b"},
}
EXPECTED_HASHES = {
    "qwen": "3dc4bdcdcec301b3c947020f1c24755280af07aaf5fb8ab74ba10e3db9e73752",
    "llama": "3b1863bf5b9770223c46c1b8a7b8e818b4b70c65d484eec78a07fcaa9f5aa235",
    "gemma": "5ec98556b81c8cf499f6c4521b6120196124aacebefcb55d33338e8d8ad12191",
}
K_VALUES = range(4, 11)
N_STARTS = 100
N_SUBSAMPLES = 50
N_SUBSAMPLE_STARTS = 20
MAX_ITER = 300
REL_TOL = 1e-10
STABLE_STEPS = 5


@dataclass
class SphericalSolution:
    labels: np.ndarray
    objective: float
    iterations: int
    seed: int
    valid: bool
    monotone: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def aggregate_source_hash(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_vectors(directory: Path) -> tuple[list[str], np.ndarray, list[list[int]], str]:
    files = sorted(directory.glob("*.pt"))
    if len(files) != 275:
        raise RuntimeError(f"expected 275 role tensors in {directory}, found {len(files)}")
    source_hash = aggregate_source_hash(files)
    names: list[str] = []
    vectors: list[np.ndarray] = []
    shapes: list[list[int]] = []
    for path in files:
        tensor = torch.load(path, map_location="cpu").detach().to(torch.float64)
        shapes.append(list(tensor.shape))
        if tensor.ndim != 2:
            raise RuntimeError(f"expected layer-by-feature tensor: {path}")
        vector = tensor.mean(dim=0).numpy()
        norm = float(np.linalg.norm(vector))
        if not np.all(np.isfinite(vector)) or not np.isfinite(norm) or norm <= 0:
            raise RuntimeError(f"invalid vector: {path}")
        names.append(path.stem)
        vectors.append(vector / norm)
    if len(set(names)) != 275:
        raise RuntimeError("duplicate role filename stems")
    return names, np.stack(vectors), shapes, source_hash


def repair_empty(labels: np.ndarray, similarities: np.ndarray, k: int) -> np.ndarray:
    result = labels.copy()
    while True:
        counts = np.bincount(result, minlength=k)
        empty = np.flatnonzero(counts == 0)
        if not len(empty):
            return result
        donor_candidates = np.flatnonzero(counts[result] > 1)
        if not len(donor_candidates):
            raise RuntimeError("cannot repair empty spherical cluster")
        assigned = similarities[donor_candidates, result[donor_candidates]]
        move = donor_candidates[np.lexsort((donor_candidates, assigned))[0]]
        result[move] = int(empty[0])


def cluster_similarities(gram: np.ndarray, labels: np.ndarray, k: int) -> np.ndarray:
    n = len(labels)
    membership = np.zeros((n, k), dtype=np.float64)
    membership[np.arange(n), labels] = 1.0
    numerators = np.einsum("ij,jk->ik", gram, membership, optimize=False)
    norm_sq = np.sum(membership * numerators, axis=0)
    if np.any(norm_sq <= 0) or not np.all(np.isfinite(norm_sq)):
        raise FloatingPointError("invalid centroid norm")
    return numerators / np.sqrt(norm_sq)[None, :]


def objective_for_labels(gram: np.ndarray, labels: np.ndarray, k: int) -> float:
    similarities = cluster_similarities(gram, labels, k)
    return float(similarities[np.arange(len(labels)), labels].sum())


def spherical_kmeans_pp(gram: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = len(gram)
    centers = [int(rng.integers(n))]
    for _ in range(1, k):
        distance = np.maximum(1.0 - gram[:, centers].max(axis=1), 0.0)
        distance[np.asarray(centers)] = 0.0
        weights = distance**2
        if weights.sum() <= 0:
            remaining = np.setdiff1d(np.arange(n), np.asarray(centers), assume_unique=False)
            centers.append(int(remaining[0]))
        else:
            centers.append(int(rng.choice(n, p=weights / weights.sum())))
    similarities = gram[:, centers]
    labels = np.argmax(similarities, axis=1)
    return repair_empty(labels, similarities, k)


def fit_spherical(gram: np.ndarray, k: int, seed: int) -> SphericalSolution:
    rng = np.random.default_rng(seed)
    labels = spherical_kmeans_pp(gram, k, rng)
    previous = objective_for_labels(gram, labels, k)
    stable = 0
    monotone = True
    for iteration in range(1, MAX_ITER + 1):
        similarities = cluster_similarities(gram, labels, k)
        updated = np.argmax(similarities, axis=1)
        updated = repair_empty(updated, similarities, k)
        objective = objective_for_labels(gram, updated, k)
        tolerance = REL_TOL * max(1.0, abs(previous))
        if objective < previous - tolerance:
            monotone = False
            break
        if np.array_equal(updated, labels):
            labels = updated
            previous = objective
            return SphericalSolution(labels, previous, iteration, seed, True, monotone)
        if objective - previous < tolerance:
            stable += 1
        else:
            stable = 0
        labels = updated
        previous = objective
        if stable >= STABLE_STEPS:
            return SphericalSolution(labels, previous, iteration, seed, True, monotone)
    return SphericalSolution(labels, previous, iteration, seed, False, monotone)


def choose_best(solutions: list[SphericalSolution]) -> SphericalSolution:
    valid = [solution for solution in solutions if solution.valid and solution.monotone]
    if not valid:
        raise RuntimeError("no valid spherical K-means starts")
    valid.sort(key=lambda solution: (-solution.objective, solution.seed))
    best = valid[0]
    tied = [
        solution
        for solution in valid
        if best.objective - solution.objective <= 1e-12 * max(1.0, abs(best.objective))
    ]
    return min(tied, key=lambda solution: solution.seed)


def anonymous_mapping(labels: np.ndarray, model: str, k: int) -> dict[int, str]:
    prefix = MODELS[model]["prefix"]
    ordering = []
    for cluster in range(k):
        members = np.flatnonzero(labels == cluster).astype("<i8", copy=False)
        digest = sha256_bytes(members.tobytes())
        ordering.append((digest, len(members), cluster))
    ordering.sort()
    return {
        cluster: f"{prefix}{k:02d}_{chr(65 + rank)}"
        for rank, (_, _, cluster) in enumerate(ordering)
    }


def stability_label(median_ari: float, p10_ari: float) -> str:
    if median_ari >= 0.90 and p10_ari >= 0.75:
        return "high"
    if median_ari >= 0.75 and p10_ari >= 0.50:
        return "moderate"
    return "low"


def metric_summary(values: list[float], prefix: str) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        f"{prefix}_median": float(np.median(array)),
        f"{prefix}_p10": float(np.quantile(array, 0.10)),
        f"{prefix}_minimum": float(array.min()),
    }


def fit_many(gram: np.ndarray, k: int, seeds: list[int]) -> list[SphericalSolution]:
    return [fit_spherical(gram, k, seed) for seed in seeds]


def assign_from_subsample(
    full_gram: np.ndarray, sample: np.ndarray, sample_labels: np.ndarray, k: int
) -> np.ndarray:
    membership = np.zeros((len(sample), k), dtype=np.float64)
    membership[np.arange(len(sample)), sample_labels] = 1.0
    numerator = np.einsum("ij,jk->ik", full_gram[:, sample], membership, optimize=False)
    sample_gram = full_gram[np.ix_(sample, sample)]
    sample_numerator = np.einsum("ij,jk->ik", sample_gram, membership, optimize=False)
    norm_sq = np.sum(membership * sample_numerator, axis=0)
    similarities = numerator / np.sqrt(norm_sq)[None, :]
    return np.argmax(similarities, axis=1)


def centroid_matrix(vectors: np.ndarray, labels: np.ndarray, k: int) -> np.ndarray:
    centroids = []
    for cluster in range(k):
        centroid = vectors[labels == cluster].mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        centroids.append(centroid)
    return np.stack(centroids)


def direct_gram_check(vectors: np.ndarray, gram: np.ndarray) -> float:
    labels = np.arange(len(vectors)) % 4
    gram_similarity = cluster_similarities(gram, labels, 4)
    native = centroid_matrix(vectors, labels, 4)
    native_similarity = np.einsum("id,kd->ik", vectors, native, optimize=False)
    return float(np.max(np.abs(gram_similarity - native_similarity)))


def model_bank(model: str, vectors: np.ndarray, output: Path) -> dict[str, object]:
    model_index = MODELS[model]["index"]
    gram = np.clip(np.einsum("id,jd->ij", vectors, vectors, optimize=False), -1.0, 1.0)
    gram_error = direct_gram_check(vectors, gram)
    if gram_error > 1e-10:
        raise RuntimeError(f"Gram/native equivalence failed: {gram_error}")

    memberships: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    start_rows: list[dict[str, object]] = []
    subsample_rows: list[dict[str, object]] = []
    retained: dict[int, tuple[SphericalSolution, dict[int, str]]] = {}
    centroid_arrays: dict[str, np.ndarray] = {}
    centroid_rows: list[dict[str, object]] = []

    for k in K_VALUES:
        started = time.time()
        seeds = [2_026_091 + 10_000 * model_index + 100 * k + s for s in range(1, N_STARTS + 1)]
        starts = fit_many(gram, k, seeds)
        valid = [solution for solution in starts if solution.valid and solution.monotone]
        best = choose_best(starts)
        mapping = anonymous_mapping(best.labels, model, k)
        retained[k] = (best, mapping)
        aris = [float(adjusted_rand_score(best.labels, solution.labels)) for solution in valid]
        nmis = [float(normalized_mutual_info_score(best.labels, solution.labels)) for solution in valid]
        objectives = np.asarray([solution.objective for solution in valid])
        for solution, ari, nmi in zip(valid, aris, nmis):
            start_rows.append(
                {
                    "model": model,
                    "K": k,
                    "seed": solution.seed,
                    "objective": solution.objective,
                    "iterations": solution.iterations,
                    "ari_to_retained": ari,
                    "nmi_to_retained": nmi,
                    "retained_start": solution.seed == best.seed,
                }
            )

        subsample_aris: list[float] = []
        subsample_nmis: list[float] = []
        for r in range(1, N_SUBSAMPLES + 1):
            sample_seed = 3_026_091 + 10_000 * model_index + 100 * k + r
            sample_rng = np.random.default_rng(sample_seed)
            sample = np.sort(sample_rng.choice(len(vectors), size=math.floor(0.8 * len(vectors)), replace=False))
            sample_gram = gram[np.ix_(sample, sample)]
            fit_seeds = [
                4_026_091 + 1_000_000 * model_index + 10_000 * k + 100 * r + s
                for s in range(1, N_SUBSAMPLE_STARTS + 1)
            ]
            refits = fit_many(sample_gram, k, fit_seeds)
            refit = choose_best(refits)
            full_labels = assign_from_subsample(gram, sample, refit.labels, k)
            ari = float(adjusted_rand_score(best.labels, full_labels))
            nmi = float(normalized_mutual_info_score(best.labels, full_labels))
            subsample_aris.append(ari)
            subsample_nmis.append(nmi)
            subsample_rows.append(
                {
                    "model": model,
                    "K": k,
                    "resample": r,
                    "sample_seed": sample_seed,
                    "valid_starts": sum(x.valid and x.monotone for x in refits),
                    "best_seed": refit.seed,
                    "ari_to_full": ari,
                    "nmi_to_full": nmi,
                }
            )

        centroids = centroid_matrix(vectors, best.labels, k)
        similarities = np.einsum("id,kd->ik", vectors, centroids, optimize=False)
        counts = np.bincount(best.labels, minlength=k)
        for cluster in range(k):
            profile_id = mapping[cluster]
            centroid = centroids[cluster].astype("<f8", copy=False)
            centroid_arrays[profile_id] = centroid
            centroid_rows.append(
                {
                    "model": model,
                    "K": k,
                    "profile_id": profile_id,
                    "native_dimension": len(centroid),
                    "centroid_l2_norm": float(np.linalg.norm(centroid)),
                    "member_count": int(counts[cluster]),
                    "centroid_float64_le_sha256": sha256_bytes(centroid.tobytes()),
                }
            )
            members = np.flatnonzero(best.labels == cluster)
            order = members[np.argsort(-similarities[members, cluster], kind="stable")]
            rank = {int(index): position + 1 for position, index in enumerate(order)}
            for index in members:
                memberships.append(
                    {
                        "model": model,
                        "K": k,
                        "profile_id": profile_id,
                        "opaque_role_id": f"R{index + 1:03d}",
                        "similarity_to_centroid": float(similarities[index, cluster]),
                        "within_profile_centroid_rank": rank[int(index)],
                    }
                )

        start_stats = metric_summary(aris, "start_ari")
        subsample_stats = metric_summary(subsample_aris, "subsample_ari")
        sorted_objectives = np.sort(objectives)[::-1]
        summaries.append(
            {
                "model": model,
                "K": k,
                "fit_status": "available",
                "valid_starts": len(valid),
                "best_seed": best.seed,
                "best_objective": best.objective,
                "objective_per_role": best.objective / len(vectors),
                "objective_min": float(objectives.min()),
                "objective_max": float(objectives.max()),
                "objective_sd": float(objectives.std(ddof=1)),
                "best_to_second_objective_gap": float(sorted_objectives[0] - sorted_objectives[1]),
                "best_iterations": best.iterations,
                **start_stats,
                "start_nmi_median": float(np.median(nmis)),
                "start_ari_share_ge_0_90": float(np.mean(np.asarray(aris) >= 0.90)),
                "start_ari_share_ge_0_75": float(np.mean(np.asarray(aris) >= 0.75)),
                "start_stability": stability_label(start_stats["start_ari_median"], start_stats["start_ari_p10"]),
                "valid_subsample_refits": len(subsample_aris),
                **subsample_stats,
                "subsample_nmi_median": float(np.median(subsample_nmis)),
                "subsample_ari_share_ge_0_75": float(np.mean(np.asarray(subsample_aris) >= 0.75)),
                "subsample_stability": stability_label(
                    subsample_stats["subsample_ari_median"], subsample_stats["subsample_ari_p10"]
                ),
                "minimum_cluster_size": int(counts.min()),
                "maximum_cluster_size": int(counts.max()),
                "cluster_sizes": ";".join(
                    f"{mapping[cluster]}:{int(counts[cluster])}" for cluster in sorted(mapping, key=mapping.get)
                ),
                "small_cluster_warning": bool(counts.min() < 5),
                "elapsed_seconds": time.time() - started,
            }
        )
        print(json.dumps({"completed_model": model, "K": k, **summaries[-1]}), flush=True)

    continuity_rows: list[dict[str, object]] = []
    for lower_k in range(4, 10):
        lower, lower_map = retained[lower_k]
        higher, higher_map = retained[lower_k + 1]
        pair_ari = float(adjusted_rand_score(lower.labels, higher.labels))
        pair_nmi = float(normalized_mutual_info_score(lower.labels, higher.labels))
        for low_cluster in range(lower_k):
            low_members = lower.labels == low_cluster
            for high_cluster in range(lower_k + 1):
                high_members = higher.labels == high_cluster
                overlap = int(np.sum(low_members & high_members))
                union = int(np.sum(low_members | high_members))
                continuity_rows.append(
                    {
                        "model": model,
                        "lower_K": lower_k,
                        "higher_K": lower_k + 1,
                        "lower_profile_id": lower_map[low_cluster],
                        "higher_profile_id": higher_map[high_cluster],
                        "lower_size": int(low_members.sum()),
                        "higher_size": int(high_members.sum()),
                        "overlap_count": overlap,
                        "jaccard": overlap / union,
                        "share_of_lower": overlap / int(low_members.sum()),
                        "share_of_higher": overlap / int(high_members.sum()),
                        "adjacent_partition_ari": pair_ari,
                        "adjacent_partition_nmi": pair_nmi,
                    }
                )

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(memberships).sort_values(["K", "profile_id", "within_profile_centroid_rank"]).to_csv(
        output / "memberships.csv", index=False
    )
    pd.DataFrame(summaries).to_csv(output / "solution_summary.csv", index=False)
    pd.DataFrame(start_rows).to_csv(output / "start_stability.csv", index=False)
    pd.DataFrame(subsample_rows).to_csv(output / "subsample_stability.csv", index=False)
    pd.DataFrame(continuity_rows).to_csv(output / "adjacent_k_continuity.csv", index=False)
    pd.DataFrame(centroid_rows).sort_values(["K", "profile_id"]).to_csv(
        output / "native_centroid_metadata.csv", index=False
    )
    np.savez_compressed(output / "native_centroids.npz", **centroid_arrays)
    return {
        "gram_native_max_abs_error": gram_error,
        "solutions": summaries,
        "opaque_role_mapping_committed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    loaded: dict[str, tuple[list[str], np.ndarray, list[list[int]], str]] = {}
    for model, spec in MODELS.items():
        directory = args.vector_root.resolve() / spec["directory"] / "role_vectors"
        loaded[model] = load_vectors(directory)
        if loaded[model][3] != EXPECTED_HASHES[model]:
            raise RuntimeError(f"{model} source hash mismatch: {loaded[model][3]}")
    reference_names = loaded["qwen"][0]
    if any(names != reference_names for names, _, _, _ in loaded.values()):
        raise RuntimeError("the three models do not share identical sorted 275-role inventories")

    results = {}
    sources = {}
    for model, (names, vectors, shapes, source_hash) in loaded.items():
        results[model] = model_bank(model, vectors, output / "model" / model)
        sources[model] = {
            "role_count": len(names),
            "tensor_shapes": sorted({tuple(shape) for shape in shapes}),
            "native_dimension": int(vectors.shape[1]),
            "aggregate_filename_plus_bytes_sha256": source_hash,
            "opaque_inventory_sha256": sha256_bytes("\n".join(names).encode("utf-8")),
        }
    manifest = {
        "status": "ANONYMOUS NUMERICAL MODEL BANK; SEMANTIC ROLE MAP NOT EMITTED",
        "method": "exact Gram implementation of spherical K-means on L2-normalized layer-mean vectors",
        "K_values": list(K_VALUES),
        "starts_per_solution": N_STARTS,
        "subsample_refits_per_solution": N_SUBSAMPLES,
        "starts_per_subsample_refit": N_SUBSAMPLE_STARTS,
        "sources": sources,
        "results": results,
        "software": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "torch": torch.__version__,
        },
        "boundaries": {
            "human_data_loaded": False,
            "trait_matrices_loaded": False,
            "semantic_role_names_emitted": False,
            "human_model_scores_computed": False,
            "gpu_used": False,
            "runpod_used": False,
            "new_inference": False,
            "new_activation_extraction": False,
            "external_model_api": False,
        },
    }
    json_write(output / "model" / "numerical_bank_manifest.json", manifest)


if __name__ == "__main__":
    main()
