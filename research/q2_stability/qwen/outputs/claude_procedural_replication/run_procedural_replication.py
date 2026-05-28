"""
Claude Procedural Replication Loop

Goal: Force Claude to independently discover and optimize procedural/operating-mode
explanatory structure for canonical activation PCA geometry, constrained to an
operating-mode ontology only (no Big Five or personality-trait labels).

Constraint: Only 20 allowed procedural dimensions as the search space.
Baseline: semantic cluster one-hot features (same as shared benchmark).
Target: canonical activation PCA3D (same as shared benchmark).
Splits: same 5 deterministic Codex outer-loop splits.

Codex benchmark to beat: mean PCA3D R²=0.490 (31 behavioral/motivational dims).
BigFive benchmark (ceiling reference): mean PCA3D R²=0.613.
"""

import json
import csv
import re
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import os

# ─── PATHS ────────────────────────────────────────────────────────────────────
REPO = os.path.dirname(os.path.abspath(__file__)).rstrip("/")
while not os.path.exists(os.path.join(REPO, "research")):
    REPO = os.path.dirname(REPO)

NO_LABEL_PROMPTS = os.path.join(
    REPO,
    "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl",
)
CANONICAL_PCA = os.path.join(
    REPO,
    "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv",
)
SEMANTIC_BASELINE = os.path.join(
    REPO,
    "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/semantic_baseline_features.csv",
)
SPLIT_ASSIGNMENTS = os.path.join(
    REPO,
    "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv",
)
BIGFIVE_FEATURES = os.path.join(
    REPO,
    "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv",
)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── PROCEDURAL DIMENSION DEFINITIONS ────────────────────────────────────────
# Each dimension: list of keyword patterns (case-insensitive, word-boundary matched)
# Score = number of distinct pattern families matched (0-3) across all 5 no-label prompts
PROCEDURAL_DIMENSIONS = {
    "evaluation": [
        r"\b(evaluat|assess|judg|verif|screen|review|grade|audit|inspect|check|test|measur|examin|score|rat|apprais)\w*",
        r"\b(quality|standard|criterion|criteria|benchmark|threshold|pass|fail|correctness|accuracy)\w*",
        r"\b(critique|feedback|diagnos|detect|identif)\w*",
    ],
    "mediation": [
        r"\b(mediat|arbitrat|negotiat|facilitat|broker|reconcil|resolv|settl|adjudicat)\w*",
        r"\b(bridg|connect|link|intermediar|neutral|impartial|balanced|compromise)\w*",
        r"\b(peac|conflict.resol|disput|tension|between.parties|both.sides)\w*",
    ],
    "destabilization": [
        r"\b(destabiliz|disrupt|challeng|undermin|provok|overturn|subvert|erode|weaken)\w*",
        r"\b(question|interrogat|contradict|confront|refus|reject|push.back)\w*",
        r"\b(chaos|disorder|upend|unsettle|shock|jolt|disturb|perturb)\w*",
    ],
    "protection": [
        r"\b(protect|guard|defend|shield|safeguard|preserv|secur|watch.over)\w*",
        r"\b(prevent|ward.off|keep.safe|patrol|surveil|monitor.for.threats)\w*",
        r"\b(loyalt|duty.to.protect|respons.for.safety|unwavering.commit)\w*",
    ],
    "witnessing": [
        r"\b(witness|observ|watch|perceiv|attend|notice|pay.attention|be.present)\w*",
        r"\b(testif|record.what.happens|document.events|bear.witness|register)\w*",
        r"\b(see|look|gaz|spectat|audit)\w*",
    ],
    "archiving": [
        r"\b(archiv|catalog|record|preserv|stor|collect|maintain.records|log)\w*",
        r"\b(document|index|curate|compil|gather|assembl|organiz.data)\w*",
        r"\b(histor|memor|register|ledger|repository|librarl|inventori)\w*",
    ],
    "manipulation": [
        r"\b(manipulat|decei|scheme|trick|exploit|misdirect|gaslight|mislead)\w*",
        r"\b(ulterior|hidden.agenda|puppet|control.from.behind|pull.strings)\w*",
        r"\b(seduc|lure|ensnare|entrap|corrupts|twist)\w*",
    ],
    "persuasion": [
        r"\b(persuad|convinc|advocat|argu|debat|influenc|sway|lobby|pitch)\w*",
        r"\b(rhetoric|appeal|compel.others|change.minds|seek.agreement|win.over)\w*",
        r"\b(negotiat|diplomac|sell|pitch|champion|campaign.for)\w*",
    ],
    "care": [
        r"\b(care|nurt|support|heal|comfort|console|compassion|empathi|tenderness)\w*",
        r"\b(help|assist|aid|serve|tend.to|look.after|foster|protect.wellbeing)\w*",
        r"\b(welfare|wellbeing|well-being|therapeutic|caregiv|counsel|sooth)\w*",
    ],
    "enforcement": [
        r"\b(enforc|rule|command|control|discipline|regulat|punish|polic|comply)\w*",
        r"\b(law|order|obligat|mandate|prohibit|sanction|penalt|authorit|jurisdict)\w*",
        r"\b(obedience|hierarchy|ranks|chain.of.command|uphold|bound.by)\w*",
    ],
    "translation": [
        r"\b(translat|interpret|convey|communicat|transmit|relay|render)\w*",
        r"\b(bridge.language|cross-cultural|mediator.between|explai|clarif|decod)\w*",
        r"\b(meaning|signal|message|concept|understand.between|make.clear)\w*",
    ],
    "ritualization": [
        r"\b(ritual|ceremoni|sacr|symbol|rite|traditi|consecrat|sanctif)\w*",
        r"\b(pattern|repeating|observance|custom|habit|routin|protocol)\w*",
        r"\b(mark|commemorat|celebrat|solemn|spiritual.practice|honor)\w*",
    ],
    "exposure": [
        r"\b(expos|reveal|uncover|disclos|unmask|publish|broadcast|dissemin)\w*",
        r"\b(bring.to.light|lay.bare|show.the.truth|speak.out|whistleblow|report)\w*",
        r"\b(truth-telling|transparency|openness|surfac|make.known|spread.awareness)\w*",
    ],
    "coordination": [
        r"\b(coordinat|organiz|manag|plan|schedul|direct|orchestrat|align)\w*",
        r"\b(synchroniz|collaborat|team|integrat|assembl|deploy|dispatch)\w*",
        r"\b(logistics|oversight|workflow|resource.allocation|prioritiz)\w*",
    ],
    "optimization": [
        r"\b(optimiz|improv|streamlin|efficien|productiv|maximiz|perfect|refin)\w*",
        r"\b(enhance|better|best.possible|fine-tun|calibrat|tight|sharpen)\w*",
        r"\b(performance|output|throughput|eliminating.waste|continu.improvement)\w*",
    ],
    "disruption": [
        r"\b(disrupt|interrupt|break|overthrow|subvert|destroy.norms|demolish)\w*",
        r"\b(revolutionary|upheav|overturn|radical.change|shake.up|transgress)\w*",
        r"\b(norm-breaking|status.quo|convention|challenge.existing|iconoclast)\w*",
    ],
    "guidance": [
        r"\b(guid|mentor|teach|coach|advis|lead|instruct|educate|tutor)\w*",
        r"\b(show.the.way|model.behavior|exemplif|develop|cultivat|nurtur.growth)\w*",
        r"\b(wisdom|insight|lesson|demonstrat|help.others.understand|scaffold)\w*",
    ],
    "coercion": [
        r"\b(coerc|forc|compel|threaten|intimidat|dominat|subjugat|overpower)\w*",
        r"\b(must|shall|demand|insist|pressure|bully|impose|command|ultimatum)\w*",
        r"\b(no.choice|obey|comply.or|submission|subordinat|forced.to)\w*",
    ],
    "containment": [
        r"\b(contain|restrain|limit|restrict|confine|bound|manage.within|suppress)\w*",
        r"\b(keep.under.control|prevent.spread|quarantin|isolat|fence|enclos)\w*",
        r"\b(stability|stabiliz|de-escalat|reduce.threat|dampen|moderate)\w*",
    ],
    "repair": [
        r"\b(repair|restor|heal|fix|mend|recover|rehabilitat|reconstruct)\w*",
        r"\b(reconcil|rebuild|reconnect|make.amends|apolog|redress|compensat)\w*",
        r"\b(resolve.damage|restore.trust|overcome.harm|undo|correct.past)\w*",
    ],
}

N_PATTERNS = 3  # patterns per dimension; score = # matched (0-3)
RIDGE_ALPHA = 1.0  # default, overridden by kfold alpha search
ALPHAS = [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]  # same as shared benchmark
PLATEAU_THRESHOLD = 0.01
CODEX_PROCEDURAL_R2 = 0.490  # benchmark to compare against


# ─── LOAD DATA ────────────────────────────────────────────────────────────────

def norm(s):
    return s.replace(" ", "_").lower().strip()


def load_no_label_prompts():
    """Return dict: role_normalized -> concatenated text of all 5 no-label prompts."""
    role_texts = defaultdict(list)
    with open(NO_LABEL_PROMPTS) as f:
        for line in f:
            d = json.loads(line.strip())
            role_texts[norm(d["role"])].append(d["rewritten_prompt"])
    return {role: " ".join(texts) for role, texts in role_texts.items()}


def load_canonical_targets():
    """Return dict: persona -> (pc1, pc2, pc3, cluster)."""
    targets = {}
    with open(CANONICAL_PCA) as f:
        for row in csv.DictReader(f):
            targets[row["persona"]] = (
                float(row["activation_pc1"]),
                float(row["activation_pc2"]),
                float(row["activation_pc3"]),
                row["activation_cluster"],
            )
    return targets


def load_semantic_baseline():
    """Return dict: persona -> feature_dict (21 one-hot cluster cols)."""
    feats = {}
    with open(SEMANTIC_BASELINE) as f:
        reader = csv.DictReader(f)
        feat_cols = [c for c in reader.fieldnames if c not in ("persona", "provenance_manifest", "feature_set")]
        for row in reader:
            feats[row["persona"]] = {c: float(row[c]) for c in feat_cols}
    return feats, feat_cols


def load_splits():
    """Return dict: split_id(int) -> {persona: 'train'|'heldout'}."""
    splits = defaultdict(dict)
    with open(SPLIT_ASSIGNMENTS) as f:
        for row in csv.DictReader(f):
            if row["in_common_benchmark"] == "True":
                splits[int(row["canonical_split_id"])][row["persona"]] = row["canonical_assignment"]
    return splits


def load_bigfive():
    """Return dict: persona -> {big5_col: float}."""
    feats = {}
    with open(BIGFIVE_FEATURES) as f:
        reader = csv.DictReader(f)
        bf_cols = [c for c in reader.fieldnames if c.startswith("big5_")]
        for row in reader:
            feats[row["persona"]] = {c: float(row[c]) for c in bf_cols}
    return feats, bf_cols


# ─── SCORE PROCEDURAL DIMENSIONS ──────────────────────────────────────────────

def score_dimension(text: str, patterns: list) -> float:
    """Score a role's text against a dimension's patterns. Returns 0-3 (count matched)."""
    score = 0
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            score += 1
    return float(score)


def build_procedural_features(personas, no_label_texts, dim_subset):
    """
    Build feature matrix for given personas and dimension subset.
    Returns dict: persona -> {dim_name: score}.
    """
    features = {}
    for persona in personas:
        text = no_label_texts.get(persona, "")
        features[persona] = {
            dim: score_dimension(text, PROCEDURAL_DIMENSIONS[dim])
            for dim in dim_subset
        }
    return features


# ─── EVALUATION ───────────────────────────────────────────────────────────────

def make_feature_matrix(personas, feature_dicts, col_names):
    """Build np array from list of feature_dicts using col_names ordering."""
    X = np.array(
        [[feat_dicts[col] for col in col_names] for feat_dicts in
         [feature_dicts[p] for p in personas]],
        dtype=float,
    )
    return X


def standardize(train: np.ndarray, test: np.ndarray):
    """Match shared benchmark standardization exactly."""
    mean = train.mean(axis=0, keepdims=True)
    std = train.std(axis=0, keepdims=True)
    std[std < 1e-9] = 1.0
    return (train - mean) / std, (test - mean) / std


def ridge_fit(X: np.ndarray, Y: np.ndarray, alpha: float) -> np.ndarray:
    """Match shared benchmark ridge exactly (adds bias, uses pinv)."""
    Xi = np.c_[np.ones(len(X)), X]
    reg = alpha * np.eye(Xi.shape[1])
    reg[0, 0] = 0.0
    return np.linalg.pinv(Xi.T @ Xi + reg) @ Xi.T @ Y


def ridge_predict(X: np.ndarray, coef: np.ndarray) -> np.ndarray:
    return np.c_[np.ones(len(X)), X] @ coef


def joint_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Joint multi-output R² (same as shared benchmark r2())."""
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean(axis=0, keepdims=True)) ** 2).sum())
    return 0.0 if ss_tot < 1e-12 else 1.0 - ss_res / ss_tot


def per_axis_r2(y_true: np.ndarray, y_pred: np.ndarray) -> list:
    """Per-axis R² using joint metric per column."""
    return [joint_r2(y_true[:, i:i+1], y_pred[:, i:i+1]) for i in range(3)]


def kfold_alpha(X_train: np.ndarray, Y_train: np.ndarray, alphas=ALPHAS) -> float:
    """Select best alpha by 5-fold CV on training data."""
    n = len(X_train)
    folds = [np.arange(i, n, 5) for i in range(5)]
    best_alpha, best_score = alphas[0], -1e9
    for alpha in alphas:
        scores = []
        for val_idx in folds:
            val_set = set(val_idx.tolist())
            tr_idx = np.array([i for i in range(n) if i not in val_set])
            xt, xv = standardize(X_train[tr_idx], X_train[val_idx])
            coef = ridge_fit(xt, Y_train[tr_idx], alpha)
            scores.append(joint_r2(Y_train[val_idx], ridge_predict(xv, coef)))
        score = float(np.mean(scores))
        if score > best_score:
            best_alpha, best_score = alpha, score
    return best_alpha


def r2_score(y_true, y_pred):
    """Kept for compatibility; use joint_r2 for shared benchmark alignment."""
    return joint_r2(y_true, y_pred)


def evaluate_features_on_splits(personas_list, X, Y, splits):
    """
    Evaluate using exact shared benchmark evaluation protocol:
    - kfold alpha selection on training data
    - joint multi-output R² (not mean-per-axis)
    - custom standardize + ridge_fit with bias term
    """
    personas_idx = {p: i for i, p in enumerate(personas_list)}
    split_results = []

    for split_id in range(5):
        split_map = splits[split_id]
        train_personas = [p for p in personas_list if split_map.get(p) == "train"]
        test_personas = [p for p in personas_list if split_map.get(p) == "heldout"]

        if not train_personas or not test_personas:
            continue

        train_idx = [personas_idx[p] for p in train_personas]
        test_idx = [personas_idx[p] for p in test_personas]

        X_train, X_test = X[train_idx], X[test_idx]
        Y_train, Y_test = Y[train_idx], Y[test_idx]

        alpha = kfold_alpha(X_train, Y_train)
        X_train_s, X_test_s = standardize(X_train, X_test)
        coef = ridge_fit(X_train_s, Y_train, alpha)
        Y_pred = ridge_predict(X_test_s, coef)

        pca3d_r2 = joint_r2(Y_test, Y_pred)
        axis_r2 = per_axis_r2(Y_test, Y_pred)
        residuals = np.linalg.norm(Y_test - Y_pred, axis=1)
        mean_residual = float(np.mean(residuals))

        split_results.append({
            "split_id": split_id,
            "pca3d_r2": pca3d_r2,
            "per_axis_r2": axis_r2,
            "mean_residual": mean_residual,
            "selected_alpha": alpha,
            "n_train": len(train_personas),
            "n_test": len(test_personas),
            "test_personas": test_personas,
            "y_test": Y_test.tolist(),
            "y_pred": Y_pred.tolist(),
        })

    mean_r2 = float(np.mean([s["pca3d_r2"] for s in split_results]))
    mean_per_axis = [
        float(np.mean([s["per_axis_r2"][i] for s in split_results]))
        for i in range(3)
    ]
    mean_residual = float(np.mean([s["mean_residual"] for s in split_results]))

    return {
        "mean_pca3d_r2": mean_r2,
        "mean_per_axis_r2": mean_per_axis,
        "mean_residual": mean_residual,
        "split_results": split_results,
    }


# ─── ITERATIVE LOOP ───────────────────────────────────────────────────────────

def run_iterative_loop(personas_list, canonical_pca_targets, semantic_feats, semantic_cols,
                       splits, no_label_texts):
    """
    Iterative procedural dimension search.
    Starts with semantic baseline, then adds procedural bundles.
    Retains a bundle if mean PCA3D R² improves by > PLATEAU_THRESHOLD.
    Stops after 2 consecutive non-improving iterations.
    """

    # Build target matrix
    Y = np.array([
        [canonical_pca_targets[p][0], canonical_pca_targets[p][1], canonical_pca_targets[p][2]]
        for p in personas_list
    ], dtype=float)

    # All 20 procedural dimensions
    all_dims = list(PROCEDURAL_DIMENSIONS.keys())

    # Build all procedural scores upfront
    all_proc_features = build_procedural_features(personas_list, no_label_texts, all_dims)

    # Baseline: semantic cluster one-hot features only
    print("Evaluating semantic baseline...")
    X_baseline = make_feature_matrix(
        personas_list,
        {p: semantic_feats[p] for p in personas_list},
        semantic_cols
    )
    baseline_result = evaluate_features_on_splits(personas_list, X_baseline, Y, splits)
    print(f"  Semantic baseline mean R²: {baseline_result['mean_pca3d_r2']:.4f}")

    # Define dimension bundles for iterative addition
    # Each bundle groups related procedural modes
    dim_bundles = [
        # Round 1: core operating modes (high prior coverage in activation literature)
        {
            "name": "F1_eval_guide_care",
            "dims": ["evaluation", "guidance", "care"],
            "rationale": "Evaluation (judge/verify), guidance (teach/mentor), care (support/heal) — the positive-service procedural triad. Hypothesized to explain editorial and grounded_social clusters."
        },
        # Round 2: authority and enforcement modes
        {
            "name": "F2_enforce_coordinate_optimize",
            "dims": ["enforcement", "coordination", "optimization"],
            "rationale": "Enforcement (rule/police), coordination (organize/plan), optimization (improve/efficiency) — the procedural-professional operating cluster."
        },
        # Round 3: destabilizing and disruptive modes
        {
            "name": "F3_destab_disrupt_coerce",
            "dims": ["destabilization", "disruption", "coercion"],
            "rationale": "Destabilization (challenge/undermine), disruption (break/overturn), coercion (force/threaten) — the combative/iconoclast and trickster clusters."
        },
        # Round 4: communication and bridging modes
        {
            "name": "F4_persuade_translate_expose",
            "dims": ["persuasion", "translation", "exposure"],
            "rationale": "Persuasion (argue/influence), translation (bridge/interpret), exposure (reveal/disclose) — communicative and activist operating modes."
        },
        # Round 5: relational and boundary modes
        {
            "name": "F5_protect_contain_repair",
            "dims": ["protection", "containment", "repair"],
            "rationale": "Protection (guard/shield), containment (restrain/limit), repair (restore/heal) — boundary maintenance and restorative operating modes."
        },
        # Round 6: symbolic and observational modes
        {
            "name": "F6_witness_archive_ritualize",
            "dims": ["witnessing", "archiving", "ritualization"],
            "rationale": "Witnessing (observe/testify), archiving (record/catalog), ritualization (ceremony/symbol) — mythic_spiritual and editorial archive modes."
        },
        # Round 7: manipulation and adversarial modes
        {
            "name": "F7_manipulate_mediate",
            "dims": ["manipulation", "mediation"],
            "rationale": "Manipulation (deceive/exploit) and mediation (arbitrate/bridge) — the high-ambiguity procedural dyad that spans trickster and mediator archetypes."
        },
    ]

    retained_dims = []
    retained_cols = list(semantic_cols)
    retained_X = X_baseline.copy()
    best_r2 = baseline_result["mean_pca3d_r2"]
    consecutive_non_improving = 0
    iteration_log = []

    for bundle in dim_bundles:
        if consecutive_non_improving >= 2:
            print(f"\nPlateau triggered after {len(iteration_log)} iterations (2 consecutive non-improving).")
            break

        bundle_dims = bundle["dims"]
        bundle_name = bundle["name"]

        # Build trial feature matrix: retained + new bundle
        trial_proc_cols = bundle_dims
        trial_proc = np.array(
            [[all_proc_features[p][d] for d in trial_proc_cols] for p in personas_list],
            dtype=float
        )
        X_trial = np.hstack([retained_X, trial_proc])

        print(f"\nIteration {len(iteration_log)+1}: testing bundle '{bundle_name}' ({bundle_dims})")
        trial_result = evaluate_features_on_splits(personas_list, X_trial, Y, splits)
        delta = trial_result["mean_pca3d_r2"] - best_r2
        print(f"  R²={trial_result['mean_pca3d_r2']:.4f}, delta={delta:+.4f} (vs Codex={CODEX_PROCEDURAL_R2})")

        decision = "retained" if delta > PLATEAU_THRESHOLD else "discarded"
        print(f"  Decision: {decision}")

        iter_entry = {
            "iteration": len(iteration_log) + 1,
            "bundle_name": bundle_name,
            "bundle_dims": bundle_dims,
            "rationale": bundle["rationale"],
            "mean_pca3d_r2": trial_result["mean_pca3d_r2"],
            "delta_vs_prior": delta,
            "mean_per_axis_r2": trial_result["mean_per_axis_r2"],
            "mean_residual": trial_result["mean_residual"],
            "codex_procedural_r2": CODEX_PROCEDURAL_R2,
            "delta_vs_codex": trial_result["mean_pca3d_r2"] - CODEX_PROCEDURAL_R2,
            "decision": decision,
            "retained_dims_after": list(retained_dims + (bundle_dims if decision == "retained" else [])),
        }

        if decision == "retained":
            retained_dims.extend(bundle_dims)
            retained_cols.extend(bundle_dims)
            retained_X = X_trial
            best_r2 = trial_result["mean_pca3d_r2"]
            consecutive_non_improving = 0
        else:
            consecutive_non_improving += 1

        iteration_log.append(iter_entry)

    # Final evaluation on retained features
    print(f"\n=== FINAL MODEL: {len(retained_dims)} procedural dims retained ===")
    final_result = evaluate_features_on_splits(personas_list, retained_X, Y, splits)
    print(f"Final mean R²: {final_result['mean_pca3d_r2']:.4f}")
    print(f"Per-axis: PC1={final_result['mean_per_axis_r2'][0]:.3f}, PC2={final_result['mean_per_axis_r2'][1]:.3f}, PC3={final_result['mean_per_axis_r2'][2]:.3f}")
    print(f"Codex procedural benchmark: {CODEX_PROCEDURAL_R2:.3f}")
    print(f"Delta vs Codex: {final_result['mean_pca3d_r2'] - CODEX_PROCEDURAL_R2:+.3f}")

    return {
        "baseline_result": baseline_result,
        "iteration_log": iteration_log,
        "final_result": final_result,
        "retained_dims": retained_dims,
        "final_r2": final_result["mean_pca3d_r2"],
        "codex_r2": CODEX_PROCEDURAL_R2,
        "Y": Y,
        "retained_X": retained_X,
        "personas_list": personas_list,
    }


# ─── PERSONA RESIDUAL ANALYSIS ────────────────────────────────────────────────

def build_persona_residuals(personas_list, Y, final_X, final_result, clusters):
    """Compute per-persona mean residual across held-out appearances."""
    per_persona_residuals = defaultdict(list)

    for split in final_result["split_results"]:
        test_personas = split["test_personas"]
        y_test = np.array(split["y_test"])
        y_pred = np.array(split["y_pred"])
        residuals = np.linalg.norm(y_test - y_pred, axis=1)
        for p, r in zip(test_personas, residuals):
            per_persona_residuals[p].append(r)

    summary = []
    for p in personas_list:
        resids = per_persona_residuals.get(p, [])
        if resids:
            summary.append({
                "persona": p,
                "mean_residual": float(np.mean(resids)),
                "n_heldout": len(resids),
                "activation_cluster": clusters.get(p, "unknown"),
            })

    return sorted(summary, key=lambda x: x["mean_residual"])


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    no_label_texts = load_no_label_prompts()
    targets = load_canonical_targets()
    semantic_feats, semantic_cols = load_semantic_baseline()
    splits = load_splits()

    # Common personas (benchmark intersection)
    personas_list = sorted(targets.keys())
    print(f"Benchmark personas: {len(personas_list)}")

    # Filter to personas with semantic features
    personas_list = [p for p in personas_list if p in semantic_feats]
    print(f"After semantic feature filter: {len(personas_list)}")

    # Extract clusters for residual analysis
    clusters = {p: targets[p][3] for p in personas_list}

    # Run the iterative loop
    loop_result = run_iterative_loop(
        personas_list, targets, semantic_feats, semantic_cols, splits, no_label_texts
    )

    # Build persona residual rankings
    residual_rankings = build_persona_residuals(
        personas_list, loop_result["Y"], loop_result["retained_X"],
        loop_result["final_result"], clusters
    )

    # ── Write outputs ──────────────────────────────────────────────────────────

    # 1. Master results JSON
    master_log = {
        "date": "2026-05-28",
        "analysis_model": "claude-sonnet-4-6",
        "constraint": "procedural_operating_mode_only__no_bigfive",
        "target": "canonical_activation_pca3d",
        "n_personas": len(personas_list),
        "n_splits": 5,
        "baseline_pca3d_r2": loop_result["baseline_result"]["mean_pca3d_r2"],
        "baseline_per_axis_r2": loop_result["baseline_result"]["mean_per_axis_r2"],
        "final_pca3d_r2": loop_result["final_r2"],
        "final_per_axis_r2": loop_result["final_result"]["mean_per_axis_r2"],
        "final_mean_residual": loop_result["final_result"]["mean_residual"],
        "n_retained_dims": len(loop_result["retained_dims"]),
        "retained_dims": loop_result["retained_dims"],
        "delta_vs_baseline": loop_result["final_r2"] - loop_result["baseline_result"]["mean_pca3d_r2"],
        "codex_procedural_r2": CODEX_PROCEDURAL_R2,
        "delta_vs_codex": loop_result["final_r2"] - CODEX_PROCEDURAL_R2,
        "iteration_log": loop_result["iteration_log"],
        "plateau_threshold": PLATEAU_THRESHOLD,
    }

    with open(os.path.join(OUT_DIR, "claude_procedural_replication_results.json"), "w") as f:
        json.dump(master_log, f, indent=2)

    # 2. Iteration log JSON
    with open(os.path.join(OUT_DIR, "claude_procedural_iteration_log.json"), "w") as f:
        json.dump(loop_result["iteration_log"], f, indent=2)

    # 3. Persona residual rankings CSV
    with open(os.path.join(OUT_DIR, "claude_procedural_persona_residuals.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["persona", "mean_residual", "n_heldout", "activation_cluster"])
        writer.writeheader()
        writer.writerows(residual_rankings)

    # Print top/bottom
    worst = sorted(residual_rankings, key=lambda x: x["mean_residual"], reverse=True)[:15]
    best = residual_rankings[:15]
    print("\nTop 15 WORST explained (procedural model):")
    for r in worst:
        print(f"  {r['persona']}: {r['mean_residual']:.3f} ({r['activation_cluster']})")
    print("\nTop 15 BEST explained (procedural model):")
    for r in best:
        print(f"  {r['persona']}: {r['mean_residual']:.3f} ({r['activation_cluster']})")

    print(f"\nOutputs written to: {OUT_DIR}")
    return master_log, residual_rankings


if __name__ == "__main__":
    main()
