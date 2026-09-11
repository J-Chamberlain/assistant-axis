#!/usr/bin/env python3
"""Build the saved-artifact trait-profile geometry equalizer.

This script performs CPU-only regression fitting against existing activation-derived
artifacts. It never invokes Qwen, extracts activations, or calls an external API.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
PREDICTOR_DIR = REPO_ROOT / "research/outputs/trait_profile_pc_predictor"
CANONICAL_MATRIX = REPO_ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
GEOMETRY = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
DEFINITIONS = REPO_ROOT / "data/traits/trait_list.json"
CANONICAL_EXPLORER = REPO_ROOT / "research/visualizations/persona_geometry_explorer.html"
RUNNER_PATH = PREDICTOR_DIR / "run_trait_profile_pc_predictor.py"
CLI_PATH = PREDICTOR_DIR / "predict_trait_profile.py"
LOPO_CSV = PREDICTOR_DIR / "leave_one_persona_out_predictions.csv"
RIDGE_JSON = PREDICTOR_DIR / "ridge_predictor.json"
OOD_JSON = PREDICTOR_DIR / "ood_reference.json"
VALIDATION_JSON = PREDICTOR_DIR / "validation_summary.json"
LOPO_MODELS_PATH = HERE / "lopo_ridge_predictors.json"
DATA_PATH = HERE / "trait_profile_geometry_data.json"
REFERENCE_CASES_PATH = HERE / "browser_python_reference_cases.json"
SOURCE_MANIFEST_PATH = HERE / "source_manifest.json"
GENERATED_HTML_PATH = HERE / "trait_profile_geometry_explorer.html"
INVENTORY_PATH = HERE / "artifact_inventory.csv"
RAW_BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
BRANCH_RAW_BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/trait-profile-equalizer/"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_output(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def load_inputs() -> dict[str, Any]:
    matrix = pd.read_csv(CANONICAL_MATRIX)
    geometry = read_json(GEOMETRY)
    definitions = read_json(DEFINITIONS)
    ridge = read_json(RIDGE_JSON)
    ood = read_json(OOD_JSON)
    validation = read_json(VALIDATION_JSON)
    personas = matrix["persona"].astype(str).tolist()
    traits = matrix.columns[1:].astype(str).tolist()
    coordinates = np.asarray(geometry["roles"]["pca3d"], dtype=np.float64)
    clusters = list(geometry["roles"]["clusters"])
    x = matrix.iloc[:, 1:].to_numpy(dtype=np.float64)
    if personas != list(geometry["roles"]["names"]):
        raise RuntimeError("Matrix personas do not exactly match canonical geometry order")
    if traits != list(ridge["trait_feature_names"]):
        raise RuntimeError("Matrix traits do not exactly match Ridge feature order")
    if traits != list(ood["trait_feature_names"]):
        raise RuntimeError("Matrix traits do not exactly match OOD feature order")
    if set(traits) != set(definitions):
        raise RuntimeError("Canonical trait definitions do not exactly cover the 240 predictor traits")
    if len(personas) != len(set(personas)) or len(personas) != 275:
        raise RuntimeError("Expected 275 unique personas")
    if len(traits) != len(set(traits)) or len(traits) != 240:
        raise RuntimeError("Expected 240 unique traits")
    if not np.isfinite(x).all() or not np.isfinite(coordinates).all():
        raise RuntimeError("Nonfinite matrix or geometry value")
    return {
        "matrix": matrix,
        "x": x,
        "coordinates": coordinates,
        "personas": personas,
        "traits": traits,
        "clusters": clusters,
        "definitions": definitions,
        "ridge": ridge,
        "ood": ood,
        "validation": validation,
    }


def load_saved_lopo(personas: list[str]) -> dict[str, dict[str, Any]]:
    saved: dict[str, dict[str, Any]] = {}
    with LOPO_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["representation"] != "raw_cosine":
                continue
            saved[row["persona"]] = {
                "prediction": [float(row[f"predicted_pc{i}"]) for i in (1, 2, 3)],
                "selected_alpha": float(row["selected_alpha"]),
                "actual": [float(row[f"actual_pc{i}"]) for i in (1, 2, 3)],
            }
    if list(saved) != personas:
        raise RuntimeError("Saved raw-cosine LOPO rows do not match canonical persona order")
    return saved


def fit_lopo_models(inputs: dict[str, Any], n_jobs: int) -> tuple[dict[str, Any], dict[str, Any]]:
    runner = load_module(RUNNER_PATH, "canonical_trait_profile_runner")
    x = inputs["x"]
    y = inputs["coordinates"]
    personas = inputs["personas"]
    saved = load_saved_lopo(personas)
    models: dict[str, Any] = {}
    errors: list[float] = []
    alpha_mismatches: list[dict[str, Any]] = []
    for held_out, persona in enumerate(personas):
        train_mask = np.ones(len(personas), dtype=bool)
        train_mask[held_out] = False
        search = runner.fit_tuned(
            "ridge", "raw_cosine", x[train_mask], y[train_mask], 10_000 + held_out, n_jobs
        )
        portable = runner.linear_portable(search.best_estimator_, x.shape[1])
        prediction = np.asarray(search.predict(x[[held_out]])[0], dtype=np.float64)
        portable_prediction = np.asarray(portable["coefficients"], dtype=np.float64) @ x[held_out] + np.asarray(portable["intercepts"])
        saved_prediction = np.asarray(saved[persona]["prediction"], dtype=np.float64)
        error = float(np.max(np.abs(portable_prediction - saved_prediction)))
        errors.append(error)
        selected_alpha = float(search.best_params_["regressor__model__alpha"])
        if not math.isclose(selected_alpha, saved[persona]["selected_alpha"], rel_tol=0.0, abs_tol=0.0):
            alpha_mismatches.append({"persona": persona, "refit": selected_alpha, "saved": saved[persona]["selected_alpha"]})
        if float(np.max(np.abs(prediction - portable_prediction))) > 1e-10:
            raise RuntimeError(f"Portable held-out prediction mismatch for {persona}")
        models[persona] = {
            "model_type": "Ridge",
            "input_representation": "raw_cosine",
            "excluded_persona": persona,
            "training_persona_count": 274,
            "inner_cv": {"type": "KFold", "n_splits": 4, "shuffle": True, "random_state": 10_000 + held_out},
            "candidate_alphas": [float(value) for value in runner.ALPHAS],
            "selected_alpha": selected_alpha,
            "raw_input_to_pc": portable,
            "saved_unedited_lopo_prediction": saved[persona]["prediction"],
        }
        if (held_out + 1) % 25 == 0 or held_out + 1 == len(personas):
            print(f"held-out Ridge bundles: {held_out + 1}/{len(personas)}", flush=True)
    if alpha_mismatches:
        raise RuntimeError(f"Held-out alpha selection mismatches: {alpha_mismatches[:5]}")
    audit = {
        "persona_count": len(models),
        "training_count_per_model": 274,
        "each_bundle_names_its_excluded_persona": all(name == value["excluded_persona"] for name, value in models.items()),
        "selected_alpha_mismatch_count": len(alpha_mismatches),
        "maximum_unedited_lopo_reproduction_error": max(errors),
        "strict_tolerance": 1e-9,
        "passed": max(errors) <= 1e-9 and not alpha_mismatches,
    }
    if not audit["passed"]:
        raise RuntimeError(f"Held-out bundle audit failed: {audit}")
    payload = {
        "schema_version": "1.0",
        "model_family": "per-persona raw-cosine Ridge",
        "construction": "For persona index i, exact validated LOPO procedure: remove i; tune Ridge alpha by shuffled 4-fold CV on 274 profiles with random_state=10000+i; fit fold-local feature and target StandardScalers; export direct raw-profile-to-PC coefficients.",
        "source_procedure": relative(RUNNER_PATH),
        "trait_feature_names": inputs["traits"],
        "audit": audit,
        "models": models,
    }
    return payload, audit


def predict_direct(profile: list[float], model: dict[str, Any]) -> list[float]:
    direct = model.get("portable_prediction", {}).get("raw_input_to_pc", model.get("raw_input_to_pc"))
    coefficients = np.asarray(direct["coefficients"], dtype=np.float64)
    intercepts = np.asarray(direct["intercepts"], dtype=np.float64)
    return (coefficients @ np.asarray(profile, dtype=np.float64) + intercepts).tolist()


def build_reference_cases(inputs: dict[str, Any], models: dict[str, Any]) -> dict[str, Any]:
    cli = load_module(CLI_PATH, "canonical_trait_profile_cli")
    ood = inputs["ood"]
    traits = inputs["traits"]
    references = ood["percentile_reference"]["sorted_raw_values_by_trait"]
    indices = np.linspace(0, len(inputs["personas"]) - 1, 30, dtype=int).tolist()
    cases = []
    for case_number, persona_index in enumerate(indices):
        persona = inputs["personas"][persona_index]
        profile = inputs["x"][persona_index].tolist()
        trait_indices = [
            (case_number * 37 + 3) % len(traits),
            (case_number * 71 + 41) % len(traits),
            (case_number * 101 + 89) % len(traits),
        ]
        deltas = [10.0, -10.0, 6.5]
        edits = []
        modified = list(profile)
        for trait_index, delta in zip(trait_indices, deltas):
            before = cli.percentile_of_reference(profile[trait_index], references[trait_index])
            requested = before + delta
            after = min(max(requested, 0.0), 100.0)
            raw = cli.empirical_quantile(references[trait_index], after)
            modified[trait_index] = raw
            edits.append({
                "trait": traits[trait_index],
                "trait_index": trait_index,
                "baseline_percentile": before,
                "delta_percentile": delta,
                "requested_percentile": requested,
                "modified_percentile": after,
                "modified_raw_cosine": raw,
                "clamped": requested != after,
            })
        model = models[persona]
        cases.append({
            "case_id": f"modified_{case_number:02d}_{persona}",
            "persona": persona,
            "edits": edits,
            "expected_prediction": predict_direct(modified, model),
            "expected_ood": cli.ood_diagnostic(modified, ood, exclude_name=persona),
        })
    return {
        "schema_version": "1.0",
        "case_count": len(cases),
        "construction": "Thirty deterministic three-trait percentile edits evaluated with predict_trait_profile.py conversion, held-out direct Ridge bundle, and canonical OOD diagnostic.",
        "cases": cases,
    }


def build_data(inputs: dict[str, Any], saved_lopo: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "source_model": "Qwen/Qwen3-32B",
        "personas": [
            {
                "name": name,
                "cluster": cluster,
                "coordinate": coordinate.tolist(),
                "profile": profile.tolist(),
                "saved_lopo_prediction": saved_lopo[name]["prediction"],
            }
            for name, cluster, coordinate, profile in zip(
                inputs["personas"], inputs["clusters"], inputs["coordinates"], inputs["x"]
            )
        ],
        "traits": [
            {"name": name, "definition": inputs["definitions"].get(name)} for name in inputs["traits"]
        ],
        "clusters": list(dict.fromkeys(inputs["clusters"])),
        "all_persona_predictor": inputs["ridge"],
        "ood_reference": inputs["ood"],
        "error_reference": inputs["ridge"]["validation_summary"]["empirical_error_reference"],
        "scientific_labels": {
            "profile": "Activation-derived same-space Qwen trait affinity; percentile relative to 275 canonical Qwen personas.",
            "existing_persona_prediction": "Persona-held-out Ridge prediction.",
            "edited_prediction": "Predicted counterfactual location, not observed model behavior or a causal intervention.",
            "ood": "Heuristic profile-geometry diagnostic, not a calibrated probability.",
        },
    }


def source_manifest(inputs: dict[str, Any], audit: dict[str, Any], canonical_explorer_hash: str) -> dict[str, Any]:
    sources = [
        PREDICTOR_DIR / "trait_profile_pc_predictor_report.md",
        RIDGE_JSON,
        LOPO_CSV,
        OOD_JSON,
        CLI_PATH,
        RUNNER_PATH,
        PREDICTOR_DIR / "source_manifest.json",
        CANONICAL_MATRIX,
        GEOMETRY,
        DEFINITIONS,
        CANONICAL_EXPLORER,
        REPO_ROOT / "research/visualizations/scripts/build_geometry_viz.py",
        REPO_ROOT / "research/outputs/persona_trait_ridge_plots/persona_trait_ridges.html",
        REPO_ROOT / "research/outputs/persona_trait_surface_viewer/persona_trait_surface_viewer.html",
    ]
    return {
        "schema_version": "1.0",
        "generation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "generation_commit": git_output("rev-parse", "HEAD"),
        "branch": git_output("branch", "--show-current"),
        "model_used": "GPT-5.5",
        "source_model": "Qwen/Qwen3-32B",
        "new_model_inference": False,
        "new_activation_extraction": False,
        "gpu_used": False,
        "runpod_used": False,
        "external_model_api_used": False,
        "implementation_choice": "Active companion explorer; canonical generated explorer remains byte-identical because its builder only replaces embedded geometry and parallel edits to the monolithic generated HTML would not be safely reproducible.",
        "canonical_explorer_sha256_before_and_after": canonical_explorer_hash,
        "input_integrity": {
            "persona_count": len(inputs["personas"]),
            "unique_persona_count": len(set(inputs["personas"])),
            "trait_count": len(inputs["traits"]),
            "unique_trait_count": len(set(inputs["traits"])),
            "finite_profiles": bool(np.isfinite(inputs["x"]).all()),
            "finite_coordinates": bool(np.isfinite(inputs["coordinates"]).all()),
            "feature_order_exactly_matches_predictor": inputs["traits"] == inputs["ridge"]["trait_feature_names"],
        },
        "held_out_bundle_audit": audit,
        "dependencies": [
            {"path": relative(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in sources
        ],
    }


def build_html(data: dict[str, Any], lopo_payload: dict[str, Any]) -> None:
    template = (HERE / "viewer_template.html").read_text(encoding="utf-8")
    core = (HERE / "trait_profile_geometry_core.js").read_text(encoding="utf-8")
    viewer = (HERE / "viewer.js").read_text(encoding="utf-8")
    app_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    model_json = json.dumps(lopo_payload["models"], separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*__APP_DATA__*/", f"window.TRAIT_PROFILE_GEOMETRY_DATA={app_json};")
    html = html.replace("/*__LOPO_MODELS__*/", f"window.TRAIT_PROFILE_LOPO_MODELS={model_json};")
    html = html.replace("/*__CORE_JS__*/", core).replace("/*__VIEWER_JS__*/", viewer)
    if any(token in html for token in ("/*__APP_DATA__*/", "/*__LOPO_MODELS__*/", "/*__CORE_JS__*/", "/*__VIEWER_JS__*/")):
        raise RuntimeError("Generated HTML contains an unreplaced source token")
    GENERATED_HTML_PATH.write_text(html, encoding="utf-8")


def write_inventory() -> None:
    paths = sorted(
        path for path in HERE.iterdir()
        if path.is_file() and path.name != INVENTORY_PATH.name and not path.name.startswith(".")
    )
    with INVENTORY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "status", "sha256", "size_bytes", "canonical_raw_url", "branch_raw_url"],
            lineterminator="\n",
        )
        writer.writeheader()
        for path in paths:
            rel = relative(path)
            writer.writerow({
                "path": rel,
                "status": "active",
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
                "canonical_raw_url": RAW_BASE + rel,
                "branch_raw_url": BRANCH_RAW_BASE + rel,
            })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument("--reuse-lopo", action="store_true")
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    if args.inventory_only:
        write_inventory()
        return

    canonical_explorer_hash = sha256(CANONICAL_EXPLORER)
    inputs = load_inputs()
    saved_lopo = load_saved_lopo(inputs["personas"])
    if args.reuse_lopo and LOPO_MODELS_PATH.exists():
        lopo_payload = read_json(LOPO_MODELS_PATH)
        audit = lopo_payload["audit"]
        if list(lopo_payload["models"]) != inputs["personas"]:
            raise RuntimeError("Reusable held-out model bundle order is stale")
    else:
        lopo_payload, audit = fit_lopo_models(inputs, args.n_jobs)
        write_json(LOPO_MODELS_PATH, lopo_payload)
    data = build_data(inputs, saved_lopo)
    references = build_reference_cases(inputs, lopo_payload["models"])
    write_json(DATA_PATH, data)
    write_json(REFERENCE_CASES_PATH, references)
    write_json(SOURCE_MANIFEST_PATH, source_manifest(inputs, audit, canonical_explorer_hash))
    build_html(data, lopo_payload)
    if sha256(CANONICAL_EXPLORER) != canonical_explorer_hash:
        raise RuntimeError("Canonical explorer changed during companion generation")
    write_inventory()
    print(json.dumps({
        "output": relative(GENERATED_HTML_PATH),
        "personas": len(inputs["personas"]),
        "traits": len(inputs["traits"]),
        "held_out_models": len(lopo_payload["models"]),
        "reference_cases": len(references["cases"]),
        "maximum_unedited_lopo_reproduction_error": audit["maximum_unedited_lopo_reproduction_error"],
        "canonical_explorer_sha256": canonical_explorer_hash,
    }, indent=2))


if __name__ == "__main__":
    main()
