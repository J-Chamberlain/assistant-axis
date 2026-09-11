#!/usr/bin/env python3
"""Build a self-contained three-model viewer of five editorial trait groups."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import plotly
from plotly.offline import get_plotlyjs
from scipy.interpolate import RBFInterpolator
from scipy.spatial import Delaunay, cKDTree


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RIDGES = ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json"
SMOOTHING = [("Detail", 0.003), ("Balanced", 0.03), ("Gentle", 0.3)]
MODEL_ORDER = ["qwen", "llama", "gemma"]
QWEN_REFERENCE_COMMIT = "d68921b898ed179194223f449149d715298cdabe"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, allow_nan=False, indent=2) + "\n")


def save_csv(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_groups(model_key: str, ridge_data: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    model = ridge_data["models"][model_key]
    categories = ridge_data["categories"]
    names = model["personas"]
    coordinates = model["coordinates"]
    if len(names) != len(set(names)) or len(names) != 275:
        raise ValueError(f"{model_key}: expected 275 unique personas")
    if len(categories) != 15:
        raise ValueError("Expected the unchanged 15 displayed traits")
    percentile, z_score, raw = [
        np.asarray(model[key], dtype=np.float64)
        for key in ["height_percentile", "z_score", "raw_affinity"]
    ]
    if percentile.shape != z_score.shape or z_score.shape != raw.shape or raw.shape != (275, 15):
        raise ValueError(f"{model_key}: unexpected ridge matrix shapes")
    if not np.isfinite(percentile).all() or np.any((percentile < 0) | (percentile > 100)):
        raise ValueError(f"{model_key}: invalid percentiles")

    groups: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    for label in dict.fromkeys(category["group"] for category in categories):
        indices = [index for index, category in enumerate(categories) if category["group"] == label]
        if len(indices) != 3:
            raise ValueError(f"{label}: expected exactly three editorial members")
        members = [
            {
                "key": categories[index]["trait"],
                "label": categories[index]["trait"].capitalize(),
                "percentile": percentile[:, index].tolist(),
                "raw": raw[:, index].tolist(),
                "z": z_score[:, index].tolist(),
            }
            for index in indices
        ]
        mean = percentile[:, indices].mean(axis=1)
        if abs(mean.mean() - 50) >= 1e-10:
            raise ValueError(f"{model_key}/{label}: expected population group mean of 50")
        groups.append(
            {
                "key": label.lower(),
                "label": label,
                "values": mean.tolist(),
                "mean_z": z_score[:, indices].mean(axis=1).tolist(),
                "members": members,
            }
        )
        for persona_index, name in enumerate(names):
            row: dict[str, object] = {
                "model": model_key,
                "model_label": model["label"],
                "persona": name,
                "group": label,
                "group_mean_trait_percentile": float(mean[persona_index]),
                "group_mean_trait_z": float(z_score[persona_index, indices].mean()),
                "pc1": coordinates[persona_index][0],
                "pc2": coordinates[persona_index][1],
                "pc3": coordinates[persona_index][2],
            }
            for member_index, category_index in enumerate(indices, 1):
                row.update(
                    {
                        f"trait_{member_index}": categories[category_index]["trait"],
                        f"percentile_{member_index}": float(percentile[persona_index, category_index]),
                        f"raw_cosine_{member_index}": float(raw[persona_index, category_index]),
                        f"z_{member_index}": float(z_score[persona_index, category_index]),
                    }
                )
            rows.append(row)
    if len(groups) != 5 or len(rows) != 1375:
        raise ValueError(f"{model_key}: expected five groups and 1,375 rows")
    roles = [{"name": name, "pcs": pc} for name, pc in zip(names, coordinates)]
    return roles, groups, rows


def make_meshes(
    roles: list[dict[str, object]], groups: list[dict[str, object]], model_key: str
) -> tuple[dict[str, object], list[dict[str, object]]]:
    coordinates = np.asarray([role["pcs"] for role in roles], dtype=np.float64)
    scores = np.asarray([group["values"] for group in groups], dtype=np.float64).T
    views: dict[str, object] = {}
    diagnostics: list[dict[str, object]] = []
    for axes in itertools.combinations(range(3), 2):
        xy = coordinates[:, axes]
        center = xy.mean(axis=0)
        scale = float(np.sqrt(np.mean(np.var(xy, axis=0))))
        points = (xy - center) / scale
        unique, inverse = np.unique(points, axis=0, return_inverse=True)
        targets = np.stack([scores[inverse == index].mean(axis=0) for index in range(len(unique))])
        tree = cKDTree(unique)
        distances, _ = tree.query(unique, k=6)
        radius = float(np.quantile(distances[:, -1], 0.9))
        x = np.linspace(xy[:, 0].min(), xy[:, 0].max(), 61)
        y = np.linspace(xy[:, 1].min(), xy[:, 1].max(), 61)
        xx, yy = np.meshgrid(x, y)
        grid = (np.column_stack([xx.ravel(), yy.ravel()]) - center) / scale
        sixth, _ = tree.query(grid, k=6)
        supported = ((Delaunay(unique).find_simplex(grid) >= 0) & (sixth[:, -1] <= radius)).reshape(61, 61)
        node_basis = np.column_stack([np.ones(len(points)), points])
        grid_basis = np.column_stack([np.ones(len(grid)), grid])
        flat_grid_arrays: list[np.ndarray] = []
        flat_plane: list[dict[str, object]] = []
        for group_index in range(len(groups)):
            coefficients = np.linalg.lstsq(node_basis, scores[:, group_index], rcond=None)[0]
            flat_nodes_raw = node_basis @ coefficients
            flat_grid_raw = (grid_basis @ coefficients).reshape(61, 61)
            node_sst = float(np.sum((scores[:, group_index] - scores[:, group_index].mean()) ** 2))
            node_sse = float(np.sum((scores[:, group_index] - flat_nodes_raw) ** 2))
            node_r2 = None if node_sst < 1e-12 else float(1 - node_sse / node_sst)
            flat_grid_arrays.append(np.clip(flat_grid_raw, 0, 100))
            flat_plane.append(
                {
                    "coefficients": coefficients.tolist(),
                    "node_rmse": float(np.sqrt(np.mean((scores[:, group_index] - flat_nodes_raw) ** 2))),
                    "node_r2": node_r2,
                }
            )
        flat_grids = [
            [
                [round(float(value), 6) if ok else None for value, ok in zip(row, supported_row)]
                for row, supported_row in zip(flat_grid, supported)
            ]
            for flat_grid in flat_grid_arrays
        ]
        levels: list[dict[str, object]] = []
        for label, smoothing in SMOOTHING:
            fit = RBFInterpolator(
                unique, targets, kernel="thin_plate_spline", smoothing=smoothing, degree=1
            )
            original = fit(grid).reshape(61, 61, 5)
            fitted_original = fit(points)
            if not np.isfinite(original).all() or not np.isfinite(fitted_original).all():
                raise ValueError(f"{model_key}/{axes}/{label}: non-finite surface fit")
            values = np.clip(original, 0, 100)
            fitted = np.clip(fitted_original, 0, 100)
            rmse = np.sqrt(np.mean((fitted - scores) ** 2, axis=0))
            grids: list[list[list[float | None]]] = []
            flat_adherence: list[dict[str, float | None]] = []
            for group_index in range(len(groups)):
                grids.append(
                    [
                        [round(float(value), 6) if ok else None for value, ok in zip(row, mask)]
                        for row, mask in zip(values[:, :, group_index], supported)
                    ]
                )
                displayed = original[:, :, group_index][supported]
                rolling = values[:, :, group_index][supported]
                flat = flat_grid_arrays[group_index][supported]
                flat_sse = float(np.sum((rolling - flat) ** 2))
                rolling_sst = float(np.sum((rolling - rolling.mean()) ** 2))
                flat_r2 = None if rolling_sst < 1e-12 else float(1 - flat_sse / rolling_sst)
                flat_score = None if flat_r2 is None else float(np.clip(100 * flat_r2, 0, 100))
                flat_adherence.append(
                    {
                        "fabric_flat_rmse": float(np.sqrt(np.mean((rolling - flat) ** 2))),
                        "fabric_flat_r2": flat_r2,
                        "fabric_flat_score": flat_score,
                    }
                )
                diagnostics.append(
                    {
                        "model": model_key,
                        "x_axis": axes[0] + 1,
                        "y_axis": axes[1] + 1,
                        "group": groups[group_index]["label"],
                        "smoothing_label": label,
                        "smoothing": smoothing,
                        "fit_rmse_percentile_points": float(rmse[group_index]),
                        "support_fraction": float(supported.mean()),
                        "supported_cells": int(supported.sum()),
                        "clipped_supported_cells": int(((displayed < 0) | (displayed > 100)).sum()),
                        "fitted_nodes_clipped": int(
                            ((fitted_original[:, group_index] < 0) | (fitted_original[:, group_index] > 100)).sum()
                        ),
                        "unclipped_supported_min": float(displayed.min()),
                        "unclipped_supported_max": float(displayed.max()),
                        "maximum_node_fabric_gap": float(
                            np.max(np.abs(fitted[:, group_index] - scores[:, group_index]))
                        ),
                        "flat_plane_node_rmse": flat_plane[group_index]["node_rmse"],
                        "flat_plane_node_r2": flat_plane[group_index]["node_r2"],
                        "fabric_flat_rmse": flat_adherence[-1]["fabric_flat_rmse"],
                        "fabric_flat_r2": flat_r2,
                        "fabric_flat_score": flat_score,
                    }
                )
            levels.append(
                {
                    "label": label,
                    "smoothing": smoothing,
                    "grids": grids,
                    "fitted_nodes": fitted.T.tolist(),
                    "fit_rmse": rmse.tolist(),
                    "flat_adherence": flat_adherence,
                }
            )
        views[f"{axes[0]}_{axes[1]}"] = {
            "axes": list(axes),
            "x": x.tolist(),
            "y": y.tolist(),
            "levels": levels,
            "fit_center": center.tolist(),
            "fit_common_scale": scale,
            "support_sixth_neighbor_radius": radius,
            "supported_grid_fraction": float(supported.mean()),
            "flat_grids": flat_grids,
            "flat_plane": flat_plane,
        }
    return views, diagnostics


def build_html(data: dict[str, object]) -> None:
    text = (HERE / "viewer_template.html").read_text()
    replacements = {
        "__BOOTSTRAP_JS__": (HERE / "viewer_bootstrap.js").read_text(),
        "__PLOTLY_LIBRARY__": get_plotlyjs(),
        "__VIEWER_DATA__": json.dumps(data, separators=(",", ":"), allow_nan=False).replace("</", "<\\/"),
        "__CAMERA_JS__": (HERE / "camera_controls.js").read_text(),
        "__VIEWER_JS__": (HERE / "viewer.js").read_text(),
    }
    for token, value in replacements.items():
        if text.count(token) != 1:
            raise ValueError(f"Expected one template token: {token}")
        text = text.replace(token, value)
    if any(token in text for token in replacements):
        raise ValueError("Unreplaced viewer template token")
    (HERE / "persona_trait_surface_viewer.html").write_text(text)


def git_json(commit: str, path: str) -> dict[str, object]:
    content = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)
    return json.loads(content)


def recursive_max_difference(current: object, previous: object, path: str = "") -> tuple[float, str]:
    if isinstance(current, dict) and isinstance(previous, dict):
        if current.keys() != previous.keys():
            raise ValueError(f"Qwen compatibility key mismatch at {path}")
        candidates = [recursive_max_difference(current[key], previous[key], f"{path}/{key}") for key in current]
        return max(candidates, default=(0.0, path), key=lambda pair: pair[0])
    if isinstance(current, list) and isinstance(previous, list):
        if len(current) != len(previous):
            raise ValueError(f"Qwen compatibility length mismatch at {path}")
        candidates = [
            recursive_max_difference(value, old, f"{path}/{index}")
            for index, (value, old) in enumerate(zip(current, previous))
        ]
        return max(candidates, default=(0.0, path), key=lambda pair: pair[0])
    if isinstance(current, (int, float)) and not isinstance(current, bool):
        difference = abs(float(current) - float(previous))
        return difference, path
    if current != previous:
        raise ValueError(f"Qwen compatibility value mismatch at {path}: {current!r} != {previous!r}")
    return 0.0, path


def inventory() -> None:
    files = sorted(path for path in HERE.iterdir() if path.is_file() and path.name != "artifact_inventory.csv")
    save_csv(
        "artifact_inventory.csv",
        [
            {
                "path": str(path.relative_to(ROOT)),
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
                "raw_github_url": (
                    "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
                    + str(path.relative_to(ROOT))
                ),
            }
            for path in files
        ],
    )


def main(qwen_reference_commit: str) -> None:
    ridge_data = json.loads(RIDGES.read_text())
    models: dict[str, object] = {}
    rows: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for model_key in MODEL_ORDER:
        roles, groups, model_rows = load_groups(model_key, ridge_data)
        views, model_diagnostics = make_meshes(roles, groups, model_key)
        ridge_model = ridge_data["models"][model_key]
        models[model_key] = {
            "key": model_key,
            "label": ridge_model["label"],
            "short_label": ridge_model["short_label"],
            "coordinate_source": ridge_model["coordinate_source"],
            "orientation_signs": ridge_model["orientation_signs"],
            "roles": roles,
            "categories": groups,
            "views": views,
            "height_range": [0, 100],
            "aggregation": "Equal-weight mean of three within-model trait midrank percentiles",
            "caveat": "Editorial same-space trait-cosine summaries, not independently validated factors or probabilities",
        }
        rows.extend(model_rows)
        diagnostics.extend(model_diagnostics)

    old_qwen = git_json(
        qwen_reference_commit,
        "research/outputs/persona_trait_surface_viewer/persona_trait_surface_data.json",
    )
    current_qwen_science = {
        key: models["qwen"][key]
        for key in ["roles", "categories", "views", "height_range", "aggregation", "caveat"]
    }
    # Original wording is retained exactly for the compatibility comparison.
    current_qwen_science["aggregation"] = "Equal-weight mean of three within-trait midrank percentiles from the ridge plots"
    current_qwen_science["caveat"] = "Editorial same-space trait-cosine summaries, not independently validated factors or probabilities"
    qwen_max_difference, qwen_max_path = recursive_max_difference(current_qwen_science, old_qwen)
    if qwen_max_difference != 0:
        raise ValueError(
            f"Qwen surface compatibility drift at {qwen_max_path}: {qwen_max_difference}"
        )

    data = {
        "schema_version": 2,
        "default_model": "qwen",
        "model_order": MODEL_ORDER,
        "models": models,
        "height_range": [0, 100],
        "aggregation": "Equal-weight mean of three member-trait within-model percentiles",
        "scientific_label": "same-space activation-cosine trait profiles",
        "cross_model_caveat": (
            "Percentiles are within-model ranks. Equal percentiles do not imply equal absolute cosine "
            "or identical psychological semantics across models."
        ),
    }
    save_csv("persona_trait_group_scores.csv", rows)
    save_csv("trait_surface_fit_diagnostics.csv", diagnostics)
    save_json("persona_trait_surface_data.json", data)
    build_html(data)

    source_paths = [
        RIDGES,
        ROOT / "research/outputs/persona_trait_ridge_plots/trait_category_order.csv",
        ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_manifest.json",
        ROOT / "research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md",
        ROOT / "research/outputs/multimodel_trait_viewer_data.py",
        ROOT / (
            "research/outputs/multimodel_ordered_trait_region_viewer/"
            "run_multimodel_ordered_trait_region_viewer.py"
        ),
        ROOT / (
            "research/outputs/multimodel_ordered_trait_region_viewer/"
            "multimodel_ordered_trait_region_data.json"
        ),
        HERE / "run_persona_trait_surface.py",
        HERE / "viewer.js",
        HERE / "camera_controls.js",
        HERE / "viewer_template.html",
        HERE / "viewer_bootstrap.js",
        HERE / "trait_surface_methodology.md",
        HERE / "verify_trait_surface_data.py",
        HERE / "verify_trait_surface_controls.cjs",
        HERE / "verify_trait_viewers_browser.cjs",
        HERE / "render_trait_surface_preview.cjs",
    ]
    ridge_manifest = json.loads(
        (ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_manifest.json").read_text()
    )
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
        "qwen_compatibility_reference_commit": qwen_reference_commit,
        "author": "Codex / GPT-5.5",
        "default_model": "qwen",
        "models": {
            key: {
                "label": models[key]["label"],
                "personas": 275,
                "source_traits": 240,
                "member_traits": 15,
                "groups": 5,
                "group_rows": 1375,
                "coordinate_source": models[key]["coordinate_source"],
                "orientation_signs": models[key]["orientation_signs"],
                "vector_sources": ridge_manifest["models"][key]["vector_sources"],
            }
            for key in MODEL_ORDER
        },
        "group_rows": len(rows),
        "qwen_group_rows": 1375,
        "ordered_axis_views_per_model": 6,
        "mesh_variants_per_model": 45,
        "aggregation": data["aggregation"],
        "grid_size": 61,
        "smoothing": SMOOTHING,
        "height_range": [0, 100],
        "color_range": [0, 100],
        "bounded_fabric": "Clip fitted surface only to 0-100; preserve exact group nodes",
        "support_mask": "Recomputed independently per model and PC pair from that model's oriented coordinates",
        "flat_plane_fit": "Recomputed per model/group/view by least squares over normalized selected-model PC coordinates",
        "flat_adherence": "Descriptive R2 of each model's flat plane as an approximation to its displayed rolling fabric",
        "fit_diagnostics": "In-sample descriptive errors recomputed independently per model; not held-out validation",
        "coordinate_orientation": ridge_data["methodology"]["coordinate_orientation"],
        "cross_model_caveat": data["cross_model_caveat"],
        "qwen_reproduction_max_abs_difference": qwen_max_difference,
        "qwen_reproduction_max_difference_path": qwen_max_path,
        "gpu_used": False,
        "runpod_used": False,
        "api_calls": 0,
        "new_activations": False,
        "new_inference": False,
        "plotly_python_version": plotly.__version__,
        "sources": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in source_paths
        ],
    }
    save_json("trait_surface_manifest.json", manifest)
    print(
        json.dumps(
            {
                "models": MODEL_ORDER,
                "personas_per_model": 275,
                "groups_per_model": 5,
                "group_rows": len(rows),
                "mesh_variants": 45 * len(MODEL_ORDER),
                "qwen_reproduction_max_abs_difference": qwen_max_difference,
                "clipped_cells": {
                    key: sum(
                        row["clipped_supported_cells"] for row in diagnostics if row["model"] == key
                    )
                    for key in MODEL_ORDER
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument(
        "--qwen-reference-commit",
        default=os.environ.get("QWEN_VIEWER_REFERENCE_COMMIT", QWEN_REFERENCE_COMMIT),
    )
    arguments = parser.parse_args()
    if arguments.html_only:
        build_html(json.loads((HERE / "persona_trait_surface_data.json").read_text()))
    elif not arguments.inventory_only:
        main(arguments.qwen_reference_commit)
    inventory()
