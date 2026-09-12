#!/usr/bin/env python3
"""Independent integrity, leakage, provenance, and determinism checks for AA-7."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = HERE / "run_human_supported_trait_convergence.py"
VENV_PYTHON = Path(
    "/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/.venv/bin/python"
)
EXPECTED_TRAITS = [
    "adventurous", "altruistic", "forgiving", "grandiose", "impulsive", "manipulative",
    "optimistic", "pessimistic", "traditional", "innovative", "introspective", "judgmental",
]
EXPECTED_SOURCE_HASH = "1cc78b543bf44e636dc8000617c61f0285e8cfc998b33946c38ab164ecdcd5a6"
GENERATED_DETERMINISTIC = [
    "aligned_agreeableness_focal_test.json", "aligned_big_five_directions.csv",
    "aligned_human_supported_trait_directions.csv", "aligned_trait_consensus_summary.csv",
    "comparator_summary.csv", "core_vs_extended_alignment.csv", "feature_budget_context.csv",
    "feature_family_subspace_coverage.csv", "geometry_optimized_k12_selections.csv",
    "human_support_vs_geometric_utility.csv", "human_supported_trait_contributions.csv",
    "human_supported_trait_convergence_report.md", "human_supported_trait_pc_associations.csv",
    "human_supported_trait_redundancy.csv", "human_supported_trait_scores.csv",
    "isotropic_k12_distribution.csv", "local_pc_prediction_per_pc.csv",
    "local_pc_prediction_summary.csv", "persona_span_k12_distribution.csv",
    "primary_decisions.json", "procrustes_alignment_cv.csv", "procrustes_alignment_matrices.json",
    "procrustes_alignment_null.csv", "procrustes_role_residuals.csv",
    "random_real_k12_distribution.csv", "role_family_holdout_summary.csv", "source_manifest.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("aa7_runner_for_verification", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import AA-7 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-deterministic-rerun", action="store_true")
    args = parser.parse_args()
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": json_safe(detail)})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    runner = load_runner()
    models, support, frozen, direct, vector_root, source_checks = runner.load_sources()

    freeze = json.loads((HERE / "human_supported_trait_set_freeze.json").read_text(encoding="utf-8"))
    check("canonical starting SHA frozen", freeze["canonical_starting_sha"] == runner.CANONICAL_STARTING_SHA,
          freeze["canonical_starting_sha"])
    check("exact ordered 12-trait freeze", frozen == EXPECTED_TRAITS, frozen)
    levels = [row["aa1_human_support_level"] for row in freeze["traits"]]
    check("AA-1 support levels are 9 high and 3 moderate",
          levels.count("high") == 9 and levels.count("moderate") == 3,
          {"high": levels.count("high"), "moderate": levels.count("moderate")})
    source_path = REPO / freeze["source_artifact"]
    check("AA-1 canonical source hash", sha256(source_path) == EXPECTED_SOURCE_HASH, sha256(source_path))
    check("AA-1 direct semantic count", len(direct) == 45, len(direct))

    for key, model in models.items():
        check(f"{key} shared role count", len(model.personas) == 275, len(model.personas))
        check(f"{key} shared trait count", len(model.traits) == 240, len(model.traits))
        check(f"{key} AA-3 PC1-PC6 exact reproduction",
              source_checks[key]["aa3_pc1_pc6_max_abs_error"] <= 1e-9,
              source_checks[key]["aa3_pc1_pc6_max_abs_error"])
        check(f"{key} frozen raw-cosine reproduction",
              source_checks[key]["frozen_trait_cosine_matrix_max_abs_error"] <= 1e-10,
              source_checks[key]["frozen_trait_cosine_matrix_max_abs_error"])

    directions = json.loads(
        (REPO / "research/outputs/externally_anchored_big_five/big_five_domain_directions_manifest.json")
        .read_text(encoding="utf-8")
    )["directions"]
    bf_scores = pd.read_csv(REPO / "research/outputs/externally_anchored_big_five/big_five_role_scores.csv")
    bf_scores = bf_scores[bf_scores.construction.eq("human_anchored_strict")]
    max_bf_error = 0.0
    for key, model in models.items():
        for domain in runner.DOMAINS:
            entry = directions[f"{key}__human_anchored_strict__{domain}"]
            raw = base64.b64decode(entry["vector_base64"])
            check(f"{key}/{domain} AA-2 direction byte hash", hashlib.sha256(raw).hexdigest() == entry["sha256"], entry["sha256"])
            direction = np.frombuffer(raw, dtype="<f4").astype(np.float64)
            saved = bf_scores[(bf_scores.model == key) & (bf_scores.domain == domain)].set_index("persona")
            expected = saved.loc[model.personas, "raw_projection_score"].to_numpy(float)
            max_bf_error = max(max_bf_error, float(np.max(np.abs(model.role_unit @ direction - expected))))
    check("AA-2 strict Big Five directions reproduce saved role scores", max_bf_error <= 2e-7, max_bf_error)

    for protocol, splits in {
        "fixed_5fold": runner.kfold_splits(275, 42),
        "leave_one_persona_out": runner.lopo_splits(275),
        "role_family_holdout": runner.family_splits(models["qwen"].clusters),
    }.items():
        valid = all(
            len(set(map(int, split["train_idx"])).intersection(map(int, split["test_idx"]))) == 0
            and len(split["train_idx"]) + len(split["test_idx"]) == 275
            for split in splits
        )
        check(f"{protocol} outer train/test separation", valid, len(splits))

    selection = pd.read_csv(HERE / "geometry_optimized_k12_selections.csv")
    aa4 = pd.read_csv(REPO / "research/outputs/qwen_trait_sparsity_prediction/nested_forward_selection_paths.csv")
    reproduced = selection[
        (selection.model_key == "qwen") & (selection.scope == "core")
        & (selection.outer_fold == "kfold_42_0")
    ].sort_values("entry_rank")
    canonical = aa4[(aa4.repeat == 0) & (aa4.outer_seed == 42) & (aa4.outer_fold == 0)] \
        .sort_values("entry_rank").head(12)
    path_same = reproduced.trait.tolist() == canonical.trait.tolist()
    alpha_same = np.allclose(reproduced.selected_alpha.to_numpy(float), canonical.selected_alpha.to_numpy(float), rtol=0, atol=0)
    check("AA-4 nested optimized k=12 method/path reproduction", path_same and alpha_same,
          {"traits_match": path_same, "alphas_match": bool(alpha_same)})

    random_real = pd.read_csv(HERE / "random_real_k12_distribution.csv")
    isotropic = pd.read_csv(HERE / "isotropic_k12_distribution.csv")
    persona = pd.read_csv(HERE / "persona_span_k12_distribution.csv")
    for label, frame in {"random-real": random_real, "isotropic": isotropic, "persona-span": persona}.items():
        groups = frame.groupby(["model_key", "feature_budget", "scope"]).size()
        check(f"{label} has exactly 500 banks per model/budget/scope",
              len(groups) == 12 and groups.eq(500).all(), groups.to_dict())
    shared_subsets = random_real[random_real.scope.eq("core")].groupby(["feature_budget", "bank"]).traits.nunique()
    check("random-real subsets fixed identically across models", shared_subsets.eq(1).all(), int(shared_subsets.max()))
    check("random-real seed fixed", random_real.subset_seed.eq(2026091201).all(), sorted(random_real.subset_seed.unique().tolist()))
    for label, frame, base in [("isotropic", isotropic, 30_000_000), ("persona-span", persona, 50_000_000)]:
        probe = frame.drop_duplicates(["model_key", "feature_budget", "bank"])
        expected_min = probe.apply(
            lambda row: base + runner.MODEL_ORDER.index(row.model_key) * 1_000_000 + int(row.bank) * 100,
            axis=1,
        )
        seeds_ok = (probe.fold_seed_min.to_numpy() == expected_min.to_numpy()).all() and \
            (probe.fold_seed_max.to_numpy() == expected_min.to_numpy() + 4).all()
        check(f"{label} preregistered fold-local seed formula", bool(seeds_ok), int(len(probe)))
        check(f"{label} direction generation is target-independent",
              (~frame.direction_generation_used_pc_targets.astype(bool)).all(), False)
    check("persona-span directions use outer training roles only", persona.outer_training_role_only.astype(bool).all(), True)

    alignment = pd.read_csv(HERE / "procrustes_alignment_cv.csv")
    check("alignment CV row count/protocol coverage", len(alignment) == 132,
          alignment.groupby(["pair", "dimensions", "variant", "protocol"]).size().to_dict())
    check("alignment transforms fit on training roles only", alignment.fit_roles_only.astype(bool).all(), True)
    fits = json.loads((HERE / "procrustes_alignment_matrices.json").read_text(encoding="utf-8"))["fits"]
    orthogonal = len(fits) == 12
    for fit in fits.values():
        rotation = np.asarray(fit["rotation"], float)
        orthogonal = orthogonal and np.max(np.abs(rotation.T @ rotation - np.eye(rotation.shape[0]))) < 1e-10
    check("all 12 full Procrustes rotations are orthogonal", bool(orthogonal), len(fits))
    null = pd.read_csv(HERE / "procrustes_alignment_null.csv")
    null_groups = null.groupby(["pair", "dimensions", "variant"]).size()
    check("alignment null has 1000 permutations per pair/dimension/variant",
          len(null_groups) == 12 and null_groups.eq(1000).all(), null_groups.to_dict())
    check("alignment null permutes labels before fit and excludes held-out targets",
          null.role_labels_permuted_before_fit.astype(bool).all() and null.fit_roles_only.astype(bool).all(), True)

    expected_rows = {
        "human_supported_trait_scores.csv": 9900,
        "human_supported_trait_pc_associations.csv": 216,
        "human_supported_trait_redundancy.csv": 234,
        "human_supported_trait_contributions.csv": 324,
        "local_pc_prediction_summary.csv": 78,
        "local_pc_prediction_per_pc.csv": 351,
        "role_family_holdout_summary.csv": 30,
        "geometry_optimized_k12_selections.csv": 360,
        "aligned_human_supported_trait_directions.csv": 24,
        "aligned_big_five_directions.csv": 10,
        "aligned_trait_consensus_summary.csv": 34,
        "procrustes_alignment_null.csv": 12000,
    }
    for name, expected in expected_rows.items():
        frame = pd.read_csv(HERE / name)
        check(f"{name} parses with expected rows", len(frame) == expected, len(frame))
        numeric = frame.select_dtypes(include=[np.number]).to_numpy(float)
        check(f"{name} contains no numeric infinity", not np.isinf(numeric).any(), int(np.isinf(numeric).sum()))

    score_columns = pd.read_csv(HERE / "human_supported_trait_scores.csv").columns.str.lower().tolist()
    forbidden_columns = {"respondent", "respondent_id", "occupation", "occupational_centroid", "human_outcome"}
    check("no human respondent/person-level fields in model score output",
          forbidden_columns.isdisjoint(score_columns), score_columns)
    manifest = json.loads((HERE / "source_manifest.json").read_text(encoding="utf-8"))
    check("source manifest records no prohibited human-data operation",
          not any(manifest["human_data_boundary"][field] for field in [
              "human_respondents_projected", "occupational_centroids_projected",
              "respondent_level_human_microdata_committed", "respondent_level_human_microdata_loaded",
              "human_outcomes_predicted",
          ]), manifest["human_data_boundary"])
    check("source manifest records prohibited compute as unused",
          not any(manifest["compute"][field] for field in [
              "gpu_used", "runpod_used", "new_model_inference", "activation_extraction",
              "response_generation", "external_model_api",
          ]), manifest["compute"])
    runner_manifest_path = str(RUNNER.relative_to(REPO))
    check("source manifest hashes final analysis runner",
          manifest["inputs"][runner_manifest_path]["sha256"] == sha256(RUNNER), sha256(RUNNER))

    rerun_hashes: dict[str, str] = {}
    if not args.skip_deterministic_rerun:
        with tempfile.TemporaryDirectory(prefix="aa7-reproduction-") as temporary:
            destination = Path(temporary)
            command = [
                str(VENV_PYTHON), str(RUNNER), "--output-dir", str(destination),
                "--control-draws", "500", "--alignment-permutations", "1000", "--n-jobs", "4",
            ]
            completed = subprocess.run(command, cwd=REPO, check=False, text=True, capture_output=True)
            check("full deterministic reproduction command exits zero", completed.returncode == 0,
                  {"returncode": completed.returncode, "stdout_tail": completed.stdout[-1000:], "stderr_tail": completed.stderr[-1000:]})
            mismatches = []
            for name in GENERATED_DETERMINISTIC:
                left, right = HERE / name, destination / name
                if not right.exists() or sha256(left) != sha256(right):
                    mismatches.append(name)
                else:
                    rerun_hashes[name] = sha256(left)
            check("primary CSV/JSON/report outputs reproduce byte-for-byte", not mismatches, mismatches)
    else:
        check("deterministic rerun explicitly skipped", True, "--skip-deterministic-rerun")

    report = {
        "analysis": "AA-7 verification",
        "canonical_starting_sha": runner.CANONICAL_STARTING_SHA,
        "overall_status": "PASS",
        "checks": checks,
        "deterministic_rerun_completed": not args.skip_deterministic_rerun,
        "deterministic_output_sha256": rerun_hashes,
        "human_data_boundary": manifest["human_data_boundary"],
        "compute_boundary": manifest["compute"],
        "vector_root_read_only": str(vector_root),
    }
    (HERE / "verification_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"overall_status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
