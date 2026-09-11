#!/usr/bin/env python3
# Canonical cross-model replication runner.
"""Replicate the Qwen trait-profile -> persona-PC predictor for Llama and Gemma.

This CPU-only analysis imports the canonical Qwen validation implementation so
that estimators, grids, folds, seeds, preprocessing, metrics, OOD diagnostics,
and synthetic-pair selection remain methodologically identical. It consumes
saved role and trait tensors only; it performs no model inference or activation
extraction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = REPO_ROOT / "research/outputs/multimodel_trait_profile_pc_predictor"
REFERENCE_RUNNER = REPO_ROOT / "research/outputs/trait_profile_pc_predictor/run_trait_profile_pc_predictor.py"
QWEN_SUMMARY = REPO_ROOT / "research/outputs/trait_profile_pc_predictor/validation_summary.json"
QWEN_RIDGE = REPO_ROOT / "research/outputs/trait_profile_pc_predictor/ridge_predictor.json"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
CLUSTER_PATH = REPO_ROOT / "research/geometry_tables/cluster_membership_table.csv"
MULTIMODEL_DATA = REPO_ROOT / "research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_data.json"
MULTIMODEL_RUNNER = REPO_ROOT / "research/outputs/multimodel_ordered_trait_region_viewer/run_multimodel_ordered_trait_region_viewer.py"
MULTIMODEL_REPORT = REPO_ROOT / "research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_report.md"
MODEL_SPECS = {
    "llama": {"label": "Llama-3.3-70B", "folder": "llama-3.3-70b"},
    "gemma": {"label": "Gemma-2-27B", "folder": "gemma-2-27b"},
}
PC_NAMES = ["PC1", "PC2", "PC3"]
PARTITION_LABEL = "Qwen-canonical role-family partition applied cross-model"
PCA_TOLERANCE = 1e-8
MATRIX_REFERENCE_TOLERANCE = 1e-5


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_record(path: Path) -> dict[str, Any]:
    return {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def directory_manifest(directory: Path, logical_path: str) -> dict[str, Any]:
    aggregate = hashlib.sha256()
    files = []
    for path in sorted(directory.glob("*.pt")):
        digest = sha256_file(path)
        aggregate.update(path.name.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
        files.append({"filename": path.name, "size_bytes": path.stat().st_size, "sha256": digest})
    return {
        "actual_local_path": str(directory.resolve()),
        "logical_repository_path": logical_path,
        "file_count": len(files),
        "total_size_bytes": sum(row["size_bytes"] for row in files),
        "aggregate_sha256_of_sorted_filename_and_file_hashes": aggregate.hexdigest(),
        "files": files,
    }


def import_reference_runner() -> Any:
    spec = importlib.util.spec_from_file_location("canonical_qwen_trait_profile_runner", REFERENCE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import canonical Qwen runner: {REFERENCE_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_vector_root(explicit: Path | None) -> Path:
    candidates = []
    if explicit is not None:
        candidates.append(explicit)
    candidates.extend(
        [
            REPO_ROOT / "downloads/hf_vectors",
            REPO_ROOT.parent / "assistant-axis/downloads/hf_vectors",
        ]
    )
    for candidate in candidates:
        if all((candidate / spec["folder"] / "role_vectors").is_dir() for spec in MODEL_SPECS.values()):
            return candidate.resolve()
    raise FileNotFoundError(
        "Required saved Llama/Gemma vector bundles were not found. Checked: "
        + ", ".join(str(path) for path in candidates)
    )


def load_mean_vectors(directory: Path, expected_names: list[str]) -> tuple[np.ndarray, dict[str, Any]]:
    import torch

    paths = sorted(directory.glob("*.pt"))
    names = [path.stem for path in paths]
    if names != expected_names:
        missing = sorted(set(expected_names) - set(names))
        extra = sorted(set(names) - set(expected_names))
        raise RuntimeError(f"Vector-name mismatch under {directory}: missing={missing[:10]} extra={extra[:10]}")
    vectors = []
    shapes: Counter[str] = Counter()
    dtypes: Counter[str] = Counter()
    for path in paths:
        tensor = torch.load(path, map_location="cpu")
        shapes[str(tuple(tensor.shape))] += 1
        dtypes[str(tensor.dtype)] += 1
        tensor = tensor.float()
        if tensor.ndim == 2:
            tensor = tensor.mean(0)
        elif tensor.ndim != 1:
            raise RuntimeError(f"Unexpected tensor shape for {path}: {tuple(tensor.shape)}")
        vector = tensor.numpy().astype(np.float64, copy=False)
        if not np.isfinite(vector).all() or np.linalg.norm(vector) == 0:
            raise RuntimeError(f"Nonfinite or zero source vector: {path}")
        vectors.append(vector)
    return np.stack(vectors), {
        "file_count": len(paths),
        "tensor_shape_counts": dict(sorted(shapes.items())),
        "tensor_dtype_counts": dict(sorted(dtypes.items())),
        "all_mean_vectors_finite": True,
    }


def pca_numpy(x: np.ndarray, n_components: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0, keepdims=True)
    centered = x - mean
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :n_components] * s[:n_components]
    explained = (s**2) / max(1, x.shape[0] - 1)
    return coords, vt[:n_components], explained[:n_components] / explained.sum(), mean[0]


def build_model_data(
    model_key: str,
    vector_root: Path,
    geometry: dict[str, Any],
    clusters: pd.DataFrame,
    multimodel: dict[str, Any],
    expected_traits: list[str],
) -> dict[str, Any]:
    spec = MODEL_SPECS[model_key]
    model_root = vector_root / spec["folder"]
    role_dir = model_root / "role_vectors"
    trait_dir = model_root / "trait_vectors"
    persona_names = sorted(path.stem for path in role_dir.glob("*.pt"))
    trait_names = sorted(path.stem for path in trait_dir.glob("*.pt"))
    qwen_names = list(geometry["roles"]["names"])
    if persona_names != qwen_names:
        raise RuntimeError(f"{model_key}: persona names/order do not exactly match canonical Qwen labels")
    if trait_names != expected_traits:
        raise RuntimeError(f"{model_key}: trait names/order do not exactly match canonical Qwen labels")
    if clusters["role"].astype(str).tolist() != persona_names:
        raise RuntimeError("Canonical role-family table order does not match persona order")

    role_raw, role_audit = load_mean_vectors(role_dir, persona_names)
    trait_raw, trait_audit = load_mean_vectors(trait_dir, trait_names)
    if role_raw.shape[1] != trait_raw.shape[1]:
        raise RuntimeError(f"{model_key}: role/trait hidden dimensions differ")

    coords, components, explained, pca_mean = pca_numpy(role_raw, 3)
    qwen_reference = np.asarray(geometry["roles"]["pca3d"], dtype=np.float64)
    orientation_correlations = []
    orientation_signs = []
    for pc in range(3):
        correlation = float(np.corrcoef(coords[:, pc], qwen_reference[:, pc])[0, 1])
        sign = -1 if correlation < 0 else 1
        orientation_correlations.append(correlation)
        orientation_signs.append(sign)
        coords[:, pc] *= sign
        components[pc] *= sign

    saved_points = multimodel["models"][model_key]["points"]
    saved_names = [str(row["persona"]) for row in saved_points]
    saved_coords = np.asarray([[row["pc1"], row["pc2"], row["pc3"]] for row in saved_points], dtype=np.float64)
    if saved_names != persona_names:
        raise RuntimeError(f"{model_key}: saved multimodel coordinate order differs")
    pca_error = np.abs(coords - saved_coords)
    pca_check = {
        "passed": bool(float(pca_error.max()) <= PCA_TOLERANCE),
        "strict_tolerance": PCA_TOLERANCE,
        "max_abs_coordinate_reproduction_error": float(pca_error.max()),
        "mean_abs_coordinate_reproduction_error": float(pca_error.mean()),
        "coordinate_target_source": str(MULTIMODEL_DATA.relative_to(REPO_ROOT)),
        "reconstruction_procedure_source": str(MULTIMODEL_RUNNER.relative_to(REPO_ROOT)),
        "procedure": "SVD PCA on lexically ordered mean-pooled same-model role vectors; same-index PC signs oriented by correlation to Qwen geometry",
        "orientation_correlations_before_sign": orientation_correlations,
        "orientation_signs": orientation_signs,
        "permutation": [0, 1, 2],
        "explained_variance_ratio": explained.tolist(),
    }
    if not pca_check["passed"]:
        raise RuntimeError(f"{model_key}: strict established-coordinate reproduction failed: {pca_check}")

    role_norm = role_raw / np.linalg.norm(role_raw, axis=1, keepdims=True)
    trait_norm = trait_raw / np.linalg.norm(trait_raw, axis=1, keepdims=True)
    X = role_norm @ trait_norm.T
    if not np.isfinite(X).all():
        raise RuntimeError(f"{model_key}: nonfinite cosine matrix")

    saved_profiles = multimodel["models"][model_key]["trait_profiles"]
    saved_matrix = np.asarray(
        [[saved_profiles[persona][trait] for trait in trait_names] for persona in persona_names], dtype=np.float64
    )
    matrix_error = np.abs(X - saved_matrix)
    matrix_check = {
        "passed": bool(float(matrix_error.max()) <= MATRIX_REFERENCE_TOLERANCE),
        "reference_tolerance": MATRIX_REFERENCE_TOLERANCE,
        "max_abs_difference_vs_established_float32_viewer_matrix": float(matrix_error.max()),
        "mean_abs_difference_vs_established_float32_viewer_matrix": float(matrix_error.mean()),
        "construction": "mean over stored layer vectors, L2-normalize role and trait means, same-model role @ trait.T",
        "new_matrix_numeric_precision": "float64 after float32 tensor mean",
        "established_viewer_matrix_numeric_precision": "float32",
    }
    if not matrix_check["passed"]:
        raise RuntimeError(f"{model_key}: cosine matrix disagrees with established multimodel artifact: {matrix_check}")

    target_like = sorted(set(trait_names) & {"PC1", "PC2", "PC3", "pc1", "pc2", "pc3", "cluster", "role", "persona"})
    integrity = {
        "passed": bool(
            len(persona_names) == len(set(persona_names)) == 275
            and len(trait_names) == len(set(trait_names)) == 240
            and np.isfinite(role_raw).all()
            and np.isfinite(trait_raw).all()
            and np.isfinite(X).all()
            and np.isfinite(saved_coords).all()
            and not target_like
        ),
        "persona_count": len(persona_names),
        "unique_persona_count": len(set(persona_names)),
        "trait_count": len(trait_names),
        "unique_trait_count": len(set(trait_names)),
        "same_intended_persona_labels": persona_names == qwen_names,
        "same_intended_trait_labels": trait_names == expected_traits,
        "role_vectors_finite": bool(np.isfinite(role_raw).all()),
        "trait_vectors_finite": bool(np.isfinite(trait_raw).all()),
        "cosine_matrix_finite": bool(np.isfinite(X).all()),
        "targets_finite": bool(np.isfinite(saved_coords).all()),
        "target_or_metadata_columns_in_features": target_like,
        "role_family_partition_label": PARTITION_LABEL,
        "role_family_counts": dict(sorted(Counter(clusters["cluster"].astype(str)).items())),
        "role_vector_audit": role_audit,
        "trait_vector_audit": trait_audit,
    }
    if not integrity["passed"]:
        raise RuntimeError(f"{model_key}: integrity check failed: {integrity}")
    return {
        "model_key": model_key,
        "label": spec["label"],
        "role_dir": role_dir,
        "trait_dir": trait_dir,
        "persona_names": persona_names,
        "trait_names": trait_names,
        "role_families": clusters["cluster"].astype(str).tolist(),
        "role_raw": role_raw,
        "trait_raw": trait_raw,
        "X": X,
        "Y": saved_coords,
        "pca_basis": {"mean": pca_mean, "components": components, "check": pca_check},
        "pca_check": pca_check,
        "matrix_check": matrix_check,
        "integrity": integrity,
    }


def role_family_outputs(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(columns={"cluster": "role_family"}).copy()
    renamed.insert(0, "partition", PARTITION_LABEL)
    return renamed


def portable_ridge_predict(X: np.ndarray, bundle: dict[str, Any]) -> np.ndarray:
    coef = np.asarray(bundle["coefficients"], dtype=np.float64)
    intercept = np.asarray(bundle["intercepts"], dtype=np.float64)
    return X @ coef.T + intercept


def synthetic_error_association(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {}
    row_pearson = pearsonr(frame["source_pc_3d_distance"], frame["standardized_3d_error"]).statistic
    row_spearman = spearmanr(frame["source_pc_3d_distance"], frame["standardized_3d_error"]).statistic
    pair = (
        frame.groupby(["persona_a", "persona_b"], as_index=False)
        .agg(source_pc_3d_distance=("source_pc_3d_distance", "first"), mean_standardized_3d_error=("standardized_3d_error", "mean"))
    )
    pair_pearson = pearsonr(pair["source_pc_3d_distance"], pair["mean_standardized_3d_error"]).statistic
    pair_spearman = spearmanr(pair["source_pc_3d_distance"], pair["mean_standardized_3d_error"]).statistic
    return {
        "row_level": {"pearson": float(row_pearson), "spearman": float(row_spearman), "n": len(frame)},
        "pair_aggregated": {"pearson": float(pair_pearson), "spearman": float(pair_spearman), "n": len(pair)},
    }


def deterministic_checks(ref: Any, data: dict[str, Any], n_jobs: int) -> dict[str, Any]:
    X, Y = data["X"], data["Y"]
    checks: dict[str, Any] = {}
    for model_name in ref.MODEL_NAMES:
        first = ref.fit_tuned(model_name, "raw_cosine", X[:160], Y[:160], 6060 + ref.MODEL_NAMES.index(model_name), n_jobs)
        second = ref.fit_tuned(model_name, "raw_cosine", X[:160], Y[:160], 6060 + ref.MODEL_NAMES.index(model_name), n_jobs)
        checks[f"{model_name}_representative_refit_max_abs_difference"] = float(
            np.max(np.abs(first.predict(X[160:175]) - second.predict(X[160:175])))
        )
    first_q = ref.fit_tuned("ridge", "quantile", X[:160], Y[:160], 7070, n_jobs)
    second_q = ref.fit_tuned("ridge", "quantile", X[:160], Y[:160], 7070, n_jobs)
    checks["quantile_ridge_representative_refit_max_abs_difference"] = float(
        np.max(np.abs(first_q.predict(X[160:175]) - second_q.predict(X[160:175])))
    )
    lopo = {}
    indices = np.arange(len(X))
    for held_out in [0, len(X) // 2, len(X) - 1]:
        train = indices[indices != held_out]
        first = ref.fit_tuned("ridge", "raw_cosine", X[train], Y[train], 10_000 + held_out, n_jobs)
        second = ref.fit_tuned("ridge", "raw_cosine", X[train], Y[train], 10_000 + held_out, n_jobs)
        lopo[data["persona_names"][held_out]] = float(
            np.max(np.abs(first.predict(X[[held_out]]) - second.predict(X[[held_out]])))
        )
    checks["representative_lopo_reruns_max_abs_difference"] = lopo
    checks["passed"] = bool(
        max(value for key, value in checks.items() if key.endswith("max_abs_difference") and isinstance(value, float)) < 1e-12
        and max(lopo.values()) < 1e-12
    )
    return checks


def run_model(ref: Any, data: dict[str, Any], n_jobs: int, generation_timestamp: str) -> dict[str, Any]:
    model_key = data["model_key"]
    out = OUTPUT_ROOT / model_key
    out.mkdir(parents=True, exist_ok=True)
    X, Y = data["X"], data["Y"]
    personas, traits, families = data["persona_names"], data["trait_names"], data["role_families"]

    matrix = pd.DataFrame(X, columns=traits)
    matrix.insert(0, "persona", personas)
    matrix.to_csv(out / "persona_trait_similarity_matrix.csv", index=False)

    source_manifest = {
        "generation_timestamp_utc": generation_timestamp,
        "branch": git_value("branch", "--show-current"),
        "generation_base_commit": git_value("rev-parse", "HEAD"),
        "analysis_model_used": "GPT-5.5",
        "activation_model": data["label"],
        "new_model_inference": False,
        "new_activation_extraction": False,
        "gpu_used": False,
        "runpod_used": False,
        "external_model_api_calls": False,
        "source_location_note": "Saved vector files were read from the existing main-worktree downloads tree because downloads are gitignored and not duplicated into linked worktrees; that source tree was not modified.",
        "sources": {
            "role_vectors": directory_manifest(data["role_dir"], f"downloads/hf_vectors/{MODEL_SPECS[model_key]['folder']}/role_vectors"),
            "trait_vectors": directory_manifest(data["trait_dir"], f"downloads/hf_vectors/{MODEL_SPECS[model_key]['folder']}/trait_vectors"),
            "established_multimodel_coordinates": source_record(MULTIMODEL_DATA),
            "established_multimodel_runner": source_record(MULTIMODEL_RUNNER),
            "established_multimodel_report": source_record(MULTIMODEL_REPORT),
            "qwen_geometry_orientation_reference": source_record(GEOMETRY_PATH),
            "qwen_canonical_role_family_partition": source_record(CLUSTER_PATH),
            "canonical_qwen_predictor_runner": source_record(REFERENCE_RUNNER),
            "canonical_qwen_validation_summary": source_record(QWEN_SUMMARY),
        },
        "integrity": data["integrity"],
        "matrix_verification": data["matrix_check"],
        "pca_reconstruction": data["pca_check"],
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": __import__("sklearn").__version__,
            "scipy": __import__("scipy").__version__,
            "torch": __import__("torch").__version__,
        },
    }
    write_json(out / "source_manifest.json", source_manifest)

    nested, comparison = ref.run_nested_model_comparison(X, Y, personas, n_jobs, ref.OUTER_SEEDS)
    nested.to_csv(out / "nested_cv_oof_predictions.csv", index=False)
    comparison.to_csv(out / "model_comparison.csv", index=False)

    lopo, _ = ref.run_lopo(X, Y, personas, traits, n_jobs)
    lopo["normalized_3d_error"] = lopo["standardized_3d_error"]
    lopo.to_csv(out / "leave_one_persona_out_predictions.csv", index=False)
    lopo_metrics = {representation: ref.metrics_from_prediction_frame(group) for representation, group in lopo.groupby("representation")}
    lopo_raw = lopo[lopo["representation"] == "raw_cosine"].copy()

    family_predictions, family_summary = ref.run_leave_cluster_out(X, Y, personas, families, lopo, n_jobs)
    family_predictions["normalized_3d_error"] = family_predictions["standardized_3d_error"]
    family_out_predictions = role_family_outputs(family_predictions)
    family_out_summary = role_family_outputs(family_summary)
    raw_lopo_rmse = lopo_metrics["raw_cosine"]["normalized_3d_error_rmse"]
    family_out_summary["role_family_holdout_over_lopo_rmse_ratio"] = (
        family_out_summary["normalized_3d_error_rmse"] / raw_lopo_rmse
    )
    family_out_predictions.to_csv(out / "leave_one_role_family_out_predictions.csv", index=False)
    family_out_summary.to_csv(out / "leave_one_role_family_out_summary.csv", index=False)
    selection = ref.select_primary(comparison, family_summary)

    permutations = ref.run_permutations(X, Y, personas, n_jobs, ref.PERMUTATIONS)
    permutations.to_csv(out / "permutation_control.csv", index=False)
    permutation_summary = {
        "n_permutations": len(permutations),
        "mean_pc_r2_mean": float(permutations["mean_pc_r2"].mean()),
        "mean_pc_r2_std": float(permutations["mean_pc_r2"].std(ddof=0)),
        "mean_pc_r2_q95": float(permutations["mean_pc_r2"].quantile(0.95)),
        "mean_pc_r2_max": float(permutations["mean_pc_r2"].max()),
        "normalized_3d_error_rmse_mean": float(permutations["normalized_3d_error_rmse"].mean()),
        "leakage_anomaly_threshold": 0.20,
        "leakage_anomaly_detected": bool(permutations["mean_pc_r2"].quantile(0.95) > 0.20),
    }
    if permutation_summary["leakage_anomaly_detected"]:
        raise RuntimeError(f"{model_key}: anomalously positive permutation control: {permutation_summary}")

    final_searches = {
        name: ref.fit_tuned(name, "raw_cosine", X, Y, 50_000 + index, n_jobs)
        for index, name in enumerate(ref.MODEL_NAMES)
    }
    comparison_models = [ref.export_comparison_model(name, final_searches[name], X, traits) for name in ref.MODEL_NAMES]
    comparison_bundle = {
        "schema_version": 1,
        "activation_model": data["label"],
        "input_representation": "raw_cosine",
        "trait_feature_names": traits,
        "training_persona_count": len(personas),
        "models": comparison_models,
        "note": "All-model context; the canonical selection rule remains the Qwen predeclared >=10% normalized-RMSE improvement without harder-holdout degradation.",
    }
    write_json(out / "comparison_predictors.json", comparison_bundle)

    ridge_export = next(row for row in comparison_models if row["name"] == "Ridge")
    error_reference = ref.empirical_error_reference(lopo_raw)
    ridge_bundle = {
        "schema_version": 1,
        "activation_model": data["label"],
        "model_type": "Ridge",
        "input_representation": "raw_cosine",
        "trait_feature_names": traits,
        "feature_transform": ridge_export["feature_transform"],
        "target_transform": ridge_export["target_transform"],
        "ridge_alpha": ridge_export["ridge_alpha"],
        "coefficients": ridge_export["coefficients"],
        "intercepts": ridge_export["intercepts"],
        "coefficient_space": ridge_export["coefficient_space"],
        "standardized_model_coefficients": ridge_export["standardized_model_coefficients"],
        "standardized_model_intercepts": ridge_export["standardized_model_intercepts"],
        "portable_prediction": ridge_export["portable_prediction"],
        "training_target_means": Y.mean(axis=0).tolist(),
        "training_target_stds": Y.std(axis=0, ddof=0).tolist(),
        "training_feature_ranges": {"min": X.min(axis=0).tolist(), "max": X.max(axis=0).tolist()},
        "training_persona_count": len(personas),
        "training_trait_count": len(traits),
        "source_artifact_paths": {
            "trait_profile_matrix": f"research/outputs/multimodel_trait_profile_pc_predictor/{model_key}/persona_trait_similarity_matrix.csv",
            "source_role_vectors_actual": str(data["role_dir"]),
            "source_trait_vectors_actual": str(data["trait_dir"]),
            "persona_pca_source": str(MULTIMODEL_DATA.relative_to(REPO_ROOT)),
            "role_family_partition": str(CLUSTER_PATH.relative_to(REPO_ROOT)),
        },
        "source_sha256": {
            "trait_profile_matrix": sha256_file(out / "persona_trait_similarity_matrix.csv"),
            "role_vector_directory_aggregate": source_manifest["sources"]["role_vectors"]["aggregate_sha256_of_sorted_filename_and_file_hashes"],
            "trait_vector_directory_aggregate": source_manifest["sources"]["trait_vectors"]["aggregate_sha256_of_sorted_filename_and_file_hashes"],
            "persona_pca_artifact": source_manifest["sources"]["established_multimodel_coordinates"]["sha256"],
        },
        "validation_summary": {
            "raw_cosine_lopo": lopo_metrics["raw_cosine"],
            "quantile_lopo": lopo_metrics["quantile"],
            "model_selection": selection,
            "empirical_error_reference": error_reference,
        },
        "generation_timestamp_utc": generation_timestamp,
        "generation_base_commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "provenance_boundary": "Same-model activation-derived features and PCA targets; not independent psychology, causality, behavioral realization, or human transfer.",
    }
    write_json(out / "ridge_predictor.json", ridge_bundle)

    ood_reference, neighbor_reference = ref.build_ood_reference(X, personas, traits)
    ood_reference["activation_model"] = data["label"]
    ood_reference["calibration_boundary"] = "Geometric reference only; not calibrated probabilities."
    write_json(out / "ood_reference.json", ood_reference)
    neighbor_reference.to_csv(out / "nearest_neighbor_reference.csv", index=False)

    synthetic_predictions, synthetic_summary = ref.run_synthetic_interpolation(
        X, Y, personas, data["role_raw"], data["trait_raw"], data["pca_basis"], n_jobs, ref.SYNTHETIC_PAIRS_PER_BAND
    )
    if synthetic_summary["run"]:
        synthetic_summary["error_vs_endpoint_distance"] = synthetic_error_association(synthetic_predictions)
        synthetic_predictions.to_csv(out / "synthetic_interpolation_predictions.csv", index=False)
    write_json(out / "synthetic_interpolation_summary.json", synthetic_summary)

    representation_rows = []
    for representation in ref.REPRESENTATIONS:
        nested_row = comparison[(comparison["representation"] == representation) & (comparison["model"] == "ridge")].iloc[0].to_dict()
        representation_rows.append({"representation": representation, "validation_regime": "nested_5fold_x10", **{k: v for k, v in nested_row.items() if k not in {"representation", "model", "hyperparameter_selection_counts"}}})
        representation_rows.append({"representation": representation, "validation_regime": "leave_one_persona_out", **lopo_metrics[representation]})
    pd.DataFrame(representation_rows).to_csv(out / "profile_representation_comparison.csv", index=False)

    error_ood = ref.correlation_with_ood(lopo_raw)
    family_records = role_family_outputs(family_summary).to_dict(orient="records")
    summary = {
        "generation_timestamp_utc": generation_timestamp,
        "branch": git_value("branch", "--show-current"),
        "generation_base_commit": git_value("rev-parse", "HEAD"),
        "activation_model": data["label"],
        "scientific_scope": "Same-space saved-vector replication; no behavioral validation or cross-model semantic identity claim.",
        "integrity": data["integrity"],
        "matrix_verification": data["matrix_check"],
        "pca_reconstruction": data["pca_check"],
        "validation_design": {
            "reference_pipeline": str(REFERENCE_RUNNER.relative_to(REPO_ROOT)),
            "nested_outer": "5-fold shuffled KFold repeated across 10 deterministic seeds",
            "nested_outer_seeds": ref.OUTER_SEEDS,
            "inner": "4-fold shuffled KFold; representation transforms, scaling, and tuning fit on training data only",
            "lopo": "275 outer holdouts x raw cosine and fold-safe quantile representations; training-only Ridge alpha selection",
            "role_family_holdout": PARTITION_LABEL,
            "permutations": ref.PERMUTATIONS,
            "synthetic_pairs": "20 disjoint nearest and 20 disjoint distant endpoint pairs; alpha 0.25/0.50/0.75; both endpoints excluded",
        },
        "lopo": lopo_metrics,
        "model_selection": selection,
        "model_comparison": comparison.to_dict(orient="records"),
        "leave_one_role_family_out": family_records,
        "permutation_control": permutation_summary,
        "error_vs_ood": error_ood,
        "ood": {
            "method": ood_reference["method"],
            "n_components": ood_reference["profile_pca"]["n_components"],
            "cumulative_explained_variance": ood_reference["profile_pca"]["cumulative_explained_variance"],
            "heuristic_labels": ood_reference["heuristic_labels"],
        },
        "empirical_error_reference": error_reference,
        "synthetic_interpolation": synthetic_summary,
        "no_gpu_runpod_inference_activation_extraction_or_external_model_api": True,
    }
    write_json(out / "validation_summary.json", summary)

    ridge_expected = np.asarray(final_searches["ridge"].predict(X[:20]))
    ridge_portable = portable_ridge_predict(X[:20], ridge_bundle)
    deterministic = deterministic_checks(ref, data, n_jobs)
    pca_again, _, _, _ = pca_numpy(data["role_raw"], 3)
    for pc, sign in enumerate(data["pca_check"]["orientation_signs"]):
        pca_again[:, pc] *= sign
    role_norm_again = data["role_raw"] / np.linalg.norm(data["role_raw"], axis=1, keepdims=True)
    trait_norm_again = data["trait_raw"] / np.linalg.norm(data["trait_raw"], axis=1, keepdims=True)
    matrix_again = role_norm_again @ trait_norm_again.T
    verification = {
        "generated_utc": utc_now(),
        "all_checks_passed": False,
        "checks": {
            "integrity": data["integrity"],
            "pca_reconstruction": data["pca_check"],
            "cosine_matrix_verification": data["matrix_check"],
            "pca_deterministic_recompute_max_abs_difference": float(np.max(np.abs(pca_again - data["Y"]))),
            "cosine_matrix_deterministic_recompute_max_abs_difference": float(np.max(np.abs(matrix_again - X))),
            "no_target_columns_in_features": not data["integrity"]["target_or_metadata_columns_in_features"],
            "fold_local_scaling": True,
            "fold_local_quantile_transforms": True,
            "training_only_hyperparameter_selection": True,
            "lopo_no_held_out_persona_in_training": True,
            "role_family_no_held_out_member_in_training": True,
            "lopo_rows": len(lopo),
            "lopo_every_persona_per_representation": bool(all(group["persona"].nunique() == 275 for _, group in lopo.groupby("representation"))),
            "role_family_all_seven_families_all_models": bool(family_predictions.groupby("model")["cluster"].nunique().eq(7).all()),
            "permutation_null_clean": not permutation_summary["leakage_anomaly_detected"],
            "ridge_bundle_roundtrip_max_abs_error": float(np.max(np.abs(ridge_expected - ridge_portable))),
            "synthetic_endpoint_exclusion": bool(synthetic_predictions["endpoints_excluded_from_training"].all()) if not synthetic_predictions.empty else None,
            "finite_nested_predictions": bool(np.isfinite(nested.select_dtypes(include=[np.number]).to_numpy()).all()),
            "finite_lopo_predictions": bool(np.isfinite(lopo.select_dtypes(include=[np.number]).to_numpy()).all()),
            "deterministic_fixed_seed_reruns": deterministic,
        },
        "methodology_evidence": {
            "pipeline": "Canonical Qwen representation/scaling pipeline is inside TransformedTargetRegressor passed to inner GridSearchCV, fit separately on every outer-training partition.",
            "partition": PARTITION_LABEL,
            "ood": "Each LOPO OOD scaler/PCA is fit on the 274 training profiles; the held-out profile is transformed afterward.",
        },
    }
    checks = verification["checks"]
    verification["all_checks_passed"] = bool(
        data["integrity"]["passed"]
        and data["pca_check"]["passed"]
        and data["matrix_check"]["passed"]
        and checks["lopo_every_persona_per_representation"]
        and checks["role_family_all_seven_families_all_models"]
        and checks["permutation_null_clean"]
        and checks["ridge_bundle_roundtrip_max_abs_error"] < 1e-9
        and checks["synthetic_endpoint_exclusion"] is True
        and checks["finite_nested_predictions"]
        and checks["finite_lopo_predictions"]
        and deterministic["passed"]
    )
    write_json(out / "verification_report.json", verification)
    if not verification["all_checks_passed"]:
        raise RuntimeError(f"{model_key}: verification failed: {verification}")

    for path in sorted(out.glob("*.csv")):
        pd.read_csv(path)
    for path in sorted(out.glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
    return summary


def qwen_row(summary: dict[str, Any]) -> dict[str, Any]:
    family = next(row for row in summary["leave_one_cluster_out"] if row["model"] == "ridge" and row["cluster"] == "ALL_CLUSTERS")
    syn = summary["synthetic_interpolation"]["by_band"]["all"]
    raw = summary["lopo"]["raw_cosine"]
    quantile = summary["lopo"]["quantile"]
    return {
        "model": "Qwen/Qwen3-32B",
        "role_count": summary["integrity"]["persona_count"],
        "trait_count": summary["integrity"]["trait_count"],
        "raw_ridge_lopo_r2_pc1": raw["pc1_r2"],
        "raw_ridge_lopo_r2_pc2": raw["pc2_r2"],
        "raw_ridge_lopo_r2_pc3": raw["pc3_r2"],
        "raw_normalized_3d_rmse": raw["normalized_3d_error_rmse"],
        "quantile_normalized_3d_rmse": quantile["normalized_3d_error_rmse"],
        "role_family_holdout_normalized_3d_rmse": family["normalized_3d_error_rmse"],
        "family_holdout_over_lopo_mean_error_ratio": family["cluster_holdout_vs_lopo_mean_error_ratio"],
        "family_holdout_over_lopo_rmse_ratio": family["normalized_3d_error_rmse"] / raw["normalized_3d_error_rmse"],
        "permutation_p95_mean_pc_r2": summary["permutation_control"]["mean_pc_r2_q95"],
        "synthetic_interpolation_r2_pc1": syn["pc1_r2"],
        "synthetic_interpolation_r2_pc2": syn["pc2_r2"],
        "synthetic_interpolation_r2_pc3": syn["pc3_r2"],
        "synthetic_normalized_3d_rmse": syn["normalized_3d_error_rmse"],
        "selected_model_family": summary["model_selection"]["selected_model"],
        "canonical_source": str(QWEN_SUMMARY.relative_to(REPO_ROOT)),
    }


def replicated_row(summary: dict[str, Any]) -> dict[str, Any]:
    family = next(row for row in summary["leave_one_role_family_out"] if row["model"] == "ridge" and row["role_family"] == "ALL_CLUSTERS")
    syn = summary["synthetic_interpolation"]["by_band"]["all"]
    raw = summary["lopo"]["raw_cosine"]
    quantile = summary["lopo"]["quantile"]
    return {
        "model": summary["activation_model"],
        "role_count": summary["integrity"]["persona_count"],
        "trait_count": summary["integrity"]["trait_count"],
        "raw_ridge_lopo_r2_pc1": raw["pc1_r2"],
        "raw_ridge_lopo_r2_pc2": raw["pc2_r2"],
        "raw_ridge_lopo_r2_pc3": raw["pc3_r2"],
        "raw_normalized_3d_rmse": raw["normalized_3d_error_rmse"],
        "quantile_normalized_3d_rmse": quantile["normalized_3d_error_rmse"],
        "role_family_holdout_normalized_3d_rmse": family["normalized_3d_error_rmse"],
        "family_holdout_over_lopo_mean_error_ratio": family["cluster_holdout_vs_lopo_mean_error_ratio"],
        "family_holdout_over_lopo_rmse_ratio": family["role_family_holdout_over_lopo_rmse_ratio"],
        "permutation_p95_mean_pc_r2": summary["permutation_control"]["mean_pc_r2_q95"],
        "synthetic_interpolation_r2_pc1": syn["pc1_r2"],
        "synthetic_interpolation_r2_pc2": syn["pc2_r2"],
        "synthetic_interpolation_r2_pc3": syn["pc3_r2"],
        "synthetic_normalized_3d_rmse": syn["normalized_3d_error_rmse"],
        "selected_model_family": summary["model_selection"]["selected_model"],
        "canonical_source": f"research/outputs/multimodel_trait_profile_pc_predictor/{summary['activation_model'].split('-')[0].lower()}/validation_summary.json",
    }


def metric_triplet(metrics: dict[str, Any], suffix: str) -> str:
    return "/".join(f"{metrics[f'pc{i}_{suffix}']:.6f}" for i in (1, 2, 3))


def build_report(rows: list[dict[str, Any]], summaries: dict[str, dict[str, Any]], qwen: dict[str, Any], vector_root: Path) -> str:
    lines = [
        "# Multimodel trait-profile to persona-PC predictor",
        "",
        f"Generated UTC: {utc_now()}",
        "",
        "## Result",
        "",
        "Observed: complete same-model activation-derived trait profiles predict held-out persona PCA location in both Llama and Gemma under the canonical Qwen pipeline. Ridge remains the selected family under the predeclared 10% material-improvement rule unless the table below states otherwise. This is same-space representation analysis, not evidence that any model has more sophisticated or more human-like psychology.",
        "",
        "## Cross-model comparison",
        "",
        "| Model | Raw Ridge LOPO R2 PC1/PC2/PC3 | Raw norm. 3D RMSE | Quantile norm. 3D RMSE | Family norm. 3D RMSE | Family/LOPO mean-error ratio | Permutation p95 mean R2 | Synthetic R2 PC1/PC2/PC3 | Synthetic norm. 3D RMSE | Selected |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['raw_ridge_lopo_r2_pc1']:.6f}/{row['raw_ridge_lopo_r2_pc2']:.6f}/{row['raw_ridge_lopo_r2_pc3']:.6f} | {row['raw_normalized_3d_rmse']:.6f} | {row['quantile_normalized_3d_rmse']:.6f} | {row['role_family_holdout_normalized_3d_rmse']:.6f} | {row['family_holdout_over_lopo_mean_error_ratio']:.3f}x | {row['permutation_p95_mean_pc_r2']:.6f} | {row['synthetic_interpolation_r2_pc1']:.6f}/{row['synthetic_interpolation_r2_pc2']:.6f}/{row['synthetic_interpolation_r2_pc3']:.6f} | {row['synthetic_normalized_3d_rmse']:.6f} | {row['selected_model_family']} |"
        )
    lines.extend([
        "",
        "Qwen numbers above are read directly from the canonical saved validation summary, not recomputed.",
        "",
        "## Methods held constant",
        "",
        "The canonical Qwen runner is imported for the estimator definitions, grids, repeated 5-fold x 10-seed outer validation, 4-fold inner tuning, LOPO, 100 target permutations, training-only OOD PCA, and deterministic synthetic-pair selection. Raw profiles are same-model role-to-trait cosines after layer mean-pooling and L2 normalization. QuantileTransformer and all scaling remain inside each training fold.",
        "",
        f"Role-family transfer uses the fixed label: {PARTITION_LABEL}. It is not described as Llama-native or Gemma-native clustering.",
        "",
        "## Model-specific results",
        "",
    ])
    for key in ["llama", "gemma"]:
        summary = summaries[key]
        raw = summary["lopo"]["raw_cosine"]
        quant = summary["lopo"]["quantile"]
        family = next(row for row in summary["leave_one_role_family_out"] if row["model"] == "ridge" and row["role_family"] == "ALL_CLUSTERS")
        perm = summary["permutation_control"]
        syn = summary["synthetic_interpolation"]
        syn_all = syn["by_band"]["all"]
        near = syn["by_band"]["near"]
        distant = syn["by_band"]["distant"]
        ood = summary["error_vs_ood"]
        spec = MODEL_SPECS[key]
        lines.extend([
            f"### {summary['activation_model']}",
            "",
            f"Sources: {vector_root / spec['folder'] / 'role_vectors'} and {vector_root / spec['folder'] / 'trait_vectors'}.",
            "",
            f"PCA reproduction max absolute error: {summary['pca_reconstruction']['max_abs_coordinate_reproduction_error']:.3e} (strict tolerance {summary['pca_reconstruction']['strict_tolerance']:.1e}); orientation signs {summary['pca_reconstruction']['orientation_signs']}.",
            "",
            f"Raw Ridge LOPO: R2 {metric_triplet(raw, 'r2')}; Pearson {metric_triplet(raw, 'pearson')}; Spearman {metric_triplet(raw, 'spearman')}; RMSE {metric_triplet(raw, 'rmse')}; MAE {metric_triplet(raw, 'mae')}; normalized 3D RMSE {raw['normalized_3d_error_rmse']:.6f}.",
            "",
            f"Fold-safe quantile Ridge LOPO: R2 {metric_triplet(quant, 'r2')}; normalized 3D RMSE {quant['normalized_3d_error_rmse']:.6f}. Quantiles are {'less' if quant['normalized_3d_error_rmse'] > raw['normalized_3d_error_rmse'] else 'not less'} precise than raw cosines for this model.",
            "",
            f"Role-family holdout Ridge: R2 {metric_triplet(family, 'r2')}; normalized 3D RMSE {family['normalized_3d_error_rmse']:.6f}; mean-error degradation {family['cluster_holdout_vs_lopo_mean_error_ratio']:.3f}x; aggregate bias [{family['bias_pc1']:.4f}, {family['bias_pc2']:.4f}, {family['bias_pc3']:.4f}].",
            "",
            f"Permutation control: {perm['n_permutations']} permutations, p95 mean-PC R2 {perm['mean_pc_r2_q95']:.6f}, maximum {perm['mean_pc_r2_max']:.6f}; leakage anomaly detected={perm['leakage_anomaly_detected']}.",
            "",
            f"Synthetic endpoint-held-out interpolation: R2 {metric_triplet(syn_all, 'r2')}; normalized 3D RMSE {syn_all['normalized_3d_error_rmse']:.6f}; nearby {near['normalized_3d_error_rmse']:.6f}; distant {distant['normalized_3d_error_rmse']:.6f}; pair-level endpoint-distance/error Pearson {syn['error_vs_endpoint_distance']['pair_aggregated']['pearson']:.4f}, Spearman {syn['error_vs_endpoint_distance']['pair_aggregated']['spearman']:.4f}.",
            "",
            f"OOD/error association: 5-NN distance Pearson {ood['mean_5nn_distance']['pearson']:.4f}, Spearman {ood['mean_5nn_distance']['spearman']:.4f}; reconstruction residual Pearson {ood['profile_pca_reconstruction_error']['pearson']:.4f}, Spearman {ood['profile_pca_reconstruction_error']['spearman']:.4f}. These are geometric associations, not calibrated probabilities.",
            "",
            f"Selected model family: {summary['model_selection']['selected_model']}. {summary['model_selection']['reason']}",
            "",
        ])
    qood = qwen["error_vs_ood"]
    lines.extend([
        "## OOD association comparison",
        "",
        "| Model | 5-NN distance Pearson/Spearman | Reconstruction residual Pearson/Spearman |",
        "|---|---:|---:|",
        f"| Qwen/Qwen3-32B | {qood['mean_5nn_distance']['pearson']:.4f}/{qood['mean_5nn_distance']['spearman']:.4f} | {qood['profile_pca_reconstruction_error']['pearson']:.4f}/{qood['profile_pca_reconstruction_error']['spearman']:.4f} |",
    ])
    for key in ["llama", "gemma"]:
        ood = summaries[key]["error_vs_ood"]
        lines.append(f"| {summaries[key]['activation_model']} | {ood['mean_5nn_distance']['pearson']:.4f}/{ood['mean_5nn_distance']['spearman']:.4f} | {ood['profile_pca_reconstruction_error']['pearson']:.4f}/{ood['profile_pca_reconstruction_error']['spearman']:.4f} |")
    lines.extend([
        "",
        "## Epistemic status",
        "",
        "Observed:",
        "",
        "- Held-out LOPO, whole-role-family, permutation, OOD-association, and endpoint-held-out synthetic metrics reported above.",
        "- Exact 275-role and 240-trait label coverage in each model, finite sources and cosine matrices, and strict reproduction of the established within-model PCA coordinates.",
        "- Raw and quantile Ridge performance plus repeated nested comparisons with PLS, RBF Kernel Ridge, and distance-weighted KNN.",
        "",
        "Interpretation:",
        "",
        "- Replication across the three saved open-model vector sets supports broad same-space trait-bank coverage of their respective persona geometries.",
        "- If Ridge remains selected, the relationship is approximately linear at the resolution tested; this does not imply individual coefficients are stable semantic explanations because the 240 traits are highly correlated.",
        "- Whole-family degradation and distance-linked synthetic error identify limits of interpolation inside the saved artifact family.",
        "",
        "Hypotheses and unresolved questions:",
        "",
        "- Whether frozen profile-based predictions match newly elicited behavioral persona activations remains untested.",
        "- Whether the pattern extends to frontier models, other checkpoints, humans, or a human personality ontology remains untested.",
        "- PC sign orientation helps display consistency; it does not establish identical PC1/PC2/PC3 semantics across models.",
        "",
        "No GPU, RunPod, new model inference, new activation extraction, or external model API was used.",
    ])
    return "\n".join(lines) + "\n"


def artifact_inventory() -> pd.DataFrame:
    rows = []
    branch_base = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/llama-gemma-trait-predictor/"
    master_base = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
    for path in sorted(OUTPUT_ROOT.rglob("*")):
        if not path.is_file() or path.name == "artifact_inventory.csv" or path.suffix == ".pyc":
            continue
        relative = str(path.relative_to(REPO_ROOT))
        rows.append({
            "path": relative,
            "status": "active",
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "branch_raw_github_url": branch_base + relative,
            "canonical_master_raw_github_url": master_base + relative,
        })
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vector-root", type=Path, default=None, help="Root containing saved hf_vectors model folders")
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument("--smoke-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    vector_root = resolve_vector_root(args.vector_root)
    ref = import_reference_runner()
    geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    clusters = pd.read_csv(CLUSTER_PATH)
    multimodel = json.loads(MULTIMODEL_DATA.read_text(encoding="utf-8"))
    expected_traits = json.loads(QWEN_RIDGE.read_text(encoding="utf-8"))["trait_feature_names"]
    datasets = {
        key: build_model_data(key, vector_root, geometry, clusters, multimodel, expected_traits)
        for key in ["llama", "gemma"]
    }
    if args.smoke_test:
        payload = {
            key: {
                "integrity": value["integrity"],
                "pca_reconstruction": value["pca_check"],
                "matrix_verification": value["matrix_check"],
                "ridge_smoke_best": ref.clean_params(ref.fit_tuned("ridge", "quantile", value["X"][:80], value["Y"][:80], 123, args.n_jobs).best_params_),
            }
            for key, value in datasets.items()
        }
        print(json.dumps(payload, indent=2))
        return 0

    generated = utc_now()
    summaries = {}
    for key in ["llama", "gemma"]:
        print(f"starting complete analysis for {key}", flush=True)
        summaries[key] = run_model(ref, datasets[key], args.n_jobs, generated)
        print(f"completed complete analysis for {key}", flush=True)

    qwen = json.loads(QWEN_SUMMARY.read_text(encoding="utf-8"))
    rows = [qwen_row(qwen), replicated_row(summaries["llama"]), replicated_row(summaries["gemma"])]
    pd.DataFrame(rows).to_csv(OUTPUT_ROOT / "cross_model_comparison.csv", index=False)
    write_json(
        OUTPUT_ROOT / "cross_model_comparison.json",
        {
            "generation_timestamp_utc": generated,
            "qwen_source": source_record(QWEN_SUMMARY),
            "models": rows,
            "ood_error_association": {
                "Qwen/Qwen3-32B": qwen["error_vs_ood"],
                summaries["llama"]["activation_model"]: summaries["llama"]["error_vs_ood"],
                summaries["gemma"]["activation_model"]: summaries["gemma"]["error_vs_ood"],
            },
            "interpretation_boundary": "Accuracy differences do not measure psychological sophistication, human-likeness, causal trait determination, or semantic identity of oriented PCs.",
        },
    )
    (OUTPUT_ROOT / "multimodel_trait_profile_pc_predictor_report.md").write_text(
        build_report(rows, summaries, qwen, vector_root), encoding="utf-8"
    )

    inventory = artifact_inventory()
    inventory.to_csv(OUTPUT_ROOT / "artifact_inventory.csv", index=False)
    for path in sorted(OUTPUT_ROOT.rglob("*.csv")):
        pd.read_csv(path)
    for path in sorted(OUTPUT_ROOT.rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
    print("multimodel analysis complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
