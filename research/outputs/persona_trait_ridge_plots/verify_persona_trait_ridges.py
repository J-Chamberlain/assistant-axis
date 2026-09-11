#!/usr/bin/env python3
"""Independent numerical, compatibility, and complete-markup ridge checks."""
from __future__ import annotations

import csv
import hashlib
from html.parser import HTMLParser
import json
import subprocess
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODELS = ["qwen", "llama", "gemma"]


class PlotParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict[str, str | None]] = []
        self.circles = 0
        self.scripts = 0
        self.external: list[str] = []
        self.model_views: list[dict[str, str | None]] = []
        self.model_options: list[dict[str, str | None]] = []
        self._model_select = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if "ridge-row" in classes:
            self.rows.append(attributes)
        if "model-view" in classes:
            self.model_views.append(attributes)
        if tag == "circle":
            self.circles += 1
        if tag == "script":
            self.scripts += 1
            if "src" in attributes:
                self.external.append(attributes["src"] or "")
        if tag == "select" and attributes.get("id") == "model-select":
            self._model_select = True
        elif tag == "option" and self._model_select:
            self.model_options.append(attributes)

    def handle_endtag(self, tag: str) -> None:
        if tag == "select" and self._model_select:
            self._model_select = False


def git_json(commit: str, path: str) -> dict[str, object]:
    return json.loads(
        subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)
    )


def main() -> None:
    data = json.loads((HERE / "persona_trait_ridge_data.json").read_text())
    manifest = json.loads((HERE / "persona_trait_ridge_manifest.json").read_text())
    keys = [row["trait"] for row in data["categories"]]
    if data["default_model"] != "qwen" or data["model_order"] != MODELS:
        raise AssertionError("Qwen must be the default model and model order must be stable")
    if len(keys) != len(set(keys)) or len(keys) != 15:
        raise AssertionError("Displayed trait set must contain exactly 15 unique traits")

    role_sets: list[set[str]] = []
    coordinates_by_model: dict[str, np.ndarray] = {}
    raw_by_model: dict[str, np.ndarray] = {}
    established = json.loads(
        (
            ROOT
            / "research/outputs/multimodel_ordered_trait_region_viewer/"
            "multimodel_ordered_trait_region_data.json"
        ).read_text()
    )["models"]
    coordinate_differences: dict[str, float] = {}
    for model_key in MODELS:
        model = data["models"][model_key]
        names = model["personas"]
        coordinates = np.asarray(model["coordinates"], dtype=np.float64)
        raw = np.asarray(model["raw_affinity"], dtype=np.float64)
        z_score = np.asarray(model["z_score"], dtype=np.float64)
        percentile = np.asarray(model["height_percentile"], dtype=np.float64)
        if not (len(names) == len(set(names)) == model["source_role_count"] == 275):
            raise AssertionError(f"{model_key}: role count")
        if model["source_trait_count"] != 240 or model["displayed_trait_count"] != 15:
            raise AssertionError(f"{model_key}: trait count")
        if coordinates.shape != (275, 3) or raw.shape != (275, 15):
            raise AssertionError(f"{model_key}: matrix shape")
        if not np.isfinite(coordinates).all() or not np.isfinite(raw).all() or not np.isfinite(z_score).all():
            raise AssertionError(f"{model_key}: finite data")
        independent = np.asarray(
            [
                [100 * ((raw[:, trait] < value).sum() + 0.5 * (raw[:, trait] == value).sum()) / 275
                 for trait, value in enumerate(row)]
                for row in raw
            ]
        )
        if not np.allclose(independent, percentile, atol=1e-12, rtol=0):
            raise AssertionError(f"{model_key}: within-model percentile calculation")
        expected_z = (raw - raw.mean(axis=0)) / raw.std(axis=0, ddof=0)
        if not np.allclose(expected_z, z_score, atol=1e-12, rtol=0):
            raise AssertionError(f"{model_key}: population z calculation")
        for axis in range(3):
            order = sorted(range(275), key=lambda index: (-coordinates[index, axis], names[index]))
            if model["orders"][axis] != order:
                raise AssertionError(f"{model_key}: PC{axis+1} order")
        saved = {point["persona"]: point for point in established[model_key]["points"]}
        coordinate_differences[model_key] = max(
            abs(coordinates[index, axis] - saved[name][f"pc{axis+1}"])
            for index, name in enumerate(names) for axis in range(3)
        )
        if coordinate_differences[model_key] > 1e-10:
            raise AssertionError(f"{model_key}: established coordinate mismatch")
        role_sets.append(set(names))
        coordinates_by_model[model_key] = coordinates
        raw_by_model[model_key] = raw
    if len({frozenset(names) for names in role_sets}) != 1:
        raise AssertionError("Role-name set differs across models")

    matrix = {
        row["persona"]: row
        for row in csv.DictReader(
            (ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv").open()
        )
    }
    qwen = data["models"]["qwen"]
    canonical_raw = np.asarray([[float(matrix[name][key]) for key in keys] for name in qwen["personas"]])
    if not np.array_equal(canonical_raw, raw_by_model["qwen"]):
        raise AssertionError("Qwen raw scores drifted from canonical primary matrix")
    for key in ["personas", "coordinates", "raw_affinity", "z_score", "height_percentile", "orders"]:
        if data[key] != qwen[key]:
            raise AssertionError(f"Backward-compatible Qwen alias mismatch: {key}")

    previous = git_json(
        manifest["qwen_compatibility_reference_commit"],
        "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json",
    )
    qwen_max_differences = {
        key: float(np.max(np.abs(np.asarray(qwen[key]) - np.asarray(previous[key]))))
        for key in ["coordinates", "raw_affinity", "z_score", "height_percentile"]
    }
    if any(value != 0 for value in qwen_max_differences.values()):
        raise AssertionError(f"Qwen numeric compatibility drift: {qwen_max_differences}")

    parser = PlotParser()
    markup = (HERE / "persona_trait_ridges.html").read_text()
    parser.feed(markup)
    if len(parser.rows) != 2475 or parser.circles != 37125:
        raise AssertionError("Complete three-model pre-rendered markup counts failed")
    if parser.scripts != 1 or parser.external:
        raise AssertionError("Ridge viewer must have one inline script and no external scripts")
    if len(parser.model_views) != 3 or [option.get("value") for option in parser.model_options] != MODELS:
        raise AssertionError("Model selector/view markup")
    if "hidden" in parser.model_views[0] or any("hidden" not in view for view in parser.model_views[1:]):
        raise AssertionError("Default Qwen visibility")

    offset = 0
    for model_key in MODELS:
        model = data["models"][model_key]
        for axis in range(3):
            expected = model["orders"][axis]
            chunk = parser.rows[offset:offset + 275]
            offset += 275
            for rank, (index, row) in enumerate(zip(expected, chunk), 1):
                if row["data-model"] != model_key or int(row["data-axis"] or 0) != axis + 1:
                    raise AssertionError("Model/axis markup mismatch")
                if row["data-persona"] != model["personas"][index] or int(row["data-rank"] or 0) != rank:
                    raise AssertionError("Persona rank markup mismatch")
                if not np.isclose(float(row["data-pc"] or "nan"), model["coordinates"][index][axis], atol=1e-10):
                    raise AssertionError("Persona coordinate markup mismatch")

    scores = list(csv.DictReader((HERE / "persona_trait_ridge_scores.csv").open()))
    if len(scores) != 12375 or len({(row["model"], row["persona"], row["trait"]) for row in scores}) != 12375:
        raise AssertionError("Complete score CSV")
    if sum(row["model"] == "qwen" for row in scores) != 4125:
        raise AssertionError("Qwen row count")
    for source in manifest["source_files"]:
        if hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() != source["sha256"]:
            raise AssertionError(f"Source checksum failed: {source['path']}")

    coordinate_data_changes = {
        model_key: {
            "coordinate_max_abs_difference_vs_qwen": float(
                np.max(np.abs(coordinates_by_model[model_key] - coordinates_by_model["qwen"]))
            ),
            "displayed_raw_score_max_abs_difference_vs_qwen": float(
                np.max(np.abs(raw_by_model[model_key] - raw_by_model["qwen"]))
            ),
        }
        for model_key in ["llama", "gemma"]
    }
    if any(
        values["coordinate_max_abs_difference_vs_qwen"] == 0
        or values["displayed_raw_score_max_abs_difference_vs_qwen"] == 0
        for values in coordinate_data_changes.values()
    ):
        raise AssertionError("Model selection would only relabel Qwen data")

    checks = {
        "status": "pass",
        "models": MODELS,
        "unique_roles_per_model": 275,
        "source_traits_per_model": 240,
        "displayed_traits": keys,
        "score_rows": 12375,
        "qwen_score_rows": 4125,
        "persona_rows_in_html": 2475,
        "category_points_in_html": 37125,
        "role_name_sets_identical": True,
        "finite_coordinates": True,
        "finite_trait_scores": True,
        "within_model_percentiles": True,
        "all_model_pc_orders_descending": True,
        "coordinate_max_abs_difference_vs_established": coordinate_differences,
        "qwen_reproduction_max_abs_differences": qwen_max_differences,
        "model_data_changes": coordinate_data_changes,
        "default_model": "qwen",
        "all_panels_prerendered": True,
        "no_external_scripts": True,
        "browser_validation": "Recorded separately; this check is numerical/static markup only",
    }
    (HERE / "persona_trait_ridge_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
