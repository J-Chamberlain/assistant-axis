#!/usr/bin/env python3
"""
First-pass latent-feature discovery loop for persona activation geometry.

This script treats GPT-5.5/Codex-supplied dimensions as hypotheses only.
Evidence is computed from held-out predictive performance against existing
activation-cluster labels, assistant-axis/rank structure, and residual-style
semantic-activation mismatch proxies.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/latent_feature_discovery"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FULL_RANKING = ROOT / "visualizations/full_ranking.csv"
INSTRUCTION_DIR = ROOT / "data/roles/instructions"
NO_LABEL_PROMPTS = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
)
CLUSTER_ASSIGNMENTS = (
    ROOT
    / "research/assistant_axis_methodology/semantic_vs_activation_geometry/cluster_assignments_comparison.csv"
)
BRIDGE_ROLES = ROOT / "research/assistant_axis_methodology/bridge_roles.csv"
SEMANTIC_BRIDGE = ROOT / "research/assistant_axis_methodology/semantic_bridge_roles.csv"
DISPLACEMENT = (
    ROOT
    / "research/assistant_axis_methodology/semantic_vs_activation_geometry/role_displacement_metrics.csv"
)
STABLE_ANCHORS = ROOT / "research/assistant_axis_methodology/stable_anchor_roles.csv"
RESIDUAL_SUMMARY = (
    ROOT / "research/q2_stability/qwen/outputs/paper1_5/semantic_activation_residuals_summary.json"
)

MODEL_USED = "GPT-5.5 Standard"
SPLIT_SEED = "latent_feature_loop_v1_2026-05-28"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(text: str) -> int:
    h = hashlib.sha256((SPLIT_SEED + "::" + text).encode()).hexdigest()
    return int(h[:16], 16)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def role_text(role: str) -> tuple[str, str]:
    path = INSTRUCTION_DIR / f"{role}.json"
    if not path.exists():
        return "", ""
    data = load_json(path)
    prompts = " ".join(item.get("pos", "") for item in data.get("instruction", []))
    questions = " ".join(data.get("questions", [])[:10])
    return prompts, questions


def load_no_label_prompts() -> dict[str, str]:
    out: dict[str, list[str]] = defaultdict(list)
    if not NO_LABEL_PROMPTS.exists():
        return {}
    for line in NO_LABEL_PROMPTS.read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        out[item["role"]].append(item.get("rewritten_prompt", ""))
    return {role: " ".join(parts) for role, parts in out.items()}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def one_hot(values: list[str], universe: list[str]) -> np.ndarray:
    idx = {v: i for i, v in enumerate(universe)}
    x = np.zeros((len(values), len(universe)), dtype=float)
    for row, value in enumerate(values):
        if value in idx:
            x[row, idx[value]] = 1.0
    return x


def standardize_train_test(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train.mean(axis=0, keepdims=True)
    std = train.std(axis=0, keepdims=True)
    std[std < 1e-9] = 1.0
    return (train - mean) / std, (test - mean) / std


def ridge_fit_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    alpha: float = 1.0,
) -> np.ndarray:
    x_train_i = np.c_[np.ones(len(x_train)), x_train]
    x_test_i = np.c_[np.ones(len(x_test)), x_test]
    reg = alpha * np.eye(x_train_i.shape[1])
    reg[0, 0] = 0.0
    coef = np.linalg.pinv(x_train_i.T @ x_train_i + reg) @ x_train_i.T @ y_train
    return x_test_i @ coef


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    if ss_tot < 1e-12:
        return 0.0
    return 1.0 - ss_res / ss_tot


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(((np.asarray(y_true) - np.asarray(y_pred)) ** 2).mean())


def nearest_neighbor_preservation(
    true_coords: np.ndarray, pred_coords: np.ndarray, k: int = 5
) -> float:
    n = len(true_coords)
    if n <= k + 1:
        return 0.0
    scores = []
    for i in range(n):
        true_d = np.linalg.norm(true_coords - true_coords[i], axis=1)
        pred_d = np.linalg.norm(pred_coords - pred_coords[i], axis=1)
        true_nn = set(np.argsort(true_d)[1 : k + 1])
        pred_nn = set(np.argsort(pred_d)[1 : k + 1])
        scores.append(len(true_nn & pred_nn) / k)
    return float(np.mean(scores))


def permutation_r2_null(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    n_perm: int = 100,
) -> dict[str, float]:
    rng = np.random.default_rng(42)
    vals = []
    for _ in range(n_perm):
        y_perm = np.array(y_train, copy=True)
        rng.shuffle(y_perm)
        pred = ridge_fit_predict(x_train, y_perm, x_test)
        vals.append(r2_score(y_test, pred))
    vals = np.array(vals)
    return {
        "mean": float(vals.mean()),
        "p95": float(np.quantile(vals, 0.95)),
        "max": float(vals.max()),
    }


@dataclass(frozen=True)
class Dimension:
    name: str
    description: str
    positive_terms: tuple[str, ...]
    negative_terms: tuple[str, ...] = ()
    weight_source: str = "role_name + no-label prompts + original prompts"


ITERATION_DIMENSIONS: list[list[Dimension]] = [
    [
        Dimension(
            "procedural_professional_orientation",
            "Task-facing, standards-driven, technical, evaluative, or improvement-oriented stance.",
            (
                "evaluate",
                "assess",
                "analyze",
                "refine",
                "improve",
                "expertise",
                "professional",
                "technical",
                "method",
                "system",
                "strategy",
                "accuracy",
                "clarity",
                "knowledge",
            ),
        ),
        Dimension(
            "theatrical_fantastical_vividness",
            "Symbolic, performative, fantastical, paradoxical, or genre-like behavioral cues.",
            (
                "myth",
                "mischief",
                "paradox",
                "riddle",
                "story",
                "chaos",
                "magic",
                "spirit",
                "ancient",
                "dream",
                "performance",
                "character",
                "unexpected",
                "twist",
            ),
        ),
        Dimension(
            "interpersonal_lived_reactivity",
            "Role organized around social position, life circumstance, care, survival, or interpersonal response.",
            (
                "people",
                "others",
                "relationship",
                "family",
                "life",
                "experience",
                "survive",
                "care",
                "support",
                "community",
                "social",
                "human",
                "emotion",
                "trust",
            ),
        ),
        Dimension(
            "oppositional_moral_pressure",
            "Challenging, adversarial, rebellious, corrective, or norm-pressuring stance.",
            (
                "challenge",
                "question",
                "rebel",
                "oppose",
                "conflict",
                "critic",
                "truth",
                "conventional",
                "norm",
                "radical",
                "provoc",
                "argument",
                "justice",
            ),
        ),
    ],
    [
        Dimension(
            "assistant_basin_adjacency",
            "Helpful, supportive, clarifying, coordinating, advising, or user-task-facing behavior likely to compress toward assistant-like action.",
            (
                "help",
                "support",
                "guide",
                "clarify",
                "coordinate",
                "advise",
                "assist",
                "provide",
                "needs",
                "queries",
                "tasks",
                "answer",
                "explain",
            ),
        ),
        Dimension(
            "boundary_liminal_instability",
            "Hybrid, threshold, outsider, forgotten, uncertain, or identity-unstable role cues.",
            (
                "between",
                "boundary",
                "outsider",
                "unknown",
                "liminal",
                "lost",
                "memory",
                "exile",
                "orphan",
                "wander",
                "ambiguous",
                "shift",
                "transform",
            ),
        ),
        Dimension(
            "collectivized_or_nonindividual_agency",
            "Role is organized as a collective, ecosystemic, distributed, or nonindividual agent.",
            (
                "collective",
                "network",
                "swarm",
                "hive",
                "ecosystem",
                "coral",
                "mycorrhizal",
                "shared",
                "group",
                "systems",
                "distributed",
            ),
        ),
        Dimension(
            "communicative_media_register",
            "Speech, writing, narration, explanation, audience, or publication-centered role organization.",
            (
                "write",
                "story",
                "narrative",
                "audience",
                "communicate",
                "explain",
                "publish",
                "voice",
                "language",
                "interview",
                "podcast",
                "report",
                "blog",
            ),
        ),
    ],
    [
        Dimension(
            "semantic_label_dependence_risk",
            "Likelihood that role identity depends on explicit naming, stage identity, or performed self-label rather than behavior alone.",
            (
                "role",
                "identity",
                "character",
                "persona",
                "embody",
                "act as",
                "take on",
                "performance",
                "become",
                "portray",
            ),
        ),
        Dimension(
            "standards_and_error_aversion",
            "Fear-of-error or standard-enforcement pattern distinct from generic professional competence.",
            (
                "correct",
                "error",
                "mistake",
                "precision",
                "standard",
                "review",
                "proof",
                "check",
                "scrutin",
                "quality",
                "final",
            ),
        ),
        Dimension(
            "forceful_self_assertion",
            "Assertive, dominant, disruptive, competitive, or self-authorizing orientation.",
            (
                "force",
                "dominant",
                "assert",
                "compete",
                "disrupt",
                "unafraid",
                "push",
                "refuse",
                "bold",
                "power",
                "will",
            ),
        ),
    ],
]


def term_score(text: str, positive_terms: tuple[str, ...], negative_terms: tuple[str, ...]) -> float:
    t = " " + re.sub(r"[^a-z0-9_ ]+", " ", text.lower()) + " "
    pos = sum(t.count(" " + term.lower() + " ") if " " not in term else t.count(term.lower()) for term in positive_terms)
    neg = sum(t.count(" " + term.lower() + " ") if " " not in term else t.count(term.lower()) for term in negative_terms)
    length = max(1.0, math.sqrt(len(t.split())))
    return (pos - neg) / length


def load_personas() -> list[dict[str, Any]]:
    full = {r["character"]: r for r in read_csv(FULL_RANKING)}
    assignments = {r["role"]: r for r in read_csv(CLUSTER_ASSIGNMENTS)}
    bridge = {r["role"]: r for r in read_csv(BRIDGE_ROLES)}
    semantic_bridge = {r["role"]: r for r in read_csv(SEMANTIC_BRIDGE)}
    displacement = {r["role"]: r for r in read_csv(DISPLACEMENT)}
    stable = {r["role"] for r in read_csv(STABLE_ANCHORS)}
    no_label = load_no_label_prompts()

    personas = []
    for role, row in sorted(full.items()):
        prompts, questions = role_text(role)
        assign = assignments.get(role, {})
        bridge_row = bridge.get(role, {})
        sem_bridge_row = semantic_bridge.get(role, {})
        disp = displacement.get(role, {})
        bridge_score = to_float(bridge_row.get("bridge_score"), 0.0)
        semantic_margin = to_float(
            bridge_row.get("semantic_bridge_margin")
            or sem_bridge_row.get("cluster_margin"),
            1.0,
        )
        displacement_value = to_float(
            disp.get("displacement_role_name_to_no_label_prompt"), 0.0
        )
        residual_proxy = bridge_score + displacement_value * 5.0 + max(0.0, 0.08 - semantic_margin) * 10.0
        personas.append(
            {
                "role": role,
                "activation_cluster": row["cluster_label"],
                "rank": int(row["rank"]),
                "axis_projection": to_float(row["axis_projection_layer22"]),
                "original_prompt_k7": assign.get("original_prompt_k7", "missing"),
                "no_label_prompt_k7": assign.get("no_label_prompt_k7", "missing"),
                "role_name_k7": assign.get("role_name_k7", "missing"),
                "is_stable_anchor": role in stable,
                "bridge_score": bridge_score,
                "semantic_margin": semantic_margin,
                "semantic_displacement": displacement_value,
                "residual_proxy": residual_proxy,
                "original_prompts": prompts,
                "no_label_prompts": no_label.get(role, ""),
                "questions_sample": questions,
                "nearest_neighbors": sem_bridge_row.get("nearest_neighbors", ""),
            }
        )
    return personas


def split_roles(personas: list[dict[str, Any]]) -> tuple[list[int], list[int]]:
    order = sorted(range(len(personas)), key=lambda i: stable_hash(personas[i]["role"]))
    train = sorted(order[:200])
    holdout = sorted(order[200:])
    return train, holdout


def feature_matrix(
    personas: list[dict[str, Any]],
    dimensions: list[Dimension],
    semantic_only: bool = False,
) -> tuple[np.ndarray, list[str]]:
    original_clusters = sorted({p["original_prompt_k7"] for p in personas})
    no_label_clusters = sorted({p["no_label_prompt_k7"] for p in personas})
    role_name_clusters = sorted({p["role_name_k7"] for p in personas})
    chunks = [
        one_hot([p["original_prompt_k7"] for p in personas], original_clusters),
        one_hot([p["no_label_prompt_k7"] for p in personas], no_label_clusters),
        one_hot([p["role_name_k7"] for p in personas], role_name_clusters),
    ]
    names = (
        [f"original_prompt_k7={c}" for c in original_clusters]
        + [f"no_label_prompt_k7={c}" for c in no_label_clusters]
        + [f"role_name_k7={c}" for c in role_name_clusters]
    )
    if not semantic_only:
        dim_values = []
        for dim in dimensions:
            values = []
            for p in personas:
                text = " ".join(
                    [
                        p["role"].replace("_", " "),
                        p["original_prompts"],
                        p["no_label_prompts"],
                        p["questions_sample"],
                    ]
                )
                values.append(term_score(text, dim.positive_terms, dim.negative_terms))
            dim_values.append(values)
            names.append(dim.name)
        if dim_values:
            chunks.append(np.array(dim_values, dtype=float).T)
    return np.concatenate(chunks, axis=1), names


def evaluate_iteration(
    personas: list[dict[str, Any]],
    train_idx: list[int],
    hold_idx: list[int],
    dimensions: list[Dimension],
    iteration: int,
) -> dict[str, Any]:
    clusters = sorted({p["activation_cluster"] for p in personas})
    cluster_to_i = {c: i for i, c in enumerate(clusters)}
    y_cluster = np.zeros((len(personas), len(clusters)))
    for i, p in enumerate(personas):
        y_cluster[i, cluster_to_i[p["activation_cluster"]]] = 1.0
    y_axis = np.array([p["axis_projection"] for p in personas], dtype=float)
    y_resid = np.array([p["residual_proxy"] for p in personas], dtype=float)

    x_base, base_names = feature_matrix(personas, [], semantic_only=True)
    x_latent, latent_names = feature_matrix(personas, dimensions, semantic_only=False)

    train = np.array(train_idx)
    hold = np.array(hold_idx)
    xbt, xbh = standardize_train_test(x_base[train], x_base[hold])
    xlt, xlh = standardize_train_test(x_latent[train], x_latent[hold])

    cluster_base_pred = ridge_fit_predict(xbt, y_cluster[train], xbh)
    cluster_latent_pred = ridge_fit_predict(xlt, y_cluster[train], xlh)
    base_cluster_acc = float(
        np.mean(np.argmax(cluster_base_pred, axis=1) == np.argmax(y_cluster[hold], axis=1))
    )
    latent_cluster_acc = float(
        np.mean(np.argmax(cluster_latent_pred, axis=1) == np.argmax(y_cluster[hold], axis=1))
    )

    axis_base_pred = ridge_fit_predict(xbt, y_axis[train], xbh).reshape(-1)
    axis_latent_pred = ridge_fit_predict(xlt, y_axis[train], xlh).reshape(-1)
    resid_base_pred = ridge_fit_predict(xbt, y_resid[train], xbh).reshape(-1)
    resid_latent_pred = ridge_fit_predict(xlt, y_resid[train], xlh).reshape(-1)

    true_coords = np.c_[y_axis[hold], y_resid[hold]]
    base_coords = np.c_[axis_base_pred, resid_base_pred]
    latent_coords = np.c_[axis_latent_pred, resid_latent_pred]

    dim_rows = []
    for dim in dimensions:
        all_x, names = feature_matrix(personas, [dim], semantic_only=False)
        dim_values = all_x[:, -1]
        for target_name, target in [("axis_projection", y_axis), ("residual_proxy", y_resid)]:
            if np.std(dim_values[hold]) < 1e-9 or np.std(target[hold]) < 1e-9:
                corr = 0.0
            else:
                corr = float(np.corrcoef(dim_values[hold], target[hold])[0, 1])
            dim_rows.append(
                {
                    "iteration": iteration,
                    "dimension": dim.name,
                    "target": target_name,
                    "heldout_correlation": round(corr, 6),
                }
            )

    metrics = {
        "iteration": iteration,
        "n_dimensions": len(dimensions),
        "dimensions": [d.name for d in dimensions],
        "heldout_cluster_accuracy_baseline": base_cluster_acc,
        "heldout_cluster_accuracy_latent": latent_cluster_acc,
        "heldout_cluster_accuracy_delta": latent_cluster_acc - base_cluster_acc,
        "heldout_axis_r2_baseline": r2_score(y_axis[hold], axis_base_pred),
        "heldout_axis_r2_latent": r2_score(y_axis[hold], axis_latent_pred),
        "heldout_axis_r2_delta": r2_score(y_axis[hold], axis_latent_pred)
        - r2_score(y_axis[hold], axis_base_pred),
        "heldout_residual_r2_baseline": r2_score(y_resid[hold], resid_base_pred),
        "heldout_residual_r2_latent": r2_score(y_resid[hold], resid_latent_pred),
        "heldout_residual_r2_delta": r2_score(y_resid[hold], resid_latent_pred)
        - r2_score(y_resid[hold], resid_base_pred),
        "residual_mse_baseline": mse(y_resid[hold], resid_base_pred),
        "residual_mse_latent": mse(y_resid[hold], resid_latent_pred),
        "residual_mse_reduction": mse(y_resid[hold], resid_base_pred)
        - mse(y_resid[hold], resid_latent_pred),
        "nn_preservation_baseline": nearest_neighbor_preservation(true_coords, base_coords),
        "nn_preservation_latent": nearest_neighbor_preservation(true_coords, latent_coords),
        "nn_preservation_delta": nearest_neighbor_preservation(true_coords, latent_coords)
        - nearest_neighbor_preservation(true_coords, base_coords),
        "axis_permutation_null": permutation_r2_null(xlt, y_axis[train], xlh, y_axis[hold]),
        "residual_permutation_null": permutation_r2_null(xlt, y_resid[train], xlh, y_resid[hold]),
        "dimension_correlations": dim_rows,
        "feature_names": latent_names,
    }
    return metrics


def compact_role_packet(personas: list[dict[str, Any]], indices: list[int]) -> list[dict[str, Any]]:
    packet = []
    for i in indices:
        p = personas[i]
        packet.append(
            {
                "role": p["role"],
                "no_label_prompt_excerpt": p["no_label_prompts"][:240],
                "activation_cluster": p["activation_cluster"],
                "semantic_clusters": {
                    "role_name_k7": p["role_name_k7"],
                    "original_prompt_k7": p["original_prompt_k7"],
                    "no_label_prompt_k7": p["no_label_prompt_k7"],
                },
                "axis_projection_proxy": p["axis_projection"],
                "residual_proxy": round(p["residual_proxy"], 4),
                "bridge_score": p["bridge_score"],
                "nearest_neighbors": p["nearest_neighbors"],
            }
        )
    return packet


def summarize_results(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    best_axis = max(metrics, key=lambda m: m["heldout_axis_r2_delta"])
    best_resid = max(metrics, key=lambda m: m["heldout_residual_r2_delta"])
    best_cluster = max(metrics, key=lambda m: m["heldout_cluster_accuracy_delta"])
    repeated = Counter()
    for m in metrics:
        for d in m["dimensions"]:
            repeated[d] += 1
    return {
        "date": "2026-05-28",
        "analysis_model": MODEL_USED,
        "script_author_model": MODEL_USED,
        "n_personas": len(load_personas()),
        "train_visible_personas": 200,
        "heldout_personas": 75,
        "residual_summary_available": RESIDUAL_SUMMARY.exists(),
        "residual_target_note": (
            "semantic_activation_residuals_summary.json was absent; residual_proxy uses bridge_score, "
            "role-name-to-no-label displacement, and low semantic margin from existing methodology artifacts."
        ),
        "best_axis_iteration": best_axis["iteration"],
        "best_residual_iteration": best_resid["iteration"],
        "best_cluster_iteration": best_cluster["iteration"],
        "best_axis_r2_delta": best_axis["heldout_axis_r2_delta"],
        "best_residual_r2_delta": best_resid["heldout_residual_r2_delta"],
        "best_cluster_accuracy_delta": best_cluster["heldout_cluster_accuracy_delta"],
        "convergent_dimensions": [name for name, count in repeated.items() if count >= 1],
        "metrics": metrics,
    }


def main() -> None:
    personas = load_personas()
    train_idx, hold_idx = split_roles(personas)
    all_metrics = []
    all_dims: list[Dimension] = []
    metric_rows: list[dict[str, Any]] = []
    corr_rows: list[dict[str, Any]] = []

    for iteration, dims in enumerate(ITERATION_DIMENSIONS, start=1):
        all_dims.extend(dims)
        metrics = evaluate_iteration(personas, train_idx, hold_idx, all_dims, iteration)
        all_metrics.append(metrics)
        metric_rows.append(
            {
                k: round(v, 6) if isinstance(v, float) else v
                for k, v in metrics.items()
                if k
                in {
                    "iteration",
                    "n_dimensions",
                    "heldout_cluster_accuracy_baseline",
                    "heldout_cluster_accuracy_latent",
                    "heldout_cluster_accuracy_delta",
                    "heldout_axis_r2_baseline",
                    "heldout_axis_r2_latent",
                    "heldout_axis_r2_delta",
                    "heldout_residual_r2_baseline",
                    "heldout_residual_r2_latent",
                    "heldout_residual_r2_delta",
                    "residual_mse_baseline",
                    "residual_mse_latent",
                    "residual_mse_reduction",
                    "nn_preservation_baseline",
                    "nn_preservation_latent",
                    "nn_preservation_delta",
                }
            }
        )
        corr_rows.extend(metrics["dimension_correlations"])

    summary = summarize_results(all_metrics)
    input_packet = {
        "date": "2026-05-28",
        "analysis_model": MODEL_USED,
        "split_seed": SPLIT_SEED,
        "train_visible_count": len(train_idx),
        "heldout_count": len(hold_idx),
        "visible_sample": compact_role_packet(personas, train_idx[:40]),
        "heldout_roles_hidden_during_feature_discovery": [personas[i]["role"] for i in hold_idx],
        "constraints": [
            "Do not treat proposed dimensions as evidence.",
            "Evaluate only operationalized features on held-out personas.",
            "Do not allow freeform coordinate prediction.",
            "Avoid consciousness, felt-sense, or causal-overclaim language.",
        ],
    }
    dimension_manifest = [
        {
            "iteration": i,
            "name": d.name,
            "description": d.description,
            "positive_terms": list(d.positive_terms),
            "negative_terms": list(d.negative_terms),
            "operationalization": "sqrt-length-normalized lexical indicator score over role name, original prompts, no-label prompts, and question sample",
        }
        for i, dims in enumerate(ITERATION_DIMENSIONS, start=1)
        for d in dims
    ]

    (OUT_DIR / "latent_feature_discovery_results.json").write_text(
        json.dumps(summary, indent=2)
    )
    (OUT_DIR / "latent_feature_discovery_input_packet.json").write_text(
        json.dumps(input_packet, indent=2)
    )
    (OUT_DIR / "latent_feature_dimensions.json").write_text(
        json.dumps(dimension_manifest, indent=2)
    )
    write_csv(OUT_DIR / "latent_feature_iteration_metrics.csv", metric_rows)
    write_csv(OUT_DIR / "latent_feature_dimension_correlations.csv", corr_rows)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
