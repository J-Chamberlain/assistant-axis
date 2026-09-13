#!/usr/bin/env python3
"""Create post-freeze semantic summaries and deterministic descriptive figures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


OUT = Path(__file__).resolve().parent
FIG = OUT / "figures"
ELIGIBLE_K = [4, 5, 6, 7, 8, 10]
FAMILIES = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
COLORS = dict(zip(FAMILIES, sns.color_palette("colorblind", 4)))


def savefig(path: Path) -> None:
    plt.savefig(path, dpi=180, bbox_inches="tight", facecolor="white", metadata={"Software": "matplotlib"})
    plt.close()


def make_item_order() -> tuple[pd.DataFrame, pd.DataFrame]:
    values = pd.read_csv(OUT / "human_sapa_item_profile_values.csv")
    mapping = (
        values[["trait", "item_id", "item_text", "orientation_sign", "transformation"]]
        .drop_duplicates()
        .sort_values(["item_id", "trait"])
    )
    order_rows = []
    for item, g in mapping.groupby("item_id", sort=False):
        traits = sorted(g["trait"].tolist())
        order_rows.append(
            {
                "item_id": item,
                "item_text": g.iloc[0]["item_text"],
                "primary_frozen_trait_owner": traits[0],
                "all_frozen_direct_trait_mappings": ";".join(traits),
                "mapping_count": len(traits),
                "trait_orientation_signs": ";".join(f"{r.trait}:{int(r.orientation_sign)}" for r in g.itertuples()),
            }
        )
    order = pd.DataFrame(order_rows)
    order["item_number"] = order["item_id"].str.split("_").str[1].astype(int)
    order = order.sort_values(["primary_frozen_trait_owner", "item_number", "item_id"]).reset_index(drop=True)
    order["visualization_order"] = np.arange(1, len(order) + 1)
    order.to_csv(OUT / "human_sapa_item_visualization_order.csv", index=False)

    unique = values.drop_duplicates(["K", "profile_id", "item_id"]).copy()
    unique["raw_expected_item_z"] = (unique["expected_response"] - unique["empirical_mean_raw"]) / unique["empirical_sd_raw_ddof1"]
    ridge = unique.merge(order, on=["item_id", "item_text"], validate="many_to_one")
    ridge = ridge[
        ["K", "profile_id", "profile_size", "profile_proportion", "item_id", "item_text", "visualization_order",
         "primary_frozen_trait_owner", "all_frozen_direct_trait_mappings", "expected_response", "empirical_mean_raw",
         "empirical_sd_raw_ddof1", "raw_expected_item_z"]
    ].sort_values(["K", "profile_id", "visualization_order"])
    ridge.to_csv(OUT / "human_sapa_item_ridge_values.csv", index=False, float_format="%.12g")
    return order, ridge


def ridgeline(matrix: pd.DataFrame, title: str, xlabel: str, path: Path, colors=None) -> None:
    labels = list(matrix.index)
    x = np.arange(matrix.shape[1])
    fig, ax = plt.subplots(figsize=(16, max(4.5, 0.72 * len(labels) + 1.7)))
    scale = 0.75 / max(0.5, float(np.nanpercentile(np.abs(matrix.to_numpy()), 95)))
    palette = colors or sns.color_palette("viridis", len(labels))
    for i, (label, row) in enumerate(matrix.iterrows()):
        baseline = len(labels) - 1 - i
        y = baseline + row.to_numpy(float) * scale
        color = palette[i]
        ax.plot(x, y, color=color, lw=1.25)
        ax.fill_between(x, baseline, y, color=color, alpha=0.25)
    ax.set_yticks(np.arange(len(labels))[::-1], labels)
    ax.axvline(-1, color="none")
    ax.set_xlim(0, max(1, len(x) - 1))
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", weight="bold")
    ax.grid(axis="x", color="#dddddd", lw=.4, alpha=.5)
    sns.despine(ax=ax, left=True)
    savefig(path)


def plot_ridges(order: pd.DataFrame, ridge: pd.DataFrame) -> None:
    order_items = order.sort_values("visualization_order")["item_id"].tolist()
    human = pd.read_csv(OUT / "human_trait_profiles_45.csv")
    traits = sorted(human["trait"].unique())
    for k in [4, 6, 10]:
        d = ridge.loc[ridge["K"].eq(k)].pivot(index="profile_id", columns="item_id", values="raw_expected_item_z")
        d = d.loc[sorted(d.index), order_items]
        ridgeline(d, f"Human SAPA literal-item profile ridges — K={k}",
                  "96 items ordered by frozen trait mapping (exact wording in companion CSV)", FIG / f"human_sapa_ridges_k{k:02d}.png")
        t = human.loc[human["K"].eq(k)].pivot(index="profile_id", columns="trait", values="human_trait_value")
        t = t.loc[sorted(t.index), traits]
        ridgeline(t, f"Human direct-bridge trait profile ridges — K={k}", "45 frozen direct traits (alphabetical)",
                  FIG / f"human_trait_ridges_k{k:02d}.png")

    model = pd.read_csv(OUT / "model_family_trait_profiles_45.csv")
    m = model.pivot(index="family_id", columns="trait", values="three_model_consensus_value").loc[FAMILIES, traits]
    ridgeline(m, "Primary reconciled model-family ridges", "45 frozen direct traits (alphabetical)",
              FIG / "model_family_trait_ridges_A_D.png", [COLORS[x] for x in FAMILIES])
    e = model.loc[model["family_id"].eq("MFamily_E")].set_index("trait").loc[traits, "three_model_consensus_value"].to_frame().T
    e.index = ["MFamily_E (secondary)"]
    ridgeline(e, "Secondary developmental-outlier family ridge", "45 frozen direct traits (alphabetical)",
              FIG / "model_family_trait_ridge_E.png", ["#777777"])


def plot_heatmaps() -> None:
    sim = pd.read_csv(OUT / "profile_similarity_45.csv")
    for k in ELIGIBLE_K:
        matrix = sim.loc[sim["K"].eq(k)].pivot(index="human_profile_id", columns="model_family_id", values="pearson_r")
        matrix = matrix.loc[sorted(matrix.index), FAMILIES]
        plt.figure(figsize=(7.2, max(4.2, .48 * k + 1.8)))
        sns.heatmap(matrix, cmap="vlag", center=0, vmin=-.8, vmax=.8, annot=True, fmt=".2f", linewidths=.4,
                    cbar_kws={"label": "Pearson r across 45 traits"})
        plt.title(f"Aggregate human × model-family similarity — human K={k}", loc="left", weight="bold")
        plt.xlabel("Frozen model consensus family"); plt.ylabel("Frozen human latent profile")
        savefig(FIG / f"similarity_heatmap_k{k:02d}.png")


def plot_scores_and_null() -> None:
    a45 = pd.read_csv(OUT / "primary_assignments_by_k.csv").drop_duplicates("K")
    a12 = pd.read_csv(OUT / "primary_assignments_12_by_k.csv").drop_duplicates("K")
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(a45["K"], a45["back_transformed_mean_r_for_K"], marker="o", label="45 direct traits", lw=2)
    ax.plot(a12["K"], a12["back_transformed_mean_r_for_K"], marker="s", label="12 supported traits", lw=2)
    for k, label in [(4, "BIC/ICL anchor"), (10, "predictive anchor")]:
        ax.axvline(k, color="#888888", ls="--", lw=.8); ax.text(k+.05, .08, label, rotation=90, va="bottom", fontsize=8)
    ax.axvspan(3.85, 6.15, color="#3b82f6", alpha=.06, label="moderate-stability K range")
    ax.set(xticks=ELIGIBLE_K, xlabel="Human K", ylabel="Back-transformed mean assigned r", title="Injective assignment score across eligible human resolutions")
    ax.legend(frameon=False, ncol=2); ax.grid(alpha=.25); sns.despine(ax=ax)
    savefig(FIG / "k_level_primary_scores.png")

    null = pd.read_csv(OUT / "bridge_permutation_null_45.csv")
    primary = json.loads((OUT / "primary_global_result.json").read_text())
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.hist(null["global_max_fisher_z"], bins=60, color="#7895b2", alpha=.85)
    ax.axvline(primary["observed_max_mean_fisher_z"], color="#b91c1c", lw=2.4,
               label=f"Observed={primary['observed_max_mean_fisher_z']:.3f}")
    ax.set(xlabel="Maximum mean Fisher-z after assignment and K search", ylabel="Permutation count",
           title="Search-adjusted 45-trait bridge-permutation null")
    ax.legend(frameon=False); sns.despine(ax=ax)
    savefig(FIG / "bridge_permutation_null_45.png")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    x=np.arange(len(ELIGIBLE_K)); width=.36
    ax.bar(x-width/2,a45.set_index('K').loc[ELIGIBLE_K,'back_transformed_mean_r_for_K'],width,label='45 direct')
    ax.bar(x+width/2,a12.set_index('K').loc[ELIGIBLE_K,'back_transformed_mean_r_for_K'],width,label='12 supported')
    ax.set_xticks(x,ELIGIBLE_K); ax.set(xlabel='Human K',ylabel='Back-transformed mean assigned r',title='Full bridge and conservative-core comparison')
    ax.legend(frameon=False); sns.despine(ax=ax)
    savefig(FIG / "trait_set_sensitivity.png")


def plot_assignment() -> None:
    primary=json.loads((OUT/"primary_global_result.json").read_text()); k=int(primary['maximizing_K'])
    a=pd.read_csv(OUT/"primary_assignments_by_k.csv"); a=a[a.K.eq(k)].sort_values('model_family_id')
    fig,ax=plt.subplots(figsize=(9,5.6)); ax.axis('off')
    ys=np.linspace(.85,.15,4)
    for y,(_,r) in zip(ys,a.iterrows()):
        ax.text(.08,y,r.model_family_id,ha='center',va='center',bbox=dict(boxstyle='round,pad=.35',fc=COLORS[r.model_family_id],alpha=.2,ec=COLORS[r.model_family_id]))
        ax.text(.92,y,r.human_profile_id,ha='center',va='center',bbox=dict(boxstyle='round,pad=.35',fc='#eeeeee',ec='#555555'))
        ax.plot([.19,.81],[y,y],color=COLORS[r.model_family_id],lw=1.5+4*max(0,r.pearson_r),alpha=.8)
        ax.text(.50,y+.025,f"r={r.pearson_r:.3f}",ha='center',va='bottom',fontsize=9)
    ax.text(.08,.97,'Frozen model families',ha='center',weight='bold'); ax.text(.92,.97,f'Frozen human profiles (K={k})',ha='center',weight='bold')
    ax.set_title('Preregistered maximum-weight injective assignment',loc='left',weight='bold')
    savefig(FIG/'primary_assignment.png')


def plot_persistence() -> None:
    d=pd.read_csv(OUT/'cross_resolution_human_persistence.csv')
    fig,axes=plt.subplots(4,1,figsize=(10,8.5),sharex=True)
    for ax,fam in zip(axes,FAMILIES):
        g=d[d.origin_model_family.eq(fam)].sort_values('K')
        ax.plot(g.K,g.best_pearson_r,color=COLORS[fam],marker='o',lw=2)
        for r in g.itertuples():
            ax.annotate(f"{r.human_profile_id}\n→{r.best_model_family[-1]}",(r.K,r.best_pearson_r),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7)
        ax.axhline(0,color='#aaaaaa',lw=.7); ax.set_ylabel(fam[-1]); ax.grid(alpha=.2)
    axes[-1].set_xticks(range(4,11)); axes[-1].set_xlabel('Human K (K=9 is diagnostic/ineligible)')
    axes[0].set_title('Mutual-nearest human lineages from primary K=10 counterparts\nLabels show profile and its unconstrained nearest model family',loc='left',weight='bold')
    sns.despine(fig=fig); savefig(FIG/'cross_resolution_persistence.png')


def plot_replication() -> None:
    d=pd.read_csv(OUT/'model_specific_replication.csv')
    d=d[d.representation.isin(['three_model_consensus','qwen','llama','gemma'])].copy()
    order=['three_model_consensus','qwen','llama','gemma']; d['representation']=pd.Categorical(d.representation,order,ordered=True)
    fig,ax=plt.subplots(figsize=(10,5)); sns.barplot(data=d,x='model_family_id',y='pearson_r',hue='representation',hue_order=order,ax=ax)
    ax.axhline(0,color='#555555',lw=.8); ax.set(xlabel='Frozen family / fixed human counterpart',ylabel='Pearson r across 45 traits',title='Model-specific replication without reassignment')
    ax.legend(title='',frameon=False,ncol=4,loc='upper center',bbox_to_anchor=(.5,1.13)); sns.despine(ax=ax)
    savefig(FIG/'model_specific_replication.png')


def semantic_summary(order: pd.DataFrame, ridge: pd.DataFrame) -> None:
    human=pd.read_csv(OUT/'human_trait_profiles_45.csv'); model=pd.read_csv(OUT/'model_family_trait_profiles_45.csv')
    primary=json.loads((OUT/'primary_global_result.json').read_text()); k=int(primary['maximizing_K'])
    assignments=pd.read_csv(OUT/'primary_assignments_by_k.csv'); assignments=assignments[assignments.K.eq(k)].sort_values('model_family_id')
    descriptions={
        'MFamily_A':'professional/analytical broad role family',
        'MFamily_B':'mythic/symbolic and expressive role family',
        'MFamily_C':'informal life-stage/social role family',
        'MFamily_D':'adversarial/competitive role family',
        'MFamily_E':'primitive/literal developmental outlier family (secondary)',
    }
    lines=['# Post-freeze semantic profile summary','',
           'All numerical profiles, similarities, assignments, null results, and robustness results were committed before this wording was inspected jointly. Descriptions are restrained interpretations of frozen aggregate profiles, not labels used to create or select them.','']
    for a in assignments.itertuples():
        hd=human[(human.K.eq(k))&human.profile_id.eq(a.human_profile_id)].sort_values('human_trait_value')
        md=model[model.family_id.eq(a.model_family_id)].sort_values('three_model_consensus_value')
        item=ridge[(ridge.K.eq(k))&ridge.profile_id.eq(a.human_profile_id)].sort_values('raw_expected_item_z')
        high=', '.join(f"{r.trait} ({r.human_trait_value:+.2f})" for r in hd.tail(5).itertuples())
        low=', '.join(f"{r.trait} ({r.human_trait_value:+.2f})" for r in hd.head(5).itertuples())
        mhigh=', '.join(f"{r.trait} ({r.three_model_consensus_value:+.2f})" for r in md.tail(5).itertuples())
        mlow=', '.join(f"{r.trait} ({r.three_model_consensus_value:+.2f})" for r in md.head(5).itertuples())
        ihigh='; '.join(f"\"{r.item_text}\" ({r.raw_expected_item_z:+.2f} SD)" for r in item.tail(3).itertuples())
        ilow='; '.join(f"\"{r.item_text}\" ({r.raw_expected_item_z:+.2f} SD)" for r in item.head(3).itertuples())
        lines += [f"## {a.model_family_id} ↔ {a.human_profile_id}",'',
                  f"Frozen model-side description: {descriptions[a.model_family_id]}. Primary profile-shape similarity: Pearson r={a.pearson_r:.3f}, Spearman rho={a.spearman_rho:.3f}.",'',
                  f"Human proxy elevations: {high}. Human proxy depressions: {low}.",'',
                  f"Model-family elevations: {mhigh}. Model-family depressions: {mlow}.",'',
                  f"Literal SAPA statements with highest raw expected agreement relative to their observed item means: {ihigh}.",'',
                  f"Literal SAPA statements with lowest raw expected agreement relative to their observed item means: {ilow}.",'']
    lines += ['## Restrained joint interpretation','',
              '- A↔H10_C shares orderly, patient, low-manipulation/low-impulsivity structure, although the model family is more reserved and secular than the human proxy profile.','- B↔H10_J is the weakest primary link. Shared grandiose/dramatic structure coexists with a substantial mismatch between the model family’s creative/theatrical emphasis and the human profile’s rebellious/manipulative pattern; B does not pass its family-specific adjusted test.','- C↔H10_G shares anxious/neurotic/emotional elevation, but the human profile is reserved and low in assertiveness while the model family is gregarious and extroverted. C’s unconstrained best human profile is H10_I, which is also D’s much stronger counterpart, so C is not cleanly distinguished by the injective solution.','- D↔H10_I is the clearest pair: both show high antagonistic/negative-affect patterning and low calm, patience, optimism, and prosocial traits.','- E also selects H10_I and therefore has adjusted evidence for similarity but no distinct human counterpart separate from D in this analysis.','',
              'The conservative 12-trait assignment changes three of four K=10 pair identities even though the global signal strengthens. This supports aggregate cross-domain structure while warning that exact family-to-profile identities depend on measurement resolution.','']
    (OUT/'semantic_profile_summary.md').write_text('\n'.join(lines)+'\n')


def main() -> None:
    FIG.mkdir(parents=True,exist_ok=True); sns.set_theme(style='whitegrid',context='notebook')
    order,ridge=make_item_order(); plot_ridges(order,ridge); plot_heatmaps(); plot_scores_and_null(); plot_assignment(); plot_persistence(); plot_replication(); semantic_summary(order,ridge)
    print(f"wrote {len(list(FIG.glob('*.png')))} figures and semantic summary")


if __name__=='__main__':
    main()
