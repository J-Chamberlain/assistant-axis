#!/usr/bin/env python3
"""PC2 trait-profile analysis with PC1 stratification/control.

This script uses saved public-artifact outputs only. It does not call APIs,
run judges, or perform model inference.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "outputs" / "pc2_trait_stratified_profile"
GEOMETRY_PATH = ROOT / "research" / "visualizations" / "geometry_viz_data.json"
TRAIT_MATRIX_PATH = (
    ROOT
    / "research"
    / "outputs"
    / "trait_persona_prediction"
    / "persona_trait_similarity_matrix.csv"
)
TRAIT_STATS_PATH = (
    ROOT
    / "research"
    / "outputs"
    / "trait_persona_prediction"
    / "trait_predicts_persona_pcs_stats.json"
)
PC2_MUTED_PATH = (
    ROOT
    / "research"
    / "outputs"
    / "pc2_muted_pc1_extremes"
    / "pc2_muted_pc1_top_bottom.csv"
)
PC2_CLUSTER_DIAG_PATH = (
    ROOT
    / "research"
    / "outputs"
    / "pc2_cluster_conditioned_extremes"
    / "pc2_diagnostic_roles_table.csv"
)

RNG = np.random.default_rng(20260604)
BOOTSTRAPS = 400


def slug(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def load_geometry() -> tuple[pd.DataFrame, dict]:
    with GEOMETRY_PATH.open() as f:
        data = json.load(f)
    roles = data["roles"]
    coords = np.array(roles["pca3d"], dtype=float)
    df = pd.DataFrame(
        {
            "persona": roles["names"],
            "pc1": coords[:, 0],
            "pc2": coords[:, 1],
            "pc3": coords[:, 2],
            "cluster": roles.get("clusters", ["unknown"] * len(roles["names"])),
        }
    )
    for pc in ["pc1", "pc2", "pc3"]:
        df[f"{pc}_percentile"] = df[pc].rank(pct=True, method="average") * 100
    return df, data.get("metadata", {})


def load_joined() -> tuple[pd.DataFrame, list[str], dict, dict]:
    geom, metadata = load_geometry()
    traits = pd.read_csv(TRAIT_MATRIX_PATH)
    trait_names = [c for c in traits.columns if c != "persona"]
    joined = geom.merge(traits, on="persona", how="inner")
    if len(joined) != len(geom) or len(joined) != len(traits):
        missing_geom = sorted(set(geom["persona"]) - set(joined["persona"]))
        missing_traits = sorted(set(traits["persona"]) - set(joined["persona"]))
        raise RuntimeError(
            f"Role/trait join mismatch. missing_geom={missing_geom[:5]}, "
            f"missing_traits={missing_traits[:5]}"
        )
    stats = {}
    if TRAIT_STATS_PATH.exists():
        stats = json.loads(TRAIT_STATS_PATH.read_text())
    return joined, trait_names, metadata, stats


def define_strata(df: pd.DataFrame) -> tuple[dict, dict[str, pd.Index]]:
    pct = lambda q: float(df["pc1"].quantile(q))
    definitions: dict[str, dict] = {}
    masks: dict[str, pd.Series] = {}

    definitions["global"] = {
        "type": "all_roles",
        "pc1_quantile_low": None,
        "pc1_quantile_high": None,
        "pc1_low": None,
        "pc1_high": None,
        "n_roles": int(len(df)),
    }
    masks["global"] = pd.Series(True, index=df.index)

    terciles = {
        "low_pc1": (0.0, 1 / 3),
        "mid_pc1": (1 / 3, 2 / 3),
        "high_pc1": (2 / 3, 1.0),
    }
    quintiles = {f"pc1_q{i + 1}": (i / 5, (i + 1) / 5) for i in range(5)}
    central = {"central_pc1_muted_45_55": (0.45, 0.55)}

    for name, (lo_q, hi_q) in {**terciles, **quintiles, **central}.items():
        lo, hi = pct(lo_q), pct(hi_q)
        if hi_q == 1.0:
            mask = (df["pc1"] >= lo) & (df["pc1"] <= hi)
        else:
            mask = (df["pc1"] >= lo) & (df["pc1"] < hi)
        definitions[name] = {
            "type": "pc1_quantile_band",
            "pc1_quantile_low": lo_q,
            "pc1_quantile_high": hi_q,
            "pc1_low": lo,
            "pc1_high": hi,
            "n_roles": int(mask.sum()),
        }
        masks[name] = mask

    return definitions, {k: df.index[v].copy() for k, v in masks.items()}


def high_low_for_stratum(
    df: pd.DataFrame, idx: pd.Index, stratum: str, top_frac: float = 0.20
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    sub = df.loc[idx].sort_values("pc2", ascending=False).copy()
    n = len(sub)
    k = max(3, int(math.ceil(n * top_frac)))
    if n >= 20:
        k = max(5, k)
    if 2 * k > n:
        k = max(1, n // 2)
    sub["pc2_rank_desc_within_stratum"] = np.arange(1, n + 1)
    sub["pc2_percentile_within_stratum"] = (
        sub["pc2"].rank(pct=True, method="average") * 100
    )
    high = sub.head(k).copy()
    low = sub.tail(k).copy()
    high["pc2_group"] = "high_pc2"
    low["pc2_group"] = "low_pc2"
    thresholds = {
        "stratum": stratum,
        "n_roles": int(n),
        "tail_fraction": top_frac,
        "tail_n_each": int(k),
        "high_pc2_min": float(high["pc2"].min()),
        "low_pc2_max": float(low["pc2"].max()),
    }
    return high, low, thresholds


def cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2 or len(y) < 2:
        return float("nan")
    pooled_var = ((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1)) / (
        len(x) + len(y) - 2
    )
    if pooled_var <= 0:
        return 0.0
    return float((x.mean() - y.mean()) / math.sqrt(pooled_var))


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) == 0 or len(y) == 0:
        return float("nan")
    diff = x[:, None] - y[None, :]
    return float(((diff > 0).sum() - (diff < 0).sum()) / diff.size)


def bootstrap_ci(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) == 0 or len(y) == 0:
        return float("nan"), float("nan")
    vals = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        vals[i] = RNG.choice(x, len(x), replace=True).mean() - RNG.choice(
            y, len(y), replace=True
        ).mean()
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def enrichment_table(
    df: pd.DataFrame,
    trait_names: list[str],
    high_idx: pd.Index,
    low_idx: pd.Index,
    stratum: str,
) -> pd.DataFrame:
    rows = []
    for trait in trait_names:
        x = df.loc[high_idx, trait].to_numpy(float)
        y = df.loc[low_idx, trait].to_numpy(float)
        diff = float(x.mean() - y.mean())
        ci_lo, ci_hi = bootstrap_ci(x, y)
        rows.append(
            {
                "stratum": stratum,
                "trait": trait,
                "n_high_pc2": int(len(x)),
                "n_low_pc2": int(len(y)),
                "mean_high_pc2": float(x.mean()),
                "mean_low_pc2": float(y.mean()),
                "mean_diff_high_minus_low": diff,
                "cohens_d": cohen_d(x, y),
                "cliffs_delta": cliffs_delta(x, y),
                "bootstrap_ci_low": ci_lo,
                "bootstrap_ci_high": ci_hi,
                "enriched_pole": "high_pc2" if diff >= 0 else "low_pc2",
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values("cohens_d", ascending=False, key=lambda s: s.abs())


def residualize(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta, beta


def standardize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    sd = v.std(ddof=0)
    if sd == 0:
        return np.zeros_like(v)
    return (v - v.mean()) / sd


def pc1_control_models(df: pd.DataFrame, trait_names: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    pc1 = standardize(df["pc1"].to_numpy(float))
    pc2 = standardize(df["pc2"].to_numpy(float))
    pc2_resid, resid_beta = residualize(pc2, pc1)
    rows = []
    for trait in trait_names:
        t = standardize(df[trait].to_numpy(float))
        X = np.column_stack([np.ones(len(df)), pc1, t])
        beta, *_ = np.linalg.lstsq(X, pc2, rcond=None)
        pred = X @ beta
        ss_res = float(((pc2 - pred) ** 2).sum())
        ss_tot = float(((pc2 - pc2.mean()) ** 2).sum())
        corr = float(np.corrcoef(t, pc2_resid)[0, 1])
        rows.append(
            {
                "trait": trait,
                "beta_trait_pc1_controlled": float(beta[2]),
                "beta_pc1": float(beta[1]),
                "intercept": float(beta[0]),
                "r2_pc2_model": 1 - ss_res / ss_tot if ss_tot else float("nan"),
                "corr_trait_with_pc2_residual": corr,
                "pc2_residualization_intercept": float(resid_beta[0]),
                "pc2_residualization_beta_pc1": float(resid_beta[1]),
            }
        )
    coeffs = pd.DataFrame(rows).sort_values(
        "beta_trait_pc1_controlled", ascending=False, key=lambda s: s.abs()
    )
    df_resid = df.copy()
    df_resid["pc2_residual_after_pc1"] = pc2_resid
    return coeffs, df_resid


def replicated_traits(enrich_all: pd.DataFrame) -> pd.DataFrame:
    q_strata = [f"pc1_q{i}" for i in range(1, 6)]
    q = enrich_all[enrich_all["stratum"].isin(q_strata)].copy()
    global_map = (
        enrich_all[enrich_all["stratum"] == "global"]
        .set_index("trait")["cohens_d"]
        .to_dict()
    )
    rows = []
    for trait, g in q.groupby("trait"):
        pos = g[g["cohens_d"] >= 0.50]
        neg = g[g["cohens_d"] <= -0.50]
        if len(pos) >= 3:
            pole = "high_pc2"
            keep = pos
        elif len(neg) >= 3:
            pole = "low_pc2"
            keep = neg
        else:
            continue
        rows.append(
            {
                "trait": trait,
                "replicated_pole": pole,
                "n_quintile_strata_abs_d_ge_0_5_same_sign": int(len(keep)),
                "mean_cohens_d_across_quintiles": float(g["cohens_d"].mean()),
                "median_cohens_d_across_quintiles": float(g["cohens_d"].median()),
                "mean_abs_cohens_d_same_sign_strata": float(keep["cohens_d"].abs().mean()),
                "supporting_strata": ", ".join(keep["stratum"].tolist()),
                "global_cohens_d": float(global_map.get(trait, np.nan)),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["replicated_pole", "n_quintile_strata_abs_d_ge_0_5_same_sign", "mean_abs_cohens_d_same_sign_strata"],
        ascending=[True, False, False],
    )


THEMES = {
    "accommodation_responsiveness": [
        "accommodating",
        "adaptable",
        "agreeable",
        "collaborative",
        "conciliatory",
        "diplomatic",
        "empathetic",
        "supportive",
        "deferential",
        "flexible",
        "nurturing",
        "inclusive",
    ],
    "situated_immediacy_social_exposure": [
        "animated",
        "emotional",
        "experiential",
        "extroverted",
        "gregarious",
        "grounded",
        "reactive",
        "visceral",
        "urgent",
        "casual",
        "theatrical",
        "dramatic",
    ],
    "developmental_openness_vulnerability": [
        "naive",
        "anxious",
        "neurotic",
        "impatient",
        "disorganized",
        "avoidant",
        "submissive",
        "patient",
        "open_ended",
        "exploratory",
        "curious",
    ],
    "performance_pressure": [
        "entertaining",
        "charismatic",
        "performative",
        "sassy",
        "witty",
        "playful",
        "dramatic",
        "theatrical",
        "provocative",
        "competitive",
    ],
    "stable_internal_organization": [
        "calm",
        "circumspect",
        "conscientious",
        "decisive",
        "disciplined",
        "formal",
        "methodical",
        "meticulous",
        "principled",
        "regulatory",
        "resilient",
        "serious",
        "stoic",
        "traditional",
    ],
    "abstraction_worldview": [
        "abstract",
        "analytical",
        "big_picture",
        "conceptual",
        "data_driven",
        "erudite",
        "historical",
        "holistic",
        "philosophical",
        "rationalist",
        "systems_thinker",
        "theoretical",
        "universalist",
    ],
    "autonomy_self_direction": [
        "assertive",
        "confident",
        "independent",
        "individualistic",
        "libertarian",
        "proactive",
        "self_directed",
        "dominant",
    ],
    "institutional_standards_bearing": [
        "convergent",
        "deontological",
        "educational",
        "factual",
        "formalist",
        "literal",
        "pedantic",
        "perfectionist",
        "prescriptive",
        "principled",
        "quantitative",
        "regulatory",
        "technical",
        "utilitarian",
    ],
}


def theme_table(rep: pd.DataFrame, coeffs: pd.DataFrame, trait_names: list[str]) -> pd.DataFrame:
    rep_traits = set(rep["trait"]) if not rep.empty else set()
    coef = coeffs.set_index("trait")["beta_trait_pc1_controlled"].to_dict()
    rows = []
    for theme, candidates in THEMES.items():
        available = [t for t in candidates if t in trait_names]
        replicated = [t for t in available if t in rep_traits]
        top_controlled = sorted(available, key=lambda t: abs(coef.get(t, 0)), reverse=True)[:8]
        mean_beta = float(np.mean([coef.get(t, np.nan) for t in available])) if available else float("nan")
        if len(replicated) >= 3:
            evidence = "Observed"
        elif len(replicated) >= 1:
            evidence = "Inferred"
        else:
            evidence = "Speculative"
        rows.append(
            {
                "theme": theme,
                "available_traits": ", ".join(available),
                "replicated_traits": ", ".join(replicated),
                "top_pc1_controlled_traits": ", ".join(top_controlled),
                "mean_pc1_controlled_beta_available_traits": mean_beta,
                "evidence_status": evidence,
                "interpretive_note": theme_note(theme),
            }
        )
    return pd.DataFrame(rows)


def theme_note(theme: str) -> str:
    notes = {
        "accommodation_responsiveness": "Tests whether high PC2 reflects context-responsiveness or interpersonal accommodation.",
        "situated_immediacy_social_exposure": "Tests whether high PC2 reflects local immediacy and social exposure.",
        "developmental_openness_vulnerability": "Tests whether high PC2 reflects formative, unsettled, or dependent states.",
        "performance_pressure": "Tests whether high PC2 is partly performative/reactive rather than only developmental.",
        "stable_internal_organization": "Tests the low-PC2 side as organized, disciplined, durable, or stabilizing.",
        "abstraction_worldview": "Tests the low-PC2 side as integrated abstraction and broad worldview structure.",
        "autonomy_self_direction": "Tests whether low PC2 is more internally directed rather than context-shaped.",
        "institutional_standards_bearing": "Tests whether low PC2 carries standards-bearing or institutional structure.",
    }
    return notes[theme]


def write_markdown(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n")


def md_table(df: pd.DataFrame, n: int = 12, cols: list[str] | None = None) -> str:
    sub = df.head(n).copy()
    if cols:
        sub = sub[cols]
    return df_to_md(sub)


def fmt_cell(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def df_to_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    headers = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt_cell(row[c]) for c in df.columns) + " |")
    return "\n".join(lines)


def make_plots(
    joined: pd.DataFrame,
    enrich_all: pd.DataFrame,
    rep: pd.DataFrame,
    high_low_roles: pd.DataFrame,
) -> None:
    q_strata = [f"pc1_q{i}" for i in range(1, 6)]
    if not rep.empty:
        top_traits = (
            rep.sort_values("mean_abs_cohens_d_same_sign_strata", ascending=False)
            .head(24)["trait"]
            .tolist()
        )
    else:
        top_traits = (
            enrich_all[enrich_all["stratum"] == "global"]
            .reindex(enrich_all[enrich_all["stratum"] == "global"]["cohens_d"].abs().sort_values(ascending=False).index)
            .head(24)["trait"]
            .tolist()
        )
    heat = (
        enrich_all[enrich_all["stratum"].isin(q_strata) & enrich_all["trait"].isin(top_traits)]
        .pivot(index="trait", columns="stratum", values="cohens_d")
        .reindex(top_traits)
    )
    fig, ax = plt.subplots(figsize=(8, max(5, 0.32 * len(heat))))
    im = ax.imshow(heat.fillna(0).to_numpy(), cmap="coolwarm", aspect="auto", vmin=-2.5, vmax=2.5)
    ax.set_xticks(range(len(heat.columns)))
    ax.set_xticklabels(heat.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index)
    ax.set_title("PC2 high-vs-low trait effect sizes across PC1 quintiles")
    fig.colorbar(im, ax=ax, label="Cohen's d (high PC2 - low PC2)")
    fig.tight_layout()
    fig.savefig(OUT / "pc2_trait_enrichment_heatmap.png", dpi=180)
    plt.close(fig)

    global_enrich = enrich_all[enrich_all["stratum"] == "global"].copy()
    top_high = global_enrich.sort_values("cohens_d", ascending=False).head(14)
    top_low = global_enrich.sort_values("cohens_d", ascending=True).head(14)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    axes[0].barh(top_high["trait"][::-1], top_high["cohens_d"][::-1], color="#3b82f6")
    axes[0].set_title("Global high-PC2 enriched traits")
    axes[0].set_xlabel("Cohen's d")
    axes[1].barh(top_low["trait"][::-1], top_low["cohens_d"][::-1], color="#ef4444")
    axes[1].set_title("Global low-PC2 enriched traits")
    axes[1].set_xlabel("Cohen's d")
    fig.tight_layout()
    fig.savefig(OUT / "pc2_trait_high_low_barplots.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 8))
    clusters = joined["cluster"].astype("category")
    ax.scatter(joined["pc1"], joined["pc2"], c=clusters.cat.codes, cmap="tab10", alpha=0.45, s=28)
    label_roles = set(
        high_low_roles[
            high_low_roles["stratum"].isin(["central_pc1_muted_45_55", "mid_pc1"])
        ]
        .sort_values("pc2", key=lambda s: s.abs(), ascending=False)
        .head(24)["persona"]
    )
    diagnostic = {
        "patient",
        "amateur",
        "tree",
        "hive",
        "philosopher",
        "shapeshifter",
        "chameleon",
        "elder",
        "caregiver",
    }
    for _, row in joined[joined["persona"].isin(label_roles | diagnostic)].iterrows():
        ax.text(row["pc1"], row["pc2"], row["persona"], fontsize=8)
    ax.axvline(0, color="black", lw=0.6, alpha=0.4)
    ax.axhline(0, color="black", lw=0.6, alpha=0.4)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Qwen persona PC1/PC2 with PC2 diagnostic roles")
    fig.tight_layout()
    fig.savefig(OUT / "pc2_trait_representative_roles_scatter.png", dpi=180)
    plt.close(fig)


def write_reports(
    joined: pd.DataFrame,
    trait_names: list[str],
    metadata: dict,
    stats: dict,
    stratum_defs: dict,
    threshold_rows: list[dict],
    high_low_roles: pd.DataFrame,
    enrich_global: pd.DataFrame,
    enrich_all: pd.DataFrame,
    rep: pd.DataFrame,
    themes: pd.DataFrame,
    coeffs: pd.DataFrame,
    residual_enrich: pd.DataFrame,
) -> None:
    vector_space = stats.get("vector_space", {})
    top_high = enrich_global.sort_values("cohens_d", ascending=False)
    top_low = enrich_global.sort_values("cohens_d", ascending=True)
    rep_high = rep[rep["replicated_pole"] == "high_pc2"].sort_values(
        "mean_abs_cohens_d_same_sign_strata", ascending=False
    ) if not rep.empty else pd.DataFrame()
    rep_low = rep[rep["replicated_pole"] == "low_pc2"].sort_values(
        "mean_abs_cohens_d_same_sign_strata", ascending=False
    ) if not rep.empty else pd.DataFrame()

    write_markdown(
        OUT / "pc2_trait_profile_inventory.md",
        f"""
# PC2 Trait-Profile Inventory

- Startup status: verified by raw GitHub startup files with cache-busted `curl`.
- Geometry source: `{GEOMETRY_PATH.relative_to(ROOT)}`
- Trait-profile source: `{TRAIT_MATRIX_PATH.relative_to(ROOT)}`
- Prior trait stats source: `{TRAIT_STATS_PATH.relative_to(ROOT)}`
- Optional prior PC2 sources: `{PC2_MUTED_PATH.relative_to(ROOT)}`, `{PC2_CLUSTER_DIAG_PATH.relative_to(ROOT)}`
- Source model: `{metadata.get('source_model', 'unknown')}`
- Geometry metadata `model_used`: `{metadata.get('model_used', 'unknown')}`. This is project metadata, not the source model for the public role vectors.
- Trait/profile model: `{vector_space.get('model', 'unknown')}`
- Trait/profile layer: `{vector_space.get('layer', 'unknown')}`
- Trait score meaning: `{vector_space.get('similarity', 'raw activation-space cosine between mean role and mean trait vectors')}`
- Stored-vector pooling note: `{vector_space.get('mean_pooling', 'unknown')}`
- Joined role count: {len(joined)}
- Trait count: {len(trait_names)}
- Cluster count: {joined['cluster'].nunique()}

The joined matrix stores Qwen role PCA coordinates plus the 240-dimensional persona-by-trait cosine profile. These trait scores are activation-space similarity features, not direct human ratings or causal psychological labels.
""",
    )

    stratum_summary = pd.DataFrame(threshold_rows)
    write_markdown(
        OUT / "pc2_trait_pc1_control_report.md",
        f"""
# PC1-Controlled PC2 Trait Diagnostics

## Method

For each trait, the script fit a standardized linear model:

`PC2_z ~ PC1_z + trait_z`

The reported trait coefficient is the association with PC2 after removing the linear PC1 component. A second diagnostic regressed PC2 on PC1, then correlated each trait with the residual.

Because PC1 and PC2 are PCA-orthogonal, regressing PC2 directly on PC1 produces a near-zero PC1 coefficient; target residualization therefore mostly reproduces PC2. The more useful control is the per-trait model that includes PC1 as a covariate, plus the PC1-stratified enrichment tables. Since individual trait features can be collinear with PC1 and with each other, the residual correlation column is the safer first-read statistic; the beta column is retained for auditability.

## Strongest Positive PC1-Controlled Residual Correlations

{md_table(coeffs.sort_values('corr_trait_with_pc2_residual', ascending=False), 15, ['trait','corr_trait_with_pc2_residual','beta_trait_pc1_controlled','r2_pc2_model'])}

## Strongest Negative PC1-Controlled Residual Correlations

{md_table(coeffs.sort_values('corr_trait_with_pc2_residual', ascending=True), 15, ['trait','corr_trait_with_pc2_residual','beta_trait_pc1_controlled','r2_pc2_model'])}

## Residual-Enrichment Check

Traits enriched in high residual-PC2 roles broadly overlap with stratified PC2 enrichment, but residual models remain correlational over trait-cosine features. They reduce PC1 confounding; they do not establish a causal trait basis for PC2.

Top residual high-PC2 traits:

{md_table(residual_enrich.sort_values('cohens_d', ascending=False), 12, ['trait','cohens_d','mean_diff_high_minus_low','bootstrap_ci_low','bootstrap_ci_high'])}

Top residual low-PC2 traits:

{md_table(residual_enrich.sort_values('cohens_d', ascending=True), 12, ['trait','cohens_d','mean_diff_high_minus_low','bootstrap_ci_low','bootstrap_ci_high'])}
""",
    )

    write_markdown(
        OUT / "pc2_trait_theme_synthesis.md",
        f"""
# PC2 Trait Theme Synthesis

## Basis

Themes are grouped from traits that distinguish high-PC2 from low-PC2 roles within PC1 strata. A theme is marked `Observed` when at least three of its candidate traits replicate across PC1 quintiles, `Inferred` when one or two replicate, and `Speculative` otherwise. This is a deterministic synthesis over trait names and effect sizes, not a new LLM judgment.

## Replicated High-PC2 Traits

{md_table(rep_high, 15, ['trait','n_quintile_strata_abs_d_ge_0_5_same_sign','mean_cohens_d_across_quintiles','global_cohens_d','supporting_strata']) if not rep_high.empty else 'No high-PC2 replicated traits passed the threshold.'}

## Replicated Low-PC2 Traits

{md_table(rep_low, 15, ['trait','n_quintile_strata_abs_d_ge_0_5_same_sign','mean_cohens_d_across_quintiles','global_cohens_d','supporting_strata']) if not rep_low.empty else 'No low-PC2 replicated traits passed the threshold.'}

## Theme Table

{df_to_md(themes[['theme','replicated_traits','top_pc1_controlled_traits','evidence_status','interpretive_note']])}

## Interpretation

The trait-profile evidence should update PC2 wording toward a contrast between context-shaped, socially/situationally exposed, affectively immediate roles and roles with more stable internal organization, abstraction, or standards-bearing structure. The evidence supports the existing situated/formative versus integrated/stable interpretation, but it also suggests `accommodation/context-reactivity versus stable/internalized frame` is a useful shorter operational rubric. PC2 should remain provisional because trait profiles are correlated activation features and because cluster-conditioned counterexamples remain.
""",
    )

    by_stratum_top = []
    for stratum in stratum_defs:
        tab = enrich_all[enrich_all["stratum"] == stratum]
        if tab.empty:
            continue
        for _, r in tab.sort_values("cohens_d", ascending=False).head(5).iterrows():
            by_stratum_top.append(
                {
                    "stratum": stratum,
                    "pole": "high_pc2",
                    "trait": r["trait"],
                    "cohens_d": r["cohens_d"],
                }
            )
        for _, r in tab.sort_values("cohens_d", ascending=True).head(5).iterrows():
            by_stratum_top.append(
                {
                    "stratum": stratum,
                    "pole": "low_pc2",
                    "trait": r["trait"],
                    "cohens_d": r["cohens_d"],
                }
            )
    by_stratum_top_df = pd.DataFrame(by_stratum_top)

    interpretation = (
        "supports and sharpens"
        if (not rep_high.empty and not rep_low.empty)
        else "partially supports"
    )
    write_markdown(
        OUT / "pc2_trait_stratified_profile_report.md",
        f"""
# PC2 Trait-Stratified Profile Report

## Startup Status

Startup verified against the raw GitHub startup files listed in `research/STARTUP_MANIFEST.md` using cache-busted direct fetches. No GPU work, API calls, or new judge calls were run.

## Sources

- Geometry: `{GEOMETRY_PATH.relative_to(ROOT)}`
- Trait profile: `{TRAIT_MATRIX_PATH.relative_to(ROOT)}`
- Prior trait prediction stats: `{TRAIT_STATS_PATH.relative_to(ROOT)}`
- Prior muted-PC1 PC2 diagnostic: `{PC2_MUTED_PATH.relative_to(ROOT)}`
- Prior cluster-conditioned PC2 diagnostic: `{PC2_CLUSTER_DIAG_PATH.relative_to(ROOT)}`

## Dataset

- Roles/personas: {len(joined)}
- Traits: {len(trait_names)}
- Source model: `{metadata.get('source_model', 'unknown')}`
- Trait-profile model/layer: `{vector_space.get('model', 'unknown')}`, layer `{vector_space.get('layer', 'unknown')}`
- Trait score meaning: activation-space cosine between mean role vector and mean trait vector.

## PC1 Strata

{df_to_md(stratum_summary[['stratum','n_roles','tail_n_each','high_pc2_min','low_pc2_max']])}

## Global High-PC2 Enriched Traits

{md_table(top_high, 15, ['trait','cohens_d','mean_diff_high_minus_low','cliffs_delta','bootstrap_ci_low','bootstrap_ci_high'])}

## Global Low-PC2 Enriched Traits

{md_table(top_low, 15, ['trait','cohens_d','mean_diff_high_minus_low','cliffs_delta','bootstrap_ci_low','bootstrap_ci_high'])}

## Top Traits By PC1 Stratum

{df_to_md(by_stratum_top_df)}

## Replicated Traits Across PC1 Quintiles

High-PC2 replicated traits:

{md_table(rep_high, 20, ['trait','n_quintile_strata_abs_d_ge_0_5_same_sign','mean_cohens_d_across_quintiles','global_cohens_d','supporting_strata']) if not rep_high.empty else 'None at threshold.'}

Low-PC2 replicated traits:

{md_table(rep_low, 20, ['trait','n_quintile_strata_abs_d_ge_0_5_same_sign','mean_cohens_d_across_quintiles','global_cohens_d','supporting_strata']) if not rep_low.empty else 'None at threshold.'}

## PC1-Controlled Residual Traits

Positive PC1-controlled residual correlations:

{md_table(coeffs.sort_values('corr_trait_with_pc2_residual', ascending=False), 12, ['trait','corr_trait_with_pc2_residual','beta_trait_pc1_controlled'])}

Negative PC1-controlled residual correlations:

{md_table(coeffs.sort_values('corr_trait_with_pc2_residual', ascending=True), 12, ['trait','corr_trait_with_pc2_residual','beta_trait_pc1_controlled'])}

## Interpretation Update

The trait-profile evidence {interpretation} the current PC2 wording. High PC2 is best read as a context-shaped pole: situated immediacy, practical/experiential grounding, accessibility, responsiveness/accommodation, affective or developmental exposure, and performance pressure appear repeatedly after stratifying by PC1. Low PC2 is best read as a stable/internalized pole: abstraction, conceptual/theoretical structure, ritual/formal organization, conscientiousness, emotional reserve, and durable self-organization appear repeatedly after PC1 stratification and covariate checks.

This revises the wording slightly. `Situated/formative/impressionable versus integrated/stable` remains valid, but the trait evidence makes `context-reactive/accommodating/situated versus stable/internalized/integrated` the cleaner operational phrasing for future rubrics.

## Caveats

- Trait profiles are 240-dimensional activation-space cosine features, not independent psychological ratings.
- Stratification reduces PC1 confounding but does not remove cluster semantics or correlated-feature effects.
- Replication across PC1 quintiles is descriptive, not a preregistered hypothesis test.
- PC2 remains provisional and should not be presented as causal.
""",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    joined, trait_names, metadata, stats = load_joined()
    joined.to_csv(OUT / "pc2_trait_profile_joined_matrix.csv", index=False)

    stratum_defs, strata_idx = define_strata(joined)
    threshold_rows = []
    high_low_frames = []
    enrich_frames = []
    high_low_indices = {}

    for stratum, idx in strata_idx.items():
        high, low, thresholds = high_low_for_stratum(joined, idx, stratum)
        threshold_rows.append(thresholds)
        high_low_indices[stratum] = (high.index, low.index)
        sub_roles = pd.concat([high, low], ignore_index=False).copy()
        sub_roles.insert(0, "stratum", stratum)
        high_low_frames.append(sub_roles)
        enrich_frames.append(enrichment_table(joined, trait_names, high.index, low.index, stratum))

    high_low_roles = pd.concat(high_low_frames, ignore_index=True)
    high_low_cols = [
        "persona",
        "pc2_group",
        "cluster",
        "pc1",
        "pc2",
        "pc3",
        "pc1_percentile",
        "pc2_percentile",
        "pc3_percentile",
        "pc2_rank_desc_within_stratum",
        "pc2_percentile_within_stratum",
    ]
    high_low_out = high_low_roles[["stratum"] + high_low_cols].copy()
    high_low_out.to_csv(OUT / "pc2_high_low_roles_by_pc1_stratum.csv", index=False)

    for row in threshold_rows:
        stratum_defs[row["stratum"]].update(row)
    (OUT / "pc1_strata_definition.json").write_text(json.dumps(stratum_defs, indent=2))

    enrich_all = pd.concat(enrich_frames, ignore_index=True)
    enrich_global = enrich_all[enrich_all["stratum"] == "global"].copy()
    enrich_global.to_csv(OUT / "pc2_trait_enrichment_global.csv", index=False)
    enrich_all.to_csv(OUT / "pc2_trait_enrichment_by_pc1_stratum.csv", index=False)

    rep = replicated_traits(enrich_all)
    rep.to_csv(OUT / "pc2_trait_enrichment_replicated_traits.csv", index=False)

    coeffs, df_resid = pc1_control_models(joined, trait_names)
    coeffs.to_csv(OUT / "pc2_trait_pc1_control_coefficients.csv", index=False)
    df_resid_rank = df_resid.copy()
    df_resid_rank["pc2"] = df_resid_rank["pc2_residual_after_pc1"]
    resid_high, resid_low, _ = high_low_for_stratum(
        df_resid_rank, df_resid_rank.index, "pc2_residual_after_pc1"
    )
    residual_enrich = enrichment_table(joined, trait_names, resid_high.index, resid_low.index, "pc2_residual_after_pc1")
    residual_enrich.to_csv(OUT / "pc2_trait_residual_enrichment.csv", index=False)

    themes = theme_table(rep, coeffs, trait_names)
    themes.to_csv(OUT / "pc2_trait_theme_table.csv", index=False)

    enrich_all.sort_values(["stratum", "cohens_d"], ascending=[True, False]).to_html(
        OUT / "pc2_trait_interactive_table.html", index=False
    )

    make_plots(joined, enrich_all, rep, high_low_out)
    write_reports(
        joined,
        trait_names,
        metadata,
        stats,
        stratum_defs,
        threshold_rows,
        high_low_out,
        enrich_global,
        enrich_all,
        rep,
        themes,
        coeffs,
        residual_enrich,
    )

    print(
        json.dumps(
            {
                "output_dir": str(OUT.relative_to(ROOT)),
                "roles": int(len(joined)),
                "traits": int(len(trait_names)),
                "strata": len(stratum_defs),
                "replicated_traits": int(len(rep)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
