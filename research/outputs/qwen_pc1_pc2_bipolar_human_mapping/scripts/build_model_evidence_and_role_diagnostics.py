#!/usr/bin/env python3
"""Join frozen AA-8 evidence after coordinate-blind ratings have been committed."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats


STRICT_COMMIT = "6497d28383aac33ea9f61b6ce2ac2ff195dccae4"
BROAD_COMMIT = "db782414c6708f6fd2c46f3e5b08d0e61668b14d"
STRICT_PATH = "research/outputs/qwen_trait_axis_specificity/qwen_axis_specific_marker_sets.csv"
BROAD_PATH = "research/outputs/qwen_pc_trait_specificity/qwen_trait_cross_pc_specificity_all.csv"
RATINGS_DIMS = [
    "embodied_physical_engagement",
    "practical_concrete_engagement",
    "social_outward_engagement",
    "abstract_conceptual_engagement",
    "ritual_formal_mediation",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def git_csv(repo: Path, commit: str, path: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(git_bytes(repo, commit, path).decode("utf-8"))))


def f(value: str | float | int | None) -> float:
    if value in (None, ""):
        return math.nan
    return float(value)


def truth(value: str | bool) -> bool:
    return value is True or str(value).lower() == "true"


def correlation(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    pr = stats.pearsonr(x, y)
    sr = stats.spearmanr(x, y)
    return float(pr.statistic), float(pr.pvalue), float(sr.statistic), float(sr.pvalue)


def residualize(y: np.ndarray, controls: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(y)), controls])
    return y - x @ np.linalg.lstsq(x, y, rcond=None)[0]


def ols(y: np.ndarray, x: np.ndarray) -> dict[str, object]:
    design = np.column_stack([np.ones(len(y)), x])
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    pred = design @ beta
    resid = y - pred
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - sse / sst
    df = len(y) - design.shape[1]
    mse = sse / df
    cov = mse * np.linalg.pinv(design.T @ design)
    se = np.sqrt(np.diag(cov))
    tvals = beta / se
    pvals = 2 * stats.t.sf(np.abs(tvals), df)
    return {"beta": beta, "se": se, "p": pvals, "r2": r2, "df": df}


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        seen = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    fieldnames.append(key)
                    seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def display_path(path: Path, repo: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def trait_rows(repo: Path, axis: str, strict_rows: list[dict], broad_rows: list[dict]) -> list[dict]:
    strict_lookup = {(r["pc"], r["pole"], r["trait"]): r for r in strict_rows}
    out = []
    for row in broad_rows:
        if row["pc"] != axis or not truth(row["is_pc_associated"]):
            continue
        key = (row["pc"], row["pole"], row["trait"])
        strict = strict_lookup.get(key)
        tier = "PC_ASSOCIATED_CONTEXT"
        if truth(row["is_primary_pc_defining"]):
            tier = "PC_DEFINING_TARGET_DOMINANT"
        if strict:
            tier = "STRICT_AXIS_SPECIFIC"
        if truth(row["is_highly_concentrated"]):
            tier = "HIGHLY_CONCENTRATED_AND_STRICT" if strict else "HIGHLY_CONCENTRATED"
        out.append({
            "evidence_kind": "TRAIT_MARKER",
            "axis": axis,
            "pole": row["pole"],
            "evidence_tier": tier,
            "trait": row["trait"],
            "definition_or_summary": row["canonical_definition"],
            "target_r": row["target_pearson_r"],
            "r_PC1": row.get("r_PC1", ""),
            "r_PC2": row.get("r_PC2", ""),
            "r_PC3": row.get("r_PC3", ""),
            "r_PC4": row.get("r_PC4", ""),
            "r_PC5": row.get("r_PC5", ""),
            "r_PC6": row.get("r_PC6", ""),
            "largest_offtarget_pc": row["largest_offtarget_pc"],
            "largest_offtarget_r": row["largest_offtarget_signed_r"],
            "specificity_margin": row["specificity_margin"],
            "concentration_fraction": row["pc1_6_concentration_fraction"],
            "target_is_largest_probability": row["target_is_largest_probability"],
            "axis_purity": strict["axis_purity"] if strict else row["pc1_6_concentration_fraction"],
            "is_pc_associated": True,
            "is_target_dominant": truth(row["is_primary_pc_defining"]),
            "is_strict_axis_specific": bool(strict),
            "is_highly_concentrated": truth(row["is_highly_concentrated"]),
            "source_path": BROAD_PATH if not strict else f"{BROAD_PATH};{STRICT_PATH}",
            "epistemic_status": "OBSERVED",
        })
    return out


def role_rows(axis: str, roles: list[dict]) -> list[dict]:
    coord = axis.lower()
    asc = sorted(roles, key=lambda r: f(r[coord]))
    bottom = {r["role"]: i + 1 for i, r in enumerate(asc[:15])}
    top = {r["role"]: i + 1 for i, r in enumerate(reversed(asc[-15:]))}
    out = []
    for row in roles:
        label = "INTERIOR"
        rank = ""
        if row["role"] in top:
            label, rank = "TOP_15_POSITIVE", top[row["role"]]
        elif row["role"] in bottom:
            label, rank = "TOP_15_NEGATIVE", bottom[row["role"]]
        out.append({
            "evidence_kind": "ROLE_COORDINATE",
            "axis": axis,
            "pole": "positive" if f(row[coord]) >= 0 else "negative",
            "evidence_tier": label,
            "role": row["role"],
            "cluster": row["cluster"],
            "pc1": row["pc1"],
            "pc2": row["pc2"],
            "pc3": row["pc3"],
            "axis_rank_ascending": row[f"{coord}_rank_ascending"],
            "axis_rank_descending": row[f"{coord}_rank_descending"],
            "axis_percentile": row[f"{coord}_percentile"],
            "axis_extreme_rank": rank,
            "positive_instruction_1": row["positive_instruction_1"],
            "positive_instruction_2": row["positive_instruction_2"],
            "positive_instruction_3": row["positive_instruction_3"],
            "positive_instruction_4": row["positive_instruction_4"],
            "positive_instruction_5": row["positive_instruction_5"],
            "source_path": "research/outputs/role_geometry_instruction_inventory/qwen_role_geometry_with_positive_instructions.csv",
            "epistemic_status": "OBSERVED",
        })
    return out


def cluster_rows(axis: str, roles: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in roles:
        grouped[row["cluster"]].append(row)
    out = []
    for cluster, members in sorted(grouped.items()):
        vals = np.array([f(r[axis.lower()]) for r in members])
        out.append({
            "evidence_kind": "CLUSTER_DISTRIBUTION",
            "axis": axis,
            "evidence_tier": "CONTEXT",
            "cluster": cluster,
            "definition_or_summary": f"n={len(members)}; mean={np.mean(vals):.6f}; sd={np.std(vals, ddof=1):.6f}; min={np.min(vals):.6f}; max={np.max(vals):.6f}",
            "n": len(members),
            "axis_mean": f"{np.mean(vals):.12g}",
            "axis_sd": f"{np.std(vals, ddof=1):.12g}",
            "axis_min": f"{np.min(vals):.12g}",
            "axis_max": f"{np.max(vals):.12g}",
            "source_path": "research/outputs/role_geometry_instruction_inventory/qwen_role_geometry_with_positive_instructions.csv",
            "epistemic_status": "OBSERVED",
        })
    return out


PRIOR_EVIDENCE = {
    "PC1": [
        ("assistant_axis_alignment", "PC1 explains 31.5954% of saved-role variance and aligns 0.802310 with the historical assistant axis.", "research/FINDINGS_LEDGER.md", "OBSERVED"),
        ("blind_external_standard_accountability", "Coordinate-blind instruction ratings predict PC1 at R2=0.704; higher external-standard accountability maps to higher PC1.", "research/outputs/blind_pc_interpretation_rating_benchmark/blind_pc_interpretation_rating_report.md", "OBSERVED"),
        ("professional_objective_certainty", "Within 102 professional roles, objective-certainty ratings correlate r=0.394 with PC1.", "research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md", "OBSERVED"),
        ("competing_theories", "External-standard/accountability vocabulary has cluster-and-length-controlled r=0.192 and adds R2=.0071 beyond controls, exceeding orderliness and determination vocabularies but remaining weak lexical evidence.", "research/outputs/pc1_competing_theories_test/pc1_competing_theories_report.md", "OBSERVED"),
        ("focused_accountability_activation", "Across matched prompts, accountability/scrutiny exceeds determination by mean PC1 +3.297 and arithmetic/checking by +9.551; all 10 pair contrasts are positive.", "research/outputs/pc1_accountability_validation/accountability_validation_report.md", "OBSERVED"),
        ("weakened_single_construct_reading", "Objective certainty alone is incomplete because blind intelligence/expertise ratings correlate more strongly with PC1 (r=.663) than objective-certainty ratings (r=.558).", "research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md", "INTERPRETATION"),
        ("residual", "Positive PC1 combines factual transparency, analysis, procedure, and institutional legibility; negative PC1 combines symbolic imagination, expressiveness, ambiguity, and improvisation. No conventional human trait is assumed to cover all of this.", "AA-8 synthesis", "INTERPRETATION"),
    ],
    "PC2": [
        ("blind_integration_coherence", "Coordinate-blind integration/coherence ratings predict PC2 at R2=0.423 with higher integration mapping to lower PC2.", "research/outputs/blind_pc_interpretation_rating_benchmark/blind_pc_interpretation_rating_report.md", "OBSERVED"),
        ("blind_abstraction", "Reading-based abstraction ratings correlate r=-0.655 and rho=-0.658 with PC2, stronger than coherent-action-under-uncertainty at r=0.373.", "research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md", "OBSERVED"),
        ("pc1_conditioned_abstraction", "After PC1-band demeaning, abstraction remains the strongest tested PC2 predictor at r=-0.618 and R2=.382; uncertainty exposure is near zero.", "research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md", "OBSERVED"),
        ("muted_pc1_roles", "Within the central 10% PC1 band, high PC2 roles are socially situated and immediate while low PC2 roles are abstracting, integrative, systemic, standards-bearing, or craft/procedural.", "research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md", "OBSERVED"),
        ("cluster_conditioning", "Situated developmental immediacy versus abstraction correlates r=.655 globally and r=.486 after cluster control; the mapping is region-dependent.", "research/outputs/cluster_conditioned_axis_tests/cluster_conditioned_axis_report.md", "OBSERVED"),
        ("weakened_uncertainty_reading", "Coherent action under unresolved uncertainty remains a secondary behavioral expression, not the best single axis label; professional-role correlation was r=-.007.", "research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md", "INTERPRETATION"),
        ("residual", "Positive PC2 may combine experiential practicality, social accessibility, and developmental immediacy; negative PC2 combines inwardness, abstraction, theory, ritual/formality, and integrated world-modeling. Physicality is tested separately rather than assumed.", "AA-8 synthesis", "HYPOTHESIS"),
    ],
}


def prior_rows(axis: str) -> list[dict]:
    return [{
        "evidence_kind": "PRIOR_MODEL_RESULT",
        "axis": axis,
        "evidence_tier": "PRIOR_VALIDATED_OR_BOUNDED",
        "evidence_id": evidence_id,
        "definition_or_summary": summary,
        "source_path": source,
        "epistemic_status": status,
    } for evidence_id, summary, source, status in PRIOR_EVIDENCE[axis]]


def role_associations(ratings: list[dict], roles: list[dict]) -> tuple[list[dict], dict]:
    role_lookup = {r["role"]: r for r in roles}
    joined = [(r, role_lookup[r["role"]]) for r in ratings]
    if len(joined) != 275 or len({r[0]["role"] for r in joined}) != 275:
        raise ValueError("Role-rating join must contain exactly 275 unique roles")

    rows = []
    arrays = {d: np.array([f(r[d]) for r, _ in joined]) for d in RATINGS_DIMS}
    pcs = {pc: np.array([f(g[pc]) for _, g in joined]) for pc in ["pc1", "pc2", "pc3"]}
    for dim in RATINGS_DIMS:
        for pc in ["pc1", "pc2", "pc3"]:
            pearson, pearson_p, spearman, spearman_p = correlation(arrays[dim], pcs[pc])
            partial = partial_p = ""
            if pc == "pc2":
                dr = residualize(arrays[dim], pcs["pc1"])
                pr = residualize(pcs["pc2"], pcs["pc1"])
                partial, partial_p, _, _ = correlation(dr, pr)
            rows.append({
                "analysis_type": "DIMENSION_PC_ASSOCIATION",
                "dimension_or_model": dim,
                "target": pc.upper(),
                "n": len(joined),
                "pearson_r": pearson,
                "pearson_p": pearson_p,
                "spearman_rho": spearman,
                "spearman_p": spearman_p,
                "partial_pearson_r_controlling_PC1": partial,
                "partial_pearson_p_controlling_PC1": partial_p,
                "interpretive_status": "COORDINATE_BLIND_DIAGNOSTIC",
            })

    order = np.argsort(pcs["pc2"])
    k = max(1, int(round(len(joined) * 0.10)))
    low, high = order[:k], order[-k:]
    for dim in RATINGS_DIMS:
        for label, idx in [("PC2_BOTTOM_10_PERCENT", low), ("PC2_TOP_10_PERCENT", high)]:
            vals = arrays[dim][idx]
            rows.append({
                "analysis_type": "PC2_EXTREME_ENRICHMENT",
                "dimension_or_model": dim,
                "target": label,
                "n": len(idx),
                "mean_rating": float(np.mean(vals)),
                "high_rating_fraction_ge_4": float(np.mean(vals >= 4)),
                "interpretive_status": "DESCRIPTIVE",
            })

    z = lambda a: (a - np.mean(a)) / np.std(a, ddof=1)
    y = z(pcs["pc2"])
    base_names = ["PC1", "practical_concrete_engagement", "social_outward_engagement"]
    base_x = np.column_stack([z(pcs["pc1"]), z(arrays["practical_concrete_engagement"]), z(arrays["social_outward_engagement"])])
    full_names = base_names + ["embodied_physical_engagement"]
    full_x = np.column_stack([base_x, z(arrays["embodied_physical_engagement"])])
    base = ols(y, base_x)
    full = ols(y, full_x)
    rows.append({
        "analysis_type": "NESTED_OLS",
        "dimension_or_model": "PC2 ~ PC1 + practical + social",
        "target": "PC2",
        "n": len(y),
        "predictors": ";".join(base_names),
        "model_r_squared": base["r2"],
        "interpretive_status": "DESCRIPTIVE_CONTROL_MODEL",
    })
    rows.append({
        "analysis_type": "NESTED_OLS",
        "dimension_or_model": "add embodied physical engagement",
        "target": "PC2",
        "n": len(y),
        "predictors": ";".join(full_names),
        "model_r_squared": full["r2"],
        "delta_r_squared": full["r2"] - base["r2"],
        "standardized_beta": full["beta"][-1],
        "beta_p": full["p"][-1],
        "interpretive_status": "PHYSICALITY_BEYOND_PRACTICAL_SOCIAL_WITH_PC1_CONTROL",
    })
    summary = {
        "joined": joined,
        "arrays": arrays,
        "pcs": pcs,
        "base_r2": base["r2"],
        "full_r2": full["r2"],
        "physical_beta": float(full["beta"][-1]),
        "physical_p": float(full["p"][-1]),
    }
    return rows, summary


def diagnostic_report(path: Path, summary: dict, assoc_rows: list[dict]) -> None:
    joined = summary["joined"]
    required = ["surfer", "coach", "competitor", "soldier", "warrior"]
    role_map = {r["role"]: (r, g) for r, g in joined}
    pc2_assoc = {r["dimension_or_model"]: r for r in assoc_rows if r["analysis_type"] == "DIMENSION_PC_ASSOCIATION" and r["target"] == "PC2"}
    physical = sorted(joined, key=lambda x: (f(x[0]["embodied_physical_engagement"]), f(x[1]["pc2"])), reverse=True)
    high_pc2_low_phys = sorted([x for x in joined if f(x[0]["embodied_physical_engagement"]) <= 2], key=lambda x: f(x[1]["pc2"]), reverse=True)[:10]
    low_pc2_high_phys = sorted([x for x in joined if f(x[0]["embodied_physical_engagement"]) >= 3], key=lambda x: f(x[1]["pc2"]))[:10]
    lines = [
        "# PC2 Coordinate-Blind Role-Dimension Diagnostic",
        "",
        "## Method boundary",
        "",
        "The five ordinal ratings were frozen at commit `06b605d210b2a16d63682719af565781025dad31` before geometry was joined. The rating file contains role names and instructions but no coordinates, ranks, clusters, trait correlations, or specificity outcomes. Scores are deterministic rubric-coded instruction content, not human ratings or independent validation.",
        "",
        "## Dimension associations",
        "",
        "| Dimension | Pearson r with PC2 | Spearman rho | Partial r controlling PC1 | Pearson r with PC1 | Pearson r with PC3 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for dim in RATINGS_DIMS:
        p2 = pc2_assoc[dim]
        p1 = next(r for r in assoc_rows if r["analysis_type"] == "DIMENSION_PC_ASSOCIATION" and r["dimension_or_model"] == dim and r["target"] == "PC1")
        p3 = next(r for r in assoc_rows if r["analysis_type"] == "DIMENSION_PC_ASSOCIATION" and r["dimension_or_model"] == dim and r["target"] == "PC3")
        lines.append(f"| {dim} | {f(p2['pearson_r']):+.3f} | {f(p2['spearman_rho']):+.3f} | {f(p2['partial_pearson_r_controlling_PC1']):+.3f} | {f(p1['pearson_r']):+.3f} | {f(p3['pearson_r']):+.3f} |")
    delta = summary["full_r2"] - summary["base_r2"]
    lines += [
        "",
        "## Physicality beyond practical and social engagement",
        "",
        f"A standardized model with PC1, practical/concrete engagement, and social/outward engagement explains R2={summary['base_r2']:.3f} of PC2. Adding embodied/physical engagement changes R2 by {delta:+.3f}; its standardized beta is {summary['physical_beta']:+.3f} (p={summary['physical_p']:.4g}). This is a descriptive nested-model diagnostic, not a causal or construct-validity test.",
        "",
        "## User-named roles",
        "",
        "| Role | PC1 | PC2 | PC3 | Physical | Practical | Social | Abstract | Ritual/formal |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for role in required:
        r, g = role_map[role]
        lines.append(f"| {role} | {f(g['pc1']):+.3f} | {f(g['pc2']):+.3f} | {f(g['pc3']):+.3f} | {r['embodied_physical_engagement']} | {r['practical_concrete_engagement']} | {r['social_outward_engagement']} | {r['abstract_conceptual_engagement']} | {r['ritual_formal_mediation']} |")
    lines += ["", "## Counterexamples", "", "High-PC2 roles with physical score <=2:", ""]
    lines.append(", ".join(f"{g['role']} (PC2 {f(g['pc2']):+.2f})" for _, g in high_pc2_low_phys))
    lines += ["", "Low-PC2 roles with physical score >=3:", ""]
    lines.append(", ".join(f"{g['role']} (PC2 {f(g['pc2']):+.2f})" for _, g in low_pc2_high_phys) or "None")
    lines += [
        "",
        "## Interpretation",
        "",
        "Physicality is supported only if its direct, partial, extreme-enrichment, and incremental-model results converge. Practicality and social outwardness are evaluated separately so that an occupationally active or interpersonal role is not silently relabeled as embodied. The role examples and counterexamples remain necessary because the five dimensions are sparse ordinal content codes.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--roles", type=Path, required=True)
    parser.add_argument("--ratings", type=Path, required=True)
    parser.add_argument("--rating-freeze-manifest", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    outdir = args.output_dir.resolve()
    args.roles = args.roles.resolve()
    args.ratings = args.ratings.resolve()
    args.rating_freeze_manifest = args.rating_freeze_manifest.resolve()
    strict_rows = git_csv(repo, STRICT_COMMIT, STRICT_PATH)
    broad_rows = git_csv(repo, BROAD_COMMIT, BROAD_PATH)

    if len(strict_rows) != 88:
        raise ValueError(f"Strict marker count mismatch: {len(strict_rows)}")
    if sum(truth(r["is_primary_pc_defining"]) for r in broad_rows) != 202:
        raise ValueError("Target-dominant count mismatch")
    if sum(truth(r["is_highly_concentrated"]) for r in broad_rows) != 70:
        raise ValueError("Highly concentrated count mismatch")

    with args.roles.open(newline="", encoding="utf-8") as fh:
        roles = list(csv.DictReader(fh))
    with args.ratings.open(newline="", encoding="utf-8") as fh:
        ratings = list(csv.DictReader(fh))
    freeze = json.loads(args.rating_freeze_manifest.read_text(encoding="utf-8"))
    if freeze.get("geometry_join_performed") is not False or freeze.get("role_count") != 275:
        raise ValueError("Invalid coordinate-blind rating freeze manifest")
    if sha256(args.ratings) != freeze["ratings_sha256"]:
        raise ValueError("Frozen ratings hash mismatch")

    packets = {}
    for axis in ["PC1", "PC2"]:
        rows = trait_rows(repo, axis, strict_rows, broad_rows) + role_rows(axis, roles) + cluster_rows(axis, roles) + prior_rows(axis)
        path = outdir / f"{axis.lower()}_bipolar_model_evidence_packet.csv"
        write_csv(path, rows)
        packets[axis] = {"path": display_path(path, repo), "row_count": len(rows), "sha256": sha256(path), "kind_counts": dict(Counter(r["evidence_kind"] for r in rows))}

    assoc_rows, summary = role_associations(ratings, roles)
    assoc_path = outdir / "pc2_role_dimension_pc_associations.csv"
    write_csv(assoc_path, assoc_rows)
    report_path = outdir / "pc2_role_dimension_diagnostic_report.md"
    diagnostic_report(report_path, summary, assoc_rows)

    source_hashes = {
        f"{STRICT_COMMIT}:{STRICT_PATH}": hashlib.sha256(git_bytes(repo, STRICT_COMMIT, STRICT_PATH)).hexdigest(),
        f"{BROAD_COMMIT}:{BROAD_PATH}": hashlib.sha256(git_bytes(repo, BROAD_COMMIT, BROAD_PATH)).hexdigest(),
        str(args.roles.relative_to(repo)): sha256(args.roles),
        str(args.ratings.relative_to(repo)): sha256(args.ratings),
        str(args.rating_freeze_manifest.relative_to(repo)): sha256(args.rating_freeze_manifest),
    }
    manifest = {
        "analysis": "AA-8 frozen PC1 and PC2 bipolar model evidence packets",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "canonical_starting_sha": "8f4e589df5d92217e56f76a978d51df07af5aa3a",
        "strict_specificity_commit": STRICT_COMMIT,
        "broader_specificity_commit": BROAD_COMMIT,
        "coordinate_blind_rating_freeze_commit": freeze["freeze_commit"],
        "specificity_rerun": False,
        "marker_counts": {
            "pc_associated": sum(truth(r["is_pc_associated"]) for r in broad_rows),
            "pc_defining_target_dominant": sum(truth(r["is_primary_pc_defining"]) for r in broad_rows),
            "strict_axis_specific": len(strict_rows),
            "highly_concentrated": sum(truth(r["is_highly_concentrated"]) for r in broad_rows),
        },
        "role_count": len(roles),
        "packets": packets,
        "role_association_path": display_path(assoc_path, repo),
        "role_association_sha256": sha256(assoc_path),
        "role_diagnostic_report_path": display_path(report_path, repo),
        "role_diagnostic_report_sha256": sha256(report_path),
        "source_hashes": source_hashes,
        "firewall": {
            "ratings_frozen_before_geometry_join": True,
            "rating_packet_contains_geometry": False,
            "human_respondent_rows_loaded": False,
            "llama_or_gemma_scientific_data_loaded": False,
            "AA7_results_used": False,
        },
    }
    (outdir / "model_evidence_packet_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
