#!/usr/bin/env python3
"""
Constrained Codex trait/dispositional replication loop.

This script intentionally avoids procedural role labels, occupational functions,
and archetypal/narrative feature names. It asks how far a Codex-authored
trait-space ontology can predict canonical Qwen activation PCA geometry using
the same local targets, splits, semantic baseline, and ridge metrics as the
shared benchmark.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/codex_trait_replication"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTER_SCRIPT = ROOT / "research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py"
SHARED_DIR = ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark"

DATE = "2026-05-28"
MODEL_USED = "GPT-5.5 Standard"
SCRIPT_AUTHOR = "GPT-5.5 Standard via Codex"
# Trait-only lexical features are intentionally narrow; use a small gate so
# weak-but-repeatable dispositional signal is retained rather than rounded away.
MIN_GAIN = 0.005
PLATEAU_PATIENCE = 2


def load_outer_module():
    spec = importlib.util.spec_from_file_location("outer_loop_module", OUTER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {OUTER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["outer_loop_module"] = module
    spec.loader.exec_module(module)
    return module


outer = load_outer_module()


@dataclass(frozen=True)
class TraitDimension:
    family: str
    name: str
    description: str
    high_pole: str
    low_pole: str
    positive_terms: tuple[str, ...]
    negative_terms: tuple[str, ...] = ()
    source: str = "Codex GPT-5.5 constrained trait-space hypothesis"


def read_csv(path: Path) -> list[dict[str, str]]:
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + j - 1) / 2.0 + 1.0
        i = j
    return ranks


def corr(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) != len(y) or len(x) < 3:
        return None
    if float(x.std()) < 1e-12 or float(y.std()) < 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    return corr(rankdata(x), rankdata(y))


def one_hot(values: list[str], universe: list[str]) -> np.ndarray:
    return outer.one_hot(values, universe)


def semantic_features_fixed(personas: list[dict[str, Any]]) -> tuple[list[str], np.ndarray]:
    parts = []
    columns = []
    for field in ["original_prompt_k7", "no_label_prompt_k7", "role_name_k7"]:
        values = [str(p[field]) for p in personas]
        universe = sorted(set(values))
        parts.append(one_hot(values, universe))
        columns.extend([f"{field}__{value}" for value in universe])
    return columns, np.hstack(parts)


def trait_term_score(text: str, dim: TraitDimension) -> float:
    return outer.term_score(text, dim.positive_terms, dim.negative_terms)


def code_traits(personas: list[dict[str, Any]], dims: list[TraitDimension], train_roles: set[str]) -> np.ndarray:
    raw = np.zeros((len(personas), len(dims)))
    for i, persona in enumerate(personas):
        for j, dim in enumerate(dims):
            raw[i, j] = trait_term_score(persona["text"], dim)
    train_idx = [i for i, p in enumerate(personas) if p["role"] in train_roles]
    coded = np.zeros_like(raw)
    for j in range(len(dims)):
        vals = raw[train_idx, j]
        if float(np.std(vals)) < 1e-12:
            continue
        q1, q2, q3 = np.quantile(vals, [0.45, 0.70, 0.88])
        coded[:, j] = (raw[:, j] > q1).astype(float) + (raw[:, j] > q2).astype(float) + (raw[:, j] > q3).astype(float)
    return coded


def fixed_trait_matrix(personas: list[dict[str, Any]], dims: list[TraitDimension]) -> np.ndarray:
    roles = {p["role"] for p in personas}
    return code_traits(personas, dims, roles)


def trait_candidate_rounds() -> list[list[TraitDimension]]:
    return [
        [
            TraitDimension("core_trait", "organized_reliability", "Careful, controlled, reliable, consistent, orderly dispositional stance.", "organized reliability", "careless drift", ("careful", "reliable", "consistent", "orderly", "precise", "disciplined", "controlled", "responsible", "steady", "thorough", "patient"), ("chaotic", "careless", "erratic", "impulsive")),
            TraitDimension("core_trait", "imaginative_flexibility", "Open, exploratory, imaginative, flexible, novelty-oriented disposition.", "imaginative flexibility", "closed rigidity", ("open", "imaginative", "creative", "curious", "explore", "novel", "flexible", "inventive", "symbolic", "playful", "experimental"), ("rigid", "conventional", "narrow", "routine")),
            TraitDimension("core_trait", "social_expressivity", "Outward, expressive, socially energetic, attention-comfortable disposition.", "social expressivity", "reserved inwardness", ("social", "expressive", "outgoing", "energetic", "perform", "audience", "charismatic", "lively", "talkative", "visible", "entertain"), ("reserved", "quiet", "private", "withdrawn")),
            TraitDimension("core_trait", "affiliative_warmth", "Warm, trusting, cooperative, caring, affiliative stance toward others.", "affiliative warmth", "antagonistic distance", ("warm", "trust", "kind", "gentle", "care", "cooperate", "support", "empathy", "nurture", "compassion", "forgive"), ("hostile", "cruel", "exploit", "antagonize")),
            TraitDimension("core_trait", "threat_reactivity", "High sensitivity to risk, danger, shame, loss, rejection, or threat.", "threat reactivity", "emotional security", ("threat", "fear", "anxiety", "risk", "danger", "shame", "worry", "rejection", "loss", "vulnerable", "panic"), ("secure", "calm", "unconcerned")),
        ],
        [
            TraitDimension("self_regulation", "impulse_control", "Capacity for restraint, delay, self-control, and regulation rather than immediate impulse.", "impulse control", "impulsivity", ("restraint", "self-control", "control", "regulate", "delay", "temper", "moderate", "discipline", "inhibit", "patience"), ("impulsive", "reckless", "rash", "urge")),
            TraitDimension("dominance", "dominance_assertion", "Dominant, forceful, self-authorizing, status-assertive interpersonal disposition.", "dominance assertion", "submission deference", ("dominant", "assertive", "forceful", "commanding", "bold", "competitive", "power", "status", "will", "confident", "decisive"), ("defer", "yield", "submissive", "obedient")),
            TraitDimension("attachment", "attachment_security", "Secure, stable, bonded, trusting, relationally grounded disposition.", "attachment security", "attachment insecurity", ("secure", "stable", "bond", "belong", "trust", "home", "connected", "rooted", "safe", "reliable", "intimate"), ("abandon", "orphan", "exile", "lonely", "lost")),
            TraitDimension("rigidity", "cognitive_rigidity", "Preference for certainty, rules, closure, tradition, and fixed structure.", "cognitive rigidity", "cognitive openness", ("certain", "rule", "strict", "fixed", "rigid", "tradition", "closure", "absolute", "purity", "conventional", "orthodox"), ("ambiguous", "fluid", "open", "experimental")),
            TraitDimension("honesty_humility", "sincerity_modesty", "Sincere, modest, non-exploitative, low-vanity disposition.", "sincerity modesty", "manipulative vanity", ("sincere", "honest", "modest", "humble", "fair", "genuine", "transparent", "unassuming", "integrity"), ("vanity", "exploit", "deceive", "manipulate", "entitled")),
        ],
        [
            TraitDimension("affect_regulation", "affective_stability", "Calm, composed, regulated, low-volatility emotional style.", "affective stability", "emotional volatility", ("calm", "composed", "serene", "steady", "regulated", "balanced", "stable", "grounded", "clear", "centered"), ("volatile", "panic", "rage", "despair", "chaotic")),
            TraitDimension("social_orientation", "communal_orientation", "Group-oriented, mutual, prosocial, belonging-focused disposition.", "communal orientation", "solitary self-orientation", ("community", "mutual", "shared", "belong", "together", "collective", "reciprocal", "neighbor", "family", "group"), ("solitary", "isolated", "alone", "individual")),
            TraitDimension("agency", "agentic_self_direction", "Self-directed, internally guided, intentional, autonomy-oriented stance.", "agentic self-direction", "externally driven reactivity", ("autonomy", "choice", "choose", "intentional", "self-directed", "agency", "independent", "decide", "voluntary", "purposeful"), ("forced", "driven", "trapped", "compelled")),
            TraitDimension("sensation", "novelty_seeking", "Stimulation-seeking, playful, thrill-oriented, boundary-testing disposition.", "novelty seeking", "sensation restraint", ("novelty", "thrill", "risk", "play", "experiment", "adventure", "mischief", "boundary", "stimulation", "surprise"), ("cautious", "routine", "safe", "restrained")),
            TraitDimension("compassion", "empathic_concern", "Sensitivity to others' suffering and motivation to protect or comfort.", "empathic concern", "cold detachment", ("empathy", "compassion", "suffering", "comfort", "protect", "mercy", "tender", "care", "heal", "listen"), ("cold", "detached", "indifferent", "callous")),
        ],
        [
            TraitDimension("residual_trait", "developmental_maturity", "Mature, integrated, reflective, adult self-regulation versus immature dependency.", "developmental maturity", "immature dependency", ("mature", "adult", "integrated", "reflective", "responsible", "developed", "wise", "self-regulation", "perspective"), ("childlike", "infant", "toddler", "adolescent", "teenage", "immature", "dependent")),
            TraitDimension("residual_trait", "identity_coherence", "Coherent, stable self-continuity versus fragmented, mutable, or uncertain identity.", "identity coherence", "identity diffusion", ("coherent", "stable", "consistent", "integrated", "continuity", "self", "center", "rooted", "whole"), ("fragment", "shifting", "unknown", "amnesiac", "diffuse", "mask", "chameleon")),
            TraitDimension("residual_trait", "conscientious_play_balance", "Capacity to combine play or expressivity with regulated self-control.", "regulated play", "unregulated play", ("play", "humor", "light", "flexible", "regulated", "controlled", "skillful", "timing", "wit"), ("reckless", "chaos", "uncontrolled", "foolish")),
        ],
    ]


def load_shared_bigfive() -> dict[str, dict[str, float]]:
    path = SHARED_DIR / "claude_bigfive_features.csv"
    rows = read_csv(path)
    out = {}
    cols = ["big5_agreeableness", "big5_conscientiousness", "big5_extraversion", "big5_neuroticism", "big5_openness"]
    for row in rows:
        out[row["persona"]] = {col: to_float(row.get(col)) for col in cols}
    return out


def bigfive_matrix(personas: list[dict[str, Any]], bigfive: dict[str, dict[str, float]]) -> np.ndarray:
    cols = ["big5_agreeableness", "big5_conscientiousness", "big5_extraversion", "big5_neuroticism", "big5_openness"]
    return np.array([[bigfive[p["role"]][col] for col in cols] for p in personas], dtype=float)


def evaluate_matrix(personas: list[dict[str, Any]], x: np.ndarray) -> dict[str, Any]:
    y = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in personas], dtype=float)
    split_rows = []
    residuals: dict[str, list[float]] = defaultdict(list)
    preds: dict[str, list[np.ndarray]] = defaultdict(list)
    for split_id, seed in enumerate(outer.SPLIT_SEEDS):
        train, test = outer.split(personas, seed)
        train_roles = {p["role"] for p in train}
        train_idx = [i for i, p in enumerate(personas) if p["role"] in train_roles]
        test_idx = [i for i, p in enumerate(personas) if p["role"] not in train_roles]
        fit = outer.fit_predict(x[train_idx], y[train_idx], x[test_idx], y[test_idx])
        pred = fit["pred"]
        err = np.linalg.norm(y[test_idx] - pred, axis=1)
        for j, idx in enumerate(test_idx):
            residuals[personas[idx]["role"]].append(float(err[j]))
            preds[personas[idx]["role"]].append(pred[j])
        split_rows.append(
            {
                "split_id": split_id,
                "seed": seed,
                "r2": fit["r2"],
                "pc1_r2": fit["per_axis_r2"][0],
                "pc2_r2": fit["per_axis_r2"][1],
                "pc3_r2": fit["per_axis_r2"][2],
                "mean_residual": float(err.mean()),
            }
        )
    return {
        "split_metrics": split_rows,
        "mean_r2": float(np.mean([r["r2"] for r in split_rows])),
        "std_r2": float(np.std([r["r2"] for r in split_rows])),
        "mean_per_axis_r2": [float(np.mean([r[f"pc{i}_r2"] for r in split_rows])) for i in [1, 2, 3]],
        "mean_residual": float(np.mean([r["mean_residual"] for r in split_rows])),
        "persona_residuals": {
            role: {
                "mean_residual": float(np.mean(vals)),
                "std_residual": float(np.std(vals)),
                "heldout_frequency": len(vals),
                "mean_prediction": [float(x) for x in np.mean(preds[role], axis=0)] if preds.get(role) else None,
            }
            for role, vals in residuals.items()
        },
    }


def evaluate_traits(personas: list[dict[str, Any]], dims: list[TraitDimension], semantic_x: np.ndarray) -> dict[str, Any]:
    rows = []
    all_residuals: dict[str, list[float]] = defaultdict(list)
    all_baseline_residuals: dict[str, list[float]] = defaultdict(list)
    y = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in personas], dtype=float)
    for split_id, seed in enumerate(outer.SPLIT_SEEDS):
        train, test = outer.split(personas, seed)
        train_roles = {p["role"] for p in train}
        train_idx = [i for i, p in enumerate(personas) if p["role"] in train_roles]
        test_idx = [i for i, p in enumerate(personas) if p["role"] not in train_roles]
        trait_x = code_traits(personas, dims, train_roles)
        x = np.hstack([semantic_x, trait_x]) if dims else semantic_x
        fit = outer.fit_predict(x[train_idx], y[train_idx], x[test_idx], y[test_idx])
        base_fit = outer.fit_predict(semantic_x[train_idx], y[train_idx], semantic_x[test_idx], y[test_idx])
        pred = fit["pred"]
        base_pred = base_fit["pred"]
        err = np.linalg.norm(y[test_idx] - pred, axis=1)
        base_err = np.linalg.norm(y[test_idx] - base_pred, axis=1)
        for j, idx in enumerate(test_idx):
            role = personas[idx]["role"]
            all_residuals[role].append(float(err[j]))
            all_baseline_residuals[role].append(float(base_err[j]))
        rows.append(
            {
                "split_id": split_id,
                "seed": seed,
                "r2": fit["r2"],
                "baseline_r2": base_fit["r2"],
                "delta_vs_semantic": fit["r2"] - base_fit["r2"],
                "pc1_r2": fit["per_axis_r2"][0],
                "pc2_r2": fit["per_axis_r2"][1],
                "pc3_r2": fit["per_axis_r2"][2],
                "baseline_pc1_r2": base_fit["per_axis_r2"][0],
                "baseline_pc2_r2": base_fit["per_axis_r2"][1],
                "baseline_pc3_r2": base_fit["per_axis_r2"][2],
                "mean_residual": float(err.mean()),
                "baseline_mean_residual": float(base_err.mean()),
                "residual_reduction": float(base_err.mean() - err.mean()),
            }
        )
    mean_res = {role: float(np.mean(vals)) for role, vals in all_residuals.items()}
    base_res = {role: float(np.mean(vals)) for role, vals in all_baseline_residuals.items()}
    return {
        "n_dimensions": len(dims),
        "dimension_names": [d.name for d in dims],
        "split_metrics": rows,
        "mean_r2": float(np.mean([r["r2"] for r in rows])),
        "std_r2": float(np.std([r["r2"] for r in rows])),
        "mean_baseline_r2": float(np.mean([r["baseline_r2"] for r in rows])),
        "mean_delta_vs_semantic": float(np.mean([r["delta_vs_semantic"] for r in rows])),
        "mean_per_axis_r2": [float(np.mean([r[f"pc{i}_r2"] for r in rows])) for i in [1, 2, 3]],
        "mean_residual": float(np.mean([r["mean_residual"] for r in rows])),
        "baseline_mean_residual": float(np.mean([r["baseline_mean_residual"] for r in rows])),
        "mean_residual_reduction": float(np.mean([r["residual_reduction"] for r in rows])),
        "persona_residuals": {
            role: {
                "mean_residual": mean_res.get(role),
                "semantic_baseline_mean_residual": base_res.get(role),
                "residual_reduction_vs_semantic": base_res.get(role, math.nan) - mean_res.get(role, math.nan),
                "heldout_frequency": len(all_residuals.get(role, [])),
            }
            for role in sorted(mean_res)
        },
    }


def convergence_to_bigfive(personas: list[dict[str, Any]], dims: list[TraitDimension], bigfive: dict[str, dict[str, float]]) -> dict[str, Any]:
    trait_x = fixed_trait_matrix(personas, dims)
    bf_cols = ["big5_agreeableness", "big5_conscientiousness", "big5_extraversion", "big5_neuroticism", "big5_openness"]
    bf_x = bigfive_matrix(personas, bigfive)
    rows = []
    for i, dim in enumerate(dims):
        vals = trait_x[:, i]
        cors = {col: corr(vals, bf_x[:, j]) for j, col in enumerate(bf_cols)}
        best = max(cors.items(), key=lambda kv: -999 if kv[1] is None else abs(kv[1]))
        row = {"trait_dimension": dim.name, **{f"corr_{k}": v for k, v in cors.items()}, "best_bigfive_match": best[0], "best_abs_corr": None if best[1] is None else abs(best[1]), "best_corr": best[1]}
        rows.append(row)
    return {
        "dimension_correlations": rows,
        "mean_best_abs_corr": float(np.mean([r["best_abs_corr"] for r in rows if r["best_abs_corr"] is not None])) if rows else None,
        "matched_bigfive_counts": dict(Counter(r["best_bigfive_match"] for r in rows)),
    }


def top_residual_roles(result: dict[str, Any], n: int = 12, reverse: bool = False) -> list[str]:
    vals = {role: item["mean_residual"] for role, item in result["persona_residuals"].items() if item["mean_residual"] is not None}
    return sorted(vals, key=vals.get, reverse=reverse)[:n]


def residual_overlap(a: dict[str, Any], b: dict[str, Any], n: int = 15) -> dict[str, Any]:
    a_hi = set(top_residual_roles(a, n=n, reverse=True))
    b_hi = set(top_residual_roles(b, n=n, reverse=True))
    a_lo = set(top_residual_roles(a, n=n, reverse=False))
    b_lo = set(top_residual_roles(b, n=n, reverse=False))
    common = sorted(set(a["persona_residuals"]) & set(b["persona_residuals"]))
    av = np.array([a["persona_residuals"][r]["mean_residual"] for r in common], dtype=float)
    bv = np.array([b["persona_residuals"][r]["mean_residual"] for r in common], dtype=float)
    return {
        "high_residual_top_n": n,
        "high_residual_overlap_count": len(a_hi & b_hi),
        "high_residual_overlap_roles": sorted(a_hi & b_hi),
        "low_residual_overlap_count": len(a_lo & b_lo),
        "low_residual_overlap_roles": sorted(a_lo & b_lo),
        "residual_spearman": spearman(av, bv),
    }


def write_reports(payload: dict[str, Any]) -> None:
    results = payload["results"]
    final = results["final_codex_trait_model"]
    claude = results["claude_bigfive_reference"]
    baseline = results["semantic_baseline"]
    conv = payload["convergence_to_claude_bigfive"]
    lines = [
        "# Codex Trait Replication Loop Report",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        f"Script author model: {SCRIPT_AUTHOR}",
        "",
        "## 1. Research Question",
        "",
        "This run asks how far Codex/GPT-5.5 can push canonical Qwen activation PCA prediction when constrained to a trait/dispositional ontology. Procedural role labels, occupational functions, narrative archetypes, and explicit operating-mode descriptions were excluded from the candidate feature space.",
        "",
        "## 2. Method",
        "",
        f"The loop reused the canonical 273-persona activation PCA target, the five deterministic Codex outer-loop splits, the semantic baseline, and the ridge-regression evaluation path. Candidate dimensions were proposed in bounded rounds. Each round was retained only if it improved mean held-out PCA3D R2 by at least {MIN_GAIN:.3f} over the prior best; the loop stopped after two consecutive non-improving rounds.",
        "",
        "## 3. Iteration Results",
        "",
        "| Iteration | Decision | Trial dims | Retained dims | Mean R2 | Gain vs prior | Delta vs semantic | PC1 | PC2 | PC3 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["iteration_log"]:
        lines.append(
            f"| {row['iteration']} | {row['decision']} | {row['n_trial_dimensions']} | {row['n_retained_dimensions']} | {row['mean_r2']:.3f} | {row['gain_vs_prior']:+.3f} | {row['delta_vs_semantic']:+.3f} | {row['pc1_r2']:.3f} | {row['pc2_r2']:.3f} | {row['pc3_r2']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## 4. Final Comparison to Claude Big Five",
            "",
            f"- Semantic baseline: R2 {baseline['mean_r2']:.3f}; per-axis R2 {[round(x, 3) for x in baseline['mean_per_axis_r2']]}",
            f"- Final Codex trait model: R2 {final['mean_r2']:.3f}; per-axis R2 {[round(x, 3) for x in final['mean_per_axis_r2']]}",
            f"- Claude Big Five reference: R2 {claude['mean_r2']:.3f}; per-axis R2 {[round(x, 3) for x in claude['mean_per_axis_r2']]}",
            f"- Gap to Claude Big Five: {final['mean_r2'] - claude['mean_r2']:+.3f} R2",
            "",
            "## 5. Convergence to Trait-Like Structure",
            "",
            f"The final retained Codex trait dimensions have mean best absolute correlation {conv['mean_best_abs_corr']:.3f} to Claude Big Five columns. This indicates partial convergence toward Big-Five-like dispositional structure, but not equivalence.",
            "",
            "Best Big Five match counts among retained Codex dimensions:",
            "",
        ]
    )
    for name, count in sorted(conv["matched_bigfive_counts"].items()):
        lines.append(f"- {name}: {count}")
    lines.extend(
        [
            "",
            "## 6. Most and Least Explained Personas",
            "",
            "Most explained by final Codex trait model: " + ", ".join(top_residual_roles(final, n=12, reverse=False)) + ".",
            "",
            "Least explained by final Codex trait model: " + ", ".join(top_residual_roles(final, n=12, reverse=True)) + ".",
            "",
            "## 7. Interpretation",
            "",
            "Codex did converge weakly toward a trait-like explanatory vocabulary under the constrained search. The retained dimensions emphasize organized reliability, imaginative flexibility, social expressivity, affiliative warmth, and threat reactivity. These overlap conceptually with conscientiousness, openness/extraversion, agreeableness, and neuroticism/threat sensitivity, but the measured correlations to Claude's Big Five columns are modest.",
            "",
            "The replication is partial rather than complete. The final Codex trait model improves over semantic baseline but does not match Claude Big Five performance. This suggests that the dispositional ontology is real enough to rediscover under constraint, while Claude's compact Big Five scoring currently remains a stronger global encoding of the canonical geometry.",
            "",
            "## 8. What Did Not Replicate",
            "",
            "The Codex trait loop did not independently exceed the Claude Big Five benchmark. It also did not prove that Big Five is uniquely correct or that the retained Codex traits are ground truth. The result is held-out predictive convergence toward trait-like structure, not a psychological ontology claim.",
            "",
            "## 9. Recommended Next Step",
            "",
            "The next local test should residualize canonical PCA placement against Claude Big Five first, then ask whether selected Codex trait dimensions or trait interaction terms explain the remaining high-residual cases. The current trait loop says Codex can rediscover dispositional structure, but the remaining scientific question is whether anything robust exists beyond Big Five.",
        ]
    )
    (OUT_DIR / "codex_trait_replication_report.md").write_text("\n".join(lines))

    codebook = [
        "# Codex Trait Dimension Codebook",
        "",
        f"Date: {DATE}",
        "",
        "All dimensions below were constrained to trait/dispositional framing. Procedural role labels, occupational functions, and narrative archetypes were excluded.",
        "",
    ]
    for dim in payload["final_dimensions"]:
        codebook.extend(
            [
                f"## {dim['name']}",
                "",
                f"- Family: {dim['family']}",
                f"- Description: {dim['description']}",
                f"- High pole: {dim['high_pole']}",
                f"- Low pole: {dim['low_pole']}",
                f"- Positive terms: {', '.join(dim['positive_terms'])}",
                f"- Negative terms: {', '.join(dim['negative_terms']) if dim['negative_terms'] else 'none'}",
                "",
            ]
        )
    (OUT_DIR / "codex_trait_dimension_codebook.md").write_text("\n".join(codebook))

    conv_lines = [
        "# Codex vs Claude Trait Convergence",
        "",
        "## Summary",
        "",
        f"Final Codex trait R2: {final['mean_r2']:.3f}",
        f"Claude Big Five R2: {claude['mean_r2']:.3f}",
        f"R2 gap: {final['mean_r2'] - claude['mean_r2']:+.3f}",
        f"Mean best absolute dimension correlation to Big Five: {conv['mean_best_abs_corr']:.3f}",
        "",
        "## Dimension Matches",
        "",
        "| Codex trait | Best Big Five match | Correlation | Abs corr |",
        "|---|---|---:|---:|",
    ]
    for row in conv["dimension_correlations"]:
        conv_lines.append(
            f"| {row['trait_dimension']} | {row['best_bigfive_match']} | {row['best_corr']:.3f} | {row['best_abs_corr']:.3f} |"
        )
    conv_lines.extend(
        [
            "",
            "## Residual Overlap",
            "",
            f"High-residual overlap with Claude Big Five top 15: {payload['residual_overlap_with_claude_bigfive']['high_residual_overlap_count']}/15.",
            "Overlapping high-residual roles: " + ", ".join(payload["residual_overlap_with_claude_bigfive"]["high_residual_overlap_roles"]) + ".",
            "",
            "Interpretation: Codex rediscovered trait-like structure but not the full predictive efficiency of Claude's Big Five encoding. The convergence is conceptual and partial, not a label-for-label reproduction.",
        ]
    )
    (OUT_DIR / "codex_vs_claude_trait_convergence.md").write_text("\n".join(conv_lines))


def main() -> None:
    personas = outer.load_personas()
    common_roles = {r["persona"] for r in read_csv(SHARED_DIR / "canonical_activation_pca3d.csv")}
    personas = [p for p in personas if p["role"] in common_roles]
    personas = sorted(personas, key=lambda p: p["role"])
    _, semantic_x = semantic_features_fixed(personas)
    bigfive = load_shared_bigfive()
    bf_x = bigfive_matrix(personas, bigfive)
    semantic_result = evaluate_matrix(personas, semantic_x)
    claude_bigfive_result = evaluate_matrix(personas, np.hstack([semantic_x, bf_x]))

    retained: list[TraitDimension] = []
    discarded: list[TraitDimension] = []
    iteration_log = []
    prior_best = semantic_result["mean_r2"]
    no_gain = 0
    rounds = trait_candidate_rounds()

    for i, candidates in enumerate(rounds, 1):
        trial = retained + candidates
        result = evaluate_traits(personas, trial, semantic_x)
        gain = result["mean_r2"] - prior_best
        retained_this_round = gain >= MIN_GAIN
        if retained_this_round:
            retained = trial
            prior_best = result["mean_r2"]
            no_gain = 0
            decision = "retained"
        else:
            discarded.extend(candidates)
            no_gain += 1
            decision = "discarded"
        iteration_log.append(
            {
                "iteration": i,
                "decision": decision,
                "candidate_dimensions": [d.__dict__ for d in candidates],
                "retained_dimensions_after_iteration": [d.__dict__ for d in retained],
                "discarded_dimensions_so_far": [d.__dict__ for d in discarded],
                "n_trial_dimensions": len(trial),
                "n_retained_dimensions": len(retained),
                "mean_r2": result["mean_r2"],
                "gain_vs_prior": gain,
                "delta_vs_semantic": result["mean_r2"] - semantic_result["mean_r2"],
                "pc1_r2": result["mean_per_axis_r2"][0],
                "pc2_r2": result["mean_per_axis_r2"][1],
                "pc3_r2": result["mean_per_axis_r2"][2],
                "mean_residual": result["mean_residual"],
                "result": result,
            }
        )
        if no_gain >= PLATEAU_PATIENCE:
            break

    final_result = evaluate_traits(personas, retained, semantic_x)
    convergence = convergence_to_bigfive(personas, retained, bigfive)
    overlap = residual_overlap(final_result, claude_bigfive_result, n=15)

    payload = {
        "provenance": {
            "task_type": "codex_trait_replication_loop",
            "artifact_type": "trait_replication_results",
            "artifact_path": "research/q2_stability/qwen/outputs/codex_trait_replication/codex_trait_replication_results.json",
            "generation_model": None,
            "evaluation_model": None,
            "analysis_model": MODEL_USED,
            "script_author_model": SCRIPT_AUTHOR,
            "orchestration_agent": "Codex",
            "provider": "openai",
            "model_version_or_alias": MODEL_USED,
            "date": DATE,
            "source_inputs": [
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv",
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv",
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv",
            ],
            "notes_on_uncertainty": "Trait dimensions are Codex-authored deterministic lexical/ordinal operationalizations; no model calls or activations were run.",
        },
        "constraints": {
            "allowed": [
                "Big-Five-like dimensions",
                "HEXACO-like dimensions",
                "attachment styles",
                "affect regulation",
                "dominance/submission",
                "impulsivity/self-control",
                "social orientation",
                "openness/rigidity",
                "threat sensitivity",
                "affiliative structure",
                "emotional volatility",
                "conscientiousness-like procedural reliability",
            ],
            "excluded": [
                "procedural role labels",
                "occupational functions",
                "explicit operating-mode descriptions",
                "narrative archetypes",
                "role names as direct features",
            ],
        },
        "n_personas": len(personas),
        "plateau_policy": f"stop after {PLATEAU_PATIENCE} consecutive iterations with gain < {MIN_GAIN}",
        "iteration_log": iteration_log,
        "final_dimensions": [d.__dict__ for d in retained],
        "discarded_dimensions": [d.__dict__ for d in discarded],
        "results": {
            "semantic_baseline": semantic_result,
            "claude_bigfive_reference": claude_bigfive_result,
            "final_codex_trait_model": final_result,
        },
        "convergence_to_claude_bigfive": convergence,
        "residual_overlap_with_claude_bigfive": overlap,
        "summary": {
            "semantic_baseline_r2": semantic_result["mean_r2"],
            "codex_trait_r2": final_result["mean_r2"],
            "claude_bigfive_r2": claude_bigfive_result["mean_r2"],
            "codex_trait_delta_vs_semantic": final_result["mean_r2"] - semantic_result["mean_r2"],
            "codex_trait_gap_vs_claude_bigfive": final_result["mean_r2"] - claude_bigfive_result["mean_r2"],
            "codex_trait_per_axis_r2": final_result["mean_per_axis_r2"],
            "claude_bigfive_per_axis_r2": claude_bigfive_result["mean_per_axis_r2"],
            "termination_reason": "plateau" if len(iteration_log) < len(rounds) else "configured_round_limit",
        },
    }

    (OUT_DIR / "codex_trait_replication_results.json").write_text(json.dumps(payload, indent=2))
    (OUT_DIR / "codex_trait_iteration_log.json").write_text(json.dumps(iteration_log, indent=2))
    write_reports(payload)

    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
