#!/usr/bin/env python3
"""Create a descriptive occupation-prevalence overlay for Qwen persona geometry."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "outputs" / "occupation_prevalence_geometry_overlay"
SRC = ROOT / "research" / "outputs" / "occupation_population_persona_join"
OUT.mkdir(parents=True, exist_ok=True)

CLUSTER_COLORS = {
    "procedural_professional": "#2878b5",
    "editorial": "#5f4690",
    "grounded_social": "#4daf4a",
    "mythic_spiritual": "#984ea3",
    "trickster_chaos": "#e41a1c",
    "combative_iconoclast": "#ff7f00",
    "other": "#777777",
}
MATCH_SYMBOLS = {"exact": "circle", "close": "diamond", "broad": "square"}


def fmt_num(x):
    if pd.isna(x):
        return "missing"
    return f"{int(round(float(x))):,}"


def point_size(series: pd.Series) -> pd.Series:
    log_emp = series.fillna(series.dropna().min() if series.notna().any() else 1)
    if log_emp.max() == log_emp.min():
        return pd.Series(np.full(len(log_emp), 18), index=series.index)
    return 10 + 32 * (log_emp - log_emp.min()) / (log_emp.max() - log_emp.min())


def make_hover(df: pd.DataFrame) -> list[str]:
    hovers = []
    for _, r in df.iterrows():
        hovers.append(
            "<br>".join(
                [
                    f"<b>{r['role']}</b>",
                    f"Occupation: {r.get('matched_occupation_title', '')}",
                    f"SOC: {r.get('soc_code', '')}",
                    f"Match: {r.get('match_class', '')}",
                    f"Employment: {fmt_num(r.get('employment_count'))}",
                    f"Median wage: {fmt_num(r.get('annual_median_wage'))}",
                    f"Cluster: {r.get('cluster', '')}",
                    f"PC1: {r['pc1']:.2f}",
                    f"PC2: {r['pc2']:.2f}",
                    f"PC3: {r['pc3']:.2f}",
                    f"Rationale: {r.get('rationale', '')}",
                ]
            )
        )
    return hovers


def main() -> None:
    qwen = pd.read_csv(ROOT / "research" / "geometry_tables" / "qwen_role_pc_rankings.csv")
    mapping = pd.read_csv(SRC / "role_occupation_mapping.csv")
    joined = qwen.merge(mapping, on="role", how="left")
    joined["match_class"] = joined["match_class"].fillna("no_match")
    joined["employment_present"] = joined["employment_count"].notna()
    joined["cluster_color"] = joined["cluster"].map(CLUSTER_COLORS).fillna("#999999")

    exact_close = joined[joined["match_class"].isin(["exact", "close"])].copy()
    exact_close_broad = joined[joined["match_class"].isin(["exact", "close", "broad"])].copy()
    primary = exact_close.copy()
    primary["plot_size"] = point_size(primary["log_employment_count"])
    exact_close_broad["plot_size"] = point_size(exact_close_broad["log_employment_count"])

    table_cols = [
        "role",
        "matched_occupation_title",
        "soc_code",
        "match_class",
        "employment_count",
        "annual_median_wage",
        "cluster",
        "pc1",
        "pc2",
        "pc3",
        "axis_projection",
        "rationale",
    ]
    table = (
        exact_close[table_cols]
        .sort_values(["employment_count", "role"], ascending=[False, True], na_position="last")
        .reset_index(drop=True)
    )
    table.to_csv(OUT / "occupation_prevalence_geometry_table.csv", index=False)

    cluster_summary = (
        exact_close.groupby("cluster")
        .agg(
            exact_close_roles=("role", "count"),
            roles_with_employment=("employment_count", lambda s: int(s.notna().sum())),
            total_employment_count=("employment_count", "sum"),
            median_employment_count=("employment_count", "median"),
            median_annual_wage=("annual_median_wage", "median"),
            median_pc1=("pc1", "median"),
            median_pc2=("pc2", "median"),
            median_pc3=("pc3", "median"),
        )
        .reset_index()
        .sort_values("exact_close_roles", ascending=False)
    )
    cluster_summary.to_csv(OUT / "occupation_prevalence_cluster_summary.csv", index=False)

    # Interactive Plotly overlay.
    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=joined["pc1"],
            y=joined["pc2"],
            mode="markers",
            name="all roles background",
            marker=dict(size=5, color="#d0d0d0", opacity=0.35),
            text=joined["role"],
            hovertemplate="<b>%{text}</b><br>PC1=%{x:.2f}<br>PC2=%{y:.2f}<extra></extra>",
        )
    )

    trace_indices_exact_close = []
    trace_indices_broad = []
    for match_class in ["exact", "close", "broad"]:
        df = exact_close_broad[exact_close_broad["match_class"] == match_class].copy()
        if df.empty:
            continue
        df["plot_size"] = point_size(exact_close_broad["log_employment_count"]).reindex(df.index)
        missing = ~df["employment_present"]
        for missing_flag, suffix in [(False, ""), (True, " missing employment")]:
            sdf = df[missing == missing_flag].copy()
            if sdf.empty:
                continue
            visible = True if match_class in ["exact", "close"] else "legendonly"
            trace_index = len(fig.data)
            if match_class in ["exact", "close"]:
                trace_indices_exact_close.append(trace_index)
            else:
                trace_indices_broad.append(trace_index)
            fig.add_trace(
                go.Scattergl(
                    x=sdf["pc1"],
                    y=sdf["pc2"],
                    mode="markers",
                    name=f"{match_class}{suffix}",
                    visible=visible,
                    marker=dict(
                        size=sdf["plot_size"] if not missing_flag else 13,
                        color=sdf["cluster_color"],
                        symbol="x" if missing_flag else MATCH_SYMBOLS[match_class],
                        opacity=0.9,
                        line=dict(color="#111111", width=1.0),
                    ),
                    text=make_hover(sdf),
                    hovertemplate="%{text}<extra></extra>",
                )
            )

    # Buttons control broad traces while keeping background and exact/close visible.
    visible_default = [True] + [True] * len(trace_indices_exact_close) + ["legendonly"] * len(trace_indices_broad)
    visible_broad = [True] + [True] * (len(fig.data) - 1)
    fig.update_layout(
        title="Qwen PC1×PC2 occupation-prevalence overlay",
        xaxis_title="PC1",
        yaxis_title="PC2",
        template="plotly_white",
        width=1100,
        height=820,
        legend_title="Match type / missing employment",
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=1.08,
                buttons=[
                    dict(label="Exact + close", method="update", args=[{"visible": visible_default}]),
                    dict(label="Exact + close + broad", method="update", args=[{"visible": visible_broad}]),
                ],
            )
        ],
        annotations=[
            dict(
                text="Point size reflects log BLS OEWS employment count when available; x markers indicate missing employment counts. Ambiguous/unmatched roles are excluded from highlighted overlay.",
                xref="paper",
                yref="paper",
                x=0,
                y=-0.11,
                showarrow=False,
                align="left",
                font=dict(size=12),
            )
        ],
    )
    fig.write_html(OUT / "occupation_prevalence_geometry_overlay.html", include_plotlyjs=True)

    # Static SVG.
    fig2, ax = plt.subplots(figsize=(12, 9))
    ax.scatter(joined["pc1"], joined["pc2"], s=14, c="#d7d7d7", alpha=0.45, linewidths=0)
    for cluster, cdf in primary.groupby("cluster"):
        cdf = cdf.copy()
        sizes = point_size(cdf["log_employment_count"]) * 5.5
        ax.scatter(
            cdf["pc1"],
            cdf["pc2"],
            s=sizes.fillna(40),
            c=CLUSTER_COLORS.get(cluster, "#777777"),
            alpha=0.82,
            edgecolor="#222222",
            linewidth=0.7,
            label=cluster,
        )
    label_df = primary.sort_values("employment_count", ascending=False, na_position="last").head(24)
    for _, r in label_df.iterrows():
        ax.text(r["pc1"] + 0.8, r["pc2"] + 0.8, r["role"], fontsize=7)
    ax.set_title("Qwen PC1×PC2 occupation-prevalence overlay: exact + close matches")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(loc="best", fontsize=8, frameon=True)
    ax.grid(alpha=0.18)
    fig2.tight_layout()
    fig2.savefig(OUT / "occupation_prevalence_geometry_overlay.svg")
    fig2.savefig(OUT / "occupation_prevalence_geometry_overlay.png", dpi=180)
    plt.close(fig2)

    # Coverage and observations.
    mapping_counts = mapping["match_class"].value_counts().to_dict()
    exact_close_count = len(exact_close)
    exact_close_with_employment = int(exact_close["employment_count"].notna().sum())
    exact_close_with_wage = int(exact_close["annual_median_wage"].notna().sum())
    top_roles = table.head(12)
    top_cluster = cluster_summary.sort_values("total_employment_count", ascending=False).head(5)

    report = f"""# Occupation-Prevalence Geometry Overlay

## Overview

This visualization is a descriptive follow-up to the occupation-population join. It overlays exact and close occupation-matched persona roles on Qwen PC1×PC2 geometry, with highlighted point size reflecting log U.S. occupational employment count where BLS OEWS values were available.

This is not a broad predictive claim. It is an inspection layer for seeing where common matched occupations sit in persona space.

## Data Coverage

- Geometry source: `research/geometry_tables/qwen_role_pc_rankings.csv`.
- Occupation source inherited from prior audit: BLS OEWS May 2025 national cross-industry estimates via `research/outputs/occupation_population_persona_join/`.
- Role mapping source: `research/outputs/occupation_population_persona_join/role_occupation_mapping.csv`.
- Total roles in background geometry: {len(joined)}
- Exact matches: {mapping_counts.get('exact', 0)}
- Close matches: {mapping_counts.get('close', 0)}
- Broad matches available only in optional view: {mapping_counts.get('broad', 0)}
- Ambiguous mappings excluded from overlay: {mapping_counts.get('ambiguous', 0)}
- Unmatched roles excluded from highlighted overlay: {mapping_counts.get('no_match', 0)}
- Exact+close highlighted roles: {exact_close_count}
- Exact+close roles with employment counts: {exact_close_with_employment}
- Exact+close roles with annual median wage: {exact_close_with_wage}

## Visual Observations

### Observed

- High-employment exact/close roles are not spread uniformly across the map. The largest returned employment counts include `caregiver`, `secretary`, `accountant`/`auditor`, `recruiter`, `consultant`, and `lawyer`.
- Common service/administrative occupations such as `caregiver` and `secretary` sit closer to grounded-social or assistant-adjacent/procedural territory than mythic or trickster territory.
- Highly differentiated professional roles such as `accountant`, `auditor`, `lawyer`, and `consultant` appear on the high-PC1/procedural side, but the overlay also contains creative/media occupations outside that region.
- The exact+close overlay is visibly cluster-skewed because the role inventory contains many professional and media roles but many nonmodern/archetypal roles are intentionally unmatched.

### Inferred

- Weak global correlations can coexist with visually interesting regional concentration: the prior correlation table asks whether employment count tracks PCs linearly, while this overlay shows where a filtered subset of occupational roles lands in the geometry.
- The descriptive pattern is more useful as a coverage and territory-inspection tool than as evidence for a labor-demographic explanation of persona geometry.

### Speculative

- A stronger future analysis might compare OEWS employment counts with web-text frequency, O*NET descriptors, credentialing level, public-contact level, and institutional procedure intensity.

### Unknown

- Whether occupational employment count approximates role salience in model pretraining, user-query frequency, or prompt artifact frequency. This overlay does not measure any of those.

## Top Employment Exact/Close Roles

{top_roles[['role','matched_occupation_title','soc_code','match_class','employment_count','annual_median_wage','cluster','pc1','pc2']].to_string(index=False)}

## Cluster-Level Summary

{top_cluster[['cluster','exact_close_roles','roles_with_employment','total_employment_count','median_employment_count','median_annual_wage','median_pc1','median_pc2']].to_string(index=False)}

## Answer to Prompted Questions

1. Common matched occupations sit mainly in grounded-social, procedural-professional, and editorial/assistant-adjacent territories, with creative/media roles forming a visible secondary spread.
2. High-employment occupations visually concentrate more in grounded-social and procedural/administrative regions than in mythic/spiritual or trickster regions, but missing BLS values limit the claim.
3. Differentiated professional roles are overrepresented in high-PC1 procedural territory, especially accounting/auditing, law, consulting, and administrative/professional roles.
4. Common lower-degree or service occupations are underrepresented in the role inventory relative to the U.S. labor market, but available examples such as caregiver/secretary/bartender/paramedic tend toward grounded-social or service-adjacent regions when present.
5. The visual pattern differs from the weak global correlation result because the overlay emphasizes regional concentration of a filtered subset rather than linear PC-wide prediction.
6. The useful future-work question is whether occupational institutionalization, credentialing, public-contact intensity, or text/corpus frequency explains more than employment count alone.

## Caveats

- Do not claim persona geometry reflects U.S. labor demographics.
- Do not treat BLS employment count as training-corpus frequency.
- Do not infer prevalence for unmatched archetypal roles.
- Ambiguous and unmatched roles are excluded from the primary overlay.
- This belongs outside Paper 1.5 core evidence; at most it is a future-work note or appendix visualization.
"""
    (OUT / "occupation_prevalence_overlay_report.md").write_text(report)

    artifacts = [
        ("occupation_prevalence_geometry_overlay.html", "interactive HTML overlay", "active"),
        ("occupation_prevalence_geometry_overlay.svg", "static SVG overlay", "active"),
        ("occupation_prevalence_geometry_overlay.png", "static PNG overlay", "active"),
        ("occupation_prevalence_geometry_table.csv", "exact+close sorted role table", "active"),
        ("occupation_prevalence_cluster_summary.csv", "exact+close cluster summary", "active"),
        ("occupation_prevalence_overlay_report.md", "interpretation report", "active"),
        ("artifact_inventory.csv", "artifact inventory", "active"),
        ("run_occupation_prevalence_geometry_overlay.py", "generation script", "active"),
    ]
    with (OUT / "artifact_inventory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["artifact", "description", "status", "path"])
        writer.writeheader()
        for artifact, desc, status in artifacts:
            writer.writerow({"artifact": artifact, "description": desc, "status": status, "path": str((OUT / artifact).relative_to(ROOT))})

    print(
        json.dumps(
            {
                "output_dir": str(OUT.relative_to(ROOT)),
                "exact_close_roles": exact_close_count,
                "exact_close_with_employment": exact_close_with_employment,
                "broad_optional_roles": int((joined["match_class"] == "broad").sum()),
                "html": str((OUT / "occupation_prevalence_geometry_overlay.html").relative_to(ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
