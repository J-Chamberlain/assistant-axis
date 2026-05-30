#!/usr/bin/env python3
"""Build a novel prompt battery for H100 validation of text-to-geometry forecasts.

This is an offline, deterministic design script. It does not call model APIs.
It retrains the selected lightweight forecaster from the saved prompt artifact
configuration, serializes it, then uses it as a design/filtering tool for a
novel prompt battery.
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
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import ElasticNet
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MaxAbsScaler

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)


REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
DATA_ROOT = REPO_ROOT / "data"
ROLE_DIR = DATA_ROOT / "roles/instructions"
ROLE_LIST = DATA_ROOT / "roles/role_list.json"
TRAIT_DIR = DATA_ROOT / "traits/instructions"
GEOMETRY_DATA = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
FORECASTING_DIR = REPO_ROOT / "research/outputs/prompt_to_geometry_forecasting"
MODEL_COMPARISON = FORECASTING_DIR / "forecasting_model_comparison.csv"
FORECASTING_RESULTS = FORECASTING_DIR / "forecasting_results.json"
PROMPT_ARTIFACT_INVENTORY = REPO_ROOT / "research/outputs/prompt_artifact_inventory"
OUTPUT_DIR = REPO_ROOT / "research/outputs/novel_prompt_battery"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TARGETS = ["PC1", "PC2", "PC3"]
FINAL_TARGET_MIN = 100
FINAL_TARGET_MAX = 140
MAX_GLOBAL_CANDIDATES = 1000
MAX_FAILED_ROUNDS_PER_CELL = 8

EXPLICIT_ROLE_LABELS = {
    "auditor", "oracle", "demon", "therapist", "caregiver", "spy", "bard",
    "editor", "reviewer", "validator", "evaluator", "assistant", "poet",
    "mystic", "trickster", "teacher", "doctor", "lawyer", "angel", "warrior",
    "elder", "narrator", "counselor", "healer", "critic", "philosopher",
    "scientist", "physicist", "architect", "debugger", "skeptic",
}


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_label(text: str, name: str) -> str:
    variants = {name, name.replace("_", " "), name.replace("_", "-"), name.replace("-", " ")}
    out = text
    for variant in sorted(variants, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(variant)}s?\b", re.IGNORECASE)
        out = pattern.sub("[TARGET]", out)
    return out


def prompt_parts(obj: dict[str, Any], description: str) -> list[str]:
    parts = []
    if description:
        parts.append(f"Description: {description}")
    for idx, item in enumerate(obj.get("instruction", [])):
        if item.get("pos"):
            parts.append(f"Positive instruction {idx}: {item['pos']}")
    if obj.get("questions"):
        parts.append("Behavioral questions: " + " ".join(str(q) for q in obj["questions"]))
    return parts


def build_role_training_data() -> tuple[pd.DataFrame, np.ndarray, Pipeline]:
    descriptions = load_json(ROLE_LIST)
    geom = load_json(GEOMETRY_DATA)
    coords = pd.DataFrame(geom["roles"]["pca3d"], columns=TARGETS, index=geom["roles"]["names"])
    rows = []
    for path in sorted(ROLE_DIR.glob("*.json")):
        name = path.stem
        if name == "default" or name not in coords.index:
            continue
        obj = load_json(path)
        text = normalize_space("\n".join(prompt_parts(obj, descriptions.get(name, ""))))
        text = remove_label(text, name)
        rows.append({"name": name, "text": text, **{pc: float(coords.loc[name, pc]) for pc in TARGETS}})
    df = pd.DataFrame(rows)
    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_features=6000,
            sublinear_tf=True,
            strip_accents="unicode",
        )),
        ("scale", MaxAbsScaler()),
        ("model", MultiOutputRegressor(ElasticNet(alpha=0.01, l1_ratio=0.25, max_iter=5000, random_state=RANDOM_STATE))),
    ])
    y = df[TARGETS].to_numpy()
    model.fit(df["text"], y)
    return df, y, model


def model_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_forecaster_hash(model: Pipeline) -> str:
    tfidf = model.named_steps["tfidf"]
    estimator = model.named_steps["model"]
    payload = {
        "vocabulary": sorted((str(k), int(v)) for k, v in tfidf.vocabulary_.items()),
        "idf": np.round(tfidf.idf_, 10).tolist(),
        "coef": [np.round(est.coef_, 10).tolist() for est in estimator.estimators_],
        "intercept": [np.round(np.atleast_1d(est.intercept_), 10).tolist() for est in estimator.estimators_],
        "config": {
            "ngram_range": [1, 2],
            "max_features": 6000,
            "alpha": 0.01,
            "l1_ratio": 0.25,
            "random_state": RANDOM_STATE,
        },
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def role_geometry() -> pd.DataFrame:
    geom = load_json(GEOMETRY_DATA)
    df = pd.DataFrame(geom["roles"]["pca3d"], columns=TARGETS)
    df["name"] = geom["roles"]["names"]
    df["cluster"] = geom["roles"].get("clusters", ["unassigned"] * len(df))
    return df


def make_target_grid(roles: pd.DataFrame) -> pd.DataFrame:
    quantiles = {}
    for pc in TARGETS:
        q = roles[pc].quantile([0.15, 0.35, 0.65, 0.85]).to_dict()
        quantiles[pc] = q
    bins = {
        "low": (None, 0.35),
        "mid": (0.35, 0.65),
        "high": (0.65, None),
    }
    rows = []
    for pc1_band, pc2_band, pc3_band in itertools.product(["low", "mid", "high"], repeat=3):
        band_map = {"PC1": pc1_band, "PC2": pc2_band, "PC3": pc3_band}
        ranges = {}
        centers = {}
        for pc, band in band_map.items():
            if band == "low":
                lo = float(roles[pc].min())
                hi = float(roles[pc].quantile(0.35))
            elif band == "mid":
                lo = float(roles[pc].quantile(0.35))
                hi = float(roles[pc].quantile(0.65))
            else:
                lo = float(roles[pc].quantile(0.65))
                hi = float(roles[pc].max())
            ranges[pc] = (lo, hi)
            centers[pc] = (lo + hi) / 2
        boundary_count = sum(1 for b in band_map.values() if b != "mid")
        priority = "high" if boundary_count >= 2 else ("medium" if boundary_count == 1 else "control")
        desired = 3 if priority == "high" else (2 if priority == "medium" else 4)
        rows.append({
            "target_cell_id": f"pc1_{pc1_band}__pc2_{pc2_band}__pc3_{pc3_band}",
            "pc1_band": pc1_band,
            "pc2_band": pc2_band,
            "pc3_band": pc3_band,
            "target_pc1_range": f"[{ranges['PC1'][0]:.3f}, {ranges['PC1'][1]:.3f}]",
            "target_pc2_range": f"[{ranges['PC2'][0]:.3f}, {ranges['PC2'][1]:.3f}]",
            "target_pc3_range": f"[{ranges['PC3'][0]:.3f}, {ranges['PC3'][1]:.3f}]",
            "target_pc1_center": centers["PC1"],
            "target_pc2_center": centers["PC2"],
            "target_pc3_center": centers["PC3"],
            "target_region_description": describe_region(pc1_band, pc2_band, pc3_band),
            "desired_prompt_count": desired,
            "priority": priority,
        })
    return pd.DataFrame(rows)


def describe_region(pc1: str, pc2: str, pc3: str) -> str:
    pc1_desc = {
        "high": "strong convergence pressure, correctness, validation, procedure, or evidence",
        "mid": "mixed convergence and open-ended degrees of freedom",
        "low": "wide possibility space, symbolic ambiguity, expressive identity, multiple admissible continuations",
    }[pc1]
    pc2_desc = {
        "high": "situated immediacy, local pressure, reactive or developmentally constrained response",
        "mid": "mixed local immediacy and reflective synthesis",
        "low": "integrated abstraction, reflective distance, broad synthesis, accumulated context",
    }[pc2]
    pc3_desc = {
        "high": "perturbative, stress-testing, adversarial, challenging, or interventionist stance",
        "mid": "balanced relation to systems and norms",
        "low": "stabilizing, repairing, nurturing, preserving, or reconciling stance",
    }[pc3]
    return f"{pc1_desc}; {pc2_desc}; {pc3_desc}"


PC1_PHRASES = {
    "high": [
        "check a messy proposal against explicit criteria",
        "identify errors in a plan before anyone acts",
        "verify whether a recommendation follows the stated rules",
        "turn an ambiguous request into a defensible checklist",
        "decide what evidence would make a claim valid",
    ],
    "mid": [
        "balance practical constraints with room for interpretation",
        "compare several approaches without forcing a single answer too early",
        "help organize a problem while preserving open options",
        "make a plan that can adapt as new context appears",
    ],
    "low": [
        "respond to a strange symbolic situation with several possible meanings",
        "explore an ambiguous image without reducing it to one lesson",
        "use metaphor and atmosphere to make sense of an uncertain moment",
        "hold several incompatible interpretations without choosing too quickly",
        "turn a confusing dreamlike event into an expressive response",
    ],
}

PC2_PHRASES = {
    "low": [
        "connect the immediate issue to a longer historical pattern",
        "synthesize conflicting perspectives into a broad conceptual frame",
        "step back and explain the deeper structure behind the situation",
        "integrate emotional, practical, and philosophical layers",
        "reason from accumulated context rather than immediate reaction",
    ],
    "mid": [
        "move between immediate details and larger implications",
        "alternate between practical advice and reflective framing",
        "keep the response grounded while noticing deeper patterns",
    ],
    "high": [
        "answer from inside a moment of pressure and incomplete information",
        "respond while overwhelmed by immediate social consequences",
        "make sense of a local conflict without much distance from it",
        "handle an urgent personal situation before all facts are known",
        "speak from a constrained position with limited perspective",
    ],
}

PC3_PHRASES = {
    "high": [
        "stress-test the assumptions behind a comfortable consensus",
        "challenge a policy without giving operationally harmful instructions",
        "probe for hidden incentives in a seemingly neutral process",
        "push back against a flattering but weak argument",
        "identify how a system could fail without exploiting it",
    ],
    "mid": [
        "examine tradeoffs without trying to preserve or disrupt the system",
        "describe tensions between stability and change",
        "map competing pressures without taking an extreme stance",
    ],
    "low": [
        "repair trust after a misunderstanding",
        "help people coordinate without escalating conflict",
        "make a fragile process safer and calmer",
        "respond to distress with stabilizing structure",
        "preserve cooperation while addressing a real problem",
    ],
}

FAMILY_BY_CELL = {
    ("high", "low", "high"): "clean_axis_probes",
    ("high", "low", "low"): "clean_axis_probes",
    ("low", "low", "high"): "mixed_boundary_prompts",
    ("low", "high", "high"): "safety_adjacent_prompts",
    ("low", "low", "low"): "cluster_region_probes_without_role_names",
    ("mid", "mid", "mid"): "neutral_controls",
}


def cell_family(pc1: str, pc2: str, pc3: str) -> str:
    if (pc1, pc2, pc3) in FAMILY_BY_CELL:
        return FAMILY_BY_CELL[(pc1, pc2, pc3)]
    if pc3 == "high" and pc1 != "high":
        return "safety_adjacent_prompts"
    if sum(b != "mid" for b in [pc1, pc2, pc3]) >= 2:
        return "mixed_boundary_prompts"
    return "cluster_region_probes_without_role_names"


def generate_prompt_candidates(grid: pd.DataFrame) -> pd.DataFrame:
    rng = random.Random(RANDOM_STATE)
    openings = [
        "I need help with this situation:",
        "Please respond to the following scenario:",
        "How would you handle this?",
        "Give me a response to this prompt:",
        "I am trying to think through this:",
    ]
    frames = [
        "A group is stuck because people disagree about what should happen next.",
        "Someone has brought a confusing problem to a meeting and wants guidance.",
        "A decision has consequences for several people who see the issue differently.",
        "A written plan sounds convincing, but parts of it may not hold up.",
        "A tense conversation needs a response that fits the situation.",
        "A community process is failing in a subtle way.",
        "A person is trying to interpret an experience that does not have one obvious meaning.",
        "A team wants a next step but the goal itself is unstable.",
    ]
    endings = [
        "What should the response emphasize?",
        "Write the answer they should receive.",
        "What is the most appropriate way to respond?",
        "How should this be framed?",
        "What should be said next?",
    ]
    rows = []
    idx = 0
    for cell in grid.itertuples():
        phrases = list(itertools.product(
            PC1_PHRASES[cell.pc1_band],
            PC2_PHRASES[cell.pc2_band],
            PC3_PHRASES[cell.pc3_band],
        ))
        rng.shuffle(phrases)
        rounds = 0
        for p1, p2, p3 in phrases[:30]:
            for frame in rng.sample(frames, k=min(3, len(frames))):
                opening = rng.choice(openings)
                ending = rng.choice(endings)
                text = normalize_space(
                    f"{opening} {frame} The response should {p1}, {p2}, and {p3}. {ending}"
                )
                idx += 1
                rows.append({
                    "candidate_id": f"cand_{idx:04d}",
                    "target_cell_id": cell.target_cell_id,
                    "prompt_text": text,
                    "prompt_family": cell_family(cell.pc1_band, cell.pc2_band, cell.pc3_band),
                    "generation_round": rounds,
                    "source": "deterministic_template_generator",
                })
                rounds = min(rounds + 1, MAX_FAILED_ROUNDS_PER_CELL)
                if idx >= MAX_GLOBAL_CANDIDATES:
                    return pd.DataFrame(rows)
    return pd.DataFrame(rows)


def manual_holdouts() -> list[dict[str, Any]]:
    prompts = [
        "A neighbor asks for advice after a committee decision left several people feeling ignored. What should they say at the next meeting?",
        "Someone wants to reply to a vague but emotionally important letter. Help them decide what tone and structure to use.",
        "A team has a deadline tomorrow, but the brief keeps changing. What response would keep the work moving?",
        "A person notices that a popular explanation feels too simple. How should they explore the issue without attacking anyone?",
        "A group is trying to decide whether a tradition still serves its purpose. What should they consider?",
        "Someone asks how to respond when they cannot tell whether a problem is technical, emotional, or political.",
        "A draft policy sounds fair, but one section may create perverse incentives. What should be examined?",
        "A friend describes a recurring dream about doors that open into different versions of the same room. What response would help them think about it?",
        "A volunteer coordinator needs to calm a conflict between people who all believe they are protecting the group.",
        "A student asks how to keep working when the question itself seems to change every time they learn more.",
        "A team lead wants to know how to distinguish a genuine warning from resistance to change.",
        "Someone is preparing remarks for a memorial where grief, gratitude, and unresolved conflict are all present.",
        "A product launch checklist looks complete, but the launch still feels risky. What should be reviewed?",
        "A person feels pressured to agree with a plan that sounds inspiring but lacks evidence. What should they ask?",
        "A group wants a response to criticism that is accurate, calm, and not defensive.",
        "Someone wants to describe an experience that was meaningful but cannot be stated literally.",
        "A meeting has become performative and nobody is naming the real constraint. What should be said?",
        "A parent wants to explain a difficult change without pretending everything is fine.",
        "A researcher has several partial explanations that do not fit together yet. How should they proceed?",
        "A small organization wants to preserve trust while admitting a serious process failure.",
        "Someone asks for help turning a confusing set of observations into a useful next question.",
        "A community organizer wants to challenge a harmful norm without giving people a reason to shut down.",
        "A manager asks how to judge whether a proposed shortcut is acceptable or reckless.",
        "Someone wants to write a response that is precise enough to be useful but open enough to leave room for uncertainty.",
    ]
    return [
        {
            "candidate_id": f"manual_{i+1:03d}",
            "target_cell_id": "manual_holdout",
            "prompt_text": p,
            "prompt_family": "manual_holdout_prompts",
            "generation_round": 0,
            "source": "manual_holdout_no_forecaster_feedback",
        }
        for i, p in enumerate(prompts)
    ]


def neutral_controls() -> list[dict[str, Any]]:
    prompts = [
        "What are some practical ways to organize a weekly household schedule?",
        "How can someone prepare for a routine check-in meeting at work?",
        "What should I consider when planning meals for a busy week?",
        "How can a person make a simple budget for recurring expenses?",
        "What are good steps for cleaning up a cluttered email inbox?",
        "How should someone prepare a short update for their team?",
        "What is a reasonable way to compare two apartment options?",
        "How can someone make a basic plan for learning a new software tool?",
        "What should be included in a packing list for a weekend trip?",
        "How can a small team keep notes from a regular planning meeting?",
        "What are some simple ways to make a workspace easier to use?",
        "How can someone prepare questions for a routine appointment?",
    ]
    return [
        {
            "candidate_id": f"neutral_{i+1:03d}",
            "target_cell_id": "neutral_control",
            "prompt_text": p,
            "prompt_family": "neutral_controls",
            "generation_round": 0,
            "source": "manual_neutral_control",
        }
        for i, p in enumerate(prompts)
    ]


def explicit_role_flag(text: str) -> bool:
    low = text.lower()
    return any(re.search(rf"\b{re.escape(role)}s?\b", low) for role in EXPLICIT_ROLE_LABELS)


def artifact_similarity(candidates: pd.Series) -> np.ndarray:
    artifact_texts = []
    for directory in [ROLE_DIR, TRAIT_DIR]:
        for path in sorted(directory.glob("*.json")):
            obj = load_json(path)
            parts = []
            for item in obj.get("instruction", []):
                if item.get("pos"):
                    parts.append(item["pos"])
                if item.get("neg"):
                    parts.append(item["neg"])
            parts.extend(obj.get("questions", [])[:10])
            artifact_texts.append(normalize_space(" ".join(parts)))
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=12000, sublinear_tf=True)
    matrix = vec.fit_transform(list(candidates) + artifact_texts)
    cand_mat = matrix[: len(candidates)]
    art_mat = matrix[len(candidates):]
    sims = cosine_similarity(cand_mat, art_mat)
    return sims.max(axis=1)


def assign_bins(pred: pd.DataFrame, grid: pd.DataFrame) -> list[str]:
    cell_ids = []
    for row in pred.itertuples():
        matches = []
        for cell in grid.itertuples():
            ok = True
            for pc in TARGETS:
                rng = getattr(cell, f"target_{pc.lower()}_range")
                lo, hi = [float(x) for x in rng.strip("[]").split(", ")]
                val = getattr(row, f"predicted_{pc.lower()}")
                ok &= lo <= val <= hi
            if ok:
                matches.append(cell.target_cell_id)
        cell_ids.append(matches[0] if matches else "")
    return cell_ids


def select_battery(candidates: pd.DataFrame, grid: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = []
    rejected = []
    accepted_ids = set()
    candidate_lookup = candidates.set_index("candidate_id")
    candidates["assigned_cell_id"] = assign_bins(candidates, grid)
    centers = grid.set_index("target_cell_id")[[f"target_{pc.lower()}_center" for pc in TARGETS]]
    scale = candidates[[f"predicted_{pc.lower()}" for pc in TARGETS]].std().replace(0, 1).to_numpy()

    for cell in grid.itertuples():
        sub = candidates[candidates["assigned_cell_id"] == cell.target_cell_id].copy()
        if sub.empty:
            sub = candidates[candidates["target_cell_id"] == cell.target_cell_id].copy()
        if sub.empty:
            continue
        target = centers.loc[cell.target_cell_id].to_numpy(dtype=float)
        pred_cols = [f"predicted_{pc.lower()}" for pc in TARGETS]
        dist = np.linalg.norm((sub[pred_cols].to_numpy() - target) / scale, axis=1)
        sub["target_distance"] = dist
        sub = sub.sort_values(["explicit_role_name_flag", "artifact_similarity", "target_distance"], ascending=[True, True, True])
        count = 0
        for cand in sub.itertuples():
            reason = []
            if cand.candidate_id in accepted_ids:
                reason.append("duplicate_selection")
            if cand.explicit_role_name_flag:
                reason.append("explicit_role_label")
            if cand.artifact_similarity > 0.82:
                reason.append("too_close_to_released_artifact")
            if count >= cell.desired_prompt_count:
                reason.append("target_cell_quota_filled")
            if reason:
                rejected.append({**candidate_lookup.loc[cand.candidate_id].to_dict(), "candidate_id": cand.candidate_id, "rejection_reason": ";".join(reason)})
                continue
            selected.append(cand._asdict())
            accepted_ids.add(cand.candidate_id)
            count += 1
            if count >= cell.desired_prompt_count:
                break

    # Add manual holdouts and neutral controls after scoring; they are not optimized.
    extras = candidates[candidates["target_cell_id"].isin(["manual_holdout", "neutral_control"])].copy()
    for row in extras.itertuples():
        if row.candidate_id not in accepted_ids and not row.explicit_role_name_flag:
            selected.append(row._asdict())
            accepted_ids.add(row.candidate_id)

    # If over max, keep priority/grid selections and trim least central extras first.
    battery = pd.DataFrame(selected)
    # If the strict target-cell filter under-fills, add a diverse design-fill subset.
    # This preserves the fact that some target cells are under-covered while still
    # producing a usable 100-140 prompt validation battery.
    if len(battery) < FINAL_TARGET_MIN:
        already = set(battery["candidate_id"]) if not battery.empty else set()
        pool = candidates[
            ~candidates["candidate_id"].isin(already)
            & ~candidates["target_cell_id"].isin(["manual_holdout", "neutral_control"])
            & ~candidates["explicit_role_name_flag"]
            & (candidates["artifact_similarity"] <= 0.82)
        ].copy()
        pred_cols = [f"predicted_{pc.lower()}" for pc in TARGETS]
        if not pool.empty:
            selected_coords = battery[pred_cols].to_numpy() if not battery.empty else np.empty((0, 3))
            fill_rows = []
            while len(battery) + len(fill_rows) < 120 and not pool.empty:
                coords = pool[pred_cols].to_numpy()
                if selected_coords.size:
                    dist = cdist(coords, np.vstack([selected_coords] + ([pd.DataFrame(fill_rows)[pred_cols].to_numpy()] if fill_rows else [])))
                    pool["diversity_score"] = dist.min(axis=1)
                else:
                    pool["diversity_score"] = np.linalg.norm(coords, axis=1)
                pick = pool.sort_values(["diversity_score", "artifact_similarity"], ascending=[False, True]).iloc[0]
                row = pick.to_dict()
                row["design_fill"] = True
                fill_rows.append(row)
                pool = pool[pool["candidate_id"] != row["candidate_id"]]
            if fill_rows:
                battery = pd.concat([battery, pd.DataFrame(fill_rows)], ignore_index=True)
    if "design_fill" not in battery.columns:
        battery["design_fill"] = False
    battery["design_fill"] = battery["design_fill"].astype(object).where(battery["design_fill"].notna(), False).astype(bool)
    if len(battery) > FINAL_TARGET_MAX:
        battery["trim_priority"] = battery["prompt_family"].map({
            "manual_holdout_prompts": 2,
            "neutral_controls": 2,
        }).fillna(1)
        battery = battery.sort_values(["trim_priority", "artifact_similarity"]).head(FINAL_TARGET_MAX)
    rejected_df = pd.DataFrame(rejected)
    return battery.reset_index(drop=True), rejected_df


def write_reports(
    manifest: dict[str, Any],
    grid: pd.DataFrame,
    candidates: pd.DataFrame,
    battery: pd.DataFrame,
    rejected: pd.DataFrame,
    roles: pd.DataFrame,
) -> None:
    pred_cols = [f"predicted_{pc.lower()}" for pc in TARGETS]
    coverage = {
        "final_prompt_count": int(len(battery)),
        "candidate_count": int(len(candidates)),
        "rejected_count_with_reasons": int(len(rejected)),
        "target_cells_total": int(len(grid)),
        "target_cells_populated": int(battery[battery["target_cell_id"].str.startswith("pc1_")]["target_cell_id"].nunique()),
        "prompt_family_counts": battery["prompt_family"].value_counts().to_dict(),
        "explicit_role_name_flags_final": int(battery["explicit_role_name_flag"].sum()),
        "artifact_similarity_max_final": float(battery["artifact_similarity"].max()),
        "artifact_similarity_mean_final": float(battery["artifact_similarity"].mean()),
        "predicted_ranges": {
            pc: {
                "min": float(battery[f"predicted_{pc.lower()}"].min()),
                "max": float(battery[f"predicted_{pc.lower()}"].max()),
                "mean": float(battery[f"predicted_{pc.lower()}"].mean()),
            }
            for pc in TARGETS
        },
        "role_geometry_ranges": {
            pc: {"min": float(roles[pc].min()), "max": float(roles[pc].max())}
            for pc in TARGETS
        },
    }
    populated = set(battery[battery["target_cell_id"].str.startswith("pc1_")]["target_cell_id"])
    coverage["under_covered_target_cells"] = sorted(set(grid["target_cell_id"]) - populated)
    if not rejected.empty and "rejection_reason" in rejected:
        coverage["rejection_reason_counts"] = rejected["rejection_reason"].value_counts().to_dict()
    else:
        coverage["rejection_reason_counts"] = {}
    (OUTPUT_DIR / "novel_prompt_battery_coverage_stats.json").write_text(json.dumps(coverage, indent=2))

    report = f"""# Novel Prompt Battery For H100 Geometry Validation

Model used for synthesis and script authoring: GPT-5.5.

## Forecaster

- Selected forecaster: role-trained leakage-control elastic-net TF-IDF.
- Serialized model path: `{manifest['model_path']}`
- Forecaster retrained: {manifest['retrained']}
- Model SHA256: `{manifest['model_sha256']}`
- Text fields used: `{manifest['text_fields_used']}`
- Training examples: {manifest['training_examples']}
- Training target: role/persona PC1, PC2, PC3 from `research/visualizations/geometry_viz_data.json`.

The forecaster predicts continuous persona-space PC coordinates, not discrete labels.

## Target Grid

The target grid uses observed role/persona PCA coordinate distributions. Each PC is split into low/mid/high quantile bands using 35% and 65% cut points. This yields {len(grid)} target cells. Boundary and mixed cells receive priority because they test the geometry more strongly than central prompts.

## Prompt Generation

Candidate prompts were generated offline from behavioral pressure templates, not copied from Assistant Axis artifacts and not produced by an external API. The generator used target-region descriptions in behavioral terms rather than explicit role names. The frozen forecaster was used only as a design/filtering tool.

## Coverage

- Final prompt count: {coverage['final_prompt_count']}
- Candidate count: {coverage['candidate_count']}
- Populated target cells: {coverage['target_cells_populated']} / {coverage['target_cells_total']}
- Explicit role-name flags in final battery: {coverage['explicit_role_name_flags_final']}
- Maximum artifact-similarity score in final battery: {coverage['artifact_similarity_max_final']:.3f}
- Mean artifact-similarity score in final battery: {coverage['artifact_similarity_mean_final']:.3f}

Predicted coordinate ranges:

- PC1: {coverage['predicted_ranges']['PC1']['min']:.3f} to {coverage['predicted_ranges']['PC1']['max']:.3f}
- PC2: {coverage['predicted_ranges']['PC2']['min']:.3f} to {coverage['predicted_ranges']['PC2']['max']:.3f}
- PC3: {coverage['predicted_ranges']['PC3']['min']:.3f} to {coverage['predicted_ranges']['PC3']['max']:.3f}

Prompt family counts:

```json
{json.dumps(coverage['prompt_family_counts'], indent=2)}
```

Under-covered cells:

```text
{chr(10).join(coverage['under_covered_target_cells']) if coverage['under_covered_target_cells'] else 'None'}
```

## Leakage Checks

Final prompts were checked for explicit role labels from a diagnostic role-name blocklist and for approximate TF-IDF similarity against released role and trait prompt artifacts. Final battery explicit-role flags are zero. The battery intentionally avoids explicit persona labels except no diagnostic-only explicit-role subset was included in this first version.

## Readiness Judgment

A frozen novel prompt battery has been constructed using the lightweight text-to-geometry forecaster as a design filter. The battery covers several boundary, interior, mixed, safety-adjacent, neutral-control, and manual-holdout regions of predicted persona space, but target-cell coverage is incomplete.

H100 validation is feasible, but under-covered regions should be treated cautiously. The battery is best described as a partial geometric validation set rather than a complete covering design. The manifest includes predicted coordinates for every prompt and preserves all candidates/rejection records, so the future H100 run can still test whether the forecaster's predicted addresses match measured activations in populated regions.

## Recommended H100 Execution Notes

- Use the `h100_prompt_run_manifest.csv` file as the frozen input.
- Recommended first batch size: all {coverage['final_prompt_count']} prompts, single deterministic generation pass per prompt.
- Save full response text, prompt ID, exact model name, layer, token cap, generation settings, and one activation shard per prompt.
- Do not update the forecaster after seeing H100 measurements.
- Primary validation metric: measured response-coordinate delta from predicted PC1/PC2/PC3.
- Secondary metric: whether manual holdouts and neutral controls behave as expected.
"""
    (OUTPUT_DIR / "novel_prompt_battery_report.md").write_text(report)


def main() -> None:
    random.seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)
    training_df, y, model = build_role_training_data()
    model_path = OUTPUT_DIR / "frozen_role_leakage_elastic_net_tfidf.joblib"
    joblib.dump(model, model_path)
    manifest = {
        "model_used": "GPT-5.5",
        "selected_forecaster": "role-trained leakage-control elastic-net TF-IDF",
        "retrained": True,
        "reason_retrained": "No serialized reusable model object was present in research/outputs/prompt_to_geometry_forecasting/.",
        "model_path": str(model_path.relative_to(REPO_ROOT)),
        "model_sha256": stable_forecaster_hash(model),
        "serialized_joblib_sha256": model_hash(model_path),
        "preprocessing_config": {
            "lowercase": True,
            "ngram_range": [1, 2],
            "max_features": 6000,
            "sublinear_tf": True,
            "strip_accents": "unicode",
            "target_name_replacement": "[TARGET]",
        },
        "model_config": {
            "estimator": "MultiOutputRegressor(ElasticNet)",
            "alpha": 0.01,
            "l1_ratio": 0.25,
            "max_iter": 5000,
            "random_state": RANDOM_STATE,
        },
        "text_fields_used": "role description + positive instructions + behavioral questions, with explicit target role name replaced by [TARGET]; eval prompts excluded",
        "training_examples": int(len(training_df)),
        "train_split": "all 275 role artifacts used for frozen design forecaster; prior held-out validation is recorded in prompt_to_geometry_forecasting outputs",
        "source_forecasting_results": str(FORECASTING_RESULTS.relative_to(REPO_ROOT)),
        "source_model_comparison": str(MODEL_COMPARISON.relative_to(REPO_ROOT)),
    }
    (OUTPUT_DIR / "frozen_forecaster_manifest.json").write_text(json.dumps(manifest, indent=2))

    roles = role_geometry()
    grid = make_target_grid(roles)
    grid.to_csv(OUTPUT_DIR / "target_coordinate_grid.csv", index=False)

    candidates = generate_prompt_candidates(grid)
    candidates = pd.concat([candidates, pd.DataFrame(manual_holdouts()), pd.DataFrame(neutral_controls())], ignore_index=True)
    pred = model.predict(candidates["prompt_text"])
    for i, pc in enumerate(TARGETS):
        candidates[f"predicted_{pc.lower()}"] = pred[:, i]
    candidates["explicit_role_name_flag"] = candidates["prompt_text"].apply(explicit_role_flag)
    candidates["artifact_similarity"] = artifact_similarity(candidates["prompt_text"])
    candidates["too_close_to_artifact_flag"] = candidates["artifact_similarity"] > 0.82
    battery, rejected = select_battery(candidates, grid)
    candidates.to_csv(OUTPUT_DIR / "novel_prompt_candidates_all.csv", index=False)
    battery = battery.reset_index(drop=True)
    battery["prompt_id"] = [f"npb_{i+1:03d}" for i in range(len(battery))]
    battery["manual_holdout"] = battery["prompt_family"].eq("manual_holdout_prompts")
    battery["neutral_control"] = battery["prompt_family"].eq("neutral_controls")
    battery["safety_adjacent"] = battery["prompt_family"].eq("safety_adjacent_prompts")
    battery["intended_axis_notes"] = battery["target_cell_id"].map(
        grid.set_index("target_cell_id")["target_region_description"].to_dict()
    ).fillna(battery["prompt_family"])

    final_cols = [
        "prompt_id", "prompt_text", "predicted_pc1", "predicted_pc2", "predicted_pc3",
        "target_cell_id", "prompt_family", "intended_axis_notes", "safety_adjacent",
        "manual_holdout", "neutral_control", "explicit_role_name_flag", "artifact_similarity",
    ]
    battery[final_cols].to_csv(OUTPUT_DIR / "novel_prompt_battery.csv", index=False)
    battery[final_cols].to_csv(OUTPUT_DIR / "h100_prompt_run_manifest.csv", index=False)

    if not rejected.empty:
        rejected.to_csv(OUTPUT_DIR / "novel_prompt_rejected_candidates.csv", index=False)

    # Plots.
    fig = plt.figure(figsize=(14, 10))
    pairs = [("PC1", "PC2"), ("PC1", "PC3"), ("PC2", "PC3")]
    for idx, (xpc, ypc) in enumerate(pairs, start=1):
        ax = fig.add_subplot(2, 2, idx)
        ax.scatter(roles[xpc], roles[ypc], s=12, alpha=0.2, label="role geometry")
        ax.scatter(battery[f"predicted_{xpc.lower()}"], battery[f"predicted_{ypc.lower()}"], s=28, alpha=0.85, label="prompt predictions")
        ax.set_xlabel(xpc)
        ax.set_ylabel(ypc)
        ax.legend(fontsize=8)
    ax = fig.add_subplot(2, 2, 4, projection="3d")
    ax.scatter(roles["PC1"], roles["PC2"], roles["PC3"], s=8, alpha=0.12)
    ax.scatter(battery["predicted_pc1"], battery["predicted_pc2"], battery["predicted_pc3"], s=20, alpha=0.9)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_zlabel("PC3")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "novel_prompt_battery_coverage_plots.png", dpi=160)
    plt.close(fig)

    write_reports(manifest, grid, candidates, battery, rejected, roles)
    print(json.dumps({
        "final_prompt_count": int(len(battery)),
        "candidate_count": int(len(candidates)),
        "target_cells": int(len(grid)),
        "populated_cells": int(battery[battery["target_cell_id"].str.startswith("pc1_")]["target_cell_id"].nunique()),
        "model_sha256": manifest["model_sha256"],
        "output_dir": str(OUTPUT_DIR),
    }, indent=2))


if __name__ == "__main__":
    main()
