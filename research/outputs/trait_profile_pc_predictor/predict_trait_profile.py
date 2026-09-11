#!/usr/bin/env python3
"""Predict canonical Qwen persona PC1/PC2/PC3 from a complete trait profile.

This CLI performs no model inference. It evaluates transparent JSON model bundles
generated from the existing 275-persona by 240-trait activation-cosine matrix.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL = HERE / "ridge_predictor.json"
DEFAULT_OOD = HERE / "ood_reference.json"
DEFAULT_COMPARISON = HERE / "comparison_predictors.json"
DEFAULT_MATRIX = REPO_ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
DEFAULT_GEOMETRY = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
DEFAULT_LOPO = HERE / "leave_one_persona_out_predictions.csv"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def euclidean(a: Iterable[float], b: Iterable[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def percentile_of_reference(value: float, sorted_reference: list[float]) -> float:
    if not sorted_reference:
        return math.nan
    if len(sorted_reference) == 1:
        return 100.0 if value >= sorted_reference[0] else 0.0
    left = bisect.bisect_left(sorted_reference, value)
    right = bisect.bisect_right(sorted_reference, value)
    average_index = (left + right - 1) / 2.0
    return 100.0 * min(max(average_index / (len(sorted_reference) - 1), 0.0), 1.0)


def empirical_quantile(sorted_values: list[float], percentile: float) -> float:
    if not 0.0 <= percentile <= 100.0:
        raise ValueError(f"Percentile must be in [0, 100], got {percentile}")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = percentile / 100.0 * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return float((1.0 - weight) * sorted_values[lower] + weight * sorted_values[upper])


def read_matrix(path: Path, feature_names: list[str]) -> tuple[list[str], dict[str, list[float]]]:
    profiles: dict[str, list[float]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or reader.fieldnames[0] != "persona":
            raise ValueError(f"Expected first matrix column to be persona: {path}")
        observed = reader.fieldnames[1:]
        if observed != feature_names:
            raise ValueError("Matrix feature order does not match ridge_predictor.json")
        for row in reader:
            name = row["persona"]
            if name in profiles:
                raise ValueError(f"Duplicate persona in matrix: {name}")
            values = [float(row[name_]) for name_ in feature_names]
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"Nonfinite profile for persona: {name}")
            profiles[name] = values
    return list(profiles), profiles


def validate_named_profile(profile: dict[str, Any], feature_names: list[str]) -> list[float]:
    observed = set(profile)
    expected = set(feature_names)
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        raise ValueError(
            f"Profile must contain exactly {len(feature_names)} unique named traits; "
            f"missing={missing[:10]}, extra={extra[:10]}"
        )
    values = [float(profile[name]) for name in feature_names]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Profile contains a nonfinite value")
    return values


def read_external_profile(path: Path, feature_names: list[str]) -> tuple[list[float], str | None]:
    if path.suffix.lower() == ".json":
        payload = load_json(path)
        declared_format = None
        if isinstance(payload, dict) and "traits" in payload:
            declared_format = payload.get("format")
            payload = payload["traits"]
        if not isinstance(payload, dict):
            raise ValueError("JSON profile must be a trait-to-value object or contain a traits object")
        return validate_named_profile(payload, feature_names), declared_format

    if path.suffix.lower() != ".csv":
        raise ValueError("External profile must be CSV or JSON")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError("CSV profile is empty")
    header = rows[0]
    if header[:2] in (["trait", "value"], ["name", "value"]):
        named: dict[str, float] = {}
        for row in rows[1:]:
            if len(row) < 2:
                raise ValueError(f"Malformed trait/value row: {row}")
            if row[0] in named:
                raise ValueError(f"Duplicate trait in CSV profile: {row[0]}")
            named[row[0]] = float(row[1])
        return validate_named_profile(named, feature_names), None
    if header != feature_names:
        raise ValueError("Wide CSV header must contain the 240 traits in exact model order")
    if len(rows) != 2:
        raise ValueError("Wide CSV profile must contain exactly one data row")
    return [float(value) for value in rows[1]], None


def convert_percentile_profile(values: list[float], ood: dict[str, Any]) -> list[float]:
    references = ood["percentile_reference"]["sorted_raw_values_by_trait"]
    converted = []
    for value, sorted_values in zip(values, references):
        if not 0.0 <= value <= 100.0:
            raise ValueError(f"Percentile profile values must be in [0, 100], got {value}")
        converted.append(empirical_quantile(sorted_values, value))
    return converted


def predict_ridge(profile: list[float], model: dict[str, Any]) -> list[float]:
    direct = model["portable_prediction"]["raw_input_to_pc"]
    coefficients = direct["coefficients"]
    intercepts = direct["intercepts"]
    return [dot(row, profile) + intercept for row, intercept in zip(coefficients, intercepts)]


def standardized_features(profile: list[float], transform: dict[str, Any]) -> list[float]:
    return [
        (value - mean) / scale
        for value, mean, scale in zip(profile, transform["mean"], transform["scale"])
    ]


def predict_comparison(profile: list[float], model: dict[str, Any]) -> list[float]:
    kind = model["model_type"]
    if kind in {"Ridge", "PLSRegression"}:
        direct = model["portable_prediction"]["raw_input_to_pc"]
        return [dot(row, profile) + intercept for row, intercept in zip(direct["coefficients"], direct["intercepts"])]

    x = standardized_features(profile, model["feature_transform"])
    target_mean = model["target_transform"]["mean"]
    target_scale = model["target_transform"]["scale"]
    if kind == "KernelRidgeRBF":
        gamma = model["gamma"]
        standardized_prediction = [0.0, 0.0, 0.0]
        for train_x, dual in zip(model["training_features_transformed"], model["dual_coefficients"]):
            kernel = math.exp(-gamma * sum((a - b) ** 2 for a, b in zip(x, train_x)))
            for index in range(3):
                standardized_prediction[index] += kernel * dual[index]
    elif kind == "KNeighborsRegressor":
        distances = sorted(
            (euclidean(x, train_x), index)
            for index, train_x in enumerate(model["training_features_transformed"])
        )[: model["n_neighbors"]]
        # JSON round-tripping can move a mathematically exact standardized row by
        # a few ulps. Treat sub-1e-10 distances as exact, matching sklearn's
        # zero-distance behavior for a query identical to a training profile.
        exact = [index for distance, index in distances if distance <= 1e-10]
        if exact:
            standardized_prediction = [
                sum(model["training_targets_standardized"][index][axis] for index in exact) / len(exact)
                for axis in range(3)
            ]
        else:
            weights = [1.0 / max(distance, 1e-15) for distance, _ in distances]
            denominator = sum(weights)
            standardized_prediction = [
                sum(weight * model["training_targets_standardized"][index][axis] for weight, (_, index) in zip(weights, distances))
                / denominator
                for axis in range(3)
            ]
    else:
        raise ValueError(f"Unsupported comparison model type: {kind}")
    return [mean + scale * value for mean, scale, value in zip(target_mean, target_scale, standardized_prediction)]


def project_profile(profile: list[float], ood: dict[str, Any]) -> list[float]:
    scaler = ood["feature_standardizer"]
    scaled = standardized_features(profile, scaler)
    pca = ood["profile_pca"]
    centered = [value - mean for value, mean in zip(scaled, pca["mean"])]
    return [dot(component, centered) for component in pca["components"]]


def profile_pca_reconstruction_error(profile: list[float], ood: dict[str, Any]) -> float:
    scaler = ood["feature_standardizer"]
    scaled = standardized_features(profile, scaler)
    pca = ood["profile_pca"]
    centered = [value - mean for value, mean in zip(scaled, pca["mean"])]
    scores = [dot(component, centered) for component in pca["components"]]
    reconstructed = [
        sum(score * component[index] for score, component in zip(scores, pca["components"]))
        for index in range(len(centered))
    ]
    return euclidean(centered, reconstructed)


def ood_diagnostic(
    profile: list[float],
    ood: dict[str, Any],
    top_k: int = 5,
    exclude_name: str | None = None,
) -> dict[str, Any]:
    score = project_profile(profile, ood)
    names = ood["training_personas"]
    training_scores = ood["training_profile_pca_scores"]
    distances = sorted(
        (euclidean(score, train_score), name)
        for name, train_score in zip(names, training_scores)
        if name != exclude_name
    )
    if not distances:
        raise ValueError("No training profiles remain for OOD comparison")
    neighbors = [{"persona": name, "distance": distance} for distance, name in distances[:top_k]]
    k5 = min(5, len(distances))
    mean_5nn = sum(distance for distance, _ in distances[:k5]) / k5
    distance_percentile = percentile_of_reference(mean_5nn, ood["reference_distances"]["loo_mean_5nn_sorted"])
    reconstruction_error = profile_pca_reconstruction_error(profile, ood)
    reconstruction_percentile = percentile_of_reference(
        reconstruction_error,
        ood["reference_distances"]["profile_pca_reconstruction_error_sorted"],
    )
    ranges = ood["training_feature_ranges"]
    outside = [
        name
        for name, value, minimum, maximum in zip(ood["trait_feature_names"], profile, ranges["min"], ranges["max"])
        if value < minimum or value > maximum
    ]
    if distance_percentile > 99.0 or reconstruction_percentile > 99.0 or len(outside) >= 5:
        label = "out-of-distribution"
    elif distance_percentile > 90.0 or reconstruction_percentile > 90.0 or outside:
        label = "edge-of-distribution"
    else:
        label = "in-distribution"
    return {
        "heuristic_label": label,
        "nearest_neighbor_distance": distances[0][0],
        "mean_5nn_distance": mean_5nn,
        "distance_percentile_vs_canonical_loo": distance_percentile,
        "profile_pca_reconstruction_error": reconstruction_error,
        "reconstruction_error_percentile_vs_canonical": reconstruction_percentile,
        "traits_outside_training_range_count": len(outside),
        "traits_outside_training_range": outside,
        "nearest_personas": neighbors,
        "note": "Heuristic profile-geometry diagnostic, not a calibrated probability.",
    }


def parse_delta_spec(spec: str | None, feature_names: list[str]) -> dict[str, float]:
    if not spec:
        return {}
    deltas: dict[str, float] = {}
    for item in spec.split(","):
        if "=" not in item:
            raise ValueError(f"Malformed delta item {item!r}; expected trait=delta")
        name, value = item.split("=", 1)
        name = name.strip()
        if name not in feature_names:
            raise ValueError(f"Unknown trait in delta specification: {name}")
        if name in deltas:
            raise ValueError(f"Duplicate trait in delta specification: {name}")
        deltas[name] = float(value)
    return deltas


def apply_percentile_deltas(
    profile: list[float],
    deltas: dict[str, float],
    feature_names: list[str],
    ood: dict[str, Any],
) -> tuple[list[float], list[dict[str, Any]], list[dict[str, Any]]]:
    modified = list(profile)
    changes = []
    clamps = []
    references = ood["percentile_reference"]["sorted_raw_values_by_trait"]
    for trait, delta in deltas.items():
        index = feature_names.index(trait)
        before_raw = profile[index]
        before_percentile = percentile_of_reference(before_raw, references[index])
        requested = before_percentile + delta
        after_percentile = min(max(requested, 0.0), 100.0)
        if after_percentile != requested:
            clamps.append(
                {
                    "trait": trait,
                    "requested_percentile": requested,
                    "clamped_percentile": after_percentile,
                }
            )
        after_raw = empirical_quantile(references[index], after_percentile)
        modified[index] = after_raw
        changes.append(
            {
                "trait": trait,
                "delta_percentile": delta,
                "baseline_percentile": before_percentile,
                "requested_percentile": requested,
                "modified_percentile": after_percentile,
                "baseline_raw_cosine": before_raw,
                "modified_raw_cosine": after_raw,
            }
        )
    return modified, changes, clamps


def load_actual_coordinates(path: Path) -> dict[str, list[float]]:
    geometry = load_json(path)
    return {
        name: [float(value) for value in coordinate]
        for name, coordinate in zip(geometry["roles"]["names"], geometry["roles"]["pca3d"])
    }


def load_lopo(path: Path, persona: str, representation: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["persona"] == persona and row["representation"] == representation:
                return {
                    "predicted_pc1": float(row["predicted_pc1"]),
                    "predicted_pc2": float(row["predicted_pc2"]),
                    "predicted_pc3": float(row["predicted_pc3"]),
                    "raw_3d_error": float(row["raw_3d_error"]),
                    "standardized_3d_error": float(row["standardized_3d_error"]),
                    "selected_alpha": float(row["selected_alpha"]),
                }
    return None


def model_disagreement(profile: list[float], comparison_path: Path) -> dict[str, Any] | None:
    if not comparison_path.exists():
        return None
    bundle = load_json(comparison_path)
    predictions = {
        model["name"]: predict_comparison(profile, model)
        for model in bundle["models"]
    }
    axis_ranges = [
        max(values) - min(values)
        for values in zip(*predictions.values())
    ]
    pairwise = []
    names = list(predictions)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pairwise.append(euclidean(predictions[left], predictions[right]))
    return {
        "predictions": predictions,
        "per_pc_range": axis_ranges,
        "maximum_pairwise_3d_disagreement": max(pairwise) if pairwise else 0.0,
    }


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    model = load_json(args.model)
    ood = load_json(args.ood_reference)
    feature_names = model["trait_feature_names"]
    persona_names, profiles = read_matrix(args.matrix, feature_names)
    del persona_names

    if bool(args.persona) == bool(args.profile):
        raise ValueError("Specify exactly one of --persona or --profile")
    source_format = "raw-cosine"
    source_persona = None
    if args.persona:
        if args.persona not in profiles:
            raise ValueError(f"Unknown persona: {args.persona}")
        source_persona = args.persona
        profile = profiles[args.persona]
        source = {"mode": "existing_persona", "persona": args.persona}
    else:
        profile, declared_format = read_external_profile(args.profile, feature_names)
        profile_format = declared_format or args.profile_format
        if profile_format not in {"raw-cosine", "percentile"}:
            raise ValueError(f"Unknown profile format: {profile_format}")
        source_format = profile_format
        if profile_format == "percentile":
            profile = convert_percentile_profile(profile, ood)
        source = {"mode": "external_profile", "path": str(args.profile), "declared_format": profile_format}

    deltas = parse_delta_spec(args.delta_percentile, feature_names)
    if deltas and not source_persona and source_format != "percentile":
        raise ValueError("--delta-percentile requires --persona or a percentile-format profile")

    baseline_prediction = predict_ridge(profile, model)
    baseline_ood = ood_diagnostic(profile, ood, args.top_k, exclude_name=source_persona)
    actual = load_actual_coordinates(args.geometry).get(source_persona) if source_persona else None
    result: dict[str, Any] = {
        "source": source,
        "source_profile_format": source_format,
        "predictor": {
            "model_type": model["model_type"],
            "input_representation": model["input_representation"],
            "ridge_alpha": model["ridge_alpha"],
        },
        "predicted_pc": dict(zip(["PC1", "PC2", "PC3"], baseline_prediction)),
        "actual_pc": dict(zip(["PC1", "PC2", "PC3"], actual)) if actual is not None else None,
        "lopo_reference": load_lopo(args.lopo, source_persona, model["input_representation"]) if source_persona else None,
        "nearest_profile_and_ood": baseline_ood,
        "empirical_held_out_error_reference_from_existing_personas": model["validation_summary"]["empirical_error_reference"],
        "model_disagreement": model_disagreement(profile, args.comparison_models),
    }

    if deltas:
        modified, changes, clamps = apply_percentile_deltas(profile, deltas, feature_names, ood)
        modified_prediction = predict_ridge(modified, model)
        delta_pc = [after - before for after, before in zip(modified_prediction, baseline_prediction)]
        result["counterfactual"] = {
            "label": "PREDICTED COUNTERFACTUAL LOCATION",
            "trait_changes": changes,
            "clamps": clamps,
            "baseline_predicted_pc": dict(zip(["PC1", "PC2", "PC3"], baseline_prediction)),
            "modified_predicted_pc": dict(zip(["PC1", "PC2", "PC3"], modified_prediction)),
            "delta_pc": dict(zip(["PC1", "PC2", "PC3"], delta_pc)),
            "displacement_3d": math.sqrt(sum(value * value for value in delta_pc)),
            "baseline_nearest_profile_and_ood": baseline_ood,
            "modified_nearest_profile_and_ood": ood_diagnostic(modified, ood, args.top_k),
            "modified_model_disagreement": model_disagreement(modified, args.comparison_models),
            "empirical_held_out_error_reference_from_existing_personas": model["validation_summary"]["empirical_error_reference"],
            "interpretation_boundary": "This is a model prediction under a profile edit, not observed Qwen behavior and not a causal trait intervention.",
        }
    return result


def fmt_pc(values: dict[str, float] | None) -> str:
    if values is None:
        return "not available"
    return ", ".join(f"{name}={value:.4f}" for name, value in values.items())


def print_human(result: dict[str, Any]) -> None:
    print("Trait-profile -> canonical persona-PC prediction")
    print(f"Source: {json.dumps(result['source'], sort_keys=True)}")
    print(f"Source profile format: {result['source_profile_format']}")
    print(f"Final Ridge prediction: {fmt_pc(result['predicted_pc'])}")
    if result["actual_pc"] is not None:
        print(f"Actual canonical coordinate: {fmt_pc(result['actual_pc'])}")
    if result["lopo_reference"] is not None:
        lopo = result["lopo_reference"]
        print(
            "LOPO prediction: "
            f"PC1={lopo['predicted_pc1']:.4f}, PC2={lopo['predicted_pc2']:.4f}, PC3={lopo['predicted_pc3']:.4f}; "
            f"raw 3D error={lopo['raw_3d_error']:.4f}, standardized 3D error={lopo['standardized_3d_error']:.4f}"
        )
    diagnostic = result["nearest_profile_and_ood"]
    nearest = ", ".join(f"{row['persona']} ({row['distance']:.3f})" for row in diagnostic["nearest_personas"])
    print(
        f"OOD diagnostic: {diagnostic['heuristic_label']}; 5-NN={diagnostic['mean_5nn_distance']:.4f}; "
        f"distance percentile={diagnostic['distance_percentile_vs_canonical_loo']:.1f}; "
        f"reconstruction percentile={diagnostic['reconstruction_error_percentile_vs_canonical']:.1f}; "
        f"outside-range traits={diagnostic['traits_outside_training_range_count']}"
    )
    print(f"Nearest profiles: {nearest}")
    bands = result["empirical_held_out_error_reference_from_existing_personas"]
    print(
        "Empirical held-out error reference from existing personas (q95 absolute): "
        + ", ".join(f"{pc}=+/-{bands[pc]['q95_absolute_error']:.4f}" for pc in ["PC1", "PC2", "PC3"])
    )
    if result["model_disagreement"]:
        disagreement = result["model_disagreement"]
        print(f"Model maximum pairwise 3D disagreement: {disagreement['maximum_pairwise_3d_disagreement']:.4f}")
    if "counterfactual" in result:
        counterfactual = result["counterfactual"]
        print("PREDICTED COUNTERFACTUAL LOCATION")
        print(f"Baseline: {fmt_pc(counterfactual['baseline_predicted_pc'])}")
        print(f"Modified: {fmt_pc(counterfactual['modified_predicted_pc'])}")
        print(f"Delta: {fmt_pc(counterfactual['delta_pc'])}")
        print(f"3D displacement: {counterfactual['displacement_3d']:.4f}")
        if counterfactual["clamps"]:
            print(f"Clamps: {json.dumps(counterfactual['clamps'], sort_keys=True)}")
        modified_ood = counterfactual["modified_nearest_profile_and_ood"]
        print(
            f"Modified OOD diagnostic: {modified_ood['heuristic_label']}; "
            f"5-NN={modified_ood['mean_5nn_distance']:.4f}; "
            f"distance percentile={modified_ood['distance_percentile_vs_canonical_loo']:.1f}; "
            f"reconstruction percentile={modified_ood['reconstruction_error_percentile_vs_canonical']:.1f}; "
            f"outside-range traits={modified_ood['traits_outside_training_range_count']}"
        )
        print(counterfactual["interpretation_boundary"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persona", help="Existing canonical persona name")
    parser.add_argument("--profile", type=Path, help="Complete named 240-trait CSV or JSON profile")
    parser.add_argument(
        "--profile-format",
        choices=["raw-cosine", "percentile"],
        default="raw-cosine",
        help="Format of an external profile when not declared inside JSON",
    )
    parser.add_argument(
        "--delta-percentile",
        help="Comma-separated deterministic edits, e.g. empathetic=10,agreeable=10,reactive=-10",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--ood-reference", type=Path, default=DEFAULT_OOD)
    parser.add_argument("--comparison-models", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--geometry", type=Path, default=DEFAULT_GEOMETRY)
    parser.add_argument("--lopo", type=Path, default=DEFAULT_LOPO)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.top_k < 1:
        raise ValueError("--top-k must be positive")
    result = build_result(args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
