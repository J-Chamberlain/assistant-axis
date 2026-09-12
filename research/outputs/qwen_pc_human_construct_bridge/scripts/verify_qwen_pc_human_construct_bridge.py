#!/usr/bin/env python3
"""Verify and inventory the Qwen-first human-construct bridge."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "research/outputs/qwen_pc_human_construct_bridge"
BRANCH = "codex/aa1-qwen-human-construct-bridge"
STARTING_COMMIT = "4b568f3a8062203a288a412ea447829de455f586"
CLAUDE_SHA = "71902fbe78fd4dec9742af8ca25a1c27dd9429263f3319a85937b85fd3a9a86a"
CODEX_REVIEW_SHA = "f8e77caf9f5970ac8c48743e8422f04a146ac8013fb3cac5a88b1069c82c29a6"
GENERATED_AT = "2026-09-12T10:45:00Z"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def kappa(labels_a: list[str], labels_b: list[str]) -> float:
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("Kappa inputs differ or are empty")
    categories = sorted(set(labels_a) | set(labels_b))
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / len(labels_a)
    count_a, count_b = Counter(labels_a), Counter(labels_b)
    expected = sum(count_a[c] * count_b[c] for c in categories) / len(labels_a) ** 2
    return (observed - expected) / (1.0 - expected)


def build_source_manifest() -> dict[str, object]:
    source_paths = {
        "external_claude_review": OUT / "sapa_category3_blinded_review_judgments.csv",
        "codex_frozen_review": REPO / "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_second_pass_review.csv",
        "codex_frozen_packet": REPO / "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_blinded_review_packet.csv",
        "sapa_item_dictionary": REPO / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv",
        "sapa_scale_inventory": REPO / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv",
        "sapa_raw_responses_gitignored": REPO / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/sapaTempData696items08dec2013thru26jul2014.tab",
        "sapa_official_scoring_keys_gitignored": REPO / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/superKey696.csv",
        "sapa_official_item_info_gitignored": REPO / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/ItemInfo696.csv",
        "qwen_canonical_pc1_pc3": REPO / "research/geometry_tables/qwen_role_pc_rankings.csv",
        "qwen_trait_profiles": REPO / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
        "qwen_extended_trait_associations": REPO / "research/outputs/extended_persona_pca/qwen_extended_pc_trait_associations.csv",
        "qwen_extended_role_rankings": REPO / "research/outputs/extended_persona_pca/qwen_extended_pc_role_rankings.csv",
        "qwen_extended_browser_bundle": REPO / "research/outputs/extended_persona_pca/viewer_data.json",
        "aa3_component_retention": REPO / "research/outputs/extended_persona_pca/component_retention_summary.csv",
        "aa4_pc_specific_rankings": REPO / "research/outputs/qwen_trait_sparsity_prediction/pc_specific_trait_rankings.csv",
        "aa4_conditional_importance": REPO / "research/outputs/qwen_trait_sparsity_prediction/full_model_permutation_importance.csv",
        "aa2_qwen_big_five_role_scores": REPO / "research/outputs/externally_anchored_big_five/big_five_role_scores.csv",
        "pc1_accountability": REPO / "research/outputs/pc1_accountability_validation/experiment_summary.csv",
        "qwen_interpretation_note": REPO / "research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md",
    }
    records = []
    for role, path in source_paths.items():
        records.append({
            "role": role,
            "path": str(path.relative_to(REPO)),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "tracked": bool(git("ls-files", "--error-unmatch", str(path.relative_to(REPO))) if not str(path.relative_to(REPO)).startswith("data_external/") else ""),
        })
    for record in records:
        if record["path"].startswith("data_external/"):
            record["tracked"] = False
            record["privacy"] = "gitignored local human microdata/metadata; no respondent rows committed"
    manifest = {
        "generated_at_utc": GENERATED_AT,
        "analysis_model": "GPT-5.5",
        "starting_commit": STARTING_COMMIT,
        "branch": BRANCH,
        "discovery_model": "Qwen/Qwen3-32B",
        "external_reviewer": {
            "reviewer": "Claude Opus 5",
            "provider": "Anthropic",
            "review_date": "2026-09-11",
            "review_sha256": CLAUDE_SHA,
            "structural_conflict": "Anthropic-produced AI system",
            "independence_boundary": "Genuinely separate from prior Codex semantic decisions and downstream geometry to the extent documented by the reviewer; not independent human psychometric expertise.",
        },
        "human_dataset": {
            "dataset": "SAPA 696-item release V5",
            "institution": "Harvard Dataverse / SAPA Project",
            "doi": "10.7910/DVN/SD7SVE",
            "license": "CC0 per versioned Dataverse metadata",
            "respondents": 23679,
            "raw_data_committed": False,
        },
        "sources": records,
        "public_construct_sources": {
            "IPIP": "https://ipip.ori.org/",
            "BFAS": "https://ipip.ori.org/BFASKeys.htm",
            "HEXACO": "https://hexaco.org/scaledescriptions",
            "SAPA_SPI": "https://www.sapa-project.org/research/SPI/SPIdevelopment.pdf",
            "Questionnaire_Big_Six": "https://doi.org/10.1037/a0024165",
            "EPQ_R": "https://doi.org/10.1016/0191-8869(85)90026-1",
            "Big_Five_metatraits": "https://doi.org/10.1037/0022-3514.91.6.1138",
            "Need_for_Cognitive_Closure": "https://doi.org/10.1037/0022-3514.67.6.1049",
        },
        "dependency_order": [
            "external review agreement and metadata corrections",
            "Qwen-only signature plus human construct library",
            "rubric freeze",
            "PC1 worked example and PC1-PC6 candidate application",
            "Qwen-derived hypothesis freeze",
            "future held-out validation plan",
        ],
        "firewall": {
            "aa7_used": False,
            "llama_used_for_selection": False,
            "gemma_used_for_selection": False,
            "human_respondent_projection": False,
            "model_performance_optimization": False,
            "new_inference": False,
            "activation_extraction": False,
            "external_model_api": False,
        },
    }
    (OUT / "source_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return manifest


def build_inventory() -> None:
    excluded = {"artifact_inventory.csv", "verification_report.json"}
    rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name not in excluded):
        rel = path.relative_to(REPO)
        suffix = path.suffix.lower()
        if suffix not in {".csv", ".json", ".md", ".py"}:
            continue
        rows.append({
            "path": str(rel),
            "status": "active",
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "branch_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/{rel}",
            "future_canonical_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{rel}",
        })
    with (OUT / "artifact_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify(manifest: dict[str, object]) -> dict[str, object]:
    checks: dict[str, object] = {}
    claude_path = OUT / "sapa_category3_blinded_review_judgments.csv"
    codex_path = REPO / "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_second_pass_review.csv"
    checks["external_review_preserved_exactly"] = sha256(claude_path) == CLAUDE_SHA
    checks["codex_frozen_review_unchanged"] = sha256(codex_path) == CODEX_REVIEW_SHA
    claude = pd.read_csv(claude_path)
    codex = pd.read_csv(codex_path)
    checks["external_review_exactly_78_unique_ids"] = len(claude) == claude.review_id.nunique() == 78
    joined = codex[["review_id", "trait", "decision"]].merge(
        claude[["review_id", "trait", "decision"]], on=["review_id", "trait"], suffixes=("_codex", "_claude"), validate="one_to_one"
    )
    summary = json.loads((OUT / "external_review_agreement_summary.json").read_text())
    checks["agreement_counts_reproduce"] = int((joined.decision_codex == joined.decision_claude).sum()) == summary["exact_five_category_agreement_n"] == 69
    checks["unweighted_kappa_reproduces"] = abs(kappa(joined.decision_codex.tolist(), joined.decision_claude.tolist()) - summary["cohens_kappa_unweighted_five_category"]) < 1e-12
    checks["all_disagreements_saved"] = len(pd.read_csv(OUT / "external_review_disagreements.csv")) == 9

    flagged = pd.read_csv(OUT / "sapa_flagged_item_quality_audit.csv")
    checks["all_eight_flagged_items_audited"] = set(flagged.item_id) == {"q_251", "q_1483", "q_1671", "q_1758", "q_566", "q_463", "q_1742", "q_1624"}
    checks["future_direction_corrections_explicit"] = all(token in ";".join(flagged.verified_direction.astype(str)) for token in ["naive:reverse", "adaptable:reverse", "independent:reverse", "reserved:reverse", "rebellious:reverse"])

    library = pd.read_csv(OUT / "human_construct_library.csv")
    checks["construct_library_126_unique"] = len(library) == library.construct_id.nunique() == 126
    checks["construct_definitions_and_sources_present"] = library.construct_definition.notna().all() and library.source_citation.notna().all()
    checks["all_construct_statistics_finite"] = pd.to_numeric(library.sapa_pairwise_standardized_alpha, errors="coerce").notna().all()

    signature = pd.read_csv(OUT / "qwen_pc1_pc6_model_side_signatures.csv")
    traits = signature[signature.evidence_class == "model_trait_association"]
    checks["six_by_240_trait_signature"] = len(traits) == 1440 and all(len(group) == group.subject.nunique() == 240 for _, group in traits.groupby("pc"))
    checks["signature_finite_trait_associations"] = pd.to_numeric(traits.pearson).map(math.isfinite).all() and pd.to_numeric(traits.spearman).map(math.isfinite).all()
    checks["signature_has_no_peer_model_values"] = not signature.astype(str).apply(lambda col: col.str.contains("llama|gemma", case=False, regex=True).any()).any()
    signature_manifest = json.loads((OUT / "qwen_pc1_pc6_signature_manifest.json").read_text())
    checks["canonical_qwen_pc1_pc3_reproduces"] = signature_manifest["canonical_pc1_pc3_max_abs_reproduction_error"] <= 1e-5
    checks["qwen_only_firewall_recorded"] = signature_manifest["firewall"]["aa7_paths_opened"] == [] and not signature_manifest["firewall"]["llama_or_gemma_values_retained"]

    candidates = pd.read_csv(OUT / "qwen_pc_human_construct_candidates.csv")
    frozen = pd.read_csv(OUT / "qwen_derived_human_construct_hypotheses_v1.csv")
    feasibility = pd.read_csv(OUT / "selected_construct_human_measurement_feasibility.csv")
    checks["all_pc_candidates_present"] = set(candidates.pc) == {f"PC{i}" for i in range(1, 7)}
    checks["frozen_hypothesis_status_exact"] = set(frozen.validation_status) == {"DISCOVERY_ONLY / NOT YET CROSS-MODEL VALIDATED"}
    checks["frozen_hypotheses_have_no_model_peer_dependency"] = not frozen.astype(str).apply(lambda col: col.str.contains("llama|gemma|aa-7|aa7", case=False, regex=True).any()).any()
    checks["feasibility_rows_match_frozen_rows"] = len(feasibility) == len(frozen) == 37
    checks["one_external_measure_required"] = int((~frozen.sapa_available.astype(bool)).sum()) == 1
    checks["no_respondent_id_output_column"] = not any(str(column).lower() in {"rid", "respondent_id", "person_id", "name", "email", "address"} for path in OUT.glob("*.csv") for column in pd.read_csv(path, nrows=0).columns)

    raw_tracked = git("ls-files", "data_external/human_validation/sapa")
    checks["raw_human_data_untracked"] = raw_tracked == ""
    tracked_out = git("ls-files", str(OUT.relative_to(REPO))).splitlines()
    checks["no_raw_respondent_artifact_committed"] = not any("sapaTempData" in path or "respondent" in Path(path).name.lower() for path in tracked_out)
    checks["aa7_absent_from_source_manifest"] = not any("aa7" in record["path"].lower() or "human_trait_convergence" in record["path"].lower() for record in manifest["sources"])

    # Every CSV/JSON in the output directory parses.
    parse_failures = []
    for path in sorted(OUT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            if path.suffix == ".csv":
                pd.read_csv(path)
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - explicit failure record
            parse_failures.append(f"{path.relative_to(REPO)}: {exc}")
    checks["all_csv_json_parse"] = not parse_failures

    inventory = pd.read_csv(OUT / "artifact_inventory.csv")
    inventory_failures = []
    for row in inventory.itertuples(index=False):
        path = REPO / row.path
        if not path.exists() or sha256(path) != row.sha256 or path.stat().st_size != int(row.bytes):
            inventory_failures.append(row.path)
    checks["artifact_inventory_hashes_match"] = not inventory_failures

    checks = {key: bool(value) for key, value in checks.items()}
    passed = all(checks.values())
    return {
        "generated_at_utc": GENERATED_AT,
        "analysis": "Qwen-first human-construct bridge verification",
        "passed": passed,
        "check_count": len(checks),
        "checks": checks,
        "parse_failures": parse_failures,
        "inventory_failures": inventory_failures,
        "privacy": "No respondent-level human data are tracked or emitted.",
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
    }


def main() -> None:
    manifest = build_source_manifest()
    build_inventory()
    report = verify(manifest)
    (OUT / "verification_report.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": report["check_count"]}, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
