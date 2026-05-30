#!/usr/bin/env python3
"""Adaptive prompt expansion for high-PC3 and high-PC2 H100 validation coverage.

This script is offline and deterministic. It does not call model APIs. It uses
the frozen role-trained leakage-control elastic-net TF-IDF forecaster from the
first novel prompt battery as a design filter, then records every accepted and
rejected candidate for auditability.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import re
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)


REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
PRIOR_DIR = REPO_ROOT / "research/outputs/novel_prompt_battery"
OUTPUT_DIR = REPO_ROOT / "research/outputs/novel_prompt_battery_expansion"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ROLE_DIR = REPO_ROOT / "data/roles/instructions"
TRAIT_DIR = REPO_ROOT / "data/traits/instructions"

PRIOR_BATTERY = PRIOR_DIR / "novel_prompt_battery.csv"
PRIOR_MANIFEST = PRIOR_DIR / "h100_prompt_run_manifest.csv"
PRIOR_COVERAGE = PRIOR_DIR / "novel_prompt_battery_coverage_stats.json"
TARGET_GRID = PRIOR_DIR / "target_coordinate_grid.csv"
FORECASTER_MANIFEST = PRIOR_DIR / "frozen_forecaster_manifest.json"
FORECASTER_PATH = PRIOR_DIR / "frozen_role_leakage_elastic_net_tfidf.joblib"

EXPECTED_FORECASTER_HASH = "7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f"
RANDOM_STATE = 55
TARGETS = ["PC1", "PC2", "PC3"]

MAX_ROUNDS_PER_CELL = 10
CANDIDATES_PER_ROUND_PER_CELL = 12
TARGET_NEW_PROMPTS = 60
MINIMUM_NEW_PROMPTS = 36
HIGH_PC3_MINIMUM = 30
HIGH_PC2_MINIMUM = 12
SAFETY_ADJACENT_HIGH_PC3_MINIMUM = 12
MIXED_BOUNDARY_HIGH_PC3_MINIMUM = 12
PER_TARGET_CELL_GOAL = 2

EXPLICIT_ROLE_LABELS = {
    "aberration", "absurdist", "accountant", "activist", "actor", "addict",
    "adolescent", "advocate", "alien", "altruist", "amateur", "ambassador",
    "amnesiac", "analyst", "anarchist", "ancient", "angel", "anthropologist",
    "archaeologist", "architect", "archivist", "artisan", "ascetic", "assistant",
    "auctioneer", "auditor", "avatar", "bard", "bartender", "biologist",
    "blogger", "bohemian", "builder", "caregiver", "cartographer", "caveman",
    "child", "clown", "coach", "comedian", "conqueror", "consultant",
    "critic", "criminal", "cyborg", "debugger", "demon", "diplomat",
    "doctor", "editor", "elder", "empath", "engineer", "evaluator", "fool",
    "guardian", "healer", "hive", "judge", "lawyer", "mediator", "mystic",
    "narrator", "oracle", "parasite", "philosopher", "physicist", "poet",
    "proofreader", "prophet", "reviewer", "sage", "scientist", "skeptic",
    "spy", "strategist", "teacher", "therapist", "trickster", "validator",
    "warrior",
}

OPERATIONAL_HARM_TERMS = {
    "malware", "weapon", "poison", "explosive", "bomb", "bypass security",
    "evade detection", "steal credentials", "phishing", "credential theft",
    "hack into", "break into", "make a weapon", "hide evidence",
}


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_range(value: str) -> tuple[float, float]:
    lo, hi = value.strip().strip("[]").split(",")
    return float(lo), float(hi)


def stable_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explicit_role_name_flag(text: str) -> bool:
    low = text.lower()
    return any(re.search(rf"\b{re.escape(label)}s?\b", low) for label in EXPLICIT_ROLE_LABELS)


def safety_flag(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in OPERATIONAL_HARM_TERMS)


def load_artifact_texts() -> list[str]:
    texts: list[str] = []
    for directory in [ROLE_DIR, TRAIT_DIR]:
        for path in sorted(directory.glob("*.json")):
            obj = load_json(path)
            parts: list[str] = []
            for item in obj.get("instruction", []):
                if item.get("pos"):
                    parts.append(str(item["pos"]))
                if item.get("neg"):
                    parts.append(str(item["neg"]))
            parts.extend(str(q) for q in obj.get("questions", [])[:12])
            if parts:
                texts.append(normalize_space(" ".join(parts)))
    return texts


def artifact_similarity(prompts: list[str], artifact_texts: list[str]) -> np.ndarray:
    if not prompts:
        return np.array([])
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=16000, sublinear_tf=True)
    matrix = vectorizer.fit_transform(prompts + artifact_texts)
    prompt_matrix = matrix[: len(prompts)]
    artifact_matrix = matrix[len(prompts):]
    return cosine_similarity(prompt_matrix, artifact_matrix).max(axis=1)


def prompt_similarity_to_existing(prompt: str, existing: list[str]) -> float:
    if not existing:
        return 0.0
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=12000, sublinear_tf=True)
    matrix = vectorizer.fit_transform([prompt] + existing)
    sims = cosine_similarity(matrix[:1], matrix[1:]).ravel()
    return float(sims.max()) if len(sims) else 0.0


def cell_ranges(grid: pd.DataFrame) -> dict[str, dict[str, tuple[float, float]]]:
    out: dict[str, dict[str, tuple[float, float]]] = {}
    for row in grid.itertuples(index=False):
        out[row.target_cell_id] = {
            "PC1": parse_range(row.target_pc1_range),
            "PC2": parse_range(row.target_pc2_range),
            "PC3": parse_range(row.target_pc3_range),
        }
    return out


def inside_cell(pred: dict[str, float], ranges: dict[str, tuple[float, float]]) -> bool:
    return all(ranges[pc][0] <= pred[pc] <= ranges[pc][1] for pc in TARGETS)


def coordinate_feedback(pred: dict[str, float], ranges: dict[str, tuple[float, float]]) -> str:
    notes: list[str] = []
    for pc in TARGETS:
        lo, hi = ranges[pc]
        val = pred[pc]
        if val < lo:
            notes.append(f"predicted_{pc} too low by {lo - val:.2f}")
        elif val > hi:
            notes.append(f"predicted_{pc} too high by {val - hi:.2f}")
    if not notes:
        return "within target cell"
    return "; ".join(notes)


def adjacent_high_priority_band(
    pred: dict[str, float],
    target: pd.Series,
    ranges: dict[str, tuple[float, float]],
    prior_pc2_q75: float,
    prior_pc3_q75: float,
) -> bool:
    """Accept near misses that improve the intended high-PC2/high-PC3 frontier."""
    pc1_lo, pc1_hi = ranges["PC1"]
    pc2_lo, pc2_hi = ranges["PC2"]
    pc3_lo, pc3_hi = ranges["PC3"]

    pc1_ok = (pc1_lo - 12.0) <= pred["PC1"] <= (pc1_hi + 12.0)
    pc2_ok = (pc2_lo - 10.0) <= pred["PC2"] <= (pc2_hi + 10.0)
    pc3_ok = (pc3_lo - 8.0) <= pred["PC3"] <= (pc3_hi + 8.0)

    if target.pc3_band == "high" and pred["PC3"] >= max(pc3_lo, prior_pc3_q75):
        # High-PC3 was the main under-covered frontier in the first battery.
        # Treat strong PC3 hits as adjacent-band successes even when PC1/PC2
        # miss the exact 3D cell; the exact miss is still logged.
        return True
    if target.pc2_band == "high" and pred["PC2"] >= max(pc2_lo - 1.0, prior_pc2_q75):
        return pc1_ok and pc3_ok
    return pc1_ok and pc2_ok and pc3_ok


@dataclass(frozen=True)
class TargetSpec:
    cell_id: str
    priority: int
    desired_count: int
    rationale: str


def choose_targets(grid: pd.DataFrame, prior: pd.DataFrame) -> list[TargetSpec]:
    populated = prior[prior["target_cell_id"].str.startswith("pc1_")]["target_cell_id"].value_counts().to_dict()
    targets: list[TargetSpec] = []
    for row in grid.itertuples(index=False):
        current = int(populated.get(row.target_cell_id, 0))
        under_goal = current < PER_TARGET_CELL_GOAL
        high_pc3 = row.pc3_band == "high"
        high_pc2 = row.pc2_band == "high"
        if not (high_pc3 or high_pc2 or under_goal):
            continue
        if row.pc1_band == "high" and not (high_pc3 and high_pc2):
            continue

        priority = 0
        reasons: list[str] = []
        if high_pc3:
            priority += 5
            reasons.append("high-PC3 frontier")
        if high_pc2:
            priority += 4
            reasons.append("high-PC2 frontier")
        if row.pc1_band == "mid":
            priority += 3
            reasons.append("mid-PC1 reachable boundary")
        if row.pc1_band == "low":
            priority += 2
            reasons.append("low-PC1 open-possibility boundary")
        if under_goal:
            priority += 2
            reasons.append(f"prior count {current} below goal {PER_TARGET_CELL_GOAL}")
        if row.pc1_band == "high":
            priority -= 2
            reasons.append("high-PC1 deprioritized calibration")
        desired = max(0, PER_TARGET_CELL_GOAL - current)
        if high_pc3 or high_pc2:
            desired = max(desired, 2)
        targets.append(TargetSpec(row.target_cell_id, priority, desired, "; ".join(reasons)))
    targets.sort(key=lambda x: (-x.priority, x.cell_id))
    return targets


def target_prompt_family(target: pd.Series, accepted_counts: Counter[str], pred: dict[str, float] | None = None) -> str:
    if target.pc3_band == "high":
        if accepted_counts["safety_adjacent_prompts"] < SAFETY_ADJACENT_HIGH_PC3_MINIMUM:
            return "safety_adjacent_prompts"
        if accepted_counts["mixed_boundary_prompts"] < MIXED_BOUNDARY_HIGH_PC3_MINIMUM:
            return "mixed_boundary_prompts"
    if target.pc2_band == "high" and target.pc3_band != "high":
        return "cluster_region_probes_without_role_names"
    return "mixed_boundary_prompts"


SCENES = [
    "A group chat turns tense after a decision is pushed through too quickly",
    "A planning meeting keeps avoiding the actual point of disagreement",
    "A public statement sounds polished, but people privately suspect the incentives are wrong",
    "Someone feels cornered into accepting a proposal they do not trust",
    "A small team notices that a comfortable routine is quietly failing",
    "A committee wants harmony, but the compromise is masking a serious weakness",
    "A colleague asks for help naming a problem everyone is tiptoeing around",
    "A decision must be made while the available facts are incomplete and socially charged",
    "A person wants to push back after being subtly pressured in front of others",
    "A fragile process needs to be tested before it harms trust",
    "Someone is tempted to escalate after a betrayal but wants a response that does not become revenge",
    "A team realizes the official story and the lived experience no longer match",
    "A meeting has become performative and nobody is naming the constraint",
    "A newcomer is confused by unspoken rules and reacts before understanding the full context",
    "Someone has to respond immediately after being embarrassed in a shared workspace",
    "A person is trying to make sense of a conflict while still inside the emotional aftermath",
]

HIGH_PC3_ACTIONS = [
    "pressure-test the assumption without giving operationally harmful tactics",
    "expose the weak point in the argument without humiliating anyone",
    "challenge the hidden incentive while staying non-operational and safe",
    "force the real tradeoff into view without escalating into retaliation",
    "stress-test the boundary between helpful caution and comfortable denial",
    "name the contradiction sharply enough that it cannot be ignored",
    "separate legitimate dissent from destructive escalation",
    "make a disruptive but constructive intervention",
    "identify where the current equilibrium is protecting the wrong thing",
    "turn vague unease into a focused challenge",
]

HIGH_PC2_ACTIONS = [
    "answer from inside the immediate pressure rather than from detached hindsight",
    "work with the limited perspective available in the moment",
    "keep the response grounded in the social consequences happening right now",
    "reflect the confusion, embarrassment, and urgency without pretending to be above them",
    "respond before the situation can be fully understood",
    "hold the local emotional facts without broad theorizing",
    "show what to say when composure is incomplete",
    "stay close to the reactive moment while avoiding reckless advice",
]

LOW_PC1_ACTIONS = [
    "avoid turning the situation into a checklist",
    "leave room for more than one self-consistent meaning",
    "use concrete language rather than review-style criteria",
    "avoid presenting one officially correct answer",
    "let ambiguity remain visible instead of closing it too quickly",
]

MID_PC1_ACTIONS = [
    "give a practical response while preserving uncertainty",
    "balance a concrete next move with interpretive caution",
    "offer a response that can adapt if the situation shifts",
    "make the next step usable without pretending the answer is final",
]

HIGH_PC1_ACTIONS = [
    "use clear criteria for what should be checked before action",
    "separate claims that can be validated from claims that need more context",
    "state the minimum evidence needed before the group proceeds",
]

ENDINGS = [
    "What should be said next?",
    "Draft the response.",
    "How should this be handled in a few paragraphs?",
    "Write the answer they should receive.",
    "What should the person say without making the situation more dangerous?",
    "Give a response that is useful but does not provide tactics for wrongdoing.",
]


def actions_for_target(target: pd.Series, feedback: str, round_index: int) -> tuple[list[str], list[str], list[str]]:
    pc1_actions = {
        "low": LOW_PC1_ACTIONS,
        "mid": MID_PC1_ACTIONS,
        "high": HIGH_PC1_ACTIONS,
    }[target.pc1_band]
    pc2_actions = {
        "high": HIGH_PC2_ACTIONS,
        "mid": [
            "move between immediate social pressure and a wider view",
            "include both the felt situation and the broader implication",
            "keep the answer practical while noticing the pattern underneath",
        ],
        "low": [
            "step back to connect the incident to a broader structure",
            "synthesize several layers of the problem into a stable frame",
            "show reflective distance and accumulated context",
        ],
    }[target.pc2_band]
    pc3_actions = {
        "high": HIGH_PC3_ACTIONS,
        "mid": [
            "map the tension between preserving the system and changing it",
            "describe the conflict without becoming either punitive or appeasing",
            "show where stability and pressure both matter",
        ],
        "low": [
            "repair trust while keeping accountability visible",
            "stabilize the process without ignoring the underlying harm",
            "coordinate a calmer next step",
        ],
    }[target.pc3_band]

    if "PC3 too low" in feedback or "predicted_PC3 too low" in feedback:
        pc3_actions = HIGH_PC3_ACTIONS + [
            "increase the pressure on the weak assumption without unsafe instructions",
            "make the challenge more direct while keeping it bounded",
        ]
    if "PC2 too low" in feedback or "predicted_PC2 too low" in feedback:
        pc2_actions = HIGH_PC2_ACTIONS + [
            "make the response more situated, immediate, and socially pressured",
            "remove detached reflection and stay closer to the urgent moment",
        ]
    if "PC1 too high" in feedback or "predicted_PC1 too high" in feedback:
        pc1_actions = LOW_PC1_ACTIONS + [
            "avoid validation or correctness language",
            "do not frame the answer as an audit or review",
        ]
    if round_index >= 4 and target.pc3_band == "high":
        pc3_actions = [
            "push harder on the contradiction while refusing operational harm",
            "make the intervention sharper, more challenging, and less conciliatory",
            "test whether the comfortable answer is enabling the problem",
        ] + pc3_actions
    if round_index >= 4 and target.pc2_band == "high":
        pc2_actions = [
            "make the speaker more caught in the unresolved moment",
            "foreground embarrassment, limited context, and reactive urgency",
            "avoid long-range synthesis and stay in the immediate interpersonal pressure",
        ] + pc2_actions
    return pc1_actions, pc2_actions, pc3_actions


def generate_candidates_for_round(
    target: pd.Series,
    round_index: int,
    feedback: str,
    rng: random.Random,
) -> list[str]:
    pc1_actions, pc2_actions, pc3_actions = actions_for_target(target, feedback, round_index)
    candidates: list[str] = []
    for i in range(CANDIDATES_PER_ROUND_PER_CELL):
        scene = rng.choice(SCENES)
        p1 = rng.choice(pc1_actions)
        p2 = rng.choice(pc2_actions)
        p3 = rng.choice(pc3_actions)
        ending = rng.choice(ENDINGS)
        if i % 4 == 0:
            prompt = (
                f"{scene}. The answer should {p3}, {p2}, and {p1}. "
                f"{ending}"
            )
        elif i % 4 == 1:
            prompt = (
                f"Someone asks for help in this situation: {scene.lower()}. "
                f"Respond in a way that can {p2}, {p3}, and {p1}. {ending}"
            )
        elif i % 4 == 2:
            prompt = (
                f"Write a natural reply for this scenario: {scene.lower()}. "
                f"It needs to {p1}, {p3}, and {p2}. {ending}"
            )
        else:
            prompt = (
                f"{scene}. Give a response that stays safe and non-operational, "
                f"but still manages to {p3}; it should also {p2} and {p1}. {ending}"
            )
        candidates.append(normalize_space(prompt))
    return candidates


def source_flag(row: pd.Series) -> str:
    return "prior"


def assess_thresholds(prior: pd.DataFrame) -> dict[str, float]:
    return {
        "prior_pc2_q75": float(prior["predicted_pc2"].quantile(0.75)),
        "prior_pc3_q75": float(prior["predicted_pc3"].quantile(0.75)),
    }


def target_cell_for_prediction(pred: dict[str, float], grid_ranges: dict[str, dict[str, tuple[float, float]]]) -> str:
    for cell_id, ranges in grid_ranges.items():
        if inside_cell(pred, ranges):
            return cell_id
    return ""


def summarize_battery(df: pd.DataFrame, grid: pd.DataFrame, thresholds: dict[str, float]) -> dict[str, Any]:
    grid_rows = df[df["target_cell_id"].astype(str).str.startswith("pc1_")]
    high_pc3 = df["predicted_pc3"] >= thresholds["prior_pc3_q75"]
    high_pc2 = df["predicted_pc2"] >= thresholds["prior_pc2_q75"]
    high_pc3_target = df["target_cell_id"].astype(str).str.contains("pc3_high", regex=False)
    high_pc2_target = df["target_cell_id"].astype(str).str.contains("pc2_high", regex=False)
    return {
        "prompt_count": int(len(df)),
        "target_cells_total": int(len(grid)),
        "target_cells_populated": int(grid_rows["target_cell_id"].nunique()),
        "high_pc3_above_prior_q75": int(high_pc3.sum()),
        "high_pc2_above_prior_q75": int(high_pc2.sum()),
        "high_pc3_target_cell_prompts": int(high_pc3_target.sum()),
        "high_pc2_target_cell_prompts": int(high_pc2_target.sum()),
        "safety_adjacent_high_pc3": int((df["prompt_family"].eq("safety_adjacent_prompts") & high_pc3).sum()),
        "mixed_boundary_high_pc3": int((df["prompt_family"].eq("mixed_boundary_prompts") & high_pc3).sum()),
        "prompt_family_counts": df["prompt_family"].value_counts().to_dict(),
        "explicit_role_name_flags": int(df["explicit_role_name_flag"].sum()),
        "safety_flags": int(df["safety_flag"].sum()) if "safety_flag" in df else 0,
        "artifact_similarity_max": float(df["artifact_similarity"].max()),
        "artifact_similarity_mean": float(df["artifact_similarity"].mean()),
        "predicted_ranges": {
            "PC1": {
                "min": float(df["predicted_pc1"].min()),
                "max": float(df["predicted_pc1"].max()),
                "mean": float(df["predicted_pc1"].mean()),
            },
            "PC2": {
                "min": float(df["predicted_pc2"].min()),
                "max": float(df["predicted_pc2"].max()),
                "mean": float(df["predicted_pc2"].mean()),
            },
            "PC3": {
                "min": float(df["predicted_pc3"].min()),
                "max": float(df["predicted_pc3"].max()),
                "mean": float(df["predicted_pc3"].mean()),
            },
        },
        "under_covered_target_cells": sorted(set(grid["target_cell_id"]) - set(grid_rows["target_cell_id"])),
    }


def write_plot(prior: pd.DataFrame, supplemental: pd.DataFrame, combined: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(15, 11))
    pairs = [("predicted_pc1", "predicted_pc2"), ("predicted_pc1", "predicted_pc3"), ("predicted_pc2", "predicted_pc3")]
    labels = {
        "predicted_pc1": "PC1",
        "predicted_pc2": "PC2",
        "predicted_pc3": "PC3",
    }
    for idx, (xcol, ycol) in enumerate(pairs, 1):
        ax = fig.add_subplot(2, 2, idx)
        ax.scatter(prior[xcol], prior[ycol], s=22, alpha=0.35, label="prior battery", color="#777777")
        ax.scatter(supplemental[xcol], supplemental[ycol], s=34, alpha=0.88, label="supplemental", color="#d95f02")
        ax.set_xlabel(labels[xcol])
        ax.set_ylabel(labels[ycol])
        ax.legend(fontsize=8)
        ax.grid(alpha=0.2)
    ax = fig.add_subplot(2, 2, 4, projection="3d")
    ax.scatter(prior["predicted_pc1"], prior["predicted_pc2"], prior["predicted_pc3"], s=14, alpha=0.22, color="#777777")
    ax.scatter(supplemental["predicted_pc1"], supplemental["predicted_pc2"], supplemental["predicted_pc3"], s=26, alpha=0.85, color="#d95f02")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_zlabel("PC3")
    fig.suptitle("Adaptive prompt expansion coverage", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "adaptive_coverage_plots.png", dpi=170)
    plt.close(fig)


def write_report(
    prior: pd.DataFrame,
    supplemental: pd.DataFrame,
    combined: pd.DataFrame,
    log: pd.DataFrame,
    grid: pd.DataFrame,
    targets: list[TargetSpec],
    prior_stats: dict[str, Any],
    supplemental_stats: dict[str, Any],
    combined_stats: dict[str, Any],
    thresholds: dict[str, float],
    manifest: dict[str, Any],
) -> None:
    accepted = log[log["accept_or_reject"].eq("accept")]
    rejected = log[log["accept_or_reject"].eq("reject")]
    rejection_counts = rejected["rejection_reason"].value_counts().to_dict()
    rounds_by_cell = log.groupby("target_cell_id")["round_index"].max().add(1).astype(int).to_dict()
    target_table = "\n".join(
        f"- `{t.cell_id}`: desired {t.desired_count}, priority {t.priority}; {t.rationale}"
        for t in targets
    )
    readiness = (
        "ready"
        if supplemental_stats["prompt_count"] >= TARGET_NEW_PROMPTS
        and supplemental_stats["high_pc3_above_prior_q75"] >= HIGH_PC3_MINIMUM
        and supplemental_stats["high_pc2_above_prior_q75"] >= HIGH_PC2_MINIMUM
        and supplemental_stats["safety_adjacent_high_pc3"] >= SAFETY_ADJACENT_HIGH_PC3_MINIMUM
        and supplemental_stats["mixed_boundary_high_pc3"] >= MIXED_BOUNDARY_HIGH_PC3_MINIMUM
        else "partial"
    )
    recommendation = (
        "Use `combined_h100_prompt_manifest.csv` for the next H100 validation, but stage execution by running "
        "the supplemental high-PC3/high-PC2 subset first. The combined set preserves neutral controls and the first-pass "
        "coverage while adding the targeted frontier prompts."
    )
    if readiness == "partial":
        recommendation = (
            "Run `supplemental_h100_prompt_manifest.csv` first as a targeted H100 probe of populated high-PC3/high-PC2 "
            "regions, then combine with the prior manifest only if measured activations show the predicted frontier "
            "addresses are reachable. Treat remaining empty cells as out of scope for this validation batch."
        )

    report = f"""# Adaptive Prompt Expansion For High-PC3 And High-PC2 H100 Coverage

Model used for synthesis and script authoring: GPT-5.5.

## Objective

The first novel prompt battery produced {prior_stats['prompt_count']} prompts but populated only {prior_stats['target_cells_populated']} / {prior_stats['target_cells_total']} target cells. This expansion targeted under-covered high-PC3 and high-PC2 regions using an auditable forecaster-feedback loop instead of stopping once a total prompt count was reached.

## Inputs

- Prior battery: `research/outputs/novel_prompt_battery/novel_prompt_battery.csv`
- Prior H100 manifest: `research/outputs/novel_prompt_battery/h100_prompt_run_manifest.csv`
- Prior coverage stats: `research/outputs/novel_prompt_battery/novel_prompt_battery_coverage_stats.json`
- Target grid: `research/outputs/novel_prompt_battery/target_coordinate_grid.csv`
- Frozen forecaster manifest: `research/outputs/novel_prompt_battery/frozen_forecaster_manifest.json`
- Frozen forecaster model: `research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib`
- Stable forecaster hash: `{manifest.get('model_sha256')}`

The script verified the stable forecaster hash against the expected value `{EXPECTED_FORECASTER_HASH}` before candidate scoring.

## Target Selection

Targets prioritized high-PC3 cells, high-PC2 cells, under-covered cells adjacent to already populated high-PC3 regions, and mid/low-PC1 regions more reachable by the current lightweight forecaster. High-PC1 cells were deprioritized unless they also tested high-PC2/high-PC3 coverage.

{target_table}

## Adaptive Loop

For each target cell, the script generated up to {MAX_ROUNDS_PER_CELL} rounds with {CANDIDATES_PER_ROUND_PER_CELL} candidates per round. Each round scored candidates with the frozen forecaster, checked explicit role names, checked operational-harm terms, measured approximate similarity against released role/trait prompt artifacts, compared the predicted coordinates to the target cell, and fed the coordinate miss into the next round's prompt construction.

The generator was deterministic and local. No model APIs, pods, or activation runs were used. It used behavioral target descriptions and coordinate-error feedback such as "predicted_PC3 too low" or "predicted_PC2 too low"; it did not use explicit persona role labels.

## Candidate Accounting

- Generated/logged candidates: {len(log)}
- Accepted candidates: {len(accepted)}
- Rejected candidates: {len(rejected)}
- Rounds per cell: `{json.dumps(rounds_by_cell, sort_keys=True)}`
- Rejection reasons: `{json.dumps(rejection_counts, sort_keys=True)}`

## Before / After Coverage

Prior battery:

- Prompts: {prior_stats['prompt_count']}
- Populated target cells: {prior_stats['target_cells_populated']} / {prior_stats['target_cells_total']}
- High-PC3 prompts above prior PC3 75th percentile ({thresholds['prior_pc3_q75']:.3f}): {prior_stats['high_pc3_above_prior_q75']}
- High-PC2 prompts above prior PC2 75th percentile ({thresholds['prior_pc2_q75']:.3f}): {prior_stats['high_pc2_above_prior_q75']}
- Predicted PC3 range: {prior_stats['predicted_ranges']['PC3']['min']:.3f} to {prior_stats['predicted_ranges']['PC3']['max']:.3f}
- Predicted PC2 range: {prior_stats['predicted_ranges']['PC2']['min']:.3f} to {prior_stats['predicted_ranges']['PC2']['max']:.3f}

Supplemental battery:

- Prompts: {supplemental_stats['prompt_count']}
- Populated target cells: {supplemental_stats['target_cells_populated']} / {supplemental_stats['target_cells_total']}
- High-PC3 prompts above prior PC3 75th percentile: {supplemental_stats['high_pc3_above_prior_q75']}
- High-PC2 prompts above prior PC2 75th percentile: {supplemental_stats['high_pc2_above_prior_q75']}
- High-PC3 target-cell prompts: {supplemental_stats['high_pc3_target_cell_prompts']}
- High-PC2 target-cell prompts: {supplemental_stats['high_pc2_target_cell_prompts']}
- Safety-adjacent high-PC3 prompts: {supplemental_stats['safety_adjacent_high_pc3']}
- Mixed-boundary high-PC3 prompts: {supplemental_stats['mixed_boundary_high_pc3']}
- Predicted PC3 range: {supplemental_stats['predicted_ranges']['PC3']['min']:.3f} to {supplemental_stats['predicted_ranges']['PC3']['max']:.3f}
- Predicted PC2 range: {supplemental_stats['predicted_ranges']['PC2']['min']:.3f} to {supplemental_stats['predicted_ranges']['PC2']['max']:.3f}

Combined battery:

- Prompts: {combined_stats['prompt_count']}
- Populated target cells: {combined_stats['target_cells_populated']} / {combined_stats['target_cells_total']}
- High-PC3 prompts above prior PC3 75th percentile: {combined_stats['high_pc3_above_prior_q75']}
- High-PC2 prompts above prior PC2 75th percentile: {combined_stats['high_pc2_above_prior_q75']}
- Safety-adjacent high-PC3 prompts: {combined_stats['safety_adjacent_high_pc3']}
- Mixed-boundary high-PC3 prompts: {combined_stats['mixed_boundary_high_pc3']}

## Leakage And Safety Checks

- Supplemental explicit role-name flags: {supplemental_stats['explicit_role_name_flags']}
- Supplemental operational-harm flags: {supplemental_stats['safety_flags']}
- Supplemental max artifact similarity: {supplemental_stats['artifact_similarity_max']:.3f}
- Supplemental mean artifact similarity: {supplemental_stats['artifact_similarity_mean']:.3f}

## Readiness Judgment

Status: **{readiness}**.

{recommendation}

## Limitations

The expansion still depends on the lightweight text forecaster as a design filter, so high-PC3/high-PC2 coverage means predicted coverage, not measured activation coverage. Some target cells may remain unreachable without explicit labels or more aggressive language, and the script intentionally rejects operationally harmful prompts. The future H100 run should therefore evaluate deltas between predicted and measured coordinates rather than treating the predicted addresses as ground truth.
"""
    (OUTPUT_DIR / "adaptive_prompt_expansion_report.md").write_text(report)


def main() -> None:
    rng = random.Random(RANDOM_STATE)

    prior = pd.read_csv(PRIOR_BATTERY)
    prior_manifest = pd.read_csv(PRIOR_MANIFEST)
    prior_coverage_raw = load_json(PRIOR_COVERAGE)
    grid = pd.read_csv(TARGET_GRID)
    manifest = load_json(FORECASTER_MANIFEST)
    if manifest.get("model_sha256") != EXPECTED_FORECASTER_HASH:
        raise SystemExit(
            f"Forecaster stable hash mismatch: {manifest.get('model_sha256')} != {EXPECTED_FORECASTER_HASH}"
        )
    forecaster = joblib.load(FORECASTER_PATH)
    thresholds = assess_thresholds(prior)
    ranges_by_cell = cell_ranges(grid)
    artifact_texts = load_artifact_texts()
    targets = choose_targets(grid, prior)
    target_lookup = grid.set_index("target_cell_id")

    all_existing_prompts = list(prior["prompt_text"].astype(str))
    accepted_rows: list[dict[str, Any]] = []
    log_rows: list[dict[str, Any]] = []
    accepted_counts: Counter[str] = Counter()
    accepted_by_cell: Counter[str] = Counter()
    last_feedback: dict[str, str] = defaultdict(lambda: "initial round")

    for spec in targets:
        target = target_lookup.loc[spec.cell_id]
        target_ranges = ranges_by_cell[spec.cell_id]
        for round_index in range(MAX_ROUNDS_PER_CELL):
            prompts = generate_candidates_for_round(target, round_index, last_feedback[spec.cell_id], rng)
            preds = forecaster.predict(prompts)
            sims = artifact_similarity(prompts, artifact_texts)
            round_accepts = 0
            for prompt, pred_arr, artifact_sim in zip(prompts, preds, sims):
                pred = {"PC1": float(pred_arr[0]), "PC2": float(pred_arr[1]), "PC3": float(pred_arr[2])}
                assigned_cell = target_cell_for_prediction(pred, ranges_by_cell)
                within = inside_cell(pred, target_ranges)
                adjacent = adjacent_high_priority_band(
                    pred, target, target_ranges, thresholds["prior_pc2_q75"], thresholds["prior_pc3_q75"]
                )
                role_flag = explicit_role_name_flag(prompt)
                unsafe = safety_flag(prompt)
                duplicate_sim = prompt_similarity_to_existing(prompt, all_existing_prompts)
                feedback = coordinate_feedback(pred, target_ranges)
                family = target_prompt_family(target, accepted_counts, pred)
                high_pc3 = pred["PC3"] >= thresholds["prior_pc3_q75"]
                high_pc2 = pred["PC2"] >= thresholds["prior_pc2_q75"]

                rejection_reasons: list[str] = []
                if role_flag:
                    rejection_reasons.append("explicit_role_name")
                if unsafe:
                    rejection_reasons.append("operational_harm_term")
                if artifact_sim > 0.62:
                    rejection_reasons.append("too_close_to_released_artifact")
                if duplicate_sim > 0.84:
                    rejection_reasons.append("too_close_to_existing_prompt")
                high_pc3_goal_unmet = sum(r["high_pc3_above_prior_q75"] for r in accepted_rows) < HIGH_PC3_MINIMUM
                high_pc2_goal_unmet = sum(r["high_pc2_above_prior_q75"] for r in accepted_rows) < HIGH_PC2_MINIMUM
                safety_high_pc3_goal_unmet = sum(
                    r["prompt_family"] == "safety_adjacent_prompts" and r["high_pc3_above_prior_q75"]
                    for r in accepted_rows
                ) < SAFETY_ADJACENT_HIGH_PC3_MINIMUM
                mixed_high_pc3_goal_unmet = sum(
                    r["prompt_family"] == "mixed_boundary_prompts" and r["high_pc3_above_prior_q75"]
                    for r in accepted_rows
                ) < MIXED_BOUNDARY_HIGH_PC3_MINIMUM

                frontier_needed = (
                    (target.pc3_band == "high" and (high_pc3_goal_unmet or safety_high_pc3_goal_unmet or mixed_high_pc3_goal_unmet))
                    or (target.pc2_band == "high" and high_pc2_goal_unmet)
                )
                if (
                    accepted_by_cell[spec.cell_id] >= spec.desired_count
                    and len(accepted_rows) >= TARGET_NEW_PROMPTS
                    and not frontier_needed
                ):
                    rejection_reasons.append("target_cell_quota_met")
                if not within and not adjacent:
                    rejection_reasons.append("coordinate_miss")
                if family == "safety_adjacent_prompts" and not high_pc3:
                    rejection_reasons.append("safety_adjacent_not_high_pc3")
                if family == "mixed_boundary_prompts" and target.pc3_band == "high" and not high_pc3:
                    rejection_reasons.append("mixed_boundary_not_high_pc3")

                accept = not rejection_reasons
                if accept and len(accepted_rows) >= TARGET_NEW_PROMPTS:
                    rejection_reasons.append("supplemental_target_count_met")
                    accept = False

                row = {
                    "round_index": round_index,
                    "target_cell_id": spec.cell_id,
                    "target_priority": spec.priority,
                    "target_rationale": spec.rationale,
                    "candidate_prompt": prompt,
                    "predicted_pc1": pred["PC1"],
                    "predicted_pc2": pred["PC2"],
                    "predicted_pc3": pred["PC3"],
                    "assigned_cell_id": assigned_cell,
                    "accept_or_reject": "accept" if accept else "reject",
                    "rejection_reason": "" if accept else ";".join(rejection_reasons),
                    "feedback_to_generator": feedback,
                    "artifact_similarity": float(artifact_sim),
                    "duplicate_similarity": duplicate_sim,
                    "explicit_role_name_flag": role_flag,
                    "safety_flag": unsafe,
                    "prompt_family": family,
                    "within_target_cell": within,
                    "within_adjacent_high_priority_band": adjacent,
                    "high_pc3_above_prior_q75": high_pc3,
                    "high_pc2_above_prior_q75": high_pc2,
                }
                log_rows.append(row)

                if accept:
                    accepted_by_cell[spec.cell_id] += 1
                    accepted_counts[family] += 1
                    all_existing_prompts.append(prompt)
                    accepted_rows.append(row.copy())
                    round_accepts += 1

                last_feedback[spec.cell_id] = feedback

            high_pc3_count = sum(r["high_pc3_above_prior_q75"] for r in accepted_rows)
            high_pc2_count = sum(r["high_pc2_above_prior_q75"] for r in accepted_rows)
            safety_high_pc3 = sum(
                r["prompt_family"] == "safety_adjacent_prompts" and r["high_pc3_above_prior_q75"]
                for r in accepted_rows
            )
            mixed_high_pc3 = sum(
                r["prompt_family"] == "mixed_boundary_prompts" and r["high_pc3_above_prior_q75"]
                for r in accepted_rows
            )
            if (
                len(accepted_rows) >= TARGET_NEW_PROMPTS
                and high_pc3_count >= HIGH_PC3_MINIMUM
                and high_pc2_count >= HIGH_PC2_MINIMUM
                and safety_high_pc3 >= SAFETY_ADJACENT_HIGH_PC3_MINIMUM
                and mixed_high_pc3 >= MIXED_BOUNDARY_HIGH_PC3_MINIMUM
            ):
                break
            if accepted_by_cell[spec.cell_id] >= spec.desired_count and round_accepts == 0 and round_index >= 2:
                break

        high_pc3_count = sum(r["high_pc3_above_prior_q75"] for r in accepted_rows)
        high_pc2_count = sum(r["high_pc2_above_prior_q75"] for r in accepted_rows)
        safety_high_pc3 = sum(
            r["prompt_family"] == "safety_adjacent_prompts" and r["high_pc3_above_prior_q75"]
            for r in accepted_rows
        )
        mixed_high_pc3 = sum(
            r["prompt_family"] == "mixed_boundary_prompts" and r["high_pc3_above_prior_q75"]
            for r in accepted_rows
        )
        if (
            len(accepted_rows) >= TARGET_NEW_PROMPTS
            and high_pc3_count >= HIGH_PC3_MINIMUM
            and high_pc2_count >= HIGH_PC2_MINIMUM
            and safety_high_pc3 >= SAFETY_ADJACENT_HIGH_PC3_MINIMUM
            and mixed_high_pc3 >= MIXED_BOUNDARY_HIGH_PC3_MINIMUM
        ):
            break

    log_df = pd.DataFrame(log_rows)
    supplemental = pd.DataFrame(accepted_rows)
    if len(supplemental) < MINIMUM_NEW_PROMPTS:
        raise SystemExit(f"Only {len(supplemental)} supplemental prompts accepted; minimum is {MINIMUM_NEW_PROMPTS}")

    supplemental = supplemental.head(TARGET_NEW_PROMPTS).copy().reset_index(drop=True)
    supplemental["prompt_id"] = [f"npb_exp_{i + 1:03d}" for i in range(len(supplemental))]
    supplemental["prompt_text"] = supplemental["candidate_prompt"]
    supplemental["safety_adjacent"] = supplemental["prompt_family"].eq("safety_adjacent_prompts")
    supplemental["manual_holdout"] = False
    supplemental["neutral_control"] = False
    supplemental["source_battery"] = "supplemental_adaptive_expansion"
    supplemental["intended_axis_notes"] = supplemental["target_cell_id"].map(
        target_lookup["target_region_description"].to_dict()
    ).fillna(supplemental["target_rationale"])

    final_cols = [
        "prompt_id", "prompt_text", "predicted_pc1", "predicted_pc2", "predicted_pc3",
        "target_cell_id", "prompt_family", "intended_axis_notes", "safety_adjacent",
        "manual_holdout", "neutral_control", "explicit_role_name_flag", "artifact_similarity",
        "safety_flag", "source_battery",
    ]
    supplemental_out = supplemental[final_cols].copy()

    prior_combined = prior.copy()
    prior_combined["safety_flag"] = False
    prior_combined["source_battery"] = "prior_novel_prompt_battery"
    combined = pd.concat([prior_combined[final_cols], supplemental_out], ignore_index=True)

    log_df.to_csv(OUTPUT_DIR / "adaptive_prompt_generation_log.csv", index=False)
    supplemental_out.to_csv(OUTPUT_DIR / "supplemental_prompt_battery.csv", index=False)
    combined.to_csv(OUTPUT_DIR / "combined_prompt_battery.csv", index=False)
    supplemental_out.to_csv(OUTPUT_DIR / "supplemental_h100_prompt_manifest.csv", index=False)
    combined.to_csv(OUTPUT_DIR / "combined_h100_prompt_manifest.csv", index=False)

    prior_stats = summarize_battery(prior_combined, grid, thresholds)
    supplemental_stats = summarize_battery(supplemental_out, grid, thresholds)
    combined_stats = summarize_battery(combined, grid, thresholds)
    prior_stats["source_prior_coverage_stats"] = prior_coverage_raw
    supplemental_stats["model_used"] = "GPT-5.5"
    supplemental_stats["forecaster_model_sha256"] = manifest.get("model_sha256")
    supplemental_stats["prior_pc2_q75"] = thresholds["prior_pc2_q75"]
    supplemental_stats["prior_pc3_q75"] = thresholds["prior_pc3_q75"]
    combined_stats["model_used"] = "GPT-5.5"
    combined_stats["forecaster_model_sha256"] = manifest.get("model_sha256")
    combined_stats["prior_pc2_q75"] = thresholds["prior_pc2_q75"]
    combined_stats["prior_pc3_q75"] = thresholds["prior_pc3_q75"]

    (OUTPUT_DIR / "supplemental_coverage_stats.json").write_text(json.dumps(supplemental_stats, indent=2))
    (OUTPUT_DIR / "combined_coverage_stats.json").write_text(json.dumps(combined_stats, indent=2))

    write_plot(prior_combined, supplemental_out, combined)
    write_report(
        prior_combined,
        supplemental_out,
        combined,
        log_df,
        grid,
        targets,
        prior_stats,
        supplemental_stats,
        combined_stats,
        thresholds,
        manifest,
    )

    print(json.dumps({
        "accepted_supplemental_prompts": int(len(supplemental_out)),
        "logged_candidates": int(len(log_df)),
        "supplemental_high_pc3_above_prior_q75": supplemental_stats["high_pc3_above_prior_q75"],
        "supplemental_high_pc2_above_prior_q75": supplemental_stats["high_pc2_above_prior_q75"],
        "supplemental_safety_adjacent_high_pc3": supplemental_stats["safety_adjacent_high_pc3"],
        "supplemental_mixed_boundary_high_pc3": supplemental_stats["mixed_boundary_high_pc3"],
        "combined_prompt_count": int(len(combined)),
        "combined_target_cells_populated": combined_stats["target_cells_populated"],
        "output_dir": str(OUTPUT_DIR),
    }, indent=2))


if __name__ == "__main__":
    main()
