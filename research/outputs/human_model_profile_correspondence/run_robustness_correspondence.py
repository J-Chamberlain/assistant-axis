#!/usr/bin/env python3
"""Run preregistered robustness and post-primary descriptive analyses."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ELIGIBLE_K = [4, 5, 6, 7, 8, 10]
STABLE_K = [4, 5, 6]
FAMILIES = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
N_PERM = 20_000
SEED_12 = 2_026_091_312
SEED_45 = 2_026_091_304
CLIP = 0.999999999999


def row_normalize(x: np.ndarray) -> np.ndarray:
    centered = x - x.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(centered, axis=1, keepdims=True)
    if np.any(norm <= 0) or not np.isfinite(norm).all():
        raise ValueError("Constant or nonfinite profile")
    return centered / norm


def corr_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return row_normalize(a) @ row_normalize(b).T


def spearman_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return corr_rows(np.apply_along_axis(rankdata, 1, a), np.apply_along_axis(rankdata, 1, b))


def assign(corr_family_by_human: np.ndarray) -> tuple[list[tuple[int, int]], float]:
    penalty = np.arange(corr_family_by_human.shape[0])[:, None] * 1e-15 + np.arange(corr_family_by_human.shape[1])[None, :] * 1e-13
    human_rows, family_cols = linear_sum_assignment(-corr_family_by_human.T + penalty.T)
    pairs = sorted((int(f), int(h)) for h, f in zip(human_rows, family_cols))
    if len(pairs) != 4 or len({h for _, h in pairs}) != 4:
        raise ValueError("Noninjective assignment")
    rs = np.array([corr_family_by_human[f, h] for f, h in pairs])
    return pairs, float(np.arctanh(np.clip(rs, -CLIP, CLIP)).mean())


def load_space(trait_count: int) -> tuple[list[str], dict[int, dict], pd.DataFrame, np.ndarray]:
    human = pd.read_csv(OUT / f"human_trait_profiles_{trait_count}.csv")
    model = pd.read_csv(OUT / f"model_family_trait_profiles_{trait_count}.csv")
    traits = sorted(human["trait"].unique())
    if len(traits) != trait_count:
        raise ValueError(f"Expected {trait_count} traits")
    by_k = {}
    for k in range(4, 11):
        d = human.loc[human["K"].eq(k)]
        ids = sorted(d["profile_id"].unique())
        x = d.pivot(index="profile_id", columns="trait", values="human_trait_value").loc[ids, traits].to_numpy(float)
        by_k[k] = {"profiles": ids, "raw": x, "norm": row_normalize(x)}
    model_primary = model.loc[model["family_id"].isin(FAMILIES)]
    m = model_primary.pivot(index="family_id", columns="trait", values="three_model_consensus_value").loc[FAMILIES, traits].to_numpy(float)
    return traits, by_k, model, m


def run_12_trait() -> dict:
    traits, by_k, _, model_raw = load_space(12)
    model_norm = row_normalize(model_raw)
    sim_rows, assignment_rows = [], []
    observed, family_candidates = {}, defaultdict(list)
    for k in ELIGIBLE_K:
        corr = by_k[k]["norm"] @ model_norm.T
        rho = spearman_rows(by_k[k]["raw"], model_raw)
        for h, profile in enumerate(by_k[k]["profiles"]):
            for f, family in enumerate(FAMILIES):
                sim_rows.append(
                    {"trait_set": "12_HUMAN_SUPPORTED", "K": k, "human_profile_id": profile, "model_family_id": family,
                     "pearson_r": corr[h, f], "spearman_rho": rho[h, f]}
                )
                family_candidates[family].append((corr[h, f], rho[h, f], k, profile))
        pairs, score = assign(corr.T)
        for f, h in pairs:
            assignment_rows.append(
                {"trait_set": "12_HUMAN_SUPPORTED", "K": k, "model_family_id": FAMILIES[f],
                 "human_profile_id": by_k[k]["profiles"][h], "pearson_r": corr[h, f], "spearman_rho": rho[h, f],
                 "fisher_z": np.arctanh(np.clip(corr[h, f], -CLIP, CLIP)), "mean_fisher_z_for_K": score,
                 "back_transformed_mean_r_for_K": np.tanh(score)}
            )
        observed[k] = score
    winner = max(ELIGIBLE_K, key=lambda k: (observed[k], -k))

    rng = np.random.default_rng(SEED_12)
    global_null = np.empty(N_PERM)
    family_null = {f: np.empty(N_PERM) for f in FAMILIES}
    null_rows = []
    for draw in range(N_PERM):
        perm = rng.permutation(12)
        scores, fmax = {}, np.full(4, -np.inf)
        for k in ELIGIBLE_K:
            corr = by_k[k]["norm"][:, perm] @ model_norm.T
            _, scores[k] = assign(corr.T)
            fmax = np.maximum(fmax, corr.max(axis=0))
        wk = max(ELIGIBLE_K, key=lambda k: (scores[k], -k))
        global_null[draw] = scores[wk]
        for i, f in enumerate(FAMILIES):
            family_null[f][draw] = fmax[i]
        null_rows.append(
            {"permutation_index": draw + 1, "seed": SEED_12, "global_max_fisher_z": scores[wk],
             "global_max_back_transformed_r": np.tanh(scores[wk]), "global_maximizing_K": wk,
             **{f"{f}_max_r": fmax[i] for i, f in enumerate(FAMILIES)}}
        )

    family_rows = []
    for family in FAMILIES:
        r, rho, k, profile = max(family_candidates[family], key=lambda x: (x[0], -x[2], x[3]))
        p = (1 + np.sum(family_null[family] >= r)) / (N_PERM + 1)
        family_rows.append(
            {"trait_set": "12_HUMAN_SUPPORTED", "model_family_id": family, "best_K": k, "best_human_profile": profile,
             "best_pearson_r": r, "best_spearman_rho": rho, "family_specific_search_adjusted_p": p,
             "positive_adjusted_evidence": bool(r > 0 and p <= .05)}
        )
    pd.DataFrame(sim_rows).sort_values(["K", "human_profile_id", "model_family_id"]).to_csv(OUT / "profile_similarity_12.csv", index=False, float_format="%.12g")
    pd.DataFrame(assignment_rows).sort_values(["K", "model_family_id"]).to_csv(OUT / "primary_assignments_12_by_k.csv", index=False, float_format="%.12g")
    pd.DataFrame(null_rows).to_csv(OUT / "bridge_permutation_null_12.csv", index=False, float_format="%.12g")
    pd.DataFrame(family_rows).to_csv(OUT / "family_specific_results_12.csv", index=False, float_format="%.12g")
    obs = observed[winner]
    return {
        "best_K": winner, "mean_fisher_z": obs, "back_transformed_mean_r": float(np.tanh(obs)),
        "search_adjusted_p": float((1 + np.sum(global_null >= obs)) / (N_PERM + 1)),
        "null_exceedance_count": int(np.sum(global_null >= obs)), "permutation_count": N_PERM, "seed": SEED_12,
    }


def stable_k_sensitivity(primary: dict) -> dict:
    k_scores = {int(x["K"]): x for x in primary["K_scores"]}
    winner = max(STABLE_K, key=lambda k: (k_scores[k]["mean_fisher_z"], -k))
    observed = k_scores[winner]["mean_fisher_z"]
    null = pd.read_csv(OUT / "bridge_permutation_null_45.csv")
    p = float((1 + (null["stable_K456_max_fisher_z"] >= observed).sum()) / (len(null) + 1))
    rows = []
    for k in STABLE_K:
        rows.append(
            {"row_type": "K_score", "K": k, "mean_fisher_z": k_scores[k]["mean_fisher_z"],
             "back_transformed_mean_r": k_scores[k]["back_transformed_mean_r"], "is_stable_subset_max": k == winner,
             "search_adjusted_p": p if k == winner else np.nan, "permutation_count": len(null), "seed": SEED_45}
        )
    pd.DataFrame(rows).to_csv(OUT / "human_stability_sensitivity.csv", index=False, float_format="%.12g")
    return {"best_K": winner, "mean_fisher_z": observed, "back_transformed_mean_r": float(np.tanh(observed)), "search_adjusted_p": p}


def k9_diagnostic() -> tuple[pd.DataFrame, dict]:
    _, by_k, _, model_raw = load_space(45)
    corr = corr_rows(by_k[9]["raw"], model_raw)
    rho = spearman_rows(by_k[9]["raw"], model_raw)
    pairs, score = assign(corr.T)
    rows = []
    for f, h in pairs:
        rows.append(
            {"status": "DIAGNOSTIC / INELIGIBLE", "K": 9, "model_family_id": FAMILIES[f],
             "human_profile_id": by_k[9]["profiles"][h], "pearson_r": corr[h, f], "spearman_rho": rho[h, f],
             "mean_fisher_z": score, "back_transformed_mean_r": np.tanh(score), "included_in_primary": False}
        )
    out = pd.DataFrame(rows).sort_values("model_family_id")
    out.to_csv(OUT / "k9_diagnostic.csv", index=False, float_format="%.12g")
    return out, {"mean_fisher_z": score, "back_transformed_mean_r": float(np.tanh(score))}


def model_replication() -> pd.DataFrame:
    human = pd.read_csv(OUT / "human_trait_profiles_45.csv")
    model = pd.read_csv(OUT / "model_family_trait_profiles_45.csv")
    selected = pd.read_csv(OUT / "primary_assignments_by_k.csv")
    primary = json.loads((OUT / "primary_global_result.json").read_text())
    k = int(primary["maximizing_K"])
    selected = selected.loc[selected["K"].eq(k)]
    traits = sorted(human["trait"].unique())
    rows = []
    for _, pair in selected.iterrows():
        family, profile = pair["model_family_id"], pair["human_profile_id"]
        h = human.loc[(human["K"].eq(k)) & human["profile_id"].eq(profile)].set_index("trait").loc[traits, "human_trait_value"].to_numpy(float)[None, :]
        mrow = model.loc[model["family_id"].eq(family)].set_index("trait").loc[traits]
        vectors = {
            "three_model_consensus": mrow["three_model_consensus_value"].to_numpy(float),
            "qwen": mrow["qwen_value"].to_numpy(float), "llama": mrow["llama_value"].to_numpy(float), "gemma": mrow["gemma_value"].to_numpy(float),
            "leave_out_gemma_qwen_llama": mrow[["qwen_value", "llama_value"]].mean(axis=1).to_numpy(float),
            "leave_out_llama_qwen_gemma": mrow[["qwen_value", "gemma_value"]].mean(axis=1).to_numpy(float),
            "leave_out_qwen_llama_gemma": mrow[["llama_value", "gemma_value"]].mean(axis=1).to_numpy(float),
        }
        model_rs = []
        for representation, vec in vectors.items():
            r = float(corr_rows(h, vec[None, :])[0, 0]); rho = float(spearman_rows(h, vec[None, :])[0, 0])
            rows.append({"K": k, "model_family_id": family, "human_profile_id": profile, "representation": representation,
                         "pearson_r": r, "spearman_rho": rho, "pair_fixed_no_reassignment": True})
            if representation in {"qwen", "llama", "gemma"}: model_rs.append(r)
        rows.append({"K": k, "model_family_id": family, "human_profile_id": profile, "representation": "model_specific_range_summary",
                     "pearson_r": max(model_rs)-min(model_rs), "spearman_rho": np.nan,
                     "pair_fixed_no_reassignment": True, "all_model_signs_agree": len({np.sign(x) for x in model_rs}) == 1,
                     "minimum_model_r": min(model_rs), "maximum_model_r": max(model_rs)})
    out = pd.DataFrame(rows).sort_values(["model_family_id", "representation"])
    out.to_csv(OUT / "model_specific_replication.csv", index=False, float_format="%.12g")
    return out


def e_secondary() -> dict:
    traits, by_k, model, _ = load_space(45)
    e = model.loc[model["family_id"].eq("MFamily_E")].set_index("trait").loc[traits]
    e_raw = e["three_model_consensus_value"].to_numpy(float)[None, :]
    e_norm = row_normalize(e_raw)
    rows, candidates = [], []
    for k in range(4, 11):
        r = (by_k[k]["norm"] @ e_norm.T)[:, 0]
        rho = spearman_rows(by_k[k]["raw"], e_raw)[:, 0]
        for i, profile in enumerate(by_k[k]["profiles"]):
            rows.append({"K": k, "eligible_primary_K": k in ELIGIBLE_K, "human_profile_id": profile,
                         "pearson_r": r[i], "spearman_rho": rho[i]})
            if k in ELIGIBLE_K: candidates.append((r[i], rho[i], k, profile))
    best_r, best_rho, best_k, best_profile = max(candidates, key=lambda x: (x[0], -x[2], x[3]))
    rng = np.random.default_rng(SEED_45)
    null = np.empty(N_PERM)
    for draw in range(N_PERM):
        perm = rng.permutation(45)
        null[draw] = max(float((by_k[k]["norm"][:, perm] @ e_norm.T).max()) for k in ELIGIBLE_K)
    p = float((1 + np.sum(null >= best_r)) / (N_PERM + 1))
    status = "ADJUSTED EVIDENCE" if best_r > 0 and p <= .05 else ("SUGGESTIVE" if best_r > 0 and p <= .10 else "NO DETECTABLE ADJUSTED COUNTERPART")
    out = pd.DataFrame(rows)
    out["is_best_eligible"] = out["eligible_primary_K"] & out["K"].eq(best_k) & out["human_profile_id"].eq(best_profile)
    out["family_specific_search_adjusted_p"] = np.where(out["is_best_eligible"], p, np.nan)
    out["secondary_status"] = status
    out["excluded_from_primary_A_D_global"] = True
    out.sort_values(["K", "human_profile_id"]).to_csv(OUT / "mfamily_e_secondary.csv", index=False, float_format="%.12g")
    return {"best_K": best_k, "best_human_profile": best_profile, "pearson_r": float(best_r), "spearman_rho": float(best_rho),
            "search_adjusted_p": p, "null_exceedance_count": int(np.sum(null >= best_r)), "status": status}


def relaxed_and_persistence(k9: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sim = pd.read_csv(OUT / "profile_similarity_45.csv")
    family_results = pd.read_csv(OUT / "family_specific_results.csv").set_index("model_family_id")
    relaxed = []
    for (k, profile), g in sim.groupby(["K", "human_profile_id"], sort=True):
        g = g.sort_values(["pearson_r", "model_family_id"], ascending=[False, True])
        first, second = g.iloc[0], g.iloc[1]
        p = family_results.loc[first["model_family_id"], "family_specific_search_adjusted_p"]
        relaxed.append({"K": k, "human_profile_id": profile, "best_model_family": first["model_family_id"],
                        "best_pearson_r": first["pearson_r"], "best_spearman_rho": first["spearman_rho"],
                        "second_best_model_family": second["model_family_id"], "second_best_pearson_r": second["pearson_r"],
                        "top_two_margin": first["pearson_r"]-second["pearson_r"], "ambiguous_margin_le_0_10": first["pearson_r"]-second["pearson_r"] <= .10,
                        "family_specific_adjusted_p_for_best_family": p,
                        "descriptively_unmatched": bool(first["pearson_r"] <= 0 or p > .05)})
    relaxed_df = pd.DataFrame(relaxed).sort_values(["K", "human_profile_id"])
    relaxed_df.to_csv(OUT / "relaxed_split_merge_browsing.csv", index=False, float_format="%.12g")

    # Add K=9 similarities for lineage descriptions only.
    traits, by_k, _, model_raw = load_space(45)
    c9 = corr_rows(by_k[9]["raw"], model_raw); r9 = spearman_rows(by_k[9]["raw"], model_raw)
    best9 = {}
    for h, profile in enumerate(by_k[9]["profiles"]):
        order = sorted(range(4), key=lambda f: (-c9[h, f], FAMILIES[f]))
        best9[profile] = (FAMILIES[order[0]], c9[h, order[0]], r9[h, order[0]])
    best = {(int(r.K), r.human_profile_id): (r.best_model_family, r.best_pearson_r, r.best_spearman_rho) for r in relaxed_df.itertuples()}
    best.update({(9, p): v for p, v in best9.items()})

    adjacency = pd.read_csv(ROOT / "research/outputs/cross_resolution_profile_banks/human/human_adjacent_k_continuity.csv")
    edges = adjacency.loc[adjacency["mutual_nearest"].astype(str).str.lower().eq("true")]
    graph = defaultdict(set)
    for r in edges.itertuples():
        a=(int(r.lower_K),r.lower_profile_id); b=(int(r.higher_K),r.higher_profile_id); graph[a].add(b); graph[b].add(a)
    summary = pd.read_csv(ROOT / "research/outputs/cross_resolution_profile_banks/human/human_cross_resolution_solution_summary.csv").set_index("K")
    primary = json.loads((OUT / "primary_global_result.json").read_text())
    selected = pd.read_csv(OUT / "primary_assignments_by_k.csv")
    winner = int(primary["maximizing_K"])
    selected_winner = selected.loc[selected["K"].eq(winner)]
    assignment_lookup = {(int(r.K),r.human_profile_id):r.model_family_id for r in selected.itertuples()}
    rows=[]
    for pair in selected_winner.itertuples():
        start=(winner,pair.human_profile_id); seen={start}; q=deque([start])
        while q:
            node=q.popleft()
            for nxt in graph[node]:
                if nxt not in seen: seen.add(nxt); q.append(nxt)
        lineage_id=f"{pair.model_family_id}_from_{pair.human_profile_id}"
        for k, profile in sorted(seen):
            fam,r,rho=best[(k,profile)]
            rows.append({"human_profile_lineage":lineage_id,"origin_model_family":pair.model_family_id,"origin_K":winner,
                         "K":k,"human_profile_id":profile,"eligible_primary_K":k in ELIGIBLE_K,"best_model_family":fam,
                         "best_pearson_r":r,"best_spearman_rho":rho,"origin_family_retained":fam==pair.model_family_id,
                         "assignment_status":("primary_assigned_to_origin" if assignment_lookup.get((k,profile))==pair.model_family_id else
                                              "primary_assigned_other_family" if (k,profile) in assignment_lookup else
                                              "diagnostic_ineligible" if k==9 else "unassigned_human_profile"),
                         "human_split_refit_stability_rating":summary.loc[k,"split_refit_stability_rating"],
                         "human_response_style_warning":summary.loc[k,"strong_response_style_warning"],
                         "mutual_nearest_lineage_rule":True})
    persistence=pd.DataFrame(rows).drop_duplicates().sort_values(["origin_model_family","K","human_profile_id"])
    persistence.to_csv(OUT / "cross_resolution_human_persistence.csv",index=False,float_format="%.12g")
    return relaxed_df,persistence


def main() -> None:
    primary = json.loads((OUT / "primary_global_result.json").read_text())
    result12 = run_12_trait()
    stable = stable_k_sensitivity(primary)
    k9_df, k9 = k9_diagnostic()
    replication = model_replication()
    e = e_secondary()
    relaxed, persistence = relaxed_and_persistence(k9_df)

    selected45 = pd.read_csv(OUT / "primary_assignments_by_k.csv")
    selected45 = selected45.loc[selected45["K"].eq(primary["maximizing_K"])]
    sim12 = pd.read_csv(OUT / "profile_similarity_12.csv")
    same_pair_12 = selected45[["K","model_family_id","human_profile_id"]].merge(sim12,on=["K","model_family_id","human_profile_id"],validate="one_to_one")
    positive_same_pairs_12 = int((same_pair_12["pearson_r"] > 0).sum())
    family45 = pd.read_csv(OUT / "family_specific_results.csv")
    family_evidence_count = int(family45["positive_adjusted_evidence"].astype(str).str.lower().eq("true").sum())
    primary_r = float(primary["observed_max_back_transformed_mean_r"])
    criteria = {
        "primary_global_p_le_0_05": bool(primary["search_adjusted_global_p"] <= .05),
        "at_least_3_of_4_family_specific_positive_adjusted": family_evidence_count >= 3,
        "twelve_trait_directionally_concordant": bool(result12["back_transformed_mean_r"] > 0 and positive_same_pairs_12 >= 3),
        "stable_K456_recognizable": bool(stable["search_adjusted_p"] <= .05 and stable["back_transformed_mean_r"] >= .8 * primary_r),
    }
    if not criteria["primary_global_p_le_0_05"]:
        tier="WEAK / ABSENT AGGREGATE CORRESPONDENCE"
    elif all(criteria.values()):
        tier="STRONG AGGREGATE CORRESPONDENCE"
    else:
        tier="MODERATE / PARTIAL AGGREGATE CORRESPONDENCE"
    response_style = pd.DataFrame([{
        "status":"NOT_RUN_NO_FROZEN_TRANSFORM","separate_corrected_statistic":False,
        "primary_item_baseline_handling":"observed-item marginal z scores",
        "primary_profile_level_handling":"Pearson removes profile-wide additive elevation",
        "remaining_caveat":"material frozen response-style predictability may still affect relative trait shape",
        "frozen_item_centered_between_profile_variance_fraction_range":"0.965-0.990"
    }])
    response_style.to_csv(OUT/"response_style_sensitivity.csv",index=False)
    result={
        "analysis":"preregistered_robustness_and_secondary_results","date":"2026-09-13","model_used":"GPT-5.5",
        "twelve_trait":result12,"human_stability_K456":stable,"k9_diagnostic_ineligible":k9,"mfamily_e_secondary":e,
        "primary_45_selected_pairs_positive_on_12":positive_same_pairs_12,"family_45_adjusted_evidence_count":family_evidence_count,
        "decision_criteria":criteria,"final_decision_tier":tier,
        "response_style_sensitivity":"NOT_RUN_NO_FROZEN_TRANSFORM",
        "persistence_rows":len(persistence),"relaxed_browsing_rows":len(relaxed),
        "semantic_interpretation_performed":False,
    }
    (OUT/"robustness_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2))
    print("\n12-trait maximizing assignment")
    a12=pd.read_csv(OUT/"primary_assignments_12_by_k.csv"); print(a12.loc[a12.K.eq(result12['best_K'])].to_string(index=False))
    print("\nModel replication")
    print(replication.loc[replication.representation.isin(['three_model_consensus','qwen','llama','gemma'])].to_string(index=False))


if __name__ == "__main__":
    main()
