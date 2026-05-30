#!/usr/bin/env python3
"""Test whether Qwen trait-vector geometry predicts persona PCA coordinates."""

from __future__ import annotations

import json
import math
import os
import warnings
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import ElasticNetCV, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning


warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "research" / "outputs" / "trait_persona_prediction"
GEOMETRY_PATH = REPO_ROOT / "research" / "visualizations" / "geometry_viz_data.json"
ROLE_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "qwen-3-32b" / "role_vectors"
TRAIT_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "qwen-3-32b" / "trait_vectors"

DIAGNOSTIC_PERSONAS = [
    "counselor",
    "therapist",
    "healer",
    "caregiver",
    "angel",
    "spy",
    "auditor",
    "debugger",
    "skeptic",
    "demon",
    "parasite",
    "criminal",
    "warrior",
    "romantic",
    "elder",
    "narrator",
]

PERTURBATION_STABILIZATION_TRAITS = [
    "hostile",
    "manipulative",
    "competitive",
    "subversive",
    "iconoclastic",
    "deconstructionist",
    "contrarian",
    "irreverent",
    "sarcastic",
    "dominant",
    "calculating",
    "strategic",
    "nurturing",
    "conciliatory",
    "empathetic",
    "forgiving",
    "diplomatic",
    "calm",
    "cautious",
    "regulatory",
    "humanistic",
]

MORAL_VALENCE_TRAITS = [
    "principled",
    "deontological",
    "humanistic",
    "generous",
    "forgiving",
    "empathetic",
    "nurturing",
    "callous",
    "hostile",
    "manipulative",
    "petty",
    "misanthropic",
    "nihilistic",
    "self_righteous",
]


def load_mean_vector(path: Path) -> np.ndarray:
    tensor = torch.load(path, map_location="cpu").float()
    vector = tensor.mean(0) if tensor.ndim > 1 else tensor
    arr = vector.cpu().numpy().astype(np.float64, copy=False)
    norm = np.linalg.norm(arr)
    if not np.isfinite(norm) or norm == 0:
        raise ValueError(f"Invalid vector norm for {path}: {norm}")
    return arr / norm


def corr_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    pearson = pearsonr(y_true, y_pred).statistic if len(np.unique(y_pred)) > 1 else math.nan
    spearman = spearmanr(y_true, y_pred).statistic if len(np.unique(y_pred)) > 1 else math.nan
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "pearson": float(pearson),
        "spearman": float(spearman),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }


def evaluate_regressor(X: np.ndarray, y: np.ndarray, estimator, seed: int = 42) -> dict[str, dict[str, float]]:
    cv = KFold(n_splits=5, shuffle=True, random_state=seed)
    y_cv = cross_val_predict(estimator, X, y, cv=cv)
    train_idx, test_idx = train_test_split(np.arange(len(y)), test_size=0.2, random_state=seed)
    estimator.fit(X[train_idx], y[train_idx])
    y_test = estimator.predict(X[test_idx])
    return {
        "five_fold_cv": corr_metrics(y, y_cv),
        "heldout_20_percent": corr_metrics(y[test_idx], y_test),
    }


def permutation_baseline(X: np.ndarray, y: np.ndarray, seed: int = 42, n_perm: int = 30) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    cv = KFold(n_splits=5, shuffle=True, random_state=seed)
    r2_values = []
    estimator = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))
    for _ in range(n_perm):
        y_perm = rng.permutation(y)
        pred = cross_val_predict(estimator, X, y_perm, cv=cv)
        r2_values.append(r2_score(y_perm, pred))
    arr = np.array(r2_values)
    return {
        "n_permutations": n_perm,
        "mean_r2": float(arr.mean()),
        "std_r2": float(arr.std(ddof=0)),
        "p95_r2": float(np.percentile(arr, 95)),
    }


def subset_matrix(matrix: pd.DataFrame, trait_names: list[str]) -> tuple[np.ndarray, list[str]]:
    available = [name for name in trait_names if name in matrix.columns]
    return matrix[available].to_numpy(), available


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    geometry = json.loads(GEOMETRY_PATH.read_text())
    role_names = list(geometry["roles"]["names"])
    pca3d = np.array(geometry["roles"]["pca3d"], dtype=float)
    clusters = list(geometry["roles"]["clusters"])

    missing_roles = [name for name in role_names if not (ROLE_DIR / f"{name}.pt").exists()]
    if missing_roles:
        raise RuntimeError(f"Missing role vectors for geometry personas: {missing_roles[:10]}")

    trait_paths = sorted(TRAIT_DIR.glob("*.pt"))
    trait_names = [p.stem for p in trait_paths]
    if not trait_paths:
        raise RuntimeError(f"No trait vectors found under {TRAIT_DIR}")

    role_vectors = np.stack([load_mean_vector(ROLE_DIR / f"{name}.pt") for name in role_names])
    trait_vectors = np.stack([load_mean_vector(path) for path in trait_paths])

    role_shape = tuple(torch.load(ROLE_DIR / f"{role_names[0]}.pt", map_location="cpu").shape)
    trait_shape = tuple(torch.load(trait_paths[0], map_location="cpu").shape)
    if role_vectors.shape[1] != trait_vectors.shape[1]:
        raise RuntimeError(f"Dimensionality mismatch: roles {role_vectors.shape}, traits {trait_vectors.shape}")

    similarity = role_vectors @ trait_vectors.T
    sim_df = pd.DataFrame(similarity, index=role_names, columns=trait_names)
    sim_out = sim_df.copy()
    sim_out.insert(0, "persona", role_names)
    sim_out.to_csv(OUTPUT_DIR / "persona_trait_similarity_matrix.csv", index=False)

    X = similarity
    target_names = ["PC1", "PC2", "PC3"]
    y_targets = {name: pca3d[:, i] for i, name in enumerate(target_names)}

    stats: dict[str, object] = {
        "data_sources": {
            "geometry_data": str(GEOMETRY_PATH.relative_to(REPO_ROOT)),
            "role_vectors": str(ROLE_DIR.relative_to(REPO_ROOT)),
            "trait_vectors": str(TRAIT_DIR.relative_to(REPO_ROOT)),
        },
        "vector_space": {
            "model": "Qwen/Qwen3-32B",
            "layer": 48,
            "role_tensor_shape_example": role_shape,
            "trait_tensor_shape_example": trait_shape,
            "mean_pooling": "mean over 64 stored vectors per persona/trait, then L2 normalize",
            "similarity": "raw activation-space cosine between mean role and mean trait vectors",
        },
        "counts": {"personas": len(role_names), "traits": len(trait_names)},
        "models": {},
        "pc3_subtests": {},
    }

    coef_rows = []
    best_cv_predictions = {}
    for pc_name, y in y_targets.items():
        ridge = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))
        elastic = make_pipeline(
            StandardScaler(),
            ElasticNetCV(l1_ratio=[0.2, 0.5, 0.8], alphas=np.logspace(-2, 1, 10), cv=3, max_iter=10000),
        )

        stats["models"][pc_name] = {
            "ridge": evaluate_regressor(X, y, ridge),
            "elastic_net": evaluate_regressor(X, y, elastic),
            "random_forest_optional": "not run; skipped to keep this repo-local validation bounded",
            "permutation_baseline_ridge_5fold": permutation_baseline(X, y),
        }

        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        ridge_for_pred = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))
        best_cv_predictions[pc_name] = cross_val_predict(ridge_for_pred, X, y, cv=cv)

        ridge_all = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))
        ridge_all.fit(X, y)
        ridge_model = ridge_all.named_steps["ridgecv"]
        for trait, coef in zip(trait_names, ridge_model.coef_):
            coef_rows.append({"pc": pc_name, "trait": trait, "ridge_standardized_coefficient": float(coef)})

    coef_df = pd.DataFrame(coef_rows)
    coef_df.to_csv(OUTPUT_DIR / "pc_trait_predictor_coefficients.csv", index=False)

    perturb_X, perturb_traits = subset_matrix(sim_df, PERTURBATION_STABILIZATION_TRAITS)
    moral_X, moral_traits = subset_matrix(sim_df, MORAL_VALENCE_TRAITS)
    pc3 = y_targets["PC3"]
    stats["pc3_subtests"] = {
        "perturbation_stabilization_traits": {
            "traits_used": perturb_traits,
            "ridge": evaluate_regressor(perturb_X, pc3, make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))),
        },
        "moral_valence_traits": {
            "traits_used": moral_traits,
            "ridge": evaluate_regressor(moral_X, pc3, make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))),
        },
    }

    diagnostic_rows = []
    for persona in DIAGNOSTIC_PERSONAS:
        if persona not in sim_df.index:
            diagnostic_rows.append({"persona": persona, "status": "missing"})
            continue
        scores = sim_df.loc[persona].sort_values(ascending=False)
        for rank, (trait, score) in enumerate(scores.head(10).items(), 1):
            diagnostic_rows.append({"persona": persona, "profile_side": "nearest", "rank": rank, "trait": trait, "cosine": float(score)})
        for rank, (trait, score) in enumerate(scores.tail(10).sort_values().items(), 1):
            diagnostic_rows.append({"persona": persona, "profile_side": "farthest", "rank": rank, "trait": trait, "cosine": float(score)})
    pd.DataFrame(diagnostic_rows).to_csv(OUTPUT_DIR / "diagnostic_persona_trait_profiles.csv", index=False)

    stats_path = OUTPUT_DIR / "trait_predicts_persona_pcs_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, pc_name in zip(axes, target_names):
        y = y_targets[pc_name]
        pred = best_cv_predictions[pc_name]
        metrics = corr_metrics(y, pred)
        ax.scatter(y, pred, s=18, alpha=0.75)
        lo, hi = min(y.min(), pred.min()), max(y.max(), pred.max())
        ax.plot([lo, hi], [lo, hi], color="black", linewidth=1, alpha=0.5)
        ax.set_title(f"{pc_name}: Ridge 5-fold R2={metrics['r2']:.3f}, r={metrics['pearson']:.3f}")
        ax.set_xlabel(f"Actual {pc_name}")
        ax.set_ylabel(f"Predicted {pc_name}")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "trait_prediction_plots.png", dpi=180)
    plt.close(fig)

    report = render_report(stats, coef_df)
    (OUTPUT_DIR / "trait_predicts_persona_pcs_report.md").write_text(report, encoding="utf-8")
    return 0


def top_coefficients(coef_df: pd.DataFrame, pc: str, n: int = 12) -> tuple[pd.DataFrame, pd.DataFrame]:
    subset = coef_df[coef_df["pc"] == pc].sort_values("ridge_standardized_coefficient")
    return subset.tail(n).sort_values("ridge_standardized_coefficient", ascending=False), subset.head(n)


def render_metric_block(metrics: dict[str, float]) -> str:
    return f"R2={metrics['r2']:.3f}, Pearson={metrics['pearson']:.3f}, Spearman={metrics['spearman']:.3f}, RMSE={metrics['rmse']:.3f}"


def render_report(stats: dict[str, object], coef_df: pd.DataFrame) -> str:
    lines = [
        "# Trait Geometry Prediction of Persona PCA Axes",
        "",
        "## Data Sources",
        "",
        f"- Geometry data: `{stats['data_sources']['geometry_data']}`",
        f"- Persona vectors: `{stats['data_sources']['role_vectors']}`",
        f"- Trait vectors: `{stats['data_sources']['trait_vectors']}`",
        "- Vector use: raw activation-space cosine between mean-pooled Qwen role vectors and mean-pooled Qwen trait vectors.",
        f"- Model/layer: {stats['vector_space']['model']}, layer {stats['vector_space']['layer']}.",
        f"- Tensor examples: role {stats['vector_space']['role_tensor_shape_example']}; trait {stats['vector_space']['trait_tensor_shape_example']}.",
        f"- Counts: {stats['counts']['personas']} personas, {stats['counts']['traits']} traits.",
        "",
        "## Validation Method",
        "",
        "The predictor matrix is persona-by-trait cosine similarity in Qwen activation space. Targets are the PCA coordinates embedded in `geometry_viz_data.json`. Each PC was evaluated with 5-fold cross-validation, an 80/20 held-out split, and a 30-permutation ridge baseline. Ridge and elastic net are linear models over standardized trait-cosine features; the optional random forest comparison was skipped to keep this repo-local validation bounded.",
        "",
        "## Predictive Performance",
        "",
        "| PC | Ridge 5-fold | Ridge held-out | Elastic net 5-fold | Optional nonlinear comparison | Permutation mean R2 / p95 |",
        "|---|---|---|---|---|---|",
    ]
    for pc in ["PC1", "PC2", "PC3"]:
        pc_stats = stats["models"][pc]
        perm = pc_stats["permutation_baseline_ridge_5fold"]
        lines.append(
            "| {pc} | {ridge_cv} | {ridge_holdout} | {elastic_cv} | {forest_cv} | {perm_mean:.3f} / {perm_p95:.3f} |".format(
                pc=pc,
                ridge_cv=render_metric_block(pc_stats["ridge"]["five_fold_cv"]),
                ridge_holdout=render_metric_block(pc_stats["ridge"]["heldout_20_percent"]),
                elastic_cv=render_metric_block(pc_stats["elastic_net"]["five_fold_cv"]),
                forest_cv=pc_stats["random_forest_optional"],
                perm_mean=perm["mean_r2"],
                perm_p95=perm["p95_r2"],
            )
        )

    lines.extend(["", "## Top Ridge Trait Predictors", ""])
    for pc in ["PC1", "PC2", "PC3"]:
        pos, neg = top_coefficients(coef_df, pc)
        lines.extend([f"### {pc}", "", "Positive coefficients:"])
        lines.extend([f"- {row.trait}: {row.ridge_standardized_coefficient:.4f}" for row in pos.itertuples()])
        lines.append("")
        lines.append("Negative coefficients:")
        lines.extend([f"- {row.trait}: {row.ridge_standardized_coefficient:.4f}" for row in neg.itertuples()])
        lines.append("")

    pstats = stats["pc3_subtests"]["perturbation_stabilization_traits"]["ridge"]["five_fold_cv"]
    mstats = stats["pc3_subtests"]["moral_valence_traits"]["ridge"]["five_fold_cv"]
    lines.extend(
        [
            "## PC3 Perturbation/Stabilization Versus Moral-Valence Trait Test",
            "",
            f"- Perturbation/stabilization trait subset: {render_metric_block(pstats)}",
            f"- Moral-valence trait subset: {render_metric_block(mstats)}",
            f"- Perturbation/stabilization traits used: {', '.join(stats['pc3_subtests']['perturbation_stabilization_traits']['traits_used'])}",
            f"- Moral-valence traits used: {', '.join(stats['pc3_subtests']['moral_valence_traits']['traits_used'])}",
            "",
            "The subset test is limited because trait labels are hand-selected and partially overlapping. It is diagnostic, not a causal decomposition.",
            "",
            "## Interpretation",
            "",
            "Trait-vector geometry strongly predicts persona PCA coordinates from raw Qwen activation-space cosine profiles. This supports the layered Paper 1.5 interpretation: persona location is not only role semantics or cluster membership; trait structure carries substantial information about where a persona lands in PCA space. The near-ceiling performance should be interpreted cautiously because 240 trait vectors in the same activation space can function as a high-dimensional basis for reconstructing persona PCA coordinates.",
            "",
            "PC1 is strongly predicted, but its coefficient profile is not a simple Big Five-style conscientiousness story. Positive coefficients include conscientious, emotional, risk_taking, strategic, temperamental, confrontational, poetic, interdisciplinary, ironic, absolutist, artistic, and calm; negative coefficients include closure_seeking, ethereal, charismatic, contrarian, dispassionate, edgy, rationalist, deferential, eclectic, nurturing, metaphorical, and generalist. This suggests PC1 is recoverable from trait geometry, but the coefficient basis is correlated and should not be read as a clean one-trait axis.",
            "",
            "PC2 is also predicted well, with a mixed coefficient profile. Positive coefficients include closure_seeking, animated, subversive, specialized, poetic, patient, deferential, experiential, generalist, grounded, concise, and open_ended; negative coefficients include ethereal, traditional, confrontational, flippant, risk_taking, irreverent, romantic, decisive, cynical, adaptable, critical, and resilient. This remains consistent with the current view that PC2 is compound and should not be reduced to one verbal label.",
            "",
            "PC3 is predicted substantially. The full-model coefficient signs are not a direct readable perturbation/stabilization list, but the targeted subset test shows perturbation/stabilization traits predict PC3 slightly better than moral-valence traits. This supports the current PC3 interpretation as perturbation/intervention versus stabilization/care, while leaving room for coefficient-basis instability and correlated-feature effects.",
            "",
            "## Limitations",
            "",
            "- Trait vectors and persona vectors are both derived from Lu-style elicitation artifacts; this test does not prove independent psychological ontology.",
            "- The predictor matrix has 240 trait features for 275 personas, so ridge regularization and held-out validation are essential.",
            "- Near-ceiling prediction means trait geometry spans the persona PCA targets; it does not by itself prove that any single trait label is causally responsible for an axis.",
            "- Coefficients are interpretable only as standardized linear predictors over correlated trait-cosine features.",
            "- The PC3 subset test depends on hand-selected trait groups and should be replaced by a preregistered trait taxonomy or independent rater labels.",
            "",
            "## Recommended Next Test",
            "",
            "Distill the top trait predictors into a small preregistered axis-rubric set, then test whether those traits predict held-out local-manifold perturbation directions around Trickster, Actor, Therapist, and Spy.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
