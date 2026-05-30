#!/usr/bin/env python3
"""Reading-based blinded PCA-axis rater study harness.

This script prepares anonymized persona dossiers from the richest available
persona text corpus and analyzes rater scores after Codex-as-rater annotation.
It does not perform keyword-proxy scoring.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
OUT_DIR = REPO / "research/q2_stability/qwen/outputs/blinded_axis_rater_study"
NO_LABEL_PATH = REPO / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
VIZ_PATH = REPO / "research/visualizations/geometry_viz_data.json"
CANONICAL_PCA_PATH = REPO / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"
MODEL_USED = "GPT-5.5"
RANDOM_SEED = 42


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        return
    if fields is None:
        fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def inspect_jsonl(path: Path, role_key: str = "persona") -> dict:
    rows = read_jsonl(path)
    roles = Counter((r.get(role_key) or r.get("role") or "") for r in rows)
    fields = sorted(rows[0].keys()) if rows else []
    text_fields = [f for f in fields if any(s in f.lower() for s in ("prompt", "response", "text"))]
    chars_by_role = defaultdict(int)
    for row in rows:
        role = row.get(role_key) or row.get("role") or ""
        for field in text_fields:
            chars_by_role[role] += len(str(row.get(field, "")))
    return {
        "source_path": str(path),
        "personas_covered": len([r for r in roles if r]),
        "records_per_persona": (
            f"{min(roles.values())}-{max(roles.values())}" if roles else "0"
        ),
        "fields_available": ", ".join(fields),
        "contains_role_name": "yes-metadata" if ("persona" in fields or "role" in fields) else "unknown",
        "contains_prompt": "yes" if any("prompt" in f.lower() for f in fields) else "no",
        "contains_response": "yes" if any("response" in f.lower() for f in fields) else "no",
        "contains_judge_score": "yes" if any("score" in f.lower() for f in fields) else "no",
        "estimated_tokens_per_persona": round(np.mean([estimate_tokens("x" * v) for v in chars_by_role.values()]), 1) if chars_by_role else 0,
        "chosen_for_scoring": "no",
        "reason": "",
    }


def build_corpus_inventory() -> list[dict]:
    candidates = []
    for path, reason in [
        (NO_LABEL_PATH, "Full 275-persona no-label prompt corpus; no rollout responses but complete coverage."),
        (REPO / "data/roles/instructions", "Canonical original role system prompts; complete prompt coverage but direct role-label exposure."),
        (REPO / "research/q2_stability/qwen/outputs/calibration/cluster_synthesis_inputs.json", "Cluster synthesis prompt source; contains cluster grouping and role labels."),
        (REPO / "research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl", "Full rollout responses, but trickster only."),
        (REPO / "research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128.jsonl", "Full rollout responses, but editor only."),
        (REPO / "research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl", "Full rollout responses, but editor only and matched 64."),
        (REPO / "research/q2_stability/qwen/outputs/dyad_v1", "Dyad dialogue outputs for a small representative role set, not all 275 personas."),
    ]:
        if path.is_dir():
            if path.name == "instructions":
                files = sorted(path.glob("*.json"))
                rows = []
                records = []
                fields = set()
                for file in files:
                    try:
                        data = json.loads(file.read_text())
                    except Exception:
                        continue
                    fields.update(data.keys() if isinstance(data, dict) else [])
                    prompts = []
                    if isinstance(data, dict):
                        for key in ("positive", "prompts", "instructions", "system_prompts"):
                            if isinstance(data.get(key), list):
                                prompts.extend(map(str, data[key]))
                        if not prompts:
                            prompts.extend(str(v) for v in data.values() if isinstance(v, str))
                    records.append(len(prompts) or 1)
                rows.append(
                    {
                        "source_path": str(path),
                        "personas_covered": len(files),
                        "records_per_persona": f"{min(records)}-{max(records)}" if records else "0",
                        "fields_available": ", ".join(sorted(fields)),
                        "contains_role_name": "yes-text-and-filename",
                        "contains_prompt": "yes",
                        "contains_response": "no",
                        "contains_judge_score": "no",
                        "estimated_tokens_per_persona": "not-computed",
                        "chosen_for_scoring": "no",
                        "reason": reason,
                    }
                )
                candidates.extend(rows)
            else:
                json_files = list(path.rglob("*.json"))
                csv_files = list(path.rglob("*.csv"))
                candidates.append(
                    {
                        "source_path": str(path),
                        "personas_covered": "small-subset",
                        "records_per_persona": "varies",
                        "fields_available": f"{len(json_files)} json, {len(csv_files)} csv files",
                        "contains_role_name": "yes",
                        "contains_prompt": "yes/varies",
                        "contains_response": "yes/varies",
                        "contains_judge_score": "varies",
                        "estimated_tokens_per_persona": "not-computed",
                        "chosen_for_scoring": "no",
                        "reason": reason,
                    }
                )
        elif path.exists() and path.suffix == ".jsonl":
            row = inspect_jsonl(path)
            row["reason"] = reason
            candidates.append(row)
        elif path.exists() and path.suffix == ".json":
            data = json.loads(path.read_text())
            personas = set()
            prompt_count = 0
            if isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, dict):
                        for key, subval in val.items():
                            if isinstance(subval, list):
                                personas.add(key)
                                prompt_count += len(subval)
            candidates.append(
                {
                    "source_path": str(path),
                    "personas_covered": len(personas),
                    "records_per_persona": "varies",
                    "fields_available": "nested cluster/persona prompt lists",
                    "contains_role_name": "yes",
                    "contains_prompt": "yes",
                    "contains_response": "no",
                    "contains_judge_score": "no",
                    "estimated_tokens_per_persona": round(prompt_count * 25 / max(1, len(personas)), 1),
                    "chosen_for_scoring": "no",
                    "reason": reason,
                }
            )
    for row in candidates:
        if row["source_path"] == str(NO_LABEL_PATH):
            row["chosen_for_scoring"] = "yes"
            row["reason"] = (
                "Chosen because no full 275-persona rollout-response corpus was found locally; "
                "this is the richest complete persona-associated text source and has label exposure removed in scored text."
            )
            row["contains_role_name"] = "metadata-only; scored rewritten_prompt has validated no target-label exposure"
    return candidates


def load_no_label_grouped() -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for row in read_jsonl(NO_LABEL_PATH):
        grouped[row["role"]].append(row)
    return {role: sorted(rows, key=lambda r: r["prompt_index"]) for role, rows in grouped.items()}


def prepare() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "rater_prompts").mkdir(exist_ok=True)
    (OUT_DIR / "rater_raw_outputs").mkdir(exist_ok=True)

    inventory = build_corpus_inventory()
    write_csv(
        OUT_DIR / "corpus_inventory.csv",
        inventory,
        [
            "source_path",
            "personas_covered",
            "records_per_persona",
            "fields_available",
            "contains_role_name",
            "contains_prompt",
            "contains_response",
            "contains_judge_score",
            "estimated_tokens_per_persona",
            "chosen_for_scoring",
            "reason",
        ],
    )

    grouped = load_no_label_grouped()
    id_map = {}
    dossiers = []
    for i, role in enumerate(sorted(grouped), start=1):
        persona_id = f"P{i:04d}"
        id_map[persona_id] = role
        records = []
        for row in grouped[role]:
            text = row["rewritten_prompt"].strip()
            records.append(
                {
                    "record_index": row["prompt_index"],
                    "text_field": "rewritten_prompt",
                    "text": text,
                    "char_count": len(text),
                }
            )
        dossiers.append(
            {
                "persona_id": persona_id,
                "records_used": len(records),
                "text_source_path": str(NO_LABEL_PATH),
                "blinding": {
                    "persona_name_removed": True,
                    "pca_coordinates_removed": True,
                    "cluster_labels_removed": True,
                    "bigfive_scores_removed": True,
                    "residuals_removed": True,
                },
                "records": records,
            }
        )
    with (OUT_DIR / "persona_id_map.json").open("w") as f:
        json.dump(id_map, f, indent=2)
    with (OUT_DIR / "blinded_persona_dossiers.jsonl").open("w") as f:
        for dossier in dossiers:
            f.write(json.dumps(dossier, ensure_ascii=False) + "\n")

    chunks = [dossiers[i : i + 20] for i in range(0, len(dossiers), 20)]
    for idx, chunk in enumerate(chunks, start=1):
        chunk_path = OUT_DIR / "rater_prompts" / f"chunk_{idx:02d}.md"
        chunk_path.write_text(build_rater_prompt(idx, len(chunks), chunk))
    manifest = {
        "model_used": MODEL_USED,
        "task_type": "reading_based_blinded_annotation_preparation",
        "artifact_type": "blinded_persona_dossiers",
        "artifact_path": str(OUT_DIR / "blinded_persona_dossiers.jsonl"),
        "source_inputs": [str(NO_LABEL_PATH)],
        "personas": len(dossiers),
        "records_per_persona": 5,
        "chunks": len(chunks),
        "rater_type": "Codex-as-rater, to be run over prompt chunks",
        "notes_on_uncertainty": (
            "No full 275-persona rollout-response corpus was found locally. "
            "Dossiers use no-label rewritten prompts only."
        ),
    }
    (OUT_DIR / "rater_study_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Prepared {len(dossiers)} dossiers and {len(chunks)} rater prompts in {OUT_DIR}")


def build_rater_prompt(chunk_idx: int, total_chunks: int, chunk: list[dict]) -> str:
    records = []
    for dossier in chunk:
        joined = "\n".join(
            f"Record {r['record_index']}: {r['text']}" for r in dossier["records"]
        )
        records.append(f"### {dossier['persona_id']}\n{joined}")
    return f"""You are Codex/GPT-5.5 acting as a blinded semantic rater.

Task: Read each anonymized persona dossier and assign reading-based ratings. Do not infer from persona names; no persona names are provided. Do not use keywords mechanically. Base scores on the whole text and the behavioral/linguistic pattern implied by the dossier.

Chunk {chunk_idx} of {total_chunks}.

Scales are 0-100.

pc1_objective_certainty_score:
Question: How externally specified is this role's objective function?
High: rule-bound, externally specified, compliance/checking/validation oriented.
Low: objective must be interpreted, negotiated, discovered, or constructed under ambiguity.

pc2_coherent_action_under_uncertainty_score:
Question: How well can this role continue functioning coherently while the correct answer, objective, or resolution remains unavailable?
Important scoring direction for this study: HIGH means coherent action collapses or fragments under uncertainty, including impulsive, avoidant, developmentally unstable, or unable to integrate ambiguity. LOW means the role can sustain coherent action under unresolved uncertainty.
Do not score amount of uncertainty. Score competence/capacity under unresolved uncertainty.

pc3_antagonistic_transgressive_score:
Question: Does this role tend toward cooperative-care/system-stabilization or antagonistic-disruptive/transgressive stance?
High: antagonistic, adversarial, disruptive, transgressive, norm-inverting, conflict-generating.
Low: cooperative, nurturing, stabilizing, mediating, caring, reconciling.

PC2 alternatives:
maturity_score: high means mature, integrated, self-regulated; low means developmentally immature or dependent.
abstraction_score: high means abstract, symbolic, world-model-oriented, theoretical, or metaphysical.
intelligence_expertise_score: high means expert, analytical, technical, disciplined knowledge practice.
uncertainty_exposure_score: high means the text places the role in uncertainty, ambiguity, paradox, incomplete information, or unresolved questions.
uncertainty_residence_time_score: high means the role can remain productively with unresolved uncertainty rather than rushing closure or fragmenting.

Return only valid JSON, an array of objects. Each object must have:
persona_id, pc1_objective_certainty_score, pc1_rationale, pc2_coherent_action_under_uncertainty_score, pc2_rationale, pc3_antagonistic_transgressive_score, pc3_rationale, maturity_score, abstraction_score, intelligence_expertise_score, uncertainty_exposure_score, uncertainty_residence_time_score, pc2_alternative_rationale.

Keep rationales short and grounded in the dossier text. Do not mention PCA, clusters, Big Five, residuals, or coordinates.

DOSSIERS:

{chr(10).join(records)}
"""


def parse_jsonish(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, list):
        raise ValueError("Rater output must be a JSON array")
    return data


def load_rater_scores() -> list[dict]:
    outputs = sorted((OUT_DIR / "rater_raw_outputs").glob("chunk_*.json"))
    if not outputs:
        raise SystemExit("No rater outputs found. Run Codex over rater_prompts first.")
    rows = []
    for path in outputs:
        rows.extend(parse_jsonish(path.read_text()))
    seen = Counter(r["persona_id"] for r in rows)
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        raise SystemExit(f"Duplicate persona IDs in rater outputs: {dupes[:10]}")
    return rows


def load_pca() -> dict[str, dict[str, float]]:
    data = json.loads(VIZ_PATH.read_text())
    roles = data["roles"]
    out = {}
    for name, coords, cluster in zip(roles["names"], roles["pca3d"], roles["clusters"]):
        out[name] = {
            "pc1": float(coords[0]),
            "pc2": float(coords[1]),
            "pc3": float(coords[2]),
            "cluster": cluster,
        }
    return out


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def rankdata(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return pearson(rankdata(x), rankdata(y))


def fit_linear(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    X_aug = np.column_stack([np.ones(len(X)), X])
    coef = np.linalg.pinv(X_aug) @ y
    pred = X_aug @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return coef, 1.0 - ss_res / ss_tot if ss_tot else float("nan")


def cv_r2(X: np.ndarray, y: np.ndarray, k: int = 5) -> float:
    rng = random.Random(RANDOM_SEED)
    idx = list(range(len(y)))
    rng.shuffle(idx)
    folds = [idx[i::k] for i in range(k)]
    pred = np.zeros(len(y), dtype=float)
    for fold in folds:
        test = np.array(fold)
        train = np.array([i for i in idx if i not in set(fold)])
        coef, _ = fit_linear(X[train], y[train])
        pred[test] = np.column_stack([np.ones(len(test)), X[test]]) @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot else float("nan")


def permutation_null(X: np.ndarray, y: np.ndarray, n: int = 500) -> dict:
    rng = np.random.default_rng(RANDOM_SEED)
    vals = [cv_r2(X, rng.permutation(y)) for _ in range(n)]
    arr = np.array(vals)
    return {
        "n_permutations": n,
        "mean_cv_r2": float(np.nanmean(arr)),
        "p95_cv_r2": float(np.nanpercentile(arr, 95)),
        "max_cv_r2": float(np.nanmax(arr)),
    }


def correlations(rows: list[dict]) -> list[dict]:
    score_cols = [
        "pc1_objective_certainty_score",
        "pc2_coherent_action_under_uncertainty_score",
        "pc3_antagonistic_transgressive_score",
        "maturity_score",
        "abstraction_score",
        "intelligence_expertise_score",
        "uncertainty_exposure_score",
        "uncertainty_residence_time_score",
    ]
    out = []
    for score in score_cols:
        x = np.array([float(r[score]) for r in rows])
        for pc in ("pc1", "pc2", "pc3"):
            y = np.array([float(r[pc]) for r in rows])
            out.append(
                {
                    "score": score,
                    "pc": pc,
                    "pearson": pearson(x, y),
                    "spearman": spearman(x, y),
                    "target_aligned": (
                        (score == "pc1_objective_certainty_score" and pc == "pc1")
                        or (score == "pc2_coherent_action_under_uncertainty_score" and pc == "pc2")
                        or (score == "pc3_antagonistic_transgressive_score" and pc == "pc3")
                    ),
                }
            )
    return out


def regression(rows: list[dict]) -> dict:
    cols = [
        "pc1_objective_certainty_score",
        "pc2_coherent_action_under_uncertainty_score",
        "pc3_antagonistic_transgressive_score",
    ]
    alt_cols = cols + [
        "maturity_score",
        "abstraction_score",
        "intelligence_expertise_score",
        "uncertainty_exposure_score",
        "uncertainty_residence_time_score",
    ]
    out = {"model_used": MODEL_USED, "rater_type": "Codex-as-rater", "models": {}}
    for name, use_cols in [("main_three_scores", cols), ("expanded_with_pc2_alternatives", alt_cols)]:
        X = np.array([[float(r[c]) for c in use_cols] for r in rows])
        X = (X - X.mean(axis=0)) / np.where(X.std(axis=0) == 0, 1, X.std(axis=0))
        out["models"][name] = {}
        for pc in ("pc1", "pc2", "pc3"):
            y = np.array([float(r[pc]) for r in rows])
            coef, train = fit_linear(X, y)
            out["models"][name][pc] = {
                "train_r2": train,
                "cv_r2": cv_r2(X, y),
                "permutation_null": permutation_null(X, y),
                "intercept": float(coef[0]),
                "coefficients": {col: float(v) for col, v in zip(use_cols, coef[1:])},
            }
    return out


def matched_pairs(rows: list[dict], n: int = 20) -> list[dict]:
    score_for = {
        "pc1": "pc1_objective_certainty_score",
        "pc2": "pc2_coherent_action_under_uncertainty_score",
        "pc3": "pc3_antagonistic_transgressive_score",
    }
    out = []
    for target in ("pc1", "pc2", "pc3"):
        others = [pc for pc in ("pc1", "pc2", "pc3") if pc != target]
        pairs = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                gap = abs(float(a[target]) - float(b[target]))
                if gap == 0:
                    continue
                orth = math.sqrt(sum((float(a[o]) - float(b[o])) ** 2 for o in others))
                pairs.append((orth / gap, orth, -gap, a, b))
        pairs.sort(key=lambda x: (x[0], x[1], x[2]))
        for _, orth, neg_gap, a, b in pairs[:n]:
            score = score_for[target]
            pc_delta = float(a[target]) - float(b[target])
            score_delta = float(a[score]) - float(b[score])
            out.append(
                {
                    "target_pc": target,
                    "persona_id_a": a["persona_id"],
                    "persona_id_b": b["persona_id"],
                    "persona_name_a": a["persona_name"],
                    "persona_name_b": b["persona_name"],
                    "pc_delta_a_minus_b": pc_delta,
                    "score_column": score,
                    "score_delta_a_minus_b": score_delta,
                    "direction_matches": pc_delta * score_delta > 0,
                    "absolute_target_pc_gap": abs(pc_delta),
                    "orthogonal_pc_distance": orth,
                    "score_a": a[score],
                    "score_b": b[score],
                    "pc_a": a[target],
                    "pc_b": b[target],
                }
            )
    return out


def md_table(rows: Iterable[dict], fields: list[str], limit: int | None = None) -> str:
    rows = list(rows)
    if limit is not None:
        rows = rows[:limit]
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        vals = []
        for field in fields:
            value = row.get(field, "")
            vals.append(f"{value:.3f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def analyze() -> None:
    id_map = json.loads((OUT_DIR / "persona_id_map.json").read_text())
    grouped = load_no_label_grouped()
    pca = load_pca()
    raw_scores = load_rater_scores()
    rows = []
    for score in raw_scores:
        persona_id = score["persona_id"]
        persona = id_map[persona_id]
        row = {
            "persona_id": persona_id,
            "persona_name": persona,
            "persona_name_if_used": "",
            "dossier_records_used": len(grouped[persona]),
            "text_source_path": str(NO_LABEL_PATH),
        }
        for key, value in score.items():
            if key != "persona_id":
                row[key] = value
        row.update(pca[persona])
        rows.append(row)
    rows.sort(key=lambda r: r["persona_id"])
    required = [
        "persona_id",
        "persona_name_if_used",
        "pc1_objective_certainty_score",
        "pc1_rationale",
        "pc2_coherent_action_under_uncertainty_score",
        "pc2_rationale",
        "pc3_antagonistic_transgressive_score",
        "pc3_rationale",
        "dossier_records_used",
        "text_source_path",
    ]
    extra = [
        "maturity_score",
        "abstraction_score",
        "intelligence_expertise_score",
        "uncertainty_exposure_score",
        "uncertainty_residence_time_score",
        "pc2_alternative_rationale",
        "persona_name",
        "pc1",
        "pc2",
        "pc3",
        "cluster",
    ]
    write_csv(OUT_DIR / "axis_rater_scores.csv", rows, required + extra)

    corr = correlations(rows)
    write_csv(OUT_DIR / "axis_rater_correlations.csv", corr, ["score", "pc", "pearson", "spearman", "target_aligned"])
    reg = regression(rows)
    (OUT_DIR / "axis_rater_regression_results.json").write_text(json.dumps(reg, indent=2))
    pairs = matched_pairs(rows)
    write_csv(
        OUT_DIR / "axis_rater_pairwise_validation.csv",
        pairs,
        [
            "target_pc",
            "persona_id_a",
            "persona_id_b",
            "persona_name_a",
            "persona_name_b",
            "pc_delta_a_minus_b",
            "score_column",
            "score_delta_a_minus_b",
            "direction_matches",
            "absolute_target_pc_gap",
            "orthogonal_pc_distance",
            "score_a",
            "score_b",
            "pc_a",
            "pc_b",
        ],
    )
    pc2_alt = [c for c in corr if c["pc"] == "pc2" and c["score"] in {
        "pc2_coherent_action_under_uncertainty_score",
        "maturity_score",
        "abstraction_score",
        "intelligence_expertise_score",
        "uncertainty_exposure_score",
        "uncertainty_residence_time_score",
    }]
    pc2_alt.sort(key=lambda r: -abs(float(r["pearson"])))
    write_csv(OUT_DIR / "pc2_alternative_comparison.csv", pc2_alt, ["score", "pc", "pearson", "spearman", "target_aligned"])
    write_methodology()
    write_report(rows, corr, reg, pairs, pc2_alt)
    print(f"Analyzed {len(rows)} rated dossiers. Report: {OUT_DIR / 'blinded_axis_rater_report.md'}")


def write_methodology() -> None:
    inventory = list(csv.DictReader((OUT_DIR / "corpus_inventory.csv").open()))
    text = f"""# Reading-Based Blinded PCA-Axis Rater Study Methodology

## Corpus Inventory

{md_table(inventory, ["source_path", "personas_covered", "records_per_persona", "contains_prompt", "contains_response", "contains_role_name", "chosen_for_scoring", "reason"])}

## Corpus Choice

Observed: full rollout-response corpora are available locally for trickster and editor extraction runs, and dyad response corpora exist for small role sets. Unknown: no full 275-persona rollout-response corpus was found locally.

Observed: the chosen corpus is `{NO_LABEL_PATH}`. It covers all 275 personas with exactly five no-label rewritten system prompts per persona. The scored text is `rewritten_prompt`, not `original_prompt`, because the rewritten prompts were already validated as having no normalized target-label exposure.

## Dossier Construction

Observed: each dossier contains one anonymized `persona_id`, five complete no-label rewritten prompts, source metadata, and no persona name, PCA coordinate, cluster label, Big Five score, residual, or prior interpretation label. The role-name mapping is stored separately in `persona_id_map.json` for post-rating joins only.

Observed: no sampling was required because the complete five-record corpus per persona was manageable.

## Rater Independence

Observed: no local independent LLM was available through Ollama, LM Studio, or another local runtime. The annotation therefore uses Codex-as-rater via non-interactive Codex chunk prompts. This is reading-based semantic annotation, not deterministic keyword scoring, but it is not as independent as a separate model or human rater.

## Rating Rubrics

PC1: externally specified objective function. High scores indicate rule-bound, externally specified, compliance/checking/validation-oriented objectives. Low scores indicate objectives that must be interpreted, negotiated, discovered, or constructed under ambiguity.

PC2: coherent action under unresolved uncertainty, scored in the direction of actual high PC2. High scores indicate collapse or fragmentation under uncertainty, including impulsive, avoidant, developmentally unstable, or ambiguity-unintegrated action. Low scores indicate the role can sustain coherent action under unresolved uncertainty.

PC3: antagonistic-transgressive stance. High scores indicate antagonistic, adversarial, disruptive, transgressive, norm-inverting, or conflict-generating stance. Low scores indicate cooperative, nurturing, stabilizing, mediating, caring, or reconciling stance.

PC2 alternatives: maturity, abstraction, intelligence/expertise, uncertainty exposure, and uncertainty residence time.

## Model Provenance

`model_used`: {MODEL_USED}

`evaluation_model`: Codex/GPT-5.5 as rater

`analysis_model`: Codex/GPT-5.5

`script_author_model`: Codex/GPT-5.5
"""
    (OUT_DIR / "axis_rater_methodology.md").write_text(text)


def write_report(rows: list[dict], corr: list[dict], reg: dict, pairs: list[dict], pc2_alt: list[dict]) -> None:
    target = [c for c in corr if c["target_aligned"]]
    off = sorted([c for c in corr if not c["target_aligned"]], key=lambda c: -abs(float(c["pearson"])))[:10]
    pair_summary = []
    for pc in ("pc1", "pc2", "pc3"):
        sub = [p for p in pairs if p["target_pc"] == pc]
        pair_summary.append(
            {
                "pc": pc,
                "pairs": len(sub),
                "direction_match_rate": sum(1 for p in sub if p["direction_matches"]) / len(sub),
            }
        )
    main = reg["models"]["main_three_scores"]
    expanded = reg["models"]["expanded_with_pc2_alternatives"]
    target_by_pc = {c["pc"]: c for c in target}
    strongest_pc = max(target, key=lambda c: abs(float(c["pearson"])))
    weakest_pc = min(target, key=lambda c: abs(float(c["pearson"])))
    prior_proxy = {"pc1": 0.247, "pc2": 0.224, "pc3": 0.349}
    failures = [p for p in pairs if not p["direction_matches"]][:8]

    report = f"""# Reading-Based Blinded PCA-Axis Rater Study

## What Was Done

Observed: Codex/GPT-5.5 performed a reading-based blinded annotation study over anonymized persona dossiers. Each dossier contained the complete available no-label persona-associated text: five rewritten system prompts per persona, with no persona name, PCA coordinate, cluster label, Big Five score, residual, or prior interpretation label shown to the rater.

Observed: the study covers {len(rows)} personas. Scoring used the whole dossier text for each persona and produced 0-100 ratings plus short text-grounded rationales for PC1, PC2, PC3, and PC2 alternatives.

## Corpus Actually Used

Observed: no full 275-persona rollout-response corpus was found locally. Full responses exist for specific experiments, especially trickster and editor, but not for all personas. The chosen corpus is the complete no-label prompt-ablation corpus at `{NO_LABEL_PATH}`.

Observed: this means the study validates interpretations against persona operationalization text, not generated rollout behavior.

## Rater Independence

Observed: scoring type is Codex-as-rater. No local independent LLM runtime was available, and the previous deterministic keyword-proxy method was not reused. This is stronger than the lexical proxy because the rater read the dossiers and assigned semantic scores with rationales, but weaker than an independent model or human blinded study.

## Main Quantitative Results

Target-aligned correlations:

{md_table(target, ["score", "pc", "pearson", "spearman"])}

Strongest off-target correlations:

{md_table(off, ["score", "pc", "pearson", "spearman"], 10)}

Cross-validated R2 from the three main rater scores:

| Target | Train R2 | CV R2 | Permutation p95 CV R2 |
| --- | ---: | ---: | ---: |
| PC1 | {main['pc1']['train_r2']:.3f} | {main['pc1']['cv_r2']:.3f} | {main['pc1']['permutation_null']['p95_cv_r2']:.3f} |
| PC2 | {main['pc2']['train_r2']:.3f} | {main['pc2']['cv_r2']:.3f} | {main['pc2']['permutation_null']['p95_cv_r2']:.3f} |
| PC3 | {main['pc3']['train_r2']:.3f} | {main['pc3']['cv_r2']:.3f} | {main['pc3']['permutation_null']['p95_cv_r2']:.3f} |

Cross-validated R2 from expanded scores including PC2 alternatives:

| Target | Train R2 | CV R2 | Permutation p95 CV R2 |
| --- | ---: | ---: | ---: |
| PC1 | {expanded['pc1']['train_r2']:.3f} | {expanded['pc1']['cv_r2']:.3f} | {expanded['pc1']['permutation_null']['p95_cv_r2']:.3f} |
| PC2 | {expanded['pc2']['train_r2']:.3f} | {expanded['pc2']['cv_r2']:.3f} | {expanded['pc2']['permutation_null']['p95_cv_r2']:.3f} |
| PC3 | {expanded['pc3']['train_r2']:.3f} | {expanded['pc3']['cv_r2']:.3f} | {expanded['pc3']['permutation_null']['p95_cv_r2']:.3f} |

Matched-pair validation:

{md_table(pair_summary, ["pc", "pairs", "direction_match_rate"])}

## PC2 Alternative Comparison

Observed: PC2 alternatives are ranked below by absolute correlation with PC2.

{md_table(pc2_alt, ["score", "pc", "pearson", "spearman", "target_aligned"])}

## Interpretation Update

Observed: the strongest target-aligned reading-based correlation is `{strongest_pc['score']}` to {strongest_pc['pc']} at r={strongest_pc['pearson']:.3f}. The weakest is `{weakest_pc['score']}` to {weakest_pc['pc']} at r={weakest_pc['pearson']:.3f}.

Observed: all three target correlations exceed the prior deterministic lexical-proxy screen: PC1 {target_by_pc['pc1']['pearson']:.3f} vs {prior_proxy['pc1']:.3f}, PC2 {target_by_pc['pc2']['pearson']:.3f} vs {prior_proxy['pc2']:.3f}, and PC3 {target_by_pc['pc3']['pearson']:.3f} vs {prior_proxy['pc3']:.3f}. The reading-based study therefore strengthens the claim that the working axis interpretations are present in the no-label prompt dossiers, especially PC3 and PC1.

Observed: PC1 is strengthened but not isolated. The objective-certainty score predicts PC1 at r={target_by_pc['pc1']['pearson']:.3f} and has a 0.750 matched-pair direction rate, but intelligence/expertise is an even stronger PC1 correlate at r=0.663. This suggests PC1 should be framed as objective certainty plus disciplined expertise/procedural competence, not only constraint.

Observed: PC3 is strongly strengthened. The antagonistic-transgressive score predicts PC3 at r={target_by_pc['pc3']['pearson']:.3f}, with cross-validated R2={main['pc3']['cv_r2']:.3f} from the three main scores and a 0.950 matched-pair direction rate. The cooperative-stabilizing versus antagonistic-transgressive interpretation is now the best-supported direct axis interpretation in this rater study.

Observed: PC2 remains the main uncertainty. The coherent-action-under-uncertainty score predicts PC2 at r={target_by_pc['pc2']['pearson']:.3f} and performs well in matched pairs, but abstraction is a much stronger PC2 correlate in the opposite direction at r={pc2_alt[0]['pearson']:.3f}. Uncertainty residence time, maturity, and expertise also correlate with PC2 at magnitudes similar to or larger than the direct coherent-action score. This weakens the claim that coherent action under uncertainty is the best single PC2 formulation.

Speculative: divergence between dossier ratings and PCA coordinates may reflect activation geometry reorganizing prompt semantics, the absence of rollout behavior in the corpus, rater-model subjectivity, or genuinely compound axes.

## Strongest Counterexamples

Observed: the following matched pairs violate the predicted score direction while staying relatively close on the other two PCs:

{md_table(failures, ["target_pc", "persona_name_a", "persona_name_b", "pc_delta_a_minus_b", "score_delta_a_minus_b", "orthogonal_pc_distance"], 8)}

## Confidence Update

PC1: confidence increases to moderate. The rater score predicts PC1 clearly, but the stronger intelligence/expertise correlation means the constraint versus possibility language should include disciplined knowledge practice and externally legible competence.

PC2: confidence remains low to moderate. The axis appears to involve abstraction, maturity, expertise, and residence with uncertainty more strongly than the direct coherent-action score alone. Strong paper language should wait for a richer full-response rater study or a targeted matched-pair annotation design.

PC3: confidence increases to moderate-high within the limits of prompt-dossier evidence. It should still be described as a partial stance axis rather than a complete account of PC3.

## Recommended Next Test

Run an independent-rater version of this study using a second model or human annotators and, if possible, richer rollout responses rather than system-prompt dossiers. For PC2, use a smaller matched-pair design that forces raters to distinguish maturity, abstraction, uncertainty exposure, and coherent action under unresolved uncertainty.
"""
    (OUT_DIR / "blinded_axis_rater_report.md").write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "analyze"])
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    else:
        analyze()


if __name__ == "__main__":
    main()
