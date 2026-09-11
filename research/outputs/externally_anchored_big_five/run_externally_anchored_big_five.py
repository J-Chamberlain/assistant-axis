#!/usr/bin/env python3
"""Run the frozen externally anchored Big Five audit using saved vectors only."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.util
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch
from scipy.interpolate import RBFInterpolator
from scipy.spatial import Delaunay, cKDTree
from scipy.stats import rankdata, spearmanr
from sklearn.model_selection import KFold


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MAPPING_FREEZE_COMMIT = "636c5c1d9b832a1199e8d5b35dea993a41f94d4b"
GENERATED_UTC = "2026-09-11T23:18:00Z"
DOMAINS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
DOMAIN_LABELS = {domain: domain.capitalize() for domain in DOMAINS}
CONSTRUCTIONS = [
    "human_anchored_strict",
    "human_anchored_extended",
    "external_taxonomy_expanded",
    "historical_hand_predeclared",
]
CONSTRUCTION_LABELS = {
    "human_anchored_strict": "Human-anchored strict",
    "human_anchored_extended": "Human-anchored extended",
    "external_taxonomy_expanded": "External-taxonomy expanded",
    "historical_hand_predeclared": "Historical hand-predeclared",
}
MODELS = {
    "qwen": ("Qwen/Qwen3-32B", "qwen-3-32b"),
    "llama": ("Llama-3.3-70B", "llama-3.3-70b"),
    "gemma": ("Gemma-2-27B", "gemma-2-27b"),
}
AXIS_PAIRS = [(0, 1), (0, 2), (1, 2)]
SMOOTHING = [("Detail", 0.003), ("Balanced", 0.03), ("Gentle", 0.3)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(directory.glob("*.pt")):
        digest.update(path.name.encode())
        digest.update(b"\0")
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def established_module():
    path = ROOT / (
        "research/outputs/multimodel_ordered_trait_region_viewer/"
        "run_multimodel_ordered_trait_region_viewer.py"
    )
    spec = importlib.util.spec_from_file_location("established_big_five_geometry", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def resolve_vector_root(requested: Path | None) -> Path:
    candidate = requested or (Path(os.environ["ASSISTANT_AXIS_VECTOR_ROOT"]) if os.environ.get("ASSISTANT_AXIS_VECTOR_ROOT") else None)
    if candidate is None:
        candidate = ROOT / "downloads/hf_vectors"
    root = candidate.expanduser().resolve()
    missing = []
    for _, folder in MODELS.values():
        for kind in ("role_vectors", "trait_vectors"):
            path = root / folder / kind
            if not path.is_dir():
                missing.append(str(path))
    if missing:
        raise FileNotFoundError("Missing saved vector dependencies; no download attempted:\n" + "\n".join(missing))
    return root


def load_mappings() -> dict[str, list[dict[str, str]]]:
    freeze = json.loads((OUT / "mapping_freeze_manifest.json").read_text())
    if freeze["freeze_commit"] != MAPPING_FREEZE_COMMIT or not freeze["geometry_blind"]:
        raise ValueError("Mapping freeze boundary is absent or changed")
    for path, expected in freeze["frozen_artifacts"].items():
        if sha256(ROOT / path) != expected:
            raise ValueError(f"Frozen mapping hash changed: {path}")

    strict = read_csv(OUT / "human_anchored_strict_trait_mapping.csv")
    extended = read_csv(OUT / "human_anchored_extended_trait_mapping.csv")
    expanded_all = read_csv(OUT / "external_taxonomy_expanded_trait_mapping.csv")
    historical_all = read_csv(ROOT / "research/outputs/same_space_big_five_overlay/big_five_trait_facet_sets.csv")

    def human(rows: list[dict[str, str]]) -> list[dict[str, str]]:
        return [{
            "trait": row["trait"], "domain": row["external_domain"],
            "facet": row["external_facet_code"], "polarity": row["polarity"],
            "tier": row["sapa_review_tier"], "rationale": row["mapping_rationale"],
        } for row in rows]

    expanded = [{
        "trait": row["trait"], "domain": row["domain"], "facet": row["facet_code"],
        "polarity": row["polarity"], "tier": "external_high_direct", "rationale": row["mapping_rationale"],
    } for row in expanded_all if row["included_in_construction"] == "yes"]
    historical = [{
        "trait": row["trait"], "domain": row["dimension"], "facet": "",
        "polarity": row["polarity"], "tier": row["polarity_type"], "rationale": row["rationale"],
    } for row in historical_all if row["available"].lower() == "true"]
    result = {
        "human_anchored_strict": human(strict),
        "human_anchored_extended": human(extended),
        "external_taxonomy_expanded": expanded,
        "historical_hand_predeclared": historical,
    }
    for key, entries in result.items():
        if {row["domain"] for row in entries} != set(DOMAINS):
            raise ValueError(f"{key}: incomplete domain coverage")
    return result


def normalized_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(norms < 1e-12):
        raise ValueError("Zero vector")
    return matrix / norms


def direction_for(entries: list[dict[str, str]], traits: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, Any]]:
    positive = [row["trait"] for row in entries if row["polarity"] == "positive"]
    negative = [row["trait"] for row in entries if row["polarity"] == "negative"]
    if not positive and not negative:
        raise ValueError("Empty domain mapping")
    pos_mean = np.mean([traits[name] for name in positive], axis=0) if positive else None
    neg_mean = np.mean([traits[name] for name in negative], axis=0) if negative else None
    if pos_mean is not None and neg_mean is not None:
        raw = pos_mean - neg_mean
        mode = "bipolar_positive_mean_minus_negative_mean"
    elif pos_mean is not None:
        raw = pos_mean
        mode = "positive_only_no_opposite_fabricated"
    else:
        raw = -neg_mean
        mode = "negative_only_reoriented_no_opposite_fabricated"
    norm = float(np.linalg.norm(raw))
    if norm < 1e-12:
        raise ValueError("Degenerate domain direction")
    direction = (raw / norm).astype("<f4")
    direction = (direction / np.linalg.norm(direction)).astype("<f4")
    return direction, {
        "positive_traits": positive,
        "negative_traits": negative,
        "positive_count": len(positive),
        "negative_count": len(negative),
        "construction_mode": mode,
        "pre_normalization_norm": norm,
    }


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if np.std(a) < 1e-14 or np.std(b) < 1e-14:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return float(spearmanr(a, b).statistic)


def percentiles(values: np.ndarray) -> np.ndarray:
    return 100 * (rankdata(values, method="average") - 0.5) / len(values)


def r2(y: np.ndarray, pred: np.ndarray) -> float:
    sst = float(np.sum((y - y.mean()) ** 2))
    return float(1 - np.sum((y - pred) ** 2) / sst)


def residualize(target: np.ndarray, controls: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(len(target)), controls])
    return target - design @ np.linalg.lstsq(design, target, rcond=None)[0]


def fixed_splits(n: int) -> list[tuple[np.ndarray, np.ndarray]]:
    return list(KFold(n_splits=10, shuffle=True, random_state=20260911).split(np.arange(n)))


def oof_linear(x: np.ndarray, y: np.ndarray, splits: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    pred = np.empty(len(y), dtype=float)
    for train, test in splits:
        mean = x[train].mean(axis=0)
        scale = x[train].std(axis=0, ddof=0)
        scale[scale < 1e-12] = 1
        train_x = (x[train] - mean) / scale
        test_x = (x[test] - mean) / scale
        beta = np.linalg.lstsq(np.column_stack([np.ones(len(train)), train_x]), y[train], rcond=None)[0]
        pred[test] = np.column_stack([np.ones(len(test)), test_x]) @ beta
    return pred


def vif_values(x: np.ndarray) -> list[float]:
    z = (x - x.mean(axis=0)) / x.std(axis=0, ddof=0)
    values = []
    for column in range(z.shape[1]):
        others = np.delete(z, column, axis=1)
        fitted = np.column_stack([np.ones(len(z)), others]) @ np.linalg.lstsq(
            np.column_stack([np.ones(len(z)), others]), z[:, column], rcond=None
        )[0]
        column_r2 = r2(z[:, column], fitted)
        values.append(float("inf") if 1 - column_r2 < 1e-12 else float(1 / (1 - column_r2)))
    return values


def plane_diagnostic(coords: np.ndarray, target: np.ndarray, axes: tuple[int, int]) -> dict[str, float]:
    xy = coords[:, axes]
    center = xy.mean(axis=0)
    scale = float(np.sqrt(np.mean(np.var(xy, axis=0))))
    normalized = (xy - center) / scale
    design = np.column_stack([np.ones(len(xy)), normalized])
    beta = np.linalg.lstsq(design, target, rcond=None)[0]
    fitted = design @ beta
    return {
        "intercept": float(beta[0]), "x_coefficient": float(beta[1]), "y_coefficient": float(beta[2]),
        "node_rmse": float(np.sqrt(np.mean((target - fitted) ** 2))), "node_r2": r2(target, fitted),
        "fit_center_x": float(center[0]), "fit_center_y": float(center[1]), "fit_common_scale": scale,
    }


def render_agreeableness(coords: np.ndarray, percent: np.ndarray, axes: tuple[int, int], suffix: str) -> None:
    xy = coords[:, axes]
    center = xy.mean(axis=0)
    scale = float(np.sqrt(np.mean(np.var(xy, axis=0))))
    points = (xy - center) / scale
    tree = cKDTree(points)
    distances, _ = tree.query(points, k=6)
    radius = float(np.quantile(distances[:, -1], 0.9))
    x = np.linspace(xy[:, 0].min(), xy[:, 0].max(), 61)
    y = np.linspace(xy[:, 1].min(), xy[:, 1].max(), 61)
    xx, yy = np.meshgrid(x, y)
    grid = (np.column_stack([xx.ravel(), yy.ravel()]) - center) / scale
    sixth, _ = tree.query(grid, k=6)
    supported = ((Delaunay(points).find_simplex(grid) >= 0) & (sixth[:, -1] <= radius)).reshape(61, 61)
    fabric = RBFInterpolator(points, percent, kernel="thin_plate_spline", smoothing=0.03, degree=1)(grid).reshape(61, 61)
    fabric = np.clip(fabric, 0, 100)
    fabric[~supported] = np.nan
    design = np.column_stack([np.ones(len(points)), points])
    beta = np.linalg.lstsq(design, percent, rcond=None)[0]
    plane = (np.column_stack([np.ones(len(grid)), grid]) @ beta).reshape(61, 61)
    plane = np.clip(plane, 0, 100)
    plane[~supported] = np.nan
    fitted = design @ beta
    plane_r2 = r2(percent, fitted)

    xmin, xmax = float(x.min()), float(x.max())
    ymin, ymax = float(y.min()), float(y.max())

    def project(x_value: float, y_value: float, z_value: float) -> tuple[float, float]:
        xn = 2 * (x_value - xmin) / (xmax - xmin) - 1
        yn = 2 * (y_value - ymin) / (ymax - ymin) - 1
        zn = z_value / 100
        return 600 + 230 * (xn - yn), 570 + 105 * (xn + yn) - 330 * zn

    def color(value: float) -> str:
        anchors = [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)]
        position = max(0.0, min(0.999999, value / 100)) * (len(anchors) - 1)
        left = int(position)
        fraction = position - left
        a, b = anchors[left], anchors[min(left + 1, len(anchors) - 1)]
        return "#" + "".join(f"{round(a[i] + fraction * (b[i] - a[i])):02x}" for i in range(3))

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">',
        '<rect width="1200" height="900" fill="#fbfaf7"/>',
        f'<text x="55" y="55" font-family="Arial,sans-serif" font-size="25" font-weight="700" fill="#17202a">Qwen human-anchored strict Agreeableness: PC{axes[0]+1} × PC{axes[1]+1}</text>',
        f'<text x="55" y="82" font-family="Arial,sans-serif" font-size="14" fill="#4b5563">Balanced surface + least-squares flat plane; node plane R²={plane_r2:.3f}</text>',
    ]
    cells = []
    for row in range(60):
        for column in range(60):
            values = [fabric[row, column], fabric[row, column + 1], fabric[row + 1, column + 1], fabric[row + 1, column]]
            if any(not np.isfinite(value) for value in values):
                continue
            points_svg = [
                project(x[column], y[row], values[0]), project(x[column + 1], y[row], values[1]),
                project(x[column + 1], y[row + 1], values[2]), project(x[column], y[row + 1], values[3]),
            ]
            points_text = " ".join(f"{px:.2f},{py:.2f}" for px, py in points_svg)
            cells.append((row + column, f'<polygon points="{points_text}" fill="{color(float(np.mean(values)))}" fill-opacity="0.72" stroke="none"/>'))
    svg.extend(value for _, value in sorted(cells, reverse=True))
    # Fixed red wireframe for the selected-model flat plane.
    for row in range(0, 61, 5):
        points_line = [project(x[column], y[row], plane[row, column]) for column in range(61) if np.isfinite(plane[row, column])]
        if len(points_line) > 1:
            svg.append('<polyline points="' + " ".join(f"{px:.2f},{py:.2f}" for px, py in points_line) + '" fill="none" stroke="#c73e4d" stroke-width="1.6" stroke-opacity="0.82"/>')
    for column in range(0, 61, 5):
        points_line = [project(x[column], y[row], plane[row, column]) for row in range(61) if np.isfinite(plane[row, column])]
        if len(points_line) > 1:
            svg.append('<polyline points="' + " ".join(f"{px:.2f},{py:.2f}" for px, py in points_line) + '" fill="none" stroke="#c73e4d" stroke-width="1.6" stroke-opacity="0.82"/>')
    for row in range(len(xy)):
        px, py = project(float(xy[row, 0]), float(xy[row, 1]), float(percent[row]))
        svg.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3.2" fill="{color(float(percent[row]))}" stroke="#111827" stroke-width="0.75"/>')
    # Axes and fixed scientific annotations.
    origin = project(xmin, ymin, 0)
    x_end = project(xmax, ymin, 0)
    y_end = project(xmin, ymax, 0)
    z_end = project(xmin, ymin, 100)
    for end in (x_end, y_end, z_end):
        svg.append(f'<line x1="{origin[0]:.2f}" y1="{origin[1]:.2f}" x2="{end[0]:.2f}" y2="{end[1]:.2f}" stroke="#1f2937" stroke-width="2"/>')
    svg.extend([
        f'<text x="{x_end[0]+8:.2f}" y="{x_end[1]+15:.2f}" font-family="Arial,sans-serif" font-size="15">PC{axes[0]+1}</text>',
        f'<text x="{y_end[0]-45:.2f}" y="{y_end[1]+15:.2f}" font-family="Arial,sans-serif" font-size="15">PC{axes[1]+1}</text>',
        f'<text x="{z_end[0]-25:.2f}" y="{z_end[1]-12:.2f}" font-family="Arial,sans-serif" font-size="15">100</text>',
        f'<text x="{origin[0]-18:.2f}" y="{origin[1]+22:.2f}" font-family="Arial,sans-serif" font-size="15">0</text>',
        '<text x="55" y="838" font-family="Arial,sans-serif" font-size="13" fill="#4b5563">Height/color: within-Qwen Agreeableness percentile. Red wireframe: independently fitted flat plane.</text>',
        '<text x="55" y="862" font-family="Arial,sans-serif" font-size="12" fill="#6b7280">Fixed camera and axis ranges; same-space activation-derived score, not independent psychometric validation.</text>',
        '</svg>',
    ])
    svg_path = OUT / f"qwen_agreeableness_{suffix}.svg"
    svg_path.write_text("\n".join(svg), encoding="utf-8")
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if chrome.is_file():
        subprocess.run([
            str(chrome), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--window-size=1200,900", f"--screenshot={OUT / f'qwen_agreeableness_{suffix}.png'}",
            svg_path.as_uri(),
        ], check=True, capture_output=True)


def main(vector_root_request: Path | None) -> None:
    vector_root = resolve_vector_root(vector_root_request)
    mappings = load_mappings()
    established, established_path = established_module()
    geometry = json.loads((ROOT / "research/visualizations/geometry_viz_data.json").read_text())["roles"]
    canonical_names = list(geometry["names"])
    reference_coords = np.asarray(geometry["pca3d"], dtype=float)
    reference = {name: reference_coords[i].tolist() for i, name in enumerate(canonical_names)}
    established_data = json.loads((ROOT / "research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_data.json").read_text())

    role_score_rows: list[dict[str, Any]] = []
    correlation_rows: list[dict[str, Any]] = []
    cosine_rows: list[dict[str, Any]] = []
    sensitivity_rows: list[dict[str, Any]] = []
    joint_rows: list[dict[str, Any]] = []
    partial_rows: list[dict[str, Any]] = []
    intercorrelation_rows: list[dict[str, Any]] = []
    plane_rows: list[dict[str, Any]] = []
    direction_manifest: dict[str, Any] = {"schema_version": 1, "vectors_encoding": "little-endian float32 base64", "directions": {}}
    viewer_data: dict[str, Any] = {
        "schema_version": 1, "default_construction": "human_anchored_strict",
        "construction_order": CONSTRUCTIONS, "construction_labels": CONSTRUCTION_LABELS,
        "domains": [{"key": d, "label": DOMAIN_LABELS[d]} for d in DOMAINS], "models": {},
        "scientific_label": "Externally anchored activation-derived Big Five; same-space model evidence",
    }
    source_models: dict[str, Any] = {}
    saved_scores: dict[tuple[str, str, str], np.ndarray] = {}
    saved_percentiles: dict[tuple[str, str, str], np.ndarray] = {}
    saved_coords: dict[str, np.ndarray] = {}
    saved_pca_components: dict[str, np.ndarray] = {}

    for model_key, (model_label, folder) in MODELS.items():
        model_root = vector_root / folder
        role_names, role_matrix = established.load_mean_vectors(model_root / "role_vectors")
        trait_names, trait_matrix = established.load_mean_vectors(model_root / "trait_vectors")
        if len(role_names) != len(set(role_names)):
            raise ValueError(f"{model_key}: invalid role count")
        if len(role_names) != 275 or len(trait_names) != 240 or set(role_names) != set(canonical_names):
            raise ValueError(f"{model_key}: role/trait coverage mismatch")
        role_by_name = {name: role_matrix[i] for i, name in enumerate(role_names)}
        trait_by_name_raw = {name: trait_matrix[i] for i, name in enumerate(trait_names)}
        ordered_roles = np.stack([role_by_name[name] for name in canonical_names])
        normalized_role = normalized_rows(ordered_roles)
        normalized_traits = {name: vector for name, vector in zip(trait_names, normalized_rows(trait_matrix))}
        if set(normalized_traits) != set(json.loads((ROOT / "data/traits/trait_list.json").read_text())):
            raise ValueError(f"{model_key}: trait names differ from canonical inventory")

        sorted_names = sorted(role_names)
        sorted_matrix = np.stack([role_by_name[name] for name in sorted_names])
        pca_coords, pca_components, explained = established.pca_numpy(sorted_matrix, 3)
        signs = established.orient_to_reference(sorted_names, pca_coords, reference)
        pca_components = pca_components * np.asarray(signs)[:, None]
        coords_by_name = {name: pca_coords[i] for i, name in enumerate(sorted_names)}
        recomputed_coords = np.stack([coords_by_name[name] for name in canonical_names])
        coords = reference_coords.copy() if model_key == "qwen" else recomputed_coords
        existing = {point["persona"]: np.array([point["pc1"], point["pc2"], point["pc3"]]) for point in established_data["models"][model_key]["points"]}
        coordinate_max_difference = max(float(np.max(np.abs(coords[i] - existing[name]))) for i, name in enumerate(canonical_names))
        if coordinate_max_difference > 1e-10:
            raise ValueError(f"{model_key}: established coordinate drift {coordinate_max_difference}")
        saved_coords[model_key] = coords
        saved_pca_components[model_key] = pca_components
        orders = [sorted(range(275), key=lambda i: (-coords[i, axis], canonical_names[i])) for axis in range(3)]
        viewer_model: dict[str, Any] = {
            "key": model_key, "label": model_label, "personas": canonical_names, "coordinates": coords.tolist(),
            "orders": orders, "orientation_signs": signs, "constructions": {},
        }
        source_models[model_key] = {
            "label": model_label,
            "logical_role_vectors": f"downloads/hf_vectors/{folder}/role_vectors",
            "logical_trait_vectors": f"downloads/hf_vectors/{folder}/trait_vectors",
            "role_bundle_sha256": bundle_sha256(model_root / "role_vectors"),
            "trait_bundle_sha256": bundle_sha256(model_root / "trait_vectors"),
            "roles": len(role_names), "traits": len(trait_names), "orientation_signs": signs,
            "coordinate_max_abs_difference_vs_established_viewer": coordinate_max_difference,
            "pca_explained_variance": [float(value) for value in explained],
        }

        for construction in CONSTRUCTIONS:
            entries = mappings[construction]
            viewer_domains = []
            score_matrix = np.empty((275, 5), dtype=float)
            for domain_index, domain in enumerate(DOMAINS):
                domain_entries = [row for row in entries if row["domain"] == domain]
                direction, info = direction_for(domain_entries, normalized_traits)
                encoded = base64.b64encode(direction.tobytes()).decode("ascii")
                vector_hash = hashlib.sha256(direction.tobytes()).hexdigest()
                direction_key = f"{model_key}__{construction}__{domain}"
                direction_manifest["directions"][direction_key] = {
                    "model": model_key, "construction": construction, "domain": domain,
                    "dimension": len(direction), "dtype": "float32", "sha256": vector_hash,
                    "vector_base64": encoded, **info,
                }
                scores = normalized_role @ direction.astype(float)
                pct = percentiles(scores)
                saved_scores[(model_key, construction, domain)] = scores
                saved_percentiles[(model_key, construction, domain)] = pct
                score_matrix[:, domain_index] = scores
                composition = [{key: row[key] for key in ("trait", "facet", "polarity", "tier", "rationale")} for row in domain_entries]
                viewer_domains.append({
                    "key": domain, "label": DOMAIN_LABELS[domain], "raw_score": scores.tolist(),
                    "height_percentile": pct.tolist(), "composition": composition, "direction_sha256": vector_hash,
                    "construction_mode": info["construction_mode"],
                })
                for i, name in enumerate(canonical_names):
                    role_score_rows.append({
                        "model": model_key, "model_label": model_label, "construction": construction,
                        "construction_label": CONSTRUCTION_LABELS[construction], "domain": domain,
                        "persona": name, "raw_projection_score": float(scores[i]),
                        "within_model_percentile": float(pct[i]),
                        "pc1": float(coords[i, 0]), "pc2": float(coords[i, 1]), "pc3": float(coords[i, 2]),
                    })
                for axis in range(3):
                    p = pearson(scores, coords[:, axis])
                    s = spearman(scores, coords[:, axis])
                    correlation_rows.append({
                        "model": model_key, "construction": construction, "domain": domain, "pc": f"PC{axis+1}",
                        "n": 275, "pearson_r": p, "spearman_r": s, "single_domain_r2": p * p,
                    })
                    cosine_rows.append({
                        "model": model_key, "construction": construction, "domain": domain, "pc": f"PC{axis+1}",
                        "direction_cosine": float(np.dot(direction.astype(float), pca_components[axis])),
                    })
                for axes in AXIS_PAIRS:
                    diagnostic = plane_diagnostic(coords, pct, axes)
                    plane_rows.append({
                        "model": model_key, "construction": construction, "domain": domain,
                        "x_axis": f"PC{axes[0]+1}", "y_axis": f"PC{axes[1]+1}", **diagnostic,
                    })

                full_scores = scores
                for dropped in domain_entries:
                    subset = [row for row in domain_entries if row["trait"] != dropped["trait"]]
                    if not subset:
                        continue
                    alternate, _ = direction_for(subset, normalized_traits)
                    alternate_scores = normalized_role @ alternate.astype(float)
                    sensitivity_rows.append({
                        "model": model_key, "construction": construction, "domain": domain,
                        "sensitivity_type": "leave_one_trait_out", "omitted": dropped["trait"],
                        "omitted_polarity": dropped["polarity"],
                        "direction_cosine_to_full": float(np.dot(direction.astype(float), alternate.astype(float))),
                        "role_score_pearson_to_full": pearson(full_scores, alternate_scores),
                        "role_score_spearman_to_full": spearman(full_scores, alternate_scores),
                    })
                facets = sorted({row["facet"] for row in domain_entries if row["facet"]})
                for facet in facets:
                    subset = [row for row in domain_entries if row["facet"] != facet]
                    if not subset:
                        continue
                    alternate, _ = direction_for(subset, normalized_traits)
                    alternate_scores = normalized_role @ alternate.astype(float)
                    sensitivity_rows.append({
                        "model": model_key, "construction": construction, "domain": domain,
                        "sensitivity_type": "leave_one_facet_out", "omitted": facet,
                        "omitted_polarity": "mixed",
                        "direction_cosine_to_full": float(np.dot(direction.astype(float), alternate.astype(float))),
                        "role_score_pearson_to_full": pearson(full_scores, alternate_scores),
                        "role_score_spearman_to_full": spearman(full_scores, alternate_scores),
                    })
                positive_entries = [row for row in domain_entries if row["polarity"] == "positive"]
                if positive_entries and positive_entries != domain_entries:
                    alternate, _ = direction_for(positive_entries, normalized_traits)
                    alternate_scores = normalized_role @ alternate.astype(float)
                    sensitivity_rows.append({
                        "model": model_key, "construction": construction, "domain": domain,
                        "sensitivity_type": "positive_only_vs_bipolar", "omitted": "all_negative_traits",
                        "omitted_polarity": "negative",
                        "direction_cosine_to_full": float(np.dot(direction.astype(float), alternate.astype(float))),
                        "role_score_pearson_to_full": pearson(full_scores, alternate_scores),
                        "role_score_spearman_to_full": spearman(full_scores, alternate_scores),
                    })
            viewer_model["constructions"][construction] = {
                "key": construction, "label": CONSTRUCTION_LABELS[construction], "domains": viewer_domains,
            }

            splits = fixed_splits(275)
            vif = vif_values(score_matrix)
            condition = float(np.linalg.cond((score_matrix - score_matrix.mean(axis=0)) / score_matrix.std(axis=0, ddof=0)))
            for left in range(5):
                for right in range(left + 1, 5):
                    intercorrelation_rows.append({
                        "model": model_key, "construction": construction,
                        "domain_1": DOMAINS[left], "domain_2": DOMAINS[right],
                        "pearson_r": pearson(score_matrix[:, left], score_matrix[:, right]),
                        "spearman_r": spearman(score_matrix[:, left], score_matrix[:, right]),
                        "condition_number_five_domain_matrix": condition,
                    })
            xz = (score_matrix - score_matrix.mean(axis=0)) / score_matrix.std(axis=0, ddof=0)
            for axis in range(3):
                y = coords[:, axis]
                yz = (y - y.mean()) / y.std(ddof=0)
                standardized_beta = np.linalg.lstsq(np.column_stack([np.ones(275), xz]), yz, rcond=None)[0][1:]
                full_pred = oof_linear(score_matrix, y, splits)
                joint_rows.append({
                    "model": model_key, "construction": construction, "pc": f"PC{axis+1}",
                    "model_type": "joint_five_domain", "domain": "all_five",
                    "held_out_r2": r2(y, full_pred), "in_sample_r2": r2(y, np.column_stack([np.ones(275), score_matrix]) @ np.linalg.lstsq(np.column_stack([np.ones(275), score_matrix]), y, rcond=None)[0]),
                    "condition_number": condition, "max_vif": max(vif),
                    **{f"standardized_beta_{domain}": float(standardized_beta[i]) for i, domain in enumerate(DOMAINS)},
                    **{f"vif_{domain}": float(vif[i]) for i, domain in enumerate(DOMAINS)},
                })
                full_sse = float(np.sum((y - full_pred) ** 2))
                for domain_index, domain in enumerate(DOMAINS):
                    individual_pred = oof_linear(score_matrix[:, domain_index], y, splits)
                    corr = pearson(score_matrix[:, domain_index], y)
                    joint_rows.append({
                        "model": model_key, "construction": construction, "pc": f"PC{axis+1}",
                        "model_type": "individual_domain", "domain": domain,
                        "held_out_r2": r2(y, individual_pred), "in_sample_r2": corr * corr,
                        "condition_number": 1.0, "max_vif": 1.0,
                        **{f"standardized_beta_{d}": float(corr) if d == domain else "" for d in DOMAINS},
                        **{f"vif_{d}": 1.0 if d == domain else "" for d in DOMAINS},
                    })
                    reduced = np.delete(score_matrix, domain_index, axis=1)
                    reduced_pred = oof_linear(reduced, y, splits)
                    reduced_sse = float(np.sum((y - reduced_pred) ** 2))
                    other_indices = [i for i in range(5) if i != domain_index]
                    x_resid = residualize(score_matrix[:, domain_index], score_matrix[:, other_indices])
                    y_resid = residualize(y, score_matrix[:, other_indices])
                    partial_corr = pearson(x_resid, y_resid)
                    partial_rows.append({
                        "model": model_key, "construction": construction, "pc": f"PC{axis+1}", "domain": domain,
                        "standardized_joint_coefficient": float(standardized_beta[domain_index]),
                        "partial_correlation": partial_corr, "partial_r2_in_sample": partial_corr * partial_corr,
                        "partial_r2_held_out": float(1 - full_sse / reduced_sse),
                        "full_model_held_out_r2": r2(y, full_pred), "reduced_model_held_out_r2": r2(y, reduced_pred),
                    })
        viewer_data["models"][model_key] = viewer_model

    # Explicit direct-only versus direct+close sensitivity.
    for model_key in MODELS:
        for domain in DOMAINS:
            strict_key = (model_key, "human_anchored_strict", domain)
            extended_key = (model_key, "human_anchored_extended", domain)
            strict_vector = np.frombuffer(base64.b64decode(direction_manifest["directions"]["__".join(strict_key)]["vector_base64"]), dtype="<f4")
            extended_vector = np.frombuffer(base64.b64decode(direction_manifest["directions"]["__".join(extended_key)]["vector_base64"]), dtype="<f4")
            sensitivity_rows.append({
                "model": model_key, "construction": "human_anchored_extended", "domain": domain,
                "sensitivity_type": "direct_only_vs_direct_plus_close", "omitted": "all_ACCEPT_CLOSE",
                "omitted_polarity": "mixed", "direction_cosine_to_full": float(np.dot(strict_vector, extended_vector)),
                "role_score_pearson_to_full": pearson(saved_scores[strict_key], saved_scores[extended_key]),
                "role_score_spearman_to_full": spearman(saved_scores[strict_key], saved_scores[extended_key]),
            })

    write_csv(OUT / "big_five_role_scores.csv", role_score_rows)
    write_csv(OUT / "big_five_pc_correlations.csv", correlation_rows)
    write_csv(OUT / "big_five_pc_direction_cosines.csv", cosine_rows)
    write_csv(OUT / "big_five_joint_pc_models.csv", joint_rows)
    write_csv(OUT / "big_five_partial_r2.csv", partial_rows)
    write_csv(OUT / "big_five_domain_intercorrelations.csv", intercorrelation_rows)
    write_csv(OUT / "big_five_facet_sensitivity.csv", sensitivity_rows)
    write_csv(OUT / "big_five_surface_fit_diagnostics.csv", plane_rows)
    save_json(OUT / "big_five_domain_directions_manifest.json", direction_manifest)
    save_json(OUT / "big_five_viewer_data.json", viewer_data)

    focal: dict[str, Any] = {
        "preregistered_focus": "Agreeableness versus model-local PC3, primary construction human_anchored_strict",
        "mapping_freeze_commit": MAPPING_FREEZE_COMMIT, "models": {},
    }
    cross_rows = []
    for model_key in MODELS:
        corr_rows = [r for r in correlation_rows if r["model"] == model_key and r["construction"] == "human_anchored_strict" and r["pc"] == "PC3"]
        agree_corr = next(r for r in corr_rows if r["domain"] == "agreeableness")
        agree_cos = next(r for r in cosine_rows if r["model"] == model_key and r["construction"] == "human_anchored_strict" and r["domain"] == "agreeableness" and r["pc"] == "PC3")
        agree_partial = next(r for r in partial_rows if r["model"] == model_key and r["construction"] == "human_anchored_strict" and r["domain"] == "agreeableness" and r["pc"] == "PC3")
        joint = next(r for r in joint_rows if r["model"] == model_key and r["construction"] == "human_anchored_strict" and r["model_type"] == "joint_five_domain" and r["pc"] == "PC3")
        competing = {r["domain"]: {"pearson_r": r["pearson_r"], "single_domain_r2": r["single_domain_r2"]} for r in corr_rows}
        payload = {
            "activation_direction_cosine": agree_cos["direction_cosine"],
            "pearson_r": agree_corr["pearson_r"], "spearman_r": agree_corr["spearman_r"],
            "single_domain_r2": agree_corr["single_domain_r2"],
            "joint_five_domain_standardized_coefficient": agree_partial["standardized_joint_coefficient"],
            "partial_correlation_controlling_other_four": agree_partial["partial_correlation"],
            "partial_r2_in_sample": agree_partial["partial_r2_in_sample"],
            "partial_r2_held_out": agree_partial["partial_r2_held_out"],
            "joint_five_domain_held_out_r2": joint["held_out_r2"],
            "remaining_pc3_variance_after_single_domain": 1 - agree_corr["single_domain_r2"],
            "competing_domains": competing,
        }
        focal["models"][model_key] = payload
        cross_rows.append({"model": model_key, **{key: value for key, value in payload.items() if key != "competing_domains"}})
    save_json(OUT / "agreeableness_pc3_focal_test.json", focal)
    write_csv(OUT / "agreeableness_pc3_cross_model_comparison.csv", cross_rows)

    qwen_coords = saved_coords["qwen"]
    qwen_agree = saved_percentiles[("qwen", "human_anchored_strict", "agreeableness")]
    render_agreeableness(qwen_coords, qwen_agree, (0, 2), "pc1_pc3")
    render_agreeableness(qwen_coords, qwen_agree, (1, 2), "pc2_pc3")
    render_agreeableness(qwen_coords, qwen_agree, (0, 1), "pc1_pc2")

    prior_files = [
        ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json",
        ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridges.html",
        ROOT / "research/outputs/persona_trait_surface_viewer/persona_trait_surface_data.json",
        ROOT / "research/outputs/persona_trait_surface_viewer/persona_trait_surface_viewer.html",
    ]
    source_manifest = {
        "schema_version": 1, "generated_utc": GENERATED_UTC, "model_used": "GPT-5.5",
        "starting_commit": "7914d01f7d9c23060fe199815a90e547241d9682",
        "mapping_freeze_commit": MAPPING_FREEZE_COMMIT,
        "mapping_freeze_manifest_sha256": sha256(OUT / "mapping_freeze_manifest.json"),
        "models": source_models,
        "coordinate_procedure": (
            "Qwen uses canonical geometry_viz_data coordinates. PCA loading vectors are recomputed from Qwen's "
            "own layer-mean role vectors and sign-oriented to that reference. Llama and Gemma use their own "
            "layer-mean role-vector PCA, with the established corresponding-axis Qwen sign orientation."
        ),
        "established_coordinate_script": str(established_path.relative_to(ROOT)),
        "pre_integration_viewer_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in prior_files},
        "compute": "CPU-only over saved local released vectors; no inference, activation extraction, GPU, RunPod, or external model API.",
        "scientific_boundary": "Same-space activation-derived trait evidence; external anchoring is not independent human psychometric validation.",
    }
    save_json(OUT / "source_manifest.json", source_manifest)
    print(json.dumps(focal, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector-root", type=Path)
    args = parser.parse_args()
    main(args.vector_root)
