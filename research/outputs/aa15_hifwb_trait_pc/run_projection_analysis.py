#!/usr/bin/env python3
"""Project prospectively extracted HiFWB contrasts onto frozen AA-14 trait PCs.

Requires complete private `.npz` extraction bundles for all 3×13×3 cases.
Refuses partial inference results. Does not refit trait PCA.
"""
from __future__ import annotations

import argparse
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
from scipy.spatial.distance import cdist, pdist
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AA14 = HERE.parent / "three_model_trait_pca"
SOURCE = ROOT.parent / "assistant-axis" / "downloads" / "hf_vectors"
MODELS = {"qwen": ("qwen-3-32b", 5120, 64),
          "llama": ("llama-3.3-70b", 8192, 80),
          "gemma": ("gemma-2-27b", 4608, 46)}
FORMS = ("primary_positive_pole", "exact_survey", "minimal_first_person")
SEED = 150015
BOOT = 500
NULL = 5000
K = 20


def read_rows(name: str) -> list[dict]:
    with (HERE / name).open() as stream:
        return list(csv.DictReader(stream))


def aa14_rows(name: str, model: str, key: str) -> tuple[list[str], np.ndarray]:
    with (AA14 / name).open() as stream:
        rows = [r for r in csv.DictReader(stream) if r["model"] == model]
    pcs = [f"trait_pc{i}" for i in range(1, 240)]
    return [r[key] for r in rows], np.array([[float(r[c]) for c in pcs] for r in rows])


def write_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        return
    with (HERE / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denominator) if denominator > 0 else float("nan")


def reference_ood(scores: np.ndarray) -> float:
    d = cdist(scores[:, :K], scores[:, :K])
    np.fill_diagonal(d, np.inf)
    return float(np.quantile(np.partition(d, 4, axis=1)[:, 4], 0.99))


def compactness(indicator_scores: np.ndarray, indicator_norms: np.ndarray,
                trait_scores: np.ndarray, rng: np.random.Generator) -> dict:
    observed = float(np.median(pdist(indicator_scores[:, :K])))
    random_null = np.empty(NULL)
    for i in range(NULL):
        chosen = rng.choice(len(trait_scores), len(indicator_scores), replace=False)
        random_null[i] = np.median(pdist(trait_scores[chosen, :K]))
    trait_norms = np.linalg.norm(trait_scores, axis=1)
    candidates = [np.flatnonzero(abs(trait_norms - norm) / max(norm, 1.0) <= 0.20)
                  for norm in indicator_norms]
    matched = []
    if min(map(len, candidates)) >= 5:
        for _ in range(NULL * 5):
            order = rng.permutation(len(candidates))
            chosen = []
            for j in order:
                available = np.setdiff1d(candidates[j], chosen, assume_unique=False)
                if len(available) == 0:
                    break
                chosen.append(int(rng.choice(available)))
            if len(chosen) == len(candidates):
                matched.append(float(np.median(pdist(trait_scores[chosen, :K]))))
            if len(matched) == NULL:
                break
    matched_valid = len(matched) == NULL
    return {"observed_median_pairwise_distance_20": observed,
            "unmatched_null_median": float(np.median(random_null)),
            "unmatched_compactness_p": float((1 + (random_null <= observed).sum()) / (NULL + 1)),
            "norm_match_tolerance": 0.20,
            "min_candidates_per_indicator": int(min(map(len, candidates))),
            "matched_null_valid": matched_valid,
            "matched_null_draws": len(matched),
            "matched_null_median": float(np.median(matched)) if matched_valid else None,
            "matched_compactness_p": float((1 + (np.array(matched) <= observed).sum()) / (NULL + 1)) if matched_valid else None}


def source_centered(folder: str, kind: str, name: str, mean: np.ndarray) -> np.ndarray:
    path = SOURCE / folder / f"{kind}_vectors" / f"{name}.pt"
    tensor = torch.load(io.BytesIO(path.read_bytes()), map_location="cpu", weights_only=True)
    return tensor.float().mean(0).numpy().astype(np.float64) - mean


def main(private_root: Path) -> None:
    items = read_rows("hifwb_indicator_inventory.csv")
    assert len(items) == 13
    expected_ids = [r["item_id"] for r in items]
    rng = np.random.default_rng(SEED)
    coord_rows, diagnostic_rows, stability_rows, neighborhood_rows = [], [], [], []
    persona_rows, trait_rows, compact_rows, cross_rows, human_rows = [], [], [], [], []
    cross_ranking_rows, cross_form_rows, cross_subspace_rows, centroid_rows = [], [], [], []
    per_model, verification = {}, {"seed": SEED, "models": {}, "all_model_formulation_cases": 117,
                                   "fit_source": "frozen_aa14_trait_mean_and_directions_only"}
    prompt_bytes = (HERE / "hifwb_prompt_freeze.csv").read_bytes()
    question_bytes = (HERE / "hifwb_extraction_questions.csv").read_bytes()
    protocol_hash = hashlib.sha256(prompt_bytes + b"\0" + question_bytes).hexdigest()

    for model, (folder, dim, layers) in MODELS.items():
        manifest_path = private_root / model / "extraction_manifest.json"
        assert manifest_path.exists(), f"Missing complete extraction manifest for {model}"
        manifest = json.loads(manifest_path.read_text())
        assert manifest["model_key"] == model and manifest["all_layers"] == layers
        assert manifest["prompt_question_protocol_sha256"] == protocol_hash
        assert len(manifest["items"]) == 39 and all(r["status"] in ("extracted", "reused") for r in manifest["items"])
        expected_cases = {(item_id, form) for item_id in expected_ids for form in FORMS}
        assert {(r["item_id"], r["formulation"]) for r in manifest["items"]} == expected_cases
        manifest_cases = {(r["item_id"], r["formulation"]): r for r in manifest["items"]}
        frozen = np.load(AA14 / f"{model}_trait_pca_directions.npz")
        frozen_sha = hashlib.sha256((AA14 / f"{model}_trait_pca_directions.npz").read_bytes()).hexdigest()
        mean, directions = frozen["mean"].astype(np.float64), frozen["directions"].astype(np.float64)
        assert mean.shape == (dim,) and directions.shape == (239, dim)
        trait_names, trait_scores = aa14_rows("trait_pc_scores_all.csv", model, "trait")
        persona_names, persona_scores = aa14_rows("projected_personas_all_pcs.csv", model, "persona")
        assert len(trait_names) == 240 and len(persona_names) == 275
        ood_threshold = reference_ood(trait_scores)

        pooled, units, scores, centered, diagnostics = {}, {}, {}, {}, {}
        max_layer_pool_error = 0.0
        for item in items:
            item_id = item["item_id"]
            for form in FORMS:
                path = private_root / model / f"{item_id}__{form}.npz"
                assert path.exists(), f"Missing extraction: {path.name} for {model}"
                assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest_cases[(item_id, form)]["sha256"]
                with np.load(path) as source:
                    layer = source["all_layer_contrast"].astype(np.float64)
                    vector = source["pooled_vector"].astype(np.float64)
                    paired = source["unit_pooled_differences"].astype(np.float64)
                    assert source["protocol_sha256"].item() == protocol_hash
                assert layer.shape == (layers, dim) and vector.shape == (dim,) and paired.shape[1:] == (dim,)
                assert 38 <= len(paired) <= 40
                assert np.isfinite(layer).all() and np.isfinite(vector).all() and np.isfinite(paired).all()
                max_layer_pool_error = max(max_layer_pool_error, float(np.max(abs(layer.mean(0) - vector))))
                key = (item_id, form)
                pooled[key], units[key] = vector, paired
                z = vector - mean
                pc = z @ directions.T
                residual20sq = max(float(z @ z - pc[:K] @ pc[:K]), 0.0)
                residualfullsq = max(float(z @ z - pc @ pc), 0.0)
                norm = float(np.linalg.norm(z))
                assert norm > 0 and np.sum(pc ** 2) <= norm * norm * (1 + 1e-5)
                dist = cdist(pc[None, :K], trait_scores[:, :K])[0]
                dist_full = cdist(pc[None, :], trait_scores)[0]
                nearest = np.argsort(dist)[:5]
                farthest = np.argsort(dist)[-5:][::-1]
                nearest_full = np.argsort(dist_full)[:5]
                pooled20 = float(np.sum(pc[:K] ** 2))
                diagnostic = {
                    "model": model, "item_id": item_id, "formulation": form,
                    "centered_norm": norm, "projected_norm_squared_20": pooled20,
                    "captured_fraction_20": pooled20 / (norm * norm),
                    "residual_norm_20": residual20sq ** 0.5,
                    "projected_norm_squared_full": float(np.sum(pc ** 2)),
                    "residual_norm_full": residualfullsq ** 0.5,
                    "distance_from_trait_center_20": float(np.linalg.norm(pc[:K])),
                    "distance_from_trait_center_full": float(np.linalg.norm(pc)),
                    "nearest_trait_distance_20": float(dist[nearest[0]]),
                    "nearest_trait_distance_full": float(dist_full[nearest_full[0]]),
                    "ood_threshold_20": ood_threshold,
                    "ood": int(dist[nearest[0]] > ood_threshold),
                }
                neighborhood_rows.append({"model": model, "item_id": item_id, "formulation": form,
                                          "nearest_traits": ";".join(trait_names[i] for i in nearest),
                                          "nearest_distances_20": ";".join(f"{dist[i]:.8f}" for i in nearest),
                                          "nearest_traits_full": ";".join(trait_names[i] for i in nearest_full),
                                          "nearest_distances_full": ";".join(f"{dist_full[i]:.8f}" for i in nearest_full),
                                          "farthest_traits": ";".join(trait_names[i] for i in farthest),
                                          "farthest_distances_20": ";".join(f"{dist[i]:.8f}" for i in farthest)})
                coord_rows.append({"model": model, "item_id": item_id, "formulation": form,
                                   **{f"trait_pc{i+1}": float(v) for i, v in enumerate(pc)}})
                diagnostic_rows.append(diagnostic)
                centered[key], scores[key], diagnostics[key] = z, pc, diagnostic
        assert max_layer_pool_error < 0.002

        primary = np.stack([centered[(name, FORMS[0])] for name in expected_ids])
        primary_scores = np.stack([scores[(name, FORMS[0])] for name in expected_ids])
        unit_primary = [units[(name, FORMS[0])] for name in expected_ids]
        centroid = primary.mean(0)
        centroid_dir = centroid / np.linalg.norm(centroid)
        centroid_score = primary_scores.mean(0)
        centroid_rows.append({"model": model, "definition": "mean_primary_positive_pole_centered_vectors",
                              "activation_space_norm": float(np.linalg.norm(centroid)),
                              **{f"trait_pc{i+1}": float(v) for i, v in enumerate(centroid_score)}})
        loo_count = sum((primary[i] @ (primary.sum(0) - primary[i])) > 0 for i in range(13))
        boot_centroids = np.zeros((BOOT, dim), dtype=np.float64)
        for paired in unit_primary:
            draws = rng.integers(0, len(paired), size=(BOOT, len(paired)))
            boot_centroids += paired[draws].mean(axis=1) / 13
        boot_centroids -= mean
        boot_cos = (boot_centroids @ centroid_dir) / np.linalg.norm(boot_centroids, axis=1)
        boot_q05 = float(np.quantile(boot_cos, 0.05))
        comp = compactness(primary_scores, np.linalg.norm(primary, axis=1), trait_scores, rng)
        same_pole, opposite_pole = [], []
        for item in items:
            item_id = item["item_id"]
            for form in FORMS[1:]:
                similarity = cosine(pooled[(item_id, FORMS[0])], pooled[(item_id, form)])
                expected = "opposite" if item["reverse_keyed"] == "1" else "same"
                stability_rows.append({"model": model, "item_id": item_id, "formulation": form,
                                       "raw_vector_cosine_to_primary": similarity,
                                       "expected_pole_relation": expected,
                                       "meets_0_8_expected_relation": int(similarity <= -0.8 if expected == "opposite" else similarity >= 0.8),
                                       "pc20_coordinate_distance": float(np.linalg.norm(scores[(item_id, form)][:K] - scores[(item_id, FORMS[0])][:K]))})
                (opposite_pole if expected == "opposite" else same_pole).append(similarity)
        compact_rows.append({"model": model, **comp, "centroid_norm": float(np.linalg.norm(centroid)),
                             "centroid_pc1": float(centroid_score[0]), "centroid_pc2": float(centroid_score[1]),
                             "centroid_pc3": float(centroid_score[2]),
                             "leave_one_out_positive_count": int(loo_count),
                             "bootstrap_centroid_cosine_q05": boot_q05,
                             "same_pole_median_cosine": float(np.median(same_pole)),
                             "opposite_pole_median_cosine": float(np.median(opposite_pole)),
                             "stable_direction_gate": int(bool(comp["matched_null_valid"] and comp["matched_compactness_p"] < .05
                              and loo_count >= 10 and np.median(same_pole) >= .8
                              and np.median(opposite_pole) <= -.8 and boot_q05 >= .8))})
        for item in items:
            item_id = item["item_id"]
            p = scores[(item_id, FORMS[0])]
            boot = units[(item_id, FORMS[0])]
            draws = rng.integers(0, len(boot), size=(BOOT, len(boot)))
            boot_pc = (boot[draws].mean(axis=1) - mean) @ directions[:3].T
            diagnostic = diagnostics[(item_id, FORMS[0])]
            diagnostic.update({f"pc{j+1}_bootstrap_q05": float(np.quantile(boot_pc[:, j], .05)) for j in range(3)})
            diagnostic.update({f"pc{j+1}_bootstrap_q95": float(np.quantile(boot_pc[:, j], .95)) for j in range(3)})

        stable = bool(compact_rows[-1]["stable_direction_gate"])
        for kind, names, pcs in (("trait", trait_names, trait_scores), ("persona", persona_names, persona_scores)):
            output = trait_rows if kind == "trait" else persona_rows
            for name, pc in zip(names, pcs):
                z = source_centered(folder, "trait" if kind == "trait" else "role", name, mean)
                nearest = int(np.argmin(np.linalg.norm(primary_scores[:, :K] - pc[:K], axis=1)))
                output.append({"model": model, "kind": kind, "name": name,
                               "signed_projection_on_centroid_direction": float(z @ centroid_dir),
                               "activation_cosine_to_centroid_direction": cosine(z, centroid_dir),
                               "distance_to_indicator_centroid_20": float(np.linalg.norm(pc[:K] - centroid_score[:K])),
                               "nearest_indicator": expected_ids[nearest],
                               "centroid_direction_stable": int(stable),
                               "uncertainty_flag": "direction_not_validated" if not stable else "prompt_bootstrap_only"})

        std = trait_scores[:, :K].std(0, ddof=1)
        per_model[model] = {"trait_names": trait_names, "trait_scores": trait_scores,
                            "persona_names": persona_names, "persona_scores": persona_scores,
                            "indicator_scores": scores, "primary_scores": primary_scores,
                            "std": std, "stable": stable,
                            "nearest": {r["item_id"]: r["nearest_traits"].split(";")
                                        for r in neighborhood_rows if r["model"] == model and r["formulation"] == FORMS[0]}}
        verification["models"][model] = {"items": 13, "formulations": 3,
                                          "paired_units_min": min(len(v) for v in units.values()),
                                          "paired_units_max": max(len(v) for v in units.values()),
                                          "frozen_rank": 239, "frozen_directions_sha256": frozen_sha,
                                          "max_layer_pool_error": max_layer_pool_error,
                                          "stable_direction_gate": stable}

    qref = per_model["qwen"]
    for model in MODELS:
        record = per_model[model]
        if model == "qwen":
            rotation = np.eye(K)
        else:
            assert record["trait_names"] == qref["trait_names"]
            rotation, _ = orthogonal_procrustes(record["trait_scores"][:, :K] / record["std"],
                                                qref["trait_scores"][:, :K] / qref["std"])
        record["rotation_to_qwen"] = rotation
        record["aligned_primary"] = record["primary_scores"][:, :K] / record["std"] @ rotation
    model_names = list(MODELS)
    for i in range(len(model_names)):
        for j in range(i+1, len(model_names)):
            a_name, b_name = model_names[i], model_names[j]
            a, b = per_model[a_name]["aligned_primary"], per_model[b_name]["aligned_primary"]
            observed = float(np.mean(np.linalg.norm(a-b, axis=1)))
            null = np.array([np.mean(np.linalg.norm(a-b[rng.permutation(13)], axis=1)) for _ in range(NULL)])
            pvalue = float((1 + (null <= observed).sum()) / (NULL+1))
            centroid_cos = cosine(a.mean(0), b.mean(0))
            geometry_corr = float(np.corrcoef(pdist(a), pdist(b))[0, 1])
            a_basis = np.linalg.svd(a-a.mean(0), full_matrices=False)[2][:3].T
            b_basis = np.linalg.svd(b-b.mean(0), full_matrices=False)[2][:3].T
            angles = subspace_angles(a_basis, b_basis)
            cross_subspace_rows.append({"left": a_name, "right": b_name,
                                        "subspace": "top_three_centered_indicator_directions_in_aligned_standardized_trait_pc20",
                                        "principal_angles_degrees": ";".join(f"{np.degrees(v):.8f}" for v in angles),
                                        "canonical_correlations": ";".join(f"{np.cos(v):.8f}" for v in angles)})
            for k, item_id in enumerate(expected_ids):
                near_a, near_b = set(per_model[a_name]["nearest"][item_id]), set(per_model[b_name]["nearest"][item_id])
                cross_rows.append({"left": a_name, "right": b_name, "item_id": item_id,
                                   "aligned_item_cosine": cosine(a[k], b[k]),
                                   "aligned_item_distance": float(np.linalg.norm(a[k]-b[k])),
                                   "nearest_five_trait_jaccard": len(near_a & near_b) / len(near_a | near_b),
                                   "mean_matched_item_distance": observed, "item_label_permutation_p": pvalue,
                                   "centroid_cosine": centroid_cos, "within_indicator_distance_correlation": geometry_corr})
            for form in FORMS:
                af = np.stack([per_model[a_name]["indicator_scores"][(n, form)][:K]
                               for n in expected_ids]) / per_model[a_name]["std"] @ per_model[a_name]["rotation_to_qwen"]
                bf = np.stack([per_model[b_name]["indicator_scores"][(n, form)][:K]
                               for n in expected_ids]) / per_model[b_name]["std"] @ per_model[b_name]["rotation_to_qwen"]
                cross_form_rows.append({"left": a_name, "right": b_name, "formulation": form,
                                        "mean_matched_item_distance": float(np.mean(np.linalg.norm(af-bf, axis=1))),
                                        "centroid_cosine": cosine(af.mean(0), bf.mean(0)),
                                        "within_indicator_distance_correlation": float(np.corrcoef(pdist(af), pdist(bf))[0, 1])})
            for population, records in (("trait", trait_rows), ("persona", persona_rows)):
                left = {r["name"]: float(r["signed_projection_on_centroid_direction"])
                        for r in records if r["model"] == a_name}
                right = {r["name"]: float(r["signed_projection_on_centroid_direction"])
                         for r in records if r["model"] == b_name}
                labels = sorted(left.keys() & right.keys())
                assert len(labels) == (240 if population == "trait" else 275)
                cross_ranking_rows.append({"left": a_name, "right": b_name,
                                           "population": population, "matched_labels": len(labels),
                                           "signed_direction_rank_spearman": float(spearmanr(
                                               [left[n] for n in labels], [right[n] for n in labels]).statistic),
                                           "interpret_only_if_both_direction_gates_pass": int(
                                               per_model[a_name]["stable"] and per_model[b_name]["stable"])})

    human = json.loads((HERE / "human_reference_freeze.json").read_text())
    for item in items:
        item_id = item["item_id"]
        row = {"item_id": item_id, "hifwb_domain": item["hifwb_domain"],
               "exact_wording": item["exact_item_wording"],
               "human_item_specific_sapa_pc_association": "not_available",
               "human_hifwb_internal_pc1_variance_fraction_overall": human["hifwb_first_internal_component_variance_fraction"],
               "human_sapa_pc1_r_with_hifwb_overall": human["broad_sapa_pc1_hifwb_pearson"],
               "human_sapa_pc4_r_with_hifwb_overall": human["broad_sapa_pc4_hifwb_pearson"],
               "evidence_type": "model semantic activation geometry versus separate human covariance"}
        for model in MODELS:
            p = per_model[model]["indicator_scores"][(item_id, FORMS[0])]
            row.update({f"{model}_trait_pc{k+1}": float(p[k]) for k in range(3)})
            row[f"{model}_nearest_traits"] = ";".join(per_model[model]["nearest"][item_id][:3])
        human_rows.append(row)

    write_csv("hifwb_projection_coordinates.csv", coord_rows)
    write_csv("hifwb_projection_diagnostics.csv", diagnostic_rows)
    write_csv("hifwb_prompt_stability.csv", stability_rows)
    write_csv("hifwb_trait_neighborhoods.csv", neighborhood_rows)
    write_csv("hifwb_persona_alignment.csv", persona_rows)
    write_csv("hifwb_trait_alignment.csv", trait_rows)
    write_csv("hifwb_cluster_compactness.csv", compact_rows)
    write_csv("hifwb_cross_model_alignment.csv", cross_rows)
    write_csv("hifwb_centroid_coordinates.csv", centroid_rows)
    write_csv("hifwb_cross_model_subspace.csv", cross_subspace_rows)
    write_csv("hifwb_cross_model_rankings.csv", cross_ranking_rows)
    write_csv("hifwb_cross_model_formulation_alignment.csv", cross_form_rows)
    write_csv("hifwb_human_model_crosswalk.csv", human_rows)
    verification["projection_completed"] = True
    verification["public_deployment_verified"] = False
    (HERE / "verification_report.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps({"models": verification["models"], "compactness": compact_rows}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-vector-root", type=Path, required=True)
    args = parser.parse_args()
    main(args.private_vector_root)
