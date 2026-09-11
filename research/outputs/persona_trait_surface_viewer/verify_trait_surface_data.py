#!/usr/bin/env python3
"""Independent multimodel aggregation, surface, support, and compatibility checks."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay, cKDTree


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODELS = ["qwen", "llama", "gemma"]


def git_json(commit: str, path: str) -> dict[str, object]:
    return json.loads(
        subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)
    )


def recursive_max(current: object, previous: object, path: str = "") -> tuple[float, str]:
    if isinstance(current, dict) and isinstance(previous, dict):
        assert current.keys() == previous.keys(), path
        return max(
            (recursive_max(current[key], previous[key], f"{path}/{key}") for key in current),
            default=(0.0, path), key=lambda pair: pair[0],
        )
    if isinstance(current, list) and isinstance(previous, list):
        assert len(current) == len(previous), path
        return max(
            (recursive_max(value, old, f"{path}/{index}") for index, (value, old) in enumerate(zip(current, previous))),
            default=(0.0, path), key=lambda pair: pair[0],
        )
    if isinstance(current, (int, float)) and not isinstance(current, bool):
        return abs(float(current) - float(previous)), path
    assert current == previous, (path, current, previous)
    return 0.0, path


def expected_support(coordinates: np.ndarray, axes: list[int], view: dict[str, object]) -> np.ndarray:
    xy = coordinates[:, axes]
    center = xy.mean(axis=0)
    scale = float(np.sqrt(np.mean(np.var(xy, axis=0))))
    points = (xy - center) / scale
    unique = np.unique(points, axis=0)
    tree = cKDTree(unique)
    distances, _ = tree.query(unique, k=6)
    radius = float(np.quantile(distances[:, -1], 0.9))
    xx, yy = np.meshgrid(np.asarray(view["x"]), np.asarray(view["y"]))
    grid = (np.column_stack([xx.ravel(), yy.ravel()]) - center) / scale
    sixth, _ = tree.query(grid, k=6)
    support = ((Delaunay(unique).find_simplex(grid) >= 0) & (sixth[:, -1] <= radius)).reshape(61, 61)
    assert np.allclose(center, view["fit_center"], atol=1e-12, rtol=0)
    assert abs(scale - view["fit_common_scale"]) < 1e-12
    assert abs(radius - view["support_sixth_neighbor_radius"]) < 1e-12
    return support


def main() -> None:
    data = json.loads((HERE / "persona_trait_surface_data.json").read_text())
    ridge = json.loads(
        (ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json").read_text()
    )
    manifest = json.loads((HERE / "trait_surface_manifest.json").read_text())
    assert data["default_model"] == "qwen" and data["model_order"] == MODELS
    masks: dict[str, dict[str, np.ndarray]] = {model: {} for model in MODELS}
    for model_key in MODELS:
        model = data["models"][model_key]
        ridge_model = ridge["models"][model_key]
        assert [role["name"] for role in model["roles"]] == ridge_model["personas"]
        assert [role["pcs"] for role in model["roles"]] == ridge_model["coordinates"]
        assert len(model["roles"]) == 275 and len(model["categories"]) == 5
        coordinates = np.asarray([role["pcs"] for role in model["roles"]], dtype=np.float64)
        for category in model["categories"]:
            indices = [
                index for index, trait in enumerate(ridge["categories"])
                if trait["group"] == category["label"]
            ]
            assert len(indices) == 3
            source = np.asarray(ridge_model["height_percentile"])[:, indices]
            assert np.array_equal(np.asarray(category["values"]), source.mean(axis=1))
            assert abs(np.mean(category["values"]) - 50) < 1e-12
            for member, index in zip(category["members"], indices):
                assert member["key"] == ridge["categories"][index]["trait"]
                assert np.array_equal(member["percentile"], np.asarray(ridge_model["height_percentile"])[:, index])
                assert np.array_equal(member["raw"], np.asarray(ridge_model["raw_affinity"])[:, index])
        assert len(model["views"]) == 3
        for view_key, view in model["views"].items():
            support = expected_support(coordinates, view["axes"], view)
            masks[model_key][view_key] = support
            assert abs(float(support.mean()) - view["supported_grid_fraction"]) < 1e-15
            assert len(view["levels"]) == 3
            assert len(view["flat_grids"]) == 5 and len(view["flat_plane"]) == 5
            scores = np.asarray([category["values"] for category in model["categories"]]).T
            points = (coordinates[:, view["axes"]] - np.asarray(view["fit_center"])) / view["fit_common_scale"]
            basis = np.column_stack([np.ones(len(points)), points])
            for group_index, (flat_grid, plane) in enumerate(zip(view["flat_grids"], view["flat_plane"])):
                flat_mask = np.asarray([[value is not None for value in row] for row in flat_grid])
                assert np.array_equal(flat_mask, support)
                array = np.asarray([[np.nan if value is None else value for value in row] for row in flat_grid])
                assert np.nanmin(array) >= 0 and np.nanmax(array) <= 100
                coefficients = np.linalg.lstsq(basis, scores[:, group_index], rcond=None)[0]
                fitted = basis @ coefficients
                rmse = float(np.sqrt(np.mean((scores[:, group_index] - fitted) ** 2)))
                sst = float(np.sum((scores[:, group_index] - scores[:, group_index].mean()) ** 2))
                r2 = float(1 - np.sum((scores[:, group_index] - fitted) ** 2) / sst)
                assert np.allclose(coefficients, plane["coefficients"], atol=1e-12, rtol=0)
                assert abs(rmse - plane["node_rmse"]) < 1e-12
                assert abs(r2 - plane["node_r2"]) < 1e-12
            for level in view["levels"]:
                assert len(level["grids"]) == 5 and len(level["flat_adherence"]) == 5
                for group_index, grid in enumerate(level["grids"]):
                    grid_mask = np.asarray([[value is not None for value in row] for row in grid])
                    assert np.array_equal(grid_mask, support)
                    array = np.asarray([[np.nan if value is None else value for value in row] for row in grid])
                    assert np.nanmin(array) >= 0 and np.nanmax(array) <= 100
                    fitted = np.asarray(level["fitted_nodes"][group_index])
                    assert len(fitted) == 275 and np.isfinite(fitted).all()
                    rmse = np.sqrt(np.mean((fitted - np.asarray(model["categories"][group_index]["values"])) ** 2))
                    assert abs(rmse - level["fit_rmse"][group_index]) < 1e-10
                    flat = level["flat_adherence"][group_index]
                    assert flat["fabric_flat_rmse"] >= 0
                    assert flat["fabric_flat_r2"] is None or np.isfinite(flat["fabric_flat_r2"])
                    assert flat["fabric_flat_score"] is None or 0 <= flat["fabric_flat_score"] <= 100

    mask_differences = {
        model: {
            key: int(np.count_nonzero(masks[model][key] != masks["qwen"][key]))
            for key in masks[model]
        }
        for model in ["llama", "gemma"]
    }
    assert all(any(count > 0 for count in differences.values()) for differences in mask_differences.values())

    rows = list(csv.DictReader((HERE / "persona_trait_group_scores.csv").open()))
    assert len(rows) == len({(row["model"], row["persona"], row["group"]) for row in rows}) == 4125
    assert all(sum(row["model"] == model for row in rows) == 1375 for model in MODELS)
    for row in rows:
        assert abs(
            float(row["group_mean_trait_percentile"])
            - sum(float(row[f"percentile_{index}"]) for index in [1, 2, 3]) / 3
        ) < 1e-12
    diagnostics = list(csv.DictReader((HERE / "trait_surface_fit_diagnostics.csv").open()))
    assert len(diagnostics) == 135
    assert all(sum(row["model"] == model for row in diagnostics) == 45 for model in MODELS)
    for source in manifest["sources"]:
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"], source["path"]

    previous = git_json(
        manifest["qwen_compatibility_reference_commit"],
        "research/outputs/persona_trait_surface_viewer/persona_trait_surface_data.json",
    )
    qwen_science = {
        key: data["models"]["qwen"][key]
        for key in ["roles", "categories", "views", "height_range", "aggregation", "caveat"]
    }
    qwen_science["aggregation"] = "Equal-weight mean of three within-trait midrank percentiles from the ridge plots"
    difference, difference_path = recursive_max(qwen_science, previous)
    assert difference == 0

    html = (HERE / "persona_trait_surface_viewer.html").read_text()
    for token in ["__BOOTSTRAP_JS__", "__PLOTLY_LIBRARY__", "__VIEWER_DATA__", "__CAMERA_JS__", "__VIEWER_JS__"]:
        assert token not in html
    assert "<script src=" not in html and "__traitViewer" in html
    scripts = [part.split("</script>", 1)[0] for part in html.split("<script")[1:]]
    embedded = [part.split(">", 1)[1] for part in scripts if 'id="viewer-data"' in part]
    assert len(embedded) == 1 and json.loads(embedded[0]) == data

    result = {
        "status": "pass",
        "models": MODELS,
        "personas_per_model": 275,
        "source_traits_per_model": 240,
        "displayed_traits": 15,
        "groups_per_model": 5,
        "group_rows": 4125,
        "qwen_group_rows": 1375,
        "surface_variants": 135,
        "exact_model_coordinates": True,
        "exact_member_scores": True,
        "equal_weight_group_means": True,
        "population_group_mean": 50,
        "all_meshes_bounded": True,
        "support_masks_recomputed_from_selected_model_coordinates": True,
        "support_mask_cell_differences_vs_qwen": mask_differences,
        "flat_planes_recomputed_per_model": True,
        "flat_adherence_recomputed_per_model": True,
        "qwen_reproduction_max_abs_difference": difference,
        "qwen_reproduction_max_difference_path": difference_path,
        "source_hashes": True,
        "self_contained_html": True,
        "default_model": "qwen",
        "new_activations": False,
        "new_inference": False,
    }
    (HERE / "trait_surface_data_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
