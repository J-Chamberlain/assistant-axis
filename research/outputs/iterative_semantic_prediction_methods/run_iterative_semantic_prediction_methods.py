#!/usr/bin/env python3
"""Archive the iterative semantic prediction methods summary and benchmark table."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research" / "outputs" / "iterative_semantic_prediction_methods"

ROWS = [
    {
        "order": 1,
        "feature_family": "Semantic baseline",
        "status": "established",
        "mean_r2": 0.389,
        "interpretation": "Baseline reference; semantic topology partially predicts activation topology but does not fully explain it.",
        "primary_source": "research/RESEARCH_INDEX.md; research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv",
    },
    {
        "order": 2,
        "feature_family": "Codex trait replication",
        "status": "provisional/weak",
        "mean_r2": 0.398,
        "interpretation": "Weak positive trait signal; not a successful replication of stronger Big Five-style results.",
        "primary_source": "research/PROVENANCE_REGISTRY.md; research/q2_stability/qwen/outputs/codex_trait_replication/codex_trait_replication_report.md",
    },
    {
        "order": 3,
        "feature_family": "Codex retained procedural/behavioral features",
        "status": "established",
        "mean_r2": 0.490,
        "interpretation": "Procedural and behavioral features improve substantially over semantic baseline.",
        "primary_source": "research/RESEARCH_INDEX.md; research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv",
    },
    {
        "order": 4,
        "feature_family": "Claude Big Five-style features",
        "status": "established",
        "mean_r2": 0.613,
        "interpretation": "Strongest compact global predictor; useful but not independent psychometric evidence.",
        "primary_source": "research/RESEARCH_INDEX.md; research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv",
    },
    {
        "order": 5,
        "feature_family": "Hierarchical trait-plus-procedural model",
        "status": "provisional",
        "mean_r2": 0.622,
        "interpretation": "Small residual improvement over Big Five-style stage, supporting layered structure.",
        "primary_source": "research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/hierarchical_model_report.md",
    },
    {
        "order": 6,
        "feature_family": "Residual-manifold hand-feature layer",
        "status": "provisional/diagnostic",
        "mean_r2": 0.632,
        "interpretation": "Small diagnostic improvement over hierarchy; useful for residual regions, not a solved third-layer model.",
        "primary_source": "research/q2_stability/qwen/outputs/residual_manifold_analysis/residual_manifold_report.md",
    },
    {
        "order": 7,
        "feature_family": "Semantic + Big Five + SVD15 prompt-register basis",
        "status": "provisional/strong",
        "mean_r2": 0.707,
        "interpretation": "Strongest predictive result; lexical/register-sensitive and not yet distilled into stable human-readable features.",
        "primary_source": "research/q2_stability/qwen/outputs/residual_svd_interpretation/residual_svd_interpretation_report.md",
    },
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(ROWS)
    table["approx_r"] = table["mean_r2"].map(lambda x: math.sqrt(x))
    table["benchmark_scope"] = "273 common personas; canonical Qwen activation PCA3D; five deterministic held-out splits"
    table.to_csv(OUT / "iterative_semantic_prediction_benchmark_table.csv", index=False)

    methods = f"""# Methods: Iterative Semantic Prediction of Persona Activation Geometry

`model_used`: GPT-5.5 for archival/report generation. No model APIs, GPU work, response generation, activation extraction, projection reruns, or new benchmark fitting were performed for this archive.

## Purpose

This note memorializes the iterative semantic-prediction benchmark sequence used in Paper 1.5 planning. It is derived from the canonical summary in `research/RESEARCH_INDEX.md` and the artifact lineage in `research/PROVENANCE_REGISTRY.md`.

## Benchmark Definition

To test whether persona activation geometry could be predicted from interpretable semantic features, the project constructed a sequence of held-out prediction benchmarks over canonical Qwen activation PCA coordinates. The target variable was the three-dimensional activation geometry of the common persona set, represented by PC1, PC2, and PC3 coordinates in the reconstructed Qwen persona space.

The benchmark used 273 common personas and five deterministic train/test split assignments. Performance was evaluated using held-out mean R2 across the activation PCA dimensions. For readability, the table below also reports approximate R as the positive square root of R2.

## Iterative Results

| Feature family | Status | Mean R2 | Approx R | Interpretation |
|---|---|---:|---:|---|
"""
    for row in table.itertuples(index=False):
        methods += (
            f"| {row.feature_family} | {row.status} | {row.mean_r2:.3f} | "
            f"{row.approx_r:.3f} | {row.interpretation} |\n"
        )

    methods += """
## Interpretation

The semantic baseline established that ordinary lexical or semantic topology partially predicts activation topology, but does not fully explain it. The constrained Codex trait replication improved only slightly over that baseline and should be treated as weak positive trait signal rather than a successful replication of the stronger Big Five-style feature result.

Codex-retained procedural and behavioral features produced a larger improvement over semantic baseline, supporting the view that activation geometry contains interpretable operating-mode structure beyond ordinary semantic similarity. Claude Big Five-style features were the strongest compact global predictor, but they remain structured descriptors for prediction rather than independent psychometric measurements.

The hierarchical trait-plus-procedural model and residual-manifold hand-feature layer produced modest incremental gains. These are best framed as evidence for layered residual structure, not as a solved ontology. The strongest observed predictive result came from adding a 15-dimensional SVD prompt/register basis to semantic and Big Five-style predictors. Because this basis is lexical and register-sensitive, it should be interpreted as evidence that residual activation geometry remains partly predictable from prompt/register structure, pending distillation into stable human-readable features.

## Bottom Line

Across iterations, held-out mean R2 increased from 0.389 for the semantic baseline to 0.707 for the semantic + Big Five + SVD15 prompt-register model. This supports a layered interpretation of persona activation geometry: semantic similarity explains a meaningful baseline portion; compact trait-style descriptors explain substantially more; procedural and residual features add smaller increments; and lexical/register-sensitive SVD features currently give the strongest prediction while requiring caution.

## Caveats

- These are held-out prediction results over the canonical shared benchmark, not execution-time activation validation.
- Big Five-style and SVD/register features are useful predictors but should not be treated as causal psychological ontology.
- The SVD15 result may capture prompt-corpus or register structure; it needs distillation and retesting before being elevated to a stable interpretation.
- R values are reported only as approximate square roots of R2 for interpretive convenience.
"""
    (OUT / "iterative_semantic_prediction_methods.md").write_text(methods, encoding="utf-8")

    inventory = pd.DataFrame(
        [
            {
                "artifact": "iterative_semantic_prediction_methods.md",
                "path": str((OUT / "iterative_semantic_prediction_methods.md").relative_to(REPO)),
                "status": "active",
                "description": "Methods prose for the iterative semantic prediction benchmark sequence.",
            },
            {
                "artifact": "iterative_semantic_prediction_benchmark_table.csv",
                "path": str((OUT / "iterative_semantic_prediction_benchmark_table.csv").relative_to(REPO)),
                "status": "active",
                "description": "Excel-friendly benchmark table with mean R2, approximate R, status, caveat, and source.",
            },
            {
                "artifact": "artifact_inventory.csv",
                "path": str((OUT / "artifact_inventory.csv").relative_to(REPO)),
                "status": "active",
                "description": "Artifact inventory for this methods archive.",
            },
            {
                "artifact": "run_iterative_semantic_prediction_methods.py",
                "path": str((OUT / "run_iterative_semantic_prediction_methods.py").relative_to(REPO)),
                "status": "active",
                "description": "Generation script for this methods archive.",
            },
        ]
    )
    inventory.to_csv(OUT / "artifact_inventory.csv", index=False)


if __name__ == "__main__":
    main()
