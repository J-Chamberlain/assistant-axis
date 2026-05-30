#!/usr/bin/env python3
"""Prompt-to-geometry forecasting from released Assistant Axis prompt artifacts.

The main test is concept-level generalization: train on 200 complete trait
artifacts and evaluate on 40 held-out trait artifacts. Role/persona forecasting
is included as a parallel 80/20 held-out-concept check because persona PCs are
defined for roles, while trait PCs are defined for traits.
"""

from __future__ import annotations

import json
import math
import random
import re
import warnings
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MaxAbsScaler

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
DATA_ROOT = REPO_ROOT / "data"
TRAIT_DIR = DATA_ROOT / "traits/instructions"
ROLE_DIR = DATA_ROOT / "roles/instructions"
TRAIT_LIST = DATA_ROOT / "traits/trait_list.json"
ROLE_LIST = DATA_ROOT / "roles/role_list.json"
GEOMETRY_DATA = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
TRAIT_COORDS = REPO_ROOT / "research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv"
ARTIFACT_INVENTORY = REPO_ROOT / "research/outputs/prompt_artifact_inventory"
OUTPUT_DIR = REPO_ROOT / "research/outputs/prompt_to_geometry_forecasting"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TARGETS = ["PC1", "PC2", "PC3"]
VARIANTS = {
    "description_only": ["description"],
    "description_plus_instructions": ["description", "instructions"],
    "description_plus_questions": ["description", "questions"],
    "description_plus_instructions_plus_questions": ["description", "instructions", "questions"],
    "leakage_control": ["description", "instructions", "questions"],
}


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_label(text: str, name: str) -> str:
    variants = {
        name,
        name.replace("_", " "),
        name.replace("_", "-"),
        name.replace("-", " "),
    }
    out = text
    for variant in sorted(variants, key=len, reverse=True):
        if not variant:
            continue
        pattern = re.compile(rf"\b{re.escape(variant)}s?\b", re.IGNORECASE)
        out = pattern.sub("[TARGET]", out)
    return out


def prompt_parts(obj: dict[str, Any], description: str, fields: list[str], include_negative: bool = True) -> list[str]:
    parts: list[str] = []
    if "description" in fields and description:
        parts.append(f"Description: {description}")
    if "instructions" in fields:
        for idx, item in enumerate(obj.get("instruction", [])):
            if item.get("pos"):
                parts.append(f"Positive instruction {idx}: {item['pos']}")
            if include_negative and item.get("neg"):
                parts.append(f"Negative instruction {idx}: {item['neg']}")
    if "questions" in fields:
        questions = obj.get("questions", [])
        parts.append("Behavioral questions: " + " ".join(str(q) for q in questions))
    return parts


def build_trait_dataset() -> pd.DataFrame:
    descriptions = load_json(TRAIT_LIST)
    coords = pd.read_csv(TRAIT_COORDS).set_index("trait")
    rows = []
    for path in sorted(TRAIT_DIR.glob("*.json")):
        name = path.stem
        if name not in coords.index:
            continue
        obj = load_json(path)
        desc = descriptions.get(name, "")
        for variant, fields in VARIANTS.items():
            text = normalize_space("\n".join(prompt_parts(obj, desc, fields, include_negative=True)))
            if variant == "leakage_control":
                text = remove_label(text, name)
            rows.append({
                "concept_type": "trait",
                "name": name,
                "variant": variant,
                "text": text,
                "PC1": float(coords.loc[name, "trait_pc1"]),
                "PC2": float(coords.loc[name, "trait_pc2"]),
                "PC3": float(coords.loc[name, "trait_pc3"]),
            })
    return pd.DataFrame(rows)


def build_role_dataset() -> pd.DataFrame:
    descriptions = load_json(ROLE_LIST)
    geom = load_json(GEOMETRY_DATA)
    names = geom["roles"]["names"]
    coords = pd.DataFrame(geom["roles"]["pca3d"], columns=TARGETS, index=names)
    clusters = pd.Series(geom["roles"].get("clusters", ["unassigned"] * len(names)), index=names)
    rows = []
    for path in sorted(ROLE_DIR.glob("*.json")):
        name = path.stem
        if name == "default" or name not in coords.index:
            continue
        obj = load_json(path)
        desc = descriptions.get(name, "")
        for variant, fields in VARIANTS.items():
            text = normalize_space("\n".join(prompt_parts(obj, desc, fields, include_negative=False)))
            if variant == "leakage_control":
                text = remove_label(text, name)
            rows.append({
                "concept_type": "role",
                "name": name,
                "variant": variant,
                "text": text,
                "cluster": clusters.get(name, "unassigned"),
                "PC1": float(coords.loc[name, "PC1"]),
                "PC2": float(coords.loc[name, "PC2"]),
                "PC3": float(coords.loc[name, "PC3"]),
            })
    return pd.DataFrame(rows)


def metric_dict(y_true: np.ndarray, y_pred: np.ndarray, prefix: str = "") -> dict[str, float | str]:
    out: dict[str, float | str] = {}
    for idx, pc in enumerate(TARGETS):
        yt = y_true[:, idx]
        yp = y_pred[:, idx]
        out[f"{prefix}{pc}_R2"] = float(r2_score(yt, yp))
        out[f"{prefix}{pc}_Pearson_r"] = None if np.std(yp) == 0 else float(pearsonr(yt, yp).statistic)
        out[f"{prefix}{pc}_Spearman_r"] = None if np.std(yp) == 0 else float(spearmanr(yt, yp).statistic)
        out[f"{prefix}{pc}_RMSE"] = float(math.sqrt(mean_squared_error(yt, yp)))
    out[f"{prefix}mean_R2"] = float(np.mean([out[f"{prefix}{pc}_R2"] for pc in TARGETS]))
    return out


def build_models() -> dict[str, Any]:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=6000,
        sublinear_tf=True,
        strip_accents="unicode",
    )
    return {
        "ridge_tfidf": make_pipeline(vectorizer, MaxAbsScaler(), Ridge(alpha=10.0)),
        "elastic_net_tfidf": make_pipeline(clone(vectorizer), MaxAbsScaler(), MultiOutputRegressor(ElasticNet(alpha=0.01, l1_ratio=0.25, max_iter=5000, random_state=RANDOM_STATE))),
        "gradient_boosting_tfidf": make_pipeline(clone(vectorizer), MultiOutputRegressor(GradientBoostingRegressor(random_state=RANDOM_STATE, n_estimators=80, max_depth=2))),
        "small_mlp_tfidf": make_pipeline(clone(vectorizer), MaxAbsScaler(), MLPRegressor(hidden_layer_sizes=(64,), alpha=0.01, max_iter=500, random_state=RANDOM_STATE, early_stopping=True)),
    }


def nearest_neighbor_predict(train_texts: list[str], y_train: np.ndarray, test_texts: list[str]) -> np.ndarray:
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=6000, sublinear_tf=True, strip_accents="unicode")
    train_x = vec.fit_transform(train_texts)
    test_x = vec.transform(test_texts)
    sims = test_x @ train_x.T
    nn = np.asarray(sims.argmax(axis=1)).ravel()
    return y_train[nn]


def evaluate_variant(df: pd.DataFrame, concept_type: str, variant: str, holdout_names: set[str]) -> tuple[list[dict[str, Any]], pd.DataFrame, dict[str, Any]]:
    sub = df[(df["concept_type"] == concept_type) & (df["variant"] == variant)].copy()
    train = sub[~sub["name"].isin(holdout_names)].copy()
    test = sub[sub["name"].isin(holdout_names)].copy()
    y_train = train[TARGETS].to_numpy()
    y_test = test[TARGETS].to_numpy()

    rows: list[dict[str, Any]] = []
    predictions: list[pd.DataFrame] = []

    # Baselines.
    mean_pred_train = np.repeat(y_train.mean(axis=0, keepdims=True), len(train), axis=0)
    mean_pred_test = np.repeat(y_train.mean(axis=0, keepdims=True), len(test), axis=0)
    rows.append({"concept_type": concept_type, "variant": variant, "model": "mean_predictor", "split": "train", **metric_dict(y_train, mean_pred_train)})
    rows.append({"concept_type": concept_type, "variant": variant, "model": "mean_predictor", "split": "heldout", **metric_dict(y_test, mean_pred_test)})

    rng = np.random.default_rng(RANDOM_STATE)
    random_pred = rng.normal(loc=y_train.mean(axis=0), scale=y_train.std(axis=0), size=y_test.shape)
    rows.append({"concept_type": concept_type, "variant": variant, "model": "random_predictor", "split": "heldout", **metric_dict(y_test, random_pred)})

    nn_pred = nearest_neighbor_predict(train["text"].tolist(), y_train, test["text"].tolist())
    rows.append({"concept_type": concept_type, "variant": variant, "model": "nearest_neighbor_semantic_retrieval", "split": "heldout", **metric_dict(y_test, nn_pred)})
    nn_out = test[["name", "variant"]].copy()
    for idx, pc in enumerate(TARGETS):
        nn_out[f"actual_{pc}"] = y_test[:, idx]
        nn_out[f"pred_{pc}"] = nn_pred[:, idx]
    nn_out["model"] = "nearest_neighbor_semantic_retrieval"
    predictions.append(nn_out)

    for model_name, model in build_models().items():
        fit_model = clone(model)
        fit_model.fit(train["text"], y_train)
        pred_train = np.asarray(fit_model.predict(train["text"]))
        pred_test = np.asarray(fit_model.predict(test["text"]))
        rows.append({"concept_type": concept_type, "variant": variant, "model": model_name, "split": "train", **metric_dict(y_train, pred_train)})
        rows.append({"concept_type": concept_type, "variant": variant, "model": model_name, "split": "heldout", **metric_dict(y_test, pred_test)})
        pred_out = test[["name", "variant"]].copy()
        for idx, pc in enumerate(TARGETS):
            pred_out[f"actual_{pc}"] = y_test[:, idx]
            pred_out[f"pred_{pc}"] = pred_test[:, idx]
            pred_out[f"error_{pc}"] = pred_test[:, idx] - y_test[:, idx]
        pred_out["model"] = model_name
        predictions.append(pred_out)

    # Permutation baseline for best intended model class, ridge.
    perm_r2s = []
    for perm_idx in range(30):
        perm_y = y_train.copy()
        rng.shuffle(perm_y, axis=0)
        model = build_models()["ridge_tfidf"]
        model.fit(train["text"], perm_y)
        pred = np.asarray(model.predict(test["text"]))
        perm_r2s.append([r2_score(y_test[:, i], pred[:, i]) for i in range(3)])
    perm_arr = np.array(perm_r2s)
    perm_summary = {
        "concept_type": concept_type,
        "variant": variant,
        "ridge_permutation_30_mean_R2": float(np.mean(perm_arr)),
        "ridge_permutation_30_p95_mean_axis_R2": float(np.percentile(perm_arr.mean(axis=1), 95)),
    }
    return rows, pd.concat(predictions, ignore_index=True), perm_summary


def ridge_feature_analysis(df: pd.DataFrame, concept_type: str, variant: str) -> pd.DataFrame:
    sub = df[(df["concept_type"] == concept_type) & (df["variant"] == variant)].copy()
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=6000, sublinear_tf=True, strip_accents="unicode")
    x = vectorizer.fit_transform(sub["text"])
    y = sub[TARGETS].to_numpy()
    model = Ridge(alpha=10.0).fit(x, y)
    names = np.array(vectorizer.get_feature_names_out())
    rows = []
    for idx, pc in enumerate(TARGETS):
        coefs = model.coef_[idx]
        for rank, j in enumerate(np.argsort(coefs)[::-1][:25], start=1):
            rows.append({"concept_type": concept_type, "variant": variant, "pc": pc, "side": "positive", "rank": rank, "feature": names[j], "coefficient": float(coefs[j])})
        for rank, j in enumerate(np.argsort(coefs)[:25], start=1):
            rows.append({"concept_type": concept_type, "variant": variant, "pc": pc, "side": "negative", "rank": rank, "feature": names[j], "coefficient": float(coefs[j])})
    return pd.DataFrame(rows)


def write_reports(
    dataset: pd.DataFrame,
    results: pd.DataFrame,
    predictions: pd.DataFrame,
    feature_df: pd.DataFrame,
    permutation: list[dict[str, Any]],
    trait_holdout: list[str],
    role_holdout: list[str],
) -> None:
    best = (
        results[results["split"] == "heldout"]
        .sort_values("mean_R2", ascending=False)
        .head(12)
    )
    trait_best = results[(results.concept_type == "trait") & (results.split == "heldout")].sort_values("mean_R2", ascending=False).iloc[0]
    role_best = results[(results.concept_type == "role") & (results.split == "heldout")].sort_values("mean_R2", ascending=False).iloc[0]
    leakage = results[(results.concept_type == "trait") & (results.variant == "leakage_control") & (results.split == "heldout")].sort_values("mean_R2", ascending=False).iloc[0]

    summary = f"""# Prompt-To-Geometry Forecasting Dataset Summary

Model used for analysis scripting: GPT-5.5.

## Exact Artifacts Used

- Trait prompts: `data/traits/instructions/*.json`
- Trait descriptions: `data/traits/trait_list.json`
- Role prompts: `data/roles/instructions/*.json`
- Role descriptions: `data/roles/role_list.json`
- Prompt inventory: `research/outputs/prompt_artifact_inventory/`
- Trait PCA targets: `research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv`
- Persona/role PCA targets: `research/visualizations/geometry_viz_data.json`

## Dataset Construction

One row was created per concept per text variant. This is a concept-level forecasting test, not an individual prompt-row memorization test.

Variants:

- `description_only`
- `description_plus_instructions`
- `description_plus_questions`
- `description_plus_instructions_plus_questions`
- `leakage_control`: description + instructions + questions with exact target names replaced by `[TARGET]`; eval prompts excluded.

Eval prompts were excluded from all variants because they directly reveal target labels and scoring rubrics. The leakage-control variant additionally removes explicit target names where feasible.

## Holdout Methodology

- Trait test: exactly 40 complete held-out traits; 200 complete train traits.
- Role test: 20% held-out roles by concept using a fixed random seed.
- No train/test split occurs at the individual prompt level.

Held-out trait names: {', '.join(trait_holdout)}

## Best Held-Out Results

Best trait model: `{trait_best.model}` on `{trait_best.variant}`, mean R2={trait_best.mean_R2:.3f}; PC1 R2={trait_best.PC1_R2:.3f}, PC2 R2={trait_best.PC2_R2:.3f}, PC3 R2={trait_best.PC3_R2:.3f}.

Best role model: `{role_best.model}` on `{role_best.variant}`, mean R2={role_best.mean_R2:.3f}; PC1 R2={role_best.PC1_R2:.3f}, PC2 R2={role_best.PC2_R2:.3f}, PC3 R2={role_best.PC3_R2:.3f}.

Best leakage-control trait model: `{leakage.model}`, mean R2={leakage.mean_R2:.3f}; PC1 R2={leakage.PC1_R2:.3f}, PC2 R2={leakage.PC2_R2:.3f}, PC3 R2={leakage.PC3_R2:.3f}.

## Top Held-Out Model Rows

```text
{best[['concept_type','variant','model','mean_R2','PC1_R2','PC2_R2','PC3_R2','PC1_Pearson_r','PC2_Pearson_r','PC3_Pearson_r']].to_string(index=False)}
```

## Interpretation

The forecasting test should be interpreted as a prompt-artifact predictability study. Positive held-out performance means the released prompt text contains geometry-relevant information before generation. It does not prove that a new model execution would land at the same geometry under different sampling, nor does it create a safety controller.
"""
    (OUTPUT_DIR / "forecasting_dataset_summary.md").write_text(summary)

    best_model_name = str(trait_best.model)
    best_variant = str(trait_best.variant)
    err = predictions[
        (predictions.concept_type == "trait")
        & (predictions.model == best_model_name)
        & (predictions.variant == best_variant)
    ].copy()
    if "error_PC1" in err:
        err["abs_total_error"] = err[[f"error_{pc}" for pc in TARGETS]].abs().sum(axis=1)
        failures = err.sort_values("abs_total_error", ascending=False).head(15)
        successes = err.sort_values("abs_total_error", ascending=True).head(15)
    else:
        failures = pd.DataFrame()
        successes = pd.DataFrame()
    feat = feature_df[(feature_df.concept_type == "trait") & (feature_df.variant == "leakage_control")]
    feature_lines = []
    for pc in TARGETS:
        pos = feat[(feat.pc == pc) & (feat.side == "positive")].head(10)
        neg = feat[(feat.pc == pc) & (feat.side == "negative")].head(10)
        feature_lines.append(f"- {pc} positive features: " + ", ".join(pos.feature))
        feature_lines.append(f"- {pc} negative features: " + ", ".join(neg.feature))

    error_report = f"""# Forecasting Error Analysis

## Best Trait Forecasting Model

Best held-out trait model: `{best_model_name}` on `{best_variant}`.

## Strongest Successes

```text
{successes[['name','actual_PC1','pred_PC1','actual_PC2','pred_PC2','actual_PC3','pred_PC3','abs_total_error']].to_string(index=False) if not successes.empty else 'n/a'}
```

## Strongest Failures

```text
{failures[['name','actual_PC1','pred_PC1','actual_PC2','pred_PC2','actual_PC3','pred_PC3','abs_total_error']].to_string(index=False) if not failures.empty else 'n/a'}
```

## Prompt Features Most Predictive In Leakage-Control Trait Ridge Model

{chr(10).join(feature_lines)}

## Nearest-Neighbor Baseline

The model comparison CSV includes `nearest_neighbor_semantic_retrieval`, which predicts held-out targets by copying the target coordinates of the most semantically similar training prompt artifact in TF-IDF space. Ridge performance should be evaluated against this baseline rather than only against the mean predictor.

## Implications

Prompt text alone can be evaluated as a pre-generation signal for anticipated geometry, but any downstream steering/control use would require a separate model-execution validation step.
"""
    (OUTPUT_DIR / "forecasting_error_analysis.md").write_text(error_report)

    stats = {
        "model_used": "GPT-5.5",
        "dataset_rows": int(len(dataset)),
        "trait_count": int(dataset[dataset.concept_type == "trait"]["name"].nunique()),
        "role_count": int(dataset[dataset.concept_type == "role"]["name"].nunique()),
        "trait_holdout_count": len(trait_holdout),
        "role_holdout_count": len(role_holdout),
        "trait_holdout_names": trait_holdout,
        "role_holdout_names": role_holdout,
        "best_trait_heldout": trait_best.to_dict(),
        "best_role_heldout": role_best.to_dict(),
        "best_trait_leakage_control": leakage.to_dict(),
        "permutation_baselines": permutation,
        "readiness_assessment": "mixed" if trait_best.mean_R2 > 0 and leakage.mean_R2 > 0 else "failed",
    }
    (OUTPUT_DIR / "forecasting_results.json").write_text(json.dumps(stats, indent=2))


def main() -> None:
    random.seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)
    trait_df = build_trait_dataset()
    role_df = build_role_dataset()
    dataset = pd.concat([trait_df, role_df], ignore_index=True)

    trait_names = sorted(trait_df["name"].unique())
    train_traits, test_traits = train_test_split(trait_names, test_size=40, random_state=RANDOM_STATE)
    role_names = sorted(role_df["name"].unique())
    _, test_roles = train_test_split(role_names, test_size=0.2, random_state=RANDOM_STATE)
    trait_holdout = set(test_traits)
    role_holdout = set(test_roles)

    all_rows = []
    all_predictions = []
    permutation = []
    for concept_type, holdout in [("trait", trait_holdout), ("role", role_holdout)]:
        for variant in VARIANTS:
            rows, preds, perm = evaluate_variant(dataset, concept_type, variant, holdout)
            all_rows.extend(rows)
            all_predictions.append(preds.assign(concept_type=concept_type))
            permutation.append(perm)

    results = pd.DataFrame(all_rows)
    predictions = pd.concat(all_predictions, ignore_index=True)
    feature_df = pd.concat([
        ridge_feature_analysis(dataset, "trait", "leakage_control"),
        ridge_feature_analysis(dataset, "role", "leakage_control"),
    ], ignore_index=True)

    dataset.drop(columns=["text"]).to_csv(OUTPUT_DIR / "forecasting_dataset_index.csv", index=False)
    results.to_csv(OUTPUT_DIR / "forecasting_model_comparison.csv", index=False)
    predictions[predictions.concept_type == "trait"].to_csv(OUTPUT_DIR / "heldout_trait_predictions.csv", index=False)
    feature_df.to_csv(OUTPUT_DIR / "forecasting_feature_coefficients.csv", index=False)
    write_reports(dataset, results, predictions, feature_df, permutation, sorted(trait_holdout), sorted(role_holdout))

    # Plots for best leakage-control trait ridge and best role row.
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for row_idx, (concept_type, title) in enumerate([("trait", "Held-out traits"), ("role", "Held-out roles")]):
        best = results[(results.concept_type == concept_type) & (results.split == "heldout")].sort_values("mean_R2", ascending=False).iloc[0]
        pred = predictions[(predictions.concept_type == concept_type) & (predictions.model == best.model) & (predictions.variant == best.variant)]
        for col_idx, pc in enumerate(TARGETS):
            ax = axes[row_idx, col_idx]
            ax.scatter(pred[f"actual_{pc}"], pred[f"pred_{pc}"], s=30, alpha=0.75)
            lo = min(pred[f"actual_{pc}"].min(), pred[f"pred_{pc}"].min())
            hi = max(pred[f"actual_{pc}"].max(), pred[f"pred_{pc}"].max())
            ax.plot([lo, hi], [lo, hi], color="black", linewidth=1)
            ax.set_title(f"{title} {pc}\\n{best.model}, {best.variant}")
            ax.set_xlabel("Actual")
            ax.set_ylabel("Predicted")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "prompt_to_geometry_plots.png", dpi=160)
    plt.close(fig)

    print(json.dumps({
        "output_dir": str(OUTPUT_DIR),
        "dataset_rows": int(len(dataset)),
        "trait_holdout": len(trait_holdout),
        "role_holdout": len(role_holdout),
        "best_trait": results[(results.concept_type == "trait") & (results.split == "heldout")].sort_values("mean_R2", ascending=False).iloc[0].to_dict(),
        "best_role": results[(results.concept_type == "role") & (results.split == "heldout")].sort_values("mean_R2", ascending=False).iloc[0].to_dict(),
    }, indent=2))


if __name__ == "__main__":
    main()
