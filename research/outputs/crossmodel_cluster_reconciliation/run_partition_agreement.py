#!/usr/bin/env python3
"""Frozen phase-1/2 cross-model partition agreement analysis.

Uses only opaque role IDs, frozen memberships, and frozen solution diagnostics.
It does not read role names, trait profiles, human data, or SAPA artifacts.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    adjusted_mutual_info_score,
    adjusted_rand_score,
    mutual_info_score,
    normalized_mutual_info_score,
)
from sklearn.metrics.cluster import expected_mutual_information


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "research/outputs/cross_resolution_profile_banks/model"
FIGURES = HERE / "figures"
MODELS = ("qwen", "llama", "gemma")
MODEL_LABELS = {"qwen": "Qwen", "llama": "LLaMA", "gemma": "Gemma"}
MODEL_PAIRS = (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma"))
KS = tuple(range(4, 11))
EXPECTED_ROLES = 275
PERMUTATIONS = 5000
SEED = 2026091303
NEAR_DELTA = 0.02
QUALITY_REFIT_ARI = 0.70
EXPECTED_MEMBERSHIP_HASHES = {
    "qwen": "2c4aee82f6ed7499401e45174b7e354bb4a4e09ff4600536c5534dc48a6a2f0d",
    "llama": "e4e74cd915c3490fd7e4adbddf8bb38e4058dc41e104acf7ab03a8a2285aa86f",
    "gemma": "4df15ca4048a26a7b5ac3c93885baa1f9f0ffe866e2282c83d4c0520cf38d2d1",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entropy(labels: np.ndarray) -> float:
    counts = np.bincount(labels)
    probs = counts[counts > 0] / labels.size
    return float(-(probs * np.log(probs)).sum())


def metrics(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    ha, hb = entropy(a), entropy(b)
    mi = float(mutual_info_score(a, b))
    vi = ha + hb - 2.0 * mi
    return {
        "ami": float(adjusted_mutual_info_score(a, b, average_method="arithmetic")),
        "ari": float(adjusted_rand_score(a, b)),
        "nmi": float(normalized_mutual_info_score(a, b, average_method="arithmetic")),
        "variation_of_information": vi,
        "normalized_vi": vi / math.log(a.size),
    }


def contingency(a: np.ndarray, b: np.ndarray, ka: int, kb: int) -> np.ndarray:
    return np.bincount(a * kb + b, minlength=ka * kb).reshape(ka, kb)


def fast_ami(a: np.ndarray, b: np.ndarray, ka: int, kb: int, emi: float, denominator: float) -> float:
    c = contingency(a, b, ka, kb)
    nz_i, nz_j = np.nonzero(c)
    nij = c[nz_i, nz_j].astype(float)
    ai = c.sum(axis=1).astype(float)
    bj = c.sum(axis=0).astype(float)
    n = float(a.size)
    mi = float(np.sum((nij / n) * np.log((n * nij) / (ai[nz_i] * bj[nz_j]))))
    numerator = mi - emi
    if abs(denominator) < np.finfo(float).eps:
        return 1.0 if abs(numerator) < np.finfo(float).eps else 0.0
    return numerator / denominator


def load_inputs():
    labels: dict[str, dict[int, np.ndarray]] = {m: {} for m in MODELS}
    summaries: dict[str, pd.DataFrame] = {}
    hashes: dict[str, dict[str, str]] = {}
    role_set = None
    role_order = None
    for model in MODELS:
        membership_path = SOURCE / model / "memberships.csv"
        observed_hash = sha256(membership_path)
        if observed_hash != EXPECTED_MEMBERSHIP_HASHES[model]:
            raise RuntimeError(f"Frozen hash mismatch for {membership_path}: {observed_hash}")
        df = pd.read_csv(membership_path)
        if sorted(df["K"].unique().tolist()) != list(KS):
            raise RuntimeError(f"K inventory failure for {model}")
        this_roles = set(df["opaque_role_id"])
        if len(this_roles) != EXPECTED_ROLES:
            raise RuntimeError(f"Role inventory failure for {model}: {len(this_roles)}")
        if role_set is None:
            role_set = this_roles
            role_order = sorted(this_roles)
        elif this_roles != role_set:
            raise RuntimeError(f"Role inventory differs for {model}")
        for k in KS:
            sub = df[df.K == k].copy()
            if len(sub) != EXPECTED_ROLES or sub["opaque_role_id"].duplicated().any():
                raise RuntimeError(f"One-assignment check failed for {model} K={k}")
            mapping = dict(zip(sub.opaque_role_id, sub.profile_id))
            ordered_profiles = [mapping[r] for r in role_order]
            profile_levels = sorted(set(ordered_profiles))
            encode = {profile: i for i, profile in enumerate(profile_levels)}
            encoded = np.array([encode[p] for p in ordered_profiles], dtype=np.int16)
            if len(profile_levels) != k:
                raise RuntimeError(f"Profile count mismatch for {model} K={k}")
            labels[model][k] = encoded
        summary_path = SOURCE / model / "solution_summary.csv"
        summaries[model] = pd.read_csv(summary_path).sort_values("K")
        hashes[model] = {
            "memberships.csv": observed_hash,
            "solution_summary.csv": sha256(summary_path),
            "adjacent_k_continuity.csv": sha256(SOURCE / model / "adjacent_k_continuity.csv"),
        }
    return labels, summaries, role_order, hashes


def pair_key(a: str, b: str) -> str:
    return f"{a}_{b}"


def make_heatmap(frame: pd.DataFrame, a: str, b: str) -> None:
    matrix = frame.pivot(index="K_a", columns="K_b", values="ami").loc[KS, KS]
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    im = ax.imshow(matrix.to_numpy(), origin="lower", cmap="viridis", aspect="equal")
    ax.set_xticks(range(len(KS)), KS)
    ax.set_yticks(range(len(KS)), KS)
    ax.set_xlabel(f"{MODEL_LABELS[b]} K")
    ax.set_ylabel(f"{MODEL_LABELS[a]} K")
    ax.set_title(f"{MODEL_LABELS[a]} × {MODEL_LABELS[b]} adjusted mutual information")
    for i in range(len(KS)):
        for j in range(len(KS)):
            value = matrix.iloc[i, j]
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if value < matrix.to_numpy().mean() else "black")
    fig.colorbar(im, ax=ax, label="AMI")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{pair_key(a,b)}_ami_heatmap.png", dpi=180)
    plt.close(fig)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    labels, summaries, role_order, source_hashes = load_inputs()

    pair_rows = []
    for a, b in MODEL_PAIRS:
        for ka, kb in itertools.product(KS, KS):
            row = {"model_a": a, "model_b": b, "K_a": ka, "K_b": kb}
            row.update(metrics(labels[a][ka], labels[b][kb]))
            pair_rows.append(row)
    pairs = pd.DataFrame(pair_rows)
    pairs["near_best"] = False
    pair_best_summary = []
    for a, b in MODEL_PAIRS:
        mask = (pairs.model_a == a) & (pairs.model_b == b)
        max_ami = float(pairs.loc[mask, "ami"].max())
        pairs.loc[mask, "near_best"] = pairs.loc[mask, "ami"] >= max_ami - NEAR_DELTA - 1e-12
        ranked = pairs.loc[mask].sort_values(
            ["ami", "ari", "nmi", "K_a", "K_b"], ascending=[False, False, False, True, True]
        )
        best = ranked.iloc[0]
        near = pairs.loc[mask & pairs.near_best]
        broad = len(near) >= 4 and near.K_a.nunique() >= 2 and near.K_b.nunique() >= 2
        pair_best_summary.append({
            "model_a": a,
            "model_b": b,
            "best_K_a": int(best.K_a),
            "best_K_b": int(best.K_b),
            "best_ami": float(best.ami),
            "best_ari": float(best.ari),
            "best_nmi": float(best.nmi),
            "near_best_count": int(len(near)),
            "near_best_K_a_values": ";".join(map(str, sorted(near.K_a.unique()))),
            "near_best_K_b_values": ";".join(map(str, sorted(near.K_b.unique()))),
            "broad_ridge": bool(broad),
        })
        make_heatmap(pairs.loc[mask], a, b)
    pairs.to_csv(HERE / "pairwise_k_agreement.csv", index=False)

    pair_lookup = {
        (r.model_a, r.model_b, int(r.K_a), int(r.K_b)): r
        for r in pairs.itertuples(index=False)
    }
    quality = {
        m: {
            int(r.K): {
                "start_ari": float(r.start_ari_median),
                "refit_ari": float(r.subsample_ari_median),
                "small_cluster_warning": bool(r.small_cluster_warning),
                "quality_included": float(r.subsample_ari_median) >= QUALITY_REFIT_ARI,
            }
            for r in summaries[m].itertuples(index=False)
        }
        for m in MODELS
    }
    triple_rows = []
    for kq, kl, kg in itertools.product(KS, KS, KS):
        ql = pair_lookup[("qwen", "llama", kq, kl)]
        qg = pair_lookup[("qwen", "gemma", kq, kg)]
        lg = pair_lookup[("llama", "gemma", kl, kg)]
        amis = [ql.ami, qg.ami, lg.ami]
        triple_rows.append({
            "K_qwen": kq,
            "K_llama": kl,
            "K_gemma": kg,
            "qwen_llama_ami": ql.ami,
            "qwen_gemma_ami": qg.ami,
            "llama_gemma_ami": lg.ami,
            "mean_pairwise_ami": float(np.mean(amis)),
            "minimum_pairwise_ami": float(np.min(amis)),
            "qwen_start_ari": quality["qwen"][kq]["start_ari"],
            "qwen_refit_ari": quality["qwen"][kq]["refit_ari"],
            "qwen_small_cluster_warning": quality["qwen"][kq]["small_cluster_warning"],
            "llama_start_ari": quality["llama"][kl]["start_ari"],
            "llama_refit_ari": quality["llama"][kl]["refit_ari"],
            "llama_small_cluster_warning": quality["llama"][kl]["small_cluster_warning"],
            "gemma_start_ari": quality["gemma"][kg]["start_ari"],
            "gemma_refit_ari": quality["gemma"][kg]["refit_ari"],
            "gemma_small_cluster_warning": quality["gemma"][kg]["small_cluster_warning"],
            "mean_refit_ari": float(np.mean([
                quality["qwen"][kq]["refit_ari"],
                quality["llama"][kl]["refit_ari"],
                quality["gemma"][kg]["refit_ari"],
            ])),
            "quality_constrained": all([
                quality["qwen"][kq]["quality_included"],
                quality["llama"][kl]["quality_included"],
                quality["gemma"][kg]["quality_included"],
            ]),
        })
    triples = pd.DataFrame(triple_rows)
    max_triple = float(triples.mean_pairwise_ami.max())
    triples["near_best"] = triples.mean_pairwise_ami >= max_triple - NEAR_DELTA - 1e-12
    triples = triples.sort_values(
        ["mean_pairwise_ami", "minimum_pairwise_ami", "mean_refit_ari", "K_qwen", "K_llama", "K_gemma"],
        ascending=[False, False, False, True, True, True],
    ).reset_index(drop=True)
    triples.insert(0, "rank", np.arange(1, len(triples) + 1))
    triples.to_csv(HERE / "triple_k_agreement.csv", index=False)
    qtriples = triples[triples.quality_constrained].copy()
    qtriples.to_csv(HERE / "quality_constrained_agreement.csv", index=False)
    observed_best = triples.iloc[0]
    quality_best = qtriples.iloc[0]
    if quality_best.mean_pairwise_ami >= observed_best.mean_pairwise_ami - NEAR_DELTA - 1e-12:
        anchor = quality_best
        anchor_rule = "quality-constrained best lies within 0.02 of global maximum"
    else:
        anchor = observed_best
        anchor_rule = "quality-constrained best falls more than 0.02 below global maximum"

    # Expected-MI terms are fixed by the preserved margins for each K pair.
    ami_constants = {}
    for a, b in MODEL_PAIRS:
        for ka, kb in itertools.product(KS, KS):
            aa, bb = labels[a][ka], labels[b][kb]
            c = contingency(aa, bb, ka, kb)
            emi = float(expected_mutual_information(c, aa.size))
            denominator = 0.5 * (entropy(aa) + entropy(bb)) - emi
            ami_constants[(a, b, ka, kb)] = (emi, denominator)

    rng = np.random.default_rng(SEED)
    null_rows = []
    for draw in range(1, PERMUTATIONS + 1):
        model_permutations = {m: rng.permutation(EXPECTED_ROLES) for m in MODELS}
        permuted = {
            m: {k: labels[m][k][model_permutations[m]] for k in KS}
            for m in MODELS
        }
        matrices = {}
        pair_maxima = {}
        for a, b in MODEL_PAIRS:
            mat = np.empty((len(KS), len(KS)), dtype=float)
            for ia, ka in enumerate(KS):
                for ib, kb in enumerate(KS):
                    emi, denominator = ami_constants[(a, b, ka, kb)]
                    mat[ia, ib] = fast_ami(
                        permuted[a][ka], permuted[b][kb], ka, kb, emi, denominator
                    )
            matrices[(a, b)] = mat
            pair_maxima[pair_key(a, b)] = float(mat.max())
        cube = (
            matrices[("qwen", "llama")][:, :, None]
            + matrices[("qwen", "gemma")][:, None, :]
            + matrices[("llama", "gemma")][None, :, :]
        ) / 3.0
        null_rows.append({
            "permutation": draw,
            "qwen_llama_max_ami": pair_maxima["qwen_llama"],
            "qwen_gemma_max_ami": pair_maxima["qwen_gemma"],
            "llama_gemma_max_ami": pair_maxima["llama_gemma"],
            "triple_max_mean_ami": float(cube.max()),
        })
    null = pd.DataFrame(null_rows)
    null.to_csv(HERE / "permutation_max_null.csv", index=False)

    pair_null_cols = {
        ("qwen", "llama"): "qwen_llama_max_ami",
        ("qwen", "gemma"): "qwen_gemma_max_ami",
        ("llama", "gemma"): "llama_gemma_max_ami",
    }
    for result in pair_best_summary:
        col = pair_null_cols[(result["model_a"], result["model_b"])]
        result["search_adjusted_p"] = float(
            (1 + (null[col] >= result["best_ami"] - 1e-15).sum()) / (PERMUTATIONS + 1)
        )
    triple_p = float(
        (1 + (null.triple_max_mean_ami >= observed_best.mean_pairwise_ami - 1e-15).sum())
        / (PERMUTATIONS + 1)
    )

    near = triples[triples.near_best]
    triple_broad = (
        len(near) >= 5
        and sum(near[c].nunique() >= 2 for c in ["K_qwen", "K_llama", "K_gemma"]) >= 2
    )
    summary = {
        "status": "PARTITION AGREEMENT NUMERICALLY FROZEN; NO ROLE NAMES OR TRAITS USED",
        "model_used": "GPT-5.5",
        "role_count": EXPECTED_ROLES,
        "K_values": list(KS),
        "pairwise_comparison_count": int(len(pairs)),
        "comparisons_per_model_pair": 49,
        "triple_count": int(len(triples)),
        "permutation_count": PERMUTATIONS,
        "permutation_seed": SEED,
        "source_hashes": source_hashes,
        "pairwise_best": pair_best_summary,
        "observed_best_triple": observed_best.to_dict(),
        "quality_best_triple": quality_best.to_dict(),
        "consensus_anchor_triple": {
            "K_qwen": int(anchor.K_qwen),
            "K_llama": int(anchor.K_llama),
            "K_gemma": int(anchor.K_gemma),
            "mean_pairwise_ami": float(anchor.mean_pairwise_ami),
            "rule_triggered": anchor_rule,
        },
        "triple_near_best_count": int(len(near)),
        "triple_broad_ridge": bool(triple_broad),
        "triple_search_adjusted_p": triple_p,
        "quality_threshold_refit_ari": QUALITY_REFIT_ARI,
        "boundary": "Model-only shared-role partition comparison; no human data or semantic matching.",
    }
    (HERE / "partition_agreement_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=False, default=lambda x: x.item() if hasattr(x, "item") else str(x)) + "\n"
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ranked = triples.sort_values("mean_pairwise_ami", ascending=False).reset_index(drop=True)
    ax.plot(np.arange(1, len(ranked) + 1), ranked.mean_pairwise_ami, color="#176B87", lw=2)
    ax.scatter(
        ranked.index[ranked.quality_constrained] + 1,
        ranked.loc[ranked.quality_constrained, "mean_pairwise_ami"],
        s=15, color="#F28E2B", label="All three refit ARI ≥ 0.70", zorder=3,
    )
    ax.axhline(observed_best.mean_pairwise_ami - NEAR_DELTA, color="0.4", ls="--", lw=1, label="Near-best boundary")
    ax.set(xlabel="Ranked K triple", ylabel="Mean pairwise AMI", title="All 343 cross-model resolution triples")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "triple_agreement_ranked.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    ax.hist(null.triple_max_mean_ami, bins=45, color="#9ECAE1", edgecolor="white")
    ax.axvline(observed_best.mean_pairwise_ami, color="#C51B7D", lw=2.5,
               label=f"Observed maximum = {observed_best.mean_pairwise_ami:.3f}")
    ax.set(
        xlabel="Maximum mean AMI after searching 343 triples",
        ylabel="Permutation draws",
        title=f"Search-adjusted null ({PERMUTATIONS:,} preserved-structure permutations)",
    )
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "observed_vs_permutation_max_null.png", dpi=180)
    plt.close(fig)

    print(json.dumps({
        "best_triple": [int(observed_best.K_qwen), int(observed_best.K_llama), int(observed_best.K_gemma)],
        "best_mean_ami": float(observed_best.mean_pairwise_ami),
        "triple_p": triple_p,
        "anchor": [int(anchor.K_qwen), int(anchor.K_llama), int(anchor.K_gemma)],
        "quality_best": [int(quality_best.K_qwen), int(quality_best.K_llama), int(quality_best.K_gemma)],
    }, indent=2))


if __name__ == "__main__":
    main()
