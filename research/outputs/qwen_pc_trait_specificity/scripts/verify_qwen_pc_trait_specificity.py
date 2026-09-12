#!/usr/bin/env python3
"""Independent verification of Qwen PC trait-specificity outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr


AA1_COMMIT = "667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb"
SPEC_FREEZE_COMMIT = "595c1e22cc5e7cd7b7e9a6a90046e18b9b103d68"
BOOTSTRAP_SEED = 20260912
BOOTSTRAP_RESAMPLES = 2000
EPSILON = 1e-12
PC_ORDER = [f"PC{i}" for i in range(1, 7)]
CORE_FILES = [
    "qwen_trait_cross_pc_specificity_all.csv",
    "qwen_pc_defining_trait_sets.csv",
    "qwen_pc_trait_specificity_pareto.csv",
    "qwen_pc_specificity_threshold_sensitivity.csv",
    "qwen_pc_specificity_composites.csv",
    "qwen_pc_specificity_human_inventory.csv",
    "qwen_pc_specificity_human_summary.csv",
    "pc3_reference_composite_audit.md",
    "qwen_pc_specificity_report.md",
    "source_manifest.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)


def qwen_points(path: Path) -> pd.DataFrame:
    collecting = False
    depth = 0
    lines: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not collecting:
                if line.strip() == '"qwen": {':
                    collecting = True
                    lines.append("{")
                    depth = 1
                continue
            for char in line:
                depth += (char == "{") - (char == "}")
            if depth == 0:
                break
            lines.append(line)
    lines.append("}")
    qwen = json.loads("".join(lines))
    rows = []
    for point in qwen["points"]:
        rows.append({"persona": point["persona"], **{f"PC{i}": point["coordinates"][i - 1] for i in range(1, 7)}})
    return pd.DataFrame(rows)


def load_numeric_sources(repo: Path) -> tuple[pd.DataFrame, list[str], np.ndarray, np.ndarray]:
    source = pd.read_csv(repo / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv")
    traits = [column for column in source.columns if column != "persona"]
    points = qwen_points(repo / "research/outputs/extended_persona_pca/viewer_data.json")
    merged = source.merge(points, on="persona", validate="one_to_one").sort_values("persona", kind="mergesort")
    return merged, traits, merged[traits].to_numpy(float), merged[PC_ORDER].to_numpy(float)


def independent_observed(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    result = np.empty((x.shape[1], y.shape[1]), dtype=float)
    for trait in range(x.shape[1]):
        for pc in range(y.shape[1]):
            result[trait, pc] = float(pearsonr(x[:, trait], y[:, pc]).statistic)
    return result


def independent_bootstrap(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Recompute with raw-sum Pearson algebra, distinct from the main script."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    result = np.empty((BOOTSTRAP_RESAMPLES, x.shape[1], y.shape[1]), dtype=float)
    n = x.shape[0]
    offset = 0
    batch_size = 20
    while offset < BOOTSTRAP_RESAMPLES:
        batch = min(batch_size, BOOTSTRAP_RESAMPLES - offset)
        indices = rng.integers(0, n, size=(batch, n))
        xb = x[indices, :]
        yb = y[indices, :]
        sx = xb.sum(axis=1)
        sy = yb.sum(axis=1)
        sxx = np.einsum("bnt,bnt->bt", xb, xb, optimize=True)
        syy = np.einsum("bnp,bnp->bp", yb, yb, optimize=True)
        sxy = np.einsum("bnt,bnp->btp", xb, yb, optimize=True)
        numerator = sxy - sx[:, :, None] * sy[:, None, :] / n
        denominator = np.sqrt(
            (sxx - sx * sx / n)[:, :, None] * (syy - sy * sy / n)[:, None, :]
        )
        result[offset : offset + batch] = numerator / denominator
        offset += batch
    return result


def independent_pareto(group: pd.DataFrame) -> dict[str, bool]:
    values = group[["target_abs_r", "specificity_margin", "pc1_6_concentration_fraction"]].to_numpy(float)
    output = {}
    for i, name in enumerate(group["trait"]):
        dominated = False
        for j in range(len(values)):
            if i == j:
                continue
            if all(values[j, k] >= values[i, k] - EPSILON for k in range(3)) and any(
                values[j, k] > values[i, k] + EPSILON for k in range(3)
            ):
                dominated = True
                break
        output[name] = not dominated
    return output


def normalize_strings(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame[columns].fillna("").copy()
    for column in columns:
        result[column] = result[column].map(lambda value: "" if value == "" else str(value))
    return result


def verify(repo: Path, output: Path) -> dict[str, object]:
    checks: dict[str, bool] = {}
    cross = pd.read_csv(output / "qwen_trait_cross_pc_specificity_all.csv")
    sets = pd.read_csv(output / "qwen_pc_defining_trait_sets.csv")
    pareto = pd.read_csv(output / "qwen_pc_trait_specificity_pareto.csv")
    sensitivity = pd.read_csv(output / "qwen_pc_specificity_threshold_sensitivity.csv")
    composites = pd.read_csv(output / "qwen_pc_specificity_composites.csv")
    human_inventory = pd.read_csv(output / "qwen_pc_specificity_human_inventory.csv")
    human_summary = pd.read_csv(output / "qwen_pc_specificity_human_summary.csv")
    manifest = json.loads((output / "source_manifest.json").read_text(encoding="utf-8"))
    aa1_all = pd.read_csv(repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_pc_correlations_all.csv")
    aa1_members = pd.read_csv(repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_family_membership_primary.csv")
    aa1_judgments = pd.read_csv(repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_family_human_mapping_judgments.csv")
    merged, traits, x, y = load_numeric_sources(repo)

    checks["exactly_240_traits_x_6_targets"] = (
        len(cross) == 1440 and cross["trait"].nunique() == 240 and set(cross["pc"]) == set(PC_ORDER)
        and cross.groupby("trait")["pc"].nunique().eq(6).all()
    )
    checks["all_six_signed_correlations_retained_per_row"] = all(
        column in cross.columns for column in [f"r_PC{i}" for i in range(1, 7)]
    ) and np.isfinite(cross[[f"r_PC{i}" for i in range(1, 7)]].to_numpy(float)).all()
    checks["source_role_trait_counts_are_275_by_240"] = len(merged) == 275 and len(traits) == 240

    observed = independent_observed(x, y)
    trait_index = {trait: i for i, trait in enumerate(traits)}
    observed_ok = True
    metric_ok = True
    for row in cross.itertuples(index=False):
        t = trait_index[row.trait]
        p = int(row.pc[2:]) - 1
        saved = np.array([getattr(row, f"r_PC{i}") for i in range(1, 7)], dtype=float)
        observed_ok &= bool(np.allclose(saved, observed[t], atol=2e-12, rtol=2e-12))
        off = [i for i in range(6) if i != p]
        off_index = off[int(np.argmax(np.abs(saved[off])))]
        expected_margin = abs(saved[p]) - abs(saved[off_index])
        expected_ratio = abs(saved[p]) / (abs(saved[off_index]) + EPSILON)
        expected_concentration = saved[p] ** 2 / np.sum(saved * saved)
        metric_ok &= bool(
            np.isclose(row.target_pearson_r, saved[p], atol=2e-12, rtol=2e-12)
            and row.largest_offtarget_pc == f"PC{off_index + 1}"
            and np.isclose(row.largest_offtarget_signed_r, saved[off_index], atol=2e-12, rtol=2e-12)
            and np.isclose(row.specificity_margin, expected_margin, atol=2e-12, rtol=2e-12)
            and np.isclose(row.specificity_ratio, expected_ratio, atol=2e-12, rtol=2e-12)
            and np.isclose(row.pc1_6_concentration_fraction, expected_concentration, atol=2e-12, rtol=2e-12)
        )
    checks["observed_correlations_independently_recomputed"] = observed_ok
    checks["specificity_metrics_independently_recomputed"] = metric_ok

    aa1_keys = set(zip(aa1_members["pc"], aa1_members["trait"]))
    reproduced = aa1_all[
        (aa1_all["pearson_r"].abs() >= 0.50)
        & (aa1_all["BH_FDR_q"] < 0.01)
        & (aa1_all["bootstrap_sign_stability"] >= 0.95)
    ]
    reproduced_keys = set(zip(reproduced["pc"], reproduced["trait"]))
    output_associated = set(zip(cross.loc[cross["is_pc_associated"], "pc"], cross.loc[cross["is_pc_associated"], "trait"]))
    checks["original_aa1_membership_reproduced_exactly"] = (
        aa1_keys == reproduced_keys == output_associated
        and len(sets) == 1440
        and int(sets["is_pc_associated"].sum()) == 328
    )
    checks["original_aa1_association_statistics_reproduced"] = all(
        np.isclose(
            cross.set_index(["pc", "trait"]).loc[(row.pc, row.trait), "target_pearson_r"],
            row.pearson_r,
            atol=2e-12,
            rtol=2e-12,
        )
        for row in aa1_all.itertuples(index=False)
    )

    bootstrap = independent_bootstrap(x, y)
    bootstrap_ok = True
    quantile_ok = True
    for p, pc in enumerate(PC_ORDER):
        target = np.abs(bootstrap[:, :, p])
        off = [i for i in range(6) if i != p]
        largest = np.abs(bootstrap[:, :, off]).max(axis=2)
        margin = target - largest
        ratio = target / (largest + EPSILON)
        squared = bootstrap * bootstrap
        concentration = squared[:, :, p] / squared.sum(axis=2)
        group = cross[cross["pc"] == pc].set_index("trait")
        for t, trait in enumerate(traits):
            row = group.loc[trait]
            bootstrap_ok &= bool(np.isclose(row.target_is_largest_probability, np.mean(target[:, t] >= largest[:, t]), atol=1e-15))
            for prefix, values in [
                ("target_abs_r", target[:, t]),
                ("largest_offtarget_abs_r", largest[:, t]),
                ("specificity_margin", margin[:, t]),
                ("specificity_ratio", ratio[:, t]),
                ("concentration_fraction", concentration[:, t]),
            ]:
                q025, median, q975 = np.quantile(values, [0.025, 0.5, 0.975])
                quantile_ok &= bool(
                    np.isclose(row[f"{prefix}_median"], median, atol=2e-11, rtol=2e-11)
                    and np.isclose(row[f"{prefix}_q025"], q025, atol=2e-11, rtol=2e-11)
                    and np.isclose(row[f"{prefix}_q975"], q975, atol=2e-11, rtol=2e-11)
                )
    checks["bootstrap_seed_and_resamples_fixed"] = (
        manifest["bootstrap"]["seed"] == BOOTSTRAP_SEED
        and manifest["bootstrap"]["resamples"] == BOOTSTRAP_RESAMPLES
        and set(cross["specificity_bootstrap_seed"]) == {BOOTSTRAP_SEED}
        and set(cross["specificity_bootstrap_resamples"]) == {BOOTSTRAP_RESAMPLES}
    )
    checks["target_is_largest_probability_independently_reproduced"] = bootstrap_ok
    checks["bootstrap_distribution_summaries_independently_reproduced"] = quantile_ok

    expected_primary = cross["is_pc_associated"] & (cross["target_is_largest_probability"] >= 0.95)
    checks["primary_pc_defining_rule_reproduced"] = bool((cross["is_primary_pc_defining"] == expected_primary).all())
    expected_high = expected_primary & (cross["pc1_6_concentration_fraction"] >= 0.75)
    expected_moderate = expected_primary & (cross["pc1_6_concentration_fraction"] >= 0.50) & (cross["pc1_6_concentration_fraction"] < 0.75)
    checks["descriptive_tiers_reproduced"] = bool(
        (cross["is_target_dominant"] == expected_primary).all()
        and (cross["is_highly_concentrated"] == expected_high).all()
        and (cross["is_moderately_concentrated"] == expected_moderate).all()
    )

    pareto_ok = True
    for (pc, pole), group in sets.groupby(["pc", "pole"], sort=False):
        expected = independent_pareto(group)
        actual = pareto[(pareto["pc"] == pc) & (pareto["pole"] == pole)].set_index("trait")["is_pareto_frontier"].to_dict()
        pareto_ok &= expected == actual
    checks["pareto_frontiers_independently_recomputed"] = pareto_ok

    sensitivity_ok = len(sensitivity) == 108
    for row in sensitivity.itertuples(index=False):
        family = cross[(cross["pc"] == row.pc) & (cross["pole"] == row.pole)]
        assoc = (
            (family["target_abs_r"] >= row.target_abs_r_threshold)
            & (family["BH_FDR_q"] < 0.01)
            & (family["bootstrap_sign_stability"] >= 0.95)
        )
        defining = assoc & (family["target_is_largest_probability"] >= row.target_is_largest_probability_threshold)
        sensitivity_ok &= int(assoc.sum()) == row.associated_count and int(defining.sum()) == row.pc_defining_count
    checks["full_3_by_3_sensitivity_grid_reproduced"] = sensitivity_ok

    qwen_rows = []
    group_path = repo / "research/outputs/persona_trait_surface_viewer/persona_trait_group_scores.csv"
    with group_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["model"] == "qwen" and row["group"] == "Affiliation":
                qwen_rows.append(row)
    qwen_rows.sort(key=lambda row: row["persona"])
    ref_values = np.array([float(row["group_mean_trait_percentile"]) for row in qwen_rows])
    formula_ok = all(
        np.isclose(float(row["group_mean_trait_percentile"]), np.mean([float(row[f"percentile_{i}"]) for i in range(1, 4)]), atol=1e-12)
        and [row[f"trait_{i}"] for i in range(1, 4)] == ["empathetic", "agreeable", "altruistic"]
        for row in qwen_rows
    )
    ref_corr = np.array([pearsonr(ref_values, y[:, i]).statistic for i in range(6)])
    saved_ref = composites[composites["composite_id"] == "canonical_pc3_affiliation_surface"].iloc[0]
    checks["pc3_reference_composite_exact_formula_and_members"] = len(qwen_rows) == 275 and formula_ok
    checks["pc3_reference_pc1_pc6_correlations_reproduced"] = np.allclose(
        ref_corr, [saved_ref[f"r_PC{i}"] for i in range(1, 7)], atol=2e-12, rtol=2e-12
    )
    checks["reference_did_not_set_thresholds"] = (
        manifest["specificity_spec_freeze_commit"] == SPEC_FREEZE_COMMIT
        and git(repo, "cat-file", "-e", f"{SPEC_FREEZE_COMMIT}:research/outputs/qwen_pc_trait_specificity/qwen_pc_trait_specificity_spec.md").returncode == 0
        and git(repo, "cat-file", "-e", f"{SPEC_FREEZE_COMMIT}:research/outputs/qwen_pc_trait_specificity/qwen_trait_cross_pc_specificity_all.csv").returncode != 0
    )

    original_columns = list(aa1_judgments.columns)
    original = normalize_strings(aa1_judgments, original_columns)
    refined_original = normalize_strings(human_inventory, original_columns)
    checks["frozen_human_mapping_judgments_unchanged"] = original.equals(refined_original)
    checks["all_12_human_family_summaries_present"] = len(human_summary) == 12 and set(zip(human_summary["pc"], human_summary["pole"])) == {
        (pc, pole) for pc in PC_ORDER for pole in ("positive", "negative")
    }
    checks["human_inventory_has_no_respondent_identifiers"] = not {
        "respondent_id", "caseid", "subject_id", "nlsyid", "person_id"
    } & {column.lower() for column in human_inventory.columns}

    checks["qwen_only_firewall"] = (
        manifest["firewall"]["models_used"] == ["Qwen/Qwen3-32B"]
        and manifest["firewall"]["Llama_or_Gemma_values_loaded"] is False
        and manifest["firewall"]["AA7_scientific_result_paths_used"] == []
    )
    checks["mandatory_stopping_point_respected"] = all(
        manifest["firewall"][key] is False
        for key in [
            "human_respondent_rows_loaded_or_scored", "human_model_projection_performed",
            "human_model_correspondence_test_run", "next_experiment_selected",
            "respondent_level_human_microdata_emitted",
        ]
    )
    checks["cpu_saved_artifact_only_compute"] = manifest["compute"].startswith("CPU only")

    parse_ok = True
    for path in output.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            if path.suffix == ".csv":
                pd.read_csv(path)
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            parse_ok = False
    checks["all_csv_and_json_outputs_parse"] = parse_ok

    deterministic = True
    with tempfile.TemporaryDirectory(prefix="qwen_specificity_verify_") as temp_name:
        temp = Path(temp_name)
        command = [
            sys.executable,
            str(output / "scripts/compute_qwen_pc_trait_specificity.py"),
            "--repo-root", str(repo), "--output-dir", str(temp),
        ]
        subprocess.run(command, cwd=repo, check=True, stdout=subprocess.DEVNULL)
        deterministic = all((temp / name).read_bytes() == (output / name).read_bytes() for name in CORE_FILES)
    checks["deterministic_rerun_reproduces_primary_outputs"] = deterministic

    inventory_failures = []
    artifact_inventory = output / "artifact_inventory.csv"
    if artifact_inventory.exists():
        for row in csv.DictReader(artifact_inventory.open(newline="", encoding="utf-8")):
            path = repo / row["path"]
            if not path.exists() or sha256(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
                inventory_failures.append(row["path"])
    checks["artifact_inventory_hashes_match"] = artifact_inventory.exists() and not inventory_failures

    checks["aa1_source_commit_is_ancestor"] = git(repo, "merge-base", "--is-ancestor", AA1_COMMIT, "HEAD").returncode == 0
    checks["spec_freeze_precedes_results"] = git(repo, "merge-base", "--is-ancestor", SPEC_FREEZE_COMMIT, "HEAD").returncode == 0
    tracked_raw = git(repo, "ls-files", "data_external/human_validation").stdout.strip()
    checks["no_respondent_level_human_microdata_committed"] = tracked_raw == ""

    failures = sorted(name for name, value in checks.items() if not value)
    return {
        "analysis": "Qwen PC trait specificity verification",
        "generated_at_utc": "2026-09-12T20:30:00Z",
        "check_count": len(checks),
        "passed": not failures,
        "checks": {name: bool(value) for name, value in sorted(checks.items())},
        "failures": failures,
        "artifact_inventory_failures": inventory_failures,
        "counts": {
            "cross_pc_rows": len(cross),
            "associated_memberships": int(sets["is_pc_associated"].sum()),
            "pc_defining_memberships": int(sets["is_primary_pc_defining"].sum()),
            "highly_concentrated_memberships": int(sets["is_highly_concentrated"].sum()),
            "pareto_frontier_memberships": int(sets["is_pareto_frontier"].sum()),
            "human_mapping_rows": len(human_inventory),
            "human_summary_rows": len(human_summary),
        },
        "firewall": {
            "Qwen_only": True,
            "AA7_results_used": False,
            "human_respondents_scored": False,
            "human_model_projection": False,
            "human_model_correspondence_test": False,
            "next_experiment_selected": False,
        },
        "privacy": "No respondent-level human data are tracked or emitted.",
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = verify(args.repo_root.resolve(), args.output_dir.resolve())
    path = args.output_dir.resolve() / "verification_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "check_count": report["check_count"], "failures": report["failures"]}, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
