#!/usr/bin/env python3
"""Compute Qwen PC1-PC6 trait specificity and refine the frozen SAPA inventory.

This is a CPU-only analysis of saved Qwen role/trait and PCA artifacts. It does
not load human respondent records, other model values, or AA-7 results.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


QWEN_MODEL = "Qwen/Qwen3-32B"
AA1_COMMIT = "667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb"
STARTING_SHA = AA1_COMMIT
SPEC_FREEZE_COMMIT = "595c1e22cc5e7cd7b7e9a6a90046e18b9b103d68"
BRANCH = "codex/aa1-qwen-pc-trait-specificity"
REPO_SLUG = "J-Chamberlain/assistant-axis"
BOOTSTRAP_SEED = 20260912
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_BATCH_SIZE = 25
EPSILON = 1e-12
PRIMARY_ABS_R = 0.50
FDR_THRESHOLD = 0.01
SIGN_STABILITY_THRESHOLD = 0.95
PRIMARY_TARGET_LARGEST = 0.95
EFFECT_SENSITIVITY = (0.40, 0.50, 0.60)
DOMINANCE_SENSITIVITY = (0.90, 0.95, 0.99)
CONCENTRATION_SENSITIVITY = (0.60, 0.70, 0.80)
PC_ORDER = [f"PC{i}" for i in range(1, 7)]
POLE_ORDER = ["positive", "negative"]
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


def qwen_object_from_multimodel_json(path: Path) -> dict[str, object]:
    """Parse only the exact top-level Qwen object from the shared viewer file."""
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
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
            if depth == 0:
                break
            lines.append(line)
    if not collecting or depth != 0:
        raise ValueError(f"Could not isolate Qwen object from {path}")
    lines.append("}")
    return json.loads("".join(lines))


def split_semicolon(value: object) -> list[str]:
    if value is None or pd.isna(value):
        return []
    return [part for part in str(value).split(";") if part]


def joined(values: list[str] | set[str]) -> str:
    return ";".join(sorted(set(values)))


def ordered_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["_pc_order"] = result["pc"].map({pc: i for i, pc in enumerate(PC_ORDER)})
    result["_pole_order"] = result["pole"].map({pole: i for i, pole in enumerate(POLE_ORDER)})
    return result.sort_values(["_pc_order", "_pole_order", "trait"], kind="mergesort").drop(
        columns=["_pc_order", "_pole_order"]
    )


def load_inputs(repo: Path) -> tuple[pd.DataFrame, list[str], pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    paths = {
        "trait_matrix": repo / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
        "qwen_pc_coordinates": repo / "research/outputs/extended_persona_pca/viewer_data.json",
        "aa1_correlations": repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_pc_correlations_all.csv",
        "aa1_membership": repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_family_membership_primary.csv",
        "aa1_human_judgments": repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_family_human_mapping_judgments.csv",
        "aa1_human_inventory": repo / "research/outputs/qwen_trait_family_human_inventory/qwen_pc_trait_family_human_inventory.csv",
        "aa1_selection_spec": repo / "research/outputs/qwen_trait_family_human_inventory/qwen_trait_family_selection_spec.md",
        "aa1_verification": repo / "research/outputs/qwen_trait_family_human_inventory/verification_report.json",
        "trait_definitions": repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_model_trait_candidate_crosswalk.csv",
        "pc3_group_scores": repo / "research/outputs/persona_trait_surface_viewer/persona_trait_group_scores.csv",
        "pc3_methodology": repo / "research/outputs/persona_trait_surface_viewer/trait_surface_methodology.md",
        "pc3_generator": repo / "research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py",
        "pc3_ridge_data": repo / "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json",
    }
    navigation_paths = [
        repo / "research/REPO_NAVIGATION.md",
        repo / "research/REPO_FILE_INDEX.csv",
        repo / "research/RAW_URL_INDEX.md",
    ]
    if any(not path.exists() for path in navigation_paths):
        raise FileNotFoundError("Canonical navigation system is incomplete")
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required sources: {missing}")

    traits_frame = pd.read_csv(paths["trait_matrix"])
    if traits_frame.shape != (275, 241) or traits_frame["persona"].duplicated().any():
        raise ValueError("Expected 275 unique roles and 240 trait columns")
    traits = [column for column in traits_frame.columns if column != "persona"]
    if len(traits) != 240 or len(set(traits)) != 240:
        raise ValueError("Expected 240 unique Qwen trait names")

    qwen = qwen_object_from_multimodel_json(paths["qwen_pc_coordinates"])
    if qwen.get("label") != QWEN_MODEL or int(qwen.get("role_count", -1)) != 275:
        raise ValueError("Unexpected Qwen coordinate metadata")
    point_rows = []
    for point in qwen["points"]:
        coordinates = point["coordinates"]
        if len(coordinates) < 6:
            raise ValueError("Qwen role is missing PC1-PC6 coordinates")
        point_rows.append(
            {"persona": point["persona"], **{f"PC{i}": coordinates[i - 1] for i in range(1, 7)}}
        )
    points = pd.DataFrame(point_rows)
    merged = traits_frame.merge(points, on="persona", how="inner", validate="one_to_one")
    merged = merged.sort_values("persona", kind="mergesort").reset_index(drop=True)
    if len(merged) != 275 or not np.isfinite(merged[traits + PC_ORDER].to_numpy(float)).all():
        raise ValueError("Qwen trait/coordinate join is incomplete or nonfinite")

    definitions_frame = pd.read_csv(paths["trait_definitions"])
    definitions = dict(
        zip(definitions_frame["model_trait"], definitions_frame["canonical_definition"], strict=True)
    )
    if set(definitions) != set(traits):
        raise ValueError("Trait definition names do not match the 240 trait columns")

    aa1_all = pd.read_csv(paths["aa1_correlations"])
    aa1_members = pd.read_csv(paths["aa1_membership"])
    judgments = pd.read_csv(paths["aa1_human_judgments"]).fillna("")
    inventory = pd.read_csv(paths["aa1_human_inventory"]).fillna("")
    if len(aa1_all) != 1440 or len(aa1_members) != 328 or len(judgments) != 48:
        raise ValueError("Validated AA-1 source counts differ from 1,440 / 328 / 48")
    verification = json.loads(paths["aa1_verification"].read_text(encoding="utf-8"))
    if not verification.get("passed") or verification.get("check_count") != 34:
        raise ValueError("AA-1 source does not carry the required 34/34 verification")
    return merged, traits, aa1_all, aa1_members, judgments, inventory, definitions, paths


def correlation_matrix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    xc = x - x.mean(axis=0, keepdims=True)
    yc = y - y.mean(axis=0, keepdims=True)
    # Explicit contraction avoids platform-BLAS warning noise observed for this
    # small, well-bounded matrix while preserving float64 arithmetic.
    numerator = np.einsum("nt,np->tp", xc, yc, optimize=True)
    denominator = np.sqrt(np.sum(xc * xc, axis=0)[:, None] * np.sum(yc * yc, axis=0)[None, :])
    with np.errstate(divide="ignore", invalid="ignore"):
        result = numerator / denominator
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite observed correlation")
    return result


def joint_bootstrap(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    output = np.empty((BOOTSTRAP_RESAMPLES, x.shape[1], y.shape[1]), dtype=np.float64)
    offset = 0
    while offset < BOOTSTRAP_RESAMPLES:
        batch = min(BOOTSTRAP_BATCH_SIZE, BOOTSTRAP_RESAMPLES - offset)
        indices = rng.integers(0, x.shape[0], size=(batch, x.shape[0]))
        xb = x[indices, :]
        yb = y[indices, :]
        xc = xb - xb.mean(axis=1, keepdims=True)
        yc = yb - yb.mean(axis=1, keepdims=True)
        numerator = np.einsum("bnt,bnp->btp", xc, yc, optimize=True)
        denominator = np.sqrt(
            np.einsum("bnt,bnt->bt", xc, xc, optimize=True)[:, :, None]
            * np.einsum("bnp,bnp->bp", yc, yc, optimize=True)[:, None, :]
        )
        with np.errstate(divide="ignore", invalid="ignore"):
            output[offset : offset + batch] = numerator / denominator
        offset += batch
    if not np.isfinite(output).all():
        raise ValueError("Nonfinite joint bootstrap correlation")
    return output


def quantiles(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q = np.quantile(values, [0.025, 0.5, 0.975], axis=0)
    return q[1], q[0], q[2]


def build_cross_pc(
    traits: list[str], definitions: dict[str, str], observed: np.ndarray, bootstrap: np.ndarray,
    aa1_all: pd.DataFrame, aa1_members: pd.DataFrame,
) -> pd.DataFrame:
    aa1_lookup = aa1_all.set_index(["pc", "trait"]).to_dict(orient="index")
    associated_keys = set(zip(aa1_members["pc"], aa1_members["trait"]))
    boot_abs = np.abs(bootstrap)
    boot_squared = bootstrap * bootstrap
    boot_concentration_all = boot_squared / boot_squared.sum(axis=2, keepdims=True)
    rows: list[dict[str, object]] = []
    for target_index, pc in enumerate(PC_ORDER):
        off_indices = [index for index in range(6) if index != target_index]
        target = observed[:, target_index]
        absolute = np.abs(target)
        off_abs = np.abs(observed[:, off_indices])
        off_arg = np.argmax(off_abs, axis=1)
        off_index = np.asarray(off_indices)[off_arg]
        largest_off = off_abs[np.arange(len(traits)), off_arg]
        concentration = target * target / np.sum(observed * observed, axis=1)

        boot_target = boot_abs[:, :, target_index]
        boot_off = boot_abs[:, :, off_indices]
        boot_largest_off = boot_off.max(axis=2)
        boot_margin = boot_target - boot_largest_off
        boot_ratio = boot_target / (boot_largest_off + EPSILON)
        boot_concentration = boot_concentration_all[:, :, target_index]
        target_largest = boot_target >= boot_largest_off
        exact_ties = boot_target == boot_largest_off

        distributions = {
            "target_abs_r": quantiles(boot_target),
            "largest_offtarget_abs_r": quantiles(boot_largest_off),
            "specificity_margin": quantiles(boot_margin),
            "specificity_ratio": quantiles(boot_ratio),
            "concentration_fraction": quantiles(boot_concentration),
        }
        for trait_index, trait in enumerate(traits):
            source = aa1_lookup[(pc, trait)]
            if not np.isclose(target[trait_index], float(source["pearson_r"]), atol=2e-12, rtol=2e-12):
                raise ValueError(f"Observed correlation does not reproduce AA-1: {pc}/{trait}")
            is_associated = (pc, trait) in associated_keys
            probability = float(target_largest[:, trait_index].mean())
            is_defining = bool(is_associated and probability >= PRIMARY_TARGET_LARGEST)
            conc = float(concentration[trait_index])
            if is_defining and conc >= 0.75:
                tier = "HIGHLY CONCENTRATED"
            elif is_defining and conc >= 0.50:
                tier = "MODERATELY CONCENTRATED"
            elif is_defining:
                tier = "TARGET-DOMINANT"
            elif is_associated:
                tier = "BROAD / CROSS-PC"
            else:
                tier = "NOT PC-ASSOCIATED"
            row: dict[str, object] = {
                "pc": pc,
                "trait": trait,
                "canonical_definition": definitions[trait],
                "pole": "positive" if target[trait_index] > 0 else "negative",
                **{f"r_PC{i + 1}": observed[trait_index, i] for i in range(6)},
                "target_pearson_r": target[trait_index],
                "target_abs_r": absolute[trait_index],
                "target_r_squared": target[trait_index] ** 2,
                "largest_offtarget_abs_r": largest_off[trait_index],
                "largest_offtarget_pc": f"PC{off_index[trait_index] + 1}",
                "largest_offtarget_signed_r": observed[trait_index, off_index[trait_index]],
                "specificity_margin": absolute[trait_index] - largest_off[trait_index],
                "specificity_ratio": absolute[trait_index] / (largest_off[trait_index] + EPSILON),
                "pc1_6_concentration_fraction": conc,
                "BH_FDR_q": source["BH_FDR_q"],
                "bootstrap_sign_stability": source["bootstrap_sign_stability"],
                "aa1_bootstrap_seed": source["bootstrap_seed"],
                "aa1_bootstrap_resamples": source["bootstrap_resamples"],
                "is_pc_associated": is_associated,
                "specificity_bootstrap_seed": BOOTSTRAP_SEED,
                "specificity_bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                "target_is_largest_probability": probability,
                "target_largest_exact_tie_count": int(exact_ties[:, trait_index].sum()),
                "is_primary_pc_defining": is_defining,
                "is_target_dominant": is_defining,
                "is_highly_concentrated": bool(is_defining and conc >= 0.75),
                "is_moderately_concentrated": bool(is_defining and 0.50 <= conc < 0.75),
                "specificity_tier": tier,
            }
            for metric, (median, q025, q975) in distributions.items():
                row[f"{metric}_median"] = median[trait_index]
                row[f"{metric}_q025"] = q025[trait_index]
                row[f"{metric}_q975"] = q975[trait_index]
            rows.append(row)
    return pd.DataFrame(rows)


def pareto_classification(cross: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for pc in PC_ORDER:
        for pole in POLE_ORDER:
            group = cross[(cross["pc"] == pc) & (cross["pole"] == pole)].copy()
            metrics = group[["target_abs_r", "specificity_margin", "pc1_6_concentration_fraction"]].to_numpy(float)
            names = group["trait"].tolist()
            for i, row in enumerate(group.itertuples(index=False)):
                dominators = []
                for j, other in enumerate(metrics):
                    if i == j:
                        continue
                    if np.all(other >= metrics[i] - EPSILON) and np.any(other > metrics[i] + EPSILON):
                        dominators.append(names[j])
                rows.append({
                    "pc": pc,
                    "pole": pole,
                    "trait": row.trait,
                    "target_pearson_r": row.target_pearson_r,
                    "target_abs_r": row.target_abs_r,
                    "specificity_margin": row.specificity_margin,
                    "pc1_6_concentration_fraction": row.pc1_6_concentration_fraction,
                    "target_is_largest_probability": row.target_is_largest_probability,
                    "is_pc_associated": row.is_pc_associated,
                    "is_primary_pc_defining": row.is_primary_pc_defining,
                    "is_pareto_frontier": not dominators,
                    "dominated_by_count": len(dominators),
                    "dominated_by_traits": joined(dominators),
                })
    return ordered_frame(pd.DataFrame(rows))


def defining_sets(cross: pd.DataFrame, pareto: pd.DataFrame) -> pd.DataFrame:
    result = cross.copy()
    frontier = set(
        zip(
            pareto.loc[pareto["is_pareto_frontier"], "pc"],
            pareto.loc[pareto["is_pareto_frontier"], "trait"],
        )
    )
    result["is_pareto_frontier"] = [
        (row.pc, row.trait) in frontier for row in result.itertuples(index=False)
    ]
    memberships = []
    for row in result.itertuples(index=False):
        labels = []
        if row.is_pc_associated:
            labels.append("ASSOCIATED FAMILY")
        if row.is_primary_pc_defining:
            labels.append("PC-DEFINING CORE")
        if row.is_highly_concentrated:
            labels.append("HIGHLY CONCENTRATED")
        if row.is_pareto_frontier:
            labels.append("PARETO FRONTIER")
        memberships.append(";".join(labels) if labels else "NONE")
    result["set_membership"] = memberships
    keep = [
        "pc", "pole", "trait", "canonical_definition", "set_membership",
        "is_pc_associated", "is_primary_pc_defining", "is_target_dominant", "is_highly_concentrated",
        "is_moderately_concentrated", "is_pareto_frontier", "specificity_tier",
        "target_pearson_r", "target_abs_r", "largest_offtarget_pc",
        "largest_offtarget_signed_r", "largest_offtarget_abs_r", "specificity_margin",
        "specificity_ratio", "pc1_6_concentration_fraction",
        "target_is_largest_probability", "specificity_margin_median",
        "specificity_margin_q025", "specificity_margin_q975",
        "concentration_fraction_median", "concentration_fraction_q025",
        "concentration_fraction_q975", "BH_FDR_q", "bootstrap_sign_stability",
    ]
    return ordered_frame(result[keep])


def sensitivity_table(cross: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for effect in EFFECT_SENSITIVITY:
        for dominance in DOMINANCE_SENSITIVITY:
            associated = (
                (cross["target_abs_r"] >= effect)
                & (cross["BH_FDR_q"] < FDR_THRESHOLD)
                & (cross["bootstrap_sign_stability"] >= SIGN_STABILITY_THRESHOLD)
            )
            defining = associated & (cross["target_is_largest_probability"] >= dominance)
            for pc in PC_ORDER:
                for pole in POLE_ORDER:
                    family = (cross["pc"] == pc) & (cross["pole"] == pole)
                    record: dict[str, object] = {
                        "pc": pc,
                        "pole": pole,
                        "target_abs_r_threshold": effect,
                        "target_is_largest_probability_threshold": dominance,
                        "associated_count": int((family & associated).sum()),
                        "pc_defining_count": int((family & defining).sum()),
                        "pc_defining_traits": joined(cross.loc[family & defining, "trait"].tolist()),
                    }
                    for cutoff in CONCENTRATION_SENSITIVITY:
                        selected = family & defining & (cross["pc1_6_concentration_fraction"] >= cutoff)
                        tag = str(cutoff).replace(".", "_")
                        record[f"concentration_at_least_{tag}_count"] = int(selected.sum())
                        record[f"concentration_at_least_{tag}_traits"] = joined(
                            cross.loc[selected, "trait"].tolist()
                        )
                    rows.append(record)
    result = pd.DataFrame(rows)
    result["_pc"] = result["pc"].map({pc: i for i, pc in enumerate(PC_ORDER)})
    result["_pole"] = result["pole"].map({pole: i for i, pole in enumerate(POLE_ORDER)})
    return result.sort_values(
        ["target_abs_r_threshold", "target_is_largest_probability_threshold", "_pc", "_pole"],
        kind="mergesort",
    ).drop(columns=["_pc", "_pole"])


def observed_profile_metrics(vector: np.ndarray, y: np.ndarray, target_index: int) -> dict[str, object]:
    correlations = correlation_matrix(vector[:, None], y)[0]
    off_indices = [i for i in range(6) if i != target_index]
    off_abs = np.abs(correlations[off_indices])
    off_index = off_indices[int(np.argmax(off_abs))]
    target_abs = abs(correlations[target_index])
    largest_off = abs(correlations[off_index])
    return {
        **{f"r_PC{i + 1}": correlations[i] for i in range(6)},
        "target_pearson_r": correlations[target_index],
        "target_abs_r": target_abs,
        "largest_offtarget_pc": f"PC{off_index + 1}",
        "largest_offtarget_signed_r": correlations[off_index],
        "largest_offtarget_abs_r": largest_off,
        "specificity_margin": target_abs - largest_off,
        "specificity_ratio": target_abs / (largest_off + EPSILON),
        "pc1_6_concentration_fraction": correlations[target_index] ** 2 / np.sum(correlations * correlations),
    }


def build_composites(
    repo: Path, merged: pd.DataFrame, traits: list[str], sets: pd.DataFrame, pareto: pd.DataFrame, paths: dict[str, Path]
) -> tuple[pd.DataFrame, dict[str, object]]:
    y = merged[PC_ORDER].to_numpy(float)
    x_lookup = {trait: merged[trait].to_numpy(float) for trait in traits}
    records: list[dict[str, object]] = []

    # Stream-filter the shared visualization table so no Llama/Gemma numerical
    # value is loaded into the analysis.
    qwen_reference_rows = []
    with paths["pc3_group_scores"].open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["model"] == "qwen" and row["group"] == "Affiliation":
                qwen_reference_rows.append(row)
    reference = pd.DataFrame(qwen_reference_rows)
    numeric_reference_columns = [
        "group_mean_trait_percentile", "percentile_1", "percentile_2", "percentile_3",
    ]
    reference[numeric_reference_columns] = reference[numeric_reference_columns].astype(float)
    reference = reference.sort_values("persona", kind="mergesort")
    exact_members = ["empathetic", "agreeable", "altruistic"]
    exact_formula_ok = (
        len(reference) == 275
        and all(reference[f"trait_{i + 1}"].eq(name).all() for i, name in enumerate(exact_members))
        and np.allclose(
            reference["group_mean_trait_percentile"].to_numpy(float),
            reference[["percentile_1", "percentile_2", "percentile_3"]].to_numpy(float).mean(axis=1),
            atol=1e-12,
            rtol=1e-12,
        )
        and reference["persona"].tolist() == merged["persona"].tolist()
    )
    if not exact_formula_ok:
        raise ValueError("Canonical PC3 Affiliation composite formula did not reproduce exactly")
    ref_vector = reference["group_mean_trait_percentile"].to_numpy(float)
    ref_metrics = observed_profile_metrics(ref_vector, y, 2)
    records.append({
        "analysis_label": "SECONDARY / DESCRIPTIVE COMPOSITES",
        "composite_id": "canonical_pc3_affiliation_surface",
        "composite_type": "CANONICAL VISUALIZATION REFERENCE",
        "pc": "PC3",
        "pole": "negative",
        "availability": "AVAILABLE_EXACT_PROVENANCE",
        "member_count": 3,
        "member_traits": ";".join(exact_members),
        "profile_formula": "mean(within-Qwen midrank percentile(empathetic), within-Qwen midrank percentile(agreeable), within-Qwen midrank percentile(altruistic))",
        "profile_scale": "within-Qwen midrank percentile; weights exactly 1/3; composite not reranked or restandardized",
        **ref_metrics,
    })

    for pc_index, pc in enumerate(PC_ORDER):
        for pole in POLE_ORDER:
            group = sets[(sets["pc"] == pc) & (sets["pole"] == pole)]
            primary = group[group["is_primary_pc_defining"]].sort_values(
                ["pc1_6_concentration_fraction", "target_abs_r", "trait"],
                ascending=[False, False, True], kind="mergesort",
            )
            frontier_names = set(
                pareto.loc[
                    (pareto["pc"] == pc) & (pareto["pole"] == pole) & pareto["is_pareto_frontier"],
                    "trait",
                ]
            )
            frontier = group[group["trait"].isin(frontier_names)].sort_values(
                ["pc1_6_concentration_fraction", "target_abs_r", "trait"],
                ascending=[False, False, True], kind="mergesort",
            )
            primary_members = primary.head(3)["trait"].tolist()
            pareto_members = frontier.head(3)["trait"].tolist()
            for kind, members in [("TOP3_TARGET_DOMINANT", primary_members), ("TOP3_PARETO_FRONTIER", pareto_members)]:
                record: dict[str, object] = {
                    "analysis_label": "SECONDARY / DESCRIPTIVE COMPOSITES",
                    "composite_id": f"{pc.lower()}_{pole}_{kind.lower()}",
                    "composite_type": kind,
                    "pc": pc,
                    "pole": pole,
                    "member_count": len(members),
                    "member_traits": ";".join(members),
                    "profile_formula": "unweighted mean of saved raw Qwen activation-cosine trait profiles",
                    "profile_scale": "raw activation cosine; equal weights",
                }
                if len(members) < 3:
                    record["availability"] = "UNAVAILABLE_FEWER_THAN_THREE_ELIGIBLE_TRAITS"
                elif kind == "TOP3_PARETO_FRONTIER" and members == primary_members:
                    record["availability"] = "NOT_EVALUATED_IDENTICAL_TO_TOP3_TARGET_DOMINANT"
                else:
                    record["availability"] = "AVAILABLE"
                    vector = np.mean(np.column_stack([x_lookup[name] for name in members]), axis=1)
                    record.update(observed_profile_metrics(vector, y, pc_index))
                records.append(record)
    columns = [
        "analysis_label", "composite_id", "composite_type", "pc", "pole", "availability",
        "member_count", "member_traits", "profile_formula", "profile_scale",
        *[f"r_PC{i}" for i in range(1, 7)], "target_pearson_r", "target_abs_r",
        "largest_offtarget_pc", "largest_offtarget_signed_r", "largest_offtarget_abs_r",
        "specificity_margin", "specificity_ratio", "pc1_6_concentration_fraction",
    ]
    frame = pd.DataFrame(records).reindex(columns=columns)
    provenance = {
        "status": "EXACT_CANONICAL_REFERENCE_LOCATED",
        "group": "Affiliation",
        "members_in_canonical_order": exact_members,
        "weights": [1 / 3, 1 / 3, 1 / 3],
        "formula": records[0]["profile_formula"],
        "reference_qwen_compatibility_commit": "d68921b898ed179194223f449149d715298cdabe",
        "artifact_paths": [
            str(paths["pc3_group_scores"].relative_to(repo)),
            str(paths["pc3_methodology"].relative_to(repo)),
            str(paths["pc3_generator"].relative_to(repo)),
            str(paths["pc3_ridge_data"].relative_to(repo)),
        ],
        "metrics": {key: float(value) if isinstance(value, (float, np.floating)) else value for key, value in ref_metrics.items()},
    }
    return frame, provenance


def build_human_refinement(
    judgments: pd.DataFrame, inventory: pd.DataFrame, sets: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    family_keys = inventory[["family_id", "pc", "pole"]].drop_duplicates()
    if len(family_keys) != 12 or family_keys["family_id"].nunique() != 12:
        raise ValueError("Expected one PC/pole key for each of 12 AA-1 family IDs")
    base_columns = list(judgments.columns)
    refined = judgments.merge(family_keys, on="family_id", how="left", validate="many_to_one")
    additions: list[dict[str, object]] = []
    for row in refined.itertuples(index=False):
        family = sets[(sets["pc"] == row.pc) & (sets["pole"] == row.pole)]
        associated = set(family.loc[family["is_pc_associated"], "trait"])
        defining = set(family.loc[family["is_primary_pc_defining"], "trait"])
        highly = set(family.loc[family["is_highly_concentrated"], "trait"])
        pareto = set(family.loc[family["is_pareto_frontier"], "trait"])
        covered = set(split_semicolon(row.covered_qwen_family_members)) & associated
        additions.append({
            "associated_qwen_traits_covered": joined(covered),
            "associated_qwen_traits_covered_count": len(covered),
            "pc_defining_qwen_traits_covered": joined(covered & defining),
            "pc_defining_qwen_traits_covered_count": len(covered & defining),
            "highly_concentrated_qwen_traits_covered": joined(covered & highly),
            "highly_concentrated_qwen_traits_covered_count": len(covered & highly),
            "pareto_frontier_qwen_traits_covered": joined(covered & pareto),
            "pareto_frontier_qwen_traits_covered_count": len(covered & pareto),
            "pc_defining_traits_not_covered_by_this_construct": joined(defining - covered),
            "mapping_judgment_changed": False,
        })
    additions_frame = pd.DataFrame(additions)
    refined = pd.concat([refined.reset_index(drop=True), additions_frame], axis=1)
    refined = refined[["pc", "pole", *base_columns, *additions_frame.columns]]

    summary_rows: list[dict[str, object]] = []
    for pc in PC_ORDER:
        for pole in POLE_ORDER:
            family = sets[(sets["pc"] == pc) & (sets["pole"] == pole)]
            family_ids = family_keys.loc[(family_keys["pc"] == pc) & (family_keys["pole"] == pole), "family_id"]
            if len(family_ids) != 1:
                raise ValueError(f"Missing unique family ID for {pc}/{pole}")
            family_id = family_ids.iloc[0]
            maps = refined[refined["family_id"] == family_id]
            associated = set(family.loc[family["is_pc_associated"], "trait"])
            defining = set(family.loc[family["is_primary_pc_defining"], "trait"])
            highly = set(family.loc[family["is_highly_concentrated"], "trait"])
            frontier = set(family.loc[family["is_pareto_frontier"], "trait"])
            covered_associated: set[str] = set()
            covered_defining: set[str] = set()
            covered_highly: set[str] = set()
            covered_frontier: set[str] = set()
            associated_constructs, defining_constructs, high_constructs, pareto_constructs = [], [], [], []
            for mapping in maps.itertuples(index=False):
                construct_id = str(mapping.human_construct_id)
                if not construct_id:
                    continue
                label = f"{mapping.human_construct_name} [{construct_id}]"
                covered = set(split_semicolon(mapping.covered_qwen_family_members)) & associated
                covered_associated |= covered
                covered_defining |= covered & defining
                covered_highly |= covered & highly
                covered_frontier |= covered & frontier
                if covered:
                    associated_constructs.append(label)
                if covered & defining:
                    defining_constructs.append(label)
                if covered & highly:
                    high_constructs.append(label)
                if covered & frontier:
                    pareto_constructs.append(label)
            summary_rows.append({
                "pc": pc,
                "pole": pole,
                "family_id": family_id,
                "associated_trait_count": len(associated),
                "pc_defining_trait_count": len(defining),
                "highly_concentrated_trait_count": len(highly),
                "moderately_concentrated_trait_count": int(family["is_moderately_concentrated"].sum()),
                "target_dominant_below_0_50_concentration_count": int(
                    (family["is_primary_pc_defining"] & ~family["is_highly_concentrated"] & ~family["is_moderately_concentrated"]).sum()
                ),
                "broad_cross_pc_trait_count": int((family["is_pc_associated"] & ~family["is_primary_pc_defining"]).sum()),
                "pareto_frontier_trait_count": len(frontier),
                "associated_traits_covered_by_any_human_construct_count": len(covered_associated),
                "pc_defining_traits_covered_by_any_human_construct_count": len(covered_defining),
                "highly_concentrated_traits_covered_by_any_human_construct_count": len(covered_highly),
                "pareto_frontier_traits_covered_by_any_human_construct_count": len(covered_frontier),
                "human_constructs_covering_any_associated_trait": joined(associated_constructs),
                "human_constructs_covering_any_pc_defining_trait": joined(defining_constructs),
                "human_constructs_covering_highly_concentrated_traits": joined(high_constructs),
                "human_constructs_covering_pareto_frontier_traits": joined(pareto_constructs),
                "unmatched_pc_defining_traits": joined(defining - covered_defining),
                "unmatched_highly_concentrated_traits": joined(highly - covered_highly),
                "unmatched_pareto_frontier_traits": joined(frontier - covered_frontier),
            })
    summary = pd.DataFrame(summary_rows)
    return refined, summary


def fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.{digits}f}"


def report_markdown(sets: pd.DataFrame, summary: pd.DataFrame, sensitivity: pd.DataFrame, composites: pd.DataFrame) -> str:
    lines = [
        "# Qwen PC Trait Specificity Report",
        "",
        "## Result in one sentence",
        "",
        "The original AA-1 families identify **PC-associated traits** (strong target-PC salience), whereas this refinement identifies the smaller **PC-defining core** whose target PC is preferentially dominant across paired role bootstraps; strength and specificity are reported separately throughout.",
        "",
        "## Associated family versus PC-defining core",
        "",
        "| PC/pole | Associated | PC-defining | Highly concentrated | Pareto frontier |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.pc} {row.pole} | {row.associated_trait_count} | {row.pc_defining_trait_count} | {row.highly_concentrated_trait_count} | {row.pareto_frontier_trait_count} |"
        )

    lines += ["", "## Complete signed trait sets", ""]
    for pc in PC_ORDER:
        for pole in POLE_ORDER:
            group = sets[(sets["pc"] == pc) & (sets["pole"] == pole)].sort_values(
                ["target_abs_r", "trait"], ascending=[False, True], kind="mergesort"
            )
            associated_names = group.loc[group["is_pc_associated"], "trait"].tolist()
            defining_names = group.loc[group["is_primary_pc_defining"], "trait"].tolist()
            high_names = group.loc[group["is_highly_concentrated"], "trait"].tolist()
            moderate_names = group.loc[group["is_moderately_concentrated"], "trait"].tolist()
            low_concentration_names = group.loc[
                group["is_primary_pc_defining"] & ~group["is_highly_concentrated"] & ~group["is_moderately_concentrated"],
                "trait",
            ].tolist()
            broad_names = group.loc[group["is_pc_associated"] & ~group["is_primary_pc_defining"], "trait"].tolist()
            pareto_names = group.loc[group["is_pareto_frontier"], "trait"].tolist()
            lines += [
                f"### {pc} {pole}",
                "",
                f"- Associated family ({len(associated_names)}): {', '.join(associated_names) if associated_names else 'none'}",
                "",
                f"- PC-defining core ({len(defining_names)}): {', '.join(defining_names) if defining_names else 'none'}",
                "",
                f"- Highly concentrated ({len(high_names)}): {', '.join(high_names) if high_names else 'none'}",
                "",
                f"- Moderately concentrated ({len(moderate_names)}): {', '.join(moderate_names) if moderate_names else 'none'}",
                "",
                f"- Target-dominant below 0.50 concentration ({len(low_concentration_names)}): {', '.join(low_concentration_names) if low_concentration_names else 'none'}",
                "",
                f"- Broad / cross-PC ({len(broad_names)}): {', '.join(broad_names) if broad_names else 'none'}",
                "",
                f"- Pareto frontier ({len(pareto_names)}): {', '.join(pareto_names) if pareto_names else 'none'}",
                "",
            ]

    lines += ["", "## Top PC-defining candidates", ""]
    for pc in PC_ORDER:
        for pole in POLE_ORDER:
            group = sets[(sets["pc"] == pc) & (sets["pole"] == pole) & sets["is_primary_pc_defining"]].sort_values(
                ["pc1_6_concentration_fraction", "target_abs_r", "trait"],
                ascending=[False, False, True], kind="mergesort",
            )
            lines += [f"### {pc} {pole}", ""]
            if group.empty:
                lines += ["No primary PC-defining traits.", ""]
                continue
            lines += [
                "| Trait | Target r | Largest off-target | Margin | Concentration | Target-largest p | Tier |",
                "|---|---:|---:|---:|---:|---:|---|",
            ]
            for row in group.head(5).itertuples(index=False):
                lines.append(
                    f"| {row.trait} | {fmt(row.target_pearson_r)} | {row.largest_offtarget_pc} {fmt(row.largest_offtarget_signed_r)} | {fmt(row.specificity_margin)} | {fmt(row.pc1_6_concentration_fraction)} | {fmt(row.target_is_largest_probability)} | {row.specificity_tier} |"
                )
            lines.append("")

    lines += [
        "## Human-measurement inventory: associated family versus defining core",
        "",
        "These are intersections with the frozen AA-1 semantic mappings, not new human/model correspondence evidence.",
        "",
        "| PC/pole | Associated traits covered | Defining traits covered | Constructs covering defining core | Unmatched defining traits |",
        "|---|---:|---:|---|---|",
    ]
    for row in summary.itertuples(index=False):
        constructs = str(row.human_constructs_covering_any_pc_defining_trait).replace(";", "; ") or "—"
        unmatched = str(row.unmatched_pc_defining_traits).replace(";", ", ") or "—"
        lines.append(
            f"| {row.pc} {row.pole} | {row.associated_traits_covered_by_any_human_construct_count}/{row.associated_trait_count} | {row.pc_defining_traits_covered_by_any_human_construct_count}/{row.pc_defining_trait_count} | {constructs} | {unmatched} |"
        )
    associated_total = int(summary["associated_trait_count"].sum())
    associated_covered = int(summary["associated_traits_covered_by_any_human_construct_count"].sum())
    defining_total = int(summary["pc_defining_trait_count"].sum())
    defining_covered = int(summary["pc_defining_traits_covered_by_any_human_construct_count"].sum())
    assoc_fraction = associated_covered / associated_total if associated_total else 0.0
    defining_fraction = defining_covered / defining_total if defining_total else 0.0
    lines += [
        "",
        f"Across signed families, the frozen mappings explicitly cover {associated_covered}/{associated_total} associated memberships ({assoc_fraction:.1%}) and {defining_covered}/{defining_total} PC-defining memberships ({defining_fraction:.1%}). The apparent match is therefore **qualitatively different and more focused**, not a uniform strengthening: specificity removes broad cross-PC members, concentrates attention on a smaller diagnostic core, and leaves the family-by-family coverage uneven. This remains an inventory-level description, not a human/model correspondence test.",
        "",
        "## PC1 requested inspection",
        "",
        "| Trait | Associated? | PC-defining? | Tier | PC1 r | Largest off-target | Margin | Concentration |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for trait in ["transparent", "factual", "analytical", "methodical", "conscientious"]:
        item = sets[(sets["pc"] == "PC1") & (sets["trait"] == trait)].iloc[0]
        lines.append(
            f"| {trait} | {'yes' if item.is_pc_associated else 'no'} | {'yes' if item.is_primary_pc_defining else 'no'} | {item.specificity_tier} | {fmt(item.target_pearson_r)} | {item.largest_offtarget_pc} {fmt(item.largest_offtarget_signed_r)} | {fmt(item.specificity_margin)} | {fmt(item.pc1_6_concentration_fraction)} |"
        )

    lines += [
        "",
        "## PC3 requested inspection",
        "",
        "Selection was completed before this post-selection semantic inspection.",
        "",
        "| Trait | Pole | Associated? | PC-defining? | Tier | PC3 r | Largest off-target | Margin | Concentration |",
        "|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    pc3_traits = [
        "callous", "cynical", "pessimistic", "benevolent", "nurturing", "supportive",
        "agreeable", "altruistic", "empathetic", "forgiving", "collaborative",
        "accommodating", "conciliatory", "tactful",
    ]
    # This is post-selection inspection of the complete trait-target table.
    for trait in pc3_traits:
        item = sets[(sets["pc"] == "PC3") & (sets["trait"] == trait)].iloc[0]
        lines.append(
            f"| {trait} | {item.pole} | {'yes' if item.is_pc_associated else 'no'} | {'yes' if item.is_primary_pc_defining else 'no'} | {item.specificity_tier} | {fmt(item.target_pearson_r)} | {item.largest_offtarget_pc} {fmt(item.largest_offtarget_signed_r)} | {fmt(item.specificity_margin)} | {fmt(item.pc1_6_concentration_fraction)} |"
        )

    reference = composites[composites["composite_id"] == "canonical_pc3_affiliation_surface"].iloc[0]
    lines += [
        "",
        "## Canonical PC3 visualization reference",
        "",
        "The indexed Qwen Affiliation surface is exactly the equal-weight mean of within-Qwen midrank percentiles for `empathetic`, `agreeable`, and `altruistic`; it was not used to tune thresholds.",
        "",
        "| Target r | Largest off-target | Margin | Ratio | PC1-PC6 concentration |",
        "|---:|---:|---:|---:|---:|",
        f"| {fmt(reference.target_pearson_r)} | {reference.largest_offtarget_pc} {fmt(reference.largest_offtarget_signed_r)} | {fmt(reference.specificity_margin)} | {fmt(reference.specificity_ratio)} | {fmt(reference.pc1_6_concentration_fraction)} |",
        "",
        "## Threshold sensitivity",
        "",
        "All 3 × 3 effect/dominance combinations are reported in `qwen_pc_specificity_threshold_sensitivity.csv`; no combination was selected after inspection. The table also reports descriptive concentration cutoffs 0.60, 0.70, and 0.80.",
        "",
        "## Epistemic boundary",
        "",
        "Observed: saved Qwen trait-PC correlations, cross-PC profiles, margins, PC1-PC6 concentration, paired-bootstrap target dominance, and availability of frozen SAPA constructs/items.",
        "",
        "Interpretation: traits combining strength with relative specificity are more diagnostic labels for a Qwen PC than traits selected by target correlation alone.",
        "",
        "Hypothesis: a mapped human construct could reflect the same latent property.",
        "",
        "Unknown: human-model quantitative correspondence, causal meaning, respondent-level mapping, and cross-model generalization.",
        "",
        "This analysis stops at the requested specificity-refined trait and human inventories.",
    ]
    return "\n".join(lines) + "\n"


def pc3_audit_markdown(provenance: dict[str, object]) -> str:
    metrics = provenance["metrics"]
    artifact_lines = "\n".join(f"- `{path}`" for path in provenance["artifact_paths"])
    return f"""# Canonical Three-Trait PC3 Composite Audit

Status: **EXACT CANONICAL REFERENCE LOCATED**.

## Navigation route

The artifact was located through `research/REPO_NAVIGATION.md`, then confirmed
in `research/REPO_FILE_INDEX.csv` and `research/RAW_URL_INDEX.md`. The indexed
source chain is:

{artifact_lines}

## Exact constituents and formula

The canonical Qwen Editorial `Affiliation` surface uses, in saved order:

1. `empathetic`
2. `agreeable`
3. `altruistic`

For each of the 275 Qwen roles, the viewer computes the within-Qwen midrank
percentile of each saved raw trait-affinity profile, then takes their exact
equal-weight mean. Each weight is `1/3`. The mean is not reranked or
restandardized. The current viewer generator also verifies byte-for-byte Qwen
scientific-data compatibility against commit
`d68921b898ed179194223f449149d715298cdabe`.

## PC1-PC6 benchmark

| Metric | Value |
|---|---:|
| PC1 r | {metrics['r_PC1']:.6f} |
| PC2 r | {metrics['r_PC2']:.6f} |
| PC3 r | {metrics['r_PC3']:.6f} |
| PC4 r | {metrics['r_PC4']:.6f} |
| PC5 r | {metrics['r_PC5']:.6f} |
| PC6 r | {metrics['r_PC6']:.6f} |
| Target PC3 absolute r | {metrics['target_abs_r']:.6f} |
| Largest off-target | {metrics['largest_offtarget_pc']} ({metrics['largest_offtarget_signed_r']:.6f}) |
| Specificity margin | {metrics['specificity_margin']:.6f} |
| Specificity ratio | {metrics['specificity_ratio']:.6f} |
| PC1-PC6 concentration | {metrics['pc1_6_concentration_fraction']:.6f} |

The reference is secondary and descriptive. No threshold was chosen or changed
to make it pass, and the reference did not affect any single-trait selection.
"""


def source_manifest(repo: Path, paths: dict[str, Path], provenance: dict[str, object], generated_at: str) -> dict[str, object]:
    return {
        "analysis": "Qwen PC-associated versus PC-defining trait specificity and frozen SAPA inventory refinement",
        "generated_at_utc": generated_at,
        "branch": BRANCH,
        "starting_sha": STARTING_SHA,
        "source_aa1_commit": AA1_COMMIT,
        "specificity_spec_freeze_commit": SPEC_FREEZE_COMMIT,
        "model": QWEN_MODEL,
        "role_count": 275,
        "trait_count": 240,
        "pc_count": 6,
        "source_hashes": {str(path.relative_to(repo)): sha256(path) for path in paths.values()},
        "navigation_sources_consulted": [
            "research/REPO_NAVIGATION.md",
            "research/REPO_FILE_INDEX.csv",
            "research/RAW_URL_INDEX.md",
        ],
        "rules": {
            "pc_associated": "target |r| >= 0.50; within-PC BH-FDR q < 0.01; AA-1 bootstrap sign stability >= 0.95",
            "primary_pc_defining": "PC-associated and paired-bootstrap target-is-largest probability >= 0.95",
            "highly_concentrated": "primary PC-defining and observed PC1-PC6 concentration >= 0.75",
            "moderately_concentrated": "primary PC-defining and observed PC1-PC6 concentration >= 0.50 and < 0.75",
            "pareto_universe": "all 240 traits divided by observed target-correlation pole within each PC",
            "pareto_objectives": ["higher target |r|", "higher specificity margin", "higher PC1-PC6 concentration"],
        },
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "generator": "NumPy default_rng / PCG64",
            "resamples": BOOTSTRAP_RESAMPLES,
            "batch_size": BOOTSTRAP_BATCH_SIZE,
            "paired_across_traits_and_PC1_PC6": True,
        },
        "epsilon": EPSILON,
        "pc3_reference_composite": provenance,
        "firewall": {
            "models_used": [QWEN_MODEL],
            "Llama_or_Gemma_values_loaded": False,
            "AA7_scientific_result_paths_used": [],
            "human_respondent_rows_loaded_or_scored": False,
            "human_model_projection_performed": False,
            "human_model_correspondence_test_run": False,
            "next_experiment_selected": False,
            "respondent_level_human_microdata_emitted": False,
        },
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
        "concentration_caveat": "Concentration is within PC1-PC6 only, not the proportion of total trait activation-space variance explained uniquely by the target PC.",
    }


def compute(repo: Path, output: Path, generated_at: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    merged, traits, aa1_all, aa1_members, judgments, inventory, definitions, paths = load_inputs(repo)
    x = merged[traits].to_numpy(float)
    y = merged[PC_ORDER].to_numpy(float)
    observed = correlation_matrix(x, y)
    bootstrap = joint_bootstrap(x, y)
    cross = build_cross_pc(traits, definitions, observed, bootstrap, aa1_all, aa1_members)
    pareto = pareto_classification(cross)
    sets = defining_sets(cross, pareto)
    sensitivity = sensitivity_table(cross)
    composites, pc3_provenance = build_composites(repo, merged, traits, sets, pareto, paths)
    human_inventory, human_summary = build_human_refinement(judgments, inventory, sets)

    cross.to_csv(output / "qwen_trait_cross_pc_specificity_all.csv", index=False, lineterminator="\n")
    sets.to_csv(output / "qwen_pc_defining_trait_sets.csv", index=False, lineterminator="\n")
    pareto.to_csv(output / "qwen_pc_trait_specificity_pareto.csv", index=False, lineterminator="\n")
    sensitivity.to_csv(output / "qwen_pc_specificity_threshold_sensitivity.csv", index=False, lineterminator="\n")
    composites.to_csv(output / "qwen_pc_specificity_composites.csv", index=False, lineterminator="\n")
    human_inventory.to_csv(output / "qwen_pc_specificity_human_inventory.csv", index=False, lineterminator="\n")
    human_summary.to_csv(output / "qwen_pc_specificity_human_summary.csv", index=False, lineterminator="\n")
    (output / "pc3_reference_composite_audit.md").write_text(
        pc3_audit_markdown(pc3_provenance), encoding="utf-8"
    )
    (output / "qwen_pc_specificity_report.md").write_text(
        report_markdown(sets, human_summary, sensitivity, composites), encoding="utf-8"
    )
    (output / "source_manifest.json").write_text(
        json.dumps(source_manifest(repo, paths, pc3_provenance, generated_at), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    counts = human_summary[[
        "pc", "pole", "associated_trait_count", "pc_defining_trait_count",
        "highly_concentrated_trait_count", "pareto_frontier_trait_count",
    ]].to_dict(orient="records")
    print(json.dumps({
        "cross_pc_rows": len(cross),
        "trait_set_rows": len(sets),
        "associated_rows": int(sets["is_pc_associated"].sum()),
        "pc_defining_rows": int(sets["is_primary_pc_defining"].sum()),
        "highly_concentrated_rows": int(sets["is_highly_concentrated"].sum()),
        "pareto_frontier_rows": int(sets["is_pareto_frontier"].sum()),
        "family_counts": counts,
        "pc3_reference": pc3_provenance["metrics"],
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--generated-at", default="2026-09-12T20:30:00Z")
    args = parser.parse_args()
    compute(args.repo_root.resolve(), args.output_dir.resolve(), args.generated_at)


if __name__ == "__main__":
    main()
