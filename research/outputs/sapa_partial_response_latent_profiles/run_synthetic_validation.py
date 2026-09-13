#!/usr/bin/env python3
"""Validate the sparse categorical LCA on known classes and SAPA-like missingness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.special import softmax
from sklearn.metrics import adjusted_rand_score

from latent_class_model import (
    align_profiles,
    build_sparse_responses,
    canonical_profile_order,
    fit_multiple_starts,
    posterior_and_loglik,
    reorder_solution,
)


SEED = 2026091302
K = 4
N = 4_000
J = 120
C = 6
STARTS = [2026091300 + 100 * K + i for i in range(1, 7)]


def simulate() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    categories = np.arange(1, C + 1, dtype=np.float64)
    base = 3.5 + 0.45 * np.sin(np.arange(J) * 0.23)
    signatures = np.empty((K, J), dtype=np.float64)
    for k in range(K):
        block = ((np.arange(J) // 15 + k) % K)
        signatures[k] = np.where(block == 0, 1.15, np.where(block == 2, -1.15, 0.0))
        signatures[k] += 0.25 * (k - 1.5)
    means = np.clip(base[None, :] + signatures, 1.35, 5.65)
    logits = -0.72 * (categories[None, None, :] - means[:, :, None]) ** 2
    true_theta = softmax(logits, axis=2)
    true_pi = np.array([0.28, 0.26, 0.24, 0.22], dtype=np.float64)
    labels = rng.choice(K, size=N, p=true_pi)
    complete = np.empty((N, J), dtype=np.int8)
    for k in range(K):
        rows = np.flatnonzero(labels == k)
        for j in range(J):
            complete[rows, j] = rng.choice(np.arange(1, C + 1), size=len(rows), p=true_theta[k, j])
    respondent_rate = np.where(rng.random(N) < 0.15, 0.40, 0.08)
    item_multiplier = np.linspace(0.72, 1.28, J)
    mask = rng.random((N, J)) < np.clip(respondent_rate[:, None] * item_multiplier[None, :], 0, 0.95)
    responses = np.where(mask, complete, 0).astype(np.int8)
    return responses, mask, labels, true_theta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    responses, mask, true_labels, true_theta = simulate()
    data = build_sparse_responses(responses, observed_mask=mask)
    solutions = fit_multiple_starts(data, K, STARTS)
    converged = [s for s in solutions if s.converged and s.monotone]
    if not converged:
        raise RuntimeError("no converged synthetic starts")
    best = converged[0]
    item_weights = np.asarray(mask.sum(axis=0), dtype=np.float64)
    candidate_order, distances, mean_distance = align_profiles(true_theta, best.theta, item_weights)
    estimated = best.theta[candidate_order]
    aligned_post = best.responsibilities[:, candidate_order]
    predicted = aligned_post.argmax(axis=1)
    ari = float(adjusted_rand_score(true_labels, predicted))
    accuracy = float(np.mean(predicted == true_labels))

    rng = np.random.default_rng(SEED + 1)
    mutated = responses.copy()
    mutated[~mask] = rng.integers(1, C + 1, size=int((~mask).sum()), dtype=np.int8)
    data_mutated = build_sparse_responses(mutated, observed_mask=mask)
    post_a, ll_rows_a, ll_a = posterior_and_loglik(data, best.pi, best.theta)
    post_b, ll_rows_b, ll_b = posterior_and_loglik(data_mutated, best.pi, best.theta)
    missing_invariance = max(
        float(np.max(np.abs(post_a - post_b))),
        float(np.max(np.abs(ll_rows_a - ll_rows_b))),
        abs(ll_a - ll_b),
    )

    permutation = np.array([2, 0, 3, 1])
    recovered_order, perm_distances, _ = align_profiles(
        true_theta, true_theta[permutation], item_weights
    )
    label_permutation_exact = bool(np.allclose(true_theta[permutation][recovered_order], true_theta))

    answered = mask.sum(axis=1)
    max_post = aligned_post.max(axis=1)
    q25, q75 = np.quantile(answered, [0.25, 0.75])
    bottom_median = float(np.median(max_post[answered <= q25]))
    top_median = float(np.median(max_post[answered >= q75]))
    history_diffs = np.diff(best.history)
    monotone = bool(np.all(history_diffs >= -1e-7 * np.maximum(1.0, np.abs(best.history[:-1]))))
    normalized = bool(
        np.allclose(best.pi.sum(), 1.0, atol=1e-12)
        and np.allclose(best.theta.sum(axis=2), 1.0, atol=1e-12)
    )

    checks = {
        "finite_monotone_likelihood": bool(np.isfinite(best.log_likelihood) and monotone),
        "probabilities_normalize": normalized,
        "mean_aligned_profile_distance_le_0_075": mean_distance <= 0.075,
        "adjusted_rand_index_ge_0_70": ari >= 0.70,
        "aligned_map_accuracy_ge_0_80": accuracy >= 0.80,
        "missing_storage_invariance_le_1e_12": missing_invariance <= 1e-12,
        "label_permutation_alignment_exact": label_permutation_exact,
        "certainty_increases_with_answer_count": top_median > bottom_median,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    metrics = {
        "status": status,
        "seed": SEED,
        "n_respondents": N,
        "n_items": J,
        "n_classes": K,
        "observed_fraction": float(mask.mean()),
        "missing_fraction": float(1 - mask.mean()),
        "median_items_answered": float(np.median(answered)),
        "starts": STARTS,
        "converged_starts": len(converged),
        "best_seed": best.seed,
        "best_iterations": best.iterations,
        "best_log_likelihood": best.log_likelihood,
        "mean_aligned_profile_distance": mean_distance,
        "per_class_profile_distance": distances.tolist(),
        "adjusted_rand_index": ari,
        "aligned_map_accuracy": accuracy,
        "missing_storage_max_absolute_effect": missing_invariance,
        "explicit_permutation": permutation.tolist(),
        "recovered_candidate_order": recovered_order.tolist(),
        "permutation_distances": perm_distances.tolist(),
        "bottom_answer_quartile_max_posterior_median": bottom_median,
        "top_answer_quartile_max_posterior_median": top_median,
        "checks": checks,
    }
    (output / "synthetic_validation_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    report = f"""# Synthetic validation report

Status: **{status}**

The frozen sparse product-multinomial implementation was tested on {N:,} simulated respondents, {J} six-category items, and {K} known latent classes. Heterogeneous class-independent planned missingness left {100*mask.mean():.2f}% of cells observed ({100*(1-mask.mean()):.2f}% missing), with a median of {np.median(answered):.0f} answered items. Missing cells entered neither the likelihood nor sufficient statistics.

Six deterministic starts were attempted and {len(converged)} converged monotonically. The retained seed was `{best.seed}` after {best.iterations} iterations. After frozen weighted Jensen–Shannon/Hungarian alignment, mean profile distance was {mean_distance:.6f}, adjusted Rand index was {ari:.6f}, and aligned MAP accuracy was {accuracy:.6f}.

Changing every stored value underneath the unchanged missingness mask had maximum likelihood/posterior effect {missing_invariance:.3e}; this verifies that unobserved values are ignored rather than imputed. An explicit class-label permutation was recovered exactly. Median maximum posterior increased from {bottom_median:.6f} in the bottom answered-count quartile to {top_median:.6f} in the top quartile.

## Frozen-gate checks

"""
    for name, passed in checks.items():
        report += f"- {name}: **{'PASS' if passed else 'FAIL'}**\n"
    report += "\nNo SAPA item wording, human/model artifact, or external personality-profile literature was used.\n"
    (output / "synthetic_validation_report.md").write_text(report, encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
