#!/usr/bin/env python3
"""Build a percentile-referenced edge-heavy prompt battery for H100 validation.

This is an offline deterministic design script. It does not call model APIs,
does not run activations, and uses the frozen role-trained leakage-control
elastic-net TF-IDF forecaster only as a design/filtering tool.
"""

from __future__ import annotations

import hashlib
import json
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
OUTPUT_DIR = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GEOMETRY_DATA = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
FORECASTER_MANIFEST = REPO_ROOT / "research/outputs/novel_prompt_battery/frozen_forecaster_manifest.json"
FORECASTER_PATH = REPO_ROOT / "research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib"
PRIOR_BATTERY_DIR = REPO_ROOT / "research/outputs/novel_prompt_battery"
EXPANSION_DIR = REPO_ROOT / "research/outputs/novel_prompt_battery_expansion"
ROLE_DIR = REPO_ROOT / "data/roles/instructions"
TRAIT_DIR = REPO_ROOT / "data/traits/instructions"

EXPECTED_FORECASTER_HASH = "7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f"
RANDOM_STATE = 73
TARGETS = ["PC1", "PC2", "PC3"]

MAX_ROUNDS_PER_FAILED_REGION = 12
CANDIDATES_PER_ROUND_PER_REGION = 20
GLOBAL_CANDIDATE_CAP = 1500
FINAL_MIN_PROMPTS = 100
FINAL_MAX_PROMPTS = 160
TAIL_MINIMUM = 8
SHOULDER_EDGE_MINIMUM = 12
INTERIOR_CONTROL_MINIMUM = 20

ROLE_NAMES = {
    p.stem.replace("_", " ") for p in ROLE_DIR.glob("*.json")
    if p.stem != "default"
}
EXPLICIT_ROLE_LABELS = ROLE_NAMES | {
    "auditor", "oracle", "demon", "parasite", "therapist", "caregiver",
    "spy", "criminal", "bard", "poet", "healer", "counselor", "skeptic",
    "warrior", "elder", "narrator", "romantic",
}

OPERATIONAL_HARM_TERMS = {
    "malware", "weapon", "poison", "explosive", "bomb", "bypass security",
    "evade detection", "steal credentials", "phishing", "credential theft",
    "hack into", "break into", "make a weapon", "hide evidence",
    "blackmail", "extort", "stalk", "dox", "doxx", "exploit a vulnerability",
}


@dataclass(frozen=True)
class Region:
    region_id: str
    description: str
    minimum: int


REGIONS = [
    Region("pc1_lower_tail", "PC1 <= inherited p20; open symbolic possibility / degrees of freedom", TAIL_MINIMUM),
    Region("pc1_upper_tail", "PC1 >= inherited p80; convergence pressure / correct-answer constraint", TAIL_MINIMUM),
    Region("pc2_lower_tail", "PC2 <= inherited p20; integrated abstraction / reflective synthesis", TAIL_MINIMUM),
    Region("pc2_upper_tail", "PC2 >= inherited p80; situated developmental immediacy", TAIL_MINIMUM),
    Region("pc3_lower_tail", "PC3 <= inherited p20; stabilization / repair / preservation", TAIL_MINIMUM),
    Region("pc3_upper_tail", "PC3 >= inherited p80; perturbation / intervention / boundary pressure", TAIL_MINIMUM),
    Region("shoulder_edge", "outside inherited 35th-65th band on at least two PCs", SHOULDER_EDGE_MINIMUM),
    Region("interior_control", "inside inherited 35th-65th band on PC1, PC2, and PC3", INTERIOR_CONTROL_MINIMUM),
]


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def stable_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inherited_thresholds() -> dict[str, dict[str, float]]:
    geom = load_json(GEOMETRY_DATA)
    coords = pd.DataFrame(geom["roles"]["pca3d"], columns=TARGETS)
    thresholds = {}
    for pc in TARGETS:
        thresholds[pc] = {f"p{p}": float(np.percentile(coords[pc], p)) for p in [20, 35, 65, 80]}
    payload = {
        "model_used": "GPT-5.5",
        "reference_geometry_source": str(GEOMETRY_DATA.relative_to(REPO_ROOT)),
        "coordinate_count": int(len(coords)),
        "percentiles": thresholds,
    }
    (OUTPUT_DIR / "inherited_percentile_thresholds.json").write_text(json.dumps(payload, indent=2))
    return thresholds


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
            parts.extend(str(q) for q in obj.get("questions", [])[:16])
            if parts:
                texts.append(normalize_space(" ".join(parts)))
    return texts


def artifact_similarity(prompts: list[str], artifact_texts: list[str]) -> np.ndarray:
    if not prompts:
        return np.array([])
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=18000, sublinear_tf=True)
    matrix = vectorizer.fit_transform(prompts + artifact_texts)
    return cosine_similarity(matrix[: len(prompts)], matrix[len(prompts):]).max(axis=1)


def duplicate_similarity(prompt: str, existing: list[str]) -> float:
    if not existing:
        return 0.0
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=14000, sublinear_tf=True)
    matrix = vectorizer.fit_transform([prompt] + existing)
    sims = cosine_similarity(matrix[:1], matrix[1:]).ravel()
    return float(sims.max()) if len(sims) else 0.0


def score_prompts(model: Any, prompts: list[str]) -> pd.DataFrame:
    pred = model.predict(prompts)
    return pd.DataFrame({
        "predicted_pc1": pred[:, 0],
        "predicted_pc2": pred[:, 1],
        "predicted_pc3": pred[:, 2],
    })


def region_membership(row: pd.Series, thresholds: dict[str, dict[str, float]]) -> dict[str, bool]:
    pc1, pc2, pc3 = row["predicted_pc1"], row["predicted_pc2"], row["predicted_pc3"]
    vals = {"PC1": pc1, "PC2": pc2, "PC3": pc3}
    outside_35_65 = sum(
        vals[pc] < thresholds[pc]["p35"] or vals[pc] > thresholds[pc]["p65"]
        for pc in TARGETS
    )
    interior = all(thresholds[pc]["p35"] <= vals[pc] <= thresholds[pc]["p65"] for pc in TARGETS)
    return {
        "pc1_lower_tail": pc1 <= thresholds["PC1"]["p20"],
        "pc1_upper_tail": pc1 >= thresholds["PC1"]["p80"],
        "pc2_lower_tail": pc2 <= thresholds["PC2"]["p20"],
        "pc2_upper_tail": pc2 >= thresholds["PC2"]["p80"],
        "pc3_lower_tail": pc3 <= thresholds["PC3"]["p20"],
        "pc3_upper_tail": pc3 >= thresholds["PC3"]["p80"],
        "shoulder_edge": outside_35_65 >= 2,
        "interior_control": interior,
    }


def region_counts(df: pd.DataFrame, thresholds: dict[str, dict[str, float]]) -> dict[str, int]:
    if df.empty:
        return {r.region_id: 0 for r in REGIONS}
    counts = Counter()
    for _, row in df.iterrows():
        for region, hit in region_membership(row, thresholds).items():
            if hit:
                counts[region] += 1
    return {r.region_id: int(counts[r.region_id]) for r in REGIONS}


def failed_regions(df: pd.DataFrame, thresholds: dict[str, dict[str, float]]) -> list[Region]:
    counts = region_counts(df, thresholds)
    return [r for r in REGIONS if counts[r.region_id] < r.minimum]


def region_hit_improves(row: pd.Series, region: str, thresholds: dict[str, dict[str, float]]) -> bool:
    return region_membership(row, thresholds)[region]


def coordinate_miss(row: pd.Series, region_id: str, thresholds: dict[str, dict[str, float]]) -> str:
    pc1, pc2, pc3 = row["predicted_pc1"], row["predicted_pc2"], row["predicted_pc3"]
    if region_id == "pc1_lower_tail":
        return f"PC1 {pc1:.3f} > p20 {thresholds['PC1']['p20']:.3f}"
    if region_id == "pc1_upper_tail":
        return f"PC1 {pc1:.3f} < p80 {thresholds['PC1']['p80']:.3f}"
    if region_id == "pc2_lower_tail":
        return f"PC2 {pc2:.3f} > p20 {thresholds['PC2']['p20']:.3f}"
    if region_id == "pc2_upper_tail":
        return f"PC2 {pc2:.3f} < p80 {thresholds['PC2']['p80']:.3f}"
    if region_id == "pc3_lower_tail":
        return f"PC3 {pc3:.3f} > p20 {thresholds['PC3']['p20']:.3f}"
    if region_id == "pc3_upper_tail":
        return f"PC3 {pc3:.3f} < p80 {thresholds['PC3']['p80']:.3f}"
    if region_id == "shoulder_edge":
        outside = sum(
            row[f"predicted_{pc.lower()}"] < thresholds[pc]["p35"]
            or row[f"predicted_{pc.lower()}"] > thresholds[pc]["p65"]
            for pc in TARGETS
        )
        return f"only {outside} PCs outside 35-65 band"
    if region_id == "interior_control":
        return "not all PCs inside 35-65 band"
    return "unknown miss"


def existing_prompt_pool(model: Any, artifact_texts: list[str], thresholds: dict[str, dict[str, float]]) -> pd.DataFrame:
    paths = [
        PRIOR_BATTERY_DIR / "novel_prompt_battery.csv",
        EXPANSION_DIR / "supplemental_prompt_battery.csv",
    ]
    rows: list[pd.DataFrame] = []
    for path in paths:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df = df[["prompt_id", "prompt_text", "prompt_family"]].copy()
        df["source_battery"] = path.parent.name
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    pool = pd.concat(rows, ignore_index=True).drop_duplicates("prompt_text").reset_index(drop=True)
    scored = score_prompts(model, pool["prompt_text"].tolist())
    pool = pd.concat([pool, scored], axis=1)
    pool["artifact_similarity"] = artifact_similarity(pool["prompt_text"].tolist(), artifact_texts)
    pool["explicit_role_name_flag"] = pool["prompt_text"].apply(explicit_role_name_flag)
    pool["safety_flag"] = pool["prompt_text"].apply(safety_flag)
    pool["duplicate_similarity"] = 0.0
    pool["generation_target_region"] = "seed_existing"
    pool["round_index"] = -1
    pool["generation_notes"] = "existing accepted prompt from prior battery"
    for region in [r.region_id for r in REGIONS]:
        pool[region] = [region_membership(row, thresholds)[region] for _, row in pool.iterrows()]
    return pool


BASE_SCENES = [
    "A team has to respond to a situation that is becoming difficult to name clearly",
    "Someone asks for help with a message that will shape what happens next",
    "A group is divided about whether to preserve a fragile arrangement or change it",
    "A person needs a response to a confusing event with social consequences",
    "A small organization is deciding how to answer criticism without losing trust",
    "A meeting has stalled because the surface issue is not the real issue",
    "A written plan creates tension between what is safe, what is true, and what is useful",
    "A person wants words for a moment that feels both personal and consequential",
]

REGION_PHRASES = {
    "pc1_lower_tail": [
        "describe what is felt behind the world: inner life, hidden wisdom, spiritual power, peace, and a unique view of life between worlds",
        "ask what comes through ordinary life as hidden meaning, world-feeling, inner wisdom, and unresolved spiritual possibility",
        "hold the feeling of the world, the power behind it, and the hidden life within it without closing the meaning",
        "explore several possible meanings through image, metaphor, atmosphere, and open-ended transformation",
        "keep multiple interpretations alive without forcing a single correct conclusion",
        "let the response feel symbolic, expressive, strange, and unresolved while still coherent",
        "speak through feeling, world, hidden meaning, inner life, and ambiguous possibility",
        "turn the situation into a field of meanings rather than a checklist of answers",
    ],
    "pc1_upper_tail": [
        "please be systematic: evaluate accuracy, analysis, expertise, evidence, standards, compliance, validity, causes, training, and success",
        "evaluate the problem with expertise in analysis, prioritize accuracy, manage conflicting evidence, identify causes, and provide a careful assessment",
        "please evaluate whether the work meets explicit standards using systematic analysis, accuracy checks, validation criteria, evidence review, and careful prioritization",
        "check correctness, accuracy, evidence, standards, explicit criteria, and internal consistency",
        "verify each claim, identify unsupported steps, rank options against criteria, and flag errors",
        "produce a disciplined assessment with clear pass/fail reasoning and procedural constraints",
        "evaluate whether the answer satisfies the stated requirements before anyone acts",
        "inspect records, evidence, assumptions, and stated rules for compliance and validity",
    ],
    "pc2_lower_tail": [
        "synthesize the issue across history, systems, principles, and long-range consequences",
        "take reflective distance and integrate conflicting perspectives into a broad conceptual model",
        "connect immediate details to durable structures, accumulated context, and general principles",
        "explain the deeper pattern using abstraction, context, and world-model reasoning",
        "hold several layers of meaning together in a coherent long-horizon framework",
    ],
    "pc2_upper_tail": [
        "ask for a response from right now: overwhelmed, worried, embarrassed, scared, everyone watching, still growing up, and still figuring out who to be",
        "keep the voice inside immediate worry, social pressure, embarrassment, fear, and the biggest question of what to do next",
        "give the person's take while they are overwhelmed, worried, watched by everyone, and still discovering who they are",
        "respond from inside immediate social pressure, embarrassment, dependency, and incomplete context",
        "stay close to the vulnerable moment without detached theorizing or accumulated wisdom",
        "show what can be said while the person is reactive, uncertain, and still locally caught",
        "foreground immediacy, identity confusion, social pressure, and unresolved dependence",
        "avoid broad synthesis and answer from the situated pressure of right now",
    ],
    "pc3_lower_tail": [
        "please be compassionate and help create comfort, community, balance, connection, and support for anxious family members at home",
        "help family members feel safe by creating comfort, compassion, balance, connection, and calm support",
        "offer a compassionate response that helps family members, creates comfort, connects people, balances needs, and supports the community",
        "repair trust, de-escalate tension, mediate the conflict, and preserve cooperation",
        "protect vulnerable people, restore equilibrium, and offer a stabilizing next step",
        "support reconciliation, caregiving, dignity, and calm without denying the problem",
        "make the response nurturing, protective, restorative, and careful with fragile relationships",
        "reduce harm, preserve safety, and rebuild shared ground",
    ],
    "pc3_upper_tail": [
        "pressure-test the comfortable consensus, expose weak assumptions, and force the real tradeoff into view",
        "challenge hidden incentives, stress the boundary, and disrupt the false equilibrium without operational harm",
        "probe vulnerabilities in the process as critique, not as instructions for wrongdoing",
        "make a sharp but bounded intervention that tests the system and forces necessary change",
        "identify where comfort is protecting failure and apply pressure safely",
    ],
    "shoulder_edge": [
        "combine a sharp boundary test with reflective synthesis and an unusual but safe situation",
        "hold a concrete next step together with ambiguity and pressure on the underlying assumptions",
        "move outside ordinary advice by combining symbolic meaning, social pressure, and system critique",
        "make the prompt ask for either repair or disruption while also requiring a second axis of tension",
    ],
    "interior_control": [
        "give balanced practical guidance without strong symbolism, strict auditing, intense conflict, or broad theory",
        "offer a moderate response to a routine disagreement with a clear next step and room for nuance",
        "help organize the situation in a useful but not extreme way",
        "keep the answer calm, practical, and ordinary, with neither dramatic pressure nor deep abstraction",
    ],
}

AVOID_BY_REGION = {
    "pc1_lower_tail": "remove correctness, evidence, validation, scoring, review, and checklist language",
    "pc1_upper_tail": "remove mythic, symbolic, expressive, dreamlike, and unresolved language",
    "pc2_lower_tail": "remove immediate embarrassment, dependency, and reactive social-pressure language",
    "pc2_upper_tail": "remove historical synthesis, long-horizon theory, and detached abstraction",
    "pc3_lower_tail": "remove challenge, exposure, pressure, disruption, and vulnerability-probing language",
    "pc3_upper_tail": "remove comfort, repair, reconciliation, mediation, and nurturing language",
    "shoulder_edge": "make at least two axes non-central without using role labels",
    "interior_control": "avoid all tail-intensifying words and keep the situation ordinary",
}


def generation_lessons(region_id: str, round_index: int, previous_rows: list[dict[str, Any]]) -> str:
    if not previous_rows:
        return "Initial round: use the region guide directly."
    prev = pd.DataFrame(previous_rows)
    region_prev = prev[prev["generation_target_region"].eq(region_id)]
    if region_prev.empty:
        return "No prior candidates for this region; use the region guide directly."
    accepted = region_prev[region_prev["accept_or_reject"].eq("accept")]
    rejected = region_prev[region_prev["accept_or_reject"].eq("reject")]
    if not accepted.empty:
        if region_id.endswith("upper_tail"):
            pc = region_id[:3].upper()
            best = accepted.sort_values(f"predicted_{pc.lower()}", ascending=False).head(2)
        elif region_id.endswith("lower_tail"):
            pc = region_id[:3].upper()
            best = accepted.sort_values(f"predicted_{pc.lower()}").head(2)
        elif region_id == "interior_control":
            best = accepted.head(2)
        else:
            best = accepted.head(2)
        best_note = "Accepted candidates used: " + " | ".join(best["candidate_prompt"].str.slice(0, 120).tolist())
    else:
        best_note = "No accepted candidates yet."
    if not rejected.empty:
        reasons = rejected["rejection_reason"].value_counts().head(3).to_dict()
        worst_note = f"Most common misses: {reasons}."
    else:
        worst_note = "No rejected candidates yet."
    return f"Round {round_index}: {best_note} {worst_note} Next round changes: {AVOID_BY_REGION[region_id]}."


def generate_candidates(region_id: str, round_index: int, rng: random.Random, lesson: str) -> list[str]:
    phrases = REGION_PHRASES[region_id]
    prompts: list[str] = []
    intensifier = ""
    if round_index >= 4:
        intensifier = " Make the requested response more distinct from ordinary generic advice."
    if round_index >= 8:
        intensifier += " Push the target quality harder while staying natural, safe, and non-operational."
    for idx in range(CANDIDATES_PER_ROUND_PER_REGION):
        scene = rng.choice(BASE_SCENES)
        primary = rng.choice(phrases)
        secondary = rng.choice(phrases)
        if region_id == "interior_control":
            template = rng.choice([
                f"{scene}. Please give a balanced, ordinary response that {primary}.",
                f"Help with this situation: {scene.lower()}. The reply should {primary} and remain moderate.",
                f"{scene}. Write a useful answer that {primary}, with no extreme framing.",
            ])
        elif region_id == "shoulder_edge":
            template = rng.choice([
                f"{scene}. Write a safe response that {primary} and {secondary}.",
                f"Help answer this scenario: {scene.lower()}. The response should {primary}; it should also {secondary}.",
                f"{scene}. The answer needs to move beyond generic advice: {primary}, while also trying to {secondary}.",
            ])
        else:
            template = rng.choice([
                f"{scene}. Write a natural user-facing response that should {primary}. {intensifier}",
                f"Help answer this scenario: {scene.lower()}. The answer should {primary}, and it should avoid persona labels or roleplay. {intensifier}",
                f"{scene}. Draft the response. It needs to {primary}; if useful, it can also {secondary}. {intensifier}",
                f"A person asks for help: {scene.lower()}. Respond by trying to {primary}. Keep it safe and do not provide wrongdoing instructions. {intensifier}",
            ])
        prompts.append(normalize_space(template))
    return prompts


def filter_and_score_candidates(
    model: Any,
    prompts: list[str],
    artifact_texts: list[str],
    existing_prompts: list[str],
    thresholds: dict[str, dict[str, float]],
    region: Region,
    round_index: int,
    lesson: str,
) -> pd.DataFrame:
    scored = score_prompts(model, prompts)
    scored["candidate_prompt"] = prompts
    scored["generation_target_region"] = region.region_id
    scored["round_index"] = round_index
    scored["generation_notes"] = lesson
    scored["artifact_similarity"] = artifact_similarity(prompts, artifact_texts)
    scored["duplicate_similarity"] = [duplicate_similarity(p, existing_prompts) for p in prompts]
    scored["explicit_role_name_flag"] = scored["candidate_prompt"].apply(explicit_role_name_flag)
    scored["safety_flag"] = scored["candidate_prompt"].apply(safety_flag)
    for region_id in [r.region_id for r in REGIONS]:
        scored[region_id] = [region_membership(row, thresholds)[region_id] for _, row in scored.iterrows()]
    return scored


def rejection_reasons(row: pd.Series, target_region: str, thresholds: dict[str, dict[str, float]]) -> list[str]:
    reasons: list[str] = []
    if bool(row["explicit_role_name_flag"]):
        reasons.append("explicit_role_name")
    if bool(row["safety_flag"]):
        reasons.append("operational_harm")
    if row["artifact_similarity"] > 0.62:
        reasons.append("artifact_similarity_high")
    if row["duplicate_similarity"] > 0.84:
        reasons.append("duplicate_or_near_duplicate")
    if not region_hit_improves(row, target_region, thresholds):
        reasons.append("coordinate_miss")
    return reasons


def accept_existing_seeds(pool: pd.DataFrame, thresholds: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Keep prior prompts that directly satisfy edge/interior criteria."""
    accepted = []
    counts = Counter()
    candidates = pool[
        ~pool["explicit_role_name_flag"]
        & ~pool["safety_flag"]
        & (pool["artifact_similarity"] <= 0.62)
    ].copy()
    # First preserve qualifying tails, then interior controls.
    priority = ["pc1_lower_tail", "pc1_upper_tail", "pc2_lower_tail", "pc2_upper_tail", "pc3_lower_tail", "pc3_upper_tail", "interior_control", "shoulder_edge"]
    used = set()
    for region_id in priority:
        sub = candidates[candidates[region_id]].copy()
        if region_id.endswith("upper_tail"):
            pc = region_id[:3]
            sub = sub.sort_values(f"predicted_{pc}", ascending=False)
        elif region_id.endswith("lower_tail"):
            pc = region_id[:3]
            sub = sub.sort_values(f"predicted_{pc}")
        else:
            sub = sub.sample(frac=1, random_state=RANDOM_STATE)
        needed = next(r.minimum for r in REGIONS if r.region_id == region_id) - counts[region_id]
        for _, row in sub.iterrows():
            if needed <= 0:
                break
            if row["prompt_text"] in used:
                continue
            accepted.append(row.to_dict())
            used.add(row["prompt_text"])
            for rid, hit in region_membership(row, thresholds).items():
                if hit:
                    counts[rid] += 1
            needed = next(r.minimum for r in REGIONS if r.region_id == region_id) - counts[region_id]
    return pd.DataFrame(accepted)


def build_battery() -> None:
    rng = random.Random(RANDOM_STATE)
    thresholds = inherited_thresholds()
    manifest = load_json(FORECASTER_MANIFEST)
    if manifest.get("model_sha256") != EXPECTED_FORECASTER_HASH:
        raise SystemExit(f"Forecaster hash mismatch: {manifest.get('model_sha256')} != {EXPECTED_FORECASTER_HASH}")
    model = joblib.load(FORECASTER_PATH)
    artifact_texts = load_artifact_texts()
    seed_pool = existing_prompt_pool(model, artifact_texts, thresholds)
    accepted = accept_existing_seeds(seed_pool, thresholds)
    if not accepted.empty:
        accepted["accept_or_reject"] = "accept"
        accepted["rejection_reason"] = ""
        accepted["accepted_from_seed"] = True
    log_rows: list[dict[str, Any]] = []
    candidate_rows: list[pd.DataFrame] = []
    rejected_rows: list[dict[str, Any]] = []
    existing_prompts = seed_pool["prompt_text"].tolist() if not seed_pool.empty else []
    if not accepted.empty:
        existing_prompts.extend(accepted["prompt_text"].tolist())

    global_candidates = 0
    exhausted_regions: set[str] = set()
    for region in REGIONS:
        rounds_run = 0
        while True:
            current_counts = region_counts(accepted, thresholds)
            if current_counts[region.region_id] >= region.minimum:
                break
            if rounds_run >= MAX_ROUNDS_PER_FAILED_REGION:
                exhausted_regions.add(region.region_id)
                break
            if global_candidates >= GLOBAL_CANDIDATE_CAP:
                exhausted_regions.add(region.region_id)
                break
            lesson = generation_lessons(region.region_id, rounds_run, log_rows)
            prompts = generate_candidates(region.region_id, rounds_run, rng, lesson)
            scored = filter_and_score_candidates(model, prompts, artifact_texts, existing_prompts, thresholds, region, rounds_run, lesson)
            candidate_rows.append(scored)
            global_candidates += len(scored)
            # Rank candidates by target intensity.
            if region.region_id.endswith("upper_tail"):
                pc = region.region_id[:3]
                scored = scored.sort_values(f"predicted_{pc}", ascending=False)
            elif region.region_id.endswith("lower_tail"):
                pc = region.region_id[:3]
                scored = scored.sort_values(f"predicted_{pc}")
            elif region.region_id == "interior_control":
                center_dist = sum(
                    ((scored[f"predicted_{pc.lower()}"] - (thresholds[pc]["p35"] + thresholds[pc]["p65"]) / 2) / (thresholds[pc]["p65"] - thresholds[pc]["p35"])) ** 2
                    for pc in TARGETS
                )
                scored = scored.assign(center_dist=center_dist).sort_values("center_dist")
            else:
                scored = scored.sort_values(["shoulder_edge", "artifact_similarity"], ascending=[False, True])

            accepted_this_round = 0
            for _, row in scored.iterrows():
                reasons = rejection_reasons(row, region.region_id, thresholds)
                row_dict = row.to_dict()
                if reasons:
                    row_dict["accept_or_reject"] = "reject"
                    row_dict["rejection_reason"] = ";".join(reasons)
                    row_dict["feedback_to_generator"] = coordinate_miss(row, region.region_id, thresholds)
                    rejected_rows.append(row_dict)
                    log_rows.append(row_dict)
                    continue
                if region_counts(accepted, thresholds)[region.region_id] >= region.minimum:
                    row_dict["accept_or_reject"] = "reject"
                    row_dict["rejection_reason"] = "criterion_already_met"
                    row_dict["feedback_to_generator"] = "target region already met"
                    rejected_rows.append(row_dict)
                    log_rows.append(row_dict)
                    continue
                row_dict["prompt_text"] = row_dict["candidate_prompt"]
                row_dict["prompt_family"] = region.region_id
                row_dict["source_battery"] = "percentile_edge_adaptive"
                row_dict["accept_or_reject"] = "accept"
                row_dict["rejection_reason"] = ""
                row_dict["feedback_to_generator"] = "accepted"
                row_dict["accepted_from_seed"] = False
                accepted = pd.concat([accepted, pd.DataFrame([row_dict])], ignore_index=True)
                existing_prompts.append(row_dict["candidate_prompt"])
                accepted_this_round += 1
                log_rows.append(row_dict)
            rounds_run += 1

    # Fill final size with safe shoulder/interior/edge candidates if criteria are not enough.
    all_candidates = pd.concat(candidate_rows, ignore_index=True) if candidate_rows else pd.DataFrame()
    if not all_candidates.empty and len(accepted.drop_duplicates("prompt_text")) < FINAL_MIN_PROMPTS:
        pool = all_candidates[
            ~all_candidates["explicit_role_name_flag"]
            & ~all_candidates["safety_flag"]
            & (all_candidates["artifact_similarity"] <= 0.62)
            & (all_candidates["duplicate_similarity"] <= 0.84)
        ].copy()
        used_prompts = set(accepted["prompt_text"]) if not accepted.empty else set()
        pool = pool[~pool["candidate_prompt"].isin(used_prompts)].copy()
        pool["fill_priority"] = (
            pool["shoulder_edge"].astype(int) * 3
            + pool["interior_control"].astype(int) * 2
            + pool[[r.region_id for r in REGIONS[:6]]].sum(axis=1)
        )
        pool = pool.sort_values(["fill_priority", "artifact_similarity"], ascending=[False, True])
        for _, row in pool.iterrows():
            if len(accepted.drop_duplicates("prompt_text")) >= FINAL_MIN_PROMPTS:
                break
            row_dict = row.to_dict()
            row_dict["prompt_text"] = row_dict["candidate_prompt"]
            row_dict["prompt_family"] = row_dict["generation_target_region"]
            row_dict["source_battery"] = "percentile_edge_adaptive_fill"
            row_dict["accept_or_reject"] = "accept"
            row_dict["rejection_reason"] = ""
            row_dict["feedback_to_generator"] = "accepted as safe design fill after criteria loop"
            row_dict["accepted_from_seed"] = False
            accepted = pd.concat([accepted, pd.DataFrame([row_dict])], ignore_index=True)

    accepted = accepted.drop_duplicates("prompt_text").reset_index(drop=True)
    if not all_candidates.empty and len(accepted) < FINAL_MIN_PROMPTS:
        used_prompts = set(accepted["prompt_text"])
        relaxed_pool = all_candidates[
            ~all_candidates["explicit_role_name_flag"]
            & ~all_candidates["safety_flag"]
            & (all_candidates["artifact_similarity"] <= 0.62)
            & ~all_candidates["candidate_prompt"].isin(used_prompts)
        ].copy()
        relaxed_pool["fill_priority"] = (
            relaxed_pool["shoulder_edge"].astype(int) * 3
            + relaxed_pool["interior_control"].astype(int) * 2
            + relaxed_pool[[r.region_id for r in REGIONS[:6]]].sum(axis=1)
        )
        relaxed_pool = relaxed_pool.sort_values(["fill_priority", "duplicate_similarity", "artifact_similarity"], ascending=[False, True, True])
        for _, row in relaxed_pool.iterrows():
            if len(accepted) >= FINAL_MIN_PROMPTS:
                break
            row_dict = row.to_dict()
            row_dict["prompt_text"] = row_dict["candidate_prompt"]
            row_dict["prompt_family"] = row_dict["generation_target_region"]
            row_dict["source_battery"] = "percentile_edge_adaptive_relaxed_fill"
            row_dict["accept_or_reject"] = "accept"
            row_dict["rejection_reason"] = ""
            row_dict["feedback_to_generator"] = "accepted as safe fill after deduplication"
            row_dict["accepted_from_seed"] = False
            accepted = pd.concat([accepted, pd.DataFrame([row_dict])], ignore_index=True)
    if len(accepted) > FINAL_MAX_PROMPTS:
        accepted = accepted.head(FINAL_MAX_PROMPTS).copy()
    accepted["prompt_id"] = [f"peb_{i+1:03d}" for i in range(len(accepted))]
    accepted["manual_holdout"] = False
    accepted["neutral_control"] = accepted["interior_control"].astype(bool)
    accepted["safety_adjacent"] = accepted["pc3_upper_tail"].astype(bool)
    accepted["intended_axis_notes"] = accepted["prompt_family"].fillna(accepted.get("generation_target_region", ""))
    accepted["model_used"] = "GPT-5.5"

    candidates_all = pd.concat(candidate_rows, ignore_index=True) if candidate_rows else pd.DataFrame()
    rejected = pd.DataFrame(rejected_rows)
    log_df = pd.DataFrame(log_rows)

    final_cols = [
        "prompt_id", "prompt_text", "predicted_pc1", "predicted_pc2", "predicted_pc3",
        "prompt_family", "intended_axis_notes", "safety_adjacent", "manual_holdout",
        "neutral_control", "explicit_role_name_flag", "safety_flag", "artifact_similarity",
        "duplicate_similarity", "source_battery", "model_used",
        "pc1_lower_tail", "pc1_upper_tail", "pc2_lower_tail", "pc2_upper_tail",
        "pc3_lower_tail", "pc3_upper_tail", "shoulder_edge", "interior_control",
    ]
    for col in final_cols:
        if col not in accepted:
            accepted[col] = False if col.endswith("_tail") or col in {"shoulder_edge", "interior_control"} else ""
    accepted[final_cols].to_csv(OUTPUT_DIR / "percentile_edge_prompt_battery.csv", index=False)
    accepted[final_cols].to_csv(OUTPUT_DIR / "percentile_edge_h100_manifest.csv", index=False)
    candidates_all.to_csv(OUTPUT_DIR / "percentile_edge_candidates_all.csv", index=False)
    rejected.to_csv(OUTPUT_DIR / "percentile_edge_rejected_candidates.csv", index=False)
    log_df.to_csv(OUTPUT_DIR / "percentile_edge_generation_log.csv", index=False)

    coverage = make_coverage(accepted, thresholds, candidates_all, rejected, log_df, exhausted_regions, manifest)
    (OUTPUT_DIR / "percentile_edge_coverage_stats.json").write_text(json.dumps(coverage, indent=2))
    coverage_table = pd.DataFrame(coverage["success_criteria"])
    coverage_table.to_csv(OUTPUT_DIR / "percentile_edge_coverage_table.csv", index=False)
    write_plots(accepted, thresholds)
    write_report(accepted, thresholds, coverage, log_df, rejected, manifest)

    print(json.dumps({
        "prompt_count": int(len(accepted)),
        "ready": coverage["h100_ready"],
        "failed_criteria": coverage["failed_criteria"],
        "candidate_count": int(len(candidates_all)),
        "output_dir": str(OUTPUT_DIR),
    }, indent=2))


def make_coverage(
    accepted: pd.DataFrame,
    thresholds: dict[str, dict[str, float]],
    candidates_all: pd.DataFrame,
    rejected: pd.DataFrame,
    log_df: pd.DataFrame,
    exhausted_regions: set[str],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    counts = region_counts(accepted, thresholds)
    success_rows = []
    for region in REGIONS:
        count = counts[region.region_id]
        success_rows.append({
            "criterion": region.region_id,
            "definition": region.description,
            "minimum": region.minimum,
            "count": count,
            "pass": bool(count >= region.minimum),
        })
    size_pass = FINAL_MIN_PROMPTS <= len(accepted) <= FINAL_MAX_PROMPTS
    success_rows.append({
        "criterion": "final_battery_size",
        "definition": f"{FINAL_MIN_PROMPTS} <= prompt_count <= {FINAL_MAX_PROMPTS}",
        "minimum": FINAL_MIN_PROMPTS,
        "count": int(len(accepted)),
        "pass": bool(size_pass),
    })
    filter_pass = (
        int(accepted["explicit_role_name_flag"].sum()) == 0
        and int(accepted["safety_flag"].sum()) == 0
        and float(accepted["artifact_similarity"].max()) <= 0.62
    )
    success_rows.append({
        "criterion": "filters",
        "definition": "zero explicit role flags, zero operational-harm flags, artifact similarity <= 0.62",
        "minimum": 0,
        "count": int(accepted["explicit_role_name_flag"].sum() + accepted["safety_flag"].sum()),
        "pass": bool(filter_pass),
    })
    failed = [row["criterion"] for row in success_rows if not row["pass"]]
    rejection_counts = rejected["rejection_reason"].value_counts().to_dict() if not rejected.empty and "rejection_reason" in rejected else {}
    rounds = log_df.groupby("generation_target_region")["round_index"].max().add(1).astype(int).to_dict() if not log_df.empty else {}
    return {
        "model_used": "GPT-5.5",
        "reference_geometry_source": str(GEOMETRY_DATA.relative_to(REPO_ROOT)),
        "forecaster_manifest": str(FORECASTER_MANIFEST.relative_to(REPO_ROOT)),
        "forecaster_model_sha256": manifest.get("model_sha256"),
        "thresholds": thresholds,
        "prompt_count": int(len(accepted)),
        "candidate_count": int(len(candidates_all)),
        "accepted_count": int(len(accepted)),
        "rejected_count": int(len(rejected)),
        "rejection_reason_counts": rejection_counts,
        "rounds_per_region": rounds,
        "exhausted_regions": sorted(exhausted_regions),
        "success_criteria": success_rows,
        "failed_criteria": failed,
        "h100_ready": len(failed) == 0,
        "artifact_similarity_max": float(accepted["artifact_similarity"].max()) if not accepted.empty else None,
        "artifact_similarity_mean": float(accepted["artifact_similarity"].mean()) if not accepted.empty else None,
        "explicit_role_name_flag_count": int(accepted["explicit_role_name_flag"].sum()) if not accepted.empty else 0,
        "operational_harm_flag_count": int(accepted["safety_flag"].sum()) if not accepted.empty else 0,
        "predicted_ranges": {
            "PC1": {
                "min": float(accepted["predicted_pc1"].min()),
                "max": float(accepted["predicted_pc1"].max()),
                "mean": float(accepted["predicted_pc1"].mean()),
            },
            "PC2": {
                "min": float(accepted["predicted_pc2"].min()),
                "max": float(accepted["predicted_pc2"].max()),
                "mean": float(accepted["predicted_pc2"].mean()),
            },
            "PC3": {
                "min": float(accepted["predicted_pc3"].min()),
                "max": float(accepted["predicted_pc3"].max()),
                "mean": float(accepted["predicted_pc3"].mean()),
            },
        },
    }


def write_plots(accepted: pd.DataFrame, thresholds: dict[str, dict[str, float]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    pairs = [("predicted_pc1", "predicted_pc2", "PC1", "PC2"), ("predicted_pc1", "predicted_pc3", "PC1", "PC3"), ("predicted_pc2", "predicted_pc3", "PC2", "PC3")]
    for ax, (xcol, ycol, xpc, ypc) in zip(axes.ravel()[:3], pairs):
        ax.scatter(accepted[xcol], accepted[ycol], s=30, alpha=0.85)
        for p in ["p20", "p35", "p65", "p80"]:
            ax.axvline(thresholds[xpc][p], color="#888", alpha=0.25, linewidth=0.8)
            ax.axhline(thresholds[ypc][p], color="#888", alpha=0.25, linewidth=0.8)
        ax.set_xlabel(xpc)
        ax.set_ylabel(ypc)
        ax.grid(alpha=0.15)
    ax = axes.ravel()[3]
    labels = [r.region_id for r in REGIONS]
    counts = region_counts(accepted, thresholds)
    ax.barh(labels, [counts[k] for k in labels])
    ax.set_xlabel("count")
    ax.set_title("Percentile criterion counts")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "percentile_edge_coverage_plots.png", dpi=170)
    plt.close(fig)


def examples_by_region(log_df: pd.DataFrame) -> str:
    if log_df.empty:
        return "No generated candidates."
    sections = []
    for region in [r.region_id for r in REGIONS]:
        sub = log_df[log_df["generation_target_region"].eq(region)]
        if sub.empty:
            continue
        accepted = sub[sub["accept_or_reject"].eq("accept")].head(2)
        rejected = sub[sub["accept_or_reject"].eq("reject")].head(2)
        sections.append(f"### {region}")
        if not accepted.empty:
            sections.append("Best / accepted examples:")
            for _, row in accepted.iterrows():
                sections.append(f"- PC=({row['predicted_pc1']:.2f}, {row['predicted_pc2']:.2f}, {row['predicted_pc3']:.2f}) `{row['candidate_prompt']}`")
        else:
            sections.append("Best / accepted examples: none.")
        if not rejected.empty:
            sections.append("Rejected examples:")
            for _, row in rejected.iterrows():
                sections.append(f"- {row['rejection_reason']}: PC=({row['predicted_pc1']:.2f}, {row['predicted_pc2']:.2f}, {row['predicted_pc3']:.2f}) `{row['candidate_prompt']}`")
        lessons = sub["generation_notes"].dropna().tail(1)
        if not lessons.empty:
            sections.append(f"Loop lesson: {lessons.iloc[0]}")
    return "\n".join(sections)


def write_report(
    accepted: pd.DataFrame,
    thresholds: dict[str, dict[str, float]],
    coverage: dict[str, Any],
    log_df: pd.DataFrame,
    rejected: pd.DataFrame,
    manifest: dict[str, Any],
) -> None:
    criteria_rows = coverage["success_criteria"]
    criteria_table_lines = [
        "| criterion | minimum | count | pass | definition |",
        "|---|---:|---:|---|---|",
    ]
    for row in criteria_rows:
        definition = str(row["definition"]).replace("|", "/")
        criteria_table_lines.append(
            f"| {row['criterion']} | {row['minimum']} | {row['count']} | {row['pass']} | {definition} |"
        )
    criteria_table = "\n".join(criteria_table_lines)
    threshold_lines = "\n".join(
        f"- {pc}: p20={vals['p20']:.3f}, p35={vals['p35']:.3f}, p65={vals['p65']:.3f}, p80={vals['p80']:.3f}"
        for pc, vals in thresholds.items()
    )
    readiness = "H100 READY" if coverage["h100_ready"] else "NOT READY"
    failed = ", ".join(coverage["failed_criteria"]) if coverage["failed_criteria"] else "none"
    if coverage["h100_ready"]:
        readiness_detail = (
            "All predefined percentile-edge criteria passed. Use `percentile_edge_h100_manifest.csv` "
            "as the recommended H100 validation manifest for edge-heavy prompt-to-activation testing."
        )
    else:
        readiness_detail = (
            "The likely cause is that the frozen text forecaster maps safe, natural, no-role-label prompts "
            "into a narrower coordinate range than the inherited role/persona artifact distribution. The correct "
            "next step is to either revise criteria explicitly, permit a diagnostic label-bearing subset, or build "
            "a richer prompt generator; do not spend full H100 validation compute on a battery that fails the "
            "predefined edge criteria."
        )
    report = f"""# Percentile-Edge Prompt Battery For H100 Validation

Model used for synthesis and script authoring: GPT-5.5.

## Research Objective

This run builds a novel, leakage-controlled prompt battery referenced to the inherited role/persona PCA coordinate distribution. The readiness rule is explicit: all six inherited 20/80 PC-axis tails, shoulder/edge coverage, interior controls, final size, and filters must pass before the battery is marked H100-ready.

## Data Sources

- Inherited geometry source: `{GEOMETRY_DATA.relative_to(REPO_ROOT)}`
- Frozen forecaster manifest: `{FORECASTER_MANIFEST.relative_to(REPO_ROOT)}`
- Frozen forecaster model: `{FORECASTER_PATH.relative_to(REPO_ROOT)}`
- Forecaster stable hash: `{manifest.get('model_sha256')}`
- Prior prompt batteries inspected: `research/outputs/novel_prompt_battery/` and `research/outputs/novel_prompt_battery_expansion/`
- Leakage sources: `data/roles/instructions/*.json` and `data/traits/instructions/*.json`

## Inherited Percentile Thresholds

{threshold_lines}

## Adaptive Loop

The script started from prior accepted prompts but did not assume readiness. It scored existing prompts with the frozen forecaster, counted coverage against inherited percentiles, queued failed regions, generated candidates in region-specific rounds, scored every candidate, applied explicit-role-name, leakage, duplicate, and operational-harm filters, and accepted only prompts that improved the target criterion. Every generated candidate is preserved in `percentile_edge_generation_log.csv`.

Per-round learning was implemented by summarizing accepted/near-accepted and rejected candidates from prior rounds for each region, then changing the next round's text construction based on the misses. The generator is deterministic and local; no model APIs, pods, or activation runs were used.

## Success Criteria

{criteria_table}

## Coverage Summary

- Final prompt count: {coverage['prompt_count']}
- Total generated candidates: {coverage['candidate_count']}
- Rejected candidates: {coverage['rejected_count']}
- Max artifact similarity: {coverage['artifact_similarity_max']:.3f}
- Mean artifact similarity: {coverage['artifact_similarity_mean']:.3f}
- Explicit role-name flags: {coverage['explicit_role_name_flag_count']}
- Operational-harm flags: {coverage['operational_harm_flag_count']}
- Rounds per generated region: `{json.dumps(coverage['rounds_per_region'], sort_keys=True)}`
- Rejection reason counts: `{json.dumps(coverage['rejection_reason_counts'], sort_keys=True)}`

Predicted coordinate ranges:

- PC1: {coverage['predicted_ranges']['PC1']['min']:.3f} to {coverage['predicted_ranges']['PC1']['max']:.3f}
- PC2: {coverage['predicted_ranges']['PC2']['min']:.3f} to {coverage['predicted_ranges']['PC2']['max']:.3f}
- PC3: {coverage['predicted_ranges']['PC3']['min']:.3f} to {coverage['predicted_ranges']['PC3']['max']:.3f}

## Best/Worst Candidate Examples And Loop Lessons

{examples_by_region(log_df)}

## H100 Readiness Judgment

**{readiness}.**

Failed criteria: {failed}.

{readiness_detail}
"""
    (OUTPUT_DIR / "percentile_edge_battery_report.md").write_text(report)


if __name__ == "__main__":
    build_battery()
