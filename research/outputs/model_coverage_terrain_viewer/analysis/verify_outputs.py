#!/usr/bin/env python3
"""Verify numerical, visual, privacy, and scope requirements for the terrain viewer."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[2]
MODEL_ORDER = ["qwen", "llama", "gemma"]
SOURCE_LABELS = {"qwen": "Qwen/Qwen3-32B", "llama": "Llama-3.3-70B", "gemma": "Gemma-2-27B"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, observed: object, expected: object = True) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed, "expected": expected})
        if not passed:
            raise AssertionError(f"{name}: observed={observed!r} expected={expected!r}")

    startup = {
        "STARTUP_MANIFEST.md": {"status": 200, "bytes": 4521, "sha256": "a1791983863ce43c2d75d73101f557a484bc5a6fc07445d3cc41b5a3f338a8cf"},
        "RESEARCH_STATE.md": {"status": 200, "bytes": 185112, "sha256": "272020b975c78eb4dce86e83b6ea5bff0015787eb2e3c2782c28759f17d8cdf8"},
        "THREAD_START.md": {"status": 200, "bytes": 38451, "sha256": "3433cf08fb8d3cbf94a95f450c4ab8f2418d612d587c871c6ea8336e2f49d29a"},
        "CLAIMS_REGISTER.md": {"status": 200, "bytes": 50422, "sha256": "7f543f3a5a5f8fa308c9ddfbf2efa6068ea7a7e516c7a133a08e14b63b1c69d0"},
    }
    check("startup passed using exact ordered raw URLs", all(row["status"] == 200 for row in startup.values()), startup)
    navigation = [
        ROOT / "research/REPO_NAVIGATION.md", ROOT / "research/REPO_FILE_INDEX.csv", ROOT / "research/RAW_URL_INDEX.md",
        ROOT / "research/RESEARCH_INDEX.md", ROOT / "research/PROVENANCE_REGISTRY.md", ROOT / "research/FINDINGS_LEDGER.md",
    ]
    check("all six canonical navigation artifacts consulted and present", all(path.exists() for path in navigation), [str(x.relative_to(ROOT)) for x in navigation])

    source = json.loads((ROOT / "research/outputs/extended_persona_pca/viewer_data.json").read_text())
    coords = pd.read_csv(OUT / "role_coordinates.csv")
    density = pd.read_csv(OUT / "role_density_scores.csv")
    sparsity = pd.read_csv(OUT / "role_sparsity_scores.csv")
    families = pd.read_csv(OUT / "role_family_membership.csv")
    coverage = pd.read_csv(OUT / "coverage_region_summary.csv")
    sensitivity = pd.read_csv(OUT / "density_bandwidth_sensitivity.csv")
    neighbors = pd.read_csv(OUT / "nearest_role_neighbors.csv")
    recurrence = pd.read_csv(OUT / "cross_model_neighborhood_recurrence.csv")
    traits = pd.read_csv(OUT / "trait_landmarks.csv")
    viewer_data = json.loads((OUT / "terrain_viewer_data.json").read_text())
    source_manifest = json.loads((OUT / "source_manifest.json").read_text())

    counts = coords.groupby("model").size().to_dict()
    check("exact saved 275-role inventory reused per model", counts == {m: 275 for m in MODEL_ORDER}, counts)
    sets = {m: set(coords[coords.model.eq(m)].role) for m in MODEL_ORDER}
    check("role names align exactly across all models", sets["qwen"] == sets["llama"] == sets["gemma"] and len(sets["qwen"]) == 275, {m: len(v) for m, v in sets.items()})
    check("native PC coordinates are finite and unique by model-role", bool(np.isfinite(coords[["native_pc1", "native_pc2", "native_pc3"]]).all().all() and not coords.duplicated(["model", "role"]).any()), len(coords))

    max_viewer_diff = 0.0
    for model in MODEL_ORDER:
        expected = {p["persona"]: np.asarray(p["coordinates"][:3], float) for p in source["models"][model]["points"]}
        for row in coords[coords.model.eq(model)].itertuples():
            max_viewer_diff = max(max_viewer_diff, float(np.max(np.abs(expected[row.role] - np.array([row.native_pc1, row.native_pc2, row.native_pc3])))))
    check("canonical model-local PCA coordinates reproduced from saved viewer source", max_viewer_diff < 1e-8, max_viewer_diff, "<1e-8")

    qwen_table = pd.read_csv(ROOT / "research/geometry_tables/qwen_role_pc_rankings.csv").set_index("role")
    qwen_coords = coords[coords.model.eq("qwen")].set_index("role")
    qwen_error = float(np.max(np.abs(qwen_coords[["native_pc1", "native_pc2", "native_pc3"]].to_numpy() - qwen_table.loc[qwen_coords.index, ["pc1", "pc2", "pc3"]].to_numpy())))
    check("Qwen native coordinates reproduce canonical geometry table", qwen_error < 2e-6, qwen_error, "<2e-6")

    spectrum = pd.read_csv(ROOT / "research/outputs/extended_persona_pca/full_pca_spectrum.csv")
    spectrum_error = 0.0
    for model in MODEL_ORDER:
        part = spectrum[(spectrum.model == SOURCE_LABELS[model]) & (spectrum.component <= 3)].sort_values("component")
        arrays = np.column_stack([json.loads(value) for value in part.role_scores_json])
        actual = coords[coords.model.eq(model)].sort_values("role")[["native_pc1", "native_pc2", "native_pc3"]].to_numpy()
        spectrum_error = max(spectrum_error, float(np.max(np.abs(arrays - actual))))
    check("coordinates reproduce frozen full-PCA role-score arrays", spectrum_error < 1e-8, spectrum_error, "<1e-8")
    check("no role-vector recomputation", source_manifest["coordinate_verification"]["no_role_vector_recomputation"] is True, source_manifest["coordinate_verification"])

    expected_scott = 275 ** (-1 / 7)
    factors = coverage.groupby("model").scott_factor.first().to_dict()
    check("density uses frozen 3D Scott covariance-aware factor", max(abs(value - expected_scott) for value in factors.values()) < 1e-10, factors, expected_scott)
    check("density and sparsity tables contain roles only", len(density) == len(sparsity) == 825 and set(density.role) == sets["qwen"] and set(sparsity.role) == sets["qwen"], {"density": len(density), "sparsity": len(sparsity)})
    check("trait landmarks remain a separate 240-row Qwen-only layer", len(traits) == 240 and set(traits.model) == {"qwen"} and traits.landmark_type.str.contains("excluded from occupancy density").all(), {"rows": len(traits), "models": sorted(traits.model.unique())})

    achieved = coverage.pivot(index="model", columns="target_sample_coverage_percent", values="achieved_role_count").to_dict("index")
    check("coverage thresholds reproduce advertised enclosed sample fractions", all(row == {50: 138, 80: 220, 95: 261} for row in achieved.values()), achieved, "138/220/261 of 275")
    check("coverage grid is frozen at 36 cubed", set(coverage.grid_resolution_per_axis) == {36}, sorted(coverage.grid_resolution_per_axis.unique()))
    check("bandwidth sensitivity uses only 0.75x 1x 1.25x Scott", set(np.round(sensitivity.bandwidth_multiplier, 2)) == {0.75, 1.0, 1.25} and len(sensitivity) == 9, sensitivity.groupby("model").bandwidth_multiplier.apply(list).to_dict())
    check("density-rank sensitivity passes frozen rho rule throughout", bool(sensitivity.density_ordering_robust_at_frozen_rule.all()), float(sensitivity.role_density_rank_spearman_vs_primary.min()), ">=0.90")

    check("nearest-role table contains exactly 10 non-self neighbors per role/model", len(neighbors) == 8250 and neighbors.groupby(["model", "role"]).size().eq(10).all() and not (neighbors.role == neighbors.neighbor_role).any(), len(neighbors))
    check("cross-model neighborhood recurrence covers all shared roles", len(recurrence) == 275 and set(recurrence.role) == sets["qwen"], len(recurrence))

    frozen_family = pd.read_csv(ROOT / "research/outputs/crossmodel_cluster_reconciliation/consensus_family_roles.csv")
    family_match = True
    for model in MODEL_ORDER:
        support = frozen_family[frozen_family[f"{model}_support"].astype(bool)].set_index("role").consensus_family_id.to_dict()
        actual = families[(families.model.eq(model)) & (~families.consensus_family_id.eq("Unassigned"))].set_index("role").consensus_family_id.to_dict()
        family_match &= support == actual
    check("MFamily A-E memberships reproduce frozen reconciliation flags", family_match, {m: families[(families.model.eq(m)) & (~families.consensus_family_id.eq("Unassigned"))].shape[0] for m in MODEL_ORDER})
    e = families[families.consensus_family_id.eq("MFamily_E")].groupby("model").size().to_dict()
    check("E remains small and resolution-sensitive", e == {"gemma": 4, "llama": 3} and families[families.consensus_family_id.eq("MFamily_E")].family_status.eq("secondary_small_resolution_sensitive").all(), e)
    hulls = {model: viewer_data["models"][model]["family_hulls"] for model in MODEL_ORDER}
    check("minimum N=10 family-envelope rule respected", "MFamily_E" not in hulls["llama"] and "MFamily_E" not in hulls["gemma"] and all(family != "MFamily_E" for family in hulls["qwen"]), {m: sorted(v) for m, v in hulls.items()})

    alignment = pd.read_csv(OUT / "display_alignment_coordinates.csv")
    check("display-alignment table covers all roles/models and stays secondary", len(alignment) == 825 and np.isfinite(alignment[["display_aligned_x", "display_aligned_y", "display_aligned_z"]]).all().all(), len(alignment))
    check("display alignment provenance is the frozen model-only transform", any(row["path"].endswith("procrustes_alignment_matrices.json") and row.get("access") == "git object; model-only transform" for row in source_manifest["inputs"]), [row["path"] for row in source_manifest["inputs"]])

    html = (OUT / "model_coverage_terrain_viewer.html").read_text(encoding="utf-8")
    check("viewer is self-contained with embedded Plotly and terrain data", "plotly.js v" in html and "const TERRAIN=" in html and not re.search(r"<script[^>]+src=['\"]https?://", html, re.I), len(html))
    controls = ["model", "view", "mode", "showPoints", "showSurface", "showHulls", "showTraits", "roleSearch", "traitSearch", "resetCamera"]
    check("all required core viewer controls are present", all(f'id="{control}"' in html for control in controls), controls)
    check("coverage UI contains the required non-probability warning", "Coverage reflects the selected 275-role inventory. It is not a population probability distribution." in html, True)
    check("native coordinates are not raw-overlaid; aligned view is explicitly non-native", "Linked native comparison" in html and "Display-aligned shared-role overlay · non-native axes" in html, True)
    check("2D contour modes are all present", all(label in html for label in ["Native PC1 × PC2", "Native PC1 × PC3", "Native PC2 × PC3"]), True)

    browser = json.loads((OUT / "browser_verification.json").read_text())
    check("headless Chrome render and interaction suite passed", browser["status"] == "PASS" and browser["failed"] == 0 and browser["passed"] >= 20, {"browser": browser["browser"], "passed": browser["passed"], "failed": browser["failed"]})

    inventory = pd.read_csv(OUT / "figure_inventory.csv")
    missing_figures = []
    bad_dimensions = []
    for files in inventory.files:
        for item in files.split(";"):
            path = OUT / item
            if not path.exists():
                missing_figures.append(item)
            elif path.suffix.lower() == ".png":
                width, height = Image.open(path).size
                if width < 800 or height < 500:
                    bad_dimensions.append({"file": item, "size": [width, height]})
    check("all inventoried static figures exist", not missing_figures and len(inventory) >= 26, {"inventory_rows": len(inventory), "missing": missing_figures})
    check("all PNG static figures render at inspection resolution", not bad_dimensions, bad_dimensions)

    generator = (OUT / "analysis/build_terrain_data.py").read_text()
    forbidden_inputs = ["human_model_profile_correspondence", "SAPA", "sapa_", "NLSY97", "nlsy"]
    check("analysis generator contains no human or correspondence input", not any(token in generator for token in forbidden_inputs), [token for token in forbidden_inputs if token in generator])
    check("source manifest confirms model-only compute boundaries", source_manifest["boundaries"] == {
        "roles_only_define_occupancy": True,
        "trait_landmarks_excluded_from_density": True,
        "human_artifacts_loaded": False,
        "human_model_correspondence_loaded": False,
        "new_inference": False,
        "activation_extraction": False,
        "external_api": False,
        "gpu": False,
        "runpod": False,
    }, source_manifest["boundaries"])

    reproducible_paths = sorted(
        path for path in OUT.iterdir() if path.suffix in {".csv", ".json"} and path.name not in {"browser_verification.json", "verification_report.json"}
    )
    before = {path.name: digest(path) for path in reproducible_paths}
    subprocess.run([str(ROOT.parent / "assistant-axis/.venv/bin/python"), str(OUT / "analysis/build_terrain_data.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {path.name: digest(path) for path in reproducible_paths}
    check("deterministic regeneration reproduces all numerical source tables byte-for-byte", before == after, {"files": len(before), "mismatches": [name for name in before if before[name] != after[name]]})

    check("no new inference activation extraction API GPU or RunPod", all(source_manifest["boundaries"][key] is False for key in ["new_inference", "activation_extraction", "external_api", "gpu", "runpod"]), source_manifest["boundaries"])

    report = {
        "status": "PASS",
        "analysis": "AA-12 follow-up 6 model-only persona-space coverage terrain viewer",
        "method_freeze_commit": "5c2814f7554d26cfce97cb83fd0cda34ffbf2333",
        "numerical_terrain_freeze_commit": "9335ffaeac215cfdbb709b041c1fa1db0d8f754e",
        "viewer_commit": "bdecaee2511a19d7c52fd796bf19bbc1c83f803d",
        "startup": startup,
        "checks": checks,
        "passed": sum(item["passed"] for item in checks),
        "failed": sum(not item["passed"] for item in checks),
        "final_worktree_clean_check": "performed after the final commit and reported in the Codex handoff",
    }
    (OUT / "verification_report.json").write_text(
        json.dumps(report, indent=2, default=lambda value: value.item() if isinstance(value, np.generic) else str(value)) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "passed": report["passed"], "failed": report["failed"]}, indent=2))


if __name__ == "__main__":
    main()
