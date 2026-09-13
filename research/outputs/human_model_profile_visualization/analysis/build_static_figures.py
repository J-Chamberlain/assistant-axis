#!/usr/bin/env python3
"""Build the AA-12 frozen correspondence inspection figures.

All plotted values come from figure-ready tables frozen by
extract_visualization_data.py. No correspondence fitting, matching, or null
generation occurs here.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = OUT / "data"
FIG = OUT / "figures"
SOURCE_FIG = REPO / "research/outputs/human_model_profile_correspondence/figures"

FAMILY_ORDER = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
FAMILY_SHORT = {f"MFamily_{x}": x for x in "ABCDE"}
FAMILY_COLORS = {
    "MFamily_A": "#1878b4",
    "MFamily_B": "#d99100",
    "MFamily_C": "#009c76",
    "MFamily_D": "#e06b00",
    "MFamily_E": "#7a5195",
}
HUMAN_COLOR = "#222b45"
MODEL_COLOR = "#d1495b"
STABILITY_COLORS = {"moderate": "#27856f", "low": "#c65f3b"}

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "xtick.labelsize": 8,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.facecolor": "white",
        "axes.facecolor": "#fbfbfc",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.facecolor": "white",
        "svg.hashsalt": "aa12-followup5-frozen-visualization",
    }
)
sns.set_theme(style="whitegrid", rc={"grid.color": "#e7e7ea", "grid.linewidth": 0.7})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_both(fig: plt.Figure, stem: str, png_dpi: int = 190) -> list[Path]:
    FIG.mkdir(parents=True, exist_ok=True)
    paths = [FIG / f"{stem}.png", FIG / f"{stem}.svg"]
    fig.savefig(
        paths[0],
        dpi=png_dpi,
        bbox_inches="tight",
        metadata={"Software": "AA-12 frozen visualization packet"},
    )
    fig.savefig(
        paths[1],
        bbox_inches="tight",
        metadata={"Date": "2026-09-13", "Creator": "AA-12 frozen visualization packet"},
    )
    plt.close(fig)
    return paths


def core_labels(traits: list[str], core: set[str]) -> list[str]:
    return [f"{t} •" if t in core else t for t in traits]


def primary_shapes(order_col: str, stem: str, title_suffix: str) -> list[Path]:
    d = pd.read_csv(DATA / "primary_matched_profile_shapes.csv").sort_values(
        ["model_family_id", order_col]
    )
    traits = (
        d[d.model_family_id.eq("MFamily_A")]
        .sort_values(order_col)
        .trait.tolist()
    )
    core = set(d[d.is_12_trait_core].trait)
    fig, axes = plt.subplots(4, 1, figsize=(18, 12.5), sharex=True, sharey=True)
    for ax, fam in zip(axes, FAMILY_ORDER):
        g = d[d.model_family_id.eq(fam)].sort_values(order_col)
        x = np.arange(len(g))
        ax.axhline(0, color="#8c8c92", lw=0.8)
        ax.plot(x, g.human_value, color=HUMAN_COLOR, lw=2.0, marker="o", ms=3.2, label=f"Human {g.human_profile_id.iloc[0]}")
        ax.plot(x, g.model_consensus_value, color=FAMILY_COLORS[fam], lw=2.0, marker="s", ms=3.0, label=f"{fam} consensus")
        ax.set_ylabel("standardized\nprofile value")
        ax.set_title(
            f"{fam} ↔ {g.human_profile_id.iloc[0]}  |  Pearson r={g.pair_pearson_r.iloc[0]:.3f}; Spearman ρ={g.pair_spearman_rho.iloc[0]:.3f}",
            loc="left",
            fontweight="bold",
        )
        ax.legend(loc="upper right", frameon=False, ncol=2)
    axes[-1].set_xticks(np.arange(len(traits)))
    axes[-1].set_xticklabels(core_labels(traits, core), rotation=65, ha="right", fontsize=7.5)
    axes[-1].set_xlabel("Frozen shared trait (• = 12-trait conservative core)")
    fig.suptitle(f"Primary K=10 matched profile shapes — {title_suffix}", fontsize=18, fontweight="bold", y=1.005)
    fig.text(0.5, -0.005, "r measures similarity of the relative 45-trait profile shape; it is not identity, prevalence, or equivalence.", ha="center", fontsize=10)
    fig.tight_layout()
    return save_both(fig, stem)


def trait_decomposition() -> list[Path]:
    d = pd.read_csv(DATA / "primary_matched_profile_shapes.csv")
    meta = pd.read_csv(DATA / "trait_metadata.csv").sort_values("canonical_order")
    traits = meta.trait.tolist()
    core = set(meta[meta.is_12_trait_core].trait)
    contrib = d.pivot(index="model_family_id", columns="trait", values="covariance_contribution").loc[FAMILY_ORDER, traits]
    diff = d.pivot(index="model_family_id", columns="trait", values="signed_difference_human_minus_model").loc[FAMILY_ORDER, traits]
    fig, axes = plt.subplots(2, 1, figsize=(18, 6.8), sharex=True)
    lim1 = np.nanmax(np.abs(contrib.to_numpy()))
    lim2 = np.nanmax(np.abs(diff.to_numpy()))
    sns.heatmap(contrib, ax=axes[0], cmap="vlag", center=0, vmin=-lim1, vmax=lim1, cbar_kws={"label": "centered covariance contribution"})
    sns.heatmap(diff, ax=axes[1], cmap="vlag", center=0, vmin=-lim2, vmax=lim2, cbar_kws={"label": "human − model"})
    axes[0].set_title("Trait contribution to frozen pairwise profile covariance", loc="left", fontweight="bold")
    axes[1].set_title("Signed standardized disagreement", loc="left", fontweight="bold")
    for ax in axes:
        ax.set_ylabel("")
        ax.set_yticklabels([FAMILY_SHORT[x] for x in FAMILY_ORDER], rotation=0)
    axes[0].set_xticklabels([])
    axes[1].set_xticklabels(core_labels(traits, core), rotation=65, ha="right", fontsize=7.3)
    axes[1].set_xlabel("Frozen shared trait (• = 12-trait core)")
    fig.suptitle("Where the four primary correspondences agree—and disagree", fontsize=18, fontweight="bold", y=1.02)
    fig.text(0.5, -0.02, "Per-trait contributions are descriptive decomposition terms, not independent hypothesis tests.", ha="center", fontsize=10)
    fig.tight_layout()
    return save_both(fig, "02_trait_decomposition_all_traits")


def top_driver_figure() -> list[Path]:
    d = pd.read_csv(DATA / "top_trait_drivers.csv")
    fig, axes = plt.subplots(4, 2, figsize=(15, 15))
    for row_idx, fam in enumerate(FAMILY_ORDER):
        pos = d[(d.model_family_id.eq(fam)) & (d.driver_type.eq("top_positive_covariance_contribution"))].sort_values("rank", ascending=False)
        dis = d[(d.model_family_id.eq(fam)) & (d.driver_type.eq("top_absolute_disagreement"))].sort_values("rank", ascending=False)
        ax = axes[row_idx, 0]
        ax.barh(pos.trait, pos.covariance_contribution, color=FAMILY_COLORS[fam], alpha=.85)
        ax.set_title(f"{FAMILY_SHORT[fam]}: strongest positive covariance contributors", loc="left", fontweight="bold")
        ax.set_xlabel("centered product")
        ax = axes[row_idx, 1]
        colors = np.where(dis.signed_difference_human_minus_model >= 0, "#4267ac", "#d1495b")
        ax.barh(dis.trait, dis.absolute_difference, color=colors, alpha=.85)
        ax.set_title(f"{FAMILY_SHORT[fam]}: largest |human − model| differences", loc="left", fontweight="bold")
        ax.set_xlabel("absolute standardized difference")
    fig.suptitle("Top trait-level drivers and disagreements in the primary K=10 pairs", fontsize=18, fontweight="bold", y=1.01)
    fig.text(.75, .004, "Blue: human higher; red: model higher", ha="center", fontsize=9)
    fig.tight_layout()
    return save_both(fig, "02b_top_trait_drivers")


def paired_heatmap() -> list[Path]:
    d = pd.read_csv(DATA / "primary_matched_profile_shapes.csv")
    meta = pd.read_csv(DATA / "trait_metadata.csv").sort_values("canonical_order")
    traits = meta.trait.tolist(); core = set(meta[meta.is_12_trait_core].trait)
    rows, labels = [], []
    for fam in FAMILY_ORDER:
        g = d[d.model_family_id.eq(fam)].set_index("trait").loc[traits]
        rows.extend([g.model_consensus_value.to_numpy(), g.human_value.to_numpy()])
        labels.extend([f"{FAMILY_SHORT[fam]} model", f"{g.human_profile_id.iloc[0]} human"])
    matrix = np.vstack(rows)
    lim = np.nanmax(np.abs(matrix))
    fig, ax = plt.subplots(figsize=(18, 6.2))
    sns.heatmap(matrix, cmap="vlag", center=0, vmin=-lim, vmax=lim, ax=ax, yticklabels=labels, xticklabels=core_labels(traits, core), cbar_kws={"label": "standardized profile value"})
    for y in [2, 4, 6]: ax.axhline(y, color="black", lw=1.5)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=65, ha="right", fontsize=7.2)
    ax.set_title("Primary pairs in one shared 45-trait view", fontsize=18, fontweight="bold", loc="left")
    ax.set_xlabel("Frozen shared trait (• = 12-trait core)")
    ax.set_ylabel("")
    fig.tight_layout()
    return save_both(fig, "03_primary_pair_heatmap")


def k_progression_figure() -> list[Path]:
    d = pd.read_csv(DATA / "k_progression.csv").sort_values("K")
    eligible = d[d.included_in_primary]
    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    first = eligible[eligible.K <= 8]
    ax.plot(first.K, first.back_transformed_mean_r, color="#455a7a", lw=2.4, zorder=1)
    k8 = eligible[eligible.K.eq(8)].iloc[0]; k10 = eligible[eligible.K.eq(10)].iloc[0]
    ax.plot([8, 10], [k8.back_transformed_mean_r, k10.back_transformed_mean_r], color="#455a7a", lw=2.0, ls="--", zorder=1)
    for _, row in eligible.iterrows():
        ax.scatter(row.K, row.back_transformed_mean_r, s=110, color=STABILITY_COLORS[row.human_stability], edgecolor="white", linewidth=1.2, zorder=3)
        ax.text(row.K, row.back_transformed_mean_r + .018, f"{row.back_transformed_mean_r:.3f}", ha="center", fontsize=9)
    diag = d[d.K.eq(9)].iloc[0]
    ax.scatter(9, diag.back_transformed_mean_r, marker="X", s=125, color="#777777", zorder=4)
    ax.text(9, diag.back_transformed_mean_r - .055, "K9 diagnostic / ineligible", ha="center", fontsize=8, color="#555")
    ax.annotate("BIC/ICL anchor", (4, eligible[eligible.K.eq(4)].back_transformed_mean_r.iloc[0]), xytext=(4.2,.31), arrowprops={"arrowstyle":"->","color":"#555"})
    ax.annotate("predictive anchor + primary max", (10, k10.back_transformed_mean_r), xytext=(8.1,.575), arrowprops={"arrowstyle":"->","color":"#555"})
    ax.text(8.95, .37, "dashed gap: K9 excluded", ha="center", fontsize=8, color="#555")
    ax.set_xticks([4,5,6,7,8,9,10]); ax.set_ylim(.2,.63)
    ax.set_xlabel("Human latent-profile resolution K")
    ax.set_ylabel("injective-assignment back-transformed mean r")
    ax.set_title("Frozen aggregate correspondence across human K", fontsize=18, fontweight="bold", loc="left")
    handles = [mpl.lines.Line2D([],[],marker='o',ls='',color=c,label=f"{s} split-refit stability") for s,c in STABILITY_COLORS.items()]
    handles.append(mpl.lines.Line2D([],[],marker='X',ls='',color="#777",label="diagnostic / ineligible"))
    ax.legend(handles=handles, frameon=False, loc="upper left")
    fig.tight_layout()
    return save_both(fig, "04_k_progression")


def family_best_figure() -> list[Path]:
    d = pd.read_csv(DATA / "family_best_by_k.csv")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True, sharey=True)
    for ax, fam in zip(axes.flat, FAMILY_ORDER):
        g = d[d.model_family_id.eq(fam)].sort_values("K")
        ax.plot(g.K, g.best_pearson_r, marker="o", lw=2.2, color=FAMILY_COLORS[fam])
        for _, row in g.iterrows():
            ax.text(row.K, row.best_pearson_r + .025, row.best_human_profile_id, ha="center", fontsize=8)
        p = g.family_specific_search_adjusted_p_over_all_K_profiles.iloc[0]
        status = "passes" if g.passes_frozen_p05.iloc[0] else "marginal / does not pass"
        ax.set_title(f"{fam}: adjusted p={p:.6f} ({status})", loc="left", fontweight="bold")
        ax.axhline(0, color="#888", lw=.8)
        ax.set_xticks([4,5,6,7,8,10])
        ax.set_ylim(-.05,.82)
    for ax in axes[:,0]: ax.set_ylabel("best available Pearson r")
    for ax in axes[-1,:]: ax.set_xlabel("Human K")
    fig.suptitle("Best available human-profile similarity by model family", fontsize=18, fontweight="bold", y=1.01)
    fig.text(.5,.005,"Unconstrained family maxima; these are not the injective primary assignments.",ha="center",fontsize=10)
    fig.tight_layout()
    return save_both(fig, "05_family_best_across_k")


def assignment_evolution_figure() -> list[Path]:
    d = pd.read_csv(DATA / "assignment_evolution.csv")
    k_order = [4,5,6,7,8,10]
    value = d.pivot(index="model_family_id", columns="K", values="pearson_r").loc[FAMILY_ORDER, k_order]
    annot = np.empty(value.shape, dtype=object)
    for i, fam in enumerate(FAMILY_ORDER):
        for j, k in enumerate(k_order):
            row = d[(d.model_family_id.eq(fam)) & (d.K.eq(k))].iloc[0]
            best_note = "" if row.assignment_equals_unconstrained_best else f"\nbest {row.best_human_profile_id}"
            annot[i,j] = f"{row.human_profile_id}\nr={row.pearson_r:.2f}{best_note}"
    fig, ax = plt.subplots(figsize=(12, 5.3))
    sns.heatmap(value, cmap="vlag", center=0, vmin=-.1, vmax=.8, annot=annot, fmt="", linewidths=1.5, linecolor="white", cbar_kws={"label":"assigned Pearson r"}, ax=ax)
    ax.set_yticklabels([FAMILY_SHORT[x] for x in FAMILY_ORDER], rotation=0)
    ax.set_xlabel("Human K (K8→K10 gap omits ineligible K9)"); ax.set_ylabel("Frozen model family")
    ax.set_title("Evolution of the frozen injective assignment", fontsize=18, fontweight="bold", loc="left")
    fig.text(.5,.005,"Cell IDs are assigned human profiles. ‘best’ flags an unconstrained family maximum displaced by injectivity; this is not respondent lineage.",ha="center",fontsize=9)
    fig.tight_layout()
    return save_both(fig, "06_assignment_evolution_matrix")


def reuse_frozen_figure(source_name: str, target_name: str) -> tuple[Path, str]:
    src = SOURCE_FIG / source_name
    dst = FIG / target_name
    shutil.copyfile(src, dst)
    if sha256(src) != sha256(dst):
        raise AssertionError(f"Copied figure hash mismatch: {source_name}")
    return dst, sha256(dst)


def similarity_heatmaps() -> list[Path]:
    d = pd.read_csv(DATA / "full_similarity_matrices.csv")
    paths: list[Path] = []
    for k in [4,5,6,7,8,10]:
        g = d[d.K.eq(k)]
        profiles = sorted(g.human_profile_id.unique())
        families = ["MFamily_A","MFamily_B","MFamily_C","MFamily_D","MFamily_E"]
        matrix = g.pivot(index="human_profile_id", columns="model_family_id", values="pearson_r").loc[profiles, families]
        annotations = np.empty(matrix.shape, dtype=object)
        for i,hp in enumerate(profiles):
            for j,fam in enumerate(families):
                row=g[(g.human_profile_id.eq(hp))&(g.model_family_id.eq(fam))].iloc[0]
                marks=""
                if row.is_primary_injective_assignment: marks += "●"
                if row.is_unconstrained_family_best_at_K: marks += "▲"
                annotations[i,j]=f"{row.pearson_r:.2f}{marks}"
        ylabels=[]
        for hp in profiles:
            amb=bool(g[g.human_profile_id.eq(hp)].human_profile_has_ambiguous_top_two_margin.iloc[0])
            ylabels.append(hp + (" †" if amb else ""))
        fig,ax=plt.subplots(figsize=(8.6, max(5.0,.58*len(profiles)+2.2)))
        sns.heatmap(matrix,cmap="vlag",center=0,vmin=-.8,vmax=.8,annot=annotations,fmt="",linewidths=.7,linecolor="white",yticklabels=ylabels,xticklabels=["A","B","C","D","E secondary"],cbar_kws={"label":"45-trait Pearson r"},ax=ax)
        ax.axvline(4,color="black",lw=2)
        ax.set_title(f"Human × model-family profile similarity — K={k}",fontsize=17,fontweight="bold",loc="left")
        ax.set_xlabel("Frozen model consensus family"); ax.set_ylabel("Frozen human profile")
        fig.text(.5,.005,"● primary injective assignment  ▲ unconstrained best at this K  † human profile has frozen top-two ambiguity; E is secondary.",ha="center",fontsize=8.5)
        fig.tight_layout()
        paths.extend(save_both(fig,f"08_similarity_matrix_k{k:02d}"))
    return paths


def cde_figure() -> list[Path]:
    comp=pd.read_csv(DATA/"cde_competition.csv")
    shapes=pd.read_csv(DATA/"cde_profile_shapes.csv")
    fams=["MFamily_C","MFamily_D","MFamily_E"]
    order=(comp.groupby("human_profile_id").pearson_r.max().sort_values(ascending=False).index.tolist())
    matrix=comp.pivot(index="human_profile_id",columns="model_family_id",values="pearson_r").loc[order,fams]
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(18,11),gridspec_kw={"height_ratios":[1,2.2]})
    sns.heatmap(matrix,cmap="vlag",center=0,vmin=-.8,vmax=.8,annot=True,fmt=".2f",linewidths=1,linecolor="white",cbar_kws={"label":"Pearson r"},ax=ax1)
    ax1.set_title("C/D/E correlations across the deterministically selected K=10 human region",loc="left",fontweight="bold")
    ax1.set_xlabel("E is secondary and excluded from the A–D global test"); ax1.set_ylabel("Human profile")
    canonical=shapes.sort_values("canonical_order").trait.drop_duplicates().tolist()
    x=np.arange(len(canonical))
    for profile in ["H10_I","MFamily_C","MFamily_D","MFamily_E","H10_G"]:
        g=shapes[shapes.profile_id.eq(profile)].sort_values("canonical_order")
        if profile.startswith("H"):
            color=HUMAN_COLOR if profile=="H10_I" else "#7a8699"; ls="-" if profile=="H10_I" else "--"; lw=2.4 if profile=="H10_I" else 1.2
        else:
            color=FAMILY_COLORS[profile]; ls="-"; lw=1.8
        ax2.plot(x,g.value,label=profile,color=color,ls=ls,lw=lw)
    ax2.axhline(0,color="#888",lw=.8); ax2.set_xticks(x); ax2.set_xticklabels(canonical,rotation=65,ha="right",fontsize=7.2)
    ax2.set_ylabel("standardized profile value"); ax2.set_xlabel("Frozen 45-trait bridge")
    ax2.set_title("H10_I against C, D, and E profile shapes (H10_G shown as the injective C comparator)",loc="left",fontweight="bold")
    ax2.legend(ncol=5,frameon=False,loc="upper center")
    fig.suptitle("Why C, D, and E compete for the same human-profile region",fontsize=18,fontweight="bold",y=1.01)
    fig.tight_layout()
    return save_both(fig,"09_cde_competition")


def ad_exemplar_figure() -> list[Path]:
    d=pd.read_csv(DATA/"ad_exemplars.csv")
    specs=[("MFamily_A","H10_C"),("MFamily_A","H06_A"),("MFamily_D","H10_I")]
    fig,axes=plt.subplots(3,1,figsize=(18,10.5),sharex=True,sharey=True)
    traits=d.sort_values("canonical_order").trait.drop_duplicates().tolist(); x=np.arange(len(traits))
    for ax,(fam,hp) in zip(axes,specs):
        g=d[(d.model_family_id.eq(fam))&(d.human_profile_id.eq(hp))].sort_values("canonical_order")
        ax.plot(x,g.human_value,color=HUMAN_COLOR,lw=2,marker='o',ms=3,label=hp)
        ax.plot(x,g.model_consensus_value,color=FAMILY_COLORS[fam],lw=2,marker='s',ms=3,label=fam)
        ax.axhline(0,color="#888",lw=.8); ax.legend(frameon=False,ncol=2)
        ax.set_ylabel("standardized value")
        role=g.comparison_role.iloc[0].replace('_',' ')
        ax.set_title(f"{fam} ↔ {hp}: r={g.pearson_r.iloc[0]:.3f} ({role})",loc="left",fontweight="bold")
    axes[-1].set_xticks(x); axes[-1].set_xticklabels(traits,rotation=65,ha="right",fontsize=7.2); axes[-1].set_xlabel("Frozen shared trait")
    fig.suptitle("A and D exemplars: broad family evidence versus exact assignment identity",fontsize=18,fontweight="bold",y=1.01)
    fig.tight_layout()
    return save_both(fig,"10_ad_exemplars")


def trait_set_figure() -> list[Path]:
    d=pd.read_csv(DATA/"trait_set_comparison.csv")
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14.5,6.2),gridspec_kw={"width_ratios":[1.35,1]})
    x=np.arange(4); width=.34
    for offset,(trait_set,label,color) in zip([-width/2,width/2],[
        ("45_ACCEPT_DIRECT","45 direct","#4f77b6"),("12_HUMAN_SUPPORTED","12 supported","#e1844c")]):
        g=d[d.trait_set.eq(trait_set)].set_index("model_family_id").loc[FAMILY_ORDER]
        ax1.bar(x+offset,g.selected_pearson_r,width,label=label,color=color)
        for xi,(_,row) in zip(x+offset,g.iterrows()): ax1.text(xi,row.selected_pearson_r+.025,row.selected_human_profile_id,ha="center",fontsize=8,rotation=45)
    ax1.set_xticks(x); ax1.set_xticklabels(["A","B","C","D"]); ax1.set_ylim(-.05,1.02)
    ax1.set_ylabel("selected-pair Pearson r"); ax1.set_title("Separate K=10 injective assignments",loc="left",fontweight="bold"); ax1.legend(frameon=False)
    primary=d[d.trait_set.eq("45_ACCEPT_DIRECT")].set_index("model_family_id").loc[FAMILY_ORDER]
    ax2.bar(x,primary.primary_45_pair_r_evaluated_on_12_traits,color=[FAMILY_COLORS[f] for f in FAMILY_ORDER])
    ax2.axhline(0,color="#777",lw=.8); ax2.set_xticks(x); ax2.set_xticklabels(["A","B","C","D"]); ax2.set_ylim(-.1,1.02)
    ax2.set_ylabel("same 45-trait pair, r on 12 traits"); ax2.set_title("Fixed 45-trait pairs on the 12-trait core",loc="left",fontweight="bold")
    for xi,row in zip(x,primary.itertuples()): ax2.text(xi,row.primary_45_pair_r_evaluated_on_12_traits+.025,f"{row.primary_45_pair_r_evaluated_on_12_traits:.2f}",ha="center",fontsize=9)
    fig.suptitle("Global structure persists; exact pair identity does not",fontsize=18,fontweight="bold",y=1.02)
    fig.text(.5,.005,"45 traits: mean r=0.520, search-adjusted p=0.000050. 12 traits: mean r=0.761, p=0.000650. Only A retains the same selected K10 profile.",ha="center",fontsize=9.5)
    fig.tight_layout()
    return save_both(fig,"11_trait_set_comparison")


def annotated_null_figure() -> list[Path]:
    hist=pd.read_csv(DATA/"permutation_null_histogram.csv")
    summary=pd.read_csv(DATA/"permutation_null_summary.csv").set_index("statistic").value
    fig,ax=plt.subplots(figsize=(11,6.5))
    widths=hist.bin_right-hist.bin_left
    ax.bar(hist.bin_midpoint,hist['count'],width=widths*.94,color="#92abc4",edgecolor="white")
    lines=[("median",summary.null_median,"#59636e","--"),("95%",summary.null_95th_percentile,"#8b6c42","--"),("99.9%",summary.null_99_9th_percentile,"#8b3f3f",":"),("observed",summary.observed_max_mean_fisher_z,"#c51b27","-")]
    for label,x,color,ls in lines:
        ax.axvline(x,color=color,ls=ls,lw=2.5,label=f"{label}: {x:.3f}")
    ax.set_xlabel("maximum mean Fisher-z after full assignment and eligible-K search"); ax.set_ylabel("permutation count")
    ax.set_title("Search-adjusted 45-trait bridge-permutation null",fontsize=18,fontweight="bold",loc="left")
    ax.legend(frameon=False)
    ax.text(.99,.96,"0 / 20,000 null maxima ≥ observed\nempirical p = 1 / 20,001 = 0.000050",transform=ax.transAxes,ha="right",va="top",fontsize=11,bbox={"boxstyle":"round,pad=.4","facecolor":"white","edgecolor":"#c51b27"})
    fig.text(.5,.005,"Every null draw repeated all correlations, injective assignment optimization, and the complete eligible-K search.",ha="center",fontsize=9.5)
    fig.tight_layout()
    return save_both(fig,"13_primary_permutation_null")


def family_statistics_figure() -> list[Path]:
    d=pd.read_csv(DATA/"family_specific_statistics.csv").set_index("model_family_id").loc[FAMILY_ORDER]
    x=np.arange(4); colors=[FAMILY_COLORS[f] for f in FAMILY_ORDER]
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13.5,5.8))
    ax1.bar(x,d.family_specific_best_pearson_r,color=colors); ax1.set_xticks(x); ax1.set_xticklabels(["A","B","C","D"]); ax1.set_ylim(0,.82)
    ax1.set_ylabel("strongest Pearson r across all eligible profiles/K"); ax1.set_title("Observed family-specific maxima",loc="left",fontweight="bold")
    for xi,row in zip(x,d.itertuples()): ax1.text(xi,row.family_specific_best_pearson_r+.025,f"{row.family_specific_best_human_profile}\n{row.family_specific_best_pearson_r:.3f}",ha="center",fontsize=8)
    ax2.bar(x,d.family_specific_search_adjusted_p,color=colors); ax2.axhline(.05,color="#222",ls="--",lw=1.5,label="frozen p=.05 threshold")
    ax2.set_yscale("log"); ax2.set_ylim(3e-5,.12); ax2.set_xticks(x); ax2.set_xticklabels(["A","B","C","D"]); ax2.set_ylabel("search-adjusted p (log scale)"); ax2.set_title("Adjusted max-search evidence",loc="left",fontweight="bold"); ax2.legend(frameon=False)
    for xi,row in zip(x,d.itertuples()): ax2.text(xi,row.family_specific_search_adjusted_p*1.18,f"{row.family_specific_search_adjusted_p:.5f}",ha="center",fontsize=8)
    fig.suptitle("Family-specific evidence does not imply four distinct counterparts",fontsize=18,fontweight="bold",y=1.02)
    fig.text(.5,.005,"C passes its max test but shares H10_I with D; B is marginal at p≈0.0535.",ha="center",fontsize=9.5)
    fig.tight_layout()
    return save_both(fig,"14_family_specific_statistics")


def sapa_language_figure() -> list[Path]:
    d=pd.read_csv(DATA/"sapa_language_profiles.csv")
    profiles=["H10_C","H10_J","H10_G","H10_I","H06_A"]
    item_meta=d.sort_values("visualization_order").drop_duplicates("item_id")
    items=item_meta.item_id.tolist()
    labels=[f"{row.primary_frozen_trait_owner} · {row.item_text}" for row in item_meta.itertuples()]
    matrix=d.pivot(index="item_id",columns="profile_id",values="oriented_item_z").loc[items,profiles]
    lim=max(1,float(np.nanmax(np.abs(matrix.to_numpy()))))
    fig,ax=plt.subplots(figsize=(13,26))
    sns.heatmap(matrix,cmap="vlag",center=0,vmin=-lim,vmax=lim,yticklabels=labels,xticklabels=profiles,linewidths=.25,linecolor="#eeeeee",cbar_kws={"label":"oriented item expectation in observed human SD units"},ax=ax)
    ax.set_yticklabels(ax.get_yticklabels(),rotation=0,fontsize=6.2); ax.set_xticklabels(ax.get_xticklabels(),rotation=0,fontsize=11)
    ax.set_xlabel("Frozen aggregate human profile"); ax.set_ylabel("Frozen mapped trait · exact SAPA wording")
    ax.set_title("Human profiles in SAPA’s own language — all 96 unique bridge items",fontsize=18,fontweight="bold",loc="left")
    fig.text(.5,.003,"H06_A is included because it is MFamily_A’s family-specific strongest counterpart; all values are aggregate profile expectations.",ha="center",fontsize=9)
    fig.tight_layout()
    return save_both(fig,"15_sapa_language_profiles",png_dpi=170)


def main() -> None:
    FIG.mkdir(parents=True,exist_ok=True)
    created: list[dict] = []
    def record(requirement: str, description: str, source_tables: str, paths: list[Path], provenance: str="created from frozen source table") -> None:
        for path in paths:
            created.append({
                "requirement":requirement,"figure_path":str(path.relative_to(REPO)),"format":path.suffix.lstrip('.'),
                "status":"reused" if provenance.startswith("reused") else "created",
                "source_tables":source_tables,"description":description,"provenance":provenance,
                "sha256":sha256(path),"size_bytes":path.stat().st_size,
            })

    record("Figure 1A","Primary A-D matched shapes in canonical bridge order","data/primary_matched_profile_shapes.csv; data/trait_metadata.csv",primary_shapes("canonical_order","01_primary_matched_shapes_canonical","canonical bridge order"))
    record("Figure 1B","Primary A-D matched shapes grouped by frozen human-measurement tier","data/primary_matched_profile_shapes.csv; data/trait_metadata.csv",primary_shapes("grouped_order","01b_primary_matched_shapes_measurement_grouped","frozen measurement-support grouping"))
    record("Figure 2A","All-trait covariance contribution and signed disagreement","data/primary_matched_profile_shapes.csv",trait_decomposition())
    record("Figure 2B","Top eight positive contributors and top eight disagreements per pair","data/top_trait_drivers.csv",top_driver_figure())
    record("Figure 3","Paired A-D model/human 45-trait heatmap","data/primary_matched_profile_shapes.csv",paired_heatmap())
    record("Figure 4","K progression with stability, anchors, and ineligible K9","data/k_progression.csv",k_progression_figure())
    record("Figure 5","Unconstrained best human-profile similarity by family across K","data/family_best_by_k.csv",family_best_figure())
    record("Figure 6","Injective assignment evolution matrix across eligible K","data/assignment_evolution.csv",assignment_evolution_figure())
    reused, digest = reuse_frozen_figure("cross_resolution_persistence.png","07_human_profile_continuity_reused.png")
    record("Figure 7","Frozen mutual-nearest human continuity relevant to A-D","data/human_profile_continuity.csv",[reused],f"reused byte-for-byte from research/outputs/human_model_profile_correspondence/figures/cross_resolution_persistence.png ({digest})")
    record("Figure 8","Full human × A-D plus secondary E similarity matrices","data/full_similarity_matrices.csv",similarity_heatmaps())
    record("Figure 9","C/D/E competition in K10 human-profile region","data/cde_competition.csv; data/cde_profile_shapes.csv",cde_figure())
    record("Figure 10","A primary-versus-family maximum and D exemplar","data/ad_exemplars.csv",ad_exemplar_figure())
    record("Figure 11","45-trait versus 12-trait assignments and fixed-pair sensitivity","data/trait_set_comparison.csv",trait_set_figure())
    reused, digest = reuse_frozen_figure("model_specific_replication.png","12_model_specific_replication_reused.png")
    record("Figure 12","Fixed-pair consensus/Qwen/LLaMA/Gemma replication","data/model_specific_replication.csv",[reused],f"reused byte-for-byte from research/outputs/human_model_profile_correspondence/figures/model_specific_replication.png ({digest})")
    record("Figure 13","Complete 20,000-draw search-adjusted null with quantiles","data/permutation_null_histogram.csv; data/permutation_null_summary.csv",annotated_null_figure())
    record("Figure 14","Family-specific max r and adjusted p","data/family_specific_statistics.csv",family_statistics_figure())
    record("Figure 15","Exact 96-item SAPA wording view for selected human profiles","data/sapa_language_profiles.csv",sapa_language_figure())

    inventory=pd.DataFrame(created).sort_values(["requirement","figure_path"])
    inventory.to_csv(OUT/"figure_inventory.csv",index=False,lineterminator="\n")
    print(f"Wrote {len(inventory)} static files covering {inventory.requirement.nunique()} figure requirements")


if __name__ == "__main__":
    main()
