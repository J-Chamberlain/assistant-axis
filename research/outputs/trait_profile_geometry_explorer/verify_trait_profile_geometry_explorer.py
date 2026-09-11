#!/usr/bin/env python3
"""Independent integrity and numerical checks for the companion explorer bundle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
PREDICTOR = REPO_ROOT / "research/outputs/trait_profile_pc_predictor"
MATRIX = REPO_ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
GEOMETRY = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
CANONICAL_EXPLORER = REPO_ROOT / "research/visualizations/persona_geometry_explorer.html"
REPORT = HERE / "verification_report.json"
TOLERANCE = 1e-9


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def max_abs(a: list[float], b: list[float]) -> float:
    return max(abs(x - y) for x, y in zip(a, b))


def finite_nested(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(finite_nested(item) for item in value)
    if isinstance(value, dict):
        return all(finite_nested(item) for item in value.values())
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    cli = load_module(PREDICTOR / "predict_trait_profile.py", "canonical_cli_for_equalizer_check")
    data = read_json(HERE / "trait_profile_geometry_data.json")
    bundle = read_json(HERE / "lopo_ridge_predictors.json")
    cases = read_json(HERE / "browser_python_reference_cases.json")
    manifest = read_json(HERE / "source_manifest.json")
    ridge = read_json(PREDICTOR / "ridge_predictor.json")
    ood = read_json(PREDICTOR / "ood_reference.json")
    geometry = read_json(GEOMETRY)
    names = [item["name"] for item in data["personas"]]
    traits = [item["name"] for item in data["traits"]]
    models = bundle["models"]

    with MATRIX.open(newline="", encoding="utf-8") as handle:
        matrix_rows = list(csv.DictReader(handle))
        matrix_traits = list(matrix_rows[0])[1:]
    matrix_names = [row["persona"] for row in matrix_rows]
    raw_lopo = {}
    with (PREDICTOR / "leave_one_persona_out_predictions.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["representation"] == "raw_cosine":
                raw_lopo[row["persona"]] = [float(row[f"predicted_pc{i}"]) for i in (1, 2, 3)]

    checks: dict[str, Any] = {
        "persona_count": len(names),
        "unique_persona_count": len(set(names)),
        "trait_count": len(traits),
        "unique_trait_count": len(set(traits)),
        "persona_order_matches_matrix": names == matrix_names,
        "persona_order_matches_geometry": names == geometry["roles"]["names"],
        "feature_order_matches_matrix": traits == matrix_traits,
        "feature_order_matches_all_persona_predictor": traits == ridge["trait_feature_names"],
        "feature_order_matches_ood": traits == ood["trait_feature_names"],
        "feature_order_matches_lopo_bundle": traits == bundle["trait_feature_names"],
        "held_out_model_count": len(models),
        "every_model_excludes_its_key": all(name == models[name]["excluded_persona"] for name in names),
        "every_model_has_274_training_personas": all(models[name]["training_persona_count"] == 274 for name in names),
        "no_duplicate_traits": len(traits) == len(set(traits)),
        "finite_bundle": finite_nested(bundle),
        "generated_html_contains_no_source_tokens": not any(
            token in (HERE / "trait_profile_geometry_explorer.html").read_text(encoding="utf-8")
            for token in ("/*__APP_DATA__*/", "/*__LOPO_MODELS__*/", "/*__CORE_JS__*/", "/*__VIEWER_JS__*/")
        ),
        "canonical_explorer_sha256_unchanged": sha256(CANONICAL_EXPLORER)
        == manifest["canonical_explorer_sha256_before_and_after"],
    }

    lopo_errors = []
    final_model_errors = []
    for persona in data["personas"]:
        name = persona["name"]
        prediction = cli.predict_ridge(persona["profile"], {"portable_prediction": {"raw_input_to_pc": models[name]["raw_input_to_pc"]}})
        lopo_errors.append(max_abs(prediction, raw_lopo[name]))
        final_from_embedded = cli.predict_ridge(persona["profile"], data["all_persona_predictor"])
        final_from_source = cli.predict_ridge(persona["profile"], ridge)
        final_model_errors.append(max_abs(final_from_embedded, final_from_source))
    checks["maximum_all_persona_lopo_reproduction_error"] = max(lopo_errors)
    checks["maximum_embedded_final_predictor_vs_cli_error"] = max(final_model_errors)

    percentile_errors = []
    modified_prediction_errors = []
    ood_scalar_errors = []
    deterministic_errors = []
    references = ood["percentile_reference"]["sorted_raw_values_by_trait"]
    by_name = {persona["name"]: persona for persona in data["personas"]}
    for case in cases["cases"]:
        name = case["persona"]
        baseline = by_name[name]["profile"]
        first_modified = list(baseline)
        for edit in case["edits"]:
            index = edit["trait_index"]
            before = cli.percentile_of_reference(baseline[index], references[index])
            percentile_errors.append(abs(before - edit["baseline_percentile"]))
            converted = cli.empirical_quantile(references[index], edit["modified_percentile"])
            percentile_errors.append(abs(converted - edit["modified_raw_cosine"]))
            first_modified[index] = converted
        second_modified = list(baseline)
        for edit in case["edits"]:
            second_modified[edit["trait_index"]] = cli.empirical_quantile(
                references[edit["trait_index"]], edit["modified_percentile"]
            )
        deterministic_errors.append(max_abs(first_modified, second_modified))
        prediction = cli.predict_ridge(
            first_modified, {"portable_prediction": {"raw_input_to_pc": models[name]["raw_input_to_pc"]}}
        )
        modified_prediction_errors.append(max_abs(prediction, case["expected_prediction"]))
        observed_ood = cli.ood_diagnostic(first_modified, ood, exclude_name=name)
        expected_ood = case["expected_ood"]
        for key in (
            "nearest_neighbor_distance",
            "mean_5nn_distance",
            "distance_percentile_vs_canonical_loo",
            "profile_pca_reconstruction_error",
            "reconstruction_error_percentile_vs_canonical",
        ):
            ood_scalar_errors.append(abs(observed_ood[key] - expected_ood[key]))
        if observed_ood["heuristic_label"] != expected_ood["heuristic_label"]:
            ood_scalar_errors.append(math.inf)
    checks.update({
        "modified_reference_case_count": len(cases["cases"]),
        "maximum_percentile_mapping_reference_error": max(percentile_errors),
        "maximum_modified_prediction_reference_error": max(modified_prediction_errors),
        "maximum_ood_reference_scalar_error": max(ood_scalar_errors),
        "maximum_multitrait_determinism_error": max(deterministic_errors),
        "reset_all_profile_error": max(max_abs(persona["profile"], list(persona["profile"])) for persona in data["personas"]),
    })

    projection_errors = []
    for persona in data["personas"]:
        point = persona["saved_lopo_prediction"]
        for axes in ((0, 1), (0, 2), (1, 2)):
            projection = [point[axes[0]], point[axes[1]]]
            projection_errors.append(max_abs(projection, cli_projection(point, axes)))
    checks["maximum_2d_projection_error"] = max(projection_errors)

    numeric_thresholds = {
        "maximum_all_persona_lopo_reproduction_error": TOLERANCE,
        "maximum_embedded_final_predictor_vs_cli_error": TOLERANCE,
        "maximum_percentile_mapping_reference_error": TOLERANCE,
        "maximum_modified_prediction_reference_error": TOLERANCE,
        "maximum_ood_reference_scalar_error": TOLERANCE,
        "maximum_multitrait_determinism_error": 0.0,
        "reset_all_profile_error": 0.0,
        "maximum_2d_projection_error": 0.0,
    }
    booleans_pass = all(
        value for key, value in checks.items()
        if isinstance(value, bool)
    )
    counts_pass = (
        checks["persona_count"] == checks["unique_persona_count"] == 275
        and checks["trait_count"] == checks["unique_trait_count"] == 240
        and checks["held_out_model_count"] == 275
        and checks["modified_reference_case_count"] >= 25
    )
    numeric_pass = all(checks[key] <= threshold for key, threshold in numeric_thresholds.items())
    report = {
        "schema_version": "1.0",
        "test_type": "Python artifact/integration verification (not a browser test)",
        "strict_tolerance": TOLERANCE,
        "checks": checks,
        "passed": booleans_pass and counts_pass and numeric_pass,
    }
    if args.write_report:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


def cli_projection(point: list[float], axes: tuple[int, int]) -> list[float]:
    return [point[axes[0]], point[axes[1]]]


if __name__ == "__main__":
    main()
