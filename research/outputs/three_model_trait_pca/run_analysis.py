#!/usr/bin/env python3
"""AA-14: CPU-only trait PCA and frozen persona projections from saved vectors."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch
from scipy.linalg import orthogonal_procrustes, subspace_angles
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
VECTORS = ROOT.parent / "assistant-axis" / "downloads" / "hf_vectors"
MODELS = {"qwen": ("qwen-3-32b", 5120), "llama": ("llama-3.3-70b", 8192), "gemma": ("gemma-2-27b", 4608)}
SEED = 140016
BOOT = 100
PARALLEL = 60
PERM = 500
K_DISPLAY = 20


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def table(name, rows):
    if not rows:
        return
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load(folder, kind, dim):
    paths = sorted((VECTORS / folder / f"{kind}_vectors").glob("*.pt"))
    names, vectors, shapes = [], [], {}
    digest = hashlib.sha256()
    for path in paths:
        data = path.read_bytes()
        file_hash = hashlib.sha256(data).hexdigest()
        digest.update(f"{path.name}\0{file_hash}\n".encode())
        tensor = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
        shapes[str(tuple(tensor.shape))] = shapes.get(str(tuple(tensor.shape)), 0) + 1
        vector = tensor.float().mean(0) if tensor.ndim > 1 else tensor.float()
        names.append(path.stem)
        vectors.append(vector.numpy().astype("float64"))
    arr = np.stack(vectors)
    expected = 240 if kind == "trait" else 275
    assert arr.shape == (expected, dim) and len(set(names)) == expected and np.isfinite(arr).all()
    return names, arr, {"count": len(names), "pooled_shape": list(arr.shape), "source_shapes": shapes,
                        "aggregate_sha256": digest.hexdigest(), "source": f"downloads/hf_vectors/{folder}/{kind}_vectors"}


def fit(x):
    mean = x.mean(0)
    centered = x - mean
    gram = centered @ centered.T
    eigen, u = np.linalg.eigh(gram)
    order = np.argsort(eigen)[::-1]
    eigen, u = np.maximum(eigen[order], 0), u[:, order]
    rank = len(x) - 1
    singular = np.sqrt(eigen[:rank])
    scores = u[:, :rank] * singular
    directions = (centered.T @ u[:, :rank] / np.where(singular > 1e-9, singular, np.inf)).T
    # Deterministic sign anchor: largest-magnitude activation coordinate positive.
    signs = np.sign(directions[np.arange(rank), np.argmax(abs(directions), axis=1)])
    signs[signs == 0] = 1
    scores *= signs
    directions *= signs[:, None]
    eigen = eigen[:rank] / rank
    ratios = eigen / eigen.sum()
    return {"mean": mean, "centered": centered, "scores": scores, "directions": directions,
            "eigen": eigen, "ratios": ratios, "cumulative": ratios.cumsum()}


def aligned_scores(left, right, k):
    a = left[:, :k] / left[:, :k].std(0, ddof=1)
    b = right[:, :k] / right[:, :k].std(0, ddof=1)
    qa, _ = np.linalg.qr(a)
    qb, _ = np.linalg.qr(b)
    singular = np.linalg.svd(qa.T @ qb, compute_uv=False)
    rotation, _ = orthogonal_procrustes(b, a)
    matched = b @ rotation
    return float(np.mean([np.corrcoef(a[:, i], matched[:, i])[0, 1] for i in range(k)])), singular


def main():
    rng = np.random.default_rng(SEED)
    records, spectra, scores_rows, component_rows, stability_rows, parallel_rows = {}, [], [], [], [], []
    full_persona_rows, full_trait_rows, retention_rows = [], [], []
    sources, viz = {}, {"version": "aa14-v1", "default_model": "qwen", "models": {}}
    names_ref = roles_ref = None
    prior = {r["trait"]: r for r in csv.DictReader((ROOT / "research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv").open())}
    for model, (folder, dim) in MODELS.items():
        traits, t, taudit = load(folder, "trait", dim)
        roles, p, paudit = load(folder, "role", dim)
        if names_ref is None:
            names_ref, roles_ref = traits, roles
        assert traits == names_ref and roles == roles_ref, f"{model}: shared inventory/order mismatch"
        sources[model] = {"traits": taudit, "personas": paudit, "missing_traits": [], "excluded_traits": [],
                          "layer": {"qwen": 48, "llama": "released layer-mean", "gemma": "released layer-mean"}[model]}
        z = fit(t)
        if model == "qwen":
            for pc in range(3):
                reference = np.array([float(prior[name][f"trait_pc{pc+1}"]) for name in traits])
                if np.corrcoef(reference, z["scores"][:, pc])[0, 1] < 0:
                    z["scores"][:, pc] *= -1
                    z["directions"][pc] *= -1
            reproduction = {"new": z["ratios"][:3].tolist(), "prior": [0.35283568247600433, 0.16806772977536064, 0.13374404483700736],
                            "score_max_abs_difference": float(max(np.max(abs(z["scores"][:, i] - np.array([float(prior[n][f"trait_pc{i+1}"]) for n in traits]))) for i in range(3)))}
        persona_pca = fit(p)
        centered_personas = p - z["mean"]
        projected = centered_personas @ z["directions"].T
        captured20 = np.sum(projected[:, :20] ** 2, axis=1)
        norm2 = np.sum(centered_personas ** 2, axis=1)
        residual20 = np.sqrt(np.maximum(norm2 - captured20, 0))
        captured_full = np.sum(projected ** 2, axis=1)
        residual_full = np.sqrt(np.maximum(norm2 - captured_full, 0))
        # Sensitivity is frozen before interpretation: row-unit-normalize both banks, refit, project.
        tn = t / np.linalg.norm(t, axis=1, keepdims=True)
        pn = p / np.linalg.norm(p, axis=1, keepdims=True)
        zn = fit(tn)
        alternative = (pn - zn["mean"]) @ zn["directions"].T
        alternative_r = aligned_scores(projected, alternative, 3)[0]
        d3 = cdist(projected[:, :3], z["scores"][:, :3])
        d20 = cdist(projected[:, :20], z["scores"][:, :20])
        trait_nn = np.partition(cdist(z["scores"][:, :20], z["scores"][:, :20]) + np.eye(240)*1e8, 4, axis=1)[:, 4]
        ood_cut = float(np.quantile(trait_nn, .99))
        for i, name in enumerate(roles):
            row = {"model": model, "persona": name, "projected_norm_squared_20": captured20[i],
                   "centered_norm_squared": norm2[i], "residual_norm_20": residual20[i],
                   "projected_norm_squared_full": captured_full[i], "residual_norm_full": residual_full[i],
                   "captured_fraction_20": captured20[i] / norm2[i], "trait_cloud_distance_20": d20[i].min(),
                   "ood": bool(d20[i].min() > ood_cut), "nearest_traits_3d": ";".join(traits[j] for j in np.argsort(d3[i])[:5])}
            row.update({f"trait_pc{j+1}": projected[i, j] for j in range(K_DISPLAY)})
            scores_rows.append(row)
            full_persona_rows.append({"model": model, "persona": name, **{f"trait_pc{j+1}": projected[i,j] for j in range(projected.shape[1])}})
        for i, name in enumerate(traits):
            row = {"model": model, "trait": name}
            row.update({f"trait_pc{j+1}": z["scores"][i, j] for j in range(K_DISPLAY)})
            component_rows.append(row)
            full_trait_rows.append({"model": model, "trait": name, **{f"trait_pc{j+1}": z["scores"][i,j] for j in range(z["scores"].shape[1])}})
        for j, (e, r, c) in enumerate(zip(z["eigen"], z["ratios"], z["cumulative"]), 1):
            spectra.append({"model": model, "pc": j, "eigenvalue": e, "explained_variance": r, "cumulative_variance": c})
        for threshold in (.5, .6, .68, .7, .75, .8, .9, .95):
            retention_rows.append({"model": model, "target_cumulative_variance": threshold,
                                   "components_required": int(np.searchsorted(z["cumulative"], threshold)+1)})
        # Bootstrap roles/traits as observations; compare recovered directions to frozen axes.
        boot_axis = np.zeros((BOOT, K_DISPLAY))
        boot_sub = np.zeros((BOOT, 2))
        for b in range(BOOT):
            zb = fit(t[rng.integers(0, len(t), len(t))])
            cosine = abs(z["directions"][:K_DISPLAY] @ zb["directions"][:K_DISPLAY].T)
            boot_axis[b] = cosine.max(axis=1)
            for idx, k in enumerate((3, 10)):
                boot_sub[b, idx] = np.cos(subspace_angles(z["directions"][:k].T, zb["directions"][:k].T)).mean()
        for j in range(K_DISPLAY):
            stability_rows.append({"model": model, "pc": j+1, "matched_axis_cosine_median": np.median(boot_axis[:, j]),
                                   "matched_axis_cosine_q05": np.quantile(boot_axis[:, j], .05),
                                   "top3_subspace_mean_cosine_median": np.median(boot_sub[:, 0]),
                                   "top10_subspace_mean_cosine_median": np.median(boot_sub[:, 1])})
        # Coordinate-wise permutation retains per-feature marginals, destroys joint trait structure.
        nulls = np.zeros((PARALLEL, K_DISPLAY))
        for b in range(PARALLEL):
            shuffled = np.take_along_axis(t, np.argsort(rng.random(t.shape), axis=0), axis=0)
            nulls[b] = fit(shuffled)["eigen"][:K_DISPLAY]
        for j in range(K_DISPLAY):
            parallel_rows.append({"model": model, "pc": j+1, "observed_eigenvalue": z["eigen"][j],
                                  "null_q95": np.quantile(nulls[:, j], .95), "above_null": bool(z["eigen"][j] > np.quantile(nulls[:, j], .95))})
        top = {}
        for j in range(K_DISPLAY):
            order = np.argsort(z["scores"][:, j])
            top[f"PC{j+1}"] = {"low": [traits[i] for i in order[:10]], "high": [traits[i] for i in order[-10:][::-1]]}
        angles = {}
        for k in (1, 3, 6, 10, 20):
            angles[str(k)] = np.degrees(subspace_angles(z["directions"][:k].T, persona_pca["directions"][:k].T)).tolist()
        np.savez_compressed(OUT / f"{model}_trait_pca_directions.npz", directions=z["directions"].astype("float32"), mean=z["mean"].astype("float32"))
        records[model] = {"trait": z, "persona": persona_pca, "traits": traits, "roles": roles,
                          "top": top, "angles": angles, "alternative_score_alignment3": alternative_r,
                          "ood_count": int(np.sum(d20.min(axis=1) > ood_cut)), "ood_cut": ood_cut,
                          "capture20_median": float(np.median(captured20/norm2)),
                          "residual20_median": float(np.median(residual20))}
        viz["models"][model] = {"label": model.title(), "variance": z["ratios"][:K_DISPLAY].tolist(), "axis_poles": top,
                                 "traits": [{"name": n, "pcs": z["scores"][i, :K_DISPLAY].round(5).tolist()} for i,n in enumerate(traits)],
                                 "personas": [{"name": n, "pcs": projected[i, :K_DISPLAY].round(5).tolist(),
                                                "captured": round(float(captured20[i]/norm2[i]), 5),
                                                "residual": round(float(residual20[i]), 5),
                                                "nearest": [traits[j] for j in np.argsort(d3[i])[:5]],
                                                "ood": bool(d20[i].min() > ood_cut)} for i,n in enumerate(roles)],
                                 "axis_stability": [bool(np.quantile(boot_axis[:, j], .05) >= .75) for j in range(K_DISPLAY)]}
        print(model, "variance", z["ratios"][:3], "capture20", records[model]["capture20_median"], flush=True)
    cross = []
    for left, right in (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma")):
        a, b = records[left]["trait"]["scores"], records[right]["trait"]["scores"]
        for k in (3, 6, 10, 20):
            corr, cc = aligned_scores(a, b, k)
            null = np.array([aligned_scores(a, b[rng.permutation(len(b))], k)[1].mean() for _ in range(PERM)])
            cross.append({"left": left, "right": right, "k": k, "aligned_mean_axis_correlation": corr,
                          "mean_canonical_correlation": cc.mean(), "min_canonical_correlation": cc.min(),
                          "permutation_p": (1 + np.sum(null >= cc.mean()))/(PERM+1)})
    table("full_spectra.csv", spectra)
    table("trait_pc_scores.csv", component_rows)
    table("trait_pc_scores_all.csv", full_trait_rows)
    table("projected_personas.csv", scores_rows)
    table("projected_personas_all_pcs.csv", full_persona_rows)
    table("retention_thresholds.csv", retention_rows)
    table("bootstrap_stability.csv", stability_rows)
    table("parallel_analysis.csv", parallel_rows)
    table("cross_model_alignment.csv", cross)
    dump("viewer_data.json", viz)
    dump("source_inventory.json", sources)
    dump("qwen_reproduction.json", reproduction)
    dump("analysis_summary.json", {m: {"variance_first20": r["trait"]["ratios"][:20].tolist(),
                                       "cumulative_3": float(r["trait"]["cumulative"][2]),
                                       "effective_rank_participation": float(1/sum(r["trait"]["ratios"]**2)),
                                       "retention_80pct": int(np.searchsorted(r["trait"]["cumulative"], .8)+1),
                                       "top_traits": r["top"], "trait_persona_principal_angles_degrees": r["angles"],
                                       "same_number_pc_direction_cosines_descriptive_only": np.diag(r["trait"]["directions"][:20] @ r["persona"]["directions"][:20].T).tolist(),
                                       "normalized_sensitivity_aligned_r3": r["alternative_score_alignment3"],
                                       "ood_count": r["ood_count"], "median_capture20": r["capture20_median"],
                                       "median_residual20": r["residual20_median"]} for m,r in records.items()})
    checks = {"seed": SEED, "bootstrap": BOOT, "parallel": PARALLEL, "cross_model_permutations": PERM,
              "same_trait_labels_and_order": True, "same_persona_labels_and_order": True,
              "qwen_variance_max_error": float(max(abs(np.array(reproduction["new"])-reproduction["prior"]))),
              "qwen_score_max_error": reproduction["score_max_abs_difference"],
              "spectra_sum_max_error": float(max(abs(r["trait"]["ratios"].sum()-1) for r in records.values())),
              "projection_identity_max_error": float(max(np.max(abs(np.sum(((r["trait"]["centered"] @ r["trait"]["directions"].T))**2, axis=1)-np.sum(r["trait"]["centered"]**2, axis=1))) for r in records.values()))}
    dump("verification.json", checks)
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
