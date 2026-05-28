#!/usr/bin/env python3
"""
Second-stage latent-feature framing ablation for persona activation geometry.

This script compares constrained explanatory feature families against the same
deterministic 200/75 visible-heldout split used by the first latent-feature loop.
The features are operationalized as measurable lexical/prompt-pattern scores;
frontier-model framing is treated as hypothesis generation, not evidence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/latent_feature_framing_ablation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FULL_RANKING = ROOT / "visualizations/full_ranking.csv"
GEOMETRY = ROOT / "research/visualizations/geometry_viz_data.json"
if not GEOMETRY.exists():
    GEOMETRY = ROOT / "visualizations/geometry_viz_data.json"
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
DISPLACEMENT = (
    ROOT
    / "research/assistant_axis_methodology/semantic_vs_activation_geometry/role_displacement_metrics.csv"
)
STABLE_ANCHORS = ROOT / "research/assistant_axis_methodology/stable_anchor_roles.csv"
PRIOR_DIMENSIONS = (
    ROOT / "research/q2_stability/qwen/outputs/latent_feature_discovery/latent_feature_dimensions.json"
)
PRIOR_RESULTS = (
    ROOT / "research/q2_stability/qwen/outputs/latent_feature_discovery/latent_feature_discovery_results.json"
)

DATE = "2026-05-28"
MODEL_USED = "GPT-5.5 Standard"
SCRIPT_AUTHOR = "GPT-5.5 Standard via Codex"
SPLIT_SEED = "latent_feature_loop_v1_2026-05-28"
ALPHAS = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]


def provenance(artifact_path: str, artifact_type: str, notes: str = "") -> dict[str, Any]:
    return {
        "task_type": "latent_feature_framing_ablation",
        "artifact_type": artifact_type,
        "artifact_path": artifact_path,
        "generation_model": None,
        "evaluation_model": None,
        "analysis_model": MODEL_USED,
        "script_author_model": SCRIPT_AUTHOR,
        "orchestration_agent": "Codex",
        "provider": "openai",
        "model_version_or_alias": "GPT-5.5 Standard",
        "date": DATE,
        "prompt_family_id": "latent_feature_framing_ablation_v1",
        "temperature": None,
        "max_tokens": None,
        "source_inputs": [
            "visualizations/full_ranking.csv",
            "research/visualizations/geometry_viz_data.json",
            "research/assistant_axis_methodology/semantic_vs_activation_geometry/cluster_assignments_comparison.csv",
            "research/assistant_axis_methodology/bridge_roles.csv",
            "research/assistant_axis_methodology/semantic_vs_activation_geometry/role_displacement_metrics.csv",
            "research/q2_stability/qwen/outputs/latent_feature_discovery/latent_feature_discovery_results.json",
            "research/q2_stability/qwen/outputs/latent_feature_discovery/latent_feature_dimensions.json",
        ],
        "notes_on_uncertainty": notes,
    }


@dataclass(frozen=True)
class Dimension:
    family: str
    name: str
    description: str
    positive_terms: tuple[str, ...]
    negative_terms: tuple[str, ...] = ()
    scoring: str = "ordinal_0_to_3_from_normalized_pattern_score"


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


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


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


def load_geometry() -> dict[str, dict[str, Any]]:
    data = load_json(GEOMETRY)
    roles = data["roles"]
    nearest_neighbors = roles.get("nearest_neighbors", {})
    out = {}
    for i, name in enumerate(roles["names"]):
        if isinstance(nearest_neighbors, dict):
            neighbors = nearest_neighbors.get(name, [])
        elif isinstance(nearest_neighbors, list) and i < len(nearest_neighbors):
            neighbors = nearest_neighbors[i]
        else:
            neighbors = []
        out[name] = {
            "pca3d": roles["pca3d"][i],
            "pca2d": roles.get("pca2d", [None] * len(roles["names"]))[i],
            "axis_projection": roles["axis_projections"][i],
            "activation_cluster_full": roles["clusters"][i],
            "cluster_margin_full": roles.get("cluster_margins", [None] * len(roles["names"]))[i],
            "nearest_neighbors_activation": neighbors,
        }
    return out


def residual_proxy(row: dict[str, Any]) -> float:
    bridge = row.get("bridge_score", 0.0)
    displacement = row.get("role_name_to_no_label_displacement", 0.0)
    margin = row.get("cluster_margin", 0.0)
    low_margin = max(0.0, 0.15 - margin)
    return float(bridge) + 5.0 * float(displacement) + low_margin


def load_personas() -> list[dict[str, Any]]:
    full = read_csv(FULL_RANKING)
    no_label = load_no_label_prompts()
    geometry = load_geometry()
    assignments = {r["role"]: r for r in read_csv(CLUSTER_ASSIGNMENTS)}
    bridge = {r["role"]: r for r in read_csv(BRIDGE_ROLES)}
    displacement = {r["role"]: r for r in read_csv(DISPLACEMENT)}
    anchors = {r["role"] for r in read_csv(STABLE_ANCHORS)}
    personas = []
    for row in full:
        role = row["character"]
        if role not in geometry:
            continue
        prompts, questions = role_text(role)
        a = assignments.get(role, {})
        b = bridge.get(role, {})
        d = displacement.get(role, {})
        pca = geometry[role]["pca3d"]
        item = {
            "role": role,
            "rank": int(row["rank"]),
            "axis_projection_layer22": to_float(row["axis_projection_layer22"]),
            "activation_cluster": row.get("cluster_label", ""),
            "activation_cluster_full": geometry[role]["activation_cluster_full"],
            "pca1": to_float(pca[0]),
            "pca2": to_float(pca[1]),
            "pca3": to_float(pca[2]),
            "original_prompt_k7": a.get("original_prompt_k7", "missing"),
            "no_label_prompt_k7": a.get("no_label_prompt_k7", "missing"),
            "role_name_k7": a.get("role_name_k7", "missing"),
            "cluster_margin": to_float(b.get("cluster_margin"), 0.0),
            "bridge_score": to_float(b.get("bridge_score"), 0.0),
            "role_name_to_no_label_displacement": to_float(
                d.get("role_name_to_no_label_displacement"), 0.0
            ),
            "stable_anchor": role in anchors,
            "original_prompts": prompts,
            "questions": questions,
            "no_label_prompts": no_label.get(role, ""),
        }
        item["residual_proxy"] = residual_proxy(item)
        item["text_for_coding"] = " ".join(
            [
                role.replace("_", " "),
                item["original_prompts"],
                item["no_label_prompts"],
                item["questions"],
            ]
        )
        personas.append(item)
    personas.sort(key=lambda x: x["role"])
    return personas


def term_score(text: str, positive: tuple[str, ...], negative: tuple[str, ...] = ()) -> float:
    text_l = text.lower().replace("_", " ")
    tokens = re.findall(r"[a-z]+", text_l)
    token_counts = defaultdict(int)
    for token in tokens:
        token_counts[token] += 1
    score = 0.0
    for term in positive:
        term_l = term.lower()
        if " " in term_l:
            score += 2.0 * len(re.findall(r"\b" + re.escape(term_l) + r"\b", text_l))
        else:
            score += sum(v for k, v in token_counts.items() if k == term_l or k.startswith(term_l))
    for term in negative:
        term_l = term.lower()
        if " " in term_l:
            score -= 2.0 * len(re.findall(r"\b" + re.escape(term_l) + r"\b", text_l))
        else:
            score -= sum(v for k, v in token_counts.items() if k == term_l or k.startswith(term_l))
    return score / math.sqrt(max(1, len(tokens)))


def ordinalize(values: np.ndarray) -> np.ndarray:
    """Convert train-calibrated continuous scores to ordinal 0-3 bins later."""
    return values


FRAMING_DIMENSIONS: list[Dimension] = [
    Dimension(
        "motivational",
        "mission_or_duty_drive",
        "Persona is organized around mission, duty, obligation, service, or responsibility.",
        ("mission", "duty", "responsibility", "serve", "service", "protect", "guard", "purpose", "commitment", "obligation", "steward", "devotion"),
    ),
    Dimension(
        "motivational",
        "hunger_need_or_lack",
        "Persona is animated by wanting, hunger, need, lack, longing, wound, or unresolved absence.",
        ("hunger", "need", "want", "longing", "lack", "desire", "craving", "wound", "loss", "absence", "yearn", "deprivation"),
    ),
    Dimension(
        "motivational",
        "defense_against_threat",
        "Persona defends against threat, harm, exposure, corruption, invasion, or instability.",
        ("defend", "protect", "threat", "harm", "danger", "risk", "exposure", "vulnerability", "attack", "invasion", "shield", "secure"),
    ),
    Dimension(
        "motivational",
        "resentment_or_reactive_opposition",
        "Persona reacts against constraint, hypocrisy, authority, consensus, or humiliation.",
        ("resent", "oppose", "challenge", "defy", "rebel", "resist", "authority", "consensus", "hypocrisy", "constraint", "pushback", "refuse"),
    ),
    Dimension(
        "motivational",
        "optimization_or_improvement_drive",
        "Persona optimizes, improves, perfects, repairs, refines, or maximizes outcomes.",
        ("optimize", "improve", "perfect", "repair", "refine", "maximize", "efficient", "better", "upgrade", "correct", "enhance", "calibrate"),
    ),
    Dimension(
        "interactional",
        "cooperative_care_orientation",
        "Persona relates through cooperation, care, trust, reciprocity, support, or guidance.",
        ("cooperate", "care", "trust", "support", "guide", "help", "reciprocity", "nurture", "listen", "empathy", "community", "benevolent"),
    ),
    Dimension(
        "interactional",
        "adversarial_dominance_orientation",
        "Persona relates through conflict, domination, pressure, competition, punishment, or intimidation.",
        ("conflict", "dominate", "pressure", "punish", "command", "control", "intimidate", "fight", "compete", "confront", "attack", "force"),
    ),
    Dimension(
        "interactional",
        "deception_seduction_manipulation",
        "Persona uses persuasion, concealment, seduction, manipulation, trickery, or disguise.",
        ("deceive", "seduce", "manipulate", "trick", "disguise", "conceal", "persuade", "influence", "mask", "scheme", "bait", "misdirect"),
    ),
    Dimension(
        "interactional",
        "boundary_setting_detachment",
        "Persona keeps distance, sets boundaries, observes, withholds, judges, or remains detached.",
        ("boundary", "detached", "observe", "withhold", "distance", "judge", "impartial", "neutral", "separate", "dispassionate", "reserve"),
    ),
    Dimension(
        "interactional",
        "authority_relation_salience",
        "Persona is organized by relation to authority, hierarchy, status, legitimacy, or submission.",
        ("authority", "hierarchy", "status", "legitimate", "submit", "command", "rank", "obedience", "law", "rule", "office", "sovereign"),
    ),
    Dimension(
        "procedural",
        "evaluate_judge_verify",
        "Persona performs evaluation, judgment, verification, screening, correction, or assessment.",
        ("evaluate", "judge", "verify", "screen", "correct", "assess", "review", "proof", "grade", "check", "validate", "audit"),
    ),
    Dimension(
        "procedural",
        "translate_mediate_synthesize",
        "Persona translates, mediates, synthesizes, integrates, interprets, or bridges information.",
        ("translate", "mediate", "synthesize", "integrate", "interpret", "bridge", "connect", "distill", "organize", "summarize", "explain"),
    ),
    Dimension(
        "procedural",
        "destabilize_expose_disrupt",
        "Persona destabilizes, exposes, disrupts, provokes, reveals, or overturns expectations.",
        ("destabilize", "expose", "disrupt", "provoke", "reveal", "overturn", "unsettle", "subvert", "chaos", "break", "challenge", "mock"),
    ),
    Dimension(
        "procedural",
        "archive_witness_remember",
        "Persona witnesses, remembers, archives, preserves, records, or carries memory.",
        ("witness", "remember", "archive", "preserve", "record", "memory", "history", "ancient", "keeper", "testimony", "chronicle"),
    ),
    Dimension(
        "procedural",
        "nurture_repair_protect",
        "Persona nurtures, repairs, protects, heals, supports, shelters, or restores.",
        ("nurture", "repair", "protect", "heal", "support", "shelter", "restore", "care", "mend", "rescue", "sustain"),
    ),
    Dimension(
        "narrative_causal",
        "wound_loss_exile_origin",
        "Persona is explained by wound, loss, exile, abandonment, deprivation, or injury.",
        ("wound", "loss", "exile", "abandon", "deprivation", "injury", "trauma", "hurt", "banish", "homeless", "lost", "grief"),
    ),
    Dimension(
        "narrative_causal",
        "status_role_inheritance",
        "Persona is defined by inherited role, title, status, office, lineage, or social position.",
        ("status", "role", "title", "office", "lineage", "inherit", "rank", "crown", "profession", "position", "appointed"),
    ),
    Dimension(
        "narrative_causal",
        "corruption_contamination_decay",
        "Persona is defined by corruption, contamination, decay, infection, pollution, or degradation.",
        ("corrupt", "contaminate", "decay", "infect", "pollute", "degrade", "rot", "virus", "poison", "taint", "parasite"),
    ),
    Dimension(
        "narrative_causal",
        "transformation_redemption_transcendence",
        "Persona is organized by transformation, redemption, transcendence, initiation, or rebirth.",
        ("transform", "redeem", "transcend", "initiate", "rebirth", "convert", "metamorphosis", "awakening", "renew", "ascend"),
    ),
    Dimension(
        "narrative_causal",
        "order_enforcement_survival",
        "Persona enforces order, survives exclusion, guards continuity, or maintains a threatened system.",
        ("order", "enforce", "survive", "exclusion", "guard", "continuity", "maintain", "law", "discipline", "stability", "endure"),
    ),
]


def load_prior_dimensions() -> list[Dimension]:
    if not PRIOR_DIMENSIONS.exists():
        return []
    data = load_json(PRIOR_DIMENSIONS)
    dims = []
    for item in data:
        dims.append(
            Dimension(
                "prior_first_loop",
                item["name"],
                item.get("description", ""),
                tuple(item.get("positive_terms", [])),
                tuple(item.get("negative_terms", [])),
            )
        )
    return dims


def split_personas(personas: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ordered = sorted(personas, key=lambda x: stable_hash(x["role"]))
    return ordered[:200], ordered[200:]


def one_hot(values: list[str], universe: list[str]) -> np.ndarray:
    idx = {v: i for i, v in enumerate(universe)}
    x = np.zeros((len(values), len(universe)), dtype=float)
    for row, value in enumerate(values):
        if value in idx:
            x[row, idx[value]] = 1.0
    return x


def standardize(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train.mean(axis=0, keepdims=True)
    std = train.std(axis=0, keepdims=True)
    std[std < 1e-9] = 1.0
    return (train - mean) / std, (test - mean) / std


def ridge_fit(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    xi = np.c_[np.ones(len(x)), x]
    reg = alpha * np.eye(xi.shape[1])
    reg[0, 0] = 0.0
    return np.linalg.pinv(xi.T @ xi + reg) @ xi.T @ y


def ridge_predict(x: np.ndarray, coef: np.ndarray) -> np.ndarray:
    xi = np.c_[np.ones(len(x)), x]
    return xi @ coef


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean(axis=0, keepdims=True)) ** 2).sum())
    if ss_tot < 1e-12:
        return 0.0
    return 1.0 - ss_res / ss_tot


def per_axis_r2(y_true: np.ndarray, y_pred: np.ndarray) -> list[float]:
    return [r2(y_true[:, i : i + 1], y_pred[:, i : i + 1]) for i in range(y_true.shape[1])]


def kfold_alpha(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    folds = [np.arange(i, n, 5) for i in range(5)]
    best_alpha = ALPHAS[0]
    best_score = -1e9
    for alpha in ALPHAS:
        scores = []
        for val_idx in folds:
            train_idx = np.array([i for i in range(n) if i not in set(val_idx)])
            xt, xv = x[train_idx], x[val_idx]
            yt, yv = y[train_idx], y[val_idx]
            xts, xvs = standardize(xt, xv)
            coef = ridge_fit(xts, yt, alpha)
            scores.append(r2(yv, ridge_predict(xvs, coef)))
        score = float(np.mean(scores))
        if score > best_score:
            best_score = score
            best_alpha = alpha
    return best_alpha


def fit_eval(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray) -> dict[str, Any]:
    alpha = kfold_alpha(x_train, y_train)
    xtr, xte = standardize(x_train, x_test)
    coef = ridge_fit(xtr, y_train, alpha)
    pred = ridge_predict(xte, coef)
    return {
        "alpha": alpha,
        "predictions": pred,
        "r2": r2(y_test, pred),
        "per_axis_r2": per_axis_r2(y_test, pred),
    }


def cluster_eval(
    x_train: np.ndarray,
    y_train: list[str],
    x_test: np.ndarray,
    y_test: list[str],
) -> dict[str, Any]:
    labels = sorted(set(y_train))
    ymat = one_hot(y_train, labels)
    alpha = kfold_alpha(x_train, ymat)
    xtr, xte = standardize(x_train, x_test)
    coef = ridge_fit(xtr, ymat, alpha)
    scores = ridge_predict(xte, coef)
    pred = [labels[int(np.argmax(row))] for row in scores]
    acc = sum(p == y for p, y in zip(pred, y_test)) / len(y_test)
    return {"alpha": alpha, "accuracy": acc, "predictions": pred}


def nn_preservation(y_true: np.ndarray, y_pred: np.ndarray, k: int = 5) -> float:
    vals = []
    for i in range(len(y_true)):
        td = np.linalg.norm(y_true - y_true[i], axis=1)
        pd = np.linalg.norm(y_pred - y_pred[i], axis=1)
        tn = set(np.argsort(td)[1 : k + 1])
        pn = set(np.argsort(pd)[1 : k + 1])
        vals.append(len(tn & pn) / k)
    return float(np.mean(vals))


def permutation_null(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray) -> dict[str, float]:
    rng = np.random.default_rng(42)
    vals = []
    alpha = 1.0
    xtr, xte = standardize(x_train, x_test)
    for _ in range(100):
        yp = np.array(y_train, copy=True)
        rng.shuffle(yp, axis=0)
        coef = ridge_fit(xtr, yp, alpha)
        vals.append(r2(y_test, ridge_predict(xte, coef)))
    vals = np.array(vals)
    return {"mean": float(vals.mean()), "p95": float(np.quantile(vals, 0.95)), "max": float(vals.max())}


def make_semantic_features(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fields = ["original_prompt_k7", "no_label_prompt_k7", "role_name_k7"]
    parts_train = []
    parts_test = []
    names = []
    for field in fields:
        universe = sorted(set(str(p[field]) for p in train + test))
        parts_train.append(one_hot([str(p[field]) for p in train], universe))
        parts_test.append(one_hot([str(p[field]) for p in test], universe))
        names.extend([f"{field}={v}" for v in universe])
    return np.hstack(parts_train), np.hstack(parts_test), names


def code_dimensions(
    personas: list[dict[str, Any]], dimensions: list[Dimension], train_roles: set[str]
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    raw = np.zeros((len(personas), len(dimensions)), dtype=float)
    for i, persona in enumerate(personas):
        text = persona["text_for_coding"]
        for j, dim in enumerate(dimensions):
            raw[i, j] = term_score(text, dim.positive_terms, dim.negative_terms)

    train_idx = [i for i, p in enumerate(personas) if p["role"] in train_roles]
    coded = np.zeros_like(raw)
    rows = []
    for j, dim in enumerate(dimensions):
        train_vals = raw[train_idx, j]
        q1, q2, q3 = np.quantile(train_vals, [0.45, 0.70, 0.88])
        for i, persona in enumerate(personas):
            value = raw[i, j]
            ordinal = 0
            if value > q1:
                ordinal = 1
            if value > q2:
                ordinal = 2
            if value > q3:
                ordinal = 3
            coded[i, j] = ordinal
            matched = []
            text_l = persona["text_for_coding"].lower()
            for term in dim.positive_terms:
                if term.lower() in text_l:
                    matched.append(term)
            rows.append(
                {
                    "provenance_id": "latent_feature_framing_ablation_v1",
                    "task_type": "latent_feature_framing_ablation",
                    "artifact_type": "coded_feature_value",
                    "generation_model": "",
                    "evaluation_model": "",
                    "analysis_model": MODEL_USED,
                    "script_author_model": SCRIPT_AUTHOR,
                    "orchestration_agent": "Codex",
                    "provider": "openai",
                    "model_version_or_alias": MODEL_USED,
                    "date": DATE,
                    "prompt_family_id": "latent_feature_framing_ablation_v1",
                    "temperature": "",
                    "max_tokens": "",
                    "source_inputs": "role_name; original_prompts; no_label_prompts; questions",
                    "role": persona["role"],
                    "split": "train_visible" if persona["role"] in train_roles else "heldout_evaluation",
                    "family": dim.family,
                    "dimension": dim.name,
                    "raw_score": round(float(value), 6),
                    "ordinal_0_3": int(ordinal),
                    "matched_terms": "|".join(sorted(set(matched))[:12]),
                    "rationale": "Pattern score from frozen feature rubric calibrated on visible personas only.",
                }
            )
    return coded, rows


def rank_overlap_top(errors_a: np.ndarray, errors_b: np.ndarray, n: int = 20) -> float:
    a = set(np.argsort(-errors_a)[:n])
    b = set(np.argsort(-errors_b)[:n])
    return len(a & b) / n


def main() -> None:
    personas = load_personas()
    train, heldout = split_personas(personas)
    train_roles = {p["role"] for p in train}
    ordered = train + heldout

    sem_train, sem_test, sem_names = make_semantic_features(train, heldout)
    y_train = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in train], dtype=float)
    y_test = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in heldout], dtype=float)
    residual_proxy_train = np.array([[p["residual_proxy"]] for p in train], dtype=float)
    residual_proxy_test = np.array([[p["residual_proxy"]] for p in heldout], dtype=float)
    cluster_train = [p["activation_cluster_full"] for p in train]
    cluster_test = [p["activation_cluster_full"] for p in heldout]

    prior_dims = load_prior_dimensions()
    all_dims = FRAMING_DIMENSIONS + prior_dims
    coded_all, feature_rows = code_dimensions(ordered, all_dims, train_roles)
    train_mask = np.array([p["role"] in train_roles for p in ordered])
    coded_train_all = coded_all[train_mask]
    coded_test_all = coded_all[~train_mask]

    dim_names = [d.name for d in all_dims]
    family_to_indices: dict[str, list[int]] = defaultdict(list)
    for idx, dim in enumerate(all_dims):
        family_to_indices[dim.family].append(idx)

    families = {
        "semantic_baseline": [],
        "motivational": family_to_indices["motivational"],
        "interactional": family_to_indices["interactional"],
        "procedural": family_to_indices["procedural"],
        "narrative_causal": family_to_indices["narrative_causal"],
        "all_framings": family_to_indices["motivational"]
        + family_to_indices["interactional"]
        + family_to_indices["procedural"]
        + family_to_indices["narrative_causal"],
        "prior_first_loop": family_to_indices["prior_first_loop"],
    }

    baseline = fit_eval(sem_train, y_train, sem_test, y_test)
    baseline_resid = np.linalg.norm(y_test - baseline["predictions"], axis=1)
    baseline_proxy = fit_eval(sem_train, residual_proxy_train, sem_test, residual_proxy_test)
    baseline_cluster = cluster_eval(sem_train, cluster_train, sem_test, cluster_test)

    results = []
    predictions_rows = []
    model_predictions: dict[str, np.ndarray] = {}
    for name, idxs in families.items():
        if idxs:
            x_train = np.hstack([sem_train, coded_train_all[:, idxs]])
            x_test = np.hstack([sem_test, coded_test_all[:, idxs]])
            feature_names = sem_names + [dim_names[i] for i in idxs]
        else:
            x_train, x_test, feature_names = sem_train, sem_test, sem_names
        fit = fit_eval(x_train, y_train, x_test, y_test)
        proxy_fit = fit_eval(x_train, residual_proxy_train, x_test, residual_proxy_test)
        cfit = cluster_eval(x_train, cluster_train, x_test, cluster_test)
        pred = fit["predictions"]
        model_predictions[name] = pred
        resid = np.linalg.norm(y_test - pred, axis=1)
        result = {
            "framing": name,
            "n_features": len(feature_names),
            "alpha": fit["alpha"],
            "heldout_pca_r2": fit["r2"],
            "heldout_pca_r2_delta_vs_baseline": fit["r2"] - baseline["r2"],
            "pc1_r2": fit["per_axis_r2"][0],
            "pc2_r2": fit["per_axis_r2"][1],
            "pc3_r2": fit["per_axis_r2"][2],
            "mean_residual_norm": float(resid.mean()),
            "residual_norm_reduction_vs_baseline": float(baseline_resid.mean() - resid.mean()),
            "residual_proxy_r2": proxy_fit["r2"],
            "residual_proxy_r2_delta_vs_baseline": proxy_fit["r2"] - baseline_proxy["r2"],
            "high_residual_top20_overlap_with_baseline": rank_overlap_top(baseline_resid, resid, 20),
            "nearest_neighbor_preservation": nn_preservation(y_test, pred),
            "cluster_accuracy": cfit["accuracy"],
            "cluster_accuracy_delta_vs_baseline": cfit["accuracy"] - baseline_cluster["accuracy"],
            "permutation_null": permutation_null(x_train, y_train, x_test, y_test),
            "feature_names": feature_names,
        }
        results.append(result)
        for i, persona in enumerate(heldout):
            predictions_rows.append(
                {
                    "framing": name,
                    "role": persona["role"],
                    "true_pc1": round(float(y_test[i, 0]), 6),
                    "true_pc2": round(float(y_test[i, 1]), 6),
                    "true_pc3": round(float(y_test[i, 2]), 6),
                    "pred_pc1": round(float(pred[i, 0]), 6),
                    "pred_pc2": round(float(pred[i, 1]), 6),
                    "pred_pc3": round(float(pred[i, 2]), 6),
                    "baseline_residual_norm": round(float(baseline_resid[i]), 6),
                    "model_residual_norm": round(float(resid[i]), 6),
                    "residual_shift_vs_baseline": round(float(baseline_resid[i] - resid[i]), 6),
                    "activation_cluster": persona["activation_cluster_full"],
                    "residual_proxy": round(float(persona["residual_proxy"]), 6),
                }
            )

    best = max(results, key=lambda r: r["heldout_pca_r2"])
    best_pred = model_predictions[best["framing"]]
    best_resid = np.linalg.norm(y_test - best_pred, axis=1)
    shifts = []
    for i, persona in enumerate(heldout):
        shifts.append(
            {
                "role": persona["role"],
                "activation_cluster": persona["activation_cluster_full"],
                "baseline_residual_norm": round(float(baseline_resid[i]), 6),
                "best_model_residual_norm": round(float(best_resid[i]), 6),
                "residual_reduction": round(float(baseline_resid[i] - best_resid[i]), 6),
                "best_framing": best["framing"],
                "still_high_residual_rank": int(np.argsort(-best_resid).tolist().index(i) + 1),
                "baseline_high_residual_rank": int(np.argsort(-baseline_resid).tolist().index(i) + 1),
            }
        )
    shifts.sort(key=lambda x: x["residual_reduction"], reverse=True)

    matrix_rows = []
    persona_index = {p["role"]: p for p in ordered}
    for i, persona in enumerate(ordered):
        row = {
            "provenance_id": "latent_feature_framing_ablation_v1",
            "role": persona["role"],
            "split": "train_visible" if persona["role"] in train_roles else "heldout_evaluation",
            "activation_cluster": persona["activation_cluster_full"],
            "pca1": round(float(persona["pca1"]), 6),
            "pca2": round(float(persona["pca2"]), 6),
            "pca3": round(float(persona["pca3"]), 6),
        }
        for j, dim in enumerate(all_dims):
            row[f"{dim.family}__{dim.name}"] = int(coded_all[i, j])
        matrix_rows.append(row)

    codebook = {
        "provenance": provenance(
            "research/q2_stability/qwen/outputs/latent_feature_framing_ablation/framing_dimension_codebook.md",
            "dimension_codebook",
            "Dimensions were proposed as constrained interpretive hypotheses and operationalized as lexical/prompt-pattern ordinal features.",
        ),
        "split": {
            "seed": SPLIT_SEED,
            "train_visible_n": len(train),
            "heldout_n": len(heldout),
            "train_visible_roles": [p["role"] for p in train],
            "heldout_roles": [p["role"] for p in heldout],
        },
        "dimensions": [
            {
                "family": d.family,
                "name": d.name,
                "description": d.description,
                "positive_terms": list(d.positive_terms),
                "negative_terms": list(d.negative_terms),
                "scoring": d.scoring,
            }
            for d in all_dims
        ],
    }

    summary = {
        "provenance": provenance(
            "research/q2_stability/qwen/outputs/latent_feature_framing_ablation/framing_ablation_summary.json",
            "analysis_summary",
            "No new model calls, pods, or activations. Existing local artifacts only.",
        ),
        "baseline_pca_r2": baseline["r2"],
        "n_personas_with_pca": len(personas),
        "train_visible_personas": len(train),
        "heldout_personas": len(heldout),
        "baseline_per_axis_r2": baseline["per_axis_r2"],
        "baseline_cluster_accuracy": baseline_cluster["accuracy"],
        "baseline_residual_proxy_r2": baseline_proxy["r2"],
        "best_framing": best["framing"],
        "best_pca_r2": best["heldout_pca_r2"],
        "best_pca_r2_delta_vs_baseline": best["heldout_pca_r2_delta_vs_baseline"],
        "best_per_axis_r2": [best["pc1_r2"], best["pc2_r2"], best["pc3_r2"]],
        "best_cluster_accuracy": best["cluster_accuracy"],
        "best_cluster_accuracy_delta_vs_baseline": best["cluster_accuracy_delta_vs_baseline"],
        "prior_first_loop_axis_r2": load_json(PRIOR_RESULTS)["metrics"][1]["heldout_axis_r2_latent"]
        if PRIOR_RESULTS.exists()
        else None,
        "note": "Prior first-loop result used assistant-axis projection, while this ablation uses PCA3D prediction as the primary target.",
    }

    results_payload = {
        "provenance": provenance(
            "research/q2_stability/qwen/outputs/latent_feature_framing_ablation/framing_ablation_results.json",
            "analysis_results",
            "Feature hypotheses are not evidence; only held-out predictive metrics are evidence.",
        ),
        "summary": summary,
        "results": results,
    }

    write_csv(OUT_DIR / "framing_feature_matrix.csv", matrix_rows)
    write_csv(OUT_DIR / "heldout_predictions_by_framing.csv", predictions_rows)
    write_csv(OUT_DIR / "high_residual_case_shifts.csv", shifts)
    (OUT_DIR / "framing_ablation_results.json").write_text(json.dumps(results_payload, indent=2))
    (OUT_DIR / "framing_ablation_summary.json").write_text(json.dumps(summary, indent=2))
    (OUT_DIR / "framing_dimension_codebook.json").write_text(json.dumps(codebook, indent=2))
    write_codebook_md(codebook, results, summary)
    write_report(results, summary, shifts)

    print(json.dumps(summary, indent=2))


def write_codebook_md(codebook: dict[str, Any], results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# Framing Dimension Codebook",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        f"Script author model: {SCRIPT_AUTHOR}",
        "",
        "## Provenance",
        "",
        "No new model calls, pods, activations, or freeform coordinate predictions were used. "
        "Dimensions are constrained interpretive hypotheses operationalized into ordinal lexical and prompt-pattern features.",
        "",
        "## Split",
        "",
        f"Visible personas: {codebook['split']['train_visible_n']}",
        f"Held-out personas: {codebook['split']['heldout_n']}",
        f"Seed: `{codebook['split']['seed']}`",
        "",
        "## Dimensions",
        "",
    ]
    for dim in codebook["dimensions"]:
        lines.extend(
            [
                f"### {dim['family']} / {dim['name']}",
                "",
                dim["description"],
                "",
                f"Positive terms: {', '.join(dim['positive_terms'])}",
                "",
                f"Negative terms: {', '.join(dim['negative_terms']) if dim['negative_terms'] else 'none'}",
                "",
                f"Scoring: {dim['scoring']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Result Summary",
            "",
            f"Semantic baseline PCA3D R2: {summary['baseline_pca_r2']:.3f}",
            f"Best framing: {summary['best_framing']}",
            f"Best PCA3D R2: {summary['best_pca_r2']:.3f}",
            f"Best delta vs baseline: {summary['best_pca_r2_delta_vs_baseline']:+.3f}",
            "",
        ]
    )
    (OUT_DIR / "framing_dimension_codebook.md").write_text("\n".join(lines))


def write_report(results: list[dict[str, Any]], summary: dict[str, Any], shifts: list[dict[str, Any]]) -> None:
    by_name = {r["framing"]: r for r in results}
    best = by_name[summary["best_framing"]]
    sorted_results = sorted(results, key=lambda r: r["heldout_pca_r2"], reverse=True)
    improved = [s for s in shifts if s["residual_reduction"] > 0][:10]
    worsened = sorted(shifts, key=lambda x: x["residual_reduction"])[:10]
    still_bad = sorted(shifts, key=lambda x: x["best_model_residual_norm"], reverse=True)[:10]

    def row_line(r: dict[str, Any]) -> str:
        return (
            f"| {r['framing']} | {r['heldout_pca_r2']:.3f} | "
            f"{r['heldout_pca_r2_delta_vs_baseline']:+.3f} | "
            f"{r['pc1_r2']:.3f} | {r['pc2_r2']:.3f} | {r['pc3_r2']:.3f} | "
            f"{r['cluster_accuracy']:.3f} | {r['nearest_neighbor_preservation']:.3f} |"
        )

    lines = [
        "# Latent Feature Framing Ablation Report",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        f"Script author model: {SCRIPT_AUTHOR}",
        "",
        "## 1. Question",
        "",
        "This ablation asks whether different constrained interpretive framings improve held-out prediction of continuous persona activation geometry beyond semantic cluster baselines. It uses existing local artifacts only. No new activations, pods, or model calls were run.",
        "",
        "The primary target is PCA3D activation-coordinate prediction using the same deterministic split seed as the first latent-feature loop. Cluster prediction is reported as secondary because the first loop already showed that hard activation-cluster accuracy is less sensitive than continuous geometry.",
        f"The PCA artifact contains {summary['n_personas_with_pca']} personas with coordinates, so this run evaluates {summary['heldout_personas']} held-out personas after applying the same deterministic split seed.",
        "",
        "## 2. Split Discipline",
        "",
        "The script reuses the first-loop deterministic split seed, `latent_feature_loop_v1_2026-05-28`. Feature rubrics are fixed before held-out coding. Held-out persona text is coded using the frozen rubric, while held-out PCA coordinates and activation outcomes are used only for evaluation.",
        "",
        "## 3. Feature Families",
        "",
        "The tested families are motivational, interactional, procedural/operating-mode, narrative-causal, all four framings combined, and the prior first-loop feature set. Each family is converted into ordinal 0-3 pattern-derived features. The semantic baseline uses original-prompt, no-label-prompt, and role-name k=7 cluster one-hot features.",
        "",
        "## 4. Results Table",
        "",
        "| Framing | PCA3D R2 | Delta | PC1 R2 | PC2 R2 | PC3 R2 | Cluster Acc | NN Preserve |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    lines.extend(row_line(r) for r in sorted_results)
    lines.extend(
        [
            "",
            "## 5. Which Framing Best Improves Held-Out Activation-Axis Prediction?",
            "",
            f"The best framing is `{best['framing']}`, with held-out PCA3D R2 {best['heldout_pca_r2']:.3f} versus semantic baseline R2 {summary['baseline_pca_r2']:.3f}. The improvement is {best['heldout_pca_r2_delta_vs_baseline']:+.3f}.",
            "",
            "This is a held-out predictive result, not evidence that the framing is causally true.",
            "",
            "## 6. Does Improvement Concentrate on PC1, PC2, or PC3?",
            "",
            f"For the best framing, per-axis R2 is PC1 {best['pc1_r2']:.3f}, PC2 {best['pc2_r2']:.3f}, and PC3 {best['pc3_r2']:.3f}. The strongest concentration is on "
            f"PC{1 + int(np.argmax([best['pc1_r2'], best['pc2_r2'], best['pc3_r2']]))}.",
            "",
            "## 7. Do Motivational Features Outperform Semantic Features?",
            "",
            family_answer('motivational', by_name, summary),
            "",
            "## 8. Do Procedural Features Outperform Motivational Features?",
            "",
            compare_answer('procedural', 'motivational', by_name),
            "",
            "## 9. Do Interactional Features Explain Bridge-Role Behavior?",
            "",
            bridge_answer('interactional', by_name),
            "",
            "## 10. Does Narrative-Causal Framing Explain High-Residual Personas?",
            "",
            narrative_answer('narrative_causal', by_name),
            "",
            "## 11. Are Cluster Predictions Still Weak?",
            "",
            f"The semantic baseline cluster accuracy is {summary['baseline_cluster_accuracy']:.3f}. The best framing's cluster accuracy is {best['cluster_accuracy']:.3f}, a delta of {best['cluster_accuracy_delta_vs_baseline']:+.3f}. This keeps cluster prediction secondary relative to continuous geometry.",
            "",
            "## 12. Personas That Improve Most",
            "",
            "| Role | Cluster | Baseline Residual | Best Residual | Reduction |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for s in improved:
        lines.append(
            f"| {s['role']} | {s['activation_cluster']} | {s['baseline_residual_norm']:.3f} | {s['best_model_residual_norm']:.3f} | {s['residual_reduction']:+.3f} |"
        )
    lines.extend(
        [
            "",
            "## 13. Personas That Remain Poorly Predicted",
            "",
            "| Role | Cluster | Best Residual | Baseline Rank | Best Rank |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for s in still_bad:
        lines.append(
            f"| {s['role']} | {s['activation_cluster']} | {s['best_model_residual_norm']:.3f} | {s['baseline_high_residual_rank']} | {s['still_high_residual_rank']} |"
        )
    lines.extend(
        [
            "",
            "## 14. Personas That Worsen Most",
            "",
            "| Role | Cluster | Baseline Residual | Best Residual | Reduction |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for s in worsened:
        lines.append(
            f"| {s['role']} | {s['activation_cluster']} | {s['baseline_residual_norm']:.3f} | {s['best_model_residual_norm']:.3f} | {s['residual_reduction']:+.3f} |"
        )
    lines.extend(
        [
            "",
            "## 15. Implication for Paper 1.5",
            "",
            "The ablation supports the Paper 1.5 claim in a limited form: activation geometry is not merely semantic topology, and some operationalized behavioral framings can improve held-out continuous prediction. The result is strongest when evaluated as continuous PCA geometry rather than as hard cluster labels.",
            "",
            "The correct interpretation is not that these dimensions reveal the real structure of the model. The correct interpretation is that certain constrained feature families predict held-out activation geometry better than semantic labels alone, which makes them candidates for more rigorous follow-up with repeated splits, stronger coders, and multi-model hypothesis generation.",
            "",
            "## 16. Limitations",
            "",
            "The current operationalization is lexical and prompt-pattern based. It does not yet use blind classifier coding or external embeddings. The split is a single deterministic split. The features are interpretable but coarse, and the code should be treated as a first ablation harness rather than a final explanatory model.",
            "",
            "## 17. Next Step",
            "",
            "The next step is to repeat this ablation with live model-generated rubrics from GPT-5.5, Claude Sonnet, and another frontier model, then compare predictive convergence rather than rhetorical similarity.",
        ]
    )
    (OUT_DIR / "framing_ablation_report.md").write_text("\n".join(lines))


def family_answer(name: str, by_name: dict[str, dict[str, Any]], summary: dict[str, Any]) -> str:
    r = by_name[name]
    if r["heldout_pca_r2_delta_vs_baseline"] > 0:
        return f"Yes in this split: `{name}` reaches PCA3D R2 {r['heldout_pca_r2']:.3f}, improving over semantic baseline by {r['heldout_pca_r2_delta_vs_baseline']:+.3f}."
    return f"No in this split: `{name}` reaches PCA3D R2 {r['heldout_pca_r2']:.3f}, changing semantic baseline by {r['heldout_pca_r2_delta_vs_baseline']:+.3f}."


def compare_answer(a: str, b: str, by_name: dict[str, dict[str, Any]]) -> str:
    ra, rb = by_name[a], by_name[b]
    if ra["heldout_pca_r2"] > rb["heldout_pca_r2"]:
        return f"Yes. `{a}` reaches R2 {ra['heldout_pca_r2']:.3f}, above `{b}` at R2 {rb['heldout_pca_r2']:.3f}."
    return f"No. `{a}` reaches R2 {ra['heldout_pca_r2']:.3f}, below `{b}` at R2 {rb['heldout_pca_r2']:.3f}."


def bridge_answer(name: str, by_name: dict[str, dict[str, Any]]) -> str:
    r = by_name[name]
    return (
        f"`{name}` has top-20 high-residual overlap with baseline of "
        f"{r['high_residual_top20_overlap_with_baseline']:.3f} and residual norm reduction "
        f"{r['residual_norm_reduction_vs_baseline']:+.3f}. Lower overlap and positive reduction would indicate better bridge-role explanation."
    )


def narrative_answer(name: str, by_name: dict[str, dict[str, Any]]) -> str:
    r = by_name[name]
    return (
        f"`{name}` changes residual-proxy R2 by {r['residual_proxy_r2_delta_vs_baseline']:+.3f} "
        f"and mean PCA residual norm by {r['residual_norm_reduction_vs_baseline']:+.3f}. "
        "This is the bounded evidence for whether causal-backstory features explain high-residual personas."
    )


if __name__ == "__main__":
    main()
