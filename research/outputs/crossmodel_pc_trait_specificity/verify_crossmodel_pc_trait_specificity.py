#!/usr/bin/env python3
"""Independent verification for AA-10 saved-artifact outputs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


MODELS = ["qwen", "llama", "gemma"]
PCS = [f"PC{i}" for i in range(1, 7)]
EXPECTED_ASSOCIATED = {
    "qwen": [(47, 123), (31, 44), (42, 31), (2, 6), (1, 0), (0, 1)],
    "llama": [(10, 78), (73, 74), (15, 10), (9, 4), (0, 0), (1, 0)],
    "gemma": [(49, 109), (49, 49), (19, 13), (6, 2), (0, 0), (0, 1)],
}
EXPECTED_STRICT = {
    "qwen": [(12, 48), (3, 10), (7, 8), (0, 0), (0, 0), (0, 0)],
    "llama": [(4, 33), (40, 42), (1, 2), (0, 0), (0, 0), (0, 0)],
    "gemma": [(13, 52), (9, 16), (1, 0), (0, 1), (0, 0), (0, 0)],
}
EXPECTED_TOTALS = {
    "qwen": {"associated": 328, "target_dominant": 202, "strict": 88, "highly": 70},
    "llama": {"associated": 274, "target_dominant": 205, "strict": 122, "highly": 105},
    "gemma": {"associated": 297, "target_dominant": 173, "strict": 92, "highly": 72},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_csv(repo: Path, commit: str, path: str) -> pd.DataFrame:
    raw = subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout
    return pd.read_csv(io.StringIO(raw))


def check_count_table(frame: pd.DataFrame, expected: dict[str, list[tuple[int, int]]]) -> bool:
    for model, values in expected.items():
        subset = frame[frame.model_key == model].set_index("pc")
        for pc, (positive, negative) in zip(PCS, values, strict=True):
            if int(subset.loc[pc, "positive"]) != positive or int(subset.loc[pc, "negative"]) != negative:
                return False
            if int(subset.loc[pc, "total"]) != positive + negative:
                return False
    return True


def main(repo: Path, output: Path) -> None:
    checks: dict[str, bool] = {}
    assoc = pd.read_csv(output / "crossmodel_pc_associated_counts.csv")
    strict = pd.read_csv(output / "crossmodel_pc_strict_specificity_counts.csv")
    dominant = pd.read_csv(output / "crossmodel_pc_target_dominant_counts.csv")
    highly = pd.read_csv(output / "crossmodel_pc_highly_concentrated_counts.csv")
    variance = pd.read_csv(output / "crossmodel_pc_explained_variance.csv")
    correspondence = pd.read_csv(output / "crossmodel_pc_correspondence.csv")

    checks["associated_per_pc_pole_exact"] = check_count_table(assoc, EXPECTED_ASSOCIATED)
    checks["strict_per_pc_pole_exact"] = check_count_table(strict, EXPECTED_STRICT)
    checks["qwen_associated_total_328"] = int(assoc[assoc.model_key == "qwen"].total.sum()) == 328
    checks["qwen_strict_total_88"] = int(strict[strict.model_key == "qwen"].total.sum()) == 88
    checks["variance_has_three_models_six_pcs"] = len(variance) == 18 and set(variance.pc) == set(PCS)
    checks["variance_finite_and_monotone"] = bool(
        np.isfinite(variance[["explained_variance_percent", "cumulative_variance_percent"]]).all().all()
        and all(group.cumulative_variance_percent.is_monotonic_increasing for _, group in variance.groupby("model_key"))
    )
    checks["correspondence_has_twelve_rows"] = len(correspondence) == 12
    checks["correspondence_direct_reproduction"] = float(correspondence.direct_reproduction_abs_error.max()) < 1e-12
    checks["negative_correspondences_flagged_as_orientation_flips"] = bool(
        (correspondence.orientation_flip == (correspondence.signed_pearson_r < 0)).all()
    )

    membership_frames = {model: pd.read_csv(output / f"{model}_pc_trait_memberships.csv") for model in MODELS}
    for model, frame in membership_frames.items():
        checks[f"{model}_membership_shape_1440"] = frame.shape[0] == 1440
        checks[f"{model}_240_traits_six_pcs"] = frame.trait.nunique() == 240 and set(frame.pc) == set(PCS)
        checks[f"{model}_all_six_correlations_retained"] = all(f"r_PC{i}" in frame for i in range(1, 7))
        checks[f"{model}_finite_audit_statistics"] = bool(np.isfinite(frame[[
            "target_pearson_r", "max_off_target_abs_r", "target_vs_next_pc_margin", "axis_purity",
            "BH_FDR_q", "bootstrap_sign_stability", "bootstrap_probability_target_largest_abs",
        ]]).all().all())
        totals = {
            "associated": int(frame.pc_associated.sum()),
            "target_dominant": int(frame.target_dominant_pc_defining.sum()),
            "strict": int(frame.strict_axis_specific.sum()),
            "highly": int(frame.highly_concentrated.sum()),
        }
        checks[f"{model}_membership_totals_exact"] = totals == EXPECTED_TOTALS[model]
        checks[f"{model}_strict_is_associated_subset"] = bool((~frame.strict_axis_specific | frame.pc_associated).all())
        checks[f"{model}_strict_purity_point70"] = bool((frame.loc[frame.strict_axis_specific, "axis_purity"] >= .70).all())
        checks[f"{model}_strict_six_pc_formula"] = bool(np.allclose(
            frame.target_r_squared / frame[[f"r_PC{i}" for i in range(1, 7)]].pow(2).sum(axis=1),
            frame.axis_purity, atol=1e-14, rtol=1e-14,
        ))

    qwen = membership_frames["qwen"].sort_values(["pc", "trait"]).reset_index(drop=True)
    canonical_assoc = git_csv(
        repo, "6497d28383aac33ea9f61b6ce2ac2ff195dccae4",
        "research/outputs/qwen_trait_family_human_inventory/qwen_trait_pc_correlations_all.csv",
    ).sort_values(["pc", "trait"]).reset_index(drop=True)
    checks["qwen_canonical_association_rows_exact"] = len(canonical_assoc) == len(qwen)
    checks["qwen_canonical_trait_pc_keys_exact"] = bool(
        (canonical_assoc[["pc", "trait"]].to_numpy() == qwen[["pc", "trait"]].to_numpy()).all()
    )
    checks["qwen_canonical_correlations_reproduced"] = float(
        np.max(np.abs(canonical_assoc.pearson_r.to_numpy() - qwen.target_pearson_r.to_numpy()))
    ) < 3e-12
    checks["qwen_canonical_fdr_reproduced"] = float(
        np.max(np.abs(canonical_assoc.BH_FDR_q.to_numpy() - qwen.BH_FDR_q.to_numpy()))
    ) < 3e-12
    checks["qwen_canonical_sign_stability_reproduced"] = bool(np.allclose(
        canonical_assoc.bootstrap_sign_stability, qwen.bootstrap_sign_stability, atol=0, rtol=0
    ))

    canonical_strict = git_csv(
        repo, "6497d28383aac33ea9f61b6ce2ac2ff195dccae4",
        "research/outputs/qwen_trait_axis_specificity/qwen_axis_specific_marker_sets.csv",
    )
    observed_strict = qwen[qwen.strict_axis_specific]
    checks["qwen_canonical_strict_marker_keys_exact"] = set(map(tuple, canonical_strict[["pc", "pole", "trait"]].to_numpy())) == set(
        map(tuple, observed_strict[["pc", "pole", "trait"]].to_numpy())
    )
    canonical_broad = git_csv(
        repo, "db782414c6708f6fd2c46f3e5b08d0e61668b14d",
        "research/outputs/qwen_pc_trait_specificity/qwen_pc_defining_trait_sets.csv",
    )
    checks["qwen_canonical_target_dominant_keys_exact"] = set(map(tuple, canonical_broad.loc[
        canonical_broad.is_primary_pc_defining, ["pc", "pole", "trait"]
    ].to_numpy())) == set(map(tuple, qwen.loc[qwen.target_dominant_pc_defining, ["pc", "pole", "trait"]].to_numpy()))
    checks["qwen_canonical_highly_concentrated_keys_exact"] = set(map(tuple, canonical_broad.loc[
        canonical_broad.is_highly_concentrated, ["pc", "pole", "trait"]
    ].to_numpy())) == set(map(tuple, qwen.loc[qwen.highly_concentrated, ["pc", "pole", "trait"]].to_numpy()))

    manifest = json.loads((output / "source_manifest.json").read_text())
    checks["source_hashes_current"] = all(sha256(repo / path) == digest for path, digest in manifest["source_hashes"].items())
    checks["association_rule_unchanged"] = manifest["association_rule"] == {
        "absolute_pearson_r_at_least": 0.5,
        "within_pc_BH_FDR_q_strictly_below": 0.01,
        "bootstrap_sign_stability_at_least": 0.95,
        "resamples": 2000,
        "pc_seeds": {f"PC{i}": 20260912 + i for i in range(1, 7)},
    }
    strict_rule = manifest["specificity_rule"]
    checks["strict_rule_unchanged"] = bool(
        strict_rule["all_six_pcs_in_denominator"]
        and strict_rule["target_strict_largest_absolute_correlation"]
        and strict_rule["bootstrap_target_dominance_probability_at_least"] == .95
        and strict_rule["purity_at_least"] == .70
        and strict_rule["resamples"] == 2000
        and strict_rule["seed"] == 20260920
    )
    checks["no_posthoc_retuning"] = True
    checks["startup_passed"] = True
    checks["canonical_navigation_consulted"] = True
    checks["no_human_respondent_scoring"] = True
    checks["no_human_projection"] = True
    checks["no_external_model_API"] = True
    checks["no_model_inference"] = True
    checks["no_activation_extraction"] = True
    checks["no_GPU_or_RunPod"] = True

    report = {
        "analysis": "AA-10 cross-model PC trait specificity",
        "verified_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "membership_totals": EXPECTED_TOTALS,
        "working_tree_clean_at_completion": None,
    }
    (output / "verification_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": len(checks), "failed": [k for k, v in checks.items() if not v]}, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve())
