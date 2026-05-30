#!/usr/bin/env python3
"""Trait-space PCA and interpretation tests for Assistant Axis Paper 1.5.

This script intentionally uses local artifacts only. It computes PCA directly
from raw Qwen/Qwen3-32B layer-48 trait activation vectors, compares trait-space
axes to persona-space axes, runs lightweight name-based rubric controls, and
exports paper-facing tables/reports.
"""

from __future__ import annotations

import json
import math
import os
import statistics
import warnings
from collections import Counter
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
warnings.filterwarnings("ignore", category=RuntimeWarning)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import ConvexHull
from scipy.stats import entropy, pearsonr, spearmanr


REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b"
TRAIT_DIR = VECTOR_ROOT / "trait_vectors"
ROLE_DIR = VECTOR_ROOT / "role_vectors"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
PRIOR_DIR = REPO_ROOT / "research/outputs/trait_persona_prediction"
SIMILARITY_PATH = PRIOR_DIR / "persona_trait_similarity_matrix.csv"
COEFFICIENT_PATH = PRIOR_DIR / "pc_trait_predictor_coefficients.csv"
STATS_PATH = PRIOR_DIR / "trait_predicts_persona_pcs_stats.json"
OUTPUT_DIR = REPO_ROOT / "research/outputs/trait_space_interpretation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DIAGNOSTIC_PERSONAS = [
    "assistant",
    "evaluator",
    "auditor",
    "poet",
    "bard",
    "counselor",
    "therapist",
    "spy",
    "demon",
    "warrior",
    "romantic",
    "elder",
    "narrator",
]


def load_vector_dir(vector_dir: Path) -> tuple[list[str], np.ndarray, dict[str, list[int]]]:
    names: list[str] = []
    vectors: list[np.ndarray] = []
    shapes: dict[str, list[int]] = {}
    for path in sorted(vector_dir.glob("*.pt")):
        tensor = torch.load(path, map_location="cpu").float()
        shapes[path.stem] = list(tensor.shape)
        vec = tensor.mean(0) if tensor.dim() > 1 else tensor
        arr = np.nan_to_num(vec.numpy().astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
        names.append(path.stem)
        vectors.append(arr)
    return names, np.stack(vectors), shapes


def normalize_rows(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)


def safe_corr(x: np.ndarray, y: np.ndarray, method: str) -> float | None:
    if np.std(x) == 0 or np.std(y) == 0:
        return None
    if method == "pearson":
        return float(pearsonr(x, y).statistic)
    if method == "spearman":
        return float(spearmanr(x, y).statistic)
    raise ValueError(method)


PERTURBATION_POS = {
    "challenging", "subversive", "rebellious", "disruptive", "provocative",
    "confrontational", "irreverent", "edgy", "transgressive", "combative",
    "critical", "competitive", "skeptical", "contrarian", "risk_taking",
    "bold", "assertive", "aggressive", "chaotic", "mischievous", "cynical",
    "hostile", "blunt", "acerbic", "dominant", "calculating",
}
PERTURBATION_NEG = {
    "supportive", "nurturing", "collaborative", "cooperative", "conciliatory",
    "accommodating", "agreeable", "altruistic", "benevolent", "empathetic",
    "patient", "gentle", "warm", "calm", "deferential", "cautious",
    "protective", "loyal", "responsible", "respectful", "kind", "careful",
}
MORAL_POS = {
    "benevolent", "altruistic", "ethical", "honest", "kind", "supportive",
    "nurturing", "empathetic", "responsible", "loyal", "respectful",
    "principled", "cooperative", "agreeable", "patient", "gentle",
}
MORAL_NEG = {
    "hostile", "callous", "cruel", "deceptive", "manipulative", "cynical",
    "selfish", "arrogant", "aggressive", "bitter", "ruthless", "dishonest",
    "exploitative", "malicious", "combative",
}
PROFESSIONAL_POS = {
    "professional", "analytical", "precise", "conscientious", "disciplined",
    "methodical", "systematic", "efficient", "reliable", "technical",
    "rationalist", "objective", "focused", "organized", "practical",
    "responsible", "careful", "concise",
}
PROFESSIONAL_NEG = {
    "casual", "flippant", "chaotic", "impulsive", "mercurial", "irreverent",
    "playful", "romantic", "poetic", "dreamy", "whimsical", "eclectic",
}
ABSTRACTION_POS = {
    "abstract", "conceptual", "theoretical", "philosophical", "reflective",
    "pensive", "big_picture", "interdisciplinary", "metaphorical", "symbolic",
    "open_ended", "imaginative", "creative", "artistic", "introspective",
    "mystical", "ethereal", "visionary", "speculative", "complex",
}
ABSTRACTION_NEG = {
    "concrete", "practical", "literal", "reactive", "impulsive", "animated",
    "concise", "technical", "grounded", "direct", "simple", "efficient",
    "closure_seeking", "decisive", "routine", "procedural",
}


def rubric_score(name: str, pos: set[str], neg: set[str]) -> float:
    """Return a simple 0-100 trait-name control score."""
    n = name.lower()
    score = 50.0
    for term in pos:
        if term == n or term in n:
            score += 25.0
    for term in neg:
        if term == n or term in n:
            score -= 25.0
    return float(max(0.0, min(100.0, score)))


def pc_rank_rows(names: list[str], coords: np.ndarray) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for pc_idx in range(3):
        scores = coords[:, pc_idx]
        order = np.argsort(scores)[::-1]
        near_zero = np.argsort(np.abs(scores))[:30]
        for rank, i in enumerate(order[:30], start=1):
            rows.append({"pc": f"PC{pc_idx+1}", "side": "positive_top30", "rank": rank, "trait": names[i], "score": scores[i]})
        for rank, i in enumerate(order[-30:][::-1], start=1):
            rows.append({"pc": f"PC{pc_idx+1}", "side": "negative_top30", "rank": rank, "trait": names[i], "score": scores[i]})
        for rank, i in enumerate(near_zero, start=1):
            rows.append({"pc": f"PC{pc_idx+1}", "side": "near_zero_30", "rank": rank, "trait": names[i], "score": scores[i]})
    return rows


def cone_tests(coords: np.ndarray, names: list[str], trait_norm: np.ndarray) -> tuple[dict[str, object], pd.DataFrame]:
    pc1 = coords[:, 0]
    bins = pd.qcut(pc1, q=5, labels=["lowest_pc1", "low_pc1", "mid_pc1", "high_pc1", "highest_pc1"])
    rows = []
    sim = trait_norm @ trait_norm.T
    pc1_bin_labels = np.array([str(x) for x in bins])
    for label in ["lowest_pc1", "low_pc1", "mid_pc1", "high_pc1", "highest_pc1"]:
        idx = np.where(pc1_bin_labels == label)[0]
        xy = coords[idx, 1:3]
        hull_area = None
        if len(idx) >= 3:
            try:
                hull_area = float(ConvexHull(xy).volume)
            except Exception:
                hull_area = None
        radii = np.linalg.norm(xy, axis=1)
        neighbor_entropies = []
        for i in idx:
            order = np.argsort(sim[i])[::-1]
            neighbor_bins = pc1_bin_labels[order[1:11]]
            counts = np.array(list(Counter(neighbor_bins).values()), dtype=float)
            neighbor_entropies.append(float(entropy(counts / counts.sum(), base=2)))
        rows.append({
            "pc1_bin": label,
            "count": int(len(idx)),
            "pc1_min": float(pc1[idx].min()),
            "pc1_max": float(pc1[idx].max()),
            "pc2_variance": float(np.var(coords[idx, 1], ddof=1)),
            "pc3_variance": float(np.var(coords[idx, 2], ddof=1)),
            "pc2_pc3_radial_mean": float(np.mean(radii)),
            "pc2_pc3_radial_iqr": float(np.percentile(radii, 75) - np.percentile(radii, 25)),
            "pc2_pc3_convex_hull_area": hull_area,
            "neighbor_pc1_bin_entropy_mean": float(np.mean(neighbor_entropies)),
        })
    df = pd.DataFrame(rows)
    high = df[df["pc1_bin"] == "highest_pc1"].iloc[0]
    low = df[df["pc1_bin"] == "lowest_pc1"].iloc[0]
    summary = {
        "bin_rows": rows,
        "secondary_variation_expands_as_pc1_decreases": bool(low["pc2_pc3_radial_mean"] > high["pc2_pc3_radial_mean"]),
        "lowest_vs_highest_radial_mean_ratio": float(low["pc2_pc3_radial_mean"] / high["pc2_pc3_radial_mean"]),
        "lowest_vs_highest_hull_area_ratio": (
            None if not high["pc2_pc3_convex_hull_area"] else float(low["pc2_pc3_convex_hull_area"] / high["pc2_pc3_convex_hull_area"])
        ),
    }
    return summary, df


def diagnostic_neighborhoods(sim_path: Path, personas: list[str]) -> pd.DataFrame:
    sim = pd.read_csv(sim_path, index_col=0)
    rows = []
    for persona in personas:
        if persona not in sim.index:
            rows.append({"persona": persona, "rank_type": "missing", "rank": None, "trait": None, "cosine": None})
            continue
        s = sim.loc[persona].sort_values(ascending=False)
        for rank, (trait, val) in enumerate(s.head(15).items(), start=1):
            rows.append({"persona": persona, "rank_type": "nearest_positive", "rank": rank, "trait": trait, "cosine": float(val)})
        for rank, (trait, val) in enumerate(s.tail(10).sort_values().items(), start=1):
            rows.append({"persona": persona, "rank_type": "nearest_negative", "rank": rank, "trait": trait, "cosine": float(val)})
    return pd.DataFrame(rows)


def write_report(
    stats: dict[str, object],
    coords_df: pd.DataFrame,
    rankings_df: pd.DataFrame,
    cone_df: pd.DataFrame,
    diag_df: pd.DataFrame,
) -> None:
    def top(pc: str, side: str, n: int = 10) -> str:
        sub = rankings_df[(rankings_df.pc == pc) & (rankings_df.side == side)].head(n)
        return ", ".join(f"{r.trait} ({r.score:.3f})" for r in sub.itertuples())

    pca_var = stats["trait_pca_explained_variance"]
    pc_compare = stats["persona_trait_pc_direction_cosines"]
    validation = stats["rubric_validation"]
    cone = stats["cone_tests"]
    report = f"""# Trait-Space Axis Interpretation

Model used for analysis scripting: GPT-5.5.

## Data Sources

- Trait vectors: `{TRAIT_DIR}`
- Role vectors for comparison: `{ROLE_DIR}`
- Persona geometry data: `{GEOMETRY_PATH}`
- Prior persona-trait cosine matrix: `{SIMILARITY_PATH}`
- Prior trait predictor coefficients: `{COEFFICIENT_PATH}`

This analysis used raw activation vectors for trait PCA. Each Qwen/Qwen3-32B layer-48 trait tensor has shape `[64, 5120]`; each tensor was mean-pooled to one 5120-D vector before PCA and cosine comparisons. Role vectors were used only as comparison/reference.

## Observed Numerical Results

- Trait count: {stats['trait_count']}
- Persona count for comparison: {stats['persona_count']}
- Trait PC explained variance: PC1={pca_var['pc1']:.3f}, PC2={pca_var['pc2']:.3f}, PC3={pca_var['pc3']:.3f}, cumulative={pca_var['pc1_pc2_pc3']:.3f}.
- Absolute cosine alignment between trait and persona PCA directions: PC1={pc_compare['PC1_abs']:.3f}, PC2={pc_compare['PC2_abs']:.3f}, PC3={pc_compare['PC3_abs']:.3f}.
- Correlation between trait PCA coordinates and prior persona-PC trait coefficients is strongest for: {stats['best_trait_pc_to_persona_loading_match']}.

## Trait PC Rankings

### Trait PC1

Positive: {top('PC1', 'positive_top30')}

Negative: {top('PC1', 'negative_top30')}

Near zero examples: {top('PC1', 'near_zero_30')}

### Trait PC2

Positive: {top('PC2', 'positive_top30')}

Negative: {top('PC2', 'negative_top30')}

Near zero examples: {top('PC2', 'near_zero_30')}

### Trait PC3

Positive: {top('PC3', 'positive_top30')}

Negative: {top('PC3', 'negative_top30')}

Near zero examples: {top('PC3', 'near_zero_30')}

## Streamlined Axis Interpretations

**Trait PC1 interpretation:** The ranking separates formal, serious, calm, conscientious, patient, and methodical traits from flippant, irreverent, goofy, sassy, edgy, witty, entertaining, temperamental, and sardonic traits. A concise paper-ready label is **controlled seriousness / formal composure versus playful irreverence / expressive volatility**. It overlaps moderately with persona PC1 direction in raw activation space, so it should not be treated as a one-to-one copy of the assistant-axis/cone interpretation. It does, however, support the broader claim that trait geometry supplies a strong basis for reconstructing persona placement.

**Trait PC2 interpretation:** The ranking separates callous, detached, technical, dispassionate, esoteric, acerbic, cruel, hostile, savage, and misanthropic traits from nurturing, accessible, empathetic, emotional, benevolent, naive, supportive, meditative, chill, and optimistic traits. A concise paper-ready label is **cold detachment / hard-edged abstraction versus warm accessibility / affiliative care**. The name-based abstraction/integration control correlates with trait PC2 at Pearson {validation['abstraction_vs_pc2']['pearson']:.3f} / Spearman {validation['abstraction_vs_pc2']['spearman']:.3f}. This weakens any simple claim that trait PC2 independently recovers the current persona PC2 abstraction/integration interpretation; PC2 remains the least settled persona-axis interpretation.

**Trait PC3 interpretation:** The ranking separates grounded, practical, understated, accessible, efficient, concise, nonchalant, avoidant, casual, and literal traits from eloquent, bombastic, cryptic, poetic, theatrical, dramatic, philosophical, melodramatic, metaphorical, and esoteric traits. A concise paper-ready label is **plain practical groundedness versus ornate symbolic/theatrical expressivity**. The perturbation/stabilization control correlates with trait PC3 at Pearson {validation['perturbation_vs_pc3']['pearson']:.3f} / Spearman {validation['perturbation_vs_pc3']['spearman']:.3f}, while moral valence correlates at Pearson {validation['moral_valence_vs_pc3']['pearson']:.3f} / Spearman {validation['moral_valence_vs_pc3']['spearman']:.3f}. Trait PC3 therefore does not independently validate a clean perturbation-stabilization axis by itself, even though the prior persona-PC3 prediction subset favored perturbation/stabilization over moral valence.

## Comparison To Persona-Space Interpretations

- Persona PC1: careful evaluative/procedural certainty versus open symbolic possibility. Trait space shares only partial directional alignment with this axis, but the trait bank reconstructs persona PC1 almost perfectly through the persona-trait similarity profile.
- Persona PC2: abstraction/integration versus developmental/reactive immediacy. Trait PC2 does not cleanly resolve this interpretation; the observed trait ranking is more strongly about cold detachment versus affiliative warmth.
- Persona PC3: perturbative/interventionist versus stabilizing/nurturing. Trait PC3 is not reducible to this framing; direct trait PC3 is more lexical/register-like, contrasting plain grounded practicality with ornate symbolic/theatrical expressivity.

## Cone / Constraint Tests

The trait-space cone test bins traits by trait PC1 and measures secondary spread in PC2/PC3.

- Lowest-PC1 vs highest-PC1 radial spread ratio: {cone['lowest_vs_highest_radial_mean_ratio']:.3f}
- Lowest-PC1 vs highest-PC1 convex hull area ratio: {cone['lowest_vs_highest_hull_area_ratio']}
- Secondary variation expands as PC1 decreases: {cone['secondary_variation_expands_as_pc1_decreases']}

The trait-space result is therefore {'consistent with' if cone['secondary_variation_expands_as_pc1_decreases'] else 'not consistent with'} the same simple cone/constraint pattern observed in persona space. See `trait_space_cone_tests.json` and `trait_space_cone_plots.png` for bin-level values.

## Diagnostic Trait Neighborhoods

Diagnostic persona neighborhoods were read from the prior persona-trait cosine matrix, not recomputed. The exported table includes nearest positive and negative trait profiles for assistant, evaluator, auditor, poet, bard, counselor, therapist, spy, demon, warrior, romantic, elder, and narrator.

## Interpretations

Trait-space analysis strengthens the layered interpretation in one specific sense: raw trait vectors occupy the same activation space and provide a highly predictive coordinate basis for persona PCA placement. It does not prove that the paper-ready persona axes are simply trait axes. Direct trait-only PCA partially reorganizes the structure, especially for PC2 and PC3.

## Hypotheses

- Trait vectors may act as a dense local basis for role/persona geometry rather than as independent psychological dimensions.
- Persona axes may emerge from interactions among trait-like, procedural, semantic, and lexical/register structure rather than any single source.
- PC2 likely needs a narrower validation design; trait-only PCA does not settle it.

## Unknowns / Limitations

- The rubric tests in this report are trait-name controls, not independent human or model annotation.
- PCA signs are conventional; interpretation uses rankings and absolute directional comparisons.
- Same-space near-ceiling reconstruction can reflect shared vector provenance and high-dimensional basis coverage.
- Trait PC axes are not guaranteed to align with persona PC axes because PCA was fit on a different point cloud.

## Recommended Next Experiment

Run a reduced, preregistered trait taxonomy test: choose a small non-overlapping set of perturbation/stabilization, moral-valence, abstraction/integration, and professionalism traits before looking at coefficients, then test which subsets predict held-out persona PC directions and within-cluster rankings.
"""
    (OUTPUT_DIR / "trait_space_axis_report.md").write_text(report)


def main() -> None:
    trait_names, trait_vecs, trait_shapes = load_vector_dir(TRAIT_DIR)
    role_names, role_vecs, role_shapes = load_vector_dir(ROLE_DIR)
    trait_norm = normalize_rows(trait_vecs)
    role_norm = normalize_rows(role_vecs)

    trait_pca = PCA(n_components=3, random_state=42)
    trait_coords = trait_pca.fit_transform(trait_vecs)
    role_pca = PCA(n_components=3, random_state=42)
    role_coords = role_pca.fit_transform(role_vecs)

    coords_df = pd.DataFrame({
        "trait": trait_names,
        "trait_pc1": trait_coords[:, 0],
        "trait_pc2": trait_coords[:, 1],
        "trait_pc3": trait_coords[:, 2],
        "perturbation_stabilization_score": [rubric_score(n, PERTURBATION_POS, PERTURBATION_NEG) for n in trait_names],
        "moral_valence_score": [rubric_score(n, MORAL_POS, MORAL_NEG) for n in trait_names],
        "professionalism_score": [rubric_score(n, PROFESSIONAL_POS, PROFESSIONAL_NEG) for n in trait_names],
        "abstraction_integration_score": [rubric_score(n, ABSTRACTION_POS, ABSTRACTION_NEG) for n in trait_names],
    })
    coords_df.to_csv(OUTPUT_DIR / "trait_space_pca_coordinates.csv", index=False)

    rankings_df = pd.DataFrame(pc_rank_rows(trait_names, trait_coords))
    rankings_df.to_csv(OUTPUT_DIR / "trait_space_pc_rankings.csv", index=False)

    # Direction comparison between PCA bases in the same 5120-D activation space.
    direction_stats = {}
    for i in range(3):
        signed = float(np.dot(trait_pca.components_[i], role_pca.components_[i]))
        direction_stats[f"PC{i+1}_signed"] = signed
        direction_stats[f"PC{i+1}_abs"] = abs(signed)

    # Correlate trait-only PCA coordinates with prior trait coefficients used to predict persona PCs.
    coeff = pd.read_csv(COEFFICIENT_PATH)
    coeff_wide = coeff.pivot(index="trait", columns="pc", values="ridge_standardized_coefficient")
    merged = coords_df.set_index("trait").join(coeff_wide, how="inner")
    loading_corrs = {}
    best_match = None
    best_abs = -1.0
    for tpc in ["trait_pc1", "trait_pc2", "trait_pc3"]:
        for ppc in ["PC1", "PC2", "PC3"]:
            val = safe_corr(merged[tpc].to_numpy(), merged[ppc].to_numpy(), "pearson")
            loading_corrs[f"{tpc}_vs_persona_{ppc}_coefficient_pearson"] = val
            if val is not None and abs(val) > best_abs:
                best_abs = abs(val)
                best_match = f"{tpc} vs persona {ppc} coefficient, Pearson={val:.3f}"

    validation = {
        "perturbation_vs_pc3": {
            "pearson": safe_corr(coords_df["perturbation_stabilization_score"].to_numpy(), coords_df["trait_pc3"].to_numpy(), "pearson"),
            "spearman": safe_corr(coords_df["perturbation_stabilization_score"].to_numpy(), coords_df["trait_pc3"].to_numpy(), "spearman"),
        },
        "moral_valence_vs_pc3": {
            "pearson": safe_corr(coords_df["moral_valence_score"].to_numpy(), coords_df["trait_pc3"].to_numpy(), "pearson"),
            "spearman": safe_corr(coords_df["moral_valence_score"].to_numpy(), coords_df["trait_pc3"].to_numpy(), "spearman"),
        },
        "professionalism_vs_pc3": {
            "pearson": safe_corr(coords_df["professionalism_score"].to_numpy(), coords_df["trait_pc3"].to_numpy(), "pearson"),
            "spearman": safe_corr(coords_df["professionalism_score"].to_numpy(), coords_df["trait_pc3"].to_numpy(), "spearman"),
        },
        "abstraction_vs_pc2": {
            "pearson": safe_corr(coords_df["abstraction_integration_score"].to_numpy(), coords_df["trait_pc2"].to_numpy(), "pearson"),
            "spearman": safe_corr(coords_df["abstraction_integration_score"].to_numpy(), coords_df["trait_pc2"].to_numpy(), "spearman"),
        },
    }

    cone_summary, cone_df = cone_tests(trait_coords, trait_names, trait_norm)
    (OUTPUT_DIR / "trait_space_cone_tests.json").write_text(json.dumps(cone_summary, indent=2))

    diag_df = diagnostic_neighborhoods(SIMILARITY_PATH, DIAGNOSTIC_PERSONAS)
    diag_df.to_csv(OUTPUT_DIR / "diagnostic_trait_neighborhoods.csv", index=False)

    stats = {
        "model_used": "GPT-5.5",
        "source_model": "Qwen/Qwen3-32B",
        "layer": 48,
        "analysis_used_raw_activation_vectors": True,
        "trait_vector_path": str(TRAIT_DIR),
        "role_vector_path": str(ROLE_DIR),
        "geometry_data_path": str(GEOMETRY_PATH),
        "prior_outputs": [str(SIMILARITY_PATH), str(COEFFICIENT_PATH), str(STATS_PATH)],
        "trait_count": len(trait_names),
        "persona_count": len(role_names),
        "trait_tensor_shape_counts": {str(k): v for k, v in Counter(tuple(x) for x in trait_shapes.values()).items()},
        "role_tensor_shape_counts": {str(k): v for k, v in Counter(tuple(x) for x in role_shapes.values()).items()},
        "mean_pooled_vector_dim": int(trait_vecs.shape[1]),
        "vectors_normalized_for_cosine": True,
        "pca_fit_on_raw_mean_pooled_vectors": True,
        "trait_pca_explained_variance": {
            "pc1": float(trait_pca.explained_variance_ratio_[0]),
            "pc2": float(trait_pca.explained_variance_ratio_[1]),
            "pc3": float(trait_pca.explained_variance_ratio_[2]),
            "pc1_pc2_pc3": float(sum(trait_pca.explained_variance_ratio_[:3])),
        },
        "persona_pca_explained_variance_recomputed": {
            "pc1": float(role_pca.explained_variance_ratio_[0]),
            "pc2": float(role_pca.explained_variance_ratio_[1]),
            "pc3": float(role_pca.explained_variance_ratio_[2]),
        },
        "persona_trait_pc_direction_cosines": direction_stats,
        "trait_pc_to_persona_pc_coefficient_correlations": loading_corrs,
        "best_trait_pc_to_persona_loading_match": best_match,
        "rubric_validation": validation,
        "rubric_limitation": "Rubric scores are deterministic trait-name controls, not independent annotation of trait descriptions.",
        "cone_tests": cone_summary,
    }
    (OUTPUT_DIR / "trait_space_validation_stats.json").write_text(json.dumps(stats, indent=2))

    write_report(stats, coords_df, rankings_df, cone_df, diag_df)

    # Plots.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for idx, ax in enumerate(axes):
        ax.scatter(trait_coords[:, idx], np.zeros(len(trait_names)), s=18, alpha=0.65)
        ax.set_title(f"Trait PC{idx+1} coordinate distribution")
        ax.set_yticks([])
        ax.set_xlabel(f"PC{idx+1}")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "trait_space_pc_plots.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(trait_coords[:, 0], trait_coords[:, 1], c=np.linalg.norm(trait_coords[:, 1:3], axis=1), cmap="viridis", s=35)
    ax.set_xlabel("Trait PC1")
    ax.set_ylabel("Trait PC2")
    ax.set_title("Trait-space secondary spread across PC1")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "trait_space_cone_plots.png", dpi=160)
    plt.close(fig)

    print(json.dumps({
        "output_dir": str(OUTPUT_DIR),
        "trait_count": len(trait_names),
        "persona_count": len(role_names),
        "trait_pca_explained_variance": stats["trait_pca_explained_variance"],
        "pc_direction_cosines": direction_stats,
        "cone_expands": cone_summary["secondary_variation_expands_as_pc1_decreases"],
    }, indent=2))


if __name__ == "__main__":
    main()
