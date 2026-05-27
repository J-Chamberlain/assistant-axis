#!/usr/bin/env python3
"""Semantic overlap analysis for persona inventory sensitivity runs.

Computes:
  - Inventory sizes per model
  - Jaccard overlap between model-level aggregated role sets (exact-match after normalization)
  - TF-IDF cosine similarity between model vocabularies (captures near-matches)
  - Lu et al. reference overlap per model
  - Within-model prompt variance (mean Jaccard across prompt pairs)
  - Roles present across all / most models (invariant core)
  - Roles unique to single models (model-specific manifold structure)

Input:  runs/runs.jsonl
Output: analysis/overlap_report.json
        analysis/overlap_report.md

Usage:
    python analyze_overlap.py [--min-runs 1]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS_JSONL = HERE / "runs" / "runs.jsonl"
ANALYSIS_DIR = HERE / "analysis"
LU_ROLES_FILE = ROOT / "data" / "roles" / "role_list.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def tfidf_cosine_matrix(docs: list[list[str]]) -> np.ndarray:
    """TF-IDF cosine similarity matrix for a list of token lists."""
    vocab: dict[str, int] = {}
    for doc in docs:
        for tok in doc:
            if tok not in vocab:
                vocab[tok] = len(vocab)

    n, v = len(docs), len(vocab)
    mat = np.zeros((n, v))
    for i, doc in enumerate(docs):
        tf = Counter(doc)
        total = sum(tf.values()) or 1
        for tok, cnt in tf.items():
            mat[i, vocab[tok]] = cnt / total

    df = (mat > 0).sum(axis=0)
    idf = np.log((n + 1) / (df + 1)) + 1
    mat = mat * idf

    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1
    mat = mat / norms

    sim = mat @ mat.T
    return sim


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-runs", type=int, default=1, help="Min successful runs per cell to include")
    args = parser.parse_args()

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    if not RUNS_JSONL.exists():
        raise FileNotFoundError(f"No runs file at {RUNS_JSONL}. Run generate_inventories.py first.")

    runs: list[dict] = []
    with open(RUNS_JSONL) as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("status") == "ok" and rec.get("roles_parsed"):
                    runs.append(rec)
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(runs)} valid runs")
    if not runs:
        raise SystemExit("No valid runs found.")

    lu_roles: set[str] = set()
    if LU_ROLES_FILE.exists():
        lu_data = json.loads(LU_ROLES_FILE.read_text())
        lu_roles = {k.lower().replace("_", " ") for k in lu_data}
        print(f"Lu reference: {len(lu_roles)} roles")

    # Group: (model_id, prompt_id) → list of role lists
    cells: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
    for run in runs:
        cells[(run["model_id"], run["prompt_id"])].append(run["roles_parsed"])

    # Model-level aggregate (union across all prompts and runs)
    model_sets: dict[str, set[str]] = defaultdict(set)
    for (mid, _), role_lists in cells.items():
        for rl in role_lists:
            model_sets[mid].update(rl)

    model_ids = sorted(model_sets.keys())
    prompt_ids = sorted({p for (_, p) in cells})
    n = len(model_ids)

    print(f"Models: {model_ids}")
    print(f"Prompts: {prompt_ids}")

    # Jaccard matrix
    jac_mat = np.array(
        [[jaccard(model_sets[m1], model_sets[m2]) for m2 in model_ids] for m1 in model_ids]
    )

    # TF-IDF cosine matrix
    model_docs = [list(model_sets[m]) for m in model_ids]
    tfidf_mat = tfidf_cosine_matrix(model_docs)

    # Lu overlap
    lu_overlap = {}
    for mid in model_ids:
        rset = model_sets[mid]
        lu_overlap[mid] = {
            "total_generated": len(rset),
            "in_lu": len(rset & lu_roles),
            "model_only": len(rset - lu_roles),
            "lu_only": len(lu_roles - rset),
            "jaccard_vs_lu": round(jaccard(rset, lu_roles), 4),
        }

    # Within-model prompt variance
    within_model_var: dict[str, dict | None] = {}
    for mid in model_ids:
        prompt_sets = [
            set().union(*cells[(mid, pid)])
            for pid in prompt_ids
            if (mid, pid) in cells
        ]
        if len(prompt_sets) < 2:
            within_model_var[mid] = None
            continue
        pairwise = [
            jaccard(prompt_sets[i], prompt_sets[j])
            for i in range(len(prompt_sets))
            for j in range(i + 1, len(prompt_sets))
        ]
        within_model_var[mid] = {
            "mean_jaccard": round(float(np.mean(pairwise)), 4),
            "min_jaccard": round(float(np.min(pairwise)), 4),
            "max_jaccard": round(float(np.max(pairwise)), 4),
            "n_pairs": len(pairwise),
        }

    # Prevalence: how many models include each role
    role_counter: Counter = Counter()
    for rset in model_sets.values():
        for r in rset:
            role_counter[r] += 1

    invariant_core = [r for r, c in role_counter.items() if c == n]
    by_prevalence = sorted(role_counter.items(), key=lambda x: -x[1])
    model_unique = {
        mid: sorted(model_sets[mid] - set().union(*(model_sets[m] for m in model_ids if m != mid)))
        for mid in model_ids
    }

    report = {
        "experiment_id": "persona_inventory_sensitivity_v1",
        "n_runs_analyzed": len(runs),
        "model_ids": model_ids,
        "prompt_ids": prompt_ids,
        "lu_reference_size": len(lu_roles),
        "model_inventory_sizes": {m: len(model_sets[m]) for m in model_ids},
        "jaccard_matrix": {"model_ids": model_ids, "values": jac_mat.tolist()},
        "tfidf_cosine_matrix": {"model_ids": model_ids, "values": tfidf_mat.tolist()},
        "lu_overlap": lu_overlap,
        "within_model_prompt_variance": within_model_var,
        "invariant_core": invariant_core,
        "invariant_core_size": len(invariant_core),
        "roles_by_prevalence_top100": [{"role": r, "model_count": c} for r, c in by_prevalence[:100]],
        "model_unique_roles": {m: roles[:50] for m, roles in model_unique.items()},
    }

    out_json = ANALYSIS_DIR / "overlap_report.json"
    out_json.write_text(json.dumps(report, indent=2))
    print(f"Written: {out_json}")

    # Markdown report
    lines: list[str] = [
        "# Persona Inventory Sensitivity — Overlap Report",
        "",
        f"Runs analyzed: {len(runs)}  ",
        f"Models: {', '.join(model_ids)}  ",
        f"Prompts: {', '.join(prompt_ids)}  ",
        f"Lu reference size: {len(lu_roles)} roles",
        "",
        "## Inventory Sizes",
    ]
    for mid in model_ids:
        lines.append(f"- **{mid}**: {len(model_sets[mid])} unique roles (union across all prompts and runs)")
    lines.append("")

    lines += [
        "## Jaccard Overlap Between Models",
        "(1.0 = identical vocabulary; higher = more shared role names)",
        "| model | " + " | ".join(model_ids) + " |",
        "|" + "---|" * (n + 1),
    ]
    for i, mid in enumerate(model_ids):
        row = f"| {mid} | " + " | ".join(f"{jac_mat[i][j]:.3f}" for j in range(n)) + " |"
        lines.append(row)
    lines.append("")

    lines += [
        "## TF-IDF Cosine Similarity Between Models",
        "(captures semantic proximity beyond exact string matches)",
        "| model | " + " | ".join(model_ids) + " |",
        "|" + "---|" * (n + 1),
    ]
    for i, mid in enumerate(model_ids):
        row = f"| {mid} | " + " | ".join(f"{tfidf_mat[i][j]:.3f}" for j in range(n)) + " |"
        lines.append(row)
    lines.append("")

    lines += [
        "## Lu Reference Overlap",
        "| model | generated | in Lu | Lu only | Jaccard vs Lu |",
        "|---|---|---|---|---|",
    ]
    for mid in model_ids:
        ov = lu_overlap[mid]
        lines.append(
            f"| {mid} | {ov['total_generated']} | {ov['in_lu']} | {ov['lu_only']} | {ov['jaccard_vs_lu']} |"
        )
    lines.append("")

    lines += [
        "## Within-Model Prompt Variance",
        "(mean Jaccard between role sets from different prompts, same model)",
        "| model | mean Jaccard | min | max |",
        "|---|---|---|---|",
    ]
    for mid in model_ids:
        v = within_model_var.get(mid)
        if v is None:
            lines.append(f"| {mid} | — | — | — |")
        else:
            lines.append(f"| {mid} | {v['mean_jaccard']} | {v['min_jaccard']} | {v['max_jaccard']} |")
    lines.append("")

    lines.append(f"## Invariant Core ({len(invariant_core)} roles present in all {n} models)")
    for r in sorted(invariant_core):
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Top 25 Most Widely Shared Roles")
    for item in by_prevalence[:25]:
        lines.append(f"- {item['role']} ({item[1]}/{n} models)")
    lines.append("")

    lines.append("## Model-Unique Roles (up to 20 per model)")
    for mid in model_ids:
        uniq = model_unique[mid][:20]
        lines.append(f"### {mid} ({len(model_unique[mid])} unique)")
        for r in uniq:
            lines.append(f"- {r}")
    lines.append("")

    out_md = ANALYSIS_DIR / "overlap_report.md"
    out_md.write_text("\n".join(lines))
    print(f"Written: {out_md}")


if __name__ == "__main__":
    main()
