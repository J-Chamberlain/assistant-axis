#!/usr/bin/env python3
"""Run the preregistered 45-trait primary aggregate correspondence test."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata


OUT = Path(__file__).resolve().parent
ELIGIBLE_K = [4, 5, 6, 7, 8, 10]
STABLE_K = [4, 5, 6]
FAMILIES = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
N_PERM = 20_000
SEED = 2_026_091_304
CLIP = 0.999999999999


def row_normalize(x: np.ndarray) -> np.ndarray:
    centered = x - x.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    if np.any(norms <= 0) or not np.isfinite(norms).all():
        raise ValueError("Constant or invalid profile")
    return centered / norms


def spearman_matrix(human: np.ndarray, model: np.ndarray) -> np.ndarray:
    return row_normalize(np.apply_along_axis(rankdata, 1, human)) @ row_normalize(
        np.apply_along_axis(rankdata, 1, model)
    ).T


def assignment(corr: np.ndarray, profile_ids: list[str]) -> tuple[list[tuple[int, int]], float]:
    # Rows are lexicographic A-D. A sub-floating-point lexicographic penalty makes
    # exact profile ties deterministic without altering meaningful comparisons.
    penalty = np.arange(corr.shape[0])[:, None] * 1e-15 + np.arange(corr.shape[1])[None, :] * 1e-13
    rows, cols = linear_sum_assignment(-corr.T + penalty.T)
    pairs = sorted([(int(col), int(row)) for row, col in zip(rows, cols)])
    if len(pairs) != 4 or len({p[1] for p in pairs}) != 4:
        raise ValueError("Assignment is not injective across four distinct human profiles")
    rs = np.array([corr[f, h] for f, h in pairs])
    score = float(np.arctanh(np.clip(rs, -CLIP, CLIP)).mean())
    return pairs, score


def load_matrices() -> tuple[list[str], dict[int, dict], np.ndarray, np.ndarray]:
    human = pd.read_csv(OUT / "human_trait_profiles_45.csv")
    model = pd.read_csv(OUT / "model_family_trait_profiles_45.csv")
    traits = sorted(human["trait"].unique())
    if len(traits) != 45 or traits != sorted(model["trait"].unique()):
        raise ValueError("Human/model direct trait axes differ")
    model_primary = model.loc[model["family_id"].isin(FAMILIES)]
    model_matrix = (
        model_primary.pivot(index="family_id", columns="trait", values="three_model_consensus_value")
        .loc[FAMILIES, traits]
        .to_numpy(float)
    )
    model_norm = row_normalize(model_matrix)
    by_k = {}
    for k in range(4, 11):
        subset = human.loc[human["K"].eq(k)]
        profiles = sorted(subset["profile_id"].unique())
        matrix = subset.pivot(index="profile_id", columns="trait", values="human_trait_value").loc[profiles, traits].to_numpy(float)
        if matrix.shape != (k, 45):
            raise ValueError(f"Unexpected human matrix at K={k}: {matrix.shape}")
        by_k[k] = {"profiles": profiles, "raw": matrix, "norm": row_normalize(matrix)}
    return traits, by_k, model_matrix, model_norm


def main() -> None:
    traits, by_k, model_raw, model_norm = load_matrices()
    similarities = []
    assignments = []
    observed = {}
    family_candidates = {family: [] for family in FAMILIES}
    corr_cache = {}

    for k in ELIGIBLE_K:
        corr = by_k[k]["norm"] @ model_norm.T
        rho = spearman_matrix(by_k[k]["raw"], model_raw)
        corr_cache[k] = corr
        for h_idx, profile_id in enumerate(by_k[k]["profiles"]):
            for f_idx, family in enumerate(FAMILIES):
                similarities.append(
                    {
                        "trait_set": "45_ACCEPT_DIRECT",
                        "K": k,
                        "eligible_primary_k": True,
                        "human_profile_id": profile_id,
                        "model_family_id": family,
                        "pearson_r": corr[h_idx, f_idx],
                        "spearman_rho": rho[h_idx, f_idx],
                    }
                )
                family_candidates[family].append((corr[h_idx, f_idx], rho[h_idx, f_idx], k, profile_id))
        pairs, score = assignment(corr.T, by_k[k]["profiles"])
        pair_rows = []
        for f_idx, h_idx in pairs:
            row = {
                "trait_set": "45_ACCEPT_DIRECT",
                "K": k,
                "model_family_id": FAMILIES[f_idx],
                "human_profile_id": by_k[k]["profiles"][h_idx],
                "pearson_r": corr[h_idx, f_idx],
                "spearman_rho": rho[h_idx, f_idx],
                "fisher_z": np.arctanh(np.clip(corr[h_idx, f_idx], -CLIP, CLIP)),
            }
            pair_rows.append(row)
        back_r = float(np.tanh(score))
        for row in pair_rows:
            row["mean_fisher_z_for_K"] = score
            row["back_transformed_mean_r_for_K"] = back_r
            assignments.append(row)
        observed[k] = {"score": score, "back_r": back_r, "pairs": pair_rows}

    winner_k = max(ELIGIBLE_K, key=lambda k: (observed[k]["score"], -k))
    observed_max = observed[winner_k]["score"]

    rng = np.random.default_rng(SEED)
    null_rows = []
    family_null = {family: np.empty(N_PERM, dtype=float) for family in FAMILIES}
    global_null = np.empty(N_PERM, dtype=float)
    stable_null = np.empty(N_PERM, dtype=float)
    for draw in range(N_PERM):
        perm = rng.permutation(len(traits))
        scores = {}
        fam_max = np.full(4, -np.inf)
        for k in ELIGIBLE_K:
            corr = by_k[k]["norm"][:, perm] @ model_norm.T
            _, scores[k] = assignment(corr.T, by_k[k]["profiles"])
            fam_max = np.maximum(fam_max, corr.max(axis=0))
        max_k = max(ELIGIBLE_K, key=lambda k: (scores[k], -k))
        stable_k = max(STABLE_K, key=lambda k: (scores[k], -k))
        global_null[draw] = scores[max_k]
        stable_null[draw] = scores[stable_k]
        for idx, family in enumerate(FAMILIES):
            family_null[family][draw] = fam_max[idx]
        null_rows.append(
            {
                "permutation_index": draw + 1,
                "seed": SEED,
                "global_max_fisher_z": global_null[draw],
                "global_max_back_transformed_r": np.tanh(global_null[draw]),
                "global_maximizing_K": max_k,
                "stable_K456_max_fisher_z": stable_null[draw],
                "stable_K456_max_back_transformed_r": np.tanh(stable_null[draw]),
                "stable_K456_maximizing_K": stable_k,
                **{f"{family}_max_r": fam_max[idx] for idx, family in enumerate(FAMILIES)},
            }
        )

    global_p = float((1 + np.sum(global_null >= observed_max)) / (N_PERM + 1))
    assignments_df = pd.DataFrame(assignments).sort_values(["K", "model_family_id"])
    winner_assignments = assignments_df.loc[assignments_df["K"].eq(winner_k)]

    family_results = []
    for family in FAMILIES:
        best_r, best_rho, best_k, best_profile = max(
            family_candidates[family], key=lambda x: (x[0], -x[2], x[3])
        )
        family_p = float((1 + np.sum(family_null[family] >= best_r)) / (N_PERM + 1))
        selected = winner_assignments.loc[winner_assignments["model_family_id"].eq(family)].iloc[0]
        family_results.append(
            {
                "trait_set": "45_ACCEPT_DIRECT",
                "model_family_id": family,
                "family_specific_best_K": best_k,
                "family_specific_best_human_profile": best_profile,
                "family_specific_best_pearson_r": best_r,
                "family_specific_best_spearman_rho": best_rho,
                "family_specific_search_adjusted_p": family_p,
                "positive_adjusted_evidence": bool(best_r > 0 and family_p <= 0.05),
                "primary_global_selected_K": winner_k,
                "primary_global_selected_human_profile": selected["human_profile_id"],
                "primary_global_selected_pearson_r": selected["pearson_r"],
                "primary_global_selected_spearman_rho": selected["spearman_rho"],
            }
        )

    pd.DataFrame(similarities).sort_values(["K", "human_profile_id", "model_family_id"]).to_csv(
        OUT / "profile_similarity_45.csv", index=False, float_format="%.12g"
    )
    assignments_df.to_csv(OUT / "primary_assignments_by_k.csv", index=False, float_format="%.12g")
    pd.DataFrame(null_rows).to_csv(OUT / "bridge_permutation_null_45.csv", index=False, float_format="%.12g")
    family_df = pd.DataFrame(family_results).sort_values("model_family_id")
    family_df.to_csv(OUT / "family_specific_results.csv", index=False, float_format="%.12g")

    k_scores = [
        {
            "K": k,
            "mean_fisher_z": observed[k]["score"],
            "back_transformed_mean_r": observed[k]["back_r"],
            "maximizing_K": k == winner_k,
        }
        for k in ELIGIBLE_K
    ]
    result = {
        "analysis": "primary_45_trait_aggregate_human_model_profile_correspondence",
        "date": "2026-09-13",
        "model_used": "GPT-5.5",
        "eligible_K": ELIGIBLE_K,
        "primary_model_families": FAMILIES,
        "assignment": "maximum total raw Pearson r; injective A-D to four distinct human profiles",
        "K_score": "mean Fisher-z of four assigned r values",
        "null": "single bridge permutation applied consistently to all human K/profiles; maximum over assignments and eligible K",
        "permutation_count": N_PERM,
        "seed": SEED,
        "K_scores": k_scores,
        "maximizing_K": winner_k,
        "observed_max_mean_fisher_z": observed_max,
        "observed_max_back_transformed_mean_r": float(np.tanh(observed_max)),
        "search_adjusted_global_p": global_p,
        "null_exceedance_count": int(np.sum(global_null >= observed_max)),
        "family_specific_positive_evidence_count": int(family_df["positive_adjusted_evidence"].sum()),
        "primary_global_pass_p05": bool(global_p <= 0.05),
        "decision_tier": "PENDING_PREDECLARED_ROBUSTNESS",
        "semantic_interpretation_performed": False,
    }
    (OUT / "primary_global_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))
    print(family_df.to_string(index=False))


if __name__ == "__main__":
    main()
