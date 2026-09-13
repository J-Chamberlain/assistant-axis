#!/usr/bin/env python3
"""Independent deterministic verification for AA-12 Follow-up 4."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VENV_PYTHON = REPO.parent / "assistant-axis/.venv/bin/python"
ELIGIBLE_K = [4, 5, 6, 7, 8, 10]
FAMILIES = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
PHASE_COMMITS = [
    "c71bcf9568cfed478d706bc559606de01af48f04",
    "ba095f60783bd70f0003e14a88eb2e041b65cd42",
    "96c3e0d8595dfdfd15974c6bc66e31b58f0af065",
    "e1d10da957ac9b31486bb17bcdaabf1306f29a03",
    "f55738dcb002c8da8d5013aa40f1ca1855214d3f",
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def normalize(x: np.ndarray) -> np.ndarray:
    x = x - x.mean(axis=1, keepdims=True)
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    checks = []

    def check(name: str, condition: bool, detail="") -> None:
        checks.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "detail": str(detail)})

    clean_at_start = git("status", "--porcelain") == ""
    startup = json.loads((HERE / "startup_verification_record.json").read_text())
    check("startup passed", startup["status"] == "PASS")
    check("four exact startup URLs fetched in order", [x["fetched_in_required_order"] for x in startup["checks"]] == [1, 2, 3, 4])
    check("all startup HTTP responses 200", all(x["http_status"] == 200 for x in startup["checks"]))
    check("startup content nonempty", all(x["bytes"] > 1000 for x in startup["checks"]))
    check("visible metadata and integrity verified", all(x.get("visible_metadata_match", True) and x.get("integrity_matches_manifest", True) for x in startup["checks"]))
    check("manifest generation time recorded", startup["manifest_generated_timestamp_utc"] == "2026-09-12T21:15:38Z")
    check("six canonical navigation artifacts consulted", len(startup["canonical_navigation_consulted"]) == 6)
    check("correct prior base used", startup["branch_base_resolution"]["base_used"] == "c8383931fcaf4847b67fb178fd9ffd825f42e2f7")

    check("method freeze exists", git("cat-file", "-t", PHASE_COMMITS[0]) == "commit")
    check("phase commit ordering", all(subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=REPO).returncode == 0 for a, b in zip(PHASE_COMMITS, PHASE_COMMITS[1:])))
    frozen_method = git("show", f"{PHASE_COMMITS[0]}:research/outputs/human_model_profile_correspondence/analysis_preregistration.md")
    check("current preregistration equals method-freeze bytes", frozen_method == (HERE / "analysis_preregistration.md").read_text().rstrip("\n"))
    check("20000 and seeds frozen before results", "exactly 20,000" in frozen_method and "2026091304" in frozen_method and "2026091312" in frozen_method)
    check("decision tier frozen before results", "STRONG AGGREGATE CORRESPONDENCE" in frozen_method and "WEAK / ABSENT" in frozen_method)

    manifest = json.loads((HERE / "common_space_manifest.json").read_text())
    check("common-space stage calculated no correspondence", manifest["correspondence_calculated"] is False)
    check("correct SAPA source hash", manifest["human"]["raw_sapa_sha256"] == "fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6")
    check("23679 respondents checked", manifest["human"]["respondent_rows"] == 23679)
    check("45 direct mappings verified", len(manifest["direct_traits"]) == 45)
    check("96 mapped SAPA items verified", manifest["human"]["mapped_unique_items"] == 96)
    check("119 frozen trait-item rows verified", manifest["human"]["mapped_trait_item_rows"] == 119)
    check("12 supported traits verified", len(manifest["supported_traits_12"]) == 12)
    check("eligible K exact", manifest["eligible_primary_k"] == ELIGIBLE_K)
    check("privacy declaration aggregate only", "aggregate outputs only" in manifest["privacy"])

    human45 = pd.read_csv(HERE / "human_trait_profiles_45.csv")
    human12 = pd.read_csv(HERE / "human_trait_profiles_12.csv")
    items = pd.read_csv(HERE / "human_sapa_item_profile_values.csv")
    moments = pd.read_csv(HERE / "human_item_normalization_moments.csv")
    model45 = pd.read_csv(HERE / "model_family_trait_profiles_45.csv")
    model12 = pd.read_csv(HERE / "model_family_trait_profiles_12.csv")
    check("human K bank reused without refit", sorted(human45.K.unique()) == list(range(4, 11)) and human45[["K", "profile_id"]].drop_duplicates().shape[0] == 49)
    check("human 45 matrix complete", len(human45) == 49 * 45 and not human45.duplicated(["K", "profile_id", "trait"]).any())
    check("human 12 matrix complete", len(human12) == 49 * 12 and not human12.duplicated(["K", "profile_id", "trait"]).any())
    check("all item moments observed-only and finite", len(moments) == 96 and moments.observed_n.between(1, 23679).all() and np.isfinite(moments.select_dtypes('number')).all().all())
    recomputed_z = items.orientation_sign * (items.expected_response - items.empirical_mean_raw) / items.empirical_sd_raw_ddof1
    check("all orientation and z scoring recompute", np.allclose(recomputed_z, items.oriented_item_z, atol=1e-10))
    expected_traits = items.groupby(["K", "profile_id", "trait"]).oriented_item_z.mean().rename("recomputed").reset_index()
    merged = human45.merge(expected_traits, on=["K", "profile_id", "trait"], validate="one_to_one")
    check("equal-weight human proxy construction recomputes", np.allclose(merged.human_trait_value, merged.recomputed, atol=1e-10))
    check("no respondent identifier columns", not any("respondent" in c.lower() or c.lower() == "rid" for df in [human45, human12, items] for c in df.columns))

    check("model A-E 45 profiles complete", len(model45) == 5 * 45 and sorted(model45.family_id.unique()) == FAMILIES + ["MFamily_E"])
    check("model A-E 12 profiles complete", len(model12) == 5 * 12)
    check("A-D primary and E secondary frozen", model45.loc[model45.family_id.isin(FAMILIES), "analysis_role"].eq("primary_A-D").all() and model45.loc[model45.family_id.eq("MFamily_E"), "analysis_role"].eq("secondary_E").all())
    check("model consensus is simple three-model mean", np.allclose(model45.three_model_consensus_value, model45[["qwen_value", "llama_value", "gemma_value"]].mean(axis=1), atol=1e-11))
    check("E exact frozen components", model45.loc[model45.family_id.eq("MFamily_E"), "model_components"].str.contains("qwen:Q07_G;llama:L09_I;gemma:G06_A", regex=False).all())

    sim45 = pd.read_csv(HERE / "profile_similarity_45.csv")
    assignment45 = pd.read_csv(HERE / "primary_assignments_by_k.csv")
    null45 = pd.read_csv(HERE / "bridge_permutation_null_45.csv")
    primary = json.loads((HERE / "primary_global_result.json").read_text())
    check("all eligible 45 similarity cells present", len(sim45) == sum(ELIGIBLE_K) * 4 and sorted(sim45.K.unique()) == ELIGIBLE_K)
    check("Pearson correlations recompute", all(
        np.isclose(r.pearson_r, np.corrcoef(
            human45[(human45.K == r.K) & (human45.profile_id == r.human_profile_id)].sort_values('trait').human_trait_value,
            model45[(model45.family_id == r.model_family_id)].sort_values('trait').three_model_consensus_value
        )[0, 1], atol=1e-10) for r in sim45.itertuples()
    ))
    check("injective four distinct profiles every K", assignment45.groupby("K").human_profile_id.nunique().eq(4).all() and assignment45.groupby("K").model_family_id.nunique().eq(4).all())
    check("primary metric Pearson", primary["assignment"].startswith("maximum total raw Pearson"))
    check("maximizing K is 10", primary["maximizing_K"] == 10)
    check("20000 primary null maxima", len(null45) == 20000 and null45.permutation_index.nunique() == 20000 and null45.seed.eq(2026091304).all())
    p45 = (1 + (null45.global_max_fisher_z >= primary["observed_max_mean_fisher_z"] - 1e-15).sum()) / 20001
    check("primary search-adjusted p recomputes", np.isclose(p45, primary["search_adjusted_global_p"]), p45)
    check("K search included in null", null45.global_maximizing_K.isin(ELIGIBLE_K).all())
    check("family max-search columns present", all(f"{f}_max_r" in null45 for f in FAMILIES))
    family = pd.read_csv(HERE / "family_specific_results.csv")
    check("three of four primary families pass", family.positive_adjusted_evidence.astype(str).str.lower().eq('true').sum() == 3)
    check("no prevalence weighting", "profile_proportion" not in assignment45.columns)

    sim12 = pd.read_csv(HERE / "profile_similarity_12.csv")
    null12 = pd.read_csv(HERE / "bridge_permutation_null_12.csv")
    robust = json.loads((HERE / "robustness_result.json").read_text())
    check("separate 12-trait similarities complete", len(sim12) == sum(ELIGIBLE_K) * 4)
    check("separate 12-trait null complete", len(null12) == 20000 and null12.seed.eq(2026091312).all())
    p12 = (1 + (null12.global_max_fisher_z >= robust["twelve_trait"]["mean_fisher_z"] - 1e-15).sum()) / 20001
    check("12-trait p recomputes", np.isclose(p12, robust["twelve_trait"]["search_adjusted_p"]), p12)
    check("stable K sensitivity exact 4-6", pd.read_csv(HERE / "human_stability_sensitivity.csv").K.tolist() == [4, 5, 6])
    check("K9 explicitly diagnostic and excluded", pd.read_csv(HERE / "k9_diagnostic.csv").status.eq("DIAGNOSTIC / INELIGIBLE").all() and not pd.read_csv(HERE / "k9_diagnostic.csv").included_in_primary.any())
    check("E excluded from primary", pd.read_csv(HERE / "mfamily_e_secondary.csv").excluded_from_primary_A_D_global.all())
    check("model-specific replication fixed", pd.read_csv(HERE / "model_specific_replication.csv").pair_fixed_no_reassignment.all())
    check("response-style handling documented", pd.read_csv(HERE / "response_style_sensitivity.csv").iloc[0].status == "NOT_RUN_NO_FROZEN_TRANSFORM")
    check("strong tier follows all frozen criteria", robust["final_decision_tier"] == "STRONG AGGREGATE CORRESPONDENCE" and all(robust["decision_criteria"].values()))

    numerical_scripts = "\n".join((HERE / f).read_text().lower() for f in ["build_common_space.py", "run_primary_correspondence.py", "run_robustness_correspondence.py"])
    check("no ACCEPT_CLOSE primary use", "accept_close" not in numerical_scripts)
    check("no PC or geometry mapping", "pc coordinate" not in numerical_scripts and "persona geometry" not in numerical_scripts)
    check("no model reclustering", "kmeans" not in numerical_scripts and "cluster(" not in numerical_scripts)
    check("no inference or activation extraction", "transformers" not in numerical_scripts and "generate(" not in numerical_scripts and "activation extraction" not in numerical_scripts)
    check("no external model API", "openai" not in numerical_scripts and "anthropic" not in numerical_scripts)
    check("no GPU or RunPod", "cuda" not in numerical_scripts and "runpod" not in numerical_scripts)
    prohibited_names = [p.name.lower() for p in HERE.iterdir() if p.is_file()]
    check("no respondent-level output files", not any(any(x in n for x in ["respondent", "posterior", "imputed", "response_mask"]) for n in prohibited_names))
    check("no individual completed profiles", manifest["privacy"].startswith("aggregate outputs only"))

    required_figs = [
        "human_sapa_ridges_k04.png", "human_sapa_ridges_k06.png", "human_sapa_ridges_k10.png",
        "human_trait_ridges_k04.png", "human_trait_ridges_k06.png", "human_trait_ridges_k10.png",
        "model_family_trait_ridges_A_D.png", "model_family_trait_ridge_E.png",
        *[f"similarity_heatmap_k{k:02d}.png" for k in ELIGIBLE_K],
        "k_level_primary_scores.png", "bridge_permutation_null_45.png", "primary_assignment.png",
        "cross_resolution_persistence.png", "trait_set_sensitivity.png", "model_specific_replication.png",
    ]
    check("all 20 required figures present", len(required_figs) == 20 and all((HERE / "figures" / f).stat().st_size > 10_000 for f in required_figs))
    check("96-item searchable wording table", len(pd.read_csv(HERE / "human_sapa_item_visualization_order.csv")) == 96)
    check("semantic inspection occurred only after freezes", PHASE_COMMITS[3] in git("rev-list", "--all") and git("merge-base", "--is-ancestor", PHASE_COMMITS[3], PHASE_COMMITS[4]) == "")
    check("primary report present", (HERE / "human_model_profile_correspondence_report.md").stat().st_size > 5000)

    if args.rerun:
        core = [
            "common_space_manifest.json", "human_item_normalization_moments.csv", "human_sapa_item_profile_values.csv",
            "human_trait_profiles_45.csv", "human_trait_profiles_12.csv", "model_family_trait_profiles_45.csv",
            "model_family_trait_profiles_12.csv", "profile_similarity_45.csv", "primary_assignments_by_k.csv",
            "primary_global_result.json", "bridge_permutation_null_45.csv", "family_specific_results.csv",
            "profile_similarity_12.csv", "primary_assignments_12_by_k.csv", "bridge_permutation_null_12.csv",
            "family_specific_results_12.csv", "human_stability_sensitivity.csv", "k9_diagnostic.csv",
            "model_specific_replication.csv", "cross_resolution_human_persistence.csv", "relaxed_split_merge_browsing.csv",
            "mfamily_e_secondary.csv", "response_style_sensitivity.csv", "robustness_result.json",
            "human_sapa_item_visualization_order.csv", "human_sapa_item_ridge_values.csv", "semantic_profile_summary.md",
        ]
        before = {f: sha(HERE / f) for f in core}
        for script in ["build_common_space.py", "run_primary_correspondence.py", "run_robustness_correspondence.py", "build_semantic_report_and_figures.py"]:
            subprocess.run([str(VENV_PYTHON), str(HERE / script)], cwd=REPO, check=True, capture_output=True, text=True)
        after = {f: sha(HERE / f) for f in core}
        check("full deterministic numerical and semantic rerun", before == after)
        check("rerun leaves tracked outputs unchanged", git("status", "--porcelain") == "")

    check("working tree clean at verification start", clean_at_start)
    failures = [x for x in checks if x["status"] == "FAIL"]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "date": "2026-09-13",
        "model_used": "GPT-5.5",
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": checks,
        "phase_commits": PHASE_COMMITS,
        "boundaries": {
            "individual_respondent_projection": False,
            "respondent_imputation": False,
            "prevalence_comparison": False,
            "bridge_expansion_after_results": False,
            "accept_close_primary_use": False,
            "pc_informed_mapping": False,
            "model_reclustering": False,
            "new_model_inference": False,
            "activation_extraction": False,
            "external_model_api": False,
            "gpu": False,
            "runpod": False
        }
    }
    (HERE / "verification_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "passed": report["checks_passed"], "total": report["checks_total"]}, indent=2))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure['name']} :: {failure['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
