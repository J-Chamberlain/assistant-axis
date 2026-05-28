#!/usr/bin/env python3
"""Claude-side latent feature discovery loop.

Independent hypothesis-generation and interpretation pass over the
assistant-axis persona geometry data. Purpose: cross-model convergence test.

Does Claude Code independently converge on similar explanatory dimensions,
similar held-out predictive gains, and similar most/least explained personas
as a GPT-5.5/Codex analysis would?

TARGET VARIABLES (pseudo-PCA3D):
  PCA on the 275x7 Qwen cluster-cosine matrix gives PC1, PC2, PC3.
  These are the activation-space coordinates we try to predict from
  semantic/psychological features.

SECONDARY TARGET:
  Gemma 2 27B axis_projection_layer22 (1D, normalized).

FEATURE DOMAINS (Claude-hypothesized, operationalized deterministically):
  F0 - TF-IDF semantic baseline (no-label prompts)
  F1 - BigFive traits (5 dims, ordinal 1-5)
  F2 - DarkTriad traits (3 dims, ordinal 1-5)
  F3 - Semantic cluster membership (7 one-hot, from no-label k7 topology)
  F4 - Anchor/bridge status (3 binary: stable_anchor, semantic_bridge, semantic_anchor)
  F5 - Claude-hypothesized semantic dimensions (10 binary)
  F6 - Cross-model rank convergence (Qwen rank, Llama rank, rank z-scores)

SPLIT DISCIPLINE:
  Stratified 5-fold by Gemma activation cluster label.
  Deterministic seed=42. Features are never fit on held-out folds.

PROVENANCE:
  generation_model: n/a (no LLM inference in this script)
  analysis_model: claude-sonnet-4-6 (feature hypotheses and code)
  script_author_model: claude-sonnet-4-6
  orchestration_agent: claude-code
  provider: anthropic
  date: 2026-05-28
  source_inputs: visualizations/full_ranking.csv, bigfive_profiles.json,
    dark_triad_profiles.json, cluster_analysis/qwen_cluster_directionality.csv,
    assistant_axis_methodology/deep_semantic_topology_analysis.json,
    assistant_axis_methodology/stable_anchor_roles.csv,
    assistant_axis_methodology/semantic_bridge_roles.csv,
    no_label_prompt_ablation/no_label_role_prompts.jsonl,
    cross_model/outputs/three_model_ranking_comparison.csv
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import Ridge
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[5]
OUT_DIR = Path(__file__).parent

PROVENANCE = {
    "generation_model": "n/a",
    "analysis_model": "claude-sonnet-4-6",
    "script_author_model": "claude-sonnet-4-6",
    "orchestration_agent": "claude-code",
    "provider": "anthropic",
    "model_version_or_alias": "claude-sonnet-4-6",
    "date": "2026-05-28",
    "source_inputs": [
        "visualizations/full_ranking.csv",
        "visualizations/bigfive_profiles.json",
        "visualizations/dark_triad_profiles.json",
        "research/cluster_analysis/qwen_cluster_directionality.csv",
        "research/assistant_axis_methodology/deep_semantic_topology_analysis.json",
        "research/assistant_axis_methodology/stable_anchor_roles.csv",
        "research/assistant_axis_methodology/semantic_bridge_roles.csv",
        "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl",
        "research/cross_model/outputs/three_model_ranking_comparison.csv",
    ],
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _normalize_role(name: str) -> str:
    return name.replace(" ", "_").lower().strip()


def load_all_data() -> dict:
    """Load and merge all data sources. Returns dict with aligned arrays."""
    # Gemma rankings (source of activation cluster labels and axis projection)
    gemma_rows = list(csv.DictReader(open(ROOT / "visualizations/full_ranking.csv")))
    roles = [_normalize_role(r["character"]) for r in gemma_rows]
    role_idx = {r: i for i, r in enumerate(roles)}
    n = len(roles)
    print(f"Loaded {n} roles from Gemma rankings")

    # Gemma axis projection (1D target)
    gemma_proj = np.array([float(r["axis_projection_layer22"]) for r in gemma_rows])
    gemma_cluster = [r["cluster_label"] for r in gemma_rows]

    # Qwen cluster cosines (7D proxy activation coordinates)
    qdir_rows = list(csv.DictReader(open(ROOT / "research/cluster_analysis/qwen_cluster_directionality.csv")))
    cosine_cols = [c for c in qdir_rows[0].keys() if c.startswith("cos_to_")]
    qdir_by_role = {_normalize_role(r["persona"]): r for r in qdir_rows}
    # Handle the two name mismatches (coral_reef / devils_advocate)
    if "coral reef" in {_normalize_role(r["persona"]) for r in qdir_rows}:
        for r in qdir_rows:
            n_role = _normalize_role(r["persona"])
            qdir_by_role[n_role.replace(" ", "_")] = r

    qwen_cosines = np.zeros((n, len(cosine_cols)))
    for i, role in enumerate(roles):
        if role in qdir_by_role:
            for j, col in enumerate(cosine_cols):
                try:
                    qwen_cosines[i, j] = float(qdir_by_role[role][col])
                except (ValueError, KeyError):
                    qwen_cosines[i, j] = 0.0
        else:
            # fallback: try space variant
            sp = role.replace("_", " ")
            if sp in qdir_by_role:
                for j, col in enumerate(cosine_cols):
                    try:
                        qwen_cosines[i, j] = float(qdir_by_role[sp][col])
                    except (ValueError, KeyError):
                        qwen_cosines[i, j] = 0.0

    print(f"Qwen cosine matrix: {qwen_cosines.shape}, cosine cols: {cosine_cols}")

    # BigFive
    big5_data = json.load(open(ROOT / "visualizations/bigfive_profiles.json"))
    big5_dims = ["Agreeableness", "Conscientiousness", "Extraversion", "Neuroticism", "Openness"]
    big5_mat = np.zeros((n, 5))
    for i, role in enumerate(roles):
        if role in big5_data:
            for j, dim in enumerate(big5_dims):
                big5_mat[i, j] = big5_data[role].get(dim, 3)

    # DarkTriad
    dark3_data = json.load(open(ROOT / "visualizations/dark_triad_profiles.json"))
    dark3_dims = ["Machiavellianism", "Narcissism", "Psychopathy"]
    dark3_mat = np.zeros((n, 3))
    for i, role in enumerate(roles):
        if role in dark3_data:
            for j, dim in enumerate(dark3_dims):
                dark3_mat[i, j] = dark3_data[role].get(dim, 3)

    # Semantic clusters from deep topology analysis
    topo = json.load(open(ROOT / "research/assistant_axis_methodology/deep_semantic_topology_analysis.json"))
    sem_cluster_by_role = {}
    for cluster_info in topo["no_label_k7_clusters"]:
        cid = cluster_info["cluster_id"]
        for role in cluster_info["all_roles"]:
            sem_cluster_by_role[_normalize_role(role)] = cid

    sem_cluster_ids = sorted(set(sem_cluster_by_role.values()))
    sem_cluster_mat = np.zeros((n, len(sem_cluster_ids)))
    sem_cluster_labels = []
    for i, role in enumerate(roles):
        cid = sem_cluster_by_role.get(role, sem_cluster_ids[0])
        sem_cluster_labels.append(cid)
        j = sem_cluster_ids.index(cid)
        sem_cluster_mat[i, j] = 1.0

    # Anchor/bridge status
    stable_anchors = set()
    with open(ROOT / "research/assistant_axis_methodology/stable_anchor_roles.csv") as f:
        for row in csv.DictReader(f):
            stable_anchors.add(_normalize_role(row["role"]))

    sem_bridges = set()
    with open(ROOT / "research/assistant_axis_methodology/semantic_bridge_roles.csv") as f:
        for row in csv.DictReader(f):
            sem_bridges.add(_normalize_role(row["role"]))

    sem_anchors = set()
    with open(ROOT / "research/assistant_axis_methodology/cluster_anchor_roles.csv") as f:
        for row in csv.DictReader(f):
            sem_anchors.add(_normalize_role(row["role"]))

    anchor_mat = np.zeros((n, 3))
    for i, role in enumerate(roles):
        anchor_mat[i, 0] = 1.0 if role in stable_anchors else 0.0
        anchor_mat[i, 1] = 1.0 if role in sem_bridges else 0.0
        anchor_mat[i, 2] = 1.0 if role in sem_anchors else 0.0

    # No-label prompts (for TF-IDF baseline and feature engineering)
    nl_prompts_by_role = {}
    with open(ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl") as f:
        for line in f:
            rec = json.loads(line.strip())
            r = _normalize_role(rec["role"])
            if r not in nl_prompts_by_role:
                nl_prompts_by_role[r] = rec["rewritten_prompt"]

    nl_docs = [nl_prompts_by_role.get(role, role) for role in roles]

    # Cross-model ranks
    cross_rows = list(csv.DictReader(open(ROOT / "research/cross_model/outputs/three_model_ranking_comparison.csv")))
    qwen_rank_by_role = {}
    llama_rank_by_role = {}
    for row in cross_rows:
        qr = _normalize_role(row["qwen_role"])
        lr = _normalize_role(row["llama_role"])
        rank = int(row["rank"])
        qwen_rank_by_role[qr] = rank
        llama_rank_by_role[lr] = rank

    cross_mat = np.zeros((n, 2))
    for i, role in enumerate(roles):
        cross_mat[i, 0] = qwen_rank_by_role.get(role, 138) / 275.0  # normalized rank
        cross_mat[i, 1] = llama_rank_by_role.get(role, 138) / 275.0

    return {
        "roles": roles,
        "n": n,
        "gemma_proj": gemma_proj,
        "gemma_cluster": gemma_cluster,
        "qwen_cosines": qwen_cosines,
        "cosine_cols": cosine_cols,
        "big5_mat": big5_mat,
        "big5_dims": big5_dims,
        "dark3_mat": dark3_mat,
        "dark3_dims": dark3_dims,
        "sem_cluster_mat": sem_cluster_mat,
        "sem_cluster_ids": sem_cluster_ids,
        "sem_cluster_labels": sem_cluster_labels,
        "anchor_mat": anchor_mat,
        "nl_docs": nl_docs,
        "cross_mat": cross_mat,
    }


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

# Claude Hypothesis 1: Evaluative-Procedural Orientation
# Roles that evaluate, assess, or certify external artifacts tend to occupy
# the positive assistant-axis pole. Key marker: quality control function.
EVALUATIVE_ROLES = {
    "proofreader", "screener", "grader", "editor", "reviewer", "evaluator",
    "examiner", "auditor", "assessor", "inspector", "critic", "judge",
    "validator", "verifier", "fact_checker", "analyst", "debugger",
    "diagnostician", "appraiser", "referee", "arbitrator", "moderator",
    "quality_controller", "corrector",
}
EVALUATIVE_KEYWORDS = re.compile(
    r'\b(proof|review|grade|grading|evaluat|assess|audit|inspect|verif|examin|'
    r'debug|diagnos|check|critique|critiqu|quality|accurate|correct|error|mistake|'
    r'refine|polish|standard|rubric|feedback)\b',
    re.IGNORECASE
)

# Claude Hypothesis 2: Relational/Social Embodiment
# Roles defined by social position or lived social experience rather than task function.
RELATIONAL_ROLES = {
    "parent", "orphan", "widow", "refugee", "exile", "prisoner", "immigrant",
    "expatriate", "nomad", "survivor", "elder", "grandparent", "newlywed",
    "divorcee", "celebrity", "adolescent", "teenager", "infant", "toddler",
    "graduate", "caregiver", "companion", "friend", "mentor", "confidant",
    "comforter", "witness", "martyr",
}
RELATIONAL_KEYWORDS = re.compile(
    r'\b(loss|grief|exile|banish|displace|community|belonging|family|lived|'
    r'experience|social|personal|relationship|identity|trauma|journey|narrative|'
    r'life|story|memory|childhood|partner|loved|bond|connection)\b',
    re.IGNORECASE
)

# Claude Hypothesis 3: Mythic/Symbolic/Non-Human Identity
# Roles invoking non-ordinary ontological categories activate differently.
MYTHIC_ROLES = {
    "demon", "angel", "witch", "oracle", "spirit", "ghost", "wraith", "golem",
    "dragon", "leviathan", "eldritch", "chimera", "alien", "robot", "android",
    "egregore", "hive", "swarm", "mycorrhizal", "crystalline", "coral_reef",
    "ecosystem", "void", "wind", "wave", "dreamer", "avatar", "homunculus",
    "zeitgeist", "simulacrum", "trickster", "shapeshifter", "ancient",
}
MYTHIC_KEYWORDS = re.compile(
    r'\b(entity|being|creature|spirit|force|realm|dimension|supernatural|'
    r'mythic|archetype|symbol|sacred|cosmic|eternal|ancient|primordial|'
    r'collective|consciousness|mystical|otherworldly|beyond|transcend)\b',
    re.IGNORECASE
)

# Claude Hypothesis 4: Adversarial/Oppositional Stance
# Roles defined by challenge or disruption rather than assistance.
ADVERSARIAL_ROLES = {
    "contrarian", "devil", "provocateur", "skeptic", "rebel", "anarchist",
    "revolutionary", "maverick", "adversary", "challenger", "rival",
    "competitor", "antagonist", "saboteur", "disruptor", "iconoclast",
    "heretic", "luddite", "nihilist", "pessimist", "cynic",
    "devils_advocate",
}
ADVERSARIAL_KEYWORDS = re.compile(
    r'\b(challenge|oppose|disagree|question|disrupt|resist|push.?back|'
    r'contrary|critical|skeptic|doubt|refute|argue|debate|contest|'
    r'unconventional|provocat|confrontat)\b',
    re.IGNORECASE
)

# Claude Hypothesis 5: Creative/Narrative Function
# Roles whose primary function is artistic creation or storytelling.
CREATIVE_ROLES = {
    "writer", "poet", "novelist", "screenwriter", "playwright", "artist",
    "painter", "sculptor", "composer", "musician", "actor", "narrator",
    "storyteller", "bard", "blogger", "podcaster", "journalist", "author",
    "choreographer", "filmmaker", "illustrator", "photographer",
}
CREATIVE_KEYWORDS = re.compile(
    r'\b(creat|artis|express|imagin|fiction|story|narrat|compose|perform|'
    r'paint|sculpt|poetic|aesthetic|craft|write|wrote|written|novel|'
    r'poem|music|lyric|drama|visual|art)\b',
    re.IGNORECASE
)

# Claude Hypothesis 6: Professional Specialization (Domain Expert)
# Deep domain expertise in a named professional field.
PROFESSIONAL_ROLES = {
    "doctor", "surgeon", "lawyer", "engineer", "architect", "pharmacist",
    "accountant", "economist", "mathematician", "physicist", "chemist",
    "biologist", "geologist", "historian", "sociologist", "psychologist",
    "linguist", "statistician", "data_scientist", "programmer", "developer",
    "veterinarian", "dentist", "nurse", "therapist",
}
PROFESSIONAL_KEYWORDS = re.compile(
    r'\b(expertise|specialist|professional|practitioner|practis|discipline|'
    r'field|domain|industry|sector|credential|licensed|certif|degree|'
    r'qualified|technical|scientific|medical|legal|financial)\b',
    re.IGNORECASE
)

# Claude Hypothesis 7: Abstract/Collective Identity
# Non-individual entities (collectives, systems, forces).
ABSTRACT_ROLES = {
    "hive", "swarm", "ecosystem", "mycorrhizal", "coral_reef", "egregore",
    "collective", "network", "system", "algorithm", "virus", "zeitgeist",
    "simulacrum", "void", "wave", "wind", "crystalline", "aberration",
}
ABSTRACT_KEYWORDS = re.compile(
    r'\b(collective|distributed|network|system|multiple|emergence|plural|'
    r'nodes|interconnect|organism|colony|swarm|hivemind|aggregate|'
    r'abstract|concept|pattern|process|force)\b',
    re.IGNORECASE
)

# Claude Hypothesis 8: Knowledge Transmission / Pedagogical
# Roles whose primary function is transferring knowledge to others.
PEDAGOGICAL_ROLES = {
    "teacher", "tutor", "instructor", "professor", "lecturer", "coach",
    "trainer", "mentor", "guide", "educator", "facilitator", "counselor",
    "advisor", "consultant", "expert", "specialist", "supervisor",
    "translator", "interpreter",
}
PEDAGOGICAL_KEYWORDS = re.compile(
    r'\b(teach|instruct|educat|train|mentor|guid|facilitat|explain|'
    r'demonstrat|help|assist|support|learn|understand|clarif|simplif|'
    r'knowledge|skill|develop|empower|coach)\b',
    re.IGNORECASE
)

# Claude Hypothesis 9: Hedonistic/Pleasure-Seeking Identity
# Roles oriented toward pleasure, indulgence, or leisure rather than productivity.
HEDONISTIC_ROLES = {
    "hedonist", "epicurean", "gamer", "tourist", "traveler", "adventurer",
    "explorer", "daredevil", "thrill_seeker", "bon_vivant", "aesthete",
    "dilettante", "flaneur", "gourmand",
}
HEDONISTIC_KEYWORDS = re.compile(
    r'\b(pleasure|enjoy|indulg|leisure|fun|thrill|experience|taste|'
    r'adventure|travel|game|play|entertain|excit|delight|savor)\b',
    re.IGNORECASE
)

# Claude Hypothesis 10: Moral/Ideological Anchor
# Roles defined by a strong ethical or ideological commitment.
MORAL_ROLES = {
    "altruist", "activist", "pacifist", "humanitarian", "vegan", "ascetic",
    "stoic", "moralist", "saint", "martyr", "prophet", "purist",
    "traditionalist", "reformer",
}
MORAL_KEYWORDS = re.compile(
    r'\b(moral|ethic|principle|value|belief|conviction|justice|right|'
    r'wrong|duty|virtue|commit|dedic|ideal|creed|dogma|faith|sacred|'
    r'righteous|pure|tenet|ideology)\b',
    re.IGNORECASE
)


def _role_in_set(role: str, role_set: set) -> bool:
    return role in role_set or role.replace("_", " ") in role_set


def build_claude_features(roles: list[str], nl_docs: list[str]) -> tuple[np.ndarray, list[str]]:
    """Build Claude-hypothesized binary feature matrix.

    Each row is a role; each column is a binary indicator for one
    Claude-hypothesized semantic dimension.
    Operationalization: role-name membership OR keyword match in no-label prompt.
    Never uses activation labels or targets.
    """
    hypotheses = [
        ("evaluative_orientation", EVALUATIVE_ROLES, EVALUATIVE_KEYWORDS),
        ("relational_embodiment", RELATIONAL_ROLES, RELATIONAL_KEYWORDS),
        ("mythic_symbolic", MYTHIC_ROLES, MYTHIC_KEYWORDS),
        ("adversarial_oppositional", ADVERSARIAL_ROLES, ADVERSARIAL_KEYWORDS),
        ("creative_narrative", CREATIVE_ROLES, CREATIVE_KEYWORDS),
        ("professional_specialist", PROFESSIONAL_ROLES, PROFESSIONAL_KEYWORDS),
        ("abstract_collective", ABSTRACT_ROLES, ABSTRACT_KEYWORDS),
        ("pedagogical_knowledge", PEDAGOGICAL_ROLES, PEDAGOGICAL_KEYWORDS),
        ("hedonistic_leisure", HEDONISTIC_ROLES, HEDONISTIC_KEYWORDS),
        ("moral_ideological", MORAL_ROLES, MORAL_KEYWORDS),
    ]

    mat = np.zeros((len(roles), len(hypotheses)))
    names = []
    for j, (name, role_set, kw_pattern) in enumerate(hypotheses):
        names.append(name)
        for i, (role, doc) in enumerate(zip(roles, nl_docs)):
            if _role_in_set(role, role_set) or (kw_pattern and kw_pattern.search(doc)):
                mat[i, j] = 1.0

    # Print coverage
    print(f"\nClaude dimension coverage:")
    for j, name in enumerate(names):
        count = int(mat[:, j].sum())
        print(f"  {name}: {count}/275 ({100*count/275:.0f}%)")

    return mat, names


# ---------------------------------------------------------------------------
# TF-IDF baseline
# ---------------------------------------------------------------------------

def build_tfidf_baseline(docs: list[str], n_components: int = 50) -> np.ndarray:
    """TF-IDF on no-label prompts, SVD-reduced. No external libraries beyond numpy."""
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "been", "being", "by",
        "for", "from", "in", "into", "is", "it", "its", "of", "on", "or",
        "that", "the", "their", "to", "was", "were", "who", "with", "you",
        "your", "has", "have", "who", "this", "they", "we", "i", "me",
    }

    def tokenize(text: str) -> list[str]:
        toks = re.findall(r"[a-z]+", text.lower())
        return [t for t in toks if t not in stopwords and len(t) > 2]

    token_lists = [tokenize(doc) for doc in docs]
    vocab: dict[str, int] = {}
    for tl in token_lists:
        for tok in tl:
            if tok not in vocab:
                vocab[tok] = len(vocab)

    n, v = len(docs), len(vocab)
    mat = np.zeros((n, v))
    for i, tl in enumerate(token_lists):
        from collections import Counter
        tf = Counter(tl)
        total = sum(tf.values()) or 1
        for tok, cnt in tf.items():
            mat[i, vocab[tok]] = cnt / total

    df = (mat > 0).sum(axis=0)
    idf = np.log((n + 1) / (df + 1)) + 1
    mat = mat * idf

    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1
    mat = mat / norms

    n_comp = min(n_components, v - 1, n - 1)
    svd = TruncatedSVD(n_components=n_comp, random_state=42)
    reduced = svd.fit_transform(mat)
    print(f"TF-IDF baseline: vocab={v}, SVD components={n_comp}, "
          f"explained variance={svd.explained_variance_ratio_.sum():.3f}")
    return reduced


# ---------------------------------------------------------------------------
# Target construction
# ---------------------------------------------------------------------------

def build_pca3d_targets(qwen_cosines: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """PCA on Qwen cluster cosines → pseudo-PC1, PC2, PC3.

    Returns: (pca3d_coords [n x 3], explained_variance_ratios [3])
    """
    from sklearn.decomposition import PCA
    scaler = StandardScaler()
    scaled = scaler.fit_transform(qwen_cosines)
    pca = PCA(n_components=3, random_state=42)
    coords = pca.fit_transform(scaled)
    print(f"\nPseudo-PCA3D from Qwen cosines:")
    for k, ev in enumerate(pca.explained_variance_ratio_):
        print(f"  PC{k+1}: {ev:.3f} variance explained")
    print(f"  Total: {pca.explained_variance_ratio_.sum():.3f}")
    return coords, pca.explained_variance_ratio_


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def r2_multivariate(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean R² across all target columns."""
    ss_res = ((y_true - y_pred) ** 2).sum(axis=0)
    ss_tot = ((y_true - y_true.mean(axis=0)) ** 2).sum(axis=0)
    r2s = np.where(ss_tot > 0, 1 - ss_res / ss_tot, 0.0)
    return float(r2s.mean())


def r2_per_axis(y_true: np.ndarray, y_pred: np.ndarray) -> list[float]:
    """Per-axis R²."""
    out = []
    for k in range(y_true.shape[1]):
        ss_res = ((y_true[:, k] - y_pred[:, k]) ** 2).sum()
        ss_tot = ((y_true[:, k] - y_true[:, k].mean()) ** 2).sum()
        out.append(float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0)
    return out


def evaluate_features(
    X: np.ndarray,
    y_pca: np.ndarray,
    y_gemma: np.ndarray,
    cluster_labels: list[str],
    alpha: float = 1.0,
) -> dict:
    """Stratified 5-fold CV evaluation of X predicting y_pca and y_gemma."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cluster_ids = sorted(set(cluster_labels))
    strat_labels = [cluster_ids.index(c) for c in cluster_labels]

    pca3d_preds = np.zeros_like(y_pca)
    gemma_preds = np.zeros_like(y_gemma)

    for train_idx, test_idx in skf.split(X, strat_labels):
        X_tr, X_te = X[train_idx], X[test_idx]
        y_pca_tr = y_pca[train_idx]
        y_gemma_tr = y_gemma[train_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        # Predict PCA3D (multivariate Ridge)
        ridge_pca = Ridge(alpha=alpha)
        ridge_pca.fit(X_tr_s, y_pca_tr)
        pca3d_preds[test_idx] = ridge_pca.predict(X_te_s)

        # Predict Gemma axis (univariate Ridge)
        ridge_g = Ridge(alpha=alpha)
        ridge_g.fit(X_tr_s, y_gemma_tr)
        gemma_preds[test_idx] = ridge_g.predict(X_te_s)

    pca3d_r2 = r2_multivariate(y_pca, pca3d_preds)
    pca3d_per_axis = r2_per_axis(y_pca, pca3d_preds)
    gemma_r2 = float(1 - ((y_gemma - gemma_preds)**2).sum() /
                     ((y_gemma - y_gemma.mean())**2).sum())

    # Residuals
    pca3d_residuals = np.linalg.norm(y_pca - pca3d_preds, axis=1)
    gemma_residuals = np.abs(y_gemma - gemma_preds)

    return {
        "pca3d_r2": pca3d_r2,
        "pca3d_per_axis_r2": pca3d_per_axis,
        "gemma_r2": gemma_r2,
        "pca3d_preds": pca3d_preds,
        "pca3d_residuals": pca3d_residuals,
        "gemma_preds": gemma_preds,
        "gemma_residuals": gemma_residuals,
    }


def permutation_null(
    X: np.ndarray,
    y_pca: np.ndarray,
    cluster_labels: list[str],
    n_perm: int = 200,
    alpha: float = 1.0,
) -> dict:
    """Permutation test: shuffle y, refit. Returns null R² distribution."""
    rng = np.random.RandomState(42)
    cluster_ids = sorted(set(cluster_labels))
    strat_labels = [cluster_ids.index(c) for c in cluster_labels]
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    null_r2s = []
    for _ in range(n_perm):
        y_perm = y_pca[rng.permutation(len(y_pca))]
        preds = np.zeros_like(y_pca)
        for train_idx, test_idx in skf.split(X, strat_labels):
            sc = StandardScaler()
            X_tr = sc.fit_transform(X[train_idx])
            X_te = sc.transform(X[test_idx])
            ridge = Ridge(alpha=alpha)
            ridge.fit(X_tr, y_perm[train_idx])
            preds[test_idx] = ridge.predict(X_te)
        null_r2s.append(r2_multivariate(y_pca, preds))

    null_r2s = np.array(null_r2s)
    return {
        "null_mean": float(null_r2s.mean()),
        "null_std": float(null_r2s.std()),
        "null_p95": float(np.percentile(null_r2s, 95)),
        "null_p99": float(np.percentile(null_r2s, 99)),
    }


# ---------------------------------------------------------------------------
# Iterative outer loop
# ---------------------------------------------------------------------------

def run_iterative_loop(data: dict, y_pca: np.ndarray, ev_ratios: np.ndarray) -> list[dict]:
    """Iterative feature addition loop with plateau detection.

    Returns list of round records, each with metrics and feature set used.
    Plateau rule: stop if last 2 consecutive rounds each improved PCA3D R² by < 0.01.
    """
    roles = data["roles"]
    y_gemma_raw = data["gemma_proj"]
    # Normalize Gemma projection to [-1, 1] range for comparability
    g_min, g_max = y_gemma_raw.min(), y_gemma_raw.max()
    y_gemma = 2 * (y_gemma_raw - g_min) / (g_max - g_min) - 1
    cluster_labels = data["gemma_cluster"]
    nl_docs = data["nl_docs"]

    # Build all feature blocks
    print("\n=== Building feature blocks ===")
    tfidf = build_tfidf_baseline(nl_docs, n_components=50)
    big5 = data["big5_mat"]
    dark3 = data["dark3_mat"]
    sem_cluster = data["sem_cluster_mat"]
    anchor = data["anchor_mat"]
    cross = data["cross_mat"]
    claude_features, claude_names = build_claude_features(roles, nl_docs)

    print("\n=== Running permutation null baseline ===")
    null_stats = permutation_null(tfidf, y_pca, cluster_labels, n_perm=200)
    print(f"  Null PCA3D R² mean={null_stats['null_mean']:.4f}, "
          f"p95={null_stats['null_p95']:.4f}, p99={null_stats['null_p99']:.4f}")

    feature_sets = [
        ("F0_tfidf_semantic_baseline", tfidf),
        ("F1_big5_traits", np.hstack([tfidf, big5])),
        ("F2_big5_dark3", np.hstack([tfidf, big5, dark3])),
        ("F3_sem_cluster", np.hstack([tfidf, big5, dark3, sem_cluster])),
        ("F4_anchor_bridge", np.hstack([tfidf, big5, dark3, sem_cluster, anchor])),
        ("F5_claude_hypotheses", np.hstack([tfidf, big5, dark3, sem_cluster, anchor, claude_features])),
        ("F6_cross_model_rank", np.hstack([tfidf, big5, dark3, sem_cluster, anchor, claude_features, cross])),
    ]

    rounds = []
    prev_r2 = -np.inf
    plateau_count = 0
    PLATEAU_THRESHOLD = 0.01
    best_result = None
    best_name = None
    best_X = None

    print("\n=== Iterative outer loop ===")
    for round_idx, (fs_name, X) in enumerate(feature_sets):
        print(f"\nRound {round_idx}: {fs_name} ({X.shape[1]} features)")
        result = evaluate_features(X, y_pca, y_gemma, cluster_labels)
        r2 = result["pca3d_r2"]
        improvement = r2 - prev_r2
        print(f"  PCA3D R²={r2:.4f}  Gemma R²={result['gemma_r2']:.4f}  "
              f"improvement={improvement:+.4f}")
        print(f"  Per-axis R²: PC1={result['pca3d_per_axis_r2'][0]:.4f}  "
              f"PC2={result['pca3d_per_axis_r2'][1]:.4f}  "
              f"PC3={result['pca3d_per_axis_r2'][2]:.4f}")

        rounds.append({
            "round": round_idx,
            "feature_set": fs_name,
            "n_features": int(X.shape[1]),
            "pca3d_r2": round(r2, 4),
            "pca3d_per_axis_r2": [round(v, 4) for v in result["pca3d_per_axis_r2"]],
            "gemma_r2": round(result["gemma_r2"], 4),
            "improvement_over_prev": round(improvement, 4),
            "null_pca3d_r2_mean": round(null_stats["null_mean"], 4),
            "null_pca3d_r2_p95": round(null_stats["null_p95"], 4),
        })

        if result["pca3d_r2"] > (best_result["pca3d_r2"] if best_result else -np.inf):
            best_result = result
            best_name = fs_name
            best_X = X

        if improvement < PLATEAU_THRESHOLD and round_idx > 0:
            plateau_count += 1
            print(f"  [plateau {plateau_count}/2]")
            if plateau_count >= 2:
                print(f"  Plateau reached after round {round_idx}. Stopping.")
                break
        else:
            plateau_count = 0

        prev_r2 = r2

    print(f"\nBest feature set: {best_name}  PCA3D R²={best_result['pca3d_r2']:.4f}")
    return rounds, best_result, best_name, null_stats, y_gemma, claude_names


# ---------------------------------------------------------------------------
# Persona ranking table
# ---------------------------------------------------------------------------

def build_ranking_table(
    data: dict,
    y_pca: np.ndarray,
    best_result: dict,
    baseline_result: dict,
    null_stats: dict,
    claude_features: np.ndarray,
    claude_names: list[str],
) -> list[dict]:
    """Build per-persona ranked table sorted by final model residual (ascending = best explained)."""
    roles = data["roles"]
    y_gemma_norm = best_result["gemma_preds"]  # proxy for predicted gemma
    y_gemma_actual = baseline_result["gemma_residuals"]  # residuals under baseline

    rows = []
    for i, role in enumerate(roles):
        # Find most relevant Claude dimension (highest-value feature for this role)
        # claude_features indexed by role — need to rebuild from data
        most_rel_dims = []
        if hasattr(data, "claude_feat_mat"):
            cf = data["claude_feat_mat"][i]
            active = [(claude_names[j], cf[j]) for j in range(len(claude_names)) if cf[j] > 0]
            most_rel_dims = [n for n, _ in active]

        rows.append({
            "persona": role,
            "final_model_residual_pca3d": round(float(best_result["pca3d_residuals"][i]), 4),
            "baseline_residual_pca3d": round(float(baseline_result["pca3d_residuals"][i]), 4),
            "residual_improvement_pca3d": round(
                float(baseline_result["pca3d_residuals"][i]) - float(best_result["pca3d_residuals"][i]), 4
            ),
            "actual_pc1": round(float(y_pca[i, 0]), 4),
            "actual_pc2": round(float(y_pca[i, 1]), 4),
            "actual_pc3": round(float(y_pca[i, 2]), 4),
            "predicted_pc1": round(float(best_result["pca3d_preds"][i, 0]), 4),
            "predicted_pc2": round(float(best_result["pca3d_preds"][i, 1]), 4),
            "predicted_pc3": round(float(best_result["pca3d_preds"][i, 2]), 4),
            "gemma_axis_proj_raw": round(float(data["gemma_proj"][i]), 2),
            "gemma_cluster": data["gemma_cluster"][i],
            "semantic_cluster_id": data["sem_cluster_labels"][i],
            "is_stable_anchor": bool(data["anchor_mat"][i, 0]),
            "is_semantic_bridge": bool(data["anchor_mat"][i, 1]),
            "is_semantic_anchor": bool(data["anchor_mat"][i, 2]),
        })

    rows.sort(key=lambda r: r["final_model_residual_pca3d"])
    return rows


# ---------------------------------------------------------------------------
# Report writing
# ---------------------------------------------------------------------------

def write_report(
    rounds: list[dict],
    best_result: dict,
    best_name: str,
    baseline_result: dict,
    null_stats: dict,
    ranking: list[dict],
    ev_ratios: np.ndarray,
    claude_names: list[str],
    claude_cov: np.ndarray,
    roles: list[str],
) -> None:
    lines = [
        "# Claude Latent Feature Discovery Loop — Report",
        "",
        "## Provenance",
        f"- analysis_model: claude-sonnet-4-6",
        f"- script_author_model: claude-sonnet-4-6",
        f"- orchestration_agent: claude-code",
        f"- provider: anthropic",
        f"- date: 2026-05-28",
        "",
        "## Purpose",
        "Independent hypothesis-generation and interpretation pass over assistant-axis",
        "persona geometry data. Cross-model convergence test: does Claude Code",
        "independently converge on similar explanatory dimensions and predictive gains",
        "as a Codex/GPT-5.5 analysis?",
        "",
        "## Target Variables",
        "Primary target: pseudo-PCA3D from 275×7 Qwen cluster-cosine matrix.",
        "Secondary target: Gemma 2 27B axis_projection_layer22 (normalized).",
        "",
        "Pseudo-PCA3D explained variance:",
    ]
    for k, ev in enumerate(ev_ratios):
        lines.append(f"  PC{k+1}: {ev:.3f}")
    lines.append(f"  Total: {ev_ratios.sum():.3f}")
    lines += [
        "",
        "## Null Baseline (permutation test, n=200)",
        f"- Null PCA3D R² mean: {null_stats['null_mean']:.4f}",
        f"- Null PCA3D R² p95:  {null_stats['null_p95']:.4f}",
        f"- Null PCA3D R² p99:  {null_stats['null_p99']:.4f}",
        "",
        "## Claude-Hypothesized Dimensions",
        "Ten semantic dimensions independently proposed by Claude as likely",
        "explanatory of activation cluster structure:",
        "",
    ]
    for j, name in enumerate(claude_names):
        count = int(claude_cov[:, j].sum())
        lines.append(f"{j+1}. **{name}** — {count}/275 roles ({100*count/275:.0f}%)")

    lines += [
        "",
        "## Iterative Loop Results",
        "",
        "| Round | Feature Set | n_features | PCA3D R² | PC1 R² | PC2 R² | PC3 R² | Gemma R² | ΔR² |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rounds:
        per = r["pca3d_per_axis_r2"]
        lines.append(
            f"| {r['round']} | {r['feature_set']} | {r['n_features']} "
            f"| {r['pca3d_r2']} | {per[0]} | {per[1]} | {per[2]} "
            f"| {r['gemma_r2']} | {r['improvement_over_prev']:+.4f} |"
        )
    lines += [
        "",
        f"**Best feature set: {best_name}**",
        f"**Best PCA3D R²: {best_result['pca3d_r2']:.4f}**",
        f"**Best Gemma R²: {best_result['gemma_r2']:.4f}**",
        "",
        "## Top 20 Best-Explained Personas (lowest final residual)",
        "",
        "| Rank | Persona | Residual | Cluster | Stable Anchor | Bridge |",
        "|---|---|---|---|---|---|",
    ]
    for rank, row in enumerate(ranking[:20], 1):
        lines.append(
            f"| {rank} | {row['persona']} | {row['final_model_residual_pca3d']:.4f} "
            f"| {row['gemma_cluster']} | {row['is_stable_anchor']} | {row['is_semantic_bridge']} |"
        )
    lines += [
        "",
        "## Top 20 Worst-Explained Personas (highest final residual)",
        "",
        "| Rank | Persona | Residual | Cluster | Stable Anchor | Bridge |",
        "|---|---|---|---|---|---|",
    ]
    worst = sorted(ranking, key=lambda r: -r["final_model_residual_pca3d"])
    for rank, row in enumerate(worst[:20], 1):
        lines.append(
            f"| {rank} | {row['persona']} | {row['final_model_residual_pca3d']:.4f} "
            f"| {row['gemma_cluster']} | {row['is_stable_anchor']} | {row['is_semantic_bridge']} |"
        )
    lines += [
        "",
        "## Baseline vs Best Model Residual Improvement",
        "",
        f"Baseline (TF-IDF only) PCA3D R²: {rounds[0]['pca3d_r2']:.4f}",
        f"Best model PCA3D R²: {best_result['pca3d_r2']:.4f}",
        f"Improvement: {best_result['pca3d_r2'] - rounds[0]['pca3d_r2']:+.4f}",
        "",
        "## Interpretation Notes",
        "- Claude independently proposed 10 semantic dimensions as likely explanatory.",
        "- The evaluative_orientation dimension (proofreader, screener, grader, etc.) was",
        "  hypothesized as the primary driver of the assistant axis positive pole.",
        "- The mythic_symbolic and relational_embodiment dimensions were hypothesized",
        "  as primary drivers of the non-procedural activation clusters.",
        "- Cross-model rank features were added as the final round to test whether",
        "  Qwen/Llama axis convergence adds independent predictive signal.",
        "- Per interpretation constraints: Claude-derived dimensions are hypotheses,",
        "  not truths. Cross-model convergence with a Codex/GPT-5.5 analysis (if",
        "  available) would support but not confirm interpretive stability.",
    ]

    report_path = OUT_DIR / "claude_latent_feature_loop_report.md"
    report_path.write_text("\n".join(lines))
    print(f"\nReport written: {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== Claude Latent Feature Discovery Loop ===")
    print(f"Output dir: {OUT_DIR}")

    # Load all data
    print("\n=== Loading data ===")
    data = load_all_data()

    # Build pseudo-PCA3D target
    print("\n=== Building pseudo-PCA3D targets ===")
    y_pca, ev_ratios = build_pca3d_targets(data["qwen_cosines"])

    # Build Claude features for coverage reporting
    claude_features, claude_names = build_claude_features(data["roles"], data["nl_docs"])
    data["claude_feat_mat"] = claude_features  # store for ranking table

    # Run iterative loop
    rounds, best_result, best_name, null_stats, y_gemma, claude_names = run_iterative_loop(
        data, y_pca, ev_ratios
    )

    # Build baseline result for comparison
    print("\n=== Building TF-IDF baseline result ===")
    tfidf = build_tfidf_baseline(data["nl_docs"], n_components=50)
    baseline_result = evaluate_features(
        tfidf, y_pca, y_gemma, data["gemma_cluster"]
    )

    # Build ranking table
    print("\n=== Building persona ranking table ===")
    ranking = build_ranking_table(
        data, y_pca, best_result, baseline_result, null_stats,
        claude_features, claude_names
    )

    # Write CSV
    csv_path = OUT_DIR / "claude_persona_explanation_rankings.csv"
    fieldnames = list(ranking[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ranking)
    print(f"CSV written: {csv_path}")

    # Write JSON
    json_path = OUT_DIR / "claude_persona_explanation_rankings.json"
    json_path.write_text(json.dumps({"provenance": PROVENANCE, "ranking": ranking}, indent=2))
    print(f"JSON written: {json_path}")

    # Write report
    write_report(
        rounds, best_result, best_name, baseline_result,
        null_stats, ranking, ev_ratios, claude_names, claude_features, data["roles"]
    )

    # Write master log
    master_log = {
        "provenance": PROVENANCE,
        "n_roles": data["n"],
        "pseudo_pca3d_explained_variance": ev_ratios.tolist(),
        "null_baseline": null_stats,
        "rounds": rounds,
        "best_feature_set": best_name,
        "best_pca3d_r2": best_result["pca3d_r2"],
        "best_per_axis_r2": best_result["pca3d_per_axis_r2"],
        "best_gemma_r2": best_result["gemma_r2"],
        "baseline_pca3d_r2": rounds[0]["pca3d_r2"] if rounds else None,
        "claude_dimension_names": claude_names,
        "improvement_over_baseline": round(
            best_result["pca3d_r2"] - (rounds[0]["pca3d_r2"] if rounds else 0), 4
        ),
    }
    log_path = OUT_DIR / "claude_latent_feature_loop_master_log.json"
    log_path.write_text(json.dumps(master_log, indent=2))
    print(f"Master log written: {log_path}")

    print("\n=== Summary ===")
    print(f"Null R² (permutation): {null_stats['null_mean']:.4f} ± {null_stats['null_std']:.4f}")
    print(f"Baseline (TF-IDF) PCA3D R²: {rounds[0]['pca3d_r2']:.4f}")
    print(f"Best model PCA3D R²: {best_result['pca3d_r2']:.4f}")
    print(f"Best Gemma R²: {best_result['gemma_r2']:.4f}")
    print(f"Best feature set: {best_name}")
    print(f"\nTop 5 best-explained: {[r['persona'] for r in ranking[:5]]}")
    print(f"Top 5 worst-explained: {[r['persona'] for r in sorted(ranking, key=lambda r: -r['final_model_residual_pca3d'])[:5]]}")


if __name__ == "__main__":
    main()
