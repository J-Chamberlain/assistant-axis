#!/usr/bin/env python3
"""Shared released-vector loader for the multimodel trait viewers.

The coordinate functions are imported from the established multimodel ordered
trait-region generator.  This module deliberately does not define a second PCA
or orientation procedure.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch
from scipy.stats import rankdata


MODEL_SPECS = {
    "qwen": {
        "label": "Qwen/Qwen3-32B",
        "short_label": "Qwen",
        "folder": "qwen-3-32b",
    },
    "llama": {
        "label": "Llama-3.3-70B",
        "short_label": "Llama",
        "folder": "llama-3.3-70b",
    },
    "gemma": {
        "label": "Gemma-2-27B",
        "short_label": "Gemma",
        "folder": "gemma-2-27b",
    },
}
MODEL_ORDER = list(MODEL_SPECS)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_sha256(directory: Path) -> str:
    """Hash relative names and contents so a vector directory is auditable."""
    digest = hashlib.sha256()
    for path in sorted(directory.glob("*.pt")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def resolve_vector_root(repo: Path, requested: str | Path | None) -> Path:
    candidate = requested or os.environ.get("ASSISTANT_AXIS_VECTOR_ROOT")
    root = Path(candidate).expanduser().resolve() if candidate else repo / "downloads/hf_vectors"
    missing = []
    for spec in MODEL_SPECS.values():
        for kind in ("role_vectors", "trait_vectors"):
            path = root / spec["folder"] / kind
            if not path.is_dir():
                missing.append(str(path))
    if missing:
        raise FileNotFoundError(
            "Required local released-vector bundles are absent; no download or "
            "substitution was attempted:\n" + "\n".join(missing)
        )
    return root


def _established_module(repo: Path):
    path = repo / (
        "research/outputs/multimodel_ordered_trait_region_viewer/"
        "run_multimodel_ordered_trait_region_viewer.py"
    )
    spec = importlib.util.spec_from_file_location("established_multimodel_trait_regions", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load established coordinate generator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def _reference_geometry(repo: Path) -> tuple[list[str], np.ndarray]:
    path = repo / "research/visualizations/geometry_viz_data.json"
    geometry = json.loads(path.read_text())["roles"]
    names = list(geometry["names"])
    coordinates = np.asarray(geometry["pca3d"], dtype=np.float64)
    if len(names) != len(set(names)) or coordinates.shape != (275, 3):
        raise ValueError("Canonical Qwen geometry must contain 275 unique roles and three PCs")
    if not np.isfinite(coordinates).all():
        raise ValueError("Canonical Qwen coordinates contain non-finite values")
    return names, coordinates


def _established_coordinates(repo: Path) -> dict[str, dict[str, list[float]]]:
    path = repo / (
        "research/outputs/multimodel_ordered_trait_region_viewer/"
        "multimodel_ordered_trait_region_data.json"
    )
    data = json.loads(path.read_text())
    return {
        model: {
            point["persona"]: [point["pc1"], point["pc2"], point["pc3"]]
            for point in payload["points"]
        }
        for model, payload in data["models"].items()
    }


def _qwen_primary_matrix(repo: Path) -> tuple[list[str], dict[str, dict[str, str]], Path]:
    path = repo / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 275 or not rows:
        raise ValueError("Canonical Qwen trait matrix must contain 275 persona rows")
    traits = [key for key in rows[0] if key != "persona"]
    if len(traits) != 240 or len(set(traits)) != 240:
        raise ValueError("Canonical Qwen trait matrix must contain 240 unique traits")
    return traits, {row["persona"]: row for row in rows}, path


def _midrank_percentiles(raw: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [100 * (rankdata(raw[:, column], method="average") - 0.5) / len(raw)
         for column in range(raw.shape[1])]
    )


def load_multimodel_traits(
    repo: Path,
    vector_root: str | Path | None,
    selected_traits: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Load three exact model datasets with one established coordinate convention."""
    repo = repo.resolve()
    vector_root = resolve_vector_root(repo, vector_root)
    established, established_script = _established_module(repo)
    reference_names, reference_coordinates = _reference_geometry(repo)
    reference = {name: reference_coordinates[i].tolist() for i, name in enumerate(reference_names)}
    saved_coordinates = _established_coordinates(repo)
    qwen_traits, qwen_rows, qwen_matrix_path = _qwen_primary_matrix(repo)

    if len(selected_traits) != len(set(selected_traits)):
        raise ValueError("Displayed trait keys must be unique")
    if not set(selected_traits) <= set(qwen_traits):
        raise ValueError("Displayed trait keys are missing from the canonical Qwen matrix")

    models: dict[str, dict[str, Any]] = {}
    role_sets: dict[str, set[str]] = {}
    trait_sets: dict[str, set[str]] = {}
    for model_key, model_spec in MODEL_SPECS.items():
        model_root = vector_root / model_spec["folder"]
        role_dir = model_root / "role_vectors"
        trait_dir = model_root / "trait_vectors"
        role_names, role_vectors = established.load_mean_vectors(role_dir)
        trait_names, trait_vectors = established.load_mean_vectors(trait_dir)
        role_sets[model_key] = set(role_names)
        trait_sets[model_key] = set(trait_names)
        if not (len(role_names) == len(set(role_names)) == 275):
            raise ValueError(f"{model_key}: role-vector names are not exactly 275 unique roles")
        if not (len(trait_names) == len(set(trait_names)) == 240):
            raise ValueError(f"{model_key}: trait-vector names are not exactly 240 unique traits")
        if set(role_names) != set(reference_names):
            missing = sorted(set(reference_names) - set(role_names))
            extra = sorted(set(role_names) - set(reference_names))
            raise ValueError(f"{model_key}: role set differs from Qwen geometry; missing={missing[:5]} extra={extra[:5]}")
        if set(trait_names) != set(qwen_traits):
            missing = sorted(set(qwen_traits) - set(trait_names))
            extra = sorted(set(trait_names) - set(qwen_traits))
            raise ValueError(f"{model_key}: trait set differs; missing={missing[:5]} extra={extra[:5]}")

        role_by_name = {name: role_vectors[i] for i, name in enumerate(role_names)}
        trait_by_name = {name: trait_vectors[i] for i, name in enumerate(trait_names)}
        sorted_roles = sorted(role_names)
        sorted_traits = sorted(trait_names)
        role_matrix = np.stack([role_by_name[name] for name in sorted_roles])
        trait_matrix = np.stack([trait_by_name[name] for name in sorted_traits])

        if model_key == "qwen":
            sorted_coordinates = np.asarray([reference[name] for name in sorted_roles], dtype=np.float64)
            explained = [None, None, None]
            orientation_signs = [1, 1, 1]
            coordinate_source = "canonical_geometry_viz_data"
        else:
            sorted_coordinates, _, explained_array = established.pca_numpy(role_matrix, 3)
            orientation_signs = established.orient_to_reference(sorted_roles, sorted_coordinates, reference)
            explained = [float(value) for value in explained_array]
            coordinate_source = "recomputed_layer_mean_role_vector_pca_oriented_to_qwen_reference"

        coordinates_by_name = {
            name: sorted_coordinates[index].tolist() for index, name in enumerate(sorted_roles)
        }
        coordinates = np.asarray([coordinates_by_name[name] for name in reference_names], dtype=np.float64)
        established_max_coordinate_difference = max(
            abs(coordinates_by_name[name][axis] - saved_coordinates[model_key][name][axis])
            for name in sorted_roles for axis in range(3)
        )
        if established_max_coordinate_difference > 1e-10:
            raise ValueError(
                f"{model_key}: coordinate mismatch against established viewer: "
                f"{established_max_coordinate_difference}"
            )

        role_tensor = established.normalize_rows(torch.from_numpy(role_matrix).float())
        trait_tensor = established.normalize_rows(torch.from_numpy(trait_matrix).float())
        established_similarity = torch.mm(role_tensor, trait_tensor.T).numpy().astype(float)
        established_similarity_by_name = {
            name: established_similarity[index] for index, name in enumerate(sorted_roles)
        }
        trait_index = {name: index for index, name in enumerate(sorted_traits)}
        selected_established = np.asarray([
            [established_similarity_by_name[name][trait_index[trait]] for trait in selected_traits]
            for name in reference_names
        ], dtype=np.float64)

        if model_key == "qwen":
            raw = np.asarray([
                [float(qwen_rows[name][trait]) for trait in selected_traits]
                for name in reference_names
            ], dtype=np.float64)
            qwen_recompute_max_difference = float(np.max(np.abs(raw - selected_established)))
            score_source = "canonical_saved_qwen_persona_trait_similarity_matrix"
        else:
            raw = selected_established
            qwen_recompute_max_difference = None
            score_source = "established_multimodel_float32_activation_cosine_recomputation"

        if not np.isfinite(raw).all() or np.any(np.abs(raw) > 1 + 1e-6):
            raise ValueError(f"{model_key}: invalid activation-cosine values")
        z_score = (raw - raw.mean(axis=0)) / raw.std(axis=0, ddof=0)
        height_percentile = _midrank_percentiles(raw)
        orders = [
            sorted(range(len(reference_names)), key=lambda i: (-coordinates[i, axis], reference_names[i]))
            for axis in range(3)
        ]
        models[model_key] = {
            "key": model_key,
            "label": model_spec["label"],
            "short_label": model_spec["short_label"],
            "folder": model_spec["folder"],
            "coordinate_source": coordinate_source,
            "orientation_signs": orientation_signs,
            "pca_explained_variance": explained,
            "source_role_count": len(role_names),
            "source_trait_count": len(trait_names),
            "displayed_trait_count": len(selected_traits),
            "personas": reference_names,
            "coordinates": coordinates.tolist(),
            "raw_affinity": raw.tolist(),
            "z_score": z_score.tolist(),
            "height_percentile": height_percentile.tolist(),
            "orders": orders,
            "score_source": score_source,
            "vector_sources": {
                "role_vectors": f"downloads/hf_vectors/{model_spec['folder']}/role_vectors",
                "trait_vectors": f"downloads/hf_vectors/{model_spec['folder']}/trait_vectors",
                "role_bundle_sha256": bundle_sha256(role_dir),
                "trait_bundle_sha256": bundle_sha256(trait_dir),
            },
            "established_coordinate_max_abs_difference": float(established_max_coordinate_difference),
            "qwen_vector_recompute_vs_canonical_matrix_max_abs_difference": qwen_recompute_max_difference,
        }

    if len({frozenset(values) for values in role_sets.values()}) != 1:
        raise ValueError("Role-name sets are not identical across models")
    if len({frozenset(values) for values in trait_sets.values()}) != 1:
        raise ValueError("Trait-name sets are not identical across models")
    audit = {
        "vector_root_resolved": str(vector_root),
        "logical_vector_root": "downloads/hf_vectors",
        "established_coordinate_script": str(established_script.relative_to(repo)),
        "established_coordinate_data": (
            "research/outputs/multimodel_ordered_trait_region_viewer/"
            "multimodel_ordered_trait_region_data.json"
        ),
        "canonical_qwen_matrix": str(qwen_matrix_path.relative_to(repo)),
        "canonical_geometry": "research/visualizations/geometry_viz_data.json",
        "role_sets_identical": True,
        "trait_sets_identical": True,
        "cross_model_normalization": (
            "Each displayed trait is midrank-percentiled independently within the selected "
            "model's 275-persona distribution. Equal percentile does not imply equal cosine "
            "or identical psychological semantics across models."
        ),
        "coordinate_orientation": (
            "Qwen uses canonical geometry_viz_data coordinates. Llama and Gemma use PCA "
            "over their own layer-mean role vectors, with each PC sign oriented to the "
            "corresponding Qwen reference PC exactly as in the established ordered-trait viewer."
        ),
    }
    return models, audit
