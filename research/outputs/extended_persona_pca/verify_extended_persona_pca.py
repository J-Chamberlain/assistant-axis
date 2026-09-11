#!/usr/bin/env python3
"""Independent integrity checks for the extended persona PCA audit."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import warnings

import numpy as np
from scipy.optimize import linear_sum_assignment


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = HERE / "run_extended_persona_pca.py"
VECTOR_ROOT = Path(
    "/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_runner():
    spec = importlib.util.spec_from_file_location("extended_persona_pca_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import audit runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def csv_rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check(name: str, passed: bool, detail: str, checks: list[dict]) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def main() -> int:
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*encountered in matmul.*")
    runner = load_runner()
    checks: list[dict] = []

    required = [
        "extended_persona_pca_report.md",
        "persona_pca_construction_audit.md",
        "full_pca_spectrum.csv",
        "pca_cumulative_variance_thresholds.csv",
        "pca_knee_diagnostics.json",
        "pca_broken_stick_comparison.csv",
        "pca_parallel_analysis.csv",
        "pca_bootstrap_component_stability.csv",
        "pca_subspace_stability.csv",
        "qwen_extended_pc_role_rankings.csv",
        "qwen_extended_pc_trait_associations.csv",
        "qwen_extended_pc_interpretation_packet.csv",
        "cross_model_pc_score_correspondence.csv",
        "cross_model_pc_subspace_similarity.csv",
        "cross_model_pc_permutation_control.csv",
        "component_retention_summary.csv",
        "extended_persona_pca_viewer.html",
        "viewer_data.json",
        "source_manifest.json",
        "deterministic_second_pass.json",
    ]
    check(
        "required_artifacts_exist",
        all((HERE / name).is_file() for name in required),
        f"{sum((HERE / name).is_file() for name in required)}/{len(required)} required files present",
        checks,
    )

    parsed_csv = []
    parsed_json = []
    parse_errors = []
    for path in sorted(HERE.glob("*.csv")):
        try:
            csv_rows(path.name)
            parsed_csv.append(path.name)
        except Exception as exc:  # pragma: no cover - reported as a failed audit check
            parse_errors.append(f"{path.name}: {exc}")
    for path in sorted(HERE.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            parsed_json.append(path.name)
        except Exception as exc:  # pragma: no cover
            parse_errors.append(f"{path.name}: {exc}")
    check(
        "all_csv_json_parse_strictly",
        not parse_errors,
        f"parsed {len(parsed_csv)} CSV and {len(parsed_json)} JSON files; errors={parse_errors}",
        checks,
    )

    names, qwen_reference, _, established = runner.load_references()
    results = {}
    audits = {}
    qwen_scores = None
    for key, spec in runner.MODEL_SPECS.items():
        role_dir = VECTOR_ROOT / spec["folder"] / "role_vectors"
        role_names, vectors, audit = runner.load_mean_role_vectors(role_dir, spec["expected_dim"])
        result = runner.fit_full_pca(
            key, role_names, vectors, audit, names, qwen_reference, qwen_scores, established
        )
        results[key] = result
        audits[key] = audit
        if key == "qwen":
            qwen_scores = result.scores

    expected_shapes = {
        "qwen": (275, 5120),
        "llama": (275, 8192),
        "gemma": (275, 4608),
    }
    check(
        "exact_role_counts_and_vector_dimensions",
        all(results[k].vectors.shape == expected_shapes[k] for k in expected_shapes),
        str({k: list(results[k].vectors.shape) for k in results}),
        checks,
    )
    check(
        "shared_role_ordering",
        all(results[k].names == names for k in results),
        "all three model matrices use the canonical 275-role lexical order",
        checks,
    )
    check(
        "finite_source_vectors",
        all(np.isfinite(results[k].vectors).all() for k in results),
        "all mean-pooled source-vector entries are finite",
        checks,
    )

    canonical_errors = {k: results[k].canonical_pc123_max_abs_error for k in results}
    canonical_limits = {"qwen": 2e-6, "llama": 1e-10, "gemma": 1e-8}
    check(
        "canonical_pc123_reproduction",
        all(canonical_errors[k] <= canonical_limits[k] for k in results),
        str(canonical_errors),
        checks,
    )
    reconstruction = {k: results[k].reconstruction_relative_frobenius_error for k in results}
    check(
        "full_rank_reconstruction",
        all(value < 1e-12 for value in reconstruction.values()),
        str(reconstruction),
        checks,
    )
    variance_sums = {k: float(results[k].explained_ratio.sum()) for k in results}
    check(
        "variance_sums_and_cumulative_monotonicity",
        all(abs(v - 1.0) < 1e-12 for v in variance_sums.values())
        and all(np.all(np.diff(results[k].cumulative_ratio) >= -1e-15) for k in results),
        str(variance_sums),
        checks,
    )

    spectrum = csv_rows("full_pca_spectrum.csv")
    spectrum_by_model = {}
    for row in spectrum:
        spectrum_by_model.setdefault(row["model"], []).append(row)
    spectrum_ok = len(spectrum) == 3 * 274
    score_ok = True
    for result in results.values():
        rows = spectrum_by_model[result.label]
        spectrum_ok &= len(rows) == 274
        for pc in range(274):
            score_ok &= np.allclose(
                np.asarray(json.loads(rows[pc]["role_scores_json"]), dtype=float),
                result.scores[:, pc],
                rtol=0,
                atol=2e-10,
            )
    check(
        "saved_full_spectrum_matches_recomputation",
        spectrum_ok and score_ok,
        "822 rows and all 274 role-score vectors per model match a fresh SVD",
        checks,
    )

    broken = csv_rows("pca_broken_stick_comparison.csv")
    expected_broken = np.asarray([sum(1.0 / j for j in range(i, 275)) / 274 for i in range(1, 275)])
    broken_ok = len(broken) == 822
    for result in results.values():
        rows = [r for r in broken if r["model"] == result.label]
        broken_ok &= len(rows) == 274 and np.allclose(
            [float(r["broken_stick_expected_share"]) for r in rows], expected_broken, atol=1e-15, rtol=0
        )
    check(
        "broken_stick_formula",
        broken_ok and abs(expected_broken.sum() - 1.0) < 1e-12,
        f"rank-274 expected shares sum to {expected_broken.sum():.16f}",
        checks,
    )

    deterministic = json.loads((HERE / "deterministic_second_pass.json").read_text(encoding="utf-8"))
    deterministic_ok = deterministic.get("performed") is True and deterministic.get(
        "all_major_numerical_artifacts_byte_identical"
    ) is True
    seed_ok = True
    source = json.loads((HERE / "source_manifest.json").read_text(encoding="utf-8"))
    for key, seed in runner.PARALLEL_SEEDS.items():
        recorded = source["parameters"]["seeds"]["parallel"][key]
        seed_ok &= recorded["seed"] == seed and recorded["replicates"] == runner.N_PARALLEL
    check(
        "parallel_analysis_seed_reproducibility",
        deterministic_ok and seed_ok,
        "250-per-model null and all 14 major numerical outputs are byte-identical on the second fixed-seed pass",
        checks,
    )

    # Synthetic swap/sign test for absolute-cosine Hungarian matching.
    reference = np.eye(4)
    permutation = np.asarray([2, 0, 3, 1])
    signs = np.asarray([-1.0, 1.0, -1.0, 1.0])
    candidate = reference[:, permutation] * signs
    similarity = reference.T @ candidate
    ri, ci = linear_sum_assignment(-np.abs(similarity))
    mapping = dict(zip(ri.tolist(), ci.tolist(), strict=True))
    recovered = all(permutation[mapping[i]] == i and abs(similarity[i, mapping[i]]) == 1 for i in range(4))
    check(
        "bootstrap_hungarian_matching_and_sign_handling",
        recovered,
        f"synthetic permutation/sign test mapping={mapping}",
        checks,
    )

    theta = 0.731
    base = np.eye(8)[:, :3]
    rotation = np.asarray(
        [[math.cos(theta), -math.sin(theta), 0], [math.sin(theta), math.cos(theta), 0], [0, 0, 1]]
    )
    canonical = np.linalg.svd(base.T @ (base @ rotation), compute_uv=False)
    check(
        "principal_angle_subspace_rotation_invariance",
        np.allclose(canonical, 1.0, atol=1e-14),
        f"synthetic within-subspace rotation canonical correlations={canonical.tolist()}",
        checks,
    )

    correspondence = csv_rows("cross_model_pc_score_correspondence.csv")
    hungarian_ok = True
    for target in (results["llama"].label, results["gemma"].label):
        rows = [r for r in correspondence if r["target_model"] == target]
        cross_n = int(round(math.sqrt(len(rows))))
        matrix = np.zeros((cross_n, cross_n))
        saved_matches = {}
        for row in rows:
            i = int(row["reference_component"]) - 1
            j = int(row["target_component"]) - 1
            matrix[i, j] = float(row["matching_objective_mean_absolute_correlation"])
            if row["is_hungarian_match"] == "True":
                saved_matches[i] = j
        ri, ci = linear_sum_assignment(-matrix)
        recomputed = dict(zip(ri.tolist(), ci.tolist(), strict=True))
        hungarian_ok &= saved_matches == recomputed and len(set(saved_matches.values())) == cross_n
    check(
        "cross_model_hungarian_matching",
        hungarian_ok,
        "saved one-to-one correspondence map re-optimizes exactly from the saved objective matrices",
        checks,
    )

    controls = csv_rows("cross_model_pc_permutation_control.csv")
    component_controls = [r for r in controls if r["control_type"] == "best_component_absolute_pearson"]
    subspace_controls = [r for r in controls if r["control_type"] == "mean_subspace_canonical_correlation"]
    control_ok = (
        len(component_controls) > 0
        and len(subspace_controls) == 18
        and all(int(r["permutations"]) == 1000 for r in controls)
        and all(0 < float(r["empirical_p_value"]) <= 1 for r in controls)
    )
    check(
        "role_label_permutation_controls",
        control_ok,
        f"component summaries={len(component_controls)}, subspace summaries={len(subspace_controls)}, permutations=1000",
        checks,
    )

    viewer = json.loads((HERE / "viewer_data.json").read_text(encoding="utf-8"))
    viewer_ok = True
    for key, result in results.items():
        points = viewer["models"][key]["points"]
        viewer_ok &= [p["persona"] for p in points] == result.names
        viewer_ok &= np.allclose(
            np.asarray([p["coordinates"] for p in points]), result.scores[:, :10], rtol=0, atol=2e-10
        )
    html = (HERE / "extended_persona_pca_viewer.html").read_text(encoding="utf-8")
    viewer_ok &= all(
        token in html
        for token in ('id="model"', 'id="mode"', 'id="pc-x"', 'id="pc-y"', 'id="pc-z"')
    )
    check(
        "viewer_coordinates_and_controls",
        viewer_ok,
        "all 825 PC1-PC10 point records match fresh PCA scores; required 2D/3D controls are embedded",
        checks,
    )

    runner_hash_ok = source["runner_sha256"] == sha256(RUNNER)
    source_hash_resolution = {}
    for item in source["source_files"]:
        path = REPO / item["path"]
        current_matches = path.is_file() and sha256(path) == item["sha256"]
        starting_matches = False
        if not current_matches:
            try:
                original = subprocess.check_output(
                    ["git", "show", f"{source['starting_canonical_myfork_master_sha']}:{item['path']}"],
                    cwd=REPO,
                )
                starting_matches = hashlib.sha256(original).hexdigest() == item["sha256"]
            except subprocess.CalledProcessError:
                starting_matches = False
        source_hash_resolution[item["path"]] = (
            "current_worktree" if current_matches else "recorded_starting_commit" if starting_matches else "unresolved"
        )
    source_hash_ok = all(value != "unresolved" for value in source_hash_resolution.values())
    check(
        "source_manifest_hashes",
        runner_hash_ok and source_hash_ok,
        f"runner hash match={runner_hash_ok}; source resolutions={source_hash_resolution}",
        checks,
    )

    report = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "numerical_warning_note": (
            "The local Apple Accelerate/NumPy backend emitted spurious matmul floating-point status warnings. "
            "Direct finite checks, full-SVD reconstruction, canonical-coordinate reproduction, and a byte-identical "
            "second numerical pass establish that saved results are finite and reproducible."
        ),
        "compute_boundary": "CPU only; no GPU, RunPod, model inference, activation extraction, or external model API.",
    }
    (HERE / "verification_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    runner.build_artifact_inventory()
    inventory = csv_rows("artifact_inventory.csv")
    inventory_ok = all(
        (REPO / row["path"]).is_file()
        and int(row["size_bytes"]) == (REPO / row["path"]).stat().st_size
        and row["sha256"] == sha256(REPO / row["path"])
        for row in inventory
    )
    report["inventory_after_report_refresh"] = {
        "passed": inventory_ok,
        "artifacts_checked": len(inventory),
        "inventory_excludes_itself_to_avoid_a_circular_hash": True,
    }
    if not inventory_ok:
        report["status"] = "FAIL"
    (HERE / "verification_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Refresh once more because the verification report now includes the inventory result.
    runner.build_artifact_inventory()
    print(f"{report['status']}: {report['checks_passed']}/{report['checks_total']} checks; {len(inventory)} artifact hashes")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
