#!/usr/bin/env python3
"""Sparse observed-cell product-multinomial latent-class model.

Missing entries are encoded as zero in ``responses`` and never enter the CSR
item-category design matrix, likelihood, or category sufficient statistics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.special import logsumexp
from scipy.sparse import csr_matrix


@dataclass
class SparseResponses:
    design: csr_matrix
    n_items: int
    n_categories: int
    answered: np.ndarray

    @property
    def n_rows(self) -> int:
        return self.design.shape[0]

    @property
    def n_observed(self) -> int:
        return int(self.design.nnz)


@dataclass
class LCASolution:
    k: int
    seed: int
    pi: np.ndarray
    theta: np.ndarray
    log_likelihood: float
    iterations: int
    converged: bool
    monotone: bool
    history: np.ndarray
    responsibilities: np.ndarray


def build_sparse_responses(
    responses: np.ndarray, n_categories: int = 6, observed_mask: np.ndarray | None = None
) -> SparseResponses:
    x = np.asarray(responses)
    if x.ndim != 2:
        raise ValueError("responses must be a two-dimensional array")
    if observed_mask is None:
        observed = x != 0
    else:
        observed = np.asarray(observed_mask, dtype=bool)
        if observed.shape != x.shape:
            raise ValueError("observed_mask shape differs from responses")
    rows, items = np.nonzero(observed)
    values = x[rows, items].astype(np.int16, copy=False)
    if len(values) and (values.min() < 1 or values.max() > n_categories):
        raise ValueError("observed responses must be in 1..n_categories")
    columns = items.astype(np.int64) * n_categories + (values - 1)
    design = csr_matrix(
        (np.ones(len(rows), dtype=np.float64), (rows, columns)),
        shape=(x.shape[0], x.shape[1] * n_categories),
        dtype=np.float64,
    )
    return SparseResponses(
        design=design,
        n_items=x.shape[1],
        n_categories=n_categories,
        answered=np.asarray(observed.sum(axis=1), dtype=np.int32),
    )


def _m_step(
    data: SparseResponses, responsibilities: np.ndarray, alpha: float
) -> tuple[np.ndarray, np.ndarray]:
    nk = responsibilities.sum(axis=0)
    if np.any(nk <= 0):
        raise FloatingPointError("empty effective class")
    pi = nk / nk.sum()
    counts_flat = np.asarray(data.design.T @ responsibilities)
    counts = counts_flat.reshape(data.n_items, data.n_categories, -1).transpose(2, 0, 1)
    theta = counts + alpha
    theta /= theta.sum(axis=2, keepdims=True)
    return pi, theta


def log_joint(data: SparseResponses, pi: np.ndarray, theta: np.ndarray) -> np.ndarray:
    if theta.shape != (len(pi), data.n_items, data.n_categories):
        raise ValueError("theta shape does not match data and pi")
    flat_log_theta = np.log(np.clip(theta, 1e-300, 1.0)).reshape(len(pi), -1)
    result = np.asarray(data.design @ flat_log_theta.T)
    result += np.log(np.clip(pi, 1e-300, 1.0))[None, :]
    return result


def posterior_and_loglik(
    data: SparseResponses, pi: np.ndarray, theta: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    joint = log_joint(data, pi, theta)
    row_loglik = logsumexp(joint, axis=1)
    posterior = np.exp(joint - row_loglik[:, None])
    return posterior, row_loglik, float(row_loglik.sum())


def fit_lca(
    data: SparseResponses,
    k: int,
    seed: int,
    *,
    alpha: float = 0.5,
    dirichlet_concentration: float = 0.35,
    max_iter: int = 250,
    min_iter: int = 25,
    tolerance_per_observation: float = 1e-7,
    consecutive_tolerance: int = 5,
    monotonicity_relative_tolerance: float = 1e-8,
) -> LCASolution:
    if data.n_rows < k:
        raise ValueError("fewer rows than classes")
    if data.n_observed <= 0:
        raise ValueError("no observed responses")
    rng = np.random.default_rng(seed)
    responsibilities = rng.dirichlet(
        np.full(k, dirichlet_concentration, dtype=np.float64), size=data.n_rows
    )
    pi, theta = _m_step(data, responsibilities, alpha)
    history: list[float] = []
    converged = False
    monotone = True
    stable_steps = 0

    for iteration in range(1, max_iter + 1):
        responsibilities, _, ll = posterior_and_loglik(data, pi, theta)
        history.append(ll)
        if len(history) > 1:
            delta = history[-1] - history[-2]
            if delta < -monotonicity_relative_tolerance * max(1.0, abs(history[-2])):
                monotone = False
                break
            if delta / data.n_observed < tolerance_per_observation:
                stable_steps += 1
            else:
                stable_steps = 0
        if iteration >= min_iter and stable_steps >= consecutive_tolerance:
            converged = True
            break
        pi, theta = _m_step(data, responsibilities, alpha)

    # Synchronize posterior and reported likelihood with the returned parameters.
    responsibilities, _, ll = posterior_and_loglik(data, pi, theta)
    if not history or ll != history[-1]:
        if history and ll < history[-1] - monotonicity_relative_tolerance * max(1.0, abs(history[-1])):
            monotone = False
        history.append(ll)
    return LCASolution(
        k=k,
        seed=seed,
        pi=pi,
        theta=theta,
        log_likelihood=ll,
        iterations=iteration,
        converged=converged,
        monotone=monotone,
        history=np.asarray(history, dtype=np.float64),
        responsibilities=responsibilities,
    )


def expected_scores(theta: np.ndarray) -> np.ndarray:
    categories = np.arange(1, theta.shape[2] + 1, dtype=np.float64)
    return np.tensordot(theta, categories, axes=([2], [0]))


def canonical_profile_order(theta: np.ndarray) -> np.ndarray:
    scores = expected_scores(theta)
    # np.lexsort uses the last key as primary. Mean response is primary; the
    # reversed score columns supply deterministic lexicographic tie-breaks.
    keys: list[np.ndarray] = [scores[:, j] for j in range(scores.shape[1] - 1, -1, -1)]
    keys.append(scores.mean(axis=1))
    return np.lexsort(tuple(keys))


def reorder_solution(solution: LCASolution, order: np.ndarray) -> LCASolution:
    order = np.asarray(order, dtype=int)
    return LCASolution(
        k=solution.k,
        seed=solution.seed,
        pi=solution.pi[order],
        theta=solution.theta[order],
        log_likelihood=solution.log_likelihood,
        iterations=solution.iterations,
        converged=solution.converged,
        monotone=solution.monotone,
        history=solution.history.copy(),
        responsibilities=solution.responsibilities[:, order],
    )


def profile_distance_matrix(
    reference_theta: np.ndarray,
    candidate_theta: np.ndarray,
    item_weights: np.ndarray,
) -> np.ndarray:
    if reference_theta.shape[1:] != candidate_theta.shape[1:]:
        raise ValueError("profile item/category shapes differ")
    weights = np.asarray(item_weights, dtype=np.float64)
    weights = weights / weights.sum()
    cost = np.empty((len(reference_theta), len(candidate_theta)), dtype=np.float64)
    for a in range(len(reference_theta)):
        p = np.clip(reference_theta[a], 1e-300, 1.0)
        for b in range(len(candidate_theta)):
            q = np.clip(candidate_theta[b], 1e-300, 1.0)
            m = 0.5 * (p + q)
            js_item = 0.5 * np.sum(p * np.log(p / m), axis=1) + 0.5 * np.sum(
                q * np.log(q / m), axis=1
            )
            cost[a, b] = float(np.sum(weights * np.sqrt(np.maximum(js_item, 0.0))))
    return cost


def align_profiles(
    reference_theta: np.ndarray,
    candidate_theta: np.ndarray,
    item_weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    if len(reference_theta) != len(candidate_theta):
        raise ValueError("alignment requires equal K")
    cost = profile_distance_matrix(reference_theta, candidate_theta, item_weights)
    rows, cols = linear_sum_assignment(cost)
    if not np.array_equal(rows, np.arange(len(rows))):
        raise AssertionError("unexpected Hungarian row ordering")
    matched = cost[rows, cols]
    return cols, matched, float(matched.mean())


def fit_multiple_starts(
    data: SparseResponses,
    k: int,
    seeds: Iterable[int],
    **fit_kwargs: object,
) -> list[LCASolution]:
    solutions = [fit_lca(data, k, int(seed), **fit_kwargs) for seed in seeds]
    return sorted(solutions, key=lambda s: (-int(s.converged and s.monotone), -s.log_likelihood, s.seed))


def free_parameter_count(k: int, n_items: int, n_categories: int = 6) -> int:
    return (k - 1) + k * n_items * (n_categories - 1)


def normalized_entropy(responsibilities: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = np.clip(responsibilities, 1e-300, 1.0)
    raw = -np.sum(p * np.log(p), axis=1)
    normalized = raw / np.log(responsibilities.shape[1])
    return raw, normalized


def profile_labels(k: int) -> list[str]:
    if k > 26:
        raise ValueError("anonymous label helper supports K<=26")
    return [f"Profile {chr(65 + i)}" for i in range(k)]
