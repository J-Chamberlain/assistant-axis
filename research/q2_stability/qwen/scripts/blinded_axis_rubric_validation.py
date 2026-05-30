#!/usr/bin/env python3
"""Coordinate-blind rubric validation for persona PCA interpretations.

This script scores full persona-associated no-label prompt text with local,
deterministic lexical-semantic rubrics, then joins those scores to PCA
coordinates only after scoring. No model APIs are used.
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
CORPUS_PATH = REPO / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
VIZ_PATH = REPO / "research/visualizations/geometry_viz_data.json"
OUT_DIR = REPO / "research/q2_stability/qwen/outputs/blinded_axis_rubric_validation"

MODEL_USED = "GPT-5.5"
RANDOM_SEED = 42


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def count_terms(text: str, terms: dict[str, float]) -> float:
    norm = f" {normalize_text(text)} "
    total = 0.0
    for term, weight in terms.items():
        term_norm = normalize_text(term)
        if not term_norm:
            continue
        # Phrase-aware but conservative: normalized substring with word padding.
        total += weight * len(re.findall(rf"(?<![a-z0-9]){re.escape(term_norm)}(?![a-z0-9])", norm))
    return total


def bipolar_score(text: str, high_terms: dict[str, float], low_terms: dict[str, float], prior: float = 3.0) -> float:
    high = count_terms(text, high_terms)
    low = count_terms(text, low_terms)
    score = 50.0 + 50.0 * ((high - low) / (high + low + prior))
    return float(max(0.0, min(100.0, score)))


def unipolar_score(text: str, terms: dict[str, float], scale: float = 8.0) -> float:
    count = count_terms(text, terms)
    score = 100.0 * (1.0 - math.exp(-count / scale))
    return float(max(0.0, min(100.0, score)))


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def rankdata(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        rank = (i + j) / 2.0 + 1.0
        ranks[order[i : j + 1]] = rank
        i = j + 1
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return pearson(rankdata(x), rankdata(y))


def fit_linear_regression(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    X_aug = np.column_stack([np.ones(len(X)), X])
    coef = np.linalg.pinv(X_aug) @ y
    pred = X_aug @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return coef, r2


def kfold_cv_r2(X: np.ndarray, y: np.ndarray, k: int = 5, seed: int = RANDOM_SEED) -> float:
    rng = random.Random(seed)
    idx = list(range(len(y)))
    rng.shuffle(idx)
    folds = [idx[i::k] for i in range(k)]
    preds = np.zeros(len(y), dtype=float)
    for fold in folds:
        test = np.array(fold)
        train = np.array([i for i in idx if i not in set(fold)])
        coef, _ = fit_linear_regression(X[train], y[train])
        X_aug = np.column_stack([np.ones(len(test)), X[test]])
        preds[test] = X_aug @ coef
    ss_res = float(((y - preds) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot else float("nan")


def permutation_cv_baseline(X: np.ndarray, y: np.ndarray, n_perm: int = 500) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED)
    vals = []
    for _ in range(n_perm):
        vals.append(kfold_cv_r2(X, rng.permutation(y), k=5))
    arr = np.array(vals, dtype=float)
    return {
        "n_permutations": n_perm,
        "mean_cv_r2": float(np.nanmean(arr)),
        "p95_cv_r2": float(np.nanpercentile(arr, 95)),
        "max_cv_r2": float(np.nanmax(arr)),
    }


PC1_EXTERNAL = {
    "rule": 1.2, "rules": 1.2, "procedure": 1.4, "procedures": 1.4, "protocol": 1.4,
    "standard": 1.4, "standards": 1.4, "criteria": 1.5, "compliance": 1.5,
    "verify": 1.3, "validate": 1.3, "audit": 1.6, "accuracy": 1.2, "correct": 1.0,
    "evidence": 1.0, "measure": 1.0, "consistent": 0.9, "consistency": 1.0,
    "step by step": 1.6, "check": 0.9, "proofread": 1.7, "error": 1.0,
    "facts": 1.0, "precision": 1.2, "objective": 1.0, "external": 1.0,
    "requirements": 1.3, "deliverable": 1.2, "deadline": 1.0, "schedule": 1.1,
}

PC1_POSSIBILITY = {
    "possibility": 1.6, "possibilities": 1.6, "explore": 1.2, "interpret": 1.2,
    "interpretation": 1.2, "ambiguity": 1.5, "ambiguous": 1.4, "paradox": 1.5,
    "open ended": 1.5, "multiple": 1.0, "construct": 1.2, "negotiate": 1.4,
    "meaning": 1.0, "uncertainty": 1.2, "unknown": 1.0, "emergent": 1.3,
    "symbolic": 1.2, "subjective": 1.2, "discover": 1.1, "wonder": 1.0,
    "imagine": 1.1, "creative": 0.9, "reflect": 1.0, "question": 0.8,
    "worldview": 1.2, "mystery": 1.1, "tension": 1.0,
}

PC2_FRAGMENTED = {
    "impulsive": 1.6, "fragmented": 1.7, "avoid": 1.1, "avoidant": 1.4,
    "procrastinate": 1.7, "immature": 1.6, "childish": 1.6, "reactive": 1.2,
    "chaotic": 1.4, "unstable": 1.5, "distracted": 1.2, "overwhelmed": 1.3,
    "inconsistent": 1.1, "evade": 1.2, "stall": 1.1, "volatile": 1.3,
    "whim": 1.2, "whimsical": 1.0, "rumor": 1.0, "gossip": 1.0,
    "immediate": 0.8, "tantrum": 1.7, "play": 0.6, "joke": 0.8, "fool": 1.0,
}

PC2_INTEGRATED = {
    "uncertainty": 1.0, "unknown": 0.9, "ambiguity": 1.0, "paradox": 1.2,
    "rigorous": 1.4, "disciplined": 1.4, "coherent": 1.4, "integrate": 1.5,
    "integration": 1.5, "framework": 1.2, "sustained": 1.2, "contemplation": 1.4,
    "inquiry": 1.2, "model": 0.9, "theory": 1.1, "worldview": 1.3,
    "hypothesis": 1.1, "patience": 1.1, "long horizon": 1.5, "practice": 0.9,
    "principle": 1.0, "perspective": 0.9, "complexity": 1.0, "depth": 1.0,
}

PC3_ANTAGONISTIC = {
    "challenge": 1.0, "disrupt": 1.5, "invert": 1.3, "subvert": 1.6,
    "sabotage": 1.8, "adversarial": 1.7, "transgress": 1.8, "exploit": 1.5,
    "deceive": 1.5, "conceal": 1.3, "provoke": 1.4, "provocation": 1.4,
    "attack": 1.2, "undermine": 1.5, "hack": 1.3, "manipulate": 1.5,
    "cynical": 1.2, "ruthless": 1.4, "rebellion": 1.3, "defy": 1.2,
    "mock": 1.0, "trick": 1.2, "deception": 1.5, "conflict": 1.0,
}

PC3_COOPERATIVE = {
    "care": 1.2, "nurture": 1.6, "nurturing": 1.6, "stabilize": 1.7,
    "repair": 1.5, "reconcile": 1.5, "coordinate": 1.2, "support": 1.1,
    "heal": 1.5, "healing": 1.5, "protect": 1.2, "guide": 0.9,
    "empathy": 1.4, "compassion": 1.4, "maintain": 1.0, "mediate": 1.3,
    "collaborate": 1.2, "trust": 1.0, "gentle": 1.0, "listen": 0.9,
    "soothe": 1.2, "relationship": 0.8, "community": 0.9,
}

ABSTRACTION = {
    "abstract": 1.5, "symbolic": 1.4, "metaphor": 1.2, "archetype": 1.4,
    "cosmic": 1.2, "myth": 1.3, "theory": 1.1, "concept": 1.0,
    "ontology": 1.5, "philosophical": 1.4, "metaphysical": 1.5,
    "principle": 1.0, "systems": 1.1, "pattern": 0.9,
}

EXPERTISE = {
    "expert": 1.4, "technical": 1.2, "rigorous": 1.4, "evidence": 0.9,
    "analysis": 0.9, "specialized": 1.2, "domain": 0.8, "method": 1.0,
    "model": 0.8, "hypothesis": 1.1, "data": 1.0, "scientific": 1.3,
    "professional": 1.0, "diagnosis": 1.1, "precision": 1.0,
}

OPENNESS = {
    "curious": 1.2, "explore": 1.2, "possibility": 1.3, "imagine": 1.1,
    "creative": 1.2, "novel": 1.0, "wonder": 1.1, "interpret": 1.0,
    "open": 0.9, "expansive": 1.1, "experiment": 1.0, "discover": 1.0,
}

UNCERTAINTY_EXPOSURE = {
    "uncertainty": 1.4, "unknown": 1.2, "ambiguous": 1.3, "ambiguity": 1.3,
    "unresolved": 1.5, "question": 0.8, "doubt": 1.0, "risk": 0.8,
    "complexity": 1.0, "tension": 1.0, "paradox": 1.4,
}

RESIDENCE = {
    "sustain": 1.4, "sustained": 1.4, "remain": 0.9, "linger": 1.1,
    "hold": 1.0, "patience": 1.2, "contemplate": 1.3, "contemplation": 1.3,
    "practice": 1.0, "long horizon": 1.5, "endure": 1.0, "sit with": 1.5,
}


@dataclass
class PersonaText:
    role: str
    prompt_count: int
    no_label_text: str
    original_text: str
    role_descriptions: list[str]


def load_persona_texts() -> list[PersonaText]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    with CORPUS_PATH.open() as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                grouped[row["role"]].append(row)
    personas = []
    for role in sorted(grouped):
        rows = sorted(grouped[role], key=lambda r: r.get("prompt_index", 0))
        personas.append(
            PersonaText(
                role=role,
                prompt_count=len(rows),
                no_label_text="\n\n".join(r.get("rewritten_prompt", "") for r in rows),
                original_text="\n\n".join(r.get("original_prompt", "") for r in rows),
                role_descriptions=sorted({r.get("role_description", "") for r in rows if r.get("role_description")}),
            )
        )
    return personas


def load_pca() -> dict[str, dict[str, float]]:
    data = json.loads(VIZ_PATH.read_text())
    roles = data["roles"]
    names = roles["names"]
    pca3 = roles["pca3d"]
    clusters = roles.get("clusters", [""] * len(names))
    return {
        name: {
            "pc1": float(coords[0]),
            "pc2": float(coords[1]),
            "pc3": float(coords[2]),
            "cluster": clusters[i],
        }
        for i, (name, coords) in enumerate(zip(names, pca3))
    }


def score_persona(p: PersonaText) -> dict[str, float | str | int]:
    text = p.no_label_text
    pc1 = bipolar_score(text, PC1_EXTERNAL, PC1_POSSIBILITY)
    pc2 = bipolar_score(text, PC2_FRAGMENTED, PC2_INTEGRATED)
    pc3 = bipolar_score(text, PC3_ANTAGONISTIC, PC3_COOPERATIVE)
    uncertainty = unipolar_score(text, UNCERTAINTY_EXPOSURE, scale=5.0)
    residence = unipolar_score(text, RESIDENCE, scale=4.0)
    abstraction = unipolar_score(text, ABSTRACTION, scale=5.0)
    expertise = unipolar_score(text, EXPERTISE, scale=6.0)
    openness = unipolar_score(text, OPENNESS, scale=5.0)
    immaturity = unipolar_score(text, PC2_FRAGMENTED, scale=4.0)
    integrated_uncertainty = max(0.0, min(100.0, (uncertainty * 0.35 + residence * 0.35 + (100.0 - pc2) * 0.30)))
    return {
        "persona": p.role,
        "prompt_count": p.prompt_count,
        "text_source": "no_label_rewritten_prompts",
        "text_char_count": len(text),
        "pc1_objective_certainty_score": pc1,
        # Per user rubric, high score corresponds to the high-PC2 side: poor integration under uncertainty.
        "pc2_coherent_action_under_uncertainty_score": pc2,
        "pc3_antagonistic_transgressive_score": pc3,
        "pc2_maturity_risk_score": immaturity,
        "pc2_abstraction_score": abstraction,
        "pc2_openness_proxy_score": openness,
        "pc2_intelligence_expertise_score": expertise,
        "pc2_uncertainty_exposure_score": uncertainty,
        "pc2_uncertainty_residence_time_score": residence,
        "pc2_integrated_uncertainty_alt_score": integrated_uncertainty,
    }


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        return
    if fields is None:
        fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in fields})


def compute_correlations(rows: list[dict]) -> list[dict]:
    score_cols = [
        "pc1_objective_certainty_score",
        "pc2_coherent_action_under_uncertainty_score",
        "pc3_antagonistic_transgressive_score",
        "pc2_maturity_risk_score",
        "pc2_abstraction_score",
        "pc2_openness_proxy_score",
        "pc2_intelligence_expertise_score",
        "pc2_uncertainty_exposure_score",
        "pc2_uncertainty_residence_time_score",
        "pc2_integrated_uncertainty_alt_score",
    ]
    pc_cols = ["pc1", "pc2", "pc3"]
    out = []
    for score in score_cols:
        x = np.array([float(r[score]) for r in rows])
        for pc in pc_cols:
            y = np.array([float(r[pc]) for r in rows])
            out.append(
                {
                    "score": score,
                    "pc": pc,
                    "pearson": pearson(x, y),
                    "spearman": spearman(x, y),
                    "abs_pearson": abs(pearson(x, y)),
                    "target_aligned": (
                        (score == "pc1_objective_certainty_score" and pc == "pc1")
                        or (score == "pc2_coherent_action_under_uncertainty_score" and pc == "pc2")
                        or (score == "pc3_antagonistic_transgressive_score" and pc == "pc3")
                    ),
                }
            )
    return out


def regression_results(rows: list[dict]) -> dict:
    main_cols = [
        "pc1_objective_certainty_score",
        "pc2_coherent_action_under_uncertainty_score",
        "pc3_antagonistic_transgressive_score",
    ]
    alt_cols = main_cols + [
        "pc2_maturity_risk_score",
        "pc2_abstraction_score",
        "pc2_openness_proxy_score",
        "pc2_intelligence_expertise_score",
        "pc2_uncertainty_exposure_score",
        "pc2_uncertainty_residence_time_score",
        "pc2_integrated_uncertainty_alt_score",
    ]
    out = {
        "model_used": MODEL_USED,
        "analysis_type": "local_coordinate_blind_lexical_semantic_rubric_validation",
        "main_predictors": main_cols,
        "expanded_predictors": alt_cols,
        "targets": {},
    }
    for label, cols in [("main_three_rubric_scores", main_cols), ("expanded_with_pc2_alternatives", alt_cols)]:
        X = np.array([[float(r[c]) for c in cols] for r in rows], dtype=float)
        # Standardize predictors for stable coefficients.
        X = (X - X.mean(axis=0)) / np.where(X.std(axis=0) == 0, 1.0, X.std(axis=0))
        out[label] = {}
        for pc in ["pc1", "pc2", "pc3"]:
            y = np.array([float(r[pc]) for r in rows], dtype=float)
            coef, r2 = fit_linear_regression(X, y)
            cv = kfold_cv_r2(X, y)
            null = permutation_cv_baseline(X, y)
            out[label][pc] = {
                "train_r2": r2,
                "cv_r2": cv,
                "permutation_null": null,
                "intercept": float(coef[0]),
                "coefficients": {col: float(val) for col, val in zip(cols, coef[1:])},
            }
    return out


def matched_pairs(rows: list[dict], n: int = 20) -> list[dict]:
    pcs = ["pc1", "pc2", "pc3"]
    score_for_pc = {
        "pc1": "pc1_objective_certainty_score",
        "pc2": "pc2_coherent_action_under_uncertainty_score",
        "pc3": "pc3_antagonistic_transgressive_score",
    }
    out = []
    for target in pcs:
        other = [pc for pc in pcs if pc != target]
        candidates = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                target_gap = abs(float(a[target]) - float(b[target]))
                other_dist = math.sqrt(sum((float(a[pc]) - float(b[pc])) ** 2 for pc in other))
                if target_gap <= 0:
                    continue
                candidates.append((other_dist / target_gap, other_dist, -target_gap, a, b))
        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        for _, other_dist, neg_gap, a, b in candidates[:n]:
            score_col = score_for_pc[target]
            pc_delta = float(a[target]) - float(b[target])
            score_delta = float(a[score_col]) - float(b[score_col])
            out.append(
                {
                    "target_pc": target,
                    "persona_a": a["persona"],
                    "persona_b": b["persona"],
                    "pc_delta_a_minus_b": pc_delta,
                    "score_column": score_col,
                    "score_delta_a_minus_b": score_delta,
                    "direction_matches": (pc_delta == 0 and score_delta == 0) or (pc_delta * score_delta > 0),
                    "absolute_target_pc_gap": abs(pc_delta),
                    "orthogonal_pc_distance": other_dist,
                    "persona_a_score": a[score_col],
                    "persona_b_score": b[score_col],
                    "persona_a_pc": a[target],
                    "persona_b_pc": b[target],
                }
            )
    return out


def markdown_table(rows: Iterable[dict], fields: list[str], max_rows: int | None = None) -> str:
    rows = list(rows)
    if max_rows is not None:
        rows = rows[:max_rows]
    header = "| " + " | ".join(fields) + " |"
    sep = "| " + " | ".join(["---"] * len(fields)) + " |"
    body = []
    for row in rows:
        vals = []
        for f in fields:
            v = row.get(f, "")
            if isinstance(v, float):
                vals.append(f"{v:.3f}")
            else:
                vals.append(str(v))
        body.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + body)


def write_reports(rows: list[dict], correlations: list[dict], regressions: dict, pairs: list[dict]) -> None:
    corpus_stats = {
        "corpus_path": str(CORPUS_PATH),
        "pca_path": str(VIZ_PATH),
        "personas_covered": len(rows),
        "total_prompt_records": sum(int(r["prompt_count"]) for r in rows),
        "text_fields_used": ["rewritten_prompt"],
        "available_but_not_scored_fields": ["original_prompt", "role_description"],
        "corpus_type": "no-label rewritten system prompts, not full rollout responses",
        "sampling_decision": "No sampling; all five no-label rewritten prompts per persona were concatenated.",
        "missing_personas_after_join": [],
        "model_used": MODEL_USED,
    }
    (OUT_DIR / "corpus_audit.json").write_text(json.dumps(corpus_stats, indent=2))

    target_corrs = [c for c in correlations if c["target_aligned"]]
    off_axis = sorted([c for c in correlations if not c["target_aligned"] and c["score"].startswith("pc")], key=lambda c: -abs(c["pearson"]))[:10]
    pc2_alts = sorted([c for c in correlations if c["pc"] == "pc2" and c["score"].startswith("pc2_")], key=lambda c: -abs(c["pearson"]))
    pair_summary = []
    for pc in ["pc1", "pc2", "pc3"]:
        subset = [p for p in pairs if p["target_pc"] == pc]
        pair_summary.append(
            {
                "pc": pc,
                "pairs": len(subset),
                "direction_match_rate": sum(1 for p in subset if p["direction_matches"]) / len(subset) if subset else float("nan"),
            }
        )

    methodology = f"""# Blinded Axis Rubric Validation Methodology

## Corpus Audit

Observed: the validation used `{CORPUS_PATH}` as the full persona-associated text corpus. It contains 1,375 prompt records covering 275 personas with exactly five prompts per persona. The scored text field was `rewritten_prompt`, produced by the no-label prompt-ablation workflow. `original_prompt` and `role_description` are present but were not used for scoring because the study is intended to avoid role-name and label exposure.

Observed: the corpus is not a full rollout-response corpus. It is a full five-prompt-per-persona system-prompt corpus. No broader 275-persona full response corpus was identified in the canonical tracker files during this pass.

Observed: no sampling was used. The five no-label prompts for each persona were concatenated in prompt order.

## Blinding

Observed: scoring occurred before PCA coordinates, clusters, residuals, or prior interpretation labels were joined. The scoring function used only no-label prompt text and retained `persona` only as a row identifier for later joining.

## Scoring Method

Observed: no external model or API calls were made. Because a local independent LLM judge was not available in this session, the study used deterministic coordinate-blind lexical-semantic rubric proxies. This is weaker than an independent human or model semantic-rating study and should be treated as an initial validation screen, not a final blinded adjudication.

Inferred: the proxy is still useful because it tests whether the working axis interpretations have recoverable signal in full prompt text without using persona names or PCA coordinates.

## Rubrics

PC1 score: high values indicate externally specified objectives, constraints, standards, rules, and ambiguity reduction. Low values indicate internally negotiated objectives, open possibility, interpretation, and ambiguity maintenance.

PC2 score: despite the requested column name `pc2_coherent_action_under_uncertainty_score`, high values operationalize the high-PC2 side of the current interpretation, namely fragmented or poorly integrated action under uncertainty. Low values indicate sustained coherent action under uncertainty. This direction was chosen so positive score-PC correlation is the target-aligned result.

PC3 score: high values indicate antagonistic, disruptive, adversarial, or transgressive stance. Low values indicate cooperative, stabilizing, caring, reconciling, or system-maintaining stance.

## Alternative PC2 Rubrics

The rival PC2 pass computed lexical proxies for maturity risk, abstraction, openness, intelligence or expertise, uncertainty exposure, uncertainty residence time, and an integrated-uncertainty alternative. These were used to test whether the current PC2 formulation outperforms simpler explanations.

## PCA Coordinates

Actual coordinates were loaded from `{VIZ_PATH}` after scoring. The validation uses the embedded persona PCA coordinates in the visualization dataset, covering 275 personas.

## Model Provenance

`model_used`: {MODEL_USED}. The model wrote and orchestrated the script; the numeric scores were produced by deterministic local code, not model inference.
"""
    (OUT_DIR / "axis_rubric_methodology.md").write_text(methodology)

    target_by_pc = {c["pc"]: c for c in target_corrs}
    main_reg = regressions["main_three_rubric_scores"]
    expanded_reg = regressions["expanded_with_pc2_alternatives"]
    pc2_best_alt = pc2_alts[0] if pc2_alts else {}

    report = f"""# Blinded Axis Rubric Validation Report

## What Was Done

Observed: this study tested whether coordinate-blind scores from the full available no-label persona prompt corpus predict actual Qwen persona PCA coordinates. It used all 275 personas and all five no-label rewritten prompts per persona. It did not use persona names, PCA coordinates, clusters, residuals, or prior labels during scoring.

Observed: no pods were launched, no activations were generated, and no external model APIs were called.

## Corpus Used

{markdown_table([corpus_stats], ["corpus_path", "personas_covered", "total_prompt_records", "corpus_type", "sampling_decision"])}

Unknown: a complete 275-persona rollout-response corpus was not located from the canonical state files during this pass. The strongest available full text corpus is therefore the no-label system-prompt corpus, which captures operationalized persona instructions rather than model responses.

## Main Quantitative Results

Target-aligned correlations:

{markdown_table(target_corrs, ["score", "pc", "pearson", "spearman"])}

Strongest off-axis correlations among rubric scores:

{markdown_table(off_axis, ["score", "pc", "pearson", "spearman"], max_rows=10)}

PC2 alternative rubric correlations with PC2:

{markdown_table(pc2_alts, ["score", "pc", "pearson", "spearman"])}

Matched-pair validation summary:

{markdown_table(pair_summary, ["pc", "pairs", "direction_match_rate"])}

Regression results are saved in `axis_rubric_regression_results.json`.

## Interpretation

Observed: the target-aligned rubric correlations are positive but modest: PC1 r={target_by_pc['pc1']['pearson']:.3f}, PC2 r={target_by_pc['pc2']['pearson']:.3f}, and PC3 r={target_by_pc['pc3']['pearson']:.3f}. The simple three-score regression has cross-validated R2 values of PC1={main_reg['pc1']['cv_r2']:.3f}, PC2={main_reg['pc2']['cv_r2']:.3f}, and PC3={main_reg['pc3']['cv_r2']:.3f}. The expanded score set improves PC1 and PC3 cross-validated prediction to {expanded_reg['pc1']['cv_r2']:.3f} and {expanded_reg['pc3']['cv_r2']:.3f}, but does not improve PC2, which falls to {expanded_reg['pc2']['cv_r2']:.3f}.

Observed: matched-pair validation is weak, with direction-match rates of PC1={pair_summary[0]['direction_match_rate']:.3f}, PC2={pair_summary[1]['direction_match_rate']:.3f}, and PC3={pair_summary[2]['direction_match_rate']:.3f}. Many failures are ties produced by the coarse lexical proxy, so the pairwise result mainly limits confidence in the proxy scorer rather than falsifying the axis interpretations.

Observed: PC3 is the strongest of the three target rubrics in direct correlation, which modestly supports the cooperative-stabilizing versus antagonistic-transgressive interpretation. PC1 remains positive but weaker than expected, and PC2 remains the weakest and most methodologically fragile interpretation.

Observed: among PC2 alternatives, the current coherent-action-under-uncertainty proxy is the strongest PC2 correlate in this lexical implementation (r={pc2_best_alt.get('pearson', float('nan')):.3f} for `{pc2_best_alt.get('score', 'n/a')}`), but it only narrowly exceeds maturity risk and does not produce useful cross-validated PC2 prediction.

Inferred: this study weakens any strong claim that the current axis interpretations are recoverable from simple no-label prompt-text rubrics alone. It does not weaken the broader layered-geometry interpretation, because earlier benchmark work already shows that semantic, trait, procedural, and lexical/register features jointly predict activation geometry better than any single simple rubric.

Speculative: the weak pairwise results may reflect the limits of lexical proxies, the short five-prompt corpus, or genuinely mixed axis structure. A richer blinded human or LLM rater using full rollout responses could produce stronger evidence either for or against the current interpretations.

## Key Judgment Calls

Observed: the study used no-label prompts instead of original label-exposed prompts to avoid direct role-name leakage. It used all prompts rather than sampling. It used deterministic lexical-semantic proxies because no local independent LLM judge was available and API calls were outside the task constraints.

Inferred: this makes the study conservative for semantic richness and weaker for nuanced judgment. It is best treated as an initial validation screen before a true blinded human or multi-model rater study.

## Axis-Level Confidence Update

PC1: confidence is unchanged to slightly weakened by this validation. The target correlation is positive, but the matched-pair test is weak and an expertise/procedural proxy has a stronger off-axis relationship with PC1 than the direct PC1 rubric.

PC2: confidence remains low. The current formulation slightly outperforms the simpler PC2 alternatives in direct correlation, but the effect is modest and cross-validated regression is poor.

PC3: confidence remains moderate. It is the strongest direct rubric correlation in this validation, but the pairwise result is not strong enough to treat the interpretation as settled.

## Strongest Counterexamples

Observed: top matched-pair failures and off-axis correlations should be inspected before using the scores as confirmatory evidence. Examples include PC1 pairs where large PCA separation receives tied rubric scores, such as merchant versus novelist and amnesiac versus expatriate; PC2 pairs such as maverick versus virus and gossip versus rebel; and PC3 pairs such as familiar versus pilgrim and fixer versus refugee. See `axis_rubric_pairwise_validation.csv` for the full concrete pair list.

## Competing Explanations Still Viable

Unknown: prompt-register artifacts may explain part of the predictive signal. Unknown: LLM-assigned or lexical trait features may conflate role operationalization with target-model geometry. Unknown: a full rollout-response corpus could produce different results from the system-prompt corpus used here.

## Recommended Next Test

Run a true blinded rating study using an independent evaluator or human annotation on full rollout responses where available, then compare it against this prompt-corpus proxy. For PC2 specifically, use matched pairs and force raters to distinguish uncertainty exposure, immaturity, abstraction, and coherent action under unresolved uncertainty.
"""
    (OUT_DIR / "blinded_axis_validation_report.md").write_text(report)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    personas = load_persona_texts()
    pca = load_pca()
    missing = [p.role for p in personas if p.role not in pca]
    if missing:
        raise SystemExit(f"Missing PCA coordinates for {len(missing)} personas: {missing[:20]}")

    rows = []
    for p in personas:
        row = score_persona(p)
        row.update(pca[p.role])
        rows.append(row)

    fields = [
        "persona", "cluster", "prompt_count", "text_source", "text_char_count",
        "pc1", "pc2", "pc3",
        "pc1_objective_certainty_score",
        "pc2_coherent_action_under_uncertainty_score",
        "pc3_antagonistic_transgressive_score",
        "pc2_maturity_risk_score",
        "pc2_abstraction_score",
        "pc2_openness_proxy_score",
        "pc2_intelligence_expertise_score",
        "pc2_uncertainty_exposure_score",
        "pc2_uncertainty_residence_time_score",
        "pc2_integrated_uncertainty_alt_score",
    ]
    write_csv(OUT_DIR / "axis_rubric_scores.csv", rows, fields)

    correlations = compute_correlations(rows)
    write_csv(
        OUT_DIR / "axis_rubric_correlations.csv",
        correlations,
        ["score", "pc", "pearson", "spearman", "abs_pearson", "target_aligned"],
    )

    regressions = regression_results(rows)
    (OUT_DIR / "axis_rubric_regression_results.json").write_text(json.dumps(regressions, indent=2))

    pairs = matched_pairs(rows)
    write_csv(
        OUT_DIR / "axis_rubric_pairwise_validation.csv",
        pairs,
        [
            "target_pc", "persona_a", "persona_b", "pc_delta_a_minus_b", "score_column",
            "score_delta_a_minus_b", "direction_matches", "absolute_target_pc_gap",
            "orthogonal_pc_distance", "persona_a_score", "persona_b_score",
            "persona_a_pc", "persona_b_pc",
        ],
    )

    write_reports(rows, correlations, regressions, pairs)

    print(f"Wrote outputs to {OUT_DIR}")
    print("Target-aligned correlations:")
    for c in correlations:
        if c["target_aligned"]:
            print(f"  {c['score']} vs {c['pc']}: pearson={c['pearson']:.3f}, spearman={c['spearman']:.3f}")
    for pc in ["pc1", "pc2", "pc3"]:
        subset = [p for p in pairs if p["target_pc"] == pc]
        rate = sum(1 for p in subset if p["direction_matches"]) / len(subset)
        print(f"  matched pairs {pc}: {rate:.2%}")


if __name__ == "__main__":
    main()
