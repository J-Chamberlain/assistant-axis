#!/usr/bin/env python3
from pathlib import Path
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
RAW = Path(os.environ["AA21_SAPA_DIR"])
SEED = 20260915
KEYS = ["IPIP100agree", "IPIP100consc", "IPIP100extra", "IPIP100intel", "IPIP100stability"]
HUMAN_NAMES = ["agreeableness", "conscientiousness", "extraversion", "openness", "emotional_stability"]
CONSTRUCTIONS = ["human_anchored_strict", "external_taxonomy_expanded"]


def zfit(a, idx):
    mu = np.nanmean(a[idx], axis=0)
    sd = np.nanstd(a[idx], axis=0, ddof=1)
    sd[(~np.isfinite(sd)) | (sd == 0)] = 1
    return (a - mu) / sd, mu, sd


def score_human_data():
    freeze = pd.read_csv(ROOT / "research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv")
    freeze = freeze[freeze.tier == "DIRECT"].copy()
    key = pd.read_csv(RAW / "superKey696.csv", index_col=0).fillna(0)
    out_items = freeze.item_id.tolist()
    bridge = pd.read_csv(ROOT / "research/outputs/aa19_human_consensus_factor_validation/bridge_mapping_audit.csv")
    primary = bridge[bridge.aa19_primary_selected.astype(str).str.lower() == "true"].sort_values("model_trait").copy()
    trait_items = set(";".join(primary.sapa_item_ids).split(";"))
    bf_items = set().union(*[set(key.index[key[k] != 0]) for k in KEYS])
    raw = pd.read_csv(
        RAW / "sapaTempData696items08dec2013thru26jul2014.tab", sep="\t", usecols=sorted(set(out_items) | bf_items | trait_items),
        na_values=["NA"], low_memory=False
    ).apply(pd.to_numeric, errors="coerce")

    # Match AA-20 scoring: orient items, standardize each item, then average.
    y_items = raw[out_items].to_numpy(float).copy()
    for j, row in enumerate(freeze.itertuples()):
        if row.orientation == "-":
            y_items[:, j] = 7 - y_items[:, j]
    y_items, _, _ = zfit(y_items, np.arange(len(raw)))
    yn = np.isfinite(y_items).sum(1)
    y = np.nanmean(y_items, axis=1)
    y[yn < 2] = np.nan

    scores, counts = [], []
    for k in KEYS:
        ids = key.index[key[k] != 0].tolist()
        signs = key.loc[ids, k].to_numpy(float)
        x = raw[ids].to_numpy(float).copy()
        x[:, signs < 0] = 7 - x[:, signs < 0]
        x, _, _ = zfit(x, np.arange(len(raw)))
        n = np.isfinite(x).sum(1)
        s = np.nanmean(x, axis=1)
        s[n < 2] = np.nan
        scores.append(s)
        counts.append(n)
    X = np.column_stack(scores)
    bf_ok = np.isfinite(y) & np.isfinite(X).all(axis=1)

    # Reconstruct the narrower AA-20 common eligibility set for a coefficient sensitivity.
    T, O = [], []
    for row in primary.itertuples():
        ids = row.sapa_item_ids.split(";")
        signs = {x.split(":")[0]: int(x.split(":")[1]) for x in row.orientation_signs.split(";")}
        v = raw[ids].to_numpy(float).copy()
        for j, item in enumerate(ids):
            if signs[item] < 0:
                v[:, j] = 7 - v[:, j]
        v, _, _ = zfit(v, np.arange(len(raw)))
        n = np.isfinite(v).sum(1)
        a = np.nanmean(v, axis=1)
        a[n == 0] = np.nan
        T.append(a); O.append(n > 0)
    T, O = np.column_stack(T), np.column_stack(O)
    traits = primary.model_trait.tolist()
    load = pd.read_csv(ROOT / "research/outputs/aa19_human_consensus_factor_validation/human_factor_loadings.csv").pivot(
        index="trait", columns="human_factor", values="pattern_loading"
    ).loc[traits].to_numpy(float)
    Q = np.linalg.qr(load)[0]
    cons = pd.read_csv(ROOT / "research/outputs/aa18_three_model_consensus_trait_structure/consensus_trait_loadings.csv")
    weights = {}
    for j in (1, 2, 3):
        v = cons[cons.component == f"C{j}"].set_index("trait").loc[traits].consensus_loading.to_numpy(float)
        weights[f"C{j}_subspace"] = Q @ (Q.T @ v)
    weights["C1"], weights["C2"] = weights["C1_subspace"], weights["C2_subspace"]
    h2 = load[:, 1]
    v = cons[cons.component == "C3"].set_index("trait").loc[traits].consensus_loading.to_numpy(float)
    weights["C3"] = h2 * np.sign(h2 @ v)
    for j in range(5):
        weights[f"H{j+1}"] = load[:, j]

    def weighted(w):
        den = O @ np.abs(w)
        num = np.nansum(np.where(O, T * w, 0), axis=1)
        out = np.full(len(T), np.nan)
        keep = den >= .15 * np.abs(w).sum()
        out[keep] = num[keep] / den[keep]
        return out

    ws = {name: weighted(w) for name, w in weights.items()}
    common = bf_ok & (O.sum(1) >= 8)
    for name in ("C1", "C2", "C3"):
        w = weights[name]
        common &= (O[:, w > 0].sum(1) >= 2) & (O[:, w < 0].sum(1) >= 2)
    for name in ["C1", "C2", "C3", "H1", "H2", "H3", "H4", "H5"]:
        common &= np.isfinite(ws[name])

    Xfull, _, _ = zfit(X, np.where(bf_ok)[0])
    yfull = (y - np.nanmean(y[bf_ok])) / np.nanstd(y[bf_ok], ddof=1)
    Xcommon, _, _ = zfit(X, np.where(common)[0])
    ycommon = (y - np.nanmean(y[common])) / np.nanstd(y[common], ddof=1)
    return Xfull[bf_ok], yfull[bf_ok], Xcommon[common], ycommon[common], int(bf_ok.sum()), int(common.sum())


def fit_and_validate(X, y, forced_alpha=None):
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(y))
    a, b = int(.6 * len(y)), int(.8 * len(y))
    tr, va, te = order[:a], order[a:b], order[b:]
    alphas = [0, .01, .1, 1, 10, 100]
    candidates = []
    for alpha in alphas:
        m = Ridge(alpha=alpha).fit(X[tr], y[tr])
        candidates.append((mean_squared_error(y[va], m.predict(X[va])), alpha))
    alpha = min(candidates)[1] if forced_alpha is None else forced_alpha
    heldout = Ridge(alpha=alpha).fit(X[np.r_[tr, va]], y[np.r_[tr, va]])
    pred = heldout.predict(X[te])
    metrics = {
        "eligible_n": len(y), "train_n": len(tr), "validation_n": len(va), "test_n": len(te),
        "selected_alpha": alpha, "test_r2": float(r2_score(y[te], pred)),
        "test_rmse": float(np.sqrt(mean_squared_error(y[te], pred)))
    }
    final = Ridge(alpha=alpha).fit(X, y)
    coefs = pd.DataFrame({"domain": HUMAN_NAMES, "standardized_coefficient": final.coef_})
    coefs["absolute_coefficient"] = coefs.standardized_coefficient.abs()
    return final, coefs, metrics


def project_personas(models):
    scores = pd.read_csv(ROOT / "research/outputs/externally_anchored_big_five/big_five_role_scores.csv")
    scores = scores[scores.construction.isin(CONSTRUCTIONS)].copy()
    wide = scores.pivot_table(
        index=["model", "model_label", "construction", "persona"],
        columns="domain", values="raw_projection_score"
    ).reset_index()
    rows = []
    for (mod, construction), g in wide.groupby(["model", "construction"], sort=True):
        g = g.copy()
        # The human fifth domain is Emotional Stability, the inverse of Neuroticism.
        vals = pd.DataFrame({
            "agreeableness": g.agreeableness,
            "conscientiousness": g.conscientiousness,
            "extraversion": g.extraversion,
            "openness": g.openness,
            "emotional_stability": -g.neuroticism,
        })
        z = (vals - vals.mean()) / vals.std(ddof=1)
        for fit_name, model in models.items():
            pred = model.predict(z[HUMAN_NAMES].to_numpy(float))
            q = pd.DataFrame({
                "model": mod, "model_label": g.model_label.values, "human_fit": fit_name,
                "construction": construction, "persona": g.persona.values,
                "hifwb_associated_score_sd": pred,
            })
            q["within_model_percentile"] = q.hifwb_associated_score_sd.rank(pct=True, method="average") * 100
            rows.append(q)
    return pd.concat(rows, ignore_index=True)


def comparisons(proj):
    proj = proj[proj.human_fit == "full_overlap_primary"].copy()
    construction_rows = []
    for mod, g in proj.groupby("model"):
        w = g.pivot(index="persona", columns="construction", values="hifwb_associated_score_sd")
        a, b = w[CONSTRUCTIONS[0]], w[CONSTRUCTIONS[1]]
        top_a, top_b = set(a.nlargest(10).index), set(b.nlargest(10).index)
        bot_a, bot_b = set(a.nsmallest(10).index), set(b.nsmallest(10).index)
        construction_rows.append({
            "model": mod, "pearson_r": float(a.corr(b)),
            "spearman_rho": float(spearmanr(a, b).statistic),
            "top10_overlap": len(top_a & top_b), "bottom10_overlap": len(bot_a & bot_b)
        })
    cross_rows = []
    for construction, g in proj.groupby("construction"):
        w = g.pivot(index="persona", columns="model", values="hifwb_associated_score_sd")
        mods = sorted(w.columns)
        for i in range(len(mods)):
            for j in range(i + 1, len(mods)):
                a, b = w[mods[i]], w[mods[j]]
                cross_rows.append({
                    "construction": construction, "model_a": mods[i], "model_b": mods[j],
                    "pearson_r": float(a.corr(b)), "spearman_rho": float(spearmanr(a, b).statistic),
                    "top10_overlap": len(set(a.nlargest(10).index) & set(b.nlargest(10).index)),
                    "bottom10_overlap": len(set(a.nsmallest(10).index) & set(b.nsmallest(10).index)),
                })
    return pd.DataFrame(construction_rows), pd.DataFrame(cross_rows)


def main():
    X, y, Xc, yc, n, nc = score_human_data()
    model, coefs, metrics = fit_and_validate(X, y)
    common_model, common_coefs, common_metrics = fit_and_validate(Xc, yc, forced_alpha=100)
    metrics["common_eligible_n"] = nc
    common_metrics["fit"] = "aa20_common_ridge_sensitivity"
    coefs["human_fit"] = "full_overlap_primary"
    common_coefs["human_fit"] = "aa20_common_ridge_sensitivity"
    coefs = pd.concat([coefs, common_coefs], ignore_index=True)
    proj = project_personas({"full_overlap_primary": model, "aa20_common_ridge_sensitivity": common_model})
    construction, cross = comparisons(proj)
    coefs.to_csv(HERE / "human_bigfive_hifwb_coefficients.csv", index=False)
    proj.to_csv(HERE / "persona_bigfive_hifwb_projection.csv", index=False)
    construction.to_csv(HERE / "construction_sensitivity.csv", index=False)
    cross.to_csv(HERE / "cross_model_convergence.csv", index=False)
    (HERE / "human_model_metrics.json").write_text(json.dumps({"primary": metrics, "sensitivity": common_metrics}, indent=2) + "\n")
    print(json.dumps({"primary": metrics, "sensitivity": common_metrics}, indent=2))
    print("\nCOEFFICIENTS\n", coefs.to_string(index=False))
    print("\nCONSTRUCTION SENSITIVITY\n", construction.to_string(index=False))
    print("\nCROSS-MODEL CONVERGENCE\n", cross.to_string(index=False))
    for construction_name in CONSTRUCTIONS:
        print(f"\nTOP/BOTTOM: {construction_name}")
        for mod in sorted(proj.model.unique()):
            q = proj[(proj.model == mod) & (proj.construction == construction_name) & (proj.human_fit == "full_overlap_primary")]
            top = ", ".join(q.nlargest(5, "hifwb_associated_score_sd").persona)
            bottom = ", ".join(q.nsmallest(5, "hifwb_associated_score_sd").persona)
            print(mod, "TOP:", top)
            print(mod, "BOTTOM:", bottom)


if __name__ == "__main__":
    main()
