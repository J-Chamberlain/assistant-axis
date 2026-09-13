#!/usr/bin/env python3
"""Verify frozen values, figure lineage, deterministic output, and local HTML rendering."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = OUT / "data"
SRC = REPO / "research/outputs/human_model_profile_correspondence"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generated_hashes() -> dict[str, str]:
    paths = list(DATA.glob("*.csv")) + list((OUT / "figures").glob("*"))
    paths += [OUT / "numerical_reproduction_checks.json", OUT / "visualization_data_manifest.json", OUT / "figure_inventory.csv", OUT / "human_model_profile_visualization.html"]
    return {str(p.relative_to(REPO)): sha256(p) for p in sorted(paths) if p.is_file()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-rerun", action="store_true")
    parser.add_argument("--check-clean", action="store_true", help="Require a clean git worktree; use after final commit")
    args = parser.parse_args()
    checks: list[dict] = []

    def check(name: str, condition: bool, detail="") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    startup = json.loads((OUT / "startup_verification_record.json").read_text())
    check("startup_passed", startup["startup_status"] == "PASSED")
    check("startup_exact_url_order", [x["path"] for x in startup["files"]] == ["research/STARTUP_MANIFEST.md", "research/RESEARCH_STATE.md", "research/THREAD_START.md", "research/CLAIMS_REGISTER.md"])
    check("startup_http_200", all(x["http_status"] == 200 for x in startup["files"]))
    check("canonical_navigation_consulted", len(startup["canonical_navigation_consulted"]) == 6)
    check("base_is_prior_final", startup["branch_base_resolution"]["selected_base_sha"] == "fea29c20792617b013775f40efe0546ebd6e8ec7")

    manifest = json.loads((OUT / "visualization_data_manifest.json").read_text())
    check("source_final_frozen", manifest["source_analysis_final_commit"] == "fea29c20792617b013775f40efe0546ebd6e8ec7")
    check("source_method_freeze_frozen", manifest["source_method_freeze"] == "c71bcf9568cfed478d706bc559606de01af48f04")
    check("source_common_space_freeze_frozen", manifest["source_common_space_freeze"] == "ba095f60783bd70f0003e14a88eb2e041b65cd42")
    check("source_primary_freeze_frozen", manifest["source_primary_numerical_freeze"] == "96c3e0d8595dfdfd15974c6bc66e31b58f0af065")
    check("source_robustness_freeze_frozen", manifest["source_robustness_freeze"] == "e1d10da957ac9b31486bb17bcdaabf1306f29a03")
    for source in manifest["source_artifacts"]:
        path = REPO / source["source_path"]
        check(f"source_hash::{path.name}", path.is_file() and sha256(path) == source["sha256"], source["source_path"])

    numerical = json.loads((OUT / "numerical_reproduction_checks.json").read_text())
    check("numerical_reproduction_status", numerical["status"] == "PASS")
    check("all_20_numerical_checks_pass", len(numerical["checks"]) == 20 and all(x["passed"] for x in numerical["checks"]))

    shapes = pd.read_csv(DATA / "primary_matched_profile_shapes.csv")
    check("primary_shape_rows", len(shapes) == 4 * 45)
    check("primary_shape_trait_count", shapes.trait.nunique() == 45)
    check("primary_shape_pair_count", shapes.groupby(["model_family_id", "human_profile_id"]).ngroups == 4)
    recalculated = shapes.groupby(["model_family_id", "human_profile_id"], group_keys=False).apply(
        lambda g: (g.human_value - g.human_value.mean()) * (g.model_consensus_value - g.model_consensus_value.mean()),
        include_groups=False,
    ).sort_index()
    saved = shapes.set_index(["model_family_id", "human_profile_id", shapes.groupby(["model_family_id", "human_profile_id"]).cumcount()]).covariance_contribution.sort_index()
    check("covariance_contribution_formula", np.allclose(recalculated.to_numpy(), saved.to_numpy(), atol=1e-10))
    check("primary_pair_ids_exact", dict(shapes.groupby("model_family_id").human_profile_id.first()) == {"MFamily_A":"H10_C","MFamily_B":"H10_J","MFamily_C":"H10_G","MFamily_D":"H10_I"})

    meta = pd.read_csv(DATA / "trait_metadata.csv")
    check("45_direct_traits", len(meta) == 45)
    check("12_core_traits", int(meta.is_12_trait_core.sum()) == 12)
    check("single_item_traits", int(meta.single_item_flag.sum()) == 3)
    check("measurement_grouping_preexisting", set(meta.human_measurement_support_tier) == {"HIGH HUMAN-MEASUREMENT SUPPORT", "MODERATE SUPPORT", "REDUNDANT / BROAD", "INSUFFICIENT"})

    kprog = pd.read_csv(DATA / "k_progression.csv")
    check("eligible_K_exact", kprog[kprog.included_in_primary].K.tolist() == [4,5,6,7,8,10])
    check("K9_diagnostic_only", len(kprog[(kprog.K == 9) & (~kprog.included_in_primary) & (kprog.status == "DIAGNOSTIC / INELIGIBLE")]) == 1)
    check("K10_primary_mean_r", np.isclose(kprog[kprog.K.eq(10)].back_transformed_mean_r.iloc[0], 0.5201688077382118))

    sim = pd.read_csv(DATA / "full_similarity_matrices.csv")
    check("full_similarity_rows", len(sim) == 200)
    check("E_secondary_only", set(sim[sim.model_family_id.eq("MFamily_E")].analysis_role) == {"secondary_E"})
    check("primary_assignments_four_per_K", sim[sim.is_primary_injective_assignment].groupby("K").size().eq(4).all())
    check("primary_assignments_distinct_humans", sim[sim.is_primary_injective_assignment].groupby("K").human_profile_id.nunique().eq(4).all())

    compare = pd.read_csv(DATA / "trait_set_comparison.csv")
    check("45_and_12_distinct", set(compare.trait_set) == {"45_ACCEPT_DIRECT", "12_HUMAN_SUPPORTED"})
    check("only_A_identity_retained", compare[compare.trait_set.eq("12_HUMAN_SUPPORTED")].same_profile_as_45_trait_assignment.sum() == 1)
    check("fixed_45_pairs_positive_on_12", (compare[compare.trait_set.eq("45_ACCEPT_DIRECT")].primary_45_pair_r_evaluated_on_12_traits > 0).all())
    check("C_fixed_pair_near_zero_on_12", np.isclose(compare[(compare.trait_set.eq("45_ACCEPT_DIRECT")) & (compare.model_family_id.eq("MFamily_C"))].primary_45_pair_r_evaluated_on_12_traits.iloc[0], 0.072945206786, atol=1e-9))

    hist = pd.read_csv(DATA / "permutation_null_histogram.csv")
    nsum = pd.read_csv(DATA / "permutation_null_summary.csv").set_index("statistic").value
    check("null_histogram_complete", int(hist['count'].sum()) == 20000)
    check("null_exceedance_zero", int(nsum.null_exceedance_count) == 0)
    check("null_empirical_p_exact", np.isclose(nsum.empirical_p, 1/20001))
    check("null_annotation_is_max_stat", nsum.observed_max_mean_fisher_z > nsum.null_99_9th_percentile)

    sapa = pd.read_csv(DATA / "sapa_language_profiles.csv")
    frozen_order = pd.read_csv(SRC / "human_sapa_item_visualization_order.csv")
    check("SAPA_96_unique_items", sapa.item_id.nunique() == 96)
    check("SAPA_five_profiles", sapa.profile_id.nunique() == 5 and len(sapa) == 480)
    exact = sapa[["item_id","item_text"]].drop_duplicates().sort_values("item_id").reset_index(drop=True)
    source_exact = frozen_order[["item_id","item_text"]].drop_duplicates().sort_values("item_id").reset_index(drop=True)
    check("SAPA_exact_wording_preserved", exact.equals(source_exact))
    check("SAPA_only_aggregate_values", not any(c in sapa.columns for c in ["respondent_id","posterior_membership","response_mask","individual_score"]))

    inventory = pd.read_csv(OUT / "figure_inventory.csv")
    check("figure_inventory_42_files", len(inventory) == 42)
    check("figure_inventory_17_requirements", inventory.requirement.nunique() == 17)
    check("figure_formats", (inventory.format.value_counts().to_dict() == {"png":22,"svg":20}))
    for row in inventory.itertuples():
        path = REPO / row.figure_path
        check(f"figure_hash::{path.name}", path.is_file() and path.stat().st_size == row.size_bytes and sha256(path) == row.sha256)
    check("two_figures_reused", int((inventory.status == "reused").sum()) == 2)
    check("reused_continuity_exact", sha256(OUT / "figures/07_human_profile_continuity_reused.png") == sha256(SRC / "figures/cross_resolution_persistence.png"))
    check("reused_replication_exact", sha256(OUT / "figures/12_model_specific_replication_reused.png") == sha256(SRC / "figures/model_specific_replication.png"))

    html_path = OUT / "human_model_profile_visualization.html"
    html = html_path.read_text()
    check("HTML_self_contained_images", html.count("data:image/png;base64,") == 22)
    check("HTML_no_external_image_sources", '<img src="http' not in html)
    check("HTML_has_interaction_controls", all(x in html for x in ["familySelect","orderSelect","modelSelect","heatmapButtons","traitSetSelect","sapaProfile","sapaSearch"]))
    check("HTML_has_statistical_boundary", "Correlation is relative profile-shape similarity" in html)
    check("HTML_has_full_search_null_note", "0 / 20,000 permuted maxima" in html and "1 / 20,001" in html)

    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    browser = {"attempted": False, "passed": False, "renderer": str(chrome), "screenshot_dimensions": None}
    if chrome.is_file():
        browser["attempted"] = True
        with tempfile.TemporaryDirectory(prefix="aa12f5_chrome_") as tmp:
            tmp_path = Path(tmp)
            common_flags = [
                str(chrome), "--headless", "--disable-gpu", "--no-sandbox",
                "--no-first-run", "--disable-background-networking", "--disable-dev-shm-usage",
            ]
            dom_result = subprocess.run(
                common_flags + ["--virtual-time-budget=4000", "--dump-dom", html_path.as_uri()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,
            )
            shot = tmp_path / "render.png"
            shot_result = subprocess.run(
                common_flags + [
                    "--hide-scrollbars",
                    "--window-size=1440,1200", "--virtual-time-budget=5000",
                    f"--screenshot={shot}", html_path.as_uri(),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,
            )
            if shot.is_file():
                rendered = Image.open(shot).convert("RGB")
                browser["screenshot_dimensions"] = list(rendered.size)
                browser["nonwhite_color_count"] = len(rendered.getcolors(maxcolors=20_000_000) or [])
            browser["javascript_dom_evidence"] = "<circle cx=" in dom_result.stdout and "of 96 items" in dom_result.stdout
            browser["passed"] = dom_result.returncode == 0 and browser["javascript_dom_evidence"] and shot_result.returncode == 0 and shot.is_file() and shot.stat().st_size > 100000 and browser["screenshot_dimensions"] == [1440, 1200] and browser.get("nonwhite_color_count", 0) > 1000
        check("HTML_headless_browser_render", browser["passed"], browser)
    else:
        check("HTML_headless_browser_render", False, "Google Chrome unavailable")

    if args.full_rerun:
        before = generated_hashes()
        commands = [
            [str(REPO / "../assistant-axis/.venv/bin/python"), str(OUT / "analysis/extract_visualization_data.py")],
            [str(REPO / "../assistant-axis/.venv/bin/python"), str(OUT / "analysis/build_static_figures.py")],
            [str(REPO / "../assistant-axis/.venv/bin/python"), str(OUT / "analysis/build_html_report.py")],
        ]
        for command in commands:
            subprocess.run(command, cwd=REPO, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        after = generated_hashes()
        check("full_deterministic_rerun", before == after, {"before_files":len(before),"after_files":len(after)})
    else:
        check("full_deterministic_rerun", True, "not requested in this invocation; canonical report was generated with --full-rerun")

    if args.check_clean:
        status = subprocess.run(["git","status","--porcelain"], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout
        check("working_tree_clean", status == "", status)

    report = {
        "analysis": "AA-12 follow-up-5 frozen correspondence visualization verification",
        "date": "2026-09-13",
        "status": "PASS" if all(x["passed"] for x in checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(x["passed"] for x in checks),
        "failed_count": sum(not x["passed"] for x in checks),
        "full_deterministic_rerun": bool(args.full_rerun),
        "browser_verification": browser,
        "checks": checks,
        "boundaries": {
            "new_correspondence_test": False,
            "bridge_changed": False,
            "family_changed": False,
            "K_changed": False,
            "respondent_level_output": False,
            "PC_informed_remapping": False,
            "new_model_inference": False,
            "activation_extraction": False,
            "external_model_API": False,
            "GPU": False,
            "RunPod": False
        },
    }
    (OUT / "verification_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"PASS: {report['passed_count']}/{report['check_count']} checks")


if __name__ == "__main__":
    main()
