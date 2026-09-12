#!/usr/bin/env python3
"""Independent verification suite for AA-8 outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


STRICT = "6497d28383aac33ea9f61b6ce2ac2ff195dccae4"
BROAD = "db782414c6708f6fd2c46f3e5b08d0e61668b14d"
FREEZE = "06b605d210b2a16d63682719af565781025dad31"
OUT_REL = Path("research/outputs/qwen_pc1_pc2_bipolar_human_mapping")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_csv(repo: Path, commit: str, path: str) -> list[dict]:
    text = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo, text=True)
    return list(csv.DictReader(io.StringIO(text)))


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def truth(v) -> bool:
    return v is True or str(v).lower() == "true"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    out = repo / OUT_REL
    checks = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    for commit, label in [(STRICT, "strict source commit"), (BROAD, "broader source commit"), (FREEZE, "rating freeze commit")]:
        ok = subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=repo).returncode == 0
        check(label, ok, commit)

    strict = git_csv(repo, STRICT, "research/outputs/qwen_trait_axis_specificity/qwen_axis_specific_marker_sets.csv")
    broad = git_csv(repo, BROAD, "research/outputs/qwen_pc_trait_specificity/qwen_trait_cross_pc_specificity_all.csv")
    check("strict 88-marker set", len(strict) == 88, f"n={len(strict)}")
    check("associated membership count", sum(truth(r["is_pc_associated"]) for r in broad) == 328, f"n={sum(truth(r['is_pc_associated']) for r in broad)}")
    check("target-dominant membership count", sum(truth(r["is_primary_pc_defining"]) for r in broad) == 202, f"n={sum(truth(r['is_primary_pc_defining']) for r in broad)}")
    check("highly concentrated membership count", sum(truth(r["is_highly_concentrated"]) for r in broad) == 70, f"n={sum(truth(r['is_highly_concentrated']) for r in broad)}")
    counts = Counter((r["pc"], r["pole"]) for r in strict)
    check("PC1 strict pole counts", counts[("PC1", "positive")] == 12 and counts[("PC1", "negative")] == 48, str(counts))
    check("PC2 strict pole counts", counts[("PC2", "positive")] == 3 and counts[("PC2", "negative")] == 10, str(counts))

    roles = read_csv(repo / "research/outputs/role_geometry_instruction_inventory/qwen_role_geometry_with_positive_instructions.csv")
    ratings = read_csv(out / "pc2_coordinate_blind_role_ratings.csv")
    check("275 canonical roles", len(roles) == 275 and len({r["role"] for r in roles}) == 275, f"n={len(roles)}")
    check("275 frozen role ratings", len(ratings) == 275 and {r["role"] for r in ratings} == {r["role"] for r in roles}, f"n={len(ratings)}")
    forbidden = ("pc", "rank", "percentile", "cluster", "correlation", "specificity", "purity")
    bad_fields = [field for field in ratings[0] if any(x in field.lower() for x in forbidden)]
    check("coordinate-blind rating fields", not bad_fields, f"forbidden_fields={bad_fields}")
    freeze_manifest = json.loads((out / "pc2_role_rating_freeze_manifest.json").read_text())
    check("rating hash matches freeze manifest", sha(out / "pc2_coordinate_blind_role_ratings.csv") == freeze_manifest["ratings_sha256"], freeze_manifest["ratings_sha256"])
    frozen_bytes = subprocess.check_output(["git", "show", f"{FREEZE}:{OUT_REL}/pc2_coordinate_blind_role_ratings.csv"], cwd=repo)
    check("ratings existed identically at freeze commit", hashlib.sha256(frozen_bytes).hexdigest() == freeze_manifest["ratings_sha256"], FREEZE)
    check("freeze predates current branch tip", subprocess.run(["git", "merge-base", "--is-ancestor", FREEZE, "HEAD"], cwd=repo).returncode == 0, "git ancestry")

    packet1, packet2 = read_csv(out / "pc1_bipolar_model_evidence_packet.csv"), read_csv(out / "pc2_bipolar_model_evidence_packet.csv")
    for axis, packet, trait_n in [("PC1", packet1, 170), ("PC2", packet2, 75)]:
        proles = [r for r in packet if r["evidence_kind"] == "ROLE_COORDINATE"]
        traits = [r for r in packet if r["evidence_kind"] == "TRAIT_MARKER"]
        check(f"{axis} packet role coverage", len(proles) == 275 and {r["role"] for r in proles} == {r["role"] for r in roles}, f"roles={len(proles)}")
        check(f"{axis} packet associated traits", len(traits) == trait_n, f"traits={len(traits)}")
        check(f"{axis} packet six correlations", all(all(r[f"r_PC{i}"] != "" for i in range(1, 7)) for r in traits), "all trait rows contain r_PC1..r_PC6")
        role_lookup = {r["role"]: r for r in roles}
        exact = all(all(abs(float(r[pc]) - float(role_lookup[r["role"]][pc])) < 1e-12 for pc in ["pc1", "pc2", "pc3"]) for r in proles)
        check(f"{axis} role coordinates reproduce", exact, "max tolerance 1e-12")

    pc1_re = read_csv(out / "pc1_sapa_construct_reconsideration.csv")
    pc2_re = read_csv(out / "pc2_sapa_construct_reconsideration.csv")
    check("PC1 full 126-construct universe", len(pc1_re) == 126 and len({r["construct_id"] for r in pc1_re}) == 126, f"n={len(pc1_re)}")
    check("PC2 full 126-construct universe", len(pc2_re) == 126 and len({r["construct_id"] for r in pc2_re}) == 126, f"n={len(pc2_re)}")
    items = read_csv(repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv")
    check("696-item dictionary", len(items) == 696 and len({r["item_id"] for r in items}) == 696, f"n={len(items)}")
    item_audits = read_csv(out / "pc1_rule_procedure_item_audit.csv") + read_csv(out / "pc2_physicality_activity_item_audit.csv")
    check("single-item epistemic labeling", all("item" in r.get("interpretive_note", "").lower() for r in item_audits), f"rows={len(item_audits)}")
    check("no direct physicality construct fabricated", not any(r.get("physicality_status") == "DIRECT_PHYSICALITY_CONSTRUCT" for r in item_audits), "semantic neighbors kept separate")

    expected_csv = [p for p in out.glob("*.csv")]
    expected_json = [p for p in out.glob("*.json") if p.name not in {"verification_report.json"}]
    parse_ok = True
    try:
        for path in expected_csv:
            read_csv(path)
        for path in expected_json:
            json.loads(path.read_text())
    except Exception:
        parse_ok = False
    check("all current CSV and JSON parse", parse_ok, f"csv={len(expected_csv)}, json={len(expected_json)}")

    inventory = read_csv(out / "artifact_inventory.csv")
    inventoried = {r["path"] for r in inventory}
    expected_inventory = {
        p.relative_to(repo).as_posix()
        for p in out.rglob("*")
        if p.is_file() and p.name != "artifact_inventory.csv"
    }
    inventory_hashes_ok = all(
        sha(repo / r["path"]) == r["sha256"]
        and (repo / r["path"]).stat().st_size == int(r["size_bytes"])
        and r["introducing_commit"] != "PENDING_FINAL_COMMIT"
        for r in inventory
    )
    check("artifact inventory coverage", inventoried == expected_inventory, f"rows={len(inventory)}, expected={len(expected_inventory)}")
    check("artifact inventory hashes and commits", inventory_hashes_ok, "all non-self artifacts hashed with introducing commits")

    source_manifest = json.loads((out / "source_manifest.json").read_text())
    check("source manifest commits exact", source_manifest["source_branches"]["strict_axis_specificity"]["commit"] == STRICT and source_manifest["source_branches"]["target_dominance_specificity"]["commit"] == BROAD, "exact SHAs")
    source_hash_ok = True
    for source in source_manifest["sources"]:
        if source["source_commit"] in {STRICT, BROAD}:
            data = subprocess.check_output(["git", "show", f"{source['source_commit']}:{source['path']}"], cwd=repo)
        elif source["source_commit"] in {"8f4e589df5d92217e56f76a978d51df07af5aa3a", "AA8_BRANCH"}:
            data = (repo / source["path"]).read_bytes()
        else:
            source_hash_ok = False
            break
        if hashlib.sha256(data).hexdigest() != source["sha256"] or len(data) != source["bytes"]:
            source_hash_ok = False
            break
    check("source hashes and byte counts", source_hash_ok, f"sources={len(source_manifest['sources'])}")
    firewall = source_manifest["firewall"]
    check("specificity not rerun or retuned", firewall["specificity_rerun_or_retuned"] is False, "saved artifacts only")
    check("no human respondent rows or projection", firewall["human_respondent_rows_loaded_or_scored"] is False and firewall["human_projection_performed"] is False, "metadata and item dictionary only")
    check("no Llama/Gemma or AA-7 selection", firewall["llama_or_gemma_scientific_data_used"] is False and firewall["AA7_result_used_to_choose_interpretation"] is False, "Qwen-only interpretive sources")
    check("no NLSY outcomes", firewall["NLSY_outcomes_used"] is False, "not loaded")
    check("no next experiment selected", firewall["next_experiment_selected"] is False, "stopping point preserved")
    check("PC3 remains reference only", source_manifest["pc3_reference_only"]["selection_or_mapping_reopened"] is False, "no PC3 output modified")

    tracked_diff = subprocess.check_output(["git", "diff", "--name-only", "8f4e589df5d92217e56f76a978d51df07af5aa3a..HEAD"], cwd=repo, text=True).splitlines()
    check("no respondent microdata committed", not any("response" in p.lower() and "qwen_pc1_pc2" not in p for p in tracked_diff), f"changed_paths={len(tracked_diff)}")
    maintenance_paths = {
        "research/REPO_NAVIGATION.md",
        "research/REPO_FILE_INDEX.csv",
        "research/RAW_URL_INDEX.md",
        "research/RESEARCH_INDEX.md",
        "research/PROVENANCE_REGISTRY.md",
        "research/FINDINGS_LEDGER.md",
        "research/RESEARCH_STATE.md",
        "research/THREAD_START.md",
        "research/paper15_content_ledger.md",
        "research/paper15_content_ledger_artifact_inventory.csv",
        "research/runtime/CURRENT_RESULTS.md",
        "research/runtime/PENDING_TASK.md",
        "research/STARTUP_MANIFEST.md",
    }
    unexpected = [p for p in tracked_diff if not p.startswith(str(OUT_REL)) and p not in maintenance_paths]
    check("AA-8 outputs and maintenance isolated", not unexpected, f"unexpected={unexpected}")

    with tempfile.TemporaryDirectory(prefix="aa8_verify_") as td:
        tmp = Path(td)
        subprocess.run([
            "python3", str(out / "scripts/build_pc2_coordinate_blind_role_ratings.py"),
            "--input", str(repo / "research/outputs/role_geometry_instruction_inventory/qwen_role_geometry_with_positive_instructions.csv"),
            "--output", str(tmp / "ratings.csv"), "--manifest", str(tmp / "rating_manifest.json"),
            "--rubric", str(out / "pc2_coordinate_blind_role_rating_rubric.md"), "--freeze-commit", FREEZE,
        ], cwd=repo, check=True)
        check("deterministic role ratings", sha(tmp / "ratings.csv") == sha(out / "pc2_coordinate_blind_role_ratings.csv"), sha(tmp / "ratings.csv"))
        model_tmp = tmp / "model"
        subprocess.run([
            "python3", str(out / "scripts/build_model_evidence_and_role_diagnostics.py"), "--repo", str(repo),
            "--output-dir", str(model_tmp), "--roles", str(repo / "research/outputs/role_geometry_instruction_inventory/qwen_role_geometry_with_positive_instructions.csv"),
            "--ratings", str(out / "pc2_coordinate_blind_role_ratings.csv"), "--rating-freeze-manifest", str(out / "pc2_role_rating_freeze_manifest.json"),
        ], cwd=repo, check=True)
        model_files = ["pc1_bipolar_model_evidence_packet.csv", "pc2_bipolar_model_evidence_packet.csv", "pc2_role_dimension_pc_associations.csv", "pc2_role_dimension_diagnostic_report.md"]
        check("deterministic model packets and diagnostics", all(sha(model_tmp / f) == sha(out / f) for f in model_files), ";".join(model_files))
        human_tmp = tmp / "human"
        human_tmp.mkdir()
        subprocess.run([
            "python3", str(out / "scripts/build_human_reconsideration.py"), "--repo", str(repo),
            "--item-dictionary", str(repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"), "--output-dir", str(human_tmp),
        ], cwd=repo, check=True)
        human_files = ["pc1_sapa_construct_reconsideration.csv", "pc1_rule_procedure_item_audit.csv", "pc1_bipolar_human_mapping.csv", "pc2_sapa_construct_reconsideration.csv", "pc2_physicality_activity_item_audit.csv", "pc2_bipolar_human_mapping.csv"]
        check("deterministic human inventories", all(sha(human_tmp / f) == sha(out / f) for f in human_files), ";".join(human_files))

    passed = sum(c["status"] == "PASS" for c in checks)
    report = {
        "analysis": "AA-8 verification",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']} {passed}/{len(checks)}")
    if report["status"] != "PASS":
        for row in checks:
            if row["status"] == "FAIL":
                print("FAIL", row["name"], row["detail"])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
